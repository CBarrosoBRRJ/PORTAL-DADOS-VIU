# Auditoria técnica, dados e previsão — 26/10/2026

**Complemento posterior:** após o encerramento desta auditoria de dados, Caio autorizou ajustes exclusivamente de movimento. Nessa rodada, CSS e JavaScript receberam mudanças de animação, preservando templates, layout e informação. Ver [revisão de movimento](REVISAO_MOVIMENTO_2026-10-26.md). As declarações de preservação do CSS abaixo descrevem o encerramento da etapa original, antes desse novo pedido.

## Resultado e escopo

As contagens e o SLA verificados fecharam com a carga consultada. Corrigidos defeitos de cache, concorrência, registro de falhas, validação de previsões e JavaScript no celular. **HTML, CSS e textos das páginas foram preservados**; a única alteração no JavaScript é uma proteção contra medição de elemento oculto. Não houve criação de tabela, alteração de dados, IAM ou implantação no GCP.

Não é uma garantia de ausência de qualquer defeito. A evidência cobre o checkout atual, a carga de 26/10/2026 com corte em 25/10 e os cenários descritos abaixo. Autenticação de produção, futuras cargas/anos e o novo pipeline Gold ainda exigem homologação. As fontes Silver anuais e a régua fixa da previsão impedem afirmar que o projeto está pronto para crescer indefinidamente sem manutenção.

Entrega para continuidade com Claude: [Plano Gold por visual e SQL passo a passo](PLANO_GOLD_POR_VISUAL.md). O PRD e as decisões visuais anteriores não foram reescritos. Este documento complementa aquelas decisões com achados técnicos.

## 1. Conferência com BigQuery

Identidade efetiva confirmada: `caio.barroso@viu.com.br`; projeto `gglobo-viu-dados-hdg-prd`. Somente SELECT, metadados e dry runs. Snapshots detalhados ficaram fora do repositório, em pasta temporária local; os documentos guardam evidências agregadas.

| Fonte/contrato consultado | Linhas lidas |
|---|---:|
| Gold entradas diárias | 2.344 |
| Gold fluxo mensal | 622 |
| Silver: divisão anual de talentos | 3 |
| Silver: ranking e histórico mensal | 431 |
| Gold movimentos SLA | 14.998 |
| Silver itens + log: composição das saídas | 40 |

Evidências: [fontes, schemas e jobs](../validacao/auditoria_fontes_2026-10-26.json), [reconciliação](../validacao/reconciliacao_auditoria_2026-10-26.json) e [SLA independente](../validacao/auditoria_sla_2026-10-26.json).

Resultados:

- **5.556 entradas** na safra de 2026 = **5.389 resolvidas/saídas + 167 em andamento**. “Resolvida” inclui saídas sem entrega; não equivale a entrega ao cliente.
- Entrada e fluxo conciliados em **299 grupos de safra × grupo × tipo × família**. As quatro situações fecham o total em cada linha de entrada.
- Talentos: **3.451 exclusivos + 1.980 não exclusivos + 125 sem classificação = 5.556**. Nenhum dos 125 sem classificação tinha nome preenchido na consulta de perfil realizada. Squad: 119 nos não exclusivos, conforme regra existente.
- A composição por status conciliou com as saídas sem entrega em **janeiro a outubro**. Outubro permanece parcial.
- Exemplo A27 de outubro: 717 para atender − 19 saídas externas = 698 no denominador; 446 entregues ÷ 698 = 63,90%, apresentado como 64%. A classificação de quais status são externos é regra de negócio, não conclusão estatística.
- SLA recalculado por SQL de intervalos, sem chamar as funções de duração do site: **2.347 pedidos, mediana 14,252 h**; exclusivos: **1.609 / 11,826 h**; não exclusivos: **725 / 19,642 h**. O total inclui 13 pedidos sem classificação de exclusividade; não forçar a soma dos dois filtros a igualar o total. Foram comparados também cortes de 16h, meses, tipos, status e travamentos nos três grupos.

A auditoria das fontes registrou **501.238 bytes processados e 31.457.280 bytes faturáveis**. Os dois jobs da conferência independente de SLA registraram cache hit e zero bytes processados; aquele utilitário não registra bytes faturáveis. Os nove SELECTs do plano foram apenas dry runs, com estimativas individuais no JSON. Esses números não representam custo de futura publicação nem uma auditoria de todo o faturamento da conta.

Limites: o calendário veio da mesma especificação operacional do projeto, embora o algoritmo SQL de intervalos seja independente. Não foi revalidada a origem de cada evento contra o Monday nem reprocessada toda a Bronze. A reconciliação de totais não prova equivalência item a item entre cargas sem um identificador comum.

## 2. Defeitos corrigidos

| Prioridade | Arquivo | Reprodução/efeito anterior | Correção e evidência |
|---|---|---|---|
| Alta | `app/dados.py` | Só o log Silver muda; cache de `saidas_status` observa apenas itens e mantém composição antiga | `Consulta` aceita dependências; assinatura inclui metadado do log. Teste altera só o log e exige nova carga |
| Alta | `ml/rodar.py`, `juntar` | Resultados de cargas diferentes eram reunidos com aviso, inclusive modelos antigos preservados em execução parcial | Recusa lote e modelo de outra carga antes de escrever resultado |
| Alta | `ml/rodar.py`, `_previsao` | Publicação falha, exceção é impressa e execução termina com sucesso | Exceção propagada; estado registra falha e mantém último arquivo válido |
| Alta | `ml/rodar.py`, rotina/acompanhamento | Segundo processo sobrescreve a trava do primeiro | Criação exclusiva com `open('x')`; concorrente não apaga a trava existente |
| Média | `ml/rodar.py`, acompanhamento | Atualizador retorna False e job anuncia sucesso | Retorno recusado gera falha nas duas entradas de execução |
| Alta | `ml/regua.py`, `_normalizar` | NaN/inf no previsto ou limites inválidos podem distorcer comparação | Recusa previsto não finito, limites infinitos, incompletos ou invertidos; ausência dos dois limites continua permitida |
| Média | `previsao/calculos.py`, `ler` | JSON regravado com mesmo tamanho/timestamp mantém contrato anterior em cache | Cache por SHA-256 do conteúdo; o teste de troca de versão que falhava passou |
| Alta | `app/static/apresentacao.js`, `colocar` | Em 390px, aba oculta tem `offsetParent=null`; TypeError interrompe inicialização dos controles | Só mede elemento com caixa de layout; reprodução no navegador desapareceu, sem mudar desenho |

Os testes falsos de acompanhamento foram ajustados para retornar True em sucesso, como a função real. Adicionado teste específico para False. Nenhuma validação foi relaxada para fazer a suíte passar.

## 3. Testes e interface

Baseline: 462 passaram, um falhou (cache do contrato da previsão). Após as correções Python: **475 passaram**, um aviso de descontinuação Starlette/httpx, sem falha. Evidência: [JUnit](../validacao/testes_auditoria_2026-10-26.xml).

Após a proteção JavaScript: **46 testes de movimento, Talentos e interface passaram**; verificações reais com Playwright em **390×844 e 1440×900**, nas páginas Início, Talentos filtrado, SLA filtrado, Previsão filtrada e Atendimento: dez navegações com HTTP 200, sem erro JavaScript e sem rolagem horizontal global. [Evidência do navegador](../validacao/navegador_auditoria_2026-10-26.json).

Qualidade respondeu 200 no desktop. `/resultado` respondeu 404: seção desabilitada por configuração de reunião (`na_reuniao=False`), não defeito novo de roteamento. Não foi habilitada ou preenchida artificialmente.

Essas verificações não são certificação completa de acessibilidade ou de todos os cruzamentos de filtros, zoom e navegador. Nenhuma mudança visual foi feita para corrigir problemas hipotéticos. Comparação SHA-256 com o backup preserva todos os templates e CSS; só o JS citado mudou entre os ativos de apresentação.

## 4. Previsão: o que está certo e o que precisa evoluir

Foram recalculadas **1.284 métricas WAPE/MAE** dos resultados salvos dos **61 candidatos**, com tolerância apenas para o arredondamento de duas casas do backtest: **zero divergências**. Verificações incompletas de séries curtas continuam sem nota agregada, conforme D56. [Auditoria reproduzível](../../tools/auditar_modelos.py), [resultado e sensibilidade ao retirar um mês](../validacao/auditoria_modelos_2026-10-26.json).

| Série | Modelo publicado | WAPE jun–set, h1 | WAPE jan–mai | Cobertura no teste da faixa nominal 80% |
|---|---|---:|---:|---:|
| Inbound | Média de 6 meses | 14,41% | 26,93% | 3/4 = 75% |
| Mercado | MLP 1 unidade | 12,63% | 26,77% | 1/4 = 25% |
| Mercado exclusivos | Mediana de modelos | 10,90% | Sem janela completa | Sem faixa |
| Mercado não exclusivos | Holt amortecido | 19,23% | Sem janela completa | Sem faixa |

Os erros estão calculados corretamente, mas **não demonstram robustez futura**. Quatro meses para selecionar entre dezenas de candidatos favorecem um vencedor por acaso. A verificação anterior não é um novo holdout intocado depois de repetidas explorações. Cobertura observada com quatro pontos tem enorme incerteza; não comprova cobertura de 80%. Os horizontes 2 e 3 são avaliados, mas não determinam o vencedor embora apareçam na previsão.

Há divergência entre documentação D56 e implementação: `RedeNeural(..., globais=True)` usa também janelas da outra série, cortadas no passado de cada origem. Não encontrei uso de meses futuros nessa rotina, mas ela **não é univariada**, como a descrição afirma. Não mudar essa opção sem versionar o experimento e refazer os resultados.

Experimento isolado, sem publicar: MLP com uma unidade, mesmas cinco sementes, `globais=False`, só Mercado. WAPE h1 foi **20,33%** e verificação **31,40%**. Desligar o compartilhamento não melhorou esse protocolo. [Evidência](../validacao/mlp_univariado_2026-10-26.json). Isso testa uma hipótese, não seleciona um novo vencedor nem prova superioridade futura do modelo global.

Outras limitações:

- Períodos TESTE/VERIFICACAO e ano visual são fixos em 2026. Reexecutar mensalmente não torna a avaliação automaticamente móvel.
- Séries de exclusividade têm somente nove meses fechados; modelos complexos e sazonalidade anual não ficam sustentados por esse histórico.
- Faixas futuras podem não conter a previsão pontual (Inbound nos horizontes seguintes), consequência da calibração por razão. Não “corrigir” visualmente encaixando o ponto à força: revisar o método de distribuição/viés.
- Acompanhamento proporcional aos dias úteis pressupõe chegada uniforme. Pedidos em lote violam essa aproximação; o diagnóstico de lotes é descritivo e não prova a causa do desvio.
- Resultados atuais podem ser reproduzidos com dados revisados depois dos eventos; sem versões históricas dos dados, não é possível provar um backtest com exatamente a informação disponível na época.

### Protocolo recomendado para a próxima etapa

1. Congelar e versionar dados, calendário, sementes, dependências e protocolo. Preservar os retratos já publicados.
2. Usar origens temporais móveis: treino só no passado, escolha de hiperparâmetros dentro do treino e período externo para avaliação; reservar meses futuros ainda não vistos para acompanhamento prospectivo. Essa separação segue [TimeSeriesSplit](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html) e a validação temporal de [Forecasting: Principles and Practice](https://otexts.com/fpp3/toolbox.html).
3. Comparar uma grade pequena: último mês, médias 3/6, SES/Holt amortecido, ridge com atrasos e calendário; testar modelos de contagem Poisson/binomial negativa quando houver série diária/semanal suficiente. Manter MLP global como desafiante explicitamente identificado; não ampliar a busca para centenas de candidatos com quatro meses de prova.
4. Avaliar h1/h2/h3 separadamente e o impacto operacional: MAE em pedidos, WAPE agregado, viés, MASE quando aplicável e erro acumulado do trimestre. Não usar média de WAPEs de grupos como WAPE global.
5. Calibrar intervalos por horizonte em resíduos fora do treino; medir cobertura e largura conjuntamente, além do escore de intervalo. Poucos resíduos devem resultar em limitação declarada, não certeza estatística.
6. Exigir melhoria consistente contra referência simples em origens múltiplas e registrar estabilidade do vencedor. Definir com o negócio o ganho mínimo útil em pedidos; um pequeno ganho percentual não justifica complexidade por si só.
7. Para coerência entre total e exclusividade, modelar também “sem classificação” e reconciliar as partes. Não repartir o total por proporção fixa nem somar dois filtros incompletos como total.

Nada desse protocolo substituiu os modelos publicados nesta auditoria. Trata-se de evolução metodológica que deve receber nova versão; não de ajuste cosmético para produzir um resultado mais bonito.

## 5. Arquivos, organização e resíduos

Inventário individual com SHA-256, tamanho, classificação, decisão e definições Python: [inventário](../validacao/inventario_auditoria_2026-10-26.json). Todos os Python encontrados foram analisados sintaticamente; revisão semântica concentrou-se nos caminhos de dados, cálculos, atualização, publicação e navegação. Isso não significa que cada linha tenha sido demonstrada formalmente correta.

Backup anterior às alterações: `C:/Users/CCMB/AppData/Local/Codex/Backups/PPD-AGENCIAMENTO-SLA-auditoria-20261026`, sem `.env`. Não havia repositório Git ativo neste diretório; não foi criado commit nem PR fictício.

Organização: plano separado do PRD, SQL em `docs/sql/gold_relatorio`, evidências em `docs/validacao`, utilitários reproduzíveis em `tools`. Preservados `_descartados`, estudos D47/D55, imagens e documentos de revisões anteriores.

Duplicatas binárias ativas preservadas por necessidade:

- `__init__.py` vazios: cada um identifica um pacote diferente.
- `.gcloudignore` e `.dockerignore`: consumidores diferentes; ambos precisam existir.
- `ml/saida/previsao.json` e `retratos/2026-09.json`: arquivo corrente e retrato imutável; podem coincidir hoje e divergir na próxima atualização.

Não foram removidos arquivos de negócio por suposição. A tentativa de excluir somente bytecodes órfãos foi bloqueada pela revisão automática do ambiente. Esses resíduos são regeneráveis e não afetam os cálculos; não contornei o bloqueio usando outro mecanismo de exclusão.

## 6. Pendências para continuidade

| Prioridade | Pendência | Critério de conclusão |
|---|---|---|
| Alta | Contratos Gold e corte comum | Executar plano em homologação, conciliar todas as chaves, migrar leitores e testar cargas reais |
| Alta | Virada anual | Fontes históricas unificadas, testes 31/dez e 1/jan; ano da previsão dinâmico com dados disponíveis |
| Alta | Previsão robusta | Protocolo temporal versionado, avaliação prospectiva e intervalos calibrados |
| Alta para produção | Autenticação | Implementar/homologar controle de acesso; `AUTH=off` continua proibido no Cloud Run |
| Média | Concorrência completa de ML | CLI manual `--modulo`/`--juntar` ainda não usa a trava da rotina; não executar junto com job. Estado da última tentativa pode refletir concorrente recusado, e não o proprietário ativo |
| Média | Falha abrupta do job | Trava pode sobreviver à queda; verificar PID/processo antes de remoção manual; não apagar por tempo arbitrário |
| Média | Extração consistente | CSVs trocados individualmente; publicação de snapshot inteiro e `load_id` comum melhorariam atomicidade |
| Média | Cache/hash de dataset | `processado_em` identifica carga, mas não substitui hash de todos os dados, código e dependências do experimento |
| Média | Documentação técnica | Comentários antigos A25 coexistem com A27; regra executada atual documentada aqui. Harmonizar descrições na próxima revisão de regras, sem alterar a página |

O projeto pode continuar localmente com as correções entregues. Não classifico essas evidências como implantação de produção nem como comprovação de escalabilidade ilimitada. O plano identifica o que falta para retirar a Silver da aplicação e tornar a atualização rastreável.
