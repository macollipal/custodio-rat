---
name: consentimiento-management
description: Valida el ciclo de vida del consentimiento (Art. 12 Ley 21.719). Creacion, renovacion, revocacion, evidencia y almacenamiento seguro (cifrado Fernet).
---

# Consentimiento Management Validator

Especialista en consentimientos de tratamiento de datos personales bajo la Ley 21.719, Art. 12.

## Contexto Legal

Art. 12 — Consentimiento del titular:
- Debe ser libre, especifico, informado e inequivoco
- Puede revocarse en cualquier momento (efecto inmediato)
- La revocacion no afecta tratamientos realizados antes de ella
- Debe existir evidencia del consentimiento obtenido

## Modelo de Consentimiento en Custodio RAT

### Canales de obtencion
- WEB — formulario online
- PAPEL — documento fisico
- FIRMA_DIGITAL — firma electronica
- VERBAL — registrada con testigo
- OTRO

### Estados
- activo = True: consentimiento vigente
- activo = False: consentimiento revocado (fecha_revocacion debe existir)

## Cuando Usar Esta Skill

- Se crea o revoca un consentimiento
- Se auditan los consentimientos de un RAT o empresa
- Se detecta RAT sin consentimientos asociados
- Se acerca fecha de renovacion de consentimiento

## Checklist de Compliance

### 1. Identificacion del Titular
- [ ] nombre_titular presente (no puede ser nulo ni vacio)
- [ ] email_titular presente (para notificacion de revocacion)
- [ ] company_id corresponde a la empresa del solicitante

### 2. Datos del Consentimiento
- [ ] rat_id vinculado (proceso de tratamiento al que corresponde)
- [ ] canal registrado (WEB/PAPEL/FIRMA_DIGITAL/VERBAL/OTRO)
- [ ] texto_consentimiento presente (debe ser el texto exacto entregado)
- [ ] fecha_obtencion existe y es valida (no futura)

### 3. Almacenamiento Seguro
- [ ] nombre_titular_cipher existe (cifrado Fernet)
- [ ] email_titular_cipher existe (cifrado Fernet)
- [ ] texto_consentimiento_hash existe (SHA-256 para integridad)
- [ ] ip_origen_masked existe (IP del titular, enmascarada)

### 4. Revocacion (Art. 12)
- [ ] Si activo = False -> fecha_revocacion debe existir
- [ ] Si activo = False -> no debe haber tratamientos posteriores a fecha_revocacion
- [ ] La revocacion es inmediata: activo = False desde fecha_revocacion en adelante

### 5. Validez Temporal
- [ ] Si fecha_obtencion > 2 anos -> WARNING: considerar renovacion
- [ ] Consentimiento activo para RATs con datos sensibles -> verificar vigencia anual

### 6. Consentimiento vs RAT
- [ ] RAT que trata datos de menores -> consentimiento requiere representacion
- [ ] RAT con decisiones automatizadas -> consentimiento especifico para logica automatizada
- [ ] Si RAT tiene base_legal = "consentimiento" -> debe tener al menos 1 consentimiento activo

## Validacion Anti-Abuso

```
SI rat.base_legal == "consentimiento":
    SI consentimiento_para_rat_count == 0:
        -> FALLA: RAT requiere consentimiento pero no existe

SI consentimiento.activo == False:
    SI consentimiento.fecha_revocacion es NULL:
        -> FALLA: Consentimiento inactivo sin fecha de revocacion

SI consentimiento.canal == "VERBAL":
    SI consentimiento.texto_consentimiento_hash es NULL:
        -> WARNING: Consentimiento verbal sin evidencia hash
```

## Reporte de Compliance

```
## Consentimiento Compliance Report

**Consentimiento ID:** {id}
**Titular:** {nombre_titular}
**Empresa:** {company}
**RAT:** {rat_id}
**Canal:** {canal}
**Estado:** {activo}

### Identificacion
:green_circle: / :red_circle: Titular identificado

### Almacenamiento Seguro
| Campo | Estado |
|-------|--------|
| nombre_titular cifrado | :green_circle: / :yellow_circle: |
| email_titular cifrado | :green_circle: / :yellow_circle: |
| texto_hash | :green_circle: / :yellow_circle: |
| ip_masked | :green_circle: / :yellow_circle: |

### Vigencia
Otorgado: {fecha_obtencion} ({dias} dias)
:green_circle: Vigente / :yellow_circle: Por vencer (>1.5 anos) / :red_circle: Vencido (>2 anos)

### Revocacion
:green_circle: Activo / :yellow_circle: Revocado ({fecha_revocacion})

### RAT Vinculado
{rat_nombre}
Base legal: {base_legal}

### Acciones
1. [ ] Solicitar renovacion de consentimiento (>2 anos)
2. [ ] Revocar consentimiento si RAT cambia de base legal
```

## Integracion con Otras Skills

- **rat-compliance**: Verifica que RATs con base legal "consentimiento" tengan consentimientos activos
- **qa-senior**: Revision general de compliance
- **tester-rat**: Casos de prueba para consentimiento workflow
- **audit-service**: log_audit en cada creacion/revocacion
