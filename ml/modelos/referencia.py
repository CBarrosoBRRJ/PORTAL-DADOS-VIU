"""Referências simples (baseline oficial, D20): ML só fica se vencer a melhor destas no backtest.

Faixa p10-p90 pelos erros do próprio passado de treino (ml.regua.ModeloPontual).
"""

import math

import numpy as np

from ml.regua import ModeloPontual


class UltimoMes(ModeloPontual):
    nome, descricao = "ref_ultimo_mes", "repete o último mês fechado"

    def prever_ponto(self, hist, h):
        return [float(hist.iloc[-1])] * h


class Media(ModeloPontual):
    def __init__(self, n):
        self.n, self.nome, self.minimo_hist = n, f"ref_media_{n}m", n
        self.descricao = f"média dos últimos {n} meses"

    def prever_ponto(self, hist, h):
        return [float(hist.iloc[-self.n:].mean())] * h


class MesmoMesAnoAnterior(ModeloPontual):
    nome, descricao = "ref_mesmo_mes_ano_anterior", "o mesmo mês do ano anterior"
    minimo_hist = 12

    def prever_ponto(self, hist, h):
        # mês i à frente (1..h) = valor de 12 meses antes dele = hist[-12 + i - 1]
        return [float(hist.iloc[-12 + i - 1]) if len(hist) >= 13 - i else math.nan for i in range(1, h + 1)]


class TendenciaLinear(ModeloPontual):
    def __init__(self, n=6):
        self.n, self.nome, self.minimo_hist = n, f"ref_tendencia_{n}m", n
        self.descricao = f"reta dos últimos {n} meses, prolongada"

    def prever_ponto(self, hist, h):
        y = hist.iloc[-self.n:].to_numpy(dtype=float)
        a, b = np.polyfit(np.arange(len(y)), y, 1)
        return [max(0.0, a * (len(y) - 1 + i) + b) for i in range(1, h + 1)]


MODELOS = [UltimoMes(), Media(3), Media(6), MesmoMesAnoAnterior(), TendenciaLinear(6)]
