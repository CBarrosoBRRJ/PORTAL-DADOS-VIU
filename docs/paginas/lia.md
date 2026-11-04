# LIA — e-mails lidos e filtrados (V2)

**Ordem (Caio, 04/11/2026):** a LIA vem logo depois da Demanda e antes do SLA (Capa → Roadmap → Demanda → LIA → SLA (estudo pelo botão) → Iniciativas → Previsão → Encerramento).

**Atualização de 03/11/2026 (Caio, D67; extrator corrigido na validação da tarde):** LIA extraída de novo até
**31/10** (`tools/extrair_lia.py --fim 2026-10-31`, extraída em 03/11 16:44): **2.164** e-mails de 21/09 a 31/10; não
lead 1.880 (86,9%), lead 200 (9,2%), validação 84 (3,9%); revisado (até 12/10) 946 / 112 / 43, sem revisão 934 / 88 /
41; 304 no fim de semana; 459 itens com revisão manual; triagem poupada ≈ 63 h (≈ 11 h/semana, premissa
`MINUTOS_TRIAGEM` = 2); **50% fora do expediente (1.083)**. A extração das 13:20 dava 2.160 (1.876 não lead): o extrator
não lia `extracted_emails_2026-11.json`, gravado em UTC, onde estão 4 e-mails de 31/10 à noite (São Paulo); guardada em
`_descartados/2026-11-03/app/apresentacoes/gestao_orcamentos/lia/retrato_2160.json`. Retrato anterior (até 29/10, 2.047
lidos) em `_descartados/2026-11-03/`. Percentuais das partes pelo maior resto (fecham em 100%; ver a tabela de 03/11 em
"Quando o inbound chega"). **Vídeo publicado** no pop-up (`app/static/video/lia-na-pratica.mp4`,
"lia escopo completo.mp4" do Caio (03/11, substituiu o "fluxo LIA.mp4"), H.264 1920×1080, 1min46s, 42 MB; `lia_na_pratica.ARQUIVO`). As etapas do vídeo mostram a
situação: ✓ azul = iniciativa em produção (1 a 4: LIA e GPS), ampulheta + selo "Em teste" = fase de testes (5 e 6:
Orça+AI e COP.IA), derivada do `iniciativas/catalogo.py`. Os números abaixo, de 30/10, são histórico.

**Estado (30/10/2026): entregue na V2 (porta 8400), aprovado pelo Caio.** Histórico das rodadas abaixo. Uma tela
só: o que a LIA leu e como os e-mails se dividem, com o extrato de cada semana ao clicar e o vídeo "A LIA na prática" num
pop-up. Rota `/viu-agenciamento/lia#1` (`?semana=NN` abre o extrato sem JS). A análise de tempo na régua do SLA
(D-LIA-1) saiu da tela por decisão do Caio e fica registrada abaixo ("Análise de tempo"). A versão de duas visões está em
`_descartados/2026-10-30/` (LEIAME lá).
Arquivos: `app/apresentacoes/gestao_orcamentos/lia/` (`__init__.py` contas, `template.html`, `retrato.json`),
`app/static/lia.js` (extrato da semana), `app/static/lia_video.js` (pop-up do vídeo), blocos "LIA (D-LIA-3…)" e "LIA,
botão e pop-up do vídeo" em `estilo.css`, `tools/extrair_lia.py`, `tests/test_v2_paginas.py`. O vídeo e as etapas vêm
de `lia_na_pratica/__init__.py` (ficha `lia-na-pratica.md`); arquivos em `app/static/video/`.

## Pergunta e leitura

Sobretítulo "LIA". Pergunta (título da tela e da seção em `apresentacao.py`): **Quanto a LIA já leu e quanto deixou de
chegar à equipe?** Nome da seção: "LIA: e-mails lidos e filtrados".

**Hierarquia (D-LIA-3, Caio; posição revista em 30/10/2026):** o maior número é o total lido ("**2.047** e-mails."); o
segundo, "**87%** a LIA resolveu sozinha."; logo abaixo, a barra de fração com nome, quantidade e % de cada parte. O bloco
começa logo abaixo do título, alinhado ao topo dos números da direita (≈ 59 h e 54%), em tom de nuvem de palavras: números
grandes em Playfair, "e-mails." e "a LIA resolveu sozinha." em itálico marinho. A frase anterior ("ela resolveu sozinha:
garantiu que não era lead.") saiu por decisão do Caio, 30/10/2026 (sem mencionar lead). O botão "Ver a LIA na prática"
saiu da coluna da esquerda e fica embaixo do gráfico semanal, na última linha do cartão, à esquerda; o gráfico encolheu o
necessário para caber sem rolagem.

**Entregue (Caio, 30/10/2026): "está perfeito, entregamos".** Tela final: 2.047 e-mails com a barra de fração
(não lead 86,8%, lead 9,4%, validação 3,8% hachurada); prévia do vídeo "A LIA na prática" à direita; "O ganho para a
equipe" (≈ 59 h, ≈ 11 h por semana; 1.777 descartados sem a equipe abrir, 87% do total; **50% lidos fora do expediente**,
1.020 e-mails); "Quando o inbound chega" com leads, não leads e validação em quadrantes dentro × fora do expediente
(almoço dentro); gráfico "E-mails por semana" com a dica ao lado da coluna e a semana 44 no padrão de parcial. Cabe sem
rolagem em 1440×810, 1280×720 e 1920×1080 (cartões da esquerda e do gráfico com o mesmo topo e a mesma base) e não rola
para o lado em 390 px. Legenda dos quadrantes enxuta (sem fundo de pílula), cada grupo numa linha nas telas de mesa.

**Números da tela em 03/11/2026 (retrato de 21/09 a 31/10, 2.164 e-mails; mesmas regras e mesmo layout de 30/10).**
Percentuais pelo maior resto em dois níveis (`lia._pct_lados`): dentro + fora = 100% em cada categoria e as faixas de
cada lado somam o lado. Antes, arredondados um a um, os leads davam 74% + 27% = 101%.

| Faixa | Leads | % dos 200 | Não leads | % dos 1.880 | Validação | % das 84 | E-mails | % dos 2.164 | Taxa de lead |
|---|---|---|---|---|---|---|---|---|---|
| 10h–12h (dentro) | 35 | 18% | 270 | 14% | 13 | 16% | 318 | 15% | 11,0% |
| Almoço 12h–13h (dentro) | 13 | 7% | 98 | 5% | 6 | 7% | 117 | 5% | 11,1% |
| 13h–19h (dentro) | 99 | 49% | 521 | 28% | 26 | 31% | 646 | 30% | 15,3% |
| Antes das 10h (fora) | 17 | 9% | 191 | 10% | 15 | 18% | 223 | 10% | 7,6% |
| Noite e madrugada (fora) | 27 | 13% | 469 | 25% | 15 | 18% | 511 | 24% | 5,3% |
| Fim de semana e feriado (fora) | 9 | 4% | 331 | 18% | 9 | 10% | 349 | 16% | 2,6% |
| **Dentro / fora** | 147 / 53 | **74% / 26%** | 889 / 991 | **47% / 53%** | 45 / 39 | **54% / 46%** | 1.081 / 1.083 | **50% / 50%** | 13,6% / 4,9% |

Taxa de lead do período: 9,2% (200 ÷ 2.164). Fração (1 casa, maior resto): 86,9% + 9,2% + 3,9% = 100,0%; cada semana
do gráfico também fecha em 100,0%. A tabela de 30/10 abaixo é histórico.

**Estado vigente de "Quando o inbound chega" (Caio, 30/10/2026, última rodada) — substitui as versões abaixo.**

*Expediente da LIA (definição do Caio):* dias úteis 10h–19h, com o **almoço (12h–13h) dentro**; fora = antes das 10h,
depois das 19h, fim de semana e feriado. **Difere da regra do SLA**, que trata o almoço (13h–14h) como fora; o SLA não
mudou. O "lidos fora do expediente" do bloco de cima segue a mesma definição: **1.020 (50%)**, contra 1.112 (54%) na
regra do SLA e 1.130 (55%) na versão intermediária com almoço 12h–13h fora. Linha de apoio: "antes das 10h, noite e fim
de semana".

*Três barras em dois quadrantes:* Leads (193), Não leads (1.777) e Validação (77), cada uma em % da sua categoria. À
esquerda, só as faixas do expediente, na ordem 10h–12h → almoço → 13h–19h, encostadas no divisor; à direita, só as de
fora, na ordem antes das 10h → noite e madrugada → fim de semana e feriado, saindo do divisor. **Escala comum:** o
quadrante da esquerda mede a maior fatia "dentro" das três categorias (73%, leads) e o da direita a maior fatia "fora"
(53%, não leads). Assim o divisor é a mesma linha nas três barras e na legenda, e nenhum segmento de fora fica sob o
rótulo de dentro. O total de cada grupo aparece ao lado (ex.: Leads 73% | 27%). Legenda em dois grupos, na ordem dos
segmentos. Validação hachurada sobre as mesmas cores. Frase-resposta fora da tela (o achado está abaixo). `_quadrantes()`
em `lia/__init__.py`.

| Faixa | Leads | % dos 193 | Não leads | % dos 1.777 | Validação | % das 77 | E-mails | Taxa de lead |
|---|---|---|---|---|---|---|---|---|
| 10h–12h (dentro) | 33 | 17% | 254 | 14% | 12 | 16% | 299 | 11,0% |
| Almoço 12h–13h (dentro) | 10 | 5% | 94 | 5% | 6 | 8% | 110 | 9,1% |
| 13h–19h (dentro) | 98 | 51% | 494 | 28% | 26 | 34% | 618 | 15,9% |
| Antes das 10h (fora) | 16 | 8% | 186 | 10% | 14 | 18% | 216 | 7,4% |
| Noite e madrugada (fora) | 27 | 14% | 449 | 25% | 13 | 17% | 489 | 5,5% |
| Fim de semana e feriado (fora) | 9 | 5% | 300 | 17% | 6 | 8% | 315 | 2,9% |
| **Dentro / fora** | 141 / 52 | **73% / 27%** | 842 / 935 | **47% / 53%** | 44 / 33 | **57% / 43%** | 1.027 / 1.020 | 13,7% / 5,1% |

Achado (fora da tela): **metade dos e-mails chega fora do expediente, mas só 27% dos leads**; a tarde (13h–19h) concentra
51% dos leads com 30% dos e-mails. Validação = e-mails − leads − não leads da faixa (as categorias se excluem). Poucos leads
no almoço (10) e no fim de semana (9): mostrar o número, sem conclusão própria. Fonte: `horas`, `horas_lead` e
`horas_nao_lead` do retrato (`extrair_lia.py`, só leitura; os demais campos idênticos a cada nova extração).

*Cores (só os azuis do projeto, sem amarelo nem verde):* rampa ordinal #1e2a78 (`--t-mercado`, 10h–12h), #2f3fb8
(`--t-inbound`, almoço), #4a59c8 (13h–19h), #6a77d2 (antes das 10h), #8691dc (noite), #a3ace4 (`--t-sem-tipo`, fim de
semana); validada na skill dataviz como rampa ordinal (monótona, ΔL ≥ 0,06, ponta clara 2,14:1, um matiz: PASS).
Contraste do texto dentro dos segmentos (≥ 4,5:1): branco em #1e2a78 12,7:1, #2f3fb8 8,3:1 e #4a59c8 5,9:1; tinta em
#8691dc 6,1:1 e #a3ace4 8,2:1; #6a77d2 não chega a 4,5 com branco (4,05) nem com tinta (4,45), por isso o % vai numa
etiqueta branca (tinta sobre branco, 17:1); validação hachurada também com etiqueta branca. % dentro do segmento só a
partir de 8% da categoria (validação: 10%); os demais ficam na dica e no leitor de tela. Barra de fração e gráfico
semanal: não lead `--t-sem-tipo`, lead `--t-mercado` (número branco 12,7:1), validação hachurada (`.chave-anterior`,
sem número).

**Barra de e-mails × leads (Caio, 30/10/2026) — histórico; substituída pelos quadrantes acima. Antes era vigente para "Quando o inbound chega".**

Duas barras de 100% alinhadas, com as mesmas faixas na mesma ordem: **E-mails** (os 2.047) e **Leads** (os 193). A ordem
é **expediente | fora** (10h–12h, 13h–19h | antes das 10h, almoço, noite, fim de semana), e não a ordem do dia, para as
duas chaves finas acima ("No expediente · 45%", "Fora do expediente · 55%", referentes à barra de e-mails) ficarem
contínuas. Cor: 10h–12h `--t-mercado`, 13h–19h `--t-inbound`, antes das 10h `--t-proativo`, noite `--t-internos`, almoço
e fim de semana `--t-sem-tipo`. O % aparece dentro do segmento só quando ele tem ≥ 8% da barra. Legenda em pílulas numa
linha (cor e rótulo curto). E-mails, leads e taxa de cada faixa ficam na dica nativa do segmento (`title`) e no texto do
leitor de tela. Cartão com sombra em camadas mais presente e contorno leve (o do gráfico também); o bloco do ganho
continua chapado.

Frase-resposta: "**55% dos e-mails chegam fora do expediente, mas só 32% dos leads**".

| Faixa | E-mails (n) | % dos e-mails | Leads (n) | % dos leads | Taxa de lead (leads ÷ e-mails) |
|---|---|---|---|---|---|
| 10h–12h (expediente) | 299 | 15% | 33 | 17% | 11,0% |
| 13h–19h (expediente) | 618 | 30% | **98** | **51%** | **15,9%** |
| Antes das 10h (7h–10h) | 216 | 11% | 16 | 8% | 7,4% |
| Almoço (12h–13h) | 110 | 5% | 10 | 5% | 9,1% |
| Noite e madrugada (19h–7h) | 489 | 24% | 27 | 14% | 5,5% |
| Fim de semana e feriado | 315 | 15% | 9 | 5% | 2,9% |
| **Total** | 2.047 | | 193 | | 9,4% |

No expediente: 917 e-mails (45%) e 131 leads (68%), taxa 14,3%; fora: 1.130 (55%) e 62 (32%), taxa 5,5%. Diferença de
**+23 pontos** na fatia dos leads em relação à dos e-mails no expediente; a tarde sozinha tem +21 pontos (51% dos leads com
30% dos e-mails). Robustez: qui-quadrado expediente × fora, χ² = 45,9 (1 gl, p < 0,001); seis faixas, χ² = 56,5 (5 gl,
p < 0,001). **Cautela:** almoço (10 leads) e fim de semana (9) têm poucos leads; aparecem com o número inteiro, sem
conclusão própria. Hora = processamento pela LIA (aproxima a chegada). Fonte: `horas_lead` no retrato (leads por hora em
dia útil, fim de semana e feriado), acrescentado por `extrair_lia.py` em 30/10/2026 (só leitura; os demais campos saíram
idênticos).

**Rodada final (Caio, 30/10/2026) — vigente: o dia em faixas, expediente da LIA, dica ao lado, eixo e semana parcial.**

*Expediente da LIA (definição do Caio, 30/10/2026):* manhã 10h–12h, **almoço 12h–13h** (fora do expediente) e tarde
13h–19h, em dias úteis sem feriado. **Difere da regra do SLA** (10h–13h e 14h–19h, almoço 13h–14h, `app/expediente.py`),
que não mudou. Com essa definição, o "fora do expediente" do bloco de cima passou de **1.112 (54%) para 1.130 (55%)**,
+18 e-mails: o almoço das 12h tem 110 e-mails, contra 92 no das 13h. Os dois blocos usam o mesmo número
(`faixas_do_dia()`; o bloco de cima lê `dd["fora"]` em `tela()`).

*Quando o inbound chega:* frase-resposta "55% chegam fora do expediente; 11% antes das 10h", os dois grupos ("No
expediente 45%", "Fora do expediente 55%") e a lista das faixas na ordem do dia: rótulo, mini barra (proporcional à maior
faixa), % e número discreto; expediente em `--t-mercado`, fora em `--t-sem-tipo`.

| Faixa (pela hora do processamento) | E-mails | % dos 2.047 | Regra |
|---|---|---|---|
| Antes das 10h | 216 | 11% | dias úteis 7h–10h. **7h escolhido pelos dados**: 6h (35) e 7h (32) ainda estão no nível da madrugada; o volume sobe às 8h (64) e às 9h (120). Com 6h–10h seriam 251 |
| Manhã, 10h–12h | 299 | 15% | expediente |
| Almoço, 12h–13h | 110 | 5% | fora do expediente (definição do Caio) |
| Tarde, 13h–19h | 618 | 30% | expediente |
| Noite e madrugada | 489 | 24% | dias úteis 19h–7h |
| Fim de semana e feriado | 315 | 15% | sábado e domingo (270) e 12/10 (45), o dia todo |

Soma: 2.047; fora = 216 + 110 + 489 + 315 = 1.130. Fonte: campo `horas` do retrato (e-mails por hora em dia útil, fim de
semana e feriado), acrescentado em 30/10/2026 por `extrair_lia.py` (só leitura no bucket, só contagens; os demais campos
saíram idênticos ao rodar de novo). Barra de 100% com legenda de 6 faixas (versão anterior, achada confusa) em
`_descartados/2026-10-30/`.

*Dia da semana fora da tela por decisão do Caio, 30/10/2026; diferença pequena entre os dias* (média por dia: seg 59,
ter 63, qua 61, qui 66, sex 55, sáb–dom 27; totais 355 · 380 · 367 · 398 · 277 · 270; feriado na segunda). O cálculo
`recebimento()["dias"]` continua no código e nos testes.

*Gráfico semanal:* dica de cada semana no padrão `.dica` do portal (fundo branco, borda, sombra), **ao lado da coluna**
(à direita nas três primeiras semanas, à esquerda nas três últimas), na altura média da coluna e com seta; mouse ou foco;
Esc fecha (`app/static/lia_dica.js`). Eixo como o de Demanda e SLA: rótulos em `--tinta-2` sem negrito, 0,8em; período
em `--tinta-3`; linha de base `--eixo`; no mouse ou foco, fundo `--fundo-2` e texto `--tinta`. **Semana 44 parcial** no
padrão do mês parcial da Demanda (`.mes-parcial`): barra com as cores normais (não vazada), "parcial" em texto miúdo
cinza; sem cor forte, a pedido do Caio. Na dica, "parcial" em `<small>`.

**10ª rodada (Caio, 30/10/2026) — vigente: textos de apoio, capa do vídeo e cores iguais às de Talentos/Demanda.**

- **Bloco "O ganho para a equipe"** (antes "O que a LIA tirou das mãos da equipe"): três colunas iguais, conteúdo
  centralizado, réguas verticais entre elas. Textos: "≈ 59 h de triagem que saíram da rotina" (apoio "≈ 11 h por
  semana"); "1.777 e-mails descartados sem a equipe abrir" (apoio "87% do total" = não lead ÷ lidos); "54% lidos fora do
  expediente" (apoio "noite, almoço, fim de semana e feriado", a regra de `FORA`).
- **Fora da tela por decisão do Caio, 30/10/2026** (registro): "Estimativa de 2 min por e-mail; premissa a confirmar com
  a equipe" (a premissa continua valendo: `MINUTOS_TRIAGEM` = 2, não medida; o "≈" marca a estimativa), "Só 270, 1 em cada
  8, chegaram à equipe", "1.112 e-mails, 270 deles no fim de semana" e, na prévia do vídeo, "Do e-mail à carta orçamento".
- **Capa da prévia do vídeo:** campo `CAPA` em `lia_na_pratica/__init__.py` (arquivo em `app/static/video/`). Vazio = o
  degradê marinho; preenchido = `<img class="lia-vc-poster">` dentro da miniatura (sem `style=""`), e o mesmo arquivo vira
  o pôster do vídeo no pop-up. O Caio vai mandar um print do início do vídeo.
- **Cores:** as mesmas três da divisão de Talentos (exclusivo / não exclusivo / sem talento) e da situação na Demanda:
  não lead = `--t-sem-tipo` #a3ace4 (pastel), lead = `--t-mercado` #1e2a78 (escuro), validação = `--t-proativo` #5566cc
  (médio). Legendas com as classes do portal (`.chave .t-sem-tipo/.t-mercado/.t-proativo`); números dentro das barras
  como `.seg` (0,88em, peso 600, branco: 12,7:1 no lead); barras do bloco do inbound em `--t-sem-tipo` com o maior em
  `--t-mercado`. Script da skill dataviz: como rampa ordinal (como o portal valida esses tokens), todas as verificações
  passam; como categórica, daltonismo passa (ΔE 20,7), mas faixa de luminosidade (marinho) e croma (pastel) acusam, e o
  pastel fica a 2,1:1 no branco, compensado pelos números escritos e pela legenda. Substitui a paleta da 8ª rodada.

**9ª rodada (Caio, 30/10/2026) — vigente: extrato retirado, prévia do vídeo e grade alinhada.**

- **Extrato da semana retirado por decisão do Caio, 30/10/2026.** Clicar numa semana não troca mais nada; `?semana=NN` é
  aceito e ignorado (sem erro); sem `aria-current`, sem "Voltar ao período". Cada semana continua focável pelo teclado
  (`tabindex="0"`), com a dica ao passar o mouse ou focar (período, total e cada categoria com quantidade e %) e o texto
  completo para leitor de tela. O código saiu para `_descartados/2026-10-30/` (`lia_extrato.js`, `estilo_lia_extrato.css`,
  `lia/template_extrato.html`, `lia/extrato.py`; LEIAME lá). As regras e os números do extrato descritos abaixo ficam
  como registro.
- **Prévia do vídeo** no lugar do botão: miniatura 16:9 (9,5em) de player, fundo marinho em degradê com composição
  abstrata (ou o pôster, quando existir), play branco translúcido com triângulo de cantos arredondados; ao lado, "A LIA na
  prática" em Playfair e a linha "Do e-mail à carta orçamento". Hover/foco: sombra maior e halo no play; com movimento
  permitido, a miniatura cresce 3%, o play 12% e o halo pulsa uma vez; ao clicar, afunda. É um link (sem JS, leva à
  página antiga do vídeo); com JS abre o mesmo pop-up, que cresce a partir da miniatura e devolve o foco a ela.
- **Grade única:** a prévia fica à direita, na faixa do 2.047; o cartão do gráfico ocupa exatamente a mesma faixa
  vertical dos dois blocos da esquerda (mesmo topo e mesma base, medido: 0 px de diferença em 1440×810, 1280×720 e
  1920×1080); colunas 5,6 : 6,4 e vão de 2,4em; as colunas do gráfico crescem com a altura disponível.

**8ª rodada (Caio, 30/10/2026) — vigente: "Quando o inbound chega" sobre os 2.047, cores do portal e botão novo.**

*Base = os e-mails do período.* As duas leituras dividem os 2.047 (todas as categorias; a LIA só lê inbound) e somam o
total. Leads ficam fora deste bloco (estão no gráfico semanal e na fração).

| Gráfico | Retrato de 30/10/2026 20:49 (campo `turnos` acrescentado ao retrato; demais campos idênticos) | Regra |
|---|---|---|
| "54% chegam fora do expediente": barra de 100% por turno, o maior em `--t-inbound` | manhã 409 (20%) · tarde 526 (26%) · **fora 1.112 (54%)** = 2.047; leads 43 · 88 · 62 | turnos alinhados ao expediente do SLA (`app/expediente.py::SEM_ALMOCO`, seg–sex 10h–13h e 14h–19h): **manhã = 10h–13h, tarde = 14h–19h, fora = o resto** (almoço 13h–14h, 19h–10h, sábado, domingo e feriado). O "fora" é exatamente a regra dos 54% / 1.112 do bloco de cima (`FORA`), então os dois blocos batem; manhã + tarde = 935 = `faixas.expediente`. Fonte: `extrair_lia.py::turno` |
| "E-mails por dia, em média" e o total do período: mini barras seg, ter, qua, qui, sex e sáb–dom, o maior em `--t-inbound` | média por dia (total; dias): Seg 59 (355; 6) · Ter 63 (380; 6) · Qua 61 (367; 6) · **Qui 66 (398; 6)** · Sex 55 (277; 5) · Sáb–dom 27 (270; 10); totais somam 2.047 | todos os dias da janela; o **feriado de 12/10 fica na segunda** (o dia em que caiu: 45 e-mails). A barra e o destaque usam a **média inteira por dia**, porque a janela tem 6 segundas a quintas, 5 sextas e 10 dias de fim de semana: pelo total, a sexta (277) pareceria fraca só por ter um dia a menos. O total aparece ao lado, para a conta fechar em 2.047. Sem frase de padrão (ressalva acima: p ≈ 0,45) |

*Alternativa registrada (não adotada):* 4 períodos citados pelo Caio — manhã 7h–12h, tarde 12h–19h e fora do expediente
(o resto). Ficamos com os 3 turnos alinhados ao expediente do SLA, que batem com os 54% do bloco de cima. Para adotar a
alternativa, basta mudar `turno()` no extrator e rodar de novo.

*Extrator:* `tools/extrair_lia.py` ganhou `turno()` (manhã/tarde do expediente e fora), o campo `turnos` no retrato (por
categoria) e `--saida` para gravar em outro arquivo. Rodado em 30/10/2026 (só leitura no bucket) para um arquivo à parte:
todos os campos antigos saíram idênticos; ao retrato só foi acrescentado `turnos` (a data de extração ficou a mesma). O
extrato da semana ainda mostra os períodos antigos do dia (manhã 6h–12h, tarde 12h–18h, noite 18h–6h), por semana; o
retrato não tem os turnos por semana.

*Cores (paleta do portal, Caio):* não lead = `--t-internos` #7f8bd8, lead = `--t-inbound` #2f3fb8, validação =
`--atencao` #9a5b00 (o tom de atenção do portal), em todos os lugares (gráfico semanal, legendas, barra de fração, extrato,
dica da semana); barras do bloco do inbound em `--t-sem-tipo` com o maior em `--t-inbound`. Validado no script da skill
dataviz (`validate_palette.js "#7f8bd8,#2f3fb8,#9a5b00" --mode light`: faixa de luminosidade, croma, daltonismo — pior par
ΔE 20,8 — e contraste ≥ 3:1, todos PASS); branco sobre o lead 8,3:1; texto em `--atencao` 5,4:1. O marinho puro (#1e2a78)
para o lead reprovava na faixa de luminosidade.

*Botão do vídeo (refeito):* texto "A LIA na prática" (sem duração: ainda não há vídeo); pill de vidro acima do cartão do
gráfico, à direita; play = triângulo de cantos arredondados, centrado opticamente, num círculo azul VIU com degradê sutil
(SVG próprio); hover/foco: sombra cresce e o halo acende; com movimento permitido (`prefers-reduced-motion:
no-preference` e `html.js`), sobe 2 px, o círculo cresce 7% e o halo pulsa uma vez; ao clicar, afunda (scale 0,98). O
pop-up é o mesmo (cresce do botão e devolve o foco ao botão).

**6ª rodada (Caio, 30/10/2026) — histórico; os cortes do inbound foram trocados na 8ª rodada.** São dois assuntos, com dois visuais:

- **"O que a LIA tirou das mãos da equipe"** (antes "O que a equipe ganhou"): painel de fundo lavanda claro (#f1f2fc),
  cantos arredondados, sem sombra; os três números (≈ 59 h, 1.777, 54%) e as regras são os da tabela abaixo.
- **"Quando o inbound chega"**: cartão flutuante branco com os tokens `--cartao-*`. A LIA só lê inbound, então os dois
  cortes passam a contar **e-mails de inbound** (todas as categorias), não leads:

| Gráfico | Retrato de 30/10/2026 20:49 | Regra |
|---|---|---|
| "A tarde recebe 37% do inbound e 52% dos leads": barra de 100% dos e-mails por período, o maior em azul | manhã 605 (30%) · **tarde 761 (37%)** · noite 681 (33%); leads 54 · **101** · 38 (28% · 52% · 20%) | e-mails por período do dia (6h–12h, 12h–18h, 18h–6h; a noite tem 12 h), todos os dias da janela (2.047); o complemento "e X% dos leads" só aparece quando o período com mais e-mails é também o com mais leads. Verbo "recebe", não "concentra": 37% contra 33% não é concentração |
| "E-mails por dia útil, em média": mini barras seg–sex, o maior em azul | Seg 62 · Ter 63 · Qua 61 · **Qui 66** · Sex 55 (médias 62,0 · 63,3 · 61,2 · 66,3 · 55,4; 5 · 6 · 6 · 6 · 5 dias) | média de e-mails por dia útil sem o feriado, arredondada para inteiro (meio para cima); a barra usa o mesmo inteiro e é proporcional ao maior. A tela destaca o maior dia **sem frase de padrão** |

**Ressalva do dia da semana (só na ficha, fora da tela por decisão do Caio, 30/10/2026):** nem os e-mails (permutação
p ≈ 0,45, 3.000 vezes, semente 2026; 0,44 na análise anterior) nem os leads (p = 0,33) variam de forma clara entre os dias úteis; a quinta com 66 e-mails por dia e a segunda
com 8 leads por dia são o maior valor do período, não um padrão. A nota "Diferença pequena entre os dias; ainda sem padrão
firme." saiu da tela; a média de leads por dia útil (8 · 7 · 7 · 7 · 4) continua calculada (`leads_int`) e registrada
abaixo. Em `padroes()`: `mails_int`, `largura_mails`, `forte_mails`, `lider_mails`.

**Tela vigente (Caio, 30/10/2026, 4ª e 5ª rodadas; substitui a composição da 3ª rodada logo abaixo).**
Duas colunas iguais. **Esquerda** (painel do período; o extrato da semana troca a coluna inteira e "Voltar ao período"
restaura tudo): em cima, achatado, "**2.047** e-mails." / "**87%** a LIA resolveu sozinha." / barra de fração com a
legenda numa linha só ("Não lead 1.777 86,8% · Lead 193 9,4% · Validação 77 3,8%"); embaixo, sobre uma régua fina e com a
base alinhada à do cartão, dois blocos:

*O que a equipe ganhou* (três números inteiros lado a lado, ícones de traço discretos):

| Número | Retrato de 30/10/2026 20:49 | Regra |
|---|---|---|
| ≈ 59 h de triagem poupada | 59,2 h; "≈ 11 h por semana" | não leads × `MINUTOS_TRIAGEM` (2 min) ÷ 60; por semana = horas ÷ (39 dias da janela ÷ 7) = 59,2 ÷ 5,57 = 10,6 → 11. **Estimativa; premissa a confirmar com a equipe** (dito na tela) |
| 1.777 e-mails que a equipe não precisou abrir | 1.777 | categoria não lead. Linha: "Só 270, 1 em cada 8, chegaram à equipe" = lead + validação (193 + 77); 2.047 ÷ 270 = 7,58 → 8. Ressalva: até 12/10 a equipe ainda revisou parte da triagem à mão (459 e-mails) |
| 54% lidos fora do expediente | 1.112 e-mails, 270 no fim de semana | hora do processamento fora de seg–sex 10h–13h e 14h–19h, ou fim de semana, ou feriado (`FORA`) |

*Quando chegam os leads* (sem médias decimais na tela: o Caio pediu inteiros ou percentuais — "não recebemos 1,6 pedidos"):

| Gráfico | Retrato | Regra e leitura |
|---|---|---|
| "A tarde concentra 52% dos leads": barra de 100% dos leads por período, a maior parte em azul | manhã 54 (28%) · **tarde 101 (52%)** · noite 38 (20%) | leads por período do dia (6h–12h, 12h–18h, 18h–6h), todos os dias da janela; frase só quando o qui-quadrado sustenta (`leitura_periodo` ≠ "sem"; hoje χ² = 25,2, p < 0,001) |
| "Leads por dia útil, em média": mini barras seg–sex, a maior em azul | **Seg 8** · Ter 7 · Qua 7 · Qui 7 · Sex 4 (médias 7,8 · 7,3 · 6,7 · 6,5 · 4,4; 5 · 6 · 6 · 6 · 5 dias) | média de leads por dia útil sem o feriado, **arredondada para inteiro** (meio para cima); a barra usa o mesmo inteiro. Não usamos o total por dia (39 · 44 · 40 · 39 · 22) porque a janela tem 5 segundas e 6 terças: a terça "ganharia" só por ter um dia a mais |
| Nota sob as barras | "Diferença pequena entre os dias; ainda sem padrão firme." | **ressalva obrigatória**: teste de permutação p = 0,33 (`leitura_dia` = "sem"). Com p entre 0,05 e 0,10 a nota vira "Tendência, ainda sem padrão firme."; abaixo de 0,05, "Diferença consistente entre os dias." A tela destaca o dia de maior média, mas não afirma padrão |

O mapa de calor dia × período (médias decimais) saiu da tela por decisão do Caio, 30/10/2026; o cálculo (`padroes()["mapa"]`)
continua no código e nos testes, e os valores estão abaixo, em "Mapa dia × período". CSS em
`_descartados/2026-10-30/app/static/estilo_lia_mapa.css`.

**Direita:** só o gráfico semanal, no cartão e nas classes dos gráficos de Demanda e SLA (`colunas cartao-grafico`,
`colunas-titulo`, `legenda` + `chave` com o % em `<strong>`, total em cinza sobre a coluna, rótulo em `tinta-2`, linha de
base contínua). Título "E-mails por semana, 21/09 a 29/10"; o botão "Ver a LIA na prática" fica no canto direito do
cabeçalho do cartão. O cartão tem altura própria (as colunas com 19,5em), apoiado na base da coluna da esquerda, e começa
mais ou menos na altura do 87%.

**Composição (Caio, 30/10/2026, 3ª rodada; histórico).** Duas colunas iguais. À esquerda, o painel do período: em cima 2.047 / 87% /
fração; embaixo, sobre uma régua fina e com a base alinhada à do cartão, as análises de apoio — à esquerda os dois números
empilhados (relógio discreto + "≈ 59 h de triagem poupada à equipe", linha "7,4 dias de trabalho. Estimativa: 2 min por
e-mail descartado; premissa a confirmar com a equipe"; lua discreta + "54% lidos fora do expediente", linha "1.112 e-mails à
noite, no almoço, em feriado ou no fim de semana"), à direita o mapa compacto "Quando chegam os leads · média por dia" (dia ×
período, tooltip mantido) com legenda de escala "menos ▢▢▢▢▢ mais". À direita, o cartão só com o gráfico semanal na
altura toda e o botão do vídeo embaixo. O detalhe "270 no sábado e no domingo" saiu da linha do 54% (fica na tabela
abaixo). **Extrato:** troca a coluna da esquerda inteira (números e mapa somem enquanto ele está aberto, porque o extrato
é alto e traz a divisão por período da semana); "Voltar ao período" restaura tudo.

**Página mais limpa (Caio, 30/10/2026):** saíram da tela a frase de abertura "De 21/09 a 29/10, a LIA leu" (o período
foi para o título do cartão do gráfico, hoje "E-mails por semana, 21/09 a 29/10", e o leitor de tela ainda ouve
a frase inteira antes do total, em `so-leitor`), as legendas pequenas sob cada parte da fração, a nota em itálico da
revisão até 12/10, as leituras "Dia da semana" e "Período do dia" e a nota do gráfico (semana ISO, hora do
processamento, data de extração). Os textos, as regras e as ressalvas continuam abaixo, marcados *(fora da tela por decisão do Caio, 30/10/2026)*.
O gráfico das semanas e o mapa dia × período continuam; o extrato da semana não mudou.

| Elemento da tela | Número (retrato de 30/10/2026 20:49) | Regra |
|---|---|---|
| E-mails lidos | **2.047** | mensagens únicas da janela 21/09–29/10 (todas as categorias) |
| Resolvidos sozinha ("a LIA resolveu sozinha.") | **87%** (1.777) | categoria não lead (com a correção da revisão manual, quando houve) |
| Fração | não lead 1.777 (86,8%) · lead 193 (9,4%) · validação 77 (3,8%); as legendas "a LIA garantiu que não era lead", "virou lead no monday" e "seguiu para análise da equipe" (`CATEGORIAS` em `lia/__init__.py`) estão *(fora da tela por decisão do Caio, 30/10/2026)* | categorias ÷ lidos; uma ordem só na barra, na pilha das semanas, na legenda e na dica |
| Apoio *(fora da tela por decisão do Caio, 30/10/2026)* | "Até 12/10, a equipe ainda conferia parte da triagem (459 e-mails revistos à mão); desde então, recebe só leads e validações (270 no período)." | `revisado` na revisão manual (todos até 12/10); lead + validação |
| Triagem poupada (coluna da esquerda, sob a fração) | **≈ 59 h** (59,2 h; 7,4 dias de trabalho de 8 h) | **estimativa**: não leads × `MINUTOS_TRIAGEM` (padrão 2 min) ÷ 60; premissa a confirmar com a equipe |
| Lidos fora do expediente (coluna da esquerda) | **54%** = 1.112 (noite 705, almoço 92, fim de semana 270, feriado 45) | hora do processamento fora de seg–sex 10h–13h e 14h–19h, ou fim de semana, ou feriado (12/10) |
| % que virou lead | 9,4% | na fração (a faixa de números de apoio ficou com dois itens para não repetir) |
| Semanas (gráfico; título "E-mails por semana, 21/09 a 29/10") | Semana 39 (21–27/09) 377 · 40 (28/09–04/10) 339 · 41 (05–11/10) 340 · 42 (12–18/10) 348 · 43 (19–25/10) 353 · 44 (26–29/10, parcial) 290 | semana ISO, segunda a domingo da data do processamento, com fim de semana e feriado; pilha de baixo para cima: não lead, lead, validação; a semana parcial vazada |
| Leads por semana | 37 · 35 · **39** · 25 · 38 · 19 | a semana 41 teve mais leads, quase empatada com a 43 (38) e a 39 (37); a 42 (feriado) teve menos; saiu dos destaques (fica no extrato de cada semana) |

**Padrões do mercado (D-LIA-5; na tela fica só o mapa, ao lado do gráfico; as duas leituras e a nota estão *(fora da tela por decisão do Caio, 30/10/2026)*).** O Caio pediu comportamento
recorrente, não datas. Hora = a do **processamento** pela LIA, que aproxima a chegada (a LIA processa a caixa o dia todo).

*Dia da semana.* Regra: dias úteis sem o feriado de 12/10 (28 dias); média de leads e de e-mails por dia; fim de semana
à parte (10 dias). Robustez: teste de permutação (embaralha o dia da semana entre os 28 dias, estatística F, 3.000
vezes, semente 2026; na análise, 20.000 vezes deu o mesmo): **p = 0,32** (amplitude 3,4 leads/dia, p = 0,23). Regra da
frase: p < 0,05 "costuma"; 0,05 a 0,10 "tendência"; acima, "sem diferença clara".

| Dia | n | Leads por dia | E-mails por dia | % lead |
|---|---|---|---|---|
| Segunda | 5 | 7,8 | 62 | 12,6% |
| Terça | 6 | 7,3 | 63 | 11,6% |
| Quarta | 6 | 6,7 | 61 | 10,9% |
| Quinta | 6 | 6,5 | 66 | 9,8% |
| Sexta | 5 | 4,4 | 55 | 7,9% |
| Sábado e domingo | 10 | 0,8 | 27 | 3,0% |

Frase que estava na tela *(fora da tela por decisão do Caio, 30/10/2026)*: "**Dia da semana:** sem diferença clara entre os dias úteis, de 4,4 leads por dia (sexta) a 7,8
(segunda), com 5 a 6 dias de cada. No fim de semana, 0,8 lead por dia." A sexta isolada contra os demais dias daria p =
0,03 (unilateral), mas foi escolhida depois de olhar os dados; corrigida pelas 5 comparações possíveis (≈ 0,15), não
sustenta "costuma". Os e-mails por dia útil também não variam de forma clara (p = 0,44).

*Período do dia.* Faixas: manhã 6h–12h, tarde 12h–18h, noite 18h–6h (12 h; a madrugada conta na noite do próprio dia
do calendário). Todos os dias da janela (2.047 e-mails, 193 leads). Robustez: qui-quadrado da taxa de lead por período
(2 graus de liberdade): **χ² = 25,2, p < 0,001**; e a tarde teve mais leads que manhã e noite em **19 dos 28 dias úteis**.

| Período | E-mails | % dos e-mails | Leads | % dos leads | % dos e-mails que viram lead |
|---|---|---|---|---|---|
| Manhã (6h–12h) | 605 | 30% | 54 | 28% | 9% |
| Tarde (12h–18h) | 761 | 37% | 101 | 52% | 13% |
| Noite (18h–6h) | 681 | 33% | 38 | 20% | 6% |

Frase que estava na tela *(fora da tela por decisão do Caio, 30/10/2026)*: "**Período do dia:** os leads chegam mais à tarde: 52% dos leads com 37% dos e-mails; 13% dos e-mails da
tarde viram lead, contra 9% de manhã e 6% à noite." (O e-mail que chega à noite é, em boa parte, não lead: a taxa cai
para 6%.)

*Mapa dia × período* (fora da tela por decisão do Caio, 30/10/2026, 4ª rodada: médias decimais; média de leads por dia útil; tooltip com leads e e-mails por dia e o n): Seg 1,6 · 4,4 · 1,8 (5
dias); Ter 3,3 · 3,0 · 1,0 (6); Qua 1,5 · 3,8 · 1,3 (6); Qui 2,0 · 3,7 · 0,8 (6); Sex 0,8 · 2,6 · 1,0 (5); sáb–dom 0,1 ·
0,3 · 0,4 (10). Cinco tons de um azul só (escala ordinal validada na skill dataviz), pela posição entre o menor e o maior
valor do mapa; número escrito em cada célula.

**Extrato da semana (D-LIA-4/5).** Ao clicar (ou Enter) numa semana do gráfico, o bloco da esquerda dá lugar ao
extrato dela: "Semana NN, de dd/mm a dd/mm" (parcial, se for), total lido, barra de fração da semana com quantidade e %,
e-mails e leads por período do dia (manhã, tarde, noite), e-mails fora do expediente (quantidade e %) e uma leitura por
regra: o % de lead da semana contra o do período, com 1 casa ("acima", "abaixo" ou "igual"). Sem datas de dias (D-LIA-5).
Exemplo (semana 41): 340 e-mails; não lead 288 (84,7%), lead 39 (11,5%), validação 13 (3,8%); manhã 88 e-mails e 7 leads,
tarde 146 e 22, noite 106 e 10; fora do expediente 181 (53%); "Lead em 11,5% dos e-mails da semana, acima dos 9,4% do
período." Fora do expediente por semana: 191 · 176 · 181 · 221 · 196 · 147.

**Vídeo "A LIA na prática".** Botão "Ver a LIA na prática" logo acima do cartão do gráfico semanal, alinhado à direita dele (desde a 7ª rodada, Caio, 30/10/2026): play num círculo azul VIU com halo, cantos de 6 px, sombra em camadas; ao passar o mouse ou focar, sobe 1 px, a sombra cresce e o halo acende (pulsa uma vez só com `prefers-reduced-motion: no-preference` e `html.js`); no celular, entra no fluxo antes do cartão. O título do cartão fica sozinho, com a legenda embaixo. Antes (branco, borda fina, ▶ pequeno; azul só no hover e
no foco) abre um pop-up (`<dialog>`) com o vídeo 16:9 à esquerda e "O que o vídeo mostra" (6 etapas) à direita; no
celular, a lista vai para baixo. Sem arquivo, o espaço reservado "Vídeo a incluir". Sem JS, o botão leva à página antiga
`/viu-agenciamento/lia-na-pratica` (oculta da navegação). Regras do vídeo na ficha `lia-na-pratica.md`.

**Premissa da estimativa de tempo:** 2 minutos para a equipe abrir, ler e descartar um e-mail que não é oportunidade
(`MINUTOS_TRIAGEM` em `lia/__init__.py`; o Caio pediu esse padrão). Não foi medida; a tela diz "Estimativa … premissa a
confirmar com a equipe". Com 1 min seriam ≈ 30 h; com 3 min, ≈ 89 h. A conta não desconta o tempo que a equipe ainda
gastou revisando a triagem até 12/10 (459 e-mails) nem o tempo de validar os 77 casos.

**Por que "resolveu sozinha" e o apoio de 12/10** *(fora da tela por decisão do Caio, 30/10/2026)***:** até 12/10 a equipe conferia parte da classificação à mão
(período "revisado"); só de 13/10 em diante a triagem roda sem revisão. O apoio dizia isso na tela; agora fica só aqui.

**Hora do processamento como hora de chegada** *(fora da tela por decisão do Caio, 30/10/2026)***:** o arquivo da LIA não guarda a hora em que o e-mail chegou, só a do
processamento. A LIA processa a caixa o dia todo (minutos uniformes: 311 a 374 e-mails por dezena de minuto; todas as
horas do dia com e-mails), então a hora do processamento é uma boa aproximação.

**Nota do gráfico** *(fora da tela por decisão do Caio, 30/10/2026)*: "Semana ISO, de segunda a domingo. Hora = processamento pela LIA, que aproxima a chegada;
dias da semana sem o feriado de 12/10. Dados extraídos em 30/10/2026, 20:49." (data de `extraido_em` do retrato; o
rodapé datado da página continua).

## Fonte e regras

Fonte: `gs://gglobo-viu-lia-dados-prd/data/` (Cloud Storage da LIA), lida **só para leitura** com as credenciais do
portal (ADC do gcloud-viu, conta `caio.barroso@viu.com.br`) por `tools/extrair_lia.py`, que grava **só contagens
agregadas** em `retrato.json` (nenhum remetente, assunto ou conteúdo de e-mail). O slide lê o retrato; não consulta nada
ao abrir. Fora da gold (D57): exceção registrada aqui, como a sensibilidade de 2025 do ML.

| Regra | Como |
|---|---|
| E-mail | mensagem única (`internet_message_id`) em `extracted_emails_AAAA-MM.json`; reprocessada = vale o último processamento **dentro da janela** (116 reprocessamentos na janela de 30/10). Os arquivos são por mês em UTC: o extrator lê também o mês anterior a `--inicio` e o seguinte a `--fim` (03/11/2026) |
| Dia | data de `data_processamento` no fuso de São Paulo; janela 21/09 a 31/10/2026 (até 29/10 antes de 03/11) |
| Categoria | `classificacao` da LIA (`nao_lead`, `lead`, `duvida`/`DUVIDA` = validação), trocada por `classificacao_correta` de `revisao_manual.json` quando `revisado` |
| Períodos | revisado até 12/10; sem revisão de 13/10 em diante |
| Semana (novo, D-LIA-2) | segunda a domingo; todos os dias (as semanas somam o total) |
| Faixas de horário (novo, D-LIA-2) | expediente, almoço, noite (dia útil), fim de semana, feriado — `extrair_lia.py::faixa` |
| Período do dia (D-LIA-5) | manhã 6h–12h, tarde 12h–18h, noite 18h–6h pela hora do processamento; cada dia traz `periodos` com as três categorias — `extrair_lia.py::periodo` |
| Dias (D-LIA-3/4) | todos os dias da janela, com zero quando não houve e-mail, marcas `fim_de_semana` e `feriado` e `fora` (e-mails fora do expediente); as semanas também trazem `fora` |

Retrato extraído em 30/10/2026 20:49 (mesmos períodos do de 18:55): **2.047** únicos = 1.101 (revisado) + 946 (sem
revisão); não lead 1.777 (86,8%), lead 193 (9,4%), validação 77 (3,8%); 270 no fim de semana; 459 itens do 1º período
com revisão manual. As leituras diárias da versão anterior (61 e-mails/dia útil; 6,6 leads/dia útil; sexta a mais fraca;
pico 08/10 com 11 leads) continuam valendo, mas saíram da tela.

Para atualizar: `python tools/extrair_lia.py [--inicio AAAA-MM-DD] [--fim AAAA-MM-DD] [--corte AAAA-MM-DD]` (venv, com
`CLOUDSDK_CONFIG` do gcloud-viu), depois `python -m pytest tests -q`.

## Conferência com o PRD de @cris (30/10/2026)

| Número | PRD | Fonte (bucket) | Situação |
|---|---|---|---|
| E-mails únicos | 2.047 (1.101 + 946) | 2.047 (1.101 + 946) | ✅ bate |
| Fim de semana | 270 | 270 | ✅ |
| Dias úteis / e-mails neles | 29 / 1.781 | 29 / 1.777 | ⚠️ PRD soma 2.051 (transcrito de imagem) |
| 22/10 | 10 leads em 59 | 10 leads em 59 | ✅ |
| Leads, 2º período | 81 | 81 | ✅ |
| Leads, 1º período | 75 | 112 (113 sem a revisão) | ❌ não reproduzido por nenhuma regra testada (revisão, item no monday, conversa única) |
| Total de leads | 156 (7,6%) | 193 (9,4%) | ❌ consequência da linha acima |
| Dia com mais leads | 22/10 (10) | 08/10 (11) | ❌ idem |
| Validação | 103 | 77 | ❌ idem |

**Decisão pendente (Caio + equipe da LIA):** qual é a regra do relatório da equipe para o 1º período. Enquanto isso,
o slide mostra a fonte. Se o relatório for o oficial, basta trocar o retrato (ou a regra do extrator) e rodar os testes.

## Análise de tempo (fora da tela desde a D-LIA-2): antes × depois na régua do SLA (D-LIA-1, 30/10/2026)

Decisão do Caio (30/10/2026, noite): a análise sai da tela porque os dados não sustentam ganho de velocidade; fica
aqui, inteira (números, SQL, bootstrap, placebo e conclusão). O código que a mostrava está em
`_descartados/2026-10-30/app/apresentacoes/gestao_orcamentos/lia/`.

### Auditoria da versão anterior (por que 4,6 → 2,1 dias não se compara com o SLA)

A primeira versão mostrava "o tempo típico até a carta caiu de 4,6 para 2,1 dias (−54,2%)", com constantes da planilha
manual da equipe (PRD de @cris). Comparada com a página SLA, ela media outra coisa em quase tudo:

| Item | Versão anterior (planilha) | Página SLA (gold) |
|---|---|---|
| Início | chegada do e-mail | entrada do pedido no monday (passo 1) |
| Fim | carta enviada | 1ª entrega ao cliente (1ª chegada em Aguardando Feedback, C1) |
| Relógio | horas corridas (noites e fins de semana); "dia" = 24 h | horas de trabalho do expediente, sem almoço (10h–13h + 14h–19h); dia de trabalho = 8 h |
| Estatística | mediana (certo), dividida por 24 | mediana (típico), em horas de trabalho; C3c em dias úteis com fração |
| Amostra | 6 casos antes (jul–set) e 16 depois, escolhidos à mão | todos os orçamentos medidos (2.347 jan–set na carga de 26/10) |
| Recorte | sem grupo de controle | por mês da 1ª entrega; grupos de talento e de tipo de input |

Por isso "4,6 dias" (110,6 h corridas) não conversa com "1,8 dia útil" ou "14 h de trabalho" do SLA: um dia corrido
de 24 h tem só 8 h de expediente, e um fim de semana no meio soma 48 h corridas sem nenhuma hora de trabalho. A queda de
54% também não tinha controle (sazonalidade e carga do mês entram junto). A planilha saiu da tela; fica citada no cartão
dos passos como outra régua (e-mail → carta, horas corridas), porque é a única medição do trecho e-mail → monday.

### Regra (recorte e janelas do Caio, 30/10/2026)

A LIA só toca pedidos **Inbound** (lê as caixas dos talentos e registra o lead no monday). A comparação é:

- **Inbound antes × Inbound depois da LIA**, com as regras do SLA e pela **data da 1ª entrega** (C4, a mesma regra do mês
  do SLA). **Antes = 01/01 a 20/09/2026** (o ano inteiro até a véspera da LIA, como o SLA olha o ano). **Depois = 21/09 a
  29/10/2026** (até o "Dados até" da carga; a LIA processa desde a sexta 18/09 e a janela do slide começa na segunda 21/09).
- **Controle:** os outros tipos de input (Mercado, Proativo e os Internos: ViU, Interna, Globo, ViU First, OTR), que a
  LIA não toca, nas mesmas janelas: diferença nas diferenças (DiD). Pedido sem tipo fica fora.
- **Métrica:** a do SLA. Típico = mediana de `h_trabalho` (horas de trabalho da equipe, expediente sem almoço, da entrada
  à 1ª entrega, C2), também em dias de trabalho (÷ 8 h, escrita E3 do estudo); quartis (1º e 3º); % em até 16 h (meta
  sugerida, C6); n de cada grupo.
- **Robustez:** intervalos de 95% por reamostragem (bootstrap de percentis, 2.000 réplicas, semente fixa 2026) da
  diferença de medianas do Inbound, da diferença do % em até 16 h, da DiD das medianas e da DiD do %. Sensibilidade com
  "antes" só de 01/07 a 20/09. Placebo: o mesmo desenho (antes = 01/01 até a véspera do corte; depois com 39 dias) em 19
  segundas-feiras de 06/04 a 10/08/2026, com o "depois" inteiro antes da LIA. Leitura por regra: intervalo inteiro acima
  de zero = "mais lento"; abaixo = "mais rápido"; cruzando o zero = direção do ponto + "dentro do acaso".
- **Fonte:** só a view gold `gld_agenciamento_2026_sla_entregas` (colunas `entregue_em`, `tipo_de_input`, `h_trabalho`),
  a mesma da página SLA (`sla.calculos.entregas`). O site só recorta e agrega (D57). Código: `lia/__init__.py`
  (`antes_depois`, `_visao_tempo`; constantes `ANTES_INICIO`, `LIA_INICIO`, `RECENTE_INICIO`). Rodapé da seção datado
  pelas tabelas do SLA (`tabelas=("sla", "sla_entregas")`).
- Com menos de 30 entregas em algum dos quatro grupos, a tela não compara (mensagem).

### Números (carga de 30/10/2026 09:01, `_processado_em` 12:01:46 UTC, dados até 29/10)

| Período (data da 1ª entrega) | Tipo de input | n | Típico (h) | Típico (dias de trabalho) | 1º–3º quartil | Em até 16 h |
|---|---|---|---|---|---|---|
| Antes, 01/01–20/09 | Inbound | 603 | **13,7** | 1,7 | 6,8–24,5 h | **57%** (56,7) |
| Depois, 21/09–29/10 | Inbound | 134 | **15,7** | 2,0 | 7,3–27,0 h | **51%** (51,5) |
| Antes, 01/01–20/09 | Outros (controle) | 1.611 | 14,5 | 1,8 | 6,5–28,0 h | 55% (54,5) |
| Depois, 21/09–29/10 | Outros (controle) | 345 | 12,8 | 1,6 | 6,5–26,6 h | 57% (57,1) |

| Leitura | Ponto | Intervalo de 95% (bootstrap) | Leitura |
|---|---|---|---|
| Inbound, típico depois − antes | **+2,0 h** | −1,6 a +6,3 h | mais lento, dentro do acaso |
| Inbound, % em até 16 h | −5 pontos | −14 a +4 | dentro do acaso |
| Controle, típico depois − antes | −1,7 h | — | mais rápido (ponto) |
| DiD do típico (Inbound − controle) | **+3,7 h** | −1,9 a +8,1 h | dentro do acaso |
| DiD do % em até 16 h | −8 pontos | −18 a +3 | dentro do acaso |
| Sensibilidade, antes = 01/07–20/09 (Inbound 12,0 h, n 263; 65% em 16 h) | DiD +4,6 h | −0,8 a +9,8 h | dentro do acaso; no % em 16 h, −15 pontos (−27 a −3, BigQuery) fora do acaso |
| Placebo (19 cortes sem LIA) | 5 de 19 com DiD ≥ +3,7 h | — | diferença comum sem LIA |

(Intervalos da tela, calculados no site com semente fixa; o mesmo bootstrap no BigQuery, 2.000 réplicas, deu +1,8 h de
mediana do Inbound com −1,8 a +6,1 h e DiD −1,8 a +8,1 h: a diferença é só de sorteio.)

**Por data de entrada do pedido** (outra data, mostrada só para checar; a regra do SLA é a da 1ª entrega): Inbound 13,9 h
(612; 56% em 16 h) → 15,1 h (125; 54%); controle 14,6 h (1.640; 54%) → 12,0 h (316; 60%). Mesma leitura.

**Conclusão honesta:** na régua do SLA, o típico do Inbound **subiu** de 13,7 h (1,7 dia de trabalho) para 15,7 h
(2,0 dias) depois que a LIA entrou, e o % em até 16 h caiu de 57% para 51%, enquanto os outros tipos ficaram um pouco mais
rápidos (14,5 → 12,8 h). A direção é de **piora**, mas **não é robusta**: todos os intervalos cruzam o zero, e em 5 de 19
cortes de mentira (sem LIA) apareceu diferença do mesmo tamanho. **Não há ganho da LIA no relógio do SLA**, e também não
dá para dizer que ela piorou o tempo: é associação, com 5,5 semanas de "depois". Com "antes" só de julho a 20/09 (meses
rápidos para o Inbound, 12,0 h) a piora parece maior (+4,6 h com controle; −15 pontos em 16 h, este fora do acaso): por
isso a janela importa e a do ano é a da regra do SLA.

**Pistas (fora da tela, para investigar):**
- Mês a mês, o típico do Inbound (mês da 1ª entrega): jan 8,4 · fev 15,6 · mar 15,1 · abr 16,4 · mai 19,9 · jun 16,9 ·
  jul 10,5 · ago 11,9 · set 14,1 · out 17,0 h (n 52 · 35 · 65 · 54 · 69 · 65 · 106 · 113 · 77 · 101). Outubro fica no
  patamar de abr–jun; a subida começa em setembro (que mistura antes e depois de 21/09). Controle: 13,8 · 15,8 · 14,9 ·
  16,3 · 12,8 · 16,0 · 13,7 · 13,6 · 13,3 · 15,4 h.
- Onde está a diferença (médias, que somam; antes = jul–20/09): Inbound 15,2 → 18,7 h, quase toda na **revisão**
  (6,6 → 9,7 h); fila 5,1 → 4,7 h, elaboração 3,6 → 4,3 h. A LIA não revisa nada (ou os pedidos chegam menos prontos:
  hipótese, sem dado).
- Pedidos que a própria LIA registrou (marcados por `lia_chave_sync_nao_editar` na **silver** `slv_agenciamento_2026_itens`,
  167 itens, 126 na gold): no Inbound entregue depois de 21/09, 91 da LIA com típico 15,2 h (fila 3,6 h) contra 43 dos
  demais com 17,3 h. Os da LIA não são mais lentos que o resto do Inbound.
- Exclusivo × não exclusivo dentro do Inbound (antes = jul–20/09): exclusivos 12,3 h (248) → 15,2 h (117); não
  exclusivos 9,0 h (15) → 24,0 h (17), n pequeno demais.
- Recortes anteriores desta mesma tarde (registro): exclusivos × não exclusivos, todos os tipos, antes jul–20/09:
  exclusivos 10,5 h (766) → 11,1 h (321), DiD +1,0 h (−5,7 a +3,5); Inbound com antes jul–20/09: 12,0 → 15,7 h. Trocados
  pelo recorte do Inbound (a LIA só toca o Inbound) e pela janela do ano (Caio).

**O que o SLA não enxerga:** os passos 1 a 3 (ler, classificar, registrar) acontecem antes de o pedido existir no
monday. Se a LIA encurta o caminho do e-mail até o registro, isso não aparece no SLA, que começa na entrada do pedido.
Não há dado para medir esse trecho: os arquivos da LIA têm a hora de processamento, mas não a hora de chegada do e-mail,
e o item do monday não guarda o id do e-mail. Os passos 4 a 6 (GPS, Orça+AI, COP.IA) estão dentro do relógio, e dois
deles ainda estão em fase de testes.

### SQL para reproduzir (BigQuery, só leitura)

```sql
-- n, quartis, típico e % em até 16 h: Inbound × controle, antes × depois (pela data da 1ª entrega, regra do SLA)
WITH e AS (
  SELECT IF(tipo_de_input = 'Inbound', 'Inbound', 'controle') AS grupo,
         IF(DATE(entregue_em) >= '2026-09-21', '2_depois', '1_antes') AS periodo, h_trabalho
  FROM `gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_2026_sla_entregas`
  WHERE tipo_de_input IS NOT NULL AND DATE(entregue_em) BETWEEN '2026-01-01' AND '2026-10-29')
SELECT grupo, periodo, COUNT(*) AS n, ANY_VALUE(p25) AS p25, ANY_VALUE(med) AS tipico, ANY_VALUE(med) / 8 AS dias,
       ANY_VALUE(p75) AS p75, ROUND(100 * AVG(IF(h_trabalho <= 16, 1, 0)), 1) AS pct_ate_16h
FROM (SELECT *, PERCENTILE_CONT(h_trabalho, 0.25) OVER w AS p25, PERCENTILE_CONT(h_trabalho, 0.5) OVER w AS med,
             PERCENTILE_CONT(h_trabalho, 0.75) OVER w AS p75
      FROM e WINDOW w AS (PARTITION BY grupo, periodo))
GROUP BY grupo, periodo ORDER BY grupo, periodo;
-- carga de 30/10/2026: Inbound  603 · 6,8 · 13,69 · 24,5 · 56,7 | 134 · 7,3 · 15,73 · 27,0 · 51,5
--                       controle 1.611 · 6,5 · 14,48 · 28,0 · 54,5 | 345 · 6,5 · 12,79 · 26,6 · 57,1
```

O bootstrap no BigQuery (conferência dos intervalos) numera as linhas de cada grupo, sorteia `n` índices por réplica com
`RAND()` (`GENERATE_ARRAY(1, 2000)` × `GENERATE_ARRAY(1, n)`), junta pelo índice e tira `PERCENTILE_CONT(h, 0.5)` por
réplica; os percentis 2,5 e 97,5 das diferenças dão o intervalo. O placebo usa `GENERATE_DATE_ARRAY` de segundas-feiras
e as mesmas janelas. Na tela, a mesma conta roda em `lia.antes_depois` (numpy, semente 2026).

### Proposta para a gold (não aplicada)

Para mostrar na tela "pedidos que a LIA registrou × os demais" sem ler a silver no site (D57): coluna
`criado_pela_lia BOOL` (= `lia_chave_sync_nao_editar IS NOT NULL` em `slv_agenciamento_2026_itens`) na tabela de
movimentos e na view `gld_agenciamento_2026_sla_entregas`. Para medir o trecho e-mail → monday: a LIA gravar no item a
hora de recebimento do e-mail (`recebido_em`), e a gold levar `h_email_ate_registro`. Decisão do Caio.

### Limites

- Amostras: 134 Inbound depois (5,5 semanas); todos os intervalos com a janela do ano cruzam o zero. Ler como sinal, não prova.
- Sem causalidade: no mesmo período mudaram outras coisas (equipe, volume e mix de outubro); o placebo mostra que
  diferenças desse tamanho aparecem sem LIA (5 de 19 cortes).
- A janela do "antes" muda a leitura: com jul–20/09 (meses rápidos do Inbound) a piora parece maior. A regra adotada é a
  do ano (Caio, 30/10/2026).
- O "depois" cresce a cada carga; números mudam até a janela estabilizar (rodar de novo e trocar esta tabela).
- Pedidos ainda sem 1ª entrega não entram (como no SLA); se os lentos do "depois" ainda não foram entregues, o "depois"
  real pode ser pior.

## Interação e acessibilidade

- **Gráfico das semanas** (`role="region"` com descrição para leitor de tela): cada semana é um link `?semana=NN` com o
  texto completo ("Semana 39, de 21/09 a 27/09: 377 e-mails; não lead 328 (87,0%); lead 37 (9,8%); validação 12
  (3,2%)"); dica ao passar o mouse ou focar (só CSS: período, total e cada categoria com quantidade e %). Dentro do
  gráfico, ← → (e Home/End) andam entre as semanas e não trocam de página.
- **Extrato** (`lia.js`): clique ou Enter troca o bloco da esquerda (sai deslizando para cima em 150 ms e o extrato entra
  em 250 ms; com movimento reduzido, troca direta); a semana fica com `aria-current="true"` e as outras esmaecem; a URL
  acompanha (`?semana=NN`); "Voltar ao período" ou Esc restauram o bloco e devolvem o foco à semana. O bloco da esquerda
  é `aria-live="polite"`. Sem JS, o link abre a página com o extrato renderizado pelo servidor.
- **Pop-up do vídeo** (`lia_video.js`): `showModal()` (foco preso no painel), entra crescendo a partir do botão (~420 ms)
  e volta para ele ao fechar; Fechar, Esc ou clique no fundo fecham; o vídeo pausa ao fechar; o foco volta ao botão;
  setas e espaço dentro do pop-up não trocam de página.
- Sem `style=""` (larguras e alturas pelo `<style>` com nonce). Cores: trio validado na skill dataviz (#8f99e8 lavanda,
  #2400ff azul VIU, #d4890b âmbar; todos os pares, inclusive daltonismo); contraste baixo do lavanda e do âmbar
  compensado pelos números escritos. Movimento só com `prefers-reduced-motion: no-preference` e `html.js`. Conferido em
  1440×810, 1280×720, 1920×1080 (sem rolagem, com e sem extrato) e 390 px (sem rolagem lateral; pop-up com a lista
  embaixo).

## Histórico

- 03/11/2026 (revisão, tela cheia do vídeo): com o vídeo em tela cheia pelo próprio player, o portal deixava de se marcar
  como em tela cheia (`html.tela-cheia`, rótulo "Sair da tela cheia"); só a página inteira em tela cheia conta
  (`document.fullscreenElement === raiz` em `apresentacao.js`). Vídeo com **faststart**: o índice do MP4 (moov) ficava no
  fim do arquivo (o navegador pedia o fim dos 42,5 MB antes de tocar e o player ficava preto); refeito com
  `ffmpeg -c copy -map 0 -movflags +faststart`, sem recodificar (ffprobe: 106,13 s, H.264 1920×1080 + AAC, 3.184 quadros,
  iguais ao original; 42.536.010 bytes). Original em `_descartados/2026-11-03/app/static/video/`. Teste:
  `tests/test_revisao_20261103.py::test_video_da_lia_tem_o_indice_antes_dos_dados`. Pendente (Caio, em produção): conferir
  com `curl -s -D - -o NUL -H "Range: bytes=0-" <url>/static/video/lia-na-pratica.mp4` se o Cloud Run entrega a resposta
  inteira (limite de resposta HTTP/1 não confirmado).
- 03/11/2026 (validação, extrator): `tools/extrair_lia.py::meses` passa a ler o mês anterior a `--inicio` e o seguinte a `--fim` (arquivos gravados em UTC; 4 e-mails de 31/10 à noite estavam em `extracted_emails_2026-11.json`); filtro pela data em São Paulo mantido; dedup pelo último processamento dentro da janela (`ultimos_na_janela`); contagem separada em `montar_retrato()` (sem rede). Testes sintéticos em `tests/test_lia_extrator.py`.
- 03/11/2026 (validação, retrato): retrato regerado com `--fim 2026-10-31`: 2.164 = 1.880 / 200 / 84 (antes 2.160 = 1.876 / 200 / 84; cópia em `_descartados/2026-11-03/app/apresentacoes/gestao_orcamentos/lia/retrato_2160.json`). `tools/congelar_base.py --conferir` "Tudo certo" e `python -m app.conferir_base` "Pacote conferido".
- 03/11/2026 (validação, percentuais): partes pelo maior resto (`lia._maior_resto`, `_pct_partes`, `_pct_lados`): quadrantes dentro × fora e faixas (leads 74% + 26%, antes 74% + 27%), fração e semanas (1 casa, fecham em 100,0%), turnos e períodos; o "fora do expediente" do bloco de cima é o mesmo número do par. Teste `test_lia_percentuais_das_partes_fecham_em_100`.
- 03/11/2026 (validação, comentários): comentários de `lia/__init__.py` (TURNOS e FAIXAS_DIA), do `template.html` e do teste que citavam "54%" corrigidos (o 54% era a regra do SLA de 30/10; a tela usa o expediente da LIA, com o almoço dentro, hoje 50%).
- 03/11/2026 (validação, ficha): topo com os números de 2.164 e tabela de 03/11 em "Quando o inbound chega" com as faixas, os % e as taxas de lead da tela.
- 31/10/2026 (auditoria do Codex, F05 e F10): retrato fora do contrato (sem semanas, sem dias ou total zero, campos ausentes, JSON quebrado) vira a lâmina "Os números da LIA estão indisponíveis agora", sem erro (`lia.validar_retrato`, `RetratoInvalido`); rodapé próprio "Dados da LIA até dd/mm/aaaa · extraídos em …" (fim do retrato), no lugar da data da carga de entradas. Testes em `tests/test_auditoria_dados.py`.
- 30/10/2026: criada na V2 a partir do PRD de @cris; números da fonte; conferência acima.
- 30/10/2026 (noite, D-LIA-1): visão 2 auditada e refeita na régua do SLA (view gold de entregas; típico em horas e
  dias de trabalho, quartis, % em até 16 h), Inbound antes (01/01–20/09) × depois (21/09–29/10) com os outros tipos de
  input como controle, intervalos por bootstrap e placebo (recorte e janelas do Caio). Resultado: Inbound mais lento no
  ponto (13,7 → 15,7 h; 57% → 51% em até 16 h), dentro do acaso; sem ganho da LIA no SLA. Planilha manual (e-mail →
  carta) fora da tela, citada como outra régua. Título da seção: "LIA: e-mails, leads e tempo de entrega"; rodapé pelas
  tabelas do SLA.
- 30/10/2026 (noite, D-LIA-2, Caio): a análise de tempo sai da tela (fica nesta ficha); a página mostra só o resultado
  dos e-mails: 87% filtrados pela LIA, 270 levados à equipe, triagem poupada estimada (≈ 59 h a 2 min por e-mail,
  premissa a confirmar), 54% lidos fora do expediente, 9,4% de leads e as semanas. Extrator ganhou semanas e faixas de
  horário. Seção "LIA: e-mails lidos e filtrados"; rodapé de volta à tabela de entrada (o slide não lê a gold).
- 30/10/2026 (noite, D-LIA-3, Caio): hierarquia nova (2.047 lidos > 87% resolvidos sozinha > barra de fração em três
  partes); semanas ISO empilhadas em três cores, legenda com a fração, dica com quantidade e %; extrator com todos os
  dias.
- 30/10/2026 (noite, D-LIA-4, Caio): destaques por dia (mais e menos leads; segunda mais forte e sexta mais fraca, como
  tendência); extrato da semana ao clicar (ou `?semana=NN`); botão discreto "Ver a LIA na prática" com o vídeo em
  pop-up (a página do vídeo ficou oculta, endereço mantido); extrator com e-mails fora do expediente por dia e semana.
- 30/10/2026 (noite, D-LIA-5, Caio): destaques por data saem; entram os padrões do mercado — dia da semana (sem
  diferença clara; teste de permutação p = 0,32) e período do dia (tarde concentra 52% dos leads; χ² p < 0,001), com o
  mapa dia × período; extrato da semana sem datas, com a divisão por período; extrator com o período do dia por dia.
- 30/10/2026 (Caio, página mais limpa): saem da tela a frase "De 21/09 a 29/10, a LIA leu" (período no título do
  gráfico; frase mantida para leitor de tela), as legendas sob a fração, a nota de 12/10, as leituras de dia da semana e
  período e a nota do gráfico; textos e ressalvas ficam nesta ficha. Gráfico e mapa ganham a altura liberada. CSS órfão
  em `_descartados/2026-10-30/app/static/estilo_lia_textos.css`.
- 30/10/2026 (Caio, 2ª rodada): bloco da esquerda sobe para o topo, alinhado aos números da direita; "87% a LIA resolveu
  sozinha." (sem "garantiu que não era lead"); fração logo abaixo; botão do vídeo embaixo do gráfico, no cartão; gráfico
  mais baixo para caber o botão. Pop-up igual.
- 30/10/2026 (Caio, 3ª rodada): triagem poupada, fora do expediente e o mapa ("Quando chegam os leads", com legenda de
  escala) descem para a coluna da esquerda, sob a fração; o cartão da direita fica só com o gráfico semanal; colunas 6/6;
  o extrato troca a coluna inteira.
- 30/10/2026 (Caio, 4ª rodada): gráfico semanal no padrão de Demanda e SLA (cartão, título, legenda, colunas), com altura
  própria a partir do 87%; botão do vídeo no cabeçalho do cartão; título "E-mails por semana, 21/09 a 29/10".
- 30/10/2026 (Caio, 5ª rodada): bloco de cima achatado (legenda da fração numa linha); embaixo, "O que a equipe ganhou"
  (≈ 59 h e ≈ 11 h por semana, 1.777 não abertos e "1 em cada 8" chega à equipe, 54% fora do expediente) e "Quando chegam
  os leads" (barra de 100% por período; média inteira por dia útil com a ressalva "ainda sem padrão firme"); mapa de
  calor fora da tela.
- 30/10/2026 (noite): a linha "87% a LIA resolveu sozinha" saiu da tela por decisão do Caio; a barra de fração continua mostrando os não leads (86,8%).
- 30/10/2026 (Caio, 6ª rodada): ganho num painel lavanda ("O que a LIA tirou das mãos da equipe"); "Quando o inbound
  chega" num cartão flutuante, com e-mails de inbound por período (tarde 37%, e 52% dos leads) e média inteira de
  e-mails por dia útil (quinta 66 em destaque, sem frase de padrão); a nota "sem padrão firme" ficou só na ficha.
- 30/10/2026 (Caio, 7ª rodada): botão do vídeo sai do cartão e vai para cima dele, à direita, com play num círculo azul,
  sombra em camadas e halo que acende no hover/foco; pop-up igual (cresce do botão, devolve o foco).
- 30/10/2026 (Caio, 8ª rodada): "Quando o inbound chega" sobre os 2.047 — turnos do expediente (manhã 10h–13h 20%, tarde
  14h–19h 26%, fora 54%, igual ao bloco de cima) e dia da semana com média inteira por dia e total (soma 2.047; feriado na
  segunda); extrator com `turnos`; paleta do portal (não lead `--t-internos`, lead `--t-inbound`, validação `--atencao`);
  botão "A LIA na prática" refeito (pill de vidro, play arredondado com degradê e halo).
- 30/10/2026 (Caio, 9ª rodada): extrato da semana retirado (clique e `?semana=`; a dica e o foco ficam); prévia do vídeo
  em miniatura de player no lugar do botão; grade única com o cartão do gráfico na mesma faixa dos dois blocos de apoio.
- 30/10/2026 (Caio, 10ª rodada): "O ganho para a equipe" com três colunas centralizadas e textos curtos; textos de apoio
  fora da tela (registrados acima); campo `CAPA` para a miniatura; cores e legendas iguais às de Talentos e Demanda.
- 30/10/2026 (Caio, rodada final): expediente da LIA com almoço 12h–13h (fora 1.130, 55%; SLA inalterado); "Quando o
  inbound chega" como lista das faixas do dia (antes das 10h 11%); dia da semana fora da tela; dica da semana ao lado da
  coluna; eixo mais delicado; semana 44 no padrão de parcial do portal; extrator com `horas`.
- 30/10/2026 (Caio): "Quando o inbound chega" volta à barra única, agora em duas barras alinhadas (e-mails × leads) em
  ordem expediente | fora, com chaves acima, legenda em pílulas e % só nos segmentos grandes; "55% dos e-mails chegam fora
  do expediente, mas só 32% dos leads"; extrator com `horas_lead`; mais sombra nos cartões flutuantes.
- 30/10/2026 (Caio): três barras (leads, não leads, validação) em dois quadrantes dentro × fora do expediente com escala
  comum; almoço dentro do expediente (fora = 1.020, 50%); validação hachurada no padrão do ano anterior da Demanda; rampa
  ordinal dos azuis do projeto; contraste do texto por cor da faixa; extrator com `horas_nao_lead`.
- 30/10/2026 (Caio): página da LIA aprovada e entregue ("está perfeito, entregamos").
