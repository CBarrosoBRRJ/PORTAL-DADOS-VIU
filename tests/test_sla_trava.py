"""D42 (25/10/2026, Caio): slide 6 do estudo "Como medimos" — "Onde o tempo trava?". Horas da equipe abertas por
status (a soma por orçamento é o h_trabalho, sem o Retorno Marca), limite de Tukey por status, tempo travado = tempo
inteiro, no status, de quem travou (decisão do Caio, 25/10/2026; antes era o excesso acima do limite), % somando 100, destaque dos 2 maiores, cartão "Outros", faixa do pé por regra, seletor para #6 e
gancho do slide 5 ligado a #6 e do slide 6 a #7 (K1–K8)."""

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from app.apresentacoes.gestao_orcamentos.sla import calculos as c

SEGUNDAS = ["2026-01-05", "2026-02-02", "2026-03-02", "2026-04-06"]  # sem feriado no dia


def _mov(versao: str, n: int = 80) -> pd.DataFrame:
    """n orçamentos; cada um: Entrada 1 h, Orçamentos 1 h, Retorno Marca 0,5 h (fora), Orçamentos de novo 0,5 h,
    Validação Talento 1 h (13h–15h, com o almoço no meio), Aguardando Feedback. Os 8 primeiros ficam na fila das 10h
    às 14h (3 h úteis, sem o almoço) e o resto do ciclo anda 3 h."""
    linhas = []
    for i in range(n):
        d = SEGUNDAS[i % 4]
        t = lambda hm: pd.Timestamp(f"{d} {hm}")  # noqa: E731
        lento = i < 8
        passos = [("Entrada", "equipe", "10:00", "11:00"),
                  ("Em elaboração - Orçamentos", "equipe", "11:00", "12:00"),
                  ("Em elaboração - Retorno Marca/Executivo", "equipe", "12:00", "12:30"),
                  ("Em elaboração - Orçamentos", "equipe", "12:30", "13:00"),
                  ("Em revisão - Validação Talento", "equipe", "13:00", "15:00"),
                  ("Aguardando Feedback", "cliente", "15:00", None)]
        if lento:  # fila de 10h às 14h (3 h úteis) e o resto deslocado 3 h
            passos = [("Entrada", "equipe", "10:00", "14:00"),
                      ("Em elaboração - Orçamentos", "equipe", "14:00", "15:00"),
                      ("Em elaboração - Retorno Marca/Executivo", "equipe", "15:00", "15:30"),
                      ("Em elaboração - Orçamentos", "equipe", "15:30", "16:00"),
                      ("Em revisão - Validação Talento", "equipe", "16:00", "17:00"),
                      ("Aguardando Feedback", "cliente", "17:00", None)]
        b = {"projeto_id": f"T{i}", "exclusivo": i % 2 == 0, "nome_projeto": f"T{i}", "sla_util_horas": None}
        for k, (st, fase, e, s) in enumerate(passos, start=1):
            linhas.append({**b, "passo": k, "status": st, "fase": fase, "entrada": t(e),
                           "saida": t(s) if s else pd.NaT})
    df = pd.DataFrame(linhas)
    df.attrs["versao"] = versao
    df["_processado_em"] = pd.Timestamp("2026-05-12 21:16:22", tz="UTC")  # mês parcial = maio
    return df


def test_soma_por_status_igual_h_trabalho_e_retorno_marca_fora():
    mov = _mov("d42-a")
    e = c.entregas(mov).set_index("projeto_id")
    ps = c.horas_por_status(mov)
    assert not ps["status"].str.lower().str.startswith(c.RETORNO_MARCA).any()  # C2 (D-SLA-2)
    soma = ps.groupby("projeto_id")["h"].sum()
    assert (soma.reindex(e.index) - e["h_trabalho"]).abs().max() < 1e-9  # K1
    # passagens repetidas no mesmo status somam: Orçamentos = 1 h + 0,5 h
    orc = ps.loc[ps["status"] == "Em elaboração - Orçamentos"].set_index("projeto_id")["h"]
    assert (orc - 1.5).abs().max() < 1e-9
    assert e.loc["T0", "h_trabalho"] == pytest.approx(3 + 1.5 + 1) and e.loc["T9", "h_trabalho"] == pytest.approx(3.5)


def test_travas_com_movimentos_sinteticos():
    mov = _mov("d42-b")
    v = c.travas(mov, "2026-05", "todos")
    assert v["n"] == 80
    fila = next(s for s in v["status"] if s["nome"] == "Fila de entrada")
    # 72 com 1 h e 8 com 3 h: Q1 = Q3 = 1 → limite 1 h; 8 travaram; tempo travado = o tempo inteiro deles, 8 × 3 h (K4)
    assert fila["limite"] == pytest.approx(1) and fila["travaram"] == 8 and fila["travado"] == pytest.approx(24)
    assert fila["pct"] == 100 and fila["destaque"] and fila["tipico"] == "1,0 h"
    assert [e["nome"] for e in v["etapas"]] == ["Entrada", "Elaboração", "Revisão"]
    assert [k["nome"] for k in v["etapas"][1]["cartoes"]] == ["Orçamentos"]
    assert v["etapas"][1]["retorno"] and not v["etapas"][0]["retorno"]
    assert v["tipo"] == "um" and "<strong>Fila de entrada</strong> concentra <em>100% do tempo travado</em>" in v["rodape"]
    assert v["gancho"] == "E em que tipo de pedido isso pesa mais?"
    # tudo muda com o grupo: só os exclusivos (pares) → 4 dos 8 lentos
    ex = next(s for s in c.travas(mov, "2026-05", "exclusivos")["status"] if s["nome"] == "Fila de entrada")
    assert ex["n"] == 40 and ex["travaram"] == 4


def _u(n: int = 40) -> pd.DataFrame:
    return pd.DataFrame({"projeto_id": [f"P{i}" for i in range(n)], "mes": "2026-04", "h_trabalho": 0.0})


def _ps(spec: dict[str, list[float]]) -> pd.DataFrame:
    """{status: [horas do orçamento P0, P1, ...]}"""
    return pd.DataFrame([{"projeto_id": f"P{i}", "status": st, "h": float(h)} for st, hs in spec.items()
                         for i, h in enumerate(hs)])


def test_limite_de_tukey_por_status_e_tempo_travado_inteiro():
    hs = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 40, 60]
    v = c._travas(_u(), _ps({"Entrada": hs, "Em revisão": [2] * 12}), "2026-05")
    s = pd.Series(hs, dtype=float)
    q1, q3 = s.quantile(0.25), s.quantile(0.75)
    lim = q3 + 1.5 * (q3 - q1)
    fila = v["status"][0]
    assert fila["limite"] == pytest.approx(lim) and fila["mediana"] == pytest.approx(s.median())
    assert fila["travaram"] == int((s > lim).sum()) == 2
    # K4 (Caio, 25/10/2026): o tempo inteiro de quem travou, não só o excesso acima do limite
    assert fila["travado"] == pytest.approx(float(s[s > lim].sum())) == pytest.approx(100)
    assert fila["travado"] > float((s[s > lim] - lim).sum())
    assert len(v["status"]) == 2 and v["status"][1]["travado"] == 0  # todos iguais: ninguém trava


def test_pcts_somam_100_destaque_outros_e_menor_que_1():
    base = [1.0] * 36
    spec = {"Entrada": base + [11] * 4,  # 44 (tempo inteiro dos 4 que travaram)
            "Em Elaboração": base + [210] * 4,  # 840 → maior
            "Em elaboração - Orçamentos": base + [6] * 4,  # 24
            "Em elaboração (Produção)": base + [3.5] * 4,  # 14
            "Em elaboração - Cotação Externa": base + [2.5] * 4,  # 10
            "Em elaboração - GP": base + [1.25] * 2 + [1] * 2,  # 2,5 (grafias do GP somam no mesmo cartão)
            "Em elaboração GP": [0.0] * 40,
            "Em revisão - Validação Talento": base + [1.1] * 4}  # 4,4 de 938,9 → <1%
    v = c._travas(_u(), _ps(spec), "2026-05")
    assert sum(s["pct"] for s in v["status"]) == 100
    nomes = [s["nome"] for s in v["status"]]
    assert nomes[:2] == ["Em elaboração", "Fila de entrada"] and "GP" in nomes and "Em elaboração GP" not in nomes
    assert [s["destaque"] for s in v["status"]] == [True, True] + [False] * (len(nomes) - 2)
    elab = v["etapas"][1]["cartoes"]
    assert [k["nome"] for k in elab] == ["Em elaboração", "Orçamentos", "Produção", "Outros 2 status"]
    outros = elab[-1]
    assert outros["outros"] and not outros["destaque"] and outros["membros"] == ["Cotação Externa", "GP"]
    assert outros["pct"] == sum(s["pct"] for s in v["status"] if s["nome"] in ("Cotação Externa", "GP"))
    assert outros["travaram"] == 4 and "Cotação Externa e GP" in outros["leitor"]
    vt = next(s for s in v["status"] if s["nome"] == "Validação Talento")
    assert vt["pct"] == 0 and vt["pct_txt"] == "<1%"
    assert elab[0]["barra"] == 100 and 0 < elab[1]["barra"] < 100


def test_variantes_da_faixa_do_pe():
    base = [1.0] * 36
    dois = c._travas(_u(), _ps({"Entrada": base + [11] * 4, "Em elaboração - Orçamentos": base + [11] * 4,
                                "Em revisão": base + [6] * 4}), "2026-05")
    assert dois["tipo"] == "dois" and "em dois pontos" in dois["rodape"] and "<em>78% do tempo travado</em>" in dois["rodape"]
    esp = c._travas(_u(), _ps({st: base + [11] * 4 for st in ("Entrada", "Em elaboração - Orçamentos",
                                                               "Em elaboração (Produção)", "Em revisão",
                                                               "Em revisão - Validação Talento", "Em elaboração - GP")}),
                    "2026-05")
    assert esp["tipo"] == "espalhado" and "espalhado pelo ciclo" in esp["rodape"]
    assert sum(s["pct"] for s in esp["status"][:2]) < 40
    um = c._travas(_u(), _ps({"Entrada": base + [21] * 4, "Em revisão": base + [6] * 4}), "2026-05")
    assert um["tipo"] == "um" and "em um ponto" in um["rodape"]


def test_status_visto_so_ate_um_mes_e_poucos_dados():
    u = _u()
    u.loc[:19, "mes"] = "2026-01"
    ps = _ps({"Em Elaboração": [1.0] * 18 + [9, 9], "Entrada": [1.0] * 36 + [3] * 4})
    v = c._travas(u, ps, "2026-05")  # último mês completo: abril; o status geral só aparece em janeiro
    ger = next(s for s in v["status"] if s["nome"] == "Em elaboração")
    # K6: a nota fica numa linha curta própria; a linha de números ("N travaram · típico") não muda
    assert ger["ate"] == "jan" and ger["nota"] == "só até jan" and "só até" not in ger["meta"]
    assert len(ger["partes"]) == 2 and "entregues até jan" in ger["leitor"]
    assert all(s["nota"] is None for s in v["status"] if s["nome"] != "Em elaboração")
    assert "(só até jan)" in v["rodape"]
    assert c._travas(_u(29), _ps({"Entrada": [1.0] * 29}), "2026-05") is None  # K1: menos de 30
    assert c._travas(_u(), _ps({"Entrada": [1.0] * 40}), "2026-05") is None  # nada travou


def test_mapeamento_status_etapa_e_nomes():
    assert c._etapa_ciclo("Entrada") == "Entrada" and c._nome_status("Entrada") == "Fila de entrada"
    assert c._etapa_ciclo("Em Elaboração") == "Elaboração" and c._nome_status("Em Elaboração") == "Em elaboração"
    assert c._nome_status("Em elaboração (Produção)") == "Produção"
    assert c._nome_status("Em elaboração - Cotação Externa") == "Cotação Externa"
    assert c._nome_status("Em elaboração GP") == c._nome_status("Em elaboração - GP") == "GP"
    assert c._etapa_ciclo("Em revisão - Validação Talent Manager") == "Revisão"
    assert c._nome_status("Em revisão") == "Em revisão" and c._nome_status("Em revisão (Planejamento)") == "Planejamento"
    assert c._etapa_ciclo("Algo novo") == c.OUTRAS


def test_slide_6_no_html_seletor_e_gancho_do_slide_5(monkeypatch):
    from app import dados, sla
    from app.main import app

    mov = _mov("d42-html")
    monkeypatch.setattr(dados.sla, "df", lambda forcar=False: mov)
    sla._cache.clear()
    with TestClient(app) as cli:
        html = cli.get("/viu-agenciamento/sla/como-medimos?talentos=exclusivos").text
    sla._cache.clear()
    assert html.count('class="slide slide-estudo') == 5  # contagem automática (D43, D44; D64 tirou o slide 7; V2 uniu 3 e 4 e tirou a conclusão)
    s6 = html.split('slide-trava"')[1]
    assert "o ciclo, da entrada ao Aguardando Feedback" in s6 and "Onde o tempo trava?" in s6
    for g in ("todos", "exclusivos", "nao-exclusivos"):
        assert f'href="?talentos={g}#5"' in s6  # V2 (30/10/2026): o slide da trava passou a ser o 5 (o último)
    assert 'href="?talentos=exclusivos#5" class="grupo" aria-current="true"' in s6
    # a definição fica só no aria-label da lista (pedido do Caio: sem a linha explicativa na tela)
    assert 'aria-label="Onde o tempo trava, por etapa do ciclo. De todo o tempo travado' in s6
    assert 'class="trava-intro"' not in s6
    assert s6.count("o tempo travado é o tempo inteiro, naquele status, dos orçamentos que travaram.") == 1
    for t in ("Entrada", "Elaboração", "Revisão", "Entrega", "Retorno da marca", "espera da marca: fora da conta",
              "Aguardando Feedback", "Daqui em diante o tempo é do cliente e não entra na conta."):
        assert t in s6
    assert 'class="trava-cartao trava-destaque"' in s6 and "Fila de entrada: 100% do tempo travado." in s6
    assert "explora-conclusoes" not in s6  # V2 (30/10/2026, Caio): faixa do pé fora da tela (frase segue calculada)
    # V2: último slide, com a saída do estudo (era a da conclusão): volta ao SLA com o filtro e a próxima página
    # V2 (30/10/2026, Caio): sem os links da saída; o ✕ destacado volta ao SLA com o filtro (fim do estudo)
    assert 'class="fechar-estudo fechar-fim" href="/viu-agenciamento/sla?talentos=exclusivos#1" aria-label="Fim do estudo: voltar ao SLA" title="Fim do estudo"' in s6
    assert "Voltar ao SLA" not in s6 and "gancho-sec" not in s6 and "E o que os dados nos mostraram?" not in s6
    for proibido in ("outlier", "boxplot", "tukey", "quartil", "mediana"):
        assert proibido not in s6.lower()
    assert 'style="' not in s6 and "<style" not in s6
    s5 = html.split('slide-mes"')[1].split('slide-trava"')[0]
    assert '<a class="gancho-link" href="#5">' in s5 and "onde o tempo trava?" in s5


def test_slide_6_com_poucos_dados(monkeypatch):
    from app import dados, sla
    from app.main import app

    mov = _mov("d42-poucos", n=12)
    monkeypatch.setattr(dados.sla, "df", lambda forcar=False: mov)
    sla._cache.clear()
    with TestClient(app) as cli:
        html = cli.get("/viu-agenciamento/sla/como-medimos").text
    sla._cache.clear()
    s6 = html.split('slide-trava"')[1]
    assert "Ainda não há orçamentos suficientes" in s6 and "trava-cartao" not in s6
