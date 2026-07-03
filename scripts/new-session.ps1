# scripts/new-session.ps1
# Genera docs/SESSION_STATE.md para continuar la sesion en otra instancia de opencode
# Uso: .\scripts\new-session.ps1

$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

$branch = git rev-parse --abbrev-ref HEAD 2>$null
$lastCommits = git log --oneline -15 2>$null
$status = git status --short 2>$null

$pendingTodos = @"
- Fase 2: 5 skills de compliance (rat-compliance, breach-management, arco-rights, multi-tenant-security, api-review)
- Fase 3: CI/CD (.github/workflows/, .pre-commit-config.yaml, cobertura tests)
- Fase 4: Track E (QW3-QW6: score empresa, exports, SLA alerts, ficha tabs)
- Limpieza: ~104 RATs en BD (duplicados)
"@

$skillsActivas = @"
- security-secret-scan, commit-helper, tester-rat, custodio-auditoria
- qa-senior, architect-senior, deploy-cors-multienv, debug-login
- frontend-guardian, equipo-compuesto
"@

$leyesDivinas = @"
- NO secrets en git (NUNCA hardcodear passwords, API keys, tokens)
- Variables de entorno para TODA credencial (DATABASE_URL, JWT_SECRET, etc.)
- Pre-commit hook con gitleaks BLOQUEA cualquier secret antes de commit
- .env.example documenta todas las variables requeridas
"@

$sessionContent = @"
# Session State - Custodio RAT

**Generado:** $(Get-Date -Format 'yyyy-MM-dd HH:mm')
**Branch:** $branch

## Ultimos 15 commits
$lastCommits

## Working tree status
$status

## Proximos pasos (prioridad alta)
$pendingTodos

## Skills activas (vinculadas en CLAUDE.md / AGENTS.md)
$skillsActivas

## LEYES DIVINAS (no negociar)
$leyesDivinas

## Commits de la sesion anterior (Fase 0 - Higiene)
1. e2b9ab0  fix(skills): corregir ley 21.663 -> 21.719 en qa-senior
2. 2c30308  chore(skills): eliminar arquitecto-test (meta-prompt obsoleto)
3. 7ea7d85  chore(skills): archivar Experto-Senior-OCI como deprecated
4. 487d840  chore(skills): renombrar soluciona_cors -> deploy-cors-multienv
5. deed884  docs(skills): vincular 8 skills a backend/CLAUDE.md
6. 17bc516  docs(skills): vincular 4 skills a frontend-next/AGENTS.md

## Fase 2 - Skills de compliance (proxima sesion)
| Skill | Proposito |
|-------|-----------|
| rat-compliance | Valida Art. 16, campos obligatorios (7+3), EIPD |
| breach-management | Valida notificacion 72h a APDC por brecha |
| arco-rights | Workflow ARCO completo + plazos (10 dias habiles) |
| multi-tenant-security | RBAC + IDOR en multi-tenant |
| api-review | Transversal para nuevos endpoints |

## Como continuar
1. Cerrar opencode actual
2. Abrir nueva sesion: opencode .
3. Escribir: "Lee docs/SESSION_STATE.md. Que hay pendiente?"
"@

$outPath = Join-Path $repoRoot 'docs/SESSION_STATE.md'
Set-Content -Path $outPath -Value $sessionContent -Encoding UTF8

Write-Host ''
Write-Host 'SESSION_STATE.md generado en docs/' -ForegroundColor Green
Write-Host "Branch: $branch" -ForegroundColor Cyan
Write-Host ''
Write-Host 'Proximos pasos pendientes:' -ForegroundColor Yellow
Write-Host '  - Fase 2: 5 skills de compliance' -ForegroundColor White
Write-Host '  - Fase 3: CI/CD + cobertura tests' -ForegroundColor White
Write-Host '  - Fase 4: Track E (producto)' -ForegroundColor White
Write-Host ''
Write-Host 'Cerrar sesion -> abrir nueva -> decir "Lee docs/SESSION_STATE.md"' -ForegroundColor Gray
