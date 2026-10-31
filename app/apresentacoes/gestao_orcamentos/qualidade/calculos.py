"""Qualidade dos dados da área de orçamentos: verificações sobre a tabela gold de SLA (D21).

Duas famílias. **Integridade** (Q1–Q6): o esperado é zero; qualquer caso indica falha na gold ou na carga e precisa
de correção. **Atenção** (A1–A5): situações reais do board que o relatório trata de um jeito definido; a contagem
mostra quanto pesam e o efeito no SLA. Mudou uma verificação? Altere aqui e registre no PRD. O template só mostra.

Q1  Base atualizada no horário: a gold atualizou na agenda (seg–sex 09:00 + tolerância) e o site leu a carga.
Q2  Passo repetido: mesmo projeto e passo mais de uma vez (o contrato da carga já recusa; fica visível aqui).
Q3  Projeto que não começa em Entrada: passo 1 ausente ou com outro status.
Q4  Saída antes da entrada num passo.
Q5  Buraco no histórico: passo sem saída que não é o último do projeto.
Q6  Ida ao cliente sem passar pela equipe: 1ª fase `cliente` no passo 1 (C4 descarta).
A1  Entregue em menos de 5 minutos (calendário até a 1ª ida ao cliente): card movido direto, sem o trabalho registrado.
A2  Entregue depois de 30 dias corridos.
A3  Card que voltou de Aguardando Feedback para Entrada (F4: ajuste, pedido novo ou movimentação em lote?).
A4  Aguardando o cliente há mais de 30 dias corridos (a automação de Encerrado deveria ter fechado; F1).
A5  Projeto sem talento (`exclusivo` nulo).
"""

import pandas as pd

from app.apresentacoes.gestao_orcamentos.sla import calculos as sla_calculos
from app.dados import versao_de

ENTREGA_RELAMPAGO_MIN = 5  # A1
LIMITE_DIAS_CORRIDOS = 30  # A2, A4 (mesmo prazo da automação de Encerrado)
FUSO = "America/Sao_Paulo"  # `entrada`/`saida` da gold são horário de Brasília sem fuso

_cache: dict = {}


def _integridade(mov: pd.DataFrame, estado: str) -> list[dict]:
    ultimo = mov.groupby("projeto_id")["passo"].transform("max")
    inicio = mov.loc[mov["passo"] == 1].set_index("projeto_id")["status"]
    projetos = mov["projeto_id"].nunique()
    cliente = mov.loc[mov["fase"] == "cliente"].groupby("projeto_id")["passo"].min()
    itens = [
        ("Q1", "Base atualizada no horário", "a gold atualiza seg–sex às 09:00", 0 if estado in ("em_dia", "congelada") else 1),
        ("Q2", "Nenhum passo repetido", "cada projeto tem um registro por passo", int(mov.duplicated(["projeto_id", "passo"]).sum())),
        ("Q3", "Todo projeto começa em Entrada", "o pedido sempre nasce na fila", int(projetos - (inicio == "Entrada").sum())),
        ("Q4", "Nenhuma saída antes da entrada", "datas de cada passo em ordem", int((mov["saida"] < mov["entrada"]).sum())),
        ("Q5", "Histórico sem buracos", "só o passo atual fica sem saída", int((mov["saida"].isna() & (mov["passo"] < ultimo)).sum())),
        ("Q6", "Nenhuma ida ao cliente sem a equipe", "a 1ª entrega sempre passa pela equipe", int((cliente <= 1).sum())),
    ]
    return [{"id": i, "titulo": t, "detalhe": d, "n": n, "ok": n == 0} for i, t, d, n in itens]


def _atencao(mov: pd.DataFrame) -> list[dict]:
    e = sla_calculos.entregas(mov)  # mesma base do slide de SLA (C1, C4)
    anterior = mov.sort_values(["projeto_id", "passo"]).groupby("projeto_id")["status"].shift()
    volta = (mov["status"] == "Entrada") & (anterior == "Aguardando Feedback")
    processado = mov["_processado_em"].max().tz_convert(FUSO).tz_localize(None)
    atual = mov.loc[mov["passo"] == mov.groupby("projeto_id")["passo"].transform("max")]
    parado = atual.loc[(atual["status"] == "Aguardando Feedback") & atual["saida"].isna()]
    sem_talento = mov.loc[mov["passo"] == 1, "exclusivo"].isna()
    com_volta = mov.loc[volta, "projeto_id"].nunique()
    itens = [
        ("A1", f"Entregues em menos de {ENTREGA_RELAMPAGO_MIN} minutos", int((e["h_calendario"] < ENTREGA_RELAMPAGO_MIN / 60).sum()),
         "orçamentos", "card movido direto, sem o trabalho registrado",
         "entram no SLA e puxam o tempo típico para baixo"),
        ("A2", f"Entregues depois de {LIMITE_DIAS_CORRIDOS} dias corridos", int((e["h_calendario"] > LIMITE_DIAS_CORRIDOS * 24).sum()),
         "orçamentos", "pedido parado muito tempo antes da 1ª entrega",
         "entram no SLA; a mediana quase não muda"),
        ("A3", "Voltaram do cliente para Entrada", int(volta.sum()),
         f"voltas em {com_volta} projeto{'s' if com_volta != 1 else ''}", "ajuste, pedido novo ou movimentação em lote?",
         "não mudam a 1ª entrega; o depois conta como retrabalho"),
        ("A4", f"Aguardando o cliente há mais de {LIMITE_DIAS_CORRIDOS} dias", int((processado - parado["entrada"] > pd.Timedelta(days=LIMITE_DIAS_CORRIDOS)).sum()),
         "projetos", "a automação deveria ter encerrado",
         "não afetam o SLA; inflam a lista de pendências do board"),
        ("A5", "Projetos sem talento", int(sem_talento.sum()),
         "projetos", "campo de talento vazio no board",
         "ficam fora dos grupos exclusivos e não exclusivos"),
    ]
    return [{"id": i, "titulo": t, "n": n, "unidade": u, "explicacao": x, "efeito": f} for i, t, n, u, x, f in itens]


def qualidade(mov: pd.DataFrame, situacao: dict) -> dict:
    """Números do slide "Os dados do relatório são confiáveis?" (em cache por carga e estado da base)."""
    chave = (versao_de(mov), situacao["estado"])
    if chave not in _cache:
        while len(_cache) >= 3:
            _cache.pop(next(iter(_cache)))
        integridade = _integridade(mov, situacao["estado"])
        _cache[chave] = {
            "integridade": integridade,
            "integridade_ok": sum(i["ok"] for i in integridade),
            "atencao": _atencao(mov),
            "passos": len(mov),
            "projetos": int(mov["projeto_id"].nunique()),
        }
    return {**_cache[chave], "situacao": situacao}
