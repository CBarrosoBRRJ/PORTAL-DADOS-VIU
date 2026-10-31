# Link 2 (D66, 31/10/2026): o mesmo portal atrás do IAP (login Google), só para os e-mails de $EMAILS, com edição das
# Iniciativas ligada (mesmo Firestore/bucket do link aberto). Rodar no PowerShell DO COMPUTADOR (não no Cloud Shell):
#   pwsh -ExecutionPolicy Bypass -File "G:\Meu Drive\Workspace\globo\scripts\PPD-AGENCIAMENTO-SLA-V2\tools\publicar_restrito.ps1"
# Gold ao vivo (CORTE_DADOS=off) até a carga de 02/11/2026; na segunda, -Congelado (docs/congelar_outubro.md).
# Incluir alguém depois: rodar de novo com o e-mail na lista (o deploy é o mesmo; as permissões só se somam).
param([switch]$Congelado)

$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $true  # gcloud com erro para o roteiro (não segue para o passo seguinte)
$env:CLOUDSDK_CONFIG = "C:\Users\CCMB\AppData\Roaming\gcloud-viu"
Set-Location (Split-Path $PSScriptRoot -Parent)

$PROJETO = "gglobo-viu-dados-hdg-prd"; $NUMERO = "241421786646"; $REGIAO = "us-central1"
$SERVICO = "viu-agenciamento-restrito"
$EMAILS = @("caio.barroso@viu.com.br", "gustavo.siano@viu.com.br", "cristina.andrade@viu.com.br", "renata.fernandes@g.globo")
$corte = if ($Congelado) { "2026-10-31" } else { "off" }
$conta = gcloud config get-value account 2>$null
Write-Host "Conta: $conta | projeto: $PROJETO | serviço: $SERVICO | corte: $corte" -ForegroundColor Cyan
if ($conta -ne "caio.barroso@viu.com.br") { throw "Conta errada no gcloud: rode 'gcloud auth login caio.barroso@viu.com.br'." }

Write-Host "`n[1/3] Publicando o serviço com IAP (5 a 10 min)..." -ForegroundColor Cyan
gcloud run deploy $SERVICO `
  --source . `
  --region $REGIAO `
  --project $PROJETO `
  --service-account "viu-agenciamento@$PROJETO.iam.gserviceaccount.com" `
  --no-allow-unauthenticated --iap `
  --min-instances 1 --max-instances 3 `
  --memory 2Gi --cpu 1 --cpu-boost --timeout 300 `
  --set-env-vars "AUTH=iap,IAP_AUDIENCE=/projects/$NUMERO/locations/$REGIAO/services/$SERVICO,CORTE_DADOS=$corte,MODO=apresentacao,INICIATIVAS_BACKEND=firestore,INICIATIVAS_BUCKET=gglobo-viu-dados-hdg-prd-viu-agenciamento-anexos,INICIATIVAS_EDICAO=on" `
  --labels "projeto=ppd-agenciamento-sla,app=viu-agenciamento" `
  --quiet

Write-Host "`n[2/3] Deixando o IAP chamar o serviço..." -ForegroundColor Cyan
gcloud run services add-iam-policy-binding $SERVICO --region $REGIAO --project $PROJETO `
  --member "serviceAccount:service-$NUMERO@gcp-sa-iap.iam.gserviceaccount.com" --role "roles/run.invoker" `
  --format "value(etag)" --quiet

Write-Host "`n[3/3] Liberando os e-mails no IAP..." -ForegroundColor Cyan
foreach ($e in $EMAILS) {
  gcloud iap web add-iam-policy-binding --project $PROJETO --region $REGIAO --resource-type cloud-run `
    --service $SERVICO --member "user:$e" --role "roles/iap.httpsResourceAccessor" --format "value(etag)" --quiet
  Write-Host "  ok: $e"
}
$url = gcloud run services describe $SERVICO --region $REGIAO --project $PROJETO --format "value(status.url)"
Write-Host "`nLink restrito: $url/viu-agenciamento/capa" -ForegroundColor Green
