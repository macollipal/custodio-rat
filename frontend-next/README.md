# Custodio Frontend — RAT Manager

## Descripción

Frontend de **Custodio RAT Manager**, sistema de gestión del Registro de Actividades de Tratamiento (RAT) conforme a la Ley 21.719 de Chile.

Stack: Next.js 16 (App Router) + React 19 + TypeScript + Tailwind CSS v4 + Sonner + jsPDF + jspdf-autotable.

## Inicio rápido

```bash
npm install
npm run dev
```

Abrir [http://localhost:3000](http://localhost:3000).

## Scripts disponibles

| Script | Descripción |
|--------|-------------|
| `npm run dev` | Modo desarrollo |
| `npm run build` | Build de producción |
| `npm start` | Iniciar build de producción |
| `npm run lint` | Linting con ESLint |

## Variables de entorno

| Variable | Descripción | Valor por defecto |
|----------|-------------|------------------|
| `NEXT_PUBLIC_API_BASE` | URL del backend FastAPI | `http://localhost:8002` |

## Estructura de carpetas

```
frontend-next/
├── app/
│   ├── (app)/              # Rutas autenticadas
│   ├── login/              # Login
│   ├── onboarding/         # Onboarding primera empresa
│   └── layout.tsx          # Layout raíz + Toaster
├── components/
│   ├── dashboard/          # KPICard, StatusChart, AlertBanner
│   ├── layout/             # Sidebar, Topbar, PasswordModal
│   ├── rat/                 # RatTable, RatWizard, RatEditForm
│   └── ui/                  # Badge, CompletitudBar, Skeleton, Drawer, validation
├── context/
│   └── AppContext.tsx      # Estado global
├── lib/
│   ├── api.ts               # Cliente HTTP al backend
│   └── constants.ts         # Constantes compartidas
└── types/
    └── index.ts             # Interfaces TypeScript
```

## Convenciones

- **Estado global**: usar `useApp()` desde `context/AppContext.tsx`
- **Toasts**: `import { toast } from 'sonner'`
- **Colores**: azul `#2563EB`, verde `#059669`, rojo `#DC2626`, amarillo `#D97706`
- **LocalStorage**: usar las funciones del AppContext, no `window.localStorage` directo

## Backend

El backend corre en FastAPI (puerto 8002). Ver `backend/` para más detalles.

Usuario por defecto: `admin` / `admin1234`