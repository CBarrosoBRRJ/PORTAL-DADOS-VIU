"""Especialista de combinação (ml/modelos/combinacao.py) com séries sintéticas, sem BigQuery."""

import numpy as np
import pandas as pd
import pytest

from ml import regua
from ml.modelos import combinacao as cb


def _serie(valores, inicio="2024-10", nome="Inbound"):
    return pd.Series([float(v) for v in valores], index=pd.period_range(inicio, periods=len(valores), freq="M"),
                     name=nome)


CONSTANTE = np.full(24, 100.0)
RETA = 50.0 + 5.0 * np.arange(24)


def test_componentes_constante_preveem_a_constante():
    for nome, f in cb.COMPONENTES.items():
        assert f(CONSTANTE, 3) == pytest.approx([100.0] * 3, rel=1e-6), nome


def test_tendencia_capturada_por_drift_e_holt():
    assert cb.drift(RETA, 3) == pytest.approx([RETA[-1] + 5 * k for k in (1, 2, 3)])
    holt = cb.holt_amort(RETA, 3)
    assert holt[0] > RETA[-1] and holt[2] > holt[0]
    assert cb.theta(RETA, 1)[0] > cb.ses(RETA, 1)[0]  # Theta soma metade da tendência à suavização


def test_sazonal_ajusta_indice_do_ano_anterior_ao_patamar():
    y = np.array([100.0] * 24)
    y[-12] = 200.0  # o mês seguinte ao fim do treino valeu o dobro há um ano
    assert cb.sazonal(y, 2) == pytest.approx([200.0, 100.0])


def test_combinacoes_e_selecao():
    y = RETA.copy()
    prev = np.array([cb.COMPONENTES[c](y, 3) for c in cb.NAO_SAZONAIS])
    med = cb.Combinacao("m", "", cb.NAO_SAZONAIS, "mediana").prever_ponto(_serie(y), 3)
    assert med == pytest.approx(list(np.median(prev, axis=0)))
    w = cb._wape_interno(y, cb.NAO_SAZONAIS)
    assert w["drift"] == pytest.approx(0.0, abs=1e-9)  # reta perfeita: o drift não erra
    sel = cb.Combinacao("s", "", cb.NAO_SAZONAIS, "selecao").prever_ponto(_serie(y), 3)
    assert sel == pytest.approx(cb.drift(y, 3))


def test_fator_de_vies_so_usa_o_passado():
    y = RETA.copy()
    fat = cb._fator_vies(y, cb.ultimo, 3)
    assert all(f > 1 for f in fat)  # o último mês subestima uma série que cresce
    # sem vazamento na régua: a previsão a partir de uma origem não muda se o futuro mudar
    s = _serie(y)
    s2 = s.copy()
    s2.iloc[-3:] = 10_000.0
    m = cb.MODELOS[[x.nome for x in cb.MODELOS].index("comb_mediana_corr")]
    origem = s.index[-3]
    pd.testing.assert_frame_equal(regua.prever_de(m, s, origem, 3), regua.prever_de(m, s2, origem, 3))


@pytest.mark.parametrize("modelo", cb.MODELOS, ids=lambda m: m.nome)
def test_modelos_na_regua(modelo):
    rng = np.random.default_rng(0)
    s = _serie(80 + 3 * np.arange(24) + rng.normal(0, 5, 24))
    if getattr(modelo, "minimo_treino", 0) > regua.JANELA:  # D48 (R4): o sazonal pede 15 meses
        with pytest.raises(regua.NaoSeAplica):
            regua.backtest(modelo, s)
        return
    b = regua.backtest(modelo, s)
    assert len(b) == len(regua.pares_d48()) == 17
    assert b[["valor"]].notna().all().all() and (b["valor"] >= 0).all()
    # faixa empírica (razões real/previsto do treino): p10 <= p90, mas pode não conter o valor quando o passado
    # só errou para um lado (mesmo comportamento das referências da régua)
    assert (b["p10"] <= b["p90"] + 1e-9).all()
    f = regua.prever_de(modelo, s, s.index[-1] + 1, 3)
    assert list(f.index.astype(str)) == ["2026-10", "2026-11", "2026-12"]
    assert len(regua.backtest(modelo, s, pares=regua.pares_d47(), janela=None)) == 27  # R6: protocolo antigo acessível


def test_nomes_unicos_e_deterministico():
    nomes = [m.nome for m in cb.MODELOS]
    assert len(nomes) == len(set(nomes))
    s = _serie(RETA + np.sin(np.arange(24)) * 10)
    m = cb.MODELOS[nomes.index("comb_mediana")]
    a = regua.prever_de(m, s, s.index[-1] + 1, 3)
    b = regua.prever_de(m, s, s.index[-1] + 1, 3)
    pd.testing.assert_frame_equal(a, b)
