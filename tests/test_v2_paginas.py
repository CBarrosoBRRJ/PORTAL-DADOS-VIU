"""V2 (30/10/2026): páginas novas — Iniciativas, LIA (e-mails e leads; antes × depois), A LIA na prática (vídeo), Roadmap — e a capa sem o menu dos temas, com o "Começar" para o Roadmap. Conteúdo fixo ou retrato; nenhuma consulta ao BigQuery."""

import itertools
import json
import math
import re
from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient

from app.apresentacoes.gestao_orcamentos import (
    iniciativas,
    lia,
    lia_na_pratica,
    roadmap,
)
from app.apresentacoes.gestao_orcamentos.iniciativas import catalogo


@pytest.fixture
def cliente():
    from app.main import app

    with TestClient(app) as c:
        yield c


FASES = ["Em produção", "Fase de testes", "Em desenvolvimento", "Na esteira"]


def test_capa_sem_menu_com_comecar_para_o_roadmap(cliente):
    """V2 (Caio, 30/10/2026): sem o menu dos temas; o Roadmap faz a navegação. Capa nova aplicada em 03/11/2026 (Caio):
    sem o subtítulo, sem textos no desenho e sem o rodapé datado; o "Começar" leva ao Roadmap. Loop contínuo só na capa
    (autorizado pelo Caio), parado com movimento reduzido e com a aba oculta (capa_nova.js). Detalhes em
    tests/test_capa_nova.py."""
    html = cliente.get("/viu-agenciamento/capa").text
    assert "capa-menu" not in html and "Temas</p>" not in html
    assert html.count('class="cn-comecar"') == 1
    assert '<a class="cn-comecar" href="/viu-agenciamento/roadmap#1">Começar' in html
    assert '<div class="cn-desenho" aria-hidden="true">' in html
    assert "Tudo o que a área analisa" not in html and "rodape-dados" not in html
    assert 'href="/viu-agenciamento/roadmap#1" rel="next"' in html  # seta → e passador seguem para o Roadmap
    assert 'style="' not in html  # CSP
    assert 'repeatCount="indefinite"' in html and "capa-pausa" not in html
    assert '<script src="/static/capa_nova.js' in html
    for outra in ("/viu-agenciamento", "/viu-agenciamento/roadmap", "/viu-agenciamento/sla"):
        assert "repeatCount" not in cliente.get(outra).text, outra
    from pathlib import Path

    js = (Path(__file__).resolve().parents[1] / "app" / "static" / "capa_nova.js").read_text(encoding="utf-8")
    assert "pauseAnimations" in js and "visibilitychange" in js and "prefers-reduced-motion" in js

def test_iniciativas_colunas_quadros_e_painel(cliente, quadro_limpo):
    t = iniciativas.tela()
    assert [g["titulo"] for g in t["grupos"]] == FASES
    assert [g["nivel"] for g in t["grupos"]] == [4, 3, 2, 1]  # medidor: a mais madura acende tudo
    assert t["total"] == sum(len(g["itens"]) for g in t["grupos"]) == 13
    html = cliente.get("/viu-agenciamento/iniciativas").text
    # colunas na ordem do catálogo, com a contagem escrita (não só cor)
    posicoes = [html.index(f'>{f}</h3>') for f in FASES]
    assert posicoes == sorted(posicoes)
    assert '<span class="ini-num">2</span><span class="so-leitor"> iniciativas</span>' in html
    # sem JS: cada quadro é um details nativo com o detalhe dentro; Fechar e Expandir só aparecem com JS (hidden)
    assert html.count('<details class="ini-quadro">') == 13
    assert html.count('role="group" aria-label="Descrição: ') == 13
    assert html.count('data-ini-fechar hidden>') == 13
    assert html.count('data-ini-expandir aria-haspopup="dialog" hidden>') == 13
    assert 'class="ini-painel"' in html and "13</span> iniciativas" in html
    # só a LIA tem página própria: botão "Ver resultados"
    assert html.count('class="ini-botao ini-botao-forte" href="/viu-agenciamento/lia#1"') == 1
    assert 'src="/static/iniciativas.js' in html and 'style="' not in html
    assert "ini-referencia" not in html  # REFERENCIA vazia: sem nota (RF9)
    # sem linhas animadas de fundo (saíram a pedido do Caio): a página não tem loop
    assert "ini-fluxo" not in html


def test_iniciativas_item_sem_sigla_usa_o_nome(monkeypatch, quadro_limpo):
    grupos = ({"chave": "producao", "titulo": "Em produção", "sub": "", "itens": (
        {"sigla": "", "nome": "Projeto novo", "curta": "Resumo", "desc": ""},)},)
    monkeypatch.setattr(catalogo, "GRUPOS", grupos)  # antes da 1ª leitura: a semente usa este catálogo
    t = iniciativas.tela()
    item = t["grupos"][0]["itens"][0]
    assert item["titulo"] == "Projeto novo" and item["texto"] == "Resumo"  # RF3 e RF4
    assert item["link"] is None and t["grupos"][0]["nivel"] == 1 and t["total"] == 1


def test_iniciativas_ferramenta_grava_no_servidor(cliente, quadro_limpo):
    """Ferramenta do quadro (Caio, 30/10/2026; dados no servidor na mesma noite): arrastar entre fases e na ordem, lápis
    e "+ Nova iniciativa" abrem um pop-up (<dialog>) com sigla, nome, fase, responsável, descrição, status, próximo passo
    e anexos; ✕ exclui. Tudo vai à API (fetch com X-Requested-With); o localStorage só é lido para a importação única.
    Sem JS: ferramentas hidden e pop-ups fechados (só leitura)."""
    t = iniciativas.tela()
    ids = [i["id"] for g in t["grupos"] for i in g["itens"]]
    assert len(set(ids)) == 13 and ids[:2] == ["lia", "gps"] and "orca-ai" in ids and "auto" in ids  # estáveis e únicos
    html = cliente.get("/viu-agenciamento/iniciativas").text
    for chave in ("producao", "testes", "desenvolvimento", "esteira"):
        assert f'data-ini-fase="{chave}"' in html
    assert html.count('<li class="ini-item" data-ini-id="') == 13
    assert ('<li class="ini-item" data-ini-id="lia" data-ini-sigla="LIA" data-ini-nome="Leitura Inteligente Automatizada" '
            'data-ini-resp="" data-ini-status="" data-ini-prox="">') in html
    assert 'data-ini-api="/viu-agenciamento/iniciativas/api" data-ini-edicao="on" data-ini-semente="1"' in html
    # botões com nome acessível; sem JS ficam ocultos
    assert html.count('class="ini-ferramentas" data-ini-ferramentas hidden>') == 13
    assert 'data-ini-editar aria-label="Editar iniciativa: LIA"' in html
    assert 'data-ini-excluir aria-label="Excluir do quadro: LIA"' in html
    assert html.count("data-ini-editar") == html.count("data-ini-excluir") == 13
    assert html.count('data-ini-nova hidden aria-label="Nova iniciativa em ') == 4
    assert "class=\"ini-edicao" not in html and "Restaurar o catálogo" not in html and "Copiar resumo" not in html
    assert "13</span> iniciativas" in html and "Clique em uma iniciativa para ver o que ela faz." in html
    assert html.count("<dt>Responsável</dt><dd>a definir</dd>") == 13
    # pop-ups: fechados sem JS; campos com rótulo; erro ligável; anexos com rótulo e dica; visor e visão ampliada
    assert '<dialog class="ini-dialogo" data-ini-dialogo aria-labelledby="ini-d-titulo">' in html and "<dialog open" not in html
    for campo, rotulo in (("sigla", "Sigla"), ("nome", "Nome / título"), ("fase", "Fase"), ("resp", "Responsável")):
        assert f'<label for="ini-d-{campo}">{rotulo}</label>' in html
    assert '<textarea id="ini-d-desc"' in html and 'id="ini-d-status"' in html and 'id="ini-d-prox"' in html
    assert 'id="ini-d-erro" hidden>Preencha a sigla ou o nome.' in html
    assert 'for="ini-d-arquivo"' in html and 'accept=".png,.jpg,.jpeg,.webp,.gif,.pdf"' in html and ".svg" not in html
    assert "Salvo no servidor: vale para todos que abrirem o portal." in html
    assert '<dialog class="ini-ampliado"' in html and '<dialog class="ini-visor"' in html
    assert 'aria-label="Anexo anterior"' in html and 'aria-label="Próximo anexo"' in html
    assert all(f'<option value="{c}">{f}</option>' in html for c, f in
               zip(("producao", "testes", "desenvolvimento", "esteira"), FASES))
    assert 'aria-live="polite" data-ini-anuncio' in html and 'data-ini-estado aria-live="polite" hidden' in html
    assert html.count('<details class="ini-quadro">') == 13 and 'style="' not in html  # CSP; details segue nativo
    from pathlib import Path

    js = (Path(__file__).resolve().parents[1] / "app" / "static" / "iniciativas.js").read_text(encoding="utf-8")
    assert "fetch(" in js and '"X-Requested-With": "iniciativas"' in js and "showModal" in js
    assert '"ini-quadro:v1"' in js and "localStorage.setItem" not in js  # só lê (importação) e apaga a chave antiga
    assert "/mover" in js and "/anexos" in js and "/importar" in js
    assert "pointerdown" in js and "d > 6" in js  # limiar: arrasto não vira clique
    assert "bloquearClique" in js and "ArrowLeft" in js and "e.altKey" in js and "so-leitor" in js
    assert 'setAttribute("style"' not in js and ".style.cssText" not in js and "innerHTML" not in js
    assert "n <= 3 ? 1 : n === 4 ? 2 : 3" in js  # densidade igual à do servidor


def test_iniciativas_densidade_por_coluna(monkeypatch, quadro_limpo):
    """Coluna que enche fica mais compacta (1 até 3 cartões, 2 com 4, 3 com 5 ou mais) e, acima do que cabe, rola
    por dentro (CSS). Testado com 8 cartões numa coluna e 4 em todas."""
    assert [iniciativas.densidade(n) for n in (0, 3, 4, 5, 6, 8, 12)] == [1, 1, 2, 3, 3, 3, 3]
    item = {"sigla": "X", "nome": "Nome", "curta": "", "desc": "d"}
    grupos = tuple({"chave": c, "titulo": f, "sub": "", "itens": tuple(dict(item, sigla=f"{c}{k}") for k in range(n))}
                   for c, f, n in (("producao", "Em produção", 4), ("testes", "Fase de testes", 4),
                                   ("desenvolvimento", "Em desenvolvimento", 4), ("esteira", "Na esteira", 8)))
    monkeypatch.setattr(catalogo, "GRUPOS", grupos)
    t = iniciativas.tela()
    assert [g["densidade"] for g in t["grupos"]] == [2, 2, 2, 3] and t["total"] == 20
    from app.main import app

    with TestClient(app) as c:
        html = c.get("/viu-agenciamento/iniciativas").text
    assert html.count('data-densidade="2"') == 3 and html.count('data-densidade="3"') == 1
    assert html.count('class="ini-item"') == 20 and 'style="' not in html


def test_lia_numeros_batem_com_o_retrato():
    r = json.loads(lia.RETRATO.read_text(encoding="utf-8"))
    tot = {k: sum(p[k] for p in r["periodos"]) for k in ("nao_lead", "lead", "validacao")}
    total = sum(tot.values())
    # as bases do retrato fecham no mesmo total: períodos, semanas, dias (todos, com zeros) e faixas de horário
    assert sum(s["nao_lead"] + s["lead"] + s["validacao"] for s in r["semanas"]) == total
    assert sum(d["nao_lead"] + d["lead"] + d["validacao"] for d in r["dias"]) == total
    assert sum(r["faixas"].values()) == total and r["faixas"]["fim_de_semana"] == r["fim_de_semana"]
    e = lia.tela()
    assert e["total"] == f"{total:,}".replace(",", ".")
    # fração: uma ordem só (não lead, lead, validação), larguras somam 100
    assert [f["nome"] for f in e["fracao"]] == ["Não lead", "Lead", "Validação"]
    assert abs(sum(f["largura"] for f in e["fracao"]) - 100) < 0.01
    assert [f["n"] for f in e["fracao"]] == [f"{tot[k]:,}".replace(",", ".") for k in ("nao_lead", "lead", "validacao")]
    # semanas: rótulo ISO, a mesma ordem da fração na pilha, partes somam o total, a mais alta = 100%
    assert max(s["h_total"] for s in e["semanas"]) == 100
    for s in e["semanas"]:
        assert [p["chave"] for p in s["partes"]] == ["nao_lead", "lead", "validacao"]
        assert sum(p["n"] for p in s["partes"]) == s["total"]
    assert e["semanas"][0]["iso"] == date.fromisoformat(r["semanas"][0]["inicio"]).isocalendar().week
    u = r["horas"]["util"]  # Caio, 30/10/2026: fora = antes das 10h + almoço 12h–13h + depois das 19h + fim de semana e feriado
    fora = sum(u[:10]) + sum(u[19:]) + sum(r["horas"]["fim_de_semana"]) + sum(r["horas"]["feriado"])  # almoço conta dentro
    assert e["fora"] == f"{fora:,}".replace(",", ".") and "expediente" not in lia.FORA


def _dia_sintetico(d, leads, per):
    """Um dia do retrato: `per` = leads por período (manhã, tarde, noite); 10 e-mails não lead em cada período."""
    periodos = {k: {"nao_lead": 10, "lead": n, "validacao": 0} for k, n in zip(("manha", "tarde", "noite"), per)}
    return {"data": d.isoformat(), "feriado": "Feriado" if d == date(2026, 9, 28) else "", "fim_de_semana": d.weekday() >= 5,
            "nao_lead": 30, "lead": sum(per), "validacao": 0, "fora": 0, "periodos": periodos}


def test_lia_padroes_dia_da_semana_e_periodo():
    # D-LIA-5: 4 semanas; segunda forte e sexta fraca de forma consistente; tarde com mais leads; feriado fora das médias
    dias, d = [], date(2026, 9, 21)
    base = {0: (3, 6, 1), 1: (2, 4, 1), 2: (2, 4, 1), 3: (2, 4, 1), 4: (0, 1, 0), 5: (0, 0, 0), 6: (0, 1, 0)}
    while d <= date(2026, 10, 18):
        dias.append(_dia_sintetico(d, None, base[d.weekday()] if d != date(2026, 9, 28) else (0, 0, 0)))
        d += timedelta(days=1)
    p = lia.padroes({"dias": dias})
    assert [(x["nome"], x["n"]) for x in p["dias"]] == [("segunda", 3), ("terça", 4), ("quarta", 4), ("quinta", 4), ("sexta", 4)]
    assert (p["forte"]["nome"], p["forte"]["leads_txt"], p["fraco"]["nome"], p["fraco"]["leads_txt"]) == ("segunda", "10,0", "sexta", "1,0")
    assert p["leitura_dia"] == "claro" and p["p_dia"] < lia.ALFA  # diferença consistente: "costuma"
    assert p["fds"]["n"] == 8 and p["n_uteis"] == 19
    assert p["lider"]["chave"] == "tarde" and p["leitura_periodo"] == "claro" and p["dias_lider"] == 19
    assert [c["rot"] for c in p["mapa"]] == ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb–dom"]
    assert p["mapa"][0]["c"][1]["leads"] == "6,0" and p["mapa"][0]["c"][1]["tom"] == 4 and p["mapa"][4]["c"][0]["tom"] == 0
    # sem padrão: todos os dias iguais -> "sem diferença clara"
    iguais = [_dia_sintetico(x["data"] and date.fromisoformat(x["data"]), None, (1, 1, 1)) for x in dias]
    q = lia.padroes({"dias": iguais})
    assert q["leitura_dia"] == "sem" and q["leitura_periodo"] == "sem"
    assert lia._periodo(date(2026, 9, 28), date(2026, 10, 4)) == "28/09–04/10"


def test_lia_ganho_e_quando_em_inteiros():
    """Caio, 30/10/2026: horas por semana pela mesma premissa, 1 em cada N chega à equipe, médias por dia útil inteiras
    (somas por dia da semana enganam: dias com contagens diferentes) e barra de 100% dos leads por período."""
    r = json.loads(lia.RETRATO.read_text(encoding="utf-8"))
    tot = {k: sum(p[k] for p in r["periodos"]) for k in ("nao_lead", "lead", "validacao")}
    total = sum(tot.values())
    t = lia.tela()
    horas = tot["nao_lead"] * lia.MINUTOS_TRIAGEM / 60
    assert t["horas_semana"] == f"{math.floor(horas / (len(r['dias']) / 7) + 0.5)}"
    assert t["uma_em"] == f"{math.floor(total / (tot['lead'] + tot['validacao']) + 0.5)}"
    assert t["nao_lead"] == f"{tot['nao_lead']:,}".replace(",", ".")
    pd = t["padroes"]
    assert all(isinstance(d["leads_int"], int) and d["leads_int"] == math.floor(d["leads"] + 0.5) for d in pd["dias"])
    assert max(d["largura"] for d in pd["dias"]) == 100
    # 6ª rodada (Caio, 30/10/2026): o bloco mostra e-mails de inbound (a LIA só vê inbound), média inteira por dia útil
    assert all(isinstance(d["mails_int"], int) and d["mails_int"] == math.floor(d["mails"] + 0.5) for d in pd["dias"])
    assert max(d["largura_mails"] for d in pd["dias"]) == 100 and pd["forte_mails"]["mails"] == max(d["mails"] for d in pd["dias"])
    assert abs(sum(p["largura_mails"] for p in pd["periodos"]) - 100) < 0.01 and sum(p["mails"] for p in pd["periodos"]) == total
    assert pd["lider_mails"]["mails"] == max(p["mails"] for p in pd["periodos"])
    assert abs(sum(p["largura"] for p in pd["periodos"]) - 100) < 0.01
    assert sum(p["leads"] for p in pd["periodos"]) == tot["lead"]


def test_lia_recebimento_soma_o_total_e_bate_com_o_fora():
    """Caio, 30/10/2026: 'Quando o inbound chega' sobre os e-mails do período: turnos do expediente (10h–13h, 14h–19h, fora)
    somam o total e o 'fora' dos turnos segue a regra do SLA (faixas do retrato) e o das faixas do dia é o pct_fora da tela; dia da semana com total (soma = total) e média inteira por dia."""
    r = json.loads(lia.RETRATO.read_text(encoding="utf-8"))
    total = sum(d["nao_lead"] + d["lead"] + d["validacao"] for d in r["dias"])
    rc = lia.recebimento(r)
    assert [t["chave"] for t in rc["turnos"]] == ["manha", "tarde", "fora"] and sum(t["n"] for t in rc["turnos"]) == total
    fora = next(t for t in rc["turnos"] if t["chave"] == "fora")
    assert fora["n"] == sum(r["faixas"][k] for k in lia.FORA)  # turnos antigos (regra do SLA), fora da tela
    dd = lia.faixas_do_dia(r)  # o dia em faixas (definição do Caio para a LIA: almoço 12h–13h)
    assert [f["chave"] for f in dd["faixas"]] == ["antes", "manha", "almoco", "tarde", "noite", "fds"] and dd["total"] == total
    u = r["horas"]["util"]
    assert [f["n"] for f in dd["faixas"]][:4] == [sum(u[7:10]), sum(u[10:12]), u[12], sum(u[13:19])]
    assert dd["fora"]["n"] == total - sum(u[10:19]) and dd["fora"]["pct"] == lia.tela()["pct_fora"]  # 10h–19h, almoço dentro
    # leads por faixa (Caio, 30/10/2026): mesmas faixas; somam os leads; taxa = leads ÷ e-mails da faixa
    ul = r["horas_lead"]["util"]
    assert dd["leads"]["total"] == sum(map(sum, r["horas_lead"].values())) == sum(d["lead"] for d in r["dias"])
    tarde = next(f for f in dd["faixas"] if f["chave"] == "tarde")
    assert tarde["leads"] == sum(ul[13:19]) and tarde["taxa"] == f"{sum(ul[13:19]) / sum(u[13:19]) * 100:.1f}%".replace(".", ",")
    assert [f["chave"] for f in dd["barra"]] == ["manha", "almoco", "tarde", "antes", "noite", "fds"]  # dentro | fora
    for l in dd["quadrantes"]["linhas"]:  # cada barra: só faixas do expediente à esquerda do divisor, só as de fora à direita
        assert [g["chave"] for g in l["dentro"]] == ["manha", "almoco", "tarde"] and [g["chave"] for g in l["fora"]] == ["antes", "noite", "fds"]
    # três barras (Caio, 30/10/2026): leads, não leads e validação, cada uma sobre o total da sua categoria
    assert dd["nao_leads"]["total"] == sum(d["nao_lead"] for d in r["dias"]) and dd["validacao"]["total"] == sum(d["validacao"] for d in r["dias"])
    assert all(f["leads"] + f["nl"] + f["v"] == f["n"] for f in dd["faixas"])
    assert sum(t["n"] for t in rc["turnos"] if t["chave"] != "fora") == r["faixas"]["expediente"]
    assert sum(d["total"] for d in rc["dias"]) == total and [d["curto"] for d in rc["dias"]][-1] == "Sáb–dom"
    assert all(d["media_int"] == math.floor(d["total"] / d["n"] + 0.5) for d in rc["dias"])
    assert rc["maior_dia"]["media"] == max(d["media"] for d in rc["dias"]) and max(d["largura"] for d in rc["dias"]) == 100
    assert abs(sum(t["largura"] for t in rc["turnos"]) - 100) < 0.01


def _lia_n_pct(txt: str) -> float:
    return float(txt.rstrip("%").replace(",", "."))


def test_lia_percentuais_das_partes_fecham_em_100():
    """03/11/2026: arredondadas uma a uma, as partes somavam 101% (leads 74% dentro + 27% fora). Maior resto: dentro + fora
    = 100%, as faixas de cada lado somam o lado, e a fração e cada semana (três categorias, 1 casa) somam 100,0%."""
    assert lia._maior_resto([147, 53], 200, 100) == [74, 26]  # 73,5 + 26,5: empate de resto, a ordem decide
    assert lia._maior_resto([1, 1, 1], 3, 100) == [34, 33, 33] and lia._maior_resto([0, 0], 0, 100) == [0, 0]
    assert lia._pct_partes([1880, 200, 84], 1) == ["86,9%", "9,2%", "3,9%"] and lia._pct_partes([0, 0]) == ["—", "—"]
    por, d, f = lia._pct_lados({"a": 1, "b": 1, "c": 1, "x": 1, "y": 2}, ("a", "b", "c"), ("x", "y"))
    assert (d, f) == (50, 50) and sum(por[k] for k in "abc") == 50 and por["x"] + por["y"] == 50
    with pytest.raises(ValueError):
        lia._maior_resto([1, 1], 2, 150)  # alvo que as cotas não alcançam
    e = lia.tela()
    assert sum(_lia_n_pct(x["pct"]) for x in e["fracao"]) == pytest.approx(100)
    for s in e["semanas"]:
        assert sum(_lia_n_pct(p["pct"]) for p in s["partes"]) == pytest.approx(100)
    dd = e["recebimento"]["dia"]
    assert _lia_n_pct(dd["dentro"]["pct"]) + _lia_n_pct(dd["fora"]["pct"]) == 100 and dd["fora"]["pct"] == e["pct_fora"]
    assert sum(_lia_n_pct(x["pct"]) for x in dd["faixas"]) == 100
    for campo in ("pct_leads", "pct_nl", "pct_v"):
        assert sum(_lia_n_pct(x[campo]) for x in dd["faixas"]) == 100, campo
    for linha in dd["quadrantes"]["linhas"]:
        dentro, fora = _lia_n_pct(linha["dentro_pct"]), _lia_n_pct(linha["fora_pct"])
        assert dentro + fora == 100, linha["rot"]
        assert sum(_lia_n_pct(g["pct"]) for g in linha["dentro"]) == dentro and sum(_lia_n_pct(g["pct"]) for g in linha["fora"]) == fora
    # o que a tela escreve na faixa de cada categoria é o mesmo número do quadrante
    leads = next(x for x in dd["quadrantes"]["linhas"] if x["cat"] == "l")
    assert {g["chave"]: g["pct"] for g in leads["dentro"] + leads["fora"]} == {x["chave"]: x["pct_leads"] for x in dd["faixas"]}
    assert leads["dentro_pct"] == dd["leads"]["dentro_pct"] and leads["fora_pct"] == dd["leads"]["fora_pct"]
    rc = e["recebimento"]
    assert sum(_lia_n_pct(t["pct"]) for t in rc["turnos"]) == 100
    assert sum(_lia_n_pct(p["pct_mails"]) for p in e["padroes"]["periodos"]) == 100


def test_lia_tempo_poupado_e_estimativa_com_premissa(monkeypatch):
    r = json.loads(lia.RETRATO.read_text(encoding="utf-8"))
    nao_lead = sum(p["nao_lead"] for p in r["periodos"])
    assert lia.MINUTOS_TRIAGEM == 2  # padrão pedido pelo Caio; premissa a confirmar com a equipe
    assert lia.tela()["horas"] == f"{nao_lead * 2 / 60:,.0f}".replace(",", ".")
    monkeypatch.setattr(lia, "MINUTOS_TRIAGEM", 3)  # o parâmetro é editável e a tela segue
    t = lia.tela()
    assert (t["minutos"], t["horas"]) == (3, f"{nao_lead * 3 / 60:,.0f}".replace(",", "."))


def test_lia_pagina_uma_visao_com_texto_para_leitor(cliente):
    html = cliente.get("/viu-agenciamento/lia").text
    assert "Quanto a LIA já leu e quanto deixou de chegar à equipe?" in html
    assert "≈ 11 h por semana" in html and "87% do total" in html and "Quando o inbound chega" in html
    # Caio, 30/10/2026: textos de apoio fora da tela (ficam na ficha); cores e legendas com as classes do portal
    for fora in ("premissa a confirmar com a equipe", "1 em cada", "deles no fim de semana", "Do e-mail à carta orçamento"):
        assert fora not in html, fora
    assert html.count('class="chave t-mercado"') >= 2 and html.count('class="chave t-sem-tipo"') >= 2 and html.count('class="chave chave-anterior"') >= 2  # validação hachurada
    assert "lia-per-barra-val" in html and "Não leads" in html and "dos leads" not in html.split('class="lia-per"')[1].split("</figcaption>")[0].split("so-leitor")[0]
    # Caio, 30/10/2026 (página mais limpa): frase do período, legendas da fração, nota de 12/10, leituras e nota fora da tela
    e = lia.tela()
    for fora in ("Dia da semana:", "Período do dia:", "revistos à mão", "Dados extraídos em", "Semana ISO",
                 "a LIA garantiu que não era lead", "virou lead no monday", "seguiu para análise da equipe",
                 "lia-heroi-pre", "lia-leituras", "lia-nota", "lia-apoio", "lia-fr-sub"):
        assert fora not in html, fora
    # o período foi para o título do gráfico; o leitor de tela mantém a frase antes do total
    assert f"E-mails por semana, {e['inicio']} a {e['fim']}" in html  # cartão no padrão da Demanda (Caio, 30/10/2026)
    assert 'class="lia-cartao lia-semanas colunas cartao-grafico"' in html and 'class="colunas-titulo" id="lia-sem-tit"' in html
    assert f'<span class="so-leitor">De {e["inicio"]} a {e["fim"]}, a LIA leu</span>' in html
    # Caio, 30/10/2026: "a LIA resolveu sozinha" (sem citar lead); o botão do vídeo fica embaixo do gráfico, no cartão,
    # fora do bloco da esquerda (que o extrato troca)
    assert "a LIA resolveu sozinha." not in html and "ela resolveu sozinha" not in html and "garantiu que não era lead" not in html
    cartao = html.split('data-lia-grafico')[1].split("</figure>")[0]
    esquerda = html.split('id="lia-esq"')[1].split('class="lia-direita"')[0]
    # o botão do vídeo fica acima do cartão do gráfico, à direita (fora do cartão e fora do bloco que o extrato troca)
    direita = html.split('class="lia-direita"')[1].split('data-lia-grafico')[0]
    assert "data-lia-video" in direita and "data-lia-video" not in cartao and "data-lia-video" not in esquerda
    assert 'class="lia-vc"' in direita and 'class="lia-vc-tela"' in direita and "A LIA na prática" in direita  # prévia em miniatura
    # Caio, 30/10/2026: o cartão fica só com o gráfico semanal; os números de apoio e o mapa vão para o painel do período
    # (que o extrato troca inteiro e o "Voltar ao período" restaura)
    periodo = esquerda.split('data-lia-painel="periodo"')[1]
    assert 'class="lia-kpis"' in periodo and 'class="lia-q"' in periodo and "Dentro do expediente" in periodo and "Fora do expediente" in periodo and "lia-dias-lista" not in html  # dia da semana fora da tela
    assert "lia-kpis" not in cartao and "lia-per-barra" not in cartao
    # 4ª rodada (Caio, 30/10/2026): sem mapa de calor e sem médias decimais na tela; ganho com números inteiros
    assert "lia-hm" not in html and "O ganho para a equipe" in html and "Quando o inbound chega" in html
    assert "lia-bloco-ganho" in periodo and "lia-bloco-inbound" in periodo
    quando = periodo.split('id="lia-quando-tit"')[1]
    assert not re.search(r">\s*\d+,\d", quando)  # nenhum número com vírgula decimal no bloco
    # a ressalva do dia da semana (p ≈ 0,33) fica só na ficha; a tela destaca o maior dia sem frase de padrão
    assert "sem padrão firme" not in html and "costuma" not in quando and "Fora do expediente" in quando
    assert "lia-carrossel" not in html and "?visao=" not in html  # uma visão só, sem carrossel
    r = json.loads(lia.RETRATO.read_text(encoding="utf-8"))
    n = len(r["semanas"])
    assert html.count('id="lia-s-') == n and html.count('class="lia-sem-dica dica-') == n and html.count("Semana ") >= 2 * n
    assert 'role="region"' in html and "aria-current" not in html.split("<main")[1].split("lia-sem-col")[1]
    assert 'style="' not in html and "<style nonce=" in html


def test_lia_sem_extrato_da_semana(cliente):
    """Caio, 30/10/2026: o extrato da semana saiu; clicar numa semana não troca nada e ?semana= é ignorado sem erro.
    Fica a dica de cada semana (mouse ou foco) e o texto para leitor de tela."""
    r = json.loads(lia.RETRATO.read_text(encoding="utf-8"))
    iso = date.fromisoformat(r["semanas"][0]["inicio"]).isocalendar().week
    base = cliente.get("/viu-agenciamento/lia")
    for q in (str(iso), "99", "abc"):
        res = cliente.get(f"/viu-agenciamento/lia?semana={q}")
        assert res.status_code == 200 and "lia-extrato" not in res.text and "Voltar ao período" not in res.text
    html = base.text
    assert "extratos" not in lia.tela() and "semana" not in lia.tela()
    assert "data-lia-semana" not in html and "?semana=" not in html and "/static/lia.js" not in html and 'style="' not in html
    assert html.count('tabindex="0"') >= len(r["semanas"]) and "Clique para ver o extrato" not in html


def test_lia_capa_da_previa_do_video(cliente, monkeypatch):
    """Caio, 30/10/2026: CAPA vazio = degradê; preenchido (arquivo em app/static/video/) = <img> na miniatura, sem style=""."""
    html = cliente.get("/viu-agenciamento/lia").text
    assert 'class="lia-vc-fundo"' in html and "lia-vc-poster" not in html
    monkeypatch.setattr(lia_na_pratica, "CAPA", "lia-na-pratica.jpg")
    html = cliente.get("/viu-agenciamento/lia").text
    assert '<img class="lia-vc-poster" src="/static/video/lia-na-pratica.jpg" alt="">' in html and "lia-vc-fundo" not in html
    assert 'style="' not in html


def test_lia_botao_e_popup_do_video(cliente, monkeypatch):
    """Caio, 30/10/2026: o vídeo é um pop-up da LIA; sem JS o botão leva à página antiga (oculta, endereço mantido)."""
    monkeypatch.setattr(lia_na_pratica, "ARQUIVO", "")
    html = cliente.get("/viu-agenciamento/lia").text
    assert 'href="/viu-agenciamento/lia-na-pratica#1" data-lia-video' in html and '<span class="lia-vc-tit">A LIA na prática</span>' in html
    assert '<dialog id="lia-video"' in html and "Vídeo a incluir" in html and "<video" not in html  # sem arquivo
    assert html.count('class="fn-n"') == len(lia_na_pratica.ETAPAS) and "lia_video.js" in html
    assert 'href="/viu-agenciamento/iniciativas#1" rel="next"' in html  # LIA → Iniciativas
    nav = cliente.get("/viu-agenciamento/sla").text
    assert "/viu-agenciamento/lia-na-pratica" not in nav and cliente.get("/viu-agenciamento/lia-na-pratica").status_code == 200
    monkeypatch.setattr(lia_na_pratica, "ARQUIVO", "lia-na-pratica.mp4")
    html = cliente.get("/viu-agenciamento/lia").text
    assert 'src="/static/video/lia-na-pratica.mp4?v=' in html and 'preload="metadata"' in html and "autoplay" not in html


def test_video_reservado_sem_arquivo(cliente, monkeypatch):
    assert len(lia_na_pratica.ETAPAS) == 6
    monkeypatch.setattr(lia_na_pratica, "ARQUIVO", "")
    html = cliente.get("/viu-agenciamento/lia-na-pratica").text
    assert "Vídeo a incluir" in html and "<video" not in html and 'style="' not in html
    monkeypatch.setattr(lia_na_pratica, "ARQUIVO", "lia.mp4")
    monkeypatch.setattr(lia_na_pratica, "LEGENDAS", "lia.vtt")
    html = cliente.get("/viu-agenciamento/lia-na-pratica").text
    assert 'preload="metadata"' in html and 'srclang="pt-BR"' in html and "autoplay" not in html


def test_video_publicado_e_situacao_das_etapas(cliente):
    """Caio, 03/11/2026: o vídeo entrou (app/static/video/lia-na-pratica.mp4); etapas de iniciativa em produção ficam
    concluídas (✓) e as da fase de testes em andamento (ampulheta + selo "Em teste", texto e não só cor)."""
    from pathlib import Path

    assert (Path(__file__).resolve().parents[1] / "app" / "static" / "video" / lia_na_pratica.ARQUIVO).is_file()
    situacao = [(e["sigla"], e["concluida"], e["selo"]) for e in lia_na_pratica.tela()["etapas"]]
    assert situacao == [("LIA", True, ""), ("LIA", True, ""), ("LIA", True, ""), ("GPS", True, ""),
                        ("Orça+AI", False, "Em teste"), ("COP.IA", False, "Em teste")]
    html = cliente.get("/viu-agenciamento/lia").text
    assert 'src="/static/video/lia-na-pratica.mp4?v=' in html and "Vídeo a incluir" not in html
    assert html.count('<li class="fn-feita">') == 4 and html.count('<li class="fn-andamento">') == 2
    assert html.count('<span class="fn-selo">Em teste</span>') == 2


def _bloco_rm():
    from pathlib import Path

    css = (Path(__file__).resolve().parents[1] / "app" / "static" / "estilo.css").read_text(encoding="utf-8")
    return css, css[css.index("/* Roadmap da área (V2"):css.index("/* ---------- LIA (D-LIA-3")]


def _ol(html):
    return html[html.index('<ol class="rm-marcos"'):html.index("</ol>", html.index('<ol class="rm-marcos"'))]


ORDEM_RM = ["espalhados", "mapa", "dashboards", "ti", "liberada", "centralizar", "estudos", "evolucao"]


def test_roadmap(cliente):
    """Roadmap (31/10/2026, 5ª versão, "a linha do tempo linear em Y"): 01 Dados espalhados → 02 Mapeamos → abre em Y
    (embaixo, 03 Criação de dashboards, no meio do ramo; em cima, 04 Pedido à TI logo depois da curva ┄ Aguardando ┄
    05 Infraestrutura liberada logo antes da volta) → 06 BigQuery → dois trilhos contínuos até a borda, sem nó final
    (07 Análises e estudos, "Você está aqui", e 08 Novos dashboards e melhorias), com retroalimentação pontilhada."""
    t = roadmap.tela()
    assert [e["chave"] for e in t["marcos"]] == ORDEM_RM and t["n"] == 5
    assert [e["numero"] for e in t["marcos"]] == [f"{i:02d}" for i in range(1, 9)]
    trilhos = {e["chave"]: e["trilho"] for e in t["marcos"]}
    assert trilhos == {"espalhados": "meio", "mapa": "meio", "dashboards": "baixo", "ti": "cima", "liberada": "cima",
                       "centralizar": "meio", "estudos": "baixo", "evolucao": "cima"}
    x = {e["chave"]: e["x"] for e in t["marcos"]}
    # 1º Y: o pedido logo depois da curva de abertura, a liberação logo antes da curva de volta (espera longa), a
    # criação de dashboards no meio do ramo de baixo
    assert abs(x["ti"] - (x["mapa"] + roadmap.RAIO + roadmap.FOLGA + roadmap.CURVA + roadmap.RAIO)) < 1e-2
    assert abs(x["liberada"] - (x["centralizar"] - 2 * roadmap.RAIO - roadmap.FOLGA - roadmap.CURVA)) < 1e-2
    assert abs(x["dashboards"] - (x["ti"] + x["liberada"]) / 2) < 1e-2 and x["liberada"] - x["ti"] > 18
    # regra do texto: ramo de cima acima, ramo de baixo abaixo, tronco alternando a partir de cima
    assert {e["chave"]: e["lado"] for e in t["marcos"]} == {
        "espalhados": "acima", "mapa": "abaixo", "dashboards": "abaixo", "ti": "acima", "liberada": "acima",
        "centralizar": "abaixo", "estudos": "abaixo", "evolucao": "acima"}  # o 06 desce: acima dele está o título do 05
    # títulos centrados no eixo do nó, na largura padrão (encolhida por igual só quando encosta no vizinho)
    for e in t["marcos"]:
        assert e["alinhar"] == "centro" and abs(e["css_t"] + e["css_w"] / 2 - roadmap.RAIO) < 0.02
        assert e["css_w"] <= roadmap.TITULO + 1e-6
    for lado in ("acima", "abaixo"):
        blocos = sorted((e["x"] - e["css_w"] / 2, e["x"] + e["css_w"] / 2) for e in t["marcos"] if e["lado"] == lado)
        assert all(b[0] - a[1] >= 0.8 for a, b in itertools.pairwise(blocos)), lado  # nenhum título encosta no vizinho
    # respiro no eixo vertical: o 02 desce, o 03 sobe no ramo de baixo, o 06 sobe um pouco
    assert {e["chave"]: e["css_dy"] for e in t["marcos"] if e["css_dy"]} == {"mapa": 1.2, "dashboards": -0.7, "centralizar": -0.5}
    assert t["aqui"]["chave"] == "estudos" and not any(e["futuro"] for e in t["marcos"])
    # linhas: âmbar só na espera (trilho de cima, y = 93 − 29); depois dos nós de agora, tracejada até a borda, com uma
    # seta por trilho contínuo; sem nó de chegada
    u = lambda em: f"{round(em * 10, 1):g}"
    assert t["linhas"]["espera"] == f"M {u(x['ti'])} 64 H {u(x['liberada'])}"
    assert t["linhas"]["feito"].startswith("M 0 93 H") and t["linhas"]["futuro"].count("M ") == 2
    assert t["linhas"]["futuro"].count("H 723") == 2 and len(t["setas"]) == 2 and t["continuo"] == "Evolução contínua"
    # o pulso: uma rota por ramo; os quadros-chave (com a espera devagar) e o atraso da reação de cada nó vêm da rota
    assert len(t["pulsos"]) == 2 and all(p["d"].startswith("M 0 93") and p["d"].endswith("H 723") for p in t["pulsos"])
    assert 0.15 < t["pulsos"][0]["espera_ini"] < t["pulsos"][0]["espera_fim"] < 0.55 and 0.6 < t["pulsos"][1]["aqui"] < 0.85
    assert t["quadros"][0].startswith("@keyframes rm-anda-1 {") and t["quadros"][1].startswith("@keyframes rm-anda-2 {")
    atrasos = [e["css_pulso"] for e in t["marcos"]]
    assert all(a is not None and 1.1 <= a <= 1.1 + 9 * 0.9 for a in atrasos)
    assert atrasos[0] < atrasos[1] < atrasos[5]  # 01 → 02 → 06, na ordem em que o pulso passa
    html = cliente.get("/viu-agenciamento/roadmap").text
    ol = _ol(html)
    assert ol.count('<li id="rm-no-') == 8 and html.count('<svg class="rm-trilha" viewBox="0 0 730 280"') == 1
    for e in t["marcos"]:
        assert f'<li id="rm-no-{e["chave"]}" class="rm-marco rm-i{e["indice"]} rm-t-{e["trilho"]} rm-{e["lado"]} rm-e-{e["chave"]}' in ol
        # Roadmap novo aplicado em 03/11/2026: o <style> com nonce traz antes o atraso da entrada (--rmn-d)
        assert re.search(rf"#rm-no-{e['chave']} \{{ --rmn-d: \d+ms; --x: {e['css_x']}em;", html)  # posição pelo <style> com nonce
    assert re.search(r'<style nonce="[^"]+">[^<]*@keyframes rm-anda-1', html)
    posicoes = [ol.index(f'</span>{e["titulo"]}</h3>') for e in t["marcos"]]
    assert posicoes == sorted(posicoes)  # na ordem da numeração
    for parte in ('class="rm-linha rm-linha-feito"', 'class="rm-linha rm-linha-espera"', 'class="rm-linha rm-linha-futuro"',
                  'class="rm-pulso rm-pulso-1"', 'class="rm-pulso rm-pulso-2"', '<span class="rm-espera-txt">Aguardando</span>',
                  '<span class="rm-aqui-tag">Você está aqui</span>', '<p class="rm-continuo"><span>Evolução contínua</span></p>',
                  "<span>retroalimenta a base</span>", "<span>estudo vira dashboard</span>"):
        assert html.count(parte) == 1, parte
    assert html.count('class="rm-linha rm-seta"') == 2 and html.count('class="rm-retro-ponto"') == 2
    assert ol.count('aria-current="step"') == 1 and " rm-atual" in ol and " rm-futuro" not in ol
    assert "Próximos passos" not in ol and "chegada" not in html  # sem nó final nem bandeira de chegada
    # só número e título (as frases de apoio saíram a pedido do Caio, 31/10/2026)
    assert 'class="rm-frase"' not in html and all(not e.get("texto") for e in t["marcos"])
    # título, selo "Gerencial", gancho oculto e o ✕ do cabeçalho, que no Roadmap leva à capa
    assert '<h2 class="slide-titulo" id="s-roadmap">Como chegamos até aqui?</h2>' in html
    assert '<span class="nivel">Gerencial</span>' in html and '<span class="nivel">Roadmap</span>' not in html
    assert '<nav class="proxima proxima-gancho so-leitor"' in html and 'href="/viu-agenciamento' in html
    assert re.search(r'class="cab-passo cab-passo-fechar" href="/viu-agenciamento/capa"', html)
    # situação também em texto (leitor de tela)
    sits = re.findall(r'<span class="so-leitor">((?:Etapa|Em curso)[^<]*)\.</span>', ol)
    assert sits == ["Etapa concluída"] * 6 + ["Em curso, contínuo: você está aqui", "Em curso, contínuo"]
    assert 'style="' not in html and "/viu-agenciamento/linha-do-tempo" not in html
    assert cliente.get("/viu-agenciamento/linha-do-tempo").status_code == 404


def test_roadmap_enxuto(cliente):
    """Sem leque, selos nem frases; sete chips coloridos das fontes sob o nó 01 (enfeite, aria-hidden, em fileiras sem
    sobreposição); ícones dos nós com gesto próprio em loop lento e um anel que se abre quando o pulso passa; a linha
    se desenha na entrada; tudo num painel flutuante (lavanda, pontos, sombra em camadas); sombra difusa sob a linha."""
    html = cliente.get("/viu-agenciamento/roadmap").text
    for fora in ("rm-leque", "rm-janela", "rm-cometa", "rm-selo", "rm-mancha", "rm-aro", "rm-destinos", "rm-faixa-nav",
                 "Enquanto esperávamos", 'role="tooltip"', "rm-ver", "rm-frase"):
        assert fora not in html, fora
    for e in roadmap.tela()["marcos"]:
        assert len(e["titulo"]) <= 30
    chips = re.findall(r'<span class="rm-solto rm-solto-([a-z0-9]+)">([^<]+)</span>', html)
    assert chips == [("sharepoint", "SharePoint"), ("excel", "Excel"), ("monday", "Monday"), ("onenote", "OneNote"),
                     ("salesforce", "Salesforce"), ("api", "API"), ("req2pay", "Req2Pay")]
    assert len(re.findall(r'<p class="rm-soltos" aria-hidden="true">', html)) == 1
    icones = re.findall(r'<span class="rm-no" aria-hidden="true">\s*<svg class="icone rm-no-ic rm-ic-([a-z]+)"', html)
    assert icones == ["dispersos", "fluxo", "grafico", "ampulheta", "ok", "banco", "tendencia", "lapis"]
    assert _ol(html).count(" rm-reage") == 8
    _css, bloco = _bloco_rm()
    assert "rm-mancha" not in bloco and "body:has(.rm-palco)" not in bloco  # a lâmina fica branca
    painel = bloco[bloco.index(".rm.slide-corpo {"):bloco.index(".rm .rm-palco { font-size: 0.92em; }")]
    assert "border-radius: 22px;" in painel and "0 40px 80px -36px" in painel and "22px 22px" in painel  # painel flutuante
    # linha cheia mais presente: traço mais largo, degradê marinho → azul VIU, halo difuso leve, pontas arredondadas
    assert ".rm-linha-feito { stroke: url(#rm-grad); stroke-width: 2; filter: drop-shadow(" in bloco
    assert '<linearGradient id="rm-grad"' in html and 'stop-color="#2400ff"' in html
    for tom in ("sharepoint", "excel", "monday", "onenote", "salesforce", "api", "req2pay"):
        assert f".rm-solto-{tom} {{ --f: #" in bloco, tom
    assert ".rm-soltos { position: absolute;" in bloco and "flex-wrap: wrap; justify-content: center;" in bloco
    m = bloco.index("@media (prefers-reduced-motion: no-preference)")
    movimento = bloco[m:bloco.index("\n}\n", m)]
    for regra in ("html.js .rm-solto, html.js .rm-mini-pilha", "html.js .rm-botoes > li { animation: rm-deriva-botao 7s",
                  "html.js .rm-pulso-1 { animation: rm-anda-1 9s",
                  "html.js .rm-pulso-2 { animation: rm-anda-2 9s", "html.js .rm-linha-espera { animation: rm-marcha",
                  "html.js .rm-reage .rm-no::before { animation: rm-reage 9s ease-out infinite; animation-delay: var(--pulso); }",
                  "html.js .rm-retro-ponto { animation: rm-retro-anda", "html.js .slide.entrou:not(.revisto) .rm-trilha { animation: rm-desenha"):
        assert regra in movimento, regra
    for ic in icones:  # cada ícone tem o seu gesto, só com movimento
        assert f"html.js .rm-ic-{ic}" in movimento, ic
    assert "@keyframes rm-desenha { from { clip-path: inset(0 100% 0 0); }" in bloco
    assert ".palco:has(.rm-palco) > .proxima.so-leitor { top: 0; bottom: auto; }" in bloco


def test_roadmap_cliques(cliente):
    """Navegação em 1º lugar (Caio, 31/10/2026: "os botões não navegam"): os nós e as camadas decorativas não recebem
    o ponteiro; só links, miniaturas e o círculo do nó. Nenhum JS do Roadmap impede o clique nos destinos."""
    from pathlib import Path

    _css, bloco = _bloco_rm()
    assert "pointer-events: none; }\n.rm-marco a, .rm-no { pointer-events: auto; }" in bloco
    assert ".rm-trilha, .rm-retro-rotulo, .rm-continuo, .rm-soltos, .rm-haste, .rm-aqui, .rm-espera { pointer-events: none; }" in bloco
    # Roadmap novo aplicado em 03/11/2026: o JS carregado é o roadmap_novo.js
    js = (Path(__file__).resolve().parents[1] / "app" / "static" / "roadmap_novo.js").read_text(encoding="utf-8")
    assert 'querySelectorAll("[data-rm-galeria]")' in js and "rm-destino" not in js  # o JS só trata as miniaturas


def test_roadmap_botoes(cliente):
    """Botões das páginas presos ao nó "Análises e estudos", por categoria (três tons; a forma do ícone muda por
    categoria); Iniciativas e Previsão marcadas como "próximo"; colagem organizada por nth-child, sem style; mouse ou
    foco acende o nó."""
    html = cliente.get("/viu-agenciamento/roadmap").text
    ol = _ol(html)
    # Roadmap novo aplicado em 03/11/2026: depois da linha para o leitor de tela vem a seta (enfeite, aria-hidden)
    achados = re.findall(r'<a class="rm-botao rm-destino( rm-destino-proximo)?" href="([^"]+)"><span class="rm-destino-circ" aria-hidden="true">\s*<svg[^>]*>.*?</svg>\s*</span>'
                         r'<span class="rm-destino-nome">([^<]+)</span>(?:<span class="rm-proximo">próximo</span>)?<span class="so-leitor">: ([^<]+)</span>'
                         r'<span class="rmn-destino-seta" aria-hidden="true">\s*<svg[^>]*>.*?</svg>\s*</span></a>', ol, re.DOTALL)
    assert len(achados) == 6
    links = {rot: href for _, href, rot, _ in achados}
    assert links == {"Demanda": "/viu-agenciamento", "Talentos": "/viu-agenciamento/talentos#1",
                     "SLA": "/viu-agenciamento/sla#1", "LIA": "/viu-agenciamento/lia#1",
                     "Iniciativas": "/viu-agenciamento/iniciativas#1", "Previsão": "/viu-agenciamento/previsao#1"}
    assert [rot for p, _, rot, _ in achados if p] == ["Iniciativas", "Previsão"]
    for href in links.values():
        assert cliente.get(href.split("#")[0]).status_code == 200
    estudos = ol[ol.index(" rm-e-estudos"):ol.index(" rm-e-evolucao")]
    cats = re.findall(r'<section class="rm-cat rm-cat-([a-z]+) rm-forma-([a-z]+)" aria-labelledby="rm-cat-([a-z]+)">\s*<h4 class="rm-cat-tit" id="rm-cat-\3">([^<]+)</h4>', estudos)
    assert cats == [("azul", "circulo", "analises", "Análises"), ("roxo", "quadrado", "automacao", "Automação e IA"),
                    ("verde", "gota", "projecoes", "Projeções")]
    assert estudos.count('class="rm-botao rm-destino') == 6 and " rm-alvo" in ol[ol.index('id="rm-no-estudos"'):][:400]
    assert set(re.findall(r'class="(rm-botao(?: [^"]*)?)"', html)) == (
        {"rm-botao rm-destino", "rm-botao rm-destino rm-destino-proximo", "rm-botao rm-dlg-passo", "rm-botao rm-dlg-zoom",
         "rm-botao rm-dlg-fechar"})
    _css, bloco = _bloco_rm()
    assert ".rm-alvo:has(.rm-destino:hover, .rm-destino:focus-visible) .rm-no" in bloco
    assert ".rm-botao:focus-visible { outline: 2px solid var(--azul)" in bloco
    assert "height: 2.3em;" in bloco and "rotate: -1.5deg;" in bloco  # ≥ 32 px a 1280 × 720 (2,3 × 14,8 px); colagem
    assert "grid-template-rows: repeat(4, auto); grid-auto-flow: column;" in bloco  # cresce para o lado (até ~10)
    for tom in ("azul", "roxo", "verde"):
        assert f".rm-cat-{tom} {{ --f: #" in bloco
    celular = bloco[bloco.index("@media (max-width: 900px)"):]
    assert ".rm-destino, .rm-botoes > li:nth-child(n) .rm-destino { rotate: 0deg;" in celular  # lista simples em 390 px


def test_roadmap_botoes_escalam(cliente, monkeypatch):
    """Uma página nova entra com uma linha no catálogo: com 10 destinos (4 fictícios, só no teste) as categorias
    continuam agrupadas e todos os links aparecem."""
    passos = list(roadmap.PASSOS)
    k = next(i for i, p in enumerate(passos) if "ramos" in p and any(n["chave"] == "estudos" for r in p["ramos"] for n in r["nos"]))
    extra = tuple({"rotulo": f"Página {i}", "linha": "Fictícia", "icone": "grafico", "categoria": c, "href": "/viu-agenciamento"}
                  for i, c in ((1, "analises"), (2, "analises"), (3, "automacao"), (4, "projecoes")))
    ramos = tuple({**r, "nos": tuple({**n, "botoes": n["botoes"] + extra} if n["chave"] == "estudos" else n for n in r["nos"])}
                  for r in passos[k]["ramos"])
    passos[k] = {**passos[k], "ramos": ramos}
    monkeypatch.setattr(roadmap, "PASSOS", tuple(passos))
    html = cliente.get("/viu-agenciamento/roadmap").text
    assert html.count('class="rm-botao rm-destino') == 10 and html.count('<section class="rm-cat ') == 3
    assert all(f">Página {i}<" in html for i in range(1, 5))


def test_roadmap_registros(cliente):
    """Miniaturas junto do nó (fluxo em "Mapeamos", a pilha Pagamentos + Contratos em "Criação de dashboards", o
    BigQuery em "Centralizamos"), que abrem o <dialog> (clique, Enter ou Espaço; galeria com ← → na pilha)."""
    from pathlib import Path

    t = roadmap.tela()
    gal = {e["chave"]: [x["imagem"] for x in e["galeria"]] for e in t["marcos"] if e["galeria"]}
    assert gal == {"mapa": ["fluxo-processo"], "dashboards": ["dashboard-pagamento", "dashboard-contratos", "dashboard-raiox"],
                   "centralizar": ["bigquery"]}
    estaticos = Path(__file__).resolve().parents[1] / "app" / "static"
    for x in [x for e in t["marcos"] for x in e["galeria"]]:
        for chave in ("mini", "src", "alta"):
            arquivo = estaticos / x[chave].removeprefix("/static/").split("?")[0]
            assert arquivo.is_file() and arquivo.stat().st_size < 400_000  # 03/11/2026: sem desfoque, a alta do fluxo tem ~345 KB (só carrega ao ampliar)
        assert x["w"] > 0 and x["mw"] > 0 and len(x["alt"]) >= 20
    html = cliente.get("/viu-agenciamento/roadmap").text
    links = re.findall(r'<a class="rm-mini( rm-mini-pilha)?" href="([^"]+)" data-rm-galeria=\'([^\']+)\' aria-haspopup="dialog">(.*?)</a>', html, re.DOTALL)
    assert [bool(p) for p, *_ in links] == [False, True, False]
    galerias = [json.loads(g) for _, _, g, _ in links]
    assert [[x["imagem"] for x in g] for g in galerias] == [["fluxo-processo"], ["dashboard-pagamento", "dashboard-contratos", "dashboard-raiox"], ["bigquery"]]
    assert all(h.startswith(g[0]["src"]) for (_, h, _, _), g in zip(links, galerias))  # sem JS, abre a 1ª imagem
    imgs = re.findall(r'<img class="rm-mini-img"[^>]*>', html)
    assert len(imgs) == 5
    for img in imgs:  # alt descritivo, tamanho declarado e carga preguiçosa
        assert re.search(r'alt="[^"]{20,}"', img) and 'width="' in img and 'height="' in img and 'loading="lazy"' in img
        assert re.search(r'src="/static/roadmap/[a-z-]+-mini\.webp', img)
    assert "(3 imagens; abre ampliada)" in html and re.fullmatch(r"/static/roadmap/fluxo-processo-alta\.webp\?v=[0-9a-f]+", galerias[0][0]["alta"])
    assert '<div class="rm-dlg-quadro" role="region"' in html and "data-rm-fechar" in html and "data-rm-zoom" in html
    assert 'data-rm-anterior aria-label="Imagem anterior"' in html and 'data-rm-proxima aria-label="Próxima imagem"' in html
    assert "data-rm-navegacao hidden" in html and 'data-rm-contador aria-live="polite"' in html
    # Roadmap novo aplicado em 03/11/2026: diálogo com o acabamento novo, JS próprio e sem o link "tamanho real"
    assert '<dialog id="rm-dialogo" class="rm-dialogo rmn-dialogo"' in html and 'style="' not in html
    assert 'src="/static/roadmap_novo.js' in html and 'src="/static/roadmap.js' not in html and "rm-dlg-abrir" not in html
    js = (estaticos / "roadmap_novo.js").read_text(encoding="utf-8")
    assert "data-rm-galeria" in js and "JSON.parse" in js and '"ArrowRight"' in js and "mostrar(atual + 1)" in js
    assert 'ev.key !== " "' in js  # Espaço também abre
    for nome in ("Marcela", "Pelagio", "Gil", "Boa noite"):  # nenhum nome de pessoa do PDF nem a saudação do print
        assert nome not in html


def test_roadmap_mostrar_oculta_etapa(cliente, monkeypatch):
    """mostrar=False tira o nó; uma bifurcação que fica com um ramo só volta ao tronco."""
    def sem(chaves):
        saida = []
        for p in roadmap.PASSOS:
            if "ramos" in p:
                saida.append({**p, "ramos": tuple({**r, "nos": tuple({**n, "mostrar": n["chave"] not in chaves} for n in r["nos"])}
                                                  for r in p["ramos"])})
            else:
                saida.append({**p, "mostrar": p["chave"] not in chaves})
        return tuple(saida)

    monkeypatch.setattr(roadmap, "PASSOS", sem({"dashboards"}))
    t = roadmap.tela()
    assert [e["chave"] for e in t["marcos"]] == [c for c in ORDEM_RM if c != "dashboards"]
    assert [e["trilho"] for e in t["marcos"]][:5] == ["meio"] * 5 and t["linhas"]["espera"]
    html = cliente.get("/viu-agenciamento/roadmap").text
    assert "Criação de dashboards" not in html and _ol(html).count('<li id="rm-no-') == 7 and "rm-mini-pilha" not in html
    monkeypatch.setattr(roadmap, "PASSOS", sem({"evolucao"}))
    t = roadmap.tela()
    assert [e["chave"] for e in t["marcos"]][-1] == "estudos" and t["marcos"][-1]["trilho"] == "meio"
    html = cliente.get("/viu-agenciamento/roadmap").text
    assert "Novos dashboards e melhorias" not in html and "estudo vira dashboard" not in html
    assert html.count('class="rm-botao rm-destino') == 6 and html.count('class="rm-linha rm-seta"') == 1


def test_roadmap_escala_mais_etapas(cliente, monkeypatch):
    """O projeto vai crescer: um nó a mais no tronco vira um passo a mais, com as posições recalculadas."""
    extra = {"chave": "extra", "titulo": "Etapa extra", "icone": "grafico", "situacao": "feito"}
    monkeypatch.setattr(roadmap, "PASSOS", roadmap.PASSOS[:4] + (extra,) + roadmap.PASSOS[4:])
    t = roadmap.tela()
    assert t["n"] == 6 and [e["chave"] for e in t["marcos"]][6] == "extra"
    xs = [e["x"] for e in t["marcos"] if e["trilho"] == "meio"]
    assert xs == sorted(xs) and xs[-1] < 73
    html = cliente.get("/viu-agenciamento/roadmap").text
    assert _ol(html).count('<li id="rm-no-') == 9 and " rm-i8 " in html
    _css, bloco = _bloco_rm()
    assert ".rm-i9 { --i: 9; }" in bloco and "@media (max-width: 900px)" in bloco
