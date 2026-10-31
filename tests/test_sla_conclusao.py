"""D44 (25/10/2026, Caio): slide 8 do estudo "Como medimos" — "O que os dados nos mostraram". Seis achados tirados das
mesmas funções dos slides 2–7 (nada fixo), cores por regra, "Onde olhar com mais detalhe" e "O que isso pede" (Z1–Z8)."""

import re
import pandas as pd
from fastapi.testclient import TestClient

from app.apresentacoes.gestao_orcamentos.sla import calculos as c
from tests.test_sla_tipo import _mov as _mov_tipo
import gold_simulada  # views da gold sobre os dados sintéticos (D57)


def _mov(versao: str) -> pd.DataFrame:
    """120 orçamentos de jan a abr: 1/3 Inbound com 5 h de fila, o resto Mercado (todos com 6 h); mais 30 Inbound parados
    na fila por uma semana (41 h úteis)."""
    base = _mov_tipo(versao)
    extra = []
    for i in range(30):
        d = ["2026-01-12", "2026-02-02", "2026-03-09", "2026-04-13"][i % 4]
        b = {"projeto_id": f"L{i}", "exclusivo": True, "nome_projeto": f"L{i}", "sla_util_horas": None, "tipo_de_input": "Inbound"}
        extra += [{**b, "passo": 1, "status": "Entrada", "fase": "equipe", "entrada": pd.Timestamp(f"{d} 10:00"),
                   "saida": pd.Timestamp(f"{d} 11:00") + pd.Timedelta(days=7)},
                  {**b, "passo": 2, "status": "Aguardando Feedback", "fase": "cliente",
                   "entrada": pd.Timestamp(f"{d} 11:00") + pd.Timedelta(days=7), "saida": pd.NaT}]
    df = pd.concat([base, pd.DataFrame(extra).assign(_processado_em=base["_processado_em"].iloc[0])], ignore_index=True)
    df = gold_simulada.com_sem_almoco(df)  # R24 da gold
    df.attrs["versao"] = versao
    return df


def test_numeros_iguais_aos_slides_de_origem():
    mov = _mov("d44-a")
    z = c.conclusao(mov, "2026-05", "todos")
    t, tr, tp = c.tempo_cem(mov, "2026-05"), c.travas(mov, "2026-05"), c.tipos_pedido(mov, "2026-05")
    h = c._universo(mov, "2026-05", "todos")
    a = {x["numero"]: x for x in z["achados"]}
    assert a[1]["valor"] == c._h(float(h.median())) and f"A média, {c._h(float(h.mean()))}" in a[1]["frase"]
    assert a[2]["valor"] == f"{t['a']}%" == f"{c.cem_pedidos(mov, '2026-05')['a']}%"
    assert a[3]["valor"] == f"{t['hb']}%" and f"para os {t['b']}% que levam" in a[3]["frase"]
    s1 = tr["status"][0]
    assert s1["nome"] == "Fila de entrada" and a[5]["titulo"] == "Trava em um ponto" and a[5]["valor"] == f"{s1['pct']}%"
    pior = next(r for r in tp["linhas"] if r["destaque"])
    assert a[6]["titulo"] == f"Pesa mais no {pior['tipo']}" and a[6]["valor"] == f"{pior['b']}%"
    assert "é onde a fila de entrada mais pesa." in a[6]["frase"]
    assert [x["cor"] for x in z["achados"]][2:] == ["problema"] * 4
    # Z7: o status de maior trava com a pergunta da fila (citando o tipo, pois é onde ele mais trava) e os acima de 5 dias
    assert z["olhar"][0] == {"titulo": "Fila de entrada",
                             "texto": f"Por que o pedido espera antes de começar, principalmente no {pior['tipo']}?"}
    n5 = int((h > 40).sum())
    assert n5 == 30 and len(z["olhar"]) == 2  # Orçamentos não travou: só a fila entra em "onde olhar"
    assert z["olhar"][-1]["titulo"] == "Pedidos acima de 5 dias" and f"({n5} pedidos)" in z["olhar"][-1]["texto"]
    assert "de cada 100" not in str(z) and "mediana" not in str(z).lower()


def _h(n_rapido: int, n_lento: int) -> pd.Series:
    return pd.Series([4.0] * n_rapido + [30.0] * n_lento)


def _tempo(a, hb=80):
    return {"a": a, "b": 100 - a, "hb": hb}


def test_variantes_z1_z2_z3():
    z = c._conclusao(_h(40, 10), _tempo(80), None, None, None)
    a = z["achados"]
    assert a[0]["cor"] == "bom" and a[1]["titulo"] == "A maioria é rápida" and a[1]["cor"] == "bom"
    assert c._conclusao(_h(20, 20), _tempo(50), None, None, None)["achados"][1]["titulo"] == "Metade é rápida"
    z = c._conclusao(_h(10, 30), _tempo(25), None, None, None)
    assert z["achados"][0]["cor"] == "problema"  # típico 30 h, acima de 16 h
    assert z["achados"][1]["titulo"] == "Menos da metade é rápida" and z["achados"][1]["cor"] == "problema"
    z = c._conclusao(_h(40, 0), _tempo(100, 0), None, None, None)
    assert z["achados"][2]["titulo"] == "Ninguém passa de 2 dias" and z["achados"][2]["cor"] == "bom"
    assert z["achados"][0]["frase"].endswith("fica perto.")
    assert z["olhar"] == [{"titulo": "Pedidos acima de 5 dias", "texto": "Nenhum pedido passa de 5 dias de trabalho."}]
    assert c._conclusao(_h(10, 10), _tempo(50), None, None, None) is None  # menos de 30


def _meses(tipo, resumo, ns=(100,) * 6):
    return {"tipo": tipo, "resumo": resumo, "meses": [{"n": n, "vazio": False} for n in ns]}


def test_variantes_z4():
    h = _h(40, 10)
    f = lambda m: c._conclusao(h, _tempo(80), m, None, None)["achados"][3]  # noqa: E731
    a = f(_meses("padrao", {"b0": 40, "b1": 51}, (100, 100, 100, 130, 130, 130)))
    assert (a["titulo"], a["valor"]) == ("Não é crise, é padrão", "todo mês")
    assert a["frase"] == "de 40% a 51% passam de 2 dias, mesmo com o volume crescendo."
    assert f(_meses("padrao", {"b0": 40, "b1": 51}, (100, 100, 100, 120, 120, 120)))["frase"] == "de 40% a 51% passam de 2 dias."
    assert f(_meses("padrao", {"b0": 40, "b1": 40}, (10, 10, 50)))["frase"] == "40% passam de 2 dias."  # < 6 meses
    a = f(_meses("raro", {"b0": 2, "b1": 8}))
    assert a["titulo"] == "O prazo se mantém" and a["cor"] == "bom" and a["frase"] == "só de 2% a 8% passam de 2 dias."
    a = f(_meses("picos", {"b0": 30, "b1": 40, "nomes": "abril", "verbo": "fugiu"}))
    assert a["valor"] == "quase todo mês" and a["frase"] == "de 30% a 40% passam de 2 dias; só abril fugiu."
    a = f(_meses("sazonal", {"d0": 70, "d1": 75, "contra": "43% a 60%", "quando": "em abril, maio e agosto",
                             "curto": "abr, mai e ago"}))
    assert a["valor"] == "abr, mai e ago" and a["longo"] and a["frase"].startswith("De 70% a 75% passam de 2 dias, contra 43% a 60%")
    assert "em abril, maio e agosto" in a["leitor"]


def _trava(tipo, ordem):
    return {"tipo": tipo, "status": [{"nome": n, "pct": p, "etapa": e, "ate": at} for n, p, e, at in ordem]}


def test_variantes_z5_e_perguntas_z7():
    h = _h(40, 10)
    f = lambda t: c._conclusao(h, _tempo(80), None, t, None)  # noqa: E731
    z = f(_trava("dois", [("Em elaboração", 41, "Elaboração", "jul"), ("Fila de entrada", 19, "Entrada", None)]))
    a = z["achados"][3]
    assert (a["titulo"], a["valor"]) == ("Trava em dois pontos", "60%")
    assert a["frase"] == "do tempo travado fica em dois status: Em elaboração (só até jul) e Fila de entrada."
    assert z["olhar"][0] == {"titulo": "Em elaboração (só até jul)",
                             "texto": "O que segura o orçamento? Falta de informação do pedido, cotações, vai e volta?"}
    assert z["olhar"][1]["texto"] == "Por que o pedido espera antes de começar?"
    z = f(_trava("um", [("Produção", 70, "Elaboração", None), ("Validação Talento", 10, "Revisão", None)]))
    assert z["achados"][3]["titulo"] == "Trava em um ponto" and z["achados"][3]["valor"] == "70%"
    assert z["olhar"][0]["texto"].startswith("O que segura a produção?")
    assert z["olhar"][1]["texto"].startswith("O que faz a validação demorar?")
    z = f(_trava("espalhado", [("Em revisão", 18, "Revisão", None), ("Cotação Externa", 15, "Elaboração", None)]))
    assert z["achados"][3]["titulo"] == "Trava espalhado" and z["achados"][3]["valor"] == "33%"
    assert z["olhar"][0]["texto"].startswith("O que faz a revisão demorar?")
    assert z["olhar"][1]["texto"].startswith("O que atrasa a cotação?")


def _linha(tipo, b, destaque=False, vermelho=False, etapa="Elaboração"):
    return {"tipo": tipo, "b": b, "destaque": destaque, "vermelho": vermelho, "trava": {"etapa": etapa, "p": 40}}


def test_variantes_z6():
    h = _h(40, 10)
    f = lambda t: c._conclusao(h, _tempo(80), None, None, t)["achados"][3]  # noqa: E731
    merc, inb = _linha("Mercado", 45), _linha("Inbound", 43)
    pro = _linha("Proativo", 67, vermelho=True)
    t = {"tipo": "parecido", "geral": {"b": 44}, "linhas": [merc, inb, pro],
         "grupos": [{"chave": "maior", "linhas": [merc, inb]}, {"chave": "menor", "linhas": [pro]}]}
    a = f(t)
    assert (a["titulo"], a["valor"], a["cor"]) == ("Os tipos se parecem", "43–45%", "problema")
    assert a["frase"] == "nos tipos de maior volume passam de 2 dias, perto dos 44% do geral. Exceção: Proativo."
    t1 = {"tipo": "parecido", "geral": {"b": 59}, "linhas": [_linha("Mercado", 59)],
          "grupos": [{"chave": "maior", "linhas": [_linha("Mercado", 59)]}]}
    a = f(t1)
    assert a["titulo"] == "O Mercado segue o geral" and a["valor"] == "59%" and a["cor"] == "bom"
    inb2 = _linha("Inbound", 50, destaque=True, vermelho=True, etapa="Revisão")
    a = f({"tipo": "destaque", "geral": {"b": 40}, "linhas": [merc, inb2], "grupos": []})
    assert a["titulo"] == "Pesa mais no Inbound" and a["frase"] == "dos pedidos Inbound passam de 2 dias; é onde a revisão mais pesa."
    assert len(c._conclusao(h, _tempo(80), None, None, {"tipo": "sem-tipos"})["achados"]) == 3  # sem tipos: sem achado


def test_conclusao_fora_do_estudo(monkeypatch):
    """V2 (30/10/2026, Caio): a conclusão (era o 7 de 7) saiu do estudo; o cálculo Z1–Z8 continua. O último slide passa
    a ser "Onde o tempo trava?", com a saída do estudo (volta ao SLA e a próxima página da sequência)."""
    from app import dados, sla
    from app.main import app

    mov = _mov("d44-html")
    monkeypatch.setattr(dados.sla, "df", lambda forcar=False: mov)
    sla._cache.clear()
    with TestClient(app) as cli:
        html = cli.get("/viu-agenciamento/sla/como-medimos?talentos=todos").text
    sla._cache.clear()
    assert html.count('class="slide slide-estudo') == 5
    assert 'slide-conclusao"' not in html and "O que os dados nos mostraram" not in html and 'slide-tipo"' not in html
    s5 = html.split('slide-trava"')[1]
    # V2 (30/10/2026, Caio): os links da saída saíram da tela; o ✕ do último slide é o sinal de fim e volta ao SLA
    assert "Voltar ao SLA" not in s5 and "ou seguir para a próxima" not in s5
    assert 'class="fechar-estudo fechar-fim" href="/viu-agenciamento/sla?talentos=todos#1" aria-label="Fim do estudo: voltar ao SLA" title="Fim do estudo"' in s5
    assert html.count("fechar-fim") == 1  # só no último slide
    assert "E o que os dados nos mostraram?" not in s5
