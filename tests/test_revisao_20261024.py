"""Regressões da revisão: recarga diária, cortes, filas e coerência entre fontes."""
from datetime import date, datetime, timezone

import pandas as pd

from app import config, dados
from app.apresentacoes.gestao_orcamentos import apresentacao
from app.apresentacoes.gestao_orcamentos.entrada import calculos as ent
from app.apresentacoes.gestao_orcamentos.atendimento import calculos as at
from app.apresentacoes.gestao_orcamentos.talentos import calculos as tal
from tests.test_dados import ClienteFalso
import gold_simulada  # views da gold sobre os dados sintéticos (D57)


def test_view_recarrega_quando_a_tabela_de_base_muda(monkeypatch):
    """D57: a view não tem `modified` próprio; a recarga segue o da tabela de base (gatilho)."""
    base = [datetime(2026, 10, 23, tzinfo=timezone.utc)]
    falso = ClienteFalso(pd.DataFrame({'ano': [2026], 'n': [10]}), base[0])
    lidas = []
    original = falso.get_table
    falso.get_table = lambda t, timeout=None: (lidas.append(t), original(t))[1]
    monkeypatch.setattr(dados, 'cliente', lambda: falso)
    monkeypatch.setattr(config, 'RECARGA_MIN', 0)
    monkeypatch.setattr(config, 'CONGELAR', False)
    t = dados.Tabela('teste', 'p.d.view', colunas=('ano', 'n'), chave=('ano',), gatilho='p.d.base', em_fundo=False)
    primeira = t.df()
    assert t.df() is primeira and falso.cargas == 1 and set(lidas) == {'p.d.base'}
    falso.modified = base[0].replace(day=24)
    segunda = t.df()
    assert falso.cargas == 2 and segunda is not primeira and segunda.attrs['versao'] == 2


def test_tabela_vazia_permitida_e_um_resultado_valido():
    t = dados.Tabela('teste', 'p.d.t', colunas=('grupo', 'talento', 'n', 'ultimo_pedido'), chave=('grupo', 'talento'),
                     permite_vazia=True)
    t._validar(pd.DataFrame(columns=t.colunas))


def test_site_so_le_a_gold():
    """D57: toda tabela do site está no dataset gold; nada de silver nem de SQL próprio do site."""
    assert all(t.id_tabela.startswith(config.GOLD + '.gld_agenciamento') for t in dados.TABELAS.values())
    assert not hasattr(dados, 'Consulta') and not (config.RAIZ / 'app' / 'sql').exists()
    assert {'sla_entregas', 'sla_entregas_status', 'fila', 'atendimento', 'talentos', 'talentos_top',
            'saidas_status'} <= set(dados.TABELAS)


def test_atendimento_sem_data_fecha_com_extrato(entrada_diaria):
    diaria = entrada_diaria.iloc[[4]].copy()
    diaria['quantidade'], diaria['quantidade_estimada'] = 10, 0
    diaria['entregue_no_mes'], diaria['entregue_depois'] = 6, 0
    diaria['nao_seguiu'], diaria['em_andamento'] = 2, 2
    diaria['_processado_em'] = pd.Timestamp('2026-01-25 12:00Z')
    f = pd.DataFrame({'mes_entrada': pd.to_datetime(['2026-01-01'] * 3),
                      'evento': ['entregue', 'nao_seguiu', 'em_andamento'],
                      'mes_evento': pd.to_datetime(['2026-01-01', None, None]), 'quantidade': [6, 2, 2]})
    a = at.atendimento(diaria, f, gold_simulada.atendimento_mensal(diaria, f))
    x = ent.extrato(gold_simulada.fila_mensal(f), '2026-01')['fila']
    assert a['fila_atual'] == x['seguem'] == 2
    assert a['resp_total'] == x['entregues'] + x['nao_seguiram'] == 8
    assert a['saidas_sem_data'] == 2 and a['meses'][0]['parcial']


def test_ano_fechado_sem_pedidos_no_ano_novo(entrada_diaria):
    df = entrada_diaria.copy()
    df['_processado_em'] = pd.Timestamp('2027-01-05 12:00Z')
    a = at.atendimento(df)
    assert a['ano'] == 2026 and a['meses_completos'] == 'jan a dez'
    assert not any(m['parcial'] or m['futuro'] for m in a['meses'])
    assert a['periodo'] == 'até 31 de dezembro'
    assert a['taxas_contra_anterior']['entregas'] > 0


def test_inicio_exclui_linhas_posteriores_ao_corte(entrada_diaria):
    df = entrada_diaria.copy()
    df['_processado_em'] = pd.Timestamp('2026-02-10 12:00Z')
    e = ent.entrada(df)
    assert e['total'] == 19 and e['meses'][9]['total'] == 0


def test_talentos_sem_classificacao_e_ranking_impossivel():
    df = pd.DataFrame({'ano': [2026], 'categoria': ['Sem talento'], 'n': [5], 'dos_quais_squad': [0]})
    d = tal.divisao(df, 5, 2026)
    assert d['principal']['classe'] == 'sem-talento'
    ranking = pd.DataFrame({'grupo': ['sem-talento'], 'talento': ['X'], 'n': [6], 'ultimo_pedido': [None]})
    assert tal.top_por_grupo(ranking, d) == {}


def test_mesmo_total_nao_garante_mesma_fotografia(entrada_diaria, fluxo_mensal):
    diaria, fluxo = entrada_diaria.copy(), fluxo_mensal.copy()
    diaria['_processado_em'] = fluxo['_processado_em'] = pd.Timestamp('2026-10-23 12:00Z')
    assert not apresentacao._mesma_fotografia(diaria, fluxo)
    fluxo['_processado_em'] = pd.Timestamp('2026-10-22 12:00Z')
    assert not apresentacao._mesma_fotografia(diaria, fluxo)
