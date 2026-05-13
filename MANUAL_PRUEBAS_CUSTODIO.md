# MANUAL DE PRUEBAS — SISTEMA CUSTODIO RAT

## Sistema de Registro de Actividades de Tratamiento (RAT)
### Ley 21.719 — Protección de Datos Personales en Chile

---

## 1. FLUJO DE PRUEBA COMPLETO

### Paso 1 — Crear una empresa (solo Superadmin)

**Objetivo:** Registrar el responsable del tratamiento de datos.

**Acciones:**
1. Ingresa con `admin / admin1234`
2. Ve a **Empresas** → **+ Nueva empresa**
3. Completa los campos obligatorios (RUT, Razón social, Email DPO)

**Campos disponibles:**
- Razón social, RUT, Rubro, Dirección
- Nombre del DPO (opcional), Email del DPO
- Descripción, Canal de ejercicio de derechos

**Resultado esperado:** La empresa aparece en el selector de empresa activa del sidebar.

**Valor:** Estás identificando al responsable legal ante la Ley 21.719.

---

### Paso 2 — Crear un usuario y asignarlo a la empresa

**Objetivo:** Dar acceso a colaboradores para gestionar los registros.

**Acciones:**
1. Ve a **Usuarios** → **+ Nuevo usuario**
2. Llena: username, email, nombre completo, contraseña
3. Selecciona el **rol global**:
   - `Usuario` → puede crear/editar RATs de su empresa
   - `Admin empresa` → puede gestionar todo de su empresa
   - `Superadmin` → acceso total al sistema
4. Selecciona la **empresa asignada** (obligatorio para usuario y admin_empresa)

**Resultado esperado:** El usuario aparece en la lista de usuarios con su empresa asignada.

**Valor:** Cada persona que trata datos personales queda identificada y con permisos definidos.

---

### Paso 3 — Agregar un RAT (proceso de tratamiento)

**Objetivo:** Documentar una actividad de tratamiento de datos.

**Acciones:**
1. Ve a **Procesos RAT** → **+ Nuevo RAT** (o presiona `Ctrl+N`)
2. Completa los **4 pasos del wizard**:

#### Paso 1 — Identificación
- **Nombre del proceso:** Ej: "Gestión de nóminas"
- **Categorías de titulares:** Ej: "Empleados, Candidatos"
- **Fuente de los datos:** Ej: "Formularios internos, Entrevistas"
- **Destinatarios:** Ej: "AFP, Isapre, Inspecciones del Trabajo"
- **Encargado del tratamiento:** Ej: "Equipo de Recursos Humanos"

#### Paso 2 — Datos tratados
- **Categoría de datos:** Ej: "Datos identificativos, Datos laborales"
- **Datos sensibles:** Marcar si trata datos del Art. 16 (origen racial, salud, biométricos, etc.)
- **Evaluación de impacto (EIPD):** Indica si se requiere hacer un test más detallado
- **Decisiones automatizadas:** Indica si hay decisiones algorítmicas que afectan a los titulares

#### Paso 3 — Finalidad y base legal
- **Finalidad:** Ej: "Cumplimiento de obligaciones laborales y previsionales"
- **Base legal:** Seleccionar una:
  - `Consentimiento del titular`
  - `Ejecución de contrato`
  - `Obligación legal`
  - `Interés legítimo`
  - `Interés vital del titular`
  - `Datos biométricos de identificación (Art. 16 BIS)`
- **Test de interés legítimo:** Si elegiste "Interés legítimo", el sistema guía un test de 3 pasos para verificar que el interés no prevalece sobre los derechos del titular

#### Paso 4 — Almacenamiento y transferencias
- **Plazo de retención:** Ej: "5 años después del término de la relación laboral"
- **Medidas de seguridad:** Ej: "Encriptación, control de accesos, backup"
- **Transferencia internacional:** Marcar si los datos se transfieren fuera de Chile
- **País destino y garantías:** Si hay transferencia internacional

**Resultado esperado:**
- RAT aparece en la tabla de Procesos RAT
- El estado inicial es "Borrador"
- Se registra auditoría automática de quién lo creó

**Valor:** Estás creando el registro que la Ley 21.719 exige: qué datos, para qué, con qué base legal y cuánto tiempo.

---

### Paso 4 — Completar y aprobar el RAT

**Acciones:**
1. Edita el RAT → completa los campos faltantes
2. Cambia el estado: Borrador → En revisión → Aprobado

**Resultado esperado:**
- El indicador de completitud aumenta según los campos llenos
- Al aprobar, se registra en auditoría
- Dashboard muestra el avance

**Valor:** Un RAT incompleto no cumple la ley. Solo cuando está aprobado puedes demostrar que cumpliste.

---

### Paso 5 — Reportes y exportación

**Acciones:**
1. Ve a **Reportes**
2. Filtra por: estado, riesgo, base legal, datos sensibles, EIPD
3. Ordena por cualquier columna
4. Exporta a CSV o PDF

**Resultado esperado:**
- Puedes generar informes para la autoridad (CPIC/CTA)
- Los filtros quedan guardados en URL
- El PDF incluye todos los campos del RAT

**Valor:** Puedes entregar documentación a la autoridad en minutos, no en semanas.

---

### Paso 6 — Registrar una brecha de seguridad

**Acciones:**
1. Ve a **Brechas** → **+ Registrar brecha**
2. Llena: descripción del incidente, fecha de detección, datos comprometidos
3. Adjunta los RATs afectados
4. Registra las medidas adoptadas

**Resultado esperado:**
- Se activa el plazo de 72 horas para notificar a la autoridad
- Se muestra countdown del plazo
- El dashboard muestra alerta si hay brechas activas

**Valor:** La ley exige notificar brechas en 72 horas. El sistema te ayuda a no olvidar.

---

## 2. ROLES Y QUÉ PUEDE HACER CADA UNO

| Rol | Empresas | RATs | Brechas | Reportes | Usuarios |
|-----|----------|------|---------|----------|----------|
| **Superadmin** | Todas (crear/editar/eliminar) | Todas | Todas | Todos | Todos |
| **Admin empresa** | Solo la suya (editar) | Solo su empresa | Solo su empresa | Solo su empresa | No ve |
| **Usuario** | No ve | Solo su empresa (crear/editar) | Solo su empresa (solo lectura) | Solo su empresa | No ve |

---

## 3. QUÉ ESPERAR EN CADA PANTALLA

### Dashboard
- **KPI cards:** Total RATs, Completitud promedio, Datos sensibles, Requieren EIPD, Transferencias internacionales, Decisiones automatizadas
- **Mini gráficos:** Distribución por estado, por riesgo, por base legal
- **Alertas:** Brechas activas con plazo próximo a vencer
- **Alerta si hay RATs en estado "Borrador" por más de 30 días**

### Procesos RAT
- Tabla con columnas configurables
- Filtros por estado, riesgo, base legal, datos sensibles
- Expandir fila para ver detalle completo + auditoría
- Acciones: editar, duplicar, eliminar (con undo de 5 segundos)
- Indicador pulsante rojo para riesgo "Crítico"

### Reportes
- Filtros guardados en URL (compartir por enlace)
- Agrupamiento por estado / base legal / riesgo
- Exportación CSV y PDF
- Chat IA para consultas sobre la ley

### Empresas
- Tarjeta por empresa con estado activa/inactiva
- Botón "Listado usuarios" → modal con usuarios de esa empresa
- Botón "Gestionar accesos" → panel para asignar usuarios (admin/editor/viewer)
- El admin de empresa no puede ver/modificar otras empresas

### Brechas
- Countdown del plazo legal (72 horas)
- Badge rojo "VENCIDO" si se excedió
- Registro de RATs afectados

---

## 4. MÉTRICAS DE VALOR

### Cumplimiento legal
| Obligación Ley 21.719 | Cómo Custodio lo resuelve |
|------------------------|---------------------------|
| Registro de actividades | Wizard de 4 pasos guía la captura completa |
| Base legal documentada | Campo obligatorio en cada RAT |
| Plazos de retención | Campo obligatorio en cada RAT |
| Transferencias internacionales | Checkbox + campos de país y garantías |
| Notificación de brechas (72h) | Countdown + alerta en dashboard |
| EIPD para datos sensibles | Campo obligatorio con guía de test |
| Datos biométricos (Art. 16 BIS) | Categoría específica en tipo de dato sensible |

### Beneficios medibles
- **Tiempo de documentación:** De 2 días a 15 minutos por RAT
- **Auditoría automática:** Cada cambio queda registrado con usuario y timestamp
- **Alertas proactivas:** RATs en borrador +30 días, brechas perto del plazo
- **Exportación instantánea:** PDF/CSV para la autoridad en 1 clic
- **Filtros avanzados:** Encuentra cualquier RAT por estado, riesgo, base legal

---

## 5. CHECKLIST DE PRUEBA

### Antes de comenzar
- [ ] Limpiar storage del navegador
- [ ] Login con admin/admin1234
- [ ] Verificar que hay empresas en la lista

### Crear empresa
- [ ] Ir a Empresas → Nueva empresa
- [ ] Llenar RUT válido (sino da error de validación)
- [ ] Guardar y verificar que aparece en sidebar

### Crear usuario
- [ ] Ir a Usuarios → Nuevo usuario
- [ ] Asignar empresa (obligatorio para admin_empresa y usuario)
- [ ] Verificar que aparece en "Listado usuarios" de esa empresa

### Crear RAT
- [ ] Ctrl+N o botón "+ Nuevo RAT"
- [ ] Validar que wizard no permite avanzar sin campos obligatorios
- [ ] Llenar los 4 pasos completos
- [ ] Verificar que aparece en la tabla

### Editar RAT
- [ ] Click en editar → modificar un campo → guardar
- [ ] Verificar que auditoría registra el cambio

### Reportes
- [ ] Aplicar filtro por estado = "Borrador"
- [ ] Copiar URL y abrir en otra pestaña → filtro persiste
- [ ] Exportar CSV → archivo se descarga

### Brechas
- [ ] Crear brecha → verificar countdown
- [ ] AlertBanner aparece en dashboard si hay brechas activas

---

## 6. ESCENARIOS DE PRUEBA EXTREMOS

### Escenario 1: Usuario sin empresa asignada
1. Crear usuario con rol "usuario" pero sin asignar empresa
2. Login con ese usuario
3. **Esperado:** Mensaje de error o redirige a crear empresa (nunca acceso al dashboard)

### Escenario 2: Admin empresa intenta ver otra empresa
1. Login con usuario admin de "Empresa A"
2. Intentando acceder a datos de "Empresa B"
3. **Esperado:** Backend retorna 403 y frontend muestra "Sin permisos"

### Escenario 3: RAT con datos sensibles sin EIPD
1. Crear RAT con "Datos sensibles" = sí
2. Dejar "Evaluación de impacto" vacío
3. **Esperado:** Alerta visual indicando que requiere EIPD

### Escenario 4: Brecha no notificada a las 72h
1. Registrar brecha hace 4 días sin actualizar estado
2. **Esperado:** Badge "VENCIDO" en rojo pulsante en dashboard

---

*Documento generado para pruebas de usuario del sistema Custodio RAT — Ley 21.719 Chile*