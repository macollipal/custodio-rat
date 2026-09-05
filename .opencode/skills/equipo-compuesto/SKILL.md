---
name: equipo-compuesto
description: DPO + PM + UX/UI Lead + Auditor. Análisis completo de los 9 módulos de Custodio RAT con perspectiva legal, comercial, UX y auditoría.
---

# Equipo Compuesto — Custodio RAT

Análisis de producto con 4 perspectivas integradas para cualquier módulo de Custodio RAT.

---

## El equipo

| Rol | Specialty | Focus |
|-----|-----------|-------|
| **DPO** | Ley 21.719 Chile | Compliance legal, Artikel mapping, plazos, derechos ARCO, transferencias, brechas |
| **Product Manager** | SaaS B2B compliance | Impacto comercial, diferenciación, retention, upsell, time-to-value |
| **UX/UI Lead** | GRC, ERP, enterprise | Flujos, fricción, adopción, mobile-first, accesibilidad |
| **Auditor** | Fiscalización APDP | Gaps regulatorios, trazabilidad, evidencia, missing controls |

---

## Módulos de Custodio RAT

| Módulo | Descripción | Art. clave |
|--------|-------------|-----------|
| **RAT** | Registro de Actividades de Tratamiento | Art. 16 |
| **Brechas** | Gestión de brechas de seguridad | Art. 14 bis |
| **EIPD** | Evaluaciones de Impacto | Art. 15 bis |
| **Consentimientos** | Ciclo de vida del consentimiento | Art. 12 |
| **ARCO** | Solicitudes de derechos ARCO | Arts. 12, 12.5 |
| **Encargados** | Contratos de encargado del tratamiento | Art. 14 quater |
| **Transparencia** | Políticas públicas | Art. 14 ter |
| **Reportes** | Exportación e informes | — |
| **Asesor IA** | Asistente RAG | — |

Stack: FastAPI + PostgreSQL (Neon) + Next.js + React + TypeScript + Tailwind + OCI Object Storage

---

## Protocolo de análisis

### Antes de analizar: explorar el código

**REGLA INVIOLABLE:** Nunca opinar sin explorar el código del módulo. Usar `explore-custodio` para levantar el estado actual.

Archivos mínimos a revisar:

```
backend/app/models/<modulo>.py          ← Estructura de datos
backend/app/schemas/<modulo>.py        ← Validaciones de entrada
backend/app/services/<modulo>_service.py ← Lógica de negocio
backend/app/routes/<modulo>.py          ← Endpoints
frontend-next/app/(app)/<modulo>/       ← UI pages
backend/tests/test_<modulo>*.py         ← Tests existentes
```

### Paso 1: Seleccionar módulo(s)

El usuario indica qué módulo(s) analizar. Se puede hacer uno, varios o todos.

### Paso 2: Relevar estado actual

El agente explora el código usando `explore-custodio`. Devuelve:
- Lista completa de campos con tipos
- Validaciones y constraints
- Relaciones con otros módulos
- Endpoints disponibles
- Workflows implementados
- Gaps evidentes vs. ley

### Paso 3: Análisis con 4 perspectivas

Para cada problema/mejora identificada, evaluar desde las 4 perspectivas:

**Perspectiva DPO:**
- Compliance con Ley 21.719: ¿Qué artículos exige qué?
- Plazos legales: ¿Están implementados correctamente?
- Campos obligatorios: ¿Faltan campos que la ley exige?
- Derechos de titulares: ¿Están bien implementados?
- Transferencias internacionales: ¿Están bien documentadas?
- Evidencia: ¿Los artefactos son immutable y auditables?

**Perspectiva Product Manager:**
- Valor para el cliente: ¿Qué problema real resuelve?
- Diferenciación: ¿Qué tiene que competencia no tenga?
- Retención: ¿Qué hace difícil dejar el producto?
- Upsell: ¿Qué módulos se pueden vender adicionalmente?
- Onboarding: ¿Cuánto tarda un cliente en tener valor?
- Time-to-value: ¿Dónde está el mayor friction?

**Perspectiva UX/UI Lead:**
- Flujos: ¿Son intuitivos? ¿Cuántos clicks para la acción más común?
- Información: ¿El usuario sabe qué hacer en cada momento?
- Alertas: ¿Las alertas son accionables o son ruido?
- Feedback: ¿El sistema confirma las acciones?
- Móvil: ¿Funciona bien en móvil (DPOs viajan)?
- Errores: ¿Los mensajes de error son útiles o técnicos?

**Perspectiva Auditor:**
- Trazabilidad: ¿Se puede auditar cada cambio?
- Evidencia: ¿Los artefactos son immutable?
- Completitud: ¿Los formularios capturan todo lo necesario?
- Gaps: ¿Qué falta para una auditoría APDP real?
- Controles: ¿Qué controles mitigan riesgos?
- Excepciones: ¿Qué pasa si el usuario hace algo mal?

### Paso 4: Priorización

Cada mejora se califica en:

| Score | Impacto Legal | Impacto Comercial | Complejidad |
|-------|:---:|:---:|:---:|
| **1** | Sin impacto | Sin impacto | Trivial (<1 día) |
| **2** | Bajo | Bajo | Simple (1-2 días) |
| **3** | Medio | Medio | Moderada (3-5 días) |
| **4** | Alto | Alto | Compleja (1-2 semanas) |
| **5** | Crítico | Muy alto | Muy compleja (>2 semanas) |

### Paso 5: Output estructurado

Para cada módulo, el output sigue el formato definido en `templates/MODULE_ANALYSIS.md`.

---

## Matriz Legal — Artículos Ley 21.719 por Módulo

| Artículo | Módulo | Requisito |
|----------|--------|-----------|
| Art. 5 | Company | Identificación del responsable del tratamiento |
| Art. 6 | RAT | Contenido mínimo del RAT (obligatorio por ley) |
| Art. 8 ter | ARCO | Bloqueo de tratamiento |
| Art. 9 | ARCO | Portabilidad de datos |
| Art. 12 | Consentimientos | Consentimiento libre, expreso, informado, inequívoco |
| Art. 12 | ARCO | Plazos de respuesta (10 días hábiles) |
| Art. 12 bis | ARCO | Prórroga (10 días hábiles adicionales, 1 vez) |
| Art. 12.5 | ARCO | Causales de rechazo |
| Art. 14 bis | Brechas | Notificación 72h a APDP + notificación a titulares |
| Art. 14 ter | Transparencia | Política de tratamiento pública |
| Art. 14 quater | Encargados | Contrato de encargado con cláusulas obligatorias |
| Art. 15 bis | EIPD | Evaluación de impacto obligatoria (datos sensibles, transferencias int.) |
| Art. 16 | RAT | 7 campos obligatorios + archivo si base legal no es "otra" |
| Art. 17 | — | Medidas de seguridad (implícito en RAT y encargado) |
| Art. 19 | Consentimientos | Cifrado de datos sensibles |
| Art. 20 | Audit | Registro de operaciones (audit_logs) |

---

## Dependencias entre Módulos

| Módulo A | Módulo B | Dependencia |
|----------|----------|-------------|
| RAT | EIPD | Si `datos_sensibles=True` o `transferencia_internacional=True` → EIPD obligatoria |
| RAT | Encargados | Si `nombre_encargado` existe → contrato obligatorio (Art. 14 quater) |
| RAT | Transparencia | Los RATs generan automáticamente los items de la política pública |
| RAT | Consentimientos | Datos sensibles requieren consentimiento expreso (Art. 12) |
| Brechas | RAT | `rats_afectados` referencia RATs de la empresa |
| ARCO | RAT | Puede bloquear un RAT (Art. 8 ter) y afectar plazos de retención |
| EIPD | RAT | 1:1 — cada EIPD pertenece a un RAT |
| Consentimientos | RAT | N:1 — un RAT puede tener N consentimientos |
| Encargados | RAT | Opcional — vínculo directo entre contrato y RAT |

---

## Score de Madurez por Módulo

Para cada módulo, calificar 1-5 en:

| Dimensión | Descripción |
|-----------|-------------|
| **Completitud legal** | ¿Cumple todos los requisitos de la ley? |
| **Usabilidad** | ¿Es fácil de usar para un DPO no-técnico? |
| **Automatización** | ¿Cuántos procesos son manuales vs. automáticos? |
| **Integración** | ¿Se integra bien con los otros módulos? |
| **Auditoría** | ¿Genera evidencia immutable para fiscalizaciones? |

**Escala:**
- 1 = No existe o no cumple
- 2 = Existe pero incompleto
- 3 = Cumple lo básico
- 4 = Completo y usable
- 5 = Best-in-class, diferenciador

---

## Quick Wins — Criterios

Son quick wins si cumplen TODOS estos criterios:
1. Impacto Legal ≥ 3 **o** Impacto Comercial ≥ 4
2. Complejidad ≤ 2
3. No requiere cambio de schema de BD (o es additive únicamente)
4. Se puede testear en < 1 día

---

## Reglas del skill

1. **Nunca opinar sin explorar el código primero.** Si no se entiende cómo funciona un módulo, usar `explore-custodio`.
2. **Siempre mapear a artículos de la ley.** Cada recomendación debe decir qué artículo motiva el cambio.
3. **El output debe ser accionable.** "Hay un gap" no sirve — "Falta el campo X que exige el Art. Y" sí.
4. **Priorizar con números, no con palabras.** Calificar 1-5 con rationale escrito.
5. **Costo/beneficio siempre.** Una mejora con complejidad 5 e impacto 1 no es prioritaria.
6. **El análisis completo de un módulo requiere el template** `templates/MODULE_ANALYSIS.md`.

---

## Uso del template

Cuando el usuario pide analizar un módulo, usar el template:

```
analiza el módulo [RAT|Brechas|EIPD|Consentimientos|ARCO|Encargados|Transparencia|Reportes|Asesor IA]
```

El agente debe:
1. Relevar el código con `explore-custodio`
2. Llenar `templates/MODULE_ANALYSIS.md` con los hallazgos
3. Aplicar el `templates/DASHBOARD_FRAMEWORK.md` para proponer dashboards
4. Usar `templates/RISK_INDICATORS.md` para calcular indicadores

---

## Output final por módulo

El agente produce:

```
# [MÓDULO] — Análisis Equipo Compuesto

## Problemas Detectados
[4 perspectivas]

## Oportunidades de Mejora
[Tabla priorizada 1-5]

## Diseño Propuesto
[Estructura, flujos, UI]

## Dashboard Recomendado
[Widgets y métricas]

## Automatizaciones Recomendadas
[Triggers y acciones]

## Indicadores de Riesgo
[Fórmulas y thresholds]

## Quick Wins (<1 semana)
[Lista]

## Mejoras Mediano Plazo (1-4 semanas)
[Lista]

## Mejoras Estratégicas (diferenciación Chile)
[Lista]

## Madurez Actual
[Scores 1-5 por dimensión]
```
