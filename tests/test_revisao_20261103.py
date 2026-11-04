"""Revisão de 03/11/2026 (consenso de 3 revisores): correções de interface, acessibilidade e entrega do vídeo.

O que dá para conferir pela página servida (gancho fora do Tab) e pelo arquivo (vídeo com faststart) é conferido como
comportamento; as regras de JS e CSS são conferidas no código (a medição no navegador está no registro da revisão, nas
fichas das páginas). A virada do ano do SLA (A3) está em tests/test_recorte_exibicao.py; chave e cache dos estáticos
(C1, C2) em tests/test_seguranca_iniciativas.py.
"""

import re
import struct
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

RAIZ = Path(__file__).resolve().parents[1]
JS = (RAIZ / "app" / "static" / "apresentacao.js").read_text(encoding="utf-8")
CSS = (RAIZ / "app" / "static" / "estilo.css").read_text(encoding="utf-8")
VIDEO = RAIZ / "app" / "static" / "video" / "lia-na-pratica.mp4"


@pytest.fixture
def cliente():
    from app.main import app

    with TestClient(app) as c:
        yield c


def _regra(seletor: str, css: str = CSS) -> str:
    """Corpo da regra cujo seletor é exatamente `seletor` (primeira ocorrência)."""
    m = re.search(r"(?:^|[}\n])\s*" + re.escape(seletor) + r"\s*\{([^}]*)\}", css)
    assert m, f"regra ausente: {seletor}"
    return m.group(1)


def _gancho(html: str) -> str:
    return re.search(r'<a href="[^"]*" rel="next" data-proxima-secao[^>]*>', html).group(0)


# ------------------------------------------------------------------ A10/B3/C12: gancho escondido fora da ordem do Tab

@pytest.mark.parametrize("pagina", ["capa", "roadmap", "sla/como-medimos"])
def test_gancho_escondido_sai_da_ordem_do_tab(cliente, pagina):
    html = cliente.get(f"/viu-agenciamento/{pagina}").text
    assert re.search(r'<nav class="proxima proxima-gancho so-leitor"', html)
    assert 'tabindex="-1"' in _gancho(html)  # o leitor de tela e as setas seguem usando o link


def test_gancho_visivel_continua_no_tab(cliente):
    html = cliente.get("/viu-agenciamento/talentos").text
    assert re.search(r'<nav class="proxima proxima-gancho"', html)
    assert "tabindex" not in _gancho(html)


# ------------------------------------------------------------------ A2/B7/C5: vídeo da LIA com o índice no começo

def _atomos(caminho: Path) -> list[str]:
    nomes, pos, tam = [], 0, caminho.stat().st_size
    with caminho.open("rb") as f:
        while pos < tam:
            f.seek(pos)
            tamanho, nome = struct.unpack(">I4s", f.read(8))
            if tamanho == 1:
                tamanho = struct.unpack(">Q", f.read(8))[0]
            assert tamanho >= 8, "átomo inválido no MP4"
            nomes.append(nome.decode("latin-1"))
            pos += tamanho
    return nomes


def test_video_da_lia_tem_o_indice_antes_dos_dados():
    """faststart: o navegador lê o índice (moov) no começo e toca sem pedir o fim do arquivo de 42 MB."""
    nomes = _atomos(VIDEO)
    assert "moov" in nomes and "mdat" in nomes
    assert nomes.index("moov") < nomes.index("mdat")


# ------------------------------------------------------------------ JS (apresentacao.js)

def test_setas_nao_trocam_de_pagina_nem_de_slide_com_pop_up_aberto():
    """A1/B1/C3: na Previsão, a → com "Modelos comparados" aberto levava ao Encerramento."""
    assert 'var dialogoAberto = !!document.querySelector("dialog[open]");' in JS
    assert re.search(r"if \(\(paraFrente \|\| paraTras\) && !dialogoAberto && ", JS)
    assert "if (slides.length < 2 || dialogoAberto) return;" in JS


def test_tela_cheia_do_video_nao_marca_o_portal():
    """A5/B9/C9: só a página (raiz) em tela cheia liga html.tela-cheia; o <video> em tela cheia, não."""
    assert "var ativo = document.fullscreenElement === raiz;" in JS
    assert "var ativo = !!document.fullscreenElement;" not in JS


def test_esc_no_botao_play_interrompe_a_corrida():
    """A7/B10/C7: no botão, só Enter e Espaço ficam com o click; o Esc para a corrida."""
    corpo = re.search(r"function interromper\(ev\) \{(.*?)\n    \}", JS, re.DOTALL).group(1)
    assert 'ev.type !== "keydown" || ev.key === "Enter" || ev.key === " "' in corpo


def test_extrato_nao_aplica_style_de_outra_resposta():
    """B13: o DOMParser não interpreta os <style nonce> da página buscada (erro de CSP no console)."""
    assert "parseFromString(neutralizarEstilos(res[0])" in JS
    assert "parseFromString(res[0]" not in JS
    assert 'doc.querySelector("figure.colunas template[data-estilo]")' in JS


# ------------------------------------------------------------------ CSS (estilo.css)

def test_botao_parar_fica_visivel_com_o_mouse_em_cima():
    """A6/B4/C8: o :hover (0,3,0) vencia o estado rodando (0,2,0) e o ■ branco sumia no lavanda."""
    corpo = _regra(".corrida-play.corrida-rodando, .corrida-play.corrida-rodando:hover:not(:disabled)")
    assert "background: var(--azul)" in corpo and "color: #fff" in corpo


def test_regua_como_ler_com_texto_de_ao_menos_12px():
    """A8/B5/C10: rótulos de 10,5 px saíam com menos de 11 px na tela (regra 10, R09)."""
    assert "font: 400 12px var(--sans)" in _regra(".rg-t")
    assert "font-size: 13px" in _regra(".rg-t-puxao")


def test_visor_das_iniciativas_limita_a_altura_da_imagem():
    """A4/B6/C4: com a linha da grade em auto, a imagem alta (Central de qualidade) passava da área do visor."""
    assert "grid-template: minmax(0, 1fr) / minmax(0, 1fr)" in _regra(".ini-v-midia")


def test_lista_dos_pedidos_cabe_no_celular():
    """A9/B11/C11: a 390 px a coluna dos dias quebra a linha (antes: 334 px de conteúdo em 323 visíveis)."""
    m = re.search(r"@media \(max-width: 860px\) \{\s*\.ef-dlg \{.*?\n\}", CSS, re.DOTALL)
    assert m, "bloco do celular do pop-up ausente"
    assert ".ef-tabela td, .ef-tabela tbody th { padding: 0.55em 0.5em; }" in m.group(0)
    assert ".ef-tabela td.ef-num { white-space: normal; }" in m.group(0)


def test_detalhe_com_galeria_tem_letra_menor():
    """A11/B12: com 2 fotos (MIA), o detalhe passava 28 a 40 px da caixa em telas largas."""
    assert "font-size: 1.7em" in _regra(".ini-caixa:has(.ini-galeria:not([hidden])) .ini-caixa-sigla")
    assert re.search(r"\.ini-caixa:has\(\.ini-galeria:not\(\[hidden\]\)\) \.ini-caixa-desc \{ font-size: 0\.9em;", CSS)


def test_gancho_escondido_preso_ao_topo_em_todas_as_paginas():
    """B2/C13: uma regra geral (antes, remendos só na capa e no Roadmap; o estudo rolava 1 px)."""
    assert "top: 0; bottom: auto;" in _regra(".palco > .proxima.so-leitor")
    assert ".palco:has(.rm-palco) > .proxima.so-leitor" not in CSS


def test_sem_animacoes_orfas_da_capa_antiga():
    """B14: os @keyframes da capa validada saíram com ela."""
    for nome in ("capa-pousa", "capa-risca", "capa-gira"):
        assert nome not in CSS


def test_estilo_css_continua_em_crlf():
    bruto = (RAIZ / "app" / "static" / "estilo.css").read_bytes()
    assert b"\r\n" in bruto and b"\n" not in bruto.replace(b"\r\n", b"")
