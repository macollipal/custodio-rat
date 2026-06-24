# Sprint 1 — Formulario Admin ARCO QW1-QW10 + Formulario Público QW2/QW6

**Fecha**: 2026-06-23
**Duración**: 1 día
**Estado**: ✅ Completado

---

## Objetivo

Implementar el formulario admin ARCO (nueva solicitud manual) con las 10 mejoras QW1-QW10 identificadas en la consultoría DPO+PM+UX+Auditor, más los quick wins QW2 y QW6 del formulario público.

---

## Deliverables

### Form Admin ARCO — QW1-QW10

| # | Quick Win | Implementación |
|---|-----------|---------------|
| QW1 | Validar + formatear RUT en vivo | `validarRUT()` con algoritmo chileno + formateo automático `12.345.678-9` |
| QW2 | Confirmación de email (doble input) | Segundo campo `confirmarEmail` con validación visual (borde rojo si no coincide) |
| QW3 | Dropdown Tipo con descripciones e iconos | Tooltip ⓘ junto al label con Art. 12/12 bis/12 ter |
| QW4 | Helper text en Prioridad | Tooltip ⓘ con "2 días hábiles / 10 días hábiles / sin urgencia" |
| QW5 | Artículos Ley 21.719 visibles por tipo | Mismo tooltip que QW3 — artículos convertidos a texto legible |
| QW6 | Detección de titular duplicado | Banner amarillo expandable tras 800ms debounce, `checkDuplicadoTkt()` |
| QW7 | Selector de RAT en el form | Búsqueda con 300ms debounce, `listarRats()` |
| QW8 | Campos de representante legal | `representante_nombre` + `representante_rut` en sección colapsable |
| QW9 | Date picker para fecha retroactiva | `max=hoy` en input date |
| QW10 | WCAG básico (aria-label, aria-required) | Atributos agregados a todos los campos del formulario |

### UX Sprint 1

- Homologación de tamaño: `CreateTicketForm` con `size="lg"` (consistente con `TicketDrawer`)
- 5 secciones con headers: Clasificación, Datos titular, Contexto, Representante (colapsable), Detalle
- Helper text → tooltip ⓘ (click/tap) — ahorra ~80px verticales
- Asterisco rojo `*` en campos obligatorios
- Banner duplicado sticky en la parte superior del form
- Sección Representante legal colapsable (default cerrado)
- Pantalla éxito público: `max-w-md` → `max-w-lg` (512px)
- Componentes extraídos (`FieldLabel`, `TooltipIcon`, `SectionHeader`) fuera del cuerpo del componente

### Form Público ARCO

| # | Quick Win | Implementación |
|---|-----------|---------------|
| QW2 | Banner de privacidad + link política | Banner role="note" en encabezado + link "Consultar estado" en pantalla de éxito |
| QW6 | CTA "Consultar estado" en pantalla de éxito | Link al portal de seguimiento |

---

## Cambios en Backend

### Modelo `TktSolicitudDerecho`
Nuevos campos: `telefono` (VARCHAR 50), `fecha_nacimiento` (DATE), `pais` (VARCHAR 100), `representante_nombre`, `representante_rut`

### Servicio `crear_ticket()` (`ticket_service.py`)
Acepta 5 campos nuevos: `representante_nombre`, `representante_rut`, `telefono`, `fecha_nacimiento`, `pais`

### Endpoint `GET /check-duplicado`
Detecta duplicados por `email + tipo + company` en los últimos 90 días.

### Schema `TktTicketCreate` + `TktTicketResponse`
Actualizados con campos nuevos.

---

## Migración BD

**Archivo**: `backend/migrations/2026_06_23_001_arco_admin_form_fields.sql`

Ejecutada en Neon QA (`ep-fragrant-wildflower-apeqosx9-pooler`) contra `neondb`.

Columnas agregadas:
- `telefono` VARCHAR(50)
- `fecha_nacimiento` DATE
- `pais` VARCHAR(100)
- `representante_nombre` VARCHAR(255)
- `representante_rut` VARCHAR(20)

---

## Commits

| Commit | Descripción |
|--------|-------------|
| `09aebce` | Sprint 1 QW1-QW10 + docs consultoría + E2E |
| `73e39d5` | Migración ejecutada + renombrada con timestamp |
| `e0f98f2` | UX: homologar tamaño Drawer + secciones 2-col + tooltip + asterisco |

---

## Tests

### Backend (Neon QA — PostgreSQL)
- `test_arco_tickets.py`: **18/18 PASSED** ✅
- `test_reglas_asignacion.py`: **9/9 PASSED** ✅

### E2E
- `e2e/17-form-admin-arco.spec.ts`: 12 tests (10 admin QW1-QW10 + 2 público QW2/QW6)

---

## Decisiones Técnicas

1. **Tooltip ⓘ en vez de helper text inline**: Ahorra ~80px verticales, mobile-friendly, discoverable on hover/tap.
2. **Representante legal colapsable**: 80% de solicitudes no tienen representante → oculto por default.
3. **Debounce 800ms para duplicados**: Balance entre responsividad y no sobrecargar la API.
4. **Debounce 300ms para RAT search**: Búsqueda inmediata pero sin floods de requests.

---

## Notas

- Error pre-existente lint: "Calling setState synchronously within an effect" (React 19) en `asesor/page.tsx` y `tkt_solicitud_derecho/page.tsx` — no es regresión de Sprint 1.
- ARCO-QW3 (Firma digital) fue **postergado indefinidamente** por decisión del usuario — requiere integración con audit chain/eIPD/identidad digital (Clave Única).
