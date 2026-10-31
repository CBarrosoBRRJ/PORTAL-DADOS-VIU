"""D54 (26/10/2026, Caio e gerente): rótulo curto da meta numa linha e dias úteis do cliente com fração (C3c)."""
import re
from datetime import datetime as dt
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.apresentacoes.gestao_orcamentos.sla import calculos as c
from gold_simulada import dias_uteis_entre, dias_uteis_fracao as fr, horas_uteis

CSS = Path(__file__).resolve().parents[1] / "app" / "static" / "estilo.css"


@pytest.mark.parametrize("inicio, fim, esperado", [
    (dt(2026, 3, 2, 10), dt(2026, 3, 2, 15), 0.5),     # mesmo dia: 10–13 + 14–15 = 4 h de 8
    (dt(2026, 3, 2, 10), dt(2026, 3, 4, 10), 2.0),     # segunda 10h → quarta 10h
    (dt(2026, 3, 2, 10), dt(2026, 3, 4, 15), 2.5),     # segunda 10h → quarta 15h
    (dt(2026, 3, 2, 18), dt(2026, 3, 3, 11), 0.25),    # virada de dia: 1 h na segunda + 1 h na terça
    (dt(2026, 3, 6, 17), dt(2026, 3, 9, 12), 0.5),     # fim de semana: 2 h na sexta + 2 h na segunda
    (dt(2026, 4, 1, 10), dt(2026, 4, 6, 10), 2.0),     # feriado: Sexta-feira Santa (03/04) não conta
    (dt(2026, 3, 6, 20), dt(2026, 3, 9, 12), 0.25),    # fora do expediente: sexta 20h conta da segunda 10h
    (dt(2026, 3, 7, 9), dt(2026, 3, 9, 10), 0.0),      # sábado → segunda na abertura
    (dt(2026, 3, 2, 13), dt(2026, 3, 2, 14), 0.0),     # almoço não conta
    (dt(2026, 3, 2, 8), dt(2026, 3, 2, 11), 0.125),    # antes das 10h não conta
    (dt(2026, 3, 2, 15), dt(2026, 3, 2, 10), 0.0),     # nunca negativo
])
def test_dias_uteis_fracao(inicio, fim, esperado):
    assert fr(inicio, fim) == pytest.approx(esperado)


def test_fracao_coerente_com_horas_e_com_as_viradas():
    """C3c = horas do expediente ÷ 8 (todo dia útil tem 8 h) e fica perto das viradas de dia útil (C3b)."""
    pares = [(dt(2026, 3, 2, 10), dt(2026, 3, 4, 10)), (dt(2026, 2, 13, 16), dt(2026, 2, 20, 11)),  # Carnaval no meio
             (dt(2026, 3, 6, 20), dt(2026, 3, 9, 15))]
    for a, b in pares:
        assert fr(a, b) == pytest.approx(horas_uteis(a, b) / 8)
        assert abs(fr(a, b) - dias_uteis_entre(a, b)) < 1


@pytest.mark.parametrize("mediana, txt, exemplo", [
    (2.44, "2,4 dias úteis", "pedido na segunda às 10h, resposta na quarta à tarde"),   # 3,2 h → 14h12
    (2.3, "2,3 dias úteis", "pedido na segunda às 10h, resposta na quarta de manhã"),   # 2,4 h → 12h24
    (2.0, "2,0 dias úteis", "pedido na segunda às 10h, resposta na quarta de manhã"),
    (1.6, "1,6 dia útil", "pedido na segunda às 10h, resposta na terça à tarde"),
    (2.35, "2,4 dias úteis", "pedido na segunda às 10h, resposta na quarta à tarde"),   # meio para cima (C8)
    (0.02, "no mesmo dia", "pedido na segunda às 10h, resposta na própria segunda de manhã"),
    (5.2, "5,2 dias úteis", None),
])
def test_dias_uteis_cliente(mediana, txt, exemplo):
    d = c.dias_uteis_cliente(mediana)
    assert d["txt"] == txt and d["exemplo"] == exemplo and d["exato"] == mediana


def test_dias_uteis_cliente_sem_dado():
    assert c.dias_uteis_cliente(None) is None


def test_heroi_mostra_a_mediana_com_fracao(movimentos):
    from app.main import app

    with TestClient(app) as cli:
        html = cli.get("/viu-agenciamento/sla").text
    apoio = re.sub(r"\s+", " ", html.split('class="f-apoio entra"')[1].split("</p>")[0])
    num = re.search(r'<span class="secundario-numero">(\d+,\d) (dias? úte?i[ls]|dia útil)</span>', apoio)
    assert num, apoio
    assert "no calendário para o cliente receber" in apoio and "pedido na segunda às 10h, resposta na" in apoio


def test_rotulo_da_meta_curto_numa_linha(movimentos):
    from app.main import app

    with TestClient(app) as cli:
        html = cli.get("/viu-agenciamento/sla").text
    dica = 'title="meta sugerida, ainda não oficial: metade em até 2 dias de trabalho (16 h)"'
    # mesa: rótulo na linha do título do cartão, com o traço da linha; celular: o mesmo texto sobre a própria linha
    for classe, fim in (('class="meta-chave"', '<span class="legenda">'), ('class="linha-meta"', "</div>")):
        bloco = html.split(classe)[1].split(fim)[0]
        visivel = re.sub(r"<[^>]+>", "", bloco.split(">", 1)[1]).strip()
        assert visivel == "meta sugerida: 2 dias de trabalho", visivel
        assert dica in bloco and 'aria-hidden="true"' in bloco
    assert "metade dos orçamentos (50%) prontos em até 2 dias de trabalho (16 horas)" in html  # leitor de tela


def test_css_do_rotulo_numa_linha_junto_do_sla():
    css = CSS.read_text(encoding="utf-8")
    chave = re.search(r"\.meta-chave \{ position: absolute;[^}]*\}", css)
    assert chave and "white-space: nowrap" in chave.group(0)
    linha = re.search(r"\.sla-corpo \.linha-meta span \{ display: none; white-space: nowrap;[^}]*\}", css)
    assert linha and "max-width" not in linha.group(0)
    assert ".meta-horas" not in css
    # no celular o rótulo volta para a linha e a chave do título some
    assert ".sla-corpo .linha-meta span { display: block; top: auto; bottom: 100%; text-align: center; }" in css
    estudo = css.index("Estudo \"Como medimos\", 25/10/2026")
    assert css.index(chave.group(0)) < estudo and css.index(linha.group(0)) < estudo  # junto do SLA, não no fim
