# Ficha — SLA de entrega (aba "SLA", antes "Prazo")

**Navegação revisada em 28/10/2026:** o gancho do rodapé leva à Previsão: "Quantos pedidos devem chegar até o fim do mês e do ano?". O estudo "Como medimos" continua no botão Estudo, como aprofundamento opcional. Setas na sequência principal: SLA → Previsão; dentro do estudo, mantidos os slides e a saída para Previsão. Sem mudanças nos cálculos ou no layout.

## V2 (30/10/2026, Caio) — estudo "Como medimos" enxugado de 7 para 5 slides — **só na V2** — ler primeiro

Vale só na cópia de trabalho `PPD-AGENCIAMENTO-SLA-V2` (porta 8400). O original congelado (8100) e a cola (8200)
seguem com os 7 slides. Pedido do Caio: "funilar" o estudo para quem vai apresentar (o gerente dele, que não é da área).
Nenhuma regra de negócio mudou: os números da tela são os mesmos de antes, das mesmas funções.

**Numeração nova (`/viu-agenciamento/sla/como-medimos#n`):**

| # | Título | Era |
|---|---|---|
| 1 | Como chegamos ao tempo da equipe | 1 (sem mudança) |
| 2 | A maioria é rápida. Poucos demoram muito. | 2, agora **num passo só** (sem `?passo=`) |
| 3 | Quantos saem em até 2 dias, e quanto do tempo levam? | **3 + 4 unidos** |
| 4 | Foi um mês ruim, ou é sempre assim? (título por regra U8) | 5 |
| 5 | Onde o tempo trava? | 6; agora o **último**, com a saída do estudo |
| — | O que os dados nos mostraram (conclusão, "resumão") | 7 de 7: **retirado** |
| — | Em que tipo de pedido o tempo trava? | fora desde a D64; com `ESTUDO_TIPO = True` volta como 6 (último) |

**Slide 2 num passo só (regra nova X10).** Fica a visão do antigo passo 3 (a preferida do Caio): histograma com as faixas
do boxplot no topo (rápidos, comuns, demorados, fora da curva, em % de todos os orçamentos do recorte, X6) e as barras
nas cores dessas faixas; alfinetes do típico (mediana) e da média; ao lado, "Como ler" com três números: típico
(`mediana_txt`, "metade dos pedidos sai antes disso"), média (`media_txt`, "puxada para cima pelos casos longos" quando
X4/D12 diz que a média destoa; senão "perto do típico") e fora da curva (`box.pcts[3]`, com `n_fora` e o limite
`box.lim_txt`). Faixa do pé = `exploracao.insight` (X10, `_insight_unico`): "Poucos pedidos demoram muito: os F% fora
da curva, acima de L, puxam a média para M. O pedido típico leva T. Por isso medimos pelo típico (a mediana)."
Variantes: média perto do típico; ninguém fora da curva; 1% no singular. Saíram da tela os quadros Formato (assimetria
e régua), Sino (Q-Q) e o boxplot do painel, a navegação dos quadros e o `?passo=` (o endereço antigo abre normal; o
parâmetro é ignorado). Os cálculos deles (X2–X5, X7–X9 e os insights 1–3) continuam em `sla/calculos.py`. Por que essa
forma: um gráfico só, com rótulos diretos, mostra as três coisas que o leigo precisa ver juntas (onde fica a maioria,
onde ficam o típico e a média e quem está fora da curva); o "Como ler" repete os números com a cor da marca, para o
apresentador ler em voz alta sem interpretar o gráfico.

Carga de 30/10/2026 09:01 (jan–set, Todos, 2.346 orçamentos): 25% rápidos, 50% comuns (7 a 28 h), 18% demorados (até
59 h), **7% fora da curva (171 pedidos acima de 59 h)**; típico **14 h**, média **25 h**.

**Ajustes de tela do estudo (30/10/2026, tarde, Caio) — só na V2; nenhum número mudou.**

- **Selo do canto superior direito fora de todos os slides** ("jan a set de 2026 · 2.346 orçamentos medidos · Todos";
  Caio: "não faz sentido ali"). O texto (`recorte`, R1) continua no HTML só para o leitor de tela
  (`<p class="so-leitor estudo-recorte">`); o grupo está no seletor de talentos, a data no rodapé datado e o n no texto
  dos gráficos e, no slide 3, embaixo de cada barra de pedidos. Os títulos passam a caber numa linha.
- **Slide 2, "Como ler" refeito (opção b: painel mais rico; regra X11).** O gráfico já crescia pela altura (proporção
  fixa 580 × 312), então alargá-lo deixaria o mesmo vazio; o painel passou a ocupar a altura do gráfico (topo na faixa
  colorida, pé na linha de base) em três partes: (1) **típico e média lado a lado** (14 h / 25 h, com a frase de cada
  um); (2) **régua das horas**, na mesma escala do eixo do histograma (0 até o fim de "60 h ou mais"), com o alfinete do
  típico (traço cheio) e da média (tracejado âmbar), a **seta do puxão** entre eles com "+N h" e o trecho vermelho dos
  fora da curva; (3) **fora da curva em 100 quadrados** (os `box.pcts[3]` vermelhos no fim, como no gráfico) com "N
  pedidos acima de L: olhar caso a caso". **X11** (`_puxao`): N = média escrita − típico escrito (a conta que o leitor faz
  com os números da tela: `_arred(média)` − valor de `_h_meta(mediana)`; com o típico de 1 casa, 1 casa; nunca negativo).
  A seta e o "+N h" só aparecem quando a média destoa (X4/D12, `media_relevante`).
- **Slide 3 mais cheio (as faixas de W2 de volta como detalhe).** O waffle (17,5em) e as barras (2,5em de altura) cresceram;
  os quadrados e as barras usam as cinco faixas em tons da família de cada lado: lavanda para "em até 2 dias" (até 1 dia
  `#3a46b4`, 1 a 2 dias `#8590dc`) e coral para "passam de 2 dias" (2 a 3 `#f09a8c`, 3 a 5 `#cf5446`, mais de 5 `#932c24`;
  paleta passada no validador da skill de dataviz: CVD e visão normal ok; os tons claros ficam abaixo de 3:1 no branco e
  por isso sempre vêm com o número ao lado). O lado Quantidade espelha o Tempo, na mesma linha da grade (subgrid): rótulo,
  barra de 0 a 100 em segmentos das faixas com o número grande (56 / 44), mini legenda com o % de cada faixa e "de cada
  100 pedidos · N pedidos de jan a set" (N = soma das contagens das faixas do lado, `tempo_cem.linhas[].n`). No Tempo,
  cada barra se divide nas horas de cada faixa (V3) e a mini legenda dá o % das horas de cada uma. Destaque segue nos
  A/B e HA/HB.
- **Slide 4:** quadro do gráfico mensal de 1000 × 230 para 1000 × 282 (base 224 → 276 em `_meses`), usando o espaço do
  selo e da faixa do pé; só a altura do desenho. **Slide 5:** mais respiro entre o seletor e a primeira etapa (`.trava-meio`).
- **Faixa de conclusão do pé fora da tela nos slides 2, 3, 4 e 5 — fora da tela por decisão do Caio, 30/10/2026.** A
  caixa lavanda com a frase-resposta saiu para dar respiro (o slide 4 entrou junto, pela coerência). Os ganchos ficam
  como estavam, embaixo à direita. As frases **continuam calculadas** pelas mesmas regras (cola e conferência) e ficam
  registradas aqui (carga de 30/10/2026, Todos):
  - Slide 2 (X10, `exploracao.insight`): "Poucos pedidos demoram muito: os 7% fora da curva, acima de 59 h, puxam a média
    para 25 h. O pedido típico leva 14 h. Por isso medimos pelo típico (a mediana)."
  - Slide 3 (V10, `tempo_cem.resposta`): "Mais da metade dos pedidos (56%) sai em até 2 dias e leva 16% das horas da
    equipe; os outros 44% passam disso e levam 84%."
  - Slide 4 (U8, `meses_estudo.rodape`): "Não é sazonal: todo mês, de 40% a 51% dos pedidos passam de 2 dias. O problema
    é o processo, não o mês — é nele que está a solução."
  - Slide 5 (K, `travas.rodape`): "O tempo trava principalmente em dois pontos: Em elaboração (só até jul) e Fila de
    entrada somam 60% do tempo travado."
  - O slide de tipo de pedido (desligado, `ESTUDO_TIPO = False`) mantém a faixa dele; não foi mexido.
  Com o espaço liberado: o gráfico do slide 2 cresce sozinho (mesma proporção, mais altura), o waffle do slide 3 passa a
  19,5em e as barras a 2,8em, e o gráfico do slide 4 ganha a altura acima.
- **Saída do último slide (5, ou o de tipo quando ligado) — fora da tela por decisão do Caio, 30/10/2026.** Saíram os links
  "Voltar ao SLA →" e "ou seguir para a próxima: LIA →" (a macro `saida()` fica no template, sem chamada). O sinal de fim,
  sem texto, é o próprio ✕ do topo: no último slide ele ganha fundo azul VIU e ícone branco (`.fechar-fim`), nome
  "Fim do estudo: voltar ao SLA" para o leitor de tela, e um anel azul que se abre **uma vez** ao chegar (0,9 s, só com
  movimento permitido e JS, 1ª visita; `@keyframes fim-anel`). O "Próximo" do pé, que ficava desligado no último slide,
  agora segue para a próxima página da sequência (a mesma da seta →, D62; `apresentacao.js`).

| Recorte (carga 30/10, jan–set) | Típico | Média | Puxão | Fora da curva | Pedidos por faixa (até 1 · 1–2 · 2–3 · 3–5 · >5 dias) | Horas por faixa | N em até 2 dias / acima |
|---|---|---|---|---|---|---|---|
| Todos | 14 h | 25 h | +11 h | 7% (171 acima de 59 h) | 31 · 25 · 15 · 17 · 12 | 5 · 11 · 12 · 20 · 52% | 1.303 / 1.043 |
| Exclusivos | 12 h | 23 h | +11 h | 7% (111 acima de 52 h) | 37 · 25 · 14 · 14 · 10 | 6 · 13 · 11 · 18 · 52% | 1.003 / 607 |
| Não exclusivos | 20 h | 30 h | +10 h | 9% (63 acima de 64 h) | 18 · 23 · 20 · 23 · 16 | 2 · 10 · 13 · 25 · 50% | 297 / 426 |

Conferido na página servida (porta 8400) nos três recortes: as faixas somam A e B (56 = 31 + 25; 84 = 12 + 20 + 52) e os N
somam o n do recorte (1.303 + 1.043 = 2.346). Capturas em `.playwright-mcp/v*_s{2,3,4,5}_*.png` (1440×810, 1440×900,
1280×720, 1920×1080 e 390 px). Trechos retirados em `_descartados/2026-10-30/app/templates/como_medimos_v2_selo_comoler_slide3.html`.

**Slide 3 unificado (regras V9 e V10; W2–W3 e V1–V3 sem mudança).** Layout em "T": título em cima; à esquerda,
"Quantidade · de cada 100 pedidos", o waffle de 100 em **dois tons** (A = em até 2 dias, lavanda; B = passam de 2 dias,
coral) e as duas chaves A e B; à direita, "Tempo · de cada 100 horas da equipe", a parte das horas que cada lado leva
(barra de 0 a 100 e o número, V3: soma das horas da faixa ÷ soma de todas as horas, inteiros pelo maior resto) e o
típico de cada lado (V9: mediana exata das horas dos pedidos com h ≤ 16 h e com h > 16 h, escrita por `_h_meta`). As
linhas A e B das duas metades ficam na mesma altura. A, B, HA e HB vêm de `tempo_cem` (os mesmos % do antigo slide 3,
`_cem_pcts`). A métrica do "levam X" é a do antigo slide 4: **parte das horas da equipe** (não mediana nem média); o
típico de cada lado é um acréscimo (V9), para a leitura "o pedido típico de cada lado". Resposta no pé (V10,
`_resposta_cem_tempo`): "Mais da metade dos pedidos (A%) sai em até 2 dias e leva HA% das horas da equipe; os outros B%
passam disso e levam HB%." (variantes: Metade / Menos da metade; B = 1 no singular; A = 0 e B = 0 em frase própria).
Gancho: o mesmo V7 ("Mas esses B% foram um mês ruim, ou é sempre assim?"), agora para o #4.

| Grupo (carga 30/10, jan–set) | n | A em até 2 dias | B acima | Horas de A | Horas de B | Típico A | Típico B |
|---|---|---|---|---|---|---|---|
| Todos | 2.346 | 56% | 44% | 16% | 84% | 7 h | 29 h |
| Exclusivos | 1.610 | 62% | 38% | 19% | 81% | 7 h | 29 h |
| Não exclusivos | 723 | 41% | 59% | 12% | 88% | 9 h | 30 h |

A, B, HA e HB conferem com a tela de antes (capturada no servidor 8400 antes da troca). `tools/conferir_estudo.py`
(atualizado: compara também o típico A/B, V9, e lê os textos na numeração nova) rodou em 30/10/2026 contra o BigQuery
(identidade `caio.barroso@viu.com.br` conferida pela ferramenta, só SELECT; carga 2026-10-30 12:01:46 UTC): **tudo
bate** nos 3 grupos (n 2.346 / 1.610 / 723; típico 14,195 / 11,818 / 19,642 h).

**O que saiu da tela (para onde foi):**
- Slide 3 antigo: as cinco faixas do waffle (31 / 25 / 15 / 17 / 12), a linha do processo em 3 passos e a curva
  acumulada com os marcos de 80% e 90%. Slide 4 antigo: os cartões com as faixas por linha, a frase em frações (V5), as
  notas Prazo e Fluxo (V6) e a faixa V7 com "É aí que está o ganho: encurtando esses casos, a fila anda mais rápido e o
  mesmo time dá conta de mais pedidos." (segue calculada em `tempo["rodape"]`).
- Conclusão (D44): cinco achados, "Onde olhar com mais detalhe" e "O que isso pede" (cálculo Z1–Z8 mantido em
  `calculos.conclusao`, ainda montado em `apresentacao.py` para a cola e a conferência).
- Template, CSS, JS e testes antigos: `_descartados/2026-10-30/` (`app/templates/como_medimos_slides_3_4_8.html`,
  `app/templates/como_medimos_slide2_passos.html`, `app/static/estilo_estudo_slides_3_4_8.css`,
  `app/static/estilo_estudo_slide2_passos.css`, `app/static/apresentacao_passos_slide2.js`,
  `tests/test_estudo_slides_3_4_8.py`); uma linha por item no `LEIAME.md` de lá.

**Saída do estudo:** o slide 5 termina com "Voltar ao SLA →" (mesmo filtro de talentos) e "ou seguir para a próxima:
LIA →" (o mesmo destino da seta → no último slide, D62). Teclado: ← / → trocam de slide direto (o slide 2 não tem mais
quadros); → no último slide e ← no primeiro seguem a sequência (D62).

**Movimento (D46, mesmo padrão):** slide 2 — barras sobem do eixo; contagens e alfinetes surgem no fim. Slide 3 — o
waffle enche linha a linha (máscara única) e as barras das horas crescem logo depois (A, depois B). Tudo sob
`prefers-reduced-motion: no-preference` + `html.js` + `:not(.entrou)`, só na 1ª visita, até ~1,1 s, sem loop.

**Ferramentas:** `tools/conferir_estudo.py` atualizado (V9 e numeração nova); `tools/conferir_layout.mjs` conta os
slides da página (não fixa mais 8). A cola (`gestao_orcamentos/cola.py`) ainda tem as falas dos ids
`estudo-2-1..3`, `estudo-3`, `estudo-4`, `estudo-7`/`8` do estudo antigo; na V2 ela não é usada (`SINC=off`).

## Estado vigente (26/10/2026, D49) — ler primeiro (original; na V2, o estudo segue o bloco acima)

**Situação:** página **pronta, com a meta a oficializar** ("O que falta": "Pronta · meta a oficializar"). Nenhuma regra de
negócio mudou na batalha de 26/10 (D49); mudaram textos, movimento, navegação e rastreabilidade. Esta seção substitui
as nove linhas de "Situação" que ficavam empilhadas aqui (cópia em `_descartados/2026-10-26/versoes_anteriores/`).

**Regras que valem na tela (resumo; detalhe nas seções indicadas):**

| Regra | O que diz | Onde está o detalhe |
|---|---|---|
| C1 | Pronto = 1ª chegada em Aguardando Feedback (1º passo `fase = 'cliente'`) | seção 4 |
| C2 + D-SLA-2 | Horas da equipe = horas úteis (seg–sex, 10h–13h e 14h–19h, sem feriados) de todos os passos `equipe` antes de C1, com a Entrada, **sem "Em elaboração - Retorno Marca/Executivo"**; recalculadas em `app/expediente.py` até a v2 da gold (PD21) | 0.4, 0.6 |
| C3c (D54) | Prazo do cliente na tela = **dias úteis com fração** do pedido à 1ª entrega (todos os status; fração = horas do expediente decorridas ÷ 8 h do dia), mediana com 1 casa ("1,8 dia útil") e exemplo da semana tirado do mesmo valor; revê a C3b (inteiro), que fica só no código | 000000000000.2 |
| C3b | Dias úteis inteiros (viradas de dia útil); **saiu da tela na D54**, segue em `mediana_dias_uteis` e no `dias_uteis` do exemplo | 00000000000.2 |
| D-SLA-1 (C4) | Mês de referência = **mês da 1ª entrega** (não o mês de entrada) | 0.1, 0.4 |
| C7 + A1/A2 | Números do ano só com meses completos de entrega (jan–set na carga de 26/10); mês vigente vazado, com % e típico só a partir de 30 entregas (`MIN_PARCIAL`) | 0.4 |
| D-SLA-7 (D38, C6) | **Meta sugerida = metade dos orçamentos prontos em até 2 dias de trabalho (16 h)**; não oficial (pedido nº 1 do "O que falta"). `LIMITE_DIAS = 2`, `META = 0.50`, `META_H = 16` em `sla/calculos.py` | 00.1 |
| C5, C8 | Faixas até 1 dia (≤ 8 h) / 1 a 2 dias (≤ 16 h) / acima de 2 dias; "até 2 dias" e "até 1 dia" meio para cima, "1 a 2 dias" por diferença, "acima" = 100 − "até 2 dias" | seção 4 |
| C6 (`_h_meta`) | Típico do mês com 1 casa entre 15,5 e 16,5 h (acima de 16 arredonda para cima, abaixo para baixo) | 00000000000.1 |
| E1–E3, X1–X7, W, V, U, K, J, Z | Estudo "Como medimos", slides 1–8 | mapa abaixo |

**Mapa desta ficha.** As seções com zeros à esquerda são camadas datadas, da mais nova (mais zeros) para a mais antiga.
A renumeração (com as referências do PRD, do CLAUDE.md e dos testes) fica para depois de 28/10, para não quebrar links
na véspera da reunião.

| Seção | Assunto | Vale hoje? |
|---|---|---|
| este bloco | estado vigente, números da carga da reunião, conciliação das bases | **sim** |
| 000000000000 | D54: rótulo curto da meta, C3c (dias úteis com fração) com SQL | **sim** |
| 00000000000 | batalha 2, 1ª leva: vocabulário, selo do mês, C3b com SQL | **sim** |
| 0000000000 | D46: movimento do estudo (a D49 estende a regra às páginas) | **sim** |
| 000000000 | D45: base congelada, exemplo fixo, conferências automáticas | **sim** |
| 00000000 · 0000000 · 000000 · 00000 · 0000 · 000 | slides 8, 7, 6, 5, 4 e 3 do estudo (D44, D43, D42 revista, D41, D40, D39) | **sim** (números da carga de 23/10; os de hoje estão abaixo) |
| 00 | D38: meta de 2 dias, estudo em linguagem simples | **sim**; prevalece sobre a seção 0 |
| 0 | D37: D-SLA-1 a D-SLA-6, slide 2 refeito (0.8) | sim, **menos** a meta de 75% em 3 dias e a faixa "2 a 3 dias" (revistas pela D38) |
| 1–10 | versão de 24/10 (D34, D35) | registro; continuam úteis a 1.1 (colunas), a 6 (SQL base do expediente) e a 8 (limites) |

### Números da carga da reunião (26/10/2026)

Carga: `_processado_em` **26/10/2026 09:01 (São Paulo) = 12:01:34 UTC**, dados até 25/10, meses completos jan–set.
Conferido no BigQuery (só SELECT) na mesma carga: n e típico dos três grupos e as leituras dos slides 3–8
(`tools/conferir_estudo.py`, resultado em `docs/validacao/estudo_2026-10-26.json`: **tudo bate**) e a C3b (SQL
00000000000.2: 2 / 1 / 2). As faixas e os meses vêm da mesma `entrega()` conferida pela SQL 0.6; aqui estão lidos da
tela. Se a carga da reunião for outra (27 ou 28/10), rodar `python tools/checar_reuniao.py` e trocar esta tabela.

| Elemento da tela | Texto | Regra | Função (`sla/calculos.py`) | SQL | Todos · Exclusivos · Não exclusivos |
|---|---|---|---|---|---|
| Recorte (n) | "N orçamentos medidos" (estudo) e leitor de tela do seletor | C1, C4, C7, C10 | `entrega()`, `recorte()` | 0.6 | 2.347 · 1.609 · 725 (13 sem talento só em Todos) |
| Resposta | "Levamos **X h** de trabalho da equipe … para entregar um orçamento ao cliente." | C2, D-SLA-2 | `entrega()` | 0.6 / 00.4 | 14 h · 12 h · 20 h (14,25 · 11,83 · 19,64 h) |
| Apoio | "**X,Y dias úteis** no calendário para o cliente receber" + exemplo "pedido na segunda às 10h, resposta na terça à tarde" (D54) | C3c | `entrega()["dias_uteis_cliente"]` + `expediente.dias_uteis_fracao` | 000000000000.2 | 1,8 · 1,6 · 2,5 (exatos 1,8477 · 1,5635 · 2,4999; dias corridos 2,8 · 2,0 · 4,0; C3b inteiro de antes 2 · 1 · 2) |
| Legenda do ano | "até 1 dia A%", "1 a 2 dias B%", "acima de 2 dias C%" | C5, C8 | `entrega()` / `_faixas()` | 0.6 | 31/25/44 · 37/25/38 · 18/23/59 |
| Linha sob a legenda | "C% passam de 2 dias de trabalho" (= "acima de 2 dias") | C8 | `entrega()` | 0.6 | 44 · 38 · 59 |
| Mensagem do típico | "O típico já sai em até 2 dias" / "O típico deste grupo ainda passa de 2 dias (X h)" | C6 | `meta_tipico()` | 0.6 | já sai · já sai · ainda passa (20 h) |
| Linha da meta | "meta sugerida: 2 dias de trabalho" numa linha, na linha do título do cartão (celular: sobre a linha); dica e leitor de tela com "metade em até 2 dias de trabalho (16 h)" (D54) | D-SLA-7 | constantes `META`, `META_H`, `LIMITE_DIAS` | — | 50% |
| Trilhos (% em até 2 dias, jan–set) | topo de cada coluna | C5, C8 | `entrega()["meses"]` | 0.6 | Todos 60 · 55 · 58 · 50 · 49 · 49 · 57 · 59 · 59 |
| | | | | | Exclusivos 64 · 53 · 61 · 60 · 56 · 54 · 66 · 71 · 61 |
| | | | | | Não exclusivos 56 · 57 · 52 · 25 · 30 · 40 · 43 · 25 · 53 |
| Orçamentos por mês | leitor de tela de cada coluna | C4 | idem | 0.6 | Todos 111 · 108 · 159 · 215 · 201 · 288 · 548 · 378 · 339 |
| | | | | | Exclusivos 75 · 55 · 125 · 153 · 151 · 192 · 344 · 277 · 237; Não exclusivos 32 · 53 · 33 · 60 · 50 · 96 · 200 · 100 · 101 |
| Típico do mês (selo) | sob cada coluna | C6 (`_h_meta`) | `entrega()["meses"]` | 0.6 | Todos 13 · 15,7 · 15 · 16,4 · 16,4 · 16,5 · 13 · 13 · 14 h |
| Mês vigente | "out, mês em andamento (dados até 25/10): P% … de N entregas; típico X h. Ainda vai mudar." | A2, A3 | `entrega()` | 0.6 | 52% de 267, 15 h · 65% de 173, 11 h · 29% de 91, 26 h |
| Slide 1 | exemplo do dia (muda por dia, E1) | E1–E3, C3b | `exemplo()` | 6.5 (passos do projeto) | 26/10, Todos: "[Findmykids] Chaiany \| Segurança Familiar": Entrada 19 min, Elaboração 2h53, Revisão 3h03 = **6h15**; 1 dia útil; 5 dias aguardando (em aberto) |
| Slide 2 | histograma, faixas, típico × média, cauda, sino, faixas do boxplot | X1–X6 | `exploracao()` | 0.6 + 6.7 | Todos: 56/32/12% (máx. 515 h); típico 14 h, média 25 h; cauda +7,2; 69 orçamentos acima de 93 h no sino; 25/50/18/7% (7 h · 28 h · 59 h); 171 fora da curva, 53 deles pacotes |
| Slide 3 | "De cada 100 pedidos…" + curva acumulada | W1–W7 | `cem_pedidos()` | 000 | Todos 31/25/15/17/12 → 56/44; 80% em 4 dias (31 h), 90% em 6 dias (46 h) · Exclusivos 62/38 · Não exclusivos 41/59 |
| Slide 4 | % dos pedidos × % das horas | V1–V8 | `tempo_cem()` | 0000 | 56/16 · 44/84 (horas por faixa 5/11/12/20/52) · Exclusivos 62/19 · 38/81 · Não exclusivos 41/12 · 59/88 |
| Slide 5 | "passam de 2 dias" por mês | U1–U9 | `meses_estudo()` | 00000 | Todos 40 · 45 · 42 · 50 · 51 · 51 · 43 · 41 · 41 → "padrão"; Exclusivos 29–47 → "padrão"; Não exclusivos abr, mai, ago 70–75 contra 43–60 → "sazonal"; 83 pedidos acima de 10 dias (Todos) |
| Slide 6 | % do tempo travado por status | K1–K8 | `travas()` | 000000 | Em elaboração (só até jul) 41% + Fila de entrada 19% = 60% · Exclusivos 65% · Não exclusivos 54% |
| Slide 7 | % que passa de 2 dias por tipo de input | J1–J9 | `tipos_pedido()` | 0000000 | Mercado 45% (1.265) · Inbound 43% (637) · ViU 21% · Proativo 67% (128) · Interna 68% (74) · Globo 26% |
| Slide 8 | seis achados | Z1–Z8 | `conclusao()` | 00000000 | 14 h · 56% · 84% · todo mês · 60% · 43–45% (Exclusivos 12 h · 62 · 81 · todo mês · 65 · Inbound 43%; Não exclusivos 20 h · 41 · 88 · abr, mai e ago · 54 · Mercado 59%) |

### Conciliação das bases (de "pedidos que chegaram" a "orçamentos medidos")

| Base | Carga de 26/10 | Regra | Onde |
|---|---|---|---|
| Pedidos recebidos em 2026 (até 25/10) | 5.556 | E1 do Início, mês de entrada | Início, Atendimento |
| Entregues ao cliente de jan a set (mês da entrega) | 3.969 (241 + 269 + 338 + 386 + 504 + 479 + 672 + 565 + 515) | A24, linha "− Entregues ao cliente" | Atendimento |
| Entregues no mesmo período com o ciclo completo na gold do SLA | 3.553 na carga de 23/10 (`cobertura()`, D-SLA-4; fora da tela) | R1 da gold do SLA | estudo (cálculo) |
| **Orçamentos com tempo medido** (jan–set) | **2.347** (59% dos 3.969) | C1, C4, C7; histórico de status completo | SLA e estudo |

Os não medidos são sobretudo de jan–mai (antes de o board registrar todos os status) e um pouco mais rápidos (validação da D37,
PRD seção 8: viés pequeno e conservador). Mostrar ou não essa ponte na tela é decisão do Caio (G2-6, PRD 9.7).

**Mudança entre cargas sem aviso:** de 23/10 para 26/10, jan–set passou de 2.348 para 2.347 (Todos) e de 1.610 para
1.609 (Exclusivos), com os não exclusivos iguais (725). A R1 da gold tira da base o projeto que volta à equipe depois da
1ª entrega e o devolve quando sai de novo; sem um retrato da carga anterior não dá para dizer qual `projeto_id` saiu. O
retrato por mês fechado (G2-14, item 3: n, % em até 2 dias e típico por grupo gravados a cada carga, com alarme) fica
como próximo passo; até lá, a conferência é `tools/conferir_estudo.py --anterior <json>`, que avisa leituras que mudaram.

## 000000000000. D54 — rótulo curto da meta e dias úteis com fração (26/10/2026)

Pedidos do Caio e do gerente (26/10/2026). Nenhuma regra das horas da equipe, da meta ou das faixas mudou.

### 000000000000.1 Rótulo da linha da meta

| Antes | Agora | Por quê |
|---|---|---|
| "meta sugerida: metade em até 2 dias de trabalho (16 h)", em até 3 linhas sobre os meses sem barra | **"meta sugerida: 2 dias de trabalho"**, numa linha, com um traço tracejado igual ao da linha. Na mesa (1920, 1850, 1440, 1280 px) fica à direita da **linha do título do cartão** (`.meta-chave`); no celular (barras deitadas, `@container palco (width < 600px)`) fica sobre a própria linha, acima das barras; entre 600 e 860 px (ou tela alta) desce para baixo do título, porque o alto à direita é da lupa (R06) | sobre os meses, o rótulo de uma linha cobria a barra de setembro e o contorno do mês parcial (medido: 1280 px, rótulo 178 px num vão de 163 px) e, em novembro, cobriria outubro. O detalhe "metade em até 2 dias de trabalho (16 h)" fica na dica (`title`) e no leitor de tela da figura ("meta sugerida, ainda não oficial, de metade dos orçamentos (50%) prontos em até 2 dias de trabalho (16 horas)") |

Conferência (Chrome headless, CDP, carga de 26/10): rótulo numa linha, sem tocar barra, total, número de faixa, mês
ou selo em 1920×1080, 1850×1030, 1440×900, 1280×800 e 390×844 (celular), nos três grupos; sem rolagem lateral. Letra
do rótulo: 15,8 px (1920), 15,1 px (1850), 11,3 px (1440 e 1280), 9,9 px no celular (o mesmo tamanho de antes).

### 000000000000.2 C3c — dias úteis com fração até o cliente receber (regra, SQL e resultado)

**Pedido do gerente:** ver se o prazo do cliente está mais perto de 2 ou de 3 dias (o inteiro da C3b não mostrava).

**Regra (`app/expediente.py::dias_uteis_fracao`):** tempo de calendário útil entre o pedido (`entrada` do passo 1) e a
1ª entrega ao cliente (`entrada` do 1º passo `fase = 'cliente'`, C1), **contando todos os status** (inclusive espera e
"Em elaboração - Retorno Marca/Executivo"), porque é a visão do cliente. Cada dia útil (seg–sex, sem os feriados da
R14, `sem_expediente`) vale 1; a fração do dia = horas do expediente decorridas ÷ horas do expediente do dia (10h–13h
+ 14h–19h = 8 h). Noite, almoço, fim de semana e feriado não contam; pedido fora do expediente começa a contar na
abertura do próximo dia útil. Como todo dia útil tem 8 h, C3c = horas do expediente do intervalo ÷ 8. Exemplos
(testes): segunda 10h → quarta 10h = 2,0; → quarta 15h = 2,5; segunda 18h → terça 11h = 0,25; sexta 17h → segunda 12h
= 0,5; quarta 01/04 10h → segunda 06/04 10h = 2,0 (Sexta-feira Santa); sexta 20h → segunda 12h = 0,25.

**Na tela (`sla/calculos.py::dias_uteis_cliente`, campo `dias_uteis_cliente` de `entrega()`):** mediana dos meses
completos do grupo (mesmo universo do herói: C4, C7, C10), **1 casa, meio para cima (C8)**, com vírgula; "dia útil"
abaixo de 2 (como a E3), "dias úteis" a partir de 2; abaixo de 0,05, "no mesmo dia". **Exemplo da semana:** parte de um
pedido na segunda às 10h (abertura do expediente) e anda o valor mostrado: a parte inteira escolhe o dia; a fração × 8 h,
contada de 10h com a pausa de 13h–14h, diz "de manhã" (até 13h) ou "à tarde" — "pedido na segunda às 10h, resposta na
terça à tarde" (1,8 = terça às 17h24). Acima de 4,9, sem exemplo. Dias corridos seguem só no leitor de tela.

**Slide 1 do estudo, "Para o cliente receber":** o exemplo do dia passa a usar a mesma medida (1 casa): "0,8 dia útil",
"2,0 dias úteis". O inteiro da C3b (`dias_uteis_entre`, campo `mediana_dias_uteis`) **fica só no código e nesta
ficha**, para rastreabilidade; nenhuma tela o mostra mais.

```sql
WITH m AS (SELECT projeto_id, passo, fase, entrada, exclusivo
           FROM `gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_2026_sla_movimentos`),
fer AS (SELECT d FROM UNNEST([DATE '2025-01-01','2025-01-20','2025-01-25','2025-03-03','2025-03-04','2025-03-05','2025-04-18',
  '2025-04-21','2025-04-23','2025-05-01','2025-06-19','2025-07-09','2025-09-07','2025-10-12','2025-11-02','2025-11-15',
  '2025-11-20','2025-12-24','2025-12-25','2025-12-31',
  DATE '2026-01-01','2026-01-20','2026-01-25','2026-02-16','2026-02-17','2026-02-18',
  '2026-04-03','2026-04-21','2026-04-23','2026-05-01','2026-06-04','2026-07-09','2026-09-07','2026-10-12',
  '2026-11-02','2026-11-15','2026-11-20','2026-12-24','2026-12-25','2026-12-31']) d),
ini AS (SELECT projeto_id, entrada t0, exclusivo FROM m WHERE passo = 1),
pronto AS (SELECT projeto_id, ARRAY_AGG(STRUCT(passo, entrada) ORDER BY passo LIMIT 1)[OFFSET(0)] p FROM m WHERE fase = 'cliente' GROUP BY 1),
base AS (SELECT i.*, pr.p.entrada t1, FORMAT_DATETIME('%Y-%m', pr.p.entrada) mes
         FROM ini i JOIN pronto pr USING (projeto_id) WHERE pr.p.passo > 1),
-- C3c: segundos do expediente (10h-13h e 14h-19h, seg-sex sem feriado) entre o pedido e a 1a entrega, / 8 h
jan AS (SELECT * FROM UNNEST([STRUCT(10 AS h0, 13 AS h1), STRUCT(14, 19)])),
fr AS (SELECT b.projeto_id, ANY_VALUE(b.exclusivo) exclusivo, ANY_VALUE(b.mes) mes,
         SUM(IF(d IS NULL OR f.d IS NOT NULL OR EXTRACT(DAYOFWEEK FROM d) NOT BETWEEN 2 AND 6, 0,
             GREATEST(DATETIME_DIFF(LEAST(b.t1, DATETIME(d, TIME(j.h1, 0, 0))), GREATEST(b.t0, DATETIME(d, TIME(j.h0, 0, 0))), MICROSECOND), 0)))
           / (8 * 3600e6) dias
       FROM base b
       LEFT JOIN UNNEST(GENERATE_DATE_ARRAY(DATE(b.t0), DATE(b.t1))) d
       LEFT JOIN fer f ON f.d = d
       CROSS JOIN jan j
       GROUP BY b.projeto_id),
v AS (SELECT g, dias FROM fr, UNNEST(['Todos', IF(exclusivo, 'Exclusivos', IF(NOT exclusivo, 'Nao exclusivos', NULL))]) g
      WHERE g IS NOT NULL AND mes BETWEEN '2026-01' AND '2026-09')
SELECT g, COUNT(*) n, ANY_VALUE(med) mediana, FLOOR(ANY_VALUE(med) * 10 + 0.5) / 10 tela,
  ROUND(AVG(dias), 3) media, ROUND(APPROX_QUANTILES(dias, 4)[OFFSET(1)], 3) q1, ROUND(APPROX_QUANTILES(dias, 4)[OFFSET(3)], 3) q3
FROM (SELECT g, dias, PERCENTILE_CONT(dias, 0.5) OVER (PARTITION BY g) med FROM v)
GROUP BY g ORDER BY g DESC
```

**Resultado (carga `_processado_em` 26/10/2026 12:01:34 UTC, meses completos jan–set; identidade
caio.barroso@viu.com.br, projeto gglobo-viu-dados-hdg-prd; 584 KB processados):**

| Grupo | n | Mediana exata (BigQuery) | `entrega()` (app) | Tela | Exemplo | C3b inteiro (antes) |
|---|---|---|---|---|---|---|
| Todos | 2.347 | 1,847741 | 1,847741 | **1,8 dia útil** | segunda 10h → terça à tarde | 2 |
| Exclusivos | 1.609 | 1,563523 | 1,563523 | **1,6 dia útil** | segunda 10h → terça à tarde | 1 |
| Não exclusivos | 725 | 2,499922 | 2,499922 | **2,5 dias úteis** | segunda 10h → quarta à tarde | 2 |

App = BigQuery nos três grupos (mesma mediana até a 6ª casa). Média e quartis do Todos no banco: média 3,30,
Q1 0,88, Q3 3,55 (cauda à direita, como as horas da equipe). Leitura: o típico do cliente fica **mais perto de 2 que de
1** (Todos 1,8); nos exclusivos, 1,6 — o inteiro antigo dizia "1 dia útil" porque contava viradas de dia, não horas; nos
não exclusivos, 2,5, a meio caminho entre 2 e 3.

### 000000000000.3 Testes e limites

- `tests/test_sla_d54.py`: 11 casos da fração (mesmo dia, virada, fim de semana, feriado, fora do expediente, almoço,
  antes das 10h, nunca negativo); coerência com `horas_uteis ÷ 8` e com a C3b (diferença < 1); texto e exemplo de
  `dias_uteis_cliente` (2,44 → "2,4 dias úteis", quarta à tarde; 2,3 → quarta de manhã; 1,6 → "1,6 dia útil"; 2,35 →
  2,4 meio para cima; 5,2 sem exemplo; `None`); herói com 1 casa; rótulo curto na chave do título e na linha, com a
  dica e o leitor de tela; CSS do rótulo numa linha, junto das regras do SLA (antes do bloco do estudo).
- Ajustados: `test_batalha2_textos.py` (rótulo lido da chave do título), `test_sla_20261025.py`, `test_sla_d38.py`,
  `test_rotas.py` (dados sintéticos: "1,8 dia útil", "resposta na terça à tarde"). **454 testes.**
- Limite: o exemplo supõe o pedido na abertura do expediente; um pedido de segunda às 15h com o mesmo 1,8 chegaria na
  quarta de manhã. A frase diz "às 10h" para não prometer mais do que a conta.

## 00000000000. Batalha 2, 1ª leva — dados, cálculos e textos (26/10/2026)

Nenhuma regra de negócio mudou (meta D38, D-SLA-1 a D-SLA-7 intactas). Mudaram textos, o formato do selo do mês e o
registro da C3b. Carga conferida: `_processado_em` = **26/10/2026 12:01:34 UTC** (mês parcial 2026-10, dados até 25/10).

### 00000000000.1 O que mudou na tela

| Item | Antes | Agora | Por quê |
|---|---|---|---|
| Rótulo da linha tracejada | "meta sugerida: 2 dias úteis" | "meta sugerida: metade em até 2 dias de trabalho (16 h)", em até 3 linhas sobre os meses sem barra (no celular, 2 linhas acima das barras) | a meta é de horas de trabalho (D38); "dias úteis" é o prazo de calendário do cliente (C3b). O texto anterior foi pedido pelo Caio (00.5); a troca segue a definição dele da meta em horas — **avisar o Caio** |
| Número de apoio | "2 dias úteis para o cliente receber" | "2 dias úteis **no calendário** para o cliente receber" | "dias de trabalho" fica reservado à meta e às horas da equipe |
| Legenda e leitor de tela | "mediana do mês", "mediana" | "típico do mês", "típico" | linguagem simples (sem jargão) |
| Linha sob a legenda | "12% passam de 5 dias de trabalho (289 orçamentos) — são os casos a tratar" | "44% passam de 2 dias de trabalho" (= "acima de 2 dias" da legenda) | número citado precisa estar no gráfico (o corte de 5 dias segue nos slides 4 e 8). Revisa a parte "indicador acima de 5 dias" da D38 só nesta página — **avisar o Caio** |
| Selo do mês | mediana inteira ("16 h" com 49%) | `_h_meta` (C6): uma casa entre 15,5 e 16,5 h — acima de 16, arredonda para cima; abaixo, para baixo ("16,4 h", "15,7 h", "15,9 h") | o arredondamento punha na meta meses fora dela; a mesma função do estudo |
| Slide 1, "Para o cliente receber" | dias corridos arredondados ("1 dia corrido") | C3b, dias úteis no calendário ("1 dia útil") | mesma unidade do número de apoio |
| Slide 1, nota do trabalho | "dentro da meta de 2 dias (16 h)" | "dentro do limite de 2 dias de trabalho (16 h)" | a meta é do mês (metade), não de um orçamento |
| Slide 2 (estudo) | "Formato da distribuição · Assimetria", "Assimetria positiva: cauda à direita", "Coeficiente de assimetria", "Teste de normalidade · gráfico Q-Q", "Os tempos formam um sino (curva normal)? Não.", "outliers (acima do limite estatístico, 59 h)", "bolinha em 0 h: 18% previstos abaixo de 0 h", "Faixas de tempo · boxplot", "O que é padrão do processo e o que é outlier?", "Outliers", "mediana", "na meta: até 2 dias", botões "Próxima: Normalidade / Faixas de tempo" | "Formato", "Poucos casos muito longos puxam a conta", "Tamanho da cauda", "Sino", "Se fosse um sino, onde cairiam?" + frase condicional, "fora da curva (acima de 59 h)", "Faixas", "Rápidos · comuns · demorados · fora da curva", "Fora da curva", "típico", "prontos em até 2 dias" (cai para "até 2 dias" se não couber), "Próxima: Sino / Faixas"; faixa do pé "… estão fora da curva, acima de 59 h" | G3-8: termos técnicos (assimetria, Q-Q, boxplot, 18% abaixo de 0 h) ficam no leitor de tela e na seção 8.1 |
| Recorte dos slides 2–8 | "2.347 pedidos entregues" | "2.347 orçamentos medidos" | glossário (README das fichas): pedido entra, orçamento é entregue |
| `/sla/regras` | "mês em que o pedido entrou", "dias corridos", "mediana" | "mês da primeira entrega ao cliente", "dias úteis no calendário", "o do meio" | D-SLA-1 e C3b; **2ª leva: página retirada (301 para o estudo)** |

### 00000000000.2 C3b — dias úteis até o cliente receber (regra, SQL e resultado)

**Regra (`app/expediente.py::dias_uteis_entre`, Caio 25/10/2026):** viradas de dia útil (seg–sex, sem feriado da
operação) entre o pedido (`entrada` do passo 1) e a 1ª entrega (`entrada` do 1º passo `cliente`). Pedido depois das
19h, em fim de semana ou feriado conta a partir do próximo dia útil. Pedido de segunda entregue na quarta = 2; no mesmo
dia útil = 0. Na tela: mediana dos meses completos do grupo, inteira (meio para cima, C8). Equivale a contar os dias
úteis do intervalo [dia do pedido (+1 se depois das 19h), dia da entrega).

```sql
WITH m AS (SELECT projeto_id, passo, status, fase, entrada, saida, exclusivo, nome_projeto
           FROM `gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_2026_sla_movimentos`),
fer AS (SELECT d FROM UNNEST([DATE '2025-01-01','2025-01-20','2025-01-25','2025-03-03','2025-03-04','2025-03-05','2025-04-18',
  '2025-04-21','2025-04-23','2025-05-01','2025-06-19','2025-07-09','2025-09-07','2025-10-12','2025-11-02','2025-11-15',
  '2025-11-20','2025-12-24','2025-12-25','2025-12-31',
  DATE '2026-01-01','2026-01-20','2026-01-25','2026-02-16','2026-02-17','2026-02-18',
  '2026-04-03','2026-04-21','2026-04-23','2026-05-01','2026-06-04','2026-07-09','2026-09-07','2026-10-12',
  '2026-11-02','2026-11-15','2026-11-20','2026-12-24','2026-12-25','2026-12-31']) d),
ini AS (SELECT projeto_id, entrada t0, exclusivo FROM m WHERE passo = 1),
pronto AS (SELECT projeto_id, ARRAY_AGG(STRUCT(passo, entrada) ORDER BY passo LIMIT 1)[OFFSET(0)] p FROM m WHERE fase = 'cliente' GROUP BY 1),
base AS (SELECT i.*, pr.p.entrada t1, FORMAT_DATETIME('%Y-%m', pr.p.entrada) mes
         FROM ini i JOIN pronto pr USING (projeto_id) WHERE pr.p.passo > 1),
-- C3b: dias úteis (seg–sex sem feriado) de [dia do pedido (+1 se depois das 19h), dia da entrega)
dut AS (SELECT b.projeto_id, ANY_VALUE(b.exclusivo) exclusivo, ANY_VALUE(b.mes) mes,
         COUNTIF(EXTRACT(DAYOFWEEK FROM d) BETWEEN 2 AND 6 AND f.d IS NULL) du
       FROM base b
       LEFT JOIN UNNEST(GENERATE_DATE_ARRAY(DATE_ADD(DATE(b.t0), INTERVAL IF(EXTRACT(HOUR FROM b.t0) >= 19, 1, 0) DAY),
                                            DATE_SUB(DATE(b.t1), INTERVAL 1 DAY))) d
       LEFT JOIN fer f ON f.d = d
       GROUP BY b.projeto_id),
v AS (SELECT g, du FROM dut, UNNEST(['Todos', IF(exclusivo, 'Exclusivos', IF(NOT exclusivo, 'Nao exclusivos', NULL))]) g
      WHERE g IS NOT NULL AND mes BETWEEN '2026-01' AND '2026-09')
SELECT g, COUNT(*) n, APPROX_QUANTILES(du, 2)[OFFSET(1)] mediana_aprox,
  ANY_VALUE(med) mediana, FLOOR(ANY_VALUE(med) + 0.5) dias_uteis_tela
FROM (SELECT g, du, PERCENTILE_CONT(du, 0.5) OVER (PARTITION BY g) med FROM v)
GROUP BY g ORDER BY g DESC
```

**Resultado (carga 26/10/2026 12:01:34 UTC, jan–set):** Todos n = 2.347, mediana 2 → **2 dias úteis**; Exclusivos
1.609, mediana 1 → **1 dia útil**; Não exclusivos 725, mediana 2 → **2 dias úteis**. App (`entrega()`) = BigQuery nos
três grupos. Selos dos meses (Todos): 13 · 15,7 · 15 · 16,4 · 16,4 · 16,5 · 13 · 13 · 14 h; faixas do ano 31/25/44 (56%
em até 2 dias). `tools/conferir_estudo.py` na mesma carga: **tudo bate** (n e típico dos 3 grupos: 14,252 / 11,826 /
19,642 h).

### 00000000000.3 Testes e limites

- `tests/test_batalha2_textos.py`: rótulo da meta sem "dias úteis"; nenhum "mediana" no texto visível da página;
  "no calendário para o cliente receber"; nenhum "5 dias" na página; complemento = "acima de 2 dias" da legenda; mês
  sintético de 16,4 h aparece "16,4 h" (não "16 h") com < 50%; `_h_meta` nas bordas; `/regras` pela 1ª entrega.
- `node tools/conferir_layout.mjs`: só as 3 falhas já conhecidas do histograma do slide 2 no celular (texto < 11 px,
  ficha 0.7); nenhuma rolagem lateral nem corte nos tamanhos de mesa.
- Fica para o Caio: a frase "Meta batida em N de 9 meses" (veredito da meta) não foi aplicada (decisão aberta do slide 8).

## 0000000000. D46 — movimento do estudo "Como medimos" (25/10/2026, noite)

Pedido do Caio: o estudo estava "muito estático". Três linhas de movimento (narrativa de dados, discreto e executivo, movimento que responde à pessoa) debateram; um quarto agente decidiu e aplicou. **Nenhum número, texto ou regra de cálculo mudou**: só a forma como as marcas entram.

**Síntese vencedora (consenso do debate):** um gesto de dado por slide, na ordem de leitura (régua → dado → cor de alerta); títulos, textos e números visíveis desde o 1º quadro (nada conta até o valor); uma curva só (`--ease-entra`), sem mola, sem loop, nada pulsa; cada slide termina em até ~1,15 s; a entrada roda só na 1ª visita do slide; a troca de grupo de talentos não repete a cena; a moldura fica parada na troca de slide.

### 0000000000.1 Movimento do estudo, slide a slide

| Slide | O que se move (o resto fica parado) | Tempo |
|---|---|---|
| Todos | Traço azul do título cresce (assinatura comum) | 0–0,5 s |
| Troca de slide | Conteúdo desliza 1,5% no sentido da navegação (View Transition no mesmo documento); cabeçalho, controles, menu e rodapé parados | 0,16 s sai · 0,22 s entra |
| 1 · Exemplo | Linha do tempo se desenha trecho a trecho; marco acende quando o traço chega (sem ressalto); nome, tempo e data acompanham o trecho. Números da faixa, regras, nota e gancho estáticos (antes entravam em cascata até 2,6 s) | 0,1–1,15 s |
| 2 · Histograma | Barras sobem juntas do eixo (um `<g>`); contagens no fim; mediana e média descem até o eixo; a média nasce sobre a mediana e desliza até o seu lugar ("puxada pela cauda"). Troca de passo em 0,3 s, voltar entra pela esquerda; de volta ao passo 1 a média desliza de novo. Q-Q e boxplot estáticos | ≤ 1,15 s; passo 0,3 s |
| 3 · De cada 100 | Waffle enche linha a linha (máscara única em 10 degraus); curva acumulada se desenha junto; área logo atrás. Marcos e chaves estáticos | 0,08–0,95 s |
| 4 · Para onde vai o tempo | Em cada cartão, barra dos pedidos e logo depois a das horas; cartão B 100 ms depois. Trilho e % estáticos | 0,08–0,98 s |
| 5 · Mês a mês | Nuvem em 3 camadas por opacidade (rápidas → lentas; 4 elementos, nada por ponto); linha do típico se desenha jan→set; bolinhas do típico no fim. Valores e tabela estáticos | 0,06–1,15 s |
| 6 · Onde trava | Barrinhas crescem juntas; a do destaque termina passando do neutro ao vermelho | 0,08–0,95 s |
| 7 · Por tipo | Linha tracejada do geral primeiro; barras se revelam da esquerda em onda de 25 ms por linha; vermelho dos tipos bem acima do geral por último, sóbrio | 0–1,05 s |
| 8 · Conclusão | Círculos numerados e fios acendem de 1 a 6. Títulos, valores, frases, "Onde olhar" e "O que isso pede" estáticos | 0,08–0,88 s |
| Troca de grupo | Página nova abre o slide pronto (sem repetir a entrada), com o crossfade de 240 ms que já existia; foco volta ao grupo se a troca veio do teclado | 0,24 s |
| Gancho | Seta avança 2 px no hover e no foco do teclado | 0,18 s |

### 0000000000.2 Como funciona e garantias

- **Código:** bloco D46 no fim de `app/static/estilo.css` (CRLF), `app/static/apresentacao.js` (`entrar` com `.revisto`, `mostrar`/`exibir` com `startViewTransition`, `ir` com `data-ida` e a média, aviso `estudo-sem-entrada` no `sessionStorage`, `--k` das linhas do slide 7) e `app/templates/como_medimos.html` (só `<g class="ex-barras">`, `<g class="ex-ns">`, `<g class="ex-media-g">` e `pathLength="1"` em `.cc-linha` e `.mx-tipico`).
- **Movimento reduzido, sem JS, impressão e captura:** estados de partida só sob `@media (prefers-reduced-motion: no-preference)` + `html.js` + `:not(.entrou)`; keyframes com fill `backwards`; `@media print` zera tudo. Capturas com `--force-prefers-reduced-motion` antes e depois: **idênticas** nos 8 slides em 1920×1000 e 1280×800. Sem a flag, depois de 2,5 s, o estado final é o mesmo (só muda o anti-serrilhado de textos).
- **CSP:** nenhum `style=""` nem `<style>`/`<script>` inline; atrasos por `nth-child` ou `style.setProperty` (CSSOM), como o site já fazia; a média de volta ao passo 1 usa WAAPI.
- **Desempenho:** só transform, opacity, clip-path e stroke-dashoffset; nada por ponto na dispersão (os ~2.350 pontos são 3 `<path>`); waffle e histograma animados como 1 elemento.
- **Só no estudo:** a entrada única (`.revisto`) e a View Transition entre slides valem só para `.slide-estudo`; Início, Talentos e Atendimento não mudam.
- **Testes:** `tests/test_sla_movimento.py` (7 testes); suíte com 271. `tools/conferir_layout.mjs`: 93 combinações OK; as 3 falhas são o histograma do slide 2 a 390 px (textos de ~7 px), anteriores à D46 e pendentes de decisão do Caio.

### 0000000000.3 Fora do escopo até 28/10 (fase 2, se o Caio quiser)

Barras indo do valor antigo para o novo na troca de grupo (slides 4, 6 e 7), realce por hover/foco nas tabelas dos slides 4 e 7, Q-Q e boxplot animados, holofote do slide 5, pré-busca (`prefetch`) dos links de grupo em `ESPECULACAO` (`app/main.py`, mexe no backend). Conferir no notebook do projetor (DevTools, CPU 4× mais lenta) o slide 5; se a troca de slide travar no celular real, desligá-la abaixo de 900 px.

## 000000000. D45 — revisão em batalha de agentes (25/10/2026, noite)

Dois grupos de especialistas (dados, engenharia de dados, arquitetura, web, UX e ambiente do usuário) revisaram o estudo
"Como medimos" (slides 1–8); um painel de avaliadores aprovou 9 melhorias, aplicadas aqui na ordem da nota. **Nenhuma
regra de negócio mudou** (meta, recorte, horas, Tukey, cores e limites seguem os de D38–D44). Testes: **264** (8 novos em
`tests/test_sla_batalha.py`). Conferido no BigQuery em 25/10/2026 com `tools/conferir_estudo.py` (carga 23/10/2026
20:23:42 UTC, mês parcial 2026-10): **tudo bate** nos três grupos (Todos 2.348 · 14,261 h; Exclusivos 1.610 · 11,830 h;
Não exclusivos 725 · 19,642 h).

### 000000000.1 O que mudou

| Item | Mudança | Onde |
|---|---|---|
| B-N8 base congelada | `CONGELAR` (padrão: ligado com `MODO=apresentacao`, nunca em produção): a base lida na subida não se recarrega (`Tabela._vencido` = falso) e o rodapé diz "· base congelada para a apresentação". Nenhuma carga troca "dois pontos" por "um ponto" ao vivo | `config.py`, `dados.py`, `main.py`, `apresentacao.html` |
| B-N8 exemplo fixo (E4) | `?exemplo=<projeto_id>` fixa o orçamento do slide 1 num caso revisado pelo Caio. Só com `DEV` ou `MODO=apresentacao` e nunca em produção; vale só se o projeto é candidato pelas regras E1 (ano, até o mês vigente, 2 a 16 h, caminho limpo, grupo); senão, segue o sorteio do dia | `calculos.exemplo(…, fixo=)`, `_exemplo_de`; `montar_estudo_sla` |
| B-N8/A-N12 conferência | `tools/conferir_estudo.py` (somente leitura): confirma identidade e projeto, só SELECT com teto de bytes; refaz no banco as horas por orçamento e status com os feriados de `app.expediente` e o mês parcial do `MAX(_processado_em)`; agrega sem as funções do site e compara n, típico, A, HB, B e pedidos por mês, travaram e % travado por status, tempo travado ÷ horas, pedidos e B por tipo e acima de 5 dias, nos 3 grupos. Guarda as leituras (faixas e achados) e, com `--anterior`, avisa a que mudou | `tools/conferir_estudo.py` |
| A-N12 típico perto da meta | Z1, o seletor de talentos dos slides 2–8, o slide 2 (mediana do histograma, alfinete, boxplot, espelho) e o típico do slide 7 passam a usar `_h_meta` (C6): 16,3 h aparece "16,3 h" (em vermelho no slide 8), nunca "16 h" em vermelho. Igual a `_h` fora de 16 < m < 16,5 (nada muda na carga atual) | `calculos.py` |
| A-N12/B-N11 layout | `tools/conferir_layout.mjs` (somente leitura, Chrome headless com emulação): #1–#8 × 3 grupos × 1920×1000, 1440×900, 1280×800 e 390×844; falha se rolar para o lado, se algo passar do pé da lâmina (mesa) ou se texto de gráfico (SVG) ficar abaixo de 11 px; texto HTML abaixo de 11 px sai como aviso | `tools/conferir_layout.mjs` |
| A-web-1 slide 3 no celular | O `@container` estreito era anulado pelas regras sem condição escritas depois; um bloco no fim do CSS volta a empilhar waffle e curva (rótulos da curva legíveis em 390 px) | `estilo.css` (bloco "Batalha de agentes") |
| A-N5 % de quê | Slide 4: "%" junto de cada número grande e "56% dos pedidos / 5% das horas" nas linhas. Slide 6: o cartão diz "N travaram · acima de X h" (o limite do normal do status) em vez de "típico X h" (o típico de todos que passaram, que contradizia o "travaram"); o leitor de tela diz o limite e o típico. Slide 7: cabeçalho "Onde passa mais tempo" com a base "% do tempo de quem passa de 2 dias", e o % visível também para o leitor | `calculos.py` (K5), `como_medimos.html` |
| B-N3 base comum | `travas()` devolve `pct_horas` = tempo travado ÷ todas as horas da equipe do recorte. Achado 5: "do tempo travado (X% de todas as horas) fica em…"; o aria-label do slide 6 também. J5/J7 deixam o verbo "travar" (outra medida que a do slide 6): "Onde passa mais tempo", "— e passa mais tempo na {etapa}" | `calculos.py` (K, J5, J7, Z5) |
| B-N6 escape | Nomes de status e de Tipo de Input (vêm do Monday) são escapados (`markupsafe.escape`) antes de entrar no HTML das faixas que passam por `| safe` (K7, J7) | `calculos.py` |
| B-ambiente-2 recorte | R1 `recorte()`: no topo dos slides 2–8, à direita do título, "jan a set de 2026 · 2.348 pedidos entregues · Todos" (meses completos C7, N = `len(_universo_df)`, grupo do seletor); no slide 8, "· outubro entra quando fechar". Slide 1: o gancho diz o grupo ("o orçamento típico dos exclusivos leva 12 h") | `calculos.recorte`, `como_medimos.html`, `estilo.css` |
| B-N11 texto calculado | Cartões do slide 6 com `min-height` (crescem em vez de cortar nome de 2 linhas + "só até"); linha de números quebra; número grande do slide 8 pode quebrar | `estilo.css` |
| B-N7 (parte segura) | Slides 2–8 guardados por carga, objeto e grupo (até 3 cargas × 3 grupos, com trava) e aquecidos em `dados.sla.ao_carregar` para os 3 grupos; `_cache.pop(velha, None)`. Requisição do estudo na 8096: 0,12–0,13 s (antes 0,3–0,5 s; a 1ª depois do `--reload` segue lenta) | `apresentacao.py`, `calculos.entregas` |

### 000000000.2 Memória de cálculo nova (carga 23/10/2026 20:23:42 UTC, jan–set) — app = BigQuery

| Grupo | N (recorte) | tempo travado ÷ todas as horas (achado 5) | leitura do slide 6 |
|---|---|---|---|
| Todos | 2.348 | 54% (32.558,16 h travadas) | dois pontos, 60% |
| Exclusivos | 1.610 | 59% (22.161,72 h) | dois pontos, 65% |
| Não exclusivos | 725 | 39% (8.412,47 h) | dois pontos, 54% |

SQL: a de `tools/conferir_estudo.py` (`SQL_HORAS`, CTEs `m`, `parcial`, `ini`, `pronto`, `base`, `eq`, `us`, `st` com
`@feriados` vindo de `app.expediente.sem_expediente`); o % = soma das horas de quem travou (Tukey por status, 000000.5)
÷ soma das horas da equipe do grupo. Resultado guardado em JSON (scratchpad da sessão, `batalha/estudo_2026-10-25.json`).

### 000000000.3 Como usar na reunião (Caio executa)

1. Véspera (26/10) e manhã de 28/10: `python tools/conferir_estudo.py --output docs/validacao/estudo_2026-10-26.json`
   (e, no dia 28, `--anterior` apontando para o de 26/10). Saída 0 = tudo bate; qualquer "LEITURA MUDOU" = rever o
   slide antes de apresentar.
2. `node tools/conferir_layout.mjs` com o servidor de pé: precisa terminar sem FALHA.
3. Subir para a reunião **sem `--reload`** e com `MODO=apresentacao` (base congelada), depois de encerrar outros uvicorn
   (comando no README). Para o slide 1, escolher com o Caio um orçamento sem dado sensível e abrir com `?exemplo=<id>`.

### 000000000.4 O que não foi aplicado e por quê

- **Linha visível com a definição de "travou" no slide 6 (parte da A-N5):** o Caio retirou essa linha da tela em 25/10
  (seção 000000.1; teste `trava-intro`). Fica no aria-label, agora com a base em horas. Recolocar é decisão dele.
- **Definição curta no achado 5 (A-N5):** só a base "(X% de todas as horas)" entrou, para caber na coluna do slide 8.
- **B-N7, parte de refatoração** (tirar KDE/X7–X9 do caminho, fundir os caches de `entregas`, locks nos dicionários de
  `calculos`): adiada para depois de 28/10, como pediram os avaliadores.
- **Texto de gráfico abaixo de 11 px no slide 2 em 390 px** (histograma encolhe para ~6,7 px) e rótulos HTML abaixo de
  11 px em 1440/1280 (sobretítulo, "TALENTOS", passos do slide 3): achados pelo `conferir_layout.mjs`, anteriores a esta
  revisão e fora dos itens aprovados; ficam para o Caio decidir.

## 00000000. D44 — slide 8 do estudo: "O que os dados nos mostraram" (conclusão, 25/10/2026)

Construído pela imagem de referência do Caio. URL: `/viu-agenciamento/sla/como-medimos#8` (`?talentos=` como nos slides
2–7). Código: `conclusao()` / `_conclusao()` / `_pergunta()` e regras **Z1–Z8** no fim de `sla/calculos.py` (recebe os
dicts já calculados dos slides 4–7 em `montar_estudo_sla`, chave `conclusao`; `_mes_textos` passou a devolver `resumo`
com os números da faixa do slide 5); `templates/como_medimos.html` (slide 8; o gancho do slide 7 virou link para `#8`);
`static/estilo.css` (bloco "slide 8"); testes `tests/test_sla_conclusao.py` (7). O estudo tem 8 slides ("8 de 8").

### 00000000.1 Pergunta e textos da tela

- Rótulo "Exploração dos dados · conclusão"; título "O que os dados nos mostraram"; seletor de talentos (links `#8`).
- Linha do tempo com 6 achados (círculo numerado + fio; título; número grande em serifa; frase curta). Marinho = achado
  bom, vermelho suave = problema (por regra). Texto "(ponto de atenção)" para leitor de tela nos vermelhos.
- "Onde olhar com mais detalhe" (título em serifa) com 3 itens de filete amarelo: os 2 status de maior tempo travado do
  slide 6 com uma pergunta de investigação e "Pedidos acima de 5 dias".
- Faixa "O que isso pede": "Agir nos poucos pedidos que travam, **no momento em que travam**. Para isso, o Monday precisa
  mostrar em que etapa cada pedido está e há quanto tempo. *E isso depende de como usamos o Monday.*" (texto fixo do Caio).
- Sem gancho: "Voltar ao início do estudo ↺" (link para `#1`); a navegação do pé fica em "8 de 8".

### 00000000.2 Regras (Z1–Z8, `sla/calculos.py`)

| Código | Regra |
|---|---|
| Z1 | "O tempo típico": mediana e média das horas da equipe (`_h`, os números do seletor/slide 2): "de trabalho. A média, {média}, é puxada por poucos casos longos." (média arredondada ≤ típico: "fica perto."). Azul se a mediana exata ≤ 16 h (C6); senão vermelho. Sem a palavra "mediana" |
| Z2 | A = % em até 2 dias de `tempo_cem` (= slide 3). Título: A > 50 "A maioria é rápida"; = 50 "Metade é rápida"; < 50 "Menos da metade é rápida". Azul se A ≥ 50 (meta sugerida) |
| Z3 | "Os demorados pesam": HB% "do tempo com a equipe vai para os {B}% que levam mais de 2 dias." (slide 4). B = 0: "Ninguém passa de 2 dias" (azul) |
| Z4 | Leitura U7 do slide 5: padrão → "Não é crise, é padrão" · "todo mês" · "de Bmin% a Bmax% passam de 2 dias{, mesmo com o volume crescendo}." (crescendo = pedidos dos 3 últimos meses completos ≥ 1,25 × os dos 3 primeiros, com ≥ 6 meses); picos → "No geral, é padrão" · "quase todo mês"; sazonal → "Há meses mais pesados" · meses curtos ("abr, mai e ago") · "De d0% a d1% passam de 2 dias, contra … no resto do ano."; raro → "O prazo se mantém" (azul) |
| Z5 | Leitura K7 do slide 6 (tempo travado novo, K4): dois → "Trava em dois pontos" · p1+p2 · "do tempo travado fica em dois status: S1 e S2."; um → "Trava em um ponto"; espalhado → "Trava espalhado". "(só até <mês>)" quando K6 |
| Z6 | Leitura J7 do slide 7: destaque → "Pesa mais no {tipo}" · B% · "dos pedidos {tipo} passam de 2 dias; é onde a {etapa} mais pesa."; sem destaque → "Os tipos se parecem" · "Bmin–Bmax%" · "nos tipos de maior volume passam de 2 dias, perto dos G% do geral.{ Exceção: {tipos em vermelho}.}" (um tipo de maior volume: "O {tipo} segue o geral"); vermelho se há tipo em vermelho. Sem tipos com linha: o achado não aparece |
| Z7 | Onde olhar: os 2 status de maior tempo travado (só os que travaram), pergunta por tipo de status — Fila de entrada: "Por que o pedido espera antes de começar{, principalmente no {tipo}}?" (tipo do slide 7 quando a fila é onde ele mais trava); Elaboração: cotação → "O que atrasa a cotação? Quem responde e em quanto tempo?", produção → "O que segura a produção? Falta de informação, aprovações, fila de outra área?", validação → "O que faz a validação demorar? …", demais → "O que segura o orçamento? Falta de informação do pedido, cotações, vai e volta?"; Revisão: validação → "O que faz a validação demorar? Quem valida e quando o pedido chega até ele?", demais → "O que faz a revisão demorar? …"; + "Pedidos acima de 5 dias": "São p% (n pedidos). Abrir caso a caso e achar o que eles têm em comum." (C12, > 40 h; em %, não "de cada 100") |
| Z8 | "O que isso pede": texto fixo; fim do estudo, link para o slide 1 |

### 00000000.3 Memória de cálculo (carga 23/10/2026 20:23:42 UTC, meses completos jan–set) — app = BigQuery

Cada número vem do slide de origem (conferidos no BigQuery nas seções 000–0000000 e 000000):

| # | Todos (2.348) | Exclusivos (1.610) | Não exclusivos (725) |
|---|---|---|---|
| 1 | O tempo típico · **14 h** · média 25 h (azul) | 12 h · média 23 h (azul) | 20 h · média 30 h (vermelho) |
| 2 | A maioria é rápida · **56%** (azul) | 62% (azul) | Menos da metade é rápida · 41% (vermelho) |
| 3 | Os demorados pesam · **84%** para os 44% | 81% para os 38% | 88% para os 59% |
| 4 | Não é crise, é padrão · todo mês · de 40% a 51%, mesmo com o volume crescendo (jan–mar 378 × jul–set 1.266 pedidos) | padrão · de 29% a 47%, volume crescendo | Há meses mais pesados · abr, mai e ago · De 70% a 75%, contra 43% a 60% |
| 5 | Trava em dois pontos · **60%** · Em elaboração (só até jul) e Fila de entrada | 65% | 54% |
| 6 | Os tipos se parecem · 43–45% · perto dos 44%; Exceção: Proativo e Interna (vermelho) | Pesa mais no Inbound · 43% · fila de entrada | O Mercado segue o geral · 59% · perto dos 59%; Exceção: Interna e Proativo |
| Onde olhar | Em elaboração (só até jul) — orçamento; Fila de entrada — "Por que o pedido espera antes de começar?"; acima de 5 dias: 12% (289 pedidos) | idem, fila "principalmente no Inbound?"; 10% (163) | idem; 16% (116) |

### 00000000.4 Validação e limites

- Testes `tests/test_sla_conclusao.py` (7): números iguais às funções de origem (mediana/média, A = slide 3, HB/B do
  slide 4, % do slide 6, tipo e etapa do slide 7, acima de 5 dias); variantes Z1–Z6 (títulos, cores, "volume crescendo"
  e < 6 meses, raro/picos/sazonal, um/dois/espalhado, parecido/um tipo/destaque/sem tipos); perguntas da Z7; HTML (8
  slides, seletor `#8`, gancho do slide 7 → `#8`, link `#1`, sem `style=""`). Suíte: **256 testes**.
- Capturas (scratchpad `s7/c3_{todos,exclusivos,nao-exclusivos}_{1920,1440,1280}.png`, `c3_390.png`): cabe sem rolar nos
  três tamanhos; 390 px sem rolagem lateral (achados em 1 coluna).
- O achado 5 e o "onde olhar" herdam a ressalva do slide 6: o "Em elaboração" geral (só até jul) domina por causa dos
  pacotes; se o Caio mudar o recorte do slide 6, a conclusão muda junto.

## 0000000. D43 — slide 7 do estudo: "Em que tipo de pedido o tempo trava?" (25/10/2026)

Construído pela imagem de referência do Caio e ajustado no mesmo dia ("informação demais": sem nota embaixo, análise só
na faixa, letras menores, barras finas, cores com significado). URL: `/viu-agenciamento/sla/como-medimos#7` (`?talentos=`
como nos slides 2–6). Código: `tipos_pedido()` / `_tipos()` / `_onde_trava()` / `_tipo_nome()` e regras **J1–J9** no fim
de `sla/calculos.py`; `entregas()` ganhou a coluna `tipo_input`; `montar_estudo_sla` (chave `tipos`);
`templates/como_medimos.html` (slide 7; gancho do slide 6 → `#7`); `static/estilo.css` (bloco "slide 7"); testes
`tests/test_sla_tipo.py` (7).

### 0000000.1 Origem da coluna Tipo de Input

`tipo_de_input` da própria gold de movimentos (`gld_agenciamento_2026_sla_movimentos`, `TAB_SLA`), que o app já lia
(`COLUNAS_SLA`). É atributo do projeto, igual em todos os passos (carga 23/10: 0 projetos com mais de um valor); o app lê
no passo 1. Valores no universo (2.348): Mercado 1.266 · Inbound 637 · ViU 167 · Proativo 128 · Interna 74 · Globo 57 ·
ViU First 9 · OTR (Oportunidade em Tempo Real) 5 · nulo 5. (`grupo_input` das gold de entrada/fluxo junta ViU, Interna,
Globo, ViU First e OTR em "Internos"; o slide usa o `tipo_de_input`, como a referência.)

### 0000000.2 Pergunta e textos da tela

- Rótulo "Exploração dos dados · e por tipo de pedido?"; título "Em que tipo de pedido o tempo trava?"; seletor de
  talentos (links `#7`). O seletor faz sentido: a mistura de tipos muda muito entre exclusivos (Mercado 43%, Inbound 37%)
  e não exclusivos (Mercado 79%); nenhum grupo fica vazio (não exclusivos: 1 tipo de maior volume e 3 de menor).
- Tabela-gráfico: "Tipo de input" (nome + "N pedidos · X%", o peso do tipo), legenda "Saem em até 2 dias / Passam de 2
  dias / Passam de 2 dias, bem acima do geral / ┆ Geral: A% em até 2 dias", barra 100% fina com os % dentro (quando ≥ 7),
  linha tracejada contínua no geral, "Tempo típico" (serifa) e "Onde mais trava" (etapa + "p%"; o detalhe "do tempo dos
  que passam de 2 dias" vai para o leitor de tela). "Todos os pedidos" com a barra escura; grupos "Maior volume · x% dos
  pedidos" e "Menor volume · y% dos pedidos".
- Sem nota embaixo (ajuste do Caio): recorte, tipos de menor volume em vermelho e "Outros" vão no `caption` da tabela
  (leitor de tela) e nesta ficha.
- Faixa do pé (J7) e gancho "E o que os dados nos mostraram? →" (link para `#8`).
- Acessibilidade: `<table>` com `caption`, `th scope`; cada barra com o texto "A% saem em até 2 dias e B% passam de 2
  dias{, bem acima do geral}." (o vermelho é dito em texto); SVG `aria-hidden`; sem `style=""`. Em tela estreita, cada
  tipo vira um bloco (nome e típico, barra, onde mais trava).

### 0000000.3 Regras (J1–J9, `sla/calculos.py`)

| Código | Regra |
|---|---|
| J1 | Base = universo dos slides 2–6 (meses completos de 1ª entrega; grupo de talentos; `h_trabalho` sem almoço e sem Retorno Marca). Tipo = `tipo_de_input` do passo 1; nulo/vazio = "vazio". n < 30 → mensagem de poucos dados |
| J2 | Linha própria só para tipo com ≥ 30 pedidos no recorte (TIPO_MIN); os outros e o vazio vão para "Outros" (fora da tela). Nome sem o parêntese ("OTR") |
| J3 | Maior volume = tipo com linha e ≥ 10% dos pedidos (VOLUME_MAIOR); menor volume = os demais com linha. % do tipo com 1 casa; % dos grupos (maior, menor, Outros) pelo maior resto somando 100 |
| J4 | A = % em até 2 dias (h ≤ 16 h) pela C8 (`_faixas`, o mesmo A dos slides 3/4); B = 100 − A; típico = `_h(mediana)` |
| J5 | Onde mais trava: entre os pedidos do tipo com h > 16 h, horas por etapa (status → etapa da K2: Fila de entrada, Elaboração, Revisão); a maior e p = horas dela ÷ horas desses pedidos (inteiro). Sem pedido acima de 2 dias: "—". Na linha "Todos" não aparece |
| J6 | Cores, iguais em todas as linhas (ajuste do Caio): azul = até 2 dias; amarelo = passam de 2 dias; **vermelho** = passam de 2 dias só no tipo com B ≥ B geral + 3 pontos (DESTOA_TIPO) e ≥ 30 pedidos; "Todos" escuro. Sem fundo rosado |
| J7 | Faixa do pé (1 linha): entre os de maior volume, o de maior B; em vermelho → "**O {tipo} é o que mais demora**: B% passam de 2 dias, contra G% no geral — e trava mais na {etapa}."; senão → "**Os tipos de maior volume ficam perto do geral**: de Bmin% a Bmax% passam de 2 dias, contra G%." (um tipo: "**O {tipo} fica perto do geral**") + " Só **{tipos de menor volume em vermelho}**, de menor volume, passa(m) bem mais." |
| J8 | Fora da tela (`caption`): "O tipo {X} chega a B% acima de 2 dias, com n pedidos." (menor volume em vermelho) e "Outros ({lista}): n pedidos (x%), poucos para comparar; sem linha própria." |
| J9 | Gancho: "E o que os dados nos mostraram?" → `#8` |

### 0000000.4 Memória de cálculo (carga 23/10/2026 20:23:42 UTC, meses completos jan–set) — app = BigQuery

Por tipo: n · % do recorte · A/B · típico (mediana exata) · lentos (> 16 h) · onde mais trava (p exato). ★ = vermelho.

**Todos (2.348; geral 56/44, 14 h — igual aos slides 3/4; lentos 1.044, Elaboração 54,69%)**

| Grupo | Tipo | n | % | A / B | típico | lentos | onde mais trava |
|---|---|---|---|---|---|---|---|
| Maior volume · 81% | Mercado | 1.266 | 53,9% | 55 / 45 | 14,540 → 15 h | 575 | Elaboração 43 (42,53) |
| | Inbound | 637 | 27,1% | 57 / 43 | 13,685 → 14 h | 273 | Fila de entrada 42 (41,62) |
| Menor volume · 18% | ViU | 167 | 7,1% | 79 / 21 | 8,098 → 8 h | 35 | Revisão 45 (44,99) |
| | Proativo ★ | 128 | 5,5% | 33 / 67 | 24,858 → 25 h | 86 | Elaboração 91 (90,96) |
| | Interna ★ | 74 | 3,2% | 32 / 68 | 22,365 → 22 h | 50 | Revisão 46 (45,76) |
| | Globo | 57 | 2,4% | 74 / 26 | 6,085 → 6 h | 15 | Revisão 42 (41,66) |
| Outros (fora) | ViU First 9, OTR 5, vazio 5 | 19 | 0,8% | — | — | — | — |

Faixa: "**Os tipos de maior volume ficam perto do geral**: de 43% a 45% passam de 2 dias, contra 44%. Só **Proativo e
Interna**, de menor volume, passam bem mais."

**Exclusivos (1.610; geral 62/38, 12 h):** maior volume 90% — Mercado 686 (42,6%) 66/34, 11 h, Fila de entrada 34
(34,15); **Inbound ★** 594 (36,9%) 57/43, 14 h, Fila de entrada 42 (42,48); ViU 164 (10,2%) 80/20, 8 h, Revisão 46. Menor
volume 9% — **Proativo ★** 88 (5,5%) 33/67, 25 h, Elaboração 90; Globo 56 (3,5%) 73/27, 6 h, Revisão 42. Outros: ViU
First 7, Interna 6, OTR 5, vazio 4 = 22 (1,4%). Faixa: "**O Inbound é o que mais demora**: 43% passam de 2 dias, contra
38% no geral — e trava mais na fila de entrada."

**Não exclusivos (725; geral 41/59, 20 h):** maior volume 79% — Mercado 573 (79,0%) 41/59, 20 h, Elaboração 48. Menor
volume 20% — **Interna ★** 67 (9,2%) 28/72, 22 h, Revisão 48; Inbound 43 (5,9%) 60/40, 11 h, Revisão 41; **Proativo ★** 36
(5,0%) 36/64, 21 h, Elaboração 94. Outros: ViU 3, Globo 1, ViU First 1, vazio 1 = 6 (0,8%). Faixa: "**O Mercado fica
perto do geral**: 59% passam de 2 dias, contra 59%. Só **Interna e Proativo**, de menor volume, passam bem mais."

### 0000000.5 SQL para reproduzir (BigQuery, só SELECT)

Mesmos `m` (com `tipo_de_input`), `fer` da 0.6.1; `ini` = `projeto_id, exclusivo, tipo_de_input` do passo 1; `pronto`;
`base` filtrada nos meses de 1ª entrega jan–set; `eq`, `us`, `st` como a 000000.5; e no fim:

```sql
et AS (SELECT *, CASE WHEN LOWER(TRIM(status)) = 'entrada' THEN 'Fila de entrada'
                      WHEN STARTS_WITH(LOWER(status), 'em elabora') THEN 'Elaboração'
                      WHEN STARTS_WITH(LOWER(status), 'em revis') THEN 'Revisão' ELSE 'Outros status' END etapa FROM st),
proj AS (SELECT b.projeto_id, b.exclusivo,
           IFNULL(NULLIF(TRIM(REGEXP_REPLACE(b.tipo_de_input, r'\s*\(.*$', '')), ''), 'vazio') tipo,      -- J1, J2
           IFNULL((SELECT SUM(h) FROM st WHERE st.projeto_id = b.projeto_id), 0) h FROM base b),
v AS (SELECT g, p.* FROM proj p, UNNEST(['Todos', IF(exclusivo, 'Exclusivos', IF(NOT exclusivo, 'Nao exclusivos', NULL))]) g WHERE g IS NOT NULL),
t AS (SELECT g, tipo, COUNT(*) n, COUNTIF(h <= 16) ate2, COUNTIF(h > 16) lentos FROM v GROUP BY 1, 2
      UNION ALL SELECT g, '(TODOS)', COUNT(*), COUNTIF(h <= 16), COUNTIF(h > 16) FROM v GROUP BY 1),
med AS (SELECT DISTINCT g, tipo, PERCENTILE_CONT(h, 0.5) OVER (PARTITION BY g, tipo) med FROM v
        UNION ALL SELECT DISTINCT g, '(TODOS)', PERCENTILE_CONT(h, 0.5) OVER (PARTITION BY g) FROM v),
lh AS (SELECT v.g, v.tipo, e.etapa, SUM(e.h) h FROM v JOIN et e USING (projeto_id) WHERE v.h > 16 GROUP BY 1, 2, 3   -- J5
       UNION ALL SELECT v.g, '(TODOS)', e.etapa, SUM(e.h) FROM v JOIN et e USING (projeto_id) WHERE v.h > 16 GROUP BY 1, 3),
top AS (SELECT g, tipo, ARRAY_AGG(STRUCT(etapa, h) ORDER BY h DESC LIMIT 1)[OFFSET(0)] e, SUM(h) tot FROM lh GROUP BY 1, 2)
SELECT t.g, t.tipo, t.n, t.ate2, ROUND(100 * t.ate2 / t.n, 2) p_ate2, t.lentos, ROUND(med.med, 3) mediana,
       top.e.etapa onde, ROUND(100 * top.e.h / top.tot, 2) p_onde
FROM t JOIN med USING (g, tipo) LEFT JOIN top USING (g, tipo) ORDER BY g DESC, t.n DESC;
-- 25/10/2026 (carga 23/10 20:23:42 UTC), Todos: (TODOS) 2348 | 1304 | 55,54 | 1044 | 14,261 | Elaboração | 54,69
--   Mercado 1266 | 691 | 54,58 | 575 | 14,54 | Elaboração | 42,53 · Inbound 637 | 364 | 57,14 | 273 | 13,685 | Fila de entrada | 41,62
--   ViU 167 | 132 | 79,04 | 35 | 8,098 | Revisão | 44,99 · Proativo 128 | 42 | 32,81 | 86 | 24,858 | Elaboração | 90,96
--   Interna 74 | 24 | 32,43 | 50 | 22,365 | Revisão | 45,76 · Globo 57 | 42 | 73,68 | 15 | 6,085 | Revisão | 41,66
--   ViU First 9 · vazio 5 · OTR 5 (Outros). Exclusivos e Não exclusivos: iguais a 0000000.4.
```

Passo a passo: (1) rodar a SQL; (2) A = `p_ate2` arredondado meio para cima, B = 100 − A; (3) tipos com ≥ 30 pedidos têm
linha, ≥ 10% do grupo = maior volume; (4) vermelho = B ≥ B de "(TODOS)" + 3; (5) faixa pela J7; (6) comparar com `#7`.

### 0000000.6 Validação, limites e pontos para o Caio

- Testes `tests/test_sla_tipo.py` (7): contagens, Outros, grupos e % com 1 casa; A e típico iguais aos slides 3/4;
  onde mais trava e vermelho (limite inclusivo de 3 pontos) com a faixa; variante "perto do geral" com tipo de menor
  volume em vermelho; poucos dados e sem a coluna; leitura da gold e HTML (seletor `#7`, legenda, sem nota, sem
  `style=""`). Suíte: **256 testes**.
- Capturas (scratchpad `s7/v5_1920.png`, `v5_1440_exclusivos.png`, `v5_1280.png`/`v3_1280.png`, `v5_1280_nao.png`,
  `v5_390_longo.png`): cabe sem rolar em 1920 × 1000, 1440 × 900 e 1280 × 800; 390 px sem rolagem lateral.
- Para o Caio: **Proativo** tem 67% acima de 2 dias e 91% do tempo dos lentos na Elaboração — provável efeito dos cards
  "[Pacote" (mesma ressalva do slide 6); vale olhar antes de apresentar. O recorte segue o dos slides 2–6 (ano todo).

## 000000. D42 — slide 6 do estudo: "Onde o tempo trava?" (25/10/2026)

> **Revisão de 25/10/2026 (noite), decisão do Caio:** "tempo travado" de um status = o **tempo inteiro**, naquele status,
> dos orçamentos que travaram nele (antes: só o excesso acima do limite). "Travou" segue = acima de Q3 + 1,5 × IQR do
> status; recorte o mesmo (ano todo; o Caio ainda decide jun–set sem pacotes). Números novos na 000000.4; o gancho
> "E em que tipo de pedido isso pesa mais? →" virou link para o slide 7.

Construído pela imagem de referência do Caio. URL: `/viu-agenciamento/sla/como-medimos#6` (`?talentos=` como nos slides
2–5). Código: `horas_por_status()` (horas por orçamento e status, guardadas junto com `entregas()`), `travas()` /
`_travas()` / `_trava_textos()` / `_etapa_ciclo()` / `_nome_status()` e regras **K1–K8** no fim de `sla/calculos.py`;
`montar_estudo_sla` (chave `travas`); `templates/como_medimos.html` (slide 6; o gancho do slide 5 virou link para `#6`);
`static/estilo.css` (bloco "slide 6"); testes `tests/test_sla_trava.py` (9). Contagem automática ("8 de 8" desde a D44).

### 000000.1 Pergunta e textos da tela

- Rótulo "Exploração dos dados · o ciclo, da entrada ao Aguardando Feedback"; título "Onde o tempo trava?".
- Em cima: só o seletor de talentos (o mesmo dos slides 2–5, links para `#6`). A definição "De todo o tempo travado,
  quanto fica em cada etapa. Travar é passar muito do tempo normal daquele status; o tempo travado é o tempo inteiro,
  naquele status, dos orçamentos que travaram." ficou fora da tela (ajuste do Caio,
  25/10) e vai só no `aria-label` da lista das etapas e nesta ficha.
- Quatro linhas numeradas: **1 Entrada**, **2 Elaboração**, **3 Revisão**, **4 Entrega**. Em cada uma das três primeiras,
  um cartão por status: % em serifa e o nome do status lado a lado; embaixo, "N travaram · típico X,X h" numa linha só e,
  quando K6, a nota "só até <mês>" numa linha curta, em itálico discreto; barra fina no pé proporcional ao maior status. Os 2 maiores em rosado claro com barra vermelha; os
  demais em cinza-lavanda com barra cinza-azulada. Em Elaboração, o cartão tracejado "Retorno da marca — espera da
  marca: fora da conta" (C2, D-SLA-2). Entrega: cartão escuro "Aguardando Feedback — fim do ciclo: a 1ª versão foi para
  o cliente" (mesma largura dos outros cartões) e, ao lado, discreta, "Daqui em diante o tempo é do cliente e não entra
  na conta."
- Faixa do pé (K7) e gancho "E em que tipo de pedido isso pesa mais? →" (link para o slide 7, D43).
- Tom visual leve, como o slide 5: % em serifa peso 400, nomes 500, meta 400 em `--tinta-2`; nada em negrito pesado.
- Acessibilidade: cada etapa é um `<h3>` ("Etapa N:" para leitor de tela) com a lista de cartões ligada a ele; cada
  cartão tem um texto completo para leitor de tela (`leitor`: "%, quantos de quantos travaram, passando de quanto, típico,
  'só até', 'um dos dois maiores pontos de trava'") e esconde os pedaços visuais (`aria-hidden`); o destaque é dito em
  texto, não só pela cor. Sem `style=""`, sem `<style>`; a barra é SVG com `width` no atributo.
- Layout (2ª rodada do Caio, 25/10: "cartões mais estreitos e compactos, tudo bonitinho"): grade alinhada de 5 colunas da
  mesma largura (no máximo 13,2em, alinhadas à esquerda; o Retorno da marca é a 5ª), cartões da mesma altura (5,2em) em
  todas as linhas, gap regular; coluna das etapas estreita (7,4em); o espaço vertical sobra entre as linhas das etapas
  (que dividem a altura por igual), não na largura dos cartões. Em tela estreita (< 860 px de palco), tudo empilha.

### 000000.2 Regras (K1–K8, `sla/calculos.py`)

| Código | Regra |
|---|---|
| K1 | Base = universo dos slides 2–5 (entregues nos meses completos de 1ª entrega, C7/D-SLA-1; grupo de talentos, C10); de cada orçamento, as horas úteis da equipe (sem almoço, C2) em cada status antes da 1ª entrega, **sem o Retorno Marca** (D-SLA-2). Passagens repetidas no mesmo status somam. Por orçamento, a soma dos status = `h_trabalho` (testado). n < 30 ou nenhum tempo travado → "Ainda não há orçamentos suficientes…" |
| K2 | Status → etapa: "Entrada" → Entrada; começa com "Em elabora" → Elaboração; começa com "Em revis" → Revisão; qualquer outro status da equipe → linha "Outros status" (só aparece se existir; nenhum na carga de 23/10). Nome na tela = nome do board sem o prefixo da etapa; "Entrada" → "Fila de entrada"; status gerais "Em Elaboração"/"Em revisão" → "Em elaboração"/"Em revisão"; grafias do mesmo status ("Em elaboração - GP" e "Em elaboração GP") viram um cartão |
| K3 | Por status: tempo de cada orçamento que passou por ele (inclusive 0 h, passagem fora do expediente); **típico** = mediana; **limite normal** = Q3 + 1,5 × (Q3 − Q1) do próprio status (Tukey, quantis lineares, como o passo 3 do slide 2); **travou** = tempo no status acima do limite |
| K4 | **Tempo travado** do status = soma do **tempo inteiro**, naquele status, dos orçamentos que travaram nele (**decisão do Caio, 25/10/2026**; antes era só o excesso acima do limite). % = tempo travado do status ÷ tempo travado de todos os status, inteiros pelo maior resto somando 100 (E8c); "<1%" se há tempo travado e o inteiro dá 0 |
| K5 | Em cada etapa, status em ordem de tempo travado; até 3 cartões com nome e o resto num cartão "Outros N status" (% = soma dos % escritos; "N travaram" = orçamentos distintos que travaram em algum deles; nomes no texto do leitor de tela e na dica). Sem tempo travado no resto, o "Outros" não aparece (valeria 0%). Barra = tempo travado ÷ o do maior status. Destaque = os 2 status com mais tempo travado (o "Outros" nunca) |
| K6 | Status visto só em orçamentos entregues antes do último mês completo: o cartão e a faixa dizem "só até <mês>" (os sub-status começaram em 14/05/2026; o "Em Elaboração" geral parou de aparecer) |
| K7 | Faixa do pé: o maior com mais de 50% → "O tempo trava principalmente em um ponto: **X** concentra *p% do tempo travado*."; os 2 maiores somando menos de 40% → "O tempo trava espalhado pelo ciclo: os dois pontos maiores, **X** e **Y**, somam só *p% do tempo travado*."; senão → "O tempo trava principalmente em dois pontos: **X** e **Y** somam *p% do tempo travado*." p = soma dos % escritos nos cartões. Sem artigo antes do nome (os nomes vêm dos dados) |
| K8 | Gancho fixo: "E em que tipo de pedido isso pesa mais?", link para o slide 7 (`#7`, D43) |

### 000000.3 Mapeamento status → etapa (carga 23/10/2026, passos da equipe antes da 1ª entrega)

| Status no board | Etapa | Nome na tela | Observação |
|---|---|---|---|
| Entrada | Entrada | Fila de entrada | |
| Em Elaboração | Elaboração | Em elaboração | status geral, jan–mai (antes dos sub-status de 14/05); aparece em pedidos entregues até jul |
| Em elaboração - Orçamentos | Elaboração | Orçamentos | |
| Em elaboração (Produção) | Elaboração | Produção | |
| Em elaboração - Cotação Externa | Elaboração | Cotação Externa | |
| Em elaboração - Cotação Gestão de Elenco | Elaboração | Cotação Gestão de Elenco | |
| Em elaboração - Validação Gestão Esporte | Elaboração | Validação Gestão Esporte | |
| Em elaboração - Audiência / - Conteúdo | Elaboração | Audiência / Conteúdo | poucos pedidos |
| Em elaboração - GP e Em elaboração GP | Elaboração | GP | duas grafias, um cartão |
| Em Elaboração - Validação Talents | Elaboração | Validação Talents | 2 passagens em mai (1 no universo); parece "Validação Talento" fora do lugar — **a confirmar** |
| Em elaboração - Retorno Marca/Executivo | — (fora) | cartão tracejado "Retorno da marca" | D-SLA-2 |
| Em revisão | Revisão | Em revisão | status geral, segue em uso (pouco) depois de mai |
| Em revisão - Validação Talento | Revisão | Validação Talento | |
| Em revisão - Validação Talent Manager | Revisão | Validação Talent Manager | |
| Em revisão (Planejamento) | Revisão | Planejamento | 4 pedidos, nenhum travou (fica fora dos cartões: 0%) |
| Aguardando Feedback | Entrega (fim) | cartão escuro | fase `cliente` (C1) |

Da referência do Caio, todos os status existem nos dados; "Em revisão" é o status geral (sem sub-status). A tela mostra
também "Em elaboração" (geral), que a referência não tinha, porque é o maior tempo travado do ano (ver 000000.6).

### 000000.4 Memória de cálculo (carga 23/10/2026 20:23:42 UTC, meses completos jan–set) — app = BigQuery

Por status: n (orçamentos que passaram), típico (mediana exata → tela), limite (Q3 + 1,5 × IQR), travaram, tempo travado
(tempo inteiro de quem travou, h — K4 revista em 25/10), % na tela. **Todos (2.348)** — total travado 32.558,16 h:

| Etapa | Status | n | típico | limite | travaram | travado (h) | % |
|---|---|---|---|---|---|---|---|
| Entrada | Fila de entrada ★ | 2.348 | 2,760 → 2,8 h | 19,73 | 174 | 6.002,35 | 19% |
| Elaboração | Em elaboração ★ (só até jul) | 376 | 4,951 → 5,0 h | 38,99 | 46 | 13.470,66 | 41% |
| Elaboração | Produção | 333 | 8,709 → 8,7 h | 32,50 | 39 | 3.033,61 | 9% |
| Elaboração | Orçamentos | 911 | 0,741 → 0,7 h | 9,60 | 117 | 2.982,20 | 9% |
| Elaboração | Outros 7 status (Cotação Externa 7/319,31; Cotação Gestão de Elenco 5/295,88; Validação Gestão Esporte 4/125,80; Audiência, Conteúdo, GP, Validação Talents 0) | — | — | — | 16 | 740,99 | 2% |
| Revisão | Validação Talento | 1.020 | 2,990 → 3,0 h | 20,77 | 85 | 3.408,80 | 11% |
| Revisão | Em revisão | 453 | 5,655 → 5,7 h | 33,02 | 34 | 1.951,73 | 6% |
| Revisão | Validação Talent Manager | 398 | 2,032 → 2,0 h | 12,30 | 37 | 967,82 | 3% |
| Revisão | (Planejamento: 4 pedidos, 0 travou — sem cartão) | 4 | 18,7 h | 21,44 | 0 | 0 | 0% |

Faixa: "O tempo trava principalmente em dois pontos: **Em elaboração** (só até jul) e **Fila de entrada** somam *60% do
tempo travado*." (Com o excesso, era "um ponto": Em elaboração 56%.)

**Exclusivos (1.610, total 22.161,72 h):** Em elaboração ★ 45% (37 travaram · 10.027,76 h · só até jul); Fila de entrada
★ 20% (125 · 4.399,18 h); Produção 11% (31 · 2.354,60); Validação Talento 8% (71 · 1.852,29); Em revisão 6% (29 ·
1.362,62); Orçamentos 5% (79 · 1.102,54); Validação Talent Manager 4% (35 · 931,09); Outros 5 status 1% (Cotação Externa 3
· 79,46; Validação Gestão Esporte 1 · 52,17). Faixa: "dois pontos: **Em elaboração** (só até jul) e **Fila de entrada**
somam *65%*".

**Não exclusivos (725, total 8.412,47 h):** Em elaboração ★ 39% (11 · 3.300,96 · só até jul); Fila de entrada ★ 15% (37 ·
1.261,89); Validação Talento 13% (17 · 1.089,82); Orçamentos 11% (10 · 936,89); Em revisão 7% (7 · 576,48 · só até ago);
Produção 6% (4 · 497,95); Outros 6 status 9% (Cotação Externa 8 · 354,92; Cotação Gestão de Elenco 5 · 295,88; Validação
Gestão Esporte 3 · 73,63); Validação Talent Manager <1% (1 · 24,05). Faixa: "dois pontos: … somam *54%*".

Conferências: por orçamento, soma dos status = `h_trabalho` (diferença máxima 6 × 10⁻¹⁴ h nos três grupos); nenhum
status de Retorno Marca na base; % somam 100. Nada fixo: tudo vem do recorte da carga e do grupo.

### 000000.5 SQL para reproduzir (BigQuery, só SELECT)

Mesmos CTEs `m` (sem `nome_projeto`), `fer`, `ini`, `pronto`, `base` da 0.6.1, com `base` filtrada em
`FORMAT_DATETIME('%Y-%m', pr.p.entrada) BETWEEN '2026-01' AND '2026-09'`, e no fim:

```sql
eq AS (SELECT b.projeto_id, b.exclusivo, e.status, e.entrada, e.saida FROM base b JOIN m e ON e.projeto_id = b.projeto_id
         AND e.passo < b.pp AND e.fase = 'equipe' AND e.saida IS NOT NULL
         AND NOT STARTS_WITH(LOWER(e.status), 'em elaboração - retorno marca')),                       -- K1, D-SLA-2
us AS (SELECT projeto_id, status,
         SUM(GREATEST(0, DATETIME_DIFF(LEAST(saida, DATETIME(d, TIME(j.h1,0,0))), GREATEST(entrada, DATETIME(d, TIME(j.h0,0,0))), MICROSECOND))) us
       FROM eq, UNNEST(GENERATE_DATE_ARRAY(DATE(entrada), DATE(saida))) d, UNNEST([STRUCT(10 AS h0, 13 AS h1), STRUCT(14, 19)]) j
       WHERE EXTRACT(DAYOFWEEK FROM d) BETWEEN 2 AND 6 AND d NOT IN (SELECT d FROM fer) GROUP BY 1, 2),
st AS (SELECT t.projeto_id, t.exclusivo, t.status, IFNULL(us.us, 0) us          -- passagem só fora do expediente = 0 h
       FROM (SELECT DISTINCT projeto_id, exclusivo, status FROM eq) t LEFT JOIN us USING (projeto_id, status)),
nm AS (SELECT *, CASE WHEN LOWER(TRIM(status)) = 'entrada' THEN 'Entrada'
                      WHEN STARTS_WITH(LOWER(status), 'em elabora') THEN 'Elaboração'
                      WHEN STARTS_WITH(LOWER(status), 'em revis') THEN 'Revisão' ELSE 'Outros' END etapa,      -- K2
         CASE WHEN LOWER(TRIM(status)) = 'entrada' THEN 'Fila de entrada'
              ELSE IFNULL(NULLIF(REGEXP_REPLACE(TRIM(REGEXP_REPLACE(status, r'(?i)^em (elaboração|revisão)\s*[-–]?\s*', '')), r'^\((.*)\)$', r'\1'), ''),
                          IF(STARTS_WITH(LOWER(status), 'em elabora'), 'Em elaboração', 'Em revisão')) END nome
       FROM st),
po AS (SELECT etapa, nome, projeto_id, ANY_VALUE(exclusivo) exclusivo, SUM(us) / 3.6e9 h FROM nm GROUP BY 1, 2, 3),
v AS (SELECT g, etapa, nome, h FROM po, UNNEST(['Todos', IF(exclusivo, 'Exclusivos', IF(NOT exclusivo, 'Nao exclusivos', NULL))]) g WHERE g IS NOT NULL),
w AS (SELECT *, PERCENTILE_CONT(h, 0.5) OVER x med, PERCENTILE_CONT(h, 0.25) OVER x q1, PERCENTILE_CONT(h, 0.75) OVER x q3
      FROM v WINDOW x AS (PARTITION BY g, etapa, nome)),
l AS (SELECT *, q3 + 1.5 * (q3 - q1) lim FROM w)                                                         -- K3
SELECT g, etapa, nome, COUNT(*) n, ROUND(ANY_VALUE(med), 3) tipico, ROUND(ANY_VALUE(lim), 3) limite,
  COUNTIF(h > lim) travaram, ROUND(SUM(IF(h > lim, h, 0)), 2) travado     -- K4: tempo inteiro de quem travou (25/10)
FROM l GROUP BY 1, 2, 3 ORDER BY g DESC, travado DESC;
-- 25/10/2026 (carga 23/10 20:23:42 UTC, conferido de novo com a K4 revista), Todos (travaram | travado):
--   Em elaboração 46 | 13470,66 · Fila de entrada 174 | 6002,35 · Validação Talento 85 | 3408,8 · Produção 39 | 3033,61
--   Orçamentos 117 | 2982,2 · Em revisão 34 | 1951,73 · Validação Talent Manager 37 | 967,82 · Cotação Externa 7 | 319,31
--   Cotação Gestão de Elenco 5 | 295,88 · Validação Gestão Esporte 4 | 125,8 → total 32558,16
--   (Exclusivos e Não exclusivos: iguais a 000000.4, totais 22161,72 e 8412,47; com o excesso dava 11677,27, 2568,84…)
```

Atenção ao juntar `us`: juntar só por `projeto_id, status` (com `exclusivo` no `USING`, os 13 orçamentos sem talento ficam
com 0 h e "Todos" sai diferente — erro cometido e corrigido na conferência de 25/10).

Passo a passo: (1) rodar a SQL; (2) % = travado ÷ soma do travado do grupo, inteiros pelo maior resto somando 100;
(3) por etapa, os 3 maiores com nome e o resto somado em "Outros"; (4) destaque = os 2 maiores tempos travados; (5) faixa pela
K7; (6) comparar com `#6` nos três grupos.

### 000000.6 Validação, limites e decisões para o Caio

- Testes: `tests/test_sla_trava.py` (9): soma por status = `h_trabalho` e Retorno Marca fora (movimentos sintéticos,
  passagens repetidas somadas); limite de Tukey e tempo travado inteiro (K4 revista); % somando 100, destaque dos 2 maiores, "Outros" (soma dos %,
  orçamentos distintos), "<1%" e grafias do GP juntas; variantes um/dois/espalhado; "só até" e poucos dados; mapeamento e
  nomes; HTML (8 slides desde a D44, seletor → `#6`, textos fixos, sem termos técnicos, sem `style=""`; gancho do slide 5 → `#6` e do 6 → `#7`);
  slide 6 com poucos dados. Suíte: **243 testes** na D42; **256** com a K4 revista, D43 e D44.
- Capturas conferidas (scratchpad da sessão, versão final `s6/v3_1920.png`, `v3_1440.png`, `v3_1280.png`,
  `v3_1280_exclusivos.png`, `v3_1280_nao-exclusivos.png`, `v3_390.png`, `v3_390_longo.png`; `s6_*` = 1ª versão, antes do
  ajuste do Caio): cabe sem rolar em 1920 × 1000, 1440 × 900 e 1280 × 800 (as quatro linhas dividem a altura; faixa e
  gancho acima da navegação; "N travaram · típico" numa linha em todas); 390 × 844 por emulação: documento com 390 px,
  cartões empilhados, sem rolagem lateral.
- **Leitura de hoje e por que pede decisão:** o maior ponto de trava do ano é o status geral **"Em elaboração"**, que só
  existiu até maio (pedidos entregues até julho). Esse tempo vem quase todo dos cards "[Pacote" (X6): **sem os pacotes**,
  "Em elaboração" cai para 8% e a ordem vira Fila de entrada 28% · Orçamentos 22% · Validação Talento 19% · Em revisão
  10% (Todos, 2.275 pedidos; números com o excesso, antes da K4 revista). **Só com os meses dos sub-status (jun–set, como a C14)**: Orçamentos 25% · Produção 24% ·
  Validação Talento 22% · Fila de entrada 18% (Todos, 1.554 pedidos; faixa "dois pontos": Orçamentos e Produção, 49%);
  Exclusivos: Produção 31% · Fila 25%; Não exclusivos: Orçamentos 28% · Validação Talento 26%. A tela segue o pedido
  (universo dos slides 2–5), com "só até jul" no cartão e na faixa.
- Decisões: (a) **decidida pelo Caio em 25/10/2026**: tempo travado = tempo inteiro de quem travou (K4); a validar:
  (b) universo do ano inteiro × só jun–set (sub-status) × sem pacotes; (c) "Em Elaboração - Validação Talents" (1 pedido)
  em Elaboração mesmo; (d) limite por status com poucos pedidos (Audiência 12, GP 4, Planejamento 4 — com n pequeno o
  limite quase não marca ninguém).

## 00000. D41 — slide 5 do estudo: "Foi um mês ruim, ou é sempre assim?" (25/10/2026)

Construído pela imagem de referência do Caio, com dois ajustes dele no mesmo dia (eixo com os 12 meses; faixa do pé
respondendo "sazonal ou padrão da equipe?"). URL: `/viu-agenciamento/sla/como-medimos#5` (`?talentos=` como nos slides 2–4).
Código: `meses_estudo()` / `_meses()` / `_mes_textos()` / `_destoam()` / `_sorteio()` e regras **U1–U9** no fim de
`sla/calculos.py`; `montar_estudo_sla` (chave `meses_estudo`); `templates/como_medimos.html` (slide 5; o gancho do slide 4
virou link para `#5`); `static/estilo.css` (bloco "slide 5"); testes `tests/test_sla_mes.py` (14). O estudo passa a ter
5 slides ("5 de 5", contagem automática).

### 00000.1 Pergunta e textos da tela

- Rótulo "Exploração dos dados · foi um mês ruim, ou é sempre assim?"; título por regra (U8): "A demora não é de um mês.
  Acontece o ano todo." (padrão e picos), "A demora pesa em alguns meses do ano." (sazonal) ou "Em todos os meses, quase
  nada passa de 2 dias." (raro).
- Seletor de talentos sozinho em cima (o mesmo dos slides 2–4), links para `#5`.
- Legenda sem termos técnicos: "— o típico do mês" · "▭ faixa onde fica a maioria (metade dos pedidos)" · "● cada ponto é
  um pedido" · à direita "▲ mais de 10 dias · N pedidos". O rótulo "acima desta linha: mais de 2 dias" fica sobre a linha
  tracejada (U9); sem lugar livre, ou em tela estreita, vai para a legenda.
- Gráfico: 12 colunas (jan a dez) com fundo alternado; um ponto por orçamento (cor pela faixa: até 2 dias lavanda, 2 a 5
  dias laranja, mais de 5 dias vermelho, com transparência); faixa da maioria por mês; linha do típico com o valor
  ("14 h", "16,4 h"); linha tracejada em 2 dias (16 h); eixo y em dias (0, 1, 2, 3, 5, 10 dias, escala de raiz quadrada).
  Meses ainda sem mês completo (hoje out, nov, dez) ficam vazios, nome em cinza e itálico.
- Abaixo do eixo (tabela de texto real): nome do mês; "passam de 2 dias" (vermelho) com o B do mês; "pedidos" com o n.
- Faixa do pé curta (1 linha em 1280–1920) e gancho (U8), por exemplo (Todos): "**Não é sazonal:** todo mês, de 40% a 51%
  dos pedidos passam de 2 dias. *O problema é o processo, não o mês* — é nele que está a solução." · "Se é assim, onde o
  tempo trava? →" (só texto; o slide 6 virá depois).
- Tom visual (2ª rodada do Caio, "grosseiro" → leve): nenhum texto do gráfico em negrito (meses, %, pedidos, típicos, eixo,
  rótulo da linha de 2 dias — peso 400, tamanhos menores, `--tinta-2`/`--tinta-3`); % em vermelho menos saturado
  (`#a8524c`, 5,3:1 no branco); pontos menores (3,8) e mais transparentes (0,32 / 0,48 / 0,55); linha do típico de 1,3 e
  ponto de raio 2,8; faixa da maioria e grade mais claras. Texto do SVG ≥ 11 px reais em 1280.
- Acessibilidade: SVG `role="img"` com `aria-label` resumindo cada mês (típico, % que passa de 2 dias, pedidos), os
  triângulos e os meses vazios; a linha de números é uma tabela com `<caption>` e cabeçalhos; meses vazios com "ainda sem
  mês completo" para leitor de tela; quadro do gráfico focável (`tabindex="0"`), que rola na horizontal só em tela
  estreita. Sem `style=""`, sem `<style>`.
- Desempenho: ~2.350 pontos desenhados como 3 `<path>` (um por cor, `M x y h0` com ponta redonda), coordenadas com 1 casa
  geradas no servidor; o slide pesa ~46 KB de HTML; sem JS.

### 00000.2 Regras (U1–U9, `sla/calculos.py`)

| Código | Regra |
|---|---|
| U1 | Universo = o dos slides 2–4 (X1, W1, V1): entregues nos meses completos de 1ª entrega (C7, D-SLA-1), grupo de talentos (C10); h = horas da equipe sem almoço (C2). n < 30 ou menos de 2 meses completos com pedidos → "Ainda não há orçamentos suficientes…" |
| U2 | Eixo congelado no ano: sempre 12 colunas (jan–dez). Mês vigente (parcial, hoje outubro) e futuros = colunas vazias, sem números; mês completo sem pedido = "—" |
| U3 | B do mês = h > 16 h, escrito pela conta da página SLA (C8): 100 − "até 2 dias" arredondado. Típico = mediana exata, escrita como na página (C6, `_h_meta`: 16,34 h → "16,4 h"). Faixa da maioria = 1º a 3º quartil (quantis lineares) |
| U4 | Eixo y: dias de 8 h, raiz quadrada; marcas 0/1/2/3/5/10 dias (0/8/16/24/40/80 h); > 80 h → triângulo no topo |
| U5 | x do ponto = centro da coluna + (u − 0,5) × 80% da largura, u = MD5 do `projeto_id` (determinístico; não muda entre cargas nem com a ordem das linhas) |
| U6 | Cor = faixa do slide 2 (X3): ≤ 16 h, 16–40 h, > 40 h |
| U7 | Mês destoa se B − mediana dos B mensais > 10 pontos OU típico − mediana dos típicos mensais > 4 h. Leitura: nenhum destoa → **padrão**; 1–2 → **picos**; 3+ → **sazonal**; todos os B < 10% → **raro** |
| U8 | Título, faixa do pé curta e gancho por leitura (textos no código e em 00000.3); só números visíveis no gráfico (os B por mês). Gancho único: "Se é assim, onde o tempo trava? →" |
| U9 | Rótulos sem colisão: valor do típico abaixo do ponto (acima quando passa de 2 dias); rótulo da linha de 2 dias na posição mais à direita sem típico acima de 2 dias embaixo dele (colunas vazias contam como livres); senão, legenda |

**Por que "3+ meses" e não "3+ seguidos" (sugestão do Caio, ajustada pelos dados):** nos não exclusivos, abril, maio e
agosto destoam (75%, 70%, 75% contra mediana 57%; típicos 26, 24 e 28 h contra 18 h) — dois seguidos e um isolado. Com um
só ano de dados não dá para separar calendário de acaso; o que muda a ação é haver vários meses pesados (planejar a
equipe), então vale 3+ em qualquer posição. Se forem seguidos, o texto diz "de abril a junho"; senão, lista os meses. Por
isso a recomendação é só "vale planejar a equipe para esses meses", sem afirmar ciclo. A frase do volume da referência
("o volume dobrou sem piorar o prazo") saiu, e a faixa foi encurtada (2ª rodada do Caio: 1 linha, no máximo 2).

### 00000.3 Memória de cálculo (carga 23/10/2026 20:23:42 UTC, meses completos jan–set) — app = BigQuery

| Grupo | Mês | jan | fev | mar | abr | mai | jun | jul | ago | set | Total |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Todos | pedidos | 111 | 108 | 159 | 215 | 201 | 288 | 548 | 378 | 340 | **2.348** |
| | passam de 2 dias | 40% | 45% | 42% | 50% | 51% | 51% | 43% | 41% | 41% | |
| | típico (mediana exata) | 13 h (13,162) | 16 h (15,712) | 15 h (14,888) | 16,4 h (16,343) | 16,4 h (16,317) | 16,5 h (16,460) | 13 h (12,921) | 13 h (12,597) | 14 h (13,560) | |
| | faixa da maioria (Q1–Q3) | 5,95–24,27 | 7,98–24,27 | 8,44–25,44 | 7,73–29,18 | 6,28–35,12 | 7,28–30,38 | 5,61–26,43 | 6,30–24,01 | 7,05–25,14 | |
| | triângulos (> 10 dias) | 3 | 4 | 3 | 8 | 12 | 12 | 32 | 5 | 4 | **83** |
| Exclusivos | pedidos | 75 | 55 | 125 | 153 | 151 | 192 | 344 | 277 | 238 | **1.610** |
| | passam de 2 dias | 36% | 47% | 39% | 40% | 44% | 46% | 34% | 29% | 39% | |
| | típico | 12 h | 15 h | 14 h | 14 h | 12 h | 15 h | 10 h | 10 h | 12 h | |
| | triângulos | 1 | 2 | 2 | 1 | 12 | 5 | 29 | 1 | 2 | **55** |
| Não exclusivos | pedidos | 32 | 53 | 33 | 60 | 50 | 96 | 200 | 100 | 101 | **725** |
| | passam de 2 dias | 44% | 43% | 48% | **75%** | **70%** | 60% | 57% | **75%** | 47% | |
| | típico | 14 h | 16 h | 15 h | **26 h** | **24 h** | 19 h | 18 h | **28 h** | 16 h | |
| | triângulos | 1 | 2 | 1 | 5 | 0 | 7 | 3 | 4 | 2 | **25** |

Leitura U7: **Todos** — mediana dos B = 43, dos típicos = 14,9 h; nenhum mês passa de 53% nem de 18,9 h → **padrão**.
**Exclusivos** — mediana dos B = 39, dos típicos = 12,0 h; o maior B é 47% (fev, 8 pontos) e o maior típico 15,4 h (fev,
3,4 h) → **padrão**. **Não exclusivos** — mediana dos B = 57, dos típicos = 18,1 h; abril (75%, 26,1 h), maio (70%,
23,7 h) e agosto (75%, 28,0 h) destoam pelos dois critérios → **sazonal**.

Textos gerados:
- Todos — "A demora não é de um mês. Acontece o ano todo." / "**Não é sazonal:** todo mês, de 40% a 51% dos pedidos
  passam de 2 dias. *O problema é o processo, não o mês* — é nele que está a solução."
- Exclusivos — mesmo título / "**Não é sazonal:** todo mês, de 29% a 47% dos pedidos passam de 2 dias. …"
- Não exclusivos — "A demora pesa em alguns meses do ano." / "**Há meses mais pesados:** em abril, maio e agosto, de 70% a
  75% passam de 2 dias, contra 43% a 60% no resto do ano. *Vale planejar a equipe para esses meses.*"
- Gancho nos três: "Se é assim, onde o tempo trava? →".
- Variante picos (testada): "**No geral, não é sazonal:** quase todo mês, de {Bmin}% a {Bmax}% passam de 2 dias; só {mês}
  fugiu ({mês} e {mês} fugiram) do padrão. *O problema é o processo*, com picos pontuais." — "do padrão" porque um mês pode
  destoar só pelo típico; o intervalo de % exclui os meses que destoam.

Conferências: soma dos pedidos por mês = n do grupo (2.348 / 1.610 / 725); B de cada mês = 100 − "até 2 dias" do mês na
página SLA, nos 27 grupo × mês (sem diferença de arredondamento nesta carga: nenhum mês cai no meio ponto); outubro
(parcial) fora. Nada fixo: tudo vem do recorte da carga.

### 00000.4 SQL para reproduzir (BigQuery, só SELECT) — CTEs `m`, `fer`, `ini`, `pronto`, `base`, `us` da SQL 0.6.1

```sql
p AS (SELECT b.*, IFNULL(us.us, 0) / 3.6e9 h FROM base b LEFT JOIN us USING (projeto_id)
      WHERE b.mes BETWEEN '2026-01' AND '2026-09'),                                   -- U1: meses completos
v AS (SELECT g, mes, h FROM p, UNNEST(['Todos', IF(exclusivo, 'Exclusivos', IF(NOT exclusivo, 'Nao exclusivos', NULL))]) g
      WHERE g IS NOT NULL),
w AS (SELECT *, PERCENTILE_CONT(h, 0.5) OVER x med, PERCENTILE_CONT(h, 0.25) OVER x q1, PERCENTILE_CONT(h, 0.75) OVER x q3
      FROM v WINDOW x AS (PARTITION BY g, mes))
SELECT g, mes, COUNT(*) n, ROUND(ANY_VALUE(med), 3) mediana, ROUND(ANY_VALUE(q1), 2) q1, ROUND(ANY_VALUE(q3), 2) q3,
  COUNTIF(h > 16) n_acima2, ROUND(100 * COUNTIF(h <= 16) / COUNT(*), 2) p_ate2, COUNTIF(h > 80) n_acima10
FROM w GROUP BY g, mes ORDER BY g DESC, mes;
-- 25/10/2026 (carga 23/10 20:23:42 UTC) — igual ao app (B = 100 − arredondar(p_ate2)):
-- Todos 2026-01 | 111 | 13,162 | 5,95 | 24,27 | 44 | 60,36 | 3     Todos 2026-07 | 548 | 12,921 | 5,61 | 26,43 | 234 | 57,30 | 32
-- Todos 2026-04 | 215 | 16,343 | 7,73 | 29,18 | 108 | 49,77 | 8    Nao exclusivos 2026-08 | 100 | 27,956 | 18,57 | 53,40 | 75 | 25,00 | 4
-- (as 27 linhas batem com a tabela 00000.3)
```

Passo a passo: (1) rodar a SQL; (2) B do mês = 100 − p_ate2 arredondado (meio para cima); (3) típico = mediana (horas
inteiras; entre 16 e 16,5 h, 1 casa para cima); (4) triângulos = n_acima10; (5) U7: mediana dos B e dos típicos dos meses
do grupo, marcar os meses acima de +10 pontos ou +4 h; (6) comparar com a tela (`#5`) nos três grupos.

### 00000.5 Validação e limites

- Testes: `tests/test_sla_mes.py` (14): soma dos pedidos = n e B = página em cada grupo; 12 colunas com os meses vazios
  (U2); B no meio ponto pela C8; típico e faixa da maioria; escala (0/1/2/3/5/10 dias em ordem, raiz quadrada, linha de
  2 dias) e triângulos (> 80 h; 80 h fica no topo do eixo); posição determinística e dentro da coluna, coordenadas com 1
  casa; critério de destoar pelos dois lados do limite (10 pontos, 4 h); variantes padrão, picos (1 e 2 meses), sazonal
  (seguidos e espalhados, inclusive o caso real dos não exclusivos) e raro; rótulo da linha de 2 dias (borda direita,
  antes do ponto, legenda); poucos dados; HTML (5 slides, seletor → `#5`, legenda sem termos técnicos, tabela, sem
  `style=""`; gancho do slide 4 → `#5`). Suíte: **234 testes**.
- Capturas conferidas (scratchpad da sessão, `s5/h_<grupo>_<largura>.png` na versão final; `g_…` antes da 2ª rodada): 1920 × 1000, 1440 × 900 e 1280 × 800 nos três
  grupos — cabe sem rolar (altura do conteúdo = altura da lâmina), faixa e gancho com folga até a navegação; 390 × 844
  por emulação de dispositivo nos três grupos — largura do documento = 390, o gráfico (812 px) rola dentro do próprio
  quadro, texto do SVG ≈ 11 px.
- Limites: um só ano de dados — "sazonal" aqui quer dizer "meses mais pesados neste ano", não um ciclo comprovado; meses
  com poucos pedidos (não exclusivos: jan 32, mar 33) oscilam mais; os pacotes do slide 2 seguem na base (julho tem 32
  triângulos em Todos).

## 0000. D40 — slide 4 do estudo: "Para onde vai o tempo?" (25/10/2026)

Construído pela imagem de referência do Caio. URL: `/viu-agenciamento/sla/como-medimos#4` (`?talentos=` como nos slides 2 e 3).
Código: `tempo_cem()` / `_tempo()` / `_tempo_textos()` / `_parte()` / `_fracao()` e regras **V1–V8** no fim de
`sla/calculos.py` (os % de pedidos vêm de `_cem_pcts()`, a mesma função do slide 3); `montar_estudo_sla` (chave `tempo`);
`templates/como_medimos.html` (slide 4; o gancho do slide 3 virou link para `#4`); `static/estilo.css` (bloco "slide 4");
testes `tests/test_sla_tempo.py` (35). O estudo passa a ter 4 slides ("4 de 4", contagem automática do `apresentacao.js`).

### 0000.1 Pergunta e textos da tela

- Rótulo "Exploração dos dados · de cada 100 pedidos e de cada 100 horas"; título "Para onde vai o tempo?".
- Seletor de talentos (Todos / Exclusivos / Não exclusivos, com o típico de cada um) sozinho em cima, como no slide 3; links para `#4`.
- Cartão "Saem em até 2 dias" (fio marinho): barra "pedidos" (tom claro) com A e barra "horas com a equipe" (tom escuro) com
  HA, de 0 a 100 sobre trilho cinza; frase em negrito (V5); linhas "até 1 dia — N pedidos — M horas", "de 1 a 2 dias — …".
- Cartão "Passam de 2 dias" (fio vermelho): B e HB; frase; linhas "de 2 a 3 dias", "de 3 a 5 dias", "mais de 5 dias".
- Notas: "**Prazo** O maior ganho de tempo de entrega está nesses B pedidos." e "**Fluxo** Com menos pedidos parados, a fila
  anda e a equipe absorve mais demanda com o mesmo time."
- Faixa do pé (redação do Caio): "Na maior parte das vezes entregamos em até 2 dias. Mas os **B% que passam disso** concentram
  **HB% do tempo** que os pedidos ficam com a equipe. *É aí que está o ganho:* encurtando esses casos, a fila anda mais rápido
  e o mesmo time dá conta de mais pedidos." Gancho (só texto; o slide 5 vem depois): "Mas esses B% foram um mês ruim, ou é sempre assim? →".
- Acessibilidade: cada barra é um SVG `role="img"` com "N% dos pedidos" / "N% das horas de trabalho da equipe"; o número
  grande ao lado fica `aria-hidden` (já dito pela barra); as linhas são uma tabela com `<caption>` para leitor de tela e
  "de cada 100" oculto; cor sempre com número e texto; nada de `style=""`.
- Layout: `.tempo-meio` ocupa a altura entre o título e a faixa do pé (`flex: 1 1 auto; justify-content: space-evenly`, como o
  slide 3); faixa e gancho no mesmo lugar do slide 3 (gancho em y ≈ 772 / 716 em 1440 × 900 / 1280 × 800). Em palco estreito
  ou alto (`width < 860px` ou `aspect-ratio < 1.2`) os cartões e as notas empilham.

### 0000.2 Regras (V1–V8, `sla/calculos.py`)

| Código | Regra |
|---|---|
| V1 | Universo = o dos slides 2 e 3 (X1, W1): entregues nos meses completos de 1ª entrega (C7), grupo de talentos (C10); h = horas da equipe sem almoço (C2). n < 30 ou soma de h = 0 → "Ainda não há orçamentos suficientes…" |
| V2 | Pedidos: as cinco faixas do slide 3 (W2) com os **mesmos %** (W3, função única `_cem_pcts`): A = até 1 dia + 1 a 2 dias (= "% em até 2 dias" da página, C8), B = 100 − A |
| V3 | Horas: H_faixa = soma de h da faixa ÷ soma de h do recorte × 100, inteiros pelo maior resto (E8c, somam 100); HA = H₁ + H₂; HB = 100 − HA. As linhas de cada cartão somam o número grande |
| V4 | Barras de 0 a 100 (largura = o número), pedidos em tom claro e horas em tom escuro, com texto para leitor de tela |
| V5 | Frase do cartão (`_parte`): "<fração dos pedidos> dos pedidos, <fração das horas> do tempo." (V8); 0 pedidos → "Nenhum pedido neste grupo." |
| V6 | Notas Prazo e Fluxo; Prazo cita B ("nesses B pedidos"; B = 1 "nesse pedido"); B = 0 → sem notas |
| V7 | Faixa do pé: A > 50 "Na maior parte das vezes entregamos em até 2 dias. Mas os…"; A = 50 "Metade dos pedidos sai em até 2 dias. Mas os…"; A < 50 "Neste grupo, menos da metade sai em até 2 dias. E os…"; B = 1 "o 1% que passa disso concentra"; B = 0 "Neste grupo, todos saem em até 2 dias de trabalho…". Gancho "Mas esses B% foram um mês ruim, ou é sempre assim?" (B = 1 "esse 1% foi"; B = 0 "E isso se repete todo mês?") |
| V8 | `_fracao(p)` sobre 1/10, 1/5, 1/4, 1/3, 1/2, 2/3, 3/4, 4/5, 9/10: (a) 0 "menos de 1%", 100 "100%", 50 "metade"; (b) até 1 ponto de uma fração "cerca de …"; (c) até 3 pontos abaixo "quase …" (p ≥ 50) ou "menos de …" (p < 50), senão até 3 acima "pouco mais de …"; (d) longe: se a metade é vizinha "mais/menos da metade", senão a vizinha mais perto ("mais de" a de baixo / "menos de" a de cima). Ex.: 59 mais da metade, 22 menos de um quarto, 78 quase quatro quintos, 41 menos da metade |

### 0000.3 Memória de cálculo (carga 23/10/2026 20:23:42 UTC, meses completos jan–set) — app = BigQuery

| Grupo | n | Horas da equipe (soma) | Horas por faixa ≤8 / 8–16 / 16–24 / 24–40 / >40 h | % das horas (exato) | Pedidos por faixa (slide 3) | Horas por faixa (maior resto) | A / HA | B / HB |
|---|---|---|---|---|---|---|---|---|
| Todos | 2.348 | 59.752,15 h | 2.720,17 / 6.864,64 / 7.141,75 / 12.170,35 / 30.855,24 | 4,55 / 11,49 / 11,95 / 20,37 / 51,64 | 31 / 25 / 15 / 17 / 12 | 5 / 11 / 12 / 20 / 52 | **56 / 16** | **44 / 84** |
| Exclusivos | 1.610 | 37.694,16 h | 2.187,16 / 4.791,33 / 4.298,32 / 6.876,51 / 19.540,83 | 5,80 / 12,71 / 11,40 / 18,24 / 51,84 | 37 / 25 / 14 / 14 / 10 | 6 / 13 / 11 / 18 / 52 | **62 / 19** | **38 / 81** |
| Não exclusivos | 725 | 21.388,03 h | 532,95 / 2.056,20 / 2.843,43 / 5.293,84 / 10.661,61 | 2,49 / 9,61 / 13,29 / 24,75 / 49,85 | 18 / 23 / 20 / 23 / 16 | 2 / 10 / 13 / 25 / 50 | **41 / 12** | **59 / 88** |

Frases dos cartões: Todos "Mais da metade dos pedidos, menos de um quinto do tempo." / "Menos da metade dos pedidos, mais de
quatro quintos do tempo."; Exclusivos "Mais da metade dos pedidos, cerca de um quinto do tempo." / "Menos da metade dos
pedidos, cerca de quatro quintos do tempo."; Não exclusivos "Menos da metade dos pedidos, pouco mais de um décimo do tempo." /
"Mais da metade dos pedidos, quase nove décimos do tempo." Faixa do pé: Todos e Exclusivos começam "Na maior parte das vezes
entregamos em até 2 dias. Mas os 44% / 38% que passam disso concentram 84% / 81% do tempo…"; Não exclusivos "Neste grupo, menos
da metade sai em até 2 dias. E os 59% que passam disso concentram 88% do tempo…". Ganchos "Mas esses 44% / 38% / 59% foram um
mês ruim, ou é sempre assim?". Em Exclusivos o % exato das horas em até 2 dias é 18,51; a soma das faixas pelo maior resto dá
19 (6 + 13), igual ao arredondamento direto. Nada fixo: tudo vem do recorte da carga.

### 0000.4 SQL para reproduzir (BigQuery, só SELECT) — CTEs `m`, `fer`, `ini`, `pronto`, `base`, `us` da SQL 0.6.1

```sql
p AS (SELECT b.*, IFNULL(us.us, 0) / 3.6e9 h FROM base b LEFT JOIN us USING (projeto_id)
      WHERE b.mes BETWEEN '2026-01' AND '2026-09'),                                   -- C7: meses completos (V1)
v AS (SELECT g, h FROM p, UNNEST(['Todos', IF(exclusivo, 'Exclusivos', IF(NOT exclusivo, 'Nao exclusivos', NULL))]) g
      WHERE g IS NOT NULL)
SELECT g, COUNT(*) n, ROUND(SUM(h), 2) h_total,                                       -- V1
  ROUND(SUM(IF(h <= 8, h, 0)), 2) h1, ROUND(SUM(IF(h > 8 AND h <= 16, h, 0)), 2) h2,  -- V3: horas por faixa
  ROUND(SUM(IF(h > 16 AND h <= 24, h, 0)), 2) h3, ROUND(SUM(IF(h > 24 AND h <= 40, h, 0)), 2) h4,
  ROUND(SUM(IF(h > 40, h, 0)), 2) h5,
  ROUND(100 * SUM(IF(h <= 16, h, 0)) / SUM(h), 2) pct_h_ate2                          -- HA antes do maior resto
FROM v GROUP BY g ORDER BY g DESC;
-- 25/10/2026 (carga 23/10 20:23:42 UTC), ~0,98 MB lidos — igual ao app:
-- Todos          2348 | 59752,15 | 2720,17 6864,64 7141,75 12170,35 30855,24 | 16,04
-- Nao exclusivos  725 | 21388,03 |  532,95 2056,20 2843,43  5293,84 10661,61 | 12,11
-- Exclusivos     1610 | 37694,16 | 2187,16 4791,33 4298,32  6876,51 19540,83 | 18,51
```

Passo a passo: (1) rodar a SQL; (2) % de cada faixa = h_faixa ÷ h_total × 100; inteiros pelo maior resto até somar 100;
(3) HA = faixas 1 + 2, HB = 100 − HA; (4) pedidos por faixa = SQL 000.4 (slide 3); (5) comparar com a tela (`#4`) em cada grupo.

### 0000.5 Validação e limites

- Testes: `tests/test_sla_tempo.py` (% de pedidos = slide 3, inclusive no caso do ajuste C8; A = página = slides 2 e 3;
  horas somam 100; linhas = total do cartão; `_fracao` em 23 casos; frases; variantes da faixa do pé, Prazo e gancho
  (A > 50, = 50, < 50, B = 1, B = 0); poucos dados / horas zeradas; HTML do slide 4, seletor → `#4`, 4 barras com texto,
  sem `style=""`; gancho do slide 3 → `#4`). Suíte: **220 testes**.
- Capturas conferidas: 1920 × 1000 (Todos, Exclusivos), 1440 × 900 (três grupos), 1280 × 800 (Todos, Não exclusivos): cabe
  sem rolar, faixa e gancho com folga até a navegação; 390 × 844 por emulação de dispositivo (Todos, Não exclusivos): cartões
  empilhados, largura do documento = 390, sem rolagem lateral (rola na vertical, como o slide 3).
- Limite: "horas com a equipe" = soma das horas de trabalho (C2), o tempo que os pedidos de cada faixa ficam com a equipe,
  não esforço medido por pessoa; poucos pedidos muito longos (pacotes, slide 2) pesam na faixa "mais de 5 dias".

## 000. D39 — slide 3 do estudo: "De cada 100 pedidos que chegam, em quanto tempo entregamos?" (25/10/2026)

Construído pela imagem de referência do Caio. URL: `/viu-agenciamento/sla/como-medimos#3` (`?talentos=` como no slide 2).
Código: `cem_pedidos()` / `_cem()` e regras **W1–W7** no fim de `sla/calculos.py`; `montar_estudo_sla` (chave `cem`);
`templates/como_medimos.html` (slide 3 e o gancho do slide 2 virou link para `#3`); `static/estilo.css` (bloco "slide 3");
testes `tests/test_sla_cem.py` (15). O estudo passa a ter 3 slides ("3 de 3", contagem automática do `apresentacao.js`).

### 000.1 Pergunta e textos da tela

- Rótulo "Exploração dos dados"; título "De cada 100 pedidos que chegam, em quanto tempo entregamos?".
- Linha do processo: "1 Chega o pedido do mercado — 2 O analista da área faz o orçamento — 3 A 1ª versão vai para o cliente".
- Seletor de talentos (Todos / Exclusivos / Não exclusivos, com o típico de cada um), igual ao do slide 2; os links levam a `#3`.
- Waffle 10 × 10 (1 quadrado = 1% de **todos** os orçamentos do recorte; sem nota sob o waffle, retirada a pedido do Caio); legenda com número grande + "em até 1 dia", "de 1 a 2 dias", "de 2 a 3 dias", "de 3 a 5 dias",
  "mais de 5 dias"; chaves "A em até 2 dias" (filete marinho, 2 primeiras faixas) e "B passam de 2 dias" (filete vermelho, 3 últimas).
- Painel "Curva acumulada — Quantos pedidos já saíram em cada prazo": % de orçamentos prontos × horas de trabalho, com
  três marcos tracejados (2 dias/16 h com o %; prazos dos 80% e 90% em dias e horas) e, no fim do eixo, "N% até T h";
  nota em uma linha (10 px, só em tela larga sem quebra) "1 dia de trabalho = 8 h do expediente (seg a sex, 10h–13h e 14h–19h)."
- Faixa do pé (redação do Caio): "Em uma amostra aleatória de 100 pedidos, **A ficam prontos em até 2 dias** de trabalho e
  **B levam mais de 2 dias**." (sem o prazo dos 90%). **Os 100 são a proporção do total do recorte, que é a composição
  esperada de uma amostra aleatória de 100** (não há sorteio no cálculo). Gancho: "E quanto do tempo esses B pedidos consomem? →".
- Acessibilidade: waffle `role="img"` com `aria-label` das 5 faixas e de A/B; curva `role="img"` com `aria-label` dos 3
  marcos e do teto; legenda com número + texto (nunca só cor); texto do SVG 14,5 unidades no celular (≈ 11,3 px reais em 390 px) e 12,5 em tela larga (≈ 14–15 px reais).
- Layout (2ª rodada do Caio): processo + conteúdo numa altura fixa (`.cem-meio`, 27,1em) para a faixa do pé e o gancho
  (`explora-gancho`) caírem no mesmo lugar do slide 2 (medido: faixa em y 648/604 e gancho em 707/663 em 1440 × 900 /
  1280 × 800, iguais ao slide 2); colunas waffle | legenda e chaves | curva ocupando a largura.

### 000.2 Regras (W1–W7, `sla/calculos.py`)

| Código | Regra |
|---|---|
| W1 | Universo = o do slide 2 (X1): entregues nos meses completos de 1ª entrega (C7), grupo de talentos (C10); h = horas da equipe sem almoço (C2). n < 30 → mensagem "Ainda não há orçamentos suficientes…" |
| W2 | Cinco faixas (C12): ≤ 8 h (h = 0 entra aqui), 8–16, 16–24, 24–40, > 40 h. Os 100 quadrados são a **proporção** do recorte, não um sorteio |
| W3 | Arredondamento coerente com a página e o slide 2: "até 1 dia" e "até 2 dias" (A) meio para cima (C8); "1 a 2 dias" = A − até 1 dia; as três de cima repartem B = 100 − A pelo maior resto (E8c), como `leituras()`. O maior resto puro das cinco faixas fica em `maior_resto`; `ajustado` = ele dava outro A. **Carga 23/10: o maior resto puro dá o mesmo nos três grupos (`ajustado` = falso)**; o teste cobre o caso em que ele daria 57 e a página 56 (vale 56) |
| W4 | Waffle preenchido linha a linha, da faixa mais rápida para a mais lenta |
| W5 | Curva acumulada (ECDF, h ≤ x) em 121 pontos de 0 até o teto = **P97 arredondado para cima ao múltiplo de 8 h** (mín. 24 h); acima do teto a curva não é desenhada e o fim do eixo diz "N% até T h" |
| W6 | Marcos: 16 h com o % = A (W3); prazos dos 80% e 90% = quantis lineares 0,8 e 0,9, em dias de 8 h arredondados a meio dia ("3 dias e meio", "5 dias"), horas inteiras embaixo. Rótulos que se encostariam formam um bloco centrado (`_afasta`); os % do eixo y ficam a ≥ 15 unidades |
| W7 | Faixa do pé e gancho (`_cem_textos`): singular em 1 ("fica pronto", "leva", "esse pedido consome"); 0 → "nenhum…"; B = 0 → "E quanto do tempo cada faixa consome?" |

### 000.3 Memória de cálculo (carga 23/10/2026 20:23:42 UTC, meses completos jan–set) — app = BigQuery

| Grupo | n | Contagens ≤8 / 8–16 / 16–24 / 24–40 / >40 h | % até 1 dia · até 2 dias (exato) | Waffle (5 faixas) | A / B | P80 | P90 | P97 → teto | % até o teto |
|---|---|---|---|---|---|---|---|---|---|
| Todos | 2.348 | 729 / 575 / 361 / 394 / 289 | 31,05 · 55,54 | 31 / 25 / 15 / 17 / 12 | **56 / 44** | 30,79 h → "4 dias · 31 h" | 46,32 h → "6 dias · 46 h" | 88,43 → 96 h | 97,23% ("97% até 96 h") |
| Exclusivos | 1.610 | 597 / 406 / 219 / 225 / 163 | 37,08 · 62,30 | 37 / 25 / 14 / 14 / 10 | **62 / 38** | 27,54 h → "3 dias e meio · 28 h" | 40,11 h → "5 dias · 40 h" | 84,72 → 88 h | 97,20% ("97% até 88 h") |
| Não exclusivos | 725 | 131 / 167 / 142 / 169 / 116 | 18,07 · 41,10 | 18 / 23 / 20 / 23 / 16 | **41 / 59** | 36,26 h → "4 dias e meio · 36 h" | 57,12 h → "7 dias · 57 h" | 105,26 → 112 h | 98,07% ("98% até 112 h") |

A = "% em até 2 dias" da página SLA e do slide 2 (56 / 62 / 41). Faixas do pé: "Em uma amostra aleatória de 100 pedidos, 56 ficam
prontos em até 2 dias de trabalho e 44 levam mais de 2 dias." (exclusivos 62/38; não exclusivos 41/59). Ganchos: "esses 44 / 38 / 59 pedidos". Nada fixo: tudo vem do recorte da carga.

### 000.4 SQL para reproduzir (BigQuery, só SELECT) — CTEs `m`, `fer`, `ini`, `pronto`, `base`, `us` da SQL 0.6.1

```sql
p AS (SELECT b.*, IFNULL(us.us, 0) / 3.6e9 h FROM base b LEFT JOIN us USING (projeto_id)
      WHERE b.mes BETWEEN '2026-01' AND '2026-09'),                                   -- C7: meses completos (W1)
v AS (SELECT g, h FROM p, UNNEST(['Todos', IF(exclusivo, 'Exclusivos', IF(NOT exclusivo, 'Nao exclusivos', NULL))]) g
      WHERE g IS NOT NULL),
w AS (SELECT *, PERCENTILE_CONT(h, 0.8) OVER (PARTITION BY g) p80, PERCENTILE_CONT(h, 0.9) OVER (PARTITION BY g) p90,
        PERCENTILE_CONT(h, 0.97) OVER (PARTITION BY g) p97 FROM v),
t AS (SELECT *, GREATEST(CEIL(p97 / 8) * 8, 24) teto FROM w)                          -- W5: teto do eixo
SELECT g, COUNT(*) n,
  COUNTIF(h <= 8) f1, COUNTIF(h > 8 AND h <= 16) f2, COUNTIF(h > 16 AND h <= 24) f3,   -- W2: cinco faixas
  COUNTIF(h > 24 AND h <= 40) f4, COUNTIF(h > 40) f5,
  ROUND(100 * COUNTIF(h <= 8) / COUNT(*), 2) pct_ate1, ROUND(100 * COUNTIF(h <= 16) / COUNT(*), 2) pct_ate2,  -- W3 (C8)
  ROUND(ANY_VALUE(p80), 2) p80, ROUND(ANY_VALUE(p90), 2) p90, ROUND(ANY_VALUE(p97), 2) p97,           -- W6, W5
  ANY_VALUE(teto) teto, ROUND(100 * COUNTIF(h <= teto) / COUNT(*), 2) pct_ate_teto
FROM t GROUP BY g ORDER BY g DESC;
-- 25/10/2026 (carga 23/10 20:23:42 UTC), ~1 MB lidos — igual ao app:
-- Todos          2348 | 729 575 361 394 289 | 31,05 55,54 | p80 30,79 p90 46,32 p97 88,43 | teto 96  | 97,23
-- Exclusivos     1610 | 597 406 219 225 163 | 37,08 62,30 | p80 27,54 p90 40,11 p97 84,72 | teto 88  | 97,20
-- Nao exclusivos  725 | 131 167 142 169 116 | 18,07 41,10 | p80 36,26 p90 57,12 p97 105,26 | teto 112 | 98,07
```

Passo a passo: (1) rodar a SQL; (2) A = arredondar `pct_ate2` meio para cima; até 1 dia = arredondar `pct_ate1`; 1 a 2
dias = A − até 1 dia; (3) repartir 100 − A entre f3, f4, f5 pelo maior resto (% de n); (4) P80/P90 ÷ 8, arredondados a
meio dia, e horas inteiras; (5) comparar com a tela (`#3`) em cada grupo.

### 000.5 Validação e limites

- Testes: `tests/test_sla_cem.py` (soma 100, maior resto × C8, A = página = slide 2, limites das faixas, `_dias_meio`,
  marcos 80/90 e teto, rótulos sem encostar, variantes de texto, poucos dados, HTML do slide 3, seletor → `#3`, gancho
  do slide 2 → `#3`, sem `style=""`). Suíte: **185 testes**.
- Capturas conferidas: 1440 × 900 e 1280 × 800 nos três grupos (cabe sem rolar: altura do slide = altura da área) e 390 px
  (empilha; largura do documento = 390, sem rolagem lateral; medido por emulação de dispositivo, não pela janela do Chrome headless, que tem largura mínima maior que 390).
- Limite: o waffle mostra proporção em inteiros (faixas < 0,5% somem); a curva para no P97 (o fim do eixo diz quanto falta).
  "Amostra aleatória de 100" é a redação do Caio (decisão de 25/10): leitura da proporção do total como a composição esperada
  de uma amostra de 100; o cálculo não sorteia (D38 tinha tirado "de cada 100" do slide 2).

## 00. D38 — meta de 2 dias e estudo em linguagem simples (25/10/2026, noite) — **prevalece sobre a seção 0**

Decisões do Caio aplicadas no código (`sla/calculos.py`, `sla/template.html`, `templates/como_medimos.html`,
`static/estilo.css`). Carga de referência: `_processado_em` = **23/10/2026 20:23:42 UTC** (mês parcial 2026-10; meses
completos jan–set). Números lidos pelo próprio app (`dados.sla.df()` → `calculos`) e conferidos com os números de
referência do coordenador (BigQuery, mesma carga): **todos batem**.

### 00.1 Regras novas e revistas

| Código | Regra |
|---|---|
| **D-SLA-7** (revisa a D-SLA-3) | **Meta sugerida = metade dos orçamentos (50%) prontos em até 2 dias de trabalho = 16 h** (equivale a "o típico em até 2 dias"). `LIMITE_DIAS = 2`, `META = 0.50`, `META_H = 16`. Ainda não oficial (pedido "Oficializar a meta do SLA" em `pendencias.py`) |
| C5 | Faixas: até 1 dia (≤ 8 h), 1 a 2 dias (8–16 h], acima de 2 dias (> 16 h). Saiu a faixa "2 a 3 dias" |
| C6 | Mensagem do típico pela **mediana exata** contra 16 h (`meta_tipico`): ≤ 16 h → "O típico já sai em até 2 dias"; > 16 h → "O típico [deste grupo] ainda passa de 2 dias (X h)". Entre 16 e 16,5 h o valor é escrito com 1 casa arredondada para cima (16,3 h); abr–jun/2026 tiveram 16,3–16,5 h e **não** contam como dentro da meta |
| C6b (sem meta) | **% acima de 5 dias de trabalho (> 40 h)** por grupo e meses completos: "N% passam de 5 dias de trabalho (M orçamentos) — são os casos a tratar" (`acima5`, `n_acima5`). Sem meta própria (sugestão na pendência: "no máximo X em 100") |
| C8 | Tela: "até 1 dia" e o total "até 2 dias" arredondados direto (meio para cima); "1 a 2 dias" = até 2 − até 1; "acima de 2 dias" = 100 − total |
| C11 / C12 / X8 | Leitura por regra, `_indicadores` e X8 passam a usar "até 2 dias" (`ate2`, `pct_2d`) |
| X3 | Faixa do topo do histograma: "na meta: até 2 dias (16 h)" (encolhe para "na meta: até 2 dias" / "na meta") |
| X5 | O tracejado do histograma é o **mesmo sino do meio** da reta do Q-Q (normal com a mediana e IQR / 1,349): "se fosse um sino em volta do típico". O KDE de Silverman saiu da tela (segue em `hist.kde`, `kde_banda`). Q-Q 340 × 88 (era 104). "↑ N orçamentos acima de T h" conta **orçamentos reais** acima do teto T (antes contava quantis de 200: sempre ~6) |
| X6 | **Limite estatístico (Tukey) = Q3 + 1,5 × IQR — não é a meta.** Zonas: rápidos (≤ Q1), comuns (Q1–Q3], **demorados** (Q3–limite: passam da meta, mas seguem o padrão do processo), **outliers** (> limite). Números das zonas em **% do total** do recorte ("25%"), rótulo "Dos N orçamentos entregues de jan a set". Marca da meta: tracejado fino com bolinha em cada ponta, **fora da caixa** (y 28–35 e 61–68), só se 16 h ≤ limite, com `<title>` "meta: 2 dias de trabalho (16 h)" e nota pequena "tracejado = meta de 2 dias de trabalho (16 h)" |
| E3 | Slide 1: "Trabalho da equipe" com "{d,d} dia(s) de trabalho · dentro/acima da meta de 2 dias (16 h)" (h ÷ 8, 1 casa; "dia" abaixo de 2; meta pelo valor exato); "Para o cliente receber" = "N dias corridos"; "Decisão do cliente" → "Espera do cliente". Gancho: típico do grupo ≤ 16 h → "No ano, o orçamento típico leva X: dentro da meta de 2 dias. Vamos ver o que demora."; > 16 h → "No ano, o típico deste grupo leva X, acima da meta de 2 dias. Vamos ver onde demora." |

**Terminologia na tela:** "limite estatístico" (nunca "limite do normal"); "outliers"/"casos fora da curva" para acima
do limite; "demorados" para Q3–limite. Saíram do estudo "esperado", "dentro do normal", "ainda normais" e "de cada 100"
(tudo em % do total; o gancho "E se olharmos para 100 pedidos, o que vemos?" fica, é a chamada do próximo slide).

### 00.2 Faixa do pé do slide 2 — um insight por passo (regras, sem LLM; textos finais do Caio)

Regra geral (Caio): **todo número da faixa aparece no gráfico do passo ao lado** (passo 1: % na meta na faixa do topo, típico e média nos rótulos; passo 2: rótulo no Q-Q; passo 3: faixas do topo e boxplot). Público: diretoria não analítica. Sem termos estatísticos ("mediana", "desvio", "Tukey", "percentil", "assimetria");
"típico" = mediana. Máximo 2 linhas (medido: 1–2 linhas em 1440 × 900 e 1280 × 800 nos três grupos).

| Passo | Função | Regra | Texto e variantes |
|---|---|---|---|
| 1 "Quanto tempo leva, de verdade?" | `_insight_p1(med, media, P, media_relevante)` | P = % ≤ 16 h; típico = mediana exata × 16 h (C6) | ≤ 16 h: "**P% dos orçamentos ficam prontos em até 2 dias de trabalho**, e o típico leva X: dentro da meta. A média, Y, parece pior porque poucos casos muito longos a puxam para cima; *por isso olhamos o típico*." · > 16 h: "Neste grupo, **o típico leva X, Z acima da meta de 2 dias**; só P% ficam prontos no prazo. A média, Y, ainda é puxada para cima por poucos casos muito longos; *por isso olhamos o típico*." · média perto do típico (X4/D12): "…A média, Y, fica perto dele: *aqui a média e o típico contam a mesma história*." |
| 2 "Dá para prever pela média?" | `_insight_p2(h, sino_meio, normal)` | P90 real (quantil linear) × P90 do sino do meio; os dois números ficam **visíveis no Q-Q**: anel discreto no ponto dos 10% mais lentos com o rótulo "10% mais lentos: R · sino: S" (`qq.p90`; some se o real passar do teto). Todos 46 · 34 h; Exclusivos 40 · 30 h; Não exclusivos 57 · 40 h | real > sino e não `normal`: "Os orçamentos comuns seguem um ritmo regular; **os demorados, não**: os 10% mais lentos levam R ou mais, quando um ritmo regular indicaria S. *Por isso a meta se apoia no típico, e os demorados são tratados à parte.*" · senão: "Os tempos seguem um ritmo regular, sem casos que fujam muito do padrão; *a média e o típico contam a mesma história*." |
| 3 "Faixas de tempo" (versão final) | `_frases(h, bx, n_fora, n_pac)` | Só números do gráfico do passo: R + C = rápidos + comuns (`bx.pcts[0] + [1]`, "até Q3"), D = demorados (`pcts[2]`), F = outliers (`pcts[3]`), Q3 e limite como escritos no boxplot; n_pac = cards "[Pacote". **Não diz que R + C estão na meta** (meta 16 h; Q3 passa dela). **Sem horas consumidas** (H fica no cálculo e aqui: 42/46/37%). Nota de rodapé (só no passo 3, 1 linha, `frases.nota`, linguagem simples): "Chamamos de padrão os tempos até L: é até onde vai a grande maioria dos orçamentos, com uma margem de folga. Acima disso, o tempo foge do ritmo da equipe." A regra técnica (L = Q3 + 1,5 × IQR, Tukey) fica nesta ficha e no aria-label do boxplot | "**R+C% dos orçamentos saem em até Q3**: os rápidos e os comuns. Outros D% demoram mais, até L, mas seguem o padrão do processo. *F% (n orçamentos, k deles pacotes) são outliers, fora da curva: vamos olhar caso a caso.*" Todos: 75% até 28 h · 18% até 59 h · 7% (171, 53 pacotes); Exclusivos: 75% até 24 h · 18% até 52 h · 7% (111, 36); Não exclusivos: 75% até 32 h · 16% até 64 h · 9% (63, 15) · sem demorados: a frase do meio some · sem outliers: "…seguem o padrão do processo; *neste recorte, ninguém fica fora da curva.*" · singular e "menos de 1%" |

O fecho do painel do passo 1 ("Por isso usamos a mediana…") saiu do painel (cortava ~49 px no limite de altura) e
virou o insight do passo 1.

### 00.3 Memória de cálculo (carga 23/10, meses completos jan–set)

| Grupo | n | Típico (mediana) | ≤ 16 h | Faixas 1 / 2 / acima | > 40 h (n) | Q1 · Q3 · limite | Outliers (n · %) | Horas nos outliers | Pacotes entre os outliers | 10% mais lentos: real · sino |
|---|---|---|---|---|---|---|---|---|---|---|
| Todos | 2.348 | 14,26 h → "14 h" (na meta) | 55,54% → 56 | 31 / 25 / 44 | 12% (289) | 6,5 · 27,6 · 59,1 h | 171 · 7% | 42% | 53 | 46 h · 34 h |
| Exclusivos | 1.610 | 11,83 h → "12 h" (na meta) | 62,30% → 62 | 37 / 25 / 38 | 10% (163) | 5 · 24 · 51,7 h | 111 · 7% | 46% | 36 | 40 h · 30 h |
| Não exclusivos | 725 | 19,64 h → "20 h", 4 h acima | 41,10% → 41 | 18 / 23 / 59 | 16% (116) | 11 · 32 · 64,0 h | 63 · 9% | 37% | 15 | 57 h · 40 h |

Zonas do boxplot (rápidos / comuns / demorados / outliers): Todos 25/50/18/7; Exclusivos 25/50/18/7; Não exclusivos
25/50/16/9. Média: 25 h / 23 h / 30 h. Q-Q "↑ acima do teto": Todos 69 acima de 93 h; Exclusivos 45 acima de 90 h; Não
exclusivos 23 acima de 103 h.

**% em até 16 h por mês (Todos):** jan 60 · fev 55 · mar 58 · abr 50 · mai 49 · jun 49 · jul 57 · ago 59 · set 59 ·
out 51 (parcial, até 22/10). Medianas: 13,2 · 15,7 · 14,9 · **16,3 · 16,3 · 16,5** · 12,9 · 12,6 · 13,6 h (abr–jun
acima de 16 h pelo valor exato). Exclusivos: 64 · 53 · 61 · 60 · 56 · 54 · 66 · 71 · 61 (out 65). Não exclusivos:
56 · 57 · 52 · 25 · 30 · 40 · 43 · 25 · 53 (out 23). Leitura C11 (fora da tela): "Melhor mês: jan (60%). Pior: jun
(49%). Set fechou em 59%, acima do ano (56%)."

**Sensibilidade do limite (Todos, fora da tela):** Tukey linear 59,1 h (7,3%); boxplot ajustado de Hubert-Vandervieren
(medcouple 0,291; Q3 + 1,5·e^(3·MC)·IQR) **103 h, 2,6%**; Tukey em log (sem os 42 de 0 h) **222 h, 1,2%** (a referência
do coordenador citava 239 h / 1,2%: diferença de método no log; o % é o mesmo). A tela segue com Tukey linear.

### 00.4 SQL para reconferir (BigQuery, só SELECT) — sobre a CTE de horas sem almoço por projeto da SQL 0.6

```sql
-- horas = uma linha por projeto entregue nos meses completos de 1ª entrega (jan..set/2026), com h (horas da equipe
-- sem almoço, C2) e exclusivo (C10), como na SQL 0.6.2
SELECT grupo,
       COUNT(*) AS n,
       ROUND(100 * COUNTIF(h <= 16) / COUNT(*), 2) AS pct_ate_16h,   -- D-SLA-7: 55,54 / 62,30 / 41,10
       ROUND(100 * COUNTIF(h > 40) / COUNT(*), 2)  AS pct_acima_40h   -- C6b: 12,31 / 10,12 / 16,00
FROM horas, UNNEST(['Todos', IF(exclusivo, 'Exclusivos', 'Não exclusivos')]) AS grupo
WHERE exclusivo IS NOT NULL OR grupo = 'Todos'
GROUP BY grupo;
```

### 00.5 Página SLA (tela)

Título do gráfico "Orçamentos prontos em até 2 dias de trabalho, por mês"; pilha "até 1 dia" (escura) + "1 a 2 dias"
(média), total "até 2 dias" no topo; trilho vazio = acima de 2 dias; linha pontilhada em 50% com o rótulo **"meta
sugerida: 2 dias úteis"** (texto pedido pelo Caio; a linha fica em 50%). Legenda: até 1 dia · 1 a 2 dias · acima de 2
dias · mediana do mês. Sob a legenda: ✓/↑ mensagem do típico (C6) e relógio "N% passam de 5 dias de trabalho (M
orçamentos) — são os casos a tratar" (C6b). Números dentro das faixas em tamanho único menor (0,8em, peso 500), que
encolhem pela altura real da faixa (container query) até 8 px e somem abaixo disso (valor no leitor de tela e no
`title` do mês); "PARCIAL" na barra vazada encolhe com a altura até 7 px, vira "parc." e, se nem assim couber, sai
para cima da barra.

### 00.6 Varredura "nada chapado" (número exibido → origem)

Página SLA: medianas dos botões (`grupos[].mediana_h_trabalho`, meses completos por grupo) · "Levamos X h"
(`mediana_h_trabalho`) · dias úteis (`mediana_dias_uteis`) · legenda (`ano.tela`) · típico e > 5 dias (`tipico`,
`acima5`, `n_acima5`) · barras e totais por mês (`meses[].tela`) · mediana do mês (`meses[].mediana`) · 50% e "2 dias"
são a meta (constante de regra, não dado). Slide 1: etapas, datas e horas do exemplo do dia (`exemplo`), dias de
trabalho e meta (`dias_trabalho`, `na_meta`), dias corridos e espera (`dias_cliente`, `dias_decisao`), gancho
(`exploracao.tipico`). Slide 2: medianas dos botões (`comparacao[].mediana`), barras do histograma (`hist.barras[].n`),
faixas do topo (`faixas3`, `box.pcts`), máximo (`max_txt`), mediana e média (`mediana_txt`, `media_txt`), assimetria
(`assim.txt`; 0 e 1 da régua são referências fixas), Q-Q (`qq`: escalas pelo grupo; "↑ N orçamentos acima de T h" =
`(h > teto).sum()`, **corrigido**; "% previstos abaixo de 0 h" = parcela dos 200 quantis do sino do meio abaixo de 0,
propriedade do sino do grupo), boxplot (`box.pcts`, `q1`/`q3`/`limite`, `n_fora`, `n`, `periodo`), insights (00.2). A
nuvem de 9 pontos depois da trava é ilustração (não mostra número); o eixo do histograma vai até "60 h ou mais" em todos
os grupos (escala fixa para comparar; a última barra conta os casos reais acima de 60 h).

## 0. Versão vigente — revisão de 25/10/2026 (D-SLA-1 a D-SLA-6 e itens aprovados da auditoria)

> **A D38 (seção 00) revisa esta seção:** meta = metade em até 2 dias (16 h), não 75% em até 3 dias; faixas sem "2 a 3 dias"; o limite de Tukey passa a se chamar "limite estatístico".

**Esta seção prevalece** sobre as seções 2, 3, 5 e 6 onde houver conflito: lá ficam os números e textos de 24/10
(regras anteriores: mês de entrada, Retorno Marca contando, meta em 2 dias, cerca de Tukey linear), mantidos como
registro. Carga de referência: `_processado_em` = **23/10/2026 20:23:42 UTC** (mês parcial 2026-10; dados até 22/10).
Conferido no BigQuery em **25/10/2026** (conta `caio.barroso@viu.com.br`, projeto `gglobo-viu-dados-hdg-prd`, só
SELECT) com as SQL 0.6: **todos os números da tela batem com o banco**.

### 0.1 Decisões aplicadas

| ID | Decisão (25/10/2026) | Onde |
|---|---|---|
| D-SLA-1 | Mês de referência = **mês da 1ª entrega** (entrada do 1º passo `cliente`), no gráfico, nos números do ano e no universo do estudo. O mês fecha no dia 1º seguinte (como o Atendimento, mês do evento); o mês parcial deixa de ser otimista | C4, C7, X1 |
| D-SLA-2 | Horas da equipe **sem "Em elaboração - Retorno Marca/Executivo"** (espera da marca; status em minúsculas começando por "em elaboração - retorno marca"). Fila, Cotação Externa, Cotação Gestão de Elenco e validações continuam. Exemplo do estudo: quem passou pelo Retorno Marca não é candidato (caminho não limpo) | C2, C14, E1 |
| D-SLA-3 | **Meta sugerida = 75% prontos em até 3 dias de trabalho (24 h)**; faixa nova "2 a 3 dias" (16–24 h); trilho vazio = "acima de 3 dias"; título "Orçamentos prontos em até 3 dias de trabalho, por mês". Continua sugerida (pendência de oficializar, "O que falta") | C5, C6, C8 |
| D-SLA-4 | **Fora da tela desde 25/10/2026 (noite), a pedido do Caio** ("só confunde, polui"); segue calculada em `cobertura()` e documentada aqui. Texto antigo (slide 1, sob as caixas): "Medido em N de M orçamentos entregues no período (X%); os demais não têm o histórico de status completo." N = medidos (C7); M = gold de fluxo, evento `entregue`, mês do evento jan até o mês anterior ao parcial, safras do ano, família "Nenhuma" (sem as famílias fora da regra). Some se as cargas forem de dias diferentes ou se N > M | `cobertura()` |
| D-SLA-5 | Pendências para a gold: PD21 em `pendencias.py`, `docs/lembretes_gold.md` e `docs/prompt_dados_pendentes.md` | — |
| D-SLA-6 | Rejeitadas: tirar a fila; tirar as Cotações; tirar pacotes/lotes da base (ficam, só identificados); incluir encerrados sem entrega no denominador (é outra pergunta: taxa de entrega) | — |
| A1 | Todas as análises usam só os **meses completos de entrega** (jan até o mês anterior ao da carga) | C7 |
| A2 | Mês vigente no gráfico: barra **vazada** (contorno), "parcial" e "até dd/mm" (o dia do rodapé); % e nº de entregas só no leitor de tela e na dica (`title`); com menos de 30 entregas, só o trilho ("aguardando entregas") | `MIN_PARCIAL` |
| A3 | **Mediana do mês** numa linha discreta sob o nome do mês ("14 h"), cinza; rótulo "mediana" na calha à esquerda; mês parcial em itálico (ou "—" se < 30) | `meses[].mediana` |
| A4 | Exemplo do dia: entregue no **mês vigente de entrega**, escolhido pelo hash de (data + grupo + projeto_id), data de São Paulo; "em aberto" até o fim do dia de corte do rodapé ("até 22/10") | E1–E3 |

Itens da auditoria aplicados: SLA-D01 (minutos das etapas pelo maior resto: as etapas somam o total escrito),
SLA-R13 (azul médio ≥ 4,8:1 com o rótulo branco; contorno da amostra do trilho 3,3:1), SLA-R08 (moldura do estudo nas
mesmas coordenadas do SLA), SLA-R09 (texto dos SVG ≥ 11 px reais em 1280–1800), SLA-R06 (lupa sem cobrir o título no
celular), SLA-R04 ("meta sugerida 75%"; leitor de tela: "meta sugerida, ainda não oficial"), SLA-D07 (nota "só no
expediente (sem noites, fins de semana e feriados)"), SLA-D05 (dia do exemplo no fuso de São Paulo), SLA-D09 (conta
do limite que fecha), SLA-D12 (frases condicionadas ao dado), SLA-R11 ("Recomeçar"), SLA-R14 (linha do grupo
reservada em "Todos"), SLA-R18 (número da barra fora da linha da média/mediana), SLA-D08 (fim do exemplo no dia de
corte), SLA-D10/D11/D13 (estudo sem variação devolve `None`; arredondamentos meio para cima; 16 literal virou a
constante), SLA-R16 ("SLA de entrega em 2025", "Oficializar a meta do SLA").

### 0.2 Textos da tela

**Página** (`sla/template.html`): título do cartão "Orçamentos prontos em até 3 dias de trabalho, por mês"; legenda
"até 1 dia A%", "1 a 2 dias B%", "2 a 3 dias C%", "acima de 3 dias D%"; linha "meta sugerida 75%"; leitor de tela da
figura "Linha tracejada: meta sugerida, ainda não oficial, de 75% prontos em até 3 dias de trabalho. Sob cada mês, a
mediana de horas de trabalho da equipe."; por mês "set: 74% prontos em até 3 dias (31% até 1 dia, 28% de 1 a 2 dias,
15% de 2 a 3 dias), de 340 orçamentos; mediana 14 h de trabalho."; mês vigente "out, mês em andamento (dados até
22/10): 67% prontos em até 3 dias, de 242 entregas; mediana 16 h. Ainda vai mudar." (ou "aguardando entregas…, sem
percentual."); sob os meses "parcial", "até 22/10" e a mediana; à esquerda "mediana" (no celular: "mediana de horas do
mês: o número cinza sob cada mês"). Resposta: "Levamos X h de trabalho da equipe [nos talentos …] para entregar um
orçamento ao cliente." (linha do grupo reservada, invisível, em "Todos") e "Y dias no calendário para o cliente
receber".

**Estudo, slide 1:** caixa "Entra no cálculo" + "**Cotações** (externa e de elenco)"; caixa "Fica fora": "Standby";
"Ajustes depois da 1ª versão"; "Espera da marca (Retorno Marca/Executivo)"; "Espera do cliente (Aguardando
Feedback)"; "Noites, fins de semana e feriados"; nota "Expediente: seg a sex, 10h–13h e 14h–19h."; cobertura (D-SLA-4);
faixa: "Trabalho da equipe … só no expediente (sem noites, fins de semana e feriados)".

**Estudo, slide 2** (frases condicionadas, `exploracao()`):

| Passo | Título | Texto | Faixa do pé |
|---|---|---|---|
| 1 Formato · Assimetria | "Assimetria positiva: cauda à direita" (razão > 1,2) · "Quase simétrica" (0,83–1,2) · "Assimetria negativa: cauda à esquerda" (< 0,83) | "Na metade do meio, o lado lento é **1,7× mais largo** que o rápido: do típico até o 1º quarto mais rápido são 8 h; até o último quarto, 13 h." + barra Q1–mediana–Q3 em escala ("8 h" \| "13 h"; "7 h · 14 h · 28 h"; "1º quarto · típico · último quarto") e "1,7×" grande; fecho "Por isso usamos a mediana (14 h): metade sai até aí. A média (25 h) é puxada pelos casos longos; 73% ficam abaixo dela." (sem média relevante: "A média (X h) fica perto dela.") | "O orçamento típico leva **14 h de trabalho**, e não 25 h." ("e não" só se a média passa a mediana em ≥ 10% e ≥ 2 h) |
| 2 Normalidade · Q-Q (25/10, tarde) | Sobre: "Normalidade · gráfico Q-Q, previsto × real". "Os tempos seguem o sino? Não. Seguem a log-normal, menos no extremo." ("Sim." se r_normal ≥ 0,95; "Seguem a log-normal" só se r_log ≥ 0,95; ", menos no extremo" só se há fora da curva) | O que mostra: "Cada ponto é um orçamento: na horizontal, o tempo que a curva previa; na vertical, o tempo real. **Na linha, a curva acertou.**" Dois Q-Q com nome em cima ("Contra o sino", "Contra a log-normal*"), eixos em horas reais com nome ("tempo real ↑", "previsto pela curva →"; log-normal com 1 h, 8 h, 40 h, 200 h) e rótulos diretos: no sino, faixa rosada "abaixo de 0 h: impossível (32 em 100)" e "longe da linha: o sino errou"; na log-normal, "na linha: a curva acertou" e, em vermelho, "acima da linha: demorou mais" junto dos pontos acima de 210 h. Selo "Encaixe na linha: sino 0,58 · log-normal 0,99 (1 = perfeito)", "● fora da curva (acima de 210 h)", "* log-normal = sino na escala que multiplica". Leitor de tela: os dois gráficos descritos com os números | Para nós: "**A cauda longa é natural do processo,** não erro de medição: os tempos seguem a log-normal. Por isso o típico é a mediana, 14 h, e não a média, 25 h." (normal: "É quase um sino: …"; nem normal nem log-normal: a frase de antes, "Se fosse um sino… Por isso usamos a mediana.") |
| 3 Faixas · boxplot (25/10, tarde) | "O que é demorado e o que é fora da curva?" | "De cada 100 orçamentos · o limite de 210 h é estatístico, não a meta". Boxplot horizontal na escala log com a quantidade (Playfair) e o nome sobre cada zona — 25 rápidos, 50 comuns, 24 demorados, 1 fora da curva —, fio do rótulo empurrado até a zona, hastes como faixas na cor da zona, limites "0 h · 7 h · 28 h · 210 h", linha tracejada em 40 h com "5 dias de trabalho (40 h)" / "12 em 100 passam daqui". "**Como ler:** a caixa reúne metade dos orçamentos (7 h a 28 h); as hastes, até onde o tempo ainda é esperado; os pontos, acima de 210 h, são casos à parte." **X8:** "**E se tirarmos os 28 fora da curva?** A mediana quase não muda." (ou "A mediana muda ±X h." se andar mais de 1 h) e a grade com todos → sem eles: Mediana 14 h → 14 h · Em até 3 dias 71% → 72% · Média 25 h → 20 h · 9 em 10 até 46 h → 43 h (leitor de tela: também sem os 73 cards de pacote — 14 h, 19 h, 73%, 40 h; e a conta do limite) | "De cada 100 orçamentos, **12 passam de 5 dias de trabalho** — são lentos, mas fazem parte do processo de hoje: reduzi-los pede mudar o processo. **Só 1 é caso à parte**, quase sempre card de pacote (27 dos 28)." |

Histograma: faixas do alto nos passos 1–2 "71% até 3 dias", "17% 3 a 5 dias", "12% mais de 5 dias" (X3 agora com o
limite da meta, 24 h); no passo 3 as zonas "25% rápidos", "50% comuns", "24% demorados", "1%"; a barra "60 h ou mais"
divide-se em demorados (embaixo) e fora da curva (em cima, 28). Botão do último passo: "Recomeçar". A comparação dos
grupos (X7) continua fora da tela.

### 0.3 Memória de cálculo (carga de 23/10/2026; app = BigQuery)

**Resposta, seletor e faixas do ano (meses completos de entrega, jan–set):**

| Grupo | n | Mediana horas | Tela | Mediana calendário | Tela | ≤ 8 / ≤ 16 / ≤ 24 h (%) | Legenda (C8) |
|---|---:|---:|---:|---:|---:|---|---|
| Todos | **2.348** | 14,2613 | **14 h** | 2,7960 dias | **2,8** | 31,05 / 55,54 / 70,91 | 31 · 25 · 15 · 29 (71% até 3 dias) |
| Exclusivos | **1.610** | 11,8302 | **12 h** | 2,0200 dias | **2,0** | 37,08 / 62,30 / 75,90 | 37 · 25 · 14 · 24 (76%) |
| Não exclusivos | **725** | 19,6420 | **20 h** | 3,9590 dias | **4,0** | 18,07 / 41,10 / 60,69 | 18 · 23 · 20 · 39 (61%) |

1.610 + 725 + 13 sem talento = 2.348. C8: "1 a 2 dias" = arred(≤ 16) − arred(≤ 8); "2 a 3 dias" = arred(≤ 24) −
arred(≤ 16); "acima de 3 dias" = 100 − arred(≤ 24). Ex. Todos: 31 / 56 / 71 → 31 · 25 · 15 · 29.

**Antes → depois (tela, Todos · Exclusivos · Não exclusivos):** mediana 15 → **14** h · 13 → **12** h · 21 → **20** h;
dias 2,9 → **2,8** · 2,0 → **2,0** · 4,1 → **4,0**; n 2.425 → **2.348** · 1.635 → **1.610** · 775 → **725**; legenda
"29/24/47 (até 2 dias 53%)" → **"31/25/15/29 (até 3 dias 71%)"** · 35/25/40 → **37/25/14/24** · 16/22/62 →
**18/23/20/39**. A queda vem de D-SLA-2 (Retorno Marca, −0,6 h) e de D-SLA-1 (o universo passa a ser por mês de
entrega: 2.348 entregues jan–set).

**Por mês, Todos (n · ≤ 8 h · ≤ 16 h · ≤ 24 h em % exato · mediana → tela):**

| Mês | n | ≤ 8 | ≤ 16 | ≤ 24 | Barra (C8) | Mediana | Tela |
|---|---:|---:|---:|---:|---|---:|---:|
| jan | 111 | 37,84 | 60,36 | 74,77 | 38 · 22 · 15 → **75%** | 13,16 | 13 h |
| fev | 108 | 25,00 | 54,63 | 72,22 | 25 · 30 · 17 → **72%** | 15,71 | 16 h |
| mar | 159 | 21,38 | 58,49 | 70,44 | 21 · 37 · 12 → **70%** | 14,89 | 15 h |
| abr | 215 | 27,91 | 49,77 | 64,65 | 28 · 22 · 15 → **65%** | 16,34 | 16 h |
| mai | 201 | 29,85 | 49,25 | 64,68 | 30 · 19 · 16 → **65%** | 16,32 | 16 h |
| jun | 288 | 30,56 | 48,96 | 68,06 | 31 · 18 · 19 → **68%** | 16,46 | 16 h |
| jul | 548 | 33,21 | 57,30 | 71,53 | 33 · 24 · 15 → **72%** | 12,92 | 13 h |
| ago | 378 | 34,92 | 59,26 | 74,87 | 35 · 24 · 16 → **75%** | 12,60 | 13 h |
| set | 340 | 30,59 | 58,82 | 74,12 | 31 · 28 · 15 → **74%** | 13,56 | 14 h |
| out (parcial, vazado) | 242 | 30,99 | 50,83 | 66,53 | só contorno até **67%** | 15,75 | *16 h* |

Exclusivos (n · ≤ 24 h % · mediana): jan 75 · 76,00 · 11,92; fev 55 · 70,91 · 15,36; mar 125 · 71,20 · 13,91; abr 153 ·
72,55 · 13,67; mai 151 · 68,87 · 11,97; jun 192 · 71,88 · 14,58; jul 344 · 75,58 · 10,07; ago 277 · 87,36 · 10,00; set
238 · 76,47 · 11,74; out (parcial) 159 · 81,13 · 10,63. Não exclusivos: jan 32 · 78,13 · 14,26; fev 53 · 73,58 · 16,00;
mar 33 · 69,70 · 15,20; abr 60 · 46,67 · 26,08; mai 50 · 52,00 · 23,72; jun 96 · 60,42 · 18,80; jul 200 · 65,50 ·
18,12; ago 100 · 40,00 · 27,96; set 101 · 69,31 · 15,93; out (parcial) 80 · 37,50 · 33,14. ≤ 8 e ≤ 16 h por mês e grupo:
saída da SQL 0.6.1 (arquivo de conferência abaixo).

**Meta sugerida (75% em até 3 dias):** jan e ago chegam (75%); set 74%; ano 71%. Exclusivos chegam em jan, jul, ago e
set; não exclusivos só em jan (32 pedidos).

**Leitura por regra (C11, não exibida):** "Melhor mês: ago (75%). Pior: abr (65%). Set fechou em 74%, acima do ano (71%)."

**Cobertura (D-SLA-4):** N = 2.348 medidos; M = 3.553 entregues na gold de fluxo (família "Nenhuma", safras 2026, evento
jan–set) → **66%** ("Medido em 2.348 de 3.553 orçamentos entregues no período (66%)…"). Viés pequeno e conservador:
os não medidos são um pouco mais rápidos (validação de 25/10, `q1b_cobertura_mes`).

**Exemplo do dia (25/10/2026, Todos):** [Bradesco] Vinicius Nascimento | Criança Esperança — Entrada 1h09 (05/10 ·
16:55), Elaboração 8 min, Revisão 11h48 → **13h05**; para o cliente receber **2 dias** (de 05/10 a 07/10); decisão do
cliente **15 dias**, "até 22/10 · em aberto". Os minutos das etapas fecham no total (SLA-D01). Muda a cada dia (hash).

**Estudo, slide 2 (X1–X7):**

| Medida | Todos | Exclusivos | Não exclusivos |
|---|---:|---:|---:|
| n | 2.348 | 1.610 | 725 |
| Mediana · média | 14,26 → **14 h** · 25,45 → **25 h** | 11,83 → **12 h** · 23,41 → **23 h** | 19,64 → **20 h** · 29,50 → **30 h** |
| Desvio-padrão amostral | 53,436 | 55,620 | 48,254 |
| Q1 · Q3 (lineares) | 6,541 → 7 h · 27,576 → 28 h | 5,165 → 5 h · 23,791 → 24 h | 10,654 → 11 h · 32,000 → 32 h |
| Metades (mediana − Q1 · Q3 − mediana) | 7,72 → 8 h · 13,31 → 13 h | 6,67 → 7 h · 11,96 → 12 h | 8,99 → 9 h · 12,36 → 12 h |
| **Razão das metades (X4)** | 1,725 → **1,7×** | 1,794 → **1,8×** | 1,375 → **1,4×** |
| Fisher-Pearson (só ficha) | 7,158 | 7,160 | 7,278 |
| Abaixo da média | 73,21% → **73** | 74,53% → **75** | 69,52% → **70** |
| Aderência r (sino · log-normal) | **0,58 · 0,99** (0,5764 · 0,9882) | 0,55 · 0,99 (0,5529 · 0,9897) | 0,66 · 0,98 (0,6554 · 0,9783) |
| Tempo negativo pelo sino 100 × Φ(−média ÷ desvio) | 31,7 → **32** | 33,7 → **34** | 27,1 → **27** |
| Q1ₗ · Q3ₗ de ln(h + 1) | 2,0204 · 3,3526 | 1,8188 · 3,2105 | 2,4556 · 3,4965 |
| **Limite (X6) = exp(Q3ₗ + 1,5 × (Q3ₗ − Q1ₗ)) − 1** | 209,787 → **210 h** | 198,931 → **199 h** | 156,244 → **156 h** |
| Zonas (contagem) | 587 / 1.174 / 559 / 28 | 403 / 804 / 382 / 21 | 182 / 363 / 171 / 9 |
| Zonas na tela (maior resto) | **25 / 50 / 24 / 1** | **25 / 50 / 24 / 1** | **25 / 50 / 24 / 1** |
| Fora da curva que são "[Pacote" | **27 de 28** | 21 de 21 | 8 de 9 |
| > 40 h (5 dias) | 12,31% → **12** | 10,12% → **10** | 16,00% → **16** |
| X3 ≤ 24 / 24–40 / > 40 h (tela) | 71 / 17 / 12 | 76 / 14 / 10 | 61 / 23 / 16 |
| Máximo | 515 h | 483 h | 515 h |

X7 (fora da tela): régua de Todos (209,79 h) e régua própria dão 1% nos três grupos (arredondamento `_pcts`, como as
zonas). **Resposta à diretoria (B4):** "Os dois grupos têm o mesmo formato. Os não exclusivos levam mais tempo no geral
— por isso 16 em 100 passam de 5 dias, contra 10 nos exclusivos. Os casos extremos são raros nos dois (1 em 100) e
quase todos são cards de pacote (21 de 21 nos exclusivos; 8 de 9 nos não exclusivos)."

### 0.4 Regras novas e mudadas (código: docstring e blocos E/X de `sla/calculos.py`)

| ID | Regra vigente |
|---|---|
| C2 | Horas úteis sem almoço dos passos `equipe` antes de C1, inclusive Entrada, **exceto "Em elaboração - Retorno Marca/Executivo"** (D-SLA-2). Cotações e validações contam |
| C4 | Só entregues; **mês = mês da `entrada` do passo C1** (D-SLA-1); `mes_entrada` guardado à parte |
| C5 | ≤ 8 h, 8–16 h, **16–24 h**, > 24 h |
| C6 | Meta sugerida 75% em até **3 dias (24 h)** |
| C7 | Meses completos de entrega (A1); o parcial só no gráfico, vazado (A2) |
| C8 | ≤ 8, ≤ 16 e ≤ 24 arredondados direto; faixas do meio = diferenças; acima = 100 − ≤ 24 |
| A2/A3 | Mês parcial vazado com "até dd/mm"; < 30 entregas (`MIN_PARCIAL`) = "aguardando entregas"; mediana do mês sob o nome |
| E1 | Entregue no mês vigente de entrega até o dia de corte; ordem pelo SHA-256 de "data:grupo:projeto_id" (data de São Paulo, `_hoje()`); caminho limpo sem Retorno Marca |
| E2 | Fim "em aberto" = 22/10 23:59:59 (véspera da carga em SP, `sla.data_corte`); minutos das etapas pelo maior resto com alvo = total arredondado |
| E3 | Dias meio para cima (`floor(x + 0,5)`) |
| X1 | Universo = meses completos de entrega (A1) |
| X3 | ≤ 24 h (meta), 24–40 h, > 40 h |
| X4 | Razão das metades da caixa (1 casa), títulos por faixa da razão; Fisher-Pearson só na ficha |
| X5 | Dois Q-Q (sino em horas; log-normal em ln(h + 1) com eixos em horas); aderência ("encaixe" na tela) = correlação de Pearson dos 160 pontos; normal se r ≥ 0,95; % abaixo de 0 h = 100 × Φ(−média ÷ desvio). Quadros 160 × 118 com nomes dos eixos e rótulos diretos; quantis acima do limite X6 em vermelho |
| X6 | Limite em log (acima); zonas pelos quartis em horas; pacotes = nome começa por "[Pacote"; marca em 40 h com o % acima; conta escrita com 3 casas nos termos em log (com 2 casas o exp mudaria o limite em ~1 h) |
| X7 | `pct_regua_todos` e `pct_propria` com `_pcts` (como as zonas); mais `pct_5dias`, `fora`, `pacotes_fora`, `razao` |
| X8 | **Influência dos fora da curva** (pergunta da gerente, 25/10/2026): no universo X1 do grupo, mediana, média, % em até 3 dias (≤ 24 h, meio para cima) e P90 (quantil linear) com todos, sem os fora da curva (> limite X6) e, como sensibilidade, sem os cards de pacote. "A mediana quase não muda" só se ela anda até 1 h; senão a tela diz quanto. Só descreve: nada sai da base do SLA (D-SLA-6) |
| D10 | `exploracao()` devolve `None` com desvio 0 ou limite ≤ 0 |

### 0.5 Validação

| Data | O quê | Resultado |
|---|---|---|
| 25/10/2026 | SQL 0.6.1 (regras novas) × `entrega()`/`exploracao()` sobre a mesma carga, três grupos, ano e mês a mês | ✅ **idênticos**: n, medianas, dias, ≤ 8/16/24, medianas por mês, média, desvio, Q1/Q3, razão, Q1ₗ/Q3ₗ, limite, zonas, pacotes fora, > 40 h, abaixo da média, máximo |
| 25/10/2026 | SQL 0.6.2 (160 quantis do banco) → r do Q-Q contra a normal e Φ | ✅ r = 0,5764 (app 0,5764); Φ(−25,448 ÷ 53,436) = 31,7% → 32 |
| 25/10/2026 | SQL 0.6.3 (M da cobertura) | ✅ 3.553 (app 3.553; N 2.348) |
| 25/10/2026 | Testes | ✅ suíte inteira passando (17 novos em `tests/test_sla_20261025.py`) |
| 25/10/2026 | Capturas 1280×720, 1440×900, 1800×980 e 390×844 (SLA nos três grupos; estudo slide 1 e slide 2 nos passos 1–3) | ✅ logo, título e rodapé do estudo nas mesmas coordenadas do SLA (±1 px em 1800); menor texto de SVG 11,3 px (1280) a 15,1 px (1800); sem rolagem lateral em 390 |

### 0.6 SQL para reproduzir (BigQuery, só SELECT)

**0.6.1 Todos os números da página e do slide 2, por grupo, ano e mês** (feriados de 2025 e 2026; trocar `'2026-09'`
pelo último mês completo):

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
-- 25/10/2026 (carga 23/10 20:23:42 UTC), linhas ANO:
-- Todos          | 2348 | 14,261 | 2,796 | 31,05 | 55,54 | 70,91 | 25,448 | 53,436 | 6,541 | 27,576 | 1,725 | 2,0204 | 3,3526 | 209,787 | 587 | 1174 | 559 | 28 | 27 | 12,31 | 73,21 | 515
-- Exclusivos     | 1610 | 11,830 | 2,020 | 37,08 | 62,30 | 75,90 | 23,413 | 55,620 | 5,165 | 23,791 | 1,794 | 1,8188 | 3,2105 | 198,931 | 403 |  804 | 382 | 21 | 21 | 10,12 | 74,53 | 483
-- Nao exclusivos |  725 | 19,642 | 3,959 | 18,07 | 41,10 | 60,69 | 29,501 | 48,254 | 10,654 | 32,000 | 1,375 | 2,4556 | 3,4965 | 156,244 | 182 | 363 | 171 | 9 | 8 | 16,00 | 69,52 | 515
-- linhas por mês: tabela "Por mês" da 0.3 (n, p8, p16, p24, mediana iguais à tela)
```

**0.6.2 Aderência do Q-Q (160 quantis lineares do banco; a inversa da normal é calculada fora, ex.: Python
`statistics.NormalDist(25.448, 53.436).inv_cdf((k − 0,5)/160)` e `statistics.correlation`):** mesmos CTEs `m`, `fer`,
`pronto`, `us` da 0.6.1 com `base` filtrada em `FORMAT_DATETIME('%Y-%m', pr.p.entrada) BETWEEN '2026-01' AND '2026-09'`,
e no fim:

```sql
hh AS (SELECT IFNULL(us.us, 0) / 3.6e9 h FROM base b LEFT JOIN us USING (projeto_id)),
o AS (SELECT h, ROW_NUMBER() OVER (ORDER BY h) - 1 i, COUNT(*) OVER () n FROM hh),
ks AS (SELECT kk, (kk - 0.5) / 160 * (ANY_VALUE(n) - 1) pos FROM o, UNNEST(GENERATE_ARRAY(1, 160)) kk GROUP BY kk),
q AS (SELECT ks.kk, MIN(IF(o.i = CAST(FLOOR(ks.pos) AS INT64), o.h, NULL)) + (ks.pos - FLOOR(ks.pos)) *
    (MIN(IF(o.i = CAST(CEIL(ks.pos) AS INT64), o.h, NULL)) - MIN(IF(o.i = CAST(FLOOR(ks.pos) AS INT64), o.h, NULL))) qv
  FROM ks CROSS JOIN o WHERE o.i IN (CAST(FLOOR(ks.pos) AS INT64), CAST(CEIL(ks.pos) AS INT64)) GROUP BY ks.kk, ks.pos)
SELECT STRING_AGG(CAST(ROUND(qv, 6) AS STRING), ',' ORDER BY kk) quantis FROM q;
-- 25/10/2026: 0,0,0,0.02162,…,134.253637,476.827364,482.798731 → r (normal) = 0,5764
```

**0.6.3 M da cobertura (D-SLA-4):**

```sql
SELECT SUM(quantidade) m
FROM `gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_fluxo_mensal`
WHERE evento = 'entregue' AND familia = 'Nenhuma' AND mes_entrada >= '2026-01-01'
  AND mes_evento BETWEEN '2026-01-01' AND '2026-09-01';
-- 25/10/2026: 3553   (N = 2.348 da 0.6.1 → 66%)
```

**0.6.4 X8 — influência dos fora da curva (com todos × sem os fora da curva × sem pacotes):** mesmos CTEs `m`, `fer`,
`ini`, `pronto`, `base`, `us` da 0.6.1, e no fim:

```sql
p AS (SELECT b.*, IFNULL(us.us, 0) / 3.6e9 h FROM base b LEFT JOIN us USING (projeto_id)
      WHERE b.mes BETWEEN '2026-01' AND '2026-09'),
v AS (SELECT g, h, pacote FROM p, UNNEST(['Todos', IF(exclusivo, 'Exclusivos', IF(NOT exclusivo, 'Nao exclusivos', NULL))]) g WHERE g IS NOT NULL),
w AS (SELECT *, PERCENTILE_CONT(LN(h + 1), 0.25) OVER (PARTITION BY g) lq1, PERCENTILE_CONT(LN(h + 1), 0.75) OVER (PARTITION BY g) lq3 FROM v),
lim AS (SELECT *, h > EXP(lq3 + 1.5 * (lq3 - lq1)) - 1 fora FROM w),
cen AS (SELECT g, c, h FROM lim, UNNEST(['1 com todos', IF(NOT fora, '2 sem fora da curva', NULL), IF(NOT pacote, '3 sem pacotes', NULL)]) c WHERE c IS NOT NULL),
st AS (SELECT g, c, h, PERCENTILE_CONT(h, 0.5) OVER (PARTITION BY g, c) med, PERCENTILE_CONT(h, 0.9) OVER (PARTITION BY g, c) p90 FROM cen)
SELECT g, c, COUNT(*) n, ROUND(ANY_VALUE(med), 3) mediana, ROUND(AVG(h), 3) media,
  ROUND(100 * COUNTIF(h <= 24) / COUNT(*), 2) pct_3dias, ROUND(ANY_VALUE(p90), 3) p90
FROM st GROUP BY g, c ORDER BY g DESC, c;
-- 25/10/2026 (carga 23/10 20:23:42 UTC) — igual ao app (tools: calculos.exploracao()["influencia"]):
-- Todos          com todos 2348 | 14,261 | 25,448 | 70,91 | 46,323   sem fora 2320 | 13,953 | 20,102 | 71,77 | 43,011   sem pacotes 2275 | 13,764 | 19,354 | 72,53 | 40,467
-- Exclusivos     com todos 1610 | 11,830 | 23,413 | 75,90 | 40,114   sem fora 1589 | 11,690 | 17,461 | 76,90 | 37,943   sem pacotes 1569 | 11,493 | 16,777 | 77,63 | 36,928
-- Nao exclusivos com todos  725 | 19,642 | 29,501 | 60,69 | 57,123   sem fora  716 | 19,302 | 25,004 | 61,45 | 54,534   sem pacotes  698 | 19,339 | 24,872 | 61,46 | 52,442
```

Leitura (Todos): sem os 28 fora da curva a mediana anda −0,3 h (14 h → 14 h na tela) e o % em até 3 dias, +0,9 ponto
(71% → 72%); a média cai 5,3 h (25 h → 20 h) e o P90, 3,3 h (46 h → 43 h). Nos três grupos a mediana anda ≤ 0,4 h:
**os fora da curva quase não interferem na resposta (mediana e % em até 3 dias); interferem na média**, que por isso
não é usada como resposta. Tirar também os demais cards de pacote (73 no total) mexe pouco mais (mediana −0,5 h).

### 0.8 Slide 2 do estudo refeito pela referência do Caio (25/10/2026, noite) — prevalece sobre 0.2–0.6 no slide 2

**Pedido:** "Coloquei exemplos e anotações em imagens do que eu quero exatamente nessa página. Replique. Só ajuste os
cálculos com base nos dados que a gente tem." Referência: três imagens anotadas ("Página 06 · Leituras estatísticas").
Depois, no mesmo dia: quadro 4 (curva acumulada) **retirado** (vai para outra página); faixa de conclusão mais baixa;
histograma e painel com letra menor e mais leve (≥ 11 px reais em 1280–1800).

**Saiu da tela** (alguns seguem só no cálculo/ficha): seletor de talentos (o grupo vem só por `?talentos=`; a legenda do
eixo cita o grupo quando não é "Todos"); razão das metades e a barra Q1–mediana–Q3; Q-Q log-normal e "encaixe";
% negativo pelo sino; boxplot em escala log; halteres e X8 (cálculo `influencia` mantido); comparação de grupos X7
(cálculo mantido); faixa marinho do pé (agora faixa clara); quadro 4 e as marcas P50/P80/P90 (P50/P80/P90 seguem
calculados); "Recomeçar" (agora "Voltar ao início").

**Regras (código: bloco X de `sla/calculos.py`):**

| ID | Regra |
|---|---|
| X1 | Universo = entregues dos meses completos de entrega (jan–set), grupo pela URL; h = tempo da equipe sem almoço (C2) |
| X2 | Histograma fixo: faixas de 4 h de 0 a 60 h + "60 h ou mais"; eixo 0, 8, 16 … h (a marca que encostaria em "60 h ou mais" sai) |
| X3 | Blocos do topo (passos 1 e 2): **até 2 dias (≤ 16 h)**, **de 2 a 5 dias (16–40 h)**, **mais de 5 dias (> 40 h), até {máximo}**; % pelo maior resto; o texto encolhe se não couber no bloco |
| X4 | Assimetria = **coeficiente de Fisher-Pearson ajustado** (pandas `skew`); régua 0 (simétrico) → 1 (cauda forte) → o nosso, com quebra (//) acima de 3; > 0,5 positiva, −0,5 a 0,5 quase simétrica, < −0,5 negativa; % abaixo da média |
| X5 | Q-Q com 200 quantis (p = (k − 0,5)/200), tempo real × tempo previsto pela normal (média e desvio amostrais); vermelho = quantil acima do limite X6; r ≥ 0,95 só escolhe a frase ("Quase."). No histograma (passo 2): curva normal tracejada (n × 4 h × densidade) e **KDE gaussiano** com banda de **Silverman 0,9 × min(desvio, IQR/1,34) × n^−0,2**, na escala das barras |
| X6 | **Boxplot de Tukey, escala linear:** limite = Q3 + 1,5 × IQR; zonas rápidos (≤ Q1), comuns (Q1–Q3], ainda normais (Q3–limite], fora da curva (> limite), % pelo maior resto; barras pintadas pela zona do centro da faixa; no quadro, nuvem ilustrativa de pontos depois da trava (os casos vão até o máximo, fora da escala); conta escrita com 1 casa que fecha com os termos |
| X9 | P50, P80, P90 (quantis lineares): só cálculo e ficha |

**Textos da tela (Todos, carga de 23/10/2026 20:23:42 UTC):**

| Onde | Texto |
|---|---|
| Cabeçalho | logo + "GESTÃO DE ORÇAMENTOS" (caixa alta, só neste slide) + ✕; "EXPLORAÇÃO DOS DADOS"; "A maioria é rápida. Poucos demoram muito." |
| Blocos do topo (1, 2) | "56% até 2 dias (16 h)" · "32% de 2 a 5 dias" · "12% mais de 5 dias, até 515 h" |
| Passo 1 — histograma | mediana "14 h"; "média, puxada pela cauda" "25 h"; seta pontilhada "a cauda se estende para a direita →" |
| Passo 1 — painel | "FORMATO DA DISTRIBUIÇÃO · ASSIMETRIA" / "Assimetria positiva: cauda à direita" / "Assimetria é o quanto o gráfico pende para um lado. É positiva quando a maioria fica à esquerda, nos tempos curtos, e poucos casos longos esticam uma cauda para a direita." / "+7,2" e "Coeficiente de assimetria: o número que mede o tamanho dessa cauda." Régua 0 simétrico · 1 cauda forte · 7,2 o nosso / "Por isso usamos a mediana (14 h): metade dos orçamentos sai até aí. A média (25 h) é puxada pela cauda, e 73% ficam abaixo dela." |
| Passo 1 — faixa | "O orçamento típico leva **14 h de trabalho**, e não 25 h." |
| Passo 2 — histograma | barras apagadas; "se fosse um sino, com a nossa média e o nosso desvio" (tracejada); "os nossos tempos, numa curva suavizada" (KDE) |
| Passo 2 — painel | "TESTE DE NORMALIDADE · GRÁFICO Q-Q" / "Os tempos seguem a curva normal? Não." / "O gráfico Q-Q compara cada orçamento com o tempo que ele teria numa curva normal, o sino em que quase todos ficam perto da média." / Q-Q ("tempo real →", "tempo que o sino previa →") / legenda "A reta — Como seria num sino." · "Pontos na reta — Saíram como o sino previa." · "Pontos acima da reta — Demoraram bem mais que o previsto." |
| Passo 2 — faixa | "**Se fosse um sino:** a média de 25 h ficaria no meio, com metade dos pedidos de cada lado." \| "**Como não é:** metade sai em até 14 h, e 7 em cada 100 passam de 59 h. *Por isso usamos a mediana.*" |
| Passo 3 — histograma | zonas "25%" · "50% comuns: de 7 a 28 h" · "18% demorados, ainda normais: até 59 h" · "7%"; "mediana · 14 h", "média · 25 h" |
| Passo 3 — painel | "FAIXAS DE TEMPO · BOXPLOT" / "O que é normal e o que é fora da curva?" / "De cada 100 orçamentos" 25 · 50 · 18 · 7; 7 h · 28 h · 59 h; rápidos · comuns · ainda normais · fora da curva / "A caixa é o orçamento comum; as hastes vão até onde ainda é normal; os pontos são os fora da curva." / "Limite do normal pela regra do boxplot: fim da caixa + 1,5 × a largura dela (27,6 + 1,5 × 21,0 = 59,1 h)." |
| Passo 3 — faixa | "De cada 100 orçamentos, **93 ficam dentro do normal** (até 59 h) e ***7 pedem atenção***, caso a caso." |
| Navegação | "‹ ● ○ ○ 1 de 3 [Próxima: Normalidade ›]" → "Próxima: Faixas de tempo" → "Voltar ao início"; pontos clicáveis (`aria-current="step"`); `?passo=4` ou inválido cai no passo 1 |
| Gancho | "E se olharmos para 100 pedidos, o que vemos? →" |

**Memória de cálculo (app = BigQuery, conferido em 25/10/2026 com a SQL 0.8.1):**

| Medida | Todos | Exclusivos | Não exclusivos |
|---|---:|---:|---:|
| n | 2.348 | 1.610 | 725 |
| Média · mediana | 25,448 → **25 h** · 14,261 → **14 h** | 23,413 · 11,830 | 29,501 · 19,642 |
| Assimetria (Fisher-Pearson ajustado) | 7,158 → **+7,2** | 7,160 | 7,278 |
| Abaixo da média | 1.719 / 2.348 = 73,21% → **73%** | 1.200 (74,53%) | 504 (69,52%) |
| ≤ 16 · 16–40 · > 40 h | 1.304 · 755 · 289 → **56 · 32 · 12** | 1.003 · 444 · 163 | 298 · 311 · 116 |
| Máximo | **515 h** | 483 h | 515 h |
| Q1 · Q3 · IQR | 6,541 → **7 h** · 27,576 → **28 h** · 21,035 | 5,165 · 23,791 | 10,654 · 32,000 |
| Limite Tukey Q3 + 1,5 × IQR | 59,129 → **59 h** (conta "27,6 + 1,5 × 21,0 = 59,1 h") | 51,731 → 52 h | 64,019 → 64 h |
| Zonas (contagem) | 587 · 1.174 · 416 · 171 | 403 · 804 · 292 · 111 | 182 · 363 · 117 · 63 |
| Zonas na tela (maior resto) | **25 · 50 · 18 · 7** (dentro do normal 93) | — | — |
| Fora da curva que são "[Pacote" | 53 de 171 | 36 de 111 | 15 de 63 |
| P50 · P80 · P90 (só ficha) | 14,261 · 30,787 · 46,323 → 14 · 31 · 46 h | 11,830 · 27,540 · 40,114 | 19,642 · 36,256 · 57,123 |
| r do Q-Q (200 quantis; só escolhe a frase) | 0,590 (< 0,95 → "Não.") | — | — |
| Banda do KDE (Silverman) | 0,9 × min(53,436; 21,035/1,34) × 2348^−0,2 = **2,99 h** | — | — |

**0.8.1 SQL (mesmos CTEs `m`, `fer`, `ini`, `pronto`, `base`, `us` da 0.6.1), no fim:**

```sql
p AS (SELECT b.*, IFNULL(us.us, 0) / 3.6e9 h FROM base b LEFT JOIN us USING (projeto_id) WHERE b.mes BETWEEN '2026-01' AND '2026-09'),
v AS (SELECT g, h, pacote FROM p, UNNEST(['Todos', IF(exclusivo, 'Exclusivos', IF(NOT exclusivo, 'Nao exclusivos', NULL))]) g WHERE g IS NOT NULL),
w AS (SELECT *, PERCENTILE_CONT(h, 0.25) OVER x q1, PERCENTILE_CONT(h, 0.5) OVER x med, PERCENTILE_CONT(h, 0.75) OVER x q3,
        PERCENTILE_CONT(h, 0.8) OVER x p80, PERCENTILE_CONT(h, 0.9) OVER x p90, AVG(h) OVER x media FROM v WINDOW x AS (PARTITION BY g)),
z AS (SELECT *, q3 + 1.5 * (q3 - q1) lim FROM w)                                                     -- X6 Tukey linear
SELECT g, COUNT(*) n, ROUND(ANY_VALUE(media), 3) media, ROUND(ANY_VALUE(med), 3) mediana, ROUND(ANY_VALUE(q1), 3) q1,
  ROUND(ANY_VALUE(q3), 3) q3, ROUND(ANY_VALUE(lim), 3) limite, ROUND(ANY_VALUE(p80), 3) p80, ROUND(ANY_VALUE(p90), 3) p90,
  ROUND(MAX(h), 2) maximo, COUNTIF(h <= q1) z1, COUNTIF(h > q1 AND h <= q3) z2, COUNTIF(h > q3 AND h <= lim) z3,
  COUNTIF(h > lim) z4, COUNTIF(h > lim AND pacote) z4_pacote, COUNTIF(h <= 16) f16, COUNTIF(h > 16 AND h <= 40) f16_40,
  COUNTIF(h > 40) f40, COUNTIF(h < media) abaixo_media,
  ROUND(SQRT(COUNT(*) * (COUNT(*) - 1)) / (COUNT(*) - 2) * AVG(POW(h - media, 3)) / POW(AVG(POW(h - media, 2)), 1.5), 3) assimetria
FROM z GROUP BY g ORDER BY g DESC;
-- 25/10/2026 (carga 23/10 20:23:42 UTC): Todos 2348 | 25,448 | 14,261 | 6,541 | 27,576 | 59,129 | 30,787 | 46,323 | 515
--   | 587 | 1174 | 416 | 171 | 53 | 1304 | 755 | 289 | 1719 | 7,158  → igual ao app (exploracao())
```

**Validação (25/10/2026, noite):** SQL 0.8.1 = `exploracao()` nos três grupos (idêntico); suíte de 157 testes (novos:
KDE de Silverman, Tukey linear, Q-Q, régua, tela dos três quadros e o que saiu); medição no Chrome (DevTools) em
1280×800, 1440×900 e 1800×980, passos 1–3: painel da altura do histograma (topo nos blocos do topo, pé na linha do
eixo; disposição da referência 85) e igual nos três passos (387 px; 502 px em 1800), faixa logo abaixo e gancho visível
acima do rodapé, sem rolagem lateral nem no painel, nenhum texto de SVG sobreposto, menor texto de SVG 11,3 px
(1280/1440) e 14,7 px (1800).

### 0.7 Limites desta versão

1. **Cobertura:** 2.348 de 3.553 entregues (66%) têm histórico de status; jan–mai 42–50%. Viés pequeno e
   conservador. M vem da gold de fluxo (regra de entrega pela data), N da tabela de movimentos (passo `cliente`): o
   mês de um mesmo pedido pode diferir em casos de borda.
2. **Censura:** só entram os entregues; o mês parcial (vazado) ainda vai mudar e não entra em nenhuma conta. Mês
   fechado continua sujeito ao retrabalho (R1 da gold). Kaplan-Meier depende da tabela de pedidos em andamento (PD21).
3. **Pacotes/lotes:** ficam na base (só identificados pelo nome "[Pacote"); pesam na média e na cauda, quase nada na
   mediana. 27 dos 28 fora da curva (Todos) são pacotes. O ideal é a coluna de pacote/lote na gold (PD21).
4. A meta de 3 dias é **sugerida** (pendência "Oficializar a meta do SLA" em "O que falta").
5. Retorno Marca é tirado pelo nome do status (prefixo); se o board renomear o status, a regra deixa de pegar — a fase
   própria na gold resolve (PD21).
6. Mediana do mês com poucos pedidos (não exclusivos em jan–mai, 32–60) oscila; a linha mostra o número sem
   intervalo.
7. No celular, o histograma do slide 2 fica com texto < 11 px (o SVG encolhe para ~330 px); a exigência de 11 px da
   R09 vale para 1280–1800.

## 1. Identificação

| Item | Valor |
|---|---|
| Rotas | `/viu-agenciamento/sla` (aba "SLA", título da seção "SLA de entrega"; filtro `?talentos=todos\|exclusivos\|nao-exclusivos`, valor desconhecido cai em `todos`); estudo `/viu-agenciamento/sla/como-medimos` (mantém `?talentos=`; volta para `/viu-agenciamento/sla?talentos=…#1`); regras `/viu-agenciamento/sla/regras` |
| Montagem | `app/apresentacoes/gestao_orcamentos/apresentacao.py`: `montar_sla()` (`entrega` + `sem_controles=True`, página única) e `montar_estudo_sla()` (`exemplo` e `exploracao`, recalculados a cada requisição sobre a carga em memória); rota do estudo em `app/main.py` (`como_medimos`, `controles_sempre=True`, `proxima=None`) |
| Cálculo | `app/apresentacoes/gestao_orcamentos/sla/calculos.py`: `entregas()` (C1–C4, C9, C10, C14 por projeto), `entrega()` (C5–C8, C10, C11), `leituras()` (C12–C14, **não exibido**), `exemplo()` / `_caminho()` / `_montar_exemplo()` (E1–E3), `exploracao()` / `_universo()` / `_boxplot()` (X1–X7, slide 2 do estudo; arredondamentos `_pcts` maior resto, `_pontos` e `_h` meio para cima); expediente sem almoço em `app/expediente.py` (`SEM_ALMOCO`, `microssegundos_uteis`; C2, provisório até a v2 da gold); mês parcial em `app/sla.py` (`mes_parcial`) |
| Templates | `app/apresentacoes/gestao_orcamentos/sla/template.html` (página); `app/templates/como_medimos.html` (estudo) |
| Testes | 25/10/2026: `tests/test_sla_20261025.py` (17 testes: D-SLA-1..4, A2, D01, D05, D08–D13, R04, R14, R16); `tests/test_calculos.py` (`test_entregas_segue_c1_c2_c3_c4_c9`, `test_entrega_todos`), `tests/test_expediente.py`, `tests/test_rotas.py` (`test_slide_sla_mostra_os_numeros_do_grupo`, `test_endereco_antigo_do_sla_redireciona_com_filtro`, `test_regras_e_404`, `test_como_medimos`, `test_exemplo_do_dia`), `tests/test_portal.py` (`test_prazo_leituras_cauda_e_grupos`), `tests/test_exploracao.py` (`test_exploracao_numeros`, `test_exploracao_poucos_dados_e_grupo`). Suíte: **116 testes** em 24/10/2026 |
| Conferência independente | SQL da seção 6 (expediente por interseção de janelas, sem `expediente.py`); `tools/auditar_relatorio.py`, `tools/conferir_expediente.py`, `tools/conferir_estudo.py`, `tools/checar_reuniao.py` (o antigo `tools/conferir_entrega.py`, da regra com almoço, foi para `_descartados/2026-10-26/` em 26/10/2026) |
| Carga de referência | `_processado_em` = **23/10/2026 20:23:42 UTC** (14.873 linhas, 3.114 projetos); mês parcial 2026-10 (fora do ano, C7); meses completos jan–set |
| Última validação | 24/10/2026 (seção 7), conta `caio.barroso@viu.com.br`, projeto `gglobo-viu-dados-hdg-prd`, só SELECT |

### 1.1 Tabela e colunas consumidas

**Vigente desde 27/10/2026 (D57: o site só lê a gold; fim da exceção C2).** As horas da equipe sem almoço, a fila, a
elaboração, a revisão, o calendário e os dias úteis de cada orçamento entregue vêm prontos da gold; o site não recalcula
o expediente. Código antigo × novo sobre a mesma carga real (27/10, 11:11): página e estudo iguais nos 3 grupos.

| Gold (BigQuery) | Tipo · `dados.` | Colunas usadas | Para quê |
|---|---|---|---|
| `gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_2026_sla_entregas` (`TAB_SLA_ENTREGAS`) | view · `sla_entregas` | `projeto_id`, `mes`, `mes_entrada`, `entregue_em`, `exclusivo`, `tipo_de_input`, `pacote`, `h_trabalho`, `h_fila`, `h_elaboracao`, `h_revisao`, `h_calendario`, `dias_uteis`, `dias_uteis_fr`, `_processado_em` | C1–C4, C3b, C3c, C9, C14, X6, J1: SLA e estudo (slides 1–5, 7, 8) |
| `gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_2026_sla_entregas_status` (`TAB_SLA_ENTREGAS_STATUS`) | view · `sla_entregas_status` | `projeto_id`, `status`, `h` | K1: slide 6 |
| `gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_2026_sla_movimentos` (`TAB_SLA`) | tabela · `sla` | as da tabela abaixo + `sla_sem_almoco_horas` (R24) | exemplo do slide 1 (passos e horas), mês parcial, rodapé |

As views são da mesma carga dos movimentos (o site confere `_processado_em` e relê se preciso). SQL para reproduzir:
`SELECT * FROM` cada view (regras e validação na ficha `docs/tabelas/gld_agenciamento_2026_sla_entregas.md` do
PPD-GOLDEN-AGENCIAMENTO-MONDAY). As menções a `app/expediente.py` como cálculo das horas, abaixo e nas seções anteriores,
são registro: hoje o arquivo só guarda o calendário (R14).

Estado até 26/10/2026 (registro; a página lia só a tabela de movimentos e calculava as horas):

**Tabela única:** `gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_2026_sla_movimentos` (`TAB_SLA`), grão
projeto × passo (uma linha por passagem do card por um status). Lida inteira em memória (`dados.sla`), com as colunas
de `COLUNAS_SLA` em `app/dados.py` (contrato; a carga é recusada se faltar alguma).

| Coluna | Tipo | Uso nesta página | Regra |
|---|---|---|---|
| `projeto_id` | STRING | chave do projeto | todas |
| `passo` | INT | ordem dos passos; passo 1 = início do pedido; 1º passo `cliente` = pronto | C1, C3, C4, E1 |
| `status` | STRING | etapa: `Entrada` (fila), começa por "em elabora" (Elaboração), por "em revis" (Revisão) — comparação em minúsculas | C9, C14, E1, E2 |
| `fase` | STRING | `equipe` conta no tempo da equipe; `cliente` (só "Aguardando Feedback") = entrega; `standby` e `fechamento` não contam | C1, C2 |
| `entrada` | DATETIME (São Paulo) | início do passo; mês do pedido = mês da `entrada` do passo 1 | C2, C3, C4, E2 |
| `saida` | DATETIME | fim do passo (passo sem `saida` não soma horas) | C2, E1 |
| `exclusivo` | BOOL | grupo de talento (do passo 1): TRUE exclusivos, FALSE não exclusivos, NULL só em "Todos" | C10 |
| `nome_projeto` | STRING | nome mostrado no exemplo do estudo (sem " -" / "\|" no fim) | E2 |
| `_processado_em` | TIMESTAMP | mês parcial = mês de `MAX(_processado_em)` em America/Sao_Paulo; rodapé datado | C7 |
| `sla_util_horas` | FLOAT | **não entra na tela**: só na conferência com almoço (seção 6.3); a gold ainda conta o almoço | C2 (exceção) |

As demais colunas de `COLUNAS_SLA` (`status_atual`, `marca`, `talento`, `tipo_de_input`, `tipo_de_output`, `orcamento`,
`link_projeto`, `em_aberto`, `aberto_ha_util_horas`, `retrabalho`, `reaberto`, `alerta`, `fora_expediente`,
`hora_extra_horas`) são lidas pelo contrato e por outras telas/verificações, mas **não são usadas** por nenhum número
desta página.

Valores de `fase` × `status` na carga de referência: `equipe` = Entrada (3.289), Em revisão - Validação Talento (1.422),
Em elaboração - Orçamentos (1.410), Em revisão - Validação Talent Manager (639), Em revisão (636), Em elaboração
(Produção) (534), Em Elaboração (508), Em elaboração - Retorno Marca/Executivo (319), Em elaboração - Cotação Externa
(218), Em elaboração - Validação Gestão Esporte (77), Em elaboração - Cotação Gestão de Elenco (62), Em elaboração - GP
(41), Em elaboração - Audiência (17), Em revisão (Planejamento) (10), Em elaboração - Conteúdo (5), Em elaboração GP (4),
Em Elaboração - Validação Talents (2); `cliente` = Aguardando Feedback (2.820); `fechamento` = Encerrado (2.256),
Declinado Internamente (463), Declinado pelo Mercado (117), Declinado pelo talento (2); `standby` = Standby (22).

## 2. Pergunta e resposta esperada

**Título (h2):** "Quanto tempo levamos para entregar um orçamento?"

**Resposta (carga de referência, Todos):** "Levamos **15 h** de trabalho da equipe para entregar um orçamento ao
cliente." e "**2,9 dias** no calendário para o cliente receber". Exclusivos: 13 h e 2,0 dias; não exclusivos: 21 h e
4,1 dias.

O leitor precisa sair sabendo, nesta ordem:

1. **Quanto trabalho da equipe** um orçamento típico consome até a 1ª versão ao cliente (mediana, C2).
2. **Quantos dias de calendário** o cliente espera (mediana, C3).
3. **Mês a mês, quantos ficam prontos em até 1 dia e em 1 a 2 dias** de trabalho, contra a meta sugerida (C5, C6; hoje
   metade em até 2 dias de trabalho, D38 — a versão de 24/10 dizia 75%).
4. Pelo estudo "Como medimos": **como o número é contado**, num orçamento real (E1–E3).

Pergunta da diretoria atendida: SLA de exclusivos × intervenientes (= não exclusivos), pelo seletor. Outliers do SLA
(antigo slide 2) seguem calculados em `leituras()`, fora da tela desde 24/10.

## 3. O que aparece na tela (carga de 23/10/2026 20:23 UTC)

### 3.1 Página `/viu-agenciamento/sla`

| Elemento | Texto exato | Regra | Valor (Todos · Exclusivos · Não exclusivos) |
|---|---|---|---|
| Sobretítulo | "Gerencial" | — | — |
| Título | "Quanto tempo levamos para entregar um orçamento?" | — | — |
| Seletor (abaixo da pergunta, linha própria) | rótulo "Talentos"; botões "Todos / Exclusivos / Não exclusivos" com a mediana no botão; leitor de tela: "N h de trabalho típico, N orçamentos" | C10 | 15 h (2.425) · 13 h (1.635) · 21 h (775) |
| Resposta (peça tipográfica) | "Levamos **X h** de trabalho da equipe [nos talentos exclusivos / nos talentos não exclusivos] para entregar um orçamento ao cliente." + só para leitor de tela: "(mediana: metade dos orçamentos fica pronta nesse tempo ou antes)" | C2, C4, C7 | 15 h · 13 h · 21 h |
| Apoio | "**Y dias** no calendário para o cliente receber" (Y com 1 casa) | C3, C7 | 2,9 · 2,0 · 4,1 |
| Sem mês completo (janeiro ou grupo vazio) | "—" + "ainda não há meses completos em AAAA…" + "os números do ano aparecem depois do primeiro mês fechado" | C7 | — |
| Cartão do gráfico — título | "Orçamentos prontos em até 2 dias de trabalho, por mês" | C5 | — |
| Legenda (números do ano, meses completos) | "até 1 dia **A%**", "1 a 2 dias **B%**", "acima de 2 dias **C%**" (sem "No ano (jan a set):") | C5, C8 | 29/24/47 · 35/25/40 · 16/22/62 |
| Gráfico | um trilho 0–100% por mês (jan–dez): segmento escuro = até 1 dia, médio = 1 a 2 dias, trilho vazio = acima de 2 dias; total "até 2 dias" no topo; linha "meta 75%"; mês parcial com selo "parcial"; meses futuros vazios; texto para leitor de tela por mês ("set: 51% prontos em até 2 dias (25% até 1 dia, 26% de 1 a 2 dias), de 389 orçamentos.") | C5, C6, C8 | seção 5.2 |
| Lupa (canto do cartão, amarelo suave) | ícone; no foco/hover a palavra "Estudo" contorna a lupa; nome acessível "Estudo: como chegamos a esse valor"; leva a `/sla/como-medimos` com o mesmo `?talentos=` | D34 | — |
| Rodapé | "Dados até … · atualizados em …" (`apresentacao.html`) | — | — |

**Retirados da tela em 24/10/2026 (D34):** linha "Leitura" (C11, texto segue calculado em `entrega()["leitura"]`);
quadro "Como a meta é calculada"; "No ano (jan a set):" da legenda; nota "Medianas de N pedidos…"; "(fora do gráfico)";
slides 2 e 3 (cauda e exclusivos × não exclusivos) e os botões de slide.

### 3.2 Estudo "Como medimos" (`/viu-agenciamento/sla/como-medimos`)

Visual de palestra, sóbrio (referência do Caio, 24/10/2026): fundo branco; cabeçalho claro só com logo, "GESTÃO DE
ORÇAMENTOS", filete e botão **fechar** (✕, volta ao SLA com o mesmo filtro), sem as abas; "COMO MEDIMOS" (sem
numeração de slide) e o título com o traço azul. Navegação Anterior/Próximo **sempre visível** no pé
(`controles_sempre` → `data-sempre`). Cada slide termina com um **gancho** (frase em itálico, sem botão) que lembra o
próximo assunto — "de gancho em gancho". Movimento só na entrada do slide: o traço do título cresce, a linha do tempo
se desenha etapa por etapa, os marcos acendem, regras e números entram em cascata (nada se move com
`prefers-reduced-motion`).

**Slide 1 — "Como chegamos ao tempo da equipe"**

Layout: à esquerda, o **nome do orçamento** (só o nome, sem "Um orçamento real:"), logo acima da linha do tempo, e a
legenda; à direita, as duas caixas de regras **flutuantes** (cartões brancos com sombra em camadas), começando na altura
do título; no pé, uma **faixa marinho** de borda a borda (mesmo desenho da faixa do Atendimento) com os três números e o
gancho "E nos dados do ano todo? Vamos explorar melhor."

| Elemento | Texto | Regra | Exemplo de 24/10/2026, Todos (carga de 23/10) |
|---|---|---|---|
| Nome do orçamento | `nome_projeto` (sem " -" / "\|" no fim); leitor de tela: "Orçamento de exemplo: …" | E1 | [Avatim] Wanessa Camargo (projeto 13282501151, exclusivo, entrou em 13/10) |
| Linha do tempo | uma marca por etapa com nome, horas da equipe e "dd/mm · hh:mm" do início; trecho tracejado "Aguardando Feedback" com os dias e "1ª versão ao cliente"; marca final com a data e o status seguinte — ou marca tracejada "até dd/mm · em aberto" se o cliente ainda não respondeu | E2 | Entrada 2h13 (13/10 · 18:55); Elaboração 17 min (14/10 · 12:08); Revisão 8h35 (14/10 · 12:25); Aguardando Feedback 7 dias (15/10 · 13:05, 1ª versão ao cliente); até 23/10 em aberto |
| Legenda | "trabalho da equipe: conta" · "espera do cliente: não conta" | E2 | — |
| Trabalho da equipe (faixa) | valor + "no expediente, sem o fim de semana" | E2 (= C2) | **11h04** (gold com almoço: 12,16 h) |
| Para o cliente receber (faixa) | valor + "de dd/mm a dd/mm" | E3 (C3 arredondado) | **2 dias** (de 13/10 a 15/10) |
| Decisão do cliente (faixa) | valor + "não conta" (ou "ainda aguardando · não conta") | E3 | **7 dias**, ainda aguardando |
| Caixa "Entra no cálculo" | Entrada: o relógio começa; Elaboração, todas as variações; Revisão, todas as variações; Validação do talento, dentro da Revisão | C2, C14 | — |
| Caixa "Fica fora" | Standby; Ajustes depois da 1ª versão; Espera do cliente e da marca; Noites, fins de semana e feriados; nota "Expediente: seg a sex, 10h–13h e 14h–19h." | C1, C2 | — (ver limite 8, "Retorno Marca") |
| Sem exemplo | "Ainda não há um orçamento entregue com o caminho completo nos meses fechados do ano." (só se nenhum mês do ano tiver candidato) | E1 | — |

**Slide 2 — "A maioria é rápida. Poucos demoram muito."** (`/viu-agenciamento/sla/como-medimos#2`, D35, versão final de 24/10/2026)

Sobretítulo "Exploração dos dados"; título "A maioria é rápida. Poucos demoram muito.". À esquerda, o **seletor
"Talentos"** (Todos / Exclusivos / Não exclusivos, macro `seletor`) **em cima do histograma**; à direita, o **painel
em três passos**, chapado (fundo cinza-claro, filete escuro no topo, sem sombra); no pé, a faixa marinho com a
**conclusão do passo** e o gancho. Os três passos do painel e as três conclusões ficam empilhados na mesma célula
(troca por `visibility`): o layout não se mexe ao trocar de passo. "Próximo" troca o passo e repinta o histograma
(`data-passo`). Trocar o grupo **mantém o passo**: os links levam `?passo=N` (o `apresentacao.js` atualiza os links e
a URL e, ao carregar, lê `passo`). Exemplo: `/viu-agenciamento/sla/como-medimos?talentos=exclusivos&passo=3#2`.
Tipografia: Playfair só em títulos e números; textos em IBM Plex; destaques da faixa azul em semi-negrito branco.

Valores: Todos, carga de 23/10/2026 (exclusivos e não exclusivos na seção 5.5). A coluna "Campo" é a chave do
dicionário devolvido por `exploracao()`; a coluna "SQL" aponta a consulta que refaz o número no banco.

| Elemento da tela | Texto exato (template `como_medimos.html`) | Regra | Campo do cálculo | SQL | Valor (Todos) |
|---|---|---|---|---|---|
| Seletor (em cima do gráfico) | "Talentos" + "Todos / Exclusivos / Não exclusivos" (link `?talentos=…&passo=N#2`) | C10, X1 | `grupos_estudo` (montagem) | BASE `g` | — |
| Histograma — barras | quantidade em cima de cada faixa de 4 h; eixo "0 h", "8 h", …, "48 h" e "60 h ou mais" (sem "56 h"); legenda "horas de trabalho da equipe até a 1ª versão ao cliente · cada barra é uma faixa de 4 horas · 1 dia de trabalho = 8 h" | X1, X2 | `hist.barras[].n`, `hist.marcas_x` | 6.7.2 | 367, 326, 300, 283, 220, 161, 126, 137, 74, 70, 41, 71, 18, 26, 20, 185 |
| Histograma — leitor de tela | "Orçamentos em cada faixa de 4 horas de trabalho da equipe (N no total): 0 a 4 h: n; …; mais de 60 h: n. Mediana X h, média Y h." | X2 | `hist.texto`, `n` | 6.7.2 | N = 2.425 |
| Faixas no alto (passos 1 e 2) | "P% até 2 dias (16 h)", "P% de 2 a 5 dias", "P% mais de 5 dias, até {máximo}" (o texto só aparece se a faixa for larga) | X3 | `hist.faixas[].pct`, `max_txt` | 6.7.1 (`ate16`, `de16a40`, `acima40`, `maximo`) | 53 · 32 · 15; até 515 h |
| Seta (só passo 1) | "a cauda se estende para a direita →" | X4 | `hist.cauda` | — (desenho) | — |
| Linhas de centro (passos 1 e 3) | "mediana X h"; "média, puxada pela cauda Y h" | X4 | `mediana_txt`, `media_txt` | 6.7.1 | 15 h · 27 h |
| Curva (só passo 2) | sino "se fosse um sino, com a nossa média e o nosso desvio" | X5 | `hist.curva` (média, `desvio`) | 6.7.1 (`media`, `dp`) | 26,70 · 53,02 h |
| Zonas no alto (passo 3) | "P% rápidos", "P% comuns: de Q1 a Q3", "P% demorados, ainda normais: até {limite}", "P% fora da curva"; barras pintadas pela zona do centro da faixa; acima de 60 h o limite fica no começo da barra "60 h ou mais" | X6 | `hist.zonas`, `box.pcts` | 6.7.1 (`z1`–`z4`) | 25 · 50 · 18 · 7 |
| **Passo 1** — sobretítulo / título | "Formato da distribuição · Assimetria" / "Assimetria positiva: cauda à direita" (se coeficiente > 0,5; senão "Quase simétrica") | X4 | `assimetrica` | 6.7.1 | — |
| Passo 1 — texto | "**Assimetria** mede o quanto o gráfico pende para um lado. **Positiva:** a maioria é rápida e poucos casos longos esticam a cauda para a direita." | X4 | — | — | — |
| Passo 1 — caixa | número grande "+N,N"; "**Coeficiente de assimetria**: o tamanho dessa cauda"; régua 0 "simétrico", 1 "cauda forte", "o nosso" (com "//" quando passa de ~2,9) | X4 | `assimetria_txt`, `escala` | 6.7.1 (`assimetria`) | **+7,1** |
| Passo 1 — fecho | "**Por isso usamos a mediana (X h):** metade sai até aí. A média (Y h) é puxada pela cauda; Z% ficam abaixo dela." | X4 | `mediana_txt`, `media_txt`, `abaixo_media` | 6.7.1 (`pct_abaixo_media`) | 15 h · 27 h · 72% |
| **Passo 2** — sobretítulo / título | "Teste de normalidade · Gráfico Q-Q" / "Os tempos seguem a curva normal? Não." ("Quase." se \|coeficiente\| ≤ 1) | X5 | `normal` | 6.7.1 | Não. |
| Passo 2 — texto | "O **gráfico Q-Q** compara cada orçamento com o tempo que ele teria num sino (**curva normal**)." | X5 | — | — | — |
| Passo 2 — Q-Q | 160 pontos e a reta; eixos "tempo que o sino previa →" e "tempo real →"; escala até max(maior previsto pela normal, P95 observado) × 1,15; pontos acima ficam presos no topo com "↑ ainda mais longe"; pontos acima do limite da X6 em destaque | X5 | `qq.pontos[].fora/preso`, `qq.reta` | — (desenho; quantis = `PERCENTILE_CONT(h, (k − 0,5)/160)`) | — |
| Passo 2 — legenda | "**A reta** como seria num sino" · "**Na reta** saíram como o sino previa" · "**Acima da reta** demoraram bem mais" | X5 | — | — | — |
| **Passo 3** — sobretítulo / título | "Faixas de tempo · Boxplot" / "O que é normal e o que é fora da curva?" | X6 | — | — | — |
| Passo 3 — boxplot | "De cada 100 orçamentos"; números das 4 zonas; Q1, Q3 e limite embaixo; "rápidos", "comuns", "ainda normais", "fora da curva"; "mediana X h" dentro da caixa; 8 pontos de amostra dos fora da curva | X6 | `box.pcts`, `box.q1_txt`, `box.q3_txt`, `box.lim_txt`, `caixa` | 6.7.1 | 25 · 50 · 18 · 7; 7 h · 29 h · 62 h |
| Passo 3 — legenda | "**Caixa**: os comuns · **hastes**: ainda normais · **pontos**: fora da curva." | X6 | — | — | — |
| Passo 3 — nota | "Limite do normal (regra do boxplot): fim da caixa + 1,5 × largura dela = Q3 + 1,5 × IQR = limite h." | X6 | `box.conta` | 6.7.1 (`q1`, `q3`, `limite`) | "29,1 + 1,5 × 21,9 = 61,9 h" |
| Botões do painel | "Passo anterior" (ícone); "1 de 3"; próximo só com o nome: "Normalidade" → "Faixas de tempo" → "Voltar ao início" (largura fixa do maior rótulo) | — | — | — | — |
| Faixa do pé — passo 1 | "O orçamento típico leva **X h de trabalho**, e não Y h." | X4 | `mediana_txt`, `media_txt` | 6.7.1 | 15 h · 27 h |
| Faixa do pé — passo 2 | "**Se fosse um sino,** a média de Y h ficaria no meio. **Como não é,** metade sai em até X h, e F em cada 100 passam de L h. **Por isso usamos a mediana.**" | X4–X6 | `box.fora`, `box.lim_txt` | 6.7.1 (`z4`, `limite`) | 27 h · 15 h · 7 · 62 h |
| Faixa do pé — passo 3 | "De cada 100 orçamentos, **D ficam dentro do normal** (até L h) e **F pedem atenção**, caso a caso." | X6 | `box.dentro`, `box.fora` | 6.7.1 | 93 · 62 h · 7 |
| Gancho | "E se olharmos para 100 pedidos, o que vemos?" | — | — | — | — |
| Poucos dados (< 30 no grupo) | "Ainda não há orçamentos suficientes nos meses fechados do ano para esta análise." | X1 | `exploracao()` = `None` | BASE (`COUNT(*)`) | — |
| **Fora da tela** (desde 24/10, pedido do Caio: o painel fala só do grupo filtrado) | comparação dos três grupos | X7 | `comparacao[]` (`pct_regua_todos`, `pct_propria`, `limite_proprio`), `regua_todos` | 6.7.2 | mesma régua 61,9 h: 7 · 6 · 10; régua própria: 7 (> 62 h) · 8 (> 53 h) · 6 (> 72 h) |

O texto do passo e a conclusão do pé ficam em `aria-live="polite"`; os gráficos são SVG com `aria-hidden` e o conteúdo
vai ao leitor de tela pelo `figcaption` e pelos textos do painel.

## 4. Regras

> **25/10/2026:** C2, C4–C8, E1–E3, X1 e X3–X7 mudaram; a versão vigente está na seção 0.4 (e na docstring de
> `sla/calculos.py`). A tabela abaixo é a de 24/10, com as linhas C3, C4, C6 e E1 marcadas onde a regra mudou
> (26/10/2026). Resumo vigente no topo da ficha ("Estado vigente").

Fonte: docstring e blocos "Estudo" de `sla/calculos.py` (E1–E3 e X1–X7); decisões no PRD (seção 8, D16, D30, D34, D35; regras na 9.1).

| ID | Regra | Decidido | Na tela? |
|---|---|---|---|
| C1 | Pronto = 1ª chegada em Aguardando Feedback (1º passo de `fase = 'cliente'`) | Caio, 21/10 | sim |
| C2 | Horas da equipe = horas úteis de todos os passos `fase = 'equipe'` antes de C1, **inclusive Entrada**, **sem almoço** (seg–sex, 10h–13h + 14h–19h, feriados de 2026); passo sem `saida` não soma. Standby (`fase = 'standby'`) e fechamento não contam | Caio, 21/10 | sim |
| C3 | Calendário = `entrada` do passo C1 − `entrada` do passo 1, em horas corridas ÷ 24 | Caio, 21/10 | **revista:** na tela vale a C3b (dias úteis no calendário, 25/10); dias corridos só entre parênteses e no leitor de tela |
| C4 | Só entregues (têm C1); mês = mês da `entrada` do passo 1; 1º cliente no passo 1 é descartado (`invalidos`) | Caio, 21/10 | **revista (D-SLA-1, 25/10):** mês = mês da 1ª entrega |
| C5 | Faixas: até 1 dia ≤ 8 h; 1 a 2 dias > 8 h e ≤ 16 h; acima de 2 dias > 16 h (dia útil = 8 h) | Caio, 21/10 | sim |
| C6 | Meta sugerida (não oficial): 75% em até 2 dias de trabalho | referência | **revista:** D-SLA-3 (75% em 3 dias, 25/10) e depois D-SLA-7 (D38): **metade em até 2 dias de trabalho (16 h)**, a que vale |
| C7 | Números do ano só com meses completos: de jan até o mês anterior ao de `MAX(_processado_em)` em São Paulo | proposta aceita | sim |
| C8 | Arredondamento: "até 2 dias" e "até 1 dia" meio para cima; "1 a 2 dias" = diferença; "acima" = 100 − "até 2 dias" | Claude, 21/10 | sim |
| C9 | Espera na fila (Entrada), parte da C2 | Caio, 21/10 | não |
| C10 | Grupos pela `exclusivo` do passo 1; NULL só em "Todos" | Caio, 21/10 | sim (seletor) |
| C11 | Leitura por regra (melhor, pior, último × ano) | Claude, 21/10 | **não** (retirada em 24/10) |
| C12 | Cauda > 40 h; faixas ≤ 8, 8–16, 16–24, 24–40, > 40 h | D30, 23/10 | **não** (24/10) |
| C13 | Exclusivos × não exclusivos lado a lado | D30, 23/10 | **não** (24/10; o seletor cobre a comparação) |
| C14 | Etapas: Fila = `status = 'Entrada'`; Elaboração = começa por "em elabora"; Revisão = começa por "em revis" (minúsculas); leituras por etapa só de junho em diante (`MES_ETAPAS = "06"`) | Claude, 23/10 | só no estudo (E2, sem o corte de junho) |
| **E1** | **Exemplo do dia, do mês vigente:** um orçamento real **do mês vigente** (mês da 1ª entrega = mês da carga, o parcial, desde a D-SLA-1 de 25/10; na versão de 24/10 era o mês de entrada do pedido — para o exemplo ser sempre atual e girar), sorteado **uma vez por dia** (Python `random.Random(f"{data}:{grupo}").shuffle` sobre os `projeto_id` ordenados do mês), do grupo (C10), que já teve a 1ª entrega (C1, C4), com **tempo da equipe entre 2 e 16 h** (inclusive) e **caminho limpo**: todos os passos antes de C1 são `equipe`, com `saida`, cada um numa etapa conhecida (C14), o 1º é Entrada, as etapas vêm em ordem Entrada → Elaboração → Revisão sem voltar e há Elaboração. O Aguardando Feedback **pode estar em aberto**. Prefere o 1º sorteado que tenha Revisão; sem nenhum com Revisão, o 1º sorteado sem ela. **Sem candidato no mês vigente** (ex.: primeiros dias do mês), volta mês a mês (do mais recente para janeiro) até achar | Caio, 24/10 (D34; mês vigente pedido pelo Caio na mesma data) | sim (estudo) |
| **E2** | **Linha do tempo:** início de cada etapa (passos consecutivos da mesma etapa são somados), a 1ª versão ao cliente (C1) e o passo seguinte ao Aguardando Feedback — ou, se não há passo seguinte, a marca "em aberto" com a data da carga (`max(entrada, saida)` da tabela). Horas de cada etapa = C2 (sem almoço), em "N min" (< 1 h) ou "XhMM"; a soma = tempo da equipe do projeto em `entregas()` | Caio, 24/10 (D34) | sim (estudo) |
| **E3** | **"Para o cliente receber"** = dias corridos de C3, arredondados (`round`); **"Decisão do cliente"** = dias corridos de `entrada` do C1 até `entrada` do passo seguinte (ou até a data da carga, se em aberto, com a nota "ainda aguardando"), arredondados, só ilustrativo (não conta); 0 = "no mesmo dia", 1 = "1 dia" | Caio, 24/10 (D34) | sim (estudo) |
| **X1** | **Universo do slide 2:** os mesmos orçamentos da resposta — entregues (C1, C4) com mês de entrada de janeiro até o mês anterior ao da carga (C7), no grupo escolhido (C10); a medida é o tempo da equipe sem almoço de cada um (`h_trabalho`, C2). Menos de 30 no grupo: o slide mostra o aviso em vez dos gráficos | D35, 24/10 | sim (estudo) |
| **X2** | **Histograma:** 15 faixas de 4 h — (0, 4], (4, 8], …, (56, 60] — e "60 h ou mais" (> 60 h); orçamento com 0 h entra na 1ª faixa; altura = quantidade de orçamentos | D35 | sim |
| **X3** | **Faixas de prazo:** até 2 dias (≤ 16 h, C5), 2 a 5 dias (> 16 e ≤ 40 h), mais de 5 dias (> 40 h, C12), em % pelo maior resto (`_pcts`, fecham em 100); e o maior tempo do grupo (`_h`, meio para cima) | D35 | sim |
| **X4** | **Assimetria:** média e mediana (`_h`); % abaixo da média = orçamentos com h **estritamente menor** que a média (`_pontos`, meio para cima); coeficiente de assimetria de Fisher-Pearson **ajustado** (`Series.skew()` do pandas) = n ÷ ((n − 1)(n − 2)) × Σ((h − média) ÷ desvio-padrão amostral)³, 1 casa com sinal. Título "Assimetria positiva" se > 0,5. Régua: 0 = simétrico, 1 = cauda forte | D35 | sim |
| **X5** | **Normalidade:** curva normal com a média e o desvio-padrão **amostral** do grupo, na escala das barras (n × 4 h × densidade); Q-Q com 160 quantis, p = (k − 0,5) ÷ 160: x = quantil da normal, y = quantil observado (linear); escala do Q-Q até max(maior quantil previsto, P95 observado) × 1,15, pontos acima presos no topo ("↑ ainda mais longe"); ponto acima do limite da X6 em destaque; "Segue a normal?" = "Não." se \|coeficiente\| > 1 (regra prática, não teste estatístico) | D35 | sim |
| **X6** | **Boxplot:** Q1, mediana e Q3 por interpolação linear (pandas `quantile` = `PERCENTILE_CONT`); limite do normal = Q3 + 1,5 × (Q3 − Q1) (cerca de Tukey). Zonas: rápidos (h ≤ Q1), comuns (Q1 < h ≤ Q3), demorados ainda normais (Q3 < h ≤ limite), fora da curva (h > limite), em % pelo maior resto. "Dentro do normal" = 100 − fora. Cada barra do histograma pinta pela zona do centro da sua faixa de 4 h; limite acima de 60 h é desenhado no começo da barra "60 h ou mais" | D35 | sim |
| **X7** | **Comparação dos grupos:** % de cada grupo acima do limite do grupo **Todos** (mesma régua para os três; é o que a tabela mostra) e % acima do **próprio** limite (calculado, não exibido); ambos com `_pontos` (meio para cima), mais o limite próprio (`limite_proprio`) e o de Todos (`regua_todos`); grupo com menos de 30 fica fora | D35 (pergunta da diretoria: a cauda aparece em todos os talentos?) | **não** (retirada da tela em 24/10 a pedido do Caio: o painel fala só do grupo filtrado; segue calculada) |

## 5. Memória de cálculo (carga de 23/10/2026 20:23:42 UTC, conferida em 24/10/2026)

### 5.1 Resposta e seletor (C2, C3, C7, C10)

| Grupo | Pedidos jan–set | Mediana horas da equipe (sem almoço) | Tela | Mediana calendário | Tela |
|---|---:|---:|---:|---:|---:|
| Todos | **2.425** | 15,2054 h | **15 h** | 68,90 h ÷ 24 = 2,8710 dias | **2,9 dias** |
| Exclusivos | 1.635 | 12,5735 h | **13 h** | 2,0352 dias | **2,0 dias** |
| Não exclusivos | 775 | 21,0961 h | **21 h** | 4,1258 dias | **4,1 dias** |
| Sem talento (só em Todos) | 15 | — | — | — | — |

1.635 + 775 + 15 = 2.425. Mediana = interpolação linear (pandas `median`, igual a `PERCENTILE_CONT(…, 0.5)`); inteiro
pelo filtro `inteiro` (meio para cima); dias com 1 casa (`decimal(1)`).

### 5.2 Faixas do ano e por mês (C5, C8)

**Ano (legenda):**

| Grupo | ≤ 8 h | ≤ 16 h | até 1 dia | até 2 dias | 1 a 2 dias | acima de 2 dias |
|---|---:|---:|---:|---:|---:|---:|
| Todos | 693 | 1.276 | 693 ÷ 2.425 = 28,58% → **29%** | 52,62% → 53% | 53 − 29 = **24%** | 100 − 53 = **47%** |
| Exclusivos | 569 | 980 | 34,80% → **35%** | 59,94% → 60% | **25%** | **40%** |
| Não exclusivos | 123 | 293 | 15,87% → **16%** | 37,81% → 38% | **22%** | **62%** |

**Por mês (n · até 1 dia % · até 2 dias %; 1 a 2 dias = diferença; acima = 100 − até 2 dias):**

| Mês | Todos | Exclusivos | Não exclusivos |
|---|---|---|---|
| jan | 134 · 31 · 53 | 83 · 40 · 58 | 47 · 19 · 47 |
| fev | 108 · 25 · 56 | 62 · 32 · 53 | 46 · 15 · 59 |
| mar | 173 · 20 · 55 | 126 · 24 · 60 | 44 · 9 · 43 |
| abr | 225 · 27 · 46 | 181 · 30 · 51 | 44 · 14 · 27 |
| mai | 202 · 29 · 48 | 151 · 35 · 54 | 51 · 10 · 31 |
| jun | 303 · 26 · 47 | 188 · 35 · 53 | 114 · 11 · 37 |
| jul | 528 · 32 · 57 | 324 · 38 · 68 | 201 · 23 · 39 |
| ago | 363 · 35 · 57 | 274 · 41 · 68 | 88 · 17 · 24 |
| set | 389 · 25 · 51 | 246 · 31 · 59 | 140 · 14 · 39 |
| out (parcial) | 165 · 41 · 65 | 134 · 45 · 70 | 30 · 23 · 40 |

Nenhum mês completo chega à meta de 75% em nenhum grupo (maior: 68%, exclusivos em jul e ago).

### 5.3 Exemplo do estudo (E1–E3), 24/10/2026, grupo Todos

**Regra vigente (mês vigente, a partir de 24/10/2026, 2ª versão do E1):** o sorteio de 24/10 caiu em
**[Avatim] Wanessa Camargo** (`13282501151`, exclusivo, entrada 13/10/2026 — outubro, mês vigente). Conferido no
BigQuery (passos da gold) e à mão, sem almoço:

| Passo | Status | Entrada → saída | Horas úteis sem almoço | `sla_util_horas` (gold, com almoço) |
|---|---|---|---|---|
| 1 | Entrada | 13/10 18:55 → 14/10 12:08 | 0h05 + 2h08 = **2h13** | 2,21 |
| 2 | Em elaboração - Orçamentos | 14/10 12:08 → 12:25 | **17 min** | 0,28 |
| 3 | Em revisão - Validação Talent Manager | 14/10 12:25 → 15/10 13:01 | 0h35 + 5h00 + 3h00 | 9,61 |
| 4 | Em revisão - Validação Talento | 15/10 13:01 → 13:05 | 0 (almoço) | 0,06 |
| | **Revisão (3 + 4)** | | **8h35** | |
| 5 | Aguardando Feedback | 15/10 13:05 → (em aberto) | — | — |

Total **11h04** (soma em microssegundos arredondada; à mão 11h05), gold 12,16 h (a diferença é o almoço). Para o cliente
receber: 13/10 18:55 → 15/10 13:05 = 1,76 dia → **2 dias**. Decisão do cliente: 15/10 13:05 → data da carga (23/10) →
**7 dias**, "ainda aguardando".

**Versão anterior do E1 (meses completos, só Aguardando encerrado), mantida como registro:**

Projeto `12965425253`, "[Dove] Ludi Cianci", exclusivo, entrada em 28/05/2026 (mês completo).

| Passo | Status | Etapa | Entrada → saída | Horas sem almoço (site) | `sla_util_horas` (gold, com almoço) |
|---|---|---|---|---:|---:|
| 1 | Entrada | Entrada | 28/05 19:06:31 → 29/05 10:35:26 | 35,4 min (só 29/05 10:00–10:35) | 0,59 |
| 2 | Em elaboração - Orçamentos | Elaboração | 29/05 10:35:26 → 10:52:43 | 17,3 min | 0,29 |
| 3 | Em revisão - Validação Talent Manager | Revisão | 29/05 10:52:43 → 12:27:56 | | 1,59 |
| 4 | Em revisão - Validação Talento | Revisão | 29/05 12:27:56 → 15:57:00 | | 3,48 |
| 5 | Em revisão | Revisão | 29/05 15:57:00 → 16:21:26 | 3 a 5 somados: 268,7 min = **4h29** (5h29 corridas − 1 h de almoço) | 0,41 |
| 6 | Aguardando Feedback (C1) | — | 29/05 16:21:26 → 28/06 00:01:17 | não conta | — |
| 7 | Encerrado | — | 28/06 00:01:17 | — | — |

- **Trabalho da equipe:** 35,4 + 17,3 + 268,7 = 321,4 min = **5h21** (5,36 h). Na gold, Σ `sla_util_horas` dos passos
  1–5 = **6,36 h**: a diferença de 1 h é o almoço de 29/05 (13h–14h), que a gold ainda conta (exceção C2).
- **Para o cliente receber:** 29/05 16:21 − 28/05 19:06 = 21,25 h = 0,885 dia → **1 dia** ("de 28/05 a 29/05").
- **Decisão do cliente:** 28/06 00:01 − 29/05 16:21 = 29,32 dias → **29 dias** (não conta).
- **Universo do sorteio (E1), jan–set:** 1.044 entregues com 2 a 16 h (788 exclusivos, 254 não exclusivos); com caminho
  limpo 645 (508 · 137); com Revisão 426 (378 · 48). O projeto do exemplo está no universo. O sorteio em si (qual dos
  426 sai no dia) depende do gerador do Python e **não é reproduzível em SQL**: reproduz-se pelo código (seção 6.5).

### 5.4 Calculado, não exibido desde 24/10/2026 (antigos slides 2 e 3, `leituras()`)

Mantido para a próxima conversa com o Caio (outliers da diretoria). Mesma carga.

| Faixa (C12) | Pedidos | % pedidos | % horas |
|---|---:|---:|---:|
| até 1 dia (≤ 8 h) | 693 | 29 | 4 |
| 1 a 2 dias (8–16 h) | 583 | 24 | 11 |
| 2 a 3 dias (16–24 h) | 381 | 15 | 12 |
| 3 a 5 dias (24–40 h) | 407 | 17 | 19 |
| mais de 5 dias (> 40 h) | 361 | 15 | 54 |

- Horas da equipe no ano 64.750,6 h; na cauda 35.126,1 h (54,2%). Sem a cauda (2.064): mediana 12,57 h, 61,8% em até 2 dias.
- Elaboração na cauda (jun–set): 8.745,6 h ÷ 14.470,7 h = 60%.
- C13: exclusivos 1.635 · 12,57 h · 60% · 11% acima de 5 dias; não exclusivos 775 · 21,10 h · 38% · 21%; mediana da
  elaboração (jun–set, quem passou) 3,39 h (794) × 17,77 h (360).
- % dos pedidos: as duas primeiras faixas seguem a C8 (iguais à legenda); as três de cima repartem 47 pontos pelo maior
  resto (15,71 / 16,78 / 14,89 → 15 / 17 / 15). % das horas: maior resto nas cinco.

### 5.5 Estudo, slide 2 "A maioria é rápida. Poucos demoram muito." (X1–X7)

Carga de 23/10/2026 20:23:42 UTC (mês parcial 2026-10; universo jan–set/2026). **Conferido no BigQuery em 24/10/2026**
(conta `caio.barroso@viu.com.br`, só SELECT) com as SQL 6.7.1 a 6.7.3: **todos os números abaixo batem com a tela**.
Valores brutos do banco → valor na tela.

**Bases analisadas:** uma tabela só, `gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_2026_sla_movimentos`
(colunas `projeto_id`, `passo`, `status`, `fase`, `entrada`, `saida`, `exclusivo`; `nome_projeto` só na avaliação 8.1;
`_processado_em` para a carga). Nenhuma silver, nenhuma outra gold. O tempo de cada orçamento é refeito no banco sem
almoço (mesma conta da 6.2), não lido da coluna `sla_util_horas` (que ainda conta o almoço).

**Estatísticas (X1, X3, X4, X6):**

| Medida | Todos | Exclusivos | Não exclusivos |
|---|---:|---:|---:|
| Orçamentos (n) | 2.425 | 1.635 | 775 |
| Mediana | 15,2054 → **15 h** | 12,5735 → **13 h** | 21,0961 → **21 h** |
| Média | 26,7013 → **27 h** | 24,3937 → **24 h** | 31,0773 → **31 h** |
| Desvio-padrão amostral | 53,0224 h | 55,5914 h | 47,1105 h |
| Coeficiente de assimetria | 7,0600 → **+7,1** | 7,0476 → **+7,0** | 7,2365 → **+7,2** |
| Abaixo da média (h < média) | 72,21% → **72** | 75,11% → **75** | 69,03% → **69** |
| ≤ 16 h / 16–40 h / > 40 h (contagem) | 1.276 / 788 / 361 | 980 / 467 / 188 | 293 / 320 / 162 |
| idem em % exato | 52,62 / 32,49 / 14,89 | 59,94 / 28,56 / 11,50 | 37,81 / 41,29 / 20,90 |
| idem na tela (maior resto) | **53 / 32 / 15** | **60 / 29 / 11** | **38 / 41 / 21** |
| Máximo | 515,0000 → **515 h** | 482,9645 → **483 h** | 515,0000 → **515 h** |
| Q1 | 7,2135 → **7 h** | 5,5511 → **6 h** | 11,7875 → **12 h** |
| Q3 | 29,0736 → **29 h** | 24,3486 → **24 h** | 35,9649 → **36 h** |
| IQR = Q3 − Q1 | 21,8601 | 18,7975 | 24,1774 |
| Limite = Q3 + 1,5 × IQR | 61,8637 → **62 h** ("29,1 + 1,5 × 21,9 = 61,9") | 52,5449 → **53 h** ("24,3 + 1,5 × 18,8 = 52,5") | 72,2310 → **72 h** ("36,0 + 1,5 × 24,2 = 72,2") |
| Zonas ≤ Q1 / Q1–Q3 / Q3–limite / > limite (contagem) | 607 / 1.212 / 427 / 179 | 409 / 817 / 283 / 126 | 194 / 387 / 151 / 43 |
| idem em % exato | 25,03 / 49,98 / 17,61 / 7,38 | 25,01 / 49,97 / 17,31 / 7,71 | 25,03 / 49,94 / 19,48 / 5,55 |
| idem na tela (maior resto) | **25 / 50 / 18 / 7** | **25 / 50 / 17 / 8** | **25 / 50 / 19 / 6** |
| "Dentro do normal" (100 − fora) | 93 | 92 | 94 |
| Orçamentos com 0 h | 39 | 37 | 2 |

**Como o maior resto fecha em 100 (exemplo, Todos, faixas X3):** 52,62 / 32,49 / 14,89 → partes inteiras 52 / 32 / 14
(soma 98); faltam 2 pontos, que vão às 2 maiores frações (0,89 da 3ª e 0,62 da 1ª) → **53 / 32 / 15**. Zonas X6 de
Todos: 25,03 / 49,98 / 17,61 / 7,38 → 25 / 49 / 17 / 7 (98); +1 para 0,98 e 0,61 → **25 / 50 / 18 / 7**. O mesmo vale
para os outros grupos (a soma das partes inteiras deu 98 em todos).

**Histograma (X2), contagem por faixa de 4 h** — (0,4] (inclui h = 0), (4,8], …, (56,60], > 60:

| Grupo | Contagens (16 barras) | Soma |
|---|---|---:|
| Todos | 367, 326, 300, 283, 220, 161, 126, 137, 74, 70, 41, 71, 18, 26, 20, 185 | 2.425 |
| Exclusivos | 312, 257, 223, 188, 144, 89, 72, 83, 41, 38, 26, 27, 9, 13, 12, 101 | 1.635 |
| Não exclusivos | 54, 69, 75, 95, 75, 72, 54, 54, 33, 32, 14, 43, 8, 12, 7, 78 | 775 |

**Comparação dos grupos (X7) — calculada, fora da tela desde 24/10/2026** (`exploracao()["comparacao"]`):

| Grupo | Acima do limite de Todos (61,86 h) | % (`pct_regua_todos`) | Acima do próprio limite (`limite_proprio`) | % (`pct_propria`) |
|---|---:|---:|---:|---:|
| Todos | 179 | 7,38 → **7** | 179 (> 62 h) | 7,38 → **7** |
| Exclusivos | 97 | 5,93 → **6** | 126 (> 53 h) | 7,71 → **8** |
| Não exclusivos | 76 | 9,81 → **10** | 43 (> 72 h) | 5,55 → **6** |

Leitura: com a **mesma régua**, os não exclusivos têm mais orçamentos longos (10 × 6 em cada 100); com a **régua de cada
grupo**, a ordem se inverte (8 × 6), porque o limite dos exclusivos é mais baixo (53 h × 72 h). Se voltar à tela, a mesma
régua é a comparação justa entre grupos (o limite próprio mede cada grupo contra o seu típico).

## 6. Como reproduzir no banco (BigQuery, só SELECT)

Projeto `gglobo-viu-dados-hdg-prd`. Trocar o fim do período (`'2026-09'`) pelo último mês completo da carga do dia.
O site recalcula o expediente **sem almoço** (C2) porque a gold ainda conta o almoço em `sla_util_horas`. A SQL 6.2
reproduz o "sem almoço" direto no banco, por interseção de cada passo com as janelas 10h–13h e 14h–19h de cada dia
útil; deu **exatamente** os números da tela.

### 6.1 Carga

```sql
SELECT MAX(_processado_em) AS carga, COUNT(*) AS linhas, COUNT(DISTINCT projeto_id) AS projetos
FROM `gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_2026_sla_movimentos`;
-- 24/10/2026: 2026-10-23 20:23:42 UTC | 14.873 | 3.114  → mês parcial 2026-10, meses completos 2026-01 a 2026-09
```

### 6.2 Resposta, seletor e legenda (C1–C5, C7, C10): mediana de horas sem almoço, mediana de dias e faixas do ano

```sql
WITH m AS (SELECT projeto_id, passo, status, fase, entrada, saida, exclusivo
           FROM `gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_2026_sla_movimentos`),
fer AS (SELECT d FROM UNNEST([DATE '2026-01-01','2026-01-20','2026-01-25','2026-02-16','2026-02-17','2026-02-18',
  '2026-04-03','2026-04-21','2026-04-23','2026-05-01','2026-06-04','2026-07-09','2026-09-07','2026-10-12',
  '2026-11-02','2026-11-15','2026-11-20','2026-12-24','2026-12-25','2026-12-31']) d),          -- feriados de 2026 (R14)
ini AS (SELECT projeto_id, entrada AS t0, exclusivo FROM m WHERE passo = 1),
pronto AS (SELECT projeto_id, ARRAY_AGG(STRUCT(passo, entrada) ORDER BY passo LIMIT 1)[OFFSET(0)] p
           FROM m WHERE fase = 'cliente' GROUP BY projeto_id),                                -- C1
base AS (SELECT i.projeto_id, FORMAT_DATETIME('%Y-%m', i.t0) mes, i.exclusivo, pr.p.passo pp,
                DATETIME_DIFF(pr.p.entrada, i.t0, MICROSECOND)/3.6e9 h_cal                    -- C3
         FROM ini i JOIN pronto pr USING (projeto_id) WHERE pr.p.passo > 1),                  -- C4
us AS (SELECT b.projeto_id,
         SUM(GREATEST(0, DATETIME_DIFF(LEAST(e.saida, DATETIME(d, TIME(j.h1,0,0))),
                                       GREATEST(e.entrada, DATETIME(d, TIME(j.h0,0,0))), MICROSECOND))) us
       FROM base b JOIN m e ON e.projeto_id = b.projeto_id AND e.passo < b.pp AND e.fase = 'equipe' AND e.saida IS NOT NULL,
         UNNEST(GENERATE_DATE_ARRAY(DATE(e.entrada), DATE(e.saida))) d,
         UNNEST([STRUCT(10 AS h0, 13 AS h1), STRUCT(14, 19)]) j                               -- C2 sem almoço
       WHERE EXTRACT(DAYOFWEEK FROM d) BETWEEN 2 AND 6 AND d NOT IN (SELECT d FROM fer) GROUP BY 1),
p AS (SELECT b.*, COALESCE(us.us, 0)/3.6e9 h FROM base b LEFT JOIN us USING (projeto_id)
      WHERE mes BETWEEN '2026-01' AND '2026-09'),                                              -- C7
g AS (SELECT 'todos' grupo, h, h_cal FROM p
      UNION ALL SELECT IF(exclusivo, 'exclusivos', 'nao-exclusivos'), h, h_cal FROM p WHERE exclusivo IS NOT NULL)  -- C10
SELECT grupo, COUNT(*) n, ANY_VALUE(med_h) mediana_h, ANY_VALUE(med_cal)/24 mediana_dias,
       COUNTIF(h <= 8) ate8, COUNTIF(h <= 16) ate16, ROUND(100*COUNTIF(h <= 16)/COUNT(*), 2) pct_ate16
FROM (SELECT grupo, h, h_cal, PERCENTILE_CONT(h, 0.5) OVER (PARTITION BY grupo) med_h,
             PERCENTILE_CONT(h_cal, 0.5) OVER (PARTITION BY grupo) med_cal FROM g)
GROUP BY grupo ORDER BY grupo;
-- Resultado em 24/10/2026 (carga 23/10 20:23 UTC):
-- exclusivos     | 1635 | 12,5735 | 2,0352 | 569 | 980  | 59,94
-- nao-exclusivos |  775 | 21,0961 | 4,1258 | 123 | 293  | 37,81
-- todos          | 2425 | 15,2054 | 2,8710 | 693 | 1276 | 52,62
```

Tela = inteiro meio para cima das medianas (15 / 13 / 21 h) e 1 casa dos dias (2,9 / 2,0 / 4,1); faixas pela C8
(seção 5.2). Observação: as janelas usam a hora local gravada na gold (DATETIME de São Paulo), como o site.

### 6.3 Mesma conta com a coluna da gold (`sla_util_horas`, com almoço) — diferença esperada

```sql
WITH m AS (SELECT projeto_id, passo, fase, entrada, saida, exclusivo, sla_util_horas
           FROM `gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_2026_sla_movimentos`),
ini AS (SELECT projeto_id, entrada AS t0, exclusivo FROM m WHERE passo = 1),
pronto AS (SELECT projeto_id, MIN(passo) pp FROM m WHERE fase = 'cliente' GROUP BY projeto_id),
p AS (SELECT i.projeto_id, FORMAT_DATETIME('%Y-%m', i.t0) mes, i.exclusivo,
             SUM(IF(e.fase = 'equipe' AND e.passo < pr.pp AND e.saida IS NOT NULL, e.sla_util_horas, 0)) h_gold
      FROM ini i JOIN pronto pr USING (projeto_id) JOIN m e USING (projeto_id)
      WHERE pr.pp > 1 GROUP BY 1, 2, 3),
g AS (SELECT 'todos' grupo, h_gold FROM p WHERE mes BETWEEN '2026-01' AND '2026-09'
      UNION ALL SELECT IF(exclusivo, 'exclusivos', 'nao-exclusivos'), h_gold FROM p
      WHERE mes BETWEEN '2026-01' AND '2026-09' AND exclusivo IS NOT NULL)
SELECT grupo, COUNT(*) n, ANY_VALUE(med) mediana_gold, COUNTIF(h_gold <= 16) ate16, COUNTIF(h_gold <= 18) ate18
FROM (SELECT *, PERCENTILE_CONT(h_gold, 0.5) OVER (PARTITION BY grupo) med FROM g)
GROUP BY grupo ORDER BY grupo;
-- 24/10/2026: exclusivos 1635 | 14,00 h | 892 ; nao-exclusivos 775 | 23,86 h | 242 ; todos 2425 | 17,18 h | 1137 (46,89%)
-- todos, até 18 h (dia de 9 h com almoço): 52,54%. Soma das horas: gold 72.860 h × sem almoço 64.750,6 h
```

**Diferença esperada:** com almoço, cada dia útil tem 9 h em vez de 8 h; a mediana sobe de 15,2 h para 17,2 h (todos),
de 12,6 h para 14,0 h (exclusivos) e de 21,1 h para 23,9 h (não exclusivos), e "até 16 h" cai de 52,6% para 46,9%. Esta
consulta **não reproduz a tela**; serve para medir o efeito do almoço até a v2 da gold, quando a coluna da gold passa a
ser a fonte (e a 6.2 deve então bater com ela).

### 6.4 Gráfico: faixas por mês e grupo (C5, C8)

Repetir os CTEs `m`, `fer`, `ini`, `pronto`, `base`, `us` da 6.2 (com `pronto` podendo ser `MIN(passo)`), sem o filtro
de mês em `p`, e terminar com:

```sql
p AS (SELECT b.*, COALESCE(us.us, 0)/3.6e9 h FROM base b LEFT JOIN us USING (projeto_id)),
g AS (SELECT 'todos' grupo, mes, h FROM p
      UNION ALL SELECT IF(exclusivo, 'exclusivos', 'nao-exclusivos'), mes, h FROM p WHERE exclusivo IS NOT NULL)
SELECT grupo, mes, COUNT(*) n,
       CAST(FLOOR(100*COUNTIF(h <= 8)/COUNT(*) + 0.5) AS INT64) ate1_pct,      -- C8: meio para cima
       CAST(FLOOR(100*COUNTIF(h <= 16)/COUNT(*) + 0.5) AS INT64) ate2_pct      -- 1 a 2 dias = ate2 − ate1; acima = 100 − ate2
FROM g WHERE mes LIKE '2026-%' GROUP BY 1, 2 ORDER BY 1, 2;
-- 24/10/2026: os valores da seção 5.2 (ex.: todos 2026-09 → 389 | 25 | 51)
```

### 6.5 Exemplo do estudo (E1–E3): passos e horas por etapa de um projeto

```sql
WITH m AS (SELECT * FROM `gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_2026_sla_movimentos`
           WHERE projeto_id = '13282501151'),                                 -- projeto do dia (24/10: Avatim; antes 12965425253)
fer AS (SELECT d FROM UNNEST([DATE '2026-01-01','2026-01-20','2026-01-25','2026-02-16','2026-02-17','2026-02-18',
  '2026-04-03','2026-04-21','2026-04-23','2026-05-01','2026-06-04','2026-07-09','2026-09-07','2026-10-12',
  '2026-11-02','2026-11-15','2026-11-20','2026-12-24','2026-12-25','2026-12-31']) d),
pp AS (SELECT MIN(passo) pp FROM m WHERE fase = 'cliente'),
passos AS (
  SELECT e.passo, e.entrada, e.saida, e.sla_util_horas,
    CASE WHEN e.status = 'Entrada' THEN 'Entrada' WHEN STARTS_WITH(LOWER(e.status), 'em elabora') THEN 'Elaboração'
         WHEN STARTS_WITH(LOWER(e.status), 'em revis') THEN 'Revisão' END AS etapa,              -- C14
    (SELECT SUM(GREATEST(0, DATETIME_DIFF(LEAST(e.saida, DATETIME(d, TIME(j.h1,0,0))),
                                          GREATEST(e.entrada, DATETIME(d, TIME(j.h0,0,0))), MICROSECOND)))
     FROM UNNEST(GENERATE_DATE_ARRAY(DATE(e.entrada), DATE(e.saida))) d,
          UNNEST([STRUCT(10 AS h0, 13 AS h1), STRUCT(14, 19)]) j
     WHERE EXTRACT(DAYOFWEEK FROM d) BETWEEN 2 AND 6 AND d NOT IN (SELECT d FROM fer)) / 6e7 AS min_sem_almoco
  FROM m e, pp WHERE e.passo < pp.pp AND e.fase = 'equipe')
SELECT etapa, MIN(entrada) inicio, MAX(saida) fim, ROUND(SUM(min_sem_almoco), 1) minutos_sem_almoco,
       ROUND(SUM(sla_util_horas), 2) horas_gold
FROM passos GROUP BY etapa ORDER BY inicio;
-- 24/10/2026: Entrada 28/05 19:06 → 29/05 10:35 | 35,4 min | 0,59
--             Elaboração 29/05 10:35 → 10:52  | 17,3 min | 0,29
--             Revisão 29/05 10:52 → 16:21     | 268,7 min | 5,48   → total 321,4 min = 5h21 (gold 6,36 h)
-- Passos completos (C1 e o seguinte): SELECT passo, status, fase, entrada, saida, sla_util_horas FROM ... ORDER BY passo
-- → 6 Aguardando Feedback 29/05 16:21 → 28/06 00:01 (29 dias); 7 Encerrado
```

O sorteio do dia não tem equivalente em SQL (gerador `random` do Python com semente "AAAA-MM-DD:grupo"). Para saber
qual projeto sai num dia:

```python
from datetime import date
from app import dados, sla
from app.apresentacoes.gestao_orcamentos.sla import calculos as C
mov = dados.sla.df(forcar=True)
C.exemplo(mov, sla.mes_parcial(mov), "todos", date(2026, 10, 24))   # → "[Dove] Ludi Cianci", 5h21, 1 dia, 29 dias
```

O universo do sorteio (1.044 / 645 / 426 da seção 5.3) foi contado por SQL com os CTEs da 6.2 mais o filtro
`h BETWEEN 2 AND 16` e as condições de caminho limpo de E1 (passos antes de C1 todos `equipe` com `saida` e etapa
conhecida, 1º = Entrada, ordem não decrescente Entrada < Elaboração < Revisão, ao menos uma Elaboração, C1 com `saida`
e passo C1 + 1 existente).

### 6.6 Não exibido (C12–C14)

Cauda e etapas: acrescentar `WHERE h <= 40` à 6.2 para "sem a cauda" (2.064; 12,57 h; 61,8%) e `SUM(h)`,
`SUM(IF(h > 40, h, 0))` para as horas (64.750,6 / 35.126,1). Etapas: agrupar o bloco `us` também pela etapa da 6.5 e
filtrar `mes >= '2026-06'` (elaboração na cauda 8.745,6 ÷ 14.470,7 h = 60%; mediana da elaboração com horas > 0: 3,39 h
em 794 exclusivos, 17,77 h em 360 não exclusivos).

**Base de 21/10 por time travel** (explica 2.428 → 2.425):

```sql
WITH v AS (SELECT projeto_id, passo, status, entrada, exclusivo
           FROM `gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_2026_sla_movimentos`
           FOR SYSTEM_TIME AS OF TIMESTAMP '2026-10-22 02:00:00+00')
SELECT FORMAT_DATETIME('%Y-%m', i.entrada) mes, COUNT(*) n
FROM v i WHERE i.passo = 1
  AND EXISTS (SELECT 1 FROM v c WHERE c.projeto_id = i.projeto_id AND c.status = 'Aguardando Feedback' AND c.passo > 1)
GROUP BY 1 ORDER BY 1
-- jan 134 | fev 108 | mar 173 | abr 225 | mai 202 | jun 303 | jul 529 | ago 363 | set 391  => 2.428
```

### 6.7 Estudo, slide 2 (X1–X7): cada número direto no banco

Todas as consultas começam pelo mesmo **bloco BASE** (é o da 6.2, com `nome_projeto` e `t0` a mais para a avaliação
8.1). Ele devolve `p`: uma linha por orçamento entregue de jan até o último mês completo, com `h` = horas da equipe sem
almoço. **Para outra carga, troque só `'2026-09'`** pelo último mês completo (mês anterior ao de `MAX(_processado_em)`
em São Paulo, SQL 6.1) e, a partir de 2027, a lista de feriados.

```sql
-- BLOCO BASE (copiar no início de cada consulta 6.7.x)
WITH m AS (SELECT projeto_id, passo, status, fase, entrada, saida, exclusivo, nome_projeto
           FROM `gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_2026_sla_movimentos`),
fer AS (SELECT d FROM UNNEST([DATE '2026-01-01','2026-01-20','2026-01-25','2026-02-16','2026-02-17','2026-02-18',
  '2026-04-03','2026-04-21','2026-04-23','2026-05-01','2026-06-04','2026-07-09','2026-09-07','2026-10-12',
  '2026-11-02','2026-11-15','2026-11-20','2026-12-24','2026-12-25','2026-12-31']) d),           -- feriados 2026
ini AS (SELECT projeto_id, entrada AS t0, exclusivo, nome_projeto FROM m WHERE passo = 1),
pronto AS (SELECT projeto_id, MIN(passo) pp FROM m WHERE fase = 'cliente' GROUP BY projeto_id),   -- C1
base AS (SELECT i.projeto_id, i.nome_projeto, i.t0, FORMAT_DATETIME('%Y-%m', i.t0) mes, i.exclusivo, pr.pp
         FROM ini i JOIN pronto pr USING (projeto_id) WHERE pr.pp > 1),                         -- C4
us AS (SELECT b.projeto_id,
         SUM(GREATEST(0, DATETIME_DIFF(LEAST(e.saida, DATETIME(d, TIME(j.h1,0,0))),
                                       GREATEST(e.entrada, DATETIME(d, TIME(j.h0,0,0))), MICROSECOND))) us
       FROM base b JOIN m e ON e.projeto_id = b.projeto_id AND e.passo < b.pp AND e.fase = 'equipe' AND e.saida IS NOT NULL,
         UNNEST(GENERATE_DATE_ARRAY(DATE(e.entrada), DATE(e.saida))) d,
         UNNEST([STRUCT(10 AS h0, 13 AS h1), STRUCT(14, 19)]) j                                -- C2 sem almoço
       WHERE EXTRACT(DAYOFWEEK FROM d) BETWEEN 2 AND 6 AND d NOT IN (SELECT d FROM fer) GROUP BY 1),
p AS (SELECT b.*, COALESCE(us.us, 0)/3.6e9 h FROM base b LEFT JOIN us USING (projeto_id)
      WHERE mes BETWEEN '2026-01' AND '2026-09'),                                               -- C7 (X1)
g AS (SELECT 'todos' grupo, h FROM p
      UNION ALL SELECT IF(exclusivo, 'exclusivos', 'nao-exclusivos'), h FROM p WHERE exclusivo IS NOT NULL)  -- C10
```

**6.7.1 Estatísticas do slide (X3, X4, X6):** BASE +

```sql
, q AS (SELECT grupo, h,
          PERCENTILE_CONT(h, 0.25) OVER (PARTITION BY grupo) q1,
          PERCENTILE_CONT(h, 0.5)  OVER (PARTITION BY grupo) med,
          PERCENTILE_CONT(h, 0.75) OVER (PARTITION BY grupo) q3,
          AVG(h) OVER (PARTITION BY grupo) media, STDDEV_SAMP(h) OVER (PARTITION BY grupo) dp,
          COUNT(*) OVER (PARTITION BY grupo) n FROM g)
SELECT grupo, ANY_VALUE(n) n, ROUND(ANY_VALUE(med),4) mediana, ROUND(ANY_VALUE(media),4) media, ROUND(ANY_VALUE(dp),4) dp,
  ROUND(ANY_VALUE(n)/((ANY_VALUE(n)-1)*(ANY_VALUE(n)-2)) * SUM(POW((h-media)/dp,3)),4) assimetria,  -- = pandas skew()
  ROUND(100*COUNTIF(h < media)/COUNT(*),2) pct_abaixo_media,
  COUNTIF(h <= 16) ate16, COUNTIF(h > 16 AND h <= 40) de16a40, COUNTIF(h > 40) acima40,
  ROUND(MAX(h),4) maximo, ROUND(ANY_VALUE(q1),4) q1, ROUND(ANY_VALUE(q3),4) q3,
  ROUND(ANY_VALUE(q3) + 1.5*(ANY_VALUE(q3)-ANY_VALUE(q1)),4) limite,
  COUNTIF(h <= q1) z1, COUNTIF(h > q1 AND h <= q3) z2, COUNTIF(h > q3 AND h <= q3 + 1.5*(q3-q1)) z3,
  COUNTIF(h > q3 + 1.5*(q3-q1)) z4, COUNTIF(h = 0) h_zero
FROM q GROUP BY grupo ORDER BY grupo;
-- 24/10/2026 (carga 23/10 20:23 UTC):
-- exclusivos     | 1635 | 12,5735 | 24,3937 | 55,5914 | 7,0476 | 75,11 | 980  | 467 | 188 | 482,9645 | 5,5511  | 24,3486 | 52,5449 | 409 | 817  | 283 | 126 | 37
-- nao-exclusivos |  775 | 21,0961 | 31,0773 | 47,1105 | 7,2365 | 69,03 | 293  | 320 | 162 | 515,0000 | 11,7875 | 35,9649 | 72,2310 | 194 | 387  | 151 |  43 |  2
-- todos          | 2425 | 15,2054 | 26,7013 | 53,0224 | 7,0600 | 72,21 | 1276 | 788 | 361 | 515,0000 | 7,2135  | 29,0736 | 61,8637 | 607 | 1212 | 427 | 179 | 39
```

**6.7.2 Histograma (X2) e comparação dos grupos (X7):** BASE +

```sql
, lim AS (SELECT grupo, ANY_VALUE(q3) + 1.5*(ANY_VALUE(q3)-ANY_VALUE(q1)) limite
          FROM (SELECT grupo, PERCENTILE_CONT(h,0.25) OVER (PARTITION BY grupo) q1,
                       PERCENTILE_CONT(h,0.75) OVER (PARTITION BY grupo) q3 FROM g)
          GROUP BY grupo)
SELECT g.grupo,
  STRING_AGG(CAST(c AS STRING), ', ' ORDER BY faixa) histograma,
  ANY_VALUE(x7.acima_todos) acima_lim_todos, ANY_VALUE(x7.pct_todos) pct_lim_todos,
  ANY_VALUE(x7.acima_proprio) acima_lim_proprio, ANY_VALUE(x7.pct_proprio) pct_lim_proprio
FROM (SELECT grupo, LEAST(IF(h <= 0, 0, CAST(CEIL(h/4) AS INT64) - 1), 15) faixa, COUNT(*) c   -- (0,4]=0 … (56,60]=14, >60=15
      FROM g GROUP BY 1, 2) g
JOIN (SELECT g.grupo, COUNTIF(g.h > t.limite) acima_todos, ROUND(100*COUNTIF(g.h > t.limite)/COUNT(*),2) pct_todos,
             COUNTIF(g.h > l.limite) acima_proprio, ROUND(100*COUNTIF(g.h > l.limite)/COUNT(*),2) pct_proprio
      FROM g JOIN lim l USING (grupo) CROSS JOIN (SELECT limite FROM lim WHERE grupo = 'todos') t GROUP BY 1) x7
  USING (grupo)
GROUP BY g.grupo ORDER BY g.grupo;
-- 24/10/2026:
-- exclusivos     | 312, 257, 223, 188, 144, 89, 72, 83, 41, 38, 26, 27, 9, 13, 12, 101 |  97 | 5,93 | 126 | 7,71
-- nao-exclusivos | 54, 69, 75, 95, 75, 72, 54, 54, 33, 32, 14, 43, 8, 12, 7, 78        |  76 | 9,81 |  43 | 5,55
-- todos          | 367, 326, 300, 283, 220, 161, 126, 137, 74, 70, 41, 71, 18, 26, 20, 185 | 179 | 7,38 | 179 | 7,38
```

**6.7.3 Os maiores tempos (avaliação 8.1):** BASE (sem precisar de `g`) +

```sql
SELECT projeto_id, nome_projeto, mes, exclusivo, ROUND(h, 1) h
FROM p ORDER BY h DESC LIMIT 15;
-- 24/10/2026: 515,0 "[Pacote Festival] Squad de Talento_ Pacote Rock in Rio 2026_ In Loco | M (Amplifica) - Alimentos"
--   (mar, não exclusivo); depois 14 cards "[Pacote Festival] <talento>_ Pacote Rock in Rio 2026_ Remoto" (abr, exclusivos)
--   entre 482,5 e 483,0 h — Milena, Maxiane Rodrigues, Samira Sagr, Marciele Albuquerque, Sofia Miranda, Karine Alves,
--   Pedro Rocha, Ludimilla Cianci, Wanessa Camargo, Bia Reis, Vivi Araújo, Pitel, Milton Cunha, Jonathan.
--   Quase todos ficaram ~478 h num único passo "Em Elaboração" de 07/04/2026 15:33 a 06/07/2026 ~12:45.
```

**6.7.4 Robustez (avaliação 8.1): pacotes, lotes, sem a cauda e em log:** BASE +

```sql
, g0 AS (SELECT 'todos' grupo, h, STARTS_WITH(nome_projeto,'[Pacote') pacote FROM p
         UNION ALL SELECT IF(exclusivo,'exclusivos','nao-exclusivos'), h, STARTS_WITH(nome_projeto,'[Pacote')
         FROM p WHERE exclusivo IS NOT NULL),
lim0 AS (SELECT grupo, ANY_VALUE(q3)+1.5*(ANY_VALUE(q3)-ANY_VALUE(q1)) limite FROM
         (SELECT grupo, PERCENTILE_CONT(h,0.25) OVER (PARTITION BY grupo) q1,
                 PERCENTILE_CONT(h,0.75) OVER (PARTITION BY grupo) q3 FROM g0) GROUP BY 1),
v AS (SELECT grupo, 'a_completo' variante, h x FROM g0
      UNION ALL SELECT grupo, 'b_sem_pacotes', h FROM g0 WHERE NOT pacote
      UNION ALL SELECT g0.grupo, 'c_ate_limite', h FROM g0 JOIN lim0 USING (grupo) WHERE h <= limite
      UNION ALL SELECT grupo, 'd_log_h_mais_1', LN(h + 1) FROM g0),
s AS (SELECT grupo, variante, x, AVG(x) OVER w media, STDDEV_SAMP(x) OVER w dp, COUNT(*) OVER w n,
        PERCENTILE_CONT(x,0.5) OVER w med, PERCENTILE_CONT(x,0.25) OVER w q1, PERCENTILE_CONT(x,0.75) OVER w q3,
        PERCENTILE_CONT(x,0.9) OVER w p90, PERCENTILE_CONT(x,0.95) OVER w p95
      FROM v WINDOW w AS (PARTITION BY grupo, variante))
SELECT grupo, variante, ANY_VALUE(n) n, ROUND(ANY_VALUE(med),2) mediana, ROUND(ANY_VALUE(media),2) media,
  ROUND(ANY_VALUE(n)/((ANY_VALUE(n)-1)*(ANY_VALUE(n)-2))*SUM(POW((x-media)/dp,3)),2) assimetria,
  ROUND(ANY_VALUE(q3)+1.5*(ANY_VALUE(q3)-ANY_VALUE(q1)),2) limite,
  ROUND(100*COUNTIF(x > q3+1.5*(q3-q1))/COUNT(*),2) pct_acima_limite, ROUND(ANY_VALUE(p90),2) p90, ROUND(ANY_VALUE(p95),2) p95
FROM s GROUP BY 1,2 ORDER BY 1,2;
-- 24/10/2026, Todos: completo 2425 | 15,21 | 26,70 | 7,06 | 61,86 | 7,38 | 49,55 | 74,16
--                    sem pacotes 2351 | 14,82 | 20,81 | 2,82 | 59,12 | 5,78 | 47,02 | 64,00
--                    até o limite 2246 | 13,83 | 17,14 | 0,98 | (51,59) | — | 37,32 | 47,02
--                    log(h+1) 2425 | 2,79 | 2,69 | −0,21 | 5,35 (= e^5,35 − 1 ≈ 210 h) | 1,20 | — | —
-- Exclusivos: sem pacotes 1594 | 12,14 | 17,89 | 3,01 ; log −0,01.  Não exclusivos: sem pacotes 748 | 21,00 | 26,82 | 2,79 ; log −0,58
```

Para os **lotes** (cards criados no mesmo minuto), acrescentar a `p` a coluna
`COUNT(*) OVER (PARTITION BY DATETIME_TRUNC(t0, MINUTE)) lote` e agrupar `WHERE lote >= 5` por
`DATETIME_TRUNC(t0, MINUTE)`: 6 lotes, 77 cards (resultados na 8.1).

### 6.8 Passo a passo para conferir o slide 2 sozinho

1. **Carga do dia:** rode a 6.1. O último mês completo é o mês anterior ao de `MAX(_processado_em)` em São Paulo
   (carga de 23/10/2026 → `'2026-09'`). O rodapé da página mostra a mesma data.
2. **Universo:** cole o bloco BASE da 6.7 com esse mês no filtro de `p`. Confira `SELECT COUNT(*) FROM p` = n de
   Todos (2.425); por grupo, 1.635 + 775 + 15 sem talento = 2.425.
3. **Horas de cada orçamento:** é a soma, nos passos da equipe antes da 1ª ida ao cliente, das horas dentro das
   janelas 10h–13h e 14h–19h de seg a sex fora dos feriados. Para ver um orçamento só, use a 6.5 com o `projeto_id`.
4. **Estatísticas:** rode a 6.7.1. Arredonde: horas meio para cima (15,2054 → 15; 61,8637 → 62); coeficiente com 1
   casa (7,06 → 7,1); "% abaixo da média" meio para cima (72,21 → 72).
5. **Faixas e zonas em %:** divida as contagens por n e aplique o **maior resto** (5.5): partes inteiras e, se
   faltarem pontos para 100, +1 nas maiores frações.
6. **Histograma e grupos:** rode a 6.7.2 e compare barra a barra com o leitor de tela do gráfico (o `figcaption`
   lista "0 a 4 h: 367; …"); a comparação dos grupos (7 · 6 · 10) está fora da tela, em `exploracao()["comparacao"]`.
7. **No pandas** (mesmo resultado): `h = C._universo(mov, sla.mes_parcial(mov), "todos")`; `h.median()`, `h.mean()`,
   `h.std()`, `h.skew()`, `h.quantile([.25,.5,.75])`; ou `C.exploracao(mov, sla.mes_parcial(mov), "todos")`.

### 6.9 Atualização a cada carga (nada fixo no código)

Nenhum número do slide 2 está escrito no código ou no template: tudo é recalculado da tabela a cada carga.

- A cada requisição, `montar_estudo_sla()` chama `calculos.exploracao(mov, mes_parcial, grupo)` sobre a carga em
  memória (`dados.sla.df()`); a carga em memória é trocada quando o `_processado_em` da gold muda (verificação do
  metadado; em produção, na própria requisição; no computador, em segundo plano).
- `entregas()` (horas por orçamento, C1–C4) fica em cache **por versão da carga** (`df.attrs["versao"]`): carga nova =
  chave nova = recálculo; as 3 últimas versões ficam guardadas.
- O mês parcial vem da própria carga (`sla.mes_parcial`, mês de `MAX(_processado_em)` em São Paulo): em novembro,
  outubro entra sozinho no universo (C7).
- Fixos por regra (não são números da tela): faixas de 4 h e corte em 60 h (X2), 16 h e 40 h (X3), 1,5 × IQR (X6),
  160 quantis (X5) e mínimo de 30 orçamentos (X1). Os feriados do site são calculados por ano em `app/expediente.py`
  (fixos + Páscoa), então 2027 já sai certo no site; **na SQL** a lista de feriados é fixa de 2026 e precisa ser
  estendida quando o universo cruzar o ano (limite 6).
- `tests/test_exploracao.py` confere as regras com dados sintéticos; a conferência com o banco é a 6.7 (refazer a
  cada mudança de regra ou antes de apresentar).

## 7. Validações feitas

| Data | O quê | Resultado |
|---|---|---|
| 21/10/2026 | Tela × cálculo × BigQuery (com almoço 17,19 h e 52,5% em até 18 h; calendário 2,8733 dias em 2.428) | ✅ (PRD 9.1) |
| 23/10/2026 | Revalidação completa (C2 sem almoço), carga 23/10 20:23 UTC: código × SQL independente × `tools/auditar_relatorio.py` | ✅ exatamente: 2.425; 15,2054 h; 2,871 dias; 29/24/47; meses; exclusivos 1.635 · 12,57 h · 59,94%; não exclusivos 775 · 21,10 h · 37,81%; 15 sem talento; expediente × gold em 11.759 passos, máx. 19 s |
| 23/10/2026 | Base 2.428 → 2.425 por time travel | ✅ explicada (R1 da gold: 4 voltaram para a equipe, 1 voltou a Encerrado) |
| 23/10/2026 | `leituras()` (C12–C14) × análise independente | ✅ (seção 5.4) |
| **24/10/2026** | SQL 6.2 no BigQuery (mesma carga), por grupo | ✅ igual à tela: 2.425 / 1.635 / 775; medianas 15,2054 / 12,5735 / 21,0961 h (15 / 13 / 21 h); dias 2,8710 / 2,0352 / 4,1258 (2,9 / 2,0 / 4,1); ≤ 8 h 693 / 569 / 123; ≤ 16 h 1.276 / 980 / 293 |
| **24/10/2026** | SQL 6.4: faixas por mês nos três grupos | ✅ seção 5.2 (todos igual à revalidação de 23/10) |
| **24/10/2026** | SQL 6.3 (gold com almoço) | ✅ diferença documentada: 17,18 h, 46,89% ≤ 16 h, 52,54% ≤ 18 h; 72.860 h × 64.750,6 h |
| **24/10/2026** | Exemplo do estudo (SQL 6.5) × tela | ✅ 35 min / 17 min / 4h29 = 5h21; 1 dia; 29 dias; gold 6,36 h (1 h de almoço) |
| **24/10/2026** | Universo de E1 por SQL | ✅ 1.044 → 645 → 426 (Todos); exemplo dentro |
| **24/10/2026** | Testes | ✅ 114 passando (inclui `test_como_medimos`, `test_exemplo_do_dia`: exemplo estável no dia, caminho limpo, soma das etapas = C2) |
| **24/10/2026** | Slide 2 do estudo (X1–X7), SQL 6.7.1 e 6.7.2 no BigQuery (carga 23/10 20:23:42 UTC), três grupos | ✅ **todos os números da tela batem**: n, mediana, média, coeficiente de assimetria (7,06 / 7,05 / 7,24), % abaixo da média, faixas X3, máximo, Q1, Q3, limite e a conta da nota, zonas X6, 16 barras do histograma e X7 (régua de Todos e própria, fora da tela). Nenhuma divergência |
| **24/10/2026** | Avaliação estatística do slide 2 (SQL 6.7.3 e 6.7.4) | ⚠️ cálculo certo, interpretação com ressalvas: seção 8.1 |
| **24/10/2026** | Testes | ✅ **116** passando (inclui `tests/test_exploracao.py`, base sintética de 72 orçamentos) |

## 8. Limites e pontos de atenção

1. Mês corrente é parcial e otimista (só entra quem já foi ao cliente): fica fora do ano (C7).
2. A meta é sugerida, não oficial (C6; hoje metade em até 2 dias de trabalho, D38; em 24/10 era 75%).
3. Mediana de horas e mediana de dias não são do mesmo projeto: não "fecham" entre si.
4. Expediente sem almoço é recalculado no site (exceção C2) até a v2 da gold; a coluna `sla_util_horas` dá ~2 h a mais
   na mediana (seção 6.3).
5. A base de mês fechado oscila com o retrabalho (R1 da gold): projeto que volta para a equipe some até voltar ao
   cliente (lembretes, item 4).
6. Feriados da SQL são os de 2026 (iguais aos do site); um pedido que cruze o ano precisaria dos feriados de 2025/2027.
7. O exemplo do estudo muda todo dia e por grupo; ele é **típico** por construção (2 a 16 h, caminho limpo), não médio.
   Os 426 com Revisão são 18% dos 2.425: o caminho limpo é a minoria. Não usar o exemplo como medida.
8. **(Resolvido em 25/10/2026 por D-SLA-2: o Retorno Marca saiu das horas; as Cotações ficam e aparecem na caixa "Entra no cálculo".)** **Caixa "Fica fora" × regra C2 (para decisão do Caio):** a caixa diz que a "Espera do cliente e da marca" fica fora,
   mas os sub-status de Elaboração **"Em elaboração - Retorno Marca/Executivo"** (182 projetos, ~2.078 h pela gold, jan–set),
   "Cotação Externa" (138, ~2.045 h) e "Cotação Gestão de Elenco" (42, ~1.107 h) são `fase = 'equipe'` e **contam** no
   tempo da equipe. A frase vale para a espera do cliente (Aguardando Feedback) e para o Standby (11 projetos, ~207 h,
   de fato fora). Ou a regra passa a tirar esses sub-status, ou o texto da caixa muda; nada foi alterado.
9. Não exclusivos têm menos de 50 pedidos por mês em jan–mai: o gráfico por mês do grupo oscila muito.
10. Não há prazo de 2025 (PD15): comparação com o ano anterior só em 2027.
11. **Slide 2 (X1–X7): a conta está certa, a leitura precisa de cuidado.** Ver 8.1: a cauda é dominada por cards de
    pacote/lote; "fora da curva" pela regra do boxplot não quer dizer erro ou anomalia nesta distribuição.

### 8.1 Avaliação estatística do slide 2 (24/10/2026, mesma carga)

Pergunta do Caio: "acho que a análise está um pouco errada". Resposta curta: **os números estão certos (batem no
banco), mas três leituras do slide exageram ou confundem**: (a) a assimetria de 7 é quase toda de **cards de pacote
criados em lote**, não de orçamentos individuais lentos; (b) a distribuição é **aproximadamente log-normal**, então
comparar com o sino (Q-Q contra a normal) só confirma o esperado; (c) a cerca Q3 + 1,5 × IQR, numa distribuição assim,
marca ~7% como "fora da curva" **por causa do formato**, não por serem casos anormais.

**1. O máximo de 515 h é real no dado, mas não é um orçamento lento.** Os 15 maiores tempos (SQL 6.7.3) são todos
cards **"[Pacote Festival] … Pacote Rock in Rio 2026"**: 515,0 h do "Squad de Talento … In Loco | M (Amplifica) -
Alimentos" (março, não exclusivo) e 14 cards "<talento>_ Pacote Rock in Rio 2026_ Remoto" (abril, exclusivos: Milena,
Maxiane Rodrigues, Samira Sagr, Marciele Albuquerque, Sofia Miranda, Karine Alves, Pedro Rocha, Ludimilla Cianci,
Wanessa Camargo, Bia Reis, Vivi Araújo, Pitel, Milton Cunha, Jonathan) com 482,5 a 483,0 h. Quase todos ficaram
~478 h **num único passo "Em Elaboração", de 07/04/2026 15:33 a 06/07/2026 ~12:45**, criados e movidos juntos: é um
pacote de festival montado e liberado de uma vez, não 15 orçamentos de três meses de trabalho cada. Não é erro de
carga (o passo existe no board), mas **não mede o que o slide diz** ("quanto tempo a equipe leva por orçamento").

- Cards com nome começando por "[Pacote": **74** no universo (3% dos 2.425), **15.816 h = 24,4% de todas as horas**
  da equipe no ano (64.750,6 h); 54 deles estão acima do limite de 62 h (30% dos 179 "fora da curva").
  Por prefixo: [Pacote Festival] 37 (mediana 482 h), [Pacote Casting ViU] 12 (78 h), [Pacote] 9 (477 h),
  [Pacote Efemérides] 7 (138 h), [Pacote Efeméride] 5 (76 h), outros 4.
- **Lotes** (cards criados no mesmo minuto, 5 ou mais): 6 lotes, 77 cards — Pacote Festival 06/04 20:34 (18 cards,
  ~482 h), Nestlé 17/07 e 23/07 (6 e 7 cards, 7–11 h), GWM 18/08 (9 cards, 66,8 h todos), Sesc RJ 17/09 (5 cards),
  **Amazon "Campanha Black Friday" 25/09 16:39 (32 cards, 47,0 h todos)**. O pico estranho da barra 44–48 h
  (71 orçamentos, contra 41 e 18 nas vizinhas) é **esse lote da Amazon** (32 dos 71).

**2. O coeficiente 7 é dominado por poucos casos.**

| Variante (Todos) | n | Mediana | Média | Assimetria | Limite Q3 + 1,5 IQR | % acima | P90 | P95 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Como na tela | 2.425 | 15,2 h | 26,7 h | **7,06** | 61,9 h | 7,4% | 49,6 h | 74,2 h |
| Sem os 74 "[Pacote" | 2.351 | 14,8 h | 20,8 h | **2,82** | 59,1 h | 5,8% | 47,0 h | 64,0 h |
| Só até o limite (sem os 179) | 2.246 | 13,8 h | 17,1 h | 0,98 | — | — | 37,3 h | 47,0 h |
| Em log, ln(h + 1) | 2.425 | — | — | **−0,21** | ≈ 210 h | 1,2% | — | — |

Exclusivos: 7,05 → 3,01 sem pacotes (−0,01 em log); não exclusivos: 7,24 → 2,79 (−0,58 em log). **Tirar 3% dos
cards derruba o coeficiente de 7 para menos de 3**; a mediana quase não muda (15,2 → 14,8 h) e a média cai 6 h. O
coeficiente usa a 3ª potência dos desvios e é muito sensível a extremos: "+7,1" descreve mais os pacotes que a equipe.
Mesmo sem eles a cauda continua forte (≈ 2,8): a conclusão "a maioria é rápida, poucos demoram muito" **se mantém**;
o tamanho do número, não. "Só até o limite" é circular (cortar a cauda sempre reduz a assimetria) e serve só de
referência.

**3. A distribuição é quase log-normal; o Q-Q contra a normal não é um teste útil aqui.** Em log, a assimetria fica
perto de zero (−0,21): os tempos se comportam como produto de fatores (fila × complexidade × esperas), o padrão comum
de tempos de atendimento. Tempos não são negativos e têm cauda à direita, então "não segue a normal" é esperado antes
de olhar os dados; e o critério da tela (módulo do coeficiente acima de 1) é **regra prática**, não teste
estatístico. Com n = 2.425, qualquer teste formal (Shapiro-Wilk, Anderson-Darling) rejeitaria a normal até para
desvios pequenos.

**4. A cerca Q3 + 1,5 × IQR não é adequada como "fora da curva" nessa distribuição.** A regra de Tukey foi pensada
para distribuições perto da simétrica (na normal, marca ~0,7%). Numa log-normal com o centro e a dispersão destes
dados (média 2,69 e desvio 1,11 em ln(h + 1)), cerca de **9–10% passariam de 62 h sem nada de anormal**; aqui passam
7,4%. Ou seja, os 7 em cada 100 são em boa parte o **formato da cauda**, não exceções. Aplicada em log (cerca de Tukey
sobre ln(h + 1)), o limite vira ≈ **210 h** e só **29 cards** (1,2%) ficam de fora — **27 deles são "[Pacote"**:
esses, sim, são casos à parte.

**5. "7 em cada 100 passam de 62 h" está coerente com a conta:** 179 ÷ 2.425 = 7,38% → 7 (maior resto nas 4 zonas),
e "93 dentro do normal" = 100 − 7. Observações: (i) as frases dos passos 2 e 3 usam o mesmo número (`box.fora`) e
ficam sempre iguais; (ii) a X7 (fora da tela) usa meio para cima (`_pontos`): numa carga futura, os dois
arredondamentos podem diferir em 1 ponto para o mesmo grupo; (iii) "pedem atenção, caso a caso" é justo para os 29
acima de ~210 h; dos 179 acima de 62 h, 54 são pacotes e outros 32 cards de um mesmo lote ficam logo abaixo (47 h).

**6. Ressalvas da medida (não do slide):** o "tempo da equipe" é tempo **sob responsabilidade** da equipe em horário
útil, não esforço: inclui a fila (Entrada), "Retorno Marca/Executivo", "Cotação Externa" e o tempo parado de pacotes
(limite 8); só entram os entregues (C4), então orçamentos longos ainda abertos não aparecem (a cauda real dos meses
recentes é maior que a medida); 39 orçamentos têm 0 h (entregues fora do expediente), o que puxa o Q1 para baixo.

**Recomendações (nada foi alterado; decisão do Caio):**

1. **Tratar pacotes e lotes** antes de medir: contar cada pacote/lote como **um** orçamento (mediana do lote) ou
   tirá-los do universo com um contador "N cards de pacote fora" na ficha. O ideal é a gold marcar isso (coluna
   `pacote`/`lote`), em vez de o site depender do prefixo do nome.
2. **Mostrar a assimetria sem pacotes** (≈ +2,8) ou trocar o coeficiente por uma leitura robusta, que não explode com
   poucos casos: "a média é 1,8 × a mediana" (26,7 ÷ 15,2) ou "os 10% mais lentos passam de 50 h" (P90).
3. **Q-Q contra a log-normal** (ou histograma em escala log) se a ideia for mostrar "o que é normal"; contra a
   normal, deixar claro que é ilustração ("se fosse um sino") em vez de "Teste de normalidade".
4. **Limite de "fora da curva" em log** (≈ 210 h, 1,2%), pelo **P95** (74 h, 5%) ou por boxplot ajustado para
   assimetria (Hubert–Vandervieren, medcouple). Se a cerca de 62 h ficar, chamar a faixa de **"acima de 62 h"** ou
   "demorados", não "fora da curva".
5. Usar a mesma função de arredondamento para o "fora da curva" da zona X6 e da X7.
6. A mediana como resposta principal (15 h) **está correta** e é robusta: muda pouco com ou sem pacotes.

## 9. Decisões

**D-SLA-1 a D-SLA-6 (25/10/2026, seção 0.1)**, delegadas pelo Caio a partir da validação do cálculo; itens aprovados
da auditoria SLA-D01, D05, D07–D13, R04, R06, R08, R09, R11, R13, R14, R16, R18.
**D35 (slide 2 do estudo, X1–X7, 24/10/2026)**; D16 (construção slide a slide), D30 (slides 2 e 3, 23/10), D33 (aba "SLA", página única, 24/10) e **D34 (página
redesenhada e estudo "Como medimos", 24/10/2026)**; regras C1–C14 e E1–E3 (PRD, seções 8 e 9.1).

## 10. Histórico da página

| Data | Mudança |
|---|---|
| 25/10/2026 | **D46, movimento do estudo** (seção 0000000000): um gesto de dado por slide (linha do tempo em ~1,1 s, era 2,6 s; barras do histograma, waffle linha a linha, curvas desenhadas, nuvem em camadas, vermelho por último), texto e números sempre visíveis, entrada só na 1ª visita, troca de slide direcional com moldura parada, troca de grupo sem repetir a cena; movimento reduzido idêntico ao anterior; 271 testes. |
| 21/10/2026 | Slide 1 pronto e conferido (C1–C11) |
| 25/10/2026 | **D45, revisão em batalha de agentes** (seção 000000000): base congelada na reunião (`CONGELAR`), `?exemplo=` no slide 1, `tools/conferir_estudo.py` (tudo bate no BigQuery nos 3 grupos) e `tools/conferir_layout.mjs` (sem rolagem nem corte nas 4 telas), Z1/seletor/slide 2/slide 7 com `_h_meta`, slide 3 empilha no celular, % com base escrita (slides 4, 6, 7, 8; achado 5 com "54% de todas as horas"), recorte no topo dos slides 2–8, escape dos nomes do Monday, cartões sem corte, estudo guardado por carga e grupo; 264 testes |
| 23/10/2026 | Ficha criada; divergência de base 2.428 → 2.425 anotada para a auditoria |
| 25/10/2026 | **D42 revista (Caio):** tempo travado = tempo inteiro de quem travou (K4); Todos: Em elaboração 41% · Fila de entrada 19% → "dois pontos", 60%; reconferido no BigQuery nos três grupos; gancho do slide 6 → `#7` |
| 25/10/2026 | **D43:** slide 7 do estudo ("Em que tipo de pedido o tempo trava?", J1–J9; coluna `tipo_de_input` da gold de movimentos); 2ª rodada do Caio (sem nota, faixa curta, cores azul/amarelo/vermelho por regra, letras menores); conferido no BigQuery (seção 0000000) |
| 25/10/2026 | **D44:** slide 8, conclusão do estudo ("O que os dados nos mostraram", Z1–Z8): seis achados das funções dos slides 2–7, onde olhar, o que isso pede; "8 de 8"; 256 testes |
| 25/10/2026 | **D39:** slide 3 do estudo (waffle de 100, chaves A/B, curva acumulada com 2 dias/80%/90%; W1–W7), gancho do slide 2 ligado a `#3`; números conferidos no BigQuery (seção 000) |
| 25/10/2026 | **D41:** slide 5 do estudo (dispersão por mês com os 12 meses do ano, típico, faixa da maioria, linha de 2 dias, % que passa de 2 dias e pedidos por mês; leitura sazonal × padrão por regra U7–U8; U1–U9), gancho do slide 4 ligado a `#5`; números por mês conferidos no BigQuery (seção 00000) |
| 23/10/2026 | D30: rótulo "Prazo" na aba; slides 2 (cauda, C12) e 3 (exclusivos × não exclusivos, C13–C14). Revalidação completa no BigQuery (bate exatamente) |
| 24/10/2026 | Slide 2: faixas de pedidos alinhadas ao slide 1 (29/24/15/17/15) |
| 24/10/2026 | D33: aba "Prazo" → "SLA" (título "SLA de entrega"); página única, sem botões de slide; slides 2 e 3 fora da tela (`leituras()` mantido) |
| 24/10/2026 | **D34:** retirados "Leitura" (C11), "Como a meta é calculada", "No ano (jan a set):", "Medianas de N pedidos…", "(fora do gráfico)"; resposta tipográfica "Levamos X h de trabalho da equipe para entregar um orçamento ao cliente." + "Y dias no calendário para o cliente receber" (leitor de tela informa que é mediana); seletor de talentos abaixo da pergunta; gráfico em trilhos 0–100% por mês com meta 75%, num cartão; lupa "Estudo" no canto do cartão. Estudo "Como medimos" (`/sla/como-medimos`): slide 1 "Como chegamos ao tempo da equipe" (E1–E3), slide 2 "Exploração dos dados" em branco; navegação sempre visível; cabeçalho sem abas, com fechar. Ficha refeita: colunas consumidas (1.1), SQL por número (6.2–6.5), números reconferidos no BigQuery |
| 24/10/2026 | **E1 revisto (Caio):** exemplo do **mês vigente**, sorteado por dia, com a espera do cliente em aberto aceita ("até dd/mm · em aberto", "ainda aguardando"); sem candidato no mês, volta mês a mês. Estudo com visual sóbrio: sem "1 / 2", nome do orçamento só com o nome acima da linha do tempo, regras em cartões flutuantes, faixa marinho no pé com os três números e o gancho (sem botão). Exemplo conferido no BigQuery: [Avatim] Wanessa Camargo, 11h04 (gold 12,16 h com almoço) |
| 24/10/2026 | **D35: slide 2 do estudo "A maioria é rápida. Poucos demoram muito."** (X1–X7): histograma de 4 h com o seletor de talentos em cima, painel chapado em três passos (assimetria, Q-Q, boxplot) com estrutura congelada, conclusão de cada passo na faixa do pé, gancho "E se olharmos para 100 pedidos, o que vemos?"; troca de grupo mantém o passo (`?passo=N`); textos encurtados; botão do próximo passo só com o nome; tabela de comparação dos grupos (X7) **retirada da tela** (segue calculada). Ficha: textos e mapa elemento → regra → campo → SQL (3.2), regras X1–X7 (4), memória (5.5), SQL 6.7, passo a passo (6.8), atualização por carga (6.9), avaliação estatística (8.1). Conferido no BigQuery: **todos os números batem**. 116 testes |
| 25/10/2026 | **Revisão D-SLA-1..6 (seção 0):** mês da 1ª entrega; Retorno Marca fora; meta sugerida 75% em até 3 dias com a faixa "2 a 3 dias"; mês parcial vazado com "até dd/mm"; mediana do mês sob o gráfico; exemplo do dia por hash, no fuso de São Paulo, fim no dia de corte, etapas que fecham no total; estudo: regras novas no slide 1 e cobertura (66%); slide 2 com razão das metades (1,7×), Q-Q sino × log-normal (aderência 0,58 · 0,99; 32 em 100 negativos pelo sino), boxplot em log (limite 210 h; 25/50/24/1; 12 em 100 passam de 5 dias; 27 dos 28 fora da curva são pacotes); moldura congelada com o SLA; texto de SVG ≥ 11 px; "Recomeçar". Números novos: Todos 14 h · 2,8 dias · 31/25/15/29 (2.348); exclusivos 12 h · 2,0 · 37/25/14/24 (1.610); não exclusivos 20 h · 4,0 · 18/23/20/39 (725). Conferido no BigQuery: idêntico |
| 25/10/2026 | **Tarde, moldura no celular:** no estudo "Como medimos" o rodapé "Dados até…" ficava numa faixa fixa entre o slide e os botões, por cima do conteúdo que rola; agora vai para o fim do slide visível e acompanha a troca de slide (`apresentacao.js`, decisão 14 estendida a páginas de vários slides; "Próxima pergunta" não existe no estudo). Computador sem mudança. Mês futuro (nov/dez) do gráfico já em itálico `--tinta-3` (IN-A1, `.sla-corpo .mes-futuro .mes-rotulo`, #6b6b80 ≈ 5,2:1 no branco); no celular os meses futuros não aparecem (como no Início). 152 testes |
| 25/10/2026 | **Tarde, slide 2 do estudo legível (Caio):** passo 2 mantém os dois Q-Q (pedido do Caio) com eixos em horas nomeados ("tempo real ↑", "previsto pela curva →"), rótulos diretos ("na linha: a curva acertou", "acima da linha: demorou mais", "longe da linha: o sino errou", "abaixo de 0 h: impossível (32 em 100)"), título-pergunta, frase "o que mostra", selo "Encaixe na linha" e a tradução de log-normal; passo 3 com boxplot horizontal maior, quantidade e nome sobre cada zona, limites em horas reais, "Como ler"; **X8** (pergunta da gerente): com todos → sem os 28 fora da curva (mediana 14 → 14 h, −0,3 h; 71% → 72%; média 25 → 20 h; P90 46 → 43 h), conferido no BigQuery (0.6.4); faixa do pé do passo 2 reescrita como consequência ("A cauda longa é natural do processo…"). Testes 156 |
| 25/10/2026 | **Noite, slide 2 refeito pela referência do Caio (seção 0.8):** histograma fixo com blocos até 2 dias / 2 a 5 dias / mais de 5 dias; painel com assimetria (Fisher-Pearson +7,2, régua com quebra), Q-Q contra a normal (pontos acima do limite em vermelho), boxplot de Tukey linear (limite 59 h; 25 · 50 · 18 · 7); KDE de Silverman e curva normal no passo 2; faixa de conclusão clara; sem seletor de talentos na tela; log-normal, razão das metades, halteres/X8 e X7 fora da tela. **Quadro 4 retirado a pedido do Caio; a curva acumulada vai para outra página** (P50/P80/P90 seguem calculados). Faixa de conclusão mais baixa, letras menores e mais leves no histograma e no painel, painel da altura do histograma com a faixa logo abaixo (disposição da referência 85; pedidos do Caio). Conferido no BigQuery (0.8.1). 157 testes |
| 25/10/2026 | **Quadro 1, conclusão analítica (Caio):** a faixa passa a ter duas colunas, como o quadro 2: "O que o gráfico mostra: {% até 2 dias}% saem em até 2 dias; poucos esticam a cauda até {máximo}. Assimetria {coef}, positiva (acima de 1 já é cauda forte)." \| "O que isso quer dizer: a cauda puxa a média para {média}; {% abaixo da média}% ficam abaixo dela. O típico é a mediana, que divide os orçamentos ao meio: {mediana} de trabalho." Tudo vem do cálculo (`faixas3.pcts[0]`, `max_txt`, `assim.txt/coef/positiva`, `media_txt`, `abaixo_media`, `mediana_txt`); variantes para distribuição quase simétrica e média próxima da mediana. Hoje: 56% · 515 h · +7,2 · 25 h · 73% · 14 h. Faixa e gancho com letra menor para caber acima da navegação. 157 testes |
| 25/10/2026 | **Slide 2 (Caio):** faixa do quadro 1 em tom de mensagem, sem repetir o painel ("A maioria dos orçamentos fica pronta rápido; poucos demoram muito e puxam a média para cima. Do mais rápido ao mais lento, o orçamento do meio leva {mediana} de trabalho: esse é o nosso tempo típico."); painel explica assimetria positiva × negativa no processo; **seletor de talentos de volta** (pergunta da diretoria), no desenho da página do SLA, em cima do histograma, com a mediana de cada grupo (`comparacao[].mediana`) e mantendo o passo; histograma mais baixo (H 330 → 292) para caber. 157 testes |
| 25/10/2026 | **Q-Q do quadro 2 corrigido (Caio):** os dois eixos na mesma escala de horas (reta = "real = previsto pelo sino"), teto em ~8% acima do maior entre o maior previsto e o P97 real (casos acima ficam presos no topo, "↑ N casos acima do gráfico"), previsão negativa sombreada ("< 0 h"), marcas em horas; pontos nas cores das faixas do histograma (até 2 dias · 2 a 5 · mais de 5); legenda didática: "A reta: o esperado pelo sino" · "Abaixo da reta: saiu mais rápido" · "Acima da reta: demorou mais". Faixa de conclusão em letra de rodapé nos 3 passos; passo 2 em tom de mensagem. 157 testes |
| 25/10/2026 | **Noite, slide 1: linha de cobertura retirada da tela a pedido do Caio; cobertura segue documentada** (D-SLA-4, 0.3 e 0.6.3; `cobertura()` mantido) |
| 25/10/2026 | **Q-Q v4 (Caio: "não existe dado abaixo de 0 h", "tem vermelho abaixo da reta", "proporção das cores"):** eixos a partir de 0 h, sem a área sombreada; os 200 quantis viram **bolinhas proporcionais** (quantis vizinhos da mesma faixa a < 6 px viram uma bolinha, área ∝ quantidade; soma = 200); os quantis em que o sino previa menos de 0 h (32 em 100 em Todos) ficam juntos numa bolinha azul em 0 h. Legenda só da reta, numa linha com a nota ("bolinha maior = mais orçamentos · a de 0 h junta N em 100…"); setas acima/abaixo retiradas porque a cor (tempo real) e a posição (contra o previsto) confundiam. Quadro 340 × 118, largura toda do painel. 157 testes |
| 25/10/2026 | **Passo 2: Q-Q trocado pelo espelho (X5b, Caio: "tem vermelho abaixo da reta", "uma forma fácil visual").** Diagnóstico: o sino do Q-Q usava média 25,4 h e desvio 53,4 h, inflado pela cauda; ele previa 94 h na posição 90 de 100, contra 46 h reais, então os demorados caíam abaixo da reta e escondiam a própria cauda. Novo quadro `_espelho(h)`: para N = 25, 10, 5, 1, braço rápido = P50 − P(N) e braço lento = P(100−N) − P50; num sino seriam iguais. Carga 23/10, Todos: 8 h × 13 h · 12 h × 32 h · 14 h × 57 h · 14 h × 463 h (10 mais lentos = 2,6× os 10 mais rápidos). Tracejado = onde o sino pararia; vermelho = o que o lado lento passa dele; escala até 4× o maior braço rápido, braço maior cortado (//) com o valor escrito. `_qq` fica no código, fora da tela. 158 testes |
| 25/10/2026 | **Q-Q de volta (v5), pelo sino do meio (Caio não gostou do espelho; "quero a dispersão perto da reta, fácil de explicar").** A reta passa a ser a normal com a mediana e a largura da caixa (IQR / 1,349; padrão do qqline do R), não mais com a média e o desvio. Carga 23/10, Todos: o sino do meio prevê 14 h no meio (real 14 h), 34 h na posição 90 (real 46 h), 51 h na 99 (real 477 h): o meio cai na reta e a cauda sobe acima dela. Cores pelo critério do passo 3: azul = até o limite de Tukey (59 h), vermelho = fora da curva. Horas escritas sobre a reta (20/40/60 h); eixo y até ~10% acima do P97, com "↑ N ainda mais longe". Bolinhas proporcionais mantidas; os quantis com previsão < 0 h (18 em 100) ficam numa bolinha em 0 h. `_espelho` fica no código, fora da tela. A correlação do teste (`normal`) não muda, porque é invariante à escala da reta. 158 testes |
| 25/10/2026 | **Slide 2 entregue (Caio).** Faixa do passo 2 sem os parênteses "(7 em cada 100 passam de 59 h)" e "(25 h)": "…a maioria sai rápido e poucos demoram muito. Por isso a média não representa o orçamento comum; o do meio, 14 h, representa." 158 testes |
| 25/10/2026 | **Passo 3 (boxplot) mais limpo (Caio).** Zona 4 do boxplot passa a se chamar "outliers". Legenda nova, com o que cada faixa quer dizer e os números do recorte: Rápidos (até Q1: o quarto mais rápido) · Comuns (Q1 a Q3: a metade do meio, a caixa) · Ainda normais (até o limite: demoram mais, mas dentro do esperado) · Outliers (acima do limite: fora da curva, olhar caso a caso; some quando não há). Saíram da tela a conta do limite ("fim da caixa + 1,5 × …", segue nesta ficha), a linha de nomes sob o boxplot e a legenda sob o histograma ("horas de trabalho da equipe… · cada barra…"); o histograma ganhou os 20 de altura (580 × 312) para o painel manter a altura. Fontes menores (números 13 px, valores 9,5 px). Faixa do pé: "De cada 100 orçamentos, N saem dentro do esperado, em até L; M são outliers: demoram bem mais que o normal e merecem um olhar caso a caso." Carga 23/10: Todos 93/7, até 59 h; Não exclusivos 91/9, até 64 h. 158 testes |
| 25/10/2026 | **D38 (Caio): meta sugerida = metade em até 2 dias de trabalho (16 h)** (D-SLA-7, revisa a D-SLA-3). Página SLA: faixas até 1 dia / 1 a 2 dias / acima de 2 dias (sai "2 a 3 dias"), linha em 50% "meta sugerida: 2 dias úteis", mensagem do típico pela mediana exata (16,3 h fica fora), "N% passam de 5 dias de trabalho (M orçamentos)", números das faixas e "PARCIAL" que encolhem até caber (container query). Estudo: slide 1 com dias de trabalho × meta, "dias corridos", "Espera do cliente" e gancho condicional; slide 2 com "na meta" no topo, tracejado = sino do meio (KDE fora da tela), Q-Q com 88 de altura e "↑ N orçamentos acima de T h" contando orçamentos reais, boxplot com "demorados" e "outliers", % do total ("Dos 2.348 orçamentos entregues de jan a set"), marca da meta fora da caixa com nota, insight por passo na faixa do pé só com números visíveis no gráfico do passo (seção 00.2; passo 3 sem horas consumidas; Q-Q com o ponto dos 10% mais lentos marcado). Todos 56% em até 16 h · 12% acima de 40 h · 7% outliers (171, 42% das horas); Exclusivos 62 · 10 · 7 (111, 46%); Não exclusivos 41 · 16 · 9 (63, 37%), típico 20 h, 4 h acima. 170 testes |
| 25/10/2026 | **D38, passo 3 final (Caio):** faixa "R+C% dos orçamentos saem em até Q3: os rápidos e os comuns. Outros D% demoram mais, até L, mas seguem o padrão do processo. F% (n orçamentos, k deles pacotes) são outliers, fora da curva: vamos olhar caso a caso." (sem "na meta", sem horas consumidas); nota de rodapé de 1 linha só no passo 3 ("Consideramos dentro do padrão os tempos até L: o fim da metade do meio (Q3) mais uma folga de uma vez e meia a largura dela."); legenda do boxplot sem números (Rápidos: o quarto que sai mais rápido · Comuns: a metade do meio, onde está o típico (a caixa) · Demorados: levam mais que a maioria, mas seguem o padrão do processo (a haste) · Outliers: fora da curva (os pontos)); quantidades e horas seguem no aria-label. 170 testes |
| 25/10/2026 | **D38, linguagem simples (Caio):** nota do passo 3 "Chamamos de padrão os tempos até L: é até onde vai a grande maioria dos orçamentos, com uma margem de folga. Acima disso, o tempo foge do ritmo da equipe."; legenda do boxplot sem números nem termos técnicos (Rápidos: saem antes da maioria · Comuns: o tempo de sempre da equipe · Demorados: levam mais, mas ainda no padrão · Outliers: fogem do padrão: olhar caso a caso); regra Q3 + 1,5 × IQR só na ficha e no aria-label. Faixas dos passos 1–3 revistas: sem "mediana", "caixa", "desvio", "percentil". 170 testes |
| 25/10/2026 | **Q-Q do passo 2 (Caio):** saiu a marca dos 10% mais lentos (anel + "10% mais lentos: 46 h · sino: 34 h"; `_marca_p90` fica no código). Na reta, em vez de 20/40/60 h, os cortes das faixas do histograma: "2 dias" (16 h) e "5 dias" (40 h). Faixa do pé do passo 2 sem números fora do gráfico: "Até 2 dias, os orçamentos andam junto da reta, no ritmo previsto. Depois disso, os demorados se afastam dela, e quanto mais demoram, mais longe ficam. Por isso a meta se apoia no típico, e os demorados são tratados à parte." 170 testes |
| 25/10/2026 | **Slide 3, layout (Caio):** o seletor de talentos sobe e fica sozinho acima de tudo (ele filtra a tela toda); embaixo, o quadro de 100 com a legenda e a curva acumulada ficam lado a lado em duas colunas iguais, centradas na mesma área. O bloco do meio deixou de ter altura fixa e a curva ganhou um teto de altura (14em): em tela larga e baixa, a faixa e o gancho caíam sobre a navegação. Conferido em 1920×1000 e 1280×800. |
| 26/10/2026 | **D54 (Caio e gerente):** rótulo da meta curto e numa linha ("meta sugerida: 2 dias de trabalho"), na linha do título do cartão na mesa e sobre a linha no celular; C3c — dias úteis com fração no número de apoio e no slide 1 (Todos 1,8 · Exclusivos 1,6 · Não exclusivos 2,5; BigQuery = app); `expediente.dias_uteis_fracao`, `calculos.dias_uteis_cliente`; `tests/test_sla_d54.py`; seção 000000000000. 454 testes |
| 26/10/2026 | **Batalha 2, documentação (D49):** bloco "Estado vigente" no topo no lugar das nove linhas de "Situação" (regras que valem, mapa das seções com zeros, números da carga da reunião de 26/10 por elemento da tela, função e SQL, conciliação 5.556 → 3.969 → 2.347); seções 2 e 4 marcadas onde a regra mudou (C3 → C3b, C4 → D-SLA-1, C6 → D38, E1 pelo mês da 1ª entrega); `DOIS_DIAS_H` trocada pela `META_H` em `sla/calculos.py` (mesmo valor, 16 h); `tools/conferir_entrega.py` para `_descartados/`. Renumeração das seções fica para depois de 28/10 |
| 27/10/2026 | **D57:** fim da exceção C2: as entregas (C1–C4, C3b, C3c, C9, C14) e as horas por status (K1) vêm das views gold `gld_agenciamento_2026_sla_entregas` e `..._sla_entregas_status`; o exemplo do slide 1 usa `sla_sem_almoco_horas` (R24); `app/expediente.py` ficou só com o calendário; página e estudo iguais na mesma carga |
| 29/10/2026 | **D64 (Caio):** o slide 7 do estudo ("Em que tipo de pedido o tempo trava?") saiu da apresentação: `ESTUDO_TIPO = False` em `apresentacao.py` (código e cálculos J1–J9 mantidos; `True` traz de volta). O estudo passa a 7 slides, a conclusão é o #7, o gancho do slide 6 vira "E o que os dados nos mostraram?" e a conclusão perde o achado por tipo (5 achados). Cola (`../PPD-AGENCIAMENTO-COLA/cola.js`): ficha `estudo-7` comentada, `estudo-8` aponta para o #7. Falas da cola do SLA e do estudo reescritas com o Caio (sem veredito, a diretoria conclui). 498 testes |
