"""D67 (Caio, 03/11/2026): folga do corte 1 → 2 dias. A carga congelada é a de 03/11 (dados até 02/11)."""

import importlib
from datetime import date

from app import config, congelamento


def test_folga_padrao_aceita_a_carga_de_03_11(monkeypatch):
    monkeypatch.delenv("CORTE_FOLGA_DIAS", raising=False)
    monkeypatch.delenv("CORTE_DADOS", raising=False)
    try:
        importlib.reload(config)
        assert config.CORTE_FOLGA_DIAS == 2
        assert config.CORTE_DADOS == date(2026, 10, 31)
        assert congelamento.limite() == date(2026, 11, 2)
    finally:
        monkeypatch.undo()
        importlib.reload(config)
