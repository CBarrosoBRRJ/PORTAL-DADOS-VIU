"""Área como portal (D30): ordem da reunião, próxima pergunta, máscaras, "O que falta" e modo apresentação."""

import re

import gold_simulada  # views da gold sobre os dados sintéticos (D57)
import pytest
from fastapi.testclient import TestClient

from app import config
from app.apresentacoes.gestao_orcamentos import pendencias


@pytest.fixture
def cliente():
    from app.main import app

    with TestClient(app) as c:
        yield c


# D59 (27/10/2026): Resultado e Qualidade ocultos da navegação; a sequência termina na Previsão
# V2 (Caio, 30/10/2026): Linha do tempo antes da Demanda; sem Atendimento; LIA e Vídeo depois do SLA; Previsão por último
# Caio, 04/11/2026: Talentos oculta; a LIA vem logo depois da Demanda, antes do SLA
ORDEM = ["roadmap", "lia", "sla", "iniciativas", "previsao"]  # V2: o Vídeo virou pop-up da LIA (oculta)


def test_ordem_e_proxima_pergunta(cliente):
    r = cliente.get("/viu-agenciamento")
    abas = re.findall(r'href="/viu-agenciamento/([a-z-]+)#1"', r.text.split('data-navegador')[1].split('</nav>')[0])
    assert abas == ORDEM
    assert 'rel="next"' in r.text and "Quanto a LIA já leu" in r.text  # Início → LIA (04/11)
    assert "/viu-agenciamento/talentos" not in r.text.split("<main")[1]  # Talentos oculta, mas o endereço abre
    assert cliente.get("/viu-agenciamento/talentos").status_code == 200
    assert '<link rel="prev" href="/viu-agenciamento">' in cliente.get("/viu-agenciamento/lia").text
    r = cliente.get("/viu-agenciamento/previsao")  # V2: a Previsão é a última; depois dela, o encerramento
    assert 'href="/viu-agenciamento/encerramento" rel="next"' in r.text and "Para encerrar" in r.text
    assert "o-que-falta" not in r.text.split('<main')[1]
    assert '<link rel="prev" href="/viu-agenciamento/iniciativas#1">' in r.text
    r = cliente.get("/viu-agenciamento/sla")  # SLA → Iniciativas (04/11; o estudo abre pelo botão)
    assert 'href="/viu-agenciamento/iniciativas#1" rel="next"' in r.text
    for slug in ("negocios-fechados", "qualidade"):  # ocultas: fora do menu e das abas, mas o endereço abre
        assert f'/viu-agenciamento/{slug}' not in cliente.get("/viu-agenciamento/sla").text
        r = cliente.get(f"/viu-agenciamento/{slug}")
        assert r.status_code == 200 and 'rel="next"' not in r.text


def test_capa_e_encerramento(cliente):
    """D59 (Caio, 27/10/2026): capa antes da 1ª análise (roteiro com as perguntas na ordem) e encerramento depois da
    Previsão (agradecimento e pedidos de decisão); "Demanda" é a aba da página inicial; setas do teclado seguem
    data-pagina-*."""
    # D61: desenho do relatório de referência — título em duas linhas, "Começar", jornada de 6 etapas cujo relógio para
    # no típico do SLA (o mesmo número da página do SLA)
    r = cliente.get("/viu-agenciamento/capa")
    assert r.status_code == 200 and 'id="s-capa"' in r.text and "Agenciamento" in r.text  # capa nova (Caio, 03/11/2026)
    # V2 (Caio, 30/10/2026): o menu dos temas saiu (o Roadmap navega); no plano marinho, a ilustração decorativa, a frase
    # e o "Começar", que leva ao Roadmap; a jornada animada (capa.js) continua fora
    assert "capa-menu" not in r.text and '<script src="/static/capa.js' not in r.text
    assert 'class="cn-comecar" href="/viu-agenciamento/roadmap#1"' in r.text
    assert "A equipe está dando conta da demanda?" not in r.text  # V2: Atendimento fora do relatório
    assert 'href="/viu-agenciamento/roadmap#1" rel="next"' in r.text and "data-pagina-anterior" not in r.text  # 1ª página; V2: segue para o Roadmap
    assert "<span>Demanda</span>" in cliente.get("/viu-agenciamento/sla").text
    assert '<link rel="prev" href="/viu-agenciamento/roadmap#1">' in cliente.get("/viu-agenciamento").text  # V2
    assert '<link rel="prev" href="/viu-agenciamento/capa">' in cliente.get("/viu-agenciamento/roadmap").text
    r = cliente.get("/viu-agenciamento/encerramento")
    assert r.status_code == 200 and "Obrigado." in r.text and "Dúvidas e sugestões?" not in r.text and "ViU Agenciamento" in r.text  # Caio, 31/10
    # V2 (Caio, 31/10/2026): faixa branca com o logo, o mascote (balão de conversa que acena e pisca, decorativo) no canto
    # e o "Voltar ao início" amarelo no padrão do "Começar"; o movimento fica em fim.js + SMIL (sem script inline);
    # o fluxo à direita e a mão ao lado do título saíram (3ª rodada)
    assert re.search(r'<a class="fim-voltar" href="/viu-agenciamento/capa"><svg aria-hidden="true"[^>]*>.*?</svg>Voltar ao início</a>', r.text)
    assert 'class="fim-logo" src="/static/viu_logo.jpg" alt="VIU"' in r.text and '<svg class="fim-boneco" viewBox="0 0 160 180" aria-hidden="true"' in r.text
    assert "fim-desenho" not in r.text and "fim-mao" not in r.text and '<script src="/static/fim.js' in r.text
    assert "Próximo passo" not in r.text and "<script>" not in r.text
    assert 'rel="next"' not in r.text and "data-pagina-anterior" in r.text  # última página
    assert 'style="' not in r.text


def test_capas_de_secao_desligadas(cliente, monkeypatch):
    """D61: as capas de seção entre as páginas foram desligadas no mesmo dia (Caio: "enchem linguiça"); ficam só a capa
    e o encerramento. Religadas (capas_secao=CAPAS_SECAO), cada página leva a capa da próxima ("Parte n · nome")."""
    for rota in ("/viu-agenciamento/capa", "/viu-agenciamento", "/viu-agenciamento/atendimento"):
        assert "data-capa-secao" not in cliente.get(rota).text, rota
    from dataclasses import replace

    from app.apresentacoes.gestao_orcamentos import apresentacao as ap
    religada = replace(ap.APRESENTACAO, capas_secao=ap.CAPAS_SECAO)
    _, proxima = religada.vizinhas(religada.secao("lia"))  # 04/11: Demanda → LIA → SLA; Linha do tempo sem capa de seção
    assert proxima["capa_secao"]["parte"] == 2 and proxima["rotulo"] == "SLA"


def test_mascara_sem_numeros_e_com_pendencias(cliente):
    for slug in ("negocios-fechados", "qualidade"):  # previsão saiu da máscara (D47)
        r = cliente.get(f"/viu-agenciamento/{slug}")
        assert r.status_code == 200 and "Aguardando dados" in r.text
        bloco = r.text.split('<section class="pendente')[1].split("</section>")[0]
        for p in pendencias.da_secao(slug):
            assert p.dado in bloco
        assert 'style="' not in r.text


def test_o_que_falta(cliente):
    r = cliente.get("/viu-agenciamento/o-que-falta")
    assert r.status_code == 200 and "O que ainda precisamos para completar a área?" in r.text
    for p in pendencias.PENDENCIAS:
        assert f'id="{p.codigo}"' in r.text
    assert "Aguardando dados" in r.text and "Pronta" in r.text  # estado com ícone + texto
    assert 'aria-current="page"' in r.text.split('title="O que falta"')[1][:30]
    assert 'rel="next"' not in r.text  # fim da sequência
    codigos = [p.codigo for p in pendencias.PENDENCIAS]
    assert len(codigos) == len(set(codigos))


def test_modo_apresentacao_esconde_secoes(cliente, monkeypatch):
    monkeypatch.setattr(config, "MODO_APRESENTACAO", True)
    monkeypatch.setattr(config, "SECOES_VISIVEIS", frozenset({"atendimento", "sla"}))
    r = cliente.get("/viu-agenciamento")
    assert "/viu-agenciamento/previsao" not in r.text and "/viu-agenciamento/talentos" not in r.text
    assert cliente.get("/viu-agenciamento/previsao").status_code == 404
    assert cliente.get("/viu-agenciamento/atendimento").status_code == 200
    monkeypatch.setattr(config, "SECOES_VISIVEIS", frozenset())
    r = cliente.get("/viu-agenciamento/previsao?exemplo=1")
    assert "Exemplo com dados fictícios" not in r.text and 'id="pv-t-mercado"' in r.text  # D47: só dados reais


def test_talentos_divisao_sem_nomes(cliente):
    from app import dados
    from app.apresentacoes.gestao_orcamentos.talentos import calculos as tal

    r = cliente.get("/viu-agenciamento/talentos")
    # D50 (T8): resposta composta como no SLA, lida na ordem: "Da demanda do ano, 59% vai para os talentos exclusivos."
    assert r.status_code == 200 and "Da demanda do ano," in r.text and "exclusivos.</span>" in r.text
    assert "ainda não tem os mesmos pedidos" not in r.text  # total = Início (T5)
    assert "Talento não informado" in r.text and "Sem talento" not in r.text  # T2 (lista para leitor de tela)
    assert '<li class="talentos-sem-talento">' in r.text  # não informado também na legenda (pedido do Caio, 24/10)
    assert "Talento A" in r.text and "Talento C" in r.text  # nomes no mapa (T10, "todos" junta os dois grupos)
    top = tal.top_por_grupo(dados.talentos_top.df(), tal.divisao(dados.talentos.df(), int(dados.talentos.df().n.sum()),
                                                                  int(dados.talentos.df().ano[0])))
    assert top["exclusivo"]["linhas"][0]["posicao"] == 1 and top["exclusivo"]["n"] == 5  # soma dos 10 (aqui, 2)
    assert "Juntos, 6 pedidos" in r.text and "Squad de Talentos (grupo) fora" in r.text
    assert "recorte-etiqueta" not in r.text and "jan–" not in r.text  # sem etiqueta de período (pedido do Caio, 24/10)
    assert "Aguardando dados" not in r.text  # tela limpa: o que falta fica só em "O que falta" (pedido do Caio)
    df = dados.talentos.df()
    d = tal.divisao(df, int(df.n.sum()) + 7, int(df.ano[0]))
    assert d["diferenca"] == -7 and sum(g["pct"] for g in d["grupos"]) == 100  # T4, T5
    assert tal.divisao(df, 0, 1999) is None


def test_prazo_leituras_cauda_e_grupos(cliente, movimentos):
    from app import sla
    from app.apresentacoes.gestao_orcamentos.sla import calculos as C

    l = C.leituras(movimentos, sla.mes_parcial(movimentos))
    r = cliente.get("/viu-agenciamento/sla")
    assert "A demora vem de poucos pedidos?" not in r.text and 'data-proximo' not in r.text  # uma página só (24/10)
    if l is None:  # base sintética pequena (C12 pede ≥ 30 pedidos)
        return
    assert sum(f["pct_pedidos"] for f in l["faixas"]) == 100 and sum(f["pct_horas"] for f in l["faixas"]) == 100
    assert [g["chave"] for g in l["grupos"]] == ["exclusivos", "nao-exclusivos"]


def test_fluxo_mes_fecha_a_conta(entrada_diaria, fluxo_mensal):
    """A15: represados + novos = para atender = entregues + sem entrega + seguem; represados = fila do mês anterior."""
    from app.apresentacoes.gestao_orcamentos.atendimento import calculos as at

    a = at.atendimento(entrada_diaria, fluxo_mensal, gold_simulada.atendimento_mensal(entrada_diaria, fluxo_mensal))
    f = at.fluxo_mes(a)
    if f is None:
        return
    assert f["represados"] + f["novos"] == f["total"] == f["entregues"] + f["sem_entrega"] + f["seguem"]
    com_fila = [m for m in a["meses"] if m.get("fila") is not None]
    assert f["represados"] == (com_fila[-2]["fila"] if len(com_fila) > 1 else 0)
    assert all(fx["d"].startswith("M") and fx["d"].endswith("Z") for fx in f["faixas"])


def test_analise_ritmo(entrada_diaria, fluxo_mensal):
    """A16: acumulados batem com os totais; correlação entre -1 e 1; mês parcial fora da estatística."""
    from app.apresentacoes.gestao_orcamentos.atendimento import calculos as at

    a = at.atendimento(entrada_diaria, fluxo_mensal, gold_simulada.atendimento_mensal(entrada_diaria, fluxo_mensal))
    r = at.analise_ritmo(a)
    if r is None:
        return
    fim = r["acumulado"]["fim"]
    assert fim["rec"] - fim["res"] == fim["seguem"]
    d = r["dispersao"]
    assert d["corr"] is None or -1 <= d["corr"] <= 1
    assert d["n"] == sum(1 for p in d["pontos"] if not p["parcial"])


def test_abertos_por_mes_de_entrada(entrada_diaria, fluxo_mensal):
    """A17: soma dos em andamento por mês = em andamento do ano (situação da gold)."""
    from app.apresentacoes.gestao_orcamentos.atendimento import calculos as at

    a = at.atendimento(entrada_diaria, fluxo_mensal, gold_simulada.atendimento_mensal(entrada_diaria, fluxo_mensal))
    r = at.analise_ritmo(a)
    if r is None:
        return
    ab = r["abertos"]
    ano = next(g["n"] for g in a["situacao"] if g["classe"] == "andamento")
    assert ab["total"] == ano and ab["antigos"] + ab["atual"]["n"] == ab["total"]


def test_grafico_de_controle(entrada_diaria, fluxo_mensal):
    """A18: limites em torno da média; mês parcial não entra na conta; barras da fila = fila de cada mês."""
    from app.apresentacoes.gestao_orcamentos.atendimento import calculos as at

    a = at.atendimento(entrada_diaria, fluxo_mensal, gold_simulada.atendimento_mensal(entrada_diaria, fluxo_mensal))
    r = at.analise_ritmo(a)
    if r is None:
        return
    ct = r["controle"]
    assert [q["rotulo"] for q in ct["pontos"]] == [m["rotulo"] for m in a["meses"] if m.get("fila") is not None]  # meses em ordem
    assert ct["n"] == sum(1 for q in ct["pontos"] if not q["parcial"]) and 0 <= ct["acima"] <= ct["n"]
    # A18: soma dos represados de cada mês (delta) = o que segue em andamento hoje
    assert r["acumulado"]["delta_soma"] == r["acumulado"]["fim"]["seguem"]


def test_sombra_do_mes(entrada_diaria, fluxo_mensal):
    """A19: para atender = represados do mês anterior + novos = resolvidos + represado; janeiro começa sem represados."""
    from app.apresentacoes.gestao_orcamentos.atendimento import calculos as at

    a = at.atendimento(entrada_diaria, fluxo_mensal, gold_simulada.atendimento_mensal(entrada_diaria, fluxo_mensal))
    r = at.analise_ritmo(a)
    if r is None:
        return
    cols = r["sombra"]["colunas"]
    assert cols[0]["veio"] == 0
    for ant, c in zip([None] + cols[:-1], cols):
        assert c["demanda"] == c["veio"] + c["novos"] == c["resolvidos"] + c["represado"]
        if ant:
            assert c["veio"] == ant["represado"]


def test_folego_do_represado(entrada_diaria, fluxo_mensal):
    """A21: dias de trabalho = represado ÷ (resolvidos ÷ dias úteis); dias úteis positivos nos meses com movimento."""
    from app.apresentacoes.gestao_orcamentos.atendimento import calculos as at

    a = at.atendimento(entrada_diaria, fluxo_mensal, gold_simulada.atendimento_mensal(entrada_diaria, fluxo_mensal))
    r = at.analise_ritmo(a)
    if r is None:
        return
    for q in r["folego"]["pontos"]:
        assert q["uteis"] > 0
        if q["ritmo"]:
            assert abs(q["dias"] - q["fila"] / q["ritmo"]) < 1e-9


def test_conta_por_tras_do_percentual(entrada_diaria, fluxo_mensal):
    """A22: para atender = veio + novos = resolvidos + fica; o represado de um mês é o que vem no seguinte."""
    from app.apresentacoes.gestao_orcamentos.atendimento import calculos as at

    a = at.atendimento(entrada_diaria, fluxo_mensal, gold_simulada.atendimento_mensal(entrada_diaria, fluxo_mensal))
    r = at.analise_ritmo(a)
    if r is None:
        return
    pts = r["dispersao"]["pontos"]
    for ant, q in zip([None] + pts[:-1], pts):
        assert q["atender"] == q["veio"] + q["novos"] == q["entregues"] + q["sem"] + q["fica"]
        assert q["veio"] == (ant["fica"] if ant else 0)


def test_linhas_mes_a_mes(entrada_diaria, fluxo_mensal):
    """A23: uma faixa por trecho entre meses (duas quando as linhas se cruzam)."""
    from app.apresentacoes.gestao_orcamentos.atendimento import calculos as at

    a = at.atendimento(entrada_diaria, fluxo_mensal, gold_simulada.atendimento_mensal(entrada_diaria, fluxo_mensal))
    r = at.analise_ritmo(a)
    if r is None:
        return
    ln = r["linhas"]
    n = len(ln["pontos"])
    assert n - 1 <= len(ln["faixas"]) <= 2 * (n - 1)
    assert all(f["classe"] in ("mais", "menos") for f in ln["faixas"])


def test_tendencias_mes_a_mes(entrada_diaria, fluxo_mensal):
    """A23: um rótulo por mês com os números de cada série; tendência só com meses completos."""
    from app.apresentacoes.gestao_orcamentos.atendimento import calculos as at

    a = at.atendimento(entrada_diaria, fluxo_mensal, gold_simulada.atendimento_mensal(entrada_diaria, fluxo_mensal))
    r = at.analise_ritmo(a)
    if r is None:
        return
    ln = r["linhas"]
    assert len(ln["rotulos"]) == len(ln["pontos"])
    assert all(t["rec"] >= 0 and t["res"] >= 0 for t in ln["rotulos"])


def test_quadro_da_demanda(entrada_diaria, fluxo_mensal):
    """A24: veio + entrou = para atender = resolvemos + ficou; o ficou de um mês é o veio do seguinte."""
    from app.apresentacoes.gestao_orcamentos.atendimento import calculos as at

    a = at.atendimento(entrada_diaria, fluxo_mensal, gold_simulada.atendimento_mensal(entrada_diaria, fluxo_mensal))
    r = at.analise_ritmo(a)
    if r is None:
        return
    L = {l["chave"]: [c["v"] for c in l["celulas"]] for l in r["quadro"]["linhas"]}
    for i in range(len(L["entrou"])):
        assert L["veio"][i] + L["entrou"][i] == L["atender"][i] == L["entregues"][i] + L["sem"][i] + L["ficou"][i]
        assert L["entregues"][i] + L["sem"][i] == L["saiu"][i] and L["atender"][i] - L["saiu"][i] == L["ficou"][i]  # A24b
        if i:
            assert L["veio"][i] == L["ficou"][i - 1]


def test_percentual_sobre_a_demanda_total(entrada_diaria, fluxo_mensal):
    """A30 (D58b): % = entregues no mês (entregues ao cliente + declinados) ÷ (represados que vieram + novos); corte ≤
    objetivo; nunca acima de 100%."""
    from app.apresentacoes.gestao_orcamentos.atendimento import calculos as at

    a = at.atendimento(entrada_diaria, fluxo_mensal, gold_simulada.atendimento_mensal(entrada_diaria, fluxo_mensal))
    r = at.analise_ritmo(a)
    if r is None:
        return
    d = r["dispersao"]
    assert d["corte"]["pct"] <= d["objetivo"]["pct"]
    for q in d["pontos"]:
        assert q["pct"] == at.pct_meio(q["res"], q["atender"]) and q["pct"] <= 100 and q["ent"] <= q["res"]
    assert r["quadro"]["pct"] == [q["pct"] for q in d["pontos"]]
