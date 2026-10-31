"""Qualidade dos dados (Q1–Q6, A1–A5) e entrada mensal, com dados sintéticos (a previsão de demanda, D47, está em
test_previsao_pagina.py)."""

import pandas as pd
import pytest

from app.apresentacoes.gestao_orcamentos.qualidade import calculos as qual
from tests.conftest import _passos
import gold_simulada  # views da gold sobre os dados sintéticos (D57)

EM_DIA = {"estado": "em_dia", "tabela": "teste.gld"}


@pytest.fixture(autouse=True)
def limpa_cache():
    qual._cache.clear()
    yield
    qual._cache.clear()


@pytest.fixture
def com_p7(movimentos):
    """P7: vai ao cliente 2 minutos depois de entrar (A1), volta para Entrada (A3), sem talento (A5)."""
    E, C = "equipe", "cliente"
    p7 = _passos("P7", None, [("Entrada", E, "2026-05-04 10:00", "2026-05-04 10:02"),
                              ("Aguardando Feedback", C, "2026-05-04 10:02", "2026-05-05 10:00"),
                              ("Entrada", E, "2026-05-05 10:00", "2026-05-05 11:00"),
                              ("Aguardando Feedback", C, "2026-05-05 11:00", None)])
    return pd.concat([movimentos, pd.DataFrame(p7)], ignore_index=True)


def _por_id(itens):
    return {i["id"]: i for i in itens}


def test_integridade_ok_nos_dados_sinteticos(com_p7):
    q = qual.qualidade(com_p7, EM_DIA)
    assert q["integridade_ok"] == len(q["integridade"]) == 6
    assert q["projetos"] == 7 and q["passos"] == len(com_p7)


def test_integridade_aponta_falhas(com_p7):
    quebrado = com_p7.copy()
    quebrado.loc[0, "saida"] = quebrado.loc[0, "entrada"] - pd.Timedelta(hours=1)  # Q4
    quebrado.loc[1, "saida"] = pd.NaT  # Q5: passo do meio sem saída
    q = _por_id(qual.qualidade(quebrado, {"estado": "base_atrasada", "tabela": "t"})["integridade"])
    assert not q["Q1"]["ok"] and q["Q4"]["n"] == 1 and q["Q5"]["n"] == 1
    assert q["Q2"]["ok"] and q["Q3"]["ok"] and q["Q6"]["ok"]


def test_pontos_de_atencao(com_p7):
    a = _por_id(qual.qualidade(com_p7, EM_DIA)["atencao"])
    assert a["A1"]["n"] == 1  # P7: 2 minutos
    assert a["A2"]["n"] == 0  # maior calendário: P3, 92 h
    assert a["A3"]["n"] == 1 and a["A3"]["unidade"] == "voltas em 1 projeto"
    # processado 21/10 18:16 (Brasília): P2 (04/03), P3 (10/03), P5 (06/04), P7 (05/05) passam de 30 dias; P6 (06/10) não
    assert a["A4"]["n"] == 4
    assert a["A5"]["n"] == 2  # P5 e P7


def test_entrada_mensal_por_tipo(entrada_diaria, fluxo_mensal, base_um):
    from app.apresentacoes.gestao_orcamentos.entrada import calculos as ent
    ent._cache.clear()
    e = ent.entrada(entrada_diaria)
    assert e["ano"] == 2026 and e["anos"] == [2025, 2026] and e["total"] == 22
    jan, fev, out = e["meses"][0], e["meses"][1], e["meses"][9]
    assert jan["total"] == 16 and {g["nome"]: g["n"] for g in jan["grupos"]}["Inbound"] == 6  # E1: família conta
    assert {g["nome"]: g["n"] for g in fev["grupos"]}["Sem tipo"] == 1  # E2: "Outros" cai em Sem tipo
    assert out["parcial"] and not out["futuro"] and e["meses"][10]["futuro"]  # E3
    assert sum(g["pct"] for g in jan["grupos"]) == 100
    tipos = {g["nome"]: g["tipos"] for g in e["grupos"]}  # E5
    assert tipos["Internos"] == [{"nome": "ViU", "n": 3}] and tipos["Sem tipo"] == [{"nome": "Novo", "n": 1}]
    assert tipos["Mercado"] == [{"nome": "Mercado", "n": 10}]
    e25 = ent.entrada(entrada_diaria, 2025)
    assert e["periodo"] == "até 20 de outubro"  # E4: o dia é o último da tabela; o ano está no título
    sit = {g["classe"]: g["n"] for g in e["situacao"]}  # E6
    assert sit == {"no-mes": 16, "depois": 2, "nao-seguiu": 1, "andamento": 3} and sum(sit.values()) == e["total"]
    assert jan["pct_no_mes"] == 81  # 13 de 16
    # E8 por tipo (dica dos novos): o mesmo mês do ano anterior por tipo soma o total do mês anterior
    assert sum(g["n_anterior"] for g in jan["grupos"]) == jan["anterior"]["total"]
    for g in jan["grupos"]:  # E8b (base mínima 1 neste teste): variação = mês ÷ mesmo mês do ano anterior − 1
        if g["n_anterior"]:
            assert g["variacao_mes"] == pytest.approx(g["n"] / g["n_anterior"] - 1)
    assert sum(g["pct_anterior"] for g in jan["grupos"]) == 100  # E8c: parcelas do mês anterior fecham em 100
    # E8: 2025 cobre desde janeiro → compara; mesmo período = até 20/10/2025: 5 + 3 + 1 estimado + 4 = 13
    assert e["comparacao"] == {"total": 13, "variacao": 22 / 13 - 1} and e["ano_anterior"] == 2025
    assert jan["anterior"] == {"total": 5, "variacao": 16 / 5 - 1}
    assert out["anterior"] == {"total": 4, "variacao": 3 / 4 - 1}  # mês parcial: 2025 até o mesmo dia
    assert fev["anterior"] is None  # fev/2025 sem pedidos: não há régua
    assert e25["comparacao"] is None and all(m["anterior"] is None for m in e25["meses"])  # 2024 começa em outubro
    x = ent.extrato(gold_simulada.fila_mensal(fluxo_mensal), "2026-02")  # E7
    assert x["nome"] == "Fevereiro de 2026" and x["entraram"] == 3
    # E7 (fila de fevereiro): represados no início = 1 (jan, entregue em fev); o "não seguiu" de jan sem data fica fora.
    # Demanda 1 + 3 = 4 = entregues 3 (2 novos + 1 represado) + não seguiram 0 + seguem 1 (fev entregue em março)
    f = x["fila"]
    assert (f["represados"], f["novos"], f["demanda"]) == (1, 3, 4)
    assert (f["entregues"], f["entregues_novos"], f["entregues_represados"], f["nao_seguiram"], f["seguem"]) == (3, 2, 1, 0, 1)
    assert f["demanda"] == f["entregues"] + f["nao_seguiram"] + f["seguem"]  # a conta sempre fecha
    assert (f["pct_represados"], f["pct_novos"]) == (25, 75)
    assert (f["pct_entregues"], f["pct_nao_seguiram"], f["pct_seguem"]) == (75, 0, 25)  # somam 100
    assert (f["pct_entregues_novos"], f["pct_entregues_represados"]) == (67, 100)  # sobre novos e sobre represados
    # dicas por mês de entrada: início = entregues + não seguiram + seguem; os totais batem com a caixa
    assert sum(m["entregues"] for m in f["seguem_meses"]) == f["entregues"]
    assert sum(m["nao_seguiram"] for m in f["seguem_meses"]) == f["nao_seguiram"]
    assert sum(m["seguem"] for m in f["seguem_meses"]) == f["seguem"]
    assert sum(m["inicio"] for m in f["seguem_meses"]) == f["demanda"]
    assert f["represados_meses"] == [{"mes": "2026-01", "nome": "Janeiro", "novo": False, "inicio": 1, "entregues": 1, "nao_seguiram": 0, "seguem": 0}]
    assert f["seguem_meses"] == [{"mes": "2026-02", "nome": "Fevereiro", "novo": True, "inicio": 3, "entregues": 2, "nao_seguiram": 0, "seguem": 1}] + f["represados_meses"]
    assert x["entregas"]["total"] == 3
    assert x["entregas"]["anteriores"] == [{"mes": "2026-01", "nome": "Janeiro de 2026", "n": 1}]
    # os represados no fim de fevereiro são os do início de março
    assert ent.extrato(gold_simulada.fila_mensal(fluxo_mensal), "2026-03") is None  # março sem novos pedidos: sem extrato
    assert ent.extrato(gold_simulada.fila_mensal(fluxo_mensal), "2026-05") is None
    assert ent.entrada(entrada_diaria, 2025)["periodo"] == "de janeiro a dezembro"
    assert e25["total"] == 20 and e25["meses"][2]["estimados"] == 1


def test_extratos_janela_global_de_seis_meses(entrada_diaria):
    from app.apresentacoes.gestao_orcamentos.entrada import calculos as ent
    from tests.conftest import com_dias
    # Janeiro: o semestre móvel atravessa o ano e só conta meses com pedidos (dez/2025 vazio não ocupa vaga, B5).
    df = com_dias(entrada_diaria, ["2025-04-07", "2025-05-07", "2025-06-06", "2025-07-07", "2025-08-07", "2025-09-08"],
                  "2026-01-25 12:00")
    df = df.loc[df["data"].astype(str) <= "2026-01-24"].copy()
    ent._cache.clear()
    anterior = ent.entrada(df, 2025)
    assert [m["chave"] for m in anterior["meses"] if m["detalhavel"]] == ["2025-07", "2025-08", "2025-09", "2025-10", "2025-11"]
    atual = ent.entrada(df, 2026)
    assert atual["meses"][0]["detalhavel"]
    assert atual["meses_extrato"] == ["2025-07", "2025-08", "2025-09", "2025-10", "2025-11", "2026-01"]
    assert "até 24 de janeiro" in atual["periodo"]  # último evento foi em 20/01
    assert anterior["total"] == 26  # histórico e totais anuais preservados (20 + 6 do semestre)


def test_origens_das_entregas_mantem_mes_e_ano(fluxo_mensal):
    from app.apresentacoes.gestao_orcamentos.entrada import calculos as ent
    antigos = fluxo_mensal.iloc[[2, 2]].copy()
    antigos["mes_entrada"] = [pd.Timestamp("2025-01-01").date(), pd.Timestamp("2025-12-01").date()]
    antigos["quantidade"] = [4, 7]
    x = ent.extrato(gold_simulada.fila_mensal(pd.concat([fluxo_mensal, antigos], ignore_index=True)), "2026-02")
    assert x["entregas"]["total"] == 14
    assert x["fila"]["entregues_represados"] == 1  # só jan/2026: a fila conta pedidos do próprio ano
    assert x["fila"]["entregues_anos_anteriores"] == 11  # dez/2025 (7) + jan/2025 (4), fora da conta
    # pedidos de 2025 nunca entram na fila: represados, entregues, seguem e as dicas só têm 2026
    f = x["fila"]
    assert f["represados"] == 1 and f["entregues"] == 3 and f["demanda"] == f["entregues"] + f["nao_seguiram"] + f["seguem"]
    assert all(m["mes"].startswith("2026") for m in f["represados_meses"] + f["seguem_meses"] + f["entregues_represados_meses"])
    pendente_2025 = fluxo_mensal.iloc[[3]].copy()  # um pedido de 2025 ainda em andamento
    pendente_2025["mes_entrada"], pendente_2025["evento"], pendente_2025["quantidade"] = pd.Timestamp("2025-11-01").date(), "em_andamento", 50
    y = ent.extrato(gold_simulada.fila_mensal(pd.concat([fluxo_mensal, pendente_2025], ignore_index=True)), "2026-02")
    assert y["fila"]["represados"] == 1 and y["fila"]["seguem"] == 1  # os 50 de 2025 não contam
    assert [(a["mes"], a["n"]) for a in x["entregas"]["anteriores"]] == [("2026-01", 1), ("2025-12", 7), ("2025-01", 4)]
    assert x["fila"]["pct_entregues"] + x["fila"]["pct_nao_seguiram"] + x["fila"]["pct_seguem"] == 100


def test_parcelas_fecham_em_100_e_base_minima():
    """E8c: maior resto (set/26 real soma 101 com arredondamento simples); _pct meio para cima; E8b: base mínima 30."""
    from app.apresentacoes.gestao_orcamentos.entrada import calculos as ent
    assert ent._pcts([477, 129, 29, 93, 5]) == [65, 17, 4, 13, 1]  # set/26: round() daria 65+18+4+13+1 = 101
    assert ent._pcts([227, 94, 31, 42, 1]) == [57, 24, 8, 11, 0] and sum(ent._pcts([1, 1, 1])) == 100
    assert ent._pcts([0, 0]) == [0, 0]
    assert ent._pct(1, 8) == 13 and ent._pct(5, 8) == 63 and ent._pct(1, 0) == 0  # 12,5 → 13; 62,5 → 63 (round: 12, 62)
    assert ent.BASE_MINIMA_VARIACAO == 30
    assert ent.variar(40, 29) is None and ent.variar(45, 30) == pytest.approx(0.5)


def test_mes_parcial_por_tipo_ignora_dias_depois_do_limite(entrada_diaria, base_um):
    """E8: no mês em andamento, o ano anterior por tipo só conta até o mesmo dia; a dica recebe "até DD/MM"."""
    from app.apresentacoes.gestao_orcamentos.entrada import calculos as ent
    out = ent.entrada(entrada_diaria)["meses"][9]
    assert out["parcial"] and out["ate"] == "20/10"
    assert sum(g["n_anterior"] for g in out["grupos"]) == out["anterior"]["total"] == 4
    assert all(m["ate"] is None for m in ent.entrada(entrada_diaria)["meses"] if not m["parcial"])
