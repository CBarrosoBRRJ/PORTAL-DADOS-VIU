"""Retrato da LIA para o slide "LIA" (V2, 30/10/2026; PRD Slide LIA de @cris adaptado).

Só leitura: lê os arquivos da LIA no Cloud Storage (gs://gglobo-viu-lia-dados-prd/data/) com as credenciais do portal
(ADC do gcloud-viu) e grava SÓ CONTAGENS AGREGADAS em app/apresentacoes/gestao_orcamentos/lia/retrato.json (nenhum
remetente, assunto ou conteúdo de e-mail sai da fonte). O slide lê esse retrato; não consulta nada ao abrir.

Regras (as mesmas da ficha docs/paginas/lia.md):
- e-mail = mensagem única (internet_message_id) em extracted_emails_AAAA-MM.json; se a mesma mensagem foi processada
  mais de uma vez, vale o último processamento dentro da janela; os arquivos são por mês em UTC, então se leem também
  o mês anterior a inicio e o seguinte a fim (03/11/2026: e-mails de 31/10 depois das 21h estão no arquivo de novembro);
- dia = data do processamento no fuso de São Paulo; janela padrão 21/09 a 29/10/2026;
- categoria = classificação da LIA (nao_lead, lead, duvida/DUVIDA = validação), trocada pela classificação correta da
  revisão manual (revisao_manual.json) quando o item foi revisado;
- período 1 (revisado) até 12/10; período 2 (sem revisão) de 13/10 em diante;
- semana = segunda a domingo da data do processamento (todos os dias, com fim de semana e feriado);
- período do dia (D-LIA-5) = manhã 6h–12h, tarde 12h–18h, noite 18h–6h, pela hora do processamento (a madrugada
  conta na noite do próprio dia do calendário); cada dia traz as contagens por período;
- dias = todos os dias da janela (com fim de semana, feriado e zeros), com as marcas fim_de_semana e feriado e o número
  de e-mails fora do expediente (fora); semanas também trazem fora;
- fora do expediente = processado fora de seg–sex 10h–13h e 14h–19h (o expediente do SLA), ou em fim de semana ou
  feriado. A LIA processa a caixa o dia todo (minutos espalhados de forma uniforme), então a hora do processamento é
  uma aproximação da hora de chegada do e-mail (o arquivo não guarda a hora de chegada).
- turnos (Caio, 30/10/2026) = manhã do expediente (seg–sex 10h–13h), tarde do expediente (seg–sex 14h–19h) e fora do
  expediente (o resto: almoço 13h–14h, noite, fim de semana e feriado; a mesma regra do "fora"), por categoria; somam
  o total da janela.
- horas (Caio, 30/10/2026) = e-mails por hora do processamento (0 a 23) em dia útil, fim de semana e feriado; só contagens;
  horas_lead e horas_nao_lead = o mesmo, só os leads e só os não leads.
Uso: python tools/extrair_lia.py [--inicio 2026-09-21] [--fim 2026-10-29] [--corte 2026-10-12] [--saida arquivo.json]
"""

import argparse
import json
import os
import urllib.parse
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "app" / "apresentacoes" / "gestao_orcamentos" / "lia" / "retrato.json"
BUCKET, PASTA = "gglobo-viu-lia-dados-prd", "data/"
SP = timezone(timedelta(hours=-3))
CATEGORIA = {"nao_lead": "nao_lead", "lead": "lead", "duvida": "validacao", "DUVIDA": "validacao"}
FERIADOS = {date(2026, 10, 12): "Nossa Senhora Aparecida"}


def baixar(sessao, nome: str) -> str:
    r = sessao.get(f"https://storage.googleapis.com/storage/v1/b/{BUCKET}/o/" + urllib.parse.quote(PASTA + nome, safe=""),
                   params={"alt": "media"}, timeout=120)
    if r.status_code == 404:
        return ""
    r.raise_for_status()
    return r.content.decode("utf-8")


def linhas(texto: str) -> list[dict]:
    return [json.loads(x) for x in texto.splitlines() if x.strip()]


def momento(iso: str) -> datetime:
    return datetime.fromisoformat(iso).astimezone(SP)  # Python 3.11+ aceita o "Z" do UTC


def dia(iso: str) -> date:
    return momento(iso).date()


PERIODOS = (("manha", 6, 12), ("tarde", 12, 18), ("noite", 18, 6))  # D-LIA-5: noite = 18h às 6h do dia seguinte


def periodo(t: datetime) -> str:
    """manhã (6h–12h), tarde (12h–18h) ou noite (18h–6h); a madrugada conta na noite do próprio dia do calendário."""
    return "manha" if 6 <= t.hour < 12 else "tarde" if 12 <= t.hour < 18 else "noite"


def faixa(t: datetime) -> str:
    """expediente (seg–sex 10h–13h e 14h–19h, sem feriado), fim_de_semana, feriado, almoco ou noite (dia útil)."""
    if t.weekday() >= 5:
        return "fim_de_semana"
    if t.date() in FERIADOS:
        return "feriado"
    if 10 <= t.hour < 13 or 14 <= t.hour < 19:
        return "expediente"
    return "almoco" if t.hour == 13 else "noite"


def turno(t: datetime) -> str:
    """manha (expediente 10h–13h), tarde (expediente 14h–19h) ou fora (almoço, noite, fim de semana, feriado)."""
    if faixa(t) != "expediente":
        return "fora"
    return "manha" if t.hour < 13 else "tarde"


def meses(inicio: date, fim: date) -> list[str]:
    """Meses (AAAA-MM) dos arquivos a ler: os da janela mais o anterior a inicio e o seguinte a fim. Os arquivos são
    gravados pela data em UTC (3 h à frente de São Paulo): um e-mail processado em 31/10 às 22h (SP) cai em
    extracted_emails_2026-11.json (03/11/2026: 4 e-mails se perdiam). O filtro da janela continua pela data em SP."""
    a, m = (inicio.year - 1, 12) if inicio.month == 1 else (inicio.year, inicio.month - 1)
    ultimo = (fim.year + 1, 1) if fim.month == 12 else (fim.year, fim.month + 1)
    out = []
    while (a, m) <= ultimo:
        out.append(f"{a}-{m:02d}")
        a, m = (a + 1, 1) if m == 12 else (a, m + 1)
    return out


def ultimos_na_janela(processados: list[dict], inicio: date, fim: date) -> list[dict]:
    """Um registro por mensagem (internet_message_id): o último processamento DENTRO da janela (data em SP). Filtrar antes
    de deduplicar deixa o retrato estável: reprocessar depois de fim não tira da janela um e-mail que já estava nela."""
    ultimo = {}
    for e in sorted(processados, key=lambda e: momento(e["data_processamento"])):
        if inicio <= dia(e["data_processamento"]) <= fim:
            ultimo[e["internet_message_id"]] = e
    return list(ultimo.values())


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--inicio", default="2026-09-21")
    p.add_argument("--fim", default="2026-10-29")
    p.add_argument("--corte", default="2026-10-12", help="último dia do período revisado")
    p.add_argument("--saida", default=str(SAIDA), help="arquivo de saída (padrão: o retrato do slide)")
    a = p.parse_args()
    inicio, fim, corte = (date.fromisoformat(x) for x in (a.inicio, a.fim, a.corte))

    import google.auth  # só aqui: montar_retrato() e os testes não precisam da rede nem das credenciais
    from google.auth.transport.requests import AuthorizedSession

    os.environ.setdefault("CLOUDSDK_CONFIG", r"C:\Users\CCMB\AppData\Roaming\gcloud-viu")
    cred, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/devstorage.read_only"])
    s = AuthorizedSession(cred)

    processados = [e for m in meses(inicio, fim) for e in linhas(baixar(s, f"extracted_emails_{m}.json"))]
    revisao = json.loads(baixar(s, "revisao_manual.json") or "[]")
    retrato = montar_retrato(processados, revisao, inicio, fim, corte)
    saida = Path(a.saida)
    saida.write_text(json.dumps(retrato, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    periodos = retrato["periodos"]
    tot = sum(sum(p[k] for k in ("nao_lead", "lead", "validacao")) for p in periodos)
    print(f"{tot} e-mails únicos de {inicio:%d/%m} a {fim:%d/%m}; períodos: "
          + "; ".join(f"{p['rotulo']}: {p['nao_lead']} / {p['lead']} / {p['validacao']}" for p in periodos)
          + f"; {len(retrato['dias'])} dias; {retrato['fim_de_semana']} no fim de semana -> {saida}")


def montar_retrato(processados: list[dict], revisao: list[dict], inicio: date, fim: date, corte: date) -> dict:
    """Só contagens agregadas, sem rede (testável com dados sintéticos): os processamentos lidos dos arquivos e a revisão
    manual viram o retrato.json do slide."""
    correta = {r["email_id"]: r["classificacao_correta"] for r in revisao if r.get("revisado") and r.get("classificacao_correta")}

    por_dia: dict[date, Counter] = {}
    por_faixa: Counter = Counter()
    fora_dia: Counter = Counter()  # D-LIA-4: e-mails fora do expediente por dia (o extrato da semana soma)
    per_dia: dict[date, dict[str, Counter]] = {}  # D-LIA-5: dia × período do dia × categoria
    por_turno: dict[str, Counter] = {}  # Caio, 30/10/2026: turno do expediente × categoria
    por_hora: dict[str, Counter] = {"util": Counter(), "fim_de_semana": Counter(), "feriado": Counter()}
    lead_hora: dict[str, Counter] = {"util": Counter(), "fim_de_semana": Counter(), "feriado": Counter()}
    nl_hora: dict[str, Counter] = {"util": Counter(), "fim_de_semana": Counter(), "feriado": Counter()}
    revisados = 0
    for e in ultimos_na_janela(processados, inicio, fim):
        t = momento(e["data_processamento"])
        d = t.date()
        cat = CATEGORIA[correta.get(e["email_id"], e["classificacao"])]
        revisados += e["email_id"] in correta
        por_dia.setdefault(d, Counter())[cat] += 1
        por_faixa[faixa(t)] += 1
        fora_dia[d] += faixa(t) != "expediente"
        per_dia.setdefault(d, {}).setdefault(periodo(t), Counter())[cat] += 1
        por_turno.setdefault(turno(t), Counter())[cat] += 1
        tipo = "fim_de_semana" if t.weekday() >= 5 else "feriado" if t.date() in FERIADOS else "util"
        por_hora[tipo][t.hour] += 1
        lead_hora[tipo][t.hour] += cat == "lead"
        nl_hora[tipo][t.hour] += cat == "nao_lead"

    def bloco(c: Counter) -> dict:
        return {k: c.get(k, 0) for k in ("nao_lead", "lead", "validacao")}

    periodos = []
    for rotulo, ini, fi, rev in (("revisado", inicio, corte, True), ("sem revisão", corte + timedelta(days=1), fim, False)):
        c = sum((v for d, v in por_dia.items() if ini <= d <= fi), Counter())
        periodos.append({"rotulo": rotulo, "inicio": ini.isoformat(), "fim": fi.isoformat(), "revisado": rev, **bloco(c)})
    # todos os dias da janela, com zero quando não houve e-mail (D-LIA-2: médias por dia da semana precisam do zero)
    dias = []
    d = inicio
    while d <= fim:
        dias.append({"data": d.isoformat(), "feriado": FERIADOS.get(d, ""), "fim_de_semana": d.weekday() >= 5,
                     **bloco(por_dia.get(d, Counter())), "fora": fora_dia.get(d, 0),
                     "periodos": {k: bloco(per_dia.get(d, {}).get(k, Counter())) for k, _, _ in PERIODOS}})
        d += timedelta(days=1)
    fds = sum(sum(c.values()) for d, c in por_dia.items() if d.weekday() >= 5)
    semanas = []
    seg = inicio - timedelta(days=inicio.weekday())
    while seg <= fim:
        ini, fi = max(seg, inicio), min(seg + timedelta(days=6), fim)
        c = sum((v for d, v in por_dia.items() if ini <= d <= fi), Counter())
        semanas.append({"inicio": ini.isoformat(), "fim": fi.isoformat(), **bloco(c),
                        "fora": sum(v for d, v in fora_dia.items() if ini <= d <= fi)})
        seg += timedelta(days=7)

    return {
        "fonte": f"gs://{BUCKET}/{PASTA} (extracted_emails_*, revisao_manual.json)",
        "extraido_em": datetime.now(SP).strftime("%Y-%m-%d %H:%M"),
        "inicio": inicio.isoformat(), "fim": fim.isoformat(), "corte_revisao": corte.isoformat(),
        "itens_com_revisao": revisados,
        "periodos": periodos, "dias": dias, "fim_de_semana": fds, "semanas": semanas,
        "faixas": {k: por_faixa.get(k, 0) for k in ("expediente", "almoco", "noite", "fim_de_semana", "feriado")},
        "turnos": {k: bloco(por_turno.get(k, Counter())) for k in ("manha", "tarde", "fora")},
        "horas": {k: [c.get(h, 0) for h in range(24)] for k, c in por_hora.items()},
        "horas_lead": {k: [c.get(h, 0) for h in range(24)] for k, c in lead_hora.items()},
        "horas_nao_lead": {k: [c.get(h, 0) for h in range(24)] for k, c in nl_hora.items()},
    }


if __name__ == "__main__":
    main()
