"""Calendário de dias sem expediente da gold (R14) e o expediente sem almoço — para as leituras do site que contam dias
úteis (ritmo do Atendimento, previsão de demanda) e para a conferência independente do estudo (tools/conferir_estudo.py).

As horas úteis dos orçamentos não são mais calculadas aqui (D57, 27/10/2026): vêm prontas da gold (`sla_sem_almoco_horas`,
R24, e a view gld_agenciamento_2026_sla_entregas). A cópia da conta, para os testes, está em tests/gold_simulada.py.
"""

from datetime import date, timedelta
from functools import lru_cache

SEM_ALMOCO = ((10, 13), (14, 19))  # decisão do Caio, 21/10/2026

FIXOS = [(1, 1), (1, 20), (1, 25), (4, 21), (4, 23), (5, 1), (7, 9), (9, 7), (10, 12), (11, 2), (11, 15), (11, 20),
         (12, 24), (12, 25), (12, 31)]


def _pascoa(ano: int) -> date:
    """Domingo de Páscoa (algoritmo de Meeus), como na gold."""
    a, b, c = ano % 19, ano // 100, ano % 100
    d, e = b // 4, b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = c // 4, c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7  # noqa: E741
    m = (a + 11 * h + 22 * l) // 451
    mes = (h + l - 7 * m + 114) // 31
    dia = (h + l - 7 * m + 114) % 31 + 1
    return date(ano, mes, dia)


@lru_cache(maxsize=None)
def sem_expediente(ano: int) -> frozenset[date]:
    p = _pascoa(ano)
    moveis = [p - timedelta(days=48), p - timedelta(days=47), p - timedelta(days=46),  # Carnaval e Cinzas
              p - timedelta(days=2), p + timedelta(days=60)]  # Sexta-feira Santa e Corpus Christi
    return frozenset([date(ano, m, d) for m, d in FIXOS] + moveis)
