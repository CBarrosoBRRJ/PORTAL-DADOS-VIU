# Capa (V2)

**Capa nova APLICADA (Caio, 03/11/2026):** `templates/capa.html` (com `static/capa_nova.css` e `capa_nova.js`): título atravessando o corte, desenho limpo, fluxo que termina no "Começar"; **sem** o subtítulo, sem textos no desenho e **sem o rodapé datado** (`sem_rodape`, exceção à regra 9 só na capa, pedido do Caio). Refinada com as referências do Impeccable (critique, polish, typeset, quieter, delight). `/capa-nova` responde 301 para `/capa`. A validada está em `_descartados/2026-11-03/capa_validada/`; a proposta em `_descartados/2026-11-03/app/templates/capa_nova.html`. Testes em `tests/test_capa_nova.py`.

**Estado (30/10/2026, 3ª rodada):** capa sem o menu dos temas. O subtítulo fica no lado branco. No plano marinho ficam
só a ilustração "dados → área", com fluxo contínuo, e o botão "Começar". Está na V2 (porta 8400). Rota
`/viu-agenciamento/capa` (a raiz `/` abre nela). Arquivos: `app/templates/capa.html`, textos em `capa={...}` de
`app/apresentacoes/gestao_orcamentos/apresentacao.py`, classes `.capa-*` em `app/static/estilo.css` (bloco "V2 (Caio,
30/10/2026): capa sem o menu dos temas", antes da linha D46) e `app/static/capa_fluxo.js`. Testes:
`tests/test_portal.py::test_capa_e_encerramento` e `tests/test_v2_paginas.py::test_capa_sem_menu_com_comecar_para_o_roadmap`.
A capa não lê dados (sem números ao vivo); o rodapé datado continua.

## O que mostra

- **Lado branco:** logo, sobretítulo "Relatório da área", título "ViU / *Agenciamento*", fio azul, o **subtítulo**
  "Tudo o que a área analisa, constrói e entrega, num só lugar." (`capa.subtitulo`; discreto, cinza, quebra
  equilibrada) e a data "Outubro de 2026".
  - Por que o subtítulo: o relatório não é só sobre demanda. Ele reúne demanda, prazos, automação e IA, iniciativas,
    dashboards e próximos passos. "Analisa, constrói e entrega" cobre estudos, ferramentas e resultados. Ficou no lado
    branco, como o Caio sugeriu, para o plano marinho ficar só com a ilustração e o botão.
- **Plano marinho em diagonal**, com o filete azul no corte:
  - **Ilustração decorativa** (SVG em `capa.html`, `aria-hidden`, viewBox 480×440; coluna do plano marinho de 28,5em, antes 26em, e desenho até 33em de altura, antes 31em): treze pontos
    de origem lavanda, de tamanhos variados. Onze estão à esquerda e dois chegam por cima e por baixo, que são os dados
    de muitos lugares. As linhas convergem num nó amarelo e seguem como uma linha única. É a ideia de "dados → área".
  - **Fluxo contínuo:** pequenos cartões **brancos**, de tamanhos diferentes, saem dos pontos e seguem as linhas devagar
    (34–41 unidades por segundo, ciclos de 8,7 a 14,7 s, dois itens por linha, fora de fase). No nó, cada cartão vira
    um quadradinho **amarelo VIU** igual aos outros, "padronizado", que corre pela linha única e some no fim. São
    animações SMIL do SVG (`animateMotion` + `animate` de opacidade; só posição e opacidade).
  - **Botão "Começar"**, centralizado sob a ilustração: um link para a próxima página da sequência (`proxima.href`,
    hoje `/viu-agenciamento/roadmap#1`). Amarelo VIU sobre o marinho, baixo (padding vertical de 0,52em), no padrão
    dos botões do Roadmap (`.rm-botao`): cantos de 6 px, sombra em camadas, sobe 1 px no hover, afunda ao pressionar e
    foco com contorno branco.

## O que faz

- A navegação pelas páginas fica com o **Roadmap**, a 1ª página depois da capa, que tem botões para cada página.
- **Seta → / PageDown** e o link `rel="next"` levam ao Roadmap, como o "Começar".
- **Movimento de entrada:** uma vez, até 1,2 s (o limite das páginas, `tests/test_movimento.py`). Os pontos surgem, as
  linhas se traçam até o nó, o nó acende, a linha única sai dele e o botão sobe. As partículas aparecem em seguida.
- **Animação contínua (loop autorizado pelo Caio, 30/10/2026, só na capa).** O botão de pausa foi retirado por decisão do
  Caio em 30/10/2026; a animação é contínua e respeita o movimento reduzido. Exceção à regra "nada em loop" do portal.
  O CSS continua sem loop (o teste do CSS todo segue valendo); o loop está no SVG de `capa.html`.
  `app/static/capa_fluxo.js` só pausa as animações (`svg.pauseAnimations()`) com movimento reduzido e com a aba oculta,
  para economizar. As partículas só aparecem com `prefers-reduced-motion: no-preference` e `html.js`. Sem JS ou com
  movimento reduzido, a composição fica parada, sem partículas, e o "Começar" funciona, porque é um link.
- **Telas:** cabe sem rolagem em 1280×720, 1440×810 e 1920×1080 (sobra 1 px de altura, que já existia na capa original
  da porta 8100). Abaixo de 860 px, ou em tela estreita, o plano marinho vira uma faixa abaixo do lado branco, com a
  ilustração até 13em. Em 390 px não há rolagem lateral.
- **Acessibilidade:** a ilustração é decorativa. O subtítulo (`--tinta-2` sobre branco) e o "Começar" (marinho sobre o
  amarelo) passam de 4,5:1. CSP: sem `style="..."`; JS só em `app/static/capa_fluxo.js`.

## Histórico da página

| Data | Mudança |
|---|---|
| 03/11/2026 | Revisão: o remendo do 1 px de rolagem da capa (`capa_nova.css`) virou a regra geral `.palco > .proxima.so-leitor { top: 0; bottom: auto; }` em `estilo.css` (vale para capa, Roadmap, estudo e encerramento); o gancho escondido sai da ordem do Tab (`tabindex="-1"`; o leitor de tela e as setas seguem). |
| 27/10/2026 | D59–D61: capa da reunião; desenho de referência do Caio com a jornada animada de um pedido (`static/capa.js`), cujo relógio parava no típico do SLA. |
| 30/10/2026 | Caio e gerente: o plano marinho vira o menu dos temas (o "Começar" e a jornada saem). Cópia da capa anterior em `_congelado/2026-10-30_capa_antes/` (projeto original). |
| 30/10/2026 | V2: capa "ViU *Agenciamento*", sem subtítulo; menu no modo denso a partir de 6 temas (PRD da capa, RF5). |
| 30/10/2026 | V2 (Caio): o **menu dos temas sai** (o Roadmap passa a navegar). No lugar entram a ilustração "dados → área", a frase "Como a demanda chega, como a gente responde e o que vem pela frente." e o "Começar" amarelo. O `capa.html` com o menu e o CSS do menu, do modo denso e do "Começar" antigo foram para `_descartados/2026-10-30/` (`app/templates/capa.html` e `app/static/estilo_capa_menu.css`). |
| 30/10/2026 | 2ª rodada (Caio): fluxo contínuo de partículas (loop autorizado só na capa) com botão "Pausar animação". |
| 30/10/2026 | 3ª rodada (Caio): **botão de pausa retirado por decisão do Caio; animação contínua; respeita movimento reduzido** (o `capa_fluxo.js` perdeu o botão e o `localStorage`). Ilustração maior (13 pontos; itens brancos que viram amarelos no nó; pontos e linhas mais visíveis). A frase do plano marinho foi trocada pelo subtítulo do lado branco: "Tudo o que a área analisa, constrói e entrega, num só lugar.". "Começar" mais baixo e centralizado sob a ilustração. O CSS anterior (`.capa-frase`, `.capa-pausa`) foi acrescentado a `_descartados/2026-10-30/app/static/estilo_capa_menu.css`. Depois, a coluna da ilustração foi ampliada (28,5em; até 33em de altura) para ocupar melhor o plano marinho. A versão do `capa.html` e do `capa_fluxo.js` com o botão de pausa não ficou guardada (a sessão caiu no meio da troca). Capturas: `.playwright-mcp/capa_fluxo_1440_t3s.png`, `_t8s.png`, `_reduzido.png`, `capa_fluxo_1280.png`, `capa_fluxo_1920.png`, `capa_fluxo_390.png`. |

## A confirmar com o Caio

- A redação do subtítulo.
- A velocidade e a quantidade de itens do fluxo (hoje 26, ciclos de 8,7 a 14,7 s).
- O botão no plano marinho, em amarelo (escolhido: fica no eixo da ilustração e fecha o fluxo). A alternativa é no lado
  branco, em azul VIU, ao lado da data.
