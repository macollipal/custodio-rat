# Auditoría v1.9 — 2026-07-05

## Resumen Ejecutivo

Auditoría post-Iter 13 del audit-loop. Se documentan: IDOR multi-tenant en 6 endpoints RAT (CRÍTICO), base_legal_valida strict, ConsentimientoAlert, homologación orden campos RAT entre wizard/drawer/PDF, y PDF con títulos de sección azules. Score impulsado de **6.3/10 → 6.7/10** (audit-loop RAT/ARCO/Brechas).

## Score Arquitectónico (Audit-Loop Methodology)

| Categoría | Puntuación |
|-----------|------------|
| RAT | 6.5/10 |
| ARCO | 6.8/10 |
| Brechas | 5.9/10 |
| **TOTAL** | **6.7/10** |
| Delta vs iter 12 | +0.4 |

## Cambios en Código (Iter 13)

### Fixes de Seguridad CRÍTICOS
- **IDOR multi-tenant**: `get_rat_for_user()` en 6 endpoints de `rats.py` (`GET`, `PUT`, `DELETE`, `POST /revision`, `POST /aprobar`, `GET /auditoria`) — retorna 404 si empresa no coincide, superadmin accede a todos
- **base_legal_valida strict**: validación contra enum taxativo de 6 opciones (antes siempre retornaba `v.strip()` sin verificar)

### Fixes de Compliance y UX
- **ConsentimientoAlert**: `RatEditForm.handleSave()` ahora llama `listarConsentimientos(company_id, rat.id, true)` antes de guardar — si `datos_sensibles=True` y no hay consentimiento activo → toast error y no guarda
- **Homologación orden campos RAT**: RatDetailView, RatEditForm, RatWizard y export_service.py reordenados al mismo orden canónico de 5 pasos
- **PDF con títulos de sección**: `PASO 1 — IDENTIFICACIÓN`, `PASO 2 — DATOS TRATADOS`, etc. con fondo `COLOR_PRIMARIO #1B3A6B` y texto blanco bold

### Fixes de Calidad
- **Encoding UTF-8 corregido**: `ALERTAS_AUDITORIA` (garabatos → emojis), regex `a├▒o` → `año`, `base_legal_valida` con tildes, `conftest.py` fixture `rat_base`, `main.py` log seed admin
- **Código muerto eliminado**: return duplicado `rats.py:291`, `model_dump` duplicado `rat_service.py:253`
- **Test approval workflow corregido**: `test_cambiar_estado_a_aprobado` ahora usa POST `/rats/{id}/aprobar` con RAT completo (25 campos)
- **TestCompletitud estructura corregida**: 4 métodos huérfanos con indentación corregida

### Tests Nuevos
- **TestIDORMultiTenantRAT** (`test_security.py`): 5 tests cubriendo empresa B no puede ver/actualizar/eliminar/auditar RAT de empresa A → 404; superadmin sí puede

## Hallazgos por Severidad

### Críticos
- (ninguno — IDOR multi-tenant resuelto en este iter)

### Altos
- (ninguno)

### Medios
- (ninguno)

### Bajos
- (ninguno)

## Fortalezas Detectadas
- Workflow de approval RAT con POST `/aprobar` correctamente implementaddo con 25 campos
- Homologación completa de orden de campos entre frontend y backend
- Encoding UTF-8 saneado en todo el backend
- Tests IDOR ejecutándose en CI

## Pendientes Críticos (No Abordados)
- Z-01: Security headers (CSP, X-Frame-Options)
- Z-02: CORS restrictivo por ruta
- Z-03: File upload validation (tipo MIME — resuelto parcialmente con BYTEA 10MB)
- Z-04: `categoria_titulares nullable=False` — requiere ALTER TABLE migration (breaking change BD)
- Z-06: Logs estructurados (JSON) — pendiente audit_log table

## Cadena de Commits

| Commit | Descripción |
|--------|-------------|
| `1894a4e` | fix(export): PDF con títulos de sección por paso + estilo cabecera azul |
| `ed6d994` | fix: homologar orden campos RAT — drawer, wizard y PDF |
| `6583cf5` | fix(backend+tests): encoding UTF-8 corrupto + test approval workflow + estructura clase |
| `e7318f6` | fix(backend): cerrar IDOR multi-tenant + eliminar código muerto RAT |
| `eb90e8b` | fix(frontend): corregir ortografía en constantes y labels RAT |

## Documentación Regenerada (v1.9)

| Doc | Archivo | Estado |
|-----|---------|--------|
| 02 | `02_Requisitos_Custodio_RAT_Manager_v1.9.docx` | ✅ |
| 03 | `03_Historias_Usuario_Custodio_RAT_Manager_v1.9.docx` | ✅ |
| 04 | `04_Casos_de_Uso_Custodio_RAT_Manager_v1.9.docx` | ✅ |
| 06 | `06_Arquitectura_Software_Custodio_RAT_Manager_v1.9.docx` | ✅ |
| 08 | `08_API_REST_Custodio_RAT_Manager_v1.9.docx` | ✅ |
| 09 | `09_Backlog_Producto_Custodio_RAT_Manager_v1.9.docx` | ✅ |
| 10 | `10_Plan_QA_Custodio_RAT_Manager_v1.9.docx` | ✅ |
| 12 | `12_Manual_Tecnico_Custodio_RAT_Manager_v1.9.docx` | ✅ |
| MTX | `Matriz_Trazabilidad_Custodio_RAT_Manager_v1.9.docx` | ✅ |

## Nuevos RFs (Iter 13)

| ID | Prioridad | Descripción |
|----|-----------|-------------|
| RF-163 | CRÍTICO | IDOR multi-tenant en 6 endpoints RAT |
| RF-164 | ALTO | base_legal_valida strict contra enum taxativo |
| RF-165 | ALTO | ConsentimientoAlert en RatEditForm.handleSave() |
| RF-166 | ALTO | Homologación orden campos RAT (5 pasos canónicos) |
| RF-167 | MEDIO | PDF con títulos de sección y alertas rojas |
| RF-168 | MEDIO | Encoding UTF-8 corregido en backend |
| RF-169 | BAJA | Código muerto eliminado |

## Evaluación de Madurez
- **Estado actual:** Producción Inicial
- **Qué falta para el siguiente nivel:** paginación listados, retry OCI uploads, audit_log table, Z-01/Z-02/Z-04/Z-06
