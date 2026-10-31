"""A cola usa os contextos das telas, nunca uma fotografia numérica escrita à mão."""
import pytest
from app import config
from app.apresentacoes.gestao_orcamentos import cola
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def cliente(sem_bigquery):
    with TestClient(app) as c:
        yield c


@pytest.mark.parametrize('ficha', cola.IDS)
def test_contrato_fichas(cliente, monkeypatch, ficha):
    monkeypatch.setattr(config, 'SINC', True)
    r = cliente.get('/cola/' + ficha, headers={'Origin': config.SINC_ORIGENS[0]})
    assert r.status_code in (200, 503), r.text
    assert r.headers['Access-Control-Allow-Origin'] == config.SINC_ORIGENS[0]
    assert 'no-store' in r.headers['Cache-Control']
    if r.status_code == 200:
        t = r.json()['texto']
        assert t['fala'] and t['passos'] and t['perguntas']
        assert 'P1' not in str(t)  # nenhum identificador do exemplo individual


def test_numeros_e_sentido_acompanham_contexto(monkeypatch):
    e = {'ano': 2027, 'periodo': 'até 5 de fevereiro', 'total': 10,
         'comparacao': {'total': 20, 'variacao': -0.5}, 'grupos': []}
    monkeypatch.setattr(cola.paginas, 'montar_inicio', lambda _: {'entrada': e})
    texto = str(cola.compor('demanda'))
    assert '10 pedidos em 2027' in texto and '−50%' in texto
    assert 'cresceu' not in texto and 'dobro' not in texto
    e['total'] = 35
    e['comparacao']['variacao'] = .75
    texto = str(cola.compor('demanda'))
    assert '35 pedidos em 2027' in texto and '+75%' in texto


def test_origem_e_ambiente(cliente, monkeypatch):
    monkeypatch.setattr(config, 'SINC', True)
    assert cliente.get('/cola/demanda', headers={'Origin': 'https://outro.example'}).status_code == 403
    assert cliente.get('/cola/invalida').status_code == 404
    monkeypatch.setattr(config, 'SINC', False)
    assert cliente.get('/cola/demanda').status_code == 404


def test_falta_de_base_sem_numeros_antigos(cliente, monkeypatch):
    monkeypatch.setattr(config, 'SINC', True)
    def falhar(_):
        raise cola.DadosIndisponiveis('sem dados')
    monkeypatch.setattr(cola, 'compor', falhar)
    r = cliente.get('/cola/demanda')
    assert r.status_code == 503 and 'texto' not in r.json()
