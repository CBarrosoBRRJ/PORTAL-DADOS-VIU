"""Data de corte única do portal (regra E3), usada pelo site, pelo job da previsão e pelo ML (batalha 2, G4-N10/G1-N11).

E3  A carga da gold cobre até a VÉSPERA do dia (São Paulo) em que foi processada: fim = DATE(MAX(_processado_em),
    'America/Sao_Paulo') − 1 dia, inclusive em dias sem pedido (fim de semana, feriado). Sem o metadado, o último dia
    com dado (MAX(data)). Não usar MAX(data) quando houver `_processado_em`: a gold só tem linha em dia com pedido
    (523 dias com dado em 751), e um mês que termina num sábado (31/10/2026) só "fecharia" quando aparecesse novembro.
Mês fechado = o mês anterior ao do dia seguinte ao fim (fim 31/10 → 2026-10; fim 30/10 → 2026-09).

Módulo neutro (só pandas e config): importado por app/dados.py e previsao/job.py sem import circular. A mesma regra em
SQL está nas views da gold (`dados_ate` da gld_agenciamento_previsao_mensal).
"""

from datetime import date, timedelta

import pandas as pd

from app import config


def dia_da_carga(processado_em) -> date | None:
    """Dia (São Paulo) do processamento; aceita Timestamp, texto ISO ou uma Series de `_processado_em`."""
    if processado_em is None:
        return None
    if isinstance(processado_em, pd.Series):
        s = pd.to_datetime(processado_em, utc=True, errors="coerce").dropna()
        if s.empty:
            return None
        processado_em = s.max()
    t = pd.Timestamp(processado_em)
    if pd.isna(t):
        return None
    if t.tzinfo is None:
        t = t.tz_localize("UTC")
    return t.tz_convert(config.FUSO).date()


def fim(processado_em, ultimo_dado=None) -> date | None:
    """E3: último dia coberto pela carga."""
    dia = dia_da_carga(processado_em)
    if dia is not None:
        return dia - timedelta(days=1)
    if ultimo_dado is None or pd.isna(ultimo_dado):
        return None
    return pd.Timestamp(ultimo_dado).date()


def mes_fechado(fim_da_carga) -> str | None:
    """Último mês completo ("AAAA-MM") de uma carga que cobre até `fim_da_carga`."""
    if fim_da_carga is None or pd.isna(fim_da_carga):
        return None
    dia = pd.Timestamp(fim_da_carga).normalize() + timedelta(days=1)
    return str(dia.to_period("M") - 1)


def mes_fechado_ligado() -> bool:
    """D68: recorte de exibição do mês fechado ligado (config.RECORTE_EXIBICAO = "mes_fechado")."""
    return config.RECORTE_EXIBICAO == "mes_fechado"


def data_exibicao(fim_da_carga) -> date | None:
    """D68 (Caio, 03/11/2026): último dia que as telas de dados mostram. Com o recorte do mês fechado, o último dia do mês
    anterior ao do dia seguinte ao fim da carga (fim 02/11 → 31/10; fim 31/10 → 31/10; fim 31/12 → 31/12); com "off", o
    próprio fim da carga (E3). A situação de cada pedido continua a da carga: o recorte só escolhe os dias que entram."""
    if fim_da_carga is None or pd.isna(fim_da_carga):
        return None
    dia = pd.Timestamp(fim_da_carga).date()
    if not mes_fechado_ligado():
        return dia
    return (dia + timedelta(days=1)).replace(day=1) - timedelta(days=1)
