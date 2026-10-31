# Plano de contratos Gold para o relatório

Data: 26/10/2026. Preparado para Caio executar com Claude. **Nenhuma tabela foi criada ou alterada nesta auditoria.** Layout, textos de página e fontes atuais permanecem como estavam.

## 1. Decisão de arquitetura

Consultar uma Gold com SELECT não é um erro. A pendência é o aplicativo precisar reconstruir regras na Silver e recalcular expediente que ainda não existe na Gold. Recomendo contratos de consumo por assunto/visual, compartilhando a mesma definição de pedido, corte e carga. Uma tabela para cada gráfico decorativo repetiria dados e regras sem aumentar a confiabilidade.

Para atender à separação por tela, o pacote fornece nove tabelas de consumo. As duas primeiras são espelhos contratuais opcionais das Gold existentes: podem ser dispensadas se a equipe preferir manter os nomes atuais. As demais removem dependências de Silver do caminho de leitura do site. Todos os nomes começam por `gld_relatorio_`, no dataset `gglobo-viu-dados-hdg-prd.gold_monday`.

| Tabela | Tela/visual | Grão e chave lógica | Fonte/regras |
|---|---|---|---|
| inicio_diario | Início, barras e situações | data × grupo_input × tipo_de_input × familia | Gold de entradas; contagem real + estimada |
| atendimento_fluxo | Extrato do Início e Atendimento | mes_entrada × evento × mes_evento × grupo_input × tipo_de_input × familia | Gold de fluxo; saída no mês do evento, safra preservada |
| talentos_ano | Divisão anual e denominadores | ano × categoria | Silver itens; SQL atual de talentos |
| talentos_ranking | Top 10, mapa mensal e corrida | grupo × talento × mes | SQL atual; inclui quem passou pelo top 10 acumulado, mesmo fora do top final |
| atendimento_status | Composição das saídas e exclusões A27 | mes × status | Silver itens + log; soma deve conciliar com fluxo |
| sla_movimentos_v2 | SLA e estudo Como medimos | projeto_id × passo | Gold de movimentos + microssegundos úteis sem almoço |
| previsao_mensal | Séries Inbound/Mercado | mes × tipo | Gold de entradas; meses completos separados do parcial |
| previsao_exclusividade | Séries exclusivas/não exclusivas | mes × tipo | Silver itens; mantém sem talento separado |
| previsao_lotes | Diagnóstico do mês corrente | grão do SELECT 09, por recorte/período | Silver itens; mesma regra de lote do aplicativo |

Cada tabela recebe `_dados_ate`, `_publicado_em` e `_lote_id`. O último é comum às nove tabelas em uma publicação. Não confundir `_publicado_em` com `_processado_em` da origem. A data de corte continua sendo a véspera da carga de entradas, em São Paulo.

## 2. Pré-requisitos e limites

1. Usar a conta corporativa `caio.barroso@viu.com.br` e confirmar o projeto no console. Não mudar permissões para testar.
2. Conferir que a carga de Gold terminou e que Silver itens/log correspondem ao mesmo ciclo de ingestão. A origem ainda não fornece um `load_id` comum: igualdade do dia e conciliação de totais ajudam, mas não provam identidade completa das versões. Executar após o pipeline, sem outra carga concorrente.
3. Trabalhar primeiro em homologação: adaptar os **destinos**, mantendo as fontes em leitura. Não apontar a aplicação antes da comparação completa.
4. O pacote de compatibilidade usa Silver anual de 2026. Há uma trava explícita para não publicar números errados em 2027. Para continuidade, construir fato histórico unificado entre anos e substituir a dependência anual; não basta retirar a trava.
5. O calendário sem almoço reproduz `app/expediente.py`, incluindo feriados fixos e móveis de 2024–2035. É um calendário operacional, que precisa ser homologado pelo negócio. Intervalos fora dessa cobertura interrompem a publicação.
6. Os nove SELECTs foram aceitos pelo BigQuery em **dry run**, com corte 25/10/2026. DDL, INSERT, transação, permissões de escrita e agenda **não foram executados nem homologados**. Evidência: [gold_selects](../validacao/gold_selects_2026-10-26.json).

## 3. Passo a passo no BigQuery

### Passo 1 — Revisar as consultas de cada tabela

Abra [a pasta SQL](../../_descartados/2026-10-27/docs/sql/gold_relatorio). Os arquivos `01_*.select.sql` a `09_*.select.sql` contêm somente a consulta de cada contrato, com as regras atuais do projeto. Para execução avulsa, informe `fim` como DATE, `inicio` como DATE e `tipos` como ARRAY<STRING> quando usados. Não troque o corte por CURRENT_DATE: a carga pode estar atrasada.

### Passo 2 — Criar apenas as estruturas novas

No editor SQL, execute [00_criar_estruturas.sql](../../_descartados/2026-10-27/docs/sql/gold_relatorio/00_criar_estruturas.sql). O script usa `CREATE TABLE IF NOT EXISTS` e não insere linhas. Ele não substitui nenhuma tabela existente. Se um destino já existir com outro schema, compare e migre conscientemente; `IF NOT EXISTS` não atualiza schema.

### Passo 3 — Carregar e publicar o conjunto

Execute [10_atualizar_atomicamente.sql](../../_descartados/2026-10-27/docs/sql/gold_relatorio/10_atualizar_atomicamente.sql). O script:

1. Calcula o corte da Gold e um identificador de publicação.
2. Constrói tabelas temporárias com os nove SELECTs.
3. Recusa fontes vazias, população anual divergente, situações que não fecham e movimentos duplicados.
4. Substitui o conteúdo dos nove destinos dentro de uma transação. Em falha, o conjunto anterior permanece; não executar pedaços isolados do bloco de publicação.

É uma reconstrução completa, proporcional ao volume atual (dezenas de milhares de movimentos). Ela captura correções retroativas. Antes de crescer para milhões de registros, medir custo e adotar atualização por partições afetadas com captura de alterações retroativas; atualizar apenas o dia corrente perderia correções.

### Passo 4 — Conferir antes de trocar o aplicativo

Compare cada SELECT com o destino, **sem** as três colunas técnicas, usando `EXCEPT DISTINCT` nos dois sentidos. Confira também `COUNT(*)` e chaves duplicadas: `EXCEPT DISTINCT` sozinho esconde duplicatas. Todas as nove tabelas devem ter exatamente o mesmo `_lote_id` e `_dados_ate`.

Conferências obrigatórias:

- Início: quantidade + estimada = entregue_no_mes + entregue_depois + nao_seguiu + em_andamento, por linha e por mês.
- Entrada × fluxo: totais por safra, grupo, tipo e família iguais; nenhum evento anterior à safra.
- Atendimento: fila anterior + entradas = entregues + saídas sem entrega + fila final; status por mês conciliado. Saída sem data continua sendo uma convenção, não observação histórica.
- Talentos: soma das categorias = total anual de entradas; soma mensal por talento = seu total; concentração nunca superior a 100%.
- SLA: `sla_sem_almoco_us / 3600000000` = função Python para cada intervalo fechado; NÃO substituir `sla_util_horas` antigo, que inclui almoço. Intervalo aberto mantém NULL no novo campo, não zero fictício. A agregação por primeira entrega continua necessária.
- Previsão: meses completos contínuos, nenhuma contagem negativa, exclusivos + não exclusivos + sem talento = população Silver. Conciliar Gold/Silver por mês. Ausência de linha não pode virar zero automaticamente sem prova de cobertura.

Referência desta auditoria, válida apenas para a carga de 26/10: 5.556 entradas em 2026; 5.389 saídas do fluxo da safra; 167 ainda em andamento. Talentos: 3.451 exclusivos, 1.980 não exclusivos e 125 sem classificação. Conferir o corte antes de comparar com uma carga posterior.

### Passo 5 — Adaptar o leitor, sem mudar telas

Em uma alteração posterior, substituir as três `Consulta` de `app/dados.py` por `Tabela` apontando aos contratos materializados. Manter colunas/chaves e remover as regras Silver do caminho de atendimento HTTP. Adaptar o extrator `ml/dados.py` para consumir as três tabelas de previsão. Para SLA, implementar leitura do novo campo com comparação paralela antes de desativar o cálculo Python.

Não basta mudar `TAB_TALENTO_ORIGEM`: essa variável hoje identifica **itens Silver**, e as consultas esperam seu schema. A migração precisa trocar o adaptador. Não ligar a nova fonte antes de existir. A aplicação continua usando as fontes atuais até essa etapa.

Validar os testes, `/saude`, páginas/filtros e reconciliar nova versus antiga fonte na mesma carga. Consumidores devem rejeitar ou repetir leitura se `_lote_id` mudar entre duas tabelas: a transação publica atomicamente, mas duas consultas separadas podem atravessar o instante da publicação.

### Passo 6 — Agendar e operar

Agendar o script 10 depois da conclusão confirmada do pipeline Gold, em sua região atual; não presumir que um horário fixo garante dependências concluídas. Uma execução por vez. Monitorar última carga, duração, bytes, falhas de ASSERT e disponibilidade dos nove destinos. Usar a identidade de serviço corporativa já aprovada pela equipe; este documento não cria IAM.

No modo apresentação, `CONGELAR=true` é intencional: preserva a reunião. Para operação diária, configurar `CONGELAR=false`, conferir `RECARGA_MIN` e o job separado de ML. Não aplicar isso silenciosamente ao ambiente de reunião.

Rollback: restaurar os adaptadores/configuração anteriores do site; as Gold originais não foram alteradas. Guardar a última publicação e resultados de comparação antes da troca. Não excluir origens nem evidências.

## 4. Resultados dos modelos também na Gold

O arquivo [20_estruturas_ml.sql](../../_descartados/2026-10-27/docs/sql/gold_relatorio/20_estruturas_ml.sql) define `gld_relatorio_previsoes` e `gld_relatorio_modelos_avaliacao`. A primeira guarda previsões congeladas por origem/alvo; a segunda preserva cada observação de backtest, permitindo recalcular métricas sem médias de percentuais.

SQL não executa automaticamente os modelos Python existentes. Depois de aprovar o novo protocolo, o job local deve exportar JSONL com os campos desse schema, publicar em staging e validar unicidade, finitude, horizontes, corte e hash dos dados antes de inserir. O carregamento deverá ser implementado/homologado pela equipe; **não há escritor GCP habilitado neste projeto pela auditoria**. Preservar cada retrato mensal, sem reescrever previsões antigas após conhecer o realizado.

## 5. Dados que ainda faltam

- Fato de pedidos histórico com ID estável, data de entrada real/estimada, data da primeira entrega, status e validade temporal da exclusividade, abrangendo 2027 em diante.
- Calendário operacional versionado e duração útil sem almoço na Gold.
- Identificador único de carga propagado Bronze → Silver → Gold; horário de conclusão e cobertura declarada.
- Histórico de status/snapshots para reconstruir a fila **como era conhecida** em cada fechamento. Estado atual reconstruído não é snapshot histórico.
- Capacidade disponível, pessoas/horas e complexidade dos pedidos para medir produtividade; quantidade resolvida isolada não mede esforço.
- Valores financeiros, orçamento aprovado, realizado, cancelamentos e datas de competência para a futura página Resultado. Não inventar tabela financeira a partir de contagens.
- Série diária/semanal por recorte, dias úteis, atraso de ingestão e campanhas conhecidas antecipadamente para melhorar previsão. Informações conhecidas só depois do mês não entram como variáveis preditoras.

Qualidade pode reutilizar os movimentos e os resultados das regras de validação; recomenda-se uma tabela futura de ocorrências por `regra_id × entidade × lote`, depois de acordar a taxonomia. A tela Resultado não possui implementação habilitada no modo de reunião atual. Não criar uma tabela vazia como se esses indicadores já estivessem disponíveis.

## 6. Qual é o ganho de cada tabela?

O ganho imediato é governança: uma regra calculada no pipeline, conferida e reaproveitada por todos os consumidores. Materializar não acrescenta informação à origem. Há custo de armazenamento, processamento agendado e manutenção; por isso não recomendo criar as nove tabelas apenas para separar nomes de páginas.

| Contrato | Ganho concreto depois da migração do leitor | Prioridade |
|---|---|---|
| inicio_diario | Padroniza o contrato e os metadados; a Gold atual já entrega o grão necessário | Opcional; reaproveitar a atual evita cópia |
| atendimento_fluxo | Padroniza o contrato; a Gold atual já distingue safra de entrada e mês de saída | Opcional; reaproveitar a atual |
| talentos_ano | Retira a regra de exclusividade/entrada da consulta da aplicação; denominadores publicados e conciliados | Alta |
| talentos_ranking | Publica ranking, meses e participantes da corrida com a mesma regra anual | Alta, junto da anterior |
| atendimento_status | Retira a reconstrução por itens/log do site; permite conciliar motivos das saídas antes da publicação | Alta |
| sla_movimentos_v2 | Centraliza o expediente sem almoço e evita recalcular durações em cada processo do servidor | Alta; comparar intervalo a intervalo |
| previsao_mensal | Oferece série mensal e corte comuns para outros consumidores; o volume atual já é pequeno | Condicionada ao uso compartilhado; agregação atual pode bastar |
| previsao_exclusividade | Dá ao ML recortes oficiais, conciliados, sem refazer a regra Silver em outro lugar | Alta na etapa de previsão |
| previsao_lotes | Publica diagnóstico de concentração de pedidos por marca/dia | Média; contextualiza desvios, não melhora o modelo automaticamente |
| previsoes e modelos_avaliacao | Preserva o que foi previsto antes do realizado e permite avaliar cada horizonte | Alta para governança de ML; exige escritor e rotina próprios |

**Não há ganho percentual de velocidade ou economia medido.** O site já usa cache; uma navegação não representa necessariamente nova consulta ao banco. Para medir, comparar a mesma carga e os mesmos cenários antes/depois: inicialização e recarga do servidor, latência mediana/P95, CPU/memória, bytes processados/faturáveis e custo total incluindo o job de materialização. Dry run estima leitura, não comprova economia nem tempo de execução.

Sequência recomendada: (1) centralizar Talentos, status e duração SLA; (2) migrar leitores e comparar resultados; (3) oficializar séries e histórico de previsões; (4) criar espelhos adicionais somente se houver necessidade de contrato/consumidor. Os scripts 00/10 atuais publicam o **pacote completo de nove tabelas**; a sequência enxuta exige preparar uma variante antes de executá-los, não apenas pular instruções dentro da transação.

## 7. Quais informações melhoram de fato o dashboard?

Aqui, “falta” pode significar dado existente que ainda não chega à Gold, histórico que precisa começar a ser preservado ou informação de negócio ainda não integrada. A ausência abaixo é do contrato atual do relatório; não é prova de inexistência em todos os sistemas da empresa.

| Prioridade | Informação necessária e campos mínimos | Situação e ação | Pergunta que passa a responder |
|---|---|---|---|
| 1 | Datas de entrada/primeira entrega/encerramento, status no evento, motivo e indicador real/estimado/atribuído | Parte já existe em itens/log Silver; transportar para fato Gold, tratar casos sem histórico com decisão do negócio (PD07/08/19) | Quanto foi entregue, quanto saiu sem entrega e em qual mês isso ocorreu? |
| 1 | Snapshot diário/mensal, referência, load_id e instante da publicação | Começar a guardar fotografias e identificador comum; não reconstruir fotografia antiga como observada (PD13/19) | A fila caiu de verdade desde o fechamento ou houve correção retroativa? |
| 1 | ID estável do pedido/talento, origem, exclusividade com início/fim de vigência | Dados de 2026 existem parcialmente; unificar anos e limpar identidade/grafia; histórico de 2025 requer cadastro vigente (PD01/02/03/20) | Quais talentos concentram a demanda e como isso evolui entre anos? |
| 1 | Fases/status, expediente versionado, primeira entrega, reabertura, pacote/lote e idade dos abertos | Levar regras à Gold e avaliar também os ainda não entregues; a coluna de duração proposta sozinha não resolve todas as exceções (PD21) | Onde está a demora e qual é o risco da fila ainda aberta? |
| 2 | Demanda diária/semanal por recorte, calendário, datas estimadas, atraso de carga e campanhas conhecidas antecipadamente | Publicar séries com cobertura declarada e preservar versões; datas reais antigas podem exigir retorno à origem (PD09/10/22/23) | Quanto deve chegar e com que margem de incerteza? |
| 2 | Contratação, pedido vinculado, valor, moeda, status comercial e datas de fechamento/competência; pagamento quando aplicável | Integrar planilha de contratações e sistema financeiro, com dono e conciliação; não está disponível no contrato atual (PD05/06/18) | A demanda vira contratos e receita? Qual é o ticket e o prazo de pagamento? |
| 2 | Responsável/equipe, horas disponíveis, afastamentos e complexidade/esforço | Levantamento com a operação; não inferir capacidade apenas da contagem de entregas | A equipe consegue absorver a demanda com a capacidade disponível? |
| 3 | Regra de qualidade, entidade afetada, abertura/correção e carga | Histórico de ocorrências precisa chegar à Gold com taxonomia acordada (PD12/24) | A qualidade melhora e quais erros comprometem a análise? |
| 3 | Identificador de marca/cliente, CNPJ, setor e vínculos válidos | Depende do catálogo e acesso aprovado ao Salesforce (PD16) | Quem gera demanda, conversão e concentração? |

Também faltam decisões, que nenhuma tabela resolve: oficializar a meta SLA; validar o que conta como entrega/encerramento; acordar classificação de saídas externas; definir confiança mínima e avaliação prospectiva da previsão. Os códigos remetem ao registro existente em [O que falta](../paginas/o_que_falta.md); este complemento não altera esse registro nem os textos das telas.

Para a diretoria, priorizar **fluxo confiável + fila histórica + prazo/risco + resultado comercial**. Novas tabelas sustentam essas respostas; novos dados e regras aprovadas é que ampliam a análise.
