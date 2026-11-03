"""Entrada de pedidos: cards criados por mês e grupo de input (página inicial da área; D23, D25, D26).

Base: `gld_agenciamento_entrada_diaria` (uma linha por dia × grupo × tipo × família, só onde houve card).

E1  Quantidade do mês = `quantidade` + `quantidade_estimada` (cards com data estimada pela gold contam no dia estimado).
    Todas as famílias entram: é o volume total que chegou ao board.
E2  Grupos na ordem fixa de GRUPOS (cor segue o grupo, nunca a posição); valor desconhecido cai em "Sem tipo".
E3  Mês parcial = mês da carga em São Paulo; cobertura até a véspera. Sem metadado, usa último dia da tabela + 1.
E4  Período do número do ano (o ano já está no título): "até D de mês" no ano em andamento (o dia é o último coberto
    pela carga, E3); "de janeiro a dezembro" no ano fechado, inclusive quando a carga cobre até 31/12 (carga de 01/01);
    "de mês a dezembro" (ou "de mês até D de mês") quando a base começa no meio do ano (2024 começa em outubro).
    O texto sai pronto daqui.
E0  Ano mostrado = ano do último dia coberto pela carga (E3; vira sozinho em janeiro); sem seletor de ano (D26). Se o
    ano novo ainda não tem pedido, mostra o último ano com dados.
E6  Situação por safra (dica do mês e leitor de tela): os cards que entraram no mês divididos pela situação de hoje, nas
    colunas da gold `entregue_no_mes`, `entregue_depois`, `nao_seguiu` e `em_andamento` (somam as entradas). As quatro
    parcelas fecham em 100% pelo maior resto (`_pcts`), no mês e no ano.
E8  Comparação com o ano anterior, só quando a base cobre o ano anterior desde janeiro (2026 em diante; 2025 não, pois a
    base começa em out/2024): no total, o mesmo período (1º/jan até o mesmo dia do ano anterior); em cada mês, o mesmo
    mês do ano anterior (no mês parcial, até o mesmo dia), também por tipo (dica dos novos no extrato). Variação em % = atual ÷ anterior − 1 (`variar`), só quando o
    ano anterior tem ao menos BASE_MINIMA_VARIACAO pedidos; abaixo disso a tela mostra só o número de referência.
    E8c: parcelas de um mesmo todo fecham em 100% pelo maior resto (`_pcts`): tipos de cada mês e do mesmo mês do ano
    anterior, tipos no ano e no mesmo período do ano anterior (E9), situações (E6) e as partes do extrato (E7). Os
    percentuais que não são parcelas de um todo comum (entregues dos novos ÷ novos, dos represados ÷ represados)
    arredondam meio para cima (`_pct`).
    Na tela, o sinal e a frase ("a mais" / "a menos" / "igual") saem do percentual já arredondado (formato.variacao).
E7  Extrato somente nos seis meses mais recentes que têm pedidos, na base inteira até o último dia coberto (inclui o
    mês parcial, atravessa anos; mês vazio, como o 1º dia útil caindo depois de um fim de semana, não ocupa vaga).
    A lista sai em `meses_extrato`; a tela por ora só abre os que estão no ano mostrado (em janeiro, como mostrar os
    do ano anterior é decisão do Caio). Meses anteriores conservam a fotografia de situação. Histórico e total anual
    não são limitados. Cargas de dias diferentes (entrada × fluxo, `data_carga`) escondem o extrato com aviso.
    O extrato é a fila do mês (`gld_agenciamento_fluxo_mensal`): represados no início (entraram antes e não tinham
    saído no 1º dia) + novos pedidos = demanda do mês = entregues + não seguiram + seguem represados (sempre fecha).
    Entregues dos novos ÷ novos; entregues dos represados ÷ represados; demais % sobre a demanda. Os represados de um
    mês são os represados do início do mês seguinte. Dicas: mês de entrada dos represados (início e fim) e das entregas
    de represados. A fila só conta pedidos que entraram no mesmo ano do mês analisado (decisão do Caio, 23/10/2026):
    pedidos de anos anteriores não entram na fila nem aparecem na tela (só no dado, para auditoria).
E9  Composição contra o ano anterior (caixa da legenda), sempre no mesmo período (1º/jan até o último dia da carga,
    E8): para cada tipo, pedidos e parcela no ano, pedidos e parcela no ano anterior e a variação de pedidos
    (pedidos do ano ÷ pedidos do ano anterior − 1), só quando o ano anterior tem ao menos BASE_MINIMA_VARIACAO pedidos
    daquele tipo (base pequena gera percentuais sem sentido, ex.: 77 × 3 = +2.467%); linha de total igual ao número do
    topo e à comparação E8. O teste de
    duas proporções (app/estatistica.py) fica calculado em `contra_anterior`, mas a tela não usa "pontos". Só com régua.
E5  Composição de cada grupo (dica da legenda): os valores de `tipo_de_input` que caíram nele no ano, com a
    quantidade; tipo vazio aparece como "vazio no board".
"""

import pandas as pd

from app import corte, estatistica, formato
from app.dados import (  # data_carga: regra E3, compartilhada com Talentos e Atendimento (TAL-D9)
    data_carga,
    versao_de,
)

GRUPOS = ("Mercado", "Inbound", "Proativo", "Internos", "Sem tipo")  # E2: também a ordem da pilha (de baixo para cima)
CLASSES = {"Mercado": "mercado", "Inbound": "inbound", "Proativo": "proativo", "Internos": "internos", "Sem tipo": "sem-tipo"}
# E5: só estes grupos têm dica com a composição (reúnem vários tipo_de_input: ViU, Interna, Globo, ViU First, OTR).
# Lista fixa, não decidida pelos dados, para o botão não aparecer e sumir conforme o ano (pedido do Caio, 23/10/2026)
GRUPOS_COM_DICA = ("Internos",)
# E6: (classe, rótulo, coluna da gold) — também a ordem da pilha, de baixo para cima
SITUACOES = (("no-mes", "Entregues no mês", "entregue_no_mes"), ("depois", "Entregues depois", "entregue_depois"),
             ("nao-seguiu", "Saíram sem entrega", "nao_seguiu"), ("andamento", "Em andamento", "em_andamento"))
BASE_MINIMA_VARIACAO = 30  # E9
_cache: dict = {}


def _base(df: pd.DataFrame) -> pd.DataFrame:
    chave = versao_de(df)
    if chave not in _cache:
        while len(_cache) >= 3:
            _cache.pop(next(iter(_cache)))
        b = pd.DataFrame({
            "data": pd.to_datetime(df["data"]),
            "grupo": df["grupo_input"].where(df["grupo_input"].isin(GRUPOS), "Sem tipo"),  # E2
            "n": df["quantidade"].fillna(0).astype(int) + df["quantidade_estimada"].fillna(0).astype(int),  # E1
            "estimados": df["quantidade_estimada"].fillna(0).astype(int),
            "tipo": df["tipo_de_input"].fillna("Sem tipo").replace({"Sem tipo": "vazio no board", "": "vazio no board"}),
            **{classe: df[coluna].fillna(0).astype(int) for classe, _, coluna in SITUACOES},  # E6
            "saidas": df["quantidade_saida"].fillna(0).astype(int),  # 1ª entregas no dia (aba Atendimento)
        })
        _cache[chave] = b
    return _cache[chave]


def _pct(parte: int, total: int) -> int:
    """Percentual inteiro arredondado meio para cima (12,5 → 13): a política única do portal (F13, formato.pct_inteiro)."""
    return formato.pct_inteiro(parte, total)


def _pcts(valores: list[int]) -> list[int]:
    """Parcelas que fecham em 100 pelo maior resto (E8c; empate de resto: a ordem de GRUPOS decide). F13: a regra mora
    em formato.parcelas_100 (a mesma conta de antes)."""
    return formato.parcelas_100(valores)


def _situacao(linhas: pd.DataFrame) -> list[dict]:
    """E6: as quatro situações da safra; parcelas fecham em 100 pelo maior resto (E8c)."""
    ns = [int(linhas[classe].sum()) for classe, _, _ in SITUACOES]
    return [{"nome": nome, "classe": classe, "n": n, "pct": p}
            for (classe, nome, _), n, p in zip(SITUACOES, ns, _pcts(ns))]


def variar(atual: int, anterior: int) -> float | None:
    """Variação em % (E8, E9, A7): só quando o ano anterior tem base suficiente (BASE_MINIMA_VARIACAO)."""
    return atual / anterior - 1 if anterior >= BASE_MINIMA_VARIACAO else None


def _comparacao(atual: int, anterior: int) -> dict | None:
    return {"total": anterior, "variacao": variar(atual, anterior)} if anterior else None


def ultimo_dia(df: pd.DataFrame, b: pd.DataFrame) -> pd.Timestamp:
    """E3: último dia coberto pela carga. A carga cobre até ontem, inclusive dias sem entradas: não confundir ausência de
    pedidos no fim do mês com uma carga ainda do mês anterior.

    D68 (03/11/2026): com o recorte do mês fechado, o último dia MOSTRADO (fim 02/11 → 31/10, `corte.data_exibicao`);
    tudo o que a página soma e escreve ("até 31 de outubro", o mesmo período de 2025) segue este dia."""
    carga = data_carga(df)
    fim = pd.Timestamp(carga) - pd.Timedelta(days=1) if carga is not None else b["data"].max()
    return pd.Timestamp(corte.data_exibicao(fim)) if pd.notna(fim) else fim


def meses_extrato(b: pd.DataFrame, ultimo: pd.Timestamp) -> list[str]:
    """E7: os seis meses mais recentes com pedidos ("AAAA-MM"), na base inteira até o último dia coberto. Mês vazio
    não ocupa vaga e a lista atravessa anos."""
    com_pedido = b.loc[(b["n"] > 0) & (b["data"] <= ultimo), "data"].dt.to_period("M").unique()
    return [str(p) for p in sorted(com_pedido)[-6:]]


def regua_anterior(b: pd.DataFrame, ano: int, ultimo: pd.Timestamp) -> tuple[pd.DataFrame, bool, pd.Timestamp]:
    """E8: linhas do ano anterior, se elas servem de régua (base desde janeiro) e o último dia do mesmo período."""
    anterior = b.loc[b["data"].dt.year == ano - 1]
    compara = not anterior.empty and anterior["data"].min() <= pd.Timestamp(ano - 1, 1, 7)
    return anterior, compara, min(ultimo, pd.Timestamp(ano, 12, 31)) - pd.DateOffset(years=1)


def entrada(df: pd.DataFrame, ano: int | None = None) -> dict:
    """Números da página inicial para um ano (padrão: o da carga, E0), com a comparação ao ano anterior (E8)."""
    b = _base(df)
    ultimo = ultimo_dia(df, b)
    extrataveis = meses_extrato(b, ultimo)  # E7
    anos = sorted(b["data"].dt.year.unique().tolist())
    if ano not in anos:  # E0
        ano = ultimo.year if ultimo.year in anos else anos[-1]
    corte_ano = min(ultimo, pd.Timestamp(ano, 12, 31))
    mes_parcial = (corte_ano + pd.Timedelta(days=1)).strftime("%Y-%m")
    # D68: com o recorte do mês fechado, o mês seguinte ao último dia mostrado ainda não começou na tela: futuro, sem
    # coluna de mês parcial (com "off", a regra E3 de antes: o mês da carga é o parcial)
    sem_parcial = corte.mes_fechado_ligado()
    anterior, compara, limite_anterior = regua_anterior(b, ano, ultimo)  # E8
    do_ano = b.loc[(b["data"].dt.year == ano) & (b["data"] <= ultimo)]
    por_mes = do_ano.pivot_table(index=do_ano["data"].dt.month, columns="grupo", values="n", aggfunc="sum", fill_value=0)
    estimados = do_ano.groupby(do_ano["data"].dt.month)["estimados"].sum()
    meses = []
    for m in range(1, 13):
        chave = f"{ano}-{m:02d}"
        valores = {g: int(por_mes.at[m, g]) if (m in por_mes.index and g in por_mes.columns) else 0 for g in GRUPOS}
        total = sum(valores.values())
        meses.append({
            "chave": chave, "rotulo": formato.MESES[m - 1], "extenso": formato.MESES_EXTENSO[m - 1],
            "parcial": chave == mes_parcial and not sem_parcial,
            "futuro": chave > mes_parcial or (sem_parcial and chave == mes_parcial), "total": total,
            "detalhavel": bool(total and chave in extrataveis),  # E7
            "estimados": int(estimados.get(m, 0)),
            "grupos": [{"nome": g, "classe": CLASSES[g], "n": valores[g], "pct": p}
                       for g, p in zip(GRUPOS, _pcts([valores[g] for g in GRUPOS]))],  # E8c: fecham em 100
            "situacao": _situacao(do_ano.loc[do_ano["data"].dt.month == m]),
        })
        meses[-1]["pct_no_mes"] = meses[-1]["situacao"][0]["pct"]
        mes_anterior = anterior.loc[anterior["data"].dt.month == m]
        if chave == mes_parcial:  # mês em andamento: compara só até o mesmo dia
            mes_anterior = mes_anterior.loc[mes_anterior["data"] <= limite_anterior]
        meses[-1]["anterior"] = (_comparacao(total, int(mes_anterior["n"].sum()))
                                 if compara and total and chave <= mes_parcial else None)
        # E8: o mesmo mês do ano anterior por tipo (dica dos novos no extrato); no parcial, até o mesmo dia
        por_tipo_ant = mes_anterior.groupby("grupo")["n"].sum()
        ref = meses[-1]["anterior"]
        pcts_ant = _pcts([int(por_tipo_ant.get(g, 0)) for g in GRUPOS])  # E8c: parcelas do ano anterior fecham em 100
        for g, p_ant in zip(meses[-1]["grupos"], pcts_ant):
            g["n_anterior"] = int(por_tipo_ant.get(g["nome"], 0)) if ref else None
            g["pct_anterior"] = p_ant if ref else None  # parcela do tipo no mês do ano anterior
            g["variacao_mes"] = variar(g["n"], g["n_anterior"]) if ref else None  # E8b: base mínima de 30
        # E3: no mês parcial, o último dia contado nos dois anos ("até 22/10" na dica dos novos)
        meses[-1]["ate"] = (f"{ultimo.day:02d}/{ultimo.month:02d}"
                            if chave == mes_parcial and ultimo.strftime("%Y-%m") == chave else None)
    total_ano = int(do_ano["n"].sum())
    totais = do_ano.groupby("grupo")["n"].sum()
    composicao = do_ano.groupby(["grupo", "tipo"])["n"].sum()  # E5
    escala = max([m["total"] for m in meses] + [1])
    periodo_anterior = anterior.loc[anterior["data"] <= limite_anterior]  # E9: mesmo período do ano anterior
    totais_anteriores, total_anterior = periodo_anterior.groupby("grupo")["n"].sum(), int(periodo_anterior["n"].sum())
    # E8c/E9: parcelas por tipo no ano e no mesmo período do ano anterior fecham em 100 (maior resto)
    pcts_ano = dict(zip(GRUPOS, _pcts([int(totais.get(g, 0)) for g in GRUPOS])))
    pcts_ant = dict(zip(GRUPOS, _pcts([int(totais_anteriores.get(g, 0)) for g in GRUPOS])))
    grupos = [{"nome": g, "classe": CLASSES[g], "n": int(totais.get(g, 0)), "pct": pcts_ano[g],
               "pct_anterior": pcts_ant[g] if compara else None,
               "agrupa": g in GRUPOS_COM_DICA,  # E5: dica com a composição só nestes grupos
               "tipos": [{"nome": t, "n": int(n)} for t, n in composicao.get(g, pd.Series(dtype=int)).sort_values(ascending=False).items() if n],
               "contra_anterior": (estatistica.diferenca(int(totais.get(g, 0)), total_ano, int(totais_anteriores.get(g, 0)), total_anterior)
                                   if compara else None),
               "n_anterior": int(totais_anteriores.get(g, 0)) if compara else None,
               "variacao": variar(int(totais.get(g, 0)), int(totais_anteriores.get(g, 0))) if compara else None}
              for g in GRUPOS]
    inicio = b["data"].min()
    desde = f"de {formato.MESES_EXTENSO[inicio.month - 1]} " if inicio.year == ano and inicio.month > 1 else ""
    if ultimo.year == ano and not (ultimo.month == 12 and ultimo.day == 31):  # E4: o dia final acompanha a carga
        periodo = f"{desde}até {ultimo.day} de {formato.MESES_EXTENSO[ultimo.month - 1]}"
        ate_curto = f"{ultimo.day}/{formato.MESES[ultimo.month - 1]}"  # sob as barras: "mesmo período: até 22/out"
    else:
        periodo = f"{desde or 'de janeiro '}a dezembro"
        ate_curto = None  # ano fechado: as barras comparam os anos inteiros
    return {
        "comparacao": (_comparacao(total_ano, int(anterior.loc[anterior["data"] <= limite_anterior, "n"].sum()))
                       if compara else None),
        "ano_anterior": ano - 1,
        "situacao": _situacao(do_ano),
        "meses_extrato": extrataveis,  # E7: pode incluir meses do ano anterior (B6; a tela decide o que abre)
        "ano": ano,
        "periodo": periodo,
        "ate_curto": ate_curto,
        "anos": anos,
        "total": total_ano,
        "grupos": grupos,
        "meses": meses,
        "escala": escala,
        "base_minima": BASE_MINIMA_VARIACAO,  # E8b/E9: nota do "–" nas dicas
    }


def _nome_mes(p: pd.Period) -> str:
    return formato.MESES_EXTENSO[p.month - 1]


def _por_mes(linhas: pd.DataFrame) -> list[dict]:
    """Quantidade por mês de entrada, do mais recente para o mais antigo (dicas dos represados)."""
    soma = linhas.groupby("entrada")["n"].sum().sort_index(ascending=False)
    return [{"mes": str(m), "nome": f"{_nome_mes(m).capitalize()} de {m.year}", "n": int(n)} for m, n in soma.items() if n]


def extrato(fila: pd.DataFrame, mes: str) -> dict | None:
    """E7: o mês ("AAAA-MM") como um extrato de fila: represados no início + novos pedidos = demanda do mês; dela saem
    os entregues (dos novos e dos represados) e os que não seguiram; o resto segue represado.

    Base (D57, 27/10/2026): view gold `gld_agenciamento_fila_mensal`, uma linha por mês × safra (mês de entrada) com
    novos, represados, entregues, não seguiram e seguem (regras FM1/FM2 da gold: a fila só conta pedidos do próprio ano;
    "não seguiu" sem data conta no mês de entrada e não fica represado). Aqui só se soma e se arredonda."""
    p = pd.Period(mes, "M")
    linhas = fila.loc[pd.to_datetime(fila["mes"]).dt.to_period("M") == p]
    f = pd.DataFrame({"entrada": pd.to_datetime(linhas["mes_entrada"]).dt.to_period("M"),
                      "do_ano": linhas["do_ano"].astype(bool)}
                     | {c: linhas[c].fillna(0).astype(int) for c in ("novos", "represados", "entregues", "nao_seguiram",
                                                                    "seguem")})
    ano = f.loc[f["do_ano"]]  # a fila só conta pedidos do próprio ano (decisão do Caio, 23/10)
    entraram = int(ano.loc[ano["entrada"] == p, "novos"].sum())
    if not entraram:
        return None
    represados = int(ano["represados"].sum())
    demanda = represados + entraram
    ent_novos = int(ano.loc[ano["entrada"] == p, "entregues"].sum())
    ent_repr = int(ano.loc[ano["entrada"] < p, "entregues"].sum())
    # entregas do mês de pedidos de anos anteriores: fora da fila e da tela; guardadas só para auditoria (A1 as inclui)
    anos_antes = int(f.loc[~f["do_ano"], "entregues"].sum())
    entregues = ent_novos + ent_repr
    nao_seguiram = int(ano["nao_seguiram"].sum())
    seguem = int(ano["seguem"].sum())
    # E8c: as partes da demanda (represados + novos) e das saídas (entregues + não seguiram + seguem) fecham em 100
    # pelo maior resto, sem jogar o arredondamento todo na última parcela
    pct_repr, pct_novos = _pcts([represados, entraram])
    pct_ent, pct_ns, pct_seguem = _pcts([entregues, nao_seguiram, seguem])
    # por mês de entrada (dicas): quanto estava na fila no início (no próprio mês: os novos), quanto foi entregue e quanto
    # não seguiu no mês, e quanto segue represado. Cada linha fecha: início = entregues + não seguiram + seguem
    por_safra = ano.assign(inicio=ano["novos"] + ano["represados"]).sort_values("entrada", ascending=False)
    meses_fila = [{"mes": str(r.entrada), "nome": _nome_mes(r.entrada).capitalize(), "novo": r.entrada == p,
                   "inicio": int(r.inicio), "entregues": int(r.entregues), "nao_seguiram": int(r.nao_seguiram),
                   "seguem": int(r.seguem)}
                  for r in por_safra.itertuples() if r.inicio]  # só o mês: a fila é do ano
    entregues_antes = f.loc[f["entrada"] < p, ["entrada", "do_ano", "entregues"]].rename(columns={"entregues": "n"})
    return {
        "mes": mes, "nome": f"{_nome_mes(p).capitalize()} de {p.year}", "entraram": entraram,
        "fila": {
            "represados": represados, "novos": entraram, "demanda": demanda,
            # % da composição da demanda e das saídas: parcelas pelo maior resto (E8c), somam 100
            "pct_represados": pct_repr, "pct_novos": pct_novos,
            "entregues": entregues, "pct_entregues": pct_ent,
            "entregues_novos": ent_novos, "pct_entregues_novos": _pct(ent_novos, entraram),
            "entregues_represados": ent_repr, "pct_entregues_represados": _pct(ent_repr, represados),
            "nao_seguiram": nao_seguiram, "pct_nao_seguiram": pct_ns,
            "seguem": seguem, "pct_seguem": pct_seguem,
            "represados_meses": [m for m in meses_fila if not m["novo"]], "seguem_meses": meses_fila,  # mesma tabela de cima + a linha do próprio mês (novos)
            "entregues_represados_meses": [{**m, "nome": m["nome"].split(" de ")[0]}
                                           for m in _por_mes(entregues_antes.loc[entregues_antes["do_ano"]])],
            "entregues_anos_anteriores": anos_antes,
        },
        "entregas": {"total": entregues + anos_antes,
                     "anteriores": _por_mes(entregues_antes)},
    }
