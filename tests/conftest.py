"""Dados sintéticos para os testes: 6 projetos na forma da gold (uma linha por passagem por status).

Nada aqui toca o BigQuery: `dados.sla.df` é substituído pelo DataFrame abaixo, e as views e colunas que a gold calcula
(entregas do SLA, R24, fila e Atendimento mensais) são montadas por tests/gold_simulada.py a partir destes dados. Valores esperados (calculados à mão,
expediente 10h–13h + 14h–19h, com Entrada contando como tempo da equipe — regra C2):

| projeto | entrada → 1ª Aguardando Feedback            | equipe (h) | calendário (h) | fila (h) | exclusivo |
|---------|---------------------------------------------|-----------:|---------------:|---------:|-----------|
| P1      | seg 02/03 10:00 → 14:00                     |          3 |              4 |        1 | True      |
| P2      | seg 02/03 10:00 → qua 04/03 10:00           |         16 |             48 |        8 | False     |
| P3      | sex 06/03 16:00 → ter 10/03 12:00           |         13 |             92 |        3 | True      |
| P4      | nunca foi ao cliente (Declinado)            |          — |              — |        — | True      |
| P5      | qua 01/04 10:00 → sex 03/04 10:00 (volta e 2ª ida: só a 1ª conta) | 16 | 48 | 0 | None |
| P6      | seg 05/10 10:00 → ter 06/10 10:00 (mês parcial) | 8      |             24 |        0 | True      |
"""

import json
import os
import sys
import tempfile
from pathlib import Path

import pandas as pd
import pytest

os.environ["AUTH"] = "off"  # o site só sobe sem controle de acesso no computador (D10)
# previsão (D47/D56): nenhum teste dispara o job de ML; a página lê um contrato sintético (previsao_sintetica abaixo)
os.environ["PREVISAO_JOB"] = "off"
# D63: no computador a base vem congelada por padrão; os testes de recarga precisam dela viva (quem testa o
# congelamento liga CONGELAR no próprio teste)
os.environ["CONGELAR"] = "false"
# D65: o corte de 31/10 vem ligado por padrão; os testes rodam sem ele e nunca leem nem gravam a base congelada real
# (app/base_congelada); quem testa o corte liga CORTE_DADOS e usa uma pasta própria (tests/test_corte.py)
os.environ["CORTE_DADOS"] = "off"
# D68: o recorte de exibição do mês fechado vem ligado por padrão; os testes antigos rodam sem ele (comportamento E3, até
# o fim da carga); quem testa o recorte liga config.RECORTE_EXIBICAO no próprio teste (tests/test_recorte_exibicao.py)
os.environ["RECORTE_EXIBICAO"] = "off"
os.environ["BASE_CONGELADA_DIR"] = tempfile.mkdtemp(prefix="base_congelada_teste_")
_PREVISAO_ARQ = Path(tempfile.gettempdir()) / f"previsao_teste_{os.getpid()}.json"
os.environ["PREVISAO_ARQ"] = str(_PREVISAO_ARQ)
# Iniciativas (30/10/2026): nenhum teste toca o banco real (fora do Drive, em ~/.ppd-agenciamento-v2); a sessão usa uma
# pasta temporária própria, e os testes que precisam de um quadro limpo usam o fixture quadro_limpo (tmp_path)
_INI_TMP = Path(tempfile.mkdtemp(prefix="iniciativas_teste_"))
os.environ["INICIATIVAS_BACKEND"] = "sqlite"
os.environ["INICIATIVAS_DB"] = str(_INI_TMP / "iniciativas.db")
os.environ["INICIATIVAS_ANEXOS"] = str(_INI_TMP / "anexos")
os.environ.pop("INICIATIVAS_EDICAO", None)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import gold_simulada


def _passos(projeto_id, exclusivo, passos):
    linhas = []
    for i, (status, fase, entrada, saida) in enumerate(passos, start=1):
        entrada, saida = pd.Timestamp(entrada), (pd.Timestamp(saida) if saida else pd.NaT)
        linhas.append({
            "projeto_id": projeto_id, "passo": i, "status": status, "fase": fase, "entrada": entrada, "saida": saida,
            "sla_util_horas": None,
            "sla_sem_almoco_horas": None if saida is pd.NaT else gold_simulada.horas_uteis(entrada.to_pydatetime(),
                                                                                         saida.to_pydatetime()),
            "exclusivo": exclusivo, "nome_projeto": f"[Teste] {projeto_id}", "status_atual": passos[-1][0],
            "talento": "Talento", "tipo_de_input": None, "tipo_de_output": None, "marca": "Marca", "orcamento": "Pessoa",
            "em_aberto": saida is pd.NaT, "alerta": False, "retrabalho": False, "reaberto": False, "hora_extra_horas": 0.0,
            "aberto_ha_util_horas": None, "link_projeto": "https://monday.example/" + projeto_id,
            "_processado_em": pd.Timestamp("2026-10-21 21:16:22", tz="UTC"),
        })
    return linhas


@pytest.fixture(scope="session")
def movimentos():
    E, C, F = "equipe", "cliente", "fechamento"
    linhas = []
    linhas += _passos("P1", True, [("Entrada", E, "2026-03-02 10:00", "2026-03-02 11:00"),
                                   ("Em elaboração - Orçamentos", E, "2026-03-02 11:00", "2026-03-02 14:00"),
                                   ("Aguardando Feedback", C, "2026-03-02 14:00", "2026-03-20 10:00"),
                                   ("Encerrado", F, "2026-03-20 10:00", None)])
    linhas += _passos("P2", False, [("Entrada", E, "2026-03-02 10:00", "2026-03-03 10:00"),
                                    ("Em elaboração - Orçamentos", E, "2026-03-03 10:00", "2026-03-04 10:00"),
                                    ("Aguardando Feedback", C, "2026-03-04 10:00", None)])
    linhas += _passos("P3", True, [("Entrada", E, "2026-03-06 16:00", "2026-03-09 10:00"),
                                   ("Em elaboração - Orçamentos", E, "2026-03-09 10:00", "2026-03-10 12:00"),
                                   ("Aguardando Feedback", C, "2026-03-10 12:00", None)])
    linhas += _passos("P4", True, [("Entrada", E, "2026-03-11 10:00", "2026-03-11 12:00"),
                                   ("Declinado Internamente", F, "2026-03-11 12:00", None)])
    linhas += _passos("P5", None, [("Entrada", E, "2026-04-01 10:00", "2026-04-01 10:00"),
                                   ("Em elaboração - Orçamentos", E, "2026-04-01 10:00", "2026-04-03 10:00"),
                                   ("Aguardando Feedback", C, "2026-04-03 10:00", "2026-04-06 10:00"),
                                   ("Em revisão", E, "2026-04-06 10:00", "2026-04-06 12:00"),
                                   ("Aguardando Feedback", C, "2026-04-06 12:00", None)])
    linhas += _passos("P6", True, [("Entrada", E, "2026-10-05 10:00", "2026-10-05 10:00"),
                                   ("Em elaboração - Orçamentos", E, "2026-10-05 10:00", "2026-10-06 10:00"),
                                   ("Aguardando Feedback", C, "2026-10-06 10:00", None)])
    return pd.DataFrame(linhas)


@pytest.fixture(scope="session")
def entrada_diaria():
    """Entrada diária sintética (gld_agenciamento_entrada_diaria). Esperado em 2026 (E1–E3): jan 16 (Mercado 10,
    Inbound 6), fev 3 (Proativo 2, "Outros" 1 → Sem tipo), out 3 (parcial: a tabela vai até 20/10). Total 22. Mesmo
    período de 2025 (até 20/10/2025): 5 + 3 + 1 estimado + 4 = 13."""
    linhas = [("2025-01-06", "Mercado", "Mercado", "Nenhuma", 5, 0), ("2025-03-05", "Inbound", "Inbound", "Nenhuma", 3, 1),
              ("2025-10-02", "Mercado", "Mercado", "Nenhuma", 4, 0), ("2025-11-03", "Mercado", "Mercado", "Nenhuma", 7, 0),
              ("2026-01-15", "Mercado", "Mercado", "Nenhuma", 10, 0), ("2026-01-20", "Inbound", "Inbound", "Curadoria", 6, 0),
              ("2026-02-03", "Proativo", "Proativo", "Nenhuma", 2, 0), ("2026-02-03", "Outros", "Novo", "Nenhuma", 1, 0),
              ("2026-10-20", "Internos", "ViU", "Nenhuma", 3, 0)]
    df = pd.DataFrame(linhas, columns=["data", "grupo_input", "tipo_de_input", "familia", "quantidade", "quantidade_estimada"])
    df["data"] = pd.to_datetime(df["data"]).dt.date
    # situação por safra (E6): tudo entregue no mês, exceto Mercado de 15/01 (7 no mês, 2 depois, 1 não seguiu)
    # e Internos de 20/10 (3 em andamento)
    # 1ª entregas por dia (aba Atendimento, A1–A8): jan/26 = 8 + 6 = 14 (13 do próprio mês + 1 de antes); fev/26 = 2 + 2
    # (3 + 1); out/26 = 1 (0 + 1); jan/25 = 4; mar/25 = 4; out/25 (até 20/10) = 3
    df["quantidade_saida"] = [4, 4, 3, 0, 8, 6, 2, 2, 1]
    df["entregue_no_mes"] = df["quantidade"] + df["quantidade_estimada"]
    df["entregue_depois"] = df["nao_seguiu"] = df["em_andamento"] = 0
    df.loc[4, ["entregue_no_mes", "entregue_depois", "nao_seguiu"]] = [7, 2, 1]
    df.loc[8, ["entregue_no_mes", "em_andamento"]] = [0, 3]
    return df


def com_dias(entrada: pd.DataFrame, datas: list[str], processado_em: str | None = None) -> pd.DataFrame:
    """Entrada sintética + 1 pedido Mercado (entregue no mês) em cada data; opcionalmente com `_processado_em` (UTC),
    que fixa o último dia coberto (E3: véspera da carga em São Paulo)."""
    extra = pd.DataFrame([(d, "Mercado", "Mercado", "Nenhuma", 1, 0, 1, 1, 0, 0, 0) for d in datas],
                         columns=["data", "grupo_input", "tipo_de_input", "familia", "quantidade", "quantidade_estimada",
                                  "quantidade_saida", "entregue_no_mes", "entregue_depois", "nao_seguiu", "em_andamento"])
    extra["data"] = pd.to_datetime(extra["data"]).dt.date
    df = pd.concat([entrada, extra], ignore_index=True)
    if processado_em:
        df["_processado_em"] = pd.Timestamp(processado_em, tz="UTC")
    return df


@pytest.fixture(scope="session")
def fluxo_mensal():
    """Extrato sintético (gld_agenciamento_fluxo_mensal). Safra de fev/2026: 3 pedidos — 2 entregues em fevereiro,
    1 em março. Safra de jan/2026: 1 entregue em fevereiro. Logo, em fevereiro: 3 entregas = 2 de fevereiro + 1 de
    janeiro (E7)."""
    linhas = [("2026-02-01", "entregue", "2026-02-01", 2), ("2026-02-01", "entregue", "2026-03-01", 1),
              ("2026-01-01", "entregue", "2026-02-01", 1), ("2026-01-01", "nao_seguiu", None, 1)]
    df = pd.DataFrame(linhas, columns=["mes_entrada", "evento", "mes_evento", "quantidade"])
    df["mes_entrada"] = pd.to_datetime(df["mes_entrada"]).dt.date
    df["mes_evento"] = pd.to_datetime(df["mes_evento"]).dt.date
    df["grupo_input"], df["tipo_de_input"], df["familia"] = "Mercado", "Mercado", "Nenhuma"
    return df


@pytest.fixture(autouse=True)
def sem_bigquery(monkeypatch, movimentos, entrada_diaria, fluxo_mensal):
    """Todo teste usa os dados sintéticos no lugar da tabela gold."""
    from app import dados
    from app.apresentacoes.gestao_orcamentos.sla import calculos

    monkeypatch.setattr(dados.sla, "df", lambda forcar=False: movimentos)
    monkeypatch.setattr(dados.entrada, "df", lambda forcar=False: entrada_diaria)
    monkeypatch.setattr(dados.fluxo, "df", lambda forcar=False: fluxo_mensal)
    # D57: o que a gold entrega pronto (views do SLA, fila e Atendimento mensais), simulado sobre os dados sintéticos
    monkeypatch.setattr(calculos, "_da_gold", gold_simulada.sla_views)
    # as views leem a base em vigor (como no BigQuery): um teste que troca o fluxo ou a entrada muda a view junto
    monkeypatch.setattr(dados.fila, "df", lambda forcar=False: gold_simulada.fila_mensal(dados.fluxo.df()))
    # divisão de talentos (D30): por padrão, a mesma base do Início (total igual), 60/35/5 aproximado
    from app.apresentacoes.gestao_orcamentos.entrada import calculos as _ent
    _e = _ent.entrada(entrada_diaria)
    _ex = round(_e["total"] * 0.6)
    _ne = round(_e["total"] * 0.35)
    monkeypatch.setattr(dados.talentos, "df", lambda forcar=False: pd.DataFrame({
        "ano": [_e["ano"]] * 3, "categoria": ["Exclusivos", "Não exclusivos", "Sem talento"],
        "n": [_ex, _ne, _e["total"] - _ex - _ne], "total": [_e["total"]] * 3, "pct": [0.0] * 3,
        "dos_quais_squad": [0, 4, 0]}))
    import pandas as pd

    data = pd.Timestamp("2026-10-21 09:02", tz="America/Sao_Paulo").to_pydatetime()
    monkeypatch.setattr(dados.sla, "situacao", lambda: {
        "nome": "SLA", "tabela": "teste.gld", "versao": 1, "modificada_em": data, "carregada_em": data,
        "verificada_em": data, "linhas": len(movimentos), "bytes_lidos": 0, "segundos_carga": 0.0,
        "atrasada": False, "estado": "em_dia", "erro": None})
    monkeypatch.setattr(dados.fluxo, "situacao", lambda: {
        "nome": "Fluxo", "tabela": "teste.fluxo", "versao": 1, "modificada_em": data, "carregada_em": data,
        "verificada_em": data, "linhas": len(fluxo_mensal), "bytes_lidos": 0, "segundos_carga": 0.0,
        "atrasada": False, "estado": "em_dia", "erro": None})
    # top 10 por recorte, mês a mês (D50, T6/T10): uma linha por talento e mês com pedido; "todos" junta os dois grupos
    _top = [("exclusivo", "Talento A", 3, "2026-10-20", "2026-01-01", 2), ("exclusivo", "Talento A", 3, "2026-10-20", "2026-10-01", 1),
            ("exclusivo", "Talento B", 2, "2026-09-30", "2026-02-01", 2), ("nao-exclusivo", "Talento C", 1, "2026-10-01", "2026-10-01", 1)]
    _top += [("todos",) + r[1:] for r in _top]
    monkeypatch.setattr(dados.talentos_top, "df", lambda forcar=False: pd.DataFrame({
        "grupo": [r[0] for r in _top], "talento": [r[1] for r in _top], "n": [r[2] for r in _top],
        "ultimo_pedido": pd.to_datetime([r[3] for r in _top]), "empate_fora": [0] * len(_top),
        "talentos_grupo": [{"exclusivo": 2, "nao-exclusivo": 5, "todos": 7}[r[0]] for r in _top],
        "mes": pd.to_datetime([r[4] for r in _top]).date, "n_mes": [r[5] for r in _top]}))
    # A26 (D53): status das saídas sem entrega (gold), coerente com o fluxo sintético (1 não seguiu da safra de jan, sem
    # mês do evento = mês de entrada)
    _status = pd.DataFrame({"mes": pd.to_datetime(["2026-01-01"]).date, "status": ["Standby"], "n": [1], "sem_data": [1]})
    monkeypatch.setattr(dados.saidas_status, "df", lambda forcar=False: _status)
    monkeypatch.setattr(dados.atendimento, "df", lambda forcar=False: gold_simulada.atendimento_mensal(
        dados.entrada.df(), dados.fluxo.df(), dados.saidas_status.df()))
    monkeypatch.setattr(dados.talentos, "situacao", lambda: {
        "nome": "Talentos", "tabela": "teste.talentos", "versao": 1, "modificada_em": data, "carregada_em": data,
        "verificada_em": data, "linhas": 3, "bytes_lidos": 0, "segundos_carga": 0.0,
        "atrasada": False, "estado": "em_dia", "erro": None})
    monkeypatch.setattr(dados.entrada, "situacao", lambda: {
        "nome": "Entrada", "tabela": "teste.entrada", "versao": 1, "modificada_em": data, "carregada_em": data,
        "verificada_em": data, "linhas": len(entrada_diaria), "bytes_lidos": 0, "segundos_carga": 0.0,
        "atrasada": False, "estado": "em_dia", "erro": None})
    # o cache da entrada usa id(df) sem versão: limpar entre testes evita reaproveitar a base de um DataFrame já liberado
    from app.apresentacoes.gestao_orcamentos import (
        apresentacao as _ap,  # B-N7: estudo guardado por carga e grupo
    )
    from app.apresentacoes.gestao_orcamentos.entrada import calculos as ent
    calculos._cache.clear()
    ent._cache.clear()
    _ap.limpar_caches()  # estudo e telas guardados por carga (B-N7; desempenho, 31/10/2026)
    yield
    calculos._cache.clear()
    ent._cache.clear()
    _ap.limpar_caches()


@pytest.fixture
def base_um(monkeypatch):
    """Base mínima de variação = 1 (os dados sintéticos têm bases < 30). Limpa os caches antes e depois (a entrada e
    as telas guardadas por carga, que dependem da base mínima)."""
    from app.apresentacoes.gestao_orcamentos import apresentacao as _ap
    from app.apresentacoes.gestao_orcamentos.entrada import calculos as ent

    ent._cache.clear()
    _ap.limpar_caches()
    monkeypatch.setattr(ent, "BASE_MINIMA_VARIACAO", 1)
    yield
    ent._cache.clear()
    _ap.limpar_caches()


# ---------------------------------------------------------------- previsão de demanda (D56)
CARGA_PREVISAO = "2026-10-21 21:16:22+00:00"


def series_sinteticas() -> dict:
    """D56: as 4 séries do contrato sintético. Longas (2024-10 a 2026-09): Inbound cresce 4/mês a partir de 40, Mercado
    10/mês a partir de 60. Curtas (só 2026, jan–set): Mercado exclusivos = 50% do Mercado, não exclusivos = 46% (os 4%
    restantes são "sem talento", fora dos dois)."""
    meses = pd.period_range("2024-10", "2026-09", freq="M")
    inbound = pd.Series([40.0 + 4 * i for i in range(24)], index=meses, name="Inbound")
    mercado = pd.Series([60.0 + 10 * i for i in range(24)], index=meses, name="Mercado")
    m26 = mercado[mercado.index >= pd.Period("2026-01", "M")]
    return {"Inbound": inbound, "Mercado": mercado,
            "Mercado exclusivos": (m26 * 0.5).round().rename("Mercado exclusivos"),
            "Mercado não exclusivos": (m26 * 0.46).round().rename("Mercado não exclusivos")}


def previsao_sintetica() -> dict:
    """Contrato previsao.json v3 (D56) montado por ml.previsao.montar com a régua de verdade (janela de 12 meses e R7 nas
    séries curtas, teste jun–set/2026) sobre as 4 séries de series_sinteticas(). Só referências simples (sem bibliotecas
    de ML), rodadas por ml.rodar.avaliar_modelo (o "não se aplica" por série da R7 vem de lá): "arima_100_ct" = cópia da
    reta dos últimos 6 meses, para o desempate pelo mais simples; "mlp_auto" = cópia da média 6m de outra carga;
    "boost_lgbm" falhou; "prophet_log" não se aplica. Mês em andamento (out/2026): Inbound 70, Mercado 190, Mercado
    exclusivos 60 (abaixo da faixa) e não exclusivos 87, com o diagnóstico de lotes do Mercado exclusivos."""
    from ml import dados as mld
    from ml import previsao as mp
    from ml import regua, rodar
    from ml.modelos import referencia

    series = series_sinteticas()
    modelos = {}
    for m in referencia.MODELOS:
        r, _ = rodar.avaliar_modelo(m, series)
        modelos[m.nome] = {**r, "modulo": "referencia", "carga": CARGA_PREVISAO, "segundos": 0.1}
    modelos["arima_100_ct"] = {**modelos["ref_tendencia_6m"], "modulo": "arimax", "descricao": "reta (sintético)"}
    modelos["arimax_100_ct_fimdeano"] = {**modelos["ref_ultimo_mes"], "modulo": "arimax"}
    modelos["mlp_auto"] = {**modelos["ref_media_6m"], "modulo": "neural", "carga": "2026-10-20 21:00:00+00:00"}
    modelos["boost_lgbm"] = {"modulo": "boosting", "erro": "MemoryError: sintético"}
    modelos["prophet_log"] = {"modulo": "prophet", "nao_se_aplica": "a sazonalidade anual precisa de 24 meses"}
    parcial = {"Inbound": 70.0, "Mercado": 190.0, "Mercado exclusivos": 60.0, "Mercado não exclusivos": 87.0}
    recortes = {r["serie"]: {"chave": c, "tipo": r["tipo"], "grupo": r["grupo"], "fonte": r["fonte"],
                             "inicio": str(series[r["serie"]].index[0]), "meses": len(series[r["serie"]]),
                             "treino_1o_teste": len(regua.treino_de(series[r["serie"]], regua.TESTE[0])),
                             "curta": len(regua.treino_de(series[r["serie"]], regua.TESTE[0])) < regua.JANELA}
                for c, r in mld.RECORTES.items()}
    resultados = {"carga": {"processado_em": CARGA_PREVISAO, "dados_ate": "2026-10-20", "mes_fechado": "2026-09",
                            "parcial": {s: {"mes": "2026-10", "pedidos_ate_agora": v} for s, v in parcial.items()},
                            "recortes": recortes},
                  "regua": {"nome": "D56", "janela": 12, "teste": ["2026-06", "2026-09"],
                            "verificacao": ["2026-01", "2026-05"], "horizontes": [1, 2, 3], "metrica_principal": "wape"},
                  "historico": {t: {str(k): float(v) for k, v in s.items()} for t, s in series.items()},
                  "modelos": modelos}
    linhas = []
    for tipo in ("Inbound", "Mercado"):
        for mes in [*map(str, pd.period_range("2026-01", "2026-09", freq="M")), "2026-10"]:
            p = pd.Period(mes, "M")
            if tipo == "Inbound":
                total = int(series["Inbound"].get(p, parcial["Inbound"]))
                e, n = total - 8, 6  # 6 "não exclusivos" de cadastro errado (PD24) e 2 sem talento
            else:
                total = int(series["Mercado"].get(p, parcial["Mercado"]))
                e = int(series["Mercado exclusivos"].get(p, parcial["Mercado exclusivos"]))
                n = int(series["Mercado não exclusivos"].get(p, parcial["Mercado não exclusivos"]))
            linhas.append({"mes": mes, "tipo": tipo, "exclusivos": e, "nao_exclusivos": n, "sem_talento": total - e - n,
                           "total": total})
    lotes = pd.DataFrame([{"recorte": "mercado_exclusivos", "mes": m, "ate_dia": 20, "pedidos": p, "em_lote": l,
                           "avulsos": p - l, "processado_em": CARGA_PREVISAO, "dados_ate": "2026-10-20"}
                          for m, p, l in (("2026-06", 110, 30), ("2026-07", 120, 40), ("2026-08", 116, 34),
                                          ("2026-09", 130, 40), ("2026-10", 60, 10))])
    return mp._limpo(mp.montar(resultados, pd.DataFrame(linhas), lotes,
                               gerado_em=pd.Timestamp("2026-10-21 22:00", tz="UTC")))


@pytest.fixture(scope="session", autouse=True)
def arquivo_previsao():
    _PREVISAO_ARQ.write_text(json.dumps(previsao_sintetica(), ensure_ascii=False), encoding="utf-8")
    yield _PREVISAO_ARQ
    _PREVISAO_ARQ.unlink(missing_ok=True)


@pytest.fixture
def quadro_limpo(tmp_path, monkeypatch):
    """Quadro das Iniciativas novo (SQLite em tmp_path), semeado do catálogo na 1ª leitura; a instância do processo
    volta ao normal no fim."""
    from app import config
    from app.apresentacoes.gestao_orcamentos.iniciativas import repositorio

    monkeypatch.setattr(config, "INICIATIVAS_BACKEND", "sqlite")
    monkeypatch.setattr(config, "INICIATIVAS_DB", tmp_path / "iniciativas.db")
    monkeypatch.setattr(config, "INICIATIVAS_ANEXOS", tmp_path / "anexos")
    monkeypatch.setattr(config, "INICIATIVAS_EDICAO", True)
    repositorio.redefinir()
    yield repositorio.quadro()
    repositorio.redefinir()
