"""Proposta de capa nova (Caio, 03/11/2026), em /viu-agenciamento/capa, só para comparar com a validada (/capa,
intacta). Confere a rota, o título real, o "Começar" para o Roadmap, a CSP, a decoração escondida do leitor de tela, a
camada duplicada do título (sem id e sem h2), o movimento (loop só por SMIL; CSS com movimento reduzido e sem loop) e
que a capa validada não mudou de arquivo nem de JS."""

import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

RAIZ = Path(__file__).resolve().parents[1]
CSS = (RAIZ / "app" / "static" / "capa_nova.css").read_text(encoding="utf-8")
JS = (RAIZ / "app" / "static" / "capa_nova.js").read_text(encoding="utf-8")


@pytest.fixture
def cliente():
    from app.main import app

    with TestClient(app) as c:
        yield c


@pytest.fixture
def html(cliente):
    r = cliente.get("/viu-agenciamento/capa")
    assert r.status_code == 200
    return r.text


def test_rota_titulo_e_textos(html):
    assert 'aria-labelledby="s-capa"' in html
    assert html.count('id="s-capa"') == 1
    assert re.search(r'<h2 class="cn-titulo" id="s-capa"><span class="cn-titulo-1">ViU</span> '
                     r'<span class="cn-titulo-2">Agenciamento</span></h2>', html)
    assert html.count("<h2") == 1  # a camada da noite repete o título como desenho, sem h2
    # 3ª rodada (Caio, 03/11/2026): sem subtítulo e sem palavras no desenho; sobretítulo e data viram o colofão do pé
    assert "cn-sub" not in html and "Tudo o que a área analisa" not in html
    for palavra in (">analisa<", ">constrói<", ">entrega<", "cn-paradas"):
        assert palavra not in html, palavra
    assert ('<p class="cn-colofao"><span class="cn-sobre">Relatório da área</span> '
            '<span class="cn-data">Outubro de 2026</span></p>') in html
    assert '<link rel="stylesheet" href="/static/capa_nova.css?v=' in html
    assert '<script src="/static/capa_nova.js?v=' in html
    assert "capa_fluxo.js" not in html


def test_comecar_e_tela_cheia(html):
    assert html.count('class="cn-comecar"') == 1
    assert '<a class="cn-comecar" href="/viu-agenciamento/roadmap#1">Começar' in html
    assert 'href="/viu-agenciamento/roadmap#1" rel="next"' in html  # a seta → também vai ao Roadmap
    assert re.search(r'<button type="button" class="tela-cheia-botao cn-tela-cheia" data-tela-cheia hidden '
                     r'aria-label="Tela cheia"', html)


def test_csp_e_decoracao_escondida(html):
    assert 'style="' not in html
    assert "<style" not in html  # sem bloco de estilo (nem com nonce): tudo em capa_nova.css
    assert not re.search(r'(src|href)="https?://', html)  # nada externo
    for classe in ("cn-plano", "cn-filete", "cn-desenho"):
        assert f'<div class="{classe}" aria-hidden="true">' in html, classe
    assert '<div class="cn-camada cn-noite" aria-hidden="true">' in html
    # o SVG decorativo e a seta do botão ficam fora do leitor de tela
    assert '<svg aria-hidden="true" viewBox="0 0 16 16">' in html


def test_fluxo_continuo_so_por_smil(html):
    assert html.count("<animateMotion") >= 8 and 'repeatCount="indefinite"' in html
    # nenhum begin positivo (atrasaria o início do fluxo): todos ≤ 0
    for b in re.findall(r'begin="(-?[\d.]+)s"', html):
        assert float(b) <= 0, b
    assert "pauseAnimations" in JS and "visibilitychange" in JS and "prefers-reduced-motion" in JS


def test_css_movimento_reduzido_e_sem_loop():
    assert "@media (prefers-reduced-motion: no-preference)" in CSS
    assert "infinite" not in CSS and "alternate" not in CSS
    # partículas e pulso escondidos por padrão; só aparecem dentro do bloco de movimento permitido
    assert ".cn-particulas { display: none; }" in CSS and ".cn-no-pulso {" in CSS
    m = CSS.index("@media (prefers-reduced-motion: no-preference)")
    bloco = CSS[m:CSS.index("\n}\n", m)]
    assert "html.js .cn-particulas { display: inline; }" in bloco and "html.js .cn-no-pulso { display: inline; }" in bloco
    assert "animation" not in CSS[:m]  # nenhuma animação fora do bloco de movimento permitido
    for a, y1, b, y2 in re.findall(r"cubic-bezier\(\s*([\d.]+),\s*(-?[\d.]+),\s*([\d.]+),\s*(-?[\d.]+)\)", CSS):
        assert 0 <= float(y1) <= 1 and 0 <= float(y2) <= 1
    # entrada única até 1,2 s (atraso + duração), como nas outras páginas
    entradas = re.findall(r"animation: cn-[a-z]+ (\d+)ms var\(--ease-entra\)(?: (\d+)ms)?", bloco)
    assert len(entradas) >= 10
    for dur, atraso in entradas:
        assert int(dur) + int(atraso or 0) <= 1200, (dur, atraso)
    # foco visível: anel duplo (marinho + branco) no "Começar"
    foco = re.search(r"\.cn-comecar:focus-visible \{([^}]*)\}", CSS).group(1)
    assert "0 0 0 3px #121a35" in foco and "0 0 0 5px #fff" in foco


def test_capa_nova_aplicada_e_validada_guardada(cliente):
    """Caio, 03/11/2026: a capa nova virou a capa; o endereço da proposta leva a ela e a validada ficou guardada."""
    r = cliente.get("/viu-agenciamento/capa-nova", follow_redirects=False)
    assert r.status_code == 301 and r.headers["location"] == "/viu-agenciamento/capa"
    capa = cliente.get("/viu-agenciamento/capa").text
    assert "rodape-dados" not in capa and "Dados até" not in capa  # sem o rodapé datado na capa
    guardada = Path(__file__).resolve().parents[1] / "_descartados" / "2026-11-03" / "capa_validada" / "app" / "templates" / "capa.html"
    assert '<a class="capa-comecar"' in guardada.read_text(encoding="utf-8")


def test_gancho_so_leitor_nao_cria_rolagem_na_capa(html):
    """Validação de 03/11/2026: o gancho escondido (.so-leitor, margin -1px) preso ao pé do palco descia 1px abaixo da
    janela e a capa ganhava uma barra de rolagem (visível no quadro da tela cheia, no Windows). Fica no topo — desde a
    revisão de 03/11/2026, pela regra geral de estilo.css (capa, Roadmap, estudo e encerramento), não mais só na capa."""
    assert re.search(r'<nav class="proxima proxima-gancho so-leitor"', html)  # a capa usa o gancho só para o leitor
    geral = (RAIZ / "app" / "static" / "estilo.css").read_text(encoding="utf-8")
    regra = re.search(r"^\.palco > \.proxima\.so-leitor \{([^}]*)\}", geral, re.MULTILINE)
    assert regra and "top: 0" in regra.group(1) and "bottom: auto" in regra.group(1)
    assert "proxima-gancho.so-leitor {" not in CSS  # o remendo próprio da capa saiu
