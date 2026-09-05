# scripts/dev/setup_hooks.ps1
# Instala pre-commit hooks de forma reproducible
# Uso: .\scripts\dev\setup_hooks.ps1

$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $repoRoot

Write-Host ""
Write-Host "=== Custodio RAT — Setup de Git Hooks ===" -ForegroundColor Cyan
Write-Host "Repo: $repoRoot" -ForegroundColor Gray
Write-Host ""

$pyAvailable = Get-Command python -ErrorAction SilentlyContinue
$pipAvailable = Get-Command pip -ErrorAction SilentlyContinue

if ($pyAvailable -and $pipAvailable) {
    Write-Host "[1/4] Instalando pre-commit..." -ForegroundColor Yellow
    pip install pre-commit 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "    OK: pre-commit instalado" -ForegroundColor Green
    } else {
        Write-Host "    FALLA: No se pudo instalar pre-commit" -ForegroundColor Red
        Write-Host "    Verificar que pip este disponible" -ForegroundColor Gray
    }

    Write-Host "[2/4] Verificando .pre-commit-config.yaml..." -ForegroundColor Yellow
    if (Test-Path ".pre-commit-config.yaml") {
        Write-Host "    OK: .pre-commit-config.yaml existe" -ForegroundColor Green
    } else {
        Write-Host "    FALLA: .pre-commit-config.yaml no encontrado" -ForegroundColor Red
    }

    Write-Host "[3/4] Instalando pre-commit hooks..." -ForegroundColor Yellow
    pre-commit install 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "    OK: pre-commit install exitoso" -ForegroundColor Green
    } else {
        Write-Host "    FALLA: pre-commit install falló" -ForegroundColor Red
    }

    Write-Host "[4/4] Instalando commit-msg hook..." -ForegroundColor Yellow
    pre-commit install --hook-type commit-msg 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "    OK: commit-msg hook instalado" -ForegroundColor Green
    } else {
        Write-Host "    FALLA: commit-msg hook falló" -ForegroundColor Red
    }
} else {
    Write-Host "Python/pip no encontrado. Saltando instalacion de pre-commit." -ForegroundColor Yellow
    Write-Host "Instalar manualmente:" -ForegroundColor Yellow
    Write-Host "  pip install pre-commit" -ForegroundColor Gray
    Write-Host "  pre-commit install" -ForegroundColor Gray
    Write-Host "  pre-commit install --hook-type commit-msg" -ForegroundColor Gray
}

Write-Host ""
Write-Host "[OK] Setup de hooks completo" -ForegroundColor Green
Write-Host ""
Write-Host "Para ejecutar hooks manualmente:" -ForegroundColor Cyan
Write-Host "  pre-commit run --all-files" -ForegroundColor Gray
Write-Host ""
