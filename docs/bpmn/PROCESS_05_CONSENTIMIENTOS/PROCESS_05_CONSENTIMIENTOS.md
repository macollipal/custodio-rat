# PROCESS 05: Gestión de Consentimientos

## 1. EXPLICACIÓN FUNCIONAL

El proceso de **Gestión de Consentimientos** maneja el ciclo de vida completo del consentimiento del titular de datos personales conforme a la Ley 21.719 (Ley de Protección de Datos Personales de Chile), específicamente los artículos 4 bis y 6.

### Principio Fundamental: FISU

Todo consentimiento debe cumplir con los principios de **FISU** (libre, específico, informado e inequívoco):

- **Libre (Freely Given)**: Sin coerceción, condiciones indebidas o intervención desleal
- **Específico (Specific)**: Por finalidad concreta, no genérico ni abierto
- **Informado (Informed)**: El titular conoce exactamente qué acepta
- **Inequívoco (Unambiguous)**: Acción afirmativa clara, nunca por omisión

### Alcance del Proceso

1. **Obtención**: Diseñar, publicar y capturar consentimiento válido
2. **Registro**: Almacenar con evidencia criptográfica y timestamp
3. **Versionado**: Control de cambios y notificaciones a titulares
4. **Verificación**: Validar conformidad FISU en cada otorgamiento
5. **Revocación**: Gestionar solicitud de revocación y propagar cambios
6. **Actualización RAT**: Mantener el Registro de Actividades de Tratamiento sincronizado

---

## 2. BPMN TEXTUAL DETALLADO

### FASE 1: OBTENCIÓN DEL CONSENTIMIENTO

#### 1.1 Inicio del Proceso
- **Start Event**: "Solicitud de consentimiento requerida"
  - Origen: RAT (nueva actividad requiere consentimiento) o acción directa del titular
  - Trigger: Cuando `RAT.actividad.requiere_consentimiento = true`

#### 1.2 Diseño del Formulario (Lane: DPO)
- **Tarea de Usuario**: "Diseñar formulario consentimiento"
  - Responsable: DPO
  - Campos obligatorios:
    - `finalidad`: Propósito específico del tratamiento
    - `categorias_datos`: Tipos de datos afectados
    - `terceros`: Destinatarios o categorías de terceros
    - `tiempo_retention`: Período de conservación
    - `derecho_retirar`: Cómo ejercer el derecho de revocación

- **Tarea de Usuario**: "Configurar texto información"
  - Responsable: DPO
  - Contenido obligatorio de divulgación completa:
    - Identidad del responsable del tratamiento
    - Finalidad específica del tratamiento
    - Categorías de datos personales
    - Derechos del titular (acceso, rectificación, supresión, oposición, portabilidad)
    - Procedimiento para ejercer derechos
    - Cómo retirar el consentimiento
    - Información sobre transferencias internacionales (si aplica)

#### 1.3 Publicación (Lane: Sistema)
- **Tarea de Sistema**: "Publicar formulario consentimiento"
  - Disponibilizar en aplicación web/móvil
  - Almacenar versión actual del texto
  - Habilitar captura de metadatos

---

### FASE 2: REGISTRO DEL CONSENTIMIENTO

#### 2.1 Revisión por el Titular (Lane: Titular)
- **Tarea de Usuario**: "Titular revisa información"
  - Visualiza texto completo del consentimiento
  - Comprende finalidades y derechos

#### 2.2 Otorgamiento (Lane: Titular)
- **Tarea de Usuario**: "Titular otorga consentimiento"
  - Acción必须是 explícita: checkbox marcado o acción afirmativa clara
  - No se acepta: casillas premarcadas, inacción, silencio
  - Medio de captura: WEB, MÓVIL, PAPEL, VERBAL

#### 2.3 Registro Sistemático (Lane: Sistema)
- **Tarea de Sistema**: "Registrar consentimiento con timestamp"
  - Genera `consent_id` único
  - Almacena:
    - `titular_id`
    - `finalidad`
    - `version`: formato major.minor
    - `fecha_otorgamiento`: timestamp ISO 8601
    - `ip_address`: dirección del titular en momento de otorgamiento
    - `user_agent`: identificador de navegador/aplicación
    - `medio`: WEB | MÓVIL | PAPEL | VERBAL

- **Tarea de Sistema**: "Generar evidencia hash"
  - Crea hash criptográfico de: `consent_text + timestamp + ip_address`
  - Algoritmo: SHA-256 mínimo
  - Almacena `hash_evidencia`

- **Tarea de Sistema**: "Almacenar evidencia en hashchain M1"
  - Inserta en cadena de bloques privada (Merklelike)
  - Incluye referencia al bloque anterior
  - обеспечивает inmutabilidad

- **Tarea de Sistema**: "Actualizar RAT automáticamente"
  - Condición: Si `RAT.actividad.requiere_consentimiento = true`
  - Acción: `RAT.consentimiento_registrado = true`
  - Vincula `consent_id` con `rat_id`

---

### FASE 3: VERIFICACIÓN DE VALIDEZ

#### 3.1 Evaluación (Lane: Sistema)
- **Gateway Exclusivo**: "¿Consentimiento válido?"
  - Criterios de evaluación FISU:
    - `freely_given`: ¿Sin coerceción?
    - `specific`: ¿Finalidad bien definida?
    - `informed`: ¿Texto completo divulgado?
    - `unambiguous`: ¿Acción afirmativa clara?

  - **Rama NO**:
    - **Tarea de Sistema**: "Registrar consentimiento inválido"
      - Estado: `INVALIDO`
      - Motivo de rechazo
    - **Tarea de Sistema**: "Notificar DPO"
      - Alerta sobre consentimiento fallido
      - Requiere intervención manual

  - **Rama SÍ**:
    - Continúa a fase de versionado

---

### FASE 4: VERSIONADO

#### 4.1 Asignación de Versión (Lane: Sistema)
- **Tarea de Sistema**: "Asignar versión"
  - Formato: `major.minor` (ej: 1.0, 1.1, 2.0)
  - Incrementa major: cambios sustanciales en finalidad o categorías
  - Incrementa minor: cambios menores (ej: texto informativo)

#### 4.2 Comparación (Lane: Sistema)
- **Tarea de Sistema**: "Comparar con versión anterior"
  - Recupera versión previa del consentimiento del mismo titular
  - Identifica diferencias textuales y de alcance

#### 4.3 Evaluación de Cambios (Lane: Sistema)
- **Gateway Exclusivo**: "¿Cambios significativos?"
  - Considera: nueva finalidad, nuevas categorías, nuevos terceros

  - **Rama SÍ**:
    - **Tarea de Sistema**: "Notificar titulares con consentimiento previo"
      - Canal: Sistema de Correo
      - Contenido: Descripción de cambios y nueva aceptación requerida
      - Plazo: 30 días para nueva aceptación

  - **Rama NO**:
    - Consentimiento válido mantiene versión actual

---

### FASE 5: GESTIÓN DE REVOCACIÓN

#### 5.1 Inicio por Solicitud del Titular
- **Start Event Intermediate** (Signal): "Titular solicita revocación"
  - Trigger: Mensaje recibido del titular
  - Canal: web, email, teléfono, presencial

#### 5.2 Proceso de Revocación (Lane: Sistema)
- **Tarea de Sistema**: "Registrar solicitud revocación"
  - Almacena: `fecha_revocation`, `motivo` (opcional)
  - Genera timestamp de solicitud

- **Tarea de Sistema**: "Verificar consentimiento existe"
  - Confirma que existe consentimiento activo para esta finalidad
  - Valida que el solicitante es el titular registrado

- **Tarea de Sistema**: "Invalidar consentimiento"
  - Actualiza estado: `ACTIVO` → `REVOGADO`
  - Registra fecha y motivo de revocación

- **Tarea de Sistema**: "Registrar en hashchain M1"
  - Inserta entrada de revocación en cadena de evidencia
  - Mantiene integridad de auditoría

- **Tarea de Sistema**: "Notificar a sistemas dependientes"
  - Identifica todos los sistemas que reciben datos bajo este consentimiento
  - Deshabilita tratamiento basado en este consentimiento
  - Confirma propagación

- **Tarea de Sistema**: "Actualizar RAT"
  - `RAT.consentimiento_activo = false` para esta finalidad
  - Vincula `fecha_revocation` en RAT

- **Tarea de Sistema**: "Enviar confirmación revocation"
  - Canal: Sistema de Correo
  - Destinatario: Titular
  - Contenido: Confirmación de revocación, fecha efectiva, derechos残余

- **End Event**: "Consentimiento revocado"

---

### FASE 6: REVISIÓN PERIÓDICA (12 MESES)

#### 6.1 Timer Intermedio
- **Intermediate Timer Event**: "Revisión consentimiento: 12 meses"
  - Trigger: Cada 12 meses desde otorgamiento
  - Aplica a: Consentimientos activos de larga duración

#### 6.2 Proceso de Renovación (Lane: Sistema)
- **Tarea de Sistema**: "Identificar consentimientos > 12 meses"
  - Consulta base de datos de consentimientos
  - Filtra: `estado = ACTIVO` y `fecha_otorgamiento < fecha_actual - 12 meses`

- **Tarea de Sistema**: "Solicitar renovación"
  - Canal: Sistema de Correo
  - Destinatario: Cada titular afectado
  - Contenido: Recordatorio, enlace para renovar o revocar

#### 6.3 Respuesta del Titular
- **Gateway Exclusivo**: "¿Titular responde?"
  - Espera respuesta durante 30 días

  - **Rama NO** (Silencio):
    - **Tarea de Sistema**: "Registrar como inactivo tras 30 días"
      - Actualiza estado: `ACTIVO` → `INACTIVO`
      - Ejecuta acciones de revocación implícita
    - **Tarea de Sistema**: "Actualizar RAT"
      - `RAT.consentimiento_activo = false`

  - **Rama SÍ**:
    - Regresa a Fase 1: Nueva obtención

---

## 3. TABLA RACI

| Actividad                                      | Titular | DPO | Sistema | Sistema de Correo | RAT |
|------------------------------------------------|:-------:|:---:|:-------:|:-----------------:|:---:|
| Diseñar formulario consentimiento               |    -    | R  |    I    |        -          |  -  |
| Configurar texto información                    |    -    | R  |    C    |        -          |  -  |
| Publicar formulario consentimiento              |    -    | I  |    R    |        -          |  -  |
| Titular revisa información                     |    R    | -  |    I    |        -          |  -  |
| Titular otorga consentimiento                   |    R    | -  |    C    |        -          |  -  |
| Registrar consentimiento con timestamp          |    I    | -  |    R    |        -          |  -  |
| Generar evidencia hash                          |    -    | -  |    R    |        -          |  -  |
| Almacenar evidencia en hashchain M1            |    -    | I  |    R    |        -          |  -  |
| Actualizar RAT automáticamente                 |    -    | I  |    R    |        -          |  C  |
| Verificar consentimiento válido (FISU)          |    -    | I  |    R    |        -          |  -  |
| Registrar consentimiento inválido               |    -    | I  |    R    |        -          |  -  |
| Notificar DPO (consentimiento inválido)         |    -    | R  |    I    |        I          |  -  |
| Asignar versión                                 |    -    | -  |    R    |        -          |  -  |
| Comparar con versión anterior                   |    -    | -  |    R    |        -          |  -  |
| Notificar titulares (cambios significativos)   |    I    | I  |    C    |        R          |  -  |
| Registrar solicitud revocación                 |    I    | -  |    R    |        -          |  -  |
| Verificar consentimiento existe                |    -    | -  |    R    |        -          |  -  |
| Invalidar consentimiento                        |    -    | -  |    R    |        -          |  -  |
| Registrar en hashchain M1 (revocación)         |    -    | I  |    R    |        -          |  -  |
| Notificar a sistemas dependientes               |    -    | I  |    R    |        -          |  -  |
| Actualizar RAT (revocación)                     |    -    | I  |    R    |        -          |  C  |
| Enviar confirmación revocación                 |    I    | -  |    C    |        R          |  -  |
| Identificar consentimientos > 12 meses         |    -    | -  |    R    |        -          |  -  |
| Solicitar renovación                            |    I    | -  |    C    |        R          |  -  |
| Registrar como inactivo tras 30 días           |    I    | I  |    R    |        -          |  -  |

**Leyenda**: R = Responsable, A = Accountable, C = Consultado, I = Informado

---

## 4. EVENTOS

### Start Events
| Evento                          | Tipo              | Descripción                                            |
|--------------------------------|-------------------|--------------------------------------------------------|
| Solicitud de consentimiento     | Start             | RAT requiere nuevo consentimiento o titular lo solicita |
| Solicitud de revocación         | Start Intermediate (Signal) | Titular envía solicitud de revocación              |

### Intermediate Events
| Evento                          | Tipo              | Descripción                                            |
|--------------------------------|-------------------|--------------------------------------------------------|
| Revisión consentimiento: 12 meses | Timer          | Trigger automático para revisión de consentimientos activos |

### End Events
| Evento                          | Tipo              | Descripción                                            |
|--------------------------------|-------------------|--------------------------------------------------------|
| Consentimiento registrado       | End               | Consentimiento válido almacenado con evidencia         |
| Consentimiento revocado        | End               | Revocación completada y propagada                       |

---

## 5. DATOS UTILIZADOS

### Entidades Principales

#### Consentimiento
```
consent_id: UUID (PK)
titular_id: UUID (FK -> Titular)
finalidad: String (descripción específica del tratamiento)
version: String (formato major.minor)
fecha_otorgamiento: DateTime (ISO 8601)
fecha_revocation: DateTime (nullable)
estado: Enum (ACTIVO | REVOGADO | INACTIVO | INVALIDO)
medio: Enum (WEB | MOVIL | PAPEL | VERBAL)
hash_evidencia: String (SHA-256)
ip_address: String (IPv4/IPv6)
user_agent: String
texto_integral: Text (versión completa del consentimiento aceptado)
rat_id_asociado: UUID (FK -> RAT.Actividad)
tiempo_retention: Integer (días)
categorias_datos: Array[String]
terceros: Array[String]
fecha_creacion: DateTime
fecha_actualizacion: DateTime
```

#### FormularioConsentimiento (Data Object)
```
formulario_id: UUID
version: String
campos: Object
  - finalidad: String
  - categorias_datos: Array
  - terceros: Array
  - tiempo_retention: Integer
  - derecho_retirar: String
texto_informacion: Text
fecha_vigencia: Date
```

#### RegistroConsentimiento (Data Object)
```
registro_id: UUID
consent_id: Reference
titular_id: Reference
fecha_registro: DateTime
metadatos: Object
  - ip_address: String
  - user_agent: String
  - medio: String
```

#### EvidenciaHash (Data Object)
```
evidencia_id: UUID
consent_id: Reference
hash: String
algoritmo: String (SHA-256)
timestamp: DateTime
hash_previo: String (referencia en cadena)
```

#### NotificacionRenewal (Data Object)
```
notificacion_id: UUID
titular_id: Reference
consent_id: Reference
fecha_envio: DateTime
tipo: Enum (RENOVACION | REVOCACION_RECORDATORIO)
estado_envio: Enum (ENVIADA | ENTREGADA | FALLIDA)
```

### Flujo de Datos

```
[Titular] --(1)--> [FormularioConsentimiento]
                        |
                        v
[Titular] --(2)--> [RegistroConsentimiento] --> [EvidenciaHash] --> [hashchain M1]
                        |
                        v
                   [RAT] <-- Actualización automática
                        |
                        v
[Sistema de Correo] <-- [NotificacionRenewal]
```

---

## 6. SLAS (Service Level Agreements)

### Requisitos de Calidad del Consentimiento

| ID    | Indicador                                          | Target      | Medición                    |
|-------|----------------------------------------------------|-------------|-----------------------------|
| SLA-1 | Consentimiento granular por finalidad             | 100%        | Verificar que cada finalidad tiene consentimiento separado |
| SLA-2 | Texto de información completo (Art. 4 bis)         | 100%        | Checklist de elementos obligatorios |
| SLA-3 | Acción afirmativa explícita documentada           | 100%        | Evidencia de checkbox o botón |
| SLA-4 | Metadatos completos (IP, timestamp, user_agent)   | 100%        | Todos los registros tienen campos completos |
| SLA-5 | Hash de evidencia generado                          | 100%        | Todos los consentimientos tienen hash |
| SLA-6 | Inserción en hashchain                              | 100%        | Todos los hashes insertados en cadena |

### Requisitos de Revocación

| ID    | Indicador                                          | Target      | Medición                    |
|-------|----------------------------------------------------|-------------|-----------------------------|
| SLA-7 | Revocación tan fácil como otorgamiento             | ≤ 2 clicks  | Métrica de UX               |
| SLA-8 | Tiempo de procesamiento de revocación              | ≤ 24 horas  | Desde solicitud hasta confirmación |
| SLA-9 | Notificación a sistemas dependientes               | ≤ 24 horas  | Desde invalidación hasta notificación |
| SLA-10| Actualización RAT tras revocación                  | ≤ 1 hora    | Desde invalidación hasta actualización |

### Requisitos de Renovación

| ID    | Indicador                                          | Target      | Medición                    |
|-------|----------------------------------------------------|-------------|-----------------------------|
| SLA-11| Renovación requerida cada 12 meses                 | 100%        | Consentimientos activos > 12 meses tienen notificación |
| SLA-12| Plazo de gracia para renovación                    | 30 días     | Tiempo entre notificación y expiración |
| SLA-13| Consentimientos expirados marcados inactivos        | ≤ 24 horas  | Desde fin plazo hasta cambio de estado |

### Requisitos de Conservación

| ID    | Indicador                                          | Target      | Medición                    |
|-------|----------------------------------------------------|-------------|-----------------------------|
| SLA-14| Conservación de evidencia tras revocación          | ≥ 3 años    | Fecha revocation + 3 años ≤ fecha eliminación |
| SLA-15| Integridad de hashchain verificada                 | 100%        | Verificación periódica de cadena |

---

## 7. RIESGOS

### Categoría:CONS - Consentimiento

| ID       | Riesgo                                            | Probabilidad | Impacto | Mitigación Control                              |
|----------|---------------------------------------------------|:------------:|:-------:|--------------------------------------------------|
| CONS-001 | Consentimiento no granular (finalidades mezcladas) | Media        | Alto    | FORMLY-001: Validación de formulario granular    |
| CONS-002 | Texto de información incompleto                   | Baja         | Alto    | CHECKLIST-001: Checklist Art. 4 bis obligatorio |
| CONS-003 | Evidencias insuficientes para probar consentimiento | Media     | Alto    | HASH-001: Generación automática de hash          |
| CONS-004 | Hashchain alterado o manipulado                   | Baja         | Crítico | CHAIN-001: Verificación criptográfica periódica   |
| CONS-005 | Revocación no propagada a sistemas dependientes   | Media         | Alto    | PROPAGA-001: Workflow de notificación obligatorio |
| CONS-006 | Silencio tratado como consentimiento (opt-out)    | Baja         | Crítico | UX-001: Solo acción afirmativa acepta           |
| CONS-007 | RAT no actualizado tras cambio de consentimiento  | Media         | Medio   | AUTO-001: Actualización automática en flujo      |
| CONS-008 | Versionado incorrecto de consentimientos         | Media         | Medio   | VER-001: Control de versiones por finalidad      |
| CONS-009 | Renovación no solicitada a tiempo                 | Media         | Alto    | TIMER-001: Job programado 30 días antes          |
| CONS-010 | Datos retenidos tras revocación válida            | Baja         | Crítico | PURGE-001: Verificación de eliminación en sistemas|
| CONS-011 | Consentimiento obtenido bajo presión/coerción    | Baja         | Crítico | FISU-001: Verificación de libertad de otorgamiento |
| CONS-012 | Falta de capacidad del titular para consentir      | Baja         | Alto    | CAPACITY-001: Verificación de edad/capacidad     |

---

## 8. CONTROLES Y KPIS

### Controles de Prevención

| Control      | Descripción                                                           | Automatizado |
|--------------|-----------------------------------------------------------------------|:------------:|
| FORMLY-001   | Validar que formulario tenga campos obligatorios completos            | Sí           |
| CHECKLIST-001| Verificar elementos Art. 4 bis en texto de información                | Sí           |
| UX-001       | Bloquear envío si checkbox no está marcado                           | Sí           |
| FISU-001     | Registrar contexto de otorgamiento ( IP, user_agent, timestamp)       | Sí           |
| CAPACITY-001 | Verificar mayoría de edad antes de consentir                          | Sí           |

### Controles de Detección

| Control      | Descripción                                                           | Frecuencia    |
|--------------|-----------------------------------------------------------------------|---------------|
| CHAIN-001    | Verificar integridad de hashchain mediante prueba de consistencia    | Mensual       |
| HASH-001     | Validar que todos los consentimientos tienen hash válido              | Diaria        |
| RAT-001      | Detectar inconsistencias entre RAT y consentimientos activas          | Semanal       |

### Controles de Corrección

| Control      | Descripción                                                           | SLA           |
|--------------|-----------------------------------------------------------------------|---------------|
| PROPAGA-001  | Workflow de revocación con notificación a todos los sistemas          | 24 horas      |
| PURGE-001    | Proceso de eliminación de datos tras revocación                        | 30 días       |

---

### KPIs (Key Performance Indicators)

#### KPI de Efectividad

| KPI                                    | Definición                                                    | Target   |
|----------------------------------------|---------------------------------------------------------------|----------|
| Tasa_consentimientos_activos           | (Consentimientos activos / Total consentimientos) × 100      | > 85%    |
| Tasa_consentimientos_validos           | (Consentimientos válidos / Total otorgados) × 100            | = 100%   |
| Tasa_revogacion                        | (Revocaciones / Total activos inicio período) × 100          | < 15%    |

#### KPI de Eficiencia

| KPI                                    | Definición                                                    | Target   |
|----------------------------------------|---------------------------------------------------------------|----------|
| Tiempo_medio_otorgamiento              | Tiempo promedio desde acceso a formulario hasta aceptación    | < 5 min  |
| Tiempo_procesamiento_revogacion        | Tiempo desde solicitud hasta confirmación final              | < 24 hrs |
| Tasa_notificaciones_entregadas         | (Notificaciones entregadas / Enviadas) × 100                 | > 95%   |

#### KPI de Cumplimiento

| KPI                                    | Definición                                                    | Target   |
|----------------------------------------|---------------------------------------------------------------|----------|
| Consentimientos_pendientes_renovacion  | Número de consentimientos activos > 12 meses sin renovar      | 0        |
| RAT_actualizados_vs_consentimientos    | (RAT actualizado / Consentimientos activos que afectan RAT)   | = 100%   |
| Cobertura_hashchain                    | (Consentimientos en hashchain / Total consentimientos) × 100  | = 100%   |

#### KPI de Calidad de Datos

| KPI                                    | Definición                                                    | Target   |
|----------------------------------------|---------------------------------------------------------------|----------|
| Completitud_metadatos                  | (Campos obligatorios completos / Total registros) × 100      | = 100%   |
| Integridad_hashchain                   | (Bloques verificados OK / Total bloques) × 100               | = 100%   |

---

## ANEXO: Referencia Normativa

### Ley 21.719 - Artículo 4 bis
> "El tratamiento de datos personales requiere el consentimiento libre, específico, informado e inequívoco del titular..."

### Ley 21.719 - Artículo 6
> "El consentimiento debe ser obtenido por medios que permitan dejar constancia..."

### Referencias
- Ley 21.719 (Chile): Protección de datos personales
- GDPR Art. 7 (referencia comparativa)
- ISO 27701:2019 - Privacy information management
