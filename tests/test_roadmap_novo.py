"""Roadmap novo, APLICADO (Caio, 03/11/2026) em /viu-agenciamento/roadmap: os mesmos dados de roadmap.tela() com outro
acabamento (roadmap/template.html + /static/roadmap_novo.css, escopado em .rmn, e /static/roadmap_novo.js). Painel claro e
leve, como o anterior, sem cores pesadas nem efeitos chamativos; destinos em colagem, 07 com anel amarelo fino e selo ao
lado do nó, galeria que abre a imagem inteira e entrada coreografada na abertura. O Roadmap anterior (validado) está
guardado em _descartados/2026-11-03/roadmap_validado/. Aqui se confere conteúdo, ordem, destinos, galerias, <dialog>,
CSP, o painel claro e o movimento reduzido."""

import json
import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.apresentacoes.gestao_orcamentos import roadmap

RAIZ = Path(__file__).resolve().parents[1]
CSS_NOVO = RAIZ / "app" / "static" / "roadmap_novo.css"
JS_NOVO = RAIZ / "app" / "static" / "roadmap_novo.js"
TEMPLATE = RAIZ / "app" / "apresentacoes" / "gestao_orcamentos" / "roadmap" / "template.html"  # aplicado em 03/11/2026
URL = "/viu-agenciamento/roadmap"  # aplicado no lugar do validado (Caio, 03/11/2026)
ORDEM = ["espalhados", "mapa", "dashboards", "ti", "liberada", "centralizar", "estudos", "evolucao"]
DESTINOS = {"Demanda": "/viu-agenciamento", "Talentos": "/viu-agenciamento/talentos#1", "SLA": "/viu-agenciamento/sla#1",
            "LIA": "/viu-agenciamento/lia#1", "Iniciativas": "/viu-agenciamento/iniciativas#1",
            "Previsão": "/viu-agenciamento/previsao#1"}


@pytest.fixture
def cliente():
    from app.main import app

    with TestClient(app) as c:
        yield c


@pytest.fixture
def html(cliente):
    r = cliente.get(URL)
    assert r.status_code == 200
    return r.text


def _ol(html: str) -> str:
    ini = html.index('<ol class="rm-marcos"')
    return html[ini:html.index("</ol>", ini)]


def _bloco_validado():
    css = (RAIZ / "app" / "static" / "estilo.css").read_text(encoding="utf-8")
    return css, css[css.index("/* Roadmap da área (V2"):css.index("/* ---------- LIA (D-LIA-3")]


def _css_sem_comentarios() -> str:
    return re.sub(r"/\*.*?\*/", "", CSS_NOVO.read_text(encoding="utf-8"), flags=re.DOTALL)


def _partes(seletor: str) -> list[str]:
    """Separa uma lista de seletores pelas vírgulas de nível 0 (fora de :has(...) e afins)."""
    partes, nivel, atual = [], 0, ""
    for ch in seletor:
        nivel += {"(": 1, ")": -1}.get(ch, 0)
        if ch == "," and nivel == 0:
            partes.append(atual)
            atual = ""
        else:
            atual += ch
    return [*partes, atual]


def test_rota_e_arquivos(cliente, html):
    assert '<div class="slide-corpo rm rmn rm-n5">' in html
    assert re.search(r'<link rel="stylesheet" href="/static/roadmap_novo\.css\?v=[^"]+">', html)
    assert 'src="/static/roadmap_novo.js' in html and 'src="/static/roadmap.js' not in html  # JS próprio da galeria
    assert cliente.get("/static/roadmap_novo.css").status_code == 200
    assert cliente.get("/static/roadmap_novo.js").status_code == 200
    assert '<h2 class="slide-titulo" id="s-roadmap">Como chegamos até aqui?</h2>' in html
    assert '<span class="nivel">Gerencial</span>' in html


def test_validado_guardado():
    """Caio, 03/11/2026: o Roadmap novo foi aplicado; o validado ficou guardado em _descartados/2026-11-03/."""
    guardado = (RAIZ / "_descartados" / "2026-11-03" / "roadmap_validado" / "app" / "apresentacoes" / "gestao_orcamentos"
                / "roadmap" / "template.html").read_text(encoding="utf-8")
    # no template Jinja a classe sai de "rm-n{{ t.n }}": confere-se o que está literal (o JS antigo e nada do acabamento novo)
    assert '<div class="slide-corpo rm rm-n{{ t.n }}">' in guardado and 'src="/static/roadmap.js' in guardado
    assert "rmn" not in guardado and "roadmap_novo" not in guardado
    assert not (RAIZ / "app" / "apresentacoes" / "gestao_orcamentos" / "roadmap_novo").exists()  # a seção oculta saiu


def test_oito_nos_na_ordem_com_texto_para_leitor(html):
    t = roadmap.tela()
    ol = _ol(html)
    assert ol.count('<li id="rm-no-') == 8
    ids = re.findall(r'<li id="rm-no-([a-z]+)"', ol)
    assert ids == ORDEM == [e["chave"] for e in t["marcos"]]
    for e in t["marcos"]:
        assert re.search(rf"#rm-no-{e['chave']} \{{ --rmn-d: \d+ms; --x: {e['css_x']}em;", html)  # posições pelo <style> com nonce
        assert f'<span class="rm-num" aria-hidden="true">{e["numero"]}</span><span class="so-leitor">{e["numero"]}. </span>{e["titulo"]}</h3>' in ol
    sits = re.findall(r'<span class="so-leitor">((?:Etapa|Em curso)[^<]*)\.</span>', ol)
    assert sits == ["Etapa concluída"] * 6 + ["Em curso, contínuo: você está aqui", "Em curso, contínuo"]
    assert ol.count('aria-current="step"') == 1 and ol.count(" rm-atual") == 1 and ol.count(" rmn-curso") == 1
    assert html.count('<span class="rm-aqui-tag">Você está aqui</span>') == 1
    assert html.count('<span class="rm-espera-txt">Aguardando</span>') == 1
    assert html.count('<p class="rm-continuo"><span>Evolução contínua</span></p>') == 1
    assert "<span>retroalimenta a base</span>" in html and "<span>estudo vira dashboard</span>" in html
    assert re.search(r'<style nonce="[^"]+">[^<]*@keyframes rm-anda-1', html)
    assert html.count('class="rm-pulso rm-pulso-') == 2


def test_seis_destinos_com_links_certos(cliente, html):
    ol = _ol(html)
    achados = re.findall(r'<a class="rm-botao rm-destino( rm-destino-proximo)?" href="([^"]+)"><span class="rm-destino-circ" aria-hidden="true">'
                         r'\s*<svg[^>]*>.*?</svg>\s*</span><span class="rm-destino-nome">([^<]+)</span>(?:<span class="rm-proximo">próximo</span>)?'
                         r'<span class="so-leitor">: ([^<]+)</span><span class="rmn-destino-seta" aria-hidden="true">', ol, re.DOTALL)
    assert {rot: href for _, href, rot, _ in achados} == DESTINOS
    assert [rot for p, _, rot, _ in achados if p] == ["Iniciativas", "Previsão"]
    assert all(len(linha) >= 10 for *_, linha in achados)  # a linha de apoio segue para o leitor de tela
    for href in DESTINOS.values():
        assert cliente.get(href.split("#")[0]).status_code == 200
    cats = re.findall(r'<section class="rm-cat rm-cat-([a-z]+) rm-forma-[a-z]+" aria-labelledby="rm-cat-([a-z]+)">\s*<h4 class="rm-cat-tit" id="rm-cat-\2">([^<]+)</h4>', ol)
    assert cats == [("azul", "analises", "Análises"), ("roxo", "automacao", "Automação e IA"), ("verde", "projecoes", "Projeções")]


def test_tres_galerias_e_dialogo(html):
    links = re.findall(r'<a class="rm-mini( rm-mini-pilha)?" href="([^"]+)" data-rm-galeria=\'([^\']+)\' aria-haspopup="dialog">(.*?)</a>', html, re.DOTALL)
    galerias = [json.loads(g) for _, _, g, _ in links]
    assert [[x["imagem"] for x in g] for g in galerias] == [
        ["fluxo-processo"], ["dashboard-pagamento", "dashboard-contratos", "dashboard-raiox"], ["bigquery"]]
    assert [bool(p) for p, *_ in links] == [False, True, False]
    assert all(h.startswith(g[0]["src"]) for (_, h, _, _), g in zip(links, galerias))  # sem JS, abre a 1ª imagem
    assert "(3 imagens; abre ampliada)" in html
    imgs = re.findall(r'<img class="rm-mini-img"[^>]*>', html)
    assert len(imgs) == 5
    for img in imgs:
        assert re.search(r'alt="[^"]{20,}"', img) and 'width="' in img and 'height="' in img and 'loading="lazy"' in img
    for _, _, _, miolo in links:  # a lupa é enfeite
        assert '<span class="rmn-mini-lupa" aria-hidden="true">' in miolo
    for parte in ('<dialog id="rm-dialogo" class="rm-dialogo rmn-dialogo"', '<div class="rm-dlg-quadro" role="region"',
                  "data-rm-fechar", "data-rm-zoom", 'data-rm-anterior aria-label="Imagem anterior"',
                  'data-rm-proxima aria-label="Próxima imagem"', "data-rm-navegacao hidden", 'data-rm-contador aria-live="polite"'):
        assert html.count(parte) == 1, parte
    assert "rm-dlg-abrir" not in html and "Abrir a imagem em tamanho real" not in html  # link retirado (Caio, 03/11)


def test_galeria_abre_inteira_e_100_com_a_alta():
    """A imagem abre inteira, contida na área (object-fit: contain, sem cortar); "Ver em 100%" mostra a versão "-alta"
    (quando existe) no tamanho real, com rolagem a partir do canto superior esquerdo, e volta com "Caber na tela"."""
    css = _css_sem_comentarios()
    assert re.search(r"\.rmn-dialogo \.rm-dlg-img \{ position: absolute; inset: 0; width: 100%; height: 100%;[^}]*object-fit: contain;", css)
    assert re.search(r"\.rmn-dialogo \.rm-dlg-quadro\.rm-dlg-real \{ overflow: auto;", css)
    assert re.search(r"\.rm-dlg-real \.rm-dlg-img \{ position: static; width: auto; height: auto;[^}]*object-fit: none;", css)
    assert ".rmn-dialogo { height: 88vh; }" in css  # a área tem altura definida: a imagem cabe sem cortar
    js = JS_NOVO.read_text(encoding="utf-8")
    assert "img.src = cheia ? x.alta || x.src : x.src;" in js and "x.aw || x.w" in js and "x.ah || x.h" in js
    assert "quadro.scrollLeft = 0; quadro.scrollTop = 0;" in js  # 100% começa no canto superior esquerdo
    assert 'zoom.addEventListener("click", function () { visao(!real); });' in js
    assert '"Caber na tela" : "Ver em 100%"' in js and "rm-dlg-abrir" not in js and "abrir.href" not in js
    assert "data-rm-galeria" in js and "JSON.parse" in js and '"ArrowRight"' in js and 'ev.key !== " "' in js
    assert "prefers-reduced-motion" in js  # abre e fecha sem animação com movimento reduzido
    galerias = [x for e in roadmap.tela()["marcos"] for x in e["galeria"]]
    fluxo = next(x for x in galerias if x["imagem"] == "fluxo-processo")
    assert fluxo["alta"].split("?v=")[0].endswith("-alta.webp") and "?v=" in fluxo["alta"] and (fluxo["aw"], fluxo["ah"]) == (9486, 1899)
    raiox = next(x for x in galerias if x["imagem"] == "dashboard-raiox")
    assert (raiox["aw"], raiox["ah"]) == (1672, 941)


def test_entrada_coreografada(html):
    """A linha se desenha em 900 ms; cada nó acende quando ela chega (--rmn-d proporcional à posição, no <style> com
    nonce); o 07 acende antes dos cartões, que entram em cascata. Tudo só sem movimento reduzido."""
    t = roadmap.tela()
    atrasos = {c: int(ms) for c, ms in re.findall(r"#rm-no-([a-z]+) \{ --rmn-d: (\d+)ms;", html)}
    assert set(atrasos) == set(ORDEM)
    por_x = [e["chave"] for e in sorted(t["marcos"], key=lambda e: e["x"])]
    assert [atrasos[c] for c in por_x] == sorted(atrasos.values())  # na ordem em que a linha chega
    assert all(0 <= a <= 900 for a in atrasos.values()) and atrasos["estudos"] < 820  # o 07 antes dos cartões
    css = _css_sem_comentarios()
    ini = css.index("@media (prefers-reduced-motion: no-preference)")
    movimento = css[ini:css.index("\n}\n", ini)]
    for regra in ("html.js .slide.entrou:not(.revisto) .rmn .rm-trilha { animation: rmn-desenha 900ms",
                  "html.js .slide.entrou:not(.revisto) .rmn .rm-marco { animation: none; }",
                  ("html.js .slide.entrou:not(.revisto) .rmn .rm-no { animation: rmn-acende 420ms var(--ease-entra) backwards; "
                   "animation-delay: var(--rmn-d); }"),
                  "html.js .slide:not(.entrou) .rmn .rm-botoes > li", "calc(820ms + (var(--rmn-g) * 2 + var(--rmn-k)) * 60ms)",
                  "html.js .slide.revisto .rmn .rm-botoes > li"):
        assert regra in movimento, regra
    # a abertura inteira termina em até ~1,8 s (último nó: atraso + 120 + 420 ms; último cartão: 820 + 7 × 60 + 480 ms)
    assert max(atrasos.values()) + 120 + 420 <= 1600 and 820 + (2 * 2 + 3) * 60 + 480 <= 1800


def test_csp_sem_estilo_inline_nem_recurso_externo(html):
    assert 'style="' not in html
    fonte = TEMPLATE.read_text(encoding="utf-8") + CSS_NOVO.read_text(encoding="utf-8")
    assert "http://" not in fonte and "https://" not in fonte and "@import" not in fonte and "url(http" not in fonte


def test_css_escopado_no_rmn():
    css = _css_sem_comentarios()
    css = re.sub(r"@keyframes\s+[\w-]+\s*\{(?:[^{}]*\{[^{}]*\})*[^{}]*\}", "", css)
    seletores = [s.strip() for s in re.findall(r"([^{}]+)\{", css) if not s.strip().startswith("@")]
    assert seletores
    for sel in seletores:
        for parte in _partes(sel):
            assert ".rmn" in parte, parte  # nada vaza para o validado (.rm-* do estilo.css)
    nomes = re.findall(r"@keyframes\s+([\w-]+)", _css_sem_comentarios())
    assert all(n.startswith("rmn-") for n in nomes)  # não redefine as animações do validado


def test_painel_claro_do_validado(html):
    """O painel, os trilhos e o pulso são os do validado: o CSS novo não troca o fundo do painel nem a cor das linhas,
    não põe brilho largo sob a trilha e não usa o marinho escuro da capa."""
    css = _css_sem_comentarios()
    assert ".rmn.rm.slide-corpo" not in css and "slide-corpo" not in css
    assert css.count("rm-trilha") == 1  # só a entrada (o desenho da linha), nunca a cor ou o traço
    for fora in ("rm-linha", "rm-pulso", "rmn-brilho", "rmn-foco", "#0b1220", "#121a35", "#1a2748", "drop-shadow"):
        assert fora not in css, fora
    assert '<linearGradient id="rm-grad"' in html and 'stop-color="#2400ff"' in html  # o degradê fino do validado
    assert "rmn-brilho" not in html and "rmn-foco" not in html
    # hierarquia: concluídos cheios em marinho; o agora branco com anel amarelo fino (sem disco chapado); o em curso vazado
    assert ".rmn .rm-no { background: #1e2a78;" in css
    atual = re.search(r"\.rmn \.rm-atual \.rm-no \{([^}]*)\}", css).group(1)
    assert "background: #ffffff;" in atual and "0 0 0 0.38em var(--amarelo)" in atual and "width: 2.5em;" in atual
    assert ".rmn .rmn-curso .rm-no, .rmn .rm-futuro .rm-no { background: #f8f8fe; border: 1.5px dashed" in css
    # selo pequeno ao lado do nó, abaixo da trilha e longe do título; miniaturas retas com lupa
    assert ".rmn .rm-abaixo .rm-aqui { top: calc(var(--ry) + 0.78em); bottom: auto; left: calc(var(--R) + 2.15em); }" in css
    assert "font-size: 0.68em;" in re.search(r"\.rmn \.rm-aqui-tag \{([^}]*)\}", css).group(1)
    assert ".rmn .rm-mini { rotate: 0deg;" in css


def test_destinos_em_colagem():
    """Os destinos voltam à colagem do validado: o CSS novo não desfaz a rotação alternada, o deslocamento dos pares nem
    a deriva (estilo.css); só troca o acabamento (cartão branco, seta)."""
    css = _css_sem_comentarios()
    assert "rotate: 0deg" not in re.sub(r"\.rmn \.rm-mini[^{]*\{[^}]*\}", "", css)  # só as miniaturas ficam retas
    desktop = css.split("@media (max-width: 900px)")[0]
    assert "translate: none" not in css and "rm-deriva" not in css and "grid-template-columns" not in desktop
    assert ".rmn .rm-destino { gap: 0.5em; padding: 0 0.4em 0 0.3em; background: #ffffff;" in css
    _, bloco = _bloco_validado()
    assert "rotate: -1.5deg;" in bloco and ".rm-botoes > li:nth-child(2n) { translate: 0.35em 0; }" in bloco
    assert "html.js .rm-botoes > li { animation: rm-deriva-botao 7s" in bloco


def test_movimento_reduzido_e_sem_mola():
    css = _css_sem_comentarios()
    ini = css.index("@media (prefers-reduced-motion: no-preference)")
    fim = css.index("\n}\n", ini) if "\n}\n" in css[ini:] else css.index("\r\n}\r\n", ini)
    movimento = css[ini:fim]
    assert "infinite" not in css  # nada novo em loop (o pulso e os gestos do validado seguem as regras do estilo.css)
    assert "transition:" in movimento  # só respostas ao mouse e ao foco
    assert "alternate" not in css
    for _, y1, _, y2 in re.findall(r"cubic-bezier\(\s*([\d.]+),\s*(-?[\d.]+),\s*([\d.]+),\s*(-?[\d.]+)\)", css):
        assert 0 <= float(y1) <= 1 and 0 <= float(y2) <= 1
    # entrada (.entrou): duração + atraso fixo até 1,3 s (os atrasos por nó estão em test_entrada_coreografada)
    for d, a in re.findall(r"\.entrou[^{]*\{[^}]*animation:\s*[\w-]+\s+(\d+)ms\s+[^;]*?(\d+)ms", movimento):
        assert int(d) + int(a) <= 1300
    # fora do bloco de movimento só há transform/opacity estáticos: nenhuma animação nem transição
    fora = css[:ini] + css[fim:]
    assert "animation:" not in fora.replace("animation: none", "") and "transition:" not in fora


def test_imagens_da_galeria_levam_a_versao_do_arquivo(html):
    """Caio, 03/11/2026: a galeria abre as imagens grandes pelo JSON; sem ?v= o navegador mostrava a cópia antiga
    (desfocada) por até um dia depois da troca. Cada src/alta leva a versão do próprio arquivo."""
    for g in re.findall(r"data-rm-galeria='([^']+)'", html):
        for x in json.loads(g):
            assert re.fullmatch(r"/static/roadmap/[a-z-]+\.webp\?v=[0-9a-f]+", x["src"]), x["src"]
            assert re.fullmatch(r"/static/roadmap/[a-z-]+\.webp\?v=[0-9a-f]+", x["alta"]), x["alta"]
