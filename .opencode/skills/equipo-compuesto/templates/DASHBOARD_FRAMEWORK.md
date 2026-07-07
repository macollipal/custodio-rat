# Template: Dashboard Framework — Custodio RAT

Framework reutilizable para diseñar dashboards de cualquier módulo de Custodio RAT.

---

## Anatomía de un Dashboard DPO

```
┌────────────────────────────────────────────────────────────────┐
│ HEADER                                                        │
│ [Módulo]  ·  [Empresa: Nombre]  ·  [Período: Últimos 30 días]  │
├────────────────────────────────────────────────────────────────┤
│ SCORE/SEMÁFORO                                                │
│ [████████░░] 78%  ·  Riesgo: 🟡 MEDIO  ·  [Ver detalle →]    │
├────────────────────────────────────────────────────────────────┤
│ KPI CARDS (4 max)                                             │
│ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│ │ Total    │ │ Vencidos │ │ Por     │ │ En      │          │
│ │ 24       │ │ 3 ⚠️     │ │ vencer  │ │ proceso │          │
│ │ RATs     │ │          │ │ 5       │ │ 12      │          │
│ └──────────┘ └──────────┘ └──────────┘ └──────────┘          │
├────────────────────────────────────────────────────────────────┤
│ MAIN CONTENT (2 columnas)                                     │
│ ┌─────────────────────────┐  ┌─────────────────────────────┐  │
│ │ CHART / TABLA           │  │ ALERTAS ACTIVAS             │  │
│ │                         │  │ 🔴 Alerta 1                 │  │
│ │                         │  │ 🟡 Alerta 2                 │  │
│ │                         │  │                             │  │
│ └─────────────────────────┘  └─────────────────────────────┘  │
├────────────────────────────────────────────────────────────────┤
│ DEADLINES / PRÓXIMOS EVENTOS                                  │
│ 📅 RAT "Nómina" vence en 15 días                              │
│ 📅 SLA ARCO #284 vence en 2 días ⚠️                          │
├────────────────────────────────────────────────────────────────┤
│ QUICK ACTIONS                                                  │
│ [Acción 1]  [Acción 2]  [Acción 3]  [Ver todo →]            │
└────────────────────────────────────────────────────────────────┘
```

---

## Widgets Reutilizables

### W1: KPI Card

**Uso:** Métricas principales en número grande.

**Estructura:**
```
┌────────────────┐
│ [ICONO] [Label]│
│   [NÚMERO]     │
│   [Contexto]   │
│   [Badge]      │  (opcional: trend, vs. mes pasado)
└────────────────┘
```

**Variantes por color:**
- 🟢 Verde: dentro de umbral OK
- 🟡 Amarillo: cerca del umbral (warning)
- 🔴 Rojo: sobre umbral o vencido
- 🔵 Azul: neutral/informativo

**Estados:**
- Loading: skeleton pulsante
- Empty: "Sin datos" con icono
- Error: "Error al cargar" con retry

---

### W2: Score Bar

**Uso:** Score general de compliance (0-100%).

**Estructura:**
```
[████████░░] 78%  ·  Riesgo: 🟡 MEDIO
```

**Colores por score:**
- 90-100%: Verde (score excellent)
- 70-89%: Amarillo (score aceptable, mejorar)
- 40-69%: Naranja (score bajo, atención)
- 0-39%: Rojo (score crítico, acción inmediata)

---

### W3: Semáforo de Riesgo

**Uso:** Indicador visual de riesgo general.

```
🟢 BAJO    🟡 MEDIO    🟠 ALTO    🔴 CRÍTICO
```

**Definición de niveles:**
- **BAJO**: Todos los KPIs dentro de umbral verde
- **MEDIO**: Al menos 1 KPI en warning
- **ALTO**: Al menos 1 KPI en rojo pero no vencido
- **CRÍTICO**: Al menos 1 KPI vencido sin acción en curso

---

### W4: Tabla con Indicadores de Color

**Uso:** Listados (RATs, solicitudes, brechas).

**Estructura:**
```
┌────┬──────────────┬────────┬────────────┬────────┐
│ ID │ Proceso      │ Estado │ Vencimiento│ Acciones│
├────┼──────────────┼────────┼────────────┼────────┤
│ 1  │ Nómina      │ ✅ Activo│ 15 días    │ [⋮]   │
│ 2  │ Marketing   │ ⚠️ Por vencer│ 2 días│ [⋮]   │ ← rojo
│ 3  │ CRM         │ 🔴 Vencido│ -3 días  │ [⋮]   │
└────┴──────────────┴────────┴────────────┴────────┘
```

**Indicadores de color en filas:**
- Blanco: OK
- Amarillo claro (#FEF9C8): warning (por vencer pronto)
- Rojo claro (#FEE2E2): vencido o crítico
- Verde claro (#DCFCE7): resuelto o completado

---

### W5: Donut/Pie Chart

**Uso:** Distribución por estado.

```
    ┌────────────┐
    │   [donut]  │  Total: 24
    │    78%     │
    └────────────┘

leyenda:
● Aprobado: 12 (50%)
● En proceso: 6 (25%)
● Pendiente: 4 (17%)
● Vencido: 2 (8%)
```

---

### W6: Timeline de Eventos

**Uso:** Historial de cambios, auditoría.

```
● 15 Jun — RAT "Nómina" aprobado por María García
● 14 Jun — Solicitud ARCO #284 respondida
● 12 Jun — Brecha #3 notificada a APDP
● 10 Jun — EIPD "Marketing" completada
```

---

### W7: Alert Banner

**Uso:** Alertas críticas que requieren atención.

```
┌────────────────────────────────────────────────────────────────┐
│ 🔴 Tienes 2 solicitudes ARCO vencidas y 3 RATs por vencer     │
│    [Ver vencidas]  [Ver RATs]  [Dismiss]                      │
└────────────────────────────────────────────────────────────────┘
```

**Variantes:**
- 🔴 Error/Crítico: acción inmediata requerida
- 🟡 Warning: acción recomendada
- 🔵 Info: información útil

---

### W8: Progress Bar

**Uso:** Completitud de onboarding, progreso de wizard.

```
Complitud perfil: [██████░░░░] 60%

Obligatorios: 4/5
  ✅ Empresa creada
  ✅ DPO definido
  ✅ RAT inicial
  ❌ Política de transparencia — [Publicar ahora]
```

---

### W9: Countdown Timer

**Uso:** Plazos legales countdown.

```
┌─────────────────────────────────────────────┐
│ ⏱️ SLA ARCO #284                            │
│    2 días, 4 horas restantes                │
│    Vence: 20 Jun 2026 23:59                │
│    [Responder ahora]                        │
└─────────────────────────────────────────────┘
```

**Colores:**
- >48h: Verde
- 24-48h: Amarillo
- <24h: Rojo
- <4h: Rojo + animación pulsante

---

### W10: Quick Actions Bar

**Uso:** Acciones más frecuentes en un click.

```
┌─────────────────────────────────────────────────────────────┐
│ [＋ Nuevo RAT]  [📋 Ver pendientes]  [⚠️ 3 alertas]  [📤 Exportar] │
└─────────────────────────────────────────────────────────────┘
```

---

## Patrones de Layout por Contexto

### Dashboard Principal DPO (Empresa)

```
┌─────────────────────────────────────────────────────────────┐
│ SCORE + SEMÁFORO (full width)                             │
├──────────────────┬────────────────────────────────────────┤
│ KPI CARD         │ KPI CARD                               │
│ Total RATs       │ Completitud promedio                   │
├──────────────────┴────────────────────────────────────────┤
│                    │                                        │
│ DONUT POR ESTADO  │ ALERTAS ACTIVAS (priorizadas)        │
│                    │                                        │
├────────────────────┴────────────────────────────────────────┤
│ PRÓXIMOS DEADLINES (timeline)                              │
├─────────────────────────────────────────────────────────────┤
│ QUICK ACTIONS                                               │
└─────────────────────────────────────────────────────────────┘
```

### Dashboard de Módulo Específico (ej: ARCO)

```
┌─────────────────────────────────────────────────────────────┐
│ HEADER: Solicitudes ARCO  · [Filtros: ▼Estado] [📅 Fecha] │
├─────────────────────────────────────────────────────────────┤
│ KPI CARD     │ KPI CARD     │ KPI CARD     │ KPI CARD      │
│ Pendientes   │ Vencidas     │ Resueltas    │ Tiempo prom.  │
├──────────────────────────────┬──────────────────────────────┤
│                              │                               │
│ TABLA DE SOLICITUDES        │ PANEL DE DETALLE             │
│ (click abre drawer)         │ (derecha, slide-in)          │
│                              │                               │
├──────────────────────────────┴──────────────────────────────┤
│ QUICK ACTIONS                                               │
└─────────────────────────────────────────────────────────────┘
```

### Dashboard Superadmin (multi-empresa)

```
┌─────────────────────────────────────────────────────────────┐
│ Filtros: [▼Empresa] [▼Rubro] [▼Estado compliance]        │
├─────────────────────────────────────────────────────────────┤
│ TABLA MULTI-EMPRESA                                        │
│ Empresa │ Score │ RATs │ ARCO pend. │ Brechas │ Riesgo  │
│ CLINC   │ ████░░│  24  │     3      │    0    │ 🟡 MEDIO│
│ TechSpA │ ██░░░░│   8  │     7 ⚠️   │    1 🔴 │ 🔴 ALTO │
│ Retail  │ █████░│  15  │     0      │    0    │ 🟢 BAJO │
├─────────────────────────────────────────────────────────────┤
│ COMPARATIVA SECTORIAL (barras horizontales)                │
└─────────────────────────────────────────────────────────────┘
```

---

## Diseño de Alerts

### Jerarquía de alertas

| Nivel | Color | Icono | Significado | Acción requerida |
|-------|-------|-------|-------------|------------------|
| **Crítico** | 🔴 | ⚠️ | Vencimiento de plazo legal | Inmediata |
| **Warning** | 🟡 | ⏱️ | Por vencer pronto | Próximas 48h |
| **Info** | 🔵 | ℹ️ | Recordatorio | Programada |
| **Success** | 🟢 | ✅ | Cumplimiento | Ninguna |

### Rules de alert suppression

1. **No duplicar:** Si hay 5 solicitudes ARCO pendientes, mostrar 1 alerta "5 solicitudes pendientes", no 5 alertas individuales.
2. **No mostrar vencidas dos veces:** Si ya está en la tabla como vencida, no duplicar en alerts.
3. **Dismiss explícito:** Usuario puede descartar alerta individual o todas.
4. **Auto-resolve:** Alerta desaparece cuando la condición deja de cumplirse.

---

## Responsive Strategy

| Breakpoint | Layout adaptación |
|-----------|------------------|
| Desktop (>1280px) | 2 columnas, sidebar visible |
| Tablet (768-1280px) | 2 columnas, sidebar colapsable |
| Mobile (<768px) | 1 columna, tabs colapsados, drawer full-screen |

---

## Accesibilidad

- Todos los KPIs numéricos tienen `aria-label` con contexto
- Color no es el único diferenciador (símbolos + color)
- Tablas con `role="grid"` y headers marcados
- Focus visible en todos los elementos interactivos
- Alerts con `role="alert"` para screen readers
