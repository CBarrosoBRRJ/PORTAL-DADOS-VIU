"""Especialista Prophet (ml/modelos/prophet.py) com séries sintéticas, sem BigQuery."""

import numpy as np
import pandas as pd
import pytest

pytest.importorskip("prophet")

from ml import regua  # noqa: E402
from ml.modelos import prophet as mp  # noqa: E402


def _serie(valores, inicio="2024-10", nome="Inbound"):
    return pd.Series([float(v) for v in valores], index=pd.period_range(inicio, periods=len(valores), freq="M"),
                     name=nome)


RNG = np.random.default_rng(7)
# 24 meses: patamar ~50 em 2024-25 e ~100 em 2026, com ruído
SERIE = _serie(np.r_[50 + RNG.normal(0, 4, 15), 100 + RNG.normal(0, 6, 9)].round())


def test_contrato_faixa_ordenada_e_nao_negativa():
    m = mp.ProphetMensal("t", escala="log", cps=0.1, sazonal=True, amostras=300).fit(SERIE)
    p = m.predict(3)
    assert list(p.columns) == ["valor", "p10", "p90"] and len(p) == 3
    assert (p["p10"] <= p["valor"]).all() and (p["valor"] <= p["p90"]).all() and (p["p10"] >= 0).all()


def test_acompanha_mudanca_de_patamar():
    p = mp.ProphetMensal("t", escala="log", cps=0.5, sazonal=False, amostras=0).fit(SERIE).predict(1)
    assert p["valor"].iloc[0] > 80  # perto do patamar novo, não da média geral (~70)


def test_reproduzivel_com_semente():
    a = mp.ProphetMensal("t", amostras=300).fit(SERIE).predict(3)
    b = mp.ProphetMensal("t", amostras=300).fit(SERIE).predict(3)
    pd.testing.assert_frame_equal(a, b)


def test_auto_escolhe_so_com_o_treino(monkeypatch):
    vistos = []
    original = mp.ProphetMensal.fit

    def espiao(self, serie):
        vistos.append(serie.index[-1])
        return original(self, serie)

    monkeypatch.setattr(mp.ProphetMensal, "fit", espiao)
    monkeypatch.setattr(mp.ProphetAuto, "GRADE", {"escala": ("log",), "cps": (0.1,), "sazonal": (False,)})
    origem = pd.Period("2026-03", "M")
    regua.prever_de(mp.ProphetAuto(origens_internas=2), SERIE, origem, 3)
    assert vistos and max(vistos) < origem


def test_nomes_unicos():
    nomes = [m.nome for m in mp.MODELOS]
    assert len(nomes) == len(set(nomes))
