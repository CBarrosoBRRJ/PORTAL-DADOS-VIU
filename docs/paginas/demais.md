# Fichas — seções em máscara (sem números)

Estas seções não mostram números à diretoria. Desde a D30 (23/10/2026) cada uma aparece **em máscara**: a pergunta da
seção como título, o selo "Aguardando dados" (ícone + texto), o motivo, as pendências da seção (dado · onde · quem,
vindas de `gestao_orcamentos/pendencias.py`) e o lugar do gráfico só com o eixo dos meses (macro `lamina_pendente` em
`app/templates/macros.html`). Nenhum dígito de dado dentro da máscara (teste `test_mascara_sem_numeros_e_com_pendencias`).
Quando ganharem conteúdo, cada uma passa a ter ficha própria com a estrutura completa (ver [README](README.md)). Tabela
completa das pendências: [o_que_falta.md](o_que_falta.md).

## Previsão de demanda — `/viu-agenciamento/previsao`

> **Saiu da máscara em 26/10/2026 (D47).** Ficha própria: [previsao.md](previsao.md). A tabela abaixo é histórico.

| Item | Valor |
|---|---|
| Estado | máscara (D30, decisão D5 da síntese); `estado="pendente"` |
| Pergunta (título) | "Quantos pedidos devem chegar até o fim do mês e do ano?" |
| Texto da máscara | "A previsão precisa provar o acerto antes de ir à tela" · "O teste com meses passados acerta o fechamento do mês a partir do 15º dia útil, mas a base reescreve o passado; o erro real precisa ser medido carga a carga." · lugar do gráfico: "Aqui entram os pedidos previstos até o fim do mês e do ano, com a faixa provável." |
| Cálculo existente | `app/apresentacoes/gestao_orcamentos/previsao/calculos.py` (backtest de modelos simples, P1–P6, D20); `?exemplo=1` só com `DEV` e **nunca** no modo apresentação |
| Pendências | **PD09** acerto da previsão medido dia a dia (registro das previsões a cada carga); **PD10** série homogênea para prever o próximo mês e por tipo |
| Fala na reunião | o cenário do ano só oral, se perguntarem, e dito como cenário; outubro não se comenta |

## Resultado: negócios fechados — `/viu-agenciamento/negocios-fechados`

| Item | Valor |
|---|---|
| Estado | máscara (D30); rótulo da aba "Resultado"; `estado="pendente"`; **fora da reunião** desde 26/10/2026 (`na_reuniao=False`, G2-4: a página não vai existir agora; no modo apresentação a Previsão leva à Qualidade). Rodapé datado com as tabelas do Início (D49) |
| Pergunta (título) | "Quanto do que entregamos vira contratação?" |
| Texto da máscara | "A resposta depende da base de contratações" · "O board de orçamentos não registra o fechamento: “Encerrado” junta negócios ganhos e encerramentos automáticos depois de 30 dias." · lugar do gráfico: "Aqui entram as contratações por mês de entrega: quantas, de quais talentos e com que ticket médio." |
| Pedido da diretoria | KPIs de fechamento: talentos contratados, volume, marcas, ticket médio |
| Pendências | **PD05** contratações fechadas (planilha da Mayara, a subir para o BigQuery; `vendido?` do board como conferência); **PD06** destino depois da entrega (gold do SLA); **PD18** prazo de pagamento dos intervenientes (financeiro) |
| Fonte candidata | planilha de contratações da Mayara → gold de contratações (prompt em `docs/prompt_dados_pendentes.md`); silver 2026 tem `vendido`/`data_da_venda` e `valor_da_proposta` só como conferência |

## Qualidade dos dados — `/viu-agenciamento/qualidade`

| Item | Valor |
|---|---|
| Estado | máscara (D30): volta a ser **seção** (decisão D2 da síntese), a última da área; `estado="pendente"`; a ser feita na semana de 26/10 (Caio). Candidato a 1º item: o retrato por mês fechado que avisa quando um mês já fechado muda entre cargas (G2-14, item 3; ex.: SLA jan–set 2.348 → 2.347 de 23 para 26/10) |
| Pergunta (título) | "Dá para confiar nos números desta área?" |
| Texto da máscara | "As verificações estão sendo conferidas" · "Em preparação nesta semana: verificações da base e pendências de preenchimento." (texto para o público desde 26/10/2026, D49; antes, a nota interna "Cada número desta tela precisa bater com uma consulta no BigQuery antes de ir à reunião.") · lugar do gráfico: "Aqui entram as verificações da base e a evolução das pendências de preenchimento." · rodapé datado com as tabelas SLA, entradas e fluxo |
| Cálculo existente | `app/apresentacoes/gestao_orcamentos/qualidade/calculos.py` (Q1–Q6 integridade, A1–A5 atenção, testados; D21) — só vai à tela depois de conferido no BigQuery e registrado em ficha própria |
| Pendências | **PD12** evolução das pendências de preenchimento (silver de qualidade e pendências diárias, desde 21/10, levadas para uma gold); **PD13** foto de fim de mês da base |
| Candidatos a mostrar | entradas com data estimada (445 em 2025, ficha do Início 8.1), cards sem data, "Sem tipo" (Q10), achados F7–F10 com efeito medido, **sem nomes de marca ou card** |

## Histórico

| Data | Mudança |
|---|---|
| 23/10/2026 | Fichas criadas |
| 23/10/2026 | D30: Previsão, Resultado (antes "Negócios fechados", em branco) e Qualidade passam a máscara com pergunta, motivo e pendências (PD05, PD06, PD09, PD10, PD12, PD13, PD18) |
| 26/10/2026 | Batalha 2: Resultado fora do modo apresentação (G2-4); máscara da Qualidade com texto para o público e rodapé datado em toda rota (D49); Qualidade com o retrato por mês fechado como candidato |
| 27/10/2026 | **D57:** o rodapé das máscaras segue lendo `sla_movimentos`, `entrada_diaria` e `fluxo_mensal` da gold; nada mais muda nestas seções |
