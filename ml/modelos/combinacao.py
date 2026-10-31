"""Referências bem ajustadas e combinações de métodos simples e clássicos (especialista "combinação").

Componentes (todos com hiperparâmetros escolhidos só dentro do histórico recebido, sem olhar o futuro):
  ses        suavização exponencial simples; alfa pelo menor erro de 1 passo no próprio treino
  holt_amort Holt com tendência amortecida (alfa, beta, phi pelo menor erro de 1 passo no treino)
  theta      método Theta (SES + metade da inclinação da reta; Assimakopoulos & Nikolopoulos, 2000)
  drift      último mês + inclinação média dos últimos 12 meses (passeio aleatório com deriva)
  sazonal    patamar recente (média 3m) x índice do mesmo mês do ano anterior sobre os 3 meses que
             antecederam a origem um ano antes (sazonal ajustado ao patamar; só 1 ano de sinal)
  media3 / ultimo   referências simples (as mesmas da régua), para entrar na combinação

Combinações:
  comb_mediana   mediana dos 6 componentes não sazonais — DECLARADO A PRIORI como o candidato principal
                 desta família (a mediana é robusta a um componente que erra muito; evidência das
                 competições M3/M4: combinações simples batem a maioria dos métodos isolados)
  comb_media     média de ses, holt_amort e theta (o trio clássico)
  comb_selecao   escolhe, em cada origem, o componente com menor WAPE num backtest interno dos últimos
                 6 meses do treino (horizontes 1 a 3)
  comb_ponderada média ponderada pelo inverso do WAPE desse mesmo backtest interno

D48 (janela de 12 meses): drift e drift_log usam a janela inteira (os 12 meses); sazonal não se aplica (R4).

Faixa p10-p90: empírica, pelos erros do próprio passado de treino (ml.regua.ModeloPontual).
Determinístico: não há sorteio.
"""

import math

import numpy as np

from ml.regua import ModeloPontual

GRADE_ALFA = np.round(np.arange(0.05, 1.0001, 0.05), 2)
GRADE_BETA = (0.05, 0.1, 0.2, 0.3)
GRADE_PHI = (0.8, 0.9, 0.98)


# ---------------------------------------------------------------- componentes: f(y: np.ndarray, h) -> list[float]

def _ses_ajuste(y):
    """(alfa, nível final) com menor soma de erros quadráticos de 1 passo; nível inicial = 1º valor."""
    melhor = (math.inf, 1.0, float(y[-1]))
    for a in GRADE_ALFA:
        nivel, sse = float(y[0]), 0.0
        for v in y[1:]:
            sse += (v - nivel) ** 2
            nivel = a * v + (1 - a) * nivel
        if sse < melhor[0] - 1e-9:
            melhor = (sse, float(a), nivel)
    return melhor[1], melhor[2]


def ses(y, h):
    _, nivel = _ses_ajuste(y)
    return [nivel] * h


def holt_amort(y, h):
    return [max(0.0, v) for v in _holt_bruto(np.asarray(y, dtype=float), h)]


def holt_amort_log(y, h):
    """Holt amortecido sobre log(y): tendência multiplicativa amortecida."""
    return [float(np.exp(v)) for v in _holt_bruto(np.log(np.maximum(y, 1.0)), h)]


def _holt_bruto(y, h):
    """Holt com tendência amortecida; inicial: nível = y0, tendência = inclinação média dos 3 primeiros meses."""
    if len(y) < 4:
        return [float(y[-1])] * h
    t0 = (y[3] - y[0]) / 3.0
    melhor = (math.inf, None)
    for a in GRADE_ALFA[::2]:
        for b in GRADE_BETA:
            for phi in GRADE_PHI:
                nivel, tend, sse = float(y[0]), float(t0), 0.0
                for v in y[1:]:
                    prev = nivel + phi * tend
                    sse += (v - prev) ** 2
                    novo = a * v + (1 - a) * prev
                    tend = b * (novo - nivel) + (1 - b) * phi * tend
                    nivel = novo
                if sse < melhor[0] - 1e-9:
                    melhor = (sse, (nivel, tend, phi))
    nivel, tend, phi = melhor[1]
    return [nivel + tend * sum(phi ** j for j in range(1, k + 1)) for k in range(1, h + 1)]


def theta(y, h):
    """Theta clássico (Hyndman & Billah, 2003): SES + b0/2 * ((k-1) + 1/a - (1-a)^n / a)."""
    n = len(y)
    a, nivel = _ses_ajuste(y)
    b0 = np.polyfit(np.arange(n), y, 1)[0]
    return [max(0.0, nivel + b0 / 2 * ((k - 1) + 1 / a - (1 - a) ** n / a)) for k in range(1, h + 1)]


def drift(y, h, janela=12):
    w = y[-janela:]
    inc = (w[-1] - w[0]) / (len(w) - 1) if len(w) > 1 else 0.0
    return [max(0.0, float(y[-1]) + inc * k) for k in range(1, h + 1)]


def sazonal(y, h):
    """Patamar recente x índice do mesmo mês um ano antes; sem 12+3 meses de histórico, cai na média 3m."""
    patamar = float(np.mean(y[-3:]))
    n = len(y)
    if n < 15:
        return [patamar] * h
    base_ano_ant = float(np.mean(y[n - 15:n - 12]))  # os 3 meses que antecederam a origem, um ano antes
    if base_ano_ant <= 0:
        return [patamar] * h
    return [patamar * float(y[n - 12 + k - 1]) / base_ano_ant for k in range(1, h + 1)]


def drift_log(y, h, janela=12):
    """Crescimento geométrico médio dos últimos 12 meses, a partir do nível log médio dos 3 últimos meses."""
    w = np.log(np.maximum(y[-janela:], 1.0))
    inc = (w[-1] - w[0]) / (len(w) - 1) if len(w) > 1 else 0.0
    base = float(np.mean(w[-3:]))  # centro da janela de 3 meses fica 1 mês antes do último
    return [float(np.exp(base + inc * (k + 1))) for k in range(1, h + 1)]


def media3(y, h):
    return [float(np.mean(y[-3:]))] * h


def ultimo(y, h):
    return [float(y[-1])] * h


COMPONENTES = {"ses": ses, "holt_amort": holt_amort, "theta": theta, "drift": drift, "media3": media3,
               "ultimo": ultimo, "sazonal": sazonal, "drift_log": drift_log, "holt_amort_log": holt_amort_log}
MULTIPLICATIVOS = ("drift_log", "holt_amort_log", "theta", "ses")
NAO_SAZONAIS = ("ses", "holt_amort", "theta", "drift", "media3", "ultimo")
TRIO_CLASSICO = ("ses", "holt_amort", "theta")


def _wape_interno(y, nomes, origens=6, hmax=3, minimo=6):
    """WAPE de cada componente num backtest de origem móvel DENTRO de y (últimas `origens` origens)."""
    n = len(y)
    erro = {c: 0.0 for c in nomes}
    soma = 0.0
    for i in range(max(minimo, n - origens), n):
        alvos = y[i:i + hmax]
        soma += float(np.sum(alvos))
        for c in nomes:
            p = np.asarray(COMPONENTES[c](y[:i], hmax)[:len(alvos)])
            erro[c] += float(np.sum(np.abs(p - alvos)))
    return {c: (erro[c] / soma if soma else math.nan) for c in nomes}


# ---------------------------------------------------------------- modelos registrados

class Componente(ModeloPontual):
    def __init__(self, chave, descricao, minimo_treino=0, motivo_minimo=""):
        self.chave, self.nome, self.descricao = chave, f"comb_{chave}", descricao
        self.minimo_treino, self.motivo_minimo = minimo_treino, motivo_minimo  # régua R4 (D48)

    def prever_ponto(self, hist, h):
        return COMPONENTES[self.chave](hist.to_numpy(dtype=float), h)


class Combinacao(ModeloPontual):
    def __init__(self, nome, descricao, nomes, modo):
        self.nome, self.descricao, self.nomes, self.modo = nome, descricao, tuple(nomes), modo

    def prever_ponto(self, hist, h):
        y = hist.to_numpy(dtype=float)
        prev = np.array([COMPONENTES[c](y, h) for c in self.nomes])  # componentes x h
        if self.modo == "mediana":
            return list(np.median(prev, axis=0))
        if self.modo == "media":
            return list(prev.mean(axis=0))
        w = _wape_interno(y, self.nomes)
        if self.modo == "selecao":
            validos = {c: v for c, v in w.items() if np.isfinite(v)}
            if not validos:
                return list(np.median(prev, axis=0))
            escolhido = min(validos, key=lambda c: (validos[c], self.nomes.index(c)))
            return list(prev[self.nomes.index(escolhido)])
        if self.modo == "ponderada":
            pesos = np.array([1 / max(w[c], 1e-6) if np.isfinite(w[c]) else 0.0 for c in self.nomes])
            if pesos.sum() == 0:
                return list(prev.mean(axis=0))
            return list(pesos @ prev / pesos.sum())
        raise ValueError(self.modo)


def _fator_vies(y, f, h, origens=6, minimo=6):
    """Por horizonte: mediana de real / previsto num backtest interno das últimas `origens` origens de y.

    Só usa o passado de y; com menos de 3 razões no horizonte, fator 1 (sem correção)."""
    n = len(y)
    razoes = {k: [] for k in range(1, h + 1)}
    for i in range(max(minimo, n - origens - h + 1), n):
        p = f(y[:i], h)
        for k in range(1, h + 1):
            j = i + k - 1
            if j < n and p[k - 1] > 0:
                razoes[k].append(y[j] / p[k - 1])
    return [float(np.median(razoes[k])) if len(razoes[k]) >= 3 else 1.0 for k in range(1, h + 1)]


class Corrigido(ModeloPontual):
    """Previsão do método-base x mediana de real/previsto nas últimas 6 origens do próprio treino."""

    def __init__(self, nome, descricao, base):
        self.nome, self.descricao, self.base = nome, descricao, base

    def _f(self, y, h):
        return self.base.prever_ponto_y(y, h)

    def prever_ponto(self, hist, h):
        y = hist.to_numpy(dtype=float)
        p = self._f(y, h)
        return [v * c for v, c in zip(p, _fator_vies(y, self._f, h))]


def _ponto(self, y, h):
    import pandas as pd  # noqa: PLC0415 - só para reaproveitar prever_ponto com np.ndarray
    return self.prever_ponto(pd.Series(y), h)


Componente.prever_ponto_y = _ponto
Combinacao.prever_ponto_y = _ponto


MODELOS = [
    Componente("ses", "suavização exponencial simples (alfa ajustado no próprio passado)"),
    Componente("holt_amort", "Holt com tendência amortecida (parâmetros ajustados no próprio passado)"),
    Componente("theta", "método Theta: suavização + metade da tendência"),
    Componente("drift", "último mês + crescimento médio dos últimos 12 meses"),
    # D48: com a janela de 12 meses, o índice do mesmo mês um ano antes (12 + 3 meses) não existe: cairia sempre na
    # média 3m (cópia de ref_media_3m). Fica registrado como "não se aplica" (régua R4).
    Componente("sazonal", "patamar dos últimos 3 meses x efeito do mesmo mês no ano anterior", minimo_treino=15,
               motivo_minimo="o efeito do mesmo mês do ano anterior precisa de 15 meses (12 + os 3 que antecedem)"),
    Combinacao("comb_mediana", "mediana de 6 métodos simples e clássicos (candidato principal da família)",
               NAO_SAZONAIS, "mediana"),
    Combinacao("comb_media", "média de suavização, Holt amortecido e Theta", TRIO_CLASSICO, "media"),
    Combinacao("comb_selecao", "o método que mais acertou nos últimos 6 meses do próprio passado",
               NAO_SAZONAIS, "selecao"),
    Combinacao("comb_ponderada", "média dos 6 métodos com peso maior para quem errou menos no passado recente",
               NAO_SAZONAIS, "ponderada"),
    # segunda rodada (desenhada DEPOIS de ver que a 1ª subestimava sempre; ver limites na docstring)
    Componente("drift_log", "crescimento percentual médio dos últimos 12 meses"),
    Componente("holt_amort_log", "Holt amortecido em escala log (crescimento percentual amortecido)"),
    Combinacao("comb_mediana_mult", "mediana de suavização, Theta e dois métodos de crescimento percentual",
               MULTIPLICATIVOS, "mediana"),
    Corrigido("comb_mediana_corr", "mediana de 6 métodos x correção do viés recente do próprio passado",
              Combinacao("_m", "", NAO_SAZONAIS, "mediana")),
    Corrigido("comb_theta_corr", "Theta x correção do viés recente do próprio passado",
              Componente("theta", "")),
]
