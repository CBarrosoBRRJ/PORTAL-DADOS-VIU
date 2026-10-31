"""Comparação automática com o AutoTS (D55, 26/10/2026): uma biblioteca que treina muitos modelos e devolve o melhor.

Pedido do Caio: usar uma ferramenta de "AutoML" que treina todos os modelos e devolve o melhor (ele pensava no PyCaret,
que exige Python <= 3.11; o ambiente é 3.12). Usamos o AutoTS (versão em requirements-ml.txt), DENTRO da régua oficial
(ml/regua.py, protocolo D48): a régua chama fit() com os 12 meses anteriores a cada origem e o AutoTS só vê esse trecho.

COMO FUNCIONA (AT1–AT7)
  AT1 Busca por janela: em cada fit (uma origem da régua: jan–set/2026 e o futuro out/25–set/26), o AutoTS recebe só a
      série da janela (12 meses, uma série por vez, Inbound ou Mercado) e procura o melhor modelo para 1 mês à frente.
  AT2 Modelos procurados (LISTA, 19 famílias univariadas): ingênuos (constante, último valor, média, sazonal), GLM,
      GLS, ETS, ARIMA, componentes não observados, Kalman, Theta, ARDL, regressão linear básica, motivos (vizinhos
      parecidos), FFT, regressão por janela e por data. Cada família entra com várias combinações de parâmetros e de
      transformações (diferença, escala, retirada de tendência, corte de extremos...). Ficaram de fora: Prophet (já
      está no projeto, ml/modelos/prophet.py, e é lento), ARCH (pacote ausente) e os multivariados (uma série por vez).
  AT3 Escolha interna do AutoTS (sem olhar o futuro): validação "para trás" dentro da janela — o último mês da janela e
      mais 2 recortes anteriores (num_validations = 2), sempre 1 mês à frente; nota = erro absoluto médio (MAE), que
      numa série só ordena igual ao WAPE. Os 35% melhores da 1ª rodada passam pelas outras duas.
  AT4 Os 3 melhores: autots_1, autots_2 e autots_3 = o 1º, o 2º e o 3º colocados da busca daquela janela, no máximo um
      por família (três famílias diferentes). Por isso o modelo por trás de "autots_1" pode mudar de origem para origem:
      é a escolha automática, refeita a cada mês, como o mlp_auto da rede neural. Se o colocado falhar ao prever, vale o
      próximo da lista (registrado em `escolhas`).
  AT5 Previsão: o modelo escolhido é treinado de novo na janela inteira e prevê h meses (a régua pede até 3); faixa
      p10–p90 = intervalo de 80% do próprio AutoTS; sem valores negativos.
  AT6 Determinismo: cada busca num processo Python novo (no mesmo processo, repetir a busca da mesma janela mudava as
      notas: o AutoTS guarda estado entre execuções), sementes fixas (random, numpy e random_seed = 2026), n_jobs = 1 e
      SEM gerações genéticas
      (max_generations = 0): na versão 1.0.4 com pandas 3, as gerações quebram (amostragem ponderada) e, remendadas,
      deram vencedores diferentes a cada execução. A busca é a "geração 0": o molde geral do AutoTS + combinações
      aleatórias (sementes fixas). Duas execuções da mesma janela dão o mesmo resultado (conferido em 26/10/2026).
  AT7 Tempo limitado: cerca de 10 a 30 s por janela; 10 janelas por série. `segundos` de cada busca em `escolhas`.

Parâmetros fixados antes de ver o teste: LISTA, transformações "superfast" com até 3 passos, 2 validações, 35%
revalidados, MAE, semente 2026. A escolha entre o AutoTS e os outros modelos é a da régua (menor WAPE h1 jun–set,
empate < 1 ponto = o mais simples; o AutoTS conta como o mais complexo, ml/previsao.py).
"""

import contextlib
import io
import random
import time
import warnings

import numpy as np
import pandas as pd

LISTA = ("ConstantNaive", "LastValueNaive", "AverageValueNaive", "SeasonalNaive", "GLM", "GLS", "ETS", "ARIMA",
         "UnobservedComponents", "KalmanStateSpace", "Theta", "ARDL", "BasicLinearModel", "UnivariateMotif",
         "MetricMotif", "SeasonalityMotif", "FFT", "WindowRegression", "DatepartRegression")
SEMENTE = 2026
VALIDACOES = 2
REVALIDADOS = 0.35
INTERVALO = 0.8
TOPO = 3
HMAX = 3            # a régua pede até 3 meses à frente (h1 é o do critério)
CONFIG = {"lista": list(LISTA), "transformacoes": "superfast", "profundidade": 3, "validacoes": VALIDACOES,
          "revalidados": REVALIDADOS, "metrica": "mae", "geracoes": 0, "semente": SEMENTE, "intervalo": INTERVALO}

_BUSCAS: dict = {}          # (série, meses, valores) -> {"ranking": [...], "segundos": s}
ESCOLHAS: dict = {}         # nome do modelo -> lista de {serie, treino_fim, modelo, transformacoes, posicao, segundos}

_PESOS = {k: 0 for k in ("smape_weighting", "rmse_weighting", "made_weighting", "mage_weighting", "mle_weighting",
                         "imle_weighting", "spl_weighting", "containment_weighting", "contour_weighting",
                         "runtime_weighting", "uwmse_weighting", "smoothness_weighting", "ewmae_weighting",
                         "mqae_weighting", "oda_weighting", "dwae_weighting", "maxe_weighting", "mate_weighting",
                         "wasserstein_weighting", "dwd_weighting")}
_PESOS["mae_weighting"] = 1


def _semear() -> None:
    random.seed(SEMENTE)
    np.random.seed(SEMENTE)


def _tabela(serie: pd.Series) -> pd.DataFrame:
    return pd.DataFrame({"y": serie.to_numpy(dtype=float)}, index=serie.index.to_timestamp())


def _transformacoes(t) -> list[str]:
    try:
        d = t if isinstance(t, dict) else __import__("json").loads(t)
        return [str(v) for v in (d.get("transformations") or {}).values()]
    except Exception:  # noqa: BLE001
        return []


def buscar(serie: pd.Series, prever=None) -> dict:
    """AT1/AT3/AT5: roda o AutoTS na janela recebida, ordena (um por família) pela nota da validação e já prevê HMAX
    meses com os primeiros colocados até TOPO deles conseguirem prever (quem falha fica em `falhas`)."""
    from autots import AutoTS

    _semear()
    t0 = time.time()
    with warnings.catch_warnings(), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        warnings.simplefilter("ignore")
        m = AutoTS(forecast_length=1, frequency="MS", prediction_interval=INTERVALO, ensemble=None,
                   model_list=list(LISTA), transformer_list="superfast", transformer_max_depth=3, max_generations=0,
                   num_validations=VALIDACOES, validation_method="backwards", models_to_validate=REVALIDADOS,
                   random_seed=SEMENTE, n_jobs=1, verbose=-2, metric_weighting=dict(_PESOS), no_negatives=True,
                   drop_most_recent=0)
        m.fit(_tabela(serie))
    r = m.validation_results.model_results
    if "Exceptions" in r:
        r = r[r["Exceptions"].isnull()]
    r = r[r["Runs"] >= r["Runs"].max()].sort_values(["Score", "ID"])
    ranking, vistos = [], set()
    for x in r.itertuples():
        if x.Model in vistos:
            continue
        vistos.add(x.Model)
        ranking.append({"modelo": x.Model, "parametros": x.ModelParameters, "transformacao": x.TransformationParameters,
                        "nota": float(x.Score), "posicao": len(ranking) + 1})
    escolhidos, falhas = [], []
    for t in ranking:
        if len(escolhidos) == TOPO:
            break
        try:
            prev = (prever or prever_template)(t, serie, HMAX)
        except Exception as e:  # noqa: BLE001 — AT4: vale o próximo colocado
            falhas.append({"modelo": t["modelo"], "posicao": t["posicao"], "erro": f"{type(e).__name__}: {e}"[:200]})
            continue
        escolhidos.append({**t, "previsao": prev.astype(float).to_dict("records")})
    return {"escolhidos": escolhidos, "falhas": falhas, "n_familias": len(ranking),
            "ranking": [{k: t[k] for k in ("modelo", "nota", "posicao")} for t in ranking],
            "segundos": round(time.time() - t0, 1)}


def _buscar_isolado(nome: str, meses: list[str], valores: list[float]) -> dict:
    """Roda num processo novo (AT6): no mesmo processo, a 2ª busca da mesma janela muda as notas (o AutoTS guarda estado
    global entre execuções), então cada busca nasce num interpretador limpo e não depende da ordem das janelas."""
    return buscar(pd.Series(valores, index=pd.PeriodIndex(meses, freq="M"), name=nome))


def busca_da_janela(serie: pd.Series) -> dict:
    """Uma busca por janela, guardada: autots_1, _2 e _3 da mesma origem usam a mesma busca."""
    chave = (serie.name, tuple(map(str, serie.index)), tuple(np.round(serie.to_numpy(dtype=float), 6)))
    if chave not in _BUSCAS:
        import multiprocessing
        from concurrent.futures import ProcessPoolExecutor

        with ProcessPoolExecutor(max_workers=1, mp_context=multiprocessing.get_context("spawn"),
                                 max_tasks_per_child=1) as ex:
            _BUSCAS[chave] = ex.submit(_buscar_isolado, str(serie.name), list(chave[1]),
                                       serie.to_numpy(dtype=float).tolist()).result()
    return _BUSCAS[chave]


def prever_template(t: dict, serie: pd.Series, h: int) -> pd.DataFrame:
    """AT5: treina o modelo escolhido na janela inteira e prevê h meses (valor, p10, p90)."""
    from autots import model_forecast

    _semear()
    with warnings.catch_warnings(), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        warnings.simplefilter("ignore")
        p = model_forecast(model_name=t["modelo"], model_param_dict=t["parametros"],
                           model_transform_dict=t["transformacao"], df_train=_tabela(serie), forecast_length=h,
                           frequency="MS", prediction_interval=INTERVALO, no_negatives=True, random_seed=SEMENTE,
                           n_jobs=1, verbose=0)
    v, lo, hi = (np.asarray(x.iloc[:, 0], dtype=float) for x in (p.forecast, p.lower_forecast, p.upper_forecast))
    if not np.all(np.isfinite(v)):
        raise ValueError("previsão com NaN")
    return pd.DataFrame({"valor": v, "p10": np.minimum(lo, v), "p90": np.maximum(hi, v)})


class AutoTSPosicao:
    """AT4: o k-ésimo colocado (entre os que conseguem prever) da busca do AutoTS na janela recebida."""

    minimo_treino = 0

    def __init__(self, posicao: int, busca=None):
        self.posicao = posicao
        self.nome = f"autots_{posicao}"
        self.descricao = f"AutoTS: o {posicao}º colocado da busca automática em cada janela de 12 meses"
        self._busca = busca or busca_da_janela

    def fit(self, serie: pd.Series):
        b = self._busca(serie)
        if len(b["escolhidos"]) < self.posicao:
            raise ValueError(f"a busca do AutoTS não teve {self.posicao} modelos que conseguissem prever")
        self.escolha_ = b["escolhidos"][self.posicao - 1]
        ESCOLHAS.setdefault(self.nome, []).append({
            "serie": str(serie.name), "treino_inicio": str(serie.index[0]), "treino_fim": str(serie.index[-1]),
            "n_meses": len(serie), "modelo": self.escolha_["modelo"],
            "transformacoes": _transformacoes(self.escolha_["transformacao"]), "posicao": self.escolha_["posicao"],
            "nota": self.escolha_["nota"], "segundos": b.get("segundos"), "n_familias": b.get("n_familias")})
        return self

    def predict(self, h: int) -> pd.DataFrame:
        p = pd.DataFrame(self.escolha_["previsao"])
        if len(p) < h:
            raise ValueError(f"a busca previu {len(p)} meses; a régua pediu {h}")
        return p.iloc[:h].reset_index(drop=True)


def detalhe(nome: str) -> dict | None:
    """Gancho lido por ml/rodar.py: o que o AutoTS escolheu em cada janela (sem repetição) e a configuração."""
    if nome not in ESCOLHAS:
        return None
    vistos, linhas = set(), []
    for e in ESCOLHAS[nome]:
        chave = (e["serie"], e["treino_fim"])
        if chave not in vistos:
            vistos.add(chave)
            linhas.append(e)
    return {"config": CONFIG, "escolhas": linhas}


MODELOS = [AutoTSPosicao(k) for k in range(1, TOPO + 1)]
