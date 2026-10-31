"""SLA, decisões de 25/10/2026 (D-SLA-1..4) e itens aprovados da auditoria (SLA-D01, D05, D08, D09, D10/D11/D13, D12,
R04, R11, R14, R16) sobre dados sintéticos. Ficha: docs/paginas/sla.md."""

import math
import re
from datetime import date, datetime

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from app import sla
from app.apresentacoes.gestao_orcamentos.sla import calculos as c

E, C = "equipe", "cliente"
CARGA = pd.Timestamp("2026-10-21 21:16:22", tz="UTC")  # 18:16 em São Paulo: dados até 20/10


def _mov(projetos, versao, processado=CARGA):
    """projetos: [(id, exclusivo, nome, [(status, fase, entrada, saida), ...])] na forma da gold."""
    linhas = []
    for pid, exclusivo, nome, passos in projetos:
        for i, (status, fase, ent, sai) in enumerate(passos, start=1):
            linhas.append({"projeto_id": pid, "passo": i, "status": status, "fase": fase, "entrada": pd.Timestamp(ent),
                           "saida": pd.Timestamp(sai) if sai else pd.NaT, "exclusivo": exclusivo, "nome_projeto": nome,
                           "sla_util_horas": None, "_processado_em": processado})
    df = pd.DataFrame(linhas)
    df.attrs["versao"] = versao
    return df


def test_mes_da_primeira_entrega_d_sla_1():
    mov = _mov([("A", True, "A", [("Entrada", E, "2026-03-31 10:00", "2026-03-31 11:00"),
                                  ("Em elaboração - Orçamentos", E, "2026-03-31 11:00", "2026-04-02 10:00"),
                                  ("Aguardando Feedback", C, "2026-04-02 10:00", None)])], "d-sla-1")
    e = c.entregas(mov).set_index("projeto_id")
    assert e.loc["A", "mes"] == "2026-04" and e.loc["A", "mes_entrada"] == "2026-03"


def test_retorno_marca_fica_fora_das_horas_d_sla_2():
    mov = _mov([("A", True, "A", [("Entrada", E, "2026-03-02 10:00", "2026-03-02 11:00"),
                                  ("Em elaboração - Retorno Marca/Executivo", E, "2026-03-02 11:00", "2026-03-02 17:00"),
                                  ("Em Elaboração - Cotação Externa", E, "2026-03-02 17:00", "2026-03-02 19:00"),
                                  ("Aguardando Feedback", C, "2026-03-02 19:00", None)])], "d-sla-2")
    e = c.entregas(mov).set_index("projeto_id")
    # 1 h de fila + 2 h de cotação (fica); as 5 h úteis do Retorno Marca (11h–17h sem almoço) não contam
    assert e.loc["A", "h_trabalho"] == pytest.approx(3.0) and e.loc["A", "h_elaboracao"] == pytest.approx(2.0)


def test_meta_e_faixas_ate_2_dias_d_sla_7(movimentos):
    e = c.entrega(movimentos, sla.mes_parcial(movimentos))
    assert c.LIMITE_DIAS == 2 and c.META_H == 16 and e["limite_horas"] == 16 and e["meta"] == 0.50  # D38
    assert e["ano"]["tela"]["ate2"] == 100 and e["ano"]["tela"]["acima2"] == 0 and "de2a3" not in e["ano"]["tela"]


def test_mes_parcial_vazado_e_aguardando_a2(movimentos):
    e = c.entrega(movimentos, sla.mes_parcial(movimentos))
    out = {m["chave"]: m for m in e["meses"]}["2026-10"]
    assert out["parcial"] and out["n"] == 1 and out["aguardando"]  # < 30 entregas: sem % e sem mediana
    assert out["ate"] == "20/10"  # A2: mesma data do rodapé (véspera da carga em São Paulo)
    assert e["n_ano"] == 4  # o parcial não entra no ano


def test_cobertura_d_sla_4(movimentos, fluxo_mensal):
    cob = c.cobertura(movimentos, fluxo_mensal, "2026-10")
    assert cob == {"n": 4, "m": 4, "pct": 100}  # fev: 2 + 1 da safra de jan; mar: 1
    assert c.cobertura(movimentos, fluxo_mensal.iloc[:1], "2026-10") is None  # N > M: fontes incoerentes, não mostra
    assert c.cobertura(movimentos, None, "2026-10") is None


def test_exemplo_fim_no_dia_de_corte_d08(movimentos):
    x = c.exemplo(movimentos, "2026-10", "todos", date(2026, 10, 24))
    assert x["fim"] == {"quando": "até 20/10", "status": "em aberto"}  # véspera da carga, não o último movimento
    assert x["dias_decisao"] == "15 dias"  # 06/10 10:00 → 20/10 23:59:59 = 14,6 dias


def test_exemplo_estavel_por_hash(movimentos):
    a = c.exemplo(movimentos, "2026-10", "todos", date(2026, 10, 24))
    assert a == c.exemplo(movimentos, "2026-10", "todos", date(2026, 10, 24))


def test_dia_do_exemplo_no_fuso_de_sao_paulo_d05(monkeypatch, movimentos):
    from zoneinfo import ZoneInfo

    class Relogio(datetime):
        @classmethod
        def now(cls, tz=None):  # 24/10 22:00 em São Paulo = 25/10 01:00 em UTC
            return datetime(2026, 10, 24, 22, 0, tzinfo=ZoneInfo("America/Sao_Paulo")).astimezone(tz)

    monkeypatch.setattr(c, "datetime", Relogio)
    assert c._hoje() == date(2026, 10, 24)
    assert c.exemplo(movimentos, "2026-10") == c.exemplo(movimentos, "2026-10", dia=date(2026, 10, 24))


def test_etapas_somam_o_total_escrito_d01():
    us = [int(10.6 * 60_000_000)] * 3  # 31,8 min → 32 min no total
    minutos = c._minutos_etapas(us)
    assert sum(minutos) == 32 and sorted(minutos) == [10, 11, 11]
    assert c._fmt_min(sum(minutos)) == "32 min" and c._fmt_min(664) == "11h04"


def test_arredondamento_meio_para_cima_d11():
    assert c._duracao(30_500_000) == "1 min"  # 30,5 s
    assert c._arred(2.5) == 3 and c._dias(c._arred(2.5)) == "3 dias"


def _todos_zero(n=30):
    return _mov([(f"Z{i}", True, f"Z{i}", [("Entrada", E, "2026-03-02 10:00", "2026-03-02 10:00"),
                                           ("Aguardando Feedback", C, "2026-03-02 10:00", None)]) for i in range(n)],
                "zeros")


def test_exploracao_sem_variacao_d10(monkeypatch):
    mov = _todos_zero()
    assert c.exploracao(mov, "2026-10") is None
    from app import dados
    from app.main import app

    monkeypatch.setattr(dados.sla, "df", lambda forcar=False: mov)
    sla._cache.clear()
    with TestClient(app) as cli:
        assert cli.get("/viu-agenciamento/sla/como-medimos").status_code == 200
    sla._cache.clear()


def _horas(i, h):
    """Projeto que começa numa segunda às 10:00 e leva h horas úteis (1 ≤ h ≤ 7) até o cliente."""
    fim = pd.Timestamp("2026-03-02 10:00") + pd.Timedelta(hours=h + (1 if h > 3 else 0))  # almoço 13h–14h
    return (f"S{i}", i % 2 == 0, f"S{i}", [("Entrada", E, "2026-03-02 10:00", str(fim)), ("Aguardando Feedback", C, str(fim), None)])


def _simetrico():
    projetos, i = [], 0
    for h, qtd in ((1, 2), (2, 5), (3, 9), (4, 10), (5, 9), (6, 5), (7, 2)):
        for _ in range(qtd):
            projetos.append(_horas(i, h))
            i += 1
    return _mov(projetos, "simetrico")


def test_frases_condicionadas_d12(monkeypatch):
    x = c.exploracao(_simetrico(), "2026-10")
    assert x["assim"]["titulo"] == "Os tempos se equilibram dos dois lados" and x["normal"] and not x["media_relevante"]
    from app import dados
    from app.main import app

    monkeypatch.setattr(dados.sla, "df", lambda forcar=False: _simetrico())
    sla._cache.clear()
    with TestClient(app) as cli:
        html = cli.get("/viu-agenciamento/sla/como-medimos").text
    sla._cache.clear()
    # V2 (30/10/2026): o quadro Formato saiu da tela; a frase do pé (X10) diz que a média fica perto do típico
    # V2 (30/10/2026): a faixa do pé saiu da tela; a variante "perto do típico" segue na frase calculada e no "Como ler"
    assert "Como não é" not in html and ", e não" not in html and "fica perto do típico" in x["insight"]
    assert "perto do típico" in html.split('class="explora-ler"')[1]
    assert c._assimetria(-1.2)["titulo"] == "Poucos casos muito rápidos puxam a conta"  # G3-8 (batalha 2)
    assert c._assimetria(0.3)["titulo"] == "Os tempos se equilibram dos dois lados" and c._assimetria(2.8)["txt"] == "+2,8"
    assert "Quase simétrica" in c._assimetria(0.3)["texto"]  # o nome técnico, só no leitor de tela
    assert "esperado" not in html.split("slide-explora")[1] and "dentro do normal" not in html  # D38


def test_conta_do_limite_fecha_d09():
    from tests.test_exploracao import _mov as base

    x = c.exploracao(base(), "2026-10")
    q3, iqr, lim = re.match(r"([\d,]+) \+ 1,5 × ([\d,]+) = ([\d,]+) h", x["box"]["conta"]).groups()
    f = lambda s: float(s.replace(",", "."))
    assert abs(f(q3) + 1.5 * f(iqr) - f(lim)) < 1e-9  # a conta escrita fecha com os termos escritos (Tukey linear)
    assert abs(f(lim) - x["box"]["limite"]) <= 0.1 and x["box"]["conta"] == "2,0 + 1,5 × 1,0 = 3,5 h"


def test_tukey_linear_e_pacotes_x4_x6():
    from tests.test_exploracao import _mov as base

    mov = base()
    mov.loc[mov["projeto_id"].isin(["X71", "X72"]), "nome_projeto"] = "[Pacote] lote"  # os dois de 80 h
    mov.attrs["versao"] = "pacotes"
    x = c.exploracao(mov, "2026-10")
    assert x["n_fora"] == 17 and x["pacotes_fora"] == 2  # limite de Tukey = 2 + 1,5 × 1 = 3,5 h: 8, 40 e 80 h fora
    assert x["box"]["contagens"][3] == 17 and x["assim"]["positiva"]
    assert 0 < x["r_normal"] < c.NORMAL_R and not x["normal"]


def test_tela_do_sla(movimentos):
    from app.main import app

    with TestClient(app) as cli:
        html = cli.get("/viu-agenciamento/sla").text
    assert "Orçamentos prontos em até 2 dias de trabalho, por mês" in html
    assert "meta sugerida: 2 dias de trabalho" in html and "acima de 2 dias" in html  # D-SLA-7 (D38); batalha 2
    assert "2 a 3 dias" not in html and "seg-clara" not in html
    assert 'class="mes-mediana"' in html and "típico 13 h" in html.replace(" ", " ")  # A3: março (3, 13, 16 h)
    assert "aguardando entregas" in html and "até 20/10" in html  # A2
    assert 'class="f-grupo f-grupo-vazia" aria-hidden="true"' in html  # R14


def test_tela_do_estudo():
    from app.main import app

    with TestClient(app) as cli:
        html = cli.get("/viu-agenciamento/sla/como-medimos").text
    assert "Cotações" in html and "Espera da marca" in html and "Espera do cliente" in html  # slide 1 (D)
    assert "só no expediente (sem noites, fins de semana e feriados)" not in html  # D38: troca pelos dias de trabalho
    assert "1,0 dia de trabalho · dentro do limite de 2 dias de trabalho (16 h)" in html and "Decisão do cliente" not in html
    assert "dias úteis" in html or "dia útil" in html or "no mesmo dia" in html  # batalha 2: C3b, a unidade da página
    # D-SLA-4: a cobertura segue calculada (ficha), mas saiu da tela a pedido do Caio (25/10/2026)
    assert "Medido em" not in html and "não têm o histórico de status completo" not in html


def test_pendencias_dizem_sla_r16():
    from app.apresentacoes.gestao_orcamentos import pendencias

    textos = str(pendencias.PENDENCIAS) + str(getattr(pendencias, "PEDIDOS", ""))
    assert "Prazo de entrega em 2025" not in textos and "meta de prazo" not in textos
    assert "SLA de entrega em 2025" in textos and "Oficializar a meta do SLA" in textos
