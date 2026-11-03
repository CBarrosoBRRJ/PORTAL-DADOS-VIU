"""Previsão de demanda (D48 → D56, 26/10/2026): contrato ml/previsao.py v3 → página (P1–P12), critério de escolha (C1),
robustez (C5), séries por recorte sem repartição (D56), execução mensal (C4, job J1–J3 e ml.rodar --rotina/
--acompanhamento) e o layout (cartões de mês, gráfico de 2026, diálogo "Modelos comparados"). Tudo com o contrato
sintético de tests/conftest.py (previsao_sintetica); nada toca o BigQuery nem as bibliotecas de ML pesadas."""

import json
import re

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from app import config
from app.apresentacoes.gestao_orcamentos.previsao import calculos as C
from app.apresentacoes.gestao_orcamentos.previsao import job
from ml import previsao as mp
from tests.conftest import CARGA_PREVISAO, previsao_sintetica, series_sinteticas


@pytest.fixture
def cliente():
    from app.main import app

    with TestClient(app) as c:
        yield c


@pytest.fixture
def p():
    return previsao_sintetica()


def _m(wape, modulo="referencia", verif=None):
    return {"modulo": modulo, "series": {"Inbound": {"metricas": {"1": {"wape": wape}, "verificacao": {"wape": verif}}}}}


# ---------------------------------------------------------------- contrato e critério

def test_contrato_v3_lido_e_recusado(tmp_path, p):
    arq = tmp_path / "previsao.json"
    arq.write_text(json.dumps(p), encoding="utf-8")
    assert C.ler(arq)["retrato"]["mes_fechado"] == "2026-09"
    assert p["versao"] == 3 and p["protocolo"] == "D56"
    assert p["regua"]["janela"] == 12 and p["regua"]["teste"] == ["2026-06", "2026-09"]
    for versao in (1, 2, 99):  # contratos da D47 (v1) e da D48/D55 (v2) ou desconhecido = máscara
        arq.write_text(json.dumps({**p, "versao": versao}), encoding="utf-8")
        assert C.ler(arq) is None
    assert C.ler(tmp_path / "nao_existe.json") is None
    assert C.tela(None) is None


def test_criterio_menor_erro_com_desempate_pelo_mais_simples():
    """C1: vence o menor WAPE h1 jun–set; diferença < 1 ponto = empate → o mais simples; não se aplica e falha ficam fora."""
    modelos = {"ref_media_6m": _m(0.144), "arimax_011": _m(0.135, "arimax"), "comb_theta": _m(0.151, "combinacao"),
               "mlp_1": _m(0.10, "neural"), "prophet_log": {"modulo": "prophet", "nao_se_aplica": "24 meses"},
               "boost_lgbm": {"modulo": "boosting", "erro": "x"},
               "comb_ses": {"modulo": "combinacao", "series": {"Inbound": {"nao_se_aplica": "R7"}}}}
    e = mp.escolher(modelos, "Inbound")
    assert e["vencedor"] == "mlp_1" and e["n_modelos"] == 4  # 3,5 pontos à frente: não é empate
    modelos["mlp_1"] = _m(0.134, "neural")
    e = mp.escolher(modelos, "Inbound")
    assert e["menor"] == 0.134 and e["vencedor"] == "ref_media_6m"  # 0,134 · 0,135 · 0,144 empatam → referência
    assert set(e["empatados"]) == {"ref_media_6m", "arimax_011", "mlp_1"}
    rede = {n: _m(0.126, "neural") for n in ("mlp_4x2", "mlp_1", "mlp_auto", "mlp_8")}
    assert mp.escolher(rede, "Inbound")["vencedor"] == "mlp_1"
    assert mp.complexidade("arima_100_ct", "arimax") < mp.complexidade("arimax_100_ct", "arimax")


def test_robustez_e_alternativa():
    """C5 (D56): o vencedor que perde da ingênua fora do teste é "não robusto"; a alternativa = o menor erro no teste
    entre os que batem a ingênua nos dois períodos. Sem verificação (série curta) = robustez desconhecida."""
    modelos = {"ref_ultimo_mes": _m(0.198, verif=0.247), "mlp_1": _m(0.126, "neural", 0.268),
               "arima_100_ct": _m(0.165, "arimax", 0.204), "prophet_auto": _m(0.163, "prophet", 0.209),
               "cls_theta": _m(0.196, "classico", 0.224)}
    for m in modelos.values():
        m["futuro"] = {"Inbound": []}
    r = mp.robustez(modelos, "Inbound", "mlp_1")
    assert r["robusto"] is False and "27%" in r["texto"] and "25%" in r["texto"]
    assert r["alternativa"]["modelo"] == "arima_100_ct"  # 16,3 × 16,5: empate < 1 ponto → o mais simples (ARIMA)
    assert mp.robustez(modelos, "Inbound", "arima_100_ct")["robusto"] is True
    curto = {"ref_ultimo_mes": _m(0.13), "comb_mediana": _m(0.11, "combinacao")}
    assert mp.robustez(curto, "Inbound", "comb_mediana")["robusto"] is None


def test_vencedor_e_metricas_da_tela_iguais_as_do_contrato(p):
    """P3/P8: com as séries sintéticas lineares, a reta de 6 meses e a cópia "ARIMA" empatam (erro 0) nas longas; fica a
    referência. Nas curtas (5 a 8 meses de treino), a reta de 6 meses não se aplica (R7) e vence o último mês."""
    assert p["decisao"]["vencedor"] == {"Inbound": "ref_tendencia_6m", "Mercado": "ref_tendencia_6m",
                                        "Mercado exclusivos": "ref_ultimo_mes", "Mercado não exclusivos": "ref_ultimo_mes"}
    assert "arima_100_ct" in p["series"]["Mercado"]["empatados"]
    for grupo in ("todos", "exclusivos", "nao-exclusivos"):
        for c in C.tela(p, grupo)["colunas"]:
            if c["nao_se_aplica"]:
                continue
            regua = p["series"][c["serie"]]["metricas"]["1"]
            assert c["metricas"]["n"] == 4
            for k in ("wape", "mae"):
                assert c["metricas"][k] == pytest.approx(regua[k], abs=1e-9)


# ---------------------------------------------------------------- D56: uma série e um modelo por recorte

def test_series_por_recorte_sem_reparticao(p):
    """D56: cada série tem o seu modelo, treinado só nela — a previsão dos exclusivos do Mercado é a do vencedor na
    própria série (nada de "Mercado × parcela"); os recortes não somam o total (sem talento fica fora dos dois)."""
    from ml import regua
    from ml.modelos import referencia

    series = series_sinteticas()
    assert set(p["series"]) == {"Inbound", "Mercado", "Mercado exclusivos", "Mercado não exclusivos"}
    for nome in ("Mercado exclusivos", "Mercado não exclusivos"):
        s = p["series"][nome]
        modelo = next(m for m in referencia.MODELOS if m.nome == s["modelo"])
        proprio = regua.prever_futuro(modelo, {nome: series[nome]})[nome]
        assert [x["valor"] for x in s["futuro"]] == [x["valor"] for x in proprio]
        assert s["historico"] == {str(k): float(v) for k, v in series[nome].items()}
        assert s["curta"] and s["inicio"] == "2026-01" and s["treino_1o_teste"] == 5
        assert s["robustez"]["robusto"] is None  # sem verificação (série só de 2026)
    total = p["series"]["Mercado"]["futuro"][0]["valor"]
    partes = sum(p["series"][n]["futuro"][0]["valor"] for n in ("Mercado exclusivos", "Mercado não exclusivos"))
    assert partes != pytest.approx(total)  # nenhuma repartição força a soma
    assert "filtros" in p and not any("abordagem" in json.dumps(x) for x in p["filtros"].values())
    assert "parcela" not in json.dumps(p["series"])


def test_montar_recortes_usa_a_propria_tabela():
    """S1–S4: gold para Inbound/Mercado; silver para os exclusivos/não exclusivos do Mercado, com o `completo` da gold."""
    from ml import dados as mld

    meses = [str(m) for m in pd.period_range("2025-10", "2026-10", freq="M")]
    serie = pd.DataFrame([{"mes": m, "tipo": t, "pedidos": 100 + i, "estimados": 0, "completo": m < "2026-10",
                           "dados_ate": "2026-10-25", "processado_em": "x"}
                          for t in ("Inbound", "Mercado") for i, m in enumerate(meses)])
    excl = pd.DataFrame([{"mes": m, "tipo": t, "exclusivos": 50, "nao_exclusivos": 40, "sem_talento": 2, "total": 92}
                         for t in ("Inbound", "Mercado") for m in meses if m >= "2026-01"])
    r = mld.montar_recortes(serie, excl)
    assert set(r) == set(mld.RECORTES) == {"inbound", "mercado", "mercado_exclusivos", "mercado_nao_exclusivos"}
    assert list(r["inbound"]["pedidos"]) == list(range(100, 113)) and r["inbound"]["fonte"].iloc[0].startswith("gold")
    me = r["mercado_exclusivos"]
    assert me["mes"].iloc[0] == "2026-01" and set(me["pedidos"]) == {50} and me["fonte"].iloc[0].startswith("gold de exclusividade")
    assert list(me["completo"]) == [True] * 9 + [False]  # outubro em andamento, como na gold
    assert set(r["mercado_nao_exclusivos"]["pedidos"]) == {40}
    from ml import regua
    s, meta = regua.carregar_recortes(tabelas=r)
    assert len(s["Mercado exclusivos"]) == 9 and meta["recortes"]["Mercado exclusivos"]["curta"]
    assert meta["recortes"]["Inbound"]["treino_1o_teste"] == 8  # aqui o Inbound sintético começa em out/2025
    assert meta["parcial"]["Mercado não exclusivos"] == {"mes": "2026-10", "pedidos_ate_agora": 40.0}


def test_filtros_e_nao_exclusivos_so_mercado(p, cliente):
    """P4: Todos = Inbound | Mercado; Exclusivos = Inbound (inteiro) | Mercado exclusivos; Não exclusivos = Inbound
    "não se aplica" | Mercado não exclusivos. O Mercado fica sempre à direita."""
    series = {g: [c["serie"] for c in C.tela(p, g)["colunas"]] for g in C.GRUPOS}
    assert series == {"todos": ["Inbound", "Mercado"], "exclusivos": ["Inbound", "Mercado exclusivos"],
                      "nao-exclusivos": [None, "Mercado não exclusivos"]}
    t = C.tela(p, "nao-exclusivos")
    inbound, mercado = t["colunas"]
    assert inbound["nao_se_aplica"] and inbound["texto"] == "Não se aplica: todo Inbound é de talento exclusivo"
    assert mercado["serie"] == "Mercado não exclusivos" and len(mercado["meses"]) == 3
    assert t["dialogo"]["series"] == ["Mercado não exclusivos"]
    ex = C.tela(p, "exclusivos")["colunas"][0]
    todos = C.tela(p, "todos")["colunas"][0]
    assert ex["recorte"] == "todo o Inbound é de talento exclusivo" and ex["meses"] == todos["meses"]
    html = cliente.get("/viu-agenciamento/previsao?talentos=nao-exclusivos").text
    assert "Não se aplica: todo Inbound é de talento exclusivo" in html and "talentos não exclusivos" in html
    assert html.count('class="pv-coluna pv-coluna-nao-aplica"') == 1 and html.count("pv-svg-largo") == 1
    assert re.search(r'href="\?talentos=nao-exclusivos#1" class="grupo" aria-current="true"', html)
    from app.apresentacoes.gestao_orcamentos.pendencias import PENDENCIAS
    assert any(x.codigo == "PD24" for x in PENDENCIAS)
    q = p["qualidade"]["nao_exclusivo_no_inbound"]["Inbound"]
    assert q["pendencia"] == "PD24" and q["fechados"] == 6 * 9 and q["parcial"] == 6


# ---------------------------------------------------------------- cartões de mês (P10, P11)

def test_mes_vigente_e_os_dois_seguintes_a_partir_da_carga(p):
    """P10: sempre o mês vigente (o do dia seguinte a dados_ate) + os 2 seguintes; sem previsão no retrato = aguardando."""
    assert C.meses_dos_cartoes("2026-10-20") == ["2026-10", "2026-11", "2026-12"]
    assert C.meses_dos_cartoes("2026-10-31") == ["2026-11", "2026-12", "2027-01"]  # outubro fechou na carga de 01/11
    assert C.meses_dos_cartoes(pd.Timestamp("2026-12-31")) == ["2027-01", "2027-02", "2027-03"]
    c = C.tela(p)["colunas"][1]
    out, nov, dez = c["meses"]
    assert out["vigente"] and out["mes"] == "2026-10" and out["realizado"] == 190
    assert out["valor"] == p["series"]["Mercado"]["futuro"][0]["valor"]  # previsão de fechamento do retrato
    assert not nov["vigente"] and nov["p10"] is not None and dez["mes"] == "2026-12"
    novo = {**p, "carga": {**p["carga"], "dados_ate": "2026-10-31"}}
    meses = C.tela(novo)["colunas"][0]["meses"]
    assert [m["mes"] for m in meses] == ["2026-11", "2026-12", "2027-01"]
    assert meses[2]["sem_previsao"] and meses[0]["realizado"] is None  # o acompanhamento ainda é de outubro


def test_situacao_do_mes_vigente():
    """P10: esperado até agora = previsão × dias úteis decorridos ÷ do mês; fora da faixa proporcional = abaixo/acima."""
    x = {"valor": 210.0, "p10": 168.0, "p90": 252.0}
    s = C.situacao(70, x, 10, 21)
    assert s["esperado"] == pytest.approx(100) and s["delta"] == pytest.approx(-0.3) and s["lugar"] == "abaixo"
    assert C.situacao(100, x, 10, 21)["lugar"] == "dentro"
    assert C.situacao(130, x, 10, 21)["lugar"] == "acima" and C.situacao(130, x, 10, 21)["sentido"] == "alta"
    sem_faixa = {"valor": 210.0}
    assert C.situacao(95, sem_faixa, 10, 21)["lugar"] == "dentro" and C.situacao(85, sem_faixa, 10, 21)["lugar"] == "abaixo"
    assert C.situacao(50, None, 10, 21) is None and C.situacao(50, x, 0, 0) is None


def test_por_que_do_mes_fora_da_faixa(p, cliente):
    """P11: o vigente fora da faixa traz o diagnóstico de lotes e avulsos; os recortes de exclusividade dizem quantos
    pedidos do mês ainda estão sem talento (fora dos dois)."""
    c = C.tela(p, "exclusivos")["colunas"][1]
    assert c["meses"][0]["situacao"]["lugar"] == "abaixo"
    assert c["por_que"] == "Até o dia 20: 10 pedidos em lote (média de jun–set: 36) e 50 avulsos (83)"
    assert c["sem_talento"] == 190 - 60 - 87
    assert C.tela(p, "todos")["colunas"][1]["sem_talento"] is None  # o total do Mercado não tem esse recorte
    html = cliente.get("/viu-agenciamento/previsao?talentos=exclusivos").text
    assert "Por quê" in html and "33% abaixo do esperado" in html.replace(" ", " ")
    assert "43 pedidos do Mercado em outubro ainda sem talento informado" in html


# ---------------------------------------------------------------- gráfico, tela e diálogo

def test_eixo_so_2026_com_teste_e_previsao(p):
    """P7: eixo fixo jan–dez/2026 (nada de 2024/2025); real até set; teste jun–set (vazio); out em andamento; out–dez."""
    t = C.tela(p)
    for c in t["colunas"]:
        for g in (c["grafico"], c["grafico_xl"], c["grafico_estreito"]):
            assert [r["t"] for r in g["rotulos"]] == ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]
            reais = [b for b in g["colunas"] if b["classe"] == "pv-real"]
            assert len(reais) == 9 and all("/2026" in b["dica"] for b in g["colunas"])
            assert len([b for b in g["colunas"] if b["classe"] == "pv-real-parcial"]) == 1
            assert len([x for x in g["pontos"] if x["classe"] == "pv-prev"]) == 4
            assert len([x for x in g["pontos"] if x["classe"] == "pv-fut"]) == 3
            assert [z["t"] for z in g["zonas"]] == ["teste", "previsão"]
            for b in g["colunas"]:
                assert g["topo_y"] - 0.5 <= b["y"] and b["y"] + b["h"] == pytest.approx(g["base"], abs=0.2)
    assert len({(c["grafico"]["w"], c["grafico_xl"]["w"], c["grafico_estreito"]["w"]) for c in t["colunas"]}) == 1
    assert all(g["virada"] is None for c in t["colunas"] for g in (c["grafico"], c["grafico_estreito"]))


def test_eixo_vai_ate_jan_27_quando_a_previsao_passa_de_dezembro(p):
    """P7 (03/11/2026): com o retrato de outubro, o horizonte de 3 meses chega a jan/27; o gráfico e a tabela do leitor
    de tela vão até ele (antes só o cartão mostrava), com a virada de ano tracejada, a zona "previsão" inteira e o ano
    nas dicas; no gráfico estreito o rótulo fica "jan" (sem espaço para "jan/27")."""
    for s in p["series"].values():
        ultimo = s["futuro"][-1]
        s["futuro"].append({**ultimo, "mes": "2027-01", "valor": ultimo["valor"] + 1})
    assert C.meses_do_eixo([{"mes": "2027-01"}])[-2:] == ["2026-12", "2027-01"] and len(C.meses_do_eixo(None)) == 12
    for c in C.tela(p)["colunas"]:
        if c["nao_se_aplica"]:
            continue
        largo, estreito = c["grafico"], c["grafico_estreito"]
        assert [r["t"] for r in largo["rotulos"]][-2:] == ["dez", "jan/27"]
        assert [r["t"] for r in estreito["rotulos"]][-2:] == ["dez", "jan"]
        for g in (largo, estreito, c["grafico_xl"]):
            assert len(g["rotulos"]) == 13 and g["dir"] == g["w"] - C.DIR
            assert len([x for x in g["pontos"] if x["classe"] == "pv-fut"]) == 4
            assert [z["t"] for z in g["zonas"]] == ["teste", "previsão"]
            assert g["rotulos"][-2]["x"] < g["virada"] < g["rotulos"][-1]["x"]
            assert any(x["dica"].startswith("jan/2027: previsão") for x in g["pontos"])
        assert c["acessivel"][-1]["mes"] == "jan/2027" and c["acessivel"][-1]["futuro"]["mes"] == "2027-01"
        assert c["acessivel"][0]["mes"] == "jan/2026" and len(c["acessivel"]) == 13


def test_pagina_previsao(cliente):
    r = cliente.get("/viu-agenciamento/previsao")
    assert r.status_code == 200 and "Aguardando dados" not in r.text
    html = r.text
    assert 'id="pv-t-inbound"' in html and 'id="pv-t-mercado"' in html
    assert "erro médio" in html and "em jun–set" in html and "fora do teste (jan–mai)" in html
    assert html.count('class="pv-mes pv-mes-vigente"') == 2 and html.count('class="pv-mes"') == 4
    assert "<details" not in html and "Regras e modelos" not in html and "Vale mais que o palpite simples?" not in html
    assert 'href="?talentos=exclusivos#1"' in html and 'aria-current="true"' in html
    assert "grupo-valor" not in html and "explora-conclusoes" not in html
    assert "2024" not in html  # gráfico e cartões só de 2026
    assert html.count('<div class="so-leitor"><table>') == 2  # valores de cada gráfico para o leitor de tela
    assert 'style="' not in html  # CSP: sem style=""
    assert "<script>" not in html.replace('<script src=', '')  # CSP: nada de script inline
    assert "Dados até" in html  # rodapé datado
    assert "Modelo: Reta dos últimos 6 meses" in html and "repetir o último mês erraria" in html


def test_dialogo_modelos_comparados_acessivel(p, cliente):
    """P12: <dialog> nativo com nome e descrição, aberto por um botão (invoker command + JS de reserva), fechado por um
    <form method="dialog"> com botão nomeado e com foco inicial; todos os modelos das séries do filtro, por família;
    vencedor marcado com ícone + texto para leitor de tela; "não se aplica" com o motivo."""
    html = cliente.get("/viu-agenciamento/previsao?talentos=exclusivos").text
    assert re.search(r'<button type="button" class="pv-modelos-botao" data-dialogo="pv-dialogo" commandfor="pv-dialogo" '
                     r'command="show-modal" aria-haspopup="dialog">', html)
    assert '<dialog id="pv-dialogo" class="pv-dialogo" aria-labelledby="pv-dialogo-titulo" aria-describedby="pv-dialogo-sub">' in html
    assert '<form method="dialog"' in html and re.search(r'<button class="pv-fechar" value="fechar" autofocus>.*?Fechar', html, re.DOTALL)
    assert html.count("<dialog") == 1 and 'role="region"' in html and 'tabindex="0"' in html
    d = C.tela(p, "exclusivos")["dialogo"]
    assert d["series"] == ["Inbound", "Mercado exclusivos"]
    nomes = {ln["nome"] for f in d["familias"] for ln in f["linhas"]}
    sem = sum(f["sem"]["n"] for f in d["familias"] if f["sem"])
    assert len(nomes) + sem == len(p["modelos"])  # todos os modelos do contrato aparecem (com resultado ou "não se aplica")
    venc = [(ln["nome"], i) for f in d["familias"] for ln in f["linhas"] for i, c in enumerate(ln["celulas"]) if c["vencedor"]]
    assert sorted(venc) == [("ref_tendencia_6m", 0), ("ref_ultimo_mes", 1)]
    media6 = next(ln for f in d["familias"] for ln in f["linhas"] if ln["nome"] == "ref_media_6m")
    assert media6["celulas"][1]["falta"] == "não se aplica" and "meses de treino" in media6["celulas"][1]["motivo"]
    assert "vencedor: </span>" in html and "não se aplica" in html
    js = (config.RAIZ / "app" / "static" / "apresentacao.js").read_text(encoding="utf-8")
    assert "showModal()" in js and '"command" in HTMLButtonElement.prototype' in js and "botao.focus()" in js


def test_sem_previsao_mostra_mascara(cliente, monkeypatch, tmp_path):
    monkeypatch.setattr(config, "PREVISAO_ARQ", tmp_path / "nao_existe.json")
    r = cliente.get("/viu-agenciamento/previsao")
    assert r.status_code == 200 and "Aguardando dados" in r.text and "PD09" in r.text


def test_css_da_previsao_junto_e_em_crlf():
    """CLAUDE.md: estilo.css em CRLF; as regras da Previsão num bloco só (D56), antes do bloco de movimento do portal."""
    b = (config.RAIZ / "app" / "static" / "estilo.css").read_bytes()
    assert b.count(b"\n") == b.count(b"\r\n")
    s = b.decode("utf-8")
    ini, fim = s.index("Previsão de demanda (D56"), s.index("movimento do portal (batalha 2")
    assert ini < fim and s.count(".pv-dialogo { width: min(") == 1 and s.index(".pv-dialogo {") < fim
    assert ".pv-" not in s[fim:] and ".pv-" not in s[:ini]  # nenhuma regra da Previsão fora do bloco (nem no fim)


# ---------------------------------------------------------------- execução mensal

def test_job_decide_rotina_mensal_ou_acompanhamento(p):
    """J1/C4: mês fechado novo → rotina; mesmo mês e carga nova → só o acompanhamento; mesma carga → nada."""
    assert job.mes_fechado(pd.Timestamp("2026-10-22")) == "2026-09"
    assert job.mes_fechado(pd.Timestamp("2026-10-31")) == "2026-10"
    assert job.acao(None, "2026-10-24 09:00+00:00", "2026-10-23") == "rotina"
    assert job.acao(p, "2026-11-01 09:00+00:00", "2026-10-31") == "rotina"
    assert job.acao(p, "2026-10-24 09:00+00:00", "2026-10-23") == "acompanhamento"
    assert job.acao(p, CARGA_PREVISAO.replace("+00:00", "Z"), "2026-10-20") is None
    assert job.acao(p, None, None) is None


def test_job_dispara_o_comando_certo(monkeypatch, tmp_path):
    """J2/J3: desligado nos testes; ligado, chama ml.rodar com --rotina ou --acompanhamento; espera e trava seguram."""
    assert not job.disponivel()  # PREVISAO_JOB=off (conftest)
    assert not job.disparar("rotina")
    chamadas = []

    class Falso:
        pid = 1

        def __init__(self, *a, **kw):
            chamadas.append(a[0])

        def poll(self):
            return 0  # terminou

    monkeypatch.setattr(job, "disponivel", lambda: True)
    monkeypatch.setattr(job, "_pasta_ml", lambda: tmp_path / "ml")
    monkeypatch.setattr(job.subprocess, "Popen", Falso)
    monkeypatch.setattr(job, "_ultimo_disparo", 0.0)
    assert not job.disparar(None)
    assert job.disparar("acompanhamento") and chamadas[-1][-3:] == ["-m", "ml.rodar", "--acompanhamento"]
    assert not job.disparar("rotina")  # ESPERA_MIN
    monkeypatch.setattr(job, "_ultimo_disparo", 0.0)
    assert job.disparar("rotina") and chamadas[-1][-1] == "--rotina"
    monkeypatch.setattr(job, "_ultimo_disparo", 0.0)
    (tmp_path / "ml" / "saida" / "rotina.lock").write_text("1", encoding="utf-8")
    assert not job.disparar("rotina")  # trava da rotina em curso


def test_rotina_com_retrato_do_mes_so_atualiza_o_acompanhamento(monkeypatch, tmp_path):
    """C4: se o último mês fechado já tem retrato, a rotina não roda modelo nenhum."""
    from ml import rodar

    meses = pd.period_range("2025-10", "2026-09", freq="M")
    series = {t: pd.Series([50.0] * 12, index=meses, name=t) for t in C.TIPOS}
    monkeypatch.setattr(rodar, "TRAVA", tmp_path / "rotina.lock")
    monkeypatch.setattr(rodar.regua, "carregar_recortes", lambda: (series, {"mes_fechado": "2026-09", "processado_em": "x"}))
    monkeypatch.setattr(rodar.previsao, "retrato_existe", lambda mes: mes == "2026-09")
    feito = []
    monkeypatch.setattr(rodar.previsao, "atualizar_acompanhamento", lambda: feito.append("acompanhamento") or True)
    monkeypatch.setattr(rodar, "rodar_modulo", lambda *a, **k: feito.append("modelo"))
    assert rodar.rotina(extrair=False) == "acompanhamento" and feito == ["acompanhamento"]
    assert not (tmp_path / "rotina.lock").exists()


def test_acompanhamento_nao_mexe_na_previsao(tmp_path, p):
    """C4: o acompanhamento troca só o realizado do mês em andamento (por série); a previsão do retrato fica igual."""
    arq = tmp_path / "previsao.json"
    arq.write_text(json.dumps(p), encoding="utf-8")
    linhas = [{"mes": str(m), "tipo": t, "pedidos": 100, "estimados": 0, "completo": m < pd.Period("2026-10", "M"),
               "dados_ate": "2026-10-24", "processado_em": "2026-10-25 20:00:00+00:00"}
              for t in C.TIPOS for m in pd.period_range("2025-10", "2026-10", freq="M")]
    excl = pd.DataFrame([{"mes": str(m), "tipo": t, "exclusivos": 60, "nao_exclusivos": 30, "sem_talento": 10, "total": 100}
                         for t in C.TIPOS for m in pd.period_range("2026-01", "2026-10", freq="M")])
    assert mp.atualizar_acompanhamento(arq, pd.DataFrame(linhas), excl, lotes=pd.DataFrame())
    novo = json.loads(arq.read_text(encoding="utf-8"))
    ac = novo["acompanhamento"]
    assert ac["ate"] == "2026-10-24" and ac["pedidos"] == {"Inbound": 100, "Mercado": 100, "Mercado exclusivos": 60,
                                                             "Mercado não exclusivos": 30}
    assert ac["sem_talento"] == {"Inbound": 10, "Mercado": 10} and ac["lotes"] == {}
    assert novo["series"] == p["series"] and novo["retrato"] == p["retrato"]
    linhas = [{**x, "completo": True} for x in linhas]  # outubro fechou: é hora de um retrato novo, não de acompanhar
    assert not mp.atualizar_acompanhamento(arq, pd.DataFrame(linhas), excl, lotes=pd.DataFrame())


def test_rotulo_do_holt_amortecido_simples():
    """03/11/2026: comb_holt_amort é Holt com tendência amortecida (ml/modelos/combinacao.py), não "Holt simples";
    o rótulo vem de ml/previsao.py e foi trocado também no previsao.json publicado (sem rodar os modelos)."""
    assert mp.ROTULO["comb_holt_amort"] == "Holt amortecido simples"
    assert mp.ROTULO["comb_holt_amort"] != mp.ROTULO["cls_holt_amortecido"]  # o clássico segue "Holt amortecido"
    publicado = mp.PREVISAO.read_text(encoding="utf-8") if mp.PREVISAO.exists() else ""
    assert "Holt simples" not in publicado


def test_lotes_usa_o_mes_do_acompanhamento():
    """S6 (correção de 03/11/2026): o vigente do diagnóstico de lotes é o mês do acompanhamento, não o último mês
    presente na base; série sem linha desse mês (ou sem mês anterior) fica sem diagnóstico, e mês posterior não entra
    na média."""
    carga = "2026-11-03 12:00:00+00:00"

    def linha(recorte, mes, pedidos, em_lote):
        return {"recorte": recorte, "mes": mes, "ate_dia": 2, "pedidos": pedidos, "em_lote": em_lote,
                "avulsos": pedidos - em_lote, "processado_em": carga, "dados_ate": "2026-11-02"}

    lotes = pd.DataFrame([
        linha("inbound", "2026-09", 12, 0), linha("inbound", "2026-10", 9, 0), linha("inbound", "2026-11", 4, 0),
        linha("mercado", "2026-09", 50, 30), linha("mercado", "2026-10", 20, 6),  # sem novembro: o caso de 03/11
        linha("mercado_exclusivos", "2026-11", 3, 1),  # só o mês do acompanhamento: sem anteriores
    ])
    d = mp._lotes(lotes, carga, "2026-11")
    assert set(d) == {"Inbound"}
    assert d["Inbound"]["mes"] == "2026-11" and d["Inbound"]["vigente"]["pedidos"] == 4
    assert d["Inbound"]["meses_anteriores"] == ["2026-09", "2026-10"] and d["Inbound"]["media_anteriores"]["pedidos"] == 10.5
    # num mês anterior, os meses posteriores a ele não contam como "anteriores"
    out = mp._lotes(lotes, carga, "2026-10")
    assert out["Mercado"]["mes"] == "2026-10" and out["Mercado"]["meses_anteriores"] == ["2026-09"]
    assert out["Inbound"]["meses_anteriores"] == ["2026-09"] and out["Inbound"]["vigente"]["pedidos"] == 9
    assert mp._lotes(lotes, "outra carga", "2026-11") == {} and mp._lotes(None, carga, "2026-11") == {}


def test_registro_uma_vez_por_retrato_e_protocolo(tmp_path, p):
    """P7 (PD09): uma linha por retrato e protocolo; a mudança de método (D56) entra como linha nova do mesmo retrato,
    com `substitui`, sem apagar a da D48."""
    arq = tmp_path / "historico.jsonl"
    antiga = {"retrato": "2026-09", "protocolo": "D48", "carga": "x", "previsao": {}}
    arq.write_text(json.dumps(antiga) + "\n", encoding="utf-8")
    assert mp.registrar(p, arq) and not mp.registrar(p, arq)
    linhas = [json.loads(x) for x in arq.read_text(encoding="utf-8").splitlines()]
    assert len(linhas) == 2 and linhas[0] == antiga
    d = linhas[1]
    assert d["retrato"] == "2026-09" and d["protocolo"] == "D56" and d["substitui"] == "D48" and "por recorte" in d["metodo"]
    assert set(d["previsao"]) == set(p["series"]) and d["previsao"]["Mercado exclusivos"]["curta"]


def test_rodar_modulo_guarda_a_carga_de_cada_modelo(tmp_path):
    """ml.rodar: rodar só alguns modelos mantém os outros com a carga em que foram medidos (P5 do contrato)."""
    from ml import rodar

    meses = pd.period_range("2024-10", "2026-09", freq="M")
    series = {t: pd.Series([50.0 + i for i in range(24)], index=meses, name=t) for t in C.TIPOS}
    rodar.rodar_modulo("referencia", None, series, {"processado_em": "A"}, pasta=tmp_path)
    d = rodar.rodar_modulo("referencia", {"ref_media_3m"}, series, {"processado_em": "B"}, pasta=tmp_path)
    assert d["modelos"]["ref_media_3m"]["carga"] == "B" and d["modelos"]["ref_ultimo_mes"]["carga"] == "A"
    assert d["protocolo"] == "D56"
