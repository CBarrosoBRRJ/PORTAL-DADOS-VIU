"""Caio, 03/11/2026: foto fixa do card Raio-X nas Iniciativas (catalogo.FOTOS): arquivo do site em
app/static/iniciativas/, como as imagens do Roadmap, sem passar pelo banco. Aparece na galeria e no visor do card, com
a versão do arquivo no endereço, e não pode ser removida pela tela."""

import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.apresentacoes.gestao_orcamentos import iniciativas
from app.apresentacoes.gestao_orcamentos.iniciativas import api, catalogo

API = "/viu-agenciamento/iniciativas/api"
RAIZ = Path(__file__).resolve().parents[1]


@pytest.fixture
def cliente(quadro_limpo):
    from app.main import app

    with TestClient(app) as c:
        yield c


def test_foto_do_raio_x_existe_e_vem_como_anexo_fixo(quadro_limpo):
    assert (RAIZ / "app" / "static" / "iniciativas" / "raio-x.webp").is_file()
    fotos = api.fotos_fixas("raio-x")
    assert len(fotos) == len(catalogo.FOTOS["raio-x"]) == 10  # as abas do painel (03/11/2026, noite)
    assert all(re.fullmatch(r"/static/iniciativas/raio-x[a-z0-9-]*\.webp\?v=[0-9a-f]+", x["url"]) for x in fotos)
    f = fotos[0]
    assert f["fixo"] is True and f["imagem"] is True and f["tipo"] == "image/webp"
    assert re.fullmatch(r"/static/iniciativas/raio-x\.webp\?v=[0-9a-f]+", f["url"])
    assert api.fotos_fixas("lia") == []  # só quem está no catálogo de fotos
    card = next(i for g in iniciativas.tela()["grupos"] for i in g["itens"] if i["id"] == "raio-x")
    assert card["anexos"][0]["id"] == "foto-raio-x-1"


def test_foto_fixa_na_api_e_na_pagina(cliente):
    r = cliente.get(f"{API}/iniciativas").json()
    assert r["anexos"]["raio-x"][0]["fixo"] is True
    assert cliente.get(f"{API}/iniciativas/raio-x/anexos").json()[0]["id"] == "foto-raio-x-1"
    html = cliente.get("/viu-agenciamento/iniciativas").text
    assert html.count("data-ini-anexo-fixo") == 12 and 'href="/static/iniciativas/raio-x.webp?v=' in html
    js = (RAIZ / "app" / "static" / "iniciativas.js").read_text(encoding="utf-8")
    assert "if (!a.fixo) item.appendChild(b);" in js  # sem botão de remover na edição
    assert "dashboard-raiox" not in cliente.get("/viu-agenciamento/roadmap").text  # saiu do Roadmap


def test_mia_usa_as_imagens_da_central_de_qualidade(quadro_limpo):
    """Caio, 03/11/2026: o card MIA mostra as duas imagens da Central de qualidade, as mesmas dos dashboards do Roadmap."""
    fotos = api.fotos_fixas("mia")
    assert [f["id"] for f in fotos] == ["foto-mia-1", "foto-mia-2"]
    assert re.fullmatch(r"/static/roadmap/dashboard-qualidade\.webp\?v=[0-9a-f]+", fotos[0]["url"])
    assert re.fullmatch(r"/static/roadmap/dashboard-qualidade-email\.webp\?v=[0-9a-f]+", fotos[1]["url"])
    card = next(i for g in iniciativas.tela()["grupos"] for i in g["itens"] if i["id"] == "mia")
    assert [a["id"] for a in card["anexos"][:2]] == ["foto-mia-1", "foto-mia-2"]


def test_fechar_pop_up_com_o_mouse_nao_fecha_o_detalhe():
    """Validação de 03/11/2026: fechar o visor ou o "Expandir" pelo botão Fechar (ou clicando no fundo) fechava também o
    detalhe do card, porque o clique chegava ao "clique fora fecha" do documento com o pop-up já fechado, e o foco caía no
    <body>. O clique dentro de um <dialog> não pode fechar o detalhe; assim o foco volta à miniatura ou ao "Expandir"."""
    js = (RAIZ / "app" / "static" / "iniciativas.js").read_text(encoding="utf-8")
    inicio = js.index('document.addEventListener("click", function (e) {')
    trecho = js[inicio:js.index("});", inicio)]
    assert 'e.target.closest("dialog")' in trecho and trecho.index('closest("dialog")') < trecho.index("fecharOutros(null)")


def test_galeria_do_detalhe_comeca_no_zero_e_seta_anterior_desligada():
    """Revalidação de 04/11/2026: a lista da galeria tem padding e scroll-snap obrigatório, e sem scroll-padding o snap
    alinhava a 1ª miniatura à borda do padding (scrollLeft 3 a 5 px ao abrir). Com isso a seta "anterior" nunca ficava
    desligada no início (verSetasGaleria: scrollLeft <= 1). O scroll-padding igual ao padding faz o início valer 0."""
    css = (RAIZ / "app" / "static" / "estilo.css").read_text(encoding="utf-8")
    regra = re.search(r"\.ini-galeria-lista \{([^}]*)\}", css).group(1)
    padding = re.search(r"(?:^|;)\s*padding:\s*([^;]+);", regra).group(1).strip()
    assert "scroll-snap-type: x mandatory" in regra
    assert re.search(r"scroll-padding(?:-inline)?:\s*" + re.escape(padding) + ";", regra)
