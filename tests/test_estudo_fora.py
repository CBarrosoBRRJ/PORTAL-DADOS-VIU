"""Caio, 03/11/2026: a lupa do "Fora da curva" (estudo, slide 2) abre a lista dos pedidos acima do limite de Tukey, com
nome, marca e talento, entrada, 1ª entrega, horas de trabalho e o link do item no monday (sla/calculos.fora_da_curva)."""

import re
from itertools import pairwise
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.apresentacoes.gestao_orcamentos.sla import calculos as c
from tests.test_exploracao import _mov


@pytest.fixture
def cliente():
    from app.main import app

    with TestClient(app) as cl:
        yield cl


def test_lista_dos_fora_da_curva_bate_com_a_contagem_e_vem_do_mais_longo():
    mov = _mov()
    mov["link_projeto"] = [f"https://globocorp.monday.com/boards/1/pulses/{p[1:]}" for p in mov["projeto_id"]]
    mov["marca"], mov["talento"] = "Marca", "Talento"
    x = c.exploracao(mov, "2026-10", "todos")
    lista = x["fora_lista"]
    assert len(lista) == x["n_fora"] > 0
    horas = [p["horas"] for p in lista]
    assert horas == sorted(horas, reverse=True)
    limite = c._boxplot(c._universo(mov, "2026-10", "todos"))["limite"]
    assert all(p["horas"] > limite for p in lista)
    p = lista[0]
    assert p["nome"].startswith("X") and p["marca"] == "Marca" and p["talento"] == "Talento"
    assert re.fullmatch(r"\d\d/\d\d · \d\d:\d\d", p["entrada"]) and re.fullmatch(r"\d\d/\d\d · \d\d:\d\d", p["entrega"])
    assert p["entrada"] == "02/03 · 10:00" and p["link"].startswith("https://globocorp.monday.com/boards/1/pulses/")


def test_link_que_nao_e_do_monday_nao_entra():
    mov = _mov()
    mov["link_projeto"] = "javascript:alert(1)"
    lista = c.exploracao(mov, "2026-10", "todos")["fora_lista"]
    assert lista and all(p["link"] == "" for p in lista)


def test_lupa_e_popup_no_slide_2(cliente):
    html = cliente.get("/viu-agenciamento/sla/como-medimos").text
    if 'data-ef-abrir' not in html:  # base sintética sem nenhum pedido fora da curva: sem lupa e sem pop-up
        assert '<dialog id="estudo-fora"' not in html
        return
    n = int(re.search(r'Ver os (\d+) pedidos', html).group(1))
    assert '<dialog id="estudo-fora" class="ef-dlg" aria-labelledby="ef-titulo">' in html
    corpo = html[html.index('<dialog id="estudo-fora"'):html.index("</dialog>", html.index('<dialog id="estudo-fora"'))]
    assert corpo.count('<th scope="row">') == n and "data-ef-fechar" in corpo
    assert 'style="' not in html
    js = (Path(__file__).resolve().parents[1] / "app" / "static" / "apresentacao.js").read_text(encoding="utf-8")
    assert 'getElementById("estudo-fora")' in js
    for a in re.findall(r'<a class="ef-link" [^>]*>', corpo):
        assert 'target="_blank" rel="noopener"' in a


def _exploracao_com_horas(monkeypatch, horas: list[float]):
    """Exploração da base sintética (72 pedidos) com o tempo da equipe trocado pelos valores dados, um por pedido."""
    mov = _mov()
    u = c._universo_df(mov, "2026-10", "todos").copy()
    assert len(u) == len(horas)
    u["h_trabalho"] = horas
    monkeypatch.setattr(c, "_universo_df", lambda *_a, **_k: u)
    return c.exploracao(mov, "2026-10", "todos")


def _horas(q3: float) -> list[float]:
    """Q1 = 1,875 h e Q3 = q3 → limite = 2,5 × q3 − 2,8125; 3 pedidos fora da curva (100, 120 e 300 h)."""
    return [float(k % 20) / 10 + 1 for k in range(30)] + [q3] * 39 + [100.0, 120.0, 300.0]


def _confere_hist(x):
    """X2 (Caio, 03/11/2026): faixas de 4 h até o limite de Tukey, a penúltima podendo ser mais estreita, e uma última
    barra "acima de <limite>" toda vermelha com n == n_fora; nenhuma barra de duas cores."""
    bs, lim = x["hist"]["barras"], x["box"]["limite"]
    assert [b["zona_box"] for b in bs].count("box-fora") == 1 and bs[-1]["zona_box"] == "box-fora"
    assert bs[-1]["n"] == x["n_fora"] and bs[-1]["rotulo"] == f"acima de {x['box']['lim_txt']}"
    assert sum(b["n"] for b in bs) == x["n"]
    assert all("fora" not in b for b in bs)  # sem a parte vermelha por cima
    bordas = [tuple(float(v.replace(",", ".")) for v in b["rotulo"].removesuffix(" h").split(" a ")) for b in bs[:-1]]
    assert bordas[0][0] == 0 and all(a[1] == b[0] for a, b in pairwise(bordas))
    assert all(hi - lo == 4 for lo, hi in bordas[:-1]) and abs(bordas[-1][1] - round(lim, 1)) < 1e-9
    assert all(b0["x"] + b0["w"] < b1["x"] for b0, b1 in pairwise(bs))  # sem barra sobre a outra
    zf = next(z for z in x["hist"]["zonas"] if z["zona"] == "box-fora")  # faixa do topo alinhada com a última barra
    assert abs(zf["x0"] - (bs[-1]["x"] - 0.5)) < 0.2 and x["hist"]["marcas_x"][-1]["t"] == bs[-1]["rotulo"]
    assert not any("ou mais" in m["t"] for m in x["hist"]["marcas_x"])
    return bordas


def test_vermelho_do_histograma_e_so_a_ultima_barra():
    """Caio, 03/11/2026: a última barra é a única vermelha e tem o número do cartão "Fora da curva"."""
    mov = _mov()
    for g in ("todos", "exclusivos", "nao-exclusivos"):
        x = c.exploracao(mov, "2026-10", g)
        if x is not None:
            _confere_hist(x)


def test_limite_fora_do_multiplo_de_4_ganha_faixa_estreita(monkeypatch):
    x = _exploracao_com_horas(monkeypatch, _horas(23.36))  # limite 55,59 h: resto 3,6 h, faixa própria "52 a 55,6 h"
    assert abs(x["box"]["limite"] - 55.5875) < 1e-9 and x["box"]["lim_txt"] == "55,6 h"
    bordas = _confere_hist(x)
    assert bordas[-1] == (52.0, 55.6) and len(bordas) == 14
    bs = x["hist"]["barras"]
    assert bs[-2]["w"] < bs[-3]["w"] and bs[-2]["rotulo"] == "52 a 55,6 h"  # mais estreita
    assert bs[-1]["n"] == 3 == x["n_fora"] and bs[-1]["rotulo"] == "acima de 55,6 h"


def test_resto_pequeno_entra_na_faixa_anterior(monkeypatch):
    x = _exploracao_com_horas(monkeypatch, _horas(23.76))  # limite 56,59 h: resto 0,6 h < 1 h
    bordas = _confere_hist(x)
    assert bordas[-1] == (52.0, 56.6) and len(bordas) == 14  # "52 a 56,6 h", sem o fio "56 a 56,6 h"
    bs = x["hist"]["barras"]
    assert bs[-2]["w"] > bs[-3]["w"] and bs[-1]["n"] == 3


def test_limite_com_uma_casa():
    """Caio, 03/11/2026: 69,7 h não vira "70 h" (um pedido de 69,9 h estaria na lista); inteiro fica sem ",0"."""
    assert c._h_lim(69.73) == "69,7 h" and c._h_lim(59.24) == "59,2 h" and c._h_lim(50.42) == "50,4 h"
    assert c._h_lim(35.0) == "35 h" and c._h_lim(3.5) == "3,5 h" and c._h_lim(59.96) == "60 h"


def test_histograma_na_tela_sem_barra_de_duas_cores(cliente):
    """Caio, 03/11/2026: no slide 2, um retângulo por barra, só o último vermelho, e o eixo termina em "acima de …"."""
    html = cliente.get("/viu-agenciamento/sla/como-medimos").text
    if 'class="ex-barras"' not in html:  # base sintética curta demais para o estudo
        return
    g = html.split('class="ex-barras">')[1].split("</g>")[0]
    rects = re.findall(r'<rect class="ex-barra [^"]*"', g)
    assert rects and sum("box-fora" in r for r in rects) == 1 and "box-fora" in rects[-1]
    assert "60 h ou mais" not in html and "ou mais</text>" not in html
    assert re.search(r'>acima de [\d,]+ h</text>', html)
