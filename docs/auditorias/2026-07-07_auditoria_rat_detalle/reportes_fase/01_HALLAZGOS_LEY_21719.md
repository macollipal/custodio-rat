# HALLAZGOS COMPLIANCE — Ley 21.719

**Fecha:** 2026-07-07
**Versión auditada:** v1.9
**Skills aplicadas:** `rat-compliance`, `eipd-management`, `consentimiento-management`, `encargado-tratamiento`, `breach-management`, `arco-rights`, `politica-transparencia`, `dpo-custodio`
**Score global compliance:** **8.2/10**

---

## Resumen Ejecutivo

El módulo RAT cumple **sustancialmente** con los artículos de la Ley 21.719. Los 7 campos obligatorios del Art. 16 están implementados con `nullable=False`, los flagsc condicionales (datos sensibles, transferencia internacional, decisiones automatizadas) tienen validators en schemas, y existe flujo EIPD + consentimiento + encargado vinculado. La fórmula de completitud es comprehensiva (25 campos: 7+3+5+10).

**Hallazgos principales:**
- ✅ Art. 16 — 7 obligatorios implementados correctamente
- ✅ Art. 15 bis — EIPD workflow con validación obligatoria
- ✅ Art. 12 — Consentimientos cifrados Fernet + revocación
- ✅ Art. 14 quater — Contratos PDF + validación
- ⚠️ Hallazgos menores en cobertura de Edge Cases (documentados abajo)

---

## Art. 16 — Registro de Actividades de Tratamiento (RAT)

### Status: ✅ CUMPLE (con gaps menores)

### 7 Campos Obligatorios

| # | Campo | Modelo | Schema | Validador | OK? |
|---|---|---|---|---|---|
| 1 | `nombre_proceso` | ✅ nullable=False | ✅ Field | ✅ `nombre_no_vacio` | ✅ |
| 2 | `categoria_datos` | ✅ nullable=False | ✅ Field | — | ✅ |
| 3 | `categoria_titulares` | ✅ nullable=False | ✅ Field(min_length=3) | — | ✅ (Z-04 cerrado) |
| 4 | `finalidad` | ✅ nullable=False (Text) | ✅ Field | — | ✅ |
| 5 | `base_legal` | ✅ nullable=False | ✅ Field | ✅ `base_legal_valida` (7 opciones) | ✅ |
| 6 | `fuente_datos` | ✅ nullable=False | ✅ Field | — | ✅ |
| 7 | `plazo_retencion` | ✅ nullable=False | ✅ Field | — | ✅ |

### 3 Campos Recomendados

| # | Campo | OK? |
|---|---|---|
| 1 | `medidas_seguridad` (Text, nullable) | ✅ |
| 2 | `destinatarios` (Text, nullable) | ✅ |
| 3 | `transferencia_datos` (Text, nullable) | ✅ |

### Fórmula de Completitud

`rat.py:133-185` — **25 campos totales**:
- 7 obligatorios Art. 16
- 3 recomendados Art. 16
- 5 Tier 1 críticos (Iter 11)
- 10 Tier 2 operativos (Iter 11)

Penalización: -1 si `base_legal != "Otra"` y sin archivo adjunto.

**Observación:** La fórmula de completitud penaliza correctamente la falta de documento de base legal, alineado con Art. 16.

### Flags de Compliance Condicional

| Condición | Campo requerido | Implementación | OK? |
|---|---|---|---|
| `datos_sensibles=True` | `tipo_dato_sensible` | ✅ `model_validator` RATCreate línea 121-122, RATUpdate línea 195-199 | ✅ |
| `datos_sensibles=True` | EIPD (`evaluacion_impacto=True`) | ✅ `_validar_eipd_obligatoria` rat_service.py:213 | ✅ |
| `decisiones_automatizadas=True` | `logica_automatizada` | ✅ RATCreate 118-120, RATUpdate 190-194 | ✅ |
| `transferencia_internacional=True` | `pais_destino` + `garantias_transferencia_int` | ✅ RATCreate 113-117, RATUpdate 182-189 | ✅ |
| `nombre_encargado` existe | `tiene_contrato_encargado=True` | ✅ `_validar_contrato_encargado` rat_service.py:199 | ✅ |
| `base_legal="Otra"` | `archivo_base_legal_datos` | ⚠️ WARNING en fórmula, no bloquea | ⚠️ |

### Hallazgos Art. 16

#### ⚠️ H1.1: `base_legal="Otra"` sin archivo no es bloqueante
- **Severidad:** Media
- **Ubicación:** `rat.py:181-184`
- **Detalle:** La fórmula de completitud penaliza -1 si no hay archivo, pero el sistema permite guardar un RAT con `base_legal="Otra"` sin documento adjunto. La Ley 21.719 requiere que TODA base legal tenga documentación respaldatoria (Art. 16 + Art. 11 sobre deber de informar).
- **Recomendación:** Bloquear creación/actualización con `HTTPException(422)` si `base_legal="Otra"` y `archivo_base_legal_datos` es None.
- **Prioridad:** P1 (compliance, no bloqueante en deploy actual)

#### ✅ H1.2: 7 obligatorios correctos
Todos los campos del Art. 16 están implementados con `nullable=False` y validación.

#### ✅ H1.3: Validador de email del responsable
`schemas/rat.py:73-81` — Regex `^[\w.\-]+@[\w.\-]+\.\w{2,}$` correcto.

---

## Art. 15 bis — Evaluación de Impacto (EIPD)

### Status: ✅ CUMPLE

### Workflow Implementado

```
no_requerida → pendiente → en_proceso → completada
                  o
                  no_requerida_justificada (con justificación ≥20 chars)
```

### Gatillos

✅ `datos_sensibles=True` o `transferencia_internacional=True` requieren EIPD.

### Validación (`rat_service.py:213-262`)

```python
if estado_eipd == "no_requerida":
    raise HTTPException(422, "Requiere EIPD...")
if estado_eipd == "no_requerida_justificada" and len(justificacion) < 20:
    raise HTTPException(422, "Justificación ≥20 caracteres")
if not evaluacion_impacto:
    raise HTTPException(422, "evaluacion_impacto=True requerido")
```

### Hallazgos Art. 15 bis

#### ✅ H2.1: Workflow EIPD correctamente implementado
Validación robusta con múltiples paths.

#### ⚠️ H2.2: Sin plazo automático para EIPD en proceso >90 días
- **Severidad:** Media
- **Ubicación:** `rat_service.py:449-452` solo cuenta, no alerta
- **Detalle:** El dashboard cuenta `eipd_pendientes` pero no hay scheduler que notifique al DPO cuando una EIPD lleva >90 días en proceso.
- **Recomendación:** Agregar a `scheduler.py` tarea `notificar_eipd_vencida()` que envíe email al DPO.
- **Prioridad:** P2

---

## Art. 12 — Consentimiento

### Status: ✅ CUMPLE

### Implementación

- ✅ Cifrado Fernet para `nombre_titular` y `email_titular` (PII)
- ✅ Hash SHA-256 para `texto_consentimiento` (integridad)
- ✅ IP enmascarada
- ✅ Endpoint `POST /rats/{rat_id}/consentimientos` (REC-06)
- ✅ Endpoint de revocación `POST /consentimientos/{id}/revocar`

### Validación al crear RAT

`update_rat` línea 318-319:
```python
if cambios.get("datos_sensibles") == True and not _tiene_consentimiento_activo(db, rat_id):
    _validar_consentimiento_sensibles(db, rat)
```

### Hallazgos Art. 12

#### ⚠️ H3.1: Sin renovación automática de consentimiento >2 años
- **Severidad:** Media
- **Detalle:** La skill `consentimiento-management` recomienda alerta a >2 años. No hay scheduler.
- **Prioridad:** P2

#### ✅ H3.2: Cifrado PII robusto
Fernet + SHA-256 para texto_consentimiento según Art. 11 deber de confidencialidad.

---

## Art. 14 quater — Encargados del Tratamiento

### Status: ✅ CUMPLE

### Validación (`rat_service.py:199-210`)

```python
if rat.nombre_encargado and not _tiene_contrato_encargado_activo(db, rat.id):
    raise HTTPException(422, "Este RAT tiene un encargado ... requiere contrato ...")
```

### Hallazgos Art. 14 quater

#### ✅ H4.1: Validación cruzada RAT↔Contrato implementada
Si RAT tiene `nombre_encargado` pero no hay contrato activo, bloquea.

#### ⚠️ H4.2: Sin test específico del flujo RAT con contrato
- **Severidad:** Baja
- **Detalle:** Existe `test_contrato_encargado.py` pero no test que valide el flujo: crear contrato → crear RAT vinculado → intentar borrar contrato → verificar error.
- **Prioridad:** P2

---

## Art. 14 bis — Brechas de Seguridad

### Status: ✅ CUMPLE (módulo separado)

Aunque no es parte del RAT, se menciona porque el dashboard RAT referencia brechas (`brechas_por_empresa`).

- ✅ Notificación 72h a APDC
- ✅ Notificación a titulares
- ✅ Módulo `breach_service.py` separado

---

## Art. 14 ter — Política de Transparencia

### Status: ✅ CUMPLE (módulo separado)

- ✅ Endpoint público `/publico/transparencia/{company_id}`
- ✅ Sin auth requerida (diseño correcto)
- ✅ Aplica solo a empresas con módulo transparencia habilitado

---

## ARCO — Derechos del Titular

### Status: ✅ CUMPLE (módulo separado)

- ✅ Workflow ARCO completo (Acceso, Rectificación, Cancelación, Oposición)
- ✅ 10 días hábiles (configurable)
- ✅ Plantillas de respuesta
- ✅ Módulo separado (no parte del RAT)

---

## Resumen de Hallazgos Compliance

| Código | Severidad | Hallazgo | Prioridad |
|---|---|---|---|
| **H1.1** | Media | `base_legal="Otra"` sin archivo no bloquea | **P1** |
| H2.2 | Media | Sin alerta EIPD >90 días en scheduler | P2 |
| H3.1 | Media | Sin renovación automática consentimiento >2 años | P2 |
| H4.2 | Baja | Sin test cruzado RAT-contrato | P2 |

---

## Score Compliance por Artículo

| Artículo | Status | Score |
|---|---|---|
| Art. 16 (RAT base) | ✅ | 9.5/10 |
| Art. 15 bis (EIPD) | ✅ | 9/10 |
| Art. 12 (Consentimiento) | ✅ | 9/10 |
| Art. 14 quater (Encargado) | ✅ | 9/10 |
| Art. 14 bis (Brechas) | ✅ | 8.5/10 |
| Art. 14 ter (Transparencia) | ✅ | 9/10 |
| ARCO | ✅ | 9/10 |
| **PROMEDIO** | | **9.0/10** |

> Nota: El score global compliance es **8.2/10** porque se penaliza levemente por los gaps de automatización (scheduler) y el H1.1.

---

## Acciones Recomendadas

### P1 (Compliance bloqueante para auditoría APDC)
1. **H1.1:** Bloquear `base_legal="Otra"` sin archivo con `HTTPException(422)` en `create_rat` y `update_rat`.

### P2 (Mejoras continuas)
2. **H2.2:** Agregar tarea programada `notificar_eipd_vencida()` en `scheduler.py`.
3. **H3.1:** Agregar tarea programada `solicitar_renovacion_consentimiento()`.
4. **H4.2:** Crear test integral RAT-contrato.

---

**Próxima fase:** Auditoría Multi-Tenant + API (Fase 2)