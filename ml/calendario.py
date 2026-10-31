"""Variáveis de calendário conhecidas de antemão (servem de exógenas para ARIMAX/ML sem "colar" do futuro).

Usa o mesmo calendário de dias sem expediente do site/gold (app/expediente.py, R14).
"""

from datetime import date, timedelta

import pandas as pd

from app.expediente import sem_expediente


def dias_uteis(mes: pd.Period) -> int:
    """Dias úteis (seg–sex, fora feriados/recesso da R14) do mês."""
    inicio = date(mes.year, mes.month, 1)
    fim = (mes + 1).start_time.date()
    folgas = sem_expediente(mes.year)
    n, d = 0, inicio
    while d < fim:
        if d.weekday() < 5 and d not in folgas:
            n += 1
        d += timedelta(days=1)
    return n


def exogenas(meses: pd.PeriodIndex) -> pd.DataFrame:
    """Tabela de exógenas por mês: dias_uteis, fim_de_ano (nov/dez), ano_2026 (mudança de patamar)."""
    return pd.DataFrame({
        "dias_uteis": [dias_uteis(m) for m in meses],
        "fim_de_ano": [int(m.month in (11, 12)) for m in meses],
        "ano_2026": [int(m.year >= 2026) for m in meses],
    }, index=meses)
