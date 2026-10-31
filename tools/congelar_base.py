"""Gera, confere e recupera a base congelada do corte (D65; regras K1–K7 e B1–B5 em app/congelamento.py).

Só leitura no GCP: SELECT nas tabelas e views do gold_monday (as mesmas colunas do site) e o metadado `modified`. Grava
em app/base_congelada/ (BASE_CONGELADA_DIR) o CONJUNTO das tabelas, como unidade: uma pasta de versão com um parquet por
tabela e o `manifesto.json` (corte, carga, tabelas, sha256), publicado por último e de forma atômica. Entra na imagem.

  python tools/congelar_base.py              gera a base (todas as tabelas na carga do corte) ou, se já existe, confere
  python tools/congelar_base.py --conferir   só lê os arquivos, SEM BigQuery (o que o Cloud Run vai ver; --sem-rede é
                                             sinônimo); confere também a Previsão (retrato do mês do corte, retrato e
                                             acompanhamento da mesma carga da base) e a LIA (fim)
  python tools/congelar_base.py --recuperar  sem manifesto válido, publica a versão completa mais nova (gravação
                                             interrompida); relata as pastas parciais

Saída 0 = tudo certo. Com o corte desligado (CORTE_DADOS=off), não faz nada. A mesma conferência roda no build da
imagem (`python -m app.conferir_base`). Roteiro do dia 02/11/2026: docs/congelar_outubro.md.
"""

import argparse
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

import pandas as pd  # noqa: E402

from app import config, congelamento, dados  # noqa: E402


def _sem_bigquery():
    raise RuntimeError("--conferir: o BigQuery não é consultado (a base precisa estar inteira nos arquivos)")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--conferir", action="store_true", help="só os arquivos, sem BigQuery; confere Previsão e LIA")
    ap.add_argument("--sem-rede", action="store_true", help="o mesmo que --conferir")
    ap.add_argument("--recuperar", action="store_true", help="publica a versão completa mais nova (B5)")
    args = ap.parse_args()
    conferir = args.conferir or args.sem_rede
    if not congelamento.ligado():
        print("Corte desligado (CORTE_DADOS=off): nada a fazer.")
        return 0
    print(f"Corte {config.CORTE_DADOS:%d/%m/%Y} (folga {config.CORTE_FOLGA_DIAS} dia) · pasta {congelamento.pasta()}")
    if args.recuperar:
        try:
            relato = congelamento.recuperar()
        except congelamento.BaseInvalida as e:
            print("NÃO RECUPERADA:")
            for linha in str(e).split(" | "):
                print(" -", linha)
            return 1
        for linha in relato:
            print(" -", linha)
        conferir = True  # depois de publicar, confere o pacote inteiro
    if conferir:
        dados.cliente = _sem_bigquery
    linhas, problemas, fins = [], [], set()
    for chave, t in dados.TABELAS.items():
        t.em_fundo = False
        try:
            df = t.df()
        except dados.DadosIndisponiveis as e:
            problemas.append(f"{chave}: sem base ({e})"[:300])
            linhas.append((chave, "—", "—", "—", "FALTA"))
            continue
        fim = congelamento.fim_da_carga(df)
        proc = t.processado_em()
        fins.add(fim)
        situacao = "congelada" if t.congelada else ("IGNORADA: " + t.erro if t.erro else "NÃO congelada")
        linhas.append((chave, f"{fim:%d/%m/%Y}" if fim else "—", f"{proc:%d/%m %H:%M}" if proc else "—", len(df),
                       situacao[:90]))
        if not t.congelada:
            problemas.append(f"{chave}: carga com dados até {fim} não congelou ({t.erro or 'fim antes do corte'})")
    print(f"\n{'tabela':22s} {'dados até':10s} {'processada':12s} {'linhas':>7s}  situação")
    for chave, fim, proc, n, sit in linhas:
        print(f"{chave:22s} {fim:10s} {proc:12s} {str(n):>7s}  {sit}")
    if len(fins) > 1:
        problemas.append(f"tabelas de cargas diferentes: {sorted(str(f) for f in fins)}")
    if not problemas and not conferir:
        # B1: todas congelaram em memória; a gravação acontece sozinha, mas aqui ela é exigida (e retentada uma vez)
        if not (congelamento.persistir(forcar=True) or congelamento.persistir(forcar=True)):
            problemas.append(f"base congelada em memória, mas NÃO gravada: {congelamento.situacao().get('erro_gravacao')}")
    m = None
    if not problemas:
        m, extra = congelamento.conferir_pacote() if conferir else (congelamento.validar(usar_cache=False), [])
        problemas += extra
    print()
    if problemas:
        print("ATENÇÃO:")
        for p in problemas:
            print(" -", p)
        return 1
    print(f"Tudo certo: {len(linhas)} tabelas congeladas na versão {m['pasta']} (dados até {m['fim']}, carga processada "
          f"em {pd.Timestamp(m['processado_em']).tz_convert(config.FUSO):%d/%m/%Y %H:%M}).")
    pasta_versao = congelamento.pasta() / m["pasta"]
    print(f"Arquivos: {sum(f.stat().st_size for f in pasta_versao.glob('*.parquet')) / 1e6:.1f} MB em parquet "
          f"em {pasta_versao}.")
    return 0


if __name__ == "__main__":
    pd.set_option("display.width", 160)
    sys.exit(main())
