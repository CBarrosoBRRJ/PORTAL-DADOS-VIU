"""D41 (25/10/2026, Caio): slide 5 do estudo "Como medimos" — "Foi um mês ruim, ou é sempre assim?". Dispersão por mês
(um ponto por orçamento, posição fixa pelo id), típico e faixa da maioria de cada mês, % que passa de 2 dias e pedidos
por mês, título e faixa do pé por regra, seletor de talentos levando a #5 e gancho do slide 4 ligado a #5 (U1–U9)."""

import re

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from app.apresentacoes.gestao_orcamentos.sla import calculos as c


def _d(meses: dict[str, list[tuple[float, int]]]) -> pd.DataFrame:
    """Universo sintético já pronto (colunas que `_meses` usa): {mês: [(horas, quantidade), ...]}."""
    linhas, i = [], 0
    for mes, mix in meses.items():
        for h, q in mix:
            for _ in range(q):
                i += 1
                linhas.append({"projeto_id": f"P{i}", "mes": mes, "h_trabalho": float(h)})
    return pd.DataFrame(linhas)


# segunda-feira de cada mês às 10:00, sem feriado nos 3 dias úteis seguintes
SEGUNDAS = {"2026-01": "2026-01-05", "2026-02": "2026-02-02", "2026-03": "2026-03-02", "2026-04": "2026-04-06"}
FINS = {1: pd.Timedelta(hours=1), 24: pd.Timedelta(days=3)}  # 1 h e 24 h de trabalho (3 dias úteis de 8 h)


def _mov(mix_por_mes, versao):
    linhas, i = [], 0
    for mes, mix in mix_por_mes.items():
        inicio = pd.Timestamp(f"{SEGUNDAS[mes]} 10:00")
        for horas, qtd in mix:
            for _ in range(qtd):
                i += 1
                pid, fim = f"M{i}", inicio + FINS[horas]
                b = {"projeto_id": pid, "exclusivo": i % 2 == 0, "nome_projeto": pid, "sla_util_horas": None}
                linhas.append({**b, "passo": 1, "status": "Entrada", "fase": "equipe", "entrada": inicio, "saida": fim})
                linhas.append({**b, "passo": 2, "status": "Aguardando Feedback", "fase": "cliente", "entrada": fim,
                               "saida": pd.NaT})
    df = pd.DataFrame(linhas)
    df.attrs["versao"] = versao
    df["_processado_em"] = pd.Timestamp("2026-05-12 21:16:22", tz="UTC")  # mês parcial = maio; completos jan–abr
    return df


MIX = {"2026-01": [(1, 12), (24, 8)], "2026-02": [(1, 18), (24, 12)], "2026-03": [(1, 24), (24, 16)],
       "2026-04": [(1, 30), (24, 20)]}  # 40% passam de 2 dias em todos os meses


def test_quantidades_somam_n_e_pct_por_mes_igual_a_pagina():
    mov = _mov(MIX, "d41-a")
    for g in c.GRUPOS:
        u = c.meses_estudo(mov, "2026-05", g)
        assert sum(m["n"] for m in u["meses"]) == u["n"] == len(c._universo_df(mov, "2026-05", g))
        pagina = {m["chave"]: m for m in c.entrega(mov, "2026-05", g)["meses"]}
        for m in u["meses"][:4]:
            h = c._universo_df(mov, "2026-05", g).query("mes == @m['chave']")["h_trabalho"]
            assert m["b"] == 100 - pagina[m["chave"]]["tela"]["ate2"] == c._pontos((h > c.META_H).mean())
    u = c.meses_estudo(mov, "2026-05", "todos")
    # U2: 12 colunas fixas; maio (parcial) e os futuros ficam vazios, sem números
    assert [m["rotulo"] for m in u["meses"]] == c.formato.MESES
    assert [m["vazio"] for m in u["meses"]] == [False] * 4 + [True] * 8
    assert [m["n"] for m in u["meses"]] == [20, 30, 40, 50] + [0] * 8
    assert [m["b"] for m in u["meses"]] == [40] * 4 + [None] * 8
    assert u["tipo"] == "padrao" and "mai a dez: ainda sem mês completo" in u["grafico"]["texto"]
    assert len({m["larg"] for m in u["meses"]}) == 1 and u["meses"][-1]["x0"] + u["meses"][-1]["larg"] <= u["grafico"]["dir"] + 0.1


def test_pct_pela_conta_da_pagina_no_meio_ponto():
    """U2 (C8): 100 − "até 2 dias" arredondado. Com 12,5% acima de 16 h: até 2 dias 87,5 → 88 → B = 12."""
    u = c._meses(_d({"2026-01": [(4, 35), (20, 5)], "2026-02": [(4, 35), (20, 5)]}), "2026-03")
    assert [m["b"] for m in u["meses"][:2]] == [12, 12]


def test_tipico_e_faixa_da_maioria():
    u = c._meses(_d({"2026-01": [(4, 10), (12, 10), (30, 10)], "2026-02": [(16.3, 31)]}), "2026-03")
    jan, fev = u["meses"][:2]
    h = pd.Series([4.0] * 10 + [12.0] * 10 + [30.0] * 10)
    assert jan["mediana"] == 12 and jan["q1"] == h.quantile(0.25) and jan["q3"] == h.quantile(0.75)
    assert jan["tipico"] == "12 h" and fev["tipico"] == "16,3 h"  # C6: logo acima de 16 h, 1 casa
    assert jan["y_q3"] < jan["y_med"] < jan["y_q1"]
    assert jan["y_txt"] > jan["y_med"] and fev["y_txt"] < fev["y_med"]  # U9: valor acima do ponto quando passa de 2 dias


def test_escala_em_dias_e_triangulos():
    d = _d({"2026-01": [(0, 10), (8, 5), (16, 5), (24, 5), (40, 5), (80, 5), (81, 2), (500, 1)],
            "2026-02": [(10, 30)]})
    u = c._meses(d, "2026-03")
    g = u["grafico"]
    assert [k["rotulo"] for k in g["marcas"]] == ["0", "1 dia", "2 dias", "3 dias", "5 dias", "10 dias"]
    ys = [k["y"] for k in g["marcas"]]
    assert ys == sorted(ys, reverse=True) and ys[0] == g["base"] and ys[-1] == g["topo"]
    assert ys[1] - ys[2] < ys[0] - ys[1]  # raiz quadrada: o 2º dia ocupa menos altura que o 1º
    assert g["y2"] == ys[2]  # linha de 2 dias = 16 h
    assert u["n_topo"] == 3 == g["triangulos"].count("z") == u["meses"][0]["n_topo"]  # 80 h fica no 10 dias, não vira triângulo
    pontos = sum(len(v.split("M")) - 1 for v in g["pontos"].values())
    assert pontos + u["n_topo"] == u["n"]
    assert len(g["pontos"]["mais5"].split("M")) - 1 == 5  # 80 h (> 40 h, ≤ 80 h)
    assert "3 pedidos passam de 10 dias" in g["texto"]


def test_posicao_horizontal_deterministica_e_dentro_da_coluna():
    d = _d({"2026-01": [(4, 40)], "2026-02": [(20, 40)]})
    a, b = c._meses(d, "2026-03"), c._meses(d.sample(frac=1, random_state=3), "2026-03")
    assert c._sorteio("P1") == c._sorteio("P1") and 0 <= c._sorteio("P1") < 1 and c._sorteio("P1") != c._sorteio("P2")
    assert sorted(a["grafico"]["pontos"]["ate2"].split(" ")) == sorted(b["grafico"]["pontos"]["ate2"].split(" "))
    for m, chave in zip(a["meses"], ("ate2", "de2a5")):
        xs = [float(x) for x in re.findall(r"M([\d.]+) ", a["grafico"]["pontos"][chave])]
        assert len(xs) == 40 and all(m["x0"] + 0.1 * m["larg"] - 0.1 <= x <= m["x0"] + 0.9 * m["larg"] + 0.1 for x in xs)
        assert all(re.fullmatch(r"\d+(\.\d)?", x) for x in re.findall(r"M([\d.]+) ", a["grafico"]["pontos"][chave]))


def _m(k, n, med, b):
    """Mês sintético para as regras de texto (k = 1..12)."""
    return {"chave": f"2026-{k:02d}", "extenso": c.formato.MESES_EXTENSO[k - 1], "n": n, "mediana": med, "b": b,
            "tipico": c._h_meta(med) if n else None, "vazio": False}


def _ms(bs, meds=None, ns=None):
    meds = meds or [14] * len(bs)
    ns = ns or [50] * len(bs)
    return [_m(k + 1, n, med, b) for k, (n, med, b) in enumerate(zip(ns, meds, bs))]


def test_padrao_nenhum_mes_destoa():
    ms = _ms([40, 45, 42, 50, 51, 51, 43, 41, 41], [13.16, 15.71, 14.89, 16.34, 16.32, 16.46, 12.92, 12.6, 13.56])
    ms += [{**_m(k, 0, 0, 0), "vazio": True, "mediana": None, "b": None} for k in (10, 11, 12)]
    t = c._mes_textos(ms)
    assert t["tipo"] == "padrao" and t["destoam"] == []
    assert t["titulo"] == "A demora não é de um mês. Acontece o ano todo."
    assert t["rodape"] == ("<strong>Não é sazonal:</strong> todo mês, de 40% a 51% dos pedidos passam de 2 dias. "
                           "<em>O problema é o processo, não o mês</em> — é nele que está a solução.")
    assert t["gancho"] == "Se é assim, onde o tempo trava?"


def test_destoa_pelo_pct_ou_pelo_tipico():
    # mediana dos B = 40: 50 não destoa (10 pontos), 51 destoa; mediana dos típicos = 14: 18 h não, 18,1 h destoa
    assert c._destoam(_ms([40, 40, 40, 50, 40])) == []
    assert [m["chave"] for m in c._destoam(_ms([40, 40, 40, 51, 40]))] == ["2026-04"]
    assert c._destoam(_ms([40] * 5, [14, 14, 14, 18, 14])) == []
    assert [m["chave"] for m in c._destoam(_ms([40] * 5, [14, 14, 14, 18.1, 14]))] == ["2026-04"]


def test_picos_um_ou_dois_meses():
    t = c._mes_textos(_ms([40, 42, 62, 41, 43], [13, 14, 15, 14, 16]))
    assert t["tipo"] == "picos" and t["titulo"] == "A demora não é de um mês. Acontece o ano todo."
    assert t["rodape"] == ("<strong>No geral, não é sazonal:</strong> quase todo mês, de 40% a 43% passam de 2 dias; só "
                           "março fugiu do padrão. <em>O problema é o processo</em>, com picos pontuais.")
    assert t["gancho"] == "Se é assim, onde o tempo trava?"
    # fevereiro destoa só pelo típico (22 h): "fugiram do padrão" vale para os dois critérios
    t = c._mes_textos(_ms([40, 42, 62, 41, 43, 40], [13, 22, 15, 14, 16, 14]))
    assert t["tipo"] == "picos" and "; só fevereiro e março fugiram do padrão." in t["rodape"]
    assert "de 40% a 43% passam" in t["rodape"]
    assert t["destoam"] == ["2026-02", "2026-03"]


def test_sazonal_meses_seguidos_ou_espalhados():
    t = c._mes_textos(_ms([40, 42, 41, 62, 65, 60, 43, 40, 41]))
    assert t["tipo"] == "sazonal" and t["titulo"] == "A demora pesa em alguns meses do ano."
    assert t["rodape"] == ("<strong>Há meses mais pesados:</strong> de abril a junho, de 60% a 65% passam de 2 dias, contra "
                           "40% a 43% no resto do ano. <em>Vale planejar a equipe para esses meses.</em>")
    assert t["gancho"] == "Se é assim, onde o tempo trava?"
    # não exclusivos na carga de 23/10: abril, maio e agosto destoam (fora de sequência)
    ne = _ms([44, 43, 48, 75, 70, 60, 57, 75, 47], [14.26, 16, 15.19, 26.08, 23.72, 18.8, 18.11, 27.96, 15.93])
    t = c._mes_textos(ne)
    assert t["tipo"] == "sazonal" and t["destoam"] == ["2026-04", "2026-05", "2026-08"]
    assert "em abril, maio e agosto, de 70% a 75% passam de 2 dias, contra 43% a 60% no resto do ano." in t["rodape"]


def test_raro_e_valores_iguais():
    t = c._mes_textos(_ms([5, 8], [4, 4]))
    assert t["tipo"] == "raro" and t["titulo"] == "Em todos os meses, quase nada passa de 2 dias."
    assert t["rodape"] == ("<strong>Não é sazonal:</strong> todo mês, só de 5% a 8% dos pedidos passam de 2 dias. "
                           "<em>O prazo se mantém o ano todo.</em>")
    t = c._mes_textos(_ms([40, 40], [14, 14]))
    assert "todo mês, 40% dos pedidos passam de 2 dias." in t["rodape"]


def test_rotulo_da_linha_de_2_dias():
    livre = c._meses(_d({f"2026-{k:02d}": [(4, 20)] for k in range(1, 10)}), "2026-10")
    r = livre["grafico"]["rot2"]
    assert r and r["x"] == livre["grafico"]["dir"] - 6 and r["y"] == livre["grafico"]["y2"] - 7
    # colunas vazias (out a dez) contam como livres: mesmo com todos os típicos acima de 2 dias, o rótulo fica lá
    cheio = c._meses(_d({f"2026-{k:02d}": [(30, 20)] for k in range(1, 10)}), "2026-10")
    assert cheio["grafico"]["rot2"]["x"] == cheio["grafico"]["dir"] - 6
    # 11 meses completos, o último acima de 2 dias: o rótulo termina antes do ponto de um mês anterior
    d = _d({**{f"2026-{k:02d}": [(4, 20)] for k in range(1, 11)}, "2026-11": [(30, 20)]})
    u = c._meses(d, "2026-12")
    r = u["grafico"]["rot2"]
    assert r and r["x"] < u["meses"][10]["x0"]
    # todos acima de 2 dias e só dezembro vazio: o rótulo vai para a legenda
    assert c._meses(_d({f"2026-{k:02d}": [(30, 20)] for k in range(1, 12)}), "2026-12")["grafico"]["rot2"] is None


def test_poucos_dados():
    assert c._meses(_d({"2026-01": [(4, 15)], "2026-02": [(4, 14)]}), "2026-03") is None  # 29 < 30
    assert c._meses(_d({"2026-01": [(4, 40)]}), "2026-02") is None  # 1 mês completo
    assert c._meses(_d({"2026-01": [(4, 40)]}), "2026-03") is None  # 2 meses, só 1 com pedidos
    u = c._meses(_d({"2026-01": [(4, 40)], "2026-03": [(4, 10)]}), "2026-04")
    assert u and u["meses"][1]["n"] == 0 and u["meses"][1]["b"] is None


def test_slide_5_no_html_seletor_e_gancho_do_slide_4(monkeypatch):
    from app import dados, sla
    from app.main import app

    mov = _mov(MIX, "d41-html")
    monkeypatch.setattr(dados.sla, "df", lambda forcar=False: mov)
    sla._cache.clear()
    with TestClient(app) as cli:
        html = cli.get("/viu-agenciamento/sla/como-medimos?talentos=exclusivos").text
    sla._cache.clear()
    assert html.count('class="slide slide-estudo') == 5  # contagem automática; D42 trouxe o 6, D43 o 7, D44 o 8; D64 tirou o 7; V2 uniu 3 e 4 e tirou a conclusão
    s5 = html.split('slide-mes"')[1].split('slide-trava"')[0]
    assert "foi um mês ruim, ou é sempre assim?" in s5 and "A demora não é de um mês. Acontece o ano todo." in s5
    for g in ("todos", "exclusivos", "nao-exclusivos"):
        assert f'href="?talentos={g}#4"' in s5  # V2 (30/10/2026): o slide do mês passou a ser o 4
    assert 'href="?talentos=exclusivos#4" class="grupo" aria-current="true"' in s5
    assert 'class="mes-svg"' in s5 and 'role="img" aria-label="Cada ponto é um dos' in s5
    for t in ("o típico do mês", "faixa onde fica a maioria (metade dos pedidos)", "cada ponto é um pedido"):
        assert t in s5
    for proibido in ("mediana", "quartil", "metade do meio"):
        assert proibido not in s5.lower().split("<svg")[0]
    assert s5.count('<th scope="col">') == 4 and s5.count('<th scope="col" class="mt-vazio">') == 8 and '<th scope="row">passam de 2 dias</th>' in s5
    assert "<td>40%</td>" in s5 and "maio" not in s5.split("<table")[1].split("</table>")[0]
    assert "explora-conclusoes" not in s5 and "Se é assim, onde o tempo trava?" in s5  # V2 (30/10): faixa U8 fora da tela
    assert 'style="' not in s5 and "<style" not in s5
    s4 = html.split('slide-cem-tempo"')[1].split('slide-mes"')[0]  # V2: o gancho sai do slide 3 unificado
    assert '<a class="gancho-link" href="#4">Mas esses' in s4 and "foram um mês ruim, ou é sempre assim?" in s4


def test_slide_5_com_poucos_dados(monkeypatch):
    from app import dados, sla
    from app.main import app

    mov = _mov({"2026-01": [(1, 10)], "2026-02": [(1, 10)]}, "d41-poucos")
    monkeypatch.setattr(dados.sla, "df", lambda forcar=False: mov)
    sla._cache.clear()
    with TestClient(app) as cli:
        html = cli.get("/viu-agenciamento/sla/como-medimos").text
    sla._cache.clear()
    s5 = html.split('slide-mes"')[1].split('slide-trava"')[0]
    assert "Ainda não há orçamentos suficientes" in s5 and "mes-svg" not in s5
    assert "Foi um mês ruim, ou é sempre assim?" in s5
