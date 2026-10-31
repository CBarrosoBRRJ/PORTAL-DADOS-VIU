"""Séries temporais clássicas (ETS / Holt amortecido, ARIMA, Theta) para pedidos por mês.

Escolhas para 13 a 24 meses de treino e a quebra de patamar de 2026:
  - Tudo em log (log1p): o crescimento de 2026 é multiplicativo (~2x) e a faixa fica assimétrica e nunca negativa.
    A volta é exp(.) - 1 (mediana da previsão, não a média; é o que o WAPE premia).
  - Sem sazonalidade: com menos de dois anos completos em todas as origens do backtest, um termo sazonal teria
    12 parâmetros para 1 ciclo; não é estimável. Fim de ano fica para o ARIMAX/ML (exógenas).
  - Ordens/estruturas escolhidas por AICc (corrige o AIC para amostra pequena) sobre o treino recebido; a variante
    "validado" escolhe o candidato pelo WAPE de um backtest interno feito SÓ dentro do treino (sem olhar 2026 à
    frente da origem).
  - Faixa p10-p90: intervalo de 80% do próprio modelo (em log). A variante "_faixa_erros" troca pela faixa dos erros
    do próprio passado (ml.regua.ModeloPontual), para comparar a calibragem.
"""

import math
import warnings

import numpy as np
import pandas as pd

from ml.regua import ModeloPontual

ALFA = 0.2  # intervalo de 80%


def _silencio():
    w = warnings.catch_warnings()
    w.__enter__()
    warnings.simplefilter("ignore")
    return w


# ---------------------------------------------------------------- candidatos: y (log) -> (media, lo, hi, aicc)

def _ets(y, h, trend=None, damped=False):
    from statsmodels.tsa.exponential_smoothing.ets import ETSModel
    w = _silencio()
    try:
        y = pd.Series(np.asarray(y, dtype=float), index=pd.RangeIndex(len(y)))
        m = ETSModel(y, error="add", trend=trend, damped_trend=damped).fit(disp=False, maxiter=2000)
        f = m.get_prediction(start=len(y), end=len(y) + h - 1).summary_frame(alpha=ALFA)
        return f["mean"].to_numpy(), f["pi_lower"].to_numpy(), f["pi_upper"].to_numpy(), float(m.aicc)
    finally:
        w.__exit__(None, None, None)


def _arima(y, h, order, trend):
    from statsmodels.tsa.arima.model import ARIMA
    w = _silencio()
    try:
        m = ARIMA(y, order=order, trend=trend).fit()
        f = m.get_forecast(h).summary_frame(alpha=ALFA)
        return f["mean"].to_numpy(), f["mean_ci_lower"].to_numpy(), f["mean_ci_upper"].to_numpy(), float(m.aicc)
    finally:
        w.__exit__(None, None, None)


def _theta(y, h):
    from statsmodels.tsa.forecasting.theta import ThetaModel
    w = _silencio()
    try:
        s = pd.Series(y, index=pd.RangeIndex(len(y)))
        m = ThetaModel(s, period=1, deseasonalize=False).fit()
        media = m.forecast(h).to_numpy()
        pi = m.prediction_intervals(h, alpha=ALFA)
        return media, pi["lower"].to_numpy(), pi["upper"].to_numpy(), math.nan
    finally:
        w.__exit__(None, None, None)


ETS_CANDIDATOS = {"ETS(A,N,N)": dict(trend=None), "ETS(A,A,N)": dict(trend="add"),
                  "ETS(A,Ad,N)": dict(trend="add", damped=True)}


def _arima_candidatos(n):
    """Ordens pequenas; nº de parâmetros <= n/4 (13 pontos -> até 3)."""
    out = {}
    for d in (0, 1):
        for p in range(3):
            for q in range(3):
                for trend in (("c",) if d == 0 else ("n", "t")):
                    k = p + q + (trend != "n") + 1  # + variância
                    if k <= max(2, n // 4):
                        out[f"ARIMA({p},{d},{q}){'+drift' if trend == 't' else ''}"] = ((p, d, q), trend)
    return out


def ets_aicc(y, h):
    melhor = None
    for nome, kw in ETS_CANDIDATOS.items():
        try:
            r = _ets(y, h, **kw)
        except Exception:
            continue
        if np.all(np.isfinite(r[0])) and (melhor is None or r[3] < melhor[1][3]):
            melhor = (nome, r)
    return melhor


def arima_aicc(y, h):
    melhor = None
    for nome, (order, trend) in _arima_candidatos(len(y)).items():
        try:
            r = _arima(y, h, order, trend)
        except Exception:
            continue
        if np.isfinite(r[3]) and np.all(np.isfinite(r[0])) and (melhor is None or r[3] < melhor[1][3]):
            melhor = (nome, r)
    return melhor


def holt_amortecido(y, h):
    return "ETS(A,Ad,N)", _ets(y, h, trend="add", damped=True)


def theta(y, h):
    return "Theta", _theta(y, h)


def combinado(y, h):
    """Mediana (em log) de ETS-AICc, ARIMA-AICc e Theta; faixa = mediana dos limites."""
    partes = [f(y, h) for f in (ets_aicc, arima_aicc, theta)]
    partes = [p for p in partes if p is not None]
    arr = [np.vstack([p[1][i] for p in partes]) for i in range(3)]
    return "+".join(p[0] for p in partes), tuple(np.median(a, axis=0) for a in arr) + (math.nan,)


CANDIDATOS = {"ets_aicc": ets_aicc, "arima_aicc": arima_aicc, "holt_amortecido": holt_amortecido,
              "theta": theta, "combinado": combinado}


def _validar(serie_log, candidatos, origens=6, minimo=10, hmax=3):
    """WAPE (na escala original) de cada candidato num backtest de origem móvel DENTRO do treino."""
    y = np.asarray(serie_log, dtype=float)
    n = len(y)
    erros = {c: [0.0, 0.0] for c in candidatos}
    for i in range(max(minimo, n - origens - hmax + 1), n):
        reais = np.expm1(y[i:i + hmax])
        for c in candidatos:
            try:
                prev = np.expm1(CANDIDATOS[c](y[:i], hmax)[1][0][:len(reais)])
            except Exception:
                erros[c][0] += math.inf
                continue
            erros[c][0] += float(np.abs(np.maximum(prev, 0) - reais).sum())
            erros[c][1] += float(reais.sum())
    wape = {c: (e / s if s else math.inf) for c, (e, s) in erros.items()}
    return min(wape, key=wape.get), wape


# ---------------------------------------------------------------- modelos registrados

class Classico:
    """Um candidato fixo (ou 'validado': escolhido no backtest interno) com faixa do próprio modelo."""

    def __init__(self, metodo, nome, descricao):
        self.metodo, self.nome, self.descricao = metodo, nome, descricao

    def fit(self, serie: pd.Series):
        y = np.log1p(serie.to_numpy(dtype=float))
        self.y_ = y
        if self.metodo == "validado":
            self.escolhido_, self.wape_interno_ = _validar(y, ["ets_aicc", "arima_aicc", "holt_amortecido",
                                                               "theta", "combinado"])
        else:
            self.escolhido_ = self.metodo
        return self

    def predict(self, h: int) -> pd.DataFrame:
        estrutura, (m, lo, hi, _) = CANDIDATOS[self.escolhido_](self.y_, h)
        self.estrutura_ = estrutura
        return pd.DataFrame({"valor": np.expm1(m), "p10": np.expm1(lo), "p90": np.expm1(hi)}).clip(lower=0)


class ClassicoFaixaErros(ModeloPontual):
    """Mesmo ponto do candidato, faixa pelos erros do próprio passado de treino (régua)."""
    minimo_hist = 10

    def __init__(self, metodo, nome, descricao):
        self.metodo, self.nome, self.descricao = metodo, nome, descricao

    def prever_ponto(self, hist, h):
        modelo = Classico(self.metodo, self.nome, "").fit(hist)
        return list(modelo.predict(h)["valor"].to_numpy())


MODELOS = [
    Classico("ets_aicc", "cls_ets_aicc", "ETS em log: nível, tendência ou tendência amortecida, escolhido por AICc"),
    Classico("holt_amortecido", "cls_holt_amortecido", "Holt com tendência amortecida, em log"),
    Classico("arima_aicc", "cls_arima_aicc", "ARIMA pequeno em log (p,q<=2, d<=1, drift), escolhido por AICc"),
    Classico("theta", "cls_theta", "método Theta (tendência linear + suavização exponencial), em log"),
    Classico("combinado", "cls_combinado", "mediana de ETS, ARIMA e Theta (em log)"),
    Classico("validado", "cls_validado",
             "candidato clássico escolhido pelo menor erro num backtest dentro do próprio treino"),
    ClassicoFaixaErros("arima_aicc", "cls_arima_aicc_faixa_erros",
                       "ARIMA pequeno em log escolhido por AICc; faixa pelos erros do próprio passado"),
    ClassicoFaixaErros("holt_amortecido", "cls_holt_amortecido_faixa_erros",
                       "Holt amortecido em log; faixa pelos erros do próprio passado"),
]
