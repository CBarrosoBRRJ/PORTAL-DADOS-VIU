"""Textos de variação para relatório vivo (E8, E9, A7): sinal e frase saem do percentual já arredondado."""

import pytest

from app import formato


@pytest.mark.parametrize("valor, texto, sentido", [
    (0.91, "+91%", "alta"),
    (-0.13, "−13%", "queda"),       # sinal de menos tipográfico
    (0.003, "0%", "igual"),         # antes: "+0%"
    (-0.004, "0%", "igual"),        # antes: "-0%"
    (0.005, "+1%", "alta"),         # meio para cima
    (-0.005, "−1%", "queda"),
    (24.67, "+2.467%", "alta"),     # milhar com ponto
    (0.0, "0%", "igual"),
    (None, "—", None),
])
def test_variacao_e_sentido(valor, texto, sentido):
    assert formato.variacao(valor) == texto
    assert formato.sentido(valor) == sentido


def test_variacao_sem_sinal():
    assert formato.variacao(-0.13, False) == "13%" and formato.variacao(0.91, False) == "91%"


def test_frase_de_queda_e_igual():
    from jinja2 import Environment, FileSystemLoader

    amb = Environment(loader=FileSystemLoader("app/templates"))
    amb.filters.update(formato.FILTROS_JINJA)
    macro = amb.get_template("macros.html").module.comparacao_ano
    assert "13%</strong>" in str(macro(-0.13, 3000, 2025)) and "a menos que em 2025" in str(macro(-0.13, 3000, 2025))
    assert "▼" in str(macro(-0.13, 3000, 2025))
    assert "igual a 2025" in str(macro(0.0, 3000, 2025)) and "praticamente" not in str(macro(0.0, 3000, 2025))
    assert "praticamente igual a 2025" in str(macro(0.003, 3000, 2025))
    sem = str(macro(None, 12, 2025))
    assert "Em 2025" in sem and "12 no mesmo período" in sem and "%" not in sem
