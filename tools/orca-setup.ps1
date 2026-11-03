# tools/orca-setup.ps1 — prepara um worktree novo do Orca (copia arquivos fora do Git)
$ErrorActionPreference = 'Stop'
$principal = (Resolve-Path (Split-Path (git rev-parse --path-format=absolute --git-common-dir) -Parent)).Path
$aqui = (Resolve-Path (git rev-parse --show-toplevel)).Path
if ($principal -eq $aqui) { 'Repositório principal: nada a copiar.'; exit 0 }
foreach ($f in @('.env')) {
  $origem = Join-Path $principal $f
  if (Test-Path -LiteralPath $origem) { Copy-Item -LiteralPath $origem -Destination (Join-Path $aqui $f) -Force; "copiado: $f" }
}