# Publica (ou republica) o portal no Cloud Run — D66, 31/10/2026. Rodar no PowerShell DO COMPUTADOR (não no Cloud Shell):
#   & "G:\Meu Drive\Workspace\globo\scripts\PPD-AGENCIAMENTO-SLA-V2\tools\publicar.ps1"
# Link aberto (AUTH=publico, só leitura) e gold ao vivo (CORTE_DADOS=off) até a carga de 02/11/2026. Na segunda, depois
# de congelar (docs/congelar_outubro.md): rodar com -Congelado (corte 2026-10-31; trocar também o ARG do Dockerfile).
# Mesmo nome de serviço = mesmo link; o Cloud Run mantém a revisão anterior se a nova não subir.
# Link aberto: a org bloqueia --no-invoker-iam-check (constraints/run.managed.requireInvokerIam, 31/10/2026); o Caio
# escolheu tentar o papel run.invoker para allUsers (--allow-unauthenticated). Se a org também barrar, o serviço fica
# fechado e a saída é o AUTH=iap (docs/deploy_iniciativas.md).
param([switch]$Congelado)

$ErrorActionPreference = "Stop"
$env:CLOUDSDK_CONFIG = "C:\Users\CCMB\AppData\Roaming\gcloud-viu"
Set-Location (Split-Path $PSScriptRoot -Parent)

$corte = if ($Congelado) { "2026-10-31" } else { "off" }
$conta = gcloud config get-value account 2>$null
Write-Host "Conta: $conta | projeto: gglobo-viu-dados-hdg-prd | corte: $corte | pasta: $(Get-Location)" -ForegroundColor Cyan
if ($conta -ne "caio.barroso@viu.com.br") { throw "Conta errada no gcloud: rode 'gcloud auth login caio.barroso@viu.com.br'." }

gcloud run deploy viu-agenciamento `
  --source . `
  --region us-central1 `
  --project gglobo-viu-dados-hdg-prd `
  --service-account viu-agenciamento@gglobo-viu-dados-hdg-prd.iam.gserviceaccount.com `
  --allow-unauthenticated `
  --min-instances 1 --max-instances 3 `
  --memory 2Gi --cpu 1 --cpu-boost --timeout 300 `
  --set-env-vars "AUTH=publico,CORTE_DADOS=$corte,MODO=apresentacao,INICIATIVAS_BACKEND=firestore,INICIATIVAS_BUCKET=gglobo-viu-dados-hdg-prd-viu-agenciamento-anexos" `
  --labels "projeto=ppd-agenciamento-sla,app=viu-agenciamento" `
  --quiet
