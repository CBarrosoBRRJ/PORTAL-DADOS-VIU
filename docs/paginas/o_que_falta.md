# Ficha — O que falta (fecho da área)

## 1. Identificação

| Item | Valor |
|---|---|
| Rota | `/viu-agenciamento/o-que-falta` (2 slides; link no fim da última seção e no menu lateral, não é aba) |
| Fonte única | `app/apresentacoes/gestao_orcamentos/pendencias.py`: `PENDENCIAS` (códigos PDxx) e `PEDIDOS` |
| Template | `app/templates/o_que_falta.html`; máscaras das seções em `app/templates/macros.html` (`pendente`, `lamina_pendente`) |
| Rota no código | `app/main.py` (`/{slug}/o-que-falta`, declarada antes de `/{slug}/{secao}`) |
| Testes | `tests/test_portal.py` (`test_o_que_falta`, `test_mascara_sem_numeros_e_com_pendencias`, `test_ordem_e_proxima_pergunta`) |
| Dados | nenhum número: só texto do registro de pendências e o `estado` de cada seção |

**Regra de manutenção:** a tabela abaixo é cópia de `pendencias.py` (26/10/2026), conferida por teste. O código é a fonte; mudou lá, atualize
aqui, no prompt para a gold (`docs/prompt_dados_pendentes.md`, rascunho) e no PRD. O código é o mesmo no site, no PRD e no prompt.

## 2. Pergunta e o que aparece na tela

- **Slide 1 — "O que ainda precisamos para completar a área?"** (Gerencial): "Onde estamos" lista Início e cada seção
  visível com a pergunta e o estado (ícone + texto: Pronta, Parcial, Aguardando dados); "O que pedimos hoje" lista os
  pedidos de decisão (`PEDIDOS`).
- **Slide 2 — "Que dados faltam, e quem tem a resposta?"** (Operacional): tabela Tela · Dado que falta (com o "como") ·
  Onde buscar · Quem responde, uma linha por pendência, com `id` = código (as máscaras linkam para `#PDxx`).

Estado das seções em 26/10/2026: Início, Talentos e Atendimento "Pronta"; SLA "Pronta · meta a oficializar"; Previsão
"Pronta · 2 decisões abertas"; Resultado e Qualidade "Aguardando dados" (Resultado fica fora do modo apresentação,
`na_reuniao=False`). Rodapé datado também nesta página (D49).

## 3. Pendências no código (26/10/2026)

Cópia fiel de `PENDENCIAS`, na ordem do código (gerada do próprio `pendencias.py` em 26/10/2026). O teste `tests/test_documentacao.py::test_o_que_falta_md_igual_a_pendencias` falha se um código existir só aqui ou só no código.

| Código | Tela | Dado que falta | Onde buscar | Como calcular | Quem responde |
|---|---|---|---|---|---|
| PD19 | Atendimento | Data das saídas e identificação da carga | gold de entradas e fluxo, a partir dos eventos da silver | Mesmo corte e carga nas tabelas; sinalizar saídas sem data e separar atribuição de evento observado | Caio (gold) |
| PD20 | Talentos | Continuidade dos dados na virada do ano | gold de talentos com anos e identidade estável dos pedidos | Conciliar entradas e talentos sem trocar manualmente o board; preservar origem e exclusividade histórica | Caio (gold) |
| PD01 | Talentos | Exclusividade do talento na base de entradas | silver 2026 (exclusivo, talento) levada para a gold de entradas | Pedidos por mês e grupo (exclusivo, não exclusivo, sem talento), com as regras de data do Início | Caio (gold) |
| PD02a | Talentos | Ranking dos exclusivos lido da gold (hoje a dica lê a silver) | gold de PD01 + cadastro de talentos exclusivos (39 nomes) | Pedidos por talento no período, pela exclusividade na data do pedido; mesmo top 10 da dica | Caio (gold) |
| PD02b | Talentos | Cadastro limpo de talentos não exclusivos | monday (interveniência) e padronização de nomes na silver | Padronizar as grafias e só então ranquear, com mínimo de 10 pedidos | Equipe de Talentos |
| PD03 | Talentos | Lista de exclusivos de 2025 com vigência | board 2025 e cadastro de talentos exclusivos (início e fim do contrato) | Mesma regra de 2026: exclusivo = na lista vigente na data do pedido | Equipe de Agenciamento |
| PD05 | Resultado | Contratações fechadas: talentos, volume e ticket médio | planilha de contratações (Mayara), a subir para o BigQuery; vendido? do board como conferência | Fechamentos por mês, talento e tipo; ticket médio = valor ÷ contratos; conversão sobre entregues | Mayara + Caio |
| PD06 | Resultado | Regra do que acontece depois da entrega | gold do SLA (status atual, alerta, encerrado sem entrega) | Entregues por destino: aguardando, em alerta, encerrado sem retorno, declinado | Caio + equipe de orçamentos |
| PD18 | Resultado | Prazo de pagamento dos intervenientes | contratos e pagamentos (sistema financeiro) | Dias do contrato assinado até o pagamento, por mês | Financeiro + Caio |
| PD07 | Atendimento | Motivo de quem saiu sem entrega | gold fluxo mensal (status no evento) | Separar declinado, standby e encerrado por mês | Caio (gold) |
| PD08 | Atendimento | Regra de entrega sem histórico de status | gold de entradas + decisão da equipe (185 entregas só com data de saída) | Contar ou não como entrega; nota na ficha | Equipe de orçamentos |
| PD09 | Previsão | Acerto da previsão fora do teste, mês a mês | registro de uma previsão oficial por retrato mensal (ml/saida/historico_previsoes.jsonl e retratos/<mês>.json, já gravados) + gold de entradas | A cada mês fechado (out/26 é o 1º), comparar com o previsto no retrato anterior; decidir se o Mercado mantém a rede neural (vence o teste jun–set, perde da ingênua em jan–mai) | Caio (critério) |
| PD22 | Previsão | Previsão na virada do ano | retratos de out a dez/2026 (horizonte de 3 meses chega a jan/27) e PD20 | Decidir o que a tela mostra em nov/dez (eixo só 2026 hoje; os meses de 2027 já saem com o ano, "jan/27") e quando o eixo passa a 2027 | Caio (decisão) |
| PD23 | Previsão | Job mensal da previsão em produção | hoje roda no computador do Caio (ml/, rotina disparada pelo site local); em produção: Cloud Run Job + bucket | Rodar a rotina mensal fora do site, gravar previsao.json, retratos e histórico num bucket e ler de lá; comandos de GCP com o Caio | Caio (GCP) |
| PD10 | Previsão | Datas reais de 2025 para confirmar o efeito de fim de ano | gold de entradas: 17% a 25% das datas de 2025 são estimadas (PD03/F10) | Com as datas reais, medir de novo a queda de nov/dez (2025: −31% a −59% sobre out); a janela de 12 meses não aprende fim de ano | Caio (gold) |
| PD12 | Qualidade | Evolução das pendências de preenchimento | silver de qualidade e pendências diárias (desde 21/10), levadas para uma gold | Abertas por dia e categoria; corrigidas; tempo até a correção | Caio (gold) |
| PD13 | Qualidade | Foto de fim de mês da base | gold com o mês de referência guardado | Diferença entre a foto do mês e a leitura de hoje | Caio (gold) |
| PD24 | Qualidade | Inbound marcado como talento não exclusivo | silver 2026 (TAB_TALENTO_ORIGEM, mesmo critério de app/sql/talentos_ano.sql): pedidos de Inbound cujo talento está como não exclusivo; contados por mês em ml/dados/exclusividade.csv e no bloco "qualidade" do previsao.json | Corrigir o cadastro na origem (talento ou tipo de input) e alarmar na gold; até lá a Previsão conta esses pedidos como exclusivos e o filtro "Não exclusivos" do Inbound fica "Não se aplica" | Caio (gold) + equipe de orçamentos |
| PD15 | SLA | SLA de entrega em 2025 | não existe: o board de 2025 não guardou o histórico de status | Sem cálculo possível; comparação com o ano anterior começa em 2027 | Não disponível |
| PD21 | SLA | Tempo da equipe pronto na gold | fase própria para o Retorno Marca; manter quem já teve a 1ª entrega e voltou à equipe; coluna de pacote/lote; relógio para cards criados direto em elaboração/revisão; pedidos em andamento; v2 sem almoço | SLA lido direto da gold, sem recálculo no site; mediana sem viés dos que ainda não foram entregues | Caio (gold) |
| PD16 | Fora da área por ora | Análise por marca, cliente e setor | catálogo de marcas no monday, CNPJ e setor no Salesforce (aguarda liberação) | Cruzar pelo CNPJ, que resolve nomes diferentes da mesma marca | Caio + Salesforce |

Códigos que não existem no código (PD04, PD11, PD14, PD17) foram propostos no debate de 23/10 e não entraram; não usar.

## 4. Pedidos de decisão (`PEDIDOS`, slide 1)

| Pedido | Por quê | Quem |
|---|---|---|
| Oficializar a meta do SLA | metade dos orçamentos prontos em até 2 dias de trabalho (16 h); hoje uma sugestão | Diretoria |
| Subir a planilha de contratações para o BigQuery | abre a tela de Resultado (talentos contratados, volume e ticket médio) | Mayara + Caio |
| Levar a exclusividade do talento para a base de entradas | abre a divisão por mês e os rankings da tela de Talentos | Caio (gold) |
| Validar com a equipe as regras de entrega e de encerramento | o que conta como entrega sem histórico e o que é “Encerrado” | Equipe de orçamentos |

As decisões que ainda são do Caio (vencedor do Mercado, nov/dez como cenário, régua do Atendimento, recorte do slide 6 do estudo, veredito da meta, "amostra aleatória" no slide 3, critério do vermelho, ponte de bases do SLA) não vão para esta página da diretoria: ficam no PRD, seção 9.7. SLA e Previsão aparecem como "Pronta · meta a oficializar" e "Pronta · 2 decisões abertas" (`Secao.nota_estado` em `apresentacao.py`).

## 5. Validações e limites

- 23/10/2026: testes confirmam um `id` por pendência, máscaras sem nenhum dígito de dado e a ordem Início → seções → "O
  que falta"; 89 testes.
- No modo apresentação, "Onde estamos" lista só as seções visíveis; a tabela do slide 2 lista todas as pendências.
- Talentos não mostra máscara na tela (tela limpa, a pedido do Caio): PD01–PD03 aparecem só aqui.

## 6. Histórico da página

| Data | Mudança |
|---|---|
| 23/10/2026 | Página criada (D30): estado das seções, pedidos de decisão e tabela das pendências a partir de `pendencias.py` |
| 26/10/2026 | Batalha 2 (G2-4): pedido nº 1 sem o marcador "X" — "metade dos orçamentos prontos em até 2 dias de trabalho (16 h); hoje uma sugestão" (a cláusula dos 5 dias só volta com um valor proposto pelo Caio); estado com nota (`Secao.nota_estado`): "Pronta · meta a oficializar" (SLA) e "Pronta · 2 decisões abertas" (Previsão), ícone + texto; Resultado com `na_reuniao=False` (no modo apresentação, a Previsão leva à Qualidade); `/previsao/regras` volta para a Previsão (307; só SLA e Atendimento têm `/regras`); PD22 e PD23; teste contra marcador provisório em `PEDIDOS` |
| 26/10/2026 | D55: PD24 (Inbound marcado como talento não exclusivo = erro de cadastro; a Previsão conta como exclusivo) |
| 26/10/2026 | Documentação da batalha 2 (D49): seção 3 regenerada de `pendencias.py` (20 códigos; entram PD19–PD23 e os textos atuais de PD02a, PD09 e PD10), seção 4 com o texto atual dos `PEDIDOS`, estado das seções de 26/10; teste `tests/test_documentacao.py` compara os códigos da ficha com o código; decisões internas do Caio no PRD 9.7 |

## Complemento da revisão de 24/10/2026

- **PD19 — Data das saídas e identificação da carga:** obter eventos da Silver para Golden de entrada/fluxo; publicar `load_id` e `data_referencia` comuns, mês efetivo, status/motivo e sinalizador de data ausente/atribuída. Há dez saídas sem data em 2026, atribuídas ao mês de entrada no relatório. Reconciliar por mês e tipo as quatro situações, além do total; não substituir ausência por uma data observada fictícia.
- **PD20 — Continuidade multianual de Talentos:** Golden com identidade estável do pedido, board de origem, transferências e exclusividade na data do pedido. Mesma população e corte de entradas; dispensar troca manual de tabela em janeiro. Fonte atual continua configurada no board 2026.
- **PD13 permanece:** a curva atual é reconstruída, não fotografia fechada. Manter snapshots de referência sem reescrever o passado silenciosamente.

São requisitos locais preparados para análise no projeto da Golden; nenhuma alteração de BigQuery foi executada. Ver `docs/historico/REVISAO_2026-10-24.md` para evidências e critérios de aceite. No Atendimento, 170 × 160 foi resolvido por convenção explícita de mês atribuído; a ausência das datas na fonte continua pendente.
