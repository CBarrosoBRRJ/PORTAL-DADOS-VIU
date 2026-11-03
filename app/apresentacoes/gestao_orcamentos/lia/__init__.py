"""Slide LIA (V2, 30/10/2026; D-LIA-2 a D-LIA-5, pedidos do Caio): o que a LIA leu e como os e-mails se dividem.

Lê retrato.json, contagens agregadas que tools/extrair_lia.py tira do Cloud Storage da LIA (só leitura; exceção à D57).
Aqui só se somam, dividem e comparam as contagens do retrato; regras e conferência na ficha docs/paginas/lia.md.
D-LIA-4: o extrato de cada semana (clique ou ?semana=NN) foi retirado por decisão do Caio, 30/10/2026 (_descartados/2026-10-30/).
D-LIA-5: no lugar de destaques por data, padrões do mercado — dia da semana (dias úteis sem feriado, teste de permutação)
e período do dia (manhã, tarde, noite; qui-quadrado), com o mapa dia × período.
A versão com duas visões está em _descartados/2026-10-30/; a análise de tempo na régua do SLA ficou só na ficha (D-LIA-1).
"""

import json
import math
from datetime import date, datetime
from pathlib import Path

import numpy as np

from app.apresentacoes.gestao_orcamentos import lia_na_pratica
from app.formato import decimal, inteiro, pct

RETRATO = Path(__file__).with_name("retrato.json")
# premissa da estimativa de tempo devolvido (a confirmar com a equipe): minutos que a equipe gastaria para abrir, ler e
# descartar um e-mail que não é oportunidade. Mude aqui; a tela e a ficha dizem que é estimativa
MINUTOS_TRIAGEM = 2
HORAS_DIA = 8  # dia de trabalho do portal (C5 do SLA: 10h–13h + 14h–19h)
FORA = ("almoco", "noite", "fim_de_semana", "feriado")  # faixas fora do expediente (extrair_lia.py::faixa)
# uma ordem só para a barra de fração, a pilha das semanas (de baixo para cima), a legenda e a dica
CATEGORIAS = (("nao_lead", "Não lead", "a LIA garantiu que não era lead"),
              ("lead", "Lead", "virou lead no monday"),
              ("validacao", "Validação", "seguiu para análise da equipe"))
# D-LIA-5: períodos do dia pela hora do processamento (extrair_lia.py::periodo); a noite tem 12 h (18h às 6h)
PERIODOS = (("manha", "Manhã", "6h–12h"), ("tarde", "Tarde", "12h–18h"), ("noite", "Noite", "18h–6h"))
ROTULO_MIN = 0.06  # número escrito dentro da parte da pilha só com altura ≥ 6% da coluna mais alta
DIAS_SEMANA = ("segunda", "terça", "quarta", "quinta", "sexta", "sábado", "domingo")
DIAS_CURTO = ("Seg", "Ter", "Qua", "Qui", "Sex")
PERMUTACOES, SEMENTE = 3000, 2026  # teste de permutação do dia da semana (fixo: a tela não muda a cada visita)
ALFA = 0.05  # abaixo disso, padrão claro ("costuma"); entre ALFA e 0,10, "tendência"; acima, "sem diferença clara"


def _dm(d: date) -> str:
    return f"{d.day:02d}/{d.month:02d}"


def _periodo(ini: date, fim: date) -> str:
    """"21–27/09" no mesmo mês; "28/09–04/10" quando vira o mês."""
    return f"{ini.day:02d}–{_dm(fim)}" if ini.month == fim.month else f"{_dm(ini)}–{_dm(fim)}"


def _soma(x: dict) -> int:
    return sum(x[k] for k, _, _ in CATEGORIAS)


def _maior_resto(valores: list[int], total: int, alvo: int, escala: int = 100) -> list[int]:
    """Maior resto (03/11/2026; as partes arredondadas uma a uma somavam 101%): cota de cada valor = valor ÷ total × escala;
    cada parte leva a parte inteira da cota e as `alvo − Σ partes inteiras` unidades que faltam vão para os maiores restos
    (empate: a ordem da lista). alvo = escala fecha o todo; alvo menor reparte um subtotal já arredondado (um lado do
    expediente). escala 1000 = décimos de ponto percentual. Total zero → zeros."""
    if not total:
        return [0] * len(valores)
    base = [v * escala // total for v in valores]
    falta = alvo - sum(base)
    if not 0 <= falta <= len(valores):
        raise ValueError(f"alvo {alvo} fora do alcance das cotas {valores} de {total}")
    for i in sorted(range(len(valores)), key=lambda i: -(valores[i] * escala % total))[:falta]:
        base[i] += 1
    return base


def _pct_partes(valores: list[int], casas: int = 0) -> list[str]:
    """Percentuais de partes que somam o todo, já escritos ('74%', '86,8%') e fechando em 100 pelo maior resto."""
    escala = 100 * 10 ** casas
    total = sum(valores)
    if not total:
        return ["—"] * len(valores)
    return [pct(x / escala, casas) for x in _maior_resto(valores, total, escala, escala)]


def _pct_lados(n: dict, dentro: tuple, fora: tuple) -> tuple[dict, int, int]:
    """Percentuais inteiros em dois níveis que fecham entre si: dentro + fora = 100 (maior resto no par) e as faixas de
    cada lado somam o percentual do lado (maior resto dentro do lado). Devolve ({faixa: %}, % dentro, % fora)."""
    total = sum(n[k] for k in dentro + fora)
    if not total:
        return {k: 0 for k in dentro + fora}, 0, 0
    pd_, pf = _maior_resto([sum(n[k] for k in dentro), sum(n[k] for k in fora)], total, 100)
    por = dict(zip(dentro, _maior_resto([n[k] for k in dentro], total, pd_)))
    por.update(zip(fora, _maior_resto([n[k] for k in fora], total, pf)))
    return por, pd_, pf


def _fracao(c: dict) -> list[dict]:
    n = _soma(c)
    pcts = _pct_partes([c[k] for k, _, _ in CATEGORIAS], 1)  # 03/11/2026: as três fecham em 100,0%
    return [{"chave": k, "nome": nome, "sub": sub, "n": inteiro(c[k]), "pct": p,
             "largura": round(c[k] / n * 100, 3) if n else 0} for (k, nome, sub), p in zip(CATEGORIAS, pcts)]


def _fds(d: dict) -> bool:
    return d.get("fim_de_semana", date.fromisoformat(d["data"]).weekday() >= 5)


def _uteis(dias: list[dict]) -> list[dict]:
    """Dias úteis sem feriado (a regra dos padrões por dia da semana)."""
    return [d for d in dias if not d["feriado"] and not _fds(d)]


def _f(x: np.ndarray, g: np.ndarray) -> float:
    """Estatística F de um fator (variação entre os dias da semana ÷ variação dentro deles)."""
    ks = np.unique(g)
    media = x.mean()
    entre = sum((g == k).sum() * (x[g == k].mean() - media) ** 2 for k in ks) / (len(ks) - 1)
    dentro = sum(((x[g == k] - x[g == k].mean()) ** 2).sum() for k in ks) / (len(x) - len(ks))
    return entre / dentro if dentro else math.inf


def _leitura(p: float) -> str:
    return "claro" if p < ALFA else "tendencia" if p < 0.10 else "sem"


def padroes(r: dict) -> dict:
    """D-LIA-5: comportamento do mercado a partir do que a LIA leu.

    Dia da semana: média de leads e de e-mails por dia útil (sem o feriado), n de dias de cada; diferença entre os dias
    testada por permutação (embaralha o dia da semana entre os dias, estatística F, PERMUTACOES vezes). Fim de semana à
    parte. Período do dia: e-mails e leads de todos os dias por período; a taxa de lead por período comparada pelo
    qui-quadrado (2 graus de liberdade: p = exp(−χ²/2)); e em quantos dias úteis a tarde (ou o período líder) teve
    mais leads. Mapa: média de leads por dia útil em cada dia da semana × período (e a linha do fim de semana)."""
    uteis = _uteis(r["dias"])
    dow = np.array([date.fromisoformat(d["data"]).weekday() for d in uteis])
    leads = np.array([d["lead"] for d in uteis], float)
    mails = np.array([_soma(d) for d in uteis], float)
    rng = np.random.default_rng(SEMENTE)
    f_obs = _f(leads, dow)
    p_dia = float(np.mean([_f(leads, rng.permutation(dow)) >= f_obs for _ in range(PERMUTACOES)])) if len(uteis) > 5 else 1.0
    dias = []
    for k in sorted(set(dow.tolist())):
        m = dow == k
        dias.append({"k": k, "nome": DIAS_SEMANA[k], "curto": DIAS_CURTO[k], "n": int(m.sum()),
                     "leads": float(leads[m].mean()), "mails": float(mails[m].mean()),
                     "leads_txt": decimal(leads[m].mean()), "mails_txt": inteiro(mails[m].mean()),
                     # Caio, 30/10/2026: a tela mostra a média por dia arredondada para inteiro (as somas por dia da
                     # semana enganam: a janela tem 5 segundas e 6 terças); a barra usa o mesmo inteiro
                     "leads_int": math.floor(leads[m].mean() + 0.5), "leads_total": int(leads[m].sum()),
                     # 6ª rodada (Caio, 30/10/2026): o bloco "Quando o inbound chega" mostra e-mails (a LIA só vê inbound)
                     "mails_int": math.floor(mails[m].mean() + 0.5)})
    maior_int = max((d["leads_int"] for d in dias), default=0)
    maior_mails = max((d["mails_int"] for d in dias), default=0)
    for d in dias:
        d["largura"] = round(d["leads_int"] / maior_int * 100, 2) if maior_int else 0
        d["largura_mails"] = round(d["mails_int"] / maior_mails * 100, 2) if maior_mails else 0
    forte_mails = max(dias, key=lambda d: (d["mails"], -d["k"])) if dias else None
    forte = max(dias, key=lambda d: (d["leads"], -d["k"]))
    fraco = min(dias, key=lambda d: (d["leads"], d["k"]))
    fds = [d for d in r["dias"] if _fds(d) and not d["feriado"]]

    tot = {k: {c: sum(d["periodos"][k][c] for d in r["dias"]) for c, _, _ in CATEGORIAS} for k, _, _ in PERIODOS}
    total, total_leads = sum(_soma(v) for v in tot.values()), sum(v["lead"] for v in tot.values())
    obs = np.array([[tot[k]["lead"], _soma(tot[k]) - tot[k]["lead"]] for k, _, _ in PERIODOS], float)
    esp = obs.sum(1, keepdims=True) * obs.sum(0, keepdims=True) / obs.sum()
    chi2 = float(((obs - esp) ** 2 / np.where(esp > 0, esp, 1)).sum())
    p_per = math.exp(-chi2 / 2)
    pct_mails = _pct_partes([_soma(tot[k]) for k, _, _ in PERIODOS])  # 03/11/2026: as três fecham em 100%
    pct_leads = _pct_partes([tot[k]["lead"] for k, _, _ in PERIODOS])
    periodos = [{"chave": k, "nome": nome, "faixa": faixa, "mails": _soma(tot[k]), "leads": tot[k]["lead"],
                 "pct_mails": pct_mails[i], "pct_leads": pct_leads[i],
                 "taxa": tot[k]["lead"] / _soma(tot[k]) if _soma(tot[k]) else 0,
                 "taxa_txt": pct(tot[k]["lead"] / _soma(tot[k])) if _soma(tot[k]) else "—"}
                for i, (k, nome, faixa) in enumerate(PERIODOS)]
    for p in periodos:  # barras de 100% por período: dos leads e (6ª rodada) dos e-mails de inbound
        p["largura"] = round(p["leads"] / total_leads * 100, 3) if total_leads else 0
        p["largura_mails"] = round(p["mails"] / total * 100, 3) if total else 0
    lider = max(periodos, key=lambda p: p["leads"])
    lider_mails = max(periodos, key=lambda p: p["mails"])
    dias_lider = sum(1 for d in uteis if all(d["periodos"][lider["chave"]]["lead"] > d["periodos"][o]["lead"]
                                             for o, _, _ in PERIODOS if o != lider["chave"]))

    # mapa dia × período: média de leads por dia útil (sequencial em 5 tons, pela posição entre o menor e o maior)
    celulas = []
    for d in dias:
        m = [x for x in uteis if date.fromisoformat(x["data"]).weekday() == d["k"]]
        celulas.append({"rot": d["curto"], "nome": d["nome"], "n": d["n"], "fds": False,
                        "c": [(sum(x["periodos"][k]["lead"] for x in m) / len(m), sum(_soma(x["periodos"][k]) for x in m) / len(m))
                              for k, _, _ in PERIODOS]})
    if fds:
        celulas.append({"rot": "Sáb–dom", "nome": "sábado e domingo", "n": len(fds), "fds": True,
                        "c": [(sum(x["periodos"][k]["lead"] for x in fds) / len(fds), sum(_soma(x["periodos"][k]) for x in fds) / len(fds))
                              for k, _, _ in PERIODOS]})
    vals = [v for c in celulas for v, _ in c["c"]]
    lo, hi = min(vals), max(vals)
    for c in celulas:
        c["c"] = [{"leads": decimal(v), "mails": inteiro(e), "tom": min(4, int((v - lo) / (hi - lo) * 5)) if hi > lo else 0,
                   "per": PERIODOS[i][1].lower(),
                   "texto": f"{c['nome'].capitalize()}, {PERIODOS[i][1].lower()} ({PERIODOS[i][2]}): {decimal(v)} leads e "
                            f"{inteiro(e)} e-mails por dia, em média ({c['n']} dias)"} for i, (v, e) in enumerate(c["c"])]
    return {
        "dias": dias, "forte": forte, "fraco": fraco, "p_dia": p_dia, "leitura_dia": _leitura(p_dia),
        "n_min": min(d["n"] for d in dias), "n_max": max(d["n"] for d in dias), "n_uteis": len(uteis),
        "fds": {"n": len(fds), "leads": decimal(sum(d["lead"] for d in fds) / len(fds)) if fds else "—",
                "mails": inteiro(sum(_soma(d) for d in fds) / len(fds)) if fds else "—"},
        "uteis_leads": decimal(leads.mean()) if len(leads) else "—", "uteis_mails": inteiro(mails.mean()) if len(mails) else "—",
        "periodos": periodos, "lider": lider, "lider_mails": lider_mails, "forte_mails": forte_mails, "chi2": chi2, "p_periodo": p_per, "leitura_periodo": _leitura(p_per),
        "dias_lider": dias_lider, "total_leads": inteiro(total_leads),
        "outros": [p for p in periodos if p["chave"] != lider["chave"]], "mapa": celulas,
    }


# Caio, 30/10/2026: turnos alinhados ao expediente do SLA (seg–sex 10h–13h e 14h–19h; almoço 13h–14h, noite, fim de
# semana e feriado no "fora"). Vêm prontos do retrato (extrair_lia.py::turno) e somam o total. Não estão na tela: o
# "fora do expediente" da tela é o de FAIXAS_DIA (10h–19h com o almoço 12h–13h dentro, definição do Caio para a LIA)
TURNOS = (("manha", "Manhã", "10h–13h"), ("tarde", "Tarde", "14h–19h"), ("fora", "Fora", "do expediente"))
DIAS_REC = ((0, "Seg", "segunda"), (1, "Ter", "terça"), (2, "Qua", "quarta"), (3, "Qui", "quinta"), (4, "Sex", "sexta"),
            (5, "Sáb–dom", "sábado e domingo"))


# Caio, 30/10/2026: o dia em faixas, pela hora do processamento (retrato "horas"). Expediente da LIA por definição do
# Caio: 10h–19h em dias úteis, com o almoço (12h–13h) DENTRO; fora = antes das 10h, depois das 19h, fim de semana e
# feriado. Difere do SLA (10h–13h e 14h–19h, almoço 13h–14h fora); o SLA não muda. "Antes do expediente" = dias úteis 7h–10h
# (o mercado começa às 7h–8h; pelos dados, 6h e 7h ainda estão no nível da madrugada e o volume sobe às 8h); as partes fora
# do expediente (antes, noite e madrugada, fim de semana e feriado) somam o "fora do expediente" do bloco de cima
# (e["pct_fora"]; o percentual vem do retrato, não fica escrito aqui). Cor: expediente
# no azul escuro; fora em tons claros da mesma família (classes do portal)
FAIXAS_DIA = (("antes", "Antes do expediente", "Antes das 10h", "7h–10h", False),
              ("manha", "Manhã", "Manhã, 10h–12h", "10h–12h", True),
              ("almoco", "Almoço", "Almoço, 12h–13h", "12h–13h", True),
              ("tarde", "Tarde", "Tarde, 13h–19h", "13h–19h", True),
              ("noite", "Noite e madrugada", "Noite e madrugada", "19h–7h", False),
              ("fds", "Fim de semana e feriado", "Fim de semana e feriado", "o dia todo", False))

# barra única (Caio, 30/10/2026): reordenada em expediente | fora, para as duas chaves acima dela ficarem contínuas;
# rótulos curtos da legenda; expediente nos dois azuis escuros, fora nos tons claros da mesma família (classes do portal)
ORDEM_BARRA = ("manha", "almoco", "tarde", "antes", "noite", "fds")
CURTO = {"antes": "Antes das 10h", "manha": "10h–12h", "almoco": "Almoço", "tarde": "13h–19h", "noite": "Noite e madrugada",
         "fds": "Fim de semana e feriado"}
# cores das faixas (Caio, 30/10/2026: só os azuis do projeto, sem amarelo nem verde): rampa ordinal de um matiz, do mais
# escuro (10h–12h, --t-mercado) ao mais claro (fim de semana, --t-sem-tipo), com --t-inbound e três degraus intermediários;
# expediente nos dois mais escuros, fora nos mais claros. Validada como rampa ordinal na skill dataviz (monótona, degraus
# visíveis ΔL ≥ 0,06, ponta clara ≥ 2:1, um matiz): PASS. Classes em estilo.css
COR_BARRA = {k: f"lia-cf-{k}" for k in ("manha", "tarde", "antes", "almoco", "noite", "fds")}


LEGENDA = {"noite": "Noite", "fds": "Fim de semana"}  # rótulos curtos só na legenda (a dica e o leitor dizem o nome inteiro)


def _quadrantes(faixas: list[dict], total_ld: int, total_nl: int, total_v: int, lados: dict) -> dict:
    """Dois quadrantes com escala comum (Caio, 30/10/2026): o da esquerda mede a maior fatia "dentro do expediente" entre as
    três categorias, o da direita a maior fatia "fora"; o divisor fica no mesmo lugar nas três barras e as larguras
    continuam proporcionais (% de cada categoria). Dentro de cada quadrante, a largura é relativa ao quadrante.
    lados = _pct_lados de cada categoria (campos "leads", "nl", "v"): dentro + fora = 100% e as faixas de cada lado somam
    o lado (03/11/2026: leads 74% + 27% = 101% ao arredondar cada um sozinho)."""
    cats = (("l", "Leads", "leads", total_ld), ("n", "Não leads", "nl", total_nl), ("v", "Validação", "v", total_v))
    por_k = {f["chave"]: f for f in faixas}
    dentro = [k for k in ORDEM_BARRA if por_k[k]["expediente"]]
    fora = [k for k in ORDEM_BARRA if not por_k[k]["expediente"]]
    share = {c: {k: (por_k[k][campo] / tot if tot else 0) for k in ORDEM_BARRA} for c, _, campo, tot in cats}
    max_d = max(sum(share[c][k] for k in dentro) for c, *_ in cats) or 1
    max_f = max(sum(share[c][k] for k in fora) for c, *_ in cats) or 1
    linhas = []
    def seg(c: str, campo: str, tot: int, por: dict, k: str, base: float) -> dict:
        x = share[c][k]
        return {"chave": k, "id": f"lia-q-{c}-{k}", "cor": COR_BARRA[k], "curto": CURTO[k], "n_txt": inteiro(por_k[k][campo]),
                "pct": _txt_pct(por[k], tot), "w": round(x / base * 100, 3), "rotulo": x >= 0.08}

    for c, rot, campo, tot in cats:
        por, p_dentro, p_fora = lados[campo]
        linhas.append({"cat": c, "rot": rot, "total_txt": inteiro(tot), "val": c == "v",
                       "dentro": [seg(c, campo, tot, por, k, max_d) for k in dentro],
                       "fora": [seg(c, campo, tot, por, k, max_f) for k in fora],
                       "dentro_pct": _txt_pct(p_dentro, tot), "fora_pct": _txt_pct(p_fora, tot)})
    return {"esq": round(max_d / (max_d + max_f) * 100, 3), "dir": round(max_f / (max_d + max_f) * 100, 3), "linhas": linhas,
            "leg_dentro": [{"curto": LEGENDA.get(k, CURTO[k]), "cor": COR_BARRA[k]} for k in dentro],
            "leg_fora": [{"curto": LEGENDA.get(k, CURTO[k]), "cor": COR_BARRA[k]} for k in fora]}


def _txt_pct(p: int, total: int) -> str:
    """Percentual inteiro já fechado pelo maior resto, escrito para a tela; '—' sem base."""
    return pct(p / 100) if total else "—"


DENTRO_DIA = tuple(k for k in ORDEM_BARRA if next(f[4] for f in FAIXAS_DIA if f[0] == k))  # manhã, almoço, tarde
FORA_DIA = tuple(k for k in ORDEM_BARRA if k not in DENTRO_DIA)  # antes das 10h, noite e madrugada, fim de semana


def faixas_do_dia(r: dict) -> dict:
    """Os e-mails do período nas faixas de FAIXAS_DIA (somam o total); fora = as faixas fora do expediente."""
    h = r.get("horas")
    if not h:
        return {"faixas": [], "fora": None, "antes": None}
    def por_faixa(x: dict) -> dict:
        u = x["util"]
        return {"antes": sum(u[7:10]), "manha": sum(u[10:12]), "almoco": u[12], "tarde": sum(u[13:19]),
                "noite": sum(u[19:]) + sum(u[:7]), "fds": sum(x["fim_de_semana"]) + sum(x["feriado"])}
    n = por_faixa(h)
    # Caio, 30/10/2026: leads por faixa (retrato "horas_lead"); taxa = leads ÷ e-mails da faixa
    ld = por_faixa(r["horas_lead"]) if r.get("horas_lead") else None
    nl = por_faixa(r["horas_nao_lead"]) if r.get("horas_nao_lead") else None  # não leads por faixa
    total = sum(n.values())
    total_ld = sum(ld.values()) if ld else 0
    total_nl = sum(nl.values()) if nl else 0
    total_v = total - total_ld - total_nl if ld and nl else 0
    maior = max(n.values()) if n else 0
    # 03/11/2026: percentuais pelo maior resto em dois níveis (dentro + fora = 100%; faixas somam o seu lado), por categoria
    v = {k: n[k] - ld[k] - nl[k] for k in n} if ld and nl else None
    lados = {campo: _pct_lados(x, DENTRO_DIA, FORA_DIA) for campo, x in (("n", n), ("leads", ld), ("nl", nl), ("v", v)) if x}
    # lista na ordem do dia (Caio, 30/10/2026): mini barra proporcional à maior faixa; expediente no azul escuro, fora no pastel
    faixas = [{"chave": k, "nome": nome, "rotulo": rotulo, "faixa": faixa, "expediente": exp,
               "cor": "t-mercado" if exp else "t-sem-tipo", "n": n[k], "n_txt": inteiro(n[k]),
               "pct": _txt_pct(lados["n"][0][k], total), "largura": round(n[k] / total * 100, 3) if total else 0,
               "barra": round(n[k] / maior * 100, 2) if maior else 0}
              for k, nome, rotulo, faixa, exp in FAIXAS_DIA]
    fora = sum(f["n"] for f in faixas if not f["expediente"])
    por_chave = {f["chave"]: f for f in faixas}
    for f in faixas:
        k = f["chave"]
        f["leads"] = ld[k] if ld else None
        f["leads_txt"] = inteiro(ld[k]) if ld else "—"
        f["pct_leads"] = _txt_pct(lados["leads"][0][k], total_ld) if ld else "—"
        f["largura_leads"] = round(ld[k] / total_ld * 100, 3) if ld and total_ld else 0
        f["taxa"] = pct(ld[k] / n[k], 1) if ld and n[k] else "—"
        f["rotulo_dentro"] = f["largura"] >= 8  # % escrito dentro do segmento só quando cabe
        f["rotulo_dentro_leads"] = f["largura_leads"] >= 8
        f["nl"] = nl[k] if nl else None
        f["nl_txt"] = inteiro(nl[k]) if nl else "—"
        f["pct_nl"] = _txt_pct(lados["nl"][0][k], total_nl) if nl else "—"
        f["largura_nl"] = round(nl[k] / total_nl * 100, 3) if nl and total_nl else 0
        f["rotulo_dentro_nl"] = f["largura_nl"] >= 8
        # validação = e-mails − leads − não leads da faixa (as categorias se excluem)
        f["v"] = n[k] - ld[k] - nl[k] if ld and nl else None
        f["v_txt"] = inteiro(f["v"]) if f["v"] is not None else "—"
        f["pct_v"] = _txt_pct(lados["v"][0][k], total_v) if f["v"] is not None else "—"
        f["largura_v"] = round(f["v"] / total_v * 100, 3) if f["v"] is not None and total_v else 0
        f["rotulo_dentro_v"] = f["largura_v"] >= 10
    barra = [{**por_chave[k], "curto": CURTO[k], "cor": COR_BARRA[k]} for k in ORDEM_BARRA]
    fora_ld = sum(ld[f["chave"]] for f in faixas if not f["expediente"]) if ld else 0
    return {"faixas": faixas, "barra": barra, "total": total,
            "fora": {"n": fora, "n_txt": inteiro(fora), "pct": _txt_pct(lados["n"][2], total)},
            "dentro": {"n": total - fora, "n_txt": inteiro(total - fora), "pct": _txt_pct(lados["n"][1], total),
                       "largura": round((total - fora) / total * 100, 3) if total else 0},
            "fora_largura": round(fora / total * 100, 3) if total else 0,
            "leads": {"total": total_ld, "total_txt": inteiro(total_ld), "fora": fora_ld,
                      "fora_pct": _txt_pct(lados["leads"][2], total_ld),
                      "dentro_pct": _txt_pct(lados["leads"][1], total_ld),
                      "taxa": pct(total_ld / total, 1) if total else "—",
                      "dentro_largura": round((total_ld - fora_ld) / total_ld * 100, 3) if total_ld else 0} if ld else None,
            "validacao": {"total": total_v, "total_txt": inteiro(total_v)} if nl and ld else None,
            "quadrantes": _quadrantes(faixas, total_ld, total_nl, total_v, lados) if ld and nl else None,
            "nao_leads": {"total": total_nl, "total_txt": inteiro(total_nl),
                          "fora_pct": _txt_pct(lados["nl"][2], total_nl)} if nl else None,
            "antes": faixas[0]}


def recebimento(r: dict) -> dict:
    """Quando o inbound chega (Caio, 30/10/2026): os e-mails do período (todas as categorias) por turno do expediente e
    por dia da semana; as duas leituras somam o total. Dia da semana: total do período e média por dia (inteira), porque
    a janela tem números diferentes de cada dia (o feriado fica no dia em que caiu); a barra e o destaque usam a média."""
    t = r.get("turnos") or {}
    total = sum(_soma(v) for v in t.values())
    presentes = [x for x in TURNOS if x[0] in t]
    pcts = _pct_partes([_soma(t[k]) for k, _, _ in presentes])  # 03/11/2026: as partes fecham em 100%
    pcts_leads = _pct_partes([t[k]["lead"] for k, _, _ in presentes])
    turnos = [{"chave": k, "nome": nome, "faixa": faixa, "n": _soma(t[k]), "n_txt": inteiro(_soma(t[k])),
               "pct": pcts[i], "largura": round(_soma(t[k]) / total * 100, 3) if total else 0,
               "leads": t[k]["lead"], "pct_leads": pcts_leads[i]}
              for i, (k, nome, faixa) in enumerate(presentes)]
    grupos = {}
    for d in r["dias"]:
        k = min(date.fromisoformat(d["data"]).weekday(), 5)
        g = grupos.setdefault(k, [0, 0])
        g[0] += _soma(d)
        g[1] += 1
    dias = []
    for k, curto, nome in DIAS_REC:
        if k not in grupos:
            continue
        n_tot, n_dias = grupos[k]
        dias.append({"k": k, "curto": curto, "nome": nome, "total": n_tot, "total_txt": inteiro(n_tot), "n": n_dias,
                     "media": n_tot / n_dias, "media_int": math.floor(n_tot / n_dias + 0.5)})
    maior = max((d["media_int"] for d in dias), default=0)
    for d in dias:
        d["largura"] = round(d["media_int"] / maior * 100, 2) if maior else 0
    # Caio, 30/10/2026: de que é feito o "fora do expediente" (faixas do retrato; somam o fora), do maior para o menor
    fx = r.get("faixas", {})
    fora_partes = sorted(({"chave": k, "nome": nome, "n": fx.get(k, 0), "n_txt": inteiro(fx.get(k, 0))}
                          for k, nome in (("noite", "noite"), ("fim_de_semana", "fim de semana"), ("almoco", "almoço"),
                                          ("feriado", "feriado"))), key=lambda x: -x["n"])
    return {
        "total": total, "turnos": turnos, "dias": dias, "fora_partes": fora_partes, "dia": faixas_do_dia(r),
        "maior_turno": max(turnos, key=lambda x: x["n"]) if turnos else None,
        "maior_dia": max(dias, key=lambda d: (d["media"], -d["k"])) if dias else None,
    }


_cache: dict = {}


def _padroes_guardados(r: dict) -> dict:
    """padroes() roda o teste de permutação: guardado por versão do retrato (data de modificação do arquivo)."""
    chave = (RETRATO.stat().st_mtime_ns, r.get("extraido_em"))
    if chave not in _cache:
        _cache.clear()
        _cache[chave] = padroes(r)
    return _cache[chave]


class RetratoInvalido(ValueError):
    """F05 (auditoria do Codex, 31/10/2026): retrato.json fora do contrato (a seção vira "indisponível")."""


def validar_retrato(r) -> None:
    """F05: o contrato mínimo do retrato.json antes de qualquer conta (sem isso, max() de semanas vazias dá ValueError e
    as divisões pelo total ou pelos dias dão ZeroDivisionError). RetratoInvalido com o motivo."""
    if not isinstance(r, dict):
        raise RetratoInvalido(f"retrato não é um objeto ({type(r).__name__})")
    faltam = [k for k in ("inicio", "fim", "extraido_em", "periodos", "dias", "semanas", "faixas") if k not in r]
    if faltam:
        raise RetratoInvalido(f"campos ausentes: {', '.join(faltam)}")
    for k in ("periodos", "dias", "semanas"):
        if not isinstance(r[k], list) or not r[k]:
            raise RetratoInvalido(f"sem {k}")
    for k in ("inicio", "fim"):
        date.fromisoformat(r[k])  # ValueError = data ilegível
    datetime.strptime(r["extraido_em"], "%Y-%m-%d %H:%M")
    for lista in ("periodos", "semanas", "dias"):
        for x in r[lista]:
            if any(not isinstance(x.get(c), (int, float)) or x[c] < 0 for c, _, _ in CATEGORIAS):
                raise RetratoInvalido(f"contagem inválida em {lista}")
    if sum(_soma(p) for p in r["periodos"]) <= 0:
        raise RetratoInvalido("total de e-mails zero")
    if max(_soma(s) for s in r["semanas"]) <= 0:
        raise RetratoInvalido("semanas sem e-mails")


def tela(semana=None) -> dict | None:
    """Contexto do slide; None = LIA indisponível (retrato ausente, ilegível ou fora do contrato, F05). A falha fica no
    log e a página mostra a lâmina de indisponível, sem derrubar o portal."""
    try:
        r = json.loads(RETRATO.read_text(encoding="utf-8"))
        validar_retrato(r)
        return _tela(r)
    except (OSError, ValueError, KeyError, TypeError, ZeroDivisionError) as e:
        from app.dados import log  # import tardio: só na falha

        log("ERROR", "LIA indisponível: retrato fora do contrato", arquivo=str(RETRATO),
            erro=f"{type(e).__name__}: {e}"[:300])
        return None


def _tela(r: dict) -> dict:
    tot = {k: sum(p[k] for p in r["periodos"]) for k, _, _ in CATEGORIAS}
    total = sum(tot.values())
    horas = tot["nao_lead"] * MINUTOS_TRIAGEM / 60
    # Caio, 30/10/2026: o "fora do expediente" do bloco de cima é o mesmo do bloco do inbound (almoço 12h–13h, definição
    # do Caio para a LIA); sem as horas no retrato, vale a regra antiga das faixas (almoço 13h–14h, a do SLA)
    dd = faixas_do_dia(r)
    fora = dd["fora"]["n"] if dd["fora"] else sum(r["faixas"][k] for k in FORA)

    maior = max(_soma(s) for s in r["semanas"])
    semanas = []
    for i, s in enumerate(r["semanas"]):
        n = _soma(s)
        ini, fim = date.fromisoformat(s["inicio"]), date.fromisoformat(s["fim"])
        parcial = (fim - ini).days < 6
        iso = ini.isocalendar().week
        pcts = _pct_partes([s[k] for k, _, _ in CATEGORIAS], 1)  # 03/11/2026: as três fecham em 100,0%
        partes = [{"chave": k, "nome": nome, "n": s[k], "pct": pcts[j],
                   "altura": round(s[k] / n * 100, 3) if n else 0,
                   "rotulo": bool(n) and s[k] / maior >= ROTULO_MIN} for j, (k, nome, _) in enumerate(CATEGORIAS)]
        semanas.append({
            "i": i, "iso": iso, "periodo": _periodo(ini, fim), "parcial": parcial, "total": n, "lead": s["lead"],
            "h_total": round(n / maior * 100, 2), "partes": partes,  # alturas: <style> com nonce (CSP sem style="")
            "texto": (f"Semana {iso}, de {_dm(ini)} a {_dm(fim)}{', parcial' if parcial else ''}: {n} e-mails; "
                      + "; ".join(f"{p['nome'].lower()} {p['n']} ({p['pct']})" for p in partes)),
        })
    # Caio, 30/10/2026: extrato da semana retirado; `semana` (?semana=NN) é aceito e ignorado
    return {
        "inicio": _dm(date.fromisoformat(r["inicio"])), "fim": _dm(date.fromisoformat(r["fim"])),
        "fim_ano": date.fromisoformat(r["fim"]).strftime("%d/%m/%Y"),  # F10: rodapé próprio da LIA
        "extraido_em": datetime.strptime(r["extraido_em"], "%Y-%m-%d %H:%M").strftime("%d/%m/%Y, %H:%M"),
        "total": inteiro(total), "pct_filtrados": pct(tot["nao_lead"] / total), "fracao": _fracao(tot),
        "equipe": inteiro(tot["lead"] + tot["validacao"]),
        "horas": inteiro(horas), "dias": decimal(horas / HORAS_DIA), "minutos": MINUTOS_TRIAGEM,
        # ganho para a equipe (Caio, 30/10/2026): horas por semana pela mesma premissa (dias da janela ÷ 7); e-mails que a
        # equipe não precisou abrir (não lead); "1 em cada N" chega à equipe (lidos ÷ leads e validações)
        "horas_semana": inteiro(horas / (len(r["dias"]) / 7)) if r["dias"] else "—",
        "nao_lead": inteiro(tot["nao_lead"]),
        "uma_em": inteiro(total / (tot["lead"] + tot["validacao"])) if tot["lead"] + tot["validacao"] else "—",
        "fora": inteiro(fora), "pct_fora": dd["fora"]["pct"] if dd["fora"] else pct(fora / total), "fim_de_semana": inteiro(r["faixas"]["fim_de_semana"]),
        "revisados": inteiro(r["itens_com_revisao"]), "corte": _dm(date.fromisoformat(r["corte_revisao"])),
        "semanas": semanas, "padroes": _padroes_guardados(r),
        "recebimento": recebimento(r),
        # pop-up "Ver a LIA na prática" (Caio, 30/10/2026): o vídeo e as etapas vêm de lia_na_pratica (a fonte única)
        "video": lia_na_pratica.tela(),
    }
