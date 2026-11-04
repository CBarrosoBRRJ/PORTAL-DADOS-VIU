"""Caio, 03/11/2026 (bug visto pelo gerente): imagens .webp saíam como application/octet-stream (com nosniff), e o
"Abrir em nova aba" do visor baixava o arquivo em vez de mostrar. Os tipos ficam registrados em app/main.py."""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def cliente():
    from app.main import app

    with TestClient(app) as c:
        yield c


@pytest.mark.parametrize(("caminho", "tipo"), [
    ("/static/iniciativas/raio-x.webp", "image/webp"),
    ("/static/roadmap/bigquery.webp", "image/webp"),
    ("/static/fontes/playfair-display-latin-wght-normal.woff2", "font/woff2"),
    ("/static/video/lia-na-pratica.mp4", "video/mp4"),
])
def test_estaticos_com_o_tipo_certo(cliente, caminho, tipo):
    r = cliente.get(caminho, headers={"Range": "bytes=0-15"})
    assert r.status_code in (200, 206) and r.headers["content-type"].split(";")[0] == tipo
    assert "attachment" not in r.headers.get("content-disposition", "")
