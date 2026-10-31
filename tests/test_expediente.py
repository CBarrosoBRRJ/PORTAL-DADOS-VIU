"""Calendário (app/expediente.py) e horas úteis da gold (R14, R24; simuladas em tests/gold_simulada.py), com e sem almoço."""

from datetime import date, datetime

from app.expediente import SEM_ALMOCO, _pascoa, sem_expediente
from gold_simulada import COM_ALMOCO, horas_uteis


def test_pascoa_meeus():
    assert _pascoa(2026) == date(2026, 4, 5)
    assert _pascoa(2027) == date(2027, 3, 28)
    assert _pascoa(2030) == date(2030, 4, 21)


def test_feriados_fixos_e_moveis_de_2026():
    dias = sem_expediente(2026)
    assert date(2026, 4, 21) in dias  # Tiradentes
    assert date(2026, 11, 20) in dias  # Consciência Negra
    assert date(2026, 2, 16) in dias and date(2026, 2, 17) in dias  # Carnaval
    assert date(2026, 2, 18) in dias  # Quarta-feira de Cinzas
    assert date(2026, 4, 3) in dias  # Sexta-feira Santa
    assert date(2026, 6, 4) in dias  # Corpus Christi
    assert date(2026, 3, 2) not in dias


def test_almoco_descontado_so_no_expediente_sem_almoco():
    inicio, fim = datetime(2026, 3, 2, 10), datetime(2026, 3, 2, 14)  # segunda 10h–14h
    assert horas_uteis(inicio, fim, COM_ALMOCO) == 4
    assert horas_uteis(inicio, fim, SEM_ALMOCO) == 3


def test_fim_de_semana_e_noite_nao_contam():
    assert horas_uteis(datetime(2026, 3, 6, 16), datetime(2026, 3, 9, 10), SEM_ALMOCO) == 3  # sex 16h → seg 10h
    assert horas_uteis(datetime(2026, 3, 2, 19), datetime(2026, 3, 3, 10), SEM_ALMOCO) == 0  # noite


def test_feriado_no_meio_nao_conta():
    # 20/04 (seg) 10h → 22/04 (qua) 10h: 21/04 é Tiradentes → só o dia 20 conta (8 h)
    assert horas_uteis(datetime(2026, 4, 20, 10), datetime(2026, 4, 22, 10), SEM_ALMOCO) == 8


def test_virada_de_ano_exclui_31_12_01_01_e_fim_de_semana():
    # qua 30/12 18h → seg 04/01/2027 11h: 30/12 das 18h às 19h (1 h) + 04/01 das 10h às 11h (1 h)
    assert horas_uteis(datetime(2026, 12, 30, 18), datetime(2027, 1, 4, 11), SEM_ALMOCO) == 2


def test_intervalo_invertido_ou_vazio_da_zero():
    assert horas_uteis(datetime(2026, 3, 2, 12), datetime(2026, 3, 2, 12), SEM_ALMOCO) == 0
    assert horas_uteis(datetime(2026, 3, 2, 12), datetime(2026, 3, 2, 11), SEM_ALMOCO) == 0


def test_limite_de_16h_preserva_microssegundos():
    from gold_simulada import microssegundos_uteis
    inicio = datetime(2026, 3, 2, 10)
    meio = datetime(2026, 3, 2, 11, 17, 31, 999999)
    fim = datetime(2026, 3, 4, 10)
    us = microssegundos_uteis(inicio, meio, SEM_ALMOCO) + microssegundos_uteis(meio, fim, SEM_ALMOCO)
    assert us / 3_600_000_000 == 16
    assert microssegundos_uteis(inicio, fim.replace(microsecond=1), SEM_ALMOCO) / 3_600_000_000 > 16


def test_dias_uteis_entre():
    """C3b: viradas de dia útil entre o pedido e a entrega; fora do expediente conta a partir do próximo dia útil."""
    from datetime import datetime as dt
    from gold_simulada import dias_uteis_entre as du

    assert du(dt(2026, 3, 2, 10), dt(2026, 3, 2, 14)) == 0       # segunda → segunda
    assert du(dt(2026, 3, 2, 10), dt(2026, 3, 4, 10)) == 2       # segunda → quarta
    assert du(dt(2026, 3, 6, 16), dt(2026, 3, 10, 12)) == 2      # sexta → terça (sexta e segunda)
    assert du(dt(2026, 3, 6, 20), dt(2026, 3, 9, 15)) == 0       # sexta 20h conta da segunda; entregue na segunda
    assert du(dt(2026, 4, 1, 10), dt(2026, 4, 6, 10)) == 2       # quarta → segunda, com a Sexta-feira Santa (03/04)
    assert du(dt(2026, 3, 2, 22), dt(2026, 3, 2, 23)) == 0       # nunca negativo
