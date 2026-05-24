# Custodio — RAT Manager · Ley 21.719

Sistema de gestión del **Registro de Actividades de Tratamiento (RAT)** 
conforme a la Ley 21.719 de Protección de Datos Personales de Chile.

---

## Arquitectura

```
RAT_opencode/
├── backend/              FastAPI + SQLAlchemy + PostgreSQL (Neon) + JWT + Bcrypt
│   ├── api/              Vercel Serverless handler (@vercel/python)
│   ├── app/
│   │   ├── core/         Configuración y seguridad JWT
│   │   ├── database/     Engine y sesión SQLAlchemy
│   │   ├── models/       Tablas: User, Company, RAT, AuditLog, SecurityBreach, EIPD, Consentimiento
│   │   ├── schemas/      Validación Pydantic
│   │   ├── routes/       Endpoints: /auth, /companies, /rats, /brechas, /ai, /rubros, /rats-sugeridos
│   │   └── services/     Lógica: rat, company, export, suggestions, user, breach, rubro, rats_sugerido
│   ├── tests/             95+ tests (pytest + httpx)
│   ├── data/             SQLite local para desarrollo (git ignored)
│   └── venv/             Entorno virtual Python
│
├── frontend-next/        Next.js 16.2 + React 19 + TypeScript + Tailwind CSS v4
│   ├── app/
│   │   ├── login/        Pantalla de autenticación
│   │   ├── onboarding/   Configuración inicial (primera empresa)
│   │   ├── (app)/
│   │   │   ├── dashboard/   KPIs, gráfico, alertas de cumplimiento
│   │   │   ├── rat/         CRUD procesos RAT + wizard 4 pasos + exportación
│   │   │   ├── companies/   Gestión de empresas y usuarios por empresa
│   │   │   ├── breaches/    Gestión de brechas de seguridad
│   │   │   ├── reportes/    Reportes avanzados + drawer RAT + chat IA
│   │   │   ├── usuarios/     Gestión de usuarios (superadmin)
│   │   │   ├── conexion/     Diagnóstico de conexión
│   │   │   └── rubros/       Gestión de rubros y sugerencias
│   │   └── layout.tsx    Layout raíz + Toaster
│   ├── components/
│   │   ├── layout/       Sidebar + Topbar (responsive con hamburger) + PasswordModal
│   │   ├── dashboard/    KPICard, StatusChart, AlertBanner
│   │   ├── rat/          RatTable, RatWizard, RatEditForm
│   │   └── ui/           Badge, CompletitudBar, Skeleton, Drawer, StepIndicator, validation
│   ├── context/          AppContext (auth + empresa activa)
│   ├── lib/api.ts        Cliente HTTP a FastAPI
│   └── types/index.ts    Tipos TypeScript
│
├── docs/                 Documentación (casos de uso, flujos, manual de usuario)
└── data/                 Base de datos SQLite local (fuera del repo)
```

---

## Despliegue

| Entorno | URL | Base de datos |
|---------|-----|---------------|
| **Producción** | https://custodio-rat.vercel.app (backend) | Neon PostgreSQL |
| **Frontend** | https://custodio-rat-iy24.vercel.app | — |
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

# Frontend
cd ..\frontend-next
npm install
```

### Scripts de inicio rápido

```batch
# Desde la raíz del proyecto
iniciar.bat    # Levanta backend (8002) + frontend (3000) y abre navegador
detener.bat    # Detiene ambos servicios
```

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
python -c "from app.core.config import settings; print(settings.resolved_database_url[:50])"

# Migrar datos SQLite → Neon (production)
python migrate_to_neon.py export    # Exporta SQLite a JSON
python migrate_to_neon.py init       # Crea schema en Neon
python migrate_to_neon.py import     # Importa datos a Neon
```

---

## Frontend — comandos útiles

```bash
cd frontend-next

# Modo desarrollo
npm run dev

# Build de producción
npm run build

# Iniciar build
npm start

# Linting
npm run lint
```

---

## Variables de entorno

### Backend (.env)

| Variable | Descripción | development | production |
|----------|-------------|--------------|-------------|
| `DATABASE_URL` | Connection string | `sqlite:///data/database.db` | `postgresql://...neon.tech` |
| `ENVIRONMENT` | `development` \| `production` | `development` | `production` |
| `SECRET_KEY` | JWT secret (256-bit) |默认值 | **Requerida** |
| `ALLOWED_ORIGINS` | CORS origins | localhost:3000, :8002 | `*` (auto en prod) |
| `MINIMAX_API_KEY` | IA chat | — | Opcional |
| `OPENAI_API_KEY` | IA chat | — | Opcional |

### Frontend (.env.local)

| Variable | Descripción |
|----------|-------------|
| `NEXT_PUBLIC_API_BASE` | URL del backend FastAPI (local: `http://localhost:8002`, prod: `https://custodio-rat.vercel.app`) |

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
- Login JWT con roles (superadmin / admin_empresa / usuario)
- Onboarding automático: si no hay empresas, redirige a pantalla de configuración inicial
- Validación de sesión: si el token expira, redirige automáticamente al login
- Gestión multi-empresa con usuarios por empresa (`user_companies`)
- Topbar con nombre de usuario en negrita + badge de rol con colores diferenciados

### Gestión RAT
- CRUD completo de procesos RAT con wizard de 4 pasos
- RatEditForm: edición pre-llenada con los 4 pasos del wizard
- Duplicar procesos RAT
- Indicadores de riesgo (datos sensibles, EIPD, transferencias internacionales)
- Dashboard con KPIs y alertas de cumplimiento (Ley 21.719)
- Alertas de expiración: rats por vencer (90 días antes del plazo) y rats vencidos
- Filtros avanzados en tabla RAT: por estado, riesgo, datos sensibles, EIPD

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
- Notificación a APDC y a los afectados

### Exportación
- CSV por empresa
- PDF por empresa
- PDF individual de RAT (`/rats/{id}/export/pdf`)
- Formato CNI para presentación a la APDC (Ley 21.719)

---

## Próximas funcionalidades

### Rubros + Sugerencias de RAT por Rubro (en desarrollo)
- Tabla `rubros`: id, nombre, orden (BD, ordenable por superadmin)
- Tabla `rats_sugeridos`: id, rubro_id, campos pre-llenados de RAT
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

---

## Validación de RUT chileno

El sistema incluye validación de RUT chileno con algoritmo dígito verificador en `components/ui/validation.ts`:
- `validarRUT(rut)` → `{ valido, mensaje }`
- `formatearRUT(rut)` → string formateado con puntos y guión