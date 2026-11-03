# Ficha — Talentos (divisão anual da demanda)

## Recorte do mês fechado (D68, 03/11/2026) — ler primeiro

> A tela mostra só até **31/10/2026** (`talentos.recortar`). Os 4 pedidos de 02/11 eram todos de exclusivos (Giovanna
> Pitel 1, Gilberto Nogueira 2, Beatriz Reis 1, pelo `n_mes` de novembro do ranking), o que fecha com os 4 da gold de
> entradas: a divisão do ano fica **3.544** exclusivos (61%; era 3.548), **2.084** não exclusivos (36%), **157** sem
> talento (3%) = **5.785**. 10 mais pedidos: **1.848** (32%; era 1.851); Beatriz Reis 247, Gilberto Nogueira 192; ordem
> igual. Mapa sem coluna "nov até 2" (novembro e dezembro futuros). Regra: o ranking perde as linhas dos meses depois do
> recorte (`n` = o da gold menos os `n_mes` que saem; `pos` refeito; `ultimo_pedido` vazio para quem tinha pedido
> depois); a divisão do ano (a gold não tem mês) só é recortada quando os `n_mes` de exclusivos + não exclusivos que saem
> somam os pedidos que saem da gold de entradas; se não somarem (pedido sem talento ou do Squad depois do recorte), a
> divisão fica a da carga e a página mostra o aviso de diferença da T5.

## Retrato da carga da reunião de 04/11 (carga congelada de **03/11/2026 09:02** (dados até **02/11/2026**; D67, `docs/PRD_V2.md` seção 0.6))

> Exclusivos **3.548** (61%), não exclusivos **2.084** (36%), talento não informado **157** (3%) = 5.789. Os 10 mais
> pedidos somam 1.851 (32%); 1º Tatiana Machado (283). O retrato de 26/10 abaixo é histórico.

## Retrato da carga da reunião (26/10/2026)

> **Estado (26/10/2026, D50):** página com **seletor Todos / Exclusivos / Não exclusivos**, resposta por recorte e
> **mapa de calor dos 10 talentos mais pedidos × jan–dez** (pedido do gerente do Caio; revisa a D31). Regras T1–T6
> mantidas, novas T7–T10 (seção 0). Exceção D30-b (silver) até a PD01. Antes (D49): a barra se revela num gesto só.
> **D51 (26/10/2026, Caio; seção 0-D51):** ao abrir, a barra cresce e os números contam com o top 10 parado; botão
> play (só ícone ▶, na linha da legenda da barra) roda a "corrida do ano" (entra e sai do top 10; revista no mesmo dia:
> mais calma, ~11 s); nomes sem reticências (T11, T12).

Carga da gold de entradas **26/10/2026 09:01 (São Paulo)**, `@fim` = 25/10/2026; silver modificada em 26/10, 08:33.

| Elemento | Regra | Valor (carga de 26/10) |
|---|---|---|
| Frase (Todos; D50) | T8 | "Da demanda do ano, **62%** vai para os talentos exclusivos." (até a D50: "62% da demanda do ano se concentra nos talentos exclusivos.") |
| Frase (Exclusivos / Não exclusivos; D50) | T8 | "Dos pedidos de talentos exclusivos, **52%** vão para os 10 talentos mais pedidos." / "…não exclusivos, **11%** vão…" |
| Barra (pedidos · %) | T2, T3 | Exclusivos 3.451 · 62% · Não exclusivos 1.980 · 36% · Talento não informado 125 · 2% |
| Conciliação com o Início | T5 | 3.451 + 1.980 + 125 = **5.556** = Início (sem aviso na tela) |
| Top 10 exclusivos | T6 | 282 (Tatiana Machado) … 120; "Juntos, 1.808 pedidos: 52% dos exclusivos" |
| Top 10 não exclusivos | T6 | 65 (Jonas Fernando Sulzbach) … 12; 10º lugar empatado com mais 2 talentos; "Juntos, 225 pedidos: 11% dos não exclusivos" |

SQL para reproduzir: seção 6 (mesmas consultas, com `@fim = DATE '2026-10-25'`); mapa mês a mês: seção 0.

## 0-D51. Movimento de Talentos e "corrida do ano" no botão play (26/10/2026)

> **Decisão do Caio (26/10/2026), D51 — exceção à D46/D49 ("números prontos desde o 1º quadro") só nesta página.**
> Revista no mesmo dia, nesta ordem: corrida automática ao abrir (6–8 s) → mais rápida (~4 s) → contínua, sem "tac,
> tac" → **corrida só no botão play, com entrada e saída do top 10** → **play só com ícone, fora do cartão, e corrida
> mais calma e elegante (~11 s)** (vigente, pedido do Caio em 26/10). Nenhum número, texto ou regra de cálculo da
> tabela mudou; o HTML do servidor é sempre o estado final.

**O que a tela faz (vigente)**

| Momento | Comportamento |
|---|---|
| Abertura e troca de filtro | A barra do ano cresce da esquerda para a direita e os % e as quantidades dentro dela contam de 0 ao valor (ease-out, 0,6 s), com o número grande da resposta (ex.: 0% → 62%). Na tabela, só os números das células e da coluna Ano contam até o valor (0,7 s); as **linhas ficam paradas** nas posições finais. Não há botão "Pular". |
| Botão play | **Só o ícone ▶**, num botãozinho redondo e discreto (2 em, mínimo 24 px), **fora do cartão**: na linha da legenda da barra ("Exclusivos · Não exclusivos · Talento não informado"), alinhado à borda direita do conteúdo, logo acima do canto superior direito do cartão do mapa. Nome acessível e dica (`title`) iguais: "Ver a subida e descida das posições ao longo do ano"; `aria-describedby` explica que é opcional. Durante a corrida fica azul com ■ e nome/dica "Parar"; ao terminar ou parar, volta a ▶. Foco visível (contorno azul de 2 px). Vem antes da tabela na ordem do Tab. Nenhum texto visível. |
| Corrida (~11 s nos 10 meses) | **Tempo do ano mês a mês:** cada mês anda em `TEMPOS.mes` com easing suave (easeInOutSine) e **respira** `TEMPOS.respiro` no fim. Uma **moldura** azul clara desliza para a coluna do mês corrente na primeira metade do mês; o cabeçalho do mês fica azul e os seguintes, cinza; o **mês aparece grande** (serifa itálica clara) no canto superior direito do cartão, com crossfade. As células do mês **acendem** (transição do tom, `TEMPOS.acender`) e o número delas e o do Ano **contam**; meses adiante ficam como casas vazias. **Lugar:** acumulado entre todos os que passaram pelos 10 (T12; empate = lugar no ano), com **histerese**: diferença de até 0,5 pedido ou 2% do líder não troca ninguém, e a nova ordem só vale depois de persistir por `TEMPOS.histerese`; aí entra inteira, e cada linha faz uma única viagem (mola criticamente amortecida, `TEMPOS.deslize`: velocidade contínua, sem passar do lugar, quem vai mais longe leva mais tempo). Quem sobe passa **por cima**, sobre um cartão branco com sombra leve; quem desce passa por baixo. A **numeração 1–10 é fixa** (as linhas trocam de lugar, os números não; nunca dois "10"). Começa na ordem do fim de janeiro (o 1º mês não embaralha a tabela inteira). Quem sai dos 10 desce ~meia linha e some; quem entra surge de baixo com fade. No fim: a ordem exata do ano, a moldura e o mês somem e a cópia sai — **fica a tabela do servidor**, idêntica. |
| Sem JS / captura / impressão | A tabela pronta; botão escondido (sem JS) e fora da impressão. |
| Movimento reduzido | Nada se mexe; o botão aparece desabilitado e o texto de apoio diz por quê. |
| Interrupções | "■ Parar", Esc e outras teclas (menos Tab, modificadoras e as do próprio botão), clique/roda/toque na tabela ou na barra, rolagem do mapa, troca de aba, mudança real de largura (> 40 px) e impressão: vão direto ao estado final. O foco não é movido. |

**Como funciona (para manutenção).** Bloco "D51" de `app/static/apresentacao.js` e de `app/static/estilo.css`.
Abertura e corrida rodam numa **cópia** da tabela (`.corrida-palco`, `aria-hidden`, `inert`) sobreposta à original,
que só fica transparente (`.corrida-escondida`, opacidade 0): o leitor de tela lê sempre os valores finais e nada é
anunciado. Por quadro só mudam `transform`, `opacity`, texto e classes (cor e camada); as posições das linhas são medidas uma vez. Os dados
vêm do HTML: `data-corrida-meses` (meses com dado), `data-corrida-maior` (maior mês, para os 6 tons das linhas que
entram), `data-corrida-extras` (JSON: nome, lugar no ano e pedidos de jan até o corte de quem passou pelos 10 sem
fechar o ano entre eles) e, em cada linha, `data-corrida-pedidos`. `.d51` desliga a onda de tons da D50.

**Onde mudar os tempos:** um só lugar, `var TEMPOS = { barra: 600, numeros: 700, mes: 780, respiro: 260, acender: 420,
deslize: 260, histerese: 340, rotulo: 380, assentar: 2200 }` no bloco D51 de `apresentacao.js` (ms). Abertura: `barra`
= barra + contagens de cima; `numeros` = contagem das células e do Ano. Corrida (play): `mes` = um mês andando;
`respiro` = pausa no fim de cada mês (duração ≈ meses × (mes + respiro) = 10 × 1.040 ≈ 10,4 s + ~0,5 s para pousar);
`acender` = célula ganhando o tom; `deslize` = tempo da mola das linhas (maior = mais macio e mais lento);
`histerese` = quanto a nova ordem precisa durar para valer (maior = menos trocas); `rotulo` = crossfade do mês no
canto; `assentar` = limite de espera no fim. A margem da histerese fica ao lado: `MARGEM = 0.5` pedido e
`MARGEM_REL = 0.02` (2% do líder). O teste `test_js_continuo_tempos_num_lugar_e_sem_layout_por_quadro` limita barra ≤
700, números ≤ 1.000 e 10 × (mes + respiro) entre 9.000 e 12.000 ms (pedido do Caio: 9–12 s).

**Regras novas**

| Código | Regra | Onde |
|---|---|---|
| T11 | Coluna dos nomes com a largura do maior nome exibido no recorte + ~10% de folga, sem reticências: o servidor calcula os caracteres do maior nome (`largura_nomes`, entre 10 e 30) e a classe `mapa-nomes-N` dá `width: calc((N × 0,555 em + 1,78 em) ÷ 0,92)` (0,505 em por caractere do IBM Plex Sans, o maior medido; +10%; número da posição e respiro). Fonte da tabela 0,94 em (cabeçalhos e posição 0,92): nomes, células e Ano ≥ 11 px reais em 1920/1440/1280 (12,2 / 11,6 / 11,2 px a 1280). Em 390 px o nome quebra em até 2 linhas e o mapa rola dentro do próprio quadro (a página não rola para o lado). | `calculos.py`, `template.html`, `estilo.css` |
| T12 | Corrida do play: ranking pelo acumulado de jan até cada ponto do ano entre todos os talentos do recorte; a consulta traz os 10 do ano e quem esteve entre os 10 do **acumulado no fim de algum mês** (coluna `pos` = lugar no ano; desempate = `pos`). Entre os fins de mês o acumulado é interpolado (linear no mês). Quem não fecha a soma mensal fica fora da corrida (aviso no log), sem afetar a tabela. | `talentos_top.sql` (CTEs `acumulado`, `na_corrida`), `top_por_grupo()`, `mapa()` |

**Consulta (só SELECT).** `talentos_top.sql` ganhou as CTEs `acumulado` (pedidos de jan até o fim de cada mês, por
talento) e `na_corrida` (`ROW_NUMBER() OVER (PARTITION BY grupo, mes ORDER BY ate_o_mes DESC, pos) <= 10`), ligadas ao
resultado por `LEFT JOIN` (`WHERE r.pos <= 10 OR c.chave IS NOT NULL`), e a coluna `pos`. Atenção: a 1ª versão usava
`EXISTS` correlacionado, que o BigQuery recusa ("Correlated subqueries … not supported"), e derrubou a página por
alguns minutos no servidor local; desde então a SQL é validada no BigQuery antes de ser gravada.

**Conferência no BigQuery (26/10/2026, `@fim` = 25/10/2026, carga de 26/10).** Consulta completa: exclusivos 17
talentos na corrida (10 do ano + 7: Milton Cunha #11, Giovanna Pitel #12, Maria Beltrão #14, Viviane Araújo #17,
Aline Patriarca #22, Vinicius Nascimento #23, Angélica #27); não exclusivos 21 (10 + 11); todos 17 (10 + 7). Ranking
acumulado do recorte Todos, refeito por consulta independente:

| Fim de | 1º–10º (acumulado) |
|---|---|
| jan (31/01) | Tatiana Machado 28 · Viviane Araújo 23 · Beatriz Reis 20 · Milton Cunha 20 · Gilberto Nogueira 18 · Juliette Freire 14 · Giovanna Pitel 14 · Vinicius Nascimento 14 · Renata Saldanha 13 · Maria Beltrão 13 |
| abr (30/04) | Tatiana Machado 84 · Beatriz Reis 71 · Juliette Freire 64 · Gilberto Nogueira 63 · Eliana Michaelichen 58 · Renata Saldanha 49 · Milton Cunha 48 · Viviane Araújo 47 · Ticiane Pinheiro 44 · Giovanna Pitel 42 |

Bate com os `data-corrida-*` da página (ex.: Viviane 23 → 47; Milton 20 → 48; Ticiane 0 → 44) e com o quadro de fim de
janeiro da corrida capturado na tela. Empates (Beatriz e Milton com 20 em jan) seguem o lugar no ano.

**Validação.** `tests/test_talentos_d51.py` (dados da corrida = células e Ano; soma mensal = total; quem termina no
top 10 = tabela final; extras com lugar > 10; extra que não fecha fica fora; abertura sem troca de posição; corrida só
no play; botão nativo **só ícone**, com nome e dica iguais, escondido sem JS, sem "Pular", fora do cartão na linha da
legenda e antes da tabela no Tab; histerese e numeração fixa; movimento reduzido; cópia `aria-hidden`; tempos num
lugar só; quadro sem medida de layout; T11) e exceção explícita D51 em `tests/test_movimento.py`. Capturas (CDP em
tempo real; `--virtual-time-budget` quase não avança quadros de `requestAnimationFrame`, então não serve para a
corrida) nos 3 filtros em 1920×1000 e 1280×800: abertura (250 ms), após a abertura, meio da corrida (2,2 s após o
play) e fim (6 s após o play), e com movimento reduzido; 1440×900 e 390×844 com movimento reduzido. Fim da corrida =
captura com movimento reduzido (diferença só na pílula do menu superior e no botão desabilitado).

**Revisão de 26/10/2026 (play só ícone e corrida calma) — conferência visual.** CDP em tempo real, clicando o play:
quadros a cada 1 s (0–12 s e 13,5 s) em 1920×1000 nos 3 filtros, em `C:\Users\CCMB\AppData\Local\Temp\claude\g--Meu-Drive-Workspace-globo-scripts-PPD-AGENCIAMENTO-SLA\14583fd6-acde-47fa-aa2a-77546d47d85a\scratchpad\talentos4\seq\` (`<filtro>_playN.png` e
`prancha_<filtro>.png`, recortes do cartão lado a lado); posição do botão em 1920/1440/1280/390 e com movimento
reduzido em `C:\Users\CCMB\AppData\Local\Temp\claude\g--Meu-Drive-Workspace-globo-scripts-PPD-AGENCIAMENTO-SLA\14583fd6-acde-47fa-aa2a-77546d47d85a\scratchpad\talentos4\botao\`. Avaliação: sem dois números de posição iguais (numeração fixa), quem sobe por cima de quem
desce, meses anteriores estáveis e o último quadro idêntico à tabela do servidor nos 3 filtros; o botão fica a 0 px da
borda direita do cartão (1920: botão 1794–1832, cartão até 1832) e, em 390 px, à direita da legenda em duas linhas, sem
rolagem lateral. Limites conhecidos: em quadros soltos aparecem linhas no meio do caminho durante uma troca (é o
deslize); com a histerese, a ordem pode andar até ~0,3 s atrás dos números, e na reta final as linhas se acertam no
respiro do último mês (a ordem exata do ano entra no fim). Nenhuma SQL mudou (não houve consulta nova ao BigQuery).

## 0. Estado vigente — D50 (26/10/2026): seletor, resposta por recorte e mapa mês a mês

> **Pedido do gerente do Caio (26/10/2026), decisão D50; revisa a D31,** que tinha deixado a página sem visão mensal.
> Vale esta seção onde as seções 2 e 3 (estado D31) disserem outra coisa: as dicas de top 10 na legenda saíram (o mapa
> mostra os mesmos 10 nomes com os totais) e a coluna "Último" não aparece mais na tela (segue na consulta).

**Carga de referência:** gold de entradas `_processado_em` 26/10/2026 12:01 UTC (09:01 em São Paulo), `@fim` =
25/10/2026; silver `slv_agenciamento_2026_itens` da mesma manhã. Conferido no BigQuery em 26/10/2026 (seção 0.5).

### 0.1 O que mudou na tela

| Elemento | D50 | Regra |
|---|---|---|
| Seletor | "Talentos: Todos · Exclusivos · Não exclusivos", o mesmo componente do SLA (`nav.grupos`, `data-navegador`, pílula marinho, links `?talentos=todos\|exclusivos\|nao-exclusivos#1`). Cada botão mostra os pedidos do ano do recorte (**5.556 · 3.451 · 1.980**). Filtra a página inteira; as abas, o menu e "Próxima pergunta" levam o recorte (`filtro_talentos=True`); filtro desconhecido = Todos | T7 |
| Resposta (esquerda) | Peça tipográfica do SLA ("Levamos 14 h…"): conector em sans leve, número grande em Playfair azul, complemento em itálico e fecho em Playfair. Linha de apoio com fio azul e a conta em números | T8 |
| Barra do ano (direita, em cima) | Mais fina (2,3 em, era 4,2 em), % e quantidade na mesma linha. Sempre os três grupos do ano (contexto). Com Exclusivos ou Não exclusivos, o grupo do recorte fica na cor e os outros dois em contorno claro (texto `--tinta-2`, legível); a legenda esmaece os outros dois; a lista do leitor de tela marca "(recorte escolhido)". No celular a palavra "pedidos" sai (só o número) | T9 |
| Mapa de calor (direita, embaixo) | Cartão "Os 10 talentos com mais pedidos, mês a mês": linhas = os 10 talentos do recorte em ordem de pedidos; colunas jan…dez; número em cada célula; total do ano à direita ("Ano"); outubro com "até 25" e contorno azul (mês em andamento); nov e dez em cinza, sem número, rótulo em itálico `--tinta-3` (como os meses futuros do SLA); legenda "menos ▢▢▢▢▢▢ mais pedidos no mês". Pé: "Juntos, N pedidos: X% …" + empate no 10º lugar quando houver + "Squad de Talentos (grupo) fora" em Todos | T10, T6 |
| Acessibilidade | O mapa é uma `<table>` com `<caption>` (oculta), `th scope="col"` nos meses e `th scope="row"` nos nomes: o leitor de tela lê talento, mês e pedidos. Mês futuro: "sem dado" e "(mês futuro)" no cabeçalho; outubro: "(mês em andamento)". Cor nunca sozinha: o número está escrito. Contraste: texto escuro nos tons 1–4 (≥ 6,8:1), branco nos tons 5–6 (≥ 6,7:1); zero em `--tinta-3` sobre quase branco (5,2:1). Nenhum `style=""` (tons por classe `hm-n0…hm-n6`; colunas por `hm-c0…hm-c11`) | — |
| Movimento (D46/D49) | Números prontos desde o 1º quadro. Um gesto: o tom das células aparece coluna a coluna, de jan a dez (160 ms + 11 × 40 ms + 400 ms = 1,0 s; só `opacity` da camada de cor `::before`); nas células escuras o número passa de tinta a branco junto. A barra mantém a revelação de 1,12 s. Com "menos movimento", tudo parado; troca de filtro e recarga abrem prontas (`.revisto`) | — |
| Layout | Grade como o SLA: seletor em cima à esquerda; resposta embaixo à esquerda; à direita, da altura do seletor ao pé, barra + mapa (o cartão estica até o pé e as linhas dividem a altura). Cabe sem rolar em 1920×1000, 1440×900 e 1280×800; em 390 px tudo numa coluna, sem rolagem lateral (meses futuros saem do mapa, como no SLA; nomes longos com reticências, nome inteiro no `title` e no leitor de tela) | — |

### 0.2 Números exibidos por recorte (carga de 26/10, `@fim` = 25/10/2026)

| Recorte | Resposta (frase lida na ordem) | Apoio | Barra | Mapa (pé) |
|---|---|---|---|---|
| Todos | "Da demanda do ano, **62%** vai para os talentos exclusivos." | "**3.451 de 5.556** pedidos do ano" / "1.980 não exclusivos; 125 sem talento informado" | 62% 3.451 · 36% 1.980 · 2% 125, sem destaque | "Juntos, 1.808 pedidos: 33% da demanda do ano · Squad de Talentos (grupo) fora" |
| Exclusivos | "Dos pedidos de talentos exclusivos, **52%** vão para os 10 talentos mais pedidos." | "**1.808 de 3.451** pedidos exclusivos do ano" / "39 talentos exclusivos tiveram pedidos no ano" | Exclusivos em destaque | "Juntos, 1.808 pedidos: 52% dos exclusivos" |
| Não exclusivos | "Dos pedidos de talentos não exclusivos, **11%** vão para os 10 talentos mais pedidos." | "**225 de 1.980** pedidos não exclusivos do ano" / "944 talentos não exclusivos tiveram pedidos no ano; Squad de Talentos (grupo) fica fora da lista e conta no total" | Não exclusivos em destaque | "Juntos, 225 pedidos: 11% dos não exclusivos · 10º lugar empatado com mais 2 talentos (12 pedidos cada)" |

Contas: 3.451 ÷ 5.556 = 62,11% → **62%** (T4); 1.808 ÷ 3.451 = 52,39% → **52%**; 225 ÷ 1.980 = 11,36% → **11%**;
1.808 ÷ 5.556 = 32,54% → **33%**. Em "Todos", o top 10 geral é igual ao dos exclusivos (o 1º não exclusivo, com 65
pedidos, fica abaixo do 10º exclusivo, com 120). O denominador dos não exclusivos inclui os 119 pedidos do Squad de
Talentos (T3), que fica fora da lista: o mesmo critério das dicas da D31.

### 0.3 Regras novas (T7–T10)

| ID | Regra | Onde |
|---|---|---|
| T7 | Seletor Todos / Exclusivos / Não exclusivos pela URL (`?talentos=`, mesmas chaves do SLA e da Previsão); valor de cada botão = pedidos do ano do recorte (Todos = total da divisão) | `calculos.FILTROS`, `seletor()`; `montar_talentos()`; `Secao(filtro_talentos=True)` |
| T8 | Resposta por recorte. **Todos:** % do maior grupo na divisão do ano (T4) — "Da demanda do ano, X% vai para os talentos [grupo]." (se o maior fosse "talento não informado": "…X% está sem talento informado."). **Exclusivos / Não exclusivos:** % dos pedidos do grupo que vão para os 10 talentos mais pedidos do grupo = soma do top 10 (T6) ÷ total do grupo na divisão (T1), `round()` — "Dos pedidos de talentos [grupo], X% vão para os 10 talentos mais pedidos." (concordância para 1 talento). Sem ranking coerente com a divisão: sem número ("a lista … está sendo atualizada") | `heroi()` |
| T9 | Barra do ano sempre com os três grupos; com filtro, o grupo do recorte destacado e os outros esmaecidos | `barra()` |
| T10 | Mapa de calor: os 10 talentos do recorte (T6; **Todos = exclusivos e não exclusivos juntos pelo mesmo nome normalizado**, sem Squad e sem pedido sem talento) × jan–dez do ano do corte. **Mês do pedido = mês da data de entrada** pelas mesmas regras de T1 (R21 retroativo → `data_de_entrada`; senão `DATE(criado_em)`; sem `criado_em` → `data_de_saida` − 5 dias úteis). **Um talento por pedido:** a coluna `talento` da silver guarda um nome só (conferido: nenhum valor com vírgula, ponto e vírgula ou barra; os 10 com " e " são duplas, como "Bruno e Marrone", e contam como um talento). Soma dos 12 meses = total do ano do talento; se não bater (ou houver pedido depois do corte), o mapa não aparece e o servidor registra no log. Meses depois do mês do `@fim` = futuros (sem número); o mês do `@fim`, se não terminou, é parcial ("até DD"). Tom: `ceil(6 × n ÷ maior mês do recorte)` (1 a 6; 0 = mês sem pedido), número sempre escrito. Empate no 10º lugar: mesma regra da decisão 11 (desempate alfabético + nota) | `app/sql/talentos_top.sql`, `top_por_grupo()`, `mapa()` |

### 0.4 Memória de cálculo do mapa (carga de 26/10, `@fim` = 25/10/2026)

Resultado de `app/sql/talentos_top.sql` no BigQuery (264 linhas = talento × mês com pedido, nos três recortes);
o site só faz a grade e os tons.

**Exclusivos (e Todos: o top 10 geral é o mesmo)** (out = parcial, até 25/10; nov e dez = futuros, sem número)

| # | Talento | jan | fev | mar | abr | mai | jun | jul | ago | set | out | Ano |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | Tatiana Machado | 28 | 15 | 19 | 22 | 44 | 26 | 47 | 32 | 30 | 19 | 282 |
| 2 | Beatriz Reis | 20 | 17 | 16 | 18 | 21 | 21 | 25 | 31 | 42 | 31 | 242 |
| 3 | Juliette Freire | 14 | 9 | 19 | 22 | 14 | 29 | 39 | 16 | 28 | 17 | 207 |
| 4 | Ticiane Pinheiro | 0 | 1 | 21 | 22 | 27 | 26 | 37 | 28 | 24 | 4 | 190 |
| 5 | Gilberto Nogueira | 18 | 13 | 20 | 12 | 13 | 16 | 27 | 22 | 30 | 16 | 187 |
| 6 | Eliana Michaelichen | 11 | 9 | 25 | 13 | 19 | 22 | 26 | 12 | 15 | 20 | 172 |
| 7 | Tadeu Schmidt | 9 | 8 | 7 | 13 | 17 | 25 | 32 | 20 | 14 | 7 | 152 |
| 8 | Renata Saldanha | 13 | 14 | 13 | 9 | 13 | 12 | 16 | 17 | 10 | 14 | 131 |
| 9 | Maxiane Rodrigues | 0 | 7 | 19 | 8 | 18 | 12 | 21 | 14 | 17 | 9 | 125 |
| 10 | Chaiany Pinto Andrade | 0 | 1 | 4 | 28 | 19 | 13 | 14 | 14 | 14 | 13 | 120 |
| | **Soma dos 10** | 113 | 94 | 163 | 167 | 205 | 202 | 284 | 206 | 224 | 150 | **1.808** |

Maior mês do recorte: 47 (Tatiana Machado, jul) → tom 6 a partir de 40 (`ceil(6 × 40 ÷ 47)` = 6); 11º lugar: Milton
Cunha, 117 (sem empate no corte).

**Não exclusivos** (out = parcial, até 25/10; nov e dez = futuros, sem número)

| # | Talento | jan | fev | mar | abr | mai | jun | jul | ago | set | out | Ano |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | Jonas Fernando Sulzbach | 0 | 0 | 12 | 12 | 21 | 9 | 7 | 0 | 2 | 2 | 65 |
| 2 | Tiago Medeiros | 4 | 5 | 5 | 2 | 4 | 4 | 2 | 2 | 2 | 3 | 33 |
| 3 | Gabriela Saporito | 0 | 0 | 1 | 2 | 7 | 6 | 5 | 1 | 0 | 1 | 23 |
| 4 | Everaldo Marques | 0 | 1 | 3 | 1 | 1 | 2 | 3 | 4 | 1 | 2 | 18 |
| 5 | Fred Bruno | 2 | 2 | 0 | 0 | 2 | 2 | 4 | 2 | 1 | 3 | 18 |
| 6 | Ana Maria Braga | 0 | 0 | 1 | 2 | 2 | 1 | 3 | 0 | 3 | 3 | 15 |
| 7 | Juliano Floss | 0 | 0 | 1 | 6 | 2 | 4 | 0 | 1 | 0 | 0 | 14 |
| 8 | Sol Vega | 0 | 9 | 2 | 2 | 0 | 1 | 0 | 0 | 0 | 0 | 14 |
| 9 | Pedro Bial | 1 | 1 | 4 | 0 | 0 | 2 | 3 | 0 | 0 | 2 | 13 |
| 10 | Angélica | 0 | 0 | 0 | 1 | 1 | 5 | 2 | 0 | 2 | 1 | 12 |
| | **Soma dos 10** | 7 | 18 | 29 | 28 | 40 | 36 | 29 | 10 | 11 | 17 | **225** |

Empate no corte: Angélica, Carol Maloca e Mariana Ximenes com 12 → Angélica entra pela ordem alfabética, `empate_fora`
= 2 (nota no pé do mapa). Empates internos (Everaldo Marques e Fred Bruno com 18; Juliano Floss e Sol Vega com 14) seguem
a mesma ordem alfabética. Pedro Bial passou de 12 (fim 22/10) para 13 pedidos.

### 0.5 Como reproduzir e conferência no BigQuery (somente SELECT, 26/10/2026)

1. **Corte e total do Início** (gold): `SELECT SUM(quantidade + quantidade_estimada) FROM
   gold_monday.gld_agenciamento_entrada_diaria WHERE data BETWEEN '2026-01-01' AND '2026-10-25'` → **5.556**.
2. **Divisão** (`app/sql/talentos_ano.sql`, `@fim = DATE '2026-10-25'`): Exclusivos 3.451 (62,1) · Não exclusivos 1.980
   (35,6; 119 do Squad) · Sem talento 125 (2,3) = **5.556 = Início** (sem aviso de atualização na tela).
3. **Top 10 × mês** (`app/sql/talentos_top.sql`, mesmas trocas: `{tabela_origem}` →
   `gglobo-viu-dados-hdg-prd.silver_monday.slv_agenciamento_2026_itens`, `@fim` → `DATE '2026-10-25'`): as tabelas da 0.4.
4. **Conferência independente** (sem os CTEs de ranking; conta por nome normalizado e mês só pela data de criação/R21):

```sql
WITH base AS (
  SELECT
    COALESCE(IF(data_de_saida < DATE(criado_em) AND data_de_entrada <= data_de_saida, data_de_entrada, DATE(criado_em)),
             DATE '1900-01-01') AS dia_criado,
    criado_em IS NULL AS sem_criado,
    LOWER(REGEXP_REPLACE(TRIM(talento), r'\s+', ' ')) AS chave,
    COALESCE(exclusivo, IF(criado_em IS NULL AND talentos_exclusivos IS NOT NULL, TRUE, NULL)) AS excl
  FROM `gglobo-viu-dados-hdg-prd.silver_monday.slv_agenciamento_2026_itens` WHERE state = 'active'
)
SELECT IF(excl, 'exclusivo', 'nao-exclusivo') AS grupo, chave,
  COUNTIF(NOT sem_criado AND dia_criado BETWEEN '2026-01-01' AND '2026-10-25') AS n_criado,
  COUNTIF(sem_criado) AS n_sem_criado,
  COUNTIF(NOT sem_criado AND dia_criado BETWEEN '2026-01-01' AND '2026-01-31') AS jan,
  COUNTIF(NOT sem_criado AND dia_criado BETWEEN '2026-05-01' AND '2026-05-31') AS mai,
  COUNTIF(NOT sem_criado AND dia_criado BETWEEN '2026-10-01' AND '2026-10-25') AS outu
FROM base
WHERE excl IS NOT NULL AND COALESCE(chave, '') NOT IN ('', 'squad de talentos')
GROUP BY grupo, chave
QUALIFY ROW_NUMBER() OVER (PARTITION BY grupo ORDER BY n_criado + n_sem_criado DESC, chave) <= 12
ORDER BY grupo, n_criado + n_sem_criado DESC;
```

   Resultado: os mesmos 10 nomes e totais nos dois grupos (282 … 120; 65 … 12), nenhum deles com card sem `criado_em`
   (`n_sem_criado` = 0), e jan/mai/out iguais aos do mapa (ex.: Tatiana Machado 28 / 44 / 19; Ticiane Pinheiro 0 / 27 /
   4; Jonas Fernando Sulzbach 0 / 21 / 2); 11º e 12º: Milton Cunha 117 e Giovanna Pitel 116 (exclusivos); Carol Maloca
   e Mariana Ximenes 12 (não exclusivos, empate com o 10º).
5. **Um talento por pedido:** `COUNTIF(REGEXP_CONTAINS(talento, r'[,;/]'))` = 0 nos 5.565 cards ativos; 10 cards com
   " e " no nome são duplas (ex.: "Mauricio e Michele", "Cesar Menotti e Fabiano").

### 0.6 Validação

- **Testes** (`tests/test_talentos_d50.py`, dados sintéticos): top 10 por recorte ordenado, com soma e total do recorte;
  soma dos meses = total do talento e nov/dez vazios com corte em 20/10 (outubro parcial; mês fechado sem parcial);
  mapa some se os meses não fecham ou sem colunas mensais; resposta por recorte (frases, números, concordância, sem
  número sem ranking); barra com o recorte destacado; seletor com 3 links e `aria-current`; página filtrada (mapa só
  com o grupo); tabela acessível (caption, `scope`, "sem dado", número em cada célula passada, sem `style=""`); abas
  levam o filtro; movimento sem esconder números. `tests/conftest.py` com o top 10 mensal nos três recortes; testes
  antigos ajustados (`test_portal.py`, `test_revisao_20261025.py`).
- **Capturas** (servidor local, carga de 26/10) em 1920×1000, 1440×900, 1280×800 e 390 px nos três recortes: sem
  rolagem no palco largo, sem rolagem lateral no celular, rodapé datado presente.


## Revisão vigente — 24/10/2026

Ver [revisão](../historico/REVISAO_2026-10-24.md): 3.435 + 1.955 + 130 = 5.520; top 10 1.802/221. Consulta adicional confirmou zero registros com nome entre os 130 sem classificação. SQL agora respeita `TAB_TALENTO_ORIGEM`; ranking tem agrupamento exato e determinístico. Cache considera origem e corte Golden; resultado vazio é válido, fontes divergentes suspendem indicadores. Ranking e denominador precisam compartilhar parâmetros e versão da origem. Dicas cabem na largura disponível e permitem rolagem. Fonte ainda limitada ao board configurado de 2026: PD20 registra continuidade multianual, além de PD01/PD02a. Sem comparação anual nova.

> **ENTREGUE em 24/10/2026 (D31).** Divisão anual de 2026 conciliada com o Início (5.520 = 5.520) e dicas com os 10
> talentos mais pedidos de cada grupo (T6), conferidas no BigQuery com a carga de 23/10/2026 (dados até 22/10). Lê a
> silver por exceção (D30-b) até a PD01.

## 1. Identificação

| Item | Valor |
|---|---|
| Rota | `/viu-agenciamento/talentos` (1 slide, nível Gerencial; sem máscara na tela) |
| Cálculo | `app/apresentacoes/gestao_orcamentos/talentos/calculos.py`: `divisao()` (T1–T5), `top_por_grupo()` (T6, com os meses), `seletor()` (T7), `heroi()` (T8), `barra()` (T9) e `mapa()` (T10); rótulos e classes em `GRUPOS`; parcelas por `entrada.calculos._pcts` (E8c) |
| Montagem | `app/apresentacoes/gestao_orcamentos/apresentacao.py`, `montar_talentos()`: total e ano do Início (`entrada.entrada`), divisão e top 10 |
| Leitura | `app/dados.py`: `talentos = Consulta("Talentos (silver 2026)", config.TAB_TALENTO_ORIGEM, "talentos_ano.sql", _fim_da_entrada, ...)` e `talentos_top = Consulta("Talentos mais pedidos (silver 2026)", ..., "talentos_top.sql", _fim_da_entrada, ...)`; recarga pelo metadado da silver; `estado()` só acusa falha de leitura (a silver não segue a agenda da gold) |
| SQL | `app/sql/talentos_ano.sql` (divisão) e `app/sql/talentos_top.sql` (top 10 por recorte — todos, exclusivos, não exclusivos — mês a mês, D50); parâmetro `@fim` de `_fim_da_entrada()` = véspera do `_processado_em` da gold de entradas (em São Paulo) |
| Template | `app/apresentacoes/gestao_orcamentos/talentos/template.html` |
| Estilo | `app/static/estilo.css`, blocos "Talentos (D30)" (barra, lista, animação), "T6" (dicas, sem uso desde a D50) e "Talentos, D50" (seletor, resposta, barra fina, mapa, movimento) |
| Testes | `tests/test_portal.py` (`test_talentos_divisao_sem_nomes`), `tests/test_revisao_20261025.py` (aviso de bases divergentes, empate) e `tests/test_talentos_d50.py` (T7–T10) |
| Tabela | **exceção D30-b:** `gglobo-viu-dados-hdg-prd.silver_monday.slv_agenciamento_2026_itens` (`TAB_TALENTO_ORIGEM`); total conciliado com `gold_monday.gld_agenciamento_entrada_diaria` (`TAB_ENTRADA`) |
| Carga de referência | gold `entrada_diaria` `_processado_em` 23/10/2026 20:23 UTC (dados até 22/10); silver `_processado_em` 23/10/2026 11:05 UTC; `@fim` = 22/10/2026. Top 10 reconferido no BigQuery em 24/10/2026 com o mesmo `@fim` |

### 1.1 Tabelas e colunas consumidas

**Vigente desde 27/10/2026 (D57: o site só lê a gold; fim da exceção D30-b).** Conferido com `app/dados.py`; código
antigo (silver) × novo (gold) sobre a mesma carga real (27/10, 11:11): os 3 filtros iguais (frase, barra, top 10, mapa,
corrida).

| Gold (BigQuery) | Tipo · `dados.` | Colunas usadas | Para quê |
|---|---|---|---|
| `gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_2026_talentos_ano` (`TAB_TALENTOS_ANO`) | tabela · `talentos` | `ano`, `categoria`, `n`, `total`, `dos_quais_squad`, `_processado_em` | divisão do ano (T1–T5) |
| `gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_2026_talentos_ranking` (`TAB_TALENTOS_RANKING`) | tabela · `talentos_top` | `grupo`, `talento`, `n`, `ultimo_pedido`, `empate_fora`, `talentos_grupo`, `mes`, `n_mes`, `pos`, `_processado_em` | top 10, mapa e corrida (T6–T10, D51) |
| `gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_entrada_diaria` (`TAB_ENTRADA`) | tabela · `entrada` | `data`, `quantidade`, `quantidade_estimada`, `_processado_em` | total do Início e data de corte (T5: mesmo total e mesmo dia de carga) |

As regras (data do pedido, exclusividade, Squad, nomes, ranking) são da gold: fichas
`docs/tabelas/gld_agenciamento_2026_talentos_ano.md` e `..._talentos_ranking.md` no PPD-GOLDEN-AGENCIAMENTO-MONDAY. SQL
para reproduzir: `SELECT * FROM` cada tabela. As SQL de `app/sql/` citadas abaixo e nas seções 0.5 e 6 estão em
`_descartados/2026-10-27/app/sql/` (registro).

Estado de 24/10/2026 (registro; exceção D30-b):

| Tabela (nome completo no BigQuery) | Como é lida | Colunas usadas | Para quê |
|---|---|---|---|
| `gglobo-viu-dados-hdg-prd.silver_monday.slv_agenciamento_2026_itens` (`TAB_TALENTO_ORIGEM`, exceção D30-b) | `app/sql/talentos_ano.sql` e `app/sql/talentos_top.sql` (consultas agregadas, parâmetro `@fim`); recarga pelo metadado da tabela | `state` (R5), `criado_em` (R1, T2), `data_de_entrada` e `data_de_saida` (R21, R2), `exclusivo` e `talentos_exclusivos` (T2), `talento` (T3, T6) | divisão (T1–T5) e top 10 (T6) |
| `gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_entrada_diaria` (`TAB_ENTRADA`) | em memória (`dados.entrada`, `COLUNAS_ENTRADA`) | `data`, `quantidade`, `quantidade_estimada` (total do Início, T5); `_processado_em` (`@fim` = véspera em São Paulo) | conciliação e data de corte |

Colunas devolvidas pelas SQL ao site: divisão `ano, categoria, n, total, pct, dos_quais_squad` (o site não usa `pct`);
top (D50) `grupo, talento, n, ultimo_pedido, empate_fora, talentos_grupo, mes, n_mes` e, desde a D51, `pos` (lugar no ano; linhas com `pos` > 10 = quem passou pelos 10 do acumulado, só para a corrida do play) (uma linha por talento e mês com pedido; chave `grupo, talento, mes`). Reconferido em 24/10/2026 no BigQuery (mesma silver de 23/10 11:05 UTC, `@fim`
= 22/10): 3.435 / 1.955 (119 do Squad) / 130.

## 2. Pergunta e resposta esperada (estado D31; vigente: seção 0)

**Título (h2, em pergunta, padrão do portal):** "Como a demanda se divide entre talentos exclusivos e não exclusivos?"

O leitor precisa sair sabendo: **62% da demanda de 2026 se concentra nos talentos exclusivos**; 36% vai para não
exclusivos e 2% não tem talento informado, **sobre os mesmos 5.520 pedidos do Início**. Quem quiser
o detalhe passa o mouse (ou foca pelo teclado) no grupo e vê os 10 talentos mais pedidos, com a data do pedido mais
recente de cada um, e quanto esses 10 concentram do grupo.

Escopo: só o ano corrente, **sem mês e sem 2025** (D30, decisão do Caio de 23/10). **Nomes de talentos aparecem nas
dicas** por decisão do Caio de 24/10, revendo a de 23/10 que não os mostrava.

## 3. O que aparece na tela (estado D31, carga de 23/10/2026; vigente: seção 0)

| Elemento | Texto exato / comportamento | Regra |
|---|---|---|
| Sobretítulo | "Gerencial" | — |
| Título | "Como a demanda se divide entre talentos exclusivos e não exclusivos?" (Playfair, `secao_atual.pergunta`) | — |
| Número e frase | "**62%** da demanda do ano se concentra nos talentos exclusivos." O número conta de 0 a 62 na entrada. O grupo é o maior entre exclusivos e não exclusivos (`principal`); acima de 50% o verbo é "se concentra nos talentos [grupo]"; até 50%, "**X%** da demanda do ano vai para os talentos [grupo]." Nada é fixo no template | T1, T2, T4 |
| Conciliação | Só quando as bases divergem (total ≠ Início ou outro dia de corte): os números **continuam na tela** (decisão 10, 25/10/2026; antes a página era bloqueada) e, sob a frase, o aviso `role="status"`: "A divisão por talento está sendo atualizada: a base de talentos soma N pedidos e o Início, M. As bases atualizaram em horários diferentes; tente de novo em alguns minutos." (com corte diferente: "…a base de talentos ainda usa outro dia de corte. …"; TAL-D1). A divergência também vai ao log do servidor. Na carga de referência **não aparece** (5.520 = 5.520) | T5 |
| Título do gráfico | "Distribuição dos pedidos por vínculo do talento" (`figcaption`) | — |
| Barra 100% | Três partes em HTML, larguras pelo `<style nonce>` da página (`--w` = n ÷ total × 100, 3 casas; a CSP proíbe `style=""`), 3 px entre partes, cantos arredondados nas pontas. **Dentro de cada parte**: o % e, embaixo, bem pequeno, a quantidade: "62%" / "3.435 pedidos"; "36%" / "1.955 pedidos"; "2%" / "130". Cores da página Início: Exclusivos `--t-mercado` (marinho), Não exclusivos `--t-proativo` (azul médio), Talento não informado `--t-sem-tipo` (tom claro, texto em tinta escura). A parte de **Talento não informado tem largura mínima legível**: desproporção visual consciente, pedida pelo Caio, para que "2%" e "130" caibam; as outras duas encolhem um pouco em relação à proporção exata. A barra é `aria-hidden` (ver lista oculta) | T4 |
| Legenda | Uma linha embaixo da barra com a cor e o nome dos três grupos: **Exclusivos**, **Não exclusivos** e **Talento não informado** (sem números). Só as duas primeiras abrem dica (T6). A identidade nunca depende só da cor: o nome está na legenda e os números dentro da barra | T2 |
| Lista oculta (leitor de tela) | Lista visualmente oculta com os três grupos, pedidos e %: "Exclusivos: 3.435 pedidos, 62%"; "Não exclusivos: 1.955 pedidos, 36%"; "Talento não informado: 130 pedidos, 2%" | T2, T4 |
| Animação de entrada | As partes da barra se revelam da esquerda para a direita, uma após a outra (80 ms entre partes; termina em 1,12 s); o número grande já está no valor final desde o 1º quadro (D49, 26/10/2026: a contagem saiu, mostrava "24%" com a barra em 62%). Só com `prefers-reduced-motion: no-preference`; com "menos movimento", tudo aparece parado. (A lista visível, que subia linha a linha, saiu com a troca pela legenda) | — |
| Dica de Exclusivos (T6) | Abre pela legenda de Exclusivos. Com o mouse, **só pelo quadradinho da cor**; o nome é texto comum, sem sublinhado. Pelo teclado, o nome segue focável (Tab) e abre a dica; no toque, o nome abre e fecha; Esc fecha. Classe própria `dica-top` (sem a genérica `dica-tipos`). Abre **acima da legenda, sobre a barra, alinhada à direita**, no padrão da dica "Novos pedidos" do Início. Título: "**Os 10 exclusivos mais pedidos**" (Playfair, centralizado, fio azul). Duas colunas (1º–5º e 6º–10º), cada uma com o cabeçalho "Talento · Pedidos · Último"; linha = posição, nome, pedidos, data "dd/mm" do pedido mais recente. Largura = maior nome + 10% (não estica). Fechamento: "**Juntos, 1.802 pedidos: 52% dos exclusivos**" | T6 |
| Dica de Não exclusivos (T6) | Igual, pela legenda de Não exclusivos, com o título "**Os 10 não exclusivos mais pedidos**", no fim da lista a nota de empate "**10º lugar empatado com mais 2 talentos (12 pedidos cada)**" (decisão 11, 25/10/2026; só aparece quando há empate no corte), o fechamento "**Juntos, 221 pedidos: 11% dos não exclusivos**" e a nota "Nomes como registrados no board; Squad de Talentos (grupo) fora". Por decisão, a dica não cita o tamanho do Squad nem o número de nomes de cada grupo. Nomes numa linha só no palco largo (C1, 25/10/2026: regras soltas de quebra, no meio do bloco do Atendimento, desfaziam o T6 e partiam "Chaiany Pinto / Andrade" e "Jonas Fernando / Sulzbach"; a quebra ficou só no palco < 860 px) | T3, T6 |
| Talento não informado | Na barra, na legenda e na lista oculta, mas sem dica (não há nome a ranquear) | T2 |
| Tela estreita (palco < 860 px) | A dica ocupa a largura do bloco, numa coluna só (o cabeçalho da 2ª coluna some) | — |
| Rodapé | "Dados até … · atualizados em …" (herdado de `apresentacao.html`) | — |
| Sem carga | Lâmina em máscara "A divisão por talento ainda não carregou" / "A contagem por talento está indisponível ou ainda não concilia com o período do Início." Só quando a consulta não devolve o ano (bases divergentes não bloqueiam mais: ver Conciliação). Sem o top 10 (consulta vazia ou de outra carga que a divisão), os nomes dos grupos ficam sem dica | — |

**O que saiu da tela em 24/10 (decisões do Caio):** o bloco "Aguardando dados" (PD01–PD03 ficam só em "O que falta"), a
etiqueta de período "jan–out 2026" (tela e dica), a linha fixa de quantidade e a lista visível com números sob a barra
(trocada pela legenda sem números e pelos números dentro da barra).

## 4. Regras

| ID | Regra | Fórmula / onde | Decidido |
|---|---|---|---|
| T1 | Base = os mesmos pedidos do Início | silver 2026, `state = 'active'` (R5); dia = `data_de_entrada` se cadastro retroativo (`data_de_saida < DATE(criado_em)` e `data_de_entrada <= data_de_saida`, R21), senão `DATE(criado_em)` (R1); sem `criado_em` = `data_de_saida` − 5 dias úteis (R2, feriados fixos); de 1º/jan até `@fim` (R4) | Caio, 23/10/2026 (D30-b) |
| T2 | Exclusividade **na data do pedido**; sem talento = grupo próprio, sempre visível, rótulo "Talento não informado" | `COALESCE(exclusivo, IF(criado_em IS NULL AND talentos_exclusivos IS NOT NULL, TRUE, NULL))`: TRUE = Exclusivos, FALSE = Não exclusivos, NULL = Sem talento (regras 53/56/60/63b da silver) | Caio, 23/10/2026; rótulo em 24/10 |
| T3 | "Squad de Talentos" é um grupo, não uma pessoa: conta em não exclusivos e fica fora do ranking | regra 60 da silver; `dos_quais_squad` na divisão; `NOT IN ('', 'Squad de Talentos')` no top | Caio, 23/10/2026 |
| T4 | Parcelas inteiras que fecham em 100 pelo maior resto; grupo principal = o maior entre exclusivos e não exclusivos; frase pelo % | `_pcts` (E8c): base = piso(n × 100 ÷ total), pontos que faltam vão aos maiores restos; `principal = max(exclusivos, não exclusivos, por n)`; pct > 50 → "X% da demanda do ano se concentra nos talentos [grupo]."; senão "X% da demanda do ano vai para os talentos [grupo]." | Claude, 23/10; frase do Caio, 24/10 |
| T5 | Conciliação com o Início | `diferenca = total da divisão − total do Início`; ≠ 0, ou corte da consulta ≠ `@fim` do Início → números na tela com o aviso "está sendo atualizada" e a diferença (antes da decisão 10 a montagem bloqueava a página); registro em log | Claude, 23/10/2026; decisão 10 (25/10/2026, como dizia a D30-b) |
| T6 | Top 10 por grupo (exclusivos e não exclusivos) nas dicas | `talentos_top.sql`: mesma base de T1/T2, só exclusividade conhecida e nome preenchido; agrupa por `LOWER(REGEXP_REPLACE(TRIM(talento), r'\s+', ' '))` (maiúsculas e espaços repetidos), mostra a grafia mais frequente (`ARRAY_AGG(talento ORDER BY n DESC, talento LIMIT 1)`, empate alfabético; TAL-D5, 25/10/2026: a ficha citava `APPROX_TOP_COUNT`, que não é o que a SQL faz); `n` = pedidos; `ultimo_pedido` = `MAX(dia)`; 10 primeiros por `n` desc, **desempate alfabético** (`ROW_NUMBER() … ORDER BY n DESC, talento`); `empate_fora` = quantos ficaram fora com o mesmo `n` do 10º (decisão 11). No site: soma dos 10 e `round(100 × soma ÷ total do grupo)`, total do grupo vindo da divisão (T1); "Último" em `dd/mm` ("–" se vazio) | Caio, 24/10/2026 |
| T7 | Seletor Todos / Exclusivos / Não exclusivos (`?talentos=`), filtrando a página inteira | `FILTROS`, `seletor()`; valor do botão = pedidos do ano do recorte | gerente do Caio, 26/10/2026 (D50) |
| T8 | Resposta por recorte: Todos = % do maior grupo do ano; Exclusivos / Não exclusivos = % do grupo nos 10 talentos mais pedidos do grupo | `heroi()`; seção 0.3 | D50 |
| T9 | Barra do ano sempre com os três grupos; grupo do recorte destacado | `barra()` | D50 |
| T10 | Mapa de calor: top 10 do recorte × jan–dez; mês do pedido = mês da data de entrada (T1); soma dos meses = total do ano; meses futuros sem número; tom pelo maior mês | `talentos_top.sql`, `mapa()`; seção 0.3 | D50 |
| T11 | Coluna dos nomes com a largura do maior nome do recorte + ~10%, sem reticências (classe `mapa-nomes-N`) | `largura_nomes()`; seção 0-D51 | Caio, 26/10/2026 (D51) |
| T12 | Corrida do play: ranking pelo acumulado entre os 10 do ano e quem esteve entre os 10 do acumulado no fim de algum mês; desempate = lugar no ano | `talentos_top.sql` (`pos`), `top_por_grupo()`, `mapa()`; seção 0-D51 | Caio, 26/10/2026 (D51) |

## 5. Memória de cálculo (fim = 22/10/2026)

### 5.1 Divisão (T1–T5)

| Grupo | Pedidos | Conta | Tela |
|---|---:|---|---:|
| Exclusivos | 3.435 | 3.435 × 100 ÷ 5.520 = 62,23 → base 62, resto 0,23 | **62%** |
| Não exclusivos (inclui 119 do Squad) | 1.955 | 35,42 → base 35, resto 0,42 (maior) → +1 | **36%** |
| Talento não informado | 130 | 2,36 → base 2, resto 0,36 | **2%** |
| **Total** | **5.520** | bases somam 99; o ponto que falta vai ao maior resto | 100% |

Grupo principal: exclusivos (3.435 > 1.955); 62 > 50 → "62% da demanda do ano se concentra nos talentos exclusivos."

Larguras da barra: proporcionais (62,23 / 35,42 / 2,36) com largura mínima legível na parte de Talento não informado; o
que está escrito (62% / 36% / 2% e 3.435 / 1.955 / 130) não muda com esse ajuste visual.

A SQL também devolve `pct` com uma casa (62,2 / 35,4 / 2,4, maior resto em décimos); o site **não usa** essa coluna:
recalcula os inteiros pela T4 para seguir o padrão das outras telas.

**Conciliação com o Início (5.520 = 5.520, T5):**

| Passo | Pedidos |
|---|---:|
| Silver 2026, `state = 'active'`, data pela R21/R1 entre 01/01 e 22/10 | 5.515 |
| + cards sem `criado_em` com data estimada (R2), todos em jan–jun/26 | 5 |
| **= gold `entrada_diaria`, 2026 (`quantidade + quantidade_estimada`)** | **5.520** |

Bate porque a gold de 2026 só recebe cards do board 2026 (os boards 2024/2025 não têm card com data em 2026) e aplica as
mesmas R1/R2/R4/R5/R21. Os 9 cards ativos do board 2026 cuja data pela R21 cai em 2025 ficam fora de 2026 nas duas bases
(R6: conta pela data, não pelo board). Mês a mês (só diagnóstico, não vai à tela) a regra também bate (jan 374 … out 508).

**Cobertura de `exclusivo` em 2026:** preenchido em 5.385 + 5 completados pela T2 = 5.390 (**97,6%**); vazios = 130, todos
sem talento (nem `talentos_exclusivos`, nem `interveniencia`); 45 dos 130 são de outubro (atraso no preenchimento).

### 5.2 Top 10 (T6)

| | Exclusivos | Não exclusivos |
|---|---|---|
| Total do grupo (da divisão) | 3.435 | 1.955 (dos quais 119 do Squad, fora do ranking) |
| Nomes distintos no ranking | 39 (soma 3.435: nenhum pedido exclusivo sem nome) | 928 depois de agrupar maiúsculas e espaços (soma 1.836 = 1.955 − 119) |
| Pedidos do 1º ao 10º | 281 / 242 / 206 / 189 / 186 / 172 / 151 / 130 / 125 / 120 | 65 / 33 / 23 / 18 / 16 / 14 / 14 / 14 / 12 / 12 |
| Soma dos 10 | **1.802** | **221** |
| % do grupo | 1.802 ÷ 3.435 = 52,46% → **52%** | 221 ÷ 1.955 = 11,30% → **11%** |
| Fechamento na dica | "Juntos, 1.802 pedidos: 52% dos exclusivos" | "Juntos, 221 pedidos: 11% dos não exclusivos" |
| Coluna "Último" | de 20/10 a 22/10 entre os 10 | de 10/06 a 22/10 entre os 10 |

**Empate no corte (T6, decisão 11; reconferido no BigQuery em 25/10/2026, `@fim` = 22/10):** nos não exclusivos, **4
talentos têm 12 pedidos** (posições 9 a 12 pelo `RANK()`): pela ordem alfabética, Angélica e Carol Maloca entram;
Mariana Ximenes e Pedro Bial ficam fora. A dica termina com "10º lugar empatado com mais 2 talentos (12 pedidos cada)".
Nos exclusivos não há empate no corte (120 no 10º, 116 no 11º). Também há empate interno (Ana Maria Braga, Juliano Floss e
Sol Vega com 14, `RANK` 6), sem efeito no corte.

A coluna "Último" é a data do pedido mais recente do talento no período: `MAX` da data do pedido, pela mesma regra de data
da T1 (não é a data da última entrega nem da última movimentação do card).

## 6. Como reproduzir

As SQL do site são os próprios arquivos (somente leitura). No console, trocar `@fim` por `DATE '2026-10-22'` (ou pela
véspera do `_processado_em` da gold de entradas no dia).

**6.1 Conferir `@fim` e o total do Início**

```sql
SELECT MAX(_processado_em) carga, MAX(data) ultimo_dia,
       SUM(quantidade + quantidade_estimada) pedidos_2026
FROM `gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_entrada_diaria`
WHERE data BETWEEN '2026-01-01' AND '2026-10-22'
-- esperado: 2026-10-23 20:23 UTC | 2026-10-22 | 5.520
```

**6.2 Divisão: `app/sql/talentos_ano.sql`** com `@fim = DATE '2026-10-22'`. Esperado:

| ano | categoria | n | total | pct | dos_quais_squad |
|---|---|---:|---:|---:|---:|
| 2026 | Exclusivos | 3.435 | 5.520 | 62,2 | 0 |
| 2026 | Não exclusivos | 1.955 | 5.520 | 35,4 | 119 |
| 2026 | Sem talento | 130 | 5.520 | 2,4 | 0 |

**6.3 Top 10: `app/sql/talentos_top.sql`** com `@fim = DATE '2026-10-22'`: 20 linhas (`grupo`, `talento`, `n`,
`ultimo_pedido`, `empate_fora`), 10 por grupo, com os `n` da seção 5.2; `empate_fora` = 0 nos exclusivos e **2** nos não
exclusivos (25/10/2026). Para ver o empate com `RANK()`, trocar o `SELECT` final por
`SELECT grupo, pos, talento, n, RANK() OVER (PARTITION BY grupo ORDER BY n DESC) AS rank_n FROM ranqueado WHERE pos <= 12
ORDER BY grupo, pos` (esperado nos não exclusivos: posições 9–12 com `n` = 12 e `rank_n` = 9). Para conferir sem expor nomes (como feito em 24/10), trocar o
`SELECT` final do arquivo por:

```sql
, top AS (
  SELECT grupo, n, ultimo_pedido,
         ROW_NUMBER() OVER (PARTITION BY grupo ORDER BY n DESC, talento) AS pos
  FROM ranking
  QUALIFY pos <= 10
)
SELECT grupo, STRING_AGG(CAST(n AS STRING), ' / ' ORDER BY pos) AS ns, SUM(n) AS soma10,
       MIN(ultimo_pedido) AS min_ult, MAX(ultimo_pedido) AS max_ult
FROM top
GROUP BY grupo
-- esperado: exclusivo | 281 / 242 / 206 / 189 / 186 / 172 / 151 / 130 / 125 / 120 | 1.802 | 2026-10-20 | 2026-10-22
--           nao-exclusivo | 65 / 33 / 23 / 18 / 16 / 14 / 14 / 14 / 12 / 12 | 221 | 2026-06-10 | 2026-10-22
```

Totais de controle (mesma base `pedidos` da SQL, filtrada a 2026 até `@fim`): por grupo, `COUNT(*)` = 3.435 / 1.955;
pedidos exclusivos com nome vazio = 0; `talento = 'Squad de Talentos'` = 119 (só em não exclusivos).

Plano B (não usado na tela; só para explicar diferenças): a gold do SLA no passo 1 dá 2.086 / 1.007 / 21 = 3.114
projetos (67,0 / 32,3 / 0,7%), com exclusividade idêntica à da silver (0 divergências por `projeto_id`), mas só cobre
pedidos com ciclo completo pelo log. Não é "divisão da demanda".

**6.4 Talentos com os dois vínculos e cards com `talentos_exclusivos` preenchido e `exclusivo = FALSE`** (TAL-D2/D3,
25/10/2026). Reaproveita as CTEs `feriados` e `pedidos` de `talentos_top.sql` (acrescentando `i.talentos_exclusivos` ao
`SELECT` de `pedidos`) e troca o fim por:

```sql
, ano AS (SELECT * FROM pedidos WHERE dia BETWEEN '2026-01-01' AND '2026-10-22'),
dois AS (
  SELECT LOWER(REGEXP_REPLACE(TRIM(talento), r'\s+', ' ')) AS chave,
         ANY_VALUE(REGEXP_REPLACE(TRIM(talento), r'\s+', ' ')) AS talento,
         COUNTIF(exclusivo) AS excl, COUNTIF(NOT exclusivo) AS nao_excl
  FROM ano WHERE exclusivo IS NOT NULL AND COALESCE(TRIM(talento), '') != ''
  GROUP BY chave HAVING excl > 0 AND nao_excl > 0)
SELECT 'dois_vinculos' AS item, talento AS detalhe, excl AS a, nao_excl AS b FROM dois
UNION ALL
SELECT 'cards_excl_preenchido_e_falso', 'total', COUNT(*), COUNTIF(LOWER(TRIM(talento)) = 'squad de talentos')
FROM ano WHERE talentos_exclusivos IS NOT NULL AND exclusivo = FALSE
ORDER BY item, a + b DESC
-- esperado (25/10/2026): 7 talentos, 356 pedidos — Viviane Araújo 81/6, Jonas Fernando Sulzbach 3/65, Angélica 43/12,
-- Sofia Miranda 41/3, Ana Paula Xongani 37/2, Mariana Spinelli 23/9, Luana Maluf 26/5 (exclusivo/não exclusivo);
-- cards com talentos_exclusivos preenchido e exclusivo = FALSE: 25, dos quais 6 do Squad de Talentos
```

**6.5 Datas das cargas** (para conferir a coerência): silver `MAX(_processado_em)` = 23/10/2026 11:05:35 UTC (08:05 BRT)
e `modified` da tabela = 23/10/2026 11:34:25 UTC (**08:34 BRT**, via `silver_monday.__TABLES__.last_modified_time`); gold
de entradas `_processado_em` = 23/10/2026 20:23:49 UTC (17:23 BRT).

## 7. Validações feitas

| Data | O quê | Resultado |
|---|---|---|
| 23/10/2026 | Divisão anual pela SQL da silver × total da gold de entradas (só SELECT, cargas da seção 1) | ✅ 3.435 + 1.955 + 130 = 5.520 = Início; mês a mês igual à gold |
| 23/10/2026 | Coluna de exclusividade: `exclusivo` (na data do pedido) × situação atual | ✅ escolhida a da data do pedido: com a atual, ~254 pedidos de 7 talentos que mudaram de exclusividade em 2026 passariam a não exclusivos e o passado mudaria a cada saída do quadro |
| 23/10/2026 | Silver × gold do SLA (passo 1), por `projeto_id` | ✅ exclusividade idêntica nos 3.114 projetos em comum |
| 24/10/2026 | Top 10 no BigQuery (SELECT, `@fim` = 22/10): soma do ranking × divisão | ✅ exclusivos: 39 nomes somam 3.435 (= divisão), 0 pedidos exclusivos sem nome; top 10 = 1.802 (52%). Não exclusivos: 1.836 + 119 do Squad = 1.955 (= divisão); top 10 = 221 (11%) |
| 24/10/2026 | "Último" = `MAX(dia)` pela regra de data da T1 | ✅ exclusivos 20/10–22/10; não exclusivos 10/06–22/10; nenhuma data depois de `@fim` |
| 24/10/2026 | Teste sintético `test_talentos_divisao_sem_nomes`: frase "…da demanda do ano se concentra nos talentos exclusivos.", "Talento não informado" (e nunca "Sem talento") e também na legenda, dicas dos dois grupos ligadas por `aria-describedby`, nomes e data do último pedido, "Juntos, N pedidos", nota do Squad, sem etiqueta de período, sem "Aguardando dados", T4 (soma 100) e T5 (diferença −7) | ✅ 89 testes passando |
| 24/10/2026 | Tela em 1440×900 e 390 px (sessão de ajustes com o Caio) | ✅ cabe na lâmina, sem rolagem lateral; estado final aprovado pelo Caio como entregue |
| 25/10/2026 | BigQuery (só SELECT, `@fim` = 22/10): top 10 com `empate_fora` e `RANK()`; dois vínculos; cards com `talentos_exclusivos` e `exclusivo = FALSE`; datas da silver | ✅ não exclusivos: 4 com 12 (pos. 9–12), `empate_fora` = 2; exclusivos sem empate no corte; 7 talentos / 356 pedidos; 25 cards (6 do Squad); silver 11:05 UTC processada, 08:34 BRT `modified`; top 10 inalterado (1.802 / 221) |
| 25/10/2026 | Dicas em 1440×900 e 1800×980 com o mouse nos quadradinhos (C1) | ✅ nomes numa linha só (nenhum quebrado), dica dentro da lâmina (borda esquerda 825 px > 232 px do menu); 390 px sem rolagem lateral |
| 25/10/2026 | Testes `test_revisao_20261025.py` (C1, decisões 10 e 11, TAL-D9) | ✅ 135 testes passando |

## 8. Limites e pontos de atenção

- **Exceção D30-b:** a tela (divisão e top 10) lê a silver. Sai quando a exclusividade chegar à gold de entradas (PD01) e
  o ranking dos exclusivos passar a ser lido de lá (PD02a). Antes de publicar, a conta de serviço precisaria de leitura
  na silver: preferível encerrar a exceção antes da fase 3.
- **Grafias dos não exclusivos:** o nome é digitado no board. O agrupamento só junta diferenças de maiúsculas e espaços;
  apelidos, acentos e erros de digitação continuam separados (928 nomes). O top 10 dos não exclusivos pode subestimar
  um talento com várias grafias. Limpeza do cadastro: PD02b (Equipe de Talentos). A dica avisa "Nomes como registrados
  no board".
- **Squad de Talentos:** 119 pedidos contam em não exclusivos (regra 60 da silver, decisão de 19/10 que pode mudar) e
  ficam fora do ranking; o % do top 10 é sobre os 1.955, Squad incluído.
- **Descompasso de carga:** silver (11:05 UTC) e gold (09:00 de Brasília, reprocessada à tarde em 23/10) podem atualizar
  em horários diferentes; aí os números ficam na tela com o aviso "está sendo atualizada" e a diferença (T5, decisão 10).
  O top 10 usa o total do grupo da divisão.
- **Rodapé (TAL-D7):** "Dados até … · atualizados em …" data a **gold de entradas** (fonte do `@fim`, pelo
  `_processado_em`, INI-D1), não a silver; a coerência entre as duas é garantida pela T5 e pelo corte `@fim` igual ao do
  Início (`_fim_da_entrada`, que desde 25/10/2026 usa a mesma regra E3 do Início, `data_carga`, com `utc=True` e nulos
  ignorados: TAL-D9).
- **Talentos com os dois vínculos no ano (TAL-D2, decisão 12):** 7 talentos, **356 pedidos**, contam em exclusivos ou não
  exclusivos conforme a data do pedido (T2): Viviane Araújo 81/6, Jonas Fernando Sulzbach 3/65 (exclusivo intercalado),
  Angélica 43/12, Sofia Miranda 41/3, Ana Paula Xongani 37/2, Mariana Spinelli 23/9, Luana Maluf 26/5. Correção de
  cadastro levada à gold (`docs/lembretes_gold.md`, item de 25/10/2026). SQL na seção 6.4.
- **Cards com `talentos_exclusivos` preenchido e `exclusivo = FALSE` (TAL-D3):** 25 em 2026, dos quais 6 do Squad de
  Talentos (um Squad formado só por exclusivos conta como não exclusivo). Mesma pendência (lembretes; PD01/PD02b/PD03).
- **Calendário simplificado na data estimada:** as SQL usam só feriados fixos; afeta só os 5 cards sem `criado_em`
  (podem trocar de mês, não de ano). Se a gold mudar R2, R4, R5 ou R21, as SQL mudam junto.
- **Regras da silver movem pedidos entre grupos:** mudança no quadro de Talentos ou no dicionário de nomes.
- **"Talento não informado" concentrado no mês corrente** (45 dos 130 em outubro): encolhe com o preenchimento; a
  divisão oscila alguns décimos de carga a carga.
- **Barra com largura mínima na parte de Talento não informado:** a barra deixa de ser exatamente proporcional (decisão
  do Caio, para os 2% serem legíveis); os números escritos são os exatos. Não usar a barra para medir proporções.
- O % do top 10 usa `round()` do Python (empate exato em ,5 vai ao par); com estes números não há empate.
- **Empate no 10º lugar:** a lista mostra 10 nomes pelo desempate alfabético e avisa quantos ficaram fora com o mesmo
  número (decisão 11); hoje 2 não exclusivos com 12 pedidos (seção 5.2).
- Conta **pedidos**, não contratações nem receita; não comparar com 2025 (campo e regra diferentes, PD03).
- A fatia de exclusivos no Prazo (slide 3, 1.635 de 2.425 = 67%) é outra base (só entregues com histórico): não "bate"
  com os 62% daqui.

## 9. Decisões

D30 (portal; escopo sem mês e sem 2025), D30-b (exceção da silver), **D31 (página entregue, 24/10/2026, com as decisões
do Caio na ordem em que foram tomadas)** e T1–T6; **D50 (26/10/2026, pedido do gerente do Caio: seletor, resposta por
recorte e mapa mês a mês; revisa a D31 e o "sem mês" da D30)** e T7–T10. Pendências: PD01, PD02a, PD02b, PD03 (`pendencias.py`, ficha
[o_que_falta.md](o_que_falta.md)).

## 10. Histórico da página

| Data | Mudança |
|---|---|
| 31/10/2026 | **Auditoria do Codex, F13:** a concentração dos 10 talentos (`top_por_grupo`, `pct`) passa a arredondar meio para cima (`formato.pct_inteiro`), como Demanda e o resto do portal: só o empate exato muda (1 de 8 = 13%, antes 12% pelo `round()`). Parcelas da divisão do ano continuam pelo maior resto |
| 23/10/2026 | Página criada (D30, D30-b): divisão anual de 2026 com conciliação ao Início, máscara compacta PD01–PD03. Conferida no BigQuery: 3.435 / 1.955 / 130 = 5.520 |
| 23/10/2026 | A pedido do Caio, o bloco "Aguardando dados" (por mês, rankings e 2025) saiu da tela, para deixá-la limpa: a tela mostra só a divisão anual. PD01–PD03 seguem em `pendencias.py` e aparecem só na página "O que falta" |
| 24/10/2026 | Resposta mais direta (pedido do Caio): o grupo maior e o período saem da carga (nada fixo). A linha de conciliação só aparece quando o total difere do Início |
| 24/10/2026 | Revisão de textos (aprovada pelo Caio): "Sem talento" → "Talento não informado"; título do gráfico "Distribuição dos pedidos por vínculo do talento"; título em pergunta e Playfair mantidos (padrão do portal) |
| 24/10/2026 | Frase de fechamento automática ("a maior parte da demanda" acima de 50%; senão "o maior grupo da demanda"), cores da página Início, mais respiro abaixo da pergunta, barra em HTML com o % dentro da parte e animação de entrada coordenada (respeita menos movimento). Conferido em 1440×900 e 390 px |
| 24/10/2026 | T6: dica com os 10 exclusivos mais pedidos (`app/sql/talentos_top.sql`, mesma exceção D30-b), depois a coluna "Último" (MAX da data do pedido) e, por fim, o top 10 dos não exclusivos (nomes agrupados sem diferença de maiúsculas e espaços, grafia mais frequente, Squad fora). Dica no padrão "Novos pedidos" do Início: acima da linha, alinhada à direita, duas colunas, largura do maior nome + 10%, fechamento "Juntos, N pedidos: X% do grupo". Saiu a etiqueta de período (tela e dica) |
| 24/10/2026 | Ajustes finais (Caio): frase "X% da demanda do ano se concentra nos talentos [grupo]." (até 50%: "…vai para os talentos [grupo]."); barra com % e quantidade dentro de cada parte e largura mínima legível em Talento não informado ("2%" e "130"); lista com números trocada por legenda de uma linha com cor e nome dos três grupos, sem números (Talento não informado chegou a sair da legenda e voltou a pedido do Caio); as dicas T6 abrem só pelas legendas de Exclusivos e Não exclusivos, acima delas e sobre a barra; lista oculta para leitor de tela com os três grupos, números e % |
| 24/10/2026 | Último ajuste (Caio): com o mouse, a dica abre só pelo quadradinho da cor; o nome vira texto comum, sem sublinhado; teclado (Tab no nome) e toque (nome abre e fecha) mantidos; a dica deixa a classe genérica `dica-tipos`. Com este estado, o Caio deu a página como entregue |
| 24/10/2026 | **ENTREGUE (D31).** Ficha revista inteira para o estado final; top 10 reconferido no BigQuery (exclusivos 281 … 120, 1.802 = 52%; não exclusivos 65 … 12, 221 = 11%; soma dos exclusivos = 3.435; nenhum nome vazio). 89 testes |
| 25/10/2026 | **Revisão de 25/10 (auditoria + decisões 10–12 delegadas pelo Caio):** bases divergentes mostram os números com o aviso "A divisão por talento está sendo atualizada…" em vez de bloquear (decisão 10, TAL-D1); nota "10º lugar empatado com mais N talentos" no fim do top 10 (decisão 11; `talentos_top.sql` devolve `empate_fora`); nomes da dica numa linha só no palco largo (C1); `_fim_da_entrada` com a mesma regra E3 do Início (TAL-D9); ficha: desempate alfabético com `RANK()`, dois vínculos (7 talentos, 356 pedidos), 25 cards com `talentos_exclusivos` e `exclusivo = FALSE` (6 do Squad), SQL real da T6 e datas da silver (TAL-D2/D3/D5/D6/D7); itens levados aos lembretes da gold (decisão 12). Números da tela inalterados (3.435 / 1.955 / 130; 1.802 / 221) |
| 26/10/2026 | **Batalha 2 (D49):** a barra se revela num gesto (1,12 s); números prontos desde o 1º quadro. **Documentação:** retrato da carga da reunião (3.451 / 1.980 / 125 = 5.556; top 10 1.808 = 52% e 225 = 11%) no topo; regras inalteradas |
| 26/10/2026 | **D50 (pedido do gerente do Caio; revisa a D31):** seletor Todos / Exclusivos / Não exclusivos (o mesmo do SLA) filtrando a página; resposta composta como a do SLA por recorte (62% / 52% / 11%); barra do ano mais fina com o grupo do recorte destacado; mapa de calor dos 10 talentos mais pedidos × jan–dez (tabela acessível, número em cada célula, outubro parcial, nov/dez futuros); `talentos_top.sql` passa a devolver os três recortes mês a mês; dicas de top 10 da legenda retiradas (o mapa mostra os nomes). Conferido no BigQuery (5.556 = Início; 1.808 / 225; mapa = conferência independente). Testes `tests/test_talentos_d50.py`; capturas em 1920×1000, 1440×900, 1280×800 e 390 px |
| 26/10/2026 | Caio: saíram da tela os títulos "Divisão dos pedidos do ano por vínculo do talento" e "Os 10 talentos com mais pedidos, mês a mês", a nota "Juntos, N pedidos… · Squad fora" sob o mapa e o link "Próxima pergunta" do rodapé (só em Talentos). Os textos seguem para leitor de tela (classe so-leitor) e o passador continua levando à próxima página. |
| 26/10/2026 | **D51 (Caio; exceção à D46/D49 só nesta página):** ao abrir e ao trocar o filtro, a barra cresce e os números contam (barra, resposta, células, Ano) com o top 10 parado; botão "▶ Ver a subida e descida" ↔ "■ Parar" roda a "corrida do ano" contínua (4,5 s), com entrada e saída do top 10 pelo acumulado (T12; `talentos_top.sql` com `pos` e as CTEs `acumulado`/`na_corrida`, só SELECT); nomes sem reticências com coluna do tamanho do maior nome (T11). Revisões no mesmo dia: corrida automática 6–8 s → ~4 s → contínua → só no play. Conferido no BigQuery (ranking acumulado de jan e abr, recorte Todos). Testes `tests/test_talentos_d51.py`; seção 0-D51 |
| 26/10/2026 | **D51 revista (Caio):** play só com ícone (▶ ↔ ■ "Parar"; nome e dica "Ver a subida e descida das posições ao longo do ano"), redondo e discreto, fora do cartão, na linha da legenda da barra, à direita; corrida mais calma (~11 s): mês a mês com easing e respiro, moldura na coluna do mês, mês grande no canto com crossfade, células que acendem, números que contam, trocas com histerese (0,5 pedido ou 2% do líder, por 340 ms) e reordenação inteira, mola sem ultrapassar, quem sobe por cima com sombra, numeração 1–10 fixa, entrada/saída com fade. `TEMPOS` novo; testes ajustados (botão só ícone e na linha da legenda; 9–12 s); quadros em tempo real nos 3 filtros. Seção 0-D51 |
| 27/10/2026 | **D57:** fim da exceção D30-b: divisão e ranking leem as golds `gld_agenciamento_2026_talentos_ano` e `..._talentos_ranking` (antes `app/sql/talentos_*.sql` na silver); coerência T5 pelo dia da carga; números iguais na mesma carga |
