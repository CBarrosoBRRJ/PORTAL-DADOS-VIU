"""Talentos (D30, D31, D50): como a demanda do ano se divide entre talentos exclusivos e não exclusivos.

T1  Base: os mesmos pedidos do Início, divididos na gold `gld_agenciamento_2026_talentos_ano` (job da gold, com as regras
    de data da gold de entradas; D57, 27/10/2026, encerra a exceção D30-b da silver).
T2  Exclusividade na data do pedido (a origem não guarda a situação atual); sem talento = grupo próprio, sempre visível,
    com o rótulo "Talento não informado" (o card não tem talento preenchido).
T3  "Squad de Talentos" é um grupo, não uma pessoa: conta em não exclusivos (regra da gold), dito na nota.
T4  Parcelas inteiras que fecham em 100 pelo maior resto (E8c).
T5  Conciliação: o total precisa ser igual ao do Início e o dia da carga deve coincidir. Divergência mostra os números
    com um aviso da diferença, sem bloquear a página (decisão 10, 25/10/2026).
T6  Os 10 talentos com mais pedidos no ano em cada recorte (gold `gld_agenciamento_2026_talentos_ranking`), com pedidos
    e % sobre o total do recorte. Nomes agrupados sem diferença de maiúsculas e espaços; Squad de Talentos fora (grupo);
    um talento por pedido (a origem guarda um nome só; duplas contam como um talento). Nomes na tela por decisão do Caio
    (24/10/2026). Empate no corte (decisão 11, 25/10/2026): a lista segue com 10 nomes (desempate alfabético) e
    termina com a nota "empate com mais N" quando outros talentos têm o mesmo número de pedidos do 10º lugar.

D50 (26/10/2026, pedido do gerente do Caio; revisa a D31, que deixava a página sem visão mensal):
T7  Seletor Todos / Exclusivos / Não exclusivos (?talentos=, o mesmo componente do SLA) filtra a página inteira.
T8  Resposta (herói) por recorte: Todos = % da demanda do ano no maior grupo (hoje exclusivos); Exclusivos e Não
    exclusivos = % dos pedidos do grupo que vão para os 10 talentos mais pedidos do grupo (T6). Denominador = total do
    grupo na divisão do ano (T1), com Squad de Talentos incluído nos não exclusivos (T3).
T9  Barra do ano sempre com os três grupos (contexto); com filtro, o grupo filtrado fica destacado e os outros esmaecidos.
T10 Mapa de calor: os 10 talentos do recorte (T6; "Todos" = exclusivos e não exclusivos juntos pelo mesmo nome) ×
    jan–dez do ano da carga. Mês do pedido = mês da data de entrada (mesmas regras R1/R2/R21 de T1). Soma dos meses =
    total do talento no ano (se não bater, o mapa não aparece). Meses depois do corte = futuros (cinza, sem número);
    o mês do corte, se não terminou, é parcial ("até DD"). Intensidade em 6 tons pelo maior mês do recorte, com o
    número escrito em cada célula.

D51 (26/10/2026, Caio; exceção à D46/D49 só nesta página): ao abrir e ao trocar o filtro, a barra do ano cresce e os
números (barra, resposta, células e Ano) contam até o valor, com o top 10 parado; a "corrida do ano" (subida e descida
das posições) só roda no botão play (apresentacao.js) e termina exatamente neste estado final. Nada muda nos números.
T12 Corrida do ano (botão play): ranking pelo acumulado entre todos os talentos do recorte; vêm da consulta os 10 do ano
    e quem esteve entre os 10 do acumulado no fim de algum mês (gold de ranking, coluna pos); desempate = lugar no ano.
T11 Coluna dos nomes com a largura do maior nome exibido no recorte + ~10% de folga, sem reticências (largura_nomes).
"""

import logging
import math

import pandas as pd

from app.apresentacoes.gestao_orcamentos.entrada.calculos import _pcts
from app.formato import MESES, MESES_EXTENSO, inteiro, pct_inteiro

log = logging.getLogger(__name__)

# categoria na gold (gld_agenciamento_2026_talentos_ano) -> rótulo na tela, classe CSS
GRUPOS = (("Exclusivos", "Exclusivos", "exclusivo"), ("Não exclusivos", "Não exclusivos", "nao-exclusivo"),
          ("Sem talento", "Talento não informado", "sem-talento"))
# T7: chave na URL (a mesma do SLA e da Previsão) -> rótulo do seletor, grupo da consulta de top 10
FILTROS = {"todos": ("Todos", "todos"), "exclusivos": ("Exclusivos", "exclusivo"),
           "nao-exclusivos": ("Não exclusivos", "nao-exclusivo")}
NIVEIS = 6  # T10: tons do mapa de calor (1 a 6; 0 = mês sem pedido)
NOME_MIN, NOME_MAX = 10, 30  # T11: faixa da classe de largura da coluna dos nomes (mapa-nomes-10 … mapa-nomes-30)


def divisao(df: pd.DataFrame, total_inicio: int, ano: int) -> dict | None:
    linhas = df[df["ano"] == ano].set_index("categoria") if not df.empty else df
    if linhas.empty:
        return None
    ns = [int(linhas["n"].get(categoria, 0)) for categoria, _, _ in GRUPOS]
    total = sum(ns)
    grupos = [{"nome": rotulo, "classe": classe, "n": n, "pct": pct, "largura": round(n / total * 100, 3) if total else 0}
              for (_, rotulo, classe), n, pct in zip(GRUPOS, ns, _pcts(ns))]
    return {
        "ano": ano,
        "total": total,
        "grupos": grupos,
        "principal": max(grupos, key=lambda g: g["n"]),
        "squad": int(linhas["dos_quais_squad"].sum()),
        "total_inicio": total_inicio,
        "diferenca": total - total_inicio,
    }


def top_por_grupo(df: pd.DataFrame, divisao_ano: dict | None) -> dict:
    """T6: {grupo: {"linhas": [...], "n": soma dos 10, "pct": parcela do grupo, ...}}, % sobre o total do grupo
    ("todos" = total do ano). Com as colunas mes/n_mes (D50), cada linha leva também os pedidos por mês (T10)."""
    if df.empty or not divisao_ano:
        return {}
    totais = {g["classe"]: g["n"] for g in divisao_ano["grupos"]}
    totais["todos"] = divisao_ano["total"]
    mensal = "mes" in df.columns and "n_mes" in df.columns
    saida = {}
    for grupo, d in df.groupby("grupo", sort=False):
        total = totais.get(grupo, 0)
        meses: dict[str, dict[int, int]] = {}
        if mensal:
            for r in d.dropna(subset=["mes"]).itertuples():
                m = pd.Timestamp(r.mes).month
                meses.setdefault(r.talento, {})[m] = meses.get(r.talento, {}).get(m, 0) + int(r.n_mes)
        corrida = []
        if "pos" in d.columns:  # D51: quem passou pelos 10 do acumulado em algum mês, mas não fechou o ano entre eles
            fora_do_top = d[d["pos"] > 10].drop_duplicates("talento").sort_values("pos")
            corrida = [{"talento": r.talento, "pos": int(r.pos), "n": int(r.n), "meses": meses.get(r.talento, {})}
                       for r in fora_do_top.itertuples()]
            d = d[d["pos"] <= 10]
        d = d.drop_duplicates("talento").sort_values(["n", "talento"], ascending=[False, True]).head(10)
        if total <= 0 or d['n'].sum() > total:
            continue  # ranking e denominador não reconciliam; nunca apresentar concentração >100%
        linhas = [{"posicao": i + 1, "talento": r.talento, "n": int(r.n), "meses": meses.get(r.talento, {}),
                   "ultimo": pd.Timestamp(r.ultimo_pedido).strftime("%d/%m") if pd.notna(r.ultimo_pedido) else "–"}
                  for i, r in enumerate(d.itertuples())]
        soma = sum(r["n"] for r in linhas)
        fora = int(d["empate_fora"].max()) if "empate_fora" in d and len(d) == 10 and d["empate_fora"].notna().any() else 0
        n_talentos = int(d["talentos_grupo"].max()) if "talentos_grupo" in d and d["talentos_grupo"].notna().any() else None
        saida[grupo] = {"linhas": linhas, "n": soma, "total": total, "pct": pct_inteiro(soma, total),  # F13: meio para cima
                        "talentos": n_talentos, "mensal": mensal, "corrida": corrida,
                        "empate": {"fora": fora, "n": linhas[-1]["n"]} if fora else None}
    return saida


def seletor(t: dict, filtro: str) -> list[dict]:
    """T7: os três botões, cada um com o total de pedidos do recorte (o que o filtro abre)."""
    n = {g["classe"]: g["n"] for g in t["grupos"]}
    valores = {"todos": t["total"], "exclusivos": n.get("exclusivo", 0), "nao-exclusivos": n.get("nao-exclusivo", 0)}
    return [{"chave": k, "rotulo": rot, "n": valores[k], "atual": k == filtro} for k, (rot, _) in FILTROS.items()]


def heroi(t: dict, top: dict, filtro: str) -> dict:
    """T8: a resposta composta do recorte. Frase lida na ordem: antes + pct + meio + fim (sempre uma frase correta)."""
    if filtro == "todos":
        p = t["principal"]
        resto = [g for g in t["grupos"] if g["classe"] != p["classe"]]
        if p["classe"] == "sem-talento":
            meio, fim = ("está", "sem talento"), "informado."
        else:
            meio, fim = ("vai para os", "talentos"), f"{p['nome'].lower()}."
        return {"pct": p["pct"], "antes": "Da demanda do ano,", "meio": meio, "fim": fim,
                "apoio_num": f"{inteiro(p['n'])} de {inteiro(t['total'])}", "apoio_txt": "pedidos do ano",
                "apoio_ex": "; ".join(f"{inteiro(g['n'])} {_curto(g['classe'])}" for g in resto)}
    rot, grupo = FILTROS[filtro]
    nome = rot.lower()
    tg = top.get(grupo)
    if not tg:
        return {"pct": None, "antes": f"Dos pedidos de talentos {nome},", "meio": None, "fim": None,
                "apoio_num": None, "apoio_txt": "a lista dos talentos mais pedidos está sendo atualizada", "apoio_ex": ""}
    k = len(tg["linhas"])
    ex = f"{tg['talentos']} talentos {nome} tiveram pedidos no ano" if tg.get("talentos") else ""
    if grupo == "nao-exclusivo":
        ex = (ex + "; " if ex else "") + "Squad de Talentos (grupo) fica fora da lista e conta no total"
    return {"pct": tg["pct"], "antes": f"Dos pedidos de talentos {nome},",
            # concordância: "1% … vai"; um talento só: "vão para o talento mais pedido."
            "meio": ((("vai" if tg["pct"] == 1 else "vão") + (" para os" if k != 1 else " para o")),
                     f"{k} talentos" if k != 1 else "talento"),
            "fim": "mais pedidos." if k != 1 else "mais pedido.",
            "apoio_num": f"{inteiro(tg['n'])} de {inteiro(tg['total'])}", "apoio_txt": f"pedidos {nome} do ano",
            "apoio_ex": ex}


def _curto(classe: str) -> str:
    return {"exclusivo": "exclusivos", "nao-exclusivo": "não exclusivos", "sem-talento": "sem talento informado"}[classe]


def barra(t: dict, filtro: str) -> list[dict]:
    """T9: os três grupos do ano; com filtro, o grupo do recorte destacado e os demais esmaecidos."""
    alvo = FILTROS[filtro][1]
    return [{**g, "destaque": filtro != "todos" and g["classe"] == alvo,
             "apagado": filtro != "todos" and g["classe"] != alvo} for g in t["grupos"]]


def mapa(tg: dict | None, fim) -> dict | None:
    """T10: grade talento × mês (jan–dez do ano do corte). None sem dados mensais ou se a soma dos meses não fecha."""
    if not tg or not tg.get("mensal") or not tg["linhas"]:
        return None
    fim = pd.Timestamp(fim)
    ultimo_do_mes = (fim + pd.offsets.MonthEnd(0)).day
    colunas = [{"m": m, "rotulo": MESES[m - 1], "extenso": MESES_EXTENSO[m - 1], "futuro": m > fim.month,
                "parcial": m == fim.month and fim.day < ultimo_do_mes} for m in range(1, 13)]
    for r in tg["linhas"]:
        if sum(r["meses"].values()) != r["n"] or any(m > fim.month for m in r["meses"]):
            log.warning("Talentos: meses de %s somam %s, total %s", r["talento"], sum(r["meses"].values()), r["n"])
            return None
    maior = max((v for r in tg["linhas"] for v in r["meses"].values()), default=0)
    linhas = []
    for r in tg["linhas"]:
        celulas = []
        for c in colunas:
            v = None if c["futuro"] else r["meses"].get(c["m"], 0)
            nivel = 0 if not v or not maior else max(1, math.ceil(NIVEIS * v / maior))
            celulas.append({"n": v, "nivel": nivel, "futuro": c["futuro"], "parcial": c["parcial"],
                            "rotulo": c["extenso"]})
        linhas.append({**r, "celulas": celulas})
    totais = [None if c["futuro"] else sum(r["meses"].get(c["m"], 0) for r in tg["linhas"]) for c in colunas]
    # D51 (botão play): quem entra e sai dos 10 ao longo do ano, com os pedidos de jan até o mês do corte. Fica de fora
    # (sem quebrar a tabela) quem não fecha a soma; a corrida então mostra só os 10 do ano
    extras = []
    for r in tg.get("corrida") or []:
        if sum(r["meses"].values()) == r["n"] and not any(m > fim.month for m in r["meses"]):
            extras.append({"t": r["talento"], "pos": r["pos"], "p": [r["meses"].get(m, 0) for m in range(1, fim.month + 1)]})
        else:
            log.warning("Talentos (corrida): meses de %s somam %s, total %s", r["talento"], sum(r["meses"].values()), r["n"])
    return {"colunas": colunas, "linhas": linhas, "maior": maior, "totais_mes": totais, "ate": fim.strftime("%d/%m"),
            "ate_dia": fim.day, "empate": tg.get("empate"), "n": tg["n"], "pct": tg["pct"],
            "nome_ch": largura_nomes(r["talento"] for r in linhas), "extras": extras}


def largura_nomes(nomes) -> int:
    """T11 (26/10/2026, D51): caracteres do maior nome do recorte, entre NOME_MIN e NOME_MAX; vira a classe mapa-nomes-N,
    que dá à coluna dos nomes a largura desse nome + ~10% de folga (estilo.css), sem reticências."""
    return max(NOME_MIN, min(NOME_MAX, max((len(str(n).strip()) for n in nomes), default=NOME_MIN)))
