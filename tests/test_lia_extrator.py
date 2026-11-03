"""Extrator da LIA (tools/extrair_lia.py), 03/11/2026: os arquivos do bucket são por mês em UTC; e-mails de 31/10 depois
das 21h (São Paulo) ficam em extracted_emails_2026-11.json e se perdiam. Dados sintéticos, sem rede nem credenciais."""

import importlib.util
from datetime import date
from pathlib import Path

ARQUIVO = Path(__file__).resolve().parents[1] / "tools" / "extrair_lia.py"
_spec = importlib.util.spec_from_file_location("extrair_lia", ARQUIVO)
extrair_lia = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(extrair_lia)

INICIO, FIM, CORTE = date(2026, 9, 21), date(2026, 10, 31), date(2026, 10, 12)


def _email(mid: str, quando_utc: str, classificacao: str = "lead", eid: str | None = None) -> dict:
    return {"internet_message_id": mid, "email_id": eid or mid, "data_processamento": quando_utc,
            "classificacao": classificacao}


def _total(r: dict) -> int:
    return sum(p["nao_lead"] + p["lead"] + p["validacao"] for p in r["periodos"])


def test_meses_le_o_anterior_e_o_seguinte_da_janela():
    assert extrair_lia.meses(INICIO, FIM) == ["2026-08", "2026-09", "2026-10", "2026-11"]
    # virada de ano nas duas pontas
    assert extrair_lia.meses(date(2026, 1, 5), date(2026, 12, 31)) == (
        ["2025-12"] + [f"2026-{m:02d}" for m in range(1, 13)] + ["2027-01"])


def test_email_de_31_10_a_noite_gravado_em_novembro_entra_e_1_11_fica_fora():
    processados = [
        _email("a", "2026-10-15T15:00:00Z", "nao_lead"),
        _email("b", "2026-11-01T01:00:00Z", "lead"),       # 31/10 22h em SP: arquivo de novembro, dentro da janela
        _email("c", "2026-11-01T02:59:59Z", "duvida"),     # 31/10 23h59 em SP: dentro
        _email("d", "2026-11-01T03:00:00Z", "lead"),       # 01/11 0h em SP: fora
        _email("e", "2026-09-21T02:59:00Z", "lead"),       # 20/09 23h59 em SP: fora
        _email("f", "2026-09-21T03:00:00Z", "nao_lead"),   # 21/09 0h em SP: dentro
    ]
    r = extrair_lia.montar_retrato(processados, [], INICIO, FIM, CORTE)
    assert _total(r) == 4
    ultimo_dia = next(d for d in r["dias"] if d["data"] == "2026-10-31")
    assert (ultimo_dia["lead"], ultimo_dia["validacao"]) == (1, 1)
    assert r["dias"][0]["data"] == "2026-09-21" and r["dias"][0]["nao_lead"] == 1
    assert r["periodos"][1]["fim"] == "2026-10-31" and sum(r["faixas"].values()) == 4
    # 31/10 é sábado: as duas mensagens da noite contam no fim de semana, na hora 22 e 23 de SP
    assert r["horas"]["fim_de_semana"][22] == 1 and r["horas"]["fim_de_semana"][23] == 1


def test_mensagem_reprocessada_vale_o_ultimo_processamento_dentro_da_janela():
    processados = [
        _email("x", "2026-10-30T12:00:00Z", "duvida"),
        _email("x", "2026-10-31T23:30:00Z", "lead"),       # 31/10 20h30 em SP, gravado ainda em outubro (UTC)
        _email("x", "2026-11-02T13:00:00Z", "nao_lead"),   # reprocessada depois da janela: não tira nem troca a de 31/10
        _email("y", "2026-11-02T13:00:00Z", "lead"),       # só depois da janela: fora
    ]
    r = extrair_lia.montar_retrato(processados, [], INICIO, FIM, CORTE)
    assert _total(r) == 1 and sum(d["lead"] for d in r["dias"]) == 1


def test_revisao_manual_troca_a_classificacao_e_conta_os_revisados():
    processados = [_email("m1", "2026-10-01T14:00:00Z", "duvida", eid="e1"),
                   _email("m2", "2026-10-01T15:00:00Z", "lead", eid="e2")]
    revisao = [{"email_id": "e1", "revisado": True, "classificacao_correta": "nao_lead"},
               {"email_id": "e2", "revisado": False, "classificacao_correta": "nao_lead"}]
    r = extrair_lia.montar_retrato(processados, revisao, INICIO, FIM, CORTE)
    assert r["itens_com_revisao"] == 1
    assert (r["periodos"][0]["nao_lead"], r["periodos"][0]["lead"], r["periodos"][0]["validacao"]) == (1, 1, 0)


def test_janela_vazia_da_zeros_sem_erro():
    r = extrair_lia.montar_retrato([], [], INICIO, FIM, CORTE)
    assert _total(r) == 0 and len(r["dias"]) == 41 and all(d["fora"] == 0 for d in r["dias"])
