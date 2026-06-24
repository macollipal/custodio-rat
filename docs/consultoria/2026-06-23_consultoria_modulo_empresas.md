# Análisis del Módulo Clientes (Empresas) — Custodio RAT

**Fecha**: 2026-06-23
**Consultores**: DPO + PM Senior + UX/UI Lead + Auditor
**Versión**: 1.0

---

## 1. Problemas Detectados

### 1.1 Modelo de datos insuficiente para cumplimiento

| # | Problema | Criticidad | Visto por |
|---|----------|------------|-----------|
| M1.1 | Solo 9 campos editables (nombre, RUT, rubro, dirección, contacto_dpo, email_dpo, descripción, canal_ejercicio_derechos). Falta: teléfono, sitio web, representante legal, RUT representante, tipo persona, tamaño empresa, país, fecha inicio actividades | ALTA | DPO, PM |
| M1.2 | No hay campos para Ley 21.719: consentimiento del DPO, fecha inicio como responsable, datos encargado interno, identificadores APDP | ALTA | DPO, Auditor |
| M1.3 | RUT inmutable post-creación — si se equivoca debe borrar y rehacer | MEDIA | UX, PM |
| M1.4 | No hay campos para sectores regulados (salud, financiero, educación — regulaciones especiales Art. 17) | MEDIA | DPO |
| M1.5 | `canal_ejercicio_derechos` es texto libre — imposible validar formato | MEDIA | DPO |
| M1.6 | No se distingue persona natural vs jurídica | BAJA | DPO |

### 1.2 Vista actual es un CRUD plano

| # | Problema | Criticidad | Visto por |
|---|----------|------------|-----------|
| M2.1 | Solo 2 vistas (list y create). No hay tabs ni ficha de detalle | ALTA | UX |
| M2.2 | No existe ficha navegable con drill-down a RATs, brechas, ARCO, encargados | ALTA | UX, PM |
| M2.3 | Tarjetas no muestran riesgo ni acciones pendientes — solo total_rats | ALTA | DPO, UX |
| M2.4 | Falta búsqueda y filtros por nombre, RUT, rubro, estado, riesgo | MEDIA | UX |
| M2.5 | Falta ordenamiento (alfabético, completitud, riesgo) | BAJA | UX |
| M2.6 | Falta paginación visible | BAJA | UX |

### 1.3 Cero automatización para generar RAT/EIPD/Brechas/ARCO

| # | Problema | Criticidad | Visto por |
|---|----------|------------|-----------|
| M3.1 | Crear empresa no genera nada — time-to-value de 2-4 horas | CRÍTICA | PM, UX |
| M3.2 | No hay plantillas de RAT por rubro — debe crear todo desde cero | CRÍTICA | PM, DPO |
| M3.3 | No hay asistente para nombrar DPO, encargado interno, representantes | ALTA | UX |
| M3.4 | Al crear empresa no se genera automáticamente Política de Transparencia (Art. 14 ter) ni Procedimiento de Brechas | ALTA | DPO |

### 1.4 Auditoría limitada por empresa

| # | Problema | Criticidad | Visto por |
|---|----------|------------|-----------|
| M4.1 | No existe vista de auditoría per-empresa — hay que ir a /configuracion | ALTA | Auditor, DPO |
| M4.2 | Auditoría muestra últimos 20 registros globales sin drill-down | ALTA | Auditor |
| M4.3 | No hay exportación de evidencia para fiscalización (PDF firmado, hash) | CRÍTICA | Auditor |
| M4.4 | Hash chain SHA-256 existe pero no hay UI para verificar integridad | MEDIA | Auditor |
| M4.5 | Faltan firmas digitales o sellos de tiempo en eventos clave | MEDIA | Auditor |

### 1.5 Sin cálculo de riesgo explícito

| # | Problema | Criticidad | Visto por |
|---|----------|------------|-----------|
| M5.1 | No hay score de riesgo por empresa — se calcula por RAT pero no se agrega | CRÍTICA | DPO, PM |
| M5.2 | No hay alertas automáticas cuando hay RATs vencidos, brechas sin cerrar, ARCO vencido | ALTA | DPO |
| M5.3 | No hay semáforo de cumplimiento (verde/amarillo/rojo) para la empresa | ALTA | DPO, UX |
| M5.4 | OnboardingChecklist solo aparece en dashboard, no en ficha de empresa | MEDIA | UX |

### 1.6 Sin alertas ni notificaciones

| # | Problema | Criticidad | Visto por |
|---|----------|------------|-----------|
| M6.1 | No hay alertas in-app cuando empresa tiene problemas | ALTA | UX |
| M6.2 | No hay notificaciones por email al DPO para alertas críticas | ALTA | DPO |
| M6.3 | No hay digest semanal/mensual del estado de cumplimiento | MEDIA | PM |

### 1.7 Permisos y multi-tenancy

| # | Problema | Criticidad | Visto por |
|---|----------|------------|-----------|
| M7.1 | No hay distinción clara de qué puede hacer cada rol en la ficha | MEDIA | Auditor |
| M7.2 | Hard delete no tiene rastro de quién autorizó la acción en log separado | ALTA | Auditor |
| M7.3 | No hay roles granulares por empresa (DPO solo ver, editor puede crear, etc.) | BAJA | PM |

### 1.8 Diferenciación

| # | Problema | Criticidad | Visto por |
|---|----------|------------|-----------|
| M8.1 | Cualquier competidor tiene dashboard de cumplimiento normativo — Custodio no | ALTA | PM |
| M8.2 | No hay generación automática de reportes APDP para fiscalización | CRÍTICA | DPO |
| M8.3 | No hay marketplace de plantillas (RAT, política, cláusulas) por rubro | MEDIA | PM |

---

## 2. Oportunidades de Mejora

### OP1. Ficha de empresa 360° (drill-down)
Una sola pantalla muestra TODO sobre una empresa: identidad, riesgo, alertas, RATs, brechas, ARCO, encargados, EIPD, consentimientos, política, auditoría, equipo.

### OP2. Generación automática asistida
Al crear empresa con rubro=sector_salud, ofrecer generar 5 RATs típicos, política de transparencia modelo, procedimiento de brechas modelo.

### OP3. Score de cumplimiento APDP
Score 0-100 calculado en base a 8 dimensiones (completitud RAT 20%, EIPD 15%, RATs vigentes 15%, Encargados 10%, Política 10%, Brechas 10%, SLA ARCO 10%, Procedimientos 10%).

### OP4. Alertas inteligentes con priorización
Motor de alertas: Crítica (ARCO vencido, brecha >72h sin reportar), Alta (SLA <2d, RAT por vencer 90d), Media (brecha abierta, encargado sin contrato).

### OP5. Bandeja de entrada del DPO (`/bandeja`)
Página unificada: tickets ARCO sin asignar, subsanaciones pendientes, prorogas por vencer, brechas sin atender, alertas críticas.

### OP6. Reporte APDP pre-armado (PDF firmado)
Botón "Generar Reporte para APDP" con: carátula, score, alertas, RATs, brechas, ARCOs, EIPDs, política, hash chain, firma digital.

### OP7. Marketplace de plantillas
Por rubro: RATs típicos, cláusulas de encargado, política modelo, textos de respuesta ARCO, procedimientos de breach. Versionadas y editables.

### OP8. Comparativa sectorial anónima
"Tu empresa está en el percentil 75 de cumplimiento vs empresas del rubro X." Anonimizado y agregado.

### OP9. Wizard de incorporación
Reemplazar OnboardingChecklist por wizard de 6 pasos al crear empresa: identidad, DPO, representante, canales, selección de plantillas, equipo.

### OP10. Vista comparativa temporal
"Esta empresa en marzo 2025 tenía 2 RATs y 65% completitud. Hoy tiene 8 RATs y 82%."

---

## 3. Diseño Propuesto — Ficha de Cliente

### Estructura de navegación (3 niveles)

```
/companies                         → Lista (con score y filtros)
  └── /companies/[id]              → Ficha 360°
        ├── Resumen                → Dashboard ejecutivo
        ├── Identidad              → Datos básicos + editar
        ├── Cumplimiento           → Score, alertas, brechas
        ├── Datos tratados         → RATs, EIPDs, consentimientos
        ├── Personas               → Equipo, accesos
        ├── Solicitudes ARCO       → Tickets (drill a /tkt_solicitud_derecho?ticket=ID)
        ├── Encargados             → Contratos Art. 14 quater
        ├── Transparencia          → Política Art. 14 ter
        ├── Auditoría              → Log filtrable + verificación hash
        └── Configuración         → Eliminar, desactivar, exportar
```

### Layout de la ficha (`/companies/[id]`)

```
┌──────────────────────────────────────────────────────────────────┐
│ [Logo] Razón Social                                 [⋮ Acciones]│
│ RUT: 12.345.678-9 · Rubro: Salud · [ACTIVA]                   │
│ 🟢 Score: 82/100 (Excelente)  ·  🔔 3 alertas críticas        │
├──────────────────────────────────────────────────────────────────┤
│ [Resumen] [Identidad] [Cumplimiento] [Datos tratados] [Personas]│
│ [ARCO] [Encargados] [Transparencia] [Auditoría] [Configuración]│
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  TAB "RESUMEN":                                                 │
│  RADAR DE CUMPLIMIENTO (8 dimensiones)                        │
│   Completitud RAT: ████████░░ 80%                                │
│   EIPD al día:   ██████░░░░ 60%                                 │
│   RATs vigentes: ██████████ 100%                                 │
│   Encargados:    ████████░░ 80%                                 │
│   Política:      ██████████ 100%                                │
│   Brechas:       ████████░░ 80%                                │
│   SLA ARCO:      ███████░░░ 70%                                │
│   Procedimientos: ████████░░ 80%                                │
│                                                                  │
│  KPIs: RATs:8 · Brechas(12m):2 · ARCO(12m):12 · SLA:92%       │
│  ALERTAS: 🔴 ARCO#47 vencido 2d · 🟠 RAT#3 vence 15d · 🟡1     │
│  ACTIVIDAD: Hoy 14:30 María creó RAT · Ayer 09:15 Juan respondió│
└──────────────────────────────────────────────────────────────────┘
```

---

## 4. Dashboard Recomendado (DPO al abrir empresa)

```
┌──────────────────────────────────────────────────────────────────┐
│ 🏢 Clínica San José   Score: 🟢 82/100    🔔 3 alertas críticas  │
├──────────────────────────────────────────────────────────────────┤
│  BANDEJA DEL DPO (atención requerida hoy)                        │
│  🔴 ARCO#47 (Cancelación) — Vencido hace 2 días  [RESPONDER YA]│
│  🟠 RAT "Recetas" vence revisión en 12 días        [REVISAR]   │
│  🟡 Brecha#3 — Datos email filtrados (72h)         [DOCUMENTAR] │
│  🟡 Subsanación ARCO#42 — Esperando titular        [RECORDAR]   │
│  🟢 EIPD "Telemedicina" pendiente                 [INICIAR]     │
└──────────────────────────────────────────────────────────────────┘
```

---

## 5. Automatizaciones Recomendadas

### A1. Generación automática al crear empresa
Al seleccionar rubro, ofrecer: plantillas RAT × N, política transparencia modelo, procedimiento brechas modelo, 3 cláusulas encargado comunes, email bienvenida DPO.

### A2. Cálculo automático de score (cron diario)
Job recalcula score por empresa, guarda histórico, genera alertas si baja >5 puntos en 30 días.

### A3. Asignación automática ARCO
Ya existe TktReglaAsignacion. Mejorar: si no hay regla, asignar al DPO por defecto. Notificar por email al asignado.

### A4. Recordatorio automático ARCO
- T-2 días: email al responsable
- T+1 día vencido: email + toast al DPO
- T+5 días vencido: escalación al superadmin

### A5. Renovación automática de alertas
- RAT cumple 90 días: alerta preventiva
- RAT cumple 180 días: alerta crítica + bloqueo de edición
- Contrato encargado vence en 30 días: alerta + email

---

## 6. Indicadores de Riesgo

### Indicadores principales (8 dimensiones, score 0-100)

| # | Indicador | Ponderación |
|---|-----------|-------------|
| 1 | Completitud RAT | 20% |
| 2 | EIPD al día | 15% |
| 3 | RATs vigentes | 15% |
| 4 | Encargados con contrato | 10% |
| 5 | Política vigente | 10% |
| 6 | Brechas cerradas en 72h | 10% |
| 7 | SLA ARCO cumplido | 10% |
| 8 | Procedimientos documentados | 10% |

### Indicadores secundarios (alertas)

| Alerta | Trigger | Severidad |
|--------|---------|-----------|
| RAT con datos sensibles sin EIPD | existe RAT con datos_sensibles y estado_eipd != completada | 🔴 Crítica |
| Brecha sin reportar >72h | existe Brecha con fecha_deteccion < now-72h | 🔴 Crítica |
| ARCO vencido | existe Tkt con fecha_vencimiento < now y estado no terminal | 🔴 Crítica |
| Encargado sin contrato | existe RAT con nombre_encargado y !tiene_contrato | 🟠 Alta |
| Transferencia sin garantías | existe RAT con transferencia_int y !garantias | 🟠 Alta |
| SLA ARCO < 2 días | existe Tkt con dias_restantes <= 2 | 🟠 Alta |
| RAT por vencer (90 días) | existe RAT con last_review > 90d | 🟡 Media |

---

## 7. Quick Wins (menos de 1 semana)

| # | Mejora | Esfuerzo | Impacto Legal | Impacto Comercial |
|---|--------|----------|--------------|-------------------|
| QW1 | Vista auditoría per-empresa | 2-3 días | ALTO | MEDIO |
| QW2 | Exportar Reporte APDP PDF | 3-4 días | CRÍTICO | MEDIO |
| QW3 | Score cumplimiento v1 | 3-4 días | MEDIO | ALTO |
| QW4 | Export CSV/Excel/PDF tickets ARCO | 2-3 días | ALTO | MEDIO |
| QW5 | SLA alert email T-2 días | 2 días | CRÍTICO | BAJO |
| QW6 | Ficha empresa con tabs | 3-5 días | MEDIO | ALTO |
| QW7 | Banner alertas en lista empresas | 1 día | MEDIO | ALTO |
| QW8 | Recordatorio ARCO T-2 días | 1-2 días | ALTO | BAJO |
| QW9 | Editar RUT post-creación | 0.5 día | BAJO | MEDIO |
| QW10 | Plantillas RAT por rubro seed | 5 días | MEDIO | ALTO |

---

## 8. Mejoras de Mediano Plazo

| # | Mejora | Esfuerzo | Descripción |
|---|--------|----------|-------------|
| MM1 | Generación automática inicial | 2 sprints | Wizard 6 pasos genera RATs, política, brechas |
| MM2 | Radar cumplimiento 360° | 1.5 sprints | Spider chart 8 dimensiones con drill-down |
| MM3 | Bandeja DPO | 2 sprints | Inbox unificado cross-módulo |
| MM4 | Marketplace plantillas | 2-3 sprints | Repositorio por rubro versionado |
| MM5 | Sugerencia respuesta ARCO con IA | 1.5 sprints | RAG + contexto ticket |
| MM6 | Reporte APDP completo PDF | 2 sprints | Carátula + 12 secciones + hash + firma |
| MM7 | Multi-idioma | 1.5 sprints | es-CL, en, pt-BR |
| MM8 | Roles granulares por empresa | 1.5 sprints | DPO, Editor, Visualizador, Consultor |
| MM9 | Búsqueda global cross-módulo | 1 sprint | Busca en RATs, brechas, ARCO, usuarios |
| MM10 | Comparativa sectorial | 2 sprints | Benchmark anonymizado |

---

## 9. Mejoras Estratégicas para Diferenciar Custodio

| # | Mejora | Esfuerzo | Diferenciador |
|---|--------|----------|--------------|
| ME1 | Asesor IA Legal Ley 21.719 | 3 sprints | Nadie tiene esto en Chile |
| ME2 | Generador paquete evidencia APDP | 4 sprints | Producto estrella único |
| ME3 | Conector SERNAC/APDP | 6 sprints | Integración regulatoria |
| ME4 | Marketplace cláusulas contractuales | 4 sprints | Contenido curado legal |
| ME5 | Simulador de fiscalización | 5 sprints | "Modo simulacro" APDP |
| ME6 | Integración notarías digitales | 3 sprints | Firmas certificadas |
| ME7 | Benchmark público anonymizado | 2 sprints | Marketing + diferenciador |
| ME8 | Certificación Custodio (oro/plata/bronce) | 3 sprints | Insignia compartible |
| ME9 | Integración RR.HH. y CRM | 4 sprints | Acelerar poblar RATs |
| ME10 | API pública documentada | 3 sprints | Webhooks + sandbox |

---

## 10. Resumen Ejecutivo

**Custodio tiene base sólida** (CRUD funcional, audit chain, score por RAT) pero el **módulo Empresas está subdesarrollado** — es un CRUD plano en lugar del centro de cumplimiento normativo que debería ser.

**3 acciones inmediatas** (sprint actual):
1. QW2: Reporte APDP PDF — el "wow" legal que justifica el precio
2. QW3: Score de cumplimiento — diferenciador visual vs competencia
3. QW5 + QW8: SLA alerts + recordatorios ARCO — bug crítico legal

**3 apuestas estratégicas** (6-12 meses):
1. Asesor IA especializado Ley 21.719
2. Paquete de Evidencia para Fiscalización APDP
3. Marketplace de plantillas por rubro

**Métrica clave**: pasar de "5 campos editables" a "centro de cumplimiento 360° con 50+ señales automatizadas".
