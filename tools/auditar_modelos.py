"""Recalcula métricas dos backtests salvos; não treina, publica ou acessa a rede."""
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]


def main():
    resultados = json.loads((RAIZ / 'ml/saida/resultados.json').read_text(encoding='utf-8'))
    previsao = json.loads((RAIZ / 'ml/saida/previsao.json').read_text(encoding='utf-8'))
    rel = {'carga': resultados['carga'], 'modelos': len(resultados['modelos']),
           'verificacoes': 0, 'divergencias': [], 'vencedores': {}}
    for nome, modelo in resultados['modelos'].items():
        for serie, resultado in modelo.get('series', {}).items():
            if 'backtest' not in resultado:
                continue
            for chave, metrica in resultado['metricas'].items():
                if chave == 'verificacao' and metrica.get('n_parcial') is not None:
                    # D56 exige os cinco meses; pontos parciais não formam verificação comparável.
                    continue
                linhas = [x for x in resultado['backtest'] if
                          (x['trecho'] == 'verificacao' if chave == 'verificacao' else
                           x['trecho'] == 'teste' and (chave == 'todos' or str(x['horizonte']) == chave))]
                if not linhas:
                    continue
                total = sum(x['real'] for x in linhas)
                erro = sum(abs(x['valor'] - x['real']) for x in linhas)
                # JSON preserva 2 casas nas previsões; a régua calculou com precisão completa.
                for k, calculado, tolerancia in [('wape', erro / total if total else None,
                                                 .005 * len(linhas) / total + 1e-8 if total else 0),
                                                ('mae', erro / len(linhas), .00500001)]:
                    rel['verificacoes'] += 1
                    salvo = metrica.get(k)
                    if (calculado is None) != (salvo is None) or (calculado is not None and abs(calculado-salvo) > tolerancia):
                        rel['divergencias'].append({'modelo': nome, 'serie': serie, 'trecho': chave,
                                                   'metrica': k, 'salvo': salvo, 'recalculado': calculado})
    for serie, nome in previsao['decisao']['vencedor'].items():
        modelo = resultados['modelos'][nome]
        s = modelo['series'][serie]
        teste = [x for x in s['backtest'] if x['trecho'] == 'teste' and x['horizonte'] == 1]
        sensibilidade = []
        for excluir in sorted({x['alvo'] for x in teste}):
            placar = []
            for n, m in resultados['modelos'].items():
                linhas = [x for x in m.get('series', {}).get(serie, {}).get('backtest', [])
                          if x['trecho'] == 'teste' and x['horizonte'] == 1 and x['alvo'] != excluir]
                if len(linhas) == len(teste)-1 and sum(x['real'] for x in linhas):
                    placar.append((sum(abs(x['valor']-x['real']) for x in linhas)/sum(x['real'] for x in linhas), n))
            sensibilidade.append({'mes_retirado': excluir, 'menor_wape_bruto': min(placar) if placar else None})
        rel['vencedores'][serie] = {'modelo': nome, 'metricas': s['metricas'],
            'futuro': modelo.get('futuro', {}).get(serie), 'sensibilidade_excluir_mes': sensibilidade,
            'nota': 'Sensibilidade interna; não é novo teste independente nem aplica desempate por simplicidade.'}
    destino = RAIZ / 'docs/validacao/auditoria_modelos_2026-10-26.json'
    destino.write_text(json.dumps(rel, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'verificacoes':rel['verificacoes'], 'divergencias':len(rel['divergencias']),
                      'modelos':rel['modelos']}, ensure_ascii=False))
    if rel['divergencias']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
