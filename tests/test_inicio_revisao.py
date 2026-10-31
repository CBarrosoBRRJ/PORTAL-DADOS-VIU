"""Página Início: correções da validação final de 23/10/2026 (B1, B2, B3, B5, B6, B7, B8), com dados sintéticos."""

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from app.apresentacoes.gestao_orcamentos.entrada import calculos as ent
from tests.conftest import com_dias
import gold_simulada  # views da gold sobre os dados sintéticos (D57)

MAI_A_SET_2026 = ["2026-05-05", "2026-06-05", "2026-07-06", "2026-08-05", "2026-09-04"]


@pytest.fixture(autouse=True)
def limpa_cache():
    ent._cache.clear()
    yield
    ent._cache.clear()


@pytest.fixture
def cliente():
    from app.main import app

    with TestClient(app) as c:
        yield c


def test_b1_tipos_no_ano_fecham_em_100_nos_dois_anos(entrada_diaria, cliente):
    """B1 (E8c/E9): parcelas por tipo no ano e no mesmo período do ano anterior pelo maior resto."""
    # números reais da carga de 23/10/2026: a soma simples dava 99 nos dois anos (53+24+7+14+1; 39+33+16+11+0)
    assert ent._pcts([2945, 1322, 407, 769, 77]) == [53, 24, 7, 14, 2]
    assert ent._pcts([1134, 955, 468, 330, 3]) == [39, 33, 16, 12, 0]
    e = ent.entrada(entrada_diaria)
    assert [g["pct"] for g in e["grupos"]] == [45, 27, 9, 14, 5] and sum(g["pct"] for g in e["grupos"]) == 100
    # 2025 até 20/10: Mercado 9, Inbound 4 (3 + 1 estimado) de 13
    assert [g["pct_anterior"] for g in e["grupos"]] == [69, 31, 0, 0, 0]
    assert ent.entrada(entrada_diaria, 2025)["grupos"][0]["pct_anterior"] is None  # sem régua (2024 começa em out)
    r = cliente.get("/viu-agenciamento")
    assert '<td class="coluna-anterior">69%</td>' in r.text and '<td class="coluna-anterior">31%</td>' in r.text


def test_b2_situacao_fecha_em_100():
    """B2 (E6): jan/26 real (241/72/60/1 de 374) somava 99 com o arredondamento simples."""
    def linhas(*ns):
        return pd.DataFrame([dict(zip(["no-mes", "depois", "nao-seguiu", "andamento"], ns))])
    assert [s["pct"] for s in ent._situacao(linhas(241, 72, 60, 1))] == [65, 19, 16, 0]
    assert [s["pct"] for s in ent._situacao(linhas(1, 1, 4, 0))] == [17, 17, 66, 0]  # _pct daria 17+17+67 = 101
    assert [s["pct"] for s in ent._situacao(linhas(0, 0, 0, 0))] == [0, 0, 0, 0]


def test_b2_todos_os_meses_e_o_ano_fecham(entrada_diaria):
    e = ent.entrada(entrada_diaria)
    assert sum(s["pct"] for s in e["situacao"]) == 100
    for m in e["meses"]:
        assert sum(s["pct"] for s in m["situacao"]) == (100 if m["total"] else 0)
        assert m["pct_no_mes"] == m["situacao"][0]["pct"]


def _fluxo(linhas):
    df = pd.DataFrame(linhas, columns=["mes_entrada", "evento", "mes_evento", "quantidade"])
    df["mes_entrada"] = pd.to_datetime(df["mes_entrada"]).dt.date
    df["mes_evento"] = pd.to_datetime(df["mes_evento"]).dt.date
    return df


def test_b3_extrato_sem_percentual_por_diferenca():
    """B3 (E7/E8c): fila de jun/26 real — demanda 717 (148 represados + 569 novos) = 479 entregues + 97 + 141.
    Por diferença, "seguem" ficava 19 (exato 19,7); pelo maior resto, 67/13/20."""
    f = ent.extrato(gold_simulada.fila_mensal(_fluxo([("2026-05-01", "entregue", "2026-06-01", 68), ("2026-05-01", "em_andamento", None, 80),
                            ("2026-06-01", "entregue", "2026-06-01", 411), ("2026-06-01", "nao_seguiu", "2026-06-01", 97),
                            ("2026-06-01", "em_andamento", None, 61)])), "2026-06")["fila"]
    assert (f["represados"], f["novos"], f["demanda"], f["entregues"], f["nao_seguiram"], f["seguem"]) == (148, 569, 717, 479, 97, 141)
    assert (f["pct_represados"], f["pct_novos"]) == (21, 79)
    assert (f["pct_entregues"], f["pct_nao_seguiram"], f["pct_seguem"]) == (67, 13, 20)
    assert (f["pct_entregues_novos"], f["pct_entregues_represados"]) == (72, 46)  # sobre novos e sobre represados (_pct)


def test_b5_mes_vazio_nao_ocupa_vaga(entrada_diaria):
    """B5 (E7): carga em 02/11/2026 (01/11 é domingo, novembro vazio): seguem 6 meses clicáveis, mai–out."""
    df = com_dias(entrada_diaria, MAI_A_SET_2026, "2026-11-02 12:00")
    e = ent.entrada(df)
    assert [m["chave"] for m in e["meses"] if m["detalhavel"]] == ["2026-05", "2026-06", "2026-07", "2026-08", "2026-09", "2026-10"]
    assert e["meses_extrato"] == ["2026-05", "2026-06", "2026-07", "2026-08", "2026-09", "2026-10"]
    nov = e["meses"][10]
    assert nov["parcial"] and nov["total"] == 0 and not nov["detalhavel"]


def test_b6_lista_de_meses_atravessa_o_ano_sem_mudar_a_tela(entrada_diaria, monkeypatch):
    """B6: em 05/01/2027 a lista de meses válidos inclui jun–out/26; a tela segue abrindo só os meses do ano mostrado
    (a forma de mostrar os do ano anterior é decisão do Caio)."""
    from app import dados
    from app.apresentacoes.gestao_orcamentos import apresentacao
    df = com_dias(entrada_diaria, MAI_A_SET_2026 + ["2027-01-04"], "2027-01-05 12:00")
    e = ent.entrada(df)
    assert e["ano"] == 2027 and e["meses_extrato"] == ["2026-06", "2026-07", "2026-08", "2026-09", "2026-10", "2027-01"]
    assert [m["chave"] for m in e["meses"] if m["detalhavel"]] == ["2027-01"]
    monkeypatch.setattr(dados.entrada, "df", lambda: df)
    assert apresentacao.montar_inicio({"mes": "2026-10"})["entrada"]["extrato"] is None  # não quebra nem abre
    assert apresentacao.montar_inicio({"mes": "2027-01"})["entrada"]["extrato_em_atualizacao"] is False


def test_b7_cargas_de_dias_diferentes_escondem_o_extrato(cliente, entrada_diaria, fluxo_mensal, monkeypatch):
    """B7 (E7): os novos de fevereiro coincidem (3 = 3), mas o fluxo é da carga da véspera: aviso, sem números."""
    from app import dados
    recente = entrada_diaria.loc[entrada_diaria["data"].astype(str) < "2026-03"].copy()
    recente["_processado_em"] = pd.Timestamp("2026-03-02 12:00", tz="UTC")
    # O fluxo sintético cobre só jan/fev: alinhar a população inteira para testar apenas a geração.
    recente = recente.loc[recente["data"].astype(str) >= "2026"].copy()
    recente.loc[recente["data"].astype(str) < "2026-02", "quantidade"] = [1, 1]
    fluxo_ontem, fluxo_hoje = fluxo_mensal.copy(), fluxo_mensal.copy()
    fluxo_ontem["_processado_em"] = pd.Timestamp("2026-03-01 12:00", tz="UTC")
    fluxo_hoje["_processado_em"] = pd.Timestamp("2026-03-02 12:30", tz="UTC")
    assert ent.data_carga(recente) == pd.Timestamp("2026-03-02").date() and ent.data_carga(fluxo_mensal) is None
    monkeypatch.setattr(dados.entrada, "df", lambda: recente)
    monkeypatch.setattr(dados.fluxo, "df", lambda: fluxo_ontem)
    r = cliente.get("/viu-agenciamento?mes=2026-02")
    assert "O extrato está sendo atualizado" in r.text and 'id="extrato-titulo"' not in r.text
    monkeypatch.setattr(dados.fluxo, "df", lambda: fluxo_hoje)
    r = cliente.get("/viu-agenciamento?mes=2026-02")
    assert "O extrato está sendo atualizado" not in r.text and 'id="extrato-titulo"' in r.text


def test_b8_periodo_na_virada_do_ano(entrada_diaria):
    """B8 (E4): a carga de 01/01 cobre até 31/12 e mostra o ano fechado; a de 31/12 ainda está em andamento."""
    fechado = ent.entrada(com_dias(entrada_diaria, [], "2027-01-01 12:00"))
    assert fechado["ano"] == 2026 and fechado["periodo"] == "de janeiro a dezembro"
    assert not any(m["parcial"] for m in fechado["meses"])
    ent._cache.clear()
    assert ent.entrada(com_dias(entrada_diaria, [], "2026-12-31 12:00"))["periodo"] == "até 30 de dezembro"
