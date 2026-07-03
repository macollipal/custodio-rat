# Protocolo de Respuesta a Incidentes de Seguridad

## Version
1.0.0 — 2026-07-03

## Objetivo

Este documento establece el protocolo de respuesta ante una brecha de seguridad de datos personales en Custodio RAT Manager, en cumplimiento del Art. 14 bis de la Ley 21.719.

## Definiciones

- **Brecha de seguridad**: cualquier acceso no autorizado, divulgacion, destruccion o perdida de datos personales.
- **Responsable**: la empresa (company) que trata datos personales a traves de Custodio RAT.
- **APDP**: Agencia de Proteccion de Datos Personales (el ente regulador en Chile).
- **DPO**: Delegado de Proteccion de Datos de la empresa.

---

## Fase 1: Contencion (0-4 horas)

### 1.1 Deteccion y Evaluacion Inicial

Al recibir alerta de brecha:

- [ ] Confirmar que existe una brecha (no es un falso positivo)
- [ ] Identificar el tipo: confidencialidad / integridad / disponibilidad
- [ ] Estimar alcance: numero de titulares afectados, volumen de datos
- [ ] Identificar RATs y procesos afectados

### 1.2 Contencion Inmediata

- [ ] Revocar credenciales expuestas (tokens, passwords, API keys)
- [ ] Bloquear acceso comprometido (invalidar sesiones, rotar secrets)
- [ ] Si hay acceso no autorizado a la BD: auditar logs de acceso
- [ ] Preserve evidencia (logs, timestamps, IPs) sin modificar

### 1.3 Evaluar si es Reportable a APDP

Una brecha DEBE notificarse a APDP si:
- [ ] Hay acceso no autorizado a datos personales
- [ ] La brecha genera riesgo para los derechos de los titulares

**Calculo de riesgo razonable** (Art. 14 sexies):
- [ ] Nivel de riesgo: bajo / medio / alto / critico
- [ ] Volumen de titulares afectados
- [ ] Incluye datos sensibles (biometricos, salud, menores, financieros)?
- [ ] Efectos probables documentados

---

## Fase 2: Notificacion (72 horas)

### 2.1 Notificacion a APDP (Obligatorio, maximo 72h)

**Deadline**: 72 horas habiles desde la deteccion

Contenido minimo de la notificacion:
1. Descripcion de la brecha (naturaleza, alcance)
2. Datos personales comprometidos (categorias)
3. RATs/procesos afectados
4. Medidas adoptadas para contener
5. Efectos probables para los titulares
6. Medidas para remediar la brecha

- [ ] Crear registro en `SecurityBreach` en Custodio RAT
- [ ] Subir evidencia de notificacion (folio APDP)
- [ ] Notificar al DPO de la empresa

### 2.2 Notificacion a Titulares (si aplica)

**Obligatorio sin dilacion** si:
- [ ] Incluye datos sensibles
- [ ] Incluye datos de menores
- [ ] Incluye datos financieros

Contenido para titulares:
1. Descripcion clara de la brecha
2. Datos comprometidos
3. Que esta haciendo la empresa para remediar
4. Medidas que el titular puede tomar
5. Canal de contacto para consultas

### 2.3 Documentacion

- [ ] Fecha y hora de deteccion
- [ ] Fecha y hora de notificacion APDP
- [ ] Folio/numero de caso APDP
- [ ] Lista de medidas adoptadas
- [ ] Notificaciones a titulares (fechas y metodos)

---

## Fase 3: Remediacion (72h en adelante)

### 3.1 Investigacion de Causa Raiz

- [ ] Determinar comooccurrio la brecha
- [ ] Identificar fallos en controles de seguridad
- [ ] Documentar causa raiz en `SecurityBreach.causa_raiz`

### 3.2 Medidas Correctivas

- [ ] Implementar medidas para prevenir recurrence
- [ ] Actualizar configuraciones de seguridad
- [ ] Revocar y rotar todas las credenciales expuestas
- [ ] Actualizar politicas de acceso

### 3.3 Cierre de la Brecha

- [ ] Todas las medidas implementadas y verificadas
- [ ] Estado de cierre: `cerrada`
- [ ] `fecha_cierre` establecida
- [ ] Revision final con DPO

---

## Roles y Responsabilidades

| Rol | Responsabilidad |
|-----|----------------|
| DPO de empresa | Declarar la brecha, liderar respuesta |
| Equipo tecnico | Contencion, remediacion tecnica |
| Responsable legal | Coordinar notificacion a APDP |
| Custodio RAT | Registro y trazabilidad de la brecha |

---

## Checklist de Cumplimiento

- [ ] Brecha registrada en Custodio RAT (`SecurityBreach`)
- [ ] Notificacion a APDP dentro de 72h habiles
- [ ] Evidencia de notificacion guardada (folio APDP)
- [ ] Notificacion a titulares (si corresponde)
- [ ] Causa raiz documentada
- [ ] Medidas correctivas implementadas
- [ ] Cierre de brecha registrado

---

## Referencia Legal

Art. 14 bis, 14 sexies — Ley 21.719 de Chile (Proteccion de Datos Personales).

Para mas informacion sobre el modelo de breach en Custodio RAT, ver skill `breach-management`.
