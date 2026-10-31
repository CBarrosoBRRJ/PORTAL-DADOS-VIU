"""ARIMAX (regressão com erros ARIMA, statsmodels SARIMAX) contra o ARIMA de mesma ordem sem exógenas.

Exógenas só de calendário, conhecidas antes do mês acontecer (ml.calendario.exogenas):
  dias_uteis  dias úteis do mês (feriados/recesso de app/expediente.py)
  fim_de_ano  1 em nov/dez
  ano_2026    degrau de patamar a partir de jan/2026
Nenhuma série entra como regressora da outra: com horizonte 2 e 3 a defasagem de 1 mês da outra série
já não é conhecida no momento da previsão, e a interface só recebe a própria série.

Escala log (log1p): o crescimento é multiplicativo, a previsão nunca fica negativa e a faixa fica assimétrica
(mais espaço para cima), como os dados. O valor devolvido é a mediana (expm1 da média em log), que é o ponto
que minimiza o erro absoluto (WAPE). Faixa p10-p90 = intervalo de 80% do próprio modelo, em log.

Regras do módulo:
  AX1 Exógena constante no treino (ex.: ano_2026 com treino só até 2025) sai do ajuste: não há como estimar
      seu efeito. Indicador (nov/dez, 2026) também sai se o seu valor raro aparece em menos de 2 meses.
  AX2 Pares fixos ARIMA x ARIMAX com a MESMA ordem, para a comparação direta na tela.
  AX3 "auto": ordem (e, no ARIMAX, conjunto de exógenas) escolhida por validação de origem móvel DENTRO do
      treino recebido (últimas 6 origens, horizontes 1-3, WAPE): só meses anteriores à origem da régua.
  AX4 Falha numérica de um candidato: ele é descartado na escolha; se a ordem fixa falhar, cai para o passeio
      aleatório (0,1,0) com as mesmas exógenas.
  AX5 arimax_100_ct_fimdeano foi definido depois de olhar o backtest de 2026 (o ARIMAX completo perdeu e a
      decomposição mostrou que só nov/dez ajudava): o resultado dele é otimista e a tela precisa dizer.
"""

import warnings

import numpy as np
import pandas as pd

from ml.calendario import exogenas

TODAS = ("dias_uteis", "fim_de_ano", "ano_2026")
# candidatos da escolha "auto" (AX3): 3 ordens x 4 conjuntos = 12 ajustes por origem interna
CONJUNTOS_EXOG = ((), ("dias_uteis",), ("fim_de_ano",), TODAS)
# (ordem, tendência statsmodels): com d=1 "t" é deriva; com d=0 "ct" é nível + reta (em log = crescimento %)
ORDENS = (((0, 1, 1), "n"), ((1, 1, 0), "n"), ((1, 0, 0), "ct"))
Z80 = 0.2  # alpha do intervalo de 80%


def _rotulo(ordem, tendencia):
    p, d, q = ordem
    return f"{p}{d}{q}" + ("" if tendencia == "n" else "_" + tendencia)


def _matriz(indice, cols, d):
    """AX1: exógenas do treino que têm informação para estimar."""
    if not cols:
        return None, ()
    X = exogenas(indice)[list(cols)].astype(float)
    ficam = []
    for c in cols:
        v = X[c]
        if v.nunique() < 2:
            continue
        if c != "dias_uteis" and min((v == 1).sum(), (v == 0).sum()) < 2:
            continue
        ficam.append(c)
    return (X[ficam] if ficam else None), tuple(ficam)


def _ajustar_prever(y_log, ordem, tendencia, cols, h):
    """Ajusta SARIMAX em log e devolve (media_log, p10_log, p90_log) para h meses."""
    from statsmodels.tsa.statespace.sarimax import SARIMAX

    X, usadas = _matriz(y_log.index, cols, ordem[1])
    futuro = pd.period_range(y_log.index[-1] + 1, periods=h, freq="M")
    Xf = exogenas(futuro)[list(usadas)].astype(float) if usadas else None
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        mod = SARIMAX(y_log.to_numpy(), exog=None if X is None else X.to_numpy(), order=ordem, trend=tendencia)
        res = mod.fit(disp=False, maxiter=200)
        fc = res.get_forecast(h, exog=None if Xf is None else Xf.to_numpy())
        media = np.asarray(fc.predicted_mean, dtype=float)
        ic = np.asarray(fc.conf_int(alpha=Z80), dtype=float)
    if not np.all(np.isfinite(media)):
        raise FloatingPointError("previsão não finita")
    return media, ic[:, 0], ic[:, 1], usadas, res


def _wape_interno(y, ordem, tendencia, cols, n_origens=6, minimo=8, hmax=3):
    """AX3: WAPE da origem móvel dentro do treino (escala original)."""
    n = len(y)
    erro = soma = 0.0
    for i in range(max(minimo, n - n_origens), n):
        try:
            media, *_ = _ajustar_prever(np.log1p(y.iloc[:i]), ordem, tendencia, cols, hmax)
        except Exception:
            return np.inf
        reais = y.iloc[i:i + hmax].to_numpy()
        prev = np.expm1(media[:len(reais)])
        erro += np.abs(prev - reais).sum()
        soma += reais.sum()
    return erro / soma if soma else np.inf


class Arimax:
    """Regressão com erros ARIMA em log; cols=() é o ARIMA puro da mesma ordem."""

    def __init__(self, nome, ordem=(0, 1, 1), tendencia="n", cols=TODAS, auto=False, descricao=""):
        self.nome, self.ordem, self.tendencia, self.cols, self.auto = nome, ordem, tendencia, tuple(cols), auto
        self.descricao = descricao

    def _escolher(self, y):
        conjuntos = CONJUNTOS_EXOG if self.cols else ((),)
        melhor = (np.inf, ORDENS[0][0], ORDENS[0][1], ())
        for ordem, tend in ORDENS:
            for cols in conjuntos:
                w = _wape_interno(y, ordem, tend, cols)
                if w < melhor[0] - 1e-9:
                    melhor = (w, ordem, tend, cols)
        return melhor

    def fit(self, serie: pd.Series):
        self.serie_ = serie.astype(float)
        if self.auto:
            self.wape_interno_, self.ordem_, self.tendencia_, self.cols_ = self._escolher(self.serie_)
        else:
            self.ordem_, self.tendencia_, self.cols_ = self.ordem, self.tendencia, self.cols
        return self

    def predict(self, h: int) -> pd.DataFrame:
        y_log = np.log1p(self.serie_)
        try:
            media, lo, hi, self.usadas_, res = _ajustar_prever(y_log, self.ordem_, self.tendencia_, self.cols_, h)
        except Exception:  # AX4
            media, lo, hi, self.usadas_, res = _ajustar_prever(y_log, (0, 1, 0), "n", self.cols_, h)
        self.coef_ = dict(zip(res.model.param_names, np.asarray(res.params, dtype=float)))
        return pd.DataFrame({"valor": np.expm1(media), "p10": np.expm1(lo), "p90": np.expm1(hi)})


def _par(ordem, tendencia, texto):
    r = _rotulo(ordem, tendencia)
    return [Arimax(f"arima_{r}", ordem, tendencia, cols=(),
                   descricao=f"ARIMA{ordem}{' ' + texto if texto else ''} em log, sem variáveis externas"),
            Arimax(f"arimax_{r}", ordem, tendencia, cols=TODAS,
                   descricao=f"ARIMAX{ordem}{' ' + texto if texto else ''} em log + dias úteis, nov/dez e "
                             "degrau de 2026")]


MODELOS = [
    *_par((0, 1, 1), "n", ""),
    *_par((1, 1, 0), "n", ""),
    *_par((0, 1, 1), "t", "com deriva"),
    *_par((1, 0, 0), "ct", "com nível e reta"),
    # AX5 variante escolhida DEPOIS de ver o backtest de 2026 (decomposição por variável): resultado otimista
    Arimax("arimax_100_ct_fimdeano", (1, 0, 0), "ct", cols=("fim_de_ano",),
           descricao="ARIMAX(1,0,0) com nível e reta em log + só nov/dez; variável escolhida após ver o "
                     "backtest de 2026 (resultado otimista)"),
    Arimax("arima_auto", cols=(), auto=True,
           descricao="ARIMA em log; ordem escolhida por validação dentro do treino, sem variáveis externas"),
    Arimax("arimax_auto", cols=TODAS, auto=True,
           descricao="ARIMAX em log; ordem e variáveis externas escolhidas por validação dentro do treino "
                     "(pode escolher nenhuma)"),
]
