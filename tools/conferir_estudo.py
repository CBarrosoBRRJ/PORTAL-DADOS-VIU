"""Conferência somente leitura do estudo "Como medimos" (V2, 30/10/2026: slides 2–5) contra o BigQuery (batalha de agentes,
25/10/2026: B-N8 e A-N12).

O que faz:
1. Confirma a identidade (SESSION_USER = caio.barroso@viu.com.br) e o projeto antes de cada consulta; só SELECT, com
   teto de bytes e rótulos do projeto (como tools/checar_reuniao.py).
2. Refaz no banco, por um caminho independente do site, as horas úteis da equipe (sem almoço, sem Retorno Marca) de cada
   orçamento e status antes da 1ª entrega: o expediente e os feriados vêm de `app.expediente` (não fixos na SQL), e o
   mês parcial vem do MAX(_processado_em) em São Paulo (nada de '2026-09' escrito à mão).
3. Agrega em pandas, sem as funções do site, e compara com `montar_estudo_sla` nos 3 grupos: n, típico, A/B, HB, típico de cada lado de 2 dias (V9), B e
   pedidos de cada mês, % do tempo travado de cada status, B de cada Tipo de Input e pedidos acima de 5 dias. Contagens
   batem exatas; % aceitam só a diferença de arredondamento (o site escreve inteiros que somam 100).
4. Guarda as leituras do estudo (títulos, faixas do pé e achados) e, com --anterior, avisa o que mudou desde a última
   conferência (ex.: "dois pontos" virou "um ponto").

Uso (no computador do Caio, com as credenciais ADC do gcloud-viu):
  python tools/conferir_estudo.py --output docs/validacao/estudo_AAAA-MM-DD.json [--anterior docs/validacao/estudo_….json]
Saída 0 = tudo bate; 1 = alguma diferença (listada). Rodar na véspera da apresentação, na manhã da reunião e a cada carga
(junto da Q1/Q2 do Início). Não contém DDL/DML e não usa serviços de IA.
"""
import argparse
import json
import math
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd  # noqa: E402
from google.cloud import bigquery  # noqa: E402

from app import config, dados, sla  # noqa: E402
from app.expediente import SEM_ALMOCO, sem_expediente  # noqa: E402

IDENTIDADE = "caio.barroso@viu.com.br"
TETO = 500 * 1024**2  # bytes por consulta
GRUPOS = {"todos": None, "exclusivos": True, "nao-exclusivos": False}

SQL_HORAS = """
WITH m AS (SELECT projeto_id, passo, status, fase, entrada, saida, exclusivo, nome_projeto, tipo_de_input
           FROM `{tabela}`),
parcial AS (SELECT FORMAT_TIMESTAMP('%Y-%m', MAX(_processado_em), 'America/Sao_Paulo') p FROM `{tabela}`),
ini AS (SELECT projeto_id, exclusivo, tipo_de_input, nome_projeto FROM m WHERE passo = 1),
pronto AS (SELECT projeto_id, ARRAY_AGG(STRUCT(passo, entrada) ORDER BY passo LIMIT 1)[OFFSET(0)] p
           FROM m WHERE fase = 'cliente' GROUP BY 1),
base AS (SELECT i.*, pr.p.passo pp, FORMAT_DATETIME('%Y-%m', pr.p.entrada) mes
         FROM ini i JOIN pronto pr USING (projeto_id) WHERE pr.p.passo > 1),
eq AS (SELECT b.projeto_id, e.status, e.entrada, e.saida FROM base b JOIN m e ON e.projeto_id = b.projeto_id
         AND e.passo < b.pp AND e.fase = 'equipe' AND e.saida IS NOT NULL
         AND NOT STARTS_WITH(LOWER(e.status), 'em elaboração - retorno marca')),
us AS (SELECT projeto_id, status,
         SUM(GREATEST(0, DATETIME_DIFF(LEAST(saida, DATETIME(d, TIME(j.h1, 0, 0))),
                                       GREATEST(entrada, DATETIME(d, TIME(j.h0, 0, 0))), MICROSECOND))) us
       FROM eq, UNNEST(GENERATE_DATE_ARRAY(DATE(entrada), DATE(saida))) d, UNNEST([{janelas}]) j
       WHERE EXTRACT(DAYOFWEEK FROM d) BETWEEN 2 AND 6 AND d NOT IN UNNEST(@feriados) GROUP BY 1, 2),
st AS (SELECT t.projeto_id, t.status, IFNULL(us.us, 0) us
       FROM (SELECT DISTINCT projeto_id, status FROM eq) t LEFT JOIN us USING (projeto_id, status))
SELECT b.projeto_id, b.mes, b.exclusivo, b.tipo_de_input, b.nome_projeto, st.status, st.us, (SELECT p FROM parcial) parcial
FROM base b LEFT JOIN st USING (projeto_id)
WHERE b.mes >= CONCAT(SUBSTR((SELECT p FROM parcial), 1, 4), '-01') AND b.mes < (SELECT p FROM parcial)
"""


def pontos(fracao: float) -> int:
    return math.floor(fracao * 100 + 0.5)


def etapa_nome(status: str) -> tuple[str, str]:
    """Etapa e nome do status (mesma leitura da ficha 000000.5, escrita aqui de novo)."""
    s = " ".join(str(status).split())
    baixo = s.lower()
    if baixo == "entrada":
        return "Entrada", "Fila de entrada"
    for prefixo, etapa in (("em elaboração", "Elaboração"), ("em revisão", "Revisão")):
        if baixo.startswith(prefixo):
            resto = s[len(prefixo):].strip().lstrip("-–").strip()
            if resto.startswith("(") and resto.endswith(")"):
                resto = resto[1:-1].strip()
            return etapa, (resto[:1].upper() + resto[1:]) if resto else prefixo.capitalize()
    if baixo.startswith("em elabora"):
        return "Elaboração", s
    if baixo.startswith("em revis"):
        return "Revisão", s
    return "Outros status", s


def referencia(linhas: pd.DataFrame, grupo: str) -> dict:
    """Números do estudo refeitos só com as horas do banco."""
    proj = (linhas.groupby("projeto_id")
            .agg(mes=("mes", "first"), exclusivo=("exclusivo", "first"), tipo=("tipo_de_input", "first"),
                 us=("us", "sum"))
            .assign(h=lambda d: d["us"].fillna(0) / 3.6e9))
    if GRUPOS[grupo] is not None:
        proj = proj.loc[proj["exclusivo"].eq(GRUPOS[grupo])]
    h = proj["h"]
    n = len(h)
    r = {"n": n, "mediana_h": float(h.median()), "a_exato": float((h <= 16).mean()),
         "hb_exato": float(h[h > 16].sum() / h.sum()), "acima5": int((h > 40).sum()),
         # V9 (V2, 30/10/2026): típico (mediana exata) dos que saem em até 2 dias e dos que passam
         "tipico_a": float(h[h <= 16].median()) if (h <= 16).any() else None,
         "tipico_b": float(h[h > 16].median()) if (h > 16).any() else None}
    r["meses"] = {m: {"n": int(len(g)), "b_exato": float((g > 16).mean())} for m, g in proj.groupby("mes")["h"]}
    tipo = proj["tipo"].fillna("").map(lambda t: " ".join(str(t).split()).split(" (")[0] or "vazio")
    r["tipos"] = {t: {"n": int(len(g)), "b_exato": float((g > 16).mean())} for t, g in proj["h"].groupby(tipo)}
    st = linhas.loc[linhas["projeto_id"].isin(proj.index) & linhas["status"].notna()].copy()
    st[["etapa", "nome"]] = pd.DataFrame([etapa_nome(s) for s in st["status"]], index=st.index)
    po = st.groupby(["etapa", "nome", "projeto_id"])["us"].sum() / 3.6e9
    travado = {}
    for (etapa, nome), g in po.groupby(level=[0, 1]):
        q1, q3 = float(g.quantile(0.25)), float(g.quantile(0.75))
        lim = q3 + 1.5 * (q3 - q1)
        travado[f"{etapa}|{nome}"] = {"travaram": int((g > lim).sum()), "travado_h": float(g[g > lim].sum())}
    total = sum(v["travado_h"] for v in travado.values())
    for v in travado.values():
        v["pct_exato"] = v["travado_h"] / total if total else 0.0
    r["status"], r["travado_total_h"] = travado, total
    r["pct_horas_travado_exato"] = total / float(h.sum()) if h.sum() else 0.0
    return r


def comparar(site: dict, ref: dict, grupo: str) -> list[str]:
    """Diferenças entre o que o site mostra e a referência do banco (vazio = tudo bate)."""
    d = []

    def igual(nome, a, b):
        if a != b:
            d.append(f"{grupo}: {nome} site={a} banco={b}")

    def arred(nome, escrito, exato):  # o inteiro escrito precisa estar a menos de 1 ponto do exato
        if escrito is None or abs(escrito - 100 * exato) >= 1:
            d.append(f"{grupo}: {nome} site={escrito}% banco={100 * exato:.2f}%")

    t, x, tr, tp, z, me = (site.get(k) for k in ("tempo", "exploracao", "travas", "tipos", "conclusao", "meses_estudo"))
    igual("n (recorte)", site["recorte"]["n"] if site.get("recorte") else None, ref["n"])
    if x:
        igual("n (slide 2)", x["n"], ref["n"])
        if abs(x["mediana"] - ref["mediana_h"]) > 1e-6:
            d.append(f"{grupo}: típico site={x['mediana']:.6f} h banco={ref['mediana_h']:.6f} h")
    if t:
        igual("A = 100 − B", t["a"] + t["b"], 100)
        arred("A (em até 2 dias)", t["a"], ref["a_exato"])
        arred("HB", t["hb"], ref["hb_exato"])
        for lado in ("a", "b"):  # V9
            sv, rv = t.get(f"tipico_{lado}"), ref[f"tipico_{lado}"]
            if (sv is None) != (rv is None) or (sv is not None and abs(sv - rv) > 1e-6):
                d.append(f"{grupo}: típico {lado.upper()} site={sv} banco={rv}")
    if me:
        for m in me["meses"]:
            if m.get("vazio"):
                continue
            rm = ref["meses"].get(m["chave"], {"n": 0, "b_exato": 0.0})
            igual(f"pedidos de {m['chave']}", m["n"], rm["n"])
            if m["n"]:
                arred(f"B de {m['chave']}", m["b"], rm["b_exato"])
    if tr:
        for s in tr["status"]:
            rs = ref["status"].get(f"{s['etapa']}|{s['nome']}")
            if rs is None:
                d.append(f"{grupo}: status {s['nome']} não existe no banco")
                continue
            igual(f"travaram em {s['nome']}", s["travaram"], rs["travaram"])
            arred(f"% travado de {s['nome']}", s["pct"], rs["pct_exato"])
        if tr.get("pct_horas") is not None:
            arred("tempo travado ÷ todas as horas", tr["pct_horas"], ref["pct_horas_travado_exato"])
    if tp:
        for r in tp["linhas"]:
            rt = ref["tipos"].get(r["tipo"], {"n": 0, "b_exato": 0.0})
            igual(f"pedidos {r['tipo']}", r["n"], rt["n"])
            arred(f"B de {r['tipo']}", r["b"], rt["b_exato"])
    if z:
        igual("acima de 5 dias", z["n_acima5"], ref["acima5"])
    return d


def leituras(site: dict) -> dict:
    """Textos que dependem de limites (K7, J7, U7, Z4–Z6): mudam com a carga e precisam ser vistos antes da reunião."""
    pega = lambda k, c: (site.get(k) or {}).get(c)  # noqa: E731
    z = site.get("conclusao") or {}
    # V2 (30/10/2026): numeração nova — 2 (um passo, X10), 3 (quantidade × tempo, V10), 4 (mês), 5 (trava); o tipo de
    # pedido e a conclusão saíram da tela (seguem calculados; ficam aqui como registro)
    return {"slide2": pega("exploracao", "insight"), "slide3": pega("tempo", "resposta"),
            "slide4_titulo": pega("meses_estudo", "titulo"), "slide4": pega("meses_estudo", "rodape"),
            "slide5": pega("travas", "rodape"), "fora_tipo": pega("tipos", "rodape"),
            "fora_conclusao": [f"{a['titulo']} · {a['valor']}" for a in z.get("achados", [])]}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--anterior", type=Path, help="JSON de uma conferência anterior, para avisar leituras que mudaram")
    args = parser.parse_args()
    client = bigquery.Client(project=config.PROJETO)
    jobs = []

    def identidade():
        email = list(client.query("SELECT SESSION_USER()").result())[0][0]
        if email != IDENTIDADE or client.project != "gglobo-viu-dados-hdg-prd":
            raise RuntimeError("Identidade ou projeto corporativo divergente; operação interrompida.")
        return email

    def consulta(sql, params=()):
        identidade()
        cfg = lambda **kw: bigquery.QueryJobConfig(query_parameters=list(params), **kw)  # noqa: E731
        dry = client.query(sql, job_config=cfg(dry_run=True, use_query_cache=False))
        if dry.statement_type != "SELECT":
            raise RuntimeError(f"Consulta não é SELECT ({dry.statement_type}); interrompida.")
        if dry.total_bytes_processed > TETO:
            raise RuntimeError("Consulta acima do teto de bytes; revisar antes de executar.")
        job = client.query(sql, job_config=cfg(maximum_bytes_billed=TETO, labels=config.LABELS))
        df = job.to_dataframe(create_bqstorage_client=False)
        jobs.append({"id": job.job_id, "bytes": job.total_bytes_processed, "cache": job.cache_hit})
        return df

    email = identidade()
    # 1) a base que o site lê (mesmas colunas de app/dados.py)
    colunas = ", ".join(dict.fromkeys((*dados.sla.colunas, "_processado_em")))
    mov = consulta(f"SELECT {colunas} FROM `{dados.sla.id_tabela}`")
    mov.attrs["versao"] = f"conferencia-{pd.Timestamp.now(tz=config.FUSO).isoformat()}"
    parcial = sla.mes_parcial(mov)
    # 2) as horas pelo caminho independente (feriados de app.expediente para os anos da base)
    anos = range(int(pd.to_datetime(mov["entrada"]).min().year), int(parcial[:4]) + 1)
    feriados = sorted(d for a in anos for d in sem_expediente(a))
    janelas = ", ".join(f"STRUCT({int(a)} AS h0, {int(b)} AS h1)" for a, b in SEM_ALMOCO)  # expediente sem almoço (C2)
    linhas = consulta(SQL_HORAS.format(tabela=dados.sla.id_tabela, janelas=janelas),
                      [bigquery.ArrayQueryParameter("feriados", "DATE", feriados)])
    parcial_banco = str(linhas["parcial"].iloc[0]) if len(linhas) else None
    if parcial_banco != parcial:
        raise RuntimeError(f"Mês parcial diverge: site {parcial} × banco {parcial_banco}")
    from app.apresentacoes.gestao_orcamentos import apresentacao as ap

    rel = {"data": pd.Timestamp.now(tz=config.FUSO).isoformat(), "identidade": email, "projeto": client.project,
           "tabela": dados.sla.id_tabela, "processado_em": str(mov["_processado_em"].max()), "mes_parcial": parcial,
           "feriados": [str(d) for d in feriados if d.year == int(parcial[:4])], "jobs": jobs, "grupos": {}}
    diferencas = []
    for grupo in GRUPOS:
        site = ap._estudo_slides(mov, parcial, grupo)
        ref = referencia(linhas, grupo)
        dif = comparar(site, ref, grupo)
        diferencas += dif
        rel["grupos"][grupo] = {"n": ref["n"], "tipico_h": round(ref["mediana_h"], 4), "diferencas": dif,
                                "leituras": leituras(site)}
        print(f"{'OK  ' if not dif else 'DIFERENÇA'} {grupo}: n={ref['n']} típico={ref['mediana_h']:.3f} h"
              + "".join(f"\n    - {x}" for x in dif), flush=True)
    if args.anterior and args.anterior.exists():
        antes = json.loads(args.anterior.read_text(encoding="utf-8"))
        for grupo, g in rel["grupos"].items():
            velhas = antes.get("grupos", {}).get(grupo, {}).get("leituras", {})
            for chave, valor in g["leituras"].items():
                if chave in velhas and velhas[chave] != valor:
                    print(f"LEITURA MUDOU ({grupo}, {chave}):\n    antes: {velhas[chave]}\n    agora: {valor}", flush=True)
                    rel.setdefault("leituras_mudaram", []).append({"grupo": grupo, "chave": chave, "antes": velhas[chave],
                                                                   "agora": valor})
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(rel, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print(f"\nArquivo: {args.output}  ·  carga {rel['processado_em']}  ·  mês parcial {parcial}  ·  "
          f"{'TUDO BATE' if not diferencas else f'{len(diferencas)} diferença(s)'}")
    sys.exit(1 if diferencas else 0)


if __name__ == "__main__":
    main()
