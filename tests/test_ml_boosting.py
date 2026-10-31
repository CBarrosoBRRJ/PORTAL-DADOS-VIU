"""Teste rápido do especialista de gradient boosting (ml/modelos/boosting.py) com dados sintéticos."""

import numpy as np
import pandas as pd
import pytest

pytest.importorskip("lightgbm")
pytest.importorskip("xgboost")

from ml import regua  # noqa: E402
from ml.modelos import boosting  # noqa: E402


def _serie(n=24, inicio="2024-10", nome="Inbound", crescimento=0.03, semente=0):
    rng = np.random.default_rng(semente)
    t = np.arange(n)
    v = 50 * np.exp(crescimento * t) * (1 + 0.1 * rng.standard_normal(n))
    return pd.Series(np.round(np.clip(v, 1, None)), index=pd.period_range(inicio, periods=n, freq="M"), name=nome)


def test_interface_e_faixa():
    s = _serie()
    for m in boosting.MODELOS:
        p = regua.prever_de(m, s, s.index[-1] + 1, 3)
        assert list(p.columns) == ["valor", "p10", "p90"] and len(p) == 3
        assert (p["valor"] > 0).all()
        # D48: com a janela de 12 meses a faixa empírica sai de ~6 origens internas e pode não conter o ponto quando
        # o passado errou só para um lado (mesmo comportamento das referências); só a ordem p10 <= p90 é garantida
        assert (p["p10"] <= p["p90"] + 1e-9).all()


def test_extrapola_crescimento_acima_do_maximo():
    """O alvo em razão sobre o nível deixa a árvore acompanhar a alta (árvore pura travaria no máximo)."""
    s = pd.Series(np.round(30 * 1.06 ** np.arange(24)), index=pd.period_range("2024-10", periods=24, freq="M"),
                  name="Mercado")
    v = boosting.prever_boost(s, 3, "lgbm")
    assert v[0] > s.iloc[-3:].mean()


def test_deterministico_e_sem_futuro():
    s = _serie(semente=3)
    a = regua.prever_de(boosting.Boost("xgb"), s, pd.Period("2026-03", "M"), 3)
    boosting._CACHE.clear()
    b = regua.prever_de(boosting.Boost("xgb"), s, pd.Period("2026-03", "M"), 3)
    pd.testing.assert_frame_equal(a, b)
    # mudar o futuro (depois da origem) não muda a previsão
    s2 = s.copy()
    s2[s2.index >= pd.Period("2026-03", "M")] *= 10
    c = regua.prever_de(boosting.Boost("xgb"), s2, pd.Period("2026-03", "M"), 3)
    pd.testing.assert_frame_equal(a, c)


def test_auto_escolhe_dentro_do_treino():
    s = _serie(n=18)
    motor, erros = boosting.escolher_motor(s)
    assert motor in boosting.CANDIDATOS_AUTO and set(erros) == set(boosting.CANDIDATOS_AUTO)
