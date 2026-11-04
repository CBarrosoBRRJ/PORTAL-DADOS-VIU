"""D53 (26/10/2026, Caio): Atendimento com resolvido = entregue ao cliente (A15b), extrato em três blocos com uma linha
de % (A24b), dica dos status das saídas sem entrega (A26), taxa de CAPACIDADE — entregues ÷ demanda que dependia da
equipe (A27) —, ▲/▼ no que ficou (A28), dispersão com origem em 0 e "Próxima pergunta" fora da tela em todas as
páginas."""
import re

import gold_simulada  # views da gold sobre os dados sintéticos (D57)
import pandas as pd
import pytest
from fastapi.testclient import TestClient

from app import dados
from app.apresentacoes.gestao_orcamentos.atendimento import calculos as at
from app.main import app


@pytest.fixture
def cliente():
    with TestClient(app) as c:
        yield c


def test_faixa_do_ano_pelo_maior_resto():
    """A15b: % sobre os recebidos, inteiros pelo maior resto; carga de 26/10: 4.415/974/167 de 5.556 = 79/18/3."""
    meses = [{"entregues_ano": 4415, "sem_entrega_ano": 974}]
    total = {"entradas": 5556}
    r = at._faixa_ano({"meses": meses, "fila_atual": 167, "total": total})
    assert (r["pct_entregues"], r["pct_sem_entrega"], r["pct_andamento"]) == (79, 18, 3)
    # A30 (D58b): (entregues + declinados) ÷ recebidos = 5.389 ÷ 5.556 = 97,0% → 97 (calculado; o selo saiu da tela)
    st = {"meses": {"2026-10": {"confere": True, "externos": 160}}, "ano": {"externos": 160}}
    r = at._faixa_ano({"meses": meses, "fila_atual": 167, "total": total}, st)
    assert (r["externos_ano"], r["dependia_ano"], r["pct_dependia"]) == (160, 5556, 97)
    # divisão inteira dava 96 + 4 no "resolvido"; agora as partes sempre fecham 100
    for ent, sem, seg in [(1, 1, 1), (5389 - 974, 974, 167), (0, 0, 5), (10, 0, 0)]:
        r = at._faixa_ano({"meses": [{"entregues_ano": ent, "sem_entrega_ano": sem}], "fila_atual": seg,
                           "total": {"entradas": ent + sem + seg}})
        assert r["pct_entregues"] + r["pct_sem_entrega"] + r["pct_andamento"] == 100


def test_quadro_em_tres_blocos_e_uma_linha_de_pct(entrada_diaria, fluxo_mensal):
    a = at.atendimento(entrada_diaria, fluxo_mensal, gold_simulada.atendimento_mensal(entrada_diaria, fluxo_mensal))
    q = at.analise_ritmo(a)["quadro"]
    assert [b["chave"] for b in q["blocos"]] == ["entrada", "saida", "saldo"]
    assert [[l["chave"] for l in b["linhas"]] for b in q["blocos"]] == [["veio", "entrou", "atender"], ["entregues", "sem", "saiu"], ["ficou"]]
    assert [l["chave"] for l in q["linhas"] if l["subtotal"]] == ["atender", "saiu", "ficou"]
    L = {l["chave"]: [c["v"] for c in l["celulas"]] for l in q["linhas"]}
    # A30 (D58b): entregues no mês (entregues + declinados) ÷ para atender; ex. set/2026: 661 ÷ 834 = 79%
    assert q["pct"] == [at.pct_meio(s, a_) for s, a_ in zip(L["saiu"], L["atender"])]
    assert L["saiu"] == [e + s for e, s in zip(L["entregues"], L["sem"])]
    assert at.pct_meio(661, 834) == 79
    d = at.analise_ritmo(a)["dispersao"]
    assert [p["pct"] for p in d["pontos"]] == q["pct"]  # os pontos batem com a linha da tabela
    assert d["objetivo"]["pct"] == 100 and d["corte"]["pct"] == 90  # visual do gráfico mantido (Caio)
    # D53: eixos a partir de 0 — as duas retas saem da mesma origem (o canto do quadro)
    assert d["marcas"][0]["rotulo"] == "0"
    assert (d["objetivo"]["x0"], d["objetivo"]["y0"]) == (d["corte"]["x0"], d["corte"]["y0"]) == (d["x0"], d["y0"])
    # A28: variação do que ficou contra o mês anterior
    assert q["ficou_var"][0] is None and q["ficou_var"][1:] == [b - a_ for a_, b in zip(L["ficou"][:-1], L["ficou"][1:])]


def test_pct_independe_do_status(entrada_diaria, fluxo_mensal):
    """A30 (D58b): (entregues + declinados) ÷ para atender, qualquer que seja o status dos declinados; com ou sem a
    composição por status, a conta é a mesma."""
    a = at.atendimento(entrada_diaria, fluxo_mensal, gold_simulada.atendimento_mensal(entrada_diaria, fluxo_mensal))
    jan = next(m for m in a["meses"] if m["chave"] == "2026-01")
    n = jan["sem_entrega_ano"]
    assert n >= 1
    sem_status = at.analise_ritmo(a)["quadro"]["pct"][0]
    for status in ("Declinado pelo Mercado", "Encerrado", "Declinado pelo talento", "Declinado Internamente", "Standby"):
        df = pd.DataFrame({"mes": pd.to_datetime(["2026-01-01"]).date, "status": [status], "n": [n], "sem_data": [0]})
        st = at.status_sem_entrega(a, df)
        q = at.analise_ritmo(a, st)["quadro"]
        k = q["conta"][0]
        assert k["declinados"] == n and k["saiu"] == k["entregues"] + n and k["dependia"] == k["atender"]
        assert [i["status"] for i in k["itens"]] == [status]  # a dica da conta lista o status do mês
        assert k["pct"] == at.pct_meio(k["saiu"], k["atender"]) == q["pct"][0] == sem_status


def test_status_sem_entrega_so_quando_bate(entrada_diaria, fluxo_mensal):
    """A26: composição por status só no mês cujo total bate com a célula (gold); o ano só se todos baterem."""
    a = at.atendimento(entrada_diaria, fluxo_mensal, gold_simulada.atendimento_mensal(entrada_diaria, fluxo_mensal))
    jan = next(m for m in a["meses"] if m["chave"] == "2026-01")
    df = pd.DataFrame({"mes": pd.to_datetime(["2026-01-01", "2026-01-01"]).date, "status": ["Standby", "Encerrado"],
                       "n": [jan["sem_entrega_ano"], 0], "sem_data": [0, 0]})
    st = at.status_sem_entrega(a, df)
    assert st["meses"]["2026-01"]["confere"] and sum(i["n"] for i in st["meses"]["2026-01"]["itens"]) == jan["sem_entrega_ano"]
    assert all(i["n"] for i in st["meses"]["2026-01"]["itens"])  # status zerado não aparece
    assert st["ano"]["total"] == sum(m["sem_entrega_ano"] or 0 for m in a["meses"])
    errado = df.assign(n=[jan["sem_entrega_ano"] + 1, 0])
    st = at.status_sem_entrega(a, errado)
    assert not st["meses"]["2026-01"]["confere"] and st["meses"]["2026-01"]["itens"] == [] and st["ano"] is None
    assert at.status_sem_entrega(a, None) is None


def test_pagina_atendimento_d53(cliente):
    r = cliente.get("/viu-agenciamento/atendimento")
    assert r.status_code == 200 and 'style="' not in r.text
    assert re.search(r'<dt><span class="kpi-chave kpi-entregue" aria-hidden="true"></span>Entregues ao cliente</dt>', r.text)
    assert "kpi-selo" not in r.text and "dependia da equipe" not in r.text and "kpi-legenda" not in r.text  # D58b
    for bloco in ("Entrada", "Saída", "Saldo"):
        assert '<th scope="rowgroup" rowspan="' in r.text and f"<span>{bloco}</span></th>" in r.text
    # D58 (Caio, 27/10/2026): nomes das linhas da saída e % dos recebidos em cada número da faixa
    assert "Entregues no Mês</th>" in r.text and "Ficou para o mês seguinte</th>" in r.text
    assert "Saiu no mês" not in r.text and "Saíram sem entrega" not in r.text
    assert r.text.count(">Declinados (Não teve seguimento)</button>") == 2  # faixa do topo e linha do quadro
    assert r.text.count('<span class="so-leitor"> dos recebidos</span>') == 3
    assert r.text.count('<tr class="quadro-pct">') == 1 and "quadro-pct-saiu" not in r.text  # uma só linha de %
    assert "do que havia para atender </span>%</button>" in r.text and 'id="conta-regra" role="tooltip"' in r.text
    assert "q-var" in r.text or "cresceu" not in r.text  # A28 só quando o que ficou muda
    # títulos fora da tela (a dica do "%" e a legenda do leitor de tela usam a frase, D58b)
    assert "ritmo-eixo-tit" not in r.text and 'class="painel-tit" aria-hidden="true">Quanto entregamos' not in r.text
    # dica dos status: botão com aria-describedby apontando para um role="tooltip" existente
    ids = re.findall(r'class="tipo-info q-(?:num|info)" aria-describedby="([^"]+)"', r.text)
    assert "sem-status-ano" in ids and "conta-regra" in ids and len(ids) >= 3
    for i in ids:
        assert f'id="{i}" role="tooltip"' in r.text
    jan = r.text.split('id="sem-status-2026-01" role="tooltip"')[1].split("</span></span>")[0]
    assert "Standby" in jan and "Total" in jan
    assert "entregamos a mais" in r.text and "entregamos a menos" in r.text and "resolvemos a" not in r.text


@pytest.mark.parametrize("rota, pergunta", [
    ("/viu-agenciamento", "Quanto a LIA já leu e quanto deixou de chegar à equipe?"),  # 04/11: Talentos oculta
    ("/viu-agenciamento/lia", "Quanto tempo levamos para entregar um orçamento?"),  # 04/11: LIA → SLA
    ("/viu-agenciamento/sla", "Quais iniciativas de automação e IA estamos tocando?")])  # SLA → Iniciativas; estudo pelo botão
def test_gancho_para_a_proxima_pagina(cliente, rota, pergunta):
    """D59 (27/10/2026): a pergunta da próxima página volta à tela como gancho (a D53 a deixava só para o leitor)."""
    html = cliente.get(rota).text
    nav = re.search(r'<nav class="proxima[^"]*"', html)
    assert nav and "so-leitor" not in nav.group(0) and "proxima-gancho" in nav.group(0)
    assert f'<span class="proxima-texto">{pergunta}</span>' in html
    assert 'rel="next"' in html  # o passador (PageDown) e o leitor de tela continuam com o link


def test_status_le_a_gold():
    assert dados.saidas_status.id_tabela.endswith(".gld_agenciamento_2026_saidas_status")
    assert dados.atendimento.gatilho == dados.fluxo.id_tabela  # view: recarga pela gold de fluxo
    assert "saidas_status" in dados.TABELAS and "atendimento" in dados.TABELAS
