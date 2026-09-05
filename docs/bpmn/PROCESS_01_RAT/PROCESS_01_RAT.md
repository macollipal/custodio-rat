# PROCESO 01: RAT - Registro de Actividades de Tratamiento

**Plataforma:** Custodio SaaS  
**Versión:** 1.0  
**Fecha:** 2026-06-18  
**Clasificación:** Público  
**Fundamento Legal:** Art. 30 GDPR / Art. 11 Ley 21.719 Chile

---

## 1. EXPLICACIÓN FUNCIONAL

El proceso RAT (Registro de Actividades de Tratamiento) gestiona el ciclo de vida completo de los registros de actividades de tratamiento de datos personales, en cumplimiento con el Artículo 30 del RGPD y el Artículo 11 de la Ley 21.719 chilena sobre protección de datos personales.

Este proceso garantiza que toda actividad de tratamiento de datos personales esté debidamente documentada, evaluada en cuanto a riesgos, y aprobada antes de su activación. El proceso se divide en cuatro fases principales:

### Fase 1: Identificación y Registro
En esta fase inicial, el DPO (Delegado de Protección de Datos) crea un nuevo registro RAT e ingresa la información básica del tratamiento, incluyendo el nombre de la actividad, la empresa responsable, el responsable del tratamiento, la finalidad y una descripción detallada de la operación. Esta información constituye la base identificativa del registro.

### Fase 2: Evaluación y Clasificación
Durante esta fase se determinan todos los elementos críticos para la clasificación del tratamiento: la base legal aplicable, las categorías de datos involucrados (incluyendo datos sensibles cuando corresponda), los encargados de tratamiento externos, y se realiza una evaluación automática de riesgos según los criterios del Artículo 35 del RGPD.

### Fase 3: Validación y Aprobación
El DPO elabora las medidas de seguridad apropiadas, se calcula el riesgo residual, y el registro pasa por una revisión de validación. Finalmente, un DPO Senior o Gerente con rol admin_empresa debe aprobar formalmente el registro RAT.

### Fase 4: Activación y Mantenimiento
Una vez aprobado, el sistema genera el PDF oficial del RAT, lo registra en un hashchain para garantizar su inmutabilidad, y activa el registro. Se establecen timers para revisión periódica anual y alertas de caducidad de contratos con encargados de tratamiento.

---

## 2. BPMN TEXTUAL DETALLADO

### Flujo Principal del Proceso

**Inicio:** El DPO inicia un nuevo registro RAT desde la consola de administración de la plataforma Custodio.

**Tarea: Completar información básica del tratamiento** (Lane: DPO)  
El DPO ingresa los siguientes campos obligatorios:
- nombre_actividad: Identificador único de la actividad de tratamiento
- empresa_id: Identificador de la empresa titular del tratamiento
- responsable_tratamiento: Persona o entidad que determina los fines y medios del tratamiento
- finalidad: Propósito específico y legítimo del tratamiento
- descripcion_operacion: Descripción detallada de las operaciones de tratamiento

**Tarea: Determinar base legal** (Lane: DPO)  
El DPO debe seleccionar la base legal aplicable al tratamiento:
- consentimiento: El interesado dio su consentimiento explícito
- contrato: El tratamiento es necesario para la ejecución de un contrato
- obligación_legal: El tratamiento es necesario para cumplir una obligación legal
- interés_público: El tratamiento es necesario para el ejercicio de funciones públicas
- interés_legítimo: El tratamiento es necesario para intereses legítimos del responsable
- protección_vital: El tratamiento es necesario para proteger intereses vitales

**Gateway: Base legal = consentimiento?** (Gateway Exclusivo)  
- **Sí:** Continuar a "Configurar mecanismo de obtención consentimiento"
- **No:** Saltar a "Identificar categorías de datos"

**Tarea: Configurar mecanismo de obtención consentimiento** (Lane: DPO)  
Se definen los parámetros de obtención del consentimiento:
- Mecanismo de obtención (formulario, checkbox, etc.)
- Texto del consentimiento informado
- Método de registro de la aceptación

**Tarea: Identificar categorías de datos** (Lane: DPO)  
El DPO selecciona las categorías de datos involucradas:
- datos_identificativos: Nombres, apellidos, RUT, documentos de identidad
- datos_contacto: Teléfono, email, dirección postal
- datos_economicos: Cuentas bancarias, información financiera
- datos_salud: Información médica y de salud
- datos_geneticos: Datos genéticos y biomédicos
- datos_biometricos: Huellas dactilares, reconocimiento facial, etc.
- datos_ubicacion: Datos de geolocalización
- datos_electronicos: Direcciones IP, cookies, registros de actividad

**Tarea: Identificar datos sensibles** (Lane: DPO)  
El DPO identifica si hay datos sensibles según Art. 11 Ley 21.719:
- origen_étnico: Origen étnico o racial
- opiniones_políticas: Opiniones o convicciones políticas
- creencias_religiosas: Creencias religiosas o filosóficas
- afiliación_sindical: Afiliación sindical o gremial
- salud_sexual: Salud sexual y reproductiva
- datos_penales: Datos relativos a condenas o infracciones penales

**Gateway: ¿Datos sensibles detectados?** (Gateway Exclusivo)  
- **Sí:** Continuar a "Aplicar medidas adicionales Art. 11 Ley 21.719"
- **No:** Saltar a "¿Transferencias internacionales?"

**Tarea: Aplicar medidas adicionales Art. 11 Ley 21.719** (Lane: DPO)  
Se implementan medidas especiales para datos sensibles:
- Evaluación de necesidad y proporcionalidad
- Medidas técnicas y organizativas reforzadas
- Documentación de justificación del tratamiento

**Gateway: ¿Transferencias internacionales?** (Gateway Exclusivo)  
- **Sí:** Continuar a "Documentar transferencia internacional"
- **No:** Saltar a "Identificar encargados de tratamiento"

**Tarea: Documentar transferencia internacional** (Lane: DPO)  
Se documenta la transferencia internacional de datos:
- País de destino
- Organismo internacional receptor
- Mecanismo de transferencia utilizado
- Garantías aplicables (cláusulas contractuales, binding corporate rules, etc.)

**Tarea: Identificar encargados de tratamiento** (Lane: DPO)  
El DPO registra la información de los encargados de tratamiento externos:
- Identificación del encargado
- Servicios prestados
- Ubicación y país
- Datos compartidos

**Tarea: Evaluar riesgo automático** (Lane: Sistema)  
El sistema realiza una evaluación automática de riesgos según Art. 35 GDPR:
- Calcula probabilidad_impacto basándose en naturaleza, alcance y contexto
- Determina nivel_riesgo: BAJO, MEDIO o ALTO
- Aplica fórmula de evaluación de riesgo según metodología internal
- Genera informe de evaluación de riesgo

**Gateway: ¿Riesgo ALTO (requiere EIPD)?** (Gateway Exclusivo)  
- **Sí:** Continuar a "Crear EIPD-001" y "Revisar conclusiones EIPD"
- **No:** Saltar a "Elaborar medidas de seguridad"

**Tarea: Crear EIPD-001** (Lane: Sistema)  
El sistema crea automáticamente una nueva Evaluación de Impacto en la Protección de Datos (EIPD):
- Genera identificador único EIPD-001
- Vincula el EIPD al RAT correspondiente
- Activa el proceso de EIPD para evaluación detallada
- Notifica al DPO para revisión

**Tarea: Revisar conclusiones EIPD** (Lane: DPO)  
El DPO revisa las conclusiones del EIPD:
- Analiza los resultados de la evaluación de impacto
- Documenta medidas de mitigación propuestas
- Aprueba o modifica las conclusiones

**Tarea: Elaborar medidas de seguridad** (Lane: DPO)  
El DPO define las medidas de seguridad apropiadas:
- Medidas técnicas (cifrado, control de acceso, etc.)
- Medidas organizativas (políticas, procedimientos, formación)
- Medidas específicas según el nivel de riesgo

**Tarea: Calcular puntuación riesgo residual** (Lane: Sistema)  
El sistema recalcula el riesgo después de aplicar las medidas de seguridad:
- Evalúa efectividad de las medidas implementadas
- Calcula riesgo residual剩余风险
- Compara con umbral de aceptabilidad

**Gateway: ¿Riesgo residual acceptable?** (Gateway Exclusivo)  
- **Sí:** Saltar a "Revisar y validar registro"
- **No:** Continuar a "Implementar controles adicionales"

**Tarea: Implementar controles adicionales** (Lane: DPO)  
El DPO implementa controles adicionales para reducir el riesgo residual:
- Refuerza medidas técnicas y organizativas
- Documenta nuevas medidas
- Recalcula riesgo residual

**Tarea: Revisar y validar registro** (Lane: DPO)  
El DPO realiza una revisión final del registro:
- Verifica completitud de toda la información
- Confirma coherencia entre base legal y medidas
- Aprueba el registro para enviar a aprobación final

**Tarea: Aprobar registro RAT** (Lane: DPO Senior/Gerente)  
Usuario con rol admin_empresa aprueba formalmente el registro:
- Revisa y aprueba el registro RAT completado
- Confirma la adecuación de medidas de seguridad
- Firme electrónicamente la aprobación
- Solo usuarios con rol admin_empresa pueden ejecutar esta tarea

**Tarea: Generar PDF oficial RAT** (Lane: Sistema)  
El sistema genera el documento oficial:
- Compila toda la información del RAT en formato PDF
- Incluye código QR para verificación
- Genera firma digital del sistema
- Almacena el PDF como evidencia oficial

**Tarea: Registrar en historial de cambios** (Lane: Sistema)  
El sistema registra la aprobación en hashchain inmutable:
- Crea registro de auditoría con marca de tiempo
- Calcula hash criptográfico del contenido
- Vincula al hash anterior (cadena de bloques interno)
- Garantiza inmutabilidad del registro

**Tarea: Activar registro RAT** (Lane: Sistema)  
El sistema cambia el estado del registro:
- Establece estado = ACTIVO
- Hace visible el RAT en el portal público (si aplica)
- Activa timers de revisión periódica
- Notifica a partes interesadas

**Fin:** El registro RAT queda activo en el sistema.

---

### Eventos de Temporizador Intermedios

**Revisión periódica anual** (Lane: DPO)  
Cada 12 meses desde la activación, el sistema genera un timer que requiere:
- Revisión completa del RAT por el DPO
- Verificación de que las condiciones no han cambiado
- Actualización si es necesario
- Re-aprobación si hay cambios significativos

**Notificar caducidad certificados encargados** (Lane: Sistema)  
Cada 30 días antes del vencimiento de contratos con encargados de tratamiento:
- El sistema verifica fechas de vencimiento
- Genera alertas automáticas
- Notifica al DPO para renovación
- Registra alertas en historial de auditoría

---

## 3. TABLA RACI

| Actividad | Titular | DPO | DPO Senior | Sistema | Encargado | APDC | Comentario |
|-----------|---------|-----|------------|---------|-----------|------|------------|
| Completar información básica | I | R | - | I | - | - | DPO ingresa datos |
| Determinar base legal | I | R/A | C | - | - | - | Titular consultado |
| Configurar mecanismo consentimiento | I | R | A | C | - | - | Si aplica |
| Identificar categorías de datos | I | R | - | C | - | - | Clasificación |
| Identificar datos sensibles | I | R | - | C | - | - | Art. 11 Ley 21.719 |
| Aplicar medidas adicionales | I | R/A | C | - | C | - | Datos sensibles |
| Documentar transferencia internacional | I | R | A | C | I | C | Si aplica |
| Identificar encargados | I | R | - | I | C | - | Coordinación |
| Evaluar riesgo automático | - | I | - | R/A | - | - | Sistema calcula |
| Crear EIPD-001 | - | I | C | R | - | - | Si riesgo ALTO |
| Revisar conclusiones EIPD | - | R/A | C | I | - | - | Requiere DPO |
| Elaborar medidas de seguridad | I | R/A | C | I | - | - | Aprobación DPO Senior |
| Calcular riesgo residual | - | I | - | R/A | - | - | Sistema |
| Implementar controles adicionales | I | R/A | C | I | - | - | Si riesgo no aceptable |
| Revisar y validar registro | - | R/A | C | I | - | - | Validación final |
| Aprobar registro RAT | I | C | R/A | I | - | - | admin_empresa |
| Generar PDF oficial | - | - | - | R/A | - | - | Automático |
| Registrar en historial | - | I | - | R/A | - | I | Hashchain |
| Activar registro RAT | - | I | - | R/A | - | - | Cambio estado |
| Revisión periódica anual | - | R/A | C | I | I | - | Timer event |
| Notificar caducidad contratos | - | I | - | R/A | - | - | Alertas automáticas |

**Leyenda:** R=Responsable, A=Autoriza, C=Consultado, I=Informado

---

## 4. EVENTOS

### Eventos de Inicio (Start Events)

| Evento | Tipo | Descripción | Trigger |
|--------|------|-------------|---------|
| DPO inicia registro | None StartEvent | DPO crea nuevo RAT desde consola | Usuario (DPO) |
| Timer revisión anual | Timer StartEvent | Revisión programada cada 12 meses | Temporizador automático |

### Eventos de Fin (End Events)

| Evento | Tipo | Descripción | Resultado |
|--------|------|-------------|-----------|
| Registro RAT activo | None EndEvent | RAT completado y activado | Estado = ACTIVO |
| Registro archivado | None EndEvent | RAT dado de baja | Estado = ARCHIVADO |
| EIPD creado | None EndEvent | EIPD generado | Nuevo proceso EIPD |

### Eventos Intermedios (Intermediate Events)

| Evento | Tipo | Descripción | Duración |
|--------|------|-------------|----------|
| Timer 12 meses | Timer Intermediate Throw Event | Revisión periódica obligatoria | 12 meses desde activación |
| Timer 30 días | Timer Intermediate Catch Event | Renovación contratos encargados | 30 días antes de vencimiento |

---

## 5. DATOS UTILIZADOS

| Nombre Datos | Descripción | Tipo | Fuente | Obligatorio |
|--------------|-------------|------|--------|-------------|
| nombre_actividad | Identificador único de la actividad | String(100) | Usuario DPO | Sí |
| finalidad | Propósito del tratamiento | String(500) | Usuario DPO | Sí |
| base_legal | Fundamento jurídico del tratamiento | Enum | Usuario DPO | Sí |
| categorias_datos | Categorías de datos procesados | Array[Enum] | Usuario DPO | Sí |
| datos_sensibles | Indicador de datos sensibles | Boolean | Usuario DPO | Sí |
| medidas_seguridad | Medidas técnicas y organizativas | Array[Object] | Usuario DPO | Sí |
| encargado_tratamiento | Entidad que procesa datos por cuenta del responsable | Object | Usuario DPO | No |
| contrato_encargado | Contrato formal con encargado | Document | Usuario DPO | No |
| evaluacion_riesgo | Resultado de evaluación automática | Object | Sistema | Sí |
| eipd_id | Identificador de EIPD vinculada | String(20) | Sistema | No |
| riesgo_residual | Nivel de riesgo después de controles | Enum(BAJO/MEDIO/ALTO) | Sistema | Sí |
| estado | Estado actual del RAT | Enum | Sistema | Sí |
| version | Número de versión del registro | Integer | Sistema | Sí |
| hash_inmutable | Hash criptográfico del registro | String(64) | Sistema | Sí |
| empresa_id | Identificador de la empresa | String(20) | Sistema | Sí |
| rat_id | Identificador único del RAT | String(20) | Sistema | Sí |
| fecha_creacion | Fecha de creación del registro | DateTime | Sistema | Sí |
| fecha_aprobacion | Fecha de aprobación | DateTime | Sistema | Sí |
| fecha_caducidad | Fecha de vencimiento para revisión | DateTime | Sistema | Sí |
| pdf_oficial | Documento PDF oficial del RAT | Binary | Sistema | Sí |
| mecanismo_consentimiento | Configuración del consentimiento | Object | Usuario DPO | No |
| pais_destino | País de destino de transferencia | String(50) | Usuario DPO | No |
| garantia_transferencia | Mecanismo de garantía utilizado | String(100) | Usuario DPO | No |

---

## 6. SLAS

| Tipo | Plazo | Fundamento Legal | Consecuencia Incumplimiento |
|------|-------|------------------|---------------------------|
| Creación inicial | 72 horas desde solicitud | Art. 30.1 GDPR / Art. 11 Ley 21.719 | Sanción administrativa hasta 10M CLP (Art. 47 Ley 21.719) |
| Revisión periódica | 12 meses | Art. 30.5 GDPR | Registro no conforme, potencial sanción |
| Renovación contratos encargados | 30 días antes vencimiento | Art. 28 GDPR / Art. 12 Ley 21.719 | Tratamiento sin contrato válido, sanción hasta 20M CLP |
| Notificación APDC transferencias | 1 mes antes de transferencia | Art. 25 Ley 21.719 | Prohibición de transferencia, multa hasta 15M CLP |
| Actualización por cambio sustancial | 15 días desde cambio | Art. 30.2 GDPR | Registro desactualizado, falta de conformidad |
| Respuesta a ejercicio de derechos | 10 días hábiles | Art. 12.3 GDPR / Art. 17 Ley 21.719 | Infracción, reclamación ante APDC |
| Conservación de registros | 5 años desde fin tratamiento | Art. 12 Ley 21.719 | Imposibilidad de demostrar compliance |

---

## 7. RIESGOS

| ID | Descripción | Probabilidad | Impacto | Nivel | Mitigación |
|----|-------------|--------------|---------|-------|------------|
| RAT-001 | No registrar actividad de tratamiento | Alta | Crítico | ALTO | Auto-detection de actividades no registradas mediante análisis de flujo de datos |
| RAT-002 | Base legal incorrecta o inapropiada | Media | Alto | MEDIO | Wizard guiado con ejemplos y validación de coherencia |
| RAT-003 | EIPD no solicitado cuando es requerido (riesgo ALTO) | Alta | Crítico | ALTO | Flag automático en evaluación de riesgo con bloqueo de aprobación sin EIPD |
| RAT-004 | Contratos con encargados de tratamiento vencidos | Media | Alto | MEDIO | Alertas automáticas 60, 30 y 15 días antes del vencimiento |
| RAT-005 | Datos sensibles sin medidas adicionales apropiadas | Alta | Crítico | ALTO | Validación en flujo que impide avanzar sin medidas Art. 11 |
| RAT-006 | Revisión periódica vencida (más de 12 meses) | Media | Medio | MEDIO | Timer events con notificaciones progresivas y degradación de estado |
| RAT-007 | Transferencia internacional sin autorización APDC | Alta | Crítico | ALTO | Checklist obligatorio con países y mecanismos pre-validados |
| RAT-008 | Hashchain comprometido o alterado | Baja | Crítico | MEDIO | Auditoría externa trimestral, verificación criptográfica mensual |
| RAT-009 | RAT activado sin aprobación de admin_empresa | Baja | Alto | MEDIO | Control de acceso basado en roles, firma electrónica de aprobación |
| RAT-010 | Flujo de datos no corresponde con registro RAT | Media | Alto | MEDIO | Detección de anomalías mediante monitoring continuo |

---

## 8. CONTROLES

| ID | Control | Tipo | Frecuencia | Responsable | Evidencia |
|----|---------|------|------------|-------------|-----------|
| CTRL-001 | Verificación automática de registro de todas las actividades | Preventivo | Mensual | Sistema | Reporte de actividades no registradas |
| CTRL-002 | Validación de coherencia base legal vs categorías de datos | Preventivo | Por registro | Sistema | Log de validación |
| CTRL-003 | Bloqueo de aprobación RAT con riesgo ALTO sin EIPD | Preventivo | Por registro | Sistema | Estado del proceso BPMN |
| CTRL-004 | Sistema de alertas de caducidad de contratos | Detectivo | Diaria | Sistema | Registro de alertas enviadas |
| CTRL-005 | Checklist obligatorio de medidas Art. 11 para datos sensibles | Preventivo | Por registro | DPO | Formulario completado |
| CTRL-006 | Timer events para revisión periódica con escalamiento | Detectivo | Por timer | Sistema | Historial de revisiones |
| CTRL-007 | Validación pre-envío de transferencias internacionales | Preventivo | Por transferencia | DPO/Sistema | Formulario APDC completado |
| CTRL-008 | Verificación criptográfica de hashchain | Detectivo | Mensual | Sistema Externo | Certificado de verificación |
| CTRL-009 | Auditoría de firmas electrónicas en aprobaciones | Detectivo | Trimestral | DPO Senior | Log de auditoría |
| CTRL-010 | Monitorización de flujo de datos vs RAT registrados | Detectivo | Continuo | Sistema | Dashboard de anomalías |

---

## 9. KPIS

| KPI | Definición | Meta | Frecuencia | Sentido |
|-----|------------|------|------------|---------|
| Total RAT activos | Count de registros con estado=ACTIVO | = número de actividades reales de tratamiento | Mensual | = Actividad real |
| Cumplimiento revisión | (RAT revisados en plazo / RAT totales) × 100 | 100% | Mensual | ↑ Mejor |
| RAT pendientes aprobación | Count de registros con estado=PENDIENTE_APROBACION | < 5 | Semanal | ↓ Mejor |
| Vencimiento contratos encargados | Count de contratos con vencimiento < 30 días | 0 | Diaria | ↓ Mejor |
| EIPDs requeridos vs ejecutados | Ratio EIPD creados / EIPD requeridos por riesgo ALTO | 1.0 | Mensual | = 1.0 |
| Tiempo promedio creación RAT | Días promedio desde inicio hasta estado ACTIVO | < 5 días | Mensual | ↓ Mejor |
| RAT sin revisión > 12 meses | Count de RAT con última revisión > 12 meses | 0 | Mensual | ↓ Mejor |
| Transferencias sin documentar | Count de transferencias sin registro en RAT | 0 | Diaria | ↓ Mejor |

---

**Documento generado por:** Custodio Platform  
**Fecha generación:** 2026-06-18  
**Versión documento:** 1.0
