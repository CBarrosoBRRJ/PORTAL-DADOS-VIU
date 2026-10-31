"""Gestão de orçamentos: apresentação com seções no navegador do topo.

Ordem da reunião (D30): Início (entrada) → Talentos → Atendimento → SLA → Previsão → Resultado (negócios
fechados) → Qualidade, e no fim "O que falta". Seções sem base mostram a pergunta com máscara (pendencias.py).
"""

import copy
import hashlib
import json
import logging
import threading

import pandas as pd

from app import config, dados, sla
from app.apresentacoes import Apresentacao, Secao
from app.apresentacoes.gestao_orcamentos import SLUG, iniciativas, lia, lia_na_pratica, pendencias, roadmap
from app.apresentacoes.gestao_orcamentos.atendimento import calculos as atendimento
from app.apresentacoes.gestao_orcamentos.entrada import calculos as entrada
from app.apresentacoes.gestao_orcamentos.previsao import calculos as previsao
from app.apresentacoes.gestao_orcamentos.previsao import job as previsao_job
from app.apresentacoes.gestao_orcamentos.sla import calculos
from app.apresentacoes.gestao_orcamentos.talentos import calculos as talentos

log = logging.getLogger(__name__)


def montar_sla(params: dict) -> dict:
    mov = (
        dados.sla.df()
    )  # base: a tabela gold inteira (C4); cálculos ficam em cache até a tabela mudar
    grupo = (
        params.get("talentos") if params.get("talentos") in calculos.GRUPOS else "todos"
    )
    parcial = sla.mes_parcial(mov)
    return {
        # desempenho (31/10/2026): a tela do SLA guardada por carga, mês parcial e grupo (~70 ms de pandas a cada clique)
        "entrega": _guardado("sla", (mov,), (parcial, grupo), lambda: calculos.entrega(mov, parcial, grupo)),
        # uma página só, sem botões de slide (24/10/2026): mesmo layout congelado das outras seções
        "sem_controles": True,
    }


def medida_capa() -> float | None:
    """D61: o número em que o relógio da capa para = o típico do SLA de todos os talentos (o mesmo "14 h" da página do
    SLA, C6). Sem a base do SLA, None: a capa mostra a jornada sem o número."""
    try:
        return montar_sla({})["entrega"]["mediana_h_trabalho"]
    except (dados.DadosIndisponiveis, KeyError, TypeError):
        return None


def _estudo_slides(mov: pd.DataFrame, parcial: str, grupo: str) -> dict:
    """Slides 2–8 do estudo (só dependem da carga, do mês parcial e do grupo). Guardados por carga e grupo (B-N7, batalha
    de agentes, 25/10/2026): o clique no seletor ou no passo não refaz as contas; a carga nova chega já aquecida."""
    chave = (dados.versao_de(mov), id(mov), len(mov), parcial, grupo)  # o objeto da carga no ar (o mesmo do aquecimento)
    with _trava_estudo:
        if chave in _cache_estudo:
            return _cache_estudo[chave]
    tempo = calculos.tempo_cem(mov, parcial, grupo)  # slide 4 (V1–V8, D40)
    meses = calculos.meses_estudo(mov, parcial, grupo)  # slide 5 (U1–U8, D41)
    trava = calculos.travas(mov, parcial, grupo)  # slide 6 (K1–K8, D42)
    tipos = calculos.tipos_pedido(mov, parcial, grupo)  # slide 7 (J1–J9, D43)
    r = {"exploracao": calculos.exploracao(mov, parcial, grupo),  # slide 2 (X1–X7)
         "cem": calculos.cem_pedidos(mov, parcial, grupo),  # slide 3 (W1–W7, D39)
         "tempo": tempo, "meses_estudo": meses, "travas": trava, "tipos": tipos, "mostrar_tipo": ESTUDO_TIPO,
         # slide 8 (Z1–Z8, D44): a conclusão usa os mesmos números dos slides 4–7; sem o slide 7 (D64), sem o achado
         # por tipo de pedido ({} = nenhum tipo)
         "conclusao": calculos.conclusao(mov, parcial, grupo, tempo=tempo, meses=meses, trava=trava,
                                         tipos=tipos if ESTUDO_TIPO else {}),
         "recorte": calculos.recorte(mov, parcial, grupo)}  # R1: período, N e grupo no topo dos slides 2–8
    with _trava_estudo:
        while len(_cache_estudo) >= 3 * len(calculos.GRUPOS):  # até 3 cargas × 3 grupos
            _cache_estudo.pop(next(iter(_cache_estudo)), None)
        _cache_estudo[chave] = r
    return r


def _aquecer_estudo(mov: pd.DataFrame) -> None:
    """B-N7: carga nova da gold com o estudo dos 3 grupos já calculado (ninguém espera na sala)."""
    parcial = sla.mes_parcial(mov)
    for grupo in calculos.GRUPOS:
        _estudo_slides(mov, parcial, grupo)


_cache_estudo: dict = {}
_trava_estudo = threading.Lock()

# Desempenho (31/10/2026): a troca de página precisa parecer instantânea. As contas de cada tela (pandas) só mudam com
# a carga: ficam guardadas por carga e parâmetros. A chave identifica cada DataFrame pela versão, pelo objeto e pelo
# tamanho (a mesma regra do estudo) e a entrada guarda o próprio DataFrame, para o id não ser reaproveitado por outro
# objeto enquanto a conta estiver guardada. Carga nova = chave nova; as antigas saem por ordem de chegada.
_cache_telas: dict = {}
_trava_telas = threading.Lock()
LIMITE_TELAS = 40


def _carga(df):
    return None if df is None else (dados.versao_de(df), id(df), len(df))


def _ambiente_calculo() -> tuple:
    """O que muda o resultado além da carga e dos parâmetros da URL: corte e congelamento (D65, também o estado de cada
    tabela), modo e a base mínima da variação (E9). Vai em toda chave de `_cache_telas` (F18)."""
    return (config.CORTE_DADOS, config.CONGELAR, config.DEV, config.MODO_APRESENTACAO, entrada.BASE_MINIMA_VARIACAO,
            tuple(bool(getattr(t, "congelada", False)) for t in dados.TABELAS.values()))


def limpar_caches() -> None:
    """Esvazia todas as contas guardadas por carga (telas, estudo, SLA, entrada, LIA, imagens do Roadmap): testes e
    mudança de parâmetro de cálculo (F18)."""
    with _trava_telas:
        _cache_telas.clear()
    with _trava_estudo:
        _cache_estudo.clear()
    calculos.limpar_cache()
    sla.limpar_cache()
    entrada._cache.clear()
    lia._cache.clear()
    roadmap._tamanhos.clear()


def _guardado(nome: str, dfs: tuple, extra: tuple, calcular):
    """F18: devolve sempre uma cópia (deepcopy) da conta guardada, para nenhuma requisição mexer na de outra. Carga nova
    da mesma tela descarta as entradas das cargas antigas."""
    chave = (nome, tuple(_carga(d) for d in dfs), extra, _ambiente_calculo())
    with _trava_telas:
        if chave in _cache_telas:
            return copy.deepcopy(_cache_telas[chave][1])
    valor = calcular()
    with _trava_telas:
        for k, (antigos, _) in list(_cache_telas.items()):
            if k[0] == nome and any(a is not b for a, b in zip(antigos, dfs)):
                _cache_telas.pop(k, None)  # carga antiga desta tela
        while len(_cache_telas) >= LIMITE_TELAS:
            _cache_telas.pop(next(iter(_cache_telas)), None)
        _cache_telas[chave] = (dfs, valor)
    return copy.deepcopy(valor)


# D64 (Caio, 29/10/2026): o slide 7 do estudo ("Em que tipo de pedido o tempo trava?") saiu da apresentação. Código e
# cálculos ficam; True o traz de volta (com ele, o achado por tipo volta à conclusão e a conclusão volta a ser o #8).
ESTUDO_TIPO = False


def montar_estudo_sla(params: dict) -> dict:
    # estudo "Como medimos" (24/10/2026): tela 1 = um orçamento real sorteado no dia (E1–E3), no grupo de talentos da volta
    mov = dados.sla.df()
    grupo = params.get("talentos") if params.get("talentos") in calculos.GRUPOS else "todos"
    parcial = sla.mes_parcial(mov)
    try:  # D-SLA-4: cobertura (N medidos de M entregues pela gold de fluxo); sem a tabela de fluxo, a linha some
        fluxo = dados.fluxo.df()
    except dados.DadosIndisponiveis:
        fluxo = None
    # E4 (B-N8): exemplo fixo revisado pelo Caio (?exemplo=<projeto_id>), só no computador (DEV) ou na reunião
    fixo = (params.get("exemplo") or None) if (config.DEV or config.MODO_APRESENTACAO) and not config.EM_PRODUCAO else None
    # o exemplo é o sorteio do dia (E1): o dia entra na chave
    return {"exemplo": _guardado("exemplo", (mov,), (parcial, grupo, fixo, calculos._hoje()),
                                 lambda: calculos.exemplo(mov, parcial, grupo, fixo=fixo)),
            "cobertura": _guardado("cobertura", (mov, fluxo), (parcial,),
                                   lambda: calculos.cobertura(mov, fluxo, parcial)),
            **_estudo_slides(mov, parcial, grupo),
            "grupos_estudo": [{"chave": k, "rotulo": rot, "atual": k == grupo} for k, (rot, _) in calculos.GRUPOS.items()]}


def montar_inicio(params: dict) -> dict:
    # página inicial: pedidos que entraram por mês e tipo de input, sempre no ano da carga, com a comparação ao ano
    # anterior (D23, D25, D26)
    df_entrada = dados.entrada.df()
    # desempenho (31/10/2026): números do ano e fotografia guardados por carga; o extrato do mês entra numa cópia rasa
    e = dict(_guardado("inicio", (df_entrada,), (), lambda: _inicio_base(df_entrada)))
    # extrato do mês clicado (?mes=AAAA-MM), só nos 6 meses mais recentes que já têm pedidos (E7). A lista vem da base
    # inteira e pode ter meses do ano anterior (B6); a tela por ora só abre os do ano mostrado, porque a forma de
    # mostrar os do ano anterior em janeiro ainda é decisão do Caio
    mes = params.get("mes", "")
    totais_do_ano = {m["chave"]: m["total"] for m in e["meses"]}
    validos = set(e["meses_extrato"]) & set(totais_do_ano)
    e["extrato"] = None
    e["extrato_em_atualizacao"] = False
    if mes in validos:
        df_fluxo, df_fila = dados.fluxo.df(), dados.fila.df()  # E7: extrato da view gold de fila (D57)
        e["extrato"] = entrada.extrato(df_fila, mes)
        # Cargas independentes podem se atualizar em momentos diferentes (B7). Não exibir um extrato de outro dia de
        # carga nem um cuja entrada contradiga a coluna selecionada
        dias_diferentes = (not _mesma_fotografia(df_entrada, df_fluxo)
                           or entrada.data_carga(df_fila) != entrada.data_carga(df_fluxo))
        e["extrato_em_atualizacao"] = bool(
            e["extrato"]
            and (dias_diferentes or e["extrato"]["entraram"] != totais_do_ano[mes])
        )
        if e["extrato_em_atualizacao"]:
            e["extrato"] = None
    return {"entrada": e}


def _inicio_base(df_entrada: pd.DataFrame) -> dict:
    e = entrada.entrada(df_entrada)
    # A troca parcial do extrato só é segura enquanto o gráfico e os totais
    # pertencem à mesma fotografia. O navegador recarrega se esta assinatura mudar.
    e["fotografia"] = hashlib.sha256(
        json.dumps(
            [
                e,
                str(df_entrada["_processado_em"].max())
                if "_processado_em" in df_entrada
                else None,
            ],
            sort_keys=True,
            default=str,
        ).encode()
    ).hexdigest()[:16]
    return e


def montar_atendimento(params: dict) -> dict:
    # quanto da demanda a equipe atende: entregas por mês contra as entradas, em quantidade e proporção (A1–A8, D27)
    diaria, fluxo, mensal = dados.entrada.df(), dados.fluxo.df(), dados.atendimento.df()
    coerente = _mesma_fotografia(diaria, fluxo) and entrada.data_carga(mensal) == entrada.data_carga(fluxo)
    a = atendimento.atendimento(diaria, fluxo, mensal) if coerente else None
    status = None
    if a:  # A26 (D53): composição por status da dica; sem a tabela, a dica mostra só o total
        try:
            status = atendimento.status_sem_entrega(a, dados.saidas_status.df())
        except Exception as e:  # noqa: BLE001 — a página não depende desta tabela
            log.warning("Composição por status das saídas sem entrega indisponível: %s", f"{type(e).__name__}: {e}"[:200])
    return {
        "atendimento": a,
        "status_sem": status,
        "fluxo_mes": atendimento.fluxo_mes(a, status) if a else None,  # A15/A27: números do ano (faixa de cima)
        "ritmo": atendimento.analise_ritmo(a, status) if a else None,  # A16/A27: quadro e dispersão mês a mês
        "em_atualizacao": not coerente,
        "sem_controles": True,
    }


def _mesma_fotografia(diaria, fluxo):
    """Contrato entre fontes: dia da carga e distribuição por safra, não só total geral. Decisão 5 (25/10/2026): só
    uma safra do ano exibido (o da carga, E0) bloqueia o extrato e o Atendimento; divergência numa safra de ano anterior
    (2024/2025) fica só registrada em log, porque a tela não mostra esses números."""
    d1, d2 = entrada.data_carga(diaria), entrada.data_carga(fluxo)
    if d1 is not None and d2 is not None:
        if d1 != d2:
            return False
        ultimo = entrada.ultimo_dia(diaria, entrada._base(diaria))
        recorte = diaria.loc[pd.to_datetime(diaria.data) <= ultimo]
        esperado = (
            (recorte.quantidade + recorte.quantidade_estimada)
            .groupby(pd.to_datetime(recorte.data).dt.to_period("M"))
            .sum()
        )
        obtido = fluxo.quantidade.groupby(
            pd.to_datetime(fluxo.mes_entrada).dt.to_period("M")
        ).sum()
        a, b = esperado.align(obtido, fill_value=0)
        diverge = a.index[a.ne(b)]
        if len(diverge):
            do_ano = [p for p in diverge if p.year == ultimo.year]
            antigas = [p for p in diverge if p.year != ultimo.year]
            if antigas:
                log.warning("Entrada e fluxo divergem em safras de anos anteriores (sem efeito na tela): %s",
                            ", ".join(f"{p}: entrada {int(a[p])} x fluxo {int(b[p])}" for p in antigas))
            if do_ano:
                return False
    return True


def montar_talentos(params: dict) -> dict:
    # como a demanda do ano se divide entre talentos exclusivos e não exclusivos (D30, T1–T5): mesmos pedidos do Início
    diaria, agregado, ranking = (
        dados.entrada.df(),
        dados.talentos.df(),
        dados.talentos_top.df(),
    )
    filtro = params.get("talentos") if params.get("talentos") in talentos.FILTROS else "todos"
    # desempenho (31/10/2026): a tela inteira guardada por carga das três tabelas e filtro
    return _guardado("talentos", (diaria, agregado, ranking), (filtro,),
                     lambda: _talentos(diaria, agregado, ranking, filtro))


def _talentos(diaria: pd.DataFrame, agregado: pd.DataFrame, ranking: pd.DataFrame, filtro: str) -> dict:
    e = entrada.entrada(diaria)
    t = talentos.divisao(agregado, e["total"], e["ano"])
    fim = min(
        entrada.ultimo_dia(diaria, entrada._base(diaria)),
        pd.Timestamp(e["ano"], 12, 31),
    ).date()
    # T5 (D57): as três tabelas gold saem do mesmo job; o dia da carga precisa ser o do Início (E3)
    carga_inicio = entrada.data_carga(diaria)
    carga = entrada.data_carga(agregado) if not agregado.empty else carga_inicio
    incoerente = bool(t and (t["diferenca"] or carga != carga_inicio))
    top_coerente = ranking.empty or entrada.data_carga(ranking) == carga
    # decisão 10 (25/10/2026): divergência com o Início mostra os números com o aviso da diferença (T5)
    if incoerente:
        log.warning("Talentos: divisão e Início divergem (talentos %s x Início %s; carga %s x %s)",
                    t["total"], t["total_inicio"], carga, carga_inicio)
    # D50 (T7–T10): o seletor filtra a página inteira; a barra do ano fica como contexto, com o grupo destacado
    top = talentos.top_por_grupo(ranking, t) if top_coerente else {}
    return {
        "talentos": t,
        "em_atualizacao": incoerente,
        "periodo": e["periodo"],
        "top": top,
        "filtro": filtro,
        "seletor": talentos.seletor(t, filtro) if t else [],
        "heroi": talentos.heroi(t, top, filtro) if t else None,
        "barra": talentos.barra(t, filtro) if t else [],
        "mapa": talentos.mapa(top.get(talentos.FILTROS[filtro][1]), fim) if t else None,
        "sem_controles": True,
    }


def montar_negocios_fechados(params: dict) -> dict:
    # página preparada: o board de orçamentos não registra negócio fechado; a base virá de outra tabela (D19)
    return {"sem_controles": True}


# F10 (auditoria de 31/10/2026): Roadmap, Iniciativas e o vídeo não mostram dados da gold; o rodapé (regra 9) diz isso em
# vez de repetir a data da carga de entradas
RODAPE_EDITORIAL = "Conteúdo editorial · não depende da carga de dados"


def montar_previsao(params: dict) -> dict:
    # previsão de demanda (D48): a página só lê o último previsao.json válido do job de ML (P1–P8); sem ele, a máscara.
    # Execução mensal (J1): mês fechado novo → retrato novo; mesma carga do mês → só o acompanhamento do mês em andamento
    grupo = params.get("talentos") if params.get("talentos") in previsao.GRUPOS else "todos"
    p = previsao.ler()
    qual = None
    try:  # a gold de entradas diz se há mês fechado novo ou carga nova (o rodapé datado também vem dela)
        df_entrada = dados.entrada.df()  # desempenho (31/10/2026): a data da carga guardada por carga
        qual = previsao_job.acao(p, *_guardado("previsao_carga", (df_entrada,), (),
                                               lambda: previsao_job.da_carga(df_entrada)))
    except dados.DadosIndisponiveis:
        pass
    # G1-N11: "sendo calculado" só com o job rodando de fato; com CONGELAR (J5) nada é anunciado; se a última tentativa
    # falhou, a página diz quando (ícone + texto), em vez de prometer um cálculo que não vem
    rodando = previsao_job.disparar(qual) or previsao_job.em_andamento()
    falha = None if rodando else previsao_job.falhou()
    # F03 (auditoria de 31/10/2026): o acompanhamento tem a sua data no rodapé e, se ele ou o retrato forem de outra carga
    # que a da gold de entradas (a do rodapé), um aviso discreto; nada volta ao topo da página (pedido do Caio, 31/10)
    c = previsao.coerencia(p, dados.entrada.processado_em()) if p else None
    return {"t": previsao.tela(p, grupo), "previsao_acao": qual if p and rodando else None,
            "previsao_falha": falha if p else None, "sem_controles": True,
            "rodape_extra": f"acompanhamento até {c['acompanhamento_ate']}" if c and c["acompanhamento_ate"] else None,
            "rodape_aviso": c["aviso"] if c else None}


def montar_iniciativas(params: dict) -> dict:
    # PRD Iniciativas (@cris, 30/10/2026): portfólio de automação e IA por fase; conteúdo fixo em iniciativas/catalogo.py
    return {"iniciativas": iniciativas.tela(), "sem_controles": True, "rodape_texto": RODAPE_EDITORIAL}


def montar_lia(params: dict) -> dict:
    # V2 (D-LIA-2, 30/10/2026): o que a LIA leu e filtrou (retrato agregado do Cloud Storage da LIA, gerado por
    # tools/extrair_lia.py); a análise de tempo na régua do SLA (D-LIA-1) ficou só na ficha. o extrato da semana
    # (D-LIA-4) foi retirado por decisão do Caio, 30/10/2026; ?semana= é ignorado
    # F20 (31/10/2026): a tela guardada por versão do retrato.json (data de modificação e tamanho), sem reler o JSON
    # F05/F10 (31/10/2026): retrato fora do contrato = None (lâmina de indisponível); rodapé com a data da própria LIA
    try:
        info = lia.RETRATO.stat()
    except OSError:
        t = lia.tela()  # sem o arquivo: None (indisponível)
    else:
        t = _guardado("lia", (), (str(lia.RETRATO), info.st_mtime_ns, info.st_size, lia.MINUTOS_TRIAGEM), lia.tela)
    if t is None:
        return {"lia": None, "sem_controles": True, "rodape_texto": "Dados da LIA indisponíveis"}
    t["video"] = lia_na_pratica.tela()  # o pop-up do vídeo segue os arquivos de app/static/video/ (barato, sem cache)
    return {"lia": t, "sem_controles": True,
            "rodape_texto": f"Dados da LIA até {t['fim_ano']} · extraídos em {t['extraido_em']}"}


def montar_lia_na_pratica(params: dict) -> dict:
    # V2 (PRD do slide do vídeo de @cris, adaptado): vídeo da LIA e as etapas que ele percorre (lia_na_pratica/)
    return {"pratica": lia_na_pratica.tela(), "sem_controles": True, "rodape_texto": RODAPE_EDITORIAL}


def montar_roadmap(params: dict) -> dict:
    # V2 (Caio, 30/10/2026): roadmap da área (substitui a Linha do tempo), sem datas e sem leitura de dados (roadmap/)
    # gancho_oculto (Caio, 30/10/2026): o Roadmap abre a reunião sem o gancho no canto; o link fica para o leitor de tela e a seta →
    return {"roadmap": roadmap.tela(), "sem_controles": True, "gancho_oculto": True, "rodape_texto": RODAPE_EDITORIAL}


def montar_qualidade(params: dict) -> dict:
    # em branco por enquanto (pedido do Caio); verificações prontas em qualidade.qualidade(dados.sla.df(), situação)
    return {"sem_controles": True}


# carga nova da gold: os cálculos ficam prontos antes de ela entrar no ar (ninguém espera o recálculo); entregas()
# relê as views do SLA da mesma carga
dados.sla.ao_carregar.append(calculos.entregas)
dados.sla.ao_carregar.append(_aquecer_estudo)  # B-N7: estudo dos 3 grupos
dados.entrada.ao_carregar.append(previsao_job.ao_carregar_entrada)  # D48 (J1): mês fechado novo → retrato; senão, acompanhamento

# D61 (Caio, 27/10/2026): textos das capas de seção ("" = Demanda, a página inicial). Desligadas no mesmo dia; guardadas
# aqui para religar (Apresentacao.capas_secao)
CAPAS_SECAO = {
    "": {"titulo": "Tudo começa no pedido que chega.",
         "sub": "Quanto chegou em 2026, por tipo de input, e como se compara a 2025."},
    "talentos": {"titulo": "Quem são os talentos mais demandados.",
                 "sub": "Exclusivos e não exclusivos, e os dez que mais recebem pedidos."},
    "atendimento": {"titulo": "Do que chega ao que entregamos.",
                    "sub": "Mês a mês: o que entrou, o que saiu e o que ficou para o mês seguinte."},
    "sla": {"titulo": "Do pedido à primeira versão: quanto tempo leva.",
            "sub": "O relógio corre da entrada até a entrega ao cliente, em horas úteis."},
    "previsao": {"titulo": "Um estudo em andamento: o que deve chegar.",
                 "sub": "Modelos testados de junho a setembro; a escolha final ainda está em aberto."},
}

APRESENTACAO = Apresentacao(
    slug=SLUG,  # Caio, 31/10/2026: /viu-agenciamento (antes /gestao-orcamentos, que redireciona)
    titulo="Orçamentos",
    cabecalho="ViU Agenciamento",  # Caio, 31/10/2026: nome ao lado do logo em todas as páginas
    ordem=1,
    inicio=montar_inicio,
    tabelas_inicio=("entrada", "fluxo", "fila"),
    pendencias=pendencias.PENDENCIAS,
    pedidos=pendencias.PEDIDOS,
    pergunta_inicio="Quantos pedidos de orçamento chegaram ao longo do ano?",
    # D59 (Caio, 27/10/2026): capa e encerramento da reunião; a página inicial vira a 1ª análise, "Demanda".
    # D61 (Caio, 27/10/2026): capa e encerramento no desenho do relatório de referência do Caio (diagonal marinho, jornada
    # de um pedido cujo relógio para no típico do SLA) e capas de seção entre as páginas (só pelas setas)
    rotulo_inicio="Demanda",
    capa={
        # V2 (Caio, 30/10/2026): a capa passa a falar da ViU Agenciamento como um todo, não só dos orçamentos
        "titulo": "ViU Agenciamento em 2026",  # nome da capa no roteiro (a aba mostra só "ViU Agenciamento")
        "sobre": "Relatório da área",
        "titulo_1": "ViU",
        "titulo_2": "Agenciamento",
        # V2 (Caio, 30/10/2026): subtítulo discreto sob o título; o relatório reúne tudo o que a área analisa e faz
        "subtitulo": "Tudo o que a área analisa, constrói e entrega, num só lugar.",
        "data": "Outubro de 2026",
        "medida": medida_capa,  # típico do SLA (todos), lido na hora da página
        # jornada de um pedido (ilustração): f = fração do típico do SLA no medidor; o relógio para na 1ª entrega (C1);
        # frase = o que aparece ao lado das horas, trocando em roleta junto com a etapa (Caio, 27/10/2026)
        "etapas": (
            {"nome": "O pedido chega", "frase": "Chegou a demanda", "status": "Entrada", "cor": "azul", "icone": "envelope", "f": 0.0,
             "nota": "O relógio começa a contar."},
            {"nome": "Elaboração do orçamento", "frase": "Em elaboração", "status": "Elaboração", "cor": "ambar", "icone": "lapis", "f": 0.55,
             "nota": "A equipe monta a proposta."},
            {"nome": "Revisão", "frase": "Passou para revisão", "status": "Revisão", "cor": "lilas", "icone": "checks", "f": 0.75,
             "nota": "Conferência antes de seguir."},
            {"nome": "Validação do talento e cotação", "frase": "Validação do talento", "status": "Validação", "cor": "lilas", "icone": "checks", "f": 0.9,
             "nota": "O talento confirma; o valor fecha."},
            {"nome": "Proposta enviada ao cliente", "frase": "Proposta enviada ao cliente", "status": "Aguardando Feedback", "cor": "amarelo", "icone": "relogio",
             "f": 1.0, "nota": "Agora conta o tempo do cliente."},
            {"nome": "Desfecho", "frase": "Retorno do cliente", "status": "Negócio fechado", "cor": "neutro", "icone": "seta", "f": 1.0,
             "nota": "Muda a cada pedido.", "variacoes": ("Negócio fechado", "Ajuste", "Declinado", "Sem retorno")},
        ),
    },
    encerramento={
        "gancho": "Encerramento",  # Caio, 31/10/2026: o gancho da última página só anuncia o encerramento
        "sobre": "ViU Agenciamento",  # Caio, 31/10/2026
        "titulo": "Obrigado.",
        "frase": "",  # Caio, 31/10/2026: "Próximo passo…" e "Dúvidas e sugestões?" saíram da tela
        "pergunta": "",
        "voltar": "Voltar ao início",
    },
    # D61: capas de seção entre as páginas (pelas setas) — DESLIGADAS a pedido do Caio no mesmo dia ("enchem linguiça");
    # ficam só a capa e o encerramento. Para religar: capas_secao=CAPAS_SECAO
    capas_secao=None,
    secoes=(
        Secao(
            slug="roadmap",
            titulo="Roadmap da área",
            montar=montar_roadmap,
            tabelas=("entrada",),  # só para o rodapé datado (regra 9); a página não lê dados
            icone="lista",
            rotulo="Roadmap",
            nota_estado="ordem e textos a confirmar com o Caio",
            antes_do_inicio=True,  # V2 (Caio, 30/10/2026): 1ª página depois da capa, antes da Demanda
            pergunta="Como chegamos até aqui?",  # Caio, 30/10/2026: sem o "e para onde vamos"
        ),
        Secao(
            slug="talentos",
            titulo="Talentos",
            montar=montar_talentos,
            tabelas=("entrada", "talentos", "talentos_top"),
            icone="pessoas",
            estado="pronta",
            filtro_talentos=True,  # D50 (T7): o seletor volta; abas e "Próxima pergunta" levam o recorte
            pergunta="Como a demanda se divide entre talentos exclusivos e não exclusivos?",
        ),
        Secao(
            slug="atendimento",
            titulo="Atendimento",
            montar=montar_atendimento,
            tabelas=("entrada", "fluxo", "atendimento", "saidas_status"),
            icone="grafico",
            oculta=True,  # V2 (Caio, 30/10/2026): fora deste relatório (navegação, capa e sequência); código e endereço mantidos
            pergunta="A equipe está dando conta da demanda?",
        ),
        Secao(
            slug="sla",
            titulo="SLA de entrega",
            montar=montar_sla,
            montar_estudo=montar_estudo_sla,
            tabelas=("sla", "sla_entregas", "sla_entregas_status"),
            icone="relogio",
            rotulo="SLA",  # Caio, 24/10/2026: a aba volta a se chamar SLA
            nota_estado="meta a oficializar",  # G2-4: a meta de 2 dias de trabalho ainda é sugestão (PEDIDOS)
            filtro_talentos=True,
            pergunta="Quanto tempo levamos para entregar um orçamento?",
        ),
        Secao(
            slug="lia",
            titulo="LIA: e-mails lidos e filtrados",
            montar=montar_lia,
            tabelas=("entrada",),  # só para o rodapé datado (regra 9); o slide lê o retrato da LIA, não a gold
            icone="envelope",
            rotulo="LIA",
            nota_estado="retrato do Cloud Storage da LIA, a conferir com a equipe",
            pergunta="Quanto a LIA já leu e quanto deixou de chegar à equipe?",
        ),
        Secao(
            slug="lia-na-pratica",
            titulo="A LIA na prática",
            montar=montar_lia_na_pratica,
            tabelas=("entrada",),  # só para o rodapé datado (regra 9); o slide não lê dados
            icone="video",
            rotulo="Vídeo",
            # V2 (Caio, 30/10/2026): o vídeo virou o pop-up do botão "Ver a LIA na prática" da página LIA; a página fica
            # fora da navegação, da capa e da sequência, e o endereço continua abrindo (destino do botão sem JS)
            oculta=True,
            estado="pendente",  # PRD RF7: com o vídeo incluído, vira "pronta" e a nota sai
            nota_estado="vídeo a incluir",
            pergunta="A LIA na prática: do e-mail à carta orçamento",
        ),
        Secao(
            slug="iniciativas",
            titulo="Iniciativas de automação e IA",
            montar=montar_iniciativas,
            tabelas=("entrada",),  # só para o rodapé datado (regra 9); o slide não lê dados
            icone="faisca",
            rotulo="Iniciativas",
            nota_estado="andamento de agosto, a atualizar",  # pendência do PRD: confirmar a data de referência
            pergunta="Quais iniciativas de automação e IA estamos tocando?",
        ),
        Secao(
            slug="previsao",
            titulo="Previsão de demanda",
            montar=montar_previsao,
            tabelas=("entrada",),
            icone="tendencia",
            rotulo="Previsão",
            filtro_talentos=True,
            estado="pronta",
            nota_estado="2 decisões abertas",  # G2-4 (D48): vencedor do Mercado e nov/dez como previsão ou cenário
            pergunta="Quantos pedidos devem chegar até o fim do mês e do ano?",
        ),
        Secao(
            slug="negocios-fechados",
            titulo="Resultado: negócios fechados",
            montar=montar_negocios_fechados,
            icone="selo",
            rotulo="Resultado",
            estado="pendente",
            na_reuniao=False,  # G2-4: a página não vai existir agora; na reunião, a Previsão leva à Qualidade
            oculta=True,  # D59 (Caio, 27/10/2026): fora da navegação por ora; código e endereço mantidos
            pergunta="Quanto do que entregamos vira contratação?",
        ),
        Secao(
            slug="qualidade",
            titulo="Qualidade dos dados",
            montar=montar_qualidade,
            tabelas=("sla", "entrada", "fluxo"),  # G2-5: rodapé datado e selo do menu também na máscara
            icone="escudo",
            rotulo="Qualidade",
            estado="pendente",
            oculta=True,  # D59 (Caio, 27/10/2026): fora da navegação por ora (a Previsão leva ao "O que falta"); código e endereço mantidos
            pergunta="Dá para confiar nos números desta área?",
        ),
    ),
)
