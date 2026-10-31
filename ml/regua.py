"""Régua única de backtest para a previsão de pedidos por mês (Inbound, Mercado) — protocolo D48 (26/10/2026).

CONTRATO DO MODELO (o que cada especialista implementa, em ml/modelos/<seu_modulo>.py):

    class MeuModelo:
        nome = "meu_modelo"                      # único no projeto; vira a chave no resultados.json
        descricao = "texto curto para a tela"    # opcional
        minimo_treino = 0                        # opcional: meses de treino de que o modelo precisa (R4)
        def fit(self, serie: pd.Series) -> "MeuModelo": ...
            # serie: pedidos por mês, índice pd.PeriodIndex(freq="M") contínuo, só meses COMPLETOS < origem e,
            # no protocolo D48, só os 12 meses anteriores à origem. serie.name = "Inbound" ou "Mercado".
        def predict(self, h: int) -> pd.DataFrame: ...
            # h linhas para os meses serie.index[-1]+1 ... +h; colunas valor, p10, p90 (floats >= 0;
            # p10/p90 = faixa de 80%; NaN se o modelo não tiver faixa). O índice é refeito pela régua.

    MODELOS = [MeuModelo(), MeuModelo(param=2), ...]   # lista no módulo (variantes com nomes distintos)

    - A régua faz deepcopy do objeto antes de cada fit: o objeto registrado é só a "receita".
    - Exógenas de calendário conhecidas de antemão: ml.calendario.exogenas(pd.PeriodIndex).
    - Para faixa pelos erros do próprio passado, herde ml.regua.ModeloPontual e implemente só prever_ponto().
    - Determinismo: fixe random_state/seed. Hiperparâmetro escolhido só dentro do treino recebido.

RODAR: python -m ml.rodar --modulo <seu_modulo>; python -m ml.rodar roda todos (ver ml/rodar.py).

REGRAS DA RÉGUA (D48, decisão do Caio de 26/10/2026; revisa a D47)
  R1 Janela móvel de 12 meses: cada previsão é treinada SÓ com os 12 meses completos anteriores à origem
     (jun/26 treina com jun/25–mai/26; jul/26 com jul/25–jun/26 ...). 2025 entra só dentro da janela (17–25% de
     datas estimadas, PD10): o modelo não depende do histórico longo.
  R2 Teste (onde se escolhe o modelo): jun, jul, ago e set de 2026, horizonte 1 (a previsão feita no fim do mês
     anterior). Também medidos, só para informação: horizontes 2 e 3 dos mesmos meses (origens anteriores, cada uma
     com a sua janela de 12 meses) e a "verificação" = horizonte 1 de jan–mai/2026, fora do período de escolha.
  R3 Métricas, sobre os mesmos pares alvo x horizonte: WAPE = soma|prev-real| / soma(real) (principal); MAE (pedidos);
     viés = soma(prev-real) / soma(real) (negativo = subestima); cobertura = % de reais dentro de [p10, p90] (ideal
     ~80%); largura = média de (p90-p10) / real. Chaves: "1" = h1 jun–set (a do critério), "2", "3", "todos" (h1–h3
     jun–set) e "verificacao" (h1 jan–mai).
  R4 Não se aplica: modelo que declara `minimo_treino` maior que a janela (ex.: sazonalidade anual, que precisa de
     2 ciclos = 24 meses) não roda no protocolo e fica registrado com o motivo (NaoSeAplica).
  R5 Futuro: treino com os 12 meses completos até o último mês fechado (out/25–set/26); prevê out, nov, dez/2026.
     O mês em andamento nunca entra no treino.
  R6 Protocolo antigo (D47: histórico inteiro, alvos jan–set/2026, h1–h3) fica acessível com
     backtest(..., pares=pares_d47(), janela=None), só para comparação.

D56 (Caio, 26/10/2026): uma série e um modelo por recorte (Inbound, Mercado, Mercado exclusivos, Mercado não
exclusivos), TODOS os modelos em TODAS as séries, na mesma régua.
  R7 Séries curtas (a exclusividade só existe em 2026): a janela continua sendo "os até 12 meses fechados anteriores à
     origem" — com menos de 12 no histórico, ela fica EXPANSIVA (jun/26 treina com jan–mai, 5 meses; set/26 com
     jan–ago, 8). Cada modelo tem um mínimo de meses de treino (`minimo()`, decidido antes de ver os resultados): o
     declarado pelo modelo (`minimo_treino`) ou, sem declaração, MINIMO_CURTO (referências e combinações simples, de
     1 a 6 meses) e, para todo o resto, os 12 meses da janela (ARIMA/ETS pela regra nº de parâmetros <= n/4, rede
     neural, boosting, Prophet, AutoTS e as combinações com backtest interno foram desenhados e validados para 12
     pontos). Uma origem com menos meses que o mínimo não é prevista: se faltar qualquer mês do teste (h1 jun–set),
     o modelo "não se aplica" naquela série (NaoSeAplica, com o motivo); a verificação (h1 jan–mai) só vale completa
     (os 5 meses), senão fica vazia ("sem verificação"). Nas séries longas (desde out/2024) toda origem tem 12 meses:
     nada muda nelas.
"""

import copy
import math
from pathlib import Path

import numpy as np
import pandas as pd

from ml import dados

JANELA = 12
TESTE = (pd.Period("2026-06", "M"), pd.Period("2026-09", "M"))
VERIFICACAO = (pd.Period("2026-01", "M"), pd.Period("2026-05", "M"))
HORIZONTES = (1, 2, 3)
SERIES = dados.TIPOS
# compatibilidade (protocolo D47)
ALVO_INICIO = pd.Period("2026-01", "M")
ALVO_FIM = pd.Period("2026-09", "M")


class NaoSeAplica(Exception):
    """R4: o modelo precisa de mais meses de treino do que a janela oferece (R7: ou do que a série tem)."""


# R7 (D56): mínimo de meses de treino dos modelos que rodam em séries curtas (sem declaração = JANELA)
MINIMO_CURTO = {"ref_ultimo_mes": 1, "ref_media_3m": 3, "ref_media_6m": 6, "ref_tendencia_6m": 6,
                "comb_ses": 3, "comb_holt_amort": 3, "comb_theta": 3, "comb_drift": 3, "comb_drift_log": 3,
                "comb_mediana": 3, "comb_media": 3}


def minimo(modelo) -> int:
    """R7: meses de treino de que o modelo precisa (o maior entre o declarado e o da tabela; sem tabela, a janela)."""
    declarado = getattr(modelo, "minimo_treino", 0) or 0
    return max(declarado, MINIMO_CURTO.get(getattr(modelo, "nome", ""), JANELA))


def _curto_demais(modelo, serie: pd.Series, origem: pd.Period, janela: int | None) -> int | None:
    """R7: nº de meses de treino da origem, se for menor que o mínimo do modelo; senão None. Sem janela (protocolo
    antigo D47, R6), não se aplica."""
    if not janela:
        return None
    n = len(treino_de(serie, origem, janela))
    return n if n < minimo(modelo) else None


def _meses(inicio: pd.Period, fim: pd.Period) -> list[pd.Period]:
    return list(pd.period_range(inicio, fim, freq="M"))


def pares_d48(teste=TESTE, verificacao=VERIFICACAO, horizontes=HORIZONTES) -> list[tuple[pd.Period, int]]:
    """R2: (alvo, horizonte) do protocolo D48: h1 de jan–set (verificação + teste) e h2/h3 de jun–set."""
    pares = [(a, 1) for a in _meses(verificacao[0], verificacao[1])] if verificacao else []
    pares += [(a, k) for k in horizontes for a in _meses(*teste)]
    return sorted(set(pares))


def pares_d47(alvo_inicio=ALVO_INICIO, alvo_fim=ALVO_FIM, horizontes=HORIZONTES) -> list[tuple[pd.Period, int]]:
    """R6: protocolo antigo (todos os alvos jan–set em h1, h2, h3)."""
    return [(a, k) for k in horizontes for a in _meses(alvo_inicio, alvo_fim)]


def carregar_series(tabela: pd.DataFrame | None = None) -> tuple[dict[str, pd.Series], dict]:
    """Snapshot -> {tipo: série só de meses completos}, e informações do mês parcial e da carga."""
    t = dados.carregar_snapshot() if tabela is None else tabela
    series, parcial = {}, {}
    for tipo in SERIES:
        d = t[t["tipo"] == tipo].copy()
        d["periodo"] = pd.PeriodIndex(d["mes"], freq="M")
        ok = d["completo"].astype(str).str.lower().isin(["true", "1"])
        completos = d[ok].sort_values("periodo")
        s = pd.Series(completos["pedidos"].astype(float).to_numpy(), index=pd.PeriodIndex(completos["periodo"]))
        cheio = pd.period_range(s.index.min(), s.index.max(), freq="M")
        series[tipo] = s.reindex(cheio, fill_value=0.0).rename(tipo)
        resto = d[~ok].sort_values("periodo")
        if len(resto):
            parcial[tipo] = {"mes": str(resto["periodo"].iloc[-1]),
                             "pedidos_ate_agora": float(resto["pedidos"].iloc[-1])}
    meta = {"processado_em": str(t["processado_em"].iloc[0]), "dados_ate": str(t["dados_ate"].iloc[0]),
            "parcial": parcial, "mes_fechado": str(min(s.index[-1] for s in series.values()))}
    return series, meta


def carregar_recortes(pasta=None, tabelas: dict | None = None) -> tuple[dict[str, pd.Series], dict]:
    """D56: {nome da série: só meses completos, índice contínuo} dos 4 recortes (ml/dados/serie_<recorte>.csv) e o
    meta da carga (como carregar_series, com `recortes` = chave, fonte e se a série é curta, R7). `tabelas` = as
    mesmas tabelas já montadas em memória (dados.montar_recortes), sem ler os CSVs."""
    pasta = Path(pasta) if pasta else dados.PASTA
    if tabelas is None and not all((pasta / f"serie_{c}.csv").exists() for c in dados.RECORTES):
        # snapshot de antes da D56 (sem os CSVs por série): monta em memória a partir dos dois CSVs extraídos
        tabelas = dados.montar_recortes(dados.carregar_snapshot(), dados.carregar_exclusividade())
    series, parcial, recortes = {}, {}, {}
    meta_carga = None
    for chave, r in dados.RECORTES.items():
        d = tabelas[chave].copy() if tabelas else dados.carregar_recorte(chave, pasta)
        d["periodo"] = pd.PeriodIndex(d["mes"], freq="M")
        ok = d["completo"].astype(str).str.lower().isin(["true", "1"])
        c = d[ok].sort_values("periodo")
        s = pd.Series(c["pedidos"].astype(float).to_numpy(), index=pd.PeriodIndex(c["periodo"]))
        s = s.reindex(pd.period_range(s.index.min(), s.index.max(), freq="M"), fill_value=0.0).rename(r["serie"])
        series[r["serie"]] = s
        resto = d[~ok].sort_values("periodo")
        if len(resto):
            parcial[r["serie"]] = {"mes": str(resto["periodo"].iloc[-1]),
                                   "pedidos_ate_agora": float(resto["pedidos"].iloc[-1])}
        primeiro_teste = len(treino_de(s, TESTE[0]))
        recortes[r["serie"]] = {"chave": chave, "tipo": r["tipo"], "grupo": r["grupo"], "fonte": r["fonte"],
                                "inicio": str(s.index[0]), "fim": str(s.index[-1]), "meses": len(s),
                                "treino_1o_teste": primeiro_teste, "curta": primeiro_teste < JANELA}
        meta_carga = meta_carga or {"processado_em": str(d["processado_em"].iloc[0]),
                                    "dados_ate": str(d["dados_ate"].iloc[0])}
    meta = {**meta_carga, "parcial": parcial, "recortes": recortes,
            "mes_fechado": str(min(s.index[-1] for s in series.values()))}
    return series, meta


def carregar_sensibilidade(pasta=None) -> dict[str, pd.Series]:
    """S5 (fonte fraca): as séries de exclusividade do Mercado estendidas com a silver 2025 (só meses completos)."""
    pasta = pasta or dados.PASTA
    saida = {}
    for chave, r in dados.SENSIBILIDADE.items():
        d = dados.carregar_recorte(chave, pasta)
        c = d[d["completo"].astype(str).str.lower().isin(["true", "1"])]
        s = pd.Series(c["pedidos"].astype(float).to_numpy(), index=pd.PeriodIndex(c["mes"], freq="M")).sort_index()
        cheio = pd.period_range(s.index.min(), s.index.max(), freq="M")
        saida[r["serie"]] = s.reindex(cheio, fill_value=0.0).rename(r["serie"])
    return saida


def _normalizar(saida: pd.DataFrame, h: int, inicio: pd.Period) -> pd.DataFrame:
    saida = pd.DataFrame(saida).reset_index(drop=True)
    if "valor" not in saida or len(saida) < h:
        raise ValueError(f"predict({h}) precisa devolver {h} linhas com a coluna 'valor'")
    for c in ("p10", "p90"):
        if c not in saida:
            saida[c] = np.nan
    saida = saida.iloc[:h][["valor", "p10", "p90"]].astype(float)
    if not np.isfinite(saida['valor']).all():
        raise ValueError('Previsão pontual ausente ou não finita')
    faixa = saida[['p10', 'p90']]
    if np.isinf(faixa.to_numpy()).any() or faixa.isna().any(axis=1).ne(faixa.isna().all(axis=1)).any():
        raise ValueError('Faixa incompleta ou não finita')
    if (saida['p10'] > saida['p90']).any():
        raise ValueError('Limites da faixa invertidos')
    saida.index = pd.period_range(inicio, periods=h, freq="M")
    return saida.clip(lower=0)


def treino_de(serie: pd.Series, origem: pd.Period, janela: int | None = JANELA) -> pd.Series:
    """R1: meses < origem; com janela, só os `janela` meses imediatamente anteriores à origem."""
    t = serie[serie.index < origem]
    if janela:
        t = t[t.index >= origem - janela]
    return t.copy()


def verificar_aplica(modelo, janela: int | None = JANELA) -> None:
    """R4: levanta NaoSeAplica se o modelo pede mais meses do que a janela."""
    minimo = getattr(modelo, "minimo_treino", 0) or 0
    if janela and minimo > janela:
        motivo = getattr(modelo, "motivo_minimo", "") or f"precisa de pelo menos {minimo} meses de treino"
        raise NaoSeAplica(f"{motivo}; a janela tem {janela}")


def prever_de(modelo, serie: pd.Series, origem: pd.Period, h: int, janela: int | None = JANELA) -> pd.DataFrame:
    """Treina uma cópia do modelo com a janela anterior à origem e prevê h meses a partir da origem."""
    verificar_aplica(modelo, janela)
    m = copy.deepcopy(modelo).fit(treino_de(serie, origem, janela))
    return _normalizar(m.predict(h), h, origem)


def backtest(modelo, serie: pd.Series, pares=None, janela: int | None = JANELA) -> pd.DataFrame:
    """Linhas alvo, horizonte, origem, trecho (teste | verificacao | outro), real, valor, p10, p90.

    Cada origem (alvo - horizonte + 1) é ajustada uma vez e prevê até o maior horizonte pedido para ela."""
    pares = pares_d48() if pares is None else pares
    por_origem: dict[pd.Period, int] = {}
    for alvo, k in pares:
        o = alvo - (k - 1)
        por_origem[o] = max(por_origem.get(o, 0), k)
    verificar_aplica(modelo, janela)  # R4 antes da R7: o motivo de "não se aplica" fica o do modelo
    linhas = []
    for origem in sorted(por_origem):
        hmax = por_origem[origem]
        n = _curto_demais(modelo, serie, origem, janela)
        if n is not None:  # R7: série curta demais para o modelo nesta origem
            if any(k == 1 and a == origem and TESTE[0] <= a <= TESTE[1] for a, k in pares):
                raise NaoSeAplica(f"precisa de {minimo(modelo)} meses de treino; a série tem {n} antes de {origem} "
                                  f"(mês do teste sem treino suficiente)")
            continue
        p = prever_de(modelo, serie, origem, hmax, janela)
        for alvo, k in pares:
            if alvo - (k - 1) != origem or alvo not in serie.index:
                continue
            r = p.loc[alvo]
            trecho = ("teste" if TESTE[0] <= alvo <= TESTE[1] else
                      "verificacao" if k == 1 and VERIFICACAO[0] <= alvo <= VERIFICACAO[1] else "outro")
            linhas.append({"alvo": str(alvo), "horizonte": k, "origem": str(origem), "trecho": trecho,
                           "real": float(serie[alvo]), "valor": r["valor"], "p10": r["p10"], "p90": r["p90"]})
    return pd.DataFrame(linhas, columns=["alvo", "horizonte", "origem", "trecho", "real", "valor", "p10", "p90"])


def metricas(b: pd.DataFrame) -> dict:
    """R3 sobre um conjunto de pares previsto x real."""
    if not len(b):
        return {"n": 0, "wape": math.nan, "mae": math.nan, "vies": math.nan, "cobertura_80": math.nan,
                "n_faixa": 0, "largura": math.nan}
    erro = b["valor"] - b["real"]
    soma = b["real"].sum()
    com_faixa = b.dropna(subset=["p10", "p90"])
    dentro = (com_faixa["real"] >= com_faixa["p10"]) & (com_faixa["real"] <= com_faixa["p90"])
    larg = ((com_faixa["p90"] - com_faixa["p10"]) / com_faixa["real"]).mean() if len(com_faixa) else math.nan
    return {"n": int(len(b)), "wape": float(erro.abs().sum() / soma) if soma else math.nan,
            "mae": float(erro.abs().mean()), "vies": float(erro.sum() / soma) if soma else math.nan,
            "cobertura_80": float(dentro.mean()) if len(com_faixa) else math.nan,
            "n_faixa": int(len(com_faixa)), "largura": float(larg)}


def metricas_d48(b: pd.DataFrame) -> dict:
    """R3: "1" (critério), "2", "3", "todos" = teste jun–set; "verificacao" = h1 jan–mai."""
    teste = b[b["trecho"] == "teste"]
    m = {str(k): metricas(teste[teste["horizonte"] == k]) for k in HORIZONTES}
    m["todos"] = metricas(teste)
    verif = b[b["trecho"] == "verificacao"]
    # R7: verificação só completa (os 5 meses); série curta = "sem verificação" (n_parcial guarda quantos havia)
    if verif["alvo"].nunique() >= len(_meses(*VERIFICACAO)):
        m["verificacao"] = metricas(verif)
    else:
        m["verificacao"] = {**metricas(verif.iloc[0:0]), "n_parcial": int(len(verif))}
    return m


def avaliar(modelo, series: dict[str, pd.Series] | None = None, pares=None, janela: int | None = JANELA) -> dict:
    """Backtest + métricas. Devolve {serie: {"metricas": {...}, "backtest": [linhas]}}."""
    if series is None:
        series, _ = carregar_series()
    saida = {}
    for tipo, s in series.items():
        b = backtest(modelo, s, pares, janela)
        saida[tipo] = {"metricas": metricas_d48(b), "backtest": b.round(2).to_dict("records")}
    return saida


def prever_futuro(modelo, series: dict[str, pd.Series] | None = None, h: int = 3,
                  janela: int | None = JANELA) -> dict:
    """R5: treino com os 12 meses completos até o último mês fechado; previsões dos 3 meses seguintes."""
    if series is None:
        series, _ = carregar_series()
    saida = {}
    for tipo, s in series.items():
        if (n := _curto_demais(modelo, s, s.index[-1] + 1, janela)) is not None:  # R7
            raise NaoSeAplica(f"precisa de {minimo(modelo)} meses de treino; a série tem {n}")
        p = prever_de(modelo, s, s.index[-1] + 1, h, janela)
        saida[tipo] = [{"mes": str(i), **{c: round(float(v), 2) for c, v in r.items()}} for i, r in p.iterrows()]
    return saida


class ModeloPontual:
    """Base para modelos que só dão o valor: a faixa p10-p90 sai dos erros do PRÓPRIO passado de treino.

    Em fit, refaz um backtest interno (origens no treino com pelo menos `minimo_hist` meses antes; as últimas
    `origens_faixa`) e guarda, por horizonte, a razão real / previsto; p10/p90 = valor x quantis 10%/90% da
    razão. Com menos de `minimo_razoes` razões no horizonte, junta todos os horizontes. Nada do período
    avaliado vaza para a faixa. Com a janela de 12 meses, a faixa sai de ~6 origens internas (D48).
    A subclasse implementa prever_ponto(hist: pd.Series, h: int) -> h floats.
    """

    nome = "pontual"
    descricao = ""
    minimo_hist = 6
    minimo_razoes = 4
    origens_faixa = 12

    def prever_ponto(self, hist: pd.Series, h: int):  # pragma: no cover - abstrato
        raise NotImplementedError

    def fit(self, serie: pd.Series):
        self.serie_ = serie
        hmax = max(HORIZONTES)
        razoes = {k: [] for k in HORIZONTES}
        n = len(serie)
        for i in range(max(self.minimo_hist, n - self.origens_faixa - hmax + 1), n):
            prev = self.prever_ponto(serie.iloc[:i], hmax)
            for k in HORIZONTES:
                j = i + k - 1
                v = prev[k - 1]
                if j < n and v is not None and np.isfinite(v) and v > 0:
                    razoes[k].append(float(serie.iloc[j]) / v)
        todas = [r for v in razoes.values() for r in v]
        self.quantis_ = {}
        for k in HORIZONTES:
            base = razoes[k] if len(razoes[k]) >= self.minimo_razoes else todas
            self.quantis_[k] = ((float(np.quantile(base, 0.1)), float(np.quantile(base, 0.9)))
                                if len(base) >= self.minimo_razoes else (math.nan, math.nan))
        return self

    def predict(self, h: int) -> pd.DataFrame:
        v = np.asarray(self.prever_ponto(self.serie_, h), dtype=float)
        q = [self.quantis_.get(k, self.quantis_[max(HORIZONTES)]) for k in range(1, h + 1)]
        return pd.DataFrame({"valor": v, "p10": v * np.array([a for a, _ in q]),
                             "p90": v * np.array([b for _, b in q])})
