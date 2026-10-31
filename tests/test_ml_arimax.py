"""ARIMAX x ARIMA (ml/modelos/arimax.py) com séries sintéticas, sem BigQuery."""

import numpy as np
import pandas as pd
import pytest

pytest.importorskip("statsmodels")

from ml import regua  # noqa: E402
from ml.modelos import arimax  # noqa: E402


def _serie(valores, inicio="2024-10", nome="Mercado"):
    return pd.Series([float(v) for v in valores], index=pd.period_range(inicio, periods=len(valores), freq="M"),
                     name=nome)


RNG = np.random.default_rng(7)
# cresce ~5% ao mês com ruído multiplicativo; 2024-10 .. 2026-09 (24 meses)
SERIE = _serie(np.round(100 * 1.05 ** np.arange(24) * np.exp(RNG.normal(0, 0.08, 24))))


def test_predict_contrato_e_faixa():
    for m in (arimax.Arimax("a", (1, 0, 0), "ct", cols=()), arimax.Arimax("x", (1, 0, 0), "ct")):
        p = regua.prever_de(m, SERIE, SERIE.index[-1] + 1, 3)
        assert list(p.columns) == ["valor", "p10", "p90"] and len(p) == 3
        assert (p["valor"] > 0).all()
        assert (p["p10"] <= p["valor"]).all() and (p["valor"] <= p["p90"]).all()
        assert p["p90"].iloc[2] - p["p10"].iloc[2] >= p["p90"].iloc[0] - p["p10"].iloc[0]  # faixa abre


def test_tendencia_em_log_acompanha_crescimento():
    p = regua.prever_de(arimax.Arimax("a", (1, 0, 0), "ct", cols=()), SERIE, SERIE.index[-1] + 1, 3)
    assert p["valor"].iloc[2] > p["valor"].iloc[0] > SERIE.iloc[-6:].mean()


def test_ax1_exogena_sem_informacao_sai():
    treino = SERIE[SERIE.index < pd.Period("2026-02", "M")]  # só jan/2026 com ano_2026 = 1
    X, usadas = arimax._matriz(treino.index, arimax.TODAS, 0)
    assert "ano_2026" not in usadas and "dias_uteis" in usadas and "fim_de_ano" in usadas
    X, usadas = arimax._matriz(SERIE.index[:12], arimax.TODAS, 1)  # 2024-10..2025-09: nada de 2026
    assert "ano_2026" not in usadas


def test_exogena_conhecida_e_usada_no_futuro():
    """Série com salto em nov/dez: o ARIMAX com fim_de_ano prevê nov/dez acima de out."""
    base = 100 * np.ones(24)
    meses = pd.period_range("2024-10", periods=24, freq="M")
    base[[m.month in (11, 12) for m in meses]] = 160
    s = _serie(base * np.exp(RNG.normal(0, 0.02, 24)))
    m = arimax.Arimax("x", (1, 0, 0), "c", cols=("fim_de_ano",)).fit(s)
    p = m.predict(3)  # out, nov, dez/2026
    assert m.usadas_ == ("fim_de_ano",)
    assert p["valor"].iloc[1] > 1.3 * p["valor"].iloc[0]


def test_sem_vazamento_e_deterministico():
    m = arimax.Arimax("x", (1, 1, 0), "n")
    origem = pd.Period("2026-03", "M")
    a = regua.prever_de(m, SERIE, origem, 3)
    futuro_alterado = SERIE.copy()
    futuro_alterado[futuro_alterado.index >= origem] *= 10
    b = regua.prever_de(m, futuro_alterado, origem, 3)
    pd.testing.assert_frame_equal(a, b)


def test_auto_escolhe_dentro_do_treino():
    m = arimax.Arimax("auto", auto=True, cols=()).fit(SERIE.iloc[:14])
    assert (m.ordem_, m.tendencia_) in arimax.ORDENS and m.cols_ == ()
    assert np.isfinite(m.wape_interno_)
    assert len(m.predict(2)) == 2


def test_nomes_unicos_e_pares_mesma_ordem():
    nomes = [m.nome for m in arimax.MODELOS]
    assert len(nomes) == len(set(nomes))
    por_nome = {m.nome: m for m in arimax.MODELOS}
    for n, m in por_nome.items():
        if n.startswith("arima_") and not m.auto:
            par = por_nome["arimax_" + n[len("arima_"):]]
            assert (par.ordem, par.tendencia) == (m.ordem, m.tendencia) and par.cols and not m.cols
