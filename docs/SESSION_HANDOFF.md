# Session Handoff - Custodio RAT

> ## 📅 **ÚLTIMO DOCUMENTO DE HANDOFF: 2026-08-07**
> ## ⏰ **Versión vigente del documento** — Si tu copia es más vieja, este es el último update.
> ## 🔖 **Identificador único**: `SESSION_HANDOFF_2026-08-07`

**Branch:** `qa` (up-to-date con origin/qa)
**Autor:** Emece <marcelocollipal@gmail.com>
**Cuenta Vercel vinculada:** marcelocollipal-7370
**Administrador IA del proyecto:** Claude Code (claude-sonnet-4-6)

> **Para retomar:** abrir Claude Code en la raíz y decir "Lee docs/SESSION_HANDOFF.md y continuemos desde donde quedamos".

---

## Nota de transición (2026-08-07)

A partir de esta sesión, el proyecto es administrado con **Claude Code** (claude-sonnet-4-6). Las referencias anteriores a "Minimax" o "MiniMax" en comentarios de código eran legado histórico y ya fueron limpiadas — el stack IA del Asesor usa **Groq** (LLM: llama-3.3-70b-versatile) + **Cohere** (embeddings: embed-multilingual-v3.0), sin cambios planificados al stack técnico.

**Mejoras UX aplicadas en esta sesión (sprint 2026-08-07):**
- Fix XSS en `AlertBanner` — `dangerouslySetInnerHTML` eliminado, prop cambió a `ReactNode`
- Reemplazo de `window.confirm()` con `<ConfirmDialog />` en 5 archivos
- Sidebar: `<select>` nativo con colores hardcodeados → `<Select />` del design system
- `RatWizard`: eliminado `forceUpdate({})` en interval; reemplazado por estado `savedLabel`
- Limpieza completa de referencias legacy Minimax (`asesor_service.py`, `ai.py`, `config.py`, tests, `.env.example`, `CLAUDE.md`)

---

## 1. Estado actual del proyecto

### Score y versión
- **Versión**: v1.9 (mantenida — sin cambios en la rama docs/documentacion_oficial/)
- **Score arquitectónico (STATUS.md)**: 7.7/10 — RAT: 9.0/10
- **Madurez**: Producción Inicial → candidato a Producción Empresarial
- **Última auditoría formal**: `docs/auditorias/2026-07-07_auditoria_rat_detalle/`

### Working tree
Limpio — todos los cambios commiteados y pusheados.

### Últimos 10 commits (rama `qa`)

```
901aaf3  feat(tkt+frontend): QW4 dashboard por_tipo + axe-core a11y + e2e fixes
380b7f3  feat(frontend): homologacion UX - migracion pages restantes a <Button>
8905219  feat(frontend): homologacion UX completa - migracion a <Button> en wizard, forms y CTAs
7026d56  feat(frontend): homologacion UX + touch targets + componentes atomos
fe127b5  refactor(rat): H3.12 export DRY + Z-03 MIME validation + ignore uploads
848903e  refactor(rat): H3.5 — BASES_LEGALES deduplicated + 4 test fixes + H2 cleanup
54f4765  refactor(rat): migrate all calls to pure calculation service (H3.1)
633cb05  refactor(rat): H3.1 — extraer calcular_completitud/nivel_riesgo a servicio puro
8f5b482  fix(rat): dashboard stats — call RAT.calcular_completitud() on instance, not as column
46ce065  fix(e2e): test.fail requires boolean, not Error
```

---

## 2. Trabajo realizado en esta sesión (2026-07-08 a 2026-07-13)

### 2.1 Auditoría + fixes de bugs pre-existentes
- 4 tests rotos arreglados (tipo_dato_sensible, garantias_transferencia_int, campos Tier2 + archivo)
- Bug: validador checkeaba `archivo_base_legal_datos` post-upload en vez de `archivo_base_legal_base64` input
- Bug: `calcular_completitud` no consideraba `archivo_base_legal_storage_url` (OCI)
- Bug: `_strip_unset_required_fields` ponía `""` en campos `min_length>1`
- `.gitignore`: agregado `backend/uploads/` (PDFs de test)

### 2.2 H3.5 — BASES_LEGALES deduplication (commit `848903e`)
- Backend: `BASE_LEGAL_OPTIONS` (8 opciones), `BaseLegalOptionsOut`, endpoint `GET /rats/base-legal-opciones`
- Frontend: `AppContext` cachea opciones + descripciones; 5 componentes migrados (Step3, Step1, RatWizard, RatEditForm, reportes/page)

### 2.3 H3.12 — DRY check_company_access (commit `fe127b5`)
- 4 endpoints de export (`/export/csv`, `/export/pdf`, `/{rat_id}/export/pdf`, `/export/cni`) ahora usan helper compartido
- ~20 líneas de código duplicado eliminadas
- Z-03: Magic bytes validation conectado a `procesar_archivo_base_legal`
- Z-01, Z-06 ya estaban implementados previamente (6/6 y 7/7 tests pasan)

### 2.4 Homologación UX completa (commits `7026d56`, `8905219`, `380b7f3`)

**Componentes átomo nuevos** en `frontend-next/components/ui/`:
- `Button.tsx` — 6 variants (primary/secondary/danger/success/warning/ghost) × 3 sizes (sm/md/lg) + loading + fullWidth
- `Input.tsx`, `Select.tsx`, `Textarea.tsx` — con label, hint, error, a11y (`aria-describedby`, `aria-invalid`)
- `Card.tsx` + `CardHeader.tsx` (3 variants × 4 paddings)
- `Badge.tsx` — extendida (mantiene API legacy `estado={rat.estado}` + nuevo `variant`)
- `Alert.tsx` — 4 variants
- `index.ts` — barrel exports

**Migración masiva a `<Button>`** — 25+ archivos:

| Categoría | Archivos |
|---|---|
| Pages (app) | dashboard, breaches, reportes, rat, companies, configuracion, usuarios, tkt_solicitud_derecho, eipd, encargados-contrato, consentimientos, conexion |
| Componentes | RatWizard + WizardModular (Step0-5), RatEditForm, RatDetailView, RatTable, PdfPreview, TicketDrawer, CreateTicketForm |

**Fixes WCAG**:
- Touch targets WCAG ≥44px (botones con `min-h-[44px]` por defecto)
- Eliminados `onMouseEnter/onMouseLeave` hover-only JS (mobile funcional ahora)
- Loading states semánticos con `<Button loading>`

### 2.5 QW4 ARCO — Dashboard derechos más ejercidos (commit `901aaf3`)
- Backend: `ticket_service.get_dashboard_stats` agrega GROUP BY por tipo
- Schema: `TktDashboardResponse.por_tipo: dict`
- Tests: `tests/test_qw4_por_tipo.py` — 2/2 pasan contra Neon QA
- Frontend: nueva sección "Derechos más ejercidos (Art. 12)" con grid responsive

### 2.6 Auditoría a11y axe-core (commit `901aaf3`)
- `@axe-core/playwright` instalado
- Nuevo `e2e/19-axe-a11y.spec.ts` — 3 tests
- Login page: **0 violaciones críticas/serias** (2 moderadas pre-existentes)
- Fix: `<div>` → `<main>` en `app/login/page.tsx` (resuelve `landmark-one-main`)

### 2.7 Verificación e2e post-migración
- `18-design-system.spec.ts`: **8/8 pasan** (incluye validación de homologación UX completa)
- Migración a `<Button>` NO rompió selectores
- Tests que requieren auth (`admin`/`Admin1234!`) fallan — **no son regresiones**, son credenciales inexistentes en QA

---

## 3. Pendientes organizados por prioridad

### 3.1 P0 — Críticos (siguiente sesión, idealmente)

#### QWs del backlog canónico (docs/backlog_seguimiento.md)
De los 40 QWs identificados, **14 cerrados, 26 pendientes**. QWs fáciles / alto valor:

| ID | Descripción | Esfuerzo | Impacto |
|---|---|---|---|
| QW1 Empresas | Vista de auditoría per-empresa | 2-3d | ALTO |
| QW2 Empresas | Botón Exportar Reporte APDP (PDF) | 3-4d | CRÍTICO |
| QW3 Empresas | Score de cumplimiento v1 | 3-4d | MEDIO |
| QW5 Empresas | SLA alert por email T-2 días | 2d | CRÍTICO |
| QW6 Empresas | Ficha de empresa con tabs | 3-5d | MEDIO |
| QW8 Empresas | Recordatorio ARCO T-2 días | 1-2d | ALTO |
| QW9 Empresas | Editar RUT post-creación | 0.5d | BAJO |
| QW4 ARCO | Dashboard derechos más ejercidos | 1.5d | BAJO |
| QW5 ARCO | Bandeja de entrada del DPO | 3d | ALTO |
| QW6 ARCO | Recordatorio automático al titular | 2d | ALTO |

#### Z-items pendientes (docs/STATUS.md)
| ID | Descripción | Estado |
|---|---|---|
| Z-02 | CORS restrictivo por ruta | Pendiente (BAJA) |
| Z-06 | Logs estructurados JSON / audit_log table | Pendiente (MEDIA) |

> **Nota**: STATUS.md dice Z-01 y Z-03 pendientes, pero **YA ESTÁN HECHOS** (security headers + MIME validation). STATUS.md está desactualizado — actualizar al retomar.

### 3.2 P1 — Importantes

#### Drift entre docs y código (encontrado en esta sesión)
- `docs/manuales/MANUAL_USUARIO.md` dice "wizard de 4 pasos" — código real tiene **5**
- `MANUAL_USUARIO.md` línea 185: "(aún no está, en alguna próxima versión)" — Asistente IA ya implementado como AsesorCustodio
- Roles en manuales: "Admin/Editor/Visualizador" vs código real `superadmin/admin_empresa/usuario`
- Versión en MANUAL_USUARIO: "1.0" vs sistema v1.9

#### QWs del Formulario Público ARCO
Los 10 QWs de "Formulario Público ARCO" son **OBSOLETOS** — el formulario público fue eliminado en julio 2026 (consolidación con TKT). Marcar como NO APLICA en backlog.

#### e2e tests fallidos por auth
Los 20 e2e Playwright fallan porque las credenciales `admin`/`Admin1234!` no existen en QA. Crear:
- Fixture de auth robusta con `E2E_USERNAME`/`E2E_PASSWORD` reales
- O mock auth server

#### Manual para clientes no-técnicos
Conversación del 2026-07-13 con el usuario: quiere crear una **carpeta `manual/` aparte de docs/**, con manuales simplificados para clientes no-técnicos. Estructura propuesta (sin implementar):

```
manual/
├── README.md
├── 00_antes_de_empezar.md
├── modulos/
│   ├── 01_dashboard.md
│   ├── 02_rats.md
│   ├── 03_brechas.md
│   ├── 04_arco.md
│   ├── 05_consentimientos.md
│   └── 06_empresas.md
├── como_se_conectan.md
└── ejemplos/
    ├── caso_retailpro.md
    └── caso_miniempresa.md
```

### 3.3 P2 — Menor

- Limpieza ~104 RATs duplicados en BD
- Refactor `test_user_service.py` (passwords hardcodeados → factory pattern)
- Evaluar purga de commit histórico `48e0d08` (mensaje misleading sobre secrets)
- a11y axe-core: extender tests a páginas autenticadas (requiere fixture con auth real)
- Z-06 audit_log table (P2 → P3, ya hay logging JSON funcionando)

---

## 4. Reglas y convenciones importantes

### Git
- **NUNCA** usar `git -c user.email=...` ni `-c user.name=...` (rompe autor de Vercel)
- Si el autor está mal: `git commit --amend --reset-author --no-verify` + `git push --force-with-lease origin qa`
- Pre-commit hook está roto (python3 no en PATH en Windows) — usar `--no-verify`

### Frontend (UX homologación)
- **REGLA**: usar componentes átomo de `components/ui/` para todo componente nuevo
- **PROHIBIDO** `<button>` con `style={{ background: '#xxx' }}` o `onMouseEnter/onMouseLeave`
- Touch targets WCAG ≥44px obligatorio
- Tokens en `app/globals.css` y `lib/styles.ts`

### Backend
- Tests DEBEN ejecutarse contra Neon QA (`custodio_test`)
- `TEST_DATABASE_URL` configurado en `.env`
- Security headers ya están en `main.py` (línea 145-167)

---

## 5. Comandos útiles para retomar

### Setup
```bash
cd C:\Users\chelo\Desktop\RAT_opencode
git status        # debería estar limpio
git log -3        # ver últimos commits
```

### Tests
```bash
# Frontend unit tests
cd frontend-next
npm test

# Backend tests
cd ../backend
python -m pytest tests/test_qw4_por_tipo.py -v  # nuevo
python -m pytest tests/test_arco_tickets.py -v   # pre-existente con 1 falla
python -m pytest tests/test_dashboard.py -v      # pre-existente con 2 fallas

# E2E Playwright (requiere credenciales)
cd ../frontend-next
npm run test:e2e
```

### Verificar deploys
- QA: https://custodio-qa.vercel.app
- Vercel: cuenta `marcelocollipal-7370`
- Backend API: mismo dominio, FastAPI docs en `/docs`

---

## 6. Hitos del proyecto (resumen)

### Iter 13 (v1.9) — Cerrado
11 hallazgos de auditoría RAT cerrados en commits del 2026-07-07.

### Sesión 2026-07-08/09 (5 commits en qa)
- 4 tests rotos arreglados
- H3.5 BASES_LEGALES deduplication
- H3.12 export DRY + Z-03 MIME validation
- Sistema de diseño inicial (7 átomos)
- Migración masiva a `<Button>` (25+ archivos)
- QW4 ARCO dashboard por_tipo
- Auditoría a11y axe-core

### Próxima sesión (cuando vuelvas)
Opciones ranked:
1. **Crear carpeta `manual/` para clientes no-técnicos** (lo conversado 2026-07-13)
2. **Implementar QWs del backlog** (QW1-QW10 Empresas o ARCO)
3. **Actualizar STATUS.md** (Z-01/Z-03 marcados mal como pendientes)
4. **Actualizar MANUAL_USUARIO.md** (wizard 4→5 pasos, roles, versión)

---

## 7. Archivos clave para entender el sistema

| Archivo | Qué contiene |
|---|---|
| `frontend-next/AGENTS.md` | Convenciones frontend + sistema de diseño |
| `backend/CLAUDE.md` | Convenciones backend + endpoints |
| `docs/STATUS.md` | Estado actual del proyecto (DESACTUALIZADO, requiere update) |
| `docs/SESSION_STATE.md` | Estado sesión 2026-07-03 (DESACTUALIZADO) |
| `docs/backlog_seguimiento.md` | Backlog QWs canónico v1.1 |
| `docs/manuales/MANUAL_USUARIO.md` | Manual usuario (DESACTUALIZADO — 4 pasos vs 5 reales) |
| `frontend-next/components/ui/` | Sistema de diseño (Button, Input, etc.) |
| `backend/app/main.py` | Middleware security headers (línea 145-167) |
| `.opencode/skills/` | 21 skills de compliance + dev |

---

*Generado al cerrar sesión del 2026-07-13. Próxima sesión: retomar desde sección 3 (Pendientes) o sección 6 (próxima sesión) según prioridad.*

## Cómo identificar el documento vigente

Para verificar si tu copia local es la última versión:

| Método | Detalle |
|--------|---------|
| Por fecha | Buscar `2026-07-13` en el banner inicial |
| Por SHA | El último commit fue `aedaecb` — si tu versión no tiene ese SHA en el banner, está desactualizado |
| Por ID único | Buscar `SESSION_HANDOFF_2026-07-13` |

Comandos para sincronizar:
```bash
git fetch origin
git log -1 --oneline origin/qa -- docs/SESSION_HANDOFF.md
# Si el SHA no coincide, hacer: git pull origin qa -- docs/SESSION_HANDOFF.md
```

## Log de cambios

| Fecha | Cambio | Autor |
|-------|--------|-------|
| 2026-07-13 | Creado SESSION_HANDOFF.md consolidando sesiones 2026-07-08 a 2026-07-13 | Emece |
| 2026-07-13 | Banner destacado + ID único + sección "Cómo identificar el documento vigente" | Emece |