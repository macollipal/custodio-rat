# Custodio — Manual de Usuario

**Sistema de gestión del Registro de Actividades de Tratamiento (RAT) · Ley 21.719 de Chile**

---

## 1. ¿Qué es Custodio?

Custodio es un sistema digital que te ayuda a cumplir con la **Ley 21.719 de Protección de Datos Personales de Chile**. 
Permite documentar, gestionar y mantener actualizado el Registro de Actividades de Tratamiento (RAT) de tu organización.

**En resumen:** Custodio hace el trabajo pesado de crear y mantener el RAT para que tú no tengas que hacerlo en planillas de Excel.

---

## 2. El problema legal

### ¿Por qué existe la Ley 21.719?

La Ley 21.719, publicada en diciembre de 2024, moderniza la antigua normativa de protección de datos en Chile. 
Crea la **Agencia de Protección de Datos Personales (APDC)** y establece obligaciones concretas para todas las organizaciones que traten datos personales.

**¿Qué pasa si no cumplimiento?**

| Infracción | Multa |
|-----------|-------|
| Leves | Hasta 5.000 UTM (~$387.000) |
| Graves | Hasta 10.000 UTM (~$775.000) |
| Gravísimas | Hasta 20.000 UTM (~$1.550.000) |

Además, la APDC puede fiscalizar tu organización en cualquier momento y solicitar el RAT como primera evidencia de cumplimiento.

### ¿Cuál es la fecha límite?

**1 de diciembre de 2026** — fecha en que la ley entra en vigencia general. Después de esa fecha, las fiscalizaciones y multas aplican plenamente.

---

## 3. ¿Qué es un RAT?

**RAT** = Registro de Actividades de Tratamiento

Es un documento formal donde describes **cada actividad de tratamiento de datos personales** que realiza tu organización. Por cada tratamiento debes documentar:

- **Qué datos** y de quién (empleados, clientes, proveedores)
- **Para qué finalidad** se usan esos datos
- **Con qué autorización legal** los tratas (consentimiento, contrato, obligación legal)
- **Quiénes tienen acceso** a esos datos (internos y externos)
- **Cuánto tiempo** los conservas
- **Si se transfieren internacionalmente** y con qué garantías
- **Qué medidas de seguridad** implementas

### ¿Por qué es importante?

El RAT es la **columna vertebral documental** de tu cumplimiento. Si la APDC te fiscaliza, lo primero que pedirán es tu RAT. Tenerlo te permite:

- Demostrar que sabes qué datos tienes y para qué los usas
- Mostrar que tienes base legal para cada tratamiento
- Identificar tratamientos de alto riesgo que requieren evaluación adicional
- Responder rápidamente ante una brecha de seguridad

---

## 4. ¿Para quién es Custodio?

### Roles en el sistema

| Rol | ¿Quién es? | ¿Qué puede hacer? |
|-----|-----------|-------------------|
| **Superadmin** | El administrador del sistema | Gestionar empresas, usuarios, RATs, brechas. Acceso total. |
| **Admin de empresa** | El responsable de datos de la empresa | Gestionar todo lo de su empresa: usuarios, RATs, brechas. |
| **Usuario** | Un colaborador operativo | Crear y editar RATs de su empresa. Solo lectura de brechas. |

### ¿Quién debería usar Custodio?

- **Pequeñas y medianas empresas** que necesitan cumplir la ley sin contratar un DPO externo
- **Empresas grandes** que quieren sistematizar y documentar su cumplimiento
- **Estudio jurídicos y consultoras** que asesoran a clientes en cumplimiento
- **Organizaciones públicas** que procesan datos de ciudadanos

---

## 5. Funcionalidades principales

### 5.1 Gestión de empresas

Registra cada empresa u organización responsable del tratamiento de datos. 
Cada empresa tiene su propio conjunto de RATs, usuarios y brechas.

**Datos que se registran:**
- Razón social y RUT
- Rubro o sector
- Datos del DPO (Responsable de Protección de Datos)
- Canal de ejercicio de derechos de los titulares

### 5.2 Gestión de usuarios y accesos

Invita colaboradores a tu empresa y define qué pueden hacer:

| Rol dentro de la empresa | Alcance |
|-------------------------|---------|
| **Administrador** | Puede crear, editar y eliminar RATs y brechas |
| **Editor** | Puede crear y editar RATs y brechas |
| **Visualizador** | Solo puede ver los RATs, sin modificar |

### 5.3 Creación de procesos RAT (Wizard de 4 pasos)

El sistema te guía paso a paso para crear cada registro. No necesitas ser experto — el sistema te pide solo la información que la ley exige.

**Paso 1 — Identificación**
- Nombre del proceso de tratamiento
- Categorías de titulares (clientes, empleados, proveedores, etc.)
- Fuente de los datos
- Destinatarios y encargados

**Paso 2 — Datos tratados**
- Qué categoría de datos personales se procesan
- Si incluye datos sensibles (origen racial, salud, opiniones políticas, etc.)
- Si requiere Evaluación de Impacto (EIPD)
- Si hay decisiones automatizadas

**Paso 3 — Finalidad y ley**
- Para qué finalidad se usan los datos
- Base legal del tratamiento:
  - Consentimiento del titular
  - Ejecución de contrato
  - Obligación legal
  - Interés legítimo (requiere test documentado)
  - Interés vital del titular
  - Datos biométricos (caso especial)

**Paso 4 — Almacenamiento y transferencias**
- Plazo de retención de los datos
- Medidas de seguridad implementadas
- Transferencias internacionales de datos (si aplica)

### 5.4 Dashboard y KPIs

El panel principal te muestra de un vistazo el estado de cumplimiento de tu empresa:

| Indicador | ¿Qué significa? |
|-----------|-----------------|
| **Total de procesos** | Cantidad de RATs registrados |
| **Completitud promedio** | % de campos llenados en promedio — objetivo ≥75% |
| **Con datos sensibles** | Procesos que traten datos sensibles (requieren más cuidado) |
| **Requieren EIPD** | Procesos que necesitan Evaluación de Impacto previa |

**Colores de alerta:**

| Color | Significado |
|-------|-----------|
| 🟢 Verde | Cumplimiento bueno (≥75%) |
| 🟡 Amarillo | Cumplimiento moderado (≥50%) |
| 🔴 Rojo | Cumplimiento bajo (<50%) |

### 5.5 Alertas de cumplimiento

El sistema detecta automáticamente situaciones que necesitan atención:

- Procesos con datos sensibles sin EIPD
- Transferencias internacionales sin garantías contractuales
- Interés legítimo sin test de 3 pasos documentado
- Encargados del tratamiento sin contrato formal
- RATs vencidos (sin actualizar en +6 meses)

### 5.6 Gestión de brechas de seguridad

Si ocurre una brecha de seguridad (pérdida, robo o acceso no autorizado a datos personales), el sistema te ayuda a:

- Registrar la brecha con detalles
- Calcular el plazo APDC (72 horas desde la detección)
- Documentar qué medidas adoptaste
- Registrar si notificaste a la APDC y a los afectados

**Plazo legal:** Si la brecha puede generar riesgo para los derechos de los titulares, tienes **72 horas** para notificar a la APDC.

### 5.7 Reportes y exportaciones

Genera reportes filtrados por estado, base legal, nivel de riesgo y más. Exporta a:

- **CSV** — para análisis en Excel
- **PDF** — para presentar a la APDC o auditorías
- **CNI** — formato oficial para la Agencia de Protección de Datos Personales

### 5.8 Chat de asistencia IA(aún no esta, en alguna proxima version)

El sistema incluye un asistente con IA entrenado en la Ley 21.719. Te puede explicar conceptos, ayudarte a clasificar tratamientos y responder dudas sobre cumplimiento.

---

## 6. Proceso paso a paso: Crear tu primer RAT

### Paso 1 — Crear una cuenta e iniciar sesión

1. Abre tu navegador y entra a la URL que te proporcionó el administrador
2. Ingresa tu usuario y contraseña
3. Si es tu primera vez y no hay empresas registradas, el sistema te guiará al onboarding

### Paso 2 — Crear tu empresa

1. Ve al menú **Empresas**
2. Clic en **"+ Nueva empresa"**
3. Completa:
   - **Razón social** (obligatorio)
   - **RUT** (obligatorio)
   - **Rubro** (opcional)
   - **Nombre del DPO** (opcional, pero recomendado)
   - **Email del DPO** (opcional)
4. Clic en **"Crear empresa"**

La empresa aparecerá en el selector del sidebar. Selecciónala como empresa activa.

### Paso 3 — Invitar usuarios (opcional)

Si necesitas que otrosColaboradores trabajen contigo:

1. Ve a **Empresas** → selecciona tu empresa
2. Clic en **"+ Nuevo usuario"**
3. Completa los datos del usuario
4. Asigna un rol (Administrador, Editor o Visualizador)
5. Clic en **"Crear usuario"**

El usuario recibirá sus credenciales y podrá acceder al sistema.

### Paso 4 — Crear un proceso RAT (Wizard)

1. Ve al menú **Procesos RAT**
2. Clic en **"+ Nuevo proceso"**
3. **Sugerencias por rubro:** Si tu empresa tiene un rubro definido, el sistema te mostrará RATs predefinidos como plantillas (ej: "Gestión de nómina", "Marketing por email"). Puedes usar uno como punto de partida o crear uno personalizado.

**Sigue los 4 pasos del wizard:**

#### Paso 1 — Identificación
- **Nombre del proceso:** Describe brevemente qué actividad de tratamiento haces. Ej: "Gestión de nómina de empleados"
- **Categorías de titulares:** Selecciona quiénes son los afectados. Ej: "Empleados actuales y ex-empleados"
- **Fuente de los datos:** ¿De dónde obtienen los datos? Ej: "Formularios de contratación, sistema de RRHH"
- **Destinatarios:** ¿Quién más recibe estos datos? Ej: "AFP, isapres, TES Chile"

#### Paso 2 — Datos tratados
- **Categoría de datos:** Ej: "Datos de identificación (nombre, RUT, dirección), datos laborales (sueldo, cargo)"
- **Datos sensibles:** Si tratas datos sensibles (salud, opiniones políticas, biometría), marca la casilla y selecciona el tipo
- **¿Requiere EIPD?** Si usas datos sensibles o decisiones automatizadas, probablemente sí
- **¿Decisiones automatizadas?** Si hay decisiones que afectan a personas sin intervención humana

#### Paso 3 — Finalidad y ley
- **Finalidad:** ¿Para qué usas estos datos? Ej: "Cumplir obligaciones laborales y previsionales"
- **Base legal:** ¿Qué te autoriza a traiter estos datos?
  - **Consentimiento** — cuando la persona te autoriza expresamente
  - **Ejecución de contrato** — cuando es necesario para un contrato
  - **Obligación legal** — cuando una ley te lo exige
  - **Interés legítimo** — cuando te beneficias y no perjudicas al titular (requiere test documentado)
  - **Interés vital** — cuando hay una situación de riesgo

Si seleccionaste "Interés legítimo", el sistema te guiará a través de un test de 3 pasos.

#### Paso 4 — Almacenamiento
- **Plazo de retención:** ¿Cuánto tiempo conservas estos datos? Ej: "5 años después del fin de la relación laboral"
- **Medidas de seguridad:** ¿Cómo proteges estos datos? Ej: "Acceso restringido, cifrado, backups"
- **Transferencia internacional:** ¿Los datos salen de Chile? Si sí, indica el país y las garantías

5. Clic en **"Guardar"**

### Paso 5 — Revisar y aprobar

1. Una vez creado, el RAT aparece en la lista con estado **"Borrador"**
2. Puedes editarlo en cualquier momento
3. Cuando esté completo, puedes cambiar el estado a **"Completo"** o **"En revisión"**
4. El sistema te muestra el % de completitud y flags de riesgo

### Paso 6 — Exportar para la APDC

1. Ve a **Reportes**
2. Filtra por tu empresa y el RAT que necesitas
3. Clic en **"Exportar PDF"** o **"Exportar CNI"**
4. El archivo está listo para presentar a la APDC

---

## 7. Dashboard: Entender los números

El Dashboard te da una vista rápida del estado de cumplimiento.

### KPIs principales

| KPI | ¿Qué me dice? | ¿Qué hago si está bajo? |
|----|---------------|------------------------|
| Total de procesos | Cuántos RATs tienes registrados | Crea nuevos para cada actividad que trate datos |
| Completitud promedio | % de campos llenos en tus RATs | Completa los campos faltantes |
| Con datos sensibles | RATs que incluyen datos sensibles | Revisa si tienes base legal y EIPD si aplica |
| Requieren EIPD | RATs que necesitan Evaluación de Impacto | Prioriza estas para completar la EIPD |

### Gráfico de estados

Muestra cómo están distribuidos tus RATs:

- 🟡 **Borrador** — en progreso
- 🟢 **Completo** — listo pero no aprobado
- 🔵 **En revisión** — siendo revisado por el DPO
- 🟣 **Aprobado** — vigente y documentado

### Procesos recientes

Los últimos 6 RATs modificados, para que puedas hacer seguimiento rápido.

---

## 8. Exportar y presentar

### PDF por empresa

Genera un PDF con todos los RATs de una empresa. Ideal para audits internas o para tener como respaldo documental.

### CNI (Comunicación de Notificación Individual)

Formato oficial exigido por la APDC. Genera el documento listo para presentar.

### CSV

Exporta los datos a una planilla Excel para análisis propio, gráficos personalizados o para compartir con equipos que no usan el sistema.

---

## 9. Glosario

| Término | Significado |
|---------|-------------|
| **RAT** | Registro de Actividades de Tratamiento — documento que lista qué datos se tratan, para qué y con qué autorización |
| **APDC** | Agencia de Protección de Datos Personales — el organismo fiscalizador en Chile |
| **DPO** | Delegado de Protección de Datos — el responsable interno de cumplimiento |
| **EIPD** | Evaluación de Impacto en Protección de Datos — análisis obligatorio cuando hay datos sensibles o perfilamiento automatizado |
| **Titular** | La persona cuyos datos personales se están tratando (cliente, empleado, proveedor) |
| **Responsable** | La organización que decide cómo y para qué traiter los datos |
| **Encargado** | Un tercero que traite datos por cuenta del responsable (ej: un clouds provider) |
| **Base legal** | La razón legal que habilita el tratamiento: consentimiento, contrato, obligación legal, interés legítimo |
| **Datos sensibles** | Datos que requieren protección especial: origen racial, salud, opiniones políticas, afiliación sindical, biometría, vida sexual |
| **Brecha de seguridad** | Cuando datos personales se pierden, roban o acceden sin autorización |

---

## 10. Primeros pasos: Tu checklist para arrancar

### Semana 1: Setup inicial
- [ ] Crear cuenta de administrador
- [ ] Registrar tu empresa con todos los datos del DPO
- [ ] Invitar a los primeros usuarios
- [ ] Configurar el rubro de la empresa

### Semana 2: Primeros RATs
- [ ] Identificar los 3-5 procesos de tratamiento más importantes
- [ ] Crear un RAT con el Wizard para cada uno
- [ ] Llenar al menos los 7 campos obligatorios
- [ ] Revisar qué procesos incluyen datos sensibles

### Semana 3: Completar y afinar
- [ ] Completar los campos recomendados en cada RAT
- [ ] Realizar las EIPDs que correspondan
- [ ] Documentar los contratos con encargados del tratamiento
- [ ] Revisar transferencias internacionales

### Semana 4: Validar y exportar
- [ ] Revisar que cada RAT tenga ≥75% de completitud
- [ ] Exportar PDF y CNI de los RATs principales
- [ ] Verificar alertas de cumplimiento en el Dashboard
- [ ] Planificar revisión trimestral del RAT

---

## Info de contacto y soporte

**Sistema:** Custodio RAT Manager  
**Versión:** 1.0  
**Marco legal:** Ley 21.719 de Protección de Datos Personales de Chile  
**Fecha de vigencia:** 1 de diciembre de 2026

Para soporte técnico, contacta al administrador del sistema.