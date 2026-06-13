# Caso de Uso 3: Uso de Plantillas Inteligentes

## Objetivo
Crear un proceso RAT de forma rápida utilizando plantillas predefinidas que el sistema provee automáticamente.

## Caso real
Una empresa pequeña no sabe cómo llenar un RAT. El usuario crea un nuevo proceso y elige una plantilla del listado: videovigilancia, empleados, marketing, pacientes, etc. El sistema prellena automáticamente: finalidad, bases legales, riesgos y categorías.

## Paso a paso

### Paso 1 — Ir a RAT
- El usuario va al menú lateral: **"Procesos RAT"**
- Click en el botón: **"+ Nuevo proceso"**
- Resultado: se abre el wizard de 4 pasos

### Paso 2 — Elegir plantilla inteligente
- En el **Paso 1** del wizard, el usuario ve el bloque **"Sugerencias inteligentes"**
- Selecciona del dropdown un tipo de proceso, por ejemplo: `"Videovigilancia"`
- Click en **"Aplicar"**
- Resultado: el sistema prellena los campos automáticamente

### Campos prellenados por la plantilla

| Campo | Valor prellenado |
|-------|-----------------|
| categoria_datos | "Imágenes y videos de personas en espacios físicos" |
| categoria_titulares | "Personas presentes en las instalaciones vigiladas" |
| finalidad | "Seguridad de instalaciones y protección de bienes propios" |
| base_legal | "Interés legítimo" |
| plazo_retencion | "30 días desde la grabación" |
| datos_sensibles | false |
| evaluacion_impacto | false |
| decisiones_automatizadas | false |
| observacion | (alerta sobre señalética y limitaciones de uso) |

### Paso 3 — Completar identificación
- El usuario completa solo los campos que faltan:
  - Nombre del proceso: `"Cámaras de seguridad casa matriz"`
  - Fuente de datos: `"Cámaras de seguridad"`
  - Destinatarios: `"Empresa de vigilancia externalizada"`

### Paso 4 — Revisar resto del wizard
- El sistema ya sugiere los flags correctos según la plantilla
- El usuario revisa y completa solo lo necesario
- Resultado: RAT creado con mucho menos esfuerzo

## Plantillas disponibles

| Plantilla | Base legal | Datos sensibles | EIPD |
|-----------|------------|:----------------:|:----:|
| clientes web | Ejecución de contrato | No | No |
| empleados | Obligación legal | Sí (salud) | No |
| control biométrico asistencia | Obligación legal | **Sí (biométricos)** | **Sí** |
| proveedores | Ejecución de contrato | No | No |
| postulantes | Consentimiento | No | No |
| **pacientes** | Interés vital del titular | **Sí (salud)** | **Sí** |
| menores de edad | Consentimiento | Sí | **Sí** |
| marketing | Consentimiento | No | No |
| videovigilancia | Interés legítimo | No | No |
| socios o accionistas | Obligación legal | No | No |
| contabilidad y facturación | Obligación legal | No | No |
| evaluación de desempeño | Interés legítimo | No | No |
| riesgos laborales | Obligación legal | Sí (salud) | No |

## Alias de búsqueda

El sistema también reconoce sinónimos:

| Alias | Busca |
|-------|-------|
| "cámaras", "cctv", "vigilancia" | videovigilancia |
| "rrhh", "recursos humanos", "trabajador" | empleados |
| "clinica", "hospital", "salud" | pacientes |
| "biometría", "huella dactilar" | control biométrico asistencia |
| "SII", "facturas", "contabilidad" | contabilidad y facturación |
| "mutual", "accidentes", "SST" | riesgos laborales |
| "menor", "niños" | menores de edad |

## Qué prellena el sistema automáticamente

| Campo | ¿Se prellena? |
|-------|:--------------:|
| nombre_proceso | ❌ (usuario lo completa) |
| categoria_titulares | ✅ |
| fuente_datos | ❌ |
| destinatarios | ❌ |
| categoria_datos | ✅ |
| datos_sensibles | ✅ |
| tipo_dato_sensible | ✅ (si aplica) |
| evaluacion_impacto | ✅ (si aplica) |
| decisiones_automatizadas | ✅ |
| finalidad | ✅ |
| base_legal | ✅ |
| plazo_retencion | ✅ |
| medidas_seguridad | ❌ |
| transferencia_internacional | ❌ |
| nombre_encargado | ❌ |

## Valor real de esta funcionalidad

- **Reduce complejidad legal** → el usuario no necesita conocer la ley para empezar
- **Ahorra tiempo** → de ~20 minutos a ~3 minutos por RAT
- **Minimiza errores** → las bases legales y plazos ya cumplen la normativa
- **Detecta riesgos** → las plantillas ya activan los flags de sensible/EIPD correctos

## Diagrama de flujo

```
┌──────────────────────┐
│  Wizard paso 1       │
│  Identificación      │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────────┐
│  Selecciona plantilla    │◄────────┐
│  "Videovigilancia"       │         │
└──────────┬───────────────┘         │
           │                         │
           ▼                         │
┌──────────────────────────┐         │
│  Click "Aplicar"         │         │
│  api.sugerirRat()        │         │
└──────────┬───────────────┘         │
           │                         │
           ▼                         │
┌──────────────────────────┐         │
│  Campos prellenados      │         │
│  + Observación legal      │         │
└──────────┬───────────────┘         │
           │                         │
           ▼                         │
     ¿Completar más?                 │
        SÍ │ NO                      │
           │ │                       │
           ▼ └───────────────────────┘
```

## Endpoint involucrado

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/rats/sugerencias/tipos` | Lista todos los tipos disponibles |
| POST | `/rats/sugerencias` | Obtiene sugerencias para un tipo |

## Alerta legal que muestra cada plantilla

Después de aplicar una plantilla, el sistema muestra una alerta contextual. Por ejemplo:

**Videovigilancia:**
> "Interés legítimo requiere test de 3 pasos documentado. Colocar señalética visible antes del área vigilada."

**Pacientes:**
> "Datos de salud: categoría sensible del Art. 2 letra g. Requiere EIPD y medidas de seguridad reforzadas."

**Control biométrico:**
> "IMPORTANTE — Art. 16 BIS: Los datos biométricos destinados a identificar inequívocamente a una persona requieren EIPD previa. El consentimiento del empleado NO es base válida en contextos laborales."