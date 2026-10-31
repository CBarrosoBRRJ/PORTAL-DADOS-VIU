"""Tabelas gold em memória (D7), recarregadas só quando o metadado `modified` muda (D6).

Atualização sem espera: com uma carga em memória, a conferência do metadado (no máximo a cada RECARGA_MIN) e a
recarga rodam **em segundo plano**; a página responde na hora com os dados atuais. A carga nova é validada (contrato:
colunas, chave única, não vazia), os cálculos derivados são aquecidos (`ao_carregar`) e só então ela substitui a
anterior. Só a primeira carga (servidor recém-ligado) é feita na própria requisição. Cada worker/instância tem a
sua cópia.

Política de falha: se o BigQuery falhar e já houver uma carga válida, ela continua sendo servida (marcada como
atrasada) e a próxima tentativa espera RECARGA_MIN; sem carga válida, `DadosIndisponiveis`.

Leitura: só as colunas usadas, pela BigQuery Storage Read API (≈ 3× mais rápida); se ela falhar (ex.: permissão
`bigquery.readsessions.create` ausente), cai para a leitura comum.

Fonte única (D57, 27/10/2026): só tabelas e views da gold (gold_monday). Uma view não tem carga própria: o `modified` que
dispara a recarga é o da tabela de base (`gatilho`).
"""

import json
import threading
import time
from datetime import datetime, timedelta
from typing import Callable

import pandas as pd
from google.cloud import bigquery

from app import config, congelamento  # D65: corte e base congelada em arquivo (app/congelamento.py)

_cliente: bigquery.Client | None = None


def ler_espelho(tabela) -> tuple[pd.DataFrame, datetime]:
    """D66b: (carga, `modified` da tabela quando o espelho foi gerado) dos arquivos de ESPELHO_DIR (tools/gerar_espelho.py).
    Sem o arquivo da tabela, erro (a página mostra "dados indisponíveis"); o BigQuery nunca é consultado."""
    from pathlib import Path

    pasta = Path(config.ESPELHO_DIR)
    nome = congelamento.nome(tabela)
    ficha = json.loads((pasta / "espelho.json").read_text(encoding="utf-8"))["tabelas"][nome]
    df = pd.read_parquet(pasta / f"{nome}.parquet")
    if len(df) != ficha["linhas"]:
        raise RuntimeError(f"espelho de {nome}: {len(df)} linhas, esperado {ficha['linhas']}")
    return df, pd.Timestamp(ficha["modificada_em"]).to_pydatetime()


def cliente() -> bigquery.Client:
    global _cliente
    if _cliente is None:
        _cliente = bigquery.Client(project=config.PROJETO)
    return _cliente


def log(severidade: str, mensagem: str, **campos) -> None:
    """Log estruturado (o Cloud Logging lê o JSON e a severidade). Nunca inclui dados da tabela."""
    print(json.dumps({"severity": severidade, "message": mensagem, **campos}, ensure_ascii=False, default=str), flush=True)


def data_carga(df: pd.DataFrame):
    """Dia (São Paulo) em que a gold gravou a tabela (`_processado_em`), ou None sem o metadado (regra E3). Entrada e
    fluxo de dias diferentes não podem ser mostrados juntos (E7, aviso de atualização). Fica aqui, e não no cálculo do
    Início, porque Talentos confere a sua carga com a do Início pela mesma regra (TAL-D9) sem import circular."""
    from app import corte  # batalha 2 (G4-N10): a regra E3 mora em app/corte.py (site, job e ML)

    return corte.dia_da_carga(df["_processado_em"]) if "_processado_em" in df else None


class DadosIndisponiveis(RuntimeError):
    """Nenhuma carga válida em memória e o BigQuery não respondeu."""


def atualizacao_esperada(agora: datetime) -> datetime:
    """Última atualização que a gold já deveria ter feito: o dia útil mais recente cuja hora da agenda + tolerância
    já passou (ex.: segunda 08:00 → sexta anterior 09:00; segunda 10:00 → segunda 09:00)."""
    dia = agora.astimezone(config.FUSO)
    prazo = timedelta(hours=config.GOLD_HORA, minutes=config.GOLD_TOLERANCIA_MIN)
    for atras in range(0, 8):
        d = (dia - timedelta(days=atras)).replace(hour=0, minute=0, second=0, microsecond=0)
        if d.weekday() < 5 and d + prazo <= dia:
            return d + timedelta(hours=config.GOLD_HORA)
    return dia - timedelta(days=7)


class Tabela:
    def __init__(self, nome: str, id_tabela: str, chave: tuple[str, ...] = ("projeto_id", "passo"),
                 colunas: tuple[str, ...] = (), em_fundo: bool = True, gatilho: str | None = None,
                 permite_vazia: bool = False):
        self.nome = nome
        self.id_tabela = id_tabela
        self.gatilho = gatilho  # view: a tabela de base cujo `modified` dispara a recarga
        self.chave = chave
        self.colunas = colunas  # obrigatórias (contrato) e as únicas lidas; vazio = SELECT *
        self.em_fundo = em_fundo  # False: conferência e recarga na própria requisição (testes)
        self.ao_carregar: list[Callable[[pd.DataFrame], object]] = []  # aquecem caches antes da troca
        self._df: pd.DataFrame | None = None
        self._trava = threading.Lock()
        self._checado_em = 0.0
        self.versao = 0  # cresce a cada carga; vai em df.attrs["versao"] para os caches derivados
        self.modificada_em: datetime | None = None
        self.carregada_em: datetime | None = None
        self.bytes_lidos = 0
        self.segundos_carga = 0.0
        self.verificada_em: datetime | None = None  # última vez que o metadado foi lido com sucesso
        self.erro: str | None = None  # última falha de atualização (texto curto); None = em dia
        self._assinatura_carga = None
        self.permite_vazia = permite_vazia  # ausência legítima (ex.: janeiro sem pedido), não falha de conexão
        self.congelada = False  # D65: a carga do corte (ou a do arquivo) entrou; nenhuma outra troca a base

    def _validar(self, df: pd.DataFrame) -> None:
        faltam = [c for c in self.colunas if c not in df.columns]
        if faltam:
            raise ValueError(f"colunas ausentes: {faltam}")
        if df.empty and not self.permite_vazia:
            raise ValueError("tabela vazia")
        if self.chave and df.duplicated(list(self.chave)).any():
            raise ValueError(f"chave {self.chave} repetida")
        if not df.empty and '_processado_em' in df and (df['_processado_em'].isna().any() or df['_processado_em'].nunique() != 1):
            raise ValueError('carga com processamento ausente ou misturado')
        if {'entrada', 'saida', 'fase', 'status', 'projeto_id', 'passo'}.issubset(df.columns):
            if df[['projeto_id', 'passo', 'entrada']].isna().any().any():
                raise ValueError('histórico com identificação ou entrada ausente')
            ordenado = df.sort_values(['projeto_id', 'passo'])
            esperado = ordenado.groupby('projeto_id').cumcount() + 1
            if not ordenado['passo'].eq(esperado).all():
                raise ValueError('histórico com passos fora de sequência')
            if not ordenado.loc[ordenado.passo.eq(1), 'status'].eq('Entrada').all():
                raise ValueError('histórico não começa em Entrada')
            proxima = ordenado.groupby('projeto_id')['entrada'].shift(-1)
            if (ordenado.saida < ordenado.entrada).any() or (
                    proxima.notna() & (ordenado.saida.isna() | ordenado.saida.ne(proxima))).any():
                raise ValueError('histórico com intervalo inválido ou descontínuo')
        contagens = [c for c in ('n', 'total', 'dos_quais_squad', 'quantidade', 'quantidade_estimada', 'quantidade_saida',
                                'entregue_no_mes', 'entregue_depois', 'nao_seguiu', 'em_andamento') if c in df]
        for c in contagens:
            if df[c].isna().any() or (df[c] < 0).any() or (df[c] % 1 != 0).any():
                raise ValueError(f'contagem inválida: {c}')
        situacoes = ['entregue_no_mes', 'entregue_depois', 'nao_seguiu', 'em_andamento']
        if set(situacoes + ['quantidade_estimada']).issubset(df.columns):
            if not df[situacoes].sum(axis=1).eq(df.quantidade + df.quantidade_estimada).all():
                raise ValueError('situações não reconciliam com as entradas')

    def _baixar(self) -> tuple[pd.DataFrame, int]:
        lista = ", ".join(self.colunas) if self.colunas else "*"
        job = cliente().query(f"SELECT {lista} FROM `{self.id_tabela}`",
                              job_config=bigquery.QueryJobConfig(labels=config.LABELS))
        try:
            df = job.to_dataframe(create_bqstorage_client=True)
        except Exception as e:  # noqa: BLE001 — sem Storage API (permissão, rede): leitura comum
            log("WARNING", "Storage Read API indisponível; usando leitura comum", erro=f"{type(e).__name__}: {e}"[:200])
            df = job.to_dataframe(create_bqstorage_client=False)
        return df, job.total_bytes_processed or 0

    def _carregar(self, modificada_em: datetime, arquivo: pd.DataFrame | None = None) -> None:
        """Carga do BigQuery ou, com `arquivo`, da base congelada (D65, K6: sem consulta)."""
        inicio = time.monotonic()
        df, bytes_lidos = (arquivo, 0) if arquivo is not None else self._baixar()
        self._validar(df)
        # D65: corte dos dados (K2–K5); ForaDoCorte = carga ignorada, a anterior continua
        decisao = "congelar" if arquivo is not None else congelamento.decidir(self, df)
        df.attrs["versao"] = self.versao + 1
        df.attrs["origem_modificada_em"] = modificada_em
        for aquecer in self.ao_carregar:  # cálculos da carga nova prontos antes de ela entrar no ar
            try:
                aquecer(df)
            except Exception as e:  # noqa: BLE001 — aquecer é otimização; a página calcula se precisar
                log("WARNING", "falha ao aquecer cálculos", erro=f"{type(e).__name__}: {e}"[:200])
        self._df, self.versao = df, self.versao + 1  # troca atômica: a requisição vê a carga antiga ou a nova
        self.bytes_lidos = bytes_lidos
        self.segundos_carga = round(time.monotonic() - inicio, 1)
        self.modificada_em = modificada_em
        self.carregada_em = datetime.now(config.FUSO)
        log("INFO", "tabela carregada", tabela=self.id_tabela, versao=self.versao, linhas=len(df),
            bytes=self.bytes_lidos, segundos=self.segundos_carga, modificada_em=modificada_em,
            origem="base congelada" if arquivo is not None else "bigquery")
        if decisao == "congelar":  # D65, K3: a última carga aceita; daqui em diante nada troca a base
            self.congelada = True  # congelada EM MEMÓRIA; persistida só depois de gravada e conferida (F02, B1)
            if arquivo is None:
                # F02/F07/F08: a base é gravada como unidade quando todas as tabelas congelarem; falha = nova tentativa
                congelamento.registrar(self, df, modificada_em)

    def _atualizar(self, forcar: bool) -> None:
        """Confere o metadado e recarrega se mudou. Chamar com a trava adquirida."""
        modificada_em = None
        try:
            if self._df is None and config.ESPELHO_DIR:  # D66b: espelho da VPS, só arquivos, nunca o BigQuery
                df, modificada = ler_espelho(self)
                self._carregar(modificada, arquivo=df)
                self._assinatura_carga = modificada
                self.verificada_em = datetime.now(config.FUSO)
                self.erro = None
                return
            if self._df is None and congelamento.ligado():  # D65, K6: a base congelada em arquivo dispensa o BigQuery
                lido = congelamento.ler(self)
                if lido is not None:
                    self._carregar(lido[1], arquivo=lido[0])
                    self._assinatura_carga = lido[1]
                    self.verificada_em = datetime.now(config.FUSO)
                    self.erro = None
                    return
                if config.EM_PRODUCAO:  # F01: em produção, com o corte ligado, o BigQuery nunca é consultado
                    raise congelamento.BaseInvalida("base congelada ausente ou inválida (o arranque deveria ter "
                                                    "falhado); em produção o BigQuery não é consultado")
            modificada_em = cliente().get_table(self.gatilho or self.id_tabela).modified  # metadado: sem custo
            if self._df is None or forcar or modificada_em != self._assinatura_carga:
                self._carregar(modificada_em)
                self._assinatura_carga = modificada_em
            self.verificada_em = datetime.now(config.FUSO)
            self.erro = None
        except Exception as e:  # noqa: BLE001 — qualquer falha do BigQuery ou do contrato
            self.erro = f"{type(e).__name__}: {e}"[:300]
            if isinstance(e, congelamento.ForaDoCorte) and modificada_em is not None:
                self._assinatura_carga = modificada_em  # D65, K4: a mesma carga não é baixada de novo a cada checagem
            log("ERROR", "falha ao atualizar a tabela", tabela=self.id_tabela, erro=self.erro,
                servindo_versao=self.versao or None)
            if self._df is None:
                raise DadosIndisponiveis(f"{self.nome}: {self.erro}") from e
        finally:
            self._checado_em = time.monotonic()  # com ou sem falha, a próxima tentativa espera RECARGA_MIN

    def _atualizar_em_fundo(self) -> None:
        try:
            self._atualizar(False)
        except DadosIndisponiveis:
            pass
        finally:
            self._trava.release()

    def _congelada_agora(self) -> bool:
        """D65: congelada pelo corte; sem corte, o CONGELAR da D63 (a carga lida na subida, B-N8)."""
        if self.congelada:
            return True
        return config.CORTE_DADOS is None and config.CONGELAR and self._df is not None

    def _vencido(self) -> bool:
        if self._congelada_agora():  # B-N8 / D65: base congelada para a reunião
            return False
        return time.monotonic() - self._checado_em >= config.RECARGA_MIN * 60

    def df(self, forcar: bool = False) -> pd.DataFrame:
        if self.congelada and self._df is not None:  # D65: congelada, nem a recarga forçada troca a base
            congelamento.persistir_pendente()  # F02: gravação da base que falhou é retentada (no máximo a cada 30 s)
            return self._df
        if self._df is None or forcar:  # primeira carga (ou forçada): a requisição espera
            with self._trava:
                if self._df is None and self.erro and not forcar and not self._vencido():
                    raise DadosIndisponiveis(f'{self.nome}: nova tentativa após o intervalo de atualização')
                if self._df is None or forcar:
                    self._atualizar(forcar)
            return self._df
        if self._vencido():
            if not self.em_fundo:
                with self._trava:
                    if self._vencido():
                        self._atualizar(False)
            elif self._trava.acquire(blocking=False):  # uma atualização por vez; as outras requisições não esperam
                self._checado_em = time.monotonic()
                threading.Thread(target=self._atualizar_em_fundo, name=f"atualiza-{self.nome}", daemon=True).start()
        return self._df

    @property
    def atrasada(self) -> bool:
        return self.erro is not None

    def estado(self, agora: datetime | None = None) -> str:
        """"em_dia", "falha_leitura" (o site não conseguiu ler o BigQuery), "base_atrasada" (a gold não atualizou
        no horário da agenda) ou "congelada" (CONGELAR: a base da reunião não é relida, então não há atraso a acusar;
        batalha 2, G1-engenharia-1)."""
        if self.erro is not None:
            return "falha_leitura"
        if self._congelada_agora():  # D63 (CONGELAR sem corte) ou D65 (carga do corte)
            return "congelada"
        if self.modificada_em and self.modificada_em < atualizacao_esperada(agora or datetime.now(config.FUSO)):
            return "base_atrasada"
        return "em_dia"

    def processado_em(self) -> datetime | None:
        """MAX(_processado_em) da carga em memória (São Paulo), ou None sem a coluna (bases de teste). O rodapé
        usa este horário (INI-D1): o `modified` muda também com um ALTER só de descrições."""
        df = self._df
        guardado = getattr(self, "_processado_guardado", None)
        if guardado is not None and guardado[0] is df:  # desempenho (31/10/2026): uma conta por carga, não por página
            return guardado[1]
        if df is None or "_processado_em" not in df or not df["_processado_em"].notna().any():
            valor = None
        else:
            valor = pd.to_datetime(df["_processado_em"], utc=True).max().tz_convert(config.FUSO).to_pydatetime()
        self._processado_guardado = (df, valor)
        return valor

    def situacao(self) -> dict:
        return {
            "nome": self.nome,
            "tabela": self.id_tabela,
            "versao": self.versao,
            "modificada_em": self.modificada_em.astimezone(config.FUSO) if self.modificada_em else None,
            "processado_em": self.processado_em(),  # rodapé datado (INI-D1); o modified segue só como gatilho de recarga
            "carregada_em": self.carregada_em,
            "verificada_em": self.verificada_em,
            "linhas": 0 if self._df is None else len(self._df),
            "bytes_lidos": self.bytes_lidos,
            "segundos_carga": self.segundos_carga,
            "atrasada": self.atrasada,
            "estado": self.estado(),
            "erro": self.erro,
        }


# colunas lidas da gold (as usadas pelo site); a lista também é o contrato mínimo da carga
COLUNAS_SLA = ("projeto_id", "passo", "status", "fase", "entrada", "saida", "sla_util_horas", "sla_sem_almoco_horas",
               "exclusivo", "status_atual", "nome_projeto", "marca", "talento", "tipo_de_input", "tipo_de_output",
               "orcamento", "link_projeto", "em_aberto", "aberto_ha_util_horas", "retrabalho", "reaberto", "alerta",
               "fora_expediente", "hora_extra_horas", "_processado_em")
sla = Tabela("SLA — movimentos", config.TAB_SLA, colunas=COLUNAS_SLA, em_fundo=not config.EM_PRODUCAO)
# C1–C4, C9, C14 (view): uma linha por orçamento entregue, com as horas da equipe sem almoço (R24) e os dias úteis
sla_entregas = Tabela("SLA — entregas", config.TAB_SLA_ENTREGAS, chave=("projeto_id",),
                      colunas=("projeto_id", "mes", "mes_entrada", "inicio", "entregue_em", "exclusivo", "tipo_de_input",
                               "pacote", "h_trabalho", "h_fila", "h_elaboracao", "h_revisao", "h_calendario",
                               "dias_uteis", "dias_uteis_fr", "_processado_em"),
                      gatilho=config.TAB_SLA, permite_vazia=True, em_fundo=not config.EM_PRODUCAO)
# K1 (view): horas de cada orçamento entregue em cada status da equipe (slide 6 do estudo)
sla_entregas_status = Tabela("SLA — horas por status", config.TAB_SLA_ENTREGAS_STATUS, chave=("projeto_id", "status"),
                             colunas=("projeto_id", "status", "h", "_processado_em"), gatilho=config.TAB_SLA,
                             permite_vazia=True, em_fundo=not config.EM_PRODUCAO)
COLUNAS_ENTRADA = ("data", "grupo_input", "tipo_de_input", "familia", "quantidade", "quantidade_estimada",
                   "quantidade_saida",  # saída = 1ª entrega ao cliente (regra B da gold)
                   "entregue_no_mes", "entregue_depois", "nao_seguiu", "em_andamento", "_processado_em")
entrada = Tabela("Entrada diária", config.TAB_ENTRADA, chave=("data", "grupo_input", "tipo_de_input", "familia"),
                 colunas=COLUNAS_ENTRADA, em_fundo=not config.EM_PRODUCAO)
COLUNAS_FLUXO = ("mes_entrada", "evento", "mes_evento", "grupo_input", "tipo_de_input", "familia", "quantidade", "_processado_em")
fluxo = Tabela("Fluxo mensal", config.TAB_FLUXO,
               chave=("mes_entrada", "evento", "mes_evento", "grupo_input", "tipo_de_input", "familia"), colunas=COLUNAS_FLUXO,
               em_fundo=not config.EM_PRODUCAO)
# E7 (view): o extrato do mês do Início, por mês e safra
fila = Tabela("Fila mensal", config.TAB_FILA, chave=("mes", "mes_entrada"),
              colunas=("mes", "mes_entrada", "do_ano", "novos", "represados", "entregues", "nao_seguiram", "seguem",
                       "_processado_em"), gatilho=config.TAB_FLUXO, em_fundo=not config.EM_PRODUCAO)
# A13/A27 (view): o mês do Atendimento — respondidos, fila que veio e que ficou, externos
atendimento = Tabela("Atendimento mensal", config.TAB_ATENDIMENTO, chave=("mes",),
                     colunas=("mes", "completo", "entradas", "entregues", "sem_entrega", "sem_entrega_sem_data",
                              "respondidos", "veio", "para_atender", "ficou", "status_confere", "externos", "dependia",
                              "_processado_em"), gatilho=config.TAB_FLUXO, em_fundo=not config.EM_PRODUCAO)
# T1–T5: divisão do ano entre exclusivos, não exclusivos e sem talento (vazia em janeiro antes do 1º pedido)
talentos = Tabela("Talentos — divisão do ano", config.TAB_TALENTOS_ANO, chave=("ano", "categoria"),
                  colunas=("ano", "categoria", "n", "total", "pct", "dos_quais_squad", "_processado_em"),
                  permite_vazia=True, em_fundo=not config.EM_PRODUCAO)
# T6–T10 (D50, D51): os 10 talentos com mais pedidos por recorte, mês a mês, e quem passou pelos 10 do acumulado
talentos_top = Tabela("Talentos — mais pedidos", config.TAB_TALENTOS_RANKING, chave=("grupo", "talento", "mes"),
                      colunas=("grupo", "talento", "n", "ultimo_pedido", "empate_fora", "talentos_grupo", "mes", "n_mes",
                               "pos", "_processado_em"), permite_vazia=True, em_fundo=not config.EM_PRODUCAO)
# A26 (D53): saídas sem entrega por mês do evento × status do board (dica do quadro do Atendimento)
saidas_status = Tabela("Saídas sem entrega por status", config.TAB_SAIDAS_STATUS, chave=("mes", "status"),
                       colunas=("mes", "status", "n", "sem_data", "_processado_em"), permite_vazia=True,
                       em_fundo=not config.EM_PRODUCAO)
TABELAS = {"sla": sla, "sla_entregas": sla_entregas, "sla_entregas_status": sla_entregas_status, "entrada": entrada,
           "fluxo": fluxo, "fila": fila, "atendimento": atendimento, "talentos": talentos, "talentos_top": talentos_top,
           "saidas_status": saidas_status}


def versao_de(df: pd.DataFrame):
    """Identifica a carga de onde o DataFrame veio (para caches derivados); sem versão, a identidade do objeto."""
    return df.attrs.get("versao", id(df))


def base_congelada(fontes: list[dict]) -> bool:
    """Rodapé "base congelada para a apresentação": com o corte (D65), só quando todas as fontes da página já estão na
    carga do corte; sem o corte, o CONGELAR da D63."""
    if config.CORTE_DADOS is None:
        return config.CONGELAR
    return bool(fontes) and all(f.get("estado") == "congelada" for f in fontes)
