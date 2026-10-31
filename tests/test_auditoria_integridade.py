"""Regressões da auditoria de 26/10: sem rede, produção ou mudanças de interface."""
import json

import numpy as np
import pandas as pd
import pytest

from ml import rodar, regua


@pytest.mark.parametrize('funcao', [rodar.rotina, rodar.acompanhamento])
def test_segundo_job_nao_apaga_trava_do_primeiro(tmp_path, monkeypatch, funcao):
    lock = tmp_path/'rotina.lock'; lock.write_text('outro processo', encoding='utf-8')
    monkeypatch.setattr(rodar, 'TRAVA', lock)
    with pytest.raises(FileExistsError):
        funcao(extrair=False)
    assert lock.read_text(encoding='utf-8') == 'outro processo'


def test_publicacao_com_falha_nao_registra_sucesso(monkeypatch, tmp_path):
    monkeypatch.setattr(rodar, 'ESTADO', tmp_path/'estado.json')
    def falha():
        raise ValueError('contrato inválido')
    monkeypatch.setattr(rodar.previsao, 'gravar', falha)
    with pytest.raises(ValueError):
        rodar._registrado('teste', rodar._previsao)
    assert json.loads(rodar.ESTADO.read_text(encoding='utf-8'))['codigo'] == 1


@pytest.mark.parametrize('carga_modelo', ['antiga', 'atual'])
def test_resultados_de_cargas_diferentes_nao_sao_publicados(tmp_path, carga_modelo):
    d={'protocolo':rodar.PROTOCOLO['nome'], 'carga':{'processado_em':'antiga'},
       'modelos':{'m':{'carga':carga_modelo}}}
    (tmp_path/'m.json').write_text(json.dumps(d), encoding='utf-8')
    destino=tmp_path/'resultado.txt'
    with pytest.raises(ValueError):
        rodar.juntar(series={}, meta={'processado_em':'atual'}, pasta=tmp_path, destino=destino)
    assert not destino.exists()


@pytest.mark.parametrize('v,lo,hi', [(np.nan,0,1),(np.inf,0,1),(1,2,0),(1,0,np.inf),(1,np.nan,2)])
def test_previsoes_invalidas_nao_entram_na_comparacao(v,lo,hi):
    with pytest.raises(ValueError):
        regua._normalizar(pd.DataFrame({'valor':[v],'p10':[lo],'p90':[hi]}),1,pd.Period('2026-10','M'))


def test_acompanhamento_recusado_registra_falha(tmp_path, monkeypatch):
    monkeypatch.setattr(rodar, 'TRAVA', tmp_path/'rotina.lock')
    monkeypatch.setattr(rodar, 'ESTADO', tmp_path/'estado.json')
    monkeypatch.setattr(rodar.previsao, 'atualizar_acompanhamento', lambda: False)
    with pytest.raises(ValueError):
        rodar._registrado('acompanhamento', rodar.acompanhamento, extrair=False)
    assert json.loads(rodar.ESTADO.read_text(encoding='utf-8'))['codigo'] == 1
    assert not rodar.TRAVA.exists()
