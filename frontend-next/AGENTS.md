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
│   │   ├── dashboard/page.tsx
│   │   ├── rat/page.tsx
│   │   ├── companies/page.tsx
│   │   ├── breaches/page.tsx
│   │   └── reportes/page.tsx  # Reportes avanzados + chat IA
│   ├── login/page.tsx
│   ├── onboarding/page.tsx    # Primera empresa (onboarding)
│   ├── layout.tsx
│   └── page.tsx               # Redirige a /login o /(app)/dashboard
│
├── components/
│   ├── dashboard/             # KPICard, StatusChart, AlertBanner
│   ├── layout/                # Sidebar, Topbar, PasswordModal
│   ├── rat/                   # RatTable, RatWizard, RatEditForm
│   └── ui/                    # Badge, CompletitudBar, Skeleton, Drawer, StepIndicator, validation
│
├── context/
│   └── AppContext.tsx          # Estado global: auth, empresa activa, rats, stats
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

### Validadores — components/ui/validation.ts
- `validarRUT(rut)` → `{ valido, mensaje }` — algoritmo dígito verificador chileno
- `formatearRUT(rut)` → string formateado con puntos y guión

### Skeletons — components/ui/Skeleton.tsx
`SkeletonCard`, `SkeletonTable`, `SkeletonTableRow`, `SkeletonKPIGrid`, `SkeletonList`

### Drawer — components/ui/Drawer.tsx
Panel lateral centrado con `60vw`, fondo oscuro, bordes redondeados, animación `scaleIn`.
Props: `open`, `onClose`, `title`, `children`, `width`, `extraAction`.
El `title=""` elimina el título del Drawer wrapper para evitar duplicación con el gradiente header interno.

---

## Campos del RAT y completitud

### Fórmula de completitud (backend)
**10 campos** divididos en:
- **Obligatorios (7)**: `nombre_proceso`, `categoria_datos`, `categoria_titulares`, `finalidad`, `base_legal`, `fuente_datos`, `plazo_retencion`
- **Recomendados (3)**: `medidas_seguridad`, `destinatarios`, `transferencia_datos`

`completitud = round((completados / 10) * 100)`

### Campos que el drawer muestra (todos los del backend)
| Campo | Sección en drawer |
|-------|-------------------|
| `nombre_proceso` | Encabezado (no como Field) |
| `categoria_titulares` | Identificación |
| `fuente_datos` | Identificación |
| `destinatarios` | Identificación |
| `nombre_encargado` | Identificación |
| `base_legal` | Base legal y finalidad |
| `finalidad` | Base legal y finalidad |
| `test_interes_legitimo` | Base legal y finalidad (recuadro amarillo si existe) |
| `categoria_datos` | Datos tratados |
| `tipo_dato_sensible` | Datos tratados |
| `transferencia_datos` | Almacenamiento y transferencias |
| `plazo_retencion` | Almacenamiento y transferencias |
| `medidas_seguridad` | Almacenamiento y transferencias |
| `pais_destino` | Almacenamiento y transferencias |
| `garantias_transferencia_int` | Almacenamiento y transferencias |
| `observaciones_auditoria` | Información del registro |
| `created_by` | Información del registro |
| `created_at` | Información del registro |
| `updated_at` | Información del registro |

### Campos booleanos que se muestran como badges
- `datos_sensibles` → badge amarillo "⚠️ Datos sensibles"
- `evaluacion_impacto` → badge azul "📋 EIPD requerida"
- `transferencia_internacional` → badge púrpura "🌐 Transfer. internacional"
- `decisiones_automatizadas` → badge gris "🤖 Decisiones automatizadas"
- `nivel_riesgo === 'Crítico'` → badge rojo "⚠️ Crítico"

---

## Rutas y navegación

La navegación se maneja con `router.push('/ruta')` desde Next.js. Sidebar tiene botones que llaman `onNavigate(page)` donde `page` es `'dashboard' | 'rat' | 'companies' | 'breaches' | 'reportes'`.

---

## Notas importantes

- No usar `window.localStorage` directamente; usar las funciones del AppContext
- Para crear componentes, seguir el patrón de componentes existentes: estilo inline con `style={{}}` y clases Tailwind
- Los colores principales: azul `#2563EB`, verde `#059669`, rojo `#DC2626`, amarillo `#D97706`, púrpura `#7C3AED`
- Siempre usar `toast` de `sonner` para feedback de usuario
- Los formularios guardan en localStorage la empresa activa, token y usuario
- Fuente base: `18px` en globals.css
- Login centrado con `pt-16`
- Drawer centrado: `60vw`, bordes redondeados, animación `scaleIn`

---

## Ley 21.719 — Conceptos clave

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