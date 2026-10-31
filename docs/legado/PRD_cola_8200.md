# PRD (legado): cola do apresentador — porta 8200

> **LEGADO — não faz parte da entrega atual**

Projeto: `G:\Meu Drive\Workspace\globo\scripts\PPD-AGENCIAMENTO-COLA` (só leitura). Documento escrito em 31/10/2026 a
partir do código, sem alterá-lo. Cópia idêntica em `PPD-AGENCIAMENTO-SLA/_congelado/2026-10-29_reuniao/cola/`
(conferido por comparação de arquivos em 31/10).

## 1. O que é

Notas do apresentador (speaker notes) para a reunião de diretoria de 28/10/2026, numa segunda tela ao lado do portal
original "Gestão de orçamentos" (porta 8100). Página estática, sem servidor próprio de dados, sem CDN nem npm.

| Arquivo | Papel |
|---|---|
| `index.html` | estrutura: topo (indicador de sincronia, A−/A+), abas, subabas do estudo, ficha, rodapé ← → |
| `cola.js` | fichas (`FICHAS`), estados neutros (capa, encerramento), carga das falas, sincronia e tamanho da letra |
| `cola.css` | visual (fundo marinho, letra grande, fluida) |
| `rodar.ps1` | `python -m http.server 8200 --bind 127.0.0.1` na pasta |

## 2. Fichas e conteúdo

- Fichas em `cola.js:9-151`: `demanda`, `talentos`, `atendimento`, `sla`, `estudo-1`, `estudo-2-1/2/3` (Formato, Sino,
  Faixas do slide 2), `estudo-3` a `estudo-6`, `estudo-8` e `previsao`. A ficha `estudo-7` está comentada
  (`cola.js:125`, D64). Capa e encerramento não têm ficha: viram estados neutros (`NEUTROS`, `cola.js:153-156`).
- Cada ficha leva o `caminho` no portal (ex.: `/gestao-orcamentos/sla/como-medimos#2:1`), mensagem, **Fala**,
  **Roteiro** (passos), "Se perguntarem" e "Evitar". O texto inicial é só "Carregando…"; os números vêm do portal.
- As falas são montadas no **portal**, em `app/apresentacoes/gestao_orcamentos/cola.py` (`IDS`, `:20-22`; `compor()`,
  `:97`), com os mesmos contextos das páginas (`from . import apresentacao as paginas`) e recorte **Todos**. Cada
  ficha declara suas fontes (ex.: `('sla', 'fluxo')`), usadas para checar a carga.

## 3. Como sincroniza com o portal

Dois canais, ambos para `http://127.0.0.1:8100` (fixo em `cola.js:6`):

### 3.1 Posição: `/sinc` (D62)

| Lado | O que faz | Onde |
|---|---|---|
| Portal (servidor) | guarda em memória `{url, versao, origem, sessao}`; `versao` sobe só quando a página **normalizada** muda; `sessao` muda a cada subida | `app/main.py:155-202` (original) |
| Portal (servidor) | `GET /sinc` e `POST /sinc` respondem 404 se `config.SINC` for falso; POST aceita só `url` relativa (começa com `/`, não `//`, ≤ 300 caracteres) e `origem` `portal` ou `cola` | `main.py:181-202` |
| Portal (servidor) | CORS só para `http://127.0.0.1:8200` e `http://localhost:8200` | `app/config.py:69`; `main.py:172-178` |
| Portal (navegador) | `static/sinc.js`: publica a página atual e, a cada **600 ms**, lê `/sinc`; se a cola pediu outra página, vai até ela (no estudo, troca só o `#` ou clica o passo do slide 2) | `app/static/sinc.js:49-66` |
| Cola | `consultar()`: `GET /sinc` em cadeia, ~600 ms após cada resposta (timeout 2,5 s); segue só mudanças com `origem: "portal"` | `cola.js:452-474`, `buscar()` `:404-413`; `seguirPortal()` `:416-427` |
| Cola | ao trocar de ficha, `POST /sinc` com corpo `text/plain` `{"url", "origem": "cola"}` (sem preflight) | `enviarPortal()`, `cola.js:429-440` |

Normalização igual nos dois lados: sem a query e sem o `#`, exceto no estudo, onde o `#` é o slide e o slide 2 vira
`#2:N` pelo `?passo=` (`main.py:158-169`, `sinc.js:12-17`, `cola.js:192-211`). Se a `sessao` muda (portal reiniciou),
os dois lados esquecem a última versão vista. Indicador: "sincronizado com o portal" ou "portal fora do ar"; sem o
portal, a cola funciona sozinha (sem números).

### 3.2 Falas: `/cola/{ficha}` (28/10/2026)

- Rota no portal: `main.py:214-243`. Responde 404 se `not config.SINC or config.EM_PRODUCAO` (`:218`), 403 para
  origem fora de `SINC_ORIGENS`, `Cache-Control: no-store`. Lê as versões das tabelas antes e depois de `compor()`
  (até 2 tentativas); se a carga mudou no meio, ou uma fonte tem erro, devolve **503** "Dados indisponíveis".
- Resposta: `{ficha, texto, congelada, cargas, recorte: "Todos"}`.
- Na cola (`carregarFala`, `cola.js:162-186`): consulta ao abrir a ficha e um temporizador de **10 s** (`:188-190`)
  reconsulta a ficha visível se a última leitura tem mais de **60 s** (`:164`) e a aba não está oculta. Timeout de
  20 s. Em falha, **oculta os números** e mostra aviso; não há volta aos números antigos.
- Os números seguem a base do portal: se o portal está congelado (`CONGELAR`), a fala também, e o topo diz "base
  congelada". A Previsão usa o último retrato publicado.

## 4. Dependências

| Dependência | Para quê |
|---|---|
| Python (qualquer, `http.server`) | servir os estáticos na 8200 |
| Portal original na 8100 com `SINC` ligado (padrão no computador) | `/sinc` e `/cola/{ficha}`; sem ele, só a navegação local |
| Navegador moderno | `fetch`, `AbortController`, `localStorage` (só o tamanho da letra) |

Não usa credenciais nem BigQuery no navegador: o acesso ao banco é só do portal.

## 5. Como rodar

```powershell
# 1. portal original na 8100 (ver PRD_portal_original_8100.md), com SINC ligado (padrão)
# 2. cola
cd "G:\Meu Drive\Workspace\globo\scripts\PPD-AGENCIAMENTO-COLA"
.\rodar.ps1        # ou: python -m http.server 8200 --bind 127.0.0.1
```

Abrir <http://127.0.0.1:8200>. Setas ← → (ou PageUp/PageDown) trocam a ficha; A−/A+ mudam a letra.

## 6. Não funciona com a V2 publicada

A cola **não acompanha a V2 em produção** nem a V2 local como está configurada:

| Motivo | Evidência |
|---|---|
| Em produção (Cloud Run define `K_SERVICE`), `SINC` é falso: `SINC = not EM_PRODUCAO and SINC != off` | V2 `app/config.py` (`EM_PRODUCAO`, `SINC`) |
| `/sinc` (GET e POST) responde 404 sem `SINC` | V2 `app/main.py` (`sinc_ler`, `sinc_gravar`) |
| `/cola/{ficha}` responde 404 com `not config.SINC or config.EM_PRODUCAO` | V2 `app/main.py` (`texto_cola`) |
| Com `AUTH=iap`, toda requisição sem o cabeçalho assinado do IAP recebe 401, inclusive as da cola | V2 `app/main.py` (middleware `cabecalhos`) |
| CORS aceita só as origens `127.0.0.1:8200` e `localhost:8200`; o portal alvo é fixo em `http://127.0.0.1:8100` | V2 `config.py` (`SINC_ORIGENS`); `cola.js:6` |
| Localmente a V2 roda na 8400 com `SINC=off` ("a cola da 8200 segue só o original") | V2 `CLAUDE.md`, topo |
| As fichas são as da reunião: Atendimento (oculto na V2), estudo de 7 slides (V2 tem 5); não há fichas para Roadmap, LIA e Iniciativas. O `cola.py` da V2 é idêntico ao do original | `cola.js:9-151`; comparação de arquivos |

Para usar com a V2 seria preciso outro projeto de cola (portal alvo, fichas e falas novas); fora do escopo deste legado.

## 7. Pontos de atenção

1. **`POST /sinc` sem proteção de origem.** O corpo `text/plain` evita preflight; o CORS só limita quem **lê** a
   resposta. Qualquer página aberta no mesmo navegador pode mandar o portal local para outro endereço do próprio portal
   (só caminhos relativos, então o efeito é trocar de página). Risco baixo, só local, mas real durante a reunião.
2. Estado de `/sinc` em memória do processo (`_SINC`): com mais de um worker do uvicorn, portal e cola se desencontram.
3. README desatualizado: diz "Estudo (8 slides)"; desde a D64 são 7 (`estudo-7` comentado em `cola.js:125`), enquanto
   `IDS` do `cola.py` ainda lista `estudo-7` (inofensivo, mas divergente).
4. Endereço do portal e porta fixos no código (`cola.js:6`, `config.py:69`): mudar a porta de um dos lados quebra a
   sincronia sem aviso claro além de "portal fora do ar".
5. `seguirPortal()` (`cola.js:416-427`) só reconhece a capa, o encerramento e os caminhos exatos das fichas; numa
   página do portal sem ficha (ex.: Resultado ou Qualidade, ocultas), a cola fica na ficha anterior sem avisar.
6. As falas usam sempre o recorte **Todos**; se o apresentador troca o filtro de talentos no portal, os números falados
   deixam de bater com a tela (a cola avisa o recorte, mas não detecta a troca).
