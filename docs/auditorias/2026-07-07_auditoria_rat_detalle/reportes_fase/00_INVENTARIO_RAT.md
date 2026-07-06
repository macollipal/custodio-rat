# INVENTARIO TÉCNICO — Módulo RAT

**Fecha:** 2026-07-07
**Versión auditada:** v1.9
**Alcance:** Solo módulo RAT (no Brechas/EIPD/ARCO)
**Stack:** FastAPI + SQLAlchemy + PostgreSQL/Neon + Next.js 16 + TypeScript

---

## 1. Backend

### 1.1 Modelo (`backend/app/models/rat.py`) — 209 líneas

| Item | Detalle |
|---|---|
| Tabla | `rats` |
| Índice | `ix_rats_company_estado (company_id, estado)` |
| Enums | `EstadoRAT` (BORRADOR, COMPLETO, EN_REVISION, APROBADO), `EstadoEIPD` (NO_REQUERIDA, PENDIENTE, EN_PROCESO, COMPLETADA) |
| Columnas | 40 totales |
| Relaciones | `company` (N:1), `eipd` (1:1), `consentimientos` (1:N, cascade delete) |
| Métodos | `calcular_completitud()`, `calcular_nivel_riesgo()` |

**Distribución de columnas:**

| Categoría | Cantidad |
|---|---|
| Obligatorios Art. 16 | 7 |
| Recomendados Art. 16 | 3 |
| Flags de riesgo | 5 |
| Transferencia internacional | 4 |
| Encargado | 2 |
| Gaps Iter 10 | 5 |
| Tier 1 críticos | 5 |
| Tier 2 operativos | 10 |
| Archivo base legal | 5 |
| Audit/metadata | 8 |
| **TOTAL** | **54** (40 en tabla + 14 derivados/calculados) |

### 1.2 Schemas (`backend/app/schemas/rat.py`) — 252 líneas

| Schema | Líneas | Validators |
|---|---|---|
| `RATBase` | 8-63 | `estado_eipd_valido`, `email_formato_responsable` |
| `RATCreate` | 84-123 | `nombre_no_vacio`, `base_legal_valida`, `validar_campos_condicionales` (model_validator after) |
| `RATUpdate` | 126-200 | `validar_campos_condicionales_before` (model_validator before) |
| `RATOut` | 203-218 | — |
| `RATSugerencia` / `RATSugerenciaOut` | 221-236 | — |
| `TestInteresLegitimo` | 239-243 | — |
| `ReportesResponse` | 245-252 | — |

### 1.3 Service (`backend/app/services/rat_service.py`) — 640 líneas

| Función | Línea | Tipo |
|---|---|---|
| `get_rats` | 89 | Public |
| `get_rat` | 99 | Public |
| `get_rat_for_user` | 106 | **Public (multi-tenant security)** |
| `_procesar_archivo_base_legal` | 127 | Internal |
| `_validar_consentimiento_sensibles` | 176 | Internal |
| `_validar_contrato_encargado` | 199 | Internal |
| `_validar_eipd_obligatoria` | 213 | Internal |
| `create_rat` | 265 | Public |
| `update_rat` | 298 | Public |
| `delete_rat` | 335 | Public |
| `download_rat_file` | 365 | Public |
| `get_audit_logs` | 424 | Public |
| `get_dashboard_stats` | 433 | Public |
| `marcar_revisado` | 596 | Public |
| `aprobar_rat` | 613 | Public |
| `_calcular_estado` | 517 | Internal |
| `_generar_alertas_auditoria` | 554 | Internal |

**Catálogo `ALERTAS_AUDITORIA`** (líneas 32-86): 11 alertas que se generan automáticamente.

### 1.4 Routes (`backend/app/routes/rats.py`) — 568 líneas

**20 endpoints:**

| # | Método | Ruta | Línea |
|---|---|---|---|
| 1 | GET | `/rats/reportes` | 31 |
| 2 | GET | `/rats/` | 168 |
| 3 | GET | `/rats/dashboard/{company_id}` | 198 |
| 4 | GET | `/rats/sugerencias/tipos` | 212 |
| 5 | POST | `/rats/sugerencias` | 217 |
| 6 | GET | `/rats/{rat_id}` | 226 |
| 7 | POST | `/rats/` | 240 |
| 8 | POST | `/rats/{rat_id}/consentimientos` | 261 |
| 9 | PUT | `/rats/{rat_id}` | 293 |
| 10 | DELETE | `/rats/{rat_id}` | 311 |
| 11 | POST | `/rats/{rat_id}/revision` | 323 |
| 12 | POST | `/rats/{rat_id}/aprobar` | 336 |
| 13 | GET | `/rats/{rat_id}/archivo` | 357 |
| 14 | GET | `/rats/{rat_id}/auditoria` | 407 |
| 15 | GET | `/rats/auditoria/{company_id}` | 418 |
| 16 | GET | `/rats/auditoria/verify-chain` | 453 |
| 17 | GET | `/rats/export/csv` | 471 |
| 18 | GET | `/rats/export/pdf` | 493 |
| 19 | GET | `/rats/{rat_id}/export/pdf` | 515 |
| 20 | GET | `/rats/export/cni` | 541 |

### 1.5 Repository (`backend/app/repositories/rat_repository.py`) — 63 líneas

| Método | Línea |
|---|---|
| `get_all_by_company` | 19 |
| `get_with_relations` | 35 |
| `count_by_company` | 48 |
| `get_by_company_and_estado` | 52 |

### 1.6 Export (`backend/app/services/export_service.py` — 439 líneas, `export_cni_service.py` — 100 líneas)

| Función | Línea |
|---|---|
| `exportar_csv` | 104 |
| `exportar_pdf` | 158 |
| `exportar_rat_cni` | export_cni_service.py |

---

## 2. Frontend

### 2.1 Página (`frontend-next/app/(app)/rat/page.tsx`) — 191 líneas

| Componente | Uso |
|---|---|
| `RatTable` | Tabla principal |
| `RatWizard` | Wizard de creación (5 pasos) |
| `RatDetailModal` | Modal de detalle (view/edit) |
| `SkeletonTable` | Loading state |

### 2.2 Componentes (`frontend-next/components/rat/`)

| Archivo | Líneas | Propósito |
|---|---|---|
| `RatTable.tsx` | 302 | Tabla con filtros, badges, sort, export |
| `RatWizard.tsx` | ~1300 | Wizard 5 pasos (Identificación, Datos, Finalidad, Almacenamiento, Compliance) |
| `RatEditForm.tsx` | 805 | Edición con mismos pasos |
| `RatDetailView.tsx` | 677 | Vista detalle con audit log timeline |
| `RatDetailModal.tsx` | 191 | Modal que alterna view/edit |
| `PdfPreview.tsx` | 99 | Preview PDF antes de descargar |
| `ratWizardValidation.ts` | 86 | Validación cliente por paso |

### 2.3 Cliente API (`frontend-next/lib/api.ts`)

| Función | Línea |
|---|---|
| `listarRats` | 172 |
| `getReportes` | 221 |
| `crearRat` | 255 |
| `actualizarRat` | 263 |
| `eliminarRat` | 271 |
| `sugerirRat` | 281 |
| `exportarCsv` | 363 |
| `exportarPdf` | 369 |
| `duplicarRat` | 393 |
| `registrarConsentimiento` | 883 |

### 2.4 Tipos (`frontend-next/types/index.ts`)

- `RAT` interface: líneas 55-116
- `RATSugerido`: líneas 41-53
- `RATWizardData`: línea 230

### 2.5 Constantes (`frontend-next/lib/constants.ts`)

11 catálogos:
- `BASES_LEGALES` (7), `DESCRIPCIONES_BASE`, `TIPOS_DATO_SENSIBLE` (7),
- `DATOS_NNA_OPCIONES` (4), `NIVEL_CONFIDENCIALIDAD_OPCIONES` (4),
- `ESTRUCTURA_DATO_OPCIONES`, `OPERACIONES_TRATAMIENTO_OPCIONES` (7),
- `AUTOMATIZACION_OPCIONES` (4), `FRECUENCIA_OPCIONES` (6),
- `ESTADO_MAP/LABEL`, `RIESGO_OPTIONS`

---

## 3. Tests existentes

| Archivo | Líneas | Cobertura |
|---|---|---|
| `test_rats.py` | 288 | CRUD, completitud, estados, aprobación, eliminación |
| `test_rat_tier1_tier2.py` | 325 | 15 campos Tier 1+2 |
| `test_rat_gaps_21719.py` | 178 | 5 campos Iter 10 |
| `rat_auditoria_test.py` | 84 | `/rats/{id}/auditoria` |
| `rat_archivo_test.py` | 150 | `/rats/{id}/archivo` |
| `test_security.py::TestRATValidators` | ~178 | Validadores condicionales |
| `test_exports.py` | — | PDF, CSV |
| `test_suggestions.py` | — | Sugerencias |

**E2E (Playwright):**
- `e2e/05-rat.spec.ts` (70 líneas)
- `e2e/15-rat-modal.spec.ts`

---

## 4. Estadísticas totales

| Métrica | Valor |
|---|---|
| Líneas Python RAT | ~2,000 (model + schemas + service + routes + repo) |
| Líneas TS RAT | ~2,500 (componentes + page + lib) |
| Endpoints | 20 |
| Campos modelo | 40 |
| Artículos Ley 21.719 cubiertos | 9 (Art. 2, 8, 12, 14 bis, 14 ter, 14 quater, 15 bis, 16, 16 BIS) |
| Tests pytest | ~1,200 líneas / 6 archivos |
| Tests E2E | 2 archivos Playwright |

---

## 5. Archivos clave

- `backend/app/models/rat.py` (209 líneas)
- `backend/app/schemas/rat.py` (252 líneas)
- `backend/app/services/rat_service.py` (640 líneas)
- `backend/app/routes/rats.py` (568 líneas)
- `frontend-next/components/rat/RatWizard.tsx` (~1300 líneas)
- `frontend-next/components/rat/RatEditForm.tsx` (805 líneas)
- `frontend-next/components/rat/RatDetailView.tsx` (677 líneas)