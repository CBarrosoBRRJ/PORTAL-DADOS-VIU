# Fichas das páginas — padrão de rastreabilidade

## Continuidade atual

**Comece pelo topo de cada ficha** (26/10/2026): "Retrato da carga da reunião" (Início, Talentos, Atendimento, Previsão) ou "Estado vigente" (SLA) traz o estado, as regras que valem e os números da carga de 26/10/2026 09:01 (dados até 25/10). O resto da ficha é a memória datada (cargas de 23 e 24/10) e o histórico. Linha do tempo da etapa: [HISTORICO_2026-10.md](../HISTORICO_2026-10.md). A revisão de 24/10/2026 ([REVISAO_2026-10-24.md](../historico/REVISAO_2026-10-24.md)) é histórico.

Uma ficha por página do site. Serve para conferir, validar e auditar (Caio, equipe, Codex) **cada número e cada texto**
que vai para a diretoria, sem precisar ler o código.

## Glossário das telas (batalha 2, 26/10/2026)

Um termo por ideia, em todas as páginas. Termo técnico só no leitor de tela e nas fichas.

| Termo na tela | Quer dizer | Não usar na tela |
|---|---|---|
| pedido | o que **entra** (pedido de orçamento) | — |
| orçamento | o que a equipe **entrega** ao cliente; no estudo do SLA, "orçamentos medidos" | "pedidos entregues" no recorte do estudo |
| típico | o valor do meio (mediana): metade leva até ele | mediana |
| dias de trabalho | horas da equipe em dias de 8 h (meta: metade em até 2 dias de trabalho, 16 h) | "dias úteis" para a meta |
| dias úteis no calendário | prazo que o cliente espera, seg–sex sem feriado (C3b) | "dias corridos" na tela |
| saíram sem entrega | declinados, standby ou encerrados antes da entrega; no Início pelo mês em que o pedido **entrou** (dica), no Atendimento pelo mês em que **saiu** ("… no mês") | "encerrados sem entrega" |
| veio do mês anterior | a fila que passa de um mês para o outro (Atendimento); o Início ainda usa "represados" (pendente de decisão do Caio) | — |
| fora da curva | acima do limite do padrão do processo (Q3 + 1,5 × IQR, ficha sla.md 8.1) | outlier, limite estatístico |
| alerta abaixo de 90% | linha de referência do Atendimento (A25) | corte |
| sino | a curva normal (Q-Q) | teste de normalidade, Q-Q |

## Regra de manutenção

- Mudou um texto, uma regra, um cálculo ou o layout de uma página? **Atualize a ficha no mesmo trabalho** (seção
  "Histórico da página"), além do PRD. Página nova = ficha nova, copiando a estrutura abaixo.
- Os números de exemplo são de uma **carga datada**. Ao reconferir, anote a nova data e os novos valores; não apague
  os antigos do histórico.
- O código é a fonte da verdade das regras; a ficha aponta o arquivo e a função. Se divergirem, a ficha está
  desatualizada ou o código tem erro: registre e corrija.

## Estrutura obrigatória de cada ficha

1. **Identificação** — rota, arquivos (cálculo, template, testes), tabela de origem, carga de referência; **1.1 Tabelas
   e colunas consumidas** (nome completo da tabela ou view gold e cada coluna usada, conferidas com `app/dados.py`; desde
   a D57 o site só lê a gold, então página nova = tabela ou view gold nova, não SQL no site).
2. **Pergunta e resposta esperada** — o que a página responde e o que o leitor precisa sair sabendo.
3. **O que aparece na tela** — cada elemento, o texto exato e a regra que o gera.
4. **Regras** — com ID (E*, A*, C*), fórmula e quem decidiu.
5. **Memória de cálculo** — conta passo a passo com os números da carga de referência.
6. **Como reproduzir** — consultas SQL somente leitura que refazem **cada número da tela direto no banco** (não pelo
   código Python), com o resultado esperado e a data da carga. Índice de todas as páginas: PRD, "Módulos do portal" (M1–M7).
7. **Validações feitas** — data, o que foi conferido e o resultado.
8. **Limites e pontos de atenção** — o que o número **não** diz e riscos de leitura.
9. **Decisões** — referência às decisões do PRD (D*, Q*).
10. **Histórico da página**.

## Fichas

| Página | Rota | Ficha | Situação |
|---|---|---|---|
| Início (entrada de pedidos) | `/viu-agenciamento` | [inicio.md](inicio.md) | **entregue em 23/10/2026 (D28)**; validação em três camadas, 0 divergências; checagem diária na seção 6.4 |
| Talentos | `/viu-agenciamento/talentos` | [talentos.md](talentos.md) | **entregue em 24/10/2026 (D31)**; divisão anual de 2026 (5.556 = Início na carga de 26/10) e top 10 por grupo; lê a silver por exceção (D30-b) até a PD01 |
| Atendimento | `/viu-agenciamento/atendimento` | [atendimento.md](atendimento.md) | **entregue em 24/10/2026 (D33)**; faixa dos números do ano, quadro do extrato em 7 linhas (A24) e dispersão sobre a demanda total com objetivo 100%/90% (A16, A25), conferidos no BigQuery (carga de 26/10: 5.556 = 4.415 + 974 + 167) |
| SLA de entrega (aba "SLA", antes "Prazo") | `/viu-agenciamento/sla` | [sla.md](sla.md) | **pronta, meta a oficializar** (D34–D49): página única (resposta tipográfica, seletor de talentos, trilhos por mês com meta sugerida de metade em até 2 dias de trabalho, 16 h — D38) e estudo "Como medimos" em 8 slides (`/sla/como-medimos`); conferida no BigQuery na carga de 26/10 (`tools/conferir_estudo.py`, C3b) |
| Previsão de demanda | `/viu-agenciamento/previsao` | [previsao.md](previsao.md) | pronta, 2 decisões abertas (D48: retrato mensal; D49: textos do erro) |
| Resultado: negócios fechados | `/viu-agenciamento/negocios-fechados` | [demais.md](demais.md) | máscara (D30); fora do modo apresentação desde 26/10 |
| Qualidade dos dados | `/viu-agenciamento/qualidade` | [demais.md](demais.md) | máscara (D30); a ser feita na semana de 26/10 |
| O que falta | `/viu-agenciamento/o-que-falta` | [o_que_falta.md](o_que_falta.md) | pronta (D30), gerada de `pendencias.py` |

A ordem da tabela é a ordem da reunião (D30). Seção em máscara não mostra número; a ficha registra a pergunta, o motivo
e as pendências (PDxx de `pendencias.py`).

## Como auditar

1. Abrir a página no site e a ficha lado a lado.
2. Para cada número da tela, achar a linha na seção 5 (memória de cálculo) e rodar a consulta da seção 6 no BigQuery
   (projeto `gglobo-viu-dados-hdg-prd`, só leitura). Ajustar as datas para a carga do dia.
3. Conferir as regras da seção 4 contra o código apontado e os testes (`python -m pytest tests -q`).
4. Registrar divergências no PRD (seção 10, achados) e na ficha.

Auditoria automatizada: `tools/checar_reuniao.py` (passo único antes de apresentar: identidade, cargas, site, Início Q1/Q2, estudo nos 3 grupos, previsão; grava `docs/validacao/reuniao_AAAA-MM-DD.json`), `tools/conferir_estudo.py` (estudo do SLA), `tools/auditar_relatorio.py` (gold × silver e SLA por calendário independente) e `tools/conferir_expediente.py` (expediente contra a gold). A ficha `o_que_falta.md` é conferida contra `pendencias.py` por `tests/test_documentacao.py`.
