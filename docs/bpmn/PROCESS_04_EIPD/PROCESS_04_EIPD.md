# PROCESS 04: EIPD - Evaluación de Impacto en la Protección de Datos

**Versión Documento:** 1.0  
**Fecha de Versión:** Junio 2026  
**Estado:** APROBADO  
**Autor:** Custodio Architecture Team  
**Plataforma:** Custodio SaaS - Chile (Ley 21.719 Art. 15)  
**Proceso Padre:** RAT (Process 1)  
**Clasificación:** INTERNO

---

## 1. EXPLICACIÓN FUNCIONAL

### 1.1 Objetivo del Proceso

La **Evaluación de Impacto en la Protección de Datos (EIPD)** es un proceso obligatorio bajo el **Artículo 15 de la Ley 21.719** de Protección de Datos Personales de Chile. Su propósito es evaluar y mitigar los riesgos que el tratamiento de datos personales puede generar sobre los derechos y libertades de los titulares.

### 1.2 Trigger Automático

La EIPD se **inicia automáticamente** desde el **Process 1 (RAT)** cuando la evaluación de riesgo resulta en un nivel **ALTO** o **MUY_ALTO**:

```
RAT.evaluacion_riesgo = ALTO → Trigger EIPD
RAT.evaluacion_riesgo = MUY_ALTO → Trigger EIPD
```

### 1.3 Alcance

El proceso EIPD abarca:

- **Evaluación de riesgos**: Identificación y análisis de amenazas, vulnerabilidades e impactos sobre los datos tratados
- **Identificación de medidas**: Documentación de controles existentes y propuestos para mitigar riesgos
- **Workflow de aprobación**: Circuitos de revisión y firma por DPO y DPO Senior
- **Revisión periódica**: Programación de re-evaluaciones cada 24 meses o ante cambios significativos

### 1.4 Fundamento Legal

- **Ley 21.719 Art. 15**: Obligatoriedad de EIPD para tratamientos que resulten en alto riesgo
- **Reglamento europeo GDPR Art. 35**: Referencia comparativa para metodología
- **Guía APDP Chile**: Directrices para la realización de evaluaciones

---

## 2. BPMN TEXTUAL DETALLADO

### 2.1 Diagrama de Flujo por Etapas

#### FASE 1: TRIGGER Y CREACIÓN

| Orden | Elemento | Lane | Descripción |
|-------|----------|------|-------------|
| 1 | **Start Event** | - | EIPD requerida desde RAT (automatic trigger) |
| 2 | **TareaSistema** | Sistema | Crear EIPD-XXX desde RAT-XXX. Hereda: rat_id, categorěas_datos, finalidad, operaciones, responsable |
| 3 | **TareaSistema** | Sistema | Registrar fecha_inicio EIPD |
| 4 | **TareaSistema** | Sistema | Establecer estado = EN_ELABORACION |

#### FASE 2: EVALUACIÓN INICIAL (DPO)

| Orden | Elemento | Lane | Descripción |
|-------|----------|------|-------------|
| 5 | **TareaUsuario** | DPO | Describir tratamiento objeto EIPD. Referencia: RAT padre, finalidad tratamiento, categorías datos, operaciones específicas |
| 6 | **TareaUsuario** | DPO | Evaluar necesidad y proporcionalidad. Preguntas: ¿Tratamiento necesario? ¿Mínimos datos adecuados? |
| 7 | **TareaUsuario** | DPO | Identificar riesgos inherentes. Formato: R01, R02... con: descripción, activo afectado, amenaza, vulnerabilidad |

#### FASE 3: CÁLCULO DE RIESGOS (Sistema)

| Orden | Elemento | Lane | Descripción |
|-------|----------|------|-------------|
| 8 | **TareaSistema** | Sistema | Calcular probabilidad inherente. Escala: MUY_BAJA(1), BAJA(2), MEDIA(3), ALTA(4), MUY_ALTA(5) |
| 9 | **TareaSistema** | Sistema | Calcular impacto inherente. Escala: NINGUNO(0), MINIMO(1), MODERADO(2), SIGNIFICATIVO(3), CRÍTICO(4) |
| 10 | **TareaSistema** | Sistema | Calcular nivel riesgo inherente. Fórmula: probabilidad × impacto |
| 11 | **Gateway Exclusivo** | - | Evaluación nivel riesgo inherente |

**Matriz de decisión Gateway (Punto 11):**

| Probabilidad × Impacto | Nivel Resultante |
|------------------------|------------------|
| 1-2 | MUY_BAJO |
| 3-4 | BAJO |
| 5-9 | MEDIO |
| 10-15 | ALTO |
| 16-20 | MUY_ALTO |

#### FASE 4: IDENTIFICACIÓN DE CONTROLES

| Orden | Elemento | Lane | Descripción |
|-------|----------|------|-------------|
| 12 | **TareaUsuario** | DPO | Documentar controles existentes. Tipos: técnicos (encriptación AES-256, control acceso RBAC), organizativos (políticas, formación) |
| 13 | **TareaSistema** | Sistema | Evaluar eficacia controles existentes. Rating: EFECTIVO / PARCIAL / INEFECTIVO |
| 14 | **TareaUsuario** | DPO | Identificar controles propuestos. Obligatorio para cada riesgo ALTO / MUY_ALTO |
| 15 | **TareaSistema** | Sistema | Calcular riesgo residual. Fórmula: riesgo_residual = riesgo_inherente - eficacia_controles |

#### FASE 5: GATEWAY DECISIÓN - RIESGO RESIDUAL

| Orden | Elemento | Lane | Descripción |
|-------|----------|------|-------------|
| 16 | **Gateway Exclusivo** | - | ¿Riesgo residual acceptable? |

**Lógica Gateway (Punto 16):**

- **Sí (≤ MEDIO)**: Ir a Fase 6 - APROBACIÓN
- **No (> MEDIO)**: 
  1. TareaUsuario "Implementar controles adicionales" (DPO)
  2. Recalcular riesgo residual (Sistema)
  3. Volver a evaluar Gateway (Punto 16)

#### FASE 6: APROBACIÓN

| Orden | Elemento | Lane | Descripción |
|-------|----------|------|-------------|
| 17 | **Gateway Exclusivo** | - | ¿Nivel riesgo residual MUY_ALTO? |
| 18 | **TareaUsuario** (condicional) | DPO Senior | Obtener autorización DPO Senior. Solo si MUY_ALTO |
| 19 | **TareaUsuario** | DPO | Revisar EIPD completo. Verificar: todos los campos, cálculos, controles, firmas previas |
| 20 | **TareaUsuario** | DPO Senior | Aprobar EIPD. Genera: firma_digital, fecha_aprobacion, hash_documento |
| 21 | **TareaSistema** | Sistema | Vincular EIPD a RAT padre. RAT.eipd_id = this.eipd_id |
| 22 | **TareaSistema** | Sistema | Actualizar estado RAT a CON_EIPD |
| 23 | **TareaSistema** | Sistema | Programar revisión periódica. Timer: 24 meses desde aprobación |

#### FASE 7: RECHAZO Y CORRECCIÓN

| Orden | Elemento | Lane | Descripción |
|-------|----------|------|-------------|
| 24 | **TareaUsuario** | DPO | Rechazar EIPD con comentarios. Especificar: qué falta, qué corregir |
| 25 | **TareaSistema** | Sistema | Notificar rechazo. Canal: Sistema de Correo electrónico |
| 26 | **TareaSistema** | Sistema | Devolver a DPO para corrección |
| 27 | **Gateway Exclusivo** | - | ¿EIPD corregido? |

**Lógica Gateway (Punto 27):**

- **No**: Loopback a Fase 2 - Evaluación Inicial
- **Sí**: Flujo continúa a Fase 6 - Aprobación

#### FASE 8: REVISIÓN PERIÓDICA

| Orden | Elemento | Lane | Descripción |
|-------|----------|------|-------------|
| 28 | **Intermediate Timer Event** | Sistema | Revisión 24 meses (Timer Boundary) |
| 29 | **TareaUsuario** | DPO | Evaluar si tratamiento ha cambiado. Análisis de cambios desde última revisión |
| 30 | **Gateway Exclusivo** | - | ¿Cambios significativos? |

**Lógica Gateway (Punto 30):**

- **Sí**: Iniciar nueva EIPD (nuevo proceso)
- **No**: Actualizar fecha_revision = hoy + 24 meses

#### FASE 9: POST-APROBACIÓN

| Orden | Elemento | Lane | Descripción |
|-------|----------|------|-------------|
| 31 | **TareaSistema** | Sistema | Monitorear implementación controles. Check periódico de cumplimiento |
| 32 | **TareaSistema** | Sistema | Generar informe EIPD. Output: PDF oficial con todos los datos |
| 33 | **End Event** | - | EIPD aprobado y activo |

---

## 3. TABLA RACI

| Actividad | DPO | DPO Senior | Sistema | RAT (Proceso Padre) | Comité Asesor |
|-----------|-----|------------|---------|---------------------|---------------|
| Crear EIPD desde RAT | - | - | **R** | I | - |
| Describir tratamiento | **R** | C | I | I | - |
| Evaluar necesidad/proporcionalidad | **R/A** | C | - | I | - |
| Identificar riesgos inherentes | **R/A** | C | - | - | - |
| Calcular probabilidad/impacto | - | - | **R** | - | - |
| Documentar controles existentes | **R** | C | - | - | - |
| Evaluar eficacia controles | - | - | **R/A** | - | - |
| Identificar controles propuestos | **R** | C | - | - | I |
| Calcular riesgo residual | - | - | **R** | - | - |
| Implementar controles adicionales | **R** | A | - | - | - |
| Revisar EIPD completo | **R/A** | C | - | - | - |
| Aprobar/Rechazar EIPD | C | **R/A** | - | - | - |
| Vincular EIPD a RAT | - | - | **R/A** | I | - |
| Programar revisión periódica | I | - | **R/A** | - | - |
| Evaluar cambios significativos | **R** | C | I | - | - |

**Leyenda:** R = Responsable, A = Accountable, C = Consultado, I = Informado

---

## 4. EVENTOS

### 4.1 Eventos de Inicio

| Evento | Tipo | Descripción | Trigger |
|--------|------|-------------|---------|
| EIPD requerida desde RAT | **Start Event (Automatic)** | Inicio automático por trigger del RAT | RAT.evaluacion_riesgo = ALTO o MUY_ALTO |

### 4.2 Eventos Intermedios

| Evento | Tipo | Descripción | Duración |
|--------|------|-------------|----------|
| Revisión 24 meses | **Intermediate Timer Event (Boundary)** | Timer para revisión periódica obligatoria | 24 meses desde aprobación |

### 4.3 Eventos de Fin

| Evento | Tipo | Descripción | Condición |
|--------|------|-------------|-----------|
| EIPD aprobado y activo | **End Event (Normal)** | Proceso completado exitosamente | Aprobación por DPO Senior |
| EIPD rechazado | **End Event (Error)** | Proceso terminado por rechazo | Rechazo con comentarios |

---

## 5. DATOS UTILIZADOS

### 5.1 Datos de Entrada (Input)

| Dato | Tipo | Descripción | Origen |
|------|------|-------------|--------|
| rat_id_padre | String | ID del RAT que originó la EIPD | RAT Process |
| categorias_datos | Array | Categorías de datos tratados | RAT Process |
| finalidad | String | Finalidad del tratamiento | RAT Process |
| operaciones | Array | Operaciones específicas a realizar | RAT Process |
| responsable_tratamiento | String | Responsable del tratamiento | RAT Process |

### 5.2 Datos del Proceso

| Dato | Tipo | Descripción | Modo |
|------|------|-------------|------|
| eipd_id | String | Identificador único EIPD | Auto-generado |
| fecha_inicio | DateTime | Fecha inicio elaboración | Auto-registrado |
| fecha_aprobacion | DateTime | Fecha aprobación | Al aprobar |
| fecha_proxima_revision | DateTime | Fecha próxima revisión | Calculado (+24 meses) |
| estado | Enum | Estado actual del EIPD | Sistema |
| nivel_riesgo_inherente | Integer | Nivel riesgo sin controles | Calculado |
| nivel_riesgo_residual | Integer | Nivel riesgo con controles | Calculado |
| version | Integer | Número de versión | Auto-incrementado |
| hash_documento | String | Hash SHA-256 del documento | Al aprobar |

### 5.3 Estados del EIPD

| Estado | Descripción |
|--------|-------------|
| EN_ELABORACION | EIPD en desarrollo por DPO |
| EN_REVISION | EIPD presentado para revisión |
| APROBADO | EIPD aprobada y activa |
| RECHAZADO | EIPD rechazada, requiere correcciones |

### 5.4 Datos de Matrices

| Dato | Tipo | Estructura |
|------|------|------------|
| riesgos_inherentes | Array | [{id, descripcion, activo_afectado, amenaza, vulnerabilidad, probabilidad, impacto, nivel}] |
| controles_existentes | Array | [{id, descripcion, tipo, eficacia}] |
| controles_propuestos | Array | [{id_riesgo, descripcion, tipo, estado_implementacion}] |
| probabilidad | Array | [Integer 1-5] por riesgo |
| impacto | Array | [Integer 0-4] por riesgo |
| riesgo_residual | Array | [Integer] por riesgo post-controles |

---

## 6. SLAS (Service Level Agreements)

| Métrica | SLA | Referencia Legal |
|---------|-----|------------------|
| **EIPD debe completarse ANTES de iniciar tratamiento** | 0 días de operación sin EIPD para riesgo ALTO | Ley 21.719 Art. 15 |
| **Revisión periódica** | Cada 24 meses | Best practice APDP |
| **Decisión sobre consulta previa APDP** | 8 semanas máximo | Si aplica (art. 36 GDPR ref.) |
| **Tiempo máximo elaboración** | 30 días corridos | Internal policy |
| **Tiempo revisión DPO Senior** | 10 días hábiles | Internal policy |
| **Respuesta a rechazo** | 15 días corridos | Internal policy |

---

## 7. RIESGOS DEL PROCESO EIPD

### 7.1 Registro de Riesgos

| ID | Riesgo | Probabilidad | Impacto | Nivel |
|----|--------|--------------|---------|-------|
| EIPD-001 | EIPD no iniciada a tiempo | Media | Alto | ALTO |
| EIPD-002 | Evaluación superficial de riesgos | Baja | Crítico | ALTO |
| EIPD-003 | Controles genéricos sin especificidad | Media | Medio | MEDIO |
| EIPD-004 | Riesgo residual mal calculado | Baja | Alto | MEDIO |
| EIPD-005 | Aprobación sin revisión adecuada | Baja | Alto | MEDIO |
| EIPD-006 | Revisión vencida sin activación | Media | Alto | ALTO |
| EIPD-007 | Controles no implementados post-aprobación | Baja | Alto | MEDIO |
| EIPD-008 | Documentación incompleta para auditoría | Media | Medio | MEDIO |

---

## 8. CONTROLES DEL PROCESO EIPD

### 8.1 Controles por Riesgo

| Riesgo | Control | Tipo | Responsable |
|--------|---------|------|-------------|
| EIPD-001 | Automatización de trigger desde RAT | Preventivo | Sistema |
| EIPD-001 | Alerta temprana 15 días antes de iniciar tratamiento | Detectivo | Sistema |
| EIPD-002 | Checklist obligatorio de evaluación | Preventivo | DPO |
| EIPD-002 | Revisión por DPO Senior de matriz de riesgos | Correctivo | DPO Senior |
| EIPD-003 | Base de datos de controles por categoría de riesgo | Preventivo | Sistema |
| EIPD-003 | Plantillas específicas por tipo de tratamiento | Preventivo | DPO |
| EIPD-004 | Fórmula estandarizada en sistema con validación | Preventivo | Sistema |
| EIPD-004 | Verificación independiente por DPO Senior | Detetivo | DPO Senior |
| EIPD-005 | Circuito de firma digital con secuencia obligatoria | Preventivo | Sistema |
| EIPD-005 | Timebox de 10 días para revisión | Preventivo | Sistema |
| EIPD-006 | Timer con alertas a 30, 15 y 5 días del vencimiento | Detectivo | Sistema |
| EIPD-006 | Bloqueo de tratamiento si revisión vencida | Correctivo | Sistema |
| EIPD-007 | Dashboard de monitoreo de implementación | Detectivo | Sistema |
| EIPD-007 | Auditoría anual de controles implementados | Detectivo | Comité Asesor |
| EIPD-008 | Template con campos obligatorios firmados | Preventivo | Sistema |
| EIPD-008 | Archivo versionado con hash inmutable | Preventivo | Sistema |

---

## 9. KPIS (Key Performance Indicators)

### 9.1 Indicadores de Volumen

| KPI | Descripción | Fórmula | Meta |
|-----|-------------|---------|------|
| EIPD-001 | EIPDs activas | COUNT WHERE estado = 'APROBADO' | > 0 (tracking) |
| EIPD-002 | EIPDs en elaboración | COUNT WHERE estado IN ('EN_ELABORACION', 'EN_REVISION') | < 5 |
| EIPD-003 | Total EIPDs por estado | COUNT GROUP BY estado | Distribución balanceada |

### 9.2 Indicadores de Tiempo

| KPI | Descripción | Fórmula | Meta |
|-----|-------------|---------|------|
| EIPD-004 | Tiempo medio de aprobación | AVG(fecha_aprobacion - fecha_inicio) días | ≤ 30 días |
| EIPD-005 | Tiempo medio en estado EN_REVISION | AVG(fecha_estado_actual - fecha_ingreso_estado) | ≤ 10 días |

### 9.3 Indicadores de Cumplimiento

| KPI | Descripción | Fórmula | Meta |
|-----|-------------|---------|------|
| EIPD-006 | EIPDs con revisión vencida | COUNT WHERE fecha_proxima_revision < HOY AND estado = 'APROBADO' | 0 |
| EIPD-007 | Tratamientos ALTO riesgo sin EIPD | COUNT RAT WHERE riesgo = 'ALTO' AND eipd_id IS NULL | 0 |
| EIPD-008 | Porcentaje de EIPDs aprobadas en primer intento | COUNT estado='APROBADO' WHERE version = 1 / total | ≥ 80% |

### 9.4 Indicadores de Calidad

| KPI | Descripción | Fórmula | Meta |
|-----|-------------|---------|------|
| EIPD-009 | EIPDs con riesgos ALTO/MUY_ALTO residuales | COUNT WHERE nivel_riesgo_residual > 9 | 0 |
| EIPD-010 | Controles propuestos implementados | SUM(implementado) / COUNT(propuestos) | 100% |

---

## 10. ANEXOS

### 10.1 Anexo: Escala de Probabilidad

| Valor | Nivel | Descripción |
|-------|-------|-------------|
| 1 | MUY_BAJA | Casi imposible que ocurra |
| 2 | BAJA | Improbable que ocurra |
| 3 | MEDIA | Posible que ocurra en ciertas circunstancias |
| 4 | ALTA | Probable que ocurra |
| 5 | MUY_ALTA | Ocurrencia muy probable / constante |

### 10.2 Anexo: Escala de Impacto

| Valor | Nivel | Descripción |
|-------|-------|-------------|
| 0 | NINGUNO | Sin impacto identificable |
| 1 | MINIMO | Impacto menor, rápidamente reversible |
| 2 | MODERADO | Impacto moderado, requiere esfuerzo de recuperación |
| 3 | SIGNIFICATIVO | Impacto significativo, recuperación prolongada |
| 4 | CRÍTICO | Impacto crítico, posible daño irreversible |

### 10.3 Anexo: Matriz de Riesgo (Probabilidad × Impacto)

| | NINGUNO(0) | MINIMO(1) | MODERADO(2) | SIGNIFICATIVO(3) | CRÍTICO(4) |
|---|------------|-----------|-------------|------------------|------------|
| **MUY_BAJA(1)** | 0 | 1 | 2 | 3 | 4 |
| **BAJA(2)** | 0 | 2 | 4 | 6 | 8 |
| **MEDIA(3)** | 0 | 3 | 6 | 9 | 12 |
| **ALTA(4)** | 0 | 4 | 8 | 12 | 16 |
| **MUY_ALTA(5)** | 0 | 5 | 10 | 15 | 20 |

### 10.4 Anexo: Clasificación de Niveles

| Rango | Nivel | Acción Requerida |
|-------|-------|------------------|
| 1-2 | MUY_BAJO | Aceptación de riesgo, documentar |
| 3-4 | BAJO | Monitoreo, revisión periódica |
| 5-9 | MEDIO | Controles requeridos |
| 10-15 | ALTO | Controles obligatorios, aprobación DPO Senior |
| 16-20 | MUY_ALTO | Consulta previa a APDP recomendada |

---

**Documento generado por Custodio Architecture Team**  
**Plataforma Custodio SaaS - Cumplimiento Ley 21.719**
