"""D65 (Caio, 31/10/2026): corte e congelamento dos dados para a reunião de 04/11/2026 (outubro completo).

Regra (config.CORTE_DADOS, padrão 2026-10-31; CORTE_DADOS=off desliga):
- K1 O fim de uma carga é a regra E3 (app/corte.py): véspera do dia, em São Paulo, do `_processado_em`.
- K2 Fim < corte: carga aceita normalmente (o portal continua atualizando).
- K3 Corte <= fim <= corte + CORTE_FOLGA_DIAS: é a ÚLTIMA carga aceita. A tabela congela EM MEMÓRIA. A folga (1 dia)
     existe porque 31/10/2026 é sábado e a carga agendada seguinte (seg 02/11, 09:00) cobre até 01/11 (E3).
- K4 Fim > corte + folga: carga ignorada (a tabela fica com o que tinha e a falha aparece). Com a base já congelada,
     nenhuma carga é sequer consultada.
- K5 Todas as tabelas congelam na MESMA carga: uma tabela cuja carga tem outro fim que o das já congeladas é ignorada (K4).
- K6 Com a base válida em arquivo e do mesmo corte, a tabela nasce dela: nenhuma consulta ao BigQuery. É assim em
     produção (Cloud Run): a pasta fica dentro de app/, entra na imagem pelo `COPY app/` do Dockerfile, o build a confere
     (`python -m app.conferir_base`) e o arranque também (`exigir`): em produção, com o corte ligado, o serviço não sobe
     sem a base completa e nunca chama o BigQuery. Em produção nada é gravado (o disco do Cloud Run não persiste).
- K7 Base de outro corte, sem manifesto, incompleta ou com hash diferente: ignorada INTEIRA (aviso no log); as tabelas
     seguem a regra K2–K5 (no computador) ou ficam indisponíveis (em produção, onde o arranque já teria falhado).

Base como unidade (auditoria do Codex, 31/10/2026, F02/F07/F08):
- B1 Congelada em memória ≠ persistida. Cada tabela congela em memória (K3) e se registra aqui; a base só é gravada
     quando TODAS as tabelas do portal (dados.TABELAS) estiverem congeladas na mesma carga, e só fica "persistida"
     depois de gravada E conferida (hash e linhas relidos do disco). Falhou? Erro no log e no /saude, nova tentativa a
     cada TENTATIVA_S segundos (na próxima leitura da tabela) ou pelo `tools/congelar_base.py`.
- B2 Um escritor por vez: trava entre processos (arquivo `.escrita.lock` criado com O_EXCL; trava com mais de
     TRAVA_VELHA_S é considerada abandonada) e, dentro do processo, uma trava de thread.
- B3 Publicação atômica do conjunto: os parquets vão para uma pasta de versão nova e exclusiva (`v-<fim>-<momento>-<hex>`),
     com uma cópia do manifesto gravada por último; a base só passa a valer quando o `manifesto.json` da raiz, que aponta
     para essa pasta, é trocado com `os.replace` (atômico). Pasta de versão sem o manifesto da raiz apontando para ela é
     ignorada. Nada se apaga: versões anteriores ficam (mover para _descartados depois, se quiser).
- B4 A leitura valida o manifesto global (formato, corte, fim dentro da folga, um só fim, todas as tabelas do portal,
     arquivo, sha256 e linhas) antes de entregar qualquer tabela.
- B5 Recuperação (`recuperar`, `tools/congelar_base.py --recuperar`): sem manifesto válido na raiz, publica a versão mais
     nova cujo manifesto interno confere inteiro (gravação interrompida depois de completa); pastas sem manifesto interno
     são parciais e só são relatadas. Sem versão completa, a base é refeita do BigQuery enquanto a carga estiver na folga.

Nenhuma regra de negócio aqui (D57): o corte só escolhe QUAL carga da gold o portal mostra; as linhas não são filtradas.
Roteiro do dia 02/11 e de como descongelar: docs/congelar_outubro.md. Ferramentas: tools/congelar_base.py e
app/conferir_base.py (conferência sem rede, usada no build).
"""

import hashlib
import json
import os
import re
import secrets
import threading
import time
from contextlib import contextmanager
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import pandas as pd

from app import config, corte

FORMATO = 2  # 1 = uma ficha solta por tabela (até 31/10/2026, _descartados/2026-10-31/congelamento_por_tabela/)
MANIFESTO = "manifesto.json"
TRAVA = ".escrita.lock"
TRAVA_VELHA_S = 15 * 60  # trava mais velha que isso: o processo que gravava morreu
TENTATIVA_S = 30  # intervalo mínimo entre duas tentativas de gravar a base (B1)


class ForaDoCorte(RuntimeError):
    """Carga recusada pelo corte (K4/K5): a tabela continua com a carga que tinha."""


class BaseInvalida(RuntimeError):
    """Base congelada ausente, incompleta ou incoerente com o manifesto (K7, B4)."""


class Ocupada(RuntimeError):
    """Outro processo está gravando a base (B2)."""


def ligado() -> bool:
    return config.CORTE_DADOS is not None


def limite() -> date:
    return config.CORTE_DADOS + timedelta(days=config.CORTE_FOLGA_DIAS)


def pasta() -> Path:
    return Path(config.BASE_CONGELADA_DIR)


def nome(tabela) -> str:
    """Nome do arquivo de uma tabela: o último trecho do id (ex.: gld_agenciamento_entrada_diaria)."""
    return re.sub(r"[^A-Za-z0-9_-]", "_", tabela.id_tabela.split(".")[-1]) or "tabela"


def esperadas() -> dict:
    """As tabelas que formam a base: todas as do portal (nome do arquivo → Tabela)."""
    from app import dados  # import tardio: dados importa este módulo

    return {nome(t): t for t in dados.TABELAS.values()}


def fim_da_carga(df: pd.DataFrame) -> date | None:
    """K1: último dia coberto pela carga; None sem `_processado_em` (bases de teste, tabela vazia)."""
    if "_processado_em" not in df or not df["_processado_em"].notna().any():
        return None
    return corte.fim(df["_processado_em"])


def _log(severidade: str, mensagem: str, **campos) -> None:
    from app.dados import log  # import tardio: dados importa este módulo

    log(severidade, mensagem, **campos)


def _sha(caminho: Path) -> str:
    return hashlib.sha256(caminho.read_bytes()).hexdigest()


def _iso(valor) -> str | None:
    if valor is None or (not isinstance(valor, datetime) and pd.isna(valor)):
        return None
    return pd.Timestamp(valor).isoformat()


def _processado(df: pd.DataFrame):
    if "_processado_em" not in df or not df["_processado_em"].notna().any():
        return None
    return pd.to_datetime(df["_processado_em"], utc=True).max()


# ---------------------------------------------------------------- estado do processo (B1)

_trava = threading.RLock()
_memoria: dict[str, dict] = {}  # nome → {"tabela", "df", "modificada_em", "fim"}: congeladas em memória (K3)
_estado: dict = {}
_validado: dict = {}


def _reiniciar() -> None:
    """Estado limpo (subida do processo e testes)."""
    with _trava:
        _memoria.clear()
        _validado.clear()
        _estado.clear()
        _estado.update(persistida=False, versao=None, erro=None, tentativas=0, ultima_tentativa=None,
                       ultima_tentativa_em=None, gravada_em=None)


_reiniciar()


# ---------------------------------------------------------------- decisão do corte (K2–K5)

def decidir(tabela, df: pd.DataFrame) -> str:
    """K2–K5 para uma carga nova do BigQuery: "aceitar" ou "congelar"; ForaDoCorte se for para ignorar."""
    if not ligado():
        return "aceitar"
    fim = fim_da_carga(df)
    if fim is None or fim < config.CORTE_DADOS:
        return "aceitar"
    if fim > limite():
        raise ForaDoCorte(f"carga com dados até {fim:%d/%m/%Y}, depois do corte de {config.CORTE_DADOS:%d/%m/%Y} "
                          f"(folga de {config.CORTE_FOLGA_DIAS} dia): ignorada")
    with _trava:
        outros = {r["fim"] for n, r in _memoria.items() if n != nome(tabela)}
    if outros and outros != {fim}:
        raise ForaDoCorte(f"carga com dados até {fim:%d/%m/%Y}, mas a base congelada das outras tabelas é de outra "
                          f"carga ({', '.join(sorted(f'{o:%d/%m/%Y}' for o in outros))}): ignorada")
    return "congelar"


def registrar(tabela, df: pd.DataFrame, modificada_em) -> None:
    """B1: a tabela congelou em memória (K3); tenta gravar a base se o conjunto já estiver completo. Nunca levanta."""
    with _trava:
        _memoria[nome(tabela)] = {"tabela": tabela, "df": df, "modificada_em": modificada_em, "fim": fim_da_carga(df)}
        _estado["persistida"] = False
    _log("WARNING", "tabela congelada em memória no corte", tabela=tabela.id_tabela, corte=config.CORTE_DADOS,
         fim=fim_da_carga(df), faltam=len(pendentes()))
    persistir(forcar=True)


def pendentes() -> list[str]:
    """Tabelas do portal que ainda não congelaram em memória."""
    with _trava:
        return sorted(n for n in esperadas() if n not in _memoria)


def persistida() -> bool:
    return bool(_estado.get("persistida"))


def persistir_pendente() -> None:
    """Chamado a cada leitura de uma tabela congelada: retenta a gravação (B1) sem esperar por outra thread."""
    if _estado.get("persistida") or not ligado() or config.EM_PRODUCAO or not _memoria:
        return
    if not _trava.acquire(blocking=False):
        return
    try:
        persistir()
    finally:
        _trava.release()


def persistir(forcar: bool = False) -> bool:
    """B1–B3: grava e confere a base inteira quando todas as tabelas congelaram na mesma carga. True = persistida.
    Sem forcar, respeita TENTATIVA_S desde a última tentativa. Nunca levanta: a falha fica em _estado e no log."""
    if not ligado() or config.EM_PRODUCAO:
        return False
    with _trava:
        if _estado["persistida"]:
            return True
        faltam = pendentes()
        if faltam:
            return False  # ainda não é uma base inteira: nada a gravar (o /saude mostra quais faltam)
        ultima = _estado["ultima_tentativa"]
        if not forcar and ultima is not None and time.monotonic() - ultima < TENTATIVA_S:
            return False
        _estado.update(tentativas=_estado["tentativas"] + 1, ultima_tentativa=time.monotonic(),
                       ultima_tentativa_em=datetime.now(config.FUSO).isoformat(timespec="seconds"))
        registros = {n: _memoria[n] for n in esperadas()}
        try:
            fins = {r["fim"] for r in registros.values()}
            if len(fins) != 1:
                raise BaseInvalida(f"tabelas congeladas em cargas diferentes: {sorted(map(str, fins))}")
            fim = next(iter(fins))
            with _trava_escrita():
                try:  # outro processo pode ter publicado enquanto esta carga congelava
                    atual = validar(usar_cache=False)
                except BaseInvalida:
                    atual = None
                if atual is not None:
                    if atual["fim"] != fim.isoformat():
                        raise BaseInvalida(f"a base gravada é de outra carga (dados até {atual['fim']}); a desta "
                                           f"memória vai até {fim:%Y-%m-%d}. Ver docs/congelar_outubro.md")
                    versao = atual["pasta"]
                else:
                    versao = _gravar_conjunto(registros, fim)
            _estado.update(persistida=True, versao=versao, erro=None,
                           gravada_em=datetime.now(config.FUSO).isoformat(timespec="seconds"))
            _log("WARNING", "base congelada gravada e conferida", versao=versao, tabelas=len(registros),
                 corte=config.CORTE_DADOS, fim=fim)
            return True
        except Exception as e:  # noqa: BLE001 — disco, trava, coerência: a base segue em memória e a gravação é retentada
            _estado["erro"] = f"{type(e).__name__}: {e}"[:300]
            _log("ERROR", "falha ao gravar a base congelada; segue congelada só em memória e será tentada de novo",
                 erro=_estado["erro"], tentativas=_estado["tentativas"], nova_tentativa_em_s=TENTATIVA_S)
            return False


@contextmanager
def _trava_escrita():
    """B2: um escritor por vez entre processos (servidor da 8400, tools/congelar_base.py, servidor de conferência)."""
    pasta().mkdir(parents=True, exist_ok=True)
    arq = pasta() / TRAVA
    fd = None
    for tentativa in (1, 2):
        try:
            fd = os.open(arq, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            break
        except FileExistsError:
            try:
                idade = time.time() - arq.stat().st_mtime
            except OSError:
                continue  # sumiu entre as duas chamadas: tenta de novo
            if tentativa == 1 and idade > TRAVA_VELHA_S:
                _log("WARNING", "trava de escrita abandonada; assumindo", arquivo=str(arq), idade_s=round(idade))
                try:
                    os.remove(arq)
                except OSError:
                    pass
                continue
            raise Ocupada(f"outro processo está gravando a base congelada ({arq.name}, há {idade:.0f} s)")
    if fd is None:
        raise Ocupada(f"não foi possível criar a trava {arq.name}")
    try:
        os.write(fd, json.dumps({"pid": os.getpid(), "em": datetime.now(config.FUSO).isoformat()}).encode())
        os.close(fd)
        yield
    finally:
        try:
            os.remove(arq)
        except OSError:
            pass


def _gravar_conjunto(registros: dict[str, dict], fim: date) -> str:
    """B3: pasta de versão exclusiva → parquets → manifesto interno → conferência → manifesto da raiz (os.replace)."""
    agora = datetime.now(config.FUSO)
    versao = f"v-{fim:%Y%m%d}-{agora:%Y%m%dT%H%M%S}-{secrets.token_hex(3)}"
    destino = pasta() / versao
    destino.mkdir(parents=True, exist_ok=False)  # exclusiva: dois escritores nunca usam a mesma pasta
    tabelas, processados = {}, []
    for n, r in sorted(registros.items()):
        df, t = r["df"], r["tabela"]
        copia = df.copy()
        copia.attrs = {}  # versão e metadados da memória não vão para o arquivo
        arq = destino / f"{n}.parquet"
        copia.to_parquet(arq, index=False)
        proc = _processado(df)
        if proc is not None:
            processados.append(proc)
        tabelas[n] = {"tabela": t.id_tabela, "nome": t.nome, "arquivo": arq.name, "sha256": _sha(arq),
                      "linhas": int(len(df)), "colunas": list(map(str, df.columns)), "fim": fim_da_carga(df).isoformat()
                      if fim_da_carga(df) else None, "processado_em": _iso(proc), "modificada_em": _iso(r["modificada_em"])}
    manifesto = {"formato": FORMATO, "corte": config.CORTE_DADOS.isoformat(), "folga_dias": config.CORTE_FOLGA_DIAS,
                 "fim": fim.isoformat(), "processado_em": _iso(max(processados)) if processados else None,
                 "pasta": versao, "gravado_em": agora.isoformat(timespec="seconds"), "pandas": pd.__version__,
                 "tabelas": tabelas}
    texto = json.dumps(manifesto, ensure_ascii=False, indent=2)
    (destino / MANIFESTO).write_text(texto, encoding="utf-8")  # por último: a versão está completa (B5)
    problemas = _conferir(manifesto, destino, ler_parquet=True)
    if problemas:
        raise BaseInvalida("conferência da gravação: " + "; ".join(problemas))
    _publicar(texto, versao)
    validado = validar(usar_cache=False)
    if validado["pasta"] != versao:
        raise BaseInvalida(f"manifesto publicado aponta para {validado['pasta']}, esperado {versao}")
    return versao


def _publicar(texto: str, versao: str) -> None:
    tmp = pasta() / f".{MANIFESTO}.{versao}.{os.getpid()}.tmp"  # temporário exclusivo
    tmp.write_text(texto, encoding="utf-8")
    os.replace(tmp, pasta() / MANIFESTO)  # atômico: o leitor vê o conjunto antigo ou o novo, nunca a mistura
    _validado.clear()


# ---------------------------------------------------------------- leitura e conferência (B4)

def _conferir(m: dict, destino: Path, ler_parquet: bool = False) -> list[str]:
    """Problemas de um manifesto frente à pasta da versão; lista vazia = base completa e coerente."""
    p = []
    if not isinstance(m, dict) or m.get("formato") != FORMATO:
        return [f"manifesto de outro formato ({m.get('formato') if isinstance(m, dict) else type(m).__name__})"]
    if m.get("corte") != config.CORTE_DADOS.isoformat():
        return [f"base de outro corte ({m.get('corte')}, em vigor {config.CORTE_DADOS.isoformat()})"]
    try:
        fim = date.fromisoformat(m["fim"])
    except (KeyError, TypeError, ValueError):
        return ["manifesto sem o fim da carga"]
    if not config.CORTE_DADOS <= fim <= limite():
        p.append(f"fim da carga {fim:%d/%m/%Y} fora do corte {config.CORTE_DADOS:%d/%m/%Y} + folga")
    tabelas = m.get("tabelas") or {}
    faltam = sorted(set(esperadas()) - set(tabelas))
    sobram = sorted(set(tabelas) - set(esperadas()))
    if faltam:
        p.append(f"incompleta: faltam {', '.join(faltam)}")
    if sobram:
        p.append(f"tabelas que o portal não conhece: {', '.join(sobram)}")
    if not destino.is_dir():
        return p + [f"pasta da versão {destino.name} ausente"]
    dias = set()
    for n, info in sorted(tabelas.items()):
        arq = destino / str(info.get("arquivo", ""))
        if info.get("fim") != m["fim"]:
            p.append(f"{n}: carga até {info.get('fim')}, a base é até {m['fim']}")
        if info.get("processado_em"):
            dias.add(corte.dia_da_carga(info["processado_em"]))
        if not arq.is_file():
            p.append(f"{n}: arquivo {arq.name} ausente")
            continue
        if _sha(arq) != info.get("sha256"):
            p.append(f"{n}: arquivo diferente do registrado (sha256)")
            continue
        if ler_parquet:
            try:
                df = pd.read_parquet(arq)
            except Exception as e:  # noqa: BLE001
                p.append(f"{n}: parquet ilegível ({type(e).__name__})")
                continue
            if len(df) != info.get("linhas") or list(map(str, df.columns)) != info.get("colunas"):
                p.append(f"{n}: linhas ou colunas diferentes do manifesto")
    if len(dias) > 1:
        p.append(f"tabelas processadas em dias diferentes: {sorted(map(str, dias))}")
    return p


def validar(usar_cache: bool = True) -> dict:
    """B4: o manifesto da raiz, conferido inteiro; BaseInvalida se ausente, incompleto ou incoerente."""
    if not ligado():
        raise BaseInvalida("corte desligado")
    arq = pasta() / MANIFESTO
    try:
        info = arq.stat()
    except OSError:
        raise BaseInvalida(f"sem {MANIFESTO} em {pasta()}") from None
    chave = (info.st_mtime_ns, info.st_size, config.CORTE_DADOS, config.CORTE_FOLGA_DIAS, str(pasta()),
             tuple(sorted(esperadas())))
    if usar_cache and _validado.get("chave") == chave:
        if _validado.get("erro"):
            raise BaseInvalida(_validado["erro"])
        return _validado["m"]
    try:
        m = json.loads(arq.read_text(encoding="utf-8"))
        problemas = _conferir(m, pasta() / str(m.get("pasta", "")) if isinstance(m, dict) else pasta())
    except (OSError, ValueError) as e:
        problemas = [f"manifesto ilegível ({type(e).__name__})"]
        m = None
    if problemas:
        erro = "; ".join(problemas)[:500]
        _validado.update(chave=chave, m=None, erro=erro)
        raise BaseInvalida(erro)
    _validado.update(chave=chave, m=m, erro=None)
    return m


def ler(tabela) -> tuple[pd.DataFrame, datetime | None, dict] | None:
    """K6/K7: (carga congelada, `modified` da tabela na hora do congelamento, ficha do manifesto) ou None se não houver
    base válida para o corte em vigor (a base é lida como unidade: um problema em qualquer tabela invalida todas)."""
    if not ligado():
        return None
    try:
        m = validar()
        ficha = m["tabelas"][nome(tabela)]
        df = pd.read_parquet(pasta() / m["pasta"] / ficha["arquivo"])
        if len(df) != ficha.get("linhas"):
            raise BaseInvalida("número de linhas diferente do registrado no manifesto")
    except (OSError, ValueError, KeyError, BaseInvalida) as e:
        if (pasta() / MANIFESTO).exists() or config.EM_PRODUCAO:
            _log("WARNING", "base congelada ignorada", tabela=tabela.id_tabela, erro=f"{type(e).__name__}: {e}"[:300])
        return None
    with _trava:
        _estado.update(persistida=True, versao=m["pasta"], erro=None)
    modificada = ficha.get("modificada_em")
    modificada = pd.Timestamp(modificada).to_pydatetime() if modificada else datetime.now(timezone.utc)
    return df, modificada, ficha


def exigir() -> dict | None:
    """F01: em produção, com o corte ligado, o serviço só sobe com a base congelada completa e coerente (BaseInvalida
    derruba o arranque; o Cloud Run mantém a revisão anterior). Corte desligado: None, nada a exigir."""
    if not ligado():
        return None
    m = validar(usar_cache=False)
    _log("INFO", "base congelada conferida no arranque", versao=m["pasta"], fim=m["fim"], tabelas=len(m["tabelas"]))
    return m


def situacao() -> dict:
    """Para o /saude: congelada em memória × persistida e validada (F02)."""
    if not ligado():
        return {"corte": None}
    try:
        m = validar()
        manifesto, versao, fim = "valido", m["pasta"], m["fim"]
    except BaseInvalida as e:
        manifesto = "ausente" if not (pasta() / MANIFESTO).exists() else f"invalido: {e}"[:300]
        versao, fim = _estado.get("versao"), None
    with _trava:
        em_memoria = sorted(_memoria)
    return {"corte": config.CORTE_DADOS.isoformat(), "limite": limite().isoformat(), "manifesto": manifesto,
            "versao": versao, "fim": fim, "persistida": persistida(), "congeladas_em_memoria": len(em_memoria),
            "pendentes": pendentes() if em_memoria else [], "erro_gravacao": _estado.get("erro"),
            "tentativas": _estado.get("tentativas", 0), "ultima_tentativa_em": _estado.get("ultima_tentativa_em"),
            "gravada_em": _estado.get("gravada_em")}


# ---------------------------------------------------------------- recuperação (B5)

def recuperar() -> list[str]:
    """B5: sem manifesto válido na raiz, publica a versão completa mais nova (manifesto interno conferido). Devolve o
    relato; BaseInvalida se não houver versão completa para publicar."""
    if not ligado():
        raise BaseInvalida("corte desligado: nada a recuperar")
    try:
        m = validar(usar_cache=False)
        return [f"a base publicada já é válida ({m['pasta']}, dados até {m['fim']}): nada a recuperar"]
    except BaseInvalida as e:
        relato = [f"base publicada inválida ou ausente: {e}"]
    with _trava, _trava_escrita():
        for d in sorted((x for x in pasta().glob("v-*") if x.is_dir()), key=lambda x: x.name, reverse=True):
            interno = d / MANIFESTO
            if not interno.is_file():
                relato.append(f"{d.name}: parcial (sem manifesto interno), ignorada")
                continue
            try:
                m = json.loads(interno.read_text(encoding="utf-8"))
            except (OSError, ValueError) as e:
                relato.append(f"{d.name}: manifesto interno ilegível ({type(e).__name__}), ignorada")
                continue
            problemas = (["aponta para outra pasta"] if m.get("pasta") != d.name else []) or _conferir(m, d, True)
            if problemas:
                relato.append(f"{d.name}: {'; '.join(problemas)[:200]}")
                continue
            _publicar(interno.read_text(encoding="utf-8"), d.name)
            validar(usar_cache=False)
            _estado.update(persistida=True, versao=d.name, erro=None)
            relato.append(f"{d.name}: completa e conferida, publicada (dados até {m['fim']})")
            return relato
    raise BaseInvalida(" | ".join(relato + ["nenhuma versão completa: refazer a base (tools/congelar_base.py)"]))


# ---------------------------------------------------------------- pacote da reunião (build e --conferir)

def conferir_previsao(base_processado_em) -> list[str]:
    """F03: a Previsão da reunião é o retrato do mês fechado pelo corte, e o retrato e o acompanhamento são da MESMA
    carga da base congelada (dia do processamento em São Paulo)."""
    from app.apresentacoes.gestao_orcamentos.previsao import calculos as previsao

    try:
        p = json.loads(Path(config.PREVISAO_ARQ).read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        return [f"Previsão: {config.PREVISAO_ARQ} ilegível ({type(e).__name__})"]
    problemas = []
    mes = corte.mes_fechado(config.CORTE_DADOS)
    if (p.get("retrato") or {}).get("mes_fechado") != mes:
        problemas.append(f"Previsão: retrato de {(p.get('retrato') or {}).get('mes_fechado')}, esperado {mes} "
                         "(rodar python -m ml.rodar --rotina depois da carga do corte)")
    c = previsao.coerencia(p, base_processado_em)
    if c and not c["retrato"]:
        problemas.append("Previsão: retrato sem a data da carga (carga.processado_em)")
    if c and p.get("acompanhamento") and not c["acompanhamento"]:
        problemas.append("Previsão: acompanhamento sem a data da carga (acompanhamento.processado_em)")
    for peca, dia in (c or {}).get("divergentes", {}).items():
        problemas.append(f"Previsão: {peca} da carga de {dia:%d/%m/%Y}, a base congelada é de {c['base']:%d/%m/%Y} "
                         "(rodar python -m ml.rodar --rotina antes da próxima carga da gold)")
    return problemas


def conferir_lia() -> list[str]:
    arq = Path(__file__).resolve().parent / "apresentacoes" / "gestao_orcamentos" / "lia" / "retrato.json"
    try:
        fim = json.loads(arq.read_text(encoding="utf-8")).get("fim")
    except (OSError, ValueError) as e:
        return [f"LIA: retrato ilegível ({type(e).__name__})"]
    if fim != config.CORTE_DADOS.isoformat():
        return [f"LIA: retrato até {fim}, esperado {config.CORTE_DADOS.isoformat()} "
                f"(python tools/extrair_lia.py --fim {config.CORTE_DADOS.isoformat()})"]
    return []


def conferir_pacote() -> tuple[dict | None, list[str]]:
    """F01: o que o build e o `--conferir` exigem, sem rede: base inteira e coerente (manifesto, hash, parquet legível,
    contrato de colunas de cada tabela), Previsão da mesma carga e LIA até o corte. (manifesto ou None, problemas)."""
    if not ligado():
        return None, []
    try:
        m = validar(usar_cache=False)
    except BaseInvalida as e:  # sem base, a carga não é comparável; Previsão (mês) e LIA são conferidas mesmo assim
        return None, [f"base congelada: {e}"] + conferir_previsao(None) + conferir_lia()
    problemas = [f"base congelada: {x}" for x in _conferir(m, pasta() / m["pasta"], ler_parquet=True)]
    for n, t in esperadas().items():
        try:
            t._validar(pd.read_parquet(pasta() / m["pasta"] / m["tabelas"][n]["arquivo"]))
        except Exception as e:  # noqa: BLE001
            problemas.append(f"base congelada: {n} fora do contrato ({type(e).__name__}: {e})"[:300])
    return m, problemas + conferir_previsao(m.get("processado_em")) + conferir_lia()
