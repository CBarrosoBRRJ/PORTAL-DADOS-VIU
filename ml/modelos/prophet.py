"""Especialista Prophet: tendência por partes (changepoints) + sazonalidade anual fraca, faixa do próprio Prophet.

D48 (26/10/2026): com a janela de 12 meses, a sazonalidade anual (Fourier) só entra com 24 meses ou mais (2 ciclos);
as variantes que dependem dela (prophet_log, prophet_natural, prophet_log_degrau2026) ficam "não se aplica" (régua R4)
e o prophet_auto escolhe só entre as configurações sem sazonalidade.

Por que assim (desenho original, com 13 a 23 meses de treino):
  - Tendência linear por partes com um changepoint candidato por mês (até 90% do histórico) e prior de Laplace
    (changepoint_prior_scale) que encolhe as mudanças: a mudança de patamar de 2026 entra como dobra da
    tendência quando os dados mostram, sem data marcada à mão.
  - Sazonalidade anual só como Fourier de ordem 2 com prior estreito (há no máximo 2 ciclos; o fim de ano só
    aparece em 2025, com datas estimadas - PD10). Prophet não liga a anual sozinho com < 2 anos.
  - Escala log (log1p) como opção: crescimento proporcional e faixa assimétrica (não fica negativa).
  - Faixa p10-p90 = interval_width 0.8 do Prophet (incerteza da tendência + ruído), com semente fixa.
  - prophet_auto escolhe escala, rigidez da tendência e sazonalidade por validação DENTRO do treino de cada
    origem (últimas origens internas, h 1-3, WAPE). Nada de 2026 avaliado entra na escolha da própria origem.
"""

import itertools
import logging

import numpy as np
import pandas as pd

from ml import calendario

logging.getLogger("cmdstanpy").setLevel(logging.ERROR)
logging.getLogger("prophet").setLevel(logging.ERROR)

SEMENTE = 20261025
MESES_SAZONAL = 24  # D48: termo anual só com 2 ciclos completos (antes: 12, um único ciclo)


def _ds(idx: pd.PeriodIndex) -> pd.Series:
    return pd.Series(idx.to_timestamp(how="start"))


class ProphetMensal:
    """Uma configuração fixa do Prophet para série mensal de pedidos."""

    def __init__(self, nome, escala="log", cps=0.1, sazonal=True, sazonal_prior=0.1, degrau_2026=False,
                 amostras=1000, descricao=None):
        self.nome, self.escala, self.cps = nome, escala, cps
        self.sazonal, self.sazonal_prior, self.degrau_2026 = sazonal, sazonal_prior, degrau_2026
        # D48 (régua R4): a anual precisa de 2 ciclos; com a janela de 12 meses a variante sazonal "não se aplica"
        self.minimo_treino = MESES_SAZONAL if sazonal else 0
        self.motivo_minimo = "a sazonalidade anual precisa de 2 ciclos completos (24 meses)" if sazonal else ""
        self.amostras = amostras
        self.descricao = descricao or (
            f"Prophet, escala {'log' if escala == 'log' else 'natural'}, tendência por partes "
            f"(prior {cps}){', anual fraca' if sazonal else ''}{', degrau 2026' if degrau_2026 else ''}")

    # --- transformação -------------------------------------------------------------------------------------
    def _ida(self, y):
        return np.log1p(y) if self.escala == "log" else np.asarray(y, dtype=float)

    def _volta(self, y):
        return np.expm1(y) if self.escala == "log" else np.asarray(y, dtype=float)

    # --- contrato ------------------------------------------------------------------------------------------
    def fit(self, serie: pd.Series):
        from prophet import Prophet

        logging.getLogger("cmdstanpy").setLevel(logging.ERROR)
        self.ultimo_ = serie.index[-1]
        n = len(serie)
        df = pd.DataFrame({"ds": _ds(serie.index), "y": self._ida(serie.to_numpy(dtype=float))})
        # um changepoint candidato por mês, do 3º mês até 90% do histórico
        fim = max(3, int(np.floor(0.9 * n)))
        cps = list(df["ds"].iloc[2:fim])
        self.usa_degrau_ = self.degrau_2026 and int((serie.index.year >= 2026).sum()) >= 3
        m = Prophet(growth="linear", changepoints=cps or None, n_changepoints=0 if not cps else len(cps),
                    changepoint_prior_scale=self.cps, yearly_seasonality=False, weekly_seasonality=False,
                    daily_seasonality=False, interval_width=0.8, uncertainty_samples=self.amostras)
        if self.sazonal and n >= MESES_SAZONAL:
            m.add_seasonality("anual", period=365.25, fourier_order=2, prior_scale=self.sazonal_prior)
        if self.usa_degrau_:
            df["ano_2026"] = calendario.exogenas(serie.index)["ano_2026"].to_numpy()
            m.add_regressor("ano_2026", prior_scale=1.0, standardize=False)
        m.fit(df)
        self.m_ = m
        return self

    def predict(self, h: int) -> pd.DataFrame:
        futuro_idx = pd.period_range(self.ultimo_ + 1, periods=h, freq="M")
        f = pd.DataFrame({"ds": _ds(futuro_idx)})
        if self.usa_degrau_:
            f["ano_2026"] = calendario.exogenas(futuro_idx)["ano_2026"].to_numpy()
        np.random.seed(SEMENTE)  # amostragem da faixa usa o gerador global do numpy
        p = self.m_.predict(f)
        nada = np.full(len(p), np.nan)  # uncertainty_samples=0 (validação interna): sem faixa
        return pd.DataFrame({"valor": self._volta(p["yhat"].to_numpy()),
                             "p10": self._volta(p["yhat_lower"].to_numpy()) if "yhat_lower" in p else nada,
                             "p90": self._volta(p["yhat_upper"].to_numpy()) if "yhat_upper" in p else nada,
                             }).clip(lower=0)


class ProphetAuto:
    """Escolhe a configuração do Prophet por validação de origem móvel dentro do treino recebido."""

    nome = "prophet_auto"
    descricao = ("Prophet com escala, rigidez da tendência e sazonalidade escolhidas por validação no próprio "
                 "passado de cada origem")
    GRADE = {"escala": ("log", "natural"), "cps": (0.02, 0.1, 0.5), "sazonal": (False, True)}

    def __init__(self, origens_internas=4, minimo_treino=10):
        self.origens_internas, self.minimo_treino = origens_internas, minimo_treino

    def _validar(self, serie, cfg):
        erros, soma = 0.0, 0.0
        n = len(serie)
        for i in range(max(self.minimo_treino, n - self.origens_internas - 2), n):
            m = ProphetMensal("v", amostras=0, **cfg).fit(serie.iloc[:i])
            prev = m.predict(3)["valor"].to_numpy()
            for k in range(3):
                if i + k < n:
                    erros += abs(prev[k] - serie.iloc[i + k])
                    soma += serie.iloc[i + k]
        return erros / soma if soma else np.inf

    def fit(self, serie: pd.Series):
        grade = [dict(zip(self.GRADE, v)) for v in itertools.product(*self.GRADE.values())]
        if len(serie) < MESES_SAZONAL:  # D48: com a janela de 12 meses, só as configurações sem sazonalidade
            grade = [g for g in grade if not g["sazonal"]]
        if len(serie) < self.minimo_treino + 2:
            self.escolha_, self.wape_interno_ = {"escala": "log", "cps": 0.1, "sazonal": False}, None
        else:
            notas = [(self._validar(serie, c), j) for j, c in enumerate(grade)]
            nota, j = min(notas)
            self.escolha_, self.wape_interno_ = grade[j], float(nota)
        self.m_ = ProphetMensal("escolhido", **self.escolha_).fit(serie)
        return self

    def predict(self, h: int) -> pd.DataFrame:
        return self.m_.predict(h)


MODELOS = [
    ProphetMensal("prophet_log", escala="log", cps=0.1, sazonal=True),
    ProphetMensal("prophet_natural", escala="natural", cps=0.1, sazonal=True),
    ProphetMensal("prophet_log_sem_sazonal", escala="log", cps=0.1, sazonal=False),
    ProphetMensal("prophet_log_degrau2026", escala="log", cps=0.1, sazonal=True, degrau_2026=True),
    ProphetAuto(),
]
