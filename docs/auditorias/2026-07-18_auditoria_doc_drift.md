# Auditoría de Drift Documental — Custodio RAT

> **Fecha:** 2026-07-18
> **Branch:** qa
> **Propósito:** Documentar honestamente qué hay en el código que NO está en los docs `.docx` vigentes, y proponer roadmap de regeneración.
> **Tipo:** Auditoría técnica rápida (NO regenera docs).

## Resumen ejecutivo

Los **9 docs oficiales v1.9** (y los 2 v1.10) están **drifteados** respecto al código real desde el **2026-07-07**. La última regeneración formal fue la auditoría RAT detallada. Desde entonces, **14 commits** modificaron APIs, modelos, schemas y comportamientos que **no están reflejados en los `.docx`**.

**Estado actual:** los docs `.docx` son **históricos válidos** pero **no representan el código actual**. Riesgo bajo para uso interno, **alto** para una eventual fiscalización APDC o auditoría externa.

## Commits que generan drift (2026-07-07 → 2026-07-18)

| Commit | Descripción | Docs afectados |
|--------|-------------|----------------|
| `848903e` | H3.5 BASES_LEGALES deduplication (1 endpoint) | 08 (API), 02 (Requisitos) |
| `fe127b5` | H3.12 export DRY + Z-03 magic bytes | 08 (API), 06 (Arquitectura) |
| `b59a450` | F3.1 versionamiento /api/v1/ | 08 (API) — **crítico** |
| `b59a450` | F3.2 soft delete en User/SecurityBreach | 12 (Manual Técnico), 09 (Backlog) |
| `b59a450` | F3.3 manual cliente no-técnico | — (nuevo) |
| `b59a450` | F3.4 DR test runbook | 11 (Manual Despliegue) |
| `901aaf3` | QW4 ARCO dashboard por_tipo | 04 (CU), 08 (API) |
| `a4f4a55` | C1+C2+C4+C6 compliance crítico | 02, 06, 08, 12, 09 |
| `5cc5157` | C7 rate limit + C3 Vercel Cron + QW13 | 04, 09, 12, 10 |
| `a7e7687` | tests E2E ARCO workflow | 10 (Plan QA) |
| Actual | QW5 SLA T-2 (esta sesión) | 09 (Backlog), 12 (Manual Técnico) |

## Drift detallado por documento

### 08 — API REST (CRÍTICO — más drift)

**Versión vigente:** v1.10 (20 endpoints, regenerado 2026-07-07)
**Drift acumulado desde v1.10:**

| Endpoint / Comportamiento | Estado en v1.10 | Estado en código 2026-07-18 |
|---|---|---|
| `/api/v1/` prefix (F3.1) | NO documentado | ✅ Implementado (commit `b59a450`) |
| `/base-legal-opciones` (H3.5) | NO documentado | ✅ Implementado |
| `BASES_LEGALES` deduplication (H3.5) | NO documentado | ✅ Implementado |
| Export endpoints DRY (H3.12) | NO documentado | ✅ Refactorizado |
| `export/cni` con helper compartido | Documentado v1.10 | ✅ Refactorizado (mismo endpoint, código distinto) |
| Rate limit 10/min en `/seguimiento/{token}` (C7) | NO documentado | ✅ Implementado |
| TOTP/MFA | NO documentado | ❌ Pendiente (F3 futuro) |
| Cookie httpOnly/secure en auth | Documentado | ✅ Sin cambios |

**Acción:** Regenerar `08_API_REST_v1.11.docx`.

### 12 — Manual Técnico (drift medio)

**Versión vigente:** v1.9
**Drift acumulado:**

| Item | Estado en v1.9 | Estado en código 2026-07-18 |
|---|---|---|
| `deleted_at`, `deleted_by_id` en User y SecurityBreach (F3.2) | NO documentado | ✅ Implementado |
| Workflow SLA T-2 días (QW5) | NO documentado | ✅ Implementado |
| Notification_titulares breach (QW13) | NO documentado | ✅ Implementado (parcial — falta descifrar emails) |
| DR test runbook | NO documentado | ✅ Creado en `docs/despliegue/RUNBOOKS/DR_TEST_RUNBOOK.md` |
| Cifrado Fernet fail-loudly (C1) | NO documentado | ✅ Implementado |

**Acción:** Regenerar `12_Manual_Tecnico_v1.10.docx`.

### 04 — Casos de Uso (drift bajo)

**Versión vigente:** v1.10 (25 CUs, regenerado 2026-07-07)
**Drift:** solo el CU nuevo "Rate limit seguimiento público" no está documentado.

**Acción:** regenerar si se hace auditoría formal. Bajo impacto.

### 06 — Arquitectura (drift medio)

**Versión vigente:** v1.9
**Drift:**

| Item | Estado en v1.9 | Estado en código 2026-07-18 |
|---|---|---|
| Versionamiento API `/api/v1/` (F3.1) | NO documentado | ✅ Implementado |
| Soft delete en modelos con PII (F3.2) | NO documentado | ✅ Implementado |
| Cifrado Fernet fail-loudly (C1) | NO documentado | ✅ Implementado |
| DR plan RTO<4h / RPO<1h | NO documentado | ✅ Documentado |

**Acción:** Regenerar `06_Arquitectura_v1.10.docx`.

### 09 — Backlog (drift bajo)

**Versión vigente:** v1.9
**Drift:** el backlog ahora tiene 16 items cerrados (no 14). Falta agregar QW5 cerrado.

**Acción:** regenerar `09_Backlog_v1.10.docx`.

### 10 — Plan QA (drift bajo)

**Versión vigente:** v1.9 (8 TCs nuevos)
**Drift:** tests E2E ARCO workflow (6 tests nuevos, commit `a7e7687`) no están en el plan.

**Acción:** regenerar si auditoría formal.

### 02 — Requisitos (drift bajo)

**Versión vigente:** v1.9
**Drift:** el RF-170 (BaseLegal enum) no está documentado.

**Acción:** regenerar `02_Requisitos_v1.10.docx`.

### 03 — Historias de Usuario (drift bajo)

**Versión vigente:** v1.9
**Drift:** la HU de SLA T-2 días no está.

**Acción:** regenerar `03_Historias_Usuario_v1.10.docx`.

### MTX — Matriz de Trazabilidad (drift medio)

**Versión vigente:** v1.9
**Drift:** RF-170 (BaseLegal), RF-171 (Soft delete), RF-172 (Versionamiento API), RF-173 (SLA T-2) no están mapeados a HUs.

**Acción:** regenerar `Matriz_Trazabilidad_v1.10.docx`.

### 00 — Índice (sin cambios)

No requiere regeneración. El `docs/README.md` raíz cumple esta función.

### 01 — Visión de Producto (drift medio)

**Versión vigente:** v1.0
**Drift:** el producto ahora tiene Manual de Cliente (`manual/README.md`) y DR runbook. La visión de producto no menciona estos.

**Acción:** regenerar si se hace v1.11.

### 11 — Manual de Despliegue (drift medio)

**Versión vigente:** v1.1
**Drift:** el runbook DR está en `docs/despliegue/RUNBOOKS/` (NO en v1.1). El formato es markdown, no .docx.

**Acción:** regenerar `11_Manual_Despliegue_v1.10.docx` o documentar la descontinuación del .docx.

### 05 — Diseño Funcional (sin versión reciente)

**Versión vigente:** v1.3 (sin v1.9+)
**Drift:** el componente de UI (`RatWizard`) ahora es modular (5 pasos + WizardModular/) pero el doc describe el monolito de 1300 líneas.

**Acción:** regenerar `05_Diseno_Funcional_v1.10.docx` o documentar descontinuación.

### 07 — Modelo de Datos Detallado (sin versión reciente)

**Versión vigente:** v1.1
**Drift:** los modelos cambiaron (BASES_LEGALES enum, soft delete en User/Breach/Rat, etc.).

**Acción:** regenerar `07_Modelo_Datos_v1.10.docx`.

---

## Documentación complementaria (NO oficial .docx)

Estos docs SÍ están actualizados:

| Recurso | Ubicación | Estado |
|---|---|---|
| SESSION_HANDOFF.md | `docs/` | ✅ v1.0 (2026-07-13) |
| STATUS.md | `docs/` | ✅ Actualizado este PR |
| LEVANTAMIENTO_2026-07-18.md | raíz | ✅ Recién creado |
| manual/README.md | `manual/` raíz | ✅ Recién creado (F3.3) |
| docs/despliegue/RUNBOOKS/DR_TEST_RUNBOOK.md | `docs/` | ✅ Recién creado (F3.4) |
| Frontend AGENTS.md | `frontend-next/` | ✅ Actualizado (con autores de commits) |
| Backend CLAUDE.md | `backend/` | ✅ Actualizado |
| Skills `.opencode/skills/` | `.opencode/skills/` | ✅ 21 skills vigentes |

---

## Roadmap de regeneración v1.10

### Escenario A — Regeneración mínima (3 horas)

1. Copiar scripts de `docs/auditorias/2026-07-05_auditoria_v1.9/_scripts/`
2. Renombrar `v1_9` → `v1_10` en cada script
3. Actualizar `output_filename` y headers de cada uno
4. Ejecutar y mover .docx a `docs/documentacion_oficial/`
5. Actualizar matriz de vigencia en `documentacion_oficial/README.md`

**Docs a regenerar (7):**
- 02 Requisitos
- 03 Historias de Usuario
- 06 Arquitectura
- 09 Backlog
- 10 Plan QA
- 12 Manual Técnico
- MTX Matriz Trazabilidad

(Los 2 ya en v1.10 — 04 y 08 — no se tocan).

### Escenario B — Regeneración completa (6 horas)

Regenerar **12 docs** (los 7 de arriba + 05 Diseño Funcional + 07 Modelo Datos + 11 Manual Despliegue + 01 Visión).

### Escenario C — Híbrido recomendado (4 horas)

Regenerar los 7 de v1.10. Para 05/07/11/01, crear **un documento markdown actualizado** en `docs/documentacion_ofinal/` y referenciarlo desde la matriz de vigencia como "fuente alternativa" (igual que ya se hace con 00/05/07/11).

---

## Recomendación para el equipo

**Opción C (híbrida)** es el balance correcto:

- 7 .docx regenerados a v1.10 cubren los drifts de APIs, CU, manual técnico, etc.
- 4 docs sin regenerar se mantienen como históricos y se referencian docs .md actualizados.

**Tiempo estimado:** 4 horas en una sesión dedicada.

**Cuándo hacerlo:** antes de la fecha de vigencia APDC del 1 de diciembre 2026 (para que un fiscalizador encuentre docs actualizados).

---

## Acciones inmediatas recomendadas

1. **Hoy (2026-07-18)**: regenerar 02, 06, 09, 12 (los más críticos para fiscalización). ~2 horas.
2. **Esta semana**: regenerar 03, 10, MTX. ~1.5 horas.
3. **Antes del 1 diciembre**: regenerar 04, 08 (que ya están en v1.10) si hay nuevos endpoints (F3.1 los agregó).
4. **Pendiente futuro**: 05, 07, 11, 01 con docs .md actualizados.

---

## Convención de correlativos (pregunta frecuente)

Al listar scripts en `_scripts/`, los números **00, 01, 05, 07, 11** aparecen ausentes en las versiones v1.7+ (solo están hasta v1.3 en `paso/arquitectura_desarrollo_de_software_estandar/_build/`).

**Esto NO es un error.** El skill oficial `.opencode/skills/custodio-auditoria/SKILL.md` (sección "Documentos Sin Cambios") declara explícitamente que esos 5 docs NO se regeneran en cada auditoría:

| Correlativo | Doc | Por qué no se regenera |
|---|---|---|
| 00 | Índice | Sustituido por `docs/README.md` raíz. |
| 01 | Visión de Producto | El producto maduró, pero la visión base sigue vigente. |
| 05 | Diseño Funcional | Sustituido por código + `docs/arquitectura/`. |
| 07 | Modelo de Datos Detallado | Sustituido por `backend/app/models/` + Schema Pydantic. |
| 11 | Manual de Despliegue | Sustituido por `docs/despliegue/PLAN_DEPLOY.md` + `RUNBOOKS/`. |

**Convención**: los builds en `_scripts/` cubren **solo los 9 docs que se regeneran** (02, 03, 04, 06, 08, 09, 10, 12, MTX). La regeneración a v1.10 no incluye los correlativos discontinuados porque el proyecto maduró y esas áreas cambiaron de formato (de .docx a markdown).

Si en una auditoría futura alguno de esos 5 docs discontinuados vuelve a regenerarse (ej. por cambio de visión de producto), aparecerá un nuevo build con ese correlativo en `_scripts/`.

---

*Auditor honesta, no regeneración. Para regenerar: usar skill `custodio-auditoria` con scripts v1.9 → renombrar a v1.10.*