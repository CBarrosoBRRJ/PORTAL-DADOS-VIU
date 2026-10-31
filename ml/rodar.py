"""Roda os modelos registrados em ml/modelos/*.py na régua única (protocolo D48 + R7 da D56) e grava os resultados.

D56 (Caio, 26/10/2026): TODOS os modelos rodam em TODAS as 4 séries (Inbound, Mercado, Mercado exclusivos, Mercado não
exclusivos; ml/dados.py, S1–S4), cada uma com o seu snapshot; não há mais repartição por proporção (ml/filtros.py saiu).
Modelo que não tem meses de treino suficientes numa série fica "não se aplica" só naquela série (régua R7).

  python -m ml.rodar                                   todos os módulos + previsao.json
  python -m ml.rodar --modulo arimax                   só ml/modelos/arimax.py (e junta tudo de novo)
  python -m ml.rodar --modulo arimax --modelo arima_100_ct   só um modelo do módulo
  python -m ml.rodar --modulo neural --sem-juntar      só grava ml/saida/modelos/neural.json (rodadas em paralelo)
  python -m ml.rodar --juntar                          só junta ml/saida/modelos/*.json e refaz previsao.json
  python -m ml.rodar --rotina                          execução MENSAL (D48, regra J1 de app/.../previsao/job.py):
                                                       snapshot novo do BigQuery (só SELECT); se o último mês fechado
                                                       ainda não tem retrato, roda todos os modelos e grava
                                                       o retrato; se já tem, só atualiza o acompanhamento do mês em
                                                       andamento (realizado até a véspera da carga), sem recalcular
  python -m ml.rodar --rotina --sem-extrair            idem, com o snapshot que já está em ml/dados
  python -m ml.rodar --rotina --forcar                 refaz o retrato do mês mesmo que já exista
  python -m ml.rodar --acompanhamento                  só o snapshot + o acompanhamento do mês em andamento
  python -m ml.rodar --sensibilidade                   D56: todos os modelos nas séries de exclusividade estendidas com a
                                                       silver 2025 (fonte fraca) -> ml/saida/sensibilidade_2025.json

Cada módulo grava ml/saida/modelos/<modulo>.json (rodadas em paralelo não se sobrescrevem); depois tudo é juntado em
ml/saida/resultados.json e o contrato da página em ml/saida/previsao.json (ml/previsao.py). Modelo que precisa de mais
meses do que a janela fica "não se aplica" (R4); que precisa de mais meses do que a série tem, só naquela série (R7).
"""

import argparse
import importlib
import json
import os
import pkgutil
import time
import traceback
from pathlib import Path

from ml import modelos as pacote
from ml import previsao, regua

SAIDA = Path(__file__).resolve().parent / "saida"
POR_MODULO = SAIDA / "modelos"
RESULTADOS = SAIDA / "resultados.json"
TRAVA = SAIDA / "rotina.lock"  # o site não dispara outra rotina enquanto esta existir (app/.../previsao/job.py)
ESTADO = SAIDA / "rotina_estado.json"  # J4: última tentativa (início, fim, código, erro), lida pela página
PROTOCOLO = {"nome": "D56", "base": "D48", "janela": regua.JANELA, "teste": [str(m) for m in regua.TESTE],
             "verificacao": [str(m) for m in regua.VERIFICACAO], "horizontes": list(regua.HORIZONTES),
             "metrica_principal": "wape", "criterio": "menor WAPE no horizonte 1 de jun–set/2026; empate (< 1 ponto) "
             "= o mais simples", "faixa": "p10-p90 (80%)",
             "series_curtas": "janela expansiva (até 12 meses); mínimo de treino por modelo (R7); verificação só completa",
             "minimo_curto": regua.MINIMO_CURTO}


def _limpo(o):
    """JSON sem NaN (vira null)."""
    if isinstance(o, float) and o != o:
        return None
    if isinstance(o, dict):
        return {k: _limpo(v) for k, v in o.items()}
    if isinstance(o, list):
        return [_limpo(v) for v in o]
    return o


def avaliar_modelo(m, series) -> tuple[dict, str]:
    """Um modelo na régua: métricas, backtest e futuro por série. R4 (não se aplica em nenhuma série) e falhas ficam no
    topo; R7 (D56: não se aplica só numa série curta) fica em series[nome] = {"nao_se_aplica": motivo}."""
    base = {"descricao": getattr(m, "descricao", ""), "minimo_treino": regua.minimo(m)}
    try:
        regua.verificar_aplica(m)
    except regua.NaoSeAplica as e:
        return {**base, "nao_se_aplica": str(e)}, f"não se aplica: {e}"
    por_serie, futuro, partes = {}, {}, []
    for nome, serie in series.items():
        try:
            por_serie[nome] = regua.avaliar(m, {nome: serie})[nome]
            futuro[nome] = regua.prever_futuro(m, {nome: serie})[nome]
            partes.append(f"{nome} {por_serie[nome]['metricas']['1']['wape']:.1%}")
        except regua.NaoSeAplica as e:
            por_serie[nome] = {"nao_se_aplica": str(e)}
            partes.append(f"{nome} n/a")
        except Exception as e:  # registra a falha sem derrubar os outros modelos nem as outras séries
            por_serie[nome] = {"erro": f"{type(e).__name__}: {e}", "trace": traceback.format_exc()[-2000:]}
            partes.append(f"{nome} falhou")
    if all("nao_se_aplica" in v for v in por_serie.values()):
        motivo = next(iter(por_serie.values()))["nao_se_aplica"]
        return {**base, "nao_se_aplica": motivo}, f"não se aplica: {motivo}"
    if all("erro" in v for v in por_serie.values()):
        e = next(iter(por_serie.values()))
        return {**base, "erro": e["erro"], "trace": e["trace"]}, e["erro"]
    return {**base, "series": por_serie, "futuro": futuro}, "WAPE h1 jun–set  " + "  ".join(partes)


def rodar_modulo(nome_modulo: str, so_modelo=None, series=None, meta=None, pasta=POR_MODULO) -> dict:
    """so_modelo: um nome ou um conjunto de nomes (os outros modelos do arquivo ficam como estavam, com a carga em
    que foram medidos)."""
    if series is None:
        series, meta = regua.carregar_recortes()
    so = {so_modelo} if isinstance(so_modelo, str) else (set(so_modelo) if so_modelo else None)
    mod = importlib.import_module(f"ml.modelos.{nome_modulo}")
    arq = Path(pasta) / f"{nome_modulo}.json"
    saida = {"modulo": nome_modulo, "carga": meta, "protocolo": PROTOCOLO["nome"], "modelos": {}}
    if so and arq.exists():
        antigo = json.loads(arq.read_text(encoding="utf-8"))
        if antigo.get("protocolo") == PROTOCOLO["nome"]:
            saida["modelos"] = antigo.get("modelos", {})
            for r in saida["modelos"].values():  # quem não roda agora guarda a carga do arquivo antigo
                r.setdefault("carga", antigo.get("carga", {}).get("processado_em"))
    for m in mod.MODELOS:
        if so and m.nome not in so:
            continue
        t0 = time.time()
        r, resumo = avaliar_modelo(m, series)
        r["modulo"] = nome_modulo
        if callable(getattr(mod, "detalhe", None)) and (det := mod.detalhe(m.nome)):
            r["detalhe"] = det  # D55: o que a busca automática (AutoTS) escolheu em cada janela
        r["segundos"] = round(time.time() - t0, 1)
        r["carga"] = meta["processado_em"]
        saida["modelos"][m.nome] = r
        print(f"{m.nome:32s} {resumo}", flush=True)
    arq.parent.mkdir(parents=True, exist_ok=True)
    arq.write_text(json.dumps(_limpo(saida), ensure_ascii=False, indent=1), encoding="utf-8")
    return saida


def juntar(series=None, meta=None, pasta=POR_MODULO, destino=RESULTADOS) -> dict:
    if series is None:
        series, meta = regua.carregar_recortes()
    tudo = {"carga": meta, "regua": PROTOCOLO,
            "historico": {t: {str(k): float(v) for k, v in s.items()} for t, s in series.items()}, "modelos": {}}
    for arq in sorted(Path(pasta).glob("*.json")):
        d = json.loads(arq.read_text(encoding="utf-8"))
        if d.get("protocolo") != PROTOCOLO["nome"]:
            print(f"aviso: {arq.name} é de outro protocolo; ignorado (rode o módulo de novo)")
            continue
        if d.get("carga", {}).get("processado_em") != meta["processado_em"]:
            raise ValueError(f"{arq.name} é de outra carga; rode o módulo de novo antes de juntar")
        for r in d["modelos"].values():
            r.setdefault("carga", d.get("carga", {}).get("processado_em"))
            if r['carga'] != meta['processado_em']:
                raise ValueError(f"{arq.name} contém modelo de outra carga; refaça o módulo completo")
        tudo["modelos"].update(d["modelos"])
    melhor = {}
    for tipo in series:
        melhor[tipo] = {}
        for h in [*map(str, regua.HORIZONTES), "todos"]:
            refs = [(n, m["series"][tipo]["metricas"][h]["wape"]) for n, m in tudo["modelos"].items()
                    if n.startswith("ref_") and "metricas" in m.get("series", {}).get(tipo, {})
                    and m["series"][tipo]["metricas"][h]["wape"] is not None]
            if refs:
                n, w = min(refs, key=lambda x: x[1])
                melhor[tipo][h] = {"modelo": n, "wape": w}
    tudo["melhor_referencia"] = melhor
    Path(destino).parent.mkdir(parents=True, exist_ok=True)
    Path(destino).write_text(json.dumps(_limpo(tudo), ensure_ascii=False, indent=1), encoding="utf-8")
    return tudo


def _previsao() -> None:
    try:
        p = previsao.gravar()
        print(f"gravado {previsao.PREVISAO} (retrato de {p['retrato']['mes_fechado']})")
    except Exception as e:  # noqa: BLE001 — sem resultado válido: a página segue com o último arquivo válido
        print(f"previsao.json não gravado: {type(e).__name__}: {e}")
        raise  # a última previsão continua válida; a execução atual deve registrar falha


def todos_os_modulos() -> list[str]:
    return [m.name for m in pkgutil.iter_modules(pacote.__path__)]


def rotina(extrair: bool = True, forcar: bool = False) -> str:
    """Execução mensal (D48). Devolve "retrato" (modelos refeitos) ou "acompanhamento" (só o realizado do mês em
    andamento). Trava em ml/saida/rotina.lock enquanto roda."""
    TRAVA.parent.mkdir(parents=True, exist_ok=True)
    with TRAVA.open('x', encoding='utf-8') as trava:
        trava.write(f"{os.getpid()} {time.strftime('%Y-%m-%d %H:%M:%S')}")
    try:
        if extrair:
            from ml import dados
            dados.gravar()  # BigQuery, só SELECT (grava também os snapshots por série, D56)
        series, meta = regua.carregar_recortes()
        if not forcar and previsao.retrato_existe(meta["mes_fechado"]):
            if not previsao.atualizar_acompanhamento():
                raise ValueError('Acompanhamento não atualizado: retrato ausente ou mês incompatível')
            print(f"retrato de {meta['mes_fechado']} já existe: só o acompanhamento foi atualizado")
            return "acompanhamento"
        for modulo in todos_os_modulos():
            rodar_modulo(modulo, None, series, meta)
        juntar(series, meta)
        _previsao()
        return "retrato"
    finally:
        TRAVA.unlink(missing_ok=True)


def sensibilidade(destino: Path = SAIDA / "sensibilidade_2025.json") -> dict:
    """D56 (S5): todos os modelos nas séries de exclusividade do Mercado estendidas para trás com a silver 2025 (fonte
    fraca). Não vai à tela: mede se o histórico de 2025 mudaria o vencedor ou o erro (docs/paginas/previsao.md, 5.8)."""
    series = regua.carregar_sensibilidade()
    saida = {"protocolo": PROTOCOLO["nome"], "series": {n: {str(k): v for k, v in s.items()} for n, s in series.items()},
             "modelos": {}}
    for nome_modulo in todos_os_modulos():
        mod = importlib.import_module(f"ml.modelos.{nome_modulo}")
        for m in mod.MODELOS:
            r, resumo = avaliar_modelo(m, series)
            r["modulo"] = nome_modulo
            r.pop("trace", None)
            for v in r.get("series", {}).values():
                v.pop("trace", None)
            saida["modelos"][m.nome] = r
            print(f"{m.nome:32s} {resumo}", flush=True)
    destino.write_text(json.dumps(_limpo(saida), ensure_ascii=False, indent=1), encoding="utf-8")
    return saida


def acompanhamento(extrair: bool = True) -> None:
    # G4-N13: a mesma trava da rotina (dois jobs nunca rodam juntos, mesmo depois de um --reload do site)
    TRAVA.parent.mkdir(parents=True, exist_ok=True)
    with TRAVA.open('x', encoding='utf-8') as trava:
        trava.write(f"{os.getpid()} {time.strftime('%Y-%m-%d %H:%M:%S')}")
    try:
        if extrair:
            from ml import dados
            dados.gravar()
        if not previsao.atualizar_acompanhamento():
            raise ValueError('Acompanhamento não atualizado: retrato ausente ou mês incompatível')
    finally:
        TRAVA.unlink(missing_ok=True)


def _estado(**campos) -> None:
    """J4 (G1-N11): grava a última tentativa de forma atômica (temporário + troca)."""
    ESTADO.parent.mkdir(parents=True, exist_ok=True)
    tmp = ESTADO.with_suffix(".tmp")
    tmp.write_text(json.dumps(campos, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, ESTADO)


def _registrado(modo: str, funcao, *args, **kwargs):
    """Roda a rotina ou o acompanhamento registrando início, fim, código (0 = ok) e o erro, se houver."""
    inicio = time.strftime("%Y-%m-%dT%H:%M:%S")
    _estado(modo=modo, inicio=inicio, fim=None, codigo=None, erro=None)
    try:
        r = funcao(*args, **kwargs)
    except BaseException as e:
        _estado(modo=modo, inicio=inicio, fim=time.strftime("%Y-%m-%dT%H:%M:%S"), codigo=1,
                erro=f"{type(e).__name__}: {e}"[:500])
        raise
    _estado(modo=modo, inicio=inicio, fim=time.strftime("%Y-%m-%dT%H:%M:%S"), codigo=0, erro=None)
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--modulo")
    ap.add_argument("--modelo")
    ap.add_argument("--juntar", action="store_true")
    ap.add_argument("--sem-juntar", action="store_true")
    ap.add_argument("--rotina", action="store_true")
    ap.add_argument("--acompanhamento", action="store_true")
    ap.add_argument("--sem-extrair", action="store_true")
    ap.add_argument("--forcar", action="store_true")
    ap.add_argument("--sensibilidade", action="store_true")
    a = ap.parse_args()
    if a.sensibilidade:
        sensibilidade()
        return
    if a.rotina:
        print(_registrado("rotina", rotina, extrair=not a.sem_extrair, forcar=a.forcar))
        return
    if a.acompanhamento:
        _registrado("acompanhamento", acompanhamento, extrair=not a.sem_extrair)
        return
    series, meta = regua.carregar_recortes()
    if not a.juntar:
        for n in ([a.modulo] if a.modulo else todos_os_modulos()):
            rodar_modulo(n, a.modelo, series, meta)
    if a.sem_juntar:
        return
    juntar(series, meta)
    print(f"gravado {RESULTADOS}")
    _previsao()


if __name__ == "__main__":
    main()
