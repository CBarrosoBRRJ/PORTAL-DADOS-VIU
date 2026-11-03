"""Contrato com a página "Previsão de demanda" (v3, D56 — 26/10/2026; revisa a D48 e a D55): monta ml/saida/previsao.json
a partir de ml/saida/resultados.json (a régua, com as 4 séries) e dos snapshots de ml/dados.

A página do site NÃO importa nada daqui nem das bibliotecas de ML: ela só lê o JSON (app/.../previsao/calculos.py).

DECISÃO D56 (Caio, 26/10/2026)
  Uma série e um modelo por recorte, cada um treinado na sua própria série (sem repartição por proporção):
    Inbound (todo o Inbound, que é todo de talento exclusivo, PD24), Mercado (total), Mercado exclusivos e Mercado não
    exclusivos (ml/dados.py, S1–S4). Filtro Todos -> Inbound e Mercado; Exclusivos -> Inbound e Mercado exclusivos;
    Não exclusivos -> só Mercado não exclusivos (o Inbound "não se aplica").
  Todos os modelos em todas as séries, na mesma régua (ml/regua.py, D48 + R7 para as séries curtas).
  Critério (C1, o da D48): vence, por série, o MENOR WAPE no horizonte 1 de jun–set/2026, entre os que se aplicam;
    empate = diferença menor que 1 ponto: fica o mais simples (COMPLEXIDADE abaixo). A escolha é feita no próprio
    teste (otimista); a verificação jan–mai (fora da escolha) e o registro mensal (PD09) medem fora dela.
  Robustez (C5, informativa, D56 item 2): o vencedor é "robusto" se bate a ingênua (repetir o último mês) no teste E
    na verificação. Não robusto -> a tela e o diálogo dizem; `alternativa` = o de menor erro no teste entre os que
    batem a ingênua nos dois períodos (empate < 1 ponto = o mais simples). Série curta (sem verificação) -> robustez
    "sem verificação" e confiança menor. A alternativa NÃO troca o vencedor: é a recomendação para o Caio decidir.
  Sem confiança (C3): média da série no teste abaixo de 30 pedidos/mês ou WAPE acima de 40% -> sem número na tela.
  Métricas: WAPE (principal), MAE, viés, cobertura da faixa p10–p90. F1/ROC/acurácia não se aplicam (contagem).

EXECUÇÃO MENSAL (C4)
  O retrato é refeito uma vez por mês, quando a carga traz um mês fechado ainda sem retrato (ml.rodar --rotina). O mês
  em andamento aparece com a previsão de fechamento do retrato (não recalculada) e o realizado até a véspera da carga,
  atualizado a cada carga só no bloco "acompanhamento" (ml.rodar --acompanhamento; segundos, sem modelos).

REGRAS DO CONTRATO (v3)
  P1 Séries = os 4 recortes (S1–S4), cada uma com a fonte, o início e se é curta (R7).
  P2 Backtest exibido = o do vencedor de cada série (h1 de jun–set no gráfico).
  P3 Futuro = os 3 meses depois do último mês fechado, com a faixa p10–p90 do vencedor da série.
  P4 Filtros = a lista de séries de cada filtro (FILTROS); o Inbound não exclusivo "não se aplica" (P8).
  P5 Modelo contra modelo: em cada série, todos os modelos (`comparados`, agrupados por família; "não se aplica" com o
     motivo), com o erro no teste e na verificação — é o que o diálogo "Modelos comparados" mostra.
  P6 Versão do contrato = VERSAO; a página recusa outra versão (mostra a máscara).
  P7 Registro (PD09): um retrato por mês fechado e por protocolo em ml/saida/historico_previsoes.jsonl (e a cópia
     completa em ml/saida/retratos/<mês>.json). D56: a mudança de método grava uma linha nova para o mesmo retrato
     (protocolo "D56", campo `substitui`), sem apagar a da D48.
  P8 Inbound só de exclusivos (D55): no filtro Exclusivos, o Inbound é o Inbound inteiro; no Não exclusivos, não se
     aplica. Os casos de Inbound marcados como não exclusivos (erro de cadastro, PD24) ficam no bloco "qualidade".
  P9 Comparação automática (D55): o bloco "comparacao_automatica" (AutoTS, rede neural, referências e o vencedor nas
     séries longas), para a ficha.
  P10 Mês em andamento (D56 item 3): o acompanhamento traz, por série, o realizado até a véspera da carga, os dias
     úteis decorridos e, do diagnóstico S6, os pedidos em lote e avulsos até o mesmo dia do mês no mês vigente e nos
     4 meses fechados anteriores — a explicação, com dados, de um mês que corre fora do previsto.
"""

import json
import math
import os
import shutil
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import pandas as pd

from app.expediente import sem_expediente
from ml import dados, regua
from ml.calendario import dias_uteis

VERSAO = 3
PROTOCOLO = "D56"
SAIDA = Path(__file__).resolve().parent / "saida"
RESULTADOS = SAIDA / "resultados.json"
PREVISAO = SAIDA / "previsao.json"
RETRATOS = SAIDA / "retratos"
HISTORICO = SAIDA / "historico_previsoes.jsonl"

METRICA = "wape"
EMPATE = 0.01          # C1: diferença menor que 1 ponto = empate
POUCOS = 30            # C3: média da série no teste (pedidos/mês)
LIMITE_WAPE = 0.40     # C3: acima disto, sem número
INGENUA = "ref_ultimo_mes"
SERIES = tuple(r["serie"] for r in dados.RECORTES.values())
NAO_SE_APLICA_TXT = "Não se aplica: todo Inbound é de talento exclusivo"
# P4 (D56): o que cada filtro mostra, na ordem da tela (o Mercado sempre à direita)
FILTROS = {
    "todos": [{"serie": "Inbound"}, {"serie": "Mercado"}],
    "exclusivos": [{"serie": "Inbound", "nota": "todo o Inbound é de talento exclusivo"}, {"serie": "Mercado exclusivos"}],
    "nao_exclusivos": [{"serie": None, "tipo": "Inbound", "nao_se_aplica": NAO_SE_APLICA_TXT},
                       {"serie": "Mercado não exclusivos"}],
}

# C1: nível de complexidade para o desempate (menor = mais simples); dentro da rede neural, menos neurônios
NIVEL_MODULO = {"referencia": 0, "combinacao": 1, "classico": 2, "arimax": 3, "prophet": 3, "boosting": 4, "neural": 5,
                "automatico": 6}  # D55: a busca automática (AutoTS) conta como a mais complexa
SO_EXCLUSIVOS = ("Inbound",)  # P8 (D55): tipos em que todo pedido é de talento exclusivo
AUTOMATICOS = ("autots_1", "autots_2", "autots_3")
NEURAIS = ("mlp_1", "mlp_auto")
REFERENCIAS = ("ref_ultimo_mes", "ref_media_3m", "ref_media_6m")
# ordem das famílias no diálogo (da mais simples à mais complexa)
ORDEM_FAMILIA = ("referencia", "combinacao", "classico", "arimax", "prophet", "boosting", "neural", "automatico")


def complexidade(nome: str, modulo: str | None) -> tuple[int, int]:
    """(nível da família, tamanho dentro dela). Rede neural: o tamanho = nº de neurônios (mlp_4x2 = 6); a escolhida
    no treino (mlp_auto) conta como a maior, porque ainda soma a busca pelo tamanho."""
    if modulo == "arimax" and nome.startswith("arima_"):
        return 2, 0  # ARIMA sem variáveis externas = série clássica
    sub = 0
    if modulo == "neural":
        partes = nome.removeprefix("mlp_").split("x")
        sub = sum(int(x) for x in partes) if all(x.isdigit() for x in partes) else 99
    return NIVEL_MODULO.get(modulo or "", 9), sub


ROTULO = {
    "ref_ultimo_mes": "Último mês", "ref_media_3m": "Média de 3 meses", "ref_media_6m": "Média de 6 meses",
    "ref_mesmo_mes_ano_anterior": "Mesmo mês do ano anterior", "ref_tendencia_6m": "Reta dos últimos 6 meses",
    "comb_ses": "Suavização exponencial", "comb_holt_amort": "Holt amortecido simples", "comb_theta": "Theta simples",
    "comb_drift": "Último mês + crescimento médio", "comb_sazonal": "Patamar × mesmo mês do ano anterior",
    "comb_mediana": "Combinação de 6", "comb_media": "Média de 3 métodos", "comb_selecao": "Seleção pelo passado",
    "comb_ponderada": "Combinação ponderada", "comb_drift_log": "Crescimento % médio",
    "comb_holt_amort_log": "Holt em escala log", "comb_mediana_mult": "Combinação de crescimento %",
    "comb_mediana_corr": "Combinação de 6 corrigida", "comb_theta_corr": "Theta corrigido",
    "cls_holt_amortecido": "Holt amortecido", "cls_ets_aicc": "ETS", "cls_theta": "Theta",
    "cls_arima_aicc": "ARIMA pequeno (AICc)", "cls_combinado": "Combinação clássica", "cls_validado": "Clássico validado",
    "cls_arima_aicc_faixa_erros": "ARIMA pequeno, faixa dos erros",
    "cls_holt_amortecido_faixa_erros": "Holt amortecido, faixa dos erros",
    "arima_100_ct": "ARIMA com tendência", "arimax_100_ct": "ARIMAX (calendário)",
    "arimax_100_ct_fimdeano": "ARIMAX (nov/dez)", "arima_011": "ARIMA (0,1,1)", "arimax_011": "ARIMAX (0,1,1)",
    "arima_110": "ARIMA (1,1,0)", "arimax_110": "ARIMAX (1,1,0)", "arima_011_t": "ARIMA (0,1,1) com deriva",
    "arimax_011_t": "ARIMAX (0,1,1) com deriva", "arima_auto": "ARIMA automático", "arimax_auto": "ARIMAX automático",
    "prophet_auto": "Prophet", "prophet_log_sem_sazonal": "Prophet (log)", "prophet_log": "Prophet sazonal (log)",
    "prophet_natural": "Prophet sazonal", "prophet_log_degrau2026": "Prophet sazonal com degrau 2026",
    "boost_lgbm": "LightGBM", "boost_xgb": "XGBoost", "boost_lgbm_n1": "LightGBM (âncora no último mês)",
    "boost_auto": "Gradient boosting", "mlp_auto": "Rede neural (tamanho no treino)",
    "autots_1": "AutoTS (1º colocado)", "autots_2": "AutoTS (2º colocado)", "autots_3": "AutoTS (3º colocado)",
}
FAMILIA = {"referencia": "Referência simples", "classico": "Série clássica", "arimax": "ARIMA / ARIMAX",
           "prophet": "Prophet", "boosting": "Gradient boosting", "neural": "Rede neural", "combinacao": "Combinação",
           "automatico": "Busca automática (AutoTS)"}
# criados depois de ver o teste de jan–set/2026 da D47 (selo "exploratório"): jun–set está dentro daquele teste
POS_HOC = ("arimax_100_ct_fimdeano", "boost_lgbm_n1", "comb_drift_log", "comb_holt_amort_log", "comb_mediana_mult",
           "comb_mediana_corr", "comb_theta_corr")


def rotulo(nome: str) -> str:
    if nome in ROTULO:
        return ROTULO[nome]
    if nome.startswith("mlp_"):
        partes = nome[4:].split("x")
        if all(x.isdigit() for x in partes):
            n = " + ".join(partes)
            return f"Rede neural ({n} neurônio{'s' if n != '1' else ''})"
    if nome.startswith("arimax_"):
        return f"ARIMAX {nome[7:]}"
    if nome.startswith("arima_"):
        return f"ARIMA {nome[6:]}"
    return nome


def _met(m: dict) -> dict:
    """Métricas de um modelo numa série: chave -> {wape, mae, vies, cobertura, largura, n}."""
    return {h: {"wape": v["wape"], "mae": v["mae"], "vies": v["vies"], "cobertura": v["cobertura_80"],
                "largura": v["largura"], "n": v["n"]} for h, v in m["metricas"].items()}


def _num(w):
    return None if w is None or (isinstance(w, float) and math.isnan(w)) else w


def _wape1(m: dict, serie: str, chave: str = "1"):
    try:
        return _num(m["series"][serie]["metricas"][chave]["wape"])
    except (KeyError, TypeError):
        return None


def escolher(modelos: dict, serie: str, nomes=None) -> dict:
    """C1: menor WAPE h1 jun–set; empate (< EMPATE) = o mais simples. Devolve vencedor, empatados e o ranking.
    `nomes` restringe a disputa (C5: só quem bate a ingênua nos dois períodos)."""
    validos = [(n, w, complexidade(n, m.get("modulo"))) for n, m in modelos.items()
               if (nomes is None or n in nomes) and (w := _wape1(m, serie)) is not None]
    if not validos:
        raise ValueError(f"nenhum modelo com resultado para {serie}")
    menor = min(w for _, w, _ in validos)
    empatados = [x for x in validos if x[1] - menor < EMPATE]
    venc = min(empatados, key=lambda x: (x[2], x[1], x[0]))
    ranking = sorted(validos, key=lambda x: (x[1], x[2], x[0]))
    return {"vencedor": venc[0], "wape": venc[1], "menor": menor,
            "empatados": [n for n, _, _ in sorted(empatados, key=lambda x: (x[2], x[1]))],
            "ranking": [{"nome": n, "wape": w, "nivel": c[0]} for n, w, c in ranking], "n_modelos": len(validos)}


def _motivo(serie: str, e: dict, modelos: dict) -> str:
    ing = _wape1(modelos.get(INGENUA, {}), serie)
    txt = (f"Menor erro no teste de jun–set/2026 (horizonte 1) entre os {e['n_modelos']} modelos que se aplicam: "
           f"{e['wape']:.0%}")
    if ing is not None:
        txt += f"; repetir o último mês errou {ing:.0%}"
    txt += "."
    outros = [rotulo(n) for n in e["empatados"] if n != e["vencedor"]]
    if outros:
        txt += (f" Empatou (menos de 1 ponto de diferença) com {', '.join(outros[:3])}"
                f"{' e outros' if len(outros) > 3 else ''}; pela regra, ficou o mais simples.")
    return txt


def robustez(modelos: dict, serie: str, vencedor: str) -> dict:
    """C5 (D56): o vencedor bate a ingênua no teste e na verificação? Se não, a alternativa robusta (C1 restrita)."""
    ing_t, ing_v = _wape1(modelos.get(INGENUA, {}), serie), _wape1(modelos.get(INGENUA, {}), serie, "verificacao")
    v_t, v_v = _wape1(modelos[vencedor], serie), _wape1(modelos[vencedor], serie, "verificacao")
    if ing_v is None or v_v is None:
        return {"robusto": None, "texto": "sem verificação: a série começa em jan/2026 (confiança menor)",
                "alternativa": None, "ingenua": {"teste": ing_t, "verificacao": ing_v}}
    robusto = v_t < ing_t and v_v < ing_v
    batem = [n for n, m in modelos.items() if (t := _wape1(m, serie)) is not None and t < ing_t
             and (v := _wape1(m, serie, "verificacao")) is not None and v < ing_v]
    alt = None
    if not robusto and batem:
        e = escolher(modelos, serie, set(batem))
        n = e["vencedor"]
        alt = {"modelo": n, "rotulo": rotulo(n), "teste": _wape1(modelos[n], serie),
               "verificacao": _wape1(modelos[n], serie, "verificacao"), "n_robustos": len(batem),
               "futuro": modelos[n]["futuro"][serie]}
    texto = ("bate a ingênua no teste e fora dele" if robusto else
             f"no teste erra {v_t:.0%} contra {ing_t:.0%} da ingênua, mas em jan–mai erra {v_v:.0%} contra {ing_v:.0%}"
             if v_t < ing_t else f"perde da ingênua no teste ({v_t:.0%} × {ing_t:.0%})")
    return {"robusto": robusto, "texto": texto, "alternativa": alt, "ingenua": {"teste": ing_t, "verificacao": ing_v}}


def comparados(modelos: dict, serie: str, vencedor: str, alternativa: str | None) -> list[dict]:
    """P5: todos os modelos na série, por família (da mais simples à mais complexa), com o erro no teste (h1 jun–set) e
    na verificação (h1 jan–mai); "não se aplica" e falhas com o motivo curto."""
    grupos = {}
    for n, m in modelos.items():
        mod = m.get("modulo")
        linha = {"nome": n, "rotulo": rotulo(n), "pos_hoc": n in POS_HOC, "vencedor": n == vencedor,
                 "alternativa": n == alternativa, "ingenua": n == INGENUA}
        s = (m.get("series") or {}).get(serie, {})
        if "metricas" in s:
            linha.update(teste=_wape1(m, serie), verificacao=_wape1(m, serie, "verificacao"),
                         mae=_num(s["metricas"]["1"]["mae"]))
        else:
            motivo = s.get("nao_se_aplica") or m.get("nao_se_aplica")
            linha["falta"] = "não se aplica" if motivo else "falhou"
            linha["motivo"] = motivo or s.get("erro") or m.get("erro") or "sem resultado"
        grupos.setdefault(mod, []).append(linha)
    saida = []
    for mod in sorted(grupos, key=lambda x: (ORDEM_FAMILIA.index(x) if x in ORDEM_FAMILIA else 99)):
        linhas = sorted(grupos[mod], key=lambda x: (x.get("teste") is None, x.get("teste") or 0, x["nome"]))
        saida.append({"modulo": mod, "familia": FAMILIA.get(mod, mod), "linhas": linhas,
                      "melhor": min((x["teste"] for x in linhas if x.get("teste") is not None), default=None)})
    return saida


# ---------------------------------------------------------------- mês em andamento (P10)

def _lotes(lotes: pd.DataFrame | None, processado_em: str, mes: str) -> dict:
    """S6: por série, o mês do acompanhamento (`mes`) e a média dos meses anteriores a ele (até o mesmo dia do mês).
    Correção de 03/11/2026: o vigente é o mês do acompanhamento, não o último mês presente na base de lotes; série sem
    linha desse mês (nenhum pedido até o dia) ou sem mês anterior fica sem diagnóstico."""
    if lotes is None or lotes.empty or str(lotes["processado_em"].iloc[0]) != str(processado_em):
        return {}
    saida = {}
    for chave, r in dados.RECORTES.items():
        d = lotes[lotes["recorte"] == chave].sort_values("mes")
        meses = d["mes"].astype(str)
        vigente, ant = d[meses == str(mes)], d[meses < str(mes)]
        if vigente.empty or ant.empty:
            continue
        vig = vigente.iloc[-1]
        saida[r["serie"]] = {
            "ate_dia": int(vig["ate_dia"]), "mes": str(vig["mes"]), "meses_anteriores": [str(m) for m in ant["mes"]],
            "vigente": {k: int(vig[k]) for k in ("pedidos", "em_lote", "avulsos")},
            "media_anteriores": {k: float(ant[k].mean()) for k in ("pedidos", "em_lote", "avulsos")}}
    return saida


def _acompanhamento(meta: dict, excl: pd.DataFrame, lotes: pd.DataFrame | None = None) -> dict | None:
    """Mês em andamento: realizado até `dados_ate` por série, dias úteis decorridos / do mês, pedidos ainda sem talento
    informado (ficam fora dos dois recortes de exclusividade) e o diagnóstico de lotes (P10)."""
    p = meta.get("parcial") or {}
    if not p:
        return None
    mes = pd.Period(next(iter(p.values()))["mes"], "M")
    ate = date.fromisoformat(str(meta["dados_ate"])[:10])
    folgas = sem_expediente(mes.year)
    d, decorridos = date(mes.year, mes.month, 1), 0
    while d <= ate:
        decorridos += d.weekday() < 5 and d not in folgas
        d += timedelta(days=1)
    sem_talento = {}
    for tipo in dados.TIPOS:
        linha = excl[(excl["tipo"] == tipo) & (excl["mes"] == str(mes))]
        sem_talento[tipo] = int(linha["sem_talento"].iloc[0]) if len(linha) else None
    return {"mes": str(mes), "ate": str(ate), "processado_em": meta["processado_em"],
            "dias_uteis_decorridos": decorridos, "dias_uteis_mes": dias_uteis(mes),
            "pedidos": {s: v["pedidos_ate_agora"] for s, v in p.items() if v["mes"] == str(mes)},
            "sem_talento": sem_talento, "lotes": _lotes(lotes, meta["processado_em"], str(mes))}


def _exclusividade(excl: pd.DataFrame) -> dict:
    saida = {}
    for tipo in dados.TIPOS:
        d = excl[excl["tipo"] == tipo].sort_values("mes")
        saida[tipo] = {str(r.mes): {"exclusivos": int(r.exclusivos), "nao_exclusivos": int(r.nao_exclusivos),
                                    "sem_talento": int(r.sem_talento), "total": int(r.total)} for r in d.itertuples()}
    return saida


def qualidade(excl_d: dict, mes_fechado: str) -> dict:
    """P8 (D55, PD24): pedidos de Inbound marcados como de talento NÃO exclusivo no board 2026 (erro de cadastro; gold de
    exclusividade, D57), por mês; o mês em andamento entra separado (parcial)."""
    blocos = {}
    for tipo in SO_EXCLUSIVOS:
        meses = excl_d.get(tipo, {})
        por_mes = {m: v["nao_exclusivos"] for m, v in sorted(meses.items())}
        fechados = {m: n for m, n in por_mes.items() if m <= mes_fechado}
        total_fechados = sum(v["total"] for m, v in meses.items() if m <= mes_fechado)
        blocos[tipo] = {"pendencia": "PD24", "regra": "todo Inbound é de talento exclusivo; não exclusivo = erro de cadastro",
                        "por_mes": por_mes, "fechados": sum(fechados.values()),
                        "parcial": sum(n for m, n in por_mes.items() if m > mes_fechado),
                        "pct_fechados": sum(fechados.values()) / total_fechados if total_fechados else None,
                        "meses_com_caso": sum(1 for n in fechados.values() if n)}
    return {"nao_exclusivo_no_inbound": blocos}


def comparacao_automatica(modelos: dict, escolha: dict) -> dict:
    """P9 (D55): por série longa, os 3 colocados do AutoTS, a rede neural, as referências e o vencedor, com o teste
    jun–set (h1), a verificação jan–mai e o que o AutoTS escolheu em cada janela."""
    saida = {}
    for serie, e in escolha.items():
        linhas = []
        for grupo, nomes in (("autots", AUTOMATICOS), ("rede_neural", NEURAIS), ("referencia", REFERENCIAS),
                             ("vencedor", (e["vencedor"],))):
            for n in nomes:
                m = modelos.get(n)
                if any(x["nome"] == n for x in linhas):
                    continue
                s = (m or {}).get("series", {}).get(serie, {})
                if "metricas" not in s:
                    if m and grupo == "autots":
                        linhas.append({"grupo": grupo, "nome": n, "rotulo": rotulo(n),
                                       "falta": s.get("nao_se_aplica") or s.get("erro") or m.get("erro")
                                       or m.get("nao_se_aplica") or "sem resultado"})
                    continue
                met = _met(s)
                det = [x for x in ((m.get("detalhe") or {}).get("escolhas") or []) if x["serie"] == serie]
                linhas.append({"grupo": grupo, "nome": n, "rotulo": rotulo(n), "vencedor": n == e["vencedor"],
                               "teste": met.get("1"), "verificacao": met.get("verificacao"), "h1_h3": met.get("todos"),
                               "escolhas": [{"treino_fim": x["treino_fim"], "modelo": x["modelo"],
                                             "transformacoes": x.get("transformacoes"), "posicao": x.get("posicao")}
                                            for x in det]})
        saida[serie] = {"vencedor": e["vencedor"], "linhas": linhas,
                        "posicao_melhor_autots": next((i + 1 for i, r in enumerate(e["ranking"])
                                                       if r["nome"] in AUTOMATICOS), None)}
    return saida


# ---------------------------------------------------------------- montagem

def montar(resultados: dict, excl: pd.DataFrame, lotes: pd.DataFrame | None = None,
           gerado_em: datetime | None = None) -> dict:
    modelos = resultados["modelos"]
    carga = resultados["carga"]
    mes_fechado = carga.get("mes_fechado") or max(max(h) for h in resultados["historico"].values())
    recortes = carga.get("recortes") or {}
    series, escolha = {}, {}
    for nome in SERIES:
        if nome not in resultados["historico"]:
            continue
        e = escolher(modelos, nome)
        escolha[nome] = e
        v = modelos[e["vencedor"]]
        rob = robustez(modelos, nome, e["vencedor"])
        hist = resultados["historico"][nome]
        teste = [b for b in v["series"][nome]["backtest"] if b["trecho"] == "teste" and b["horizonte"] == 1]
        media = sum(b["real"] for b in teste) / len(teste) if teste else None
        w = _wape1(v, nome)
        info = recortes.get(nome, {})
        series[nome] = {
            "nome": nome, "chave": info.get("chave"), "tipo": info.get("tipo"), "grupo": info.get("grupo"),
            "fonte": info.get("fonte"), "inicio": info.get("inicio"), "meses": info.get("meses"),
            "treino_1o_teste": info.get("treino_1o_teste"), "curta": bool(info.get("curta")),
            "modelo": e["vencedor"], "rotulo": rotulo(e["vencedor"]), "descricao": v.get("descricao", ""),
            "familia": FAMILIA.get(v.get("modulo"), v.get("modulo")), "pos_hoc": e["vencedor"] in POS_HOC,
            "motivo": _motivo(nome, e, modelos), "empatados": e["empatados"], "n_modelos": e["n_modelos"],
            "historico": hist,
            "backtest": v["series"][nome]["backtest"], "futuro": v["futuro"][nome],
            "metricas": _met(v["series"][nome]),
            "ingenua": {"modelo": INGENUA, "wape": rob["ingenua"]["teste"], "verificacao": rob["ingenua"]["verificacao"]},
            "robustez": rob,
            "comparados": comparados(modelos, nome, e["vencedor"], (rob["alternativa"] or {}).get("modelo")),
            "media_teste": media, "poucos": media is not None and media < POUCOS,
            "erro_alto": w is not None and w > LIMITE_WAPE,
        }
        series[nome]["confiavel"] = not (series[nome]["poucos"] or series[nome]["erro_alto"])
    excl_d = _exclusividade(excl)
    tabela = []
    for nome, m in modelos.items():
        base = {"nome": nome, "rotulo": rotulo(nome), "modulo": m.get("modulo"), "descricao": m.get("descricao", ""),
                "familia": FAMILIA.get(m.get("modulo"), m.get("modulo")), "pos_hoc": nome in POS_HOC,
                "minimo_treino": m.get("minimo_treino"), "carga": m.get("carga", carga["processado_em"]),
                "segundos": m.get("segundos")}
        if "series" in m:
            base["series"] = {t: (_met(m["series"][t]) if "metricas" in m["series"][t] else
                                  {"nao_se_aplica": m["series"][t].get("nao_se_aplica"), "erro": m["series"][t].get("erro")})
                              for t in SERIES if t in m["series"]}
        elif "nao_se_aplica" in m:
            base["nao_se_aplica"] = m["nao_se_aplica"]
        else:
            base["erro"] = m.get("erro", "sem resultado")
        tabela.append(base)
    longas = {n: e for n, e in escolha.items() if not series[n]["curta"]}
    return {
        "versao": VERSAO, "protocolo": PROTOCOLO,
        "gerado_em": (gerado_em or datetime.now(UTC)).isoformat(timespec="seconds"),
        "carga": {"processado_em": carga["processado_em"], "dados_ate": carga["dados_ate"]},
        "retrato": {"mes_fechado": mes_fechado, "processado_em": carga["processado_em"], "dados_ate": carga["dados_ate"]},
        "regua": resultados.get("regua"),
        "decisao": {"metrica": METRICA, "criterio": "menor WAPE h1 jun–set/2026; empate < 1 ponto = o mais simples",
                    "robustez": "bate a ingênua no teste e na verificação (informativo; alternativa = C1 entre os robustos)",
                    "empate": EMPATE, "poucos": POUCOS, "limite_wape": LIMITE_WAPE,
                    "vencedor": {t: e["vencedor"] for t, e in escolha.items()},
                    "ranking": {t: e["ranking"] for t, e in escolha.items()}},
        "filtros": FILTROS,
        "acompanhamento": _acompanhamento(carga, excl, lotes),
        "series": series,
        "exclusividade": excl_d,
        "qualidade": qualidade(excl_d, mes_fechado),
        "comparacao_automatica": comparacao_automatica(modelos, longas),
        "pos_hoc": list(POS_HOC),
        "modelos": tabela,
    }


def _limpo(o):
    if isinstance(o, float) and math.isnan(o):
        return None
    if isinstance(o, dict):
        return {k: _limpo(v) for k, v in o.items()}
    if isinstance(o, list):
        return [_limpo(v) for v in o]
    return o


def _gravar_json(p: dict, destino: Path) -> None:
    """Grava de forma atômica (arquivo temporário + troca): a página nunca lê um arquivo pela metade."""
    destino = Path(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)
    tmp = destino.with_suffix(".tmp")
    tmp.write_text(json.dumps(p, ensure_ascii=False, indent=1), encoding="utf-8")
    os.replace(tmp, destino)


def gravar(origem: Path = RESULTADOS, destino: Path = PREVISAO) -> dict:
    resultados = json.loads(Path(origem).read_text(encoding="utf-8"))
    p = _limpo(montar(resultados, dados.carregar_exclusividade(), dados.carregar_lotes()))
    _gravar_json(p, destino)
    RETRATOS.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(destino, RETRATOS / f"{p['retrato']['mes_fechado']}.json")
    registrar(p)
    return p


def ler(arquivo: Path = PREVISAO) -> dict | None:
    try:
        p = json.loads(Path(arquivo).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return p if p.get("versao") == VERSAO else None


def retrato_existe(mes_fechado: str, arquivo: Path = PREVISAO) -> bool:
    """C4: o retrato deste mês fechado já foi gravado (na versão atual do contrato)?"""
    p = ler(arquivo)
    return bool(p and p.get("retrato", {}).get("mes_fechado") == mes_fechado)


def atualizar_acompanhamento(arquivo: Path = PREVISAO, tabela: pd.DataFrame | None = None,
                             excl: pd.DataFrame | None = None, lotes: pd.DataFrame | None = None) -> bool:
    """C4: troca só o bloco "acompanhamento" (realizado do mês em andamento) pela carga do snapshot atual. Não mexe na
    previsão. Só vale se o snapshot ainda é do mesmo mês fechado do retrato (senão, é hora de um retrato novo)."""
    p = ler(arquivo)
    if not p:
        return False
    tabela = dados.carregar_snapshot() if tabela is None else tabela
    excl = dados.carregar_exclusividade() if excl is None else excl
    _, meta = regua.carregar_recortes(tabelas=dados.montar_recortes(tabela, excl))
    if meta["mes_fechado"] != p["retrato"]["mes_fechado"]:
        return False
    p["acompanhamento"] = _limpo(_acompanhamento(meta, excl, dados.carregar_lotes() if lotes is None else lotes))
    _gravar_json(p, Path(arquivo))
    return True


def linhas_do_historico(arquivo: Path = HISTORICO) -> list[dict]:
    """P7 (G4-N13): as linhas do histórico; toda linha tem "retrato" e "protocolo" (o registro da D47, sem protocolo,
    já está em ml/saida/d47/historico_previsoes.jsonl). Linha fora do contrato = erro, nunca ignorada."""
    arquivo = Path(arquivo)
    if not arquivo.exists():
        return []
    linhas = [json.loads(x) for x in arquivo.read_text(encoding="utf-8").splitlines() if x.strip()]
    for i, x in enumerate(linhas, 1):
        if not x.get("retrato") or not x.get("protocolo"):
            raise ValueError(f"{arquivo.name}, linha {i}: sem retrato ou protocolo")
    return linhas


def registrar(p: dict, arquivo: Path = HISTORICO) -> bool:
    """P7 (PD09): guarda a previsão oficial de cada retrato mensal uma única vez por protocolo (D56: a mudança de método
    entra como linha nova do mesmo retrato, com `substitui`; nenhuma linha é apagada). Devolve True se gravou."""
    arquivo = Path(arquivo)
    mes = p["retrato"]["mes_fechado"]
    protocolo = p.get("protocolo", PROTOCOLO)
    antigas = linhas_do_historico(arquivo)
    if any(x["retrato"] == mes and x["protocolo"] == protocolo for x in antigas):
        return False
    anterior = [x["protocolo"] for x in antigas if x["retrato"] == mes]
    linha = {"retrato": mes, "protocolo": protocolo, "carga": p["carga"]["processado_em"],
             "dados_ate": p["carga"]["dados_ate"], "gerado_em": p["gerado_em"],
             "metodo": "D56: uma série e um modelo por recorte (Inbound, Mercado, Mercado exclusivos, Mercado não "
                       "exclusivos), sem repartição por proporção",
             "substitui": anterior[-1] if anterior else None,
             "previsao": {s: {"modelo": x["modelo"], "futuro": x["futuro"],
                              "robusto": x["robustez"]["robusto"], "curta": x["curta"]}
                          for s, x in p["series"].items()}}
    with open(arquivo, "a", encoding="utf-8") as f:
        f.write(json.dumps(linha, ensure_ascii=False) + "\n")
    return True


if __name__ == "__main__":
    p = gravar()
    for t, s in p["series"].items():
        print(t, s["modelo"], [(f["mes"], round(f["valor"])) for f in s["futuro"]],
              f"WAPE h1 jun–set {s['metricas']['1']['wape']:.1%}")
    print(f"gravado {PREVISAO}")
