"""Números e datas em pt-BR (filtros do Jinja e textos das páginas)."""

import math
import numbers
from datetime import datetime

HORAS_DIA_UTIL = 9  # 10h–19h (ficha da gold, R13)


def inteiro(valor) -> str:
    """Inteiro com ponto de milhar; arredonda meio para cima (8,5 → 9), como os percentuais da tela."""
    if valor is None or valor != valor:
        return "—"
    return f"{math.floor(valor + 0.5):,}".replace(",", ".")


def decimal(valor, casas: int = 1) -> str:
    if valor is None or valor != valor:
        return "—"
    return f"{valor:,.{casas}f}".replace(",", "#").replace(".", ",").replace("#", ".")


# F13 (auditoria do Codex, 31/10/2026): UMA política de arredondamento para percentuais isolados em todo o portal —
# meio para cima (12,5% → 13%; 1 de 8 dá 13% em todas as páginas), simétrica no sinal (−12,5% → −13%). O `round()` do
# Python e o formato "{:.0f}" arredondam o empate para o par (12,5 → 12) e não são usados para percentuais. Parcelas que
# precisam somar 100% (barras e frações da mesma tela) seguem o maior resto (`parcelas_100`, E8c).
_RUIDO = 9  # casas em que o resultado da conta é cortado antes de arredondar: 0,285 × 100 = 28,4999… vira o empate 28,5


def arredondar(valor: float, casas: int = 0) -> float:
    """Meio para cima (afastando do zero), sem o ruído do ponto flutuante; nunca devolve −0."""
    escala = 10 ** casas
    r = math.floor(round(abs(valor) * escala, _RUIDO) + 0.5) / escala
    return r if valor >= 0 or r == 0 else -r


def pct_inteiro(parte, total) -> int:
    """Percentual inteiro de parte ÷ total, meio para cima (conta exata com inteiros não negativos); 0 sem total."""
    if not total:
        return 0
    if isinstance(parte, numbers.Integral) and isinstance(total, numbers.Integral) and parte >= 0 and total > 0:
        return int((200 * int(parte) + int(total)) // (2 * int(total)))
    return int(arredondar(100 * parte / total))


def parcelas_100(valores: list[int]) -> list[int]:
    """Parcelas inteiras que fecham em 100 pelo maior resto (E8c): parte inteira de cada uma e +1 nos maiores restos até
    somar 100 (empate de resto: a ordem da lista decide). Total zero → zeros."""
    total = sum(valores)
    if not total:
        return [0] * len(valores)
    base = [v * 100 // total for v in valores]
    ordem = sorted(range(len(valores)), key=lambda i: -(valores[i] * 100 % total))
    for i in ordem[:100 - sum(base)]:
        base[i] += 1
    return base


def pct(valor, casas: int = 0) -> str:
    """Percentual para a tela ('13%', '87,5%'), meio para cima (F13)."""
    return "—" if valor is None or valor != valor else f"{decimal(arredondar(valor * 100, casas), casas)}%"


def _pct_inteiro(valor) -> int:
    """Percentual inteiro arredondado meio para cima, sem perder o sinal (−0,4% vira 0, não "-0%")."""
    return int(arredondar(valor * 100))


def variacao(valor, sinal: bool = True) -> str:
    """Variação para a tela: '+91%', '−13%' (sinal de menos tipográfico) ou '0%'. O sinal sai do número já
    arredondado, para a frase nunca contradizer o que está escrito. sinal=False devolve só o tamanho ('91%')."""
    if valor is None or valor != valor:
        return "—"
    n = _pct_inteiro(valor)
    if not sinal:
        return f"{inteiro(abs(n))}%"
    return f"+{inteiro(n)}%" if n > 0 else f"−{inteiro(-n)}%" if n < 0 else "0%"


def sentido(valor) -> str | None:
    """'alta', 'queda' ou 'igual' pelo percentual arredondado; None sem variação (base pequena ou sem régua)."""
    if valor is None or valor != valor:
        return None
    n = _pct_inteiro(valor)
    return "alta" if n > 0 else "queda" if n < 0 else "igual"


def dias_uteis(horas, casas: int = 1) -> str:
    return "—" if horas is None or horas != horas else decimal(horas / HORAS_DIA_UTIL, casas)


def data_hora(valor: datetime | None) -> str:
    return "—" if valor is None else valor.strftime("%d/%m/%Y %H:%M")


def atualizado(valor: datetime | None) -> str:
    """Rodapé das páginas: '23/10/2026, 17:24' (horário de Brasília)."""
    if valor is None:
        return "—"
    from app.config import FUSO

    return valor.astimezone(FUSO).strftime("%d/%m/%Y, %H:%M")


def recorte(valor: datetime | None) -> str:
    """Último dia coberto pelos números: a véspera da atualização (a gold fecha o dia anterior; regra E3)."""
    if valor is None:
        return "—"
    from datetime import timedelta

    from app.config import FUSO

    return (valor.astimezone(FUSO) - timedelta(days=1)).strftime("%d/%m/%Y")


def quando(valor: datetime | None, agora: datetime | None = None) -> str:
    """'hoje, 09:02' / 'ontem, 09:02' / '21/10, 09:02' (horário de Brasília)."""
    if valor is None:
        return "—"
    from app.config import FUSO

    valor = valor.astimezone(FUSO)
    hoje = (agora or datetime.now(FUSO)).astimezone(FUSO).date()
    dias = (hoje - valor.date()).days
    dia = "hoje" if dias == 0 else ("ontem" if dias == 1 else valor.strftime("%d/%m"))
    return f"{dia}, {valor:%H:%M}"


MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]
MESES_EXTENSO = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro",
                 "novembro", "dezembro"]


def parcela(pct, n) -> str:
    """Parcela inteira para a tela (Início, decisão 4 de 25/10/2026): '<1%' quando há pedidos mas o percentual
    arredondado dá 0 (o maior resto pode zerar 1 de 5.520); vazio sem percentual."""
    if pct is None:
        return ""
    return "<1%" if pct == 0 and n else f"{pct}%"


def mes(aaaa_mm: str) -> str:
    ano, m = aaaa_mm.split("-")
    return f"{MESES[int(m) - 1]}/{ano[2:]}"


FILTROS_JINJA = {
    "inteiro": inteiro,
    "decimal": decimal,
    "pct": pct,
    "variacao": variacao,
    "sentido": sentido,
    "dias_uteis": dias_uteis,
    "data_hora": data_hora,
    "quando": quando,
    "atualizado": atualizado,
    "recorte": recorte,
    "mes": mes,
    "parcela": parcela,
}
