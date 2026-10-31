"""Revisão de 25/10/2026 (Início, Talentos, Atendimento): itens aprovados pela auditoria e decisões 1–14, com os dados
sintéticos de tests/conftest.py (carga até 20/10/2026)."""

import re
from datetime import datetime

import pandas as pd
import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def cliente():
    from app.main import app

    with TestClient(app) as c:
        yield c


def fluxo_coerente(diaria, processado_em):
    """Fluxo com uma linha por safra (tudo entregue no próprio mês), com a mesma soma da entrada diária."""
    b = diaria.assign(m=pd.to_datetime(diaria["data"]).dt.to_period("M"))
    s = (b["quantidade"] + b["quantidade_estimada"]).groupby(b["m"]).sum()
    f = pd.DataFrame({"mes_entrada": [p.to_timestamp().date() for p in s.index], "evento": "entregue",
                      "mes_evento": [p.to_timestamp().date() for p in s.index], "quantidade": s.values})
    f["grupo_input"], f["tipo_de_input"], f["familia"] = "Mercado", "Mercado", "Nenhuma"
    f["_processado_em"] = pd.Timestamp(processado_em, tz="UTC")
    return f


# ---------- Início ----------
def test_grafico_do_inicio_em_cartao_com_titulo(cliente):
    """INI-CARTAO + decisão 1: figure com a classe comum do cartão e título visível derivado do ano."""
    r = cliente.get("/viu-agenciamento")
    assert re.search(r'<figure class="colunas tipos cartao-grafico( colunas-par)?">', r.text)
    assert '<span class="colunas-titulo">Pedidos por mês em 2026, por tipo de input</span>' in r.text


def test_grafico_do_inicio_com_o_ano_anterior_ao_lado(cliente):
    """28/10/2026 (Caio): cada mês com dado do ano anterior ganha a coluna dele (tracejada) e os anos sob o mês; a
    legenda nomeia o ano anterior; os números vêm do mesmo m.anterior da dica."""
    from app.apresentacoes.gestao_orcamentos import apresentacao as paginas

    e = paginas.montar_inicio({})["entrada"]
    html = cliente.get("/viu-agenciamento").text
    com_anterior = [m for m in e["meses"] if m["total"] and m["anterior"]]
    assert com_anterior and 'colunas-par' in html and f'{e["ano_anterior"]}, mesmo mês' in html
    assert html.count('class="pilha pilha-anterior"') == len(com_anterior)
    assert html.count('class="mes-anos"') == len(com_anterior)
    for m in com_anterior:
        assert f'<span class="pilha-total pilha-total-anterior" aria-hidden="true">{m["anterior"]["total"]}</span>' in html \
            or f'>{m["anterior"]["total"]:,}'.replace(",", ".") in html


def test_barras_dizem_mesmo_periodo(cliente):
    """Decisão 2: sob as barras, 2025 é o mesmo período (até o último dia da carga), não o ano inteiro."""
    r = cliente.get("/viu-agenciamento")
    assert '<p class="barras-periodo">mesmo período: até 20/out</p>' in r.text


def test_variacao_com_seta_e_motivo_do_traco(cliente, base_um):
    """Decisão 3 e IN-A1(b): seta pastel (▼ na queda) com o sentido para o leitor; '–' com o motivo em texto."""
    r = cliente.get("/viu-agenciamento")
    assert 'class="var-seta var-alta" aria-hidden="true">▲</span><span class="so-leitor">alta de </span>' in r.text


def test_traco_tem_texto_para_leitor(cliente):
    r = cliente.get("/viu-agenciamento")
    assert '–<span class="so-leitor"> base pequena no ano anterior</span>' in r.text


def test_parcela_menor_que_um_por_cento():
    """Decisão 4: 0% com pedidos vira '<1%'; sem pedidos continua 0%; sem percentual, vazio."""
    from app.formato import parcela

    assert parcela(0, 3) == "<1%" and parcela(0, 0) == "0%" and parcela(53, 2945) == "53%" and parcela(None, 0) == ""


def test_leitor_do_mes_parcial_diz_mesmo_periodo(cliente):
    """INI-D2: no mês parcial, o ano anterior é o mesmo período (até o mesmo dia)."""
    r = cliente.get("/viu-agenciamento")
    assert "Em outubro de 2025, no mesmo período (até 20/10): 4" in r.text


def test_divergencia_em_safra_antiga_so_vai_ao_log(entrada_diaria, fluxo_mensal, caplog):
    """Decisão 5: safra de 2025 divergente não bloqueia; safra do ano exibido (2026) bloqueia."""
    from app.apresentacoes.gestao_orcamentos import apresentacao as ap
    from tests.conftest import com_dias

    diaria = com_dias(entrada_diaria, [], processado_em="2026-10-21 12:00")
    ok = fluxo_coerente(diaria, "2026-10-21 12:00")
    assert ap._mesma_fotografia(diaria, ok)
    antiga = ok.copy()
    antiga.loc[pd.to_datetime(antiga["mes_entrada"]).dt.year == 2025, "quantidade"] += 1
    with caplog.at_level("WARNING"):
        assert ap._mesma_fotografia(diaria, antiga)
    assert "safras de anos anteriores" in caplog.text
    atual = ok.copy()
    atual.loc[pd.to_datetime(atual["mes_entrada"]).dt.year == 2026, "quantidade"] += 1
    assert not ap._mesma_fotografia(diaria, atual)


def test_mes_futuro_do_inicio_em_italico():
    """IN-A1(a): no Início, o mês futuro usa --tinta-3 (≥ 4,5:1) em itálico, não o cinza de 2,7:1."""
    from pathlib import Path

    css = (Path(__file__).resolve().parent.parent / "app" / "static" / "estilo.css").read_text(encoding="utf-8")
    assert ".entrada .mes-futuro .mes-rotulo { color: var(--tinta-3); font-style: italic; }" in css


def test_rodape_usa_o_processamento_da_carga(cliente, monkeypatch):
    """INI-D1: 'modified' em D+1 (ALTER de descrição) e _processado_em em D → o rodapé segue o processamento."""
    from app import config, dados

    processado = datetime(2026, 10, 23, 17, 23, tzinfo=config.FUSO)
    alterada = datetime(2026, 10, 24, 10, 0, tzinfo=config.FUSO)
    base = {"nome": "Entrada", "tabela": "teste.entrada", "versao": 1, "modificada_em": alterada, "processado_em": processado,
            "carregada_em": alterada, "verificada_em": alterada, "linhas": 1, "bytes_lidos": 0, "segundos_carga": 0.0,
            "atrasada": False, "estado": "em_dia", "erro": None}
    monkeypatch.setattr(dados.entrada, "situacao", lambda: base)
    r = cliente.get("/viu-agenciamento")
    assert "Dados até 22/10/2026 · atualizados em 23/10/2026, 17:23" in r.text
    monkeypatch.setattr(dados.entrada, "situacao", lambda: {**base, "processado_em": None})  # sem a coluna: modified
    assert "Dados até 23/10/2026 · atualizados em 24/10/2026, 10:00" in cliente.get("/viu-agenciamento").text


def test_processado_em_da_tabela():
    from app import dados

    t = dados.Tabela("x", "p.d.t", chave=())
    assert t.processado_em() is None
    t._df = pd.DataFrame({"_processado_em": [pd.Timestamp("2026-10-23 20:23", tz="UTC")] * 2})
    assert t.processado_em().strftime("%d/%m %H:%M") == "23/10 17:23"
    t._df = pd.DataFrame({"a": [1]})
    assert t.processado_em() is None


# ---------- Talentos ----------
def test_nomes_do_top_so_quebram_no_palco_estreito():
    """C1: no palco largo valem nowrap e max-content (T6); a quebra dos nomes só dentro de width < 860px."""
    from pathlib import Path

    css = (Path(__file__).resolve().parent.parent / "app" / "static" / "estilo.css").read_text(encoding="utf-8")
    i = css.index(".dica-top-nome { white-space: normal; overflow-wrap: anywhere; }")
    assert css.rfind("@container palco (width < 860px) {", 0, i) > css.rfind("}\n", 0, css.rfind("@container palco (width < 860px) {", 0, i))
    assert css.count("overflow-wrap: anywhere; }") == 1 or "C1 (25/10/2026)" in css


def test_bases_divergentes_mostram_numeros_com_aviso(cliente, monkeypatch, entrada_diaria):
    """Decisão 10 (+ TAL-D1): total do Início + 1 → a página mostra os números e diz que está sendo atualizada."""
    from app import dados
    from app.apresentacoes.gestao_orcamentos.entrada import calculos as ent

    total = ent.entrada(entrada_diaria)["total"]
    monkeypatch.setattr(dados.talentos, "df", lambda forcar=False: pd.DataFrame({
        "ano": [2026] * 3, "categoria": ["Exclusivos", "Não exclusivos", "Sem talento"], "n": [14, 8, 1],
        "total": [total + 1] * 3, "pct": [0.0] * 3, "dos_quais_squad": [0, 0, 0]}))
    r = cliente.get("/viu-agenciamento/talentos")
    assert r.status_code == 200 and "está sendo atualizada" in r.text
    assert "a base de talentos soma 23 pedidos e o Início, 22" in r.text and 'class="hero-numero' in r.text


def test_empate_no_corte_do_top10(cliente, monkeypatch):
    """Decisão 11: com outros talentos empatados com o 10º, a nota do mapa (D50) termina com 'empatado com mais N'."""
    from app import dados

    nomes = [f"Talento {c}" for c in "ABCDEFGHIJ"]
    monkeypatch.setattr(dados.talentos_top, "df", lambda forcar=False: pd.DataFrame({
        "grupo": ["exclusivo"] * 10, "talento": nomes, "n": [1] * 10,
        "ultimo_pedido": pd.to_datetime(["2026-10-20"] * 10), "empate_fora": [2] * 10,
        "mes": pd.to_datetime(["2026-03-01"] * 10).date, "n_mes": [1] * 10}))
    r = cliente.get("/viu-agenciamento/talentos?talentos=exclusivos")
    assert "10º lugar empatado com mais 2 talentos (1 pedidos cada)" in r.text


def test_sem_empate_sem_nota(cliente):
    r = cliente.get("/viu-agenciamento/talentos")
    assert "empatado com mais" not in r.text


def test_data_carga_ignora_fuso_e_nat(entrada_diaria):
    """TAL-D9: _processado_em sem fuso dá o mesmo dia de carga; todo NaT não quebra (sem carga)."""
    from app import dados

    com_fuso = entrada_diaria.assign(_processado_em=pd.Timestamp("2026-10-21 12:00", tz="UTC"))
    sem_fuso = entrada_diaria.assign(_processado_em=pd.Timestamp("2026-10-21 12:00"))
    assert dados.data_carga(com_fuso) == dados.data_carga(sem_fuso) == pd.Timestamp("2026-10-21").date()
    assert dados.data_carga(entrada_diaria.assign(_processado_em=pd.NaT)) is None


# ---------- Atendimento ----------
def test_quadro_marca_o_mes_parcial_e_textos_novos(cliente):
    """AT-04 + decisão 6: 'parcial' miúdo no cabeçalho (sem '*'), legenda do mês parcial, rótulos novos e AT-11."""
    r = cliente.get("/viu-agenciamento/atendimento")
    assert r.status_code == 200
    assert "<th scope=\"col\"><small>parcial</small>out</th>" in r.text  # D53: parcial em cima and "out*" not in r.text
    assert "out parcial</li>" in r.text and "out (parcial, até 20 de outubro)" in r.text
    assert "Entregues ao cliente</th>" in r.text and "Resolvemos (entregues)" not in r.text
    assert 'do que havia para atender </span>%</button>' in r.text and "Resolvemos do que havia" not in r.text  # D53: rótulo "%" com dica
    assert '<div class="kpi-periodo"><dt class="kpi-periodo-rot">dados até</dt>' in r.text
    assert '<span class="kpi-seta"' not in r.text and '<p class="kpi-periodo"' not in r.text
    assert 'role="region" aria-label="Quadro do extrato, role para o lado"' in r.text and 'tabindex="0"' in r.text
    assert "≥ 100%</li>" in r.text and "90–99%</li>" in r.text and "&lt; 90%</li>" in r.text  # do objetivo e do corte


def test_percentual_meio_para_cima():
    """AT-D07: 153/200 = 76,5 → 77 (C8), não 76 do round() do Python."""
    from app.apresentacoes.gestao_orcamentos.atendimento import calculos as at

    assert at.pct_meio(153, 200) == 77 and at.pct_meio(0, 0) == 0 and at.pct_meio(1, 3) == 33


def test_meses_zerados_nao_quebram(cliente, monkeypatch, entrada_diaria, fluxo_mensal):
    """AT-D06: fluxo e entradas zerados → a página responde (escala com amplitude mínima, sem divisão por zero)."""
    from app import dados

    zerada = entrada_diaria.copy()
    for c in ["quantidade", "quantidade_estimada", "quantidade_saida", "entregue_no_mes", "entregue_depois",
              "nao_seguiu", "em_andamento"]:
        zerada[c] = 0
    fluxo = fluxo_mensal.assign(quantidade=0)
    monkeypatch.setattr(dados.entrada, "df", lambda forcar=False: zerada)
    monkeypatch.setattr(dados.fluxo, "df", lambda forcar=False: fluxo)
    assert cliente.get("/viu-agenciamento/atendimento").status_code == 200


def test_aviso_antes_do_terceiro_mes(cliente, monkeypatch, entrada_diaria, fluxo_mensal):
    """AT-D03: carga em 15/02 (menos de 3 meses) → a faixa do ano continua e o aviso explica a ausência do quadro."""
    from app import dados

    cedo = entrada_diaria.loc[entrada_diaria["data"].astype(str) < "2026-02-15"].copy()
    cedo["_processado_em"] = pd.Timestamp("2026-02-15 12:00", tz="UTC")
    fluxo = fluxo_coerente(cedo, "2026-02-15 12:00")
    monkeypatch.setattr(dados.entrada, "df", lambda forcar=False: cedo)
    monkeypatch.setattr(dados.fluxo, "df", lambda forcar=False: fluxo)
    r = cliente.get("/viu-agenciamento/atendimento")
    assert r.status_code == 200
    assert "O quadro mês a mês e o gráfico aparecem a partir do 3º mês do ano." in r.text and "Recebidos em 2026" in r.text
