"""Leituras comuns da tabela SLA (gold de movimentos) para as páginas: o mês parcial e o dia de corte da carga.

As regras de negócio são da gold (ficha da tabela no PPD-GOLDEN-AGENCIAMENTO-MONDAY); aqui só se lê a carga. A visão por
projeto com filtros (`recorte`, `_por_projeto`), da antiga página de visão geral, saiu em 27/10/2026 (D57; cópia em
`_descartados/2026-10-27/versoes_anteriores/app/sla.py`).
"""

import threading
from datetime import timedelta

import pandas as pd

from app import config, dados

_cache: dict = {}
_trava = threading.Lock()  # F14 (31/10/2026): versão e mês parcial publicados juntos, como um par


def limpar_cache() -> None:
    with _trava:
        _cache.clear()


def mes_parcial(mov: pd.DataFrame) -> str:
    """Mês da última atualização da tabela (AAAA-MM): incompleto e sem os projetos ainda com a equipe.

    D68 na virada do ano (revisão de 03/11/2026): com o recorte do mês fechado, uma carga de janeiro mostra até 31/12 do
    ano anterior, e Demanda e Talentos exibem esse ano. Para o SLA e o estudo seguirem o mesmo ano (jan a dez completos),
    o mês de referência passa a ser "AAAA-13" do ano mostrado: as comparações por texto ("< AAAA-13") e as contas com o
    número do mês (13 - 1 = 12 meses completos) continuam valendo sem outra mudança."""
    versao = (dados.versao_de(mov), config.RECORTE_EXIBICAO)
    with _trava:
        guardado = _cache.get("parcial")
    if guardado is not None and guardado[0] == versao:
        return guardado[1]
    processado = mov["_processado_em"].max()
    if pd.isna(processado):
        raise dados.DadosIndisponiveis("tabela sem _processado_em")
    parcial = processado.tz_convert(config.FUSO).strftime("%Y-%m")
    from app import corte

    if corte.mes_fechado_ligado():
        mostrado = data_corte(mov)
        if mostrado is not None and mostrado.year < int(parcial[:4]):
            parcial = f"{mostrado.year}-13"
    with _trava:
        _cache["parcial"] = (versao, parcial)
    return parcial


def data_corte(mov: pd.DataFrame):
    """Último dia coberto pelos números (São Paulo): a véspera do `_processado_em`, a mesma regra do rodapé ("Dados até",
    E3). Sem o metadado (bases de teste), o dia do último movimento registrado. D68 (03/11/2026): com o recorte do mês
    fechado, o último dia MOSTRADO (fim 02/11 → 31/10, `corte.data_exibicao`)."""
    from app import corte

    if "_processado_em" in mov and mov["_processado_em"].notna().any():
        processado = pd.to_datetime(mov["_processado_em"], utc=True).max().tz_convert(config.FUSO)
        return corte.data_exibicao(processado.date() - timedelta(days=1))
    return corte.data_exibicao(max(mov["entrada"].max(), mov["saida"].max()).date())
