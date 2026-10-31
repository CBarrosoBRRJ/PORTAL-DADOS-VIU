"""Rede neural pequena (sklearn MLPRegressor) para pedidos por mês, com varredura do nº de neurônios.

Pedido do Caio: testar 1, 2, 3... neurônios e ver qual quantidade dá o melhor resultado.

COMO A REDE PREVÊ (N1–N7)
  N1 Janela: os últimos L = 3 meses. Escala = média da janela (+1). Entradas = log((mês + 1) / escala) dos 3
     meses e, para o mês-alvo, dias úteis ((d - 21) / 2) e fim de ano (nov/dez = 1). Só calendário conhecido de
     antemão (ml.calendario); nada do futuro.
  N2 Alvo: log((pedidos do mês-alvo + 1) / escala). A rede aprende o AJUSTE sobre a média dos últimos 3 meses:
     saída 0 = repetir a média 3m (a melhor referência do Inbound). Uma rede por horizonte (previsão direta
     de 1, 2 e 3 meses à frente), sem realimentar a própria previsão.
  N3 Dados de treino "globais": como a escala é tirada de cada janela, as janelas do Inbound e do Mercado
     falam a mesma língua e entram juntas (dobra os exemplos, que são 6 a 20 por série). A outra série é
     cortada no mesmo último mês do treino: nada posterior à origem entra. Se a série recebida não for a do
     snapshot (ex.: testes sintéticos), treina só com ela. D48: a outra série também é cortada no 1º mês da
     janela de 12 meses (mesmo período do treino recebido).
  N4 Rede: 1 camada oculta (ou 2 pequenas), tanh, solver lbfgs, regularização L2 (alpha = 0,3), até 1.000
     iterações. Early stopping do sklearn exige separar 10% dos exemplos para validação (1 ou 2 pontos aqui) e
     só vale para adam/sgd; no lugar dele, a L2 forte e o lbfgs com teto de iterações seguram o sobreajuste.
  N5 Estabilidade: média de 5 sementes fixas (0–4), em log; resultado reproduzível.
  N6 Varredura: uma variante por tamanho (mlp_1 ... mlp_16, mlp_4x2, mlp_8x4), cada uma passada pela régua.
     Essa tabela mostra neurônios x erro de 2026, mas ESCOLHER por ela seria olhar a prova.
  N7 Escolha honesta (mlp_auto): em cada origem, dentro do treino recebido, refaz as últimas 4 origens
     (horizontes 1–3, só a própria série) para cada tamanho da grade e fica com o de menor WAPE interno
     (empate até 0,5 p.p. = o menor). A faixa p10–p90 sai dos erros do próprio treino (ml.regua.ModeloPontual).

Parâmetros fixados a priori (antes de ver o backtest de 2026): L = 3, alpha = 0,3, 5 sementes, tanh, lbfgs,
4 origens de validação interna, dados globais ligados.
"""

import math
import warnings

import numpy as np
import pandas as pd
from sklearn.exceptions import ConvergenceWarning
from sklearn.neural_network import MLPRegressor

from ml import calendario
from ml.regua import HORIZONTES, ModeloPontual

GRADE = ((1,), (2,), (3,), (4,), (5,), (8,), (12,), (16,), (4, 2), (8, 4))
JANELA = 3
ALPHA = 0.3
SEMENTES = (0, 1, 2, 3, 4)
VALIDACAO_ORIGENS = 4
TOLERANCIA = 0.005

_SNAPSHOT: dict | None = None
ESCOLHAS: list[dict] = []  # registro do tamanho escolhido por mlp_auto em cada fit (para a tela e a ficha)


def rotulo(camadas: tuple) -> str:
    return "mlp_" + "x".join(str(c) for c in camadas)


def _snapshot() -> dict:
    global _SNAPSHOT
    if _SNAPSHOT is None:
        try:
            from ml.regua import carregar_series
            _SNAPSHOT, _ = carregar_series()
        except Exception:  # sem snapshot: treina só com a série recebida
            _SNAPSHOT = {}
    return _SNAPSHOT


def outras_series(serie: pd.Series) -> list[pd.Series]:
    """N3: as outras séries do snapshot, só se a recebida for mesmo a do snapshot (mesmos valores)."""
    snap = _snapshot()
    propria = snap.get(serie.name)
    if propria is None:
        return []
    comum = serie.index.intersection(propria.index)
    if len(comum) != len(serie) or not np.allclose(propria.loc[comum].to_numpy(), serie.to_numpy()):
        return []
    return [s for nome, s in snap.items() if nome != serie.name]


def _exog(meses: pd.PeriodIndex) -> np.ndarray:
    e = calendario.exogenas(meses)
    return np.column_stack([(e["dias_uteis"].to_numpy() - 21.0) / 2.0, e["fim_de_ano"].to_numpy(dtype=float)])


def _entrada(janela: np.ndarray):
    escala = janela.mean() + 1.0
    return np.log((janela + 1.0) / escala), escala


def _exemplos(serie: pd.Series, k: int):
    """N1/N2: pares (entradas, alvo) para o horizonte k, só com meses da própria série recebida."""
    v = serie.to_numpy(dtype=float)
    ex = _exog(serie.index)
    X, y = [], []
    for t in range(JANELA - 1, len(v) - k):
        x, escala = _entrada(v[t - JANELA + 1:t + 1])
        X.append(np.concatenate([x, ex[t + k]]))
        y.append(math.log((v[t + k] + 1.0) / escala))
    return X, y


class RedeNeural(ModeloPontual):
    minimo_hist = 9          # a faixa interna começa com >= 6 exemplos por horizonte na própria série
    origens_faixa = 12

    def __init__(self, camadas=(4,), globais=True, sementes=SEMENTES, alpha=ALPHA, nome=None):
        self.camadas, self.globais, self.sementes, self.alpha = tuple(camadas), globais, tuple(sementes), alpha
        self.nome = nome or rotulo(self.camadas)
        n = " + ".join(str(c) for c in self.camadas)
        self.descricao = (f"rede neural com {n} neurônio(s) sobre os últimos {JANELA} meses e o calendário; "
                          f"média de {len(self.sementes)} sementes")

    # -- núcleo ---------------------------------------------------------------------------------------
    def _dados(self, hist: pd.Series, k: int):
        X, y = _exemplos(hist, k)
        if self.globais:
            for outra in self.outras_:
                # D48: a outra série entra só dentro da mesma janela do treino (nem antes nem depois)
                Xo, yo = _exemplos(outra[(outra.index >= hist.index[0]) & (outra.index <= hist.index[-1])], k)
                X += Xo
                y += yo
        return np.asarray(X), np.asarray(y)

    def _prever(self, hist: pd.Series, h: int, camadas: tuple):
        v = hist.to_numpy(dtype=float)
        x, escala = _entrada(v[-JANELA:])
        futuros = _exog(pd.period_range(hist.index[-1] + 1, periods=h, freq="M"))
        saida = []
        for k in range(1, h + 1):
            X, y = self._dados(hist, k)
            if len(y) < 3:
                saida.append(float(v[-JANELA:].mean()))
                continue
            z = np.concatenate([x, futuros[k - 1]])[None, :]
            logs = []
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", ConvergenceWarning)
                for s in self.sementes:
                    rede = MLPRegressor(hidden_layer_sizes=camadas, activation="tanh", solver="lbfgs",
                                        alpha=self.alpha, max_iter=1000, random_state=s)
                    logs.append(float(rede.fit(X, y).predict(z)[0]))
            saida.append(max(0.0, escala * math.exp(float(np.mean(logs))) - 1.0))
        return saida

    def prever_ponto(self, hist, h):
        return self._prever(hist, h, self.camadas)

    def fit(self, serie):
        self.outras_ = outras_series(serie) if self.globais else []
        return super().fit(serie)


class RedeNeuralAuto(RedeNeural):
    """N7: escolhe o tamanho da rede só com o passado de cada origem."""

    def __init__(self, grade=GRADE, origens=VALIDACAO_ORIGENS, **kw):
        super().__init__(camadas=grade[0], nome="mlp_auto", **kw)
        self.grade, self.origens = tuple(grade), origens
        self.descricao = (f"rede neural; o nº de neurônios ({', '.join(rotulo(c)[4:] for c in self.grade)}) é "
                          f"escolhido em cada origem pelas últimas {origens} origens do próprio treino")

    def validar(self, serie: pd.Series) -> dict:
        """WAPE interno de cada tamanho da grade nas últimas `origens` origens do treino (horizontes 1–3)."""
        n, hmax = len(serie), max(HORIZONTES)
        tabela = {}
        for camadas in self.grade:
            erro = soma = 0.0
            for i in range(max(self.minimo_hist, n - self.origens), n):
                prev = self._prever(serie.iloc[:i], hmax, camadas)
                for k in HORIZONTES:
                    j = i + k - 1
                    if j < n:
                        erro += abs(prev[k - 1] - float(serie.iloc[j]))
                        soma += float(serie.iloc[j])
            tabela[rotulo(camadas)] = erro / soma if soma else math.nan
        return tabela

    def fit(self, serie):
        self.outras_ = outras_series(serie) if self.globais else []
        self.validacao_ = self.validar(serie)
        validos = [(w, c) for c, w in zip(self.grade, self.validacao_.values()) if np.isfinite(w)]
        if validos:
            melhor = min(w for w, _ in validos)
            # empate (até 0,5 p.p.) = a rede menor; a grade está em ordem de tamanho
            self.camadas = next(c for w, c in validos if w <= melhor + TOLERANCIA)
        self.escolha_ = rotulo(self.camadas)
        ESCOLHAS.append({"serie": serie.name, "origem": str(serie.index[-1] + 1), "escolha": self.escolha_,
                         "wape_interno": {c: round(w, 4) for c, w in self.validacao_.items()}})
        return ModeloPontual.fit(self, serie)


MODELOS = [RedeNeural(c) for c in GRADE] + [RedeNeuralAuto()]
