"""Atendimento: quanto da demanda a equipe atende, em quantidade e em proporção (D27; PRD seção 9.2).

Base: `gld_agenciamento_entrada_diaria`, a mesma da página inicial; saídas sem entrega por mês (A11) da
`gld_agenciamento_fluxo_mensal`; o mês a mês do quadro (A13: respondidos, fila que veio e que ficou) da view
`gld_agenciamento_atendimento_mensal`; a composição por status (A26) da `gld_agenciamento_2026_saidas_status` (D57,
27/10/2026: tudo na gold, nada refeito sobre a silver). Mudou uma regra? Altere aqui e registre no PRD. O template só
mostra.

A1  Entregas do mês = Σ `quantidade_saida` com data no mês: 1ª entrega ao cliente (regra B da gold). Reenvios e revisões
    não contam.
A2  Entregas do próprio mês = Σ `entregue_no_mes` dos pedidos que entraram no mês; de meses anteriores = A1 − A2
    (nunca negativo). As duas somam A1.
A3  Entradas do mês = Σ `quantidade` + `quantidade_estimada` (a mesma E1 da página inicial).
A4  Cobertura = A1 ÷ A3: quanto a equipe entregou em relação ao que chegou no mês. Pode passar de 100% (a equipe
    entregou mais do que chegou: a fila diminuiu). É uma razão, não uma proporção: a diferença entre anos é mostrada em
    pontos, sem teste estatístico.
A5  Entregue no próprio mês = A2 ÷ A3: parcela dos pedidos do mês que já saiu dentro do mesmo mês. É uma proporção.
A6  Ano: quantidades (A1, A2, A3) do 1º de janeiro até o último dia da carga, comparadas ao mesmo período do ano
    anterior. Taxas do ano (A4, A5) só com meses completos (janeiro até o mês anterior ao parcial), nos dois anos: a
    safra do mês parcial ainda não teve o mês inteiro para ser entregue.
A7  Mês: comparação com o mesmo mês do ano anterior. No mês parcial, quantidades até o mesmo dia e taxas não comparadas.
    Variação de quantidade em % só com base mínima no ano anterior (a mesma regra do Início, `entrada.variar`).
A8  Diferença de proporção "relevante" = teste z de duas proporções a 95% (app/estatistica.py). Vale para A5; não para A4.
    Régua do ano anterior só quando a base o cobre desde janeiro (E8): 2026 compara com 2025; 2025 não compara.
A9  Entregas do mês por tipo de input = Σ `quantidade_saida` por `grupo_input`, com o mesmo agrupamento do Início (E2:
    Mercado, Inbound, Proativo, Internos, Sem tipo). Os grupos somam A1. Gráfico (24/10/2026): coluna cheia = entregas do
    mês por tipo; contorno tracejado atrás = entradas do mês (A3), na mesma escala.
A10 Tabela-legenda (como a do Início, E8–E9): entregas do ano por tipo (A9 somado de 1º/jan até o último dia da carga),
    parcela do total pelo maior resto (E8c), e o mesmo período do ano anterior (1º/jan até o mesmo dia, E8) com parcela
    e variação de quantidade (só com base mínima no ano anterior, `entrada.variar`). Total = A1 do ano.
A11 Saíram sem entrega no mês = Σ `quantidade` de `gld_agenciamento_fluxo_mensal` com evento `nao_seguiu` (declinado,
    standby ou encerrado sem ir ao cliente) e `mes_evento` no mês. Também é uma resposta ao pedido: no gráfico fica no
    topo da coluna, em cor própria, e a coluna passa a mostrar os pedidos respondidos (A1 + A11). Só existe para o ano
    corrente (o board de 2025 não guardou o histórico de status): sem comparação com o ano anterior.
A12 Gráfico por MÊS DE ENTRADA (24/10/2026, decisão do Caio): para os pedidos que entraram em cada mês, o que aconteceu
    com eles até hoje — entregues no próprio mês, entregues depois, saíram sem entrega e ainda sem resposta (em
    andamento) — as mesmas quatro situações do Início (E6, gold de entradas), que somam as entradas do mês (A3). Responde
    "a equipe está dando conta?": o que ficou para depois e o que segue sem resposta aparece direto na coluna. A
    tabela-legenda soma as situações no ano (1º/jan até o último dia da carga), parcelas pelo maior resto (E8c).
A13 Fluxo do mês (slide 1, gráfico de halteres): entraram = A3; respondidos = eventos `entregue` + `nao_seguiu` do
    fluxo mensal com `mes_evento` no mês, só de pedidos que entraram no ano (a fila é do ano); saldo = respondidos −
    entraram (negativo = a fila cresceu); fila no fim do mês = Σ entraram − Σ respondidos, acumulados desde janeiro.
    Saídas `nao_seguiu` sem mês de evento são atribuídas ao mês de entrada (mesma convenção E7 do Início), com
    quantidade informada na tela. A fila é uma reconstrução, não um fechamento histórico observado. Na carga de
    23/10/2026, 5.520 entradas − 5.360 saídas = 160 em andamento; 10 saídas têm mês atribuído.
A15b (D53, 26/10/2026) Faixa do ano: para a diretoria, RESOLVIDO = ENTREGUE AO CLIENTE. Recebidos → entregues ao cliente
    → saíram sem entrega → em andamento, cada parte em % dos recebidos, inteiros pelo maior resto (E8c, `entrada._pcts`,
    a mesma regra do Início): as três somam 100%. Substitui "Resolvidos 96%" (entregues + sem entrega, arredondado
    para baixo com divisão inteira), que não batia com a régua nem com o % do mês.
A25b (D53) % do mês = entregues ao cliente ÷ para atender (o que veio do mês anterior + o que entrou), meio para cima
    (C8). Base diferente da faixa do ano: lá o divisor são os recebidos no ano (cada pedido conta uma vez); aqui é o que
    havia para atender no mês, que inclui o que veio do mês anterior (o mesmo pedido pode estar em dois meses). Substituída
    na tela pela A27 (mesma conta, sem as decisões externas no divisor); `pct_saiu` (a antiga A25) fica só no cálculo.
A26 (D53) Composição por status do board das saídas sem entrega (dica do quadro): gold
    `gld_agenciamento_2026_saidas_status` (regras da gold de fluxo); um mês só mostra a composição quando o total bate
    com a célula.
A27 (D53, decisão do Caio, 26/10/2026) CAPACIDADE: "a equipe deu conta de tudo o que dependia dela no mês?". Taxa do mês
    = entregues ao cliente ÷ (para atender − saídas EXTERNAS do mês), saídas externas = status "Declinado pelo Mercado",
    "Declinado pelo talento" e "Encerrado" (decisões de fora da equipe). "Declinado Internamente" e "Standby" FICAM na
    base: podem ser falta de capacidade. Meio para cima (C8). É o % da linha única do quadro, dos pontos da dispersão
    (x = demanda que dependia da equipe) e do selo dos entregues no topo (ano: entregues ÷ (recebidos − externas do
    ano)). Sem a composição por status de um mês (A26 não confere), as externas do mês contam 0 e a dica avisa.
A29 (D58, 27/10/2026; substituída pela A30 no mesmo dia, histórico) Taxa do mês = entregues ao cliente ÷ (para atender −
    DECLINADOS do mês), declinados = todas as saídas sem entrega (A13: declinado internamente ou pelo mercado/talento,
    standby, encerrado). Como para atender = entregues + declinados + ficou, a taxa é entregues ÷ (entregues + ficou):
    quanto da demanda que seguiu viva a equipe entregou. Meio para cima (C8). É o % da linha do quadro, dos pontos da
    dispersão (x = demanda que dependia da equipe) e do selo dos entregues no topo (ano: entregues ÷ (recebidos −
    declinados do ano)). As saídas externas (A27) ficam calculadas, fora da tela.
A30 (D58b, decisão do Caio, 27/10/2026; substitui a A29 no mesmo dia) Taxa do mês = ENTREGUES NO MÊS (entregues ao
    cliente + declinados) ÷ PARA ATENDER (veio do mês anterior + entrou), meio para cima (C8). Ex.: set/2026 = 661 ÷ 834
    = 79%. É o % da linha do quadro, dos pontos da dispersão (x = para atender, y = entregues no mês) e do selo do topo
    (ano: (entregues + declinados) ÷ recebidos). Equivale à antiga `pct_saiu` (A25).
A28 (D53) "Deixamos coisas para trás?": no Saldo, a variação do que ficou para o mês seguinte contra o mês anterior
    (▲ cresceu, ▼ caiu; igual, nada).
"""


import pandas as pd

from app import corte, estatistica, formato
from app.apresentacoes.gestao_orcamentos.entrada import calculos as entrada


def _taxa(parte: int, total: int) -> float | None:
    return parte / total if total else None


def _numeros(linhas: pd.DataFrame) -> dict:
    """A1–A5 para um conjunto de linhas da diária."""
    entregas, proprio, entradas = int(linhas["saidas"].sum()), int(linhas["no-mes"].sum()), int(linhas["n"].sum())
    return {"entregas": entregas, "proprio": proprio, "anteriores": max(0, entregas - proprio), "entradas": entradas,
            "cobertura": _taxa(entregas, entradas), "no_mes": _taxa(proprio, entradas)}


def _contra(atual: dict, anterior: dict) -> dict:
    """Comparações com o período anterior: quantidade (variação), A4 em pontos, A5 em pontos com o teste (A8)."""
    return {
        "entregas": anterior["entregas"],
        "variacao": entrada.variar(atual["entregas"], anterior["entregas"]),
        "cobertura": anterior["cobertura"],
        "cobertura_pontos": (estatistica.pontos_tela(atual["cobertura"], anterior["cobertura"])  # pontos como escritos
                             if atual["cobertura"] is not None and anterior["cobertura"] is not None else None),
        "no_mes": estatistica.diferenca(atual["proprio"], atual["entradas"], anterior["proprio"], anterior["entradas"]),
    }


def atendimento(df: pd.DataFrame, fluxo: pd.DataFrame | None = None, mensal: pd.DataFrame | None = None) -> dict:
    """`df` = gold de entradas; `fluxo` = gold de fluxo (A11); `mensal` = view do Atendimento mês a mês (A13). Sem `fluxo`
    ou sem `mensal`, a parte correspondente fica zerada (bases de teste)."""
    b = entrada._base(df)
    ultimo = entrada.ultimo_dia(df, b)
    mes_parcial = (ultimo + pd.Timedelta(days=1)).strftime("%Y-%m")
    anos = sorted(b["data"].dt.year.unique().tolist())
    ano = ultimo.year if ultimo.year in anos else anos[-1]  # E0
    # Quando o ano da carga ainda não tem pedidos, o ano mostrado está completo.
    corte_ano = min(ultimo, pd.Timestamp(ano, 12, 31))
    mes_parcial = (corte_ano + pd.Timedelta(days=1)).strftime("%Y-%m")
    # D68 (03/11/2026): com o recorte do mês fechado (`ultimo` = 31/10), o mês da carga ainda não começou na tela: futuro,
    # sem mês parcial; eventos (respondidos, saídas) só até o mês do último dia mostrado. Com "off", a regra de antes
    sem_parcial = corte.mes_fechado_ligado()
    ate_mes = corte_ano.strftime("%Y-%m") if sem_parcial else mes_parcial
    do_ano = b.loc[(b["data"].dt.year == ano) & (b["data"] <= ultimo)]
    anterior, compara, limite_anterior = entrada.regua_anterior(b, ano, ultimo)  # E8
    completos = f"{ano}-01" < mes_parcial  # há ao menos um mês completo no ano?
    # A11: saídas sem entrega por mês do evento (fluxo mensal), até o último dia da carga
    encerrados = {}
    if fluxo is not None and not fluxo.empty:
        f = fluxo.loc[fluxo["evento"] == "nao_seguiu"]
        meses_ev = pd.to_datetime(f["mes_evento"]).dt.strftime("%Y-%m")
        encerrados = f.groupby(meses_ev)["quantidade"].sum().astype(int).to_dict()
        encerrados = {k: v for k, v in encerrados.items() if k.startswith(str(ano)) and k <= ate_mes}
    meses = []
    for m in range(1, 13):
        chave = f"{ano}-{m:02d}"
        atual = _numeros(do_ano.loc[do_ano["data"].dt.month == m])
        mes = {"chave": chave, "rotulo": formato.MESES[m - 1], "extenso": formato.MESES_EXTENSO[m - 1],
               "parcial": chave == mes_parcial and not sem_parcial,
               "futuro": chave > mes_parcial or (sem_parcial and chave == mes_parcial), **atual, "anterior": None}
        mes["encerrados"] = encerrados.get(chave, 0)  # A11
        mes["respondidos"] = mes["entregas"] + mes["encerrados"]
        por_tipo = do_ano.loc[do_ano["data"].dt.month == m].groupby("grupo")["saidas"].sum()  # A9
        mes["grupos"] = [{"nome": g, "classe": entrada.CLASSES[g], "n": int(por_tipo.get(g, 0))} for g in entrada.GRUPOS]
        mes["situacao"] = entrada._situacao(do_ano.loc[do_ano["data"].dt.month == m])  # A12
        if compara and not mes["futuro"] and atual["entradas"]:
            linhas = anterior.loc[anterior["data"].dt.month == m]
            if mes["parcial"]:  # A7: até o mesmo dia; taxas do parcial não são comparadas
                linhas = linhas.loc[linhas["data"] <= limite_anterior]
            contra = _contra(atual, _numeros(linhas))
            if mes["parcial"]:
                contra.update(cobertura=None, cobertura_pontos=None, no_mes=None)
            mes["anterior"] = contra
        meses.append(mes)
    # A10: tabela-legenda por tipo, no ano e no mesmo período do ano anterior
    no_periodo_ant = anterior.loc[anterior["data"] <= limite_anterior] if compara else anterior.iloc[0:0]
    ns = [int(do_ano.loc[do_ano["grupo"] == g, "saidas"].sum()) for g in entrada.GRUPOS]
    ns_ant = [int(no_periodo_ant.loc[no_periodo_ant["grupo"] == g, "saidas"].sum()) for g in entrada.GRUPOS]
    grupos = [{"nome": g, "classe": entrada.CLASSES[g], "n": n, "pct": pct,
               "n_anterior": na if compara else None, "pct_anterior": pa if compara else None,
               "variacao": entrada.variar(n, na) if compara else None,
               # E5 (como no Início): dica com a composição só nos grupos que reúnem vários tipos (hoje, Internos)
               "agrupa": g in entrada.GRUPOS_COM_DICA,
               "tipos": [{"nome": t, "n": int(v)} for t, v in do_ano.loc[do_ano["grupo"] == g].groupby("tipo")["saidas"]
                         .sum().sort_values(ascending=False).items() if v]}
              for g, n, pct, na, pa in zip(entrada.GRUPOS, ns, entrada._pcts(ns), ns_ant, entrada._pcts(ns_ant))]
    # A13: respondidos por mês do evento (só pedidos do ano) e fila acumulada — prontos na view mensal (AM1: a fila
    # recomeça em janeiro; AM2: saída sem entrega sem data = mês de entrada, a convenção E7 do Início, explícita na tela
    # e que não equivale a um fechamento histórico observado)
    respondidos_ano, entregues_ano, fila_mes, sem_data_n = {}, {}, {}, 0
    if mensal is not None and not mensal.empty:
        m_ = mensal.assign(chave=pd.to_datetime(mensal["mes"]).dt.strftime("%Y-%m"))
        m_ = m_.loc[m_["chave"].str.startswith(str(ano)) & (m_["chave"] <= ate_mes)]
        respondidos_ano = dict(zip(m_["chave"], m_["respondidos"].astype(int)))
        entregues_ano = dict(zip(m_["chave"], m_["entregues"].astype(int)))
        fila_mes = dict(zip(m_["chave"], m_["ficou"].astype(int)))
        sem_data_n = int(m_["sem_entrega_sem_data"].sum())
    fila = 0
    for mes in meses:
        if mes["futuro"]:
            mes.update(resp_ano=None, saldo=None, fila=None, entregues_ano=None, sem_entrega_ano=None)
            continue
        mes["resp_ano"] = int(respondidos_ano.get(mes["chave"], 0))
        mes["entregues_ano"] = int(entregues_ano.get(mes["chave"], 0))  # A13: parte entregue dos respondidos
        mes["sem_entrega_ano"] = mes["resp_ano"] - mes["entregues_ano"]
        mes["saldo"] = mes["resp_ano"] - mes["entradas"]
        fila = fila_mes.get(mes["chave"], fila + mes["entradas"] - mes["resp_ano"])  # "ficou" da view
        mes["fila"] = fila
    fechados = do_ano.loc[do_ano["data"].dt.strftime("%Y-%m") < mes_parcial]  # A6: taxas só com meses completos
    taxas = _numeros(fechados)
    resultado = {
        "ano": ano, "ano_anterior": ano - 1, "ultimo": ultimo,
        "saidas_sem_data": sem_data_n,
        "periodo": f"até {corte_ano.day} de {formato.MESES_EXTENSO[corte_ano.month - 1]}",
        "total": _numeros(do_ano),
        "taxas": taxas if completos else None,
        "meses_completos": ("jan a dez" if mes_parcial[:4] > str(ano) else
                            f"{formato.MESES[0]} a {formato.MESES[int(mes_parcial[5:]) - 2]}"
                            if completos and int(mes_parcial[5:]) > 2 else formato.MESES[0]),
        "meses": meses,
        "escala": max([m["entradas"] for m in meses] + [1]),  # A12: a coluna é a entrada do mês
        "escala_fluxo": max([max(m["entradas"], m["resp_ano"] or 0) for m in meses] + [1]),  # A13
        "fila_atual": next((m["fila"] for m in reversed(meses) if m["fila"] is not None), 0),
        "resp_total": sum(m["resp_ano"] or 0 for m in meses),
        "escala_fila": max([m["fila"] or 0 for m in meses] + [1]),
        "fila_inicio": next((m["fila"] for m in meses if m["fila"] is not None), 0),
        "encerrados": sum(encerrados.values()),
        "situacao": entrada._situacao(do_ano),  # A12: situações dos pedidos que entraram no ano
        "contra_anterior": None, "taxas_contra_anterior": None,
        "grupos": grupos, "compara": compara,
        "total_anterior": sum(ns_ant) if compara else None,
        "variacao_total": entrada.variar(sum(ns), sum(ns_ant)) if compara else None,
    }
    if compara:
        resultado["contra_anterior"] = _contra(resultado["total"], _numeros(anterior.loc[anterior["data"] <= limite_anterior]))
        if completos:
            mes_anterior_parcial = str(pd.Period(mes_parcial, 'M') - 12)
            resultado["taxas_contra_anterior"] = _contra(
                taxas, _numeros(anterior.loc[anterior["data"].dt.strftime("%Y-%m") < mes_anterior_parcial]))
    resultado['leitura'] = leitura_executiva(meses, resultado['total']['entradas'])
    return resultado


def _pcts_decimos(valores: list[int]) -> list[float]:
    """Parcelas com 1 casa decimal que somam exatamente 100,0% pelo maior resto (E8c em décimos)."""
    total = sum(valores)
    if not total:
        return [0.0] * len(valores)
    base = [v * 1000 // total for v in valores]
    ordem = sorted(range(len(valores)), key=lambda i: -(valores[i] * 1000 % total))
    for i in ordem[:1000 - sum(base)]:
        base[i] += 1
    return [b / 10 for b in base]


def leitura_executiva(meses: list[dict], total: int) -> dict:
    """A14: estatística descritiva da safra anual; parcial separado dos últimos três meses fechados."""
    observados = [m for m in meses if not m['futuro']]
    com_movimento = [m for m in observados if not m['parcial'] or m['entradas'] or (m['resp_ano'] or 0)]
    atual = (com_movimento or observados)[-1] if observados else None
    fechados = [m for m in observados if not m['parcial']][-3:]
    entregues = sum(m['entregues_ano'] or 0 for m in observados)
    sem_entrega = sum(m['sem_entrega_ano'] or 0 for m in observados)
    fila = observados[-1]['fila'] if observados else 0
    saldo = sum(m['saldo'] for m in fechados)
    pct_entregues, pct_sem_entrega, pct_fila = _pcts_decimos([entregues, sem_entrega, fila]) if total else (None, None, None)
    return {'atual': atual, 'meses': observados, 'entregues': entregues, 'sem_entrega': sem_entrega,
            'fila': fila, 'pct_entregues': pct_entregues,
            'pct_sem_entrega': pct_sem_entrega,
            'pct_fila': pct_fila,
            'fila_anterior': (atual['fila'] + atual['saldo']) if atual else 0,
            'fechados': fechados, 'saldo_fechados': saldo,
            'entradas_fechados': sum(m['entradas'] for m in fechados),
            'saidas_fechados': sum(m['resp_ano'] for m in fechados),
            'meses_fila_cresceu': sum(m['saldo'] < 0 for m in fechados)}


# ---------- A15: fluxo do mês em faixas (opção A, decisão do Caio, 24/10/2026) ----------
# Mês mostrado = o mais recente com movimento (o corrente, marcado como parcial). Entrada: represados do início do
# mês (fila do mês anterior; janeiro = 0, D29) + novos do mês = para atender. Saída: entregues ao cliente + saíram sem
# entrega (resolvidos) + seguem em andamento (fila do fim do mês). As duas pontas somam o mesmo total (conferido).
# A geometria do diagrama (SVG, coordenadas como atributos — a CSP proíbe style="") é calculada aqui.
FLUXO_W, FLUXO_H, FLUXO_NO, FLUXO_VAO = 1000, 300, 16, 14
FLUXO_X = (250, 492, 734)  # colunas: entrada, "para atender", saída (x da esquerda de cada nó)


def _faixa(x0, y0a, y0b, x1, y1a, y1b) -> str:
    """Faixa curva entre dois trechos verticais (Bézier cúbica), como path SVG."""
    m = (x0 + x1) / 2
    return (f"M{x0:.1f},{y0a:.1f} C{m:.1f},{y0a:.1f} {m:.1f},{y1a:.1f} {x1:.1f},{y1a:.1f} "
            f"L{x1:.1f},{y1b:.1f} C{m:.1f},{y1b:.1f} {m:.1f},{y0b:.1f} {x0:.1f},{y0b:.1f} Z")


def _empilhar(valores: list[int], k: float, vao: float, altura: float) -> list[tuple[float, float]]:
    """(topo, base) de cada nó empilhado com vão, centralizado na altura."""
    usados = [v for v in valores]
    total = sum(v * k for v in usados) + vao * (len([v for v in usados if v]) - 1)
    y = (altura - total) / 2
    saida = []
    for v in usados:
        h = v * k
        saida.append((y, y + h))
        if v:
            y += h + vao
    return saida


STATUS_EXTERNOS = ("Declinado pelo Mercado", "Declinado pelo talento", "Encerrado")  # A27: decisões de fora da equipe


def externas_por_mes(status: dict | None) -> dict:
    """A27: saídas externas por mês (chave AAAA-MM); mês sem composição conferida (A26) fica de fora (vale 0)."""
    if not status:
        return {}
    return {k: v["externos"] for k, v in status["meses"].items() if v["confere"]}


def fluxo_mes(resultado: dict, status: dict | None = None) -> dict | None:
    meses = [m for m in resultado["meses"] if m.get("fila") is not None]
    if not meses:
        return None
    i = len(meses) - 1
    m = meses[i]
    represados = meses[i - 1]["fila"] if i > 0 else 0
    novos, entregues, sem_entrega, seguem = m["entradas"], m["entregues_ano"], m["sem_entrega_ano"], m["fila"]
    total = represados + novos
    if not total or entregues + sem_entrega + seguem != total:
        return None
    k = (FLUXO_H - 2 * FLUXO_VAO) / total
    xe, xm, xs = FLUXO_X
    ent = _empilhar([represados, novos], k, FLUXO_VAO, FLUXO_H)
    meio = _empilhar([total], k, 0, FLUXO_H)[0]
    sai = _empilhar([entregues, sem_entrega, seguem], k, FLUXO_VAO, FLUXO_H)
    nos_e = [{"chave": "represados", "rotulo": "Represados do mês anterior", "n": represados, "y": a, "h": b - a}
             for (a, b) in ent[:1]] + [{"chave": "novos", "rotulo": "Novos no mês", "n": novos, "y": a, "h": b - a}
                                       for (a, b) in ent[1:]]
    nos_s = [{"chave": ch, "rotulo": rot, "n": n, "y": a, "h": b - a}
             for ch, rot, n, (a, b) in zip(("entregue", "sem-entrega", "andamento"),
                                           ("Entregues ao cliente", "Saíram sem entrega", "Seguem em andamento"),
                                           (entregues, sem_entrega, seguem), sai)]
    faixas, y = [], meio[0]
    for no in nos_e:  # entrada → meio, empilhando no nó do meio
        if no["n"]:
            faixas.append({"classe": no["chave"], "d": _faixa(xe + FLUXO_NO, no["y"], no["y"] + no["h"], xm, y, y + no["h"])})
        y += no["h"]
    y = meio[0]
    for no in nos_s:  # meio → saída
        if no["n"]:
            faixas.append({"classe": no["chave"], "d": _faixa(xm + FLUXO_NO, y, y + no["h"], xs, no["y"], no["y"] + no["h"])})
        y += no["h"]
    resolvidos = entregues + sem_entrega
    return {
        "mes": m["extenso"], "rotulo": m["rotulo"], "parcial": m["parcial"], "ano": resultado["ano"],
        "represados": represados, "novos": novos, "total": total, "resolvidos": resolvidos,
        "entregues": entregues, "sem_entrega": sem_entrega, "seguem": seguem,
        "nos_e": nos_e, "nos_s": nos_s, "meio": {"y": meio[0], "h": meio[1] - meio[0]}, "faixas": faixas,
        "x": {"e": xe, "m": xm, "s": xs, "no": FLUXO_NO}, "w": FLUXO_W, "h": FLUXO_H,
        # ano como referência (janeiro começa sem represados, D29)
        "ano_recebidos": resultado["total"]["entradas"], "ano_resolvidos": resultado["resp_total"],
        "ano_seguem": resultado["fila_atual"],
        "entregues_ano_total": sum(x["entregues_ano"] or 0 for x in resultado["meses"]),
        "sem_entrega_ano_total": sum(x["sem_entrega_ano"] or 0 for x in resultado["meses"]),
    } | _faixa_ano(resultado, status)


def _faixa_ano(resultado: dict, status: dict | None = None) -> dict:
    """A15b (D53): % de cada parte sobre os recebidos do ano, inteiros pelo maior resto (E8c): somam 100%. A30 (D58b):
    selo = (entregues + declinados do ano) ÷ recebidos no ano."""
    ent = sum(x["entregues_ano"] or 0 for x in resultado["meses"])
    sem = sum(x["sem_entrega_ano"] or 0 for x in resultado["meses"])
    seguem = resultado["fila_atual"]
    p_ent, p_sem, p_and = entrada._pcts([ent, sem, seguem])
    ext = sum(externas_por_mes(status).values())  # A27: fica calculada, fora da tela
    dependia = resultado["total"]["entradas"]  # A30 (D58b): base = recebidos no ano
    return {"pct_entregues": p_ent, "pct_sem_entrega": p_sem, "pct_andamento": p_and,
            "externos_ano": ext, "dependia_ano": dependia, "pct_dependia": pct_meio(ent + sem, dependia),
            "status_completo": bool(status and status.get("ano"))}


# ---------- A16: análise do ritmo (Atendimento, 24/10/2026) ----------
# Dois gráficos que respondem "a equipe está dando conta?" com base estatística, em SVG calculado aqui (CSP):
# 1) Fluxo acumulado: recebidos e resolvidos somados mês a mês desde janeiro; a distância entre as linhas é o que segue
#    em andamento. Linhas juntas = a equipe acompanha o ritmo.
# 2) Dispersão mês a mês: x = recebidos no mês, y = resolvidos no mês (entregues + saídas sem entrega, só pedidos do
#    ano). A diagonal é o equilíbrio (resolveu o que entrou): acima, a fila diminuiu; abaixo, cresceu.
#    Correlação de Pearson e inclinação (mínimos quadrados) só com meses completos; o mês parcial aparece vazado.
def pct_meio(parte: int, todo: int) -> int:
    """% inteiro arredondado meio para cima (C8: floor(x + 0,5)); 0 sem base. 153 ÷ 200 = 76,5 → 77."""
    return formato.pct_inteiro(parte, todo)  # F13: a política única do portal (a mesma regra, sem o ruído do float)


def _arredondar_acima(v: float, passo: int) -> int:
    return int(-(-v // passo) * passo)


def analise_ritmo(resultado: dict, status: dict | None = None) -> dict | None:
    meses = [m for m in resultado["meses"] if m.get("fila") is not None]
    if len(meses) < 3:
        return None
    rec = [m["entradas"] for m in meses]
    res = [m["resp_ano"] for m in meses]
    acum_rec, acum_res, s1, s2 = [], [], 0, 0
    for a_, b_ in zip(rec, res):
        s1 += a_; s2 += b_
        acum_rec.append(s1); acum_res.append(s2)

    # 1) fluxo acumulado: 12 posições (jan–dez), escala até o próximo milhar
    W, H, ME, MB, MT, MD = 640, 340, 46, 28, 14, 120  # mesmo quadro (640×340) nos dois painéis
    FAIXA = 118  # faixa de baixo: represado no mês (delta), separada das linhas
    topo = max(1000, _arredondar_acima(max(acum_rec[-1], acum_res[-1]) * 1.05, 1000))  # AT-D06: ano zerado
    px = lambda i: ME + i * (W - ME - MD) / 11
    py = lambda v: MT + (H - MT - MB - FAIXA) * (1 - v / topo)
    pontos_rec = [(px(i), py(v)) for i, v in enumerate(acum_rec)]
    pontos_res = [(px(i), py(v)) for i, v in enumerate(acum_res)]
    fmt = lambda pts: " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    acumulado = {
        "w": W, "h": H, "base": H - MB, "base_linhas": round(py(0), 1), "esq": ME, "dir": W - MD,
        "linha_rec": fmt(pontos_rec), "linha_res": fmt(pontos_res),
        "vao": fmt(pontos_rec + pontos_res[::-1]),
        "grade": [{"y": round(py(v), 1), "rotulo": f"{v:,}".replace(",", ".")} for v in range(0, topo + 1, topo // 3)],
        "meses": [{"x": round(px(i), 1), "rotulo": formato.MESES[i]} for i in range(12)],
        "fim": {"x": round(pontos_rec[-1][0], 1), "y_rec": round(pontos_rec[-1][1], 1), "y_res": round(pontos_res[-1][1], 1),
                "rec": acum_rec[-1], "res": acum_res[-1], "seguem": acum_rec[-1] - acum_res[-1]},
        "texto": "; ".join(f"{formato.MESES[i]}: {r} recebidos e {s} resolvidos no acumulado"
                           for i, (r, s) in enumerate(zip(acum_rec, acum_res))),
    }

    # 2) dispersão (A25, decisão do Caio em 24/10/2026): a DEMANDA do mês é tudo o que havia para atender —
    #    represados que vieram do mês anterior + novos. x = para atender, y = resolvidos; % = resolvidos ÷ para atender
    #    (meio para cima, C8). Referências = o OBJETIVO 100% (resolver tudo o que havia para atender) e o corte de 90%.
    #    A média e o limite inferior natural (XmR, só meses completos) seguem calculados aqui, fora da tela.
    atd = [f + e for f, e in zip([0] + [m["fila"] for m in meses[:-1]], rec)]
    ent = [m["entregues_ano"] for m in meses]  # A25b (D53): o eixo vertical passa a ser o entregue ao cliente
    ext_mes = externas_por_mes(status)
    ext = [ext_mes.get(m["chave"], 0) for m in meses]  # A27: saídas por decisão de fora da equipe (fora da tela)
    com_quebra = [m["chave"] in ext_mes for m in meses]
    decl = [m["sem_entrega_ano"] for m in meses]  # declinados = todas as saídas sem entrega do mês
    dep = atd  # A30 (D58b): a base do % é tudo o que havia para atender
    pct_atd = [100 * s_ / a_ if a_ else 0 for s_, a_ in zip(res, dep)]
    comp_pct = [v for m, v in zip(meses, pct_atd) if not m["parcial"]]
    if len(comp_pct) >= 2:
        media_pct = sum(comp_pct) / len(comp_pct)
        am = sum(abs(a_ - b_) for a_, b_ in zip(comp_pct[1:], comp_pct[:-1])) / (len(comp_pct) - 1)
        lic_pct = max(0, media_pct - 2.66 * am)
    else:
        media_pct, lic_pct = (comp_pct[0] if comp_pct else 80), 0
    # Caio, 24/10/2026: as referências do gráfico voltam a ser o OBJETIVO — 100% (equilíbrio: resolver tudo o que havia
    # para atender) e o corte de 90% —, agora sobre a demanda total. A média e o limite XmR ficam só calculados.
    _media_xmr, _lic_xmr = media_pct, lic_pct  # só calculados (ficam para a ficha)
    # D53 (Caio, 26/10/2026): o visual do gráfico fica como estava (equilíbrio 100%, corte 90%, cores por faixa); só o
    # eixo vertical e o % passam a ser a ENTREGA (entregues ao cliente ÷ para atender). corte_pct = None desliga o corte
    # e as cores (todos os pontos neutros), se um dia a régua deixar de valer
    objetivo_pct, corte_pct = 100.0, 90.0
    fator_m, fator_l = objetivo_pct / 100, (corte_pct / 100 if corte_pct is not None else None)
    # D53 (Caio, 26/10/2026): o gráfico ocupa a coluna da direita — quadro mais alto (640×400) e margens menores
    S, SH, M, MB2, MT2, MD2 = 640, 400, 46, 30, 8, 14
    # D53 (Caio, 26/10/2026): eixos a partir de 0 (origem comum no canto), para as retas do equilíbrio (y = x) e do
    # corte (y = 0,9·x) saírem do mesmo ponto e se abrirem em leque; marcas "redondas" (ex.: 0, 250, 500, 750, 1.000)
    lo = 0
    topo_v = max(dep + res + [1]) * 1.05
    passo = next(p_ for p_ in (50, 100, 200, 250, 500, 1000, 2000, 2500, 5000, 10000) if topo_v / p_ <= 4)         if topo_v <= 40000 else _arredondar_acima(topo_v / 4, 1000)
    hi = max(passo, _arredondar_acima(topo_v, passo))  # AT-D06: meses zerados não deixam a escala sem amplitude
    pe = lambda v: M + (S - M - MD2) * (v - lo) / (hi - lo)
    pv = lambda v: SH - MB2 - (SH - MB2 - MT2) * (v - lo) / (hi - lo)
    # A30 (D58b): y = entregues no mês (entregues ao cliente + declinados); % = entregues no mês ÷ para atender
    pontos = [{"x": round(pe(d_), 1), "y": round(pv(s), 1), "rotulo": m["rotulo"], "parcial": m["parcial"],
               "rec": r, "res": s, "ent": e_, "acima": s >= fator_m * d_, "pct": pct_meio(s, d_),
               "pct_saiu": pct_meio(s, a_), "externos": x_, "declinados": dc, "dependia": d_, "com_quebra": cq}
              for m, r, s, e_, a_, x_, dc, d_, cq in zip(meses, rec, res, ent, atd, ext, decl, dep, com_quebra)]
    # A22/A25: a conta por trás do % de cada mês: represados que vieram + novos = para atender; resolvidos = entregues
    #      + saídas sem entrega; ficou = represado para o mês seguinte. % = resolvidos ÷ para atender (nunca passa de 100%).
    veio_ant = 0
    for q, m in zip(pontos, meses):
        q.update(nome=m["extenso"], veio=veio_ant, novos=m["entradas"], entregues=m["entregues_ano"],
                 sem=m["sem_entrega_ano"], fica=m["fila"], atender=veio_ant + m["entradas"],
                 do_represado=max(0, m["resp_ano"] - m["entradas"]))
        veio_ant = m["fila"]
    # faixa de cada mês: só com meta (corte); sem ela (D53), todos neutros
    for q in pontos:
        q["faixa"] = ("neutro" if corte_pct is None else "mais" if q["pct"] >= round(objetivo_pct)
                      else "perto" if q["pct"] >= round(corte_pct) else "menos")

    # rótulos sem sobreposição: evita os pontos, os outros rótulos e as duas linhas (equilíbrio e 90%)
    def _cruza_linha(caixa, fator):
        """True se a reta resolvidos = fator × recebidos passa dentro da caixa (cantos em lados opostos)."""
        lados = set()
        for cx_, cy_ in ((caixa[0], caixa[1]), (caixa[2], caixa[1]), (caixa[0], caixa[3]), (caixa[2], caixa[3])):
            v_rec = lo + (cx_ - pe(lo)) / (pe(hi) - pe(lo)) * (hi - lo)
            lados.add(cy_ < pv(fator * v_rec))
        return len(lados) > 1

    # AT-02 (25/10/2026): o texto do SVG tem 15,5 unidades do viewBox (≥ 11 px reais de 1280 a 1800 px); as larguras e
    # os deslocamentos dos rótulos acompanham a letra maior (antes 11 unidades: 6,6 por caractere)
    ocupados = [(q["x"] - 8, q["y"] - 8, q["x"] + 8, q["y"] + 8) for q in pontos]
    for q in pontos:
        larg = 9.2 * (len(q["rotulo"]) + len(str(q["pct"])) + 2)  # "jan 77%" (o mês parcial não leva mais "*")
        candidatos = [(dx, dy, anc) for dx, dy, anc in (
            (-12, -11, "end"), (12, 20, "start"), (-12, 20, "end"), (12, -11, "start"), (0, -17, "middle"), (0, 31, "middle"),
            (-15, 5, "end"), (15, 5, "start"),
            # D58: segundo anel, mais afastado, para meses agrupados (só quando o primeiro anel está todo ocupado)
            (-12, -30, "end"), (12, 39, "start"), (-12, 39, "end"), (12, -30, "start"), (0, -36, "middle"),
            (0, 50, "middle"), (-30, 5, "end"), (30, 5, "start"))]
        escolha = None
        for exigir_linha in (True, False):
            for dx, dy, anc in candidatos:
                x0 = q["x"] + dx - (larg if anc == "end" else larg / 2 if anc == "middle" else 0)
                caixa = (x0, q["y"] + dy - 14, x0 + larg, q["y"] + dy + 4)
                if any(caixa[0] < o[2] and caixa[2] > o[0] and caixa[1] < o[3] and caixa[3] > o[1] for o in ocupados):
                    continue
                if caixa[3] > pv(lo) - 2:  # D53: não desce sobre os números do eixo horizontal
                    continue
                if exigir_linha and (_cruza_linha(caixa, fator_m) or (fator_l is not None and _cruza_linha(caixa, fator_l))):
                    continue
                escolha = (dx, dy, anc, caixa)
                break
            if escolha:
                break
        dx, dy, anc, caixa = escolha or (12, -11, "start", (q["x"], q["y"], q["x"], q["y"]))
        q.update(rx=round(q["x"] + dx, 1), ry=round(q["y"] + dy, 1), ancora=anc)
        ocupados.append(caixa)
    completos = [(r, s) for m, r, s in zip(meses, rec, res) if not m["parcial"]]
    n = len(completos)
    corr = inclinacao = None
    if n >= 3:
        mx = sum(r for r, _ in completos) / n
        my = sum(s for _, s in completos) / n
        sxx = sum((r - mx) ** 2 for r, _ in completos)
        syy = sum((s - my) ** 2 for _, s in completos)
        sxy = sum((r - mx) * (s - my) for r, s in completos)
        if sxx and syy:
            corr = sxy / (sxx * syy) ** 0.5
            inclinacao = sxy / sxx
    marcas = list(range(int(lo), hi + 1, passo))  # até 4 intervalos por eixo
    dispersao = {
        "s": S, "sh": SH, "m": M, "x0": round(pe(lo), 1), "x1": round(pe(hi), 1), "y0": round(pv(lo), 1), "y1": round(pv(hi), 1),
        "pontos": pontos,
        # linhas de referência: objetivo 100% (y = x) e corte de 90% (y = 0,9·x), cortadas no quadro
        "objetivo": {"pct": round(objetivo_pct), "x0": round(pe(max(lo, lo / fator_m if fator_m else lo)), 1),
                  "y0": round(pv(max(lo, fator_m * lo)), 1), "x1": round(pe(hi), 1), "y1": round(pv(fator_m * hi), 1)},
        "corte": None if corte_pct is None else {
            "pct": round(corte_pct), "x0": round(pe(max(lo, lo / fator_l if fator_l else lo)), 1),
            "y0": round(pv(max(lo, fator_l * lo)), 1), "x1": round(pe(hi), 1), "y1": round(pv(fator_l * hi), 1)},
        # trilha dos meses em ordem (dispersão conectada): jan → fev → … facilita seguir o ano
        "trilha": " ".join(f"{q['x']},{q['y']}" for q in pontos),
        "marcas": [{"p_x": round(pe(v), 1), "p_y": round(pv(v), 1), "rotulo": f"{v:,}".replace(",", ".")} for v in marcas],
        "corr": corr, "inclinacao": inclinacao, "n": n,
        "acima": sum(1 for (r, s) in completos if s >= r),
        # AT-04: o mês parcial é dito ao leitor de tela com o período da carga ("out (parcial, até 22 de outubro)")
        "texto": "; ".join(f"{p['rotulo']}{' (parcial, ' + resultado['periodo'] + ')' if p['parcial'] else ''}: "
                           f"{p['dependia']} para atender, {p['res']} entregues no mês ({p['pct']}%)"
                           for p in pontos),
    }
    # 3) A17: onde estão os pedidos em andamento, pelo mês em que entraram (situação "em andamento" da gold de entradas,
    #    a mesma do Início). Se quase todos são do mês corrente, o que está aberto é trabalho em curso, não atraso.
    ab = [{"rotulo": m["rotulo"], "extenso": m["extenso"], "parcial": m["parcial"],
           "n": next((g["n"] for g in m["situacao"] if g["classe"] == "andamento"), 0)}
          for m in resultado["meses"] if not m["futuro"]]
    total_ab = sum(x["n"] for x in ab)
    topo_ab = max([x["n"] for x in ab] + [1])
    BW, BH, BE, BB, BT, BD = 640, 340, 16, 40, 66, 16  # topo livre para a frase de destaque
    passo_x = (BW - BE - BD) / 12
    for i, x in enumerate(ab):
        h = (BH - BB - BT) * x["n"] / topo_ab
        x.update(x=round(BE + i * passo_x + passo_x * 0.2, 1), w=round(passo_x * 0.6, 1),
                 y=round(BH - BB - h, 1), h=round(max(h, 1.5 if x["n"] else 0), 1),
                 cx=round(BE + i * passo_x + passo_x / 2, 1))
    atual = ab[-1] if ab else None
    abertos = {
        "w": BW, "h": BH, "base": BH - BB, "meses": ab,
        "rotulos": [{"cx": round(BE + i * passo_x + passo_x / 2, 1), "rotulo": formato.MESES[i]} for i in range(12)],
        "total": total_ab, "atual": atual,
        "pct_atual": formato.pct_inteiro(atual["n"], total_ab) if atual and total_ab else 0,  # F13: meio para cima
        "antigos": total_ab - (atual["n"] if atual else 0),
        "texto": "; ".join(f"{x['extenso']}: {x['n']} em andamento" for x in ab),
    }
    # 4) A18: represado no mês (delta) = recebidos − resolvidos no mês (entregues + saídas sem entrega). Positivo: o mês
    #    deixou pedidos para o seguinte (a fila cresceu); negativo: a equipe resolveu também parte do que vinha represado.
    #    Barras divergentes numa faixa própria abaixo das linhas, com o número escrito (sem eixo; a soma dá a fila atual).
    zero = H - MB - FAIXA / 2 + 14
    meia = FAIXA / 2 - 26
    maior = max([abs(m["entradas"] - m["resp_ano"]) for m in meses] + [1])
    acumulado["zero"] = round(zero, 1)
    acumulado["delta"] = []
    for i, m in enumerate(meses):
        d = m["entradas"] - m["resp_ano"]
        h = max(1.5, meia * abs(d) / maior) if d else 0
        acumulado["delta"].append({
            "x": round(px(i) - 11, 1), "w": 22, "h": round(h, 1), "y": round(zero - h if d > 0 else zero, 1),
            "n": d, "cx": round(px(i), 1), "parcial": m["parcial"], "sobe": d > 0,
            "y_rot": round(zero - h - 6 if d > 0 else zero + h + 13, 1)})
    acumulado["delta_soma"] = sum(x["n"] for x in acumulado["delta"])

    # 5) A18: equilíbrio mês a mês, com os meses em ordem (pedido do Caio): resolvidos ÷ recebidos no mês. A linha de
    #    100% é o equilíbrio (resolvemos o que entrou); acima, a fila diminuiu; abaixo, cresceu. O mês parcial fica vazado.
    razao = [100 * m["resp_ano"] / m["entradas"] if m["entradas"] else 0 for m in meses]
    CW, CH, CE, CB, CT, CD = 640, 340, 46, 28, 34, 40
    y_lo = min(60, min(razao) // 10 * 10 - 5)
    y_hi = max(120, -(-max(razao) // 10) * 10 + 5)
    cx = lambda i: CE + i * (CW - CE - CD) / 11
    cy = lambda v: CT + (CH - CT - CB) * (1 - (v - y_lo) / (y_hi - y_lo))
    pts = [{"x": round(cx(i), 1), "y": round(cy(v), 1), "v": round(v), "rotulo": m["rotulo"], "parcial": m["parcial"],
            "acima": v >= 100, "rec": m["entradas"], "res": m["resp_ano"]} for i, (m, v) in enumerate(zip(meses, razao))]
    completos_r = [q for q in pts if not q["parcial"]]
    controle = {
        "w": CW, "h": CH, "esq": CE, "dir": CW - CD, "base": CH - CB, "topo": CT,
        "linha": " ".join(f"{q['x']},{q['y']}" for q in pts),
        "pontos": pts, "y100": round(cy(100), 1),
        "grade": [{"y": round(cy(v), 1), "rotulo": f"{v}%"} for v in range(int(-(-y_lo // 20) * 20), int(y_hi) + 1, 20)],
        "meses": [{"x": round(cx(i), 1), "rotulo": formato.MESES[i]} for i in range(12)],
        "acima": sum(1 for q in completos_r if q["acima"]), "n": len(completos_r),
        "texto": "; ".join(f"{q['rotulo']}: {q['res']} resolvidos para {q['rec']} recebidos ({q['v']}%)" for q in pts),
    }
    # 6) A19 (24/10/2026, substitui o acumulado no painel da esquerda): a sombra do mês. Coluna-contorno = o que havia
    #    para atender no mês (represados do mês anterior + novos); parte cheia = resolvidos no mês (entregues + saídas
    #    sem entrega); o topo hachurado = o que ficou represado para o mês seguinte, com o número escrito. Lê-se mês a
    #    mês quanto ficou represado (fev: 85, e não "−2").
    SW, SH2, SE, SB, ST, SD = 640, 340, 46, 28, 30, 16
    filas = [0] + [m["fila"] for m in meses[:-1]]  # represados que vieram do mês anterior (janeiro = 0, D29)
    demandas = [f + m["entradas"] for m, f in zip(meses, filas)]
    topo_s = _arredondar_acima(max(demandas + [1]) * 1.05, 300)
    passo_s = (SW - SE - SD) / 12
    sy = lambda v: SH2 - SB - (SH2 - SB - ST) * v / topo_s
    colunas = []
    for i, (m, dem) in enumerate(zip(meses, demandas)):
        x = SE + i * passo_s + passo_s * 0.17
        w = passo_s * 0.66
        colunas.append({
            "x": round(x, 1), "w": round(w, 1), "cx": round(x + w / 2, 1), "parcial": m["parcial"],
            "y_dem": round(sy(dem), 1), "h_dem": round(sy(0) - sy(dem), 1),
            "y_res": round(sy(m["resp_ano"]), 1), "h_res": round(sy(0) - sy(m["resp_ano"]), 1),
            "y_rep": round(sy(dem), 1), "h_rep": round(sy(m["resp_ano"]) - sy(dem), 1),
            "demanda": dem, "resolvidos": m["resp_ano"], "represado": m["fila"], "veio": filas[i], "novos": m["entradas"],
            "rotulo": m["rotulo"], "extenso": m["extenso"]})
    sombra = {
        "w": SW, "h": SH2, "esq": SE, "dir": SW - SD, "base": round(sy(0), 1), "colunas": colunas,
        "grade": [{"y": round(sy(v), 1), "rotulo": f"{v:,}".replace(",", ".")} for v in range(0, topo_s + 1, topo_s // 3)],
        "meses": [{"x": round(SE + i * passo_s + passo_s / 2, 1), "rotulo": formato.MESES[i]} for i in range(12)],
        "texto": "; ".join(f"{c['extenso']}: {c['veio']} represados do mês anterior e {c['novos']} novos, {c['demanda']} para "
                           f"atender; {c['resolvidos']} resolvidos; {c['represado']} ficaram represados" for c in colunas),
    }
    # 7) A20 (24/10/2026, substitui as colunas da sombra por um gráfico de áreas, sem barras): curva suave do que havia
    #    para atender no mês e curva dos resolvidos; a faixa entre as duas é o que ficou represado (hachura vermelha),
    #    com o número escrito sobre cada mês. Mesmo dado da sombra (A19), outra forma.
    cxs = [c["x"] + c["w"] / 2 for c in colunas]
    p_dem = [(x, c["y_dem"]) for x, c in zip(cxs, colunas)]
    p_res = [(x, c["y_res"]) for x, c in zip(cxs, colunas)]

    def _curva(pts, inicio=True):
        """Catmull-Rom → Bézier (suave, passa por todos os pontos)."""
        d = (f"M{pts[0][0]:.1f},{pts[0][1]:.1f}" if inicio else f"L{pts[0][0]:.1f},{pts[0][1]:.1f}")
        for i in range(len(pts) - 1):
            p0 = pts[i - 1] if i else pts[i]
            p1, p2 = pts[i], pts[i + 1]
            p3 = pts[i + 2] if i + 2 < len(pts) else p2
            c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
            c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
            d += f" C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}"
        return d

    base = sombra["base"]
    area = {
        "dem": _curva(p_dem), "res": _curva(p_res),
        "area_dem": _curva(p_dem) + f" L{p_dem[-1][0]:.1f},{base} L{p_dem[0][0]:.1f},{base} Z",
        "area_res": _curva(p_res) + f" L{p_res[-1][0]:.1f},{base} L{p_res[0][0]:.1f},{base} Z",
        "faixa": _curva(p_dem) + " " + _curva(p_res[::-1], inicio=False) + " Z",
        "rotulos": [{"x": round(x, 1), "y": c["y_dem"], "y_res": c["y_res"], "n": c["represado"], "parcial": c["parcial"]}
                    for x, c in zip(cxs, colunas)],
        "fim": {"x": round(cxs[-1], 1), "y_dem": colunas[-1]["y_dem"], "y_res": colunas[-1]["y_res"]},
    }
    sombra["area"] = area

    # 8) A21 (24/10/2026): quanto trabalho o represado representa. Ritmo do mês = resolvidos ÷ dias úteis do mês
    #    (seg–sex sem feriados, app/expediente.sem_expediente; no mês parcial, até o último dia da carga). Dias de
    #    trabalho no represado = represado no fim do mês ÷ ritmo do mês: quantos dias a equipe levaria para zerar a fila
    #    no ritmo daquele mês. Referência fixa: 5 dias úteis (uma semana de trabalho).
    import datetime as _dt

    from app.expediente import sem_expediente
    ultimo_dia = resultado["ultimo"].date() if hasattr(resultado["ultimo"], "date") else resultado["ultimo"]
    feriados = sem_expediente(resultado["ano"])

    def _uteis(inicio, fim):  # [inicio, fim)
        n, d = 0, inicio
        while d < fim:
            if d.weekday() < 5 and d not in feriados:
                n += 1
            d += _dt.timedelta(days=1)
        return n

    pts_f = []
    for i, m in enumerate(meses):
        ini = _dt.date(resultado["ano"], i + 1, 1)
        fim = ultimo_dia + _dt.timedelta(days=1) if m["parcial"] else (
            _dt.date(resultado["ano"] + (i == 11), 1 if i == 11 else i + 2, 1))
        du = _uteis(ini, fim)
        ritmo = m["resp_ano"] / du if du else 0
        pts_f.append({"rotulo": m["rotulo"], "extenso": m["extenso"], "parcial": m["parcial"], "uteis": du,
                      "ritmo": ritmo, "fila": m["fila"], "dias": m["fila"] / ritmo if ritmo else 0})
    FW, FH, FE, FB, FT, FD = 640, 340, 46, 54, 44, 16
    topo_f = max(8, -(-max(q["dias"] for q in pts_f) // 2) * 2 + 1)
    fx = lambda i: FE + (i + 0.5) * (FW - FE - FD) / 12
    fy = lambda v: FT + (FH - FT - FB) * (1 - v / topo_f)
    for i, q in enumerate(pts_f):
        q.update(x=round(fx(i), 1), y=round(fy(q["dias"]), 1), dias_txt=f"{q['dias']:.1f}".replace(".", ","),
                 ritmo_txt=f"{q['ritmo']:.0f}")
    linha_f = " ".join(f"{q['x']},{q['y']}" for q in pts_f)
    folego = {
        "w": FW, "h": FH, "esq": FE, "dir": FW - FD, "base": round(fy(0), 1), "pontos": pts_f,
        "linha": linha_f,
        "area": f"M{pts_f[0]['x']},{fy(0):.1f} L" + " L".join(f"{q['x']},{q['y']}" for q in pts_f) + f" L{pts_f[-1]['x']},{fy(0):.1f} Z",
        "y_semana": round(fy(5), 1),
        "grade": [{"y": round(fy(v), 1), "rotulo": str(v)} for v in range(0, int(topo_f) + 1, 2)],
        "meses": [{"x": round(fx(i), 1), "rotulo": formato.MESES[i]} for i in range(12)],
        "atual": pts_f[-1], "ritmo_ini": pts_f[0]["ritmo"], "ritmo_fim": pts_f[-1]["ritmo"],
        "acima_semana": sum(1 for q in pts_f if q["dias"] > 5),
        "texto": "; ".join(f"{q['extenso']}: {q['fila']} represados, ritmo de {q['ritmo']:.0f} resolvidos por dia útil, "
                           f"{q['dias']:.1f} dias de trabalho" for q in pts_f),
    }
    # 9) A23 (24/10/2026, painel da esquerda, complementa a dispersão): recebidos e resolvidos MÊS A MÊS, duas linhas na
    #    ordem do ano; a área entre elas é pintada pela cor do equilíbrio — azul onde resolvemos mais do que entrou,
    #    vermelho onde entrou mais do que resolvemos (a área vermelha é o que foi para o represado). Linhas juntas =
    #    a equipe acompanha a demanda.
    LW, LH, LE, LB, LT, LD = 640, 340, 46, 28, 18, 16
    topo_l = max(200, _arredondar_acima(max(rec + res) * 1.08, 200))  # AT-D06: meses zerados
    lx = lambda i: LE + (i + 0.5) * (LW - LE - LD) / 12
    ly = lambda v: LT + (LH - LT - LB) * (1 - v / topo_l)
    pr = [(lx(i), ly(v)) for i, v in enumerate(rec)]
    ps = [(lx(i), ly(v)) for i, v in enumerate(res)]
    faixas = []
    for i in range(len(rec) - 1):
        d0, d1 = res[i] - rec[i], res[i + 1] - rec[i + 1]
        a0, a1, b0, b1 = pr[i], pr[i + 1], ps[i], ps[i + 1]
        if d0 * d1 >= 0:
            sinal = d0 + d1
            faixas.append({"pts": f"{a0[0]:.1f},{a0[1]:.1f} {a1[0]:.1f},{a1[1]:.1f} {b1[0]:.1f},{b1[1]:.1f} {b0[0]:.1f},{b0[1]:.1f}",
                           "classe": "mais" if sinal >= 0 else "menos"})
        else:  # as linhas se cruzam: dois triângulos
            t = d0 / (d0 - d1)
            cx_, cy_ = a0[0] + t * (a1[0] - a0[0]), a0[1] + t * (a1[1] - a0[1])
            faixas.append({"pts": f"{a0[0]:.1f},{a0[1]:.1f} {cx_:.1f},{cy_:.1f} {b0[0]:.1f},{b0[1]:.1f}",
                           "classe": "mais" if d0 > 0 else "menos"})
            faixas.append({"pts": f"{cx_:.1f},{cy_:.1f} {a1[0]:.1f},{a1[1]:.1f} {b1[0]:.1f},{b1[1]:.1f}",
                           "classe": "mais" if d1 > 0 else "menos"})
    # tendência (mínimos quadrados) de cada série, só meses completos: quanto a demanda e a capacidade crescem por mês
    def _reta(vals):
        idx = [i for i, m in enumerate(meses) if not m["parcial"]]
        n_ = len(idx)
        if n_ < 3:
            return None
        mx_ = sum(idx) / n_
        my_ = sum(vals[i] for i in idx) / n_
        sxx_ = sum((i - mx_) ** 2 for i in idx)
        b_ = sum((i - mx_) * (vals[i] - my_) for i in idx) / sxx_
        a_ = my_ - b_ * mx_
        i0, i1 = 0, len(vals) - 1
        return {"b": b_, "x1": round(lx(i0), 1), "y1": round(ly(a_ + b_ * i0), 1), "x2": round(lx(i1), 1),
                "y2": round(ly(a_ + b_ * i1), 1), "txt": f"{b_:+.0f}".replace("+", "+ ").replace("-", "− ")}
    tend_rec, tend_res = _reta(rec), _reta(res)
    rot = []
    for i, m in enumerate(meses):  # número de cada linha do lado de fora do par (não colidem)
        rec_em_cima = pr[i][1] <= ps[i][1]
        rot.append({"x": round(pr[i][0], 1), "rec": rec[i], "res": res[i],
                    "y_rec": round(pr[i][1] - 9 if rec_em_cima else pr[i][1] + 17, 1),
                    "y_res": round(ps[i][1] + 17 if rec_em_cima else ps[i][1] - 9, 1)})
    linhas = {
        "rotulos": rot, "tend_rec": tend_rec, "tend_res": tend_res,
        "w": LW, "h": LH, "esq": LE, "dir": LW - LD, "base": round(ly(0), 1),
        "rec": " ".join(f"{x:.1f},{y:.1f}" for x, y in pr), "res": " ".join(f"{x:.1f},{y:.1f}" for x, y in ps),
        "faixas": faixas,
        "pontos": [{"x": round(pr[i][0], 1), "y_rec": round(pr[i][1], 1), "y_res": round(ps[i][1], 1),
                    "parcial": m["parcial"]} for i, m in enumerate(meses)],
        "fim": {"x": round(pr[-1][0], 1), "y_rec": round(pr[-1][1], 1), "y_res": round(ps[-1][1], 1)},
        "grade": [{"y": round(ly(v), 1), "rotulo": f"{v:,}".replace(",", ".")} for v in range(0, topo_l + 1, topo_l // 4)],
        "meses": [{"x": round(lx(i), 1), "rotulo": formato.MESES[i]} for i in range(12)],
        "texto": "; ".join(f"{formato.MESES[i]}: {r_} recebidos, {s_} resolvidos" for i, (r_, s_) in enumerate(zip(rec, res))),
    }
    # 10) A24 (24/10/2026, painel da esquerda): extrato da demanda mês a mês, em quadro de calor. Linhas: veio do mês
    #     anterior, entrou, para atender, resolvemos, ficou para o mês seguinte. O "ficou" de um mês é o "veio" do
    #     seguinte (seta no quadro). Intensidade da cor em 5 níveis, relativa ao maior valor da própria linha.
    def _nivel(v, maior):
        return 0 if not v or not maior or v < 0 else min(5, 1 + int(4 * v / maior))  # AT-D06: nunca negativo
    veio = [0] + [m["fila"] for m in meses[:-1]]
    linhas_antigas = [
        ("veio", "Veio do mês anterior", veio),
        ("entrou", "Entrou", rec),
        ("atender", "Para atender", [v + e for v, e in zip(veio, rec)]),
        # Caio, 24/10/2026: o que saiu separado em entregues (resolvemos) e encerrados sem entrega (declinado, standby,
        # encerrado); os dois juntos fecham a conta: para atender − entregues − encerrados = ficou
        ("resolvemos", "Entregues ao cliente", [m["entregues_ano"] for m in meses]),  # decisão 6 (25/10/2026)
        # G3-8 (glossário): o mesmo termo do Início e da faixa ("saíram sem entrega"); aqui, pelo mês da saída
        ("encerrados", "Saíram sem entrega no mês", [m["sem_entrega_ano"] for m in meses]),
        ("ficou", "Ficou para o mês seguinte", [m["fila"] for m in meses]),
    ]
    del linhas_antigas  # A24 (até 26/10/2026): seis linhas soltas; histórico na ficha
    # A24b (D53, 26/10/2026): extrato em três blocos com subtotais — ENTRADA (veio + entrou = para atender), SAÍDA
    # (entregues + sem entrega = saiu no mês) e SALDO (para atender − saiu = ficou para o mês seguinte)
    atender = [v + e for v, e in zip(veio, rec)]
    sem = [m["sem_entrega_ano"] for m in meses]
    blocos_q = [
        ("entrada", "Entrada", [("veio", "", "Veio do mês anterior", veio, False), ("entrou", "+", "Entrou", rec, False),
                                ("atender", "=", "Para atender", atender, True)]),
        ("saida", "Saída", [("entregues", "", "Entregues ao cliente", ent, False),
                            # D58 (Caio, 27/10/2026): nomes da tela
                            ("sem", "+", "Declinados (Não teve seguimento)", sem, False),
                            ("saiu", "=", "Entregues no Mês", res, True)]),
        ("saldo", "Saldo", [("ficou", "=", "Ficou para o mês seguinte", [m["fila"] for m in meses], True)]),
    ]
    blocos = [{"chave": bc, "nome": bn, "linhas": [
        {"chave": ch, "op": op, "nome": nome, "subtotal": sub,
         "celulas": [{"v": v, "nivel": _nivel(v, max(vals) if vals else 0)} for v in vals]}
        for ch, op, nome, vals, sub in ls]} for bc, bn, ls in blocos_q]
    quadro = {
        "meses": [{"rotulo": m["rotulo"], "parcial": m["parcial"], "chave": m["chave"], "extenso": m["extenso"]}
                  for m in meses],
        "blocos": blocos,
        "linhas": [l for b in blocos for l in b["linhas"]],
        # A25b: % entregue sobre o que havia para atender (meio para cima, C8); secundária: % que saiu (entregues + sem)
        # A27: % entregue da demanda que dependia da equipe (o mesmo dos pontos da dispersão) e a conta de cada mês
        "pct": [q_["pct"] for q_ in pontos],
        # A30 (D58b): a conta de cada mês = (entregues ao cliente + declinados) ÷ para atender (itens = status, A26)
        "conta": [{"atender": a_, "declinados": q_["declinados"], "dependia": q_["dependia"], "entregues": e_,
                   "saiu": q_["res"], "pct": q_["pct"], "com_quebra": q_["com_quebra"],
                   "itens": ((status or {}).get("meses", {}).get(m["chave"]) or {}).get("itens", [])}
                  for q_, a_, e_, m in zip(pontos, atender, ent, meses)],
        "pct_saiu": [pct_meio(r_, a_) for r_, a_ in zip(res, atender)],
        # A28: o que ficou cresceu ou caiu em relação ao mês anterior (janeiro: sem comparação)
        "ficou_var": [None] + [b_ - a_ for a_, b_ in zip([m["fila"] for m in meses][:-1], [m["fila"] for m in meses][1:])],
        "objetivo": dispersao["objetivo"]["pct"], "corte": dispersao["corte"]["pct"] if dispersao["corte"] else None,
    }
    return {"acumulado": acumulado, "dispersao": dispersao, "abertos": abertos, "controle": controle, "sombra": sombra,
            "folego": folego, "linhas": linhas, "quadro": quadro}


# ---------- A26 (D53, 26/10/2026): composição por status das saídas sem entrega ----------
def status_sem_entrega(resultado: dict, df: pd.DataFrame | None) -> dict | None:
    """Para cada mês do quadro, os status do board (Declinado Internamente, Standby, ...) que compõem "Saíram sem
    entrega", da gold `gld_agenciamento_2026_saidas_status` (regras da gold de fluxo). O mês só leva a composição quando
    a soma bate com a célula; o ano, só quando todos os meses batem. Sem a tabela: None."""
    if df is None or df.empty:
        return None
    meses_df = pd.to_datetime(df["mes"]).dt.strftime("%Y-%m")
    saida = {"meses": {}, "ano": None}
    todos_batem, soma = True, {}
    for m in resultado["meses"]:
        if m["futuro"] or m.get("sem_entrega_ano") is None:
            continue
        linhas = df.loc[meses_df == m["chave"]]
        itens = [{"status": str(s), "n": int(n), "externo": str(s) in STATUS_EXTERNOS} for s, n in
                 linhas.groupby("status")["n"].sum().sort_values(ascending=False, kind="stable").items() if n]
        total = sum(i["n"] for i in itens)
        confere = total == m["sem_entrega_ano"]
        todos_batem &= confere
        saida["meses"][m["chave"]] = {"itens": itens if confere else [], "total": m["sem_entrega_ano"], "confere": confere,
                                      "sem_data": int(linhas["sem_data"].sum()) if confere else 0,
                                      "externos": sum(i["n"] for i in itens if i["externo"]) if confere else 0}
        for i in itens:
            soma[i["status"]] = soma.get(i["status"], 0) + i["n"]
    if todos_batem and saida["meses"]:
        itens = sorted(({"status": s, "n": n, "externo": s in STATUS_EXTERNOS} for s, n in soma.items()), key=lambda i: -i["n"])
        saida["ano"] = {"itens": itens, "total": sum(i["n"] for i in itens), "confere": True,
                        "sem_data": sum(v["sem_data"] for v in saida["meses"].values()),
                        "externos": sum(i["n"] for i in itens if i["externo"])}
    return saida
