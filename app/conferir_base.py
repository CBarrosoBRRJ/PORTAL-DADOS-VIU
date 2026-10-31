"""Conferência do pacote da reunião SEM rede (F01, auditoria do Codex, 31/10/2026): roda no build da imagem.

    python -m app.conferir_base

Com o corte ligado (CORTE_DADOS, padrão 2026-10-31), exige a base congelada completa e coerente com o manifesto
(app/congelamento.py, B4), cada tabela dentro do contrato de colunas, a Previsão do mês fechado e da mesma carga da base
(F03) e a LIA até o corte. Saída 1 = o build para (`RUN` no Dockerfile); o arranque em produção confere a base de novo
(`congelamento.exigir`). Corte desligado: nada a exigir, saída 0. O BigQuery nunca é consultado.
Mesma conferência, com a tabela por tabela: `python tools/congelar_base.py --conferir` (no computador).
"""

import sys

from app import config, congelamento, dados


def _sem_bigquery():
    raise RuntimeError("conferência do pacote: o BigQuery não é consultado (a base precisa estar inteira nos arquivos)")


def main() -> int:
    dados.cliente = _sem_bigquery
    if not congelamento.ligado():
        print("Corte desligado (CORTE_DADOS=off): nada a conferir.")
        return 0
    m, problemas = congelamento.conferir_pacote()
    print(f"Corte {config.CORTE_DADOS:%d/%m/%Y} (folga {config.CORTE_FOLGA_DIAS} dia) · pasta {congelamento.pasta()}")
    if problemas:
        print("PACOTE REPROVADO:")
        for p in problemas:
            print(" -", p)
        return 1
    print(f"Pacote conferido: {len(m['tabelas'])} tabelas da versão {m['pasta']} (dados até {m['fim']}), Previsão da mesma "
          "carga e LIA até o corte.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
