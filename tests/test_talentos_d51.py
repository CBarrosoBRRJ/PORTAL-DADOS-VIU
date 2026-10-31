"""Talentos D51 (26/10/2026, Caio; revista no mesmo dia): exceção à D46/D49 (números prontos desde o 1º quadro) só
nesta página.

Abertura (e troca de filtro): a barra do ano cresce e os números contam até o valor, com o top 10 PARADO (nenhuma troca
de posição). Botão play opcional, só ícone (▶ ↔ ■ "Parar"), na linha da legenda da barra (revisto 26/10): a "corrida
do ano", calma (mês a mês com respiro, histerese nas trocas, numeração fixa), com quem entra e sai dos 10 pelo acumulado (T12: os 10 do ano + quem esteve entre os 10 do acumulado no fim de algum mês). T11:
coluna dos nomes com a largura do maior nome, sem reticências.

O que se confere: o HTML do servidor continua sendo o estado final; os dados da corrida fecham com a tabela (soma
mensal = Ano; quem termina no top 10 = tabela final; os de fora têm lugar no ano > 10); o botão é nativo, com nome, e
começa escondido (sem JS); o JS respeita o movimento reduzido, roda tudo numa cópia aria-hidden, usa só
transform/opacidade/texto por quadro e tem os tempos num lugar só.
"""

import json
import re
from datetime import date
from html import unescape
from pathlib import Path

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from app.apresentacoes.gestao_orcamentos.talentos import calculos as tal

RAIZ = Path(__file__).resolve().parent.parent
CSS = (RAIZ / "app" / "static" / "estilo.css").read_text(encoding="utf-8")
JS = (RAIZ / "app" / "static" / "apresentacao.js").read_text(encoding="utf-8")
BLOCO_JS = JS[JS.index("// ---------- D51"):JS.index("// ---------- fim D51")]
BLOCO_CSS = CSS[CSS.index("/* ---------- D51"):CSS.index("/* ---------- fim D51")]


@pytest.fixture
def cliente():
    from app.main import app

    with TestClient(app) as c:
        yield c


def _tabela(html: str) -> str:
    return re.search(r'<table class="mapa-tabela[ "].*?</table>', html, re.S).group(0)


def _num(txt: str) -> int:
    return int(txt.replace(".", ""))


# ---------- HTML: estado final e dados da corrida ----------

@pytest.mark.parametrize("filtro", ["todos", "exclusivos", "nao-exclusivos"])
def test_dados_da_corrida_fecham_com_a_tabela_final(cliente, filtro):
    tabela = _tabela(cliente.get(f"/viu-agenciamento/talentos?talentos={filtro}").text)
    meses = int(re.search(r'data-corrida-meses="(\d+)"', tabela).group(1))
    cabecalho = re.search(r"<thead>.*?</thead>", tabela, re.S).group(0)
    assert meses == cabecalho.count('class="mapa-mes') - cabecalho.count("mapa-futuro")
    assert int(re.search(r'data-corrida-maior="(\d+)"', tabela).group(1)) > 0
    json.loads(unescape(re.search(r"data-corrida-extras='([^']*)'", tabela).group(1)))  # JSON válido no atributo
    linhas = re.findall(r'<tr data-corrida-pedidos="([\d,]*)">(.*?)</tr>', tabela, re.S)
    assert len(linhas) == tabela.count('<th scope="row"') > 0
    totais = []
    for pedidos, corpo in linhas:
        valores = [int(v) for v in pedidos.split(",")]
        assert len(valores) == meses
        celulas = [_num(n) for n in re.findall(r'<span class="hm-num">([\d.]+)</span>', corpo)]
        assert celulas == valores  # os mesmos números das células, na ordem jan…
        total = _num(re.search(r'class="mapa-total">([\d.]+)<', corpo).group(1))
        assert sum(valores) == total  # soma mensal = coluna Ano
        totais.append(total)
    assert totais == sorted(totais, reverse=True)  # estado final = ranking do ano


def test_estado_final_intacto_sem_style_e_com_tons(cliente):
    tabela = _tabela(cliente.get("/viu-agenciamento/talentos").text)
    assert "style=" not in tabela  # CSP: nada de style=""; o JS escreve só via element.style (CSSOM)
    assert re.search(r'<td class="hm hm-c0 hm-n\d', tabela)
    assert 'class="mapa-total">3<' in tabela


NOME_PLAY = "Ver a subida e descida das posições ao longo do ano"


def test_botao_play_so_icone_com_nome_escondido_sem_js_e_sem_pular(cliente):
    html = cliente.get("/viu-agenciamento/talentos").text
    botao = re.search(r"<button[^>]*data-corrida-play[^>]*>(.*?)</button>", html, re.S)
    assert botao
    tag, dentro = botao.group(0), botao.group(1)
    assert 'type="button"' in tag and " hidden" in tag  # sem JS não aparece
    assert f'aria-label="{NOME_PLAY}"' in tag and f'title="{NOME_PLAY}"' in tag  # nome acessível = dica
    assert 'aria-describedby="corrida-ajuda"' in tag and 'id="corrida-ajuda"' in html
    assert dentro == '<span class="corrida-icone" aria-hidden="true">▶</span>'  # nenhum texto visível além do ícone
    assert "corrida-texto" not in html and "corrida-controles" not in html
    assert "Pular" not in html and "data-corrida-pular" not in html  # na abertura não há o que pular


def test_botao_fora_do_cartao_na_linha_da_legenda(cliente):
    html = cliente.get("/viu-agenciamento/talentos").text
    linha = re.search(r'<div class="talentos-legenda-linha">(.*?)</div>', html, re.S).group(1)
    assert 'class="talentos-lista talentos-legenda" aria-hidden="true"' in linha  # legenda decorativa…
    assert "data-corrida-play" in linha.split("</ul>", 1)[1]  # …e o botão depois dela, fora do aria-hidden
    cartao = re.search(r'<figure class="talentos-mapa">.*?</figure>', html, re.S).group(0)
    assert "data-corrida-play" not in cartao and '<span class="corrida-rotulo" aria-hidden="true">' in cartao
    assert html.index("data-corrida-play") < html.index('<table class="mapa-tabela')  # ordem do Tab: botão antes da tabela
    regra = re.search(r"\.corrida-play \{([^}]*)\}", BLOCO_CSS).group(1)
    assert "border-radius: 50%" in regra and "margin-left: auto" in regra and "min-width: 24px" in regra
    assert ".corrida-play:focus-visible { outline: 2px solid var(--azul)" in BLOCO_CSS


# ---------- T12: quem entra e sai dos 10 ----------

def _df_corrida():
    """11 talentos exclusivos: o 11º no ano (Kátia) lidera o acumulado de janeiro e depois some."""
    linhas = []
    for i in range(10):
        meses = {1: 1, 2: 20 - i}
        for m, n_mes in meses.items():
            linhas.append({"grupo": "exclusivo", "talento": f"T{i:02d}", "n": sum(meses.values()), "pos": i + 1, "mes": date(2026, m, 1),
                           "n_mes": n_mes, "ultimo_pedido": pd.Timestamp(2026, m, 5), "empate_fora": 0, "talentos_grupo": 11})
    linhas.append({"grupo": "exclusivo", "talento": "Kátia", "n": 5, "pos": 11, "mes": date(2026, 1, 1), "n_mes": 5,
                   "ultimo_pedido": pd.Timestamp(2026, 1, 9), "empate_fora": 0, "talentos_grupo": 11})
    return pd.DataFrame(linhas)


def _divisao():
    df = pd.DataFrame({"ano": [2026] * 3, "categoria": ["Exclusivos", "Não exclusivos", "Sem talento"],
                       "n": [300, 100, 10], "dos_quais_squad": [0, 0, 0]})
    return tal.divisao(df, 410, 2026)


def test_extras_fora_do_top_entram_so_na_corrida():
    tg = tal.top_por_grupo(_df_corrida(), _divisao())["exclusivo"]
    assert [r["talento"] for r in tg["linhas"]] == [f"T{i:02d}" for i in range(10)]  # a tabela do ano não muda
    assert tg["n"] == sum(21 - i for i in range(10))
    assert [c["talento"] for c in tg["corrida"]] == ["Kátia"] and tg["corrida"][0]["pos"] == 11
    m = tal.mapa(tg, date(2026, 3, 10))
    assert m["extras"] == [{"t": "Kátia", "pos": 11, "p": [5, 0, 0]}]  # pedidos de jan até o mês do corte
    assert all(sum(x["p"]) == 5 for x in m["extras"])  # soma mensal = total do talento
    # ranking acumulado no fim de janeiro: Kátia (5) à frente de todos (1 cada); no fim do ano, fora dos 10
    jan = sorted([(r["meses"].get(1, 0), -r["posicao"], r["talento"]) for r in tg["linhas"]] + [(5, -11, "Kátia")], reverse=True)
    assert jan[0][2] == "Kátia"
    assert all(x["pos"] > len(m["linhas"]) for x in m["extras"])  # quem termina no top 10 = tabela final


def test_extra_que_nao_fecha_a_soma_fica_fora_da_corrida():
    df = _df_corrida()
    df.loc[df["talento"] == "Kátia", "n"] = 6
    m = tal.mapa(tal.top_por_grupo(df, _divisao())["exclusivo"], date(2026, 3, 10))
    assert m is not None and m["extras"] == []  # a tabela continua; a corrida mostra só os 10


def test_sem_coluna_pos_a_corrida_fica_so_com_os_10():
    tg = tal.top_por_grupo(_df_corrida().drop(columns=["pos"]), _divisao())["exclusivo"]
    assert tg["corrida"] == [] and len(tg["linhas"]) == 10


def test_ranking_lido_da_gold_com_a_posicao_no_ano():
    """D57: o ranking (top 10 e quem passou pelos 10 do acumulado, coluna pos) vem pronto da gold
    gld_agenciamento_2026_talentos_ranking; a regra e a conferência dela ficam no projeto da gold."""
    from app import dados

    assert dados.talentos_top.id_tabela.endswith(".gld_agenciamento_2026_talentos_ranking")
    assert {"pos", "n_mes", "mes", "talentos_grupo", "empate_fora"} <= set(dados.talentos_top.colunas)


# ---------- T11: nomes sem reticências ----------

def test_largura_dos_nomes_segue_o_maior_nome():
    assert tal.largura_nomes(["Ana", "Jonas Fernando Sulzbach"]) == 23
    assert tal.largura_nomes(["Sol Vega"]) == tal.NOME_MIN
    assert tal.largura_nomes(["x" * 50]) == tal.NOME_MAX
    assert tal.largura_nomes([]) == tal.NOME_MIN
    for n in range(tal.NOME_MIN, tal.NOME_MAX + 1):
        assert f".mapa-nomes-{n} {{ --nome-ch: {n}; }}" in CSS


def test_classe_de_largura_coerente_no_html(cliente):
    html = cliente.get("/viu-agenciamento/talentos").text
    nomes = re.findall(r'class="mapa-talento" title="([^"]*)"', html)
    n = int(re.search(r'class="mapa-tabela mapa-nomes-(\d+)"', html).group(1))
    assert n == tal.largura_nomes(nomes)


def test_coluna_dos_nomes_sem_reticencias():
    regra = re.search(r"\.mapa-nome \{([^}]*)\}", CSS).group(1)
    assert "ellipsis" not in regra and "nowrap" not in regra and "overflow: hidden" not in regra
    assert not re.search(r"\.mapa-(nome|talento)[^{]*\{[^}]*text-overflow", CSS)
    assert "width: calc((var(--nome-ch, 21) * 0.555em + 1.78em) / 0.92)" in CSS


# ---------- JS e CSS ----------

def test_abertura_sem_troca_de_posicao_e_corrida_so_no_play():
    abertura = BLOCO_JS[BLOCO_JS.index("function abertura"):BLOCO_JS.index("function corrida")]
    assert "translateY" not in abertura and "sort(" not in abertura  # top 10 parado na abertura
    assert "    if (podeMover) abertura();\n  })();" in BLOCO_JS
    assert BLOCO_JS.count("corrida();") == 1 and "if (!rodando) corrida();" in BLOCO_JS  # só no clique do play
    assert '"Parar" : NOME_PLAY' in BLOCO_JS and '"■" : "▶"' in BLOCO_JS and f'var NOME_PLAY = "{NOME_PLAY}"' in BLOCO_JS
    assert "play.title = nome" in BLOCO_JS  # a dica acompanha o nome (▶ / Parar)


def test_js_respeita_movimento_reduzido_e_acessibilidade():
    antes = BLOCO_JS[:BLOCO_JS.index("var TEMPOS")]
    assert "if (!podeMover && !Element.prototype.animate) return;" in antes and "play.disabled = true" in antes
    assert "if (podeMover) abertura();" in BLOCO_JS  # reduzido: controles prontos, sem abertura automática
    assert 'setAttribute("aria-hidden", "true")' in BLOCO_JS and "p.inert = true" in BLOCO_JS  # cópia decorativa
    assert 'tabela.classList.add("corrida-escondida")' in BLOCO_JS  # a original só fica transparente
    assert ".mapa-tabela.corrida-escondida { opacity: 0; }" in BLOCO_CSS  # opacidade: o leitor de tela continua lendo
    assert "aria-live" not in BLOCO_JS and ".focus(" not in BLOCO_JS  # nada é anunciado, foco não é movido
    assert 'setAttribute("style"' not in BLOCO_JS
    for ev in ('"pointerdown"', '"wheel"', '"touchstart"', '"keydown"', '"beforeprint"', '"visibilitychange"', '"scroll"'):
        assert ev in BLOCO_JS, ev


def test_js_continuo_tempos_num_lugar_e_sem_layout_por_quadro():
    tempos = dict((k, int(v)) for k, v in re.findall(r"(\w+): (\d+)", re.search(r"var TEMPOS = \{([^}]*)\}", BLOCO_JS).group(1)))
    assert tempos["barra"] <= 700 and tempos["numeros"] <= 1000
    assert 9000 <= 10 * (tempos["mes"] + tempos["respiro"]) <= 12000  # corrida de 10 meses entre 9 e 12 s (pedido do Caio)
    assert tempos["respiro"] > 0 and tempos["histerese"] > 0 and tempos["deslize"] > 0
    assert BLOCO_JS.count("var TEMPOS") == 1
    assert "suave(u)" in BLOCO_JS and "TEMPOS.mes + TEMPOS.respiro" in BLOCO_JS  # mês com easing + respiro
    assert "espera >= TEMPOS.histerese" in BLOCO_JS and "MARGEM_REL" in BLOCO_JS  # histerese nas trocas
    assert 'className = "corrida-num"' in BLOCO_JS and ".corrida-numerada tbody .mapa-pos { visibility: hidden; }" in BLOCO_CSS  # 1–10 fixos
    quadro = BLOCO_JS[BLOCO_JS.index("quadro: function (tc, dt)"):BLOCO_JS.index('tipo: "corrida"')]
    assert "getBoundingClientRect" not in quadro and "offsetTop" not in quadro and "offsetHeight" not in quadro
    assert set(re.findall(r"style\.(\w+) =", quadro)) <= {"transform", "opacity"}


def test_css_d51_sem_loop_e_impressao_limpa():
    assert "infinite" not in BLOCO_CSS and "alternate" not in BLOCO_CSS
    assert "@media print { .corrida-play, .corrida-rotulo { display: none; } }" in BLOCO_CSS
    assert ".corrida-play[hidden] { display: none; }" in BLOCO_CSS
