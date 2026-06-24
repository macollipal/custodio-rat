# Diff: Código vs Documentación v1.7

## Resumen

| Aspecto | Estado |
|---------|--------|
| Código documentado en doc 02 (Requisitos) | ✅ RF-137 a RF-140 |
| Código documentado en doc 03 (HUs) | ✅ HU-072 a HU-085 |
| Código documentado en doc 04 (CUs) | ✅ CU-059 a CU-068 |
| Código documentado en doc 06 (Arquitectura) | ✅ ADR-19 a ADR-22 |
| Código documentado en doc 08 (API) | ✅ 4 endpoints nuevos |
| Código documentado en doc 09 (Backlog) | ✅ |
| Código documentado en doc 10 (Plan QA) | ✅ TC-020 a TC-029 |
| Código documentado en doc 12 (Manual Técnico) | ✅ export_tkt + sla_alert |
| Código documentado en doc MTX (Trazabilidad) | ✅ HU→TC Sprint 1+2 |

## Endpoints Sprint 2 vs Doc 08 (API)

| Endpoint | Implementado | Documentado v1.7 | Estado |
|----------|-------------|------------------|--------|
| `GET /export/tkt/csv` | ✅ | ✅ | OK |
| `GET /export/tkt/excel` | ✅ | ✅ | OK |
| `GET /export/tkt/pdf` | ✅ | ✅ | OK |
| `POST /admin/tasks/enqueue-sla-alerts` | ✅ | ✅ | OK |

## Features Sprint 1 vs Doc 02 (Requisitos)

| RF | Feature | Implementado | Documentado |
|----|---------|-------------|-------------|
| RF-129 | Validación RUT en vivo | ✅ | ✅ |
| RF-130 | Confirmación email doble input | ✅ | ✅ |
| RF-131 | Tooltip campo Tipo ARCO | ✅ | ✅ |
| RF-132 | Helper text Prioridad | ✅ | ✅ |
| RF-133 | Detección titular duplicado | ✅ | ✅ |
| RF-134 | Selector RAT con búsqueda | ✅ | ✅ |
| RF-135 | Campos representante legal | ✅ | ✅ |
| RF-136 | Date picker retroactiva + nuevos campos | ✅ | ✅ |

## Features Sprint 2 vs Doc 02 (Requisitos)

| RF | Feature | Implementado | Documentado |
|----|---------|-------------|-------------|
| RF-137 | WCAG básico aria-label | ✅ | ✅ |
| RF-138 | SLA Alert T-2 días | ✅ | ✅ |
| RF-139 | GitHub Actions workflow | ✅ | ✅ |
| RF-140 | Export CSV/Excel/PDF | ✅ | ✅ |

## Tests Sprint 2 vs Doc 10 (Plan QA)

| TC | Descripción | Implementado | Documentado |
|----|-------------|-------------|-------------|
| TC-020 | Validar RUT con dígito verificador | ✅ | ✅ |
| TC-021 | Validar RUT inválido → error | ✅ | ✅ |
| TC-022 | Email doble input no coincide | ✅ | ✅ |
| TC-023 | Titular duplicado debounce 800ms | ✅ | ✅ |
| TC-024 | Selector RAT debounce 300ms | ✅ | ✅ |
| TC-025 | Encolar SLA Alert T-2 días | ✅ | ✅ |
| TC-026 | Exportar CSV con filtros | ✅ | ✅ |
| TC-027 | Exportar Excel con color coding | ✅ | ✅ |
| TC-028 | Exportar PDF con tabla compacta | ✅ | ✅ |
| TC-029 | Dropdown Exportar UI | ✅ | ✅ |

## Gap G1: Doc 08 (API) — Estado de Drift

| Versión | Endpoints documentados | Drift |
|---------|----------------------|-------|
| v1.4 | ~50 endpoints | Base |
| v1.5 | No regenerado | +10 endpoints nuevos |
| v1.6 | No regenerado | +4 endpoints nuevos |
| v1.7 | 60+ endpoints | ✅ Cerrado |

**Endpoints nuevos entre v1.4 y v1.7:**
- `/export/tkt/{csv,excel,pdf}` (Sprint 2)
- `/admin/tasks/enqueue-sla-alerts` (Sprint 2)
- `/tkt-solicitud-derecho/` (nuevos endpoints admin)
- `/tkt-reglas-asignacion/*` (completado)
- `/tkt-plantillas/*` (completado)
- `/admin/tasks/enqueue-sla-alerts` (Sprint 2)

## Comparativa: Contenido Nuevo vs Reorganizado

| Doc | Contenido Nuevo | Contenido Reorganizado | `_subrayado_` |
|-----|----------------|----------------------|---------------|
| 02 | RF-129 a RF-140 | — | ✅ |
| 03 | HU-072 a HU-085 | — | ✅ |
| 04 | CU-059 a CU-068 | — | ✅ |
| 06 | ADR-19 a ADR-22 | — | ✅ |
| 08 | 4 endpoints nuevos | — | ✅ |
| 09 | Backlog actualizado | — | ✅ |
| 10 | TC-020 a TC-029 | — | ✅ |
| 12 | export_tkt, sla_alert, workflow | — | ✅ |
| MTX | HU→TC Sprint 1+2 | — | ✅ |

**Total contenido nuevo: ~60 items** (todos con `_subrayado_`)
**Total contenido reorganizado: 0 items** (ninguno marcado)
