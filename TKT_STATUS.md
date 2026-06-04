# RAT - Módulo TKT Solicitudes ARCO

## Estado: ✅ Backend Completado | 🚧 Frontend Completado (listo para deploy)

---

## Objetivo
Reemplazar el módulo antiguo `solicitudes_derecho` (en tab "Configuración") por el nuevo módulo **TKT** con ticketing, SLA y notas internas.

---

## Backend ✅ (Completado)

### Modelos
- `backend/app/models/tkt_solicitud_derecho.py` — modelo principal con SLA (fecha_vencimiento, días hábiles Chile)
- `backend/app/models/tkt_nota.py` — notas internas
- `backend/app/models/tkt_adjunto.py` — adjuntos (pendiente implementación)
- `backend/app/models/tkt_historial.py` — historial de cambios

### Routes + Service
- `backend/app/routes/tkt_solicitud_derecho.py` — CRUD + dashboard KPIs
- `backend/app/services/ticket_service.py` — lógica SLA, crear_ticket, crear_ticket_desde_solicitud, get_dashboard_stats, calcular_dias_habiles()
- `backend/app/schemas/tkt_solicitud_derecho.py` — schemas Pydantic con enums validados

### Índices agregados
- `idx_tkt_estado_company` en (estado, company_id)
- `idx_tkt_fecha_vencimiento` en fecha_vencimiento
- `idx_tkt_estado_prioridad` en (estado, prioridad)

### Notas
- El endpoint público `/solicitudes-derecho/` ahora crea automáticamente un TktSolicitudDerecho al recibir una solicitud
- Día hábiles Chile: lunes-viernes, excluye feriados fijos Chile
- Enums validados: TktTipoEnum, TktEstadoEnum, TktPrioridadEnum, TktOrigenEnum
- Historial se registra en cambios de estado (PATCH ahora usa `cambiar_estado_ticket()`)
- Rol `usuario` tiene acceso solo lectura (no puede crear/editar tickets)

---

## Frontend ✅ (Completado)

### Archivos creados
- `frontend-next/app/(app)/tkt_solicitud_derecho/page.tsx` — bandeja + dashboard KPIs + drawer detalle

### Archivos modificados
- `frontend-next/components/layout/Sidebar.tsx` — agregado ítem "Solicitudes ARCO"
- `frontend-next/app/(app)/layout.tsx` — agregado case para `tkt_solicitud_derecho`

### API functions usadas (ya existentes en `lib/api.ts`)
```typescript
listarTktTickets(companyId, estado, prioridad) → GET /tkt-solicitud-derecho/
getTktDashboard(companyId) → GET /tkt-solicitud-derecho/dashboard
getTktTicket(id) → GET /tkt-solicitud-derecho/{id}
actualizarTktTicket(id, data) → PATCH /tkt-solicitud-derecho/{id}
agregarTktNota(ticketId, nota) → POST /tkt-solicitud-derecho/{ticketId}/notas
listarTktNotas(ticketId) → GET /tkt-solicitud-derecho/{ticketId}/notas
listarTktHistorial(ticketId) → GET /tkt-solicitud-derecho/{ticketId}/historial
```

---

## Diseño (Implementado)

### Dashboard KPIs (top)
6 cards en grid: Total | Abiertos | En Proceso | Pendientes | Resueltos | Vencidos
+% cumplimiento SLA (barra verde/amarillo/rojo)

### Bandeja (tabs)
Abiertos | En Proceso | Pendientes | Resueltos | Vencidos | Todos

### Tabla tickets
| Columna | Detalle |
|---------|---------|
| Tipo | Badge con abreviatura (AC/RC/CA/OP) y color |
| Titular | Nombre + RUT |
| Email | Mail del titular |
| Prioridad | Badge: alta (rojo), normal (amarillo), baja (gris) |
| Estado | Badge con color semántico (visible en lg+) |
| SLA | Días restantes con color: verde (>5), amarillo (3-5), rojo (<=2) |
| Fecha | Fecha recepción |
| Acción | Botón "Ver" |

### Drawer detalle (al clickear fila)
1. **Header** — tipo + estado badge + prioridad badge + nombre titular
2. **SLA** — fecha vencimiento + días restantes (color semafórico)
3. **Datos titular** — nombre, RUT, email, fecha recepción
4. **Descripción** — texto original de la solicitud
5. **Respuesta** — select estado + textarea respuesta + botón guardar (solo admin)
6. **Notas internas** — listar notas + form agregar nota (solo admin)
7. **Historial** — timeline de cambios de estado

### Filtros
- Tabs por estado (Abiertos, En Proceso, Pendientes, Resueltos, Vencidos, Todos)
- Refresh button

---

## Navegación Sidebar
```typescript
{ key: 'tkt_solicitud_derecho', label: 'Solicitudes ARCO', icon: '📋', roles: ['superadmin', 'admin_empresa', 'usuario'] }
```

---

## Deploy y Test QA
- QA Backend: `https://custodio-api-qa-git-qa-marcelos-projects-3cc299e0.vercel.app`
- QA Frontend: `https://custodio-qa.vercel.app`
- Login QA: `admin` / `Admin1234!`
- DB QA: `ep-fragrant-wildflower-apeqosx9-pooler.c-7.us-east-1.aws.neon.tech/neondb`

### Tablas TKT ya creadas en QA
- `tkt_solicitud_derecho`
- `tkt_notas`
- `tkt_adjuntos`
- `tkt_historial`

### 5 solicitudes ya migradas
- Estado: `abierto` (menos #5 que era `resuelto`)

---

## Siguientes Pasos
1. ✅ Crear page tkt_solicitud_derecho
2. ✅ Actualizar Sidebar
3. ⬜ Deploy frontend a Vercel QA
4. ⬜ Testear flujo end-to-end
5. ⬜ Verificar que tab antiguo en Configuración ya no se usa (futuro: deprecar)
