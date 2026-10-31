"""Gradient boosting (LightGBM / XGBoost) para pedidos por mês — especialista de ML.

DESENHO (série curta e crescente: 13 a 23 meses por origem)
  - Árvores não extrapolam: prever o NÚMERO de pedidos com árvore travaria no maior valor do treino. Por isso o
    alvo é a RAZÃO em log entre o mês-alvo e o nível recente:  alvo = log(y[t+k-1] / nivel_t),
    nivel_t = média dos 3 últimos meses conhecidos na origem t. A escala vem do nível; a árvore só aprende o
    crescimento típico, o efeito do mês e o "momento" da série. Previsão = nivel_t x exp(razão prevista).
  - Previsão DIRETA para h = 1..3, com o horizonte k como feature (uma tabela única empilha os três
    horizontes: ~27 linhas na primeira origem, ~51 na última).
  - Features, todas conhecidas na origem: razões log de lag 1, 2, 3 sobre o nível; mesmo mês do ano anterior
    sobre o nível (lag 12 em relação ao alvo; NaN quando não há); momento log(média 3m / média 6m); mês do
    alvo; dias úteis do alvo e nov/dez (ml.calendario.exogenas); horizonte.
  - Regularização forte: árvores de profundidade 2, no mínimo 4 linhas por folha, L2 = 5, taxa 0,05,
    60 árvores, razão prevista limitada a [-1, 1] em log (x0,37 a x2,7 do nível).
  - Faixa p10-p90: pelos erros do próprio passado de treino (ml.regua.ModeloPontual), sem vazamento.
  - boost_lgbm_n1: mesma receita com a âncora = último mês (a melhor referência do Mercado). Variante
    acrescentada DEPOIS de ver o 1º resultado da régua (boost_lgbm/xgb com média 3m): registrada com nome
    próprio para a tela não esconder isso.
  - boost_auto escolhe, DENTRO do treino de cada origem (validação de origem móvel nas 4 últimas origens do
    próprio treino, WAPE nos horizontes 1-3), entre LightGBM (âncora 3m ou 1m), XGBoost (3m) e a própria
    âncora sem árvore (média 3m ou último mês). Nada posterior à origem entra na escolha.
  - Determinismo: random_state fixo, 1 thread.
  - D48 (janela de 12 meses): o "mesmo mês do ano anterior" (r12) nunca existe nas linhas de treino (precisaria de
    13+ meses); a coluna fica vazia no treino e as árvores não a usam. O modelo segue válido com as demais features
    (cerca de 24 linhas por origem: 9 + 8 + 7 nos horizontes 1–3).
"""

import math
import warnings

import numpy as np
import pandas as pd

from ml.calendario import exogenas
from ml.regua import ModeloPontual

NIVEL_N = 3
LIMITE_LOG = 1.0
SEMENTE = 42
COLUNAS = ["k", "r1", "r2", "r3", "r12", "momento", "mes", "dias_uteis", "fim_de_ano"]


def _nivel(y: np.ndarray, i: int, nivel_n: int = NIVEL_N) -> float:
    return float(np.mean(y[i - nivel_n:i]))


def _log_razao(v: float, nivel: float) -> float:
    return math.log(max(v, 1.0) / max(nivel, 1.0))


def _features(y: np.ndarray, meses: pd.PeriodIndex, i: int, k: int, exo: pd.DataFrame,
              nivel_n: int = NIVEL_N) -> dict:
    """Linha de features na origem i (meses 0..i-1 conhecidos) para o alvo i+k-1."""
    nivel = _nivel(y, i, nivel_n)
    alvo = meses[0] + (i + k - 1)
    j12 = i + k - 1 - 12
    m6 = float(np.mean(y[i - 6:i])) if i >= 6 else math.nan
    return {
        "k": k,
        "r1": _log_razao(y[i - 1], nivel),
        "r2": _log_razao(y[i - 2], nivel),
        "r3": _log_razao(y[i - 3], nivel),
        "r12": _log_razao(y[j12], nivel) if 0 <= j12 < i else math.nan,
        "momento": math.log(max(nivel, 1.0) / max(m6, 1.0)) if i >= 6 else math.nan,
        "mes": alvo.month,
        "dias_uteis": float(exo.loc[alvo, "dias_uteis"]),
        "fim_de_ano": float(exo.loc[alvo, "fim_de_ano"]),
    }


def _tabela(hist: pd.Series, hmax: int, nivel_n: int = NIVEL_N):
    """Linhas de treino (todas as origens i com nível e alvo conhecidos) e linhas da previsão (origem n)."""
    y = hist.to_numpy(dtype=float)
    n = len(y)
    meses = hist.index
    exo = exogenas(pd.period_range(meses[0], periods=n + hmax, freq="M"))
    treino, alvos = [], []
    for k in range(1, hmax + 1):
        for i in range(NIVEL_N, n - k + 1):
            treino.append(_features(y, meses, i, k, exo, nivel_n))
            alvos.append(_log_razao(y[i + k - 1], _nivel(y, i, nivel_n)))
    futuro = [_features(y, meses, n, k, exo, nivel_n) for k in range(1, hmax + 1)]
    return (pd.DataFrame(treino, columns=COLUNAS), np.array(alvos),
            pd.DataFrame(futuro, columns=COLUNAS), _nivel(y, n, nivel_n))


def _lgbm():
    from lightgbm import LGBMRegressor
    return LGBMRegressor(n_estimators=60, learning_rate=0.05, max_depth=2, num_leaves=3, min_child_samples=4,
                         min_data_in_bin=1, reg_lambda=5.0, subsample=1.0, colsample_bytree=1.0,
                         random_state=SEMENTE, n_jobs=1, deterministic=True, force_row_wise=True, verbose=-1)


def _xgb():
    from xgboost import XGBRegressor
    return XGBRegressor(n_estimators=60, learning_rate=0.05, max_depth=2, min_child_weight=4, reg_lambda=5.0,
                        subsample=1.0, colsample_bytree=1.0, tree_method="exact", random_state=SEMENTE,
                        n_jobs=1, verbosity=0)


FABRICAS = {"lgbm": _lgbm, "xgb": _xgb}


_CACHE: dict = {}
_CACHE_MAX = 50_000


def prever_boost(hist: pd.Series, h: int, motor: str, nivel_n: int = NIVEL_N) -> list[float]:
    """Memoizado: função pura do histórico (valores + 1º mês), do motor e da âncora; evita reajustar o mesmo
    prefixo milhares de vezes na validação interna (e o MemoryError do LightGBM em ajustes repetidos)."""
    chave = (str(hist.index[0]) if len(hist) else "", hist.to_numpy(dtype=float).tobytes(), h, motor, nivel_n)
    if chave not in _CACHE:
        if len(_CACHE) >= _CACHE_MAX:
            _CACHE.clear()
        _CACHE[chave] = _prever_boost(hist, h, motor, nivel_n)
    return list(_CACHE[chave])


def _prever_boost(hist: pd.Series, h: int, motor: str, nivel_n: int = NIVEL_N) -> list[float]:
    """Treina o motor ("lgbm", "xgb" ou "nivel") só com hist e prevê h meses (previsão direta).

    nivel_n = meses da âncora (3 = média 3m; 1 = último mês).
    """
    hmax = max(h, 3)
    X, alvo, Xf, nivel = _tabela(hist, hmax, nivel_n)
    if motor == "nivel" or len(alvo) < 8:
        return [nivel] * h
    m = FABRICAS[motor]()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        m.fit(X, alvo)
        r = np.clip(m.predict(Xf), -LIMITE_LOG, LIMITE_LOG)
    del m
    return [float(nivel * math.exp(v)) for v in r[:h]]


CANDIDATOS_AUTO = (("lgbm", 3), ("lgbm", 1), ("xgb", 3), ("nivel", 3), ("nivel", 1))


def escolher_motor(hist: pd.Series, candidatos=CANDIDATOS_AUTO, origens: int = 4,
                   hmax: int = 3, minimo: int = 10) -> tuple[tuple, dict]:
    """Validação de origem móvel DENTRO de hist: WAPE das últimas `origens` origens, horizontes 1..hmax."""
    n = len(hist)
    inicio = max(minimo, n - origens - hmax + 1)
    if n - inicio < 2:
        return candidatos[0], {}
    erros = {}
    for c in candidatos:
        soma_err = soma_real = 0.0
        for i in range(inicio, n):
            p = prever_boost(hist.iloc[:i], hmax, *c)
            for k in range(1, hmax + 1):
                j = i + k - 1
                if j < n:
                    soma_err += abs(p[k - 1] - float(hist.iloc[j]))
                    soma_real += float(hist.iloc[j])
        erros[c] = soma_err / soma_real if soma_real else math.inf
    return min(erros, key=erros.get), erros


class Boost(ModeloPontual):
    """Um motor fixo (lgbm ou xgb) com a faixa pelos erros do próprio passado."""

    minimo_hist = 8

    def __init__(self, motor: str, nivel_n: int = NIVEL_N):
        self.motor, self.nivel_n = motor, nivel_n
        self.nome = f"boost_{motor}" + ("" if nivel_n == NIVEL_N else f"_n{nivel_n}")
        rotulo = {"lgbm": "LightGBM", "xgb": "XGBoost"}[motor]
        ancora = "a média dos últimos 3 meses" if nivel_n == 3 else "o último mês fechado"
        self.descricao = (f"{rotulo} sobre a razão entre o mês e {ancora} (defasagens 1-3 e 12, "
                          "momento, mês, dias úteis, nov/dez); previsão direta de 1 a 3 meses")

    def prever_ponto(self, hist, h):
        return prever_boost(hist, h, self.motor, self.nivel_n)


class BoostAuto(ModeloPontual):
    """Escolhe o motor por validação dentro do treino de cada origem (inclui a opção sem árvore)."""

    nome = "boost_auto"
    descricao = ("LightGBM, XGBoost ou só a âncora (média 3m ou último mês) — escolhido em cada origem por "
                 "validação no próprio passado (4 últimas origens do treino)")
    minimo_hist = 8

    def prever_ponto(self, hist, h):
        motor, _ = escolher_motor(hist)
        return prever_boost(hist, h, *motor)

    def fit(self, serie):
        super().fit(serie)
        self.motor_, self.erros_validacao_ = escolher_motor(serie)
        return self


MODELOS = [Boost("lgbm"), Boost("xgb"), Boost("lgbm", 1), BoostAuto()]
