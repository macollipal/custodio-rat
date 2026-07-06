# scripts/maintenance/pre_commit_docs_check.ps1
# Hook de pre-commit para Windows PowerShell (alternativa al framework pre-commit)
# Bloquea: lock files (~$*.docx), mojibake en .md, APDP en archivos operacionales.
#
# Instalacion:
#   copy scripts\maintenance\pre_commit_docs_check.ps1 .git\hooks\pre-commit
#   O ejecutar desde Git Bash con: ./scripts/maintenance/pre_commit_docs_check.ps1

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$ErrorActionPreference = "Stop"

# Obtener archivos en staging
$stagedFiles = git diff --cached --name-only --diff-filter=AM

if (-not $stagedFiles) {
    exit 0
}

$exitCode = 0

Write-Host "[pre-commit-docs] Verificando $($stagedFiles.Count) archivos en staging..." -ForegroundColor Cyan

# Check 1: Lock files de Office
$lockFiles = $stagedFiles | Where-Object { $_ -match '^\$\.?[A-Za-z].*\.(docx|doc|xls|xlsx)$' -or $_ -like '~*' }
if ($lockFiles) {
    Write-Host ""
    Write-Host "[ERROR] Lock files detectados (cerrar Word/Excel antes de commitear):" -ForegroundColor Red
    $lockFiles | ForEach-Object { Write-Host "  - $_" -ForegroundColor Yellow }
    $exitCode = 1
}

# Check 2: Mojibake en archivos .md en staging
$mdFiles = $stagedFiles | Where-Object { $_ -like "*.md" -and (Test-Path $_) }
foreach ($file in $mdFiles) {
    $content = Get-Content -Path $file -Raw -Encoding UTF8 -ErrorAction SilentlyContinue
    if (-not $content) { continue }

    # Patron de mojibake (3+ caracteres seguidos) — usamos escape Unicode para evitar issues de encoding
    # Caracteres: U+00C3 (Ã), U+00E2 (â), U+00F0 (ð), U+0178 (Ÿ), U+00C2 (Â), U+FFFD (ï¿½ = replacement)
    $mojibakePattern = '[\u00C3\u00E2\u00F0\u0178\u00C2]{3,}|\uFFFD'
    if ($content -match $mojibakePattern) {
        # Verificar que no sea solo texto descriptivo (e.g., documentacion que explica que es mojibake)
        $lines = $content -split "`n"
        $lineNum = 0
        $found = $false
        foreach ($line in $lines) {
            $lineNum++
            $lower = $line.ToLower()
            # Heuristica: lineas que describen el mojibake en si
            if ($lower -match 'mojibake|encoding|utf-8|detec|busc' -and $lower -match 'reemplaz|corregi|normali') {
                continue
            }
            if ($line -match $mojibakePattern) {
                Write-Host "[ERROR] Posible mojibake en ${file}:${lineNum}" -ForegroundColor Red
                Write-Host "  $($line.Substring(0, [Math]::Min(120, $line.Length)).Trim())" -ForegroundColor Yellow
                $found = $true
            }
        }
        if ($found) { $exitCode = 1 }
    }
}

# Check 3: APDP en archivos operacionales (no historicos)
$historicos = @(
    "docs/consultoria/",
    "docs/auditorias/2026-05-",
    "docs/auditorias/2026-06-",
    "docs/SESSION_STATE.md",
    "docs/backlog_seguimiento.md",
    "docs/CLEANUP_2026-",
    "BARRIDO_DOCUMENTAL"
)

foreach ($file in $mdFiles) {
    $normalized = $file -replace '\\', '/'
    $isHistoric = $false
    foreach ($prefix in $historicos) {
        if ($normalized.StartsWith($prefix)) {
            $isHistoric = $true
            break
        }
    }
    if ($isHistoric) { continue }

    $content = Get-Content -Path $file -Raw -Encoding UTF8 -ErrorAction SilentlyContinue
    if (-not $content) { continue }

    # Remover bloques de codigo antes de buscar APDP
    $contentNoCode = $content -replace '```[\s\S]*?```', '' -replace '`[^`]+`', ''

    $apdpMatches = [regex]::Matches($contentNoCode, 'APDP')
    if ($apdpMatches.Count -gt 0) {
        Write-Host "[ERROR] APDP usado en archivo operacional: $file ($($apdpMatches.Count)x). Usar APDC." -ForegroundColor Red
        $exitCode = 1
    }
}

if ($exitCode -eq 0) {
    Write-Host "[pre-commit-docs] OK" -ForegroundColor Green
}

exit $exitCode