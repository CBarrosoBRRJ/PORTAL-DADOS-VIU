"""Job da previsão no computador (D48, 26/10/2026; revisa a D47): execução MENSAL.

J1 Gatilho (acao): a cada carga nova da gold de entradas (dados.entrada.ao_carregar) ou com a página aberta, compara o
   último mês fechado da carga (o mês anterior ao do dia seguinte a MAX(data), mesma regra do snapshot) com o mês do
   retrato gravado (previsao.json → retrato.mes_fechado):
     - mês fechado novo (ou sem retrato válido) → "rotina": `python -m ml.rodar --rotina` refaz o snapshot, TODOS os
       modelos, os filtros e grava o retrato e o histórico (PD09). Uma vez por mês.
     - mesmo mês, carga diferente da do acompanhamento → "acompanhamento": `python -m ml.rodar --acompanhamento`
       atualiza só o realizado do mês em andamento (segundos; a previsão não é recalculada).
     - senão, nada.
J2 Só dispara se: PREVISAO_JOB ligado (desligado em produção, onde o job é separado: docs/paginas/previsao.md), a pasta
   ml/ existe e o Python do job tem as bibliotecas (statsmodels). O site nunca importa as bibliotecas de ML nem espera.
J3 Um job por vez: a trava ml/saida/rotina.lock (gravada pela rotina) com menos de 3 h impede outro; o processo filho
   também fica guardado aqui; entre dois disparos, no mínimo ESPERA_MIN (um job que falhou não é refeito a cada
   página aberta).
J4 Saída do job em ml/saida/rotina.log (anexada a cada rodada); o resultado da última tentativa (início, fim, código,
   erro) em ml/saida/rotina_estado.json, gravado de forma atômica por ml/rodar.py e lido pela página (falha visível).
J5 (batalha 2, G4-N10) Com CONGELAR ou no modo apresentação, o site NÃO dispara o job: a reunião mostra uma só carga.
   Na véspera, rodar à mão `python -m ml.rodar --acompanhamento` logo depois de subir o servidor congelado.
J6 (batalha 2, G1-N11) O fim da carga é a regra E3 do portal (app/corte.py: véspera do _processado_em), não MAX(data).
"""

import importlib.util
import logging
import subprocess
import sys
import threading
import time
import pandas as pd

from app import config, corte

log = logging.getLogger(__name__)
TRAVA_HORAS = 3
ESPERA_MIN = 30  # J3
COMANDO = {"rotina": "--rotina", "acompanhamento": "--acompanhamento"}
_ultimo_disparo = 0.0
_processo: subprocess.Popen | None = None
_trava = threading.Lock()


def _pasta_ml():
    return config.RAIZ / "ml"


def disponivel() -> bool:
    """J2: o job pode rodar nesta máquina?"""
    if not config.PREVISAO_JOB or not (_pasta_ml() / "rodar.py").exists():
        return False
    if config.PREVISAO_PYTHON:  # outro Python: não dá para conferir as bibliotecas daqui; o job registra a falha
        return True
    return importlib.util.find_spec("statsmodels") is not None


def em_andamento() -> bool:
    if _processo is not None and _processo.poll() is None:
        return True
    trava = _pasta_ml() / "saida" / "rotina.lock"
    return trava.exists() and time.time() - trava.stat().st_mtime < TRAVA_HORAS * 3600


def mesma_carga(processado_em, carga_previsao: str | None) -> bool:
    if processado_em is None or not carga_previsao:
        return False
    try:
        return pd.Timestamp(processado_em) == pd.Timestamp(carga_previsao)
    except (ValueError, TypeError):
        return False


def mes_fechado(dados_ate) -> str | None:
    """Último mês completo de uma carga que cobre até `dados_ate` (E3, app/corte.py; mesma regra do snapshot)."""
    return corte.mes_fechado(dados_ate)


def acao(p: dict | None, processado_em, dados_ate) -> str | None:
    """J1: "rotina" (mês fechado novo), "acompanhamento" (só o realizado do mês) ou None."""
    if processado_em is None:
        return None
    mf = mes_fechado(dados_ate)
    if p is None:
        return "rotina"
    if mf and mf > p["retrato"]["mes_fechado"]:
        return "rotina"
    carga_ac = (p.get("acompanhamento") or {}).get("processado_em") or p["carga"]["processado_em"]
    return None if mesma_carga(processado_em, carga_ac) else "acompanhamento"


def disparar(qual: str | None) -> bool:
    """J1–J3. Devolve True se um job foi iniciado agora."""
    global _processo, _ultimo_disparo
    if config.CONGELAR or config.MODO_APRESENTACAO:  # J5: na reunião, uma só carga (o job roda à mão na véspera)
        return False
    if qual not in COMANDO or not disponivel():
        return False
    with _trava:
        if em_andamento() or time.monotonic() - _ultimo_disparo < ESPERA_MIN * 60 and _ultimo_disparo:
            return False
        _ultimo_disparo = time.monotonic()
        saida = _pasta_ml() / "saida"
        saida.mkdir(parents=True, exist_ok=True)
        python = config.PREVISAO_PYTHON or sys.executable
        flags = 0
        if sys.platform == "win32":  # sem janela e fora do grupo do servidor (o --reload não derruba o job)
            flags = subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP
        with open(saida / "rotina.log", "ab") as arq:
            _processo = subprocess.Popen([python, "-m", "ml.rodar", COMANDO[qual]], cwd=config.RAIZ, stdout=arq,
                                         stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, creationflags=flags)
        log.warning("previsão: job %s iniciado (pid %s)", qual, _processo.pid)
        return True


def da_carga(df: pd.DataFrame) -> tuple:
    """(_processado_em, fim da carga pela E3) de uma carga da gold de entradas (J6: não MAX(data))."""
    if df is None or "_processado_em" not in df or not df["_processado_em"].notna().any():
        return None, None
    processado_em = pd.to_datetime(df["_processado_em"], utc=True).max()
    return processado_em, pd.Timestamp(corte.fim(processado_em, pd.to_datetime(df["data"]).max()))


def ultima_tentativa() -> dict | None:
    """J4: a última execução registrada em ml/saida/rotina_estado.json ({modo, inicio, fim, codigo, erro}); None sem
    arquivo ou ilegível."""
    import json

    try:
        e = json.loads((_pasta_ml() / "saida" / "rotina_estado.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return e if isinstance(e, dict) else None


def falhou() -> dict | None:
    """A última tentativa terminou com erro (e nenhum job está rodando agora)? Devolve o registro dela."""
    e = ultima_tentativa()
    if not (e and e.get("fim") and e.get("codigo") not in (0, None)) or em_andamento():
        return None
    try:  # hora local (São Paulo) para o texto da página
        fim = pd.Timestamp(e["fim"])
        fim = (fim.tz_localize(config.FUSO) if fim.tzinfo is None else fim.tz_convert(config.FUSO)).to_pydatetime()
    except (ValueError, TypeError):
        fim = None
    return {**e, "fim": fim}


def ao_carregar_entrada(df: pd.DataFrame) -> None:
    """Gancho de dados.entrada: carga nova da gold → job (J1)."""
    from app.apresentacoes.gestao_orcamentos.previsao import calculos

    processado_em, dados_ate = da_carga(df)
    disparar(acao(calculos.ler(), processado_em, dados_ate))
