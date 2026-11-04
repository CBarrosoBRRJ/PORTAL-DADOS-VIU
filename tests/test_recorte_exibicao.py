"""D68 (Caio, 03/11/2026; o gerente quer sempre o mês fechado): recorte de EXIBIÇÃO do mês fechado.

As telas de dados mostram só até o último dia do mês anterior ao fim da carga (fim 02/11 → 31/10; fim no último dia do
mês → ele mesmo); a situação de cada pedido continua a da carga. RECORTE_EXIBICAO=off volta ao comportamento E3. Os
testes antigos rodam com "off" (conftest); aqui cada teste liga o recorte com `mes_fechado` (fixture `recorte`).
Dados sintéticos de tests/conftest.py: a entrada vai até 20/10/2026 (sem `_processado_em`) e o SLA foi processado em
21/10/2026 (fim 20/10), então, sem dados extras, o recorte mostra até 30/09/2026.
"""

import importlib
from datetime import date, datetime

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from app import config, corte, dados, formato, sla
from app.apresentacoes.gestao_orcamentos import apresentacao as ap
from app.apresentacoes.gestao_orcamentos.atendimento import calculos as atendimento
from app.apresentacoes.gestao_orcamentos.entrada import calculos as entrada
from app.apresentacoes.gestao_orcamentos.previsao import calculos as previsao
from app.apresentacoes.gestao_orcamentos.sla import calculos as calc_sla
from app.apresentacoes.gestao_orcamentos.talentos import calculos as tal
from tests.conftest import com_dias, previsao_sintetica


@pytest.fixture
def recorte(monkeypatch):
    """Liga o recorte do mês fechado (o padrão de produção) só neste teste; caches limpos antes e depois."""
    ap.limpar_caches()
    monkeypatch.setattr(config, "RECORTE_EXIBICAO", "mes_fechado")
    yield
    ap.limpar_caches()


@pytest.fixture
def cliente():
    from app.main import app

    with TestClient(app) as c:
        yield c


# ---------------------------------------------------------------- regra (app/corte.py, app/config.py)

@pytest.mark.parametrize("fim, esperado", [
    ("2026-11-02", date(2026, 10, 31)),  # meio do mês: o mês anterior
    ("2026-10-31", date(2026, 10, 31)),  # último dia do mês: ele mesmo
    ("2026-10-30", date(2026, 9, 30)),
    ("2026-12-31", date(2026, 12, 31)),
    ("2027-01-05", date(2026, 12, 31)),  # virada de ano
    ("2028-03-01", date(2028, 2, 29)),  # ano bissexto
    (date(2026, 11, 2), date(2026, 10, 31)),
    (pd.Timestamp("2026-11-02"), date(2026, 10, 31)),
])
def test_data_de_exibicao_mes_fechado(recorte, fim, esperado):
    assert corte.data_exibicao(fim) == esperado


def test_data_de_exibicao_off_e_vazia(monkeypatch):
    monkeypatch.setattr(config, "RECORTE_EXIBICAO", "off")
    assert corte.data_exibicao("2026-11-02") == date(2026, 11, 2)
    assert not corte.mes_fechado_ligado()
    assert corte.data_exibicao(None) is None
    assert corte.data_exibicao(pd.NaT) is None


def test_config_padrao_mes_fechado_e_valor_invalido(monkeypatch):
    try:
        monkeypatch.delenv("RECORTE_EXIBICAO", raising=False)
        importlib.reload(config)
        assert config.RECORTE_EXIBICAO == "mes_fechado"
        monkeypatch.setenv("RECORTE_EXIBICAO", "False")
        importlib.reload(config)
        assert config.RECORTE_EXIBICAO == "off"
        monkeypatch.setenv("RECORTE_EXIBICAO", "trimestre")
        with pytest.raises(ValueError, match="RECORTE_EXIBICAO"):
            importlib.reload(config)
    finally:
        monkeypatch.undo()
        importlib.reload(config)
    assert config.RECORTE_EXIBICAO == "off"  # volta ao do conftest


# ---------------------------------------------------------------- rodapé (formato.recorte e situacao_carga)

def test_rodape_mostra_o_dia_exibido_e_a_situacao_da_carga(recorte):
    momento = datetime(2026, 11, 3, 9, 2, tzinfo=config.FUSO)  # carga de 03/11 09:02: fim 02/11
    assert formato.recorte(momento) == "31/10/2026"
    assert formato.situacao_carga(momento) == "02/11/2026"
    no_fim_do_mes = datetime(2026, 11, 1, 9, 2, tzinfo=config.FUSO)  # fim 31/10: nada a recortar
    assert formato.recorte(no_fim_do_mes) == "31/10/2026"
    assert formato.situacao_carga(no_fim_do_mes) == ""
    assert formato.situacao_carga(None) == ""


def test_rodape_off_como_antes(monkeypatch):
    monkeypatch.setattr(config, "RECORTE_EXIBICAO", "off")
    momento = datetime(2026, 11, 3, 9, 2, tzinfo=config.FUSO)
    assert formato.recorte(momento) == "02/11/2026"
    assert formato.situacao_carga(momento) == ""


def test_rodape_na_pagina(recorte, cliente):
    # conftest: a situação das tabelas é de 21/10/2026 09:02 (fim 20/10) → a tela mostra até 30/09
    html = cliente.get("/viu-agenciamento").text
    assert "Dados até 30/09/2026 · situação dos pedidos em 20/10/2026 · atualizados em 21/10/2026, 09:02" in html
    html = cliente.get("/viu-agenciamento/capa").text
    assert "Dados até" not in html  # a capa segue sem rodapé (sem_rodape)


# ---------------------------------------------------------------- Demanda

def _carga(entrada_diaria, processado_em):
    """Entrada sintética + 1 pedido em 01/11 e 1 em 02/11/2026 (e 1 em 01/11/2025), com a carga dada (UTC)."""
    return com_dias(entrada_diaria, ["2025-11-01", "2026-11-01", "2026-11-02"], processado_em)


def test_demanda_carga_no_meio_do_mes(recorte, entrada_diaria):
    e = entrada.entrada(_carga(entrada_diaria, "2026-11-03 12:00"))  # fim 02/11 → mostra até 31/10
    assert e["total"] == 22  # os 2 de novembro ficam fora (22 até 31/10)
    assert e["periodo"] == "até 31 de outubro" and e["ate_curto"] == "31/out"
    out, nov = e["meses"][9], e["meses"][10]
    assert out["total"] == 3 and not out["parcial"] and not out["futuro"]
    assert nov["total"] == 0 and nov["futuro"] and not nov["parcial"]
    assert e["comparacao"]["total"] == 13  # 2025 até 31/10/2025 (o pedido de 01/11/2025 fica fora)
    assert all(m < "2026-11" for m in e["meses_extrato"])


def test_demanda_carga_no_ultimo_dia_do_mes(recorte, entrada_diaria):
    e = entrada.entrada(_carga(entrada_diaria, "2026-11-01 12:00"))  # fim 31/10: ele mesmo
    assert e["total"] == 22 and e["periodo"] == "até 31 de outubro"
    assert e["meses"][10]["futuro"] and not e["meses"][10]["parcial"]


def test_demanda_off_ate_o_fim_da_carga(monkeypatch, entrada_diaria):
    monkeypatch.setattr(config, "RECORTE_EXIBICAO", "off")
    e = entrada.entrada(_carga(entrada_diaria, "2026-11-03 12:00"))
    assert e["total"] == 24 and e["periodo"] == "até 2 de novembro"
    assert e["meses"][10]["parcial"] and e["meses"][10]["total"] == 2
    assert e["comparacao"]["total"] == 14  # 2025 até 02/11/2025


def test_demanda_extrato_e_atendimento_com_safra_depois_do_recorte(recorte, monkeypatch, entrada_diaria, fluxo_mensal):
    """A safra de novembro (fluxo) fica fora da conferência entrada × fluxo: o extrato e o Atendimento continuam."""
    diaria = _carga(entrada_diaria, "2026-11-03 12:00")
    linhas = (diaria.loc[pd.to_datetime(diaria["data"]).dt.year == 2026]
              .assign(m=lambda d: pd.to_datetime(d["data"]).dt.to_period("M").dt.start_time.dt.date)
              .groupby("m").apply(lambda d: int((d.quantidade + d.quantidade_estimada).sum()), include_groups=False))
    fluxo = pd.DataFrame({"mes_entrada": list(linhas.index), "evento": "entregue", "mes_evento": list(linhas.index),
                          "quantidade": list(linhas.values), "grupo_input": "Mercado", "tipo_de_input": "Mercado",
                          "familia": "Nenhuma"})
    fluxo["_processado_em"] = diaria["_processado_em"].iloc[0]
    assert ap._mesma_fotografia(diaria, fluxo)  # a safra de novembro (2) não conta contra o recorte
    monkeypatch.setattr(config, "RECORTE_EXIBICAO", "off")
    assert ap._mesma_fotografia(diaria, fluxo)  # sem recorte, novembro entra dos dois lados
    monkeypatch.setattr(config, "RECORTE_EXIBICAO", "mes_fechado")
    a = atendimento.atendimento(diaria, fluxo)
    assert a["periodo"] == "até 31 de outubro"
    assert a["meses"][10]["futuro"] and not a["meses"][10]["parcial"]
    assert a["total"]["entradas"] == 22


# ---------------------------------------------------------------- SLA (página e estudo)

def test_sla_sem_mes_parcial_com_o_recorte(recorte, movimentos):
    # carga de 21/10 (fim 20/10) → mostra até 30/09: outubro ainda não começou na tela
    assert sla.data_corte(movimentos) == date(2026, 9, 30)
    parcial = sla.mes_parcial(movimentos)
    assert parcial == "2026-10"
    e = calc_sla.entrega(movimentos, parcial)
    out = e["meses"][9]
    assert out["futuro"] and not out["parcial"] and out["n"] == 0 and out["ate"] is None
    assert not any(m["parcial"] for m in e["meses"])
    assert e["n_ano"] == 4  # os meses completos (jan–set) não mudam


def test_sla_off_mostra_o_mes_parcial(monkeypatch, movimentos):
    monkeypatch.setattr(config, "RECORTE_EXIBICAO", "off")
    assert sla.data_corte(movimentos) == date(2026, 10, 20)
    e = calc_sla.entrega(movimentos, sla.mes_parcial(movimentos))
    out = e["meses"][9]
    assert out["parcial"] and out["n"] == 1 and out["ate"] == "20/10"
    assert e["n_ano"] == 4


def test_estudo_exemplo_so_ate_o_dia_mostrado(recorte, movimentos):
    """O exemplo do dia sai das entregas até o último dia mostrado: o P6 (entregue em 06/10) fica fora."""
    ex = calc_sla.exemplo(movimentos, sla.mes_parcial(movimentos), fixo="P6")
    assert ex is None or "06/10" not in ex["pronto"]
    r = ap.montar_estudo_sla({})
    assert r["recorte"]["n"] == 4  # o estudo usa só meses completos: igual com ou sem recorte


# ---------------------------------------------------------------- Talentos

def _ranking(linhas):
    """[(grupo, talento, mês, n_mes)] → gold de ranking (n = soma do ano, pos pela ordem da gold)."""
    df = pd.DataFrame(linhas, columns=["grupo", "talento", "mes", "n_mes"])
    df["n"] = df.groupby(["grupo", "talento"])["n_mes"].transform("sum")
    df["mes"] = pd.to_datetime(df["mes"]).dt.date
    df["ultimo_pedido"] = pd.Timestamp("2026-11-02")
    df["empate_fora"] = 0
    df["talentos_grupo"] = df.groupby("grupo")["talento"].transform("nunique")
    ordem = df.drop_duplicates(["grupo", "talento"]).sort_values(["grupo", "n", "talento"], ascending=[True, False, True])
    ordem["pos"] = ordem.groupby("grupo").cumcount() + 1
    return df.merge(ordem[["grupo", "talento", "pos"]], on=["grupo", "talento"])


def _divisao_ano(ex, ne, sem, squad=0):
    return pd.DataFrame({"ano": [2026] * 3, "categoria": ["Exclusivos", "Não exclusivos", "Sem talento"],
                         "n": [ex, ne, sem], "total": [ex + ne + sem] * 3, "pct": [0.0] * 3,
                         "dos_quais_squad": [0, squad, 0]})


def test_talentos_recorta_ranking_e_divisao_quando_reconcilia():
    rk = _ranking([("exclusivo", "A", "2026-10-01", 5), ("exclusivo", "A", "2026-11-01", 2),
                   ("exclusivo", "B", "2026-10-01", 6), ("exclusivo", "Só nov", "2026-11-01", 1),
                   ("nao-exclusivo", "C", "2026-09-01", 3), ("nao-exclusivo", "C", "2026-11-01", 1),
                   ("todos", "A", "2026-10-01", 5), ("todos", "A", "2026-11-01", 2), ("todos", "B", "2026-10-01", 6),
                   ("todos", "Só nov", "2026-11-01", 1), ("todos", "C", "2026-09-01", 3), ("todos", "C", "2026-11-01", 1)])
    ag, r, ok = tal.recortar(_divisao_ano(20, 10, 2), rk, pd.Timestamp("2026-10-31"), removidos=4)
    assert ok
    assert ag.set_index("categoria")["n"].to_dict() == {"Exclusivos": 17, "Não exclusivos": 9, "Sem talento": 2}
    assert set(ag["total"]) == {28}
    assert (pd.to_datetime(r["mes"]) <= "2026-10-31").all()
    ex = r[r.grupo == "exclusivo"].drop_duplicates("talento").set_index("talento")
    assert ex["n"].to_dict() == {"A": 5, "B": 6}  # A perdeu os 2 de novembro; "Só nov" sumiu
    assert ex.loc["B", "pos"] == 1 and ex.loc["A", "pos"] == 2  # nova ordem pelo n
    assert set(ex["talentos_grupo"]) == {2}  # 3 talentos − o que só tinha novembro
    assert pd.isna(ex.loc["A", "ultimo_pedido"])  # o último dia de A antes de novembro não está na gold
    # a página monta o mapa sem meses depois do recorte (a soma dos meses fecha com o n)
    top = tal.top_por_grupo(r, tal.divisao(ag, 28, 2026))
    assert tal.mapa(top["exclusivo"], date(2026, 10, 31)) is not None


def test_talentos_sem_reconciliar_mantem_a_divisao():
    rk = _ranking([("exclusivo", "A", "2026-10-01", 5), ("exclusivo", "A", "2026-11-01", 2),
                   ("todos", "A", "2026-10-01", 5), ("todos", "A", "2026-11-01", 2)])
    ag = _divisao_ano(20, 10, 2)
    # 3 pedidos saíram na gold de entradas, mas o ranking só explica 2 (1 sem talento ou do Squad, fora do ranking)
    novo, r, ok = tal.recortar(ag, rk, pd.Timestamp("2026-10-31"), removidos=3)
    assert not ok
    assert novo.equals(ag)
    assert r[r.grupo == "exclusivo"]["n"].iloc[0] == 5  # o ranking é recortado mesmo assim


def test_talentos_sem_nada_depois_do_recorte_fica_igual():
    rk = _ranking([("exclusivo", "A", "2026-10-01", 5), ("todos", "A", "2026-10-01", 5)])
    ag = _divisao_ano(5, 0, 0)
    novo_ag, novo_rk, ok = tal.recortar(ag, rk, pd.Timestamp("2026-10-31"), removidos=0)
    assert ok and novo_ag is ag and novo_rk is rk


def test_talentos_pagina_sem_reconciliar_avisa_e_mapa_sem_outubro(recorte):
    """conftest: entrada até 20/10 → mostra até 30/09. Saem 3 pedidos de outubro (Início 19), mas o ranking só explica 2
    (Talento A e Talento C): a divisão fica a da carga (22) com o aviso de diferença da T5; o mapa já vem sem outubro."""
    t = ap.montar_talentos({})
    assert t["talentos"]["total"] == 22 and t["talentos"]["total_inicio"] == 19 and t["em_atualizacao"]
    cols = t["mapa"]["colunas"]
    assert not any(c["parcial"] for c in cols) and cols[9]["futuro"]
    assert t["mapa"]["ate"] == "30/09"


# ---------------------------------------------------------------- Previsão

def test_previsao_sem_mes_em_andamento_com_o_recorte(recorte):
    p = previsao_sintetica()  # dados até 20/10, retrato de set, acompanhamento de out
    t = previsao.tela(p)
    assert t["acompanhamento"] is None
    col = next(c for c in t["colunas"] if not c["nao_se_aplica"])
    assert [m["mes"] for m in col["meses"]] == ["2026-10", "2026-11", "2026-12"]
    assert not any(m["vigente"] for m in col["meses"]) and all(m["realizado"] is None for m in col["meses"])
    assert not any(b["classe"] == "pv-real-parcial" for b in col["grafico"]["colunas"])
    assert p["acompanhamento"]["mes"] == "2026-10"  # o contrato não muda (só a exibição)


def test_previsao_carga_no_ultimo_dia_do_mes(recorte):
    p = previsao_sintetica()
    p["carga"]["dados_ate"] = "2026-09-30"
    t = previsao.tela(p)
    assert t["acompanhamento"] is None
    col = next(c for c in t["colunas"] if not c["nao_se_aplica"])
    assert col["meses"][0]["mes"] == "2026-10" and not col["meses"][0]["vigente"]


def test_previsao_off_mostra_o_mes_em_andamento(monkeypatch):
    monkeypatch.setattr(config, "RECORTE_EXIBICAO", "off")
    t = previsao.tela(previsao_sintetica())
    assert t["acompanhamento"]["mes"] == "2026-10"
    col = next(c for c in t["colunas"] if not c["nao_se_aplica"])
    assert col["meses"][0]["vigente"] and col["meses"][0]["realizado"] is not None


def test_previsao_pagina_e_rodape(recorte, cliente):
    html = cliente.get("/viu-agenciamento/previsao").text
    assert "em andamento" not in html and "acompanhamento até" not in html
    assert "previsão dos próximos três meses" in html
    r = ap.montar_previsao({})
    assert r["rodape_extra"] is None


def test_previsao_pagina_off_como_antes(monkeypatch, cliente):
    monkeypatch.setattr(config, "RECORTE_EXIBICAO", "off")
    ap.limpar_caches()
    html = cliente.get("/viu-agenciamento/previsao").text
    assert "em andamento" in html


def test_cache_das_telas_separa_o_recorte(monkeypatch, entrada_diaria):
    """F18: o recorte entra na chave das contas guardadas (a troca não reaproveita a tela do outro modo)."""
    diaria = com_dias(entrada_diaria, ["2026-11-02"], "2026-11-03 12:00")
    monkeypatch.setattr(dados.entrada, "df", lambda forcar=False: diaria)
    monkeypatch.setattr(config, "RECORTE_EXIBICAO", "off")
    entrada._cache.clear()
    assert ap.montar_inicio({})["entrada"]["total"] == 23
    monkeypatch.setattr(config, "RECORTE_EXIBICAO", "mes_fechado")
    assert ap.montar_inicio({})["entrada"]["total"] == 22
    assert ap._ambiente_calculo()[1] == "mes_fechado"

def test_sla_na_virada_do_ano_segue_o_ano_mostrado(recorte, movimentos):
    """Revisão de 03/11/2026 (A3): carga de 04/01/2027 com o recorte mostra até 31/12/2026, e Demanda e Talentos exibem
    2026. O SLA e o estudo seguem o mesmo ano, com jan a dez completos (antes: 2027 vazio, nenhum mês completo)."""
    jan = movimentos.copy()
    jan.attrs = {"versao": "virada-2027"}
    jan["_processado_em"] = pd.Timestamp("2027-01-04 12:00", tz="UTC")
    assert sla.data_corte(jan) == date(2026, 12, 31)
    parcial = sla.mes_parcial(jan)
    assert parcial == "2026-13"
    e = calc_sla.entrega(jan, parcial)
    assert e["ano_num"] == "2026" and e["periodo"] == "jan a dez"
    assert not any(m["parcial"] or m["futuro"] for m in e["meses"])
    assert e["n_ano"] == 5  # as 4 entregas de jan–set + a de outubro (P6), todas em meses completos de 2026
    r = calc_sla.recorte(jan, parcial)
    assert r["periodo"] == "jan a dez de 2026" and r["proximo"] == "janeiro"
    assert ap._estudo_slides(jan, parcial, "todos")["recorte"]["n"] == 5  # o estudo inteiro roda com o ano mostrado


def test_sla_na_virada_do_ano_sem_recorte_fica_no_ano_da_carga(monkeypatch, movimentos):
    monkeypatch.setattr(config, "RECORTE_EXIBICAO", "off")
    jan = movimentos.copy()
    jan.attrs = {"versao": "virada-2027-off"}
    jan["_processado_em"] = pd.Timestamp("2027-01-04 12:00", tz="UTC")
    assert sla.mes_parcial(jan) == "2027-01"  # E3: janeiro de 2027 é o mês parcial
