# PPD-AGENCIAMENTO-SLA-V2 — guia para retomar

**03/11/2026 (D67) — ler primeiro: [PRD_V2, seção 0.6](docs/PRD_V2.md).** Base **congelada da carga de 03/11** (dados
até 02/11; a de 02/11 foi trocada antes de congelar), com `CORTE_FOLGA_DIAS` padrão **2** e `ARG CORTE_DADOS=2026-10-31`
no `Dockerfile`; Previsão de outubro e LIA até 31/10; `checar_reuniao.py` TUDO CERTO. Iniciativas com MIA e Raio-X
(Firestore de produção a atualizar pela tela), vídeo da LIA no ar, Roadmap sem desfoque e com o Raio-X. Falta o Caio
publicar (Cloud Run `-Congelado`, VPS). 635 testes. Os parágrafos de 31/10 abaixo são histórico.

**Publicação de 31/10/2026 (D66/D66b) — ler primeiro: [PRD_V2, seção 0](docs/PRD_V2.md).** No Cloud Run:
`viu-agenciamento` (AUTH=publico, só leitura) e `viu-agenciamento-restrito` (IAP, 4 e-mails, edição), os dois no ar
e trancados (a org barrou o link aberto; a TI precisa liberar os e-mails no IAP). Espelho temporário na VPS do Caio
(EasyPanel `rede-globo`, `Dockerfile.vps`, ramo `vps` do GitHub `CBarrosoBRRJ/PORTAL-DADOS-VIU`; sem credencial,
link com `?k=`). Corte desligado até a carga de 02/11 (`CORTE_DADOS=off` no deploy e `ARG` no Dockerfile); na segunda,
`docs/congelar_outubro.md` + `tools/publicar*.ps1 -Congelado`. Git: o projeto agora tem repositório (dados fora).

**Endereço novo (Caio, 31/10/2026):** a área saiu de `/gestao-orcamentos/...` para `/viu-agenciamento/...` (mesmos nomes
de página). O slug fica em `app/apresentacoes/gestao_orcamentos/__init__.py` (`SLUG`; a pasta não mudou) e as rotas,
links do Roadmap, API das Iniciativas e `data-ini-api` derivam dele. Endereço antigo: um redirecionamento genérico em
`app/main.py` (`endereco_antigo_area`: GET/HEAD 301, demais métodos 308, com a query). A aba do navegador mostra só
"ViU Agenciamento" em todas as páginas. Teste: `tests/test_rotas.py::test_endereco_antigo_da_area_redireciona_para_viu_agenciamento`.

**Desempenho da troca de página (31/10/2026; auditoria F14, F15, F18, F20):** contas de cada tela guardadas por carga
em `apresentacao.py` (`_guardado`: cópia a cada requisição; chave = carga + parâmetros + corte/congelamento/modo; carga
nova descarta a antiga; `limpar_caches()` único, usado nos testes); estudo, Demanda e Talentos não refazem pandas a
cada clique; templates e estudo aquecidos ao subir (só as seções visíveis); pré-carga só da próxima página (`rel=next`,
immediate) e o resto por hover; sem sondagem de HTML com base congelada ou em produção; hash dos estáticos por data e
tamanho. Produção: `--min-instances=1 --cpu-boost` (`docs/deploy_iniciativas.md`). Números antes × depois no PRD
("Desempenho da troca de página"); registro em `docs/auditoria/correcoes_2026-10-31.md`; testes em
`tests/test_desempenho.py`. Mudou uma regra que entra no resultado de uma tela? Ponha na chave (`_ambiente_calculo`).

**Dados congelados em 31/10/2026 para a reunião de 04/11 (D65, 31/10/2026). Ler antes de mexer em dados:** o
`CORTE_DADOS=2026-10-31` vem ligado por padrão (`app/config.py`), no computador e em produção. O portal aceita cargas
até a 1ª com dados até 31/10 (ou 01/11, pela folga de 1 dia) e então congela. A base fica gravada em
`app/base_congelada/` **como unidade** (auditoria de 31/10, F01/F02/F07/F08: pasta de versão `v-…` com um parquet por
tabela + `manifesto.json` publicado por último, trava entre processos, persistida só depois de conferida; regras K1–K7 e
B1–B5 em `app/congelamento.py`) e nenhuma carga a troca depois. Com a base válida, nem o BigQuery é consultado; no Cloud
Run ela vai na imagem, o build a exige (`RUN python -m app.conferir_base`, que também reprova Previsão de outra carga e
LIA fora do corte) e o arranque também. O `Dockerfile` copia `ml/saida/previsao.json`. A Previsão da reunião é o retrato de outubro (`ml.rodar --rotina`); a LIA vai até 31/10. 31/10
é sábado e a gold só roda seg–sex: **o Caio escolheu (31/10) o caminho B**, a carga agendada de seg 02/11 (dados até
01/11, pela folga; rodapé "Dados até 01/11/2026"), com base, Previsão e LIA (`--fim 2026-10-31`) na segunda.
Roteiro do dia 01/11, deploy e como descongelar (`CORTE_DADOS=off`): `docs/congelar_outubro.md`. Ferramenta:
`tools/congelar_base.py` (`--conferir` sem BigQuery; `--recuperar` para gravação interrompida). Testes do corte:
`tests/test_corte.py` (e `tests/test_auditoria_dados.py` para F03/F05/F10/F13). Os testes rodam com
`CORTE_DADOS=off` e numa pasta temporária (`tests/conftest.py`). **Não apagar nem regravar `app/base_congelada/` sem
pedido do Caio.**

**Cópia de trabalho, 30/10/2026:** cópia do portal `../PPD-AGENCIAMENTO-SLA` (sem `_congelado`, `_descartados`,
`_entregas`) para as edições novas do Caio. Roda na porta **8400** (<http://127.0.0.1:8400/viu-agenciamento/capa>),
com `SINC=off` (a cola da 8200 segue só o original). O original (8100) e a cola (8200) continuam congelados.
**V2, mudanças de 30/10/2026 (Caio):** capa "ViU *Agenciamento*" (sobretítulo "Relatório da área"), com o
subtítulo "Tudo o que a área analisa, constrói e entrega, num só lugar." no lado branco; no plano marinho, no lugar do
menu dos temas (saiu; o Roadmap navega), só a ilustração "dados → área" e o "Começar" amarelo para o Roadmap (ficha
`docs/paginas/capa.md`); itens brancos correm das pontas e viram amarelos na linha única (loop autorizado pelo Caio só
na capa; **botão de pausa retirado por decisão do Caio em 30/10/2026; animação contínua; respeita movimento
reduzido**; SMIL no SVG, `static/capa_fluxo.js` para com a aba oculta); botão "Capa" no navegador.
Sequência: Capa → **Roadmap** (`antes_do_inicio`; "Como chegamos até aqui?", selo Gerencial, sem abas, ✕ leva à capa; HUB da reunião, 5ª versão de 31/10, "linha do tempo linear em Y" num painel flutuante: 01 Dados espalhados (7 chips coloridos) → 02 Mapeamos → Y (04 Pedido à TI ┄ Aguardando ┄ 05 Infraestrutura liberada; 03 Criação de dashboards embaixo) → 06 BigQuery → dois trilhos contínuos até a borda (07 Análises e estudos, "Você está aqui", com os botões por categoria: Análises = Demanda, Talentos, SLA; Automação e IA = LIA, Iniciativas; Projeções = Previsão; 08 Novos dashboards e melhorias), retroalimentação pontilhada; só número + título por nó, centrados no eixo do nó; miniaturas abrem no <dialog> (galeria ← →); posições e pulso calculados em roadmap/__init__.py e passados pelo <style> com nonce; ícones com gesto próprio e anel quando o pulso passa; movimento contínuo só sem movimento reduzido (exceção em tests/test_movimento.py); versões anteriores em _descartados/2026-10-31/roadmap_v4/, roadmap_v3/, roadmap_colorido/ e _descartados/2026-10-30/roadmap_diagonal/; ficha `docs/paginas/roadmap.md`) → Demanda → Talentos → SLA → **LIA** →
**Iniciativas** → Previsão (última) → **Encerramento** (31/10/2026, Caio, 3ª rodada: marinho com faixa branca no topo com o logo, "Obrigado." com fio amarelo, "Voltar ao início" amarelo para a capa e, no canto inferior direito, o mascote balão de conversa que acena, pisca e flutua sem parar (loops SMIL contínuos; `static/fim.js` os começa e só para com aba oculta e movimento reduzido); ficha `docs/paginas/encerramento.md`; versões e variações em `_descartados/2026-10-31/encerramento_antes/`). **Atendimento fora** (`oculta=True`; código e endereço mantidos).
Páginas novas a partir dos PRDs de @cris (fichas em `docs/paginas/`: `roadmap`, `iniciativas`, `lia`,
`lia-na-pratica`). A LIA lê `lia/retrato.json`, agregado do Cloud Storage da LIA por `tools/extrair_lia.py` (só leitura;
exceção à D57); o 1º período diverge do PRD (ver a ficha). LIA **entregue (Caio, 30/10/2026)**, em uma tela só (D-LIA-2 a D-LIA-4, 30/10 noite; estado final no topo de `docs/paginas/lia.md`): 2.047
lidos, 87% resolvidos sozinha, fração não lead/lead/validação, triagem poupada estimada (`MINUTOS_TRIAGEM` = 2, premissa a
confirmar), 54% fora do expediente, semanas ISO com extrato ao clicar (`lia.js`, `?semana=NN`) gráfico no padrão de Demanda/SLA; à esquerda, sob 2.047/87%, "O que a LIA tirou das mãos da equipe" (painel lavanda) e "Quando o inbound chega" (cartão flutuante; leads, não leads e validação em quadrantes dentro × fora do expediente — expediente da LIA 10h–19h com almoço dentro; fora 50%; dia da semana só na ficha); cores do portal; prévia do vídeo em miniatura; **página mais limpa (Caio, 30/10):** sem a frase "De … a …, a LIA leu" (período no título do gráfico), sem legendas sob a fração, nota de 12/10, leituras de dia/período e nota do gráfico (tudo na ficha); o
**Vídeo** virou pop-up da LIA (`lia_video.js`; página `lia-na-pratica` oculta, arquivos em `app/static/video/`); a
análise de tempo na régua do SLA (D-LIA-1, Inbound sem ganho robusto) ficou só na ficha; versão antiga em
`_descartados/2026-10-30/`. 505 testes (`tests/test_v2_paginas.py` novo).
**Iniciativas com dados no servidor (31/10/2026, Caio e gerente):** criar, editar, mover, excluir e anexar ficam no servidor (valem para todos, sobrevivem a recarregar). Computador: SQLite **fora do Drive** em `C:/Users/CCMB/.ppd-agenciamento-v2/iniciativas.db` + `anexos/` (`INICIATIVAS_DB`, `INICIATIVAS_ANEXOS`); Cloud Run: Firestore + bucket privado (`INICIATIVAS_BACKEND=firestore`, `INICIATIVAS_BUCKET`). `catalogo.py` = semente. API em `/viu-agenciamento/iniciativas/api` (escrita com `X-Requested-With: iniciativas`; em produção só com `INICIATIVAS_EDICAO=on`, e isso só atrás do IAP). Galeria, visor e "Expandir"; layout ocupa a lâmina; sem loop (linhas de fundo retiradas pelo Caio). `AUTH=iap` (`app/iap.py`) = exceção temporária à D10 para a reunião do gerente, **a aprovar pelo Caio**. Backup: `python tools/iniciativas_admin.py backup`. Deploy (nada executado): `docs/deploy_iniciativas.md`. Ficha: topo de `docs/paginas/iniciativas.md`. 550 testes.
**Estudo "Como medimos" na V2 (30/10/2026, Caio): 5 slides** — 2 num passo só (faixas + típico × média, X10), 3 e 4
unidos (quantidade × tempo, V9/V10), conclusão retirada; o 5 ("Onde o tempo trava?") é o último e sai para o SLA ou a
LIA. Detalhe e números no topo de `docs/paginas/sla.md`; sobras em `_descartados/2026-10-30/`.
O texto abaixo é o guia herdado do original.

**Congelado para apresentar, 29/10/2026:** portal (8100) e cola (8200) validados pelo Caio; cópia em
`_congelado/2026-10-29_reuniao/` (LEIAME lá). Não mexer sem pedido. Estudo com 7 slides (D64: tipo de pedido fora,
`ESTUDO_TIPO` em `apresentacao.py`); falas da cola sem veredito (a diretoria conclui). 498 testes.
Deck temporário à parte: `../PPD-FECHAMENTO-INTERVENIENCIA` (porta 8300, fechamentos de interveniência; cópias dos
estáticos deste portal; descartável, README lá).

**Cola dinâmica, 28/10/2026:** `/cola/{ficha}` fornece falas agregadas pelo módulo `gestao_orcamentos/cola.py`, reutilizando os contextos das páginas. A cola na porta 8200 consulta ao abrir e a cada 60 s, sem números fixos. Recorte Todos explícito; segue cache/base congelada do portal; previsão segue o retrato publicado. Falhas ocultam valores. Endpoint só com SINC, fora de produção.

**Navegação, 28/10/2026:** o gancho e as setas principais seguem SLA → Previsão. O estudo fica opcional pelo botão Estudo; ao abri-lo, continuam disponíveis os slides, a volta ao SLA e a saída para Previsão.

## Estado atual (27/10/2026, D57) — ler primeiro

**D57 (27/10/2026): o site só lê a gold.** Cada gráfico lê a sua tabela ou view do `gold_monday` (8 tabelas + 8 views do
projeto irmão); sem silver, sem `app/sql/`, sem expediente recalculado no site. Código antigo × novo na mesma carga real:
0 diferenças. Mapa página × gráfico × tabela no PRD ("Retrato do código"). Limpeza em `_descartados/2026-10-27/LEIAME.md`;
revisões e auditorias externas em `docs/historico/`.


Portal **"Gestão de orçamentos"** pronto para a reunião de diretoria de **28/10/2026** (apresentação local, `MODO=apresentacao`;
nada publicado). A batalha do portal de 26/10 (D49) revisou todas as páginas em três levas (textos e cálculos; interface e
movimento; documentação e limpeza) **sem mudar regra de negócio**.

- **Antes da reunião (27/10 e manhã de 28/10):** `python -m ml.rodar --acompanhamento`; subir o servidor com
  `MODO=apresentacao`, sem `--reload` (base congelada, job da Previsão parado); `python tools/checar_reuniao.py` (precisa
  das credenciais do gcloud-viu e do servidor no ar; grava `docs/validacao/reuniao_AAAA-MM-DD.json`). Em 26/10, carga das
  09:01: **tudo certo**. Se a carga mudar, trocar o "Retrato da carga da reunião" no topo de cada ficha.
- **Regras que mais se confundem com as antigas:** meta do SLA = **metade dos orçamentos prontos em até 2 dias de trabalho
  (16 h)** (D38; a "75% em até 3 dias" da D37 foi revista), mês do SLA = mês da 1ª entrega, prazo do cliente em dias
  úteis no calendário (C3b), "típico" = mediana; Previsão com janela de 12 meses, teste jun–set/2026, menor WAPE e
  execução mensal (D48; a D47 é histórico).
- **Decisões abertas do Caio** (16, com a opção recomendada e onde mexer): PRD, seção 9.7. Não aplicar sem o aval dele.
- **Onde está cada coisa:** estado e decisões no [PRD](docs/PRD.md) (topo, seção 8 e 9.7); linha do tempo de 21–26/10 em
  [docs/HISTORICO_2026-10.md](docs/HISTORICO_2026-10.md); por página, o topo de cada ficha em [docs/paginas/](docs/paginas/README.md)
  ("Retrato da carga da reunião" ou, no SLA, "Estado vigente"); sobras movidas em `_descartados/<data>/LEIAME.md`.
- **Testes:** `python -m pytest tests -q` no venv (475 em 27/10/2026; as views da gold simuladas em `tests/gold_simulada.py`).
  **Servidor local:** porta **8100**.

Os blocos "Último ajuste / Ajuste anterior" que ficavam aqui (D33 a D49) estão resumidos no histórico da etapa; os blocos
equivalentes do PRD estão na seção 12 dele; a cópia literal deste arquivo está em `_descartados/2026-10-26/versoes_anteriores/`.

Leia este arquivo primeiro. Detalhes no [PRD](docs/PRD.md); não releia tudo se a tarefa não pedir.

## O que é

Site interno de relatórios do board **Backlog 2026 | Agenciamento** (Cloud Run + FastAPI), lendo **só** as tabelas e
views gold do projeto irmão `../PPD-GOLDEN-AGENCIAMENTO-MONDAY` (dataset `gold_monday`; uma variável `TAB_*` por fonte em
`app/config.py`, um objeto por fonte em `app/dados.py`). Cresce por páginas. Controle de acesso próprio: link por e-mail, domínios permitidos,
sessão de 30 dias, tela de admin. Responsável e admin: Caio Barroso (`caio.barroso@viu.com.br`, GCP
`gglobo-viu-dados-hdg-prd`).

## Estado por página (26/10/2026, D49)

| Item | Estado |
|---|---|
| Decisões de arquitetura e acesso | ✅ D1–D12 no PRD |
| GCP | ✅ permissões, APIs e deploy de teste; ⏳ G4 (serviço aberto à internet) |
| Início | ✅ **ENTREGUE (D28, 23/10)**; carga de 26/10: 5.556 até 25/10, +89% sobre 2025; Q1/Q2 em ordem. Ficha [inicio.md](docs/paginas/inicio.md) |
| Talentos | ✅ **ENTREGUE (D31, 24/10)**; 3.451 / 1.980 / 125 = 5.556; golds `..._talentos_ano` e `..._talentos_ranking` (D57). Ficha [talentos.md](docs/paginas/talentos.md) |
| Atendimento | ✅ **ENTREGUE (D33, 24/10)**; D58/D58b (27/10): "Declinados (Não teve seguimento)", "Entregues no Mês"; % = Entregues no Mês ÷ Para atender (set 661 ÷ 834 = 79%), objetivo 100%, alerta 90%; faixa só com o % de cada número sobre os recebidos (80 · 17 · 3 de 5.598), sem selo. Ficha [atendimento.md](docs/paginas/atendimento.md), seção 000 |
| SLA de entrega | ✅ **Pronta · meta a oficializar** (D34–D38, D49): típico 14 / 12 / 20 h, 2 / 1 / 2 dias úteis, 56% em até 2 dias de trabalho (jan–set, 2.347 orçamentos medidos). Horas sem almoço da gold (R24 e view `..._sla_entregas`, D57). Ficha [sla.md](docs/paginas/sla.md) |
| Estudo "Como medimos" | ✅ 8 slides (D34–D46), conferido no BigQuery por `tools/conferir_estudo.py` (26/10: tudo bate) |
| Previsão de demanda | ✅ **Pronta · 2 decisões abertas** (D48, D55): retrato de setembro, Inbound 138/mês, Mercado 464 · 517 · 588; D55: tela só com os dois gráficos (sem painel lateral e sem "Regras e modelos"; documentação só na ficha/PRD), Inbound não exclusivo = "Não se aplica" (PD24), AutoTS na régua não venceu (`ml/modelos/automatico.py`); job mensal local (`ml/`), em produção ainda não (PD23). Ficha [previsao.md](docs/paginas/previsao.md) |
| Resultado | máscara; **oculta da navegação** (D59, `oculta=True`; endereço e código mantidos) |
| Qualidade | máscara com texto para o público; **oculta da navegação** (D59); a fazer depois da reunião |
| Navegação (D59–D61, 27/10) | `/` abre na **capa** (desenho de referência do Caio: jornada animada de um pedido, frase da etapa em roleta, relógio para no típico do SLA; `static/capa.js`); sequência Capa → Demanda (antiga "Início") → Talentos → Atendimento → SLA → Previsão → **Encerramento** (marinho, "Obrigado."); capa e encerramento **sem aba** (setas, gancho, logo); gancho visível para a próxima página; setas → / ← trocam de página (no estudo, de slide); capas de seção **desligadas** (`CAPAS_SECAO` guardado em apresentacao.py); **cola do apresentador** à parte em `../PPD-AGENCIAMENTO-COLA`, porta 8200, **sincronizada** com o portal pelo `/sinc` (D62, `static/sinc.js`; só no computador, `SINC=off` desliga); sem menu lateral (`MENU_LATERAL=on` traz de volta); tela cheia mantida ao navegar (quadro em tela cheia, `frame-ancestors 'self'`) |
| O que falta | ✅ gerada de `pendencias.py` (PD01–PD23 e 4 pedidos); ficha conferida por `tests/test_documentacao.py` |
| Publicação | nada publicado |

**Fichas por página (rastreabilidade):** [docs/paginas/](docs/paginas/README.md) — pergunta, textos da tela, regras, memória de cálculo, SQL para reproduzir, validações e limites; glossário das telas no README das fichas.
**Lembretes para a gold:** [docs/lembretes_gold.md](docs/lembretes_gold.md). **Dados que faltam (para a gold):** [docs/prompt_dados_pendentes.md](docs/prompt_dados_pendentes.md) — **rascunho**, códigos iguais a `pendencias.py`.
**Conferências (só leitura):** `tools/checar_reuniao.py` (passo único antes de apresentar), `tools/conferir_estudo.py` (estudo do SLA nos 3 grupos, por caminho independente), `tools/auditar_modelos.py` (métricas dos backtests salvos), `node tools/conferir_layout.mjs [--movimento]` (layout em 4 telas e movimento). Checagem diária do Início: Q1/Q2 da [ficha, seção 6.4](docs/paginas/inicio.md) (também dentro do `checar_reuniao.py`).
**Histórico de revisões e auditorias externas:** [docs/historico/](docs/historico/) (revisões de 22–24/10, auditoria e plano de golds do Codex de 26/10, validações e evidências antigas). São registro: o estado atual está no PRD.

## Fases

| Fase | Entrega | Situação |
|---|---|---|
| 0 | Desenho, PRD, custo inicial | ✅ |
| 1 | Esqueleto local: layout, menu automático, carga da tabela em memória com recarga, página Visão geral de SLA | ✅ 21/10/2026 |
| 2 | Controle de acesso completo local (envio simulado) + tela de admin + testes | ⏳ próxima |
| 3 | GCP (o Caio roda): dataset `app_relatorios`, conta de serviço, segredos, teste G4, 1º deploy | |
| 4 | Envio real pela caixa do Outlook | |
| 5 | Demais páginas de SLA; depois, novas tabelas gold | |

**Ao fim de cada fase:** reestimar o custo e registrar no PRD (seção 7.3).

## Como trabalhar aqui

1. **GCP corporativo: só consultas pelo Claude.** Criar/alterar recursos, permissões, segredos e deploy é com o Caio:
   comando pronto, um bloco por vez, explicado; aguardar a saída.
2. **Nunca publicar com `AUTH=off`** nem com o serviço aberto antes do controle de acesso (D10).
3. Números do site devem bater com consultas no BigQuery; conferir antes de dar uma página por pronta. Rodar
   `python -m pytest tests -q` (venv) a cada mudança em cálculo, rota ou template; regra nova = teste novo com os
   dados sintéticos de `tests/conftest.py`. Em produção (`K_SERVICE`) a recarga roda na própria requisição; no
   computador, em segundo plano.
4. **O site só lê a gold (D57).** Regras de negócio são da gold (fichas em `docs/tabelas/` do projeto irmão); o site só
   agrega e mostra. Gráfico novo que precise de regra nova = tabela ou view nova na gold, não SQL nem conta no site. A
   única leitura fora da gold é a sensibilidade de 2025 do ML (silver 2025, fora da tela). Mudou uma regra na gold?
   Mude também a simulação dela em `tests/gold_simulada.py`.
5. Sem LLM por API (D2). Segredos só no Secret Manager; o Claude nunca vê valores.
6. Ambiente local: venv fora do Drive em `C:\Users\CCMB\.venvs\ppd-agenciamento-sla`; credenciais ADC de
   `C:\Users\CCMB\AppData\Roaming\gcloud-viu` (`CLOUDSDK_CONFIG` e `GOOGLE_APPLICATION_CREDENTIALS`). Servidor local na
   porta **8100** (`--reload --reload-dir app`, `WATCHFILES_FORCE_POLLING=true`; comando no README).
7. Atualizar o PRD (estado atual no topo, decisões, custo, histórico), `docs/HISTORICO_2026-10.md` (ou o do mês) e
   este arquivo a cada fase ou leva. Este arquivo fica curto: estado atual + regras de trabalho; o resto vai para o PRD.
8. **Ficha da página sempre em dia:** mudou texto, regra, cálculo ou layout de uma página, atualize `docs/paginas/<pagina>.md` no mesmo trabalho (memória de cálculo com a carga datada, SQL, validação, histórico). Página nova = ficha nova. Número que vai à diretoria precisa estar na ficha e conferido no BigQuery.
9. **Rodapé datado** em toda página ("Dados até … · atualizados em …", `apresentacao.html`): não remover; página nova herda.
10. **Acessibilidade** em toda tela: controles nativos com nome; filtros só aplicam pelo botão (nada recarrega ao
   mudar um campo); texto pequeno ≥ 4,5:1; gráfico em HTML/CSS com texto para leitor de tela em cada mês/barra;
   link externo com `link_externo()`; status com ícone + texto, nunca só cor. Slide novo: cabe em 1440×900 e não
   rola para o lado em 390 px (conferir com captura). Nas fases 2+ (login, admin):
   erros ligados ao campo (`aria-describedby`, `aria-invalid`), mensagens de envio em `aria-live`, confirmação de
   bloqueio acessível pelo teclado.
11. **Nada se apaga** (o projeto não tem git): arquivo que perdeu o sentido vai para `_descartados/AAAA-MM-DD/`, mantendo as
   pastas, com uma linha no `LEIAME.md` de lá (origem e motivo); antes, confirmar por busca que nada ativo o referencia
   e rodar os testes depois. `ml/saida/d47/`, retratos e histórico da previsão ficam (rastreabilidade).
