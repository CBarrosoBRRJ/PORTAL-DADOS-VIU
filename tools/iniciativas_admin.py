"""Administração do quadro das Iniciativas no computador (backend SQLite). Só local; nada de GCP.

Uso (no venv, dentro da V2):
    python tools/iniciativas_admin.py backup                 # cópia consistente do banco + anexos num .zip
    python tools/iniciativas_admin.py backup --destino D:/x  # outra pasta (padrão: ~/.ppd-agenciamento-v2/backups)
    python tools/iniciativas_admin.py resumo                 # quantas iniciativas e anexos, e onde estão
    python tools/iniciativas_admin.py restaurar-catalogo --confirmo-restaurar
        # volta o quadro ao catalogo.py (os incluídos ficam excluídos, logicamente); faz um backup antes

O backup usa a API de backup do SQLite (cópia consistente mesmo com o servidor rodando) e junta a pasta de anexos.
Para voltar um backup: pare o servidor, descompacte iniciativas.db e anexos/ nos caminhos de INICIATIVAS_DB e
INICIATIVAS_ANEXOS, e suba o servidor de novo. Em produção (Firestore + bucket), ver docs/deploy_iniciativas.md.
"""

import argparse
import os
import sqlite3
import sys
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ.setdefault("AUTH", "off")

from app import config  # noqa: E402
from app.apresentacoes.gestao_orcamentos.iniciativas import repositorio  # noqa: E402


def backup(destino: Path | None = None) -> Path:
    if config.INICIATIVAS_BACKEND != "sqlite":
        raise SystemExit("Backup local só com INICIATIVAS_BACKEND=sqlite (produção: ver docs/deploy_iniciativas.md).")
    if not config.INICIATIVAS_DB.exists():
        raise SystemExit(f"Banco não encontrado: {config.INICIATIVAS_DB}")
    destino = Path(destino or config.INICIATIVAS_DB.parent / "backups")
    destino.mkdir(parents=True, exist_ok=True)
    arq = destino / f"iniciativas_{datetime.now():%Y%m%d-%H%M%S}.zip"
    with tempfile.TemporaryDirectory() as tmp:
        copia = Path(tmp) / "iniciativas.db"
        origem = sqlite3.connect(config.INICIATIVAS_DB)
        alvo = sqlite3.connect(copia)
        with alvo:
            origem.backup(alvo)
        origem.close()
        alvo.close()
        with zipfile.ZipFile(arq, "w", zipfile.ZIP_DEFLATED) as z:
            z.write(copia, "iniciativas.db")
            if config.INICIATIVAS_ANEXOS.exists():
                for f in sorted(config.INICIATIVAS_ANEXOS.iterdir()):
                    if f.is_file():
                        z.write(f, f"anexos/{f.name}")
    return arq


def resumo() -> None:
    q = repositorio.quadro()
    itens, anexos = q.listar(), q.anexos()
    print(f"backend: {config.INICIATIVAS_BACKEND}")
    print(f"banco: {config.INICIATIVAS_DB}")
    print(f"anexos: {config.INICIATIVAS_ANEXOS}")
    print(f"iniciativas na tela: {len(itens)}; anexos: {len(anexos)}; na semente: {q.na_semente()}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="acao", required=True)
    b = sub.add_parser("backup")
    b.add_argument("--destino", type=Path)
    sub.add_parser("resumo")
    r = sub.add_parser("restaurar-catalogo")
    r.add_argument("--confirmo-restaurar", action="store_true", help="obrigatório: confirma que quer desfazer as edições")
    a = ap.parse_args()
    if a.acao == "backup":
        print(f"backup gravado: {backup(a.destino)}")
    elif a.acao == "resumo":
        resumo()
    else:
        if not a.confirmo_restaurar:
            raise SystemExit("Recusado: use --confirmo-restaurar (as edições feitas na tela deixam de aparecer).")
        print(f"backup antes de restaurar: {backup()}")
        repositorio.quadro().restaurar_semente()
        print("quadro restaurado ao catálogo (catalogo.py).")


if __name__ == "__main__":
    main()
