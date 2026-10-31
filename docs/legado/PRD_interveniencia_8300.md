# PRD (legado): deck "Fechamentos de interveniência 2026" — porta 8300

> **LEGADO — não faz parte da entrega atual**

Projeto: `G:\Meu Drive\Workspace\globo\scripts\PPD-FECHAMENTO-INTERVENIENCIA` (só leitura). Documento escrito em
31/10/2026 a partir do código, sem alterá-lo e sem copiar dados do cache.

## 1. O que é

Deck local (FastAPI + Jinja) com os **fechamentos de interveniência de 2026**, no visual do portal "Gestão de
orçamentos". Pedido do Caio em 29/10/2026 para uma possível apresentação ("Reunião de diretoria · 29 de outubro de
2026", `app/main.py:19`). O README o declara **descartável**: deve ser refeito no padrão (gold + fichas). Não usa o
`gold_monday`: lê a planilha de projetos de agenciamento do SharePoint pela **bronze**.

Estáticos (`estilo.css`, fontes, logo, `apresentacao.js`, `icones.html`) e `app/formato.py` são cópias do portal de
29/10/2026.

## 2. Páginas

Sequência em `app/main.py:22-62`: Capa → 5 indicadores → Encerramento. Rotas `/interveniencia/capa`,
`/interveniencia/{secao}`, `/interveniencia/encerramento`; `/` leva à capa (`:78-80`).

| Slug | Pergunta (título) | Bloco de `calculos.montar()` |
|---|---|---|
| `fechamentos` | Quantos contratos de interveniência fechamos em {ano}? | `fechamentos` |
| `talentos` | Quem são os talentos contratados, e quantos voltaram? | `talentos` |
| `marcas` | Quais marcas mais contratam interveniências? | `marcas` |
| `ticket` | Qual é o porte dos contratos? | `ticket` |
| `conferencia` | O que ainda precisa de conferência na base? | `conferencia` |

## 3. Dados

### 3.1 Fonte e consulta (`app/dados.py`)

- Tabela: **`gglobo-viu-dados-hdg-prd.bronze_sharepoint.planilha__projetos_agenciamento`** (`dados.py:16-17`).
- Cada carga grava a aba inteira com o mesmo `_versao_id`; entra só a **versão mais recente** por `_ingested_at` e só
  `tipo_talento IN ('Interveniência', 'Não Exclusivo')` (`dados.py:18`, `:26-35`), ordenada por
  `data_de_fechamento, order_id`.
- Colunas lidas (`dados.py:21-24`): `order_id`, `data_de_fechamento`, `ano_de_fechamento`, `talento`,
  `origem_talento`, `tipo_talento`, `projeto`, `marca`, `origem_do_projeto`, `valor_total`, `cache_talento`,
  `comissao_globo`, `imposto`, `producao`, `saving`, `tipo_de_contratacao`, `contrato`, `comissao`, `responsavel`,
  `status_projetos`, `data_de_entrada`, `data_de_saida`, `pagamento`, `observacoes`, `projetos_a_conferir`; mais
  `_versao_id`, `_arquivo_modificado_em`, `_ingested_at` (metadados).
- Conversões (`dados.py:42-46`): datas para `AAAA-MM-DD` (inválidas viram nulo); valores, `ano_de_fechamento` e
  `order_id` para `float`.
- Cliente: `bigquery.Client(project="gglobo-viu-dados-hdg-prd")`, credenciais ADC do `gcloud-viu`; só SELECT.

### 3.2 Cache `dados/base.json`

- **Gerado** por `carregar()` (`dados.py:55-63`) quando o arquivo não existe ou `FORCAR_BQ` ∈ {`1`, `true`, `sim`};
  **usado** sem consultar o BigQuery em todas as outras subidas (base congelada).
- Estrutura: `{"meta": {versao, arquivo_modificado_em, ingerido_em, lido_em}, "linhas": [ {as 25 colunas acima} ]}`.
  Em 31/10/2026: 248 linhas, versão lida em 29/10/2026 00:58 (arquivo do SharePoint modificado em 28/10/2026).
- Contém nomes de talentos, marcas, valores, comissões e observações: **dado sensível**; não copiar para fora.
- `quadro()` (`dados.py:66-70`): `data` = `data_de_fechamento` em data; `ano` = `ano_de_fechamento`, ou o ano de
  `data` quando vazio.
- O resultado de `montar()` fica em memória (`_estado`, `main.py:42-49`) até o processo reiniciar.

## 4. Regras dos indicadores (`app/calculos.py`)

### 4.1 Preparação (`preparar`, `:41-48`)

| Campo | Regra |
|---|---|
| `nome` | `talento` sem espaços nas pontas (vazio → `""`) |
| `marca_n` | `marca_normal()` (`:34-38`): nulo → "Não informada"; minúsculas sem acento comparadas a `_MARCAS` (`:22-23`): tena → Tena, nivea → Nivea, irga → IRGA, boticario / o boticario → O Boticário, hyundai → Hyundai; demais ficam como escritas (ex.: "Essity Tena" separada) |
| `fornecedor` | nome começa com "BR Media" ou "Microboost", sem diferenciar maiúsculas (`FORNECEDOR`, `:21`) |
| `cancelado` | `status_projetos` sem espaços, em minúsculas, **igual** a "cancelado" |
| `mes` | mês de `data` |

### 4.2 Universo e período (`montar`, `:71-83`)

- `ano` = **maior** `ano` da base (inclui cancelados). `tudo_ano` = linhas desse ano; **universo `u`** = `tudo_ano`
  sem cancelados. Cada linha é um contrato; homônimos não se fundem.
- `ate` = maior `data` de `u`. Ano anterior `ant` = linhas de `ano − 1`, sem cancelados, com `data ≤ ate` levada ao
  ano anterior (mesmo dia e mês).
- Somas (`_soma`, `:51-52`) só com o preenchido; vazios contados à parte. Variação `var(a, b) = a / b − 1`, `None` se
  `b = 0`.

### 4.3 Fechamentos

| Indicador | Fórmula |
|---|---|
| `n`, `valor`, `comissao` | `len(u)`, Σ `valor_total`, Σ `comissao_globo` |
| `sem_valor`, `sem_comissao` | nulos em `valor_total`, `comissao_globo` |
| `nao_exclusivos` | linhas de `u` com `tipo_talento == "Não Exclusivo"` |
| `anterior` | mesmos totais em `ant` e `var_n`, `var_valor`, `var_comissao` |
| `pct_comissao` | `comissao / valor` (`None` se `valor = 0`) |
| `meses[1..12]` | `n`, `valor`, `comissao` do mês em `u`; `n_ant` = mês do ano anterior, **até o mesmo dia** só no mês de `ate`; `parcial` = mês de `ate`; `futuro` = meses depois dele (`:88-97`) |
| `escala` | maior `n` ou `n_ant` dos meses (mínimo 1) |

### 4.4 Talentos

- `pessoas` = `u` sem fornecedores. `_grupos(…, "nome")` (`:60-68`) por talento: `n`, `valor`, `comissao`,
  `sem_comissao`, `marcas` (distintas), `ticket` = Σ valor ÷ nº de valores preenchidos (mínimo 1).
- Ordem: mais contratos, depois maior comissão, depois nome. `n` = talentos distintos; `fornecedores` = grupos de
  fornecedor; `contratos_pessoas` = `len(pessoas)`.
- `recorrentes` = talentos com `n > 1`; `pct_recorrentes` = recorrentes ÷ talentos; `pct_contratos_recorrentes` =
  contratos dos recorrentes ÷ `len(pessoas)`.
- `por_frequencia`: faixas 1, 2, 3 e "4 ou mais" contratos (talentos e contratos por faixa, `:104-110`).
- `top` = 10 primeiros. `top_comissao` = 5 maiores comissões **em `u` inteiro** (inclui fornecedores, `:111`);
  `pct_top5_comissao` = Σ comissão dos 5 ÷ `comissao` total.

### 4.5 Marcas

`_grupos(u, "marca_n")`, ordem: mais contratos, maior valor, nome. `n` = marcas; `com_2` = marcas com mais de um
contrato; `top` = 10; `maior_n` = primeira; `maior_valor` = maior Σ valor.

### 4.6 Ticket

- `medio` = `valor` ÷ nº de valores preenchidos; `mediano` = mediana dos preenchidos (0 sem valores); `n_valor`.
- `faixas` (`FAIXAS`, `:24-26`; regra `:117-119`): 1ª faixa `0 ≤ valor ≤ 50 mil`; demais `lo < valor ≤ hi`
  (50–100 mil, 100–300 mil, 300 mil–1 mi, acima de 1 mi). Por faixa: `n`, Σ valor, Σ comissão.
- `maior` = 3 maiores `valor_total`.

### 4.7 Conferência

| Item | Regra |
|---|---|
| `recebidos` | `len(tudo_ano)` (com cancelados) |
| `cancelados`, `comissao_cancelados` | linhas canceladas do ano e Σ da comissão delas |
| `divergencias` | `valor_total` preenchido e `abs(valor_total − (cache_talento + comissao_globo + imposto + producao)) > 1`, vazios como 0 (`:121-122`); `saving` fica fora |
| `sem_valor`, `sem_comissao` | listas das linhas sem valor e sem comissão |
| `pagamento` | contagem por `pagamento` (vazio → "Não informado") |
| `a_conferir` | `projetos_a_conferir == "Conferir"` |

As listas (`linhas()`, `:127-133`) trazem `order_id`, nome, marca, projeto, data `dd/mm`, valor, comissão, soma das
partes e observação.

### 4.8 Formatação e arredondamento (`app/formato.py`)

- `inteiro`: meio para cima (`floor(x + 0,5)`), ponto de milhar. `variacao` e `sentido`: percentual inteiro meio para
  cima, sinal do número já arredondado (`:26-48`). `pct`: formatação do Python com `casas` (padrão 0).
- `reais` (`:127-138`): ≥ 1 mi → "R$ x,y mi" (1 casa); ≥ 10 mil → "R$ x mil" (inteiro); abaixo → "R$ x";
  negativo com "−". `reais_cheio`: "R$ 27.819.736" (sem centavos).

## 5. Como rodar

```powershell
cd "G:\Meu Drive\Workspace\globo\scripts\PPD-FECHAMENTO-INTERVENIENCIA"
.\rodar.ps1                  # define CLOUDSDK_CONFIG/ADC do gcloud-viu e sobe o uvicorn na 8300 com --reload
# para reler a bronze (só SELECT): $env:FORCAR_BQ = "true"; .\rodar.ps1
```

Abrir <http://127.0.0.1:8300/interveniencia/capa>. Venv compartilhado com o portal
(`C:\Users\CCMB\.venvs\ppd-agenciamento-sla`). Com o cache presente, as credenciais não são usadas.

## 6. Pontos de atenção

1. **`ano` = maior ano da base, não "ano da carga"** (`calculos.py:73`, contra o docstring `:4`): uma linha com
   `ano_de_fechamento` digitado errado (ex.: 2027), mesmo cancelada, muda o deck inteiro para esse ano.
2. **29 de fevereiro quebra o deck:** `ate.replace(year=ano − 1)` (`:80`) dá erro se a última data for 29/02 (ex.:
   2028).
3. Base vazia (última versão sem esses tipos) quebra em `df["_versao_id"].iloc[0]` (`dados.py:47`) e em
   `int(df["ano"].max())`.
4. Cancelado só com grafia exata "cancelado" (`:46`); "Cancelada" ou "Cancelado - …" entram como fechados, apesar do
   docstring dizer "qualquer grafia".
5. Linhas sem `data_de_fechamento` mas com `ano_de_fechamento` contam no total do ano, mas em nenhum mês (soma dos
   meses ≠ total) e nunca entram no ano anterior (`ant` exige data).
6. Talento ou marca vazios (`""`) viram um "talento"/"marca" próprio nas contagens; só marca nula vira "Não informada".
7. `top_comissao` inclui fornecedores (BR Media, Microboost), enquanto o resto da página de talentos os exclui.
8. Valores negativos ficam fora de todas as faixas de ticket; a divergência ignora `saving`.
9. `pct` arredonda pelo padrão do Python (`decimal`), diferente do "meio para cima" de `inteiro`/`variacao`: um mesmo
   percentual pode aparecer com uma unidade de diferença entre telas. `reais(999_960)` sai "R$ 1.000 mil".
10. Cache sensível (nomes, valores, observações) em pasta sincronizada do Google Drive, sem prazo de validade; o
    `_estado` em memória não recarrega sem reiniciar. `@app.on_event` está obsoleto no FastAPI.
11. A consulta busca a última versão por `ORDER BY _ingested_at DESC LIMIT 1` sobre a tabela inteira: varre todas as
    versões (custo cresce com o histórico).
12. Sem controle de acesso nem cabeçalhos de segurança: só para uso local (uvicorn em 127.0.0.1, padrão).
