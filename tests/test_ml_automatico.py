"""Comparação automática com o AutoTS (D55, 26/10/2026; ml/modelos/automatico.py, regras AT1–AT7).

Sem rodar o AutoTS de verdade (lento e com processo próprio): a busca é trocada por um "stub" que registra a janela
recebida e devolve um ranking fixo. Confere que a régua D48 só entrega ao AutoTS os 12 meses anteriores a cada origem
(sem vazamento), que autots_k usa o k-ésimo colocado, que o vencedor segue a regra de desempate e que o contrato leva a
comparação para a ficha."""

import pandas as pd
import pytest

from ml import previsao as mp
from ml import regua
from ml.modelos import automatico as A


def _serie(nome="Mercado"):
    meses = pd.period_range("2024-10", "2026-09", freq="M")
    return pd.Series([100.0 + 5 * i for i in range(len(meses))], index=meses, name=nome)


def Stub(n=3):
    """Busca falsa: guarda cada janela e devolve n 'modelos' que preveem o último valor x (1, 1,1, 1,2). É uma função
    (a régua faz deepcopy do modelo, e o deepcopy mantém a mesma função: as janelas ficam numa lista só)."""
    def busca(serie):
        busca.janelas.append(serie.copy())
        ultimo = float(serie.iloc[-1])
        return {"segundos": 0.0, "n_familias": n, "escolhidos": [
            {"modelo": f"M{k}", "transformacao": "{}", "nota": float(k), "posicao": k,
             "previsao": [{"valor": ultimo * (1 + 0.1 * (k - 1)), "p10": ultimo * 0.9, "p90": ultimo * 1.3}] * A.HMAX}
            for k in range(1, n + 1)]}

    busca.janelas = []
    return busca


def test_autots_so_ve_a_janela_de_12_meses_antes_da_origem():
    """AT1 + régua R1: em cada origem (jan–set/2026 e o futuro), a busca recebe só os 12 meses fechados anteriores."""
    stub = Stub()
    s = _serie()
    b = regua.backtest(A.AutoTSPosicao(1, busca=stub), s)
    regua.prever_futuro(A.AutoTSPosicao(1, busca=stub), {"Mercado": s})
    origens = sorted({pd.Period(o, "M") for o in b["origem"]}) + [pd.Period("2026-10", "M")]
    assert [j.index[-1] + 1 for j in stub.janelas] == origens
    for j in stub.janelas:
        origem = j.index[-1] + 1
        assert len(j) == 12 and j.index[0] == origem - 12 and (j.index < origem).all()
        assert j.equals(s[(s.index >= origem - 12) & (s.index < origem)])  # os mesmos números, nada do futuro
    teste = b[(b["trecho"] == "teste") & (b["horizonte"] == 1)]
    assert list(teste["alvo"]) == ["2026-06", "2026-07", "2026-08", "2026-09"]
    for r in teste.itertuples():  # h1 = último mês da janela (o stub repete o último valor)
        assert r.valor == pytest.approx(s[pd.Period(r.alvo, "M") - 1])


def test_autots_k_usa_o_k_esimo_colocado_e_falha_sem_ele():
    s = _serie()
    origem = pd.Period("2026-07", "M")
    p2 = regua.prever_de(A.AutoTSPosicao(2, busca=Stub()), s, origem, 3)
    assert p2["valor"].tolist() == pytest.approx([s[origem - 1] * 1.1] * 3)
    with pytest.raises(ValueError, match="3 modelos"):
        regua.prever_de(A.AutoTSPosicao(3, busca=Stub(n=2)), s, origem, 1)
    from ml import rodar

    r, _ = rodar.avaliar_modelo(A.AutoTSPosicao(3, busca=Stub(n=2)), {"Mercado": s})
    assert "erro" in r  # registrada, sem derrubar os outros modelos


def test_autots_conta_como_o_mais_complexo_no_desempate():
    """C1: empate (< 1 ponto) entre o AutoTS e a rede neural de 1 neurônio fica com a rede (mais simples)."""
    assert mp.complexidade("autots_1", "automatico") > mp.complexidade("mlp_16", "neural")

    def m(w, mod):
        return {"modulo": mod, "series": {"Mercado": {"metricas": {"1": {"wape": w}}}}}

    modelos = {"autots_1": m(0.120, "automatico"), "mlp_1": m(0.126, "neural"), "ref_media_6m": m(0.30, "referencia")}
    assert mp.escolher(modelos, "Mercado")["vencedor"] == "mlp_1"
    modelos["autots_1"] = m(0.10, "automatico")  # 2,6 pontos à frente: o AutoTS vence
    assert mp.escolher(modelos, "Mercado")["vencedor"] == "autots_1"


def test_comparacao_automatica_no_contrato():
    """P9: por série, os 3 do AutoTS, a rede neural, as referências e o vencedor, com o que o AutoTS escolheu em cada
    janela (gancho detalhe() gravado por ml/rodar.py)."""
    A.ESCOLHAS.clear()
    s = {"Inbound": _serie("Inbound"), "Mercado": _serie()}
    modelos = {}
    for nome, mod, obj in (("autots_1", "automatico", A.AutoTSPosicao(1, busca=Stub())),
                           ("autots_2", "automatico", A.AutoTSPosicao(2, busca=Stub())),
                           ("ref_media_6m", "referencia", None), ("mlp_1", "neural", None)):
        if obj is None:
            from ml.modelos import referencia
            obj = next(x for x in referencia.MODELOS if x.nome == "ref_media_6m") if mod == "referencia" else \
                next(x for x in referencia.MODELOS if x.nome == "ref_ultimo_mes")
        modelos[nome] = {"modulo": mod, "series": regua.avaliar(obj, s), "futuro": regua.prever_futuro(obj, s)}
        if mod == "automatico":
            modelos[nome]["detalhe"] = A.detalhe(nome)
    modelos["autots_3"] = {"modulo": "automatico", "erro": "ValueError: sem 3 modelos"}
    escolha = {t: mp.escolher(modelos, t) for t in s}
    c = mp.comparacao_automatica(modelos, escolha)
    for t in s:
        nomes = [x["nome"] for x in c[t]["linhas"]]
        assert nomes[:3] == ["autots_1", "autots_2", "autots_3"] and "mlp_1" in nomes and "ref_media_6m" in nomes
        a1 = c[t]["linhas"][0]
        assert a1["teste"]["n"] == 4 and a1["verificacao"]["n"] == 5
        assert [e["treino_fim"] for e in a1["escolhas"]][:1] == ["2025-12"] and a1["escolhas"][-1]["treino_fim"] == "2026-09"
        assert {e["modelo"] for e in a1["escolhas"]} == {"M1"}
        assert c[t]["linhas"][2]["falta"].startswith("ValueError")
        assert sum(x.get("vencedor", False) for x in c[t]["linhas"]) == 1
    assert A.detalhe("autots_1")["config"]["geracoes"] == 0 and A.detalhe("nao_existe") is None
