# Encerramento (V2)

**Estado (31/10/2026, 3ª rodada):** o Caio gostou do marinho, mas achou a página "morta" perto do resto e pediu três
rodadas de ajuste no mesmo dia. Rota: `/viu-agenciamento/encerramento`, a última página, depois da Previsão. Arquivos:

- `app/templates/encerramento.html` (o SVG do mascote é gerado por script);
- textos em `encerramento={...}` de `app/apresentacoes/gestao_orcamentos/apresentacao.py`;
- bloco `/* Encerramento (V2, Caio, 31/10/2026)` … `/* fim do bloco do encerramento (V2) */` em `app/static/estilo.css`,
  antes da linha D46;
- `app/static/fim.js`.

A página não lê dados; o rodapé datado continua. As versões anteriores e as variações descartadas estão em
`_descartados/2026-10-31/encerramento_antes/`.

## O que mostra

- **Fundo:** o marinho inteiro da capa (`--capa-marinho`).
- **Faixa branca no topo:** estreita, com o corte em diagonal e o filete azul da capa (7,6em à esquerda e 4,7em à
  direita). Ela leva o **logo da VIU** à esquerda e a data da capa ("Outubro de 2026", `capa.data`) à direita. Ficou
  no topo, e não na lateral, porque uma faixa à esquerda passaria sob o rodapé datado, que é claro.
- **Corpo, à esquerda e centralizado na vertical:** "ViU Agenciamento" (`sobre`, lavanda), "Obrigado." (`titulo`,
  Playfair, 8,6em) com o **fio amarelo** e o botão **"Voltar ao início"** (`voltar`), que leva à capa. O botão segue o
  padrão do "Começar" da capa: amarelo VIU, cantos de 6 px, sombra em camadas, sobe 1 px no hover e tem ícone de
  retorno. A frase e a pergunta antigas ficam vazias (`frase`, `pergunta`).
- **Mascote, no canto inferior direito:** cerca de 24% da altura da lâmina, longe do rodapé datado, que fica à esquerda.
  É um SVG próprio e decorativo (`aria-hidden`), no estilo flat de mascote de app:
  - um balão de conversa lavanda claro (`#e2e5ff`) com contorno marinho fino e brilho branco;
  - olhos ovais com brilho, sorriso aberto com língua rosada e bochechas rosadas suaves;
  - um braço com mão gorducha que acena;
  - um coração amarelo VIU ao lado.

  O balão foi escolhido entre três propostas (humano, balão e gota), em três iterações. As capturas das propostas estão
  em `_descartados/2026-10-31/encerramento_antes/mascotes_variacoes/`. O gerador é o `mascotes.py`, também guardado lá.

## Movimento

- **Entrada:** acontece uma vez, em até 1,2 s. A faixa e o filete descem, sobem o sobretítulo e o título, e o fio amarelo
  se estende. Depois o mascote sobe e o botão aparece.
- **Loops contínuos, sem pausa, até a pessoa sair da página:**
  - **aceno:** o antebraço gira ±10° no cotovelo e a mão gira ±17° no punho, com leve atraso; ciclo de 1,4 s;
  - **piscar:** escala rápida no eixo Y a cada 3,4 s;
  - **flutuar:** 3 unidades a cada 3,2 s;
  - **coração:** pulsa a cada 1,4 s.

  Todos são SMIL com `begin="indefinite"` e `repeatCount="indefinite"`; o CSS não tem loop.
- **`fim.js`:**
  - começa os loops 1,1 s depois de abrir a página;
  - pausa só com a aba oculta (economia) e retoma ao voltar;
  - não anima nada com movimento reduzido: o mascote fica parado, sorrindo, de olhos abertos.
- **Sem JS:** os loops nem começam.

## Telas e acessibilidade

- Cabe sem rolagem em 1440×810, 1280×720 e 1920×1080 (capturas de 31/10/2026). Em 390 px não rola para o lado: a
  faixa encolhe, o título passa a 4,1em e o mascote fica à direita, abaixo do botão.
- O título é um `h2` que nomeia o slide (`aria-labelledby`). O logo tem `alt="VIU"`. O mascote é `aria-hidden`.
- Contraste: o botão tem tinta `#0b1220` sobre `#f8fd0b`. A data usa `--tinta-2` sobre branco. O título fica em branco
  e o sobretítulo em lavanda `#a9b1ff` sobre o marinho. Todos ficam acima de 4,5:1.
- CSP: sem `style="…"` e sem script inline. As cores do mascote são atributos de apresentação do SVG. O JS fica em
  `fim.js`.

## Testes

- `tests/test_portal.py::test_capa_e_encerramento`: textos, botão com ícone para a capa, logo, mascote decorativo,
  `fim.js`, sem o fluxo antigo nem a mão, sem "Próximo passo" e sem `style=`.
- `tests/test_movimento.py::test_encerramento_loop_so_por_smil_e_parado_sem_movimento`: confere que os 5 loops são
  SMIL, contínuos e só começam pelo `fim.js`. Confere também o aceno de 1,4 s (antebraço e mão), o piscar de 3,4 s,
  nada de `infinite` no bloco `.fim-*` e a pausa com movimento reduzido e com a aba oculta. A exceção 3 está registrada
  em `test_sem_mola_sem_loop_no_css_todo`.
- A entrada é conferida pelo limite de 1,2 s em `test_entrada_das_paginas_ate_1200ms`.

## Histórico

- 27/10/2026 (D59/D61): encerramento só com texto sobre o marinho: sobretítulo, "Obrigado.", fio lavanda, frase,
  pergunta e botão contornado.
- 31/10/2026, 1ª rodada:
  - entraram a faixa com o logo, o fio amarelo e o botão amarelo;
  - entraram também a mão que acena ao lado do título e, à direita, o espelho do fluxo da capa (`encerramento_fluxo.html`).
- 31/10/2026, 2ª rodada:
  - o Caio pediu para tirar o fluxo e trocar a mão por um bonequinho no canto inferior direito
    (`encerramento_bonequinho.html`).
- 31/10/2026, 3ª rodada:
  - o Caio achou o bonequinho "muito feio" e pediu animação contínua;
  - entrou o mascote balão de conversa, que acena e pisca sem parar.
