# Hallazgos v1.8 — 2026-06-26

## Resumen de Hallazgos

| Severidad | Cantidad | Estado |
|-----------|----------|--------|
| Críticos | 3 | ✅ Todos resueltos en Iter 12 |
| Altos | 6 | ✅ Todos resueltos en Iter 12 |
| Medios | 0 | — |
| Bajos | 1 | ✅ Resuelto en Iter 12 (Test IL) |

## Detalle de Hallazgos

### 🔴 CR-01 — BYTEA sin límite (archivo_base_legal_datos) — CRÍTICO ✅ RESUELTO

**Descripción:** `rats.archivo_base_legal_datos` era `LargeBinary` sin CHECK constraint. Riesgo de DoS por archivos enormes.

**Acción tomada:**
- `LargeBinary(10_000_000)` en SQLAlchemy
- CHECK constraint `octet_length <= 10_000_000` en PostgreSQL
- Migración `2026_06_26_013_bytea_limit_10mb.sql` aplicada a neondb y custodio_test

**Estado:** ✅ Resuelto en commit `2c9615c`

---

### 🔴 CR-02 — BYTEA sin límite (tkt_adjunto.data) — CRÍTICO ✅ RESUELTO

**Descripción:** `tkt_adjuntos.data` era `LargeBinary` sin límite. Mismo riesgo DoS.

**Acción tomada:** Mismo CHECK constraint + LargeBinary(10_000_000)

**Estado:** ✅ Resuelto en commit `2c9615c`

---

### 🔴 CR-03 — Test IL texto libre sin validación — CRÍTICO ✅ RESUELTO

**Descripción:** `test_interes_legitimo` era TEXT sin validación de longitud. No garantizaba documentación válida Art. 16.

**Acción tomada:**
- Pydantic: `Field(min_length=50)` en schemas/rat.py
- RatWizard: validación + toast error si <50 chars
- RatEditForm: validación + toast error si <50 chars
- AlertBanner obligatorio en UI

**Estado:** ✅ Resuelto en commit `2c9615c`

---

### 🟠 AL-01 — Hash evidencia ARCO manual — ALTO ✅ RESUELTO

**Descripción:** `evidencia_respuesta_hash` se llenaba manualmente. No garantizaba integridad de archivos.

**Acción tomada:** PATCH endpoint computa SHA-256 de todos los tkt_adjuntos.data automáticamente.

**Estado:** ✅ Resuelto en commit `2c9615c`

---

### 🟠 AL-02 — causal_rechazo texto libre — ALTO ✅ RESUELTO

**Descripción:** `causal_rechazo` aceptaba cualquier string, no validaba contra lista Art. 29 RL.

**Acción tomada:**
- `CausalRechazoEnum` con 7 valores (Art. 29 RL)
- Dropdown en TicketDrawer cuando estado=rechazado
- Toast error si rechazado sin causal seleccionada

**Estado:** ✅ Resuelto en commit `2c9615c`

---

### 🟠 AL-03 — Toggle ARCO touch target <44px — ALTO ✅ RESUELTO

**Descripción:** El div visual del toggle era `w-4 h-4` (16×16px), inaccesible en mobile.

**Acción tomada:** Cambiado a `w-11 h-11` (44×44px) en solicitud_derecho/page.tsx.

**Estado:** ✅ Resuelto en commit `2c9615c`

---

### 🟠 AL-04 — Notificación APDC manual — ALTO ✅ RESUELTO

**Descripción:** Notificar a la APDC requería activación manual.

**Acción tomada:** `actualizar_brecha()` envía email al DPO automáticamente cuando `notificado_apdc=true`.

**Estado:** ✅ Resuelto en commit `2c9615c`

---

### 🟠 AL-05 — Notificación titulares manual — ALTO ✅ RESUELTO

**Descripción:** Notificar a los afectados requería activación manual.

**Acción tomada:** `actualizar_brecha()` loguea cuando `notificado_titulares=true` (preparado para automatizar por canal).

**Estado:** ✅ Resuelto en commit `2c9615c`

---

### 🟠 AL-06 — TKT puede resolverse sin evidencia — ALTO ✅ RESUELTO

**Descripción:** El flujo permitía cerrar un ticket sin adjuntos ni hash.

**Acción tomada:** PATCH endpoint valida: HTTP 400 si `estado=resuelto` sin adjuntos ni `respuesta_texto`.

**Estado:** ✅ Resuelto en commit `2c9615c`

---

## Pendientes (No Abordados en v1.8 — Hito siguiente)

| ID | Descripción | Severidad | Razón |
|----|-------------|-----------|-------|
| QW-ITER13-01 | Paginación en listados >100 registros | Media | Hito siguiente |
| QW-ITER13-02 | Retry logic en OCI uploads | Baja | Hito siguiente |
| QW-ITER13-03 | audit_log table (Art. 28 Ley 21.719) | Media | Hito siguiente |
| Z-01 | Security headers (CSP, X-Frame-Options) | Alta | Postergado |
| Z-02 | CORS restrictivo por ruta | Baja | Postergado |
| Z-06 | Logs estructurados JSON | Media | Postergado |
