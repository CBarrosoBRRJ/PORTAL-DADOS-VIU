# Congelar outubro para a reunião de 04/11/2026 (D65)

> **O que aconteceu de fato (03/11/2026, D67):** o roteiro de segunda não foi rodado a tempo; na terça a carga das 09:02
> (dados até 02/11) já tinha substituído a de 02/11. Decisão do Caio: congelar essa carga com folga de 2 dias
> (`CORTE_FOLGA_DIAS` padrão 2) e rodapé "Dados até 02/11/2026". Passos 2 a 5 executados em 03/11; o deploy (passo 6)
> fica com o Caio. Registro em `docs/PRD_V2.md`, seção 0.6.

Roteiro para o Caio. O objetivo é que o portal mostre **outubro completo** e não mude mais entre 01/11 e 04/11, no
computador e no link publicado. A regra está em `app/congelamento.py` (K1–K7 e, desde a auditoria de 31/10, B1–B5), a
configuração em `app/config.py` (`CORTE_DADOS`, `CORTE_FOLGA_DIAS`, `BASE_CONGELADA_DIR`) e a ferramenta em
`tools/congelar_base.py`. A conferência do build está em `app/conferir_base.py`. Os testes estão em `tests/test_corte.py`
e `tests/test_auditoria_dados.py`. Correções da auditoria (F01, F02, F03, F07, F08): `docs/auditoria/correcoes_2026-10-31.md`.

## O que muda (resumo)

- **Corte ligado por padrão:** `CORTE_DADOS=2026-10-31`. Enquanto a carga da gold tiver dados até antes de 31/10
  (regra E3: o dia anterior ao `_processado_em`, no horário de São Paulo), o portal continua atualizando.
- **Congelamento:** a 1ª carga com dados até 31/10 é a última aceita. Uma carga até 01/11 também é aceita, pela folga de
  1 dia. Nesse momento cada tabela congela **em memória**. Quando as 10 congelaram na mesma carga, a base é gravada
  **como unidade** em `app/base_congelada/`: uma pasta de versão `v-<fim>-<momento>-<código>` com um `.parquet` por
  tabela e o `manifesto.json` (corte, carga, tabelas, sha256), publicado por último e de forma atômica. Só depois de
  gravada e relida ela conta como **persistida** (o `/saude` mostra `base_congelada.persistida`). Se a gravação falhar,
  a base continua em memória, o erro aparece no log e no `/saude` e o portal tenta de novo a cada 30 s. Um escritor por
  vez (trava `.escrita.lock`). Depois disso nada troca a base, nem a recarga forçada, e o BigQuery não é mais consultado.
- **Cargas que chegam tarde demais:** se a 1ª carga vista já cobre além de 01/11, ela é ignorada, a base anterior
  continua no ar e a falha aparece na tela. Todas as tabelas congelam na mesma carga; uma tabela de outra carga também
  é ignorada.
- **Produção (Cloud Run):** a pasta `app/base_congelada/` entra na imagem pelo `COPY app/`. O serviço lê só desses
  arquivos e nunca chama o BigQuery. Assim não depende da permissão de leitura do BigQuery e abre mais rápido. A
  Previsão vai junto: o `Dockerfile` copia `ml/saida/previsao.json`. A LIA já estava em `app/`. **Novo (F01):** o build
  roda `python -m app.conferir_base` e **para** se a base estiver ausente, incompleta ou incoerente com o manifesto, se a
  Previsão não for de outubro e da mesma carga da base (retrato e acompanhamento) ou se a LIA não for até 31/10. O
  arranque confere a base de novo: sem ela, a revisão nova não sobe e a anterior continua no ar.
- **Rodapé (caminho B, escolhido):** "Dados até 01/11/2026 · atualizados em 02/11/2026, 09:0x · base congelada para a
  apresentação". No caminho A, seria "Dados até 31/10/2026 · atualizados em 01/11/2026, …".
- **Por que não filtrar as linhas por data:** as tabelas da gold trazem o estado do board na hora da carga (em aberto,
  status atual, horas). Cortar as linhas depois de 31/10 no site seria refazer regra de negócio, o que viola a D57. O
  corte escolhe apenas qual carga inteira da gold é mostrada.

## Caminho escolhido: B, a carga agendada de segunda 02/11 (Caio, 31/10/2026)

31/10/2026 é sábado. A agenda é bronze 08:00 → silver 08:30 → gold 09:00, de segunda a sexta. A última carga foi a de
sexta, 30/10 às 09:01, com **dados até 29/10** (conferido em 31/10). No fim de semana não há carga.

| Caminho | O que fazer | Rodapé | Observação |
|---|---|---|---|
| **B (escolhido)** | Esperar a carga agendada de **segunda 02/11 às 09:00** e seguir este roteiro **depois das 09:30** | **Dados até 01/11/2026** | aceita pela folga de 1 dia (`CORTE_FOLGA_DIAS=1`, sem mudar código); em 2026 caíram só 6 pedidos em domingos no ano inteiro; nada a executar no GCP se a carga rodar |
| A (alternativa) | No domingo 01/11, disparar à mão a cadeia bronze → silver → gold (comandos do passo 0) | Dados até 31/10/2026 | outubro exato; exige o Caio executar os jobs no domingo |

**Tudo acontece na segunda 02/11, depois da carga:** base congelada, Previsão (`ml.rodar --rotina`) e LIA. O ML lê o
BigQuery direto: rode a rotina no mesmo dia, antes da carga de terça 03/11 às 09:00, para ela usar a mesma carga da base.

## Preparação (PowerShell, na raiz da V2)

```powershell
cd "G:\Meu Drive\Workspace\globo\scripts\PPD-AGENCIAMENTO-SLA-V2"
$env:CLOUDSDK_CONFIG = "C:\Users\CCMB\AppData\Roaming\gcloud-viu"
$env:GOOGLE_APPLICATION_CREDENTIALS = "$env:CLOUDSDK_CONFIG\application_default_credentials.json"
$py = "C:\Users\CCMB\.venvs\ppd-agenciamento-sla\Scripts\python.exe"
gcloud config list --format="value(core.account,core.project)"   # esperado: caio.barroso@viu.com.br  gglobo-viu-dados-hdg-prd
```

Em 31/10 o login do `gcloud` (a CLI) tinha expirado ("Reauthentication failed"); as credenciais ADC do Python ainda
funcionavam. Se a CLI pedir, rode `gcloud auth login` (e, se o Python falhar, `gcloud auth application-default login`)
com a conta corporativa.

## Passo 0 (segunda 02/11, depois das 09:30): a carga de Finados rodou?

**02/11 é feriado (Finados).** O agendamento `1-5` não pula feriado, então a carga deve rodar normalmente. Confira
antes de seguir (só leitura):

```powershell
gcloud scheduler jobs list --location=us-central1 --project=gglobo-viu-dados-hdg-prd --format="table(name.basename(),schedule,timeZone,state)"
gcloud run jobs executions list --job=bronze-monday --region=us-central1 --project=gglobo-viu-dados-hdg-prd --limit=1 --format="table(name,status.completionTime,status.succeededCount,status.failedCount)"
gcloud run jobs executions list --job=silver-monday --region=us-central1 --project=gglobo-viu-dados-hdg-prd --limit=1 --format="table(name,status.completionTime,status.succeededCount,status.failedCount)"
gcloud run jobs executions list --job=gold-agenciamento --region=us-central1 --project=gglobo-viu-dados-hdg-prd --limit=1 --format="table(name,status.completionTime,status.succeededCount,status.failedCount)"
```

O esperado é encontrar `bronze-monday-diario` (`0 8 * * 1-5`), `silver-monday-diario` (`30 8 * * 1-5`) e
`gold-agenciamento-diario` (`0 9 * * 1-5`), todos `ENABLED`. As três execuções mais recentes devem ser de 02/11, com
`succeededCount = 1`, e a do gold deve ter terminado por volta das 09:0x. O passo 1 confirma isso pelos dados.

**Se a carga de segunda não rodou ou falhou**, dispare a cadeia à mão pelos próprios agendamentos (mesmos argumentos
de todo dia), **um por vez**, esperando cada um terminar com sucesso antes do próximo. Os mesmos comandos servem para o
caminho A no domingo.

```powershell
gcloud scheduler jobs run bronze-monday-diario --location=us-central1 --project=gglobo-viu-dados-hdg-prd
gcloud run jobs executions list --job=bronze-monday --region=us-central1 --project=gglobo-viu-dados-hdg-prd --limit=1 --format="table(name,status.completionTime,status.succeededCount,status.failedCount)"
# quando succeededCount = 1:
gcloud scheduler jobs run silver-monday-diario --location=us-central1 --project=gglobo-viu-dados-hdg-prd
gcloud run jobs executions list --job=silver-monday --region=us-central1 --project=gglobo-viu-dados-hdg-prd --limit=1 --format="table(name,status.completionTime,status.succeededCount,status.failedCount)"
# quando succeededCount = 1:
gcloud scheduler jobs run gold-agenciamento-diario --location=us-central1 --project=gglobo-viu-dados-hdg-prd
gcloud run jobs executions list --job=gold-agenciamento --region=us-central1 --project=gglobo-viu-dados-hdg-prd --limit=1 --format="table(name,status.completionTime,status.succeededCount,status.failedCount)"
```

Se só o gold falhou e o bronze e o silver de 02/11 saíram com sucesso, basta disparar o gold. A gold confere se a
silver é do dia; ela espera até 30 min e falha sem gravar nada se a silver não tiver chegado. Uma falha deixa a tabela
com a carga anterior, sem dano. Disparada na segunda, a carga continua com dados até 01/11. Os nomes dos jobs vêm dos
roteiros de deploy dos projetos bronze, silver e gold: confira na listagem acima.

## Passo 1: conferir que a carga trouxe dados até 01/11 (só leitura)

```powershell
bq query --use_legacy_sql=false --project_id=gglobo-viu-dados-hdg-prd --format=pretty @'
SELECT 'sla_movimentos' AS tabela, MAX(_processado_em) AS processado_em, DATE_SUB(DATE(MAX(_processado_em), 'America/Sao_Paulo'), INTERVAL 1 DAY) AS dados_ate FROM `gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_2026_sla_movimentos`
UNION ALL SELECT 'entrada_diaria', MAX(_processado_em), DATE_SUB(DATE(MAX(_processado_em), 'America/Sao_Paulo'), INTERVAL 1 DAY) FROM `gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_entrada_diaria`
UNION ALL SELECT 'fluxo_mensal', MAX(_processado_em), DATE_SUB(DATE(MAX(_processado_em), 'America/Sao_Paulo'), INTERVAL 1 DAY) FROM `gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_fluxo_mensal`
UNION ALL SELECT 'talentos_ano', MAX(_processado_em), DATE_SUB(DATE(MAX(_processado_em), 'America/Sao_Paulo'), INTERVAL 1 DAY) FROM `gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_2026_talentos_ano`
UNION ALL SELECT 'talentos_ranking', MAX(_processado_em), DATE_SUB(DATE(MAX(_processado_em), 'America/Sao_Paulo'), INTERVAL 1 DAY) FROM `gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_2026_talentos_ranking`
UNION ALL SELECT 'saidas_status', MAX(_processado_em), DATE_SUB(DATE(MAX(_processado_em), 'America/Sao_Paulo'), INTERVAL 1 DAY) FROM `gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_2026_saidas_status`
'@
bq query --use_legacy_sql=false --project_id=gglobo-viu-dados-hdg-prd --format=pretty "SELECT data, SUM(quantidade) AS pedidos FROM ``gglobo-viu-dados-hdg-prd.gold_monday.gld_agenciamento_entrada_diaria`` WHERE data >= '2026-10-28' GROUP BY data ORDER BY data"
```

Esperado: as 6 linhas com `processado_em` de 02/11 (≈ 12:0x UTC) e `dados_ate` = **2026-11-01** (caminho B; no A seria
2026-10-31). Na 2ª consulta deve aparecer o dia 30/10 com pedidos (em 31/10 a gold só ia até 29/10); 31/10 e 01/11
devem ter poucos ou nenhum. Se `dados_ate` ainda for 29/10, a carga não rodou: volte ao passo 0. Se for 02/11 ou
depois, a carga já passou da folga: veja "Se algo der errado".

## Passo 2: gerar a base congelada

```powershell
& $py tools\congelar_base.py
```

Esperado: as 10 tabelas `congelada`, a mesma data em "dados até" e "Tudo certo: 10 tabelas congeladas na versão
v-20261101-… (dados até 2026-11-01, carga processada em 02/11/2026 09:0x)". Os arquivos ficam em
`app\base_congelada\`: o `manifesto.json` e a pasta `v-…` (cerca de 1 MB). Se o servidor da 8400 estiver no ar, ele
também congela em até 5 min; quem chegar primeiro grava, e o outro reconhece a base gravada (mesma carga) sem regravar.
Se aparecer "NÃO gravada" ou "outro processo está gravando", espere 1 minuto e rode o passo 2 de novo.

O ensaio de 31/10, com corte simulado em 29/10 numa pasta temporária, deu: 10 tabelas congeladas, e as 8 páginas
geradas do arquivo **idênticas** às geradas do BigQuery.

## Passo 3: Previsão e LIA

**Decisão (D65):** a reunião mostra o **retrato de outubro**. Pelo protocolo D48 (J1), outubro fechado é mês novo e
pede a rotina. Se o retrato de setembro fosse mantido, outubro ficaria **fora do gráfico**: ele não é mais o mês em
andamento da carga (o mês em andamento passa a ser novembro) nem um mês fechado do retrato. A régua (teste jun–set/2026,
menor WAPE) não muda; muda a janela de treino, que passa a terminar em outubro, e os meses previstos passam a ser nov,
dez e jan.

```powershell
# guardar o retrato de setembro (nada se apaga; ml/saida/retratos/2026-09.json também fica)
New-Item -ItemType Directory -Force "_descartados\2026-11-02\ml\saida" | Out-Null
Copy-Item ml\saida\previsao.json "_descartados\2026-11-02\ml\saida\previsao_retrato_2026-09.json"
& $py -m ml.rodar --rotina          # snapshot (só SELECT) + os modelos + retrato de 2026-10 (~9 min)
& $py -c "import json; p=json.load(open('ml/saida/previsao.json', encoding='utf-8')); print(p['retrato'], p['carga'])"
```

Rode na segunda 02/11, logo depois do passo 2 e antes da carga de terça 03/11 às 09:00.
Esperado: `mes_fechado: 2026-10` (dados até 01/11 → último mês fechado = outubro) e `processado_em` de 02/11, o mesmo
dia da base congelada. **Novo (F03):** o acompanhamento também precisa ser da carga de 02/11. Confira com
`& $py -c "import json; p=json.load(open('ml/saida/previsao.json', encoding='utf-8')); print(p['acompanhamento']['ate'], p['acompanhamento']['processado_em'])"`;
se o `processado_em` não for de 02/11, rode `& $py -m ml.rodar --acompanhamento` no mesmo dia.
`tools/congelar_base.py --conferir` e o build reprovam retrato ou acompanhamento de outra carga; na página, o rodapé da
Previsão mostra "acompanhamento até dd/mm" e, se as cargas divergirem, um aviso com ícone. Se `ml.rodar` reclamar de
biblioteca, instale com `& $py -m pip install -r requirements-ml.txt` (README).

**LIA** (só leitura no bucket `gglobo-viu-lia-dados-prd`), também na segunda 02/11. Os dias 31/10 e 01/11 já estão
completos no bucket.

**Recomendação: `--fim 2026-10-31`.** A LIA tem a própria janela, que aparece no título do gráfico ("21/09 a 31/10");
ela não segue o rodapé, que é o das tabelas da gold. Fechar em 31/10 mantém a mensagem da reunião, "outubro
completo", e bate com o `congelar_base.py --conferir`, que espera a LIA até a data do corte. Com `--fim 2026-11-01`, a
última semana ISO (26/10 a 01/11) ficaria inteira e a data coincidiria com o rodapé. Em troca, entraria um domingo de
novembro, com e-mails processados fora do expediente (pesa no "54% fora do expediente"), e o `--conferir` acusaria
"LIA até 2026-11-01". Se o Caio preferir 01/11, troque `--fim` e ignore só essa linha do `--conferir`.


```powershell
New-Item -ItemType Directory -Force "_descartados\2026-11-02\app\apresentacoes\gestao_orcamentos\lia" | Out-Null
Copy-Item app\apresentacoes\gestao_orcamentos\lia\retrato.json "_descartados\2026-11-02\app\apresentacoes\gestao_orcamentos\lia\retrato_ate_2026-10-29.json"
& $py tools\extrair_lia.py --fim 2026-10-31
& $py -c "import json; p=json.load(open('app/apresentacoes/gestao_orcamentos/lia/retrato.json', encoding='utf-8')); print(p['inicio'], p['fim'], p['extraido_em'])"
```

Esperado: `2026-09-21 2026-10-31 2026-11-02 …`. A última semana ISO (26/10 a 01/11) fica sem o domingo. Registre uma
linha no `_descartados\2026-11-02\LEIAME.md` para cada cópia guardada.

Depois disso, os números da Previsão (ficha `docs/paginas/previsao.md`) e da LIA (`docs/paginas/lia.md`: 2.047 lidos,
87% etc.) mudam. Atualize o "Retrato da carga" das fichas (Demanda, Talentos, SLA, LIA, Previsão) com a carga
congelada.

## Passo 4: testes

```powershell
& $py -m pytest tests -q -p no:cacheprovider
```

## Passo 5: conferir as páginas

```powershell
& $py tools\congelar_base.py --conferir    # SEM BigQuery: base inteira (manifesto) + Previsão de 2026-10 da mesma carga (retrato e acompanhamento) + LIA até 31/10
& $py -m app.conferir_base                 # a mesma conferência que o build da imagem roda
```

Esperado: "Tudo certo" e "Pacote conferido". Para ver o portal como o Cloud Run vai ver, suba um servidor de conferência **sem credenciais**
(qualquer tentativa de ler o BigQuery falharia). Use outra porta, sem mexer no da 8400:

```powershell
$env:AUTH = "off"; $env:SINC = "off"; $env:GOOGLE_APPLICATION_CREDENTIALS = "C:\nao-existe.json"
& $py -m uvicorn app.main:app --port 8401
```

Abra <http://127.0.0.1:8401/viu-agenciamento/capa> e percorra Capa → Roadmap → Demanda → Talentos → SLA (e o estudo) →
LIA → Iniciativas → Previsão → Encerramento. O rodapé deve dizer "Dados até 01/11/2026 · atualizados em 02/11/2026, … ·
base congelada para a apresentação". Em <http://127.0.0.1:8401/saude>, todas as tabelas devem estar com
`"estado": "congelada"` e o bloco `base_congelada` com `"manifesto": "valido"` e `"persistida": true`. No rodapé da
LIA: "Dados da LIA até 31/10/2026 · extraídos em …"; no Roadmap, Iniciativas e vídeo: "Conteúdo editorial · não depende
da carga de dados"; na Previsão: "… · acompanhamento até 01/11", sem o aviso de outra carga. Feche com Ctrl+C. O servidor da 8400 (`--reload`) relê `config.py` sozinho; a LIA e a
Previsão mudam ao reabrir a página.

## Passo 6: deploy

**Atualização de 31/10/2026 (D66, PRD_V2 seção 0):** os serviços já existem (`viu-agenciamento` e
`viu-agenciamento-restrito`). Na segunda, depois do passo 5:

1. No `Dockerfile`, troque `ARG CORTE_DADOS=off` por `ARG CORTE_DADOS=2026-10-31` (o build volta a conferir a base).
2. No PowerShell do computador, rode `tools\publicar_restrito.ps1 -Congelado` e `tools\publicar.ps1 -Congelado`.
3. Gere de novo a cópia da VPS (`python tools/gerar_espelho.py`), envie o ramo `vps` e mande o EasyPanel publicar de novo.
   Gere também o PDF e o PPT novos (`tools/exportar_paginas.mjs` + `tools/montar_pdf_ppt.py`).

As observações abaixo continuam valendo (o roteiro antigo citava `docs/deploy_iniciativas.md`):

- Antes do deploy, `app\base_congelada\` precisa ter o `manifesto.json` e a pasta `v-…` com os 10 `.parquet` (o passo 5
  deu "Tudo certo"), e `ml\saida\previsao.json` precisa ser o de 2026-10, da mesma carga. Se não estiver, o build para
  no passo `RUN python -m app.conferir_base` com "PACOTE REPROVADO" e a lista do que falta (nada é publicado).
- No `--set-env-vars` do bloco 6, acrescente `CORTE_DADOS=2026-10-31`. É o padrão do código; deixar explícito evita
  surpresa.
- Com a base na imagem, o portal **não consulta o BigQuery**, e o bloco 4b (permissões de BigQuery da conta de serviço)
  deixa de ser necessário para esta reunião.
- Depois do deploy, `/saude` (no navegador, logado) deve mostrar todas as tabelas com `"estado": "congelada"` e
  `base_congelada.manifesto = "valido"`, e o rodapé deve dizer "base congelada para a apresentação". Se a instância não
  subir, o log do Cloud Run mostra `BaseInvalida` com o motivo (a revisão anterior continua servindo).

## Depois da reunião: descongelar

1. **Computador:** acrescente `CORTE_DADOS=off` no `.env` da raiz (ou `$env:CORTE_DADOS = "off"` antes de subir o
   servidor) e reinicie. Sem o corte, vale de novo a D63: carga lida na subida, sem recarga por hora. Para recarregar a
   cada carga nova, use `CONGELAR=false`.
2. **Tirar a base do projeto:** mova `app\base_congelada\` para `_descartados\AAAA-MM-DD\app\base_congelada\` (fica fora
   da imagem) e registre uma linha no `LEIAME.md` de lá.
3. **Padrão do código:** em `app/config.py`, troque `os.environ.get("CORTE_DADOS", "2026-10-31")` por
   `os.environ.get("CORTE_DADOS", "off")` e registre no PRD (D65).
4. **Produção:** tire o serviço do ar (bloco 9 de `deploy_iniciativas.md`) ou faça um novo deploy com
   `CORTE_DADOS=off`. Nesse caso o portal volta a ler o BigQuery e a conta de serviço precisa do bloco 4b.
5. Para um novo corte (ex.: fim de novembro), basta `CORTE_DADOS=2026-11-30`. Base de outro corte é ignorada (K7).
6. Com o padrão do código em `"off"` (passo 3), o `RUN python -m app.conferir_base` do build não exige nada.

## Se algo der errado

- **"IGNORADA: … depois do corte"** no passo 2: a carga já passou de 01/11 (o portal ficou parado). A base de
  outubro exato não pode mais vir da gold (ela só guarda a carga atual). Decida com o Caio: aceitar a carga do dia,
  com `CORTE_FOLGA_DIAS` maior e o rodapé honesto ("Dados até …"), ou apresentar com a base anterior.
- **"base congelada das outras tabelas é de outra carga"**: alguma tabela congelou numa carga diferente (só em memória;
  nada é gravado pela metade). Reinicie o servidor da 8400 (ou rode o passo 2 num terminal novo) logo depois de uma carga.
- **"a base gravada é de outra carga"**: já existe uma base válida de outra carga. Mova `app\base_congelada\` inteira
  para `_descartados\…` e rode o passo 2 de novo.
- **Gravação interrompida** (computador desligou, Drive travou): rode `& $py tools\congelar_base.py --recuperar`. Ele
  publica a versão completa mais nova (pasta `v-…` com o manifesto interno conferido) e relata as parciais; sem versão
  completa, rode o passo 2 de novo enquanto a carga ainda estiver na folga.
- **"outro processo está gravando"** por mais de 15 min: a trava `.escrita.lock` ficou de um processo que morreu; a
  próxima tentativa a assume sozinha.
- **Refazer a base** (ex.: a carga de segunda veio errada e foi refeita à mão no mesmo dia, ainda com dados até
  01/11): mova a pasta para
  `_descartados\…` e rode o passo 2 de novo.
