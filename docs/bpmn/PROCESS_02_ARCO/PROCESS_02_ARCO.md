# PROCESS_02_ARCO: Gestión Derechos ARCO
## Custodio SaaS Platform - Cumplimiento Ley 21.719 Chile

**Versión:** 2.1  
**Fecha:** 2026-08-08 (actualización) / 2026-06-18 (original)  
**Propietario:** DPO  
**Clasificación:** Operacional - Crítico  

> **Nota de actualización (2026-08-08):** El formulario público legacy en `/solicitud_derecho`
> fue eliminado en julio 2026 junto con el modelo `SolicitudDerecho`.
>
> **Nota de actualización (2026-08-09 — C-08):** Se implementó el nuevo formulario público
> en `/ejercer-derechos` (frontend) que crea tickets `TktSolicitudDerecho` vía
> `POST /publico/ejercer-derechos` (rate limit 10/h por IP, sin auth).
> El seguimiento del titular sigue disponible en `/seguimiento/{tracking_token}`.

---

## 1. EXPLICACIÓN FUNCIONAL

### Propósito
Este proceso constituye el núcleo central de gestión de los derechos ARCO (Acceso, Rectificación, Cancelación, Oposición) establecidos en la Ley 21.719 que modifica la Ley 19.628 sobre Protección de la Vida Privada. El proceso abarca el ciclo completo desde la recepción pública de solicitudes hasta su resolución definitiva, garantizando trazabilidad inmutable mediante hashchain y cumplimiento estricto de los plazos legales.

### Derechos Cubiertos
| Derecho | Base Legal | Descripción |
|---------|------------|-------------|
| **Acceso** | Art. 8 lit. a | Derecho a conocer qué datos personales son tratados |
| **Rectificación** | Art. 9 | Derecho a corregir datos inexactos o incompletos |
| **Cancelación** | Art. 8 lit. c | Derecho a eliminar datos personales |
| **Oposición** | Art. 13 | Derecho a oponerse al tratamiento |
| **Bloqueo** | Art. 8 ter | Suspensión temporal del tratamiento |
| **Portabilidad** | Art. 12 | Derecho a recibir datos en formato estructurado |

### Macro-Fases del Proceso

#### FASE 1: Recepción y Validación
Etapa inicial donde se recibe la solicitud del titular mediante formulario público, se validan los datos de entrada (RUN, email, archivos), se detecta si es una solicitud por representante, y se genera el ticket inicial con tracking único.

#### FASE 2: Gestión y Evaluación
Fase de procesamiento donde se evalúa la solicitud según su tipo, se determinan las acciones necesarias (subsanación, prorroga), se asigna al DPO correspondiente mediante reglas QW9, y se verifica el cumplimiento de plazos.

#### FASE 3: Resolución
Etapa final de decisión donde el DPO determina la resolución (favorable o rechazada), se generan los documentos de respuesta según plantillas QW6, y se notifica al titular.

#### FASE 4: Cierre y Archivo
Cierre del proceso con actualización del hashchain de bitácora M1, archivado del ticket en estado terminal, y consolidación de métricas.

---

## 2. BPMN TEXTUAL DETALLADO

### FASE 1 - RECEPCIÓN

**Inicio del Proceso (dos canales):**
- **StartEvent A:** "Titular envía solicitud vía formulario público" (`/ejercer-derechos` → `POST /publico/ejercer-derechos`, sin auth, rate limit 10/h)
- **StartEvent B:** "Staff crea ticket ARCO interno" (endpoint `POST /tkt-solicitud-derecho/`, requiere auth)

**Actividades del Staff/DPO (Lane: Staff):**
- **TareaUsuario:** "Registrar solicitud ARCO recibida (email/carta/presencial)"
  - Campos obligatorios: `titular_nombre`, `titular_email`, `tipo`, `descripcion`, `company_id`
  - Campos opcionales: `titular_rut`, `telefono`, `rat_id`, `representante_nombre`, `representante_rut`
  - Campo `tipo`: selección de 6 opciones (acceso, rectificacion, cancelacion, oposicion, bloqueo, portabilidad)
  - El titular NO accede al sistema directamente para crear la solicitud

**Actividades del Sistema (Lane: Sistema):**
- **TareaSistema:** "Validar datos de entrada"
  - Valida campos obligatorios
  - Valida tipo en enum permitido
  - Valida company_id para el usuario autenticado

- **GatewayExclusivo:** "¿Datos válidos?"
  - **No** → **TareaSistema:** "Retornar 422 con detalle del error"
  - **Sí** → Continúa flujo

- **GatewayExclusivo:** "¿Es solicitud de REPRESENTANTE?"
  - `representante_nombre` presente
  - **Sí** → Staff registra `representante_nombre` + `representante_rut`
  - **No** → Continúa flujo

- **TareaSistema:** "Crear TktSolicitudDerecho con estado=abierto"
  - Genera `tracking_token` (UUID v4 único)
  - Registra `rat_id` (identificador interno)
  - Timestamp de creación

- **TareaSistema:** "Generar hash inicial bitácora M1"
  - Hash SHA-256 con: tracking_token + timestamp + estado
  - Almacena en campo `hash_inmutable`

- **TareaSistema:** "Notificar acuse de recibo al titular"
  - Canal: Sistema de Correo
  - Incluye link de seguimiento: `/seguimiento/{tracking_token}`
  - Template: QW6-001

- **TareaSistema:** "Registrar acuse_enviado_at"
  - Timestamp de envío de notificación

---

### FASE 2 - GESTIÓN

**Actividades del Sistema (Lane: Sistema):**

- **TareaSistema:** "Auto-asignar por reglas QW9"
  - Evalúa `TktReglaAsignacion`
  - Ponderación: `company=4`, `tipo=2`, `prioridad=1`
  - Asigna DPO disponible con menor carga

- **GatewayExclusivo:** "¿Asignación automática exitosa?"
  - **No** → **TareaUsuario:** "DPO asigna manualmente" (DPO Senior selecciona)
  - **Sí** → Continúa flujo

- **TareaSistema:** "Evaluar necesidad subsanación"
  - Analiza si documentación está completa
  - Evalúa si hay campos faltantes o ambiguous

- **GatewayExclusivo:** "¿Requiere subsanación?"
  - **Sí** → Flujo **SUBSANACION** (subproceso detallado abajo)
  - **No** → Continúa flujo

- **TareaSistema:** "Verificar plazo"
  - Calcula días restantes hasta vencimiento
  - Compara contra umbral de 8 días

- **GatewayExclusivo:** "¿Plazo próximo a vencer (>8 días)?"
  - **No** → Continúa flujo
  - **Sí** → **TareaSistema:** "Invocar Art. 12 bis - Prórroga"

- **GatewayExclusivo MULTIPLE:** "Evaluar tipo de solicitud"
  - 6 branches según valor de `tipo_solicitud`:
    - `acceso` → **TareaUsuario:** "Revisar solicitud ACCESO"
    - `rectificacion` → **TareaUsuario:** "Revisar solicitud RECTIFICACIÓN"
    - `cancelacion` → **TareaUsuario:** "Evaluar excepciones Art. 8 c.ii"
    - `oposicion` → **TareaUsuario:** "Evaluar base legal tratamiento"
    - `bloqueo` → **TareaSistema:** "Procesar BLOQUEO Art. 8 ter"
    - `portabilidad` → **TareaUsuario:** "Identificar datos para exportación"

---

#### SUBPROCESO: SUBSANACION

**Activación:** Gateway "¿Requiere subsanación?" = Sí

**Actividades del Sistema (Lane: Sistema):**
- **TareaSistema:** "Establecer estado=SUBSANACION"
- **TareaSistema:** "Establecer `subsanacion_fecha_pedido` = hoy"
- **TareaSistema:** "Establecer `subsanacion_detalle`" (lista de documentos requeridos)
- **TareaSistema:** "Enviar notificación subsanación" (Sistema de Correo)
  - Template: QW6-002
  - Incluye plazo de respuesta

**Actividades del Titular (Lane: Titular):**
- **TareaUsuario:** "Titular completa documentación"
  - Acceso vía formulario en `/seguimiento/{tracking_token}`
  - Puede subir hasta 5 archivos de hasta 5MB cada uno

**Gateway Exclusivo:** "¿Plazo subsanación vencido (>10 días hábiles)?"
- **Sí** → Flujo **RECHAZAR** (ver sección correspondiente)
- **No** → Continúa flujo

**Actividades del Sistema (Lane: Sistema):**
- **TareaSistema:** "Restablecer estado=EN_PROCESO"
- **TareaSistema:** "Resetear plazo (+10 días hábiles)"
  - Actualiza `plazo_bloqueo_vencimiento`

**Fin subproceso SUBSANACION**

---

#### SUBPROCESO: PRÓRROGA (Art. 12 bis)

**Activación:** Gateway "¿Plazo próximo a vencer?" = Sí

**Gateway Exclusivo:** "¿prorroga_fecha IS NULL?"
- Valida que no se haya solicitado prorroga anteriormente (solo una vez permitido)
- **No** → No permite prorrogar (ya se usó)
- **Sí** → Continúa flujo

**Actividades del Sistema (Lane: Sistema):**
- **TareaSistema:** "Establecer estado=PRORROGA"
- **TareaSistema:** "Establecer `prorroga_fecha` = hoy, `prorroga_dias` = 10"
- **TareaSistema:** "Enviar notificación prorroga" (Sistema de Correo)
  - Template: QW6-003
  - Informa nuevo plazo al titular

**Fin subproceso PRÓRROGA**

---

### FASE 3 - RESOLUCIÓN

**GatewayExclusivo:** "Decision DPO"
- 2 branches según evaluación del DPO

#### Rama Favorable:

**TareaUsuario:** "DPO selecciona plantilla respuesta QW6"
- Selecciona template según tipo de solicitud y resolución

**TareaSistema:** "Establecer estado=RESUELTO"

**TareaSistema:** "Generar archivos exportación (PDF/CSV/Excel)"
- Para ACCESO: Exportación completa de datos
- Para RECTIFICACION: Documento con cambios aplicados
- Para PORTABILIDAD: Archivo JSON/CSV con datos estructurados
- Para CANCELACION/BLOQUEO: Confirmación de acción tomada

**TareaSistema:** "Notificar resolución favorable"
- Canal: Sistema de Correo
- Incluye link de descarga (válido 30 días)
- Template: QW6-004

#### Rama Rechazado:

**TareaUsuario:** "DPO ingresa fundamento legal"
- Campo obligatorio según Art. 15
- Selecciona causal de rechazo

**TareaSistema:** "Establecer estado=RECHAZADO"

**TareaSistema:** "Notificar rechazo con fundamento"
- Canal: Sistema de Correo
- Incluye texto del fundamento legal
- Template: QW6-005

---

**Actividades del Sistema (Lane: Sistema):**
- **TareaSistema:** "Actualizar hashchain bitácora M1"
  - Genera nuevo hash: hash_anterior + estado_nuevo + timestamp
  - Mantiene cadena de bloques de integridad

---

### FASE 4 - CIERRE

**Actividades del Sistema (Lane: Sistema):**

- **TareaSistema:** "Actualizar historial de cambios" (hashchain M1)
  - Registra todas las transiciones de estado
  - Consolida evidencia de cumplimiento

- **TareaSistema:** "Archivar ticket" (estado terminal)
  - Establece `archivado_en` = timestamp
  - Transición a estado: CERRADO

- **EndEvent:** "Solicitud ARCO cerrada"

---

### FLUJO DE RECHAZO (Manejo de Rechazos)

**Activación:** Desde subproceso SUBSANACION (plazo vencido) o decisión DPO

**GatewayExclusivo:** "¿Rechazo fundado?"
- Valida que exista fundamento legal seleccionado
- **No** → No puede rechazar (requiere fundamento)
- **Sí** → Continúa flujo

**TareaUsuario:** "DPO redacta fundamento legal"
- Campo obligatorio
- Guía según causales del Art. 15

**TareaSistema:** "Guardar en campo observaciones"
- Almacena texto del fundamento
- Adjunta evidencia

**TareaSistema:** "Enviar notificación rejection"
- Sistema de Correo
- Template: QW6-006

---

## 3. TABLA RACI

| Actividad | Titular | DPO | DPO Senior | Sistema | Sistema de Correo | APDC |
|-----------|:-------:|:---:|:----------:|:-------:|:-----------------:|:----:|
| Recibir solicitud | **R** | - | - | A | - | I |
| Validar datos | I | - | - | **R/A** | - | - |
| Asignar | - | C | **R** | A | - | I |
| Evaluar subsanación | I | **R** | - | A | - | - |
| Subsanar | **R** | C | - | A | I | - |
| Prorrogar | I | C | - | **R/A** | I | - |
| Resolver | C | **R** | A | A | - | I |
| Rechazar | I | **R** | A | A | I | - |
| Notificar | - | I | - | A | **R** | - |
| Exportar | I | C | - | **R/A** | - | - |
| Archivar | I | I | - | **R/A** | - | I |

**Leyenda:** R=Responsable, A=Accountable, C=Consultado, I=Informado

---

## 4. EVENTOS

### Eventos de Inicio
| Evento | Tipo | Descripción |
|--------|------|-------------|
| Formulario público recibido | Start A | Titular envía solicitud vía `/ejercer-derechos` → `POST /publico/ejercer-derechos` (sin auth) |
| Ticket creado por staff | Start B | DPO/admin registra solicitud recibida vía `POST /tkt-solicitud-derecho/` (auth requerida) |

### Eventos de Fin
| Evento | Tipo | Descripción |
|--------|------|-------------|
| Solicitud ARCO cerrada | End | Ticket en estado terminal (RESUELTO o RECHAZADO) |

### Eventos de Tiempo (Timer Intermediate)
| Evento | Duración | Descripción |
|--------|----------|-------------|
| Plazo subsanación | 10 días hábiles | Tiempo para que titular complete documentación |
| Plazo prórroga | 10 días | Ampliación de plazo Art. 12 bis |
| Recordatorio 72h | 3 días (72h) | Antes del vencimiento de plazo |

### Eventos de Señal (Signal)
| Evento | Descripción |
|--------|-------------|
| Notificación cambio estado | Signal broadcast cuando cambia estado del ticket |

---

## 5. DATOS UTILIZADOS

### Estructura TktSolicitudDerecho

| Campo | Tipo | Descripción | Requerido |
|-------|------|-------------|:---------:|
| `tracking_token` | UUID v4 | Identificador único público | Sí |
| `estado` | ENUM | ABRIRTO, EN_PROCESO, SUBSANACION, PRORROGA, RESUELTO, RECHAZADO, CERRADO | Sí |
| `tipo` | ENUM | ACCESO, RECTIFICACION, CANCELACION, OPOSICION, BLOQUEO, PORTABILIDAD | Sí |
| `rat_id` | VARCHAR(50) | Identificador interno del sistema | Sí |
| `nombre` | VARCHAR(200) | Nombre completo del titular | Sí |
| `run` | VARCHAR(12) | RUN sin puntos, con dv | Sí |
| `email` | VARCHAR(254) | Email del titular | Sí |
| `telefono` | VARCHAR(20) | Teléfono de contacto | No |
| `empresa` | VARCHAR(200) | Nombre de empresa | No |
| `descripcion` | TEXT | Detalle de la solicitud | Sí |
| `archivos_adjuntos` | JSONB | Array de {nombre, tipo, tamaño, hash} | No |
| `plazo_bloqueo_vencimiento` | TIMESTAMP | Fecha límite de resolución | Sí |
| `portability_data` | JSONB | Datos estructurados para exportación | No |
| `representante_nombre` | VARCHAR(200) | Nombre del representante | No |
| `representante_rut` | VARCHAR(12) | RUT del representante | No |
| `subsanacion_detalle` | TEXT | Detalle de documentos requeridos | No |
| `subsanacion_fecha_pedido` | DATE | Fecha de solicitud de subsanación | No |
| `prorroga_fecha` | DATE | Fecha de otorgamiento de prorroga | No |
| `prorroga_dias` | INTEGER | Días de ampliación | No |
| `hash_inmutable` | VARCHAR(64) | Hash SHA-256 de integridad | Sí |
| `acuse_enviado_at` | TIMESTAMP | Fecha de envío de acuse | No |
| `plantilla_id` | VARCHAR(20) | Plantilla de respuesta usada | No |
| `observaciones` | TEXT | Fundamento legal de rechazo | No |
| `archivado_en` | TIMESTAMP | Fecha de archivo | No |

### Estados del Ticket
1. ABIERTO - Solicitud recibida, validada
2. EN_PROCESO - Asignada y en evaluación
3. SUBSANACION - Esperando documentación del titular
4. PRORROGA - Plazo ampliado Art. 12 bis
5. RESUELTO - Resolución favorable aplicada
6. RECHAZADO - Rechazada con fundamento
7. CERRADO - Archivado, proceso terminado

---

## 6. SLAS

### Plazos por Tipo de Solicitud

| Derecho | Plazo Base | Ampliación | Total Máximo | Referencia |
|---------|------------|------------|--------------|------------|
| **Acceso** | 10 días hábiles | +10 días (prórroga) | 20 días hábiles | Art. 8 lit. a |
| **Rectificación** | 10 días hábiles | +10 días (prórroga) | 20 días hábiles | Art. 9 |
| **Cancelación** | 10 días hábiles | +10 días (prórroga) | 20 días hábiles | Art. 8 lit. c |
| **Oposición** | 10 días hábiles | +10 días (prórroga) | 20 días hábiles | Art. 13 |
| **Bloqueo** | Inmediato | No aplica | Inmediato | Art. 8 ter |
| **Portabilidad** | 10 días hábiles | +10 días (prórroga) | 20 días hábiles | Art. 12 |

### Plazos de Subprocesos

| Proceso | Plazo | Consecuencia |
|---------|-------|--------------|
| **Subsanación** | 10 días hábiles | Rechazo automático si vence |
| **Rechazo** | Fundamento obligatorio | Sin fundamento no se puede rechazar |
| **Prórroga** | 1 vez por solicitud | Solo aplicable una vez Art. 12 bis |

### Métricas de Cumplimiento
- **Meta cumplimiento SLA:** 100%
- **Umbral de alerta:** 90% cumplimiento mensual
- **Escalamiento:** DPO Senior si >5 tickets en riesgo

---

## 7. RIESGOS

### ARCO-001: Vencimiento de Plazos
**Descripción:** Solicitudes no resueltas dentro del plazo legal  
**Probabilidad:** Media  
**Impacto:** Alto  
**Mitigación:** Monitoreo automático con alertas a 72h, 48h y 24h antes del vencimiento. Regla QW11 de escalamiento automático a DPO Senior.

### ARCO-002: Manipulación de Hashchain
**Descripción:** Alteración de registros históricos de bitácora M1  
**Probabilidad:** Baja  
**Impacto:** Crítico  
**Mitigación:** Hash SHA-256 encadenado con validación criptográfica. Almacenamiento en blockchain inmutable. Verificación de integridad en cada lectura.

### ARCO-003: Exposición de Datos Sensibles
**Descripción:** Datos personales sensibles sin protección adecuada durante exportación  
**Probabilidad:** Media  
**Impacto:** Crítico  
**Mitigación:** Encriptación AES-256 en tránsito y en reposo. Máscara de datos sensibles en logs. Permisos RBAC estricto.

### ARCO-004: Fallo en Notificaciones
**Descripción:** Notificaciones de email no entregadas al titular  
**Probabilidad:** Media  
**Impacto:** Medio  
**Mitigación:** Integración con servicio de email con retry automático (3 intentos). Webhook de confirmación. Registro en bitácora de todos los envíos.

### ARCO-005: Representante Sin Poderes
**Descripción:** Solicitud tramitada por representante sin poder notarial válido  
**Probabilidad:** Baja  
**Impacto:** Alto  
**Mitigación:** Validación obligatoria de poder notarial en campo `representante_rut`. Verificación de firma digital si disponible.

### ARCO-006: Exportación Incompleta
**Descripción:** Datos exportados no incluyen todos los registros del titular  
**Probabilidad:** Baja  
**Impacto:** Alto  
**Mitigación:** Query de validación cruzada contra tabla maestra. Checksum de registros exportados vs almacenados. Prueba de integridad post-exportación.

### ARCO-007: Prórroga Multiple
**Descripción:** Aplicación de más de una prórroga por solicitud (ilegal)  
**Probabilidad:** Muy Baja  
**Impacto:** Alto  
**Mitigación:** Validación de `prorroga_fecha IS NULL` antes de aplicar. Control a nivel de base de datos con constraint único.

### ARCO-008: Subsanación Fuera de Plazo
**Descripción:** Titular responde subsanación pero ya venció el plazo  
**Probabilidad:** Media  
**Impacto:** Medio  
**Mitigación:** Cálculo preciso de días hábiles. Bloqueo de acceptance si `now() > subsanacion_fecha_pedido + 10 días hábiles`.

### ARCO-009: Concurrencia en Asignación
**Descripción:** Mismo ticket asignado a dos DPOs simultáneamente  
**Probabilidad:** Muy Baja  
**Impacto:** Medio  
**Mitigación:** Lock optimista en tabla de asignaciones. Transacción atómica para asignación.

### ARCO-010: Pérdida de Archivos Adjuntos
**Descripción:** Archivos subidos por titular se pierden o corrompen  
**Probabilidad:** Baja  
**Impacto:** Medio  
**Mitigación:** Almacenamiento en S3/ blob storage con redundancia. Hash de verificación en metadata. Backup automático diario.

---

## 8. CONTROLES

| Riesgo | Control | Tipo | Responsable |
|--------|---------|------|-------------|
| ARCO-001 | Sistema de alertas de vencimiento (QW11) | Preventivo | Sistema |
| ARCO-001 | Escalamiento automático a DPO Senior | Detectivo | Sistema |
| ARCO-002 | Algoritmo hash SHA-256 encadenado | Preventivo | Sistema |
| ARCO-002 | Auditoría de acceso a bitácora M1 | Detectivo | DPO |
| ARCO-003 | Encriptación AES-256 datos en reposo | Preventivo | Sistema |
| ARCO-003 | RBAC para acceso a exportaciones | Preventivo | DPO |
| ARCO-004 | Retry automático de notificaciones | Correctivo | Sistema |
| ARCO-004 | Confirmación de lectura de email | Detectivo | Sistema |
| ARCO-005 | Validación de poder notarial | Preventivo | DPO |
| ARCO-006 | Checksum de validación post-export | Correctivo | Sistema |
| ARCO-007 | Constraint en base de datos | Preventivo | Sistema |
| ARCO-008 | Validación de fecha en backend | Preventivo | Sistema |
| ARCO-009 | Lock optimista en transacciones | Preventivo | Sistema |
| ARCO-010 | Almacenamiento redundante S3 | Preventivo | Sistema |
| ARCO-010 | Backup automático diario | Correctivo | Sistema |

---

## 9. KPIS

### KPI-01: Tasa de Resolución en Plazo
**Fórmula:** `(resueltas_en_plazo / total_resueltas) × 100`  
**Meta:** ≥ 95%  
**Frecuencia:** Mensual  
**Umbral de alerta:** < 90%

### KPI-02: Tiempo Promedio de Resolución por Tipo
**Fórmula:** `AVG(días_resolucion)` agrupado por `tipo`  
**Meta:** ≤ 8 días hábiles  
**Frecuencia:** Mensual por tipo

### KPI-03: Tasa de Subsanación
**Fórmula:** `(subsanaciones / total) × 100`  
**Meta:** < 15%  
**Frecuencia:** Mensual  
**Tendencia esperada:** Decreciente

### KPI-04: Tickets Pendientes
**Fórmula:** `COUNT(estado) WHERE estado NOT IN (RESUELTO, RECHAZADO, CERRADO)`  
**Meta:** ≤ 50 activos  
**Umbral de alerta:** > 100

### KPI-05: Cumplimiento SLA
**Fórmula:** `(cumple_plazo / total) × 100`  
**Meta:** 100%  
**Frecuencia:** Mensual  
**Umbral de alerta:** < 95%

### KPI-06: Tasa de Rechazo
**Fórmula:** `(rechazadas / total) × 100`  
**Meta:** < 10%  
**Frecuencia:** Trimestral

### KPI-07: Tiempo de Asignación
**Fórmula:** `AVG(TIMESTAMPDIFF(asignado_en, creado_en))`  
**Meta:** < 2 horas  
**Frecuencia:** Semanal

---

## 10. REGISTRO DE VERSIONES

| Versión | Fecha | Autor | Cambios |
|---------|-------|-------|---------|
| 1.0 | 2026-01-15 | DPO | Creación inicial |
| 2.0 | 2026-06-18 | Architect | Actualización Ley 21.719,新增Portabilidad, mejora de SLAs |

---

*Documento controlado - Uso interno Custodio SaaS*
