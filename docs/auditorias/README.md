# Índice de Auditorías — Custodio RAT

## Auditorías por Fecha

| Fecha | Auditoría | Estado | Score |
|-------|-----------|--------|-------|
| 2026-05-31 | Opinion Arquitectónica | ✅ Corregido | 6.3/10 |
| 2026-06-08 | Auditoría v1.2 | ✅ Corregido | 4.83/10 → 7.5/10 |
| 2026-06-09 | Beta Launch | ✅ Producción | 7.5/10 |
| 2026-06-09 | AsesorGPT v1.0 | ✅ Cerrada | — |
| 2026-06-11 | Incidente ENV_VARS | ✅ Resuelto | — |
| 2026-06-12 | Auditoría v1.4 | ✅ Documentación | 7.6/10 |
| 2026-06-13 | Post-fix OCI | ✅ Activo | 7.6/10 |
| 2026-06-14 | Auditoría v1.5 | ✅ Documentación | 8.3/10 |

### 2026-06-14 — Auditoría v1.5
- **Estado:** ✅ Documentación generada
- **Score:** 8.3/10 (7.6/10 → 8.3/10)
- **Tema:** S14 CSRF + C1 BYTEA Encryption + A6 Service Layer + A10 Schemas Pydantic
- **Commits:** `7ef3d78` (ZAP+CHANGELOG), `82d5723` (A6), `9f50f04` (C1 crypto), `1328001` (C1 initial)
- **Docs generados:** 02, 03, 04, 06, 09, 10, 12, MTX (8 documentos)
- **Carpeta:** `2026-06-14_auditoria_v1.5/`

### 2026-06-12 — Auditoría v1.4
- **Estado:** ✅ Documentación generada
- **Score:** 7.6/10
- **Tema:** OCI Object Storage + Admin Asesor IA + documentación v1.4
- **Commits:** `57cbffc` (OCI fallback), reorganización-carpetas
- **Docs generados:** 02, 03, 04, 06, 08, 09, 10, 12, MTX (9 documentos)
- **Carpeta:** `2026-06-12_auditoria_v1.4/`

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
| Z-01 | Security headers (CSP, X-Frame-Options) | Media | ❌ PENDIENTE |
| Z-02 | CORS restrictivo | Baja | ❌ PENDIENTE |
| Z-03 | File upload validation | Media | ❌ PENDIENTE |
| Z-06 | Backups documentados | Baja | ❌ PENDIENTE |
| DT-009 | Coverage 40% | Media | 📋 Parcial |
| DT-010 | E2E Playwright | Media | 📋 Parcial |

## Ver También

- [AUDITORIA_V1.5.md](2026-06-14_auditoria_v1.5/AUDITORIA_V1.5.md)
- [AUDITORIA_V1.4.md](2026-06-12_auditoria_v1.4/AUDITORIA_V1.4.md)
- [HALLAZGOS.md](2026-06-12_auditoria_v1.4/HALLAZGOS.md)
- [diff_codigo_vs_docs.md](2026-06-12_auditoria_v1.4/diff_codigo_vs_docs.md)
- [INFORME_BETA_LAUNCH.md](2026-06-09_BETA_LAUNCH/INFORME_BETA_LAUNCH.md)
- [AUDITORIA_V1.3_BETA.md](2026-06-09_BETA_LAUNCH/AUDITORIA_V1.3_BETA.md)
- [INCIDENTE.md](2026-06-11_INCIDENTE_ENV/INCIDENTE.md)

---

*Última actualización: 2026-06-14*
