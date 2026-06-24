# Inventario v1.7 — 2026-06-24

## Archivos del Sprint 2 (Código)

### Nuevos
| Archivo | Descripción |
|---------|-------------|
| `backend/app/routes/export_tkt.py` | 3 endpoints REST: CSV, Excel, PDF |
| `backend/app/services/export_tkt_service.py` | Generadores csv/excel/pdf |
| `backend/tests/test_export_tkt.py` | 11 tests para export |
| `backend/tests/test_sla_alert.py` | 7 tests para SLA alert |
| `.github/workflows/sla-alert.yml` | Cron 4h + workflow_dispatch |

### Modificados
| Archivo | Cambio |
|---------|--------|
| `backend/app/models/task.py` | `TaskType.SLA_ALERT_T2` |
| `backend/app/services/task_service.py` | `_run_sla_alert_t2()` + handler |
| `backend/app/services/email_service.py` | `notificar_sla_alert_t2()` |
| `backend/app/routes/admin_tasks.py` | `POST /enqueue-sla-alerts` |
| `backend/app/routes/admin_tasks.py` | Handler para SLA_ALERT_T2 |
| `backend/app/main.py` | Registro de `export_tkt.router` |
| `backend/requirements.txt` | `openpyxl==3.1.5` |
| `frontend-next/app/(app)/tkt_solicitud_derecho/page.tsx` | SlaAlertBanner + Export dropdown |
| `frontend-next/lib/api.ts` | `descargarTktCsv/Excel/Pdf()` + `downloadBlob()` |

## Documentación Sprint 1 (ya en qa)

| Archivo | Descripción |
|---------|-------------|
| `docs/sprints/sprint_1_arco_formadmin.md` | Sprint 1 completo |

## Documentación Sprint 2

| Archivo | Descripción |
|---------|-------------|
| `docs/sprints/sprint_2_arco_sla_export.md` | Sprint 2 completo |

## Scripts de Build v1.7

| Script | Doc | Estado |
|--------|-----|--------|
| `build_02_requisitos_v1_7.py` | 02 | ✅ Ejecutado |
| `build_03_historias_usuario_v1_7.py` | 03 | ✅ Ejecutado |
| `build_04_casos_uso_v1_7.py` | 04 | ✅ Ejecutado |
| `build_06_arquitectura_v1_7.py` | 06 | ✅ Ejecutado |
| `build_08_api_v1_7.py` | 08 | ✅ Creado desde cero |
| `build_09_backlog_v1_7.py` | 09 | ✅ Ejecutado |
| `build_10_plan_qa_v1_7.py` | 10 | ✅ Ejecutado |
| `build_12_manual_tecnico_v1_7.py` | 12 | ✅ Ejecutado |
| `build_MTX_matriz_v1_7.py` | MTX | ✅ Ejecutado |

## Archivos de Auditoría v1.7

| Archivo | Descripción |
|---------|-------------|
| `AUDITORIA_V1.7.md` | Resumen ejecutivo + score |
| `HALLAZGOS.md` | Detalle de hallazgos |
| `CIERRE_SESION_v1.7.md` | Cierre de sesión |
| `INVENTARIO_v1.7.md` | Este archivo |
| `_scripts/` | 9 scripts adaptados + _theme_custodio.py |

## Dependencias Agregadas

| Paquete | Versión | Uso |
|---------|---------|-----|
| `openpyxl` | 3.1.5 | Exportar a Excel con color coding |
