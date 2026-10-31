"""D65 (31/10/2026): corte e congelamento dos dados em 31/10/2026 para a reunião de 04/11 (app/congelamento.py).

Um BigQuery falso entrega cargas com `_processado_em` em dias diferentes; o fim de cada carga é a regra E3 (véspera do
processamento, em São Paulo). Nada aqui sai do computador; a base congelada vai para uma pasta temporária.

Auditoria do Codex (31/10/2026): F01 (base exigida no build e no arranque, produção sem BigQuery), F02 (congelada em
memória × persistida e validada, nova tentativa), F07/F08 (base como unidade: trava entre processos, pasta de versão
exclusiva, manifesto global publicado por último, leitura que valida o conjunto, recuperação). Versão anterior destes
testes em _descartados/2026-10-31/congelamento_por_tabela/."""

import json
import os
import time
from datetime import date, datetime, timezone

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from app import config, congelamento, dados


def carga(dia: str, valores=(10, 20)) -> pd.DataFrame:
    """Carga da gold processada em `dia` às 09:01 de Brasília (12:01 UTC): fim = véspera (E3)."""
    ts = pd.Timestamp(f"{dia} 12:01:30", tz="UTC")
    return pd.DataFrame({"chave": list(range(1, len(valores) + 1)), "valor": list(valores),
                         "dia": pd.to_datetime(["2026-10-01"] * len(valores)).date, "_processado_em": [ts] * len(valores)})


class _Job:
    def __init__(self, df):
        self._df, self.total_bytes_processed = df, 100

    def to_dataframe(self, create_bqstorage_client=False):
        return self._df.copy()


class _Meta:
    def __init__(self, modified):
        self.modified = modified


class BigQueryFalso:
    """A gold: cada `publicar` é uma carga nova (o `modified` muda); conta metadados e downloads."""

    def __init__(self):
        self.df, self.modified, self.metadados, self.cargas = None, None, 0, 0

    def publicar(self, dia: str, valores=(10, 20)):
        self.df = carga(dia, valores)
        self.modified = pd.Timestamp(f"{dia} 12:02", tz="UTC").to_pydatetime()

    def get_table(self, _id, timeout=None):
        self.metadados += 1
        return _Meta(self.modified)

    def query(self, sql, job_config=None, timeout=None):
        self.cargas += 1
        return _Job(self.df)


@pytest.fixture
def gold(monkeypatch, tmp_path):
    falso = BigQueryFalso()
    monkeypatch.setattr(dados, "cliente", lambda: falso)
    monkeypatch.setattr(dados, "TABELAS", {})  # a base do teste = as tabelas criadas por nova_tabela
    monkeypatch.setattr(config, "CORTE_DADOS", date(2026, 10, 31))
    monkeypatch.setattr(config, "CORTE_FOLGA_DIAS", 1)
    monkeypatch.setattr(config, "BASE_CONGELADA_DIR", tmp_path)
    monkeypatch.setattr(config, "RECARGA_MIN", 0)  # cada chamada confere o metadado
    monkeypatch.setattr(config, "CONGELAR", True)  # o padrão do computador (D63): o corte manda no lugar dele
    monkeypatch.setattr(config, "EM_PRODUCAO", False)
    congelamento._reiniciar()
    yield falso
    congelamento._reiniciar()


def nova_tabela(id_tabela="p.gold_monday.gld_teste"):
    """Tabela nova (servidor recém-ligado) que faz parte da base (dados.TABELAS); a mesma id substitui a anterior."""
    t = dados.Tabela("teste", id_tabela, chave=("chave",), colunas=("chave", "valor", "_processado_em"),
                     em_fundo=False)
    dados.TABELAS[id_tabela] = t
    return t


def reiniciar_processo():
    """Simula outro processo (ou o servidor religado): esquece o que estava em memória."""
    congelamento._reiniciar()


def manifesto(tmp_path) -> dict:
    return json.loads((tmp_path / congelamento.MANIFESTO).read_text(encoding="utf-8"))


def test_carga_ate_30_10_e_aceita_e_o_portal_segue_atualizando(gold, tmp_path):
    gold.publicar("2026-10-30")  # sexta 30/10: dados até 29/10
    t = nova_tabela()
    assert t.df()["valor"].tolist() == [10, 20] and not t.congelada
    gold.publicar("2026-10-31", valores=(11, 21))  # carga de sábado: dados até 30/10 (< corte)
    assert t.df()["valor"].tolist() == [11, 21] and not t.congelada and t.versao == 2
    assert t.estado() != "congelada"
    assert not list(tmp_path.rglob("*.parquet")) and not (tmp_path / congelamento.MANIFESTO).exists()


def test_carga_ate_31_10_congela_grava_o_conjunto_e_confere(gold, tmp_path):
    gold.publicar("2026-10-30")
    t = nova_tabela()
    t.df()
    gold.publicar("2026-11-01", valores=(12, 22))  # domingo 01/11 (rodada à mão): dados até 31/10
    df = t.df()
    assert df["valor"].tolist() == [12, 22] and t.congelada and t.estado() == "congelada"
    m = manifesto(tmp_path)
    assert m["formato"] == 2 and m["corte"] == "2026-10-31" and m["fim"] == "2026-10-31"
    ficha = m["tabelas"]["gld_teste"]
    assert ficha["linhas"] == 2 and ficha["fim"] == "2026-10-31" and len(ficha["sha256"]) == 64
    assert (tmp_path / m["pasta"] / "gld_teste.parquet").exists()
    assert (tmp_path / m["pasta"] / congelamento.MANIFESTO).exists()  # cópia interna (recuperação, B5)
    s = congelamento.situacao()
    assert s["persistida"] is True and s["manifesto"] == "valido" and s["erro_gravacao"] is None
    assert not (tmp_path / congelamento.TRAVA).exists()  # a trava sai ao terminar
    assert dados.base_congelada([t.situacao()]) is True


def test_depois_de_congelar_a_carga_ate_02_11_e_ignorada(gold):
    gold.publicar("2026-11-01", valores=(12, 22))
    t = nova_tabela()
    t.df()
    metadados, cargas = gold.metadados, gold.cargas
    gold.publicar("2026-11-03", valores=(99, 99))  # terça 03/11: dados até 02/11
    assert t.df()["valor"].tolist() == [12, 22]
    assert t.df(forcar=True)["valor"].tolist() == [12, 22]  # nem a recarga forçada troca a base
    assert (gold.metadados, gold.cargas) == (metadados, cargas)  # nenhuma consulta depois de congelar
    assert t.estado() == "congelada" and t.erro is None


def test_carga_da_segunda_02_11_cabe_na_folga_e_congela(gold, tmp_path):
    gold.publicar("2026-11-02")  # segunda 02/11 (agendada): dados até 01/11 = corte + 1 dia de folga (caminho B)
    t = nova_tabela()
    t.df()
    assert t.congelada and congelamento.fim_da_carga(t.df()) == date(2026, 11, 1)
    assert manifesto(tmp_path)["fim"] == "2026-11-01"


def test_carga_alem_da_folga_e_ignorada_e_a_anterior_continua(gold):
    gold.publicar("2026-10-30")
    t = nova_tabela()
    t.df()
    gold.publicar("2026-11-03", valores=(99, 99))  # o portal ficou desligado e a 1ª carga vista já passou do corte
    assert t.df()["valor"].tolist() == [10, 20] and not t.congelada
    assert "ForaDoCorte" in (t.erro or "") and t.estado() == "falha_leitura"  # visível: a base não chegou ao corte
    cargas = gold.cargas
    t.df()
    assert gold.cargas == cargas  # a mesma carga recusada não é baixada de novo a cada checagem


def test_todas_as_tabelas_congelam_na_mesma_carga(gold, tmp_path):
    gold.publicar("2026-11-01")
    a = nova_tabela("p.gold_monday.gld_a")
    b = nova_tabela("p.gold_monday.gld_b")
    a.df()
    assert a.congelada
    # B1: "a" congelou só em memória; a base não é gravada pela metade
    s = congelamento.situacao()
    assert s["persistida"] is False and s["pendentes"] == ["gld_b"] and s["manifesto"] == "ausente"
    assert not (tmp_path / congelamento.MANIFESTO).exists()
    gold.publicar("2026-11-02")  # "b" só é vista depois da carga de segunda (fim 01/11, dentro da folga)
    with pytest.raises(dados.DadosIndisponiveis):
        b.df()  # K5: fim diferente do da base congelada de "a"
    assert "outra carga" in b.erro and not (tmp_path / congelamento.MANIFESTO).exists()


def test_o_conjunto_so_e_gravado_quando_todas_congelam(gold, tmp_path):
    gold.publicar("2026-11-02")
    a, b = nova_tabela("p.gold_monday.gld_a"), nova_tabela("p.gold_monday.gld_b")
    a.df()
    assert not (tmp_path / congelamento.MANIFESTO).exists()
    b.df()
    m = manifesto(tmp_path)
    assert set(m["tabelas"]) == {"gld_a", "gld_b"} and m["fim"] == "2026-11-01"
    assert m["processado_em"].startswith("2026-11-02T12:01:30")


def test_producao_le_a_base_sem_bigquery(gold, monkeypatch):
    gold.publicar("2026-11-01", valores=(12, 22))
    nova_tabela().df()  # no computador: congela e grava

    def proibido():
        raise AssertionError("o BigQuery não pode ser consultado com a base congelada")

    monkeypatch.setattr(dados, "cliente", proibido)
    monkeypatch.setattr(config, "EM_PRODUCAO", True)
    monkeypatch.setattr(config, "CONGELAR", False)  # como no Cloud Run
    reiniciar_processo()
    assert congelamento.exigir()["fim"] == "2026-10-31"  # F01: o arranque confere a base
    t = nova_tabela()  # instância nova (o servidor recém-ligado)
    df = t.df()
    assert df["valor"].tolist() == [12, 22] and t.congelada and t.estado() == "congelada"
    assert t.processado_em().date() == date(2026, 11, 1) and t.bytes_lidos == 0
    assert congelamento.persistir(forcar=True) is False  # em produção nada é gravado
    assert t.df()["valor"].tolist() == [12, 22]


def test_producao_sem_base_nao_sobe_e_nunca_chama_o_bigquery(gold, monkeypatch, tmp_path):
    def proibido():
        raise AssertionError("em produção o BigQuery não é consultado")

    monkeypatch.setattr(dados, "cliente", proibido)
    monkeypatch.setattr(config, "EM_PRODUCAO", True)
    with pytest.raises(congelamento.BaseInvalida, match="sem manifesto"):
        congelamento.exigir()
    t = nova_tabela()
    with pytest.raises(dados.DadosIndisponiveis, match="não é consultado"):
        t.df()  # nem a requisição cai no BigQuery


def test_arranque_em_producao_falha_sem_base(gold, monkeypatch):
    from app.main import app

    monkeypatch.setattr(config, "EM_PRODUCAO", True)
    with pytest.raises(congelamento.BaseInvalida):
        with TestClient(app):
            pass


def test_arquivo_alterado_invalida_a_base_inteira(gold, tmp_path, monkeypatch):
    gold.publicar("2026-11-01", valores=(12, 22))
    a, b = nova_tabela("p.gold_monday.gld_a"), nova_tabela("p.gold_monday.gld_b")
    a.df(), b.df()
    m = manifesto(tmp_path)
    (tmp_path / m["pasta"] / "gld_a.parquet").write_bytes(b"corrompido")
    reiniciar_processo()
    gold.publicar("2026-10-30")
    b2 = nova_tabela("p.gold_monday.gld_b")
    # B4: o problema em "a" invalida também "b" (o conjunto é a unidade): volta ao BigQuery no computador
    assert b2.df()["valor"].tolist() == [10, 20] and not b2.congelada
    assert congelamento.situacao()["manifesto"].startswith("invalido: ") and "sha256" in congelamento.situacao()["manifesto"]
    monkeypatch.setattr(config, "CORTE_DADOS", date(2026, 11, 30))  # manifesto de outro corte
    assert congelamento.ler(nova_tabela("p.gold_monday.gld_b")) is None


def test_manifesto_incompleto_ou_incoerente_e_recusado(gold, tmp_path):
    gold.publicar("2026-11-01")
    nova_tabela("p.gold_monday.gld_a").df()
    nova_tabela("p.gold_monday.gld_b").df()
    raiz = tmp_path / congelamento.MANIFESTO
    original = raiz.read_text(encoding="utf-8")
    m = json.loads(original)
    sem_b = {**m, "tabelas": {"gld_a": m["tabelas"]["gld_a"]}}
    raiz.write_text(json.dumps(sem_b), encoding="utf-8")
    with pytest.raises(congelamento.BaseInvalida, match="faltam gld_b"):
        congelamento.validar(usar_cache=False)
    outra = json.loads(original)
    outra["tabelas"]["gld_b"]["fim"] = "2026-11-01"  # uma tabela de outra carga
    raiz.write_text(json.dumps(outra), encoding="utf-8")
    with pytest.raises(congelamento.BaseInvalida, match="gld_b: carga até 2026-11-01"):
        congelamento.validar(usar_cache=False)
    raiz.write_text(original, encoding="utf-8")
    assert congelamento.validar(usar_cache=False)["fim"] == "2026-10-31"


def test_falha_ao_gravar_fica_visivel_e_e_retentada(gold, tmp_path, monkeypatch):
    gold.publicar("2026-11-01", valores=(12, 22))
    falhas = {"n": 1}
    gravar = congelamento._gravar_conjunto

    def instavel(registros, fim):
        if falhas["n"]:
            falhas["n"] -= 1
            raise OSError("disco cheio")
        return gravar(registros, fim)

    monkeypatch.setattr(congelamento, "_gravar_conjunto", instavel)
    t = nova_tabela()
    assert t.df()["valor"].tolist() == [12, 22] and t.congelada  # F02: congelada em memória, a página segue
    s = congelamento.situacao()
    assert s["persistida"] is False and "disco cheio" in s["erro_gravacao"] and s["tentativas"] == 1
    assert not (tmp_path / congelamento.MANIFESTO).exists()
    with TestClient(__import__("app.main", fromlist=["app"]).app) as cli:
        saude = cli.get("/saude").json()["base_congelada"]
    assert saude["persistida"] is False and "disco cheio" in saude["erro_gravacao"]
    t.df()  # dentro do intervalo de nova tentativa: não tenta de novo
    assert congelamento.situacao()["tentativas"] == 1
    monkeypatch.setattr(congelamento, "TENTATIVA_S", 0)
    t.df()  # passou o intervalo: a leitura retenta e grava
    s = congelamento.situacao()
    assert s["persistida"] is True and s["erro_gravacao"] is None and s["tentativas"] == 2
    assert manifesto(tmp_path)["fim"] == "2026-10-31"


def test_um_escritor_por_vez_e_trava_abandonada(gold, tmp_path, monkeypatch):
    gold.publicar("2026-11-01")
    (tmp_path / congelamento.TRAVA).write_text("outro processo", encoding="utf-8")
    t = nova_tabela()
    t.df()
    s = congelamento.situacao()
    assert s["persistida"] is False and "Ocupada" in s["erro_gravacao"]  # B2: não grava com outro escritor
    assert not (tmp_path / congelamento.MANIFESTO).exists()
    velha = time.time() - congelamento.TRAVA_VELHA_S - 60
    os.utime(tmp_path / congelamento.TRAVA, (velha, velha))  # o outro processo morreu há mais de 15 min
    assert congelamento.persistir(forcar=True) is True
    assert not (tmp_path / congelamento.TRAVA).exists()


def test_pastas_de_versao_exclusivas_e_publicacao_atomica(gold, tmp_path, monkeypatch):
    gold.publicar("2026-11-01")
    t = nova_tabela()
    t.df()
    primeira = manifesto(tmp_path)["pasta"]
    registros = dict(congelamento._memoria)
    segunda = congelamento._gravar_conjunto(registros, date(2026, 10, 31))  # outro escritor, mesma carga
    assert segunda != primeira and (tmp_path / primeira).is_dir() and (tmp_path / segunda).is_dir()  # nada se apaga
    assert manifesto(tmp_path)["pasta"] == segunda
    assert not list(tmp_path.glob(".*.tmp"))  # o temporário do manifesto virou o manifesto
    # gravação interrompida no meio: o manifesto da raiz continua apontando para a versão completa anterior
    original = pd.DataFrame.to_parquet

    def quebra(self, *a, **k):
        raise OSError("energia caiu")

    monkeypatch.setattr(pd.DataFrame, "to_parquet", quebra)
    with pytest.raises(OSError):
        congelamento._gravar_conjunto(registros, date(2026, 10, 31))
    monkeypatch.setattr(pd.DataFrame, "to_parquet", original)
    assert manifesto(tmp_path)["pasta"] == segunda
    reiniciar_processo()
    assert congelamento.ler(nova_tabela())[0]["valor"].tolist() == [10, 20]


def test_recuperar_congelamento_interrompido(gold, tmp_path):
    gold.publicar("2026-11-01")
    nova_tabela("p.gold_monday.gld_a").df()
    nova_tabela("p.gold_monday.gld_b").df()
    pasta = manifesto(tmp_path)["pasta"]
    (tmp_path / congelamento.MANIFESTO).rename(tmp_path / "manifesto_perdido.json")  # caiu antes de publicar
    (tmp_path / "v-20261031-20261102T090000-aaaaaa").mkdir()  # outra gravação, interrompida no meio
    reiniciar_processo()
    assert congelamento.ler(nova_tabela("p.gold_monday.gld_a")) is None  # sem manifesto, nada vale
    relato = congelamento.recuperar()
    assert any("parcial" in r for r in relato) and any(f"{pasta}: completa e conferida, publicada" in r for r in relato)
    assert manifesto(tmp_path)["pasta"] == pasta and congelamento.persistida()
    assert congelamento.ler(nova_tabela("p.gold_monday.gld_a")) is not None
    assert "nada a recuperar" in congelamento.recuperar()[0]


def test_recuperar_sem_versao_completa_avisa(gold, tmp_path):
    (tmp_path / "v-20261031-20261102T090000-bbbbbb").mkdir(parents=True)
    nova_tabela()
    with pytest.raises(congelamento.BaseInvalida, match="nenhuma versão completa"):
        congelamento.recuperar()


def test_conferencia_do_build_reprova_sem_base_e_aprova_o_pacote_coerente(gold, tmp_path, monkeypatch, capsys):
    from app import conferir_base

    nova_tabela()
    assert conferir_base.main() == 1  # F01: sem base, o RUN do Dockerfile falha
    assert "PACOTE REPROVADO" in capsys.readouterr().out
    monkeypatch.setattr(dados, "cliente", lambda: gold)  # a conferência trocou o cliente por um que recusa o BigQuery
    gold.publicar("2026-11-02")
    nova_tabela().df()
    prev = tmp_path / "previsao.json"
    prev.write_text(json.dumps({"retrato": {"mes_fechado": "2026-10"},
                                "carga": {"processado_em": "2026-11-02 12:01:46+00:00", "dados_ate": "2026-11-01"},
                                "acompanhamento": {"mes": "2026-11", "ate": "2026-11-01",
                                                   "processado_em": "2026-11-02 12:04:00+00:00"}}), encoding="utf-8")
    monkeypatch.setattr(config, "PREVISAO_ARQ", prev)
    monkeypatch.setattr(congelamento, "conferir_lia", lambda: [])
    assert conferir_base.main() == 0
    assert "Pacote conferido" in capsys.readouterr().out
    # F03: acompanhamento de outra carga reprova o pacote
    p = json.loads(prev.read_text(encoding="utf-8"))
    p["acompanhamento"]["processado_em"] = "2026-10-28 12:04:07+00:00"
    prev.write_text(json.dumps(p), encoding="utf-8")
    assert conferir_base.main() == 1
    assert "acompanhamento da carga de 28/10/2026, a base congelada é de 02/11/2026" in capsys.readouterr().out


def test_dockerfile_confere_o_pacote_no_build():
    texto = (config.RAIZ / "Dockerfile").read_text(encoding="utf-8")
    copia_prev = texto.index("COPY ml/saida/previsao.json")
    assert texto.index("RUN python -m app.conferir_base") > copia_prev  # depois de a Previsão entrar na imagem


def test_tipos_da_gold_voltam_iguais_do_arquivo(gold):
    gold.df = pd.DataFrame({
        "chave": [1, 2], "valor": [1.5, None], "_processado_em": [pd.Timestamp("2026-11-01 12:01", tz="UTC")] * 2,
        "data": pd.Series(pd.to_datetime(["2026-10-30", "2026-10-31"]).date, dtype="dbdate"),
        "entrada": pd.to_datetime(["2026-10-30 10:00", None]), "texto": pd.Series(["a", None], dtype="string"),
        "flag": pd.Series([True, None], dtype="boolean"), "inteiro": pd.Series([1, None], dtype="Int64")})
    gold.modified = datetime(2026, 11, 1, 12, 2, tzinfo=timezone.utc)
    original = nova_tabela().df().copy()
    lido, _, _ = congelamento.ler(nova_tabela())
    pd.testing.assert_frame_equal(lido, original)


def test_sem_corte_volta_o_comportamento_anterior(gold, monkeypatch):
    gold.publicar("2026-11-01")
    nova_tabela().df()  # congela e grava com o corte ligado
    monkeypatch.setattr(config, "CORTE_DADOS", None)  # descongelar (CORTE_DADOS=off)
    gold.publicar("2026-11-03", valores=(99, 99))
    t = nova_tabela()
    assert t.df()["valor"].tolist() == [99, 99] and not t.congelada  # o arquivo não é lido
    assert t.estado() == "congelada"  # só o CONGELAR da D63 (carga da subida), como antes
    assert dados.base_congelada([t.situacao()]) is True
    assert congelamento.situacao() == {"corte": None} and congelamento.exigir() is None
    monkeypatch.setattr(config, "CONGELAR", False)  # CONGELAR=false: volta a recarregar a cada carga
    gold.publicar("2026-11-04", valores=(7, 7))
    assert t.df()["valor"].tolist() == [7, 7] and dados.base_congelada([t.situacao()]) is False


def test_rodape_da_base_congelada_no_corte(monkeypatch):
    from app.main import app

    monkeypatch.setattr(config, "CORTE_DADOS", date(2026, 10, 31))
    processado = datetime(2026, 11, 1, 9, 1, tzinfo=config.FUSO)
    for tab in dados.TABELAS.values():
        s = tab.situacao()
        monkeypatch.setattr(tab, "situacao", lambda s=s: {**s, "versao": 1, "estado": "congelada",
                                                          "processado_em": processado, "modificada_em": processado})
    with TestClient(app) as cli:
        html = cli.get("/viu-agenciamento").text
    assert ('class="rodape-dados">Dados até 31/10/2026 · atualizados em 01/11/2026, 09:01 · base congelada para a '
            'apresentação') in html
    # antes da carga do corte, o rodapé não diz "congelada"
    for tab in dados.TABELAS.values():
        s = tab.situacao()
        monkeypatch.setattr(tab, "situacao", lambda s=s: {**s, "estado": "em_dia"})
    with TestClient(app) as cli:
        assert "base congelada para a apresentação" not in cli.get("/viu-agenciamento").text
