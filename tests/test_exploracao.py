"""Estudo "Como medimos", slide 2 (X1–X9, refeito pela referência do Caio em 25/10/2026): histograma, assimetria,
Q-Q contra a normal, boxplot de Tukey (linear), curva acumulada e KDE de Silverman.

Base sintética com 72 entregues em março/2026 (mês completo), todos começando numa segunda às 10:00 (expediente
10h–13h + 14h–19h): 40 com 1 h, 15 com 2 h, 10 com 8 h (até o dia seguinte, 10:00), 5 com 40 h (uma semana) e 2 com
80 h (duas semanas). Metade exclusivos, metade não.
"""

import math
import re

import pandas as pd

from app.apresentacoes.gestao_orcamentos.sla import calculos as c


def _mov():
    linhas, i = [], 0
    inicio = pd.Timestamp("2026-03-02 10:00")  # segunda-feira
    fins = {1: pd.Timedelta(hours=1), 2: pd.Timedelta(hours=2), 8: pd.Timedelta(days=1), 40: pd.Timedelta(days=7),
            80: pd.Timedelta(days=14)}
    for horas, qtd in ((1, 40), (2, 15), (8, 10), (40, 5), (80, 2)):
        for _ in range(qtd):
            i += 1
            pid, fim = f"X{i}", inicio + fins[horas]
            base = {"projeto_id": pid, "exclusivo": i % 2 == 0, "nome_projeto": pid, "sla_util_horas": None}
            linhas.append({**base, "passo": 1, "status": "Entrada", "fase": "equipe", "entrada": inicio, "saida": fim})
            linhas.append({**base, "passo": 2, "status": "Aguardando Feedback", "fase": "cliente", "entrada": fim, "saida": pd.NaT})
    df = pd.DataFrame(linhas)
    df.attrs["versao"] = "teste-exploracao"
    return df


def test_exploracao_numeros():
    x = c.exploracao(_mov(), "2026-10", "todos")
    assert x["n"] == 72
    assert x["mediana_txt"] == "1 h"
    # X2: 40 + 15 na 1ª faixa (≤ 4 h), 10 na 2ª (8 h), 5 em (36, 40], 2 em "60 h ou mais"
    n = [b["n"] for b in x["hist"]["barras"]]
    assert sum(n) == 72 and n[0] == 55 and n[1] == 10 and n[9] == 5 and n[-1] == 2
    # X3: até 2 dias (≤ 16 h) = 65, 16–40 h = 5, > 40 h = 2 → 90/7/3 pelo maior resto; o 3º bloco leva o máximo
    assert x["faixas3"]["contagens"] == [65, 5, 2] and x["faixas3"]["pcts"] == [90, 7, 3]
    assert [f["pct"] for f in x["hist"]["faixas"]] == [90, 7, 3] and x["max_txt"] == "80 h"
    assert x["hist"]["faixas"][2]["opcoes"][0] == "mais de 5 dias, até 80 h"
    # X4: coeficiente de Fisher-Pearson (pandas skew), cauda à direita
    h = pd.Series([1.0] * 40 + [2.0] * 15 + [8.0] * 10 + [40.0] * 5 + [80.0] * 2)
    assert abs(x["assimetria"] - h.skew()) < 1e-9 and x["assim"]["positiva"] and not x["normal"]
    assert x["regua"]["quebra"] is not None and x["regua"]["marcas"][2]["nosso"]  # > 3: régua com quebra
    assert x["abaixo_media"] == round(100 * (h < h.mean()).mean())
    # X6: Tukey linear — Q1 = 1, Q3 = 2, IQR = 1, limite 3,5 h; zonas 40/15/0/17 → 55/21/0/24
    bx = x["box"]
    assert (bx["q1"], bx["mediana"], bx["q3"], bx["limite"]) == (1.0, 1.0, 2.0, 3.5)
    assert bx["contagens"] == [40, 15, 0, 17] and bx["pcts"] == [55, 21, 0, 24] and x["n_fora"] == 17
    # X9: P50/P80/P90 só no cálculo (quadro 4 saiu da tela a pedido do Caio)
    assert (x["p50"], x["p80"], x["p90"]) == (1.0, 8.0, 8.0) and "ecdf" not in x
    # X7: os três grupos com a mesma régua (limite de "Todos")
    assert [g["chave"] for g in x["comparacao"]] == ["todos", "exclusivos", "nao-exclusivos"]


def test_exploracao_poucos_dados_e_grupo():
    mov = _mov()
    poucos = mov.loc[mov["projeto_id"].isin(["X1", "X2"])].copy()
    poucos.attrs["versao"] = "teste-poucos"  # entregas() guarda cache pela versão da carga
    assert c.exploracao(poucos, "2026-10") is None  # < 30 orçamentos
    e = c.exploracao(mov, "2026-10", "exclusivos")
    assert e["n"] == 36 and e["grupo"] == "exclusivos"


def test_kde_silverman_x5():
    """KDE gaussiano com a banda de Silverman: 0,9 × min(desvio, IQR/1,34) × n^−0,2; a densidade integra ~1."""
    import numpy as np

    v = pd.Series([2.0, 3.0, 3.5, 4.0, 4.0, 5.0, 6.0, 7.5, 9.0, 12.0])
    xs = [k * 0.05 for k in range(-400, 801)]  # −20 a 40, passo 0,05
    dens, bw = c.kde_silverman(v, xs)
    iqr = float(np.quantile(v, 0.75) - np.quantile(v, 0.25))
    assert abs(bw - 0.9 * min(float(v.std()), iqr / 1.34) * len(v) ** -0.2) < 1e-12
    assert abs(sum(dens) * 0.05 - 1) < 1e-3
    # no ponto 4 a densidade é a média de normais centradas em cada valor
    d4 = sum(math.exp(-0.5 * ((4 - x) / bw) ** 2) for x in v) / (len(v) * bw * math.sqrt(2 * math.pi))
    assert abs(dens[xs.index(4.0) if 4.0 in xs else 480] - d4) < 1e-9
    assert c.kde_silverman(pd.Series([3.0] * 5), [3.0]) == ([0.0], 0.0)  # sem variação: sem curva


def test_qq_x5():
    """Q-Q: 200 quantis; os de previsão negativa (impossível) saem do gráfico e vão para a nota; a reta y = x recortada."""
    x = c.exploracao(_mov(), "2026-10", "todos")
    q = x["qq"]
    assert sum(p["n"] for p in q["pontos"]) == c.QQ_K == 200  # bolinhas proporcionais: nenhum quantil se perde
    assert all(p["x"] >= q["e"] for p in q["pontos"])
    assert sum(p["n"] for p in q["pontos"] if p["neg"]) == q["n_neg"]  # previsão < 0 h: juntas numa bolinha em 0 h
    assert q["n_fora"] > 0
    assert q["e"] <= q["reta"]["x1"] <= q["reta"]["x2"] <= q["dir"] and q["reta"]["y2"] <= q["reta"]["y1"]


def test_caixa_linear_x6():
    """Boxplot de Tukey em escala linear: posições na ordem, nomes das zonas sem se encostar e dentro do quadro."""
    x = c.exploracao(_mov(), "2026-10", "todos")
    cx = x["caixa"]
    assert cx["x_min"] <= cx["x_q1"] <= cx["x_med"] <= cx["x_q3"] <= cx["x_lim"]
    assert [z["t"] for z in cx["zonas"]] == ["rápidos", "comuns", "demorados", "outliers"]  # D38
    assert [n["t"] for n in cx["numeros"]] == ["55%", "21%", "0%", "24%"] and cx["nuvem"]
    larg = [len(n["t"]) * c.LETRA * 11.5 for n in cx["nomes"]]
    ini = [n["x"] - w / 2 for n, w in zip(cx["nomes"], larg)]
    assert all(ini[k + 1] >= ini[k] + larg[k] + 5 for k in range(len(ini) - 1))
    assert ini[-1] + larg[-1] <= cx["w"] + 0.5
    assert [v["t"] for v in cx["valores"]] == ["1 h", "2 h", "4 h"]


def test_tela_num_passo_so(monkeypatch):
    """V2 (30/10/2026, Caio): o slide 2 num passo só — histograma com as faixas do boxplot (antigo passo 3), alfinetes
    do típico e da média, "Como ler" com os três números e a frase X10; sem quadros, sem ?passo= (ignorado)."""
    from fastapi.testclient import TestClient

    from app import dados, sla
    from app.main import app

    mov = _mov()
    mov["_processado_em"] = pd.Timestamp("2026-10-21 21:16:22", tz="UTC")
    monkeypatch.setattr(dados.sla, "df", lambda forcar=False: mov)
    sla._cache.clear()
    with TestClient(app) as cli:
        html = cli.get("/viu-agenciamento/sla/como-medimos?passo=2").text  # endereço antigo: abre normal
    sla._cache.clear()
    s2 = html.split('slide-explora"')[1].split('slide-cem-tempo"')[0]
    for t in ('class="ex-camada ex-box"', 'class="ex-camada ex-alfinetes"', 'class="explora-ler"', "Como ler",
              "Típico (mediana)", "Média", "Fora da curva", "metade dos pedidos sai antes disso",
              "puxada para cima pelos casos longos", "17 pedidos acima de 4 h: olhar caso a caso",
              "E se olharmos para 100 pedidos, o que vemos?"):
        assert t in s2, t
    x = c.exploracao(mov, "2026-10")
    # V2 (30/10/2026, Caio): a faixa do pé (X10) saiu da tela; a frase segue calculada
    assert x["insight"] not in s2 and "explora-conclusoes" not in s2 and "Poucos pedidos demoram muito:" in x["insight"]
    assert f'{x["box"]["pcts"][3]}%' in s2
    for t in ("data-passo", "data-explora-ir", "explora-painel", "explora-passo", "ex-centro", "ex-sino", "ex-c3",
              "Próxima: Sino", "1 de 3", "Q-Q", "boxplot", "outlier", "assimetria", "Curva acumulada", 'class="ex-kde"'):
        assert t not in re.sub(r'<span class="so-leitor">.*?</span>|<figcaption class="so-leitor">.*?</figcaption>', " ", s2, flags=re.S), t
    assert 'class="grupos estudo-grupos"' in s2 and '?talentos=exclusivos#2' in s2
    assert 'style="' not in s2
    # X11 (V2, 30/10/2026): régua típico × média com o puxão e os fora da curva em 100 quadrados
    assert 'class="el-regua"' in s2 and (f'>+{x["puxao_txt"]}</text>' in s2) == x["media_relevante"]
    assert s2.count('<span class="eq') == 100 and s2.count('class="eq eq-fora"') == x["box"]["pcts"][3]
    assert '<p class="estudo-recorte">' not in s2  # o selo do topo saiu (V2)


def test_x11_puxao():
    """X11: puxão = média escrita − típico escrito (a conta que o leitor faz com os números da tela)."""
    assert c._puxao(14.2, 25.3) == "11 h"
    assert c._puxao(16.2, 25.0) == "8,8 h"  # típico de 1 casa perto da meta (C6)
    assert c._puxao(14.0, 13.6) == "0 h"


def test_x10_frase_do_slide_2():
    """X10: uma frase para leigos, com as variantes (média perto do típico, ninguém fora da curva, 1%)."""
    bx = {"pcts": [25, 50, 18, 7], "limite": 59.2}
    assert c._insight_unico(14.0, 25.0, bx, 171, True) == (
        "<strong>Poucos pedidos demoram muito:</strong> os 7% fora da curva, acima de 59 h, puxam a média para 25 h. "
        "O pedido típico leva 14 h. <em>Por isso medimos pelo típico (a mediana).</em>")
    assert "o 1% fora da curva" in c._insight_unico(14.0, 25.0, {**bx, "pcts": [25, 50, 24, 1]}, 3, True)
    assert c._insight_unico(14.0, 25.0, bx, 0, True).startswith("Os pedidos mais longos puxam a média para 25 h")
    assert c._insight_unico(14.0, 15.0, bx, 171, False).startswith("A média (15 h) fica perto do típico (14 h)")


def test_espelho_x5b():
    """Espelho: braço esquerdo = P50 − P(N), direito = P(100−N) − P50; excesso só quando o lento passa do espelho."""
    x = c.exploracao(_mov(), "2026-10", "todos")
    es = x["espelho"]
    assert [l["n"] for l in es["linhas"]] == [25, 10, 5, 1]
    for l in es["linhas"]:
        assert abs(l["x_esq"] + l["w_esq"] - es["cx"]) < 0.2  # braço esquerdo encosta no meio
        assert l["w_espelho"] <= l["w_esq"] + 0.1 and l["w_exc"] >= 0
        assert l["x_fim"] <= es["w"]
