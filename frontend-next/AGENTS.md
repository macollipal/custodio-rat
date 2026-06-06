# Custodio — Frontend Agents

## Contexto del proyecto

**Custodio RAT Manager** — Gestión del Registro de Actividades de Tratamiento (RAT) conforme a la Ley 21.719 de Chile (protección de datos personales).

Stack: Next.js 16 (App Router) + React 19 + TypeScript + Tailwind CSS v4 + Sonner (notificaciones) + jsPDF + jspdf-autotable.

---

## Sistema de roles (3 niveles)

| Rol | Alcance |
|-----|---------|
| `superadmin` | Todo el sistema |
| `admin_empresa` | Su empresa + usuarios de su empresa |
| `usuario` | Su empresa + RATs (solo lectura) |

- `admin_empresa` y `usuario` → empresa obligatoria al crearse
- Cada usuario tiene relación en `user_companies` que define su empresa asignada
- `rol_global` en BD es la fuente de verdad para el rol

---

## Estructura de carpetas

```
frontend-next/
├── app/
│   ├── (app)/                 # Rutas autenticadas
│   │   ├── dashboard/page.tsx        # Dashboard + OnboardingChecklist
│   │   ├── rat/page.tsx             # RATs (wizard + tabla)
│   │   ├── companies/page.tsx        # Empresas + accesos
│   │   ├── breaches/page.tsx         # Brechas de seguridad
│   │   ├── reportes/page.tsx         # Reportes avanzados + chat IA
│   │   ├── usuarios/page.tsx         # Gestión de usuarios (superadmin)
│   │   ├── conexion/page.tsx         # Diagnóstico de conexión
│   │   ├── rubros/page.tsx           # Gestión de rubros y sugerencias
│   │   ├── encargados-contrato/page.tsx  # CRUD contratos Art. 14 quater
│   │   ├── transparencia/page.tsx     # Política de transparencia Art. 14 ter
│   │   ├── tkt_solicitud_derecho/page.tsx  # Gestión tickets ARCO
│   │   └── configuracion/page.tsx    # Configuración de cuenta
│   ├── login/page.tsx
│   ├── solicitud_derecho/page.tsx   # Formulario público ARCO
│   ├── onboarding/page.tsx          # Primera empresa (onboarding)
│   ├── layout.tsx
│   └── page.tsx                      # Redirige a /login o /(app)/dashboard
│
├── components/
│   ├── dashboard/             # KPICard, StatusChart, AlertBanner, OnboardingChecklist
│   ├── layout/                # Sidebar, Topbar, PasswordModal
│   ├── rat/                   # RatTable, RatWizard, RatEditForm
│   └── ui/                    # Badge, CompletitudBar, Skeleton, Drawer, StepIndicator, validation
│
├── context/
│   └── AppContext.tsx # Estado global: auth, empresa activa, rats, stats
│
├── lib/
│   ├── api.ts                 # Cliente HTTP — todos los llamados al backend
│   └── constants.ts           # Constantes compartidas: API_BASE, BASES_LEGALES, etc.
│
└── types/
    └── index.ts               # Interfaces: User, Company, RAT, SecurityBreach, ReportesParams, etc.
```

---

## Convenciones de código

### Estado global — AppContext
Acceder con `useApp()` desde cualquier componente client. Funciones de caché:
- `actualizarRatEnCache(rat)` — hace merge parcial de un RAT actualizado
- `agregarRatEnCache(rat)` — agrega si no existe
- `eliminarRatDeCache(ratId)` — remueve por id
- `actualizarStatsEnCache(stats)` — reemplaza stats del dashboard

### API client — lib/api.ts
Todos los endpoints del backend (FastAPI, puerto 8002). Headers: `Bearer <token>`.
Manejo de 401: `window.location.replace()` + `return {} as T`.

### Constantes — lib/constants.ts
Single source of truth para todos los magic strings: `API_BASE`, `STORAGE_KEYS`, `DRAFT_KEY_PREFIX`, `DIAS_REVISION`, `ESTADO_MAP`, `ESTADO_OPTIONS`, `RIEGO_OPTIONS`, `EIPD_OPTIONS`, `BASES_LEGALES`, `TIPOS_DATO_SENSIBLE`.

### Página de empresas — companies/page.tsx
- `CompanyForm` — formulario de creación
- `CompanyEditForm` — edición inline
- `UserAccessPanel` — gestión de accesos por empresa
- `CreateUserModal` — crear usuario global (solo superadmin)
- `CompanyUsersModal` — tabla de usuarios de una empresa (nombre, full_name, email, rol_global)

### RatTable — operaciones disponibles
- Editar, duplicar, eliminar (con confirmación)
- Expandir para ver detalle + auditoría
- Exportar CSV/PDF por empresa

### RatWizard — wizard de creación de RAT (4 pasos)
1. Identificación (nombre, categoria_titulares, fuente, destinatarios, encargado)
2. Datos tratados (categoria_datos, datos_sensibles, EIPD, decisiones automatizadas)
3. Finalidad y ley (finalidad, base_legal, test_interes_legitimo guiado 3 pasos)
4. Almacenamiento y transferencias (plazo, medidas, transferencia internacional)

### RatEditForm — edición de RAT (4 pasos)
Mismos 4 pasos que el wizard, pero pre-llenado con los datos existentes del RAT.
Incluye: `observaciones_auditoria`, `estado` y `tiene_contrato_encargado`.

### Módulo Reportes — reportes/page.tsx
- KPI cards: total, completitud promedio, datos sensibles, EIPD, transf. internacional, dec. automatizadas
- Mini gráficos de barras: por estado, riesgo, base legal
- 14 columnas configurables (selector ☰ Columnas)
- Agrupamiento por estado / base legal / nivel de riesgo
- Paginación (20 por página, navegación numérica)
- Filtros guardados por nombre (localStorage key: `custodio_saved_filters`)
- Ordenamiento por cualquier columna (asc/desc)
- Exportación CSV y PDF (jsPDF + autotable)
- **Drawer con detalle completo del RAT**:
  - Encabezado con ID y nombre del RAT (gradiente azul)
  - Badges de estado, completitud, nivel de riesgo, flags
  - Secciones: Identificación, Base legal y finalidad, Datos tratados, Almacenamiento y transferencias, Información del registro
  - **Campos vacíos se marcan con `**` en rojo itálico** (para saber qué falta)
  - Historial de cambios (auditoría)
- **Botón Exportar PDF** en drawer → descarga PDF del RAT individual (endpoint `/rats/{id}/export/pdf`)
- Chat IA flotante (botón 🤚 esquina inferior derecha)
  - Requiere `MINIMAX_API_KEY` o `OPENAI_API_KEY` en `backend/.env`
  - System prompt sobre Ley 21.719 Chile
  - Pasa contexto de empresa + RATs activos

### OnboardingChecklist — components/dashboard/OnboardingChecklist.tsx
Checklist de primeros pasos que aparece en el dashboard para empresas nuevas:
- Empresa creada, DPO definido, Primer RAT, Contrato de encargado, Política de transparencia, Procedimiento de brechas
- Barra de progreso animada
- Botones CTA a cada sección
- Se oculta automáticamente cuando todos los items están completos

### Validadores — components/ui/validation.ts
- `validarRUT(rut)` → `{ valido, mensaje }` — algoritmo dígito verificador chileno
- `formatearRUT(rut)` → string formateado con puntos y guión

### Skeletons — components/ui/Skeleton.tsx
`SkeletonCard`, `SkeletonTable`, `SkeletonTableRow`, `SkeletonKPIGrid`, `SkeletonList`

### Drawer — components/ui/Drawer.tsx
Panel lateral centrado con `95vw` en mobile, `60vw` en desktop. Max-width 640px. Fondo oscuro con backdrop blur. Bordes redondeados, animación `scaleIn`.
Props: `open`, `onClose`, `title`, `children`, `width`, `extraAction`.
El `title=""` elimina el título del Drawer wrapper para evitar duplicación con el gradiente header interno.

### Responsive — components/layout/
**Sidebar:** overlay deslizable desde izquierda en mobile (<1024px). Hidden por default, se abre con hamburger button del Topbar. Backdrop oscuro cierra al clickear fuera.
**Topbar:** botón hamburguesa `☰` visible solo en mobile (`lg:hidden`). Pasa `onMenuClick` handler para toggle del sidebar.
**AppLayout:** maneja estado `sidebarOpen` + resize listener que cierra sidebar en desktop (≥1024px). Navegación cierra sidebar automáticamente.

---

## Rutas y navegación

La navegación se maneja con `router.push('/ruta')` desde Next.js. Sidebar tiene botones que llaman `onNavigate(page)` donde `page` es `'dashboard' | 'rat' | 'companies' | 'breaches' | 'reportes' | 'encargados-contrato' | 'transparencia' | 'tkt_solicitud_derecho'`.

---

## Notas importantes

- No usar `window.localStorage` directamente; usar las funciones del AppContext
- Para crear componentes, seguir el patrón de componentes existentes: estilo inline con `style={{}}` y clases Tailwind
- Los colores principales: azul `#2563EB`, verde `#059669`, rojo `#DC2626`, amarillo `#D97706`, púrpura `#7C3AED`
- Siempre usar `toast` de `sonner` para feedback de usuario
- Los formularios guardan en localStorage la empresa activa, token y usuario
- Fuente base: `16px` en mobile, `18px` en desktop (`lg:` media query) — globals.css
- Login centrado con `pt-8 sm:pt-16`
- Drawer: `w-[95vw] max-w-[640px] sm:w-[60vw]`
- AI Chat drawer (reportes): `width: 95vw` mobile, `maxWidth: 420px` desktop
- Tablas: `overflow-x-auto` para scroll horizontal en mobile
- **No hacer commits directos a `main` para cambios de features** — usar rama develop o feature branches
- **Dark mode:** switch en Topbar (🌙/☀️), estado en `localStorage[custodio_dark_mode]`, clase `.dark` en `<html>`

---

## Ley21.719 — Conceptos clave

**RAT (Registro de Actividades de Tratamiento)** — Art. 16
9 campos mínimos obligatorios: nombre_proceso, categoria_titulares, categoria_datos, finalidad, base_legal, fuente_datos, plazo_retencion.

**Datos sensibles** — Art. 2 letra g
7 categorías: origen racial/étnico, situación socioeconómica, salud, vida sexual, opiniones políticas, afiliación sindical, biometría.

**Art. 16 BIS** — Datos biométricos de identificación
Tratamiento específico para identificar inequívocamente. Requiere EIPD previa. En laboral, consentimiento NO es base válida.

**Base legal: Interés legítimo** — Art. 16
Requiere test de 3 pasos documentado:
1. ¿Existe interés legítimo real?
2. ¿El tratamiento es necesario para ese interés?
3. ¿Prevalece sobre los derechos del titular?

**Encargado del tratamiento** — Art. 14 quáter
Todo tercero que trata datos por cuenta del responsable debe tener contrato de encargo.

**Brechas de seguridad** — Art. 14 bis
72 horas para notificar a la APDP. Notificar a titulares sin dilación si hay datos sensibles, menores o financieros.

**EIPD** — Art. 15 bis
Evaluación de Impacto en Protección de Datos. Obligatoria cuando hay datos sensibles, perfilamiento automatizado o transferencias internacionales de alto riesgo.

---

## Estados y constantes

- Estados RAT: `borrador` | `completo` | `en_revision` | `aprobado`
- Estados EIPD: `no_requerida` | `pendiente` | `en_proceso` | `completada`
- Roles empresa: `admin` | `editor` | `viewer`
- Roles globales: `superadmin` | `admin_empresa` | `usuario`

---

## Despliegue y ambientes

### Variables de entorno (Vercel Frontend)

| Variable | Descripción | QA | Producción |
|----------|-------------|-----|------------|
| `NEXT_PUBLIC_API_BASE` | URL del backend | `https://custodio-qa.vercel.app` | `https://custodio-api-prod.vercel.app` |
| `NEXT_PUBLIC_DEPLOY_ENV` | Ambiente de despliegue | `qa` | `production` |

### Arquitectura de ambientes

```
┌─────────────────────────────────────────────────────────────┐
│  LOCAL DEV │
│  Frontend: localhost:3000  →  API: localhost:8002         │
│  .env: NEXT_PUBLIC_API_BASE=http://localhost:8002           │
└─────────────────────────────────────────────────────────────┘
  │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  QA                                                        │
│  Frontend: https://custodio-qa.vercel.app                   │
│  API: https://custodio-qa.vercel.app (mismo dominio)        │
│  Vercel: proyecto separado "custodio-qa"                  │
│  .env: NEXT_PUBLIC_API_BASE=https://custodio-qa.vercel.app  │
│         NEXT_PUBLIC_DEPLOY_ENV=qa                           │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  PRODUCTION                                                │
│  Frontend: https://custodio-rat.vercel.app                  │
│  API: https://custodio-api-prod.vercel.app                  │
│  Vercel: proyecto separado "custodio-rat"                 │
│  .env: NEXT_PUBLIC_API_BASE=https://custodio-api-prod...   │
│         NEXT_PUBLIC_DEPLOY_ENV=production                  │
└─────────────────────────────────────────────────────────────┘
```

### Reglas de CORS (Backend FastAPI)

- `ALLOWED_ORIGINS` es la **única** fuente de verdad para CORS
- Sin `ALLOWED_ORIGINS` → la app no levanta (fail loud)
- Sin wildcards, sin VERCEL_URL, sin ENVIRONMENT para CORS
- QA: `ALLOWED_ORIGINS=https://custodio-qa.vercel.app,http://localhost:3000`
- Prod: `ALLOWED_ORIGINS=https://custodio-rat.vercel.app`
