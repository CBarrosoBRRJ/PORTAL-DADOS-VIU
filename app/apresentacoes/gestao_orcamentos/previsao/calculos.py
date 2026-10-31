"""Previsão de demanda (D56, 26/10/2026; revisa a D48 e a D55): quantos pedidos (cards) devem entrar por mês — uma série e
um modelo por recorte (Inbound, Mercado, Mercado exclusivos, Mercado não exclusivos), acompanhamento mensal de 2026.

A página só lê o JSON gravado pelo job de ML (ml/saida/previsao.json, contrato v3 em ml/previsao.py); não importa nada
de ml/ nem as bibliotecas de ML. Sem o arquivo (ou com outra versão do contrato), a tela mostra a máscara.

P1  Séries (D56): Inbound e Mercado = pedidos que entraram por mês na gold de entradas (quantidade +
    quantidade_estimada, regra E1); Mercado exclusivos e Mercado não exclusivos = gold
    `gld_agenciamento_2026_previsao_exclusividade_mensal` (critério de talentos da gold). Cada série tem o seu modelo, treinado só nela (nada é repartido por proporção).
P2  Teste: jun, jul, ago e set/2026, cada mês previsto no fim do mês anterior (horizonte 1). O gráfico mostra esses 4
    pontos (marcador vazio) sobre o real; o erro da tela é o WAPE desses 4 meses.
P3  Modelo de cada série = o de menor erro no teste (empate < 1 ponto = o mais simples), escolhido no ml/previsao.py.
P4  Filtros (D56): Todos = Inbound | Mercado; Exclusivos = Inbound (todo ele é de talento exclusivo) | Mercado
    exclusivos; Não exclusivos = Inbound "não se aplica" | Mercado não exclusivos. O Mercado fica sempre à direita.
P5  Sem confiança: média da série no teste abaixo de 30 pedidos/mês ou erro acima de 40% — a tela diz "poucos pedidos
    para prever com confiança" (ou "erro alto demais") no lugar do número; o erro aparece mesmo assim.
P6  Execução mensal: o retrato (modelos e previsões) é refeito quando um mês fecha; o mês em andamento mostra a
    previsão de fechamento do retrato e o realizado até a véspera da carga (acompanhamento, atualizado a cada carga).
P7  Eixo fixo jan–dez/2026: meses sem dado ficam vazios até a previsão; nada de 2024/2025 na tela.
P8  Métricas (iguais à régua R3): WAPE = Σ|previsto − real| ÷ Σ real ("errou X%"); MAE em pedidos por mês.
P9  Pé do gráfico: o erro no teste jun–set (onde o modelo foi escolhido, otimista) e na verificação jan–mai (fora da
    escolha), com o que erraria repetir o último mês; série curta (só 2026) = "sem verificação · confiança menor";
    vencedor que perde da ingênua fora do teste = "não robusto" (C5 do contrato).
P10 Cartões de mês (D56 item 4): sempre o MÊS VIGENTE + os 2 SEGUINTES, a partir da data da carga (vigente = o mês do
    dia seguinte a `dados_ate`, regra E3). Vigente: realizado até a véspera da carga, previsão de fechamento do retrato
    e a situação: esperado até agora = previsão × dias úteis decorridos ÷ dias úteis do mês; "abaixo"/"acima" quando
    o realizado sai da faixa provável na mesma proporção (p10 e p90 × a fração), senão "dentro da faixa"; o % é
    realizado ÷ esperado − 1. Os dois seguintes: previsão com a faixa. Mês sem previsão no retrato (carga de um mês
    que ainda não tem retrato) = "aguardando o retrato".
P11 Por quê do mês vigente (D56 item 3): quando o vigente sai da faixa, uma linha com o diagnóstico S6 do contrato —
    pedidos em lote (3 ou mais da mesma marca no mesmo dia) e avulsos até o mesmo dia do mês, contra a média dos meses
    fechados anteriores. Nos recortes de exclusividade, os pedidos do mês ainda sem talento informado (fora dos dois).
P12 Diálogo "Modelos comparados" (D56 item 4): <dialog> nativo com todos os modelos testados nas séries do filtro, por
    família, com o erro no teste e na verificação; vencedor e alternativa robusta marcados; "não se aplica" com o
    motivo no title. Sem painel lateral (D55).
"""

import json
import hashlib
import math
import re
import threading
from pathlib import Path

import pandas as pd

from app import config, formato

VERSAO = 3
ANO = 2026
GRUPOS = {"todos": ("Todos", "todos"), "exclusivos": ("Exclusivos", "exclusivos"),
          "nao-exclusivos": ("Não exclusivos", "nao_exclusivos")}
DE_QUEM = {"todos": "", "exclusivos": " nos talentos exclusivos", "nao-exclusivos": " nos talentos não exclusivos"}
RECORTE_TXT = {"Inbound": "", "Mercado": "", "Mercado exclusivos": "talentos exclusivos",
               "Mercado não exclusivos": "talentos não exclusivos"}
TIPOS = ("Inbound", "Mercado")

_cache: dict = {}
_trava = threading.Lock()


# ---------------------------------------------------------------- leitura do contrato

def _valido(p) -> bool:
    try:
        return (p.get("versao") == VERSAO and "mes_fechado" in p["retrato"] and "processado_em" in p["carga"]
                and all(len(s["futuro"]) >= 1 for s in p["series"].values()) and set(p["filtros"]) == set(
                    x[1] for x in GRUPOS.values()))
    except (AttributeError, KeyError, TypeError):
        return False


def ler(caminho: Path | None = None) -> dict | None:
    """Último previsao.json válido, identificado pelo conteúdo; None sem arquivo ou com contrato diferente."""
    arq = Path(caminho or config.PREVISAO_ARQ)
    try:
        conteudo = arq.read_bytes()
        marca = hashlib.sha256(conteudo).digest()  # mesmo tamanho e timestamp não garantem o mesmo conteúdo
    except OSError:
        return None
    with _trava:
        if _cache.get("chave") == (str(arq), marca):
            return _cache["dados"]
    try:
        p = json.loads(conteudo)
    except (OSError, ValueError):
        return _cache.get("dados") if _cache.get("arquivo") == str(arq) else None  # gravação em curso: o anterior
    p = p if _valido(p) else None
    with _trava:
        _cache.update(chave=(str(arq), marca), dados=p, arquivo=str(arq))
    return p


def coerencia(p: dict | None, base_processado_em) -> dict | None:
    """F03 (auditoria do Codex, 31/10/2026): o retrato e o acompanhamento do previsao.json têm data própria; aqui eles
    são comparados com a carga da base que a página mostra no rodapé (a gold de entradas, ou a base congelada). Devolve
    o "acompanhamento até dd/mm" para o rodapé e, se alguma das duas peças vier de outra carga (dia do `processado_em`
    em São Paulo, regra E3), um aviso curto. None sem previsão. A mesma regra reprova o `congelar_base.py --conferir`."""
    if not p:
        return None
    from app import corte  # import tardio: só esta função usa a regra E3

    base = corte.dia_da_carga(base_processado_em) if base_processado_em is not None else None
    retrato = corte.dia_da_carga((p.get("carga") or {}).get("processado_em"))
    ac = p.get("acompanhamento") or {}
    acompanhamento = corte.dia_da_carga(ac.get("processado_em"))
    divergentes = {}
    if base and retrato and retrato != base:
        divergentes["retrato"] = retrato
    if base and acompanhamento and acompanhamento != base:
        divergentes["acompanhamento"] = acompanhamento
    aviso = None
    if divergentes:
        nomes = " e ".join(("previsão" if k == "retrato" else "acompanhamento") for k in divergentes)
        datas = " e ".join(sorted({d.strftime("%d/%m/%Y") for d in divergentes.values()}))
        aviso = f"{nomes} de outra carga ({datas})"
    ate = pd.Timestamp(ac["ate"]).strftime("%d/%m") if ac.get("ate") else None
    return {"base": base, "retrato": retrato, "acompanhamento": acompanhamento, "acompanhamento_ate": ate,
            "divergentes": divergentes, "aviso": aviso}


# ---------------------------------------------------------------- regras

def _per(m: str) -> pd.Period:
    return pd.Period(m, "M")


def _ano(m: str) -> str:
    """G1-N11: mês de outro ano que não o do gráfico leva o ano ("jan/27")."""
    return "" if m[:4] == str(ANO) else f"/{m[2:4]}"


def _mes_nome(m: str) -> str:
    return formato.MESES_EXTENSO[int(m[5:]) - 1] + _ano(m)


def _curto(m: str) -> str:
    return formato.MESES[int(m[5:]) - 1] + _ano(m)


def chave_css(serie: str) -> str:
    return {"Inbound": "inbound", "Mercado": "mercado", "Mercado exclusivos": "mercado-excl",
            "Mercado não exclusivos": "mercado-nao-excl"}.get(serie, "serie")


def teste_h1(backtest: list[dict]) -> list[dict]:
    """P2: os pares do teste (jun–set/2026, horizonte 1)."""
    return sorted((b for b in backtest if b.get("trecho") == "teste" and b["horizonte"] == 1), key=lambda b: b["alvo"])


def metricas(pares: list[dict]) -> dict | None:
    """P8 sobre pares {real, valor} (a mesma conta da régua R3)."""
    if not pares:
        return None
    soma = sum(x["real"] for x in pares)
    erro = [x["valor"] - x["real"] for x in pares]
    return {"wape": sum(map(abs, erro)) / soma if soma else None, "mae": sum(map(abs, erro)) / len(pares),
            "vies": sum(erro) / soma if soma else None, "n": len(pares)}


def mes_vigente(dados_ate) -> str:
    """P10: o mês em andamento na data da carga = o mês do dia seguinte a `dados_ate` (E3)."""
    return str((pd.Timestamp(dados_ate).normalize() + pd.Timedelta(days=1)).to_period("M"))


def meses_dos_cartoes(dados_ate) -> list[str]:
    """P10: o mês vigente e os dois seguintes."""
    v = _per(mes_vigente(dados_ate))
    return [str(v + k) for k in range(3)]


def situacao(realizado: float, x: dict | None, decorridos: int, total: int) -> dict | None:
    """P10: o realizado do mês vigente contra o esperado até agora (previsão × dias úteis decorridos ÷ do mês)."""
    if not x or realizado is None or not total:
        return None
    fracao = decorridos / total
    esperado = x["valor"] * fracao
    if esperado <= 0:
        return None
    delta = realizado / esperado - 1
    lo = x["p10"] * fracao if x.get("p10") is not None else None
    hi = x["p90"] * fracao if x.get("p90") is not None else None
    if lo is not None and hi is not None:
        lugar = "abaixo" if realizado < lo else "acima" if realizado > hi else "dentro"
    else:
        lugar = "abaixo" if delta <= -0.10 else "acima" if delta >= 0.10 else "dentro"
    return {"fracao": fracao, "esperado": esperado, "delta": delta, "lugar": lugar,
            "faixa": (lo, hi) if lo is not None else None, "sentido": formato.sentido(delta)}


# ---------------------------------------------------------------- gráfico (SVG; textos de 13 unidades = ≥ 11 px reais)

W, H = 340, 250            # largura estreita (celular, uma coluna)
W_LARGO, H_LARGO = 480, 250  # duas colunas (proporção ~1,9: telas de 1280 a 1600)
W_XL, H_XL = 620, 250        # duas colunas em telas largas (cartão do gráfico com 640 px ou mais: 1850 e 1920)
ESQ, DIR, TOPO, PE = 34, 6, 24, 22


def _teto(v: float) -> tuple[float, float]:
    """Topo "redondo" do eixo e o passo das linhas de grade (até 4 faixas)."""
    v = max(v, 1.0)
    for passo in sorted(k * 10 ** e for e in range(5) for k in (1, 2, 2.5, 5)):
        if v / passo <= 4:
            return math.ceil(v / passo) * passo, passo
    return v, v / 4


def grafico(f: dict, acompanhamento: dict | None, mes_fechado: str, prefixo: str, mostra_previsao: bool,
            w: int = W, h: int = H) -> dict:
    """Geometria de um gráfico (P7): eixo jan–dez/2026; colunas do real, pontos vazios do teste (P2), mês em andamento
    hachurado e a previsão com a faixa (só se `mostra_previsao`, P5)."""
    meses = [str(m) for m in pd.period_range(f"{ANO}-01", f"{ANO}-12", freq="M")]
    hist = {m: v for m, v in f["historico"].items() if m.startswith(str(ANO))}
    teste = {b["alvo"]: b for b in teste_h1(f["backtest"])} if mostra_previsao else {}
    futuro = {x["mes"]: x for x in f["futuro"]} if mostra_previsao else {}
    mes_and = acompanhamento["mes"] if acompanhamento else None
    parcial = acompanhamento.get("valor") if acompanhamento else None
    unidade = (w - ESQ - DIR) / len(meses)
    altura = h - TOPO - PE
    valores = (list(hist.values()) + [b["valor"] for b in teste.values()]
               + [x.get("p90") or x["valor"] for x in futuro.values()] + [parcial or 0])
    topo, passo = _teto(max(valores or [1]))

    def y(v):
        return round(TOPO + altura * (1 - v / topo), 1)

    base = TOPO + altura
    grade = [{"y": y(i * passo), "t": formato.inteiro(i * passo)} for i in range(int(round(topo / passo)) + 1)]
    barra = unidade * 0.6
    colunas, pontos, faixas, rotulos, linha = [], [], [], [], []
    for i, m in enumerate(meses):
        cx = round(ESQ + unidade * (i + 0.5), 1)
        x0 = round(cx - barra / 2, 1)
        nome = _curto(m)
        rotulos.append({"x": cx, "t": nome})
        if m in hist and m <= mes_fechado:
            v = hist[m]
            colunas.append({"x": x0, "y": y(v), "w": round(barra, 1), "h": round(base - y(v), 1), "classe": "pv-real",
                            "dica": f"{nome}/{ANO}: {formato.inteiro(v)} pedidos"})
        if m == mes_and and parcial is not None:
            colunas.append({"x": x0, "y": y(parcial), "w": round(barra, 1), "h": round(base - y(parcial), 1),
                            "classe": "pv-real-parcial", "dica": f"{nome}/{ANO}: {formato.inteiro(parcial)} até agora"})
        if m in teste:
            b = teste[m]
            pontos.append({"cx": cx, "cy": y(b["valor"]), "classe": "pv-prev",
                           "dica": f"{nome}/{ANO}: previsto no fim do mês anterior {formato.inteiro(b['valor'])}, "
                                   f"entraram {formato.inteiro(b['real'])}"})
        if m in futuro:
            x = futuro[m]
            if x.get("p10") is not None and x.get("p90") is not None:
                faixas.append({"x": round(cx - unidade * 0.4, 1), "w": round(unidade * 0.8, 1), "y": y(x["p90"]),
                               "h": round(max(y(x["p10"]) - y(x["p90"]), 0), 1)})
            linha.append(f"{cx},{y(x['valor'])}")
            pontos.append({"cx": cx, "cy": y(x["valor"]), "classe": "pv-fut",
                           "dica": f"{nome}/{ANO}: previsão {formato.inteiro(x['valor'])}"
                                   + (f" (faixa {formato.inteiro(x['p10'])} a {formato.inteiro(x['p90'])})"
                                      if x.get("p10") is not None else "")})
    if linha and mes_fechado in hist:  # a linha da previsão sai do último mês fechado
        i = meses.index(mes_fechado)
        linha.insert(0, f"{round(ESQ + unidade * (i + 0.5), 1)},{y(hist[mes_fechado])}")

    def zona(ini, fim, texto):
        if ini not in meses or fim not in meses:
            return None
        a, b = meses.index(ini), meses.index(fim)
        return {"x": round(ESQ + unidade * a, 1), "w": round(unidade * (b - a + 1), 1), "t": texto,
                "tx": round(ESQ + unidade * (a + b + 1) / 2, 1)}

    zonas = []
    if teste:
        zonas.append(zona(min(teste), max(teste), "teste"))
    if futuro:
        zonas.append(zona(min(futuro), max(futuro), "previsão"))
    return {"w": w, "h": h, "esq": ESQ, "dir": w - DIR, "base": base, "topo_y": TOPO, "grade": grade, "colunas": colunas,
            "pontos": pontos, "faixas": faixas, "linha": " ".join(linha) if len(linha) > 1 else "", "rotulos": rotulos,
            "zonas": [z for z in zonas if z], "y_mes": base + 16, "prefixo": prefixo}


# ---------------------------------------------------------------- tela

def _cartoes_mes(s: dict, ac: dict | None, dados_ate) -> list[dict]:
    """P10: mês vigente + 2 seguintes a partir da data da carga."""
    fut = {x["mes"]: x for x in s["futuro"]}
    saida = []
    for i, m in enumerate(meses_dos_cartoes(dados_ate)):
        x = fut.get(m)
        c = {"mes": m, "rotulo": _mes_nome(m), "curto": _curto(m), "vigente": i == 0, "valor": x and x["valor"],
             "p10": x and x.get("p10"), "p90": x and x.get("p90"), "sem_previsao": x is None, "realizado": None,
             "situacao": None, "barra": None}
        if i == 0 and ac and ac.get("mes") == m and s["nome"] in (ac.get("pedidos") or {}):
            c["realizado"] = ac["pedidos"][s["nome"]]
            c["situacao"] = situacao(c["realizado"], x, ac["dias_uteis_decorridos"], ac["dias_uteis_mes"])
            if x and x["valor"] > 0:
                c["barra"] = {"cheio": round(min(c["realizado"] / x["valor"], 1) * 100, 1),
                              "marca": round(ac["dias_uteis_decorridos"] / ac["dias_uteis_mes"] * 100, 1)}
        saida.append(c)
    return saida


def _por_que(s: dict, ac: dict | None, vig: dict) -> str | None:
    """P11: o diagnóstico S6 (lotes e avulsos até o mesmo dia do mês) quando o vigente sai da faixa."""
    if not ac or not vig.get("situacao") or vig["situacao"]["lugar"] == "dentro":
        return None
    d = (ac.get("lotes") or {}).get(s["nome"])
    if not d:
        return None
    va, me = d["vigente"], d["media_anteriores"]
    ant = d["meses_anteriores"]
    periodo = f"{_curto(ant[0])}–{_curto(ant[-1])}" if ant else "meses anteriores"
    return (f"Até o dia {d['ate_dia']}: {formato.inteiro(va['em_lote'])} pedidos em lote (média de {periodo}: "
            f"{formato.inteiro(me['em_lote'])}) e {formato.inteiro(va['avulsos'])} avulsos ({formato.inteiro(me['avulsos'])})")


def _coluna(p: dict, item: dict) -> dict:
    if item.get("serie") is None:  # P4: Inbound não exclusivo não existe (erro de cadastro, PD24)
        return {"nao_se_aplica": True, "titulo": item.get("tipo", ""), "recorte": "", "texto": item["nao_se_aplica"],
                "chave": chave_css(item.get("tipo", "")), "serie": None}
    s = p["series"][item["serie"]]
    ac = p.get("acompanhamento")
    acomp = None
    if ac and s["nome"] in (ac.get("pedidos") or {}):
        acomp = {"mes": ac["mes"], "valor": ac["pedidos"][s["nome"]]}
    mt = metricas(teste_h1(s["backtest"]))
    confiavel = s.get("confiavel", True)
    meses = _cartoes_mes(s, ac, p["carga"]["dados_ate"])
    teste = {b["alvo"]: b for b in teste_h1(s["backtest"])}
    fut = {x["mes"]: x for x in s["futuro"]}
    acessivel = []
    for m in map(str, pd.period_range(f"{ANO}-01", f"{ANO}-12", freq="M")):
        acessivel.append({"mes": f"{_curto(m)}/{ANO}", "real": s["historico"].get(m) if m <= p["retrato"]["mes_fechado"] else None,
                          "previsto": teste[m]["valor"] if m in teste and confiavel else None,
                          "parcial": acomp["valor"] if acomp and m == acomp["mes"] else None,
                          "futuro": fut.get(m) if confiavel else None})
    verif = s["metricas"].get("verificacao") or {}
    ing = s.get("ingenua") or {}
    maes = sorted(round(x["mae"]) for x in (mt, verif) if x and x.get("mae") is not None)
    sem_talento = None
    if s.get("grupo") and ac and (ac.get("sem_talento") or {}).get(s["tipo"]):
        sem_talento = ac["sem_talento"][s["tipo"]]
    chave = chave_css(s["nome"])
    return {
        "nao_se_aplica": False, "serie": s["nome"], "chave": chave, "titulo": s["tipo"] or s["nome"],
        "recorte": item.get("nota") or RECORTE_TXT.get(s["nome"], ""), "curta": s.get("curta", False),
        "modelo": s["modelo"], "modelo_txt": s["rotulo"], "familia": s.get("familia"), "fonte": s.get("fonte"),
        "meses": meses, "por_que": _por_que(s, ac, meses[0]), "sem_talento": sem_talento,
        "metricas": mt, "verificacao": verif if verif.get("wape") is not None else None,
        "ingenua": ing if ing.get("wape") is not None else None, "mae_faixa": maes,
        "robustez": s.get("robustez") or {}, "confiavel": confiavel, "poucos": s.get("poucos", False),
        "erro_alto": s.get("erro_alto", False), "media_teste": s.get("media_teste"),
        "grafico": grafico(s, acomp, p["retrato"]["mes_fechado"], f"pv-{chave}-l", confiavel, W_LARGO, H_LARGO),
        "grafico_estreito": grafico(s, acomp, p["retrato"]["mes_fechado"], f"pv-{chave}-e", confiavel),
        "grafico_xl": grafico(s, acomp, p["retrato"]["mes_fechado"], f"pv-{chave}-x", confiavel, W_XL, H_XL),
        "acessivel": acessivel,
    }


def motivo_curto(motivo: str | None) -> str | None:
    """P12: o motivo do "não se aplica" em poucas palavras (o texto inteiro fica no resultados.json e na ficha)."""
    if not motivo:
        return motivo
    m = re.search(r"precisa de (\d+) meses de treino; a série tem (\d+)", motivo)
    if m:
        return f"pede {m.group(1)} meses de treino; a série tem {m.group(2)}"
    if "sazonalidade anual" in motivo:
        return "pede 24 meses (sazonalidade anual)"
    if "mesmo mês do ano anterior" in motivo:
        return "pede 15 meses (mesmo mês do ano anterior)"
    return motivo if len(motivo) <= 80 else motivo[:79] + "…"


def dialogo(p: dict, nomes: list[str]) -> dict:
    """P12: a tabela do diálogo — famílias (da mais simples à mais complexa) × modelos, com o erro no teste e na
    verificação em cada série do filtro. Família inteira sem resultado nas séries do filtro = uma linha só."""
    series = [p["series"][n] for n in nomes]
    familias, ordem = {}, []
    for s in series:
        for g in s["comparados"]:
            if g["modulo"] not in familias:
                familias[g["modulo"]] = {"familia": g["familia"], "linhas": {}}
                ordem.append(g["modulo"])
            for ln in g["linhas"]:
                familias[g["modulo"]]["linhas"].setdefault(ln["nome"], {"nome": ln["nome"], "rotulo": ln["rotulo"],
                                                                        "pos_hoc": ln["pos_hoc"], "valores": {}})
                familias[g["modulo"]]["linhas"][ln["nome"]]["valores"][s["nome"]] = ln
    saida = []
    for mod in ordem:
        f = familias[mod]
        linhas = []
        for ln in f["linhas"].values():
            vals = [ln["valores"].get(s["nome"], {}) for s in series]
            linhas.append({**ln, "celulas": [{"teste": v.get("teste"), "verificacao": v.get("verificacao"),
                                              "falta": v.get("falta"), "motivo": motivo_curto(v.get("motivo")),
                                              "vencedor": v.get("vencedor", False), "alternativa": v.get("alternativa", False),
                                              "ingenua": v.get("ingenua", False)} for v in vals],
                           "vencedor": any(v.get("vencedor") for v in vals),
                           "algum": any(v.get("teste") is not None for v in vals)})
        def media(x):  # ordem dentro da família: o erro médio no teste nas séries do filtro
            v = [c["teste"] for c in x["celulas"] if c["teste"] is not None]
            return sum(v) / len(v) if v else 9
        linhas.sort(key=lambda x: (not x["algum"], media(x), x["nome"]))
        com = [x for x in linhas if x["algum"]]
        sem = [x for x in linhas if not x["algum"]]
        motivos = sorted({c["motivo"] for x in sem for c in x["celulas"] if c.get("motivo")}, key=len)
        saida.append({"familia": f["familia"], "modulo": mod, "linhas": com,
                      "sem": {"n": len(sem), "nomes": ", ".join(x["rotulo"] for x in sem),
                              "motivo": " · ".join(motivos[:2])} if sem else None})
    resumo = []
    for s in series:
        r = s.get("robustez") or {}
        alt = r.get("alternativa")
        resumo.append({"serie": s["nome"], "modelo": s["rotulo"], "teste": s["metricas"]["1"]["wape"],
                       "verificacao": (s["metricas"].get("verificacao") or {}).get("wape"), "robusto": r.get("robusto"),
                       "texto": r.get("texto"), "curta": s.get("curta"), "n_modelos": s.get("n_modelos"),
                       "alternativa": alt and {"rotulo": alt["rotulo"], "teste": alt["teste"],
                                               "verificacao": alt["verificacao"]}})
    return {"series": [s["nome"] for s in series], "familias": saida, "resumo": resumo,
            "n_modelos": len(p.get("modelos") or [])}


def tela(p: dict | None, grupo: str = "todos") -> dict | None:
    """Contexto da página. None = sem previsão válida (máscara)."""
    if p is None:
        return None
    grupo = grupo if grupo in GRUPOS else "todos"
    itens = p["filtros"][GRUPOS[grupo][1]]
    colunas = [_coluna(p, i) for i in itens if i.get("serie") is None or i["serie"] in p["series"]]
    if not any(not c["nao_se_aplica"] for c in colunas):
        return None
    ac = p.get("acompanhamento")
    mes_fechado = p["retrato"]["mes_fechado"]
    teste = (p.get("regua") or {}).get("teste") or ["2026-06", "2026-09"]
    verif = (p.get("regua") or {}).get("verificacao") or ["2026-01", "2026-05"]
    return {
        "grupo": grupo, "de_quem": DE_QUEM[grupo], "colunas": colunas,
        "grupos": [{"chave": k, "rotulo": r, "atual": k == grupo} for k, (r, _) in GRUPOS.items()],
        "acompanhamento": ac and {**ac, "ate_txt": pd.Timestamp(ac["ate"]).strftime("%d/%m"), "rotulo": _mes_nome(ac["mes"])},
        "retrato": {**p["retrato"], "rotulo": _mes_nome(mes_fechado), "ate_txt": (_per(mes_fechado).end_time).strftime("%d/%m/%Y")},
        "carga": p["carga"], "gerado_em": pd.Timestamp(p["gerado_em"]).tz_convert(config.FUSO).to_pydatetime(),
        "teste_txt": f"{_curto(teste[0])}–{_curto(teste[1])}", "verificacao_txt": f"{_curto(verif[0])}–{_curto(verif[1])}",
        "janela": (p.get("regua") or {}).get("janela", 12), "decisao": p["decisao"],
        "dialogo": dialogo(p, [c["serie"] for c in colunas if not c["nao_se_aplica"]]),
    }
