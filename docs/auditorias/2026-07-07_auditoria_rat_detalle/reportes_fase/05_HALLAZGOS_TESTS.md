# HALLAZGOS COBERTURA DE TESTS — Módulo RAT

**Fecha:** 2026-07-07
**Versión auditada:** v1.9
**Skills aplicadas:** `tester-rat`, `qa-custodio`
**Score cobertura RAT:** **7.0/10**

---

## Resumen Ejecutivo

El módulo RAT tiene **6 archivos de tests pytest** + **2 archivos Playwright E2E** cubriendo CRUD, validators, archivos, auditoría y gaps Ley 21.719.

**Cobertura estimada:**
- Backend RAT: **~75%** (objetivo: 85%)
- Frontend RAT: **~30%** (objetivo: 60%)

**Gaps principales:**
- ⚠️ Sin test E2E del workflow completo (RAT → EIPD → aprobar)
- ⚠️ Sin test de paginación >100 registros (QW-ITER14-01)
- ⚠️ Sin test del endpoint CNI export
- ⚠️ Sin test del dashboard stats

---

## Inventario de Tests Backend

| Archivo | Líneas | Tests | Cobertura | Score |
|---|---|---|---|---|
| `test_rats.py` | 288 | ~25 | CRUD + completitud + flags | 9/10 |
| `test_rat_gaps_21719.py` | 178 | ~12 | Campos Iter 10 (5 nuevos) | 8/10 |
| `test_rat_tier1_tier2.py` | 325 | ~20 | Tier 1 (5) + Tier 2 (10) | 8.5/10 |
| `rat_archivo_test.py` | 150 | 5 | Descarga archivo | 7/10 |
| `rat_auditoria_test.py` | 84 | 4 | IDOR + sin auth | 7/10 |
| `test_security.py::TestRATValidators` | ~178 | 8 | Validators condicionales | 9/10 |
| **Total pytest** | **~1,200** | **~74** | | **8/10** |

## Inventario de Tests E2E (Playwright)

| Archivo | Líneas | Tests | Cobertura | Score |
|---|---|---|---|---|
| `e2e/05-rat.spec.ts` | 70 | 4 | Carga página, tabla, filtros | 6/10 |
| `e2e/15-rat-modal.spec.ts` | — | 3 | Modal detalle | 6/10 |
| **Total E2E** | **~140** | **~7** | | **6/10** |

---

## Análisis Detallado

### ✅ `test_rats.py` (288 líneas) — Score 9/10

**Cubre:**
- ✅ Crear RAT completo (201)
- ✅ Crear sin nombre → 422
- ✅ Crear sin company_id → 422
- ✅ Crear con company_id inexistente → 404/400
- ✅ Crear con datos sensibles
- ✅ Crear con transferencia internacional
- ✅ Listar, obtener por ID
- ✅ Actualizar
- ✅ Eliminar
- ✅ Aprobar (con 100% completitud)
- ✅ Cálculo de completitud
- ✅ Cálculo de riesgo

**Gaps:**
- ⚠️ Sin test de RBAC explícito (admin_empresa no puede crear)
- ⚠️ Sin test de superadmin vs admin_empresa en mismo endpoint

---

### ✅ `test_rat_gaps_21719.py` (178 líneas) — Score 8/10

**Cubre:**
- ✅ `sistema_almacenamiento`
- ✅ `volumen_titulares_estimado`
- ✅ `operaciones_tratamiento` (JSON)
- ✅ `logica_automatizada`
- ✅ `responsable_tratamiento_email` con regex

**Gaps:**
- ⚠️ Sin test de email inválido siendo rechazado (422)

---

### ✅ `test_rat_tier1_tier2.py` (325 líneas) — Score 8.5/10

**Cubre:**
- ✅ Tier 1 (5 campos): `datos_nna`, `nivel_confidencialidad`, `estructura_dato`, `datos_anonimizados`, `datos_seudonimizados`
- ✅ Tier 2 (10 campos): `sistema_almacenamiento`, `volumen_titulares`, etc.

✅ Buena cobertura de los 15 campos nuevos.

---

### ⚠️ `rat_archivo_test.py` (150 líneas) — Score 7/10

**Cubre:**
- ✅ Sin auth → 401
- ✅ RAT inexistente → 404 (P0 FIXED)
- ✅ RAT sin archivo → 404 (P0 FIXED)
- ✅ Descarga con archivo cifrado Fernet
- ✅ IDOR otra empresa → 404 (P0 FIXED)

**Gaps:**
- ⚠️ Sin test con storage_url OCI (solo BYTEA)
- ⚠️ Sin test de Fernet decrypt falla → 500

---

### ⚠️ `rat_auditoria_test.py` (84 líneas) — Score 7/10

**Cubre:**
- ✅ Sin auth → 401
- ✅ RAT inexistente → 200 con lista vacía (comportamiento deliberado)
- ✅ RAT con logs → 200
- ✅ IDOR otra empresa → 404 (P0 FIXED)

**Gaps:**
- ⚠️ Sin test de paginación (`skip`, `limit`)
- ⚠️ Sin test de ordenamiento

---

### ✅ `test_security.py::TestRATValidators` (~178 líneas) — Score 9/10

**Cubre:**
- ✅ Validador `transferencia_internacional` requiere `pais_destino` + `garantias`
- ✅ Validador `decisiones_automatizadas` requiere `logica_automatizada`
- ✅ Validador `datos_sensibles` requiere `tipo_dato_sensible`
- ✅ Validación UPDATE con campos opcionales
- ✅ Email regex

✅ Excelente cobertura de validators.

---

## Análisis E2E

### ⚠️ `e2e/05-rat.spec.ts` (70 líneas) — Score 6/10

**Cubre:**
- ✅ Carga de página `/rat`
- ✅ Tabla visible
- ✅ Filtros funcionan
- ✅ Exportar CSV

**Gaps:**
- ⚠️ No cubre creación de RAT (wizard)
- ⚠️ No cubre edición
- ⚠️ No cubre eliminación
- ⚠️ No cubre duplicación
- ⚠️ No cubre modal de detalle

### ⚠️ `e2e/15-rat-modal.spec.ts` — Score 6/10

**Cubre:**
- ✅ Modal de detalle se abre

**Gaps:**
- ⚠️ No cubre edición desde modal
- ⚠️ No cubre audit log en modal

---

## Gaps Identificados

### P1 (Críticos para compliance)

| Código | Gap | Endpoint / Función |
|---|---|---|
| **H5.1** | Sin test E2E flujo RAT → EIPD → aprobar | Workflow completo |
| **H5.2** | Sin test paginación >100 registros (QW-ITER14-01) | `GET /rats/reportes` |
| **H5.3** | Sin test endpoint CNI export | `GET /rats/export/cni` |
| **H5.4** | Sin test dashboard stats | `GET /rats/dashboard/{company_id}` |

### P2 (Importantes)

| Código | Gap | Endpoint / Función |
|---|---|---|
| H5.5 | Sin test de RBAC admin_empresa | `POST /rats/`, `PUT /rats/{id}` |
| H5.6 | Sin test de email inválido (422) | `RATCreate.responsable_tratamiento_email` |
| H5.7 | Sin test E2E del wizard 5 pasos | `RatWizard.tsx` |
| H5.8 | Sin test de Fernet decrypt falla | `GET /rats/{id}/archivo` |
| H5.9 | Sin test de storage_url OCI | `GET /rats/{id}/archivo` |
| H5.10 | Sin test de paginación auditoría | `GET /rats/{rat_id}/auditoria` |
| H5.11 | Sin test de a11y (axe-core) | Todos los componentes frontend |
| H5.12 | Sin test E2E mobile viewport | Todos los componentes |

### P3 (Mejoras continuas)

| Código | Gap | Endpoint / Función |
|---|---|---|
| H5.13 | Sin test de duplicación de RAT | `POST /rats/` con datos copiados |
| H5.14 | Sin test de `marcar_revisado` | `POST /rats/{id}/revision` |
| H5.15 | Sin test de `aprobar_rat` con <100% (debe fallar) | `POST /rats/{id}/aprobar` |
| H5.16 | Sin test de carga (100+ RATs) | Todos los endpoints de lista |
| H5.17 | Sin test de concurrencia (2 users edit mismo RAT) | `PUT /rats/{id}` |

---

## Matriz de Cobertura por Módulo

| Módulo | Cobertura Actual | Objetivo | Gap |
|---|---|---|---|
| Auth | 90% | 90% | ✅ |
| **RATs CRUD** | 75% | 85% | -10% |
| **RAT Tier 1+2** | 85% | 85% | ✅ |
| **RAT Gaps 21719** | 80% | 85% | -5% |
| **RAT Validators** | 90% | 90% | ✅ |
| **RAT Auditoria** | 65% | 80% | -15% |
| **RAT Archivo** | 70% | 80% | -10% |
| Dashboard | 30% | 70% | -40% |
| Export (CSV/PDF) | 70% | 75% | -5% |
| Export (CNI) | 0% | 75% | -75% |
| Wizard frontend | 0% | 60% | -60% |
| Drawer/Drawer | 30% | 60% | -30% |

---

## Score Cobertura por Módulo RAT

| Módulo | Score |
|---|---|
| pytest RAT total | 8.0/10 |
| Playwright RAT | 6.0/10 |
| E2E flujos completos | 4.0/10 |
| a11y | 0/10 |
| Performance/carga | 0/10 |
| **TOTAL** | **7.0/10** |

---

## Tests Priorizados a Crear

### Sprint 1 (P1)
1. **Test E2E RAT → EIPD → aprobar** (10 tests, ~300 líneas)
2. **Test paginación reportes** (5 tests, ~150 líneas)
3. **Test CNI export** (3 tests, ~80 líneas)
4. **Test dashboard stats** (5 tests, ~150 líneas)

### Sprint 2 (P2)
5. **Test RBAC** (4 tests, ~100 líneas)
6. **Test email inválido** (1 test, ~20 líneas)
7. **Test E2E wizard 5 pasos** (15 tests, ~500 líneas)
8. **Test a11y con axe-core** (10 tests, ~200 líneas)

### Backlog (P3)
- Tests de duplicación, carga, concurrencia.

---

## Estimación de Esfuerzo

| Sprint | Tests a crear | Horas estimadas |
|---|---|---|
| Sprint 1 (P1) | 23 tests | 6-8 horas |
| Sprint 2 (P2) | 30 tests | 8-10 horas |
| Backlog (P3) | 20 tests | 4-6 horas |
| **TOTAL** | **73 tests** | **18-24 horas** |

---

**Próxima fase:** Documentación vs código (Fase 6)