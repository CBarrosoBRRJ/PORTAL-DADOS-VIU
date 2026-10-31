# PRD (legado): portal original "Gestão de orçamentos" — porta 8100

> **LEGADO — não faz parte da entrega atual**

Projeto: `G:\Meu Drive\Workspace\globo\scripts\PPD-AGENCIAMENTO-SLA` (só leitura). Documento escrito em 31/10/2026 a
partir do código e dos documentos do projeto, sem alterá-lo. A entrega atual é a V2 (`..\..\` desta pasta,
"ViU Agenciamento").

## 1. O que é

Site interno de relatórios do board **Backlog 2026 | Agenciamento** (FastAPI + Jinja), lendo **só** as tabelas e views
gold do dataset `gold_monday` (projeto irmão `PPD-GOLDEN-AGENCIAMENTO-MONDAY`; decisão D57 de 27/10/2026). Foi o portal
apresentado na **reunião de diretoria de 28/10/2026**, em apresentação local (`MODO=apresentacao`), sem publicação.

| Item | Valor |
|---|---|
| Nome na tela | "Gestão de orçamentos" (`cabecalho`, `app/apresentacoes/gestao_orcamentos/apresentacao.py:296`) |
| Porta local | 8100 |
| Acesso | só `AUTH=off`, só no computador (`app/main.py:21-26`); qualquer outro valor impede a subida |
| Fonte de dados | gold `gold_monday` (8 tabelas + 8 views); exceção: sensibilidade de 2025 do ML (silver, fora da tela) |
| Previsão | lê `ml/saida/previsao.json` (job de ML local, mensal, D48); em produção o job não existe (PD23) |
| Cola do apresentador | `../PPD-AGENCIAMENTO-COLA` (porta 8200), via `/sinc` e `/cola/{ficha}` (ver `PRD_cola_8200.md`) |
| Testes | 498 em 29/10/2026 (LEIAME do congelado) |

## 2. Sequência de páginas (como foi apresentada)

Definida em `APRESENTACAO` (`apresentacao.py:293-409`):

| # | Página | Endereço | Observação |
|---|---|---|---|
| 0 | Capa | `/gestao-orcamentos/capa` (a raiz `/` abre nela) | jornada animada de um pedido; relógio para no típico do SLA (`medida_capa`, `:42-48`) |
| 1 | Demanda (antiga "Início") | `/gestao-orcamentos` | `rotulo_inicio="Demanda"` (`:306`) |
| 2 | Talentos | `/gestao-orcamentos/talentos` | filtro de talentos (`:344-353`) |
| 3 | Atendimento | `/gestao-orcamentos/atendimento` | visível (`:354-361`) |
| 4 | SLA de entrega | `/gestao-orcamentos/sla` | "meta a oficializar"; estudo "Como medimos" opcional pelo botão Estudo (`:362-373`) |
| 4a | Estudo "Como medimos" | `/gestao-orcamentos/sla/como-medimos#N` | **7 slides** (slide de tipo de pedido fora, D64: `ESTUDO_TIPO = False`, `:90`) |
| 5 | Previsão de demanda | `/gestao-orcamentos/previsao` | "2 decisões abertas" (`:374-385`) |
| 6 | Encerramento | `/gestao-orcamentos/encerramento` | marinho, "Obrigado." (`:332-339`) |
| — | Resultado, Qualidade | endereços mantidos | `oculta=True` (D59, `:394`, `:405`) |

Capas de seção desligadas (`capas_secao=None`, `:342`; textos guardados em `CAPAS_SECAO`, `:280-291`). Navegação de
28/10: gancho e setas seguem SLA → Previsão; o estudo é desvio opcional.

## 3. Estado congelado (28–29/10/2026)

- **28/10/2026:** reunião de diretoria; base congelada (`CONGELAR`, ligado por padrão no computador desde a D63,
  `app/config.py:74`), job da Previsão parado, carga da gold de 28/10 (09:03–09:05).
- **29/10/2026:** o Caio validou portal e cola; cópia fiel em `_congelado/2026-10-29_reuniao/` e instrução "não mexer
  sem pedido" (`CLAUDE.md`, topo).

## 4. Onde ficam as cópias

| Caminho (relativo a `PPD-AGENCIAMENTO-SLA`) | Conteúdo |
|---|---|
| `_congelado/2026-10-29_reuniao/portal/app/` | cópia do `app/` validado (sem `__pycache__`) |
| `_congelado/2026-10-29_reuniao/cola/` | cópia da cola (`index.html`, `cola.js`, `cola.css`, `README.md`, `rodar.ps1`) |
| `_congelado/2026-10-29_reuniao/falas_da_cola.json` | falas que `/cola/{ficha}` devolveu no congelamento (recorte Todos, carga de 28/10) |
| `_congelado/2026-10-29_reuniao/LEIAME.md` | como restaurar: copiar `portal/app/` sobre `app/` e `cola/` sobre `../PPD-AGENCIAMENTO-COLA/`, depois rodar os testes |
| `_congelado/2026-10-30_capa_antes/` | `capa.html`, `capa.js`, `estilo.css` (iguais aos do congelado de 29/10) e um `gestao_orcamentos_init.py` vazio; **sem LEIAME** |
| `../PPD-AGENCIAMENTO-SLA-V2/` | cópia de trabalho de 30/10 (sem `_congelado`, `_descartados`, `_entregas`): a entrega atual |

## 5. Como rodar (só no computador)

```powershell
$env:CLOUDSDK_CONFIG = "C:\Users\CCMB\AppData\Roaming\gcloud-viu"
$env:GOOGLE_APPLICATION_CREDENTIALS = "$env:CLOUDSDK_CONFIG\application_default_credentials.json"
$env:AUTH = "off"
$env:MODO = "apresentacao"      # como na reunião; sem --reload
C:\Users\CCMB\.venvs\ppd-agenciamento-sla\Scripts\python.exe -m uvicorn app.main:app --port 8100
```

Abrir <http://127.0.0.1:8100/gestao-orcamentos/capa>. Antes de apresentar (README): `python -m ml.rodar
--acompanhamento` e `python tools\checar_reuniao.py` (só SELECT; grava `docs/validacao/reuniao_AAAA-MM-DD.json`).
Testes: `python -m pytest tests -q` no venv. Para trabalhar com recarga: `--reload --reload-dir app` e
`WATCHFILES_FORCE_POLLING=true`. Conferir antes que não há outro uvicorn do projeto na mesma porta (README).

## 6. O que a V2 mudou

Comparação entre `PPD-AGENCIAMENTO-SLA/app/apresentacoes/gestao_orcamentos/apresentacao.py` (original) e
`PPD-AGENCIAMENTO-SLA-V2/app/apresentacoes/gestao_orcamentos/apresentacao.py` (V2), mais `app/main.py`,
`app/config.py` e `CLAUDE.md` da V2.

| Tema | Original (8100) | V2 (8400 local; Cloud Run com IAP) |
|---|---|---|
| Nome | "Gestão de orçamentos" (`:296`) | "ViU Agenciamento" (V2 `:319`); capa "ViU *Agenciamento*", sobretítulo "Relatório da área" (V2 `:330-338`) |
| Sequência | Capa → Demanda → Talentos → Atendimento → SLA → Previsão → Encerramento | Capa → **Roadmap** (`antes_do_inicio=True`, V2 `:369-379`) → Demanda → Talentos → SLA → **LIA** (V2 `:411-420`) → **Iniciativas** (V2 `:435-444`) → Previsão (última) → Encerramento |
| Atendimento | visível | `oculta=True` (V2 `:396`); código e endereço mantidos |
| Estudo "Como medimos" | 7 slides (8 com `ESTUDO_TIPO`) | 5 slides; conclusão retirada; o 5º sai para SLA ou LIA (V2 `CLAUDE.md`; ficha `docs/paginas/sla.md`) |
| LIA | não existe | página nova; lê `lia/retrato.json` (extraído do Cloud Storage da LIA por `tools/extrair_lia.py`; exceção à D57); vídeo em pop-up, página `lia-na-pratica` oculta (V2 `:421-434`) |
| Iniciativas | não existe | página com banco próprio: SQLite fora do Drive no computador, Firestore + bucket privado no Cloud Run (`INICIATIVAS_BACKEND`, V2 `app/config.py`); edição em produção só com `INICIATIVAS_EDICAO=on` (V2 `config.py`) |
| Encerramento | gancho "E o que levamos desta reunião?", próximo passo e pergunta | gancho "Encerramento", frase e pergunta vazias (V2 `:357-364`) |
| Acesso | só `AUTH=off` (`main.py:24-26`) | `AUTH=off` (computador) ou `AUTH=iap` com `IAP_AUDIENCE` obrigatório (V2 `main.py`, travas do início do arquivo); com `iap`, toda requisição sem o cabeçalho assinado recebe 401 (V2 `main.py`, middleware `cabecalhos`) |
| Publicação | nada publicado | roteiro de deploy em `docs/deploy_iniciativas.md` (Cloud Run + IAP); `AUTH=iap` é exceção temporária à D10, a aprovar pelo Caio |
| Cola (8200) | sincronizada (`SINC` ligado no computador) | `SINC=off` na 8400; em produção `SINC` e `/cola` desligam sozinhos (ver `PRD_cola_8200.md`) |
| Testes | 498 (29/10) | 550 (31/10, V2 `CLAUDE.md`) |

Inalterados: `ESTUDO_TIPO = False`, `CAPAS_SECAO` desligadas, Resultado e Qualidade ocultas, leitura só da gold nas
páginas herdadas, `app/static/sinc.js` e `gestao_orcamentos/cola.py` (arquivos idênticos nos dois projetos).

## 7. Pontos de atenção

1. **O `app/` do original não é mais o congelado.** `app/templates/capa.html` (30/10 10:43) e `app/static/estilo.css`
   (30/10 12:49) diferem de `_congelado/2026-10-29_reuniao/portal/app/`, apesar da regra "não mexer sem pedido".
   Quem subir a 8100 hoje não vê exatamente a versão da reunião; para isso, restaurar pelo LEIAME do congelado.
2. `_congelado/2026-10-30_capa_antes/` não tem LEIAME (contraria a regra 11 do `CLAUDE.md`) e traz um
   `gestao_orcamentos_init.py` de 0 byte: se alguém o copiar sobre o `__init__.py` real, apaga o conteúdo.
3. Documentação desatualizada em pontos: README fala em 475 testes e "8 slides × 3 grupos" no `conferir_layout.mjs`
   (hoje 7 slides); o docstring de `apresentacao.py:3-4` ainda lista Resultado e Qualidade na ordem da reunião.
4. O site não tem controle de acesso próprio (fase 2 não feita): não pode ser publicado (D10). A trava de
   `main.py:21-26` impede subir com qualquer `AUTH` diferente de `off`.
5. `CONGELAR` ligado por padrão no computador (D63): sem `CONGELAR=false`, os números ficam presos à carga lida na
   subida; útil para apresentar, enganoso para conferir dados novos.
