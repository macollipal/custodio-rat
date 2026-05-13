# Casos de Uso — Custodio RAT Manager

## Ley 21.719 · Chile

---

## Caso de Uso 1: Onboarding — Primera empresa

### Objetivo
Dejar configurada la empresa responsable del tratamiento para comenzar el cumplimiento de la Ley 21.719.

### Paso a paso

**Paso 1 — Login**
- El usuario entra al sistema (`http://localhost:3000`)
- Ingresa usuario y contraseña
- Resultado: entra al sistema

**Paso 2 — Redirección a onboarding**
- El sistema detecta que no hay empresas registradas
- Redirige automáticamente a `/onboarding`
- Resultado: el usuario ve la pantalla de configuración inicial

**Paso 3 — Crear empresa**
- El usuario completa:
  - Razón social (obligatorio)
  - RUT con validación de dígito verificador (obligatorio)
  - Nombre del DPO (opcional)
  - Email del DPO (obligatorio)
- Resultado: empresa queda registrada en el sistema

**Paso 4 — Selección automática**
- El sistema selecciona automáticamente la empresa recién creada como activa
- Redirige al dashboard
- Resultado: todos los RAT se asociarán a esa empresa

### Flujo actual de la app

```
Login (/login)
    ↓
api.listarEmpresas()
    ↓
¿Hay empresas?
  → SÍ → /dashboard (AppLayout auto-selecciona la primera)
  → NO → /onboarding
           ↓
     Form: razón social, RUT, DPO, email DPO
           ↓
     api.crearEmpresa()
           ↓
     setCompany(empresa)
     router.push('/dashboard')
```

### Archivos involucrados

| Archivo | Cambio |
|---------|--------|
| `app/login/page.tsx` | Redirige a `/onboarding` si no hay empresas |
| `app/(app)/layout.tsx` | Redirige a `/onboarding` si no hay empresa activa |
| `app/onboarding/page.tsx` | **NUEVO** — pantalla de bienvenida y creación de empresa |
| `components/ui/validation.ts` | Validador RUT chileno con dígito verificador |

### Validaciones implementadas

- RUT: algoritmo dígito verificador chileno (DV)
- Campos obligatorios: razón social, RUT, email del DPO
- El campo DPO nombre es opcional

---

## Caso de Uso 2: Crear Primer Proceso RAT

### Objetivo
Registrar un tratamiento de datos personales en el RAT de la organización.

### Caso real
Una clínica guarda: nombre, RUT, teléfono, fichas médicas. Necesita documentarlo legalmente conforme a la Ley 21.719.

### Paso a paso

**Paso 1 — Ir a RAT**
- El usuario va al menú lateral: **"Procesos RAT"**
- Click en el botón: **"+ Nuevo proceso"**
- Resultado: se abre el wizard de 4 pasos

**Paso 2 — Wizard paso 1: Identificación**
- El usuario completa:
  - Nombre del proceso: `"Gestión pacientes"`
  - Categoría de titulares: `"Pacientes"`
  - Fuente de los datos: `"Directamente del titular"`
  - Destinatarios: `"Proveedor de sistema de fichas médicas"`
- Resultado: actividad identificada

**Paso 3 — Wizard paso 2: Datos tratados**
- El usuario define:
  - Categoría de datos: `"Datos identificativos, fichas médicas"`
  - Marca **datos sensibles**: `"Salud (física o mental)"`
- Resultado: sistema detecta alto riesgo → sugiere EIPD obligatoria

**Paso 4 — Wizard paso 3: Finalidad y ley**
- El usuario completa:
  - Finalidad: `"Atención médica integral"`
  - Base legal: `"Ejecución de contrato"`
  - Plazo de retención: `"10 años"`

**Paso 5 — Wizard paso 4: Almacenamiento y transferencias**
- El usuario completa:
  - Medidas de seguridad: `"Cifrado AES-256"`
  - Encargados externos: `"Proveedor de sistema de fichas médicas"`
  - ¿Tiene contrato de encargado?: `"Sí"`

### Qué hizo el sistema internamente

1. **Calculó completitud** → porcentaje de campos
2. **Generó alertas de auditoría** → datos sensibles de salud
3. **Detecto nivel de riesgo** → crítico (datos sensibles + EIPD)
4. **Sugirió EIPD** → obligatorio para datos de salud
5. **Registró auditoría** → log de creación con usuario

### Archivo del caso de uso

→ `CASO_02_Crear_Primer_Proceso_RAT.md`

---

## Caso de Uso 3: Uso de Plantillas Inteligentes

### Objetivo
Crear un RAT rápido utilizando plantillas predefinidas que prellenan campos automáticamente.

### Caso real
Empresa pequeña no sabe cómo llenar el RAT. Elige plantilla: videovigilancia, empleados, marketing, pacientes, etc.

### Paso a paso

**Paso 1 — Ir a RAT**
- Click en **"+ Nuevo proceso"**

**Paso 2 — Elegir plantilla**
- En paso 1 del wizard, dropdown **"Sugerencias inteligentes"**
- Selecciona: `"Videovigilancia"`, `"Pacientes"`, `"Empleados"`, etc.
- Click **"Aplicar"**
- Resultado: campos prellenados + observación legal

### Qué prellena el sistema

| Campo | ¿Prellenado? |
|-------|:------------:|
| categoria_titulares | ✅ |
| categoria_datos | ✅ |
| finalidad | ✅ |
| base_legal | ✅ |
| plazo_retencion | ✅ |
| datos_sensibles | ✅ |
| tipo_dato_sensible | ✅ |
| evaluacion_impacto | ✅ |
| decisiones_automatizadas | ✅ |

### Valor real

- Reduce complejidad legal
- Ahorra ~15 min por RAT
- Minimiza errores de cumplimiento

### Archivo del caso de uso

→ `CASO_03_Plantillas_Inteligentes.md`

---

## Caso de Uso 4: Detectar Incumplimiento Automáticamente

### Objetivo
Que el sistema detecte riesgos de incumplimiento cuando se configura un proceso con datos biométricos.

### Caso real
Una empresa crea un RAT de control de acceso facial. El sistema detecta que usa consentimiento como base legal para biometría → inválido según Art. 16 BIS.

### Paso a paso

**Paso 1 — Crear RAT biométrico**
- Click en **"+ Nuevo proceso"**
- Nombre: `"Control de acceso facial"`

**Paso 2 — Sistema detecta flags de riesgo**
- Marca datos sensibles: `"Datos biométricos de identificación (Art. 16 BIS)"`
- Base legal por defecto: `"Consentimiento del titular"` → ⚠️ INVÁLIDO

**Paso 3 — Alertas generadas**

| Alerta | Causa |
|--------|-------|
| ⚠️ Consentimiento inválido para biometría | Relación jerárquica asimétrica |
| 🔐 Art. 16 BIS activo | EIPD obligatoria |
| 📋 EIPD pendiente | No completada |
| 📄 Encargado sin contrato | Falta contrato |

**Paso 4 — Correcciones sugeridas**
- Base legal → `"Obligación legal"`
- Activar EIPD
- Agregar contrato con proveedor

### Qué logró la empresa

- Entendió que su base legal era incorrecta
- Evitó una infracción gravísima (hasta 20.000 UTM)
- Documentó los riesgos antes de la fiscalización

### Archivo del caso de uso

→ `CASO_04_Deteccion_Incumplimiento.md`

---

## Caso de Uso 5: Registrar Brecha de Seguridad

### Objetivo
Cumplir la obligación legal del Art. 14 bis ante una filtración de datos.

### Caso real
Un hackeo expone datos de clientes. La empresa tiene 72 horas para notificar a la APDC.

### Paso a paso

**Paso 1 — Ir a Brechas**
- Menú lateral: **"Brechas"** → **"+ Nueva brecha"**

**Paso 2 — Completar formulario**
- Descripción, fecha detección, RATs afectados, datos comprometidos

**Paso 3 — Sistema calcula plazos**
- Horas transcurridas desde detección
- Alerta: APDC por vencer (< 12h restantes)
- Urgencia si hay datos sensibles o menores

**Paso 4 — Registrar notificaciones**
- Marca `notificado_apdc` + fecha
- Marca `notificado_titulares` si corresponde

### Obligaciones legales

| Notificación | Plazo | Referencia |
|-------------|-------|------------|
| APDC | 72 horas | Art. 14 bis |
| Titulares | Sin dilación | Si hay sensibles/menores |

### Qué logró

- Trazabilidad legal del incidente
- Evidencia de reacción en plazo
- Alertas para no superar las 72h

### Archivo del caso de uso

→ `CASO_05_Registrar_Brecha_Seguridad.md`

---

## Caso de Uso 6: Exportar Evidencia para Auditoría

### Objetivo
Generar evidencia formal del RAT para demostrar cumplimiento ante fiscalización.

### Paso a paso

**Paso 1 — Ir a Reportes**
- Menú lateral: **"Reportes"**

**Paso 2 — Filtrar**
- Filtra por estado, base legal, sensible, EIPD, transferencia
- Agrupa por: estado / riesgo / base legal

**Paso 3 — Exportar**
- **📥 CSV** → archivo para Excel/Google Sheets
- **📥 PDF** → documento formal con membrete

### Qué está vendiendo realmente

Tu sistema NO vende: formularios.
Tu sistema vende: **orden, trazabilidad, cumplimiento, evidencia, reducción de riesgo legal.**

### Evidencia que genera

| Tipo | Qué demuestra |
|------|---------------|
| PDF formal | RAT existente para la APDC |
| CSV detallado | Campos técnicos completos |
| Historial auditoría | Quién, cuándo, qué cambió |
| KPIs completitud | Madurez del programa |
| Alertas activas | Qué falta corregir |

### Archivo del caso de uso

→ `CASO_06_Exportar_Evidencia_Auditoria.md`

---

## Documentación del flujo actual de la app

### Arquitectura general

```
Login → [onboarding si es primera vez] → Dashboard
                                        ↓
                              Sidebar: selector de empresa
                                        ↓
                              Procesos RAT / Empresas / Brechas / Reportes
```

### Páginas principales

| Ruta | Descripción |
|------|-------------|
| `/login` | Autenticación con usuario y contraseña |
| `/onboarding` | Configuración inicial (primera empresa) — **NUEVO** |
| `/dashboard` | KPIs, alertas de cumplimiento, procesos recientes |
| `/rat` | CRUD de procesos RAT (wizard de 4 pasos) |
| `/companies` | Gestión de empresas responsables + usuarios por empresa |
| `/breaches` | Registro de brechas de seguridad (Art. 14 bis) |
| `/reportes` | Reportes avanzados con exportación CSV/PDF |

### Autenticación y autorización

- JWT con expiry de 8 horas
- Roles: admin global, admin de empresa, editor, viewer
- El admin global puede crear usuarios y gestionar todas las empresas
- El rol por empresa define qué puede hacer cada usuario

### Modelo de datos principal

```
User ─────────────────┐
  │                   │ (UserCompany: many-to-many con rol)
  │                   ↓
Company ◄────────── UserCompany
  │
  └── RAT (uno a muchos)
        │
        ├── EIPD (1:1)
        └── Consentimiento (1:N)
```

### Módulo RAT — Campos del Art. 16 Ley 21.719

Los 7 campos mínimos obligatorios:
1. Nombre del proceso
2. Categoría de datos
3. **Categoría de titulares** (Art. 16 — campo mínimo)
4. Finalidad
5. Base legal (Art. 13)
6. Fuente de datos
7. Plazo de retención

### Alertas automáticas de auditoría

- Datos sensibles sin base legal expresa
- Biométricos sin EIPD (Art. 16 BIS)
- Transferencia internacional sin garantías (Art. 28)
- Decisiones automatizadas sin documentación (Art. 8)
- Interés legítimo sin test de 3 pasos (Art. 16)
- Encargados sin contrato de encargo (Art. 14 quáter)
- EIPD pendiente
- RATs por vencer (90 días antes del plazo)
- RATs vencidos

### Tecnologías

- **Frontend**: Next.js 16 + React 19 + TypeScript + Tailwind CSS v4
- **Backend**: FastAPI + SQLAlchemy + SQLite
- **Auth**: JWT + Bcrypt
- **Validación**: Zod + Pydantic
- **Exportación**: jsPDF + jspdf-autotable (CSV/PDF)
- **Notificaciones**: Sonner (toasts)