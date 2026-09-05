# PROCESS 03: Brechas de Seguridad
## Custodio SaaS Platform - Gestión de Brechas según Art. 26 Ley 21.719

---

## 1. EXPLICACIÓN FUNCIONAL

Este proceso maneja la gestión de brechas de seguridad de datos personales conforme al **Art. 26 Ley 21.719** (Ley de Protección de Datos Personales de Chile).

### Objetivo
Establecer el procedimiento operacional para la detección, clasificación, evaluación, notificación y remediación de brechas de seguridad que afecten a datos personales tratados por Custodio SaaS Platform.

### Requisitos Clave

| Requisito | Descripción | Base Legal |
|-----------|-------------|------------|
| Detección y registro | Identificar y documentar toda brecha de seguridad | Art. 26.1 |
| Clasificación de severidad | Categorizar según impacto: CONFIDENCIALIDAD, INTEGRIDAD, DISPONIBILIDAD | Art. 26.1 |
| Evaluación de impacto | Analizar consecuencias para derechos de titulares | Art. 26.2 |
| Notificación a APDC | Informar a la Agencia en máximo 72 horas | Art. 26.3 |
| Notificación a titulares | Comunicar a afectados cuando exista riesgo | Art. 26.4 |
| Plan de remediación | Documentar medidas correctivas y preventivas | Art. 26.5 |
| Evidencias e inmutabilidad | Mantener trazabilidad mediante hashchain | Art. 26.6 |

### Flujo Principal

```
Detección → Clasificación → Evaluación → Comité → Decisión → Notificación → Remediación → Cierre
```

---

## 2. BPMN TEXTUAL DETALLADO

### FASE 1 - DETECCIÓN Y REGISTRO

| Elemento | Descripción | Lane |
|----------|-------------|------|
| Start Event | **Brecha detectada** (mensaje interno o externo) | - |
| TareaUsuario | **Reportar brecha** - Formulario con: descripcion, fecha_deteccion, sistemas_afectados, datos_afectados, categorias_datos, numero_titulares_afectados_estimado | Cualquier usuario |
| TareaSistema | **Crear Brecha registro** - estado=DETECTADA, genera brecha_id único | Sistema |
| TareaSistema | **Registrar evidencia hashchain M1** - timestamp + hash del reporte inicial | Sistema |
| TareaSistema | **Notificar DPO inmediatamente** - email automático con brecha_id | Sistema de Correo |
| TareaSistema | **Iniciar Timer 72 horas APDC** - Timer event que cuenta desde fecha_deteccion | Sistema |

### FASE 2 - CLASIFICACIÓN

| Elemento | Descripción | Lane |
|----------|-------------|------|
| TareaUsuario | **Clasificar tipo de brecha** - Tipos: CONFIDENCIALIDAD, INTEGRIDAD, DISPONIBILIDAD | DPO |
| TareaUsuario | **Identificar categorías datos comprometidos** - Opciones: normal, sensible, protected | DPO |
| TareaUsuario | **Estimar número titulares afectados** - Cantidad estimada de personas afectadas | DPO |
| TareaSistema | **Calcular puntuación criticidad automática** - Fórmula: (categorias × ponderacion) + (num_afectados × factor) + (tipo × peso) | Sistema |
| GatewayExclusivo | **Clasificación criticidad** → BAJA / MEDIA / ALTA / CRÍTICA | - |

### FASE 3 - EVALUACIÓN DE IMPACTO

| Elemento | Descripción | Lane |
|----------|-------------|------|
| GatewayExclusivo | **¿Criticidad >= MEDIA?** → No → Flujo simplificado, Sí → continúa evaluación completa | - |
| TareaUsuario | **Evaluar impacto negocio** - campos: financial_impact, reputational_impact, legal_impact | DPO |
| TareaUsuario | **Evaluar impacto derechos titulares** - campos: daño_reputacional, discriminacion, fraude, perdida_financiera | DPO |
| GatewayParalelo | **Evaluación paralela** - 3 ramas simultáneas | - |
| Branch 1 | TareaUsuario: **Evaluar obligaciones contractuales** | DPO |
| Branch 2 | TareaUsuario: **Evaluar Encargados de Tratamiento involucrados** | DPO |
| Branch 3 | TareaSistema: **Buscar controles existentes breach** | Sistema |
| GatewayParalelo | **Reunir evaluaciones** - Sincronización de ramas paralelas | - |
| TareaSistema | **Generar informe evaluación impacto** - Documento consolidado | Sistema |

### FASE 4 - COMITÉ DE REVISIÓN

| Elemento | Descripción | Lane |
|----------|-------------|------|
| GatewayExclusivo | **¿Criticidad = CRÍTICA?** → Sí → Convocar comité de emergencia, No → continúa | - |
| TareaSistema | **Convocar comité de emergencia** - Invita: DPO, Gerente Legal, Risk Manager, Comunicaciones | Sistema |
| TareaUsuario | **Sesión comité de revisión** - Participantes: DPO, Legal, Risk, Compliance, Comunicaciones | Comité |
| TareaUsuario | **Documentar acuerdos committee** - Minuta con: decisiones, responsables, plazos | DPO |
| GatewayExclusivo | **Decisión del comité** → Informar APDC / No informar APDC | - |
| GatewayExclusivo | **¿Riesgo para titulares?** → Sí → Notificar titulares, No → Omitir notificación | - |

### FASE 5 - NOTIFICACIÓN APDC (72 horas)

| Elemento | Descripción | Lane |
|----------|-------------|------|
| GatewayExclusivo | **¿Decisión: Notificar APDC?** → No → Saltar a remediación, Sí → continúa | - |
| TareaUsuario | **Elaborar notificación APDC** - Contenido según Art. 26.3: naturaleza breach, categorías datos, consecuencias, medidas adoptadas | DPO |
| TareaSistema | **Validar completitud notificación** - Verificar campos requeridos | Sistema |
| TareaSistema | **Enviar notificación APDC** - Medio: registro APDC o email certificado | Sistema |
| TareaSistema | **Registrar fecha_envio_apdp** - Timestamp oficial de envío | Sistema |
| TareaSistema | **Actualizar evidencia hashchain** - Registrar envío con hash | Sistema |
| GatewayExclusivo | **¿APDC requiere información adicional?** → Sí → Preparar respuesta, No → continúa | - |
| TareaUsuario | **Preparar respuesta APDC** - Complementar información requerida | DPO |

### FASE 6 - NOTIFICACIÓN A TITULARES

| Elemento | Descripción | Lane |
|----------|-------------|------|
| GatewayExclusivo | **¿Riesgo para titulares?** → No → Saltar notificación, Sí → continúa | - |
| TareaUsuario | **Redactar comunicación a afectados** - DPO + Comunicaciones | DPO / Comunicaciones |
| TareaSistema | **Enviar notificación masivo** - Una notificación por cada titular afectado | Sistema de Correo |
| TareaSistema | **Registrar envios** - Logs de entrega con timestamps | Sistema |

### FASE 7 - REMEDIACIÓN

| Elemento | Descripción | Lane |
|----------|-------------|------|
| TareaUsuario | **Elaborar plan remediación** - Medidas: técnicas, organizativas, correctivas | DPO |
| TareaUsuario | **Asignar responsables remediación** - DefinirOWNER por cada medida | DPO |
| TareaSistema | **Crear tareas seguimiento** - Tickets de monitoreo | Sistema |
| GatewayExclusivo | **¿Brecha contenida?** → No → Continuar remediación, Sí → continúa | - |
| TareaUsuario | **Verificar implementación medidas** - Validar que controles funcionan | DPO |
| TareaSistema | **Documentar lecciones aprendidas** - Best practices para futuro | Sistema |

### FASE 8 - CIERRE

| Elemento | Descripción | Lane |
|----------|-------------|------|
| TareaSistema | **Actualizar estado = CERRADA** - Cambio de estado final | Sistema |
| TareaSistema | **Generar informe final breach** - PDF con: cronograma, evidencias, notificaciones, remediación | Sistema |
| TareaSistema | **Archivar evidencias hashchain** - Almacenamiento inmutable | Sistema |
| TareaSistema | **Notificar cierre a stakeholders** - Comunicación de cierre proceso | Sistema de Correo |
| End Event | **Brecha cerrada y documentada** | - |

---

## 3. TABLA RACI

| Actividad | Reportante | DPO | Comité | Sistema | Sistema de Correo | APDC | Titulares Afectados |
|-----------|:----------:|:---:|:------:|:-------:|:-----------------:|:----:|:-------------------:|
| Reportar brecha | **R** | - | - | - | - | - | - |
| Crear registro brecha | I | I | - | **R/A** | - | - | - |
| Clasificar tipo brecha | - | **R/A** | - | C | - | - | - |
| Calcular criticidad | - | C | - | **R/A** | - | - | - |
| Evaluar impacto negocio | - | **R** | A | C | - | - | - |
| Convocar comité | - | I | - | **R/A** | I | - | - |
| Sesión comité | - | R | **A** | I | - | - | - |
| Decisión notificar APDC | - | R | **A** | C | - | - | - |
| Elaborar notificación APDC | - | **R/A** | C | C | - | I | - |
| Enviar notificación APDC | - | I | - | **R** | **A** | **I** | - |
| Notificar titulares | - | R | C | C | **A** | - | **I** |
| Plan remediación | - | **R/A** | C | I | - | - | - |
| Verificar implementación | - | **R/A** | - | C | - | - | - |
| Cierre brecha | - | I | - | **R/A** | I | - | - |

**Leyenda**: R=Responsable, A=Autoridad, C=Consultado, I=Informado

---

## 4. EVENTOS

### Start Events
| Evento | Tipo | Descripción |
|--------|------|-------------|
| Brecha detectada | Mensaje (Start) | Indica que se ha recibido notificación de una brecha de seguridad |

### Intermediate Events
| Evento | Tipo | Descripción |
|--------|------|-------------|
| 72 horas APDC | Timer (Intermediate) | Deadline legal para notificación a la Agencia de Protección de Datos Personales |
| 24 horas recordatorio | Timer (Intermediate) | Recordatorio antes del deadline APDC |
| Comité convocado | Signal (Intermediate) | Señal de que el comité de emergencia ha sido convocado |

### Boundary Events
| Evento | Tipo | Attached To | Descripción |
|--------|------|-------------|-------------|
| Timeout 72h | Timer (Boundary) | Tarea "Elaborar notificación APDC" | Alerta de deadline inminente |

### End Events
| Evento | Tipo | Descripción |
|--------|------|-------------|
| Brecha cerrada | End | Proceso completado exitosamente con toda la documentación |

---

## 5. DATOS UTILIZADOS

### Entidad Principal: Brecha

| Campo | Tipo | Descripción | Requerido |
|-------|------|-------------|:---------:|
| brecha_id | UUID | Identificador único del registro | Sí |
| fecha_deteccion | DateTime | Momento en que se detectó la brecha | Sí |
| fecha_creacion | DateTime | Timestamp de creación del registro | Sí |
| tipo | Enum | CONFIDENCIALIDAD, INTEGRIDAD, DISPONIBILIDAD | Sí |
| criticidad | Enum | BAJA, MEDIA, ALTA, CRÍTICA | Sí |
| categorias_datos_afectados | Array | [normal, sensible, protected] | Sí |
| num_titulares_afectados | Integer | Cantidad estimada de afectados | Sí |
| impacto_financiero_estimado | Decimal | Estimación de impacto económico (UF) | No |
| notificacion_apdp_enviada | Boolean | Indica si se notificó a APDC | Sí |
| fecha_envio_apdp | DateTime | Timestamp de envío a APDC | Condicional |
| notificacion_titulares_enviada | Boolean | Indica si se notificaron afectados | Sí |
| estado | Enum | DETECTADA, EN_EVALUACION, EN_COMITE, EN_NOTIFICACION, EN_REMEDIACION, CERRADA | Sí |
| plan_remediacion | JSON | Detalle de medidas correctivas | Condicional |
| evidencia_hashchain | Array | Lista de hashes de evidencia | Sí |
| lecciones_aprendidas | Text | Documentación de mejoras | No |

### Data Objects

| Data Object | Descripción |
|-------------|-------------|
| ReporteBrecha | Documento inicial de reporte con formato libre |
| InformeImpacto | Evaluación consolidada de impacto |
| NotificacionAPDC | Documento formal de notificación a la Agencia |
| PlanRemediacion | Plan estructurado de medidas correctivas |
| EvidenciaHashchain | Conjunto de evidencias con hashes immutables |

---

## 6. SLAS

| SLA | Descripción | Base Legal | Criticidad Aplica |
|-----|-------------|------------|-------------------|
| Notificación APDC | **72 horas** desde detección | Art. 26.3 Ley 21.719 | Todas |
| Notificación titulares | **Sin dilación indebida** cuando existe riesgo | Art. 26.4 Ley 21.719 | MEDIA, ALTA, CRÍTICA |
| Comité crítico | Within **24 horas** de clasificación CRÍTICA | Intern policy | CRÍTICA |
| Plan remediación | Within **7 días** (BAJA), **3 días** (MEDIA), **24h** (ALTA/CRÍTICA) | Art. 26.5 Ley 21.719 | Según severidad |
| Respuesta APDC adicional | Within **72 horas** de requerimiento | Art. 26.3 Ley 21.719 | Cuando aplique |

---

## 7. RIESGOS

| ID | Riesgo | Probabilidad | Impacto | Mitigación |
|----|--------|:------------:|:-------:|------------|
| BR-001 | Incumplimiento deadline 72h APDC | Media | Crítico | Timer + alertas automáticas + escalamiento |
| BR-002 | Notificación a APDC incompleta o incorrecta | Baja | Alto | Template validado + checklist de completitud |
| BR-003 | Evidencia insuficiente para auditoría | Baja | Alto | Hashchain automático desde detección |
| BR-004 | Recurrencia de brechas similares | Media | Medio | Lecciones aprendidas + revisión controles |
| BR-005 | Titular no notificado cuando es requerido | Baja | Crítico | Gateway obligatorio + registro de envíos |
| BR-006 | Plan de remediación ineficaz | Media | Alto | Verificación + métricas de efectividad |
| BR-007 | Comité no documentado adecuadamente | Baja | Medio | Minuta obligatoria + aprobación DPO |
| BR-008 | Datos afectados mal clasificados | Baja | Alto | Guía de clasificación + revisión DPO |
| BR-009 | Encargado de tratamiento no informado | Baja | Medio | Evaluación obligatoria en Fase 3 |
| BR-010 | Exposición reputacional por comunicación deficiente | Baja | Alto | Revisión Comunicaciones + template aprobado |

---

## 8. CONTROLES Y KPIS

### Controles

| Control | Descripción | Frecuencia |
|---------|-------------|------------|
| C-01 | Verificación de hashchain en cada fase | Continuo |
| C-02 | Validación de completitud antes de envío APDC | Por notificación |
| C-03 | Audit trail de accesos a registro de brecha | Continuo |
| C-04 | Review de clasificación por segundo DPO (brechas CRÍTICAS) | Por caso |
| C-05 | Testing de plan de contingencia de comunicación | Trimestral |

### KPIs

| KPI | Definición | Meta | Umbral Alerta |
|-----|------------|-----:|---------------|
| K-01 | **Brechas notificadas en plazo** = (Notificaciones APDC ≤72h / Total notificadas) × 100 | ≥95% | <90% |
| K-02 | **Tiempo medio detección→cierre** = Promedio días desde fecha_deteccion hasta estado=CERRADA | ≤15 días | >21 días |
| K-03 | **Tasa notificación titulares** = (Titulares notificados / Titulares que debían ser notificados) × 100 | 100% | <100% |
| K-04 | **Recurrencia brechas** = Número de brechas del mismo tipo en 12 meses | ≤3 ocurrencias | >5 ocurrencias |
| K-05 | **Eficacia remediación** = (Medidas implementadas / Medidas planificadas) × 100 | ≥90% | <80% |

---

## 9. ANEXOS

### A. Fórmula de Criticidad

```
Puntuación = (categorias_peso × Σponderacion_categorias) + (num_afectados_factor × num_afectados) + (tipo_peso × tipo)

Donde:
- categorias_peso = 25
- ponderacion_categorias: normal=1, sensible=3, protected=5
- num_afectados_factor = 0.1
- tipo_peso: CONFIDENCIALIDAD=3, INTEGRIDAD=2, DISPONIBILIDAD=1

Clasificación:
- Puntuación < 30 → BAJA
- 30 ≤ Puntuación < 60 → MEDIA
- 60 ≤ Puntuación < 100 → ALTA
- Puntuación ≥ 100 → CRÍTICA
```

### B. Contenido Mínimo Notificación APDC (Art. 26.3)

1. Naturaleza de la brecha
2. Categorías y número aproximado de afectados
3. Consecuencias probables
4. Medidas adoptadas o propuestas
5. Indicación si se informó o no a los titulares

### C. Estados del Proceso

```
DETECTADA → EN_EVALUACION → EN_COMITE → EN_NOTIFICACION → EN_REMEDIACION → CERRADA
     │              │             │              │                  │           │
     └──────────────┴─────────────┴──────────────┴──────────────────┴───────────┘
                         (posibles flujos alternativos según criticidad)
```

---

*Documento generado para Custodio SaaS Platform - Compliance Ley 21.719*
*Versión: 1.0 | Fecha: 2026-06-18*