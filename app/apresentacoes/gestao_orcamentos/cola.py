"""Falas da cola do apresentador (D63, Caio, 28/10/2026): a narrativa da reunião, com os números ao vivo das mesmas
funções que montam as páginas (nenhuma consulta nova; sem números fixos).

Linha da apresentação, que cada página retoma em meia frase: a demanda quase dobrou → é concentrada nos exclusivos e
espalhada nos demais → quanto do que chegou já teve resposta (só dados, sem conclusão: a diretoria decide) → a mediana sai rápido, mas a parcela que passa de dois
dias consome a maior parte do tempo → o atraso é de processo, em poucas etapas → e a previsão diz que a pressão continua.

Cadência de cada fala: ponte com a página anterior → o número (com a deixa de mouse) → a leitura (um insight, uma
hipótese, às vezes uma pergunta para a sala) → conclusão (= mensagem da ficha) → gancho para a próxima. Vocabulário:
"mediana" (pedido do Caio), nunca "hora trabalhada". Só texto agregado, sem linhas do banco; nomes de talentos só os que
o Caio escolheu como exemplo em Talentos (28/10/2026), e só enquanto estiverem no top 10 da tela (`_linha`).
"""
import math
import re

from app import formato
from app.dados import DadosIndisponiveis
from . import apresentacao as paginas

IDS = ('demanda', 'talentos', 'atendimento', 'sla', 'estudo-1', 'estudo-2-1',
       'estudo-2-2', 'estudo-2-3', 'estudo-3', 'estudo-4', 'estudo-5', 'estudo-6',
       'estudo-7', 'estudo-8', 'previsao')


def exigir(valor):
    if not valor:
        raise DadosIndisponiveis('Sem dados suficientes para esta fala')
    return valor


def _h(valor) -> str:
    """Horas inteiras, meio para cima (a mesma leitura do "14 h" da tela)."""
    return f"{formato.inteiro(valor)} h"



def _falado(txt: str) -> str:
    """O tempo como está na tela ("25 h") dito em voz alta ("25 horas")."""
    return txt.removesuffix(' h') + (' hora' if txt.removesuffix(' h') == '1' else ' horas') if txt.endswith(' h') else txt


def _ate_o_dia(dias: str) -> str:
    """"6 dias" → "o sexto dia" (até o décimo); com fração ou acima disso, fica como está ("6,5 dias")."""
    ordem = ('primeiro', 'segundo', 'terceiro', 'quarto', 'quinto', 'sexto', 'sétimo', 'oitavo', 'nono', 'décimo')
    num = dias.split(' ')[0]
    return f"o {ordem[int(num) - 1]} dia" if num.isdigit() and 1 <= int(num) <= 10 else dias

def _ritmo(variacao) -> str:
    """Como falar a variação do ano: "quase o dobro" só quando for perto disso."""
    if variacao is None:
        return 'uma mudança de patamar'
    if variacao >= 0.95:
        return 'o dobro'
    if variacao >= 0.75:
        return 'quase o dobro'
    if variacao >= 0.3:
        return 'um crescimento forte'
    if variacao > 0:
        return 'um crescimento'
    return 'uma queda'


_MESES = ('janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 'julho', 'agosto', 'setembro', 'outubro',
          'novembro', 'dezembro')


# Big Brother de edições anteriores no top 10 dos exclusivos (Caio, 28/10/2026) e como ele os chama
_BBB_ANTIGOS = ('Juliette Freire', 'Beatriz Reis', 'Gilberto Nogueira', 'Renata Saldanha')
_APELIDO = {'Juliette Freire': 'a Juliette', 'Beatriz Reis': 'a Beatriz Reis', 'Gilberto Nogueira': 'o Gil do Vigor',
            'Renata Saldanha': 'a Renata Saldanha'}


def _media(linha: dict, meses) -> float:
    meses = list(meses)
    return sum((linha.get('meses') or {}).get(m, 0) for m in meses) / len(meses)


def _linha(top: dict, nome: str):
    """A linha de um talento no top 10 da tela (ou None, se ele saiu da lista)."""
    return next((x for x in top.get('linhas') or [] if x['talento'] == nome), None)


def _lista(nomes: list[str]) -> str:
    return nomes[0] if len(nomes) == 1 else ', '.join(nomes[:-1]) + ' e ' + nomes[-1]


def _passos(fala: list[str], gancho: str) -> list[list[str]]:
    """Roteiro = as deixas de mouse da própria fala, na ordem (cada uma com a frase que vem logo depois), mais o gancho."""
    passos = []
    for paragrafo in fala:
        for deixa, texto in re.findall(r'\[([^\]]+)\]\s*([^\[]+)', paragrafo):
            frase = re.split(r'(?<=[.?!])\s', texto.strip(), maxsplit=1)[0]
            passos.append([deixa, frase])
    return passos[:10] + ([['→ próxima', gancho]] if gancho else [])  # sem gancho: a página fecha na fala


def compor(ficha):
    n = formato.inteiro
    fontes = ('entrada',)
    periodo = ''
    if ficha == 'demanda':
        e = paginas.montar_inicio({})['entrada']
        periodo = f"{e['ano']} · {e['periodo']}"
        c = e.get('comparacao') or {}
        var = c.get('variacao')
        g = max(e['grupos'], key=lambda x: x['n']) if e['grupos'] else None
        tamanho = _ritmo(var)
        mensagem = (f"Chegou **{tamanho}** de pedidos: **{n(e['total'])}** em {e['ano']}" if var is not None and var >= 0.75
                    else f"Chegaram **{n(e['total'])}** pedidos em {e['ano']}") + (
            f", {formato.variacao(var)} sobre {e['ano'] - 1}." if var is not None else '.')
        fala = [
            f"Vamos começar pela demanda. Aqui estão todos os pedidos de orçamento que chegaram para a equipe. "
            f"[mouse no número grande] Até agora, já recebemos {n(e['total'])} pedidos em {e['ano']}.",
        ]
        if var is not None:
            # "sempre acima" só quando cada mês com comparação ficou acima do mesmo mês do ano anterior
            comparados = [m['anterior']['variacao'] for m in e.get('meses') or []
                          if m.get('total') and (m.get('anterior') or {}).get('variacao') is not None]
            todos = bool(comparados) and all(v > 0 for v in comparados)
            fala.append(
                f"[mouse na barra de {e['ano'] - 1}] No mesmo período do ano passado, foram {n(c['total'])} pedidos. "
                + (f"Praticamente {tamanho.replace('quase ', '')}: um aumento de {formato.variacao(var).lstrip('+')}."
                   if var >= 0.75 else f"Ou seja, {tamanho}: {formato.variacao(var)}.") +
                (" [mouse no gráfico mensal] E olhando o gráfico à direita, dá para ver que não tivemos um mês fora "
                 "da curva. " + (f"Comparando mês a mês com o ano passado, {e['ano']} ficou acima em todos os meses. Ou "
                              "seja, o aumento veio ao longo de todo o ano, não foi um período isolado." if todos else
                              "O volume ficou alto ao longo do ano, não foi um período isolado.")
                 if var > 0 else ''))
        if g:
            cresceu = g.get('variacao') is not None and g['variacao'] > 0
            outros = sorted((x for x in e['grupos'] if x is not g), key=lambda x: -x['n'])
            g2 = outros[0] if outros and (outros[0].get('variacao') or 0) > 0 else None
            fala.append(
                f"[mouse na tabela de tipos] E esse aumento veio principalmente do {g['nome']}. Sozinho, ele "
                f"representa {g['pct']}% dos pedidos que chegaram este ano" +
                (f" e cresceu {formato.variacao(g['variacao']).lstrip('+')} em relação ao ano passado." if cresceu
                 else '.') +
                (f" O {g2['nome']} também subiu, {formato.variacao(g2['variacao']).lstrip('+')}, mas foi o {g['nome']} "
                 f"que puxou o aumento do volume em {e['ano']}." if g2 else ''))
        # o mês em andamento (ou, sem ele, o último fechado) com análise mensal, em poucas frases: planta a ideia de que
        # todo mês começa com demanda represada (a conta completa vem no Atendimento)
        abertos = [m['chave'] for m in e.get('meses') or []
                   if m['total'] and not m.get('futuro') and m['chave'] in (e.get('meses_extrato') or [])]
        x = paginas.montar_inicio({'mes': abertos[-1]})['entrada'].get('extrato') if abertos else None
        if x and x['fila']['represados']:
            q, mes = x['fila'], x['nome'].split(' de ')[0].lower()
            fala.append(
                f"Um detalhe antes de seguir para a próxima página. [clica em {mes}] Se olharmos {mes} de perto, "
                f"entraram {n(q['novos'])} pedidos. [mouse em Represados do início do mês] Mas a equipe já "
                f"começou o mês com {n(q['represados'])} pedidos que vieram dos meses anteriores. Ou seja, todo mês a "
                "equipe começa com uma demanda represada. Temos algumas hipóteses. Uma pode ser o pedido que chega "
                "perto da virada do mês e acaba seguindo no mês seguinte. A outra são pendências de processo: "
                "falta de informação ou um pedido preso em alguma etapa. Na prática, deve ser uma mistura de cada "
                "coisa. "
                "[clica em Fechar]")
        gancho = ('Agora, o próximo passo é entender como esses pedidos se distribuem entre os talentos: exclusivos e '
                  'não exclusivos.')
        perguntas = [['É pico ou é patamar?', 'O mês a mês mostra o volume alto ao longo do ano; a previsão, no fim, '
                                               'diz se ele continua.'],
                     ['O que conta como pedido?', 'Cada orçamento aberto no board de Agenciamento, pela data de entrada; '
                                                  'o tipo de input vem do próprio board.']]
        evitar = 'Ler a tabela de tipos linha a linha: fique no maior grupo.'
    elif ficha == 'talentos':
        fontes = ('entrada', 'talentos', 'talentos_top')
        t = paginas.montar_talentos({})
        if t['em_atualizacao']:
            raise DadosIndisponiveis('Bases em conciliação')
        d = exigir(t['talentos'])
        periodo = f"{d['ano']} · {t['periodo']}"
        grupos = {g['nome'].lower(): g for g in d['grupos']}
        excl = grupos.get('exclusivos')
        nao = grupos.get('não exclusivos')
        top_e = (t['top'].get('exclusivo') or {}).get('pct')
        top_n = (t['top'].get('nao-exclusivo') or {}).get('pct')
        exigir(excl and nao)
        mensagem = (f"**{excl['pct']}%** da demanda é de exclusivos" +
                    (f", e dez nomes concentram **{top_e}%** dela" if top_e is not None else '') + '.')
        resto = max(0, 100 - excl['pct'] - nao['pct'])
        fala = [
            f"[mouse na barra do ano] Dos pedidos que chegaram, {excl['pct']}% são para os nossos talentos exclusivos e "
            f"{nao['pct']}% para as interveniências." +
            (f" Os outros {resto}% não conseguimos relacionar, por falta de informação na base." if resto else '') +
            " Com isso, já podemos dizer que a maior parte da demanda é para os nossos talentos exclusivos.",
        ]
        # exemplos citados pelo Caio (28/10/2026): só entram na fala enquanto estiverem no top 10 da tela
        top_ex = t['top'].get('exclusivo') or {}
        top_ne = t['top'].get('nao-exclusivo') or {}
        tati = _linha(top_ex, 'Tatiana Machado')
        esporte = [x for x in (_linha(top_ne, nome) for nome in ('Tiago Medeiros', 'Fred Bruno', 'Everaldo Marques'))
                   if x]
        if top_e is not None:
            # leitura do Caio (28/10/2026), conferida na carga: o BBB 2026 foi de 12/jan ao fim de abril. Cada frase só
            # entra se os meses da tela a sustentarem
            antigos = [x for x in (_linha(top_ex, nome) for nome in _BBB_ANTIGOS) if x]
            antigos_ok = antigos and all(len(x.get('meses') or {}) >= 9 for x in antigos)
            atuais = [x for x in (_linha(top_ex, nome) for nome in ('Chaiany Pinto Andrade', 'Maxiane Rodrigues')) if x]
            atuais_ok = atuais and all(not (x.get('meses') or {}).get(1)
                                       and all((x.get('meses') or {}).get(m) for m in range(5, 10)) for x in atuais)
            tati_ok = tati and (tati.get('meses') or {}).get(5) in sorted((tati.get('meses') or {}).values())[-2:]
            partes = [
                f"Se olharmos os exclusivos, [clica em Exclusivos] a demanda é concentrada: [mouse no top 10] o top 10 "
                f"reúne {top_e}% de todos os pedidos do grupo."]
            if antigos_ok or atuais_ok:
                partes.append("[mouse nos nomes do Big Brother] E vários nomes desse top 10 vieram do Big Brother." +
                              (" Os de edições antigas têm pedidos o ano todo." if antigos_ok else '') +
                              (" Já os da edição deste ano, assim que saíram da casa, começaram a receber pedidos "
                               "todos os meses." if atuais_ok else ''))
            if tati_ok:
                partes.append(
                    "Um outro caso interessante é o da Tati Machado: [mouse na linha da Tatiana Machado] em maio, quando "
                    "assumiu o Mais Você nas férias da Ana Maria Braga, ela teve um dos maiores meses do ano. Uma "
                    "hipótese é a exposição: quem está no ar acaba recebendo mais pedidos.")
            fala.append(' '.join(partes))
        if top_n is not None:
            fala.append(
                f"Já nas interveniências é o oposto. [clica em Não exclusivos] A procura é bem espalhada: o top 10 "
                f"soma só {top_n}% dos pedidos. [mouse no mapa de calor] E os picos que a gente vê aqui são, na maioria, "
                "de ex-participantes do Big Brother, puxados pelo programa.")
            if esporte:
                ano_todo = all(len(x.get('meses') or {}) >= 6 for x in esporte)
                fala[-1] += (
                    " [mouse nos nomes do esporte] E aparece também o pessoal do esporte, como " +
                    _lista(['o ' + x['talento'] for x in esporte]) + ". Dá para pensar que foi a Copa, " +
                    ("mas eles tiveram pedidos o ano todo, não só durante a Copa." if ano_todo else
                     "e vale acompanhar se o volume se mantém depois dela.") + " [clica em Todos]")
            else:
                fala[-1] += " [clica em Todos]"
        fala.append("Em resumo: nos exclusivos, a demanda é concentrada. Já nas interveniências, ela é pulverizada.")
        gancho = ('Agora que conhecemos um pouco a demanda e para quem ela vai, podemos começar a olhar o outro lado: a '
                  'equipe está dando conta de tudo o que entra?')
        perguntas = [['Quem são os do Big Brother antigo?', 'Juliette, Beatriz Reis, Gil do Vigor e Renata Saldanha, todos com pedidos de janeiro a outubro.'],
                     ['Por que olhar o top 10?', 'Mostra concentração: quando poucos nomes respondem por metade da '
                                                 'demanda exclusiva, agir neles tem efeito grande.'],
                     ['O que é "talento não informado"?', 'Pedido que entrou sem talento no board; é pouco e não muda a '
                                                          'leitura.']]
        evitar = 'Ler a lista de nomes: escolha um exemplo e siga.'
    elif ficha == 'atendimento':
        fontes = ('entrada', 'fluxo', 'atendimento')
        a = paginas.montar_atendimento({})
        f = exigir(a['fluxo_mes'])
        periodo = f"{f['ano']} · {a['atendimento']['periodo']}"
        resolvidos = f['pct_entregues'] + f['pct_sem_entrega']
        pcts = ((a.get('ritmo') or {}).get('quadro') or {}).get('pct') or []
        mensagem = (f"Resolvemos **{resolvidos}%** do que chegou: {f['pct_entregues']}% entregues e "
                    f"{f['pct_sem_entrega']}% sem seguimento.")
        fala = [
            "Até aqui, vimos que a demanda praticamente dobrou e que ela se concentra nos talentos exclusivos. Agora, "
            "vamos ver o que aconteceu com esses pedidos.",
            f"[mouse na faixa do topo] Dos {n(f['ano_recebidos'])} "
            f"pedidos que chegaram, {n(f['entregues_ano_total'])} foram entregues ao cliente e "
            f"{n(f['sem_entrega_ano_total'])} foram declinados, ou seja, não tiveram seguimento. Somando os dois, "
            f"{resolvidos}% do que chegou já teve resposta. [mouse em Em andamento] Os "
            f"outros {100 - resolvidos}%, que totalizam {n(f['ano_seguem'])} pedidos, estão em andamento: são os que a equipe "
            "está tocando hoje.",
        ]
        if pcts:
            fala.append(
                "[mouse na linha do % da tabela] Na tabela abaixo aparece a demanda represada de que falamos na "
                f"primeira página: todo mês, a equipe resolve cerca de {min(pcts)}% a {max(pcts)}% de tudo o que tem para "
                "atender. Para isso, temos as hipóteses que comentamos: pedidos que chegam no fim do mês ou que ficam "
                "presos por alguma pendência.")
        gancho = 'Agora, vamos ver quanto tempo leva para entregar um orçamento.'
        perguntas = [['Declinado é perda?', 'É pedido sem seguimento: decisão do mercado, do talento ou interna. Não é '
                                            'falha de entrega.'],
                     ['Por que o ano dá mais do que o melhor mês?', 'O mês carrega o que veio do mês anterior; o ano '
                                                                    'conta cada pedido uma vez.']]
        evitar = 'Abrir as dicas da tabela: leia um mês só, com o mouse na coluna.'
    elif ficha == 'sla':
        fontes = ('sla',)
        e = paginas.montar_sla({})['entrega']
        exigir(e['n_ano'])
        periodo = f"{e['periodo']} de {e['ano_num']}"
        grupos = {g['chave']: g for g in e['grupos']}
        tela = e['ano']['tela']
        lim = e['limite_dias']
        du = e.get('dias_uteis_cliente') or {}
        mensagem = (f"A mediana é de **{_h(e['mediana_h_trabalho'])}** úteis; **{tela['ate2']}%** saem em até {lim} "
                    f"dias e **{tela['acima2']}%** passam disso.")
        # na fala, os dias úteis vão inteiros ("cerca de 2"); a tela continua com a casa decimal
        dias = math.floor(du['valor'] + 0.5) if du.get('valor') is not None else None
        dias_txt = (f"{'' if dias == du['valor'] else 'cerca de '}{dias} {'dia útil' if dias == 1 else 'dias úteis'}"
                    if dias else '')
        # o exemplo da tela ("pedido na segunda às 10h, resposta na terça à tarde") dito como frase
        exemplo = (du.get('exemplo') or '').replace('pedido na ', 'o pedido chega na ', 1).replace(
            ', resposta ', ' e a resposta sai ', 1)
        fala = [
            "Aqui, essa página mostra quanto tempo a equipe leva para entregar um orçamento.",
            f"[mouse no {_h(e['mediana_h_trabalho'])}] Hoje, a equipe leva {n(e['mediana_h_trabalho'])} horas úteis "
            "para entregar um orçamento ao cliente, contando da entrada do pedido até a entrega." +
            (f" [mouse no {du['txt']}] No calendário de quem pede, isso equivale a {dias_txt}: por exemplo, "
             f"{exemplo}." if dias_txt and exemplo else ''),
        ]
        if 'exclusivos' in grupos and 'nao-exclusivos' in grupos:
            ge, gn = grupos['exclusivos'], grupos['nao-exclusivos']
            mais = gn['mediana_h_trabalho'] > ge['mediana_h_trabalho']
            fala.append(
                "Se a gente separar esse número entre exclusivos e interveniências, [clica em Exclusivos] os exclusivos "
                + (f"são um pouco mais rápidos, {n(ge['mediana_h_trabalho'])} horas, [clica em Não exclusivos] e as "
                   f"interveniências acabam demorando um pouco mais, {n(gn['mediana_h_trabalho'])} horas." if mais else
                   f"levam {n(ge['mediana_h_trabalho'])} horas [clica em Não exclusivos] e as interveniências, "
                   f"{n(gn['mediana_h_trabalho'])} horas.") + " [clica em Todos]")
        # fechamento (Caio, 28/10/2026): um dado novo da própria tela, sem veredito. O tempo de cada mês fechado
        # (o número sob a barra) e o mês com mais entregas; "mesma faixa" só se os meses variarem até 4 h
        fechados = [m for m in e['meses'] if m['n'] and not m['parcial'] and not m['futuro']]
        if len(fechados) >= 3:
            menor = min(fechados, key=lambda m: m['mediana'])
            maior = max(fechados, key=lambda m: m['mediana'])
            pico = max(fechados, key=lambda m: m['n'])
            def hora(m):
                # a mesma escrita do número sob a barra, dita em voz alta: "16,5 h" → "16 horas e meia"
                t = m['mediana_txt'].removesuffix(' h')
                return f"{t[:-2]} horas e meia" if t.endswith(',5') else f"{t} horas"
            if maior['mediana'] - menor['mediana'] <= 4:
                fala.append(
                    f"[mouse nos números sob cada mês] E esse tempo ficou na mesma faixa o ano todo: entre "
                    f"{hora(menor).removesuffix(' horas')} e {hora(maior)} para entregar um orçamento, mesmo com a "
                    f"demanda praticamente dobrando. [mouse em {pico['rotulo']}] Em {_MESES[int(pico['chave'][5:]) - 1]}, "
                    f"o mês com mais entregas, levamos, em geral, {hora(pico)} para entregar cada um dos orçamentos. "
                    "Ou seja, o volume aumentou e o tempo de entrega se manteve.")
        # o estudo abre pelo botão da lupa no SLA (fora da sequência das setas); do estudo, a saída é a Previsão
        gancho = "Antes de seguir, vou mostrar rapidamente como chegamos a esse valor. [clica na lupa, Como medimos]"
        perguntas = [['Por que mediana e não média?', 'Poucos casos muito longos puxam a média para cima; a mediana '
                                                      'mostra o pedido do meio.'],
                     ['E a meta?', f"A sugestão, ainda a oficializar, é metade dos orçamentos em até {lim} dias de "
                                   f"trabalho. Hoje, {tela['ate2']}% saem nesse prazo e {tela['acima2']}% passam disso."]]
        evitar = 'Chamar de "hora trabalhada" ou de "tempo de uma pessoa".'
    elif ficha.startswith('estudo-'):
        fontes = ('sla', 'fluxo')
        e = paginas.montar_estudo_sla({})
        r = exigir(e['recorte'])
        periodo = r['periodo']
        perguntas = [['Por que mediana e não média?', 'Poucos casos muito longos puxam a média para cima; a mediana '
                                                      'mostra o pedido do meio.']]
        evitar = 'Termos de estatística (distribuição, simetria, quartil): fale de pedido comum e pedido que trava.'
        if ficha == 'estudo-1':
            mensagem = 'O relógio corre da entrada à primeira versão, só no expediente.'
            fala = [
                "[mouse no topo do slide] Este é um pedido real, de ponta a ponta. [mouse na linha do tempo] O relógio "
                "começa quando a demanda entra e vai contando conforme o pedido avança no desenvolvimento. [mouse em "
                "Aguardando Feedback] Quando o orçamento chega ao cliente, o relógio para.",
            ]
            # gancho para o slide 2 (todos os orçamentos no histograma)
            gancho = ('Isso é um exemplo de um pedido. Agora, colocando toda a base do ano lado a lado, a gente começa a '
                      'entender de onde vem o SLA.')
            perguntas = [['E o tempo total que o cliente espera?', 'Também está na tela, em dias úteis; o SLA é a nossa '
                                                                   'parte, até a primeira versão.'],
                         ['O que não entra na conta?', 'Só conta o expediente. Standby, ajustes e a espera da marca e do '
                                                       'cliente ficam de fora (a parte de baixo do slide).']]
        elif ficha.startswith('estudo-2-'):
            x = exigir(e['exploracao'])
            b = x['box']
            if ficha == 'estudo-2-1':
                mensagem = f"Poucos casos longos puxam a média para **{x['media_txt']}**; a mediana fica em **{x['mediana_txt']}**."
                # D63 (Caio, 28/10/2026): duas ou três frases por passo, com o termo certo, até chegar à mediana
                fala = [
                    "[mouse no gráfico da esquerda] Aqui estão os orçamentos entregues no ano; cada barra é uma faixa de "
                    "tempo: à esquerda, os que levaram menos, e à direita, os que levaram mais. [mouse na direita do "
                    "gráfico] O gráfico tem uma assimetria positiva, ou seja, poucos casos, com muitas horas, puxam a "
                    f"média para {_falado(x['media_txt'])}. [mouse no típico] Para esses outliers não distorcerem o "
                    "número, a métrica que usamos é a mediana; por isso chegamos ao valor de "
                    f"{_falado(x['mediana_txt'])}.",
                ]
                # sem "sino" nem "distribuição normal" na fala (Caio): "normal" soaria como "o que deveria ser"
                gancho = ('E dá para ver isso de outro jeito: comparando com como os tempos seriam se fossem bem '
                          'distribuídos. [clica em Próxima: Sino]')
            elif ficha == 'estudo-2-2':
                mensagem = 'Não há um tempo único: existe o pedido comum e o pedido que trava.'
                fala = [
                    "[mouse na linha pontilhada do gráfico da esquerda] No gráfico da esquerda, a linha pontilhada mostra "
                    "como ele seria se os dados fossem bem distribuídos. [mouse na reta] No gráfico menor, à direita, é "
                    "como se a gente esticasse essa linha numa reta: se os dados fossem bem distribuídos, todos os pontos "
                    "cairiam em cima dela. [mouse nas bolinhas que sobem] Os pontos que saem da reta são os pedidos que "
                    "fogem do tempo esperado.",
                ]
                gancho = ('Para saber quantos são esses pedidos, a gente separa os orçamentos por faixa de tempo. [clica em '
                          'Próxima: Faixas]')
            else:
                mensagem = f"Três em cada quatro ficam prontos em até **{b['q3_txt']}**; **{b['fora']}%** passam de {b['lim_txt']}."
                # as quatro faixas da tela (rápidos, comuns, demorados, fora da curva), com os % e os limites dela
                pr, pc, pd_, po = b['pcts']
                fala = [
                    f"[mouse nas faixas] Separando os orçamentos por faixa de tempo: {pr}% saem em até "
                    f"{_falado(b['q1_txt'])}, {'metade' if pc == 50 else f'{pc}%'} fica entre "
                    f"{b['q1_txt'].removesuffix(' h')} e {_falado(b['q3_txt'])}, e {pd_}% vão até "
                    f"{_falado(b['lim_txt'])}. [mouse em Fora da curva] Os outros {po}%, acima disso, são os outliers. "
                    f"Eles continuam na conta, mas, como usamos a mediana, não distorcem as {_falado(x['mediana_txt'])}.",
                ]
                gancho = 'Para ficar mais fácil de enxergar, vamos ver isso em 100 pedidos.'
        elif ficha in ('estudo-3', 'estudo-4'):
            t = exigir(e['tempo'])
            if ficha == 'estudo-3':
                mensagem = f"De cada 100 pedidos, **{t['a']}** saem em até dois dias e **{t['b']}** passam disso."
                quase = ', quase metade,' if 40 <= t['b'] < 50 else ''
                # "ao acaso": é a proporção da base dita como 100 pedidos sorteados (o esperado, não um sorteio na tela)
                fala = [
                    f"[mouse nos quadradinhos] Se pegássemos 100 pedidos ao acaso, {t['a']} ficariam prontos em até 2 dias "
                    f"de trabalho. Os outros {t['b']}{quase} passariam disso.",
                ]
                # fechamento (Caio, 28/10/2026): a curva acumulada da direita, nos marcos que a tela escreve
                m = {x['chave']: x for x in ((e.get('cem') or {}).get('curva') or {}).get('marcos', [])}
                # só dois marcos, para quem é de fora da área (Caio): 2 dias e o de 90 pedidos
                if {'m2', 'm90'} <= m.keys():
                    # a mensagem da curva (Caio): por que mostrar assim — sobe rápido no começo e depois vai deitando
                    fala.append(
                        "[mouse na curva da direita] A curva da direita vai somando os pedidos que ficam prontos, dia após "
                        f"dia. [mouse em 2 dias] Nos 2 primeiros dias, {m['m2']['pct']} já saíram. [mouse em "
                        f"{m['m90']['dias']}] Mas, para chegar a 90 pedidos, é preciso esperar até "
                        f"{_ate_o_dia(m['m90']['dias'])}. Ou seja, a curva sobe rápido no começo: a maioria sai logo, e os "
                        "últimos pedidos levam bem mais tempo para serem entregues. Uma hipótese é o que já comentamos: "
                        "pedidos que ficam presos em alguma etapa ou esperando alguma informação.")
                gancho = f"Na próxima página, vamos analisar quanto tempo a equipe dedica para entregar esses {t['b']} pedidos."
            else:
                ha = t.get('ha', 100 - t['hb'])
                mensagem = f"Os **{t['b']}%** que passam de dois dias consomem **{t['hb']}%** do tempo."
                fala = [
                    "[mouse no quadro da esquerda] Aqui a gente vê quanto tempo a equipe leva. Os "
                    f"{t['a']}% de pedidos que saem em até 2 dias consomem {ha}% das horas da equipe. [mouse no quadro da "
                    f"direita] Já os {t['b']}% que passam de 2 dias consomem {t['hb']}%." +
                    # conclusão para a diretoria (Caio, 28/10/2026): o que os números querem dizer, apoiada no cartão
                    # "Fluxo" da própria tela; "horas da equipe" é o tempo do pedido com a equipe, não ocupação de pessoas
                    # condicional, sem afirmar capacidade: a diretoria tira a conclusão (Caio)
                    (" Ou seja, a maior parte do tempo da equipe vai para a parcela menor dos pedidos. [mouse em Fluxo] "
                     "Uma hipótese: se a gente conseguir reduzir o tempo desses pedidos, a equipe atende a mesma demanda "
                     "consumindo bem menos do seu tempo."
                     if t['b'] < t['a'] and t['hb'] > 50 else ''),
                    # frentes citadas pelo Caio (28/10/2026); ditas como expectativa, sem prometer resultado
                    "Para isso, já temos algumas frentes em andamento: a LIA, que faz a leitura automática dos e-mails, e "
                    "a precificação automática, que estamos testando. A ideia é acompanhar o SLA nos próximos meses e "
                    "ver se esses números diminuem.",
                ]
                gancho = ('Na próxima página, vamos ver se isso aconteceu em um mês específico ou ao longo do ano '
                          'todo.')
                perguntas = [['Isso é a ocupação das pessoas?', 'Não: é o tempo do pedido nas etapas. Mostra onde ele '
                                                                'fica parado, não quanto alguém trabalhou.'],
                             ['Por que esses pedidos demoram?', 'Hipóteses: informação indo e voltando entre áreas, o '
                                                                'mesmo dado preenchido em vários lugares, validações em '
                                                                'cadeia e pouca automação.']]
        elif ficha == 'estudo-5':
            t = exigir(e['meses_estudo'])
            valores = exigir([m['b'] for m in t['meses'] if m['b'] is not None])
            mensagem = f"Todo mês, entre **{min(valores)}%** e **{max(valores)}%** passam de dois dias: é padrão, não exceção."
            # curto (Caio, 28/10/2026): passa rápido; "não é sazonal" só enquanto os meses ficarem numa faixa estreita
            fala = [
                "[mouse no gráfico] Olhando mês a mês, dá para ver que " +
                ("não é um problema sazonal: " if max(valores) - min(valores) <= 15 else '') +
                f"a parcela que passa de 2 dias fica entre {min(valores)}% e {max(valores)}% o ano todo.",
            ]
            gancho = 'Na próxima página, vamos ver em quais etapas esse tempo se concentra.'
        elif ficha == 'estudo-6':
            t = exigir(e['travas'])
            st = t['status'][:3]
            exigir(st)
            lista = ', '.join(f"{s['nome']} ({s['pct_txt']})" for s in st)  # os nomes como estão na tela
            mensagem = f"O tempo de quem trava se concentra na etapa **{st[0]['nome']}** ({st[0]['pct_txt']})."
            # curto e focado (Caio, 28/10/2026): a fila de entrada (a surpresa) e a maior etapa; nomes como na tela
            por_nome = {x['nome']: x for x in t['status']}
            fila, elab = por_nome.get('Fila de entrada'), por_nome.get('Em elaboração')
            # o % da tela é a parte do tempo dos pedidos que passaram do normal em cada etapa (K4), somando 100% entre
            # as etapas; elaboração é trabalho, não espera, por isso "demoram mais do que o normal" e não "parados"
            fala = ["[mouse nas etapas] Aqui separamos os pedidos por etapa, para ver onde eles demoram mais do que o "
                    "normal."]
            if fila and elab and elab['pct_txt'] == st[0]['pct_txt']:
                juntas = int(fila['pct_txt'].rstrip('%')) + int(elab['pct_txt'].rstrip('%'))
                # um tópico por parágrafo (Caio, 29/10/2026): fica mais fácil de ler na cola
                fala += [
                    f"[mouse em Fila de entrada] Um ponto que me chamou atenção é a fila de entrada, com "
                    f"{fila['pct_txt']} desse tempo: o pedido é cadastrado, mas fica parado sem ser puxado para a "
                    "elaboração.",
                    f"[mouse em Em elaboração] O outro é a elaboração, com {elab['pct_txt']}, que é quando a equipe está "
                    "de fato fazendo o orçamento.",
                    ("Ou seja, mais da metade desse tempo" if juntas > 50 else f"Ou seja, {juntas}% desse tempo") +
                    " está concentrada em dois momentos: na espera para começar e no desenvolvimento de fato.",
                    "Acredito que garantir que o pedido não fique muito tempo parado na fila seria um ganho de processo.",
                ]
            else:
                fala[0] += f" [mouse na maior barra] O tempo se concentra em poucas etapas: {lista}."
            gancho = ''  # Caio (29/10/2026): a página fecha na hipótese, sem gancho
            perguntas = [['Quem age em cada etapa?', 'Cada etapa tem um responsável no fluxo; o pedido desta reunião é '
                                                     'definir o plano com cada um.']]
        elif ficha == 'estudo-7':
            t = exigir(e['tipos'])
            linhas = sorted(t['linhas'], key=lambda x: x['n'], reverse=True)
            maiores, pior = linhas[:2], max(linhas, key=lambda x: x['b'])
            mensagem = f"Cada tipo trava diferente: **{pior['tipo']}** é o que mais passa de dois dias ({pior['b']}%)."
            fala = [
                "[mouse na tabela] Por tipo de pedido, nos dois maiores: " +
                '; '.join(f"{l['tipo']}, {l['b']}% dos {n(l['n'])} passam de dois dias" for l in maiores) + '.',
                f"[mouse no maior %] O que mais passa é {pior['tipo']}, com {pior['b']}%. Não dá para tratar tudo com a "
                "mesma receita: cada tipo trava num lugar diferente.",
            ]
            gancho = 'O que os dados nos mostraram, então?'
            perguntas = [['Um tipo pequeno com % alto importa?', 'Pesa menos no total, mas mostra um fluxo que vale '
                                                                 'olhar de perto.']]
        else:
            c = exigir(e['conclusao'])
            mensagem = 'O pedido comum sai rápido; o atraso é de processo, em poucas etapas.'
            # resumo do estudo em poucas frases (Caio, 29/10/2026), com os números dos próprios slides; cada parte só
            # entra se o dado dela estiver na carga
            x, tm = e.get('exploracao') or {}, e.get('tempo') or {}
            ms = [m['b'] for m in (e.get('meses_estudo') or {}).get('meses', []) if m.get('b') is not None]
            por_nome = {s_['nome']: s_ for s_ in (e.get('travas') or {}).get('status', [])}
            # enxuto (Caio, 29/10/2026): um parágrafo de números e um da trava; a passagem para a Previsão ele improvisa
            fala = ["[mouse no topo do slide] Resumindo tudo:" +
                    (f" hoje, a equipe leva {_falado(x['mediana_txt'])} úteis para entregar um orçamento." if
                     x.get('mediana_txt') else '') +
                    (f" {tm['a']}% dos pedidos ficam prontos em até 2 dias, e os outros {tm['b']}% consomem {tm['hb']}% "
                     "do tempo da equipe." if tm.get('a') is not None else '') +
                    (" Não é um problema sazonal: temos esse comportamento o ano todo." if ms and
                     max(ms) - min(ms) <= 15 else '')]
            if 'Fila de entrada' in por_nome and 'Em elaboração' in por_nome:
                fala.append("E, basicamente, os pedidos travam em dois momentos: na fila de entrada e na elaboração.")
            gancho = 'Próxima página: Previsão.'
    elif ficha == 'previsao':
        t = exigir(paginas.montar_previsao({})['t'])
        periodo = f"Retrato até {t['retrato']['ate_txt']} · modelo gerado em {formato.atualizado(t['gerado_em'])}"
        # D63 (Caio, 29/10/2026): a página conta o que estamos começando a fazer e dá uma pincelada nos primeiros
        # resultados, sem explicar o modelo e sem concluir; o erro dos testes fica nas perguntas
        fala = ["Aqui a gente já está começando a trabalhar com modelos de machine learning. Até agora, olhamos o nosso "
                "histórico para analisar os nossos resultados; a partir desse histórico, queremos começar a olhar para frente."]
        previstos, erros = [], []
        for c in t['colunas']:
            if c.get('nao_se_aplica') or not c.get('confiavel'):
                continue
            futuros = [m for m in c['meses'] if not m['vigente'] and m.get('valor') is not None]
            if futuros:
                # só o próximo mês (Caio, 29/10/2026), em dezenas ("cerca de 520"); a tela mostra o número exato
                prox = futuros[0]
                previstos.append((c['titulo'], n(round(prox['valor'] / 10) * 10)))
                mes_prox = prox['rotulo']
            if c.get('metricas'):
                erros.append(f"{formato.pct(c['metricas']['wape'])} no {c['titulo']}")
        if previstos:
            (t1, v1), resto = previstos[0], previstos[1:]
            fala.append("Já rodamos alguns modelos, e eles começam a trazer os primeiros resultados. Para o próximo mês, "
                        f"{mes_prox}, [mouse em {t1}] a previsão é de cerca de {v1} pedidos no {t1}" +
                        ''.join(f"; [mouse em {ti}] no {ti}, cerca de {vi}" for ti, vi in resto) + '.')
        fala.append("Esses resultados ainda não são o ideal, porque temos vários problemas de dados, mas já estamos "
                    "tratando isso para que, mais para frente, sejam mais assertivos.")
        mensagem = 'Começamos a olhar para frente: os primeiros modelos já trazem resultados, ainda em ajuste.'
        gancho = 'Próxima página: Encerramento.'
        perguntas = [['Dá para confiar no número?', 'Como ordem de grandeza, sim: nos meses de teste' +
                      (f" ({t['teste_txt']}), o erro médio ficou em " + ' e '.join(erros) if erros else '') +
                      '. Não é para cravar o mês.'],
                     ['Por que nem todo grupo tem previsão?', 'Onde a série é curta ou instável, preferimos não mostrar '
                                                              'um número que não se sustenta.']]
        evitar = 'Ler a faixa provável em voz alta ou prometer o número exato do mês.'
    else:
        raise ValueError('Ficha inválida')
    passos = _passos(fala, gancho)
    if gancho:
        fala.append(gancho)
    return {'fala': fala, 'mensagem': mensagem, 'passos': passos, 'perguntas': perguntas,
            'evitar': evitar,
            'nota': 'Recorte: Todos. Quando a fala manda clicar num filtro, volte a Todos antes de seguir.',
            'periodo': periodo, 'fontes': fontes}
