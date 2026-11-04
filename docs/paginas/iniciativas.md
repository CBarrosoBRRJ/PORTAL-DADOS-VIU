# Iniciativas de automação e IA (V2)

**Fotos da MIA e tipo dos arquivos (Caio e gerente, 03/11/2026, noite):** o card MIA mostra as duas imagens da Central de qualidade (`catalogo.FOTOS["mia"]`, lidas de `app/static/roadmap/`, as mesmas dos dashboards do Roadmap, sem cópia; `pasta` opcional em cada foto). Bug visto pelo gerente: o "Abrir em nova aba" do visor **baixava** a imagem, porque o servidor mandava `.webp` como `application/octet-stream` (o Python do Windows e da imagem slim não conhece o tipo) com `nosniff`; corrigido registrando `.webp`, `.woff2`, `.vtt` e `.mp4` em `app/main.py` (teste `tests/test_tipos_estaticos.py`).

**Foto fixa do Raio-X (Caio, 03/11/2026):** o print do painel Raio-X dos talentos saiu do Roadmap e virou foto do card Raio-X: arquivo do site (`app/static/iniciativas/raio-x.webp` e `-mini`), declarado em `catalogo.FOTOS` (chave = id do item), sem passar pelo banco, então aparece igual no computador, na VPS e no Cloud Run. Entra como 1º anexo na galeria e no visor (`api.fotos_fixas`, com `?v=` da versão do arquivo), marcado `fixo` (sem "Remover" na edição). Testes `tests/test_iniciativas_fotos.py`.

**Atualização de 03/11/2026 (Caio):** 13 iniciativas. Em produção: **MIA** (Monitoramento Inteligente
Automatizado; robô que revisa o board do Backlog todo dia, corrige no monday.com o que foi preenchido errado, guarda o
valor original e manda para revisão o que tem dúvida). FILA virou "Priorização da demanda" (sem Raio-X). Na esteira:
**Raio-X dos talentos** (características e dados de cada talento; texto proposto pelo Claude, a confirmar). G1.IA:
"Revisão de matérias publicitárias", descrição do Caio ("Agente de IA que revisa e valida textos de branded content e
conteúdos publicitários publicados nos ambientes Globo (Branded Content Afiliadas)"). Mudança no `catalogo.py` e aplicada
no banco local com `tools/iniciativas_admin.py restaurar-catalogo` (backup antes). **Produção (Firestore) não muda
sozinha:** a semente só roda em banco vazio; incluir lá pela tela do link restrito ou restaurar o catálogo no Firestore.

**Estado (31/10/2026, dados no servidor):** a página virou ferramenta com **dados persistentes no servidor**, anexos
e galeria, a pedido do Caio e do gerente. Criar, editar, mover, excluir e anexar ficam salvos no servidor, sobrevivem
a recarregar, a fechar o navegador e aparecem em qualquer outro navegador. Rota `/viu-agenciamento/iniciativas#1`.
O `catalogo.py` virou **semente** (o quadro nasce dele na 1ª execução) e histórico; depois disso, o quadro salvo é a
fonte da página. Pronta para deploy (Cloud Run + IAP), **nada publicado** e **nada criado no GCP**: roteiro em
[`docs/deploy_iniciativas.md`](../deploy_iniciativas.md).

> A versão anterior (alterações só no `localStorage` do navegador, chave `ini-quadro:v1`) foi substituída. Quem tiver
> alterações guardadas nessa chave vê, uma vez, "Importar alterações deste navegador" no painel (só enquanto o quadro do
> servidor estiver na semente); depois a chave é apagada. Arquivos antigos em
> `_descartados/2026-10-30/iniciativas_antes_do_servidor/`.

Arquivos: `app/apresentacoes/gestao_orcamentos/iniciativas/` (`catalogo.py` semente, `repositorio.py` dados,
`api.py` API, `__init__.py` tela, `template.html`), `app/static/iniciativas.js`, `app/iap.py` (AUTH=iap), classes
`.ini-*` em `estilo.css` (bloco "Iniciativas, dados no servidor" antes do D46), ícones `clipe` e `documento` novos,
`tools/iniciativas_admin.py` (backup e restauração), testes em `tests/test_iniciativas_servidor.py` e
`tests/test_v2_paginas.py`.

## Arquitetura (31/10/2026)

| Camada | O que faz | Onde |
|---|---|---|
| Quadro (regras) | semente do catálogo, validação, ordem por fase, exclusão lógica, anexos, importação única | `repositorio.Quadro` |
| Backend local (padrão no computador) | SQLite + pasta de anexos **fora do Google Drive** (SQLite em pasta sincronizada pode corromper) | `repositorio.SqliteBackend` |
| Backend de produção (padrão no Cloud Run) | Firestore (coleções `iniciativas`, `anexos`, `iniciativas_meta`) + bucket privado do Cloud Storage (objetos `anexos/<iniciativa>/<uuid>.<ext>`), credenciais ADC da conta de serviço | `repositorio.FirestoreBackend` |
| API JSON | leitura aberta; escrita com guarda (edição ligada + CSRF) | `api.py`, prefixo `/viu-agenciamento/iniciativas/api` |
| Página | renderizada do quadro salvo (sem JS: só leitura); com JS, ferramenta, galeria, visor e "Expandir" | `__init__.tela()`, `template.html`, `iniciativas.js` |

Escolha do backend por variável (`INICIATIVAS_BACKEND`: `sqlite` no computador, `firestore` com `K_SERVICE`). Os
dois têm a mesma interface pequena (`iniciativas`, `gravar`, `meta`, `meta_gravar`, `meta_criar`, `anexos`,
`gravar_anexo`, `ler_anexo`, `apagar_anexo`); as regras ficam no `Quadro`, iguais para os dois. Dependências novas:
`python-multipart` (upload), `google-cloud-firestore` e `google-cloud-storage` (só usadas em produção; importadas na
1ª chamada).

**Onde ficam os dados no computador:** banco `C:\Users\CCMB\.ppd-agenciamento-v2\iniciativas.db` (`INICIATIVAS_DB`) e
anexos em `C:\Users\CCMB\.ppd-agenciamento-v2\anexos\` (`INICIATIVAS_ANEXOS`). Não ficam no Drive nem vão para a imagem
(`.gcloudignore`/`.dockerignore`). Os testes usam sempre um banco temporário (`tests/conftest.py`, fixture
`quadro_limpo`).

**Tabelas (SQLite; no Firestore, os mesmos campos por documento):**
- `iniciativas`: `id` (do catálogo, ex. `orca-ai`; novas `ini-<10 hex>`), `sigla`, `nome`, `fase`, `ordem`,
  `responsavel`, `descricao`, `status`, `proximo`, `link_rotulo`, `link_href` (botão "Ver resultados", só da semente),
  `semente`, `criado_em`, `atualizado_em`, `atualizado_por` (e-mail do IAP em produção), `excluido` (exclusão lógica).
- `anexos`: `id` (uuid), `iniciativa_id`, `nome_original` (só legenda), `arquivo` (`<uuid>.<ext>`, nunca o nome do
  usuário), `tipo`, `tamanho`, `ordem`, `criado_em`. Remover anexo apaga o registro e o arquivo.
- `meta`: `semeado_em` (a semente roda uma vez, mesmo com duas instâncias) e `alterado` (0 enquanto o quadro está na
  semente; condição da importação do navegador). **F04 (31/10/2026):** a semente é transacional (`backend.semear`): no
  SQLite, itens + marcas numa transação só (`BEGIN IMMEDIATE`); no Firestore, num batch só, com `semeado_em` como
  `create` depois dos itens. Falha no meio = nada gravado, e a próxima leitura tenta de novo; marca sem nenhum item
  (estado que a versão anterior podia deixar) = semeia de novo.

**Concorrência:** uma trava por processo serializa as escritas. No Cloud Run com mais de uma instância, duas pessoas
mexendo na mesma coluna no mesmo segundo podem deixar um empate de `ordem`, que a próxima mudança renumera; para a
reunião, o roteiro usa `--max-instances=1`.

## API (contrato)

Prefixo `/viu-agenciamento/iniciativas/api`. Escritas exigem `X-Requested-With: iniciativas` e, quando o navegador
manda, `Origin`/`Sec-Fetch-Site` do próprio site (senão 403); com a edição desligada, 403.

| Método e caminho | Corpo | Resposta |
|---|---|---|
| `GET /iniciativas` | — | `{iniciativas: [...], anexos: {id: [...]}, na_semente, edicao}` |
| `POST /iniciativas` | `{sigla, nome, fase, responsavel, descricao, status, proximo}` | 201 + iniciativa (fim da coluna) |
| `PUT /iniciativas/{id}` | campos parciais (mudou a fase: vai para o fim da nova coluna) | 200 + iniciativa |
| `POST /iniciativas/{id}/mover` | `{fase, posicao}` (posição 0..n, ajustada) | 200 + iniciativa |
| `DELETE /iniciativas/{id}` | — | 204 (exclusão lógica) |
| `GET /iniciativas/{id}/anexos` | — | lista |
| `POST /iniciativas/{id}/anexos` | `multipart/form-data`, campo `arquivo` | 201 + anexo |
| `DELETE /anexos/{aid}` | — | 204 |
| `GET /anexos/{aid}/arquivo` | — | o arquivo (`inline`, tipo certo, `nosniff`, CSP própria) |
| `POST /importar` | estado do `localStorage` antigo | `{incluidas, editadas, excluidas}`; 409 se o quadro já mudou |

Validação (Pydantic + regras): sigla ≤ 40, nome ≤ 120, descrição ≤ 400, responsável ≤ 80, status e próximo passo ≤ 120;
sigla ou nome obrigatório; fase entre as 4 do catálogo; campos extras recusados (422). Erros: 400 regra, 404 não
achou, 409 importação recusada, 413 arquivo grande, 415 tipo, 422 contrato, 503 armazenamento fora (a mensagem vai à
tela). Toda escrita gera um log estruturado (`iniciativas: criada/editada/movida/...`, com o usuário).

## Segurança

- **Escrita bloqueada em produção por padrão** (`INICIATIVAS_EDICAO` = `off` com `K_SERVICE`); leitura funciona.
  Liga com `INICIATIVAS_EDICAO=on` **só** com o serviço atrás do IAP (`AUTH=iap`) ou, no futuro, com o login da fase 2.
- **CSRF mínimo:** cabeçalho próprio + mesma origem nas escritas.
- **Anexos:** extensão **e** assinatura (PNG, JPEG, WebP, GIF, PDF; SVG, HTML e o resto recusados — risco de XSS),
  até 10 MB (conferido no `Content-Length`, nos bytes contados durante a recepção — 413 mesmo sem `Content-Length`,
  F11 de 31/10/2026 — e na regra; a gravação roda em `run_in_threadpool`), até 30 por iniciativa, nome salvo = uuid. Servidos
  pelo app com `Content-Type` do tipo conferido, `X-Content-Type-Options: nosniff`, `Content-Disposition: inline`,
  `Cross-Origin-Resource-Policy: same-origin` e CSP própria (`default-src 'none'; img-src 'self'; style-src
  'unsafe-inline'; object-src 'self'; frame-ancestors 'self'`), que permite o visor de PDF do navegador num quadro do
  próprio site. A CSP das páginas **não mudou** (`frame-src` cai em `default-src 'self'`).
- **AUTH=iap** (exceção temporária à D10, para a reunião do gerente): o app confere o JWT do IAP em toda requisição
  (`app/iap.py`; 401 sem ele). `AUTH=off` continua recusado em produção.
- Sem `style="` no HTML; o JS não usa `innerHTML` (só `textContent` e nós criados).

## Interface (31/10/2026)

- **Layout:** o quadro desce (margem de 2,4em sob o título, antes 1,5em) e estica até o pé da lâmina (`flex: 1`), sem a
  faixa branca de baixo; cartões da densidade 1 maiores (sigla 1,36em, mais respiro); painel 20em. Medido
  (Chrome headless, 4 colunas com 3/2/3/3–4 cartões): 1440×810 quadro 235–734 px (lâmina até 754), 1280×720 208–646
  (até 664), 1920×1080 318–997 (até 1024), nenhuma coluna rola e nenhuma rolagem da página; 390 px sem rolagem lateral.
- **Detalhe (painel):** fase, sigla, nome, descrição, responsável/status/próximo passo, botões "Ver resultados"
  (LIA), **"Expandir"** e "Fechar", e a **galeria** (miniaturas num trilho horizontal com setas que só aparecem quando há
  mais para rolar; imagem com `object-fit: cover`, PDF com ícone e nome). Com anexos, o detalhe fica mais compacto.
- **Visor** (`<dialog>` com `showModal`, padrão do pop-up do vídeo da LIA): imagem grande (`object-fit: contain`) ou o
  PDF num quadro do próprio site, botões anterior/próximo, ← → no teclado (não trocam de página do portal), contador
  "2 de 3", legenda com o nome, "Abrir em nova aba", Esc e clique no fundo fecham, foco devolvido à miniatura.
- **Expandir** (visão ampliada, `<dialog>`): fase, sigla grande, nome, descrição, responsável/status/próximo passo,
  "Ver resultados", "Editar e anexar" (com edição ligada) e a galeria grande; clicar abre o visor por cima; Esc fecha um
  de cada vez.
- **Pop-up de edição:** os campos de antes + **Anexos** (lista com miniatura, nome e "Remover", com confirmação; "Anexar
  imagem ou PDF", vários de uma vez, envia na hora; recusa local de tipo e tamanho com mensagem `role="alert"`). Numa
  iniciativa nova, "Salve a iniciativa para anexar". Aviso no topo: "Salvo no servidor: vale para todos que abrirem o
  portal."
- **Estados:** aviso flutuante no pé da tela (`aria-live="polite"`): "Salvando…", "Salvo", "Anexo salvo" e erros
  (ex.: "Sem conexão com o servidor…"). Criar/editar só fecham o pop-up e pintam "Salvo" **depois** do OK do servidor;
  se falhar, o pop-up fica aberto com a mensagem (`role="alert"`). Mover e excluir são otimistas: se o servidor falhar,
  o quadro volta ao que está salvo e avisa ("… O quadro voltou ao que está salvo."). Nada falha em silêncio.
- **Excluir** agora pede confirmação (o efeito vale para todos).
- **Movimento:** sem loop. Entrada em onda das colunas e cartões, medidor acendendo e, no hover, o cartão sobe 2 px com
  um brilho leve na borda (parado durante o arrasto); pop-ups surgem em 300 ms; tudo só com
  `prefers-reduced-motion: no-preference` e `html.js`. As linhas tracejadas animadas de fundo (pedido do Caio de 30/10)
  foram testadas e **retiradas** por decisão dele ("ficou feia"; bloco guardado em
  `_descartados/2026-10-30/iniciativas_antes_do_servidor/estilo_ini_linhas_de_fundo.css`).
- "Copiar resumo" e "Restaurar o catálogo" saíram da tela. Restaurar virou ação de administração:
  `python tools/iniciativas_admin.py restaurar-catalogo --confirmo-restaurar` (faz backup antes).

## Backup (computador)

`python tools/iniciativas_admin.py backup` grava `~/.ppd-agenciamento-v2/backups/iniciativas_AAAAMMDD-HHMMSS.zip`
(cópia consistente pela API de backup do SQLite, mesmo com o servidor no ar, + a pasta de anexos); `--destino` muda a
pasta. Para voltar: parar o servidor, descompactar `iniciativas.db` e `anexos/` nos caminhos de `INICIATIVAS_DB` e
`INICIATIVAS_ANEXOS`, subir de novo. `python tools/iniciativas_admin.py resumo` mostra quantas iniciativas e anexos há.
Em produção: `gcloud firestore export` + cópia do bucket (comandos no roteiro de deploy, bloco 9).

## Produção (GCP)

Roteiro completo, numerado e explicado em [`docs/deploy_iniciativas.md`](../deploy_iniciativas.md) (APIs, Firestore
`(default)` nativo, bucket privado com acesso uniforme e prevenção de acesso público, papéis mínimos da conta de
serviço — `roles/datastore.user` no projeto e `roles/storage.objectAdmin` só no bucket —, deploy com IAP e
`--no-allow-unauthenticated`, `roles/iap.httpsResourceAccessor` para o gerente e o Caio, verificação, checklist da
reunião e como tirar do ar). Caminho principal: **Cloud Run protegido por IAP**, `AUTH=iap`,
`INICIATIVAS_BACKEND=firestore`, `INICIATIVAS_BUCKET=…`, `INICIATIVAS_EDICAO=on`. Nada foi executado no GCP.

## Testes e validação (31/10/2026)

- `tests/test_iniciativas_servidor.py` (30 testes): semente única; CRUD, mover (renumera destino e origem), exclusão
  lógica, restaurar; importação do navegador (e 409); API ponta a ponta com a página renderizada do banco; validação
  (422/400/404); CSRF (sem cabeçalho, outro cabeçalho, outra origem, `cross-site` → 403); produção simulada (escrita
  403, leitura 200, página com `data-ini-edicao="off"`); padrões com `K_SERVICE`; upload válido (PNG, JPEG, WebP,
  GIF, PDF; nome salvo uuid; cabeçalhos do arquivo) e inválido (SVG, HTML, SVG com extensão .png, assinatura trocada,
  sem extensão, .exe, vazio, > 10 MB); fallback para o catálogo se o armazenamento cair; backend Firestore + Storage
  com falsos (semente, ordem, exclusão, anexos no bucket, 2ª réplica, prefixo, falhas → indisponível); fábrica pela
  configuração; IAP (assinatura, público, emissor, chave errada; 401 em tudo sem cabeçalho; `atualizado_por` com o
  e-mail); **persistência de ponta a ponta** (cria, edita, move, exclui e anexa; "reinicia" o processo; API e página
  mostram tudo igual); **falha na gravação** (503, nada muda, o JS só diz "Salvo" depois do OK).
- Navegador (Chrome headless, servidor de teste na porta 8401 com banco no scratchpad; o 8400 e o banco real não foram
  usados nos testes): roteiro completo (criar, anexar 2 imagens sintéticas + 1 PDF, SVG recusado no navegador,
  galeria, visor 1→2→3 (PDF)→2, Esc devolve o foco, Expandir, visor sobre o Expandir com Esc um de cada vez,
  recarregar = persistiu, Alt+← = moveu e persistiu, excluir = sumiu depois de recarregar, console sem erros) e
  **dois perfis de navegador**: o que o perfil A gravou (criar, responsável, anexo, mover, excluir MATCH) o perfil B
  viu; B editou e A viu; A fechou o navegador e abriu de novo: tudo lá; com a rede derrubada em B, criar mostrou "Sem
  conexão com o servidor…" no pop-up e no aviso `aria-live` e não criou o cartão; mover voltou ao estado salvo.
- Capturas em `.playwright-mcp/`: `ini-servidor-{1440x810,1280x720,1920x1080,390}.png`,
  `ini-servidor-popup-nova-1440x810.png`, `ini-servidor-popup-anexos-1440x810.png`,
  `ini-servidor-detalhe-galeria-1440x810.png`, `ini-servidor-visor-{1,2,pdf}-1440x810.png`,
  `ini-servidor-expandir-1440x810.png`, `ini-servidor-depois-de-excluir-1440x810.png`,
  `ini-persistencia-perfil-B-ve-o-que-A-gravou.png`, `ini-persistencia-perfil-A-reaberto.png`,
  `ini-persistencia-falha-ao-salvar.png` (as `ini-v3-*` são da versão com as linhas de fundo, retiradas).

---

O texto abaixo descreve o desenho e a ferramenta de 30/10/2026; onde fala em `localStorage`, "Copiar resumo" e
"Restaurar o catálogo", vale o que está acima.

**Pergunta:** Quais iniciativas de automação e IA estamos tocando?

## Conteúdo

Fonte: planilha `iniciativasVIU-automacao-ia.xlsx`, curada à mão em `catalogo.py` (não vem do BigQuery). 4 faixas e 11
quadros: Em produção (LIA, GPS), Fase de testes (Orça+AI, COP.IA), Em desenvolvimento (FILA, CACHÊ, G1.IA), Na esteira
(Salesforce, MATCH, Auto+, GUIA+). Incluir projeto = copiar um item; fase nova = novo grupo + cor `.ini-<chave>`.

## Desenho (30/10/2026)

Quadro de fases em colunas, lido da esquerda para a direita da mais madura à próxima (ordem do catálogo: Em produção,
Fase de testes, Em desenvolvimento, Na esteira), e um painel fixo à direita para o detalhe.

- **Coluna da fase:** contagem em serifa grande na cor da fase, medidor de maturidade (4 degraus; acende `nivel` =
  nº de fases − posição, então Em produção acende 4 e Na esteira 1), nome da fase e a frase. Fundo pastel por fase; Na
  esteira sem fundo e com borda tracejada (ainda não começou). A contagem também vai ao leitor de tela ("2 iniciativas");
  o medidor é decorativo (`aria-hidden`), a fase está sempre escrita.
- **Quadro:** sigla em serifa e nome abaixo (sem sigla, o nome é o título), seta à direita; botão com sombra em camadas
  como os do Roadmap. Aberto: borda azul VIU.
- **Painel:** vazio, mostra o total (11 iniciativas) e "Clique em uma iniciativa para ver o que ela faz". Com um quadro
  aberto, o detalhe cobre o painel: fase (medidor + texto), sigla grande, nome em itálico, descrição (`desc` ou, se
  vazia, `curta`), botão "Ver resultados" quando o item tem `link` (hoje só a LIA → `/viu-agenciamento/lia#1`) e
  "Fechar".
- **Estreito (≤ 900 px):** colunas em duas (uma ≤ 560 px), sem painel; o detalhe abre logo abaixo do quadro e a seta gira
  para baixo.

## Ferramenta do quadro (30/10/2026)

O Caio não tinha certeza da fase de cada iniciativa e quis ajustar na tela, como num kanban; depois pediu para usar a
página como ferramenta (pop-up, incluir, quadro que aguenta crescer). Só com JS (`iniciativas.js`, 2º bloco; classe
`.ini-editavel`); sem JS a página é só leitura (botões `hidden`, `<dialog>` fechado).

- **Clique alterna o detalhe:** clicar no cartão abre o detalhe no painel; clicar de novo no mesmo cartão fecha e volta ao
  resumo ("11 iniciativas" / "Clique em uma iniciativa para ver o que ela faz."); o botão Fechar, o Esc e o clique fora
  também fecham (eventos delegados, valem para os cartões incluídos).
- **Arrastar e soltar** (Pointer Events, sem biblioteca): leva o cartão a outra coluna ou posição. Limiar de 6 px (abaixo é
  clique); o clique que vem com o soltar é descartado. Cópia seguindo o ponteiro, vaga tracejada, contorno na coluna de
  destino, contagens ao vivo; perto da borda de uma coluna que rola, ela rola junto. Esc cancela. No toque: segurar
  ~0,35 s antes (sem isso é rolagem).
- **Teclado:** com o cartão em foco, Alt + ← / → muda a fase e Alt + ↑ / ↓ a ordem; as setas simples seguem trocando de
  página. O atalho está só para leitor de tela (`so-leitor`, ligado aos cartões por `aria-describedby` e
  `aria-keyshortcuts`); cada mudança é anunciada num `aria-live="polite"`.
- **Pop-up (`<dialog>` com `showModal`)**, aberto pelo lápis do cartão ("Editar iniciativa: <sigla>") ou pelo
  "+ Nova iniciativa" no pé de cada coluna: Sigla, Fase (seletor; mudar move o cartão ao salvar, para o fim da coluna),
  Nome / título, Responsável (pessoa ou área), Descrição (é a do detalhe) e, opcionais, Status / observação e Próximo
  passo. Salvar (Enter; na Descrição, Shift + Enter quebra a linha), Cancelar e Esc fecham e devolvem o foco ao cartão
  (ou ao "+ Nova"); Excluir só na edição. Sigla e nome vazios: erro ligado aos campos (`aria-invalid`,
  `aria-describedby`). Dentro do pop-up as setas não trocam de página. Vidro, sombra em camadas, botões de 6 px; entra
  (260 ms) só com movimento permitido. Em 390 px, uma coluna de campos.
- **✕ do cartão** tira o cartão (sem confirmação); o incluído some de vez.
- **Detalhe:** passa a mostrar Responsável (vazio no catálogo = "a definir"; nenhum nome inventado) e, se preenchidos,
  Status e Próximo passo. `responsavel`, `status` e `proximo` são campos opcionais novos do catálogo (hoje vazios).
- **Painel sem barra de edição** (Caio): o aviso, "Copiar alterações" e "Restaurar original" saíram da tela. O aviso
  "Salvo só neste navegador; o catálogo não muda" fica no topo do pop-up. **Saída para voltar ao catálogo:** no pé do
  pop-up, só quando há alteração, "Este navegador tem alterações no quadro" com **Copiar resumo** e **Restaurar o
  catálogo** (pede confirmação). Escolhido por ser o mais simples de achar sem poluir a tela (sem parâmetro na URL).
- **Copiar resumo** gera, por exemplo: `- LIA → Fase de testes (posição 3 de 4)`, `- FILA renomeada para RAIO-X — …`,
  `- FILA — responsável: Time de Dados`, `- FILA — status: Piloto em novembro`, `- Auto+ excluída`,
  `- + Nova: XYZ — Painel de contratos (Na esteira); descrição: …`, `- Nova ordem em …`. É assim que o Caio leva as
  mudanças ao `catalogo.py` (ou lendo o próprio quadro).
- **Quadro que aguenta crescer:** `data-densidade` por coluna, calculado no servidor (`iniciativas.densidade`) e
  recalculado pelo JS a cada mudança: até 3 cartões = 1 (como antes), 4 = 2 (mais justo; nome em até 2 linhas), 5 ou
  mais = 3 (compacto; nome em 1 linha com reticências, inteiro no detalhe). Piso legível: sigla 1em, nome 0,72em em
  `--tinta-2` (≥ 4,5:1). Acima do que cabe, a lista rola por dentro (a página nunca rola), barra fina e esmaecido embaixo
  enquanto houver mais (`.ini-mais`); o detalhe não é cortado (o contêiner dele é o `.ini`, fora da área que rola). No
  estreito (≤ 900 px) não há rolagem interna.
- **Onde salva:** `localStorage`, chave `ini-quadro:v1`: `{fases: {chave: [ids]}, dados: {id: campos editados},
  novos: {id: campos}, excluidos: [ids]}` (try/catch; aba privada funciona na visita, não persiste; sem alteração, a
  chave é apagada). `id` do catálogo vem de `__init__.py` (ex.: `orca-ai`); incluídos usam `nova-<tempo>`. Item novo no
  catálogo aparece na sua fase mesmo para quem já editou. Nada vai ao servidor.
- CSP: a cópia do arrasto usa `element.style` (CSSOM), aceito por `style-src-attr 'none'` (sem erro no console); o HTML
  segue sem `style="`. FLIP com `element.animate` (180 ms) só com movimento permitido; depois da 1ª mexida a entrada em
  onda não se repete (`.ini-mexido`).

**Validado em 30/10/2026** (Chrome headless próprio, porta 8400; o Playwright MCP estava em uso por outro agente):
- Densidade, com cartões incluídos de nome longo, em 1440×810, 1280×720 e 1920×1080: 3 por coluna (densidade 1), 4 em
  todas (2), 5 e 6 em Na esteira (3) **sem rolar**; 8 em Na esteira rola com 6 inteiros e esmaecido. A barra só aparece
  a partir do 7º cartão.
- Clique abre, 2º clique fecha, Fechar fecha; arrasto da LIA para Fase de testes sem abrir o cartão; pop-up da FILA
  (sigla, responsável, status e fase → Fase de testes) com foco de volta no cartão; erro com campos vazios; Esc fecha e
  devolve o foco ao "+ Nova"; nova XYZ em Na esteira abre no detalhe com "Responsável: a definir"; exclusão e recarga
  mantidas; Copiar resumo e Restaurar o catálogo (chave apagada); pop-up em 390 px sem rolar para o lado; console sem
  erros.
- Capturas em `.playwright-mcp/`: `ini-ferramenta-{3longos,4todas,5esteira,6esteira,8esteira}-{1440x810,1280x720}.png`,
  `ini-ferramenta-8esteira-1920x1080.png`, `ini-ferramenta-detalhe.png`, `ini-ferramenta-popup-editar-1440x810.png`,
  `ini-ferramenta-popup-nova-1440x810.png`, `ini-ferramenta-popup-com-restaurar.png`, `ini-ferramenta-nova-no-detalhe.png`,
  `ini-ferramenta-popup-390.png` (as `ini-edicao-*.png` são da 1ª versão, com a barra no painel).

## Regras de tela (PRD)

- Uma descrição aberta por vez (RF5). Fecha ao clicar fora, com Esc ou no botão Fechar; o foco volta ao quadro (RF6).
- Sem JS, os `details` abrem e fecham sozinhos e o detalhe aparece no mesmo painel; o Fechar fica oculto (`hidden`).
- O detalhe nunca fica cortado: ocupa a área fixa do painel (posição absoluta no contêiner `.ini`; nenhum ancestral
  entre os dois tem `position` ou `transform`, por isso a entrada anima só o topo das colunas e os quadros). Texto longo
  rola dentro do painel.
- Incluir projeto = copiar um item em `catalogo.py`; a coluna cresce sozinha. Fase nova = grupo novo + cores em
  `.ini-<chave>` (`--ini-cor` e `--ini-fundo`); o medidor e as colunas se ajustam ao número de fases. `link` opcional
  vira o botão de resultados. `REFERENCIA` vazia = sem nota.
- Movimento só com `prefers-reduced-motion: no-preference` e `html.js`: topo das colunas e quadros entram em onda
  (até ~1 s), o medidor acende e o detalhe desliza para o painel (320 ms). Sem laço.

Validado em 30/10/2026 (Playwright, porta 8400): cabe numa tela sem rolagem em 1440×810, 1280×720 e 1920×1080; 390 px
sem rolar para o lado; G1.IA (texto mais longo) sem corte em 1280×720; teclado (Enter abre, Esc fecha e devolve o foco),
clique fora, botão Fechar e funcionamento sem JS conferidos. Capturas em `.playwright-mcp/ini-*.png` da V2.

## Pendências (do PRD)

Data de referência do andamento; confirmar FILA, CACHÊ e G1.IA em desenvolvimento; manter ou tirar `curta` (hoje só
aparece se `desc` estiver vazia); outras iniciativas com página ou resultados para ganhar o botão `link`.

## Histórico

- 04/11/2026 (revalidação): a seta "anterior" da galeria do detalhe ficava ligada já no início (o scroll-snap alinhava a 1ª miniatura à borda do padding, `scrollLeft` 3 a 5 px); `scroll-padding-inline: 0.2em` em `.ini-galeria-lista` (`estilo.css`). Teste `test_galeria_do_detalhe_comeca_no_zero_e_seta_anterior_desligada`. Conferido no Chrome headless: 13 cards nas 4 colunas, galeria do Raio-X (10) e da MIA (2) dentro da caixa em 1280, 1440, 1920 e 390 px, visor com as 10 fotos na ordem, "Abrir em nova aba" como `image/webp`.
- 03/11/2026 (revisão): o visor cortava imagens altas (a Central de qualidade, 960×805, saía com 987 px numa área
  de 740 px em 1440×900): `.ini-v-midia` com `grid-template: minmax(0, 1fr) / minmax(0, 1fr)`. Nos cards com galeria
  (MIA, 2 fotos), a sigla vai a 1,7 em e, na mesa (> 900 px), o nome a 1 em e a descrição a 0,9 em (o detalhe passava
  28–40 px da caixa em 1536–2560 px). As 10 fotos `raio-x-*.webp` (+ `-mini`) foram ligadas ao card Raio-X em
  `catalogo.FOTOS` (originais em `_descartados/2026-11-03/app/static/iniciativas/`).
- 31/10/2026 (auditoria do Codex, F10): rodapé "Conteúdo editorial · não depende da carga de dados" no lugar da data da carga de entradas.
- 30/10/2026: criada na V2 a partir do PRD de @cris.
- 30/10/2026 (noite): redesenho a pedido do Caio: faixas com caixinha flutuante → colunas por fase com contagem e
  medidor de maturidade, detalhe num painel fixo à direita, botão "Ver resultados" da LIA e botão Fechar. Conteúdo do
  catálogo mantido (só o campo `link` novo). Versão anterior em `_descartados/2026-10-30/`.
- 30/10/2026 (noite): edição no quadro a pedido do Caio (arrastar entre fases e na ordem, lápis, ✕, Alt + setas,
  Copiar alterações, Restaurar original), só no navegador; `id` estável por item em `__init__.py`; ícone `lapis`. JS
  anterior em `_descartados/2026-10-30/app/static/iniciativas_antes_da_edicao.js`.
- 30/10/2026 (noite, 2ª leva): ferramenta do quadro: pop-up (`<dialog>`) para editar e incluir (campos responsável,
  descrição, status e próximo passo; responsável vazio = "a definir"), "+ Nova iniciativa" por coluna, densidade por
  coluna e rolagem interna (5 e 6 cartões sem rolar), barra de edição tirada do painel (copiar e restaurar no pé do
  pop-up), clique alterna o detalhe.
- 31/10/2026 (madrugada): dados no servidor (SQLite fora do Drive no computador; Firestore + Cloud Storage em produção), API JSON com
  CSRF mínimo e escrita bloqueada em produção por padrão, anexos com galeria, visor e "Expandir", layout que ocupa a lâmina, AUTH=iap
  para a publicação temporária do gerente, roteiro de deploy (`docs/deploy_iniciativas.md`), importação única do localStorage,
  `tools/iniciativas_admin.py`; linhas animadas de fundo testadas e retiradas a pedido do Caio. Antes em
  `_descartados/2026-10-30/iniciativas_antes_do_servidor/`.
