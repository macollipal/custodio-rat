# Custodio — RAT Manager · Ley 21.719

Sistema de gestión del **Registro de Actividades de Tratamiento (RAT)**
conforme a la Ley 21.719 de Protección de Datos Personales de Chile.

---

## 🔒 Seguridad y secrets

**REGLA ABSOLUTA:** Este proyecto NUNCA acepta credenciales en el código fuente o historial de git.

**📖 Fuente canónica:** `.opencode/skills/security-secret-scan/SKILL.md`

Reglas clave:
- Credenciales via variables de entorno (`.env`, Vercel Env Vars)
- `.env` en `.gitignore` (siempre)
- `.env.example` con placeholders (sin valores reales)
- Si accidentalmente commiteaste un secret: ROTAR + `git filter-repo` + force-push

Si sos un agente de IA: detectá secrets y **NEGATE** a commitear hasta corregir.

---

## Arquitectura

```
RAT_opencode/
├── api/                  Vercel Serverless handler (@vercel/python, entry point para backend)
├── backend/              FastAPI + SQLAlchemy + PostgreSQL (Neon) + JWT + Bcrypt
│   ├── app/
│   │   ├── core/         Configuración, seguridad JWT (access+refresh), logging estructurado
│   │   ├── database/     Engine y sesión SQLAlchemy
│   │   ├── middleware/   RequestIdMiddleware (X-Request-ID + contextvars)
│   │   ├── models/       Tablas: User, Company, RAT, AuditLog, SecurityBreach, EIPD,
│   │   │                 Consentimiento, Rubro, RATSugerido, TktSolicitudDerecho,
│   │   │                 TktNota, TktAdjunto, TktHistorial, EncargadoContrato,
│   │   │                 PoliticaTransparencia, TaskQueue, TokenBlacklist
│   │   ├── schemas/      Validación Pydantic
│   │   ├── routes/       Endpoints: /auth, /auth/refresh, /companies, /rats, /brechas, /ai,
│   │   │                 /rubros, /encargados-contrato, /transparencia, /publico/transparencia,
│   │   │                 /tkt-solicitud-derecho, /consentimientos, /eipd,
│   │   │                 /seguimiento, /admin/tasks, /feriados, /module-permissions
│   │   └── services/     Lógica: rat, company, export, suggestions, user, breach, rubro,
│   │                      ticket, email (SMTP), scheduler (enqueue), task_service (cola),
│   │                      audit (transversal), policy, eipd
│   ├── tests/             761+ tests (pytest + httpx)

│   └── venv/             Entorno virtual Python
│
├── frontend-next/        Next.js 16.2 + React 19 + TypeScript + Tailwind CSS v4
│   ├── app/
│   │   ├── login/        Pantalla de autenticación
│   │   ├── onboarding/   Configuración inicial (primera empresa)
│   │   ├── seguimiento/  Consulta pública de estado ARCO (titular, sin auth)
│   │   ├── (app)/
│   │   │   ├── dashboard/   KPIs, gráfico, alertas + OnboardingChecklist
│   │   │   ├── rat/         CRUD procesos RAT + wizard 4 pasos + exportación
│   │   │   ├── companies/   Gestión de empresas y usuarios por empresa
│   │   │   ├── breaches/    Gestión de brechas de seguridad
│   │   │   ├── reportes/    Reportes avanzados + drawer RAT + chat IA
│   │   │   ├── usuarios/     Gestión de usuarios (superadmin)
│   │   │   ├── conexion/     Diagnóstico de conexión
│   │   │   ├── rubros/       Gestión de rubros y sugerencias
│   │   │   ├── encargados-contrato/  CRUD contratos Art. 14 quater
│   │   │   ├── transparencia/   Política de transparencia Art. 14 ter (editor M-04)
│   │   │   ├── tkt_solicitud_derecho/  Gestión tickets ARCO
│   │   │   ├── consentimientos/   Gestión de consentimientos (Art. 12)
│   │   │   ├── eipd/            EIPD editable (Art. 15 bis)
│   │   │   └── configuracion/ Configuración de cuenta
│   │   └── layout.tsx    Layout raíz + Toaster
│   ├── components/
│   │   ├── layout/       Sidebar (4 grupos) + Topbar (responsive con hamburger) + PasswordModal
│   │   ├── dashboard/    KPICard, StatusChart, AlertBanner, OnboardingChecklist
│   │   ├── rat/          RatTable, RatWizard, RatEditForm
│   │   └── ui/           Badge, CompletitudBar, Skeleton, Drawer, StepIndicator, validation
│   ├── context/          AppContext (auth + empresa activa)
│   ├── lib/api.ts        Cliente HTTP a FastAPI (con auto-refresh en 401)
│   ├── e2e/              Tests E2E con Playwright
│   ├── playwright.config.ts
│   └── types/index.ts    Tipos TypeScript
│
├── docs/                 Documentación (casos de uso, flujos, manual de usuario, errores de deploy Vercel)

```

---

## Despliegue

| Entorno | URL | Base de datos |
|---------|-----|---------------|
| **Backend API** | https://custodio-api-prod.vercel.app | Neon PostgreSQL |
| **Frontend Prod** | https://custodio-rat.vercel.app | — |
| **QA (Frontend + API)** | https://custodio-qa.vercel.app | Neon QA |
| **Local** | http://localhost:3000 (frontend) / :8002 (backend) | Neon PostgreSQL (desarrollo) |

---

## Iniciar el sistema (desarrollo local)

### Requisitos
- Python 3.9+
- Node.js 18+
- Git

### Setup

```bash
# Clonar repositorio
git clone https://github.com/macollipal/custodio-rat.git
cd RAT_opencode

# Backend
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Frontend (usa Bun)
cd ..\frontend-next
bun install

# Pre-commit hook (detecta secretos antes de push)
pip install pre-commit
pre-commit install
```

### Scripts de inicio rápido

```batch
# Desde la raíz del proyecto
iniciar_todo.bat  # Levanta backend (8002) + frontend (3000) y abre navegador
matar_puertos.bat # Detiene ambos servicios (proceso huérfanos en puerto 3000)
```

> **Nota:** `iniciar_todo.bat` es un script local, no está en git.

### Desarrollo individual

```bash
# Backend
cd backend
venv\Scripts\activate
python -c "from app.main import app; print('Backend OK')"

# Frontend
cd frontend-next
npm run dev
```

---

## Backend — comandos útiles

```bash
cd backend

# Activar entorno virtual
venv\Scripts\activate

# Ejecutar servidor local
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload

# Ejecutar tests
pytest tests/ -v

# Verificar conexión a base
python -c "from app.core.config import settings; print(settings.DATABASE_URL[:50])"

# Migrar datos (script deprecated: migrate_to_neon.py esta deprecado jul-2026)
```

---

## Frontend — comandos útiles

> El proyecto usa **Bun** como package manager (bun.lock presente en git).

```bash
cd frontend-next

# Instalar dependencias
bun install

# Modo desarrollo
bun dev

# Build de producción
bun build

# Linting
bun lint
```

---

## Tests

### Backend (pytest)
```bash
cd backend
pytest tests/ -v
```

### Frontend E2E (Playwright)
```bash
cd frontend-next

# Instalar Playwright (solo primera vez)
npm install
npm run test:e2e:install

# Correr todos los tests E2E
npm run test:e2e

# Con interfaz headed (debug)
npm run test:e2e:headed
```

**Variables de entorno para E2E:**
| Variable | Default | Descripción |
|----------|---------|-------------|
| `E2E_USERNAME` | `admin` | Usuario de prueba |
| `E2E_PASSWORD` | `admin1234` | Contraseña |
| `E2E_BASE_URL` | `http://localhost:3000` | URL del frontend |

**Tests incluidos:**
- `01-login.spec.ts`: carga página, login exitoso, error con credenciales inválidas
- `02-sidebar.spec.ts`: 4 grupos, navegación entre páginas
- `03-consentimientos.spec.ts`: KPIs, modal de creación, filtros
- `04-eipd.spec.ts`: KPIs, alerta de pendientes

---

## Variables de entorno

### Backend (.env)

| Variable | Descripción | development | production |
|----------|-------------|--------------|-------------|
| `DATABASE_URL` | Connection string | `postgresql://...neon.tech` | `postgresql://...neon.tech` |
| `ALLOWED_ORIGINS` | CORS lista blanca (URLs separadas por coma) | `http://localhost:3000` | **Requerida en todos los ambientes** |
| `SECRET_KEY` | JWT secret (256-bit) |默认值 | **Requerida** |
| `GROQ_API_KEY` | LLM chat IA (llama-3.3-70b-versatile via Groq) | — | Opcional |
| `COHERE_API_KEY` | Embeddings para el Asesor IA (Cohere) | — | Opcional |
| `SMTP_URL` | SMTP DSN (ej. `smtplib://apikey:SG.xxx@smtp.sendgrid.net:587/?use_tls=true&from_email=admin@yopmail.com&from_name=Custodio%20RAT`) | — | Opcional |

> **Nota:** Si `SMTP_URL` no está configurado, el servicio de email opera en modo DRY_RUN (loguea sin enviar). Si `ALLOWED_ORIGINS` no está configurada, la app **no levanta** (fail loud).

### Frontend (.env.local)

| Variable | Descripción |
|----------|-------------|
| `NEXT_PUBLIC_API_BASE` | URL del backend FastAPI (local: `http://localhost:8002`, prod: URL de Vercel del backend) |

---

## Stack tecnológico

**Backend:**
- FastAPI 0.115 + Uvicorn
- SQLAlchemy 2.0 + PostgreSQL (Neon)
- Pydantic 2.10
- JWT + Bcrypt
- ReportLab (exportación PDF)
- Groq (LLM chat) + Cohere (embeddings)

**Frontend:**
- Next.js 16.2 (App Router)
- React 19 + TypeScript
- Tailwind CSS v4
- Sonner (notificaciones)
- React Hook Form + Zod
- jsPDF + jspdf-autotable (exportación)
- lucide-react (iconos)

**Infraestructura:**
- Vercel (serverless functions + hosting)
- Neon PostgreSQL (base de datos production)

---

## Sistema de roles (3 niveles)

| Rol | Alcance |
|-----|---------|
| `superadmin` | Todo el sistema |
| `admin_empresa` | Su empresa + usuarios de su empresa |
| `usuario` | Su empresa + RATs (solo lectura) |

- `admin_empresa` y `usuario` → empresa obligatoria al crearse
- `superadmin` gestiona usuarios globales y todas las empresas
- `admin_empresa` solo ve/gestiona su propia empresa y sus usuarios

---

## Campos del RAT (Art. 16 Ley 21.719)

| Campo | Obligatorio | Completitud |
|-------|:-----------:|:-----------:|
| Nombre del proceso | ✅ | Sí |
| Categoría de datos | ✅ | Sí |
| Categorías de titulares | ✅ | Sí |
| Finalidad | ✅ | Sí |
| Base legal | ✅ | Sí |
| Fuente de datos | ✅ | Sí |
| Plazo de retención | ✅ | Sí |
| Destinatarios / Encargados | — | Sí (recomendado) |
| Medidas de seguridad | — | Sí (recomendado) |
| Transferencias de datos | — | Sí (recomendado) |
| Transferencia internacional | — | Flags |
| Tipo de dato sensible | — | Sí |
| Decisiones automatizadas | — | Flags |
| EIPD requerida | — | Flags |
| Test interés legítimo | — | Sí |
| Encargado tratamiento | — | Sí |
| Tiene contrato encargado | — | Flags |
| Observaciones auditoría | — | Sí |

**Fórmula:** `(7 campos obligatorios + 3 recomendados) / 10 campos = completitud %`

---

## Funcionalidades

### Autenticación y usuarios
- **Refresh tokens JWT**: access token (8h) + refresh token (30 días) en cookies httpOnly
- **Rotación automática**: cuando el access token expira, el frontend usa el refresh token para obtener uno nuevo sin interrumpir al usuario
- **Auto-logout**: si el refresh también expira, redirige al login limpiando storage
- Login JWT con roles (superadmin / admin_empresa / usuario)
- Onboarding automático: si no hay empresas, redirige a pantalla de configuración inicial
- Gestión multi-empresa con usuarios por empresa (`user_companies`)
- Topbar con nombre de usuario en negrita + badge de rol con colores diferenciados

### Módulo Empresas

Gestión de responsables del tratamiento de datos personales.

**Endpoints:** `GET/POST /companies`, `GET/PUT/DELETE /companies/{id}`, `PATCH /companies/{id}/desactivar`, `GET /companies/{id}/usuarios/`, `GET /admin/companies/{id}/hard-delete`

**Campos destacados en `CompanyOut`:**
- `completitud_promedio` — promedio de completitud de todos los RATs de la empresa
- `rats_vencidos` — RATs cuyo plazo de retención ha expirado
- `solicitudes_pendientes` — tickets ARCO en estado abierto o en_proceso
- `solicitudes_vencidas_sla` — tickets ARCO con plazo legal vencido
- `has_politica_transparencia` — si existe política Art. 14 ter publicada
- `canal_ejercicio_derechos` — canal oficial para ejercicio de derechos (Art. 12)
- `desactivada_por` — username que desactivó la empresa

**Roles de empresa (tabla `user_companies`):** `admin` | `editor` | `viewer`
- VIEWER solo puede consultar; no puede editar ni desactivar.
- Solo superadmin puede realizar hard-delete.

**Frontend:** `/companies` — cards con badges de alertas (RATs vencidos, ARCO pendientes/SLA), botón "Ver RATs →", **Ficha de empresa** (tabs Datos/RATs/ARCO/Brechas con carga lazy), drawer de auditoría, gestión de accesos, exportación APDP.

### Módulo de Consentimientos (Art. 12 Ley 21.719) — NUEVO
- Página `/consentimientos` con tabla y KPIs (Total / Activos / Revocados)
- Filtros: por RAT, solo activos
- Modal de creación con campos: RAT, titular, email, canal (web/papel/firma_digital/verbal/otro), texto
- Modal de detalle con texto completo del consentimiento
- Endpoint `POST /consentimientos/{id}/revocar` para revocación (Art. 12)
- Audit log automático en todas las operaciones

### Módulo EIPD (Art. 15 bis Ley 21.719) — NUEVO
- Página `/eipd` con tabla y KPIs (Total / En proceso / Completadas / Pendientes)
- **Alerta de RATs pendientes**: detecta RATs con `evaluacion_impacto=true` sin EIPD registrada
- Formulario completo: metodología, objetivos, necesidad/proporcionalidad, riesgos, medidas, parecer DPO
- Workflow: en_proceso → completada (o no_requerida)
- Fechas de elaboración y aprobación
- Audit log automático en todas las operaciones

### Cola de Tareas Asíncronas
- Modelo `task_queue` persistente en BD
- Tipos: `revisar_rats_vencidos`, `notificar_brecha_dpo`, `notificar_respuesta_arco`, `cleanup_tokens`, `revisar_encargados_vencidos`, `sla_alert_t2`, `notificar_eipd_vencida`, `solicitar_renovacion_consentimiento`, `sla_alert_brecha_72h`, `sla_alert_plazo_retencion`
- Scheduler en **modo enqueue** (compatible con Vercel serverless) — 8 jobs periódicos
- Endpoint `POST /admin/tasks/run` para que un cron externo procese la cola
- Dashboard de admin: `/admin/tasks/stats` y `/admin/tasks/` para listar
- Reintentos automáticos con backoff (max 3 intentos)
- Monitor brechas 72h (C-03): cada 12h detecta brechas sin notificar APDP y alerta al DPO
- Alerta plazo retención (C-02): cada 24h notifica RATs con plazo de retención vencido

### Gestión RAT
- CRUD completo de procesos RAT con wizard de 4 pasos
- RatEditForm: edición pre-llenada con los 4 pasos del wizard
- Duplicar procesos RAT
- Indicadores de riesgo (datos sensibles, EIPD, transferencias internacionales)
- Dashboard con KPIs y alertas de cumplimiento (Ley 21.719)
- Alertas de expiración: rats por vencer (90 días antes del plazo) y rats vencidos
- Filtros avanzados en tabla RAT: por estado, riesgo, datos sensibles, EIPD
- **OnboardingChecklist**: checklist de primeros pasos con barra de progreso en el dashboard

### Reportes avanzados (reportes/page.tsx)
- KPI cards y mini gráficos de barras (por estado, riesgo, base legal)
- 14 columnas configurables (selector ☰)
- Agrupamiento por estado, base legal o nivel de riesgo
- Paginación (20 por página)
- Filtros guardados por nombre (localStorage, con `limpiarFiltros()` y `saveFilter()`)
- Ordenamiento por cualquier columna (asc/desc)
- Exportación CSV y PDF (jsPDF + autotable)
- **Drawer RAT desplegable** con:
  - Encabezado con ID `#N` y nombre del RAT (gradiente azul oscuro)
  - Badges de estado, completitud, nivel de riesgo
  - Flags (datos sensibles, EIPD, transferencia internacional, decisiones automatizadas)
  - Secciones: Identificación, Base legal, Datos tratados, Almacenamiento, Info
  - **Campos vacíos marcados con `**` en rojo** para identificar qué falta
  - Historial de cambios (auditoría)
  - **Botón Exportar PDF** → descarga PDF individual del RAT
- Chat IA flotante (botón 🤚 esquina inferior derecha)
  - Requiere `GROQ_API_KEY` en `backend/.env`

### Módulo de Brechas de Seguridad (Art. 14 bis Ley 21.719)
- Gestión de brechas con plazos legales obligatorios
- Plazo APDP (72h) vencido + cálculo de horas desde detección
- Notificación automática al DPO por email (si SMTP configurado)

### Módulo Encargados de Tratamiento (Art. 14 quater Ley 21.719)
- CRUD de contratos de encargado (`/encargados-contrato`)
- Vinculación de contratos a RATs específicos
- Alertas de vencimiento de contratos

### Módulo de Transparencia (Art. 14 ter Ley 21.719)
- Política de transparencia pública generada dinámicamente desde los RATs
- **Editor por ítem** (M-04): admin_empresa puede personalizar cada sección; override se persiste en BD
- Versionado con hash SHA-256 recalculado en cada guardado
- Disponible en `/transparencia` (autenticado, con editor) y `/publico/transparencia/{id}` (público)

### Módulo ARCO — Solicitudes de Derecho (Art. 12 y 14 Ley 21.719)
- **Gestión interna de tickets** (`/tkt_solicitud_derecho`): el staff crea y gestiona solicitudes ARCO
  - Tipos: Acceso, Rectificación, Cancelación, Oposición, Bloqueo temporal, Portabilidad
  - Validación de RUT chileno, email, límite de 2000 caracteres en descripción
  - Tabla con paginación, historial de cambios de estado, notas internas y adjuntos
  - Respuesta al titular + notificación por email automática (si SMTP configurado)
  - Plazo legal 10 días hábiles con cálculo de feriados Chile hasta 2040
  - Prórroga de plazo (+10 días hábiles, Art. 12 bis) — 1 vez por ticket
  - Causal de rechazo (enum), verificación de identidad obligatoria para resolver
  - Hash de integridad SHA-256 al resolver (Art. 12.5)
- **Formulario público ARCOP+** (`/ejercer-derechos`): formulario de 3 pasos para que el titular ejerza sus derechos sin login — validación RUT, confirmación email, stepper, glosario intro, detección de titular repetido (aviso si ya tiene ticket abierto en esa empresa)
- **Acuse de recibo automático** (ARCO-QW6): email al titular al crear su solicitud, con tracking token
- **Chips de placeholders** (ARCO-QW7): al redactar respuesta, chips insertan `{{nombre_titular}}`, `{{empresa}}`, `{{fecha}}`, etc.
- **Banner SLA con tiempos reales** (ARCO-QW8): FlujoModal muestra días hábiles consumidos y días restantes con semáforo de color
- **Consulta pública** (`/seguimiento/{tracking_token}`): titular consulta estado sin autenticación
- **Monitor SLA** (C-03): job cada 12h alerta DPO por brechas sin notificar APDP >72h
- Tabla canónica: `tkt_solicitud_derecho` (tabla legacy `solicitudes_derecho` eliminada jul-2026)

### Exportación
- CSV por empresa
- PDF por empresa
- PDF individual de RAT (`/rats/{id}/export/pdf`)
- Formato CNI para presentación a la APDP (Ley 21.719)

### Tema oscuro
- Switch en Topbar (🌙/☀️)
- Estado persistente en `localStorage[custodio_dark_mode]`
- Clase `.dark` aplicada al `<html>`

---

---

## Modelos (2026)

| Modelo | Tabla | Descripción |
|--------|-------|-------------|
| EIPD | `eipds` | Documento formal de Evaluación de Impacto en Protección de Datos (Art. 15 bis) — linked 1:1 a cada RAT |
| Consentimiento | `consentimientos` | Registro de consentimientos obtenidos: canal, texto, fecha, revocación (Art. 12) |
| Rubro | `rubros` | Rubros de empresa ordenados por prioridad (ej: Salud, Retail, Educación) |
| RAT Sugerido | `rats_sugeridos` | Plantillas de RAT pre-llenadas por rubro |
| EncargadoContrato | `encargados_contrato` | Contratos de encargado (Art. 14 quater) |
| TktSolicitudDerecho | `tkt_solicitud_derecho` | Tickets de solicitudes ARCO |

---

## Validación de RUT chileno

El sistema incluye validación de RUT chileno con algoritmo dígito verificador en `components/ui/validation.ts`:
- `validarRUT(rut)` → `{ valido, mensaje }`
- `formatearRUT(rut)` → string formateado con puntos y guión
