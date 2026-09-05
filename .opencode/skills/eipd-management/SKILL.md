---
name: eipd-management
description: Valida el workflow de EIPD (Evaluacion de Impacto en Proteccion de Datos, Art. 15 bis). Estados, plazos, responsables, metodologia y resultado.
---

# EIPD Management Validator

Especialista en Evaluaciones de Impacto en la Proteccion de Datos (EIPD / DPIA) bajo la Ley 21.719, Art. 15 bis.

## Contexto Legal

Art. 15 bis — Evaluacion de Impacto (EIPD/DPIA):
Obligatoria cuando el tratamiento de datos puede generar un riesgo alto para los derechos y libertades de los titulares. Condiciones que requieren EIPD:
- Datos sensibles (biometricos, salud, menores)
- Perfilamiento automatizado
- Transferencias internacionales de alto riesgo
- Tratamiento a gran escala

La EIPD debe ser documentada antes de iniciar el tratamiento.

## Modelo EIPD en Custodio RAT

Workflow de estados:
```
no_requerida -> pendiente -> en_proceso -> completada
                o
                no_requerida_justificada (cuando no aplica pero se documenta por que)
```

## Cuando Usar Esta Skill

- Se crea o edita un RAT con evaluacion_impacto = True
- Se solicita auditoria de EIPDs vigentes
- Se acerca fecha de revision de una EIPD existente
- Se detecta RAT con datos_sensibles sin EIPD vinculada

## Checklist de Compliance

### 1. Gatillo — Cuando se requiere EIPD
- [ ] rat.evaluacion_impacto = True
- [ ] RAT tiene estado_eipd != "no_requerida" (debe ser pendiente, en_proceso, o completada)
- [ ] Si rat.datos_sensibles = True -> EIPD obligatoria (no_requerida NO es valido)

### 2. Vinculacion RAT-EIPD
- [ ] eipd.rat_id existe y es unico (1 EIPD por RAT)
- [ ] RAT.estado_eipd es consistente con eipd.resultado
- [ ] Si eipd.resultado = "no_requerida_justificada" -> RAT.estado_eipd = "no_requerida_justificada"

### 3. Contenido Minimo (Art. 15 bis)
- [ ] metodologia — metodo utilizado (ej: PIA, CNIL, NIST)
- [ ] objetivos — objetivos del tratamiento
- [ ] necesidad_proporcionalidad — por que es necesario y proporcional
- [ ] riesgos_identificados — riesgos para los titulares
- [ ] medidas_propuestas — medidas para mitigar los riesgos

### 4. Aprobacion DPO
- [ ] parecer_dpo — opinion formal del DPO
- [ ] parecer_dpo_autor — nombre del DPO que emite el parecer
- [ ] parecer_dpo_fecha — fecha del parecer

### 5. Fechas
- [ ] fecha_elaboracion — cuando se elaboro la evaluacion
- [ ] fecha_aprobacion — cuando fue aprobada
- [ ] Si resultado = "en_proceso" y han pasado > 60 dias -> ALERTA

### 6. Resultado Final
| Resultado | Significado |
|-----------|------------|
| completada | EIPD realizada y aprobada |
| en_proceso | EIPD en curso |
| no_requerida | No aplica (rat no requiere EIPD) |
| no_requerida_justificada | No aplica pero se documenta la justificacion |

## Validacion de Consistencia RAT-EIPD

```
SI rat.evaluacion_impacto == True:
    SI eipd NO existe:
        -> FALLA: RAT requiere EIPD pero no esta creada
    SI eipd.resultado == "no_requerida":
        -> FALLA: EIPD no puede ser no_requerida si el RAT la indica como necesaria
    SI eipd.resultado == "en_proceso" AND dias_desde_creacion > 90:
        -> WARNING: EIPD en proceso hace mas de 90 dias

SI rat.datos_sensibles == True:
    SI eipd.resultado != "completada":
        -> WARNING: Datos sensibles requieren EIPD completada

SI rat.evaluacion_impacto == False:
    SI eipd.resultado != "no_requerida" AND != "no_requerida_justificada":
        -> WARNING: RAT indica que no requiere EIPD pero EIPD existe con otro resultado
```

## Reporte de Compliance

```
## EIPD Compliance Report

**RAT ID:** {rat_id}
**Empresa:** {company}
**Estado RAT:** {estado_eipd}
**Resultado EIPD:** {resultado}

### Gatillo
:green_circle: / :red_circle: EIPD requerida (datos_sensibles/perfilamiento/transf.int)

### Vinculacion RAT-EIPD
:green_circle: EIPD vinculada correctamente
:red_circle: RAT requiere EIPD pero no existe

### Contenido
| Campo | Estado |
|-------|--------|
| metodologia | :green_circle: / :yellow_circle: |
| objetivos | ... |
| necesidad_proporcionalidad | ... |
| riesgos_identificados | ... |
| medidas_propuestas | ... |
| parecer_dpo | ... |

### Plazos
EIPD en proceso: {dias} dias (maximo recomendado: 90)
```

## Integracion con Otras Skills

- **rat-compliance**: Usa para detectar RATs que requieren EIPD
- **qa-senior**: Revision general de compliance
- **tester-rat**: Casos de prueba para EIPD workflow
