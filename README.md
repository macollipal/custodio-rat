# Custodio — RAT Manager · Ley 21.719

Sistema de gestión del **Registro de Actividades de Tratamiento (RAT)**
conforme a la Ley 21.719 de Protección de Datos Personales de Chile.

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
│   │   │                 /rubros, /encargados-contrato, /politica-transparencia,
│   │   │                 /tkt-solicitud-derecho, /consentimientos, /eipd,
│   │   │                 /solicitudes-derecho, /admin/tasks
│   │   └── services/     Lógica: rat, company, export, suggestions, user, breach, rubro,
│   │                      ticket, email (SMTP), scheduler (enqueue), task_service (cola),
│   │                      audit (transversal), policy, eipd
│   ├── tests/             95+ tests (pytest + httpx)
│   ├── data/             SQLite local para desarrollo (git ignored)
│   └── venv/             Entorno virtual Python
│
├── frontend-next/        Next.js 16.2 + React 19 + TypeScript + Tailwind CSS v4
│   ├── app/
│   │   ├── login/        Pantalla de autenticación
│   │   ├── onboarding/   Configuración inicial (primera empresa)
│   │   ├── solicitud_derecho/  Formulario público ARCO
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
│   │   │   ├── transparencia/   Política de transparencia Art. 14 ter
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
└── data/                 Base de datos SQLite local (fuera del repo)
```

---

## Despliegue

| Entorno | URL | Base de datos |
|---------|-----|---------------|
| **Backend API** | https://custodio-api-prod.vercel.app | Neon PostgreSQL |
| **Frontend Prod** | https://custodio-rat.vercel.app | — |
| **QA (Frontend + API)** | https://custodio-qa.vercel.app | Neon QA |
| **Local** | http://localhost:3000 (frontend) / :8002 (backend) | SQLite local |

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

# Migrar datos SQLite → Neon (production)
python migrate_to_neon.py export    # Exporta SQLite a JSON
python migrate_to_neon.py init       # Crea schema en Neon
python migrate_to_neon.py import     # Importa datos a Neon
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
| `DATABASE_URL` | Connection string | `sqlite:///data/database.db` | `postgresql://...neon.tech` |
| `ALLOWED_ORIGINS` | CORS lista blanca (URLs separadas por coma) | `http://localhost:3000` | **Requerida en todos los ambientes** |
| `SECRET_KEY` | JWT secret (256-bit) |默认值 | **Requerida** |
| `MINIMAX_API_KEY` | IA chat | — | Opcional |
| `OPENAI_API_KEY` | IA chat | — | Opcional |
| `SMTP_HOST` | Servidor SMTP (ej. smtp.sendgrid.net) | — | Opcional |
| `SMTP_PORT` | Puerto SMTP (587 o465) | — | Opcional |
| `SMTP_USERNAME` | Usuario SMTP | — | Opcional |
| `SMTP_PASSWORD` | Password/API key SMTP | — | Opcional |
| `SMTP_FROM_EMAIL` | Email remitente | — | Opcional |
| `SMTP_FROM_NAME` | Nombre remitente | — | Opcional |

> **Nota:** Si `SMTP_HOST` no está configurado, el servicio de email opera en modo DRY_RUN (loguea sin enviar). Si `ALLOWED_ORIGINS` no está configurada, la app **no levanta** (fail loud).

### Frontend (.env.local)

| Variable | Descripción |
|----------|-------------|
| `NEXT_PUBLIC_API_BASE` | URL del backend FastAPI (local: `http://localhost:8002`, prod: URL de Vercel del backend) |

---

## Stack tecnológico

**Backend:**
- FastAPI 0.115 + Uvicorn
- SQLAlchemy 2.0 + PostgreSQL (Neon) / SQLite (local)
- Pydantic 2.10
- JWT + Bcrypt
- ReportLab (exportación PDF)
- Zod (validación)

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

### Cola de Tareas Asíncronas — NUEVO
- Modelo `task_queue` persistente en BD
- Tipos: `revisar_rats_vencidos`, `notificar_brecha_dpo`, `notificar_respuesta_arco`, `cleanup_tokens`
- Scheduler actualizado a **modo enqueue** (compatible con Vercel serverless)
- Endpoint `POST /admin/tasks/run` para que un cron externo procese la cola
- Dashboard de admin: `/admin/tasks/stats` y `/admin/tasks/` para listar
- Reintentos automáticos con backoff (max 3 intentos)
- Las notificaciones de brechas ahora son asíncronas (no bloquean la request)

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
  - Requiere `MINIMAX_API_KEY` o `OPENAI_API_KEY` en `backend/.env`

### Módulo de Brechas de Seguridad (Art. 14 bis Ley 21.719)
- Gestión de brechas con plazos legales obligatorios
- Plazo APDC (72h) vencido + cálculo de horas desde detección
- Notificación automática al DPO por email (si SMTP configurado)

### Módulo Encargados de Tratamiento (Art. 14 quater Ley 21.719)
- CRUD de contratos de encargado (`/encargados-contrato`)
- Vinculación de contratos a RATs específicos
- Alertas de vencimiento de contratos

### Módulo de Transparencia (Art. 14 ter Ley 21.719)
- Política de transparencia pública generada dinámicamente desde los RATs
- Versionado con hash SHA-256
- Disponible en `/transparencia` para cada empresa

### Módulo ARCO — Solicitudes de Derecho (Art. 14 y 16 bis Ley 21.719)
- **Formulario público** (`/solicitud_derecho`): permite a cualquier persona ejercer sus derechos ARCO
  - Tipos: Acceso, Rectificación, Cancelación, Oposición, Bloqueo temporal, Portabilidad
  - Validación de RUT chileno, email, límite de 2000 caracteres en descripción
  - Creación de ticket → registra `solicitud_fecha`
- **Gestión tickets** (`/tkt_solicitud_derecho`): gestión completa de solicitudes ARCO
  - Tabla con paginación
  - Historial de cambios de estado
  - Notas internas y adjuntos
  - Respuesta al titular + notificación por email automática (si SMTP configurado)

### Exportación
- CSV por empresa
- PDF por empresa
- PDF individual de RAT (`/rats/{id}/export/pdf`)
- Formato CNI para presentación a la APDC (Ley 21.719)

### Tema oscuro
- Switch en Topbar (🌙/☀️)
- Estado persistente en `localStorage[custodio_dark_mode]`
- Clase `.dark` aplicada al `<html>`

---

## Próximas funcionalidades

### Rubros + Sugerencias de RAT por Rubro (V1-04)
- Tabla `rubros`: id, nombre, orden (BD, ordenable por superadmin)
- Tabla `rats_sugeridos`: id, rubro_id, campos pre-llenados de RAT
- 13 rubros adicionales con plantillas pre-seedeadas
- Wizard de RAT con Paso 0: muestra tarjetas de sugerencias según el rubro de la empresa
- "Usar sugerencia" → wizard pre-llenado; "Crear personalizado" → wizard en blanco
- Permisos: superadmin CRUD todos, admin_empresa CRUD solo de su rubro
- Página de gestión de rubros (drag-to-reorder) y sugerencias

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
