"""Regras do slide 1 (C1–C11) sobre os dados sintéticos de conftest.py, e os invariantes de arredondamento."""

import random

import pandas as pd
import pytest

from app import formato, sla
from app.apresentacoes.gestao_orcamentos.sla import calculos
import gold_simulada  # views da gold sobre os dados sintéticos (D57)


def test_entregas_segue_c1_c2_c3_c4_c9(movimentos):
    e = calculos.entregas(movimentos).set_index("projeto_id")
    assert set(e.index) == {"P1", "P2", "P3", "P5", "P6"}  # P4 nunca foi ao cliente (C4)
    assert e.loc["P1", "h_trabalho"] == 3 and e.loc["P1", "h_fila"] == 1 and e.loc["P1", "h_calendario"] == 4
    assert e.loc["P2", "h_trabalho"] == 16 and e.loc["P2", "h_fila"] == 8 and e.loc["P2", "h_calendario"] == 48
    assert e.loc["P3", "h_trabalho"] == 13 and e.loc["P3", "h_fila"] == 3 and e.loc["P3", "h_calendario"] == 92
    assert e.loc["P5", "h_trabalho"] == 16  # a volta do cliente e a 2ª ida não entram (C1: 1ª chegada)
    assert e.loc["P5", "mes"] == "2026-04"
    assert e.loc["P5", "exclusivo"] is None or pd.isna(e.loc["P5", "exclusivo"])


def test_entrega_todos(movimentos):
    e = calculos.entrega(movimentos, sla.mes_parcial(movimentos))
    assert e["n_ano"] == 4  # P6 é de outubro, mês parcial (C7)
    assert e["mediana_h_trabalho"] == pytest.approx(14.5)  # mediana de 3, 13, 16, 16
    assert e["mediana_dias_calendario"] == pytest.approx(2.0)  # mediana de 4, 48, 48, 92 h → 48 h
    assert e["mediana_h_fila"] == pytest.approx(2.0)  # mediana de 0, 1, 3, 8
    assert e["ano"]["tela"] == {"ate1": 25, "de1a2": 75, "acima2": 0, "ate2": 100}  # D-SLA-7: 16 h conta como até 2 dias
    por_mes = {m["chave"]: m for m in e["meses"]}
    assert por_mes["2026-03"]["n"] == 3 and por_mes["2026-03"]["tela"]["ate2"] == 100 and por_mes["2026-03"]["tela"]["ate1"] == 33
    assert por_mes["2026-03"]["tela"]["de1a2"] == 67  # C8: 100 − 33, não 66,7 arredondado
    assert por_mes["2026-03"]["mediana"] == pytest.approx(13.0)  # A3: mediana de 3, 13, 16
    assert por_mes["2026-10"]["parcial"] and por_mes["2026-10"]["n"] == 1
    assert por_mes["2026-11"]["futuro"] and por_mes["2026-11"]["n"] == 0
    assert e["periodo"] == "jan a set"
    assert e["leitura"].startswith("Melhor mês: mar (100%).") and e["leitura"].endswith("igual ao ano.")


def test_grupos_de_talento_c10(movimentos):
    e = calculos.entrega(movimentos, sla.mes_parcial(movimentos), "exclusivos")
    assert e["grupo"] == "exclusivos" and e["n_ano"] == 2  # P1 e P3
    assert e["mediana_h_trabalho"] == pytest.approx(8.0)
    valores = {g["chave"]: g["mediana_h_trabalho"] for g in e["grupos"]}
    assert valores == {"todos": 14.5, "exclusivos": 8.0, "nao-exclusivos": 16.0}  # P5 (sem talento) só em "todos"


def test_faixas_sempre_somam_o_total_c8():
    rng = random.Random(7)
    for _ in range(200):
        h = pd.Series([rng.uniform(0, 40) for _ in range(rng.randint(1, 60))])
        tela = calculos._faixas(h)["tela"]
        assert tela["ate1"] + tela["de1a2"] == tela["ate2"]
        assert tela["ate2"] + tela["acima2"] == 100
        assert 0 <= tela["ate1"] <= tela["ate2"] <= 100 and set(tela) == {"ate1", "de1a2", "acima2", "ate2"}


def test_faixas_na_fronteira_e_sem_faixa_do_meio():
    # 16 h conta como "até 2 dias"; 16,0001 h não (limites inclusivos, C5 / D-SLA-7)
    tela = calculos._faixas(pd.Series([8, 16, 16.0001, 24]))["tela"]
    assert tela == {"ate1": 25, "de1a2": 25, "acima2": 50, "ate2": 50}
    tela = calculos._faixas(pd.Series([1, 2, 20]))["tela"]
    assert tela == {"ate1": 67, "de1a2": 0, "acima2": 33, "ate2": 67}  # sem faixa do meio inventada


def test_cliente_no_passo_1_e_descartado(movimentos):
    extra = movimentos.iloc[:1].copy()
    extra["projeto_id"], extra["status"], extra["fase"] = "PX", "Aguardando Feedback", "cliente"
    base = pd.concat([movimentos, extra], ignore_index=True)
    e = calculos.entregas(base)
    # C4 é regra da gold (view de entregas); a simulação dela conta o descarte
    assert "PX" not in set(e["projeto_id"]) and gold_simulada.sla_views(base)[0].attrs["invalidos"] == 1


def test_arredondamento_meio_para_cima():
    assert calculos._pontos(0.675) == 68 and calculos._pontos(0.665) == 67 and calculos._pontos(0.5) == 50
    assert formato.inteiro(8.5) == "9" and formato.inteiro(14.5) == "15" and formato.inteiro(2.4) == "2"
    assert formato.inteiro(1234) == "1.234" and formato.inteiro(None) == "—"
    assert formato.decimal(2.8733, 1) == "2,9" and formato.pct(0.5261) == "53%"
