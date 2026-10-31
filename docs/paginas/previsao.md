# Ficha: Previsão de demanda (`/viu-agenciamento/previsao`)

## Retrato da carga da reunião (26/10/2026)

> **Estado (26/10/2026, D56 — vigente; revisa a D48 e a D55 na escolha das séries e na tela):** **uma série e um modelo
> por recorte**, cada um treinado só na sua própria série, sem repartição por proporção: **Inbound** (todo o Inbound,
> gold), **Mercado** (total, gold), **Mercado exclusivos** e **Mercado não exclusivos** (silver 2026, critério de
> `talentos_ano.sql`). Os **61 modelos** rodaram nas **4 séries** na mesma régua (D48 + R7 para as séries curtas,
> seção 5.0). Tela nova: em cada coluna, **cartões do mês vigente e dos dois seguintes** (calculados a partir da data da
> carga) e o gráfico de 2026 num cartão flutuante; botão **"Modelos comparados"** abre um `<dialog>` nativo com todos
> os modelos testados nas séries do filtro. Filtros: Todos = Inbound | Mercado; Exclusivos = Inbound | Mercado
> exclusivos; Não exclusivos = Inbound "não se aplica" | Mercado não exclusivos. Retrato de setembro refeito em
> 26/10/2026 17:58 com a carga de 26/10/2026 09:01 (São Paulo; dados até 25/10):
>
> | Série | Modelo (vencedor) | Teste jun–set | Jan–mai | Out (até 25/10 · previsto) | Nov | Dez |
> |---|---|---:|---:|---|---|---|
> | Inbound | Média de 6 meses | 14,4% | 26,9% | 133 · 138 (faixa 131–212), dentro da faixa | 138 (146–219) | 138 (147–221) |
> | Mercado | Rede neural (1 neurônio) — **não robusto** | 12,6% | 26,8% | 304 · 464 (334–483), dentro da faixa (−14%) | 517 (372–538) | 588 (423–612) |
> | Mercado exclusivos | Combinação de 6 — série só de 2026 | 10,9% | — | **87 · 196 (158–214), 42% abaixo do esperado** | 200 (161–219) | 204 (164–223) |
> | Mercado não exclusivos | Holt simples — série só de 2026 | 19,2% | — | 185 · 244 (194–318), dentro da faixa | 263 (209–343) | 282 (224–367) |
>
> Outubro do Mercado exclusivos: explicado na seção 5.0.7 (menos pedidos em lote e menos avulsos dos talentos
> exclusivos; a série própria não corrige). Sensibilidade com a silver 2025 (fonte fraca): seção 5.0.8, **não usada**.
> Mercado total: reavaliação e recomendação na seção 5.0.9.

> **Estado (26/10/2026, D55 — histórico, substituído pela D56):** a tela ficou só com os **dois gráficos** (Inbound | Mercado), largos, cada um
> com o nome simples do modelo ("Modelo: Média de 6 meses", "Modelo: Rede neural (1 neurônio)"), as previsões out/nov/dez
> e o **erro médio**. Saíram o painel "Vale mais que o palpite simples?" e o botão "Regras e modelos": a documentação
> (regras, todos os modelos, AutoTS) fica **só nesta ficha e no PRD**. Regra nova do Caio: **não existe Inbound de talento
> não exclusivo** (erro de cadastro, PD24): no filtro "Não exclusivos" o Inbound diz "Não se aplica: todo Inbound é de
> talento exclusivo"; no "Exclusivos", o Inbound é o Inbound inteiro. Re-treino com **AutoTS** dentro da régua D48
> (seção 5.6): não venceu; os vencedores continuam **média de 6 meses (Inbound)** e **rede neural de 1 neurônio
> (Mercado)**. Retrato de setembro refeito em 26/10/2026 17:00 com a carga de 26/10/2026 09:01 (São Paulo; dados até
> 25/10): Inbound **138 · 138 · 138**, Mercado **464 · 517 · 588** (iguais ao retrato anterior).

> **Estado (26/10/2026, D48 + D49):** "Pronta · 2 decisões abertas" (vencedor do Mercado; nov/dez como previsão ou
> cenário). Batalha de 26/10: corte único E3 (`app/corte.py`) no site, no job e no ML; job não dispara com `CONGELAR`
> nem no modo apresentação (J5); falha do job visível na página; contrato do snapshot (`validar()`) antes de gravar; pé
> do cartão com as duas medidas de erro; painel "Vale mais que o palpite simples?"; subtítulo "o modelo que menos errou
> no teste". O texto "faixa provável de 80%" segue na tela até decisão do Caio (a faixa cobriu 3 de 4 meses no Inbound e
> 1 de 4 no Mercado no teste; PRD 9.7).

| Item | Valor |
|---|---|
| Retrato | **setembro/2026**, calculado em 26/10/2026 01:29 com a gold de entradas processada em 23/10/2026 20:23 UTC (dados até 22/10); `ml/saida/retratos/2026-09.json` e a linha de `historico_previsoes.jsonl` |
| Acompanhamento | outubro até 25/10, carga 26/10/2026 09:01 (São Paulo), 16 de 21 dias úteis (`python -m ml.rodar --acompanhamento`, 26/10 11:12, código 0) |
| Inbound | média de 6 meses: **138 · 138 · 138** (out, nov, dez); faixas 131–212, 146–219, 147–221 (nov e dez com o número fora da própria faixa: decisão aberta); já entraram 133 em outubro |
| Mercado | rede neural de 1 neurônio: **464 · 517 · 588**; faixas 334–483, 372–538, 423–612; já entraram 304 em outubro |
| Erro no teste jun–set (h1) | Inbound 14% (≈ 20 pedidos/mês; repetir o último mês 26%) · Mercado 13% (≈ 49/mês; repetir o último mês 20%) |
| Verificação jan–mai (fora da escolha) | Inbound 27% (repetir o último mês 47%) · Mercado 27% (repetir o último mês 25%: a rede perde da ingênua aqui) |

Antes da reunião: `python -m ml.rodar --acompanhamento` na véspera (o site não roda o job com a base congelada) e
`python tools/checar_reuniao.py`, que confere se o acompanhamento é da mesma carga da gold de entradas.

> **Estado (26/10/2026, D48 — revisa a D47):** acompanhamento mensal de 2026 com números reais. Protocolo novo do Caio:
> janela móvel de 12 meses, teste jun–set/2026 (1 mês à frente), vence o menor erro. Retrato de **setembro/2026**
> calculado com a gold de entradas processada em **23/10/2026 20:23 UTC** (dados até 22/10/2026); outubro em andamento.
> Modelo calculado fora do site (job de ML) e lido de `ml/saida/previsao.json` (contrato v2). Nada publicado; em
> produção o job ainda não existe (seção 9). **Avaliação honesta na seção 5.5.**

## 1. Identificação

| Item | Onde |
|---|---|
| Rota | `/viu-agenciamento/previsao` (`?talentos=todos|exclusivos|nao-exclusivos`) |
| Página (só lê o JSON) | `app/apresentacoes/gestao_orcamentos/previsao/calculos.py` (regras P1–P12, D56), `template.html` (cartões de mês, gráfico, `<dialog>` "Modelos comparados"), `job.py` (J1–J6); `montar_previsao` em `apresentacao.py`; abertura do diálogo em `app/static/apresentacao.js` (bloco D56) |
| Estilo | `app/static/estilo.css`, bloco "Previsão de demanda (D56…)" (antes do bloco "movimento do portal"; CRLF) |
| Laboratório de ML | `ml/dados.py` (snapshot), `ml/regua.py` (protocolo D48, R1–R6), `ml/modelos/*.py` (61 modelos, 7 famílias; D55: `automatico.py`, AutoTS), `ml/rodar.py` (runner por série, rotina mensal, acompanhamento, `--sensibilidade`), `ml/previsao.py` (critério C1–C5 e contrato v3 P1–P10). D56: `ml/filtros.py` (repartição) saiu; snapshots por série em `ml/dados/serie_<recorte>.csv` |
| Saídas | `ml/saida/resultados.json` (régua, 4 séries), `ml/saida/previsao.json` (contrato v3 da página), `ml/saida/sensibilidade_2025.json` (D56, fonte fraca), `ml/saida/d55/` (saída da D48/D55 com os filtros repartidos), `ml/saida/retratos/<mês>.json` (cópia de cada retrato mensal), `ml/saida/historico_previsoes.jsonl` (uma previsão oficial por retrato, PD09), `ml/saida/rotina.log`; `ml/saida/d47/` guarda a saída do protocolo antigo |
| Testes | `tests/test_previsao_pagina.py` (contrato v2, critério, filtros, eixo 2026, layout, execução mensal, registro), `tests/test_ml_regua.py` (janela de 12 meses sem vazamento, protocolo antigo, não se aplica), `tests/test_ml_*.py` (especialistas), `tests/test_ml_automatico.py` (AutoTS na régua sem vazamento, D55) |
| Configuração | `PREVISAO_ARQ` (arquivo lido), `PREVISAO_JOB` (`off` desliga o disparo), `PREVISAO_PYTHON` (Python com as bibliotecas) em `app/config.py` |

### 1.1 Tabelas e colunas consumidas

**Vigente desde 27/10/2026 (D57: o ML só lê a gold, exceto a sensibilidade de 2025).** Código antigo × novo sobre a
mesma carga real (27/10, 11:11): séries Inbound e Mercado e lotes iguais; na exclusividade do Mercado, 1 pedido passa de
abril para março (81 → 82 em mar, 134 → 133 em abr): o card sem data de criação com saída em 08/04, que a gold põe em
março pelo calendário completo (Sexta-feira Santa); a SQL antiga do site só tinha os feriados fixos. Vale a partir da
próxima rodada do ML.

| Gold (BigQuery) | Tipo | Colunas usadas | Para quê |
|---|---|---|---|
| `gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_previsao_mensal` (`TAB_PREVISAO_MENSAL`) | view | `mes`, `tipo`, `pedidos`, `estimados`, `completo`, `dados_ate`, `_processado_em` | S1 Inbound, S2 Mercado (`ml/dados/serie_mensal.csv`) |
| `gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_2026_previsao_exclusividade_mensal` (`TAB_EXCLUSIVIDADE_MENSAL`) | view | `mes`, `tipo`, `exclusivos`, `nao_exclusivos`, `sem_talento`, `total` | S3/S4 (`ml/dados/exclusividade.csv`) |
| `gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_2026_previsao_lotes` (`TAB_LOTES`) | tabela | `data`, `recorte`, `pedidos`, `em_lote`, `avulsos` | S6: lotes do mês, somados até o mesmo dia (`ml/dados/lotes_vigente.csv`) |
| `gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_entrada_diaria` (`TAB_ENTRADA`) | tabela | `_processado_em` | o site: rodapé e gatilho do job (mês fechado novo ou carga nova) |
| `gglobo-viu-dados-hdg-prd.silver_monday.slv_agenciamento_2025_itens` (`TAB_SILVER_2025`) | silver | como abaixo | só a sensibilidade de 2025 (fonte fraca, não vai à tela; a silver 2025 não tem gold) |

As SQL de `app/sql/` e de `ml/dados.py` citadas nas seções 5.0.2 e seguintes são registro da extração até 26/10/2026.

Estado até 26/10/2026 (registro):

| Tabela (BigQuery) | Colunas | Para quê |
|---|---|---|
| `gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_entrada_diaria` (`TAB_ENTRADA`) | `data`, `tipo_de_input`, `quantidade`, `quantidade_estimada`, `_processado_em` | série mensal por tipo (E1); data da carga; último mês fechado; mês em andamento |
| `gglobo-viu-dados-hdg-prd.silver_monday.slv_agenciamento_2026_itens` (`TAB_TALENTO_ORIGEM`, exceção D30-b) | as de `app/sql/talentos_ano.sql` (bloco `pedidos`) + `tipo_de_input`; no diagnóstico S6, + `marca`, `nome_projeto` | exclusivos / não exclusivos / sem talento por mês e tipo em 2026 = as séries Mercado exclusivos e não exclusivos (D56) e o realizado do mês; lotes e avulsos do mês vigente |
| `gglobo-viu-dados-hdg-prd.silver_monday.slv_agenciamento_2025_itens` (D56, fonte fraca, só sensibilidade) | `criado_em`, `data_de_saida`, `state`, `tipo_de_input`, `talentos_exclusivos` | exclusividade de 2025 para a sensibilidade 5.0.8 (não vai à tela) |

O site em si só lê a gold de entradas (rodapé datado e decisão do job: mês fechado novo ou carga nova). O job lê as duas,
só com SELECT.

## 2. Pergunta e resposta esperada

"Quantos pedidos devem chegar até o fim do mês e do ano?" — quantos **pedidos (cards)** devem **entrar** em outubro (em
andamento), novembro e dezembro de 2026 no **Inbound** e no **Mercado**, com faixa provável de 80%, quanto o modelo errou
no teste de jun–set/2026 (menor é melhor) e qual modelo foi escolhido. Visão de acompanhamento mensal: só 2026.

## 3. O que aparece na tela

| Elemento | Texto / regra |
|---|---|
| Linha do topo | "Retrato de {mês fechado} · modelos de {gerado_em} · {mês em andamento} até {véspera da carga}"; "o mês fechou: o retrato novo está sendo calculado" (J1 = rotina) ou "realizado do mês sendo atualizado" (J1 = acompanhamento) |
| Seletor de talentos | Todos / Exclusivos / Não exclusivos, **sem número ao lado** (os números soltos "637 · 373 · 255" da D47 saíram: não diziam o que mediam) |
| Legenda | entraram · previsto no teste · mês em andamento · previsão e faixa provável |
| Cartão Inbound e cartão Mercado | modelo (Todos) ou abordagem do filtro; **out · nov · dez** (out = previsão de fechamento do retrato + "em andamento: N até 22/10"; nov e dez com a faixa); gráfico; rodapé "Erro médio no teste jun–set — erra em média X% ≈ N pedidos/mês · menor é melhor" |
| Sem confiança (C3) | "Poucos pedidos para prever com confiança (N por mês no teste)" ou "Erro alto demais no teste para prever com confiança" no lugar dos números; o gráfico mostra só o real; o erro continua no rodapé |
| Pé do cartão (P9, 2ª leva, 26/10/2026) | "Quanto errou: **14%** em jun–set e **27%** em jan–mai (≈ 20 a 34 pedidos/mês) · repetir o último mês erraria 26% e 47%" (Inbound); Mercado "13% … 27% (≈ 49 a 60) · 20% e 25%". Teste = onde o modelo foi escolhido (otimista); jan–mai = verificação fora da escolha. Nos filtros, só o teste. Subtítulo do cartão (Todos): "o modelo que menos errou no teste" (nome técnico no title) |
| ~~Vale mais que o palpite simples?~~ (P9; **retirado na D55**) | 3 linhas: modelo escolhido · média dos 3 últimos meses · repetir o último mês, com o erro no teste jun–set de cada tipo (Inbound 14% / 15% / 26%; Mercado 13% / 21% / 20%); ✓ no escolhido; nome técnico no title; nota "os nomes e o erro de todos os 58 modelos estão em 'Regras e modelos'" |
| ~~Modelo contra modelo~~ (até 26/10, 1ª leva) | "Erro médio no teste jun–set (menor é melhor)"; um representante por família + o vencedor de cada tipo (que substitui o representante da própria família); ✓ no escolhido; ○ na referência ingênua (repetir o último mês). Nos filtros, "no total do tipo" |
| ~~Botão "Regras e modelos"~~ (**retirado na D55**; o conteúdo está nesta ficha, seções 4 e 5) | `<details>` nativo: o que prevemos; protocolo de 12 meses e meses de teste; critério de escolha e ressalva; motivo de cada vencedor com a verificação jan–mai e a da ingênua; métricas e por que WAPE (e não F1/ROC/acurácia); quando roda (mensal + acompanhamento); filtros (abordagens, regra de confiança, tabela repartir × direto × escolhida); todos os 58 modelos (teste h1, h1–h3, verificação; "não se aplica" com motivo); ARIMAX × ARIMA; neurônios × erro; limites |
| Faixa de conclusão do pé | **retirada** (D48, item 6) |
| Nome do modelo (D55) | no topo de cada gráfico, em nome simples: Todos "Modelo: Média de 6 meses" / "Modelo: Rede neural (1 neurônio)"; filtros repartidos "Modelo: … × parcela do grupo em 2026" (ou "nos 3 últimos meses"); previsão direta "Modelo: …, direto no grupo"; Inbound exclusivos "Modelo: Média de 6 meses (todo o Inbound)"; nome técnico no title |
| Pé do cartão (D55) | rótulo "Erro médio" (antes "Quanto errou"); mesmo conteúdo da P9; no Inbound exclusivos, igual ao Todos (teste, verificação e ingênua) |
| Inbound · Não exclusivos (D55) | cartão sem número e sem gráfico: "Não se aplica: todo Inbound é de talento exclusivo" + "Os poucos pedidos de Inbound marcados como não exclusivos são erro de cadastro e contam em Exclusivos." |
| Layout (D55) | `.pv-corpo` com duas colunas iguais; cada gráfico em duas larguras: `.pv-svg-largo` (viewBox 440×250, duas colunas) e `.pv-svg-estreito` (340×270, uma coluna/celular), trocadas pela mesma container query do layout de uma coluna |
| Rodapé | "Dados até 22/10/2026 · atualizados em 23/10/2026, 17:23" (gold de entradas, INI-D1) |
| **D56 — colunas** | Todos: Inbound \| Mercado; Exclusivos: Inbound ("todo o Inbound é de talento exclusivo") \| Mercado "talentos exclusivos"; Não exclusivos: Inbound "Não se aplica" (cartão tracejado) \| Mercado "talentos não exclusivos". O Mercado fica sempre à direita; as duas colunas dividem as linhas (subgrid), então os gráficos ficam alinhados mesmo com o "Por quê" de um lado só |
| **D56 — cartões de mês** | mês vigente (a partir da carga) + os 2 seguintes; vigente: "133 até 25/10", barra do ritmo, "de 138 previstos", situação ("✓ dentro da faixa (+26%)" ou "▼ 42% abaixo do esperado"); seguintes: previsão e "146–219 provável"; regra P10, seção 5.0.6 |
| **D56 — Por quê** | só com o vigente fora da faixa: lotes e avulsos até o mesmo dia do mês × média dos 4 meses anteriores; nos recortes de exclusividade, os pedidos do mês sem talento (P11) |
| **D56 — gráfico** | cartão flutuante; "Modelo: …" e "erro médio X% em jun–set" no topo; pé com a verificação, o erro em pedidos/mês, a ingênua e o selo "não robusto" ou "confiança menor · série só de 2026"; três larguras do SVG (480×250, 620×250 em cartão ≥ 640 px, 340×250 no celular) |
| **D56 — Modelos comparados** | botão discreto à direita dos controles; `<dialog>` nativo (P12, seção 5.0.6) |

Gráfico (SVG, textos de 13 unidades ≥ 11 px reais em 1280 px e 390 px): **eixo fixo jan–dez/2026** (nada de 2024/2025);
colunas do real (jan–set), anel vazio = previsão do teste feita no fim do mês anterior (jun–set), coluna hachurada =
realizado parcial de outubro, zonas "teste" (jun–set) e "previsão" (out–dez) com a faixa p10–p90 e o ponto; meses futuros
vazios até a previsão. Os valores de cada mês estão numa tabela para leitor de tela (dentro de `<div class="so-leitor">`,
que não estica a lâmina no celular).

## 4. Regras

### Página (`previsao/calculos.py`)

| ID | Regra |
|---|---|
| P1 | Série = quantidade + quantidade_estimada da gold de entradas (E1) por mês e tipo; cada previsão treina só com os 12 meses fechados anteriores (D48) |
| P2 | Teste = jun, jul, ago, set/2026 no horizonte 1; o gráfico mostra esses 4 pontos; o erro da tela é o WAPE desses 4 meses |
| P3 | Modelo de cada tipo = o de menor erro no teste; empate (< 1 ponto) = o mais simples (C1, `ml/previsao.py`) |
| P4 | Filtros: cada filtro e tipo usa a abordagem de menor erro no teste (C2) |
| P5 | Sem confiança (C3): média do filtro no teste < 30 pedidos/mês ou WAPE > 40% → mensagem no lugar do número |
| P6 | Execução mensal: retrato refeito quando o mês fecha; o mês em andamento mostra a previsão de fechamento do retrato e o realizado até a véspera da carga (acompanhamento, atualizado a cada carga) |
| P7 | Eixo fixo jan–dez/2026 |
| P8 | WAPE = Σ\|prev − real\| ÷ Σ real ("errou X%"); MAE em pedidos/mês (igual à régua R3) |
| P9 | (2ª leva, G4-N8) Pé do cartão no filtro Todos com as duas medidas: WAPE h1 do teste (`metricas.1`) e da verificação jan–mai (`series[t].metricas.verificacao`), MAE das duas como faixa, e a ingênua (`series[t].ingenua.wape` e `.verificacao`); painel `palpite()` com 3 linhas (vencedor `series[t].metricas.1.wape`, `ref_media_3m` e `ingenua`). A conta e o vencedor não mudam |
| P10 (D56) | Cartões do mês vigente + 2 seguintes a partir da carga (`meses_dos_cartoes`), situação do vigente (`situacao`: esperado = previsão × dias úteis decorridos ÷ do mês; fora da faixa proporcional = abaixo/acima) |
| P11 (D56) | "Por quê" do vigente fora da faixa (diagnóstico S6) e pedidos sem talento nos recortes de exclusividade |
| P12 (D56) | Diálogo "Modelos comparados" (`dialogo()`): todos os modelos das séries do filtro, por família, teste e verificação, vencedor/alternativa; `<dialog>` nativo com `commandfor`/`command` e JS de reserva |
| P10 antiga | (D55) Tela só com os dois gráficos, o nome simples do modelo (`modelo_texto`), as previsões e o erro médio; sem `comparacao`/`palpite`/`todos_modelos` e sem `<details>`. Cartão com `nao_se_aplica` (Inbound não exclusivo) = estado limpo sem número nem gráfico. Gráfico em duas larguras (`grafico` 440×250 e `grafico_estreito` 340×270) |

### Protocolo (`ml/regua.py`, D48)

- **R1** janela móvel de 12 meses: cada previsão treina só com os 12 meses fechados anteriores à origem (jun/26 com
  jun/25–mai/26; jul/26 com jul/25–jun/26…). 2025 entra só dentro da janela.
- **R2** teste = h1 de jun–set/2026 (o critério); informativos: h2 e h3 dos mesmos meses (origens anteriores, cada uma
  com a sua janela) e a **verificação** = h1 de jan–mai/2026, fora do período de escolha.
- **R3** métricas (chaves "1" = critério, "2", "3", "todos" = h1–h3 jun–set, "verificacao").
- **R4** "não se aplica": modelo que declara `minimo_treino` maior que a janela não roda (fica registrado com o motivo).
- **R5** futuro = out, nov, dez/2026 com treino out/25–set/26; o mês em andamento nunca treina.
- **R6** protocolo antigo D47 acessível: `backtest(..., pares=pares_d47(), janela=None)`.
- **R7** (D56) séries curtas: janela expansiva (até 12 meses) e mínimo de meses por modelo (`minimo()`); origem curta
  não é prevista; teste incompleto = "não se aplica" naquela série; verificação só completa (seção 5.0.3). Sem janela
  (protocolo D47) a R7 não vale.

Modelos ajustados para 12 pontos: **Prophet** com sazonalidade anual só com 24+ meses (2 ciclos) — `prophet_log`,
`prophet_natural` e `prophet_log_degrau2026` **não se aplicam**; `prophet_auto` escolhe só entre as configurações sem
sazonalidade. **`comb_sazonal`** (efeito do mesmo mês do ano anterior, 15 meses) **não se aplica** — com 12 meses cairia
sempre na média de 3 meses. **Rede neural**: a outra série (treino "global") também é cortada na mesma janela.
**Boosting**: o lag 12 nunca existe nas linhas de treino; a coluna fica vazia e as árvores a ignoram. `ref_mesmo_mes_ano_anterior`
roda (usa o 1º mês da janela), mas sem faixa (a faixa empírica pede 12 meses antes da 1ª origem interna).

### Critério e contrato (`ml/previsao.py`)

- **C1** vence, por série, o **menor WAPE h1 jun–set/2026** entre os modelos que se aplicam; **empate = diferença < 1
  ponto** → o mais simples: referência → combinação → série clássica (inclui ARIMA sem exógenas) → ARIMAX/Prophet →
  boosting → rede neural; dentro da rede, menos neurônios (a `mlp_auto`, que ainda busca o tamanho, conta como a maior).
  **Ressalva registrada (critério do Caio):** a escolha é feita no próprio período de teste (4 meses, 54 modelos que se
  aplicam), então o erro do vencedor é otimista; a verificação jan–mai e o PD09 medem fora da escolha.
- **C2** filtros: por tipo e filtro, menor WAPE h1 jun–set entre **(a) repartir** a previsão do tipo pela parcela do
  grupo nos meses de 2026 **anteriores à origem** (`a_todos` = todos; `a_3m` = os 3 últimos) e **(b) prever direto** a
  série do filtro (`ml/filtros.py`, 11 candidatos simples, 3 a 9 meses de dados). Empate (< 1 ponto) = repartir (um modelo
  só, grupos coerentes com o total). A (b) escolhe entre mais candidatos no próprio teste: vantagem a favor dela.
- **C3** sem confiança: média do filtro no teste < 30 pedidos/mês **ou** WAPE > 40% (limites fixados antes de ver o
  resultado).
- **C4** execução mensal (seção 4, Job).
- **C1 (D55)** o AutoTS (`autots_1`–`autots_3`) entra na disputa como a família **mais complexa** (nível 6, acima da
  rede neural): empate de menos de 1 ponto com qualquer outro modelo fica com o outro.
- **P8 do contrato (D55)** Inbound só de exclusivos: `filtros.Inbound.exclusivos` = cópia do total do tipo (abordagem
  `tipo_inteiro`; histórico, teste, futuro e erro iguais ao Todos); `filtros.Inbound.nao_exclusivos` = `nao_se_aplica`
  (sem futuro); acompanhamento do Inbound com exclusivos = o Inbound inteiro e não exclusivos vazio; casos contados no
  bloco `qualidade.nao_exclusivo_no_inbound` (PD24). O Mercado segue a C2, só com a parcela do próprio Mercado.
- **P9 do contrato (D55)** bloco `comparacao_automatica` (os 3 do AutoTS, a rede neural, as referências e o vencedor,
  com teste, verificação, h1–h3 e o modelo que o AutoTS escolheu em cada janela) — fonte da seção 5.6.
- **C5** (D56) robustez, informativa: o vencedor bate a ingênua no teste e na verificação? Se não, `alternativa` = C1
  restrita aos que batem a ingênua nos dois. Não troca o vencedor (seção 5.0.9).
- **Contrato v3 P1–P10** (docstring de `ml/previsao.py`): 4 séries, `filtros` = lista de séries por filtro, `comparados`
  por série, `robustez`, acompanhamento por série com lotes e sem talento; **P7** = um registro por retrato e protocolo
  (D56: linha nova do mesmo retrato com `substitui`).
- (D48/D55, histórico) **Contrato P1–P7**; **P7** = um registro por retrato mensal (PD09), com os filtros.

### Job (`previsao/job.py`) — execução mensal

- **J1** a cada carga da gold de entradas (`dados.entrada.ao_carregar`) ou com a página aberta: último mês fechado da carga
  (mês anterior ao do dia seguinte ao **fim E3**: véspera, em São Paulo, de `MAX(_processado_em)`; `app/corte.py`, J6 —
  até 26/10/2026 era `MAX(data)`) > mês do retrato → **`python -m ml.rodar --rotina`** (snapshot novo, os
  58 modelos, os filtros, o retrato e o histórico; ~9 min, **uma vez por mês**); mesmo mês e carga diferente da do
  acompanhamento → **`python -m ml.rodar --acompanhamento`** (só o realizado do mês em andamento; segundos; a previsão
  não muda); senão, nada. A rotina confere de novo e, se o retrato do mês já existe, só atualiza o acompanhamento
  (`--forcar` refaz).
- **J2** só com `PREVISAO_JOB` ligado (desligado em produção), pasta `ml/` e `statsmodels`. **J3** um job por vez (trava
  `ml/saida/rotina.lock` < 3 h, gravada também pelo `--acompanhamento`) e 30 min entre disparos. **J4** saída em
  `ml/saida/rotina.log`; a última tentativa (modo, início, fim, código, erro) em `ml/saida/rotina_estado.json`, gravado
  de forma atômica. Se ela falhou e nada está rodando, a página diz "a última atualização falhou em dd/mm/aaaa hh:mm;
  mostrando o retrato anterior" (ícone + texto); "sendo calculado" só aparece com o job de fato rodando.
- **J5** (batalha 2, 26/10/2026) com `CONGELAR` ou `MODO=apresentacao`, o site **não dispara** o job (uma só carga na
  reunião). Na véspera: subir o servidor congelado e rodar à mão `python -m ml.rodar --acompanhamento`.
- **J6** corte único: `app/corte.py` (E3) serve o site (`app.dados.data_carga`), o job (`da_carga`, `mes_fechado`) e o
  ML (`ml/dados.py`, `SQL_FIM`). Conferido em 26/10/2026 no BigQuery: fim E3 = **25/10** (MAX(data) = 24/10;
  `_processado_em` 26/10 12:01 UTC) = rodapé do site. Em 02/11/2026 (31/10 é sábado) outubro fecha pela E3.
- **Contrato do snapshot (G4-N13):** `ml/dados.validar()` antes de gravar — uma carga só (`processado_em` e `dados_ate`
  únicos), contagens inteiras e não negativas, meses completos sem buraco por tipo, exclusividade da mesma carga e partes
  somando o total; com problema, `SnapshotInvalido` e nada é gravado (sem retrato nem histórico). Gold × silver por mês
  e tipo só vai para o log (hoje: Mercado mar 252 × 251, abr 228 × 229). CSVs gravados por troca atômica. Consultas com
  `config.PROJETO` e `config.LABELS`. Histórico (`historico_previsoes.jsonl`): toda linha com `retrato` e `protocolo`
  (`linhas_do_historico`); o registro da D47 já está em `ml/saida/d47/`.
- **Rótulos:** mês de outro ano que não o do gráfico sai com o ano ("jan/27"); o eixo segue jan–dez/2026 (PD22).
- Observado em 26/10: com o `previsao.json` ainda na versão 1, a página aberta disparou uma rotina completa (J1 sem retrato
  válido) — comportamento esperado; levou ~9 min (569 s somando os modelos).

## 5.0 D56 — uma série e um modelo por recorte (26/10/2026; carga de 26/10/2026 09:01, dados até 25/10)

Decisão do Caio (26/10/2026): cada recorte tem a **sua série** e o **seu modelo**, treinado só nela; nada de repartir a
previsão do tipo pela parcela do grupo (a abordagem "a" da D48, `ml/filtros.py`, saiu). Todos os modelos rodam em
todas as séries na mesma régua; vence o menor WAPE no teste (regra D48) e a verificação jan–mai diz se o vencedor é
robusto. Código: `ml/dados.py` (S1–S6), `ml/regua.py` (R7, `carregar_recortes`), `ml/rodar.py` (por série),
`ml/previsao.py` (contrato v3, C5), `previsao/calculos.py` (P10–P12) e `template.html`.

### 5.0.1 As quatro séries (snapshots em `ml/dados/`)

| Série (nome no contrato) | Tabela | Colunas usadas | Regras de filtro | Snapshot | Meses fechados | Treino no 1º mês do teste |
|---|---|---|---|---|---|---|
| **Inbound** (S1) | `gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_entrada_diaria` | `data`, `tipo_de_input`, `quantidade`, `quantidade_estimada`, `_processado_em` | `tipo_de_input = 'Inbound'`; `data` de 01/10/2024 até o fim E3 (véspera, em São Paulo, de `MAX(_processado_em)`); pedidos = `quantidade + quantidade_estimada` (E1); mês completo = `LAST_DAY` ≤ fim E3 | `serie_inbound.csv` | 24 (out/24–set/26) | 12 (jun/25–mai/26) |
| **Mercado** (S2) | a mesma gold | as mesmas | `tipo_de_input = 'Mercado'`; o resto igual | `serie_mercado.csv` | 24 | 12 |
| **Mercado exclusivos** (S3) | `gglobo-viu-dados-hdg-prd.silver_monday.slv_agenciamento_2026_itens` (exceção D30-b) | `criado_em`, `data_de_entrada`, `data_de_saida`, `state`, `talento`, `talentos_exclusivos`, `exclusivo`, `tipo_de_input` | bloco `pedidos` de `app/sql/talentos_ano.sql` (R1 data de criação, R21 cadastro retroativo, R2 data estimada, R5 `state = 'active'`, R4 até o fim E3); `tipo_de_input = 'Mercado'` e exclusivo = `COALESCE(exclusivo, IF(criado_em IS NULL AND talentos_exclusivos IS NOT NULL, TRUE, NULL))` = TRUE | `serie_mercado_exclusivos.csv` | 9 (jan–set/26) | **5** (jan–mai/26) |
| **Mercado não exclusivos** (S4) | a mesma silver | as mesmas | idem, exclusivo = FALSE (inclui "Squad de Talentos", regra 60 da silver); **sem talento fica fora dos dois** | `serie_mercado_nao_exclusivos.csv` | 9 | **5** |

Cada CSV tem `mes, pedidos, completo, fonte, dados_ate, processado_em`; o `completo` das séries da silver é o da gold no
mesmo mês e tipo (E3), e os quatro saem da mesma carga (`ml/dados.validar()` recusa carga misturada e mês do Mercado
faltando na exclusividade). O Inbound é a série inteira porque todo Inbound é de talento exclusivo (D55, PD24): os 78
pedidos de jan–set marcados como não exclusivos são erro de cadastro. **S3 + S4 < S2**: os pedidos sem talento
informado (46 em jan–set; 32 em outubro até 25/10) não entram em nenhum dos dois, como na página Talentos; as previsões
dos dois recortes não são forçadas a somar a do total.

Valores (jan → set/2026): Mercado exclusivos **62, 81, 81, 134, 164, 177, 186, 154, 194**; Mercado não exclusivos
**60, 106, 163, 94, 170, 155, 213, 158, 272**; outubro até 25/10: 87 e 185 (e 32 sem talento). Inbound e Mercado: os
mesmos de antes (seção 5.1; Mercado set/26 = 477).

### 5.0.2 SQL completo (só SELECT; projeto `gglobo-viu-dados-hdg-prd`, conta `caio.barroso@viu.com.br`)

S1 e S2 (`ml/dados.py::SQL_SERIE`; esperado: Inbound jun–set 112, 165, 156, 129 e out 133; Mercado 339, 404, 322, 477
e out 304):

```sql
WITH fim AS (SELECT COALESCE(DATE_SUB(DATE(MAX(_processado_em), 'America/Sao_Paulo'), INTERVAL 1 DAY), MAX(data)) AS dados_ate,
                    MAX(_processado_em) AS processado_em
             FROM `gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_entrada_diaria`)
SELECT FORMAT_DATE('%Y-%m', DATE_TRUNC(e.data, MONTH)) AS mes, e.tipo_de_input AS tipo,
       SUM(e.quantidade + e.quantidade_estimada) AS pedidos, SUM(e.quantidade_estimada) AS estimados,
       LAST_DAY(MIN(e.data)) <= ANY_VALUE(f.dados_ate) AS completo,
       ANY_VALUE(f.dados_ate) AS dados_ate, ANY_VALUE(f.processado_em) AS processado_em
FROM `gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_entrada_diaria` e CROSS JOIN fim f
WHERE e.tipo_de_input IN ('Inbound', 'Mercado') AND e.data >= DATE '2024-10-01' AND e.data <= f.dados_ate
GROUP BY mes, tipo ORDER BY tipo, mes;
```

S3 e S4 (`ml/dados.py::_sql_exclusividade`, o bloco `pedidos` de `talentos_ano.sql` com a coluna do tipo; conferido no
BigQuery em 26/10/2026: resultado igual ao snapshot, linha a linha):

```sql
WITH parametros AS (SELECT DATE '2026-10-25' AS fim, DATE_TRUNC(DATE '2026-10-25', YEAR) AS inicio),
feriados AS (
  SELECT ARRAY_AGG(DATE(a, f.m, f.d)) AS dias
  FROM UNNEST([EXTRACT(YEAR FROM DATE '2026-10-25') - 1, EXTRACT(YEAR FROM DATE '2026-10-25')]) AS a,
    UNNEST(ARRAY<STRUCT<m INT64, d INT64>>[(1,1),(1,20),(1,25),(4,21),(4,23),(5,1),(7,9),(9,7),(10,12),(11,2),
      (11,15),(11,20),(12,24),(12,25),(12,31)]) AS f
),
pedidos AS (
  SELECT
    COALESCE(
      IF(i.data_de_saida < DATE(i.criado_em) AND i.data_de_entrada <= i.data_de_saida, i.data_de_entrada, DATE(i.criado_em)),
      (SELECT ARRAY_AGG(d ORDER BY d DESC)[SAFE_OFFSET(4)]
       FROM UNNEST(GENERATE_DATE_ARRAY(DATE_SUB(i.data_de_saida, INTERVAL 21 DAY), DATE_SUB(i.data_de_saida, INTERVAL 1 DAY))) AS d
       WHERE EXTRACT(DAYOFWEEK FROM d) BETWEEN 2 AND 6 AND d NOT IN UNNEST(f.dias))) AS dia,
    i.talento, i.tipo_de_input,
    COALESCE(i.exclusivo, IF(i.criado_em IS NULL AND i.talentos_exclusivos IS NOT NULL, TRUE, NULL)) AS exclusivo
  FROM `gglobo-viu-dados-hdg-prd.silver_monday.slv_agenciamento_2026_itens` i CROSS JOIN feriados f
  WHERE i.state = 'active'
)
SELECT FORMAT_DATE('%Y-%m', DATE_TRUNC(p.dia, MONTH)) AS mes, p.tipo_de_input AS tipo,
       COUNTIF(p.exclusivo) AS exclusivos, COUNTIF(NOT p.exclusivo) AS nao_exclusivos,
       COUNTIF(p.exclusivo IS NULL) AS sem_talento, COUNT(*) AS total
FROM pedidos p CROSS JOIN parametros pr
WHERE p.dia BETWEEN pr.inicio AND pr.fim AND p.tipo_de_input = 'Mercado'
GROUP BY mes, tipo ORDER BY tipo, mes;
-- esperado (exclusivos / não exclusivos / sem talento): jan 62/60/3 · fev 81/106/0 · mar 81/163/7 · abr 134/94/1 ·
-- mai 164/170/2 · jun 177/155/7 · jul 186/213/5 · ago 154/158/10 · set 194/272/11 · out (até 25/10) 87/185/32
```

S6, diagnóstico do mês vigente (`ml/dados.py::_sql_lotes`; mesmo bloco `pedidos` acrescido de
`COALESCE(i.marca, REGEXP_EXTRACT(i.nome_projeto, r'^\[([^\]]+)\]')) AS marca` e com `inicio` = 4 meses antes do mês de
`fim`): por recorte e mês, até o mesmo dia do mês de `fim`, pedidos, **em lote** (3 ou mais do recorte com a mesma
marca no mesmo dia) e avulsos:

```sql
-- (parametros com inicio = DATE_SUB(DATE_TRUNC(DATE '2026-10-25', MONTH), INTERVAL 4 MONTH); feriados e pedidos como acima, + marca)
, recortes AS (
  SELECT p.*, r AS recorte FROM pedidos p CROSS JOIN parametros pr,
    UNNEST(ARRAY_CONCAT(IF(p.tipo_de_input = 'Inbound', ['inbound'], []), IF(p.tipo_de_input = 'Mercado', ['mercado'], []),
      IF(p.tipo_de_input = 'Mercado' AND p.exclusivo, ['mercado_exclusivos'], []),
      IF(p.tipo_de_input = 'Mercado' AND NOT p.exclusivo, ['mercado_nao_exclusivos'], []))) AS r
  WHERE p.dia BETWEEN pr.inicio AND pr.fim AND EXTRACT(DAY FROM p.dia) <= EXTRACT(DAY FROM pr.fim)
),
grupos AS (SELECT recorte, FORMAT_DATE('%Y-%m', dia) AS mes, dia, marca, COUNT(*) AS n FROM recortes GROUP BY recorte, mes, dia, marca)
SELECT recorte, mes, SUM(n) AS pedidos, SUM(IF(marca IS NOT NULL AND n >= 3, n, 0)) AS em_lote,
       SUM(IF(marca IS NOT NULL AND n >= 3, 0, n)) AS avulsos
FROM grupos GROUP BY recorte, mes ORDER BY recorte, mes;
-- esperado (mercado_exclusivos, até o dia 25): jun 143 (34 em lote, 109 avulsos) · jul 141 (51, 90) · ago 135 (50, 85)
-- · set 171 (63, 108) · out 87 (17, 70)
```

S5 (silver 2025, fonte fraca, só a sensibilidade 5.0.8): `ml/dados.py::SQL_EXCLUSIVIDADE_2025` — data = `criado_em`
(sem ele, `data_de_saida` − 5 dias úteis, R2), `state = 'active'`, exclusivo = `talentos_exclusivos` preenchido,
jan–dez/2025, por mês e tipo.

### 5.0.3 Régua (R7) e o mínimo de meses de cada modelo

A régua é a da D48 (teste = h1 de jun–set/2026; verificação = h1 de jan–mai/2026; menor WAPE vence; empate < 1 ponto =
o mais simples). Para as séries curtas, **R7**: a janela continua "os até 12 meses fechados antes da origem" — com
menos de 12, ela é **expansiva** (jun/26 treina com jan–mai = 5 meses; jul com 6; ago com 7; set com 8; o futuro com
jan–set = 9). Cada modelo tem um mínimo de meses de treino, decidido antes de ver os resultados (`regua.minimo()`):

| Mínimo | Modelos |
|---|---|
| 1 | último mês (`ref_ultimo_mes`) |
| 3 | média de 3 meses; suavização exponencial, Holt simples, Theta simples, último mês + crescimento, crescimento % médio, combinação de 6, média de 3 métodos (`comb_*` simples) |
| 6 | média de 6 meses; reta dos últimos 6 meses |
| 12 (a janela) | todo o resto: ARIMA/ARIMAX e ETS/Theta do statsmodels (regra do projeto nº de parâmetros ≤ n/4), rede neural, boosting, Prophet, AutoTS, combinações com backtest interno ou correção de viés, mesmo mês do ano anterior |
| 15 e 24 | sazonal (`comb_sazonal`) e Prophet sazonal: "não se aplica" em todas as séries (R4) |

Origem com menos meses que o mínimo não é prevista; se faltar um mês do teste, o modelo **"não se aplica" naquela
série** (com o motivo, registrado em `resultados.json` e no diálogo). A verificação jan–mai só vale completa (5 meses);
nas séries curtas ela não existe ("sem verificação": a série começa em jan/2026). Nas séries longas toda origem tem 12
meses: os resultados do Inbound e do Mercado são **idênticos** aos da D48/D55 (conferido modelo a modelo).
Teste de vazamento: `tests/test_ml_regua.py::test_series_curtas_janela_expansiva_sem_vazamento`.

### 5.0.4 Resultados por série (WAPE h1; teste jun–set = onde se escolhe; verificação jan–mai = fora da escolha)

**Inbound** — 57 modelos se aplicam, 4 não (sazonais). Robusto: bate a ingênua nos dois períodos.

| Posição | Modelo | Teste | Verificação |
|---:|---|---:|---:|
| 1 | ARIMAX (0,1,1) `arimax_011` | 13,5% | 27,4% |
| 2 | ARIMAX (1,1,0) `arimax_110` | 14,2% | 29,0% |
| 3 | Seleção pelo passado `comb_selecao` | 14,3% | 34,9% |
| 4 | **Média de 6 meses `ref_media_6m` — vencedor** | **14,4%** | **26,9%** |
| 5 | AutoTS 1º `autots_1` | 15,0% | 37,9% |
| — | Último mês (ingênua) | 26,0% | 47,0% |

Motivo: os quatro primeiros empatam (menos de 1 ponto do menor erro) e fica o mais simples, a média de 6 meses.

**Mercado (total)** — 57 se aplicam, 4 não. **Não robusto**: no teste erra 13% contra 20% da ingênua, mas em jan–mai
erra 27% contra 25% (27º de 57 na verificação).

| Posição | Modelo | Teste | Verificação |
|---:|---|---:|---:|
| 1 | Rede neural (4 + 2) `mlp_4x2` | 12,6% | 27,2% |
| 2 | **Rede neural (1 neurônio) `mlp_1` — vencedor** | **12,6%** | **26,8%** |
| 3 | Rede neural (8 + 4) `mlp_8x4` | 12,7% | 27,2% |
| 4 | Rede neural (tamanho no treino) `mlp_auto` | 12,8% | 26,8% |
| 5 | Rede neural (8) `mlp_8` | 12,8% | 26,9% |
| — | ARIMA com tendência `arima_100_ct` (alternativa robusta, C5) | 16,5% | 20,4% |
| — | Último mês (ingênua) | 19,8% | 24,7% |

Motivo: as 11 redes empatam (12,6–13,0%) e fica a de 1 neurônio (a mais simples do empate).

**Mercado exclusivos** — **9 se aplicam**, 52 não (46 pedem 12 meses de treino, 2 pedem 6, 4 sazonais). Sem
verificação (série só de 2026): **confiança menor**.

| Posição | Modelo | Teste |
|---:|---|---:|
| 1 | **Combinação de 6 `comb_mediana` — vencedor** | **10,9%** |
| 2 | Theta simples `comb_theta` | 11,0% |
| 3 | Média de 3 métodos `comb_media` | 11,0% |
| 4 | Holt simples `comb_holt_amort` | 11,4% |
| 5 | Último mês (ingênua) `ref_ultimo_mes` | 13,2% |

Motivo: as quatro combinações empatam (< 1 ponto), todas do mesmo nível; fica a de menor erro, a combinação de 6
(mediana de suavização, Holt, Theta, último mês + crescimento, média de 3 meses e último mês). Bate a ingênua no teste
(10,9% × 13,2%).

**Mercado não exclusivos** — 9 se aplicam, 52 não. Sem verificação: **confiança menor**.

| Posição | Modelo | Teste |
|---:|---|---:|
| 1 | **Holt simples `comb_holt_amort` — vencedor** | **19,2%** |
| 2 | Média de 3 métodos `comb_media` | 22,4% |
| 3 | Theta simples `comb_theta` | 24,3% |
| 4 | Média de 3 meses `ref_media_3m` | 25,6% |
| 5 | Combinação de 6 `comb_mediana` | 25,9% |
| — | Último mês (ingênua) | 30,3% |

Motivo: menor erro sem empate (3,2 pontos à frente do 2º). Bate a ingênua no teste (19,2% × 30,3%).

Previsto no teste (h1) × real — Mercado exclusivos: jun 169 × 177, jul 183 × 186, ago 192 × 154, set 165 × 194
(|8| + |3| + |38| + |29| = 78 ÷ 711 = 10,9%); Mercado não exclusivos: jun 162 × 155, jul 177 × 213, ago 205 × 158,
set 208 × 272 (7 + 36 + 47 + 64 = 154 ÷ 798 ≈ 19%; 19,2% sem arredondar). No teste, as séries curtas não têm faixa (a faixa empírica pede
6 razões internas e as origens têm 5 a 8 meses).

### 5.0.5 Memória de cálculo das previsões e das faixas (out · nov · dez/2026)

- **Inbound** (média de 6 meses, treino abr–set/26): (99 + 169 + 112 + 165 + 156 + 129) ÷ 6 = **138,3** nos três meses.
  Faixa = 138,3 × quantis 10%/90% das razões real ÷ previsto nas origens internas do treino (ModeloPontual): out
  131–212, nov 146–219, dez 147–221 (nov/dez com o número fora da própria faixa: a média subestimou o passado recente).
- **Mercado** (rede de 1 neurônio, treino out/25–set/26 com as janelas do Inbound como exemplos extras, N3): **464 ·
  517 · 588**; faixa 334–483, 372–538, 423–612.
- **Mercado exclusivos** (combinação de 6, treino jan–set/26, 9 meses): componentes para outubro — suavização 194
  (alfa 1,0), Holt 197,0, Theta 202,3, último mês + crescimento médio 210,5, média de 3 meses 178,0, último mês 194 →
  mediana = (194 + 197) ÷ 2 = **195,5**; nov 199,7; dez 203,5. Faixa = previsão × (0,808; 1,095), os quantis 10%/90% de
  6 razões real ÷ previsto das origens internas jul, ago e set (h1 a h3 juntos, porque cada horizonte tem menos de 4):
  **158–214, 161–219, 164–223**.
- **Mercado não exclusivos** (Holt simples): **243,9 · 263,1 · 281,9**; faixa × (0,794; 1,302): 194–318, 209–343,
  224–367.

### 5.0.6 O que a tela mostra (cartões de mês, P10–P12)

- **Mês vigente + 2 seguintes, a partir da carga:** vigente = o mês do dia seguinte a `dados_ate` (carga de 26/10 →
  dados até 25/10 → outubro; na carga de 02/11, com dados até 01/11, novembro, dezembro e janeiro/27; mês sem previsão
  no retrato = "aguardando o retrato").
- **Vigente:** realizado até a véspera da carga; "de N previstos" (previsão de fechamento do retrato); barra = realizado
  ÷ previsão com a marca dos dias úteis decorridos (16 de 21); situação = realizado contra o **esperado até agora** =
  previsão × 16 ÷ 21. "Abaixo"/"acima" quando o realizado sai da faixa na mesma proporção (p10 e p90 × 16/21), senão
  "dentro da faixa"; o % é realizado ÷ esperado − 1. Hoje: Inbound 133 × 105 esperado (+26%, dentro: 100–161); Mercado
  304 × 354 (−14%, dentro: 254–368); **Mercado exclusivos 87 × 149 (−42%, abaixo: 120–163)**; não exclusivos 185 × 186
  (0%, dentro).
- **Por quê** (só quando o vigente sai da faixa; diagnóstico S6): "Até o dia 25: 17 pedidos em lote (média de jun–set:
  50) e 70 avulsos (98)". Nos recortes de exclusividade: "32 pedidos do Mercado em outubro ainda sem talento informado
  (fora deste recorte)".
- **Gráfico:** jan–dez/2026, real, previsto no teste, outubro hachurado, previsões com faixa; topo "Modelo: … · erro
  médio X% em jun–set"; pé "fora do teste (jan–mai): Y% · ≈ N pedidos/mês · repetir o último mês erraria …" e o selo
  "não robusto" (Mercado) ou "confiança menor · série só de 2026" (exclusividade).
- **Modelos comparados** (`<dialog>` nativo: foco no botão Fechar ao abrir, Esc e o botão fecham, clicar fora fecha, o
  foco volta ao botão): resumo por série (vencedor, erros, robustez, alternativa) e a tabela de todos os modelos por
  família com teste e verificação em cada série do filtro; vencedor com ✓ (e texto para leitor de tela), alternativa
  sublinhada, "não se aplica" com o motivo no `title`; família sem nenhum modelo aplicável = uma linha.

### 5.0.7 Outubro do Mercado exclusivos: por que está tão abaixo (item 3 da D56)

Até 25/10 entraram **87** pedidos de talento exclusivo no Mercado; a previsão de fechamento é 196 (esperado até agora
≈ 149). Comparando com os meses fechados **no mesmo ponto do mês** (até o dia 25; SQL S6 e a consulta por talento
abaixo, BigQuery, 26/10/2026):

| Até o dia 25 | jun | jul | ago | set | média | **out** |
|---|---:|---:|---:|---:|---:|---:|
| Mercado exclusivos | 143 | 141 | 135 | 171 | 147,5 | **87 (−41%)** |
| … em lote (3+ da mesma marca no dia) | 34 | 51 | 50 | 63 | 49,5 | **17 (−66%)** |
| … avulsos | 109 | 90 | 85 | 108 | 98 | **70 (−29%)** |
| Mercado não exclusivos | 143 | 165 | 147 | 219 | 168,5 | 185 (+10%) |
| Mercado sem talento | 4 | 3 | 10 | 7 | 6 | **32** |
| Mercado total | 290 | 309 | 292 | 397 | 322 | 304 (−6%) |

Causa, com os dados: (1) **o total do Mercado está quase normal** (−6% no mesmo ponto do mês); o que mudou foi a
**mistura** — a parcela exclusiva até o dia 25 caiu de ~46% para **29%**; (2) **lotes**: pedidos de exclusivos em lote
(campanhas com vários talentos de uma marca no mesmo dia: Veja, Nestlé, NexGard, Sesc… em jun–set) quase sumiram
(17 contra 50) — explicam ~55% da queda; (3) **avulsos** também caíram (70 contra 98), espalhado entre os talentos
mais pedidos: Ticiane Pinheiro 13,5 → 2, Juliette Freire 10,5 → 4, Milena Moreira Lages 7,8 → 2, Tadeu Schmidt 7 → 2,
Tatiana Machado 9,5 → 5 (média até o dia 25 em jun–set → outubro); Beatriz Reis (11 → 11), Gilberto Nogueira (9 → 8)
e Ana Paula Renault (6 → 6) ficaram estáveis; (4) **32 pedidos ainda sem talento** (5× o normal): curadorias em
andamento criadas em lote ("Talento 1/2/3": Mercado Pago 6, Travelex 6, Serasa 6, Makita 5) — quando o talento for
preenchido, parte pode virar exclusiva e reduzir a distância; (5) **mudança de exclusividade** é pequena: Viviane
Araújo (8 pedidos exclusivos em jun–set) aparece com 3 não exclusivos em outubro; (6) **sazonalidade de 2025 não
explica**: na silver 2025 (fonte fraca) outubro/25 teve 125 exclusivos contra 56 em setembro/25 — não há queda de
outubro no ano anterior.

**A série própria não corrige.** A previsão de outubro com a série própria é 196 (faixa 158–214) contra 214 da
repartição da D48 (464 × 0,462); com a extensão de 2025, 193 a 212 em todos os modelos. Nenhum modelo vê a queda: a
série vinha subindo até 194 em setembro. No ritmo atual (87 em 16 de 21 dias úteis), outubro fecharia perto de **114**,
mais uma parte dos 32 sem talento — bem abaixo da faixa. Isso entra no registro PD09 como o primeiro erro fora da
amostra. Consulta por talento usada (só SELECT): o bloco `pedidos` de 5.0.2 com `WHERE tipo_de_input = 'Mercado' AND
exclusivo AND EXTRACT(DAY FROM dia) <= 25`, contando por `talento` e mês.

### 5.0.8 Sensibilidade: estender a exclusividade com a silver 2025 (fonte fraca) — avaliada e NÃO usada

A silver 2025 (`slv_agenciamento_2025_itens`) não tem `exclusivo` nem `talento`; o único sinal é a coluna
`talentos_exclusivos` (nome do talento exclusivo, preenchida ou não). Avaliação (BigQuery, 26/10/2026):

| Critério | Resultado |
|---|---|
| Totais por mês × gold (com a data estimada R2) | iguais de fev a nov/2025; jan −4 (Inbound 73 × 77) e −2 (Mercado), dez Mercado 99 × 105 |
| Mesmo sinal em 2026 | `talentos_exclusivos` preenchido × `exclusivo` da silver 2026: Mercado 1.321 de 1.321 exclusivos com o campo; 14 não exclusivos com o campo (concordância de ~99%) |
| Separa "sem talento" | **não**: em 2025, "não exclusivo" inclui os sem talento (~3% do Mercado em 2026) |
| Preenchimento (Inbound, que é todo exclusivo) | 2025: 89,5% (abr 83%, mai 77%, ago 77%); 2026: 92,7% |
| Itens nos dois anos (para cruzar) | nenhum (`item_id_legado`/`item_id_atual` × `item_id`) |
| Datas estimadas (R2) | 17–25% dos meses de 2025, como na gold (PD10) |

Rodada completa (`python -m ml.rodar --sensibilidade` → `ml/saida/sensibilidade_2025.json`, os 61 modelos nas duas
séries estendidas, 21 meses): **Mercado exclusivos** — vence `arimax_100_ct_fimdeano` (9,9%, exploratório), que prevê
212 · 95 · 104 (a queda de nov/dez vem dos meses fracos de 2025 do próprio sinal fraco); a combinação de 6 piora para
12,8% (contra 10,9% só com 2026); **Mercado não exclusivos** — Prophet (log) 18,5% (19,2% só com 2026). Nenhum modelo
corrige outubro (193–212). **Decisão:** a extensão não melhora o erro dos modelos simples, traz um vencedor
exploratório e mistura dois critérios de exclusividade; fica **fora da tela**. A série oficial é só 2026, com "confiança
menor". Revisar quando houver a exclusividade na gold de entradas (PD01) ou um ano inteiro de 2026.

### 5.0.9 Mercado total: reavaliação e recomendação (item 2 da D56)

Pela regra D48 o vencedor é a rede de 1 neurônio (12,6%), mas ela **não é robusta**: perde da ingênua em jan–mai
(26,8% × 24,7%; 27º de 57). Onze modelos batem a ingênua nos dois períodos; o de menor erro no teste é o Prophet (log)
16,3% / 20,9%, empatado (< 1 ponto) com o **ARIMA com tendência** `arima_100_ct` (16,5% / 20,4%), que fica por ser o
mais simples (C5: `robustez.alternativa`). Previsões do ARIMA: **515 · 570 · 635** (faixa 385–690, 418–777, 465–868).
Outubro corre a ~360–400 (304 até 25/10; no ritmo de dias úteis, 399; pela proporção típica até o dia 25, ~360):
**as duas previsões estão altas**, e o ARIMA mais (515 × 464).

**Recomendação:** manter a rede na tela desta reunião (é a regra D48 aprovada), **com o selo "não robusto"** já
visível, e apresentar nov/dez do Mercado como cenário; decidir a regra C5 (exigir que o vencedor bata a ingênua também
fora do teste) com o fechamento de outubro, que é o primeiro ponto fora da amostra (PD09). Trocar agora pelo ARIMA
pioraria outubro e não teria mais base que 5 meses de verificação.

### 5.0.10 Limites (D56)

- Séries de exclusividade com 9 meses: só 9 modelos simples se aplicam, sem verificação e com faixa de 6 razões
  internas; os erros (10,9% e 19,2%) são de 4 meses escolhidos entre 9 modelos (menos otimista que entre 57, mas pouco).
- Os recortes não somam o total (sem talento fica fora; modelos independentes). Mercado exclusivos + não exclusivos de
  outubro previstos = 440 × 464 do total.
- O realizado do mês vigente nos recortes muda quando o talento é preenchido (32 sem talento em outubro).
- O "esperado até agora" supõe pedidos proporcionais aos dias úteis; até o dia 25, os meses de jun–set tiveram 76% a
  91% do mês (16/21 = 76%).
- PD09: o histórico (`historico_previsoes.jsonl`) ganhou a linha do retrato de setembro no protocolo D56 (`substitui`:
  D48), sem apagar a da D48.

## 5. Decisão D48 e memória de cálculo (retrato de setembro, carga de 23/10/2026) — histórico

As séries do Inbound e do Mercado (total) seguem iguais na D56; os filtros (5.2–5.3, repartição) foram substituídos pela
seção 5.0.

### 5.1 Vencedores (C1)

| Série | Vencedor | Erro no teste h1 jun–set (MAE) | h2 · h3 · h1–h3 | Verificação jan–mai | Ingênua (último mês): teste · verificação | Empatados (< 1 ponto) |
|---|---|---|---|---|---|---|
| Inbound | `ref_media_6m` (média dos últimos 6 meses) | **14,4%** (≈ 20 pedidos/mês), viés −9,6% | 17,5 · 22,3 · 18,1% | 26,9% | 26,0% · 47,0% | `arimax_011` 13,5% (menor), `arimax_110` 14,2%, `comb_selecao` 14,3% → fica a referência |
| Mercado | `mlp_1` (rede neural, 1 neurônio) | **12,6%** (≈ 49 pedidos/mês), viés +7,4% | 8,5 · 24,7 · 15,3% | 26,8% | 19,8% · 24,7% | as 11 variantes da rede (12,6–13,0%) → fica a de 1 neurônio |

Previsto no teste (h1) × real:

| Mês | Inbound previsto (faixa) | Inbound real | Mercado previsto (faixa) | Mercado real |
|---|---|---:|---|---:|
| jun/26 | 114 (81–186) | 112 | 372 (390–728) | 339 |
| jul/26 | 124 (118–203) | 165 | 411 (381–678) | 404 |
| ago/26 | 130 (124–212) | 156 | 437 (426–619) | 322 |
| set/26 | 141 (138–231) | 129 | 437 (309–442) | 477 |

Conta do Inbound à mão: |114−112| + |124−165| + |130−156| + |141−129| = 2 + 41 + 26 + 12 = 81 ÷ (112+165+156+129 = 562) = 14,4%.
Faixas empíricas (erros do próprio passado) podem não conter o ponto quando o passado errou para um lado.

### 5.2 Números da tela (retrato de setembro)

| Filtro | Inbound out · nov · dez (faixa) | Mercado out · nov · dez (faixa) | Erro no teste I / M (abordagem) |
|---|---|---|---|
| Todos | 138 (131–212) · 138 (146–219) · 138 (147–221); em andamento: 128 até 22/10 | 464 (334–483) · 517 (372–538) · 588 (423–612); em andamento: 275 até 22/10 | 14,4% / 12,6% (vencedor do tipo) |
| Exclusivos | 129 (122–198) · 129 (137–204) · 129 (137–206); em andamento: 107 | 214 (154–223) · 239 (172–248) · 272 (195–283); em andamento: 77 | 14,8% (repartir, todos os meses) / 11,3% (repartir, empate com direto 10,9%) |
| Não exclusivos | **sem número** — "Poucos pedidos para prever com confiança (8 por mês no teste)"; erro 68,7% | 242 (174–252) · 269 (194–280) · 306 (221–319); em andamento: 161 | 68,7% (direto, Theta) / 20,0% (repartir, empate com direto 19,2%) |

Parcelas do futuro (a_todos, jan–set/2026, silver): Inbound exclusivos 1.115 ÷ 1.194 = 0,934; Mercado exclusivos 1.233 ÷
2.670 = 0,462, não exclusivos 1.391 ÷ 2.670 = 0,521 (46 sem talento). Outubro dos grupos: Mercado tem 37 pedidos ainda sem
talento informado.

### 5.3 Filtros: repartir × prever direto (WAPE h1 jun–set)

| Tipo · filtro | Repartir (melhor) | Direto (melhor) | Escolhida | Média no teste |
|---|---|---|---|---:|
| Inbound · exclusivos | 14,8% (todos os meses) | 16,2% (`comb_ses`) | repartir | 133 |
| Inbound · não exclusivos | 80,3% | 68,7% (`comb_theta`) | direto — **sem número** (poucos e erro > 40%) | 8 |
| Mercado · exclusivos | 11,3% | 10,9% (`comb_mediana`) | repartir (empate) | 178 |
| Mercado · não exclusivos | 20,0% | 19,2% (`comb_holt_amort`) | repartir (empate) | 200 |

**Correção feita na mesma data:** a 1ª lista da (b) incluía `arima_100_ct`, `arima_011_t`, `cls_holt_amortecido`,
`cls_ets_aicc` e `cls_theta`, que estimam 3 a 5 parâmetros por máxima verossimilhança em 5 a 8 pontos (a regra do projeto,
`ml/modelos/classico.py`, é nº de parâmetros ≤ n/4). O `arima_100_ct` venceu o Mercado não exclusivo com **10,8%** contra
19% do 2º colocado — sinal de sorte no teste. Os cinco continuam rodando e registrados em `filtros.json` ("excluidos"),
mas não são elegíveis.

### 5.4 Modelo contra modelo (WAPE %, teste h1 · h1–h3 · verificação jan–mai)

| Modelo | Inbound | Mercado |
|---|---|---|
| `ref_ultimo_mes` (ingênua) | 26,0 · 22,0 · 47,0 | 19,8 · 21,4 · 24,7 |
| `ref_media_3m` | 15,4 · 14,8 · 29,9 | 21,4 · 27,6 · 32,4 |
| `ref_media_6m` | **14,4** · 18,1 · 26,9 | 31,6 · 40,0 · 30,0 |
| `ref_tendencia_6m` | 23,0 · 20,1 · 31,7 | 14,2 · 16,2 · 33,6 |
| `cls_holt_amortecido` | 16,3 · 20,7 · 29,5 | 17,5 · 22,6 · 27,8 |
| `arima_100_ct` | 16,5 · 20,8 · 37,0 | 16,5 · 15,9 · **20,4** |
| `arimax_100_ct` | 15,1 · 20,2 · 26,7 | 40,4 · 64,1 · 47,9 |
| `arimax_011` | 13,5 · 11,2 · 27,4 | 39,2 · 32,0 · 60,0 |
| `prophet_auto` | 23,3 · 18,0 · 32,4 | 21,6 · 18,3 · 28,6 |
| `prophet_log_sem_sazonal` | 17,1 · 20,3 · 33,3 | 16,3 · 17,2 · 20,9 |
| `boost_lgbm` | 28,0 · 16,6 · 30,6 | 20,9 · 21,7 · 33,6 |
| `mlp_1` | 26,8 · 29,5 · 30,3 | **12,6** · 15,3 · 26,8 |
| `mlp_auto` | 26,9 · 29,4 · 30,6 | 12,8 · 15,2 · 26,8 |
| `comb_mediana` | 18,0 · 18,5 · 34,0 | 19,0 · 20,9 · 23,8 |
| `comb_theta` | 15,1 · 16,8 · 31,3 | 19,0 · 19,8 · 23,0 |
| `comb_drift_log` (exploratório) | 19,7 · 18,7 · 33,2 | 13,9 · 17,5 · 25,4 |

Não se aplicam (4): `prophet_log`, `prophet_natural`, `prophet_log_degrau2026`, `comb_sazonal`. Nenhuma falha.
ARIMAX × ARIMA (mesma ordem, h1 jun–set, Inbound / Mercado): nível e reta 15,1 × 16,5 / 40,4 × 16,5; (1,1,0) 14,2 × 16,4 /
20,3 × 22,8; (0,1,1) 13,5 × 18,6 / 39,2 × 29,6; (0,1,1) com deriva 36,5 × 22,9 / 29,8 × 34,5 — com 12 meses as exógenas
ajudam o Inbound em 3 de 4 pares e pioram muito o Mercado em 2 (instáveis). Rede neural: de 1 a 16 neurônios o erro muda
menos de 1 ponto (Inbound 26,7–27,4%, Mercado 12,6–13,0%). Tabela completa: `ml/saida/resultados.json` (o painel
"Regras e modelos" saiu da tela na D55).

### 5.5 Avaliação honesta (26/10/2026)

- **Inbound (Todos e Exclusivos): dá para apresentar, com ressalva.** A média de 6 meses erra 14% no teste (≈ 20
  pedidos/mês) contra 26% da ingênua, e também vence a ingênua fora da escolha (27% × 47% em jan–mai). Mas é constante e
  subestima (viés −10% no teste, −24% em jan–mai): a faixa fica acima do número. Outubro: 128 em 15 de 21 dias úteis ≈ 179
  no ritmo atual, acima de 138 e dentro da faixa (131–212).
- **Mercado (Todos): o número de outubro pode ir com ressalva; nov e dez, não como previsão firme.** A rede de 1 neurônio
  vence o teste (12,6% × 19,8% da ingênua), mas na verificação jan–mai erra 26,8% contra 24,7% da ingênua — a vantagem
  não se sustenta fora dos 4 meses de escolha (54 modelos disputando 4 meses). Outubro: 275 em 15/21 dias úteis ≈ 385 no
  ritmo, 17% abaixo dos 464 previstos e abaixo da faixa (334–483 contém 385). Nov 517 e dez 588 prolongam o crescimento,
  mas em 2025 nov e dez caíram 31% e 56% sobre outubro; nenhum modelo de 12 meses aprende isso. O único modelo que bate a
  ingênua nos dois períodos é `arima_100_ct` (16,5% no teste, 20,4% em jan–mai).
- **Filtros:** Mercado exclusivos (11%) e não exclusivos (20%) são apresentáveis pela repartição; Inbound não exclusivo
  (8 pedidos/mês, erro 69%) não — a tela já diz "poucos pedidos para prever com confiança".
- **Proposta para a reunião:** mostrar a tela como acompanhamento real × previsto (o teste jun–set e outubro em andamento)
  e o fechamento de outubro; apresentar nov/dez do Mercado só como "se o crescimento continuar", lembrando a queda de fim
  de ano de 2025. Decisões pendentes do Caio na seção 8.

### 5.6 D55 — Comparação automática com o AutoTS (26/10/2026, carga de 26/10 09:01, dados até 25/10)

**Por que AutoTS.** O Caio pediu uma biblioteca que "treina todos os modelos e devolve o melhor" (pensava no PyCaret, que
exige Python ≤ 3.11; o venv é 3.12). Instalado `autots==1.0.4` (só ele; pandas/numpy não mudaram; `requirements-ml.txt`).

**Como rodou (`ml/modelos/automatico.py`, AT1–AT7).** Dentro da régua D48: em cada origem (jan–set/2026 e o futuro) o
AutoTS recebe **só os 12 meses anteriores** e procura, para **1 mês à frente**, entre 19 famílias univariadas (ingênuos,
GLM, GLS, ETS, ARIMA, componentes não observados, Kalman, Theta, ARDL, regressão linear, motivos, FFT, regressão por
janela e por data), cada uma com várias combinações de parâmetros e transformações. Escolha interna por MAE numa
validação para trás dentro da janela (3 recortes de 1 mês; os 35% melhores revalidados). `autots_1`, `autots_2` e
`autots_3` = o 1º, 2º e 3º colocados (um por família) **de cada janela** — a escolha automática refeita todo mês, como a
`mlp_auto`. Sementes fixas, `n_jobs = 1`, sem gerações genéticas (na 1.0.4 com pandas 3 elas quebram e, remendadas,
davam vencedores diferentes a cada execução) e **cada busca num processo Python novo** (no mesmo processo, repetir a
busca mudava as notas). Duas execuções completas deram **resultados idênticos**. Tempo: ~7 min (20 buscas de 10–30 s).

**Resultado (WAPE h1; teste jun–set = onde se escolhe; verificação jan–mai = fora da escolha).**

| Série | Modelo | Teste jun–set | MAE (pedidos/mês) | Viés | Faixa (cobertura) | Verificação jan–mai | Previsão out · nov · dez |
|---|---|---|---|---|---|---|---|
| Inbound | AutoTS 1º (`autots_1`) | 15,0% | 21,1 | −14,5% | 3 de 4 | 37,9% | 159 · 162 · 165 |
| Inbound | AutoTS 2º (`autots_2`) | 25,6% | 36,0 | −11,3% | 2 de 4 | 27,1% | 159 · 165 · 171 |
| Inbound | AutoTS 3º (`autots_3`) | 16,3% | 22,9 | −0,2% | 4 de 4 | 31,6% | 158 · 163 · 169 |
| Inbound | Rede neural 1 neurônio (`mlp_1`) | 26,8% | 37,6 | +26,8% | 3 de 4 | 30,3% | 179 · 185 · 224 |
| Inbound | Rede neural, tamanho no treino (`mlp_auto`) | 26,9% | 37,8 | +26,9% | 3 de 4 | 30,6% | — |
| Inbound | Repetir o último mês (`ref_ultimo_mes`) | 26,0% | 36,5 | +7,1% | 3 de 4 | 47,0% | 129 · 129 · 129 |
| Inbound | Média de 3 meses (`ref_media_3m`) | 15,4% | 21,6 | −0,9% | 4 de 4 | 29,9% | — |
| Inbound | **Média de 6 meses (`ref_media_6m`) — vencedor** | **14,4%** | 20,3 | −9,6% | 3 de 4 | **26,9%** | **138 · 138 · 138** |
| Mercado | AutoTS 1º (`autots_1`) | 29,5% | 113,8 | −6,2% | 2 de 4 | 31,3% | **0 · 0 · 0** (ARIMA degenerado no futuro) |
| Mercado | AutoTS 2º (`autots_2`) | 29,3% | 112,9 | +0,8% | 1 de 4 | 25,5% | 327 · 327 · 327 |
| Mercado | AutoTS 3º (`autots_3`) | 26,7% | 102,8 | −12,2% | 0 de 4 | 33,2% | 439 · 465 · 492 |
| Mercado | **Rede neural 1 neurônio (`mlp_1`) — vencedor** | **12,6%** | 48,7 | +7,4% | 1 de 4 | 26,8% | **464 · 517 · 588** |
| Mercado | Rede neural, tamanho no treino (`mlp_auto`) | 12,8% | 49,2 | +7,4% | 1 de 4 | 26,8% | — |
| Mercado | Repetir o último mês (`ref_ultimo_mes`) | 19,8% | 76,2 | −9,1% | 2 de 4 | 24,7% | 477 · 477 · 477 |
| Mercado | Média de 3 meses (`ref_media_3m`) | 21,4% | 82,4 | −16,5% | 4 de 4 | 32,4% | — |
| Mercado | Média de 6 meses (`ref_media_6m`) | 31,6% | 121,9 | −31,6% | 3 de 4 | 30,0% | 351 · 351 · 351 |

O que o AutoTS escolheu em cada janela (treino até → previsão de): **Inbound** 1º: mai→jun LastValueNaive, jun→jul
LastValueNaive, jul→ago LastValueNaive, ago→set WindowRegression, set→out–dez Theta; 2º: SeasonalNaive, SeasonalNaive,
UnobservedComponents, DatepartRegression → UnobservedComponents; 3º: FFT, WindowRegression, ETS, UnobservedComponents →
ETS. **Mercado** 1º: ETS, Theta, DatepartRegression, ARIMA → ARIMA; 2º: UnobservedComponents, ARIMA, KalmanStateSpace,
ConstantNaive → LastValueNaive; 3º: LastValueNaive, ConstantNaive, AverageValueNaive, FFT → ETS. Lista completa (com as
transformações e jan–mai) em `ml/saida/previsao.json`, bloco `comparacao_automatica`.

**Vencedores e por quê (regra D48).** Inbound: o menor erro no teste é `arimax_011` (13,5%); `arimax_110` (14,2%),
`comb_selecao` (14,3%) e a **média de 6 meses (14,4%)** empatam com ele (< 1 ponto) e fica a mais simples, a média de 6
meses. O melhor AutoTS (15,0%) fica 1,5 ponto atrás do menor erro: não empata e não vence (5º de 57 no teste). Mercado: a
rede neural (12,6–13,0% nas 11 variantes) fica 14 pontos à frente do melhor AutoTS (26,7%; 45º de 57); fica a de **1
neurônio** (a mais simples do empate). Previsões e erro da tela não mudaram.

**É robusto?** Inbound: **sim, com ressalva** — a média de 6 meses também é a melhor das linhas acima fora da escolha
(26,9% em jan–mai, 5º de 57 modelos) e bate a ingênua nos dois períodos; segue constante e abaixo do real (viés −10%). O
AutoTS 1º, que quase empatou no teste, piora muito em jan–mai (37,9%): sinal de sorte nos 4 meses. Mercado: **não** — a
rede neural vence o teste com folga, mas em jan–mai erra 26,8% contra 24,7% da ingênua e 25,5% do AutoTS 2º (27º de 57
modelos na verificação); nenhum candidato domina os dois períodos. O AutoTS não resolve: com 12 meses, a validação
interna dele tem 3 recortes de 1 mês, e ele troca de família quase todo mês (mesmo problema de escolher com pouco dado).
No Mercado, o 1º colocado chegou a prever **0** para out–dez (ARIMA com transformações escolhido na janela out/25–set/26):
mais uma razão para não usar a escolha automática sem a régua.

### 5.7 D55 — Inbound marcado como talento não exclusivo (qualidade, PD24)

Regra do Caio: todo Inbound é de talento exclusivo; o que aparece como não exclusivo é **erro de preenchimento**. Contagem
na silver 2026 (`ml/dados/exclusividade.csv`, mesmo critério de `app/sql/talentos_ano.sql`; carga de 26/10/2026 09:01,
dados até 25/10):

| Mês (2026) | jan | fev | mar | abr | mai | jun | jul | ago | set | out (até 25/10) |
|---|---|---|---|---|---|---|---|---|---|---|
| Inbound marcado não exclusivo | 7 | 11 | 5 | 6 | 19 | 12 | 14 | 3 | 1 | 19 |
| Inbound no mês | 132 | 88 | 144 | 99 | 169 | 112 | 165 | 156 | 129 | 133 |

Jan–set: **78 de 1.194 (6,5%)**, em todos os 9 meses; outubro já tem 19 de 133. Efeito na Previsão: o filtro
"Exclusivos" do Inbound usa o Inbound inteiro (138 · 138 · 138, erro 14,4%), e não a repartição de antes (129/mês); o
"Não exclusivos" do Inbound deixa de existir na tela. Registrado em `pendencias.py` (PD24), em
`docs/lembretes_gold.md` e no bloco `qualidade` do `previsao.json`. SQL para listar os casos: o bloco `pedidos` de
`app/sql/talentos_ano.sql` com `WHERE p.tipo_de_input = 'Inbound' AND p.exclusivo = FALSE` (só SELECT).

## 6. Como reproduzir

**D56:** o SQL completo de cada uma das 4 séries, com o resultado esperado, está na seção 5.0.2 (S1–S6). Rodar:
`python -m ml.dados` (snapshot e CSVs por série, só SELECT), `python -m ml.rodar --modulo <m> --sem-juntar` (os 8
módulos em paralelo, ~10 min o mais lento), `python -m ml.rodar --juntar` (resultados.json, previsao.json, retrato e
histórico), `python -m ml.rodar --sensibilidade` (silver 2025, ~15 min) ou tudo de uma vez com `python -m ml.rodar --rotina --forcar`.

(Histórico, D48) Série mensal (a mesma de `ml/dados.py`, `SQL_SERIE` — hoje com o fim E3; esperado: as colunas "real" acima e, em out/26, Inbound 128 e Mercado
275 na carga de 23/10):

```sql
WITH fim AS (SELECT MAX(data) AS dados_ate, MAX(_processado_em) AS processado_em
             FROM `gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_entrada_diaria`)
SELECT FORMAT_DATE('%Y-%m', DATE_TRUNC(e.data, MONTH)) AS mes, e.tipo_de_input AS tipo,
       SUM(e.quantidade + e.quantidade_estimada) AS pedidos, SUM(e.quantidade_estimada) AS estimados,
       LAST_DAY(MIN(e.data)) <= ANY_VALUE(f.dados_ate) AS completo
FROM `gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_entrada_diaria` e CROSS JOIN fim f
WHERE e.tipo_de_input IN ('Inbound', 'Mercado') AND e.data >= '2024-10-01'
GROUP BY mes, tipo ORDER BY tipo, mes;
```

Média de 6 meses à mão (Inbound): futuro = abr–set/2026 = (99 + 169 + 112 + 165 + 156 + 129) ÷ 6 = 830 ÷ 6 = 138,3;
teste de jun = os 6 últimos meses da janela jun/25–mai/26 = dez/25–mai/26 = (50 + 132 + 88 + 144 + 99 + 169) ÷ 6 = 113,7.

Exclusividade por mês e tipo: o bloco `pedidos` de `app/sql/talentos_ano.sql` com a coluna `i.tipo_de_input` e a
agregação `COUNTIF(p.exclusivo)`, `COUNTIF(NOT p.exclusivo)`, `COUNTIF(p.exclusivo IS NULL)`, `COUNT(*)` por mês e tipo,
de 1º/jan/2026 até `dados_ate` (`ml/dados.py::_sql_exclusividade`). Esperado jan–set/2026: Inbound 1.115 / 78 / 1 de
1.194; Mercado 1.233 / 1.391 / 46 de 2.670.

Rodar: `python -m ml.rodar --rotina --sem-extrair --forcar` (retrato completo, ~9 min) ou módulos em paralelo
(`python -m ml.rodar --modulo neural --sem-juntar` …) e depois `python -m ml.rodar --juntar`; `python -m ml.previsao`
só refaz o contrato; `python -m ml.rodar --acompanhamento --sem-extrair` só o mês em andamento.

## 7. Validações feitas

| Data | O quê | Resultado |
|---|---|---|
| 25/10/2026 | Snapshot congelado (BigQuery, só SELECT) | carga 23/10 20:23 UTC, dados até 22/10 |
| 26/10/2026 | Snapshot refeito pela rotina disparada pela página (só SELECT) | mesma carga e mesmos números |
| 26/10/2026 | 58 modelos re-rodados no protocolo D48 (5 módulos em paralelo + rotina completa) | 54 com resultado, 4 não se aplicam, 0 falhas; rodadas determinísticas (mesmos números) |
| 26/10/2026 | Teste de vazamento: cada fit recebe exatamente os 12 meses anteriores à origem (`test_janela_de_12_meses_sem_vazamento`); parcela só com meses anteriores (`test_reparticao_so_com_meses_anteriores_a_origem`); conta do WAPE do Inbound à mão (5.1) | ok |
| 26/10/2026 | Capturas 1920×1000, 1440×900, 1280×800 (3 filtros, painel aberto) e 390 px | lâmina sem rolar no desktop; 390 px sem rolagem lateral (corrigido: tabela do leitor e tabela de modelos esticavam a lâmina para 581 px) |
| 26/10/2026 | `pytest tests` | 345 passando |
| 26/10/2026 | D55: rotina mensal completa (`--rotina --forcar`, snapshot novo só com SELECT: carga 26/10 12:01 UTC, dados até 25/10) com os 61 modelos | 57 com resultado, 4 não se aplicam, 0 falhas; vencedores e números iguais ao retrato anterior |
| 26/10/2026 | D55: AutoTS rodado duas vezes (processos separados) | séries, futuro e escolhas idênticos |
| 26/10/2026 | D55: vazamento do AutoTS com busca falsa (`tests/test_ml_automatico.py`): cada busca recebe exatamente os 12 meses anteriores à origem | ok |
| 26/10/2026 | D55: capturas 1850×1030, 1440×900, 1280×800 e 390 px nos 3 filtros (servidor temporário, depois gravado) | sem rolagem lateral; lâmina sem rolar no desktop; texto do SVG ≥ 11 px; sem erro no console |
| 26/10/2026 | D55: `pytest tests` | 459 passando |
| 26/10/2026 | D56: snapshot por série (BigQuery, só SELECT, `caio.barroso@viu.com.br`, `gglobo-viu-dados-hdg-prd`): carga 26/10 12:01 UTC, dados até 25/10 | S1–S4 iguais ao `exclusividade.csv`/`serie_mensal.csv`; SQL literal da 5.0.2 refeito no BigQuery: mesmas contagens (S3/S4 e S6) |
| 26/10/2026 | D56: 61 modelos × 4 séries (8 módulos em paralelo na cópia, depois `--juntar`) | Inbound e Mercado idênticos à D55; séries curtas: 9 modelos se aplicam, 52 não (R7), 0 falhas |
| 26/10/2026 | D56: silver 2025 avaliada (totais × gold, sinal × 2026, preenchimento) e sensibilidade com os 61 modelos | não usada (5.0.8) |
| 26/10/2026 | D56: outubro do Mercado exclusivos investigado no BigQuery (lotes, talentos, sem talento, mudança de exclusividade, 2025) | seção 5.0.7 |
| 26/10/2026 | D56: capturas 1920×1000, 1850×1030, 1440×900 e 1280×800 nos 3 filtros, diálogo aberto (1440 e 390) e 390 px (servidor temporário na cópia, porta 8131) | lâmina sem rolar no desktop; 390 px sem rolagem lateral; texto do SVG ≥ 16 px reais; foco no botão Fechar ao abrir o diálogo; sem erro de console da página (o erro `colocar … clientWidth` no celular é anterior e de todas as páginas, ver 8) |
| 26/10/2026 | D56: `pytest tests` | 463 passando |

## 8. Limites e pendências

- **D56:** limites das séries curtas, dos recortes que não somam o total e do "esperado até agora" na seção 5.0.10;
  decisão aberta do Mercado total (C5) na 5.0.9; a silver 2025 só volta com a exclusividade na gold (PD01).
- **Achado (não corrigido, fora do escopo):** no celular, `apresentacao.js` (`colocar`, linha ~134) lança
  `Cannot read properties of null (reading 'clientWidth')` em todas as páginas com o navegador das seções escondido;
  a página continua funcionando (a entrada do slide já foi marcada), mas o resto de `exibir()` não roda.

- D55: o vencedor do Mercado não é robusto (perde da ingênua em jan–mai); o AutoTS não trouxe candidato melhor. A
  decisão aberta segue (PRD 9.7).
- D55: o histórico PD09 (`historico_previsoes.jsonl`) guarda uma linha por retrato e não foi reescrito; como os
  vencedores e os números do retrato de setembro não mudaram, a linha de setembro continua valendo (o filtro Inbound
  exclusivos dela ainda é a repartição antiga, 129/mês).
- D55: Inbound não exclusivo é erro de cadastro (PD24): enquanto não for corrigido na origem, a Previsão o conta como
  exclusivo.
- Escolha no próprio teste (4 meses, 54 modelos): erro do vencedor otimista (ver verificação). Com 4 meses, poucos pontos
  de diferença podem ser sorte.
- Com 12 meses não há sazonalidade anual: nov/dez seguem a tendência recente (2025: Inbound nov −41% e dez −59% sobre out;
  Mercado −31% e −56%; 2025 tem 17–25% de datas estimadas, PD10).
- Faixas empíricas (média 6m, rede) com ~6 origens internas: Inbound com a faixa acima do número; cobertura do Mercado no
  teste 25% (1 de 4).
- Filtros: a parcela não entra na faixa; no mês em andamento parte dos pedidos ainda está sem talento.
- **Para o Caio decidir:** (1) manter o critério puro no Mercado (rede neural) ou exigir que o vencedor também bata a
  ingênua na verificação jan–mai (ficaria `arima_100_ct`); (2) mostrar nov/dez do Mercado como previsão ou como cenário;
  (3) PD09 passa a medir o acerto fora da amostra a cada retrato (out/26 é o 1º).

## 9. Como o job roda

**No computador (pronto):** o servidor dispara sozinho (J1–J4). Manual: `python -m ml.rodar --rotina` (precisa das
credenciais ADC de `gcloud-viu`, como o site). Requer `pip install -r requirements.txt -r requirements-ml.txt` no venv.

**Em produção (Cloud Run) — a fazer, comandos para o Caio, nada executado.** O site em produção não tem a pasta `ml/`
nem as bibliotecas (o `Dockerfile` só copia `app/`), então mostra a máscara até existir um job separado que entregue o
`previsao.json`. Desenho proposto (D48: o job pesado é **mensal**; o acompanhamento, diário e leve):

1. Imagem do job: um `Dockerfile.ml` (a criar) com `requirements.txt` + `requirements-ml.txt`, `app/` e `ml/`, comando
   `python -m ml.rodar --rotina` (ela mesma decide: retrato novo no 1º dia útil com o mês fechado; senão, só o
   acompanhamento, em segundos).
2. Saída num bucket: o job grava `previsao.json` em `gs://<bucket>/previsao/previsao.json`; o site passa a ler de lá
   (mudança de código pendente: hoje `PREVISAO_ARQ` é um caminho local).
3. Comandos (Caio, um bloco por vez, conferindo a saída):

```powershell
gcloud config set account caio.barroso@viu.com.br
gcloud config set project gglobo-viu-dados-hdg-prd
# bucket só para o resultado (região do site)
gcloud storage buckets create gs://<bucket> --location=<regiao> --uniform-bucket-level-access
# imagem do job (Artifact Registry do projeto)
gcloud builds submit --config cloudbuild-ml.yaml .
# job: mesma conta de serviço do site, só leitura no BigQuery + escrita no bucket
gcloud run jobs create previsao-agenciamento --image <regiao>-docker.pkg.dev/gglobo-viu-dados-hdg-prd/<repo>/previsao-ml:1 `
  --region <regiao> --service-account <conta-do-site> --memory 2Gi --cpu 2 --task-timeout 30m --max-retries 1
# disparo depois da gold (seg–sex 09:45): a rotina só refaz os modelos quando o mês fechou
gcloud scheduler jobs create http previsao-agenciamento-diario --location <regiao> --schedule "45 9 * * 1-5" `
  --time-zone "America/Sao_Paulo" --http-method POST `
  --uri "https://run.googleapis.com/v2/projects/gglobo-viu-dados-hdg-prd/locations/<regiao>/jobs/previsao-agenciamento:run" `
  --oauth-service-account-email <conta-do-scheduler>
```

O Cloud Scheduler revisa a D6 ("sem Cloud Scheduler", que era sobre a recarga do site) e precisa de decisão do Caio; a
alternativa é encadear ao job da gold. Custo estimado: ~10 min uma vez por mês + segundos por dia útil, 2 vCPU/2 GiB
(centavos de dólar por mês); reestimar na fase 3 (PRD 7.3).

## 10. Histórico da página

| Data | Mudança |
|---|---|
| 31/10/2026 | **Auditoria do Codex, F03:** o rodapé leva a data própria do acompanhamento ("· acompanhamento até dd/mm") e, quando o retrato (`carga.processado_em`) ou o acompanhamento (`acompanhamento.processado_em`) são de outra carga que a da gold de entradas (a do rodapé; na reunião, a base congelada), um aviso discreto com ícone e texto ("acompanhamento de outra carga (dd/mm/aaaa)"). Nada volta ao topo (pedido do Caio). Regra em `previsao.coerencia`; o `tools/congelar_base.py --conferir` e o build (`python -m app.conferir_base`) reprovam a incoerência. Testes em `tests/test_auditoria_dados.py` |
| 26/10/2026 | **D56** (Caio): uma série e um modelo por recorte (Inbound, Mercado, Mercado exclusivos, Mercado não exclusivos), sem repartição (`ml/filtros.py` saiu); 61 modelos × 4 séries na régua D48 + R7 (janela expansiva e mínimo por modelo nas séries só de 2026); vencedores: média de 6 meses, rede de 1 neurônio (não robusta; alternativa ARIMA com tendência), combinação de 6 e Holt simples; tela com cartões do mês vigente + 2 seguintes, gráfico em cartão flutuante e o diálogo "Modelos comparados"; outubro do Mercado exclusivos explicado (lotes e avulsos); silver 2025 avaliada e não usada; contrato v3; histórico com a linha D56 do retrato de setembro; 463 testes |
| 26/10/2026 | **D55** (Caio): tela só com os dois gráficos largos (nome simples do modelo, previsões, erro médio); saíram "Vale mais que o palpite simples?" e "Regras e modelos" (documentação só na ficha e no PRD); Inbound não exclusivo = "Não se aplica", Inbound exclusivos = Inbound inteiro, casos contados (PD24); AutoTS (`ml/modelos/automatico.py`, 3 colocados por janela) dentro da régua D48 — não venceu (Inbound 15,0% × 14,4%; Mercado 26,7% × 12,6%); rotina completa refeita; 459 testes |
| 26/10/2026 | Batalha 2, 2ª leva (D49, G4-N8): pé do cartão com o erro do teste e o da verificação e a ingênua; painel "Vale mais que o palpite simples?" (3 linhas) no lugar de "Modelo contra modelo"; subtítulo em linguagem simples; filtro de talentos levado entre SLA e Previsão |
| 22/10/2026 | D20: esqueleto com série fictícia, 3 referências, mínimo 25 meses |
| 23/10/2026 | D30: máscara (PD09, PD10) |
| 25–26/10/2026 | D47: laboratório de ML (régua única, 58 modelos em 6 famílias, 3 avaliadores); WAPE h1–h3 jan–set; Inbound = média de 3 meses, Mercado = ARIMA com tendência; dois gráficos, seletor de talentos, modelo contra modelo, "Regras e modelos" e faixa do pé; job a cada carga; registro por carga (PD09). Saída guardada em `ml/saida/d47/` |
| 26/10/2026 | Batalha 2, 1ª leva: corte E3 único (`app/corte.py`) no job e no ML; job travado com CONGELAR/modo apresentação (J5); falha visível (J4); trava também no acompanhamento; contrato do snapshot antes do retrato; CSVs atômicos; projeto e rótulos do config no ML; histórico só com protocolo; "jan/27"; PD22 (virada do ano) e PD23 (job em produção); estado "Pronta · 2 decisões abertas" no "O que falta" |
| 26/10/2026 | **D48** (Caio): janela móvel de 12 meses; teste h1 jun–set/2026; vence o menor erro (empate < 1 ponto = o mais simples; ressalva da escolha no teste); 58 modelos re-rodados (4 não se aplicam); Inbound = média de 6 meses (14,4%), Mercado = rede neural de 1 neurônio (12,6%); filtros revalidados (repartir × prever direto; candidatos com parâmetros demais retirados da b); "poucos pedidos para prever com confiança" no Inbound não exclusivo; execução mensal (retrato + acompanhamento diário leve; histórico por retrato); gráficos só de 2026; faixa do pé retirada; pílulas sem número; "Modelo contra modelo" com "erro médio no teste jun–set (menor é melhor)"; correção de rolagem lateral no celular |
| 26/10/2026 | **Batalha 2, 2ª leva e documentação (D49):** pé do cartão com o erro do teste e o da verificação; painel "Vale mais que o palpite simples?"; subtítulo "o modelo que menos errou no teste"; retrato da carga da reunião no topo (retrato de setembro + acompanhamento de 26/10) com a cobertura medida da faixa; decisões abertas no PRD 9.7 |
| 27/10/2026 | **D57:** `ml/dados.py` lê as golds `gld_agenciamento_previsao_mensal`, `..._2026_previsao_exclusividade_mensal` e `..._2026_previsao_lotes` (antes gold de entradas + silver 2026); só a sensibilidade de 2025 segue na silver 2025; 1 pedido do Mercado exclusivos muda de abril para março (calendário completo) |
