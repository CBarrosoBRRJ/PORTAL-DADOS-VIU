"""Checagem única antes da reunião (batalha 2, G1-engenharia-1, 26/10/2026). Somente leitura.

Junta num passo só o que antes estava em cinco rotinas manuais. Rodar no computador do Caio, com o servidor local no ar
e as credenciais ADC do gcloud-viu, na véspera (27/10) e na manhã da reunião (28/10):

  python tools/checar_reuniao.py [--site http://127.0.0.1:8096] [--sem-estudo] [--output arquivo.json | -]

Grava o registro do que foi conferido em docs/validacao/reuniao_AAAA-MM-DD.json (rastreabilidade da carga da reunião).

O que confere (saída 0 = tudo certo; 1 = algum problema, listado):
1. Identidade e projeto: SESSION_USER() = caio.barroso@viu.com.br no projeto gglobo-viu-dados-hdg-prd, antes de cada
   consulta; só SELECT (dry-run confere o tipo), com teto de bytes e os rótulos do projeto.
2. Carga: MAX(_processado_em) das três golds (SLA, entradas, fluxo) no mesmo dia; e o site (/saude) com todas as tabelas
   carregadas, em dia ou congeladas (sem "base atrasada" nem falha de leitura) e com o mesmo _processado_em do banco.
3. Início: Q1 (sanidade) e Q2 (fila dos 6 meses do extrato) da ficha docs/paginas/inicio.md, seção 6.4, com o fim na
   véspera da carga (CAST(NULL AS DATE)); qualquer alarme listado lá falha.
4. Estudo "Como medimos": tools/conferir_estudo.py nos 3 grupos (a menos de --sem-estudo), gravando
   docs/validacao/estudo_AAAA-MM-DD.json.
5. Previsão: ml/saida/previsao.json válido, com o acompanhamento da mesma carga da gold de entradas e o retrato do último
   mês fechado pela regra E3 (app/corte.py).

Não contém DDL/DML, não publica nada e não usa serviços de IA.
"""
import argparse
import json
import subprocess
import sys
import urllib.request
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import pandas as pd  # noqa: E402
from google.cloud import bigquery  # noqa: E402

from app import config, corte  # noqa: E402

IDENTIDADE = "caio.barroso@viu.com.br"
PROJETO = "gglobo-viu-dados-hdg-prd"
TETO = 200 * 1024**2

Q1 = """
WITH
ent AS (SELECT * FROM `{ent}`),
flu AS (SELECT * FROM `{flu}`),
p AS (
  SELECT
    (SELECT DATE(MAX(_processado_em), 'America/Sao_Paulo') FROM ent) AS d_entrada,
    (SELECT DATE(MAX(_processado_em), 'America/Sao_Paulo') FROM flu) AS d_fluxo,
    COALESCE(CAST(NULL AS DATE),
             (SELECT DATE_SUB(DATE(MAX(_processado_em), 'America/Sao_Paulo'), INTERVAL 1 DAY) FROM ent)) AS fim),
q AS (SELECT *, EXTRACT(YEAR FROM fim) AS a FROM p),
ent_mes AS (SELECT DATE_TRUNC(e.data, MONTH) AS m, SUM(e.quantidade + e.quantidade_estimada) AS n
            FROM ent e, q WHERE EXTRACT(YEAR FROM e.data) = q.a GROUP BY 1),
flu_mes AS (SELECT f.mes_entrada AS m, SUM(f.quantidade) AS n FROM flu f, q WHERE EXTRACT(YEAR FROM f.mes_entrada) = q.a GROUP BY 1)
SELECT
  q.fim, q.d_entrada, q.d_fluxo,
  q.d_entrada = q.d_fluxo AS ok_mesma_carga,
  DATE_SUB(q.d_entrada, INTERVAL 1 DAY) = q.fim AS ok_fim_e_vespera,
  (SELECT MAX(data) FROM ent) <= q.fim AS ok_sem_data_futura,
  (SELECT COUNTIF(grupo_input IS NULL OR grupo_input NOT IN ('Mercado','Inbound','Proativo','Internos','Sem tipo')) FROM ent) AS linhas_tipo_fora_lista,
  (SELECT COUNTIF(IFNULL(quantidade,0) + IFNULL(quantidade_estimada,0) <> IFNULL(entregue_no_mes,0) + IFNULL(entregue_depois,0)
                  + IFNULL(nao_seguiu,0) + IFNULL(em_andamento,0)) FROM ent) AS linhas_situacao_nao_fecha,
  (SELECT COUNT(*) FROM ent_mes FULL JOIN flu_mes USING (m) WHERE IFNULL(ent_mes.n,-1) <> IFNULL(flu_mes.n,-1)) AS meses_safra_divergente,
  (SELECT COUNTIF(evento <> 'em_andamento' AND mes_evento < mes_entrada) FROM flu) AS eventos_antes_da_entrada,
  (SELECT SUM(quantidade + quantidade_estimada) FROM ent e WHERE e.data BETWEEN DATE(q.a,1,1) AND q.fim) AS total_ano,
  (SELECT IFNULL(SUM(quantidade),0) FROM flu f WHERE evento = 'nao_seguiu' AND mes_evento IS NULL
          AND EXTRACT(YEAR FROM f.mes_entrada) = q.a) AS nao_seguiu_sem_data_ano
FROM q
"""

Q2 = """
WITH
p AS (SELECT COALESCE(CAST(NULL AS DATE),
        (SELECT DATE_SUB(DATE(MAX(_processado_em), 'America/Sao_Paulo'), INTERVAL 1 DAY) FROM `{ent}`)) AS fim),
f AS (SELECT * FROM `{flu}`),
meses AS (SELECT m FROM (SELECT DISTINCT f.mes_entrada AS m FROM f, p WHERE f.quantidade > 0 AND f.mes_entrada <= p.fim)
          ORDER BY m DESC LIMIT 6),
x AS (
  SELECT m,
    SUM(IF(mes_entrada < m AND (evento='em_andamento' OR mes_evento >= m), quantidade, 0)) represados,
    SUM(IF(mes_entrada = m, quantidade, 0)) novos,
    SUM(IF(evento='entregue' AND mes_evento=m AND mes_entrada=m, quantidade, 0)) entregues_novos,
    SUM(IF(evento='entregue' AND mes_evento=m AND mes_entrada<m, quantidade, 0)) entregues_represados,
    SUM(IF(evento='nao_seguiu' AND (mes_evento=m OR (mes_evento IS NULL AND mes_entrada=m)), quantidade, 0)) nao_seguiram,
    SUM(IF(evento='em_andamento' OR mes_evento>m, quantidade, 0)) seguem
  FROM meses JOIN f ON EXTRACT(YEAR FROM f.mes_entrada) = EXTRACT(YEAR FROM m) AND f.mes_entrada <= m
  GROUP BY m)
SELECT m, represados+novos = entregues_novos+entregues_represados+nao_seguiram+seguem AS ok_fecha,
  represados = LAG(seguem) OVER (ORDER BY m) AS ok_encadeia
FROM x ORDER BY m
"""

CARGAS = """
SELECT 'sla' AS t, MAX(_processado_em) AS p FROM `{sla}`
UNION ALL SELECT 'entrada', MAX(_processado_em) FROM `{ent}`
UNION ALL SELECT 'fluxo', MAX(_processado_em) FROM `{flu}`
"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--site", default="http://127.0.0.1:8096")
    ap.add_argument("--sem-estudo", action="store_true", help="pula o tools/conferir_estudo.py (mais demorado)")
    ap.add_argument("--output", default=None,
                    help="registro JSON (padrão docs/validacao/reuniao_AAAA-MM-DD.json; '-' não grava)")
    args = ap.parse_args()
    problemas: list[str] = []
    registro: list[dict] = []  # tudo o que foi conferido, para docs/validacao/reuniao_AAAA-MM-DD.json (G2-14)

    def ok(msg):
        registro.append({"resultado": "OK", "item": msg})
        print(f"OK    {msg}", flush=True)

    def falha(msg):
        problemas.append(msg)
        registro.append({"resultado": "FALHA", "item": msg})
        print(f"FALHA {msg}", flush=True)

    client = bigquery.Client(project=config.PROJETO)

    def identidade():
        email = list(client.query("SELECT SESSION_USER()").result())[0][0]
        if email != IDENTIDADE or client.project != PROJETO:
            raise RuntimeError("Identidade ou projeto corporativo divergente; operação interrompida.")
        return email

    def consulta(sql):
        identidade()
        dry = client.query(sql, job_config=bigquery.QueryJobConfig(dry_run=True, use_query_cache=False))
        if dry.statement_type != "SELECT":
            raise RuntimeError(f"Consulta não é SELECT ({dry.statement_type}); interrompida.")
        if dry.total_bytes_processed > TETO:
            raise RuntimeError("Consulta acima do teto de bytes; revisar antes de executar.")
        job = client.query(sql, job_config=bigquery.QueryJobConfig(maximum_bytes_billed=TETO, labels=config.LABELS))
        return job.to_dataframe(create_bqstorage_client=False)

    ok(f"identidade {identidade()} · projeto {client.project}")
    tabs = {"sla": config.TAB_SLA, "ent": config.TAB_ENTRADA, "flu": config.TAB_FLUXO}

    # 2) carga: as três golds no mesmo dia; o site com a mesma carga
    cargas = consulta(CARGAS.format(**tabs)).set_index("t")["p"]
    dias = {t: corte.dia_da_carga(v) for t, v in cargas.items()}
    (ok if len(set(dias.values())) == 1 else falha)(f"golds no mesmo dia de carga: {dias}")
    try:
        with urllib.request.urlopen(f"{args.site.rstrip('/')}/saude", timeout=30) as r:
            saude = json.loads(r.read().decode("utf-8"))
        estados = {t: s.get("estado") for t, s in saude["tabelas"].items()}
        (ok if saude.get("dados_prontos") else falha)("site com todas as tabelas carregadas (/saude dados_prontos)")
        ruins = {t: e for t, e in estados.items() if e not in ("em_dia", "congelada")}
        (ok if not ruins else falha)(f"site sem aviso de atraso ou falha: {estados}")
        for chave, t in (("sla", "sla"), ("entrada", "entrada"), ("fluxo", "fluxo")):
            site = saude["tabelas"].get(chave, {}).get("processado_em")
            mesma = site is not None and pd.Timestamp(site) == pd.Timestamp(cargas[t])
            (ok if mesma else falha)(f"site × banco na mesma carga ({chave}): site {site} · banco {cargas[t]}")
    except OSError as e:
        falha(f"site fora do ar em {args.site} ({e}); suba o servidor local antes de conferir")

    # 3) Início: Q1 e Q2 (ficha inicio.md 6.4)
    q1 = consulta(Q1.format(**tabs)).iloc[0]
    oks = [c for c in q1.index if c.startswith("ok_")]
    (ok if all(bool(q1[c]) for c in oks) else falha)("Q1 " + ", ".join(f"{c}={bool(q1[c])}" for c in oks))
    for c in ("linhas_tipo_fora_lista", "linhas_situacao_nao_fecha", "meses_safra_divergente", "eventos_antes_da_entrada"):
        (ok if int(q1[c]) == 0 else falha)(f"Q1 {c} = {int(q1[c])}")
    print(f"      Q1 fim {q1['fim']} · total do ano {int(q1['total_ano'])} · 'não seguiu' sem data {int(q1['nao_seguiu_sem_data_ano'])}"
          " (comparar com o dia anterior: não pode cair o total nem subir o sem data)")
    q2 = consulta(Q2.format(**tabs))
    (ok if q2["ok_fecha"].all() else falha)(f"Q2 ok_fecha em {len(q2)} meses")
    enc = q2.iloc[1:]
    enc = enc.loc[pd.to_datetime(enc["m"]).dt.month != 1]  # janeiro: fila do ano começa em 0, por desenho
    (ok if enc["ok_encadeia"].fillna(False).all() else falha)("Q2 ok_encadeia (fora de janeiro)")

    # 4) estudo nos 3 grupos
    if not args.sem_estudo:
        saida = RAIZ / "docs" / "validacao" / f"estudo_{date.today():%Y-%m-%d}.json"
        r = subprocess.run([sys.executable, str(RAIZ / "tools" / "conferir_estudo.py"), "--output", str(saida)], cwd=RAIZ)
        (ok if r.returncode == 0 else falha)(f"estudo 'Como medimos' nos 3 grupos ({saida.name})")

    # 5) previsão: mesma carga e retrato do último mês fechado (E3)
    try:
        p = json.loads(Path(config.PREVISAO_ARQ).read_text(encoding="utf-8"))
        # o retrato é do fechamento do mês (carga daquele dia); o acompanhamento do mês em andamento segue a carga do dia
        dia_prev = corte.dia_da_carga((p.get("acompanhamento") or {}).get("processado_em") or p["carga"]["processado_em"])
        (ok if dia_prev == dias.get("entrada") else falha)(
            f"previsão (acompanhamento) na mesma carga da gold de entradas: previsão {dia_prev} · gold {dias.get('entrada')}"
            + ("" if dia_prev == dias.get("entrada") else " (rodar python -m ml.rodar --acompanhamento)"))
        esperado = corte.mes_fechado(corte.fim(cargas["entrada"]))
        (ok if p["retrato"]["mes_fechado"] == esperado else falha)(
            f"retrato da previsão = último mês fechado: {p['retrato']['mes_fechado']} · esperado {esperado}")
    except (OSError, ValueError, KeyError) as e:
        falha(f"previsao.json ausente ou inválido ({type(e).__name__}: {e})")

    print("\n" + ("TUDO CERTO para a reunião." if not problemas else f"{len(problemas)} problema(s): revisar antes de apresentar."))
    if args.output != "-":
        saida = Path(args.output) if args.output else RAIZ / "docs" / "validacao" / f"reuniao_{date.today():%Y-%m-%d}.json"
        saida.parent.mkdir(parents=True, exist_ok=True)
        saida.write_text(json.dumps({
            "data": pd.Timestamp.now(tz="America/Sao_Paulo").isoformat(),
            "projeto": client.project,
            "cargas": {t: str(v) for t, v in cargas.items()},
            "inicio_q1": {"fim": str(q1["fim"]), "total_ano": int(q1["total_ano"]),
                          "nao_seguiu_sem_data_ano": int(q1["nao_seguiu_sem_data_ano"])},
            "resultado": "tudo certo" if not problemas else f"{len(problemas)} problema(s)",
            "itens": registro,
        }, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Registro gravado em {saida}")
    return 1 if problemas else 0


if __name__ == "__main__":
    sys.exit(main())
