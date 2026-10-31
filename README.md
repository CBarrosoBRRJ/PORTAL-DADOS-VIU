# PPD-AGENCIAMENTO-SLA

Site interno de relatórios do board Backlog 2026 | Agenciamento (Cloud Run + FastAPI), lendo as tabelas gold do
`PPD-GOLDEN-AGENCIAMENTO-MONDAY`. Hoje é o portal **"Gestão de orçamentos"** (Início, Talentos, Atendimento, SLA de
entrega com o estudo "Como medimos", Previsão de demanda, Resultado e Qualidade em máscara, "O que falta").
**Para retomar, comece pelo [CLAUDE.md](CLAUDE.md)**; o projeto inteiro está no [PRD](docs/PRD.md) (estado atual no topo,
arquitetura, acesso, custos, decisões) e a linha do tempo de 21–26/10/2026 em [docs/HISTORICO_2026-10.md](docs/HISTORICO_2026-10.md).

## Rodar no computador

```powershell
$env:CLOUDSDK_CONFIG = "C:\Users\CCMB\AppData\Roaming\gcloud-viu"
$env:GOOGLE_APPLICATION_CREDENTIALS = "$env:CLOUDSDK_CONFIG\application_default_credentials.json"
$env:AUTH = "off"   # só no computador; o site não sobe sem isso enquanto a fase 2 não existe
$env:WATCHFILES_FORCE_POLLING = "true"   # para o --reload perceber mudanças no Google Drive
C:\Users\CCMB\.venvs\ppd-agenciamento-sla\Scripts\python.exe -m uvicorn app.main:app --port 8100 --reload --reload-dir app
```

Venv (fora do Drive): `python -m venv C:\Users\CCMB\.venvs\ppd-agenciamento-sla` e
`...\Scripts\python.exe -m pip install -r requirements.txt`.

Abrir <http://127.0.0.1:8100/viu-agenciamento>. Porta 8100 porque a 8080, a 8081, a 8090 e a 8095 ficaram presas a
processos fantasmas do Windows (voltam a funcionar depois de reiniciar o computador). Antes de subir, conferir que não há
outro uvicorn deste projeto rodando: no Windows dois servidores conseguem ouvir a mesma porta e as conexões podem ir para
o antigo. Não confundir um preview congelado antigo (porta 8890) com o servidor do dia.

Filtro de talentos nas páginas que o têm (SLA, estudo, Previsão): `?talentos=todos|exclusivos|nao-exclusivos`; passo do
slide 2 do estudo: `?passo=1|2|3`.

## Modo apresentação (reunião de 28/10/2026)

Encerrar outros uvicorn deste projeto (`Get-Process python | Where-Object { $_.Path -like '*ppd-agenciamento-sla*' } | Stop-Process`,
conferindo antes a lista) e subir **sem `--reload`**, com `$env:MODO = "apresentacao"`:

- só as seções `na_reuniao` aparecem (Resultado fica fora; a Previsão leva à Qualidade), ou as de `$env:SECOES_VISIVEIS`;
- a base lida na subida fica **congelada** (`CONGELAR`; menu "base congelada para a apresentação", sem aviso de atraso;
  `$env:CONGELAR = "false"` desliga): carga nova só mostra "Há dados novos na base. Atualizar";
- o job da Previsão **não roda** (rodar o acompanhamento à mão antes de subir, abaixo);
- o exemplo do slide 1 do estudo pode ser fixado: `…/sla/como-medimos?exemplo=<projeto_id>#1` (só DEV ou apresentação).

Passo a passo na véspera (27/10) e na manhã de 28/10, no venv e com as credenciais acima:

```powershell
C:\Users\CCMB\.venvs\ppd-agenciamento-sla\Scripts\python.exe -m ml.rodar --acompanhamento   # realizado do mês na carga do dia
# subir o servidor em modo apresentação (bloco acima, sem --reload, com $env:MODO = "apresentacao")
C:\Users\CCMB\.venvs\ppd-agenciamento-sla\Scripts\python.exe tools\checar_reuniao.py          # saída 0 = tudo certo
node tools\conferir_layout.mjs http://127.0.0.1:8100                                          # layout: 8 slides × 3 grupos × 4 telas
```

`tools/checar_reuniao.py` (só SELECT, confere identidade e projeto antes de cada consulta) verifica: as três golds no mesmo
dia de carga; o site no ar com essa mesma carga e sem aviso de atraso; Q1/Q2 do Início; o estudo do SLA nos 3 grupos
(`tools/conferir_estudo.py`, `--sem-estudo` pula); a Previsão na mesma carga e com o retrato do último mês fechado. Grava o
registro em `docs/validacao/reuniao_AAAA-MM-DD.json` (e o do estudo em `docs/validacao/estudo_AAAA-MM-DD.json`). Se a
carga mudar, trocar o "Retrato da carga da reunião" no topo das fichas (`docs/paginas/`). Capturas de celular: usar a
emulação do `conferir_layout.mjs` (`--window-size` abaixo de ~500 px não serve no Chrome).

## Previsão de demanda (laboratório de ML, D48: execução mensal)

O site não depende das bibliotecas de ML: a página `/viu-agenciamento/previsao` só lê `ml/saida/previsao.json` (o
retrato do último mês fechado + o acompanhamento do mês em andamento). Protocolo D48: janela de 12 meses, teste
jun–set/2026, vence o menor erro (WAPE). O mês fecha pela regra E3 de `app/corte.py` (véspera do dia de processamento da
carga, em São Paulo), a mesma do site, do job e do ML. Comandos (no venv, com as credenciais acima):

```powershell
C:\Users\CCMB\.venvs\ppd-agenciamento-sla\Scripts\python.exe -m pip install -r requirements.txt -r requirements-ml.txt   # uma vez
C:\Users\CCMB\.venvs\ppd-agenciamento-sla\Scripts\python.exe -m ml.rodar --rotina                 # mensal: snapshot (BigQuery, só SELECT); se o mês fechado ainda não tem retrato, os 58 modelos + filtros + retrato (~9 min); senão, só o acompanhamento
C:\Users\CCMB\.venvs\ppd-agenciamento-sla\Scripts\python.exe -m ml.rodar --rotina --sem-extrair --forcar   # refaz o retrato com o snapshot de ml/dados
C:\Users\CCMB\.venvs\ppd-agenciamento-sla\Scripts\python.exe -m ml.rodar --acompanhamento         # só o realizado do mês em andamento (segundos; não recalcula a previsão)
C:\Users\CCMB\.venvs\ppd-agenciamento-sla\Scripts\python.exe -m ml.rodar --modulo neural --sem-juntar   # uma família (para rodar várias em paralelo)
C:\Users\CCMB\.venvs\ppd-agenciamento-sla\Scripts\python.exe -m ml.rodar --juntar                 # junta ml/saida/modelos/*.json, refaz os filtros e previsao.json
```

Com o servidor ligado (fora do modo apresentação), a carga que traz um mês fechado novo dispara `--rotina` sozinha, em
segundo plano; as demais cargas só disparam `--acompanhamento` (log em `ml/saida/rotina.log`; estado em
`ml/saida/rotina_estado.json`, com a falha visível na página; trava `ml/saida/rotina.lock`). Antes de gravar, o snapshot
passa pelo contrato `validar()`; com problema, nada é gravado. Cada retrato fica em `ml/saida/retratos/<mês>.json` e uma
linha em `ml/saida/historico_previsoes.jsonl` (PD09); a saída do protocolo antigo está em `ml/saida/d47/`.
`$env:PREVISAO_JOB = "off"` desliga o disparo. Em produção (Cloud Run) o job é separado e ainda não existe (PD23):
passo a passo em `docs/paginas/previsao.md`, seção 9.

## Testes e conferências

**Fontes (D57, 27/10/2026): o site só lê a gold** (`gold_monday`, 8 tabelas e 8 views do PPD-GOLDEN-AGENCIAMENTO-MONDAY).
O mapa página × gráfico × tabela está no [PRD](docs/PRD.md), "Retrato do código". Registros de revisões e auditorias
externas (auditoria e plano de golds de 26/10, já executado) em [docs/historico/](docs/historico/).

`...\Scripts\python.exe -m pip install -r requirements-dev.txt` e depois `...\Scripts\python.exe -m pytest tests -q` —
475 testes em 27/10/2026, sem BigQuery (`tests/conftest.py` substitui as tabelas gold por dados sintéticos calculados à
mão, e `tests/gold_simulada.py` monta sobre eles as views e colunas que a gold calcula; os testes de `ml/` levam a maior
parte do tempo). Cobrem a carga (`test_dados.py`), calendário e horas úteis da gold (`test_expediente.py`), as regras de cada página (`test_calculos.py`, `test_sla_*.py`, `test_atendimento*.py`,
`test_inicio_revisao.py`, `test_qualidade_previsao.py`, `test_previsao_pagina.py`), o portal e as máscaras
(`test_portal.py`), rotas, segurança e acessibilidade básica (`test_rotas.py`), textos e interface da batalha de 26/10
(`test_batalha2_*.py`), a regra de movimento no CSS (`test_movimento.py`), os modelos (`test_ml_*.py`) e a ficha "O que
falta" contra `pendencias.py` (`test_documentacao.py`).

Os números reais são conferidos contra o BigQuery (só leitura) por `tools/checar_reuniao.py` (passo único antes de
apresentar), `tools/conferir_estudo.py` (estudo do SLA, por caminho independente no banco) e `tools/auditar_modelos.py`
(métricas dos backtests salvos). Layout e movimento: `node tools/conferir_layout.mjs [URL] [--movimento]`.

## Área e seção novas

- **Seção nova numa área** (ex.: uma aba ao lado de SLA em Gestão de orçamentos): criar
  `app/apresentacoes/gestao_orcamentos/<secao>/` com `__init__.py`, `calculos.py` (regras com IDs) e `template.html`
  (`{% extends "apresentacao.html" %}`, um `<section class="slide">` por slide) e incluir um `Secao(...)` em
  `secoes` no `apresentacao.py` da área (com `pergunta`, `estado`, `na_reuniao`). Endereço `/viu-agenciamento/<secao>`.
  Página nova = ficha nova em `docs/paginas/`.
- **Área nova** (item novo no menu lateral): pasta `app/apresentacoes/<area>/` com `apresentacao.py`
  (`APRESENTACAO = Apresentacao(..., secoes=(...))`) e as subpastas das seções.
- Reiniciar o servidor: menu e navegador se montam sozinhos.

## Estrutura

```text
CLAUDE.md                     retomada: estado atual, fases, como trabalhar
.env                          tabelas de origem (fora do Git)
docs/
  PRD.md                      o projeto: estado atual, módulos por página, arquitetura, acesso, custos, decisões, histórico
  HISTORICO_2026-10.md        linha do tempo da etapa 21–26/10/2026, com as decisões
  paginas/                    fichas auditáveis por página (inicio, talentos, atendimento, sla, previsao, o_que_falta, demais) e glossário
  validacao/                  registros das conferências (reuniao_*.json, estudo_*.json e outros de 26/10)
  lembretes_gold.md           situações a validar no projeto da gold
  prompt_dados_pendentes.md   especificação das pendências de dados (PDxx) para a camada gold (rascunho)
  historico/                  registro: revisões externas de 22–24/10, auditoria e plano de golds de 26/10 (executado
                              em 27/10, D57), validações e capturas antigas (evidencias/)
app/
  main.py                     FastAPI: rotas, cabeçalhos, 503 sem dados, /saude
  config.py                   variáveis de ambiente (GOLD_DATASET e TAB_* de cada tabela/view gold, AUTH, DEV, MODO,
                              CONGELAR, PREVISAO_*, trava de produção)
  corte.py                    regra única do corte da carga (E3): véspera do processamento, mês fechado
  dados.py                    tabelas e views gold em memória: recarga pelo metadado (view: o da tabela de base),
                              contrato, base congelada, política de falha
  estatistica.py              teste de duas proporções (diferença "relevante" entre anos)
  expediente.py               calendário de feriados (R14) e expediente sem almoço (as horas vêm da gold, D57)
  sla.py, formato.py          mês parcial e dia de corte da carga do SLA; formatação pt-BR
  apresentacoes/<area>/       apresentacao.py, pendencias.py, inicio.html e <secao>/{calculos.py, template.html}
  templates/                  moldura (apresentacao.html), como_medimos.html, o_que_falta.html, macros
  static/                     estilo, navegação, fontes e logo VIU
ml/                           laboratório da Previsão (dados, régua, modelos, filtros, rotina mensal; saída em ml/saida/)
tests/                        testes com dados sintéticos (sem BigQuery); gold_simulada.py = as views da gold sobre eles
tools/                        conferências contra o BigQuery (só leitura) e de layout
_descartados/                 arquivos que saíram do projeto, por data, com LEIAME (o projeto não tem git: nada se apaga)
Dockerfile, .gcloudignore, .dockerignore, requirements.txt, requirements-dev.txt, requirements-ml.txt
Previstos (fases 2 e 3): app/acesso/ (login por link, sessões, admin) e deploy/gcp_setup.md
```
