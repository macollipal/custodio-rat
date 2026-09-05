# Sprint 2 — ARCO-QW2 SLA Alert T-2 días + ARCO-QW1 Exportación CSV/Excel/PDF

**Fecha**: 2026-06-24
**Duración**: ~4 días
**Estado**: ✅ Completado

---

## Objetivo

Implementar las funcionalidades críticas de SLA y exportación para el módulo ARCO.

---

## ARCO-QW2: SLA Alert T-2 días

### Problema
Los tickets ARCO pueden vencer sin que el DPO se entere. El plazo legal es 10 días hábiles — se necesita alertar 2 días antes del vencimiento.

### Solución

#### Backend

**`TaskType.SLA_ALERT_T2`** — Nuevo tipo de tarea encola.

**`_run_sla_alert_t2()`** (`task_service.py`):
- Query tickets con `fecha_vencimiento <= ahora + 2 días` Y estado activo (`abierto`, `en_proceso`, `pendiente`, `subsanacion`, `prorroga`)
- Incluye tickets YA vencidos (`fecha_vencimiento < ahora`)
- Agrupa por empresa
- Envía email grupal al DPO con tabla de tickets ordenados por urgencia

**`notificar_sla_alert_t2()`** (`email_service.py`):
- Tabla HTML con: ID, Tipo, Titular, Responsable, Días restantes, Prioridad
- Color coding: rojo (#FEE2E2) para vencidos, amarillo (#FEF9C8) para T-2, verde para OK
- Badge: 🔴 VENCIDO / 🟡 T-Xd / 🟢 Xd
- Agrupa por responsable para facilitar asignación

**Endpoint `POST /admin/tasks/enqueue-sla-alerts`** (`admin_tasks.py`):
- Encola tarea `SLA_ALERT_T2` para ejecución inmediata
- Solo superadmin

#### Cron — GitHub Actions

**`.github/workflows/sla-alert.yml`**:
- Schedule: cada 4 horas (`cron: "0 */4 * * *"`)
- `workflow_dispatch` para ejecución manual
- Encola tarea → espera 2s → ejecuta `run?max_tasks=1`
- Requiere `SUPERADMIN_TOKEN` como secret

#### Frontend

**Banner de alerta en `tkt_solicitud_derecho/page.tsx`**:
- Aparece cuando `slaAlertTickets.length > 0` (tickets con <= 2 días)
- Muestra conteo: X vencido(s) · Y vence(n) en 2 días o menos
- Botón "Ver tickets" que cambia tab a 'abierto'
- `role="alert"`, `aria-label`

### Decisiones Técnicas
- **GitHub Actions** en vez de Vercel Cron Pro (gratuito, ya disponible)
- **No modifica `fecha_vencimiento`** — solo notifica, no extiende plazos
- **Email grupal por empresa** — 1 email con todos los tickets, agrupados por urgencia

---

## ARCO-QW1: Exportación CSV/Excel/PDF

### Problema
El DPO necesita exportar tickets ARCO para reportes, auditorías y presentaciones a la APDC.

### Solución

#### Backend

**`export_tkt_service.py`**:
- `generar_csv()` — `csv.writer` con delimitador `;`, encoding `utf-8-sig`
- `generar_excel()` — `openpyxl` con:
  - Header con fondo azul (#2563EB)
  - Freeze panes en fila 1
  - Auto-filter
  - Color coding de filas (rojo vencidos, amarillo T-2)
  - Columnas auto-adjust width
- `generar_pdf()` — `reportlab` con tabla compacta

**Endpoints** (`/export/tkt/csv`, `/export/tkt/excel`, `/export/tkt/pdf`):
- Filtros: `company_id`, `estado`, `prioridad`, `fecha_desde`, `fecha_hasta`
- Streaming response con `Content-Disposition: attachment`
- Validación de permisos: superadmin o acceso a la empresa

#### Frontend

**Dropdown "⬇ Exportar"** en `tkt_solicitud_derecho/page.tsx`:
- 3 opciones: 📄 CSV, 📊 Excel (.xlsx), 📑 PDF
- Filtra por tab activo (estado actual)
- `downloadBlob()` helper para trigger de descarga
- Toast de confirmación

### Dependencias
- `openpyxl==3.1.5` agregado a `requirements.txt`

---

## Archivos Creados/Modificados

### Backend
| Archivo | Cambio |
|---------|--------|
| `app/models/task.py` | + `SLA_ALERT_T2` al enum `TaskType` |
| `app/services/email_service.py` | + `notificar_sla_alert_t2()` |
| `app/services/task_service.py` | + `_run_sla_alert_t2()` + handler en `run_task()` |
| `app/routes/admin_tasks.py` | + endpoint `POST /enqueue-sla-alerts` |
| `app/services/export_tkt_service.py` | **NUEVO** — CSV/Excel/PDF |
| `app/routes/export_tkt.py` | **NUEVO** — endpoints `/export/tkt/*` |
| `app/main.py` | + import `export_tkt` + `app.include_router(export_tkt.router)` |
| `requirements.txt` | + `openpyxl==3.1.5` |
| `.github/workflows/sla-alert.yml` | **NUEVO** — cron cada 4h |

### Frontend
| Archivo | Cambio |
|---------|--------|
| `lib/api.ts` | + `exportarTktCsv/Excel/Pdf()` + `descargarTktCsv/Excel/Pdf()` |
| `app/(app)/tkt_solicitud_derecho/page.tsx` | + SLA Alert Banner + Export dropdown |

### Docs
| Archivo | Cambio |
|---------|--------|
| `docs/backlog_seguimiento.md` | Actualizado: Sprint 1 ✅, Sprint 2 ✅, QW3 ⏸️ Postergado |
| `docs/sprints/sprint_1_arco_formadmin.md` | **NUEVO** |
| `docs/sprints/sprint_2_arco_sla_export.md` | **NUEVO** |

---

## Postergado

### ARCO-QW3: Firma digital + timestamp en respuesta

**Razón**: El usuario prefiere no implementarla aún. Requiere:
- Integración con audit chain
- Integración con eIPD (Evaluación de Impacto en Protección de Datos)
- Sistema de identidad digital (Clave Única o eIPD)
- Definición de: quién firma, cómo se verifica identidad, dónde se almacena el hash

**Evaluado para Sprint 4+**.

---

## Next Steps Sugeridos (Sprint 3)

| # | Quick Win | Impacto | Esfuerzo |
|---|-----------|---------|----------|
| 1 | Bandeja de entrada del DPO (dashboard ARCO unificado) | ALTO | 3 días |
| 2 | Dashboard "derechos más ejercidos" | MEDIO | 1.5 días |
| 3 | Recordatorio automático al titular (T-3 días) | ALTO | 2 días |
| 4 | Portal del titular con descarga de respuesta | ALTO | 2 días |
