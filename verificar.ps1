# verificar.ps1 — Definição de pronto deste projeto (lint e testes). Saída 0 = tudo passou.
# Usado pelo pre-commit do Git e pelo hook "pronto" do Claude Code. Ajuste as etapas ao projeto.
$ErrorActionPreference = 'Continue'
Set-Location -LiteralPath $PSScriptRoot
$falhas = [System.Collections.Generic.List[string]]::new()
$avisos = [System.Collections.Generic.List[string]]::new()
function Etapa([string]$nome, [scriptblock]$acao) {
  Write-Host "== $nome" -ForegroundColor Cyan
  & $acao
  if ($LASTEXITCODE -ne 0) { $falhas.Add($nome) }
}
# Nome do repositório principal: funciona também dentro de worktrees do Orca
$comum = git rev-parse --path-format=absolute --git-common-dir 2>$null
$nome = if ($comum) { Split-Path (Split-Path $comum -Parent) -Leaf } else { Split-Path $PSScriptRoot -Leaf }
$cands = @()
if ($env:VERIFICAR_PYTHON) { $cands += $env:VERIFICAR_PYTHON }
$cands += '.venv\Scripts\python.exe', 'venv\Scripts\python.exe', (Join-Path $HOME ".venvs\$nome\Scripts\python.exe")
$cands += Get-ChildItem (Join-Path $HOME '.venvs') -Directory -ErrorAction SilentlyContinue | Where-Object { $nome -like "$($_.Name)*" } | Sort-Object { $_.Name.Length } -Descending | ForEach-Object { Join-Path $_.FullName 'Scripts\python.exe' }
$py = $cands | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $py) { $py = 'python' }
$temPython = (Test-Path 'pyproject.toml') -or (Test-Path 'requirements.txt') -or [bool](Get-ChildItem -Filter '*.py' -File -ErrorAction SilentlyContinue)
if ($temPython) {
  & $py -m ruff --version *> $null
  if ($LASTEXITCODE -eq 0) {
    # Lint só nos .py alterados (vs HEAD + novos). VERIFICAR_LINT_TUDO=1 força o projeto inteiro.
    $alterados = @(@(git -c core.quotepath=off diff --name-only --diff-filter=ACMR HEAD -- '*.py' 2>$null) +
                   @(git -c core.quotepath=off ls-files --others --exclude-standard -- '*.py' 2>$null) |
                   Where-Object { $_ -and (Test-Path -LiteralPath $_ -PathType Leaf) } | Sort-Object -Unique)
    if ($env:VERIFICAR_LINT_TUDO -eq '1') { Etapa 'ruff (lint, projeto inteiro)' { & $py -m ruff check . } }
    elseif ($alterados.Count) { Etapa "ruff (lint, $($alterados.Count) arquivo(s) alterado(s))" { & $py -m ruff check -- $alterados } }
    else { Write-Host '== ruff: nenhum .py alterado' -ForegroundColor Cyan }
  } else { $avisos.Add('ruff não instalado no ambiente do projeto: lint não executado') }
  if ((Test-Path 'tests') -or (Test-Path 'test')) {
    & $py -m pytest --version *> $null
    if ($LASTEXITCODE -eq 0) {
      $pastaTestes = if (Test-Path 'tests') { 'tests' } else { 'test' }
      # Caio, 03/11/2026: testes em paralelo (pytest-xdist) com VERIFICAR_PROCESSOS processos (padrão 8: no Google Drive,
      # mais que isso fica mais lento). Modo rápido (VERIFICAR_RAPIDO=1, usado pelo hook de fim de resposta): sem pytest
      # quando só mudaram documentos (.md/.txt); o pre-commit continua com a verificação completa
      $mudados = @(@(git -c core.quotepath=off diff --name-only HEAD 2>$null) + @(git -c core.quotepath=off ls-files --others --exclude-standard 2>$null) | Where-Object { $_ })
      $soDocs = $mudados.Count -and -not ($mudados | Where-Object { $_ -notmatch '\.(md|txt)$' })
      if ($env:VERIFICAR_RAPIDO -eq '1' -and $soDocs) {
        Write-Host '== pytest: só documentos alterados (modo rápido), testes não executados' -ForegroundColor Cyan
      } else {
        $par = @()
        & $py -c "import xdist" *> $null
        if ($LASTEXITCODE -eq 0) { $n = if ($env:VERIFICAR_PROCESSOS) { $env:VERIFICAR_PROCESSOS } else { '8' }; $par = @('-n', $n) }
        Etapa "pytest $pastaTestes" { & $py -m pytest $pastaTestes -q -p no:cacheprovider @par }
      }
    } else { $falhas.Add('pytest ausente, mas o projeto tem testes') }
  }
}
if (Test-Path 'package.json') {
  $pkg = (Get-Content 'package.json' -Raw | ConvertFrom-Json).scripts
  foreach ($s in 'lint', 'typecheck', 'test') {
    if ($pkg -and $pkg.PSObject.Properties.Name -contains $s) { Etapa "npm run $s" { npm run $s --silent } }
  }
}
$avisos | ForEach-Object { Write-Warning $_ }
if ($falhas.Count) { Write-Host "FALHOU: $($falhas -join ', ')" -ForegroundColor Red; exit 1 }
Write-Host 'OK: todas as verificações configuradas passaram.' -ForegroundColor Green
exit 0