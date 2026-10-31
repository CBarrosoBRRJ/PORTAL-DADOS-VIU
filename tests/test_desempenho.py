"""Desempenho da troca de página (31/10/2026): compressão, cabeçalhos de cache, regras de pré-carga e contas guardadas
por carga. Nada aqui muda o que a tela mostra; só quando e quantas vezes as contas são feitas."""

import json
import time

import pandas as pd
import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def cliente():
    from app.main import app

    return TestClient(app)


# ---------------------------------------------------------------- transporte e cabeçalhos
def test_estaticos_e_paginas_vao_comprimidos(cliente):
    css = cliente.get("/static/estilo.css?v=1", headers={"Accept-Encoding": "gzip"})
    assert css.status_code == 200 and css.headers.get("content-encoding") == "gzip"
    pagina = cliente.get("/viu-agenciamento/sla", headers={"Accept-Encoding": "gzip"})
    assert pagina.status_code == 200 and pagina.headers.get("content-encoding") == "gzip"


def test_cache_longo_so_com_versao_e_paginas_nunca_guardadas(cliente):
    assert cliente.get("/static/estilo.css?v=abc").headers["cache-control"] == "public, max-age=31536000, immutable"
    assert cliente.get("/static/estilo.css").headers["cache-control"] == "public, max-age=86400"
    pagina = cliente.get("/viu-agenciamento/sla")
    assert pagina.headers["cache-control"] == "private, no-store"
    assert pagina.headers["speculation-rules"] == '"/especulacao.json"'


def test_links_dos_estaticos_levam_a_versao(cliente):
    from app.main import versao_estaticos

    html = cliente.get("/viu-agenciamento/sla").text
    assert f"/static/estilo.css?v={versao_estaticos()}" in html
    assert f"/static/apresentacao.js?v={versao_estaticos()}" in html


# ---------------------------------------------------------------- pré-carga (Speculation Rules)
def _regras(cliente):
    r = cliente.get("/especulacao.json")
    assert r.status_code == 200 and r.headers["content-type"].startswith("application/speculationrules+json")
    return r.json()


def test_so_a_proxima_pagina_e_montada_na_hora(cliente):
    """F15: uma renderização extra por página (a próxima da sequência, rel=next); o resto só por intenção (hover)."""
    regras = _regras(cliente)
    assert set(regras) == {"prerender"}  # sem prefetch imediato de vários destinos
    imediata = [p for p in regras["prerender"] if p["eagerness"] == "immediate"]
    assert len(imediata) == 1
    seletor = next(c["selector_matches"] for c in imediata[0]["where"]["and"] if "selector_matches" in c)
    assert seletor == "[rel~=next]"
    outras = [p for p in regras["prerender"] if p is not imediata[0]]
    assert [p["eagerness"] for p in outras] == ["moderate"]


def test_regras_nunca_miram_estaticos_nem_api(cliente):
    for regra in _regras(cliente)["prerender"]:
        condicoes = json.dumps(regra["where"])
        assert '"not": {"href_matches": "/static/*"}' in condicoes
        assert '"not": {"href_matches": "/*/api/*"}' in condicoes


def test_cada_pagina_tem_um_so_link_rel_next(cliente):
    for rota in ("/viu-agenciamento/roadmap", "/viu-agenciamento/sla", "/viu-agenciamento/lia"):
        html = cliente.get(rota).text
        assert html.count('rel="next"') == 1, rota


def test_sem_sondagem_com_base_congelada_ou_em_producao(cliente, monkeypatch):
    """F15: sem a meta do intervalo, apresentacao.js não pede o HTML de novo a cada 5 min."""
    from app import config, dados

    monkeypatch.setattr(dados, "base_congelada", lambda fontes: True)
    assert 'name="relatorio-intervalo"' not in cliente.get("/viu-agenciamento/sla").text
    monkeypatch.setattr(dados, "base_congelada", lambda fontes: False)
    assert 'name="relatorio-intervalo"' in cliente.get("/viu-agenciamento/sla").text
    monkeypatch.setattr(config, "EM_PRODUCAO", True)
    assert 'name="relatorio-intervalo"' not in cliente.get("/viu-agenciamento/sla").text
    assert "if (versaoDados && intervaloDados)" in (cliente.get("/static/apresentacao.js").text)


# ---------------------------------------------------------------- contas guardadas por carga
def test_talentos_calcula_uma_vez_por_carga_e_filtro(cliente, monkeypatch):
    from app import dados
    from app.apresentacoes.gestao_orcamentos import apresentacao as ap
    from app.apresentacoes.gestao_orcamentos.talentos import calculos as talentos

    # em produção df() devolve sempre o mesmo objeto da carga; os dados sintéticos criam um novo a cada chamada
    for t in (dados.talentos, dados.talentos_top):
        fixo = t.df()
        monkeypatch.setattr(t, "df", lambda forcar=False, fixo=fixo: fixo)
    chamadas = []
    original = talentos.top_por_grupo
    monkeypatch.setattr(talentos, "top_por_grupo", lambda *a, **k: chamadas.append(1) or original(*a, **k))
    primeira = ap.montar_talentos({})
    segunda = ap.montar_talentos({})
    assert len(chamadas) == 1
    assert segunda is not primeira and segunda["talentos"] is not primeira["talentos"]  # F18: cópia, não o mesmo objeto
    assert segunda["heroi"] == primeira["heroi"] and segunda["seletor"] == primeira["seletor"]
    ap.montar_talentos({"talentos": "exclusivos"})
    assert len(chamadas) == 2  # outro filtro, outra conta
    nova = dados.talentos_top.df().copy()  # carga nova (outro objeto): refaz
    monkeypatch.setattr(dados.talentos_top, "df", lambda forcar=False: nova)
    ap.montar_talentos({})
    assert len(chamadas) == 3


def test_demanda_guarda_os_numeros_do_ano_e_monta_o_extrato_a_cada_mes(cliente, monkeypatch):
    from app.apresentacoes.gestao_orcamentos import apresentacao as ap
    from app.apresentacoes.gestao_orcamentos.entrada import calculos as entrada

    chamadas = []
    original = entrada.entrada
    monkeypatch.setattr(entrada, "entrada", lambda *a, **k: chamadas.append(1) or original(*a, **k))
    base = ap.montar_inicio({})["entrada"]
    mes = sorted(set(base["meses_extrato"]) & {m["chave"] for m in base["meses"]})[-1]
    com_extrato = ap.montar_inicio({"mes": mes})["entrada"]
    assert len(chamadas) == 1
    assert com_extrato["fotografia"] == base["fotografia"]
    assert base["extrato"] is None  # a cópia guardada não recebe o extrato de outra requisição
    assert ap.montar_inicio({})["entrada"]["extrato"] is None


def test_exemplo_do_estudo_guardado_no_dia_e_sorteado_de_novo_no_dia_seguinte(cliente, monkeypatch):
    from datetime import date

    from app.apresentacoes.gestao_orcamentos import apresentacao as ap
    from app.apresentacoes.gestao_orcamentos.sla import calculos

    chamadas = []
    original = calculos.exemplo
    monkeypatch.setattr(calculos, "exemplo", lambda *a, **k: chamadas.append(1) or original(*a, **k))
    monkeypatch.setattr(calculos, "_hoje", lambda: date(2026, 10, 30))
    ap.montar_estudo_sla({})
    ap.montar_estudo_sla({})
    assert len(chamadas) == 1
    monkeypatch.setattr(calculos, "_hoje", lambda: date(2026, 10, 31))
    ap.montar_estudo_sla({})
    assert len(chamadas) == 2


def test_chave_inclui_corte_congelamento_e_base_minima(monkeypatch):
    from datetime import date

    from app import config
    from app.apresentacoes.gestao_orcamentos import apresentacao as ap
    from app.apresentacoes.gestao_orcamentos.entrada import calculos as entrada

    df = pd.DataFrame({"a": [1]})
    assert ap._guardado("t", (df,), (), lambda: "a") == "a"
    monkeypatch.setattr(entrada, "BASE_MINIMA_VARIACAO", 1)
    assert ap._guardado("t", (df,), (), lambda: "b") == "b"
    monkeypatch.setattr(config, "CORTE_DADOS", date(2026, 11, 30))
    assert ap._guardado("t", (df,), (), lambda: "c") == "c"
    monkeypatch.setattr(config, "CONGELAR", not config.CONGELAR)
    assert ap._guardado("t", (df,), (), lambda: "d") == "d"
    ap.limpar_caches()
    assert not ap._cache_telas and not ap._cache_estudo


def test_cache_das_telas_tem_limite(monkeypatch):
    from app.apresentacoes.gestao_orcamentos import apresentacao as ap

    monkeypatch.setattr(ap, "LIMITE_TELAS", 3)
    df = pd.DataFrame({"a": [1]})
    for k in range(10):
        ap._guardado("teste", (df,), (k,), lambda: k)
    assert len(ap._cache_telas) == 3
    assert ap._guardado("teste", (df,), (9,), lambda: "outro") == 9  # o mais novo continua guardado


def test_processado_em_conta_uma_vez_por_carga(monkeypatch):
    from app import dados

    t = dados.Tabela("teste", "x.y", chave=())
    t._df = pd.DataFrame({"_processado_em": pd.to_datetime(["2026-10-30 12:00"], utc=True)})
    chamadas = []
    original = pd.to_datetime
    monkeypatch.setattr(dados.pd, "to_datetime", lambda *a, **k: chamadas.append(1) or original(*a, **k))
    primeiro = t.processado_em()
    assert t.processado_em() == primeiro and len(chamadas) == 1
    t._df = pd.DataFrame({"_processado_em": original(["2026-10-31 12:00"], utc=True)})  # carga nova
    assert t.processado_em() != primeiro and len(chamadas) == 2


def test_versao_dos_estaticos_nao_espera_a_releitura(monkeypatch):
    from app import config, main

    monkeypatch.setattr(config, "DEV", True)
    monkeypatch.setattr(main, "_hash_estaticos", lambda: time.sleep(0.5) or "novo")
    monkeypatch.setitem(main._versao, "lido_em", time.monotonic() - 10)
    monkeypatch.setitem(main._versao, "refazendo", False)
    antes = main._versao["valor"]
    inicio = time.monotonic()
    assert main.versao_estaticos() == antes  # responde na hora com a versão atual
    assert time.monotonic() - inicio < 0.2
    for _ in range(50):
        if main._versao["valor"] == "novo":
            break
        time.sleep(0.05)
    assert main._versao["valor"] == "novo"
    monkeypatch.setitem(main._versao, "valor", antes)


def test_tamanho_das_imagens_le_so_o_cabecalho(tmp_path):
    from app.apresentacoes.gestao_orcamentos import roadmap

    png = tmp_path / "x.png"
    png.write_bytes(bytes.fromhex("89504e470d0a1a0a") + b"\0\0\0\rIHDR" + (40).to_bytes(4, "big") + (20).to_bytes(4, "big")
                    + b"\0" * 5000)
    assert roadmap._tamanho(png) == (40, 20)
    assert roadmap._tamanho(tmp_path / "falta.png") is None


def test_cache_devolve_copia_e_descarta_carga_antiga():
    """F18: mexer no resultado de uma requisição não muda o da seguinte; carga nova tira a antiga da mesma tela."""
    from app.apresentacoes.gestao_orcamentos import apresentacao as ap

    velha, nova = pd.DataFrame({"a": [1]}), pd.DataFrame({"a": [1, 2]})
    r = ap._guardado("t", (velha,), (), lambda: {"lista": [1]})
    r["lista"].append(2)
    assert ap._guardado("t", (velha,), (), lambda: None) == {"lista": [1]}
    ap._guardado("t", (nova,), (), lambda: {"lista": [3]})
    assert [k for k in ap._cache_telas if k[0] == "t"] == [k for k in ap._cache_telas if k[0] == "t" and k[1][0][1] == id(nova)]


def test_limpar_caches_esvazia_todos():
    from app import sla
    from app.apresentacoes.gestao_orcamentos import apresentacao as ap
    from app.apresentacoes.gestao_orcamentos import lia, roadmap
    from app.apresentacoes.gestao_orcamentos.entrada import calculos as entrada
    from app.apresentacoes.gestao_orcamentos.sla import calculos

    for c in (ap._cache_telas, ap._cache_estudo, calculos._cache, calculos._cache_status, sla._cache, entrada._cache,
              lia._cache, roadmap._tamanhos):
        c["x"] = 1
    ap.limpar_caches()
    assert not any((ap._cache_telas, ap._cache_estudo, calculos._cache, calculos._cache_status, sla._cache,
                    entrada._cache, lia._cache, roadmap._tamanhos))


def test_entregas_e_horas_por_status_publicadas_juntas_sob_concorrencia(movimentos):
    """F14: várias threads pedindo a mesma carga recebem o mesmo par coerente (entregas + horas por status)."""
    import threading

    from app.apresentacoes.gestao_orcamentos.sla import calculos

    calculos.limpar_cache()
    saidas, erros = [], []

    def pedir():
        try:
            saidas.append((calculos.entregas(movimentos), calculos.horas_por_status(movimentos)))
        except Exception as e:  # noqa: BLE001
            erros.append(e)

    threads = [threading.Thread(target=pedir) for _ in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert not erros
    e0, s0 = saidas[0]
    assert all(e is e0 and s is s0 for e, s in saidas)
    assert len(calculos._cache) == len(calculos._cache_status) == 1


def test_mes_parcial_guardado_como_par(movimentos):
    from app import sla

    sla.limpar_cache()
    p = sla.mes_parcial(movimentos)
    assert sla._cache["parcial"][1] == p and sla.mes_parcial(movimentos) == p


def test_lia_guardada_pela_versao_do_retrato(cliente, monkeypatch):
    """F20: a tela da LIA não relê o retrato.json enquanto ele não muda."""
    from app.apresentacoes.gestao_orcamentos import apresentacao as ap
    from app.apresentacoes.gestao_orcamentos import lia

    chamadas = []
    original = lia.tela
    monkeypatch.setattr(lia, "tela", lambda *a, **k: chamadas.append(1) or original(*a, **k))
    ap.montar_lia({})
    ap.montar_lia({})
    assert len(chamadas) == 1


def test_capa_nao_calcula_a_medida_do_sla(cliente, monkeypatch):
    from app.apresentacoes.gestao_orcamentos import apresentacao as ap

    monkeypatch.setitem(ap.APRESENTACAO.capa, "medida", lambda: (_ for _ in ()).throw(AssertionError("calculou")))
    assert cliente.get("/viu-agenciamento/capa").status_code == 200


def test_hash_dos_estaticos_nao_le_o_conteudo(monkeypatch):
    """F20: a versão vem de caminho, tamanho e data; ler bytes não faz parte da conta."""
    from pathlib import Path

    from app import main

    monkeypatch.setattr(Path, "read_bytes", lambda self: (_ for _ in ()).throw(AssertionError("leu " + self.name)))
    assert len(main._hash_estaticos()) == 12
