---
name: breach-management
description: Valida el proceso de gestión de brechas de seguridad segun Art. 14 bis de la Ley 21.719. Notificacion 72h APDC, notificacion a titulares, calculo de riesgo.
---

# Breach Management Validator

Especialista en gestión de brechas de seguridad bajo la Ley 21.719 de Chile, Art. 14 bis.

## Contexto Legal

Art. 14 bis — Notificación de brechas:
- **72 horas hábiles** desde detección → notificar a APDC
- Si hay datos sensibles, menores o financieros → notificar a titulares "sin dilación"
- Debe documentarse: descripción, datos comprometidos, medidas adoptadas, naturaleza de la brecha

## Cuando Usar Esta Skill

- Usuario crea o edita una breach
- Se solicita auditoría de brechas
- Se acerca el plazo de 72h sin notificación
- Se detecta brecha sin registro en sistema

## Validación de Compliance

### Checklist de una Breach

#### 1. Identificación (obligatorio)
- [ ] descripcion — descripción clara del incidente
- [ ] fecha_deteccion — fecha y hora de cuando se descubrió
- [ ] fecha_ocurrencia_estimada — cuándo se estima que ocurrió (si aplica)
- [ ] rats_afectados — qué RATs involucra
- [ ] datos_comprometidos — qué categorías de datos se vieron afectadas

#### 2. Notificación APDC (plazo: 72h hábiles)
- [ ] notificado_apdc = True
- [ ] fecha_notificacion_apdc debe existir
- [ ] Plazo: fecha_notificacion_apdc - fecha_deteccion <= 72 horas hábiles
- [ ] evidencia_notificacion_apdc_folio — folio/número de caso APDC

#### 3. Notificación a Titulares
- [ ] Si incluye_datos_sensibles, incluye_datos_nna o incluye_datos_financieros → notificado_titulares debe ser True
- [ ] fecha_notificacion_titulares debe existir

#### 4. Evaluación de Riesgo (Art. 14 sexies)
- [ ] nivel_riesgo (bajo/medio/alto/crítico)
- [ ] volumen_titulares_afectados
- [ ] naturaleza (confidencialidad/integridad/disponibilidad)
- [ ] efectos_probables
- [ ] causa_raiz
- [ ] reportable_apdc_calculado (cálculo automático del sistema)

#### 5. Medidas y Cierre
- [ ] medidas_adoptadas — qué se hizo para contener
- [ ] estado_cierre — estado final del proceso
- [ ] fecha_cierre — fecha de cierre (si aplica)

## Cálculo de Plazo 72h

```
horas_desde_deteccion = (now - fecha_deteccion).total_hours()
# Días hábiles = exclude weekends
# Si > 72h hábiles sin notificación → ALERTA CRÍTICA
```

## Reporte de Compliance

```
## Breach Compliance Report

**Breach ID:** {id}
**Empresa:** {company}
**Fecha Deteccion:** {fecha}
**Días desde deteccion:** {dias}
**Plazo APDC:** {estado_plazo}

### Notificacion APDC
:green_circle: / :yellow_circle: / :red_circle: NOTIFICADO / PENDIENTE / VENCIÓ

### Notificacion Titulares
Obligatorio: {si/no}
Estado: {notificado/pendiente}

### Nivel Riesgo
{nivel} — Volumen: {volumen} titulares

### Acciones Requeridas
1. [ ] Notificar APDC antes de {fecha_limite}
2. [ ] Notificar titulares (datos sensibles detectados)
3. [ ] Documentar causa raíz
```

## Alertas Automáticas

| Condición | Severidad |
|-----------|-----------|
| 72h hábiles vencidas sin notificación APDC | CRÍTICO |
| Datos sensibles/menores sin notificación a titulares | CRÍTICO |
| Breach con nivel_riesgo = crítico | ALERTA |
| volumen_titulares > 1000 | ALERTA |
| Causa raíz no documentada a 7 días | WARNING |
