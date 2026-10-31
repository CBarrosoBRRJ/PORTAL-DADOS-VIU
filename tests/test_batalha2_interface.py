"""Batalha 2, 2ª leva (interface, layout, animação; 26/10/2026): base congelada sem aviso de atraso, rodapé datado em
toda rota (inclusive máscaras), um só horário no menu e no rodapé, /regras retirada, Resultado fora da reunião, filtro
de talentos nos links, "Voltar ao SLA" no slide 8 e Previsão com as duas medidas de erro (G4-N8)."""

import re
from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from app import config


@pytest.fixture
def cliente():
    from app.main import app

    with TestClient(app) as c:
        yield c


# G1-engenharia-1: com CONGELAR, a base da reunião não é relida — nada de "base atrasada"
def test_base_congelada_nao_acende_atraso(monkeypatch):
    import pandas as pd

    from app import dados

    t = dados.Tabela("x", "p.d.t", em_fundo=False)
    t._df = pd.DataFrame({"a": [1]})
    t.modificada_em = datetime(2026, 10, 23, 17, 23, tzinfo=config.FUSO)  # sexta; hoje segunda 10:00
    seg_10h = datetime(2026, 10, 26, 10, 0, tzinfo=config.FUSO)
    monkeypatch.setattr(config, "CONGELAR", False)
    assert t.estado(seg_10h) == "base_atrasada"
    monkeypatch.setattr(config, "CONGELAR", True)
    assert t.estado(seg_10h) == "congelada"
    t.erro = "BigQuery fora"
    assert t.estado(seg_10h) == "falha_leitura"  # falha de leitura continua visível


def test_pagina_congelada_sem_aviso_amarelo(cliente, monkeypatch):
    from app import dados

    monkeypatch.setattr(config, "CONGELAR", True)
    for nome in ("entrada", "fluxo", "sla"):
        tab = getattr(dados, nome)
        s = tab.situacao()
        monkeypatch.setattr(tab, "situacao", lambda s=s: {**s, "estado": "congelada"})
    for rota in ("/viu-agenciamento", "/viu-agenciamento/sla", "/viu-agenciamento/qualidade"):
        html = cliente.get(rota).text
        assert 'class="aviso-atraso"' not in html and "não atualizou no horário" not in html, rota
        assert "base congelada para a apresentação" in html, rota


# G2-5 / G3-7 / G4-N1: rodapé datado em toda rota visível, inclusive as máscaras e o estudo
@pytest.mark.parametrize("rota", ["/viu-agenciamento", "/viu-agenciamento/talentos", "/viu-agenciamento/atendimento",
                                  "/viu-agenciamento/sla", "/viu-agenciamento/sla/como-medimos",
                                  "/viu-agenciamento/previsao", "/viu-agenciamento/negocios-fechados",
                                  "/viu-agenciamento/qualidade", "/viu-agenciamento/o-que-falta"])
def test_rodape_datado_em_toda_rota(cliente, rota):
    r = cliente.get(rota)
    assert r.status_code == 200 and 'class="rodape-dados">Dados até' in r.text, rota
    assert 'class="menu-status' in r.text, rota  # selo do menu também nas máscaras


def test_menu_e_rodape_com_o_mesmo_horario(cliente, monkeypatch):
    from app import dados

    processado = datetime(2026, 10, 26, 9, 1, tzinfo=config.FUSO)
    alterada = datetime(2026, 10, 26, 9, 3, tzinfo=config.FUSO)
    for nome in ("entrada", "fluxo"):
        tab = getattr(dados, nome)
        s = tab.situacao()
        monkeypatch.setattr(tab, "situacao", lambda s=s: {**s, "modificada_em": alterada, "processado_em": processado})
    html = cliente.get("/viu-agenciamento").text
    menu = re.search(r"<strong>Dados de ([^<]+)</strong>", html).group(1)
    assert menu.endswith("09:01") and "atualizados em 26/10/2026, 09:01" in html
    assert "metadado da tabela: 26/10/2026, 09:03" in html  # o modified fica só no title


def test_mascara_da_qualidade_sem_nota_interna(cliente):
    html = cliente.get("/viu-agenciamento/qualidade").text
    assert "antes de ir à reunião" not in html and "Em preparação nesta semana" in html


@pytest.mark.parametrize("secao", ["sla", "atendimento", "previsao", "talentos", "qualidade"])
def test_nenhuma_rota_regras_responde(cliente, secao):
    r = cliente.get(f"/viu-agenciamento/{secao}/regras", follow_redirects=False)
    assert r.status_code == 301


def test_regras_html_retirado():
    from pathlib import Path

    assert not (Path(__file__).resolve().parent.parent / "app" / "templates" / "regras.html").exists()


def test_reuniao_termina_na_previsao_e_modo_no_html(monkeypatch):
    from app.main import app

    monkeypatch.setattr(config, "MODO_APRESENTACAO", True)
    monkeypatch.setattr(config, "SECOES_VISIVEIS", frozenset())
    with TestClient(app) as cli:
        html = cli.get("/viu-agenciamento/previsao").text
    assert '<meta name="relatorio-modo" content="apresentacao">' in html
    assert "negocios-fechados" not in html and "/viu-agenciamento/qualidade" not in html  # D59: fora da navegação
    assert re.search(r'href="/viu-agenciamento/encerramento" rel="next"', html)  # V2: a Previsão segue a última


# G4-N1: filtro de talentos nos links entre SLA, estudo e Previsão
def test_links_com_filtro_de_talentos(cliente):
    html = cliente.get("/viu-agenciamento/sla?talentos=exclusivos").text
    assert re.search(r'href="/viu-agenciamento/previsao#1"[^>]*data-filtro-talentos', html)  # aba e menu
    # o estudo abre pelo botão (fora da sequência das setas): do SLA a sequência segue para a Previsão, levando o
    # filtro; do estudo, a saída também é a Previsão
    assert re.search(r'href="/viu-agenciamento/lia#1" rel="next" data-proxima-secao', html)  # V2: SLA → LIA
    assert not re.search(r'href="/viu-agenciamento/atendimento#1"[^>]*data-filtro-talentos', html)
    html = cliente.get("/viu-agenciamento/sla/como-medimos?talentos=exclusivos").text
    assert 'class="fechar-estudo" href="/viu-agenciamento/sla?talentos=exclusivos#1"' in html  # volta com o filtro
    assert re.search(r'href="/viu-agenciamento/lia#1" rel="next" data-proxima-secao', html)  # V2: do estudo, à LIA
    assert 'class="proxima proxima-gancho so-leitor"' in html  # o estudo tem os próprios ganchos
    from pathlib import Path  # V2: sem a conclusão, a saída fica no último slide: volta ao SLA (principal) e a próxima página
    tpl = (Path(__file__).resolve().parent.parent / "app" / "templates" / "como_medimos.html").read_text(encoding="utf-8")
    assert '<a class="gancho-link" href="{{ volta }}">Voltar ao SLA' in tpl and 'class="gancho-link gancho-sec" href="{{ proxima.href }}"' in tpl


# G4-N8: as duas medidas do erro (D55: o painel de três linhas saiu da tela; D56: série curta sem verificação)
def test_previsao_duas_medidas(cliente):
    from app.apresentacoes.gestao_orcamentos.previsao import calculos as C

    p = C.ler()
    t = C.tela(p)
    assert "palpite" not in t and "comparacao" not in t
    c = t["colunas"][0]
    assert c["verificacao"]["wape"] == p["series"][c["serie"]]["metricas"]["verificacao"]["wape"]
    assert c["ingenua"]["wape"] == p["series"][c["serie"]]["ingenua"]["wape"]
    curta = C.tela(p, "exclusivos")["colunas"][1]  # D56: Mercado exclusivos = série própria só de 2026 → sem verificação
    assert curta["verificacao"] is None and curta["curta"] and curta["ingenua"]["verificacao"] is None
    html = cliente.get("/viu-agenciamento/previsao").text
    assert "Vale mais que o palpite simples?" not in html and "Modelo contra modelo" not in html
    assert f"Modelo: {p['series']['Inbound']['rotulo']}" in html and "repetir o último mês erraria" in html
    assert "(jan–mai)" in html
