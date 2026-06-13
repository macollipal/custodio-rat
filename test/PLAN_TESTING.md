# Plan de Testing — Custodio RAT Manager v1.2 Beta

**Fecha:** 2026-06-08
**Alcance:** Testing funcional completo de todas las páginas, flujos, filtros, botones, links, modals y drawers del frontend Next.js + validación del backend FastAPI.
**Stack:** pytest (backend), Playwright (frontend), PostgreSQL (QA Neon)
**Rol:** Test Architect + Automation Engineer

---

## Resumen Ejecutivo

El sistema Custodio RAT Manager tiene **22 páginas** con más de **250 elementos interactivos** (botones, inputs, selects, checkboxes, tabs, drawers, modals). Este plan documenta cada caso de prueba, clasificado por prioridad (P0/P1/P2/P3), por módulo funcional y por tipo de testing (happy path, edge case, security, compliance).

**Cobertura objetivo:** 100% de elementos P0/P1, 80% de P2.

---

## Metodología

### Pirámide de Testing

```
        /\
       /  \      E2E (Playwright) — flujos completos de usuario
      /----\     Integration (pytest + TestClient) — endpoints + RBAC
     /      \    Unit (pytest) — modelos, formulas, servicios
    /________\
```

### Clasificación de prioridad

| Prioridad | Descripción | Cobertura objetivo |
|-----------|-------------|---------------------|
| **P0** | Funcionalidad crítica (auth, CRUD RAT, RBAC, IDOR) | 100% |
| **P1** | Funcionalidad importante (export, filtros, brechas, ARCO) | 100% |
| **P2** | Funcionalidad secundaria (UI, notificaciones, etc.) | 80% |
| **P3** | Casos edge y optimización | 50% |

---

## Módulo 1: Autenticación

### 1.1 Login Page — `/login`

#### Elementos interactivos

| ID | Elemento | Tipo | Descripción |
|----|----------|------|-------------|
| LOGIN-001 | Campo username | input text | Placeholder: "tu.usuario", autocomplete: username |
| LOGIN-002 | Campo password | input password | Placeholder: "••••••••", autocomplete: current-password |
| LOGIN-003 | Botón "Ingresar al sistema" | primary button | Submit del formulario |

#### Casos de prueba

| ID | Caso | Prioridad | Tipo | Resultado esperado |
|----|------|-----------|------|-------------------|
| AUTH-001 | Login con credenciales válidas (superadmin) | P0 | Happy path | Redirige a dashboard, muestra nombre de usuario |
| AUTH-002 | Login con credenciales válidas (admin_empresa) | P0 | Happy path | Redirige a dashboard, selector de empresa visible |
| AUTH-003 | Login con credenciales válidas (usuario) | P0 | Happy path | Redirige a dashboard, sin botón crear RAT |
| AUTH-004 | Login con username inexistente | P0 | Edge | Toast error "Usuario o contraseña incorrectos", sin redirect |
| AUTH-005 | Login con contraseña incorrecta | P0 | Edge | Toast error "Usuario o contraseña incorrectos", sin redirect |
| AUTH-006 | Login con campos vacíos (username vacío) | P1 | Edge | Validación HTML5 required, no envío |
| AUTH-007 | Login con campos vacíos (password vacío) | P1 | Edge | Validación HTML5 required, no envío |
| AUTH-008 | Login con SQL injection en username | P0 | Security | No permite acceso, muestra error genérico |
| AUTH-009 | Login con XSS en username | P1 | Security | No ejecuta script, muestra texto plano |
| AUTH-010 | Login con token JWT vencido en localStorage | P1 | Edge | Redirige a login |
| AUTH-011 | Login dos veces rápido (double submit) | P2 | Edge | Solo crea una sesión |
| AUTH-012 | Login desde otro dispositivo mientras session activa | P1 | Security | Sesión anterior se mantiene activa |
| AUTH-013 | Login con caracteres especiales en password | P2 | Edge | Acepta cualquier caracter UTF-8 |
| AUTH-014 | Login con email en vez de username | P1 | Edge | Rechaza, username esperado |
| AUTH-015 | Presionar Enter en campo password | P1 | Happy path | Envía formulario |
| AUTH-016 | Click en placeholder del navegador (autofill) | P1 | Edge | Autofill funciona correctamente |
| AUTH-017 | Login con empresa deshabilitada | P0 | Edge | Rechaza, empresa no tiene acceso |

#### Checklist de verificación visual

- [ ] Página centrada verticalmente
- [ ] Logo Custodio visible
- [ ] Campos tienen labels correctos
- [ ] Placeholder visible
- [ ] Botón deshabilitado durante loading (spinner)
- [ ] Toast de error aparece en rojo
- [ ] Redirección a dashboard al успех

---

### 1.2 Logout

| ID | Caso | Prioridad | Tipo | Resultado esperado |
|----|------|-----------|------|-------------------|
| AUTH-020 | Logout desde sidebar | P0 | Happy path | Token agregado a blacklist, redirige a login |
| AUTH-021 | Logout y acceso inmediato con mismo token | P0 | Security | 401, token en blacklist |
| AUTH-022 | Logout desde múltiples tabs | P1 | Edge | Todos los tabs redirigen a login |

---

### 1.3 Refresh Token

| ID | Caso | Prioridad | Tipo | Resultado esperado |
|----|------|-----------|------|-------------------|
| AUTH-030 | Refresh con token válido | P0 | Happy path | Nuevo access token recibido |
| AUTH-031 | Refresh con token expirado | P0 | Edge | 401, redirige a login |
| AUTH-032 | Refresh usado dos veces (rotation) | P0 | Security | Primer uso OK, segundo uso 401 |
| AUTH-033 | Refresh sin token | P1 | Edge | 401 |

---

### 1.4 Cambiar Contraseña — Modal

| ID | Elemento | Tipo | Descripción |
|----|----------|------|-------------|
| PASS-001 | Botón "Cambiar contraseña" (sidebar) | button | Abre PasswordModal |
| PASS-002 | Campo contraseña actual | input password | Validación required |
| PASS-003 | Campo nueva contraseña | input password | Mínimo 8 caracteres |
| PASS-004 | Campo confirmar nueva contraseña | input password | Debe coincidir con nueva |
| PASS-005 | Botón "Cambiar" | primary button | Envía cambio |
| PASS-006 | Botón "Cancelar" | secondary button | Cierra modal |

| ID | Caso | Prioridad | Tipo | Resultado esperado |
|----|------|-----------|------|-------------------|
| AUTH-040 | Cambiar contraseña con datos correctos | P1 | Happy path | Toast success, modal cerrado |
| AUTH-041 | Cambiar contraseña actual incorrecta | P1 | Edge | Toast error "Contraseña actual incorrecta" |
| AUTH-042 | Nueva contraseña no coincide | P1 | Edge | Toast error "Las contraseñas no coinciden" |
| AUTH-043 | Nueva contraseña < 8 caracteres | P1 | Edge | Validación frontend |
| AUTH-044 | Campos vacíos en formulario | P1 | Edge | Validación required |
| AUTH-045 | Token expira durante cambio de contraseña | P1 | Edge | Redirige a login |

---

## Módulo 2: Dashboard — `/dashboard`

### Elementos interactivos

| ID | Elemento | Tipo | Descripción |
|----|----------|------|-------------|
| DASH-001 | KPI Cards (5 métricas) | card | Muestra: total rats, completitud, datos sensibles, EIPD, transferencias |
| DASH-002 | StatusChart | chart | Gráfico de barras por estado |
| DASH-003 | AlertBanner | alert | Alertas de Rats vencidos o por vencer |
| DASH-004 | OnboardingChecklist (6 pasos) | checklist | Barra de progreso + botones CTA |
| DASH-005 | Botón "Crear primer proceso" (Onboarding) | primary button | Navega a /rat con wizard |
| DASH-006 | Botón "Registrar primera brecha" (Onboarding) | primary button | Navega a /breaches |
| DASH-007 | Botón "Definir encargado" (Onboarding) | primary button | Navega a /encargados-contrato |
| DASH-008 | Botón "Configurar transparencia" (Onboarding) | primary button | Navega a /transparencia |
| DASH-009 | Botón "Ver configuración" (Onboarding) | secondary button | Navega a /configuracion |
| DASH-010 | Selector de empresa (sidebar) | select | Cambia empresa activa |

### Casos de prueba

| ID | Caso | Prioridad | Tipo | Resultado esperado |
|----|------|-----------|------|-------------------|
| DASH-100 | Dashboard con datos cargados (empresa con RATs) | P0 | Happy path | KPIs muestran números, gráfico renderiza |
| DASH-101 | Dashboard empresa sin RATs | P0 | Happy path | KPIs en 0, gráfico vacío, OnboardingChecklist visible |
| DASH-102 | Superadmin ve datos de todas las empresas | P0 | Happy path | Selector de empresa funciona, datos cambian |
| DASH-103 | Admin empresa ve solo su empresa | P0 | Happy path | Selector muestra solo su empresa |
| DASH-104 | Usuario ve dashboard de su empresa | P0 | Happy path | Datos de su empresa |
| DASH-105 | OnboardingChecklist oculto cuando todos los pasos completados | P1 | Edge | Checklist desaparece, KPIs visibles |
| DASH-106 | Click en KPI card | P1 | Edge | Navega a la sección correspondiente |
| DASH-107 | Refresh de página en dashboard | P1 | Edge | Datos persisten |
| DASH-108 | Cambiar de empresa y volver | P1 | Edge | Datos de empresa anterior no persisten |
| DASH-109 | Dark mode toggle | P2 | Edge | Tema cambia a oscuro |
| DASH-110 | Alerta de RAT por vencer muestra fecha correcta | P1 | Compliance | Fecha de vencimiento calculada correctamente |

---

## Módulo 3: RAT — Procesos — `/rat`

### 3.1 RatTable (Vista principal)

#### Elementos interactivos

| ID | Elemento | Tipo | Descripción |
|----|----------|------|-------------|
| RAT-TBL-001 | Botón "+ Nuevo proceso" | primary button (header) | Abre RatWizard (view = 'wizard') |
| RAT-TBL-002 | Campo búsqueda | input text | Placeholder: "Buscar por nombre..." |
| RAT-TBL-003 | Filtro estado | select | Opciones: Todos, Borrador, Completo, En revisión, Aprobado |
| RAT-TBL-004 | Filtro base legal | select | Lista de BASES_LEGALES |
| RAT-TBL-005 | Filtro categoría titulares | input text | Free text |
| RAT-TBL-006 | Toggle "Datos sensibles" | button toggle | Filtro boolean |
| RAT-TBL-007 | Toggle "Requieren EIPD" | button toggle | Filtro boolean |
| RAT-TBL-008 | Toggle "Transf. internacional" | button toggle | Filtro boolean |
| RAT-TBL-009 | Botón "Aplicar filtros" | secondary button | Ejecuta búsqueda con filtros |
| RAT-TBL-010 | Botón "Limpiar filtros" | secondary button | Limpia todos los filtros |
| RAT-TBL-011 | Selector columnas (☰ Columnas) | button + dropdown | 14 columnas configurables |
| RAT-TBL-012 | Botón "Exportar CSV" | secondary button | Descarga CSV de empresa |
| RAT-TBL-013 | Botón "Exportar PDF" | secondary button | Descarga PDF de empresa |
| RAT-TBL-014 | Fila de RAT (expandible) | row click | Expande para ver detalle + auditoría |
| RAT-TBL-015 | Botón "Editar" (fila expandida) | icon button | Abre RatEditForm (view = 'edit') |
| RAT-TBL-016 | Botón "Duplicar" (fila expandida) | icon button | Abre RatWizard pre-llenado |
| RAT-TBL-017 | Botón "Eliminar" (fila expandida) | icon button | Confirmación + DELETE |
| RAT-TBL-018 | CompletitudBar (en fila) | bar | Muestra % de completitud |
| RAT-TBL-019 | Badge estado (en fila) | badge | Color según estado |
| RAT-TBL-020 | Paginación: Primera ( « ) | button | Ir a página 0 |
| RAT-TBL-021 | Paginación: Anterior ( ‹ ) | button | Ir a página anterior |
| RAT-TBL-022 | Paginación: Siguiente ( › ) | button | Ir a página siguiente |
| RAT-TBL-023 | Paginación: Última ( » ) | button | Ir a última página |
| RAT-TBL-024 | Indicador de página | text | "Página X de Y" |

#### Casos de prueba

| ID | Caso | Prioridad | Tipo | Resultado esperado |
|----|------|-----------|------|-------------------|
| RAT-100 | Listar RATs con datos existentes | P0 | Happy path | Tabla muestra filas con datos |
| RAT-101 | Lista vacía (empresa sin RATs) | P0 | Happy path | Mensaje "No hay procesos registrados" + botón crear |
| RAT-102 | Búsqueda por nombre (coincidencia exacta) | P0 | Happy path | Filtra resultados correctamente |
| RAT-103 | Búsqueda por nombre (coincidencia parcial) | P0 | Happy path | Filtra con LIKE %texto% |
| RAT-104 | Búsqueda con caracteres especiales | P1 | Edge | No causa error SQL |
| RAT-105 | Filtro por estado (cada opción) | P0 | Happy path | Filtra por estado correcto |
| RAT-106 | Filtro por base legal | P0 | Happy path | Filtra por base legal correcta |
| RAT-107 | Filtro por categoría titulares | P1 | Happy path | Filtra por texto parcial |
| RAT-108 | Toggle datos_sensibles = true | P0 | Happy path | Muestra solo RATs con datos_sensibles = true |
| RAT-109 | Toggle EIPD = true | P0 | Happy path | Muestra solo RATs con evaluacion_impacto = true |
| RAT-110 | Toggle transferencia_internacional = true | P1 | Happy path | Muestra solo RATs con transferencia = true |
| RAT-111 | Múltiples filtros combinados | P0 | Happy path | AND entre filtros |
| RAT-112 | Filtro que retorna 0 resultados | P1 | Edge | Mensaje "No se encontraron resultados" |
| RAT-113 | Click en fila expande detalle | P0 | Happy path | Panel expandido con detalle + auditoría |
| RAT-114 | Expandir dos filas simultáneamente | P1 | Edge | Solo última expandida |
| RAT-115 | Click en "Editar" abre RatEditForm | P0 | Happy path | View cambia a 'edit' con datos cargados |
| RAT-116 | Click en "Duplicar" abre RatWizard pre-llenado | P1 | Happy path | Wizard con datos pre-llenados |
| RAT-117 | Click en "Eliminar" muestra confirmación | P0 | Happy path | Modal de confirmación |
| RAT-118 | Confirmar eliminación | P0 | Happy path | RAT eliminado, tabla actualizada, toast success |
| RAT-119 | Cancelar eliminación | P0 | Edge | Modal cerrado, RAT no eliminado |
| RAT-120 | Eliminar y immediately expandir otra fila | P1 | Edge | Estado de expandido se reinicia |
| RAT-121 | Exportar CSV con RATs | P0 | Happy path | Descarga archivo CSV con headers correctos |
| RAT-122 | Exportar CSV vacío | P1 | Edge | CSV con headers pero sin datos |
| RAT-123 | Exportar PDF con RATs | P0 | Happy path | Descarga archivo PDF con datos |
| RAT-124 | Column picker muestra 14 opciones | P1 | Happy path | Todas las columnas disponibles |
| RAT-125 | Column picker oculta columnas | P1 | Happy path | Columnas seleccionadas visible |
| RAT-126 | Cambiar página | P0 | Happy path | Navega a página seleccionada |
| RAT-127 | Ir a última página | P1 | Happy path | Navega correctamente |
| RAT-128 | Hover en fila muestra fondo azul | P1 | UI | Estilo visual correcto |
| RAT-129 | Dark mode en tabla | P2 | Edge | Tabla visible correctamente |
| RAT-130 | Superadmin ve RATs de todas las empresas | P0 | RBAC | Filtro por empresa aplica |
| RAT-131 | Admin empresa ve solo sus RATs | P0 | RBAC | No ve RATs de otras empresas |
| RAT-132 | Usuario sin botón "Nuevo proceso" | P0 | RBAC | Botón no visible |
| RAT-133 | Usuario sin botones editar/eliminar | P0 | RBAC | Solo puede leer |
| RAT-134 | IDOR: acceder a RAT de otra empresa via URL | P0 | Security | 403 o 404 |

---

### 3.2 RatWizard — Creación de RAT (4 pasos)

#### Elementos interactivos

| ID | Elemento | Tipo | Paso | Descripción |
|----|----------|------|------|-------------|
| WIZ-001 | StepIndicator | indicator | All | Muestra pasos 1-4, paso activo azul |
| WIZ-002 | Botón "Anterior" | secondary button | 2,3,4 | Va al paso anterior |
| WIZ-003 | Botón "Siguiente" | secondary button | 1,2,3 | Va al paso siguiente (valida paso actual) |
| WIZ-004 | Botón "Guardar como borrador" | secondary button | 4 | Guarda RAT en estado borrador |
| WIZ-005 | Botón "Guardar proceso" | primary button | 4 | Guarda RAT completo |

#### Paso 1 — Identificación

| ID | Elemento | Tipo | Required | Descripción |
|----|----------|------|---------|-------------|
| WIZ-101 | nombre_proceso | input text | **Sí** | Nombre del proceso |
| WIZ-102 | categoria_titulares | select | **Sí** | Categoría de titulares |
| WIZ-103 | fuente_datos | textarea | **Sí** | Fuente de los datos |
| WIZ-104 | destinatarios | textarea | No | Destinatarios externos |
| WIZ-105 | nombre_encargado | input text | No | Nombre del encargado |
| WIZ-106 | tiene_contrato_encargado | checkbox | No | Indica si hay contrato |
| WIZ-107 | "Siguiente" button | button | — | Valida campos requeridos |

#### Paso 2 — Datos Tratados

| ID | Elemento | Tipo | Required | Descripción |
|----|----------|------|---------|-------------|
| WIZ-201 | categoria_datos | select | **Sí** | Categoría de datos |
| WIZ-202 | datos_sensibles | checkbox | No | Flag de datos sensibles |
| WIZ-203 | tipo_dato_sensible | select | Depende | Visible si datos_sensibles = true |
| WIZ-204 | evaluacion_impacto | checkbox | No | Requiere EIPD |
| WIZ-205 | estado_eipd | select | Depende | Visible si evaluacion_impacto = true |
| WIZ-206 | fecha_eipd | input date | Depende | Visible si evaluacion_impacto = true |
| WIZ-207 | decisiones_automatizadas | checkbox | No | Flag decisiones automatizadas |

#### Paso 3 — Finalidad y Base Legal

| ID | Elemento | Tipo | Required | Descripción |
|----|----------|------|---------|-------------|
| WIZ-301 | finalidad | textarea | **Sí** | Finalidad del tratamiento |
| WIZ-302 | base_legal | select | **Sí** | Base legal del tratamiento |
| WIZ-303 | test_interes_legitimo | textarea | Depende | Visible si base_legal = "interes_legitimo" |
| WIZ-304 | documento_legal | file input | No | Upload de documento (PDF, JPG, PNG) |

#### Paso 4 — Almacenamiento y Transferencias

| ID | Elemento | Tipo | Required | Descripción |
|----|----------|------|---------|-------------|
| WIZ-401 | plazo_retencion | input number | **Sí** | Plazo en meses |
| WIZ-402 | medidas_seguridad | textarea | No | Medidas de seguridad |
| WIZ-403 | transferencia_datos | textarea | No | Transferencia de datos |
| WIZ-404 | transferencia_internacional | checkbox | No | Flag transferencia internacional |
| WIZ-405 | pais_destino | input text | Depende | Visible si transferencia_internacional = true |
| WIZ-406 | garantias_transferencia_int | textarea | Depende | Visible si transferencia_internacional = true |

#### Casos de prueba — RatWizard

| ID | Caso | Prioridad | Tipo | Resultado esperado |
|----|------|-----------|------|-------------------|
| WIZ-500 | Crear RAT completo válido (todos los campos) | P0 | Happy path | RAT creado, redirige a tabla, toast success |
| WIZ-501 | Crear RAT solo con campos obligatorios (7) | P0 | Happy path | RAT creado, completitud 70% |
| WIZ-502 | Crear RAT sin campos obligatorios (validation) | P0 | Edge | Error en campo requerido, no avanza |
| WIZ-503 | Navegar paso 1 → paso 2 → paso 3 → paso 4 | P0 | Happy path | StepIndicator actualiza, datos preservados |
| WIZ-504 | Navegar atrás de paso 4 a paso 1 | P0 | Happy path | Datos preservados en todos los pasos |
| WIZ-505 | Saltar de paso 1 a paso 3 directamente | P1 | Edge | No permite, debe pasar por paso 2 |
| WIZ-506 | Hacer click en step indicator de paso pasado | P1 | Edge | Permite navegar a pasos anteriores |
| WIZ-507 | Toggle datos_sensibles muestra tipo_dato_sensible | P0 | Happy path | Select aparece con 7 opciones |
| WIZ-508 | Toggle evaluacion_impacto muestra estado_eipd y fecha_eipd | P0 | Happy path | Campos aparecen correctamente |
| WIZ-509 | Base legal = interes_legitimo muestra test | P0 | Happy path | Textarea de 3 pasos aparece |
| WIZ-510 | Toggle transferencia_internacional muestra pais y garantías | P0 | Happy path | Campos aparecen correctamente |
| WIZ-511 | Upload documento legal (PDF válido) | P1 | Happy path | Archivo adjuntado, nombre visible |
| WIZ-512 | Upload documento legal (JPG válido) | P2 | Edge | Acepta formatos válidos |
| WIZ-513 | Upload documento legal (EXE inválido) | P1 | Security | Rechaza, mensaje de error |
| WIZ-514 | Upload documento legal (>10MB) | P1 | Edge | Rechaza por tamaño |
| WIZ-515 | Plazo retención = 0 | P1 | Edge | Validación rechaza o acepta con warning |
| WIZ-516 | Plazo retención negativo | P1 | Edge | Validación rechaza |
| WIZ-517 | Nombre proceso > 255 caracteres | P1 | Edge | Validación rechaza o trunca |
| WIZ-518 | Guardar como borrador (campos incompletos) | P0 | Happy path | RAT creado en estado borrador |
| WIZ-519 | Guardar proceso sin paso 4 | P1 | Edge | No permite, debe completar paso 4 |
| WIZ-520 | Draft guardado en localStorage se preserva | P1 | Edge | Refrescar página no pierde datos |
| WIZ-521 | Abrir wizard, escribir, cerrar, abrir de nuevo | P1 | Edge | Draft anterior aparece |
| WIZ-522 | Duplicar RAT pre-llena todos los campos | P1 | Happy path | Wizard abierto con datos del original |
| WIZ-523 | Base legal = consentimiento muestra consent requirements | P2 | Edge | Información adicional visible |
| WIZ-524 | Nombre de proceso duplicado | P1 | Edge | Permite crear, no hay restricción de nombres únicos |
| WIZ-525 | Todas las categorías de datos sensibles (7) | P2 | Edge | Cada tipo se guarda correctamente |

---

### 3.3 RatEditForm — Edición de RAT

#### Elementos interactivos

Los mismos que el Wizard (4 pasos) más:

| ID | Elemento | Tipo | Descripción |
|----|----------|------|-------------|
| EDIT-001 | Botón "Volver" | secondary button | Retorna a RatTable sin guardar |
| EDIT-002 | Botón "Guardar cambios" | primary button | Envía PUT al backend |
| EDIT-003 | Campo estado | select | Estado del RAT (borrador, completo, en_revision, aprobado) |
| EDIT-004 | Campo observaciones_auditoria | textarea | Notas de auditoría |

#### Casos de prueba — RatEditForm

| ID | Caso | Prioridad | Tipo | Resultado esperado |
|----|------|-----------|------|-------------------|
| EDIT-500 | Editar RAT cambiando nombre | P0 | Happy path | Cambio persiste, toast success |
| EDIT-501 | Editar RAT todos los campos | P0 | Happy path | Todos los cambios guardados |
| EDIT-502 | Editar RAT sin campos obligatorios | P0 | Edge | Validación rechaza |
| EDIT-503 | Cambiar estado de borrador a completo | P0 | Happy path | Estado actualizado |
| EDIT-504 | Agregar observaciones de auditoría | P1 | Happy path | Texto guardado |
| EDIT-505 | Click en "Volver" sin guardar cambios | P1 | Edge | Confirmación antes de salir |
| EDIT-506 | Editar y guardar, inmediatamente editar de nuevo | P1 | Edge | Estado fresco cargado |
| EDIT-507 | Editar RAT de otra empresa (IDOR) | P0 | Security | 403 o redirect |
| EDIT-508 | Editar RAT que fue eliminado por otro usuario | P0 | Edge | 404, toast error |
| EDIT-509 | Cambiar base legal a interes_legitimo sin test | P1 | Edge | Validación solicita test |
| EDIT-510 | Upload nuevo documento reemplaza anterior | P1 | Edge | Anterior se elimina |

---

## Módulo 4: Empresas — `/companies`

### Elementos interactivos

| ID | Elemento | Tipo | Descripción |
|----|----------|------|-------------|
| COMP-001 | Botón "+ Nueva empresa" | primary button | Abre CompanyForm |
| COMP-002 | Botón "+ Nuevo usuario" | secondary button | Abre CreateUserModal (superadmin) |
| COMP-003 | Campo búsqueda | input text | Filtra empresas por nombre |
| COMP-004 | Card empresa: botón "Seleccionar" | primary button | Selecciona empresa activa |
| COMP-005 | Card empresa: botón "Editar" | secondary button | Muestra CompanyEditForm inline |
| COMP-006 | Card empresa: botón "Gestionar accesos" | toggle button | Abre UserAccessPanel |
| COMP-007 | Card empresa: botón "Listado usuarios" | secondary button | Abre CompanyUsersModal |
| COMP-008 | Card empresa: botón "Eliminar" | danger button | Confirmación inline |
| COMP-009 | Card empresa: botón "Confirmar eliminación" | danger button | Ejecuta DELETE |
| COMP-010 | Card empresa: botón "Cancelar" (delete) | secondary button | Cancela confirmación |

#### CompanyForm (Create)

| ID | Elemento | Tipo | Required | Descripción |
|----|----------|------|---------|-------------|
| COMP-101 | nombre (Razón social) | input text | **Sí** | |
| COMP-102 | rut | input text | **Sí** | Validación RUT chileno |
| COMP-103 | rubro | input text | No | |
| COMP-104 | direccion | input text | No | |
| COMP-105 | contacto_dpo | input text | No | |
| COMP-106 | email_dpo | input email | No | |
| COMP-107 | descripcion | textarea | No | |
| COMP-108 | Botón "Crear empresa" | primary button | Envía POST |

#### UserAccessPanel

| ID | Elemento | Tipo | Descripción |
|----|----------|------|-------------|
| COMP-201 | Campo username | input text | Usuario a invitar |
| COMP-202 | Select rol | select | admin / editor / viewer |
| COMP-203 | Botón "Agregar" | primary button | Ejecuta invitación |
| COMP-204 | Botón "Remover" (por fila) | danger button | Elimina acceso |

#### CreateUserModal

| ID | Elemento | Tipo | Required | Descripción |
|----|----------|------|---------|-------------|
| COMP-301 | username | input text | **Sí** | |
| COMP-302 | email | input email | **Sí** | |
| COMP-303 | full_name | input text | No | |
| COMP-304 | password | input password | **Sí** | |
| COMP-305 | rol_global | select | No | usuario / admin_empresa / admin |
| COMP-306 | Botón "Crear usuario" | primary button | |

#### Casos de prueba

| ID | Caso | Prioridad | Tipo | Resultado esperado |
|----|------|-----------|------|-------------------|
| COMP-600 | Crear empresa con datos válidos | P0 | Happy path | Empresa creada, aparece en lista |
| COMP-601 | Crear empresa sin campos obligatorios | P0 | Edge | Validación rechaza |
| COMP-602 | Crear empresa con RUT inválido | P0 | Edge | Validación RUT rechaza |
| COMP-603 | Crear empresa con RUT duplicado | P1 | Edge | Rechaza o permite (decidir) |
| COMP-604 | RUT con formato válido (12.345.678-9) | P1 | Happy path | Formateo automático con puntos |
| COMP-605 | Email DPO sin formato | P1 | Edge | Validación HTML5 email |
| COMP-606 | Editar empresa cambiando nombre | P0 | Happy path | Cambio persiste |
| COMP-607 | Editar empresa con RUT duplicado | P1 | Edge | Rechaza |
| COMP-608 | Eliminar empresa con RATs asociados | P0 | Edge | Confirmación adicional o bloqueo |
| COMP-609 | Eliminar empresa sin RATs | P0 | Happy path | Empresa eliminada |
| COMP-610 | Buscar empresa por nombre | P0 | Happy path | Filtra resultados |
| COMP-611 | Buscar empresa que no existe | P1 | Edge | Mensaje "No se encontraron empresas" |
| COMP-612 | Invitar usuario (username existente) | P0 | Happy path | Acceso creado, toast success |
| COMP-613 | Invitar usuario (username inexistente) | P1 | Edge | Error o comportamiento definido |
| COMP-614 | Invitar usuario con rol viewer | P1 | Happy path | Acceso creado con rol viewer |
| COMP-615 | Remover acceso de usuario | P0 | Happy path | Acceso eliminado |
| COMP-616 | Crear usuario global (superadmin) | P0 | Happy path | Usuario creado y asignado a empresa |
| COMP-617 | Crear usuario sin password | P0 | Edge | Validación rechaza |
| COMP-618 | Crear usuario con email duplicado | P1 | Edge | Validación rejects o acepta |
| COMP-619 | Ver listado de usuarios de empresa | P1 | Happy path | Modal muestra tabla |
| COMP-620 | Click en email de usuario abre mailto | P1 | Happy path | Abre cliente de correo |
| COMP-621 | Superadmin ve botón "+ Nuevo usuario" | P0 | RBAC | Visible solo para superadmin |
| COMP-622 | Admin empresa no ve botón "+ Nuevo usuario" | P0 | RBAC | Botón oculto |
| COMP-623 | Admin empresa no ve botón "Eliminar" empresa | P0 | RBAC | Solo superadmin puede eliminar |
| COMP-624 | IDOR: acceder a empresa de otro via URL | P0 | Security | 403 o redirect |
| COMP-625 | Crear empresa con todos los campos opcionales | P1 | Happy path | Empresa creada con todos los datos |

---

## Módulo 5: Usuarios — `/usuarios`

### Elementos interactivos

| ID | Elemento | Tipo | Descripción |
|----|----------|------|-------------|
| USR-001 | Botón "+ Nuevo usuario" | primary button | Abre UserModal |
| USR-002 | Campo búsqueda | input text | Placeholder: "Buscar usuario..." |
| USR-003 | Botón editar (fila) | icon button | Abre UserModal en modo edit |
| USR-004 | Botón eliminar (fila) | danger icon | Abre confirmación delete |
| USR-005 | Modal eliminar: botón "Cancelar" | secondary | Cierra modal |
| USR-006 | Modal eliminar: botón "Eliminar" | danger button | Ejecuta DELETE |

#### UserModal (Create/Edit)

| ID | Elemento | Tipo | Required | Notes |
|----|----------|------|---------|-------|
| USR-101 | username | input text | **Sí** | Disabled en edit |
| USR-102 | email | input email | **Sí** | |
| USR-103 | full_name | input text | No | |
| USR-104 | password | input password | **Sí** (create) | No requerido en edit |
| USR-105 | newPw (edit mode) | input password | No | Reset password |
| USR-106 | rol_global | select | No | Superadministrador / Admin empresa / Usuario |
| USR-107 | empresa_id | select | **Sí** (si rol != superadmin) | Lista de empresas |
| USR-108 | Botón "Cambiar" (password reset) | secondary | Solo edit | Envía nuevo password |
| USR-109 | Botón "Crear usuario" / "Guardar cambios" | primary button | | |

#### Casos de prueba

| ID | Caso | Prioridad | Tipo | Resultado esperado |
|----|------|-----------|------|-------------------|
| USR-700 | Crear usuario con todos los campos | P0 | Happy path | Usuario creado, visible en lista |
| USR-701 | Crear usuario sin campos requeridos | P0 | Edge | Validación rechaza |
| USR-702 | Crear usuario con email inválido | P0 | Edge | Validación rechaza |
| USR-703 | Crear usuario con username duplicado | P1 | Edge | Rechaza, error 409 o similar |
| USR-704 | Crear usuario admin_empresa sin empresa_id | P0 | Edge | Validación requiere empresa_id |
| USR-705 | Editar usuario cambiando email | P0 | Happy path | Cambio persiste |
| USR-706 | Editar usuario cambiando rol_global | P0 | Happy path | Cambio persiste |
| USR-707 | Reset password de usuario | P1 | Happy path | Password actualizado |
| USR-708 | Reset password con < 8 caracteres | P1 | Edge | Validación rechaza |
| USR-709 | Eliminar usuario | P0 | Happy path | Usuario eliminado de lista |
| USR-710 | Eliminar usuario que tiene actividad | P1 | Edge | Allowed o bloqueado (definir) |
| USR-711 | Buscar usuario por username | P0 | Happy path | Filtra resultados |
| USR-712 | Buscar usuario que no existe | P1 | Edge | Mensaje vacío |
| USR-713 | Solo superadmin ve página /usuarios | P0 | RBAC | Otros roles → 403 |
| USR-714 | Superadmin ve botón "+ Nuevo usuario" | P0 | RBAC | Visible |
| USR-715 | Admin empresa no ve página /usuarios | P0 | RBAC | Redirect a dashboard |
| USR-716 | Click en email de usuario abre mailto | P1 | Happy path | Abre cliente de correo |
| USR-717 | Crear usuario y asignarlo a empresa | P0 | Happy path | Relación user_companies creada |
| USR-718 | Cambiar empresa de un usuario | P1 | Happy path | Relación actualizada |
| USR-719 | Crear usuario con rol superadmin | P1 | Security | Allowed solo para superadmin existente |

---

## Módulo 6: Brechas de Seguridad — `/breaches`

### Elementos interactivos

| ID | Elemento | Tipo | Descripción |
|----|----------|------|-------------|
| BRE-001 | Botón "+ Registrar brecha" | primary button (rojo) | Abre BreachForm en modo create |
| BRE-002 | Breach cards: botón "Editar" | secondary | Abre BreachForm en modo edit |
| BRE-003 | Breach cards: botón "Eliminar" | danger | Confirmación + DELETE |
| BRE-004 | Breach cards: PlazoBadge | badge | Muestra countdown 72h |
| BRE-005 | Breach cards: nivel_riesgo badge | badge | Color según nivel |
| BRE-006 | Botón "Volver al listado" | secondary | Retorna a lista |
| BRE-007 | Botón "Cancelar" (form) | secondary | Cierra form |
| BRE-008 | Botón "✓ Guardar brecha" | primary button (rojo) | Submit |

#### BreachForm

| ID | Elemento | Tipo | Required | Descripción |
|----|----------|------|---------|-------------|
| BRE-101 | descripcion | textarea | **Sí** | Descripción de la brecha |
| BRE-102 | fecha_deteccion | datetime-local | **Sí** | Fecha y hora de detección |
| BRE-103 | rats_afectados | input text | No | RATs involucrados |
| BRE-104 | datos_comprometidos | textarea | No | Datos comprometidos |
| BRE-105 | medidas_adoptadas | textarea | No | Medidas tomadas |
| BRE-106 | notificado_apdc | checkbox | No | ¿Se notificó a APDC? |
| BRE-107 | notificado_titulares | checkbox | No | ¿Se notificó a titulares? |
| BRE-108 | volumen_titulares_afectados | input number | No | Min 0 |
| BRE-109 | incluye_datos_sensibles | checkbox | No | |
| BRE-110 | incluye_datos_nna | checkbox | No | Menores de edad |
| BRE-111 | incluye_datos_financieros | checkbox | No | Datos financieros |

#### Casos de prueba

| ID | Caso | Prioridad | Tipo | Resultado esperado |
|----|------|-----------|------|-------------------|
| BRE-800 | Crear brecha con todos los campos | P0 | Happy path | Brecha creada, card aparece en lista |
| BRE-801 | Crear brecha solo con campos requeridos | P0 | Happy path | Brecha creada |
| BRE-802 | Crear brecha sin descripción | P0 | Edge | Validación rechaza |
| BRE-803 | Crear brecha sin fecha_deteccion | P0 | Edge | Validación rechaza |
| BRE-804 | Fecha de detección futura | P1 | Edge | Allowed o warning |
| BRE-805 | Fecha de notificación APDC anterior a detección | P1 | Edge | Allowed o validación |
| BRE-806 | Toggle notificado_apdc = true | P1 | Happy path | Checkbox marcado |
| BRE-807 | Toggle notificado_titulares = true | P1 | Happy path | Checkbox marcado |
| BRE-808 | Editar brecha existente | P0 | Happy path | Cambios guardados |
| BRE-809 | Eliminar brecha | P0 | Happy path | Brecha eliminada, lista actualizada |
| BRE-810 | PlazoBadge muestra countdown correcto | P0 | Compliance | 72h desde fecha_deteccion |
| BRE-811 | PlazoBadge rojo cuando < 12h | P1 | Edge | Color cambia a rojo |
| BRE-812 | PlazoBadge verde cuando > 48h | P1 | Edge | Color verde |
| BRE-813 | Badge nivel_riesgo muestra color correcto | P1 | Edge | Alto/Medio/Bajo con colores |
| BRE-814 | Crear brecha dispara email a DPO | P0 | Integration | Email enviado o logueado (DRY_RUN) |
| BRE-815 | Leer brecha de otra empresa (IDOR) | P0 | Security | 403 |
| BRE-816 | Editar brecha de otra empresa | P0 | Security | 403 |
| BRE-817 | Volumen = 0 | P1 | Edge | Allowed |
| BRE-818 | Volumen negativo | P1 | Edge | Validación rechaza |
| BRE-819 | Todas las categorías de breach flags | P2 | Edge | Cada checkbox funciona |
| BRE-820 | Click en badge rats_afectados | P2 | Edge | Navega a RATs filtrados |

---

## Módulo 7: Reportes — `/reportes`

### Elementos interactivos

| ID | Elemento | Tipo | Descripción |
|----|----------|------|-------------|
| REP-001 | Botón "📥 CSV" | secondary button | Exporta CSV |
| REP-002 | Botón "📥 PDF" | secondary button | Exporta PDF |
| REP-003 | Botón "🔄 Actualizar" | secondary button | Recarga datos |
| REP-004 | Botón "+ Nuevo proceso" | primary button | Navega a /rat |
| REP-005 | KPI Cards (6 métricas) | card | Total, Completitud, Sensibles, EIPD, Transf.Int, Dec.Auto |
| REP-006 | Mini chart "Por estado" | chart | Barras por estado |
| REP-007 | Mini chart "Por riesgo" | chart | Barras por nivel_riesgo |
| REP-008 | Mini chart "Por base legal" | chart | Barras por base legal |
| REP-009 | Campo búsqueda | input text | "Buscar por nombre..." |
| REP-010 | Select estado | select | Filtro por estado |
| REP-011 | Select base_legal | select | Filtro por base legal |
| REP-012 | Input categoria_titulares | input text | Filtro自由 |
| REP-013 | Toggle "⚠️ Datos sensibles" | button toggle | Filtro boolean |
| REP-014 | Toggle "📋 Requieren EIPD" | button toggle | Filtro boolean |
| REP-015 | Toggle "🌐 Transfer. internacional" | button toggle | Filtro boolean |
| REP-016 | Botón "Aplicar filtros" | secondary button | Aplica todos los filtros |
| REP-017 | Botón "Limpiar filtros" / "Limpiar todos" | secondary button | Limpia filtros |
| REP-018 | Select ordenar por | select | 7 opciones de ordenamiento |
| REP-019 | Botón orden (↓/↑) | toggle button | Asc/Desc |
| REP-020 | Select agrupar por | select | Sin agrupar / Estado / Base legal / Nivel riesgo |
| REP-021 | Botón "☰ Columnas (N)" | button + dropdown | Selector de columnas |
| REP-022 | Checkbox por columna (14) | checkbox | Toggle visibilidad columna |
| REP-023 | Paginación: « ‹ › » | buttons | Navegación de páginas |
| REP-024 | Indicador de página | text | "Página X de Y" |
| REP-025 | Fila de tabla (clickeable) | row | Abre Drawer de detalle |
| REP-026 | Drawer: botón "←" | icon button | Cierra drawer |
| REP-027 | Drawer: botón "📄 Exportar PDF" | secondary button | Descarga PDF individual |
| REP-028 | Chat IA: botón 🤖 | floating button | Abre chat drawer |
| REP-029 | Chat IA: input | text input | Placeholder: "Preguntá sobre la Ley 21.719..." |
| REP-030 | Chat IA: botón enviar (→) | icon button | Envía mensaje |
| REP-031 | Chat IA: botón "✕" | icon button | Cierra drawer |
| REP-032 | Guardar filtro: botón nombre | badge | Carga filtro guardado |
| REP-033 | Guardar filtro: botón "✕" | icon | Elimina filtro guardado |
| REP-034 | Modal guardar filtro: input nombre | text input | Nombre del filtro |
| REP-035 | Modal guardar filtro: botón "Cancelar" | secondary | Cierra modal |
| REP-036 | Modal guardar filtro: botón "Guardar" | primary button | Guarda en localStorage |

#### Casos de prueba

| ID | Caso | Prioridad | Tipo | Resultado esperado |
|----|------|-----------|------|-------------------|
| REP-900 | Reportes muestra KPIs con datos | P0 | Happy path | 6 KPI cards con números |
| REP-901 | Reportes muestra tabla con RATs | P0 | Happy path | Tabla con filas |
| REP-902 | Mini charts renderizan correctamente | P1 | Happy path | 3 gráficos de barras visibles |
| REP-903 | Búsqueda por nombre filtra resultados | P0 | Happy path | Resultados filtrados |
| REP-904 | Filtro por estado filtra correctamente | P0 | Happy path | Solo RATs del estado seleccionado |
| REP-905 | Filtro por base legal filtra correctamente | P0 | Happy path | Solo RATs de esa base legal |
| REP-906 | Filtro por categoria_titulares | P1 | Happy path | Filtra por texto parcial |
| REP-907 | Toggle datos_sensibles = true | P0 | Happy path | Muestra solo RATs con flag |
| REP-908 | Toggle EIPD = true | P0 | Happy path | Muestra solo RATs que requieren EIPD |
| REP-909 | Toggle transferencia = true | P1 | Happy path | Muestra solo RATs con transf. internacional |
| REP-910 | Múltiples filtros combinados | P0 | Happy path | AND entre todos los filtros |
| REP-911 | Filtros retornan 0 resultados | P1 | Edge | Mensaje "No se encontraron resultados" |
| REP-912 | Ordenar por nombre (A-Z) | P0 | Happy path | Tabla ordenada |
| REP-913 | Ordenar por nombre (Z-A) | P0 | Happy path | Tabla ordenada inverso |
| REP-914 | Ordenar por fecha creación | P0 | Happy path | Tabla ordenada por fecha |
| REP-915 | Agrupar por estado | P1 | Happy path | Tabla agrupada con headers |
| REP-916 | Agrupar por base legal | P1 | Happy path | Tabla agrupada con headers |
| REP-917 | Agrupar por nivel riesgo | P1 | Happy path | Tabla agrupada con headers |
| REP-918 | Column picker muestra 14 columnas | P1 | Happy path | Dropdown con checkboxes |
| REP-919 | Ocultar columna específica | P1 | Happy path | Columna no visible en tabla |
| REP-920 | Mostrar todas las columnas | P1 | Happy path | Tabla con 14 columnas |
| REP-921 | Click en fila abre drawer | P0 | Happy path | Drawer con detalle completo |
| REP-922 | Drawer muestra campos vacíos como "**" rojo | P1 | Edge | Campos faltantes marcados |
| REP-923 | Drawer: exportar PDF individual | P0 | Happy path | Descarga PDF del RAT |
| REP-924 | Drawer: auditoría muestra historial | P1 | Happy path | Lista de cambios |
| REP-925 | Exportar CSV con filtros aplicados | P0 | Happy path | CSV solo con resultados filtrados |
| REP-926 | Exportar PDF con filtros aplicados | P0 | Happy path | PDF solo con resultados filtrados |
| REP-927 | Paginación: cambiar de página | P0 | Happy path | Datos de página cargados |
| REP-928 | Paginación: ir a última página | P1 | Happy path | Última página visible |
| REP-929 | Paginación: con filtros activos | P1 | Edge | Paginación recalculada |
| REP-930 | Guardar filtro con nombre | P1 | Happy path | Filtro guardado en localStorage |
| REP-931 | Cargar filtro guardado | P1 | Happy path | Filtros aplicados automáticamente |
| REP-932 | Eliminar filtro guardado | P1 | Happy path | Filtro removido de localStorage |
| REP-933 | Chat IA: enviar pregunta válida | P1 | Happy path | Respuesta del asistente |
| REP-934 | Chat IA: enviar pregunta sobre Ley 21.719 | P1 | Compliance | Responde con contexto legal correcto |
| REP-935 | Chat IA: enviar pregunta vacía | P1 | Edge | No envía, input requerido |
| REP-936 | Chat IA: loading state | P1 | Edge | Muestra "Escribiendo..." |
| REP-937 | Chat IA: cerrar y abrir de nuevo | P1 | Edge | Historial preservado |
| REP-938 | Refresh recarga datos | P1 | Happy path | Datos actualizados |
| REP-939 | Dark mode en reportes | P2 | Edge | Todo visible correctamente |
| REP-940 | Reportes vacío (sin RATs) | P0 | Happy path | Mensaje "No hay procesos" + botón crear |
| REP-941 | Superadmin ve RATs de todas las empresas | P0 | RBAC | Selector de empresa funciona |
| REP-942 | Admin empresa ve solo sus RATs | P0 | RBAC | No ve RATs de otras empresas |
| REP-943 | Usuario puede ver reportes | P0 | RBAC | Acceso de solo lectura |
| REP-944 | IDOR: acceder a RAT de otra empresa via drawer | P0 | Security | 403 o datos ocultos |

---

## Módulo 8: Tickets ARCO — `/tkt_solicitud_derecho`

### Elementos interactivos

| ID | Elemento | Tipo | Descripción |
|----|----------|------|-------------|
| TKT-001 | Botón "+ Nueva Solicitud" | primary button | Abre CreateTicketForm (admin only) |
| TKT-002 | Botón "🔄 Refrescar" | secondary button | Recarga datos |
| TKT-003 | Tabs: Abierto / En Proceso / Pendiente / Resuelto / Vencido / Todos | tabs | Filtro por estado |
| TKT-004 | Tab badge (contador) | badge | Cantidad por estado |
| TKT-005 | Tabla: columna "Ver" | button | Abre TicketDrawer |
| TKT-006 | Tabla: fila completa clickeable | row | Abre TicketDrawer |
| TKT-007 | Tabla: email link | mailto link | Abre cliente de correo |
| TKT-008 | KPI Cards (6 métricas) | card | Total, Abiertos, En Proceso, Pendientes, Resueltos, Vencidos |
| TKT-009 | SLA bar | progress bar | Muestra SLA remaining |

#### CreateTicketForm (Drawer)

| ID | Elemento | Tipo | Required | Descripción |
|----|----------|------|---------|-------------|
| TKT-101 | tipo | select | **Sí** | Acceso / Rectificación / Cancelación / Oposición / Bloqueo / Portabilidad |
| TKT-102 | prioridad | select | No | Alta / Normal / Baja |
| TKT-103 | origen | select | No | Web / Email / Teléfono / Presencial / Manual |
| TKT-104 | titular_nombre | input text | **Sí** | |
| TKT-105 | titular_email | input email | **Sí** | |
| TKT-106 | titular_rut | input text | No | |
| TKT-107 | descripcion | textarea | No | |
| TKT-108 | Botón "Cancelar" | secondary | Cierra drawer | |
| TKT-109 | Botón "Crear Solicitud" | primary button | Submit | |

#### TicketDrawer

| ID | Elemento | Tipo | Descripción |
|----|----------|------|-------------|
| TKT-201 | Botón "←" | icon button | Cierra drawer |
| TKT-202 | Select nuevoEstado | select | Cambiar estado del ticket |
| TKT-203 | Textarea respuesta | textarea | Respuesta formal |
| TKT-204 | Botón "Guardar respuesta" | primary button (verde) | Envía respuesta |
| TKT-205 | Botón "Bloquear RAT" | danger button | Abre sección de bloqueo |
| TKT-206 | Botón "Desbloquear" | primary button (verde) | Ejecuta desbloqueo |
| TKT-207 | Botón "Exportar Portabilidad (JSON)" | primary button (verde) | Descarga JSON |
| TKT-208 | Input nuevaNota | text input | Nota interna |
| TKT-209 | Botón "+" | warning button | Agrega nota |
| TKT-210 | Select RAT (bloqueo) | select | RAT a bloquear |
| TKT-211 | Input plazo días (bloqueo) | number | 1-365 |

#### Casos de prueba

| ID | Caso | Prioridad | Tipo | Resultado esperado |
|----|------|-----------|------|-------------------|
| TKT-600 | Crear ticket con todos los campos | P0 | Happy path | Ticket creado, aparece en lista |
| TKT-601 | Crear ticket solo con campos requeridos | P0 | Happy path | Ticket creado |
| TKT-602 | Crear ticket sin tipo | P0 | Edge | Validación rechaza |
| TKT-603 | Crear ticket sin titular_nombre | P0 | Edge | Validación rechaza |
| TKT-604 | Crear ticket sin titular_email | P0 | Edge | Validación rechaza |
| TKT-605 | Crear ticket con email inválido | P0 | Edge | Validación rechaza |
| TKT-606 | Crear ticket tipo BLOQUEO | P0 | Happy path | Ticket creado con tipo especial |
| TKT-607 | Cambiar estado de ticket (workflow) | P0 | Happy path | Estado actualizado |
| TKT-608 | Agregar respuesta formal | P0 | Happy path | Respuesta guardada |
| TKT-609 | Agregar nota interna | P0 | Happy path | Nota agregada a historial |
| TKT-610 | Bloquear RAT desde ticket | P1 | Happy path | RAT bloqueado |
| TKT-611 | Desbloquear RAT desde ticket | P1 | Happy path | RAT desbloqueado |
| TKT-612 | Exportar portabilidad JSON | P1 | Happy path | Descarga JSON con datos del titular |
| TKT-613 | Filtro por tab (cada estado) | P0 | Happy path | Lista filtrada por estado |
| TKT-614 | Badge de contador actualizado | P1 | Happy path | Contador refleja cantidad real |
| TKT-615 | SLA bar muestra tiempo restante | P1 | Compliance | Barra verde/amarilla/roja según SLA |
| TKT-616 | Ticket vencido muestra en tab "Vencido" | P0 | Edge | Tickets con SLA expirado en tab correcto |
| TKT-617 | Click en email abre mailto | P1 | Happy path | Cliente de correo abre |
| TKT-618 | Ver detalle de ticket | P0 | Happy path | Drawer con toda la información |
| TKT-619 | Refrescar lista de tickets | P1 | Happy path | Lista actualizada |
| TKT-620 | Crear ticket sin permisos (usuario) | P0 | RBAC | Botón oculto, 403 si fuerza |
| TKT-621 | Leer ticket de otra empresa (IDOR) | P0 | Security | 403 |
| TKT-622 | Editar ticket de otra empresa | P0 | Security | 403 |
| TKT-623 | TKT vacío (sin tickets) | P1 | Happy path | Mensaje "No hay solicitudes" |
| TKT-624 | Crear ticket con todos los tipos ARCO (6) | P2 | Edge | Cada tipo se crea correctamente |

---

## Módulo 9: Configuración — `/configuracion`

### Elementos interactivos

| ID | Elemento | Tipo | Descripción |
|----|----------|------|-------------|
| CONF-001 | Tabs: Sistema / Último log / Exportación / Feriados | tabs | Navegación de secciones |
| CONF-002 | Sistema: botón "🔄 Refrescar estado" | primary button | Llama fetchDbHealth() |
| CONF-003 | Sistema: indicador estado DB | status | Muestra healthy/unhealthy |
| CONF-004 | Sistema: indicador latencia | metric | ms de latencia |
| CONF-005 | Exportación: select formato predeterminado | select | PDF / CSV |
| CONF-006 | Exportación: toggle "Nombre de empresa en archivo" | toggle switch | Incluye RUT en nombre de archivo |
| CONF-007 | Exportación: toggle "Incluir historial de auditoría" | toggle switch | Incluye auditoría en PDF |
| CONF-008 | Feriados: select año | select | Selector de año |
| CONF-009 | Feriados: botón "📁 Subir CSV" | button | Trigger file input |
| CONF-010 | Feriados: input file (hidden) | file input | Acepta .csv |
| CONF-011 | Feriados: botón "📥 Descargar CSV ejemplo" | link | Descarga CSV de ejemplo |
| CONF-012 | Feriados: botón "🗑 Eliminar año" | danger button | Elimina feriados del año |
| CONF-013 | Feriados: tabla de feriados | table | Lista de fechas cargadas |
| CONF-014 | Registros: botón 🔄 | secondary | Refresca logs de auditoría |

#### Casos de prueba

| ID | Caso | Prioridad | Tipo | Resultado esperado |
|----|------|-----------|------|-------------------|
| CONF-700 | Ver estado de DB (Sistema tab) | P0 | Happy path | Muestra healthy + latencia |
| CONF-701 | Refrescar estado de DB | P1 | Happy path | Datos actualizados |
| CONF-702 | Cambiar formato predeterminado a CSV | P1 | Happy path | Selección guardada |
| CONF-703 | Toggle nombre con RUT = ON | P1 | Happy path | Toggle activo |
| CONF-704 | Toggle nombre con RUT = OFF | P1 | Happy path | Toggle inactivo |
| CONF-705 | Toggle incluir auditoría = ON | P1 | Happy path | Toggle activo |
| CONF-706 | Toggle incluir auditoría = OFF | P1 | Happy path | Toggle inactivo |
| CONF-707 | Seleccionar año de feriados | P1 | Happy path | Tabla muestra feriados del año |
| CONF-708 | Subir CSV de feriados válido | P0 | Happy path | Feriados cargados, tabla actualizada |
| CONF-709 | Subir CSV de feriados (formato inválido) | P0 | Edge | Error, mensaje de formato incorrecto |
| CONF-710 | Subir CSV vacío | P1 | Edge | Error o 0 registros |
| CONF-711 | Descargar CSV ejemplo | P1 | Happy path | Descarga archivo de ejemplo |
| CONF-712 | Eliminar año de feriados | P1 | Happy path | Feriados eliminados |
| CONF-713 | Ver logs de auditoría | P1 | Happy path | Tabla con registros recientes |
| CONF-714 | Refrescar logs de auditoría | P1 | Happy path | Logs actualizados |
| CONF-715 | Estado DB unhealthy muestra error | P1 | Edge | Mensaje de error visible |
| CONF-716 | Todas las tabs accesibles | P1 | Happy path | Cada tab muestra contenido correcto |
| CONF-717 | Toggle switch estados persisten post-refresh | P1 | Edge | Estado en localStorage o backend |
| CONF-718 | Superadmin ve todas las tabs | P0 | RBAC | Todas visibles |
| CONF-719 | Admin empresa ve todas las tabs | P0 | RBAC | Todas visibles |
| CONF-720 | Usuario ve todas las tabs | P0 | RBAC | Todas visibles (solo lectura) |

---

## Módulo 10: Encargados de Contrato — `/encargados-contrato`

### Elementos interactivos

| ID | Elemento | Tipo | Descripción |
|----|----------|------|-------------|
| ENC-001 | Botón "+ Nuevo Contrato" | primary button | Abre drawer en modo create |
| ENC-002 | Card: botón "Editar" | secondary | Abre drawer en modo edit |
| ENC-003 | Card: botón "Eliminar" | danger | Confirmación + DELETE |

#### Drawer Form

| ID | Elemento | Tipo | Required | Descripción |
|----|----------|------|---------|-------------|
| ENC-101 | nombre_encargado | input text | **Sí** | |
| ENC-102 | objeto | textarea | **Sí** | |
| ENC-103 | duracion_inicio | date | **Sí** | |
| ENC-104 | duracion_fin | date | No | |
| ENC-105 | finalidad | input text | **Sí** | |
| ENC-106 | tipo_datos | input text | **Sí** | |
| ENC-107 | categorias_titulares | input text | **Sí** | |
| ENC-108 | derechos_obligaciones | textarea | **Sí** | |
| ENC-109 | rat_id | select | No | Vinculación a RAT |
| ENC-110 | activo | checkbox | No | Contrato activo |
| ENC-111 | Botón "Cancelar" | secondary | Cierra drawer | |
| ENC-112 | Botón "Guardar" | primary button | Submit | |

#### Casos de prueba

| ID | Caso | Prioridad | Tipo | Resultado esperado |
|----|------|-----------|------|-------------------|
| ENC-500 | Crear contrato con todos los campos | P0 | Happy path | Contrato creado, aparece en lista |
| ENC-501 | Crear contrato solo con campos requeridos | P0 | Happy path | Contrato creado |
| ENC-502 | Crear contrato sin campos requeridos | P0 | Edge | Validación rechaza |
| ENC-503 | duracion_fin anterior a duracion_inicio | P1 | Edge | Validación rechaza |
| ENC-504 | Editar contrato existente | P0 | Happy path | Cambios guardados |
| ENC-505 | Eliminar contrato | P0 | Happy path | Contrato eliminado |
| ENC-506 | Toggle activo = false | P1 | Happy path | Badge "Inactivo" visible |
| ENC-507 | Vincular contrato a RAT | P1 | Happy path | rat_id asociado |
| ENC-508 | Crear contrato sin vincular a RAT | P1 | Happy path | Contrato sin RAT asociado |
| ENC-509 | Leer contrato de otra empresa (IDOR) | P0 | Security | 403 |
| ENC-510 | Editar contrato de otra empresa | P0 | Security | 403 |
| ENC-511 | Contrato vacío (sin contratos) | P1 | Happy path | Mensaje "No hay contratos" |
| ENC-512 | Duración > 5 años | P2 | Edge | Allowed |

---

## Módulo 11: Transparencia — `/transparencia`

### Elementos interactivos

| ID | Elemento | Tipo | Descripción |
|----|----------|------|-------------|
| TRANS-001 | Política completa (11 secciones a-l) | read-only | Display de política |
| TRANS-002 | Versión y SHA-256 | text | Hash de verificación |

#### Casos de prueba

| ID | Caso | Prioridad | Tipo | Resultado esperado |
|----|------|-----------|------|-------------------|
| TRANS-300 | Ver política de transparencia | P0 | Happy path | 11 secciones visibles |
| TRANS-301 | Todas las secciones con contenido | P1 | Edge | Ninguna sección vacía |
| TRANS-302 | Hash SHA-256 visible y correcto | P1 | Compliance | Hash para verificación |
| TRANS-303 | Superadmin ve página | P0 | RBAC | Accesible |
| TRANS-304 | Admin empresa ve página | P0 | RBAC | Accesible |
| TRANS-305 | Usuario ve página | P0 | RBAC | Accesible |
| TRANS-306 | Sin login (público) — no aplicable | P2 | Edge | Redirige a login |

---

## Módulo 12: Onboarding — `/onboarding`

### Elementos interactivos

| ID | Elemento | Tipo | Required | Descripción |
|----|----------|------|---------|-------------|
| ONB-001 | nombre (Razón social) | input text | **Sí** | |
| ONB-002 | rut | input text | **Sí** | Validación RUT chileno |
| ONB-003 | contacto_dpo | input text | No | |
| ONB-004 | email_dpo | input email | **Sí** | |
| ONB-005 | rubro_id | select | No | Lista de rubros |
| ONB-006 | Botón "Comenzar con Custodio" | primary button | Submit | |

#### Casos de prueba

| ID | Caso | Prioridad | Tipo | Resultado esperado |
|----|------|-----------|------|-------------------|
| ONB-200 | Onboarding completo válido | P0 | Happy path | Empresa creada, redirige a dashboard |
| ONB-201 | Onboarding sin campos requeridos | P0 | Edge | Validación rechaza |
| ONB-202 | Onboarding con RUT inválido | P0 | Edge | Validación RUT rechaza |
| ONB-203 | Onboarding con email inválido | P0 | Edge | Validación email rejects |
| ONB-204 | Onboarding con todos los campos | P1 | Happy path | Empresa creada con todos los datos |
| ONB-205 | RUT con formato válido | P1 | Happy path | Formateo automático |
| ONB-206 | Empresas ya logueadas no ven onboarding | P1 | Edge | Redirige a dashboard |
| ONB-207 | Onboarding con RUBRO seleccionado | P1 | Happy path | Rubro asociado a empresa |

---

## Módulo 13: Solicitud de Derecho Pública — `/solicitud_derecho`

### Elementos interactivos

| ID | Elemento | Tipo | Descripción |
|----|----------|------|-------------|
| PUB-001 | StepIndicator | indicator | Pasos 1 y 2 |
| PUB-002 | Botón tipo ARCO (6 botones) | button grid | Selección de tipo |
| PUB-003 | Botón "Continuar" | primary button | Pasa a paso 2 |
| PUB-004 | Select companyId | select | **Sí** — Empresas disponibles |
| PUB-005 | input nombre_titular | text | **Sí** | |
| PUB-006 | input rut_titular | text | No | RUT validación |
| PUB-007 | input email_titular | email | **Sí** | |
| PUB-008 | textarea descripcion | textarea | No | Max 2000 chars |
| PUB-009 | Contador de caracteres | text | Muestra chars usados |
| PUB-010 | Botón "Volver" | secondary | Retrocede a paso 1 |
| PUB-011 | Botón "Enviar solicitud" | primary button (verde) | Submit |
| PUB-012 | Step 3: success state | display | Mensaje de éxito |
| PUB-013 | Botón "Hacer otra solicitud" | primary button | Resetea wizard |

#### Casos de prueba

| ID | Caso | Prioridad | Tipo | Resultado esperado |
|----|------|-----------|------|-------------------|
| PUB-400 | Solicitud completa (todos los pasos) | P0 | Happy path | Solicitud creada, email de confirmación (si SMTP) |
| PUB-401 | Solicitud sin seleccionar tipo | P0 | Edge | Botón "Continuar" deshabilitado |
| PUB-402 | Solicitud sin empresa | P0 | Edge | Validación "Seleccioná una empresa" |
| PUB-403 | Solicitud sin nombre | P0 | Edge | Validación "El nombre es obligatorio" |
| PUB-404 | Solicitud con nombre < 3 chars | P1 | Edge | Validación "Debe tener al menos 3 caracteres" |
| PUB-405 | Solicitud con RUT inválido | P1 | Edge | Validación "El RUT no es válido" |
| PUB-406 | Solicitud sin email | P0 | Edge | Validación "El email es obligatorio" |
| PUB-407 | Solicitud con email inválido | P0 | Edge | Validación "El email no es válido" |
| PUB-408 | Descripción > 2000 caracteres | P1 | Edge | Validación rechazada |
| PUB-409 | Volver del paso 2 al paso 1 | P0 | Happy path | Datos preservados |
| PUB-410 | Enviar solicitud sin descripción | P1 | Happy path | Allowed, descripción opcional |
| PUB-411 | Todos los tipos ARCO (6 botones) | P2 | Edge | Cada tipo selectable |
| PUB-412 | Success state muestra mensaje | P0 | Happy path | Step 3 visible |
| PUB-413 | "Hacer otra solicitud" resetea todo | P0 | Happy path | Vuelve al paso 1 |
| PUB-414 | Seleccionar empresa sin RATs activos | P1 | Edge | Allowed, empresa listada |
| PUB-415 | Página accesible sin login | P0 | Happy path | Público sin auth |

---

## Módulo 14: Consentimientos — `/consentimientos`

### Elementos interactivos

| ID | Elemento | Tipo | Descripción |
|----|----------|------|-------------|
| CONS-001 | Botón "+ Nuevo Consentimiento" | primary button | Abre formulario |
| CONS-002 | Lista de consentimientos | table/list | Con estado (activo/revocado) |
| CONS-003 | Botón "Revocar" | danger button | Marca fecha_revocado |

#### Casos de prueba

| ID | Caso | Prioridad | Tipo | Resultado esperado |
|----|------|-----------|------|-------------------|
| CONS-100 | Crear consentimiento | P0 | Happy path | Consentimiento creado |
| CONS-101 | Revocar consentimiento | P0 | Happy path | fecha_revocado seteada |
| CONS-102 | Ver consentimiento de otro RAT | P1 | Happy path | Filtro por rat_id funciona |
| CONS-103 | Consentimiento sin fecha_revocado = activo | P0 | Edge | Badge "Activo" |
| CONS-104 | Consentimiento con fecha_revocado = revocado | P0 | Edge | Badge "Revocado" |
| CONS-105 | IDOR: acceder a consentimiento de otra empresa | P0 | Security | 403 |

---

## Módulo 15: EIPD — `/eipd`

### Elementos interactivos

| ID | Elemento | Tipo | Descripción |
|----|----------|------|-------------|
| EIPD-001 | KPI Cards (4) | card | Total, en_proceso, completadas, pendientes |
| EIPD-002 | AlertBanner | alert | RATs que requieren EIPD |
| EIPD-003 | Tabla de EIPDs | table | RAT, resultado, fechas, acciones |
| EIPD-004 | Botón crear EIPD | primary button | Abre formulario |
| EIPD-005 | Formulario: RAT selector | select | Vinculación a RAT |
| EIPD-006 | Formulario: metodologia | textarea | |
| EIPD-007 | Formulario: objetivos | textarea | |
| EIPD-008 | Formulario: necesidad | textarea | |
| EIPD-009 | Formulario: riesgos | textarea | |
| EIPD-010 | Formulario: medidas | textarea | |
| EIPD-011 | Formulario: parecer_dpo | textarea | |
| EIPD-012 | Formulario: fecha_elaboracion | date | |
| EIPD-013 | Formulario: fecha_aprobacion | date | |
| EIPD-014 | Formulario: resultado | select | |

#### Casos de prueba

| ID | Caso | Prioridad | Tipo | Resultado esperado |
|----|------|-----------|------|-------------------|
| EIPD-100 | Crear EIPD para RAT | P0 | Happy path | EIPD creado |
| EIPD-101 | EIPD se crea automáticamente si RAT tiene evaluacion_impacto | P1 | Edge | EIPD generado |
| EIPD-102 | Actualizar estado EIPD | P0 | Happy path | Estado transiciona |
| EIPD-103 | AlertBanner muestra RATs sin EIPD | P1 | Compliance | Warning visible |
| EIPD-104 | EIPD vacío (sin EIPDs) | P1 | Happy path | Mensaje vacío |
| EIPD-105 | IDOR: acceder a EIPD de otra empresa | P0 | Security | 403 |

---

## Módulo 16: Rubros — `/rubros`

### Elementos interactivos

| ID | Elemento | Tipo | Descripción |
|----|----------|------|-------------|
| RUB-001 | Lista de rubros | list | Clickeable |
| RUB-002 | Botones up/down | icon buttons | Reordenar (superadmin) |
| RUB-003 | Sugerencias panel | panel | RAT templates por rubro |

#### Casos de prueba

| ID | Caso | Prioridad | Tipo | Resultado esperado |
|----|------|-----------|------|-------------------|
| RUB-200 | Ver lista de rubros | P1 | Happy path | Lista visible |
| RUB-201 | Click en rubro muestra sugerencias | P1 | Happy path | Panel de sugerencias aparece |
| RUB-202 | Reordenar rubro (up) | P2 | Edge | Orden actualizado |
| RUB-203 | Reordenar rubro (down) | P2 | Edge | Orden actualizado |
| RUB-204 | Superadmin ve botones up/down | P0 | RBAC | Visibles |
| RUB-205 | Admin empresa no ve botones up/down | P0 | RBAC | Ocultos |

---

## Módulo 17: Asistente IA — `/asistente-ia`

### Elementos interactivos

| ID | Elemento | Tipo | Descripción |
|----|----------|------|-------------|
| IA-001 | Chat input | text input | Pregunta sobre Ley 21.719 |
| IA-002 | Botón enviar | icon button | Envía pregunta |
| IA-003 | Historial de mensajes | list | User + assistant bubbles |

#### Casos de prueba

| ID | Caso | Prioridad | Tipo | Resultado esperado |
|----|------|-----------|------|-------------------|
| IA-300 | Enviar pregunta válida | P1 | Happy path | Respuesta del asistente |
| IA-301 | Enviar pregunta vacía | P1 | Edge | No se envía |
| IA-302 | Respuesta con contexto de Ley 21.719 | P1 | Compliance | Respuesta legalmente correcta |
| IA-303 | Loading state visible | P1 | Edge | "Escribiendo..." mostrado |
| IA-304 | Historial preservado al recargar | P1 | Edge | Mensajes persistentes |
| IA-305 | API key no configurada | P1 | Edge | Mensaje de error amigable |

---

## Módulo 18: Conexión — `/conexion`

### Elementos interactivos

| ID | Elemento | Tipo | Descripción |
|----|----------|------|-------------|
| CONN-001 | Estado de DB | status | Indicador visual |
| CONN-002 | Botón "Refrescar" | secondary button | Recarga estado |
| CONN-003 | Botón "Medir latencia" | secondary button | Mide latencia |

#### Casos de prueba

| ID | Caso | Prioridad | Tipo | Resultado esperado |
|----|------|-----------|------|-------------------|
| CONN-400 | Ver estado de conexión | P1 | Happy path | Estado visible |
| CONN-401 | Refrescar estado | P1 | Happy path | Estado actualizado |
| CONN-402 | Medir latencia | P1 | Happy path | Latencia en ms mostrada |
| CONN-403 | DB no disponible muestra error | P1 | Edge | Mensaje de error visible |
| CONN-404 | Solo superadmin ve página | P0 | RBAC | Otros roles → 403 |

---

## Módulo 19: Navegación y Layout

### Elementos interactivos

| ID | Elemento | Tipo | Descripción |
|----|----------|------|-------------|
| NAV-001 | Sidebar: Dashboard | nav item | Navega a /dashboard |
| NAV-002 | Sidebar: Procesos RAT | nav item | Navega a /rat |
| NAV-003 | Sidebar: Tickets ARCO | nav item | Navega a /tkt_solicitud_derecho |
| NAV-004 | Sidebar: Brechas | nav item | Navega a /breaches |
| NAV-005 | Sidebar: Transparencia | nav item | Navega a /transparencia |
| NAV-006 | Sidebar: Enc. Contrato | nav item | Navega a /encargados-contrato |
| NAV-007 | Sidebar: Consentimientos | nav item | Navega a /consentimientos |
| NAV-008 | Sidebar: EIPD | nav item | Navega a /eipd |
| NAV-009 | Sidebar: Reportes | nav item | Navega a /reportes |
| NAV-010 | Sidebar: Asistente IA | nav item | Navega a /asistente-ia |
| NAV-011 | Sidebar: Empresas | nav item | Navega a /companies |
| NAV-012 | Sidebar: Usuarios | nav item | Navega a /usuarios (superadmin) |
| NAV-013 | Sidebar: Rubros | nav item | Navega a /rubros |
| NAV-014 | Sidebar: Configuración | nav item | Navega a /configuracion |
| NAV-015 | Sidebar: Selector empresa | select | Cambia empresa activa |
| NAV-016 | Sidebar: "¿Qué es un RAT?" | button | Abre tooltip/popover |
| NAV-017 | Sidebar: "Cambiar contraseña" | button | Abre PasswordModal |
| NAV-018 | Sidebar: "Cerrar sesión" | button | Logout |
| NAV-019 | Topbar: Botón hamburger (mobile) | button | Abre sidebar en mobile |
| NAV-020 | Topbar: Toggle dark mode | button | Cambia tema |
| NAV-021 | Sidebar: Cierre (X) en mobile | button | Cierra sidebar |

#### Casos de prueba

| ID | Caso | Prioridad | Tipo | Resultado esperado |
|----|------|-----------|------|-------------------|
| NAV-100 | Navegar a cada página desde sidebar | P0 | Happy path | Página correcta carga |
| NAV-101 | Navegación con keyboard (Tab + Enter) | P1 | Accessibility | Navegación funcional |
| NAV-102 | Breadcrumb o título de página actualizado | P1 | UI | Título refleja página actual |
| NAV-103 | Cambiar empresa desde sidebar | P0 | Happy path | Datos de empresa nueva cargados |
| NAV-104 | "¿Qué es un RAT?" se abre y cierra | P1 | Happy path | Popover visible/cerrado |
| NAV-105 | Dark mode se activa y persiste | P1 | Happy path | Tema oscuro en toda la app |
| NAV-106 | Dark mode se desactiva | P1 | Happy path | Tema claro en toda la app |
| NAV-107 | Sidebar cerrado en desktop por defecto | P1 | Edge | Sidebar visible en desktop |
| NAV-108 | Sidebar se abre en mobile | P0 | Happy path | Overlay cubre pantalla |
| NAV-109 | Click fuera del sidebar lo cierra (mobile) | P1 | Edge | Sidebar cerrado |
| NAV-110 | Item activo del sidebar tiene color azul | P1 | UI | Estilo visual correcto |
| NAV-111 | Superadmin ve todos los items | P0 | RBAC | Todos los items visibles |
| NAV-112 | Admin empresa no ve "Usuarios" | P0 | RBAC | Item oculto |
| NAV-113 | Usuario no ve "Empresas" | P0 | RBAC | Item oculto |
| NAV-114 | 404 en ruta inexistente | P0 | Edge | Página 404 o redirect a dashboard |
| NAV-115 | Navegación rápida (click rápido en sidebar) | P1 | Edge | Sin errores de estado |

---

## Módulo 20: Hash Chain y Audit Trail

### Validación de integridad

| ID | Caso | Prioridad | Tipo | Resultado esperado |
|----|------|-----------|------|-------------------|
| AUD-001 | Crear RAT genera log con hash y prev_hash | P0 | Integrity | Log tiene hash correcto, prev_hash del anterior |
| AUD-002 | Cadena de hashes intacta | P0 | Integrity | verify_audit_chain() retorna true |
| AUD-003 | Modificar RAT rompe cadena | P0 | Integrity | Hash no coincide con esperado |
| AUD-004 | Logs de diferentes empresas aislados | P1 | Security | empresa visible en detalle del log |
| AUD-005 | Eliminar log de auditoría | P0 | Security | No se permite (soft delete o reject) |

---

## Módulo 21: Exportación

### Casos de prueba — Exportación

| ID | Caso | Prioridad | Tipo | Resultado esperado |
|----|------|-----------|------|-------------------|
| EXP-001 | Exportar CSV desde RatTable | P0 | Happy path | Archivo CSV con headers correctos |
| EXP-002 | Exportar PDF desde RatTable | P0 | Happy path | Archivo PDF con datos |
| EXP-003 | Exportar CSV desde Reportes (con filtros) | P0 | Happy path | CSV solo con resultados filtrados |
| EXP-004 | Exportar PDF desde Reportes (con filtros) | P0 | Happy path | PDF solo con resultados filtrados |
| EXP-005 | Exportar PDF individual desde drawer (Reportes) | P0 | Happy path | PDF del RAT específico |
| EXP-006 | Exportar CNI (formato APDC) | P1 | Compliance | JSON con estructura Ley 21.719 |
| EXP-007 | Exportar portabilidad JSON (ticket ARCO) | P1 | Happy path | JSON con datos del titular |
| EXP-008 | Exportar con 0 resultados | P1 | Edge | Archivo vacío con headers |
| EXP-009 | Exportar con caracteres especiales en datos | P1 | Edge | CSV/PDF maneja UTF-8 correctamente |
| EXP-010 | Nombre archivo incluye RUT (config toggle) | P1 | Edge | Toggle configurado = filename con RUT |
| EXP-011 | PDF incluye auditoría (config toggle) | P1 | Edge | Toggle configurado = historial incluido |

---

## Módulo 22: Carga y Rendimiento

| ID | Caso | Prioridad | Tipo | Resultado esperado |
|----|------|-----------|------|-------------------|
| PERF-001 | Cargar dashboard con 100 RATs | P1 | Performance | < 3 segundos |
| PERF-002 | Cargar reportes con 1000 RATs | P1 | Performance | < 5 segundos |
| PERF-003 | Búsqueda con filtro retorna 0 resultados | P1 | Edge | Sin error, mensaje claro |
| PERF-004 | Crear 10 RATs en batch rápido | P1 | Edge | Todos creados sin race conditions |
| PERF-005 | Refresh de página en medio de wizard | P1 | Edge | Draft preservado en localStorage |
| PERF-006 | Exportar PDF con 100 RATs | P1 | Performance | < 10 segundos |
| PERF-007 | Tabla con 100 filas y scroll | P1 | UI | Sin lag, scroll fluido |
| PERF-008 | Chat IA con 50 mensajes en historial | P1 | Edge | Sin degrade de performance |

---

## Resumen de cobertura

| Módulo | Casos P0 | Casos P1 | Casos P2 | Total |
|--------|----------|----------|----------|-------|
| Auth (Login, Logout, Refresh, Password) | 15 | 15 | 3 | 33 |
| Dashboard | 6 | 6 | 2 | 14 |
| RAT (Table, Wizard, Edit) | 35 | 25 | 8 | 68 |
| Empresas | 12 | 13 | 1 | 26 |
| Usuarios | 10 | 9 | 0 | 19 |
| Brechas | 10 | 10 | 2 | 22 |
| Reportes | 18 | 22 | 4 | 44 |
| Tickets ARCO | 14 | 10 | 1 | 25 |
| Configuración | 7 | 12 | 1 | 20 |
| Encargados Contrato | 7 | 5 | 1 | 13 |
| Transparencia | 4 | 2 | 1 | 7 |
| Onboarding | 5 | 4 | 1 | 10 |
| Solicitud Pública ARCO | 10 | 5 | 1 | 16 |
| Consentimientos | 5 | 1 | 0 | 6 |
| EIPD | 4 | 3 | 0 | 7 |
| Rubros | 2 | 3 | 2 | 7 |
| Asistente IA | 3 | 4 | 0 | 7 |
| Conexión | 3 | 3 | 0 | 6 |
| Navegación y Layout | 12 | 11 | 4 | 27 |
| Hash Chain / Audit | 5 | 1 | 0 | 6 |
| Exportación | 6 | 5 | 0 | 11 |
| Performance | 3 | 5 | 0 | 8 |
| **TOTAL** | **196** | **169** | **32** | **397** |

---

## Distribución de testing

### Backend — pytest (TestClient)

- Auth (login, logout, refresh, password)
- RBAC e IDOR en todos los módulos
- CRUD RAT completo
- Hash chain y audit trail
- Exportación CSV/PDF
- Brechas y notificaciones
- Tickets ARCO
- Empresas y usuarios

### Frontend — Playwright

- Todos los flujos de usuario (login → crear → editar → exportar)
- Filtros y búsquedas
- Navegación entre páginas
- Modals y drawers
- Dark mode
- Responsive (mobile)

### Compliance — Validación manual

- Verificar que todos los Artículos de Ley 21.719 están representados
- Revisar que la política de transparencia sea completa
- Validar plazos de brechas (72h APDC)
- Validar workflow de tickets ARCO

---

## Checklist final de testing

- [ ] Todos los botones tienen handler
- [ ] Todos los formularios validan inputs requeridos
- [ ] Todos los filtros devuelven resultados correctos
- [ ] RBAC: cada rol ve lo que debe y no ve lo que no debe
- [ ] IDOR: no se puede acceder a recursos de otras empresas
- [ ] Token blacklist funciona post-logout
- [ ] Hash chain intacto después de operaciones
- [ ] Exportación genera archivos válidos
- [ ] Dark mode funciona en todas las páginas
- [ ] Mobile responsive sin scroll horizontal
- [ ] Loading states visibles durante operaciones async
- [ ] Error states claros para el usuario
- [ ] Toast notifications para operaciones exitosas y errores