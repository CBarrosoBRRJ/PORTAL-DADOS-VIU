"""A14: tendência descritiva separa mês parcial e categorias de saída."""
from app.apresentacoes.gestao_orcamentos.atendimento.calculos import leitura_executiva


def mes(n, entrou, entregue, sem, fila, parcial=False, futuro=False):
    return dict(rotulo=str(n), futuro=futuro, parcial=parcial, entradas=entrou,
                entregues_ano=entregue, sem_entrega_ano=sem, resp_ano=entregue+sem,
                fila=fila, saldo=entregue+sem-entrou)


def test_tendencia_exclui_parcial_e_preserva_ponte_da_fila():
    meses=[mes(1,100,80,10,10),mes(2,100,75,15,20),mes(3,100,85,10,25),
           mes(4,100,80,10,35),mes(5,50,40,15,30,parcial=True)]
    l=leitura_executiva(meses,450)
    assert [m['rotulo'] for m in l['fechados']]==['2','3','4']
    assert l['saldo_fechados']==-20-5  # fila passa de 10 para 35
    assert l['meses_fila_cresceu']==3
    assert l['fila_anterior']==35
    assert l['entregues']+l['sem_entrega']+l['fila']==450
    assert l['entregues']==360 and l['sem_entrega']==60


def test_leitura_sem_base_nao_inventa_percentual_ou_tendencia():
    l=leitura_executiva([],0)
    assert l['atual'] is None and l['pct_entregues'] is None and l['fechados']==[]


def test_ano_fechado_inclui_ultimo_mes_e_ignora_futuros():
    l=leitura_executiva([mes(11,10,7,1,2),mes(12,5,4,1,2),
                        mes(1,0,0,0,0,futuro=True)],15)
    assert l['atual']['rotulo']=='12' and len(l['fechados'])==2


def test_virada_de_mes_sem_movimento_mantem_ultimo_mes_com_dados_no_foco():
    l=leitura_executiva([mes(10,100,80,10,10),mes(11,0,0,0,10,parcial=True)],100)
    assert l['atual']['rotulo']=='10'


def test_percentuais_da_leitura_somam_cem_pelo_maior_resto():
    # total=7 com 2, 2, 3: round simples daria 28,6 + 28,6 + 42,9 = 100,1%
    l=leitura_executiva([mes(1,7,2,2,3)],7)
    assert round(l['pct_entregues']+l['pct_sem_entrega']+l['pct_fila'],1)==100.0
