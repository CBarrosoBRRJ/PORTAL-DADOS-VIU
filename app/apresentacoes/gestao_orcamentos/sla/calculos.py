"""Regras de cálculo da apresentação SLA — definidas com o Caio uma a uma (PRD, seção 9.1; ficha docs/paginas/sla.md).

Mudou uma regra? Altere aqui e registre na ficha e no PRD. O template só mostra.

Fonte (D57, 27/10/2026): C1–C4, C9 e C14 vêm prontos da view gold `gld_agenciamento_2026_sla_entregas` (e K1 da
`..._sla_entregas_status`), calculados no PPD-GOLDEN-AGENCIAMENTO-MONDAY com o expediente sem almoço (R24 da tabela de
movimentos). O site não refaz essas regras; aqui ficam só as leituras sobre elas (faixas, meta, estudo).

C1  Orçamento pronto = 1ª chegada do projeto em Aguardando Feedback (1º passo de fase `cliente`).
C2  Tempo com a equipe até pronto = horas úteis dos passos da equipe antes de C1 — **inclusive Entrada** (a fila está sob
    controle da equipe; decisão do Caio, 21/10/2026) —, **sem almoço** (10h–13h + 14h–19h). Validações de talento/TM e
    as Cotações (externa e de elenco) contam. **Fica fora (D-SLA-2, 25/10/2026):** "Em elaboração - Retorno
    Marca/Executivo" (espera da marca; status em minúsculas começando por "em elaboração - retorno marca"), além de
    Standby e fechamento (que não são fase `equipe`). Calculado na gold (R24 e view de entregas, D57).
C3  Tempo de calendário até pronto = entrada do passo C1 − entrada do passo 1, em horas corridas (o cliente vê
    dias corridos).
C4  Recorte: só projetos entregues (que têm C1). **Mês de referência = mês da 1ª entrega** (entrada do passo C1;
    D-SLA-1, 25/10/2026): o mês fecha no dia 1º seguinte, como no Atendimento (mês do evento). Retrabalho fica fora.
    Projeto cuja 1ª ida ao cliente é o passo 1 (sem Entrada antes — incompatível com a R12 da gold) é descartado e
    contado em `invalidos`, nunca mostrado como entrega instantânea.
C5  Faixas de trabalho (D-SLA-7, 25/10/2026, revisa a D-SLA-3): até 1 dia (≤ 8 h), 1 a 2 dias (8–16 h) e acima de
    2 dias (> 16 h); dia útil = 8 h.
C6  Meta sugerida (D-SLA-7): metade dos orçamentos (50%) prontos em até 2 dias de trabalho (16 h), o mesmo que "o
    típico (mediana) em até 2 dias". Ainda não oficial. A mensagem compara a mediana EXATA com 16 h (16,3 h fica fora,
    mesmo que a tela arredonde para "16 h"). Indicador ao lado, sem meta: % acima de 5 dias de trabalho (> 40 h, C12).
C7  Meses completos (A1): todas as análises — resposta, dias no calendário, seletor de talentos, faixas do ano, meta,
    estudo — usam só os meses completos de ENTREGA, de janeiro até o mês anterior ao da carga. O mês vigente (parcial)
    aparece só no gráfico mensal, vazado (A2), e não entra em nenhuma conta. Em janeiro não há mês completo: a tela
    diz isso em vez de mostrar percentuais vazios.
A2  Mês vigente no gráfico: barra vazada (só contorno) com "parcial" e "até dd/mm" (o dia do rodapé); com menos de
    MIN_PARCIAL entregas, barra vazia ("aguardando entregas"), sem %.
A3  Mediana do mês: mediana das horas da equipe de cada mês, numa linha discreta sob os meses; mês parcial com "—" se
    tiver menos de MIN_PARCIAL entregas.
C9  Espera na fila = horas úteis (sem almoço) em Entrada antes de C1: o pedido parado no backlog, antes de a equipe
    começar. É uma parte de C2, medida à parte para slides futuros (mediana do ano, C7).
C10 Grupos de talento: `exclusivo` do projeto (gold/silver: exclusivo na data do projeto). Exclusivos = TRUE, não
    exclusivos = FALSE; projetos sem talento (NULL) só entram em "Todos".
C11 Leitura por regra (sem LLM, D2): entre os meses completos, o melhor e o pior em "até 2 dias", e o último mês
    comparado ao ano (acima/abaixo/igual).
C12 Cauda (pedidos lentos): acima de 5 dias de trabalho (> 40 h). Peso = parcela das horas da equipe do ano que esses
    pedidos somam; "sem a cauda" = mediana e % em até 2 dias recalculados sem eles. Faixas da distribuição: ≤ 8, 8–16,
    16–24, 24–40 e > 40 h, com pedidos e horas fechando em 100 pelo maior resto (E8c). Na tela do SLA (D38): "N% passam
    de 5 dias de trabalho (M orçamentos)", por grupo, nos meses completos (C7).
C13 Exclusivos × não exclusivos (os "intervenientes"): mesmos indicadores lado a lado (C10), meses completos (C7).
C14 Etapas: Fila (Entrada), Elaboração (status "Em elaboração…", sem o Retorno Marca) e Revisão (status "Em
    revisão…") dentro de C2. Os sub-status só existem desde 14/05/2026: as leituras por etapa usam os meses completos a
    partir de junho (MES_ETAPAS).
C8  Arredondamento na tela: "até 1 dia" e o total "até 2 dias" arredondados direto (meio para cima); "1 a 2 dias" =
    até 2 − até 1 e "acima de 2 dias" = 100 − total, para as faixas sempre somarem o que está escrito.
"""

import hashlib
import math
import re
import threading
from datetime import datetime, time
from itertools import pairwise
from statistics import NormalDist, correlation

import pandas as pd
from markupsafe import escape

# D68: `corte_regra` = app/corte.py (o nome `corte` já é o dia de corte dentro das funções)
from app import config, formato
from app import corte as corte_regra
from app.dados import versao_de

HORAS_DIA = 8  # C5: 10h–13h + 14h–19h
LIMITE_DIAS = 2  # C5, C6 (D-SLA-7, D38: revisa a D-SLA-3, que era 3 dias)
META = 0.50  # C6: metade em até 2 dias (= mediana em até 2 dias)
META_H = LIMITE_DIAS * HORAS_DIA  # 16 h
FILA = "Entrada"  # C9: status que é espera na fila (dentro do tempo da equipe, C2)
RETORNO_MARCA = "em elaboração - retorno marca"  # C2 (D-SLA-2): espera da marca, fora do tempo da equipe
CAUDA_H = 40  # C12: acima de 5 dias de trabalho
MES_ETAPAS = "06"  # C14: primeiro mês completo com os sub-status de elaboração e revisão
MIN_PARCIAL = 30  # A2, A3: entregas mínimas para mostrar o % e a mediana do mês parcial

_cache: dict = {}
_cache_status: dict = {}  # K1: horas por orçamento e status, mesma chave de `_cache`
# F14 (31/10/2026): `_cache` e `_cache_status` são publicados juntos, sob a mesma trava; uma requisição nunca vê a entrega de uma carga com as horas por status de outra
_trava = threading.Lock()


def limpar_cache() -> None:
    with _trava:
        _cache.clear()
        _cache_status.clear()


def _carga(df: pd.DataFrame):
    """`_processado_em` da carga (para casar movimentos e views); None sem a coluna ou vazia."""
    if "_processado_em" not in df or not df["_processado_em"].notna().any():
        return None
    return pd.to_datetime(df["_processado_em"], utc=True).max()


def _da_gold(mov: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """As views `gld_agenciamento_2026_sla_entregas` e `..._sla_entregas_status` da MESMA carga dos movimentos `mov`. A
    view reflete a tabela na hora; se a lida antes for de outra carga (os movimentos acabaram de mudar), relê uma vez."""
    from app import dados

    e, ps = dados.sla_entregas.df(), dados.sla_entregas_status.df()
    carga = _carga(mov)
    if carga is not None and (_carga(e) not in (None, carga) or _carga(ps) not in (None, carga)):
        e, ps = dados.sla_entregas.df(forcar=True), dados.sla_entregas_status.df(forcar=True)
        if _carga(e) not in (None, carga) or _carga(ps) not in (None, carga):
            raise dados.DadosIndisponiveis("SLA: views de entregas de outra carga que a dos movimentos")
    return e, ps


def entregas(mov: pd.DataFrame) -> pd.DataFrame:
    """Uma linha por orçamento entregue (C1, C4): mês da 1ª entrega, horas com a equipe sem almoço (C2), na fila (C9), em
    elaboração e em revisão (C14), de calendário (C3), dias úteis (C3b, C3c), se é card de pacote (X6) e o tipo de input
    (J1). Vem pronto da view gold `gld_agenciamento_2026_sla_entregas` (D57, 27/10/2026: o site não refaz a regra); aqui
    só os tipos voltam ao formato das telas (mês "AAAA-MM", exclusivo True/False/None).

    `mov` = a carga dos movimentos: a view precisa ser da mesma carga. Guardado por carga (`df.attrs["versao"]`)."""
    chave = versao_de(mov)
    return _publicado(mov, chave)[0]


def _publicado(mov: pd.DataFrame, chave) -> tuple:
    """(entregas, horas por status) da carga: a conta roda fora da trava (uma carga nova aquecendo não segura as páginas
    da carga no ar) e o par é publicado de uma vez; se outra thread publicou antes, vale o dela."""
    with _trava:
        if chave in _cache and chave in _cache_status:
            return _cache[chave], _cache_status[chave]
    e, status = _contar_entregas(mov)
    with _trava:
        if chave in _cache and chave in _cache_status:
            return _cache[chave], _cache_status[chave]
        # guarda as 3 últimas (carga no ar + carga nova sendo aquecida em segundo plano + conferência)
        while len(_cache) >= 3:
            velha = next(iter(_cache))
            _cache.pop(velha, None)
            _cache_status.pop(velha, None)
        _cache[chave], _cache_status[chave] = e, status
        return e, status


def _contar_entregas(mov: pd.DataFrame) -> tuple:
    bruto, ps = _da_gold(mov)
    e = pd.DataFrame({
        "projeto_id": bruto["projeto_id"].astype(str),
        "mes": pd.to_datetime(bruto["mes"]).dt.strftime("%Y-%m"),
        "mes_entrada": pd.to_datetime(bruto["mes_entrada"]).dt.strftime("%Y-%m"),
        "entregue_em": pd.to_datetime(bruto["entregue_em"]),
        # Caio, 03/11/2026: entrada do pedido (coluna `inicio` da view), para a lista dos fora da curva
        "inicio": pd.to_datetime(bruto["inicio"]) if "inicio" in bruto else pd.NaT,
        "exclusivo": bruto["exclusivo"].astype(object).where(bruto["exclusivo"].notna(), None),  # C10: NA vira None
        **{c: bruto[c].astype(float) for c in ("h_trabalho", "h_fila", "h_elaboracao", "h_revisao", "h_calendario",
                                               "dias_uteis_fr")},
        "dias_uteis": bruto["dias_uteis"].astype(int),
        "pacote": bruto["pacote"].astype(bool),
        "tipo_input": bruto["tipo_de_input"].astype(object).where(bruto["tipo_de_input"].notna(), None),
    }).sort_values("projeto_id", kind="stable").reset_index(drop=True)
    # K1 (slide 6): horas de cada orçamento em cada status (view `..._sla_entregas_status`); por orçamento, soma h_trabalho
    status = pd.DataFrame({"projeto_id": ps["projeto_id"].astype(str), "status": ps["status"].astype(str),
                           "h": ps["h"].astype(float)}).sort_values(["projeto_id", "status"]).reset_index(drop=True)
    return e, status


def horas_por_status(mov: pd.DataFrame) -> pd.DataFrame:
    """K1: projeto_id, status, h — horas úteis (sem almoço) de cada orçamento entregue em cada status da equipe antes da
    1ª entrega, sem o Retorno Marca (C2). Por orçamento, a soma é o `h_trabalho` de `entregas`."""
    chave = versao_de(mov)
    return _publicado(mov, chave)[1]


def _pontos(fracao: float) -> int:
    """Percentual inteiro, meio para cima (C8)."""
    return math.floor(fracao * 100 + 0.5)


def _faixas(h: pd.Series) -> dict:
    """C5, C8 (D-SLA-7): as três faixas (exatas, para as alturas) e o que aparece escrito (somando 100)."""
    n = len(h)
    if not n:
        return {"n": 0, "ate1": None, "de1a2": None, "acima2": None, "ate2": None, "mediana": None, "tela": None}
    ate1, ate2 = ((h <= d * HORAS_DIA).mean() for d in (1, LIMITE_DIAS))
    p1, p2 = _pontos(ate1), _pontos(ate2)
    return {"n": n, "ate1": ate1, "de1a2": ate2 - ate1, "acima2": 1 - ate2, "ate2": ate2,
            "mediana": float(h.median()),
            # o que aparece escrito (C8); as alturas das barras usam os valores exatos
            "tela": {"ate1": p1, "de1a2": p2 - p1, "acima2": 100 - p2, "ate2": p2}}


def _h_meta(m: float) -> str:
    """C6: a mediana escrita perto da meta. Em horas inteiras (meio para cima); perto de 16 h, com 1 casa, para o texto
    nunca pôr do lado errado da meta um valor arredondado: logo acima (16 < m < 16,5, que arredondaria para "16 h"),
    arredondada para cima (16,3 h; 16,01 h → 16,1 h); logo abaixo (15,5 ≤ m < 16, que arredondaria para "16 h"),
    arredondada para baixo (15,96 h → 15,9 h). Batalha 2 (G2-2): a mesma função escreve o selo de cada mês do SLA."""
    if META_H < m < META_H + 0.5:
        return _br1(math.ceil(m * 10) / 10) + " h"
    if META_H - 0.5 <= m < META_H:
        return _br1(math.floor(m * 10) / 10) + " h"
    return f"{_arred(m)} h"


def _br1(x: float) -> str:
    return f"{x:.1f}".replace(".", ",")


def meta_tipico(m: float | None) -> dict | None:
    """C6 (D38): o típico (mediana exata) contra a meta de 2 dias (16 h). `acima_txt` = quanto passa, na mesma precisão
    do valor escrito (20 h → "4 h"; 16,3 h → "0,3 h")."""
    if m is None:
        return None
    na_meta = m <= META_H
    if na_meta:
        acima = None
    elif m >= META_H + 0.5:
        acima = f"{_arred(m) - META_H} h"
    else:
        acima = _br1(math.ceil(m * 10) / 10 - META_H) + " h"
    return {"na_meta": na_meta, "mediana_txt": _h_meta(m), "acima_txt": acima}


GRUPOS = {  # C10: chave na URL -> (rótulo, filtro)
    "todos": ("Todos", lambda e: e.index == e.index),
    "exclusivos": ("Exclusivos", lambda e: e["exclusivo"].eq(True)),
    "nao-exclusivos": ("Não exclusivos", lambda e: e["exclusivo"].eq(False)),
}


def _mediana(serie: pd.Series) -> float | None:
    return float(serie.median()) if len(serie) else None


def _completos(e: pd.DataFrame, mes_parcial: str) -> pd.Series:
    """C7 (A1): meses completos de entrega do ano da carga (janeiro até o mês anterior ao parcial)."""
    return (e["mes"] >= f"{mes_parcial[:4]}-01") & (e["mes"] < mes_parcial)


def entrega(mov: pd.DataFrame, mes_parcial: str, grupo: str = "todos") -> dict:
    """Números do slide "Quanto tempo levamos para entregar um orçamento?", para um grupo de talento (C10)."""
    from app import sla

    todos = entregas(mov)
    ano = mes_parcial[:4]
    no_ano = _completos(todos, mes_parcial)
    grupos = [{"chave": k, "rotulo": rot, "atual": k == grupo,
               "mediana_h_trabalho": _mediana(todos.loc[no_ano & filtro(todos), "h_trabalho"]),
               "n": int((no_ano & filtro(todos)).sum())}
              for k, (rot, filtro) in GRUPOS.items()]
    e = todos.loc[GRUPOS[grupo][1](todos)]
    completos = e.loc[_completos(e, mes_parcial)]  # C7
    corte = sla.data_corte(mov)
    ate = corte.strftime("%d/%m") if corte.strftime("%Y-%m") == mes_parcial else None  # A2: "até 22/10"
    # D68: com o recorte do mês fechado, o mês da carga (novembro) ainda não começou na tela: sem barra de mês parcial,
    # e nenhuma entrega depois do último dia mostrado entra no gráfico
    sem_parcial = corte_regra.mes_fechado_ligado()
    if sem_parcial:
        e = e.loc[e["mes"] <= corte.strftime("%Y-%m")]
    meses = []
    for m in range(1, 13):
        chave = f"{ano}-{m:02d}"
        f = _faixas(e.loc[e["mes"] == chave, "h_trabalho"])
        parcial = chave == mes_parcial and not sem_parcial
        meses.append({
            "chave": chave,
            "rotulo": formato.MESES[m - 1],
            "parcial": parcial,
            "futuro": chave > mes_parcial or (sem_parcial and chave == mes_parcial),
            "ate": ate if parcial else None,
            # A2/A3: mês parcial com poucas entregas: sem %, sem mediana ("aguardando entregas")
            "aguardando": parcial and f["n"] < MIN_PARCIAL,
            **f,
            # G2-2: o selo do mês na mesma escrita do estudo (C6): 16,4 h, nunca "16 h" com 49%
            "mediana_txt": _h_meta(f["mediana"]) if f["n"] else None,
        })
    # leitura por regra (C11): melhor e pior mês completo e o último mês contra o ano
    fechados = [m for m in meses if m["n"] and not m["parcial"] and not m["futuro"]]
    leitura = None
    if len(fechados) >= 2:
        melhor, pior, ultimo = max(fechados, key=lambda m: m["ate2"]), min(fechados, key=lambda m: m["ate2"]), fechados[-1]
        ano_pct = _pontos((completos["h_trabalho"] <= META_H).mean())
        comparacao = "acima" if ultimo["tela"]["ate2"] > ano_pct else ("abaixo" if ultimo["tela"]["ate2"] < ano_pct else "igual")
        leitura = (f"Melhor mês: {melhor['rotulo']} ({melhor['tela']['ate2']}%). Pior: {pior['rotulo']} ({pior['tela']['ate2']}%). "
                   f"{ultimo['rotulo'].capitalize()} fechou em {ultimo['tela']['ate2']}%, "
                   + (f"{comparacao} do ano ({ano_pct}%)." if comparacao != "igual" else "igual ao ano."))
    mes_num = int(mes_parcial[5:])
    return {
        "leitura": leitura,
        "n_ano": len(completos),
        "ano_num": ano,
        "invalidos": todos.attrs.get("invalidos", 0),
        "mediana_h_trabalho": _mediana(completos["h_trabalho"]),
        "mediana_dias_calendario": (_mediana(completos["h_calendario"]) / 24) if len(completos) else None,
        # C3b: mediana de dias úteis até o cliente receber, inteira (meio para cima, C8)
        "mediana_dias_uteis": (math.floor(_mediana(completos["dias_uteis"]) + 0.5) if len(completos) else None),
        # C3c (D54): o que a tela mostra — mediana dos dias úteis com fração, 1 casa (meio para cima) e o exemplo da semana
        "dias_uteis_cliente": dias_uteis_cliente(_mediana(completos["dias_uteis_fr"])) if len(completos) else None,
        "mediana_h_fila": _mediana(completos["h_fila"]),
        "ano": _faixas(completos["h_trabalho"]),
        "periodo": (formato.MESES[0] if mes_num == 2 else f"{formato.MESES[0]} a {formato.MESES[mes_num - 2]}") if mes_num > 1 else "",
        "meses": meses,
        "grupo": grupo,
        "grupos": grupos,
        "meta": META,
        "limite_dias": LIMITE_DIAS,
        "limite_horas": META_H,
        # C6 (D38): o típico do grupo contra a meta (mediana exata) e o indicador ao lado, sem meta (C12)
        "tipico": meta_tipico(_mediana(completos["h_trabalho"])),
        "acima5": _pontos((completos["h_trabalho"] > CAUDA_H).mean()) if len(completos) else None,
        "n_acima5": int((completos["h_trabalho"] > CAUDA_H).sum()),
        "min_parcial": MIN_PARCIAL,
    }


def _pcts(valores: list[float], alvo: int = 100, total: float | None = None) -> list[int]:
    """Parcelas inteiras pelo maior resto (E8c) que somam `alvo` (100 por padrão), em % de `total` (padrão: a soma)."""
    total = sum(valores) if total is None else total
    if not total:
        return [0] * len(valores)
    exatos = [v * 100 / total for v in valores]
    base = [math.floor(x) for x in exatos]
    for i in sorted(range(len(valores)), key=lambda i: -(exatos[i] - base[i]))[:max(alvo - sum(base), 0)]:
        base[i] += 1
    return base


FAIXAS_CAUDA = ((0, 8, "até 1 dia"), (8, 16, "1 a 2 dias"), (16, 24, "2 a 3 dias"), (24, 40, "3 a 5 dias"),
                (40, math.inf, "mais de 5 dias"))


def _indicadores(h: pd.Series) -> dict:
    return {"n": len(h), "mediana": _mediana(h),
            "ate2": _pontos((h <= META_H).mean()) if len(h) else None,
            "cauda_pct": _pontos((h > CAUDA_H).mean()) if len(h) else None}


def leituras(mov: pd.DataFrame, mes_parcial: str) -> dict | None:
    """Leituras do SLA fora da tela (C12–C14): os pedidos lentos e o peso deles; exclusivos × não exclusivos."""
    todos = entregas(mov)
    ano = mes_parcial[:4]
    c = todos.loc[_completos(todos, mes_parcial)]  # C7
    if len(c) < 30:
        return None
    h = c["h_trabalho"]
    cauda = h > CAUDA_H
    contagens = [int(((h > a) & (h <= b)).sum()) if a else int((h <= b).sum()) for a, b, _ in FAIXAS_CAUDA]
    horas = [float(h[(h > a) & (h <= b)].sum()) if a else float(h[h <= b].sum()) for a, b, _ in FAIXAS_CAUDA]
    # pedidos: as duas primeiras faixas seguem a C8 (iguais ao gráfico: até 1 dia e 1 a 2 dias); as três de cima
    # repartem o resto (100 − até 2 dias) pelo maior resto, para o total fechar em 100
    tela = _faixas(h)["tela"]
    pedidos = [tela["ate1"], tela["de1a2"]] + _pcts(contagens[2:], alvo=tela["acima2"], total=sum(contagens))
    faixas = [{"rotulo": rot, "n": n, "pct_pedidos": pp, "pct_horas": ph, "cauda": a >= CAUDA_H}
              for (a, _, rot), n, pp, ph in zip(FAIXAS_CAUDA, contagens, pedidos, _pcts(horas))]
    desde = c["mes"] >= f"{ano}-{MES_ETAPAS}"  # C14
    cauda_etapas = c.loc[desde & cauda]
    elab_cauda = (_pontos(cauda_etapas["h_elaboracao"].sum() / cauda_etapas["h_trabalho"].sum())
                  if len(cauda_etapas) and cauda_etapas["h_trabalho"].sum() else None)
    mes_num = int(mes_parcial[5:])
    grupos = []
    for chave in ("exclusivos", "nao-exclusivos"):
        rot, filtro = GRUPOS[chave]
        g = c.loc[filtro(c)]
        elab = g.loc[(g["mes"] >= f"{ano}-{MES_ETAPAS}") & (g["h_elaboracao"] > 0), "h_elaboracao"]
        grupos.append({"chave": chave, "rotulo": rot, **_indicadores(g["h_trabalho"]),
                       "elaboracao_mediana": _mediana(elab)})
    return {
        "n": len(c),
        "periodo": f"{formato.MESES[0]} a {formato.MESES[mes_num - 2]}" if mes_num > 2 else formato.MESES[0],
        "periodo_etapas": f"{formato.MESES[int(MES_ETAPAS) - 1]} a {formato.MESES[mes_num - 2]}",
        "todos": _indicadores(h),
        "faixas": faixas,
        "cauda": {"n": int(cauda.sum()), "pct_pedidos": faixas[-1]["pct_pedidos"], "pct_horas": faixas[-1]["pct_horas"],
                  "elaboracao_pct": elab_cauda},
        "sem_cauda": _indicadores(h[~cauda]),
        "grupos": grupos,
        "meta": _pontos(META),
        "limite_horas": META_H,
    }


def cobertura(mov: pd.DataFrame, fluxo: pd.DataFrame | None, mes_parcial: str) -> dict | None:
    """D-SLA-4: N orçamentos medidos (entregues nos meses completos, C7) de M entregues pela gold de fluxo no mesmo
    recorte (evento `entregue`, mês do evento de janeiro até o mês anterior ao parcial, safras do ano, família
    "Nenhuma" = sem as famílias fora da regra R3/R4). None sem a tabela de fluxo, com cargas de dias diferentes ou
    com N > M (fontes incoerentes: a tela não mostra uma cobertura acima de 100%)."""
    from app import dados

    if fluxo is None or fluxo.empty:
        return None
    d_sla, d_fluxo = dados.data_carga(mov), dados.data_carga(fluxo)
    if d_sla is not None and d_fluxo is not None and d_sla != d_fluxo:
        return None
    ano = mes_parcial[:4]
    todos = entregas(mov)
    n = int(_completos(todos, mes_parcial).sum())
    evento = pd.to_datetime(fluxo["mes_evento"]).dt.strftime("%Y-%m")
    safra = pd.to_datetime(fluxo["mes_entrada"]).dt.strftime("%Y-%m")
    sel = ((fluxo["evento"] == "entregue") & (evento >= f"{ano}-01") & (evento < mes_parcial) & (safra >= f"{ano}-01")
           & (fluxo["familia"] == "Nenhuma"))
    m = int(fluxo.loc[sel, "quantidade"].sum())
    if not m or n > m:
        return None
    return {"n": n, "m": m, "pct": _pontos(n / m)}


# ---------- Estudo "Como medimos" (24/10/2026; revisto em 25/10/2026) ----------
# E1  Exemplo do dia: um orçamento real ENTREGUE NO MÊS VIGENTE (mês da 1ª entrega = mês da carga, o parcial), escolhido
#     de forma estável no dia: os candidatos são ordenados pelo hash de (data + grupo + projeto_id), com a data no fuso de
#     São Paulo (config.FUSO) — não pela ordem da lista. Entra quem já teve a 1ª entrega (C1, C4) até o dia de corte do
#     rodapé, com caminho limpo até ela: Entrada → Elaboração → Revisão (cada etapa contígua, C14; quem passou pelo
#     Retorno Marca, que não conta na C2, não é exemplo) e tempo da equipe entre 2 e 16 h (típico). Prefere quem tem
#     Revisão. Sem candidato no mês vigente (ex.: começo do mês), volta mês a mês até achar.
# E2  Linha do tempo: início de cada etapa, a 1ª versão ao cliente (C1) e o passo seguinte ao Aguardando Feedback — ou
#     "em aberto" até o fim do dia de corte do rodapé (véspera da carga em São Paulo, 23:59:59). As horas de cada etapa
#     são as de C2 e somam o tempo da equipe: os minutos de cada etapa são arredondados pelo maior resto, com alvo = o
#     total arredondado, para a soma escrita fechar.
# E3  "Trabalho da equipe" = C2 do exemplo, com os dias de trabalho (h ÷ 8, 1 casa) e se está dentro da meta de 2 dias
#     (h ≤ 16, D38). "Para o cliente receber" = dias corridos de C3, arredondados (meio para cima), escritos "dias
#     corridos" (não é a meta); "Espera do cliente" = dias corridos em Aguardando Feedback (até o passo seguinte, ou
#     até o fim do dia de corte se ainda em aberto), só ilustrativo (não conta).
ETAPAS = ("Entrada", "Elaboração", "Revisão")
EXEMPLO_H = (2, 16)  # E1


def _etapa(status: str) -> str | None:
    s = str(status).lower()
    if status == FILA:
        return "Entrada"
    if s.startswith(RETORNO_MARCA):
        return None  # C2 (D-SLA-2): espera da marca, não é etapa da equipe
    if s.startswith("em elabora"):
        return "Elaboração"
    if s.startswith("em revis"):
        return "Revisão"
    return None


def _arred(x: float) -> int:
    """Meio para cima (C8), para minutos e dias do exemplo."""
    return math.floor(x + 0.5)


def _fmt_min(minutos: int) -> str:
    return f"{minutos // 60}h{minutos % 60:02d}" if minutos >= 60 else f"{minutos} min"


def _duracao(us: int) -> str:
    return _fmt_min(_arred(us / 60_000_000))


def _minutos_etapas(us: list[int]) -> list[int]:
    """E2: minutos inteiros de cada etapa pelo maior resto, somando o total arredondado (as etapas fecham no total)."""
    exatos = [u / 60_000_000 for u in us]
    alvo = _arred(sum(exatos))
    base = [math.floor(x) for x in exatos]
    for i in sorted(range(len(us)), key=lambda i: -(exatos[i] - base[i]))[:max(alvo - sum(base), 0)]:
        base[i] += 1
    return base


def _dias(n: int) -> str:
    return "no mesmo dia" if n == 0 else ("1 dia" if n == 1 else f"{n} dias")


SEMANA = ("segunda", "terça", "quarta", "quinta", "sexta")


def _dias_uteis_txt(d: float) -> str:
    """C3c: "2,4 dias úteis", "1,6 dia útil" (singular abaixo de 2, como E3); menos de 0,05 = "no mesmo dia"."""
    if d == 0:
        return "no mesmo dia"
    return f"{_br1(d)} {'dia útil' if d < 2 else 'dias úteis'}"


def dias_uteis_cliente(mediana: float | None) -> dict | None:
    """C3c (D54): mediana dos dias úteis com fração, arredondada a 1 casa (meio para cima, C8), e o exemplo da semana.

    O exemplo parte de um pedido na segunda às 10h (abertura do expediente) e anda o valor arredondado em dias úteis:
    a parte inteira escolhe o dia; a fração × 8 h, contada de 10h com a pausa de 13h–14h, diz "de manhã" (até 13h)
    ou "à tarde". Acima de 4,9 dias (passaria da sexta), sem exemplo.
    """
    if mediana is None:
        return None
    d = math.floor(mediana * 10 + 0.5) / 10
    dia, h = int(d), round((d - int(d)) * HORAS_DIA, 6)
    exemplo = None
    if dia < len(SEMANA):
        periodo = "de manhã" if h < 3 else "à tarde"
        alvo = "na própria segunda" if dia == 0 else f"na {SEMANA[dia]}"
        exemplo = f"pedido na segunda às 10h, resposta {alvo} {periodo}"
    return {"valor": d, "exato": mediana, "txt": _dias_uteis_txt(d), "exemplo": exemplo}


def _dias_trabalho(h: float) -> str:
    """E3 (D38): horas da equipe em dias de trabalho de 8 h, 1 casa (meio para cima), "dia" abaixo de 2."""
    d = math.floor(h / HORAS_DIA * 10 + 0.5) / 10
    return f"{_br1(d)} {'dia' if d < 2 else 'dias'} de trabalho"


def _quando(t: pd.Timestamp) -> str:
    return t.strftime("%d/%m · %H:%M")


LINK_MONDAY = re.compile(r"https://[a-z0-9-]+\.monday\.com/boards/\d+/pulses/\d+")


def fora_da_curva(mov: pd.DataFrame, u: pd.DataFrame, fora_mask) -> list[dict]:
    """Caio, 03/11/2026: os pedidos fora da curva do estudo (acima do limite de Tukey, X6), do mais longo ao mais curto,
    para a lupa do slide 2: nome, marca e talento (movimentos), entrada (`inicio` da view; sem ela, a 1ª entrada nos
    movimentos), 1ª entrega e horas de trabalho, e o link do item no monday. Só junta colunas da gold (D57); o link só
    entra se for um endereço de item do monday (entrada externa tratada como não confiável)."""
    fora = u.loc[getattr(fora_mask, "values", fora_mask)]
    if fora.empty:
        return []
    m = mov.assign(projeto_id=mov["projeto_id"].astype(str))
    info = m.drop_duplicates("projeto_id").set_index("projeto_id")
    entrada = pd.to_datetime(m.groupby("projeto_id")["entrada"].min()) if "entrada" in m else pd.Series(dtype="datetime64[ns]")
    lista = []
    for r in fora.sort_values(["h_trabalho", "projeto_id"], ascending=[False, True]).itertuples(index=False):
        pid = str(r.projeto_id)
        i = info.loc[pid] if pid in info.index else None
        ini = getattr(r, "inicio", pd.NaT)
        ini = entrada.get(pid, pd.NaT) if pd.isna(ini) else ini
        link = str(i["link_projeto"]) if i is not None and "link_projeto" in i and pd.notna(i["link_projeto"]) else ""
        lista.append({
            "id": pid,
            "nome": (str(i["nome_projeto"]) if i is not None and pd.notna(i.get("nome_projeto")) else f"Projeto {pid}"),
            "marca": str(i["marca"]) if i is not None and pd.notna(i.get("marca")) else "",
            "talento": str(i["talento"]) if i is not None and pd.notna(i.get("talento")) else "",
            "entrada": _quando(pd.Timestamp(ini)) if pd.notna(ini) else "–",
            "entrega": _quando(pd.Timestamp(r.entregue_em)) if pd.notna(r.entregue_em) else "–",
            "horas": float(r.h_trabalho), "horas_txt": _h(float(r.h_trabalho)), "dias_txt": _dias_trabalho(float(r.h_trabalho)),
            "link": link if LINK_MONDAY.fullmatch(link) else "",
        })
    return lista


def _caminho(passos: pd.DataFrame, pronto: int):
    """Etapas antes da 1ª entrega, na ordem E2, ou None se o caminho não for limpo (E1)."""
    antes = passos.loc[passos["passo"] < pronto]
    if antes.empty or (antes["fase"] != "equipe").any() or antes["saida"].isna().any():
        return None
    nomes = [_etapa(s) for s in antes["status"]]
    if None in nomes or nomes[0] != "Entrada":
        return None
    ordem = [ETAPAS.index(n) for n in nomes]
    if ordem != sorted(ordem) or "Elaboração" not in nomes:
        return None
    return antes, nomes


def _hoje():
    """Dia de hoje em São Paulo (no Cloud Run o relógio é UTC; o exemplo do dia vira à meia-noite de Brasília)."""
    return datetime.now(config.FUSO).date()


def exemplo(mov: pd.DataFrame, mes_parcial: str, grupo: str = "todos", dia=None, fixo: str | None = None) -> dict | None:
    """E1–E3: o orçamento do dia (entregue no mês vigente), com a linha do tempo e os três números do estudo.

    E4 (batalha de agentes, 25/10/2026, B-N8): `fixo` = projeto_id revisado pelo Caio para a reunião (`?exemplo=` só em
    DEV ou MODO=apresentacao, nunca em produção). Vale só se o projeto é candidato pelas mesmas regras E1 (ano, até o
    mês vigente, 2 a 16 h, caminho limpo, grupo); senão, o sorteio do dia segue."""
    from app import sla

    dia = dia or _hoje()
    ano = mes_parcial[:4]
    corte = sla.data_corte(mov)
    agora = pd.Timestamp(datetime.combine(corte, time(23, 59, 59)))  # E2: fim do dia de corte do rodapé
    e = entregas(mov)
    e = e.loc[(e["mes"] >= f"{ano}-01") & (e["mes"] <= mes_parcial) & e["h_trabalho"].between(*EXEMPLO_H)
              & (e["entregue_em"] <= agora)]
    e = e.loc[GRUPOS[grupo][1](e)] if grupo in GRUPOS and grupo != "todos" else e
    linhas = e.set_index("projeto_id")  # C3b/C3c do exemplo vêm da mesma linha da view
    if fixo:
        escolhido = _exemplo_de(mov, e, str(fixo), agora)
        if escolhido is not None:
            return escolhido
    for mes in sorted(e["mes"].unique(), reverse=True):  # mês vigente primeiro; sem candidato, o anterior
        ids = sorted(e.loc[e["mes"] == mes, "projeto_id"].astype(str),
                     key=lambda pid: hashlib.sha256(f"{dia.isoformat()}:{grupo}:{pid}".encode()).hexdigest())
        por_projeto = mov.loc[mov["projeto_id"].astype(str).isin(set(ids))]
        por_projeto = {k: g.sort_values("passo") for k, g in por_projeto.groupby(por_projeto["projeto_id"].astype(str))}
        reserva = None
        for pid in ids:
            passos = por_projeto.get(pid)
            cliente = passos.loc[passos["fase"] == "cliente"] if passos is not None else None
            if cliente is None or cliente.empty:
                continue
            c1 = cliente.iloc[0]
            caminho = _caminho(passos, c1["passo"])
            if caminho is None:
                continue
            depois = passos.loc[passos["passo"] == c1["passo"] + 1]
            depois = depois.iloc[0] if len(depois) and depois.iloc[0]["entrada"] <= agora else None
            if "Revisão" in caminho[1]:
                return _montar_exemplo(passos, caminho, c1, depois, agora, linhas.loc[pid])
            reserva = reserva or (passos, caminho, c1, depois, agora, linhas.loc[pid])
        if reserva:
            return _montar_exemplo(*reserva)
    return None


def _exemplo_de(mov: pd.DataFrame, candidatos: pd.DataFrame, pid: str, agora) -> dict | None:
    """E4: o exemplo fixo, se o projeto está entre os candidatos E1 e tem caminho limpo."""
    if pid not in set(candidatos["projeto_id"].astype(str)):
        return None
    passos = mov.loc[mov["projeto_id"].astype(str) == pid].sort_values("passo")
    cliente = passos.loc[passos["fase"] == "cliente"]
    if cliente.empty:
        return None
    c1 = cliente.iloc[0]
    caminho = _caminho(passos, c1["passo"])
    if caminho is None:
        return None
    depois = passos.loc[passos["passo"] == c1["passo"] + 1]
    depois = depois.iloc[0] if len(depois) and depois.iloc[0]["entrada"] <= agora else None
    return _montar_exemplo(passos, caminho, c1, depois, agora, candidatos.set_index("projeto_id").loc[pid])


def _montar_exemplo(passos, caminho, c1, depois, agora, entrega: pd.Series) -> dict:
    """`entrega` = a linha do orçamento na view de entregas (dias úteis C3b/C3c). As horas de cada passo vêm da gold
    (`sla_sem_almoco_horas`, R24, sem arredondar), em microssegundos para as etapas somarem o total (E2)."""
    antes, nomes = caminho
    etapas = []
    for (_, p), nome in zip(antes.iterrows(), nomes):
        us = round(float(p["sla_sem_almoco_horas"]) * 3_600_000_000)
        if etapas and etapas[-1]["nome"] == nome:
            etapas[-1]["us"] += us
        else:
            etapas.append({"nome": nome, "inicio": p["entrada"], "us": us})
    total = sum(x["us"] for x in etapas)
    minutos = _minutos_etapas([x["us"] for x in etapas])  # E2: as etapas escritas somam o total escrito
    inicio = antes.iloc[0]["entrada"]
    dias_uteis = int(entrega["dias_uteis"])  # C3b (só no código)
    dias_fr = math.floor(float(entrega["dias_uteis_fr"]) * 10 + 0.5) / 10  # C3c
    aberto = depois is None  # E2: o cliente ainda não respondeu até o dia de corte
    fim = agora if aberto else depois["entrada"]
    dias_decisao = max(_arred((fim - c1["entrada"]).total_seconds() / 86400), 0)
    return {
        "nome": str(passos.iloc[0]["nome_projeto"]).strip().rstrip("-|").strip(),  # há nomes terminados em " -" no board
        "etapas": [{"nome": x["nome"], "tempo": _fmt_min(m), "minutos": m, "quando": _quando(x["inicio"]),
                    "h": x["us"] / 3_600_000_000}
                   for x, m in zip(etapas, minutos)],
        "pronto": _quando(c1["entrada"]),
        "fim": ({"quando": f"até {fim.strftime('%d/%m')}", "status": "em aberto"} if aberto
                else {"quando": _quando(fim), "status": depois["status"]}),
        "aberto": aberto,
        "h_trabalho": total / 3_600_000_000,
        "trabalho": _fmt_min(sum(minutos)),
        # E3 (D38): dias de trabalho (8 h) com 1 casa; singular abaixo de 2 ("1,5 dia"); meta pelo valor exato
        "dias_trabalho": _dias_trabalho(total / 3_600_000_000),
        "na_meta": total / 3_600_000_000 <= META_H,
        # batalha 2 (G1-N1/G2-1) e D54: a mesma unidade do número de apoio da página (C3c, dias úteis com fração)
        "dias_cliente": _dias_uteis_txt(dias_fr),
        "dias_uteis": dias_uteis,
        "de_ate": f"de {inicio.strftime('%d/%m')} a {c1['entrada'].strftime('%d/%m')}",
        "dias_decisao": _dias(dias_decisao),
    }


# ---------- Estudo "Como medimos", slide 2: exploração dos dados (refeito em 25/10/2026 pela referência do Caio) ----------
# Referência: imagens anotadas do Caio ("Página 06 · Leituras estatísticas"). Histograma fixo à esquerda; painel com
# três quadros à direita (assimetria, Q-Q, boxplot); cada quadro "acende" a marcação do histograma.
# X1  Universo: entregues dos meses completos de entrega do ano (C4, C7/A1), no grupo de talentos (C10, só pela URL);
#     h = tempo da equipe (C2). Cards de pacote ficam na base (só identificados, X6).
# X2  Histograma (Caio, 03/11/2026): faixas de 4 h — (0, 4], (4, 8], … — de 0 até o limite de Tukey do grupo (X6); se
#     o limite não é múltiplo de 4, a última faixa vai do último múltiplo até ele (mais estreita, rótulo próprio; resto
#     < 1 h entra na faixa anterior). Depois, uma barra só "acima de <limite>" (> limite), toda vermelha: o número dela é
#     o n_fora do cartão "Fora da curva". h = 0 entra na 1ª. Alturas = quantidade de orçamentos. Eixo x: 0, 8, 16, … h
#     e "acima de <limite>". Limite escrito com 1 casa quando não é inteiro (`_h_lim`: 69,7 h, não "70 h").
# X3  Faixas do topo (quadros 1 e 2): na meta, até 2 dias (≤ 16 h, C6/D38), de 2 a 5 dias (16–40 h) e mais de 5 dias
#     (> 40 h, C12), em % pelo maior resto (E8c); o 3º bloco leva o maior tempo do grupo ("até N h"). A faixa do pé do
#     quadro 1 diz se o típico (mediana exata) está dentro da meta ou quantas horas passa dela.
# X4  Assimetria (quadro 1): coeficiente de Fisher-Pearson ajustado (pandas `Series.skew()`), numa régua 0 (simétrico)
#     → 1 (cauda forte) → o nosso; acima de 3 a régua ganha uma quebra. > 0,5 = positiva (cauda à direita); −0,5 a 0,5 =
#     quase simétrica; < −0,5 = negativa. % abaixo da média = orçamentos com h < média (meio para cima).
# X5  Normalidade (quadro 2): Q-Q com 200 quantis (p = (k − 0,5)/200): tempo real (quantil linear) × tempo previsto
#     pela normal com a média e o desvio amostral. Em vermelho, os quantis acima do limite X6. Aderência r = correlação
#     de Pearson dos pontos; "segue a normal?" = sim se r ≥ 0,95 (só escolhe a frase). No histograma (D38): o MESMO
#     sino do meio da reta do Q-Q (normal com a mediana e IQR/1,349; "se fosse um sino em volta do típico"), em
#     n × 4 h × densidade. O KDE gaussiano (banda de Silverman 0,9 × min(desvio, IQR/1,34) × n^−0,2, mesma escala)
#     segue calculado, mas saiu da tela (D38, Caio). A faixa do pé liga o tracejado ao Q-Q (o mesmo sino).
# X6  Boxplot de Tukey (quadro 3), escala linear: Q1, mediana e Q3 (quantis lineares); limite estatístico (Tukey) =
#     Q3 + 1,5 × IQR — não é a meta. Zonas: rápidos (≤ Q1), comuns (Q1–Q3], demorados (Q3–limite: passam da meta,
#     mas seguem o padrão do processo), outliers (> limite), em % pelo maior resto. Marca fina da meta (16 h) na caixa,
#     se 16 h ≤ limite. Card de pacote = nome começa por "[Pacote" (só identificado). Faixa do pé: o típico contra a
#     meta, % em até 16 h, % de outliers e a parcela das horas que eles somam (`pct_horas_outliers`).
# X7  Comparação dos grupos (só cálculo e ficha): % acima do limite do grupo "Todos" e do próprio limite; % > 5 dias.
# X8  Influência dos outliers (só cálculo e ficha): mediana, média, % em até 2 dias (16 h, D38) e P90 com todos, sem os
#     outliers e sem os cards de pacote.
# X9  P50, P80 e P90 (quantis lineares) em horas: só cálculo e ficha. O quadro 4 (curva acumulada) saiu da tela a pedido
#     do Caio (25/10/2026); a curva acumulada vai para outra página.
BIN_H = 4  # X2: faixas de 4 h até o limite de Tukey + "acima de <limite>"
RESTO_MIN_H = 1.0  # X2: resto do limite (acima do último múltiplo de 4) menor que isso entra na faixa anterior
NORMAL_R = 0.95  # X5: aderência mínima para dizer que segue a curva
# X3: o corte de 2 dias do slide 2 é a própria META_H (16 h); a constante duplicada saiu em 26/10/2026 (G3-13)
QQ_K = 200  # X5: quantis do Q-Q
LETRA = 0.575  # largura média estimada de um caractere do IBM Plex, em fração do tamanho da letra (12 → 6,9)


def _br(x: float, casas: int = 1) -> str:
    return f"{x:.{casas}f}".replace(".", ",")


def _h(x: float) -> str:
    return f"{math.floor(x + 0.5)} h"


def _n_lim(x: float) -> str:
    """X2/X6 (Caio, 03/11/2026): horas do limite de Tukey e das bordas do histograma com 1 casa, sem ",0" (59,2; 56;
    69,7). O inteiro arredondado enganava: "acima de 70 h" para 69,7 h, com um pedido de 69,9 h na lista."""
    return _br(x).removesuffix(",0")


def _h_lim(x: float) -> str:
    return f"{_n_lim(x)} h"


def _larg(texto: str, fonte: float) -> float:
    return len(texto) * LETRA * fonte


def _universo_df(mov: pd.DataFrame, mes_parcial: str, grupo: str) -> pd.DataFrame:
    todos = entregas(mov)
    c = todos.loc[_completos(todos, mes_parcial)]  # C7 (A1)
    return c.loc[GRUPOS[grupo][1](c)]


def _universo(mov: pd.DataFrame, mes_parcial: str, grupo: str) -> pd.Series:
    return _universo_df(mov, mes_parcial, grupo)["h_trabalho"].astype(float)


def _boxplot(h: pd.Series) -> dict:
    """X6: quartis em horas e limite estatístico de Tukey (não é a meta), em escala linear (Q3 + 1,5 × IQR)."""
    q1, med, q3 = (float(h.quantile(q)) for q in (0.25, 0.5, 0.75))
    iqr = q3 - q1
    lim = q3 + 1.5 * iqr
    contagens = [int((h <= q1).sum()), int(((h > q1) & (h <= q3)).sum()), int(((h > q3) & (h <= lim)).sum()), int((h > lim).sum())]
    return {"q1": q1, "mediana": med, "q3": q3, "iqr": iqr, "limite": lim, "contagens": contagens, "pcts": _pcts(contagens)}


def _assimetria(g: float) -> dict:
    """X4: título e texto do quadro 1 pelo coeficiente de assimetria (D12: a frase segue o dado). G3-8 (batalha 2):
    linguagem simples na tela; o nome técnico (assimetria positiva/negativa) fica no leitor de tela e na ficha."""
    if g > 0.5:
        titulo = "Poucos casos muito longos puxam a conta"
        texto = ("A maioria sai rápido e poucos casos demoram muito, esticando o gráfico para a direita: é a "
                 "<strong>cauda</strong>.<span class=\"so-leitor\"> Assimetria positiva.</span>")
    elif g >= -0.5:
        titulo = "Os tempos se equilibram dos dois lados"
        texto = ("Os tempos se espalham quase igual dos dois lados do meio: <strong>quase sem cauda</strong>."
                 "<span class=\"so-leitor\"> Quase simétrica.</span>")
    else:
        titulo = "Poucos casos muito rápidos puxam a conta"
        texto = ("A maioria demora e poucos casos saem muito rápido, esticando o gráfico para a esquerda: é a "
                 "<strong>cauda</strong>.<span class=\"so-leitor\"> Assimetria negativa.</span>")
    return {"coef": g, "txt": ("+" if g >= 0 else "−") + _br(abs(g)), "titulo": titulo, "texto": texto, "positiva": g > 0.5}


def _regua(g: float) -> dict:
    """X4: régua 0 (simétrico) → 1 (cauda forte) → o nosso, num quadro de 230 × 50. Até 3 é linear; acima de 3, o
    trecho entre 1 e o nosso ganha uma quebra (//) no meio."""
    W, M = 230, 14
    quebra = g > 3
    if quebra:
        x = {0: M, 1: M + 0.36 * (W - 2 * M), "nosso": W - M}
        xq = (x[1] + x["nosso"]) / 2
    else:
        lo, hi = min(g, 0.0), max(g, 1.0)
        f = lambda v: M + (W - 2 * M) * (v - lo) / (hi - lo)
        x = {0: f(0), 1: f(1), "nosso": f(g)}
        xq = None
    marcas = [{"x": round(x[0], 1), "v": "0", "t": "simétrico", "nosso": False},
              {"x": round(x[1], 1), "v": "1", "t": "cauda forte", "nosso": False},
              {"x": round(x["nosso"], 1), "v": _br(g) if g >= 0 else "−" + _br(abs(g)), "t": "o nosso", "nosso": True}]
    for m in marcas:  # o texto centrado no ponto, sem sair do quadro
        meia = max(_larg(m["v"], 12), _larg(m["t"], 11)) / 2
        m["tx"] = round(min(max(m["x"], meia), W - meia), 1)
    return {"w": W, "h": 50, "x0": M, "x1": W - M, "marcas": marcas, "quebra": round(xq, 1) if xq else None}


def _pct_de(p: int, verbo_sing: str, verbo_pl: str) -> str:
    """"56% saem" (% de TODOS os orçamentos do recorte, D38: não "de cada 100", que soa como amostra de 100), com
    singular em 1% e "menos de 1%"."""
    if p == 0:
        return f"menos de 1% {verbo_sing}"
    return f"{p}% {verbo_sing if p == 1 else verbo_pl}"


def _orcamentos(n: int) -> str:
    return f"{formato.inteiro(n)} {'orçamento' if n == 1 else 'orçamentos'}"


def _pct(p: int) -> str:
    return "menos de 1%" if p == 0 else f"{p}%"


def _frases(h: pd.Series, bx: dict, n_fora: int, n_pac: int = 0) -> dict:
    """X6 (D38, versão final do Caio, 25/10/2026): faixa do pé do passo 3, curta, só com números do gráfico do passo:
    R + C = rápidos + comuns (`bx.pcts[0] + [1]`, "até Q3"), D = demorados (`pcts[2]`, até o limite estatístico),
    F = outliers (`pcts[3]`), Q3 e limite como escritos no boxplot; n_pac = cards "[Pacote" entre os outliers. Não diz
    que os R + C estão "na meta" (a meta é 16 h; Q3 passa dela). `nota` = o padrão em linguagem simples, numa linha
    abaixo da faixa (a regra Q3 + 1,5 × IQR fica na ficha e no aria-label). As horas que os outliers somam ficam no cálculo
    (`pct_horas_outliers`), fora da tela. Variantes: sem demorados, sem outliers, singular e "menos de 1%"."""
    r, c, d, f = bx["pcts"]
    rc = r + c
    q3, lim = _h(bx["q3"]), _h_lim(bx["limite"])
    horas = _pontos(float(h[h > bx["limite"]].sum() / h.sum())) if h.sum() else 0
    p = _pontos(float((h <= META_H).mean()))
    partes = [f"<strong>{_pct(rc)} dos orçamentos {'sai' if rc <= 1 else 'saem'} em até {q3}</strong>: os rápidos e os comuns."]
    if bx["contagens"][2]:
        um = d <= 1
        partes.append(f"{'Outro' if um else 'Outros'} {_pct(d)} {'demora' if um else 'demoram'} mais, até {lim}, mas "
                      f"{'segue' if um else 'seguem'} o padrão do processo")
    if not n_fora:
        txt = " ".join(partes) + ("; " if bx["contagens"][2] else " ") + "<em>neste recorte, ninguém fica fora da curva.</em>"
    else:
        um = n_fora == 1
        pac = ("" if not n_pac else ", um pacote" if um else
               f", {formato.inteiro(n_pac)} {'deles pacote' if n_pac == 1 else 'deles pacotes'}")
        if bx["contagens"][2]:
            partes[-1] += "."
        partes.append(f"<em>{_pct(f)} ({_orcamentos(n_fora)}{pac}) {'está' if um else 'estão'} fora da curva, acima de "
                      f"{lim}: vamos olhar caso a caso.</em>")  # G3-8: "fora da curva" no lugar de "outlier"
        txt = " ".join(partes)
    # D38 (Caio): linguagem simples; a regra técnica (Q3 + 1,5 × IQR) fica na ficha e no aria-label do boxplot
    nota = (f"Chamamos de padrão os tempos até {lim}: é até onde vai a grande maioria dos orçamentos, com uma margem de "
            "folga. Acima disso, o tempo foge do ritmo da equipe.")
    return {"fora_rodape": txt, "nota": nota, "pct_meta": p, "pct_horas_outliers": horas}


def _insight_p1(med: float, media: float, p: int, relevante: bool) -> str:
    """D38 (textos finais): faixa do pé do passo 1 — "Quanto tempo leva, de verdade?". P = % em até 16 h; típico =
    mediana exata contra 16 h (C6); média puxada por poucos casos longos (relevante = X4/D12) ou perto do típico."""
    t = meta_tipico(med)
    pp = "fica pronto" if p <= 1 else "ficam prontos"
    if t["na_meta"]:
        abre = (f"<strong>{_pct(p)} dos orçamentos {pp} em até 2 dias de trabalho</strong>, e o típico leva "
                f"{t['mediana_txt']}: dentro da meta.")
        media_txt = f"A média, {_h(media)}, parece pior porque poucos casos muito longos a puxam para cima;"
    else:
        abre = (f"Neste grupo, <strong>o típico leva {t['mediana_txt']}, {t['acima_txt']} acima da meta de 2 dias</strong>; "
                f"só {_pct(p)} {pp} no prazo.")
        media_txt = f"A média, {_h(media)}, ainda é puxada para cima por poucos casos muito longos;"
    if not relevante:
        return f"{abre} A média, {_h(media)}, fica perto dele: <em>aqui a média e o típico contam a mesma história</em>."
    return f"{abre} {media_txt} <em>por isso olhamos o típico</em>."


def _puxao(med: float, media: float) -> str:
    """X11 (V2, 30/10/2026): o "puxão" dos casos longos no "Como ler" do slide 2 = média escrita − típico escrito, a
    conta que o leitor faz com os dois números da tela (14 h e 25 h → "11 h"); com o típico de 1 casa (C6, perto de
    16 h), 1 casa."""
    tip = float(_h_meta(med).removesuffix(" h").replace(",", "."))
    d = max(_arred(media) - tip, 0.0)
    return (f"{int(d)} h" if d == int(d) else _br1(d) + " h")


def _insight_unico(med: float, media: float, bx: dict, n_fora: int, relevante: bool) -> str:
    """X10 (V2, 30/10/2026, Caio): slide 2 num passo só, para quem não é da área — uma frase: poucos pedidos demoram
    muito e puxam a média; o típico (mediana exata, C6) é a medida. F = % fora da curva (`bx.pcts[3]`), acima do limite
    estatístico escrito no gráfico; média relevante = X4/D12 (a mesma regra do rótulo da média). Variantes: média perto
    do típico; ninguém fora da curva; 1% no singular."""
    tip, med_txt, lim = _h_meta(med), _h(media), _h_lim(bx["limite"])
    if not relevante:
        return (f"A média ({med_txt}) fica perto do típico ({tip}): aqui as duas contam a mesma história. "
                "<em>Seguimos com o típico (a mediana)</em>, que não se deixa levar pelos casos longos.")
    if not n_fora:
        return (f"Os pedidos mais longos puxam a média para {med_txt}, mas <strong>o pedido típico leva {tip}</strong>. "
                "<em>Por isso medimos pelo típico (a mediana).</em>")
    f = bx["pcts"][3]
    os_ = "o" if f == 1 else "os"
    return (f"<strong>Poucos pedidos demoram muito:</strong> {os_} {_pct(f)} fora da curva, acima de {lim}, puxam a média "
            f"para {med_txt}. O pedido típico leva {tip}. <em>Por isso medimos pelo típico (a mediana).</em>")


def _insight_p2(h: pd.Series, sino: NormalDist, normal: bool) -> dict:
    """D38 (textos finais): faixa do pé do passo 2 — "Dá para prever pela média?". P90 real (quantil linear: onde
    começam os 10% mais lentos) contra o P90 do sino do meio (o "ritmo regular": o mesmo sino do tracejado e da reta do
    Q-Q). Real acima do sino (e não `normal`) = os demorados fogem do ritmo; senão, a variante "ritmo regular"."""
    p90 = float(h.quantile(0.9))
    s90 = max(sino.inv_cdf(0.9), 0.0)
    if normal or p90 <= s90:
        txt = ("Os tempos seguem um ritmo regular, sem casos que fujam muito do padrão; <em>a média e o típico contam a "
               "mesma história</em>.")
    else:
        # 25/10 (Caio): sem números que não estão no gráfico; cita os cortes marcados na reta (2 e 5 dias)
        txt = ("Até 2 dias, os orçamentos andam junto da reta, no ritmo previsto. <strong>Depois disso, os demorados se "
               "afastam dela</strong>, e quanto mais demoram, mais longe ficam. <em>Por isso a meta se apoia no típico, e "
               "os demorados são tratados à parte.</em>")
    return {"texto": txt, "p90": p90, "sino_p90": s90}


def _rotulo_livre(cx: float, texto: str, linhas: list[float], fonte: float, folga: float) -> tuple[float, str]:
    """R18: tira o número da barra de cima de uma linha vertical (mediana, média): se a distância entre a linha e o
    centro da barra for menor que meia largura do rótulo + 4, o rótulo anda para o lado oposto ao da linha, até `folga`
    (para não invadir o número da barra vizinha); o contorno branco do texto (CSS) cobre o que ainda encostar."""
    meia = len(texto) * 0.6 * fonte / 2
    for x in linhas:
        if abs(x - cx) < meia + 4:
            alvo = x + meia + 4 if cx >= x else x - meia - 4
            return round(min(max(alvo, cx - folga), cx + folga), 1), "middle"
    return cx, "middle"


def _influencia(h: pd.Series, fora: pd.Series, pacote: pd.Series | None) -> dict:
    """X8: o quanto os outliers mexem nos números (com todos × sem eles × sem os cards de pacote). Só ficha."""
    def _numeros(v: pd.Series) -> dict:
        v = v.astype(float)
        return {"n": len(v), "mediana": float(v.median()), "media": float(v.mean()), "p90": float(v.quantile(0.9)),
                "pct_2d": _pontos(float((v <= META_H).mean())),
                "mediana_txt": _h(float(v.median())), "media_txt": _h(float(v.mean())), "p90_txt": _h(float(v.quantile(0.9)))}

    fora = fora.astype(bool).values
    todos, sem = _numeros(h), _numeros(h[~fora])
    sem_pac = _numeros(h[~pacote.astype(bool).values]) if pacote is not None and bool(pacote.any()) else None
    return {"todos": todos, "sem_fora": sem, "sem_pacotes": sem_pac, "n_fora": int(fora.sum()),
            "d_mediana": sem["mediana"] - todos["mediana"], "d_media": sem["media"] - todos["media"]}


def kde_silverman(h: pd.Series, xs) -> tuple[list[float], float]:
    """X5: densidade suavizada (KDE gaussiano) nos pontos xs, com a banda de Silverman
    0,9 × min(desvio, IQR/1,34) × n^−0,2 (se o IQR for 0, vale o desvio)."""
    import numpy as np

    v = h.to_numpy(dtype=float)
    n = len(v)
    dp = float(np.std(v, ddof=1))
    iqr = float(np.quantile(v, 0.75) - np.quantile(v, 0.25))
    escala = min(dp, iqr / 1.34) if iqr > 0 else dp
    bw = 0.9 * escala * n ** -0.2
    if not bw > 0:
        return [0.0] * len(xs), 0.0
    z = (np.asarray(xs, dtype=float)[:, None] - v[None, :]) / bw
    dens = np.exp(-0.5 * z * z).sum(axis=1) / (n * bw * math.sqrt(2 * math.pi))
    return [float(d) for d in dens], bw


def _caixa(h: pd.Series, bx: dict) -> dict:
    """X6: boxplot de Tukey na escala LINEAR, num quadro de 300 × 96: haste do menor tempo até Q1, caixa Q1–Q3 com a
    mediana, haste até o limite (trava) e, depois da trava, a nuvem dos outliers (ilustração: os casos vão até o
    maior tempo, fora da escala). Em cima, as quatro zonas em % do total do recorte (D38); embaixo, Q1, Q3 e o limite em horas e o
    nome das zonas. Rótulos empurrados para não se encostarem."""
    W, L, XL = 300, 8, 232
    sx = lambda v: L + (XL - L) * min(max(v, 0.0), bx["limite"]) / bx["limite"]
    x_min, x_q1, x_med, x_q3, x_lim = (round(sx(v), 1) for v in (float(h.min()), bx["q1"], bx["mediana"], bx["q3"], bx["limite"]))
    tem_fora = bx["contagens"][3] > 0
    nuvem = []
    if tem_fora:  # nuvem determinística (sem sorteio): 9 pontos em 2 alturas, depois da trava
        for i in range(9):
            nuvem.append({"x": round(XL + 10 + i * 6.5, 1), "y": 48 + (-5 if i % 2 else 4) + (2 if i % 3 == 0 else 0)})
    centros = [(x_min + x_q1) / 2, (x_q1 + x_q3) / 2, (x_q3 + x_lim) / 2, XL + 36]
    nomes = ["rápidos", "comuns", "demorados", "outliers"]  # D38: "demorados" passam da meta, mas seguem o padrão
    rot = []
    fim = -1e9
    for c_, nome in zip(centros, nomes):
        w = _larg(nome, 11.5)
        ini = max(c_ - w / 2, fim + 6, 0)
        rot.append({"x0": ini, "w": w, "t": nome})
        fim = ini + w
    if fim > W:  # passou da borda: o último encosta nela e os anteriores abrem espaço
        rot[-1]["x0"] = W - rot[-1]["w"]
        for i in range(len(rot) - 2, -1, -1):
            rot[i]["x0"] = min(rot[i]["x0"], rot[i + 1]["x0"] - 6 - rot[i]["w"])
    nomes_rot = [{"x": round(r["x0"] + r["w"] / 2, 1), "t": r["t"]} for r in rot]
    numeros = [{"x": round(c_, 1), "t": f"{p}%"} for c_, p in zip(centros, bx["pcts"])]  # D38: % do total
    if not tem_fora:
        nomes_rot, numeros = nomes_rot[:3], numeros[:3]
    valores = [{"x": x_q1, "t": _h(bx["q1"])}, {"x": x_q3, "t": _h(bx["q3"])}, {"x": x_lim, "t": _h_lim(bx["limite"])}]
    for i in range(1, len(valores)):  # perto demais: o da direita anda
        a, b = valores[i - 1], valores[i]
        minimo = a["x"] + (_larg(a["t"], 11.5) + _larg(b["t"], 11.5)) / 2 + 6
        if b["x"] < minimo:
            b["x"] = round(minimo, 1)
    med_txt = f"típico {_h(bx['mediana'])}"  # G3-8
    # D38 (Caio): marca da meta (16 h) só se ela cabe na escala (16 h ≤ limite): linha tracejada fina com uma bolinha em
    # cada ponta, em dois trechos FORA da caixa (y 28–35 e 61–68), para não passar sobre a caixa, o "mediana N h" nem
    # os números; sem rótulo no desenho (<title> no SVG e nota pequena abaixo do boxplot)
    meta = {"x": round(sx(META_H), 1), "y_cima": (28, 35), "y_baixo": (61, 68)} if META_H <= bx["limite"] else None
    return {"w": W, "h": 80, "meta": meta, "x_min": x_min, "x_q1": x_q1, "x_med": x_med, "x_q3": x_q3, "x_lim": x_lim, "nuvem": nuvem,
            "numeros": numeros, "nomes": nomes_rot, "valores": valores, "med_txt": med_txt,
            "med_cabe": x_q3 - x_q1 > _larg(med_txt, 11) + 12,
            "zonas": [{"t": n, "pct": p} for n, p in zip(nomes, bx["pcts"])]}


def _qq(teo: list[float], obs: list[float], lim: float, h: pd.Series | None = None, p90: dict | None = None) -> dict:
    """X5 (v5, 25/10/2026, Caio): Q-Q contra o SINO DO MEIO — normal com a mediana e a largura da caixa (IQR / 1,349),
    a reta de referência padrão (qqline do R). O sino da média e do desvio era inflado pela própria cauda (desvio 53 h) e
    "esperava" tempos longos, jogando os demorados para baixo da reta. Aqui o meio cai na reta e a cauda sobe acima dela.
    x = o que o sino previa (0 h até o maior previsto), y = tempo real (0 h até ~10% acima do P97; acima disso, preso no
    topo com "↑"); escalas próprias, a reta é real = previsto, com os valores em horas escritos nela (`rotulos`).
    Cores pelo critério do passo 3: vermelho acima do limite de Tukey (outliers), azul no resto. Quantis vizinhos
    da mesma cor a < 6 px viram uma bolinha de área proporcional; os de previsão < 0 h ficam numa bolinha em 0 h."""
    W, H, L, R, T, B = 340, 88, 34, 10, 12, 14  # D38: 104 → 88 (o painel do passo 2 passava do limite de altura)
    obs_ord = sorted(obs)
    hx = max(max(teo), 1.0) * 1.06
    hy = max(obs_ord[int(0.97 * (len(obs_ord) - 1))] * 1.1, hx)
    sx = lambda v: L + (W - L - R) * min(max(v, 0.0), hx) / hx
    sy = lambda v: H - B - (H - B - T) * min(max(v, 0.0), hy) / hy
    passo_y = next(p for p in (10, 20, 25, 50, 100, 200) if hy / p <= 4)
    marcas = [{"v": f"{v} h", "y": round(sy(v), 1)} for v in range(0, int(hy) + 1, passo_y)]
    # 25/10 (Caio): na reta, os mesmos cortes das faixas do histograma (2 dias e 5 dias de trabalho), não horas soltas
    rotulos = [{"v": t, "x": round(sx(v), 1), "y": round(sy(v), 1)}
               for v, t in ((META_H, "2 dias"), (CAUDA_H, "5 dias")) if v <= hx]
    reta = {"x1": round(sx(0), 1), "y1": round(sy(0), 1), "x2": round(sx(hx), 1), "y2": round(sy(hx), 1)}
    grupos: list[list] = []
    for t, o in zip(teo, obs):
        x, y, f = sx(t), sy(o), ("fora" if o > lim else "perto")
        g = grupos[-1] if grupos else None
        if g and g[0]["f"] == f and ((t < 0 and g[0]["neg"]) or (not g[0]["neg"] and t >= 0 and math.hypot(x - g[0]["x"], y - g[0]["y"]) < 6)):
            g.append({"x": x, "y": y, "f": f, "neg": t < 0, "o": o})
        else:
            grupos.append([{"x": x, "y": y, "f": f, "neg": t < 0, "o": o}])
    pontos = [{"x": round(sum(q["x"] for q in g) / len(g), 1), "y": round(sum(q["y"] for q in g) / len(g), 1),
               "r": round(1.7 * math.sqrt(len(g)), 1), "n": len(g), "faixa": g[0]["f"], "neg": g[0]["neg"],
               "fora": g[0]["f"] == "fora", "preso": g[-1]["o"] > hy} for g in grupos]
    n_neg = sum(1 for t in teo if t < 0)
    return {"w": W, "h": H, "e": L, "base": H - B, "topo": T, "dir": W - R, "reta": reta, "pontos": pontos, "marcas": marcas,
            "rotulos": rotulos, "n_neg": n_neg, "pct_neg": _pontos(n_neg / len(teo)) if teo else 0, "lim_txt": _h(lim),
            "n_fora": sum(p["n"] for p in pontos if p["fora"]),
            # D38 (Caio): acima do teto do gráfico, ORÇAMENTOS reais (não quantis de 200, que davam sempre ~6 = 3% de 200)
            "n_presos": int((h > hy).sum()) if h is not None else sum(1 for o in obs if o > hy), "teto": hy, "teto_txt": _h(hy),
            "p90": None}  # 25/10 (Caio): marca dos 10% mais lentos retirada da tela (`_marca_p90` fica no código)


def _marca_p90(p90: dict, sx, sy, hy: float, direita: float, topo: float) -> dict | None:
    """D38 (Caio): os números da faixa do passo 2 aparecem no Q-Q — anel discreto no ponto dos 10% mais lentos (x = o
    que o sino previa, y = o real) e um rótulo curto "10% mais lentos: R · sino: S" à esquerda e acima dele (preso ao
    quadro). Some se o real passar do teto do gráfico."""
    if p90["p90"] > hy:
        return None
    x, y = sx(p90["sino_p90"]), sy(p90["p90"])
    t = f"10% mais lentos: {_h(p90['p90'])} · sino: {_h(p90['sino_p90'])}"
    w = _larg(t, 8.5)
    tx = max(x - 6, w + 2)
    return {"x": round(x, 1), "y": round(y, 1), "tx": round(min(tx, direita), 1), "ty": round(max(y - 6, topo + 8), 1), "t": t}


def _espelho(h: pd.Series) -> dict:
    """X5b (25/10/2026, Caio: "uma forma que faça sentido, fácil visual"): teste de sino pelo espelho. Num sino, os dois
    lados do meio são iguais: do orçamento do meio (mediana) até o limite dos N mais rápidos de cada 100 é a mesma
    distância que até o limite dos N mais lentos. Para N = 25, 10, 5 e 1, braço esquerdo = P50 − P(N), braço direito =
    P(100−N) − P50. O pedaço do braço direito que passa do espelho do esquerdo fica em vermelho (`excesso`). Escala
    linear até `teto` horas a partir do meio; braço maior que isso é cortado com o valor escrito."""
    W, L, R, T, LIN = 340, 112, 40, 24, 25  # quadro, coluna dos rótulos, folga à direita, topo, altura de cada linha
    med = float(h.median())
    pares = [(n, med - float(h.quantile(n / 100)), float(h.quantile(1 - n / 100)) - med) for n in (25, 10, 5, 1)]
    esq_max = max(e for _, e, _ in pares)
    teto = max(4 * esq_max, 10.0)  # o lado direito mostra até 4× o maior braço esquerdo
    esc = (W - L - R) / (esq_max + teto)
    cx = L + esq_max * esc
    linhas = []
    for i, (n, e, d) in enumerate(pares):
        y = T + i * LIN
        dv = min(d, teto)
        linhas.append({"n": n, "y": y, "x_esq": round(cx - e * esc, 1), "w_esq": round(e * esc, 1),
                       "w_espelho": round(min(e, dv) * esc, 1), "x_exc": round(cx + min(e, dv) * esc, 1),
                       "w_exc": round(max(dv - e, 0) * esc, 1), "x_fim": round(cx + max(dv, e) * esc, 1),
                       "x_ghost": round(cx + e * esc, 1), "cortado": d > teto,
                       "esq_txt": _h(e), "dir_txt": _h(d), "vezes": formato.decimal(d / e, 1) if e > 0 else "—"})
    return {"w": W, "h": T + len(pares) * LIN - 6, "cx": round(cx, 1), "rot": L - 30, "linhas": linhas,
            "med_txt": _h_meta(med), "topo": T - 13, "fim_y": T + len(pares) * LIN - 6}


def exploracao(mov: pd.DataFrame, mes_parcial: str, grupo: str = "todos") -> dict | None:
    """X1–X9: histograma e os três quadros (assimetria, Q-Q, boxplot), com a geometria dos SVG; P50/P80/P90 só ficha."""
    u = _universo_df(mov, mes_parcial, grupo)
    h = u["h_trabalho"].astype(float)
    n = len(h)
    if n < 30:
        return None
    media, dp, med = float(h.mean()), float(h.std()), float(h.median())
    bx = _boxplot(h)
    if not dp > 0 or not bx["limite"] > 0:  # D10: sem variação não há forma a descrever (evita divisão por zero)
        return None
    g = float(h.skew())
    a = _assimetria(g)
    fora_mask = h > bx["limite"]
    n_fora = int(fora_mask.sum())
    pac_fora = int(u.loc[fora_mask.values, "pacote"].sum()) if "pacote" in u else 0
    nd = NormalDist(media, dp)
    sino_meio = NormalDist(bx["mediana"], bx["iqr"] / 1.349) if bx["iqr"] > 0 else nd  # X5 v5: o sino do meio (Q-Q e curva)
    p50, p80, p90 = (float(h.quantile(q)) for q in (0.5, 0.8, 0.9))
    hmax = float(h.max())

    # X2 histograma; quadro de W × H (y para baixo). Escala ~1 em 1280 px (R09: texto ≥ 11 px reais)
    W, H, E, D = 580, 312, 28, 2  # 25/10: +20 da legenda retirada (Caio), o painel ao lado mantém a altura
    YF, HF = 0, 22  # faixa do topo
    T, base = 64, H - 20  # topo da barra mais alta; linha de base
    lim = bx["limite"]
    lim_txt = _h_lim(lim)
    # X2 (Caio, 03/11/2026): faixas de 4 h de 0 até o limite de Tukey; a última pode ser mais estreita (do último
    # múltiplo de 4 até o limite) e, depois, uma barra só "acima de <limite>", toda vermelha, com o n_fora do cartão.
    # Nenhuma barra de duas cores (antes, faixas fixas até 60 h com a parte acima do limite pintada à parte)
    bordas = [float(v) for v in range(0, int(lim // BIN_H) * BIN_H + 1, BIN_H)]
    if len(bordas) == 1 or lim - bordas[-1] >= RESTO_MIN_H:
        bordas.append(lim)
    else:  # resto pequeno (ou limite múltiplo de 4): a faixa anterior vai até o limite, para não virar um fio
        bordas[-1] = lim
    trechos = list(pairwise(bordas))
    cont = [int(((h > lo) & (h <= hi)).sum()) for lo, hi in trechos]
    cont[0] += int((h <= 0).sum())
    cont.append(n_fora)
    larg = (W - E - D) / (lim / BIN_H + 1)  # px por 4 h; a barra "acima de" tem a largura de uma faixa cheia
    x_h = lambda hr: E + min(max(hr, 0.0), lim) / BIN_H * larg  # horas → x; acima do limite, o começo da última
    fim = W - D
    xs = [(x_h(lo), x_h(hi)) for lo, hi in trechos] + [(x_h(lim), fim)]
    topo = max(cont)
    passo_y = 100 if topo > 300 else (50 if topo > 120 else 20)
    y = lambda v: base - (base - T) * v / topo
    x_med = round(x_h(med), 1)
    x_media = round(E + min(max(media, 0.0), lim + BIN_H / 2) / BIN_H * larg, 1)  # acima do limite: meio da última
    y_lin1 = YF + HF + 18  # 1ª linha dos rótulos do alto (alfinetes)

    def zona_c3(hi):  # X3
        return "rapido" if hi <= META_H else ("medio" if hi <= CAUDA_H else "lento")

    def zona_box(centro):  # X6 (só faixas até o limite: o centro nunca passa dele)
        return "box-rapido" if centro <= bx["q1"] else "box-comum" if centro <= bx["q3"] else "box-demorado"

    barras = []
    for i, (c, (x0, x1)) in enumerate(zip(cont, xs)):
        cx = round((x0 + x1) / 2, 1)
        tx, ancora = _rotulo_livre(cx, str(c), [x_med, x_media], 11.5, folga=max((x1 - x0 - len(str(c)) * 6.9) / 2, 0) + 3)
        if i == len(trechos):  # a última: toda fora da curva
            zona, zbox, rotulo = zona_c3(math.inf), "box-fora", f"acima de {lim_txt}"
        else:
            lo, hi = trechos[i]
            zona, zbox, rotulo = zona_c3(hi), zona_box((lo + hi) / 2), f"{_n_lim(lo)} a {_n_lim(hi)} h"
        barras.append({"x": round(x0 + 1.5, 1), "w": round(max(x1 - x0 - 3, 1.0), 1), "y": round(y(c), 1),
                       "h": round(base - y(c), 1), "n": c, "cx": cx, "tx": tx, "ancora": ancora,
                       "zona": zona, "zona_box": zbox, "rotulo": rotulo})
    # eixo x: 0, 8, 16, … h e "acima de <limite>" encostado na borda direita; a marca que encostaria nele sai
    t_ult = f"acima de {lim_txt}"
    ini_ult = fim - _larg(t_ult, 11.5) * 0.92
    marcas_x = [{"x": round(x_h(v), 1), "t": f"{v} h"} for v in range(0, int(lim) + 1, 2 * BIN_H)
                if v == 0 or x_h(v) + _larg(f"{v} h", 11.5) / 2 + 6 < ini_ult]
    marcas_x.append({"x": round(fim, 1), "t": t_ult})
    grade = [{"y": round(y(v), 1), "t": str(v)} for v in range(0, topo + 1, passo_y) if v <= 0.62 * topo]

    # X3 faixas do topo (só cálculo) e X6 zonas do boxplot (na tela), como trechos do eixo x. O texto encolhe
    # (opções da mais longa à mais curta) até caber na largura do bloco; no mínimo, só o %
    c3 = [int((h <= META_H).sum()), int(((h > META_H) & (h <= CAUDA_H)).sum()), int((h > CAUDA_H).sum())]
    p3 = _pcts(c3)
    q1t, q3t = _h(bx["q1"]).removesuffix(" h"), _h(bx["q3"])
    faixas = [
        {"x0": E, "x1": x_h(META_H), "zona": "rapido", "pct": p3[0],
         "opcoes": ["prontos em até 2 dias (16 h)", "prontos em até 2 dias", "até 2 dias"]},  # D38; G3-8: o pedido não "está na meta"
        {"x0": x_h(META_H), "x1": x_h(CAUDA_H), "zona": "medio", "pct": p3[1], "opcoes": ["de 2 a 5 dias", "2 a 5 dias"]},
        {"x0": x_h(CAUDA_H), "x1": fim, "zona": "lento", "pct": p3[2], "opcoes": [f"mais de 5 dias, até {_h(hmax)}", "mais de 5 dias"]},
    ]
    zonas = [
        {"x0": E, "x1": x_h(bx["q1"]), "zona": "box-rapido", "pct": bx["pcts"][0], "opcoes": [f"rápidos: até {_h(bx['q1'])}", "rápidos"]},
        {"x0": x_h(bx["q1"]), "x1": x_h(bx["q3"]), "zona": "box-comum", "pct": bx["pcts"][1], "opcoes": [f"comuns: de {q1t} a {q3t}", "comuns"]},
        {"x0": x_h(bx["q3"]), "x1": x_h(lim), "zona": "box-demorado", "pct": bx["pcts"][2],
         "opcoes": [f"demorados, no padrão: até {lim_txt}", f"demorados: até {lim_txt}", "demorados"]},  # D38
        {"x0": x_h(lim), "x1": fim, "zona": "box-fora", "pct": bx["pcts"][3], "opcoes": ["fora da curva"]},  # = a última barra
    ]
    for f in faixas + zonas:
        f["x0"], f["x1"] = round(f["x0"] + 1, 1), round(f["x1"] - 1, 1)
        f["w"] = round(f["x1"] - f["x0"], 1)
        # largura estimada (medida no navegador): % em 600 a 11,5 (0,55 por letra) e o texto a 10,8 (0,5 por letra)
        base_pct = len(f"{f['pct']}%") * 0.55 * 11.5 + 12
        f["txt"] = next((t for t in f["opcoes"] if base_pct + len(t) * 0.5 * 10.8 <= f["w"]), "")
        f["mostra_pct"] = base_pct <= f["w"] + 2
    zonas = [z for z in zonas if z["w"] > 0]
    guias_box = [round(x_h(v), 1) for v in (bx["q1"], bx["q3"], lim)]

    media_relevante = _arred(media) > _arred(med) * 1.1 and _arred(media) - _arred(med) >= 2  # D12: "e não X h"
    _, banda = kde_silverman(h, [0.0])  # X5: a banda segue no cálculo e na ficha (a curva saiu da tela, D38)

    # típico e média discretos ("típico · 14 h"), alfinetes do alto até logo acima da barra
    def _alfinete(xl, texto, yl):
        i = next((k for k, (_, x1) in enumerate(xs) if xl <= x1), len(xs) - 1)
        w = _larg(texto, 11.5)
        anc, tx = ("start", xl + 5) if xl + 5 + w <= W - D else ("end", xl - 5)
        return {"x": round(xl, 1), "tx": round(tx, 1), "ancora": anc, "ty": round(yl, 1), "y1": round(yl + 4, 1),
                "y2": round(max(y(cont[i]) - 20, yl + 10), 1), "t": texto}

    alf_med = _alfinete(x_med, f"típico · {_h_meta(med)}", y_lin1)  # G3-8: "típico" na tela
    alf_media = _alfinete(x_media, f"média · {_h(media)}", y_lin1 + 18)

    # X5 Q-Q contra a normal
    ps = [(k - 0.5) / QQ_K for k in range(1, QQ_K + 1)]
    teo = [nd.inv_cdf(p) for p in ps]
    obs = [float(v) for v in h.quantile(ps).values]
    r_normal = correlation(teo, obs) if len(set(obs)) > 1 else 0.0
    normal = r_normal >= NORMAL_R

    # X7 comparação dos grupos (só ficha)
    lim_todos = _boxplot(_universo(mov, mes_parcial, "todos"))["limite"] if grupo != "todos" else bx["limite"]
    comparacao = []
    for k, (rot, _) in GRUPOS.items():
        ug = _universo_df(mov, mes_parcial, k)
        gg = ug["h_trabalho"].astype(float)
        if len(gg) < 30:
            continue
        bg = _boxplot(gg)
        comparacao.append({"chave": k, "rotulo": rot, "n": len(gg), "atual": k == grupo,
                           "pct_regua_todos": _pcts([int((gg <= lim_todos).sum()), int((gg > lim_todos).sum())])[1],
                           "pct_propria": bg["pcts"][3], "limite_proprio": _h(bg["limite"]),
                           "pct_5dias": _pontos((gg > CAUDA_H).mean()), "fora": int((gg > bg["limite"]).sum()),
                           "mediana": _h_meta(bg["mediana"]), "media": _h(float(gg.mean())), "assimetria": _br(float(gg.skew()))})

    fora_pct = bx["pcts"][3]
    q3r, iqrr = round(bx["q3"], 1), round(bx["iqr"], 1)
    return {
        # D38: o recorte por extenso ("de jan a set"; só janeiro: "em jan"), para os % do total
        "periodo": (f"em {formato.MESES[0]}" if int(mes_parcial[5:]) == 2
                    else f"de {formato.MESES[0]} a {formato.MESES[int(mes_parcial[5:]) - 2]}"),
        "grupo": grupo, "n": n, "media": media, "mediana": med, "desvio": dp, "maximo": hmax,
        "media_txt": _h(media), "mediana_txt": _h_meta(med), "max_txt": _h(hmax),
        "assimetria": g, "assim": a, "regua": _regua(g), "abaixo_media": _pontos((h < media).mean()),
        "media_relevante": media_relevante, "puxao_txt": _puxao(med, media), "normal": normal, "r_normal": r_normal, "r_normal_txt": _br(r_normal, 2),
        "faixas3": {"contagens": c3, "pcts": p3},
        "n_fora": n_fora, "pacotes_fora": pac_fora, "frases": (fr := _frases(h, bx, n_fora, pac_fora)),
        "fora_lista": fora_da_curva(mov, u, fora_mask),  # Caio, 03/11/2026: lupa do slide 2
        # D38: um insight por passo (regras, sem LLM), em % do total
        "insights": {"1": _insight_p1(med, media, _pontos(float((h <= META_H).mean())), media_relevante),
                     "2": (i2 := _insight_p2(h, sino_meio, normal))["texto"], "3": fr["fora_rodape"]},
        # X10 (V2, 30/10/2026): o slide 2 num passo só (os três insights acima seguem calculados, fora da tela)
        "insight": _insight_unico(med, media, bx, n_fora, media_relevante),
        "p90_sino": i2["sino_p90"],
        "pct_horas_outliers": fr["pct_horas_outliers"], "pct_meta": fr["pct_meta"], "tipico": meta_tipico(med),
        "box": {**bx, "q1_txt": _h(bx["q1"]), "q3_txt": _h(bx["q3"]), "med_txt": _h_meta(bx["mediana"]), "lim_txt": _h_lim(bx["limite"]),
                # D09: a conta escrita fecha com os termos mostrados (1 casa)
                "conta": f"{_br(q3r)} + 1,5 × {_br(iqrr)} = {_br(q3r + 1.5 * iqrr)} h",
                "dentro": 100 - fora_pct, "fora": fora_pct},
        "p50": p50, "p80": p80, "p90": p90, "p50_txt": _h(p50), "p80_txt": _h(p80), "p90_txt": _h(p90),
        "kde_banda": banda,
        "hist": {"w": W, "h": H, "e": E, "dir": W - D, "base": base, "topo": T, "barras": barras, "marcas_x": marcas_x,
                 "grade": grade, "x_med": x_med, "x_media": x_media, "alf_med": alf_med, "alf_media": alf_media,
                 "faixas": faixas, "zonas": zonas, "guias_box": guias_box, "y_faixa": YF, "h_faixa": HF,
                 "fim": round(fim, 1),
                 "texto": "; ".join(f"{b['rotulo']}: {b['n']}" for b in barras)},
        "qq": _qq([sino_meio.inv_cdf(p) for p in ps], obs, bx["limite"], h, i2), "espelho": _espelho(h), "caixa": _caixa(h, bx),
        "influencia": _influencia(h, fora_mask, u.get("pacote")),
        "comparacao": comparacao, "regua_todos": _h(lim_todos),
    }


# ---------- Estudo "Como medimos", slide 3: "De cada 100 pedidos que chegam, em quanto tempo entregamos?" (D39) ----------
# Referência: imagem do Caio (25/10/2026). Waffle de 100 quadrados por faixa de tempo da equipe, chaves "em até 2 dias" e
# "passam de 2 dias" e a curva acumulada com os marcos de 2 dias, 80% e 90%.
# W1  Universo: o mesmo do slide 2 (X1): entregues dos meses completos de entrega (C7), no grupo de talentos (C10, pela
#     URL `?talentos=`); h = tempo da equipe (C2). Menos de 30 orçamentos: sem o slide (mensagem de poucos dados).
# W2  Cinco faixas (C12, FAIXAS_CAUDA): ≤ 8 h (até 1 dia; h = 0 entra aqui), 8–16, 16–24, 24–40 e > 40 h. Os 100
#     quadrados são a PROPORÇÃO de todos os orçamentos do recorte (1 quadrado = 1%), não um sorteio.
# W3  Arredondamento (coerência com a página do SLA e o slide 2): "até 1 dia" e o total "até 2 dias" (A) arredondados
#     direto (C8, meio para cima); "1 a 2 dias" = A − até 1 dia; as três faixas de cima repartem B = 100 − A pelo maior
#     resto (E8c), como em `leituras()`. Assim os 100 fecham e A = "% em até 2 dias" da página e do slide 2. O maior resto
#     puro das cinco faixas fica no retorno (`maior_resto`) e `ajustado` diz se ele dava outro A (na carga de 23/10, não).
# W4  Waffle: quadrados preenchidos linha a linha (10 × 10), da faixa mais rápida para a mais lenta.
# W5  Curva acumulada: % de orçamentos prontos (ECDF: h ≤ x) em 121 pontos de 0 até o teto do eixo = P97 (quantil
#     linear) arredondado para cima ao múltiplo de 8 h (1 dia), no mínimo 24 h; acima do teto a curva não é desenhada
#     (os ~3% mais lentos ficam no texto do fim do eixo: "N% até T h").
# W6  Marcos da curva: (a) 2 dias = 16 h (META_H) com o % = A (W3); (b) e (c) os prazos dos 80% e 90% = quantis lineares
#     0,8 e 0,9 das horas, escritos em dias de trabalho de 8 h arredondados a meio dia ("3 dias e meio", "5 dias"), com
#     as horas (inteiras, meio para cima) embaixo. Rótulos que se encostariam andam para o lado.
# W7  Faixa do pé (redação do Caio): "Em uma amostra aleatória de 100 pedidos, A ficam prontos em até 2 dias de trabalho
#     e B levam mais de 2 dias." Os 100 são a proporção do total (W2) = a composição esperada de uma amostra aleatória de
#     100. Variantes: 1 (singular) e 0 ("nenhum"). Gancho: "E quanto do tempo
#     esses B pedidos consomem? →" (B = 1: "esse pedido consome"; B = 0: "E quanto do tempo cada faixa consome? →").
CEM_MIN = 30  # W1


def _dias_meio(h: float) -> str:
    """W6: horas → dias de trabalho de 8 h, arredondados a meio dia (meio para cima): "meio dia", "1 dia e meio",
    "3 dias e meio", "5 dias"."""
    d = math.floor(h / HORAS_DIA * 2 + 0.5) / 2
    inteiro, meio = int(d), d % 1 == 0.5
    if inteiro == 0:
        return "meio dia" if meio else "menos de meio dia"
    nome = "1 dia" if inteiro == 1 else f"{inteiro} dias"
    return nome + (" e meio" if meio else "")


def recorte(mov: pd.DataFrame, mes_parcial: str, grupo: str = "todos") -> dict | None:
    """R1 (batalha de agentes, 25/10/2026, B-ambiente-2): o recorte dos slides 2–8, escrito no topo de cada um —
    meses completos de entrega (C7), N do universo (`_universo_df`, o mesmo de todos os % do estudo) e o grupo do
    seletor (C10). `proximo` = o mês parcial por extenso ("outubro"), que entra quando fechar (slide 8)."""
    if int(mes_parcial[5:]) < 2:
        return None
    n = len(_universo_df(mov, mes_parcial, grupo))
    ano, fim = mes_parcial[:4], int(mes_parcial[5:]) - 1
    periodo = f"{formato.MESES[0]} de {ano}" if fim == 1 else f"{formato.MESES[0]} a {formato.MESES[fim - 1]} de {ano}"
    rotulo = GRUPOS[grupo][0] if grupo in GRUPOS else GRUPOS["todos"][0]
    pedidos = "orçamento medido" if n == 1 else "orçamentos medidos"  # G3-8: glossário (pedido entra; orçamento é entregue)
    return {"periodo": periodo, "n": n, "grupo": rotulo, "proximo": formato.MESES_EXTENSO[fim],
            "texto": f"{periodo} · {formato.inteiro(n)} {pedidos} · {rotulo}"}


def _periodo(mes_parcial: str) -> str:
    """D38: o recorte por extenso ("de jan a set"; só janeiro: "em jan")."""
    return (f"em {formato.MESES[0]}" if int(mes_parcial[5:]) == 2
            else f"de {formato.MESES[0]} a {formato.MESES[int(mes_parcial[5:]) - 2]}")


def _afasta(itens: list[dict], chave: str, larg: str, minimo: float, maximo: float, folga: float = 6) -> None:
    """W6: posições 1D de rótulos (centro em `chave`, largura em `larg`) sem se encostarem. Rótulos que se encostariam
    formam um bloco centrado na média das posições originais (cada um anda o mínimo, para os dois lados); o bloco fica
    dentro de [minimo, maximo]."""
    blocos: list[dict] = []
    for r in sorted(itens, key=lambda r: r[chave]):
        blocos.append({"itens": [r], "alvo": [r[chave]]})
        while True:
            for b in blocos[-2:]:  # posição do bloco: centro na média dos alvos, preso às bordas
                tam = sum(i[larg] for i in b["itens"]) + folga * (len(b["itens"]) - 1)
                ini = sum(b["alvo"]) / len(b["alvo"]) - tam / 2
                b["ini"], b["tam"] = min(max(ini, minimo), maximo - tam), tam
            if len(blocos) > 1 and blocos[-2]["ini"] + blocos[-2]["tam"] + folga > blocos[-1]["ini"]:
                u = blocos.pop()
                blocos[-1]["itens"] += u["itens"]
                blocos[-1]["alvo"] += u["alvo"]
                continue
            break
    for b in blocos:
        x = b["ini"]
        for i in b["itens"]:
            i[chave] = round(x + i[larg] / 2, 1)
            x += i[larg] + folga


def _cem_textos(a: int, b: int) -> dict:
    """W7: faixa do pé (redação do Caio) e gancho."""
    if a == 0:
        pa = "<strong>nenhum fica pronto em até 2 dias</strong> de trabalho"
    else:
        verbo = "fica pronto" if a == 1 else "ficam prontos"
        pa = f"<strong>{a} {verbo} em até 2 dias</strong> de trabalho"
    if b == 0:
        pb = "<strong>nenhum leva mais de 2 dias</strong>"
    else:
        verbo = "leva" if b == 1 else "levam"
        pb = f"<strong>{b} {verbo} mais de 2 dias</strong>"
    rodape = f"Em uma amostra aleatória de 100 pedidos, {pa} e {pb}."
    if b == 0:
        gancho = "E quanto do tempo cada faixa consome?"
    elif b == 1:
        gancho = "E quanto do tempo esse pedido consome?"
    else:
        gancho = f"E quanto do tempo esses {b} pedidos consomem?"
    return {"rodape": rodape, "gancho": gancho}


def _cem_pcts(h: pd.Series) -> tuple[list[int], list[int], list[int]]:
    """W2–W3: contagens das cinco faixas, % na tela (A pela C8; as três de cima repartem B pelo maior resto) e o maior
    resto puro. Fonte única dos % de pedidos dos slides 3 e 4 (V2)."""
    n = len(h)
    contagens = [int(((h > a) & (h <= b)).sum()) if a else int((h <= b).sum()) for a, b, _ in FAIXAS_CAUDA]
    tela = _faixas(h)["tela"]  # W3 (C8)
    pcts = [tela["ate1"], tela["de1a2"]] + _pcts(contagens[2:], alvo=tela["acima2"], total=n)
    return contagens, pcts, _pcts(contagens)


def cem_pedidos(mov: pd.DataFrame, mes_parcial: str, grupo: str = "todos") -> dict | None:
    """W1–W7: waffle de 100, chaves A/B, curva acumulada com os marcos e os textos do slide 3."""
    return _cem(_universo(mov, mes_parcial, grupo), mes_parcial)


def _cem(h: pd.Series, mes_parcial: str) -> dict | None:
    import numpy as np

    n = len(h)
    if n < CEM_MIN:
        return None
    contagens, pcts, puro = _cem_pcts(h)
    a = pcts[0] + pcts[1]
    b = 100 - a
    classes = ["c1", "c2", "c3", "c4", "c5"]
    rotulos = ["em até 1 dia", "de 1 a 2 dias", "de 2 a 3 dias", "de 3 a 5 dias", "mais de 5 dias"]
    faixas = [{"classe": k, "rotulo": r, "pct": p, "n": c_} for k, r, p, c_ in zip(classes, rotulos, pcts, contagens)]
    quadrados = [k for k, p in zip(classes, pcts) for _ in range(p)]  # W4

    # W5 curva acumulada, num quadro de W × H (y para baixo)
    W, H, L, R, T, B = 460, 222, 44, 14, 22, 46
    p97 = float(h.quantile(0.97))
    teto = max(math.ceil(p97 / HORAS_DIA) * HORAS_DIA, 3 * HORAS_DIA)
    sx = lambda v: L + (W - L - R) * min(max(v, 0.0), teto) / teto
    sy = lambda f: (H - B) - (H - B - T) * f
    vals = np.sort(h.to_numpy(dtype=float))
    xs = [teto * k / 120 for k in range(121)]
    fs = [float(np.searchsorted(vals, x_, side="right")) / n for x_ in xs]
    pts = [f"{sx(x_):.1f},{sy(f_):.1f}" for x_, f_ in zip(xs, fs)]
    linha = " ".join(pts)
    area = f"M{sx(0):.1f},{sy(0):.1f} L" + " L".join(pts) + f" L{sx(teto):.1f},{sy(0):.1f} Z"
    q80, q90 = float(h.quantile(0.8)), float(h.quantile(0.9))
    f16 = float((h <= META_H).mean())
    marcos = [
        {"chave": "m2", "h": float(META_H), "f": f16, "pct": a, "dias": "2 dias", "horas": f"{META_H} h"},
        {"chave": "m80", "h": q80, "f": 0.8, "pct": 80, "dias": _dias_meio(q80), "horas": _h(q80)},
        {"chave": "m90", "h": q90, "f": 0.9, "pct": 90, "dias": _dias_meio(q90), "horas": _h(q90)},
    ]
    FX = 14.5  # texto dos eixos (unidades do viewBox; ≥ 11 px reais com o quadro a partir de ~355 px de largura, 390 px)
    for m in marcos:
        m["x"], m["y"] = round(sx(m["h"]), 1), round(sy(m["f"]), 1)
        m["tx"], m["w"] = m["x"], max(_larg(m["dias"], FX), _larg(m["horas"], FX)) + 4
    _afasta(marcos, "tx", "w", L + 14, W - R)  # rótulos do eixo x (depois do "0" do eixo)
    piso = math.inf
    for m in sorted(marcos, key=lambda m: -m["y"]):  # rótulos do eixo y (%): ao menos 15 de distância, de baixo para cima
        m["ty"] = round(min(m["y"], piso - 15), 1)
        piso = m["ty"]
    ultimo = float(np.searchsorted(vals, teto, side="right")) / n
    fim_txt = f"{_pct(_pontos(ultimo))} até {teto} h"
    texto = (f"Curva acumulada dos {formato.inteiro(n)} orçamentos entregues {_periodo(mes_parcial)}: "
             f"{a}% ficam prontos em até 2 dias de trabalho (16 h); 80% em até {marcos[1]['dias']} ({marcos[1]['horas']}); "
             f"90% em até {marcos[2]['dias']} ({marcos[2]['horas']}). O eixo vai até {teto} h: {fim_txt}.")
    curva = {"w": W, "h": H, "e": L, "dir": W - R, "topo": T, "base": H - B, "linha": linha, "area": area,
             "marcos": marcos, "teto": teto, "fim_txt": fim_txt, "texto": texto, "fim_y": round(sy(ultimo) - 7, 1),
             "grade": [round(sy(f_), 1) for f_ in (0.25, 0.5, 0.75, 1.0)]}
    t = _cem_textos(a, b)
    waffle_txt = (f"Cem quadrados; cada um é 1% dos {formato.inteiro(n)} orçamentos entregues {_periodo(mes_parcial)}: "
                  + "; ".join(f"{f['pct']} {f['rotulo']}" for f in faixas)
                  + f". Em até 2 dias: {a}; mais de 2 dias: {b}.")
    return {"n": n, "periodo": _periodo(mes_parcial), "faixas": faixas, "quadrados": quadrados, "a": a, "b": b,
            "maior_resto": puro, "ajustado": puro[0] + puro[1] != a, "contagens": contagens,
            "q80": q80, "q90": q90, "p97": p97, "f16": f16, "curva": curva, "waffle_txt": waffle_txt,
            "rodape": t["rodape"], "gancho": t["gancho"]}


# ---------- Estudo "Como medimos", slide 4: "Para onde vai o tempo?" (D40, 25/10/2026) ----------
# Referência: imagem do Caio (25/10/2026). Dois cartões, "Saem em até 2 dias" (A) e "Passam de 2 dias" (B), cada um com a
# parte dos pedidos e a parte das horas da equipe, de 0 a 100, e as faixas de tempo do slide 3.
# V1  Universo: o mesmo dos slides 2 e 3 (X1, W1): entregues dos meses completos de entrega (C7), no grupo de talentos
#     (C10, `?talentos=`); h = horas da equipe sem almoço (C2). Menos de 30 orçamentos (CEM_MIN) ou soma de horas 0: sem
#     o slide (mensagem de poucos dados).
# V2  Pedidos: as cinco faixas do slide 3 (W2) e os MESMOS % (W3, `_cem_pcts`): A = até 1 dia + 1 a 2 dias, B = 100 − A.
# V3  Horas: H_faixa = soma de h da faixa ÷ soma de h do recorte × 100, inteiros pelo maior resto (E8c, somam 100);
#     HA = H das duas primeiras faixas, HB = 100 − HA. Cada linha de um cartão soma o número grande do cartão.
# V4  Barras de 0 a 100 (trilho cinza): largura = o número (pedidos claro, horas escuro), com o % por extenso para o
#     leitor de tela.
# V5  Frase de cada cartão (`_parte`): "<parte dos pedidos> dos pedidos, <parte das horas> do tempo.", em frações por
#     extenso (`_fracao`). 0 pedidos: "Nenhum pedido neste grupo."
# V6  Notas "Prazo" e "Fluxo" (redação do Caio); Prazo cita os B pedidos (B = 1: "nesse pedido"); B = 0: sem as notas.
# V7  Faixa do pé (redação do Caio) com variantes: A > 50 "Na maior parte das vezes entregamos em até 2 dias."; A = 50
#     "Metade dos pedidos sai em até 2 dias."; A < 50 "Neste grupo, menos da metade sai em até 2 dias."; B = 1 no
#     singular; B = 0 "Neste grupo, todos saem em até 2 dias de trabalho…". Gancho (texto, o slide 5 vem depois):
#     "Mas esses B% foram um mês ruim, ou é sempre assim? →" (B = 1: "esse 1% foi"; B = 0: "E isso se repete todo mês?").
# V8  Frações por extenso (`_fracao`), sobre as frações 1/10, 1/5, 1/4, 1/3, 1/2, 2/3, 3/4, 4/5 e 9/10 (em %):
#     (a) 0 → "menos de 1%"; 100 → "100%"; 50 → "metade";
#     (b) a até 1 ponto de uma fração → "cerca de <fração>";
#     (c) até 3 pontos abaixo de uma fração → "quase <fração>" (p ≥ 50) ou "menos de <fração>" (p < 50); senão, até 3
#         pontos acima → "pouco mais de <fração>" (22 → "menos de um quarto", 78 → "quase quatro quintos");
#     (d) longe de todas: se a metade é uma das vizinhas, "mais da metade" / "menos da metade"; senão, a vizinha mais
#         perto ("mais de <de baixo>" ou "menos de <de cima>"); abaixo de 1/10 "menos de um décimo", acima de 9/10 "mais
#         de nove décimos".
# V9  (V2, 30/10/2026: slides 3 e 4 unidos num só) Típico de cada lado: mediana exata de h dos pedidos com h ≤ 16 h
#     (os A) e com h > 16 h (os B), escrita por `_h_meta` (C6); sem pedidos de um lado, None.
# V10 (V2, 30/10/2026) Resposta do slide unificado (`_resposta_cem_tempo`): "{Mais da metade|Metade|Menos da metade}
#     dos pedidos (A%) sai em até 2 dias e leva HA% das horas da equipe; os outros B% passam disso e levam HB%."
#     Os cartões, a frase V5, as notas V6 e a faixa V7 continuam calculados (cola e conferência), mas saíram da tela.
FRACOES = ((10, "um décimo"), (20, "um quinto"), (25, "um quarto"), (100 / 3, "um terço"), (50, "metade"),
           (200 / 3, "dois terços"), (75, "três quartos"), (80, "quatro quintos"), (90, "nove décimos"))


def _de(nome: str, contraida: bool = True) -> str:
    """ "mais de" + fração; com "metade", "da metade"."""
    return ("da " if contraida else "de ") + nome if nome == "metade" else "de " + nome


def _fracao(p: int) -> str:
    """V8: um % inteiro em fração por extenso para quem não é analista ("mais da metade", "menos de um quarto",
    "cerca de um terço", "quase quatro quintos")."""
    if p <= 0:
        return "menos de 1%"
    if p >= 100:
        return "100%"
    if p == 50:
        return "metade"
    for v, nome in FRACOES:  # (b)
        if abs(p - v) <= 1:
            return "cerca de " + nome
    for v, nome in FRACOES:  # (c) primeiro a fração logo acima ("quase", "menos de"), depois a logo abaixo
        if 0 < v - p <= 3:
            return ("quase " + nome) if p >= 50 else "menos " + _de(nome)
    for v, nome in FRACOES:
        if 0 < p - v <= 3:
            return "pouco mais " + _de(nome)
    baixo = [(v, n) for v, n in FRACOES if v < p]
    cima = [(v, n) for v, n in FRACOES if v > p]
    if not baixo:
        return "menos " + _de(cima[0][1])
    if not cima:
        return "mais " + _de(baixo[-1][1])
    (vb, nb), (vc, nc) = baixo[-1], cima[0]
    if nb == "metade":  # (d)
        return "mais da metade"
    if nc == "metade":
        return "menos da metade"
    return "mais " + _de(nb) if p - vb <= vc - p else "menos " + _de(nc)


def _parte(pedidos: int, horas: int) -> str:
    """V5: frase do cartão, comparando a parte dos pedidos com a parte das horas."""
    if pedidos == 0:
        return "Nenhum pedido neste grupo."
    f = _fracao(pedidos)
    return f"{f[0].upper()}{f[1:]} dos pedidos, {_fracao(horas)} do tempo."


def _tempo_textos(a: int, b: int, hb: int) -> dict:
    """V6, V7: notas, faixa do pé e gancho."""
    if b == 0:
        rodape = ("Neste grupo, <strong>todos saem em até 2 dias</strong> de trabalho: nenhum pedido passa disso, e todo o "
                  "tempo com a equipe fica nos casos rápidos.")
        return {"rodape": rodape, "gancho": "E isso se repete todo mês?", "prazo": None, "fluxo": None}
    if a > 50:
        abre = "Na maior parte das vezes entregamos em até 2 dias. Mas "
    elif a == 50:
        abre = "Metade dos pedidos sai em até 2 dias. Mas "
    else:
        abre = "Neste grupo, menos da metade sai em até 2 dias. E "
    um = b == 1
    meio = (f"{'o' if um else 'os'} <strong>{b}% que {'passa' if um else 'passam'} disso</strong> "
            f"{'concentra' if um else 'concentram'} <strong>{hb}% do tempo</strong> que os pedidos ficam com a equipe. ")
    fim = ("<em>É aí que está o ganho:</em> encurtando esses casos, a fila anda mais rápido e o mesmo time dá conta de "
           "mais pedidos.")
    gancho = "Mas esse 1% foi um mês ruim, ou é sempre assim?" if um else f"Mas esses {b}% foram um mês ruim, ou é sempre assim?"
    prazo = ("O maior ganho de tempo de entrega está nesse pedido." if um
             else f"O maior ganho de tempo de entrega está nesses {b} pedidos.")
    fluxo = "Com menos pedidos parados, a fila anda e a equipe absorve mais demanda com o mesmo time."
    return {"rodape": abre + meio + fim, "gancho": gancho, "prazo": prazo, "fluxo": fluxo}


def tempo_cem(mov: pd.DataFrame, mes_parcial: str, grupo: str = "todos") -> dict | None:
    """V1–V8: pedidos e horas da equipe por faixa, nos cartões "Saem em até 2 dias" e "Passam de 2 dias" (slide 4)."""
    return _tempo(_universo(mov, mes_parcial, grupo), mes_parcial)


def _tempo(h: pd.Series, mes_parcial: str) -> dict | None:
    n = len(h)
    if n < CEM_MIN:
        return None
    soma = float(h.sum())
    if soma <= 0:
        return None
    contagens, pcts, _ = _cem_pcts(h)  # V2: os mesmos % do slide 3
    horas_f = [float(h[(h > a) & (h <= b)].sum()) if a else float(h[h <= b].sum()) for a, b, _ in FAIXAS_CAUDA]
    hp = _pcts(horas_f)  # V3
    a, ha = pcts[0] + pcts[1], hp[0] + hp[1]
    b, hb = 100 - a, 100 - ha
    rotulos = ["até 1 dia", "de 1 a 2 dias", "de 2 a 3 dias", "de 3 a 5 dias", "mais de 5 dias"]
    linhas = [{"rotulo": r, "pedidos": p, "horas": q, "n": c_, "soma_h": s_}
              for r, p, q, c_, s_ in zip(rotulos, pcts, hp, contagens, horas_f)]
    t = _tempo_textos(a, b, hb)
    # V9 (V2, 30/10/2026): típico (mediana exata, C6) de cada lado da linha de 2 dias, para o slide 3 unificado
    tip_a, tip_b = _mediana(h[h <= META_H]), _mediana(h[h > META_H])
    cartoes = [
        {"chave": "a", "titulo": "Saem em até 2 dias", "pedidos": a, "horas": ha, "frase": _parte(a, ha), "linhas": linhas[:2]},
        {"chave": "b", "titulo": "Passam de 2 dias", "pedidos": b, "horas": hb, "frase": _parte(b, hb), "linhas": linhas[2:]},
    ]
    return {"n": n, "periodo": _periodo(mes_parcial), "soma_h": soma, "horas_faixas": horas_f, "contagens": contagens,
            "a": a, "b": b, "ha": ha, "hb": hb, "linhas": linhas, "cartoes": cartoes, **t,
            "tipico_a": tip_a, "tipico_b": tip_b,
            "tipico_a_txt": _h_meta(tip_a) if tip_a is not None else None,
            "tipico_b_txt": _h_meta(tip_b) if tip_b is not None else None,
            "resposta": _resposta_cem_tempo(a, b, ha, hb)}


def _resposta_cem_tempo(a: int, b: int, ha: int, hb: int) -> str:
    """V10 (V2, 30/10/2026): a resposta do slide 3 unificado (quantidade × tempo), ligando as duas metades: a parte dos
    pedidos que sai em até 2 dias e a parte das horas da equipe que ela leva; depois, o resto. Mesmos A, B, HA e HB dos
    cartões (V2, V3). Variantes: A > 50 "Mais da metade", A = 50 "Metade", 0 < A < 50 "Menos da metade"; B = 0 e A = 0
    em frase própria; B = 1 no singular."""
    if b == 0:
        return "Neste grupo, <strong>todos saem em até 2 dias</strong> de trabalho e levam 100% das horas da equipe."
    if a == 0:
        return "Neste grupo, <strong>nenhum sai em até 2 dias</strong>: todos passam disso e levam 100% das horas da equipe."
    abre = "Mais da metade" if a > 50 else "Metade" if a == 50 else "Menos da metade"
    resto = ("o outro <strong>1% passa disso</strong> e leva" if b == 1
             else f"os outros <strong>{b}% passam disso</strong> e levam")
    return (f"{abre} dos pedidos (<strong>{a}%</strong>) sai em até 2 dias e leva <strong>{ha}% das horas</strong> da "
            f"equipe; {resto} <strong>{hb}%</strong>.")


# ---------- Estudo "Como medimos", slide 5: "Foi um mês ruim, ou é sempre assim?" (D41, 25/10/2026) ----------
# Referência: imagem do Caio (25/10/2026). Dispersão por mês (um ponto por orçamento), a faixa onde fica a maioria (Q1–Q3)
# e o típico (mediana) de cada mês, a linha de 2 dias e, abaixo do eixo, o % que passa de 2 dias e os pedidos do mês.
# Pergunta da tela (Caio): o problema é sazonal ou é um padrão da equipe? A faixa do pé responde e diz o que fazer.
# U1  Universo: o mesmo dos slides 2–4 (X1, W1, V1): entregues dos meses completos de entrega (C7), mês = mês da 1ª
#     entrega (C4, D-SLA-1), no grupo de talentos (C10, `?talentos=`); h = horas da equipe sem almoço (C2). Menos de 30
#     orçamentos (CEM_MIN) ou menos de 2 meses completos com pedidos: sem o slide (mensagem de poucos dados).
# U2  Layout congelado no ano: o eixo x tem sempre os 12 meses (jan a dez). Os meses sem mês completo de entrega (o vigente,
#     parcial, e os futuros) ficam como colunas vazias, com o nome em cinza e itálico e sem números embaixo; quando o mês
#     fecha, a coluna se preenche sem mudar o desenho. Mês completo sem pedido: coluna com "—".
# U3  "Passam de 2 dias" do mês = B do mês = h > 16 h (META_H), escrito pela mesma conta da página SLA (C8): 100 − o
#     "até 2 dias" do mês arredondado (`_faixas(h)["tela"]["acima2"]`). Soma das quantidades dos meses = n do grupo.
#     Típico do mês = mediana exata, escrita como na página SLA (C6, `_h_meta`: horas inteiras; logo acima de 16 h, com 1
#     casa para cima). Faixa onde fica a maioria = do 1º ao 3º quartil (quantis lineares).
# U4  Eixo y em dias de trabalho (8 h) na escala de raiz quadrada (comprime a cauda): marcas 0, 1, 2, 3, 5 e 10 dias
#     (0, 8, 16, 24, 40 e 80 h). Acima de 10 dias (> 80 h): triângulo no topo (quantos, na legenda e no texto do leitor).
# U5  Posição horizontal de cada ponto na coluna do mês: determinística, pelo hash MD5 do `projeto_id` (u em [0, 1),
#     largura útil de 80% da coluna); coordenadas com 1 casa, geradas no servidor (sem JS).
# U6  Cor do ponto pela faixa de tempo do slide 2 (X3): até 2 dias (≤ 16 h), 2 a 5 dias (16–40 h), mais de 5 dias (> 40 h).
# U7  Mês que destoa (entre os meses completos com pedidos): B do mês mais de 10 pontos acima da mediana dos B mensais
#     (DESTOA_PP) OU típico do mês mais de 4 h acima da mediana dos típicos mensais (DESTOA_H, medianas exatas). Leitura:
#     (a) "raro": todos os meses com B abaixo de 10% (RARO_PCT); (b) "padrão": nenhum mês destoa; (c) "picos": 1 ou 2
#     meses destoam; (d) "sazonal": 3 ou mais destoam. A sugestão do Caio era "3+ meses seguidos"; nos dados de 23/10 os
#     não exclusivos têm 3 meses destoando fora de sequência (abr, mai, ago) — com um só ano não há como separar
#     calendário de acaso, e 3 meses pesados já mudam a resposta (planejar a equipe), então vale 3+ em qualquer posição;
#     se forem seguidos, o texto diz "de abril a junho", senão lista os meses.
# U8  Título e faixa do pé (curta, 1–2 linhas; só números visíveis no gráfico — os B de cada mês; Caio, 25/10):
#     padrão  "A demora não é de um mês. Acontece o ano todo." / "<strong>Não é sazonal:</strong> todo mês, de {Bmin}% a
#             {Bmax}% dos pedidos passam de 2 dias. <em>O problema é o processo, não o mês</em> — é nele que está a
#             solução."
#     picos   mesmo título / "<strong>No geral, não é sazonal:</strong> quase todo mês, de {Bmin}% a {Bmax}% passam de 2
#             dias; só {mês} fugiu / {mês} e {mês} fugiram do padrão. <em>O problema é o processo</em>, com picos
#             pontuais." (Bmin–Bmax sem os meses que destoam; "do padrão" porque o mês pode destoar só pelo típico.)
#     sazonal "A demora pesa em alguns meses do ano." / "<strong>Há meses mais pesados:</strong> de {ini} a {fim} (ou em
#             {m1}, {m2} e {m3}), de {B}% a {B}% passam de 2 dias, contra {B}% a {B}% no resto do ano. <em>Vale
#             planejar a equipe para esses meses.</em>"
#     raro    "Em todos os meses, quase nada passa de 2 dias." / "<strong>Não é sazonal:</strong> todo mês, só de {Bmin}%
#             a {Bmax}% dos pedidos passam de 2 dias. <em>O prazo se mantém o ano todo.</em>"
#     Faixas com mínimo = máximo viram um valor só ("40% dos pedidos"). A frase do volume (rascunho da referência) saiu.
#     Gancho (texto, o slide 6 vem depois): "Se é assim, onde o tempo trava? →".
# U9  Rótulos sem colisão: o valor do típico fica abaixo do ponto (acima dele quando passa de 2 dias); o rótulo da linha
#     de 2 dias vai sobre a linha, terminando na borda direita ou logo antes do ponto de um mês, na posição mais à
#     direita em que nenhuma coluna sob o rótulo tem típico acima de 2 dias (colunas vazias contam como livres); sem
#     posição livre, vai para a legenda ("- - - acima desta linha: mais de 2 dias"). Em tela estreita (letra maior no
#     quadro), o rótulo sempre vai para a legenda.
DESTOA_PP = 10  # U7
DESTOA_H = 4  # U7
RARO_PCT = 10  # U7
DIA_MARCAS = (0, 1, 2, 3, 5, 10)  # U4, em dias de 8 h
TETO_H = 10 * HORAS_DIA  # U4: 80 h
ROT_2DIAS = "acima desta linha: mais de 2 dias"  # U9


def _sorteio(chave) -> float:
    """U5: número em [0, 1) fixo para cada orçamento (hash MD5 do id): o ponto não muda de lugar entre cargas."""
    return int(hashlib.md5(str(chave).encode()).hexdigest()[:8], 16) / 0x100000000


def _faixa_txt(a, b, fmt) -> str:
    """ "de 40% a 51%" / "40%" (mínimo = máximo)."""
    return fmt(a) if a == b else f"de {fmt(a)} a {fmt(b)}"


def _lista(nomes: list[str]) -> str:
    return nomes[0] if len(nomes) == 1 else f"{', '.join(nomes[:-1])} e {nomes[-1]}"


def _destoam(com: list[dict]) -> list[dict]:
    """U7: meses cujo B passa a mediana dos B mensais em mais de 10 pontos ou cujo típico passa a mediana dos típicos em
    mais de 4 h."""
    mb = float(pd.Series([m["b"] for m in com]).median())
    mt = float(pd.Series([m["mediana"] for m in com]).median())
    return [m for m in com if m["b"] - mb > DESTOA_PP or m["mediana"] - mt > DESTOA_H]


def _curto(m: dict) -> str:
    """Z4: nome curto do mês ("abr")."""
    return m.get("rotulo") or formato.MESES[int(m["chave"][5:]) - 1]


def _mes_textos(meses: list[dict]) -> dict:
    """U7, U8: leitura (sazonal × padrão), título, faixa do pé e gancho, só com números que aparecem no gráfico."""
    com = [m for m in meses if not m.get("vazio") and m["n"]]
    destoam = _destoam(com)
    pct = lambda p: f"{p}%"

    def resumo(ms):
        bs = [m["b"] for m in ms]
        ordem = sorted(ms, key=lambda m: m["mediana"])
        return min(bs), max(bs), ordem[0]["tipico"], ordem[-1]["tipico"]

    if max(m["b"] for m in com) < RARO_PCT:
        tipo, titulo = "raro", "Em todos os meses, quase nada passa de 2 dias."
        b0, b1, _, _ = resumo(com)
        rodape = (f"<strong>Não é sazonal:</strong> todo mês, só {_faixa_txt(b0, b1, pct)} dos pedidos passam de 2 dias. "
                  "<em>O prazo se mantém o ano todo.</em>")
        res = {"b0": b0, "b1": b1}
    elif not destoam:
        tipo, titulo = "padrao", "A demora não é de um mês. Acontece o ano todo."
        b0, b1, _, _ = resumo(com)
        rodape = (f"<strong>Não é sazonal:</strong> todo mês, {_faixa_txt(b0, b1, pct)} dos pedidos passam de 2 dias. "
                  "<em>O problema é o processo, não o mês</em> — é nele que está a solução.")
        res = {"b0": b0, "b1": b1}
    elif len(destoam) <= 2:
        tipo, titulo = "picos", "A demora não é de um mês. Acontece o ano todo."
        b0, b1, _, _ = resumo([m for m in com if m not in destoam])
        nomes = _lista([m["extenso"] for m in destoam])
        verbo = "fugiu" if len(destoam) == 1 else "fugiram"
        rodape = (f"<strong>No geral, não é sazonal:</strong> quase todo mês, {_faixa_txt(b0, b1, pct)} passam de 2 dias; "
                  f"só {nomes} {verbo} do padrão. <em>O problema é o processo</em>, com picos pontuais.")
        res = {"b0": b0, "b1": b1, "nomes": nomes, "verbo": verbo}
    else:
        tipo, titulo = "sazonal", "A demora pesa em alguns meses do ano."
        idx = [com.index(m) for m in destoam]
        seguidos = idx == list(range(idx[0], idx[0] + len(idx))) and all(
            int(com[i + 1]["chave"][5:]) - int(com[i]["chave"][5:]) == 1 for i in idx[:-1])
        quando = (f"de {destoam[0]['extenso']} a {destoam[-1]['extenso']}" if seguidos
                  else "em " + _lista([m["extenso"] for m in destoam]))
        d0, d1, _, _ = resumo(destoam)
        o0, o1, _, _ = resumo([m for m in com if m not in destoam])
        contra = f"{o0}%" if o0 == o1 else f"{o0}% a {o1}%"
        rodape = (f"<strong>Há meses mais pesados:</strong> {quando}, {_faixa_txt(d0, d1, pct)} passam de 2 dias, contra "
                  f"{contra} no resto do ano. <em>Vale planejar a equipe para esses meses.</em>")
        res = {"d0": d0, "d1": d1, "contra": contra, "quando": quando,
               "curto": (f"{_curto(destoam[0])} a {_curto(destoam[-1])}" if seguidos
                         else _lista([_curto(m) for m in destoam]))}
    gancho = "Se é assim, onde o tempo trava?"
    return {"tipo": tipo, "titulo": titulo, "rodape": rodape, "gancho": gancho,
            "destoam": [m["chave"] for m in destoam], "resumo": res}  # resumo: números da faixa, para o slide 8 (Z4)


def meses_estudo(mov: pd.DataFrame, mes_parcial: str, grupo: str = "todos") -> dict | None:
    """U1–U9: dispersão por mês, típico e faixa da maioria, % que passa de 2 dias e pedidos de cada mês (slide 5)."""
    return _meses(_universo_df(mov, mes_parcial, grupo), mes_parcial)


def _meses(d: pd.DataFrame, mes_parcial: str) -> dict | None:
    n = len(d)
    completos = int(mes_parcial[5:]) - 1  # C7: jan até o mês anterior ao da carga
    if n < CEM_MIN or completos < 2:
        return None
    ano = mes_parcial[:4]

    # U2/U4: quadro (viewBox) de W × H com as 12 colunas do ano entre E e W − D; topo T (triângulos acima dele), base B
    W, H, E, D, T, B = 1000, 282, 92, 8, 16, 276  # V2 (30/10/2026): 230/224 -> 282/276, sem o selo do topo e a faixa do pe o quadro cresce
    larg = (W - E - D) / 12
    raiz = math.sqrt(TETO_H)

    def sy(h: float) -> float:
        return round(B - (B - T) * math.sqrt(min(max(h, 0.0), TETO_H)) / raiz, 1)

    marcas = [{"rotulo": "0" if dd == 0 else ("1 dia" if dd == 1 else f"{dd} dias"), "y": sy(dd * HORAS_DIA)}
              for dd in DIA_MARCAS]
    pontos: dict[str, list[str]] = {"ate2": [], "de2a5": [], "mais5": []}
    topo: list[str] = []
    meses = []
    for i in range(12):
        chave = f"{ano}-{i + 1:02d}"
        x0 = E + i * larg
        cx = round(x0 + larg / 2, 1)
        m = {"chave": chave, "rotulo": formato.MESES[i], "extenso": formato.MESES_EXTENSO[i], "x0": round(x0, 1),
             "larg": round(larg, 1), "cx": cx, "vazio": i >= completos, "n": 0, "mediana": None, "b": None,
             "tipico": None, "n_topo": 0}
        meses.append(m)
        if m["vazio"]:  # U2: mês vigente (parcial) ou futuro, sem números
            continue
        s = d.loc[d["mes"] == chave]
        h = s["h_trabalho"].astype(float)
        for pid, v in zip(s["projeto_id"], h):  # U5, U6
            x = round(cx + (_sorteio(pid) - 0.5) * 0.8 * larg, 1)
            if v > TETO_H:
                topo.append(f"M{x - 4.5:.1f} {T - 3}l4.5-7.8l4.5 7.8z")
                continue
            classe = "ate2" if v <= META_H else ("de2a5" if v <= CAUDA_H else "mais5")
            pontos[classe].append(f"M{x} {sy(v)}h0")
        m["n"] = len(h)
        if len(h):
            q1, med, q3 = (float(h.quantile(q)) for q in (0.25, 0.5, 0.75))
            m.update({"mediana": med, "q1": q1, "q3": q3, "tipico": _h_meta(med), "b": _faixas(h)["tela"]["acima2"],
                      "n_topo": int((h > TETO_H).sum()), "y_med": sy(med), "y_q1": sy(q1), "y_q3": sy(q3),
                      # U9: valor do típico abaixo do ponto; acima dele quando o típico passa de 2 dias (longe da linha)
                      "y_txt": round(sy(med) + 17 if med <= META_H else sy(med) - 9, 1),
                      "fx": round(cx - 0.36 * larg, 1), "fl": round(0.72 * larg, 1)})
    com = [m for m in meses if m["n"]]
    if len(com) < 2:
        return None
    n_topo = sum(m["n_topo"] for m in meses)
    # U9: rótulo da linha de 2 dias (estimativa folgada da largura: medido no Chrome, ~80% disso)
    larg_txt = _larg(ROT_2DIAS, 11.5)
    rot2 = None
    for j in range(11, -1, -1):  # fim do rótulo: borda direita (último mês) ou antes do ponto do mês j
        fim = (W - D - 6) if j == 11 else meses[j]["cx"] - 8
        ini = fim - larg_txt
        if ini < E + 4:
            break
        tocados = [m for m in meses if m["x0"] < fim and m["x0"] + larg > ini]
        if all(not m["n"] or m["mediana"] <= META_H for m in tocados):
            rot2 = {"x": round(fim, 1), "y": round(sy(META_H) - 7, 1)}
            break
    t = _mes_textos(meses)
    vazios = [m["rotulo"] for m in meses if m["vazio"]]
    texto = (f"Cada ponto é um dos {formato.inteiro(n)} orçamentos entregues {_periodo(mes_parcial)}, na coluna do mês "
             "da entrega, na altura das horas de trabalho da equipe (dias de 8 h, escala comprimida no alto). "
             + "; ".join(f"{m['rotulo']}: típico {m['tipico']}, {m['b']}% passam de 2 dias, "
                         f"{formato.inteiro(m['n'])} pedidos" if m["n"] else f"{m['rotulo']}: nenhum pedido"
                         for m in meses if not m["vazio"])
             + (f". {formato.inteiro(n_topo)} {'pedido passa' if n_topo == 1 else 'pedidos passam'} de 10 dias e "
                f"{'aparece' if n_topo == 1 else 'aparecem'} como triângulo no topo" if n_topo else "")
             + (f". {vazios[0]} a {vazios[-1]}: ainda sem mês completo." if len(vazios) > 1
                else f". {vazios[0]}: ainda sem mês completo." if vazios else "."))
    grafico = {"w": W, "h": H, "e": E, "dir": W - D, "topo": T, "base": B, "marcas": marcas, "y2": sy(META_H),
               "pontos": {k: " ".join(v) for k, v in pontos.items()}, "triangulos": "".join(topo),
               "linha": " ".join(f"{m['cx']},{m['y_med']}" for m in com), "texto": texto, "rot2": rot2,
               "rot2_txt": ROT_2DIAS}
    return {"n": n, "periodo": _periodo(mes_parcial), "meses": meses, "n_topo": n_topo, "grafico": grafico, **t}



# ---------- Slide 6 do estudo "Como medimos" (D42, 25/10/2026, referência do Caio): "Onde o tempo trava?" ----------
# K1  Base: o universo dos slides 2–5 (meses completos de entrega, C7; grupo de talentos, C10) e, de cada orçamento, as
#     horas úteis da equipe em cada status antes da 1ª entrega (Aguardando Feedback), sem almoço e sem o Retorno Marca
#     (C2, D-SLA-2): a mesma conta de `h_trabalho`, aberta por status (passagens repetidas no mesmo status somam). Por
#     orçamento, a soma dos status é o `h_trabalho`.
# K2  Status → etapa do ciclo: "Entrada" = Entrada; "Em elaboração…" = Elaboração; "Em revisão…" = Revisão (mesma
#     leitura da C14 e do slide 1). Nome na tela = o nome do board sem o prefixo da etapa ("Em elaboração - Orçamentos"
#     → "Orçamentos", "Em elaboração (Produção)" → "Produção"); os status gerais, sem sub-status ("Em Elaboração", "Em
#     revisão", usados até maio), ficam "Em elaboração" e "Em revisão"; "Entrada" vira "Fila de entrada". Grafias do
#     mesmo status ("Em elaboração - GP" e "Em elaboração GP") viram um só cartão. Status da equipe fora dessas três
#     etapas (nenhum na carga de 23/10) vão para uma linha "Outros status", para nada sumir da conta.
# K3  Por status: tempo de cada orçamento que passou por ele; típico = mediana desses tempos; limite normal = Q3 + 1,5 ×
#     (Q3 − Q1) do próprio status (Tukey, como o passo 3 do slide 2); "travou" = orçamento cujo tempo no status passou
#     do limite.
# K4  Tempo travado do status = soma do TEMPO INTEIRO, naquele status, dos orçamentos que travaram nele (decisão do
#     Caio, 25/10/2026; antes era só o excesso acima do limite). % = tempo travado do status ÷ tempo travado de todos os
#     status, inteiros pelo maior resto somando 100 (E8c); "<1%" quando há tempo travado mas o inteiro dá 0.
# K5  Cartões: em cada etapa, os status em ordem de tempo travado; até TRAVA_CARTOES cartões com nome e o resto num
#     cartão "Outros N status" (soma dos % e dos orçamentos que travaram em algum deles; os nomes vão no texto para
#     leitor de tela e na dica; sem tempo travado no resto, o cartão não aparece, pois valeria 0%). Barra fina proporcional ao
#     tempo travado do maior status. Destaque: os 2 status com mais tempo travado (por regra; o "Outros" não destaca).
# K6  Status visto só em orçamentos entregues antes do último mês completo: o cartão diz "só até <mês>" (os sub-status
#     começaram em 14/05/2026 e os status gerais deixaram de ser usados).
# K7  Faixa do pé: 1 status com mais de 50% → "um ponto"; os 2 maiores somando menos de 40% → "espalhado"; senão "dois
#     pontos" com a soma dos 2 maiores. Só números que estão nos cartões (a soma é dos dois % escritos).
# K8  Gancho: "E em que tipo de pedido isso pesa mais?", link para o slide 7 (#7, D43).
TRAVA_CARTOES = 3  # K5
TRAVA_UM = 50  # K7: % acima do qual um status domina sozinho
TRAVA_ESPALHADO = 40  # K7: soma dos 2 maiores abaixo da qual o tempo trava espalhado
ETAPAS_CICLO = ("Entrada", "Elaboração", "Revisão")  # K2
OUTRAS = "Outros status"  # K2: etapa dos status da equipe fora das três (só aparece se existir)


def _etapa_ciclo(status: str) -> str:
    """K2: etapa do ciclo de um status da equipe (o Retorno Marca já saiu da conta em K1)."""
    s = " ".join(str(status).split()).lower()
    if s == FILA.lower():
        return "Entrada"
    if s.startswith("em elabora"):
        return "Elaboração"
    if s.startswith("em revis"):
        return "Revisão"
    return OUTRAS


def _nome_status(status: str) -> str:
    """K2: nome curto na linguagem do board, sem o prefixo da etapa."""
    s = " ".join(str(status).split())
    if s.lower() == FILA.lower():
        return "Fila de entrada"
    for prefixo in ("em elaboração", "em revisão"):
        if s.lower().startswith(prefixo):
            resto = s[len(prefixo):].strip().lstrip("-–").strip()
            if resto.startswith("(") and resto.endswith(")"):
                resto = resto[1:-1].strip()
            return resto[:1].upper() + resto[1:] if resto else prefixo.capitalize()
    return s


def _h1(x: float) -> str:
    """Horas com uma casa ("2,8 h"), como a referência."""
    return f"{_br(x)} h"


def travas(mov: pd.DataFrame, mes_parcial: str, grupo: str = "todos") -> dict | None:
    """K1–K8: onde o tempo trava, por status e etapa do ciclo (slide 6)."""
    u = _universo_df(mov, mes_parcial, grupo)
    ps = horas_por_status(mov)
    return _travas(u, ps.loc[ps["projeto_id"].isin(u["projeto_id"])], mes_parcial)


def _pct_txt(p: int, exc: float) -> str:
    return "<1%" if p == 0 and exc > 0 else f"{p}%"


def _travas(u: pd.DataFrame, ps: pd.DataFrame, mes_parcial: str) -> dict | None:
    if len(u) < CEM_MIN or ps.empty:
        return None
    d = ps.merge(u[["projeto_id", "mes"]], on="projeto_id")
    d["etapa"] = d["status"].map(_etapa_ciclo)
    d["nome"] = d["status"].map(_nome_status)
    # K1/K2: um tempo por orçamento e status (grafias do mesmo status somadas)
    d = d.groupby(["etapa", "nome", "projeto_id"], as_index=False).agg(h=("h", "sum"), mes=("mes", "first"))
    originais = ps.assign(nome=ps["status"].map(_nome_status), etapa=ps["status"].map(_etapa_ciclo))
    ultimo = f"{mes_parcial[:4]}-{int(mes_parcial[5:]) - 1:02d}"
    st = []
    for (etapa, nome), g in d.groupby(["etapa", "nome"], sort=False):
        h = g["h"].astype(float)
        q1, med, q3 = (float(h.quantile(q)) for q in (0.25, 0.5, 0.75))
        lim = q3 + 1.5 * (q3 - q1)  # K3
        trav = h > lim
        ate = str(g["mes"].max())
        st.append({"etapa": etapa, "nome": nome, "n": len(h), "mediana": med, "tipico": _h1(med), "q1": q1,
                   "q3": q3, "limite": lim, "limite_txt": _h1(lim), "travaram": int(trav.sum()),
                   "travado": float(h[trav].sum()),  # K4 (Caio, 25/10/2026): o tempo inteiro de quem travou
                   "projetos": set(g.loc[trav, "projeto_id"]),
                   "originais": sorted(set(originais.loc[(originais["etapa"] == etapa) & (originais["nome"] == nome), "status"])),
                   "ate": formato.MESES[int(ate[5:]) - 1] if ate < ultimo else None})  # K6
    total = sum(s["travado"] for s in st)
    if not total:
        return None
    for s, p in zip(st, _pcts([s["travado"] for s in st])):
        s["pct"] = p
    maior = max(s["travado"] for s in st)
    ordem = sorted(st, key=lambda s: (-s["travado"], -s["n"], s["nome"]))
    destaque = {(s["etapa"], s["nome"]) for s in ordem[:2] if s["travado"] > 0}  # K5

    def cartao(s: dict) -> dict:
        c = {k: v for k, v in s.items() if k != "projetos"}
        verbo = "travou" if c["travaram"] == 1 else "travaram"
        c.update(pct_txt=_pct_txt(c["pct"], c["travado"]), barra=round(100 * c["travado"] / maior, 1),
                 destaque=(c["etapa"], c["nome"]) in destaque, outros=False,
                 partes=[f"{formato.inteiro(c['travaram'])} {verbo}", f"acima de {c['limite_txt']}"],  # batalha de agentes (A-N5/B-N3): o limite do normal, não o típico
                 nota=f"só até {c['ate']}" if c["ate"] else None)  # K6: linha curta própria
        c["meta"] = " · ".join(c["partes"])
        c["leitor"] = (f"{c['nome']}: {c['pct_txt']} do tempo travado. {formato.inteiro(c['travaram'])} de "
                       f"{formato.inteiro(c['n'])} orçamentos que passaram por este status {verbo}, isto é, passaram de "
                       f"{c['limite_txt']}, o normal deste status; tempo típico de quem passa por ele {c['tipico']}"
                       + (f"; só em pedidos entregues até {c['ate']}" if c["ate"] else "")
                       + ("; um dos dois maiores pontos de trava" if c["destaque"] else "") + ".")
        return c

    etapas = []
    for etapa in ETAPAS_CICLO + (OUTRAS,):
        lista = [s for s in ordem if s["etapa"] == etapa]
        if etapa == OUTRAS and not lista:
            continue
        cartoes = [cartao(s) for s in lista[:TRAVA_CARTOES]]
        resto = lista[TRAVA_CARTOES:]
        if resto and sum(s["travado"] for s in resto):  # K5 (sem tempo travado, o "Outros" não aparece: vale 0%)
            exc = sum(s["travado"] for s in resto)
            p = sum(s["pct"] for s in resto)
            projs = set().union(*(s["projetos"] for s in resto))
            nomes = _lista([s["nome"] for s in resto])
            verbo = "travou" if len(projs) == 1 else "travaram"
            pt = _pct_txt(p, exc)
            cartoes.append({"etapa": etapa, "nome": f"Outros {len(resto)} status", "outros": True, "destaque": False,
                            "pct": p, "pct_txt": pt, "travado": exc, "travaram": len(projs), "ate": None,
                            "barra": round(100 * exc / maior, 1), "membros": [s["nome"] for s in resto],
                            "meta": f"{formato.inteiro(len(projs))} {verbo}", "partes": [f"{formato.inteiro(len(projs))} {verbo}"], "nota": None,
                            "nomes": nomes,
                            "leitor": f"Outros {len(resto)} status ({nomes}): {pt} do tempo travado; "
                                      f"{formato.inteiro(len(projs))} {'orçamento' if len(projs) == 1 else 'orçamentos'} "
                                      f"{verbo} em algum deles."})
        etapas.append({"numero": len(etapas) + 1, "nome": etapa, "cartoes": cartoes, "retorno": etapa == "Elaboração"})
    # B-N3 (25/10/2026): base comum dos % — o tempo travado como parte de TODAS as horas da equipe do recorte
    horas = float(u["h_trabalho"].astype(float).sum())
    pct_horas = _pontos(total / horas) if horas else None
    return {"n": len(u), "status": [cartao(s) for s in ordem], "etapas": etapas, "total_h": total,
            "horas_total": horas, "pct_horas": pct_horas,
            "numero_entrega": len(etapas) + 1, **_trava_textos(ordem, pct_horas)}


def _trava_nome(s: dict) -> str:
    """K6/K7: nome na faixa do pé; status visto só até um mês leva a ressalva escrita no cartão."""
    return f"<strong>{escape(s['nome'])}</strong>" + (f" (só até {s['ate']})" if s.get("ate") else "")


def _trava_textos(ordem: list[dict], pct_horas: int | None = None) -> dict:
    """K7, K8: faixa do pé por regra, só com os % escritos nos cartões."""
    a, b = ordem[0], (ordem[1] if len(ordem) > 1 else None)
    if b is None or a["pct"] > TRAVA_UM:
        tipo = "um"
        rodape = (f"O tempo trava principalmente em um ponto: {_trava_nome(a)} concentra "
                  f"<em>{a['pct']}% do tempo travado</em>.")
    elif a["pct"] + b["pct"] < TRAVA_ESPALHADO:
        tipo = "espalhado"
        rodape = (f"O tempo trava espalhado pelo ciclo: os dois pontos maiores, {_trava_nome(a)} e "
                  f"{_trava_nome(b)}, somam só <em>{a['pct'] + b['pct']}% do tempo travado</em>.")
    else:
        tipo = "dois"
        rodape = (f"O tempo trava principalmente em dois pontos: {_trava_nome(a)} e "
                  f"{_trava_nome(b)} somam <em>{a['pct'] + b['pct']}% do tempo travado</em>.")
    return {"tipo": tipo, "rodape": rodape, "gancho": "E em que tipo de pedido isso pesa mais?",
            "intro": ("De todo o tempo travado, quanto fica em cada etapa. Travar é passar muito do tempo normal daquele "
                      "status; o tempo travado é o tempo inteiro, naquele status, dos orçamentos que travaram."
                      + (f" O tempo travado é {pct_horas}% de todas as horas da equipe." if pct_horas is not None else ""))}



# ---------- Slide 7 do estudo "Como medimos" (D43, 25/10/2026, referência do Caio): "Em que tipo de pedido o tempo trava?" ----------
# J1  Base: o universo dos slides 2–6 (meses completos de entrega, C7; mês da 1ª entrega, C4; grupo de talentos, C10;
#     h = `h_trabalho`, sem almoço e sem o Retorno Marca, C2). Tipo = `tipo_de_input` do projeto na gold de movimentos
#     (`TAB_SLA`, lido no passo 1; o mesmo em todos os passos do projeto — conferido na carga de 23/10: nenhum projeto
#     com dois tipos). Vazio/nulo = "vazio". Menos de 30 orçamentos (CEM_MIN): sem o slide.
# J2  Linha própria só para tipo com ao menos TIPO_MIN (30) pedidos no recorte; os demais e o vazio vão para "Outros"
#     (sem linha: só a nota, com os nomes, pedidos e %). Nome na tela: o do board sem a explicação entre parênteses
#     ("OTR (Oportunidade em Tempo Real)" → "OTR").
# J3  Volume: "Maior volume" = tipos com linha e ao menos VOLUME_MAIOR (10%) dos pedidos do recorte; "Menor volume" = os
#     outros tipos com linha. % de cada tipo com 1 casa (meio para cima); % dos grupos (maior, menor, Outros) inteiros
#     pelo maior resto somando 100 (E8c). Em cada grupo, tipos em ordem de pedidos (o maior primeiro).
# J4  Por linha (e na de "Todos os pedidos"): A = % em até 2 dias (h ≤ 16 h, META_H) pela C8 (`_faixas`, o mesmo A dos
#     slides 3 e 4); B = 100 − A; típico = mediana em horas inteiras (`_h_meta`, C6, como o seletor). A barra é 100% empilhada
#     (A azul, B amarelo); a linha tracejada marca o A de "Todos" ("Geral: A% em até 2 dias").
# J5  Onde mais trava: entre os pedidos do tipo que passam de 2 dias (h > 16 h), as horas por etapa do ciclo (status →
#     etapa da K2, slide 6: Entrada = "Fila de entrada", Elaboração, Revisão); a etapa com mais horas e p = horas dessa
#     etapa ÷ horas desses pedidos (inteiro, meio para cima). Na tela, só a etapa e "{p}%" (o resto no leitor de tela);
#     sem pedido acima de 2 dias: "—". Na linha "Todos" não aparece (o valor fica no dado e na ficha).
# J6  Cores por regra, iguais em todas as linhas (ajuste do Caio, 25/10/2026): azul = saem em até 2 dias; amarelo =
#     passam de 2 dias com o tipo no nível do geral ou melhor; VERMELHO = passam de 2 dias só no tipo claramente pior que
#     o geral (B ≥ B geral + DESTOA_TIPO, 3 pontos, e ao menos TIPO_MIN pedidos — todo tipo com linha). "Todos os pedidos"
#     fica escuro, como referência. `destaque` = o tipo da faixa do pé (J7), sem cor própria.
# J7  Faixa do pé (a única análise na tela; curta, só números da tela). Entre os tipos de maior volume (sem nenhum, entre
#     todos os tipos com linha), o de maior B (empate: mais pedidos). Se ele está em vermelho: "<strong>O {tipo} é o que
#     mais demora</strong>: {B}% passam de 2 dias, contra {G}% no geral — e trava mais na {etapa}." (etapa da J5, em
#     minúsculas; "Outros status" → "em outros status"). Senão: "<strong>Os tipos de maior volume ficam perto do
#     geral</strong>: de {Bmin}% a {Bmax}% passam de 2 dias, contra {G}%." (um tipo: "O {tipo} fica perto do geral";
#     faixa com mínimo = máximo vira um valor só) e, se houver tipos de menor volume em vermelho, "Só <strong>{lista}
#     </strong>, de menor volume, passa(m) bem mais."
# J8  Fora da tela (ajuste do Caio: a nota saiu): no aria-label da tabela e na ficha vão o recorte ("Os mesmos {n}
#     orçamentos…"), os tipos de menor volume em vermelho ("O tipo {X} chega a {B}% acima de 2 dias, com {n} pedidos.") e
#     "Outros ({lista}): {n} pedidos ({%}), poucos para comparar; sem linha própria."
# J9  Gancho, link para a conclusão (slide 8, #8, D44): "E o que os dados nos mostraram?".
TIPO_MIN = 30  # J2
VOLUME_MAIOR = 10  # J3: % dos pedidos
DESTOA_TIPO = 3  # J6: pontos acima do geral para o vermelho
ETAPA_TELA = {"Entrada": "Fila de entrada", "Elaboração": "Elaboração", "Revisão": "Revisão", OUTRAS: OUTRAS}  # J5


def _tipo_nome(t) -> str:
    """J1, J2: nome curto do tipo (sem a explicação entre parênteses); vazio/nulo → "vazio"."""
    if t is None or pd.isna(t) or not str(t).strip():
        return "vazio"
    s = " ".join(str(t).split())
    return s.split(" (")[0]


def _pct1(parte: int, total: int) -> str:
    """J3: % com 1 casa, meio para cima ("58,7%")."""
    return _br(math.floor(1000 * parte / total + 0.5) / 10) + "%" if total else "0,0%"


def tipos_pedido(mov: pd.DataFrame, mes_parcial: str, grupo: str = "todos") -> dict | None:
    """J1–J9: por Tipo de Input, % em até 2 dias, típico e onde mais trava (slide 7)."""
    u = _universo_df(mov, mes_parcial, grupo)
    ps = horas_por_status(mov)
    return _tipos(u, ps.loc[ps["projeto_id"].isin(u["projeto_id"])], mes_parcial)


def _onde_trava(ids: pd.Series, ps: pd.DataFrame) -> dict | None:
    """J5: etapa com mais horas entre os pedidos dados (os que passam de 2 dias) e a parte dela."""
    d = ps.loc[ps["projeto_id"].isin(ids)]
    if d.empty or float(d["h"].sum()) <= 0:
        return None
    por = d.groupby(d["status"].map(_etapa_ciclo))["h"].sum()
    ordem = sorted(por.items(), key=lambda kv: (-kv[1], (ETAPAS_CICLO + (OUTRAS,)).index(kv[0])))
    etapa, h = ordem[0]
    return {"etapa": ETAPA_TELA[etapa], "p": _pontos(h / float(por.sum())), "horas": {k: float(v) for k, v in por.items()}}


def _tipos(u: pd.DataFrame, ps: pd.DataFrame, mes_parcial: str) -> dict | None:
    n = len(u)
    if n < CEM_MIN:
        return None
    bruto = u["tipo_input"] if "tipo_input" in u else pd.Series(None, index=u.index, dtype="object")
    tipo = bruto.map(_tipo_nome)

    def linha(mask: pd.Series, nome: str) -> dict:
        h = u.loc[mask, "h_trabalho"].astype(float)
        a = _faixas(h)["tela"]["ate2"]  # J4 (C8)
        lentos = u.loc[mask & (u["h_trabalho"] > META_H), "projeto_id"]
        return {"tipo": nome, "n": int(mask.sum()), "pct_txt": _pct1(int(mask.sum()), n), "a": a, "b": 100 - a,
                "mediana": float(h.median()), "tipico": _h_meta(float(h.median())), "n_lentos": len(lentos),
                "trava": _onde_trava(lentos, ps), "destaque": False}

    geral = linha(pd.Series(True, index=u.index), "Todos os pedidos")
    contagem = tipo.value_counts()
    proprios = sorted((t for t in contagem.index if t != "vazio" and contagem[t] >= TIPO_MIN),
                      key=lambda t: (-contagem[t], t))  # J2
    outros = sorted((t for t in contagem.index if t not in proprios), key=lambda t: (t == "vazio", -contagem[t], t))
    maior = [t for t in proprios if 100 * contagem[t] / n >= VOLUME_MAIOR]  # J3
    menor = [t for t in proprios if t not in maior]
    n_maior, n_menor, n_outros = (int(sum(contagem[t] for t in g)) for g in (maior, menor, outros))
    p_maior, p_menor, _ = _pcts([n_maior, n_menor, n_outros])
    linhas = {t: linha(tipo == t, t) for t in proprios}

    # J6 cor por regra: vermelho = claramente pior que o geral (B ≥ geral + 3 pontos, tipo com linha: ≥ 30 pedidos)
    for r in linhas.values():
        r["vermelho"] = r["b"] - geral["b"] >= DESTOA_TIPO and r["n"] >= TIPO_MIN
    alvo = [linhas[t] for t in (maior or proprios)]  # J7
    pior = max(alvo, key=lambda r: (r["b"], r["n"])) if alvo else None
    if pior is not None and pior["vermelho"]:
        pior["destaque"] = True

    for r in [geral] + list(linhas.values()):
        partes = [f"{r['tipo']}: {formato.inteiro(r['n'])} {'pedido' if r['n'] == 1 else 'pedidos'}"
                  + (f", {r['pct_txt']} do total" if r is not geral else "") + ".",
                  f"{r['a']}% saem em até 2 dias e {r['b']}% passam de 2 dias"
                  + (", bem acima do geral." if r.get("vermelho") else "."), f"Tempo típico {r['tipico']}."]
        if r is not geral:
            partes.append(f"Onde passa mais tempo: {r['trava']['etapa']}, {r['trava']['p']}% do tempo dos que passam de 2 dias."
                          if r["trava"] else "Nenhum pedido passa de 2 dias.")
        r["leitor"] = " ".join(partes)
        r["a_dentro"], r["b_dentro"] = r["a"] >= 7, r["b"] >= 7  # o % só é escrito dentro da barra se couber

    grupos = []
    if maior:
        grupos.append({"chave": "maior", "rotulo": f"Maior volume · {p_maior}% dos pedidos", "linhas": [linhas[t] for t in maior]})
    if menor:
        grupos.append({"chave": "menor", "rotulo": f"Menor volume · {p_menor}% dos pedidos" if maior else "Por tipo",
                       "linhas": [linhas[t] for t in menor]})

    # J7 faixa do pé (curta; só números da tela)
    g = geral["b"]
    if pior is not None and pior["destaque"]:
        tipo_txt = "destaque"
        etapa = pior["trava"]["etapa"] if pior["trava"] else None
        onde = (" — e passa mais tempo em outros status" if etapa == OUTRAS
                else f" — e passa mais tempo na {etapa.lower()}" if etapa else "")
        rodape = (f"<strong>O {escape(pior['tipo'])} é o que mais demora</strong>: {pior['b']}% passam de 2 dias, contra "
                  f"{g}% no geral{onde}.")
    elif alvo:
        tipo_txt = "parecido"
        bs = sorted(r["b"] for r in alvo)
        faixa = f"{bs[0]}%" if bs[0] == bs[-1] else f"de {bs[0]}% a {bs[-1]}%"
        quem = (f"O {alvo[0]['tipo']} fica" if len(alvo) == 1
                else "Os tipos de maior volume ficam" if maior else "Os tipos ficam")
        rodape = f"<strong>{escape(quem)} perto do geral</strong>: {faixa} passam de 2 dias, contra {g}%."
        verm = [linhas[t]["tipo"] for t in menor if linhas[t]["vermelho"]] if maior else []
        if verm:
            rodape += (f" Só <strong>{escape(_lista(verm))}</strong>, de menor volume, "
                       f"{'passa' if len(verm) == 1 else 'passam'} bem mais.")
    else:
        tipo_txt, rodape = "sem-tipos", None

    # J8 fora da tela (aria-label da tabela e ficha): o recorte, os tipos de menor volume em vermelho e "Outros"
    nota = [f"Os mesmos {formato.inteiro(n)} orçamentos das páginas anteriores, por Tipo de Input."]
    for t in menor:
        r = linhas[t]
        if r["vermelho"]:
            nota.append(f"O tipo {r['tipo']} chega a {r['b']}% acima de 2 dias, com {formato.inteiro(r['n'])} pedidos.")
    if outros:
        nota.append(f"Outros ({_lista(outros)}): {formato.inteiro(n_outros)} {'pedido' if n_outros == 1 else 'pedidos'} "
                    f"({_pct1(n_outros, n)}), poucos para comparar; sem linha própria.")
    return {"n": n, "periodo": _periodo(mes_parcial), "geral": geral, "grupos": grupos, "linhas": list(linhas.values()),
            "outros": [{"tipo": t, "n": int(contagem[t])} for t in outros], "n_outros": n_outros,
            "pcts_grupos": {"maior": p_maior, "menor": p_menor}, "tipo": tipo_txt, "rodape": rodape,
            "nota": " ".join(nota), "gancho": "E o que os dados nos mostraram?", "legenda_geral": f"Geral: {geral['a']}% em até 2 dias",
            "texto": (f"Por Tipo de Input, dos {formato.inteiro(n)} orçamentos entregues {_periodo(mes_parcial)}: barra de "
                      f"0 a 100% com a parte que sai em até 2 dias de trabalho e a que passa de 2 dias (em vermelho quando "
                      f"passa do geral em {DESTOA_TIPO} pontos ou mais); linha tracejada no geral, {geral['a']}% em até 2 "
                      f"dias. " + " ".join(nota[1:]))}



# ---------- Slide 8 do estudo "Como medimos" (D44, 25/10/2026, referência do Caio): "O que os dados nos mostraram" ----------
# Conclusão: seis achados numa linha do tempo, todos tirados das MESMAS funções dos slides 2–7 (mesmo universo, mesmo grupo
# de talentos; nada fixo), o bloco "Onde olhar com mais detalhe" e a faixa "O que isso pede".
# Z1  O tempo típico: mediana (`_h_meta`, C6: 16,3 h nunca vira "16 h" em vermelho) e média (`_h`) das horas da
#     equipe, os números do seletor e do slide 2, "de trabalho. A
#     média, {média}, é puxada por poucos casos longos." (média ≤ mediana: "A média, {média}, fica perto."). Azul se o
#     típico está na meta de 2 dias (C6, mediana exata ≤ 16 h); senão vermelho.
# Z2  A = % em até 2 dias (slides 3 e 4, `tempo_cem["a"]`). Título: A > 50 "A maioria é rápida"; A = 50 "Metade é
#     rápida"; A < 50 "Menos da metade é rápida". Azul se A ≥ 50 (meta sugerida, C6); senão vermelho.
# Z3  HB e B do slide 4: "{HB}% do tempo com a equipe vai para os {B}% que levam mais de 2 dias." Vermelho. B = 0:
#     "Ninguém passa de 2 dias" / "0%" / "Todo o tempo fica nos pedidos rápidos." (azul).
# Z4  Leitura do slide 5 (U7, `meses_estudo`): padrão → "Não é crise, é padrão" · "todo mês" · "de {Bmin}% a {Bmax}%
#     passam de 2 dias{, mesmo com o volume crescendo}."; picos → "No geral, é padrão" · "quase todo mês" · "de {Bmin}%
#     a {Bmax}% passam de 2 dias; só {meses} fugiu/fugiram."; sazonal → "Há meses mais pesados" · "{meses curtos}" ·
#     "{faixa}% passam de 2 dias, contra {faixa} no resto do ano."; raro → "O prazo se mantém" · "todo mês" · "só {faixa}
#     passam de 2 dias." (azul; os demais vermelhos). "Volume crescendo" só se a média de pedidos dos 3 últimos meses
#     completos passa a dos 3 primeiros em 25% ou mais (VOLUME_CRESCE), com ao menos 6 meses completos com pedidos.
# Z5  Leitura do slide 6 (K7, `travas`, com o tempo travado = tempo inteiro de quem travou): dois → "Trava em dois
#     pontos" · "{p1 + p2}%" · "do tempo travado fica em dois status: {s1} e {s2}."; um → "Trava em um ponto" · "{p1}%" ·
#     "do tempo travado fica em um status: {s1}."; espalhado → "Trava espalhado" · "{p1 + p2}%" · "é o que somam os dois
#     maiores pontos, {s1} e {s2}." Status visto só até um mês leva "(só até <mês>)". Vermelho. Batalha de agentes
#     (25/10/2026, B-N3): "do tempo travado" leva a base, "({X}% de todas as horas)" = tempo travado ÷ horas da equipe do
#     recorte (`travas()["pct_horas"]`), para não ser comparado com os 84% do achado 3 (base: todas as horas).
# Z6  Leitura do slide 7 (J7, `tipos_pedido`): com destaque → "Pesa mais no {tipo}" · "{B}%" · "dos pedidos {tipo}
#     passam de 2 dias; é onde a {etapa} mais pesa." (vermelho); sem destaque → "Os tipos se parecem" · "{Bmin}–{Bmax}%"
#     (um valor só se iguais) · "nos tipos de maior volume passam de 2 dias, perto dos {G}% do geral.{ Exceção: {lista
#     dos tipos em vermelho}.}" (um tipo de maior volume só: "O {tipo} segue o geral" · "dos pedidos {tipo} passam…");
#     vermelho se há tipo em vermelho; senão azul.
# Z7  Onde olhar com mais detalhe: os 2 status de maior tempo travado do slide 6 (título = nome do status, com "(só até
#     <mês>)"), cada um com uma pergunta de investigação pelo tipo de status (PERGUNTAS; fila de entrada cita o tipo de
#     pedido do slide 7 quando a fila é onde ele mais trava) e "Pedidos acima de 5 dias": "São {p}% ({n} pedidos). Abrir
#     caso a caso e achar o que eles têm em comum." (C12, > 40 h; % e não "de cada 100", preferência do Caio).
# Z8  Faixa "O que isso pede": texto fixo de recomendação (do Caio). Sem gancho: o fim leva de volta ao slide 1.
VOLUME_CRESCE = 1.25  # Z4


def _pergunta(etapa: str, nome: str, tipo_fila: str | None) -> str:
    """Z7: pergunta de investigação pelo tipo de status."""
    n = nome.lower()
    if etapa == "Entrada":
        return "Por que o pedido espera antes de começar" + (f", principalmente no {tipo_fila}?" if tipo_fila else "?")
    if etapa == "Elaboração":
        if "cotação" in n:
            return "O que atrasa a cotação? Quem responde e em quanto tempo?"
        if "produção" in n:
            return "O que segura a produção? Falta de informação, aprovações, fila de outra área?"
        if "validação" in n:
            return "O que faz a validação demorar? Quem valida e quando o pedido chega até ele?"
        return "O que segura o orçamento? Falta de informação do pedido, cotações, vai e volta?"
    if etapa == "Revisão":
        if "validação" in n:
            return "O que faz a validação demorar? Quem valida e quando o pedido chega até ele?"
        return "O que faz a revisão demorar? Quem revisa e quando o pedido chega até ele?"
    return "O que acontece neste status e por que ele se alonga?"


def _status_txt(s: dict) -> str:
    return s["nome"] + (f" (só até {s['ate']})" if s.get("ate") else "")


def conclusao(mov: pd.DataFrame, mes_parcial: str, grupo: str = "todos", tempo: dict | None = None,
              meses: dict | None = None, trava: dict | None = None, tipos: dict | None = None) -> dict | None:
    """Z1–Z8: os achados do estudo (slide 8). Recebe os dicts já calculados dos slides 4–7 (ou calcula)."""
    h = _universo(mov, mes_parcial, grupo)
    tempo = tempo if tempo is not None else tempo_cem(mov, mes_parcial, grupo)
    meses = meses if meses is not None else meses_estudo(mov, mes_parcial, grupo)
    trava = trava if trava is not None else travas(mov, mes_parcial, grupo)
    tipos = tipos if tipos is not None else tipos_pedido(mov, mes_parcial, grupo)
    return _conclusao(h, tempo, meses, trava, tipos)


def _conclusao(h: pd.Series, tempo: dict | None, meses: dict | None, trava: dict | None, tipos: dict | None) -> dict | None:
    if len(h) < CEM_MIN or not tempo:
        return None
    achados = []

    def achado(titulo, valor, frase, problema, leitor_valor=None):
        achados.append({"numero": len(achados) + 1, "titulo": titulo, "valor": valor, "frase": frase,
                        "cor": "problema" if problema else "bom", "longo": len(valor) > 9,  # Z4: lista de meses, letra menor
                        "leitor": f"{titulo}: {leitor_valor or valor} {frase}"})

    # Z1
    med, media = float(h.median()), float(h.mean())
    resto = ("é puxada por poucos casos longos." if _arred(media) > _arred(med) else "fica perto.")
    achado("O tempo típico", _h_meta(med), f"de trabalho. A média, {_h(media)}, {resto}", med > META_H)
    # Z2
    a, b, hb = tempo["a"], tempo["b"], tempo["hb"]
    titulo = "A maioria é rápida" if a > 50 else "Metade é rápida" if a == 50 else "Menos da metade é rápida"
    achado(titulo, f"{a}%", "dos pedidos ficam prontos em até 2 dias de trabalho.", a < 50)
    # Z3
    if b == 0:
        achado("Ninguém passa de 2 dias", "0%", "Todo o tempo fica nos pedidos rápidos.", False)
    else:
        achado("Os demorados pesam", f"{hb}%", f"do tempo com a equipe vai para os {b}% que levam mais de 2 dias.", True)
    # Z4
    if meses:
        r, tp = meses.get("resumo", {}), meses["tipo"]
        faixa = lambda x, y: f"{x}%" if x == y else f"de {x}% a {y}%"
        if tp == "raro":
            achado("O prazo se mantém", "todo mês", f"só {faixa(r['b0'], r['b1'])} passam de 2 dias.", False)
        elif tp == "padrao":
            com = [m for m in meses["meses"] if not m.get("vazio") and m["n"]]
            cresce = (len(com) >= 6 and sum(m["n"] for m in com[-3:]) >= VOLUME_CRESCE * sum(m["n"] for m in com[:3]))
            achado("Não é crise, é padrão", "todo mês",
                   f"{faixa(r['b0'], r['b1'])} passam de 2 dias" + (", mesmo com o volume crescendo." if cresce else "."), True)
        elif tp == "picos":
            achado("No geral, é padrão", "quase todo mês",
                   f"{faixa(r['b0'], r['b1'])} passam de 2 dias; só {r['nomes']} {r['verbo']}.", True)
        else:
            d = faixa(r["d0"], r["d1"])
            achado("Há meses mais pesados", r["curto"], f"{d[0].upper() + d[1:]} passam de 2 dias, contra {r['contra']} "
                   "no resto do ano.", True, leitor_valor=r["quando"])
    # Z5
    s1 = s2 = None
    if trava:
        ordem = trava["status"]
        s1, s2 = ordem[0], (ordem[1] if len(ordem) > 1 else None)
        ph = trava.get("pct_horas")
        base = f"do tempo travado ({ph}% de todas as horas)" if ph is not None else "do tempo travado"
        if trava["tipo"] == "um" or s2 is None:
            achado("Trava em um ponto", f"{s1['pct']}%", f"{base} fica em um status: {_status_txt(s1)}.", True)
        elif trava["tipo"] == "espalhado":
            achado("Trava espalhado", f"{s1['pct'] + s2['pct']}%",
                   f"é o que somam os dois maiores pontos, {_status_txt(s1)} e {_status_txt(s2)}.", True)
        else:
            achado("Trava em dois pontos", f"{s1['pct'] + s2['pct']}%",
                   f"{base} fica em dois status: {_status_txt(s1)} e {_status_txt(s2)}.", True)
    # Z6
    tipo_fila = None
    if tipos and tipos["tipo"] in ("destaque", "parecido"):
        g = tipos["geral"]["b"]
        pior = next((r for r in tipos["linhas"] if r["destaque"]), None)
        if pior:
            etapa = pior["trava"]["etapa"] if pior["trava"] else None
            onde = ("" if not etapa else "; é onde outros status mais pesam." if etapa == OUTRAS
                    else f"; é onde a {etapa.lower()} mais pesa.")
            achado(f"Pesa mais no {pior['tipo']}", f"{pior['b']}%", f"dos pedidos {pior['tipo']} passam de 2 dias{onde or '.'}",
                   True)
            tipo_fila = pior["tipo"] if etapa == "Fila de entrada" else None
        else:
            maior = tipos["grupos"][0]["linhas"] if tipos["grupos"] and tipos["grupos"][0]["chave"] == "maior" else tipos["linhas"]
            bs = sorted(r["b"] for r in maior)
            verm = [r["tipo"] for r in tipos["linhas"] if r["vermelho"]]
            valor = f"{bs[0]}%" if bs[0] == bs[-1] else f"{bs[0]}–{bs[-1]}%"
            um = len(maior) == 1
            achado(f"O {maior[0]['tipo']} segue o geral" if um else "Os tipos se parecem", valor,
                   (f"dos pedidos {maior[0]['tipo']}" if um else "nos tipos de maior volume")
                   + f" passam de 2 dias, perto dos {g}% do geral."
                   + (f" Exceção: {_lista(verm)}." if verm else ""), bool(verm))

    # Z7
    olhar = []
    for s in [x for x in (s1, s2) if x and x.get("travado", x["pct"]) > 0]:  # Z7: só status que travaram
        olhar.append({"titulo": _status_txt(s), "texto": _pergunta(s["etapa"], s["nome"], tipo_fila)})
    n5 = int((h > CAUDA_H).sum())
    p5 = _pontos(n5 / len(h))
    olhar.append({"titulo": "Pedidos acima de 5 dias",
                  "texto": (f"São {_pct(p5)} ({_orcamentos(n5).replace('orçamento', 'pedido')}). Abrir caso a caso e "
                            "achar o que eles têm em comum.") if n5 else "Nenhum pedido passa de 5 dias de trabalho."})
    return {"n": len(h), "achados": achados, "olhar": olhar, "acima5": p5, "n_acima5": n5,
            "pede": ("Agir nos poucos pedidos que travam, <strong>no momento em que travam</strong>. Para isso, o Monday "
                     "precisa mostrar em que etapa cada pedido está e há quanto tempo. <em>E isso depende de como usamos "
                     "o Monday.</em>")}
