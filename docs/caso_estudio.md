# Caso de Estudio · RetailPro Chile SpA
## Implementación del RAT conforme a Ley 21.719

> **Objetivo**: Guiar paso a paso la creación completa del RAT de una empresa retail chilena, usando el sistema Custodio. Cada proceso RAT se crea con su plantilla, se interpretan las alertas, y se valida que el sistema responde como se espera.

> **Generado**: 2026-04-29
> **Última actualización**: 2026-05-12 — incluye Onboarding (Caso de Uso 1), 6 casos de uso documentados en /docs/casos_de_uso/

---

## Perfil de la empresa

| Campo | Valor |
|------|-------|
| **Razón social** | RetailPro Chile SpA |
| **RUT** | 76.123.456-7 |
| **Rubro** | Retail / Comercio minorista |
| **Sedes** | 3 tiendas + Casa matriz (Santiago) |
| **Empleados** | 150 |
| **Facturación** | $5.000M anual |
| **DPO** | María Elena Sánchez (asesora externa) |
| **Email DPO** | dpo@retailpro.cl |

---

## Resumen de procesos RAT

| # | Proceso | Plantilla | Base legal | Datos sensibles | EIPD | Completitud |
|---|---------|-----------|-----------|-----------------|------|-------------|
| 1 | Gestión de clientes CRM | Clientes web | Ejecución de contrato | No | No | ~65% |
| 2 | Nómina y remuneraciones | Empleados | Obligación legal | **Sí** (salud) | No | ~70% |
| 3 | Control de asistencia biométrica | Control biométrico asistencia | Obligación legal | **Sí** (Art. 16 BIS) | **Sí** | ~55% |
| 4 | Proveedores y pagos | Proveedores | Ejecución de contrato | No | No | ~65% |
| 5 | Reclutamiento y selección | Postulantes | Consentimiento del titular | No | No | ~60% |
| 6 | Videovigilancia tiendas | Videovigilancia | Interés legítimo | No | No | ~70% |
| 7 | Marketing y newsletters | Marketing | Consentimiento del titular | No | No | ~60% |
| 8 | Pacientes (beneficio staff) | Pacientes | Interés vital del titular | **Sí** (salud) | **Sí** | ~55% |
| 9 | Administración sociedad | Socios o accionistas | Obligación legal | No | No | ~70% |
| 10 | Contabilidad y facturación | Contabilidad y facturación | Obligación legal | No | No | ~70% |
| 11 | Evaluación de desempeño | Evaluación de desempeño | Interés legítimo | No | No | ~60% |
| 12 | Riesgos laborales (SST) | Riesgos laborales | Obligación legal | **Sí** (salud) | No | ~65% |

---

## FASE 1 · Setup inicial

### 1.0 Onboarding (primer ingreso)

> **Nuevo**: Si es el primer ingreso y no hay empresas registradas, el sistema redirige automáticamente a `/onboarding` para crear la primera empresa.

1. Login con `admin` / `admin1234`
2. Sistema detecta que no hay empresas → redirige a `/onboarding`
3. Completar: razón social, RUT, nombre DPO, email DPO
4. Empresa creada → redirige al dashboard con empresa activa

### 1.1 Crear empresa (onboarding)

1. Ir a **Empresas** → "+ Nueva empresa"
2. Completar:
   - **Razón social**: RetailPro Chile SpA
   - **RUT**: 76.123.456-7 (validación automática del dígito verificador)
   - **Rubro**: Retail
   - **Dirección**: Av. Libertador Bernardo O'Higgins 1234, Santiago
   - **Nombre DPO**: María Elena Sánchez
   - **Email DPO**: dpo@retailpro.cl
3. La empresa queda como **activa** automáticamente

### 1.2 Crear usuarios

1. Ir a **Empresas** → seleccionar "RetailPro Chile SpA" → botón "Usuarios"
2. Crear:
   - `mgarcia` — rol **Editor** (encargada de RRHH)
   - `jtorres` — rol **Viewer** (asesor legal)
3. El admin global (`admin`) tiene acceso completo

### 1.3 Selector de empresa

- El **Topbar** muestra la empresa activa con un dropdown
- Desde el Sidebar se puede cambiar empresa rápidamente
- Al cambiar de empresa se limpian los RATs en caché y se recargan

---

## FASE 2 · Procesos RAT (12 casos)

### PROCESO 1 · Gestión de clientes CRM

**Plantilla**: Clientes web

#### Paso a paso

1. Ir a **Procesos RAT** → "+ Nuevo proceso"
2. En el **Paso 1**, selector "Tipo de proceso" → elegir **"clientes web"**
3. Click **"Aplicar"** → se pre-rellenan:
   - *Categoría de datos*: "Datos identificativos (nombre, email, teléfono), datos de navegación y comportamiento online"
   - *Categorías de titulares*: "Clientes y usuarios del servicio web"
   - *Finalidad*: "Gestión de la relación comercial, atención al cliente, envío de comunicaciones y marketing digital"
   - *Base legal*: "Ejecución de contrato"
   - *Plazo de retención*: "5 años desde el último contacto comercial"
4. El campo `nombre_proceso` se ingresa manualmente: "Gestión de clientes CRM"
5. Completar `fuente_datos`: "Directamente del titular mediante formularios web y registro de cuenta"
6. Completar `destinatarios`: "Proveedor de CRM (encargado), área de ventas"

#### Campos que quedan MANUAL (la plantilla no los cubre)

| Campo | Qué ingresar |
|-------|-------------|
| `medidas_seguridad` | "Cifrado TLS en tránsito, AES-256 en reposo, MFA para acceso admin" |
| `transferencia_datos` | "Datos compartidos con Mailchimp para email marketing" |
| `transferencia_internacional` | true (si se usa servidor en USA) |
| `pais_destino` | "Estados Unidos" |
| `garantias_transferencia_int` | "Cláusulas Contractuales Tipo (SCC)" |

#### Alertas que aparecerán tras guardar

Si se Marca `transferencia_internacional = true` sin garantías:
> 🌐 ATENCIÓN: Se registró transferencia internacional sin especificar las garantías aplicadas.

Si se activa `decisiones_automatizadas` (perfilamiento):
> 🤖 Este proceso involucra decisiones automatizadas o perfilamiento.

#### Completitud esperada

Con plantilla + campos manuales completados: **~85%** (7 campos obligatorios OK + algunos recomendados)

---

### PROCESO 2 · Nómina y remuneraciones

**Plantilla**: Empleados

#### Paso a paso

1. Wizard → seleccionar **"empleados"** → Aplicar
2. Se pre-rellena:
   - *Categoría de datos*: "Datos identificativos, laborales, remuneracionales, de salud (licencias médicas), previsionales"
   - *Categorías de titulares*: "Trabajadores y ex-trabajadores de la organización"
   - *Finalidad*: "Gestión de la relación laboral, liquidación de remuneraciones, cumplimiento de obligaciones legales previsionales y tributarias"
   - *Base legal*: "Obligación legal"
   - *Plazo de retención*: "10 años desde el término de la relación laboral (Art. 58 Código del Trabajo)"
   - `datos_sensibles`: **true** (automático)
   - `tipo_dato_sensible`: **"Salud (licencias médicas)"** (automático)

#### Observación legal de la plantilla

> ⚠️ Los datos de salud (licencias) son datos sensibles — base legal: obligación legal.
> **ATENCIÓN**: Si se usan datos biométricos, registrarlos en un proceso separado "Control biométrico de asistencia", ya que requieren tratamiento bajo Art. 16 BIS. En relaciones laborales, el consentimiento del empleado NO es base legal válida para biometría.

#### Campos manuales necesarios

| Campo | Valor |
|-------|-------|
| `nombre_proceso` | "Nómina y remuneraciones" |
| `fuente_datos` | "Sistema de asistencia, formularios de contrato, licencias médicas" |
| `nombre_encargado` | "Proveedor de nómina externalizado" |
| `tiene_contrato_encargado` | **true** |
| `medidas_seguridad` | "Acceso rolificado, logs de auditoría, respaldo semanal cifrado" |

#### Alertas esperadas

> ⚠️ Este proceso trata datos sensibles (Art. 2 letra g). Verifique que cuenta con base legal expresa y medidas de seguridad reforzadas.

**Nota**: No se activa alerta de biométricos porque este proceso NO usa biometría — solo salud. La plantilla solo sugiere crear otro proceso si se tratara de biometría.

#### Completitud: ~75%

---

### PROCESO 3 · Control de asistencia biométrica

**Plantilla**: Control biométrico asistencia

#### Paso a paso

1. Wizard → seleccionar **"control biométrico asistencia"** → Aplicar
2. Se pre-rellena:
   - *Categoría de datos*: "Datos biométricos de identificación (huella dactilar, facial o equivalente), registro de hora de entrada/salida"
   - *Base legal*: "Obligación legal" (no consentimiento)
   - `datos_sensibles`: **true**
   - `tipo_dato_sensible`: **"Datos biométricos de identificación (Art. 16 BIS Ley 21.719)"**
   - `evaluacion_impacto`: **true** (automático — EIPD obligatoria)
   - *Plazo*: "5 años desde el registro"

#### Observación crítica de la plantilla

> 🔐 IMPORTANTE — Art. 16 BIS: Los datos biométricos destinados a identificar inequívocamente a una persona requieren EIPD previa y base legal específica. **El consentimiento del empleado NO es base válida** en contextos laborales por la asimetría de poder.
> Documente si usa 'minucias' (hash de huella) o imagen directa — ambas son datos biométricos protegidos.

#### Este proceso es el de MAYOR RIESGO

| Indicador | Valor | Significado |
|-----------|-------|-------------|
| Datos sensibles | ⚠️ Sí | Requiere medidas reforzadas |
| Tipo | Art. 16 BIS | Biometría = categoría especial |
| EIPD | 📋 Requerida | Debe completarse antes de operar |
| Base legal | Obligación legal | Correcta — no consentimiento |
| Riesgo calculado | Crítico/Alto | El más sensible del RAT |

#### Campos manuales críticos

| Campo | Qué ingresar |
|-------|-------------|
| `nombre_proceso` | "Control de asistencia biométrica" |
| `fuente_datos` | "Terminal de huella dactilar, sistema de reloj control" |
| `nombre_encargado` | "Proveedor reloj control" |
| `tiene_contrato_encargado` | **true** (crítico — Art. 14 quáter) |
| `medidas_seguridad` | "Hash de minucias (no imagen), cifrado AES-256, acceso restringido a RRHH" |
| `test_interes_legitimo` | NO APLICA — la base legal es obligación legal, no interés legítimo |

#### Alertas que aparecerán

1. ⚠️ Datos sensibles
2. 🔐 BIOMETRÍA: Art. 16 BIS — EIPD obligatoria
3. 📋 EIPD PENDIENTE (porque estado_eipd inicia en "pendiente")
4. ⚖️ Base legal "Interés legítimo" — solo si se hubiera elegido esa base (no aplica aquí)
5. 📄 ENCARGADO SIN CONTRATO si `tiene_contrato_encargado = false`

#### Completitud esperada: ~60% (por la EIPD que queda pendiente)

---

### PROCESO 4 · Proveedores y pagos

**Plantilla**: Proveedores

#### Campos pre-rellenados

- *Categoría de datos*: "Datos identificativos de contacto, datos tributarios (RUT, actividad económica), datos bancarios"
- *Categorías de titulares*: "Proveedores de bienes y servicios"
- *Finalidad*: "Gestión de la relación contractual, pagos, evaluación crediticia y cumplimiento tributario"
- *Base legal*: "Ejecución de contrato"
- *Plazo*: "6 años desde el cierre del ejercicio contable"

#### Observación de la plantilla

> Verificar que los datos bancarios están cifrados en reposo y en tránsito. Si se usa evaluación crediticia automatizada, activar flag de decisiones automatizadas.

#### Completitud: ~65%

---

### PROCESO 5 · Reclutamiento y selección

**Plantilla**: Postulantes

#### Campos pre-rellenados

- *Base legal*: **Consentimiento del titular** (correcto)
- *Plazo*: "2 años desde la postulación o hasta cubrir el cargo"
- `datos_sensibles`: false

#### Observación

> Informar al postulante mediante aviso de privacidad. No solicitar datos no necesarios para el cargo (principio de proporcionalidad). Si se usa screening automatizado de CVs, activar flag de decisiones automatizadas.

#### Completitud: ~60%

---

### PROCESO 6 · Videovigilancia

**Plantilla**: Videovigilancia

#### Campos pre-rellenados

- *Base legal*: **Interés legítimo** (correcto para CCTV)
- *Plazo*: "30 días desde la grabación"
- `datos_sensibles`: false

#### Observación

> Interés legítimo requiere test de 3 pasos documentado. Colocar señalética visible antes del área vigilada.

#### ⚠️ ALERTA CRÍTICA — Interés legítimo sin test

Cuando se guarda este proceso, el backend detecta que `base_legal = "Interés legítimo"` y `test_interes_legitimo` está vacío.

Se genera automáticamente:
> ⚖️ Base legal: Interés legítimo. Debe documentar el test de 3 pasos.
> ⚖️ PENDIENTE: Base legal 'Interés legítimo' requiere documentar el test de 3 pasos.

**Acción requerida**: Editar el proceso e ingresar el test en el campo `test_interes_legitimo`:
```
(1) Interés legítimo: protección de bienes e instalaciones de la empresa.
(2) El tratamiento (grabación de imágenes) es necesario para ese interés — no existe alternativa menos invasiva.
(3) Prevalece sobre el derecho a la privacidad de empleados y visitantes en espaces laborales.
```

#### Completitud: ~70% pero con alerta de test pendiente

---

### PROCESO 7 · Marketing y newsletters

**Plantilla**: Marketing

#### Campos pre-rellenados

- *Base legal*: **Consentimiento del titular**
- `decisiones_automatizadas`: **true** (perfilamiento)

#### Observación

> Implementar mecanismo de opt-out sencillo. Los titulares pueden oponerse al tratamiento para marketing directo sin necesidad de justificación (Art. 8 Ley 21.719).

#### Completitud: ~60%

---

### PROCESO 8 · Pacientes (beneficio staff)

**Plantilla**: Pacientes

#### Campos pre-rellenados

- *Base legal*: **Interés vital del titular** (para datos de salud de trabajadores)
- `datos_sensibles`: **true**
- `tipo_dato_sensible`: "Salud (física o mental)"
- `evaluacion_impacto`: **true**

#### Observación

> Datos de salud: categoría sensible del Art. 2 letra g. Requiere EIPD y medidas de seguridad reforzadas.

#### Completitud: ~55% (EIPD pendiente)

---

### PROCESO 9 · Administración sociedad

**Plantilla**: Socios o accionistas

- *Base legal*: Obligación legal (CMF + SII)
- *Plazo*: 10 años

#### Completitud: ~70%

---

### PROCESO 10 · Contabilidad y facturación

**Plantilla**: Contabilidad y facturación *(nuevo — agregado hoy)*

#### Campos pre-rellenados

- *Categoría de datos*: "Datos identificativos tributarios (RUT), datos de contacto comercial, datos de transacciones comerciales, detalle de compras y ventas, datos de pago (facturas electrónicas)"
- *Categorías de titulares*: "Clientes, proveedores y terceros con quienes se emiten o reciben documentos tributarios"
- *Finalidad*: "Cumplimiento de obligaciones tributarias ante el SII, emisión de facturas electrónicas, registro contable de transacciones comerciales"
- *Base legal*: **Obligación legal**
- *Plazo*: "10 años desde la emisión del documento (Art. 12 Ley 19.983)"

#### Observación

> La retención de facturas electrónicas es obligatoria por 10 años según normativa del SII. Si se usa factoring electrónico o cobranza automatizada, activar flag de decisiones automatizadas.

#### Completitud: ~70%

---

### PROCESO 11 · Evaluación de desempeño

**Plantilla**: Evaluación de desempeño *(nuevo)*

#### Campos pre-rellenados

- *Base legal*: **Interés legítimo** (requiere test documentado)
- *Plazo*: "2 años desde la evaluación o hasta el término de la relación laboral"

#### ⚠️ Generará alerta de test de interés legítimo pendiente

 Igual que videovigilancia — al guardar se generará la alerta de test pendiente.

#### Completitud: ~60%

---

### PROCESO 12 · Riesgos laborales (SST)

**Plantilla**: Riesgos laborales *(nuevo)*

#### Campos pre-rellenados

- *Categoría de datos*: "Datos identificativos del trabajador, datos de accidentes laborales, datos de licencias médicas, datos de exámenes de empleo, datos de mutuelle (ACHS)"
- *Base legal*: **Obligación legal** (DS 594, normativa mutual)
- *Plazo*: "5 años desde el registro del accidente"
- `datos_sensibles`: **true**
- `tipo_dato_sensible`: "Salud (física o mental)"

#### Observación

> Los datos de salud laboral son sensibles — requieren medidas de seguridad reforzadas. El reporte a la mutual es obligatorio.

#### Completitud: ~65%

---

## FASE 3 · Dashboard y análisis de alertas

### Cómo interpretar el dashboard de RetailPro

Una vez creados los 12 procesos, el dashboard mostrará:

#### KPIs esperados

| KPI | Valor esperado | Por qué |
|-----|---------------|---------|
| Total de procesos | 12 | Los creados |
| Completitud promedio | ~65-70% | Hay varios con EIPD pendiente y campos manuales por completar |
| Datos sensibles | 5 | Empleados, biométricos, pacientes, riesgos laborales, empleados |
| Requieren EIPD | 3 | Biométricos, pacientes, empleados ( salud) |
| EIPDs pendientes | 3 | Las 3 EIPDs no están completadas aún |

#### 4 KPIs nuevos agregados (hoy)

| KPI | Valor esperado | Significado |
|-----|---------------|-------------|
| EIPDs pendientes | 3 | Procesos que requieren EIPD pero aún no completada |
| Transf. sin garantías | 1 | CRM con transferencia USA sin garantías documentadas |
| Int. legítimo sin test | 2 | Videovigilancia + Evaluación de desempeño |
| Encargados sin contrato | 0 | En este caso sí tienen contrato |

#### Alertas de cumplimiento esperadas

1. ⚠️ **Datos sensibles**: 5 procesos los tratan → verificar base legal y medidas
2. 📋 **EIPD requerida**: 3 procesos
3. 🌐 **Transferencia internacional**: 1 proceso (CRM → USA)
4. ⚖️ **Interés legítimo sin test**: 2 procesos
5. 📋 **EIPDs pendientes**: 3 procesos

---

## FASE 4 · Simulación de brecha de seguridad

### Escenario

Hackean el sistema de CRM de RetailPro. Exponen emails, nombres y teléfonos de 8.000 clientes. El ataque ocurre el 28 de abril a las 14:00.

### Paso a paso en el sistema

1. **Registrar la brecha**: Ir a **Brechas** → "+ Registrar brecha"

2. **Formulario**:
   - *Descripción*: "Acceso no autorizado a base de datos CRM. Exposición de datos identificativos de clientes (nombre, email, teléfono). 8.000 registros comprometidos."
   - *Fecha de detección*: 28/04/2026 14:00
   - *Datos comprometidos*: "Nombre, email y teléfono de 8.000 clientes del CRM"
   - *RATs afectados*: "Gestión de clientes CRM (Proceso #1)"
   - *Medidas adoptadas*: "Contención inmediata: bloqueo de acceso, cambio de credenciales, notificación a clientes afectados"

3. **Badge de plazo**:
   - Inicialmente muestra: **⚠️ 72h restantes** (72 - horas transcurridas)
   - Después de 72h desde detección: **⏰ VENCIDO** (en rojo)

4. **Marcar notificaciones**:
   - `notificado_apdc: true` → se registra fecha de notificación
   - `notificado_titulares: true` → sin dilación (datos sensibles/email)

### Quién debe ser notificado

| Destinatario | ¿Obligatorio? | Plazo |
|---------------|---------------|-------|
| APDC | **Sí** — Art. 14 bis | 72 horas desde detección |
| Titulares afectados | **Sí** — si hay datos sensibles | Sin dilación |

### Qué debe contener la notificación a la APDC

1. Naturaleza de la brecha
2. Categorías de datos afectados
3. Consecuencias probables
4. Medidas adoptadas o propuestas
5. Datos de contacto del DPO

---

## FASE 5 · Reportes y filtros

### Menú de Reportes

Accesible desde el Sidebar: **📊 Reportes**

#### Filtros disponibles

| Filtro | Tipo | Ejemplo de uso |
|--------|------|---------------|
| **Búsqueda por nombre** | Texto libre | "Buscar: CRM" → muestra solo gestión de clientes |
| **Estado** | Selector | "borrador", "completo", "en_revision", "aprobado" |
| **Base legal** | Selector | "Obligación legal" → muestra todos los procesos con esa base |
| **Categoría de titulares** | Texto | "Empleados" → filtra procesos con ese titular |
| **Datos sensibles** | Toggle | Muestra solo los que tratan datos sensibles |
| **Requieren EIPD** | Toggle | Muestra procesos con EIPD requerida |
| **Transferencia internacional** | Toggle | Muestra procesos con transferencia al exterior |

#### Casos de uso del reporte

| Escenario | Filtros a aplicar |
|----------|-----------------|
| "Necesito todos los procesos en borrador" | Estado = borrador |
| "Necesito procesos con datos sensibles para audit" | Datos sensibles = true |
| "Revisar todos los procesos con base legal consentimiento" | Base legal = Consentimiento del titular |
| "Ver procesos que requieren EIPD para gestionar contractor" | Requieren EIPD = true |
| "Reporte de transferencia internacional para presentar a la APDC" | Transferencia internacional = true |
| "Buscar todos los procesos creados por mgarcia" | created_by = mgarcia |

#### Exportación desde reportes

Desde la misma página de reportes se puede usar el wizard de 4 pasos para crear nuevos procesos, o ir a **Procesos RAT** para exportar CSV/PDF de toda la empresa.

---

## FASE 6 · Interpreting el % de completitud

### Cómo se calcula

```
Campos obligatorios (7):
  1. nombre_proceso
  2. categoria_datos
  3. categoria_titulares
  4. finalidad
  5. base_legal
  6. fuente_datos
  7. plazo_retencion

Campos recomendados (3):
  8. medidas_seguridad
  9. destinatarios
  10. transferencia_datos

Total = 10 campos
% = (completados / 10) × 100
```

### Tabla de interpretación

| % | Nivel | Significado |
|---|-------|-------------|
| 100% | Óptimo | Todos los campos completados. Listo para fiscalización. |
| 80-99% | Bueno | Campos obligatorios OK, faltan recomendados. Completar para mayor protección. |
| 60-79% | Regular | Obligatorios OK. Algunos recomendados pendientes. Revisar faltantes. |
| 40-59% | Bajo | Faltan campos obligatorios. No está protegido ante auditoría de la APDC. |
| <40% | Crítico | Proceso incompleto. Urgente completar campos obligatorios. |

### Qué esperar en RetailPro

| Proceso | Completitud | Nivel |
|---------|-------------|-------|
| Gestión clientes CRM | ~85% | Bueno |
| Nómina | ~75% | Regular |
| Control biométrico | ~60% | Regular (EIPD pendiente) |
| Proveedores | ~70% | Regular |
| Reclutamiento | ~65% | Regular |
| Videovigilancia | ~70% | Regular (sin test IL) |
| Marketing | ~65% | Regular |
| Pacientes | ~60% | Regular (EIPD pendiente) |
| Administración | ~75% | Regular |
| Contabilidad | ~70% | Regular |
| Evaluación desempeño | ~65% | Regular (sin test IL) |
| Riesgos laborales | ~65% | Regular |

**Promedio esperado**: ~68-70%

---

## FASE 7 · Validación end-to-end

### Checklist de verificación

Después de seguir este caso de estudio, el sistema debería mostrar:

- [ ] Login funcional con `admin` / `admin1234`
- [ ] Onboarding visible si no hay empresas (nueva BD)
- [ ] Empresa "RetailPro Chile SpA" creada y activa
- [ ] 12 procesos RAT creados
- [ ] Dashboard: total = 12, datos_sensibles = 5, requieren_eipd = 3
- [ ] Dashboard: eipd_pendientes = 3, transferencias_sin_garantias = 1, interes_legitimo_sin_test = 2
- [ ] Alertas visibles en dashboard: todas las listadas en FASE 3
- [ ] Brecha de seguridad registrada en /breaches con badge de plazo correcto
- [ ] Reportes accesibles en /reportes con todos los filtros funcionando
- [ ] Filtro "Datos sensibles = true" muestra exactamente 5 procesos
- [ ] Filtro "Requieren EIPD = true" muestra exactamente 3 procesos
- [ ] Build exitoso: `npm run build` sin errores

---

## Resumen de cambios en el sistema

### Archivos modificados

| Archivo | Cambio |
|---------|--------|
| `backend/app/services/suggestion_service.py` | +3 nuevos tipos: contabilidad, evaluación desempeño, riesgos laborales + aliases |
| `frontend-next/lib/api.ts` | + función `getReportes()` con filtros avanzados; handle() ahora redirige a /login en 401 |
| `frontend-next/app/(app)/reportes/page.tsx` | Nueva página de reportes con todos los filtros |
| `frontend-next/components/layout/Sidebar.tsx` | Agregado "Reportes" en navegación |
| `frontend-next/app/(app)/layout.tsx` | Ruteo para /reportes; validación de sesión con /auth/me |
| `frontend-next/app/login/page.tsx` | Redirect a /onboarding si no hay empresas |
| `frontend-next/app/onboarding/page.tsx` | **NUEVO** — pantalla de bienvenida y creación de empresa |
| `frontend-next/context/AppContext.tsx` | Validación de sesión con /auth/me al iniciar |
| `backend/app/routes/rats.py` | Endpoint `GET /rats/reportes` con filtros |
| `docs/caso_estudio.md` | Este documento |
| `docs/flujo_datos.md` | Actualizado con onboarding y validación 401 |

### Archivos nuevos

- `frontend-next/app/(app)/reportes/page.tsx`
- `frontend-next/app/onboarding/page.tsx`
- `docs/casos_de_uso/CASO_01_Onboarding_Primera_Empresa.md`
- `docs/casos_de_uso/CASO_02_Crear_Primer_Proceso_RAT.md`
- `docs/casos_de_uso/CASO_03_Plantillas_Inteligentes.md`
- `docs/casos_de_uso/CASO_04_Deteccion_Incumplimiento.md`
- `docs/casos_de_uso/CASO_05_Registrar_Brecha_Seguridad.md`
- `docs/casos_de_uso/CASO_06_Exportar_Evidencia_Auditoria.md`
- `docs/casos_de_uso/README.md`

---

## Glosario rápido

| Término | Significado |
|---------|-------------|
| RAT | Registro de Actividades de Tratamiento (Art. 16 Ley 21.719) |
| EIPD | Evaluación de Impacto en Protección de Datos (Art. 15 bis) |
| APDC | Agencia de Protección de Datos Personales de Chile |
| DPO | Delegado de Protección de Datos |
| SCC | Cláusulas Contractuales Tipo (Standard Contractual Clauses) |
| Art. 16 BIS | Norma específica para datos biométricos de identificación |
| DS 594 | Decreto Supremo 594 — Reglamento sobre condiciones sanitarias |