"""Auditoria do Codex de 31/10/2026, achados de dados (docs/auditoria/correcoes_2026-10-31.md, "Dados e congelamento").

F03 Previsão coerente com a base (datas próprias, aviso discreto) · F05 LIA com retrato fora do contrato e aquecimento
que não derruba o portal · F10 rodapés por seção · F13 arredondamento único (meio para cima; 1/8 = 13%).
Os testes da base congelada (F01, F02, F07, F08) estão em tests/test_corte.py."""

import json
from datetime import datetime

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from app import config, dados, formato
from app.apresentacoes.gestao_orcamentos import lia, lia_na_pratica
from app.apresentacoes.gestao_orcamentos.atendimento import calculos as atendimento
from app.apresentacoes.gestao_orcamentos.entrada import calculos as entrada
from app.apresentacoes.gestao_orcamentos.previsao import calculos as previsao
from app.apresentacoes.gestao_orcamentos.talentos import calculos as talentos


@pytest.fixture
def cliente():
    from app.main import app

    with TestClient(app) as c:
        yield c


def _rodape(html: str) -> str:
    return html.split('class="rodape-dados">', 1)[1].split("</p>", 1)[0]


# ---------------------------------------------------------------- F03

def _p(retrato="2026-11-02 12:01:46+00:00", acomp="2026-11-02 12:04:00+00:00"):
    return {"carga": {"processado_em": retrato, "dados_ate": "2026-11-01"},
            "acompanhamento": {"mes": "2026-11", "ate": "2026-11-01", "processado_em": acomp}}


def test_f03_mesma_carga_sem_aviso_e_com_a_data_do_acompanhamento():
    c = previsao.coerencia(_p(), "2026-11-02 12:01:30+00:00")
    assert c["aviso"] is None and c["divergentes"] == {} and c["acompanhamento_ate"] == "01/11"


def test_f03_acompanhamento_ou_retrato_de_outra_carga_avisam():
    c = previsao.coerencia(_p(acomp="2026-10-28 12:04:07+00:00"), "2026-11-02 12:01:30+00:00")
    assert c["aviso"] == "acompanhamento de outra carga (28/10/2026)"
    c = previsao.coerencia(_p(retrato="2026-10-26 12:01:46+00:00", acomp="2026-10-28 12:04:07+00:00"),
                           "2026-11-02 12:01:30+00:00")
    assert c["aviso"] == "previsão e acompanhamento de outra carga (26/10/2026 e 28/10/2026)"
    assert previsao.coerencia(None, "2026-11-02") is None
    assert previsao.coerencia(_p(acomp="2026-10-28 12:04:07+00:00"), None)["aviso"] is None  # sem base, nada a comparar


def test_f03_pagina_mostra_a_data_do_acompanhamento_e_o_aviso_no_rodape(cliente, monkeypatch):
    p = previsao.ler()
    ac = p["acompanhamento"]
    ate = pd.Timestamp(ac["ate"]).strftime("%d/%m")
    base = pd.Timestamp(ac["processado_em"]).tz_convert(config.FUSO).to_pydatetime()
    monkeypatch.setattr(dados.entrada, "processado_em", lambda: base)  # base da mesma carga do acompanhamento
    html = cliente.get("/viu-agenciamento/previsao").text
    rodape = _rodape(html)
    assert f"acompanhamento até {ate}" in rodape
    if pd.Timestamp(p["carga"]["processado_em"]).tz_convert(config.FUSO).date() == base.date():
        assert "rodape-aviso" not in rodape
    outra = datetime(2026, 11, 2, 9, 1, tzinfo=config.FUSO)
    monkeypatch.setattr(dados.entrada, "processado_em", lambda: outra)
    rodape = _rodape(cliente.get("/viu-agenciamento/previsao").text)
    assert 'class="rodape-aviso"' in rodape and "de outra carga" in rodape and "<svg" in rodape  # ícone + texto
    assert "Retrato de" not in html  # pedido do Caio: o texto do retrato não volta ao topo


# ---------------------------------------------------------------- F05

RETRATO_OK = json.loads(lia.RETRATO.read_text(encoding="utf-8"))


@pytest.mark.parametrize("estrago, motivo", [
    (lambda r: r.update(semanas=[]), "sem semanas"),
    (lambda r: r.update(dias=[]), "sem dias"),
    (lambda r: r.update(periodos=[{"nao_lead": 0, "lead": 0, "validacao": 0}]), "total de e-mails zero"),
    (lambda r: r.pop("faixas"), "campos ausentes: faixas"),
])
def test_f05_retrato_fora_do_contrato_vira_indisponivel(tmp_path, monkeypatch, estrago, motivo):
    r = json.loads(json.dumps(RETRATO_OK))
    estrago(r)
    with pytest.raises(lia.RetratoInvalido, match=motivo):
        lia.validar_retrato(r)
    arq = tmp_path / "retrato.json"
    arq.write_text(json.dumps(r), encoding="utf-8")
    monkeypatch.setattr(lia, "RETRATO", arq)
    assert lia.tela() is None  # sem ValueError nem ZeroDivisionError


def test_f05_pagina_da_lia_indisponivel_sem_erro(cliente, tmp_path, monkeypatch):
    arq = tmp_path / "retrato.json"
    arq.write_text(json.dumps({**RETRATO_OK, "semanas": []}), encoding="utf-8")
    monkeypatch.setattr(lia, "RETRATO", arq)
    r = cliente.get("/viu-agenciamento/lia")
    assert r.status_code == 200 and "Os números da LIA estão indisponíveis agora" in r.text
    assert _rodape(r.text) == "Dados da LIA indisponíveis"
    arq.write_text("{ quebrado", encoding="utf-8")
    assert cliente.get("/viu-agenciamento/lia").status_code == 200


def test_f05_secao_que_falha_ao_aquecer_nao_derruba_o_portal(monkeypatch, capsys):
    from app.main import app

    def quebra():
        raise RuntimeError("falha inesperada no aquecimento")

    monkeypatch.setattr(lia_na_pratica, "tela", quebra)  # a LIA (seção visível) quebra no aquecimento
    with TestClient(app) as c:
        assert c.get("/saude").status_code == 200
        assert c.get("/viu-agenciamento/sla").status_code == 200  # o resto do portal segue
    saida = capsys.readouterr().out
    assert "falha ao aquecer a seção ao iniciar" in saida and "viu-agenciamento/lia" in saida


# ---------------------------------------------------------------- F10

def test_f10_lia_com_a_data_da_propria_lia(cliente):
    fim = datetime.strptime(RETRATO_OK["fim"], "%Y-%m-%d").strftime("%d/%m/%Y")
    extraido = datetime.strptime(RETRATO_OK["extraido_em"], "%Y-%m-%d %H:%M").strftime("%d/%m/%Y, %H:%M")
    assert _rodape(cliente.get("/viu-agenciamento/lia").text) == f"Dados da LIA até {fim} · extraídos em {extraido}"


@pytest.mark.parametrize("rota", ["/viu-agenciamento/roadmap", "/viu-agenciamento/iniciativas",
                                  "/viu-agenciamento/lia-na-pratica"])
def test_f10_paginas_editoriais_nao_usam_a_carga_de_entradas(cliente, rota):
    r = cliente.get(rota)
    assert r.status_code == 200
    assert _rodape(r.text) == "Conteúdo editorial · não depende da carga de dados"  # regra 9: o rodapé continua


def test_f10_paginas_da_gold_seguem_com_a_data_da_carga(cliente):
    for rota in ("/viu-agenciamento", "/viu-agenciamento/talentos", "/viu-agenciamento/sla",
                 "/viu-agenciamento/previsao"):
        assert _rodape(cliente.get(rota).text).startswith("Dados até "), rota


# ---------------------------------------------------------------- F13

def test_f13_um_oitavo_da_13_por_cento_em_todas_as_paginas():
    assert formato.pct(1 / 8) == "13%" and formato.pct_inteiro(1, 8) == 13
    assert entrada._pct(1, 8) == 13  # Demanda
    assert atendimento.pct_meio(1, 8) == 13  # Atendimento
    df = pd.DataFrame({"grupo": ["todos"], "talento": ["Ana"], "n": [1], "ultimo_pedido": [pd.NaT]})
    assert talentos.top_por_grupo(df, {"grupos": [], "total": 8})["todos"]["pct"] == 13  # Talentos (antes: round = 12)
    assert formato.variacao(1 / 8) == "+13%" and formato.variacao(-1 / 8) == "−13%"


def test_f13_politica_central():
    assert formato.arredondar(12.5) == 13 and formato.arredondar(13.5) == 14 and formato.arredondar(-12.5) == -13
    assert formato.arredondar(0.285 * 100) == 29  # 28,4999… do ponto flutuante é o empate 28,5
    assert formato.pct(0.875, 1) == "87,5%" and formato.pct(0.8745, 1) == "87,5%" and formato.pct(-0.004) == "0%"
    assert formato.pct_inteiro(0, 0) == 0 and formato.pct_inteiro(3, 7) == 43
    import numpy as np

    assert formato.pct_inteiro(np.int64(1), np.int64(8)) == 13
    # parcelas que somam 100 seguem o maior resto (não o arredondamento isolado)
    assert formato.parcelas_100([1, 1, 1]) == [34, 33, 33] and sum(formato.parcelas_100([1, 7])) == 100
    assert entrada._pcts([1, 7]) == formato.parcelas_100([1, 7]) == [13, 87]
