# Caso de Uso 2: Crear Primer Proceso RAT

## Objetivo
Registrar un tratamiento de datos personales en el RAT de la organización.

## Caso real
Una clínica guarda: nombre, RUT, teléfono, fichas médicas. Necesita documentarlo legalmente conforme a la Ley 21.719.

## Paso a paso

### Paso 1 — Ir a RAT
- El usuario va al menú lateral: **"Procesos RAT"**
- Click en el botón: **"+ Nuevo proceso"**
- Resultado: se abre el wizard de 4 pasos

### Paso 2 — Wizard paso 1: Identificación
- El usuario completa:
  - Nombre del proceso: `"Gestión pacientes"`
  - Categoría de titulares: `"Pacientes"`
  - Fuente de los datos: `"Directamente del titular"`
  - Destinatarios / Encargados: `"Proveedor de sistema de fichas médicas"`
- Resultado: existe una actividad identificada

### Paso 3 — Wizard paso 2: Datos tratados
- El usuario define:
  - Categoría de datos: `"Datos identificativos (nombre, RUT, teléfono), fichas médicas"`
  - Marca **datos sensibles**: `"Salud (física o mental)"`
  - Opcional: biométricos, decisiones automatizadas
- Resultado: sistema detecta alto riesgo → sugiere EIPD obligatoria

### Paso 4 — Wizard paso 3: Finalidad y ley
- El usuario completa:
  - Finalidad: `"Atención médica integral,历史的diagnóstico y tratamiento"`
  - Base legal: `"Ejecución de contrato"` (Art. 13 b)
  - Plazo de retención: `"10 años desde último contacto (norma sanitaria)"`

### Paso 5 — Wizard paso 4: Almacenamiento y transferencias
- El usuario completa:
  - Medidas de seguridad: `"Cifrado AES-256, acceso por roles, backup diario"`
  - Encargados externos: `"Proveedor de sistema de fichas médicas"`
  - ¿Tiene contrato de encargado?: `"Sí"`

## Qué hace el sistema internamente

Al guardar el RAT, el sistema:

1. **Calcula completitud** → porcentaje de campos completados
2. **Genera alertas de auditoría** → basadas en flags activados
3. **Detecta nivel de riesgo** → crítico si tiene datos sensibles + EIPD
4. **Sugiere EIPD** → si hay datos sensibles de salud o biométricos
5. **Registra auditoría** → crea log de creación con usuario y timestamp
6. **Calcula estado** → `completo` si los 7 campos mínimos están llenos

## Campos completados en este caso

| Campo | Valor |
|-------|-------|
| nombre_proceso | "Gestión pacientes" |
| categoria_titulares | "Pacientes" |
| fuente_datos | "Directamente del titular" |
| categoria_datos | "Datos identificativos, fichas médicas" |
| datos_sensibles | true |
| tipo_dato_sensible | "Salud (física o mental)" |
| finalidad | "Atención médica integral..." |
| base_legal | "Ejecución de contrato" |
| plazo_retencion | "10 años..." |
| medidas_seguridad | "Cifrado AES-256..." |
| nombre_encargado | "Proveedor de sistema de fichas" |
| tiene_contrato_encargado | true |
| evaluacion_impacto | true (sugerido por el sistema) |

## Alertas generadas automáticamente

- ⚠️ Datos sensibles de salud → base legal expresa requerida
- 📋 EIPD requerida para datos sensibles de salud
- 📄 Encargado sin contrato (si no se especifica)

## Diagrama de flujo

```
┌──────────────────┐
│  Procesos RAT    │
│  /rat            │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐     ┌─────────────────┐
│  Wizard paso 1   │────►│  Wizard paso 2  │
│  Identificación  │     │  Datos tratados │
└─────────────────┘     └────────┬────────┘
                                  │
                                  ▼ (datos sensibles → EIPD sugerida)
                         ┌─────────────────┐
                         │  Wizard paso 3  │
                         │  Finalidad y ley│
                         └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │  Wizard paso 4  │
                         │  Transferencias │
                         └────────┬────────┘
                                  │
                                  ▼
                          ┌──────────────┐
                          │  api.crearRat │
                          │  + auditoría  │
                          └───────┬───────┘
                                  │
                                  ▼
                          ┌──────────────┐
                          │   Dashboard   │
                          │  RAT creado   │
                          └──────────────┘
```

## Validaciones del wizard

| Campo | Validación |
|-------|------------|
| nombre_proceso | Obligatorio, no vacío |
| categoria_titulares | Obligatorio (Art. 16 — campo mínimo) |
| fuente_datos | Obligatorio |
| categoria_datos | Obligatorio |
| finalidad | Obligatorio |
| base_legal | Obligatorio |
| plazo_retencion | Obligatorio |
| email_dpo (empresa) | Obligatorio, formato email |
| RUT | Algoritmo dígito verificador chileno |

## Endpoint involucrado

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/rats/` | Crea un nuevo RAT |
| GET | `/rats/` | Lista RATs de la empresa |
| GET | `/rats/{id}` | Obtiene un RAT por ID |
| POST | `/rats/{id}/auditoria` | Registra auditoría |
| GET | `/rats/sugerencias/tipos` | Lista tipos de proceso para sugerencias |
| POST | `/rats/sugerencias` | Obtiene sugerencias automáticas |

## Estados del RAT

| Estado | Condición |
|--------|-----------|
| `borrador` | Faltan campos obligatorios |
| `completo` | Los 7 campos mínimos están llenos |
| `en_revision` | En proceso de revisión periódica |
| `aprobado` | Aprobado por el DPO |