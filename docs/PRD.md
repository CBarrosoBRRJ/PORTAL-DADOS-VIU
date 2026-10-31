# PRD: Site de relatórios do Agenciamento (SLA e próximas análises)

**Desempenho da troca de página (31/10/2026; auditoria F14, F15, F18, F20; sem mudança visual nem de regra):**
medido no computador (servidor 8400 com `--reload` no Google Drive, Chrome headless pelo CDP, 1440×900, navegação como
a seta →). TTFB = 1º byte da página; "pronta" = evento `load` da página nova (o título do slide visível vem junto ou
antes).

| Página | TTFB antes (3 pedidos, ms) | TTFB depois (ms) | Pronta antes (ms) | Pronta depois (ms) |
|---|---|---|---|---|
| Capa | 930 · 110 · 120 | 6 · 4 · 4 | — | — |
| Roadmap | 280 · 230 · 300 | 22 · 26 · 39 | 344 | 171 (pela →); 87–202 (vindo de uma página) |
| Demanda | 700 · 210 · 180 | 12 · 19 · 19 | 896 | 105 |
| Talentos | 260 · 280 · 240 | 17 · 9 · 17 | 403 | 64 |
| SLA | 140 · 110 · 120 | 57 · 12 · 12 | 90 | 52–104 |
| Como medimos | 470 · 400 · 370 | 20 · 9 · 10 | 1.349 | 114 |
| LIA | 60 · 80 · 100 | 32 · 16 · 31 | 137–745 | 70–158 |
| Iniciativas | 80 · 40 · 40 | 12 · 9 · 17 | 212 | 59 |
| Previsão | 110 · 110 · 1.090 | 68 · 48 · 36 | 750 | 75–179 |
| Encerramento | 50 · 50 · 40 | 17 · 20 · 3 | 51 | 57 |

Causas e correções: (1) no computador, a versão dos estáticos relia ~1 MB do Drive a cada 5 s **dentro** da
requisição (0,5–0,9 s; os picos de 700 ms–1,1 s) → hash por data + tamanho, refeito em segundo plano; (2) pandas a cada
clique (Demanda 93–318 ms, Talentos 280 ms, exemplo do estudo 950 ms, SLA 73 ms) → `_guardado` em `apresentacao.py`,
por carga + parâmetros + ambiente/corte, devolvendo cópia; `Tabela.processado_em()` uma vez por carga; (3) Jinja
conferindo a data dos templates no Drive a cada página (~40 ms) → no máximo a cada 2 s; (4) imagens do Roadmap lidas
inteiras a cada página (~65 ms) → só o cabeçalho, uma vez por processo; (5) 1ª visita compilando template/estudo → aquecidos
ao subir (só seções visíveis); (6) pré-carga: só a próxima página (`rel=next`, immediate), o resto por hover;
(7) sem sondagem de HTML com base congelada ou em produção. Já existiam e foram conferidos: gzip (CSS de 398 KB vai em
94 KB), cache de 1 ano com `?v=`, fontes com `preload` e `font-display: swap`, View Transition de 240 ms só sem
movimento reduzido. Limites: o Chrome desliga o prerender com o DevTools ligado (`PrerenderingDisabledByDevTools`), então
a tabela mostra o prefetch embutido do prerender; no navegador real a próxima página já chega montada. Dentro do quadro
da tela cheia (iframe, D59) a pré-carga não vale: para a reunião, preferir F11. Produção: `--min-instances=1
--cpu-boost` (`docs/deploy_iniciativas.md`). Registro: `docs/auditoria/correcoes_2026-10-31.md`; testes:
`tests/test_desempenho.py`.

**Corte e congelamento em 31/10/2026 — D65 (31/10/2026, reunião de 04/11):** `CORTE_DADOS=2026-10-31` (padrão do código, no computador e em produção). O portal aceita cargas enquanto os dados vão até antes de 31/10 (E3). A 1ª carga com dados até 31/10 (ou até 01/11, pela folga de 1 dia: 31/10 é sábado e a carga agendada seguinte é a de seg 02/11) é a última. Ela congela e fica gravada em `app/base_congelada/` (parquet + ficha por tabela, regras K1–K7 em `app/congelamento.py`). No Cloud Run, a pasta vai na imagem e o portal lê só dela, sem BigQuery. O `Dockerfile` passa a copiar `ml/saida/previsao.json`. A Previsão da reunião é o **retrato de outubro** (`python -m ml.rodar --rotina` depois da carga do corte). A LIA vai até 31/10 (`tools/extrair_lia.py --fim 2026-10-31`). **Caminho B (Caio, 31/10/2026):** congelar na carga agendada de seg 02/11 (dados até 01/11, pela folga); rodapé "Dados até 01/11/2026"; base, Previsão e LIA rodadas na segunda. Roteiro do dia 01/11 e de como descongelar (`CORTE_DADOS=off`): [congelar_outubro.md](congelar_outubro.md). Ferramenta: `tools/congelar_base.py` (gera; `--conferir` sem BigQuery). Testes: `tests/test_corte.py`.

**Cola dinâmica — 28/10/2026:** a porta 8200 consome `/cola/{ficha}` (local, SINC, CORS restrito), com falas montadas pelos mesmos contextos das páginas. Sem números ou interpretações de crescimento fixos no cliente. Atualização ao abrir/a cada 60 s, subordinada ao cache e ao congelamento do portal. Recorte Todos sinalizado; previsão vinculada ao último retrato publicado. Sem dados ou com falha, oculta os números e avisa. Sem nova SQL, alteração de regra de cálculo ou escrita no GCP. Código: `app/apresentacoes/gestao_orcamentos/cola.py`; testes: `tests/test_cola.py`.

**Ajuste de navegação — 28/10/2026:** SLA → Previsão no gancho do rodapé e nas setas da sequência principal. "Como medimos" é aprofundamento opcional pelo botão Estudo; seus slides e saída para Previsão permanecem disponíveis. Substitui a passagem obrigatória pelo estudo da D62, sem mudar cálculos ou layout.

## Estado atual (27/10/2026, D57) — ler primeiro

**D57 (27/10/2026): o site só lê a gold.** Cada gráfico lê a sua tabela ou view no `gold_monday` (8 tabelas + 8 views,
criadas no PPD-GOLDEN-AGENCIAMENTO-MONDAY e atualizadas pelo job `gold-agenciamento`); acabaram as exceções da silver
(D30-b, A26) e o expediente sem almoço recalculado no site (C2): o site não refaz regra de negócio. Mapa página × gráfico
× tabela em "Retrato do código". Conferência de 27/10 (carga das 11:11): o código antigo e o novo montaram as 21 visões
(Início com os extratos, Atendimento, SLA e estudo nos 3 grupos, Talentos nos 3 filtros) sobre a mesma carga real com
**0 diferenças**; na previsão, 1 pedido do Mercado exclusivos passa de abril para março (calendário completo da gold, o
card sem data de criação de 08/04), efeito só na próxima rodada do ML. Testes: 475.

Portal **"Gestão de orçamentos"** para a reunião de diretoria de **28/10/2026** (apresentação local; nada publicado). A
batalha do portal de 26/10 (D49) revisou todas as páginas em três levas — textos e cálculos, interface e movimento,
documentação e limpeza — **sem mudar regra de negócio**. Linha do tempo da etapa (21–26/10): [HISTORICO_2026-10.md](HISTORICO_2026-10.md).
Os blocos "Último ajuste / Ajuste anterior" que ficavam aqui foram para a seção 12 (arquivo, sem cortes).

| Página | Rota (sob `/viu-agenciamento`) | Estado | Regras e ficha |
|---|---|---|---|
| Início | `/` | Pronta (D28) | E0–E9; [inicio.md](paginas/inicio.md) |
| Talentos | `/talentos` | Pronta (D31; gold de talentos desde a D57) | T1–T6; [talentos.md](paginas/talentos.md) |
| Atendimento | `/atendimento` | Pronta (D33; % pela A30, D58b) | A13, A15, A16, A24, A30; [atendimento.md](paginas/atendimento.md) |
| SLA de entrega | `/sla` | **Pronta · meta a oficializar** (D34–D38, D49, D54) | C1–C10, C3c (D54; antes C3b), D-SLA-1 a D-SLA-7; [sla.md](paginas/sla.md), "Estado vigente" |
| Estudo "Como medimos" | `/sla/como-medimos` (slides 1–8; slide 2 com `?passo=1\|2\|3`) | Pronto (D34–D46) | E, X, W, V, U, K, J, Z; [sla.md](paginas/sla.md) |
| Previsão de demanda | `/previsao` | **Pronta · 2 decisões abertas** (D47, D48, D55, **D56**: uma série e um modelo por recorte) | P1–P12, C1–C5, J1–J6, R1–R7, S1–S6, AT1–AT7; [previsao.md](paginas/previsao.md), seção 5.0 |
| Resultado | `/negocios-fechados` | Aguardando dados; **fora do modo apresentação** | PD05, PD06, PD18; [demais.md](paginas/demais.md) |
| Qualidade | `/qualidade` | Aguardando dados (a fazer na semana de 26/10) | PD12, PD13; [demais.md](paginas/demais.md) |
| O que falta | `/o-que-falta` | Pronta (D30), gerada de `pendencias.py` | [o_que_falta.md](paginas/o_que_falta.md) |

**Regras vigentes que mais se confundem com as antigas:** meta do SLA = **metade dos orçamentos prontos em até 2 dias de
trabalho (16 h)** (D38/D-SLA-7; a "75% em até 3 dias" da D37 foi revista); mês do SLA = mês da 1ª entrega (D-SLA-1); prazo
do cliente em **dias úteis no calendário** (C3b); "típico" = mediana; limite do "fora da curva" no estudo = 59 h na carga
de 26/10 (Q3 + 1,5 × IQR; o de 210 h em log era da D37); Previsão com janela de 12 meses, teste jun–set/2026, menor WAPE e
execução mensal (D48; a D47 é histórico).

**Carga da reunião (por ora):** `_processado_em` 26/10/2026 09:01 (São Paulo), dados até 25/10. `tools/checar_reuniao.py`
nessa carga: **tudo certo** (registro em `docs/validacao/reuniao_2026-10-26.json`; estudo em
`docs/validacao/estudo_2026-10-26.json`). Números por página no topo de cada ficha. Na véspera e na manhã de 28/10:
`python -m ml.rodar --acompanhamento`, subir com `MODO=apresentacao` (base congelada, job da Previsão parado) e rodar
`python tools/checar_reuniao.py` de novo; se a carga mudar, trocar os retratos das fichas.

**Decisões abertas do Caio antes de 28/10:** seção [9.7](#97-decisões-do-caio-antes-de-2810-batalha-de-26102026).
**Testes:** `python -m pytest tests -q` (475 em 27/10/2026, dados sintéticos, sem BigQuery; as views da gold simuladas em
`tests/gold_simulada.py`). **Servidor local:** porta 8100.

| | |
|---|---|
| **Responsável** | Caio Barroso (dados) — também o administrador do site |
| **Situação** | 🔧 **Em desenvolvimento local** (26/10/2026): portal da área Orçamentos (D30) com Início, Talentos, Atendimento, SLA (meta a oficializar), estudo "Como medimos" e Previsão (2 decisões abertas) prontos; Resultado e Qualidade em máscara; "O que falta"; modo apresentação para 28/10; acesso (fase 2) e deploy (fase 3) pendentes; nada publicado |
| **Última revisão** | 26/10/2026 (D49) |
| **Projeto GCP** | `gglobo-viu-dados-hdg-prd` (região `us-central1`, BigQuery `US`) |
| **Fontes** | `gold_monday`: `gld_agenciamento_2026_sla_movimentos` (`TAB_SLA`), `gld_agenciamento_entrada_diaria` (`TAB_ENTRADA`), `gld_agenciamento_fluxo_mensal` (`TAB_FLUXO`); exceção temporária D30-b: `silver_monday.slv_agenciamento_2026_itens` (`TAB_TALENTO_ORIGEM`, só os agregados anuais de Talentos e a parcela de exclusividade da Previsão) |
| **Projeto anterior** | `../PPD-GOLDEN-AGENCIAMENTO-MONDAY` — gera as tabelas gold; ficha da tabela SLA em `../PPD-GOLDEN-AGENCIAMENTO-MONDAY/docs/tabelas/gld_agenciamento_2026_sla_movimentos.md` |
| **Documentos** | **retomada: [CLAUDE.md](../CLAUDE.md)** · [README](../README.md) · [histórico da etapa](HISTORICO_2026-10.md) · [fichas](paginas/README.md) |

## Retrato do código (26/10/2026)

> O retrato de 23–25/10 que abria esta seção (blocos D28 a D37) foi para a seção 12.2, sem cortes. A tabela de páginas
> abaixo está no estado de 26/10/2026 (D49); o resto da seção segue válido salvo onde marcado.

Retrato do que está no código hoje; as decisões que levaram a ele estão na seção 8 (D23–D25) e o relatório da revisão
em [REVISAO_2026-10-23.md](historico/REVISAO_2026-10-23.md) (54 testes, 89 verificações SQL, 6 extratos reconciliados).

**Fontes (D57, 27/10/2026: só gold, `gglobo-viu-dados-hdg-prd.gold_monday`, só leitura, em memória com recarga pelo
metadado).** Tabelas e views criadas e documentadas no PPD-GOLDEN-AGENCIAMENTO-MONDAY (ficha de cada uma em
`docs/tabelas/` de lá); as tabelas são atualizadas pelo job `gold-agenciamento` (seg–sex 09:00), as views refletem a base
na hora. Uma view não tem `modified` próprio: a recarga segue o da tabela de base (`gatilho` em `app/dados.py`).

| Gold | Tipo | Variável (`app/config.py`) · `dados.` | Grão | Usada em |
|---|---|---|---|---|
| `gld_agenciamento_2026_sla_movimentos` | tabela | `TAB_SLA` · `sla` | projeto × passo (com `sla_sem_almoco_horas`, R24) | SLA, estudo (slide 1), rodapé |
| `gld_agenciamento_2026_sla_entregas` | view | `TAB_SLA_ENTREGAS` · `sla_entregas` | orçamento entregue | SLA e estudo (slides 1–5, 7, 8) |
| `gld_agenciamento_2026_sla_entregas_status` | view | `TAB_SLA_ENTREGAS_STATUS` · `sla_entregas_status` | orçamento × status | estudo (slide 6) |
| `gld_agenciamento_entrada_diaria` | tabela | `TAB_ENTRADA` · `entrada` | dia × grupo × tipo × família | Início, Atendimento, Talentos (total), gatilho da Previsão |
| `gld_agenciamento_fluxo_mensal` | tabela | `TAB_FLUXO` · `fluxo` | safra × evento × mês do evento × grupo × tipo × família | Atendimento (A11), conferência de carga do Início, cobertura do estudo |
| `gld_agenciamento_fila_mensal` | view | `TAB_FILA` · `fila` | mês × safra | Início (extrato do mês, E7) |
| `gld_agenciamento_atendimento_mensal` | view | `TAB_ATENDIMENTO` · `atendimento` | mês | Atendimento (A13: faixa do ano, quadro, dispersão) |
| `gld_agenciamento_2026_saidas_status` | tabela | `TAB_SAIDAS_STATUS` · `saidas_status` | mês × status | Atendimento (A26/A27: dica de status e externos) |
| `gld_agenciamento_2026_talentos_ano` | tabela | `TAB_TALENTOS_ANO` · `talentos` | ano × categoria | Talentos (frase e barra) |
| `gld_agenciamento_2026_talentos_ranking` | tabela | `TAB_TALENTOS_RANKING` · `talentos_top` | grupo × talento × mês | Talentos (top 10, mapa, corrida) |
| `gld_agenciamento_previsao_mensal` | view | `TAB_PREVISAO_MENSAL` (ML) | mês × tipo | Previsão: séries S1 Inbound e S2 Mercado (`ml/dados.py`) |
| `gld_agenciamento_2026_previsao_exclusividade_mensal` | view | `TAB_EXCLUSIVIDADE_MENSAL` (ML) | mês × tipo | Previsão: S3/S4 Mercado exclusivos e não exclusivos |
| `gld_agenciamento_2026_previsao_lotes` | tabela | `TAB_LOTES` (ML) | dia × recorte | Previsão: diagnóstico de lotes do mês (S6) |

Não lidas pelo site (servem a outros consumidores e às views acima): `gld_agenciamento_2026_previsao_exclusividade_diaria`
(base da view mensal) e as views `..._previsao_exclusividade_mensal_inbound` / `_mercado`. **Única leitura fora da gold:**
a sensibilidade S5 do ML (`slv_agenciamento_2025_itens`, `TAB_SILVER_2025`), fonte fraca que não vai à tela; a silver
2025 não tem gold.

**Página × gráfico × tabela (D57)**

| Página | Gráfico ou bloco | Gold |
|---|---|---|
| Início | número do ano, gráfico mensal por tipo, tabela "Tipo de input", dica do mês (4 situações, ano anterior) | `entrada_diaria` |
| Início | extrato do mês (fila: represados, novos, entregues, sem entrega, seguem; dicas por mês de entrada) | `fila_mensal` (+ `fluxo_mensal` só para conferir a mesma carga) |
| Talentos | frase, barra 100% e legenda | `2026_talentos_ano` (+ `entrada_diaria`: total do Início, T5) |
| Talentos | top 10, mapa de calor por mês, corrida | `2026_talentos_ranking` |
| Atendimento | faixa do ano, quadro mês a mês (veio, entrou, para atender, entregues, sem entrega, ficou), dispersão | `atendimento_mensal` (respondidos e fila) + `entrada_diaria` (entradas, grupos, ano anterior) + `fluxo_mensal` (A11) |
| Atendimento | dica de status das saídas sem entrega, externos e "dependia da equipe" (A26/A27) | `2026_saidas_status` |
| SLA | frase do típico, dias úteis, cartão "prontos em até 2 dias" por mês, meta | `2026_sla_entregas` |
| Como medimos | slide 1 (exemplo real: passos e horas) | `2026_sla_movimentos` (R24) + `2026_sla_entregas` (dias úteis); cobertura: `fluxo_mensal` |
| Como medimos | slides 2, 3, 4, 5, 7 e 8 | `2026_sla_entregas` |
| Como medimos | slide 6 (onde o tempo trava) | `2026_sla_entregas_status` |
| Previsão | os dois gráficos e os cartões (a tela lê `ml/saida/previsao.json`) | o job de ML lê `previsao_mensal`, `2026_previsao_exclusividade_mensal` e `2026_previsao_lotes`; a carga nova da `entrada_diaria` dispara o job |
| Qualidade, Resultado, O que falta | sem dados (máscara); rodapé datado | `sla_movimentos`, `entrada_diaria`, `fluxo_mensal` |

**Páginas** (ordem da reunião, D30)

| Endereço | O que mostra hoje |
|---|---|
| `/viu-agenciamento` | **Entregue (D28).** Título "Quantos pedidos de orçamento chegaram ao longo de AAAA até o momento?" (ano fechado: "…em AAAA?"); sempre o ano da carga, sem seletor (D26); número do ano com período ("pedidos até 22 de outubro", E4), selo da variação e barras do mesmo período do ano anterior (E8, E8b); tabela "Tipo de input" com pedidos e % (maior resto) nos dois anos, Var. com base mínima 30 e total (E9, E8c); gráfico mensal empilhado por tipo; dica do mês com as 4 situações e o mesmo mês do ano anterior. Clique num dos **6 meses mais recentes com pedidos** abre o extrato = **fila do mês** (represados do início + novos = demanda = entregues dos novos/dos represados + saíram sem entrega + seguem represados; só pedidos do ano), com dicas por mês de entrada e novos por tipo. Entrada e fluxo de dias de carga diferentes, ou novos ≠ coluna: extrato escondido com aviso (E7). Ficha: `docs/paginas/inicio.md` |
| `/viu-agenciamento/atendimento` | **Entregue (D33, 24/10/2026).** "A equipe está dando conta da demanda?": faixa marinho escura com Recebidos em 2026 (5.520) → Resolvidos (5.360, 97% arredondado para baixo) → Em andamento (160, 3%), data de corte "Até 22 de outubro" em letra vazada e régua 100% (4.388 entregues ao cliente, 972 saíram sem entrega, 160 em andamento; legenda centralizada); bloco branco flutuante com dois painéis: "Quanto entrou, quanto resolvemos e quanto ficou" (quadro em 7 linhas, A24) e "Quanto resolvemos do que havia para atender, em cada mês" (dispersão sobre a demanda total, equilíbrio 100% e corte 90%, A16). % do mês = resolvidos ÷ para atender (A25). Coreografia de entrada, desligada com menos movimento. Regras A13, A15, A16, A24, A25 (as demais calculadas e não exibidas). Ficha: `docs/paginas/atendimento.md` |
| `/viu-agenciamento/talentos` | **Entregue (D31, 24/10/2026; base D30-b).** "Como a demanda se divide entre talentos exclusivos e não exclusivos?": "X% da demanda do ano se concentra nos talentos [grupo]." (grupo maior calculado; até 50%, "vai para os talentos [grupo]"); barra 100% "Distribuição dos pedidos por vínculo do talento" com % e quantidade dentro de cada parte (Talento não informado com largura mínima legível); legenda de uma linha com cor e nome dos três grupos (sem números); as dicas do **top 10** abrem pelas legendas de Exclusivos e de Não exclusivos (pedidos e "Último"; fecha com "Juntos, N pedidos: X% do grupo"); lista oculta para leitor de tela; aviso de conciliação só se o total diferir do Início. Sem mês, sem 2025, sem etiqueta de período, sem "Aguardando dados". Regras T1–T6. Ficha: `docs/paginas/talentos.md` |
| `/viu-agenciamento/sla` (aba "SLA", título "SLA de entrega"; antes "Prazo") | **Pronta · meta a oficializar (D34–D38, D49).** "Quanto tempo levamos para entregar um orçamento?"; seletor de talentos; "Levamos X h de trabalho da equipe … para entregar um orçamento ao cliente." (típico: 14 / 12 / 20 h na carga de 26/10) + "N dias úteis no calendário para o cliente receber" (C3b: 2 / 1 / 2; dias corridos entre parênteses); cartão "Orçamentos prontos em até 2 dias de trabalho, por mês" com trilhos (até 1 dia, 1 a 2 dias; vazio = acima de 2 dias), legenda do ano (31/25/44), "44% passam de 2 dias de trabalho", linha "meta sugerida: metade em até 2 dias de trabalho (16 h)", mês vigente vazado e típico do mês sob cada coluna (`_h_meta`); lupa para o estudo. Ficha: `docs/paginas/sla.md` ("Estado vigente") |
| `/viu-agenciamento/sla/como-medimos` | **Estudo em 8 slides (D34–D46; textos e navegação D49).** 1 exemplo real do dia (E1–E3, C3b); 2 formato, sino e faixas (X1–X7, `?passo=1\|2\|3`); 3 de cada 100 pedidos (W1–W7); 4 para onde vai o tempo (V1–V8); 5 mês a mês (U1–U9); 6 onde o tempo trava (K1–K8); 7 por tipo de input (J1–J9); 8 o que os dados mostraram (Z1–Z8), com "Voltar ao SLA". `?talentos=` em todos; `?exemplo=<projeto_id>` só em DEV ou apresentação. Só existe no SLA (outras seções: 404) |
| `/viu-agenciamento/<seção>/regras` | **Retirada (batalha 2, 26/10/2026):** 301 para `/sla/como-medimos#1` (SLA) ou para a própria seção, com o mesmo filtro; as regras ficam nas fichas |
| `/viu-agenciamento/previsao` | **Pronta · 2 decisões abertas (D47, D48, D49, D56).** D56: uma série e um modelo por recorte (Inbound, Mercado, Mercado exclusivos, Mercado não exclusivos; 61 modelos × 4 séries, R7 nas séries só de 2026). Em cada coluna, cartões do mês vigente + 2 seguintes (a partir da carga; vigente com realizado, previsão de fechamento e situação) e o gráfico de 2026 num cartão flutuante com o modelo e o erro; selo "não robusto" (Mercado) ou "confiança menor" (exclusividade); botão "Modelos comparados" abre um `<dialog>` nativo com todos os modelos. Inbound não exclusivo = "Não se aplica". Só lê `ml/saida/previsao.json` (contrato v3). Ficha: `docs/paginas/previsao.md` |
| `/viu-agenciamento/negocios-fechados` (rótulo "Resultado"), `/qualidade` | **Máscara** (D30): pergunta, motivo e pendências; Resultado fora do modo apresentação (`na_reuniao=False`); Qualidade com texto para o público e rodapé datado (D49). Ficha: `docs/paginas/demais.md` |
| `/viu-agenciamento/o-que-falta` | **Pronta (D30; G2-4).** Slide 1: estado de cada seção (ícone + texto, com as notas "meta a oficializar" e "2 decisões abertas") e os 4 pedidos de decisão; slide 2: as 20 pendências (PD01–PD23). Link no fim da última seção e no menu; não é aba. Ficha: `docs/paginas/o_que_falta.md`, conferida contra `pendencias.py` por `tests/test_documentacao.py` |

**Comportamento da carga (`app/dados.py`)**
- Local: conferência do metadado e recarga em segundo plano (resposta imediata). **Produção (`K_SERVICE`): na própria requisição**, porque o Cloud Run sem requisição não garante trabalho de fundo.
- Contrato ampliado: colunas, chave única, não vazia, `_processado_em` único, histórico do SLA contínuo e começando em Entrada, contagens inteiras e não negativas, situações somando as entradas. Carga inválida é recusada e a anterior continua no ar; sem carga anterior, a próxima tentativa só depois de `RECARGA_MIN`.
- Mês parcial e "até D de mês" vêm da data da carga (`_processado_em` em São Paulo, cobertura até a véspera), não do último dia com pedido.

**Cálculos**
- Horas úteis sem almoço: **da gold desde a D57** (`sla_sem_almoco_horas`, R24, em microssegundos sem arredondar; view `gld_agenciamento_2026_sla_entregas`). `app/expediente.py` ficou só com o calendário de feriados (R14) e o expediente, usados no ritmo do Atendimento, na previsão e na conferência independente do estudo; a conta antiga, para os testes, está em `tests/gold_simulada.py`.
- Regras da página inicial: E0–E9 em `app/apresentacoes/gestao_orcamentos/entrada/calculos.py`; aba Atendimento: A1–A25 em `atendimento/calculos.py` (na tela: A13, A15, A16, A24, A25; seção 9.5); teste de duas proporções em `app/estatistica.py`. Memória de cálculo na seção 9.2.
- Talentos: T1–T6 em `talentos/calculos.py` (`divisao()`, `top_por_grupo()`) sobre as golds `gld_agenciamento_2026_talentos_ano` e `..._talentos_ranking` (até 26/10, `app/sql/talentos_*.sql` na silver, hoje em `_descartados/2026-10-27/`); montagem em `apresentacao.py` (`montar_talentos`); estilo nos blocos "Talentos (D30)" e "T6" de `estilo.css` (seção 9.4). Prazo: C12–C14 e `leituras()` em `sla/calculos.py`; faixas de pedidos do slide 2 = C8 nas duas primeiras + maior resto nas três de cima (seção 9.1).

**Portal (D30)**
- `app/apresentacoes/__init__.py`: `Secao.pergunta`, `estado`, `na_reuniao`; `Apresentacao.visiveis()` (menu, abas, barra do celular e rotas passam por ela; seção oculta = 404), `vizinhas()` (anterior/próxima: Início → seções visíveis → "O que falta"), `pendencias`, `pedidos`, `pergunta_inicio`.
- `app/config.py`: `MODO=apresentacao` e `SECOES_VISIVEIS` (lista separada por vírgula); `GOLD_DATASET` e uma variável `TAB_*` por tabela ou view da gold (D57; `TAB_TALENTO_ORIGEM` e `TAB_LOG_ORIGEM` saíram).
- `gestao_orcamentos/pendencias.py`: `PENDENCIAS` (20 códigos entre PD01 e PD23, em 26/10/2026) e `PEDIDOS`; `Secao.nota_estado` ("meta a oficializar", "2 decisões abertas"); macros `pendente` e `lamina_pendente` em `templates/macros.html`; página `templates/o_que_falta.html`. Testes em `tests/test_portal.py`.

**Ferramentas e documentos**
- Ferramentas ativas: `tools/checar_reuniao.py`, `tools/conferir_estudo.py`, `tools/auditar_modelos.py` e `node tools/conferir_layout.mjs`. Saíram em 27/10/2026 (D57) para `_descartados/2026-10-27/tools/`, porque conferiam a silver, a classe `Consulta`, o expediente recalculado no site ou o plano de golds já executado: `auditar_relatorio.py` (resultados antigos em `docs/historico/validacao_2026-10-23.json`, telas em `docs/historico/evidencias/`), `auditar_paginas.py`, `conferir_expediente.py`, `preparar_gold_relatorio.py`, `validar_selects_gold.py` e `inventariar_auditoria.py`. Registros de revisões e auditorias externas em `docs/historico/`.
- `tools/conferir_entrega.py` foi aposentado em 26/10/2026 (regra antiga, com almoço) e movido para `_descartados/2026-10-26/tools/`; no lugar, `tools/checar_reuniao.py` (passo único antes da reunião; grava `docs/validacao/reuniao_AAAA-MM-DD.json`) e `tools/conferir_estudo.py` (grava `docs/validacao/estudo_AAAA-MM-DD.json`).

**Desalinhamentos conhecidos (a limpar)**
1. ~~Parâmetro `ver`, `VISOES` e comentários "situação (padrão)"~~: removidos em 23/10 com a D26.
2. ~~Comentário "em branco" em `regras.html`~~: corrigido em 23/10.
3. A data de entrada usada é a criação do card (com correção do cadastro retroativo). Relatórios de outras áreas usam o campo `data_de_entrada` e excluem declinados (ex.: out/26 = ~408 contra 508). Decisão em aberto: Q7.
4. ~~Talentos entregue (D31), mas o código ainda marca a seção como `estado="parcial"`~~ (resolvido: `estado="pronta"` em 26/10/2026; o resto do item fica como registro). Texto original: em `apresentacao.py`: a página
   "O que falta" continua mostrando "Parcial" até o Caio decidir se troca para "pronta" (a exceção D30-b e PD01–PD03
   seguem abertas). Na mesma seção, `tabelas=("entrada", "talentos")` não inclui `talentos_top` (só afeta o cartão de
   status; a origem é a mesma silver). Na ficha `o_que_falta.md`, o texto de PD02a está
   diferente do de `pendencias.py` ("Ranking dos exclusivos lido da gold (hoje a dica lê a silver)") — resolvido em 26/10/2026: a ficha foi regenerada do código e é conferida por `tests/test_documentacao.py`.

## Módulos do portal, página por página

Uma página = um módulo, sempre nas mesmas subseções: **(a)** pergunta(s) que a página responde; **(b)** resposta de
hoje, com os números e a data da carga; **(c)** por que respondemos assim (decisões, com número e data); **(d)** regras,
com os códigos do código; **(e)** base consultada (tabelas com nome completo e colunas); **(f)** SQL principal, que
refaz os números direto no banco; **(g)** resultados obtidos (valor e data); **(h)** como a página se atualiza com a
carga; **(i)** pendências e perguntas abertas. O detalhe longo (todos os textos da tela, memória completa, demais SQL,
validações e histórico) fica na ficha de cada página em [docs/paginas/](paginas/README.md); o módulo aponta para ela.

**Regra do Caio (24/10/2026): cada número da tela se confere no BigQuery, não na apresentação.** Toda regra nova de
cálculo entra primeiro no módulo e na ficha, com SQL e resultado, antes de ir à tela.

**Carga de referência de todos os módulos:** gold processada em **23/10/2026** (SLA 20:23:42 UTC; entrada 20:23:49;
fluxo 20:24:38; silver 11:05 UTC), dados até **22/10/2026**. Conferida no BigQuery em 24 e 25/10/2026 (conta
`caio.barroso@viu.com.br`, projeto `gglobo-viu-dados-hdg-prd`, só SELECT). Todas as SQL abaixo são somente leitura.

| Módulo | Endereço | Estado | Ficha |
|---|---|---|---|
| [M1. Início](#m1-início) | `/viu-agenciamento` | entregue (D28; ajustes D36; disposição em dois quadrantes D52) | [inicio.md](paginas/inicio.md) |
| [M2. Talentos](#m2-talentos) | `/viu-agenciamento/talentos` | entregue (D31; ajustes D36; seletor e mapa mês a mês D50; contagem e corrida no play D51) | [talentos.md](paginas/talentos.md) |
| [M3. Atendimento](#m3-atendimento) | `/viu-agenciamento/atendimento` | entregue (D33; ajustes D36) | [atendimento.md](paginas/atendimento.md) |
| [M4. SLA de entrega e estudo "Como medimos"](#m4-sla-de-entrega-e-estudo-como-medimos) | `/viu-agenciamento/sla`, `/viu-agenciamento/sla/como-medimos` | em construção com o Caio (D34, D35, D37–D44; estudo com 8 slides) | [sla.md](paginas/sla.md) (seção 0 vale sobre o resto) |
| [M5. Previsão de demanda](#m5-previsão-de-demanda) | `/viu-agenciamento/previsao` | acompanhamento mensal (D48); job de produção a fazer | [previsao.md](paginas/previsao.md) |
| [M6. Resultado: negócios fechados](#m6-resultado-negócios-fechados) | `/viu-agenciamento/negocios-fechados` | máscara; outra base, a conversar | [demais.md](paginas/demais.md) |
| [M7. Qualidade dos dados](#m7-qualidade-dos-dados) | `/viu-agenciamento/qualidade` | máscara; a conversar | [demais.md](paginas/demais.md) |

A página "O que falta" (`/viu-agenciamento/o-que-falta`) não é módulo de análise: é gerada de `pendencias.py`
(ficha [o_que_falta.md](paginas/o_que_falta.md)) e fecha a ordem da reunião.

### M1. Início

**(a) Pergunta.** "Quantos pedidos de orçamento chegaram ao longo de 2026 até o momento?" (ano fechado: "…chegaram em
AAAA?"). O leitor sai sabendo, nesta ordem: quantos pedidos chegaram no ano; se é mais ou menos que no mesmo período do
ano anterior; de onde vieram (tipo de input) e como cada origem mudou; como foi cada mês e, nos 6 meses mais recentes
com pedidos, o extrato da fila do mês.

**(b) Resposta de hoje (carga de 23/10, dados até 22/10).** **5.520 pedidos** de 01/01 a 22/10/2026, **▲ 91% a mais**
que no mesmo período de 2025 (2.890; o ano inteiro de 2025 teve 3.586). Mercado 2.945 (53%, ▲ 160%), Inbound 1.322
(24%, ▲ 38%), Internos 769 (14%, ▲ 133%), Proativo 407 (7%, ▼ 13%, único que caiu), Sem tipo 77 (2%; 2025 = 3, `<1%`,
"–"). Julho foi o maior mês (765); outubro, parcial, 508 até o dia 22 (+71% sobre 1–22/10/2025). Extrato de outubro:
173 represados + 508 novos = 681 → 419 entregues (286 dos novos, 133 dos represados) + 102 saíram sem entrega + 160
represados hoje.

**(c) Por que respondemos assim.** D23 (22/10: a área começa pelo volume real por tipo); D25 (23/10: uma leitura só,
tipo de input, mais o extrato); D26 (23/10: sempre o ano corrente, comparação só com o mesmo período do ano anterior —
a cor azul da variação foi revista pela D36); D27 (23/10: proporção ao lado da quantidade); D28 (23/10: entregue após
validação em três camadas, 624 itens, 0 divergências); D29 (23/10: janeiro sem represados, sem extratos do ano
anterior, estimadas de 2025 só na documentação); D32 (24/10: data de entrega = 1ª ida a "Aguardando Feedback"); **D36
(25/10)**, decisões 1–5: gráfico em cartão com título, "mesmo período: até 22/out" sob as barras, seta pastel ▲/▼ na
coluna Var., `<1%` com pedidos, divergência em safra antiga só no log.

**(d) Regras (`entrada/calculos.py`).** E0 ano mostrado = ano da véspera do `_processado_em`; E1 pedidos = `quantidade` +
`quantidade_estimada`; E2 grupos de input (Mercado, Inbound, Proativo, Internos, Sem tipo); E3 fim = véspera da carga em
São Paulo; E4 texto do período; E5 composição de Internos; E6 situação do mês; E7 extrato = fila do mês (só pedidos do
ano; `nao_seguiu` sem mês vai ao mês de entrada; extrato escondido se entrada e fluxo forem de dias diferentes, B7);
E8/E8b comparação com o mesmo período e variação só com base ≥ 30; E8c parcelas pelo maior resto; E9 composição contra
o ano anterior. Detalhe: ficha, seção 4.

**(e) Base.** `gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_entrada_diaria` (`TAB_ENTRADA`; dia × grupo ×
tipo × família): `data`, `quantidade`, `quantidade_estimada`, `grupo_input`, `tipo_de_input`, `entregue_no_mes`,
`entregue_depois`, `nao_seguiu`, `em_andamento`, `_processado_em`. `gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_fluxo_mensal`
(`TAB_FLUXO`; safra × evento × mês do evento): `mes_entrada`, `evento`, `mes_evento`, `quantidade`, `_processado_em`.

**(f) SQL principal** (número, comparação e tipos; extrato, mês a mês e silver na ficha, seções 6.2–6.4):

```sql
-- Número e comparação (E1, E8). Trocar as datas pela véspera do _processado_em e o mesmo dia do ano anterior
SELECT ano, SUM(quantidade) AS reais, SUM(quantidade_estimada) AS estimadas,
       SUM(quantidade + quantidade_estimada) AS pedidos
FROM `gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_entrada_diaria`
WHERE (ano = 2026 AND data <= '2026-10-22') OR (ano = 2025 AND data <= '2025-10-22')
GROUP BY ano ORDER BY ano;

-- Tabela por tipo (E9)
SELECT IF(grupo_input IN ('Mercado','Inbound','Proativo','Internos'), grupo_input, 'Sem tipo') AS grupo, ano,
       SUM(quantidade + quantidade_estimada) AS pedidos
FROM `gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_entrada_diaria`
WHERE (ano = 2026 AND data <= '2026-10-22') OR (ano = 2025 AND data <= '2025-10-22')
GROUP BY 1, 2 ORDER BY 1, 2;
```

**(g) Resultados.** 25/10/2026, carga de 23/10: 2026 = 5.520 (5.515 reais + 5 estimadas); 2025 = 2.890 (445 estimadas)
→ +91%; tipos 2.945 / 1.322 / 407 / 769 / 77 × 1.134 / 955 / 468 / 330 / 3; situação do ano 3.710 + 678 entregues, 972
sem entrega, 160 em andamento. Igual à tela. Sensibilidade: só com datas reais de 2025, +126% (ficha 8.1, Q11).

**(h) Atualização com a carga.** Nada fixo no código: ano, "até 22 de outubro", mês parcial e janela dos 6 extratos
saem do `_processado_em` da carga em memória. A página só mostra o extrato quando entrada e fluxo são do mesmo dia de
carga e a safra do ano exibido concilia; se não, aviso "O extrato está sendo atualizado…". **Checagem diária:** Q1
(sanidade) e Q2 (fila) da ficha, seção 6.4, a cada carga, antes de apresentar.

**(i) Pendências e perguntas.** Q7 (data de entrada: criação do card ou `data_de_entrada`), Q10 ("Sem tipo"), Q11
(15% de 2025 com data estimada), P4 (nota de dias úteis no mês parcial), P7–P9 (opcionais); achados F7–F10 levados à
gold (`docs/lembretes_gold.md`); fotografia de fim de mês (PD13).

### M2. Talentos

> **Vigente em 26/10/2026 (D50):** seletor Todos / Exclusivos / Não exclusivos; resposta por recorte (carga de 26/10,
> `@fim` 25/10): Todos "Da demanda do ano, **62%** vai para os talentos exclusivos." (3.451 de 5.556); Exclusivos
> "Dos pedidos de talentos exclusivos, **52%** vão para os 10 talentos mais pedidos." (1.808 de 3.451); Não exclusivos
> **11%** (225 de 1.980); barra do ano fina com o grupo destacado; mapa de calor dos 10 talentos mais pedidos × jan–dez
> (T10; `app/sql/talentos_top.sql`, uma linha por talento e mês; Todos = o mesmo top 10 dos exclusivos nesta carga).
> Regras T7–T10, números mês a mês, SQL e conferência no BigQuery: ficha `talentos.md`, seção 0. Os itens (b) e (g)
> abaixo são da carga de 23/10.

**(a) Pergunta.** "Como a demanda se divide entre talentos exclusivos e não exclusivos?" — de cada 100 pedidos de 2026,
quantos foram para exclusivos, não exclusivos e sem talento informado, sobre a mesma base do Início; e, em cada grupo,
quais talentos concentram a demanda (top 10) e como os pedidos deles se distribuem mês a mês (D50).

**(b) Resposta de hoje (carga de 23/10, fim 22/10).** "**62%** da demanda do ano se concentra nos talentos exclusivos."
Exclusivos 3.435 (62%), não exclusivos 1.955 (36%, inclui 119 do Squad de Talentos), talento não informado 130 (2%) =
**5.520 = Início**. Top 10 dos exclusivos: 1.802 pedidos (52% do grupo); top 10 dos não exclusivos: 221 (11%), com o
10º lugar empatado com mais 2 talentos.

**(c) Por que respondemos assim.** D30 (23/10: só a divisão anual de 2026, sem mês e sem 2025); D30-b (23/10: exceção
para ler a silver, porque a gold de entradas não tem a exclusividade e a gold do SLA cobre só 56% dos pedidos); D31
(24/10: entregue; resposta calculada, nomes de talentos nas dicas revendo a D30, top 10 com "Último"); **D36 (25/10)**,
decisões 10–12: bases divergentes mostram os números com aviso em vez de bloquear; nota de empate no fim do top 10;
talentos com dois vínculos e Squad só de exclusivos levados aos lembretes da gold. **D50 (26/10, pedido do gerente do
Caio):** seletor, resposta por recorte e mapa mês a mês (revisa a D31, que deixava a página sem visão mensal).

**(d) Regras (`talentos/calculos.py`, `app/sql/`).** T1 base = os mesmos pedidos do Início (regras R1, R2, R4, R5, R21
da gold); T2 exclusividade na data do pedido, sem talento = grupo próprio; T3 Squad de Talentos conta em não exclusivos e
fica fora do ranking; T4 parcelas pelo maior resto e frase ("se concentra" acima de 50%; senão "vai para"); T5
conciliação com o Início (diferença ≠ 0 → aviso, sem esconder os números); T6 top 10 por grupo (nome sem diferença de
maiúsculas e espaços, grafia mais frequente, `empate_fora`); D50: T7 seletor (`?talentos=`), T8 resposta por recorte
(Todos = % do maior grupo; grupo = soma do top 10 ÷ total do grupo), T9 barra com o grupo destacado, T10 mapa top 10 ×
jan–dez (mês da data de entrada; soma dos meses = total; meses futuros vazios; tom = `ceil(6 × n ÷ maior mês)`).

**(e) Base.** Exceção D30-b: `gglobo-viu-dados-hdg-prd.silver_monday.slv_agenciamento_2026_itens`
(`TAB_TALENTO_ORIGEM`): `state`, `criado_em`, `data_de_entrada`, `data_de_saida`, `exclusivo`, `talentos_exclusivos`,
`talento`. Para o `@fim` e a conciliação: `gold_monday.gld_agenciamento_entrada_diaria` (`data`, `quantidade`,
`quantidade_estimada`, `_processado_em`).

**(f) SQL principal.** O próprio arquivo do site, `app/sql/talentos_ano.sql`, trocando `{tabela_origem}` por
`gglobo-viu-dados-hdg-prd.silver_monday.slv_agenciamento_2026_itens` e `@fim` por `DATE '2026-10-22'` (o top 10 é
`app/sql/talentos_top.sql`, com as mesmas trocas). Antes, conferir o fim e o total do Início:

```sql
SELECT MAX(_processado_em) AS carga, MAX(data) AS ultimo_dia,
       SUM(quantidade + quantidade_estimada) AS pedidos_2026
FROM `gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_entrada_diaria`
WHERE data BETWEEN '2026-01-01' AND '2026-10-22';
-- esperado: 2026-10-23 20:23 UTC | 2026-10-22 | 5.520
```

**(g) Resultados.** 24 e 25/10/2026 (fim 22/10): `talentos_ano.sql` → Exclusivos 3.435 (62,2), Não exclusivos 1.955
(35,4; 119 do Squad), Sem talento 130 (2,4); total 5.520 = gold de entradas, também mês a mês. Top 10: 281 … 120 =
1.802 (52%); 65 … 12 = 221 (11%), `empate_fora` 0 e 2. Memória completa: ficha, seção 5.

**(h) Atualização com a carga.** `Consulta` em `app/dados.py`: o `@fim` vem de `_fim_da_entrada()` (véspera do
`_processado_em` da gold de entradas, mesma regra E3 do Início) e a consulta é refeita quando muda o metadado da silver
ou o fim. Se a silver e a gold estiverem em horários diferentes e o total não bater, a tela mostra os números com o
aviso de atualização (T5).

**(i) Pendências.** PD01 (exclusividade na gold de entradas; encerra a D30-b), PD02a (ranking dos exclusivos pela gold),
PD02b (cadastro limpo dos não exclusivos), PD03 (exclusivos de 2025 com vigência), PD20 (continuidade na virada do ano).
Pergunta aberta: trocar o `estado` da seção para "pronta" (hoje "parcial" no código).

### M3. Atendimento

> **D53 (26/10/2026) — vigente:** pergunta de **capacidade**; resolvido = entregue ao cliente; % do mês = entregues ÷
> (para atender − saídas por decisão externa); topo 4.415 de 5.556 recebidos, **82% do que dependia da equipe**; meses
> 65–75%. Regras A15b, A24b, A26–A28 e números na ficha `atendimento.md`, seção 0. O texto abaixo é o estado de 24–25/10.

**(a) Pergunta.** "A equipe está dando conta da demanda?" — quanto entrou no ano e em cada mês, quanto foi resolvido
(entregue ao cliente ou encerrado sem entrega), quanto ficou represado e, de tudo o que havia para atender em cada mês,
que parte foi resolvida contra o objetivo de 100% (corte de 90%).

**(b) Resposta de hoje (carga de 23/10, dados até 22/10).** Recebidos em 2026 **5.520** → Resolvidos **5.360 (97%)** →
Em andamento **160 (3%)**; régua 4.388 entregues ao cliente, 972 saíram sem entrega, 160 em andamento. % do que havia
para atender, jan–out: 77, 80, 76, 78, 81, 80, 87, 87, 79, 77 (out parcial): **os 10 meses abaixo de 90%** — a equipe
não resolve toda a demanda do mês; sempre sobra represado.

**(c) Por que respondemos assim.** D27 (23/10: aba criada; proporção ao lado da quantidade); D29 (janeiro sem
represados); D32 (24/10: data de entrega pelo log); D33 (24/10: entregue; A25 = % sobre o que havia para atender, que
nunca passa de 100%; objetivo 100%/90% na tela e XmR só no código); **D36 (25/10)**, decisões 6–9: linha "− Entregues ao
cliente" e "Resolvemos do que havia para atender"; bloco branco no mesmo cartão do SLA (`--cartao-*`); saldo/frase e
zona "▲ resolvemos a mais" só como sugestão; virada do ano mantida e documentada.

**(d) Regras (`atendimento/calculos.py`).** Na tela: A3 entradas (= E1); A13 resolvidos = `entregue` + `nao_seguiu` pelo
`mes_evento`, só pedidos do ano (`nao_seguiu` sem mês → mês de entrada, E7); A15 números do ano (% resolvido arredondado
para baixo); A16 dispersão; A24 quadro em 7 linhas; A25 % do mês = (entregues + encerrados sem entrega) ÷ para atender.
Calculadas e não exibidas: A1–A12, A14, A17–A23 e a média/limite XmR. Detalhe: seção 9.5 e ficha, seção 4.

**(e) Base.** `gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_entrada_diaria`: `data`, `quantidade`,
`quantidade_estimada` (+ `entregue_no_mes`, `entregue_depois`, `nao_seguiu`, `em_andamento` na conferência).
`gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_fluxo_mensal`: `mes_entrada`, `evento`, `mes_evento`,
`quantidade`, `_processado_em`.

**(f) SQL principal** (quadro completo; conferência pela situação e pelas cargas na ficha, seção 6):

```sql
WITH ent AS (
  SELECT DATE_TRUNC(data, MONTH) AS mes, SUM(quantidade + quantidade_estimada) AS entrou
  FROM `gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_entrada_diaria`
  WHERE data BETWEEN '2026-01-01' AND '2026-10-22' GROUP BY 1),
res AS (
  SELECT DATE_TRUNC(CAST(COALESCE(mes_evento, mes_entrada) AS DATE), MONTH) AS mes,  -- E7: sem mês, vai para a entrada
    SUM(quantidade) AS resolvemos,
    SUM(IF(evento = 'entregue', quantidade, 0)) AS entregues,
    SUM(IF(evento = 'nao_seguiu', quantidade, 0)) AS sem_entrega,
    SUM(IF(evento = 'nao_seguiu' AND mes_evento IS NULL, quantidade, 0)) AS sem_data
  FROM `gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_fluxo_mensal`
  WHERE EXTRACT(YEAR FROM CAST(mes_entrada AS DATE)) = 2026 AND evento IN ('entregue', 'nao_seguiu')
    AND CAST(COALESCE(mes_evento, mes_entrada) AS DATE) <= DATE_TRUNC(DATE '2026-10-22', MONTH)
  GROUP BY 1),
q AS (
  SELECT e.mes, e.entrou, COALESCE(r.resolvemos, 0) AS resolvemos, COALESCE(r.entregues, 0) AS entregues,
    COALESCE(r.sem_entrega, 0) AS sem_entrega, COALESCE(r.sem_data, 0) AS sem_data,
    SUM(e.entrou - COALESCE(r.resolvemos, 0)) OVER (ORDER BY e.mes) AS ficou
  FROM ent e LEFT JOIN res r USING (mes))
SELECT FORMAT_DATE('%Y-%m', mes) AS mes, entrou, entregues, sem_entrega, resolvemos, sem_data, ficou,
  COALESCE(LAG(ficou) OVER (ORDER BY mes), 0) AS veio,
  COALESCE(LAG(ficou) OVER (ORDER BY mes), 0) + entrou AS para_atender,
  CAST(FLOOR(100 * resolvemos / (COALESCE(LAG(ficou) OVER (ORDER BY mes), 0) + entrou) + 0.5) AS INT64) AS pct_tela
FROM q ORDER BY mes;
```

**(g) Resultados.** 25/10/2026 (carga de 23/10), igual à tela: veio 0/87/85/137/134/148/141/118/101/173; entrou
374/341/485/472/629/569/765/644/733/508 (5.520); entregues 4.388; sem entrega 972 (10 sem data, só em outubro);
ficou 87/85/137/134/148/141/118/101/173/160; `pct_tela` 77/80/76/78/81/80/87/87/79/77. Conferência pela situação da
safra: 3.710 + 678 = 4.388, 972, 160 = em andamento do Início. Referência não exibida: média 80,53%, limite XmR 71,60%.

**(h) Atualização com a carga.** As duas tabelas precisam ser do mesmo dia de carga (`_mesma_fotografia`); se não forem,
a página avisa em vez de misturar fotografias. Mês parcial, "dados até" e o 3º mês mínimo para a dispersão saem da carga
em memória; nada é fixo no código.

**(i) Pendências.** PD07 (motivo de quem saiu sem entrega), PD08 (regra de entrega sem histórico de status; F9), PD19
(data das saídas e identificação da carga), PD13 (foto de fim de mês: hoje a fila é reconstruída com a situação de
hoje); lembretes da gold, itens 12 e 14. Sugestões em aberto (D36, decisão 8): saldo/frase de resposta e zona
"resolvemos a mais".

### M4. SLA de entrega e estudo "Como medimos"

> **Vigente em 26/10/2026 (D38 + batalha D49):** meta sugerida = metade dos orçamentos em até 2 dias de trabalho (16 h); faixas até 1 dia / 1 a 2 dias / acima de 2 dias; mês da 1ª entrega; prazo do cliente em dias úteis no calendário (C3b); "típico" na tela; selo do mês com 1 casa entre 15,5 e 16,5 h; limite do padrão no slide 2 pela regra linear (59 h na carga de 26/10). Números da carga de 26/10 (2.347 · 14 h · 2 dias úteis · 31/25/44; exclusivos 1.609 · 12 h · 1; não exclusivos 725 · 20 h · 2) e cada elemento da tela com função e SQL: ficha `sla.md`, "Estado vigente". Os itens (b), (d) e (g) abaixo são da carga de 23/10 e da regra D37 onde não marcados.
> **D46 (25/10/2026, noite) — movimento do estudo** (`estilo.css`, bloco D46; `apresentacao.js`; `como_medimos.html` só com `<g>` e `pathLength`): um gesto de dado por slide, sem mudar números, textos ou regras. O que cada slide faz: ficha `sla.md`, seção 0000000000.1.

> **D44 (25/10/2026, noite) — slide 8 do estudo** (`#8`, `calculos.conclusao`, regras Z1–Z8): "O que os dados nos mostraram" — seis achados tirados dos dicts dos slides 2–7 já calculados em `montar_estudo_sla` (nenhum número próprio: mediana/média do universo, A e HB/B de `tempo_cem`, leitura e `resumo` de `meses_estudo`, os 2 maiores de `travas`, o tipo da faixa de `tipos_pedido`), cores por regra, onde olhar (perguntas por tipo de status) e "O que isso pede" (fixo). Mesma base e mesmas tabelas dos slides de origem. Resultados por grupo na ficha `sla.md`, seção 00000000.

> **D43 (25/10/2026, noite) — slide 7 do estudo** (`#7`, `calculos.tipos_pedido`, regras J1–J9): "Em que tipo de pedido o tempo trava?" — por `tipo_de_input` (gold `gld_agenciamento_2026_sla_movimentos`, passo 1; nenhum projeto com dois valores), mesmo universo dos slides 2–6; A = % em até 16 h (C8, igual aos slides 3/4), típico = mediana, onde mais trava = etapa (K2) com mais horas entre os pedidos do tipo acima de 16 h; vermelho = B ≥ B geral + 3 pontos. SQL e resultados por grupo na ficha `sla.md`, seção 0000000 (Todos: Mercado 1.266 · 55/45 · 15 h · Elaboração 43%; Inbound 637 · 57/43 · 14 h · Fila de entrada 42%; Proativo 128 · 33/67; Interna 74 · 32/68).

> **D42 (25/10/2026, noite) — slide 6 do estudo** (`#6`, `calculos.travas`, regras K1–K8): "Onde o tempo trava?" — por status da equipe antes da 1ª entrega (Entrada → Fila de entrada; "Em elaboração…" → Elaboração; "Em revisão…" → Revisão; Retorno Marca fora), tempo de cada orçamento no status (horas úteis sem almoço, passagens somadas; soma = `h_trabalho`), típico = mediana, limite = Q3 + 1,5 × IQR do status, travou = acima do limite, tempo travado = **tempo inteiro, no status, de quem travou** (decisão do Caio, 25/10/2026; antes o excesso), % pelo maior resto. Base = a dos slides 2–5. Tabela `gld_agenciamento_2026_sla_movimentos` (colunas `projeto_id`, `passo`, `status`, `fase`, `entrada`, `saida`, `exclusivo`). SQL, mapeamento status → etapa e resultados por grupo na ficha `sla.md`, seção 000000 (Todos: Em elaboração 41% · Fila de entrada 19% · Validação Talento 11% · Produção 9% · Orçamentos 9%… → "dois pontos", 60%). Atualiza a cada carga (nada fixo).

> **D41 (25/10/2026, noite) — slide 5 do estudo** (`#5`, `calculos.meses_estudo`, regras U1–U9): "Foi um mês ruim, ou é sempre assim?" — por mês da 1ª entrega (12 colunas; meses sem mês completo vazios), cada orçamento como ponto (horas da equipe em dias, escala de raiz quadrada), típico (mediana) e faixa da maioria (Q1–Q3), % que passa de 2 dias (h > 16 h, pela C8 da página) e pedidos. Leitura sazonal × padrão (U7): mês destoa se B > mediana dos B mensais + 10 pontos ou típico > mediana dos típicos + 4 h; 0 → padrão, 1–2 → picos, 3+ → sazonal. Base = a dos slides 2–4. Tabela `gld_agenciamento_2026_sla_movimentos` (colunas da ficha, seção 1.1). SQL e resultados por grupo e mês na ficha `sla.md`, seção 00000.4 (Todos: 111/108/159/215/201/288/548/378/340 pedidos, 40/45/42/50/51/51/43/41/41% → padrão; Exclusivos → padrão; Não exclusivos: abril, maio e agosto destoam → sazonal). Atualiza a cada carga (nada fixo).

> **D40 (25/10/2026, noite) — slide 4 do estudo** (`#4`, `calculos.tempo_cem`, regras V1–V8): "Para onde vai o tempo?" — de cada 100 pedidos e de cada 100 horas da equipe, quanto fica nos que saem em até 2 dias (A, HA) e nos que passam de 2 dias (B, HB). Base = a dos slides 2 e 3 (meses completos, grupo de talentos). Pedidos = os % do slide 3 (A = "% em até 2 dias" da página, C8); horas = soma de `h_trabalho` por faixa ÷ soma total, maior resto (somam 100), HA = 2 primeiras faixas, HB = 100 − HA. Frases dos cartões em frações por extenso (V8). Tabela `gld_agenciamento_2026_sla_movimentos` (colunas da ficha, seção 1.1). SQL e resultados por grupo na ficha `sla.md`, seção 0000.4 (Todos 56/16 · 44/84; Exclusivos 62/19 · 38/81; Não exclusivos 41/12 · 59/88). Atualiza a cada carga (nada fixo).

> **D39 (25/10/2026, noite) — slide 3 do estudo** (`#3`, `calculos.cem_pedidos`, regras W1–W7): "De cada 100 pedidos que chegam, em quanto tempo entregamos?" — waffle de 100 por faixa de tempo da equipe, chaves A (em até 2 dias) e B (passam de 2 dias), curva acumulada com os marcos de 2 dias (A%), 80% e 90% (quantis lineares, em dias de 8 h arredondados a meio dia). Base = a do slide 2 (meses completos, grupo de talentos). A = "% em até 2 dias" da página (C8); as três faixas de cima repartem B pelo maior resto. Tabela `gld_agenciamento_2026_sla_movimentos` (colunas da ficha, seção 1.1). SQL e resultados por grupo na ficha `sla.md`, seção 000.4 (Todos 56/44 · 31 h · 46 h; Exclusivos 62/38 · 28 h · 40 h; Não exclusivos 41/59 · 36 h · 57 h). Atualiza a cada carga (nada fixo).

> **D38 (25/10/2026, noite) prevalece onde houver conflito:** **SLA (D38, 25/10/2026, noite):** meta sugerida = **metade dos orçamentos em até 2 dias de trabalho (16 h)** (D-SLA-7, revisa a D-SLA-3: "75% em até 3 dias"); faixas até 1 dia / 1 a 2 dias / acima de 2 dias; linha em 50% "meta sugerida: 2 dias úteis"; mensagem do típico pela mediana exata (16,3 h fica fora); "N% passam de 5 dias de trabalho (M orçamentos)" sem meta. Estudo em % do total, "limite estatístico" (Tukey, não é a meta), "demorados"/"outliers", marca da meta no boxplot, Q-Q contando orçamentos reais acima do teto e uma frase por passo na faixa do pé só com números visíveis no gráfico. Todos 56% em até 16 h · 12% acima de 40 h; exclusivos 62 · 10; não exclusivos 41 · 16 (típico 20 h, 4 h acima). Ficha `sla.md`, seção 00. 170 testes. Onde abaixo se lê "até 3 dias", "75%" ou "fora da curva pelo boxplot em log", vale a D38.

**(a) Perguntas.** Página: "Quanto tempo levamos para entregar um orçamento?" — horas de trabalho da equipe até a 1ª
versão ao cliente, dias de calendário até o cliente receber, e quantos ficam prontos em até 2 dias de trabalho (D38; na D37, 3 dias), mês a
mês, por grupo de talento. Estudo, slide 1: "Como chegamos ao tempo da equipe?" (o cálculo num orçamento real). Slide
2: "A maioria é rápida. Poucos demoram muito." — qual o formato da distribuição, por que a mediana e o que é demorado
ou fora da curva. **Pergunta da diretoria** (exclusivos × intervenientes, outliers): respondida na ficha e aqui, não na
tela.

**(b) Resposta de hoje (carga de 23/10/2026 20:23:42 UTC; meses completos de entrega jan–set).** "Levamos **14 h** de
trabalho da equipe para entregar um orçamento ao cliente" e "**2,8 dias** no calendário para o cliente receber" (2.348
orçamentos); legenda do ano 31% até 1 dia · 25% 1 a 2 dias · 15% 2 a 3 dias · 29% acima de 3 dias (**71% em até 3
dias**, meta sugerida 75%: chegam jan e ago; set 74%). Exclusivos 1.610 · 12 h · 2,0 dias · 37/25/14/24 (76%); não
exclusivos 725 · 20 h · 4,0 dias · 18/23/20/39 (61%). Mediana por mês (Todos): jan 13, fev 16, mar 15, abr 16, mai 16,
jun 16, jul 13, ago 13, set 14 h; out 16 h (parcial, vazado, 242 entregas até 22/10). Estudo: exemplo do dia (25/10,
Todos) "[Bradesco] Vinicius Nascimento | Criança Esperança" — Entrada 1h09, Elaboração 8 min, Revisão 11h48 = 13h05; 2
dias para o cliente; 15 dias de decisão do cliente, em aberto; cobertura "Medido em 2.348 de 3.553 orçamentos entregues
no período (66%)". Slide 2 (Todos): metade do meio 1,7× mais larga do lado lento (8 h × 13 h; Q1 7 h, mediana 14 h, Q3
28 h); média 25 h, 73% abaixo dela; aderência 0,58 (sino) · 0,99 (log-normal), 32 em 100 teriam tempo negativo pelo
sino; limite do fora da curva 210 h (boxplot em log); zonas 25/50/24/1; 12 em 100 passam de 5 dias (40 h); 27 dos 28
fora da curva são cards de pacote. **Resposta à diretoria:** "Os dois grupos têm o mesmo formato; os não exclusivos
levam mais tempo no geral (16 em 100 passam de 5 dias, contra 10 nos exclusivos); os casos extremos são raros (1 em 100)
e quase todos são cards de pacote (21 de 21 nos exclusivos; 8 de 9 nos não exclusivos)."

**(c) Por que respondemos assim.** D16 (construção slide a slide com o Caio); C1–C10 (21/10: entrega = 1ª ida a
"Aguardando Feedback"; Entrada conta; sem almoço; dia útil = 8 h; mediana por grupo); D30 (23/10: cauda e exclusivos ×
não exclusivos, pedidos da diretoria); D34 (24/10: página única, resposta tipográfica, estudo "Como medimos" com o
exemplo real, E1–E3); D35 (24/10: slide 2, X1–X7; avaliação estatística mostrou cauda de pacotes e formato
log-normal); **D37 (25/10)**: D-SLA-1 mês da 1ª entrega (o mês parcial deixa de ser otimista e fecha no dia 1º, como o
Atendimento); D-SLA-2 sem "Retorno Marca/Executivo" (espera da marca, não trabalho da equipe); D-SLA-3 meta sugerida 75%
em até 3 dias (nenhum mês fechado chegava a 75% em 2 dias; em 3 dias os melhores meses chegam — atingível com melhoria);
D-SLA-4 cobertura à vista; D-SLA-5 pendências à gold (PD21); D-SLA-6 rejeitadas (tirar a fila, as Cotações ou os
pacotes; encerrados sem entrega no denominador); slide 2 em escala log porque os tempos são log-normais (a cerca linear
marcava 7% pelo formato da cauda).

**(d) Regras vigentes (`sla/calculos.py`; ficha 0.4).** C1 pronto = 1ª chegada em Aguardando Feedback (fase `cliente`);
C2 horas úteis sem almoço (seg–sex 10h–13h e 14h–19h, feriados) dos passos `equipe` antes de C1, com Entrada, Cotações
e validações, **sem Retorno Marca**; C3 calendário = horas corridas de C1 − passo 1, ÷ 24; C4 só entregues, **mês = mês
da 1ª entrega**; C5 faixas ≤ 8, 8–16, > 16 h (D38; na D37, ≤ 8, 8–16, 16–24, > 24 h); C6 meta sugerida metade em até 16 h (D38; na D37, 75% em até 24 h); C3b dias úteis no calendário na tela; C7 contas só com meses completos
de entrega, parcial vazado só no gráfico (< 30 entregas: "aguardando entregas"); C8 ≤ 8, ≤ 16, ≤ 24 arredondados
direto, faixas do meio por diferença; C10 grupos pela coluna `exclusivo` (NULL só em Todos); C11–C14 calculadas, fora
da tela; E1 exemplo do mês vigente de entrega, ordem por SHA-256 de "data:grupo:projeto_id", caminho limpo sem Retorno
Marca, 2 a 16 h; E2 linha do tempo, minutos das etapas pelo maior resto; E3 dias meio para cima; X1 universo = meses
completos de entrega; X2 histograma de 4 h; X3 ≤ 24 / 24–40 / > 40 h; X4 razão das metades (Q3 − mediana) ÷ (mediana −
Q1); X5 dois Q-Q (sino; log-normal em ln(h + 1)), aderência = correlação dos 160 pontos, normal se r ≥ 0,95; X6 limite
= exp(Q3ₗ + 1,5 × (Q3ₗ − Q1ₗ)) − 1, pacotes = nome começa por "[Pacote"; X7 comparação dos grupos, fora da tela. Tabela
de 24/10 na seção 9.1 (histórico onde divergir).

**(e) Base.** `gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_2026_sla_movimentos` (`TAB_SLA`, projeto × passo):
`projeto_id`, `passo`, `status`, `fase`, `entrada`, `saida`, `exclusivo`, `nome_projeto`, `_processado_em`;
`sla_util_horas` só na conferência com almoço. Cobertura (D-SLA-4): `gold_monday.gld_agenciamento_fluxo_mensal`
(`evento`, `familia`, `mes_entrada`, `mes_evento`, `quantidade`). Exceção temporária C2: o expediente sem almoço é
recalculado em `app/expediente.py` até a v2 da gold.

**(f) SQL principal** (todos os números da página e do slide 2, por grupo, ano e mês; expediente sem almoço refeito no
banco; trocar `'2026-09'` pelo último mês completo; aderência do Q-Q e M da cobertura na ficha, 0.6.2 e 0.6.3):

```sql
WITH m AS (SELECT projeto_id, passo, status, fase, entrada, saida, exclusivo, nome_projeto
           FROM `gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_2026_sla_movimentos`),
fer AS (SELECT d FROM UNNEST([DATE '2025-01-01','2025-01-20','2025-01-25','2025-03-03','2025-03-04','2025-03-05','2025-04-18',
  '2025-04-21','2025-04-23','2025-05-01','2025-06-19','2025-07-09','2025-09-07','2025-10-12','2025-11-02','2025-11-15',
  '2025-11-20','2025-12-24','2025-12-25','2025-12-31',
  DATE '2026-01-01','2026-01-20','2026-01-25','2026-02-16','2026-02-17','2026-02-18',
  '2026-04-03','2026-04-21','2026-04-23','2026-05-01','2026-06-04','2026-07-09','2026-09-07','2026-10-12',
  '2026-11-02','2026-11-15','2026-11-20','2026-12-24','2026-12-25','2026-12-31']) d),
ini AS (SELECT projeto_id, entrada t0, exclusivo, STARTS_WITH(TRIM(IFNULL(nome_projeto, '')), '[Pacote') pacote FROM m WHERE passo = 1),
pronto AS (SELECT projeto_id, ARRAY_AGG(STRUCT(passo, entrada) ORDER BY passo LIMIT 1)[OFFSET(0)] p FROM m WHERE fase = 'cliente' GROUP BY 1),
base AS (SELECT i.*, pr.p.passo pp, pr.p.entrada t1, FORMAT_DATETIME('%Y-%m', pr.p.entrada) mes          -- D-SLA-1
         FROM ini i JOIN pronto pr USING (projeto_id) WHERE pr.p.passo > 1),
us AS (SELECT b.projeto_id,
         SUM(GREATEST(0, DATETIME_DIFF(LEAST(e.saida, DATETIME(d, TIME(j.h1,0,0))), GREATEST(e.entrada, DATETIME(d, TIME(j.h0,0,0))), MICROSECOND))) us
       FROM base b JOIN m e ON e.projeto_id = b.projeto_id AND e.passo < b.pp AND e.fase = 'equipe' AND e.saida IS NOT NULL
         AND NOT STARTS_WITH(LOWER(e.status), 'em elaboração - retorno marca'),                           -- D-SLA-2
         UNNEST(GENERATE_DATE_ARRAY(DATE(e.entrada), DATE(e.saida))) d, UNNEST([STRUCT(10 AS h0, 13 AS h1), STRUCT(14, 19)]) j
       WHERE EXTRACT(DAYOFWEEK FROM d) BETWEEN 2 AND 6 AND d NOT IN (SELECT d FROM fer) GROUP BY 1),
p AS (SELECT b.*, IFNULL(us.us, 0) / 3.6e9 h, DATETIME_DIFF(b.t1, b.t0, MICROSECOND) / 3.6e9 h_cal FROM base b LEFT JOIN us USING (projeto_id)),
v AS (SELECT g, mm mes, h, h_cal, pacote FROM p,
        UNNEST(['Todos', IF(exclusivo, 'Exclusivos', IF(NOT exclusivo, 'Nao exclusivos', NULL))]) g,
        UNNEST([mes, IF(mes BETWEEN '2026-01' AND '2026-09', 'ANO', NULL)]) mm
      WHERE g IS NOT NULL AND mm IS NOT NULL AND mes BETWEEN '2026-01' AND '2026-10'),
w AS (SELECT *, PERCENTILE_CONT(h, 0.5) OVER x med, PERCENTILE_CONT(h_cal, 0.5) OVER x med_cal,
        PERCENTILE_CONT(h, 0.25) OVER x q1, PERCENTILE_CONT(h, 0.75) OVER x q3,
        PERCENTILE_CONT(LN(h + 1), 0.25) OVER x lq1, PERCENTILE_CONT(LN(h + 1), 0.75) OVER x lq3, AVG(h) OVER x media
      FROM v WINDOW x AS (PARTITION BY g, mes)),
lim AS (SELECT *, EXP(lq3 + 1.5 * (lq3 - lq1)) - 1 limite FROM w),                                  -- X6
z AS (SELECT *, h <= q1 z1, h > q1 AND h <= q3 z2, h > q3 AND h <= limite z3, h > limite z4, h < media abaixo FROM lim)
SELECT g, mes, COUNT(*) n, ROUND(ANY_VALUE(med), 3) mediana, ROUND(ANY_VALUE(med_cal) / 24, 3) dias_cal,
  ROUND(100 * COUNTIF(h <= 8) / COUNT(*), 2) p8, ROUND(100 * COUNTIF(h <= 16) / COUNT(*), 2) p16, ROUND(100 * COUNTIF(h <= 24) / COUNT(*), 2) p24,
  ROUND(ANY_VALUE(media), 3) media, ROUND(STDDEV_SAMP(h), 3) dp, ROUND(ANY_VALUE(q1), 3) q1, ROUND(ANY_VALUE(q3), 3) q3,
  ROUND((ANY_VALUE(q3) - ANY_VALUE(med)) / NULLIF(ANY_VALUE(med) - ANY_VALUE(q1), 0), 3) razao,
  ROUND(ANY_VALUE(lq1), 4) lq1, ROUND(ANY_VALUE(lq3), 4) lq3, ROUND(ANY_VALUE(limite), 3) limite,
  COUNTIF(z1) z_rapidos, COUNTIF(z2) z_comuns, COUNTIF(z3) z_demorados, COUNTIF(z4) z_fora, COUNTIF(z4 AND pacote) fora_pacote,
  ROUND(100 * COUNTIF(h > 40) / COUNT(*), 2) p40, ROUND(100 * COUNTIF(abaixo) / COUNT(*), 2) abaixo_media, ROUND(MAX(h), 1) maximo
FROM z GROUP BY g, mes ORDER BY g DESC, mes;
```

**(g) Resultados** (25/10/2026, carga de 23/10 20:23:42 UTC; app = BigQuery em todos os itens), linhas ANO:

| Grupo | n | Mediana h | Dias | ≤ 8 / ≤ 16 / ≤ 24 h % | Média | Q1 · Q3 | Razão | Limite log | Zonas | Fora (pacote) | > 40 h % | Máx. |
|---|---:|---:|---:|---|---:|---|---:|---:|---|---|---:|---:|
| Todos | 2.348 | 14,261 | 2,796 | 31,05 / 55,54 / 70,91 | 25,448 | 6,541 · 27,576 | 1,725 | 209,787 | 587 / 1.174 / 559 / 28 | 28 (27) | 12,31 | 515 |
| Exclusivos | 1.610 | 11,830 | 2,020 | 37,08 / 62,30 / 75,90 | 23,413 | 5,165 · 23,791 | 1,794 | 198,931 | 403 / 804 / 382 / 21 | 21 (21) | 10,12 | 483 |
| Não exclusivos | 725 | 19,642 | 3,959 | 18,07 / 41,10 / 60,69 | 29,501 | 10,654 · 32,000 | 1,375 | 156,244 | 182 / 363 / 171 / 9 | 9 (8) | 16,00 | 515 |

Por mês (Todos), n · % ≤ 24 h · mediana: jan 111 · 74,77 · 13,16; fev 108 · 72,22 · 15,71; mar 159 · 70,44 · 14,89;
abr 215 · 64,65 · 16,34; mai 201 · 64,68 · 16,32; jun 288 · 68,06 · 16,46; jul 548 · 71,53 · 12,92; ago 378 · 74,87 ·
12,60; set 340 · 74,12 · 13,56; out (parcial) 242 · 66,53 · 15,75. Cobertura: M = 3.553 (SQL 0.6.3) → 2.348 ÷ 3.553 =
66%. Aderência (SQL 0.6.2): r = 0,5764 contra a normal; Φ(−25,448 ÷ 53,436) = 31,7% → 32.

**Validação do cálculo (25/10, antes das regras novas; consultas de cobertura, Kaplan-Meier, partição, variantes, mês a mês e almoço feitas só com SELECT; as SQL que reproduzem a tela estão na ficha 0.6):** a
conta reproduzia exatamente (2.425; 15,21 h; 52,6% ≤ 16 h); almoço correto (19 s de diferença máxima para a gold);
cobertura de 67% (jan–mai 42–50%), viés pequeno e conservador; censura desprezível em jan–set; o mês de entrada enviesava
o mês parcial (outubro 65% ≤ 16 h contra 40% por Kaplan-Meier); meta de 75% em 16 h inatingível (melhor mês 58%; P75 ~29
h); fila mantida (em 9% dos casos o card vai da Entrada direto ao cliente); reabertos/Standby com efeito desprezível
(15,21 → 15,05 h); pacotes pesam na média e no P90, quase nada na mediana.

**(h) Atualização com a carga.** Tudo é recalculado sobre a carga em memória a cada versão (cache por versão): mês
parcial = mês do `_processado_em` em São Paulo; meses completos = jan até o mês anterior; "até dd/mm" e o fim do "em
aberto" = véspera da carga (`sla.data_corte`); o exemplo do estudo muda na virada do dia (data de São Paulo); a
cobertura some se a gold do SLA e a de fluxo forem de dias diferentes ou se N > M. Janeiro mostra o estado "sem mês
completo" (C7). Ficha 6.9: nada fixo no código.

**(i) Pendências e perguntas.** **PD21** (tempo da equipe pronto na gold: fase própria para Retorno Marca; manter quem
voltou à equipe depois da 1ª entrega; coluna de pacote/lote; relógio para cards criados direto em elaboração/revisão;
tabela de pedidos em andamento para Kaplan-Meier; v2 sem almoço); PD15 (SLA de 2025 não existe); pedido "Oficializar a
meta do SLA" (metade em até 2 dias de trabalho é sugerida, D38); conferir 28 `encerrado_sem_entrega` e 19 `entrega_sem_aguardando` na gold;
C3 (horas corridas ÷ 24 × diferença de datas, decidido por horas); no celular o histograma do slide 2 fica com texto
< 11 px (ficha 0.7).

### M5. Previsão de demanda

**(a) Pergunta.** "Quantos pedidos devem chegar até o fim do mês e do ano?" — acompanhamento mensal de 2026.

**(b) Resposta de hoje (D56; retrato de setembro refeito em 26/10/2026 17:58; carga de 26/10/2026 09:01, dados até
25/10).** Uma série e um modelo por recorte (sem repartição). Mês vigente (realizado até 25/10 · previsão de fechamento)
e os dois seguintes, com a faixa provável:

| Série | Modelo | Erro no teste jun–set · jan–mai | Outubro | Novembro | Dezembro |
|---|---|---|---|---|---|
| Inbound | média de 6 meses | 14,4% · 26,9% (robusto) | 133 · 138 (131–212), dentro da faixa | 138 (146–219) | 138 (147–221) |
| Mercado | rede neural de 1 neurônio | 12,6% · 26,8% (**não robusto**; alternativa ARIMA com tendência 16,5% · 20,4%) | 304 · 464 (334–483), dentro | 517 (372–538) | 588 (423–612) |
| Mercado exclusivos | combinação de 6 | 10,9% · — (série só de 2026: confiança menor) | **87 · 196 (158–214), 42% abaixo do esperado** | 200 (161–219) | 204 (164–223) |
| Mercado não exclusivos | Holt simples | 19,2% · — (série só de 2026) | 185 · 244 (194–318), dentro | 263 (209–343) | 282 (224–367) |

Filtros: Todos = Inbound | Mercado; Exclusivos = Inbound (todo ele é de talento exclusivo, PD24) | Mercado exclusivos;
Não exclusivos = Inbound "não se aplica" | Mercado não exclusivos. Outubro do Mercado exclusivos: até o dia 25, 17
pedidos em lote (média de jun–set no mesmo ponto: 50) e 70 avulsos (98); o total do Mercado está quase normal (−6%), a
parcela exclusiva caiu de ~46% para 29%; a série própria não corrige (ficha 5.0.7).

**(c) Por que.** D56 (Caio, 26/10): cada recorte com a sua série e o seu modelo; todos os modelos em todas as séries na
régua D48 (janela de 12 meses, teste h1 jun–set, menor WAPE, empate < 1 ponto = o mais simples) + R7 para as séries só de
2026 (janela expansiva e mínimo de meses por modelo: 9 dos 61 se aplicam). Inbound: `ref_media_6m` empatou com
`arimax_011` (13,5%), `arimax_110` e `comb_selecao`; Mercado: as 11 redes empataram (12,6–13,0%); Mercado exclusivos: 4
combinações empataram (10,9–11,4%), ficou a de menor erro; não exclusivos: Holt simples 3,2 pontos à frente. A silver
2025 (fonte fraca) foi avaliada como extensão da exclusividade e não entrou (ficha 5.0.8). Antes: D48 (repartição
pela parcela ou previsão direta do filtro), D55 (AutoTS não venceu; Inbound só de exclusivos).

**(d) Regras.** P1–P12 em `previsao/calculos.py` (séries, teste, vencedor, filtros, sem confiança, execução mensal, eixo
2026, métricas, pé do gráfico, cartões do mês vigente + 2 seguintes, "Por quê", diálogo "Modelos comparados");
critério e contrato C1–C5 / v3 P1–P10 em `ml/previsao.py` (C5: robustez); protocolo R1–R7 em `ml/regua.py`; séries
S1–S6 em `ml/dados.py`; AutoTS AT1–AT7 em `ml/modelos/automatico.py`; job J1–J6 em `previsao/job.py`.

**(e) Base.** `gld_agenciamento_entrada_diaria` (`data`, `tipo_de_input`, `quantidade`, `quantidade_estimada`,
`_processado_em`) para Inbound e Mercado; silver 2026 com o critério de `app/sql/talentos_ano.sql` (D30-b) para os
recortes de exclusividade e o diagnóstico de lotes (+ `marca`, `nome_projeto`); silver 2025 (`talentos_exclusivos`) só
na sensibilidade.

**(f)–(g) SQL e resultados.** Ficha [previsao.md](paginas/previsao.md), seção 5.0 (SQL completo S1–S6 com o resultado
esperado, top 5 + vencedor por série com teste e verificação, memória de cálculo das previsões e das faixas, outubro,
sensibilidade 2025, reavaliação do Mercado); seções 5.1–5.7 = D48/D55 (histórico).

**(h) Atualização.** Mensal (D48): a carga que traz um mês fechado novo dispara `python -m ml.rodar --rotina` (snapshot
e CSVs por série, 61 modelos × 4 séries, retrato em `ml/saida/previsao.json` e `retratos/<mês>.json`, histórico PD09 por
retrato e protocolo); as outras cargas do mês só atualizam o realizado do mês em andamento (`--acompanhamento`, com os
lotes e os sem talento). Em produção (Cloud Run) o job é separado e ainda não existe: comandos na ficha, seção 9.

**(i) Pendências.** DC1 (regra C5 para o Mercado total: recomendação na ficha 5.0.9 — manter a rede com o selo "não
robusto" e decidir com o fechamento de outubro); DC2 (nov/dez como cenário); PD09 (outubro é o 1º ponto fora da
amostra; o Mercado exclusivos deve fechar bem abaixo da faixa); PD01 (exclusividade na gold de entradas, que daria
histórico às séries de exclusividade); PD10 (datas reais de 2025); PD24 (Inbound marcado como não exclusivo); job de
produção e leitura num bucket.

### M6. Resultado: negócios fechados

**(a) Pergunta.** "Quanto do que entregamos vira contratação?" (pedido da diretoria: talentos contratados, volume,
marcas, ticket médio).

**(b) Resposta de hoje.** Nenhuma: **máscara** ("A resposta depende da base de contratações").

**(c) Por que.** D19 (22/10: o board de orçamentos não registra o fechamento; "Encerrado" junta ganhos e encerramentos
automáticos de 30 dias); D30 (em máscara). Vem de **outra tabela**, a conversar com o Caio.

**(d)–(g).** Sem regras nem SQL até a base existir. Fonte candidata: planilha de contratações (Mayara) → gold de
contratações; `vendido`/`data_da_venda`/`valor_da_proposta` da silver 2026 só como conferência.

**(h) Atualização.** Máscara de `pendencias.py`.

**(i) Pendências.** PD05 (contratações fechadas), PD06 (destino depois da entrega), PD18 (prazo de pagamento dos
intervenientes).

### M7. Qualidade dos dados

**(a) Pergunta.** "Dá para confiar nos números desta área?"

**(b) Resposta de hoje.** Nenhuma na tela: **máscara** ("As verificações estão sendo conferidas").

**(c) Por que.** D21 (22/10: verificações prontas e testadas, Q1–Q6 integridade e A1–A5 atenção, tela em branco a
pedido do Caio); D30 (volta a ser seção, em máscara). Conteúdo e tabela **a conversar** com o Caio (candidata: gold de
pendências de preenchimento).

**(d) Regras.** `qualidade/calculos.py` (Q1–Q6, A1–A5), testadas; só vão à tela depois de conferidas no BigQuery e com
ficha própria.

**(e)–(g).** Base atual: a gold do SLA (verificações de 22/10: 6 de 6 integridades em zero; 46 entregues em < 5 min, 29
em > 30 dias, 37 voltas para Entrada em 31 projetos, 32 aguardando > 30 dias, 21 sem talento). Fora da tela.

**(h) Atualização.** Máscara de `pendencias.py`.

**(i) Pendências.** PD12 (evolução das pendências de preenchimento), PD13 (foto de fim de mês). Candidatos: estimadas
de 2025, cards sem data, "Sem tipo", achados F7–F10, sem nomes de marca ou card.

## Como o portal funciona

**Menu lateral e áreas.** O site é um conjunto de **áreas** (hoje uma: Gestão de orçamentos, "Orçamentos" no menu). Cada
área é uma pasta em `app/apresentacoes/<area>/` (D11, D17); o site descobre as pastas e monta sozinho o menu lateral
(mapa: área → Início, seções e "O que falta"; recolhível numa régua de ícones, escolha guardada no navegador), as abas
do cabeçalho (só texto, D30) e, no celular (≤ 900 px), a gaveta "Áreas" e a barra inferior com Áreas · Início · Anterior
· Próxima (D18, D30). O cartão do menu mostra a data dos dados e a última conferência.

**Navegação entre perguntas.** Cada seção tem `pergunta` (vira o título e o texto do link "Próxima pergunta"), `estado`
(pronta / parcial / pendente) e `na_reuniao`. A ordem é a da reunião: Início → Talentos → Atendimento → SLA → Previsão
→ Resultado → Qualidade → "O que falta" (`Apresentacao.vizinhas()`); o passador (PageDown) segue o mesmo link. Dentro
de uma página com vários slides (o estudo), Anterior/Próximo, setas, deslizar o dedo e `#n` no endereço. O estudo do SLA
abre pela lupa do cartão e fecha pelo X, mantendo `?talentos=`.

**Moldura congelada.** Menu, cabeçalho (logo, abas, tela cheia), carimbo e rodapé ficam no mesmo lugar em todas as
páginas: o palco reserva a mesma faixa inferior (`--faixa-inferior`) com ou sem barra de slides, e a lâmina escala pela
mesma regra. Entre páginas, View Transitions (só com movimento permitido) trocam só o conteúdo; Speculation Rules
(`/especulacao.json`, `prerender` moderado, sem `/static` nem endereços com parâmetros) pré-carregam a próxima página. No
celular, "Próxima pergunta" e o rodapé vão para o fim do slide (D36, decisão 14; em páginas de vários slides, só o
rodapé, que acompanha o slide visível).

**Modo apresentação.** `MODO=apresentacao` mostra só as seções `na_reuniao` (ou as de `SECOES_VISIVEIS`, lista separada
por vírgula) em menu, abas, barra do celular e rotas (seção oculta = 404), e nunca telas de exemplo (`?exemplo=1`),
mesmo com `DEV`. Seção sem base aparece em máscara (pergunta + "Aguardando dados" + pendências, sem nenhum dígito).
Liga a **base congelada** (`CONGELAR`, D45): a carga lida na subida não troca, o menu diz "base congelada para a
apresentação" (estado `congelada`, sem o aviso de base atrasada), o job da Previsão não dispara (J5) e carga nova só
mostra "Há dados novos na base. Atualizar" (D49). Resultado fica fora (`na_reuniao=False`); a Previsão leva à Qualidade.

**Movimento (D46, D49).** Números prontos desde o 1º quadro (sem contagem); um gesto de dado por página ou slide, até
~1,15 s, sem mola nem loop, só com `prefers-reduced-motion: no-preference`; navegação só com o voo da pílula (320 ms);
troca de grupo de talentos e recarga por carga nova abrem a página pronta (`.revisto`), com o foco de volta no grupo;
impressão parada. Conferido por `tests/test_movimento.py` e `node tools/conferir_layout.mjs --movimento`.

**Previsão (job de ML, D48).** O site só lê `ml/saida/previsao.json`. A 1ª carga depois que um mês fecha (corte E3 de
`app/corte.py`: véspera do dia de processamento, em São Paulo) dispara `python -m ml.rodar --rotina` em segundo plano
(snapshot só SELECT, 58 modelos, filtros, retrato e histórico, ~9 min); as demais cargas, `--acompanhamento` (só o
realizado do mês). Trava `ml/saida/rotina.lock` (3 h), estado em `rotina_estado.json` e falha visível na página;
`PREVISAO_JOB=off` desliga. Em produção o job ainda não existe (PD23).

**Atualização automática dos dados.**

- **Tabela em memória** (`app/dados.py`, classe `Tabela`; `Consulta` para as SQL agregadas da silver): cada tabela gold
  fica inteira em memória por instância, só com as colunas usadas (Storage Read API, com volta à leitura comum).
- **Recarga pelo metadado:** no máximo a cada `RECARGA_MIN` (5 min) o site lê o `modified` da tabela e recarrega só se
  mudou. No computador, em segundo plano (a página responde na hora); em produção (`K_SERVICE`), na própria requisição.
- **Contrato antes de trocar:** colunas obrigatórias, chave única, não vazia, `_processado_em` único, histórico do SLA
  contínuo; carga inválida é recusada e a anterior continua no ar.
- **`ao_carregar`:** os cálculos derivados da carga nova são aquecidos antes da troca; ninguém espera o recálculo.
- **Versão da carga:** `versao_de(df)` identifica a carga; os caches dos cálculos são por versão (nunca misturam
  cargas). A página leva a meta `relatorio-versao` (assinatura das cargas) e `relatorio-intervalo`; a aba aberta
  confere a página periodicamente (só visível, sem interromper dica, seleção ou menu) e recarrega quando a assinatura
  muda.
- **Rodapé datado** em toda página: "Dados até [véspera] · atualizados em [hora]", pelo `_processado_em` da carga
  (INI-D1, 25/10; sem a coluna, o `modified`).
- **Agenda da gold:** seg–sex 09:00 com 45 min de tolerância; passou disso, aviso "a base não atualizou no horário
  previsto".
- **Corte e base congelada em arquivo (D65, 31/10/2026):** com `CORTE_DADOS` (padrão `2026-10-31`; `off` desliga), cada
  carga nova passa pela regra do corte antes de entrar (`app/congelamento.py`). K2: fim (E3) < corte → aceita. K3: corte
  ≤ fim ≤ corte + `CORTE_FOLGA_DIAS` (1) → última carga aceita; a tabela congela e é gravada em `BASE_CONGELADA_DIR`
  (`app/base_congelada/<tabela>.parquet` + `.json` com corte, fim, `_processado_em`, `modified`, linhas e sha256). K4:
  fim além da folga → ignorada (a anterior continua, com a falha visível; a mesma carga não é baixada de novo). K5:
  todas as tabelas na mesma carga. K6: com o arquivo presente, a tabela nasce dele, **sem consultar o BigQuery**; em
  produção nada é gravado. K7: arquivo de outro corte, sem ficha ou com hash diferente é ignorado. Congelada, nem
  `df(forcar=True)` troca a base. Estado `congelada`, e o rodapé ganha "base congelada para a apresentação" só quando
  todas as fontes da página estão na carga do corte (`dados.base_congelada`). Sem o corte, vale o `CONGELAR` da D63.
  Ensaio de 31/10 (corte simulado em 29/10, pasta temporária): 10 tabelas, ~1,1 MB, e as 8 páginas geradas do arquivo
  idênticas às geradas do BigQuery.

**Falhas.** BigQuery fora com carga válida: continua a última carga, com aviso "atualização atrasada", e nova tentativa
depois de `RECARGA_MIN`. Sem nenhuma carga válida: **503 honesto**, sem números, com `Retry-After`. Fontes incoerentes
(entrada × fluxo de dias diferentes, silver × gold que não conciliam): a página avisa em vez de misturar fotografias.
`/saude` informa versão, data da tabela e atraso.

**Segurança e acessibilidade.** CSP sem estilo inline (`style-src` com nonce por resposta, `style-src-attr 'none'`,
`script-src 'self'`); `Cache-Control: private, no-store` nas páginas; estáticos com hash de conteúdo. Acessibilidade
(CLAUDE.md, item 10): controles nativos com nome; filtros aplicam só pelo botão; texto pequeno ≥ 4,5:1; gráficos em
HTML/CSS/SVG com texto para leitor de tela em cada mês/barra; status com ícone + texto; mês futuro em itálico
`--tinta-3`; menos movimento respeitado; slide cabe em 1440×900 e não rola para o lado em 390 px.

**Ambiente local × produção.** Local: `AUTH=off` (só no computador), venv em `C:\Users\CCMB\.venvs\ppd-agenciamento-sla`,
credenciais ADC de `C:\Users\CCMB\AppData\Roaming\gcloud-viu`, `uvicorn` na porta **8096** (README; 8080, 8081, 8090 e 8095 ficaram presas a processos fantasmas do Windows). Produção: Cloud Run
`relatorios-agenciamento` (`us-central1`, mín. 0 / máx. 2), `AUTH=off` recusado quando `K_SERVICE` existe; fases 2
(controle de acesso), 3 (GCP, o Caio roda), 4 (envio pelo Outlook) e 5 (novas páginas) — nada publicado.

**Testes e ferramentas de auditoria.** `python -m pytest tests -q` (392 testes em 26/10/2026; dados sintéticos de
`tests/conftest.py`, sem BigQuery): cálculos e regras de cada página, rotas, cabeçalhos de segurança e cache,
acessibilidade básica, portal e máscaras. Ferramentas somente leitura em `tools/`: `auditar_relatorio.py` (gold ×
silver, integridade, SLA por calendário independente), `auditar_paginas.py` (fontes de Início/Talentos/Atendimento com
identidade e evidências), `conferir_expediente.py` (expediente contra a gold), `conferir_estudo.py` (estudo nos 3
grupos), `conferir_layout.mjs` (layout e movimento) e `checar_reuniao.py` (passo único antes da reunião). A ficha
`o_que_falta.md` é conferida contra `pendencias.py` (`tests/test_documentacao.py`).

## 1. O que é

Um **site interno de relatórios** do board Backlog 2026 | Agenciamento, publicado no Cloud Run, que lê as tabelas gold
do BigQuery e se atualiza sozinho depois do job diário (seg–sex 09:00). Começa pela análise de **SLA** e cresce por
**páginas**: cada tabela gold nova vira uma ou mais páginas, sem mexer nas existentes.

```text
monday → bronze 08:00 → silver 08:30 → gold 09:00 (gold-agenciamento)
                                          │
                                          ▼
                     site de relatórios (Cloud Run, este projeto)
                       ├─ lê as tabelas gold (só leitura) e guarda em memória
                       ├─ recarrega quando a tabela muda (metadado, sem custo)
                       └─ controle de acesso próprio (link por e-mail) + página de admin
```

**Público:** até ~200 pessoas internas, com e-mails de vários domínios da empresa.

## 2. Objetivos e critérios de sucesso

1. Painel de SLA confiável, com os mesmos números da tabela gold (conferidos contra consultas no BigQuery).
2. Dados do dia disponíveis no site até ~09:30 sem ação manual.
3. Acesso só para pessoas dos domínios da empresa, **sem fila de aprovação** e com **administração simples** por tela.
4. Página nova = uma pasta nova no código (sem alterar menu, login ou outras páginas).
5. **Sem custo extra:** dentro das cotas gratuitas e da reserva de BigQuery que a empresa já paga.
6. Profissional: código versionável, testes do controle de acesso, registro de quem acessou, deploy repetível.

## 3. Arquitetura

| Peça | Escolha | Observação |
|---|---|---|
| Site | **Python 3.12 + FastAPI**, páginas renderizadas no servidor (Jinja2), gráficos em **HTML/CSS** (sem biblioteca externa, D14) | mesma linguagem dos projetos bronze/silver/gold |
| Hospedagem | **Cloud Run (serviço)** `relatorios-agenciamento`, `us-central1`, mín. 0 / máx. 2 instâncias | desliga sem uso; 1º acesso do dia pode levar 2–3 s |
| Dados | tabelas gold lidas **inteiras em memória** (SLA: 5,4 MB por carga, 7,6 MB em memória); filtros calculados no servidor | reavaliar por tabela se alguma passar de ~200 MB |
| Atualização | a cada requisição, se a última checagem tem mais de 10 min, o site confere o **metadado `modified`** da tabela e recarrega só se mudou | dispensa Cloud Scheduler; sem tarefa em segundo plano (o Cloud Run só cobra e só dá CPU durante as requisições) |
| Controle de acesso | link de acesso por e-mail + sessão em cookie assinado (seção 5) | sem IAP, sem Firestore |
| Dados do app | dataset **`app_relatorios`** no BigQuery: usuários, domínios permitidos, eventos de acesso | poucas centenas de linhas/mês |
| Segredos | **Secret Manager**: credencial da caixa de e-mail e chave de assinatura das sessões | o Caio cadastra; o código só lê |
| E-mail | caixa de serviço da área no **Outlook** (método de envio a confirmar — Graph ou SMTP) | |
| Conta de serviço | `relatorios-agenciamento@…`: leitura nas tabelas gold usadas, escrita só em `app_relatorios`, `bigquery.jobUser`, leitura dos 2 segredos | mínimo privilégio |
| Deploy | igual ao gold: zip → Cloud Shell → `gcloud run deploy --source .`; GitHub depois | |

### 3.1 Áreas e seções como módulos (D11, D17)

Cada **área** é uma pasta em `app/apresentacoes/<area>/` com `apresentacao.py` (título, cabeçalho, ordem e a lista
de seções), `inicio.html` (página inicial da área) e uma subpasta por **seção** (`<secao>/calculos.py` com as regras
numeradas e `<secao>/template.html` com os slides). O site descobre as pastas e monta o menu lateral e o navegador de
seções sozinho. Hoje: área Gestão de orçamentos com Início e as seções Talentos, Atendimento, Prazo (SLA), Previsão,
Resultado e Qualidade, mais a página "O que falta" (D30).

Política de dados (`app/dados.py`): a tabela gold fica inteira em memória por instância; a cada requisição, se a
última checagem tem mais de `RECARGA_MIN` minutos, o site lê o metadado `modified` e recarrega só se mudou. Toda
carga passa por um contrato (colunas obrigatórias, chave única, não vazia). Se o BigQuery ou o contrato falhar com uma
carga anterior válida, ela continua servida com um aviso "atualização atrasada" e a próxima tentativa espera
`RECARGA_MIN`; sem carga válida, a página responde 503 sem números. `/saude` informa versão da carga, data da tabela
e atraso. Em produção (`K_SERVICE` definido), `AUTH=off` é recusado.

### 3.2 Primeira versão das páginas de SLA (proposta — a validar com o Caio)

| Página | Pergunta | Base |
|---|---|---|
| Visão geral | quantos projetos em aberto, tempo típico da equipe e do cliente, encerrados no período | `fase`, `sla_util_horas`, `em_aberto`, `status_atual` |
| Gargalos | em que status o projeto fica mais tempo (mediana e p90 em horas úteis) | `status`, `fase`, `sla_util_horas` |
| Cliente sem retorno | quem está em Aguardando Feedback há mais de 10 dias úteis, com link | `alerta`, `aberto_ha_util_horas`, `link_projeto` |
| Qualidade do fluxo | retrabalho, reabertura, entrega sem Aguardando Feedback, encerrado sem entrega | marcações R19 |
| Esforço | mudanças fora do expediente e hora extra estimada | `fora_expediente`, `hora_extra_horas` |

Filtros comuns: período (data de entrada), marca, talento, tipo de input/output, orçamento. Leituras em texto geradas
**por regra** (sem LLM).

## 4. Acesso — como funciona para quem usa

1. Abre a URL única do site → página "Digite seu e-mail".
2. Domínio na lista permitida → recebe e-mail da caixa de serviço com o botão **Entrar** (link vale 15 min, uso único).
3. Clicou → entra. **Aprovação automática**: o clique prova que o e-mail é dela.
4. Nos próximos 30 dias, entra direto (sessão no navegador).
5. A partir do dia 25, aviso no topo: "Seu acesso vence em X dias — **Renovar agora**" (um clique manda o link).
6. Domínio fora da lista → mensagem neutra; nada é enviado.

## 5. Controle de acesso — regras técnicas

| ID | Regra |
|---|---|
| A1 | Identidade = e-mail comprovado pelo clique no link; nunca um e-mail apenas digitado |
| A2 | Link de acesso: token aleatório assinado, validade **15 min**, **uso único** (registrado em `app_relatorios`) |
| A3 | Limites: até 3 links por e-mail a cada 15 min e por IP a cada hora; resposta igual para domínio aceito ou não (não revela quem existe) |
| A4 | Sessão: cookie assinado `HttpOnly`, `Secure`, `SameSite=Lax`, validade **30 dias**; aviso de renovação a partir do dia 25 |
| A5 | Bloqueio: o admin bloqueia na tela; o site relê a lista a cada 5 min → a pessoa perde o acesso em até 5 min, mesmo com sessão aberta |
| A6 | Perfis: `leitor` (padrão) e `admin`. Admins iniciais pela variável `ADMINS` (o Caio); demais promovidos na tela. Página pode restringir perfis (ex.: dados por pessoa) |
| A7 | Domínios permitidos editáveis na tela de admin (tabela em `app_relatorios`), com um valor inicial em variável |
| A8 | Registro: login, renovação, bloqueio, mudança de perfil e domínio — quem, quando, de onde. Último acesso por pessoa, gravado no máximo 1×/dia |
| A9 | Logout apaga a sessão; trocar a chave de assinatura no Secret Manager derruba todas as sessões (botão de emergência) |
| A10 | Desenvolvimento local: login desligado (`AUTH=off`) ou com envio simulado (link aparece no terminal). Nunca publicar com `AUTH=off` |

### 5.1 Tela de admin (só perfil `admin`)

- **Pessoas:** lista com e-mail, perfil, situação, 1º e último acesso; filtrar; **Bloquear / Desbloquear**, **Tornar admin / leitor**.
- **Domínios:** incluir e remover domínios permitidos.
- **Registro:** últimos eventos de acesso.
- **Dados:** quando cada tabela foi atualizada e quando o site recarregou; botão **Recarregar agora**.

## 6. Pré-requisitos e testes no GCP

| # | Item | Situação |
|---|---|---|
| G1 | Conta `caio.barroso@viu.com.br` com permissão de criar Cloud Run, conta de serviço, Scheduler, tabelas, e de dar papéis (`setIamPolicy`) | ✅ testado 21/10/2026 |
| G2 | APIs ativas: Cloud Run, Cloud Build, Artifact Registry, Cloud Scheduler, Secret Manager | ✅ |
| G3 | Deploy de teste no Cloud Run (imagem *hello*, privado) e exclusão | ✅ 21/10/2026 |
| G4 | **Política da organização permite serviço aberto à internet** (`allUsers` ou `--no-invoker-iam-check`) — necessário porque o login é do próprio site | ⏳ testar com o *hello* |
| G5 | Caixa de serviço do Outlook: método de envio (Graph ou SMTP) e credencial no Secret Manager | ⏳ Caio |
| G6 | Lista inicial de domínios permitidos | ⏳ Caio |

## 7. Custos

**Regra:** ao fim de cada fase, reestimar o custo mensal (cenário realista e pessimista) e registrar na tabela 7.3 —
para decidir se vale manter no ar. Depois do 1º mês publicado, trocar a estimativa pelo custo real (faturamento,
filtro pelo label `projeto=ppd-agenciamento-sla`).

### 7.1 Premissas (21/10/2026)

- **Realista:** ~50 pessoas ativas por dia útil × 10 páginas = ~11 mil páginas/mês.
- **Pessimista:** as 200 pessoas todo dia útil × 30 páginas = ~132 mil páginas/mês.
- Cada página: ~0,3 s de CPU, ~16 KB de HTML (3,4 KB comprimido) mais CSS/JS/fontes em cache no navegador; 1 vCPU,
  1 GiB. Medido no computador: 17,6 ms por página com cache aquecido (não inclui Cloud Run, partida a frio nem login).
- A franquia de saída do Cloud Run vale para tráfego na América do Norte; para pessoas no Brasil a saída é cobrada
  desde o primeiro byte (≈ US$ 0,12/GB). O volume é pequeno (≈ 1–13 GB/mês), mas não é "grátis".
- Preços de lista do Google (us-central1, USD); câmbio de referência R$ 5,50.
- **Cotas gratuitas são por conta de faturamento**: se outros serviços da empresa já as consomem, vale o pessimista
  "sem cota".

### 7.2 Estimativa por peça (mensal)

| Peça | Realista | Pessimista sem cota gratuita | Base |
|---|---|---|---|
| Cloud Run — CPU e memória | US$ 0 (≈ 3–5 mil vCPU-s; cota 180 mil) | ≈ US$ 1,10 (≈ 40 mil vCPU-s × US$ 0,000024 + memória) | cobrança só enquanto atende (mín. 0 instâncias) |
| Cloud Run — requisições | US$ 0 (≈ 40 mil; cota 2 milhões) | ≈ US$ 0,20 (≈ 400 mil × US$ 0,40/milhão) | |
| Saída de dados (internet) | US$ 0 (≈ 1 GB) | ≈ US$ 1,60 (≈ 13 GB × US$ 0,12) | páginas comprimidas |
| BigQuery — leitura | US$ 0 | US$ 0 | reserva Enterprise da empresa (`gglobo-reservabq-us-ent`): sem cobrança por volume; ~5 MB por recarga |
| BigQuery — armazenamento `app_relatorios` | US$ 0 | < US$ 0,01 | < 10 MB |
| Secret Manager | US$ 0 (2 segredos; cota 6) | ≈ US$ 0,12 | |
| Cloud Build + Artifact Registry | US$ 0 | ≈ US$ 0,10 | poucos deploys/mês; manter só as 2 últimas imagens |
| Cloud Logging | US$ 0 | US$ 0 | cota 50 GB |
| E-mail (Outlook da área) | US$ 0 | US$ 0 | caixa existente |
| Cloud Scheduler / IAP / Firestore | não usados | não usados | D5, D6 |
| **Total** | **≈ US$ 0 (R$ 0)** | **≈ US$ 3 (≈ R$ 17)** | |

### 7.3 Registro por fase

| Data | Fase | Realista | Pessimista | Observação |
|---|---|---|---|---|
| 21/10/2026 | 0 — desenho | US$ 0 | ≈ US$ 3/mês | estimativa inicial; nada publicado |
| 21/10/2026 | 1 — esqueleto local | US$ 0 | ≈ US$ 3/mês | medido: carga da tabela 5,4 MB (reserva), página ~55 KB sem compressão (gzip ligado), 0,1–0,3 s por página com filtros; ECharts pela CDN. Nada publicado; custo atual zero |

Controle: labels `projeto=ppd-agenciamento-sla` em tudo; máximo de 2 instâncias (teto de gasto); alerta de orçamento
opcional (ex.: R$ 30/mês).

## 8. Decisões

| # | Data | Decisão | Motivo |
|---|---|---|---|
| D1 | 21/10/2026 | **Site próprio no Cloud Run** em vez de Power BI ou Looker Studio | crescer por páginas, visual livre, controle de acesso próprio, código versionável; GCP testado e disponível |
| D2 | 21/10/2026 | **Sem LLM por API** no site; leituras em texto por regra; análises profundas com IA feitas fora do site, pelas assinaturas | regra do Caio: IA só pelas assinaturas, sem API paga |
| D3 | 21/10/2026 | **Login por link no e-mail** com domínios permitidos e **aprovação automática** | o Caio não controla grupos/IAM do Google nem Entra; vários domínios; sem fila de aprovação |
| D4 | 21/10/2026 | **Sessão de 30 dias** com aviso de renovação a partir do dia 25 | equilíbrio entre segurança e facilidade |
| D5 | 21/10/2026 | **Sem IAP e sem Firestore**; dados do app no BigQuery (`app_relatorios`) | menos peças; volume pequeno; nada novo para ativar |
| D6 | 21/10/2026 | **Sem Cloud Scheduler**: o site recarrega quando o metadado da tabela muda | menos peças, sem custo |
| D7 | 21/10/2026 | Tabelas gold **em memória** no site, filtros no servidor | 5 MB; resposta rápida; nenhuma consulta por clique |
| D8 | 21/10/2026 | E-mails pela **caixa de serviço do Outlook** da área, credencial no Secret Manager | já existe; sem custo; o Claude nunca vê a credencial |
| D9 | 21/10/2026 | Mesmo projeto GCP `gglobo-viu-dados-hdg-prd` | não existe projeto de aplicações |
| D10 | 21/10/2026 | Desenvolvimento local primeiro; **nada publicado aberto sem o controle de acesso** | os dados têm nomes de projetos, talentos e pessoas |
| D11 | 21/10/2026 | Páginas como módulos (`app/paginas/<slug>/`), menu automático | escalar com novas tabelas sem mexer no resto |
| D12 | 21/10/2026 | Admin por tela (pessoas, domínios, registro, dados) | o Caio precisa de controle fácil, sem comando |
| D13 | 21/10/2026 | O site é um conjunto de **apresentações**: menu lateral com as apresentações; cada uma abre slides de **uma página** (cabe na tela, sem rolar no computador), com Anterior / "n de N" / Próximo, setas, deslizar no celular, link por slide (`/sla#1`) e tela cheia. Cada slide tem nível **gerencial** (big number + estudo) ou **operacional** | pedido do Caio; referência visual de "Gestão de orçamentos" |
| D14 | 21/10/2026 | Identidade VIU: azul `#2400FF` e amarelo `#F8FD0B` (do logo `app/static/viu_logo.jpg`), Playfair Display (títulos e números) + IBM Plex Sans (texto), hospedadas no site; gráficos em HTML/CSS (sem biblioteca externa) | fiel à referência; sem dependência de CDN |
| D15 | 21/10/2026 | Endereços: `/<apresentação>` (ex.: `/sla`); `/p/...` da fase 1 redireciona | endereços curtos e estáveis |
| D18 | 22/10/2026 | **Navegação em três formatos.** Computador: menu lateral como mapa do site (área → Início e seções, seção atual marcada) com botão para **recolher** numa régua de ícones (escolha guardada no navegador; até 1400 px começa recolhido) e abas das seções no cabeçalho do slide. Celular e tablet em pé (≤ 900 px): abas saem do cabeçalho para uma **barra inferior fixa** com ícones (Áreas abre a gaveta com o menu). Navegação (abas com traço) e filtro (cápsula) têm formas diferentes | legibilidade: o slide ganha largura; navegação ao alcance do polegar no celular |
| D19 | 22/10/2026 | **Seção "Negócios fechados" preparada** (`/viu-agenciamento/negocios-fechados`, em branco): o board de orçamentos não registra negócio fechado (gold e silver só têm Encerrado e os Declinados; "Encerrado" mistura ganhos e encerramentos automáticos de 30 dias). Os dados virão de **outra base** que o Caio vai passar. No menu, cada área tem **nome curto de uma linha** (`titulo`, hoje "Orçamentos") e ícone próprio; o cabeçalho do slide mantém o nome completo | o menu vai receber muitas áreas de temas diferentes |
| D20 | 22/10/2026 | **Previsão de demanda** (`/viu-agenciamento/previsao`): quantos orçamentos entram no mês seguinte ao último completo. Esqueleto pronto e testado com série fictícia (`previsao/calculos.py`, regras P1–P6): série mensal de pedidos que entraram; três métodos de referência (mesmo mês do ano anterior, média de 3 meses, sazonal com tendência) testados prevendo os últimos 12 meses só com o passado; fica o de menor erro; faixa provável pelos erros do teste (10%–90%); gráfico com o previsto de cada mês ao lado do realizado. Modelo de ML entra depois como mais um método e só fica se vencer as referências. Mínimo 25 meses. **Aguarda:** histórico de 3 anos no BigQuery (Caio). Em DEV, `?exemplo=1` mostra a tela com dados fictícios (bloqueado em produção) | o Caio quer prever a demanda; com série curta, ML sem comparação com o simples não é confiável |
| D21 | 22/10/2026 | **Qualidade dos dados** (`/viu-agenciamento/qualidade`): lâmina **em branco** por pedido do Caio (só o selo Operacional). Verificações prontas e conferidas com o BigQuery em `qualidade/calculos.py` (Q1–Q6 integridade, esperado zero: hoje 6 de 6; A1–A5 atenção: 46 entregues em < 5 min, 29 em > 30 dias, 37 voltas para Entrada em 31 projetos, 32 aguardando > 30 dias, 21 sem talento), com testes | transparência sobre a base, para ligar quando o Caio quiser |
| D22 | 22/10/2026 | **Nomes das seções**: nome completo no menu lateral e na aba do navegador ("Negócios fechados", "Previsão de demanda", "Qualidade dos dados"); nome curto nas abas do topo e na barra do celular ("Negócios", "Previsão", "Qualidade"), com o completo na dica (`Secao.rotulo`) | cinco abas cabem no cabeçalho em 1261 px e no celular |
| D23 | 22/10/2026 | **Página inicial de Orçamentos = entrada de pedidos**: colunas mensais do ano (seletor 2024/2025/2026) com os cards criados empilhados por grupo de input (Mercado, Inbound, Proativo, Internos, Sem tipo), dica por mês (mouse ou Tab) com quantidade e parcela de cada tipo e legenda em forma de tabela do ano (com a composição de cada grupo na dica). Base: `gold_monday.gld_agenciamento_entrada_diaria` (`TAB_ENTRADA`), regras E1–E4 em `entrada/calculos.py`. Cores: escala de azuis da marca (marinho → claro, Mercado embaixo), validada pela skill dataviz como escala ordinal; pedido do Caio para combinar com o gráfico do SLA. Conferido com o BigQuery: 2026 = 5.488 até 21/10; mesmo período de 2025 = 2.868 (+91%); meses e divisão por tipo batem | pedido do Caio: começar a análise de demanda pelo volume real por tipo |
| D57 | 27/10/2026 | **D57 — O site só lê a gold** (Caio, 27/10/2026): (1) cada gráfico lê a sua tabela ou view no `gold_monday` (8 tabelas + 8 views criadas no PPD-GOLDEN-AGENCIAMENTO-MONDAY e subidas pelo Caio; mapa página × gráfico × tabela no "Retrato do código"); (2) saem as exceções: Talentos (D30-b) e status das saídas (A26) deixam a silver 2026 e passam a `..._2026_talentos_ano`, `..._2026_talentos_ranking` e `..._2026_saidas_status`; o expediente sem almoço (C2) deixa de ser recalculado no site e vem da gold (`sla_sem_almoco_horas`, R24, e as views `..._2026_sla_entregas` e `..._sla_entregas_status`); o extrato do Início lê a view `gld_agenciamento_fila_mensal` e o quadro do Atendimento a `gld_agenciamento_atendimento_mensal`; o ML lê `gld_agenciamento_previsao_mensal`, `..._2026_previsao_exclusividade_mensal` e `..._2026_previsao_lotes` (só a sensibilidade de 2025, fora da tela, segue na silver 2025); (3) sem mudar layout, texto nem regra: código antigo × novo sobre a mesma carga real = 0 diferenças nas 21 visões; (4) `app/sql/`, a classe `Consulta`, `SQL_FIM` e 6 ferramentas da silver/plano vão para `_descartados/2026-10-27/`; revisões e auditorias externas para `docs/historico/`; a regra antiga fica só como simulação nos testes (`tests/gold_simulada.py`) | a gold é a única dona das regras; o site só agrega e mostra, como manda o item 4 do CLAUDE.md |
| D58 | 27/10/2026 | **D58 — Atendimento: "Declinados" e o % sem os declinados** (Caio, 27/10/2026): (1) "Saíram sem entrega" vira **"Declinados (Não teve seguimento)"** (quadro e faixa do topo) e o subtotal "Saiu no mês" vira **"Entregues no Mês"** (= entregues + declinados, nome pedido pelo Caio); (2) **A29** substitui a A27 na tela: % = entregues ÷ (para atender − declinados) = entregues ÷ (entregues + ficou), na linha do quadro, nos pontos da dispersão e no selo do topo (ano: 4.453 ÷ 4.617 = **96%**; meses 73–85%, antes 63–75%); (3) a faixa do topo mostra o % dos recebidos em cada número (80% · 17% · 3%). Conferido na view `gld_agenciamento_atendimento_mensal` (10 meses batem). Ficha [atendimento.md](paginas/atendimento.md), seção 00 |
| D58b | 27/10/2026 | **D58b — Atendimento: % = Entregues no Mês ÷ Para atender** (Caio, mesma tarde; revê a A29 da D58): **A30** = (entregues ao cliente + declinados) ÷ (veio do mês anterior + entrou), na linha do quadro e nos pontos da dispersão (x = para atender, y = entregues no mês); meses 77 · 80 · 76 · 78 · 81 · 80 · 87 · 87 · 79 · 78% (set = 661 ÷ 834). O selo "% do que dependia da equipe" sai da faixa do topo: cada número fica só com o % dele sobre os recebidos (80 · 17 · 3). Conferido na view `gld_agenciamento_atendimento_mensal`. Ficha [atendimento.md](paginas/atendimento.md), seção 000 |
| D59 | 27/10/2026 | **D59 — Portal com cara de apresentação** (Caio, 27/10/2026): (1) **Resultado e Qualidade ocultos da navegação** (`Secao.oculta`; menu, abas, barra do celular e sequência), código e endereço mantidos; "O que falta" segue listando as duas; (2) **sem menu lateral** no computador (`MENU_LATERAL`, padrão off; `MENU_LATERAL=on` traz de volta; no celular a gaveta "Áreas" continua); (3) **gancho para a próxima página** de volta à tela: a pergunta da página seguinte em itálico, com seta, no canto inferior direito (a D53 a deixava só para o leitor de tela); a sequência é Início → Talentos → Atendimento → SLA → **Previsão, que encerra** ("O que falta" sai da sequência); (4) **tela cheia que sobrevive à troca de página**: o botão abre o site num quadro (iframe da mesma origem) em tela cheia e a navegação acontece dentro dele; ao sair (botão ou Esc) a janela fica na página em que se estava. Para isso, `frame-ancestors 'self'` e `X-Frame-Options: SAMEORIGIN` (antes 'none'/DENY; sites de fora continuam bloqueados). Testado em Chrome: abas, gancho e saída |
| D60 | 27/10/2026 | **D60 — Capa, encerramento, nomes e setas** (Caio, 27/10/2026): (1) **capa** em `/viu-agenciamento/capa` (a raiz `/` abre nela): título "Orçamentos de agenciamento em 2026", reunião de diretoria de 28/10/2026 e o **roteiro** com as 5 perguntas na ordem (links), no painel escuro da faixa do Atendimento; o logo leva à capa; (2) **encerramento** em `/viu-agenciamento/encerramento`, última aba: "Obrigado." e "O que levamos desta reunião" (os pedidos de `pendencias.PEDIDOS`); a Previsão leva a ele pelo gancho "E o que levamos desta reunião?"; (3) **nomes**: a página inicial vira **Demanda** (aba e sequência; `rotulo_inicio`), abas Demanda · Talentos · Atendimento · SLA · Previsão · Encerramento; (4) **setas do teclado**: nas páginas de um slide, → / PageDown vão à próxima e ← / PageUp à anterior (`data-pagina-*`); no estudo "Como medimos" as setas trocam o slide e, nas pontas, voltam ao SLA. Textos em `Apresentacao.capa` / `.encerramento`; templates `capa.html` e `encerramento.html`. Testado em Chrome (setas e tela cheia) |
| D61 | 27/10/2026 | **D61 — Capa, encerramento e capas de seção no desenho do relatório de referência do Caio**: (1) **capa** com lado branco (logo, "Gestão de / orçamentos", subtítulo, "Começar", data) e plano marinho em diagonal com filete azul, onde a **jornada de um pedido** avança sozinha (`static/capa.js`: 6 etapas, 1,3–1,9 s cada, clique pausa 7 s, só com a capa visível, parada na entrega com movimento reduzido) e o medidor de horas **para no típico do SLA** (`medida_capa()`, o mesmo número da página do SLA, hoje 14 h); o roteiro numerado da D60 sai; (2) **encerramento** em marinho inteiro: "Obrigado.", próximo passo, "Dúvidas e sugestões?" e "Voltar ao início" (os pedidos ficam no "O que falta"); (3) **capa de seção** ("Parte n · página", frase, subtítulo e a pergunta da página) entre as páginas, **só pelas setas**: → mostra, → de novo entra, ← ou Esc voltam; abas, gancho e clique vão direto (`capas_secao` em apresentacao.py). (4) A cola do apresentador, feita a partir do ensaio de 27/10, é um projeto à parte: `../PPD-AGENCIAMENTO-COLA`, porta 8200 (só lê o portal) |
| D62 | 27/10/2026 | **D62 — Portal e cola do apresentador sincronizados** (Caio, 27/10/2026): o portal expõe `GET/POST /sinc` (só no computador, `config.SINC`; desligado em produção) com a página atual `{url, versao, origem}`; a versão sobe só quando a página normalizada muda (sem a query; sem o #, exceto no estudo, onde o # é o slide). `static/sinc.js` avisa a página aberta (inclusive o slide do estudo) e, a cada 600 ms, segue o que a cola pediu; em tela cheia quem sincroniza é a página dentro do quadro; página pré-carregada só avisa quando é aberta. Aceita só caminhos do próprio portal; CORS só para a cola (127.0.0.1:8200 e localhost:8200). A cola (`../PPD-AGENCIAMENTO-COLA`) faz o lado dela e foi refeita: clara, sucinta, página a página, com a fala de 2–3 minutos e o gancho para a próxima |
| D63 | 28/10/2026 | **D63 — Base congelada por padrão e falas narrativas da cola** (Caio, 28/10/2026): (1) `CONGELAR` passa a vir ligado no computador (antes só no modo apresentação): os números são os da carga lida na subida do servidor, sem recarga por hora, sem o aviso "a base não atualizou" e sem disparar a Previsão; o rodapé datado continua; `CONGELAR=false` volta a recarregar; nunca em produção. Para trocar de carga, reiniciar o servidor. (2) `gestao_orcamentos/cola.py` reescrito: as falas da cola com os números ao vivo das mesmas funções das páginas, numa linha única (demanda quase dobrou → concentrada nos exclusivos → a equipe dá conta → a mediana sai rápido, mas quem passa de 2 dias consome o tempo → é processo, em poucas etapas → a pressão continua); cadência ponte → número → leitura (insight, hipótese, pergunta) → conclusão → gancho; "mediana" no texto; mensagem, roteiro (das deixas de mouse), perguntas e "Evitar" próprios de cada página; o gancho do SLA manda abrir o estudo pela lupa (o estudo está fora da sequência das setas). Versão anterior em `_descartados/2026-10-28/` |
| D65 | 31/10/2026 | **D65 — Corte e congelamento dos dados em 31/10/2026 para a reunião de 04/11** (Caio, 31/10/2026): (1) **opção escolhida:** congelar a carga inteira da gold que fecha outubro, em vez de filtrar as linhas por data no site. `CORTE_DADOS=2026-10-31` (padrão do código, no computador e em produção; `off` desliga): cargas com fim (E3) < corte entram normalmente; a 1ª com fim ≥ corte (até `CORTE_FOLGA_DIAS`=1 depois) é a última, congela e é gravada em `app/base_congelada/` (parquet + ficha JSON com sha256 por tabela); cargas posteriores são ignoradas, sem consulta; todas as tabelas na mesma carga (regras K1–K7 em `app/congelamento.py`). (2) **Produção:** a pasta vai na imagem pelo `COPY app/` e o Cloud Run lê só dela (sem BigQuery, sem depender da permissão de leitura, página mais rápida); o `Dockerfile` passa a copiar `ml/saida/previsao.json` para o caminho padrão do `PREVISAO_ARQ`; o job de ML não roda lá. (3) **Previsão:** retrato de outubro (`python -m ml.rodar --rotina` depois da carga do corte, pelo J1 da D48); manter o de setembro deixaria outubro fora do gráfico (nem mês em andamento nem mês fechado do retrato). (4) **LIA:** `tools/extrair_lia.py --fim 2026-10-31`, rodado depois da meia-noite de 01/11. (5) **Calendário:** 31/10 é sábado e a gold só roda seg–sex; caminho A = o Caio dispara bronze → silver → gold à mão no domingo 01/11 (rodapé "Dados até 31/10/2026"); caminho B = a carga agendada de seg 02/11 (dados até 01/11, aceita pela folga). **Escolha do Caio (31/10/2026): caminho B** — base, Previsão e LIA na segunda 02/11 depois das 09:30 (feriado de Finados: conferir se a carga rodou e, se não, disparar a cadeia à mão); rodapé "Dados até 01/11/2026"; LIA com `--fim 2026-10-31` (janela própria "21/09 a 31/10", outubro completo; 01/11 só completaria a semana ISO e somaria um domingo fora do expediente); código sem mudança (folga de 1 dia). Roteiro: `docs/congelar_outubro.md`; ferramenta `tools/congelar_base.py`; testes `tests/test_corte.py` | filtrar as linhas no site refaria regra de negócio (as tabelas trazem o estado do board na hora da carga: em aberto, status atual, horas) e violaria a D57; congelar a carga inteira mantém os números iguais aos do BigQuery daquela carga (ensaio: páginas idênticas) e o Cloud Run não tem disco persistente, então a base vai na imagem |
| D56 | 26/10/2026 | **D56 — Previsão: uma série e um modelo por recorte** (Caio, 26/10/2026): (1) quatro séries, cada uma na sua tabela e com o seu modelo, sem repartição por proporção — Inbound e Mercado (gold de entradas, desde out/2024), Mercado exclusivos e Mercado não exclusivos (silver 2026, critério de `talentos_ano.sql`, jan–set/2026); filtros Todos = Inbound \| Mercado, Exclusivos = Inbound \| Mercado exclusivos, Não exclusivos = só Mercado não exclusivos (Inbound "não se aplica"); snapshots `ml/dados/serie_<recorte>.csv`; `ml/filtros.py` saiu; a silver 2025 (`talentos_exclusivos`) foi avaliada como extensão e **não entrou** (mesmo sinal que 2026, mas sem separar sem talento e com preenchimento pior; a rodada de sensibilidade não melhorou os modelos simples e trouxe um vencedor exploratório); (2) os 61 modelos nas 4 séries, régua D48 + **R7** (janela expansiva até 12 meses e mínimo de meses por modelo decidido antes; teste incompleto = "não se aplica" na série; verificação só completa): Inbound **média de 6 meses** 14,4% (robusto), Mercado **rede de 1 neurônio** 12,6% (**não robusto**: 26,8% × 24,7% da ingênua em jan–mai; alternativa robusta C5 = ARIMA com tendência 16,5%/20,4%, que prevê ainda mais alto — recomendação: manter a rede com o selo e decidir C5 com o fechamento de outubro), Mercado exclusivos **combinação de 6** 10,9% e não exclusivos **Holt simples** 19,2% (9 modelos se aplicam; sem verificação, confiança menor); (3) outubro do Mercado exclusivos (87 até 25/10 × 196 previstos, 42% abaixo do esperado): o total do Mercado está quase normal, caíram os pedidos em lote (17 × 50 no mesmo ponto do mês) e os avulsos dos talentos mais pedidos (70 × 98); 32 pedidos ainda sem talento; a série própria não corrige; (4) tela: cartões do mês vigente + 2 seguintes a partir da carga (vigente com realizado, "de N previstos", barra do ritmo e situação contra o esperado até agora = previsão × dias úteis decorridos ÷ do mês; "Por quê" com lotes e avulsos quando sai da faixa), gráfico de 2026 em cartão flutuante com o modelo e o erro, colunas em subgrid, SVG em três larguras, botão "Modelos comparados" com `<dialog>` nativo; (5) rotina completa, contrato v3, histórico PD09 com linha nova D56 do retrato de setembro (`substitui`: D48); (6) 463 testes. Ficha `previsao.md` 5.0 | o Caio quer que cada recorte seja previsto pela sua própria demanda, que a diretoria leia o mês corrente e os dois seguintes de imediato e que toda comparação de modelos esteja à mão, sem poluir a tela |
| D55 | 26/10/2026 | **D55 — Previsão: só os dois gráficos, Inbound só de exclusivos e AutoTS** (Caio, 26/10/2026): (1) a tela fica só com os gráficos Inbound \| Mercado, largos (duas colunas iguais; cada gráfico em duas larguras, 440×250 e 340×270 no celular), com o nome simples do modelo, as previsões out/nov/dez e o erro médio; saem o painel "Vale mais que o palpite simples?" e o botão "Regras e modelos" — a documentação (regras, todos os modelos, AutoTS) fica só na ficha `previsao.md` e no PRD; (2) não existe Inbound de talento não exclusivo (erro de preenchimento): "Não exclusivos" do Inbound = "Não se aplica: todo Inbound é de talento exclusivo" (sem número nem gráfico), "Exclusivos" do Inbound = o Inbound inteiro (138/mês, 14,4%), casos contados por mês (jan–set 78 de 1.194, 6,5%; out 19 até 25/10) no bloco `qualidade`, PD24 e `lembretes_gold.md`; o Mercado segue repartido pela parcela do próprio Mercado (C2); (3) re-treino com **AutoTS 1.0.4** (PyCaret exige Python ≤ 3.11) dentro da régua D48: busca em cada janela de 12 meses (19 famílias, validação interna para trás, sementes fixas, processo novo por busca, resultado reproduzível), 3 colocados por janela (`autots_1`–`_3`, nível de complexidade 6); vence o menor WAPE h1 jun–set com empate < 1 ponto = o mais simples: **Inbound média de 6 meses** (14,4%; AutoTS 15,0%, verificação 37,9% × 26,9%) e **Mercado rede neural de 1 neurônio** (12,6%; AutoTS 26,7–29,5%) — nada mudou nos números; Mercado continua não robusto (jan–mai 26,8% × 24,7% da ingênua). Ficha `previsao.md` 5.6 e 5.7; `tests/test_ml_automatico.py`; 459 testes | o Caio quer a tela limpa para a diretoria e a prova de que uma ferramenta automática não acha modelo melhor; a regra de exclusividade do Inbound corrige um filtro que mostrava erro de cadastro como se fosse demanda |
| D54 | 26/10/2026 | **D54 — SLA: rótulo curto da meta e dias úteis com fração** (Caio e gerente, 26/10/2026): (1) o rótulo da linha da meta volta a ser curto e numa linha, **"meta sugerida: 2 dias de trabalho"**, com o traço da linha; na mesa fica à direita da linha do título do cartão (sobre os meses cobria a barra de setembro e o contorno do mês parcial), no celular sobre a linha; "metade em até 2 dias de trabalho (16 h)" fica na dica e no leitor de tela; (2) **C3c**: o número de apoio passa a ser a mediana dos **dias úteis com fração** entre o pedido e a 1ª entrega ao cliente (todos os status, inclusive espera e Retorno Marca — visão do cliente; fração = horas do expediente decorridas ÷ 8 h do dia; seg–sex sem feriados), 1 casa e vírgula, com o exemplo "pedido na segunda às 10h, resposta na terça à tarde" tirado do mesmo valor; o slide 1 do estudo usa a mesma medida; o inteiro da C3b fica só no código. Carga de 26/10 (jan–set): **Todos 1,8 · Exclusivos 1,6 · Não exclusivos 2,5 dias úteis** (BigQuery = app até a 6ª casa). `app/expediente.py::dias_uteis_fracao`, `sla/calculos.py::dias_uteis_cliente`; ficha `sla.md`, seção 000000000000 | o gerente quer saber se o prazo está mais perto de 2 ou de 3 dias; o inteiro escondia isso (exclusivos: "1 dia útil" com 1,6) |
| D53 | 26/10/2026 | **D53 — Atendimento: capacidade da equipe** (Caio, 26/10/2026, em sequência no mesmo dia): (1) "Próxima pergunta" fora da tela em todas as páginas (`.so-leitor` sempre; leitor de tela e passador seguem); (2) faixa do topo com resolvido = **entregue ao cliente**: Recebidos 5.556 → Entregues 4.415 (selo **82% do que dependia da equipe**) → Saíram sem entrega 974 (dica com os status) → Em andamento 167; régua 79/18/3% pelo maior resto (E8c); (3) extrato em três blocos com subtotais — Entrada, Saída, Saldo (A24b) —, "parcial" em cima do nome do mês, ▲/▼ no que ficou (A28); (4) dica com os **status do board** das saídas sem entrega (A26, `app/sql/saidas_status.sql`, silver 2026 com as regras da gold de fluxo; exceção como a D30-b; só quando bate com a gold); (5) **taxa de capacidade** (A27) = entregues ÷ (para atender − saídas por decisão externa: Declinado pelo Mercado, Declinado pelo talento, Encerrado); Declinado Internamente e Standby ficam na base (podem ser falta de capacidade); linha única "%" (dica com a regra; cada % abre a conta), pontos da dispersão com a mesma taxa; (6) dispersão com o desenho anterior (equilíbrio 100%, corte 90%, "entregamos a mais/a menos"), eixos a partir de 0 (as duas retas saem do mesmo canto), títulos só para leitor de tela, quadro 640×400. Carga de 26/10: 65·65·63·66·68·68·75·75·63·64%; ano 4.415 ÷ 5.396 = 82%. Ficha `atendimento.md`, seção 0 | a diretoria entende "resolvido" como entregue; a pergunta é se a equipe deu conta do que dependia dela, e decisões do mercado, do talento ou encerramentos não medem capacidade |
| D52 | 26/10/2026 | **D52 — Início em dois quadrantes** (Caio, 26/10/2026): coluna da esquerda dividida em dois quadrantes. Em cima, a resposta composta como **nuvem de palavras** no padrão da frase do SLA: "Chegaram" (Plex leve) · **5.556** (Playfair grande, azul) · *pedidos de orçamento* (itálico serifado, duas linhas) · "em 2026, até 25 de outubro" (Plex leve, à direita do bloco), e como apoio (traço azul do `.f-apoio`) o selo "▲ 89% a mais que em 2025" com as barras 2026 5.556 × 2025 2.943 e "mesmo período: até 25/out" — tudo dos dados (`e.total`, `e.ano`, `e.periodo`, `e.comparacao`, `e.ate_curto`; macro `resposta` em `app/templates/macros.html`). Embaixo, a caixa cinza chapada com **altura fixa** (`max(14.2em, 219px)` = a tabela do ano): tabela de tipos ou extrato do mês, trocados no mesmo lugar com a animação de troca de sempre; o extrato ficou compacto (rótulo "Análise mensal" na linha do título, totais e barras menores, linhas justas, mesmo fundo cinza) e cabe na caixa sem mover a nuvem. O cartão do gráfico tem a altura do cartão do SLA (`min(100%, 34.25em)` com letra 0,8em; 549 × 554 px em 1850×1030), não estica, e o **pé fica alinhado ao pé da caixa cinza** (e ao pé do cartão do SLA); o topo cai no quadrante de cima (meio em cima, meio embaixo). Sombra mais funda ("flutuante"); legenda dos tipos só no topo do cartão (a legenda de baixo, reservada para o extrato, saiu e a de cima deixou de ser `aria-hidden`). Movimento segue D46/D49: nuvem pronta desde o 1º quadro, só o apoio entra num fade e as barras e colunas crescem. Nenhum número ou regra mudou | o Caio quer o Início no mesmo padrão do SLA (resposta tipográfica e cartão flutuante do mesmo tamanho), sem gráfico esticado e sem a página pular ao abrir um mês |
| D50 | 26/10/2026 | **Talentos com recorte e visão mensal (pedido do gerente do Caio; revisa a D31 e o "sem mês" da D30):** seletor Todos / Exclusivos / Não exclusivos (o mesmo do SLA, `?talentos=`) filtrando a página inteira; resposta composta como a do SLA por recorte (Todos = % do maior grupo do ano, hoje 62% exclusivos; Exclusivos / Não exclusivos = % do grupo nos 10 talentos mais pedidos do grupo, hoje 52% e 11%); barra do ano mais fina, com o grupo do recorte destacado; mapa de calor dos 10 talentos mais pedidos do recorte × jan–dez (mês do pedido = mês da data de entrada, regras R1/R2/R21; "Todos" junta os dois grupos pelo nome; meses futuros sem número; número escrito em cada célula). Regras T7–T10; `talentos_top.sql` devolve os três recortes mês a mês; dicas de top 10 da legenda retiradas | o gerente quer ver quem concentra a demanda e como ela se distribui no ano, por vínculo; a mesma leitura do SLA (seletor e resposta em destaque) reduz o esforço de quem lê |
| D51 | 26/10/2026 | **Talentos: números que contam na abertura e "corrida do ano" no botão play (Caio; exceção à D46/D49 só nesta página):** ao abrir e ao trocar o filtro, a barra do ano cresce e os % e as quantidades contam de 0 ao valor (0,6 s), com o número grande da resposta; na tabela só os números das células e do Ano contam (0,7 s), com o top 10 parado. Botão "▶ Ver a subida e descida" (vira "■ Parar") roda a corrida contínua (4,5 s; tempo do ano com easeInOutCubic, acumulados interpolados, linhas deslizando) com entrada e saída do top 10 pelo acumulado (T12: `talentos_top.sql` devolve também quem esteve entre os 10 do acumulado no fim de algum mês, coluna `pos`). Tudo numa cópia `aria-hidden` sobre a tabela, que termina idêntica ao HTML do servidor; sem JS, captura, impressão ou movimento reduzido: tabela pronta. T11: coluna dos nomes do tamanho do maior nome + ~10%, sem reticências. Tempos em `TEMPOS` (apresentacao.js). Revista no mesmo dia (automática 6–8 s → ~4 s → contínua → só no play → **play só com ícone e corrida calma**: botão redondo ▶ ↔ ■ "Parar" sem texto visível (nome e dica "Ver a subida e descida das posições ao longo do ano"), fora do cartão, na linha da legenda da barra, à direita; corrida de ~11 s mês a mês com easing e respiro, moldura no mês corrente, mês grande no canto com crossfade, células que acendem, histerese nas trocas (0,5 pedido ou 2% do líder por 340 ms) com reordenação inteira e mola sem ultrapassar, quem sobe por cima com sombra, numeração 1–10 fixa; `TEMPOS` = mes 780, respiro 260, acender 420, deslize 260, histerese 340, rotulo 380, assentar 2200) | o Caio quer mostrar à diretoria como o top 10 se formou no ano sem atrasar a leitura da página; o play deixa a animação opcional e a tabela final continua sendo a resposta |
| D49 | 26/10/2026 | **Batalha do portal (26/10/2026):** grupos de especialistas revisaram todas as páginas e um painel aprovou o que não muda regra de negócio, aplicado em três levas. **1ª leva — dados, cálculos e textos:** SLA com um só vocabulário (meta "metade em até 2 dias de trabalho (16 h)", "dias úteis no calendário" só no prazo do cliente, C3b com SQL; "típico" no lugar de "mediana"; sem o corte de 5 dias na página; selo do mês com 1 casa perto de 16 h); slide 2 do estudo em linguagem simples; glossário das telas; "O que falta" sem o marcador "X", estados "Pronta · meta a oficializar"/"Pronta · 2 decisões abertas", Resultado fora do modo apresentação; corte E3 único em `app/corte.py` (site, job, ML); job da Previsão parado com `CONGELAR`/modo apresentação; contrato do snapshot antes do retrato; PD22 e PD23. **2ª leva — interface e movimento:** números prontos desde o 1º quadro; um gesto de dado por página, até ~1,15 s, sem mola nem loop; navegação só com o voo da pílula; modo apresentação avisa dados novos; base congelada sem aviso de atraso; rodapé datado em toda rota; menu e rodapé no horário do processamento; `/regras` retirada (301); filtro de talentos nos links SLA ↔ Previsão; Previsão com o erro do teste e o da verificação; `tools/checar_reuniao.py`. **3ª leva — documentação e limpeza:** retratos da carga da reunião nas fichas, "Estado vigente" na `sla.md`, PRD com o estado atual no topo e os blocos antigos em arquivo (seção 12), decisões abertas do Caio numa tabela (9.7), `docs/HISTORICO_2026-10.md`, `checar_reuniao.py` gravando o registro da carga, teste da ficha "O que falta" contra `pendencias.py`, sobras em `_descartados/2026-10-26/` | a diretora lê o número certo no primeiro instante e cada número tem regra, SQL e carga datada; nada se mexe na frente dela sem motivo; quem retoma (Caio, Claude, Codex) começa pelo estado atual, não por camadas superadas |
| D48 | 26/10/2026 | **Previsão de demanda no protocolo do Caio** (revisa a D47): janela móvel de 12 meses; teste = h1 de jun–set/2026 (h2/h3 e a verificação jan–mai só informativos); vence o **menor WAPE** por série, empate < 1 ponto = o mais simples (referência → combinação → clássica → ARIMAX/Prophet → boosting → rede, e menos neurônios); filtros por menor erro entre repartir pela parcela dos meses anteriores à origem e prever direto (empate = repartir; candidatos da previsão direta só com parâmetros ≤ n/4); sem número com média < 30/mês ou erro > 40%; **execução mensal** (retrato quando o mês fecha; acompanhamento diário só do realizado); eixo só 2026; sem faixa do pé; pílulas sem número | critério do Caio; 2025 tem 17–25% de datas estimadas; a escolha no próprio teste é otimista e fica registrada, com a verificação jan–mai e o PD09 medindo fora dela |
| D47 | 26/10/2026 | **Previsão de demanda com números** (6 especialistas + 3 avaliadores, régua única de origem móvel jan–set/2026): métrica principal **WAPE de 1 a 3 meses à frente** (viés desempata; MAE; cobertura da faixa de 80%); **Inbound = média dos últimos 3 meses** (D20), **Mercado = ARIMA em log com nível e reta** (`arima_100_ct`); exclusivos/não exclusivos sem modelo próprio (parcela dos últimos 6 meses fechados de 2026, silver D30-b); mínimo de 24 meses (revisa a P6/D20 de 25); hipótese de fim de ano só como texto; site lê `ml/saida/previsao.json` e dispara o job em segundo plano a cada carga (nunca em produção); registro de uma previsão por carga (PD09); revisa a máscara da D30 nesta seção | ganho do ARIMA no Mercado passa no bootstrap (IC90 −12,9 a −1,0 pp) e três famílias convergem; no Inbound nenhum modelo vence além do ruído; o site não pode depender das bibliotecas de ML |
| D46 | 25/10/2026 | **Movimento do estudo do SLA** (debate de três linhas de movimento + agente que aplica): um gesto de dado por slide, na ordem de leitura; títulos, textos e números visíveis desde o 1º quadro (sem contagem); sem mola, sem loop; ≤ ~1,15 s por slide; entrada só na 1ª visita (`.revisto`, só no estudo); troca de slide direcional (View Transition no mesmo documento, moldura parada); troca de grupo sem repetir a entrada, foco de volta ao grupo pelo teclado; tudo sob `prefers-reduced-motion: no-preference` + `html.js`, `@media print` sem movimento. Fase 2 fora de 28/10 (valor antigo → novo na troca de grupo, realces, prefetch). Ficha `sla.md` seção 0000000000 | o Caio achou o estudo estático; movimento que guia a leitura sem atrasar os números |
| D45 | 25/10/2026 | **Revisão do estudo do SLA em batalha de agentes** (2 grupos × 6 especialistas, painel de avaliadores): base congelada para a reunião (`CONGELAR`), exemplo fixo `?exemplo=` (E4, só DEV/apresentação), conferência automática `tools/conferir_estudo.py` (BigQuery, só SELECT) e `tools/conferir_layout.mjs`, `_h_meta` no típico do estudo, slide 3 empilhado no celular, base dos % escrita (tempo travado ÷ todas as horas no achado 5; cartão com o limite do normal; "Onde passa mais tempo"), recorte visível (R1), escape dos nomes do Monday, cartões sem corte, cache do estudo por carga e grupo. Nenhuma regra de negócio mudou. Ficha `sla.md` seção 000000000 | proteger a reunião de 28/10 (números conferidos, nada muda ao vivo) e responder "% de quê, de quando" na tela |
| D44 | 25/10/2026 | **Slide 8 do estudo do SLA: "O que os dados nos mostraram"** (conclusão, referência do Caio). Seis achados numa linha do tempo, todos das funções dos slides 2–7 (nada fixo, mesmo grupo), com títulos e cores por regra (Z1–Z6); "Onde olhar com mais detalhe" (2 status de maior trava com pergunta de investigação + pedidos acima de 5 dias em %, Z7); "O que isso pede" (texto do Caio, Z8); sem gancho, link para o slide 1; seletor em `#8`; gancho do slide 7 → `#8`. Ficha `sla.md` seção 00000000 | fechar o estudo com o que os dados mostraram e o que pedem |
| D43 | 25/10/2026 | **Slide 7 do estudo do SLA: "Em que tipo de pedido o tempo trava?"** (referência do Caio + 2ª rodada "mais clean"). Coluna `tipo_de_input` da gold de movimentos; mesmo universo dos slides 2–6; barra 100% por tipo com a linha do geral, típico e onde mais trava; maior volume ≥ 10%; tipos < 30 pedidos em "Outros" (fora da tela); vermelho só para tipo com B ≥ geral + 3 pontos; análise só na faixa do pé; seletor em `#7`; gancho do slide 6 → `#7`. Regras J1–J9; ficha `sla.md` seção 0000000 | pedido do Caio: ver se a demora depende do tipo de pedido |
| D42 | 25/10/2026 | **Slide 6 do estudo do SLA: "Onde o tempo trava?"** (referência do Caio + 2ª rodada: sem linha explicativa, cartões compactos e alinhados). Cartões por status em 4 linhas (Entrada, Elaboração, Revisão, Entrega), % do tempo travado (**revisto em 25/10/2026 pelo Caio: tempo inteiro, no status, dos orçamentos que passaram do limite de Tukey do status**; a 1ª versão usava só o excesso), quantos travaram e típico; 2 maiores em destaque; "Outros N status"; Retorno da marca fora; "só até <mês>" para status que deixaram de ser usados; faixa do pé por regra. Universo dos slides 2–5 (o status geral "Em elaboração" e os pacotes dominam: decisão do Caio sobre jun–set ou sem pacotes). Seletor em `#6`; gancho do slide 5 ligado a `#6`. Regras K1–K8; ficha `sla.md` seção 000000 | pedido do Caio: mostrar em que ponto do ciclo o tempo trava |
| D41 | 25/10/2026 | **Slide 5 do estudo do SLA: "Foi um mês ruim, ou é sempre assim?"** (referência do Caio + 2 ajustes). Dispersão por mês com os 12 meses do ano (vazios até fechar), típico e faixa da maioria, linha de 2 dias, % que passa de 2 dias e pedidos por mês; título e faixa do pé respondendo "sazonal ou padrão da equipe?" por regra (U7: destoa = +10 pontos de B ou +4 h de típico sobre as medianas mensais; 0 padrão, 1–2 picos, 3+ sazonal — a sugestão "3+ seguidos" foi ajustada porque os não exclusivos têm 3 meses pesados fora de sequência e um só ano não separa calendário de acaso); frase do volume retirada para caber em 2 linhas. Seletor em `#5`; gancho do slide 4 ligado a `#5`. Regras U1–U9; ficha `sla.md` seção 00000 | pedido do Caio: mostrar se a demora é de um mês ruim ou do processo, e o que fazer |
| D40 | 25/10/2026 | **Slide 4 do estudo do SLA: "Para onde vai o tempo?"** (referência do Caio). Cartões "Saem em até 2 dias" / "Passam de 2 dias" com % dos pedidos (iguais ao slide 3) e % das horas da equipe (soma das horas por faixa, maior resto; HB = 100 − HA); barras 0–100; frases por regra em frações por extenso (`_fracao`: "mais da metade", "menos de um quarto", "cerca de um terço", "quase quatro quintos"); notas Prazo e Fluxo; faixa do pé na redação do Caio com variantes; gancho para o slide 5 (texto). Mesmo seletor de talentos (`#4`); gancho do slide 3 ligado a `#4`. Regras V1–V8; ficha `sla.md` seção 0000 | pedido do Caio: mostrar que os pedidos acima de 2 dias, menos da metade, concentram a maior parte do tempo da equipe; é onde está o ganho de prazo e de fluxo |
| D39 | 25/10/2026 | **Slide 3 do estudo do SLA: "De cada 100 pedidos que chegam, em quanto tempo entregamos?"** (referência do Caio). Waffle de 100 = proporção de todos os orçamentos do recorte (não sorteio); A pelo arredondamento da página (C8) para bater com o "% em até 2 dias" e o slide 2, B = 100 − A repartido pelo maior resto; curva acumulada até o P97 (múltiplo de 8 h) com marcos 2 dias / 80% / 90%; mesmo seletor de talentos do slide 2 (`#3`); faixa do pé na redação do Caio "Em uma amostra aleatória de 100 pedidos, A ficam prontos em até 2 dias de trabalho e B levam mais de 2 dias." (os 100 = proporção do total = composição esperada de uma amostra de 100; sem sorteio). Regras W1–W7; ficha `sla.md` seção 000 | pedido do Caio; a leitura "de cada 100" é a da referência, com a nota de que cada quadrado é 1% do total |
| D38 | 25/10/2026 | **Meta do SLA = metade em até 2 dias de trabalho (16 h)** (D-SLA-7, decisão do Caio; revisa a D-SLA-3). Equivale a "o típico em até 2 dias"; a tela compara a mediana exata com 16 h. Indicador ao lado, sem meta: % acima de 5 dias de trabalho (> 40 h). Estudo: "limite estatístico" para a cerca de Tukey (não é a meta), zonas rápidos/comuns/demorados/outliers em % do total, marca da meta no boxplot, tracejado do histograma = sino do meio (KDE fora da tela), Q-Q com orçamentos reais acima do teto e o ponto dos 10% mais lentos marcado, slide 1 com dias de trabalho × meta e "dias corridos", faixa do pé com uma frase por passo (regras, sem LLM; só números visíveis no gráfico; sem horas consumidas). Carga 23/10: Todos 56% em até 16 h, 12% acima de 40 h, 7% outliers (171); exclusivos 62/10/7; não exclusivos 41/16/9. Módulo M4 e ficha `sla.md` seção 00 | a meta de 75% era inatingível (melhor mês 58%); "metade em 2 dias" é simples de dizer e já é alcançada no ano por Todos e Exclusivos, não pelos Não exclusivos |
| D37 | 25/10/2026 | **Regras novas do SLA e estudo atualizado** (decisões delegadas pelo Caio, a partir da validação do cálculo; módulo M4 e ficha `sla.md` seção 0). **Validação antes das mudanças** (só SELECT, carga de 23/10 20:23:42 UTC): conta correta (2.425; 15,21 h; 52,6% ≤ 16 h); almoço correto (19 s de diferença máxima para a gold); cobertura 67% (jan–mai 42–50%), viés pequeno e conservador; censura desprezível em jan–set; o mês de entrada enviesava o mês parcial (outubro 65% ≤ 16 h × 40% por Kaplan-Meier); meta de 75% em 16 h inatingível (melhor mês fechado 58%; P75 ≈ 29 h); fila mantida (em 9% dos casos o card vai da Entrada direto ao cliente); reabertos/Standby desprezíveis; pacotes pesam na média e no P90, quase nada na mediana. **Regras:** **D-SLA-1** mês de referência = mês da 1ª entrega (gráfico, números do ano e universo do estudo; o mês fecha no dia 1º seguinte, como o Atendimento); **D-SLA-2** horas da equipe sem "Em elaboração - Retorno Marca/Executivo" (espera da marca; Cotações e validações continuam); **D-SLA-3** meta sugerida 75% em até 3 dias de trabalho (24 h), faixa nova "2 a 3 dias", título "Orçamentos prontos em até 3 dias de trabalho, por mês" (continua sugerida); **D-SLA-4** cobertura no slide 1 do estudo ("Medido em 2.348 de 3.553 orçamentos entregues no período (66%)…"); **D-SLA-5** pendências da gold (PD21, `docs/lembretes_gold.md`, `prompt_dados_pendentes.md`); **D-SLA-6** rejeitadas: tirar a fila, as Cotações ou os pacotes da base; incluir encerrados sem entrega no denominador. Com elas: só meses completos de entrega nas contas (A1); mês vigente vazado com "parcial · até dd/mm" (A2); mediana do mês sob cada coluna (A3); exemplo do dia estável por hash de data + grupo + projeto_id no fuso de São Paulo (A4). **Estudo, slide 2:** razão das metades da caixa (X4, 1,7×) no lugar do Fisher-Pearson; dois Q-Q, sino e log-normal, com aderência 0,58 · 0,99 (X5); limite do fora da curva pela regra do boxplot em escala log, 210 h (X6), zonas 25/50/24/1, marca de 5 dias (12 em 100); comparação dos grupos (X7) segue fora da tela. Itens da auditoria SLA-D01…R18 (ficha 0.1). **Resposta à diretoria (exclusivos × não exclusivos):** "Os dois grupos têm o mesmo formato; os não exclusivos levam mais tempo no geral; os casos extremos são raros e quase todos são cards de pacote" (16 × 10 em 100 passam de 5 dias; 1 em 100 fora da curva; 21 de 21 e 8 de 9 são pacotes). Tela: Todos 2.348 · 14 h · 2,8 dias · 31/25/15/29 (71%); exclusivos 1.610 · 12 h · 2,0 · 76%; não exclusivos 725 · 20 h · 4,0 · 61%; **conferida no BigQuery** (SQL 0.6.1–0.6.3: app = banco). 152 testes | a validação mostrou que a conta estava certa, mas o mês de entrada distorcia o mês parcial, o Retorno Marca é espera da marca e a meta em 2 dias não era atingível; a escala log descreve o formato real dos tempos |
| D36 | 25/10/2026 | **Correções de 25/10 em Início, Talentos e Atendimento** (itens da auditoria + decisões delegadas pelo Caio; fichas `inicio.md`, `talentos.md`, `atendimento.md` e `docs/lembretes_gold.md`). Decisões: (1) Início: título do gráfico dentro do cartão, como no SLA (tokens `--cartao-*`: raio 18 px, borda fina, sombra marinho); (2) selo e barras deixam claro que 2025 é o mesmo período ("mesmo período: até 22/out"); (3) coluna Var. com seta ▲/▼ pastel, verde na alta e vermelha na queda, número neutro — **revisa a D26** (variação em azul); "–" com base pequena; (4) parcela que arredonda a 0 com pedidos mostra `<1%`; (5) divergência entre entrada e fluxo numa safra antiga (2024/2025) só vai ao log; extrato e Atendimento só escondem se atingir o ano exibido; (6) Atendimento: "− Resolvemos (entregues)" vira "− Entregues ao cliente" e a linha do % fica "Resolvemos do que havia para atender"; (7) bloco branco do Atendimento no mesmo cartão do SLA; (8) saldo/frase e zona "▲ resolvemos a mais" ficam como sugestão; (9) virada do ano (D29) mantida e documentada; (10) Talentos: silver × gold divergentes mostram os números com aviso, em vez de bloquear; (11) empate no corte do top 10: nota "empate com mais N"; (12) talentos com dois vínculos e Squad só de exclusivos vão aos lembretes da gold; (13) textos das perguntas mantidos, tamanho do número grande não padronizado agora; (14) celular: "Próxima pergunta" e rodapé no fluxo, no fim do slide (o gráfico aparece sem rolagem interna; em páginas de vários slides, só o rodapé, ajuste da tarde). Também: rodapé pelo `_processado_em` (INI-D1); leitor de tela do mês parcial "no mesmo período" (INI-D2); mês futuro em itálico `--tinta-3` (IN-A1, também no SLA); quadro do Atendimento rolável no celular com a 1ª coluna presa, contraste ≥ 4,5:1, `out` + "parcial". Números das três páginas inalterados | auditoria antes da apresentação de 26/10: legibilidade, acessibilidade e consistência da moldura, sem mudar regras de negócio |
| D35 | 24/10/2026 | **Slide 2 do estudo "Como medimos": "A maioria é rápida. Poucos demoram muito."** (regras X1–X7, seção 9.1; ficha `sla.md` 3.2, 5.5, 6.7–6.9, 8.1). Escolhas, na ordem: (1) mesmo universo da resposta (entregues jan até o último mês completo, grupo do seletor; tempo da equipe sem almoço, C2); (2) histograma de faixas de 4 h até 60 h + "60 h ou mais", com as faixas de prazo (≤ 16 h, 16–40 h, > 40 h) no alto; (3) painel em três passos que repinta o gráfico: **assimetria** (coeficiente de Fisher-Pearson ajustado, igual ao `skew()` do pandas; mediana × média; % abaixo da média), **normalidade** (curva normal com a média e o desvio do grupo; Q-Q com 160 quantis, escala até max(maior previsto, P95) × 1,15 e "↑ ainda mais longe"), **boxplot** (Q1, mediana, Q3 lineares; limite Q3 + 1,5 × IQR; zonas rápidos / comuns / ainda normais / fora da curva em % pelo maior resto); (4) conclusão de cada passo na faixa marinho e gancho "E se olharmos para 100 pedidos, o que vemos?"; (5) layout: seletor de talentos em cima do gráfico, painel chapado (cinza-claro, filete escuro, sem sombra), passos e conclusões empilhados na mesma célula (nada se mexe ao trocar), botão do próximo passo só com o nome e largura fixa, Playfair só em títulos e números, textos encurtados; trocar o grupo mantém o passo (`?passo=N`); (6) **comparação dos grupos (X7) retirada da tela** a pedido do Caio (o painel fala só do grupo filtrado), mantida no cálculo: mesma régua de Todos (61,9 h) 7 / 6 / 10; régua própria 7 (> 62 h) / 8 (> 53 h) / 6 (> 72 h). **Conferido no BigQuery** (só SELECT, carga de 23/10 20:23:42 UTC): todos os números do slide batem nos três grupos. **Avaliação estatística** (pedido do Caio, que desconfiava da análise): a conta está certa, mas (a) os 15 maiores tempos (515 h e ~483 h) são cards "[Pacote Festival] … Rock in Rio 2026" parados ~478 h num único passo "Em Elaboração" (07/04 → 06/07); os 74 cards "[Pacote" somam 24% das horas do ano e, sem eles, a assimetria cai de 7,1 para 2,8 (mediana 15,2 → 14,8 h); o pico de 44–48 h é um lote de 32 cards Amazon com 47 h; (b) em log a assimetria é −0,2 (quase log-normal), então "não segue a normal" é esperado; (c) a cerca de Tukey marca ~7% pelo formato da cauda (numa log-normal equivalente seriam ~9–10%); em log o limite seria ~210 h, com 29 cards de fora (27 pacotes). Recomendações na ficha 8.1, **nada alterado** até decisão do Caio. 116 testes | o Caio quer ver a análise por trás da mediana e conferir cada número no banco; mostrar só o grupo filtrado mantém o painel simples |
| D34 | 24/10/2026 | **SLA redesenhado (em construção) e estudo "Como medimos".** Decisões do Caio na ordem: (1) aba "Prazo" → "SLA" (título "SLA de entrega") e página única, sem os slides de cauda (C12) e de exclusivos × não exclusivos (C13–C14), cujo cálculo `leituras()` fica no código para a próxima conversa; (2) saem da tela a linha "Leitura" (C11 só no código), o quadro "Como a meta é calculada", "No ano (jan a set):" da legenda, a nota "Medianas de N pedidos…" e "(fora do gráfico)"; (3) a resposta vira composição tipográfica: "Levamos **X h** de trabalho da equipe para entregar um orçamento ao cliente." (X = mediana C2 dos meses completos do grupo; o leitor de tela informa que é mediana) e "**Y dias** no calendário para o cliente receber" (Y = mediana C3 ÷ 24, 1 casa); (4) seletor de talentos (Todos / Exclusivos / Não exclusivos) abaixo da pergunta; gráfico em trilhos 0–100% por mês (até 1 dia, 1 a 2 dias; trilho vazio = acima de 2 dias) com meta 75% (C6), num cartão; (5) lupa em amarelo suave no canto do cartão leva ao estudo `/viu-agenciamento/sla/como-medimos` (mantém `?talentos=`); (6) estudo em slides, com Anterior/Próximo sempre visíveis, cabeçalho sem abas e botão fechar; slide 1 "Como chegamos ao tempo da equipe" com as regras novas **E1** (orçamento real sorteado por dia, semente data + grupo, entre os entregues dos meses completos com caminho limpo Entrada → Elaboração → Revisão, Aguardando Feedback encerrado e 2 a 16 h de equipe), **E2** (linha do tempo com as horas de cada etapa pela C2, que somam o tempo da equipe) e **E3** ("Para o cliente receber" = C3 arredondado; "Decisão do cliente" = dias em Aguardando Feedback, não conta); slide 2 "Exploração dos dados" em branco. Revisão do E1 no mesmo dia (Caio): exemplo **do mês vigente**, girando por dia, com espera do cliente em aberto aceita; conferido: "[Avatim] Wanessa Camargo" (outubro): Entrada 2h13, Elaboração 17 min, Revisão 8h35 = **11h04**; 2 dias para o cliente; 7 dias aguardando (em aberto); gold 12,16 h com almoço. Layout do estudo no mesmo dia: visual sóbrio (branco, como a referência), sem "1 / 2", nome do orçamento só com o nome acima da linha do tempo, regras em cartões flutuantes, faixa marinho no pé com os três números e o gancho "E nos dados do ano todo? Vamos explorar melhor." (sem botão; navegação pelo Anterior/Próximo). Primeiro exemplo conferido em 24/10 (regra anterior): "[Dove] Ludi Cianci" (Todos): Entrada 35 min, Elaboração 17 min, Revisão 4h29 = **5h21**; 1 dia para o cliente; 29 dias de decisão; na gold Σ `sla_util_horas` = 6,36 h (a gold ainda conta o almoço; exceção C2). Números da tela reconferidos no BigQuery com SQL que refaz o expediente sem almoço no banco (15,2054 / 12,5735 / 21,0961 h; 2,871 / 2,035 / 4,126 dias; 2.425 / 1.635 / 775). Memória página por página na seção 9.6 | o Caio quer ver cálculo por cálculo no banco, não na apresentação; uma resposta direta na tela e a conta explicada num orçamento real no estudo |
| D33 | 24/10/2026 | **Página Atendimento entregue em 24/10/2026.** Responde "A equipe está dando conta da demanda?" sobre os **mesmos 5.520 pedidos do Início** (carga de 23/10, dados até 22/10). Tela: faixa marinho escura, reta e baixa, com **Recebidos em 2026 5.520 → Resolvidos 5.360 (97%, arredondado para baixo) → Em andamento 160 (3%)**, os três centrados cada um no seu terço com setas entre eles, data de corte à direita após um fio ("dados até" + "22 de outubro" em Playfair branca gravada) e régua 100% com legenda centralizada (4.388 entregues ao cliente, 972 saíram sem entrega, 160 em andamento); bloco branco flutuante com dois painéis do mesmo tamanho: **quadro do extrato** com 7 linhas (Veio do mês anterior / + Entrou / = Para atender / − Resolvemos (entregues) / − Encerrados sem entrega / = Ficou para o mês seguinte, com calor em vermelho / Respondemos do que havia para atender %; A24) e **dispersão** "Quanto resolvemos do que havia para atender, em cada mês" (x = para atender, y = resolvidos; equilíbrio 100% e corte 90%; zonas "resolvemos a mais/a menos"; pontos ≥ 100% marinho, 90–99% azul claro, < 90% vermelho; outubro vazado; rótulo "mês %" sem sobreposição; um único "200" na quina; legenda curta numa linha; A16). **Regra nova A25:** % do mês = (entregues + encerrados sem entrega) ÷ para atender (represados que vieram + novos) — 77, 80, 76, 78, 81, 80, 87, 87, 79, 77; **os 10 meses ficam abaixo de 90%** (a equipe não resolve toda a demanda do mês); média (80,53%) e limite inferior natural (71,60%, XmR) testados como referência e mantidos só no código. Coreografia de entrada desligada com menos movimento. Regras: resolvidos = entregues + saídas sem entrega, só de pedidos do ano (A13); `nao_seguiu` sem mês vai ao mês de entrada (E7, 10 casos); janeiro sem represados (D29); data de entrega pela D32. Validação no BigQuery (só SELECT): quadro mês a mês igual à tela; fluxo mensal × situação da gold de entradas: 4.388 = 3.710 + 678, 972, 160 = em andamento do Início. A1–A12, A14 e A17–A23 seguem calculadas e não exibidas. Decisões do Caio em ordem, memória e limites: seção 9.5; ficha `docs/paginas/atendimento.md`. **No mesmo dia, navegação:** moldura congelada entre páginas; transições entre páginas (View Transitions); pré-carga de páginas (cabeçalho `Speculation-Rules`, `/especulacao.json`); aba "Prazo" renomeada para "SLA" (título "SLA de entrega"); Prazo reduzido a uma página só, sem botões de slide | o quadro mostra a conta inteira do represado (o que veio, o que saiu entregue, o que saiu sem entrega, o que ficou); o % sobre o que havia para atender não passa de 100% e não esconde o represado (sobre o que entrou, julho dava 103%); 100% e 90% ficam como objetivo, porque a média do próprio ano descreveria o padrão, não a meta |
| D32 | 24/10/2026 | **Data de entrega = 1ª ida a "Aguardando Feedback" pelo log; sem ela, a `data_de_saida`** (regra da gold R12–R14, mantida pelo Caio). Avaliada a ordem inversa (`data_de_saida` primeiro): mudaria 178 cards de mês e contaria o último envio nos 437 reenvios regravados pela automação. Números e motivo na seção 9.2.1. No mesmo dia, Atendimento recomeçou limpo: sem comparação com o ano anterior, sem caixa de taxas e sem dicas por mês; gráfico com a **coluna cheia = entregas do mês por tipo de input** (cores do Início, regra A9) e o **contorno tracejado atrás = entradas do mês**; legenda à esquerda no formato da tabela-legenda do Início | o log guarda a primeira entrega e não muda; a `data_de_saida` é regravada nos reenvios |
| D31 | 24/10/2026 | **Página Talentos entregue em 24/10/2026.** Responde "Como a demanda se divide entre talentos exclusivos e não exclusivos?" sobre os **mesmos 5.520 pedidos do Início** (carga de 23/10, dados até 22/10). Tela: "**62%** da demanda do ano se concentra nos talentos exclusivos." (grupo maior calculado; até 50%, "…vai para os talentos [grupo]."); barra 100% "Distribuição dos pedidos por vínculo do talento" com % e quantidade dentro de cada parte (62% · 3.435 pedidos; 36% · 1.955 pedidos; 2% · 130), cores do Início e largura mínima legível em Talento não informado; legenda com os três grupos, sem números; dicas com o **top 10** de exclusivos (281 … 120; "Juntos, 1.802 pedidos: 52% dos exclusivos") e de não exclusivos (65 … 12; "Juntos, 221 pedidos: 11% dos não exclusivos"), com a coluna "Último" (data do pedido mais recente), abertas com o mouse só pelo quadradinho da cor e pelo nome no teclado e no toque; lista oculta para leitor de tela. Regras **T1–T6** (T6 nova: top 10 por grupo, `app/sql/talentos_top.sql`). Validação no BigQuery (só SELECT): total = Início (5.520 = 5.520, também mês a mês), soma dos 39 exclusivos do ranking = 3.435, nenhum pedido exclusivo sem nome, não exclusivos 1.836 + 119 do Squad = 1.955. Fontes: silver por exceção (D30-b). Decisões do Caio na ordem, memória de cálculo, limites e pendências (PD01, PD02a, PD02b, PD03): seção 9.4; ficha `docs/paginas/talentos.md`. **Nomes de talentos na tela**: decisão do Caio, revendo a D30 (23/10), que não os mostrava. No mesmo dia, Prazo: faixas de pedidos do slide 2 alinhadas ao slide 1 (C12, seção 9.1) | a divisão da demanda e a concentração em poucos talentos são a pergunta da diretoria sobre exclusivos × intervenientes; cada número é reproduzível pela SQL da ficha |
| D30 | 23/10/2026 | **A área Orçamentos vira portal para a reunião com a diretoria** (apresentação local em 26/10, reunião em 28/10; a diretoria pediu outliers do SLA, SLA de exclusivos × intervenientes e KPIs de fechamento). Aprovadas pelo Caio as decisões D1–D5 da síntese do debate: (1) **ordem das seções** = ordem da reunião: Início → Talentos → Atendimento → Prazo (SLA) → Previsão → Resultado (negócios fechados) → Qualidade, e no fim **"O que falta"** (link no fim da última seção e no menu lateral, nunca aba); cada seção ganha `pergunta` (h2 e "próxima pergunta"), `estado` (pronta / parcial / pendente) e `na_reuniao`; (2) **máscaras visíveis**, no fim da ordem: seção sem base mostra a pergunta, o selo "Aguardando dados" (ícone + texto), o motivo e as pendências (dado · onde · quem), sem nenhum número; fonte única `gestao_orcamentos/pendencias.py` (PD01–PD18 + pedidos de decisão), que alimenta as máscaras, a página "O que falta" e o `docs/prompt_dados_pendentes.md`; (3) **Qualidade volta a ser seção** (por ora em máscara, até as verificações serem conferidas); (4) **abas do topo só com texto** (rótulos ≤ 11 caracteres: Início, Talentos, Atendimento, Prazo, Previsão, Resultado, Qualidade), **revisa a D18**: os ícones ficam no menu lateral e na barra do celular; (5) **Previsão em máscara** (o teste com meses passados passou, mas a gold reescreve o passado: falta medir o acerto carga a carga, PD09). **Modo apresentação** (`MODO=apresentacao`): só as seções `na_reuniao` (ou as de `SECOES_VISIVEIS`) aparecem em menu, abas, barra do celular e rotas (oculta = 404), e nenhuma tela com dados fictícios, mesmo com `DEV`. Talentos: só a divisão anual de 2026, **sem nomes, sem mês e sem 2025** (decisão do Caio). Prazo ganha os slides de cauda (C12) e de exclusivos × não exclusivos (C13, C14) | a diretoria quer ver o que já se sabe e o que falta, com dono; mostrar a pergunta com máscara deixa claro o pedido sem inventar número; a chave `na_reuniao` permite cortar uma tela na segunda sem mexer no código |
| D30-b | 23/10/2026 | **Exceção à regra "o site só lê gold": Talentos lê a silver 2026** (`silver_monday.slv_agenciamento_2026_itens`, `TAB_TALENTO_ORIGEM`), só para um **agregado anual** (`app/sql/talentos_ano.sql`, classe `Consulta` em `dados.py`) com as mesmas regras de data e exclusão da gold de entradas (R1, R2, R4, R5, R21) e `@fim` = véspera do `_processado_em` da gold de entradas. Concilia com o Início (5.520 = 5.520 na carga de 23/10) e, se não conciliar, a tela escreve a diferença (T5). **Motivo:** a gold de entradas não tem a exclusividade do talento; a gold do SLA tem, mas cobre só 56% dos pedidos (3.114 de 5.520, só ciclos completos) e exagera os exclusivos em ~5 pontos (67% × 62%). **Condição de saída:** a exceção termina quando a exclusividade chegar à gold de entradas (**PD01**, tabela `gld_agenciamento_entrada_talento` ou coluna na `entrada_diaria`; prompt em `docs/prompt_dados_pendentes.md`); aí `TAB_TALENTO_ORIGEM` e `talentos_ano.sql` saem e o site lê a gold nova. Antes de publicar, a conta de serviço precisaria de leitura na silver: preferível encerrar a exceção antes da fase 3 | é a única fonte que dá a divisão da demanda na mesma base do Início; a exceção é estreita (um SELECT agregado, um número, prazo de saída), como a do expediente (C2) |
| D29 | 23/10/2026 | **Decisões do Caio sobre a validação final do Início:** (1) janeiro começa com **0 represados** — a página mostra sempre o ano vigente e a fila só conta pedidos do ano (regra confirmada); (2) extratos do ano anterior **não aparecem** em janeiro (fica só o cálculo invisível `meses_extrato`); (3) o aviso das 15% estimadas de 2025 **não vai para a tela**, fica só na documentação; (4) nota de dias úteis no mês parcial: **em discussão**, nada aplicado (P4); (5) contraste aprovado: com o extrato aberto, só a coluna dos outros meses esmaece e o total do mês fica legível (`--tinta-3`, sem opacidade reduzida); (6) "Sem tipo" 2% pelo maior resto **aprovado** | a página responde sobre o ano vigente; o que é limite de dado fica documentado, sem poluir a tela |
| D28 | 23/10/2026 | **Página Início entregue em 23/10/2026.** Validação final em três camadas: gabarito extraído do próprio código com a carga real (entrada 20:23:49 UTC, fluxo 20:24:38 UTC; dados até 22/10) × gold × silver, por 4 validadores independentes com troca de base (G: gold → silver, recálculo próprio; S1, S2, S3: silver → gold; S3 simulou viradas de mês e ano) e um árbitro: 624 itens (topo, tipos, 12 meses, situações, tipos por mês, 6 extratos com fila e tabelas por mês de entrada), **0 divergências**. Correções seguras aplicadas no mesmo dia (só percentuais e acesso; nenhuma quantidade mudou): **B1** tipos no ano e no mesmo período do ano anterior pelo maior resto (2026 53/24/7/14/**2**, 2025 39/33/16/**12**/0; antes somavam 99); **B2** situação do mês pelo maior resto (jan 65/19/16/0, jun 72/10/18/0, set 63/18/19/0); **B3** extrato sem percentual por diferença (jun 67/13/20, set 62/17/21); **B5** janela do extrato = 6 meses mais recentes **com pedidos** (mês vazio no início do mês não ocupa vaga); **B6** lista de meses válidos calculada na base inteira (`meses_extrato`, atravessa anos), com a tela inalterada até decisão do Caio; **B7** extrato escondido com aviso quando entrada e fluxo são de dias de carga diferentes; **B8** carga de 01/01 mostra o ano fechado ("de janeiro a dezembro"). Checagem diária (Q1 sanidade, Q2 fila) com alarmes na ficha | os números vão para a diretoria; cada um precisa ser reproduzível por terceiros e vigiado a cada carga |
| D27 | 23/10/2026 | **Proporção ao lado da quantidade** (nunca no lugar). (a) Aba nova **Atendimento** (entre Início e SLA): entregas por mês contra as entradas, com quantidade, taxas (entregue no próprio mês, cobertura) e comparação com o ano anterior (A1–A8). (b) Início: parcela de cada tipo no ano e no mesmo período do ano anterior, lado a lado (E9; a primeira versão em "pontos" foi trocada por ser difícil de explicar). (c) Diferença de proporção em destaque só quando passa da margem de oscilação (teste z de duas proporções a 95%); diferença em pontos calculada sobre os percentuais arredondados, como escritos. Nome "Atendimento" escolhido por responder à pergunta da diretoria ("estamos atendendo a demanda?") sem jargão. Conferido com o BigQuery (seção 9.2) | quantidade sozinha mistura "chegou mais" com "entregamos melhor"; a proporção separa os dois |
| D26 | 23/10/2026 | **Página inicial sempre no ano corrente, sem seletor de ano** (vira sozinha em janeiro; `?ano=` é ignorado). O histórico entra só como comparação com o ano anterior (E8): no total, o mesmo período (1º/jan até o mesmo dia); na dica de cada mês, o mesmo mês (no parcial, até o mesmo dia). Só quando o ano anterior tem base desde janeiro: 2026 compara com 2025; 2025 não compara (2024 começa em outubro). Cor da variação: azul nos dois sentidos. Conferido com o BigQuery em 22/10: 5.520 × 2.890 (+91%); set 733 × 395 (+86%); out parcial 508 × 297 (+71%) | diretoria e equipe não navegam por anos antigos; a comparação certa vem pronta |
| D25 | 23/10/2026 | **Página inicial com uma leitura só (tipo de input) + extrato do mês** (revisão do Codex, aprovada pelo Caio): sem abas Situação/Tipo; a situação fica na dica do mês e no extrato. Extrato só nos **6 meses mais recentes** da carga; entrada dividida em "entregues no mês" e "sem entrega no mês" (com a composição na dica); saída dividida em "do próprio mês" e "de meses anteriores" (por mês/ano na dica). Fonte: `gld_agenciamento_fluxo_mensal`. Substitui D24 | menos controles na tela; extrato com base certa para entrada e saída |
| D24 | 23/10/2026 | *(substituída por D25)* **Página inicial com duas leituras do mesmo gráfico** ("Ver por: Situação \| Tipo de input"; padrão Situação). Colunas = pedidos que entraram no mês (mesma altura nas duas leituras). Situação = foto do dia da safra (colunas da gold `entregue_no_mes`, `entregue_depois`, `nao_seguiu`, `em_andamento`, saída pela 1ª entrega), com o % entregue no mês escrito na coluna dos meses fechados; título muda com a leitura ("O que acontece com os pedidos que entram?" / "De onde vêm os pedidos de orçamento?"); caixa da esquerda acompanha a leitura; dica do mês traz as duas divisões. Cores de situação: escala de azuis validada (ordinal) + "em andamento" listrado. Conferido com a gold: 2026 = 3.710 / 678 / 972 / 160; agosto 489 / 51 / 101 / 3 | retrato da área para a diretoria: o que entra e o que acontece com o que entra, sem dois números soltos |
| D17 | 21/10/2026 | Menu lateral só com as **áreas** (hoje: GESTÃO DE ORÇAMENTOS); dentro de cada área, um **navegador de seções** no topo da lâmina (hoje: SLA). Endereço `/<área>/<seção>#<slide>` (ex.: `/viu-agenciamento/sla#1`); `/sla` antigo redireciona mantendo filtros | pedido do Caio: crescer por seções dentro de cada área |
| D16 | 21/10/2026 | Construção **slide a slide com o Caio**: a imagem é referência; as regras de cálculo são definidas juntas e ficam em `app/apresentacoes/<slug>/calculos.py` com IDs (C1…) | os números precisam bater com a forma de trabalho da equipe |

## 9. Em aberto

| # | Pergunta | Quem |
|---|---|---|
| Q1 | Método de envio da caixa do Outlook (Graph ou SMTP) | Caio |
| Q2 | Domínios permitidos | Caio |
| Q3 | Indicadores e páginas da 1ª versão (proposta na seção 3.2) | Caio |
| Q4 | Páginas com dados por pessoa (`saida_por`, `orcamento`, hora extra) ficam só para admin? | Caio + gestão |
| Q5 | Identidade visual (cores/logo da área) ou visual neutro | Caio |
| Q6 | Nomes: serviço `relatorios-agenciamento`, dataset `app_relatorios`, conta de serviço `relatorios-agenciamento` | Caio confirma |
| Q7 | Data de entrada do pedido em 2026: manter a criação do card (com correção do retroativo) ou usar o campo `data_de_entrada` do board? Muda out/26 de 508 para ~463; 2024/2025 não têm o campo | Caio |
| ~~Q8~~ | *(resolvida: D26)* Comparação com o mesmo período do ano anterior no bloco do total da página inicial (ex.: 2026 até 22/10 × 2025 até 22/10), **só de 2026 em diante** (2025 não tem base comparável: 2024 começa em outubro) | Caio (proposta em 23/10) |
| ~~Q9~~ | *(resolvida: D26)* **Página inicial sempre no ano corrente, sem seletor de ano** (vira sozinha em janeiro); o histórico entra só como comparação com o ano anterior: no total (mesmo período) e no mês (mesmo mês do ano anterior), escolhendo caso a caso ano completo ou mês | Caio (proposta em 23/10) |
| Q10 | Grupo "Sem tipo" (tipo de input vazio): cresceu de 3 para 77 pedidos no mesmo período. Hoje fica sem variação na caixa do Início. Corrigir o preenchimento no board, juntar a outro grupo ou tirar da contagem? | Caio + equipe |
| Q11 | **Entradas de 2025 com data estimada:** 445 de 2.890 (15%) até 22/10/2025 não têm data de criação no board; a gold estima saída − 5 dias úteis (R2). Com elas, 2026 × 2025 = +91%; só datas reais, +126%. Elas também puxam para cima a cobertura e o "no próprio mês" de 2025. Manter (recomendado, com aviso na apresentação), excluir ou outra regra? Detalhes: `docs/paginas/inicio.md` 8.1 | Caio + equipe |

### 9.0 Pendências do Caio — validação final da página Início (D28)

| # | Decisão | Opções / contexto | Quando |
|---|---|---|---|
| ~~P1~~ | *(decidida: D29)* Fila de janeiro com 0 represados | **regra confirmada**: a página mostra sempre o ano vigente; pedidos do ano anterior não entram na fila | — |
| ~~P2~~ | *(decidida: D29)* Extratos do ano anterior em janeiro | **não mostrar** (mesma razão); só o cálculo invisível `meses_extrato` | — |
| ~~P3~~ | *(decidida: D29)* Aviso das 15% estimadas em 2025 na tela | **não colocar**; fica só na documentação (ficha 8.1, Q11) | — |
| P4 | Nota de dias úteis no mês parcial ("15 × 16 dias úteis" em out 1–22) | **em discussão com o Caio**; nada aplicado; a régua por dia corrido fica | aberta |
| ~~P5~~ | *(decidida: D29)* Contraste dos totais esmaecidos | **aprovado**: com o extrato aberto, só a coluna (`.pilha`) dos outros meses esmaece; o total (`.pilha-total`) fica em `--tinta-3` sem opacidade reduzida (`app/static/estilo.css`). A nota "meses anteriores podem mudar" (G6) segue só na documentação | — |
| ~~P6~~ | *(decidida: D29)* "Sem tipo" 1% → 2% com o maior resto (B1) | **aprovado** | — |
| P7 | Selo "parcial" em mês vazio no dia 1º | esconder ou manter | opcional |
| P8 | Snapshot mensal da fila (histórico imutável, G6) | só se quiser congelar meses passados; exige tabela nova na gold (`..._fila_fechamento`) | opcional |
| P9 | B9: régua do ano anterior exige pedido até 07/01 | comparar pela cobertura da gold (desde 2024-10-01) ou manter e só registrar (registrado na ficha) | baixa |

## 9.1 Regras da apresentação SLA (provisórias — em definição com o Caio)

Código: `app/apresentacoes/gestao_orcamentos/sla/calculos.py` (seção SLA da Gestão de orçamentos). Slide 1 "Quanto
tempo levamos para entregar um orçamento?".

> **Revisão de 25/10/2026 (D37, depois D38):** C2 (sem Retorno Marca), C4 (mês da 1ª entrega), C5 (faixa 16–24 h, retirada
> pela D38), C6 (meta 75% em até 3 dias pela D37; **metade em até 2 dias de trabalho, 16 h, pela D38, a que vale**), C7 (meses completos de entrega; parcial vazado), C8 (≤ 24 h), E1–E3, X1 e X3–X7 mudaram. As regras
> vigentes estão no módulo [M4](#m4-sla-de-entrega-e-estudo-como-medimos), item (d), e na ficha `sla.md`, seção 0.4; a
> tabela abaixo fica como registro de 21–24/10.

| ID | Regra | Decidido |
|---|---|---|
| C1 | Orçamento pronto = 1ª chegada em Aguardando Feedback | Caio, 21/10/2026 |
| C2 | Tempo com a equipe até pronto = horas úteis de todos os passos da equipe antes de C1, **inclusive Entrada** (a fila está sob controle da equipe) e **sem almoço** (10h–13h + 14h–19h); validações de talento/TM contam. Calculado no site (`app/expediente.py`, calendário conferido contra a gold em 11.681 passos) até a v2 | Caio, 21/10/2026 (revisto: primeiro tirou a Entrada, depois decidiu contar) |
| C3 | Calendário até pronto = entrada em C1 − entrada no passo 1. Cliente vê **dias corridos**; equipe, **dias úteis** (Caio). **Em aberto:** horas corridas ÷ 24 (2,9) ou diferença de datas (3; outro relatório: 2,0) | **fechada pela C3b** (dias corridos só no leitor de tela e na ficha) |
| C3b | Prazo do cliente na tela = **dias úteis no calendário** (seg–sex sem feriado) entre o pedido e a 1ª entrega; pedido depois das 19h, fim de semana ou feriado conta do próximo dia útil; mediana inteira dos meses completos. SQL e resultado na ficha `sla.md`, seção 00000000000.2 (26/10/2026: 2 / 1 / 2) | Caio, 25/10/2026 |
| C4 | Recorte: só entregues (sem entrega não dá para medir — Caio); mês = mês de **entrada do pedido** (Caio; **revisto pela D-SLA-1, 25/10: mês da 1ª entrega**); retrabalho fica fora da 1ª entrega e será medida própria (L11 na gold) | Caio, 21/10/2026 |
| C5 | Faixas: até 1 dia (≤ 8 h), 1 a 2 dias (≤ 16 h), acima de 2 dias; dia útil = 8 h (sem almoço) | Caio, 21/10/2026 (trocou 9 h por 8 h) |
| C6 | Meta sugerida: 75% ou mais em até 2 dias de trabalho (**revista:** D-SLA-3 75% em 3 dias, 25/10; **D-SLA-7/D38: metade em até 2 dias de trabalho, 16 h**, a que vale) | da referência; não oficial |
| C7 | Números do ano só com meses completos | proposta |
| C9 | Espera na fila = horas úteis (sem almoço) em Entrada antes da 1ª entrega (mediana 2,73 h). Faz parte de C2; medida à parte para slides futuros (saiu da tela do slide 1) | Caio, 21/10/2026 |
| C10 | Grupos de talento pela coluna `exclusivo`: exclusivos (TRUE, 1.636 entregues jan–set), não exclusivos (FALSE, 777); sem talento (NULL, 15) só em "Todos". Seletor no slide com a mediana de cada grupo no próprio botão (`?talentos=`) | Caio, 21/10/2026 |
| C3 (decisão) | Calendário por **horas corridas ÷ 24** (2,9), não por diferença de datas — o mesmo intervalo dá sempre o mesmo número | Caio, 21/10/2026 |
| C4 (decisão) | Base: **só a tabela gold**; projetos sem Entrada registrada ficam fora (sem premissas de início) | Caio, 21/10/2026 |
| C11 | Leitura automática (sem LLM, D2): entre os meses completos, o melhor e o pior em "até 2 dias", e o último mês comparado ao ano (acima/abaixo/igual) | Claude, 21/10/2026 |
| C8 | Arredondamento: total e "até 1 dia" direto (meio para cima); "1 a 2 dias" = total − "até 1 dia"; "acima" = 100 − total — as faixas sempre somam o escrito | Claude, 21/10/2026 (corrige fev, mar e jun, que não somavam) |
| C12 | Cauda (pedidos lentos) = mais de 5 dias de trabalho (> 40 h). Peso = parcela das horas da equipe do ano nesses pedidos; "sem a cauda" = mediana e % em até 2 dias recalculados sem eles. Faixas do slide 2: ≤ 8, 8–16, 16–24, 24–40 e > 40 h. **Pedidos:** as duas primeiras faixas seguem a C8 do slide 1 ("até 1 dia" e "1 a 2 dias"); as três de cima repartem o restante (100 − "até 2 dias" do slide 1) pelo maior resto, sobre o total de pedidos. **Horas:** as cinco faixas fecham em 100 pelo maior resto (E8c) | pedido da diretoria (outliers); Caio, 23/10/2026 (D30); arredondamento dos pedidos corrigido em 24/10/2026 |
| C13 | Exclusivos × não exclusivos ("intervenientes"): os mesmos indicadores lado a lado (pedidos, mediana, % em até 2 dias, % acima de 5 dias), grupos da C10, meses completos (C7) | pedido da diretoria; Caio, 23/10/2026 (D30) |
| C14 | Etapas dentro da C2: Fila (Entrada), Elaboração (status "Em elaboração…") e Revisão ("Em revisão…"). Os sub-status existem só desde 14/05/2026: leituras por etapa só de junho em diante (`MES_ETAPAS`); mediana da elaboração só entre quem passou por ela | Claude, 23/10/2026 (D30) |
| E1 | **Estudo — exemplo do dia, do mês vigente** (revisto pelo Caio em 24/10/2026): um orçamento real **do mês vigente** (mês de entrada = mês da carga, o parcial), para o exemplo ser sempre atual e girar, sorteado uma vez por dia (`random.Random("AAAA-MM-DD:grupo")` sobre os `projeto_id` ordenados do mês), do grupo (C10), já com a 1ª entrega (C1, C4), tempo da equipe entre 2 e 16 h (inclusive) e caminho limpo até a 1ª entrega: passos antes de C1 todos `equipe`, com `saida` e etapa conhecida (C14), 1º = Entrada, ordem Entrada → Elaboração → Revisão sem voltar, com Elaboração. O Aguardando Feedback **pode estar em aberto** (linha do tempo termina em "até dd/mm · em aberto"; "Decisão do cliente" conta até a carga, com "ainda aguardando"). Prefere o 1º sorteado com Revisão. Sem candidato no mês vigente, volta mês a mês. Versão anterior (24/10, manhã): meses completos e Aguardando encerrado | Caio, 24/10/2026 (D34) |
| E2 | **Estudo — linha do tempo:** início de cada etapa (passos seguidos da mesma etapa somados), a 1ª versão ao cliente (C1) e o passo seguinte ao Aguardando Feedback; horas de cada etapa pela C2 (sem almoço), que somam o tempo da equipe do projeto | Caio, 24/10/2026 (D34) |
| E3 | **Estudo — números:** "Para o cliente receber" = dias corridos da C3 arredondados; "Decisão do cliente" = dias corridos em Aguardando Feedback (C1 → passo seguinte), arredondados, só ilustrativo (não conta) | Caio, 24/10/2026 (D34) |
| X1 | **Estudo, slide 2 — universo:** entregues (C1, C4) dos meses completos do ano (C7), no grupo do seletor (C10); medida = tempo da equipe sem almoço (C2). Menos de 30 no grupo: aviso no lugar dos gráficos | D35, 24/10/2026 |
| X2 | **Histograma:** faixas de 4 h (0,4], (4,8], …, (56,60] e > 60 h; 0 h na 1ª faixa | D35 |
| X3 | **Faixas de prazo:** ≤ 16 h (C5), 16–40 h, > 40 h (C12), em % pelo maior resto; mais o maior tempo do grupo | D35 |
| X4 | **Assimetria:** média, mediana, % com h < média (meio para cima) e coeficiente de Fisher-Pearson ajustado (pandas `skew()`): n ÷ ((n − 1)(n − 2)) × Σ((h − média) ÷ desvio amostral)³; "Assimetria positiva" se > 0,5 | D35 |
| X5 | **Normalidade:** curva normal com a média e o desvio amostral do grupo na escala das barras; Q-Q com 160 quantis (p = (k − 0,5)/160), escala até max(maior previsto, P95) × 1,15; "Não." se o módulo do coeficiente passa de 1 (regra prática, não teste) | D35 |
| X6 | **Boxplot:** Q1, mediana, Q3 lineares (= `PERCENTILE_CONT`); limite = Q3 + 1,5 × (Q3 − Q1); zonas ≤ Q1, (Q1, Q3], (Q3, limite], > limite em % pelo maior resto; "dentro do normal" = 100 − fora | D35 |
| X7 | **Comparação dos grupos:** % acima do limite de Todos e % acima do próprio limite (meio para cima). **Fora da tela** desde 24/10 (Caio), segue em `exploracao()["comparacao"]` | D35 |

**Tela de 24/10/2026 (D34):** usa C1–C8 e C10 (resposta, seletor, legenda do ano e trilhos por mês); C11 e C12–C14
ficam calculadas, fora da tela; E1–E3 e X1–X6 só no estudo "Como medimos" (X7 calculada, fora da tela). Memória de cálculo, colunas e SQL de cada número:
seção 9.6 e ficha [sla.md](paginas/sla.md) (seções 1.1, 5 e 6).

**Reconferência de 24/10/2026** (mesma carga de 23/10 20:23:42 UTC; SQL 6.2 da ficha, expediente sem almoço refeito
no BigQuery por interseção de janelas): Todos 2.425 · 15,2054 h (15 h) · 2,8710 dias (2,9) · ≤ 8 h 693 · ≤ 16 h 1.276
(29/24/47%); exclusivos 1.635 · 12,5735 h (13 h) · 2,0352 dias (2,0) · 35/25/40%; não exclusivos 775 · 21,0961 h (21 h) ·
4,1258 dias (4,1) · 16/22/62%. Com a coluna da gold (`sla_util_horas`, com almoço): 17,18 / 14,00 / 23,86 h e 46,89% em
até 16 h (52,54% em até 18 h): a diferença é o almoço, que a gold ainda conta (exceção C2, até a v2).

**Revalidação de 23/10/2026** (carga 20:23 UTC, 14.873 linhas): tela × SQL independente no BigQuery × `tools/auditar_relatorio.py`
batem **exatamente** (2.425 pedidos jan–set; mediana 15,2054 h; 53%; 2,871 dias; exclusivos 1.635 · 12,57 h; não exclusivos
775 · 21,10 h). A base de 21/10 (2.428) mudou pela R1 da gold: 4 projetos voltaram para a equipe e saíram, 1 voltou a
Encerrado e entrou. Slides 2 e 3: cauda = 15% dos pedidos e 54% das horas; sem ela, 13 h e 62%; elaboração jun–set 3 h ×
18 h. Detalhe e SQL: `docs/paginas/sla.md` (seções 5–7).

**Correção de 24/10/2026 (arredondamento do slide 2, C12):** "até 1 dia" aparecia como **29%** no slide 1 (C8: 693 ÷ 2.425 = 28,58% → 29) e **28%** no slide 2 (as cinco faixas eram repartidas juntas pelo maior resto). Agora `leituras()` usa `_faixas(h)["tela"]` nas duas primeiras faixas (29 e 53 − 29 = 24) e reparte os 47 pontos restantes entre 2–3, 3–5 e > 5 dias pelo maior resto (`_pcts(..., alvo=47, total=2.425)`: 15,71 / 16,78 / 14,89 → **15 / 17 / 15**). Resultado: **29 / 24 / 15 / 17 / 15** = 100, os dois slides com os mesmos números; a cauda continua 15% dos pedidos e 54% das horas. Horas sem mudança (4 / 11 / 12 / 19 / 54). Detalhe: `docs/paginas/sla.md`, seção 5 (slide 2).

Resultado em 21/10/2026 (jan–set, 2.428 entregues), regras atuais (com Entrada, sem almoço): mediana **15,2 h** com
a equipe (tela: 15 h); 2,9 dias corridos; **53%** dentro de 2 dias (16 h). Conferência (`tools/conferir_entrega.py`):
com almoço, o site dá 17,19 h e 52,5% em até 18 h — igual ao BigQuery. Variante sem Entrada (descartada): 8,75 h e 68%.

**v2 (quando a gold for atualizada pelo Caio):** a gold passa a separar a espera na fila (Entrada, L10) e a descontar o
almoço; o retrabalho ganha medida própria (L11). Aí o site deixa de recalcular (`app/expediente.py` sai) e lê as
colunas novas direto da gold; conferir que os números da tela não mudam.

Validação da tela (21/10/2026, 1440×900): os 10 meses, a legenda, "Hoje: 68%", "9 h" e "2,9 dias" batem com o
cálculo; faixas somam o total; altura das barras = percentual (±1 ponto); "2,9 dias" conferido de forma independente
no BigQuery (mediana 68,96 h corridas = 2,8733 dias, 2.428 projetos, nenhum negativo).

Por grupo (jan–set, regras atuais, com Entrada): exclusivos **13 h** com a equipe, não exclusivos **21 h**; calendário
2,0 × 4,1 dias corridos. (Sem Entrada, descartado: 6,2 h / 15,6 h; conferido então com o BigQuery: 7,12 h / 17,49 h
com almoço.)

Ponte com o outro relatório (13 h / 2 dias / 59%), na base gold: com as regras dele (Entrada conta, 8 h/dia) daria
15,2 h e 53%; a diferença restante vem da base (2.963 × 2.428 projetos: recuperados do log da ViU2 e 941 por premissa
de início = criação do item) e da foto de 29/09. Calendário: pela diferença de datas a base gold dá 3 (47% em até 2
datas — a mediana está na fronteira entre 2 e 3).

## 9.2 Memória de cálculo — página inicial (E8, E9) e Atendimento (A1–A8)

Fonte de tudo: `gold_monday.gld_agenciamento_entrada_diaria` (uma linha por dia × grupo × tipo × família). Código:
`entrada/calculos.py` (E), `atendimento/calculos.py` (A), `app/estatistica.py` (teste). Testes com valores à mão:
`tests/test_atendimento.py`. Números de exemplo: carga de 23/10/2026 (cobertura até 22/10), conferidos no BigQuery.

| ID | Regra | Fórmula | Exemplo (2026 × 2025) |
|---|---|---|---|
| E0 | Ano mostrado | ano da carga (`_processado_em` em São Paulo − 1 dia); sem seletor | 2026 |
| E8 | Comparação com o ano anterior | só se o ano anterior tem base desde 07/jan; mesmo período = 01/jan até o mesmo dia; mês parcial = até o mesmo dia | entradas 5.520 × 2.890 = **+91%** |
| E8b | Variação em % e frase (relatório vivo) | variação = atual ÷ anterior − 1, **só com ao menos 30 no ano anterior** (vale para o total, cada mês, cada tipo e a linha de total da tabela; também A7); abaixo disso, só o número de referência ("Em 2025 · 12 no mesmo período"). Na tela, o percentual é arredondado meio para cima **antes** de escolher sinal e frase: > 0 "▲ X% a mais que em AAAA"; < 0 "▼ X% a menos…"; = 0 "igual a AAAA" (exato) ou "praticamente igual a AAAA" (diferença que arredonda a 0). Tabelas usam o menos tipográfico (−13%) | +0,3% → "praticamente igual"; −0,4% → nunca "-0%"; 5.520 × 2.890 → "▲ 91% a mais que em 2025" |
| E4 | Período do número | ano em andamento: "até D de mês"; ano fechado: "de janeiro a dezembro"; base que começa no meio do ano: "de mês a dezembro" ou "de mês até D de mês". O ano fica no título; o texto sai pronto do cálculo | "pedidos até 22 de outubro" |
| E9 | Composição contra o ano anterior | por tipo, no mesmo período: pedidos e parcela (pedidos do tipo ÷ pedidos do ano) nos dois anos; variação = pedidos do ano ÷ pedidos do ano anterior − 1, **só se o ano anterior tiver pelo menos 30 pedidos do tipo** (abaixo disso, "–"); total = topo (E8). Sem "pontos" (decisão do Caio) | Mercado 2.945 (53%) × 1.134 (39%) = **+160%**; Inbound 1.322 × 955 = +38%; Internos 769 × 330 = +133%; Proativo 407 × 468 = −13%; Sem tipo 77 × 3 = "–"; total 5.520 × 2.890 = +91% |
| A1 | Entregas do mês | Σ `quantidade_saida` com data no mês (1ª entrega) | ano: **4.391** × 2.294 = **+91%** |
| A2 | Do próprio mês / de meses anteriores | próprio = Σ `entregue_no_mes` da safra do mês; anteriores = A1 − próprio | set: 515 = 460 + 55 |
| A3 | Entradas do mês | Σ `quantidade` + `quantidade_estimada` | set: 733 |
| A4 | Cobertura | A1 ÷ A3 (pode passar de 100%) | jan–set: 3.972 ÷ 5.012 = **79%** × 1.962 ÷ 2.593 = 76% → **+3 pontos** (sem teste) |
| A5 | Entregue no próprio mês | A2 ÷ A3 | jan–set: 3.424 ÷ 5.012 = **68%** × 1.505 ÷ 2.593 = 58% → **+10 pontos** (relevante) |
| A6 | Período das taxas do ano | só meses completos (jan até o mês anterior ao parcial), nos dois anos; quantidades até o último dia da carga | taxas jan–set; quantidades até 22/10 |
| A7 | Mês contra o mesmo mês do ano anterior | quantidade; no mês parcial, até o mesmo dia e sem taxas | set: 515 × 311 = +66%; no próprio mês 63% × 62% = +1 ponto (dentro da margem) |
| A8 | Diferença "relevante" | teste z de duas proporções, variância combinada, bilateral 95%: p = (x1+x2)/(n1+n2); erro = √(p(1−p)(1/n1+1/n2)); z = (p1−p2)/erro; relevante se \|z\| ≥ 1,96. Só para proporções (A5, E9), nunca para A4 | A5 do ano: z = 8,89 → relevante; set: z = 0,33 → oscilação; E9 Mercado: z = 12,30 → relevante |

**Limites conhecidos:** (1) 2025 usa a data de saída do campo do board (sem log): um reenvio pode ter movido a data, então
a régua de entregas de 2025 é um pouco menos precisa que a de 2026. (2) "Entregue no próprio mês" é foto do dia: um pedido
de setembro entregue em outubro deixa de contar como "no próprio mês" e passa a "de meses anteriores" em outubro.
(3) A cobertura não desconta pedidos declinados ou parados (saída sem entrega); isso fica para a medida de fila
(encerrados sem entrega por mês, só 2026), ainda não implementada.

### 9.2.1 Regra da data de entrega (D32, 24/10/2026)

**Regra (gold, R12–R14, mantida por decisão do Caio):** a entrega do orçamento é a **1ª entrada do card em "Aguardando
Feedback"**, lida no log de status da silver 2026 (`slv_agenciamento_2026_log`, `campo_alterado = 'Status'`,
`valor_depois = 'Aguardando Feedback'`, menor data). Sem essa passagem no log, vale a `data_de_saida` do card. Data que
cai antes da entrada do card (criação ou, no cadastro retroativo, `data_de_entrada`, R21) não vale. É essa data que vira
`quantidade_saida` na gold de entradas e alimenta o Atendimento (A1, A9), o extrato do Início e, no SLA, o fim do
relógio (C1).

**Por que o log vem antes da `data_de_saida`:** a automação do monday regrava a `data_de_saida` a cada nova ida ao
cliente; o log guarda a primeira, que não muda depois.

**Conferência no BigQuery (24/10/2026, só SELECT, cards ativos do board 2026):** 4.201 têm as duas datas; 3.582 (85%) são
iguais; 437 têm a `data_de_saida` **depois** da 1ª ida a "Aguardando Feedback" (reenvio regravado); 182 têm a
`data_de_saida` **antes** (possível correção manual); 178 cairiam em outro mês se a ordem fosse invertida. 220 cards só
têm `data_de_saida` e 3 só têm o log: seguem a mesma data nas duas ordens.

**Alternativa avaliada e não adotada:** `data_de_saida` primeiro (digitada pelo usuário) e o log só quando ela falta. Foi
descartada porque contaria o último envio em vez do primeiro nos 437 casos de reenvio. Se a equipe passar a corrigir a
data à mão com frequência (os 182 casos), reavaliar com exemplos.

## 9.3 Validação em três camadas — página inicial (23/10/2026)

Feita por dois agentes independentes, só com consultas (SELECT). Gold processada em 23/10/2026 20:23 UTC (dados até
22/10).

| Número da tela | Gold | Silver (regras da gold) | Bronze | Situação |
|---|---|---|---|---|
| Entradas 2026 / 2025 (mesmo período) | 5.520 / 2.890 | igual (2.890 = board 2025 2.879 + board 2024 8 + board 2026 3) | 2025 igual à silver; 2026 sem item faltando | ✅ (3 duplicados em 2025, F7) |
| Por tipo e por mês (2026 e 2025) | tela | 91 combinações, 0 diferenças | — | ✅ |
| 445 estimadas de 2025 | 445 | 725 sem criado_em; 576 com saída; 445 no período | mesmos 725; `created_at` = importação | ✅ regra; data real indisponível (F10) |
| Extrato out: 173 + 508 = 681 = 419 (286 + 133) + 102 + 160 | igual | igual, item a item | log da bronze ⊂ silver | ✅ (10 dos 508 e dos 102 são o F8) |
| Extrato set: 101 + 733 = 834 = 515 + 146 + 173 | igual | igual | — | ✅ |
| Dica dos represados de outubro (por mês de entrada) | igual | igual | — | ✅ |
| Entregas 2026 / 2025 | 4.391 / 2.294 | 4.425 / 2.297 por `data_de_saida` | — | ✅ conciliado: 4.425 − 13 excluídos − 27 saídas antes da entrada (duplicados) + 3 com log sem data + 1 regravada + 2 do board 2025 = 4.391; 2.297 + 11 (board 2024) − 14 (saída antes da criação) = 2.294 |

**Validação final de entrega (23/10/2026, D28):** 4 validadores (G gold → silver; S1, S2, S3 silver → gold) e um árbitro
conferiram 624 itens do gabarito extraído do código: gabarito = gold = silver em 100% (0 divergências). Achados novos da
gold: G2 (status de "não seguiu" sem corte em `fim`), G3 (lista fixa de boards; 2027 não entra), G4 (43 cards de setembro
contados em outubro, a confirmar), G6 (meses passados mudam a cada carga), G9 (sem filtro de `state` em 2024/2025); G1
(= F8) com efeito medido. Detalhe: `docs/lembretes_gold.md` e `docs/paginas/inicio.md` (seções 7 e 8).

Pendências que mudam números (levar à gold e à equipe): F7 (−3 em 2025), F8 (outubro 508 → 498; saíram sem entrega
102 → 92), F9 (regra de entrega para Encerrado/Declinado com data de saída), F10 (comparação entre anos). Consultas
completas: relatórios dos agentes, resumidos nas fichas `docs/paginas/inicio.md` e `atendimento.md`.

## 9.4 Página Talentos entregue (D31, 24/10/2026)

Código: `app/apresentacoes/gestao_orcamentos/talentos/calculos.py` (`divisao()`, `top_por_grupo()`), `template.html`,
`apresentacao.py` (`montar_talentos`), `app/sql/talentos_ano.sql`, `app/sql/talentos_top.sql`, `app/dados.py` (`Consulta`,
`talentos`, `talentos_top`, `_fim_da_entrada`), `app/static/estilo.css` (blocos "Talentos (D30)" e "T6"). Teste:
`tests/test_portal.py` (`test_talentos_divisao_sem_nomes`). Ficha auditável: [talentos.md](paginas/talentos.md).

### 9.4.1 O que a página responde

"Como a demanda se divide entre talentos exclusivos e não exclusivos?" — de cada 100 pedidos de 2026, quantos foram para
talentos exclusivos, quantos para não exclusivos e quantos estão sem talento informado, sobre a mesma base do Início; e,
dentro de cada grupo, quais talentos concentram a demanda. Sem mês e sem 2025 (D30).

### 9.4.2 Elementos da tela (carga de 23/10/2026, dados até 22/10)

| Elemento | O que mostra |
|---|---|
| Título | a pergunta (h2, Playfair; padrão do portal) |
| Número e frase | "**62%** da demanda do ano se concentra nos talentos exclusivos." O grupo é o maior entre exclusivos e não exclusivos; até 50% a frase vira "X% da demanda do ano vai para os talentos [grupo]." O número conta na entrada |
| Conciliação | só se o total diferir do Início: "A base de talentos ainda não tem os mesmos pedidos do Início (N): as bases atualizaram em horários diferentes." (não aparece nesta carga) |
| Barra 100% | "Distribuição dos pedidos por vínculo do talento": três partes em HTML com o % e, embaixo, a quantidade: 62% · 3.435 pedidos; 36% · 1.955 pedidos; 2% · 130. Cores do Início (`--t-mercado`, `--t-proativo`, `--t-sem-tipo`); larguras pelo `<style nonce>` (CSP); Talento não informado com largura mínima legível (desproporção visual consciente, pedido do Caio) |
| Legenda | uma linha com cor e nome dos três grupos (Exclusivos, Não exclusivos, Talento não informado), sem números |
| Dicas (T6) | pelas legendas de Exclusivos e Não exclusivos: com o mouse, **só pelo quadradinho da cor** (o nome é texto comum, sem sublinhado); pelo teclado, o nome é focável (Tab) e abre a dica; no toque, o nome abre e fecha; Esc fecha. Classe própria (`dica-top`, sem a genérica `dica-tipos`). Abrem acima da legenda e sobre a barra, alinhadas à direita, no padrão da dica "Novos pedidos" do Início: título "Os 10 [grupo] mais pedidos", duas colunas (1º–5º e 6º–10º) com Talento · Pedidos · Último, largura do maior nome + 10%, fechamento "Juntos, N pedidos: X% dos [grupo]"; nos não exclusivos, a nota "Nomes como registrados no board; Squad de Talentos (grupo) fora" |
| Leitor de tela | lista oculta com os três grupos, pedidos e %; a barra é `aria-hidden` |
| Animação | as partes da barra se revelam da esquerda para a direita junto com a contagem; só com `prefers-reduced-motion: no-preference` |
| Rodapé | "Dados até … · atualizados em …" |

### 9.4.3 Regras

| ID | Regra | Fórmula |
|---|---|---|
| T1 | Base = os mesmos pedidos do Início | silver 2026, `state = 'active'` (R5); dia = `data_de_entrada` se cadastro retroativo (R21), senão `DATE(criado_em)` (R1); sem `criado_em` = `data_de_saida` − 5 dias úteis (R2); de 1º/jan até `@fim` = véspera do `_processado_em` da gold de entradas (R4) |
| T2 | Exclusividade na data do pedido; sem talento = grupo próprio ("Talento não informado") | `COALESCE(exclusivo, IF(criado_em IS NULL AND talentos_exclusivos IS NOT NULL, TRUE, NULL))`: TRUE / FALSE / NULL |
| T3 | Squad de Talentos é grupo, não pessoa | conta em não exclusivos (regra 60 da silver); fora do ranking |
| T4 | Parcelas e frase | `_pcts` (E8c): piso de n × 100 ÷ total + pontos que faltam aos maiores restos; `principal` = maior n entre exclusivos e não exclusivos; pct > 50 → "se concentra nos talentos"; senão "vai para os talentos" |
| T5 | Conciliação com o Início | `diferenca` = total da divisão − total do Início; ≠ 0 → aviso, sem esconder o número |
| T6 | Top 10 por grupo | agrupa por `LOWER(TRIM(talento))`, grafia mais frequente (`APPROX_TOP_COUNT`); `n` = pedidos; "Último" = `MAX(dia)` pela regra da T1; 10 maiores `n`, empate alfabético; soma dos 10 e `round(100 × soma ÷ total do grupo)`, com o total do grupo vindo da divisão |

### 9.4.4 Memória de cálculo (fim = 22/10/2026)

1. **Recorte:** `@fim` = 22/10/2026 (gold de entradas processada em 23/10 20:23 UTC); silver processada em 23/10 11:05 UTC.
2. **Base:** silver ativa com data pela R21/R1 em 01/01–22/10 = 5.515, + 5 cards com data estimada (R2) = **5.520** = gold
   `entrada_diaria` (`quantidade + quantidade_estimada`), igual também mês a mês (jan 374 … out 508).
3. **Divisão:** exclusivos **3.435**, não exclusivos **1.955** (inclui 119 do Squad), talento não informado **130**.
   Exclusividade na data do pedido preenchida em 5.385 + 5 completados pela T2 = 5.390 (**cobertura de 97,6%**).
4. **Parcelas (T4):** 62,23 / 35,42 / 2,36 → bases 62 / 35 / 2 = 99; o ponto que falta vai ao maior resto (0,42) →
   **62 / 36 / 2**.
5. **Frase:** maior grupo = exclusivos; 62 > 50 → "62% da demanda do ano se concentra nos talentos exclusivos."
6. **Top 10 exclusivos (T6):** 39 nomes, somando 3.435 (nenhum pedido exclusivo sem nome). Pedidos: 281 / 242 / 206 /
   189 / 186 / 172 / 151 / 130 / 125 / 120 = **1.802**; 1.802 ÷ 3.435 = 52,46% → **52%**. "Último" entre 20/10 e 22/10.
7. **Top 10 não exclusivos (T6):** 1.955 − 119 do Squad = 1.836 pedidos em 928 nomes (depois de agrupar maiúsculas e
   espaços; mostrados na grafia mais frequente). Pedidos: 65 / 33 / 23 / 18 / 16 / 14 / 14 / 14 / 12 / 12 = **221**;
   221 ÷ 1.955 = 11,30% → **11%**. "Último" entre 10/06 e 22/10.

### 9.4.5 Fontes

- `app/sql/talentos_ano.sql` (divisão) e `app/sql/talentos_top.sql` (top 10), ambos sobre
  `silver_monday.slv_agenciamento_2026_itens` (`TAB_TALENTO_ORIGEM`), com `@fim` de `_fim_da_entrada()`.
- **Exceção D30-b** (a regra é ler só gold): a gold de entradas não tem a exclusividade; sai com a PD01 (e o ranking dos
  exclusivos com a PD02a). Antes da fase 3, preferível encerrar a exceção (a conta de serviço precisaria ler a silver).

### 9.4.6 Validações

| Data | O quê | Resultado |
|---|---|---|
| 23/10/2026 | Divisão (silver) × total da gold de entradas, também mês a mês | ✅ 3.435 + 1.955 + 130 = 5.520 = Início |
| 23/10/2026 | Exclusividade silver × gold do SLA (passo 1), por `projeto_id` | ✅ idêntica nos 3.114 projetos em comum |
| 24/10/2026 | Top 10 no BigQuery (SELECT, `@fim` = 22/10), sem expor nomes | ✅ soma do ranking dos exclusivos = 3.435; 0 pedidos exclusivos sem nome; não exclusivos 1.836 + 119 = 1.955; top 10 = 1.802 (52%) e 221 (11%) |
| 24/10/2026 | `test_talentos_divisao_sem_nomes` e suíte completa | ✅ 89 testes |

### 9.4.7 Limites

- **Silver:** a página depende da exceção D30-b e de horários de carga diferentes da gold (a conciliação T5 avisa).
- **Grafias dos não exclusivos:** o agrupamento junta só maiúsculas e espaços; apelidos, acentos e erros continuam
  separados (928 nomes), o que pode subestimar um talento no top 10 (PD02b; a dica avisa).
- **Squad de Talentos:** 119 pedidos em não exclusivos, fora do ranking; o % do top 10 é sobre os 1.955.
- **Barra não exatamente proporcional:** largura mínima em Talento não informado; os números escritos são os exatos.
- Conta pedidos, não contratações nem receita; não compara com 2025 (PD03); os 62% não "batem" com os 67% de exclusivos
  do Prazo (outra base: só entregues com histórico).

### 9.4.8 Pendências

| Código | O quê | Quem |
|---|---|---|
| PD01 | Exclusividade do talento na gold de entradas (encerra a D30-b; abre a divisão por mês) | Caio (gold) |
| PD02a | Ranking dos exclusivos lido da gold (hoje a dica lê a silver) | Caio (gold) |
| PD02b | Cadastro limpo de talentos não exclusivos (padronizar grafias; ranquear com mínimo de 10 pedidos) | Equipe de Talentos |
| PD03 | Lista de exclusivos de 2025 com vigência (comparação com o ano anterior) | Equipe de Agenciamento |

### 9.4.9 Decisões do Caio em 24/10/2026, em ordem

1. Tirar o bloco "Aguardando dados", para a tela ficar limpa.
2. Resposta direta, sem números fixos: o grupo maior é calculado. Texto desta etapa: "X% dos pedidos do ano foram para
   talentos [grupo]: a maior parte da demanda." (acima de 50%; abaixo, "o maior grupo da demanda").
3. Revisão de textos aprovada: "Talento não informado"; título do gráfico "Distribuição dos pedidos por vínculo do
   talento". O título da página continua em pergunta (padrão do portal); a fonte Playfair foi mantida.
4. Cores da página Início (`--t-mercado`, `--t-proativo`, `--t-sem-tipo`), mais respiro abaixo da pergunta e barra
   modernizada: HTML com o % dentro de cada parte e larguras pelo `<style>` com nonce. Animação de entrada coordenada:
   as partes se revelam da esquerda para a direita junto com a contagem e as linhas sobem em sequência, respeitando o
   pedido de menos movimento.
5. Dica com o top 10 de exclusivos; depois a coluna "Último"; por fim, o top 10 de não exclusivos.
6. Padrão da dica "Novos pedidos" do Início: abre acima da linha, alinhada à direita, em duas colunas (1º–5º e 6º–10º),
   largura igual ao maior nome mais 10%, sem esticar; fecha com "Juntos, N pedidos: X% do grupo".
7. Tirar a etiqueta de período "jan–out 2026" da tela e da dica: o recorte já está claro na reunião.
8. Nomes de talentos na tela, revendo a decisão de 23/10 (D30) que não os mostrava.
9. Ajustes finais: (a) frase "X% da demanda do ano se concentra nos talentos [grupo]." (até 50%: "X% da demanda do ano
   vai para os talentos [grupo]."), substituindo a do item 2; (b) dentro de cada parte da barra, o % e, embaixo, bem
   pequeno, a quantidade de pedidos, com largura mínima legível na parte de Talento não informado ("2%" e "130");
   (c) a lista com números sai: embaixo da barra fica uma legenda de uma linha com cor e nome dos três grupos, sem
   números (Talento não informado chegou a sair da legenda e voltou); as dicas de top 10 abrem só pelas legendas de
   Exclusivos e Não exclusivos, acima delas e sobre a barra; lista oculta para leitor de tela com grupos, números e %.
   A animação das linhas do item 4 saiu junto com a lista.
10. Último ajuste: com o mouse, a dica abre só pelo quadradinho da cor na legenda; o nome vira texto comum, sem
    sublinhado. Pelo teclado, o nome segue focável (Tab) e abre a dica; no toque, o nome abre e fecha. A dica deixa a
    classe genérica `dica-tipos`. **Com este estado, o Caio deu a página como ENTREGUE.**

## 9.5 Página Atendimento entregue (D33, 24/10/2026)

Código: `app/apresentacoes/gestao_orcamentos/atendimento/calculos.py` (`atendimento()`, `fluxo_mes()`, `analise_ritmo()`),
`template.html`, `apresentacao.py` (`montar_atendimento`, `_mesma_fotografia`), `app/static/estilo.css` (blocos `.kpi`,
`.ritmo`, `.quadro`, "coreografia de entrada do Atendimento"), `app/static/apresentacao.js` (`contar`). Testes:
`tests/test_portal.py` (A15–A25) e `tests/test_rotas.py::test_pagina_atendimento`. Ficha auditável:
[atendimento.md](paginas/atendimento.md).

### 9.5.1 O que a página responde

"A equipe está dando conta da demanda?" — quanto entrou no ano e em cada mês, quanto foi resolvido (entregue ao cliente
ou encerrado sem entrega) e quanto ficou represado para o mês seguinte, sobre a mesma base do Início; e, de tudo o que
havia para atender em cada mês, que parte foi resolvida contra o objetivo de 100% (corte de 90%).

### 9.5.2 Regras que valem na tela

| ID | Regra |
|---|---|
| A3 | Entradas = Σ `quantidade` + `quantidade_estimada` (gold de entradas, = E1 do Início) |
| A13 | Resolvidos no mês = `entregue` + `nao_seguiu` do fluxo mensal pelo `mes_evento`, só pedidos que entraram no ano; `nao_seguiu` sem mês vai ao mês de entrada (E7); ficou = Σ entradas − Σ resolvidos desde janeiro |
| A15 | Números do ano: recebidos, resolvidos, em andamento, entregues, sem entrega; % resolvido arredondado para baixo; % em andamento = 100 − % resolvido |
| A16 | Dispersão: mesma escala nos dois eixos, um único rótulo na quina, parcial vazado, rótulos sem sobreposição |
| A24 | Quadro em 7 linhas: veio = ficou do mês anterior; para atender = veio + entrou; − entregues; − encerrados sem entrega; = ficou (calor em 5 níveis relativos ao maior da linha); % |
| A25 | % do mês = round(100 × (entregues + encerrados sem entrega) ÷ para atender); dispersão com x = para atender; referências = objetivo: equilíbrio 100% (y = x) e corte 90% (y = 0,9 x); cor ≥ 100 marinho, 90–99 azul claro, < 90 vermelho. Média e limite inferior natural (XmR, meses completos) só calculados |
| D29, D32, E4 | janeiro sem represados; data de entrega = 1ª ida a "Aguardando Feedback" (log), senão `data_de_saida`; "até D de mês" pela véspera da carga |

Calculadas e não exibidas: A1–A12, A14, A17–A23 (acumulado, abertos, controle, sombra, fôlego, linhas), as faixas do
diagrama do mês em A15 e a média/limite XmR da A25.

### 9.5.3 Memória de cálculo (carga de 23/10/2026, dados até 22/10)

| | jan | fev | mar | abr | mai | jun | jul | ago | set | out* | Ano |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Veio do mês anterior | 0 | 87 | 85 | 137 | 134 | 148 | 141 | 118 | 101 | 173 | |
| + Entrou | 374 | 341 | 485 | 472 | 629 | 569 | 765 | 644 | 733 | 508 | 5.520 |
| = Para atender | 374 | 428 | 570 | 609 | 763 | 717 | 906 | 762 | 834 | 681 | |
| − Resolvemos (entregues) | 241 | 269 | 338 | 386 | 504 | 479 | 672 | 565 | 515 | 419 | 4.388 |
| − Encerrados sem entrega | 46 | 74 | 95 | 89 | 111 | 97 | 116 | 96 | 146 | 102 | 972 |
| = Ficou para o mês seguinte | 87 | 85 | 137 | 134 | 148 | 141 | 118 | 101 | 173 | 160 | 160 |
| Respondemos do que havia para atender | 77% | 80% | 76% | 78% | 81% | 80% | 87% | 87% | 79% | 77% | |

Exemplo: julho = (672 + 116) ÷ (141 + 765) = 788 ÷ 906 = 86,98% → 87%. Ano: ⌊5.360 × 100 ÷ 5.520⌋ = 97%;
5.520 − 5.360 = 160 (3%). Outubro: 10 das 102 saídas sem entrega não têm mês de evento e foram atribuídas ao mês de
entrada. Dispersão: escala 200–1.000, marcas a cada 200; os 10 pontos abaixo do corte de 90% (vermelhos), outubro
vazado. Referência estatística não exibida (jan–set): média 80,53%; amplitude móvel média 3,355; limite inferior
natural 80,53 − 2,66 × 3,355 = 71,60% — nenhum mês abaixo dele.

### 9.5.4 Por que 100% é o objetivo, mas não o padrão

A demanda de um mês é o que havia para atender: o represado que veio do mês anterior mais o que entrou. Sempre há
pedidos que chegam nos últimos dias do mês e ainda estão em andamento quando ele fecha; chegar a 100% exigiria zerar a
fila todo mês, o que não acontece nem no melhor mês do ano (julho, 87%). Por isso: (1) o % sobre o que entrou, que
passava de 100% quando a equipe resolvia parte do represado (julho, 788 ÷ 765 = 103%), foi trocado pelo % sobre o que
havia para atender, que nunca passa de 100%; (2) foi testada uma referência estatística (média do ano e limite inferior
natural, XmR), que descreve o padrão do próprio ano; (3) o Caio decidiu manter na tela a régua do **objetivo**
(equilíbrio 100%, corte 90%), deixando explícito que a equipe não resolve toda a demanda do mês; a referência
estatística ficou só no código.

### 9.5.5 Validações

- BigQuery (24/10, só SELECT): quadro mês a mês do fluxo mensal igual à tela; situação da safra na gold de entradas
  (3.710 + 678 = 4.388 entregues, 972 sem entrega, 160 em andamento) igual ao fluxo; as duas tabelas são da carga de 23/10.
- Invariantes testados: veio + entrou = para atender = entregues + encerrados sem entrega + ficou; ficou(m) = veio(m + 1),
  janeiro = 0; Σ (entrou − resolvemos) = 160 = em andamento = em andamento do Início; % = resolvidos ÷ para atender,
  nunca acima de 100%. **112 testes passando.**

### 9.5.6 Limites

Outubro parcial; "resolvido" inclui saídas sem entrega (não é taxa de entrega); o 97% do ano (sobre os recebidos) e o %
do mês (sobre a demanda do mês) são contas diferentes; status de "não seguiu" sem corte de data (`docs/lembretes_gold.md`,
item 12) e 10 saídas sem data pela convenção E7; 43 cards de setembro possivelmente contados em outubro (item 14); fila
reconstruída com a situação de hoje (PD13); só o ano corrente, estimadas de 2025 fora; % com `round()` do Python (empate
vai ao par; hoje nenhum caso). No código, as referências fixas de 100% e 90% seguem nas chaves `media` e `corte`, e há
comentários antigos (A22, template) a limpar.

### 9.5.7 Decisões do Caio em 24/10/2026, em ordem

1. Conteúdo antigo apagado: cartões, gráfico de entradas e saídas, painel da fila e nota.
2. Big numbers do ano no topo (recebidos → resolvidos → em andamento); depois, achatados numa faixa.
3. Testados e rejeitados: gráfico de fluxo do mês (faixas), halteres, colunas com sombra (A19), área (A20), dias de
   trabalho no represado (A21) e linhas mês a mês com tendência (A23).
4. Dispersão do equilíbrio aprovada ("está perfeito"), com o % ao lado do mês, a linha de corte de 90% e legenda.
5. Quadro do extrato aprovado ("é o tipo de gráfico que precisamos"), com as cinco linhas e o %.
6. Faixa flutuante branca com sombra para os dois painéis, títulos alinhados e legenda da direita menor.
7. Faixa escura, reta e achatada para os números do ano.
8. Coreografia de entrada (contagem, faixa que sobe, quadro coluna por coluna, linhas que se desenham, pontos em
   sequência), desligada com menos movimento.
9. Faixa escura: três números distribuídos pela largura, cada um no centro do seu terço, com setas entre eles; data de
   corte à direita, após um fio (primeiro em letra vazada); legenda da régua centralizada.
10. **A25:** o % de cada mês passa a ser sobre o que havia para atender (represados + novos), porque a demanda do mês
    inclui o represado; dispersão com x = para atender. Títulos "Quanto resolvemos do que havia para atender, em cada
    mês" e (no quadro) a linha do %; um único "200" na quina dos eixos; data de corte como "dados até" + "22 de outubro"
    em Playfair branca com efeito gravado (sai a letra vazada).
11. Referência estatística testada (média do ano 81% e limite inferior natural 72%, XmR, zonas "acima/abaixo da média")
    e **revertida**: as linhas voltam ao objetivo (equilíbrio 100%, corte 90%) sobre a demanda total, zonas "resolvemos
    a mais / a menos", cores ≥ 100 / 90–99 / < 90 (hoje os 10 meses em vermelho), legenda curta numa linha; XmR fica só
    calculado.
12. Quadro final com 7 linhas: Veio do mês anterior / + Entrou / = Para atender / − Resolvemos (entregues) /
    − Encerrados sem entrega / = Ficou para o mês seguinte / Respondemos do que havia para atender (%). **Com este
    estado, o Caio deu a página como ENTREGUE.**

Navegação, no mesmo dia: moldura (menu, cabeçalho, carimbo e rodapé) congelada entre páginas; transições entre páginas
por View Transitions (só com movimento permitido); pré-carga das páginas por Speculation Rules (cabeçalho
`Speculation-Rules` → `/especulacao.json`, `prerender` moderado, sem `/static` nem endereços com parâmetros); aba "Prazo"
renomeada para "SLA" (título "SLA de entrega"); Prazo reduzido a uma página só, sem botões de slide.

## 9.6 Memória de cálculo, página por página (movida)

Movida em 25/10/2026 para [Módulos do portal, página por página](#módulos-do-portal-página-por-página): cada módulo
traz as tabelas e colunas, a SQL principal e o resultado com a data da carga; as demais SQL ficam nas fichas
`docs/paginas/`. **O que não se reproduz só em SQL:** (1) o exemplo do estudo (E1) sai do hash SHA-256 de
"data:grupo:projeto_id" calculado no Python (`calculos.exemplo()`); a SQL da ficha lista o universo e os passos do
projeto escolhido; (2) o arredondamento "maior resto" (E8c) e o meio-para-cima de `_pontos` são refeitos à mão a partir
das contagens da SQL (as fichas mostram a conta); (3) no SLA, a tela não usa `sla_util_horas` da gold enquanto ela
contar o almoço: a SQL do módulo M4 refaz o expediente no banco e bate exatamente.

## 9.7 Decisões do Caio antes de 28/10 (batalha de 26/10/2026)

O painel da batalha (D49) aplicou só o que não mudava regra de negócio. Estes itens ficaram para o Caio; cada linha junta
as propostas dos grupos (códigos entre parênteses), com a opção recomendada pelos painéis, o efeito e onde mexer. Nenhum
deles vai à página "O que falta" (que é da diretoria); os dois que já aparecem lá são a meta do SLA e as "2 decisões
abertas" da Previsão.

| # | Decisão | Opções (recomendada primeiro) | Efeito na tela | Onde |
|---|---|---|---|---|
| DC1 | **Vencedor do Mercado na Previsão** (G3-ia-6, G2-9, G4-ia-3, G1-N3c) | (a) regra em dois passos fixada antes de ver o resultado: o modelo precisa bater "repetir o último mês" também em jan–mai; entre os que passam, vence o menor erro em jun–set → **ARIMA com tendência** (`arima_100_ct`: 16,5% no teste, 20,4% em jan–mai); (b) manter a rede neural de 1 neurônio pelo critério puro da D48 (13% no teste, mas 27% em jan–mai contra 25% da ingênua) | muda só o Mercado (o Inbound segue a média de 6 meses); out/nov/dez do Mercado mudam | `ml/previsao.py` (critério C1–C4 + teste), `python -m ml.rodar --rotina --sem-extrair --forcar`, ficha `previsao.md` 5.5, D48 |
| DC2 | **Nov/dez como previsão ou cenário** (G3-ia-1, G4-ia-3, G2-11, G1-N3b), estendida ao Inbound | (a) cenário: rótulo "se o ritmo recente continuar", número menor em `--tinta-3`, ponto vazado, e a nota gerada de `fim_de_ano_2025` ("em 2025, nov caiu 31% e dez 56% sobre out; a janela de 12 meses não aprende fim de ano"); em 28/10 só outubro como previsão; (b) manter como previsão | cartões e gráficos de nov/dez | `previsao/template.html`, `previsao/calculos.py`, PD10, PD22 |
| DC3 | **Faixa "provável de 80%"** (G1-N3a, G2-8, G3-3b, G4-N7) | (a) já, só texto: tirar "80%" e chamar de "variação vista nos erros passados", com a cobertura medida ("o real caiu na faixa em X de Y meses"); checar p10 ≤ valor ≤ p90 no job; (b) depois: faixa centrada no ponto pelos erros fora da amostra (h1–h3 de jan–set) | hoje o número do Inbound fica fora da própria faixa em nov e dez (138 contra 146–219 e 147–221); a faixa cobriu 3 de 4 meses no Inbound e 1 de 4 no Mercado | `ml/previsao.py`, `previsao/template.html`, `tests/test_previsao_pagina.py`, ficha seção 4 |
| DC4 | **O que a Previsão responde** (G4-N12, G2-11, G3-2, G1-N4) | (a) título restrito ("…de Inbound e Mercado até dezembro"), subtítulo com a parcela calculada ("Inbound e Mercado = N% dos pedidos de 2026") e "Modelo contra modelo" dentro de "Regras e modelos"; (b) série "demais tipos" pela ingênua e um total do ano (só depois da DC2) | título, subtítulo e o meio da página | `apresentacao.py` (pergunta), `previsao/*` |
| DC5 | **Ritmo do mês em andamento** (G3-4, G4-N11) | (a) sem número novo: "133 já entraram até 25/10 (16 de 21 dias úteis)"; (b) número novo "no ritmo atual ≈ N" (realizado × dias úteis do mês ÷ decorridos), só a partir de ~5 dias úteis | linha do cartão de outubro | `previsao/calculos.py::_cartao`, regra P9 nova |
| DC6 | **Veredito da meta do SLA** (G1-N2, G2-3) | (a) segundo número de mesmo peso: "56% prontos em até 2 dias · meta: metade", selo com ícone + texto, e "metade ou mais em 7 de 9 meses; maio e junho ficaram em 49%" (comparação pelo valor exato); (b) manter só o típico | resposta da página SLA e slide 8 | `sla/calculos.py`, `sla/template.html`, teste por grupo |
| DC7 | **Teto acima de 5 dias no pedido de oficializar** (G3-6, G4-N2, G1-N6) | (a) "Definir um teto para os acima de 5 dias (hoje 12%)", com o número lido do cálculo do SLA (nada fixo); (b) só a meta de metade em 2 dias (como está) | pedido nº 1 do "O que falta" | `pendencias.py::PEDIDOS` |
| DC8 | **Ponte das bases no SLA** (G2-6, G1-N10, G4-N2) | (a) recorte "2.347 orçamentos com tempo medido" e, no leitor de tela e na dica da lupa, "de 3.969 entregues de jan a set; os demais não têm o histórico de status completo"; (b) linha de cobertura visível (o Caio a tirou na D37); denominador: todas as famílias ou só "Nenhuma" | recorte do estudo, leitor de tela | `sla/calculos.py::cobertura`, ficha `sla.md` ("Conciliação das bases") |
| DC9 | **Recorte do slide 6 do estudo** (G2-13, G3-10, G4-analise-3, G1-N9d) | (a) jun–set, com os cards de pacote numa linha à parte: Orçamentos 25%, Produção 24%, Validação Talento 22%, Fila 18%; o achado 5 e o "Onde olhar" do slide 8 passam a apontar etapas vivas; (b) ano todo, tirando "Em elaboração" (status extinto em maio, peso de 46 cards de pacote) das perguntas de ação | slides 6 e 8 | `sla/calculos.py` (K4/K6, Z5/Z7), `test_sla_trava.py`, `test_sla_conclusao.py`, `conferir_estudo.py` |
| DC10 | **Slide 3: "amostra aleatória"** (G4-N4, G1-N9c) | (a) "De cada 100 pedidos entregues, em quanto tempo entregamos?" e faixa "Dos N pedidos entregues de jan a set, A em cada 100…"; título do slide 2 por regra (`titulo_rapidez`); (b) manter a redação do Caio (D39) | títulos e faixas dos slides 2 e 3 | `como_medimos.html`, `sla/calculos.py`, W7 |
| DC11 | **Critério do vermelho e frases condicionais do estudo** (G2-12, G3-9, G1-N9b) | (a) vermelho só quando o mês ou o tipo descola de fato (IC de Wilson 95% que não encosta na mediana, ou a própria meta), "poucos" só com b < 20%, "Acontece todo mês" no lugar de "Não é crise, é padrão", n ≥ 30 para um mês destoar; (b) manter U7/J6 como estão | cores e frases dos slides 5, 7 e 8 | `sla/calculos.py` (U7, J6, Z), testes de matriz |
| DC12 | **Um limiar único para "casos a tratar"** (G1-N9a, G2-3) | (a) 5 dias de trabalho (40 h) para a diretoria e o limite do padrão (59 h) só como explicação do slide 2, com a ponte "dos 12% acima de 5 dias, 171 orçamentos (7%) fogem do padrão" (carga de 26/10); (b) os dois como estão | slides 2, 4 e 8 | `sla/calculos.py`, ficha 8.1 |
| DC13 | **Régua e frase do Atendimento** (G3-5, G4-N6, G2-7, G1-N5) | já, sem mudar regra: frase-resposta por regra ligando o % do ano ao % do mês; topo com % arredondado (C8) e "em andamento" com o próprio % (hoje 96% + 4% por arredondar para baixo); nomear as bases. Decisão: (a) trocar o corte de 90%, que deixa todo mês em vermelho, pela vazão resolvidos ÷ entrou no mês (A18; 100% = a fila não cresce) ou pelo patamar XmR já calculado; (b) manter A25 | faixa do ano e dispersão | `atendimento/calculos.py`, `atendimento/template.html`, A26 na ficha |
| DC14 | **Vocabulário pendente** (1ª leva) | (a) Início: "represados" → "veio do mês anterior", como no Atendimento; (b) manter | extrato do Início | `inicio.html`, `entrada/calculos.py` |
| DC15 | **Confirmar duas trocas já aplicadas na 1ª leva** | rótulo da meta "metade em até 2 dias de trabalho (16 h)" no lugar de "2 dias úteis" (pedido antigo do Caio, ficha 00.5) e a saída do indicador "12% passam de 5 dias" da página (D38); trocadas para seguir a meta em horas e a regra "número citado está no gráfico" | página SLA | `sla/template.html` |
| DC16 | **Regras frágeis e virada para 2027** (G4-N16) | uma só SQL da silver incluída nas três consultas; feriados numa lista (ou passados como parâmetro); status conhecidos normalizados com alarme na Qualidade; janela de teste da D48 andando com o retrato em 2027 | nenhum hoje; evita quebra silenciosa | `app/sql/`, `app/expediente.py`, `ml/dados.py`, PD22 |

**D56 (26/10/2026) sobre DC1, DC2 e DC5:** DC1 continua aberta, mas a tela já marca o vencedor do Mercado como "não
robusto" e o contrato traz a alternativa da regra em dois passos (C5: ARIMA com tendência, 16,5% / 20,4%, que prevê
515 · 570 · 635); recomendação na ficha `previsao.md` 5.0.9 (manter a rede com o selo e decidir com o fechamento de
outubro). DC2 segue aberta. DC5: o cartão do mês vigente mostra o realizado contra o **esperado até agora** (previsão ×
dias úteis decorridos ÷ do mês) e a situação dentro/abaixo/acima da faixa, sem um número novo de "ritmo".

Itens de rastreabilidade que ficaram como próximos passos (sem decisão de negócio): retrato por mês fechado gravado a
cada carga com alarme quando um mês fechado muda (G2-14, item 3; ex.: 2.348 → 2.347 entre 23 e 26/10); renumerar as
seções "0000…" da ficha `sla.md` depois de 28/10; `@pytest.mark.lento` nos testes de `ml/` e `conferir_layout.mjs` com
as páginas além do estudo (G4-N14, item 5).

## 10. Achados nos dados (levar à equipe)

| # | Data | Achado |
|---|---|---|
| F1 | 21/10/2026 | Há projetos em **Aguardando Feedback desde 24/03/2026** (até ~144 dias úteis); a automação de "Encerrado" após 30 dias não os fechou. 232 de 378 aguardando (61%) passam de 10 dias úteis |
| F3 | 21/10/2026 | **Por que o tempo com a equipe (hoje 15 h; 9 h na variante sem Entrada, descartada) e 2,9 dias de calendário não "fecham":** são medianas de distribuições diferentes (não do mesmo projeto) e **75% do calendário é noite, fim de semana e feriado** (medido na variante sem Entrada; não reconferido após a C2 revista). O que puxa a mediana geral para 2,9: pedidos que entram **qui/sex esperam 3,7–4,1 dias** (atravessam o fim de semana) contra **2,0 dias** de seg–qua (reconfirmado pelo Codex em 22/10: seg 2,02, ter 1,97, qua 2,02, qui 3,71, sex 4,12); metade dos projetos cruza um fim de semana. É associação, não causa: complexidade, tipo de pedido e composição dos grupos podem participar. Candidato a slide: "o dia da entrada muda a espera do cliente" |
| F4 | 22/10/2026 | **31 cards voltaram de Aguardando Feedback para Entrada** (37 voltas). Ajuste do mesmo pedido, pedido novo no mesmo card ou movimentação em lote (9 cards Unilever/CIF em 10/07, em menos de 1 minuto)? Hoje contam como retrabalho, fora da 1ª entrega. Pauta para a equipe: `docs/pauta_equipe_volta_para_entrada.docx` (ver L-G1) |
| F5 | 23/10/2026 | **Os dois +91% (Início e Atendimento) são coincidência de arredondamento, não erro:** entradas 5.520 × 2.890 = +91,0%; entregas 4.391 × 2.294 = +91,4%; colunas diferentes, conferidas no BigQuery. Crescem quase igual porque entregas ÷ entradas ficou em 79,4% (2025) × 79,5% (2026). Mês a mês divergem (ago +36% × +94%). Silver: entregas 2.297 × 4.425. No caminho: 15% das entradas de 2025 têm data estimada (Q11) e a base do SLA passou de 2.428 para 2.425 entre 21 e 23/10 (reconferir) |
| F6 | 23/10/2026 | **Validação gold × silver × bronze da página inicial (entradas e extrato):** todos os números da tela batem com a gold, a gold se reproduz pela silver (91 combinações ano × mês × grupo, 0 diferenças; extrato item a item) e a silver bate com a bronze (2025: 3.727 itens, 0 diferenças; 2026: 5.555 itens, nenhum faltando). Detalhe e consultas: seção 9.3 |
| F7 | 23/10/2026 | **3 pedidos contados duas vezes em 2025** ("[Pacote Pipoca 2026]" Doce, Gourmet e Sal à Gosto): existem no board 2025 e no 2026, e a R21 leva os do board 2026 para 15/10/2025. Proativo/out-2025 com +3. Impacto: +91,0% → +91,2%. Corrigir na gold (deduplicar entre boards) |
| F8 | 23/10/2026 | **`criado_em` errado para cards sem `create_pulse` no log:** 104 cards (preenchimento em lote MIA - Marca em 05 e 07/10). A R21 corrige 94; os 10 restantes (sem data de saída, já declinados/encerrados, entradas reais de jan a jul) **inflam outubro**: novos 498 (não 508) e saíram sem entrega 92 (não 102). Cerca de 49 dos 508 pedidos de outubro têm `data_de_entrada` > 7 dias antes da criação. Corrigir na silver/gold: sem `create_pulse`, usar `data_de_entrada` |
| F9 | 23/10/2026 | **"Entregue" sem ida ao cliente:** 185 entregas de 2026 vêm só da `data_de_saida` (R13), sem Aguardando Feedback no log; 133 Encerrado (quase todos cadastros retroativos de 05 e 07/10), 39 Declinado/Standby. Em outubro, 10 delas (5 Declinados Internamente com Data de Saída preenchida à mão em 13/10). **Decidir com a equipe** se Encerrado/Declinado com data de saída conta como entrega |
| F10 | 23/10/2026 | **Métodos diferentes entre os anos:** 2025 usa a data de entrada manual (15% estimadas; 149 cards sem nenhuma data ficam fora, cerca de 128 no período, o que faria a variação cair para cerca de +83%) e a `data_de_saida` (guarda o último reenvio); 2026 usa a criação no sistema e a 1ª ida ao cliente pelo log. No total do ano ficam próximos; mês a mês a comparação é enviesada. A bronze não tem a data real de criação de 2025 (`created_at` = importação em 03/09/2026) |
| F11 | 23/10/2026 | **Cards parados em andamento** (entraram até setembro): 12965403423 CloseUp (26/01, Aguardando Feedback sem evento no log), 12965451235 Mastercard (11/03, sem mudança de status), 12965425564 Marcas BH (23/06), Ypê (27/07), Consul (05/08), Upfront Spinelli/Maluf (17/08), Vitha (22/09), Pague Menos/IRGA (29/09). Levar à equipe |
| F2 | 21/10/2026 | O mês corrente é sempre **parcial e otimista** no tempo da equipe: a gold só inclui projetos que já foram ao cliente ou fecharam (R1). O site marca o mês com `*` e o tira das leituras automáticas |

## 11. Histórico

| Data | O que mudou |
|---|---|
| 27/10/2026 | **D57 — O site só lê a gold** (Caio): leitor (`app/dados.py`, `ml/dados.py`) trocado para as 8 tabelas e 8 views do `gold_monday`; saem a silver, a `Consulta`, `app/sql/` e o expediente recalculado; Início (extrato), Atendimento (quadro) e SLA/estudo leem as views; conferência código antigo × novo na mesma carga real: 0 diferenças; 475 testes; limpeza em `_descartados/2026-10-27/` e `docs/historico/` |
| 27/10/2026 | **D58 — Atendimento** (Caio): rótulos "Declinados (Não teve seguimento)" e "Entregues no Mês"; % = entregues ÷ (para atender − declinados) no quadro, na dispersão e no selo (96%); % dos recebidos na faixa do topo; 2º anel de rótulos na dispersão; 475 testes |
| 27/10/2026 | **D58b — Atendimento** (Caio): % = Entregues no Mês ÷ Para atender (set 79%); selo do topo removido, faixa só com o % de cada número; 475 testes |
| 27/10/2026 | **D59 — Portal** (Caio): Resultado e Qualidade fora da navegação; sem menu lateral; gancho para a próxima página visível, terminando na Previsão; tela cheia mantida ao navegar (quadro em tela cheia); 474 testes |
| 27/10/2026 | **D60 — Capa e encerramento** (Caio): capa com o roteiro da reunião, encerramento com agradecimento e pedidos, aba "Demanda" no lugar de "Início", setas trocam de página; 475 testes |
| 27/10/2026 | **D61 — Capa no desenho de referência** (Caio): capa com a jornada animada de um pedido (relógio para no típico do SLA), encerramento marinho, capas de seção pelas setas; cola do apresentador em projeto separado (porta 8200); 476 testes |
| 27/10/2026 | **D61, ajustes do Caio**: etapas da jornada na altura toda do plano marinho; o rótulo do medidor sai e no lugar entra a frase da etapa ativa, trocando em roleta (letra a letra) junto com a jornada; capas de seção desligadas ("enchem linguiça"; textos guardados em `CAPAS_SECAO`); capa e encerramento sem aba (navegação pelas setas, gancho e logo); 476 testes |
| 27/10/2026 | **D62 — Sincronia portal ↔ cola** (Caio): `/sinc` + `static/sinc.js`; testado em Chrome (cola → portal, portal → cola, slide do estudo, sem pingue-pongue); 479 testes |
| 27/10/2026 | **D62, ajustes** (Caio): sequência do portal alinhada à da cola — SLA → estudo "Como medimos" → Previsão (gancho do SLA: "E como chegamos a esse número?"; no estudo, ← no 1º slide volta ao SLA e → no último vai à Previsão); `/sinc` com `sessao` por subida do servidor (portal e cola zeram a versão vista quando o servidor reinicia — antes a cola ignorava o portal depois de um reinício); cola com falas reescritas (ponte → número → leitura → conclusão → gancho) e letra fluida para meia tela; 479 testes |
| 27/10/2026 | **Estudo, slide 2 em três leituras** (Caio): as setas do teclado passam primeiro por Formato → Sino → Faixas e só depois trocam de slide (voltando pelo ←, o slide 2 abre em Faixas); o quadro (`?passo=`) entra na posição do `/sinc` (`…/como-medimos#2:N`), e a cola tem uma ficha curta por leitura, com a ponte para a seguinte; testado com portal e cola reais nos dois sentidos; 479 testes |
| 28/10/2026 | **D63** (Caio): base congelada por padrão no computador (sem recarga por hora e sem aviso do banco); falas da cola reescritas em narrativa com números ao vivo; 497 testes |
| 31/10/2026 | **D65** (Caio): corte e congelamento em 31/10 para a reunião de 04/11 (`CORTE_DADOS`, `app/congelamento.py`, `tools/congelar_base.py`, `docs/congelar_outubro.md`); `Dockerfile` com o `previsao.json`; Previsão no retrato de outubro; LIA até 31/10; `tests/test_corte.py` (11 testes) |
| 26/10/2026 | **D56 — Previsão** (Caio): uma série e um modelo por recorte (4 séries, sem repartição), 61 modelos × 4 séries com a R7, cartões do mês vigente + 2 seguintes, gráfico em cartão flutuante, diálogo "Modelos comparados", outubro do Mercado exclusivos explicado, silver 2025 avaliada e não usada, contrato v3 e linha D56 no histórico PD09. Ficha `previsao.md` 5.0. 463 testes |
| 26/10/2026 | **D55 — Previsão** (Caio): só os dois gráficos (sem painel lateral e sem "Regras e modelos"); Inbound não exclusivo = não se aplica, exclusivos = Inbound inteiro (PD24: 78 casos jan–set); AutoTS na régua D48 não venceu (vencedores e números iguais); rotina completa refeita com a carga de 26/10; `tests/test_ml_automatico.py`; ficha `previsao.md` 5.6–5.7. 459 testes |
| 26/10/2026 | **D54 — SLA: rótulo curto da meta e dias úteis com fração** (Caio e gerente): rótulo "meta sugerida: 2 dias de trabalho" numa linha (linha do título na mesa, sobre a linha no celular); C3c no apoio e no slide 1 (1,8 · 1,6 · 2,5), conferida no BigQuery; `tests/test_sla_d54.py`; ficha `sla.md` seção 000000000000. 454 testes |
| 26/10/2026 | **D53 — Atendimento: capacidade da equipe** (Caio): A15b, A24b, A26, A27, A28; `app/sql/saidas_status.sql` (+ `TAB_LOG_ORIGEM`, `dados.saidas_status`); "Próxima pergunta" fora da tela em todas as páginas (e corrigido o vazamento lateral do link escondido em 390 px); conferido no BigQuery (status por mês = gold de fluxo nos 10 meses; externas 160; 82% no ano); `tests/test_atendimento_d53.py`; ficha `atendimento.md` seção 0. 431 testes |
| 26/10/2026 | **D52 — Início em dois quadrantes** (Caio): nuvem de palavras em cima, caixa cinza de altura fixa embaixo (tabela ↔ extrato compacto no mesmo lugar), cartão do gráfico do tamanho do cartão do SLA com o pé alinhado ao da caixa; corrigidos os dois blocos de CSS do Início que tinham caído depois do bloco de movimento do estudo (quebravam `tests/test_sla_movimento.py`); `tests/test_inicio_d52.py`; nenhum número mudou; ficha `inicio.md` (seção 3, 9 e histórico). 420 testes |
| 26/10/2026 | **D50 — Talentos com seletor e mapa mês a mês** (pedido do gerente do Caio): T7–T10, `talentos_top.sql` com os três recortes por mês, `tests/test_talentos_d50.py`; conferido no BigQuery (5.556 = Início; top 10 1.808 / 225 e meses iguais à conferência independente); ficha `talentos.md` seção 0 |
| 26/10/2026 | **D51 — Talentos: contagem na abertura e corrida do ano no play** (Caio): T11 (nomes sem reticências), T12 (entrada e saída do top 10 pelo acumulado; `talentos_top.sql` com `pos`, só SELECT, validada no BigQuery), `tests/test_talentos_d51.py` e exceção explícita em `tests/test_movimento.py`; ranking acumulado de jan e abr conferido no BigQuery; ficha `talentos.md` seção 0-D51 |
| 26/10/2026 | **D51 revista — Talentos: play só com ícone e corrida calma** (Caio): botão fora do cartão, na linha da legenda da barra; corrida ~11 s com respiro por mês, histerese, numeração fixa e entrada/saída com fade; só JS/CSS/template (nenhuma SQL nem número mudou); testes de `tests/test_talentos_d51.py` ajustados (botão só ícone, posição, 9–12 s); quadros em tempo real nos 3 filtros e botão em 1920/1440/1280/390; ficha `talentos.md` seção 0-D51 (onde ajustar `TEMPOS`) |
| 26/10/2026 | **D49, 3ª leva — documentação e limpeza:** PRD com "Estado atual" no topo e os blocos antigos na seção 12; seção 9.7 (16 decisões do Caio); M4, 9.1 e "Como o portal funciona" alinhados à D38/D48/D49; fichas com o retrato da carga de 26/10 (Início, Talentos, Atendimento, Previsão) e `sla.md` com "Estado vigente" (regras, mapa das seções, números por elemento com função e SQL, conciliação 5.556 → 3.969 → 2.347); `o_que_falta.md` regenerada de `pendencias.py` e conferida por teste; `docs/HISTORICO_2026-10.md`; `tools/checar_reuniao.py` grava `docs/validacao/reuniao_AAAA-MM-DD.json` (26/10: tudo certo); `DOIS_DIAS_H` → `META_H`; `tools/conferir_entrega.py` e um log do Playwright em `_descartados/2026-10-26/` (LEIAME); 392 testes |
| 26/10/2026 | **D49, 2ª leva — interface e movimento** (texto completo na seção 12.1, bloco "batalha 2, 2ª leva"); 390 testes |
| 26/10/2026 | **D49, 1ª leva — dados, cálculos e textos** (texto completo na seção 12.1, bloco "batalha 2, 1ª leva"); 361 testes |
| 26/10/2026 | **D48:** Previsão de demanda no protocolo do Caio (janela de 12 meses, teste jun–set, menor erro; 58 modelos re-rodados; Inbound = média de 6 meses, Mercado = rede neural de 1 neurônio; filtros revalidados; execução mensal com acompanhamento; tela de acompanhamento só de 2026 sem faixa do pé; ficha `previsao.md` com avaliação honesta); 345 testes. |
| 26/10/2026 | **D47:** Previsão de demanda com números (laboratório `ml/`, 58 modelos, decisão WAPE / média de 3 meses no Inbound / ARIMA no Mercado; página com dois gráficos, seletor, modelo contra modelo e regras; job em segundo plano; ficha `previsao.md`); 339 testes. |
| 25/10/2026 | **D42:** slide 6 do estudo do SLA ("Onde o tempo trava?": cartões por status e etapa com % do tempo travado, travaram e típico; destaque dos 2 maiores; faixa por regra; seletor em `#6`); gancho do slide 5 ligado ao slide 6; números por status conferidos no BigQuery; 243 testes. |
| 25/10/2026 | **D46:** movimento do estudo do SLA (um gesto de dado por slide, entrada só na 1ª visita, troca de slide direcional, grupo sem repetir a cena); 271 testes. |
| 25/10/2026 | **D42 revista, D43, D44:** tempo travado = tempo inteiro de quem travou (decisão do Caio); slide 7 por Tipo de Input (2ª rodada do Caio: sem nota, cores por regra, faixa curta); slide 8, conclusão do estudo; tudo conferido no BigQuery; 256 testes. |
| 25/10/2026 | **D41:** slide 5 do estudo do SLA (dispersão mês a mês com 12 colunas fixas, típico, faixa da maioria, linha de 2 dias, % > 2 dias e pedidos por mês; leitura sazonal × padrão por regra; seletor em `#5`); gancho do slide 4 ligado ao slide 5; números por mês conferidos no BigQuery; 234 testes. |
| 25/10/2026 | **D40:** slide 4 do estudo do SLA ("Para onde vai o tempo?": cartões A/B com % dos pedidos e % das horas da equipe, frases em frações por extenso, notas Prazo/Fluxo, faixa do pé com variantes, seletor em `#4`); gancho do slide 3 ligado ao slide 4; horas por faixa conferidas no BigQuery; 220 testes. |
| 25/10/2026 | **D39:** slide 3 do estudo do SLA (waffle de 100, chaves A/B, curva acumulada com 2 dias/80%/90%, seletor de talentos em `#3`); gancho do slide 2 ligado ao slide 3; números conferidos no BigQuery; 185 testes. |
| 25/10/2026 | **D38:** meta sugerida do SLA = metade dos orçamentos em até 2 dias de trabalho (16 h), revisando a D-SLA-3; estudo em linguagem simples. Texto completo na seção 8 (D38) e na seção 12.1; ficha `sla.md`, seção 00. 170 testes. |
| 25/10/2026 | **PRD em módulos:** seções novas "Módulos do portal, página por página" (M1 Início, M2 Talentos, M3 Atendimento, M4 SLA + estudo, M5 Previsão, M6 Resultado, M7 Qualidade; subseções fixas a–i, com SQL principal e resultados da carga de 23/10) e "Como o portal funciona"; a antiga 9.6 foi movida para os módulos. Tela: rodapé do estudo "Como medimos" no fluxo do slide visível no celular (antes ficava numa faixa fixa sobre o conteúdo que rola; `apresentacao.js`, decisão 14 generalizada para páginas de vários slides); `app/main.py` com string raw no padrão das Speculation Rules (fim do SyntaxWarning); README com a porta 8090 (8081 presa a processo fantasma). 152 testes |
| 25/10/2026 | **D37: regras novas do SLA** (D-SLA-1 a D-SLA-6, A1–A4) e estudo atualizado (cobertura; slide 2 com razão das metades, Q-Q sino × log-normal, boxplot em log), depois da validação do cálculo. Tela 14 h · 2,8 dias · 31/25/15/29 (71% em até 3 dias); conferido no BigQuery. PD21. Ficha `sla.md` seção 0 |
| 25/10/2026 | **D36: correções em Início, Talentos e Atendimento** (auditoria + decisões 1–14): cartão `--cartao-*`, seta pastel na Var. (revisa a D26), `<1%`, aviso no lugar do bloqueio em Talentos, empate no top 10, "− Entregues ao cliente", rodapé pelo `_processado_em`, celular com "Próxima pergunta" e rodapé no fim do slide. Números inalterados |
| 24/10/2026 | **D35: slide 2 do estudo "Como medimos"** (X1–X7). Ficha `sla.md`: textos e mapa elemento → regra → campo → SQL (3.2), regras X1–X7 (4), memória dos três grupos (5.5), SQL executáveis 6.7.1–6.7.4 com o resultado, passo a passo (6.8), atualização a cada carga (6.9), avaliação estatística e recomendações (8.1). Conferido no BigQuery: todos os números batem. X7 fora da tela, calculada. 116 testes |
| 24/10/2026 | **D34: SLA redesenhado (em construção) e estudo "Como medimos"** (`/viu-agenciamento/sla/como-medimos`, regras E1–E3). Seção 9.6 nova: memória de cálculo página por página (tabelas, colunas, SQL, resultado). Fichas: `sla.md` refeita (colunas consumidas, SQL que refaz o expediente sem almoço no banco, SQL com a coluna da gold e a diferença, faixas por mês dos três grupos, exemplo do estudo); `inicio.md`, `talentos.md` e `atendimento.md` ganharam a seção 1.1 "Tabelas e colunas consumidas". Reconferido no BigQuery (só SELECT): cargas iguais às de 23/10; SLA 2.425 / 15,2054 h / 2,871 dias; Início 5.520; Atendimento 5.360 resolvidos; Talentos 3.435 / 1.955 / 130. Ponto para decisão: a caixa "Fica fora" do estudo diz "espera da marca", mas "Em elaboração - Retorno Marca/Executivo" conta na C2 (ficha `sla.md`, limite 8). 114 testes |
| 24/10/2026 | **D33: página Atendimento entregue.** Faixa escura com os números do ano (5.520 → 5.360, 97% → 160, 3%; régua 4.388 / 972 / 160), três números centrados nos terços, data de corte "dados até 22 de outubro" em Playfair gravada, legenda centralizada; bloco branco flutuante com o quadro do extrato em 7 linhas (A24) e a dispersão sobre a demanda total (A16); **A25**: % = (entregues + encerrados) ÷ para atender (77…87%), régua de objetivo 100%/90% (os 10 meses abaixo de 90%), XmR só calculado; coreografia de entrada. Decisões do Caio em ordem, memória e o porquê de 100% não ser o padrão na seção 9.5; ficha `atendimento.md` revista inteira; reconferido no BigQuery (fluxo × situação da gold de entradas). **Navegação:** moldura congelada, View Transitions, Speculation-Rules, aba "Prazo" → "SLA" (título "SLA de entrega"), Prazo numa página só. 112 testes |
| 24/10/2026 | **D31: página Talentos entregue.** Resposta calculada ("62% da demanda do ano se concentra nos talentos exclusivos."), barra com % e quantidade dentro de cada parte (largura mínima em Talento não informado), legenda com os três grupos sem números, lista oculta para leitor de tela, dicas com o top 10 de exclusivos e de não exclusivos (T6, `app/sql/talentos_top.sql`, coluna "Último"), sem etiqueta de período nem "Aguardando dados"; nomes de talentos na tela (revê a D30). Conferido no BigQuery: 5.520 = Início, exclusivos 3.435 (39 nomes, nenhum vazio), top 10 1.802 (52%) e 221 (11%). Decisões do Caio em ordem e memória de cálculo na seção 9.4; ficha `talentos.md` revista inteira. **Prazo:** "até 1 dia" 29% (slide 1) × 28% (slide 2) corrigido: slide 2 = C8 nas duas primeiras faixas + maior resto nas três de cima (29/24/15/17/15, seção 9.1). Desalinhamentos novos anotados (item 4 do "Estado atual"). 89 testes |
| 23/10/2026 | **D30: área como portal** (ordem da reunião, `pergunta`/`estado`/`na_reuniao` por seção, máscaras de `pendencias.py`, página "O que falta", modo apresentação, abas só com texto revisando a D18; Qualidade como seção e Previsão em máscara). **D30-b:** Talentos lê a silver 2026 por exceção (agregado anual, concilia 5.520 = 5.520; sai com a PD01). Talentos parcial (T1–T5: 3.435 / 1.955 / 130, 62/36/2%). Prazo com 3 slides (C12–C14) e **revalidado** no BigQuery (bate exatamente; 2.428 → 2.425 explicado pela R1 da gold). Fichas novas `talentos.md` e `o_que_falta.md`; `sla.md` e `demais.md` atualizadas; prompt para a gold em `docs/prompt_dados_pendentes.md` (rascunho). Talentos sem o bloco "Aguardando dados" (tela limpa, a pedido do Caio; PD01–PD03 só em "O que falta"). 89 testes |
| 23/10/2026 | D29: decisões do Caio sobre o Início (janeiro com 0 represados, sem extratos do ano anterior, sem aviso de estimadas na tela, "Sem tipo" 2% aprovado); totais dos outros meses legíveis com o extrato aberto (só a coluna esmaece). Nota de dias úteis segue em discussão (P4). 83 testes |
| 23/10/2026 | **D28: página Início entregue.** Validação final em três camadas (4 validadores + árbitro, 624 itens, 0 divergências). Correções B1 (tipos no ano pelo maior resto), B2 (situação pelo maior resto), B3 (extrato sem % por diferença), B5 (janela pelos meses com pedidos), B6 (lista de meses válidos na base inteira, tela inalterada), B7 (aviso de cargas de dias diferentes), B8 (período na virada do ano). Ficha `docs/paginas/inicio.md` completada (origem de cada número, memória de 12 meses e 6 extratos, passo a passo gold e silver, checagem diária Q1/Q2 com alarmes); pendências do Caio na seção 9.0; achados G1–G9 em `docs/lembretes_gold.md`. 83 testes |
| 22/10/2026 | D20–D22: seção **Previsão de demanda** (esqueleto P1–P6 com série fictícia em DEV), seção **Qualidade dos dados** (em branco; verificações Q/A prontas e conferidas: A1 = 46 pelo cálculo exato — a 1ª consulta dava 43 por contar minutos inteiros), nomes curtos nas abas. Conferido em 1261×638, 1440×900, 1920×1080 e 390 px: nada cortado nem rolando para o lado. 43 testes |
| 22/10/2026 | Página inicial enxuta para apoiar reuniões (a análise é falada por quem apresenta): a leitura automática por regra foi feita, conferida e depois retirada a pedido do Caio. Saíram também, a pedido do Caio: rótulo do número, comparação no topo, média/maior mês, notas de base e de estimados, título do gráfico. Número voltou à Playfair (a mesma do SLA) a pedido do Caio, com legenda na mesma letra do SLA (IBM Plex Sans; o itálico serifado foi testado e descartado pelo Caio) dizendo o período: "recebidos em 2026, até 21 de outubro" (o dia acompanha a última carga da gold), "recebidos ao longo de 2025", "recebidos de outubro a dezembro de 2024" (E4); caixa da legenda com o fundo padrão; gráfico ancorado no pé da lâmina. **Mês parcial em destaque** em todos os gráficos: nome e total em azul e selo "PARCIAL" (na previsão, selo "PREVISÃO" no mês previsto) |
| 22/10/2026 | D23: página inicial com a entrada mensal por tipo de input (tabela nova `gld_agenciamento_entrada_diaria`, conferida: totais 328 / 3.577 / 5.488, sem chave repetida). Conferida em 1440×900, 1261×638 (com dica pelo mouse e pelo Tab) e 390 px (barras deitadas, sem dica). 45 testes |
| 23/10/2026 | Efeitos e dicas revisados por agentes (4 revisores + juiz para os efeitos; 4 propostas + juiz para a dica de novos; 6 avaliadores com skills de design + aplicador para as dicas): fim do tremor da contagem (largura fixa durante a contagem), foco no mês com transição, barra do extrato que cresce, corridas de clique/Voltar e falha de rede corrigidas, Esc fecha qualquer dica, anúncio ao leitor de tela; dica de Novos pedidos só com a tabela (centralizada, dois níveis, mês × mesmo mês do ano anterior, Var. com base mínima 30); dica dos nomes só em Internos, sem a comparação; parcelas fecham em 100% (maior resto, E8c) e % arredonda meio para cima. 75 testes |
| 23/10/2026 | Bloco de resposta compactado (altura do número; número + período | selo + barras finas do mesmo período), sem cartão: a versão em cartão empurrava a tabela e mudava a coluna no extrato (reprovada pelo Caio) |
| 23/10/2026 | Início e Atendimento: bloco de resposta escolhido entre 3 propostas de agentes (A KPI editorial, B comparação visual, C resposta direta; maquetes em `docs/propostas_resposta/`). Venceu B: cartão com número, selo da variação (regra E8b) e barras proporcionais do mesmo período em SVG (sem estilo inline, CSP). Título do Início "…ao longo de AAAA até o momento?" (ano pela regra E0). Dica de novos por tipo; saída do extrato espelhada; correção da dica presa |
| 23/10/2026 | Validação em três camadas (gold × silver × bronze) da página inicial: números da tela confirmados; achados F6–F11 (duplicados em 2025, criado_em em lote inflando outubro, entregas sem ida ao cliente, métodos diferentes entre anos, cards parados). Seção 9.3 |
| 23/10/2026 | Início: extrato do mês como **fila** (E7): represados do início + novos = demanda; entregues (dos novos / dos represados), não seguiram, represados no fim; só pedidos de 2026 (decisão do Caio); dicas por mês de entrada com início, resolvidos e seguem. Conferido no BigQuery (out: 173 + 508 = 681 = 419 + 102 + 160). 72 testes |
| 23/10/2026 | Início: extrato com % entregas e % entradas por origem (E7); dica do gráfico só no nome do mês (todas as páginas com gráfico mensal); clique no mês troca só a caixa, sem recarregar, com "foco no mês"; rodapé "Dados até … · atualizados em …" em todas as páginas; "parcial" como texto miúdo e rótulos do gráfico mais leves, seguindo o deck de referência (PPD-PIPELINE-MONDAY). 72 testes |
| 23/10/2026 | Início e Atendimento: comparação compacta ao lado do número com seta verde/vermelha. Testada e **desfeita** a faixa de resposta na largura toda (cortava os meses em telas de 720–768 px de altura e esticava a tabela); a tabela volta compacta, flutuando sob o número. **Fichas por página** em `docs/paginas/` (pergunta, textos, regras, memória de cálculo, SQL, validações, limites, histórico) para auditoria. Achado F5 e pendência Q11. 72 testes |
| 23/10/2026 | Início e Atendimento: título do Início vira "Quantos pedidos de orçamento chegaram em AAAA?"; bloco do número em grade (número + comparação compacta ao lado, período embaixo), em macro única `comparacao_ano`. Regras de relatório vivo (E8b, E4): sinal e frase pelo percentual arredondado ("a mais" / "a menos" / "igual"), base mínima de 30 para toda variação em % (inclusive o total da tabela e A7), período pronto no cálculo (sem `replace` no template). Corrigido "+0%"/"-0%". 72 testes |
| 23/10/2026 | Início: tabela de tipos com cabeçalho em dois níveis (ano sobre "Pedidos" e "%"), corpo sem negrito (2026 escuro, 2025 cinza, variação azul) e total marcado só pelo traço de soma; selo "parcial" em amarelo claro com texto oliva (7,3:1), em minúsculas. 59 testes |
| 23/10/2026 | Início: caixa de tipos com pedidos e % de 2026 e do mesmo período de 2025, variação por tipo e linha de total; números centralizados. "Sem tipo" fica sem variação (77 × 3 explodiria): o tratamento desse grupo fica em aberto (Q10). Conferido com o BigQuery. 59 testes |
| 23/10/2026 | Início: caixa de tipos mostra a parcela de 2026 e a de 2025 lado a lado (em vez de "+14 pt"); selo "PARCIAL" do mês em andamento em amarelo VIU (fundo) com texto escuro, em todos os gráficos |
| 23/10/2026 | D27: aba **Atendimento** (entregas × entradas, taxas, comparação com 2025) e diferença de composição por tipo no Início, com teste de duas proporções; memória de cálculo na seção 9.2; página de regras da aba. Conferido com o BigQuery. 59 testes |
| 23/10/2026 | D26: página inicial sem seletor de ano (sempre o ano da carga) e com a comparação ao ano anterior no total e no mês (E0, E8); limpeza do parâmetro `ver` e de comentários antigos. Conferido com o BigQuery. 54 testes |
| 23/10/2026 | Documentação alinhada ao código depois da revisão do Codex: seção "Estado atual do código", D25 (substitui D24), Q7 e Q8; README e CLAUDE.md atualizados. 54 testes |
| 23/10/2026 | **Extrato do mês** (E7): clicar numa coluna abre, no lugar da legenda, para onde foram os pedidos do mês (entregues no mês, no mês seguinte, mais tarde, não seguiram, em andamento) e de onde vieram as entregas feitas nele (próprio mês, mês anterior, mais antigos), com o total em % do que entrou. Base nova `gld_agenciamento_fluxo_mensal` (`TAB_FLUXO`), conferida: bate 100% com a diária em todos os meses; set/26 = 733 → 460 set + 131 out + 138 não seguiram + 4 andamento; 515 entregas (70%) = 460 set + 50 ago + 5 antigos. Dica do mouse reduzida às 4 situações; tabela tipo × situação saiu da dica. Bronze × silver × gold de out/26 explicado: mesmos 5.555 cards, datas diferentes; relatório externo (~408) usa `data_de_entrada` e exclui declinados. 46 testes |
| 23/10/2026 | Página inicial: troca de leitura movida para abas dentro da caixa da legenda (topo só com o ano). Dica do mês com **tabela tipo × situação** (E7) e **entregas feitas no mês**, separando as da própria safra das de meses anteriores (E8: saídas do mês − entregue no mês). Conferido com a gold em set/26: Mercado 291/100/82/4, Inbound 80/11/38/0, Internos 61/20/12/0; 515 entregas = 460 + 55 |
| 23/10/2026 | D24 implantado (leitura por situação como padrão; ?ver=tipo). Gold corrigida para cadastro retroativo (79 cards de 07/10 voltaram aos meses reais; out/26 600 → 508). 45 testes |
| 21/10/2026 | Início: acesso à tabela SLA confirmado; GCP testado (permissões, APIs, deploy de teste); arquitetura e controle de acesso decididos (D1–D12) |
| 22/10/2026 | D19: seção "Negócio fechado" em branco no navegador e no menu (ícone de selo); área no menu com nome curto "Orçamentos" em uma linha (nome longo vira reticências + dica); F4 e pauta da equipe (.docx com os 31 cards e coluna para resposta). 34 testes |
| 22/10/2026 | **Menu lateral escuro em árvore** (área abre/fecha as páginas; escolha guardada; recolhido vira régua de ícones navegável) com cartão de status dos dados; **navegador** com ícones e pílula de hover; **CSP sem estilo inline** (nonce por resposta, `style-src-attr 'none'`); **dados recentes garantidos**: conferência do metadado a cada 5 min em segundo plano, agenda da gold (seg–sex 09:00 + 45 min de tolerância) com aviso "a base não atualizou", data dos dados no slide; **velocidade**: leitura pela Storage Read API só com as colunas usadas (12 s → 3,4 s), recarga e recálculo em segundo plano antes da troca (ninguém espera), páginas em 20–130 ms. 33 testes |
| 22/10/2026 | **Revisão do Codex aplicada** (robustez e acessibilidade, sem mudar regras): última carga válida continua servida quando o BigQuery falha (aviso "atualização atrasada", nova tentativa após `RECARGA_MIN`), contrato de dados antes de trocar a base, versão explícita da carga nos caches (corrige `is not id()`), 503 honesto sem números, trava `AUTH=off` em produção, `Cache-Control: private, no-store` nas páginas, hash de conteúdo nos estáticos, estado "sem mês completo" (janeiro), cliente no passo 1 descartado (C4), gaveta do celular como diálogo (foco contido, fundo inerte, botão fechar), mês em foco com fundo em vez de esmaecer os outros (contraste), layout sem JS, meses futuros anunciados ao leitor de tela, página de regras com filtro e título próprios, CSS morto removido, tipografia ~10% maior. 28 testes (`tests/test_dados.py` novo). `Dockerfile`, `.gcloudignore`, `.dockerignore` e `requirements-dev.txt` criados para a fase 3 (nada publicado) |
| 22/10/2026 | Slide 1: coluna do número 4,4/12, textos de uma linha ("tempo típico da equipe até a 1ª entrega", "2,9 dias corridos até o cliente receber", "medianas de N orçamentos entregues, jan a set" sob os dois números), conteúdo encostado no título (sem buraco no meio). Conferido em 1280×719 (menu aberto), 1261×638 (recolhido), 1440 e 1920: nenhuma quebra de linha e tudo dentro da lâmina |
| 22/10/2026 | **Testes automatizados** (`tests/`, 17 testes, dados sintéticos, sem BigQuery): calendário e horas úteis, regras C1–C11, invariantes do arredondamento (faixas sempre somam o total), rotas e redirecionamentos, cabeçalhos de segurança e cache, acessibilidade básica (idioma, h1 único, alt em imagens, nome nos botões de ícone). Acessibilidade da navegação nova: nomes dos links continuam no DOM com o menu recolhido; botão recolher com `aria-expanded`; barra inferior com `aria-current`; animações respeitam "menos movimento" |
| 22/10/2026 | D18 implantado (menu recolhível, barra inferior no celular). Legibilidade do slide pela comparação com a apresentação de referência: coluna do número 4/12 (gráfico 8/12), totais dos meses em cinza-claro, barras mais altas. 1ª atualização automática confirmada: gold de 22/10 09:00 carregada às 09:02 sem reiniciar o site |
| 21/10/2026 | Navegação ≠ filtro: as seções viram **abas editoriais** apoiadas na linha do cabeçalho, com o traço azul da marca (o mesmo sob o logo) deslizando entre as abas; o filtro de talentos continua cápsula. Legenda numa linha com "(fora do gráfico)" e "meta 75%" à direita sobre a linha. Base do número ("mediana de N orçamentos entregues, jan a set") e **Leitura** automática por regra sob o gráfico (melhor mês, pior mês, último mês × ano) — C11 |
| 21/10/2026 | Gráfico no estilo da referência (pedido do Caio): colunas largas com os percentuais das faixas sempre visíveis, total em cinza no topo (escurece no mês em foco), sem trilha; mantidos ponta arredondada, vão de 2 px, base contínua e meta leve. Sem "01" e sem a dica de hover. Textos gerenciais: "tempo típico da equipe até a primeira entrega", "dias corridos de espera típica do cliente", "Realizado no ano" |
| 21/10/2026 | Gráfico pelas marcas da skill dataviz: colunas finas (~21 px) com ar no slot, ponta arredondada só no topo, vão de 2 px entre faixas, base contínua hairline, meta em 1 px tracejado leve, **trilha clara até 100 %** atrás de cada coluna representando "acima de 2 dias" (a legenda acompanha); rótulos dos meses em cinza-escuro |
| 21/10/2026 | **Entrada volta a contar** no tempo da equipe (C2 revisto): 15 h e 53% no ano; texto "com a equipe até a 1ª entrega". Slide cabe na tela de 1261×638 do Caio (coluna da esquerda 24 em e gráfico 26 em num corpo de 30 em); link de regras compacto; seletor de talentos na cápsula com pílula branca deslizante; barra Anterior/Próximo some em seção de um slide só; "2,9 dias corridos" |
| 21/10/2026 | Slide 1 menos poluído (dataviz: rótulos seletivos): gráfico mostra só o total por mês; as faixas aparecem no mês em foco (mouse, toque ou Tab) e os demais esmaecem; meta vai para a legenda; seletor de talentos em azul-claro (único azul sólido é o navegador); caixa enxuta com botão **Ver regras e análises** → `/viu-agenciamento/sla/regras` (página em branco, a construir) |
| 21/10/2026 | Navegador novo: cápsula com abas **INÍCIO** e **SLA**; pílula azul na aba atual que desliza (efeito mola) da aba anterior ao trocar de página; reflexo que segue o mouse/teclado. **Tela cheia** vira botão redondo com ícone no fim do cabeçalho, em todas as páginas (sai da barra de baixo). Página inicial sem a barra Anterior/Próximo |
| 21/10/2026 | `/viu-agenciamento` é a **página inicial** da área: em branco, só com o navegador (vai receber um painel próprio); `/` abre ela; SLA em `/viu-agenciamento/sla` |
| 21/10/2026 | **GESTÃO DE ORÇAMENTOS** vira a área principal (D17): navegador de seções no topo; o SLA passa a ser a seção `/viu-agenciamento/sla`; menu lateral só com a área |
| 21/10/2026 | Nova apresentação em branco **GESTÃO DE ORÇAMENTOS** (`/viu-agenciamento`, pasta `app/apresentacoes/gestao_orcamentos/`), a construir com o Caio |
| 21/10/2026 | Slide 1: linha da fila sai da tela (C9 segue calculada para slides futuros); rótulo "Talentos" no seletor; definição de trabalho na caixa. Desempenho: página de 300–600 ms para ~30 ms (sem recorte por página, versão dos estáticos em cache, templates sem reler o disco fora do computador), cache no navegador para os estáticos, dados carregados ao subir o servidor |
| 21/10/2026 | Slide 1: espera na fila (C9), seletor exclusivos × não exclusivos (C10), "No ano"; animação de entrada (traço do título, número contando, textos em sequência, colunas reveladas por máscara de baixo para cima, totais e meta no fim; respeita "menos movimento") |
| 21/10/2026 | Slide 1, acabamento (sem mudar a forma): totais em negrito e por cima da linha da meta (mais leve); gráfico mais alto e alinhado pela base com a caixa da esquerda; folga sob o número grande; lâmina cresce até 16:10 em telas mais altas. Números validados na tela contra o cálculo e o BigQuery; arredondamento C8 |
| 21/10/2026 | Slide 1: regras C2/C5 revistas (sem Entrada, sem almoço, 8 h/dia; v2 da gold anotada). Layout em **lâmina 16:9 que escala** (cabe inteira em qualquer tela de computador, inclusive com zoom) e coluna única com rolagem em tela estreita/em pé; no celular o gráfico vira barras deitadas. Testado em 11 tamanhos (1920×1080 a 360×640): sem corte, sem rolagem lateral, sem sobreposição |
| 21/10/2026 | Visão geral substituída por **apresentação** (D13–D16): moldura com menu, cabeçalho VIU, navegação de slides; **slide 1 de SLA** fiel à referência, com regras C1–C7; testado em 1440×900 (cabe na tela) e 390×844 (sem rolagem lateral), teclado e menu no celular |
| 21/10/2026 | Fase 1: esqueleto local (FastAPI, menu automático, carga em memória com recarga pelo metadado, filtros, tema claro/escuro, celular) e página **SLA › Visão geral**; números conferidos contra o BigQuery (3.095 projetos; equipe 2,0 e cliente 20,3 dias úteis; 378 aguardando; 232 em alerta; 202 com retrabalho) |

## 12. Arquivo: blocos de retomada de 21–26/10/2026 (sem cortes)

Movidos do topo do PRD em 26/10/2026 (D49, 3ª leva) para o topo mostrar só o estado atual. São o registro de cada etapa
como foi escrito no dia; onde divergirem do "Estado atual", valem o estado atual e a seção 8.

### 12.1 Blocos "Último ajuste / Ajuste anterior" (do mais novo ao mais antigo)

#### Último ajuste: batalha 2, 2ª leva — interface, layout e movimento (26/10/2026)

Aplicado o aprovado pelo painel, sem mudar regra de negócio (D49). **Movimento do portal (extensão da D46):** números
grandes prontos desde o 1º quadro (saiu a contagem `data-contar`/`contar()` do Início, Talentos, Atendimento e SLA);
um gesto de dado por página, até ~1,15 s, `--ease-entra`, sem mola nem loop (colunas do Início/SLA em 1,11 s; Talentos
1,12 s; Atendimento: faixa e régua paradas, bloco branco num fade de 0,3 s, pontos numa onda de 0,89 s; frase do SLA,
linha da meta e totais do mês parados); navegação só com o voo da pílula (320 ms) e o fade do conteúdo (saíram o
brilho, a pílula "líquida", a aba que sobe e a regra duplicada); lupa do estudo num fade de 180 ms; troca de grupo de
talentos (SLA, Previsão) e recarga por carga nova abrem a página pronta (`.revisto`), com o foco de volta no grupo;
impressão parada. **Modo apresentação:** carga nova não recarrega a tela; aparece "Há dados novos na base. Atualizar"
(`role=status`). **Base congelada (CONGELAR):** estado próprio `congelada` — sem o aviso amarelo de "base atrasada";
menu "base congelada para a apresentação". **Rodapé datado em toda rota**, inclusive as máscaras (Qualidade com as
tabelas SLA, entradas e fluxo; seções sem tabela usam as do Início); **menu e rodapé com o mesmo horário** (o do
processamento, `_processado_em`; o `modified` fica no title). Máscara da Qualidade com texto para o público.
**`/{seção}/regras` retirada** (301 para o estudo do SLA ou para a própria seção, com o filtro); `regras.html` apagado.
**Filtro de talentos** levado pelas abas, menu, "Próxima pergunta" e barra do celular entre SLA e Previsão; slide 8 do
estudo com "Voltar ao SLA" (com o filtro) como link principal. **Previsão (G4-N8, P9):** pé do cartão com as duas
medidas — "14% em jun–set e 27% em jan–mai (≈ 20 a 34 pedidos/mês) · repetir o último mês erraria 26% e 47%" (Mercado
13% / 27%, ingênua 20% / 25%); painel "Vale mais que o palpite simples?" em 3 linhas (modelo escolhido, média dos 3
últimos meses, repetir o último mês); subtítulo "o modelo que menos errou no teste" (nome técnico no title). **Checagem
única pré-reunião:** `tools/checar_reuniao.py` (identidade/projeto, golds no mesmo dia, /saude com o mesmo
`_processado_em`, Q1/Q2 do Início, estudo nos 3 grupos, previsão na mesma carga); rodada em 26/10 (carga 26/10 09:01):
**tudo certo**. `tools/conferir_entrega.py` aposentado (regra antiga). `tools/conferir_layout.mjs` ganhou a checagem de
movimento (`--movimento`). Testes: `tests/test_movimento.py` e `tests/test_batalha2_interface.py` (**390 testes**).

#### Ajuste anterior: batalha 2, 1ª leva — dados, cálculos e textos (26/10/2026)

Aplicado o aprovado pelo painel, sem mudar regra de negócio: **SLA** com um só vocabulário (meta "metade em até 2 dias
de trabalho (16 h)"; "dias úteis no calendário" só no prazo do cliente, C3b; "típico" no lugar de "mediana"; sem o corte
de 5 dias na página; selo do mês com 1 casa entre 15,5 e 16,5 h pela C6), C3b registrada com SQL e conferida no BigQuery
(2 / 1 / 2 dias úteis); slide 1 em dias úteis; slide 2 em linguagem simples (termos técnicos no leitor de tela);
glossário em `docs/paginas/README.md`. **"O que falta"** sem o marcador "X", estados "Pronta · meta a oficializar" e
"Pronta · 2 decisões abertas", Resultado fora do modo apresentação, `/previsao/regras` volta para a Previsão.
**Previsão:** corte E3 único (`app/corte.py`) no site, no job e no ML (outubro fecha em 02/11 mesmo com 31/10 num
sábado); job não dispara com CONGELAR/modo apresentação; falha visível; trava nos dois modos; contrato do snapshot
antes do retrato; CSVs atômicos; PD22 (virada do ano) e PD23 (job em produção). Fichas: `sla.md` (seção 00000000000),
`previsao.md` (seção 4), `o_que_falta.md`, `atendimento.md`. Testes: `tests/test_batalha2_textos.py`.

#### Ajuste anterior: Previsão de demanda no protocolo do Caio (D48, 26/10/2026; revisa a D47)

Decisões do Caio para a "Previsão de demanda": **janela móvel de 12 meses** (cada previsão treina só com os 12 meses fechados anteriores; 2025 só dentro da janela), **teste = jun, jul, ago e set/2026 a 1 mês à frente**, **vence o menor erro (WAPE)** por série (empate < 1 ponto = o mais simples; ressalva: a escolha é feita no próprio teste). Os 58 modelos foram re-rodados (`ml/regua.py` R1–R6; 4 "não se aplicam" com 12 meses: Prophet com sazonalidade anual e `comb_sazonal`). **Inbound = média dos últimos 6 meses** (14,4% ≈ 20 pedidos/mês; ingênua 26%); **Mercado = rede neural de 1 neurônio** (12,6% ≈ 49 pedidos/mês; ingênua 19,8%), mas na verificação jan–mai (fora da escolha) a rede erra 26,8% contra 24,7% da ingênua — avaliação honesta na ficha, 5.5. Filtros revalidados (repartir pela parcela dos meses anteriores × prever direto): Inbound exclusivos 14,8%, Mercado exclusivos 11,3% e não exclusivos 20,0% por repartição; Inbound não exclusivo (8/mês, 69%) mostra "poucos pedidos para prever com confiança". **Execução mensal:** retrato refeito quando o mês fecha (`ml.rodar --rotina`, ~9 min); outubro aparece em andamento com a previsão do fim de setembro e o realizado até a véspera (`--acompanhamento`, a cada carga, sem recalcular). Tela de acompanhamento: eixo só de 2026, sem faixa do pé, pílulas sem número, "erro médio no teste jun–set (menor é melhor)". Números (retrato de setembro): Inbound 138 · 138 · 138; Mercado 464 · 517 · 588. **345 testes.** Ficha [previsao.md](paginas/previsao.md); módulo M5; decisão D48.

#### Ajuste anterior: Previsão de demanda com números (D47, 26/10/2026) — protocolo e escolha revistos pela D48

A página "Previsão de demanda" saiu da máscara. Laboratório de ML em `ml/` (snapshot congelado do BigQuery, só SELECT; régua única de origem móvel jan–set/2026, h1–h3; 58 modelos em 6 famílias: referências, séries clássicas, ARIMA/ARIMAX, Prophet, LightGBM/XGBoost, rede neural com 1 a 16 neurônios, combinações), 6 especialistas e 3 avaliadores. **Métrica principal: WAPE de 1 a 3 meses à frente** (viés desempata; MAE em pedidos; cobertura da faixa de 80%; F1/ROC/acurácia não se aplicam). **Inbound: média dos últimos 3 meses** (D20: ninguém a vence além do ruído; 22,0%, viés −16%). **Mercado: ARIMA em log com nível e reta** (20,3% contra 27,2% da melhor referência; vence em h1, h2 e h3; viés −7%). ARIMAX perde para o ARIMA de mesma ordem nos 8 pares; rede neural: o erro muda < 1 pp de 1 a 16 neurônios. Tela: dois gráficos (Inbound | Mercado) com o real, o previsto 1 mês antes, outubro parcial e out/nov/dez com faixa; seletor de talentos (exclusivos e não exclusivos = previsão do tipo × parcela dos últimos 6 meses fechados de 2026); modelo contra modelo; "Regras e modelos" (`<details>`); faixa do pé por regra. Números (carga de 23/10): Inbound 150/150/150; Mercado 449/487/533. O site só lê `ml/saida/previsao.json`; carga nova dispara `python -m ml.rodar --rotina` em segundo plano (J1–J4); produção precisa de job separado (ficha, seção 9). Registro de uma previsão por carga (PD09). **339 testes.** Ficha [previsao.md](paginas/previsao.md); módulo M5; decisão D47.

#### Ajuste anterior: movimento do estudo do SLA (D46, 25/10/2026, noite)

O Caio achou o estudo "Como medimos" muito estático. Três linhas de movimento debateram e um quarto agente aplicou a síntese: um gesto de dado por slide na ordem de leitura (régua → dado → cor de alerta), texto e números visíveis desde o 1º quadro, sem mola nem loop, até ~1,15 s por slide; entrada só na 1ª visita; troca de slide com View Transition no sentido da navegação e moldura parada; troca de grupo de talentos sem repetir a cena. Linha do tempo do slide 1 de 2,6 s para ~1,1 s. Só CSS (bloco D46), JS do site e agrupamentos/`pathLength` no template; nenhum número, texto ou regra mudou. Movimento reduzido: capturas idênticas às de antes. **271 testes.** Ficha `sla.md` seção 0000000000; decisão D46.

#### Ajuste anterior: revisão do estudo do SLA em batalha de agentes (D45, 25/10/2026, noite)

Dois grupos de especialistas debateram o estudo "Como medimos" (slides 1–8) e um painel aprovou 9 melhorias, aplicadas sem mudar nenhuma regra de negócio: **base congelada** na reunião (`CONGELAR`, padrão com `MODO=apresentacao`, nunca em produção; rodapé "base congelada para a apresentação"); **exemplo fixo** do slide 1 (`?exemplo=<projeto_id>`, só DEV ou apresentação, E4); **`tools/conferir_estudo.py`** (somente leitura, identidade e SELECT; refaz as horas no banco com os feriados de `app.expediente` e o mês do `_processado_em`; compara n, típico, A, HB, meses, status, tipos e acima de 5 dias nos 3 grupos e avisa leituras que mudaram — rodado em 25/10: tudo bate); **`tools/conferir_layout.mjs`** (4 telas × 8 slides × 3 grupos, sem rolagem nem corte); típico com `_h_meta` (C6) no slide 8, seletor, slide 2 e slide 7; slide 3 empilha no celular (cascata do CSS); "%" e base escrita nos slides 4, 6, 7 e 8 (tempo travado = 54% de todas as horas em Todos; cartão "N travaram · acima de X h"; coluna "Onde passa mais tempo"); recorte "jan a set de 2026 · N pedidos · grupo" no topo dos slides 2–8; escape dos nomes do Monday antes do `| safe`; cartões sem corte de texto; estudo guardado por carga e grupo e aquecido na carga. Não aplicado: linha visível de "travou" no slide 6 (o Caio a retirou) e a refatoração de cache (depois de 28/10). **264 testes.** Ficha `sla.md` seção 000000000; decisão D45.

#### Ajuste anterior: slides 7 e 8 do estudo do SLA e K4 revista (D42 revista, D43, D44, 25/10/2026, noite)

**D42 revista (decisão do Caio):** no slide 6, o tempo travado de um status passa a ser o **tempo inteiro**, naquele status, dos orçamentos que travaram nele (antes, só o excesso acima do limite de Tukey); "travou" e o recorte não mudam. Carga 23/10, Todos: Em elaboração (só até jul) 41% · Fila de entrada 19% · Validação Talento 11% · Produção 9% · Orçamentos 9% · Em revisão 6% · Validação Talent Manager 3% · Outros 7 status 2% → "dois pontos", 60% (exclusivos 45/20 → 65%; não exclusivos 39/15 → 54%). Reconferido no BigQuery. Gancho do slide 6 → `#7`.

**D43:** slide 7 "Em que tipo de pedido o tempo trava?" (regras J1–J9): tabela-gráfico por `tipo_de_input` (coluna da própria gold de movimentos, atributo do projeto) com barra 100% (até 2 dias × passam de 2 dias), linha tracejada do geral, típico e onde mais trava (etapa com mais horas entre os que passam de 2 dias); tipos com ≥ 30 pedidos têm linha (o resto em "Outros", fora da tela); maior volume = ≥ 10% dos pedidos. 2ª rodada do Caio no mesmo dia: sem nota embaixo, análise só na faixa do pé (1 linha), letras menores, barras finas e cores com significado (vermelho só para tipo com B ≥ geral + 3 pontos). Todos: Mercado 55/45 · Inbound 57/43 (maior volume, 81%); ViU 79/21 · **Proativo 33/67** · **Interna 32/68** · Globo 74/26 → "Os tipos de maior volume ficam perto do geral… Só Proativo e Interna, de menor volume, passam bem mais." Exclusivos: "O Inbound é o que mais demora: 43%… contra 38% — e trava mais na fila de entrada." Conferido no BigQuery. Ficha `sla.md` seção 0000000.

**D44:** slide 8, conclusão "O que os dados nos mostraram" (regras Z1–Z8): seis achados das mesmas funções dos slides 2–7 (típico 14 h e média 25 h; 56% em até 2 dias; 84% do tempo nos 44%; "todo mês", de 40% a 51%, com o volume crescendo; trava em dois pontos, 60%; tipos parecidos 43–45%), cores por regra, "Onde olhar com mais detalhe" (2 status de maior trava com perguntas + pedidos acima de 5 dias, 12%/289) e "O que isso pede" (texto do Caio); "8 de 8"; fim com link para o slide 1. Ficha `sla.md` seção 00000000. **256 testes.**

#### Ajuste anterior: slide 6 do estudo do SLA — "Onde o tempo trava?" (D42, 25/10/2026, noite)

**D42:** slide 6 do estudo "Como medimos" pela referência do Caio, com a 2ª rodada dele no mesmo dia (sem a linha explicativa na tela; cartões estreitos, da mesma largura e altura, "N travaram · típico" numa linha e a nota "só até" à parte; Aguardando Feedback na mesma largura). Uma linha por etapa do ciclo (1 Entrada, 2 Elaboração, 3 Revisão, 4 Entrega) com um cartão por status: parte do **tempo travado** (K4: soma das horas acima do limite de Tukey do próprio status, Q3 + 1,5 × IQR), quantos travaram e o típico (mediana); os 2 maiores em destaque; até 3 cartões por etapa e o resto em "Outros N status"; Retorno da marca tracejado (fora da conta, D-SLA-2); faixa do pé por regra (um ponto > 50% / dois pontos / espalhado < 40%). Base = a dos slides 2–5, com as horas da equipe abertas por status (`horas_por_status`; soma por orçamento = `h_trabalho`). Carga 23/10, Todos: **Em elaboração (status geral, só até jul) 56%** · Fila de entrada 12% · Orçamentos 9% · Produção 8% · Validação Talento 8% · Em revisão 4% · Validação Talent Manager 2% · Outros 7 status 1% → "um ponto". **Ressalva para o Caio:** o "Em elaboração" geral só existiu até maio e o tempo travado dele vem quase todo dos cards "[Pacote"; sem pacotes, a ordem vira Fila 28% · Orçamentos 22% · Validação Talento 19%; só jun–set, Orçamentos 25% · Produção 24% · Validação Talento 22% · Fila 18%. Decisões abertas: excesso × tempo inteiro (K4) e universo (ano × jun–set × sem pacotes). Conferido no BigQuery (n, típico, limite, travaram e excesso por status, três grupos). Seletor em `#6`; gancho do slide 5 ligado a `#6`. Regras K1–K8; ficha `sla.md`, seção 000000. **243 testes.**

#### Ajuste anterior: slide 5 do estudo do SLA — "Foi um mês ruim, ou é sempre assim?" (D41, 25/10/2026, noite)

**D41:** slide 5 do estudo "Como medimos" pela referência do Caio, com os ajustes dele no mesmo dia: dispersão por mês (um ponto por orçamento, posição fixa pelo hash do id, 3 `<path>` gerados no servidor), eixo congelado com os 12 meses (out–dez vazios, nome em cinza/itálico), faixa onde fica a maioria (Q1–Q3) e típico de cada mês, linha de 2 dias, triângulos acima de 10 dias e, abaixo do eixo, "passam de 2 dias" (B do mês = 100 − "até 2 dias" da página, C8) e pedidos. A faixa do pé responde "sazonal ou padrão da equipe?" por regra (U7: mês destoa se B > mediana dos B + 10 pontos ou típico > mediana dos típicos + 4 h; 0 → padrão, 1–2 → picos, 3+ → sazonal; todos < 10% → raro) e diz o que fazer. Carga 23/10: Todos e Exclusivos **padrão** ("Não é sazonal: todo mês, de 40% a 51% / 29% a 47% dos pedidos passam de 2 dias. O problema é o processo, não o mês — é nele que está a solução."); Não exclusivos **sazonal** ("Há meses mais pesados: em abril, maio e agosto, de 70% a 75% passam de 2 dias, contra 43% a 60% no resto do ano. Vale planejar a equipe para esses meses."). Gancho "Se é assim, onde o tempo trava?". 2ª rodada do Caio: tom visual mais leve (sem negrito nos textos do gráfico, cores suaves, pontos e linha mais finos) e faixa do pé em 1 linha. Mesmo seletor (`#5`); gancho do slide 4 virou link para `#5`. Conferido no BigQuery (27 grupo × mês). Regras U1–U9; ficha `sla.md`, seção 00000. **234 testes.**

#### Ajuste anterior: slide 4 do estudo do SLA — "Para onde vai o tempo?" (D40, 25/10/2026, noite)

**D40:** slide 4 do estudo "Como medimos" pela referência do Caio: cartões "Saem em até 2 dias" (A) e "Passam de 2 dias" (B) com a parte dos pedidos (os mesmos % do slide 3, função única `_cem_pcts`) e a parte das horas da equipe (soma das horas por faixa ÷ total, maior resto, HB = 100 − HA), barras de 0 a 100, frase por regra em frações por extenso (`_fracao`), linhas por faixa, notas Prazo e Fluxo, faixa do pé com variantes (A > 50 / = 50 / < 50, B = 1, B = 0) e gancho "Mas esses B% foram um mês ruim, ou é sempre assim?" (só texto; slide 5 depois). Mesmo seletor de talentos (`#4`); gancho do slide 3 virou link para `#4`. Carga 23/10: Todos 56/16 · 44/84; Exclusivos 62/19 · 38/81; Não exclusivos 41/12 · 59/88 (pedidos/horas em até 2 dias · acima de 2 dias). Conferido no BigQuery. Regras V1–V8; ficha `sla.md`, seção 0000. **220 testes.**

#### Ajuste anterior: slide 3 do estudo do SLA — "De cada 100 pedidos" (D39, 25/10/2026, noite)

**D39:** slide 3 do estudo "Como medimos" pela referência do Caio: waffle de 100 (proporção do recorte, 5 faixas ≤ 8 / 8–16 / 16–24 / 24–40 / > 40 h), chaves "A em até 2 dias" / "B passam de 2 dias" (A coerente com a página e o slide 2), curva acumulada até o P97 com os marcos de 2 dias, 80% e 90%, mesmo seletor de talentos (links para `#3`) e faixa do pé na redação do Caio ("Em uma amostra aleatória de 100 pedidos, A ficam prontos… e B levam mais de 2 dias."). Gancho do slide 2 virou link para `#3`. Carga 23/10: Todos 31/25/15/17/12 → 56/44, 80% em 4 dias (31 h), 90% em 6 dias (46 h); exclusivos 37/25/14/14/10 → 62/38, 3 dias e meio (28 h), 5 dias (40 h); não exclusivos 18/23/20/23/16 → 41/59, 4 dias e meio (36 h), 7 dias (57 h). Conferido no BigQuery. Regras W1–W7; ficha `sla.md`, seção 000. **185 testes.**

#### Ajuste anterior: meta do SLA em 2 dias e estudo em linguagem simples (D38, 25/10/2026, noite)

**SLA (D38, 25/10/2026, noite):** meta sugerida = **metade dos orçamentos em até 2 dias de trabalho (16 h)** (D-SLA-7, revisa a D-SLA-3: "75% em até 3 dias"); faixas até 1 dia / 1 a 2 dias / acima de 2 dias; linha em 50% "meta sugerida: 2 dias úteis"; mensagem do típico pela mediana exata (16,3 h fica fora); "N% passam de 5 dias de trabalho (M orçamentos)" sem meta. Estudo em % do total, "limite estatístico" (Tukey, não é a meta), "demorados"/"outliers", marca da meta no boxplot, Q-Q contando orçamentos reais acima do teto e uma frase por passo na faixa do pé só com números visíveis no gráfico. Todos 56% em até 16 h · 12% acima de 40 h; exclusivos 62 · 10; não exclusivos 41 · 16 (típico 20 h, 4 h acima). Ficha `sla.md`, seção 00. 170 testes.

#### Ajuste anterior: correções de 25/10/2026 (D36, D37) e PRD em módulos

**Início, Talentos e Atendimento (D36):** itens da auditoria e as decisões 1–14 de 25/10 (cartão do gráfico com os
tokens `--cartao-*` no Início e no Atendimento; seta pastel na coluna Var. do Início, revisando a D26; `<1%`; Talentos
mostra os números com aviso em vez de bloquear; divergência em safra antiga só no log; top 10 com nota de empate;
Atendimento com "− Entregues ao cliente"; no celular, "Próxima pergunta" e rodapé no fim do slide; rodapé pelo
`_processado_em`). Números das três páginas **inalterados** (5.520; 3.435 / 1.955 / 130; 5.360 / 160).
**SLA (D37):** regras D-SLA-1 a D-SLA-6 — mês da 1ª entrega, sem "Retorno Marca/Executivo", **meta sugerida 75% em até 3
dias** com a faixa "2 a 3 dias", só meses completos de entrega, mês vigente vazado, mediana por mês sob o gráfico,
cobertura no estudo (2.348 de 3.553, 66%) e slide 2 refeito (razão das metades 1,7×, Q-Q sino × log-normal, boxplot em
log com limite de 210 h). Tela de hoje: **14 h · 2,8 dias · 31/25/15/29 (71% em até 3 dias)**, conferida no BigQuery.
Pendência nova **PD21**. **PRD reorganizado:** [Módulos do portal, página por página](#módulos-do-portal-página-por-página)
(pergunta, resposta, decisões, regras, base, SQL, resultado, atualização e pendências de cada página) e [Como o portal
funciona](#como-o-portal-funciona). Ajustes de tela de 25/10 (tarde): rodapé do estudo "Como medimos" no fluxo do slide
no celular. **152 testes.** Servidor local na porta 8090.

#### Ajuste anterior: slide 2 do estudo "Como medimos" (D35, 24/10/2026) — substituído pela D37 no que muda

**Slide 2 do estudo do SLA** (`/viu-agenciamento/sla/como-medimos#2`): "A maioria é rápida. Poucos demoram muito.",
regras **X1–X7** (seção 9.1): histograma de 4 h do tempo da equipe com o seletor de talentos em cima, painel em três
passos (assimetria, Q-Q, boxplot) e conclusão de cada passo na faixa do pé. Todos os números conferidos no BigQuery
(só SELECT, carga de 23/10 20:23 UTC): **batem com a tela** nos três grupos (Todos 2.425 · 15 h · 27 h · +7,1 · 72% ·
53/32/15 · 515 h · 7/29/62 h · 25/50/18/7). Avaliação estatística (ficha `sla.md` 8.1): conta certa, mas a assimetria
de 7 vem quase toda de 74 cards "[Pacote" criados em lote (sem eles, 2,8), a distribuição é quase log-normal e a cerca
Q3 + 1,5 × IQR marca ~7% pelo formato da cauda; recomendações para decisão do Caio. Comparação dos grupos (X7) fora
da tela, calculada. **116 testes.** Memória e SQL: ficha 3.2 (mapa), 5.5, 6.7–6.9.

#### Ajuste anterior: SLA redesenhado e estudo "Como medimos" (D34, 24/10/2026) — em construção

**SLA (aba "SLA", título "SLA de entrega") em construção com o Caio (D34).** Página única: resposta tipográfica "Levamos
**15 h** de trabalho da equipe para entregar um orçamento ao cliente." + "**2,9 dias** no calendário para o cliente
receber" (medianas C2 e C3 dos meses completos; exclusivos 13 h / 2,0; não exclusivos 21 h / 4,1); seletor de talentos
abaixo da pergunta; gráfico em trilhos 0–100% por mês com meta 75%, num cartão; lupa "Estudo" que abre
`/viu-agenciamento/sla/como-medimos` (slide 1 "Como chegamos ao tempo da equipe", regras **E1–E3**; slide 2 em branco).
Saíram da tela: "Leitura" (C11), "Como a meta é calculada", "No ano (jan a set):", "Medianas de N pedidos…", "(fora do
gráfico)" e os slides de cauda e exclusivos × não exclusivos (`leituras()` segue no código). Reconferido no BigQuery em
24/10 (só SELECT, carga de 23/10 20:23 UTC), com SQL que refaz o expediente sem almoço no próprio banco. **Memória de
cálculo página por página: seção 9.6** (tabelas, colunas, SQL e resultado esperado de cada número). Ficha
[sla.md](paginas/sla.md). **114 testes.**

#### Ajuste anterior: Página Atendimento entregue (D33, 24/10/2026)

**Atendimento ENTREGUE (D33).** Estado final aprovado pelo Caio: título "A equipe está dando conta da demanda?"; faixa
marinho escura, reta e baixa, com os números do ano (Recebidos em 2026 5.520 → Resolvidos 5.360, 97% → Em andamento 160,
3%; data de corte "Até 22 de outubro" em letra vazada à direita) e régua 100% (4.388 entregues ao cliente, 972 saíram
sem entrega, 160 em andamento); bloco branco flutuante com o **quadro do extrato** mês a mês em 7 linhas (A24) e a **dispersão** sobre a demanda total
(A16). Regra nova **A25**: o % do mês é (entregues + encerrados sem entrega) ÷ para atender (represados + novos): 77, 80,
76, 78, 81, 80, 87, 87, 79, 77; a dispersão compara com o objetivo (equilíbrio 100%, corte 90%) e os 10 meses ficam
abaixo de 90%. Reconferido no BigQuery em 24/10 (só SELECT). Navegação no mesmo dia: moldura congelada entre
páginas, View Transitions, pré-carga (Speculation-Rules), aba "Prazo" renomeada para "SLA" (título "SLA de entrega") e
Prazo numa página só. Memória e decisões na seção 9.5; ficha [atendimento.md](paginas/atendimento.md). **112 testes.**
O bloco abaixo (visual executivo com cartões e A14) foi **substituído** pela D33 e fica como histórico.

#### Ajuste anterior (substituído pela D33): revisão geral de código, padronização do navegador e visual executivo de Atendimento (24/10/2026)

1. **Padronização do navegador (`.navegador` / `.cabecalho`) entre todas as páginas**: removida de `app/static/estilo.css` a sobrescrita em `.atendimento-executivo` que alterava `font-size`, `width`, `height` e `padding` de `.lamina` (causa de o cabeçalho e as abas do navegador mudarem de tamanho ao abrir Atendimento). Agora todas as páginas compartilham a mesma escala proporcional (`calc(min(100cqw, 177.78cqh) / 80)`) e o mesmo espaçamento (`2em 3.5em 1.2em`).
2. **Novo desenho visual de `/viu-agenciamento/atendimento#1`**: alinhado ao sistema editorial VIU das demais abas (`Início`, `Talentos`, `Prazo`), com `.sobretitulo` (`Gerencial` + recorte da safra), traço azul sob o título, cartões `.ae-card` em `.fundo-2` com barra lateral de 3 px na cor da série, números em `Playfair Display` (`var(--serifa)`), pílula `.ae-pct`, rodapé do gráfico em cápsula `.ae-rodape-grafico` e painel lateral `.ae-foco` com selo semântico do saldo da fila (`.ae-selo-saldo`) e balanço tabular.
3. **Correções de bugs e melhorias de código**:
   - `app/apresentacoes/gestao_orcamentos/atendimento/calculos.py`: percentuais de destino (`pct_entregues`, `pct_sem_entrega`, `pct_fila`) fechando sempre em `100,0%` pelo maior resto em décimos (`_pcts_decimos`); foco (`atual`) mantido no último mês com movimento quando o mês parcial recém-aberto na virada está zerado; filtro defensivo `mes_evento <= mes_parcial` em `atendimento()`.
   - `app/apresentacoes/gestao_orcamentos/talentos/calculos.py`: arredondamento meio para cima (`_pct`) em `top_por_grupo()`, alinhado à regra T2.
   - `app/apresentacoes/gestao_orcamentos/apresentacao.py`: recorte até `entrada.ultimo_dia(diaria)` em `_mesma_fotografia()`.
   - `app/dados.py`: lock (`_trava_cliente`) na criação do cliente BigQuery e `TIMEOUT_BQ = 45.0` em `get_table()` e `query()`.
   - `tools/auditar_relatorio.py`: suporte a instâncias `dados.Consulta` (`talentos`, `talentos_top`) com parâmetro `@fim`.
   - `app/templates/regras.html`, `atendimento/template.html` e `app/static/apresentacao.js`: página `/viu-agenciamento/atendimento/regras` atualizada para os indicadores vigentes; filtro `| inteiro` e `scope="col"`/`scope="row"` em Atendimento; leitura direta de `<style>` no extrato via DOM.
4. **Validação**: **101 testes passando** (`pytest`). Detalhes em `docs/paginas/atendimento.md` e `docs/historico/REVISAO_2026-10-24.md`.

#### Revisão vigente — 24/10/2026, após ajustes das três páginas

[Revisão e continuidade](historico/REVISAO_2026-10-24.md) registra correções, evidências e limites atuais, sem renumerar decisões anteriores. **96 testes**. Atendimento: fluxo e fila, com 160 em andamento (antes 170, por dez saídas sem mês). Talentos: 5.520 conciliados, ranking exato, recarga por origem e corte. Início: proteção da fotografia na troca do extrato e correção de virada de ano. Aba aberta acompanha nova assinatura; nenhuma implantação externa realizada. Pendências novas PD19 (data das saídas/carga) e PD20 (origem multianual); PD13 continua necessária para fechamento histórico. Descrições antigas de comparações e taxas de Atendimento abaixo são histórico, não o layout vigente.

### 12.2 Retrato do código de 23–25/10/2026 (abria a seção "Estado atual do código")

> **25/10/2026 (D36, D37).** **SLA:** mês = mês da 1ª entrega (D-SLA-1); horas da equipe sem "Em elaboração - Retorno
> Marca/Executivo" (D-SLA-2); faixas ≤ 8 / 8–16 / **16–24** / > 24 h e meta sugerida **75% em até 3 dias** (D-SLA-3);
> só meses completos de entrega nas contas (jan–set); mês vigente vazado com "parcial · até 22/10" e mediana do mês sob
> cada coluna (`MIN_PARCIAL` = 30); exemplo do estudo estável no dia (SHA-256 de data:grupo:projeto_id, fuso de São
> Paulo); cobertura no slide 1 (`cobertura()`, 2.348 de 3.553, 66%); slide 2 com razão das metades, dois Q-Q e limite em
> log (X4–X6). Tela: Todos 2.348 · 14 h · 2,8 dias · 31/25/15/29; exclusivos 1.610 · 12 h · 2,0 · 37/25/14/24; não
> exclusivos 725 · 20 h · 4,0 · 18/23/20/39. Testes novos em `tests/test_sla_20261025.py`. **Início, Talentos,
> Atendimento:** decisões 1–14 (D36), testes em `tests/test_revisao_20261025.py`. **Moldura:** rodapé pelo
> `_processado_em`; no celular, "Próxima pergunta" e rodapé no fim do slide (`apresentacao.js`; em páginas de vários
> slides, como o estudo, só o rodapé, que acompanha o slide visível). PD21 em `pendencias.py`. **152 testes.**
> Detalhe de cada página: [Módulos do portal](#módulos-do-portal-página-por-página). Os blocos abaixo são o retrato de
> 24/10 e ficam como histórico onde divergirem.
>
> **Página SLA (`/viu-agenciamento/sla`): EM CONSTRUÇÃO com o Caio (D34, 24/10/2026).** Página única (`montar_sla`,
> `sem_controles=True`): resposta tipográfica com a mediana de horas da equipe (C2) e de dias de calendário (C3) do grupo
> escolhido; seletor Todos / Exclusivos / Não exclusivos abaixo da pergunta (C10); gráfico em trilhos 0–100% por mês (até
> 1 dia, 1 a 2 dias; trilho vazio = acima de 2 dias) com meta 75% (C6), num cartão; lupa que leva ao estudo **"Como
> medimos"** (`/viu-agenciamento/sla/como-medimos`, `montar_estudo_sla`, `app/templates/como_medimos.html`, mantém
> `?talentos=`; cabeçalho sem abas, botão fechar, Anterior/Próximo sempre visíveis por `controles_sempre`). Slide 1 do
> estudo: um orçamento real sorteado no dia (`calculos.exemplo`, E1–E3); slide 2 "A maioria é rápida. Poucos demoram
> muito." (`calculos.exploracao`, X1–X7, D35).
> `leituras()` (C12–C14) e o texto da C11 seguem calculados, fora da tela. Conferido no BigQuery em 24/10 (seção 9.6;
> ficha [sla.md](paginas/sla.md)). 114 testes.
>
> **Página Atendimento (`/viu-agenciamento/atendimento`): ENTREGUE em 24/10/2026 (D33).** Faixa escura com os números
> do ano (5.520 → 5.360 resolvidos, 97% → 160 em andamento, 3%; régua 4.388 / 972 / 160) e bloco branco com o quadro do
> extrato em 7 linhas (veio + entrou = para atender − entregues − encerrados sem entrega = ficou; % respondemos do que
> havia para atender; A24, A25) e a dispersão (para atender × resolvidos, equilíbrio 100%, corte 90%; os 10 meses abaixo
> de 90%; A16, A25). Conferida no BigQuery
> (fluxo mensal × situação da gold de entradas: 4.388 / 972 / 160). Detalhe na seção 9.5; ficha
> [atendimento.md](paginas/atendimento.md). Navegação: moldura congelada, View Transitions, Speculation-Rules, aba "SLA"
> (título "SLA de entrega") com uma página só. 112 testes.
>
> **Página Talentos (`/viu-agenciamento/talentos`): ENTREGUE em 24/10/2026 (D31).** Resposta direta calculada ("62% da
> demanda do ano se concentra nos talentos exclusivos."), barra 100% com % e quantidade dentro de cada parte, legenda com
> os três grupos (sem números) e dicas com os **10 talentos mais pedidos** de cada grupo (T6, `app/sql/talentos_top.sql`),
> com a coluna "Último". Conferida no BigQuery (carga de 23/10, dados até 22/10): 3.435 / 1.955 / 130 = 5.520 = Início;
> top 10 exclusivos 1.802 (52%), não exclusivos 221 (11%). Segue lendo a silver por exceção (D30-b) até a PD01. Detalhe e
> decisões do Caio na seção 9.4; ficha [talentos.md](paginas/talentos.md). **Prazo:** arredondamento do slide 2 alinhado
> ao slide 1 (C12, 24/10: 29/24/15/17/15). 89 testes.
>
> **Área como portal (D30, 23/10/2026).** Ordem da reunião: Início → Talentos → Atendimento → Prazo (SLA) → Previsão →
> Resultado → Qualidade → "O que falta". Cada seção tem `pergunta` (vira o h2 e a "próxima pergunta"), `estado`
> (pronta / parcial / pendente) e `na_reuniao`. Seções sem base mostram a pergunta com **máscara** ("Aguardando dados":
> dado · onde · quem), gerada de `gestao_orcamentos/pendencias.py`, fonte única das máscaras, da página **"O que falta"**
> (`/viu-agenciamento/o-que-falta`: estado das seções, pedidos de decisão e tabela PD01–PD18) e do
> [prompt para a gold](prompt_dados_pendentes.md) (**rascunho**: vai ao Caio só quando as páginas estiverem fechadas). **Talentos**
> (entregue na D31): divisão anual de 2026 (62% exclusivos) e top 10 por grupo, lidos da silver por exceção (D30-b). **Prazo** com 3 slides (tempo até a 1ª entrega, cauda C12, exclusivos × não
> exclusivos C13–C14), revalidado no BigQuery em 23/10 (bate exatamente). **Modo apresentação** (`MODO=apresentacao`):
> só as seções `na_reuniao` (ou `SECOES_VISIVEIS`), sem tela de exemplo. Abas do topo só com texto (revisa D18).
> 89 testes. Fichas: [talentos.md](paginas/talentos.md), [sla.md](paginas/sla.md), [o_que_falta.md](paginas/o_que_falta.md).
>
> **Página Início (`/viu-agenciamento`): ENTREGUE em 23/10/2026 (D28).** Validação final em três camadas (gabarito do
> código × gold × silver, 4 validadores, 624 itens): **0 divergências de número**. Correções finais B1, B2, B3, B5, B6
> (cálculo), B7 e B8 aplicadas; 83 testes. Ficha auditável: [docs/paginas/inicio.md](paginas/inicio.md) (regras,
> origem de cada número, memória de cálculo, passo a passo gold e silver, **checagem diária** na seção 6.4).
