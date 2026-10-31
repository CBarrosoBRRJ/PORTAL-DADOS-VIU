"""Simulação, em pandas, das views e colunas da gold que o site passou a ler prontas (D57, 27/10/2026).

O site não refaz mais estas regras: lê a gold (PPD-GOLDEN-AGENCIAMENTO-MONDAY). Os testes, que não tocam o BigQuery,
precisam das mesmas tabelas montadas a partir dos dados sintéticos do conftest. Cada função abaixo reproduz o SQL da gold
indicado (a conta é a que o site fazia até 26/10/2026, conferida contra a gold em 26/10: 0 diferenças):

- `com_sem_almoco(mov)`      coluna `sla_sem_almoco_horas` (R24) de gld_agenciamento_2026_sla_movimentos
- `sla_views(mov)`           views gld_agenciamento_2026_sla_entregas e gld_agenciamento_2026_sla_entregas_status
- `fila_mensal(fluxo)`       view gld_agenciamento_fila_mensal (E7, FM1, FM2)
- `atendimento_mensal(...)`  view gld_agenciamento_atendimento_mensal (A13, AM1–AM3)

Mudou uma regra na gold? Mude aqui também, senão os testes passam a conferir outra conta.
"""

from datetime import date, datetime, time, timedelta

import pandas as pd

from app.expediente import SEM_ALMOCO, sem_expediente

COM_ALMOCO = ((10, 19),)  # o da gold em `sla_util_horas` (R13)
FILA = "Entrada"  # C9
RETORNO_MARCA = "em elaboração - retorno marca"  # C2 (D-SLA-2)
PACOTE = "[Pacote"  # X6
STATUS_EXTERNOS = ("Declinado pelo Mercado", "Declinado pelo talento", "Encerrado")  # AM3 (A27)


# ---------------------------------------------------------------- expediente (R14, R24)
def microssegundos_uteis(inicio: datetime, fim: datetime, janelas=SEM_ALMOCO) -> int:
    """Duração exata: somar inteiros antes de converter para horas evita erros nos limites do SLA."""
    if fim <= inicio:
        return 0
    total, dia = 0, inicio.date()
    while dia <= fim.date():
        if dia.weekday() < 5 and dia not in sem_expediente(dia.year):
            for h0, h1 in janelas:
                a = max(inicio, datetime.combine(dia, time(h0)))
                b = min(fim, datetime.combine(dia, time(h1)))
                if b > a:
                    intervalo = b - a
                    total += (intervalo.days * 86400 + intervalo.seconds) * 1_000_000 + intervalo.microseconds
        dia += timedelta(days=1)
    return total


def horas_uteis(inicio: datetime, fim: datetime, janelas=SEM_ALMOCO) -> float:
    return microssegundos_uteis(inicio, fim, janelas) / 3_600_000_000


def _util(dia: date) -> bool:
    return dia.weekday() < 5 and dia not in sem_expediente(dia.year)


def dias_uteis_entre(inicio: datetime, fim: datetime, fim_expediente: int = 19) -> int:
    """C3b: viradas de dia útil entre o pedido e a entrega; pedido fora do expediente conta do próximo dia útil."""
    dia = inicio.date()
    if inicio.hour >= fim_expediente or not _util(dia):
        dia += timedelta(days=1)
        while not _util(dia):
            dia += timedelta(days=1)
    n = 0
    while dia < fim.date():
        if _util(dia):
            n += 1
        dia += timedelta(days=1)
    return n


def dias_uteis_fracao(inicio: datetime, fim: datetime, janelas=SEM_ALMOCO) -> float:
    """C3c (D54): dias úteis com fração pelo expediente (8 h por dia útil)."""
    if fim <= inicio:
        return 0.0
    dia_us = sum((h1 - h0) * 3_600_000_000 for h0, h1 in janelas)
    total, dia = 0.0, inicio.date()
    while dia <= fim.date():
        if _util(dia):
            total += microssegundos_uteis(max(inicio, datetime.combine(dia, time(0))),
                                          min(fim, datetime.combine(dia + timedelta(days=1), time(0))), janelas) / dia_us
        dia += timedelta(days=1)
    return total


# ---------------------------------------------------------------- SLA
def com_sem_almoco(mov: pd.DataFrame) -> pd.DataFrame:
    """R24: horas úteis sem almoço de cada passo concluído (NULL no passo em aberto), sem arredondar."""
    mov = mov.copy()
    mov["sla_sem_almoco_horas"] = [None if pd.isna(s) else horas_uteis(e.to_pydatetime(), s.to_pydatetime())
                                   for e, s in zip(mov["entrada"], mov["saida"])]
    return mov


def sla_views(mov: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """(entregas, horas por status) no formato das duas views gold. `entregas.attrs["invalidos"]` conta os projetos
    descartados pela C4 (1ª ida ao cliente no passo 1)."""
    passo1 = mov.loc[mov["passo"] == 1].set_index("projeto_id")
    inicio = passo1["entrada"]
    cliente = mov.loc[mov["fase"] == "cliente"]
    primeira = cliente.loc[cliente.groupby("projeto_id")["passo"].idxmin()].set_index("projeto_id")
    invalidos = int((primeira["passo"] <= 1).sum())
    primeira = primeira.loc[primeira["passo"] > 1]
    antes = mov.merge(primeira["passo"].rename("passo_pronto"), left_on="projeto_id", right_index=True)
    fora = antes["status"].astype("string").str.lower().str.startswith(RETORNO_MARCA).fillna(False).astype(bool)
    equipe = antes.loc[(antes["fase"] == "equipe") & (antes["passo"] < antes["passo_pronto"]) & ~fora].dropna(
        subset=["saida"]).copy()
    equipe["us"] = [microssegundos_uteis(e.to_pydatetime(), s.to_pydatetime()) for e, s in zip(equipe["entrada"], equipe["saida"])]
    status = equipe["status"].str.lower()

    def horas(mascara) -> pd.Series:
        return equipe.loc[mascara].groupby("projeto_id")["us"].sum().reindex(primeira.index, fill_value=0) / 3_600_000_000

    ini = inicio.reindex(primeira.index)
    nomes = passo1["nome_projeto"].reindex(primeira.index) if "nome_projeto" in passo1 else pd.Series("", index=primeira.index)
    e = pd.DataFrame({
        "mes": primeira["entrada"].dt.to_period("M").dt.to_timestamp().dt.date,
        "mes_entrada": ini.dt.to_period("M").dt.to_timestamp().dt.date,
        "inicio": ini,
        "entregue_em": primeira["entrada"],
        "exclusivo": passo1["exclusivo"].reindex(primeira.index),
        "tipo_de_input": (passo1["tipo_de_input"].reindex(primeira.index) if "tipo_de_input" in passo1 else None),
        "pacote": nomes.fillna("").astype(str).str.strip().str.startswith(PACOTE),
        "h_trabalho": horas(equipe.index == equipe.index),
        "h_fila": horas(equipe["status"] == FILA),
        "h_elaboracao": horas(status.str.startswith("em elabora")),
        "h_revisao": horas(status.str.startswith("em revis")),
        "h_calendario": (primeira["entrada"] - ini).dt.total_seconds() / 3600,
        "dias_uteis": [dias_uteis_entre(a.to_pydatetime(), b.to_pydatetime()) for a, b in zip(ini, primeira["entrada"])],
        "dias_uteis_fr": [dias_uteis_fracao(a.to_pydatetime(), b.to_pydatetime()) for a, b in zip(ini, primeira["entrada"])],
    }, index=primeira.index).rename_axis("projeto_id").reset_index()
    if "_processado_em" in mov:
        e["_processado_em"] = mov["_processado_em"].max()
    e.attrs["invalidos"] = invalidos
    ps = (equipe.groupby(["projeto_id", "status"], as_index=False)["us"].sum()
          .assign(h=lambda x: x["us"] / 3_600_000_000).drop(columns="us"))
    return e, ps


# ---------------------------------------------------------------- Início e Atendimento
def _fluxo(fluxo: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame({"safra": pd.to_datetime(fluxo["mes_entrada"]).dt.to_period("M"), "evento": fluxo["evento"],
                         "quando": pd.to_datetime(fluxo["mes_evento"]).dt.to_period("M"),
                         "n": fluxo["quantidade"].fillna(0).astype(int)})


def fila_mensal(fluxo: pd.DataFrame, ate: str | None = None) -> pd.DataFrame:
    """View gld_agenciamento_fila_mensal: mês × safra, de 2024-10 (ou da 1ª safra) até `ate` (ou o último mês da base)."""
    f = _fluxo(fluxo)
    ultimo = pd.Period(ate, "M") if ate else max(f["safra"].max(), f["quando"].max())
    linhas = []
    for x in pd.period_range(min(pd.Period("2024-10", "M"), f["safra"].min()), ultimo, freq="M"):
        for safra, g in f.loc[f["safra"] <= x].groupby("safra"):
            do_ano = safra.year == x.year
            novos = int(g["n"].sum()) if safra == x else 0
            represados = int(g.loc[(safra < x) & ((g["evento"] == "em_andamento") | (g["quando"] >= x)), "n"].sum())
            entregues = int(g.loc[(g["evento"] == "entregue") & (g["quando"] == x), "n"].sum())
            nao = int(g.loc[(g["evento"] == "nao_seguiu") & ((g["quando"] == x) | (g["quando"].isna() & (safra == x))),
                            "n"].sum())
            seguem = int(g.loc[(g["evento"] == "em_andamento") | (g["quando"] > x), "n"].sum())
            if not do_ano:
                novos = represados = nao = seguem = 0
            if (novos + represados + entregues + nao + seguem if do_ano else entregues) > 0:
                linhas.append({"mes": x.to_timestamp().date(), "mes_entrada": safra.to_timestamp().date(), "do_ano": do_ano,
                               "novos": novos, "represados": represados, "entregues": entregues, "nao_seguiram": nao,
                               "seguem": seguem})
    df = pd.DataFrame(linhas, columns=["mes", "mes_entrada", "do_ano", "novos", "represados", "entregues", "nao_seguiram",
                                       "seguem"])
    if "_processado_em" in fluxo:
        df["_processado_em"] = fluxo["_processado_em"].max()
    return df


def atendimento_mensal(entrada: pd.DataFrame, fluxo: pd.DataFrame | None, status: pd.DataFrame | None = None) -> pd.DataFrame:
    """View gld_agenciamento_atendimento_mensal: um mês por linha, de 2025-01 até o mês do último dia coberto (E3)."""
    from app.apresentacoes.gestao_orcamentos.entrada import calculos as ent

    ultimo = ent.ultimo_dia(entrada, ent._base(entrada))
    meses = pd.period_range("2025-01", ultimo.to_period("M"), freq="M")
    d = entrada.loc[pd.to_datetime(entrada["data"]) <= ultimo]
    entradas = (d["quantidade"] + d["quantidade_estimada"]).groupby(pd.to_datetime(d["data"]).dt.to_period("M")).sum()
    entregues = sem = sem_data = pd.Series(dtype=int)
    if fluxo is not None and not fluxo.empty:
        f = _fluxo(fluxo)
        f = f.loc[f["evento"].isin(["entregue", "nao_seguiu"])].assign(mes=lambda x: x["quando"].fillna(x["safra"]))
        f = f.loc[f["safra"].dt.year == f["mes"].dt.year]  # AM1
        entregues = f.loc[f["evento"] == "entregue"].groupby("mes")["n"].sum()
        sem = f.loc[f["evento"] == "nao_seguiu"].groupby("mes")["n"].sum()
        sem_data = f.loc[(f["evento"] == "nao_seguiu") & f["quando"].isna()].groupby("mes")["n"].sum()  # AM2
    total_st = externos_st = pd.Series(dtype=int)
    if status is not None and not status.empty:
        m = pd.to_datetime(status["mes"]).dt.to_period("M")
        total_st = status.groupby(m)["n"].sum()
        externos_st = status.loc[status["status"].isin(STATUS_EXTERNOS)].groupby(m)["n"].sum()
    linhas, ficou = [], 0
    for x in meses:
        if x.month == 1:
            ficou = 0  # AM1: a fila recomeça em janeiro
        n, ent_, sem_ = int(entradas.get(x, 0)), int(entregues.get(x, 0)), int(sem.get(x, 0))
        confere = x in total_st.index and int(total_st[x]) == sem_  # AM3
        externos = int(externos_st.get(x, 0)) if confere else 0
        veio = ficou
        ficou = veio + n - ent_ - sem_
        linhas.append({"mes": x.to_timestamp().date(), "completo": x < ultimo.to_period("M") or ultimo == x.to_timestamp(how="end").normalize(),
                       "entradas": n, "entregues": ent_, "sem_entrega": sem_, "sem_entrega_sem_data": int(sem_data.get(x, 0)),
                       "respondidos": ent_ + sem_, "veio": veio, "para_atender": veio + n, "ficou": ficou,
                       "status_confere": confere, "externos": externos, "dependia": veio + n - externos})
    df = pd.DataFrame(linhas)
    if fluxo is not None and "_processado_em" in fluxo:
        df["_processado_em"] = fluxo["_processado_em"].max()
    return df
