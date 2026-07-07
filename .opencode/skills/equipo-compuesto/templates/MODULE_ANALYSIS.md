# Template: Análisis por Módulo — Equipo Compuesto Custodio RAT

Copiar este template y llenar para cada módulo analizado.

---

# [MÓDULO] — Análisis Equipo Compuesto

**Fecha:** `YYYY-MM-DD`
**Analista:** equipo-compuesto
**Estado del código relevado:** [ ] Explorado | [ ] No applicable

---

## 1. Perfil del Módulo

| Atributo | Detalle |
|----------|---------|
| **Nombre técnico** | |
| **Ruta backend** | `backend/app/<modelo>/`, `backend/app/services/<servicio>_service.py`, `backend/app/routes/<router>.py` |
| **Ruta frontend** | `frontend-next/app/(app)/<modulo>/` |
| **Modelo BD** | `backend/app/models/<modelo>.py` |
| **Módulo legal** | Art. X, Y, Z de Ley 21.719 |
| **Dependencias** | Qué módulos toca este módulo |
| **Usuarios objetivo** | DPO / Admin / Superadmin / Titular (público) |

---

## 2. Madurez Actual (1-5)

| Dimensión | Score | Comentario |
|-----------|:---:|---|
| Completitud legal | /5 | |
| Usabilidad | /5 | |
| Automatización | /5 | |
| Integración | /5 | |
| Auditoría | /5 | |
| **Promedio** | **/5** | |

---

## 3. Problemas Detectados

### 3.1 Perspectiva DPO

**Problemas de compliance legal:**

| # | Problema | Artículo relacionado | Severidad |
|---|----------|---------------------|:---:|
| D1 | | | |
| D2 | | | |
| D3 | | | |

**Plazos legales:**

| # | Plazo | Implementado? | Cumple? |
|---|-------|:---:|:---:|
| P1 | | [ ] | [ ] |
| P2 | | [ ] | [ ] |

**Campos obligatorios faltantes:**

| # | Campo faltante | Artículo que lo exige | Impacto |
|---|----------------|----------------------|---------|
| C1 | | | |
| C2 | | | |

### 3.2 Perspectiva Product Manager

**Problemas de valor:**

| # | Problema | Impacto en retention | Impacto en acquisition |
|---|----------|---------------------|------------------------|
| PM1 | | | |
| PM2 | | | |

**Friction en onboarding:**

| # | Situación | Tiempo perdido | Frecuencia |
|---|-----------|----------------|------------|
| F1 | | | |
| F2 | | | |

**Oportunidades de diferenciación:**

| # | Oportunidad | Competencia lo tiene? | Custodio lo tiene? |
|---|-------------|:---:|:---:|
| O1 | | [ ] | [ ] |
| O2 | | [ ] | [ ] |

### 3.3 Perspectiva UX/UI Lead

**Flujos problemáticos:**

| # | Flujo | Problema | Pains puntos por click | Alternativa propuesta |
|---|-------|----------|------------------------|----------------------|
| U1 | | | | |
| U2 | | | | |

**Alertas y notificaciones:**

| # | Alerta actual | Es accionable? | Ruido? | Mejora propuesta |
|---|---------------|:---:|:---:|---|
| A1 | | [ ] | [ ] | |
| A2 | | [ ] | [ ] | |

**Elementos de UI faltantes:**

| # | Elemento | Justificación UX | Prioridad |
|---|----------|------------------|:---:|
| UI1 | | | |
| UI2 | | | |

### 3.4 Perspectiva Auditor

**Trazabilidad:**

| # | Evento | Se loguea? | Evidencia immutable? | Gap |
|---|--------|:---:|:---:|---|
| AU1 | | [ ] | [ ] | |
| AU2 | | [ ] | [ ] | |

**Controles faltantes:**

| # | Control que falta | Riesgo sin el control | Mitigación propuesta |
|---|-------------------|------------------------|---------------------|
| C1 | | | |
| C2 | | | |

**Gaps para auditoría APDP:**

| # | Gap | Qué falta para auditor completa | Prioridad |
|---|-----|----------------------------------|:---:|
| G1 | | | |
| G2 | | | |

---

## 4. Oportunidades de Mejora

| # | Mejora | Impacto Legal (1-5) | Impacto Comercial (1-5) | Complejidad (1-5) | Cuadrante |
|---|--------|:---:|:---:|:---:|---|
| M1 | | | | | Quick Win / Mediano / Estratégico |
| M2 | | | | | |
| M3 | | | | | |
| M4 | | | | | |
| M5 | | | | | |

**Cuadrantes:**
- **Quick Win**: Impacto ≥3 AND Complejidad ≤2
- **Mediano**: Impacto ≥3 AND Complejidad 3-4
- **Estratégico**: Impacto ≥4 AND Complejidad ≥4

---

## 5. Diseño Propuesto

### 5.1 Estructura de navegación

```
[ ] Página de listado
[ ] Página de detalle
[ ] Wizard de creación
[ ] Modal de edición
[ ] Drawer de auditoría
[ ] Tabs/Pestañas (cuáles):
    - Tab 1:
    - Tab 2:
    - Tab 3:
```

### 5.2 Campos del formulario (completo)

**Obligatorios (art. X):**

| # | Campo | Tipo | Validación | Fuente legal |
|---|-------|------|------------|--------------|
| 1 | | | | |

**Recomendados:**

| # | Campo | Tipo | Validación |
|---|-------|------|------------|
| 1 | | | |

**Opcionales:**

| # | Campo | Tipo |
|---|-------|------|
| 1 | | |

**Campos que se podrían eliminar (no se usan):**

| # | Campo | Razón |
|---|-------|-------|
| 1 | | |

### 5.3 Flujo de usuario principal

```
[USER STORY]
Como [tipo de usuario]
quiero [acción]
para [beneficio]

FLUJO:
Paso 1: [Acción] → [Sistema responde]
Paso 2: [Acción] → [Sistema responde]
...
```

### 5.4 Estados y badges

| Estado | Color | Condición | Acciones disponibles |
|--------|-------|-----------|---------------------|
| | | | |

### 5.5 Validaciones sugeridas

| # | Campo | Validación | Mensaje de error |
|---|-------|------------|-----------------|
| 1 | | | |

---

## 6. Dashboard Recomendado

*(Usar framework de `DASHBOARD_FRAMEWORK.md`)*

### 6.1 KPIs principales

| KPI | Fuente de dato | Frecuencia |
|-----|-----------------|------------|
| 1 | | |

### 6.2 Widgets

**Widget 1: [Nombre]**
- Tipo: [KPI Card / Chart / Table / Alert / Timeline]
- Datos: [qué consulta/métrica]
- Threshold: [cuándo se pone rojo/amarillo]

**Widget 2: ...**

### 6.3 Mockup/wireframe en texto

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 7. Automatizaciones Recomendadas

| # | Automatización | Trigger | Acción | Prioridad | Módulo destino |
|---|----------------|---------|--------|:---:|---|
| 1 | | | | | |
| 2 | | | | | |

---

## 8. Indicadores de Riesgo

*(Usar matriz de `RISK_INDICATORS.md`)*

| # | Indicador | Fórmula SQL | Umbral Rojo | Umbral Amarillo |
|---|-----------|-------------|:---:|:---:|
| 1 | | | | |

---

## 9. Quick Wins (<1 semana)

| # | Quick win | Art. related | Impacto | Complejidad | Pasos |
|---|-----------|-------------|:---:|:---:|-------|
| 1 | | | | | 1. 2. 3. |

---

## 10. Mejoras Mediano Plazo (1-4 semanas)

| # | Mejora | Art. related | Impacto | Complejidad | Descripción |
|---|--------|-------------|:---:|:---:|------------|
| 1 | | | | | |

---

## 11. Mejoras Estratégicas (diferenciación Chile)

| # | Mejora estratégica | Diferenciación | Impacto | Complejidad | Por qué importa |
|---|-------------------|----------------|:---:|:---:|--------------|
| 1 | | | | | |

---

## 12. Dependencias con otros módulos

| Módulo | Cómo se relacionan | Cambio requerido |
|--------|---------------------|-------------------|
| | | |

---

## 13. Checklist de compliance

**Artículos de Ley 21.719 que aplica este módulo:**

- [ ] Art. X: [requisito] — **[Cumplido/No cumplimiento/Parcial]** — [evidencia]
- [ ] Art. Y: [requisito] — **[Cumplido/No cumplimiento/Parcial]** — [evidencia]

---

## 14. Tests recomendados

| # | Escenario | Pasos | Resultado esperado |
|---|-----------|-------|-------------------|
| 1 | | | |
| 2 | | | |

---

## 15. Notas adicionales

- Área de observaciones libres del equipo
