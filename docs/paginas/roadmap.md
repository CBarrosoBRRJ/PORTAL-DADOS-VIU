# Roadmap da área (V2)

**Estado (31/10/2026, noite): 5ª versão, "a linha do tempo linear em Y", num painel flutuante.** O Roadmap é a tela
que abre a reunião e o **hub de navegação**: o gerente do Caio apresenta a partir dela, clica num destino e volta pelo ✕
do cabeçalho das páginas. A 4ª versão ("a linha que desemboca nos destinos", leque de curvas e miniaturas espalhadas)
foi reprovada ("horrível, confusa, não elegante, poluída") e está em `_descartados/2026-10-31/roadmap_v4/`. A nova
partiu da referência 4 do Caio (linha horizontal fina, pontos, textos alternando acima e abaixo, muito branco) e foi
refinada em várias rodadas com ele no mesmo dia ("estamos chegando perto"; "para entrega já está bom").

**Cabeçalho:** selo "Gerencial" (padrão das páginas), título "Como chegamos até aqui?", sem as abas, com ‹ › ✕ (no
Roadmap o ✕ leva à capa; `macros.html`, fora desta página). Rodapé datado e gancho oculto mantidos.

## Estrutura (Caio, 31/10/2026)

```
01 Dados espalhados ─ 02 Mapeamos ─┬─ 04 Pedimos à TI ┄┄┄┄ Aguardando ┄┄┄┄ 05 Infraestrutura liberada ─┐
                                   └────────── 03 Criação de dashboards ───────────────────────────────┴─
─ 06 Centralizamos no BigQuery ─┬── 08 Novos dashboards e melhorias ┄┄┄┄┄┄┄┄┄┄┄┄┄┄ ›
               ↖ retroalimenta a base      ↑ estudo vira dashboard          Evolução contínua
                                └── 07 Análises e estudos (Você está aqui + botões) ┄┄┄┄┄┄ ›
```

- **Três trilhos** horizontais: o principal ao centro e os ramos 2,9 em acima e abaixo; junções em curvas suaves.
- **1º Y:** "Pedimos a infraestrutura à TI" logo depois da curva de abertura e "Infraestrutura liberada" logo antes da
  curva de volta, para o trecho âmbar tracejado **"Aguardando"** ocupar quase todo o ramo (a espera). "Criação de
  dashboards" no meio do ramo de baixo; é o **03** porque começou antes do pedido (numeração ramo a ramo).
- **Depois do BigQuery:** dois trilhos **contínuos** até a borda, sem nó final e sem bandeira de chegada (seta suave em
  cada um e o rótulo "Evolução contínua" entre eles): **Análises e estudos** ("Você está aqui", em curso) e
  **Novos dashboards e melhorias** (em curso: criação e melhoria, refeitos sobre a base central; antes "Desenvolvimento de dashboards", o Caio pediu um título resumido). A linha é cheia até esses nós e tracejada depois.
- **Retroalimentação** em pontilhado fino, com ponta pequena, rótulo pequeno em itálico e um ponto que corre devagar:
  de Análises e estudos de volta ao BigQuery ("retroalimenta a base", pela abertura do Y) e de Análises para Dashboards
  ("estudo vira dashboard", curva suave para cima).
- **Iniciativas e Previsão** nascem dos estudos: ficam no conjunto de botões de Análises e estudos, marcadas "próximo".

**Regra do texto (para leitura previsível):** nó do ramo de cima → título acima da linha; nó do ramo de baixo → título
abaixo; nós do tronco alternam, começando por cima, e, se o lado da vez bater num título de ramo, vão para o outro lado
(hoje: 01 acima, 02 abaixo, 06 abaixo, porque acima dele está o 05). **Número pequeno em cima e nome logo abaixo,
centrados juntos no eixo do ícone**, numa largura padrão (`TITULO` = 9,8 em; quebra equilibrada em até 2 linhas),
encolhida por igual dos dois lados só se encostar no título vizinho do mesmo lado (folga mínima de 0,8 em, conferida no
teste). Os títulos de cima formam uma fileira (mesma base) e os de baixo outra (mesmo topo); nós do tronco ou deslocados
ligam-se ao título por uma haste fina. Miniaturas e chips ficam centrados no mesmo eixo do nó; os botões, presos ao 07,
começam junto do título dele.

**Respiro no eixo vertical (regra):** os nós não ficam todos na mesma altura; cada nó pode ter um deslocamento `dy`
(em em) e a linha acompanha com curvas suaves; os títulos continuam nas fileiras (a haste se ajusta). Hoje: 02 desce
1,2 em; 03 sobe 0,7 em no ramo de baixo; 06 sobe 0,5 em. Os trilhos da espera ficam
retos (a espera se lê como uma linha só).

**Só número + título por nó** (Caio, 31/10/2026). Frases retiradas, para registro: 01 "Em planilhas e até em contas
pessoais."; 02 "O processo de ponta a ponta."; 03 "Com o que já tínhamos, durante a espera."; 04 "Um projeto no GCP.";
06 "Tudo num lugar só, no GCP."; 07 "Este portal."; 08 "Refeitos sobre a base central." (o título do 08 era
"Desenvolvimento de dashboards" e virou "Novos dashboards e melhorias"); e o antigo nó final "Próximos
passos" ("Evolução contínua, sem linha de chegada."), que virou o rótulo "Evolução contínua" do fim dos trilhos.

## Chips, miniaturas e botões

- **Chips das fontes** (enfeite, `aria-hidden`), centrados sob o ícone do 01, em fileiras que não
  se sobrepõem, com leve inclinação e flutuação defasada; um tom pastel por ferramenta, sem logo (texto ≥ 6:1):
  SharePoint (verde-azulado), Excel (verde), Monday (coral), OneNote (roxo), Salesforce (azul-céu), API (cinza-azulado)
  e **Req2Pay** (amora; o relatório de pagamentos do PDF do mapeamento; o Caio falou "Hack to Pay" e confirmou Req2Pay).
- **Miniaturas** ("janelas" de 5 em com moldura fina, levemente inclinadas, endireitam no mouse ou no foco): fluxo em
  02, pilha Pagamentos + Contratos em 03 (galeria com ‹ › e ← → no painel) e BigQuery em 06. Clique, Enter ou Espaço
  abrem o `<dialog>` (Ver em 100%, Abrir em tamanho real). Sem JS, o link abre a primeira imagem.
- **Botões** (compactos: ícone num círculo + nome; a linha de apoio só para o leitor de tela), presos a Análises e
  estudos, **por categoria** (`CATEGORIAS` em `roadmap/__init__.py`; no máximo três tons, e a forma do círculo do ícone
  muda por categoria):

| Categoria | Tom / forma | Botão | Endereço |
|---|---|---|---|
| Análises | azul / círculo | Demanda | `/viu-agenciamento` |
| Análises | azul / círculo | Talentos | `/viu-agenciamento/talentos#1` |
| Análises | azul / círculo | SLA | `/viu-agenciamento/sla#1` |
| Automação e IA | roxo / quadrado | LIA | `/viu-agenciamento/lia#1` |
| Automação e IA | roxo / quadrado | Iniciativas (próximo) | `/viu-agenciamento/iniciativas#1` |
| Projeções | verde-azulado / gota | Previsão (próximo) | `/viu-agenciamento/previsao#1` |

  Uma página nova entra com **uma linha** em `botoes` (e, se preciso, uma categoria nova). Cada categoria é uma coluna
  de até 4 botões que cresce para o lado (testado com 10 destinos fictícios). Colagem organizada (rotações de ±1,5°,
  pequenos deslocamentos por `nth-child`, flutuação defasada); no mouse ou no foco o botão endireita, sobe, ganha brilho
  na borda no tom da categoria, e o nó 07 acende. **Deriva dos botões (F19, 31/10/2026, Caio: "colagem com movimento",
  sem parar):** duas camadas, a normal no `<li>` (`rm-deriva-botao`, 7–8 s, até 2 px, mais suave que os ~3 px de antes)
  e a lenta no botão (`rm-deriva-lenta`, 21 s, 3× mais lenta); com o ponteiro sobre o grupo (`.rm-categorias:hover`) ou
  um botão em foco (`:focus-within`), a amplitude passa da normal (2 px) para a lenta (1 px) numa transição de 900 ms
  das propriedades registradas `--rm-amp`/`--rm-amp-lenta` (`@property`), sem salto. Os chips decorativos seguem com a
  `rm-deriva` de antes. Conferido com clique real (mouse) nos 6 destinos, sem esperar o movimento parar: 6/6 navegaram;
  deslocamento medido em 4 s: 1,6 px sem o ponteiro, 0,2 px com o ponteiro. Teste: `tests/test_seguranca_iniciativas.py`. Altura 2,3 em (≥ 32 px a 1280 × 720). Em 390 px: lista simples.

## Painel, fundo e movimento

- **Painel flutuante:** a lâmina é branca; todo o fluxograma fica num cartão grande (lavanda-claríssimo, vinheta suave,
  grade de pontos quase imperceptível, contorno leve, sombra em camadas maior que `--cartao-sombra`, cantos de 22 px).
  O palco (73 × 28 em) entra a 92%, centrado; o painel avança 2,6 em sobre as margens laterais da lâmina (chips e
  títulos a ≥ 1,5 em da borda do painel). **Linha cheia** mais presente (Caio: "muito fininha"): traço de ~3,5 px a
  1440, degradê suave do marinho ao azul VIU ao longo do caminho, halo difuso muito leve e pontas arredondadas; a espera
  (âmbar) e os trilhos contínuos seguem tracejados e o pulso corre por cima. Comparação em
  `.playwright-mcp/rm5-antes-linha-1440x810.png` × `rm5-final-1440x810.png`: ficou claramente melhor, mantida.
- **Movimento** (só com `prefers-reduced-motion: no-preference` e `html.js`; loop permitido só no bloco `.rm-*`,
  exceção em `tests/test_movimento.py`): a linha se desenha na entrada e os nós surgem em sequência; o pulso corre pelos
  dois ramos em 9 s (devagar no "Aguardando") até a borda; **quando o pulso passa por um nó, um anel fino se abre em
  volta dele** (o atraso de cada nó, `--pulso`, e os quadros-chave do pulso, `rm-anda-1`/`rm-anda-2`, são calculados em
  `tela()` com a mesma rota e vão no `<style>` com nonce, então ficam sincronizados mesmo se a geometria mudar); cada
  ícone tem o seu gesto em loop lento (peças que se afastam e voltam, o fio do fluxo, a ampulheta que vira, a barra que
  respira, as camadas do banco em sequência, a seta que sobe, o lápis que escreve; mais rápido no mouse ou no foco); o
  tracejado âmbar marcha; chips, miniaturas e botões flutuam defasados; um ponto corre pelas setas de retroalimentação.
- **Cliques** (Caio relatou "os botões não navegam"): os nós (`li`) e as camadas decorativas (SVG, rótulos, chips,
  hastes, etiqueta, espera) têm `pointer-events: none`; só links, miniaturas e o círculo do nó recebem o ponteiro.

## Dados e geometria

`roadmap/__init__.py`: `PASSOS` (nós do tronco e bifurcações, com `peso` de largura, `pos` no ramo, `dy`, `alinhar`,
`larg`, `espera`, `aqui`, `botoes`, `registros`, `soltos`, `mostrar`), `CATEGORIAS`, `RETROS` e `CONTINUO`. `tela()`
calcula posições, larguras dos textos sem sobreposição, trechos de linha (cheia, âmbar, tracejada), setas, rotas e
quadros do pulso e as curvas da retroalimentação. O SVG tem viewBox 730 × 280 (0,1 em). `mostrar: False` tira um nó; uma
bifurcação com um ramo só volta ao tronco. Abaixo de 900 px, linha vertical.

## Validação (31/10/2026, noite: 5ª versão)

- `python -m pytest tests -q -p no:cacheprovider` na V2 (testes do Roadmap reescritos em `tests/test_v2_paginas.py`:
  estrutura, posições, regra do texto, pulso, cliques, categorias, 10 destinos, miniaturas, `mostrar`, escala).
- Capturas em `.playwright-mcp/rm5-*.png` (1440 × 810, 1280 × 720, 1920 × 1080 sem rolagem; 390 px sem rolar para o lado).
- Clique real no Chrome headless (mouse do DevTools): os 6 destinos navegam e as 3 miniaturas abrem o painel, em
  1440 × 810, 1280 × 720 e 390 px; `elementFromPoint` no centro de cada um devolve o próprio link.
- Na captura, sem sobreposição: os retângulos de títulos, miniaturas, categorias de botões, chips, rótulos da
  retroalimentação, "Evolução contínua", "Você está aqui" e "Aguardando" não se cruzam, nenhum passa da borda do painel e
  nenhum título passa de 2 linhas (1440 × 810, 1280 × 720 e 1920 × 1080).

---

**Histórico das versões anteriores (abaixo, como registro).**

## 4ª versão, "a linha que desemboca nos destinos" (31/10/2026, tarde; substituída)

**Estado (31/10/2026, tarde): 4ª versão, "a linha que desemboca nos destinos".** O Roadmap é a tela que abre a reunião
e o **hub de navegação**: o gerente do Caio (que não é da área) apresenta a partir dela, clica num destino, apresenta a
página e volta pelo ✕ do cabeçalho. Retorno do Caio sobre a versão executiva: ainda "poluída", "estranha" e sem a
linguagem das outras páginas. A versão executiva está em `_descartados/2026-10-31/roadmap_v3/`; a colorida em
`_descartados/2026-10-31/roadmap_colorido/`; a diagonal em `_descartados/2026-10-30/roadmap_diagonal/`.

**Conceitos avaliados (31/10/2026):**
- A, "linha do tempo + grade de destinos": a linha enxuta em cima e, embaixo, seis cartões grandes de navegação.
  Claro, mas é a grade de cartões de qualquer painel, e a linha vira enfeite separado dos botões.
- **B, "a linha que desemboca nos destinos" (escolhido):** a história corre da esquerda para a direita numa linha fina
  e termina no "Você está aqui", de onde se abre em leque até os botões das páginas, à direita. A linha liga a história
  aos destinos (o que a gente fez leva ao que a gente mostra), conversa com a capa (lá as linhas convergem; aqui se
  abrem) e deixa os botões grandes, à direita, no lugar onde o olho termina.

**Composição (palco de 73 × 27,5 em; 1 em = 1/80 da lâmina):**
- **História (0 a 42 em):** linha a 9,4 em do topo; marcos como **pontos** (sem ícone e sem número: a ordem é a da linha
  e da lista `<ol>`); por etapa, só a situação (ícone + texto), o título em Playfair e uma frase. Na infraestrutura, a
  linha se abre: o pedido e o "liberado" acima, com a espera em âmbar tracejado entre eles; embaixo, o ramo paralelo
  ("Enquanto esperávamos…", "Dashboards com o que já tínhamos") volta à linha antes do BigQuery. Os chips soltos
  (SharePoint, Excel, Monday, OneNote) flutuam acima da partida.
- **Você está aqui (46,5 em):** o único marco grande e cheio (azul VIU, com o ícone e as ondas).
- **Destinos (53 a 73 em):** "Estudos e análises" (com a etiqueta amarela "Você está aqui") e "Próximos passos"; botões
  de 3,1 em com ícone cinza, nome em Playfair, uma linha e a seta ›. O leque é cheio até os estudos e tracejado até os
  próximos passos; o leque do botão sob o mouse ou o foco acende em azul (`:has`, classes `rm-l0` a `rm-l7`).
- **À vista:** a história inteira em uma frase por etapa, as quatro miniaturas e os seis destinos.
  **Sob demanda:** as imagens ampliadas no `<dialog>` (com "Ver em 100%" e "Abrir a imagem em tamanho real").
  **Fora da tela (cortados nesta versão):** números 01–06, "Risco de perda" como selo (virou parte da frase da etapa 1),
  as camadas Bronze/Prata/Ouro como bolinhas (viraram a frase do BigQuery), o selo "Ponto de espera", a legenda
  "quando liberou…" e os ícones dentro dos marcos.

**Destinos (botões):**

| Grupo | Botão | Linha | Endereço |
|---|---|---|---|
| Estudos e análises | Demanda | Pedidos de orçamento em 2026 | `/viu-agenciamento` |
| Estudos e análises | Talentos | Exclusivos e não exclusivos | `/viu-agenciamento/talentos#1` |
| Estudos e análises | SLA | Tempo até a entrega do orçamento | `/viu-agenciamento/sla#1` |
| Estudos e análises | LIA | E-mails que a LIA já leu | `/viu-agenciamento/lia#1` |
| Próximos passos | Iniciativas | Automação e IA em andamento | `/viu-agenciamento/iniciativas#1` |
| Próximos passos | Previsão | Pedidos esperados até o fim do ano | `/viu-agenciamento/previsao#1` |

**Ida e volta:** cada botão é um link comum para a página; nas páginas, o ✕ do cabeçalho volta ao Roadmap (bloco
`.cab-passo`, sem mudança aqui). A seta → e o gancho oculto do Roadmap seguem para a Demanda.

**Regra de dados:** etapa **sem** `botoes` fica na linha da história; etapa **com** `botoes` vira um grupo de destinos na
coluna da direita (`aqui: True` marca o grupo onde a linha desemboca). `mostrar: False` tira a etapa. Geometria em
`roadmap/__init__.py` (`HISTORIA`, `NO_AQUI`, `COLUNA`, `LINHA`, `RAMO`, `CABECA`, `BOTAO`, `VAO`, `ENTRE`), a mesma do
bloco `.rm-*` do CSS; o SVG tem `viewBox 730 × 275` (1 unidade = 0,1 em, sem distorção). Escala: de 4 a 8 etapas
(`rm-v1` a `rm-v8`, `rm-s0` a `rm-s7`).

**Movimento (só com `prefers-reduced-motion: no-preference` e `html.js`):** pulso na linha pelos dois ramos (devagar na
espera), chegando ao "Você está aqui" e seguindo pelo leque até cada estudo (ciclo de 8 s); ondas no marco atual; chips à
deriva; barras do ícone atual; marcha dos tracejados; botões sobem 1 px no mouse e a seta › anda. Sem brilho no pulso.

**Direção de arte (skill `design-taste-frontend`, 31/10/2026):** tela de app (hub), estilo `achromatic-ledger`
(semente 511015409, `--keep palette,type`): o cromo em tinta e cinza; a cor só na linha, no pulso e no "Você está aqui".
Conflitos com o pedido do Caio, mantidos de propósito: sombra em camadas nos botões (`button-fx`), azul VIU `#2400ff`
(`palette-purple`), chips com sombra leve, o selo "ROADMAP" em caixa alta do portal (`micro-label`). O texto abaixo de
11 px no celular que o inspetor aponta é do cabeçalho comum do portal, fora desta página.

## Validação (31/10/2026, tarde: 4ª versão)

- `python -m pytest tests -q -p no:cacheprovider` na V2: testes do Roadmap reescritos (`test_roadmap`,
  `test_roadmap_enxuto`, `test_roadmap_botoes`, `test_roadmap_registros`, `test_roadmap_mostrar_oculta_etapa`,
  `test_roadmap_escala_ate_8_etapas`).
- Capturas (Chrome headless) em `.playwright-mcp/v4d-*.png`: 1440 × 810, 1280 × 720 e 1920 × 1080 sem rolagem (a lâmina
  termina antes do rodapé), 390 px sem rolar para o lado; foco no teclado e painel ampliado conferidos.
- Texto miúdo da página ≥ 11 px em 1280 × 720 e em 390 px (medido no navegador).
- `inspect.mjs --app` (skill): antes, 4 FAIL e 5 WARN; depois, 1 FAIL (texto do cabeçalho comum no celular) e 3 WARN
  (selo do portal, margem do celular e título do cabeçalho), com `--allow button-fx,palette-purple` pelos pedidos do Caio.


## Versão executiva (31/10/2026, manhã; substituída)

**Estado (31/10/2026): versão EXECUTIVA.** Retorno do Caio sobre a versão colorida: "informação demais",
"carnavalesco" e sem a linguagem das outras páginas. A versão colorida está guardada em
`_descartados/2026-10-31/roadmap_colorido/`.

O que mudou:
- **Fundo e caixas:** fundo branco das outras páginas, sem manchas, aros nem cartões de vidro.
- **Paleta:**
  - linha fina em degradê `#a3ace4` → marinho;
  - marcos nos azuis do projeto;
  - âmbar só na espera; amarelo só na etiqueta pequena do "Você está aqui".
- **Textos soltos, sem caixa:**
  - número em Playfair itálico `#5566cc` e situação pequena com ícone;
  - título em Playfair 500 e uma frase em `--tinta-2`;
  - a situação aparece uma vez por etapa: o "liberado" e o ramo paralelo não repetem o "Feito".
- **O mínimo por etapa:**
  - a etapa 2 sem itens;
  - camadas numa linha só (Bronze, Prata, Ouro);
  - Próximos passos com 2 itens;
  - chips soltos só na etapa 1, discretos.
- **Linha mais baixa:** a 13 em do topo do palco; o ramo paralelo a 19 em; o SVG agora tem `viewBox 1000 × 320`.
- **Ficaram:**
  - a linha contínua com o pulso;
  - a bifurcação;
  - as ondas no marco atual e os micro-movimentos dos ícones;
  - as miniaturas que ampliam;
  - os botões no padrão do portal.

**Estado (30/10/2026, noite):** linha do tempo HORIZONTAL, base no protótipo A escolhido pelo Caio, com os efeitos
contínuos dele. A trajetória em diagonal e as dicas no "i" saíram; estão guardadas em
`_descartados/2026-10-30/roadmap_diagonal/`. O protótipo fica em `app/static/roadmap_proto/a/`, e a 1ª versão dele em
`a_v1/`. A página está na V2 (porta 8400) e substitui a "Linha do tempo" (rascunho em `_descartados/2026-10-30/`).
É a 1ª página depois da capa, antes da Demanda (`antes_do_inicio=True`). Rota `/viu-agenciamento/roadmap#1`.

Arquivos:
- `app/apresentacoes/gestao_orcamentos/roadmap/__init__.py`: `SITUACOES`, `ETAPAS` (com a bifurcação como dado:
  `espera`, `paralelo`, `legenda_ida`, `legenda_volta`), `DASHBOARDS` e a geometria (vagas, `Y_LINHA`, `Y_RAMO`);
- `app/apresentacoes/gestao_orcamentos/roadmap/template.html`;
- classes `.rm-*` em `app/static/estilo.css`;
- ícones `ampulheta`, `imagem`, `ampliar`, `dispersos`, `fluxo`, `nuvem`, `banco` e `tendencia` em
  `app/templates/icones.html`;
- painel das imagens ampliadas em `app/static/roadmap.js`;
- imagens em `app/static/roadmap/` (geradas por `tools/gerar_imagens_roadmap.py`).

A página não lê dados (`tabelas=("entrada",)` só para o rodapé datado).

**Pergunta:** Como chegamos até aqui? (Caio, 30/10/2026: sem o "e para onde vamos"; `pergunta` da seção em
`apresentacao.py`, também usada pelo gancho da capa).
- Sem o gancho no canto (`gancho_oculto` em `montar_roadmap`).
- O link para a Demanda fica para o leitor de tela e para a seta →.

## A história (narrativa do Caio, 30/10/2026; textos enxutos em 31/10/2026): tudo à vista

| # | Título | No texto | Imagens / botões | Marca | Situação |
|---|---|---|---|---|---|
| 1 | Dados espalhados | Vários formatos, inclusive em contas pessoais. Risco de perda: se a pessoa sai, o dado vai junto. | chips soltos SharePoint, Excel, Monday, OneNote | Risco de perda | Ponto de partida |
| 2 | Mapeamos e organizamos | O processo de ponta a ponta. | miniatura "Ver o fluxo" | — | Em curso |
| 3 | Pedimos a infraestrutura à tecnologia (ramo da espera, acima) | Um projeto no GCP para o BigQuery. → **Infraestrutura liberada**: A etapa mais longa. | — | Ponto de espera (tracejado âmbar) | Feito |
| 3 | **Em paralelo:** Dashboards com o que já tínhamos (ramo de baixo, "enquanto esperávamos…") | Com os dados que já existiam, sem a base central. | miniaturas Pagamentos e Contratos | — | (a do 3) |
| 4 | Centralizando tudo no BigQuery (os dois ramos se juntam; "quando liberou…") | Os dados num lugar só. Bronze, Prata, Ouro (numa linha). | miniatura "Camada ouro" | — | Em curso |
| 5 | Estudos e análises | Novas análises a partir da base central. | botões Demanda, Talentos, SLA, Projeto LIA | Você está aqui | Em curso |
| 6 | Próximos passos | Fechamentos, receita e LIA na camada ouro. Portal publicado, com acesso por e-mail. | botões Iniciativas, Previsão | — | Próximo |

A bifurcação conta a história da infraestrutura. Houve uma parada esperando a tecnologia, mas a área não ficou parada:
os dashboards de Pagamentos e Contratos e as primeiras análises saíram com os dados que já existiam. Os dashboards
mudaram da etapa 5 para o ramo paralelo.

## Desenho (30/10/2026, noite: horizontal, base no protótipo A)

- **Palco em cor**, abaixo do título (que segue na moldura do portal):
  - base lavanda clara;
  - três manchas desfocadas e translúcidas (azul VIU, lavanda e pêssego) e dois aros de vidro;
  - sem tudo azul e sem branco puro.
- **Geometria** (a mesma em `__init__.py` e no CSS):
  - o SVG (`viewBox 1000 × 290`) cobre os 29 em de cima do palco;
  - linha principal a 10,5 em; ramo paralelo a 16,5 em;
  - margem de 2% de cada lado; cada etapa ocupa uma vaga de 96% / número de vagas (classes `rm-v4` a `rm-v10` e
    `rm-s0` a `rm-s9`);
  - a etapa que se bifurca ocupa duas vagas: o pedido e o "liberado" acima da linha; o ramo paralelo desce 0,4 vaga
    depois da bifurcação e volta 0,4 vaga antes do BigQuery, com juntas brancas nos dois pontos.
- **Linha:**
  - degradê azul, sólida até o "Você está aqui" e tracejada depois;
  - âmbar tracejado no trecho da espera; lavanda no ramo paralelo.
- **Cartões de vidro:** branco translúcido com desfoque e sombra azulada. Neles: número (Playfair, azul), situação
  (ícone + texto), título (Playfair 600), frase, itens, camadas com bolinha de cor, caixa do risco, miniaturas e
  botões.
- **Botões:** o padrão do portal. Retangulares, cantos de 6 px, fundo branco levemente degradê, borda fina e sombra em
  camadas; azul VIU no mouse ou foco. Em grade 2 × 2, sem seta, todos iguais.
- **Chips soltos de vidro**, levemente girados e com `aria-hidden`, porque o texto já está nos cartões:
  - as fontes da etapa 1;
  - o que vem na etapa 6 (tracejados).
- **Movimento contínuo:** exceção do portal por decisão do Caio, só em `@media (prefers-reduced-motion:
  no-preference)`; o teste está em `tests/test_movimento.py`. Com movimento reduzido, tudo fica parado. Sem botão de
  pausa, como na capa.
  - **Pulso:** percorre a linha até o "Você está aqui" pelos dois ramos. No da espera, vai devagar no trecho âmbar; o
    paralelo chega antes. Ciclo de 8 s.
  - **Ondas:** abrem no marco atual.
  - **Ícones com micro-movimentos:**
    - peças à deriva;
    - fio do fluxo correndo;
    - nuvem flutuando;
    - linha da tendência se traçando;
    - camadas do banco pulsando;
    - barras do gráfico subindo;
    - bandeira tremulando;
    - ponteiro do "Em curso";
    - ampulheta virando;
    - alerta do risco.
  - **Tracejados:** marcham; os chips derivam.
- **Abaixo de 900 px:** lista vertical. Os dois ramos aparecem em sequência, com as legendas, uma borda âmbar
  tracejada no "liberado" e uma borda lavanda no ramo paralelo.

## Desenho anterior (diagonal; guardado em `_descartados/2026-10-30/roadmap_diagonal/`)


**Abertura das reuniões de diretoria (Caio, 30/10/2026).** A página tem de ser a mais bem acabada do portal e crescer
com o projeto. Depois do retorno "está chegando lá, mas branca demais", ela ganhou cor e a trajetória passou a subir.

- **Palco em cor** (`.rm-palco`), sangrando um pouco além das margens do título:
  - degradê do lavanda quase branco (embaixo à esquerda) ao lavanda (alto à direita), com uma grade de pontos bem leve;
  - a área sob a curva em azul VIU e marinho translúcidos (`rm-area`), como uma montanha que cresce;
  - a faixa do que vem depois, hachurada, a partir de meia coluna antes da 1ª etapa "Próximo" do fim da lista
    (`rm-futuro`, classe `rm-f<índice>`);
  - uma luz azul atrás do marco do "Você está aqui" (`rm-luz`).
- **Trajetória em diagonal ascendente:** sai do canto inferior esquerdo (entrada pontilhada) e sobe, em degraus suaves
  (curvas em S com tangente horizontal em cada marco), até o canto superior direito (cauda tracejada).
  - Um SVG só (`rm-trilha`, viewBox 1000 × 1000, `preserveAspectRatio="none"`, traço sem escala), um trecho por etapa.
  - Coordenadas em `roadmap/__init__.py`: `X_INICIO`/`X_FIM` = 40/800 e `Y_INICIO`/`Y_FIM` = 840/160. O CSS usa os
    MESMOS números (`--rm-xa: 4%`, `--rm-xb: 80%`, `--rm-ya: 0.84`, `--rm-yb: 0.16`) e posiciona marcos e cartões pelo
    índice (`--i`, classes `rm-k0` a `rm-k7`) e pelo número de etapas (`--n`, classes `rm-n4` a `rm-n8`). O teste
    confere que os dois lados batem.
  - Fita de 9 px em degradê da cor de uma etapa à da seguinte, halo de 26 px e sombra azulada.
  - Concluído ou em curso: sólido. A espera da TI: pontilhada em âmbar. Próximos: tracejados e esmaecidos.
- **Cartões de vidro** (branco translúcido com desfoque do fundo, fio branco, sombra marinho), presos ao marco por uma
  haste na cor da etapa e com a borda esquerda nessa cor:
  - na parte de baixo da subida o cartão fica **acima** do marco; na de cima, **abaixo** (os dois triângulos livres do
    palco). A base do cartão de cima fica acima do marco seguinte, então a curva nunca passa por baixo dele;
  - até 6 etapas, metade acima e metade abaixo; com 7 ou 8, só as 3 primeiras acima (colunas estreitas);
  - o do "Você está aqui" é mais opaco e tem brilho azul; o dos próximos tem a borda tracejada e é mais transparente.
- **Hierarquia do cartão:** número em Playfair na cor da etapa, situação (ícone + texto), título em Playfair, uma frase
  em IBM Plex Sans, botões e mini janelas. O "i" fica no canto de cima do cartão (não quebra mais sozinho no fim do
  título).
- **Marcos:** 3,1 em, de vidro, com anel branco e sombra na cor da etapa; os próximos, tracejados.
- **"Você está aqui":** marco 30% maior, cheio em azul VIU, halo duplo e luz no palco; a etiqueta azul, maior, com uma
  seta para o marco, do lado livre da curva.
- **Botões:** os mesmos (cantos de 6 px, sombra em camadas). Com 4 botões, grade 2 × 2; com 7 ou 8 etapas, compactos e
  sem a seta, quebrando linha.
- **Mini janelas:** as mesmas; duas no mesmo cartão dividem a largura.
- **Escala (4 a 8 etapas):** novas etapas entram só pelo catálogo; a subida, o passo e as colunas se recalculam. Com 7
  ou 8, tudo fica 10% menor. Testado com 8 etapas temporárias, só no teste `test_roadmap_escala_ate_8_etapas` e nas
  capturas `rm7-8etapas-*.png` (HTML gerado pelo TestClient com o catálogo trocado na memória e injetado no navegador).
  Elas não ficaram no catálogo.
- **Abaixo de 900 px:** trilha vertical simples, com os mesmos cartões de vidro, sem a curva.

**Versão anterior (30/10/2026, "rm6", horizontal):** curva em onda com marcos alternando a 28% e 72% (`ALTURA_ONDA`),
fita de 8 px, grade de uma coluna por etapa, texto sobre fundo branco. Saiu por "branca demais".

**Versões anteriores do desenho (30/10/2026):**

- **A curva é a protagonista.**
  - SVG em onda, um trecho por etapa, do marco dela ao da seguinte.
  - Degradê da cor de uma etapa à da seguinte, traço de 4 px com halo suave.
  - Pontilhada em âmbar na espera da TI e tracejada nos próximos passos.
  - Marcos-ícone de 2,6 em, com sombra; alturas alternadas de 30% e 70% (`ALTURA_ONDA`).
- **Texto alternando** acima e abaixo da curva, preso ao marco por uma haste fina:
  - número e situação (ícone + texto);
  - título em Playfair 1,02 em;
  - frase em IBM Plex Sans 0,72 em, com entrelinha de 1,5.
  O texto avança sobre a coluna vizinha, cujo lado está livre.
- **Dicas:** botão "i" ao lado do título (nome "Detalhes: <título>", `aria-describedby` para a dica, `role="tooltip"`).
  - Abrem com o mouse ou com o foco (também no toque); o Esc fecha sem tirar o foco.
  - Sem JS, o texto continua no HTML e é lido pelo leitor de tela.
- **Botões:** todos iguais.
  - Retangulares, com cantos de 6 px, fundo branco levemente degradê, borda fina e sombra em três camadas.
  - No mouse ou no foco: azul VIU, sobem 1 px e a sombra cresce. Ao clicar, afundam. Foco com contorno azul.
  - Volta ao Roadmap pela aba do topo (mantida).
- **Imagens:** mini janelas (moldura com barra de janela e três pontos pastel) com o nome embaixo; ampliam no painel.
  Os dois dashboards ficam lado a lado.
- **Ocultar uma etapa na reunião:** `"mostrar": False` no catálogo.
- **Abaixo de 900 px:** trilha vertical simples, sem a onda.

**Movimento.** Vale só com `prefers-reduced-motion: no-preference` e `html.js`, uma vez, sem loop; cada animação dura
até 1,1 s, a sequência inteira cerca de 2,5 s. Sem JS ou com movimento reduzido, tudo já aparece no lugar.
1. A trilha (curva e área) se desenha da esquerda para a direita, subindo, em 1,1 s (velocidade constante).
2. Cada marco surge com um leve sobressalto quando a linha chega no x dele (atraso = 44 ms + posição × 836 ms).
3. O ícone de cada marco tem a sua entrada:
   - dispersos: se juntam girando;
   - fluxo: desliza;
   - nuvem: flutua;
   - banco: empilha;
   - gráfico: as barras crescem;
   - bandeira: acena.
4. A ampulheta do "Ponto de espera" vira uma vez.
5. O cartão, a haste e as marcas aparecem logo depois do marco; a faixa do futuro e a luz do "Você está aqui" acendem.
6. No fim, um brilho branco percorre a curva uma vez, um anel se abre no marco do "Você está aqui" e um reflexo
   atravessa a etiqueta.

Ao passar o mouse sobre o texto de uma etapa, ou ao focar algo nele, o ícone repete um gesto curto: gira, desliza,
flutua, empilha, cresce ou acena. Botões e janelas sobem no mouse e afundam no clique.

## Imagens e painel ampliado

Cada registro (`ETAPAS[...]["registros"]`) tem `imagem` = nome-base em `app/static/roadmap/`:
- `<nome>-mini.webp` na janela;
- `<nome>.webp` no painel;
- `<nome>-alta.webp`, se existir, para a leitura a 100%.

O painel é o mesmo já aprovado:
- `<dialog>` aberto com `showModal()`, até 92% × 88% da tela, sobre fundo escurecido e desfocado;
- entrada a partir da miniatura em 420 ms, e volta para ela ao fechar;
- botões "Ver em 100%" e "Fechar"; clique na imagem amplia no ponto clicado; arrastar ou rolar percorre a imagem;
- o quadro da imagem é `role="region"`: as setas não trocam de página;
- Esc, Fechar e clique no fundo fecham, e o foco volta à janela que abriu;
- sem JS, o link abre a imagem.

| Imagem | Arquivos | Origem e privacidade |
|---|---|---|
| Fluxo ponta a ponta | mini, painel 2742×549, alta 9486×1899 (245 KB) | PDF "Viu Agenciamento - Fluxo 1" (30/10/2026). Desfocados: nomes de pessoas, exemplo de contrato e de proposta, e-mail da caixa de pedidos e todas as capturas coladas no quadro. |
| Camada ouro no BigQuery | mini, painel 1519×813 | **Print do Caio, 30/10/2026**: console do BigQuery, `gold_monday`. Recortado sem a barra do Google Cloud, sem a conta e sem os menus. |
| Controle do processo de pagamento | mini, painel 1198×828 (64 KB) | **Print do Caio, 30/10/2026**. Desfocada a tabela inteira por talento, marca e projeto (nomes, valores e datas por linha). Ficam o título, os filtros vazios, os totais agregados dos indicadores e a matriz de risco (só pontos). |
| Contratos e bloqueios | mini, painel 1108×817 (32 KB) | **Print do Caio, 30/10/2026**. Desfocados a saudação com o nome e a data, a data e hora da atualização, os nomes dos talentos e as contagens por talento, e as datas e prazos por contrato. Ficam os totais (30 vigentes, 12 vencem em 90 dias), os filtros e as barras da linha do tempo. |

- O quadro "Pontos de atenção" saiu da página (o Caio ficou só com o fluxo). Os arquivos estão em
  `_descartados/2026-10-30/app/static/roadmap/`, com uma linha no LEIAME de lá.
- Para refazer:
  - `python -I tools/gerar_imagens_roadmap.py <PDF> app/static/roadmap [<PNG do BigQuery>]`;
  - `python -I tools/gerar_imagens_roadmap.py --dashboards app/static/roadmap <PNG pagamento> <PNG contratos>`.

  As duas linhas usam o Python 3.12 do computador, que tem PyMuPDF. Os originais ficaram só no scratchpad da sessão.
- Legibilidade (capturas anteriores): a 100%, o fluxo fica legível em 1440×810 e em 1920×1080, e o BigQuery já na
  visão inteira.
- **Dashboards:** a área tem outros; por enquanto entram só estes dois. Para incluir mais, basta o print (PNG da tela
  inteira, 1600 a 2400 px de largura), com o nome do dashboard.

## Fontes dos fatos

- Pedido e relatos do Caio (30/10/2026): dados espalhados e em contas pessoais, mapeamento ("Fluxo 1"), pedido e
  liberação da infraestrutura pela tecnologia, centralização no BigQuery em camadas, portal e dashboards, LIA.
- Projeto: camadas em projetos separados (`PPD-BRONZE-MONDAY`, `PPD-BRONZE-SHAREPOINT`, `PPD-SILVER-MONDAY`,
  `PPD-GOLDEN-AGENCIAMENTO-MONDAY`); o portal lê só a gold (`gold_monday`, D57).

## Proposta a confirmar com o Caio

- Pedido e liberação da infraestrutura numa etapa só, com a espera marcada na curva.
- "Projeto LIA" nos estudos.
- O texto das dicas, sobretudo a explicação das camadas e a frase "dois estão aqui".
- Sem botão "Voltar ao roadmap" nas outras páginas.

## Validação (31/10/2026: versão executiva)

**Testes:**
- `test_roadmap`: caminhos com y 130/190 e 6 situações (uma por etapa).
- `test_roadmap_tudo_a_vista`:
  - no máximo 2 itens e frases de até 60 caracteres;
  - camadas numa linha;
  - um grupo de chips;
  - sem manchas nem vidro no bloco `.rm-*`.
- Os demais `test_roadmap*` seguem.

**Capturas** (`.playwright-mcp/rm-v3-*.png`):
- 1440×810, 1280×720 e 1920×1080: sem rolagem e sem sobreposição;
- 390 px: sem rolagem lateral;
- miniatura de Pagamentos ampliada, com o foco no Fechar;
- antes: `rm-v3-antes-1440x810.png`.

## Validação (30/10/2026, noite: versão horizontal)

Testes em `tests/test_v2_paginas.py`:
- `test_roadmap`: ordem, vagas e o caminho da linha.
- `test_roadmap_tudo_a_vista`: nenhuma dica nem painel; todas as frases no HTML.
- `test_roadmap_botoes`.
- `test_roadmap_registros`: os dashboards no ramo paralelo.
- `test_roadmap_mostrar_oculta_etapa`: sem a infraestrutura, a linha segue reta.
- `test_roadmap_escala_ate_8_etapas`: 9 vagas.

Em `tests/test_movimento.py`, a exceção do loop está documentada: só no bloco `.rm-*` e só sem movimento reduzido.

Capturas (Chrome headless, em `.playwright-mcp/rm-v2-*.png`):
- 1440×810, 1280×720 e 1920×1080: sem rolagem e sem sobreposição entre cartões, chips, legendas e selos;
- 390 px: sem rolagem lateral;
- miniatura ampliada no painel, com o foco no Fechar.

## Validação (30/10/2026)

Testes em `tests/test_v2_paginas.py`:
- `test_roadmap`: ordem; título "Como chegamos até aqui?" e gancho só para o leitor de tela; 3 cartões acima e 3
  abaixo; um SVG com um trecho por etapa, marcos subindo (y 840 → 160) e indo para a direita (x 40 → 800); entrada no
  canto, área sob a curva, uma cauda, faixa do futuro (`rm-f5`) e luz no "Você está aqui"; constantes do Python iguais
  às do CSS; marcas; situação com ícone e texto; frase de até 52 caracteres; sem os elementos antigos; sem `style="`.
- `test_roadmap_dicas`: seis botões "i" ligados às dicas, com o texto no HTML.
- `test_roadmap_botoes`: hrefs certos e respondendo 200, Atendimento fora, um estilo só.
- `test_roadmap_registros`: quatro janelas com nome; arquivos WebP com menos de 300 KB; `alt`, `width`/`height` e
  `lazy`; o painel; nenhum nome de pessoa nem a saudação do print.
- `test_roadmap_mostrar_oculta_etapa`: o campo `mostrar` tira a etapa da tela e a subida se recalcula para 5.
- `test_roadmap_escala_ate_8_etapas`: 8 etapas temporárias; passo recalculado, cada trecho liga um marco ao seguinte,
  só 3 cartões acima, regras de CSS para 8.

Capturas da versão em cor e diagonal, em `.playwright-mcp/` da V2 (Chrome headless próprio, movimento permitido,
porque o navegador do Playwright MCP estava em uso por outro agente):
- `rm7-1280.png`, `rm7-1440.png`, `rm7-1920.png`: sem rolagem nem gancho visível;
- `rm7-390.png`: trilha vertical, sem rolagem lateral;
- `rm7-8etapas-1280.png` e `rm7-8etapas-1440.png`: 8 etapas, sem rolagem (em 1280×720 é o limite: o cartão mais alto
  termina rente ao pé do palco);
- `rm7-dica5-1280.png` e `rm7-dica2-1280.png`: dicas pelo foco;
- `rm7-entrada-1280.png`: meio da entrada (linha e marcos juntos);
- `rm7-painel-1280.png`: painel ampliado (dashboard de contratos);
- `rm7-antes-1440.png`: a versão anterior, horizontal, para comparar.

Capturas da versão horizontal (rm6), em `../PPD-AGENCIAMENTO-SLA/.playwright-mcp/`: `rm6-1280.png`, `rm6-1440.png`,
`rm6-1920.png`, `rm6-390.png`, `rm6-brilho-1440.png`, `rm6-brilho2-1440.png` e `rm6-8etapas-*.png`.

Capturas anteriores:
- `rm5-1280.png`, `rm5-1440.png`, `rm5-1920.png` e `rm5-390.png`, todas sem rolagem: em 1280×720 o conteúdo vai de
  195 a 629 px, com o pé em 664; em 390 px não há rolagem lateral;
- `rm5-dica-mouse-1280.png` e `rm5-dica-foco-1280.png` (o Esc fecha);
- `rm5-botao-hover-1280.png`;
- `rm5-painel-1280.png` (dashboard de contratos ampliado);
- `rm5-entrada-1280.png` (meio da entrada).

## Histórico

- **31/10/2026 (auditoria do Codex, F10):** rodapé "Conteúdo editorial · não depende da carga de dados" no lugar da data da carga de entradas (a página não lê dados).
- **31/10/2026, tarde:** 4ª versão, "a linha que desemboca nos destinos" (hub: história à esquerda, leque até os
  botões das páginas à direita; marcos como pontos; sem números, selos nem legendas soltas). Executiva guardada em
  `_descartados/2026-10-31/roadmap_v3/`.

- 31/10/2026: versão executiva (Caio: "informação demais", "carnavalesco"). O que mudou:
  - fundo branco, sem vidro nem caixas;
  - paleta dos azuis do projeto;
  - o mínimo por etapa;
  - situação uma vez por etapa;
  - linha mais baixa.

  A versão colorida foi para `_descartados/2026-10-31/roadmap_colorido/`.

- 30/10/2026 (noite): o Caio escolheu o protótipo A (horizontal). O que mudou:
  - tudo à vista, sem dicas;
  - fluxo mais para baixo;
  - fundo em três cores;
  - botões no padrão do portal;
  - chips soltos;
  - bifurcação na infraestrutura (espera × "Dashboards com o que já tínhamos");
  - movimento contínuo com respeito ao movimento reduzido.

  A diagonal foi para `_descartados/2026-10-30/roadmap_diagonal/`.

- 30/10/2026: "branca demais" (Caio): palco em cor (degradê lavanda, área sob a curva, faixa hachurada do futuro, luz
  no "Você está aqui"), trajetória em diagonal ascendente em degraus suaves, cartões de vidro com haste, "i" no canto do
  cartão, posições pelo índice e pelo número de etapas (4 a 8), entrada sincronizada com a linha.
- 30/10/2026: "Linha do tempo" vira "Roadmap" (fluxo sem datas, trilha paralela da LIA); risco das contas pessoais,
  migração e dados de outras áreas.
- 30/10/2026: miniaturas do mapeamento; infográfico com faixa reta; modo "Etapa a etapa" criado e retirado; print do
  BigQuery; painel grande com leitura a 100%; botões retangulares.
- 30/10/2026: versão enxuta (curva em onda, uma linha por etapa, detalhe em dicas, botões todos iguais).
- 30/10/2026: abertura das reuniões:
  - título "Como chegamos até aqui?" e gancho oculto;
  - curva em fita com sombra e brilho de entrada;
  - marcos de vidro;
  - "Você está aqui" em destaque;
  - grade para 4 a 8 etapas.
- 30/10/2026: meio-termo:
  - narrativa nova do Caio;
  - curva e marcos mais fortes;
  - ícones com entrada própria e gesto no mouse;
  - textos menores, com hierarquia;
  - botões com sombra em camadas;
  - mini janelas com nome;
  - "Pontos de atenção" fora;
  - dois dashboards (prints do Caio) com desfoque de nomes, valores e datas por linha.
