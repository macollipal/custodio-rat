# HALLAZGOS v1.4 — 12 JUNIO 2026
## Custodio RAT Manager

---

## RESUMEN DE HALLAZGOS

| Severidad | Cantidad | Estado |
|-----------|----------|--------|
| Críticos | 0 | — |
| Altos | 2 | Documentar |
| Medios | 3 | Documentar |
| Bajos | 2 | Informar |
| **Total** | **7** | — |

---

## HALLAZGOS ALTOS

### H-001: Endpoint `/rats/{id}/archivo` no documentado en API

**Severidad:** Alto
**Categoría:** Documentación
**Ubicación:** `backend/app/routes/rats.py:341-381`
**Descripción:**
El endpoint `GET /rats/{rat_id}/archivo` para descarga de documentos de base legal con fallback chain OCI (PAR → signed GET → BYTEA) no está documentado en el doc 08_API v1.3.

**Impacto:**
- Usuarios no saben que existe la funcionalidad de descarga
- DPOs no pueden auditar descargas de archivos

**Recomendación:**
- Agregar endpoint `/rats/{rat_id}/archivo` a 08_API con descripción del fallback chain
- Documentar los campos de respuesta: `url`, `nombre`, `content_type`, `expires_in_seconds`

**Estado:** _Agregar a documentación v1.4_

---

### H-002: Endpoints `/admin/asesor/*` no documentados

**Severidad:** Alto
**Categoría:** Documentación
**Ubicación:** `backend/app/routes/admin_asesor.py`
**Descripción:**
Los 3 endpoints de administración del asesor IA no están documentados en ningún documento:
- `POST /admin/asesor/index` — Indexar corpus
- `GET /admin/asesor/stats` — Estadísticas del corpus
- `DELETE /admin/asesor/documents/{chunk_id}` — Eliminar chunk

**Impacto:**
- Superadmin no sabe que existen herramientas de gestión del asesor
- No hay documentación sobre cómo mantener el corpus actualizado

**Recomendación:**
- Agregar sección "Módulo Asesor IA" en 08_API
- Documentar los 3 endpoints con ejemplos de request/response
- Agregar RF correspondiente en 02_Requisitos

**Estado:** _Agregar a documentación v1.4_

---

## HALLAZGOS MEDIOS

### M-001: Modelo AsesorChunk no documentado en Modelo de Datos

**Severidad:** Medio
**Categoría:** Documentación
**Ubicación:** `backend/app/models/asesor.py`
**Descripción:**
El modelo `AsesorChunk` utilizado para almacenar los fragmentos del corpus de IA no está incluido en el doc 07_Modelo_Datos.

**Impacto:**
- Falta trazabilidad de la estructura de datos del asesor IA
- No se documenta la relación con el modelo Asesor

**Recomendación:**
- Verificar si 07_Modelo_Datos necesita actualización o si el módulo asesor está fuera del alcance

**Estado:** _Verificar alcance del doc 07_

---

### M-002: Campo `archivo_base_legal_storage_url` en RAT no documentado

**Severidad:** Medio
**Categoría:** Documentación
**Ubicación:** `backend/app/models/rat.py`, `backend/app/schemas/rat.py`
**Descripción:**
El campo `archivo_base_legal_storage_url` (almacenamiento OCI) y sus campos relacionados (`archivo_base_legal_hash`, `archivo_base_legal_nombre`, `archivo_base_legal_tipo`) no están explícitamente documentados en el doc 07.

**Impacto:**
- No se entiende cómo funciona el almacenamiento híbrido OCI + BYTEA
- No hay documentación sobre la estrategia de fallback

**Recomendación:**
- Agregar nota sobre almacenamiento OCI en 07_Modelo_Datos
- Documentar el campo `storage_url` como alternativa a `datos` (BYTEA)

**Estado:** _Agregar a documentación v1.4_

---

### M-003: Servicio de sugerencias RAT usa lógica de negocio duplicada

**Severidad:** Medio
**Categoría:** Deuda Técnica
**Ubicación:** `backend/app/services/suggestion_service.py`
**Descripción:**
La función `sugerir_rat()` y `listar_tipos_proceso()` contienen lógica de sugerencia que podría beneficiarse de mejoras en el corpus del asesor IA.

**Impacto:**
- Mantenimiento dividido entre dos sistemas de sugerencia
- Posible inconsistencia entre sugerencias del formulario y del chat IA

**Recomendación:**
- Evaluar unificación de lógica de sugerencias
- Considerar usar el corpus del asesor como fuente única de conocimiento regulatorio

**Estado:** _Informar — sin acción inmediata_

---

## HALLAZGOS BAJOS

### B-001: Ausencia de tests para endpoint `/rats/{id}/archivo`

**Severidad:** Bajo
**Categoría:** Testing
**Ubicación:** `backend/tests/`
**Descripción:**
No existen tests específicos para el endpoint de descarga de archivos con fallback chain OCI.

**Impacto:**
- No hay validación automática del fallback chain
- Riesgo de regressions en la descarga de archivos

**Recomendación:**
- Agregar tests para descarga BYTEA, OCI, y fallback

**Estado:** _Agregar a backlog de testing_

---

### B-002: No hay documentación sobre límites de Rate Limiting

**Severidad:** Bajo
**Categoría:** Documentación
**Ubicación:** `backend/app/core/limiter.py`
**Descripción:**
El rate limiting está implementado pero no hay documentación clara sobre los límites por endpoint.

**Impacto:**
- Usuarios no saben qué límites aplican
- Posible confusión en producción

**Recomendación:**
- Documentar límites en 08_API: `/auth/login` (5/min), `/ai/ask` (10/min), etc.

**Estado:** _Agregar a documentación v1.4_

---

## HALLAZGOS RESUELTOS DESDE v1.3

| ID | Descripción | Resuelto |
|----|-------------|----------|
| — | Sin hallazgos críticos pendientes | — |

---

*Documento generado: 12 Junio 2026*
*Hallazgos Custodio RAT Manager v1.4*