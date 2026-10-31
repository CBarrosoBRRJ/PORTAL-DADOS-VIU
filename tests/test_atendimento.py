"""Aba Atendimento (A1–A8), composição contra o ano anterior (E9) e o teste de duas proporções (app/estatistica.py).

Valores esperados calculados à mão a partir de tests/conftest.py (entrada_diaria); a tabela vai até 20/10/2026.
"""

import pytest

from app import estatistica
from app.apresentacoes.gestao_orcamentos.atendimento import calculos as at
from app.apresentacoes.gestao_orcamentos.entrada import calculos as ent


@pytest.fixture(autouse=True)
def limpa_cache():
    ent._cache.clear()
    yield
    ent._cache.clear()


def test_diferenca_de_proporcoes():
    # 68% x 58% com 100 em cada lado: z = 0,10 / √(0,63 · 0,37 · 0,02) ≈ 1,46 → dentro da oscilação
    d = estatistica.diferenca(68, 100, 58, 100)
    assert d["pontos"] == pytest.approx(10) and d["z"] == pytest.approx(1.4646, abs=1e-3) and not d["relevante"]
    assert estatistica.pontos_tela(0.792, 0.757) == 3  # 79% − 76% como escritos (o exato seria 3,5)
    # a mesma diferença com 1.000 em cada lado: z ≈ 4,63 → relevante
    assert estatistica.diferenca(680, 1000, 580, 1000)["relevante"]
    assert estatistica.diferenca(1, 0, 1, 10) is None and estatistica.diferenca(1, 10, 0, 0) is None


def test_atendimento_quantidades_e_taxas(entrada_diaria, base_um):
    a = at.atendimento(entrada_diaria)
    assert a["ano"] == 2026 and a["periodo"] == "até 20 de outubro"
    # A1–A3 no ano (até 20/10): entregas 19 = 16 do próprio mês + 3 de antes; 22 entradas
    assert a["total"]["entregas"] == 19 and a["total"]["proprio"] == 16 and a["total"]["anteriores"] == 3
    assert a["total"]["entradas"] == 22
    # A6: mesmo período de 2025 (até 20/10/2025) = 4 + 4 + 3 = 11
    assert a["contra_anterior"]["entregas"] == 11 and a["contra_anterior"]["variacao"] == pytest.approx(19 / 11 - 1)
    # A6: taxas só com meses completos (jan–set/26): 18 entregas, 16 do próprio mês, 19 entradas
    assert a["taxas"]["cobertura"] == pytest.approx(18 / 19) and a["taxas"]["no_mes"] == pytest.approx(16 / 19)
    assert a["meses_completos"] == "jan a set"
    tc = a["taxas_contra_anterior"]  # jan–set/25: 8 entregas, 9 do próprio mês, 9 entradas
    assert tc["cobertura"] == pytest.approx(8 / 9) and tc["cobertura_pontos"] == 95 - 89  # 94,7% → 95; 88,9% → 89
    assert tc["no_mes"]["anterior"] == pytest.approx(1.0) and not tc["no_mes"]["relevante"]  # amostra pequena


def test_atendimento_por_mes(entrada_diaria, base_um):
    a = at.atendimento(entrada_diaria)
    jan, fev, out = a["meses"][0], a["meses"][1], a["meses"][9]
    assert (jan["entregas"], jan["proprio"], jan["anteriores"], jan["entradas"]) == (14, 13, 1, 16)
    assert jan["cobertura"] == pytest.approx(14 / 16) and jan["no_mes"] == pytest.approx(13 / 16)
    assert jan["anterior"]["entregas"] == 4 and jan["anterior"]["variacao"] == pytest.approx(14 / 4 - 1)  # A7
    assert (fev["entregas"], fev["proprio"], fev["anteriores"]) == (4, 3, 1)
    assert fev["anterior"]["variacao"] is None and fev["anterior"]["no_mes"] is None  # fev/25 sem base
    # A7: mês parcial compara quantidade até o mesmo dia (out/25 até 20/10 = 3) e não compara taxas
    assert out["parcial"] and out["anterior"]["entregas"] == 3 and out["anterior"]["no_mes"] is None
    assert out["anterior"]["cobertura"] is None
    assert a["meses"][10]["futuro"] and a["meses"][10]["anterior"] is None
    assert a["escala"] == 16  # maior valor entre entregas e entradas de um mês


def test_composicao_contra_ano_anterior(entrada_diaria):
    e = ent.entrada(entrada_diaria)
    merc = next(g for g in e["grupos"] if g["nome"] == "Mercado")["contra_anterior"]  # E9
    # 2026: 10 de 22; mesmo período de 2025: 5 + 4 = 9 de 13
    assert merc["atual"] == pytest.approx(10 / 22) and merc["anterior"] == pytest.approx(9 / 13)
    assert merc["pontos"] == pytest.approx((10 / 22 - 9 / 13) * 100)
    m = next(g for g in e["grupos"] if g["nome"] == "Mercado")
    assert m["n_anterior"] == 9 and m["variacao"] is None  # E9: base 9 < 30 → sem variação em %
    assert ent.BASE_MINIMA_VARIACAO == 30
    assert sum(g["n_anterior"] for g in e["grupos"]) == e["comparacao"]["total"] == 13  # total confere com E8
    assert all(g["contra_anterior"] is None for g in ent.entrada(entrada_diaria, 2025)["grupos"])  # 2025 sem régua



def test_variacao_exige_base_minima(entrada_diaria):
    """E8/E9/A7: abaixo de 30 no ano anterior não há variação em %; o número de referência continua."""
    ent._cache.clear()
    assert ent.BASE_MINIMA_VARIACAO == 30
    assert ent.variar(40, 29) is None and ent.variar(60, 30) == pytest.approx(1.0)
    e = ent.entrada(entrada_diaria)
    assert e["comparacao"] == {"total": 13, "variacao": None}  # total da tabela segue a mesma regra dos tipos
    assert at.atendimento(entrada_diaria)["contra_anterior"]["variacao"] is None
