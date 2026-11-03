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
    assert len(fotos) == len(catalogo.FOTOS["raio-x"]) == 1
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
    assert html.count("data-ini-anexo-fixo") == 1 and 'href="/static/iniciativas/raio-x.webp?v=' in html
    js = (RAIZ / "app" / "static" / "iniciativas.js").read_text(encoding="utf-8")
    assert "if (!a.fixo) item.appendChild(b);" in js  # sem botão de remover na edição
    assert "dashboard-raiox" not in cliente.get("/viu-agenciamento/roadmap").text  # saiu do Roadmap
