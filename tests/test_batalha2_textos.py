"""Batalha 2, 1ª leva (26/10/2026): dados, cálculos e textos.

G1-N1/G2-1  SLA com um só vocabulário: a meta é "metade em até 2 dias de trabalho (16 h)"; "dias úteis" só no prazo
            de calendário do cliente (C3b); "típico" no lugar de "mediana" no texto da página; nenhum corte fora do
            gráfico (o "passam de 5 dias" saiu da página).
G2-2        O selo do mês perto da meta (15,5–16,5 h) com uma casa, na mesma função do estudo (C6).
"""

import re

import pandas as pd
from fastapi.testclient import TestClient

from app.apresentacoes.gestao_orcamentos.sla import calculos as c
from tests import test_sla_d38 as d38


def _texto_visivel(html: str) -> str:
    """O texto da página sem marcação, sem <style>/<script> e sem atributos (classes como "mes-mediana" não contam)."""
    html = re.sub(r"<(style|script)\b.*?</\1>", " ", html, flags=re.S)
    return re.sub(r"<[^>]+>", " ", html)


def _pagina(monkeypatch, mov, url="/viu-agenciamento/sla"):
    from app import dados, sla
    from app.main import app

    monkeypatch.setattr(dados.sla, "df", lambda forcar=False: mov)
    sla._cache.clear()
    with TestClient(app) as cli:
        html = cli.get(url).text
    sla._cache.clear()
    return html


def test_h_meta_uma_casa_perto_da_meta():
    assert c._h_meta(16.4) == "16,4 h" and c._h_meta(16.01) == "16,1 h"  # acima: arredonda para cima
    assert c._h_meta(15.7) == "15,7 h" and c._h_meta(15.96) == "15,9 h" and c._h_meta(15.5) == "15,5 h"  # abaixo: para baixo
    assert c._h_meta(16.0) == "16 h" and c._h_meta(15.4) == "15 h" and c._h_meta(16.5) == "17 h"


def test_mes_com_tipico_de_16_4_h_nao_aparece_como_16_h(monkeypatch):
    monkeypatch.setitem(d38.FINS, 16.4, pd.Timedelta(days=2, minutes=24))
    mov = d38._mov([(16.4, 3), (40, 1), (1, 1)], "b2-164")  # mediana de março = 16,4 h; 40% em até 2 dias
    e = c.entrega(mov, "2026-10")
    marco = e["meses"][2]
    assert marco["mediana_txt"] == "16,4 h" and marco["tela"]["ate2"] < 50
    html = _pagina(monkeypatch, mov).replace(" ", " ")
    assert '<span class="mes-mediana">16,4 h</span>' in html and "típico 16,4 h de trabalho" in html


def test_sla_um_so_vocabulario(movimentos, monkeypatch):
    from app.main import app

    with TestClient(app) as cli:
        html = cli.get("/viu-agenciamento/sla").text
    rotulo = html.split('class="meta-chave"')[1].split('<span class="legenda">')[0].replace(" ", " ")  # D54: rótulo na linha do título
    rotulo = rotulo.replace("&nbsp;", " ")
    assert "meta sugerida: 2 dias de trabalho</span>" in rotulo and "metade em até 2 dias de trabalho (16 h)" in rotulo  # D54
    assert "dias úteis" not in rotulo and "dia útil" not in rotulo
    visivel = _texto_visivel(html)
    assert "mediana" not in visivel.lower()  # "típico" na tela e no leitor de tela
    assert "no calendário para o cliente receber" in visivel  # C3b: dias úteis = calendário do cliente
    assert "5 dias" not in visivel  # nenhum corte fora do gráfico
    # o complemento escrito é o mesmo número da legenda "acima de 2 dias"
    acima = re.search(r"acima de 2 dias <strong>(\d+)%</strong>", html).group(1)
    if acima != "0":
        assert f"{acima}% passam de 2 dias de trabalho" in visivel.replace(" ", " ")
    else:
        assert "passam de 2 dias de trabalho" not in visivel
    mov = d38._mov([(1, 3), (24, 2)], "b2-acima")  # 2 de 5 acima de 2 dias = 40%
    html = _pagina(monkeypatch, mov)
    assert "acima de 2 dias <strong>40%</strong>" in html and "40% passam de 2 dias de trabalho" in _texto_visivel(html)


def test_regras_do_sla_pelo_mes_da_entrega():
    from app.main import app

    with TestClient(app) as cli:
        r = cli.get("/viu-agenciamento/sla/regras", follow_redirects=False)
    # 2ª leva (G3-7/G4-N1): a página de regras saiu; o endereço antigo leva ao estudo, que diz a regra vigente
    assert r.status_code == 301 and r.headers["location"] == "/viu-agenciamento/sla/como-medimos#1"


# G2-4: "O que falta" sem marcador provisório, estado honesto e Resultado fora do fluxo da reunião
def test_pedidos_sem_marcador_provisorio():
    from app.apresentacoes.gestao_orcamentos import pendencias

    for o_que, porque, quem in pendencias.PEDIDOS:
        for texto in (o_que, porque, quem):
            assert not re.search(r"(^|\s)X(\s|$)", texto) and "TODO" not in texto and "XXX" not in texto, texto
    meta = next(p for p in pendencias.PEDIDOS if "meta do SLA" in p[0])
    assert "2 dias de trabalho (16 h)" in meta[1] and "5 dias" not in meta[1]


def test_o_que_falta_estado_com_nota():
    from app.main import app

    with TestClient(app) as cli:
        html = cli.get("/viu-agenciamento/o-que-falta").text
    assert "Pronta · meta a oficializar" in html and "Pronta · 2 decisões abertas" in html


def test_resultado_fora_da_reuniao_e_regras_sem_conteudo_voltam(monkeypatch):
    from app import config
    from app.main import app

    monkeypatch.setattr(config, "MODO_APRESENTACAO", True)
    monkeypatch.setattr(config, "SECOES_VISIVEIS", frozenset())
    with TestClient(app) as cli:
        assert cli.get("/viu-agenciamento/negocios-fechados").status_code == 404
        html = cli.get("/viu-agenciamento/previsao").text
        assert 'href="/viu-agenciamento/encerramento" rel="next"' in html  # V2: a Previsão segue a última
        r = cli.get("/viu-agenciamento/previsao/regras", follow_redirects=False)
        assert r.status_code == 301 and r.headers["location"] == "/viu-agenciamento/previsao"


# G4-N10 / G1-N11: uma só data de corte (E3) no site, no job e no ML; job travado com CONGELAR; falha visível
def test_corte_e3_unico():
    from app import corte
    from app.apresentacoes.gestao_orcamentos.previsao import job

    # carga de segunda 02/11/2026 09:00 (SP) sem linhas em 31/10 (sábado) e 01/11: outubro fecha pela E3
    df = pd.DataFrame({"data": pd.to_datetime(["2026-10-29", "2026-10-30"]),
                       "_processado_em": pd.Timestamp("2026-11-02 12:00", tz="UTC")})
    processado_em, fim = job.da_carga(df)
    assert fim == pd.Timestamp("2026-11-01") and job.mes_fechado(fim) == "2026-10"
    assert corte.mes_fechado(pd.Timestamp("2026-10-30")) == "2026-09"  # a regra antiga (MAX(data)) atrasaria outubro
    # 26/10/2026 09:01 em SP (12:01Z) → dados até 25/10, o mesmo dia do rodapé do site
    assert corte.fim("2026-10-26 12:01:46+00:00") == pd.Timestamp("2026-10-25").date()
    assert corte.fim(None, pd.Timestamp("2026-10-24")) == pd.Timestamp("2026-10-24").date()  # sem metadado
    from app import dados
    assert dados.data_carga(df) == corte.dia_da_carga(df["_processado_em"])


def test_ml_snapshot_usa_e3():
    from ml import dados as mld

    from app import config

    # D57: a série vem da view gold, que já aplica a E3 (dados_ate = véspera do _processado_em em São Paulo)
    sql = mld.SQL_SERIE.format(previsao_mensal=config.TAB_PREVISAO_MENSAL)
    assert "gld_agenciamento_previsao_mensal" in sql and "dados_ate" in sql and "completo" in sql


def test_job_nao_dispara_congelado(monkeypatch, tmp_path):
    from app import config
    from app.apresentacoes.gestao_orcamentos.previsao import job

    chamadas = []
    monkeypatch.setattr(job, "disponivel", lambda: True)
    monkeypatch.setattr(job, "_pasta_ml", lambda: tmp_path / "ml")
    monkeypatch.setattr(job.subprocess, "Popen", lambda *a, **k: chamadas.append(a))
    monkeypatch.setattr(job, "_ultimo_disparo", 0.0)
    for congelar, modo in ((True, False), (False, True)):
        monkeypatch.setattr(config, "CONGELAR", congelar)
        monkeypatch.setattr(config, "MODO_APRESENTACAO", modo)
        assert not job.disparar("rotina") and not job.disparar("acompanhamento")
    assert chamadas == []


def test_falha_do_job_aparece_na_pagina(monkeypatch, tmp_path):
    import json

    from app.apresentacoes.gestao_orcamentos.previsao import job
    from app.main import app

    saida = tmp_path / "ml" / "saida"
    saida.mkdir(parents=True)
    (saida / "rotina_estado.json").write_text(json.dumps(
        {"modo": "rotina", "inicio": "2026-11-02T09:05:00", "fim": "2026-11-02T09:07:00", "codigo": 1,
         "erro": "SnapshotInvalido: série vazia"}), encoding="utf-8")
    monkeypatch.setattr(job, "_pasta_ml", lambda: tmp_path / "ml")
    f = job.falhou()
    assert f and f["fim"].strftime("%d/%m %H:%M") == "02/11 09:07"
    with TestClient(app) as cli:
        html = cli.get("/viu-agenciamento/previsao").text
    if "pv-controles" in html:  # com previsao.json válido: avisa a falha e não promete cálculo (Caio, 31/10: sem o texto do retrato)
        assert "a última atualização falhou em 02/11/2026 09:07" in html and "sendo calculado" not in html
    (saida / "rotina_estado.json").write_text(json.dumps({"modo": "rotina", "inicio": "x", "fim": "y", "codigo": 0}),
                                              encoding="utf-8")
    assert job.falhou() is None


def test_rodar_grava_estado_e_trava(monkeypatch, tmp_path):
    import json

    import pytest as _pt

    from ml import rodar

    monkeypatch.setattr(rodar, "ESTADO", tmp_path / "rotina_estado.json")
    monkeypatch.setattr(rodar, "TRAVA", tmp_path / "rotina.lock")
    vista = []
    monkeypatch.setattr(rodar.previsao, "atualizar_acompanhamento", lambda: vista.append(rodar.TRAVA.exists()) or True)
    rodar._registrado("acompanhamento", rodar.acompanhamento, extrair=False)
    e = json.loads((tmp_path / "rotina_estado.json").read_text(encoding="utf-8"))
    assert vista == [True] and not rodar.TRAVA.exists() and e["codigo"] == 0 and e["fim"]

    def quebra(**_):
        raise RuntimeError("BigQuery fora")
    with _pt.raises(RuntimeError):
        rodar._registrado("rotina", quebra)
    e = json.loads((tmp_path / "rotina_estado.json").read_text(encoding="utf-8"))
    assert e["codigo"] == 1 and "BigQuery fora" in e["erro"]


# G4-N13: contrato do snapshot antes do retrato; histórico só com retrato e protocolo
def _snapshot():
    meses = [str(m) for m in pd.period_range("2025-10", "2026-09", freq="M")]
    serie = pd.DataFrame([{"mes": m, "tipo": t, "pedidos": 100, "estimados": 0, "completo": True,
                           "dados_ate": "2026-10-25", "processado_em": "2026-10-26 12:01:46+00:00"}
                          for t in ("Inbound", "Mercado") for m in meses])
    excl = pd.DataFrame([{"mes": m, "tipo": t, "exclusivos": 60, "nao_exclusivos": 30, "sem_talento": 10, "total": 100,
                          "processado_em": "2026-10-26 12:01:46+00:00", "dados_ate": "2026-10-25"}
                         for t in ("Inbound", "Mercado") for m in meses if m >= "2026-01"])
    return serie, excl


def test_snapshot_valido_e_divergente():
    from ml import dados as mld

    serie, excl = _snapshot()
    assert mld.validar(serie, excl) == ([], [])
    excl.loc[0, ["exclusivos", "total"]] = [61, 101]  # silver ≠ gold: só aviso
    assert mld.validar(serie, excl)[0] == [] and mld.validar(serie, excl)[1]
    ruim = serie.drop(index=3)  # um mês completo sumiu do Inbound
    assert any("sem dado" in p for p in mld.validar(ruim, excl)[0])
    ruim = serie.copy()
    ruim.loc[0, "processado_em"] = "2026-10-25 12:00:00+00:00"  # carga misturada
    assert any("misturado" in p for p in mld.validar(ruim, excl)[0])


def test_snapshot_invalido_nao_grava(monkeypatch, tmp_path):
    import pytest as _pt

    from ml import dados as mld

    serie, excl = _snapshot()
    serie.loc[0, "pedidos"] = -1
    monkeypatch.setattr(mld, "extrair", lambda: (serie, excl, pd.DataFrame(), pd.DataFrame()))  # D56: + silver 2025, lotes
    monkeypatch.setattr(mld, "PASTA", tmp_path)
    monkeypatch.setattr(mld, "ARQ_SERIE", tmp_path / "serie_mensal.csv")
    monkeypatch.setattr(mld, "ARQ_EXCLUSIVIDADE", tmp_path / "exclusividade.csv")
    monkeypatch.setattr(mld, "ARQ_EXCLUSIVIDADE_2025", tmp_path / "exclusividade_2025.csv")
    monkeypatch.setattr(mld, "ARQ_LOTES", tmp_path / "lotes_vigente.csv")
    with _pt.raises(mld.SnapshotInvalido):
        mld.gravar()
    assert not (tmp_path / "serie_mensal.csv").exists() and not list(tmp_path.glob("*.tmp"))


def test_historico_exige_retrato_e_protocolo(tmp_path):
    import pytest as _pt

    from ml import previsao as mlp

    assert all(x["protocolo"] and x["retrato"] for x in mlp.linhas_do_historico())  # o arquivo real
    arq = tmp_path / "h.jsonl"
    arq.write_text('{"carga": "x"}\n', encoding="utf-8")
    with _pt.raises(ValueError):
        mlp.linhas_do_historico(arq)


def test_mes_de_outro_ano_leva_o_ano():
    from app.apresentacoes.gestao_orcamentos.previsao import calculos as pc

    assert pc._curto("2026-11") == "nov" and pc._curto("2027-01") == "jan/27"
    assert pc._mes_nome("2027-01").endswith("/27")
