---
name: arco-rights
description: Valida el workflow ARCO (Acceso, Rectificacion, Cancelacion, Oposicion) segun Ley 21.719. Plazos, verificacion identidad, causal de rechazo, hash de evidencia.
---

# ARCO Rights Validator

Especialista en derechos ARCO (Acceso, Rectificación, Cancelación, Oposición) y derechos adicionales bajo la Ley 21.719.

## Contexto Legal

Art. 12 y 13 — Derechos de los titulares:
- Plazo de respuesta: **10 días hábiles** desde receipt
- Verificación de identidad obligatoria antes de entregar datos
- Causal de rechazo documentada si se rechaza
- evidencia_respuesta_hash para integridad de la respuesta
- metodo_verificacion_identidad documentado

Tipos de solicitud:
- ACCESO — solicita copia de sus datos
- RECTIFICACION — solicita corregir datos inexactos
- CANCELACION — solicita eliminar datos (cuando proceda)
- OPOSICION — se opone al tratamiento
- BLOQUEO — solicita bloqueo temporal
- PORTABILIDAD — solicita sus datos en formato portable

## Cuando Usar Esta Skill

- Usuario crea o responde una SolicitudDerecho
- Se detecta solicitud vencida (pasó plazo de 10 días hábiles)
- Se prepara reporte de compliance ARCO
- Se audita el flujo completo de ejercicio de derechos

## Validación de Compliance

### Checklist de una Solicitud ARCO

#### 1. Identificación del Titular
- [ ] nombre_titular presente
- [ ] rut_titular presente (opcional pero recomendado)
- [ ] email_titular presente
- [ ] metodo_verificacion_identidad documentado (requerido Art. 12)

#### 2. Datos de la Solicitud
- [ ] tipo — debe ser uno de: acceso, rectificacion, cancelacion, oposicion, bloqueo, portabilidad
- [ ] descripcion — motivo de la solicitud
- [ ] rat_id asociado (vinculación al proceso de tratamiento)
- [ ] company_id — debe corresponder a la empresa del titular

#### 3. Plazo Legal (10 días hábiles)
```
dias_habiles = calcular_dias_habiles(solicitud_fecha, hoy)
si dias_habiles > 10:
    ESTADO = VENCIDA
si dias_habiles <= 10 y estado == "resuelto":
    ESTADO = OK
```

- [ ] solicitud_fecha existe
- [ ] respuesta_fecha existe (si estado = resuelto)
- [ ] Plazo no superado

#### 4. Respuesta
- [ ] respuesta — texto de la respuesta
- [ ] medio_respuesta — cómo se respondió (email/carta/etc)
- [ ] evidencia_respuesta_hash — hash SHA-256 de la respuesta para integridad

#### 5. Causales de Rechazo (si estado = rechazada)
- [ ] causal_rechazo documentada (debe ser una causal válida Art. 12)
- [ ] evidencia de que se informó al titular del rechazo

#### 6. Bloqueo (si tipo = bloqueo)
- [ ] plazo_bloqueo_vencimiento documentado
- [ ] Alerta si plazo_bloqueo_vencimiento está próximo a vencer

## Validación Anti-Abuso

- [ ] No puede haber solicitud RESUELTA sin respuesta_fecha
- [ ] No puede haber solicitud RECHAZADA sin causal_rechazo
- [ ] No puede haber respuesta sin evidencia_respuesta_hash
- [ ] Si tipo = portabilidad → debe tener origen_dato_portabilidad en RAT asociado

## Reporte de Compliance

```
## ARCO Rights Compliance Report

**Solicitud ID:** {id}
**Tipo:** {tipo}
**Titular:** {nombre_titular}
**Empresa:** {company}
**Fecha Solicitud:** {fecha}
**Días Hábiles Transcurridos:** {dias}/10

### Estado de Plazo
:green_circle: DENTRO DE PLAZO ({dias}/10 días)
:yellow_circle: PRÓXIMO A VENCER (8-10 días)
:red_circle: VENCIDA ({dias} días)

### Checklist
| Campo | Estado |
|-------|--------|
| Identificación titular | :green_circle: |
| Verificación identidad | :yellow_circle: FALTA metodo_verificacion |
| RAT vinculado | :green_circle: |
| Respuesta | :green_circle: / :red_circle: FALTA |
| Evidencia hash | :yellow_circle: FALTA |
| Causal rechazo | :green_circle: / N/A |

### Acciones Requeridas
1. [ ] Responder antes de {fecha_limite}
2. [ ] Documentar método de verificación de identidad
3. [ ] Generar evidencia_respuesta_hash
```

## Métricas de Performance

| Métrica | Meta | Alertar si |
|---------|------|------------|
| Tiempo promedio de respuesta | < 7 días hábiles | > 8 días |
| Tasa de rechazo | < 15% | > 20% |
| Solicitudes vencidas activas | 0 | > 0 |
