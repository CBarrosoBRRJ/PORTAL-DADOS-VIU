"""D62 (Caio, 27/10/2026): sincronia do portal com a cola do apresentador (porta 8200) por /sinc: guarda a página atual,
a versão sobe só quando a página (normalizada) muda, aceita só caminhos do próprio portal, libera CORS só para a cola e
não existe com SINC desligado (em produção, sempre desligado)."""
import json

import pytest
from fastapi.testclient import TestClient

from app import config, main
from app.main import app


@pytest.fixture
def cliente(monkeypatch):
    monkeypatch.setattr(config, "SINC", True)
    monkeypatch.setattr(main, "_SINC", {"url": None, "versao": 0, "origem": None, "sessao": "teste"})
    with TestClient(app) as c:
        yield c


def _post(c, url, origem="cola", **kw):
    return c.post("/sinc", content=json.dumps({"url": url, "origem": origem}), headers={"Content-Type": "text/plain", **kw})


def test_sinc_guarda_a_pagina_e_so_sobe_a_versao_quando_muda(cliente):
    assert {k: v for k, v in cliente.get("/sinc").json().items() if k != "sessao"} == {"url": None, "versao": 0, "origem": None}
    assert _post(cliente, "/viu-agenciamento/atendimento#1").json()["versao"] == 1
    # mesma página: sem a query e sem o # (fora do estudo) não conta como mudança
    assert _post(cliente, "/viu-agenciamento/atendimento?talentos=exclusivos", "portal").json()["versao"] == 1
    # no estudo o # é o slide: muda
    assert _post(cliente, "/viu-agenciamento/sla/como-medimos#2", "portal").json()["versao"] == 2
    # slide 2: o quadro (Formato/Sino/Faixas, ?passo=) também é posição; sem passo = quadro 1
    assert _post(cliente, "/viu-agenciamento/sla/como-medimos?passo=1#2", "portal").json()["versao"] == 2
    assert _post(cliente, "/viu-agenciamento/sla/como-medimos?passo=2#2").json()["versao"] == 3
    assert _post(cliente, "/viu-agenciamento/sla/como-medimos?talentos=exclusivos&passo=2#2", "portal").json()["versao"] == 3
    assert _post(cliente, "/viu-agenciamento/sla/como-medimos?passo=3#3", "portal").json()["versao"] == 4  # passo só conta no 2
    assert _post(cliente, "/viu-agenciamento/sla/como-medimos?passo=1#3", "portal").json()["versao"] == 4
    s = _post(cliente, "/viu-agenciamento/sla/como-medimos#2").json()
    assert s["versao"] == 5
    s = _post(cliente, "/viu-agenciamento/sla/como-medimos#3").json()
    assert {k: s[k] for k in ("url", "versao", "origem")} == {"url": "/viu-agenciamento/sla/como-medimos#3", "versao": 6, "origem": "cola"} and s["sessao"]
    assert cliente.get("/sinc").json() == s


def test_sinc_recusa_endereco_de_fora_e_libera_so_a_cola(cliente):
    for ruim in ("https://exemplo.com/x", "//exemplo.com", "viu-agenciamento", "/" + "a" * 400):
        assert _post(cliente, ruim).status_code == 400
    assert _post(cliente, "/viu-agenciamento", "outro").status_code == 400
    assert cliente.post("/sinc", content="não é json", headers={"Content-Type": "text/plain"}).status_code == 400
    r = cliente.get("/sinc", headers={"Origin": "http://127.0.0.1:8200"})
    assert r.headers["access-control-allow-origin"] == "http://127.0.0.1:8200"
    assert "access-control-allow-origin" not in cliente.get("/sinc", headers={"Origin": "https://exemplo.com"}).headers


def test_sinc_desligado_nao_existe(cliente, monkeypatch):
    assert '<script src="/static/sinc.js' in cliente.get("/viu-agenciamento/atendimento").text
    monkeypatch.setattr(config, "SINC", False)
    assert cliente.get("/sinc").status_code == 404 and _post(cliente, "/viu-agenciamento").status_code == 404
    assert "sinc.js" not in cliente.get("/viu-agenciamento/atendimento").text

