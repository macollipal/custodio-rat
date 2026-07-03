# Session State - Custodio RAT

**Generado:** 2026-07-03 11:51
**Branch:** qa

## Ultimos 15 commits
d978e74 feat(skills): agregar 5 skills de compliance (Fase 2) 9ff73fe chore(gitignore): ignorar docs oficial, .xlsx, .pptx y generar_ppt*.py 73ea709 chore(tools): add new-session.ps1 helper + SESSION_STATE.md 17bc516 docs(skills): vincular 4 skills relevantes a frontend-next/AGENTS.md deed884 docs(skills): vincular 8 skills relevantes a backend/CLAUDE.md 487d840 chore(skills): renombrar soluciona_cors -> deploy-cors-multienv (kebab-case) 7ea7d85 chore(skills): archivar Experto-Senior-OCI como deprecated 2c30308 chore(skills): eliminar arquitecto-test (meta-prompt obsoleto) e2b9ab0 fix(skills): corregir ley 21.663 -> 21.719 en qa-senior 8b908f2 security: agregar .env.example completo + verify_env.py audit script ef4dee0 docs(security): formalizar LEY DIVINA de NO subir passwords a git 63ca658 security: rotar credenciales Neon hardcodeadas + pre-commit hook a2cb2a9 fix(rats): agregar no_requerida_justificada al validator de estado_eipd 88cee5f test(rats): script Python que inserta 41 RATs + 5 consentimientos en Neon QA a94b7a1 test(rats): agregar set de pruebas 44 RATs + screenshot Login homologado

## Working tree status


## Proximos pasos (prioridad alta)
- Fase 2: 5 skills de compliance (rat-compliance, breach-management, arco-rights, multi-tenant-security, api-review)
- Fase 3: CI/CD (.github/workflows/, .pre-commit-config.yaml, cobertura tests)
- Fase 4: Track E (QW3-QW6: score empresa, exports, SLA alerts, ficha tabs)
- Limpieza: ~104 RATs en BD (duplicados)

## Skills activas (vinculadas en CLAUDE.md / AGENTS.md)
- security-secret-scan, commit-helper, tester-rat, custodio-auditoria
- qa-senior, architect-senior, deploy-cors-multienv, debug-login
- frontend-guardian, equipo-compuesto

## LEYES DIVINAS (no negociar)
- NO secrets en git (NUNCA hardcodear passwords, API keys, tokens)
- Variables de entorno para TODA credencial (DATABASE_URL, JWT_SECRET, etc.)
- Pre-commit hook con gitleaks BLOQUEA cualquier secret antes de commit
- .env.example documenta todas las variables requeridas

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
