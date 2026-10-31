"""Orçamentos da ViU Agenciamento. O endereço da área (slug) vem daqui; a pasta continua gestao_orcamentos.

Caio, 31/10/2026: /gestao-orcamentos/... virou /viu-agenciamento/...; o endereço antigo responde 301 (308 para
métodos que não são GET/HEAD) para o novo, pela rota genérica em app/main.py.
"""

SLUG = "viu-agenciamento"
SLUG_ANTIGO = "gestao-orcamentos"  # só para o redirecionamento dos endereços antigos


def endereco_atual(href: str) -> str:
    """Link interno gravado antes de 31/10/2026 (ex.: o "Ver resultados" da LIA na semente das Iniciativas, já salvo no
    quadro) -> o mesmo link no endereço novo. Outros links passam como vieram."""
    antigo = f"/{SLUG_ANTIGO}"
    if href == antigo or href.startswith((f"{antigo}/", f"{antigo}#", f"{antigo}?")):
        return f"/{SLUG}{href[len(antigo):]}"
    return href
