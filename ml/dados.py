"""Extrai do BigQuery (somente SELECT) o snapshot congelado que TODOS os especialistas usam.

Rodar:  python -m ml.dados          (precisa das credenciais ADC de gcloud-viu; ver CLAUDE.md, item 6)
Grava:
Fonte (D57, 27/10/2026): só gold (gold_monday), sem refazer regra; a única exceção é a S5 (silver 2025, fonte fraca).
  ml/dados/serie_mensal.csv   mes, tipo, pedidos, estimados, completo, dados_ate, processado_em
      view gold `gld_agenciamento_previsao_mensal` (TAB_PREVISAO_MENSAL): pedidos = quantidade + quantidade_estimada da
      gold de entradas (regra E1), por mês de entrada, tipo_de_input em (Inbound, Mercado), desde 2024-10. `completo` =
      o mês terminou até `dados_ate` (regra E3 do portal, app/corte.py: véspera do dia, em São Paulo, de
      MAX(_processado_em)). O mês corrente (parcial) vem com completo = False.
Contrato (G4-N13): antes de gravar, `validar()` confere o snapshot (uma só carga, contagens inteiras e não negativas,
meses completos sem buraco); com problema, nada é gravado e a rotina para (sem retrato nem histórico). A diferença
entre o total do tipo e exclusivos + não exclusivos + sem talento vai para o log (as duas golds são conferidas uma contra a outra).
  ml/dados/exclusividade.csv  mes, tipo, exclusivos, nao_exclusivos, sem_talento, total, processado_em
      view gold `gld_agenciamento_2026_previsao_exclusividade_mensal` (TAB_EXCLUSIVIDADE_MENSAL): o mesmo critério de
      data e de exclusividade da gold de talentos (R1, R2, R4, R5, R21), de 1º/jan/2026 até `dados_ate`, por mês e tipo.

D56 (Caio, 26/10/2026): UMA SÉRIE E UM MODELO POR RECORTE, cada série com o seu próprio snapshot (sem repartição):
  S1 ml/dados/serie_inbound.csv            gold de entradas, tipo Inbound (todo Inbound conta como exclusivo, PD24)
  S2 ml/dados/serie_mercado.csv            gold de entradas, tipo Mercado
  S3 ml/dados/serie_mercado_exclusivos.csv gold de exclusividade, tipo Mercado, exclusivos
  S4 ml/dados/serie_mercado_nao_exclusivos.csv  gold de exclusividade, tipo Mercado, não exclusivos
     Colunas: mes, pedidos, completo, fonte, dados_ate, processado_em. `completo` = o mesmo da gold no mês e tipo
     (E3). S3 e S4 começam em jan/2026 (só o board de 2026 tem a exclusividade na data do pedido); sem talento
     informado fica fora das duas (como na página Talentos), então S3 + S4 < S2.
  S5 ml/dados/exclusividade_2025.csv (fonte FRACA, só para a sensibilidade ml/sensibilidade.py; não vai à tela):
     silver 2025 (`slv_agenciamento_2025_itens`), mesma data da gold (criado_em; sem ele, data_de_saida − 5 dias
     úteis, R2) e exclusivo = coluna `talentos_exclusivos` preenchida (a 2025 não tem `exclusivo` nem `talento`:
     não separa "não exclusivo" de "sem talento"). Avaliação em docs/paginas/previsao.md, 5.8.
  S6 ml/dados/lotes_vigente.csv (diagnóstico do mês em andamento, D56 item 3): gold `gld_agenciamento_2026_previsao_lotes`
     (TAB_LOTES, um dia × recorte; lote = 3 ou mais pedidos da mesma marca no mesmo dia, regra L3 da gold) somada por
     recorte e mês (os 4 meses fechados anteriores e o vigente), até o MESMO dia do mês de `dados_ate`: pedidos, em lote
     e avulsos. Explica, com dados, o desvio do mês em andamento.
"""

import os
from pathlib import Path

import pandas as pd

PASTA = Path(__file__).resolve().parent / "dados"
ARQ_SERIE = PASTA / "serie_mensal.csv"
ARQ_EXCLUSIVIDADE = PASTA / "exclusividade.csv"
ARQ_EXCLUSIVIDADE_2025 = PASTA / "exclusividade_2025.csv"
ARQ_LOTES = PASTA / "lotes_vigente.csv"
TIPOS = ("Inbound", "Mercado")
INICIO = "2024-10-01"

# D56: os recortes (uma série e um modelo para cada). `serie` = nome da série no resultados.json e na régua.
RECORTES = {
    "inbound": {"serie": "Inbound", "tipo": "Inbound", "grupo": None,
                "fonte": "gold de entradas (gld_agenciamento_entrada_diaria), tipo Inbound"},
    "mercado": {"serie": "Mercado", "tipo": "Mercado", "grupo": None,
                "fonte": "gold de entradas (gld_agenciamento_entrada_diaria), tipo Mercado"},
    "mercado_exclusivos": {"serie": "Mercado exclusivos", "tipo": "Mercado", "grupo": "exclusivos",
                           "fonte": "gold de exclusividade (gld_agenciamento_2026_previsao_exclusividade_mensal), Mercado exclusivos"},
    "mercado_nao_exclusivos": {"serie": "Mercado não exclusivos", "tipo": "Mercado", "grupo": "nao_exclusivos",
                               "fonte": "gold de exclusividade (gld_agenciamento_2026_previsao_exclusividade_mensal), Mercado não exclusivos"},
}
# sensibilidade (fonte fraca): as séries S3/S4 estendidas para trás com a silver 2025 (S5); não vão à tela
SENSIBILIDADE = {
    "mercado_exclusivos_2025": {"serie": "Mercado exclusivos (com 2025)", "base": "mercado_exclusivos",
                                "col_2025": "exclusivos"},
    "mercado_nao_exclusivos_2025": {"serie": "Mercado não exclusivos (com 2025)", "base": "mercado_nao_exclusivos",
                                    "col_2025": "nao_exclusivos_ou_sem"},
}

SQL_SERIE = """
SELECT FORMAT_DATE('%Y-%m', mes) AS mes, tipo, pedidos, estimados, completo, dados_ate, _processado_em AS processado_em
FROM `{previsao_mensal}`
WHERE tipo IN UNNEST(@tipos) AND mes >= @inicio
ORDER BY tipo, mes
"""

SQL_EXCLUSIVIDADE = """
SELECT FORMAT_DATE('%Y-%m', mes) AS mes, tipo, exclusivos, nao_exclusivos, sem_talento, total
FROM `{exclusividade}`
WHERE tipo IN UNNEST(@tipos) AND mes <= @fim
ORDER BY tipo, mes
"""

# S6: a gold diária de lotes somada por recorte e mês, nos 4 meses fechados antes do mês de @fim e no próprio mês, até
# o mesmo dia do mês de @fim
SQL_LOTES = """
SELECT recorte, FORMAT_DATE('%Y-%m', data) AS mes, EXTRACT(DAY FROM @fim) AS ate_dia,
  SUM(pedidos) AS pedidos, SUM(em_lote) AS em_lote, SUM(avulsos) AS avulsos
FROM `{lotes}`
WHERE data BETWEEN DATE_SUB(DATE_TRUNC(@fim, MONTH), INTERVAL 4 MONTH) AND @fim
  AND EXTRACT(DAY FROM data) <= EXTRACT(DAY FROM @fim)
GROUP BY recorte, mes ORDER BY recorte, mes
"""

# S5: silver 2025, mesma data da gold (R2 para quem não tem criado_em); exclusivo = talentos_exclusivos preenchido
SQL_EXCLUSIVIDADE_2025 = """
WITH feriados AS (
  SELECT ARRAY_AGG(DATE(a, f.m, f.d)) AS dias
  FROM UNNEST([2024, 2025]) AS a,
    UNNEST(ARRAY<STRUCT<m INT64, d INT64>>[(1,1),(1,20),(1,25),(4,21),(4,23),(5,1),(7,9),(9,7),(10,12),(11,2),
      (11,15),(11,20),(12,24),(12,25),(12,31)]) AS f
),
pedidos AS (
  SELECT
    COALESCE(i.criado_em,
      (SELECT ARRAY_AGG(d ORDER BY d DESC)[SAFE_OFFSET(4)]
       FROM UNNEST(GENERATE_DATE_ARRAY(DATE_SUB(i.data_de_saida, INTERVAL 21 DAY),
                                       DATE_SUB(i.data_de_saida, INTERVAL 1 DAY))) AS d
       WHERE EXTRACT(DAYOFWEEK FROM d) BETWEEN 2 AND 6 AND d NOT IN UNNEST(f.dias))) AS dia,
    i.criado_em IS NULL AS estimado,
    i.tipo_de_input,
    (i.talentos_exclusivos IS NOT NULL AND TRIM(i.talentos_exclusivos) != '') AS exclusivo
  FROM `{tabela_2025}` i CROSS JOIN feriados f
  WHERE i.state = 'active' AND i.tipo_de_input IN UNNEST(@tipos)
)
SELECT
  FORMAT_DATE('%Y-%m', DATE_TRUNC(p.dia, MONTH)) AS mes,
  p.tipo_de_input AS tipo,
  COUNTIF(p.exclusivo) AS exclusivos,
  COUNTIF(NOT p.exclusivo) AS nao_exclusivos_ou_sem,
  COUNTIF(p.estimado) AS estimados,
  COUNT(*) AS total
FROM pedidos p
WHERE p.dia BETWEEN '2025-01-01' AND '2025-12-31'
GROUP BY mes, tipo
ORDER BY tipo, mes
"""


class SnapshotInvalido(ValueError):
    """O snapshot não cumpre o contrato: a rotina para antes de gravar retrato e histórico (G4-N13)."""


def validar(serie: pd.DataFrame, excl: pd.DataFrame) -> tuple[list[str], list[str]]:
    """(problemas que impedem gravar, diferenças só registradas no log)."""
    problemas, avisos = [], []
    if serie.empty:
        return ["série vazia"], avisos
    for col in ("processado_em", "dados_ate"):
        if serie[col].isna().any() or serie[col].astype(str).nunique() != 1:
            problemas.append(f"{col} ausente ou misturado")
    for c in ("pedidos", "estimados"):
        v = pd.to_numeric(serie[c], errors="coerce")
        if v.isna().any() or (v < 0).any() or (v % 1 != 0).any():
            problemas.append(f"contagem inválida: {c}")
    for tipo in TIPOS:
        d = serie[(serie["tipo"] == tipo) & serie["completo"].astype(str).str.lower().isin(["true", "1"])]
        if d.empty:
            problemas.append(f"{tipo}: sem mês completo")
            continue
        meses = pd.PeriodIndex(d["mes"], freq="M").sort_values()
        faltam = sorted(set(pd.period_range(meses.min(), meses.max(), freq="M")) - set(meses))
        if faltam:
            problemas.append(f"{tipo}: meses completos sem dado {[str(m) for m in faltam]}")
    if not excl.empty:
        if excl["processado_em"].astype(str).nunique() != 1 or str(excl["processado_em"].iloc[0]) != str(serie["processado_em"].iloc[0]):
            problemas.append("exclusividade de outra carga")
        partes = excl["exclusivos"] + excl["nao_exclusivos"] + excl["sem_talento"]
        for _, r in excl.loc[partes != excl["total"]].iterrows():
            problemas.append(f"exclusividade {r['tipo']} {r['mes']}: partes não somam o total")
        tot = serie.set_index(["mes", "tipo"])["pedidos"]
        for _, r in excl.iterrows():
            g = tot.get((r["mes"], r["tipo"]))
            if g is not None and int(g) != int(r["total"]):
                avisos.append(f"{r['tipo']} {r['mes']}: entradas {int(g)} × exclusividade {int(r['total'])}")
        # D56: os recortes S3/S4 precisam de todos os meses de 2026 até o último fechado (sem buraco)
        merc = excl[excl["tipo"] == "Mercado"]
        fechados = serie[(serie["tipo"] == "Mercado") & serie["completo"].astype(str).str.lower().isin(["true", "1"])
                         & (serie["mes"] >= "2026-01")]["mes"]
        faltam = sorted(set(fechados) - set(merc["mes"]))
        if faltam:
            problemas.append(f"exclusividade do Mercado sem os meses {faltam}")
    return problemas, avisos


def _gravar_csv(df: pd.DataFrame, destino: Path) -> None:
    """Troca atômica (temporário + os.replace): a rotina e o site nunca leem um CSV pela metade (G4-N13)."""
    tmp = destino.with_suffix(".tmp")
    df.to_csv(tmp, index=False)
    os.replace(tmp, destino)


def extrair() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    os.environ.setdefault("CLOUDSDK_CONFIG", "C:/Users/CCMB/AppData/Roaming/gcloud-viu")
    os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS",
                          "C:/Users/CCMB/AppData/Roaming/gcloud-viu/application_default_credentials.json")
    from google.cloud import bigquery

    from app import config

    cliente = bigquery.Client(project=config.PROJETO)
    tipos = bigquery.ArrayQueryParameter("tipos", "STRING", list(TIPOS))

    def consulta(sql: str, *parametros) -> pd.DataFrame:
        return cliente.query(sql, job_config=bigquery.QueryJobConfig(
            labels=config.LABELS, query_parameters=list(parametros))).to_dataframe()

    serie = consulta(SQL_SERIE.format(previsao_mensal=config.TAB_PREVISAO_MENSAL), tipos,
                     bigquery.ScalarQueryParameter("inicio", "DATE", INICIO))
    dados_ate = serie["dados_ate"].iloc[0]
    fim = bigquery.ScalarQueryParameter("fim", "DATE", dados_ate)
    excl = consulta(SQL_EXCLUSIVIDADE.format(exclusividade=config.TAB_EXCLUSIVIDADE_MENSAL), tipos, fim)
    excl["processado_em"] = serie["processado_em"].iloc[0]
    excl["dados_ate"] = dados_ate
    excl25 = consulta(SQL_EXCLUSIVIDADE_2025.replace("{tabela_2025}", config.TAB_SILVER_2025), tipos)
    lotes = consulta(SQL_LOTES.format(lotes=config.TAB_LOTES), fim)
    for df in (excl25, lotes):
        df["processado_em"] = serie["processado_em"].iloc[0]
        df["dados_ate"] = dados_ate
    return serie, excl, excl25, lotes


def _completo(x) -> bool:
    return str(x).lower() in ("true", "1")


def montar_recortes(serie: pd.DataFrame, excl: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """D56 (S1–S4): uma tabela por recorte, com o mesmo `completo`, carga e corte da gold (nada é repartido)."""
    proc, ate = str(serie["processado_em"].iloc[0]), str(serie["dados_ate"].iloc[0])
    saida = {}
    for chave, r in RECORTES.items():
        g = serie[serie["tipo"] == r["tipo"]].sort_values("mes")
        completo = dict(zip(g["mes"], g["completo"].map(_completo)))
        if r["grupo"] is None:
            d = pd.DataFrame({"mes": g["mes"], "pedidos": g["pedidos"].astype(int), "completo": g["completo"].map(_completo)})
        else:
            e = excl[excl["tipo"] == r["tipo"]].sort_values("mes")
            d = pd.DataFrame({"mes": e["mes"], "pedidos": e[r["grupo"]].astype(int),
                              "completo": [completo.get(m, False) for m in e["mes"]]})
        d["fonte"] = r["fonte"]
        d["dados_ate"], d["processado_em"] = ate, proc
        saida[chave] = d.reset_index(drop=True)
    return saida


def montar_sensibilidade(recortes: dict[str, pd.DataFrame], excl25: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """S5: as séries S3/S4 com os 12 meses de 2025 da silver 2025 na frente (fonte fraca; só para ml/sensibilidade)."""
    saida = {}
    for chave, r in SENSIBILIDADE.items():
        base = recortes[r["base"]]
        e = excl25[excl25["tipo"] == "Mercado"].sort_values("mes")
        antes = pd.DataFrame({"mes": e["mes"], "pedidos": e[r["col_2025"]].astype(int), "completo": True,
                              "fonte": "silver 2025 (talentos_exclusivos preenchido), fonte fraca",
                              "dados_ate": base["dados_ate"].iloc[0], "processado_em": base["processado_em"].iloc[0]})
        saida[chave] = pd.concat([antes, base], ignore_index=True)
    return saida


def gravar_recortes(serie: pd.DataFrame | None = None, excl: pd.DataFrame | None = None,
                    excl25: pd.DataFrame | None = None, pasta: Path = PASTA) -> dict[str, pd.DataFrame]:
    """Grava ml/dados/serie_<recorte>.csv (S1–S4) e, com a silver 2025, serie_<sensibilidade>.csv."""
    serie = carregar_snapshot() if serie is None else serie
    excl = carregar_exclusividade() if excl is None else excl
    rec = montar_recortes(serie, excl)
    if excl25 is None and ARQ_EXCLUSIVIDADE_2025.exists():
        excl25 = pd.read_csv(ARQ_EXCLUSIVIDADE_2025, dtype={"mes": str})
    if excl25 is not None and not excl25.empty:
        rec.update(montar_sensibilidade(rec, excl25))
    Path(pasta).mkdir(exist_ok=True)
    for chave, d in rec.items():
        _gravar_csv(d, Path(pasta) / f"serie_{chave}.csv")
    return rec


def gravar() -> None:
    serie, excl, excl25, lotes = extrair()
    problemas, avisos = validar(serie, excl)
    for a in avisos:
        print(f"aviso (entradas × exclusividade): {a}")
    if problemas:  # G4-N13: nada gravado; a rotina para e o retrato/histórico ficam como estavam
        raise SnapshotInvalido("; ".join(problemas))
    PASTA.mkdir(exist_ok=True)
    _gravar_csv(serie, ARQ_SERIE)
    _gravar_csv(excl, ARQ_EXCLUSIVIDADE)
    _gravar_csv(excl25, ARQ_EXCLUSIVIDADE_2025)
    _gravar_csv(lotes, ARQ_LOTES)
    gravar_recortes(serie, excl, excl25)
    print(f"snapshot gravado: carga {serie['processado_em'].iloc[0]} · dados até {serie['dados_ate'].iloc[0]}")
    print(serie.pivot(index="mes", columns="tipo", values="pedidos").to_string())
    print(excl.to_string(index=False))


def carregar_snapshot() -> pd.DataFrame:
    return pd.read_csv(ARQ_SERIE, dtype={"mes": str})


def carregar_exclusividade() -> pd.DataFrame:
    return pd.read_csv(ARQ_EXCLUSIVIDADE, dtype={"mes": str})


def carregar_recorte(chave: str, pasta: Path = PASTA) -> pd.DataFrame:
    return pd.read_csv(Path(pasta) / f"serie_{chave}.csv", dtype={"mes": str})


def carregar_lotes() -> pd.DataFrame | None:
    return pd.read_csv(ARQ_LOTES, dtype={"mes": str}) if ARQ_LOTES.exists() else None


if __name__ == "__main__":
    gravar()
