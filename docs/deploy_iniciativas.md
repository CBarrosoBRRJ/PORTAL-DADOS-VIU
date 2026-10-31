# Deploy temporário para a reunião do gerente (Cloud Run + IAP), com as Iniciativas no Firestore

**Estado (31/10/2026):** roteiro pronto, **nada executado no GCP**. Quem roda é o Caio, um bloco por vez, conferindo a
saída antes do próximo. O Claude só fez o código e este roteiro (regra do projeto: GCP corporativo só consulta).

**Dados congelados em 31/10 (D65):** antes deste deploy, siga [congelar_outubro.md](congelar_outubro.md) (passos 1–5). A
imagem leva a base congelada (`app/base_congelada/`) e o retrato da Previsão (`ml/saida/previsao.json`, copiado pelo
`Dockerfile`). Com isso, o portal publicado **não consulta o BigQuery**, e o bloco 4b não é necessário para esta reunião.
No bloco 6, acrescente `CORTE_DADOS=2026-10-31` ao `--set-env-vars`.

**Objetivo:** publicar o portal V2 por pouco tempo, só para o gerente (e o Caio) apresentarem numa reunião sem o
computador do Caio ligado, e tirar do ar depois. Acesso **só por e-mail autorizado**, pelo **IAP** (Identity-Aware
Proxy) na frente do Cloud Run. Não é link público.

## 0. Antes de tudo: o que precisa ser verdade

| Item | Valor usado aqui | Onde veio | Conferir |
|---|---|---|---|
| Projeto | `gglobo-viu-dados-hdg-prd` | PRD, seção 2 | `gcloud config get-value project` |
| Região do Cloud Run | `us-central1` | PRD, seção 3 ("Hospedagem") | — |
| Serviço | `relatorios-agenciamento` | PRD, seção 3 e Q6 ("Caio confirma") | nome final é decisão do Caio |
| Conta de serviço | `relatorios-agenciamento@gglobo-viu-dados-hdg-prd.iam.gserviceaccount.com` | PRD, seção 3 e Q6 | `gcloud iam service-accounts describe …` |
| Bucket dos anexos | `gglobo-viu-dados-hdg-prd-iniciativas-anexos` (sugestão) | este roteiro | nome livre, globalmente único |
| Banco Firestore | `(default)`, modo nativo | este roteiro | ver bloco 2 |

**Exceção temporária à D10 (registrar no PRD se o Caio aprovar):** o controle de acesso próprio (fase 2: link por
e-mail) ainda não existe. Para esta publicação, a proteção é o **IAP** e o app roda com `AUTH=iap`:
- `AUTH=off` continua **recusado** em produção (o app não sobe; trava de `app/main.py`).
- `AUTH=iap` (novo, `app/iap.py`): o app só sobe com `IAP_AUDIENCE` definido e, em **toda** requisição, confere o
  cabeçalho assinado pelo IAP (`x-goog-iap-jwt-assertion`: assinatura ES256 com as chaves públicas do Google, emissor
  `https://cloud.google.com/iap` e público = `IAP_AUDIENCE`). Sem o cabeçalho válido, responde **401** a tudo,
  inclusive aos estáticos. Ou seja: mesmo que alguém chegasse ao serviço por outro caminho, não veria nada.
- **Chaves públicas do IAP (F06, 31/10/2026):** buscadas em segundo plano já na subida e renovadas fora do caminho da
  requisição (passada 1 h, uma thread busca de novo, com 3 tentativas). Se a renovação falhar, as chaves anteriores
  continuam valendo por até 24 h (o token continua sempre verificado pela assinatura). Sem chave utilizável, a busca é
  feita na hora, fora do event loop (`run_in_threadpool`). Respostas: **401** = token ausente ou inválido; **503**
  ("Verificação de acesso indisponível", `Retry-After: 30`) = chaves do IAP indisponíveis, com log
  `IAP: chaves indisponíveis` no Cloud Logging. Se aparecer 503, a instância não alcança `www.gstatic.com`.
- **`/saude` com IAP (A29, decisão de 31/10/2026):** **não fica isenta** do JWT (mostra a situação das tabelas, com
  datas e erros). Nenhuma sonda HTTP do Cloud Run usa `/saude`: o deploy fica com a **sonda de partida padrão (TCP na
  porta)**, que não passa pelo middleware. **Não acrescente** `--startup-probe`/`--liveness-probe` HTTP em `/saude`
  (com `AUTH=iap` ela daria 401 e o Cloud Run mataria a instância). Para conferir, abra `/saude` no navegador logado.
- Além disso, o serviço sobe com `--no-allow-unauthenticated` (só o IAP pode chamar o Cloud Run).
- **Edição das Iniciativas** (`INICIATIVAS_EDICAO=on`) só faz sentido com o IAP ativo: todo mundo que passa pelo IAP
  pode criar, editar, mover, excluir e anexar. O e-mail de quem gravou fica em `atualizado_por` e no log.

**Riscos e limites desta exceção:** (1) qualquer pessoa com o papel de acesso do IAP edita o quadro (não há perfis);
(2) se o IAP for desligado por engano, o app fecha (401), não abre; (3) o `IAP_AUDIENCE` errado também fecha tudo
(401) — confira no bloco 6; (4) é temporário: o bloco 9 tira do ar.

## 1. Ativar as APIs (uma vez)

Liga Firestore, Cloud Storage, IAP, Cloud Run, Cloud Build e Artifact Registry. Se já estiverem ligadas, o comando só
confirma.

```bash
gcloud services enable firestore.googleapis.com storage.googleapis.com iap.googleapis.com \
  run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com \
  --project=gglobo-viu-dados-hdg-prd
```

Esperado: `Operation ... finished successfully` (ou nada, se já estavam ligadas).

## 2. Banco do Firestore (modo nativo)

Primeiro, **só olhar** se o projeto já tem um banco Firestore:

```bash
gcloud firestore databases list --project=gglobo-viu-dados-hdg-prd
```

- **Nenhum banco:** criar o `(default)` em modo nativo. O `(default)` é o único que entra na cota gratuita do
  Firestore (PRD: sem custo extra). Local: `us-central1` (mesma região do Cloud Run). **Conferir na hora** se
  `us-central1` aparece na lista de locais do Firestore no console; se não aparecer, usar `nam5` (multirregião EUA).
  O local **não muda depois**.

  ```bash
  gcloud firestore databases create --database="(default)" --location=us-central1 --type=firestore-native \
    --project=gglobo-viu-dados-hdg-prd
  ```

- **Já existe um `(default)` usado por outro sistema:** não criar outro; usar o mesmo banco com um prefixo nas
  coleções, para não misturar: no deploy, `INICIATIVAS_PREFIXO=relatorios_` (as coleções viram
  `relatorios_iniciativas`, `relatorios_anexos`, `relatorios_iniciativas_meta`).
- **Já existe e está em modo Datastore:** parar e conversar (o app usa o modo nativo).

O app cria os documentos sozinho na 1ª leitura (semente = `catalogo.py`); não precisa importar nada.

## 3. Bucket privado dos anexos

Acesso uniforme (sem ACL por objeto) e **prevenção de acesso público** ligada. Os arquivos nunca são servidos direto
do bucket: o app lê e entrega (proxy), atrás do IAP.

```bash
gcloud storage buckets create gs://gglobo-viu-dados-hdg-prd-iniciativas-anexos \
  --project=gglobo-viu-dados-hdg-prd --location=us-central1 \
  --uniform-bucket-level-access --public-access-prevention
```

Conferir: `gcloud storage buckets describe gs://gglobo-viu-dados-hdg-prd-iniciativas-anexos --format="yaml(iamConfiguration,location)"`
→ `publicAccessPrevention: enforced` e `uniformBucketLevelAccess: enabled: true`.

## 4. Papéis mínimos da conta de serviço do Cloud Run

`SA=relatorios-agenciamento@gglobo-viu-dados-hdg-prd.iam.gserviceaccount.com`

**4a. Iniciativas.** Firestore (ler e gravar documentos) no projeto e objetos **só neste bucket**:

```bash
gcloud projects add-iam-policy-binding gglobo-viu-dados-hdg-prd \
  --member="serviceAccount:relatorios-agenciamento@gglobo-viu-dados-hdg-prd.iam.gserviceaccount.com" \
  --role="roles/datastore.user" --condition=None

gcloud storage buckets add-iam-policy-binding gs://gglobo-viu-dados-hdg-prd-iniciativas-anexos \
  --member="serviceAccount:relatorios-agenciamento@gglobo-viu-dados-hdg-prd.iam.gserviceaccount.com" \
  --role="roles/storage.objectAdmin"
```

**4b. Resto do portal (BigQuery), se a conta ainda não tiver.** O site lê as tabelas e views do `gold_monday` (D57) e
usa a Storage Read API. Primeiro **olhar** o que a conta já tem:

```bash
gcloud projects get-iam-policy gglobo-viu-dados-hdg-prd \
  --flatten="bindings[].members" --filter="bindings.members:relatorios-agenciamento@" --format="table(bindings.role)"
bq show --format=prettyjson gglobo-viu-dados-hdg-prd:gold_monday | grep -B2 -A2 relatorios-agenciamento
```

Se faltar: `roles/bigquery.jobUser` e `roles/bigquery.readSessionUser` no projeto e `roles/bigquery.dataViewer` **no
dataset** `gold_monday` (pelo console: BigQuery → `gold_monday` → Compartilhamento → Permissões → Adicionar principal).
As views do `gold_monday` leem tabelas do próprio dataset; se alguma view ler outro dataset, a conta precisa de leitura
lá também (ou a view precisa ser "autorizada"). A silver 2025 só é lida pelo job de ML, que não roda no Cloud Run.

```bash
gcloud projects add-iam-policy-binding gglobo-viu-dados-hdg-prd \
  --member="serviceAccount:relatorios-agenciamento@gglobo-viu-dados-hdg-prd.iam.gserviceaccount.com" \
  --role="roles/bigquery.jobUser" --condition=None
gcloud projects add-iam-policy-binding gglobo-viu-dados-hdg-prd \
  --member="serviceAccount:relatorios-agenciamento@gglobo-viu-dados-hdg-prd.iam.gserviceaccount.com" \
  --role="roles/bigquery.readSessionUser" --condition=None
```

## 5. Número do projeto (para o público do IAP)

Só leitura:

```bash
gcloud projects describe gglobo-viu-dados-hdg-prd --format="value(projectNumber)"
```

Anote o número (`NUMERO` abaixo). O público (`IAP_AUDIENCE`) do IAP direto no Cloud Run tem a forma
`/projects/NUMERO/locations/us-central1/services/relatorios-agenciamento` — **conferir na hora** na documentação
oficial ("Securing your app with signed headers", seção Cloud Run); o bloco 7 mostra como confirmar no próprio log.

## 6. Deploy com IAP e as variáveis

Na raiz da V2. O `.gcloudignore` (envio ao Cloud Build) e o `.dockerignore` (contexto da imagem), iguais, deixam de
fora `docs/`, `tests/`, `tools/`, banco local e anexos, `_congelado/`, `_descartados/`, `.playwright-mcp/` (~112 MB),
`.taste-skill/`, os protótipos `app/static/roadmap_proto/` (F17/A33, 31/10/2026: ficam no disco, não vão para a
imagem) e todo o `ml/` menos `ml/saida/previsao.json` (o único arquivo de `ml/` que o `Dockerfile` copia; antes iam
~6 MB de backtests). O `Dockerfile` copia `app/` e o retrato da Previsão.
**Conferir na hora** a sintaxe vigente do IAP direto no Cloud Run (em 2025 era `gcloud beta run deploy ... --iap`;
se já for GA, `gcloud run deploy ... --iap`). `--max-instances=1` na reunião: uma instância só evita qualquer disputa
de ordem entre réplicas nas edições simultâneas.

**Desempenho (31/10/2026): `--min-instances=1` e `--cpu-boost` na reunião.** Com `--min-instances=0`, a 1ª página
depois de alguns minutos parados paga a partida a frio: subir o contêiner, importar pandas e o app, ler a base
congelada e aquecer as contas e os templates (`ao_iniciar` em `app/main.py`), vários segundos com o gerente esperando
na frente da diretoria. Com uma instância sempre ligada, toda troca de página cai num processo quente (contas guardadas
por carga, templates compilados). `--cpu-boost` dá CPU extra só durante a partida (deploy novo ou reinício). Custo: a
instância ociosa é cobrada enquanto o serviço estiver no ar; **voltar a `--min-instances=0` (ou tirar do ar, seção 9)
depois da reunião**. Conferir antes da reunião: abrir o link uma vez (aquece a sessão do IAP e o navegador) e passar
pelas páginas na ordem.

```bash
gcloud beta run deploy relatorios-agenciamento --source . \
  --project=gglobo-viu-dados-hdg-prd --region=us-central1 \
  --service-account=relatorios-agenciamento@gglobo-viu-dados-hdg-prd.iam.gserviceaccount.com \
  --no-allow-unauthenticated --iap \
  --min-instances=1 --max-instances=1 --cpu-boost \
  --set-env-vars="AUTH=iap,IAP_AUDIENCE=/projects/NUMERO/locations/us-central1/services/relatorios-agenciamento,INICIATIVAS_BACKEND=firestore,INICIATIVAS_BUCKET=gglobo-viu-dados-hdg-prd-iniciativas-anexos,INICIATIVAS_EDICAO=on"
```

Depois, o IAP precisa poder chamar o serviço (agente de serviço do IAP com `run.invoker`). **Conferir na hora** se o
`--iap` já faz isso sozinho; se não:

```bash
gcloud run services add-iam-policy-binding relatorios-agenciamento --region=us-central1 \
  --project=gglobo-viu-dados-hdg-prd \
  --member="serviceAccount:service-NUMERO@gcp-sa-iap.iam.gserviceaccount.com" --role="roles/run.invoker"
```

## 7. Quem entra: o gerente e o Caio

Papel `roles/iap.httpsResourceAccessor` para os dois e-mails corporativos (trocar `GERENTE@viu.com.br`):

```bash
for EMAIL in GERENTE@viu.com.br caio.barroso@viu.com.br; do
  gcloud beta iap web add-iam-policy-binding \
    --project=gglobo-viu-dados-hdg-prd --region=us-central1 \
    --resource-type=cloud-run --service=relatorios-agenciamento \
    --member="user:$EMAIL" --role="roles/iap.httpsResourceAccessor"
done
```

Conferir: `gcloud beta iap web get-iam-policy --project=gglobo-viu-dados-hdg-prd --region=us-central1 --resource-type=cloud-run --service=relatorios-agenciamento`.

**Se aparecer "401 Acesso só pelo endereço protegido (IAP)" para alguém já autorizado:** o `IAP_AUDIENCE` não bate.
No Cloud Logging do serviço não aparece o token (não é registrado); confira o público no console do IAP (Security →
Identity-Aware Proxy → o serviço → "Get JWT audience code") e refaça só as variáveis:

```bash
gcloud run services update relatorios-agenciamento --region=us-central1 --project=gglobo-viu-dados-hdg-prd \
  --update-env-vars="IAP_AUDIENCE=<público copiado do console>"
```

## 8. Verificação depois do deploy

```bash
gcloud run services describe relatorios-agenciamento --region=us-central1 --project=gglobo-viu-dados-hdg-prd \
  --format="yaml(status.url,spec.template.spec.serviceAccountName,spec.template.spec.containers[0].env)"
gcloud run services logs read relatorios-agenciamento --region=us-central1 --project=gglobo-viu-dados-hdg-prd --limit=50
```

- `curl -s -o /dev/null -w "%{http_code}" <URL>/saude` sem login → **302/401/403** (IAP barrando). Se der 200 sem
  login, **parar**: o IAP não está na frente.
- No navegador, com o e-mail autorizado: a capa abre.

### Checklist "pronto para a reunião" (no link publicado)

- [ ] Todas as páginas abrem (Capa → Roadmap → Demanda → Talentos → SLA → LIA → Iniciativas → Previsão → Encerramento).
- [ ] Capa (animação), Roadmap (painel de imagens), estudo "Como medimos" (5 slides) e o pop-up do vídeo da LIA
      funcionam. **Atenção:** o vídeo hoje é "a incluir" (`lia_na_pratica/__init__.py`, `ARQUIVO = ""`); sem o MP4
      em `app/static/video/`, o pop-up mostra o espaço reservado. O botão "A LIA na prática" fica **sempre visível**,
      mesmo sem o vídeo (decisão do Caio, 31/10/2026, F09).
- [ ] Dados do BigQuery carregam com a conta de serviço (rodapé "Dados até … · atualizados em …"; `/saude` com
      `dados_prontos: true` — acessar pelo navegador logado).
- [ ] **Previsão:** desde a D65 (31/10/2026), o `Dockerfile` copia `ml/saida/previsao.json` para a imagem (o build
      falha sem o arquivo). Confira que a página mostra o retrato de outubro.
- [ ] **Base congelada (D65):** o rodapé diz "Dados até 31/10/2026 · … · base congelada para a apresentação", e
      `/saude` mostra todas as tabelas com `"estado": "congelada"` (nenhuma consulta ao BigQuery).
- [ ] Iniciativas: criar uma de teste, editar, arrastar, anexar uma imagem e um PDF, abrir a galeria e o visor,
      "Expandir", recarregar (persistiu), abrir em outro navegador (aparece), excluir a de teste.
- [ ] O gerente entra com o e-mail dele (testar com ele antes do dia, ou numa janela anônima com a conta dele).
- [ ] Desligar o computador do Caio e abrir de novo pelo celular ou outra máquina: continua no ar.

## 9. Tirar do ar depois da reunião

Escolha uma das duas:

- **Tirar o acesso e manter o serviço** (dá para religar rápido):

  ```bash
  gcloud beta iap web remove-iam-policy-binding --project=gglobo-viu-dados-hdg-prd --region=us-central1 \
    --resource-type=cloud-run --service=relatorios-agenciamento \
    --member="user:GERENTE@viu.com.br" --role="roles/iap.httpsResourceAccessor"
  ```

- **Apagar o serviço** (some o link; Firestore e bucket ficam, com as edições e os anexos):

  ```bash
  gcloud run services delete relatorios-agenciamento --region=us-central1 --project=gglobo-viu-dados-hdg-prd
  ```

Os dados das Iniciativas ficam no Firestore e no bucket até o Caio decidir. Backup antes de apagar qualquer coisa:

```bash
gcloud firestore export gs://gglobo-viu-dados-hdg-prd-iniciativas-anexos/backup-firestore \
  --collection-ids=iniciativas,anexos,iniciativas_meta --project=gglobo-viu-dados-hdg-prd
gcloud storage cp -r gs://gglobo-viu-dados-hdg-prd-iniciativas-anexos/anexos ./backup-anexos
```

(O export do Firestore precisa que a conta de quem roda tenha `roles/datastore.importExportAdmin`.)

## Opções de proteção (para depois desta reunião)

| Opção | Edição das Iniciativas | Esforço | Observação |
|---|---|---|---|
| **IAP na frente do Cloud Run** (este roteiro) | `INICIATIVAS_EDICAO=on` | baixo | acesso por e-mail Google; todos os autorizados editam |
| **Cloud Run autenticado sem IAP** (`--no-allow-unauthenticated`, `roles/run.invoker` por pessoa) | `on` só se `AUTH=iap` não for usado: **não suportado** hoje pelo app | médio | o navegador não manda token sozinho; serve para chamadas de máquina, não para o gerente abrir no navegador |
| **Login do portal (fase 2, link por e-mail)** | `on`, com perfis (quem edita × quem só lê) | alto | o desenho já está no PRD (D10–D12); é o destino definitivo |
| **Publicado sem nada** | proibido (D10) | — | o app não sobe com `AUTH=off` em produção |

## Variáveis de ambiente (Iniciativas e acesso)

| Variável | Padrão no computador | Padrão no Cloud Run | Para que serve |
|---|---|---|---|
| `INICIATIVAS_BACKEND` | `sqlite` | `firestore` | onde o quadro mora |
| `INICIATIVAS_DB` | `~/.ppd-agenciamento-v2/iniciativas.db` | (não usado) | arquivo SQLite, **fora do Google Drive** |
| `INICIATIVAS_ANEXOS` | `~/.ppd-agenciamento-v2/anexos` | (não usado) | pasta dos anexos locais |
| `INICIATIVAS_FIRESTORE_DB` | `(default)` | `(default)` | banco do Firestore |
| `INICIATIVAS_PREFIXO` | vazio | vazio | prefixo das coleções (bloco 2) |
| `INICIATIVAS_BUCKET` | vazio | **obrigatório** | bucket dos anexos |
| `INICIATIVAS_EDICAO` | `on` | `off` | escrita pela API; `on` em produção só com IAP |
| `AUTH` | `off` | `iap` (este roteiro) | `off` é recusado em produção |
| `IAP_AUDIENCE` | vazio | **obrigatório com `AUTH=iap`** | público esperado no JWT do IAP |
| `SINC` | `off` (V2) | `off` (sempre) | sincronia com a cola do apresentador; `on` só no computador |

## Dependências fora das Iniciativas (só apontadas; nada foi mudado)

1. **BigQuery:** a conta de serviço precisa de leitura no `gold_monday` e de `jobUser`/`readSessionUser` (bloco 4b).
   O `checar_reuniao.py` usa as credenciais do Caio, não as da conta de serviço.
2. **Previsão (resolvido na D65, 31/10/2026):** o `Dockerfile` ganhou `COPY ml/saida/previsao.json
   ./ml/saida/previsao.json`, o mesmo caminho padrão do `config.PREVISAO_ARQ` (`/app/ml/saida/previsao.json`), sem
   variável nova. Em produção o job de ML não roda (`PREVISAO_JOB` desligado com `K_SERVICE`); o retrato vem pronto
   do computador (`python -m ml.rodar --rotina`, passo 3 de `congelar_outubro.md`).
3. **LIA:** lê `app/apresentacoes/gestao_orcamentos/lia/retrato.json`, que já está dentro de `app/` (entra na imagem).
4. **Vídeo da LIA:** `ARQUIVO = ""` (espaço reservado); o MP4 precisa estar em `app/static/video/` antes do deploy.
5. **Base congelada e sincronia:** `CONGELAR` e `SINC` ficam desligados sozinhos em produção (`K_SERVICE`); a cola do
   apresentador (porta 8200) não funciona no link publicado. Na V2, `SINC` vem **desligado por padrão também no
   computador** (F12/A32, 31/10/2026; ligar só com `SINC=on`) e o `POST /sinc` aceita só a mesma origem ou as da cola
   (`SINC_ORIGENS`); de outra origem, 403. O **corte da D65** (`CORTE_DADOS`) vale também em
   produção: com `app/base_congelada/` na imagem, o serviço lê só desses arquivos (sem BigQuery) e nada é gravado.
