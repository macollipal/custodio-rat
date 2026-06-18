# PROCESO 6: Gestión de Encargados de Tratamiento

**Plataforma:** Custodio SaaS  
**Normativa:** Ley 21.719 Art. 21 - Protección de Datos Personales Chile  
**Versión:** 1.0  
**Fecha:** 2026-06-18

---

## 1. EXPLICACIÓN FUNCIONAL

El proceso de Gestión de Encargados de Tratamiento gestiona el ciclo de vida completo de los terceros que trattamiento datos personales por cuenta del responsable (controlador). Este proceso es **obligatorio** según el Art. 21 de la Ley 21.719, que establece que el responsable debe garantizar que el encargado proporcione garantías suficientes para implementar medidas técnicas y organizativas adecuadas.

**Objetivos del proceso:**
- Onboarding controlado de nuevos encargados de tratamiento
- Gestión contractual con cláusulas obligatorias según Art. 21.3
- Revisión periódica de cumplimiento (caducidad máxima 24 meses)
- Renovación o terminación oportuna de relaciones
- Control de subcontratación
- Desvinculación segura con certificación de eliminación de datos

**Base legal:** Art. 21 Ley 21.719 - El responsable del tratamiento únicamente recurrió a encargados de tratamiento que ofrezcan garantías suficientes para implementar medidas técnicas y organizativas de seguridad.

---

## 2. BPMN TEXTUAL DETALLADO

### 2.1 ALTA DE ENCARGADO

| Elemento | Descripción |
|----------|-------------|
| **Start Event** | Nueva relación con encargado de tratamiento |
| **Lane** | DPO |
| **TareaUsuario** | Solicitar alta encargado |
| **Campos** | `nombre_encargado`, `rut/nit`, `pais`, `actividades_tratamiento`, `categorias_datos`, `medidas_seguridad_planificadas` |

| Elemento | Descripción |
|----------|-------------|
| **TareaSistema** | Verificar unicidad encargado |
| **Lane** | Sistema |
| **Validación** | Verificar que no exista otro encargado con mismo RUT/NIT |

| Elemento | Descripción |
|----------|-------------|
| **TareaUsuario** | Evaluar idoneidad del encargado |
| **Lane** | DPO |
| **Criterios** | `certificaciones` (ISO 27001, ISO 27701), `historial`, `referencias`, `ubicación_geográfica` (adequacy) |

| Elemento | Descripción |
|----------|-------------|
| **GatewayExclusivo** | ¿Encargado idóneo? |
| **Ramas** | No → Solicitar información adicional; Sí → Continúa al contrato |

**Ruta alternativa (No Idóneo):**
- TareaSistema: Solicitar información adicional
- Vuelve a: Evaluar idoneidad del encargado

---

### 2.2 CONTRATO

| Elemento | Descripción |
|----------|-------------|
| **TareaUsuario** | Elaborar proyecto de encargo de tratamiento |
| **Lane** | DPO |
| **Cláusulas mínimas Art. 21.3** | Instrucciones de tratamiento, confidencialidad, medidas de seguridad, prohibición de subencargados sin autorización, asistencia con ejercicio de derechos, devolución/eliminación al finalizar, derechos de auditoría |

| Elemento | Descripción |
|----------|-------------|
| **TareaUsuario** | Revisar proyecto con área legal |
| **Lane** | Área Legal |
| **Validación** | Verificación jurídica del contrato |

| Elemento | Descripción |
|----------|-------------|
| **TareaUsuario** | Remitir contrato a encargado |
| **Lane** | DPO |
| **Medio** | Email o plataforma segura |

| Elemento | Descripción |
|----------|-------------|
| **GatewayExclusivo** | ¿Encargado acepta condiciones? |
| **Ramas** | No → Negociación; Sí → Continúa |

**Ruta alternativa (No acepta):**
- Negociación de términos
- Vuelve a: Remitir contrato a encargado

| Elemento | Descripción |
|----------|-------------|
| **TareaUsuario** | Firmar contrato |
| **Lane** | DPO + Encargado externo |
| **Método** | Firma digital |

| Elemento | Descripción |
|----------|-------------|
| **TareaSistema** | Registrar contrato |
| **Lane** | Sistema |
| **Estado** | VIGENTE |
| **Campos** | `fecha_inicio`, `fecha_vencimiento` |

| Elemento | Descripción |
|----------|-------------|
| **TareaSistema** | Verificar medidas de seguridad |
| **Lane** | Sistema |
| **Checklist** | Encriptación, control_acceso, backup, incident_management |

| Elemento | Descripción |
|----------|-------------|
| **TareaSistema** | Vincular a RAT correspondientes |
| **Lane** | Sistema |
| **Acción** | Actualizar `RAT.encargado_id` para actividades relevantes |

| Elemento | Descripción |
|----------|-------------|
| **TareaSistema** | Programar recordatorio renovación |
| **Lane** | Sistema |
| **Timer** | 30 días antes del vencimiento |

| Elemento | Descripción |
|----------|-------------|
| **End Event** | Encargado de tratamiento activo |

---

### 2.3 REVISIÓN CONTRACTUAL

| Elemento | Descripción |
|----------|-------------|
| **Intermediate Timer Event** | Revisión contractual: 24 meses |
| **Trigger** | Automático desde fecha_inicio |
| **Fundamento** | Requisito Art. 21 - verificación periódica |

| Elemento | Descripción |
|----------|-------------|
| **TareaUsuario** | Revisar cumplimiento de obligaciones |
| **Lane** | DPO |
| **Verificaciones** | Instrucciones seguidas, medidas implementadas, subencargados no autorizados, evidencias preservadas |

| Elemento | Descripción |
|----------|-------------|
| **TareaUsuario** | Solicitar certificación cumplimiento |
| **Lane** | DPO |
| **Destinatario** | Encargado externo |

| Elemento | Descripción |
|----------|-------------|
| **GatewayExclusivo** | ¿Encargado cumple? |
| **Ramas** | No → Flujo de TERMINACIÓN; Sí → Continúa |

| Elemento | Descripción |
|----------|-------------|
| **TareaSistema** | Actualizar fecha_ultima_revision |
| **Lane** | Sistema |

| Elemento | Descripción |
|----------|-------------|
| **TareaSistema** | Documentar en bitácora |
| **Lane** | Sistema |

---

### 2.4 RENOVACIÓN

| Elemento | Descripción |
|----------|-------------|
| **Timer Intermediate Event** | 30 días antes vencimiento |
| **Trigger** | Automático |

| Elemento | Descripción |
|----------|-------------|
| **TareaSistema** | Notificar proximidad vencimiento |
| **Lane** | Sistema de Correo |
| **Destinatarios** | DPO, Encargado |

| Elemento | Descripción |
|----------|-------------|
| **TareaUsuario** | Evaluar desempeño del encargado |
| **Lane** | DPO |
| **Criterios** | Incidentes, resultados de auditoría, tiempo de respuesta, cumplimiento |

| Elemento | Descripción |
|----------|-------------|
| **GatewayExclusivo** | ¿Renovar contrato? |
| **Ramas** | No → Flujo TERMINACIÓN; Sí → Continúa |

| Elemento | Descripción |
|----------|-------------|
| **TareaUsuario** | Renegociar términos si necesario |
| **Lane** | DPO + Área Legal |

| Elemento | Descripción |
|----------|-------------|
| **TareaUsuario** | Firmar renovación |
| **Lane** | DPO + Encargado |

| Elemento | Descripción |
|----------|-------------|
| **TareaSistema** | Actualizar fechas vigencia |
| **Lane** | Sistema |

| Elemento | Descripción |
|----------|-------------|
| **TareaSistema** | Actualizar recordatorio |
| **Lane** | Sistema |
| **Acción** | Nuevo recordatorio 30 días |

---

### 2.5 TERMINACIÓN

| Elemento | Descripción |
|----------|-------------|
| **Start Event** | Decisión de terminar encargo |
| **Triggers** | Revisión fallida, decisión de no renovar, breach contractual |

| Elemento | Descripción |
|----------|-------------|
| **TareaUsuario** | Documentar motivos de terminación |
| **Lane** | DPO |

| Elemento | Descripción |
|----------|-------------|
| **TareaUsuario** | Verificar estado de datos |
| **Lane** | DPO |
| **Verificación** | Datos devueltos, datos eliminados |

| Elemento | Descripción |
|----------|-------------|
| **GatewayExclusivo** | ¿Datos en orden? |
| **Ramas** | No → Solicitar regularización; Sí → Continúa |

| Elemento | Descripción |
|----------|-------------|
| **TareaUsuario** | Solicitar certificado de eliminación |
| **Lane** | DPO |
| **Destinatario** | Encargado |

| Elemento | Descripción |
|----------|-------------|
| **TareaSistema** | Recibir certificación eliminación |
| **Lane** | Sistema |

| Elemento | Descripción |
|----------|-------------|
| **TareaSistema** | Actualizar RAT |
| **Lane** | Sistema |
| **Acción** | Desvincular encargado, marcar actividades sin encargado |

| Elemento | Descripción |
|----------|-------------|
| **TareaSistema** | Archivar documentación |
| **Lane** | Sistema |
| **Estado** | TERMINADO |

| Elemento | Descripción |
|----------|-------------|
| **TareaSistema** | Notificar terminación a sistemas |
| **Lane** | Sistema de Correo |

| Elemento | Descripción |
|----------|-------------|
| **End Event** | Relación con encargado finalizada |

---

### 2.6 SUBCONTRATACIÓN

| Elemento | Descripción |
|----------|-------------|
| **Start Event (Signal)** | Solicitud subcontratación |
| **Origen** | Encargado externo |

| Elemento | Descripción |
|----------|-------------|
| **TareaUsuario** | DPO evalúa subcontratista |
| **Lane** | DPO |
| **Criterios** | Mismos que onboarding inicial |

| Elemento | Descripción |
|----------|-------------|
| **GatewayExclusivo** | ¿Autoriza subcontratación? |
| **Ramas** | No → Notificar rechazo; Sí → Continúa |

| Elemento | Descripción |
|----------|-------------|
| **TareaUsuario** | Actualizar contrato con subencargado |
| **Lane** | DPO |

| Elemento | Descripción |
|----------|-------------|
| **TareaSistema** | Registrar subencargado |
| **Lane** | Sistema |
| **Campo** | `parent_id = encargado_principal` |

---

## 3. TABLA RACI

| Actividad | DPO | Área Legal | Encargado Externo | Sistema | Sistema de Correo |
|-----------|-----|------------|-------------------|---------|-------------------|
| Solicitar alta encargado | R | - | - | - | - |
| Verificar unicidad | - | - | - | R/A | - |
| Evaluar idoneidad | R/A | C | I | - | - |
| Elaborar proyecto contrato | R | C | - | - | - |
| Revisar con área legal | C | R/A | - | - | - |
| Remitir contrato | R | - | - | - | - |
| Aceptar condiciones | I | C | R/A | - | - |
| Firmar contrato | R | - | A | - | - |
| Registrar contrato | - | - | - | R/A | - |
| Verificar medidas seguridad | C | - | - | R/A | - |
| Vincular a RAT | - | - | - | R/A | - |
| Programar recordatorio | - | - | - | R/A | - |
| Revisión contractual 24m | I | - | - | R/A | I |
| Revisar cumplimiento | R/A | C | I | - | - |
| Solicitar certificación | R | - | - | - | - |
| Evaluar desempeño | R/A | C | I | - | - |
| Renegociar términos | R | A | C | - | - |
| Firmar renovación | R | - | A | - | - |
| Documentar terminación | R/A | C | I | - | - |
| Verificar estado datos | R/A | - | I | - | - |
| Solicitar certificado eliminación | R | - | - | - | - |
| Recibir certificación | - | - | - | R/A | - |
| Actualizar RAT | - | - | - | R/A | - |
| Archivar documentación | - | - | - | R/A | - |
| Evaluar subcontratista | R/A | C | I | - | - |

**Leyenda:** R=Responsable, A=Accountable, C=Consulted, I=Informed

---

## 4. EVENTOS

### 4.1 Start Events

| ID | Nombre | Tipo | Descripción |
|----|--------|------|-------------|
| START_ALTA | Nueva relación | None | Inicio del proceso de alta |
| START_TERMINACION | Decisión de terminar | None | Origen de la terminación |
| START_SUBCONTRATACION | Solicitud subcontratación | Signal | Cuando encargado solicita subcontratar |

### 4.2 Intermediate Events

| ID | Nombre | Tipo | Descripción |
|----|--------|------|-------------|
| TIMER_RENOVACION | 30 días antes vencimiento | Timer | Recordatorio de renovación |
| TIMER_REVISION | Revisión 24 meses | Timer | Verificación periódica obligatoria |

### 4.3 End Events

| ID | Nombre | Descripción |
|----|--------|-------------|
| END_ACTIVO | Encargado activo | Proceso exitoso, encargado operativo |
| END_TERMINADO | Relación terminada | Relación concluida correctamente |

---

## 5. DATOS UTILIZADOS

### 5.1 Entidad: Encargado

```json
{
  "encargado_id": "UUID",
  "nombre": "string",
  "rut_nit": "string",
  "pais": "string",
  "actividades": ["string"],
  "categorias_datos": ["string"],
  "medidas_seguridad": ["string"],
  "estado": "ACTIVO|PENDIENTE|TERMINADO|EN_REVISIÓN",
  "fecha_inicio": "datetime",
  "fecha_vencimiento": "datetime",
  "fecha_ultima_revision": "datetime",
  "subcontratistas": ["encargado_id"],
  "padre_id": "encargado_id|null",
  "hash_contrato": "string",
  "RAT_ids_asociados": ["RAT_id"]
}
```

### 5.2 Entidad: Contrato

```json
{
  "contrato_id": "UUID",
  "encargado_id": "UUID",
  "estado": "BORRADOR|EN_REVISIÓN|VIGENTE|TERMINADO",
  "fecha_firma": "datetime",
  "fecha_inicio": "datetime",
  "fecha_vencimiento": "datetime",
  "cláusulas_art21": {
    "instrucciones": "boolean",
    "confidencialidad": "boolean",
    "medidas_seguridad": "boolean",
    "subencargados": "boolean",
    "asistencia_derechos": "boolean",
    "devolucion_eliminacion": "boolean",
    "derechos_auditoria": "boolean"
  },
  "hash_documento": "string"
}
```

### 5.3 Data Objects

| Nombre | Tipo | Descripción |
|--------|------|-------------|
| SolicitudAlta | DataObject | Documento de solicitud de alta |
| ContratoEncargo | DataObject | Contrato firmado |
| CertificacionCumplimiento | DataObject | Certificación de cumplimiento |
| CertificadoEliminacion | DataObject | Certificado de eliminación de datos |

---

## 6. SLAS

| ID | Descripción | Plazo | Responsable |
|----|-------------|-------|-------------|
| SLA-ENC-001 | Encargado debe contar con contrato antes de procesar datos | 0 días (inmediato) | DPO |
| SLA-ENC-002 | Revisión contractual obligatoria | 24 meses | DPO + Sistema |
| SLA-ENC-003 | Notificación de vencimiento | 30 días antes | Sistema de Correo |
| SLA-ENC-004 | Respuesta a solicitud subcontratación | 15 días | DPO |
| SLA-ENC-005 | Renovación de contrato | Antes del vencimiento | DPO + Área Legal |

---

## 7. RIESGOS

| ID | Riesgo | Probabilidad | Impacto | Control Mitigador |
|----|--------|---------------|---------|-------------------|
| ENC-001 | Encargado opera sin contrato vigente | Baja | Alto | Verificación automática pre-procesamiento |
| ENC-002 | Contrato incompleto (falta Art. 21.3) | Media | Alto | Checklist obligatorio en elaboração |
| ENC-003 | Subcontratación no autorizada | Media | Alto | Registro y evaluación obligatoria |
| ENC-004 | Medidas de seguridad insuficientes | Baja | Alto | Evaluación periódica de idoneidad |
| ENC-005 | Certificación de cumplimiento falsa | Baja | Muy Alto | Verificación de autenticidad |
| ENC-006 | Datos no devueltos/eliminados al terminar | Baja | Alto | Verificación obligatoria pre-terminación |
| ENC-007 | Encargado fantasma (sin existencia real) | Baja | Muy Alto | Verificación de existencia legal |
| ENC-008 | Renovación automática no deseada | Baja | Medio | Decisión explícita requerida |
| ENC-009 | RAT desactualizado tras cambios | Media | Medio | Sincronización automática |
| ENC-010 | Incumplimiento no detectado | Media | Alto | Revisiones periódicas obligatorias |

---

## 8. CONTROLES Y KPIS

### 8.1 KPIs

| KPI | Descripción | Meta | Frecuencia |
|-----|-------------|------|------------|
| ENC-KPI-001 | Encargados con contrato vigente | 100% | Mensual |
| ENC-KPI-002 | Encargados pendientes renovación (<30 días) | <10% | Semanal |
| ENC-KPI-003 | Encargados con revisión vencida (>24 meses) | 0% | Mensual |
| ENC-KPI-004 | RAT sin encargado vinculado | <5% | Mensual |
| ENC-KPI-005 | Tiempo medio de onboarding | <30 días | Trimestral |
| ENC-KPI-006 | Tasa de renovación | >80% | Anual |

### 8.2 Controles

| Control | Descripción | Frecuencia |
|---------|-------------|------------|
| CTRL-ENC-001 | Verificación de contrato vigente antes de procesar | Continuo |
| CTRL-ENC-002 | Alerta automática 30 días antes del vencimiento | Automático |
| CTRL-ENC-003 | Revisión de subcontratistas registrados | Semestral |
| CTRL-ENC-004 | Validación de certificaciones presentadas | Anual |
| CTRL-ENC-005 | Auditoría de medidas de seguridad implementadas | Anual |

---

## 9. DIAGRAMA BPMN

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          GESTIÓN ENCARGADOS                             │
│  ┌─────────────┬─────────────┬─────────────────┬────────────────────┐   │
│  │     DPO     │  Área Legal │ Encargado Externo│      Sistema      │   │
│  └─────────────┴─────────────┴─────────────────┴────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────┐
                    │   START: Nueva relación   │
                    └───────────────────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────┐
                    │ Solicitar alta encargado  │
                    │      (User Task)          │
                    └───────────────────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────┐
                    │ Verificar unicidad        │
                    │     (Service Task)        │
                    └───────────────────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────┐
                    │ Evaluar idoneidad         │
                    │      (User Task)          │
                    └───────────────────────────┘
                                    │
                                    ▼
                              ╔═══════╗
                              ║ Idóneo?║
                              ╚═══════╝
                             /         \
                           No          Yes
                           /             \
                          ▼               ▼
            ┌──────────────┐             │
            │ Solicitar    │             │
            │ info adicional             │
            └──────────────┘             │
                   │                     │
                   └─────────┬───────────┘
                               │
                               ▼
                    ┌───────────────────────────┐
                    │ Elaborar proyecto        │
                    │    (User Task)           │
                    └───────────────────────────┘
                               │
                               ▼
                    ┌───────────────────────────┐
                    │ Revisar c/área legal      │
                    │      (User Task)          │
                    └───────────────────────────┘
                               │
                               ▼
                    ┌───────────────────────────┐
                    │ Remitir contrato          │
                    │      (User Task)          │
                    └───────────────────────────┘
                               │
                               ▼
                          ╔═════════╗
                          ║ Acepta? ║
                          ╚═════════╝
                         /           \
                       No            Yes
                       /              \
                      ▼                │
              ┌────────────┐            │
              │ Negociação │            │
              └────────────┘            │
                     │                   │
                     └───────┬───────────┘
                             │
                             ▼
                    ┌───────────────────────────┐
                    │ Firmar contrato           │
                    │  (User Task - both)       │
                    └───────────────────────────┘
                             │
                             ▼
                    ┌───────────────────────────┐
                    │ Registrar contrato        │
                    │     (Service Task)        │
                    └───────────────────────────┘
                             │
                             ▼
                    ┌───────────────────────────┐
                    │ Verificar medidas seg.    │
                    │     (Service Task)        │
                    └───────────────────────────┘
                             │
                             ▼
                    ┌───────────────────────────┐
                    │ Vincular a RAT            │
                    │     (Service Task)        │
                    └───────────────────────────┘
                             │
                             ▼
                    ┌───────────────────────────┐
                    │ Programar recordatorio   │
                    │     (Service Task)        │
                    └───────────────────────────┘
                             │
                             ▼
                    ┌───────────────────────────┐
                    │   END: Encargado activo   │
                    └───────────────────────────┘
```

---

**Documento generado:** 2026-06-18  
**Versión:** 1.0  
**Autor:** Custodio Platform
