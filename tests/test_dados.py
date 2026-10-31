"""Política de carga e falha de app/dados.py, com um BigQuery falso: nada aqui sai do computador."""

from datetime import datetime, timezone

import pandas as pd
import pytest

from app import config, dados


class _Job:
    def __init__(self, df):
        self._df, self.total_bytes_processed = df, 1234

    def to_dataframe(self, create_bqstorage_client=False):
        if create_bqstorage_client and getattr(self, "sem_storage", False):
            raise PermissionError("bigquery.readsessions.create")
        return self._df.copy()


class _Tabela:
    def __init__(self, modified):
        self.modified = modified


class ClienteFalso:
    """Simula get_table/query; `falhar` derruba a próxima chamada; conta as cargas feitas."""

    def __init__(self, df, modified):
        self.df, self.modified, self.falhar, self.cargas, self.metadados = df, modified, False, 0, 0

    def get_table(self, _id, timeout=None):
        self.metadados += 1
        if self.falhar:
            raise ConnectionError("BigQuery fora do ar")
        return _Tabela(self.modified)

    def query(self, sql, job_config=None, timeout=None):
        self.sql = sql
        self.cargas += 1
        return _Job(self.df)


@pytest.fixture
def ambiente(monkeypatch, movimentos):
    falso = ClienteFalso(movimentos, datetime(2026, 10, 22, 12, 2, tzinfo=timezone.utc))
    monkeypatch.setattr(dados, "cliente", lambda: falso)
    monkeypatch.setattr(config, "RECARGA_MIN", 0)  # cada chamada checa o metadado (sem esperar 10 min)
    tabela = dados.Tabela("teste", "p.d.t", colunas=("projeto_id", "passo"), em_fundo=False)
    return falso, tabela


def test_agenda_da_gold_e_estado():
    from app.config import FUSO

    seg_8h = datetime(2026, 10, 26, 8, 0, tzinfo=FUSO)  # segunda antes do horário: vale a sexta 09:00
    assert dados.atualizacao_esperada(seg_8h) == datetime(2026, 10, 23, 9, 0, tzinfo=FUSO)
    seg_10h = datetime(2026, 10, 26, 10, 0, tzinfo=FUSO)  # depois das 09:45: vale a segunda 09:00
    assert dados.atualizacao_esperada(seg_10h) == datetime(2026, 10, 26, 9, 0, tzinfo=FUSO)
    t = dados.Tabela("t", "p.d.t")
    t.modificada_em = datetime(2026, 10, 23, 9, 2, tzinfo=FUSO)  # gold de sexta
    assert t.estado(seg_8h) == "em_dia" and t.estado(seg_10h) == "base_atrasada"
    t.erro = "falhou"
    assert t.estado(seg_8h) == "falha_leitura"


def test_metadado_inalterado_nao_recarrega(ambiente):
    falso, tabela = ambiente
    df1 = tabela.df()
    df2 = tabela.df()
    assert falso.cargas == 1 and falso.metadados == 2 and df1 is df2
    assert tabela.versao == 1 and df1.attrs["versao"] == 1 and not tabela.atrasada


def test_metadado_alterado_recarrega_e_sobe_a_versao(ambiente):
    falso, tabela = ambiente
    tabela.df()
    falso.modified = datetime(2026, 10, 23, 12, 2, tzinfo=timezone.utc)
    df = tabela.df()
    assert falso.cargas == 2 and tabela.versao == 2 and df.attrs["versao"] == 2
    assert dados.versao_de(df) == 2


def test_falha_com_carga_anterior_serve_a_anterior_e_marca_atraso(ambiente):
    falso, tabela = ambiente
    antes = tabela.df()
    falso.falhar = True
    depois = tabela.df()
    assert depois is antes and tabela.atrasada and "BigQuery fora do ar" in tabela.erro
    assert tabela.situacao()["atrasada"] is True
    falso.falhar = False
    tabela.df()
    assert not tabela.atrasada and falso.cargas == 1  # voltou ao normal sem recarregar (metadado igual)


def test_falha_sem_carga_anterior_e_indisponivel(ambiente):
    falso, tabela = ambiente
    falso.falhar = True
    with pytest.raises(dados.DadosIndisponiveis):
        tabela.df()
    assert tabela.versao == 0 and tabela.situacao()["linhas"] == 0


def test_primeira_falha_nao_repete_consulta_a_cada_acesso(ambiente, monkeypatch):
    falso, tabela = ambiente
    monkeypatch.setattr(config, "RECARGA_MIN", 10)
    falso.falhar = True
    for _ in range(3):
        with pytest.raises(dados.DadosIndisponiveis):
            tabela.df()
    assert falso.metadados == 1
    falso.falhar = False
    assert not tabela.df(forcar=True).empty


def test_contrato_rejeita_historico_descontinuo(ambiente, movimentos):
    _, tabela = ambiente
    invalido = movimentos.copy()
    invalido.loc[invalido.index[0], "saida"] = pd.NaT
    with pytest.raises(ValueError, match="descontínuo"):
        tabela._validar(invalido)


def test_contrato_rejeita_situacoes_que_nao_fecham(entrada_diaria):
    tabela = dados.Tabela("entrada", "p.d.t", chave=("data", "grupo_input", "tipo_de_input", "familia"))
    invalido = entrada_diaria.copy()
    invalido.loc[invalido.index[0], "em_andamento"] += 1
    with pytest.raises(ValueError, match="reconciliam"):
        tabela._validar(invalido)


def test_contrato_rejeita_carga_invalida_e_mantem_a_anterior(ambiente, movimentos):
    falso, tabela = ambiente
    boa = tabela.df()
    falso.df = pd.concat([movimentos, movimentos.head(1)])  # chave projeto_id + passo repetida
    falso.modified = datetime(2026, 10, 24, 12, 2, tzinfo=timezone.utc)
    assert tabela.df() is boa and tabela.atrasada and "repetida" in tabela.erro
    falso.df = movimentos.drop(columns=["passo"])  # coluna obrigatória ausente
    falso.modified = datetime(2026, 10, 25, 12, 2, tzinfo=timezone.utc)
    assert tabela.df() is boa and "ausentes" in tabela.erro


def test_le_so_as_colunas_do_contrato(ambiente):
    falso, tabela = ambiente
    tabela.df()
    assert falso.sql.startswith("SELECT projeto_id, passo FROM")


def test_sem_storage_api_cai_para_leitura_comum(ambiente, monkeypatch):
    falso, tabela = ambiente
    monkeypatch.setattr(_Job, "sem_storage", True, raising=False)
    assert len(tabela.df()) > 0 and not tabela.atrasada


def test_aquecimento_roda_antes_da_troca(ambiente):
    falso, tabela = ambiente
    vistos = []
    tabela.ao_carregar.append(lambda df: vistos.append((df.attrs["versao"], tabela.versao)))
    tabela.df()
    assert vistos == [(1, 0)]  # a carga 1 foi aquecida enquanto a versão no ar ainda era 0


def test_em_fundo_responde_na_hora_e_troca_depois(ambiente, monkeypatch):
    falso, tabela = ambiente
    tabela.em_fundo = True
    antes = tabela.df()  # primeira carga: na própria requisição
    falso.modified = datetime(2026, 10, 23, 12, 2, tzinfo=timezone.utc)
    agora = tabela.df()  # vencido: dispara a atualização em segundo plano e devolve a carga atual na hora
    assert agora is antes
    for t in list(__import__("threading").enumerate()):
        if t.name.startswith("atualiza-"):
            t.join(5)
    assert tabela.versao == 2 and tabela.df(forcar=False).attrs["versao"] == 2


def test_falha_espera_o_intervalo_antes_de_tentar_de_novo(ambiente, monkeypatch):
    falso, tabela = ambiente
    tabela.df()
    monkeypatch.setattr(config, "RECARGA_MIN", 10)
    falso.falhar = True
    tabela._checado_em = 0  # força uma checagem agora
    tabela.df()
    metadados = falso.metadados
    tabela.df()
    tabela.df()
    assert falso.metadados == metadados  # dentro do intervalo não tenta de novo
