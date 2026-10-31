"""D38 (25/10/2026, Caio): meta sugerida = metade em até 2 dias de trabalho (16 h); indicador acima de 5 dias; frases do
estudo pela meta (típico dentro/fora, sem outliers, limite estatístico abaixo da meta); marca da meta no boxplot."""

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from app.apresentacoes.gestao_orcamentos.sla import calculos as c
from tests.test_exploracao import _mov as base

# horas de trabalho → fim do passo Entrada a partir de uma segunda às 10:00 (expediente de 8 h, sem feriados em março)
FINS = {1: pd.Timedelta(hours=1), 8: pd.Timedelta(days=1), 16: pd.Timedelta(days=2), 24: pd.Timedelta(days=3),
        40: pd.Timedelta(days=7)}


def _mov(mix, versao):
    linhas, i = [], 0
    inicio = pd.Timestamp("2026-03-02 10:00")
    for horas, qtd in mix:
        for _ in range(qtd):
            i += 1
            pid, fim = f"Y{i}", inicio + FINS[horas]
            b = {"projeto_id": pid, "exclusivo": i % 2 == 0, "nome_projeto": pid, "sla_util_horas": None}
            linhas.append({**b, "passo": 1, "status": "Entrada", "fase": "equipe", "entrada": inicio, "saida": fim})
            linhas.append({**b, "passo": 2, "status": "Aguardando Feedback", "fase": "cliente", "entrada": fim, "saida": pd.NaT})
    df = pd.DataFrame(linhas)
    df.attrs["versao"] = versao
    df["_processado_em"] = pd.Timestamp("2026-10-21 21:16:22", tz="UTC")
    return df


def test_meta_tipico_pelo_valor_exato():
    assert c.META == 0.50 and c.META_H == 16
    assert c.meta_tipico(14.26) == {"na_meta": True, "mediana_txt": "14 h", "acima_txt": None}
    assert c.meta_tipico(16.0)["na_meta"]  # 16 h conta (limite inclusivo)
    # abr–jun/2026 tiveram 16,3–16,5 h: a tela arredonda para "16 h", mas não estão dentro da meta
    assert c.meta_tipico(16.3) == {"na_meta": False, "mediana_txt": "16,3 h", "acima_txt": "0,3 h"}
    assert c.meta_tipico(16.01)["mediana_txt"] == "16,1 h"
    assert c.meta_tipico(19.64) == {"na_meta": False, "mediana_txt": "20 h", "acima_txt": "4 h"}
    assert c.meta_tipico(None) is None


def test_faixas_tres_chaves_e_acima_de_5_dias():
    e = c.entrega(_mov([(1, 40), (8, 10), (16, 10), (24, 15), (40, 3), (40, 0)], "d38-a"), "2026-10")
    assert set(e["ano"]["tela"]) == {"ate1", "de1a2", "acima2", "ate2"}
    assert e["ano"]["tela"] == {"ate1": 64, "de1a2": 13, "acima2": 23, "ate2": 77}  # 50, 10 e 18 de 78
    assert e["acima5"] == 0 and e["n_acima5"] == 0  # 40 h não passa de 5 dias (> 40 h)
    x = c.entrega(base(), "2026-10")  # 2 de 72 com 80 h
    assert x["acima5"] == 3 and x["n_acima5"] == 2 and x["tipico"]["na_meta"]


H = pd.Series([4.0] * 10 + [10.0] * 10 + [14.0] * 10 + [20.0] * 10 + [30.0] * 10 + [100.0] * 2)  # limite 20 + 15 = 35 h


def _p3(h, n_pac=0):
    bx = c._boxplot(h)
    return c._frases(h, bx, bx["contagens"][3], n_pac)


def test_insight_do_passo_3_final():
    bx = c._boxplot(H)  # zonas 39/38/19/4; Q3 20 h; limite 35 h
    f = _p3(H)
    assert f["pct_horas_outliers"] == 20 and f["pct_meta"] == 58  # horas só no cálculo
    assert f["fora_rodape"] == ("<strong>77% dos orçamentos saem em até 20 h</strong>: os rápidos e os comuns. Outros 19% "
                                "demoram mais, até 35 h, mas seguem o padrão do processo. <em>4% (2 orçamentos) estão fora da "
                                "curva, acima de 35 h: vamos olhar caso a caso.</em>")  # G3-8
    assert f["nota"] == ("Chamamos de padrão os tempos até 35 h: é até onde vai a grande maioria dos orçamentos, com uma "
                         "margem de folga. Acima disso, o tempo foge do ritmo da equipe.")
    tecnicos = ("metade do meio", "caixa", "haste", "quartil", "largura", "mediana", "desvio", "Tukey", "percentil")
    assert not any(t in f["nota"] + f["fora_rodape"] for t in tecnicos)
    assert "meta" not in f["fora_rodape"] and "horas da equipe" not in f["fora_rodape"]
    assert "4% (2 orçamentos, 1 deles pacote) estão fora da curva" in _p3(H, 1)["fora_rodape"]
    assert "4% (2 orçamentos, 2 deles pacotes) estão fora da curva" in _p3(H, 2)["fora_rodape"]
    assert "outlier" not in _p3(H, 2)["fora_rodape"]
    h2 = pd.Series([10.0] * 15 + [20.0] * 20 + [30.0] * 15 + [200.0])
    assert "(1 orçamento, um pacote) está fora da curva" in _p3(h2, 1)["fora_rodape"]
    assert "<em>menos de 1% (1 orçamento) está fora da curva" in _p3(pd.Series([4.0, 8.0, 12.0, 20.0] * 75 + [400.0]))["fora_rodape"]
    f3 = _p3(pd.Series([4.0, 8.0, 12.0, 14.0, 20.0] * 10))["fora_rodape"]
    assert f3.endswith("mas seguem o padrão do processo; <em>neste recorte, ninguém fica fora da curva.</em>")
    x = c.exploracao(base(), "2026-10")  # sem demorados: a frase do meio some
    assert x["insights"]["3"] == ("<strong>76% dos orçamentos saem em até 2 h</strong>: os rápidos e os comuns. <em>24% "
                                  "(17 orçamentos) estão fora da curva, acima de 4 h: vamos olhar caso a caso.</em>")
    assert x["pct_horas_outliers"] == 86


def test_insight_do_passo_1_quanto_leva():
    assert c._insight_p1(14.26, 25.3, 56, True) == (
        "<strong>56% dos orçamentos ficam prontos em até 2 dias de trabalho</strong>, e o típico leva 14 h: dentro da "
        "meta. A média, 25 h, parece pior porque poucos casos muito longos a puxam para cima; <em>por isso olhamos o "
        "típico</em>.")
    assert c._insight_p1(19.64, 30.2, 41, True) == (
        "Neste grupo, <strong>o típico leva 20 h, 4 h acima da meta de 2 dias</strong>; só 41% ficam prontos no prazo. "
        "A média, 30 h, ainda é puxada para cima por poucos casos muito longos; <em>por isso olhamos o típico</em>.")
    assert "o típico leva 16,3 h, 0,3 h acima" in c._insight_p1(16.3, 16.9, 49, False)
    assert c._insight_p1(10, 10.5, 70, False).endswith("A média, 11 h, fica perto dele: <em>aqui a média e o típico contam a mesma história</em>.")


def test_insight_do_passo_2_ritmo_regular():
    from statistics import NormalDist

    h = pd.Series([float(v) for v in range(1, 101)])  # 10% mais lentos a partir de 90,1 h
    assert c._insight_p2(h, NormalDist(50, 10), False)["texto"] == (
        "Até 2 dias, os orçamentos andam junto da reta, no ritmo previsto. <strong>Depois disso, os demorados se afastam "
        "dela</strong>, e quanto mais demoram, mais longe ficam. <em>Por isso a meta se apoia no típico, e os demorados "
        "são tratados à parte.</em>")
    sino = ("Os tempos seguem um ritmo regular, sem casos que fujam muito do padrão; <em>a média e o típico contam a "
            "mesma história</em>.")
    assert c._insight_p2(h, NormalDist(50, 10), True)["texto"] == sino  # quase sino
    assert c._insight_p2(h, NormalDist(80, 30), False)["texto"] == sino  # real não passa do sino
    termos = ("mediana", "desvio", "Tukey", "percentil", "assimetria", "de cada 100", "em 100", "esperado")
    for t in (_p3(H)["fora_rodape"], c._insight_p1(14, 25, 56, True), c._insight_p1(20, 30, 41, True),
              c._insight_p2(h, NormalDist(50, 10), False)["texto"], sino):
        assert not any(w in t for w in termos), t


def test_marca_da_meta_no_boxplot_dentro_do_quadro():
    cx = c._caixa(H, c._boxplot(H))
    m = cx["meta"]
    assert m and cx["x_q1"] < m["x"] < cx["x_q3"] and 0 < m["x"] < cx["w"] and cx["h"] == 80
    assert m["y_cima"][1] <= 35 and m["y_baixo"][0] >= 61  # fora da caixa (35–61): não passa sobre ela nem sobre o texto
    assert m["y_cima"][0] > 22 and m["y_baixo"][1] < 70  # abaixo dos números de cima (base 20) e acima dos valores (76)
    assert "t" not in m  # sem rótulo no desenho (D38): <title> e nota abaixo
    assert c._caixa(base_h := pd.Series([1.0] * 40 + [2.0] * 15 + [8.0] * 10), c._boxplot(base_h))["meta"] is None
    assert c.exploracao(base(), "2026-10")["caixa"]["meta"] is None  # limite 3,5 h < 16 h: sem marca


def test_dias_de_trabalho_do_exemplo():
    assert c._dias_trabalho(8) == "1,0 dia de trabalho" and c._dias_trabalho(13) == "1,6 dia de trabalho"
    assert c._dias_trabalho(16) == "2,0 dias de trabalho"


@pytest.mark.parametrize("mix, gancho, faixa", [
    (None, "No ano, o orçamento típico leva 1 h: dentro da meta de 2 dias. Vamos ver o que demora.", "e o típico leva 1 h: dentro da meta. A média, 7 h, parece pior"),
    ([(8, 5), (16, 5), (24, 20), (40, 10)], "No ano, o orçamento típico leva 24 h, acima da meta de 2 dias. Vamos ver onde demora.",
     "Neste grupo, <strong>o típico leva 24 h, 8 h acima da meta de 2 dias</strong>"),
])
def test_gancho_e_faixa_do_passo_1_condicionais(monkeypatch, mix, gancho, faixa):
    from app import dados, sla
    from app.main import app

    mov = base() if mix is None else _mov(mix, "d38-gancho")
    if mix is None:
        mov["_processado_em"] = pd.Timestamp("2026-10-21 21:16:22", tz="UTC")
    monkeypatch.setattr(dados.sla, "df", lambda forcar=False: mov)
    sla._cache.clear()
    with TestClient(app) as cli:
        html = cli.get("/viu-agenciamento/sla/como-medimos").text
        pag = cli.get("/viu-agenciamento/sla").text
    sla._cache.clear()
    assert gancho in html
    # V2 (30/10/2026): o slide 2 tem um passo só; a faixa do antigo passo 1 segue calculada (fora da tela)
    assert faixa in c.exploracao(mov, "2026-10")["insights"]["1"] and faixa not in html
    ler_ = html.split('class="explora-ler"')[1].split("</section>")[0]  # "Como ler": sem termos técnicos
    assert "metade dos pedidos sai antes disso" in ler_
    assert not any(t in ler_ for t in ("caixa", "haste", "quartil", "boxplot", "outlier"))
    assert "meta sugerida: 2 dias de trabalho" in pag
    if mix is None:
        assert "O típico já sai em até 2 dias" in pag and "passam de 5 dias" not in pag  # batalha 2: só o corte do gráfico
    else:
        assert "O típico ainda passa de 2 dias (24\u00a0h)" in pag and "passam de 5 dias" not in pag


def test_numeros_das_faixas_e_parcial_cabem_na_barra(movimentos):
    """D38 (Caio): números das faixas em tamanho único que encolhem pela altura real da faixa (container query) até 8 px
    e somem abaixo disso, com o valor no leitor de tela e no title; "PARCIAL" encolhe até 7 px, vira "parc." e, se nem
    assim couber, sai para cima da barra. Sem style="" (CSP): só classes e o bloco <style> com nonce."""
    import pathlib
    import re

    from app.main import app

    with TestClient(app) as cli:
        html = cli.get("/viu-agenciamento/sla").text
    assert '<span class="seg-num">' in html  # outubro sintético tem < 30 entregas (sem barra vazada): o PARCIAL vai no template
    tpl = pathlib.Path("app/apresentacoes/gestao_orcamentos/sla/template.html").read_text(encoding="utf-8")
    assert '<span class="vz-longo">parcial</span><span class="vz-curto">parc.</span>' in tpl
    assert 'title="mar: 100% prontos em até 2 dias (33% até 1 dia, 67% de 1 a 2 dias), de 3 orçamentos"' in html
    corpo = html.split('id="grafico-entrega"')[1].split("</figure>")[0]
    assert 'style="' not in corpo
    css = pathlib.Path("app/static/estilo.css").read_text(encoding="utf-8")
    assert ".sla-corpo .seg { container-type: size;" in css and ".sla-corpo .pilha-vazada { container-type: size; }" in css
    assert re.search(r"seg-num \{ font-size: clamp\(8px, min\(100cqh / [\d.]+, 100cqw / [\d.]+\), 1em\)", css)
    assert "@container (height < 11px) or (width < 20px) { .sla-corpo .seg-num { display: none; } }" in css
    assert re.search(r"vazada-txt \{ font-size: clamp\(7px, 100cqh / [\d.]+, 0\.72em\)", css)


def test_qq_conta_orcamentos_reais_acima_do_teto():
    """D38 (Caio): o "↑ N" do Q-Q contava quantis (sempre ~6 de 200); agora são orçamentos reais acima do teto do
    gráfico, e muda com o tamanho do grupo."""
    mov = _mov([(1, 60), (8, 30), (16, 20), (24, 20), (40, 10)], "d38-qq")
    vistos = set()
    for g in ("todos", "exclusivos", "nao-exclusivos"):
        x = c.exploracao(mov, "2026-10", g)
        h = c._universo(mov, "2026-10", g)
        q = x["qq"]
        assert q["n_presos"] == int((h > q["teto"]).sum())
        vistos.add((len(h), q["n_presos"]))
    real = c.exploracao(base(), "2026-10")["qq"]
    assert real["n_presos"] == int((c._universo(base(), "2026-10", "todos") > real["teto"]).sum())
    assert len({n for n, _ in vistos}) >= 2  # grupos de tamanhos diferentes


def test_numeros_das_faixas_estao_no_grafico_do_passo():
    """D38 (Caio): todo número da faixa do pé aparece no gráfico do passo ao lado (nos três grupos de uma base)."""
    import re

    mov = _mov([(1, 60), (8, 30), (16, 20), (24, 20), (40, 10)], "d38-visiveis")
    for g in ("todos", "exclusivos", "nao-exclusivos"):
        x = c.exploracao(mov, "2026-10", g)
        bx = x["box"]
        p3 = re.findall(r"(\d+)%", x["insights"]["3"])
        assert set(p3) <= {str(bx["pcts"][0] + bx["pcts"][1]), str(bx["pcts"][2]), str(bx["pcts"][3])}  # como no gráfico
        for v in (bx["q3_txt"], bx["lim_txt"]):  # Q3 e limite como escritos no boxplot
            assert v in x["insights"]["3"] + x["frases"]["nota"]
        assert x["faixas3"]["pcts"][0] == int(re.findall(r"(\d+)%", x["insights"]["1"])[0])  # passo 1: faixa do topo
        if "Depois disso, os demorados" in x["insights"]["2"]:  # os cortes citados estão marcados na reta
            assert x["qq"]["p90"] is None and [r["v"] for r in x["qq"]["rotulos"]][:1] == ["2 dias"]
