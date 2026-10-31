# PRD V2 — Portal "ViU Agenciamento" (documento de entrega para auditoria)

| | |
|---|---|
| **Projeto** | `PPD-AGENCIAMENTO-SLA-V2` (cópia de trabalho do portal original, criada em 30/10/2026) |
| **Responsável** | Caio Barroso (dados; administrador). Quem apresenta na reunião é o **gerente do Caio** |
| **Reunião** | Diretoria, **04/11/2026**, com os dados congelados em **31/10/2026** (D65) |
| **Escrito em** | 31/10/2026, a partir do código atual (não da memória). Onde o código e uma ficha divergem, vale o código; a divergência está na seção 10 |
| **Carga vigente** | gold processada em **30/10/2026 09:01 (São Paulo)**, dados até **29/10/2026** (lida em 31/10/2026 02:51 por uma instância local só de leitura) |
| **Endereço** | `/viu-agenciamento/...` desde 31/10/2026 (antes `/gestao-orcamentos/...`, que responde 301; 308 para POST/PUT/PATCH/DELETE). Aba do navegador: só "ViU Agenciamento" |
| **Estado de publicação** | Nada publicado. Roteiro de deploy em `docs/deploy_iniciativas.md` (Cloud Run + IAP), não executado |
| **Testes** | 564 coletados em 31/10/2026 (`tests/`, dados sintéticos, sem BigQuery) |
| **Números de linha** | conferidos no código de 31/10/2026 às 03:10; `app/main.py`, `app/dados.py` e `apresentacao.py` ainda estavam sendo editados por outros agentes, então use também o nome da função citado ao lado |

**Como ler.** Seção 1 = o que é e como se navega. Seção 2 = arquitetura. Seção 3 = uma subseção por página, sempre
na mesma ordem (pergunta → o que mostra → fonte → regras e memória → números → SQL → interações → acessibilidade →
testes → decisões e pendências). Seções 4 a 9 = regras transversais, dados, segurança, desempenho, testes e
pendências. **Seção 10 = pontos para a auditoria** (suspeitas com arquivo e linha; nada foi corrigido).

Documentos de apoio, que este PRD resume e não substitui:

- `CLAUDE.md` (guia de retomada) e `docs/PRD.md` (histórico, decisões D1–D65, seção 9.7 com as decisões abertas DC1–DC16);
- `docs/paginas/*.md` (fichas por página, com memória de cálculo datada, SQL e histórico);
- `docs/deploy_iniciativas.md` (roteiro do Cloud Run + IAP + Firestore);
- `docs/congelar_outubro.md` (roteiro do corte de 31/10; ver seção 5.3);
- `docs/legado/` (os três projetos antigos, só leitura).

---

## 1. Visão geral

### 1.1 Objetivo e público

- **Objetivo:** reunir num só lugar "tudo o que a área analisa, constrói e entrega" (subtítulo da capa): demanda de
  pedidos de orçamento, talentos, prazo de entrega (SLA), automação com a LIA, iniciativas de automação e IA e previsão
  de demanda.
- **Público:** diretoria. O portal é uma apresentação em slides (uma lâmina por página, 16:9) e é apresentado pelo
  **gerente do Caio**, que não é da área de dados. Por isso o estudo do SLA foi enxugado para 5 slides, as frases-resposta
  saem prontas do código e as decisões técnicas ficam nas fichas, não na tela.
- **Base:** board **Backlog 2026 | Agenciamento** (monday), via tabelas e views gold do projeto irmão
  `../PPD-GOLDEN-AGENCIAMENTO-MONDAY` (dataset `gglobo-viu-dados-hdg-prd.gold_monday`).

### 1.2 Sequência da reunião

Sequência calculada por `Apresentacao.vizinhas()` (`app/apresentacoes/__init__.py:89-126`) a partir de `secoes` em
`app/apresentacoes/gestao_orcamentos/apresentacao.py:410-521`:

| # | Página | Rota (sob `/viu-agenciamento`) | Observação |
|---|---|---|---|
| 1 | Capa | `/capa` (a raiz `/` redireciona para cá, `main.py:205-208`) | "Começar" leva ao Roadmap |
| 2 | **Roadmap** (hub) | `/roadmap#1` | `antes_do_inicio=True`; botões levam a cada página |
| 3 | Demanda | `/viu-agenciamento` (página inicial da área) | `rotulo_inicio="Demanda"` |
| 4 | Talentos | `/talentos#1` | filtro `?talentos=` |
| 5 | SLA | `/sla#1` | filtro `?talentos=`; estudo opcional em `/sla/como-medimos` (5 slides) |
| 6 | LIA | `/lia#1` | vídeo em pop-up |
| 7 | Iniciativas | `/iniciativas#1` | quadro editável (dados no servidor) |
| 8 | Previsão | `/previsao#1` | filtro `?talentos=` |
| 9 | Encerramento | `/encerramento` | "Voltar ao início" leva à capa |

O estudo "Como medimos" não está na sequência principal: só entra quando a pessoa está nele
(`__init__.py:118-122`). Dentro do estudo, ← no slide 1 volta ao SLA e → no último slide segue para a LIA (próxima
da sequência).

### 1.3 Navegação

- **Sem abas.** O navegador de abas existe no HTML, mas fica oculto (`hidden`) em Demanda, Talentos, SLA, LIA,
  Iniciativas, Previsão e Roadmap (`templates/macros.html:59-60`).
- **Botões ‹ › ✕ no cabeçalho** (`macros.html:76-83`): ‹ e › seguem a sequência; **✕ volta ao Roadmap**; **no
  próprio Roadmap, ✕ volta à capa** (decisão do Caio, 31/10/2026). No estudo, o ✕ é próprio e volta ao SLA
  (`templates/como_medimos.html:34`; no último slide ganha fundo azul, nome "Fim do estudo: voltar ao SLA").
- **Teclado** (`static/apresentacao.js:277-346`): → / PageDown e ← / PageUp trocam de slide; numa página de um slide só,
  trocam de página; Esc fecha menus e diálogos. Dentro de pop-ups (vídeo, visor das Iniciativas, galeria do Roadmap)
  as setas não trocam de página.
- **Logo** leva à capa; o botão "Capa" existe no navegador oculto.
- **Gancho** "Próxima pergunta" no pé de cada página (`templates/apresentacao.html:95`); no Roadmap e no estudo fica só
  para o leitor de tela (`gancho_oculto=True`).
- **Rodapé datado** em toda página: "Dados até … · atualizados em … · base congelada para a apresentação"
  (`apresentacao.html`; regra 9 do `CLAUDE.md`). Desde a F10 (31/10/2026), página que não mostra a gold leva o rodapé da
  própria fonte (`rodape_texto`): LIA "Dados da LIA até dd/mm/aaaa · extraídos em …" (fim do retrato); Roadmap,
  Iniciativas e vídeo "Conteúdo editorial · não depende da carga de dados". A Previsão acrescenta "acompanhamento até
  dd/mm" e, se o retrato ou o acompanhamento forem de outra carga, um aviso com ícone e texto (F03).
- **Tela cheia** mantida ao navegar (quadro em tela cheia, `frame-ancestors 'self'`).
- **Filtro de talentos** (`?talentos=todos|exclusivos|nao-exclusivos`) é levado de uma página para outra pelos links
  com `data-filtro-talentos` (`apresentacao.js:12-21`).

### 1.4 Páginas ocultas (fora da navegação, endereço mantido)

`oculta=True` tira a seção da navegação, das abas e da sequência; o endereço direto continua abrindo
(`__init__.py:27-28, 71-73`).

| Página | Rota | Por quê | Onde |
|---|---|---|---|
| Atendimento | `/atendimento` | V2 (Caio, 30/10/2026): fora deste relatório | `apresentacao.py:438` |
| A LIA na prática (vídeo como página) | `/lia-na-pratica#1` | virou pop-up da LIA; a página é o destino do botão sem JS | `apresentacao.py:472` |
| Resultado: negócios fechados | `/negocios-fechados` | máscara (sem base); também `na_reuniao=False` | `apresentacao.py:506-507` |
| Qualidade dos dados | `/qualidade` | máscara | `apresentacao.py:518` |
| O que falta | `/o-que-falta` | fecho da área gerado de `pendencias.py`; fora da sequência desde a D59 | `main.py:359-368` |

---

## 2. Arquitetura

### 2.1 Pilha

- **FastAPI + Jinja2** (`app/main.py`), servidor Uvicorn, 1 worker por instância (`Dockerfile`, `CMD`).
- Apresentações como módulos (`app/apresentacoes/__init__.py`, D11/D17): cada pasta tem `apresentacao.py` com
  `APRESENTACAO`; cada seção tem uma subpasta com `template.html` e, quando há, `calculos.py`. Hoje há uma área só:
  `gestao_orcamentos` (slug `viu-agenciamento`, em `gestao_orcamentos/__init__.py`; até 31/10/2026 era `gestao-orcamentos`, que redireciona).
- Templates comuns em `app/templates/` (`apresentacao.html`, `capa.html`, `encerramento.html`, `como_medimos.html`,
  `macros.html`, `icones.html`, `indisponivel.html`, `o_que_falta.html`).
- Estáticos em `app/static/` (CSS único `estilo.css`, um JS por comportamento, fontes locais, imagens do Roadmap,
  pasta `video/`). Versão dos estáticos por hash do conteúdo (`main.py:63-93`, `?v=`).
- Gráficos em HTML/CSS/SVG gerados no servidor; nenhuma biblioteca de gráfico no navegador.

### 2.2 Fonte de dados: só a gold (D57), com duas exceções documentadas

**Regra (D57, 27/10/2026):** cada gráfico lê a sua tabela ou view do `gold_monday`; o site não refaz regra de negócio
(só agrega, arredonda e escreve). Uma variável `TAB_*` por fonte em `app/config.py:24-42` e um objeto `Tabela` por fonte
em `app/dados.py` (lista em `dados.TABELAS`).

| Fonte | Tipo | Variável | Usada em |
|---|---|---|---|
| `gld_agenciamento_2026_sla_movimentos` | tabela | `TAB_SLA` | SLA, estudo (slide 1), gatilho das views do SLA |
| `gld_agenciamento_2026_sla_entregas` | view | `TAB_SLA_ENTREGAS` | SLA, estudo (slides 1–4), capa antiga (típico) |
| `gld_agenciamento_2026_sla_entregas_status` | view | `TAB_SLA_ENTREGAS_STATUS` | estudo (slide 5, "Onde o tempo trava?") |
| `gld_agenciamento_entrada_diaria` | tabela | `TAB_ENTRADA` | Demanda, Talentos (total), Atendimento, rodapé de Roadmap/LIA/Iniciativas/Previsão, gatilho do job da Previsão |
| `gld_agenciamento_fluxo_mensal` | tabela | `TAB_FLUXO` | conferência de carga do extrato da Demanda, Atendimento, cobertura do estudo |
| `gld_agenciamento_fila_mensal` | view | `TAB_FILA` | extrato do mês da Demanda (E7) |
| `gld_agenciamento_atendimento_mensal` | view | `TAB_ATENDIMENTO` | Atendimento (oculta) |
| `gld_agenciamento_2026_saidas_status` | tabela | `TAB_SAIDAS_STATUS` | Atendimento (oculta) |
| `gld_agenciamento_2026_talentos_ano` | tabela | `TAB_TALENTOS_ANO` | Talentos (divisão do ano) |
| `gld_agenciamento_2026_talentos_ranking` | tabela | `TAB_TALENTOS_RANKING` | Talentos (top 10, mapa, corrida) |
| `gld_agenciamento_previsao_mensal` | view | `TAB_PREVISAO_MENSAL` | job de ML (séries Inbound e Mercado) |
| `gld_agenciamento_2026_previsao_exclusividade_mensal` | view | `TAB_EXCLUSIVIDADE_MENSAL` | job de ML (Mercado exclusivos / não exclusivos) |
| `gld_agenciamento_2026_previsao_lotes` | tabela | `TAB_LOTES` | job de ML (diagnóstico de lotes, S6) |
| `silver_monday.slv_agenciamento_2025_itens` | silver | `TAB_SILVER_2025` | só a sensibilidade S5 do ML (fora da tela) |

**Exceções à D57 (fora do BigQuery):**

1. **LIA:** lê `app/apresentacoes/gestao_orcamentos/lia/retrato.json`, contagens agregadas extraídas do Cloud Storage
   da LIA (`gs://gglobo-viu-lia-dados-prd/data/`) por `tools/extrair_lia.py` (só leitura, sem remetente, assunto ou
   conteúdo). O arquivo está dentro de `app/` e entra na imagem.
2. **Iniciativas:** banco próprio (SQLite local ou Firestore + Cloud Storage em produção), editável pela página. A
   semente é `iniciativas/catalogo.py` (curado da planilha `iniciativasVIU-automacao-ia.xlsx`).
3. **Previsão:** a página lê `ml/saida/previsao.json` gravado pelo job de ML (que, ele sim, lê a gold).
4. **Roadmap, capa, encerramento, vídeo:** conteúdo fixo no código (sem dados).

### 2.3 Carga em memória, cache e base congelada

`app/dados.py` (classe `Tabela`):

- **Leitura:** `SELECT <colunas do contrato> FROM <tabela>` pela Storage Read API, com queda para a leitura comum
  (`_baixar`). Rótulos `config.LABELS` no job.
- **Contrato da carga** (`_validar`): colunas obrigatórias, não vazia (salvo `permite_vazia`), chave única,
  `_processado_em` único e não nulo, histórico do SLA contínuo e começando em "Entrada", contagens inteiras e não
  negativas, situações somando as entradas. Carga inválida é recusada e a anterior continua no ar.
- **Recarga pelo metadado:** `get_table(...).modified` (sem custo) a cada `RECARGA_MIN` (5 min); views usam o
  `modified` da tabela de base (`gatilho`). No computador a conferência roda em segundo plano; em produção
  (`K_SERVICE`), `em_fundo=False`: na própria requisição.
- **Aquecimento** (`ao_carregar`): carga nova do SLA já chega com `calculos.entregas` e o estudo dos 3 grupos
  calculados (`apresentacao.py:339-341`); carga nova da entrada avalia o job da Previsão.
- **Caches derivados** por versão da carga (`df.attrs["versao"]`), até 3 cargas.
- **Política de falha:** com carga válida, segue servindo e marca `falha_leitura`; sem carga, `DadosIndisponiveis`
  → página `indisponivel.html` com 503 e `Retry-After`.
- **Estados** (`Tabela.estado`): `em_dia`, `falha_leitura`, `base_atrasada` (a gold não atualizou no horário:
  seg–sex 09:00 + 45 min de tolerância, `config.GOLD_HORA`, `GOLD_TOLERANCIA_MIN`) e `congelada`.
- **Base congelada da reunião (D63):** `CONGELAR=true` por padrão no computador, nunca em produção
  (`config.py:75`): a carga lida na subida não se recarrega.
- **Corte e congelamento em arquivo (D65, 31/10/2026):** `CORTE_DADOS` (padrão `2026-10-31`) escolhe **qual carga**
  fica: a 1ª carga com fim ≥ corte (até `CORTE_FOLGA_DIAS`=1 depois) congela em memória e, quando todas as tabelas
  congelaram, é gravada **como unidade** em `app/base_congelada/` (pasta de versão com um parquet por tabela +
  `manifesto.json` com corte, carga, tabelas e sha256, publicado por último e de forma atômica; F02/F07/F08, 31/10/2026).
  Com a base válida, o portal lê dela sem consultar o BigQuery; em produção o build e o arranque exigem a base (F01) e o
  BigQuery nunca é chamado. Detalhe na seção 5.3. Enquanto o corte está ligado, ele substitui o `CONGELAR` na
  recarga (`dados.py:209-213`).
- **`/saude`**: processo vivo, versão, `processado_em`, linhas, estado e erro de cada tabela e, desde a correção F02
  (31/10/2026), o bloco `base_congelada` (`congelamento.situacao()`): manifesto válido/ausente/inválido, versão,
  `congeladas_em_memoria` × `persistida`, tabelas pendentes, erro da última gravação e tentativas.

### 2.4 CSP e cabeçalhos

Middleware `cabecalhos` (`main.py:153-184`):

- `Content-Security-Policy`: `default-src 'self'; script-src 'self'; style-src 'self' 'nonce-{nonce}';
  style-src-attr 'none'; img-src 'self' data:; font-src 'self'; connect-src 'self'; frame-ancestors 'self';
  base-uri 'self'; form-action 'self'; object-src 'none'` (`main.py:148-150`). Nonce novo por resposta; **nenhum
  `style="…"`** no HTML (alturas e larguras vão num `<style nonce>`), nenhum script inline.
- Anexos das Iniciativas têm CSP própria e mais fechada (`iniciativas/api.py:29`).
- `X-Content-Type-Options: nosniff`, `Referrer-Policy: same-origin`, `X-Frame-Options: SAMEORIGIN`.
- `Cache-Control`: estáticos com `?v=` por 1 ano (`immutable`), sem `?v=` por 1 dia; páginas `private, no-store`.
- `Speculation-Rules: "/especulacao.json"` nas páginas HTML (`main.py:211-231`, desempenho de 31/10/2026): as vizinhas
  da sequência (‹ ›, gancho) e a volta ao Roadmap (✕) são **pré-renderizadas assim que a página abre**
  (`eagerness: immediate`); os destinos do Roadmap e o botão Estudo do SLA têm o HTML baixado na hora (`prefetch` de `.rm-destino, .estudo-link`); os demais
  links internos sem parâmetros são pré-renderizados ao parar o mouse ~200 ms (`moderate`). `/static/*` e `/*/api/*`
  ficam fora.

### 2.5 Controle de acesso (`AUTH`)

`config.AUTH` (padrão `on`) e travas em `main.py:22-32`:

| Valor | Onde | Efeito |
|---|---|---|
| `off` | só no computador | sem controle de acesso; **recusado em produção** (`K_SERVICE` definido → `RuntimeError`) |
| `iap` | Cloud Run atrás do IAP | exige `IAP_AUDIENCE`; toda requisição (inclusive estáticos e `/saude`, A29) precisa do JWT `x-goog-iap-jwt-assertion` válido (ES256, emissor `https://cloud.google.com/iap`, público `IAP_AUDIENCE`); sem ele, **401**; chaves do IAP indisponíveis, **503** (F06; `app/iap.py`, middleware `cabecalhos` em `main.py`, conferência em `run_in_threadpool`). E-mail do usuário em `request.state.usuario` |
| outro (`on`…) | — | o app não sobe ("Controle de acesso ainda não implementado") — fase 2 (link por e-mail, sessão, admin) não existe |

`AUTH=iap` é **exceção temporária à D10**, criada para a reunião do gerente, e **aguarda aprovação do Caio** (seção 6.2).

### 2.6 Deploy no Cloud Run com IAP (roteiro, nada executado)

`docs/deploy_iniciativas.md`, resumo:

- Imagem `python:3.12-slim-bookworm`, usuário sem root, `COPY app/ ./app/` (inclui `app/base_congelada/` e o retrato
  da LIA) e, desde a D65, `COPY ml/saida/previsao.json ./ml/saida/previsao.json` (sem o arquivo o build falha, de
  propósito) e, desde a correção F01 (31/10/2026), `RUN python -m app.conferir_base`: com o corte ligado, o build para
  se a base congelada estiver ausente, incompleta ou incoerente com o manifesto, se a Previsão não for do mês do corte e
  da mesma carga da base, ou se a LIA não for até o corte (sem rede); `ml/` (menos o retrato), `docs/`, `tests/`, `tools/`, `_congelado/`, `_descartados/`, `.playwright-mcp/`,
  `.taste-skill/` e `app/static/roadmap_proto/` ficam fora (`.dockerignore` = `.gcloudignore`, F17/A33, 31/10/2026);
  `uvicorn ... --workers 1 --proxy-headers`. Sonda de partida padrão (TCP); nenhuma sonda HTTP em `/saude` (A29).
- `gcloud run deploy ... --no-allow-unauthenticated --iap --min-instances=0 --max-instances=1` com
  `AUTH=iap, IAP_AUDIENCE=/projects/NUMERO/locations/us-central1/services/relatorios-agenciamento,
  INICIATIVAS_BACKEND=firestore, INICIATIVAS_BUCKET=gglobo-viu-dados-hdg-prd-iniciativas-anexos, INICIATIVAS_EDICAO=on`.
- Conta de serviço: leitura no `gold_monday` + `jobUser`/`readSessionUser`; `roles/datastore.user` no projeto;
  `roles/storage.objectAdmin` só no bucket. Acesso de pessoas: `roles/iap.httpsResourceAccessor` (gerente e Caio).
- Com a base congelada na imagem (D65), o serviço não consulta o BigQuery nesta reunião; o roteiro do corte acrescenta
  `CORTE_DADOS=2026-10-31` ao `--set-env-vars` (`docs/congelar_outubro.md`, passo 6).
- Dependências em aberto: o vídeo da LIA ainda não existe; a cola (8200) não funciona no link publicado.
- Todo comando de GCP é do Caio (regra 1 do `CLAUDE.md`); o Claude só consulta.

### 2.7 Iniciativas: banco próprio

| Camada | Computador (padrão) | Cloud Run (padrão com `K_SERVICE`) |
|---|---|---|
| Backend | `SqliteBackend`: `~/.ppd-agenciamento-v2/iniciativas.db` + `anexos/` (fora do Google Drive) | `FirestoreBackend`: coleções `iniciativas`, `anexos`, `iniciativas_meta` (prefixo `INICIATIVAS_PREFIXO`) + bucket privado `INICIATIVAS_BUCKET` (`anexos/<iniciativa>/<uuid>.<ext>`) |
| Escrita | ligada (`INICIATIVAS_EDICAO=on`) | **desligada por padrão**; `on` só atrás do IAP |
| Variáveis | `INICIATIVAS_DB`, `INICIATIVAS_ANEXOS` | `INICIATIVAS_FIRESTORE_DB`, `INICIATIVAS_BUCKET`, `INICIATIVAS_PREFIXO` |

Regras no `repositorio.Quadro`, iguais para os dois backends; detalhe na seção 3.9.

---

## 3. Páginas

Números da carga vigente: **gold processada em 30/10/2026 09:01 (São Paulo), dados até 29/10/2026**, lidos da página
renderizada por uma instância local só de leitura em 31/10/2026 e, nos principais, reconferidos no BigQuery (só SELECT,
conta `caio.barroso@viu.com.br`, projeto `gglobo-viu-dados-hdg-prd`, 31/10/2026). Fichas com a memória datada de
26/10/2026 continuam valendo como registro; onde o número mudou, vale o daqui.

### 3.1 Capa

**3.1.1 Pergunta / título.** "ViU / *Agenciamento*", sobretítulo "Relatório da área", subtítulo "Tudo o que a área
analisa, constrói e entrega, num só lugar.", data "Outubro de 2026" (`apresentacao.py:372-398`, `capa={...}`).

**3.1.2 O que mostra.** Lado branco com logo e textos; plano marinho em diagonal com a ilustração decorativa "dados →
área" (13 pontos lavanda convergindo num nó amarelo; cartões brancos viram quadradinhos amarelos na linha única) e o
botão amarelo **"Começar"** (link para `proxima.href` = Roadmap).

**3.1.3 Fonte.** Nenhuma (texto fixo). `capa.medida` ainda calcula o típico do SLA (`medida_capa`,
`apresentacao.py:42-48`) e a rota passa `capa_horas` ao template (`main.py:377-380`), herança da capa de 27/10 com o
relógio; a capa atual não o mostra. As `etapas` da jornada também seguem no dicionário sem uso. Rodapé datado pelas
tabelas do Início.

**3.1.4 Regras.** Sem cálculo.

**3.1.5 Números.** Nenhum.

**3.1.6 SQL.** Não se aplica.

**3.1.7 Interações.** "Começar", → / PageDown e `rel="next"` levam ao Roadmap.

**3.1.8 Acessibilidade e movimento.** Ilustração `aria-hidden`; contraste ≥ 4,5:1 no subtítulo e no botão. Entrada
única até 1,2 s. **Loop contínuo autorizado só na capa** (SMIL no SVG; `static/capa_fluxo.js` pausa com aba oculta e com
`prefers-reduced-motion`). Botão de pausa retirado por decisão do Caio (30/10/2026). Cabe sem rolagem em 1280×720,
1440×810 e 1920×1080; abaixo de 860 px o plano marinho vira faixa; 390 px sem rolagem lateral.

**3.1.9 Testes.** `tests/test_portal.py::test_capa_e_encerramento`,
`tests/test_v2_paginas.py::test_capa_sem_menu_com_comecar_para_o_roadmap`, `tests/test_movimento.py`.

**3.1.10 Decisões e pendências.** Capa V2 (Caio, 30/10/2026, 3ª rodada). A confirmar: redação do subtítulo, velocidade
e quantidade do fluxo, posição do botão (ficha `docs/paginas/capa.md`).

### 3.2 Roadmap (hub da reunião)

**3.2.1 Pergunta / título.** "Como chegamos até aqui?" (selo "Gerencial"; `apresentacao.py:411-421`).

**3.2.2 O que mostra.** 5ª versão (31/10/2026), "linha do tempo linear em Y" num painel flutuante:
01 Dados espalhados (7 chips: SharePoint, Excel, Monday, OneNote, Salesforce, API, Req2Pay) → 02 Mapeamos e organizamos →
Y com 04 Pedimos a infraestrutura à TI ┄ "Aguardando" ┄ 05 Infraestrutura liberada (ramo de cima) e 03 Criação de
dashboards (ramo de baixo) → 06 Centralizamos no BigQuery → dois trilhos contínuos até a borda: **07 Análises e estudos**
("Você está aqui", com os botões) e 08 Novos dashboards e melhorias; retroalimentação pontilhada ("retroalimenta a base",
"estudo vira dashboard"); rótulo "Evolução contínua". Miniaturas em 02, 03 (galeria Pagamentos + Contratos) e 06.

Botões por categoria (`CATEGORIAS` em `roadmap/__init__.py`):

| Categoria | Botão | Destino |
|---|---|---|
| Análises | Demanda · Talentos · SLA | `/viu-agenciamento`, `/talentos#1`, `/sla#1` |
| Automação e IA | LIA · Iniciativas ("próximo") | `/lia#1`, `/iniciativas#1` |
| Projeções | Previsão ("próximo") | `/previsao#1` |

**3.2.3 Fonte.** Nenhum dado. `roadmap/__init__.py` (`PASSOS`, `CATEGORIAS`, `RETROS`, `CONTINUO`, `tela()`) calcula a
geometria (posições, larguras dos títulos sem sobreposição, trechos de linha, rotas e quadros-chave do pulso), passada
por `<style nonce>`. Imagens em `app/static/roadmap/*.webp`, geradas por `tools/gerar_imagens_roadmap.py` com
**desfoque** dos dados sensíveis (seção 6.4). `tabelas=("entrada",)` só para o rodapé datado.

**3.2.4 Regras.** Regra do texto: nó do ramo de cima → título acima; de baixo → abaixo; tronco alterna começando por
cima e muda de lado se colidir; largura padrão `TITULO` = 9,8 em, quebra equilibrada em até 2 linhas, folga mínima 0,8 em.
Deslocamentos `dy`: 02 desce 1,2 em; 03 sobe 0,7 em; 06 sobe 0,5 em. `mostrar: False` tira um nó. Cada categoria é uma
coluna de até 4 botões.

**3.2.5 Números.** Nenhum.

**3.2.6 SQL.** Não se aplica.

**3.2.7 Interações.** Botões navegam; miniaturas abrem `<dialog>` (Ver em 100%, Abrir em tamanho real; galeria com ‹ ›
e ← →); camadas decorativas com `pointer-events: none` para os cliques chegarem aos links. **✕ leva à capa** só aqui.

**3.2.8 Acessibilidade e movimento.** Chips `aria-hidden`; botões com nome e linha de apoio para o leitor de tela;
botões ≥ 32 px a 1280×720; abaixo de 900 px a linha fica vertical; 390 px vira lista. Movimento só com
`prefers-reduced-motion: no-preference` e `html.js`; **loop permitido no bloco `.rm-*`** (exceção registrada em
`tests/test_movimento.py`): pulso de 9 s pelos ramos, anel quando o pulso passa num nó, gesto próprio de cada ícone.

**3.2.9 Testes.** `tests/test_v2_paginas.py` (estrutura, posições, regra do texto, pulso, cliques, categorias, 10
destinos fictícios, miniaturas, `mostrar`, escala), `tests/test_movimento.py`.

**3.2.10 Decisões e pendências.** `nota_estado="ordem e textos a confirmar com o Caio"`. Propostas abertas na ficha
`docs/paginas/roadmap.md` ("Proposta a confirmar com o Caio"). Versões anteriores em `_descartados/2026-10-31/` e
`_descartados/2026-10-30/`.

### 3.3 Demanda (página inicial da área)

**3.3.1 Pergunta / título.** "Quantos pedidos de orçamento chegaram ao longo de 2026 até o momento?" (ano fechado:
"…em AAAA?"); pergunta da seção em `pergunta_inicio`.

**3.3.2 O que mostra.** Frase-resposta "Chegaram **N** pedidos de orçamento em 2026, até D de mês"; selo da variação
contra o mesmo período de 2025 e duas barras finas proporcionais; tabela "Tipo de input" (2026 × 2025 no mesmo período,
pedidos, %, Var.); gráfico mensal empilhado por tipo (Mercado, Inbound, Proativo, Internos, Sem tipo) com a dica do mês
(4 situações e o mesmo mês de 2025); clique num dos 6 meses mais recentes com pedidos abre o **extrato do mês** (fila).

**3.3.3 Fonte.** `app/apresentacoes/gestao_orcamentos/entrada/calculos.py` (`entrada()`, `extrato()`),
montagem em `apresentacao.py::montar_inicio` e `_inicio_base` (138-185), template `gestao_orcamentos/inicio.html`.

| Tabela | Colunas usadas |
|---|---|
| `gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_entrada_diaria` | `data, grupo_input, tipo_de_input, familia, quantidade, quantidade_estimada, quantidade_saida, entregue_no_mes, entregue_depois, nao_seguiu, em_andamento, _processado_em` |
| `...gld_agenciamento_fila_mensal` (view) | `mes, mes_entrada, do_ano, novos, represados, entregues, nao_seguiram, seguem, _processado_em` |
| `...gld_agenciamento_fluxo_mensal` | só para conferir que entrada e fluxo são da mesma fotografia (`_mesma_fotografia`) |

**3.3.4 Regras e memória de cálculo** (docstring de `entrada/calculos.py`, linhas 1-47):

1. **E1** pedidos do dia = `quantidade + quantidade_estimada` (cards com data estimada contam no dia estimado); todas
   as famílias entram.
2. **E2** grupo = `grupo_input` se estiver em `GRUPOS` = (Mercado, Inbound, Proativo, Internos, Sem tipo); senão
   "Sem tipo". A ordem é fixa (cor segue o grupo).
3. **E3** último dia coberto = véspera (São Paulo) de `MAX(_processado_em)` (`ultimo_dia`); sem o metadado, `MAX(data)`.
4. **E0** ano mostrado = ano do último dia coberto; sem seletor.
5. **E4** período: "até D de mês" no ano em andamento; "de janeiro a dezembro" no ano fechado.
6. **E8** comparação com o ano anterior só se a base do ano anterior começa até 07/01 (`regua_anterior`); mesmo
   período = 1º/jan até o mesmo dia do ano anterior (`min(ultimo, 31/12) − 1 ano`); por mês, o mesmo mês (no parcial,
   até o mesmo dia). **Variação = atual ÷ anterior − 1**, só com anterior ≥ `BASE_MINIMA_VARIACAO` = 30
   (`variar`); abaixo disso, "base pequena no ano anterior".
7. **E8c** parcelas de um mesmo todo fecham em 100 pelo maior resto (`_pcts`, empate decidido pela ordem de `GRUPOS`);
   percentuais que não são parcelas arredondam meio para cima (`_pct`). Sinal e frase da variação saem do percentual já
   arredondado (`formato.variacao`).
8. **E6** situação da safra (dica): `entregue_no_mes`, `entregue_depois`, `nao_seguiu`, `em_andamento`, em 100 pelo
   maior resto.
9. **E9** tabela por tipo no mesmo período; teste de duas proporções calculado em `contra_anterior` mas não exibido.
10. **E5** composição do grupo (dica) só em `GRUPOS_COM_DICA` = ("Internos",).
11. **E7** extrato só nos 6 meses mais recentes com pedidos (`meses_extrato`), na tela só os do ano mostrado. Fila do
    mês (view `fila_mensal`, só pedidos do próprio ano, `do_ano`): represados no início + novos = demanda = entregues
    (dos novos + dos represados) + não seguiram + seguem represados. Entregues dos novos ÷ novos; dos represados ÷
    represados (meio para cima). Extrato escondido com aviso se entrada e fluxo/fila forem de dias de carga
    diferentes ou se os novos do extrato ≠ total da coluna (`montar_inicio`).

**3.3.5 Números (carga de 30/10/2026, dados até 29/10).**

| Elemento | Valor |
|---|---|
| Pedidos de 2026 até 29/10 | **5.759** (BigQuery: 5.759) |
| Mesmo período de 2025 | **3.018** (BigQuery: 3.018) → **+91%** (5.759 ÷ 3.018 − 1 = 90,8%) |
| Por tipo, 2026 (pedidos · %) | Mercado 3.129 · 54% · Inbound 1.355 · 24% · Internos 776 · 13% · Proativo 414 · 7% · Sem tipo 85 · 2% |
| Por tipo, 2025 mesmo período | Mercado 1.209 · 40% · Inbound 975 · 32% · Proativo 483 · 16% · Internos 348 · 12% · Sem tipo 3 · <1% |
| Var. por tipo | Mercado +159% · Internos +123% · Inbound +39% · Proativo −14% · Sem tipo "–" (base pequena) |
| Internos (dica) | ViU 275 · Interna 267 · Globo 144 · ViU First 83 · OTR 7 |
| Mês a mês 2026 | jan 374 · fev 341 · mar 485 · abr 472 · mai 629 · jun 569 · jul 765 · ago 644 · set 733 · out (parcial, até 29/10) 747 |
| Mesmo mês de 2025 | jan 177 · fev 197 · mar 166 · abr 329 · mai 312 · jun 268 · jul 275 · ago 474 · set 395 · out (até 29/10) 425 |
| Outubro, situação | entregues no mês 454 (61%) · saíram sem entrega 94 (12%) · em andamento 199 (27%) |
| Meses com extrato | mai a out/2026 |

**3.3.6 SQL para reproduzir (BigQuery, só SELECT).**

```sql
-- Número do ano e mesmo período do ano anterior (E1, E3, E8). Fim = véspera do _processado_em.
SELECT EXTRACT(YEAR FROM data) AS ano, SUM(quantidade + quantidade_estimada) AS pedidos,
       FORMAT_TIMESTAMP('%F %T', MAX(_processado_em), 'America/Sao_Paulo') AS processado_sp
FROM `gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_entrada_diaria`
WHERE data BETWEEN '2026-01-01' AND '2026-10-29' OR data BETWEEN '2025-01-01' AND '2025-10-29'
GROUP BY ano ORDER BY ano;
-- 31/10/2026: 2025 = 3018, 2026 = 5759, processado 2026-10-30 09:01:59

-- Tabela por tipo (E2, E9)
SELECT IF(grupo_input IN ('Mercado','Inbound','Proativo','Internos'), grupo_input, 'Sem tipo') AS grupo,
       EXTRACT(YEAR FROM data) AS ano, SUM(quantidade + quantidade_estimada) AS pedidos
FROM `gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_entrada_diaria`
WHERE data BETWEEN '2026-01-01' AND '2026-10-29' OR data BETWEEN '2025-01-01' AND '2025-10-29'
GROUP BY 1, 2 ORDER BY 1, 2;

-- Extrato de um mês (E7)
SELECT * FROM `gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_fila_mensal`
WHERE mes = DATE '2026-10-01' AND do_ano ORDER BY mes_entrada;
```

Reprodução independente pela silver e checagem diária Q1/Q2: ficha `docs/paginas/inicio.md`, seções 6.3 e 6.4.

**3.3.7 Interações.** Dica por mês (foco ou mouse); clique nos meses com extrato troca a caixa por `fetch` sem recarregar
(`apresentacao.js:560-632`; se a "fotografia" mudou, recarrega a página inteira); "Voltar" fecha; Voltar/Avançar do
navegador funcionam (`popstate`). Sem JS, o link `?mes=AAAA-MM` abre a página com o extrato.

**3.3.8 Acessibilidade e movimento.** Cada mês e barra com texto para leitor de tela; selo com seta + texto (nunca só
cor); números prontos desde o 1º quadro (D46/D49); entrada até 1,2 s, sem loop.

**3.3.9 Testes.** `test_inicio_d52.py`, `test_inicio_revisao.py`, `test_revisao_20261024.py`,
`test_revisao_20261025.py`, `test_formato_variacao.py`, `test_qualidade_previsao.py` (entrada mensal), `test_rotas.py`.

**3.3.10 Decisões e pendências.** D23, D25, D26, D28 (entregue em 23/10), D52 (disposição em dois quadrantes). Abertas:
Q7 (data de entrada = criação do card × `data_de_entrada`), Q11 (2025 com ~15% de datas estimadas), DC14 ("represados" →
"veio do mês anterior"), extrato em janeiro com meses do ano anterior (B6). Achados F7–F11 (PRD, seção 10).

### 3.4 Talentos

**3.4.1 Pergunta / título.** "Como a demanda se divide entre talentos exclusivos e não exclusivos?"

**3.4.2 O que mostra.** Seletor Todos / Exclusivos / Não exclusivos (filtra a página inteira); frase-resposta (herói);
barra 100% do ano com os três grupos (o filtrado em destaque); mapa de calor "Os 10 talentos com mais pedidos, mês a mês"
(jan–dez, mês parcial "até DD", meses futuros "sem dado"); linha "Juntos, N pedidos: X% …"; botão ▶ "corrida do ano".

**3.4.3 Fonte.** `talentos/calculos.py` (`divisao`, `top_por_grupo`, `seletor`, `heroi`, `barra`, `mapa`,
`largura_nomes`), montagem em `apresentacao.py::montar_talentos` e `_talentos` (239-282).

| Tabela | Colunas usadas |
|---|---|
| `...gold_monday.gld_agenciamento_2026_talentos_ano` | `ano, categoria, n, total, pct, dos_quais_squad, _processado_em` |
| `...gold_monday.gld_agenciamento_2026_talentos_ranking` | `grupo, talento, n, ultimo_pedido, empate_fora, talentos_grupo, mes, n_mes, pos, _processado_em` |
| `...gold_monday.gld_agenciamento_entrada_diaria` | total do Início (conciliação T5) e fim do período |

**3.4.4 Regras e memória de cálculo** (docstring de `talentos/calculos.py`):

1. **T1** base = os mesmos pedidos do Início, divididos na gold `talentos_ano` (regras de data da gold de entradas).
2. **T2** exclusividade na data do pedido; sem talento = grupo "Talento não informado".
3. **T3** "Squad de Talentos" é grupo, conta nos não exclusivos e fica fora do ranking.
4. **T4** parcelas da barra pelo maior resto (`_pcts` importado de `entrada/calculos.py`).
5. **T5** conciliação: total da divisão = total do Início e mesmo dia de carga; divergência mostra os números com aviso
   (`em_atualizacao`), sem bloquear; o top 10 só aparece se o ranking for da mesma carga.
6. **T6** top 10 por recorte: `drop_duplicates("talento")`, ordena por `n` desc e nome; corta em 10; empate no corte vira
   nota "empate com mais N" (`empate_fora`); recorte cuja soma passe do total do grupo é descartado (nunca > 100%).
7. **T7/T8** herói: Todos = % do maior grupo ("Da demanda do ano, X% vai para os talentos exclusivos."); Exclusivos /
   Não exclusivos = % dos pedidos do grupo que vão para os 10 mais pedidos. Esse % é `round(100 * soma / total)`
   (ver ponto A16 da seção 10).
8. **T9** barra com o grupo filtrado destacado e os outros esmaecidos.
9. **T10** mapa: 6 tons por `ceil(6 × v ÷ maior)`; se a soma dos meses de um talento ≠ total, o mapa não aparece.
10. **T11** largura da coluna de nomes = maior nome entre 10 e 30 caracteres.
11. **T12/D51** corrida do ano só no botão ▶ (`apresentacao.js`), terminando no estado final da tabela.

**3.4.5 Números (carga de 30/10/2026, dados até 29/10).**

| Elemento | Valor |
|---|---|
| Divisão do ano | Exclusivos **3.533** (61%) · Não exclusivos **2.076** (36%; 129 do Squad) · Talento não informado **150** (3%) = 5.759 = Demanda |
| Herói (Todos) | "Da demanda do ano, 61% vai para os talentos exclusivos." · "3.533 de 5.759 pedidos do ano" |
| Top 10 (Todos), ano | Tatiana Machado 282 · Beatriz Reis 246 · Juliette Freire 208 · Ticiane Pinheiro 195 · Gilberto Nogueira 190 · Eliana Michaelichen 173 · Tadeu Schmidt 158 · Renata Saldanha 134 · Chaiany Pinto Andrade 128 · Maxiane Rodrigues 128 |
| Juntos | 1.842 pedidos: 32% da demanda do ano |

**3.4.6 SQL para reproduzir.**

```sql
SELECT categoria, n, pct, dos_quais_squad
FROM `gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_2026_talentos_ano`
WHERE ano = 2026 ORDER BY n DESC;
-- 31/10/2026: Exclusivos 3533 (61,3) · Não exclusivos 2076 (36,1; squad 129) · Sem talento 150 (2,6)

SELECT grupo, talento, n, pos, empate_fora, talentos_grupo, mes, n_mes
FROM `gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_2026_talentos_ranking`
WHERE grupo = 'todos' AND pos <= 10 ORDER BY n DESC, talento, mes;
```

Conferência independente pela silver: ficha `docs/paginas/talentos.md`, seção 0.5 (ponto A20: a ficha ainda cita
`app/sql/talentos_*.sql`, que saiu do site).

**3.4.7 Interações.** Seletor (link `?talentos=`, nada aplica sozinho), dicas por célula, ▶ corrida (opcional; a tabela já
mostra o resultado).

**3.4.8 Acessibilidade e movimento.** Mapa como tabela com cabeçalhos; cada célula com texto; "sem dado" nos meses
futuros. **Exceção D51 só aqui:** ao abrir e ao trocar o filtro, a barra cresce e os números contam até o valor (sem
mudar o valor final); corrida só no ▶.

**3.4.9 Testes.** `test_talentos_d50.py`, `test_talentos_d51.py`, `test_revisao_20261025.py`, `test_portal.py`.

**3.4.10 Decisões e pendências.** D30, D31, D50, D51, D57 (fim da exceção D30-b da silver). Nomes de talentos na tela
por decisão do Caio (24/10/2026). Pendências PD01, PD02a, PD02b, PD03, PD20 (`pendencias.py`; várias já resolvidas pela
D57, ver ponto A21).

### 3.5 SLA de entrega

**3.5.1 Pergunta / título.** "Quanto tempo levamos para entregar um orçamento?" (aba "SLA"; `nota_estado="meta a
oficializar"`).

**3.5.2 O que mostra.** Seletor de talentos (Todos 14 h / Exclusivos 12 h / Não exclusivos 20 h, com o n); frase
"Levamos **X h** de trabalho da equipe em [grupo] para entregar um orçamento ao cliente." (típico); apoio "**X,Y dia(s)
útil(eis)** no calendário para o cliente receber" com exemplo ("pedido na segunda às 10h, resposta na terça à tarde") e
dias corridos entre parênteses; cartão "Orçamentos prontos em até 2 dias de trabalho, por mês" com trilhos (até 1 dia,
1 a 2 dias; vazio = acima de 2), legenda do ano, "N% passam de 2 dias de trabalho", linha tracejada "meta sugerida: 2 dias
de trabalho", típico de cada mês sob a coluna, mês vigente vazado; lupa para o estudo.

**3.5.3 Fonte.** `sla/calculos.py::entrega()` (208-276) sobre `entregas()` (98-130); montagem
`apresentacao.py::montar_sla` (27-39); `app/sla.py` (`mes_parcial`, `data_corte`).

| Tabela | Colunas usadas |
|---|---|
| `...gold_monday.gld_agenciamento_2026_sla_movimentos` | contrato `COLUNAS_SLA` (`dados.py:289-292`); na página: `_processado_em` (mês parcial, corte) |
| `...gold_monday.gld_agenciamento_2026_sla_entregas` (view) | `projeto_id, mes, mes_entrada, inicio, entregue_em, exclusivo, tipo_de_input, pacote, h_trabalho, h_fila, h_elaboracao, h_revisao, h_calendario, dias_uteis, dias_uteis_fr, _processado_em` |

A view tem de ser da mesma carga dos movimentos; senão relê uma vez e, persistindo, `DadosIndisponiveis`
(`_da_gold`, 84-95).

**3.5.4 Regras e memória de cálculo** (docstring de `sla/calculos.py`, 1-55; constantes 63-71):

1. **C1** pronto = 1ª chegada em Aguardando Feedback (1º passo `fase='cliente'`) — calculado na gold.
2. **C2 + D-SLA-2** horas da equipe = horas úteis sem almoço (seg–sex 10h–13h e 14h–19h, sem feriados) de todos os passos
   `equipe` antes de C1, **com a Entrada** e **sem "Em elaboração - Retorno Marca/Executivo"** → `h_trabalho` (R24 da gold).
3. **C4 / D-SLA-1** mês de referência = **mês da 1ª entrega** (`mes`).
4. **C7** só meses completos de entrega do ano da carga: `mes >= AAAA-01` e `mes < mes_parcial` (`_completos`);
   `mes_parcial` = mês de `MAX(_processado_em)` em São Paulo (`app/sla.py:17-25`).
5. **C10** grupos: Todos; Exclusivos = `exclusivo == True`; Não exclusivos = `False`; sem talento só em Todos.
6. **Típico** = mediana exata de `h_trabalho` (`_mediana`); escrita por `_h_meta`: inteiro meio para cima, mas entre
   15,5 e 16,5 h com 1 casa (acima de 16 arredonda para cima, abaixo para baixo) para nunca cair do lado errado da meta.
7. **C5/C8 faixas** (`_faixas`): até 1 dia = `h ≤ 8`; até 2 dias = `h ≤ 16`; escritos: até 1 dia e até 2 dias meio para
   cima; "1 a 2 dias" = até 2 − até 1; "acima de 2 dias" = 100 − até 2.
8. **C6 / D-SLA-7 meta sugerida** = metade (`META = 0.50`) em até 2 dias de trabalho (`META_H = 16`); `meta_tipico`
   compara a mediana exata com 16 h ("O típico já sai em até 2 dias" / "ainda passa de 2 dias (X h)").
9. **C3c (D54) prazo do cliente** = mediana de `dias_uteis_fr` (dias úteis com fração), 1 casa meio para cima
   (`dias_uteis_cliente`); exemplo da semana a partir de segunda 10h; acima de 4,9 dias, sem exemplo; "dia útil" no
   singular abaixo de 2. Dias corridos = mediana de `h_calendario` ÷ 24.
10. **A2/A3 mês vigente**: barra vazada "parcial"; com menos de `MIN_PARCIAL` = 30 entregas, sem % nem típico.
11. **C11** leitura por regra (melhor e pior mês, último contra o ano) — calculada; **C12** acima de 5 dias (> 40 h)
    calculado (`acima5`), fora da tela desde a D38.

**3.5.5 Números (carga de 30/10/2026, dados até 29/10; jan–set).**

| Elemento | Todos | Exclusivos | Não exclusivos |
|---|---|---|---|
| Orçamentos medidos | **2.346** | 1.610 | 723 |
| Típico (h de trabalho) | **14 h** (14,195) | 12 h (11,818) | 20 h (19,642) |
| Dias úteis para o cliente receber | **1,8** (1,8482) | 1,6 (1,5602) | 2,5 (2,4999) |
| Dias corridos | 2,8 | — | — |
| Até 1 dia · 1 a 2 dias · acima de 2 | **31 · 25 · 44** | 37 · 25 · 38 | 18 · 23 · 59 |
| Mensagem do típico | já sai em até 2 dias | já sai | ainda passa de 2 dias |

Meses (Todos): % em até 2 dias jan 60 · fev 55 · mar 58 · abr 50 · mai 49 · jun 49 · jul 57 · ago 59 · set 59; orçamentos
111 · 108 · 159 · 215 · 201 · 288 · 548 · 379 · 337; típico 13 · 15,7 · 15 · 16,4 · 16,4 · 16,5 · 13 · 13 · 14 h. Outubro
(em andamento, até 29/10): 53% de 353 entregas, típico 15,5 h. BigQuery (31/10): n e mediana dos três grupos, dias úteis
e % até 1 / até 2 dias iguais aos da tela.

Ponte das bases (ficha `sla.md`, carga de 26/10): 5.556 recebidos → 3.969 entregues jan–set → 2.347 com tempo medido
(59%); os não medidos são sobretudo de jan–mai, antes de o board registrar todos os status.

**3.5.6 SQL para reproduzir.**

```sql
WITH e AS (
  SELECT * FROM `gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_2026_sla_entregas`
  WHERE mes >= DATE '2026-01-01' AND mes < DATE '2026-10-01'),          -- C7: meses completos
v AS (
  SELECT 'Todos' AS g, h_trabalho, dias_uteis_fr FROM e
  UNION ALL
  SELECT IF(exclusivo, 'Exclusivos', 'Nao exclusivos'), h_trabalho, dias_uteis_fr FROM e WHERE exclusivo IS NOT NULL)
SELECT g, COUNT(*) AS n, ROUND(ANY_VALUE(med), 3) AS tipico_h, ROUND(ANY_VALUE(med_d), 4) AS dias_uteis_cliente,
       ROUND(100 * COUNTIF(h_trabalho <= 8) / COUNT(*), 2) AS ate_1_dia,
       ROUND(100 * COUNTIF(h_trabalho <= 16) / COUNT(*), 2) AS ate_2_dias
FROM (SELECT *, PERCENTILE_CONT(h_trabalho, 0.5) OVER (PARTITION BY g) AS med,
             PERCENTILE_CONT(dias_uteis_fr, 0.5) OVER (PARTITION BY g) AS med_d FROM v)
GROUP BY g ORDER BY g;
-- 31/10/2026: Todos 2346 · 14,195 · 1,8482 · 31,12 · 55,54 | Exclusivos 1610 · 11,818 · 1,5602 · 37,14 · 62,30
--             Nao exclusivos 723 · 19,642 · 2,4999 · 18,12 · 41,08
```

Para o mês a mês, agrupar também por `FORMAT_DATE('%Y-%m', mes)`. Reprodução independente das horas a partir dos
movimentos (expediente e feriados em SQL): ficha `sla.md`, seções 0.6 e 000000000000.2.

**3.5.7 Interações.** Seletor de talentos (links); dica e leitor de tela em cada coluna; lupa "Como medimos".

**3.5.8 Acessibilidade e movimento.** Cada mês com frase completa para o leitor de tela; meta descrita em texto ("metade
dos orçamentos (50%) prontos em até 2 dias de trabalho (16 horas)"); status com ícone + texto; números prontos desde o 1º
quadro.

**3.5.9 Testes.** `test_calculos.py`, `test_sla_20261025.py`, `test_sla_d38.py`, `test_sla_d54.py`, `test_sla_batalha.py`,
`test_batalha2_textos.py`, `test_rotas.py`.

**3.5.10 Decisões e pendências.** D34–D38, D49, D54, D-SLA-1 a D-SLA-7. **Meta a oficializar** (pedido nº 1 do "O que
falta"). Abertas: DC6 (veredito da meta), DC7 (teto acima de 5 dias), DC8 (ponte das bases), DC12 (limiar único),
DC15. Pendências PD15 (SLA de 2025 não existe), PD21 (texto desatualizado, ver A21).

### 3.6 Estudo "Como medimos" (5 slides)

**3.6.1 Pergunta / título.** Rota `/sla/como-medimos#n` (`main.py:392-411`); `montar_estudo_sla`
(`apresentacao.py:118-135`); template `templates/como_medimos.html`. Só existe no SLA. `?talentos=` em todos os slides;
`?exemplo=<projeto_id>` só em DEV ou modo apresentação, nunca em produção.

| # | Título | Regras |
|---|---|---|
| 1 | Como chegamos ao tempo da equipe | E1–E3 (exemplo real sorteado no dia), C3c |
| 2 | A maioria é rápida. Poucos demoram muito. | X1–X6, **X10** (um passo só), **X11** (puxão) |
| 3 | Quantos saem em até 2 dias, e quanto do tempo levam? | W2–W3, V1–V3, **V9**, **V10** |
| 4 | Título por regra U8 (na carga vigente: "A demora não é de um mês. Acontece o ano todo.") | U1–U9 |
| 5 | Onde o tempo trava? (último; sai para o SLA pelo ✕ ou para a LIA pela →) | K1–K8 |

Fora da tela: o slide de tipo de pedido (`ESTUDO_TIPO = False`, D64, `apresentacao.py:115`) e a conclusão (Z1–Z8,
ainda calculada para a cola e a conferência). O selo de recorte do canto e as faixas de conclusão do pé saíram da tela
(30/10/2026); o texto do recorte fica só para o leitor de tela.

**3.6.2 O que mostra.**

- **Slide 1:** um orçamento real do dia (passos Entrada, Elaboração, Revisão com horas da equipe; "Aguardando Feedback"
  fora do cálculo), o que entra e o que fica fora da conta, expediente, total de trabalho em horas e dias de trabalho,
  dias úteis para o cliente receber e a frase "No ano, o orçamento típico leva 14 h: dentro da meta de 2 dias."
- **Slide 2:** histograma de 4 em 4 h (até "mais de 60 h") com as faixas do boxplot (rápidos, comuns, demorados, fora
  da curva); painel "Como ler" com típico × média, régua das horas com a seta do puxão e 100 quadrados do "fora da curva".
- **Slide 3:** layout em "T": Quantidade (waffle de 100 pedidos, A em até 2 dias × B acima, com as 5 faixas) e Tempo
  (parte das horas da equipe de cada lado, com o típico de cada lado).
- **Slide 4:** dispersão por mês da entrega (um ponto por pedido), típico e faixa da maioria; % que passa de 2 dias e
  pedidos por mês.
- **Slide 5:** etapas Entrada → Elaboração → Revisão com os status em que o tempo trava (% do tempo travado, quantos
  travaram, limite de Tukey por status).

**3.6.3 Fonte.** Slides 1–4: view `gld_agenciamento_2026_sla_entregas` (slide 1 também `sla_movimentos` para os passos
e `fluxo_mensal` para a cobertura). Slide 5: view `gld_agenciamento_2026_sla_entregas_status` (`projeto_id, status, h,
_processado_em`). Funções em `sla/calculos.py`: `exemplo` (487), `exploracao` (982), `tempo_cem` (1485),
`cem_pedidos` (1316), `meses_estudo` (1667), `travas` (1818), `recorte` (1238), `cobertura` (345).

**3.6.4 Regras principais e memória.**

1. **E1** exemplo: orçamento do grupo com tempo entre `EXEMPLO_H` = (2, 16) h, sorteado de forma estável no dia.
2. **X6** faixas do slide 2: rápidos ≤ Q1, comuns Q1–Q3, demorados Q3–limite, **fora da curva > limite**, com limite =
   `exp(Q3_log + 1,5 × IQR_log) − 1` sobre `ln(h + 1)` (Tukey na escala log; SQL 0.6.1 da ficha). Na carga vigente:
   7 h · 28 h · 59 h.
3. **X10** frase do pé (fora da tela, calculada): "Poucos pedidos demoram muito: os F% fora da curva, acima de L, puxam
   a média para M. O pedido típico leva T. Por isso medimos pelo típico (a mediana)."
4. **X11** puxão = média escrita − típico escrito, nunca negativo; seta só quando a média destoa (X4/D12).
5. **V3** parte das horas = soma das horas da faixa ÷ soma de todas, inteiros pelo maior resto (`_pcts`); **V9** típico
   de cada lado = mediana de `h ≤ 16` e de `h > 16`; **V10** frase-resposta.
6. **U** meses: `DESTOA_PP` = 10 pontos, `DESTOA_H` = 4 h, `RARO_PCT` = 10; teto do gráfico 80 h; título por U8.
7. **K** travas: limite de Tukey por status; `TRAVA_UM` = 50%, `TRAVA_ESPALHADO` = 40%; "Em elaboração" marcado "só até
   jul" (status extinto em maio).

**3.6.5 Números (carga de 30/10/2026, jan–set, Todos).**

| Slide | Valor |
|---|---|
| 1 | exemplo do dia 31/10: "[Bayer] Renata Saldanha \| Redoxon": Entrada 4h22 + Elaboração 4h04 + Revisão 1h13 = 9h39 (1,2 dia de trabalho); 1,2 dia útil; 7 dias aguardando o cliente. O exemplo muda por dia (E1) |
| 2 | 2.346 orçamentos; 25% rápidos (até 7 h) · 50% comuns (7–28 h) · 18% demorados (até 59 h) · 7% fora da curva (171 acima de 59 h, máx. 515 h); típico 14 h, média 25 h, puxão +11 h |
| 3 | 56 em até 2 dias (31 até 1 dia + 25 de 1 a 2; 1.303 pedidos) levam 16% das horas (típico 7 h); 44 acima (15 · 17 · 12; 1.043 pedidos) levam 84% (12 · 20 · 52; típico 29 h) |
| 4 | passam de 2 dias: 40 · 45 · 42 · 50 · 51 · 51 · 43 · 41 · 41% (jan–set); 83 pedidos acima de 10 dias |
| 5 | Fila de entrada 19% (174 travaram, acima de 19,7 h) · Em elaboração 41% (só até jul; 46 de 376, acima de 39,0 h) · Produção 9% · Orçamentos 9% · outros 7 status 3% |

Exclusivos e não exclusivos: tabelas no topo de `docs/paginas/sla.md` (bloco V2). `tools/conferir_estudo.py` (30/10,
carga 12:01:46 UTC): tudo bate nos 3 grupos.

**3.6.6 SQL.** Ficha `sla.md`: 0.6.1 (todos os números do slide 2 por grupo e mês), 000 (slide 3), 0000 (horas por
faixa), 00000 (meses), 000000.5 (travas). Conferência automática: `python tools/conferir_estudo.py` (só leitura).

**3.6.7 Interações.** Slides com ← →; seletor de talentos em cada slide; ✕ do topo volta ao SLA (último slide: anel
azul uma vez e nome "Fim do estudo: voltar ao SLA"); o "Próximo" do pé do último slide segue para a LIA.

**3.6.8 Acessibilidade e movimento.** Gráficos com texto por barra/ponto; cabe em 1440×900, sem rolagem lateral em
390 px; movimento D46 (barras sobem, waffle enche linha a linha) só na 1ª visita, até ~1,1 s, sem loop.

**3.6.9 Testes.** `test_exploracao.py`, `test_sla_cem.py`, `test_sla_tempo.py`, `test_sla_mes.py`, `test_sla_trava.py`,
`test_sla_tipo.py`, `test_sla_conclusao.py`, `test_sla_movimento.py`, `test_sla_batalha.py`; layout por
`node tools/conferir_layout.mjs`.

**3.6.10 Decisões e pendências.** D34–D46, D64 (tipo de pedido fora), V2 de 30/10 (5 slides). Abertas: DC9 (recorte do
slide de travas), DC10, DC11, DC12. A cola (`cola.py`) ainda tem as falas dos ids do estudo antigo (ponto A23).

### 3.7 LIA (e-mails lidos e filtrados)

**3.7.1 Pergunta / título.** "Quanto a LIA já leu e quanto deixou de chegar à equipe?" (seção "LIA: e-mails lidos e
filtrados"; `nota_estado="retrato do Cloud Storage da LIA, a conferir com a equipe"`).

**3.7.2 O que mostra.** "**2.047** e-mails." e "**87%** a LIA resolveu sozinha." com a barra de fração (não lead, lead,
validação hachurada); painel "O ganho para a equipe" (≈ horas de triagem, ≈ horas por semana, e-mails descartados sem a
equipe abrir, % lidos fora do expediente); cartão "Quando o inbound chega" (leads, não leads e validação em dois
quadrantes, dentro × fora do expediente); gráfico "E-mails por semana" (pilha por categoria, semana parcial marcada);
botão "Ver a LIA na prática" (pop-up do vídeo).

**3.7.3 Fonte.** `lia/__init__.py::tela()` sobre `lia/retrato.json` (exceção à D57). Retrato extraído em
**30/10/2026 20:49** por `tools/extrair_lia.py` de `gs://gglobo-viu-lia-dados-prd/data/`; janela **21/09 a 29/10/2026**;
revisão manual até 12/10 (`corte_revisao`; 459 itens revisados). Campos: `periodos, dias, semanas, faixas, turnos, horas,
horas_lead, horas_nao_lead`. Regras do extrator (ficha `lia.md`, "Fonte e regras"): e-mail = `internet_message_id`
único, vale o último processamento; dia = `data_processamento` em São Paulo; categoria = `classificacao`
(`duvida` = validação), trocada por `classificacao_correta` de `revisao_manual.json` quando revisado.

**3.7.4 Regras e memória de cálculo** (`lia/__init__.py`):

1. Totais por categoria = soma de `periodos`; total = 2.047.
2. % resolvidos sozinha = não lead ÷ total (`pct`, sem casa).
3. **Estimativa de tempo devolvido:** horas = não leads × `MINUTOS_TRIAGEM` ÷ 60, com **`MINUTOS_TRIAGEM = 2`**
   (minutos para abrir, ler e descartar um e-mail; **premissa a confirmar com a equipe**, linha 24); dias = horas ÷ 8;
   horas por semana = horas ÷ (dias da janela ÷ 7).
4. "1 em cada N" chega à equipe = total ÷ (leads + validações).
5. **Expediente da LIA (definição do Caio, 30/10/2026): dias úteis 10h–19h com o almoço (12h–13h) DENTRO**; fora = antes
   das 10h, depois das 19h, fim de semana e feriado (`FAIXAS_DIA`, 178-183; `faixas_do_dia`, 226-288). **Difere do SLA**
   (10h–13h e 14h–19h, almoço 13h–14h fora), que não muda. Sem `horas` no retrato, cai na regra antiga (`FORA`, almoço
   fora; linha 351).
6. Quadrantes (`_quadrantes`): cada barra em % da própria categoria; escala comum = maior fatia "dentro" e maior fatia
   "fora" entre as três categorias; validação da faixa = e-mails − leads − não leads.
7. Padrões por dia da semana (teste de permutação, 3.000 permutações, semente 2026) e por período do dia (qui-quadrado)
   são calculados (`padroes`) mas **não vão à tela** (leituras só na ficha).
8. Semanas ISO segunda–domingo; parcial se tiver menos de 7 dias. **O extrato da semana foi retirado (D-LIA-4,
   30/10/2026); `?semana=` é aceito e ignorado** (linha 369).

**3.7.5 Números (retrato de 30/10/2026 20:49, janela 21/09–29/10).**

| Elemento | Valor |
|---|---|
| E-mails lidos | **2.047** (1.101 no período revisado + 946 sem revisão) |
| Não lead · lead · validação | 1.777 (86,8%) · 193 (9,4%) · 77 (3,8%) |
| Triagem poupada (estimativa) | ≈ 59 h (1.777 × 2 min) · ≈ 11 h por semana |
| Lidos fora do expediente | **1.020 (50%)** na definição da LIA (na regra do SLA seriam 1.112, 54%) |
| Dentro × fora | Leads 73% / 27% · Não leads 47% / 53% · Validação 57% / 43% |
| Semanas | 39: 377 · 40: 339 · 41: 340 · 42: 348 · 43: 353 · 44 (26–29/10, parcial): 290 |

**3.7.6 SQL.** Não se aplica (Cloud Storage). Para refazer: `python tools/extrair_lia.py [--inicio] [--fim] [--corte]`
com `CLOUDSDK_CONFIG` do gcloud-viu, depois os testes. Divergência com o PRD de @cris no 1º período (75 × 112 leads) em
aberto (ficha `lia.md`, "Conferência").

**3.7.7 Interações.** Dica por semana (mouse ou foco, só CSS); ← → e Home/End dentro do gráfico andam entre semanas sem
trocar de página; pop-up do vídeo (3.8).

**3.7.8 Acessibilidade e movimento.** Gráfico com `role="region"` e texto completo por semana; frase do período só para o
leitor de tela; rampa de azuis validada (ordinal, um matiz); números sempre escritos ao lado das cores de baixo
contraste; movimento só com `prefers-reduced-motion: no-preference`.

**3.7.9 Testes.** `tests/test_v2_paginas.py` (LIA e vídeo).

**3.7.10 Decisões e pendências.** D-LIA-1 (análise de tempo na régua do SLA: sem ganho robusto; só na ficha), D-LIA-2 a
D-LIA-5. Pendentes: confirmar `MINUTOS_TRIAGEM`; regra oficial do relatório da equipe para o 1º período; a análise
de tempo fica fora da tela.

**Ressalvas da LIA (para a fala):** (1) o tempo devolvido é **estimativa** com premissa de 2 min por e-mail; (2) "fora do
expediente" usa a definição da LIA (almoço dentro), diferente da do SLA; (3) o retrato é de uma janela de 39 dias e não
se atualiza sozinho; (4) no 1º período a categoria vem da revisão manual, no 2º da classificação da LIA; (5) desde a
F10 (31/10/2026) o rodapé é o do retrato ("Dados da LIA até …", ponto A11 resolvido). Retrato ausente ou fora do contrato
(sem semanas, sem dias, total zero): a página vira "Os números da LIA estão indisponíveis agora", sem erro (F05).

### 3.8 Vídeo "A LIA na prática" (pop-up)

**3.8.1 Pergunta / título.** "A LIA na prática: do e-mail à carta orçamento".

**3.8.2 O que mostra.** `<dialog>` aberto pelo botão "Ver a LIA na prática" da página LIA: vídeo 16:9 à esquerda e "O que
o vídeo mostra" à direita, com 6 etapas: (1) O e-mail chega — LIA, em produção; (2) A LIA lê e classifica — LIA;
(3) Registra no monday — LIA; (4) Cria a pasta — GPS, em produção; (5) Preenche a planilha de valoração — Orça+AI, fase
de testes; (6) Gera a carta orçamento — COP.IA, fase de testes.

**3.8.3 Fonte.** `lia_na_pratica/__init__.py` (`ARQUIVO`, `CAPA`, `LEGENDAS`, `ETAPAS`; fonte única do pop-up e da
página oculta), `static/lia_video.js`, `app/static/video/` (com `LEIA-ME.md`).

**3.8.4 Regras.** O botão "Ver a LIA na prática" fica **sempre visível**, mesmo sem o vídeo (decisão do Caio,
31/10/2026, F09). Sem `ARQUIVO` (hoje `""`): quadro "Vídeo a incluir" (`role="img"`), sem player. Com `ARQUIVO`:
`<video controls preload="metadata">`, sem autoplay, `poster` com `CAPA`, legenda pt-BR com `LEGENDAS` (.vtt). Para
incluir: salvar `app/static/video/lia-na-pratica.mp4`, preencher `ARQUIVO`, trocar `estado` para "pronta" e tirar
`nota_estado` em `apresentacao.py:473-474`, rodar os testes.

**3.8.5–3.8.6 Números e SQL.** Não se aplica.

**3.8.7 Interações.** `showModal()`; fecha com Fechar, Esc ou clique no fundo; o vídeo pausa ao fechar; o foco volta ao
botão; setas e espaço dentro do pop-up não trocam de página. Sem JS, o botão abre `/lia-na-pratica#1`.

**3.8.8 Acessibilidade e movimento.** Foco preso no diálogo; entra crescendo a partir do botão (~420 ms) só com
movimento permitido.

**3.8.9 Testes.** `tests/test_v2_paginas.py`.

**3.8.10 Pendências.** **O arquivo do vídeo não existe**; duração, legendas e capa; confirmar as 6 etapas com a equipe.

### 3.9 Iniciativas de automação e IA

**3.9.1 Pergunta / título.** "Quais iniciativas de automação e IA estamos tocando?" (`nota_estado="andamento de agosto,
a atualizar"`).

**3.9.2 O que mostra.** 4 colunas por fase com contagem e medidor de maturidade: **Em produção** (LIA, GPS), **Fase de
testes** (Orça+AI, COP.IA), **Em desenvolvimento** (FILA, CACHÊ, G1.IA), **Na esteira** (Salesforce, MATCH, Auto+,
GUIA+) = 11 iniciativas. Painel de detalhe (fase, sigla, nome, descrição, responsável, status, próximo passo, "Ver
resultados" só na LIA, "Expandir", galeria de anexos); visor de anexos; pop-up de edição.

**3.9.3 Fonte.** Quadro salvo (`iniciativas/repositorio.py`); semente `iniciativas/catalogo.py` na 1ª execução
(F04, 31/10/2026: itens e marcas numa transação só no SQLite, `BEGIN IMMEDIATE`, e num batch só no Firestore, com
`semeado_em` como `create` no mesmo batch; marca sem nenhum item = semente interrompida, semeia de novo); tela `iniciativas/__init__.py::tela()`; API `iniciativas/api.py`; JS
`static/iniciativas.js`. Se o armazenamento falhar, a página mostra o catálogo, só leitura, com aviso.

**3.9.4 Regras.**

1. Dados (SQLite; no Firestore, os mesmos campos): `iniciativas` (`id`, `sigla`, `nome`, `fase`, `ordem`,
   `responsavel`, `descricao`, `status`, `proximo`, `link_rotulo`, `link_href`, `semente`, `criado_em`, `atualizado_em`,
   `atualizado_por`, `excluido`), `anexos` (`id` uuid, `iniciativa_id`, `nome_original`, `arquivo` = `<uuid>.<ext>`,
   `tipo`, `tamanho`, `ordem`, `criado_em`), `meta` (`semeado_em`, `alterado`).
2. Limites: sigla ≤ 40, nome ≤ 120, descrição ≤ 400, responsável ≤ 80, status e próximo ≤ 120 (`repositorio.MAX`);
   sigla ou nome obrigatório; fase entre as 4 do catálogo; campos extras recusados (422).
3. Ordem: nova = fim da coluna; mudar de fase = fim da nova coluna; mover renumera origem e destino. Exclusão lógica.
4. Densidade da coluna: até 3 cartões = 1, 4 = 2, 5+ = 3 (`densidade`, igual no JS).
5. Concorrência: uma trava por processo; com mais de uma instância pode haver empate de `ordem` (renumerado na próxima
   mudança); o roteiro usa `--max-instances=1`.

**API** (prefixo `/viu-agenciamento/iniciativas/api`):

| Método e caminho | Corpo | Resposta |
|---|---|---|
| `GET /iniciativas` | — | `{iniciativas, anexos, na_semente, edicao}` |
| `POST /iniciativas` | `{sigla, nome, fase, responsavel, descricao, status, proximo}` | 201 + iniciativa |
| `PUT /iniciativas/{id}` | campos parciais | 200 |
| `POST /iniciativas/{id}/mover` | `{fase, posicao}` (0..500) | 200 |
| `DELETE /iniciativas/{id}` | — | 204 (exclusão lógica) |
| `GET /iniciativas/{id}/anexos` | — | lista |
| `POST /iniciativas/{id}/anexos` | `multipart/form-data`, campo `arquivo` | 201 + anexo |
| `DELETE /anexos/{aid}` | — | 204 |
| `GET /anexos/{aid}/arquivo` | — | arquivo `inline` |
| `POST /importar` | estado do `localStorage` antigo (`ini-quadro:v1`) | `{incluidas, editadas, excluidas}`; 409 se o quadro já mudou |

Erros: 400 regra, 403 guarda, 404, 409, 413, 415, 422, 503 (armazenamento indisponível). Toda escrita gera log
estruturado com o usuário (`iniciativas: criada/editada/movida/…`).

**Segurança das escritas e dos anexos:**

- **Edição:** `INICIATIVAS_EDICAO` ligada no computador; **em produção desligada por padrão** (403); `on` só com o
  serviço atrás do IAP. A página recebe `edicao` = edição ligada **e** armazenamento respondendo.
- **CSRF mínimo** (`api.escrita`, 98-109): exige `X-Requested-With: iniciativas` (força preflight, que o app não
  autoriza); recusa `Sec-Fetch-Site` diferente de `same-origin`/`none`; recusa `Origin` cujo host ≠ `Host`.
- **Upload:** extensão **e** assinatura (PNG, JPEG, GIF, WebP, PDF; SVG, HTML e o resto recusados), vazio recusado, até
  10 MB (`Content-Length` + bytes contados durante a recepção, 413 sem depender do cabeçalho, F11 + regra; gravação
  em `run_in_threadpool`), até 30 por iniciativa, nome salvo = uuid, nome
  original só na legenda (sem controle nem barras). Multipart com `max_files=1, max_fields=1`.
- **Servir anexo:** `Content-Type` do tipo conferido, `nosniff`, `Content-Disposition: inline` com nome ASCII limpo +
  `filename*` UTF-8, `Cross-Origin-Resource-Policy: same-origin`, CSP `default-src 'none'; img-src 'self'; style-src
  'unsafe-inline'; object-src 'self'; frame-ancestors 'self'` (permite o visor de PDF num quadro do próprio site).
- JS sem `innerHTML` (só `textContent` e nós criados); HTML sem `style=`.

**Edição em produção:** com `AUTH=iap` + `INICIATIVAS_EDICAO=on`, todos que passam pelo IAP editam; `atualizado_por`
grava o e-mail do IAP. Backup local: `python tools/iniciativas_admin.py backup` (zip em
`~/.ppd-agenciamento-v2/backups/`); restaurar o catálogo: `restaurar-catalogo --confirmo-restaurar`. Em produção:
`gcloud firestore export` + cópia do bucket (roteiro, bloco 9).

**3.9.5 Números.** 11 iniciativas na semente (2 · 2 · 3 · 4); "Responsável a definir" em todas; 0 anexos (banco
temporário da leitura de 31/10; o banco real do Caio não foi lido).

**3.9.6 SQL.** Não se aplica (fora do BigQuery).

**3.9.7 Interações.** Clique abre o detalhe (um por vez; fecha com Esc, clique fora ou Fechar); "+ Nova iniciativa" por
coluna; lápis abre o pop-up; arrastar entre fases e na ordem; Alt + setas movem pelo teclado; excluir pede confirmação;
mover e excluir são otimistas (voltam ao salvo se o servidor falhar); criar e editar só dizem "Salvo" depois do OK.
Aviso `aria-live` ("Salvando…", "Salvo", erros). Visor: ← → entre anexos, contador "2 de 3", "Abrir em nova aba".
"Importar alterações deste navegador" aparece uma vez se houver `localStorage` antigo e o quadro ainda estiver na semente.

**3.9.8 Acessibilidade e movimento.** Controles nativos com nome; mensagens de erro `role="alert"`; foco devolvido ao
fechar; sem loop (linhas animadas de fundo retiradas pelo Caio); entrada em onda só com movimento permitido; cabe sem
rolagem em 1440×810, 1280×720 e 1920×1080.

**3.9.9 Testes.** `tests/test_iniciativas_servidor.py` (30 testes: semente única, CRUD, mover, exclusão, importação,
validação, CSRF, produção simulada, uploads válidos e inválidos, queda para o catálogo, Firestore/Storage falsos, IAP,
persistência ponta a ponta, falha na gravação), `tests/test_v2_paginas.py`.

**3.9.10 Decisões e pendências.** Dados no servidor (Caio e gerente, 30–31/10/2026). Pendentes: data de referência do
andamento ("agosto"); confirmar FILA, CACHÊ e G1.IA em desenvolvimento; responsáveis; outras iniciativas com "Ver
resultados".

### 3.10 Previsão de demanda

**3.10.1 Pergunta / título.** "Quantos pedidos devem chegar até o fim do mês e do ano?" (`nota_estado="2 decisões
abertas"`).

**3.10.2 O que mostra.** Seletor de talentos; duas colunas (Inbound à esquerda, Mercado à direita); em cada uma, cartões
do **mês vigente** (realizado até a data do acompanhamento, previsão do mês, situação dentro/abaixo/acima da faixa e
"esperado ≈ N") e dos **2 meses seguintes** (previsão e faixa provável); gráfico de 2026 (real, previsto no teste
jun–set, previsão com faixa), modelo e erro médio no teste e fora dele; selo "não robusto" ou "confiança menor"; botão
"Modelos comparados" (`<dialog>` com todos os modelos por família).

**3.10.3 Fonte.** A página só lê `ml/saida/previsao.json` (contrato **v3**, `VERSAO = 3`, `previsao/calculos.py:49`);
sem arquivo válido, máscara. O job de ML (`ml/`) lê `gld_agenciamento_previsao_mensal`,
`gld_agenciamento_2026_previsao_exclusividade_mensal` e `gld_agenciamento_2026_previsao_lotes` (e a silver 2025 só para a
sensibilidade S5, fora da tela). Gatilho e estado em `previsao/job.py`. Rodapé pelas tabelas de `entrada`, com
"acompanhamento até dd/mm" e o aviso de carga diferente (F03, `previsao.coerencia`; seção 5.3).

**3.10.4 Regras e memória de cálculo.**

Página (`previsao/calculos.py`, docstring 1-38):

1. **P1 (D56)** quatro séries, cada uma com o seu modelo: Inbound e Mercado (pedidos = `quantidade +
   quantidade_estimada`), Mercado exclusivos e Mercado não exclusivos (gold de exclusividade).
2. **P4** filtros: Todos = Inbound | Mercado; Exclusivos = Inbound inteiro | Mercado exclusivos; Não exclusivos =
   Inbound "Não se aplica" (todo Inbound é de talento exclusivo; PD24) | Mercado não exclusivos.
3. **P2/P8** teste = jun, jul, ago, set/2026, cada mês previsto no fim do anterior (h1); **WAPE = Σ|previsto − real| ÷
   Σ real**; MAE em pedidos/mês.
4. **P3** vence o menor WAPE no teste; empate (< 1 ponto) = o mais simples.
5. **P5** sem confiança: média no teste < 30 pedidos/mês ou WAPE > 40%.
6. **P9** pé: erro no teste e na verificação jan–mai (fora da escolha) e o erro de repetir o último mês; "não robusto"
   quando o vencedor perde da ingênua fora do teste (C5); "confiança menor" nas séries só de 2026.
7. **P10** cartões: vigente = mês do dia seguinte a `dados_ate`; **esperado até agora = previsão × dias úteis
   decorridos ÷ dias úteis do mês**; "abaixo"/"acima" quando o realizado sai da faixa na mesma proporção (p10 e p90 ×
   fração); o % = realizado ÷ esperado − 1.
8. **P11** "por quê" do vigente fora da faixa: diagnóstico de lotes (3 ou mais pedidos da mesma marca no mesmo dia).
9. **P7** eixo fixo jan–dez/2026 (`ANO = 2026`, linha 50).

Protocolo (`ml/regua.py`, D48 + R7 da D56): **R1** janela móvel de 12 meses fechados antes de cada origem; **R2** teste
h1 jun–set/2026, informativos h2/h3 e verificação h1 jan–mai/2026; **R4** modelo que pede mais meses que a janela "não se
aplica"; **R5** futuro = out, nov, dez com treino out/25–set/26 (o mês em andamento nunca treina); **R7** séries curtas
com janela expansiva e mínimo por modelo. Critério (`ml/previsao.py`): **C1** menor WAPE h1 jun–set, empate < 1 ponto →
o mais simples (referência → combinação → clássico → ARIMAX/Prophet → boosting → rede neural → AutoTS); **C3** sem
confiança; **C5** robustez informativa (alternativa = melhor entre os que batem a ingênua nos dois períodos; não troca
o vencedor). Ressalva registrada: a escolha é feita no próprio teste (4 meses), então o erro do vencedor é otimista.

Job (`previsao/job.py`): **J1** mês fechado novo → `python -m ml.rodar --rotina` (todos os modelos, ~9 min, uma vez
por mês); mesma carga do mês → `--acompanhamento` (só o realizado); **J2** só com `PREVISAO_JOB` (desligado em produção),
pasta `ml/` e `statsmodels`; **J3** trava `ml/saida/rotina.lock` < 3 h e 30 min entre disparos; **J4** log e
`rotina_estado.json` (falha visível na página); **J5** com `CONGELAR` ou modo apresentação o site não dispara o job;
**J6** fim da carga = E3 (`app/corte.py`).

**3.10.5 Números** (retrato de **setembro/2026**, refeito em 26/10/2026 com a carga de 26/10; acompanhamento de outubro
**até 27/10**, 18 de 21 dias úteis — o arquivo não foi atualizado com a carga de 30/10; ver ponto A9).

| Série | Modelo | Erro teste jun–set · jan–mai | Out (realizado · previsto) | Nov | Dez |
|---|---|---|---|---|---|
| Inbound | Média de 6 meses | 14% · 27% | 146 até 27/10 · 138 (faixa 131–212), dentro da faixa (+23% sobre o esperado ≈ 119) | 138 (146–219) | 138 (147–221) |
| Mercado | Rede neural (1 neurônio), **não robusto** | 13% · 27% | 351 até 27/10 · 464 (334–483), dentro (−12% sobre ≈ 398) | 517 (372–538) | 588 (423–612) |

Alternativa robusta do Mercado (C5): ARIMA com tendência, 16% · 20%. Mercado exclusivos e não exclusivos: ficha
`previsao.md`, seção 5.0.

**3.10.6 SQL para reproduzir** (séries de entrada do ML; detalhe completo na ficha, 5.0.2).

```sql
SELECT FORMAT_DATE('%Y-%m', data) AS mes, grupo_input, SUM(quantidade + quantidade_estimada) AS pedidos
FROM `gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_entrada_diaria`
WHERE grupo_input IN ('Inbound', 'Mercado') AND data BETWEEN '2025-10-01' AND '2026-10-29'
GROUP BY 1, 2 ORDER BY 1, 2;
-- deve bater, por mês fechado, com a coluna "Entraram" da tela (ex.: jun/2026 Inbound 112, Mercado 339)
```

**3.10.7 Interações.** Seletor (links); "Modelos comparados" (`<dialog>` nativo com `commandfor`/`command` e JS de
reserva); tabela de valores por mês para o leitor de tela sob cada gráfico.

**3.10.8 Acessibilidade e movimento.** Cada gráfico tem descrição e tabela; situação com ícone + texto; sem loop.

**3.10.9 Testes.** `test_previsao_pagina.py`, `test_qualidade_previsao.py`, `test_ml_*.py` (régua, clássico,
combinação, ARIMAX, Prophet, boosting, neural, AutoTS); `tools/auditar_modelos.py` (recalcula métricas dos backtests
salvos).

**3.10.10 Decisões e pendências.** D47 (histórico), **D48** (protocolo), D55 (tela só com os gráficos; Inbound não
exclusivo "não se aplica"), **D56** (uma série e um modelo por recorte). **Abertas: DC1 (vencedor do Mercado), DC2
(nov/dez como previsão ou cenário)**, DC3 (faixa "provável"), DC4, DC5. Pendências PD09 (acerto fora do teste, mês a mês),
PD10, PD22 (virada do ano), **PD23 (job em produção não existe)**, PD24.

### 3.11 Encerramento

**3.11.1 Pergunta / título.** "Obrigado." (sobretítulo "ViU Agenciamento"; `encerramento={...}`,
`apresentacao.py:399-409`; `frase` e `pergunta` vazias; gancho "Encerramento").

**3.11.2 O que mostra.** Fundo marinho; faixa branca no topo com o logo e a data da capa ("Outubro de 2026"); "Obrigado."
com fio amarelo; botão amarelo **"Voltar ao início"** (leva à capa); mascote balão de conversa no canto inferior direito
(SVG decorativo gerado por script).

**3.11.3 Fonte.** Nenhuma; `templates/encerramento.html`, `static/fim.js`, bloco "Encerramento (V2…)" de `estilo.css`.
Rodapé datado mantido.

**3.11.4–3.11.6 Regras, números e SQL.** Não se aplica.

**3.11.7 Interações.** "Voltar ao início"; ← volta à Previsão.

**3.11.8 Acessibilidade e movimento.** Título `h2` que nomeia o slide; logo com `alt`; mascote `aria-hidden`; contraste
≥ 4,5:1. Entrada única até 1,2 s; **loops contínuos SMIL** (aceno 1,4 s, piscar 3,4 s, flutuar 3,2 s, coração 1,4 s)
iniciados por `fim.js` 1,1 s depois de abrir; pausa com aba oculta; nada anima com movimento reduzido ou sem JS.

**3.11.9 Testes.** `test_portal.py::test_capa_e_encerramento`,
`test_movimento.py::test_encerramento_loop_so_por_smil_e_parado_sem_movimento`, `test_entrada_das_paginas_ate_1200ms`.

**3.11.10 Decisões.** Caio, 31/10/2026 (3 rodadas no mesmo dia; versões em `_descartados/2026-10-31/encerramento_antes/`).
Outro agente estava mexendo no encerramento durante a escrita deste PRD (seção 11).

### 3.12 Páginas ocultas (resumo)

- **Atendimento** (`/atendimento`): pronta desde a D33/D58b, fora deste relatório. `atendimento/calculos.py` sobre
  `atendimento_mensal`, `entrada_diaria`, `fluxo_mensal` e `saidas_status`. % = Entregues no Mês ÷ Para atender; objetivo
  100%, alerta 90%. Ficha `docs/paginas/atendimento.md`; testes `test_atendimento*.py`.
- **A LIA na prática** (`/lia-na-pratica#1`): a mesma fonte do pop-up (3.8).
- **Resultado** (`/negocios-fechados`) e **Qualidade** (`/qualidade`): máscaras com a pergunta, o motivo e as
  pendências (PD05, PD06, PD18; PD12, PD13, PD24). Ficha `docs/paginas/demais.md`.
- **O que falta** (`/o-que-falta`): estado de cada seção e os 4 pedidos de decisão (`pendencias.PEDIDOS`), gerada de
  `pendencias.py`; ficha conferida por `tests/test_documentacao.py`.

---

## 4. Regras transversais

| Regra | Definição | Onde |
|---|---|---|
| **Expediente (portal e SLA)** | seg–sex, **10h–13h e 14h–19h** (8 h por dia, almoço 13h–14h fora), sem feriados | `app/expediente.py:11` (`SEM_ALMOCO`), gold R24 |
| **Feriados** | fixos (01/01, 20/01, 25/01, 21/04, 23/04, 01/05, 09/07, 07/09, 12/10, 02/11, 15/11, 20/11, 24/12, 25/12, 31/12) + Carnaval (seg e ter), Cinzas, Sexta-feira Santa e Corpus Christi pela Páscoa (Meeus) | `app/expediente.py:13-37` |
| **Expediente da LIA** | dias úteis **10h–19h com o almoço 12h–13h dentro**; só na página LIA | `lia/__init__.py:172-183` |
| **Típico** | **mediana** ("metade leva até ele"); nunca "mediana" na tela | glossário (`docs/paginas/README.md`) |
| **Dia de trabalho** | 8 h de expediente (`HORAS_DIA = 8`) | `sla/calculos.py:63` |
| **Meta do SLA (sugerida, D38/D-SLA-7)** | **metade dos orçamentos (50%) prontos em até 2 dias de trabalho (16 h)**; não oficial | `sla/calculos.py:64-66`; pedido nº 1 de `PEDIDOS` |
| **Mês do SLA (D-SLA-1)** | mês da **1ª entrega** ao cliente; só meses completos (C7) | `sla/calculos.py:203-205` |
| **Prazo do cliente (C3c)** | mediana dos dias úteis com fração, 1 casa | `sla/calculos.py:439-455` |
| **Corte E3** | a carga cobre até a **véspera** (São Paulo) do dia de `MAX(_processado_em)`; sem metadado, `MAX(data)`. Mês fechado = mês anterior ao do dia seguinte ao fim | `app/corte.py` (e cópias, ponto A6) |
| **Mês parcial** | mês de `MAX(_processado_em)` (Demanda: mês de `fim + 1 dia`) | `app/sla.py:17-25`, `entrada/calculos.py:149` |
| **Categorias de talentos** | Exclusivos (`exclusivo = TRUE`, na data do pedido), Não exclusivos (`FALSE`; inclui o Squad de Talentos), Talento não informado (sem talento; só em "Todos" no SLA) | `talentos/calculos.py:48-52`, `sla/calculos.py:192-196` |
| **Arredondamento** | inteiros e % meio para cima; desde a F13 (31/10/2026) a política dos percentuais isolados mora em `formato.arredondar`/`pct`/`pct_inteiro` (1/8 = 13% em todas as páginas; sem `round()`, que arredonda o empate para o par); parcelas de um todo fecham em 100 pelo maior resto (`formato.parcelas_100`); sinal da variação pelo % arredondado | `formato.py` (`_pcts`/`_pct` de `entrada/calculos.py` delegam) |
| **Variação** | atual ÷ anterior − 1, só com anterior ≥ 30 | `entrada/calculos.py:108-110` |
| **Filtro** | só aplica pelo link/botão; nada recarrega ao mudar um campo | `CLAUDE.md`, regra 10 |

**Glossário da tela** (`docs/paginas/README.md`): pedido = o que entra; orçamento = o que a equipe entrega; típico =
mediana; dias de trabalho = horas da equipe em dias de 8 h; dias úteis no calendário = prazo que o cliente espera;
saíram sem entrega = declinados, standby ou encerrados antes da entrega; fora da curva = acima de Q3 + 1,5 × IQR (na
escala log); sino = curva normal.

---

## 5. Dados e atualização

### 5.1 Origem de cada tabela

Todas as golds são criadas e documentadas no projeto irmão `../PPD-GOLDEN-AGENCIAMENTO-MONDAY` (fichas em
`docs/tabelas/` de lá), a partir da silver do monday (`PPD-SILVER-MONDAY`), que vem da bronze (`PPD-BRONZE-MONDAY`). As
tabelas são gravadas pelo job `gold-agenciamento`; as views refletem a tabela de base na hora. Tabela por tabela: seção
2.2. Fora do BigQuery: retrato da LIA (Cloud Storage da LIA), Iniciativas (SQLite/Firestore), previsão (JSON do job).

### 5.2 Horário da carga

Job `gold-agenciamento` **seg–sex às 09:00 (Brasília)** (`config.GOLD_HORA = 9`); tolerância de 45 min antes de a tela
acusar "base atrasada" (`config.GOLD_TOLERANCIA_MIN`; `dados.atualizacao_esperada`). Na carga vigente, cada tabela tem
`_processado_em` entre 09:01:46 e 09:03:21 de 30/10/2026; o `modified` de todas é 09:04:13.

### 5.3 Corte e congelamento em 31/10/2026 para a reunião de 04/11 (D65)

Decisão do Caio de 31/10/2026 (D65 no `docs/PRD.md`, seção 8). Código: `app/congelamento.py` (K1–K7, B1–B5),
`app/config.py:76-86`, `app/dados.py`, `app/conferir_base.py` (conferência do build); ferramenta `tools/congelar_base.py`
(gera; `--conferir`/`--sem-rede` sem BigQuery; `--recuperar`); testes `tests/test_corte.py` (22); roteiro do dia:
**`docs/congelar_outubro.md`**. Correções da auditoria do Codex (F01, F02, F03, F07, F08):
`docs/auditoria/correcoes_2026-10-31.md`, seção "Dados e congelamento".

- **Configuração:** `CORTE_DADOS` (padrão **`2026-10-31`**; `off` desliga), `CORTE_FOLGA_DIAS` (padrão 1),
  `BASE_CONGELADA_DIR` (padrão `app/base_congelada/`). Vale no computador **e em produção**.
- **K1** fim de uma carga = E3 (véspera do `_processado_em`).
- **K2** fim < corte → carga aceita normalmente (o portal continua atualizando).
- **K3** corte ≤ fim ≤ corte + folga → **última carga aceita**: a tabela congela **em memória**. Daí em diante nada
  troca a tabela, nem a recarga forçada. A gravação é do conjunto (B1–B3, abaixo).
- **K4** fim > corte + folga → carga ignorada (a tabela fica com o que tinha; a falha aparece).
- **K5** todas as tabelas congelam na **mesma** carga (mesmo fim das já congeladas em memória); tabela de outra carga é
  ignorada.
- **K6** com a base válida e do mesmo corte, a tabela nasce dela, **sem consultar o BigQuery**; em produção nada é
  gravado, os arquivos entram na imagem pelo `COPY app/`, o build confere o pacote (`python -m app.conferir_base`) e o
  arranque confere a base de novo (`congelamento.exigir`): sem base completa, a instância não sobe (F01). Em produção,
  sem base válida, `dados.py` levanta `BaseInvalida` em vez de chamar o BigQuery.
- **K7** base de outro corte, sem manifesto, incompleta ou com hash/linhas diferentes → ignorada **inteira** com aviso.
- **B1 (F02)** congelada em memória ≠ persistida: a base só é gravada quando **todas** as tabelas do portal congelaram
  na mesma carga, e só vira `persistida` depois de gravada e conferida (sha256, linhas e colunas relidos). Falha de
  gravação: erro no log e no `/saude`, base segue em memória, nova tentativa a cada 30 s (na leitura) ou pelo
  `tools/congelar_base.py`.
- **B2 (F07)** um escritor por vez: trava entre processos (`.escrita.lock`, O_EXCL; trava com mais de 15 min = abandonada).
- **B3 (F07/F08)** publicação atômica do conjunto: pasta de versão nova e exclusiva `v-<fim>-<momento>-<hex>` (parquets +
  cópia do manifesto, por último) → conferência → `manifesto.json` da raiz trocado por `os.replace`. Versões antigas
  ficam (nada se apaga).
- **B4 (F08)** a leitura valida o manifesto global (formato 2, corte, fim na folga, um só fim, todas as tabelas, arquivos,
  sha256) antes de entregar qualquer tabela; um problema invalida o conjunto.
- **B5 (F08)** recuperação: `tools/congelar_base.py --recuperar` publica a versão completa mais nova (gravação
  interrompida depois de completa) e relata as parciais; sem versão completa, refazer a base enquanto a carga estiver na
  folga.
- **Previsão × base (F03):** o retrato (`carga.processado_em`) e o acompanhamento (`acompanhamento.processado_em`) do
  `previsao.json` são comparados com a carga da base (`previsao.coerencia`). A página mostra no rodapé
  "acompanhamento até dd/mm" e, se alguma peça for de outra carga, um aviso discreto com ícone e texto
  ("acompanhamento de outra carga (dd/mm/aaaa)"); nada volta ao topo da página. O `--conferir` e o build reprovam a
  incoerência.
- **Nenhuma linha é filtrada** (D57): o corte escolhe qual carga inteira da gold fica, porque as tabelas trazem o estado
  do board na hora da carga (em aberto, status atual, horas).
- Rodapé "base congelada para a apresentação" só quando todas as fontes da página estão `congelada`
  (`dados.base_congelada`, 344-349). Esperado: "Dados até 31/10/2026 · atualizados em 01/11/2026, HH:MM · base congelada
  para a apresentação".

**Calendário (31/10/2026 é sábado; a gold roda seg–sex 09:00):**

| Caminho | O que fazer | Rodapé |
|---|---|---|
| A (alternativa) | no domingo 01/11, o Caio dispara à mão bronze → silver → gold (`gcloud scheduler jobs run …`, um por vez) | Dados até **31/10/2026** |
| **B (escolhido pelo Caio em 31/10)** | esperar a carga agendada de segunda 02/11 09:00 (Finados; conferir se o agendamento `1-5` roda) | Dados até **01/11/2026** (aceita pela folga) |

**Passos do roteiro** (`docs/congelar_outubro.md`): 0) conferir se a carga de segunda rodou (caminho B; disparar à mão
só se falhou); 1) conferir no BigQuery que as 6 tabelas trazem `dados_ate` = 01/11; 2) `tools\congelar_base.py`
(10 tabelas congeladas e "base congelada gravada e conferida": `manifesto.json` + pasta `v-…` com cerca de 1 MB em
`app\base_congelada\`); 3) **Previsão: retrato de outubro** (`python -m ml.rodar --rotina`, guardando antes o de setembro
em `_descartados\2026-11-01\`) e **LIA até 31/10** (`tools\extrair_lia.py --fim 2026-10-31`, depois da meia-noite);
4) testes; 5) `tools\congelar_base.py --conferir` e um servidor de conferência **sem credenciais** na 8401 percorrendo a
sequência inteira; 6) deploy com `CORTE_DADOS=2026-10-31` explícito.

Com o retrato de outubro, os meses previstos passam a ser nov, dez e jan e outubro entra como mês fechado (a régua de
teste jun–set não muda). Ensaio registrado no roteiro (31/10): corte simulado em 29/10 numa pasta temporária, 10 tabelas
congeladas e as 8 páginas geradas do arquivo idênticas às do BigQuery. Na carga vigente (fim 29/10 < corte) o portal
ainda **aceita** cargas e `app/base_congelada/` ainda não existe. Os números da seção 3 mudam com a carga do corte; as
fichas pedem a troca do "Retrato da carga".

### 5.4 Como descongelar

Do roteiro (`docs/congelar_outubro.md`, "Depois da reunião"):

1. **Computador:** `CORTE_DADOS=off` no `.env` (ou `$env:CORTE_DADOS = "off"`) e reiniciar. Sem o corte, volta a D63
   (carga lida na subida); `CONGELAR=false` volta a recarregar a cada carga.
2. Mover `app\base_congelada\` para `_descartados\AAAA-MM-DD\app\base_congelada\` (com linha no `LEIAME.md`).
3. Trocar o padrão do código em `app/config.py` para `"off"` e registrar no PRD.
4. **Produção:** tirar do ar (bloco 9 do roteiro de deploy) ou novo deploy com `CORTE_DADOS=off` (volta a ler o BigQuery;
   a conta de serviço precisa do bloco 4b).
5. Novo corte: `CORTE_DADOS=AAAA-MM-DD`; fichas de outro corte são ignoradas (K7).

### 5.5 Atualização das fontes fora do BigQuery

- **LIA:** `python tools/extrair_lia.py` à mão (credenciais do gcloud-viu, só leitura), depois os testes.
- **Previsão:** no computador, a carga nova da entrada dispara o job (salvo `CONGELAR`/modo apresentação); à mão:
  `python -m ml.rodar --acompanhamento` (realizado do mês) ou `--rotina` (mês fechado novo). Em produção: não existe
  (PD23).
- **Iniciativas:** pela própria página (edição ligada) ou `tools/iniciativas_admin.py`.

---

## 6. Segurança

### 6.1 D10

**Nunca publicar com `AUTH=off`** nem com o serviço aberto antes do controle de acesso. Trava no código: com `K_SERVICE`
definido, `AUTH=off` derruba a subida (`main.py:22-24`); qualquer valor diferente de `off`/`iap` também
(`main.py:30-32`). `SINC`, `CONGELAR`, `PREVISAO_JOB` e o exemplo fixo do estudo ficam desligados sozinhos em produção.

### 6.2 Exceção temporária do IAP — **aguarda aprovação do Caio**

`AUTH=iap` (`app/iap.py`, 30/10/2026) foi criada para a reunião do gerente e está documentada como "a aprovar pelo
Caio" (`CLAUDE.md`, `docs/deploy_iniciativas.md`). Defesas em camadas: `--no-allow-unauthenticated` (só o IAP chama o
Cloud Run); JWT conferido em **toda** requisição (assinatura ES256, emissor, público, validade); sem cabeçalho válido,
401 (fecha por padrão); `IAP_AUDIENCE` errado também fecha tudo. **Chaves do IAP (F06, 31/10/2026):** renovadas em
segundo plano depois de 1 h (thread única, 3 tentativas), sem rede no caminho da requisição; se a renovação falhar,
as anteriores valem até 24 h; sem chave utilizável, busca na hora fora do event loop e, falhando, **503** com log (não
401); `kid` novo dispara uma renovação imediata (no máximo 1/min). `/saude` não é isenta (A29).
Acesso por pessoa com `roles/iap.httpsResourceAccessor`. **Nada foi executado no GCP.** Depois da reunião, o roteiro
manda tirar do ar (bloco 9) ou seguir para a fase 2 (login próprio).

### 6.3 Segredos

Nenhum segredo no código. Segredos só no Secret Manager; o Claude não vê valores (`CLAUDE.md`, regra 5). No computador,
credenciais ADC de `C:\Users\CCMB\AppData\Roaming\gcloud-viu`; no Cloud Run, ADC da conta de serviço (sem chave em
arquivo). `.env` e o banco/anexos locais ficam fora da imagem (`.dockerignore`, `.gcloudignore`). Sem LLM por API (D2).

### 6.4 Dados sensíveis nas imagens e nas telas

- **Imagens do Roadmap** (`tools/gerar_imagens_roadmap.py`, ficha `roadmap.md`, "Imagens e painel ampliado"): no
  mapeamento "Fluxo 1" foram **desfocados** nomes de pessoas, exemplo de contrato e de proposta, e-mail da caixa de
  pedidos e todas as capturas coladas; no print "Controle do processo de pagamento", a tabela inteira por talento, marca
  e projeto; no print "Contratos e bloqueios", saudação com nome e data, nomes de talentos, contagens por talento e datas
  por contrato. Ficam títulos, filtros e totais agregados. Desfoque gaussiano com raio ≥ 6 px na escala da imagem.
- **Dados pessoais que continuam na tela por decisão:** nomes de talentos (top 10 de Talentos, decisão do Caio de
  24/10/2026) e o orçamento de exemplo do slide 1 do estudo (marca, talento e projeto reais). Com a publicação, isso
  passa a ser visto por quem tiver acesso pelo IAP.
- **LIA:** o retrato só tem contagens agregadas (sem remetente, assunto ou conteúdo).
- **Anexos das Iniciativas:** podem conter qualquer coisa que um editor suba; o bucket é privado e o app é o único que
  serve.
- `tools/empacotar_offline.py` gera HTML estático com os números (para quem não tem servidor): fica fora de qualquer
  controle de acesso depois de enviado.

---

## 7. Desempenho

**Parcialmente a completar.** Outro agente otimizou a navegação em 31/10/2026 (código de 02:55–03:00); até a releitura
final o `docs/PRD.md` não tinha seção própria de desempenho com as medições. O que está no código:

| Mudança (31/10/2026) | Onde | Efeito declarado no código |
|---|---|---|
| Templates: data do arquivo conferida no máximo a cada 2 s (DEV) | `main.py:38-52` (`_CarregadorConferido`) | no Google Drive, cada consulta custava ~8 ms (≈ 40 ms por página) |
| Versão dos estáticos refeita em segundo plano (DEV) | `main.py:76-93` | reler `static/` no Drive custava 0,5–0,9 s a cada 5 s, dentro da troca de página |
| Aquecimento na subida: compila todos os templates e monta o estudo | `main.py:117-136` (`_aquecer_paginas`) | a 1ª visita não paga ~0,9 s de compilação nem ~1 s do estudo |
| Cache de telas por carga e parâmetros (`_guardado`, até `LIMITE_TELAS` = 40) | `apresentacao.py:87-110`; usado em Demanda (`inicio`), Talentos, estudo (`exemplo`, `cobertura`) e Previsão (`previsao_carga`) | as contas pandas de cada tela só rodam uma vez por carga |
| `processado_em` guardado por carga | `dados.py:256-268` | uma conta por carga, não por página |
| Tamanho das imagens do Roadmap pelo cabeçalho (30 bytes), guardado fora de DEV | `roadmap/__init__.py:152-160` | antes lia o arquivo inteiro a cada página |
| Speculation Rules: vizinhas e ✕ pré-renderizadas na hora; destinos do Roadmap com prefetch | `main.py:211-226` | troca de página "instantânea" pelas setas do teclado |

Já existiam: tabelas inteiras em memória por instância; caches derivados por carga; estudo dos 3 grupos aquecido na
carga; com a base congelada em arquivo (D65), nenhuma consulta ao BigQuery. Continuam valendo: em produção, sem a base
congelada, a conferência do metadado e a recarga rodam **na requisição** (`em_fundo=False`); cada aba aberta refaz a
página inteira a cada 5 min para comparar a versão dos dados (`apresentacao.js:30-44`); LIA relê o JSON e Iniciativas lê
o backend a cada página. Riscos na seção 10.4.

## 8. Testes

### 8.1 Como rodar

```powershell
cd "G:\Meu Drive\Workspace\globo\scripts\PPD-AGENCIAMENTO-SLA-V2"
C:\Users\CCMB\.venvs\ppd-agenciamento-sla\Scripts\python.exe -m pytest tests -q -p no:cacheprovider
# só a documentação:
C:\Users\CCMB\.venvs\ppd-agenciamento-sla\Scripts\python.exe -m pytest tests/test_documentacao.py -q -p no:cacheprovider
```

Sem BigQuery: `tests/conftest.py` troca as tabelas por dados sintéticos; `tests/gold_simulada.py` simula em pandas as
views e colunas que o site lê prontas da gold (mudou uma regra na gold, mude a simulação). Iniciativas sempre num banco
temporário (fixture `quadro_limpo`). Conferências contra o BigQuery (só leitura) são ferramentas, não testes:
`tools/checar_reuniao.py`, `tools/conferir_estudo.py`; layout: `node tools/conferir_layout.mjs` (servidor no ar).

### 8.2 Número atual

**629 testes aprovados** em 31/10/2026, depois das correções da auditoria do Codex (suíte completa, `AUTH=off`).

### 8.3 O que cada arquivo cobre

| Arquivo | Testes | Cobre |
|---|---:|---|
| `test_seguranca_iniciativas.py` | 16 | auditoria de 31/10: chaves do IAP (F06), `/saude` (A29), semente (F04), upload (F11), `/sinc` (F12/A32), pacote (F17/A33), botões do Roadmap (F19) |
| `test_portal.py` | 19 | área como portal: ordem, próxima pergunta, máscaras, "O que falta", modo apresentação, capa e encerramento |
| `test_rotas.py` | 20 | rotas, redirecionamentos, conteúdo e cabeçalhos (CSP, cache) |
| `test_v2_paginas.py` | 23 | páginas da V2: Roadmap, LIA, vídeo, Iniciativas (tela), capa |
| `test_iniciativas_servidor.py` | 30 | quadro salvo, API, CSRF, uploads, Firestore falso, IAP, persistência |
| `test_corte.py` | 22 | D65: corte e congelamento; F01/F02/F07/F08 (base como unidade, manifesto, trava, recuperação, build e arranque) |
| `test_auditoria_dados.py` | 16 | F03 (Previsão × base), F05 (LIA fora do contrato, aquecimento), F10 (rodapés por seção), F13 (arredondamento) |
| `test_dados.py` | 14 | política de carga e falha de `app/dados.py` (BigQuery falso) |
| `test_documentacao.py` | 2 | ficha `o_que_falta.md` × `pendencias.py` |
| `test_movimento.py` | 8 | regras de movimento (entrada ≤ 1,2 s, loops só onde há exceção) |
| `test_sinc.py` | 3 | `/sinc` (sincronia com a cola) |
| `test_cola.py` | 18 | falas da cola a partir dos contextos das telas |
| `test_expediente.py` | 9 | calendário e horas úteis (simuladas) |
| `test_formato_variacao.py` | 11 | textos de variação pelo % arredondado |
| `test_calculos.py` | 7 | regras C1–C11 e arredondamento |
| `test_inicio_d52.py`, `test_inicio_revisao.py` | 3 + 8 | Demanda |
| `test_revisao_20261024.py`, `test_revisao_20261025.py` | 8 + 20 | regressões das revisões (cortes, filas, coerência entre fontes) |
| `test_talentos_d50.py`, `test_talentos_d51.py` | 8 + 17 | Talentos (seletor, herói, mapa, corrida) |
| `test_sla_*.py` (11 arquivos) | 153 | SLA e estudo (D38, D54, meses, tempo, travas, tipo, conclusão, movimento, batalha) |
| `test_exploracao.py` | 9 | slide 2 do estudo |
| `test_batalha2_interface.py`, `test_batalha2_textos.py` | 22 + 16 | batalha 2 (rodapé, vocabulário, interface) |
| `test_atendimento*.py` (3) | 19 | Atendimento (oculta) |
| `test_auditoria_integridade.py` | 11 | regressões da auditoria de 26/10 |
| `test_previsao_pagina.py`, `test_qualidade_previsao.py` | 21 + 8 | Previsão (página, contrato) e Qualidade |
| `test_ml_*.py` (8) | 66 | régua e modelos de ML com séries sintéticas |

---

## 9. Pendências e riscos conhecidos

### 9.1 Pendências da área (`pendencias.py`, códigos PD)

| Código | Seção | O que falta | Quem |
|---|---|---|---|
| PD01, PD02a, PD02b, PD03, PD20 | Talentos | exclusividade e ranking na gold (já feitos pela D57: texto desatualizado), cadastro limpo de não exclusivos, exclusivos de 2025 com vigência, virada do ano | Caio (gold), equipes |
| PD05, PD06, PD18 | Resultado | contratações fechadas (planilha da Mayara no BigQuery), regra pós-entrega, prazo de pagamento | Mayara + Caio, Financeiro |
| PD07, PD08, PD19 | Atendimento | motivo de quem saiu sem entrega, entrega sem histórico, datas das saídas | Caio, equipe |
| PD09, PD10, PD22, **PD23** | Previsão | acerto fora do teste mês a mês, datas reais de 2025, virada do ano, **job mensal em produção** | Caio |
| PD12, PD13, PD24 | Qualidade | pendências de preenchimento, foto de fim de mês, Inbound marcado como não exclusivo | Caio, equipe |
| PD15, PD21 | SLA | SLA de 2025 (não existe), tempo da equipe pronto na gold (feito pela D57: texto desatualizado) | — |
| PD16 | fora | análise por marca/cliente/setor (CNPJ no Salesforce) | Caio + Salesforce |

**Pedidos de decisão à diretoria** (`PEDIDOS`): oficializar a meta do SLA; subir a planilha de contratações; levar a
exclusividade para a base de entradas (já feito pela D57); validar com a equipe as regras de entrega e de encerramento.

### 9.2 Decisões internas abertas do Caio (`docs/PRD.md`, 9.7)

DC1 vencedor do Mercado · DC2 nov/dez como previsão ou cenário · DC3 faixa "provável" · DC4 escopo da Previsão · DC5
ritmo do mês (resolvida em parte pela D56) · DC6 veredito da meta · DC7 teto acima de 5 dias · DC8 ponte das bases · DC9
recorte do slide de travas · DC10 "amostra aleatória" · DC11 critério do vermelho · DC12 limiar único · DC13 régua do
Atendimento · DC14 vocabulário "represados" · DC15 confirmar trocas · DC16 regras frágeis e virada para 2027.

### 9.3 Pendências da V2 e riscos

| Item | Risco | Situação |
|---|---|---|
| Aprovação do `AUTH=iap` (exceção à D10) | publicar sem o aval | aguarda o Caio |
| Vídeo da LIA | pop-up mostra "Vídeo a incluir" | arquivo não existe |
| `previsao.json` na imagem (D65) | build falha sem o arquivo; precisa ser o retrato de outubro | `Dockerfile` copia desde 31/10; rotina no passo 3 do roteiro do corte |
| Job da Previsão em produção (PD23) | retrato não se atualiza publicado | não existe |
| `MINUTOS_TRIAGEM = 2` | estimativa da LIA sem validação | premissa a confirmar |
| Regra do 1º período da LIA (PRD de @cris × fonte) | números diferentes do relatório da equipe | decisão pendente |
| Corte D65 | depende de rodar a carga certa entre 01/11 e 02/11 e gerar os arquivos antes do deploy | roteiro em `docs/congelar_outubro.md` (5.3) |
| Cola do apresentador (8200) | não funciona com a V2 publicada nem com a V2 local (`SINC=off`) | ver `docs/legado/PRD_cola_8200.md` |
| Fase 2 (login próprio) | só existe o IAP | fase 2 do `CLAUDE.md` |
| Concorrência das Iniciativas | empate de ordem com > 1 instância | roteiro usa `--max-instances=1` |

---

## 10. Pontos para a auditoria

Suspeitas encontradas na leitura do código em 31/10/2026. **Nada foi corrigido.** Severidade: **A** = pode mostrar
número errado ou derrubar a página/publicação; **M** = inconsistência ou risco real com impacto limitado; **B** = limpeza.

### 10.1 Dados, corte e números

| # | Sev. | Onde | Suspeita |
|---|---|---|---|
| A1 | A | `app/config.py:83-84`, `app/congelamento.py:84-86` | `CORTE_DADOS` tem **padrão fixo `2026-10-31`** e vale em produção. Um deploy depois de 02/11 **sem** os arquivos de `app/base_congelada/` faz toda carga do BigQuery cair em K4 (fim > corte + folga) → nenhuma tabela carrega → 503 em todas as páginas. Depois da reunião, o portal também para de atualizar até alguém mudar a variável. |
| A2 | M | `app/congelamento.py:87-90` | K5 compara o `fim` das fichas gravadas; a 1ª tabela que congelar define a carga das outras. Se uma tabela falhar na carga do corte e só voltar na seguinte (fim maior), fica em K4 para sempre e a página dela fica 503/atrasada. |
| A3 | M | `app/congelamento.py:18`, `entrada/calculos.py:149`, `app/sla.py:24` | O corte **não filtra linhas** (decisão registrada). No caminho B do roteiro (carga de 02/11, fim 01/11), a Demanda mostra "até 1 de novembro" e novembro parcial com os pedidos de 01/11. Mesmo no caminho A, `mes_parcial` (`sla.py:24`) = mês do `_processado_em` = **novembro** e outubro passa a mês completo: conferir se todas as telas (Demanda E3/E4, SLA C7 e A2, estudo, Previsão P10) tratam igual um mês vigente com zero ou quase zero dados. |
| A4 | M | `app/congelamento.py:152-153`; `docs/congelar_outubro.md`, passo 2 | Ficha sem `modificada_em` faz a tabela nascer com `modified = agora` (muda a cada subida). E o roteiro diz que o servidor da 8400 "também congela sozinho em até 5 min" enquanto `tools/congelar_base.py` grava a mesma pasta: conferir que duas gravações simultâneas (troca atômica por arquivo, mas não do conjunto parquet + ficha) não deixem ficha e parquet de cargas diferentes. |
| A5 | M | `app/sla.py:14-25` | `mes_parcial` guarda **um** valor global (`_cache`) sem trava, chaveado pela versão da carga. Com o aquecimento de uma carga nova em segundo plano e a requisição na carga antiga, duas threads podem alternar e uma ler o mês da outra (só importa na virada do mês). |
| A6 | M | `app/corte.py:36-51`, `entrada/calculos.py:117-123`, `app/sla.py:28-34`, `ml/dados.py` (`SQL_FIM`) | A regra E3 tem **quatro implementações** (Python em três lugares e SQL no ML). Mesma regra hoje, risco de divergir. |
| A7 | M | `entrada/calculos.py:88-98` × `sla/calculos.py:279-288` × `formato.py:22-23` | Três maneiras de arredondar: `_pcts` inteiro (Demanda), `_pcts` com floats (SLA), `formato.pct` com `format()` (arredondamento do Python, não "meio para cima"; usado na LIA e em textos). Pode dar ±1 ponto entre telas para o mesmo número. |
| A8 | B | `talentos/calculos.py:107` | `round(100 * soma / total)` usa arredondamento bancário (0,5 → par), contra a regra do portal (meio para cima). |
| A9 | A | `ml/saida/previsao.json` × rodapé de `/previsao` | Na carga vigente a tela da Previsão diz "146 até 27/10" e "18 de 21 dias úteis", mas o rodapé diz "Dados até 29/10/2026" (vem da gold de entradas, `tabelas=("entrada",)`). Com `CONGELAR`/modo apresentação o job não roda (J5) e o acompanhamento fica velho **sem aviso**. O roteiro do corte manda refazer o retrato (outubro) na mesma carga, mas nada na página impede mostrar um `previsao.json` de outra carga que a base congelada (só o `congelar_base.py --conferir` checa). |
| A10 | M | `previsao/calculos.py:49-50` | `ANO = 2026` fixo (eixo e séries); na virada do ano a página não muda sozinha (PD22). |
| A11 | M | `apresentacao.py:457, 467, 481, 415` | LIA, vídeo, Iniciativas e Roadmap usam `tabelas=("entrada",)` só para o rodapé: a página da LIA diz "Dados até 29/10 · atualizados em 30/10 09:01", mas os números vêm do retrato extraído em 30/10 20:49 (janela até 29/10). Coincide hoje; o rodapé não descreve a fonte real. |
| A12 | M | `lia/__init__.py:351, 373, 381` | `pct_fora` = fora (soma das `horas`) ÷ total (soma dos `periodos`). Se o retrato tiver totais diferentes entre `horas` e `periodos` (reprocessamentos), o % sai com denominadores trocados. |
| A13 | M | `lia/__init__.py:113-114, 155, 353` | `max()`/`min()` sem padrão sobre listas que podem vir vazias (retrato sem dia útil, sem semana) → exceção não tratada → 500 (não é `DadosIndisponiveis`). |
| A14 | B | `lia/__init__.py:24` | `MINUTOS_TRIAGEM = 2` é premissa fixa no código (a tela diz "≈"; a ficha diz "a confirmar"). |
| A15 | B | `sla/calculos.py:98-130` | `_cache`/`_cache_status` de `entregas` sem trava (o estudo tem `_trava_estudo`); o laço de expulsão já trata a corrida com `pop(..., None)`, mas a leitura `_cache[chave]` pode falhar se outra thread expulsar entre o teste e a leitura. |

### 10.2 Ficha × código (documentação desatualizada)

| # | Sev. | Onde | Suspeita |
|---|---|---|---|
| A16 | M | `docs/paginas/lia.md:3-11, 554-561`; `CLAUDE.md:18` | Ficha e `CLAUDE.md` ainda descrevem o extrato da semana (`lia.js`, `?semana=NN` abre o extrato). O código diz que foi retirado (`lia/__init__.py:5, 369`) e não existe `app/static/lia.js`. |
| A17 | M | `CLAUDE.md:17-18` × `docs/paginas/lia.md` × tela | `CLAUDE.md` diz "54% fora do expediente"; a tela mostra **50%** (definição da LIA, almoço dentro). |
| A18 | M | `docs/paginas/sla.md:3` e `:133` | Topo diz "SLA → Previsão" (navegação de 28/10 do original); na V2 a sequência é SLA → LIA. A linha 133 diz que o slide 5 termina com "Voltar ao SLA →" e "ou seguir para a próxima: LIA →", que a linha 82 diz terem saído da tela. |
| A19 | B | `docs/paginas/sla.md` (tabela "Estado vigente", linha C3c) | Cita `expediente.dias_uteis_fracao`, que não existe em `app/expediente.py` (o valor vem pronto da gold, `dias_uteis_fr`). A linha C2 ainda diz "recalculadas em `app/expediente.py` até a v2 da gold". |
| A20 | M | `docs/paginas/talentos.md:195-206`; `docs/paginas/previsao.md:7` | SQL de reprodução cita `app/sql/talentos_ano.sql` e `talentos_top.sql` (movidos para `_descartados/` na D57); a Previsão diz "Mercado exclusivos … (silver 2026, critério de `talentos_ano.sql`)", mas `ml/dados.py:15` lê a view gold de exclusividade. |
| A21 | M | `pendencias.py:35-42, 98-99, 109-112` | PD01, PD02a ("hoje a dica lê a silver") e PD21 ("o site recalcula") descrevem o estado anterior à D57; PD24 cita `TAB_TALENTO_ORIGEM` e `app/sql/talentos_ano.sql`, que não existem mais. O 3º pedido de `PEDIDOS` ("Levar a exclusividade para a base de entradas") também já foi feito. Isso aparece na página "O que falta". |
| A22 | B | `docs/paginas/README.md:52-66, 76` | Índice das fichas não lista as fichas da V2 (capa, roadmap, lia, lia-na-pratica, iniciativas, encerramento) e cita `tools/auditar_relatorio.py` e `tools/conferir_expediente.py`, que foram para `_descartados/`. |
| A23 | B | `cola.py:20-22` | `IDS` mantém `atendimento`, `estudo-2-1..3`, `estudo-6..8` do estudo antigo; na V2 a cola não é usada (`SINC=off`), mas o endpoint `/cola/{ficha}` ainda responde por esses ids se `SINC` estiver ligado. |
| A24 | B | `apresentacao.py:1-5`; `__init__.py:90-91` | Docstrings ainda descrevem a ordem antiga (Início → … → Resultado → Qualidade → "O que falta"). |
| A25 | B | `iniciativas/repositorio.py:14-16` × `docs/deploy_iniciativas.md:143-151` | Docstring fala em "máx. 2 instâncias"; o roteiro usa `--max-instances=1`. |
| A26 | B | `previsao/job.py:3-5` × `:20` | J1 diz "mês anterior ao do dia seguinte a MAX(data)"; J6 (e o código) usa a E3. |
| A27 | B | `CLAUDE.md:22` | "550 testes"; hoje são 564. Várias partes do `CLAUDE.md` da V2 (abaixo de "O texto abaixo é o guia herdado") falam da porta 8100, 475/498 testes e do estudo de 7–8 slides. |

### 10.3 Segurança e robustez

| # | Sev. | Onde | Suspeita |
|---|---|---|---|
| A28 | A | `app/iap.py:335-339` | Quando o cache das chaves vence (1 h) e a busca em `gstatic.com` falha, `chaves()` levanta exceção e **não reaproveita as chaves antigas**; `verificar` devolve `None` → **401 para todos** até a rede voltar. Na reunião, um soluço de rede derruba o portal. |
| A29 | M | `main.py:157-164`, `main.py:288-295` | Com `AUTH=iap`, `/saude` também exige o JWT: sondas de saúde ou monitoramento sem passar pelo IAP recebem 401. |
| A30 | M | `iniciativas/api.py:201-214` | O limite de 10 MB só é checado antes do parse se houver `Content-Length`; num envio `chunked` sem o cabeçalho, o Starlette lê e grava o arquivo inteiro antes do `f.read(MAX_ANEXO + 1)`. Risco de disco/memória com upload grande (atenuado: só quem passa pelo IAP e com a edição ligada). |
| A31 | B | `iniciativas/api.py:106-108` | A comparação `Origin` × `Host` depende do `Host` que chega ao app; atrás de domínio próprio ou balanceador com `Host` reescrito, toda escrita pode virar 403. Com o IAP direto no Cloud Run, deve funcionar. |
| A32 | M | `main.py:271-286` | `POST /sinc` não confere `Origin` (o GET também não precisa): qualquer página aberta no mesmo navegador do computador pode trocar a página do portal local enquanto `SINC` estiver ligado (padrão `on` em `config.py:69` se a variável não for passada; a V2 depende de subir com `SINC=off`). |
| A33 | B | `app/static/roadmap_proto/` | Protótipos (`a`, `a_v1`, `b`) com HTML/JS/CSS próprios continuam em `static/`, entram na imagem e são servidos (dentro do IAP). Não são usados pelas páginas. |
| A34 | M | `docs/paginas/talentos.md`, slide 1 do estudo | Nomes de talentos e um orçamento real (marca, talento, projeto) aparecem na tela; com a publicação pelo IAP, avaliar se o público autorizado pode ver (decisão de 24/10 era para a reunião local). |
| A35 | B | `main.py:301, 324` | `/cola/{ficha}` testa `not config.SINC or config.EM_PRODUCAO`, mas `SINC` já é `False` em produção (redundante); e responde `"congelada": config.CONGELAR`, que não reflete o congelamento da D65 (`dados.base_congelada`). |

### 10.4 Desempenho

| # | Sev. | Onde | Suspeita |
|---|---|---|---|
| A36 | M | `dados.py` (`em_fundo=not config.EM_PRODUCAO`, 293-333) | Em produção, sem a base congelada, a cada `RECARGA_MIN` a 1ª requisição espera o `get_table` e, se mudou, a carga inteira + aquecimento do estudo (3 grupos) **na própria requisição**. Com a base congelada na imagem (D65) isso some nesta reunião; volta ao descongelar. |
| A37 | M | `app/static/apresentacao.js:30-44`, `main.py:197` | Cada aba aberta baixa a página inteira a cada 5 min para comparar `relatorio-versao`; em páginas pesadas (estudo, Previsão) é uma renderização completa por aba. Com a base congelada, a versão nunca muda: tráfego inútil. |
| A38 | M | `main.py:183, 211-226` | Speculation Rules agora com `prerender` **imediato** das vizinhas e do ✕ e `prefetch` imediato dos 6 destinos do Roadmap e do link do estudo: cada página aberta gera de 2 a 3 renderizações extras no servidor (o Roadmap, mais 6 downloads), mesmo que a pessoa não avance. No Cloud Run com `--max-instances=1` e 1 worker, isso disputa CPU com a página atual e, atrás do IAP, cada pré-carga passa pela verificação do JWT. Conferir também se o `Cache-Control: private, no-store` das páginas não faz o Chrome descartar o `prefetch`. |
| A39 | M | `main.py:98-136` | Na subida, `ao_iniciar` monta todas as seções, inclusive as ocultas (Atendimento, Qualidade), e agora também `_aquecer_paginas` (todos os templates + o estudo); no Cloud Run com `--min-instances=0`, a 1ª visita espera esse arranque frio completo. |
| A40 | B | `lia/__init__.py:343-344`; `iniciativas/__init__.py:30-31` | LIA relê e decodifica o JSON a cada página (só `padroes` tem cache); Iniciativas lê todo o quadro e os anexos do backend a cada página (no Firestore, 2 consultas por visita). |
| A41 | B | `main.py:63-73` | `_hash_estaticos` lê todos os bytes de `static/` (inclui `fluxo-processo-alta.webp`, protótipos e futuro vídeo MP4) na subida; com o vídeo, isso cresce. |

### 10.5 Outros

| # | Sev. | Onde | Suspeita |
|---|---|---|---|
| A42 | B | `templates/macros.html:59` | Lista fixa de slugs sem abas (`talentos, sla, iniciativas, previsao, lia, roadmap`); página nova entra com abas sem querer. |
| A43 | B | `apresentacao.py:42-48` (`capa["medida"]`); `main.py:377` | `medida_capa` ainda roda o cálculo do SLA a cada visita à capa para um número que a capa V2 não mostra; `etapas` da jornada sem uso. |
| A44 | B | `docs/deploy_iniciativas.md:270-273` × `Dockerfile:17-20` | O roteiro de deploy ainda diz que `previsao.json` "não vai para a imagem"; desde a D65 o `Dockerfile` copia o arquivo (e o build falha sem ele). |
| A45 | B | `apresentacao.py:87-110` | `_guardado` devolve o **mesmo objeto** a todas as requisições (Talentos devolve o dict guardado direto; a Demanda faz cópia rasa). Um template ou filtro que altere uma lista aninhada contaminaria o cache. O cache também segura até 40 entradas com referência aos DataFrames de cargas antigas (memória). |

---

## 11. Releitura final (agentes em paralelo)

Arquivos relidos no fim deste trabalho, em 31/10/2026, por estarem sendo alterados por outros agentes: `app/config.py`,
`app/dados.py`, `app/main.py`, `app/congelamento.py`, `app/templates/encerramento.html`, `docs/congelar_outubro.md`,
`docs/PRD.md`. O registro do que mudou entre a leitura e a releitura está no fim desta seção.

| Arquivo | Na 1ª leitura | Na releitura (31/10/2026, ~03:05) | Efeito neste PRD |
|---|---|---|---|
| `app/config.py` | sem corte | `CORTE_DADOS`, `CORTE_FOLGA_DIAS`, `BASE_CONGELADA_DIR` (D65) | seções 2.3, 5.3, 5.4; A1 |
| `app/dados.py` | recarga pelo metadado | decisão de corte por carga, leitura da base em arquivo, `base_congelada()`, `processado_em` guardado | 2.3, 5.3, 7; números de linha |
| `app/congelamento.py` | não existia | K1–K7 | 5.3; A1–A4 |
| `app/main.py` | — | carregador de templates conferido a cada 2 s, versão dos estáticos em segundo plano, `_aquecer_paginas`, Speculation Rules imediatas, rodapé pela `dados.base_congelada` | 2.4, 7; A35, A38, A39; números de linha |
| `app/apresentacoes/gestao_orcamentos/apresentacao.py` | — | cache de telas `_guardado` | 7; A45; números de linha |
| `app/apresentacoes/gestao_orcamentos/roadmap/__init__.py` | — | tamanho das imagens pelo cabeçalho | 7 |
| `Dockerfile` | só `COPY app/` | também `COPY ml/saida/previsao.json` | 2.6, 9.3; A44 |
| `docs/congelar_outubro.md` | não existia | roteiro completo (caminhos A/B, passos 0–6, descongelar) | 5.3, 5.4 |
| `docs/PRD.md` | topo de 28/10 | bloco D65 no topo, item no "Como o portal funciona" e D65 na tabela de decisões; **sem seção de desempenho** | 7 marcada "parcialmente a completar" |
| `app/templates/encerramento.html` | 02:38 | sem mudança depois disso | 3.11 confere com o template |
| `tests/` | 553 + `test_corte.py` | 564 coletados | 8.2 |

Os números da seção 3 são da carga de 30/10/2026; com a carga do corte (dados até 31/10 ou 01/11), eles mudam e as fichas
devem ganhar o novo "Retrato da carga" (roteiro do corte, passo 3).
