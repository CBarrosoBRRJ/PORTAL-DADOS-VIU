"""Gera o espelho dos dados para a VPS temporária (D66b, 31/10/2026): um parquet por tabela + espelho.json.

    python tools/gerar_espelho.py [pasta]        (padrão: espelho/)

Só leitura no GCP (as mesmas consultas do site, com as credenciais do computador). A VPS recebe só estes arquivos e lê
com ESPELHO_DIR=<pasta>, sem credencial e sem BigQuery. Os arquivos têm dados internos: ficam fora do Cloud Run
(.gcloudignore) e fora do ramo principal do GitHub; apagar a pasta quando a VPS sair do ar.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from app import config, congelamento, dados  # noqa: E402


def main() -> int:
    destino = Path(sys.argv[1]) if len(sys.argv) > 1 else RAIZ / "espelho"
    destino.mkdir(parents=True, exist_ok=True)
    fichas = {}
    for t in dados.TABELAS.values():
        df = t.df().copy()
        df.attrs = {}
        nome = congelamento.nome(t)
        df.to_parquet(destino / f"{nome}.parquet", index=False)
        fichas[nome] = {"tabela": t.id_tabela, "linhas": int(len(df)),
                        "modificada_em": t.modificada_em.isoformat() if t.modificada_em else None}
        print(f"{nome}: {len(df)} linhas")
    (destino / "espelho.json").write_text(json.dumps(
        {"gerado_em": datetime.now(config.FUSO).isoformat(timespec="seconds"), "tabelas": fichas},
        ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Espelho em {destino}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
