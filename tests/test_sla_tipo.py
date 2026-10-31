"""D43 (25/10/2026, Caio): slide 7 do estudo "Como medimos" — "Em que tipo de pedido o tempo trava?". Por Tipo de Input
(coluna `tipo_de_input` da gold de movimentos): % em até 2 dias (mesmo A dos slides 3 e 4), típico, onde mais trava
entre os que passam de 2 dias, grupos de maior e menor volume, "Outros", cor por regra (vermelho só no tipo claramente
pior que o geral), faixa do pé curta e nada de nota na tela (ajuste do Caio, 25/10/2026) (J1–J9)."""

import pandas as pd
from fastapi.testclient import TestClient

from app.apresentacoes.gestao_orcamentos.sla import calculos as c
from app.apresentacoes.gestao_orcamentos import apresentacao
import gold_simulada  # views da gold sobre os dados sintéticos (D57)


def _u(spec: list[tuple[str | None, list[float]]]) -> pd.DataFrame:
    """[(tipo, [h de cada orçamento])] → universo com projeto_id, mes, h_trabalho e tipo_input."""
    linhas, i = [], 0
    for tipo, hs in spec:
        for h in hs:
            linhas.append({"projeto_id": f"P{i}", "mes": "2026-04", "h_trabalho": float(h), "tipo_input": tipo})
            i += 1
    return pd.DataFrame(linhas)


def _ps(u: pd.DataFrame, etapa_lenta: dict[str, str]) -> pd.DataFrame:
    """Horas por status: cada orçamento põe 1/4 do tempo em Entrada, 1/4 em Revisão e metade no status `etapa_lenta`
    do seu tipo (ou em Orçamentos)."""
    linhas = []
    for r in u.itertuples():
        principal = etapa_lenta.get(r.tipo_input, "Em elaboração - Orçamentos")
        partes = {"Entrada": r.h_trabalho / 4, "Em revisão - Validação Talento": r.h_trabalho / 4}
        partes[principal] = partes.get(principal, 0) + r.h_trabalho / 2
        linhas += [{"projeto_id": r.projeto_id, "status": st, "h": h} for st, h in partes.items()]
    return pd.DataFrame(linhas)


def _base():
    return _u([("Mercado", [8] * 60 + [30] * 40),  # 100: 60% até 2 dias, 40% passam
               ("Inbound", [8] * 25 + [30] * 25),  # 50: 50% / 50% → destaque (geral 45%)
               ("ViU", [4] * 35 + [20] * 5),  # 40
               ("Interna", [30] * 30),  # 30: 100% passam, poucos
               ("ViU First", [30] * 5), ("OTR (Oportunidade em Tempo Real)", [8] * 2), (None, [8] * 1)])


def test_contagens_grupos_e_outros():
    u = _base()
    v = c._tipos(u, _ps(u, {}), "2026-05")
    assert v["n"] == 228 and v["geral"]["n"] == 228
    # J2: menos de 30 pedidos (ViU First, OTR) e vazio vão para Outros, sem linha; nome sem o parêntese
    assert [o["tipo"] for o in v["outros"]] == ["ViU First", "OTR", "vazio"] and v["n_outros"] == 8
    assert {r["tipo"] for r in v["linhas"]} == {"Mercado", "Inbound", "ViU", "Interna"}
    # J3: ≥ 10% dos pedidos = maior volume (Mercado 43,9%, Inbound 21,9%, ViU 17,5%, Interna 13,2%)
    assert [g["chave"] for g in v["grupos"]] == ["maior"]
    assert [r["tipo"] for r in v["grupos"][0]["linhas"]] == ["Mercado", "Inbound", "ViU", "Interna"]
    merc = v["linhas"][0]
    assert merc["pct_txt"] == "43,9%" and merc["a"] == 60 and merc["b"] == 40 and merc["tipico"] == "8 h"


def test_mesmo_a_e_tipico_dos_slides_3_e_4():
    u = _base()
    v = c._tipos(u, _ps(u, {}), "2026-05")
    cem = c._cem(u["h_trabalho"], "2026-05")
    assert v["geral"]["a"] == cem["a"] and v["geral"]["b"] == cem["b"]
    assert v["geral"]["tipico"] == c._h(float(u["h_trabalho"].median()))
    assert v["legenda_geral"] == f"Geral: {cem['a']}% em até 2 dias"


def test_onde_mais_trava_e_destaque_com_faixa():
    u = _u([("Mercado", [8] * 60 + [30] * 40), ("Inbound", [8] * 50 + [30] * 50), ("ViU", [4] * 30)])
    v = c._tipos(u, _ps(u, {"Inbound": "Entrada", "Mercado": "Em elaboração - Orçamentos"}), "2026-05")
    inb = next(r for r in v["linhas"] if r["tipo"] == "Inbound")
    merc = next(r for r in v["linhas"] if r["tipo"] == "Mercado")
    # J5: Inbound põe 3/4 do tempo na Entrada; Mercado metade na Elaboração
    assert inb["trava"]["etapa"] == "Fila de entrada" and inb["trava"]["p"] == 75
    assert merc["trava"]["etapa"] == "Elaboração" and merc["trava"]["p"] == 50
    # J6: geral = 39% passam (90 de 230); Inbound 50% (≥ 3 pontos acima) → vermelho e tipo da faixa; Mercado 40% não
    assert v["geral"]["b"] == 39 and inb["vermelho"] and inb["destaque"] and not merc["vermelho"]
    assert v["tipo"] == "destaque"
    assert v["rodape"] == ("<strong>O Inbound é o que mais demora</strong>: 50% passam de 2 dias, contra 39% no geral "
                           "— e passa mais tempo na fila de entrada.")  # batalha de agentes (B-N3): J5 é outra medida que a do slide 6
    assert "passam de 2 dias, bem acima do geral." in inb["leitor"]
    # 2 pontos acima do geral: amarelo; 3 pontos (limite inclusivo): vermelho
    u2 = _u([("Mercado", [8] * 64 + [30] * 36), ("Inbound", [8] * 60 + [30] * 40)])
    v2 = c._tipos(u2, _ps(u2, {}), "2026-05")
    assert v2["geral"]["b"] == 38 and [r["vermelho"] for r in v2["linhas"]] == [False, False]
    u3 = _u([("Mercado", [8] * 140 + [30] * 60), ("Inbound", [8] * 65 + [30] * 35)])
    v3 = c._tipos(u3, _ps(u3, {}), "2026-05")
    assert v3["geral"]["b"] == 32 and [r["vermelho"] for r in v3["linhas"]] == [False, True]


def test_variante_parecido_aviso_de_menor_volume_e_sem_lentos():
    u = _u([("Mercado", [8] * 120 + [30] * 80), ("Inbound", [8] * 122 + [30] * 78), ("Globo", [30] * 20 + [8] * 10),
            ("ViU", [4] * 30)])
    v = c._tipos(u, _ps(u, {}), "2026-05")
    assert [g["rotulo"] for g in v["grupos"]] == ["Maior volume · 87% dos pedidos", "Menor volume · 13% dos pedidos"]
    assert v["tipo"] == "parecido" and not any(r["destaque"] for r in v["linhas"])
    assert [r["tipo"] for r in v["linhas"] if r["vermelho"]] == ["Globo"]
    assert v["rodape"] == ("<strong>Os tipos de maior volume ficam perto do geral</strong>: de 39% a 40% passam de 2 dias, "
                           "contra 39%. Só <strong>Globo</strong>, de menor volume, passa bem mais.")
    # J8 (fora da tela): Globo em vermelho no aria-label; sem Outros, sem a frase de Outros
    assert "O tipo Globo chega a 67% acima de 2 dias, com 30 pedidos." in v["nota"] and v["nota"] not in v["texto"]
    assert "O tipo Globo chega a 67%" in v["texto"]
    assert "Outros" not in v["nota"] and v["nota"].startswith("Os mesmos 460 orçamentos das páginas anteriores")
    viu = next(r for r in v["linhas"] if r["tipo"] == "ViU")
    assert viu["b"] == 0 and viu["trava"] is None and "Nenhum pedido passa de 2 dias." in viu["leitor"]
    assert not viu["b_dentro"] and viu["a_dentro"]


def test_poucos_dados_e_sem_coluna():
    assert c._tipos(_u([("Mercado", [8] * 29)]), pd.DataFrame(columns=["projeto_id", "status", "h"]), "2026-05") is None
    u = _u([(None, [8] * 40)]).drop(columns="tipo_input")
    v = c._tipos(u, _ps(u.assign(tipo_input=None), {}), "2026-05")
    assert v["grupos"] == [] and v["outros"] == [{"tipo": "vazio", "n": 40}] and v["rodape"] is None
    assert c._tipo_nome("OTR (Oportunidade em Tempo Real)") == "OTR" and c._tipo_nome("  ") == "vazio"


def _mov(versao: str) -> pd.DataFrame:
    linhas = []
    for i in range(120):
        d = ["2026-01-05", "2026-02-02", "2026-03-02", "2026-04-06"][i % 4]
        t = lambda hm: pd.Timestamp(f"{d} {hm}")  # noqa: E731
        fim_fila = "16:00" if i % 3 == 0 else "11:00"
        b = {"projeto_id": f"T{i}", "exclusivo": i % 2 == 0, "nome_projeto": f"T{i}", "sla_util_horas": None,
             "tipo_de_input": "Inbound" if i % 3 == 0 else "Mercado"}
        for k, (st, fase, e, s) in enumerate([("Entrada", "equipe", "10:00", fim_fila),
                                               ("Em elaboração - Orçamentos", "equipe", fim_fila, "17:00"),
                                               ("Aguardando Feedback", "cliente", "17:00", None)], start=1):
            linhas.append({**b, "passo": k, "status": st, "fase": fase, "entrada": t(e), "saida": t(s) if s else pd.NaT})
    df = gold_simulada.com_sem_almoco(pd.DataFrame(linhas))  # R24 da gold
    df.attrs["versao"] = versao
    df["_processado_em"] = pd.Timestamp("2026-05-12 21:16:22", tz="UTC")
    return df


def test_tipo_lido_da_gold_e_slide_7_no_html(monkeypatch):
    from app import dados, sla
    from app.main import app

    monkeypatch.setattr(apresentacao, "ESTUDO_TIPO", True)  # D64: o slide 7 saiu da apresentação; aqui, ligado
    mov = _mov("d43-html")
    v = c.tipos_pedido(mov, "2026-05", "todos")
    assert {r["tipo"]: r["n"] for r in v["linhas"]} == {"Mercado": 80, "Inbound": 40}
    monkeypatch.setattr(dados.sla, "df", lambda forcar=False: mov)
    sla._cache.clear()
    with TestClient(app) as cli:
        html = cli.get("/viu-agenciamento/sla/como-medimos?talentos=exclusivos").text
    sla._cache.clear()
    assert html.count('class="slide slide-estudo') == 6  # V2 (30/10/2026): 3 e 4 unidos e sem a conclusão; com o tipo ligado, ele é o 6 de 6
    s7 = html.split('slide-tipo"')[1]
    for txt in ("Exploração dos dados · e por tipo de pedido?", "Em que tipo de pedido o tempo trava?", "Tipo de input",
                "Saem em até 2 dias", "Passam de 2 dias", "Tempo típico", "Onde passa mais tempo", "Todos os pedidos",
                "Passam de 2 dias, bem acima do geral"):
        assert txt in s7
    # V2 (30/10/2026): com o tipo ligado, ele é o último: o ✕ dele marca o fim, o da trava não
    assert "fechar-fim" in s7 and "fechar-fim" not in html.split('slide-trava"')[1].split('slide-tipo"')[0]
    for g in ("todos", "exclusivos", "nao-exclusivos"):
        assert f'href="?talentos={g}#6"' in s7
    assert 'href="?talentos=exclusivos#6" class="grupo" aria-current="true"' in s7
    from pathlib import Path  # trava → tipo (#6) quando ligado (os dados daqui não têm trava suficiente para o slide 5)
    tpl = (Path(__file__).resolve().parent.parent / "app" / "templates" / "como_medimos.html").read_text(encoding="utf-8")
    assert '{% if mostrar_tipo %}<p class="explora-gancho"><a class="gancho-link" href="#6">{{ v.gancho }}' in tpl
    assert "saem em até 2 dias e" in s7 and 'class="so-leitor"' in s7  # barra com texto para leitor de tela
    assert 'style="' not in s7 and "<style" not in s7
    assert 'class="tq-nota"' not in s7 and "Os mesmos" not in s7  # ajuste do Caio: sem nota na tela


def test_slide_7_com_poucos_dados(monkeypatch):
    from app import dados, sla
    from app.main import app

    monkeypatch.setattr(apresentacao, "ESTUDO_TIPO", True)  # D64
    mov = _mov("d43-poucos")
    mov = mov.loc[mov["projeto_id"].isin([f"T{i}" for i in range(10)])]
    mov.attrs["versao"] = "d43-poucos"
    monkeypatch.setattr(dados.sla, "df", lambda forcar=False: mov)
    sla._cache.clear()
    with TestClient(app) as cli:
        html = cli.get("/viu-agenciamento/sla/como-medimos").text
    sla._cache.clear()
    s7 = html.split('slide-tipo"')[1]
    assert "Ainda não há orçamentos suficientes" in s7 and "tq-tabela" not in s7
