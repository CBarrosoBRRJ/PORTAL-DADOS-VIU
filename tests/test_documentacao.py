"""Rastreabilidade da documentação (batalha 2, G4-N14 item 4, 26/10/2026).

A ficha docs/paginas/o_que_falta.md copia a tabela de PENDENCIAS; o código é a fonte. Este teste falha quando um código
PDxx existe só num dos dois lados, ou quando a ordem diverge, para a ficha não voltar a ficar atrás do código.
"""
import re
from pathlib import Path

from app.apresentacoes.gestao_orcamentos.pendencias import PEDIDOS, PENDENCIAS

RAIZ = Path(__file__).resolve().parents[1]
FICHA = RAIZ / "docs" / "paginas" / "o_que_falta.md"


def _secao(texto: str, titulo: str) -> str:
    ini = texto.index(titulo)
    fim = texto.find("\n## ", ini + len(titulo))
    return texto[ini: fim if fim != -1 else None]


def test_o_que_falta_md_igual_a_pendencias():
    texto = FICHA.read_text(encoding="utf-8")
    tabela = _secao(texto, "## 3. Pendências no código")
    na_ficha = re.findall(r"^\| (PD\d+[a-z]?) \|", tabela, flags=re.M)
    assert na_ficha == [p.codigo for p in PENDENCIAS]


def test_o_que_falta_md_com_os_pedidos_do_codigo():
    texto = FICHA.read_text(encoding="utf-8")
    pedidos = _secao(texto, "## 4. Pedidos de decisão")
    for titulo, _, quem in PEDIDOS:
        assert f"| {titulo} |" in pedidos and quem in pedidos
