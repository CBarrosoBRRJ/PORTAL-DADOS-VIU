"""D39 (25/10/2026, Caio): slide 3 do estudo "Como medimos" — "De cada 100 pedidos que chegam, em quanto tempo
entregamos?". Waffle de 100 (soma 100, coerente com o "% em até 2 dias" da página e do slide 2), curva acumulada com os
marcos de 2 dias, 80% e 90%, textos com variantes e o seletor de talentos levando a #3 (regras W1–W7)."""

import re
import pandas as pd
import pytest
from fastapi.testclient import TestClient

from app.apresentacoes.gestao_orcamentos.sla import calculos as c
from tests.test_exploracao import _mov as base
from tests.test_sla_d38 import _mov


def _serie(mix):
    return pd.Series([float(h) for h, q in mix for _ in range(q)])


def test_soma_100_e_quadrados_na_ordem():
    x = c._cem(_serie([(4, 30), (12, 25), (20, 15), (30, 18), (60, 12)]), "2026-10")
    pcts = [f["pct"] for f in x["faixas"]]
    assert pcts == [30, 25, 15, 18, 12] and sum(pcts) == 100
    assert x["a"] == 55 and x["b"] == 45 and not x["ajustado"]
    assert len(x["quadrados"]) == 100
    assert x["quadrados"][:30] == ["c1"] * 30 and x["quadrados"][30:55] == ["c2"] * 25 and x["quadrados"][-12:] == ["c5"] * 12
    assert [f["rotulo"] for f in x["faixas"]] == ["em até 1 dia", "de 1 a 2 dias", "de 2 a 3 dias", "de 3 a 5 dias", "mais de 5 dias"]
    assert "30 em até 1 dia" in x["waffle_txt"] and "Em até 2 dias: 55; mais de 2 dias: 45." in x["waffle_txt"]


def test_limites_das_faixas_inclusivos():
    # 0 h e 8 h na 1ª faixa; 16 h na 2ª; 40 h na 4ª (só > 40 h é "mais de 5 dias")
    x = c._cem(_serie([(0, 10), (8, 10), (16, 10), (24, 10), (40, 10)]), "2026-10")
    assert x["contagens"] == [20, 10, 10, 10, 0]


def test_maior_resto_puro_daria_outro_A_e_vale_o_da_pagina():
    """W3: 1.000 orçamentos com 30,5% até 1 dia e 56,0% até 2 dias. O maior resto puro das cinco faixas dá 31 + 26 = 57;
    a página (C8) e o slide 2 dizem 56. Vale 56: as três de cima repartem 44 pelo maior resto."""
    h = _serie([(4, 305), (12, 255), (20, 150), (30, 145), (50, 145)])
    x = c._cem(h, "2026-10")
    assert x["maior_resto"] == [31, 26, 15, 14, 14]
    assert x["ajustado"]
    assert [f["pct"] for f in x["faixas"]] == [31, 25, 15, 15, 14]
    assert x["a"] == 56 == c._faixas(h)["tela"]["ate2"] and x["b"] == 44
    assert sum(f["pct"] for f in x["faixas"]) == 100


def test_A_igual_ao_da_pagina_e_ao_slide_2():
    mov = base()
    x = c.cem_pedidos(mov, "2026-10", "todos")
    e = c.entrega(mov, "2026-10", "todos")
    assert x["a"] == e["ano"]["tela"]["ate2"] == c.exploracao(mov, "2026-10", "todos")["faixas3"]["pcts"][0]
    assert x["n"] == 72


def test_dias_meio():
    assert c._dias_meio(28) == "3 dias e meio"
    assert c._dias_meio(41) == "5 dias"
    assert c._dias_meio(30.79) == "4 dias"
    assert c._dias_meio(12) == "1 dia e meio"
    assert c._dias_meio(8) == "1 dia"
    assert c._dias_meio(4) == "meio dia"
    assert c._dias_meio(1) == "menos de meio dia"


def test_marcos_da_curva():
    h = _serie([(4, 30), (12, 25), (20, 15), (30, 18), (60, 12)])
    x = c._cem(h, "2026-10")
    cv = x["curva"]
    m2, m80, m90 = cv["marcos"]
    assert (m2["pct"], m2["dias"], m2["horas"]) == (55, "2 dias", "16 h")
    assert m80["h"] == pytest.approx(float(h.quantile(0.8))) and m80["pct"] == 80
    assert m90["h"] == pytest.approx(float(h.quantile(0.9))) and m90["pct"] == 90
    assert (m80["dias"], m80["horas"]) == ("4 dias", "30 h")  # P80 = 30 h (3,75 dias → 4 dias)
    assert (m90["dias"], m90["horas"]) == ("7 dias e meio", "60 h")  # P90 = 60 h
    # teto do eixo = P97 arredondado para cima ao múltiplo de 8 h; a curva vai de 0 a 100% (y para baixo)
    assert cv["teto"] == 64 and cv["fim_txt"] == "100% até 64 h"
    xs = [float(p.split(",")[0]) for p in cv["linha"].split()]
    assert len(xs) == 121 and xs[0] == cv["e"] and xs[-1] == cv["dir"]
    # rótulos do eixo x não se encostam; os % do eixo y ficam a 15 ou mais um do outro
    rot = sorted(cv["marcos"], key=lambda m: m["tx"])
    for a, b in zip(rot, rot[1:]):
        assert b["tx"] - b["w"] / 2 >= a["tx"] + a["w"] / 2 + 5.9
    ys = sorted(m["ty"] for m in cv["marcos"])
    assert all(b - a >= 14.9 for a, b in zip(ys, ys[1:]))
    assert "55% ficam prontos em até 2 dias de trabalho (16 h); 80% em até 4 dias (30 h); 90% em até 7 dias e meio (60 h)" in cv["texto"]


def test_afasta_centra_o_bloco_e_respeita_as_bordas():
    r = [{"x": 100.0, "w": 40.0}, {"x": 110.0, "w": 40.0}]
    c._afasta(r, "x", "w", 0, 300)
    assert r[0]["x"] == 82.0 and r[1]["x"] == 128.0  # bloco de 86 centrado em 105
    r = [{"x": 295.0, "w": 40.0}]
    c._afasta(r, "x", "w", 0, 300)
    assert r[0]["x"] == 280.0


@pytest.mark.parametrize("a, b, trechos, gancho", [
    (56, 44, ["<strong>56 ficam prontos em até 2 dias</strong> de trabalho e <strong>44 levam mais de 2 dias</strong>."],
     "E quanto do tempo esses 44 pedidos consomem?"),
    (1, 99, ["<strong>1 fica pronto em até 2 dias</strong>", "<strong>99 levam mais de 2 dias</strong>"],
     "E quanto do tempo esses 99 pedidos consomem?"),
    (99, 1, ["<strong>99 ficam prontos em até 2 dias</strong>", "<strong>1 leva mais de 2 dias</strong>"],
     "E quanto do tempo esse pedido consome?"),
    (0, 100, ["<strong>nenhum fica pronto em até 2 dias</strong>"], "E quanto do tempo esses 100 pedidos consomem?"),
    (100, 0, ["<strong>nenhum leva mais de 2 dias</strong>"], "E quanto do tempo cada faixa consome?"),
])
def test_textos_variantes(a, b, trechos, gancho):
    t = c._cem_textos(a, b)
    assert t["rodape"].startswith("Em uma amostra aleatória de 100 pedidos, ")
    assert all(x in t["rodape"] for x in trechos)
    assert t["rodape"].endswith("mais de 2 dias</strong>.") and "90%" not in t["rodape"]  # redação do Caio, sem o prazo dos 90%
    assert t["gancho"] == gancho


def test_poucos_dados_sem_slide():
    assert c._cem(_serie([(4, 29)]), "2026-10") is None
    assert c._cem(_serie([(4, 30)]), "2026-10") is not None


def test_slide_3_unificado_no_html(monkeypatch):
    """V2 (30/10/2026): os antigos slides 3 e 4 viram o slide 3, em "T": waffle de 100 em dois tons (A e B, os mesmos %
    de W3/V2) à esquerda; parte das horas (V3) e típico de cada lado (V9) à direita; resposta V10 no pé."""
    from app import dados, sla
    from app.main import app

    mov = _mov([(1, 30), (8, 10), (16, 10), (24, 10), (40, 10)], "v2-ct-html")  # 35 exclusivos
    monkeypatch.setattr(dados.sla, "df", lambda forcar=False: mov)
    sla._cache.clear()
    with TestClient(app) as cli:
        html = cli.get("/viu-agenciamento/sla/como-medimos?talentos=exclusivos").text
    sla._cache.clear()
    assert html.count('class="slide slide-estudo') == 5  # V2: 3 e 4 unidos, conclusão fora
    assert 'slide-cem"' not in html and 'slide-tempo"' not in html and 'slide-conclusao"' not in html
    s3 = html.split('slide-cem-tempo"')[1].split('slide-mes"')[0]
    assert "Quantos saem em até 2 dias, e quanto do tempo levam?" in s3
    for g in ("todos", "exclusivos", "nao-exclusivos"):
        assert f'href="?talentos={g}#3"' in s3
    assert 'href="?talentos=exclusivos#3" class="grupo" aria-current="true"' in s3
    assert s3.count('<span class="cq cq-') == 100  # só os 100 quadrados
    # V2 (Caio, 30/10/2026): as cinco faixas (W2) em tons da família do lado (A: 1–2; B: 3–5), os mesmos % de V2/W3
    t = c.tempo_cem(mov, "2026-10", "exclusivos")
    quad = re.findall(r'class="cq (cq-[ab]) ct-sw([1-5])"', s3)
    assert len(quad) == 100 and all((k == "cq-a") == (int(f) <= 2) for k, f in quad)
    assert [sum(1 for _, f in quad if int(f) == i + 1) for i in range(5)] == [l["pedidos"] for l in t["linhas"]]
    for l in t["linhas"]:  # mini legendas: pedidos (Quantidade) e horas (Tempo) de cada faixa
        assert f'<span class="ct-mini-n">{l["pedidos"]}</span> {l["rotulo"]}' in s3
        assert f'<span class="ct-mini-n">{l["horas"]}%</span> {l["rotulo"]}' in s3
    assert s3.count('class="ct-trilho ct-trilho-q"') == 2  # a barra de pedidos de cada lado (espelha o Tempo)
    n_a = sum(l["n"] for l in t["linhas"][:2])
    assert f"de cada 100 pedidos · {n_a} pedidos de jan a set" in s3
    assert 'class="ct-waffle" role="img" aria-label="Cem quadrados; cada um é 1% dos 35 orçamentos entregues de jan a set' in s3
    assert s3.count('class="ct-trilho"') == 2 and "% das horas de trabalho da equipe" in s3
    assert '<p class="estudo-recorte">' not in s3  # V2: sem o selo do topo
    # V2 (30/10/2026, Caio): a resposta V10 saiu da tela (segue em tempo_cem["resposta"])
    assert "típico de" in s3 and "explora-conclusoes" not in s3 and "passam disso</strong> e levam" not in s3
    assert "passam disso</strong> e levam" in t["resposta"]
    assert 'class="cem-curva"' not in s3 and "Curva acumulada" not in s3  # a curva saiu (Caio: só o essencial)
    assert '<a class="gancho-link" href="#4">' in s3 and "foram um mês ruim, ou é sempre assim?" in s3
    assert 'style="' not in s3
    # gancho do slide 2 continua levando ao slide 3
    assert '<a class="gancho-link" href="#3">E se olharmos para 100 pedidos, o que vemos?' in html


def test_slide_3_unificado_com_poucos_dados(monkeypatch):
    from app import dados, sla
    from app.main import app

    mov = _mov([(1, 10), (8, 10)], "v2-ct-poucos")
    monkeypatch.setattr(dados.sla, "df", lambda forcar=False: mov)
    sla._cache.clear()
    with TestClient(app) as cli:
        html = cli.get("/viu-agenciamento/sla/como-medimos").text
    sla._cache.clear()
    s3 = html.split('slide-cem-tempo"')[1]
    assert "Ainda não há orçamentos suficientes" in s3.split('slide-mes"')[0] and "ct-waffle" not in s3
