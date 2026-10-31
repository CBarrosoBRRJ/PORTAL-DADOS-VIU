"""Batalha de agentes (25/10/2026): correções aprovadas no estudo "Como medimos" — típico perto da meta (C6) no slide 8,
nomes do Monday escapados, base dos % do tempo travado, recorte visível, exemplo fixo para a reunião, base congelada e
estudo guardado por carga e grupo (B-N8, A-N12, A-N5, B-N3, B-N6, B-ambiente-2, B-N7)."""

from datetime import date

import pandas as pd
from fastapi.testclient import TestClient

from app.apresentacoes.gestao_orcamentos.sla import calculos as c
from tests.test_sla_conclusao import _mov as _mov_conclusao
from tests.test_sla_tipo import _ps, _u


def test_z1_tipico_logo_acima_da_meta_nao_vira_16_h():
    # A-N12: 16,3 h é "16,3 h" (C6), em vermelho; nunca "16 h" em vermelho
    h = pd.Series([16.3] * 31 + [4.0] * 15 + [40.0] * 15)
    assert float(h.median()) == 16.3
    z = c._conclusao(h, {"a": 40, "b": 60, "hb": 80}, None, None, None)
    a1 = z["achados"][0]
    assert a1["valor"] == "16,3 h" and a1["cor"] == "problema"
    assert c.meta_tipico(16.3)["mediana_txt"] == a1["valor"]  # o mesmo texto do gancho do slide 1 e da página SLA


def test_numero_do_slide_8_igual_ao_texto_do_slide_de_origem():
    mov = _mov_conclusao("batalha-contrato")
    z = c.conclusao(mov, "2026-05", "todos")
    x, t, tr = c.exploracao(mov, "2026-05", "todos"), c.tempo_cem(mov, "2026-05"), c.travas(mov, "2026-05")
    a = {k["numero"]: k for k in z["achados"]}
    assert a[1]["valor"] == x["mediana_txt"] == x["tipico"]["mediana_txt"]
    assert a[2]["valor"] == f"{t['a']}%" and a[3]["valor"] == f"{t['hb']}%"
    assert a[5]["valor"] == f"{tr['status'][0]['pct']}%"


def test_base_do_tempo_travado_sobre_todas_as_horas():
    # B-N3: o tempo travado como parte de todas as horas da equipe do recorte, no achado 5 e no leitor do slide 6
    mov = _mov_conclusao("batalha-base")
    tr = c.travas(mov, "2026-05", "todos")
    u = c._universo_df(mov, "2026-05", "todos")
    assert tr["pct_horas"] == c._pontos(tr["total_h"] / float(u["h_trabalho"].sum()))
    assert f"O tempo travado é {tr['pct_horas']}% de todas as horas da equipe." in tr["intro"]
    a5 = c.conclusao(mov, "2026-05", "todos")["achados"][4]
    assert a5["frase"].startswith(f"do tempo travado ({tr['pct_horas']}% de todas as horas) fica em")
    # cartão: o limite do normal, não o típico de quem passou pelo status
    k = tr["status"][0]
    assert k["partes"][1] == f"acima de {k['limite_txt']}" and "o normal deste status" in k["leitor"]


def test_nomes_do_monday_escapados_antes_do_safe():
    # B-N6: status e Tipo de Input vêm do board; um '&' ou '<' não pode virar marcação
    ordem = [{"nome": "Em elaboração - A & <b>B", "pct": 70, "ate": None}, {"nome": "Fila", "pct": 20, "ate": None}]
    rod = c._trava_textos(ordem)["rodape"]
    assert "<strong>Em elaboração - A &amp; &lt;b&gt;B</strong>" in rod and "<b>B" not in rod
    u = _u([("X <i>", [8] * 50 + [30] * 50), ("Mercado", [8] * 60 + [30] * 40), ("ViU", [4] * 30)])
    v = c._tipos(u, _ps(u, {}), "2026-05")
    assert v["tipo"] == "destaque" and "<strong>O X &lt;i&gt; é o que mais demora</strong>" in v["rodape"]
    assert "<i>" not in v["rodape"]
    u = _u([("Mercado", [8] * 120 + [30] * 80), ("Inbound", [8] * 122 + [30] * 78), ("A & <b>", [8] * 10 + [30] * 20)])
    v = c._tipos(u, _ps(u, {}), "2026-05")
    assert "Só <strong>A &amp; &lt;b&gt;</strong>, de menor volume" in v["rodape"]


def test_recorte_visivel_igual_ao_universo(movimentos):
    # B-ambiente-2: período (meses completos), N do universo e grupo, nos slides 2–8; N = len(_universo_df)
    for g, rot in (("todos", "Todos"), ("exclusivos", "Exclusivos"), ("nao-exclusivos", "Não exclusivos")):
        r = c.recorte(movimentos, "2026-10", g)
        n = len(c._universo_df(movimentos, "2026-10", g))
        assert r["n"] == n and r["grupo"] == rot and r["periodo"] == "jan a set de 2026" and r["proximo"] == "outubro"
        assert r["texto"].startswith("jan a set de 2026 · ") and r["texto"].endswith(f" · {rot}")
    assert c.recorte(movimentos, "2026-02")["periodo"] == "jan de 2026"
    assert c.recorte(movimentos, "2026-01") is None
    from app.main import app

    with TestClient(app) as cli:
        html = cli.get("/viu-agenciamento/sla/como-medimos?talentos=exclusivos").text
    r = c.recorte(movimentos, "2026-10", "exclusivos")
    # V2 (30/10/2026, Caio: "não faz sentido ali"): o selo saiu da tela em todos os slides; fica para o leitor de tela
    assert html.count(f'<p class="so-leitor estudo-recorte">Recorte: {r["texto"]}</p>') == 4  # slides 2–5
    assert '<p class="estudo-recorte">' not in html
    assert "entra quando fechar" not in html  # o fecho do recorte era só da conclusão (V2: fora do estudo)


def test_exemplo_fixo_so_no_computador_ou_na_reuniao(movimentos, monkeypatch):
    # B-N8 (E4): ?exemplo=<projeto_id> revisado pelo Caio; inválido ou fora das regras E1 → o sorteio do dia
    dia = date(2026, 10, 24)
    assert c.exemplo(movimentos, "2026-10", "todos", dia, fixo="P5")["nome"] == "[Teste] P5"
    assert c.exemplo(movimentos, "2026-10", "todos", dia, fixo="nao-existe")["nome"] == "[Teste] P6"
    from app import config
    from app.apresentacoes.gestao_orcamentos import apresentacao as ap

    monkeypatch.setattr(config, "DEV", True)
    monkeypatch.setattr(config, "EM_PRODUCAO", False)
    assert ap.montar_estudo_sla({"exemplo": "P5"})["exemplo"]["nome"] == "[Teste] P5"
    monkeypatch.setattr(config, "EM_PRODUCAO", True)  # em produção, o parâmetro não vale
    assert ap.montar_estudo_sla({"exemplo": "P5"})["exemplo"]["nome"] != "[Teste] P5"
    monkeypatch.setattr(config, "EM_PRODUCAO", False)
    monkeypatch.setattr(config, "DEV", False)
    monkeypatch.setattr(config, "MODO_APRESENTACAO", False)
    assert ap.montar_estudo_sla({"exemplo": "P5"})["exemplo"]["nome"] != "[Teste] P5"


def test_base_congelada_nao_recarrega_e_avisa_no_rodape(monkeypatch):
    # B-N8: com CONGELAR, a base lida não se recarrega (nenhuma checagem do metadado) e o rodapé diz que está congelada
    from app import config, dados

    t = dados.Tabela("teste", "x.y.z")
    t._df = pd.DataFrame({"a": [1]})
    t._checado_em = -1e9
    monkeypatch.setattr(config, "CONGELAR", True)
    assert not t._vencido()
    monkeypatch.setattr(config, "CONGELAR", False)
    assert t._vencido()
    monkeypatch.setattr(config, "CONGELAR", True)
    from app.main import app

    with TestClient(app) as cli:
        html = cli.get("/viu-agenciamento/sla/como-medimos").text
    assert "· base congelada para a apresentação</p>" in html


def test_estudo_guardado_por_carga_e_grupo(movimentos):
    # B-N7: o estudo dos 3 grupos fica pronto na carga; o clique no seletor reaproveita; carga nova = conta nova
    from app.apresentacoes.gestao_orcamentos import apresentacao as ap

    ap._cache_estudo.clear()
    ap._aquecer_estudo(movimentos)
    assert len(ap._cache_estudo) == 3
    a = ap._estudo_slides(movimentos, "2026-10", "exclusivos")
    assert ap._estudo_slides(movimentos, "2026-10", "exclusivos") is a and len(ap._cache_estudo) == 3
    outra = movimentos.copy()
    outra.attrs["versao"] = "batalha-nova"
    assert ap._estudo_slides(outra, "2026-10", "exclusivos") is not a
    ap._cache_estudo.clear()
