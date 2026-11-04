"""Talentos D50 (26/10/2026, pedido do gerente do Caio): seletor Todos / Exclusivos / Não exclusivos filtrando a página
inteira (T7), resposta por recorte (T8), barra do ano com o grupo destacado (T9) e mapa de calor dos 10 talentos mais
pedidos × jan–dez (T10). Dados sintéticos (conftest e tabelas montadas aqui)."""

import re
from datetime import date

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from app.apresentacoes.gestao_orcamentos.talentos import calculos as tal


@pytest.fixture
def cliente():
    from app.main import app

    with TestClient(app) as c:
        yield c


def _divisao(ex=60, ne=35, sem=5):
    df = pd.DataFrame({"ano": [2026] * 3, "categoria": ["Exclusivos", "Não exclusivos", "Sem talento"],
                       "n": [ex, ne, sem], "dos_quais_squad": [0, 2, 0]})
    return tal.divisao(df, ex + ne + sem, 2026)


def _ranking(grupos: dict) -> pd.DataFrame:
    """{grupo: [(talento, {mês: n}), ...]} -> linhas no formato da gold gld_agenciamento_2026_talentos_ranking (já cortado no top 10)."""
    linhas = []
    for g, ts in grupos.items():
        for nome, meses in ts:
            for m, n_mes in meses.items():
                linhas.append({"grupo": g, "talento": nome, "n": sum(meses.values()), "ultimo_pedido": pd.Timestamp(2026, m, 5),
                               "empate_fora": 0, "talentos_grupo": len(ts) + 3, "mes": date(2026, m, 1), "n_mes": n_mes})
    return pd.DataFrame(linhas)


def _doze(prefixo, base):
    # 12 talentos com totais base, base-1, ...: o corte no 10º deixa 2 de fora
    return [(f"{prefixo} {i:02d}", {1: base - i, 3: 1}) for i in range(12)]


def test_top10_por_filtro_ordenado_e_com_soma_do_recorte():
    d = _divisao(ex=200, ne=150, sem=10)
    df = _ranking({"exclusivo": _doze("Ex", 20)[:10], "nao-exclusivo": _doze("Ne", 10)[:10],
                   "todos": sorted(_doze("Ex", 20) + _doze("Ne", 10), key=lambda t: -sum(t[1].values()))[:10]})
    top = tal.top_por_grupo(df, d)
    assert set(top) == {"exclusivo", "nao-exclusivo", "todos"}
    for tg in top.values():
        ns = [r["n"] for r in tg["linhas"]]
        assert len(ns) == 10 and ns == sorted(ns, reverse=True)
        assert [r["posicao"] for r in tg["linhas"]] == list(range(1, 11))
        assert tg["n"] == sum(ns)
    assert top["todos"]["total"] == 360 and top["exclusivo"]["total"] == 200 and top["nao-exclusivo"]["total"] == 150
    # F13 (31/10/2026): meio para cima, como o resto do portal — 165 de 200 = 82,5% → 83% (o round() dava 82)
    assert top["exclusivo"]["n"] == 165 and top["exclusivo"]["pct"] == 83
    assert top["exclusivo"]["talentos"] == 13  # talentos_grupo (talentos com pedido no ano no recorte)


def test_soma_mensal_igual_ao_total_e_meses_futuros_vazios():
    d = _divisao()
    df = _ranking({"exclusivo": [("Ana", {1: 5, 2: 3, 10: 2}), ("Bia", {4: 4})]})
    tg = tal.top_por_grupo(df, d)["exclusivo"]
    m = tal.mapa(tg, date(2026, 10, 20))
    assert [c["rotulo"] for c in m["colunas"]] == ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out",
                                                   "nov", "dez"]
    for r in m["linhas"]:
        assert sum(c["n"] or 0 for c in r["celulas"]) == r["n"]
        assert [c["n"] for c in r["celulas"][10:]] == [None, None]  # nov e dez: futuros, sem número
        assert all(c["futuro"] for c in r["celulas"][10:]) and not any(c["futuro"] for c in r["celulas"][:10])
    assert m["colunas"][9]["parcial"] and not m["colunas"][8]["parcial"]  # out até 20: parcial
    assert m["linhas"][1]["celulas"][0]["n"] == 0 and m["linhas"][1]["celulas"][0]["nivel"] == 0  # mês sem pedido = 0
    assert m["linhas"][0]["celulas"][0]["nivel"] == tal.NIVEIS  # o maior mês do recorte tem o tom mais forte
    assert all(1 <= c["nivel"] <= tal.NIVEIS for r in m["linhas"] for c in r["celulas"] if c["n"])
    assert m["totais_mes"][0] == 5 and m["totais_mes"][11] is None
    # mês fechado no último dia: nada parcial
    assert not any(c["parcial"] for c in tal.mapa(tg, date(2026, 10, 31))["colunas"])


def test_mapa_some_se_os_meses_nao_fecham_com_o_total():
    df = _ranking({"exclusivo": [("Ana", {1: 5})]})
    df.loc[0, "n"] = 6  # total do ano diferente da soma dos meses
    tg = tal.top_por_grupo(df, _divisao())["exclusivo"]
    assert tal.mapa(tg, date(2026, 10, 20)) is None
    # sem as colunas mensais (consulta antiga), o mapa também não aparece
    assert tal.mapa(tal.top_por_grupo(df.drop(columns=["mes", "n_mes"]), _divisao())["exclusivo"], date(2026, 10, 20)) is None


def test_heroi_por_filtro_frases_e_numeros():
    d = _divisao(ex=60, ne=35, sem=5)
    df = _ranking({"exclusivo": [("Ana", {1: 20}), ("Bia", {2: 10})], "nao-exclusivo": [("Caio", {3: 7})],
                   "todos": [("Ana", {1: 20}), ("Bia", {2: 10}), ("Caio", {3: 7})]})
    top = tal.top_por_grupo(df, d)
    h = tal.heroi(d, top, "todos")
    assert (h["antes"], h["pct"], h["meio"], h["fim"]) == ("Da demanda do ano,", 60, ("vai para os", "talentos"), "exclusivos.")
    assert h["apoio_num"] == "60 de 100" and "35 não exclusivos" in h["apoio_ex"] and "5 sem talento" in h["apoio_ex"]
    h = tal.heroi(d, top, "exclusivos")
    assert h["pct"] == 50 and h["antes"] == "Dos pedidos de talentos exclusivos," and h["meio"] == ("vão para os", "2 talentos")
    assert h["fim"] == "mais pedidos." and h["apoio_num"] == "30 de 60"
    h = tal.heroi(d, top, "nao-exclusivos")
    assert h["pct"] == 20 and h["meio"] == ("vão para o", "talento") and h["fim"] == "mais pedido."
    assert "Squad de Talentos" in h["apoio_ex"]
    # sem ranking coerente: resposta sem número, nunca um % inventado
    assert tal.heroi(d, {}, "exclusivos")["pct"] is None


def test_barra_destaca_o_recorte():
    d = _divisao()
    assert not any(g["destaque"] or g["apagado"] for g in tal.barra(d, "todos"))
    b = tal.barra(d, "nao-exclusivos")
    assert [g["destaque"] for g in b] == [False, True, False] and [g["apagado"] for g in b] == [True, False, True]
    assert [g["n"] for g in b] == [g["n"] for g in d["grupos"]]  # a barra continua com a divisão do ano


def test_seletor_tres_links_e_pagina_filtrada(cliente):
    r = cliente.get("/viu-agenciamento/talentos")
    nav = re.search(r'<nav class="grupos talentos-grupos".*?</nav>', r.text, re.DOTALL).group(0)
    links = re.findall(r'href="\?talentos=([\w-]+)#1"', nav)
    assert links == ["todos", "exclusivos", "nao-exclusivos"]
    assert 'data-navegador data-chave="talentos"' in nav and nav.count('aria-current="true"') == 1
    assert re.search(r'href="\?talentos=todos#1" class="grupo" aria-current="true"', nav)
    assert '<span class="grupo-valor">22<' in nav and '<span class="grupo-valor">13<' in nav  # pedidos do ano do recorte
    # Exclusivos: herói do top 10 do grupo; barra com o grupo destacado; mapa só com os exclusivos
    r = cliente.get("/viu-agenciamento/talentos?talentos=exclusivos")
    assert re.search(r'href="\?talentos=exclusivos#1" class="grupo" aria-current="true"', r.text)
    assert "Dos pedidos de talentos exclusivos," in r.text and 'f-numero">38%<' in r.text  # 5 de 13
    assert "divisao-destaque" in r.text and r.text.count("divisao-apagada") == 2
    tabela = re.search(r'<table class="mapa-tabela[ "].*?</table>', r.text, re.DOTALL).group(0)
    assert "Talento A" in tabela and "Talento B" in tabela and "Talento C" not in tabela
    assert "(recorte escolhido)" in r.text
    # Não exclusivos
    r = cliente.get("/viu-agenciamento/talentos?talentos=nao-exclusivos")
    tabela = re.search(r'<table class="mapa-tabela[ "].*?</table>', r.text, re.DOTALL).group(0)
    assert "Talento C" in tabela and "Talento A" not in tabela
    assert "Dos pedidos de talentos não exclusivos," in r.text
    # filtro desconhecido volta a "todos"
    r = cliente.get("/viu-agenciamento/talentos?talentos=xyz")
    assert re.search(r'href="\?talentos=todos#1" class="grupo" aria-current="true"', r.text)


def test_mapa_acessivel_e_com_numero_em_cada_celula(cliente):
    r = cliente.get("/viu-agenciamento/talentos")
    tabela = re.search(r'<table class="mapa-tabela[ "].*?</table>', r.text, re.DOTALL).group(0)
    assert '<caption class="so-leitor">' in tabela and tabela.count('<th scope="col"') == 14  # talento + 12 meses + ano
    assert tabela.count('<th scope="row"') == 3
    # mês futuro: célula sem número, só "sem dado" para o leitor de tela; cabeçalho diz "(mês futuro)"
    assert "(mês futuro)" in tabela and "hm-futuro" in tabela and '<span class="so-leitor">sem dado</span>' in tabela
    # meses passados: número escrito (inclusive o zero)
    celulas = re.findall(r'<td class="hm [^"]*">(.*?)</td>', tabela)
    passados = [c for c in celulas if "sem dado" not in c]
    assert passados and all(re.search(r'<span class="hm-num">\d+</span>', c) for c in passados)
    assert 'class="mapa-total">3<' in tabela
    assert "style=" not in tabela  # CSP: nada de style="" (tons por classe)
    # o rodapé datado continua na página
    assert "Dados até" in r.text


def test_abas_levam_o_filtro_e_movimento_sem_esconder_numeros(cliente):
    html = cliente.get("/viu-agenciamento/sla?talentos=exclusivos").text
    assert re.search(r'href="/viu-agenciamento/previsao#1"[^>]*data-filtro-talentos', html)  # T7: aba leva o recorte
    assert "/viu-agenciamento/talentos#1" not in html  # Caio, 04/11/2026: Talentos oculta da navegação
    from pathlib import Path

    css = (Path(__file__).resolve().parent.parent / "app" / "static" / "estilo.css").read_text(encoding="utf-8")
    bloco = css[css.index("/* ---------- Talentos, D50"):css.index("/* ---------- fim Talentos D50")]
    assert "prefers-reduced-motion: no-preference" in bloco
    # o número da célula nunca começa invisível: só o tom (::before) entra
    assert not re.search(r":not\(\.entrou\)[^{]*hm-num[^{]*\{[^}]*opacity", bloco)
    assert re.search(r":not\(\.entrou\) \.talentos-mapa \.hm::before \{ opacity: 0; \}", bloco)
