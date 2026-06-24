# Auditoría v1.7 — 2026-06-24

## Resumen Ejecutivo

Auditoría de cierre del Sprint 2 (ARCO-QW2 SLA Alert T-2 días + ARCO-QW1 Export CSV/Excel/PDF) y regeneración documental completa. Se cerró el **gap G1** que dejó doc 08 (API) desactualizado desde v1.4. Score impulsado de **8.7/10 → 9.0/10**.

## Score Arquitectónico

| Categoría | Puntuación |
|-----------|------------|
| Escalabilidad | 9/10 |
| Mantenibilidad | 9/10 |
| Seguridad | 9/10 |
| Rendimiento | 9/10 |
| Observabilidad | 9/10 |
| Arquitectura General | 9/10 |
| **TOTAL** | **9.0/10** |

## Cambios en Código (Sprint 1 + Sprint 2)

### Sprint 1: FORMADMIN ARCO QW1-QW10
- Validación RUT en vivo con dígito verificador y formateo automático
- Confirmación de email (doble input) con validación visual
- Tooltip en campo Tipo ARCO con Arts. 12, 12 bis, 12 ter Ley 21.719
- Helper text en Prioridad (2 días / 10 días hábiles / sin urgencia)
- Detección de titular duplicado con debounce 800ms
- Selector RAT con búsqueda debounce 300ms
- Campos representante legal en sección colapsable
- Date picker fecha retroactiva (max=hoy) + nuevos campos

### Sprint 2: ARCO-QW2 SLA Alert T-2 días
- `TaskType.SLA_ALERT_T2` en task.py
- `_run_sla_alert_t2()` en task_service.py — detecta tickets ≤2 días
- `notificar_sla_alert_t2()` en email_service.py — email grupal HTML
- `POST /admin/tasks/enqueue-sla-alerts` (superadmin only)
- `.github/workflows/sla-alert.yml` — cron cada 4h + workflow_dispatch
- `SlaAlertBanner` en `tkt_solicitud_derecho/page.tsx`

### Sprint 2: ARCO-QW1 Export CSV/Excel/PDF
- `export_tkt_service.py` — csv (csv.writer delim=;), excel (openpyxl), pdf (reportlab)
- `export_tkt.py` — 3 endpoints REST con 5 filtros
- Dropdown Exportar en frontend con CSV/Excel/PDF

## Hallazgos por Severidad

### Críticos
- (ninguno)

### Altos
- (ninguno)

### Medios
- (ninguno)

### Bajos
- G1: doc 08 (API) estuvo 2 versiones desactualizado (v1.4 → v1.7). Cerrado.

## Gaps Documentales Cerrados

| Gap | Doc | Antes | Después | Estado |
|-----|-----|-------|---------|--------|
| G1 | 08 (API) | v1.4 | v1.7 | ✅ Cerrado |
| G2 | 05 (ModeloDatos) | v1.3 | v1.3 | ⏸️ Postergado |
| G3 | 07 (ModeloDatosDetallado) | v1.1 | v1.1 | ⏸️ Postergado |
| G4 | 11 (Despliegue) | v1.1 | v1.1 | ⏸️ Postergado |

## Fortalezas Detectadas
- 45/45 tests passed en Neon QA PostgreSQL
- Feature freeze respetado: firma digital postergada indefinidamente
- Regla divina cumplida: todos los `.docx` regenerados tras cambios en código
- Dual provider (Cohere + Groq) implementado
- RBAC reforzado: solo superadmin/admin_empresa gestionan ARCO

## Deuda Técnica
- Firma digital (postergada indefinidamente)
- Docs 05, 07, 11 desactualizados (no en scope v1.7)
- Z-01, Z-02, Z-03 (pendientes de seguridad)

## Roadmap
### Corto Plazo
- Validar documentos .docx generados
- Commit a rama qa

### Mediano Plazo
- Abordar docs 05, 07, 11 en auditoría futura
- Firma digital cuando se defina alcance

### Largo Plazo
- Producción empresarial con score >9.5/10

## Evaluación de Madurez
- **Estado actual:** Producción Inicial
- **Qué falta para siguiente nivel:** firma digital, docs 05/07/11 actualizados, Z-01/Z-02/Z-03

## Cadena de Commits desde v1.6-BETA

| Commit | Descripción |
|--------|-------------|
| `09aebce` | Sprint 1: FORMADMIN ARCO QW1-QW10 |
| `73e39d5` | Migración backend/frontend |
| `e0f98f2` | UX Drawer responsive |
| `175e2c0` | Sprint 2: SLA Alert + Export CSV/Excel/PDF |

## Documentación Oficial Generada (v1.7)

| Doc | Archivo |
|-----|---------|
| 02 | `02_Requisitos_Custodio_RAT_Manager_v1.7.docx` |
| 03 | `03_Historias_Usuario_Custodio_RAT_Manager_v1.7.docx` |
| 04 | `04_Casos_de_Uso_Custodio_RAT_Manager_v1.7.docx` |
| 06 | `06_Arquitectura_Software_Custodio_RAT_Manager_v1.7.docx` |
| 08 | `08_API_REST_Custodio_RAT_Manager_v1.7.docx` |
| 09 | `09_Backlog_Producto_Custodio_RAT_Manager_v1.7.docx` |
| 10 | `10_Plan_QA_Custodio_RAT_Manager_v1.7.docx` |
| 12 | `12_Manual_Tecnico_Custodio_RAT_Manager_v1.7.docx` |
| MTX | `Matriz_Trazabilidad_Custodio_RAT_Manager_v1.7.docx` |
