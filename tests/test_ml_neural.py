"""Rede neural da previsão (ml/modelos/neural.py) com séries sintéticas, sem BigQuery."""

import numpy as np
import pandas as pd

from ml import regua
from ml.modelos import neural


def _serie(valores, inicio="2024-10", nome="Sintetica"):
    return pd.Series([float(v) for v in valores], index=pd.period_range(inicio, periods=len(valores), freq="M"),
                     name=nome)


CRESCE = _serie([100 * 1.03 ** i for i in range(24)])


def test_varredura_registra_um_nome_por_tamanho():
    nomes = [m.nome for m in neural.MODELOS]
    assert len(nomes) == len(set(nomes))
    for n in ("mlp_1", "mlp_2", "mlp_3", "mlp_4", "mlp_5", "mlp_8", "mlp_12", "mlp_16", "mlp_4x2", "mlp_auto"):
        assert n in nomes


def test_previsao_reprodutivel_e_com_faixa():
    m1 = neural.RedeNeural((2,)).fit(CRESCE)
    m2 = neural.RedeNeural((2,)).fit(CRESCE)
    p1, p2 = m1.predict(3), m2.predict(3)
    pd.testing.assert_frame_equal(p1, p2)  # sementes fixas
    assert len(p1) == 3 and (p1["valor"] > 0).all()
    # faixa pelos erros do passado: numa série que só cresce, pode ficar toda acima do ponto (sempre subestimou)
    assert (p1["p10"] <= p1["p90"]).all() and p1[["p10", "p90"]].notna().all().all()


def test_serie_sintetica_nao_usa_snapshot():
    assert neural.outras_series(CRESCE) == []


def test_serie_constante_preve_perto_do_nivel():
    s = _serie([200.0] * 20)
    v = neural.RedeNeural((3,)).fit(s).predict(2)["valor"]
    assert np.allclose(v, 200.0, rtol=0.05)


def test_auto_escolhe_so_com_o_treino():
    m = neural.RedeNeuralAuto(grade=((1,), (2,)), origens=2, sementes=(0,))
    treino = CRESCE.iloc[:14]
    m.fit(treino)
    assert set(m.validacao_) == {"mlp_1", "mlp_2"}
    assert m.escolha_ in m.validacao_
    assert neural.ESCOLHAS[-1]["origem"] == str(treino.index[-1] + 1)
    assert len(regua.prever_de(m, CRESCE, CRESCE.index[14], 3)) == 3


def test_outra_serie_cortada_na_origem():
    """N3: com dados globais, a outra série nunca passa do último mês do treino."""
    a, b = _serie(range(50, 74), nome="A"), _serie(range(80, 104), nome="B")
    m = neural.RedeNeural((1,), sementes=(0,))
    m.outras_ = [b]
    vistos = []
    original = neural._exemplos

    def espiao(serie, k):
        vistos.append(serie.index[-1])
        return original(serie, k)

    neural._exemplos = espiao
    try:
        m._prever(a.iloc[:12], 1, (1,))
    finally:
        neural._exemplos = original
    assert max(vistos) == a.index[11]
