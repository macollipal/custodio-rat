# PROCESO 07: MAPA MAESTRO DE CUMPLIMIENTO (Master Compliance Map)

**Plataforma:** Custodio SaaS  
**Versión:** 1.0  
**Fecha:** 2026-06-18  
**Clasificación:** Público  
**Fundamento Legal:** Art. 30 GDPR / Art. 11 Ley 21.719 Chile

---

## 1. EXPLICACIÓN FUNCIONAL

El Mapa Maestro de Cumplimiento es el proceso de orquestación central que actúa como el sistema nervioso de la plataforma Custodio, conectando los seis módulos de gestión de privacidad en una vista unificada de compliance enterprise.

### Propósito del Proceso

Este proceso no es un módulo más de gestión de datos, sino el **director de orquesta** que orquesta, supervisa y gobierna la interacción entre todos los procesos de privacy management de la organización. Su objetivo es proporcionar una visión holística del estado de cumplimiento y coordinar respuestas ante eventos regulatorios.

### Las 5 Dimensiones de Orquestación

| Dimensión | Descripción | Módulo Vinculado |
|-----------|-------------|------------------|
| **Datos Maestros** | RAT es la fuente de verdad para todas las actividades de tratamiento. Cada tratamiento debe estar documentado, evaluado y aprobado. | RAT |
| **Gestión de Riesgos** | EIPD se dispara automáticamente desde RAT cuando el riesgo inherente es ALTO, alimentando el registro central de riesgos. | EIPD |
| **Derechos ARCO** | Cada solicitud ARCO se vincula a RAT para identificar qué tratamientos pueden verse afectados y verificar base legal vigente. | ARCO |
| **Incidentes (Brechas)** | Las brechas referencian RAT para identificar actividades afectadas y pueden disparar evaluaciones EIPD o revisiones ARCO. | Brechas |
| **Consentimientos** | Los consentimientos actualizan automáticamente el RAT cuando cambian de estado, manteniendo la base legal sincronizada. | Consent |

### Beneficios del Enfoque Maestro

1. **Visibilidad Total:** Dashboard unificado con compliance score global
2. **Coordinación Automática:** Los procesos se comunican sin intervención manual
3. **Regulatory Reporting:** Generación automática de informes regulatorios
4. **Escalación Gobernanza:** Alertas automáticas cuando el score cae bajo el umbral
5. **Auditoría Unificada:** Paquete de evidencias consolidadas para auditoría externa

---

## 2. BPMN TEXTUAL DETALLADO (Master Orchestration)

### INITIALIZATION / REGULATORY SETUP

**Inicio:** "Custodio Platform inicializado" (deploy en producción)

**Tarea: Cargar configuración regulatory Chile** (Lane: Sistema)  
Carga configuración regulatoria específica para Chile:
- Ley 21.719 (nueva ley chilena de protección de datos)
- GDPR como marco supletorio (Art. 4 Ley 21.719)
- Resoluciones y guías de la APDP (Autoridad de Protección de Datos Personales)
- Plazos y sanciones aplicables

**Tarea: Inicializar dashboard compliance** (Lane: Sistema)  
Configura el dashboard de cumplimiento:
- KPIs maeestros configurados
- Compliance score inicial = 0%
- Alertas configuradas

**Tarea: Configurar calendario regulatorio** (Lane: Sistema)  
Configura las fechas límite del año:
- Vencimiento de RAT reviews (12 meses)
- Renovación de contratos con encargados
- Fechas de submission de informes APDP
- Auditorías programadas

---

### POOL 1 - RAT (AS SUB-PROCESS)

**Call Activity: RAT - Registro de Actividades de Tratamiento**

El proceso RAT se嵌入 como sub-proceso colapsado:

- **Trigger:** "Crear/actualizar actividad de tratamiento"
- **Entrada:** Datos básicos del tratamiento (nombre, finalidad, categorías)
- **Salida:** "RAT activo con EIPD si corresponde"
- **Datos:** rat_id, nivel_riesgo_inherente, base_legal, estado

---

### POOL 2 - EIPD (AS SUB-PROCESS)

**Call Activity: EIPD - Evaluación de Impacto en Protección de Datos**

El proceso EIPD se嵌入 como sub-proceso colapsado:

- **Trigger:** "RAT evalúa riesgo = ALTO"
- **Entrada:** rat_id, evaluación_riesgo, categorías_datos
- **Salida:** "EIPD aprobado"
- **Datos:** eipd_id, nivel_riesgo_residual, medidas_aprobadas

---

### POOL 3 - ARCO (AS SUB-PROCESS)

**Call Activity: ARCO - Gestión de Derechos ARCO**

El proceso ARCO se嵌入 como sub-proceso colapsado:

- **Trigger:** "Titular ejerce derecho ARCO"
- **Entrada:** tipo_derecho, titular_id, empresa_id
- **Salida:** "Solicitud ARCO resuelta"
- **Link to:** RAT (identificar tratamiento afectado)
- **Link to:** Encargados (si aplica para notificación)
- **Datos:** ticket_arco_id, tratamiento_afectado, estado_solicitud

---

### POOL 4 - BRECHAS (AS SUB-PROCESS)

**Call Activity: Brechas - Gestión de Incidentes de Seguridad**

El proceso Brechas se嵌入 como sub-proceso colapsado:

- **Trigger:** "Brecha detectada"
- **Entrada:** datos_afectados, categorias_incidente, severidad
- **Salida:** "Brecha cerrada"
- **Link to:** RAT (actividad afectada)
- **Link to:** ARCO (posibles derechos afectados de titulares)
- **Link to:** EIPD (nueva evaluación si cambia el perfil de riesgo)
- **Datos:** brecha_id, actividades_afectadas, notificaciones_enviadas

---

### POOL 5 - CONSENTIMIENTOS (AS SUB-PROCESS)

**Call Activity: Consentimientos - Gestión de Consentimientos**

El proceso Consentimientos se嵌入 como sub-proceso colapsado:

- **Trigger:** "Consentimiento requerido"
- **Entrada:** finalidad, categorias_datos, mecanismo
- **Salida:** "Consentimiento registrado/válido"
- **Link to:** RAT (actualizar base legal = consentimiento)
- **Datos:** consent_id, version, estado, fecha_expiracion

---

### POOL 6 - ENCARGADOS (AS SUB-PROCESS)

**Call Activity: Encargados - Gestión de Encargados de Tratamiento**

El proceso Encargados se嵌入 como sub-proceso colapsado:

- **Trigger:** "Nueva relación/renovación/terminación"
- **Entrada:** encargado_id, servicios, datos_compartidos
- **Salida:** "Encargado activo/terminado"
- **Link to:** RAT (asociar a actividades)
- **Datos:** encargado_id, contrato_id, estado_contrato, actividades_vinculadas

---

### CENTRAL ORCHESTRATION GATEWAY

**Parallel Gateway: Validación de estado global**

El sistema realiza verificaciones paralelas del estado de todos los procesos:

**Branch 1 - Verificar estado RAT:**
- TareaSistema: "Verificar estado RAT"
- Métricas: count activos, pendientes, vencidos
- Alerta si: vencidos > 0

**Branch 2 - Verificar EIPDs vigentes:**
- TareaSistema: "Verificar EIPDs vigentes"
- Métricas: count approved, pending, expired
- Alerta si: expired > 0 o pending > umbral

**Branch 3 - Verificar ARCO pendientes:**
- TareaSistema: "Verificar ARCO pendientes"
- Métricas: count SLA at risk
- Alerta si: SLA_at_risk > 0

**Branch 4 - Verificar consentimientos:**
- TareaSistema: "Verificar consentimientos"
- Métricas: count activos, revocados, pending renewal
- Alerta si: pending_renewal > umbral

**Branch 5 - Verificar encargos vigentes:**
- TareaSistema: "Verificar encargos vigentes"
- Métricas: count vigentes, near expiry
- Alerta si: near_expiry > 0

**Branch 6 - Verificar brechas abiertas:**
- TareaSistema: "Verificar brechas abiertas"
- Métricas: count open, critical
- Alerta si: critical > 0

**Parallel Gateway: Reunir métricas**

**TareaSistema: Calcular compliance score global** (Lane: Sistema)  
Fórmula ponderada (ver sección 5):
- Ponderación por dimensión
- Score final entre 0-100%

---

### REGULATORY REPORTING

**TareaSistema: Generar informe regulatorio APDP** (Lane: Sistema)  
Genera informe anual según Art. 48 GDPR equivalente:
- Resumen de actividades de tratamiento
- EIPDs ejecutadas
- Incidentes reportados
- Medidas implementadas
- Cambios organizativos

**TareaUsuario: Revisar y aprobar informe APDP** (Lane: DPO Senior)  
- Revisión detallada del informe
- Correcciones si necesario
- Aprobación formal

**TareaSistema: Enviar a APDP** (Lane: Sistema)  
- Envío por canal oficial requerido
- Recibo de confirmación
- Registro de submission

**TareaSistema: Archivar evidencia submission** (Lane: Sistema)  
- PDF del informe enviado
- Comprobante de envío APDP
- Timestamp de submission

---

### AUDITORÍA EXTERNA

**Intermediate Start: "Solicitud auditoría recibida"** (mensaje: autoridade)  
Evento de mensaje recibido de autoridad competente:
- Identificación del organismo auditor
- Alcance de la auditoría
- Documentos requeridos

**TareaUsuario: Preparar documentación auditoría** (Lane: DPO)  
- Compilar documentación según alcance
- Verificar completitud
- Organizar evidencias

**TareaSistema: Generar package de evidencias** (Lane: Sistema)  
Pull automático desde todos los procesos:
- RAT activos y histórico
- EIPDs aprobadas
- Tickets ARCO resueltos
- Registro de brechas
- Consentimientos vigentes
- Contratos de encargados

**TareaUsuario: Auditoría in situ / documentary** (Lane: Auditor)  
- Auditoría presencial o documental
- Revisión de evidencias
- Entrevistas con personal

**TareaSistema: Registrar hallazgos auditoría** (Lane: Sistema)  
- Clasificar hallazgos (crítico, mayor, menor)
- Registrar no conformidades
- Documentar observaciones

**GatewayExclusivo: "¿Hallazgos críticos?"**

- **Sí:** TareaSistema "Crear plan acción correctiva"
  - Definir acciones correctivas
  - Asignar responsables
  - Establecer plazos
- **No:** Continuar

**TareaSistema: Registrar resultado auditoría** (Lane: Sistema)  
- Resultado final (conforme/no conforme)
- Archivo de informe de auditoría
- Actualización de métricas

**End: "Auditoría concluida"**

---

### ANNUAL REVIEW CYCLE

**Intermediate Timer Event: "Revisión anual integral"** (12 meses)  
Timer que dispara revisión completa de todo el sistema

**TareaUsuario: Revisar todos los RAT** (Lane: DPO)  
- Verificar que cada RAT esté vigente
- Identificar tratamientos que ya no existen
- Actualizar RATs con cambios

**TareaUsuario: Revisar cumplimiento EIPDs** (Lane: DPO)  
- Verificar EIPDs vigentes
- Identificar que requieren renovación
- Actualizar medidas si necesario

**TareaUsuario: Evaluar cambios regulatorios** (Lane: DPO Senior)  
- Nuevas leyes o reglamentos
- Guías emitidas por APDP
- Cambios en jurisprudencia
- Actualizar configuración si necesario

**TareaSistema: Actualizar plataforma si necesario** (Lane: Sistema)  
- Aplicar actualizaciones de configuración
- Modificar flujos si hay cambios regulatorios
- Notificar a usuarios de cambios

**TareaSistema: Generar informe anual compliance** (Lane: Sistema)  
Genera PDF para directorio:
- Resumen ejecutivo
- Compliance score del año
- Principales incidentes
- Inversiones en privacy
- Objetivos para próximo año

---

### GOVERNANCE ESCALATION

**GatewayExclusivo: "¿Compliance score < umbral?"**  
Umbral: 80%

- **Sí → Notificar a dirección** (TareaSistema - Lane: Sistema de Correo)
  - Alerta automática a gerencia
  - Incluye métricas detalladas
  - Identificación de áreas problema

- **Sesión extraordinaria de compliance** (TareaUsuario - Lane: Comité: DPO, Legal, Risk, CEO)
  - Reunión de crisis
  - Análisis de situación
  - Decisiones inmediatas

- **Elaborar plan de mejora** (TareaUsuario - Lane: DPO)
  - Definir acciones correctivas
  - Asignar recursos
  - Establecer timeline

- **TareaSistema: Monitorear implementación plan**
  - Tracking de acciones
  - Reporting automático
  - Verificación de eficacia

- **No → Continuar operación normal**

---

### END STATES

**End: "Plataforma en operación compliant"**  
Estado ideal: todas las métricas dentro de umbrales, score >= 80%

**End: "Incidente de no-compliance en curso"**  
Estado de alerta: score < 80% o incidente crítico abierto

---

## 3. INTERCONEXIONES ENTRE PROCESOS

### Tabla Maestra de Interconexiones

| Proceso A | Evento/Tarea A | Proceso B | Evento/Tarea B | Tipo | Datos Compartidos |
|-----------|---------------|-----------|---------------|------|-------------------|
| RAT | EIPD requerida | EIPD | Iniciar evaluación | Trigger | rat_id, riesgo_inherente |
| RAT | Actividad con consent | Consent | Solicitar consentimiento | Link | finalidad, categorias_datos |
| RAT | Crear/actualizar | Encargados | Vincular encargado | Link | actividades, categorias |
| RAT | Tratamiento afectado | Brechas | Reportar brecha | Link | actividad_id, datos_afectados |
| EIPD | Aprobado | RAT | Actualizar estado | Update | eipd_id, nivel_riesgo_residual |
| EIPD | Rechazado | RAT | Mantener en elaboración | Update | comentarios_rechazo |
| ARCO | Solicitud recibida | RAT | Identificar tratamiento | Link | empresa_id, tipo_solicitud |
| ARCO | Resuelto | RAT | Verificar base legal | Check | base_legal_actual |
| Brechas | Cerrada | EIPD | ¿Evaluar nuevo riesgo? | Decision | riesgo_actualizado |
| Brechas | Notificación titulares | ARCO | ¿Derechos afectados? | Decision | categorias_datos |
| Consent | Activo | RAT | Base legal = consentimiento | Update | consent_id, version |
| Consent | Revocado | RAT | ¿Otra base legal? | Decision | finalidad_tratamiento |
| Encargados | Nuevo contrato | RAT | Vincular a actividades | Update | encargado_id, contrato_id |
| Encargados | Terminado | RAT | Desvincular | Update | actividades_afectadas |
| Encargados | Incidente | Brechas | ¿Notificar brecha? | Decision | tipo_incidente |

### Flujos de Mensaje entre Procesos

| De Proceso | A Proceso | Mensaje | Contenido |
|------------|-----------|---------|-----------|
| RAT | EIPD | EIPD_requerida | rat_id, riesgo, categorías |
| RAT | Consent | Solicitar_consentimiento | finalidad, datos, mecanismo |
| RAT | Encargados | Vincular_encargado | actividades, servicios |
| Brechas | RAT | Tratamiento_afectado | actividad_id, impacto |
| EIPD | RAT | EIPD_aprobada | eipd_id, medidas |
| Consent | RAT | Base_legal_actualizada | consent_id, estado |
| Encargados | RAT | Actividades_actualizadas | encargado_id, vinculaciones |
| Master | All | Solicitud_metricas | tipo, periodo |
| All | Master | Respuesta_metricas | KPIs, score |

---

## 4. DIAGRAMA DE FLUJOS DE DATOS

### Flujo 1: RAT → EIPD (Actividad con riesgo alto)

```
[RAT] ──(riesgo=ALTO)──▶ [EIPD]
  │                         │
  │ rat_id                  │ eipd_id
  │ riesgo_inherente        │ nivel_riesgo_residual
  │ categorías_datos        │ medidas_aprobadas
  │ finalidad               │ fecha_aprobacion
```

### Flujo 2: RAT ↔ Consent (Base legal = consentimiento)

```
[RAT] ──(solicitar)──▶ [Consent]
  │◀──(actualizar)──┘
  │                         
  │ consent_id
  │ estado (activo/revocado)
  │ version
  │ fecha_expiracion
```

### Flujo 3: Brechas → RAT + ARCO (Impacto en tratamientos y derechos)

```
[Brechas] ──(afectar)──▶ [RAT]
    │                         
    └──(notificar)──▶ [ARCO]
                          │
                          ▼
                    ¿Derechos afectados?
                          │
                          ▼
                    Notificar titulares
```

### Flujo 4: Encargados → RAT (Vincular encargos a actividades)

```
[Encargados] ──(vincular)──▶ [RAT]
     │
     └──(actualizar)──▶ [Contratos]
                              │
                              ▼
                        Encargado activo
                        con actividades vinculadas
```

### Flujo 5: All → Dashboard (Métricas de compliance)

```
[RAT] ──────────┐
[EIPD] ─────────┼──▶ [Dashboard Master]
[ARCO] ─────────┼──▶ [Compliance Score]
[Brechas] ──────┼──▶ [KPIs Globales]
[Consent] ──────┼──▶ [Regulatory Calendar]
[Encargados] ───┘
```

---

## 5. COMPLIANCE SCORE MODEL

### Fórmula de Cálculo

```
Compliance_Score = 
  (RAT_activos / RAT_total × 0.15)
+ (EIPDs_vigentes / EIPDs_requeridas × 0.15)
+ (ARCO_plazo / ARCO_total × 0.20)
+ (Consent_activos / Consent_requeridos × 0.15)
+ (Encargos_vigentes / Encargos_total × 0.15)
+ ((100 - Brechas_criticas × 10) × 0.20)
```

### Ponderaciones

| Componente | Ponderación | Justificación |
|------------|-------------|---------------|
| RAT | 15% | Base del sistema, documentación obligatoria |
| EIPD | 15% | Crítico para riesgos altos, requerimiento legal |
| ARCO | 20% | Mayor impacto en derechos de titulares |
| Consent | 15% | Base legal fundamental |
| Encargados | 15% | Responsabilidad contractual |
| Brechas | 20% | Indicador de incidentes críticos |

### Umbrales

| Score | Estado | Acción |
|-------|--------|--------|
| >= 90% | Excelente | Operación normal, continue monitoring |
| 80-89% | Aceptable | Operación normal, revisar áreas de mejora |
| 70-79% | Atención | Plan de mejora recomendado |
| < 70% | Crítico | Sesión extraordinaria obligatoria |
| < 50% | Emergencia | Escalación a CEO, parada de tratamientos no esenciales |

### Ejemplo de Cálculo

```
Supongamos:
- RAT: 8 activos / 10 total = 0.80 × 0.15 = 0.12
- EIPD: 3 vigentes / 3 requeridas = 1.0 × 0.15 = 0.15
- ARCO: 18 en plazo / 20 total = 0.90 × 0.20 = 0.18
- Consent: 5 activos / 5 requeridos = 1.0 × 0.15 = 0.15
- Encargados: 4 vigentes / 5 total = 0.80 × 0.15 = 0.12
- Brechas: 0 críticas = (100 - 0) × 0.20 = 0.20

Compliance_Score = 0.12 + 0.15 + 0.18 + 0.15 + 0.12 + 0.20 = 0.92 = 92%
```

---

## 6. RACI MATRIX FOR MASTER PROCESS

| Actividad | DPO | DPO Senior | Sistema | Comité | Auditor | APDP |
|-----------|-----|------------|---------|--------|---------|------|
| Cargar configuración regulatory | I | A | R | - | - | C |
| Inicializar dashboard | I | A | R | - | - | - |
| Configurar calendario regulatorio | C | A | R | - | - | - |
| Verificar estado RAT | I | I | R | - | - | - |
| Verificar EIPDs vigentes | I | I | R | - | - | - |
| Verificar ARCO pendientes | I | I | R | - | - | - |
| Verificar consentimientos | I | I | R | - | - | - |
| Verificar encargos vigentes | I | I | R | - | - | - |
| Verificar brechas abiertas | I | I | R | - | - | - |
| Calcular compliance score | I | I | R | - | - | - |
| Generar informe APDP | C | A | R | I | - | - |
| Revisar informe APDP | I | R/A | C | - | - | - |
| Enviar a APDP | I | A | R | - | - | C |
| Preparar documentación auditoría | R | C | C | - | I | - |
| Generar package evidencias | I | I | R | - | - | - |
| Participar en auditoría | I | C | C | I | R | - |
| Registrar hallazgos | I | C | R | - | C | - |
| Crear plan acción correctiva | R | A | C | C | - | - |
| Revisión anual integral | R | A | C | I | - | - |
| Evaluar cambios regulatorios | C | R/A | C | I | - | C |
| Actualizar plataforma | I | A | R | - | - | - |
| Generar informe anual | I | A | R | I | - | - |
| Notificar a dirección (score bajo) | I | I | R | - | - | - |
| Sesión extraordinaria | C | R | C | R/A | - | - |
| Elaborar plan de mejora | R | A | C | C | - | - |
| Monitorear implementación | I | C | R | - | - | - |

**Leyenda:** R=Responsable, A=Autoriza, C=Consultado, I=Informado

---

## 7. KPIs GLOBALES

| KPI | Definición | Meta | Frecuencia | Sentido |
|-----|-----------|------|------------|---------|
| Compliance Score | Fórmula ponderada en sección 5 | >= 90% | Mensual | ↑ Mejor |
| RAT coverage | RAT activos / actividades reales documentadas | 100% | Trimestral | ↑ Mejor |
| EIPD coverage | EIPDs aprobadas / EIPDs requeridas (riesgo ALTO) | 100% | Mensual | = 100% |
| ARCO SLA compliance | Solicitudes ARCO resueltas en plazo / total | >= 95% | Mensual | ↑ Mejor |
| Consent coverage | Consentimientos activos / consentimientos requeridos | 100% | Mensual | = 100% |
| Encargos compliance | Encargos con contrato vigente / total encargos | 100% | Mensual | = 100% |
| Brechas managed | Brechas cerradas / total brechas reportadas | 100% | Por evento | = 100% |
| Training compliance | DPOs con formación actualizada / total DPOs | 100% | Anual | = 100% |
| Tiempo respuesta ARCO | Promedio días desde solicitud hasta resolución | <= 10 días | Mensual | ↓ Mejor |
| Score trend | Variación del compliance score mes a mes | >= 0 | Mensual | ↑ Mejor |
| RAT vencidos | RAT sin revisión en 12 meses | 0 | Mensual | = 0 |
| EIPDs pendientes | EIPDs en curso hace más de 60 días | 0 | Mensual | = 0 |
| Brechas críticas abiertas | Brechas con severidad CRÍTICA sin cerrar | 0 | Semanal | = 0 |
| Informe APDP timely | Informe anual enviado antes del 31-mar | 100% | Anual | = 100% |

---

## 8. REGULATORY CALENDAR

### Calendario Anual de Cumplimiento

| Mes | Actividad | Proceso | Deadline | Responsable |
|-----|-----------|---------|----------|-------------|
| Enero | Renovación consentimientos anuales | Consent | 31-ene | DPO + Sistema |
| Enero | Revisión inicial estado compliance | Master | 15-ene | DPO Senior |
| Febrero | Preparación informe APDP | Master | 28-feb | DPO |
| Marzo | **Envío informe anual APDP** | Master | **31-mar** | DPO Senior |
| Abril | Revisión RAT tratamientos grandes volúmenes | RAT | 30-abr | DPO |
| Abril | Verificación EIPDs activas | EIPD | 30-abr | DPO |
| Mayo | Auditoría interna de compliance | Master | 15-may | DPO + Comité |
| Junio | Renovación contratos encargados | Encargados | 30-jun | DPO + Legal |
| Julio | Auditoría interna documentación | Master | 15-jul | DPO |
| Agosto | Revisión políticas de privacidad | Master | 31-ago | DPO Senior |
| Septiembre | Revisión EIPDs activos | EIPD | 30-sep | DPO |
| Octubre | Preparación presupuesto compliance | Master | 31-oct | DPO Senior + Comité |
| Noviembre | Planificación próximo año | Master | 30-nov | DPO Senior + Comité |
| Diciembre | **Cierre annual compliance** | Master | **15-dic** | DPO Senior |
| Diciembre | Renovación certificaciones equipo DPO | Master | 31-dic | DPO Senior |

### Hitos Críticos

| Hito | Fecha Límite | Consecuencia Incumplimiento |
|------|--------------|---------------------------|
| Informe APDP | 31-mar | Multa hasta 15M CLP, posible auditoría |
| Renovación consentimientos | 31-ene | Base legal inválida, tratamientos no conformes |
| Revisión EIPDs | 30-sep | EIPDs pueden estar desactualizadas |
| Cierre annual | 15-dic | Incumplimiento de governance |

---

## 9. ANEXO: Mapeo de Procesos a Artefactos

| Proceso | Archivo BPMN | Descripción |
|---------|--------------|-------------|
| RAT | PROCESS_01_RAT.bpmn | Registro de Actividades de Tratamiento |
| EIPD | PROCESS_04_EIPD.bpmn | Evaluación de Impacto en Protección de Datos |
| ARCO | PROCESS_02_ARCO.bpmn | Gestión de Derechos ARCO |
| Brechas | PROCESS_03_BRECHAS.bpmn | Gestión de Incidentes de Seguridad |
| Consent | PROCESS_05_CONSENTIMIENTOS.bpmn | Gestión de Consentimientos |
| Encargados | PROCESS_06_ENCARGADOS.bpmn | Gestión de Encargados de Tratamiento |
| Master | PROCESS_07_MAPA_MAESTRO.bpmn | Orquestación y Vista Unificada |

---

**Documento generado por:** Custodio Platform  
**Fecha generación:** 2026-06-18  
**Versión documento:** 1.0