"""D40 (25/10/2026, Caio): slide 4 do estudo "Como medimos" — "Para onde vai o tempo?". Cartões "Saem em até 2 dias"
e "Passam de 2 dias" com a parte dos pedidos (os mesmos % do slide 3) e a parte das horas da equipe (maior resto, soma
100), frases em frações por extenso, faixa do pé com variantes e o seletor de talentos levando a #4 (regras V1–V8)."""

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from app.apresentacoes.gestao_orcamentos.sla import calculos as c
from tests.test_exploracao import _mov as base
from tests.test_sla_d38 import _mov


def _serie(mix):
    return pd.Series([float(h) for h, q in mix for _ in range(q)])


MIX = [(4, 30), (12, 25), (20, 15), (30, 18), (60, 12)]


def test_pedidos_iguais_ao_slide_3_e_horas_somam_100():
    h = _serie(MIX)
    t, w = c._tempo(h, "2026-10"), c._cem(h, "2026-10")
    assert [l["pedidos"] for l in t["linhas"]] == [f["pct"] for f in w["faixas"]]
    assert (t["a"], t["b"]) == (w["a"], w["b"]) == (55, 45)
    # horas: 120 / 300 / 300 / 540 / 720 de 1.980 h → 6,06 / 15,15 / 15,15 / 27,27 / 36,36 → maior resto
    assert [l["horas"] for l in t["linhas"]] == [6, 15, 15, 27, 37]
    assert sum(l["horas"] for l in t["linhas"]) == 100
    assert (t["ha"], t["hb"]) == (21, 79)
    a, b = t["cartoes"]
    assert a["pedidos"] == sum(l["pedidos"] for l in a["linhas"]) and a["horas"] == sum(l["horas"] for l in a["linhas"])
    assert b["pedidos"] == sum(l["pedidos"] for l in b["linhas"]) and b["horas"] == sum(l["horas"] for l in b["linhas"])
    assert [l["rotulo"] for l in a["linhas"]] == ["até 1 dia", "de 1 a 2 dias"]
    assert [l["rotulo"] for l in b["linhas"]] == ["de 2 a 3 dias", "de 3 a 5 dias", "mais de 5 dias"]


def test_pedidos_seguem_o_ajuste_do_slide_3():
    """V2: no caso em que o maior resto puro daria A = 57, vale o A da página (56), como no slide 3."""
    h = _serie([(4, 305), (12, 255), (20, 150), (30, 145), (50, 145)])
    t = c._tempo(h, "2026-10")
    assert [l["pedidos"] for l in t["linhas"]] == [31, 25, 15, 15, 14] and t["a"] == 56 == c._faixas(h)["tela"]["ate2"]


def test_A_igual_ao_da_pagina_e_aos_slides_2_e_3():
    mov = base()
    t = c.tempo_cem(mov, "2026-10", "todos")
    assert t["a"] == c.cem_pedidos(mov, "2026-10", "todos")["a"] == c.entrega(mov, "2026-10", "todos")["ano"]["tela"]["ate2"]
    assert t["n"] == 72 and sum(l["horas"] for l in t["linhas"]) == 100


@pytest.mark.parametrize("p, texto", [
    (0, "menos de 1%"), (100, "100%"), (50, "metade"),
    (59, "mais da metade"), (41, "menos da metade"), (22, "menos de um quarto"), (78, "quase quatro quintos"),
    (56, "mais da metade"), (16, "menos de um quinto"), (44, "menos da metade"), (84, "mais de quatro quintos"),
    (62, "mais da metade"), (19, "cerca de um quinto"), (38, "menos da metade"), (81, "cerca de quatro quintos"),
    (12, "pouco mais de um décimo"), (88, "quase nove décimos"), (33, "cerca de um terço"), (66, "cerca de dois terços"),
    (30, "menos de um terço"), (70, "mais de dois terços"), (5, "menos de um décimo"), (95, "mais de nove décimos"),
])
def test_fracao_por_extenso(p, texto):
    assert c._fracao(p) == texto


def test_frase_do_cartao():
    assert c._parte(59, 22) == "Mais da metade dos pedidos, menos de um quarto do tempo."
    assert c._parte(41, 78) == "Menos da metade dos pedidos, quase quatro quintos do tempo."
    assert c._parte(50, 50) == "Metade dos pedidos, metade do tempo."
    assert c._parte(0, 0) == "Nenhum pedido neste grupo."


@pytest.mark.parametrize("a, b, hb, abre, trecho, gancho", [
    (56, 44, 84, "Na maior parte das vezes entregamos em até 2 dias. Mas os ",
     "<strong>44% que passam disso</strong> concentram <strong>84% do tempo</strong>",
     "Mas esses 44% foram um mês ruim, ou é sempre assim?"),
    (41, 59, 88, "Neste grupo, menos da metade sai em até 2 dias. E os ",
     "<strong>59% que passam disso</strong> concentram <strong>88% do tempo</strong>",
     "Mas esses 59% foram um mês ruim, ou é sempre assim?"),
    (50, 50, 80, "Metade dos pedidos sai em até 2 dias. Mas os ", "<strong>50% que passam disso</strong>",
     "Mas esses 50% foram um mês ruim, ou é sempre assim?"),
    (99, 1, 7, "Na maior parte das vezes entregamos em até 2 dias. Mas o ",
     "<strong>1% que passa disso</strong> concentra <strong>7% do tempo</strong>",
     "Mas esse 1% foi um mês ruim, ou é sempre assim?"),
])
def test_faixa_do_pe_variantes(a, b, hb, abre, trecho, gancho):
    t = c._tempo_textos(a, b, hb)
    assert t["rodape"].startswith(abre) and trecho in t["rodape"]
    assert "<em>É aí que está o ganho:</em>" in t["rodape"]
    assert t["gancho"] == gancho
    assert t["prazo"] == ("O maior ganho de tempo de entrega está nesse pedido." if b == 1
                          else f"O maior ganho de tempo de entrega está nesses {b} pedidos.")
    assert t["fluxo"].startswith("Com menos pedidos parados")


def test_faixa_do_pe_sem_B():
    t = c._tempo_textos(100, 0, 0)
    assert t["rodape"].startswith("Neste grupo, <strong>todos saem em até 2 dias</strong>")
    assert t["prazo"] is None and t["gancho"] == "E isso se repete todo mês?"
    x = c._tempo(_serie([(4, 40)]), "2026-10")
    assert (x["a"], x["b"], x["ha"], x["hb"]) == (100, 0, 100, 0)
    assert x["cartoes"][1]["frase"] == "Nenhum pedido neste grupo."


def test_poucos_dados_ou_sem_horas():
    assert c._tempo(_serie([(4, 29)]), "2026-10") is None
    assert c._tempo(_serie([(0, 40)]), "2026-10") is None
    assert c._tempo(_serie([(4, 30)]), "2026-10") is not None


def test_v9_tipico_de_cada_lado_e_v10_resposta():
    """V9: típico (mediana exata, C6) dos que saem em até 2 dias e dos que passam; V10: a resposta liga as duas metades."""
    h = _serie([(4, 10), (8, 10), (20, 10), (40, 5)])  # 20 em até 2 dias (4 e 8 h), 15 acima (20 e 40 h)
    t = c._tempo(h, "2026-10")
    assert t["tipico_a"] == 6.0 and t["tipico_b"] == 20.0
    assert t["tipico_a_txt"] == "6 h" and t["tipico_b_txt"] == "20 h"
    assert t["resposta"] == (f"Mais da metade dos pedidos (<strong>{t['a']}%</strong>) sai em até 2 dias e leva "
                             f"<strong>{t['ha']}% das horas</strong> da equipe; os outros <strong>{t['b']}% passam disso"
                             f"</strong> e levam <strong>{t['hb']}%</strong>.")
    assert t["a"] == 57 and t["ha"] + t["hb"] == 100
    assert c._resposta_cem_tempo(50, 50, 10, 90).startswith("Metade dos pedidos")
    assert c._resposta_cem_tempo(40, 60, 10, 90).startswith("Menos da metade dos pedidos")
    assert "o outro <strong>1% passa disso</strong> e leva <strong>9%</strong>" in c._resposta_cem_tempo(99, 1, 91, 9)
    assert "todos saem em até 2 dias" in c._resposta_cem_tempo(100, 0, 100, 0)
    assert "nenhum sai em até 2 dias" in c._resposta_cem_tempo(0, 100, 0, 100)
    s = c._tempo(_serie([(4, 40)]), "2026-10")  # ninguém passa de 2 dias: sem típico do lado B
    assert s["tipico_b"] is None and s["tipico_b_txt"] is None
