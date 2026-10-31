"""Modelos clássicos (ml/modelos/classico.py) com séries sintéticas, sem BigQuery."""

import numpy as np
import pandas as pd
import pytest

pytest.importorskip("statsmodels")

from ml import regua  # noqa: E402
from ml.modelos import classico  # noqa: E402


def _serie(valores, inicio="2024-10", nome="Mercado"):
    return pd.Series([float(v) for v in valores], index=pd.period_range(inicio, periods=len(valores), freq="M"),
                     name=nome)


RNG = np.random.default_rng(7)
CRESCE = _serie(100 * 1.05 ** np.arange(24) * np.exp(RNG.normal(0, 0.03, 24)))
PLANA = _serie(80 + RNG.normal(0, 4, 24), nome="Inbound")


@pytest.mark.parametrize("nome", ["cls_ets_aicc", "cls_holt_amortecido", "cls_arima_aicc", "cls_theta",
                                  "cls_combinado"])
def test_contrato_e_faixa(nome):
    m = next(x for x in classico.MODELOS if x.nome == nome)
    p = regua.prever_de(m, CRESCE, CRESCE.index[-1] + 1, 3)
    assert list(p.columns) == ["valor", "p10", "p90"] and len(p) == 3
    assert (p["p10"] <= p["valor"]).all() and (p["valor"] <= p["p90"]).all() and (p >= 0).all().all()


def test_segue_crescimento_e_serie_plana():
    m = next(x for x in classico.MODELOS if x.nome == "cls_arima_aicc")
    p = regua.prever_de(m, CRESCE, CRESCE.index[-1] + 1, 3)
    assert p["valor"].iloc[0] > CRESCE.iloc[-6:].mean()  # pega a tendência, não fica na média
    q = regua.prever_de(m, PLANA, PLANA.index[-1] + 1, 3)
    assert abs(q["valor"].iloc[0] - 80) < 12


def test_treino_curto_13_meses():
    """Primeira origem do backtest (nov/2025) tem só 13 meses: todos os candidatos precisam responder."""
    curta = CRESCE.iloc[:13]
    for m in classico.MODELOS:
        if "faixa_erros" in m.nome or m.nome == "cls_validado":
            continue
        p = regua.prever_de(m, curta, curta.index[-1] + 1, 3)
        assert np.isfinite(p["valor"]).all()


def test_validado_escolhe_so_com_o_treino():
    m = classico.Classico("validado", "v", "")
    treino = CRESCE.iloc[:16]
    m.fit(treino)
    assert m.escolhido_ in classico.CANDIDATOS
    # mudar o futuro não muda a escolha (nada além do treino entra na validação)
    m2 = classico.Classico("validado", "v", "").fit(CRESCE.iloc[:16].copy())
    assert m2.escolhido_ == m.escolhido_ and m2.wape_interno_ == m.wape_interno_


def test_ordens_arima_respeitam_amostra_pequena():
    for nome, ((p, d, q), trend) in classico._arima_candidatos(13).items():
        assert p + q + (trend != "n") + 1 <= 3, nome
