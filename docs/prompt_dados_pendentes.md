# Prompt para o projeto da gold — dados das telas pendentes

> **RASCUNHO — não enviar ainda.** O Caio só recebe este prompt depois de finalizar o que quer em cada página
> (23/10/2026). Até lá, ajustar livremente; ao fechar, conferir os códigos contra `pendencias.py` e tirar este aviso.

| | |
|---|---|
| Para colar em | uma sessão aberta em `G:\Meu Drive\Workspace\globo\scripts\PPD-GOLDEN-AGENCIAMENTO-MONDAY` |
| Códigos | os mesmos de `app/apresentacoes/gestao_orcamentos/pendencias.py` (fonte única) e de [paginas/o_que_falta.md](paginas/o_que_falta.md). Mudou lá, atualize aqui |
| Decisões ligadas | PRD D30 (portal, máscaras) e D30-b (exceção da silver em Talentos, termina com a PD01) |
| Versão | 23/10/2026 |

Fora deste prompt (não dependem de dado novo da gold): PD02a (decisão de mostrar nomes), PD02b (cadastro de não
exclusivos, equipe de Talentos), PD10 (datas reais de 2025 para o efeito de fim de ano, depende da PD03/F10), PD15 (não
existe) e PD16 (aguarda Salesforce). A PD09 entra só como apoio: o registro das previsões por carga já é feito pelo job
de previsão (D47, ml/saida/historico_previsoes.jsonl).

---

```text
CONTEXTO
Sou o Caio (caio.barroso@viu.com.br). O site interno PPD-AGENCIAMENTO-SLA (pasta irmã ../PPD-AGENCIAMENTO-SLA, Cloud Run
+ FastAPI, ainda só local) é um portal de dados. A área "Gestão de orçamentos" responde, nesta ordem: Início (pedidos
que chegaram), Talentos, Atendimento, SLA, Previsão, Resultado (negócios fechados) e Qualidade, e fecha na
página "O que falta". Ela lê as golds deste projeto no GCP gglobo-viu-dados-hdg-prd, dataset gold_monday:
  - gld_agenciamento_entrada_diaria  (Início, Atendimento, Talentos: total)  -> TAB_ENTRADA
  - gld_agenciamento_fluxo_mensal    (extrato do mês, Atendimento)          -> TAB_FLUXO
  - gld_agenciamento_2026_sla_movimentos (SLA)                              -> TAB_SLA
As telas sem base aparecem em "máscara" (pergunta + "Aguardando dados" + o que falta). Cada pendência tem um código
PDxx, o mesmo no site e aqui. A diretoria pediu: outliers do SLA e SLA de exclusivos × não exclusivos (já na tela) e
KPIs de fechamento (talentos contratados, volume, marcas, ticket médio), que dependem da planilha de contratações da
Mayara, ainda fora do BigQuery.
Exceção em vigor (D30-b): a tela de Talentos lê a silver 2026 (silver_monday.slv_agenciamento_2026_itens) num agregado
anual, porque a gold de entradas não tem a exclusividade do talento. Hoje: 3.435 exclusivos + 1.955 não exclusivos
(inclui 119 do "Squad de Talentos") + 130 sem talento = 5.520 = total do Início (carga de 23/10/2026 20:23 UTC, dados
até 22/10). O item 1 abaixo existe para acabar com essa exceção.

LEIA PRIMEIRO (e nada além do necessário)
- CLAUDE.md deste projeto.
- docs/tabelas/gld_agenciamento_entrada_diaria.md (regras R1–R21; sobretudo R2, R4, R5, R6, R8, R21) e
  sql/gld_agenciamento_entrada_diaria.sql; docs/tabelas/gld_agenciamento_fluxo_mensal.md; docs/tabelas/_modelo.md.
- Deste projeto: sql/gld_agenciamento_2026_talentos_ano.sql (divisão de talentos, com as mesmas regras de data; desde
  27/10/2026 o site lê esta gold, D57). Do site:
  ../PPD-AGENCIAMENTO-SLA/docs/lembretes_gold.md (itens 4, 5, 9, 11, 12, 14, 15) e
  ../PPD-AGENCIAMENTO-SLA/app/apresentacoes/gestao_orcamentos/pendencias.py.

RESTRIÇÕES
- Claude só faz SELECT no GCP corporativo. Confirme identidade (SESSION_USER()) e projeto antes de consultar. Consultas
  enxutas, com estimativa de bytes antes das grandes.
- Criar ou alterar tabela, view, job, agendamento, carga ou permissão: escreva o comando pronto, explique o efeito e eu
  rodo. Um bloco por vez; aguarde a minha saída.
- Sem LLM por API, sem BigQuery ML, sem ai.* / ML.FORECAST, sem Vertex. Nunca imprima segredos.
- Não altere as golds existentes sem eu aprovar; coluna nova em gold existente só como proposta, com o impacto no site
  (somas por grão) descrito.
- Nomes de talentos podem ficar nas tabelas (para uso futuro), mas NÃO vão para relatório, resumo, exemplo ou tela sem
  decisão minha: nas validações, mostre contagens, não nomes. Nada de nome de pessoa da equipe. Marca e cliente: fora
  das tabelas novas, salvo a gold de contratações (item 2), onde a marca é um KPI pedido; ainda assim, sem nomes no
  resumo.
- Cada tabela nova ganha ficha em docs/tabelas/ no padrão _modelo.md (regras numeradas, SQL de validação, carga datada)
  e validações em sql/validacoes/.

OBJETIVO
Construir, em ordem de prioridade, os dados que tiram as máscaras do site, com contrato de colunas estável para o site
ler. Para cada item: fonte, regra, validações, contrato da tabela de saída e comandos para eu rodar.

ITEM 1 — PD01: exclusividade na base de entradas  (PRIORIDADE 1; encerra a exceção D30-b)
Pergunta: como a demanda se divide entre exclusivos, não exclusivos e sem talento, mês a mês, na MESMA base do Início?
Fonte: silver_monday.slv_agenciamento_2026_itens (projeto_id, talento, exclusivo = exclusividade na data do projeto,
regras 53/56/60 da silver; talentos_exclusivos; state). Reaproveite as CTEs de sql/gld_agenciamento_entrada_diaria.sql
(data R1/R2/R21, exclusões R5, situação) e acrescente talento e exclusivo ANTES da agregação. Sem criado_em a silver deixa
exclusivo NULL (regra 63b): como em talentos_ano.sql, considerar exclusivo quando o talento está em talentos_exclusivos
(5 cards hoje). A R8 tira o talento da entrada_diaria de propósito: leia o motivo e diga se afeta esta tabela.
Recomendação: tabela irmã gld_agenciamento_entrada_talento, sem mexer no grão da entrada_diaria (validada em três
camadas em 23/10). Se preferir uma coluna grupo_exclusividade na própria entrada_diaria, descreva o impacto antes.
Escopo: só 2026 (2025 não tem exclusividade na data; ver item 7a).
Contrato (grão: data × grupo_input × tipo_de_input × familia × grupo_exclusividade × talento):
  data DATE                    -- data de entrada, mesma regra da entrada_diaria
  mes DATE                     -- 1º dia do mês de data
  grupo_input STRING, tipo_de_input STRING, familia STRING   -- iguais à entrada_diaria
  grupo_exclusividade STRING   -- 'Exclusivo' | 'Não exclusivo' | 'Sem talento'
  exclusivo BOOL               -- NULL quando sem talento
  talento STRING               -- como na silver; NULL se vazio (não vai à tela sem decisão)
  talento_eh_grupo BOOL        -- TRUE para 'Squad de Talentos' (grupo, não pessoa; fora de rankings)
  quantidade INT64, quantidade_estimada INT64
  entregue_no_mes INT64, entregue_depois INT64, nao_seguiu INT64, em_andamento INT64  -- mesma regra da entrada_diaria
  _processado_em TIMESTAMP
Validações (SELECT, resultado na ficha):
  V1 por mês × grupo_input: SUM(quantidade + quantidade_estimada) = entrada_diaria. Esperado 0 diferenças.
  V2 por mês: situações somam as colunas da entrada_diaria. Esperado 0 diferenças.
  V3 2026 até 22/10 por grupo_exclusividade = 3.435 / 1.955 / 130 (referência da exceção); diferença explicada por motivo.
  V4 Squad de Talentos: 119 pedidos em não exclusivos; talento_eh_grupo marcado.
  V5 talentos que mudaram de exclusividade no ano (eram 7): contagem dos que aparecem nos dois grupos, sem nomes.
  V6 unicidade do grão; nenhuma quantidade negativa; nenhuma célula de talento com vários nomes.

ITEM 2 — PD05: contratações fechadas (planilha da Mayara)  (PRIORIDADE 2; abre a tela Resultado)
Pergunta da diretoria: talentos contratados, volume, marcas e ticket médio, por mês; conversão sobre os entregues.
Fonte: planilha de contratações da Mayara (Excel/Google Sheets; peça-me o arquivo ou o link, não presuma o formato).
Passo a: diagnóstico do arquivo que eu passar (colunas, tipos, vazios, duplicados, período, chaves possíveis para
  ligar ao board: projeto_id/item_id, nome do card, talento + marca + data). Só leitura local.
Passo b: subir para o BigQuery como bronze/silver (proposta: bronze_* tabela crua + silver_monday.slv_contratacoes com
  tipos e nomes padronizados). Comando para eu rodar (bq load ou tabela externa do Sheets), com o esquema explícito.
Passo c: gold de contratações. Nome sugerido: gold_monday.gld_agenciamento_contratacoes. Colunas sugeridas:
  contrato_id STRING            -- chave da planilha (ou hash estável das colunas que identificam o contrato)
  data_fechamento DATE, mes_fechamento DATE
  projeto_id STRING             -- card do board, quando ligar; NULL se não ligar (medir a cobertura)
  mes_entrega DATE              -- 1ª entrega do card (gold do SLA/entradas), para a conversão
  talento STRING, exclusivo BOOL, grupo_exclusividade STRING  -- exclusividade na data do fechamento
  marca STRING, tipo_de_input STRING, grupo_input STRING
  valor_contrato NUMERIC        -- bruto, na moeda da planilha; dizer se inclui impostos/comissão
  quantidade_contratos INT64    -- 1 por linha, para somar
  origem STRING                 -- 'planilha' | 'board' (conferência)
  _carregado_em TIMESTAMP, _processado_em TIMESTAMP
Regras a propor (e decisões que dependem de mim ou da Mayara): o que é "fechado" (assinatura? pagamento?), data de
referência, contrato com vários talentos (uma linha por talento? rateio do valor?), cancelados, moeda.
Indicadores que o site vai calcular: contratos por mês; talentos distintos; marcas distintas; volume (R$); ticket médio =
valor ÷ contratos; conversão = contratos ligados ÷ entregues do mesmo mês de entrega (coorte madura, ≥ 60 dias).
Validações: total de linhas e valor = planilha; % ligado ao board; vendido?/data_da_venda da silver 2026 como conferência
(quantos batem, quantos só num lado); nenhum valor negativo; duplicados.

ITEM 3 — PD06: destino depois da entrega  (Resultado v0, sem a planilha)
Fonte: gld_agenciamento_2026_sla_movimentos (status_atual, alerta, em_aberto, encerrado sem entrega).
Regra: entregues (1ª chegada em Aguardando Feedback) por destino: aguardando, em alerta (> 10 dias úteis), encerrado
sem retorno (automação de 30 dias), declinado. Entregue só a proposta (view ou tabela) e a validação: soma dos destinos
= entregues por mês de entrega. Atenção ao lembrete 4: a R1 tira da tabela projetos que voltaram para a equipe; proponha
manter os já entregues ao menos uma vez (ou uma tabela de entregas), com o impacto no SLA (base jan–set 2.425).

ITEM 4 — PD07: motivo de quem saiu sem entrega  (Atendimento; lembrete 5)
Em gld_agenciamento_fluxo_mensal, separar 'nao_seguiu' em Declinado, Standby e Encerrado. Proposta: coluna motivo
(STRING) ou evento mais fino; aplicar o corte de data do lembrete 12 (status_desde <= fim). Validação: soma dos motivos =
nao_seguiu atual em cada mês. Não altere a tabela: proposta + SQL + impacto no site (o extrato soma por evento).

ITEM 5 — PD08: entregas sem histórico de status  (Atendimento; F9, lembrete 9)
185 entregas de 2026 vêm só da data_de_saida (R13), sem Aguardando Feedback no log (133 Encerrado, 39 Declinado/Standby).
Entregue: a lista por status e mês (contagens), uma coluna/flag proposta (ex.: entrega_sem_log BOOL) na entrada_diaria
ou na fluxo_mensal para o site poder separar ou excluir, e o efeito em cada mês das duas opções. A regra é decisão da
equipe; não aplique.

ITEM 6 — PD12 e PD13: qualidade  (tela Qualidade)
6a PD12 gld_agenciamento_qualidade_diaria. Fonte: slv_agenciamento_2026_pendencias_diaria (data_referencia, categoria,
   situacao, entra_no_relatorio, corrigido_em; existe desde 21/10) e slv_agenciamento_2026_qualidade (coluna, tipo_erro).
   Colunas: data_referencia DATE, categoria STRING, tipo_erro STRING, situacao STRING ('Aberta'|'Corrigida'),
   entra_no_relatorio BOOL, quantidade INT64, corrigidas_no_dia INT64, mediana_dias_ate_correcao FLOAT64, _processado_em.
   Sem nomes de marca, card ou pessoa. Validação: abertas no último dia = silver. Avise que o histórico começa em 21/10.
6b PD13 foto de fim de mês (lembrete 15): proposta de gld_agenciamento_fila_fechamento (mes_ref DATE + as colunas da
   entrada_diaria/fluxo_mensal congeladas no último dia útil do mês) e a forma de gravar sem reescrever (append por mês).
   Validação: diferença entre a foto e a leitura de hoje por mês.

ITEM 7 — diagnósticos rápidos (só SELECT e texto)
7a PD03: dá para classificar a exclusividade de 2025 na data do pedido (slv_agenciamento_2025_itens: talentos_exclusivos,
   interveniencia + quadro de talentos exclusivos com início e fim)? Cobertura esperada? O que falta da equipe?
7b PD09 (apoio): a entrada_diaria permite reconstruir, por dia útil, o acumulado do mês como estava em cada carga? Se não
   (a gold reescreve o passado), confirme que o registro das previsões tem de ser feito pelo site a cada carga.
7c Estado dos lembretes F7, F8/11, 12 e 14: o que ainda muda número, com a contagem de hoje.

ITEM 9 — PD24: Inbound marcado como talento não exclusivo  (Qualidade; D55)
Regra do Caio: todo Inbound é de talento exclusivo. Na silver 2026 há 78 pedidos de Inbound de jan–set com exclusivo =
FALSE (6,5%). Entregue: a lista por talento e mês (só SELECT, sem nomes no resumo), se o erro está no talento ou no tipo
de input, e um alarme na gold (contagem diária de Inbound não exclusivo). Validação: contagem igual à de
ml/dados/exclusividade.csv do site.

ITEM 8 — PD18: prazo de pagamento dos intervenientes  (Resultado; depois do item 2)
Fonte: contratos e pagamentos do sistema financeiro (fora do monday; pergunte-me qual sistema e se há extração). Regra:
dias do contrato assinado até o pagamento ao interveniente (talento não exclusivo/agência), por mês de assinatura;
mediana e % pagos em até N dias (N a definir com o Financeiro). Entregue: o que existe, como ligar à gold de contratações
(contrato_id) e o contrato sugerido (contrato_id, data_assinatura, data_pagamento, dias_ate_pagamento INT64,
grupo_exclusividade, _processado_em). Sem nomes no resumo. Nada criado sem a fonte confirmada.

COMO O SITE VAI LER (não altere o site; só me devolva o contrato)
- Cada tabela nova vira uma variável TAB_* em ../PPD-AGENCIAMENTO-SLA/app/config.py (ex.: TAB_ENTRADA_TALENTO,
  TAB_CONTRATACOES, TAB_QUALIDADE) e uma Tabela em app/dados.py com a lista de colunas (o contrato mínimo da carga) e a
  chave única; o site lê a tabela inteira em memória e recarrega pelo metadado `modified`.
- A exceção D30-b já saiu (27/10/2026, D57): o site lê gld_agenciamento_2026_talentos_ano e ..._talentos_ranking.
  Quando a gld_agenciamento_entrada_talento passar em V1–V6, o site confere que a divisão anual não muda e abre a
  divisão por mês sobre ela.
- Toda tabela precisa de _processado_em (o site mostra "Dados até … · atualizados em …") e da mesma cobertura até a
  véspera da carga que a entrada_diaria.

CRITÉRIOS DE ACEITE
- Item 1: tabela criada (por mim, com o seu comando), V1 e V2 com 0 diferenças, V3 batendo com 5.520 e diferenças
  explicadas, ficha em docs/tabelas/, inclusão no job diário proposta.
- Item 2: planilha diagnosticada, carga no BigQuery proposta com esquema, gold de contratações com as regras em aberto
  listadas para decisão; total de linhas e valor batendo com a planilha.
- Itens 3–6 e 8: proposta com SQL de validação e impacto no site; nada alterado sem meu ok.
- Nenhum nome de talento, marca ou pessoa em resumo ou exemplo; só contagens.
- Resumo final: tabelas criadas (nome completo), contratos de colunas, resultados das validações, comandos que eu
  ainda preciso rodar, o que ficou pendente e de quem depende, e a variável TAB_* sugerida para cada tabela.
```

## Complemento da revisão de 24/10/2026

- **PD19 — Data das saídas e identificação da carga:** obter eventos da Silver para Golden de entrada/fluxo; publicar `load_id` e `data_referencia` comuns, mês efetivo, status/motivo e sinalizador de data ausente/atribuída. Há dez saídas sem data em 2026, atribuídas ao mês de entrada no relatório. Reconciliar por mês e tipo as quatro situações, além do total; não substituir ausência por uma data observada fictícia.
- **PD20 — Continuidade multianual de Talentos:** Golden com identidade estável do pedido, board de origem, transferências e exclusividade na data do pedido. Mesma população e corte de entradas; dispensar troca manual de tabela em janeiro. Fonte atual continua configurada no board 2026.
- **PD21 — Tempo da equipe pronto na gold (SLA, D-SLA-5, 25/10/2026):** (1) fase própria para "Em elaboração - Retorno Marca/Executivo" (hoje o site tira pelo nome do status; é espera da marca, não trabalho da equipe); (2) manter na tabela de movimentos quem já teve a 1ª entrega e voltou à equipe (R1: hoje o projeto some do mês fechado até voltar ao cliente); (3) coluna de pacote/lote (hoje só o prefixo "[Pacote" no nome; 27 dos 28 "fora da curva" de jan–set são pacotes); (4) relógio para cards criados direto em Em Elaboração/Em revisão (sem Entrada, R11/R12); (5) tabela de pedidos em andamento, sem 1ª entrega, com as horas até a carga (para Kaplan-Meier: o mês parcial só fecha quando todos são entregues); (6) conferir 28 `encerrado_sem_entrega` e 19 `entrega_sem_aguardando` da validação de 25/10; (7) v2 sem almoço (10h–13h + 14h–19h) em `sla_util_horas`, para o site deixar de recalcular (C2).
- **PD13 permanece:** a curva atual é reconstruída, não fotografia fechada. Manter snapshots de referência sem reescrever o passado silenciosamente.

São requisitos locais preparados para análise no projeto da Golden; nenhuma alteração de BigQuery foi executada. Ver `docs/historico/REVISAO_2026-10-24.md` para evidências e critérios de aceite. No Atendimento, 170 × 160 foi resolvido por convenção explícita de mês atribuído; a ausência das datas na fonte continua pendente.
