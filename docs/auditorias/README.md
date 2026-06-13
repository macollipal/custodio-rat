# Índice de Auditorías — Custodio RAT

## Auditorías por Fecha

| Fecha | Auditoría | Estado | Score |
|-------|-----------|--------|-------|
| 2026-05-31 | Opinion Arquitectónica | ✅ Corregido | 6.3/10 |
| 2026-06-08 | Auditoría v1.2 | ✅ Corregido | 4.83/10 → 7.5/10 |
| 2026-06-09 | Beta Launch | ✅ Producción | 7.5/10 |
| 2026-06-09 | AsesorGPT v1.0 | ✅ Cerrada | — |
| 2026-06-11 | Incidente ENV_VARS | ✅ Resuelto | — |
| 2026-06-13 | Post-fix OCI | ✅ Activo | 7.6/10 |

## Detalle de Auditorías

### 2026-06-13 — Post-fix OCI Download
- **Estado:** ✅ Activo
- **Score:** 7.6/10
- **Tema:** Fix del fallback OCI (PAR → download directo → BYTEA)
- **Commit:** `57cbffc`

### 2026-06-11 — Incidente ENV_VARS
- **Estado:** ✅ Resuelto
- **Tema:** Frontend prod apunta a localhost por env vars no configuradas
- **Lecciones:** Fallbacks en código son anti-patrón, smoke tests deben validar bundle

### 2026-06-09 — Beta Launch
- **Estado:** ✅ Producción
- **Score:** 7.5/10
- **Commits:** `ae0d7bc`, `d542dbd`, `6209e2d`, `6980187`, `43287c0`
- **P0 cerrados:** 6/6 (100%)
- **P1 cerrados:** 12/15 (80%)

### 2026-06-08 — Auditoría v1.2
- **Estado:** ✅ Cerrada
- **Score inicial:** 4.83/10
- **Score final:** 7.5/10
- **Hallazgos críticos:** Token blacklist, IDOR, CSV injection, RBAC gaps

### 2026-06-05-31 — Opinion Arquitectónica
- **Estado:** ⚠️ Parcialmente corregido
- **Score:** 6.3/10
- **Pendientes:** CSRF (S14), App-level encryption (C1), Schemas inline (A10)

## Pendientes de Auditorías Anteriores

| ID | Descripción | Prioridad | Estado |
|----|-------------|-----------|--------|
| S14 | CSRF protection | ALTA | ❌ PENDIENTE |
| C1 | App-level encryption | ALTA | ❌ PENDIENTE |
| A10 | Schemas inline | MEDIA | ❌ PENDIENTE |
| DT-009 | Coverage 40% | MEDIA | 📋 Parcial |
| DT-010 | E2E Playwright | MEDIA | 📋 Parcial |

## Ver También

- [INFORME_BETA_LAUNCH.md](2026-06-09_BETA_LAUNCH/INFORME_BETA_LAUNCH.md)
- [AUDITORIA_V1.3_BETA.md](2026-06-09_BETA_LAUNCH/AUDITORIA_V1.3_BETA.md)
- [INCIDENTE.md](2026-06-11_INCIDENTE_ENV/INCIDENTE.md)

---

*Última actualización: 2026-06-13*
