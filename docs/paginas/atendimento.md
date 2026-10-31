# Ficha — Atendimento

## 000. D58b — % = Entregues no Mês ÷ Para atender; faixa só com o % de cada número (27/10/2026, tarde)

> **Vigente.** Revisão do Caio no mesmo dia da D58 (seção 00): os rótulos da D58 continuam; a conta do % (A29) e o selo
> do topo mudam. Carga de 27/10/2026 11:09, dados até **26/10/2026**.

| Elemento | D58 (manhã) | **D58b (vigente)** | Valor (carga de 27/10) |
|---|---|---|---|
| Linha % do quadro, pontos da dispersão | A29: entregues ÷ (para atender − declinados) | **A30: Entregues no Mês (entregues ao cliente + declinados) ÷ Para atender** (meio para cima, C8) | **77 · 80 · 76 · 78 · 81 · 80 · 87 · 87 · 79 · 78%** (out parcial). Ex.: set = 661 ÷ 834 = 79,3% → 79% |
| Dica de cada % ("A conta de …") | para atender − declinados | Entregues ao cliente + Declinados (com os status) = Entregues no Mês ÷ Para atender = Entregamos % | set: 515 + 146 = 661 ÷ 834 = 79% |
| Dispersão | x = entregues + ficou, y = entregues | **x = para atender, y = entregues no mês**; mesmo desenho (equilíbrio 100%, alerta 90%) | todos os meses < 90% |
| Selo do topo ("% do que dependia da equipe") | 96% | **Saiu da tela** (confundia com o % de cada número); o valor fica calculado em `pct_dependia` = (entregues + declinados) ÷ recebidos | 5.434 ÷ 5.598 = 97% (fora da tela) |
| Faixa do topo | % dos recebidos + selo | **Só o % de cada número sobre os recebidos** (A15b) | 4.453 **80%** · 981 **17%** · 164 **3%** de 5.598 (somam 100%) |
| Rótulo do "%" (leitor de tela) e título da dica | "… da demanda que dependia da equipe" | "Percentual entregue no mês do que havia para atender" / "Quanto entregamos do que havia para atender" | — |

**Leitura:** o % mede quanto do que havia para atender saiu da fila no mês, entregue ao cliente ou declinado. Os
declinados contam como resolvidos (decisão do Caio); a parte entregue ao cliente está na linha "Entregues ao cliente".

**SQL para reproduzir (só leitura):**

```sql
SELECT FORMAT_DATE('%Y-%m', mes) AS mes, respondidos AS entregues_no_mes, respondidos + ficou AS para_atender,
  CAST(FLOOR(100 * respondidos / (respondidos + ficou) + 0.5) AS INT64) AS pct
FROM `gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_atendimento_mensal`
WHERE mes >= '2026-01-01' ORDER BY mes
```

Resultado em 27/10/2026: os 10 meses batem com a tela. Testes: `tests/test_atendimento_d53.py`
(`test_pct_independe_do_status`, selo fora da página), `tests/test_portal.py`; 475 passaram.

## 00. D58 — "Declinados", "Entregues no Mês" e o % sem os declinados (27/10/2026)

> **Rótulos e % da faixa vigentes; a conta do % (A29) e o selo foram trocados pela D58b (seção 000).** Pedido do Caio em 27/10/2026. Carga de 27/10/2026 11:09 (gold), dados até **26/10/2026**. Substitui, na
> tela, a A27 (seção 0): o resto da D53 continua valendo.

| Elemento | Antes | Agora (regra) | Valor (carga de 27/10) |
|---|---|---|---|
| Linha do quadro e item da faixa do topo | "Saíram sem entrega" | **"Declinados (Não teve seguimento)"**; dicas "Declinados em …, por status" (grupos "Decisão interna" / "Decisão externa") | 46 · 74 · 95 · 89 · 111 · 97 · 116 · 96 · 146 · 111; ano **981** |
| Subtotal da SAÍDA | "Saiu no mês" | **"Entregues no Mês"** (= entregues ao cliente + declinados; nome pedido pelo Caio) | 287 · 343 · 433 · 475 · 615 · 576 · 788 · 661 · 661 · 595 |
| Linha % do quadro, pontos da dispersão | A27: entregues ÷ (para atender − externas) | **A29:** entregues ÷ (para atender − declinados) = entregues ÷ (entregues + ficou), meio para cima (C8) | 73 · 76 · 71 · 74 · 77 · 77 · 85 · 85 · 75 · 75% (out parcial); antes 65 · 65 · 63 · 66 · 68 · 68 · 75 · 75 · 63 · 65% |
| Dica de cada % ("A conta de …") | − Saíram por decisão externa | Para atender − Declinados (Não teve seguimento), com os status do mês = Dependia da equipe; Entregues ao cliente; Entregamos % | jan: 374 − 46 = 328; 241 ÷ 328 = 73% |
| Selo dos entregues (topo) | 82% (A27) | **A29 no ano:** entregues ÷ (recebidos − declinados) | 4.453 ÷ (5.598 − 981 = 4.617) = 96,4% → **96%** |
| Faixa do topo | % só no selo | **% dos recebidos ao lado de cada número** (A15b, maior resto, somam 100%; `.kpi-pct`; leitor ouve "dos recebidos") | Entregues 4.453 **80%** · Declinados 981 **17%** · Em andamento 164 **3%** de 5.598 |
| Dispersão | x = para atender − externas | x = entregues + ficou; y = entregues; mesmo desenho (equilíbrio 100%, alerta 90%) | todos os meses < 90% |

**Leitura:** o % deixa de penalizar o que não teve seguimento (declinado internamente, standby, declinado pelo mercado ou
talento, encerrado) e passa a responder "da demanda que seguiu viva no mês, quanto a equipe entregou". Limite: o
declinado internamente e o standby, que a A27 mantinha por poderem indicar falta de capacidade, saem da conta; a
composição continua na dica de cada mês. As externas (A27) ficam calculadas em `calculos.py`, fora da tela.

**Layout:** em telas a partir de 1.050 px de palco, os rótulos da faixa do topo ficam numa linha; abaixo disso quebram
como antes. Na dispersão, um 2º anel de posições para rótulos de meses agrupados (out ficava sobre set). Conferido por
captura em 1440×900, 1280×800 e 1024×800. Em 860 px (sem menu lateral) o quadro já invadia o gráfico antes desta
mudança (as colunas de número sozinhas passam do painel): pendência de layout, não desta leva.

**SQL para reproduzir (só leitura):**

```sql
SELECT FORMAT_DATE('%Y-%m', mes) AS mes, entregues, respondidos - entregues AS declinados, ficou,
  CAST(FLOOR(100 * entregues / (entregues + ficou) + 0.5) AS INT64) AS pct
FROM `gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_atendimento_mensal`
WHERE mes >= '2026-01-01' ORDER BY mes
```

Resultado em 27/10/2026: os 10 meses batem com a tela (73 · 76 · 71 · 74 · 77 · 77 · 85 · 85 · 75 · 75). Testes:
`tests/test_atendimento_d53.py` (`test_pct_desconta_todos_os_declinados`, rótulos e `kpi-pct` na página); 475 passaram.

## 0. D53 — capacidade da equipe, extrato em três blocos e status das saídas (26/10/2026)

> **Vigente, exceto a A27 na tela (trocada pela A29, seção 00).** Pedidos do Caio em 26/10/2026, aplicados em sequência no mesmo dia. Carga de 26/10/2026 09:01
> (entrada, fluxo e silver 2026), dados até **25/10/2026**. Tudo conferido no BigQuery (só SELECT).

**Pergunta da página = CAPACIDADE:** "a equipe está dando conta de tudo o que dependia dela no mês, ou deixou coisas
para trás?". Para a diretoria, **resolvido = entregue ao cliente**.

### 0.1 O que está na tela

| Elemento | Regra | Valor (carga de 26/10) |
|---|---|---|
| Faixa do topo | A15b, A27 | Recebidos em 2026 **5.556** → Entregues ao cliente **4.415** (selo **82% do que dependia da equipe**) → Saíram sem entrega **974** (dica com os status) → Em andamento **167**; dados até 25 de outubro |
| Régua do topo | A15b | 4.415 · 974 · 167 = 5.556 (79% · 18% · 3% dos recebidos, maior resto E8c; entregue em destaque, as outras apagadas; a chave de cor fica junto do rótulo, a legenda repetida saiu) |
| Dica "Saíram sem entrega" (topo e rótulo da linha) | A26 | Contam na demanda da equipe **814** (Declinado Internamente 540, Standby 274) · Decisão externa **160** (Declinado pelo Mercado 111, Encerrado 48, Declinado pelo talento 1) · Total **974** |
| ENTRADA — Veio do mês anterior | A24b | 0 · 87 · 85 · 137 · 134 · 148 · 141 · 118 · 101 · 173 |
| + Entrou | A24b | 374 · 341 · 485 · 472 · 629 · 569 · 765 · 644 · 733 · 544 |
| = Para atender (subtotal) | A24b | 374 · 428 · 570 · 609 · 763 · 717 · 906 · 762 · 834 · 717 |
| SAÍDA — Entregues ao cliente | A24b | 241 · 269 · 338 · 386 · 504 · 479 · 672 · 565 · 515 · 446 |
| + Saíram sem entrega (botão com dica por mês) | A24b, A26 | 46 · 74 · 95 · 89 · 111 · 97 · 116 · 96 · 146 · 104 |
| = Saiu no mês (subtotal) | A24b | 287 · 343 · 433 · 475 · 615 · 576 · 788 · 661 · 661 · 550 |
| SALDO — = Ficou para o mês seguinte | A24b, A28 | 87 · 85▼ · 137▲ · 134▼ · 148▲ · 141▼ · 118▼ · 101▼ · 173▲ · 167▼ (▲ cresceu, vermelho pastel; ▼ caiu, verde pastel; no canto da célula; o leitor ouve "cresceu/caiu N em relação ao mês anterior") |
| % (linha única; rótulo "%" à direita, com dica da regra; cada % abre a conta do mês) | A27 | 65 · 65 · 63 · 66 · 68 · 68 · 75 · 75 · 63 · 64% (out parcial) — todos abaixo de 90% |
| Dispersão (direita) | A16, A27 | mesmo desenho de antes (área acima do equilíbrio, tracejado 100%, pontilhado vermelho 90%, "▲ entregamos a mais / ▼ entregamos a menos", cores por faixa, mês parcial vazado); x = demanda que dependia da equipe, y = entregues; eixos a partir de **0** (marcas 0 · 250 · 500 · 750 · 1.000), as duas retas saem do mesmo canto; título do painel e título do eixo só para leitor de tela; quadro 640×400 ocupando a coluna |
| "Próxima pergunta" | D53 | fora da tela em todas as páginas (`.so-leitor` sempre; segue para leitor de tela e passador) |

### 0.2 Regras novas

| ID | Regra |
|---|---|
| A15b | Faixa do ano: resolvido = entregue ao cliente. Partes (entregues, sem entrega, em andamento) em % dos recebidos, inteiros pelo **maior resto** (`entrada._pcts`, E8c, a mesma do Início): somam 100%. Substitui "Resolvidos 5.389 · 96%" (entregues + sem entrega com divisão inteira, que dava 96 + 4 e não batia com a tabela, máx. 87%) |
| A24b | Extrato em três blocos com subtotais: ENTRADA (veio + entrou = para atender), SAÍDA (entregues + sem entrega = saiu no mês), SALDO (para atender − saiu = ficou para o mês seguinte). Rótulo do bloco discreto à esquerda (versalete), fio e respiro entre blocos, sinais numa coluna, subtotais em peso maior sobre fundo leve. Nomes dos meses na mesma linha de base; "parcial" em cima do nome |
| A26 | Composição por **status do board** das saídas sem entrega: `app/sql/saidas_status.sql` (silver 2026 itens + log, regras da gold de fluxo R1, R2, R4, R5, R12–R14, R16–R19, R21, F3, F4; sem data no log = mês de entrada, E7). Exceção documentada como a D30-b (a gold de fluxo não guarda status; pendência para a gold). Um mês só mostra a composição quando a soma bate com a célula (gold); senão a dica diz que a divisão não está disponível |
| A27 | **Taxa de capacidade do mês** = entregues ao cliente ÷ (para atender − saídas **externas** do mês), meio para cima (C8). Externas = "Declinado pelo Mercado", "Declinado pelo talento", "Encerrado" (decisões fora da equipe). **"Declinado Internamente" e "Standby" ficam na base**: podem ser falta de capacidade (a equipe declinou ou parou o pedido). Ano (selo do topo) = entregues ÷ (recebidos − externas do ano). Mês sem composição conferida: externas = 0 (base = para atender) e a dica avisa |
| A28 | No SALDO, ▲/▼ do que ficou contra o mês anterior (igual: nada) |

**Por que a % do ano e a % do mês têm bases diferentes:** no ano, o divisor são os **recebidos** (cada pedido conta uma
vez; menos as decisões externas do ano). No mês, o divisor é o que havia **para atender** (o que veio do mês anterior +
o que entrou; menos as decisões externas do mês): o mesmo pedido pode estar em dois meses (entra em março, fica, e volta
a contar em abril). Por isso a taxa do ano (82%) é maior que a de cada mês (63% a 75%): somar os denominadores mensais
conta os represados mais de uma vez.

### 0.3 Memória de cálculo (carga de 26/10, dados até 25/10)

| Mês | Para atender | Decisões externas (Mercado + talento + Encerrado) | Dependia da equipe | Entregues | % |
|---|---|---|---|---|---|
| jan | 374 | 1 (0 + 0 + 1) | 373 | 241 | 65 |
| fev | 428 | 12 (11 + 0 + 1) | 416 | 269 | 65 |
| mar | 570 | 37 (19 + 0 + 18) | 533 | 338 | 63 |
| abr | 609 | 20 (9 + 0 + 11) | 589 | 386 | 66 |
| mai | 763 | 25 (20 + 0 + 5) | 738 | 504 | 68 |
| jun | 717 | 10 (9 + 0 + 1) | 707 | 479 | 68 |
| jul | 906 | 7 (5 + 0 + 2) | 899 | 672 | 75 |
| ago | 762 | 11 (7 + 0 + 4) | 751 | 565 | 75 |
| set | 834 | 18 (15 + 0 + 3) | 816 | 515 | 63 |
| out (parcial) | 717 | 19 (16 + 1 + 2) | 698 | 446 | 64 |
| **Ano** | recebidos 5.556 | **160** (111 + 1 + 48) | **5.396** | **4.415** | **82** (81,8) |

Status por mês (silver, = gold de fluxo em todos os 10 meses): jan DI 23 · Standby 22 · Enc 1; fev DI 44 · Standby 18 ·
Mercado 11 · Enc 1; mar DI 39 · Mercado 19 · Standby 19 · Enc 18; abr DI 51 · Standby 18 · Enc 11 · Mercado 9; mai DI 69
· Mercado 20 · Standby 17 · Enc 5; jun DI 55 · Standby 32 · Mercado 9 · Enc 1; jul DI 72 · Standby 37 · Mercado 5 · Enc 2;
ago DI 59 · Standby 26 · Mercado 7 · Enc 4; set DI 77 · Standby 51 · Mercado 15 · Enc 3; out DI 51 · Standby 34 · Mercado
16 · Enc 2 · talento 1 (10 cards de outubro sem data de mudança no log: contados no mês de entrada, E7).

### 0.4 SQL para reproduzir (só SELECT)

Topo e linhas da tabela: seção 6 (gold de fluxo e de entradas; fim = 25/10/2026). Totais do ano conferidos em 26/10:
fluxo 2026 `entregue` 4.415, `nao_seguiu` 974, `em_andamento` 167 = 5.556.

Status das saídas sem entrega (A26) — a própria `app/sql/saidas_status.sql` com `@fim = DATE '2026-10-25'`, e a
conferência contra a gold:

```sql
-- (CTEs de app/sql/saidas_status.sql com @fim = DATE '2026-10-25', resultado em q(mes, status, n, sem_data))
, g AS (SELECT IFNULL(mes_evento, mes_entrada) mes, SUM(quantidade) n
        FROM `gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_fluxo_mensal`
        WHERE evento = 'nao_seguiu' AND EXTRACT(YEAR FROM mes_entrada) = 2026 GROUP BY 1)
SELECT mes, SUM(q.n) silver, ANY_VALUE(g.n) gold,
       SUM(IF(status IN ('Declinado pelo Mercado', 'Declinado pelo talento', 'Encerrado'), q.n, 0)) externas
FROM q LEFT JOIN g USING (mes) GROUP BY mes ORDER BY mes
-- esperado (26/10): silver = gold em todos os meses (46, 74, 95, 89, 111, 97, 116, 96, 146, 104);
-- externas 1, 12, 37, 20, 25, 10, 7, 11, 18, 19 (= 160)
```

### 0.5 Validação

- BigQuery (26/10, só SELECT): totais do ano; linhas de jan e out (e as demais) da tabela; composição por status de
  todos os meses = gold de fluxo; externas e taxas acima refeitas à mão e iguais à tela.
- Testes: `tests/test_atendimento_d53.py` (A15b maior resto e 82%, três blocos e linha única, pontos = linha da
  tabela, retas da mesma origem, A27 só com status externos, A26 só quando bate, dicas com `role="tooltip"`,
  "Próxima pergunta" `.so-leitor` em todas as páginas, SQL sem marcador e só SELECT); ajustes em `test_portal.py`,
  `test_rotas.py`, `test_revisao_20261025.py`; `tests/conftest.py` com a consulta de status sintética. 431 testes.
- Capturas 1920, 1850, 1600, 1440, 1280 e 390 px, com dicas abertas (topo, linha, mês, conta do %), sem rolagem
  lateral (390 px: corrigido o vazamento do `.so-leitor` do "Próxima pergunta" e dos textos de leitor do quadro).

### 0.6 Pendências e decisões em aberto

- **Meta da taxa de capacidade**: a régua 100%/90% continua (pedido do Caio), mas nenhum mês passa de 75%: todos os
  pontos ficam vermelhos. Definir se a meta é 90% ou outra.
- **Status na gold**: a composição vem da silver (A26, exceção como a D30-b); levar à gold de fluxo uma coluna de
  status/motivo da saída (lembrete para o projeto irmão).
- "Standby" conta como saída sem entrega (regra da gold); se voltar, vira entrega depois — confirmar com a equipe se
  standby deve continuar na base da equipe.

## Retrato da carga da reunião (26/10/2026, antes da D53)

> **Estado (26/10/2026):** ENTREGUE (D33), regra A25 inalterada. Batalha de 26/10: textos "Saíram sem entrega no mês",
> "do mês anterior + novos", "alerta abaixo de 90%" (1ª leva); faixa e régua paradas, bloco branco num fade de 0,3 s e
> os pontos numa onda de 0,89 s (2ª leva, D49). Em aberto com o Caio (PRD 9.7): frase-resposta que ligue o % do ano ao
> % do mês, % do topo arredondado para baixo (96% + 4%) e a régua de 100%/90%, que deixa todos os meses em vermelho.

Carga **26/10/2026 09:01 (São Paulo)** (entrada 09:01:46, fluxo 09:02:47), dados até **25/10/2026**. As três golds do
mesmo dia e o site na mesma carga: `tools/checar_reuniao.py`, 26/10, 11:33, **tudo certo**.

| Elemento | Regra | Valor (carga de 26/10) |
|---|---|---|
| Faixa do ano | A15 | Recebidos em 2026 **5.556** → Resolvidos **5.389** (96%, arredondado para baixo) → Em andamento **167** (4%) |
| Régua | A15 | 4.415 entregues ao cliente · 974 saíram sem entrega · 167 em andamento (= 5.556) |
| Veio do mês anterior | A24 | 0 · 87 · 85 · 137 · 134 · 148 · 141 · 118 · 101 · 173 |
| + Entrou | A24 | 374 · 341 · 485 · 472 · 629 · 569 · 765 · 644 · 733 · 544 (= Início) |
| = Para atender | A24 | 374 · 428 · 570 · 609 · 763 · 717 · 906 · 762 · 834 · 717 |
| − Entregues ao cliente | A24 | 241 · 269 · 338 · 386 · 504 · 479 · 672 · 565 · 515 · 446 |
| − Saíram sem entrega no mês | A24 | 46 · 74 · 95 · 89 · 111 · 97 · 116 · 96 · 146 · 104 |
| = Ficou para o mês seguinte | A24 | 87 · 85 · 137 · 134 · 148 · 141 · 118 · 101 · 173 · 167 |
| Resolvemos do que havia para atender | A25 | 77 · 80 · 76 · 78 · 81 · 80 · 87 · 87 · 79 · 77% (out parcial); todos abaixo de 90% |

Ponte com o SLA: entregues de jan a set = 3.969; o SLA mede 2.347 deles (59%, ficha `sla.md`, "Conciliação das bases").
SQL para reproduzir: seção 6 (fim = 25/10/2026).

> **ENTREGUE em 24/10/2026 (D33).** Estado final aprovado pelo Caio, com a regra **A25**: o % de cada mês é sobre o que
> havia para atender (represados que vieram + novos), e o gráfico da direita compara esse % com o **objetivo** —
> equilíbrio em 100% e corte em 90%. Média e limite estatísticos (XmR) ficam só calculados no código. Carga de
> referência: gold processada em 23/10/2026 (entrada 20:23:49 UTC, fluxo 20:24:38 UTC), dados até **22/10/2026**.
> Números reconferidos no BigQuery em 24/10/2026 (só SELECT). As versões anteriores da tela estão só no histórico.

## 1. Identificação

| Item | Valor |
|---|---|
| Rota | `/viu-agenciamento/atendimento` (aba "Atendimento", 3ª da ordem da reunião, D30) |
| Montagem | `app/apresentacoes/gestao_orcamentos/apresentacao.py` — `montar_atendimento()`: lê `dados.entrada` e `dados.fluxo`; só calcula se `_mesma_fotografia()` confirmar o mesmo dia de carga e as mesmas entradas por safra; entrega `atendimento`, `fluxo_mes` (A15) e `ritmo` (A16–A25) |
| Cálculo | `app/apresentacoes/gestao_orcamentos/atendimento/calculos.py` — `atendimento()` (A1–A13), `fluxo_mes()` (A15, campos `ano_*`, `entregues_ano_total`, `sem_entrega_ano_total`), `analise_ritmo()` (A16–A25: na tela, só `dispersao` e `quadro`) |
| Template | `app/apresentacoes/gestao_orcamentos/atendimento/template.html` |
| Estilo | `app/static/estilo.css`: `.kpi*` (faixa escura: blocos "faixa escura", "achatada", "três números distribuídos" e "data de corte … efeito gravado"), `.ritmo*` e `.painel-tit` (bloco branco e dispersão), `.quadro*` e `.q-*` (quadro), "coreografia de entrada do Atendimento" |
| Animação | só CSS (D49, 26/10/2026): bloco "D46 no portal" do Atendimento em `estilo.css`; a contagem `contar()`/`data-contar` saiu |
| Testes | `tests/test_portal.py` (`test_fluxo_mes_fecha_a_conta`, `test_analise_ritmo`, `test_abertos_por_mes_de_entrada`, `test_grafico_de_controle`, `test_sombra_do_mes`, `test_folego_do_represado`, `test_conta_por_tras_do_percentual`, `test_linhas_mes_a_mes`, `test_tendencias_mes_a_mes`, `test_quadro_da_demanda`, `test_percentual_sobre_a_demanda_total`), `tests/test_rotas.py::test_pagina_atendimento`; também `test_atendimento.py`, `test_atendimento_executivo.py`, `test_revisao_20261024.py` |
| Tabelas | `gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_entrada_diaria` (`TAB_ENTRADA`, entradas) e `gld_agenciamento_fluxo_mensal` (`TAB_FLUXO`, entregues e saídas sem entrega por mês do evento) |
| Carga de referência | processada em 23/10/2026; dados até **22/10/2026** |

### 1.1 Tabelas e colunas consumidas

**Vigente desde 27/10/2026 (D57: o site só lê a gold).** Conferido com `app/dados.py`; código antigo × novo sobre a
mesma carga real (27/10, 11:11): faixa do ano, quadro, dispersão e dicas iguais.

| Gold (BigQuery) | Tipo · `dados.` | Colunas usadas | Para quê |
|---|---|---|---|
| `gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_entrada_diaria` (`TAB_ENTRADA`) | tabela · `entrada` | as da tabela abaixo | entradas do mês e do ano, grupos, ano anterior |
| `gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_atendimento_mensal` (`TAB_ATENDIMENTO`) | view (entrada + fluxo + status) · `atendimento` | `mes`, `entregues`, `respondidos`, `ficou`, `sem_entrega_sem_data`, `_processado_em` | A13: entregues, sem entrega, fila que ficou (regras AM1–AM3 da gold) |
| `gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_fluxo_mensal` (`TAB_FLUXO`) | tabela · `fluxo` | `mes_entrada`, `evento`, `mes_evento`, `quantidade`, `_processado_em` | A11 (sem entrega por mês do evento) e conferência de carga |
| `gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_2026_saidas_status` (`TAB_SAIDAS_STATUS`) | tabela · `saidas_status` | `mes`, `status`, `n`, `sem_data` | A26/A27: dica dos status e externos (antes `app/sql/saidas_status.sql` na silver) |

SQL para reproduzir o quadro: `SELECT * FROM `gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_atendimento_mensal` WHERE mes >= DATE '2026-01-01'
ORDER BY mes` (veio, para atender, entregues, sem entrega, ficou, externos, dependia). A `app/sql/saidas_status.sql`
citada nas seções 0 e 0.4 está em `_descartados/2026-10-27/app/sql/` (registro).

Estado de 24/10/2026 (registro):

| Tabela (nome completo no BigQuery) | Grão | Colunas usadas nesta página | Para quê |
|---|---|---|---|
| `gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_entrada_diaria` (`TAB_ENTRADA`) | dia × grupo × tipo × família | `data`, `quantidade`, `quantidade_estimada` (A3, "Entrou", Recebidos); `entregue_no_mes`, `entregue_depois`, `nao_seguiu`, `em_andamento` (conferência independente e `_mesma_fotografia`); `quantidade_saida` (A1, não exibida); `_processado_em` (E4, data de corte) | entradas do mês e do ano |
| `gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_fluxo_mensal` (`TAB_FLUXO`) | safra × evento × mês do evento × grupo × tipo × família | `mes_entrada` (só safra do ano, A13), `evento` (`entregue`, `nao_seguiu`; `em_andamento` só na conferência), `mes_evento` (mês da resolução; nulo → mês de entrada, E7), `quantidade`; `_processado_em` (mesmo dia da entrada) | resolvidos, entregues, sem entrega, ficou |

`grupo_input`, `tipo_de_input` e `familia` são lidas (contrato, `COLUNAS_ENTRADA`/`COLUNAS_FLUXO`) e usadas só por
regras calculadas e não exibidas (A9, A10). Cargas reconferidas em 24/10/2026: entrada 23/10 20:23:49 UTC (5.520 até
22/10), fluxo 23/10 20:24:38 UTC (5.360 resolvidos da safra 2026).

## 2. Pergunta e resposta esperada

**Título:** "A equipe está dando conta da demanda?"

O leitor precisa sair sabendo:

1. **No ano:** de 5.520 pedidos recebidos, 5.360 foram resolvidos (97%) e 160 seguem em andamento (3%); dos resolvidos,
   4.388 foram entregues ao cliente e 972 saíram sem entrega.
2. **Mês a mês:** quanto veio represado, quanto entrou, quanto havia para atender, quanto foi entregue, quanto saiu sem
   entrega e quanto ficou para o mês seguinte, com o represado em destaque de calor.
3. **Contra o objetivo:** de tudo o que havia para atender, a equipe resolveu entre 76% e 87% por mês. **Os 10 meses
   ficam abaixo do corte de 90%** (vermelhos): a equipe não resolve toda a demanda do mês; sempre sobra represado.

**Por que o % passa a ser sobre o que havia para atender (A25):** a demanda do mês inclui o represado que veio do mês
anterior, não só o que entrou. Sobre o que entrou, o % passava de 100% sempre que a equipe resolvia parte do represado
(julho: 788 ÷ 765 = 103%), o que sugeria folga que não existe. Sobre o que havia para atender, o % nunca passa de 100%.

**Por que 100% é o objetivo, mas não o padrão:** há sempre pedidos que chegam no fim do mês e ainda estão em andamento
quando ele fecha; chegar a 100% exigiria zerar a fila todo mês. O Caio manteve 100% (equilíbrio) e 90% (corte) como
referências de **objetivo** na tela; a média do ano (81%) e o limite inferior natural (72%, XmR) foram testados como
referência estatística, ficaram calculados no código e **não aparecem** (ver A25 e seção 5, passo 4).

## 3. O que aparece na tela (textos exatos, carga de referência)

**Cabeçalho:** moldura padrão (abas, carimbo "Gerencial") e o título `A equipe está dando conta da demanda?`.

**Faixa escura dos números do ano** (`section.kpi`, "Demanda do ano"): plano marinho escuro (`#17173a → #12122b`), borda
reta, baixa, com sombra interna.

| Elemento | Texto na tela | Regra |
|---|---|---|
| 1º número (centro do 1º terço) | `Recebidos em 2026` · **5.520** | A3, A15 (`ano_recebidos`) |
| seta fina | — (decorativa, `aria-hidden`) | |
| 2º número, em destaque lilás (centro do 2º terço) | `Resolvidos` · **5.360** · selo `97%` | A13, A15 (`ano_resolvidos`); % arredondado **para baixo** |
| seta fina | — | |
| 3º número (centro do 3º terço) | `Em andamento` · **160** · `3%` (cinza) | A13, A15 (`ano_seguem`); % = 100 − % resolvido |
| Data de corte, à direita, separada por um fio vertical | `dados até` (pequeno, sem serifa) e, embaixo, `22 de outubro` em Playfair branca com **efeito gravado** (sombra escura em cima, brilho fino embaixo) | E4 (`atendimento.periodo` sem o "até ") |
| Régua 100% | três partes: entregues (lilás `#8f99ff`), sem entrega (vermelho `#e3877f`), em andamento (listrado branco) | larguras = parte ÷ recebidos |
| Legenda da régua, **centralizada** | `4.388 entregues ao cliente` · `972 saíram sem entrega` · `160 em andamento` | A13 (`entregues_ano_total`, `sem_entrega_ano_total`, `ano_seguem`) |

Em telas estreitas (< 860 px do palco): os três números em três colunas sem setas e a data embaixo, centralizada, com
fio superior.

**Bloco branco flutuante** (`div.ritmo`): desde 25/10/2026 no **mesmo cartão do SLA e do Início** (decisão 7: tokens
`--cartao-*`, fundo branco, borda fina rgba(30,42,120,.07), raio 18 px, sombra marinho), sem mudar o conteúdo nem o
espaçamento interno; dois painéis do mesmo tamanho (proporção 640 × 340) separados por um fio, títulos na mesma linha.
No celular (palco < 860 px) o quadro rola para o lado: primeira coluna presa, sombra à direita indicando mais meses e
caixa focável pelo teclado (`role="region"`, "Quadro do extrato, role para o lado"; AT-01).

*Painel da esquerda* — título `Quanto entrou, quanto resolvemos e quanto ficou` (quadro com 7 linhas, A24 + A25):

| Linha (rótulo exato) | jan | fev | mar | abr | mai | jun | jul | ago | set | out (parcial) |
|---|---|---|---|---|---|---|---|---|---|---|
| `Veio do mês anterior` (vermelho `--quadro-sai` #a8433c, sem opacidade) | 0 | 87 | 85 | 137 | 134 | 148 | 141 | 118 | 101 | 173 |
| `+ Entrou` (azul `--quadro-entrou` #5560b8) | 374 | 341 | 485 | 472 | 629 | 569 | 765 | 644 | 733 | 508 |
| `= Para atender` (neutro, em destaque, fio acima) | 374 | 428 | 570 | 609 | 763 | 717 | 906 | 762 | 834 | 681 |
| `− Entregues ao cliente` (marinho, fio acima; decisão 6, 25/10/2026: antes "Resolvemos (entregues)") | 241 | 269 | 338 | 386 | 504 | 479 | 672 | 565 | 515 | 419 |
| `− Encerrados sem entrega` (vermelho `--quadro-sai` #a8433c, sem opacidade) | 46 | 74 | 95 | 89 | 111 | 97 | 116 | 96 | 146 | 102 |
| `= Ficou para o mês seguinte` (calor no fundo; texto #a8433c, e #7a2e28 nos níveis 3–5) | 87 | 85 | 137 | 134 | 148 | 141 | 118 | 101 | 173 | 160 |
| `Resolvemos do que havia para atender` (decisão 6: antes "Respondemos…") | 77% | 80% | 76% | 78% | 81% | 80% | 87% | 87% | 79% | 77% |

- O % da última linha é (entregues + encerrados sem entrega) ÷ para atender, ou seja, **resolvidos ÷ para atender**
  (resolvidos = 287, 343, 433, 475, 615, 576, 788, 661, 661, 521).
- Cabeçalho das colunas: `jan` … `set`, `out` com `parcial` miúdo embaixo (AT-04, 25/10/2026: antes `out*`, sem
  explicação). A 1ª coluna de cabeçalho tem o nome "Etapa" só para leitor de tela.
- Calor do "ficou": 5 níveis relativos ao maior valor da linha (173): jan 3, fev 2, mar 4, abr 4, mai 4, jun 4, jul 3,
  ago 3, set 5, out 4.
- Cor do %: ≥ 100% marinho (`q-ok`), 90–99% azul (`q-perto`, `--quadro-entrou`), < 90% vermelho (`q-baixo`). Hoje os
  10 meses em vermelho. Faixas pelo objetivo e pelo corte (`qd.objetivo`, `qd.corte`; antes `media`/`limite`).
- **Contraste medido (AT-05, 25/10/2026; texto × fundo efetivo, mínimo 4,5:1):** Veio #a8433c × branco **5,9:1** (antes
  com opacidade .85); Entrou #5560b8 × branco **5,6:1** (antes #6b74c4, 4,3:1); Para atender e Entregues (#14142b /
  #1e2a78) ≥ 12,7:1; Encerrados #a8433c **5,9:1** (antes #b8605a com opacidade .85, < 4,3:1); Ficou n1 #a8433c × #f9f0ef
  **5,3:1**, n2 × #f5e3e2 **4,8:1**, n3 #7a2e28 × #efd4d2 **6,7:1** (antes 4,25:1), n4 × #e8c1be **5,7:1** (antes 3,6:1),
  n5 × #dfaaa6 **4,6:1** (antes 3,0:1); % < 90 #a8433c 5,9:1; % 90–99 #5560b8 5,6:1 (antes 4,3:1).
- Leitor de tela: legenda oculta "Extrato da demanda em cada mês: o que veio do mês anterior, o que entrou, o total
  para atender, o que resolvemos e o que ficou para o mês seguinte." A tabela é HTML real (`scope="col"`/`"row"`).

*Painel da direita* — título `Quanto resolvemos do que havia para atender, em cada mês` (dispersão, A16 + A25):

| Elemento | Na tela | Regra |
|---|---|---|
| Eixos | x = para atender no mês, y = resolvidos no mês, mesma escala (200 a 1.000); **um único rótulo `200` na quina** dos eixos; depois `400`, `600`, `800`, `1.000` em cada eixo; título do eixo x `para atender no mês (represados + novos)` | A16, A25 |
| Linha tracejada | **equilíbrio 100%** (resolvidos = para atender, y = x) | A25 (`objetivo`, fixado em 100) |
| Linha pontilhada vermelha | **corte 90%** (resolvidos = 0,9 × para atender) | A25 (`corte`, fixado em 90) |
| Zona acima da diagonal (fundo azul muito claro) | `▲ resolvemos a mais` (canto superior esquerdo) | A25 |
| Abaixo | `▼ resolvemos a menos` (canto inferior direito) | A25 |
| 10 pontos | cor pelo % arredondado: ≥ 100% marinho; 90–99% azul claro; < 90% vermelho. **Hoje os 10 meses em vermelho.** Outubro **vazado** (parcial: miolo branco, contorno marinho) | A25 (`faixa`), A16 (`parcial`) |
| Rótulo de cada ponto | `mês %` em posição escolhida para não sobrepor pontos, rótulos nem as duas linhas: `jan 77%`, `fev 80%`, `mar 76%`, `abr 78%`, `mai 81%`, `jun 80%`, `jul 87%`, `ago 87%`, `set 79%`, `out 77%` (o mês parcial não leva mais `*`; vazado e na legenda) | A16 (rótulos sem sobreposição) |
| Legenda curta, numa linha (no celular, quebra entre itens) | `equilíbrio 100%` · `corte 90%` · `≥ 100%` · `90–99%` · `< 90%` · `○ out parcial` — faixas geradas de `dp.objetivo.pct` e `dp.corte.pct` (AT-13) e o mês parcial do dado (AT-04) | |
| Texto do SVG | 15,5 unidades do viewBox 640 × 340 (16 nas zonas): **≥ 11 px reais** de 1280 a 1800 px (11,1 px em 1280; 11,4 em 1440; 14,8 em 1800; AT-02, antes 8 px); larguras e deslocamentos dos rótulos recalculados, sem colisão. No celular (390 px) fica em ~8 px; a lista para leitor de tela tem todos os números | A16 |

Leitor de tela: "Cada mês, o que havia para atender e o que resolvemos: jan: 374 para atender, 287 resolvidos (77%); …;
out (parcial, até 22 de outubro): 681 para atender, 521 resolvidos (77%). Equilíbrio em 100% e corte de 90%." O SVG é
`aria-hidden`.

**Antes do 3º mês do ano** (janeiro e fevereiro; AT-D03): a faixa do ano continua e, no lugar do bloco branco, o aviso
`O quadro mês a mês e o gráfico aparecem a partir do 3º mês do ano.` (`role="status"`).

**Rodapé datado** herdado de `apresentacao.html` ("Dados até 22/10/2026 · atualizados em 23/10/2026, 17:23", pelo
`_processado_em` da carga desde 25/10/2026, INI-D1). No celular, "Próxima pergunta" e o rodapé seguem o conteúdo, no
fim do slide (decisão 14).

**Entrada (D49, batalha 2, 26/10/2026; a D46 vale para o portal todo)** — só com `prefers-reduced-motion:
no-preference`; com menos movimento, tudo aparece pronto:

1. a faixa escura dos números do ano e a régua ficam **paradas**: os três números estão no valor final desde o 1º
   quadro (a contagem a partir de zero mostrava "3.917 → 3.799 → 118" ao lado de "4.415 · 974 · 167");
2. o bloco branco (quadro + dispersão) entra num fade de 0,3 s, com quadro, régua, diagonais, rótulos e legenda prontos;
3. o único gesto de dado são os pontos da dispersão, numa onda de 35 ms por mês (150 + 11 × 35 + 350 ms = 0,89 s),
   sem mola.

Antes (24/10): cascata de seis etapas até ~2,7 s, com mola nos pontos e rótulos só aos 2,1 s. Teste:
`tests/test_movimento.py`; conferência no navegador: `node tools/conferir_layout.mjs <url> --movimento`.

**Sem dados coerentes** (entrada e fluxo de cargas diferentes ou safras **do ano exibido** que não batem; safra de ano
anterior divergente só vai ao log, decisão 5): lâmina "Bases em atualização —
Entradas e fluxo ainda não representam a mesma fotografia. A análise volta quando as bases estiverem conciliadas."

## 4. Regras

Fonte única: docstring e comentários de `atendimento/calculos.py`. **Na tela** = usada por algum número ou forma da
página final; **calculada, não exibida** = segue no código (e nos testes), mas não aparece.

| ID | Regra | Situação |
|---|---|---|
| A1 | Entregas do mês por calendário = Σ `quantidade_saida` com data no mês (1ª entrega, D32). Ano: 4.391 (inclui 3 pedidos de safras anteriores) | calculada, não exibida |
| A2 | Entregues no próprio mês / de meses anteriores | calculada, não exibida |
| A3 | Entradas do mês = Σ `quantidade` + `quantidade_estimada` (= E1 do Início) | **na tela** (Recebidos, "Entrou") |
| A4 | Cobertura = A1 ÷ A3 | calculada, não exibida |
| A5 | Entregue no próprio mês = A2 ÷ A3 | calculada, não exibida |
| A6 | Período do ano e taxas só com meses completos | calculada, não exibida (o período "até D de mês" vem de `corte_ano`, como E4) |
| A7 | Mês contra o mesmo mês do ano anterior | calculada, não exibida |
| A8 | Teste z de duas proporções | calculada, não exibida |
| A9 | Entregas do mês por tipo de input | calculada, não exibida |
| A10 | Tabela-legenda por tipo contra o ano anterior | calculada, não exibida |
| A11 | Saíram sem entrega por mês do evento (todas as safras) | calculada, não exibida (a tela usa a versão de A13, só pedidos do ano) |
| A12 | Situação por mês de entrada (as quatro do Início) | calculada, não exibida |
| A13 | **Resolvidos no mês** = eventos `entregue` + `nao_seguiu` do fluxo mensal com `mes_evento` no mês, **só de pedidos que entraram no ano**; `nao_seguiu` sem `mes_evento` atribuído ao **mês de entrada** (convenção E7; 10 casos, todos de outubro); fila (ficou) = Σ entradas − Σ resolvidos desde janeiro | **na tela** (Resolvidos, entregues, sem entrega, em andamento, quadro, eixo y) |
| A14 | Leitura descritiva dos últimos 3 meses completos (`leitura_executiva`, `_pcts_decimos`) | calculada, não exibida |
| A15 | Números do ano (`fluxo_mes`): `ano_recebidos` = A3 do ano; `ano_resolvidos` = Σ resolvidos (A13); `ano_seguem` = fila atual; `entregues_ano_total`, `sem_entrega_ano_total` = Σ das partes de A13. Na tela: % resolvido = ⌊resolvidos × 100 ÷ recebidos⌋ (para baixo, nunca 100% com pedidos em andamento); % em andamento = 100 − % resolvido. As faixas do diagrama do mês (`nos_e`, `nos_s`, `faixas`) não são exibidas | **na tela** (só os campos do ano) |
| A16 | **Dispersão** (`dispersao`): mesma escala nos dois eixos (de ⌊0,85 × menor valor⌋ a ⌈1,05 × maior valor⌉, em centenas; ~4 marcas, a primeira só na quina); mês parcial vazado; rótulos posicionados entre 8 candidatos evitando pontos, outros rótulos e as duas linhas de referência. Correlação, inclinação e trilha conectada são calculadas e não exibidas | **na tela** (forma; o conteúdo segue a A25) |
| A17 | Em andamento por mês de entrada (`abertos`) | calculada, não exibida |
| A18 | Represado no mês (delta) e gráfico de controle (`acumulado.delta`, `controle`) | calculada, não exibida |
| A19 | Sombra do mês (colunas) | calculada, não exibida (testada e rejeitada) |
| A20 | Gráfico de áreas do represado | calculada, não exibida (testada e rejeitada) |
| A21 | Dias de trabalho no represado (`folego`) | calculada, não exibida (testada e rejeitada) |
| A22 | Conta por trás do % de cada ponto (veio, atender, fica) | calculada, não exibida (mesma conta do quadro) |
| A23 | Linhas mês a mês com tendência (`linhas`) | calculada, não exibida (testada e rejeitada) |
| A24 | **Quadro do extrato** (`quadro`): veio = ficou do mês anterior (janeiro = 0, D29); para atender = veio + entrou; entregues e encerrados sem entrega em linhas separadas (A13); ficou = fila do mês; calor do "ficou" = min(5, 1 + ⌊4 × v ÷ maior da linha⌋), nunca negativo (AT-D06). Escalas com amplitude mínima (`hi ≥ lo + 100` na dispersão; topos mínimos nos painéis calculados): meses zerados não dividem por zero (AT-D06) | **na tela** |
| A25 | **% do mês sobre a demanda total** (decisão do Caio, 24/10/2026): % = ⌊100 × resolvidos ÷ para atender + 0,5⌋ (meio para cima, C8; `pct_meio`, AT-D07 de 25/10/2026: antes `round()` do Python), para atender = represados que vieram + novos; nunca passa de 100%. Na dispersão, x = para atender, y = resolvidos. **Referências na tela = objetivo:** equilíbrio 100% (y = x) e corte 90% (y = 0,9 x). Cor (quadro e pontos) pelo % arredondado: ≥ 100 marinho; 90–99 azul claro; < 90 vermelho. **Calculadas e não exibidas:** média do ano e limite inferior natural (XmR) só com meses completos — média = média dos %; limite = máx(0, média − 2,66 × amplitude móvel média) (variáveis locais `media_xmr`, `lic_xmr` em `analise_ritmo`, não devolvidas) | **na tela** (% e objetivo); XmR calculada, não exibida |
| A15b, A24b, A26, A27, A28 | D53 (26/10/2026): ver seção 0.2 — substituem na tela A15 (resolvidos), A24 (seis linhas) e A25 (resolvidos ÷ para atender) | **na tela** |
| D29 | Janeiro começa sem represados (a fila só conta pedidos do ano) | **na tela** |
| D32 | Data de entrega = 1ª ida a "Aguardando Feedback" pelo log; sem ela, `data_de_saida` (regra da gold R12–R14) | **na tela** (define o mês de cada evento `entregue`) |
| E4 | "até D de mês" pela véspera do `_processado_em` em São Paulo | **na tela** (data de corte) |

Decisões de regra: Caio (D27, D29, D32, D33).

## 5. Memória de cálculo (carga de 23/10/2026, dados até 22/10)

**Passo 1 — entradas por mês (A3, gold de entradas):** 374, 341, 485, 472, 629, 569, 765, 644, 733, 508 → **5.520**.

**Passo 2 — resolvidos por mês do evento (A13, fluxo mensal, só safra 2026):**

| Mês | Entregues | Sem entrega | Resolvidos |
|---|---|---|---|
| jan | 241 | 46 | 287 |
| fev | 269 | 74 | 343 |
| mar | 338 | 95 | 433 |
| abr | 386 | 89 | 475 |
| mai | 504 | 111 | 615 |
| jun | 479 | 97 | 576 |
| jul | 672 | 116 | 788 |
| ago | 565 | 96 | 661 |
| set | 515 | 146 | 661 |
| out* | 419 | 102 (10 sem data, atribuídos ao mês de entrada) | 521 |
| **Ano** | **4.388** | **972** | **5.360** |

**Passo 3 — quadro (A24) e % (A25), mês a mês:** veio(m) = ficou(m − 1), com veio(jan) = 0.

| Mês | Veio | + Entrou | = Para atender | − Resolvidos | = Ficou | % = resolvidos ÷ para atender | Faixa |
|---|---|---|---|---|---|---|---|
| jan | 0 | 374 | 374 | 287 | 87 | 76,74% → **77%** | < 90% |
| fev | 87 | 341 | 428 | 343 | 85 | 80,14% → **80%** | < 90% |
| mar | 85 | 485 | 570 | 433 | 137 | 75,96% → **76%** | < 90% |
| abr | 137 | 472 | 609 | 475 | 134 | 78,00% → **78%** | < 90% |
| mai | 134 | 629 | 763 | 615 | 148 | 80,60% → **81%** | < 90% |
| jun | 148 | 569 | 717 | 576 | 141 | 80,33% → **80%** | < 90% |
| jul | 141 | 765 | 906 | 788 | 118 | 86,98% → **87%** | < 90% |
| ago | 118 | 644 | 762 | 661 | 101 | 86,75% → **87%** | < 90% |
| set | 101 | 733 | 834 | 661 | 173 | 79,26% → **79%** | < 90% |
| out* | 173 | 508 | 681 | 521 | 160 | 76,51% → **77%** | < 90% (parcial, vazado) |

Comparação com a regra anterior (% sobre o que entrou, não mais exibida): 77, 101, 89, 101, 98, 101, 103, 103, 90, 103.

**Passo 4 — referências estatísticas (A25, calculadas e não exibidas; meses completos jan–set):**

- média = 724,76 ÷ 9 = **80,53%**;
- amplitudes móveis: 3,40; 4,18; 2,04; 2,60; 0,27; 6,65; 0,23; 7,49 → média 3,355;
- limite inferior natural = 80,53 − 2,66 × 3,355 = **71,60%**.

Leitura: nenhum mês fica abaixo de 72%, ou seja, a variação mês a mês está dentro do normal do próprio ano; mas todos
ficam abaixo do corte de 90% do objetivo. A tela mostra a segunda leitura (contra o objetivo), por decisão do Caio.

**Passo 5 — números do ano (A15):** recebidos 5.520; resolvidos 5.360 = 4.388 + 972; % resolvido = ⌊5.360 × 100 ÷
5.520⌋ = ⌊97,10⌋ = **97%**; em andamento 5.520 − 5.360 = **160** = ficou de outubro; 100 − 97 = **3%**.
Régua: 4.388 ÷ 5.520 = 79,5%; 972 ÷ 5.520 = 17,6%; 160 ÷ 5.520 = 2,9%. (O 97% do ano é sobre os recebidos do ano
inteiro; o % mensal é sobre o que havia para atender no mês. Não são a mesma conta.)

**Passo 6 — escala da dispersão (A16):** menor valor 287 → ⌊287 × 0,85⌋ em centenas = 200; maior 906 → ⌈906 × 1,05 =
951,3⌉ em centenas = 1.000; marcas a cada 200 (200, 400, 600, 800, 1.000), com o 200 uma vez só, na quina.

## 6. Como reproduzir (BigQuery, só leitura)

```sql
-- Quadro completo (A3, A13, A24, A25): entrou, entregues, sem entrega, ficou, para atender e % sobre o que havia
-- para atender. Ajuste o fim (aqui 2026-10-22) para a véspera do _processado_em da carga do dia.
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
    AND CAST(COALESCE(mes_evento, mes_entrada) AS DATE) <= DATE_TRUNC(DATE '2026-10-22', MONTH)  -- AT-D08: nada depois do fim
  GROUP BY 1),
q AS (  -- AT-D08: COALESCE no LEFT JOIN, para um mês sem saídas não deixar o "ficou" NULL
  SELECT e.mes, e.entrou, COALESCE(r.resolvemos, 0) AS resolvemos, COALESCE(r.entregues, 0) AS entregues,
    COALESCE(r.sem_entrega, 0) AS sem_entrega, COALESCE(r.sem_data, 0) AS sem_data,
    SUM(e.entrou - COALESCE(r.resolvemos, 0)) OVER (ORDER BY e.mes) AS ficou
  FROM ent e LEFT JOIN res r USING (mes))
SELECT FORMAT_DATE('%Y-%m', mes) AS mes, entrou, entregues, sem_entrega, resolvemos, sem_data, ficou,
  COALESCE(LAG(ficou) OVER (ORDER BY mes), 0) AS veio,
  COALESCE(LAG(ficou) OVER (ORDER BY mes), 0) + entrou AS para_atender,
  ROUND(100 * resolvemos / (COALESCE(LAG(ficou) OVER (ORDER BY mes), 0) + entrou), 2) AS pct_atender,
  CAST(FLOOR(100 * resolvemos / (COALESCE(LAG(ficou) OVER (ORDER BY mes), 0) + entrou) + 0.5) AS INT64) AS pct_tela  -- C8
FROM q ORDER BY mes;
-- Resultado em 25/10/2026 (carga de 23/10/2026: entrada 20:23:49 UTC, fluxo 20:24:38 UTC), igual à tela:
-- veio 0/87/85/137/134/148/141/118/101/173; ficou 87/85/137/134/148/141/118/101/173/160;
-- pct_tela 77/80/76/78/81/80/87/87/79/77; sem_data = 10 só em 2026-10
-- Referência estatística (não exibida): com os pct_atender de jan a set, média = AVG(pct) e
-- limite = média − 2,66 × AVG(ABS(pct − LAG(pct))). Esperado: 80,53 e 71,60.

-- Conferência independente pela situação da safra (gold de entradas, a mesma do Início)
-- esperado: entradas 5.520; entregue_no_mes + entregue_depois = 4.388; nao_seguiu = 972; em_andamento = 160
SELECT SUM(quantidade + quantidade_estimada) AS entradas, SUM(entregue_no_mes) AS no_mes,
  SUM(entregue_depois) AS depois, SUM(nao_seguiu) AS nao_seguiu, SUM(em_andamento) AS em_andamento,
  SUM(quantidade_saida) AS entregas_calendario  -- 4.391 (A1, não exibida: inclui 3 de safras anteriores)
FROM `gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_entrada_diaria`
WHERE data BETWEEN '2026-01-01' AND '2026-10-22';

-- Carga: as duas tabelas precisam ser do mesmo dia (_mesma_fotografia)
SELECT 'entrada' AS t, MAX(_processado_em) AS p FROM `gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_entrada_diaria`
UNION ALL SELECT 'fluxo', MAX(_processado_em) FROM `gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_fluxo_mensal`;
```

## 7. Validações feitas

| Data | O quê | Resultado |
|---|---|---|
| 24/10/2026 | Consulta do quadro (seção 6) × tela: 10 meses, seis linhas do quadro | ✅ todos os valores iguais aos da seção 3 |
| 24/10/2026 | % sobre o que havia para atender (A25), recalculado à parte com os números do BigQuery | ✅ 77/80/76/78/81/80/87/87/79/77; todos < 90%; XmR 80,53% e 71,60% |
| 24/10/2026 | Fonte independente (situação da safra, gold de entradas) × fluxo mensal | ✅ 3.710 + 678 = **4.388** entregues; **972** sem entrega; **160** em andamento = em andamento do Início |
| 24/10/2026 | Carga das duas tabelas | ✅ entrada 23/10 20:23:49 UTC, fluxo 23/10 20:24:38 UTC (mesmo dia) |
| 24/10/2026 | Invariante veio + entrou = para atender = resolvemos (entregues + encerrados) + ficou, em todo mês | ✅ `test_quadro_da_demanda` (A24: veio + entrou = para atender = entregues + encerrados sem entrega + ficou); também `test_conta_por_tras_do_percentual` (A22), `test_sombra_do_mes` (A19) e, para o mês corrente, `test_fluxo_mes_fecha_a_conta` (A15) |
| 24/10/2026 | Invariante ficou(m) = veio(m + 1); janeiro começa em 0 (D29) | ✅ `test_quadro_da_demanda`, `test_sombra_do_mes`, `test_conta_por_tras_do_percentual` |
| 24/10/2026 | Invariante Σ (entrou − resolvemos) = 160 = em andamento (fila atual) = em andamento do Início | ✅ `test_grafico_de_controle` (Σ delta = seguem), `test_analise_ritmo` (acumulado), `test_abertos_por_mes_de_entrada` (= situação da gold); no BigQuery, 5.520 − 5.360 = 160 = `SUM(em_andamento)` |
| 24/10/2026 | A25: % = resolvidos ÷ para atender, nunca acima de 100%; % do quadro = % dos pontos; corte ≤ equilíbrio | ✅ `test_percentual_sobre_a_demanda_total` |
| 24/10/2026 | Rota | ✅ `test_pagina_atendimento`: título, carimbo, "Recebidos em", "Resolvidos", "Em andamento", nenhum `style=""` (CSP) |
| 24/10/2026 | Suíte completa | ✅ **112 testes passando** |
| 23/10/2026 | Tela anterior (A1–A8) × BigQuery e conciliação gold × silver das entregas por calendário (4.391 × 4.425) | ✅ (histórico; ver PRD 9.2 e 9.3) |
| 25/10/2026 | SQL do quadro corrigida (AT-D08: COALESCE no LEFT JOIN e corte em `DATE_TRUNC(@fim, MONTH)`), só SELECT, `@fim` = 22/10 | ✅ 10 linhas iguais à tela: veio 0/87/85/137/134/148/141/118/101/173; ficou 87/85/137/134/148/141/118/101/173/160; % 77/80/76/78/81/80/87/87/79/77; cargas entrada 23/10 20:23:49 UTC e fluxo 20:24:38 UTC |
| 25/10/2026 | Contraste do quadro (AT-05) medido por linha (texto × fundo efetivo) | ✅ todas ≥ 4,5:1 (seção 3) |
| 25/10/2026 | Texto do SVG (AT-02): `getBoundingClientRect` do SVG × 15,5/640 | ✅ 11,1 px em 1280×720, 11,4 px em 1440×900, 14,8 px em 1800×980; rótulos dos meses sem sobreposição (caixas só tangentes em 1440) |
| 25/10/2026 | Celular 390×844 (AT-01, decisão 14) | ✅ quadro rola para o lado (329/399 px), primeira coluna presa, `scrollWidth` do documento = 390; "Próxima pergunta" e rodapé no fim do slide |
| 25/10/2026 | Testes `test_revisao_20261025.py` (AT-04, decisão 6, AT-11, AT-01, AT-D03, AT-D06, AT-D07) | ✅ 135 testes passando |

## 8. Limites e pontos de atenção

- **Outubro é parcial** (até 22/10): o `parcial` miúdo no cabeçalho, o ponto vazado e o item `○ out parcial` da
  legenda marcam (antes um `*` sem explicação). Os 77% comparam o que havia para atender até o dia
  22 com o resolvido no mesmo período; tende a mudar até o fim do mês.
- **100% é objetivo, não padrão:** sempre há pedidos que chegam no fim do mês. Todos os meses abaixo de 90% descrevem
  que a fila nunca zera; não medem, sozinhos, produtividade da equipe nem prazo (ver a aba SLA).
- **97% do ano × % do mês:** o 97% da faixa é sobre os recebidos do ano inteiro (só restam 160); o % mensal é sobre a
  demanda daquele mês, incluindo o represado. Não comparar um com o outro.
- **"Resolvido" não é "entregue":** inclui 972 saídas sem entrega (declinado, standby, encerrado sem ir ao cliente).
- **Status de "não seguiu" sem corte de data** (`docs/lembretes_gold.md`, item 12 — G2): a gold usa o status de hoje
  para `nao_seguiu`, sem corte em `fim`; uma saída registrada no dia da carga pode entrar antes da hora. Junto, as 10
  saídas sem `mes_evento` (todas de outubro) vão para o mês de entrada por convenção (E7), não por data observada.
- **43 cards de setembro contados em outubro** (lembretes, item 14, a confirmar): se confirmado, setembro e outubro
  trocariam entradas e mudaria o "ficou" de setembro e o "veio" de outubro.
- **Fila reconstruída, não fotografada:** meses passados mudam a cada carga (lembretes, item 15; PD13).
- **Só o ano corrente:** sem comparação com 2025. As entradas estimadas de 2025 (445, data = saída − 5 dias úteis) ficam
  fora desta página.
- **Só pedidos do ano:** resoluções de pedidos de 2025 feitas em 2026 não entram (4.388 entregues aqui × 4.391 entregas
  por calendário em A1).
- **Arredondamento:** meio para cima (C8, `pct_meio`: 76,5 → 77; desde 25/10/2026, antes `round()` do Python, que
  levava ,5 ao par; hoje nenhum mês cai em ,5, a tela não mudou); a cor usa o % já arredondado (89,6% contaria como
  90–99%).
- **Dados de outubro com F8:** 10 dos 508 novos e dos 102 sem entrega vêm de `criado_em` errado (lote de 05–07/10).
- **Nomes internos:** desde 25/10/2026 as chaves são `objetivo` e `corte` (dispersão e quadro) e os comentários seguem a
  A25 (AT-D09/AT-13). Blocos de CSS antigos da página (versões intermediárias) **continuam** no `estilo.css`: a limpeza
  fica para depois da reunião de 28/10.
- **Janeiro e fevereiro (AT-D03):** `analise_ritmo` precisa de 3 meses; antes disso a página mostra a faixa do ano e o
  aviso "O quadro mês a mês e o gráfico aparecem a partir do 3º mês do ano.".
- **Virada do ano (D29, mantida pela decisão 9 de 25/10/2026):** em janeiro de 2027 a fila recomeça do zero: os cerca de
  160 pedidos de 2026 ainda em andamento saem do "veio" de janeiro e da faixa (a página mostra só pedidos do ano). Até
  o 3º mês, só a faixa do ano aparece (item anterior). Mostrar a fila aberta do ano anterior depende da PD20.
- **Sugestão registrada (decisão 8, não aplicada):** com o objetivo de 100% sobre a demanda total, os 10 meses ficam
  vermelhos, embora em 6 deles a equipe tenha resolvido mais do que entrou e a fila esteja estável (85–173). Avaliar
  uma leitura de saldo (resolvidos − entrou), de fila em dias, ou uma frase de resposta à pergunta; e se a zona
  "▲ resolvemos a mais" (que nunca recebe ponto, porque o % sobre a demanda total não passa de 100%) continua.
- **Divergência entre entrada e fluxo (decisão 5):** só safra do ano exibido esconde a página; safra de 2024/2025
  divergente só vai ao log.

## 9. Decisões

D27 (aba criada), D29 (janeiro sem represados), D32 (data de entrega), **D33 (página entregue; decisões do Caio em
ordem, incluindo a A25)**. Ver PRD seção 8 e 9.5.

## 10. Histórico da página

| Data | Mudança |
|---|---|
| 26/10/2026 | **D53** (Caio, em sequência): resolvido = entregue ao cliente no topo (A15b, maior resto); "Próxima pergunta" fora da tela em todas as páginas; extrato em três blocos com subtotais (A24b); dica dos status das saídas sem entrega (A26, `saidas_status.sql`); linha de % única; gráfico com o desenho anterior restaurado e só o dado trocado; taxa de **capacidade** entregues ÷ (para atender − decisões externas) (A27); ▲/▼ no saldo (A28); "parcial" em cima do mês; eixos da dispersão a partir de 0 (retas do mesmo canto), títulos só para leitor de tela, quadro 640×400; tabela sem encostar no divisor; rótulo "%" com dica; "decisão externa" no lugar de "decisão de fora". 431 testes |
| 23/10/2026 | Página criada (D27): entregas × entradas, taxas, comparação com 2025 (A1–A8) |
| 26/10/2026 | Batalha 2 (G3-8, só texto): linha do quadro "Encerrados sem entrega" → "Saíram sem entrega no mês" (mesmo termo do Início e da faixa; aqui pelo mês da saída); eixo "para atender no mês (do mês anterior + novos)"; legenda "corte 90%" → "alerta abaixo de 90%" (figcaption lê o objetivo e o corte do cálculo). Números iguais |
| 23/10/2026 | Comparação compacta com seta; período "até 22 de outubro"; base mínima 30 (A7); coincidência dos +91% explicada (entradas +91,0% × entregas +91,4%, PRD F5) |
| 24/10/2026 | Recomeço: saem comparação com 2025, caixa "Taxas do ano" e dicas; coluna = entregas por tipo de input (A9), contorno = entradas. Regra da data de entrega mantida (D32) |
| 24/10/2026 | Versões intermediárias (A11–A14): situação por mês de entrada; dois painéis (fluxo e fila, 97% em destaque); visual executivo com 3 cartões, entradas × saídas empilhadas, ponte da fila e leitura dos 3 meses (A14). Fila corrigida para 160 (antes 170) com a convenção E7 |
| 24/10/2026 | A pedido do Caio, todo o conteúdo apagado (cartões, gráfico de entradas e saídas, painel da fila, nota); template anterior em `docs/historico/evidencias/atendimento_template_2026-10-24_antes_de_apagar.html` |
| 24/10/2026 | Reconstrução com o Caio (ordem na seção 9.5 do PRD): big numbers do ano (A15) → faixa achatada; testes rejeitados (fluxo do mês, halteres, sombra A19, áreas A20, dias de trabalho A21, linhas com tendência A23); dispersão aprovada (A16, % ao lado do mês, diagonal de 100%, corte de 90%, legenda); quadro do extrato aprovado (A24, cinco linhas + % sobre o que entrou); bloco branco flutuante; faixa escura reta e achatada; coreografia de entrada |
| 24/10/2026 | Faixa escura: três números distribuídos (cada um no centro do seu terço, setas entre eles), data de corte à direita após um fio (primeiro em letra vazada); legenda da régua centralizada |
| 24/10/2026 | **A25:** % de cada mês passa a ser resolvidos ÷ para atender (77/80/76/78/81/80/87/87/79/77); dispersão com x = para atender; testadas como referência a média do ano (81%) e o limite inferior natural (72%, XmR), com zonas "acima / abaixo da média"; **correção do Caio:** as referências voltam ao objetivo (equilíbrio 100%, corte 90%) sobre a demanda total, zonas "resolvemos a mais / a menos", cores ≥ 100 / 90–99 / < 90 (hoje os 10 meses em vermelho); XmR só calculado. Títulos "Quanto resolvemos do que havia para atender, em cada mês"; um único "200" na quina; data de corte como "dados até" + "22 de outubro" em Playfair branca gravada (a letra vazada saiu). Quadro com "Resolvemos (entregues)" e "Encerrados sem entrega" em linhas separadas e última linha "Respondemos do que havia para atender". **Página ENTREGUE (D33).** Ficha revista inteira; números reconferidos no BigQuery; 112 testes |
| 25/10/2026 | **Revisão de 25/10 (auditoria + decisões 6–9 delegadas pelo Caio):** linha "− Entregues ao cliente" e "% Resolvemos do que havia para atender" (decisão 6); bloco branco no mesmo cartão do SLA e do Início, tokens `--cartao-*` (decisão 7); saldo/frase de resposta e zona "▲ resolvemos a mais" só como sugestão (decisão 8); virada do ano mantida e documentada (decisão 9). Auditoria: quadro rolável no celular com 1ª coluna presa (AT-01); contraste ≥ 4,5:1 com tokens `--quadro-*` (AT-05); `out` + `parcial` miúdo no lugar de `out*`, `○ out parcial` na legenda e "(parcial, até 22 de outubro)" para o leitor (AT-04); `dl` da faixa só com dt/dd (AT-11); texto do SVG ≥ 11 px (AT-02); escala sem divisão por zero e % meio para cima (AT-D06/D07); aviso antes do 3º mês (AT-D03); chaves `objetivo`/`corte`, legenda gerada e comentários da A25 (AT-D09/AT-13); SQL da ficha corrigida e reconferida (AT-D08). Números iguais (5.520 / 5.360 / 160; 77…77%). 135 testes |
| 26/10/2026 | **Batalha 2:** textos "Saíram sem entrega no mês", "do mês anterior + novos", "alerta abaixo de 90%" (1ª leva); faixa e régua paradas, fade de 0,3 s no bloco branco, pontos em 0,89 s (2ª leva, D49). **Documentação:** retrato da carga da reunião (5.556 → 5.389 → 167; quadro mês a mês) no topo e as decisões abertas do Caio (PRD 9.7); A25 inalterada |
| 27/10/2026 | **D57:** o quadro mês a mês (A13) lê a view gold `gld_agenciamento_atendimento_mensal` e a dica de status (A26) a tabela gold `gld_agenciamento_2026_saidas_status` (antes `app/sql/saidas_status.sql` na silver); números iguais na mesma carga |
