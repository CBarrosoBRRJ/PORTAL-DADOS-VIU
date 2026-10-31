# Ficha — Início (entrada de pedidos de orçamento)

## Retrato da carga da reunião (26/10/2026)

> **Estado (26/10/2026):** ENTREGUE (D28), regras inalteradas. Batalha de 26/10 (D49): números prontos desde o 1º quadro
> (saiu a contagem a partir de zero), só as colunas crescem (1,11 s), rodapé com o horário do processamento. O termo
> "represados" do extrato fica até decisão do Caio (glossário em `README.md`).

Carga `_processado_em` **26/10/2026 09:01 (São Paulo)**, dados até **25/10/2026**. Checagem Q1/Q2 (seção 6.4) rodada por
`tools/checar_reuniao.py` em 26/10, 11:33: **tudo certo**. Se a carga da reunião for outra, rodar de novo e trocar esta
tabela. A seção 5 guarda a memória da carga de 23/10 (5.520).

| Elemento | Regra | Valor (carga de 26/10) | SQL (seção) |
|---|---|---|---|
| Número do ano | E1, E4 | **5.556** pedidos até 25 de outubro | 6.2 (gold) |
| Selo e barras do mesmo período | E8, E8b | 2025 até 25/out: 2.943 → **▲ 89% a mais** | 6.2 (gold) |
| Tipos 2026 (pedidos · %) | E9, E8c | Mercado 2.974 · 54% · Inbound 1.327 · 24% · Internos 771 · 14% · Proativo 408 · 7% · Sem tipo 76 · 1% | 6.2 (gold) |
| Tipos 2025, mesmo período | E9 | Mercado 1.159 · 39% · Inbound 965 · 33% · Proativo 483 · 17% · Internos 333 · 11% · Sem tipo 3 · <1% | 6.2 (gold) |
| Var. por tipo | E8b (base mínima 30) | Mercado ▲ 157% · Inbound ▲ 38% · Internos ▲ 132% · Proativo ▼ 16% · Sem tipo "–" (base pequena) | 6.2 (gold) |
| Pedidos por mês | E1 | 374 · 341 · 485 · 472 · 629 · 569 · 765 · 644 · 733 · 544 (out, parcial) | 6.2 (gold) |
| Outubro (parcial) | E6 | 313 entregues no mês (58%) · 76 saíram sem entrega (14%) · 155 em andamento (28%); out/2025 no mesmo período 350 (+55%) | 6.2 (gold) |

## Revisão vigente — 24/10/2026

Ver [revisão](../historico/REVISAO_2026-10-24.md): total revalidado 5.520 até 22/10, fila atual do ano 160. Corte protege contra linhas futuras; ano anterior permanece fechado na virada sem novos pedidos. Extrato exige mesma carga e população mensal da entrada; troca de fotografia atualiza a página inteira. Mantidos os seis meses recentes com movimento para detalhamento e o histórico simples nos anteriores. A aba aberta verifica novas cargas. Os saldos são reconstruídos com a situação atual; PD13/PD19 tratam fotografias e datas ausentes. A validação de 624 itens citada abaixo é da revisão anterior, não repetida integralmente neste dia.

> **Situação: ENTREGUE em 23/10/2026 (D28).** Validada em três camadas (gabarito do código × gold × silver; 4 validadores
> independentes, 624 itens, **0 divergências de número**). Correções finais B1, B2, B3, B5, B6 (cálculo), B7 e B8
> aplicadas no mesmo dia. 83 testes. Checagem diária na seção 6.4.

## 1. Identificação

| Item | Valor |
|---|---|
| Rota | `/viu-agenciamento` (extrato do mês: `?mes=AAAA-MM`) |
| Cálculo | `app/apresentacoes/gestao_orcamentos/entrada/calculos.py` — `entrada()` (E0–E9), `extrato()` (E7), `meses_extrato()` (E7), `data_carga()` (E3/E7), `ultimo_dia()` (E3), `regua_anterior()` (E8), `variar()` (E8b), `_pct()` / `_pcts()` (E8c), `_situacao()` (E6) |
| Montagem | `app/apresentacoes/gestao_orcamentos/apresentacao.py` — `montar_inicio()` (meses que abrem extrato, aviso de cargas diferentes) |
| Template | `app/apresentacoes/gestao_orcamentos/inicio.html`; macro `resposta` em `app/templates/macros.html` |
| Formatação | `app/formato.py` — `inteiro`, `pct`, `variacao` (meio para cima, menos tipográfico), `sentido` |
| Testes | `tests/test_qualidade_previsao.py` (`test_entrada_mensal_por_tipo`, `test_extratos_janela_global_de_seis_meses`, `test_origens_das_entregas_mantem_mes_e_ano`, `test_parcelas_fecham_em_100_e_base_minima`, `test_mes_parcial_por_tipo_ignora_dias_depois_do_limite`), `tests/test_inicio_revisao.py` (B1–B8), `tests/test_rotas.py` (página), `tests/test_atendimento.py` (E9, base mínima), `tests/test_formato_variacao.py` |
| Tabelas | `gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_entrada_diaria` (`TAB_ENTRADA`: número, tipos, meses, situação); `gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_fluxo_mensal` (`TAB_FLUXO`: extrato) |
| Regras da gold | `../PPD-GOLDEN-AGENCIAMENTO-MONDAY/sql/gld_agenciamento_entrada_diaria.sql` e `.../gld_agenciamento_fluxo_mensal.sql` (R2 estimadas, R6 data manda sobre o board, R13 saída, R21 cadastro retroativo) |
| Carga de referência | entrada processada em 23/10/2026 20:23:49 UTC, fluxo 20:24:38 UTC (mesmo dia em São Paulo); dados até **22/10/2026** |

### 1.1 Tabelas e colunas consumidas

**Vigente desde 27/10/2026 (D57: o site só lê a gold).** Conferido com `app/dados.py`; código antigo × novo sobre a mesma
carga real (27/10, 11:11): número, meses, tipos e os 6 extratos iguais.

| Gold (BigQuery) | Tipo · `dados.` | Colunas usadas | Para quê |
|---|---|---|---|
| `gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_entrada_diaria` (`TAB_ENTRADA`) | tabela · `entrada` | as da tabela abaixo | número, tipos, meses, situação |
| `gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_fila_mensal` (`TAB_FILA`) | view (sobre o fluxo) · `fila` | `mes`, `mes_entrada`, `do_ano`, `novos`, `represados`, `entregues`, `nao_seguiram`, `seguem`, `_processado_em` | extrato do mês (E7): a fila pronta por mês × safra (regras FM1/FM2 da gold) |
| `gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_fluxo_mensal` (`TAB_FLUXO`) | tabela · `fluxo` | `mes_entrada`, `quantidade`, `_processado_em` | só a conferência de carga (B7): mesmo dia e mesma safra da entrada |

SQL para reproduzir o extrato de um mês: `SELECT * FROM `gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_fila_mensal` WHERE mes = DATE '2026-10-01'`
(a soma por safra dá represados, novos, entregues, não seguiram e seguem da tela).

Estado de 24/10/2026 (registro; o extrato era calculado no site a partir do fluxo):

| Tabela (nome completo no BigQuery) | Grão | Colunas usadas | Para quê |
|---|---|---|---|
| `gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_entrada_diaria` (`TAB_ENTRADA`, `COLUNAS_ENTRADA`) | dia × grupo × tipo × família (chave `data, grupo_input, tipo_de_input, familia`) | `data`, `quantidade`, `quantidade_estimada` (E1); `grupo_input` (E2, E9); `tipo_de_input` (E5); `entregue_no_mes`, `entregue_depois`, `nao_seguiu`, `em_andamento` (E6); `_processado_em` (E3, rodapé, B7) | número, tipos, meses, situação |
| `gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_fluxo_mensal` (`TAB_FLUXO`, `COLUNAS_FLUXO`) | safra × evento × mês do evento × grupo × tipo × família | `mes_entrada`, `evento`, `mes_evento`, `quantidade` (E7); `_processado_em` (B7) | extrato do mês (fila) |

Lidas pelo contrato e não usadas nesta página: `familia` (só na chave das duas tabelas), `quantidade_saida`
(Atendimento, A1) e, no fluxo, `grupo_input` e `tipo_de_input` (a dica "Novos pedidos por tipo" vem da entrada diária). Detalhe
número a número na seção 4.1; SQL na seção 6. Cargas reconferidas em 24/10/2026: entrada 23/10 20:23:49 UTC, fluxo
20:24:38 UTC; 5.520 pedidos até 22/10.

## 2. Pergunta e resposta esperada

**Título:** "Quantos pedidos de orçamento chegaram ao longo de 2026 até o momento?" (o ano vem dos dados, E0; ano já
fechado: "…chegaram em AAAA?"). Escolha do Caio, 23/10/2026.

**Resposta (carga de referência):** chegaram **5.520 pedidos** de 01/01 a 22/10/2026, **91% a mais** que no mesmo período
de 2025 (2.890). Mercado é a maior origem (53%, +160%); Proativo é o único tipo que caiu (−13%). Julho foi o maior mês
(765). Outubro, parcial, tem 508 pedidos até o dia 22 (+71% sobre 1–22/10/2025).

O leitor precisa sair sabendo, nesta ordem:
1. **Quantos pedidos chegaram no ano até hoje** (5.520 até 22/10).
2. **Se isso é mais ou menos que no ano passado, no mesmo período** (▲ 91% a mais que 2025; 2.890 no mesmo período).
3. **De onde vieram** (tipo de input: Mercado 53%, Inbound 24%…) e como cada origem mudou contra 2025.
4. **Como foi cada mês** (gráfico), com a situação do mês ao passar o mouse e o extrato (fila) ao clicar nos 6 meses
   mais recentes com pedidos.

## 3. O que aparece na tela

| Elemento | Texto na tela (carga de referência) | Regra | Origem do número |
|---|---|---|---|
| Título | Quantos pedidos de orçamento chegaram ao longo de 2026 até o momento? | E0, E4 | ano do último dia coberto |
| Disposição (D52, 26/10/2026) | coluna da esquerda em dois quadrantes: em cima a nuvem de palavras (resposta + apoio); embaixo a caixa cinza de altura fixa (tabela de tipos ↔ extrato). Cartão do gráfico à direita, com o pé no pé da caixa cinza e a altura do cartão do SLA | D52 | — |
| Número | **5.520** (nuvem: "Chegaram **5.520** *pedidos de orçamento* em 2026, até 22 de outubro", D52) | E1 | entrada_diaria, 2026 até 22/10 |
| Período | em 2026, até 22 de outubro (antes da D52: "pedidos até 22 de outubro") | E3, E4 | `_processado_em` − 1 dia |
| Selo e barras | "▲ 91% a mais que em 2025"; barras 2026 (5.520) × 2025 (2.890), proporcionais, base zero; sob as barras, `mesmo período: até 22/out` (decisão 2, 25/10/2026: 2.890 não é o ano inteiro de 2025, que tem 3.586; o selo não comporta a frase longa ao lado do número; some com o ano fechado) | E8, E8b | entrada_diaria, 2025 até 22/10/2025; `ate_curto` = último dia da carga |
| Tabela "Tipo de input" | colunas 2026 (Pedidos, %), 2025 (Pedidos, %), Var.; linha Total = número do topo; 2025 em cinza; **Var. com seta pequena em tom pastel** (decisão 3, 25/10/2026, revisa a D26): `▲ 133%`, `▼ 13%`, `▲ 38%`, `▲ 160%`, Total `▲ 91%`; seta verde `--var-sobe` #3e9b62 (3,2:1 sobre a caixa) na alta e vermelha `--var-desce` #d0605a (3,5:1) na queda; número em `--tinta`, sem sinal (o leitor de tela ouve "alta de"/"queda de"); "–" quando a base de 2025 é pequena (E8b), com o motivo também para o leitor ("base pequena no ano anterior", IN-A1). Parcela que arredonda a 0 com pedidos mostra **`<1%`** (decisão 4): hoje Sem tipo 2025 = 3 → `<1%` | E2, E9, E8b, E8c | entrada_diaria por `grupo_input` |
| Dica do tipo | só em **Internos** (lista fixa `GRUPOS_COM_DICA`): valores de `tipo_de_input` do grupo com quantidade (ViU, Interna, Globo, ViU First, OTR) | E5 | entrada_diaria por `tipo_de_input` |
| Gráfico | **cartão flutuante** (INI-CARTAO + decisão 1, 25/10/2026), no mesmo padrão do SLA: classe `.colunas.cartao-grafico` com os tokens `--cartao-*` (fundo branco, borda 1px rgba(30,42,120,.07), raio 18 px, sombra marinho); **título visível** `Pedidos por mês em 2026, por tipo de input` (ano dos dados); topo do cartão = topo do número (228 px em 1440×900) e pé = pé da área (781 px, igual ao SLA); sem trilhos 0–100% (volume, não proporção); totais em peso 400 `--tinta-2`. Colunas empilhadas por tipo, jan–dez; total no topo; mês parcial com selo "parcial"; meses futuros vazios, com o nome em itálico `--tinta-3` (IN-A1: antes cinza de 2,7:1) | E1, E2, E3 | entrada_diaria por mês × grupo |
| Dica do mês (mouse no nome do mês / foco) | "Outubro 2026 parcial · 508 pedidos entraram"; as 4 situações com n e %; "Outubro de 2025 (mesmo período): 297 +71%"; "Clique para ver o extrato do mês" nos meses com extrato | E6, E8, E8b, E8c | colunas de situação da entrada_diaria |
| Extrato (clique num dos 6 meses) | "Análise mensal · Outubro de 2026 · 681 pedidos na demanda do mês"; Represados do início do mês 173 (25%); Novos pedidos 508 (75%); "O que aconteceu com a demanda": Entregues 419 (62%) — 286 dos novos pedidos (56% deles), 133 dos represados (77% deles); Saíram sem entrega 102 (15%); Represados hoje 160 (23%) ("Represados no fim do mês" nos meses fechados) | E7, E8c | fluxo_mensal |
| Dica dos represados (início e fim) | tabela por mês de entrada: Mês, Represados, Entregues, Saíram sem entrega, Em aberto e Total; "hoje" acrescenta a linha do próprio mês ("parcial" ou "novos") | E7 | fluxo_mensal por `mes_entrada` |
| Dica "Mês de entrada dos represados entregues" | Setembro 131, Agosto 1, Março 1 (out/26) | E7 | fluxo_mensal |
| Dica "Novos pedidos por tipo" | tabela out/26 (Pedidos, %) × out/25 (Pedidos, %) × Var.; no parcial "até 22/10" nos dois anos; Total com 100% | E1, E2, E8, E8b, E8c | entrada_diaria |
| Dica "Saíram sem entrega" | "O pedido foi declinado, pausado (standby) ou encerrado antes da entrega." | E7 | texto fixo |
| Aviso | "O extrato está sendo atualizado. Tente novamente em alguns minutos." quando entrada e fluxo são de dias de carga diferentes, uma safra **do ano exibido** diverge ou os novos do fluxo ≠ coluna do mês. Divergência só numa safra de ano anterior (2024/2025) vai ao log (WARNING) e não esconde nada (decisão 5, 25/10/2026) | E7 (B7) | `_processado_em` das duas tabelas |
| Rodapé | Dados até 22/10/2026 · atualizados em 23/10/2026, 17:23 | E3 | **`_processado_em`** da carga em memória (INI-D1, 25/10/2026; antes o metadado `modified`, 17:24, que muda também com um ALTER só de descrições); sem a coluna, cai no `modified` |
| Leitor de tela | cada mês: total, situações, tipos e o mesmo mês de 2025; no mês parcial, "Em outubro de 2025, no mesmo período (até 22/10): 297 (+71%)." (INI-D2, 25/10/2026: antes dizia só "Em outubro de 2025: 297", mas o outubro inteiro de 2025 tem 459); tabelas das dicas como uma frase por linha | acessibilidade | — |
| Foco no mês | com o extrato aberto, só as colunas (`.pilha`) dos outros meses esmaecem; o total de cada mês (`.pilha-total`) continua legível em `--tinta-3`, sem opacidade reduzida (`app/static/estilo.css`); sem JavaScript, o link recarrega a página | D29 (contraste) | — |

## 4. Regras (código: docstring de `entrada/calculos.py`)

| ID | Regra | Fórmula / critério | Decidido |
|---|---|---|---|
| E0 | Ano mostrado | ano do último dia coberto pela carga (E3); sem seletor (`?ano=` ignorado); se o ano novo ainda não tem pedido, o último ano com dados | Caio, D26 |
| E1 | Pedidos | Σ `quantidade` + Σ `quantidade_estimada` (todas as famílias; estimada = data calculada pela gold, R2) | Caio, D23 |
| E2 | Grupos de tipo | `grupo_input` em ordem fixa Mercado, Inbound, Proativo, Internos, Sem tipo; valor fora da lista → "Sem tipo"; a cor segue o grupo | D25 |
| E3 | Último dia e mês parcial | último dia = data de `MAX(_processado_em)` em America/Sao_Paulo − 1 dia (sem metadado: maior `data` da tabela, só no computador); mês parcial = mês de (último dia + 1) | D23 |
| E4 | Período do número | ano em andamento: "até D de mês"; ano fechado (inclusive quando o último dia é 31/12): "de janeiro a dezembro"; base que começa no meio do ano: "de mês a dezembro" / "de mês até D de mês" | Caio, 23/10 |
| E5 | Composição do grupo | Σ pedidos por `tipo_de_input` dentro do grupo, no ano; vazio = "vazio no board"; dica só em Internos | D25, Caio |
| E6 | Situação da safra | Σ `entregue_no_mes`, `entregue_depois`, `nao_seguiu`, `em_andamento` das linhas do mês (somam os pedidos; foto do dia) | gold, D24 |
| E7 | Extrato = fila do mês *p* | ver E7 abaixo | D23, D25; fila pedida pelo Caio em 23/10 |
| E7 janela | Meses que abrem extrato | os **6 meses mais recentes com pedidos** (Σ n > 0) na base inteira até o último dia; mês vazio não ocupa vaga; a lista (`meses_extrato`) atravessa anos, mas a tela **só abre os do ano mostrado**: extratos do ano anterior não aparecem em janeiro (decisão do Caio, D29). Demais meses: só a fotografia (dica) | D26, D29; B5/B6 em 23/10 |
| E7 carga | Cargas de dias diferentes | extrato escondido com aviso se `data_carga(entrada) ≠ data_carga(fluxo)` ou se os novos do fluxo ≠ total da coluna do mês | B7, 23/10 |
| E8 | Comparação com o ano anterior | só se o ano anterior tem pedido até 07/jan (base desde janeiro); total: 01/01 até o mesmo dia (último dia − 1 ano); mês fechado: o mês inteiro; mês parcial: até o mesmo dia; também por tipo | Caio, D26 |
| E8b | Variação e frase | variação = atual ÷ anterior − 1, **só com ≥ 30 no ano anterior** (total, mês, tipo, linha de total); abaixo disso "–" ou só a referência ("Em 2025 · N no mesmo período"). Percentual arredondado meio para cima **antes** da frase: > 0 "▲ X% a mais", < 0 "▼ X% a menos", = 0 "igual"/"praticamente igual" | Caio, 23/10 |
| E8c | Parcelas que fecham em 100% | parcelas de um mesmo todo pelo **maior resto** (`_pcts`): parte inteira de cada uma e +1 nos maiores restos até somar 100 (empate: ordem da lista). Vale para: tipos de cada mês e do mesmo mês do ano anterior; tipos no ano e no mesmo período do ano anterior (E9); situações do mês e do ano (E6); represados + novos e entregues + saíram sem entrega + seguem (E7). Percentuais que não são parcelas de um todo comum ("dos novos ÷ novos", "dos represados ÷ represados") usam `_pct`: inteiro meio para cima (12,5 → 13) | Caio, 23/10; estendido em 23/10 (B1–B3) |
| E9 | Tipos contra o ano anterior | por tipo, no mesmo período: pedidos e parcela (E8c) nos dois anos; Var. = pedidos ÷ pedidos do ano anterior − 1 (E8b); Total = número do topo e comparação E8 | Caio, 23/10 |

**E7 — fila do mês *p*** (só pedidos que entraram no ano de *p*; anos anteriores ficam fora da conta e da tela —
decisão do Caio, 23/10/2026). Fonte `fluxo_mensal` (`mes_entrada`, `evento` ∈ {entregue, nao_seguiu, em_andamento},
`mes_evento`, `quantidade`):

| Parte | Fórmula |
|---|---|
| Represados no início | Σ `mes_entrada` < *p* e (`evento` = em_andamento ou `mes_evento` ≥ *p*) |
| Novos | Σ `mes_entrada` = *p* (= coluna do mês no gráfico) |
| Demanda | represados + novos |
| Entregues dos novos / dos represados | Σ `evento` = entregue e `mes_evento` = *p*, com `mes_entrada` = *p* / < *p* |
| Saíram sem entrega | Σ `evento` = nao_seguiu, `mes_entrada` ≤ *p* e (`mes_evento` = *p* ou (`mes_evento` nulo e `mes_entrada` = *p*)) |
| Seguem represados ("hoje" no parcial) | Σ `mes_entrada` ≤ *p* e (`evento` = em_andamento ou `mes_evento` > *p*) |
| Fecha | demanda = entregues + saíram sem entrega + seguem; seguem(*p*) = represados(*p* + 1) |
| % | represados e novos: `_pcts` sobre a demanda; entregues, saíram, seguem: `_pcts` sobre a demanda; dos novos: `_pct(entregues_novos, novos)`; dos represados: `_pct(entregues_represados, represados)` |
| Tabelas por mês de entrada | para cada `mes_entrada` ≤ *p*: início (represado no 1º dia; no próprio mês, os novos), entregues no mês, saíram sem entrega no mês, seguem; cada linha fecha e o Total bate com a caixa |

### 4.1 Origem de cada número

| Número | Tabela | Colunas | Filtros | Métrica | Arredondamento |
|---|---|---|---|---|---|
| Total do ano | entrada_diaria | `data`, `quantidade`, `quantidade_estimada` | `data` entre 01/01/ano e último dia | Σ (quantidade + estimada) | inteiro, separador de milhar |
| Mesmo período do ano anterior | entrada_diaria | idem | `data` entre 01/01/(ano−1) e último dia − 1 ano | Σ | inteiro |
| Variação do topo | — | — | anterior ≥ 30 | atual ÷ anterior − 1 | % inteiro meio para cima, sinal pelo arredondado |
| Tipos (n) | entrada_diaria | + `grupo_input` | mesmo período, cada ano | Σ por grupo (E2) | inteiro |
| Tipos (%) | — | — | — | n ÷ total do ano | `_pcts` (maior resto, fecha em 100; "Sem tipo" 1,39% → 2% aprovado pelo Caio, D29) |
| Tipos (Var.) | — | — | anterior do tipo ≥ 30 | n ÷ n_anterior − 1 | meio para cima |
| Composição de Internos | entrada_diaria | + `tipo_de_input` | ano mostrado | Σ por tipo | inteiro |
| Coluna do mês | entrada_diaria | `data`, `grupo_input`, quantidades | mês do ano mostrado | Σ por grupo | inteiro |
| Mesmo mês do ano anterior | entrada_diaria | idem | mês inteiro; no parcial até último dia − 1 ano | Σ (total e por tipo) | inteiro; % por tipo `_pcts`; Var. meio para cima |
| Situações do mês | entrada_diaria | `entregue_no_mes`, `entregue_depois`, `nao_seguiu`, `em_andamento` | mês | Σ | n inteiro; % `_pcts` |
| Extrato | fluxo_mensal | `mes_entrada`, `evento`, `mes_evento`, `quantidade` | `YEAR(mes_entrada)` = ano de *p*, `mes_entrada` ≤ *p* | E7 | n inteiro; % conforme E7 |
| Data dos dados / aviso | as duas | `_processado_em` | — | MAX, em São Paulo | data |

## 5. Memória de cálculo (carga de 23/10/2026, dados até 22/10)

Números já com as correções B1–B3 (valores que mudaram de 1 ponto marcados com "antes:").

### 5.1 Número e comparação (E1, E8, E8b)

| | 2026 (01/01–22/10) | 2025 (01/01–22/10) |
|---|---|---|
| `quantidade` (data real) | 5.515 | 2.445 |
| `quantidade_estimada` (data estimada, R2) | 5 | **445** |
| **Pedidos (E1)** | **5.520** | **2.890** |

Variação = 5.520 ÷ 2.890 − 1 = 0,9100 → **+91%** → "▲ 91% a mais que em 2025".

### 5.2 Tabela por tipo (E9, E8c)

| Tipo | 2026 | % exato | **%** | 2025 | % exato | **%** | Var. |
|---|---|---|---|---|---|---|---|
| Mercado | 2.945 | 53,35 | 53% | 1.134 | 39,24 | 39% | 2.945 ÷ 1.134 − 1 = **+160%** |
| Inbound | 1.322 | 23,95 | 24% | 955 | 33,04 | 33% | **+38%** |
| Proativo | 407 | 7,37 | 7% | 468 | 16,19 | 16% | **−13%** |
| Internos | 769 | 13,93 | 14% | 330 | 11,42 | **12%** (antes: 11%) | **+133%** |
| Sem tipo | 77 | 1,39 | **2%** (antes: 1%) | 3 | 0,10 | 0% | – (base 3 < 30) |
| **Total** | **5.520** | | 100% | **2.890** | | 100% | **+91%** |

Maior resto, 2026: partes inteiras 53 + 23 + 7 + 13 + 1 = 97; faltam 3 → restos ,95 (Inbound), ,93 (Internos), ,39
(Sem tipo) recebem +1. 2025: 39 + 33 + 16 + 11 + 0 = 99; falta 1 → resto ,42 (Internos). Antes da B1 a coluna somava 99
nos dois anos.

Composição de Internos (E5): valores de `tipo_de_input` ViU, Interna, Globo, ViU First e OTR somam 769 (consulta 6.2-d).

Situação do ano (E6): entregues no mês 3.710 (67%), entregues depois 678 (12%), saíram sem entrega 972 (18%), em
andamento 160 (3%) = 5.520.

### 5.3 Os 12 meses (E1, E3, E6, E8)

Comparação: mês fechado contra o mês inteiro de 2025; outubro (parcial) contra 01–22/10/2025. Nov e dez: futuros, sem
pedidos e sem comparação. Extrato: mai–out (6 meses mais recentes com pedidos).

| Mês | 2026 | 2025 | Var. | Entregues no mês | Entregues depois | Saíram sem entrega | Em andamento |
|---|---|---|---|---|---|---|---|
| jan | 374 | 177 | +111% | 241 (**65%**; antes 64%) | 72 (19%) | 60 (16%) | 1 (0%) |
| fev | 341 | 197 | +73% | 220 (65%) | 42 (12%) | 79 (23%) | 0 (0%) |
| mar | 485 | 166 | +192% | 287 (59%) | 91 (19%) | 106 (22%) | 1 (0%) |
| abr | 472 | 329 | +43% | 292 (62%) | 95 (20%) | 85 (18%) | 0 (0%) |
| mai | 629 | 312 | +102% | 449 (71%) | 67 (11%) | 113 (18%) | 0 (0%) |
| jun | 569 | 268 | +112% | 411 (72%) | 53 (**10%**; antes 9%) | 104 (18%) | 1 (0%) |
| jul | 765 | 275 | +178% | 575 (75%) | 76 (10%) | 112 (15%) | 2 (0%) |
| ago | 644 | 474 | +36% | 489 (76%) | 51 (8%) | 101 (16%) | 3 (0%) |
| set | 733 | 395 | +86% | 460 (63%) | 131 (18%) | 138 (19%) | 4 (**0%**; antes 1%) |
| out* | 508 | 297 (até 22/10) | +71% | 286 (56%) | 0 (0%) | 74 (15%) | 148 (29%) |

\* parcial, "até 22/10" nos dois anos.

**Tipos por mês** — 2026 n (%) · 2025 n (%) · Var. ("–" = base < 30 no ano anterior):

| Mês | Mercado | Inbound | Proativo | Internos | Sem tipo |
|---|---|---|---|---|---|
| jan | 125 (33) · 67 (38) · +87% | 132 (35) · 77 (43) · +71% | 69 (19) · 12 (7) · – | 45 (12) · 21 (12) · – | 3 (1) · 0 (0) · – |
| fev | 187 (55) · 98 (50) · +91% | 88 (26) · 70 (35) · +26% | 30 (9) · 17 (9) · – | 28 (8) · 12 (6) · – | 8 (2) · 0 (0) · – |
| mar | 252 (52) · 62 (37) · +306% | 144 (30) · 59 (36) · +144% | 32 (7) · 41 (25) · −22% | 51 (10) · 4 (2) · – | 6 (1) · 0 (0) · – |
| abr | 228 (48) · 151 (46) · +51% | 99 (21) · 108 (33) · −8% | 70 (15) · 26 (8) · – | 61 (13) · 44 (13) · +39% | 14 (3) · 0 (0) · – |
| mai | 336 (53) · 81 (26) · +315% | 169 (27) · 137 (44) · +23% | 37 (6) · 52 (17) · −29% | 57 (9) · 42 (13) · +36% | 30 (5) · 0 (0) · – |
| jun | 339 (60) · 93 (35) · +265% | 112 (20) · 105 (39) · +7% | 25 (4) · 34 (13) · −26% | 92 (16) · 36 (13) · +156% | 1 (0) · 0 (0) · – |
| jul | 404 (53) · 63 (23) · +541% | 165 (22) · 124 (45) · +33% | 86 (11) · 22 (8) · – | 107 (14) · 64 (23) · +67% | 3 (0) · 2 (1) · – |
| ago | 322 (50) · 140 (30) · +130% | 156 (24) · 95 (20) · +64% | 6 (1) · 201 (42) · −97% | 160 (25) · 38 (8) · +321% | 0 (0) · 0 (0) · – |
| set | 477 (65) · 227 (57) · +110% | 129 (17) · 94 (24) · +37% | 29 (4) · 31 (8) · −6% | 93 (13) · 42 (11) · +121% | 5 (1) · 1 (0) · – |
| out* | 275 (54) · 152 (51) · +81% | 128 (25) · 86 (29) · +49% | 23 (5) · 32 (11) · −28% | 75 (15) · 27 (9) · – | 7 (1) · 0 (0) · – |

### 5.4 Extratos mai–out/2026 (E7, só pedidos de 2026)

| Mês | Represados no início | Novos | Demanda | Entregues = dos novos + dos represados | Saíram sem entrega | Seguem represados |
|---|---|---|---|---|---|---|
| mai | 134 (18%) | 629 (82%) | 763 | 504 (66%) = 449 (71% dos novos) + 55 (41% dos represados) | 111 (15%) | 148 (19%) |
| jun | 148 (21%) | 569 (79%) | 717 | 479 (67%) = 411 (72%) + 68 (46%) | 97 (**13%**; antes 14%) | 141 (**20%**; antes 19%) |
| jul | 141 (16%) | 765 (84%) | 906 | 672 (74%) = 575 (75%) + 97 (69%) | 116 (13%) | 118 (13%) |
| ago | 118 (15%) | 644 (85%) | 762 | 565 (74%) = 489 (76%) + 76 (64%) | 96 (13%) | 101 (13%) |
| set | 101 (12%) | 733 (88%) | 834 | 515 (62%) = 460 (63%) + 55 (54%) | 146 (**17%**; antes 18%) | 173 (**21%**; antes 20%) |
| out* | 173 (25%) | 508 (75%) | 681 | 419 (62%) = 286 (56%) + 133 (77%) | 102 (15%) | 160 (23%) |

Conferências: cada linha fecha (ex.: 681 = 419 + 102 + 160) e encadeia (seguem de mai 148 = represados de jun; 141 = jul;
118 = ago; 101 = set; 173 = out). Entregas de pedidos de anos anteriores entre mai e out: 0 (fora da fila de qualquer
forma). Jun pelo maior resto: 479/717 = 66,81; 97/717 = 13,53; 141/717 = 19,67 → partes inteiras 66 + 13 + 19 = 98 → +1
nos restos ,81 e ,67 → 67/13/20 (por diferença, "seguem" ficava 19).

**Tabelas por mês de entrada** (dica "Represados hoje/no fim do mês": início / entregues / saíram sem entrega / em
aberto; a dica "Represados do início" é a mesma tabela sem a linha do próprio mês):

| Extrato | Linhas (mês de entrada: início / entregues / saíram / em aberto) | Total |
|---|---|---|
| mai | mai (novos) 629/449/92/88 · abr 112/53/14/45 · mar 10/1/3/6 · fev 5/0/2/3 · jan 7/1/0/6 | 763/504/111/148 |
| jun | jun 569/411/76/82 · mai 88/66/21/1 · abr 45/2/0/43 · mar 6/0/0/6 · fev 3/0/0/3 · jan 6/0/0/6 | 717/479/97/141 |
| jul | jul 765/575/87/103 · jun 82/53/26/3 · mai 1/0/0/1 · abr 43/40/3/0 · mar 6/1/0/5 · fev 3/0/0/3 · jan 6/3/0/3 | 906/672/116/118 |
| ago | ago 644/489/72/83 · jul 103/76/24/3 · jun 3/0/0/3 · mai 1/0/0/1 · mar 5/0/0/5 · fev 3/0/0/3 · jan 3/0/0/3 | 762/565/96/101 |
| set | set 733/460/117/156 · ago 83/50/26/7 · jul 3/0/1/2 · jun 3/0/2/1 · mai 1/1/0/0 · mar 5/0/0/5 · fev 3/2/0/1 · jan 3/2/0/1 | 834/515/146/173 |
| out* | out (parcial) 508/286/74/148 · set 156/131/21/4 · ago 7/1/3/3 · jul 2/0/0/2 · jun 1/0/0/1 · mar 5/1/3/1 · fev 1/0/1/0 · jan 1/0/0/1 | 681/419/102/160 |

**Mês de entrada dos represados entregues:** mai: abr 53, mar 1, jan 1 · jun: mai 66, abr 2 · jul: jun 53, abr 40,
mar 1, jan 3 · ago: jul 76 · set: ago 50, mai 1, fev 2, jan 2 · out: set 131, ago 1, mar 1.

## 6. Como reproduzir (BigQuery, só leitura)

### 6.1 Passo a passo

1. **Fixar a carga.** Ler `MAX(_processado_em)` das duas tabelas gold em America/Sao_Paulo. Devem ser do mesmo dia
   (senão o site esconde o extrato). `fim` = esse dia − 1 (22/10/2026 na carga de referência); `fim_ant` = `fim` − 1 ano;
   ano = ano de `fim`.
2. **Número e comparação** (6.2-a): Σ `quantidade + quantidade_estimada` de 01/01/ano a `fim` e de 01/01/(ano−1) a
   `fim_ant`. Variação = atual ÷ anterior − 1 se anterior ≥ 30; arredondar meio para cima.
3. **Tipos** (6.2-b): mesmo recorte por `grupo_input` (fora da lista → "Sem tipo"); % pelo maior resto em cada ano.
4. **Meses** (6.2-c): por mês do ano: total, por tipo e as 4 colunas de situação; 2025 com mês cheio, exceto o mês de
   `fim`, cortado em `fim_ant`. % de situação e de tipo pelo maior resto.
5. **Extrato** (6.4-Q2): os 6 meses mais recentes com novos > 0 até `fim`; fila só com `mes_entrada` do mesmo ano.
6. **Conferir pela silver** (6.3): reconstruir os cards pelas regras da gold e agregar; deve dar os mesmos números
   (diferença 0 na carga de referência).
7. **Comparar com a tela** (seção 5 / página): cada número deve bater; registrar a data da carga.

### 6.2 Gold

```sql
-- (a) Número, comparação e estimadas (E1, E8). Troque as datas pelo fim da carga e o mesmo dia do ano anterior
SELECT ano, SUM(quantidade) AS reais, SUM(quantidade_estimada) AS estimadas,
       SUM(quantidade + quantidade_estimada) AS pedidos
FROM `gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_entrada_diaria`
WHERE (ano = 2026 AND data <= '2026-10-22') OR (ano = 2025 AND data <= '2025-10-22')
GROUP BY ano ORDER BY ano;

-- (b) Tabela por tipo (E9)
SELECT IF(grupo_input IN ('Mercado','Inbound','Proativo','Internos'), grupo_input, 'Sem tipo') AS grupo, ano,
       SUM(quantidade + quantidade_estimada) AS pedidos
FROM `gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_entrada_diaria`
WHERE (ano = 2026 AND data <= '2026-10-22') OR (ano = 2025 AND data <= '2025-10-22')
GROUP BY 1, 2 ORDER BY 1, 2;

-- (c) Mês × tipo × situação, com o mês parcial de 2025 cortado no mesmo dia
SELECT ano, mes, IF(grupo_input IN ('Mercado','Inbound','Proativo','Internos'), grupo_input, 'Sem tipo') AS grupo,
  SUM(quantidade + quantidade_estimada) AS pedidos_mes_cheio,
  SUM(IF(data <= IF(ano = 2026, DATE '2026-10-22', DATE '2025-10-22'), quantidade + quantidade_estimada, 0)) AS pedidos_ate_fim,
  SUM(entregue_no_mes) AS no_mes, SUM(entregue_depois) AS depois, SUM(nao_seguiu) AS nao_seguiu, SUM(em_andamento) AS andamento
FROM `gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_entrada_diaria`
WHERE ano IN (2025, 2026)
GROUP BY 1, 2, 3 ORDER BY 1, 2, 3;
-- meses fechados de 2025: pedidos_mes_cheio; o mês do fim (out): pedidos_ate_fim

-- (d) Composição de Internos (E5)
SELECT tipo_de_input, SUM(quantidade + quantidade_estimada) AS pedidos
FROM `gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_entrada_diaria`
WHERE ano = 2026 AND grupo_input = 'Internos' GROUP BY 1 ORDER BY 2 DESC;

-- (e) Extrato de um mês (E7) e tabela por mês de entrada; troque o mês em m
WITH m AS (SELECT DATE '2026-10-01' AS mes),
f AS (SELECT f.* FROM `gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_fluxo_mensal` f, m
      WHERE EXTRACT(YEAR FROM f.mes_entrada) = EXTRACT(YEAR FROM m.mes) AND f.mes_entrada <= m.mes)
SELECT f.mes_entrada,
  SUM(IF(f.mes_entrada = m.mes OR f.evento = 'em_andamento' OR f.mes_evento >= m.mes, f.quantidade, 0)) AS inicio,
  SUM(IF(f.evento = 'entregue' AND f.mes_evento = m.mes, f.quantidade, 0)) AS entregues,
  SUM(IF(f.evento = 'nao_seguiu' AND (f.mes_evento = m.mes OR (f.mes_evento IS NULL AND f.mes_entrada = m.mes)), f.quantidade, 0)) AS sairam_sem_entrega,
  SUM(IF(f.evento = 'em_andamento' OR f.mes_evento > m.mes, f.quantidade, 0)) AS em_aberto
FROM f, m GROUP BY 1 ORDER BY 1 DESC;
-- represados do início = Σ inicio das linhas com mes_entrada < m; novos = inicio da linha m; a soma das linhas = caixa
```

### 6.3 Silver (reprodução independente das regras da gold)

Base: `silver_monday.slv_agenciamento_2024_itens`, `..._2025_itens`, `..._2026_itens` (`state = 'active'`) e
`..._2026_log` (1ª ida a Aguardando Feedback e dia do status final). Regras: entrada = `criado_em` (2026: R21, usa
`data_de_entrada` quando a saída é anterior à criação); sem `criado_em` e com saída → estimada = 5º dia útil antes da
saída, com feriados (R2); saída 2026 = 1ª Aguardando Feedback pelo log, senão `data_de_saida` (R13); 2024/2025 =
`data_de_saida`; situação com corte em `fim`. Validadores: S1 (`s1/cards.sql`), S2, S3, G (`valG/silver_cards.sql`).

```sql
WITH p AS (SELECT DATE '2026-10-22' AS fim),
pascoa AS (SELECT d FROM UNNEST([DATE '2024-03-31', DATE '2025-04-20', DATE '2026-04-05']) d),
fer AS (
  SELECT ARRAY_CONCAT(
    ARRAY(SELECT DATE(y, md.m, md.d) FROM UNNEST([2024,2025,2026]) y,
          UNNEST([STRUCT(1 AS m,1 AS d),(1,20),(1,25),(4,21),(4,23),(5,1),(7,9),(9,7),(10,12),(11,2),(11,15),(11,20),(12,24),(12,25),(12,31)]) md),
    ARRAY(SELECT DATE_ADD(d, INTERVAL k DAY) FROM pascoa, UNNEST([-48,-47,-46,-2,60]) k)) AS dias),
af AS (SELECT projeto_id, MIN(DATE(alterado_em)) dia FROM `gglobo-viu-dados-hdg-prd.silver_monday.slv_agenciamento_2026_log`
       WHERE campo_alterado='Status' AND valor_depois='Aguardando Feedback' GROUP BY 1),
ue AS (SELECT projeto_id, valor_depois status, MAX(DATE(alterado_em)) dia FROM `gglobo-viu-dados-hdg-prd.silver_monday.slv_agenciamento_2026_log`
       WHERE campo_alterado='Status' GROUP BY 1,2),
base AS (
  SELECT '2024' board, item_id id, criado_em ent, data_de_saida ds, CAST(NULL AS DATE) afd, tipo_de_input ti, status, CAST(NULL AS DATE) sd
  FROM `gglobo-viu-dados-hdg-prd.silver_monday.slv_agenciamento_2024_itens`
  UNION ALL SELECT '2025', item_id, criado_em, data_de_saida, NULL, tipo_de_input, status, NULL
  FROM `gglobo-viu-dados-hdg-prd.silver_monday.slv_agenciamento_2025_itens`
  UNION ALL SELECT '2026', i.projeto_id,
    CASE WHEN i.data_de_saida < DATE(i.criado_em) AND i.data_de_entrada <= i.data_de_saida THEN i.data_de_entrada ELSE DATE(i.criado_em) END,
    i.data_de_saida, af.dia, i.tipo_de_input, i.status, ue.dia
  FROM `gglobo-viu-dados-hdg-prd.silver_monday.slv_agenciamento_2026_itens` i
  LEFT JOIN af USING (projeto_id) LEFT JOIN ue ON ue.projeto_id=i.projeto_id AND ue.status=i.status
  WHERE i.state='active'),
c1 AS (
  SELECT b.*,
    IFNULL(b.ent, (SELECT ARRAY_AGG(d ORDER BY d DESC LIMIT 5)[SAFE_OFFSET(4)]
                   FROM UNNEST(GENERATE_DATE_ARRAY(DATE_SUB(b.ds, INTERVAL 21 DAY), DATE_SUB(b.ds, INTERVAL 1 DAY))) d
                   WHERE EXTRACT(DAYOFWEEK FROM d) BETWEEN 2 AND 6 AND d NOT IN UNNEST(fer.dias))) dia,
    b.ent IS NULL AND b.ds IS NOT NULL estimada,
    CASE WHEN b.afd IS NOT NULL AND (b.ent IS NULL OR b.afd >= b.ent) THEN b.afd
         WHEN b.ds IS NOT NULL AND (b.ent IS NULL OR b.ds >= b.ent) THEN b.ds END saida
  FROM base b, fer),
cards AS (
  SELECT id, board, dia, estimada, saida, sd,
    CASE WHEN saida <= p.fim THEN IF(DATE_TRUNC(saida,MONTH) <= DATE_TRUNC(dia,MONTH),'no_mes','depois')
         WHEN STARTS_WITH(status,'Declinado') OR status IN ('Standby','Encerrado') THEN 'nao_seguiu'
         ELSE 'em_andamento' END sit,
    CASE WHEN ti IN ('Mercado','Inbound','Proativo') THEN ti
         WHEN ti IN ('ViU','Interna','Globo','ViU First','OTR (Oportunidade em Tempo Real)') THEN 'Internos'
         ELSE 'Sem tipo' END grupo
  FROM c1, p
  WHERE dia BETWEEN DATE '2024-10-01' AND p.fim)
-- meses de 2026 (total, tipos, estimadas, situação); para 2025 troque o ano e corte o mês do fim em fim − 1 ano
SELECT EXTRACT(MONTH FROM dia) mes, COUNT(*) n, COUNTIF(grupo='Mercado') mer, COUNTIF(grupo='Inbound') inb,
  COUNTIF(grupo='Proativo') pro, COUNTIF(grupo='Internos') int_, COUNTIF(grupo='Sem tipo') sem, COUNTIF(estimada) est,
  COUNTIF(sit='no_mes') no_mes, COUNTIF(sit='depois') depois, COUNTIF(sit='nao_seguiu') ns, COUNTIF(sit='em_andamento') anda
FROM cards WHERE EXTRACT(YEAR FROM dia)=2026 GROUP BY 1 ORDER BY 1;
-- fila (E7) pela silver: evento = entregue (mês da saída) / nao_seguiu (mês do status final pelo log, `sd`;
-- nulo se não há mudança de status) / em_andamento; agregue por mes_entrada × evento × mes_evento e aplique E7
```

Atenção: os 5 cards de 2026 com `criado_em` nulo (estimados R2: 12965451258, 12965451261, 12965366908, 12965367218,
12965424763) precisam entrar também na fila; a 1ª rodada de um validador os perdeu e gerou 5 diferenças falsas.

### 6.4 Checagem diária (rodar a cada carga)

As duas consultas foram executadas com `fim` = 2026-10-22 e devolveram o gabarito. **Uso diário:** trocar
`CAST('2026-10-22' AS DATE)` por `CAST(NULL AS DATE)`; o `fim` passa a ser a véspera do `_processado_em`. Sem
`DECLARE` (o MCP do BigQuery pode não aceitar script).

**Q1 — sanidade da carga.** Resultado em 22/10: todos os `ok_*` = true; 0 tipos fora da lista; 0 linhas sem fechar;
0 safras divergentes; 5.520 = 5.520; 2.890 (445 estimadas); 0 eventos antes da entrada; 10 "não seguiu" sem data
(achado G1); 508 no mês corrente.

```sql
WITH
ent AS (SELECT * FROM `gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_entrada_diaria`),
flu AS (SELECT * FROM `gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_fluxo_mensal`),
p AS (
  SELECT
    (SELECT DATE(MAX(_processado_em), 'America/Sao_Paulo') FROM ent) AS d_entrada,
    (SELECT DATE(MAX(_processado_em), 'America/Sao_Paulo') FROM flu) AS d_fluxo,
    COALESCE(CAST('2026-10-22' AS DATE),  -- override; NULL = véspera da carga
             (SELECT DATE_SUB(DATE(MAX(_processado_em), 'America/Sao_Paulo'), INTERVAL 1 DAY) FROM ent)) AS fim),
q AS (SELECT *, EXTRACT(YEAR FROM fim) AS a, DATE_SUB(fim, INTERVAL 1 YEAR) AS fim_ant FROM p),
ent_mes AS (
  SELECT DATE_TRUNC(e.data, MONTH) AS m, SUM(e.quantidade + e.quantidade_estimada) AS n
  FROM ent e, q WHERE EXTRACT(YEAR FROM e.data) = q.a GROUP BY 1),
flu_mes AS (
  SELECT f.mes_entrada AS m, SUM(f.quantidade) AS n
  FROM flu f, q WHERE EXTRACT(YEAR FROM f.mes_entrada) = q.a GROUP BY 1)
SELECT
  q.fim, q.d_entrada, q.d_fluxo,
  q.d_entrada = q.d_fluxo AS ok_mesma_carga,
  DATE_SUB(q.d_entrada, INTERVAL 1 DAY) = q.fim AS ok_fim_e_vespera,
  (SELECT MAX(data) FROM ent) AS max_data,
  (SELECT MAX(data) FROM ent) <= q.fim AS ok_sem_data_futura,
  (SELECT COUNTIF(grupo_input IS NULL OR grupo_input NOT IN ('Mercado','Inbound','Proativo','Internos','Sem tipo')) FROM ent) AS linhas_tipo_fora_lista,
  (SELECT COUNTIF(IFNULL(quantidade,0) + IFNULL(quantidade_estimada,0) <> IFNULL(entregue_no_mes,0) + IFNULL(entregue_depois,0)
                  + IFNULL(nao_seguiu,0) + IFNULL(em_andamento,0)) FROM ent) AS linhas_situacao_nao_fecha,
  (SELECT COUNT(*) FROM ent_mes FULL JOIN flu_mes USING (m) WHERE IFNULL(ent_mes.n,-1) <> IFNULL(flu_mes.n,-1)) AS meses_safra_divergente,
  (SELECT SUM(n) FROM ent_mes) AS entrada_ano, (SELECT SUM(n) FROM flu_mes) AS fluxo_ano,
  (SELECT SUM(quantidade + quantidade_estimada) FROM ent e WHERE e.data BETWEEN DATE(q.a,1,1) AND q.fim) AS total_ano,
  (SELECT SUM(quantidade + quantidade_estimada) FROM ent e WHERE e.data BETWEEN DATE(q.a-1,1,1) AND q.fim_ant) AS total_mesmo_periodo_ant,
  (SELECT SUM(quantidade_estimada) FROM ent e WHERE e.data BETWEEN DATE(q.a-1,1,1) AND q.fim_ant) AS estimadas_ant,
  (SELECT COUNTIF(evento <> 'em_andamento' AND mes_evento < mes_entrada) FROM flu) AS eventos_antes_da_entrada,
  (SELECT IFNULL(SUM(quantidade),0) FROM flu f WHERE evento = 'nao_seguiu' AND mes_evento IS NULL
          AND EXTRACT(YEAR FROM f.mes_entrada) = q.a) AS nao_seguiu_sem_data_ano,
  (SELECT IFNULL(SUM(e.quantidade + e.quantidade_estimada),0) FROM ent e
          WHERE e.data BETWEEN DATE_TRUNC(q.fim, MONTH) AND q.fim) AS novos_mes_corrente
FROM q;
```

**Q2 — fila dos 6 meses do extrato** (E7, janela pelos meses com pedidos, como no site depois da B5). Resultado em
22/10 (reexecutado com a janela nova): mai 134/629/763/449/55/111/148, jun 148/569/717/411/68/97/141, jul
141/765/906/575/97/116/118, ago 118/644/762/489/76/96/101, set 101/733/834/460/55/146/173, out 173/508/681/286/133/102/160;
`ok_fecha` = true em todos e `ok_encadeia` = true de jun a out. Em janeiro, `ok_encadeia` dá false por desenho (fila do
ano começa com 0 represados).

```sql
WITH
p AS (SELECT COALESCE(CAST('2026-10-22' AS DATE),
        (SELECT DATE_SUB(DATE(MAX(_processado_em), 'America/Sao_Paulo'), INTERVAL 1 DAY)
         FROM `gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_entrada_diaria`)) AS fim),
f AS (SELECT * FROM `gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_fluxo_mensal`),
meses AS (SELECT m FROM (SELECT DISTINCT f.mes_entrada AS m FROM f, p WHERE f.quantidade > 0 AND f.mes_entrada <= p.fim)
          ORDER BY m DESC LIMIT 6),
x AS (
  SELECT m,
    SUM(IF(mes_entrada < m AND (evento='em_andamento' OR mes_evento >= m), quantidade, 0)) represados,
    SUM(IF(mes_entrada = m, quantidade, 0)) novos,
    SUM(IF(evento='entregue' AND mes_evento=m AND mes_entrada=m, quantidade, 0)) entregues_novos,
    SUM(IF(evento='entregue' AND mes_evento=m AND mes_entrada<m, quantidade, 0)) entregues_represados,
    SUM(IF(evento='nao_seguiu' AND (mes_evento=m OR (mes_evento IS NULL AND mes_entrada=m)), quantidade, 0)) nao_seguiram,
    SUM(IF(evento='em_andamento' OR mes_evento>m, quantidade, 0)) seguem
  FROM meses JOIN f ON EXTRACT(YEAR FROM f.mes_entrada) = EXTRACT(YEAR FROM m) AND f.mes_entrada <= m
  GROUP BY m)
SELECT m, represados, novos, represados+novos AS demanda, entregues_novos, entregues_represados, nao_seguiram, seguem,
  represados+novos = entregues_novos+entregues_represados+nao_seguiram+seguem AS ok_fecha,
  represados = LAG(seguem) OVER (ORDER BY m) AS ok_encadeia
FROM x ORDER BY m;
```

**Alarmes (disparam revisão antes de apresentar):** qualquer `ok_*` = false; `linhas_tipo_fora_lista` > 0 (tipo novo no
Monday cairia em "Sem tipo"); `linhas_situacao_nao_fecha` > 0; `meses_safra_divergente` > 0; `eventos_antes_da_entrada`
> 0; `nao_seguiu_sem_data_ano` maior que no dia anterior (novo lote retroativo, G1/G6); `total_ano` menor que no dia
anterior (card arquivado ou apagado, G6); na Q2, `ok_fecha` false ou `ok_encadeia` false fora de janeiro.

## 7. Validações feitas

| Data | O quê | Quem | Resultado |
|---|---|---|---|
| 23/10/2026 | Número, comparação, tabela por tipo e meses × consultas da seção 6.2 | Claude | ✅ batem com a tela |
| 23/10/2026 | Três camadas gold × silver × bronze (rodada anterior): 91 combinações ano × mês × grupo; bronze 2025 = silver (3.727 itens); extrato de set e out item a item; log da bronze contido na silver | 2 agentes | ✅ achados F6–F11 no PRD |
| 23/10/2026 | **Validação final de entrega (três camadas, troca de base):** gabarito extraído do próprio código com a carga real (`tela_inicio.json`) × gold × silver, 624 itens (topo 3, tipos 25, 12 meses 64, situações 96, tipos por mês 240, extratos 196) | **G** (gold → silver; recálculo próprio sem importar o código, `Decimal` meio para cima e maior resto reescrito); **S1** (silver → gold; feriados e R2/R21 próprios, `verifica.py`, `fila.py`); **S2** (silver → gold; foco nos extratos e na fila item a item); **S3** (silver → gold; 440 itens e simulação de virada de mês/ano, `virada.py`); árbitro releu código e SQL da gold e rodou a checagem diária | **0 divergências de número** nos 4 relatórios. Silvers processadas antes da gold (mesma foto). Diferenças do caminho foram erro de validador (5 cards estimados fora da consulta do G) |
| 23/10/2026 | Achados de apresentação dos validadores aplicados: B1 (tipos no ano somavam 99), B2 (situação somava 99/101 em jan, jun, set), B3 (extrato por diferença), B5 (mês vazio ocupava vaga), B6 (lista de meses válidos só do ano), B7 (cargas de dias diferentes sem aviso), B8 (período na virada) | Claude (revisor final) | ✅ 83 testes; números regenerados com a carga real (seção 5): só % mudaram, nenhuma quantidade |
| 23/10/2026 | Tela 1440×900 e 390 px | processo de navegador separado | cabe, sem rolagem lateral (reconferir depois das correções: ver PRD D28) |

## 8. Limites e pontos de atenção

### 8.1 ⚠️ 2025 tem 15% de entradas com data estimada (decisão pendente, Q11)

No board de 2025, 725 cards não têm data de criação. A gold estima a entrada de 576 deles (os que têm data de saída)
como **saída − 5 dias úteis** (regra R2 da gold). Até 22/10/2025 são **445 de 2.890 (15%)**; em out/25, 111 de 459;
em 2026, só 5. Os 149 cards sem criação **e** sem saída não entram em nenhuma conta.

| Leitura | 2025 | Variação 2026 × 2025 |
|---|---|---|
| Como está (reais + estimadas) | 2.890 | **+91%** |
| Só datas reais | 2.445 | **+126%** |

Por tipo, sem as estimadas: Mercado +214%, Internos +202%, Inbound +58%, Proativo −1%. A tendência se mantém; o tamanho
do número muda. Decisão do Caio (D29, 23/10/2026): manter as estimadas e **não colocar aviso na tela**; o limite fica só nesta documentação (e em Q11).

**Sensibilidade da variação principal (INI-D4, reconferida no BigQuery em 25/10/2026, carga de 23/10/2026 20:23:49 UTC):**
2025 até 22/10 = **2.890**, das quais **445** estimadas → +91% (5.520 ÷ 2.890 − 1 = 0,910); sem as estimadas, **2.445** →
**+126%** (5.520 ÷ 2.445 − 1 = 1,258). O ano inteiro de 2025 tem 3.586 (out/25 inteiro = 459). A tela não muda (D29-3).

```sql
SELECT
  SUM(IF(data BETWEEN '2025-01-01' AND '2025-10-22', quantidade + quantidade_estimada, 0)) AS total_2025_mesmo_periodo, -- 2.890
  SUM(IF(data BETWEEN '2025-01-01' AND '2025-10-22', quantidade_estimada, 0)) AS estimadas_2025,                      -- 445
  SUM(IF(data BETWEEN '2026-01-01' AND '2026-10-22', quantidade + quantidade_estimada, 0)) AS total_2026,              -- 5.520
  MAX(_processado_em) AS carga                                                                                         -- 2026-10-23 20:23:49 UTC
FROM `gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_entrada_diaria`;
```

### 8.2 Dados da gold que mudam números (detalhe em `docs/lembretes_gold.md`)

- **Outubro inflado por 10 cards sem `data_de_saida` (G1/F8):** novos de out **508 → 498** e saíram sem entrega
  **102 → 92** (74 → 64 na linha dos novos) se a gold usar `data_de_entrada`; jan–jul ganhariam esses 10. São os mesmos
  **10 "saíram sem entrega" sem data** (`nao_seguiu` sem `mes_evento`, todos de outubro; reconferido em 25/10/2026:
  `sem_data` = 10 em 2026-10), contados no mês de entrada pela convenção E7.
- **43 cards de setembro contados em outubro (G4, a confirmar):** criados em 05–15/10 com `data_de_entrada` em 22–29/09.
- **Status de "não seguiu" sem corte em `fim` (G2):** no dia 1º, um card declinado no dia da carga pode aparecer como
  "saiu sem entrega" na situação e em "seguem" no extrato.
- **Meses passados mudam a cada carga (G6):** a gold recalcula tudo com o estado de hoje. O extrato de maio visto hoje
  pode diferir do visto em junho. A página é uma **foto do dia**.
- **Lista fixa de boards (G3):** sem a silver de 2027 na gold, a página para em 2026 em janeiro sem erro.

### 8.3 Outros limites

- Extrato: "não seguiu" sem data de mudança no log conta no mês de entrada; represados e saídas são foto do dia.
- **Regra (D29):** a fila só conta pedidos do ano; **janeiro começa com 0 represados**, porque a página mostra sempre o ano
  vigente. Pedidos do ano anterior em aberto (≈ 160 hoje) não aparecem.
- **Regra (D29):** em janeiro, os extratos dos meses do ano anterior **não são mostrados**; ficam só calculados
  (`meses_extrato`, invisível na tela).
- Mês parcial comparado até o mesmo dia corrido do ano anterior (out 1–22: 15 dias úteis em 2026 × 16 em 2025, ≈ 6%).
  Nota de dias úteis na tela: **em discussão com o Caio** (PRD P4), nada aplicado.
- 29/02: em 2029 a régua de 2028 para em 28/02 (desprezível).
- Régua do ano anterior exige um pedido até 07/01 (B9, baixa prioridade): um recesso longo apagaria a comparação.
- Sem `_processado_em` (só no computador), o último dia é o maior dia com pedido.
- **Divergência entre entrada e fluxo (decisão 5, 25/10/2026):** só uma safra do ano exibido esconde o extrato (e o
  Atendimento); safra de ano anterior divergente fica só no log do servidor (`Entrada e fluxo divergem em safras de anos
  anteriores`), sem efeito na tela.
- **Rodapé (INI-D1):** "Dados até" e "atualizados em" vêm do `_processado_em` da carga (17:23); o cartão de status do
  menu lateral ("Dados de 23/10, 17:24") segue o `modified` da tabela, que também é o gatilho da recarga. Diferença de
  minutos esperada; um ALTER só de descrições muda o menu, não o rodapé.
- Mês parcial no gráfico: `ate_curto` ("22/out") e o leitor de tela dizem "mesmo período"; com o ano fechado, nada
  disso aparece e o selo compara os anos inteiros.
- "Sem tipo" cresceu de 3 para 77 (Q10). Data de entrada em 2026: criação com correção do retroativo (Q7).

## 9. Decisões

D23 (página inicial da área), D25 (só por tipo de input), D26 (sempre o ano corrente), D27 (proporção ao lado da
quantidade), **D28 (página entregue em 23/10/2026)**, **D29 (decisões do Caio: janeiro com 0 represados; sem extratos do
ano anterior; sem aviso de estimadas na tela; contraste dos totais; "Sem tipo" 2%)**; Q7, Q10 e Q11 em aberto; nota de
dias úteis em discussão (PRD P4). **D52 (26/10/2026): disposição em dois quadrantes (nuvem de palavras + caixa cinza de
altura fixa) e cartão alinhado pelo pé.** Ver PRD, seções 8 e 9.

## 10. Histórico da página

| Data | Mudança |
|---|---|
| 22/10/2026 | Página criada (entrada por mês e tipo) |
| 23/10/2026 | Sem seletor de ano; comparação com 2025; extrato dos 6 meses; tabela de tipos com 2025 e variação |
| 23/10/2026 | Título "Quantos pedidos de orçamento chegaram em 2026?"; comparação compacta ao lado do número (seta verde/vermelha); regras E8b e E4; base mínima 30 para toda variação |
| 23/10/2026 | Bloco de resposta compactado a pedido do Caio: o cartão empurrava a tabela para baixo e mudava a coluna ao abrir o extrato. Agora fica na altura do número (número + período | selo + barras finas), sem moldura; tabela de volta à posição aprovada; nada se move ao abrir o extrato |
| 23/10/2026 | Bloco de resposta redesenhado (comparação entre 3 propostas de agentes; venceu a "comparação visual", maquetes em `docs/propostas_resposta/`): cartão com número, selo da variação e barras 2026 × 2025 em SVG; barras recolhem com o extrato aberto (o gráfico não se mexe). Dica "Novos pedidos por tipo de input" no extrato. Saída do extrato como espelho da entrada; legenda do gráfico com espaço reservado |
| 23/10/2026 | Título: "…chegaram ao longo de 2026 até o momento?" (ano fechado: "…em AAAA?") |
| 23/10/2026 | "Saíram sem entrega" substitui "Encerrados" (mais direto: declinado, standby ou encerrado antes da entrega). Bug corrigido: a dica do mês ficava presa aberta depois de um clique (foco do mouse) e as dicas da caixa seguravam o mouse; agora só abrem sobre o nome ou com foco de teclado |
| 23/10/2026 | Nomes: "Não seguiram" vira **Encerrados sem entrega** (caixa e dica do mês) / **Encerrados** (coluna); colunas da dica: Represados, Entregues, Saíram sem entrega, Em aberto; linha do mês em andamento marcada "(parcial)" |
| 23/10/2026 | Dicas dos represados: só o mês (sem ano), sem texto; colunas Início, Entregues, Não seguiram, Seguem e Total (a coluna "Resolvidos" misturava entregues e não seguiram e confundia com as entregas) |
| 23/10/2026 | Extrato vira a **fila do mês** (represados + novos = demanda; entregues, não seguiram, seguem represados), só pedidos de 2026, com dicas por mês de entrada (início, resolvidos, seguem); substitui as colunas % entregas / % entradas |
| 23/10/2026 | Extrato com % entregas e % entradas por origem e "= X% das entradas" no total; dica só no nome do mês; troca da caixa sem recarregar com "foco no mês" (outros meses esmaecem); rodapé com o recorte datado; "parcial" como texto miúdo; rótulos do gráfico mais leves (referência: deck do pipeline) |
| 23/10/2026 | Teste de faixa de resposta na largura toda desfeito a pedido do Caio: cortava os meses do gráfico em telas de 720–768 px de altura e esticava a tabela. Volta: número + tabela compacta flutuando à esquerda, gráfico com a altura inteira à direita |
| 23/10/2026 | Dica "Novos pedidos por tipo de input" redesenhada (4 propostas de agentes; venceu a D, "composição 100%", maquetes em `app/static/propostas-dica/`): barras 100% dos dois anos em SVG + grade alinhada com selo pintado e Var. como na tabela de tipos. Correções dos verificadores: parcelas fecham em 100% (E8c) e `_pct` meio para cima; grade `aria-hidden` + frase por linha para leitor de tela (também na tabela dos represados); toque no celular abre a dica; alvo do quadradinho ≥ 24 px; "–" em cinza. 75 testes |
| 23/10/2026 | Dicas revisadas (6 avaliadores: espaço, tipografia, conteúdo, acessibilidade, dataviz, consistência; prevaleceu a orientação do Caio). Novos pedidos: sem as barras 100% e sem análise, só a tabela no desenho da tabela principal (cabeçalho em dois níveis, números centralizados, total sem serifa, mais distância da linha). Nome do tipo: dica só em Internos e sem a frase de comparação com 2025. Todas as dicas com escala única (13/14/12 px, nada abaixo de 12 px) e só pesos 400/500; corrigido o `font:` que zerava os algarismos alinhados (total da dica do mês). Represados: "Em aberto" destacado só pelo fundo, mais respiro e ajuste para 390 px. 75 testes |
| 23/10/2026 | Título "Novos pedidos por tipo" centralizado a pedido do Caio, em Playfair 16/500 (lining-nums) com fio curto azul embaixo, criando degrau sobre o cabeçalho "mês/26" (debate entre 2 propostas; venceu a serifa; tabela segue em sans) |
| 23/10/2026 | **Entrega (D28).** Validação final em três camadas (4 validadores, 624 itens, 0 divergências). Correções: B1 tipos no ano e no ano anterior pelo maior resto (Sem tipo 1% → 2%; Internos 2025 11% → 12%); B2 situação do mês pelo maior resto (jan 64 → 65; jun depois 9 → 10; set andamento 1 → 0); B3 extrato sem % por diferença (jun 14/19 → 13/20; set 18/20 → 17/21); B5 janela pelos 6 meses mais recentes com pedidos; B6 lista de meses válidos na base inteira (`meses_extrato`; tela inalterada); B7 aviso quando entrada e fluxo são de dias de carga diferentes; B8 carga de 01/01 mostra "de janeiro a dezembro". Ficha completada para auditoria: origem de cada número, memória de 12 meses e 6 extratos, passo a passo gold e silver, checagem diária (Q1, Q2) com alarmes. 83 testes |
| 23/10/2026 | **D29 — decisões do Caio:** janeiro começa com 0 represados (regra); extratos do ano anterior não aparecem em janeiro (só o cálculo `meses_extrato`); aviso das 15% estimadas de 2025 fica só na documentação; "Sem tipo" 2% aprovado; contraste aprovado: com o extrato aberto, só a coluna dos outros meses esmaece e o total fica legível (`estilo.css`). Nota de dias úteis no mês parcial em discussão (não aplicada) |
| 25/10/2026 | **Revisão de 25/10 (auditoria + decisões 1–5 delegadas pelo Caio):** gráfico em **cartão flutuante** com título visível, mesmo padrão, altura e posição do cartão do SLA (tokens `--cartao-*`; INI-CARTAO, decisão 1); `mesmo período: até 22/out` sob as barras (decisão 2); Var. com seta pastel ▲/▼ verde/vermelha e número neutro, revisando a D26 (decisão 3); `<1%` quando a parcela arredonda a 0 com pedidos (decisão 4; Sem tipo 2025); divergência em safra antiga só no log (decisão 5); leitor do mês parcial com "no mesmo período (até 22/10)" (INI-D2); mês futuro em itálico `--tinta-3` e motivo do "–" para o leitor (IN-A1); rodapé pelo `_processado_em` (INI-D1: 17:24 → 17:23); sensibilidade +91%/+126% documentada com SQL (INI-D4); removida linha morta de `mes_parcial` (INI-D7). Números conferidos no BigQuery (5.520 / 2.890 / 445 / +91%). Moldura medida antes e depois em 1440×900, 1800×980 e 1280×720: idêntica. 135 testes |
| 26/10/2026 | **D52 — Início em dois quadrantes** (Caio, 26/10/2026): coluna da esquerda dividida em dois quadrantes. Em cima, a resposta composta como **nuvem de palavras** no padrão da frase do SLA: "Chegaram" (Plex leve) · **5.556** (Playfair grande, azul) · *pedidos de orçamento* (itálico serifado, duas linhas) · "em 2026, até 25 de outubro" (Plex leve, à direita do bloco), e como apoio (traço azul do `.f-apoio`) o selo "▲ 89% a mais que em 2025" com as barras 2026 5.556 × 2025 2.943 e "mesmo período: até 25/out" — tudo dos dados (`e.total`, `e.ano`, `e.periodo`, `e.comparacao`, `e.ate_curto`; macro `resposta` em `app/templates/macros.html`). Embaixo, a caixa cinza chapada com **altura fixa** (`max(14.2em, 219px)` = a tabela do ano): tabela de tipos ou extrato do mês, trocados no mesmo lugar com a animação de troca de sempre; o extrato ficou compacto (rótulo "Análise mensal" na linha do título, totais e barras menores, linhas justas, mesmo fundo cinza) e cabe na caixa sem mover a nuvem. O cartão do gráfico tem a altura do cartão do SLA (`min(100%, 34.25em)` com letra 0,8em; 549 × 554 px em 1850×1030), não estica, e o **pé fica alinhado ao pé da caixa cinza** (e ao pé do cartão do SLA); o topo cai no quadrante de cima (meio em cima, meio embaixo). Sombra mais funda ("flutuante"); legenda dos tipos só no topo do cartão (a legenda de baixo, reservada para o extrato, saiu e a de cima deixou de ser `aria-hidden`). Movimento segue D46/D49: nuvem pronta desde o 1º quadro, só o apoio entra num fade e as barras e colunas crescem. Nenhum número ou regra mudou. Testes: `tests/test_inicio_d52.py` (frase dinâmica, apoio, ordem dos quadrantes, extrato no mesmo lugar, CSS da altura fixa e do cartão) e `tests/test_rotas.py` (texto do período). Capturas conferidas em 1920×1000, 1850×1030, 1440×900, 1280×800 (ano, set/26 e out/26 parcial: caixa e extrato com a mesma altura, sem transbordar, nuvem parada) e 390 px (empilhado, sem rolagem lateral). 420 testes |
| 26/10/2026 | **Batalha 2 (D49):** sem contagem a partir de zero; só as colunas crescem (1,11 s); rodapé e menu no horário do processamento. **Documentação:** retrato da carga da reunião (5.556 até 25/10, +89%; Q1/Q2 em ordem) no topo; regras inalteradas |
| 27/10/2026 | **D57:** o extrato do mês passa a ler a view gold `gld_agenciamento_fila_mensal` (antes calculado no site sobre o fluxo); números e textos iguais (código antigo × novo na mesma carga) |
| 28/10/2026 | **Ano anterior no gráfico mensal** (Caio, 28/10/2026): cada mês com dado de 2025 ganha, à esquerda da coluna de 2026, a coluna do mesmo mês de 2025 (cinza tracejado, número menor em cinza; no mês parcial, até o mesmo dia), na mesma escala (o máximo passa a considerar os dois anos); sob o nome do mês, "25 26" embaixo de cada coluna; na legenda, "2025, mesmo mês". Os números são os mesmos da dica do mês (`m.anterior.total`, regra E8; nenhuma regra nova). Carga de 28/10: jan 177 · fev 197 · mar 166 · abr 329 · mai 312 · jun 268 · jul 275 · ago 474 · set 395 · out 394 (até 27/10); todos os meses de 2026 acima (+36% a +192%). Com o extrato aberto, o mês escolhido mantém as duas colunas e os demais esmaecem. No celular (barras deitadas) o ano anterior fica só na dica. Teste: `test_grafico_do_inicio_com_o_ano_anterior_ao_lado`; capturas em 1440×900 (ano e out/26) e 760 px |
