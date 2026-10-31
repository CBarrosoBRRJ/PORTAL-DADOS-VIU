"""D52 (26/10/2026, Caio): Início em dois quadrantes — resposta composta como nuvem de palavras (padrão do SLA) em cima,
caixa cinza de altura fixa (tabela de tipos ↔ extrato do mês) embaixo e o cartão do gráfico com o pé alinhado ao da
caixa. Dados sintéticos de tests/conftest.py (carga até 20/10/2026: 22 pedidos em 2026, 13 no mesmo período de 2025)."""

import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

CSS = Path(__file__).resolve().parents[1].joinpath("app", "static", "estilo.css").read_text(encoding="utf-8")


@pytest.fixture
def cliente():
    from app.main import app

    with TestClient(app) as c:
        yield c


def _frase(html):
    m = re.search(r'<p class="frase inicio-frase">(.*?)</p>', html, re.S)
    assert m, "nuvem de palavras ausente"
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", m.group(1))).strip()


def test_nuvem_com_numeros_dinamicos(cliente):
    html = cliente.get("/viu-agenciamento").text
    # a frase segue na ordem de leitura (leitor de tela) e todos os pedaços vêm dos dados: total, ano e período (E1, E4)
    assert _frase(html) == "Chegaram 22 pedidos de orçamento em 2026, até 20 de outubro"
    assert '<span class="hero-numero f-numero">22</span>' in html
    # apoio: selo do ano anterior (E8; base 13 < 30 → só a referência) e as duas barras do mesmo período
    apoio = html[html.index('class="f-apoio inicio-apoio entra"'):]
    assert "Em 2025" in apoio and "13 no mesmo período" in apoio
    assert '<span class="barras-valor">22</span>' in apoio and '<span class="barras-valor">13</span>' in apoio
    assert '<p class="barras-periodo">mesmo período: até 20/out</p>' in apoio
    # quadrante de baixo: a tabela de tipos dentro da caixa trocável; a legenda dos tipos só no topo do cartão
    assert html.index('class="inicio-cima"') < html.index("data-caixa-troca") < html.index('class="tipos-ano"')
    assert "entrada-legenda" not in html and '<span class="legenda">' in html


def test_extrato_no_mesmo_lugar(cliente, entrada_diaria, monkeypatch):
    from app import dados
    from app.apresentacoes.gestao_orcamentos.entrada import calculos as ent
    recente = entrada_diaria.loc[entrada_diaria["data"].astype(str) < "2026-03"].copy()  # fevereiro = mês recente
    ent._cache.clear()
    monkeypatch.setattr(dados.entrada, "df", lambda: recente)
    html = cliente.get("/viu-agenciamento?mes=2026-02").text
    assert "Fevereiro de 2026" in html and 'class="tipos-ano"' not in html  # o extrato troca a tabela no mesmo lugar
    # a nuvem continua com os números do ano (dinâmicos: aqui a carga vai até fevereiro) e o rótulo fica na linha do título
    assert re.fullmatch(r"Chegaram \d+ pedidos de orçamento em 2026, até \d+ de fevereiro", _frase(html))
    assert re.search(r'<div class="extrato-topo">\s*<p class="entrada-contexto">Análise mensal</p>\s*<h3 class="extrato-titulo"', html)


def test_css_quadrantes_e_cartao():
    bloco = CSS[CSS.index("/* Início (26/10/2026, D52, Caio)"):]
    bloco = bloco[:bloco.index("\n}\n") if "\n}\n" in bloco else bloco.index("\r\n}\r\n")]
    assert ".entrada .caixa-troca { flex: none; height: max(14.2em, 219px); }" in bloco  # altura fixa = tabela do ano
    assert "align-self: end" in bloco and "height: min(100%, 34.25em)" in bloco  # pé com pé; tamanho do cartão do SLA
    assert ".entrada .caixa-troca > .extrato { flex: 1; min-height: 0; margin: 0;" in bloco  # extrato cabe na caixa
