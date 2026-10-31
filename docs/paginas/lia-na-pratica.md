# A LIA na prática — vídeo (V2)

**Estado (30/10/2026, noite):** o vídeo virou **pop-up da página LIA** (botão "Ver a LIA na prática", pedido do Caio);
esta página ficou **oculta** (`oculta=True`: fora da navegação, da capa e da sequência; LIA → Iniciativas) e continua
abrindo pelo endereço `/viu-agenciamento/lia-na-pratica#1`, que é o destino do botão sem JS. Pendente: o arquivo do
vídeo. Conforme o PRD do slide do vídeo de @cris (no projeto dela era `/funcionamento`).
Arquivos: `app/apresentacoes/gestao_orcamentos/lia_na_pratica/` (`__init__.py` com `ARQUIVO`, `CAPA`, `LEGENDAS`,
`ETAPAS`, a fonte única do pop-up e desta página; `template.html`), classes `.fn-*` em `estilo.css`, ícone `video`,
pasta `app/static/video/` (com `LEIA-ME.md`), pop-up em `lia/template.html` + `app/static/lia_video.js`,
`tests/test_v2_paginas.py`.

**Pergunta (título):** A LIA na prática: do e-mail à carta orçamento.

## Regras

Botão sempre visível por decisão do Caio, 31/10/2026 (F09 da auditoria do Codex: a sugestão de esconder o botão sem o
vídeo foi descartada). Sem `ARQUIVO`: quadro marinho "Vídeo a incluir" (`role="img"` com descrição), sem player. Com `ARQUIVO` (MP4 em
`app/static/video/`, servido como `/static/video/<nome>`): `<video controls preload="metadata">`, sem autoplay, `poster` se houver `CAPA`, legenda pt-BR ligada se
houver `LEGENDAS` (.vtt). Tudo do próprio site (CSP). 16:9 sem esticar (fundo preto, `object-fit: contain`). Seis
etapas na ordem, cada uma com a iniciativa e a fase (catálogo das Iniciativas): as duas últimas (Orça+AI, COP.IA) estão
em fase de testes, e o vídeo precisa refletir isso.

Pop-up (na página LIA): `<dialog>` com `showModal()`, ~86% da largura (celular: tela toda menos 8 px de cada lado),
fundo escurecido e desfocado, entra crescendo a partir do botão (só com movimento permitido); vídeo 16:9 à esquerda e
"O que o vídeo mostra" à direita (no celular, embaixo). Fecha com Fechar, Esc ou clique no fundo; o vídeo **pausa ao
fechar**; o foco volta ao botão; setas dentro do pop-up não trocam de página. Sem autoplay: o play é da pessoa.

**Para incluir o vídeo:** salvar `app/static/video/lia-na-pratica.mp4` (e, se houver, `lia-na-pratica.jpg` e
`lia-na-pratica.vtt` na mesma pasta), preencher `ARQUIVO = "lia-na-pratica.mp4"` (e `CAPA`/`LEGENDAS`) em
`lia_na_pratica/__init__.py`; trocar `estado` para "pronta" e tirar `nota_estado` em `apresentacao.py`; rodar os
testes.

## Pendências (do PRD)

Gravar o vídeo (duração e tamanho máximos), legendas e capa; confirmar as seis etapas com a equipe; título e rótulo
finais.

## Histórico

- 31/10/2026 (auditoria do Codex, F10): rodapé "Conteúdo editorial · não depende da carga de dados" (página oculta e pop-up).
- 30/10/2026: criada na V2 a partir do PRD de @cris.
- 30/10/2026 (noite): vídeo em pop-up na página LIA; página oculta (endereço mantido); arquivos em `app/static/video/`.
