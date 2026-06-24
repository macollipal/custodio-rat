# Análisis del Módulo ARCO (Tickets) — Custodio RAT

**Fecha**: 2026-06-23
**Consultores**: DPO + PM Senior + UX/UI Lead + Auditor
**Versión**: 1.0

---

## 1. Estado Actual (Resumen Ejecutivo)

### Fortalezas
| Fortaleza | Detalle |
|-----------|---------|
| ✅ 8 estados bien modelados | abierto, en_proceso, pendiente, subsanacion, prorroga, bloqueado, resuelto, rechazado |
| ✅ 6 tipos ARCO cubiertos | Acceso, Rectificación, Cancelación, Oposición, Bloqueo, Portabilidad |
| ✅ SLA 10 días hábiles con feriados | Chile: fijos + Semana Santa 2025-2040 inlined |
| ✅ Tracking token público | UUID v4, link `/seguimiento/{token}` |
| ✅ Acuse de recibo con email | `notificar_acuse_solicitud()` con tracking link |
| ✅ Subsanación + Prórroga implementadas | QW3 y QW4 completados |
| ✅ Plantillas de respuesta | TktPlantilla CRUD con 5 seed |
| ✅ Ver Flujo con diagramas | Mermaid con sub-pasos contextuales (Opción B implementada) |
| ✅ Auto-asignación por reglas | Specificity: company=4, tipo=2, prioridad=1 |
| ✅ Audit chain con hash SHA-256 | Inmutable en todas las operaciones |

### Brechas críticas

| # | Brecha | Criticidad |
|---|--------|------------|
| ❌ | No hay exportación masiva CSV/Excel/PDF | ALTA |
| ❌ | No hay SLA alert automático T-2 días | CRÍTICA |
| ❌ | No hay firma digital ni timestamp en respuesta | CRÍTICA |
| ❌ | No hay bandeja unificada del DPO | ALTA |
| ❌ | No hay respuesta asistida con IA | MEDIA |
| ❌ | No hay recordatorio al titular | MEDIA |
| ❌ | Sin dashboard "qué derechos se ejercen más" | BAJA |
| ❌ | Ver Flujo sin tiempos reales | MEDIA |
| ❌ | Portal del titular no muestra respuesta descargable | ALTA |
| ❌ | Sin integración con email entrante | MEDIA |

---

## 2. Problemas Detectados — Módulo ARCO

### 2.1 Exportación y Reportes

| # | Problema | Criticidad | Visto por |
|---|----------|------------|-----------|
| A1.1 | No hay exportación CSV/Excel/PDF del listado de tickets — solo JSON individual para portabilidad | ALTA | DPO, PM |
| A1.2 | No hay dashboard consolidado de métricas ARCO por empresa | MEDIA | PM |
| A1.3 | No hay export de auditoría ARCO para fiscalización | ALTA | Auditor |
| A1.4 | El dashboard solo muestra 10 KPIs genéricos — falta drill-down por tipo, responsable, plazo | MEDIA | UX |

### 2.2 Alertas y Notificaciones

| # | Problema | Criticidad | Visto por |
|---|----------|------------|-----------|
| A2.1 | No hay SLA alert cuando quedan ≤2 días — ticket se vence sin que nadie lo note | CRÍTICA | DPO |
| A2.2 | No hay notificación al DPO cuando un ticket se vence | CRÍTICA | DPO |
| A2.3 | No hay recordatorio al titular cuando no responde una subsanación | MEDIA | DPO |
| A2.4 | No hay digest diario/semanal de ARCO para el DPO | BAJA | PM |
| A2.5 | El email de acuse tiene link hardcodeado a `custodio.cl` — debería ser configurable | BAJA | DPO |

### 2.3 Respuesta y Cierre

| # | Problema | Criticidad | Visto por |
|---|----------|------------|-----------|
| A3.1 | No hay firma digital ni timestamp en respuesta_texto — prueba legal débil ante impugnación | CRÍTICA | Auditor |
| A3.2 | No hay respuesta asistida con IA — DPO escribe manualmente | MEDIA | PM |
| A3.3 | Las plantillas de respuesta son texto fijo sin placeholders dinámicos | MEDIA | DPO |
| A3.4 | No hay opción de "respuesta parcial" para casos que requieren más tiempo | BAJA | UX |
| A3.5 | No hay "cerrar ticket sin respuesta" para casos donde el titular no se identificó | BAJA | DPO |

### 2.4 Workflow y Estados

| # | Problema | Criticidad | Visto por |
|---|----------|------------|-----------|
| A4.1 | Ver Flujo solo muestra diagrama legal — no los tiempos reales por estado | MEDIA | UX, DPO |
| A4.2 | No hay forma de "pausar" un ticket (diferente de subsanacion/prorroga) | BAJA | UX |
| A4.3 | No hay opción de "combinar tickets" del mismo titular | BAJA | PM |
| A4.4 | No hay etiquetas/tags personalizables para categorizar tickets | BAJA | PM |
| A4.5 | El flujo de portabilidad tiene 3 formatos (JSON/CSV/Excel) pero el form solo ofrece JSON | MEDIA | DPO |

### 2.5 Asignación y Responsables

| # | Problema | Criticidad | Visto por |
|---|----------|------------|-----------|
| A5.1 | No se puede asignar manualmente al crear ticket (solo auto-reglas) | MEDIA | UX |
| A5.2 | No hay "delegar ticket" a otro usuario | MEDIA | UX |
| A5.3 | No hay notificaciones al responsable cuando se le asigna un ticket | MEDIA | UX |
| A5.4 | Si no hay regla, el ticket queda sin responsable (NULL) | ALTA | DPO |

### 2.6 Datos y Calidad

| # | Problema | Criticidad | Visto por |
|---|----------|------------|-----------|
| A6.1 | No hay forma de editar RUT del titular post-creación | BAJA | UX |
| A6.2 | No hay forma de cambiar el email del titular | BAJA | UX |
| A6.3 | No hay tracking de "quién vio el ticket por última vez" | BAJA | UX |
| A6.4 | No hay forma de cambiar el tipo de ARCO post-creación | BAJA | UX |
| A6.5 | La descripción tiene límite de 2000 chars pero no avisa al usuario | BAJA | UX |

### 2.7 Seguimiento (Portal del Titular)

| # | Problema | Criticidad | Visto por |
|---|----------|------------|-----------|
| A7.1 | Portal `/seguimiento` no muestra la respuesta descargable cuando está resuelto | ALTA | UX |
| A7.2 | No hay forma de que el titular Responda directamente desde el portal | BAJA | UX |
| A7.3 | No hay widget de chat/ayuda en el portal del titular | BAJA | PM |
| A7.4 | El portal no muestra "qué tipo de datos" fueron los solicitados (acces scope) | MEDIA | DPO |

### 2.8 Integración

| # | Problema | Criticidad | Visto por |
|---|----------|------------|-----------|
| A8.1 | No hay integración con email entrante (parsear emails y crear tickets automáticamente) | MEDIA | PM |
| A8.2 | No hay API REST completa para que terceros integren (webhooks ARCO) | BAJA | PM |
| A8.3 | No hay integración con sistemas del cliente (CRM, RR.HH.) | BAJA | PM |

---

## 3. Oportunidades de Mejora — Módulo ARCO

### OP1. Exportación masiva inteligente
CSV/Excel/PDF con filtros avanzados: por tipo, estado, plazo, responsable, empresa, período. Incluir métricas de SLA en el export.

### OP2. SLA Alert Engine
Motor de alertas con thresholds configurables: T-5 días (info), T-2 días (warning), T+0 (critical), T+3 (escalation to superadmin).

### OP3. Bandeja de entrada del DPO
Inbox unificado con todos los módulos: ARCO nuevos, ARCO por vencer, Subsanaciones pendientes, Prórrogas, Brechas relacionadas, Alertas.

### OP4. Respuesta asistida con IA
Integración con RAG existente. El DPO cliquea "Sugerir respuesta" → la IA genera borrador con citas legales → DPO revisa y envía.

### OP5. Firma digital + timestamp
Hash SHA-256(ticket_id + respuesta_texto + timestamp) guardado en cada respuesta. Incluido en PDF exportado.

### OP6. Portal del titular 2.0
Mejora del `/seguimiento`: muestra respuesta formal descargable en PDF, historial completo, CTA para reopen si no está conforme.

### OP7. Wizard de respuesta contextual
Por cada tipo ARCO, el DPO ve los campos específicos que debe completar antes de resolver (ej. para portabilidad: formato, alcance, datos incluidos).

### OP8. Analytics ARCO
Dashboard con: tendencia de solicitudes por mes, distribución por tipo, SLA compliance por mes, comparativa entre empresas (superadmin), top titulares (con más solicitudes).

### OP9. Integración email entrante
Webhook que parsea emails entrantes a `arco@{dominio}` y auto-crea tickets con clasificación por IA.

### OP10. Workflow multi-paso
Permitir que el DPO defina workflows custom por tipo ARCO (ej. para portabilidad: Recepcion → Identificacion → Extraccion → Validacion → Generacion → Envio → Cierre).

---

## 4. Diseño Propuesto — Bandeja del DPO

```
┌────────────────────────────────────────────────────────────────────┐
│  🔴 CRÍTICAS (requieren acción inmediata)                          │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ ARCO #47 — Cancelación — juan@mail.com                     │  │
│  │ Vencido hace 2 días · Abierta desde 10 Jun                │  │
│  │ [RESPONDER]  [ASIGNAR]  [VER FLUJO]                       │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                    │
│  🟠 ATENCIÓN PRONTA (vencen esta semana)                          │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ ARCO #51 — Acceso — maria@mail.com                          │  │
│  │ Vence en 1 día · Creada 12 Jun                             │  │
│  │ [RESPONDER]  [PRORROGAR]                                   │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                    │
│  🟡 PENDIENTES DE TERCEROS (subsanación, respuestas)            │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ ARCO #42 — Rectificación — pedro@mail.com                  │  │
│  │ Subsanación pedida hace 5 días — Sin respuesta del titular │  │
│  │ [RECORDAR]  [CERRAR SIN RESPUESTA]                         │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                    │
│  🟢 MIS TICKETS ASIGNADOS                                        │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ ARCO #44 — Bloqueo — ana@mail.com                          │  │
│  │ En proceso · Asignado a ti · Creada 8 Jun                  │  │
│  │ [ABRIR]                                                    │  │
│  └────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────┘
```

---

## 5. Automatizaciones Recomendadas

### A1. SLA Alert Engine (T-5, T-2, T+0, T+3)
- T-5 días: email info al responsable
- T-2 días: email warning + toast in-app
- T+0 (vencido): email crítico al DPO
- T+3: email escalation al superadmin

### A2. Recordatorio automático al titular
Cuando un ticket está en subsanación por >7 días sin respuesta del titular → email recordatorio automático.

### A3. Sugerencia de respuesta IA
Prompt: tipo de derecho + estado actual + descripción + historial + Ley 21.719 relevante. Devuelve borrador con citas a artículos.

### A4. Auto-asignación mejorada
Si no hay regla: asignar al DPO de la empresa (company.email_dpo). Si el DPO no existe: asignar al superadmin más antiguo.

### A5. Detección de anomalías
- Múltiples ARCOs del mismo titular en 30 días → agrupar
- Email bounced → marcar ticket para verificación
- ARCO de tipo sensible (biométrico, salud) → flag automático de prioridad alta

---

## 6. Indicadores de Riesgo — ARCO

### Indicadores principales (KPI Dashboard)

| KPI | Cálculo | Target |
|-----|---------|--------|
| SLA Cumplimiento | resueltos_en_tiempo / total_resueltos × 100 | >90% |
| Tiempo promedio de respuesta | AVG(respuesta_fecha - fecha_recepcion) en horas | <48h |
| Tasa de subsanación | tickets_subsanados / total × 100 | <20% |
| Tasa de rechazo | rechazados / total × 100 | <10% |
| Tickets vencidos | count(tickets con fecha_vencimiento < now and estado not terminal) | 0 |
| Tasa de resolución en primera respuesta | resueltos_sin_subsanacion / total_resueltos × 100 | >70% |

### Alertas ARCO

| Alerta | Trigger | Severidad |
|--------|---------|-----------|
| ARCO vencido | existe Tkt con fecha_vencimiento < now y estado no terminal | 🔴 Crítica |
| SLA < 2 días | existe Tkt con dias_restantes <= 2 | 🟠 Alta |
| Subsanación sin respuesta >7d | existe Tkt con estado=subsanacion y subsanacion_fecha_pedido < now-7d | 🟠 Alta |
| Prórroga aplicada | existe Tkt con estado=prorroga | 🟡 Media |
| Representante sin acreditar | existe Tkt con representante_nombre y !adjunto_poder | 🟡 Media |
| Mismo titular >3 tickets/mes | GROUP BY titular_email HAVING COUNT > 3 | 🟡 Media |

---

## 7. Quick Wins — ARCO (menos de 1 semana)

| # | Mejora | Esfuerzo | Impacto Legal | Impacto Comercial | Complejidad |
|---|--------|----------|--------------|-------------------|-------------|
| QW1 | Exportación CSV/Excel/PDF | 3 días | ALTO | MEDIO | BAJA |
| QW2 | SLA alert email T-2 días | 2 días | CRÍTICO | BAJO | BAJA |
| QW3 | Firma digital + timestamp | 1 día | CRÍTICO | BAJO | BAJA |
| QW4 | Dashboard "derechos más ejercidos" | 1.5 días | BAJO | MEDIO | BAJA |
| QW5 | Bandeja de entrada del DPO | 3 días | ALTO | ALTO | MEDIA |
| QW6 | Recordatorio automático al titular | 2 días | ALTO | MEDIO | BAJA |
| QW7 | Plantillas con placeholders dinámicos | 3 días | MEDIO | ALTO | MEDIA |
| QW8 | Ver Flujo con tiempos reales | 2 días | MEDIO | BAJO | BAJA |
| QW9 | Portal del titular con respuesta descargable | 2 días | ALTO | MEDIO | BAJA |
| QW10 | Editar RUT titular/representante | 0.5 día | BAJO | MEDIO | BAJA |

---

## 8. Mejoras de Mediano Plazo — ARCO (1-3 sprints)

| # | Mejora | Esfuerzo | Descripción |
|---|--------|----------|-------------|
| MM1 | Sugerencia respuesta con IA (RAG) | 1.5 sprints | Botón "Sugerir" → borrador con citas legales |
| MM2 | Integración email entrante (parser) | 2 sprints | Webhook parsea emails y crea tickets automáticamente |
| MM3 | Dashboard tiempo promedio de respuesta | 1.5 sprints | Gráfico + comparativa con SLA objetivo |
| MM4 | Asignación inteligente con SLA-awareness | 1.5 sprints | Considera carga de trabajo + historial SLA |
| MM5 | Workflow multi-paso custom por tipo | 2 sprints | DPO define pasos por tipo ARCO |
| MM6 | Analytics ARCO avanzado | 1.5 sprints | Tendencia mensual, comparativa empresas |
| MM7 | Portal del titular 2.0 | 2 sprints | Chat, respuesta inline, reopen |
| MM8 | Export de auditoría ARCO para fiscalización | 1 sprint | PDF firmado + hash chain |
| MM9 | Widget IA en portal del titular | 2 sprints | Chatbot que responde dudas sobre estado |
| MM10 | API webhooks ARCO para terceros | 2 sprints | Notificaciones push a sistemas externos |

---

## 9. Mejoras Estratégicas — ARCO

| # | Mejora | Esfuerzo | Diferenciador |
|---|--------|----------|--------------|
| ME1 | Chatbot IA ARCO para titulares | 3 sprints | Guía al titular paso a paso — único en Chile |
| ME2 | Auto-respuesta para ARCO simples | 4 sprints | IA genera respuesta + DPO approves en 1-click |
| ME3 | Integración Clave Única | 3 sprints | Verificación de identidad digital |
| ME4 | Connector APDP/SERNAC | 5 sprints | Reporte regulatorio automático |
| ME5 | Asistente DPO con RAG especializado | 2 sprints | Responde dudas legales con citas a Ley 21.719 |

---

## 10. Resumen Ejecutivo

**El módulo ARCO tiene una base sólida** (workflow de 8 estados, SLA con feriados, auto-asignación, Ver Flujo contextual) pero le faltan features que son **expectativa estándar** de cualquier sistema de gestión de tickets profesional.

**3 acciones inmediatas** (sprint actual):
1. ARCO-QW2: SLA alert T-2 días — CRÍTICO (tickets se vencen sin que nadie lo note)
2. ARCO-QW3: Firma digital + timestamp — CRÍTICO (prueba legal débil ante impugnación)
3. ARCO-QW1: Exportación CSV/Excel/PDF — ALTO (DPO necesita reportes para fiscalización)

**3 apuestas estratégicas**:
1. Sugerencia respuesta con IA (MM1) — reduce tiempo del DPO en 70%
2. Bandeja de entrada unificada (QW5) — el DPO centraliza TODO su trabajo
3. Chatbot IA para titulares (ME1) — diferenciador único en Chile
