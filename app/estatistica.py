"""Comparação de proporções entre dois períodos (D27, regra A8 do PRD).

Diferença de proporção é lida em pontos percentuais. Para saber se ela é maior que a oscilação natural, usa-se o teste
z de duas proporções com variância combinada (pooled), bilateral, a 95% (|z| ≥ 1,96):

    p1 = x1 / n1,  p2 = x2 / n2,  p = (x1 + x2) / (n1 + n2)
    erro padrão = √( p · (1 − p) · (1/n1 + 1/n2) )
    z = (p1 − p2) / erro padrão

Na tela, a diferença em pontos é a dos percentuais já arredondados (`pontos_tela` = arred(p1·100) − arred(p2·100), meio
para cima), para bater com os números escritos ao lado (como a C8 do SLA); `pontos` guarda o valor exato.

Só vale para proporções verdadeiras (parte de um todo, entre 0 e 1): parcela de um tipo nas entradas, parcela entregue
no próprio mês. Não vale para razões que podem passar de 100% (ex.: cobertura = entregas ÷ entradas).
"""

import math

Z_95 = 1.96


def pontos_tela(atual: float, anterior: float) -> int:
    """Diferença entre os percentuais arredondados (meio para cima) que aparecem escritos na tela."""
    return math.floor(atual * 100 + 0.5) - math.floor(anterior * 100 + 0.5)


def diferenca(x1: int, n1: int, x2: int, n2: int) -> dict | None:
    """Período atual (x1 de n1) contra o anterior (x2 de n2). None se algum período não tem base."""
    if not n1 or not n2:
        return None
    p1, p2 = x1 / n1, x2 / n2
    p = (x1 + x2) / (n1 + n2)
    erro = math.sqrt(p * (1 - p) * (1 / n1 + 1 / n2))
    z = (p1 - p2) / erro if erro else 0.0
    return {"atual": p1, "anterior": p2, "pontos": (p1 - p2) * 100, "pontos_tela": pontos_tela(p1, p2), "z": z,
            "relevante": abs(z) >= Z_95}
