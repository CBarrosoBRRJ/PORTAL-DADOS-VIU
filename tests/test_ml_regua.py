"""Régua de backtest da previsão (ml/regua.py) com séries sintéticas, sem BigQuery."""

import json

import numpy as np
import pandas as pd
import pytest

from ml import calendario, regua, rodar
from ml.modelos import referencia


def _serie(valores, inicio="2024-10", nome="Inbound"):
    return pd.Series([float(v) for v in valores], index=pd.period_range(inicio, periods=len(valores), freq="M"),
                     name=nome)


SERIE = _serie(range(10, 34))  # 2024-10 .. 2026-09, cresce 1 por mês


class Espiao:
    """Registra o 1º e o último mês de treino de cada fit e prevê o último valor."""
    nome = "espiao"
    registro = []

    def fit(self, serie):
        self.v_ = serie.iloc[-1]
        Espiao.registro.append((serie.index[0], serie.index[-1], len(serie)))
        return self

    def predict(self, h):
        return pd.DataFrame({"valor": [self.v_] * h, "p10": [self.v_ - 1] * h, "p90": [self.v_ + 1] * h})


def test_janela_de_12_meses_sem_vazamento():
    """D48 (R1/R2): cada previsão treina só com os 12 meses fechados anteriores à origem; teste = h1 de jun–set."""
    Espiao.registro = []
    b = regua.backtest(Espiao(), SERIE)
    assert len(b) == 17  # h1 de jan–set (5 de verificação + 4 de teste) + h2 e h3 de jun–set
    for _, r in b.iterrows():
        alvo, origem = pd.Period(r["alvo"], "M"), pd.Period(r["origem"], "M")
        assert alvo == origem + (r["horizonte"] - 1)
        assert r["valor"] == SERIE[origem - 1]  # previsão = último valor visto, do mês anterior à origem
    for inicio, fim, n in Espiao.registro:
        assert n == 12 and (fim - inicio).n == 11  # exatamente 12 meses, sem buraco
    origens = sorted(fim + 1 for _, fim, _ in Espiao.registro)
    assert [str(o) for o in origens] == [f"2026-{m:02d}" for m in range(1, 10)]  # jan..set; nunca treina com o alvo
    teste = b[(b["trecho"] == "teste") & (b["horizonte"] == 1)]
    assert list(teste["alvo"]) == ["2026-06", "2026-07", "2026-08", "2026-09"]
    jun = teste.iloc[0]
    assert jun["origem"] == "2026-06" and regua.treino_de(SERIE, pd.Period("2026-06", "M")).index[0] == pd.Period("2025-06", "M")
    assert set(b.loc[b["trecho"] == "verificacao", "alvo"]) == {f"2026-0{m}" for m in range(1, 6)}
    m = regua.metricas_d48(b)
    assert m["1"]["n"] == 4 and m["todos"]["n"] == 12 and m["verificacao"]["n"] == 5


def test_protocolo_antigo_acessivel():
    """R6: o protocolo D47 (histórico inteiro, alvos jan–set, h1–h3) continua disponível para comparação."""
    Espiao.registro = []
    b = regua.backtest(Espiao(), SERIE, pares=regua.pares_d47(), janela=None)
    assert len(b) == 27 and min(i for i, _, _ in Espiao.registro) == pd.Period("2024-10", "M")


def test_nao_se_aplica_com_janela_curta():
    """R4: modelo que pede mais meses do que a janela não roda e fica registrado com o motivo."""
    class Anual(Espiao):
        nome, minimo_treino, motivo_minimo = "anual", 24, "precisa de 2 ciclos"

    with pytest.raises(regua.NaoSeAplica, match="2 ciclos"):
        regua.backtest(Anual(), SERIE)
    r, resumo = rodar.avaliar_modelo(Anual(), {"Inbound": SERIE})
    assert "nao_se_aplica" in r and "series" not in r and resumo.startswith("não se aplica")
    regua.backtest(Anual(), SERIE, pares=regua.pares_d47(), janela=None)  # sem janela, roda


def test_metricas_contas():
    b = pd.DataFrame({"real": [100.0, 200.0], "valor": [90.0, 230.0], "p10": [80.0, np.nan], "p90": [95.0, np.nan]})
    m = regua.metricas(b)
    assert m["wape"] == pytest.approx(40 / 300)
    assert m["mae"] == pytest.approx(20)
    assert m["vies"] == pytest.approx(20 / 300)
    assert m["cobertura_80"] == 0.0 and m["n_faixa"] == 1
    assert m["largura"] == pytest.approx(0.15)


def test_serie_constante_erro_zero_e_futuro():
    s = _serie([50] * 24)
    r = regua.avaliar(referencia.Media(3), {"Inbound": s})
    assert r["Inbound"]["metricas"]["todos"]["wape"] == 0 and r["Inbound"]["metricas"]["1"]["wape"] == 0
    f = regua.prever_futuro(referencia.Media(3), {"Inbound": s})["Inbound"]
    assert [x["mes"] for x in f] == ["2026-10", "2026-11", "2026-12"]
    assert all(x["valor"] == 50 for x in f)


def test_referencias_formato_e_valores():
    hist = SERIE[SERIE.index < pd.Period("2026-01", "M")]  # termina em 2025-12 = 24.0
    assert referencia.UltimoMes().prever_ponto(hist, 2) == [24.0, 24.0]
    assert referencia.Media(3).prever_ponto(hist, 1) == [23.0]
    assert referencia.MesmoMesAnoAnterior().prever_ponto(hist, 3) == [13.0, 14.0, 15.0]  # jan, fev, mar/2025
    assert referencia.TendenciaLinear(6).prever_ponto(hist, 2) == pytest.approx([25.0, 26.0])
    for m in referencia.MODELOS:
        p = regua._normalizar(m.fit(hist).predict(3), 3, hist.index[-1] + 1)
        assert list(p.columns) == ["valor", "p10", "p90"] and len(p) == 3


def test_faixa_vem_do_passado_do_treino():
    s = _serie([100, 120] * 12)  # alterna: o "último mês" erra ±20% sempre
    m = referencia.UltimoMes().fit(s)
    p = m.predict(1).iloc[0]
    assert p["p10"] < p["valor"] < p["p90"]


def test_mes_parcial_fora_do_treino():
    linhas = [{"mes": str(p), "tipo": t, "pedidos": 10, "estimados": 0, "completo": p < pd.Period("2026-10", "M"),
               "dados_ate": "2026-10-22", "processado_em": "2026-10-23"}
              for t in ("Inbound", "Mercado") for p in pd.period_range("2024-10", "2026-10", freq="M")]
    series, meta = regua.carregar_series(pd.DataFrame(linhas))
    assert series["Mercado"].index[-1] == pd.Period("2026-09", "M") and len(series["Mercado"]) == 24
    assert meta["mes_fechado"] == "2026-09"
    assert meta["parcial"]["Inbound"] == {"mes": "2026-10", "pedidos_ate_agora": 10.0}


def test_runner_grava_json(tmp_path):
    series = {"Inbound": SERIE, "Mercado": SERIE.rename("Mercado") * 2}
    meta = {"processado_em": "x", "dados_ate": "2026-10-22", "parcial": {}}
    rodar.rodar_modulo("referencia", series=series, meta=meta, pasta=tmp_path)
    tudo = rodar.juntar(series, meta, pasta=tmp_path, destino=tmp_path / "resultados.json")
    d = json.loads((tmp_path / "resultados.json").read_text(encoding="utf-8"))
    assert set(d["modelos"]) == {m.nome for m in referencia.MODELOS}
    assert tudo["melhor_referencia"]["Inbound"]["1"]["modelo"].startswith("ref_")
    assert len(d["modelos"]["ref_media_3m"]["futuro"]["Mercado"]) == 3


def test_calendario_dias_uteis():
    assert calendario.dias_uteis(pd.Period("2026-09", "M")) == 21  # 22 dias seg-sex, 07/09 feriado
    e = calendario.exogenas(pd.period_range("2025-11", "2026-01", freq="M"))
    assert e["fim_de_ano"].tolist() == [1, 1, 0] and e["ano_2026"].tolist() == [0, 0, 1]


def test_series_curtas_janela_expansiva_sem_vazamento():
    """R7 (D56): na série só de 2026, cada previsão treina com TODOS os meses fechados antes da origem (janela
    expansiva: 5, 6, 7 e 8 meses no teste jun–set), nada da origem em diante; modelo sem mínimo curto (12 meses) não se
    aplica; a verificação jan–mai fica vazia (incompleta); o "não se aplica" é por série."""
    curta = _serie(range(50, 59), inicio="2026-01", nome="Mercado exclusivos")  # jan–set/2026

    class Curto(Espiao):
        nome = "ref_ultimo_mes"  # mínimo de 1 mês (MINIMO_CURTO)

    Espiao.registro = []
    b = regua.backtest(Curto(), curta)
    for inicio, fim, n in Espiao.registro:
        assert inicio == pd.Period("2026-01", "M") and n == (fim - inicio).n + 1  # desde o 1º mês, sem buraco
    for _, r in b.iterrows():
        assert pd.Period(r["origem"], "M") > pd.Period(r["alvo"], "M") - r["horizonte"]  # alvo nunca no treino
        assert r["valor"] == curta[pd.Period(r["origem"], "M") - 1]
    teste = b[(b["trecho"] == "teste") & (b["horizonte"] == 1)]
    assert list(teste["alvo"]) == ["2026-06", "2026-07", "2026-08", "2026-09"]
    assert [len(regua.treino_de(curta, pd.Period(a, "M"))) for a in teste["alvo"]] == [5, 6, 7, 8]
    m = regua.metricas_d48(b)
    assert m["1"]["n"] == 4 and m["verificacao"]["n"] == 0 and m["verificacao"]["n_parcial"] == 4
    assert m["verificacao"]["wape"] != m["verificacao"]["wape"]  # NaN: sem verificação
    f = regua.prever_futuro(Curto(), {"Mercado exclusivos": curta})["Mercado exclusivos"]
    assert [x["mes"] for x in f] == ["2026-10", "2026-11", "2026-12"] and Espiao.registro[-1][2] == 9
    with pytest.raises(regua.NaoSeAplica, match="12 meses"):
        regua.backtest(Espiao(), curta)  # sem mínimo curto: precisa da janela inteira
    assert regua.minimo(referencia.Media(6)) == 6 and regua.minimo(referencia.UltimoMes()) == 1
    r, resumo = rodar.avaliar_modelo(referencia.Media(6), {"Inbound": SERIE, "Mercado exclusivos": curta})
    assert "metricas" in r["series"]["Inbound"] and "nao_se_aplica" in r["series"]["Mercado exclusivos"]
    assert "Mercado exclusivos" not in r["futuro"] and "n/a" in resumo
    longa = regua.metricas_d48(regua.backtest(Curto(), SERIE))  # na série longa nada muda (12 meses em toda origem)
    assert longa["verificacao"]["n"] == 5
