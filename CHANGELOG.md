# Changelog — Custodio RAT Manager

## [Unreleased] - 2026-06-15

### Security
- (N-01) **PENDIENTE**: Asesor module — 9 constantes `ASESOR_*` faltantes en `backend/app/core/config.py` bloquean 14 tests y generan riesgo de crash en producción

### Features
- (N-02) **PENDIENTE**: Feature gates por módulo (RAT/ARCO/Brechas) — tabla `module_permissions` + endpoints + UI superadmin en `/configuracion`

### Pending (from v1.5 audit — Z-01/Z-02/Z-03/Z-06)
- (Z-01) Security headers: CSP, X-Frame-Options, X-Content-Type-Options
- (Z-02) CORS restrictivo: `allow_methods` y `allow_headers` específicos
- (Z-03) File upload validation: extensión y max size
- (Z-06) Backups documentados

---

## [1.6.0-beta] - 2026-06-15

### Features (UI/UX — RatDetailModal + Drawer)
- **NEW**: `RatDetailModal` con tabs Ver/Editar — componente React con `useReducer` para modo, `PdfPreview` integrado para archivo base legal
- **NEW**: `PdfPreview` — visor de PDF con fallback link a nueva pestaña
- **NEW**: `Drawer` responsive con 5 size variants (`sm/md/lg/xl/full`) — `sm:` 400px, `lg:` 55vw, `xl:` 70vw, maxHeight 92vh, `hasHeader` conditional, `aria-label` fallback
- **NEW**: Dashboard clickable — tarjetas "recientes" abren RAT en modal in-page (misma ruta), sin navegación

### Security
- **FIX**: `/rats/{id}/archivo` — IDOR cerrado: `get_rat()` + `require_editor_or_admin_empresa()` antes de servir archivo
- **FIX**: HTTPException propagation — `try/except` envuelve `download_rat_file()` para propagar 404/403/500 correctos (no más 500 silencioso)

### Performance
- **NEW**: `AppContext.Provider` envuelto en `useMemo` — elimina re-renders innecesarios de toda la app
- **NEW**: `GroupedRows` hoisted a nivel de módulo en `reportes/page.tsx` — evita remount de `<tbody>` completo en cada keystroke
- **NEW**: Conditional mount ARCO: `TicketDrawer` y `CreateTicketForm` montados solo cuando `open=true` — ahorra 22 hook allocations
- **NEW**: `useMemo` para `recientes`, `sinRevisionCount`, `alertas` en dashboard — orden correcto (antes de early returns)
- **NEW**: `useRef(Date.now())` para capturar timestamp una sola vez — cumple regla "no impure calls in render"
- **NEW**: `openDrawer` useCallback estable con `auditLogsRef.current` — sin deps en estado

### Fixes (UI)
- **FIX**: Sort stable — `[...arr].sort()` reemplaza `toSorted()` (ES2024 → ES2019) en RAT, ARCO, Brechas, Encargados, Usuarios, Dashboard
- **FIX**: Rules of Hooks — `useMemo` de `recientes`/`sinRevisionCount`/`alertas` movidos antes de `if (!company)` y `if (!hasCache)` en dashboard
- **FIX**: ARCO KPI grid — `lg:grid-cols-6` (6 cards en laptop), `p-3`, `w-8 h-8`, `gap-2.5` en lugar de 3-wide desktop
- **FIX**: Drawer title no duplicado — `Drawer title=""` ahora collapsible, tabs movidas dentro del gradient header
- **FIX**: ARCO badges colapsables — secondary badges agrupados en `<details>` con `+N más` en RatDetailView
- **FIX**: Audit timeline estructurado en RatDetailView — dots + timestamps + color-coded actions

### Changed
- RatDetailView: 4 secciones con blue uppercase headers, table-layout fields, deletion confirmation en caja roja
- Duplicar RAT: `onDuplicate` en dashboard ahora llama `api.duplicarRat()` + refresh stats+lista (no más navigate vacío)

### Security (S14 — CSRF Protection)
- **BREAKING**: Cookies `samesite=none` → `samesite=lax` en producción (mitigación cross-site POST)
- **NEW**: `CSRFMiddleware` — valida `X-Requested-With: XMLHttpRequest` en requests mutantes con cookie
- Requests con `Authorization: Bearer` exentas de CSRF (no vulnerables)
- Endpoints públicos (`/auth/login`, `/publico/*`, `/ai/ask`, etc.) exentos
- Fix: `CSRF_SAFE_PATHS` removió `/` que matcheaba todos los routes

### API (A10 — Schemas Pydantic)
- **NEW**: 35+ endpoints con `response_model` válido (era 0%)
- Schemas wrapper: `MessageResponse`, `OkResponse`, `PaginatedResponse[T]`, `DeleteResponse`
- Schemas específicos: `CompanyListResponse`, `BreachListResponse`, `EIPDListResponse`, `EncargadoContratoListResponse`, `ConsentimientoListResponse`, `UserListResponse`, `FeriadoListResponse`, `FeriadoYearsResponse`, `FeriadoUploadResponse`, `TaskListResponse`, `TaskStatsResponse`, `TaskRunResponse`, `TaskEnqueueResponse`
- OpenAPI spec ahora completo en `/docs` y `/openapi.json`
- **No breaking**: keys JSON mantenidos para compatibilidad frontend (`empresas`, `brechas`, `eipds`, etc.)

### Security (C1 — Encryption at Rest)
- **NEW**: `app/core/crypto.py` — módulo Fernet con `encrypt()`, `decrypt()`, `generate_key()`, `is_already_encrypted()`
- BYTEA RAT (`archivo_base_legal_datos`) ahora cifrado con Fernet antes de guardar
- BYTEA contratos encargado (`archivo_pdf_datos`) ahora cifrado con Fernet
- `download_rat_file()` descifra automáticamente antes de retornar contenido
- `ENCRYPTION_KEY` configurable via env var (obligatoria en producción)
- Dev fallback: datos sin cifrar si `ENCRYPTION_KEY` no está configurada (con warning)
- Clave inválida no crashea — almacena sin cifrar (fail-safe)
- Heurística `is_already_encrypted()` con prefijo Fernet `b"gAAAAA"` (fail-safe, sin cambios de esquema)
- **C1-F5**: Script de migración `scripts/migration/encrypt_existing_bytea.py` — one-shot, idempotente, dry-run, batch commits, backup SQLite automático, 18 tests en `tests/test_encrypt_migration.py`
- **NOTA**: OCI storage NO cifrado (PAR pre-signed URLs incompatible con cifrado cliente — evaluar Oracle KMS en futuro)
- 10 tests crypto en `tests/test_crypto.py` (1 skipped)
- Requirements: `cryptography==43.0.0` agregado

### Architecture (A6 — Service Layer)
- **NEW**: `eipd_service.py` — EIPD CRUD con validación RAT, enum conversion, audit
- **NEW**: `feriado_service.py` — CSV parsing/validation, bulk holiday management
- **NEW**: `consentimiento_service.py` — Consent CRUD con RAT validation, revocation logic
- **NEW**: `encargado_contrato_service.py` — PDF processing (encrypt/hash), alert date calculation
- **NEW**: `solicitud_derecho_service.py` — Token management, solicitud lifecycle, bloquear/desbloquear
- Route handlers refactorados: ahora son thin wrappers que delegan a services
- Lógica de negocio centralizada para mejor testabilidad y mantenibilidad

### Fixed
- `app/core/limiter.py`: rate limiter usa per-request UUID en test mode (evita contaminación entre tests)
- `app/middleware/csrf.py`: bug crítico — `"/"` en `CSRF_SAFE_PATHS` causaba que `startswith("/")` matcheara TODO

### Changed
- Documentación: aclaración de MiniMax (primario) y OpenAI (fallback opcional) en `.env.example` y skill

### Tests
- 140+ tests pasando (baseline + crypto + migration)
- 7 tests CSRF validan la lógica del middleware
- 10 tests crypto (1 skipped)
- 18 tests migration (C1-F5, 100% pass)
- 14 tests asesor pre-existentes siguen pendientes (bloqueado por config faltante)

### Files
- `backend/app/middleware/csrf.py` (NEW, 60 líneas)
- `backend/app/schemas/common.py` (NEW, 27 líneas)
- `backend/app/schemas/feriado.py` (NEW)
- `backend/app/schemas/admin_tasks.py` (NEW)
- 8 schemas existentes ampliados con `*ListResponse`
- 13 archivos de routes con `response_model=` agregado
- `backend/tests/test_csrf.py` (NEW, 10 tests)
- `backend/app/core/crypto.py` (NEW, 60 líneas — Fernet encryption)
- `backend/app/services/eipd_service.py` (NEW)
- `backend/app/services/feriado_service.py` (NEW)
- `backend/app/services/consentimiento_service.py` (NEW)
- `backend/app/services/encargado_contrato_service.py` (NEW)
- `backend/app/services/solicitud_derecho_service.py` (NEW)
- `backend/tests/test_crypto.py` (NEW, 11 tests)
- `backend/scripts/migration/encrypt_existing_bytea.py` (NEW, 305 líneas — C1-F5 migration)
- `backend/tests/test_encrypt_migration.py` (NEW, 446 líneas, 18 tests)

### Known Issues
- Asesor tests: 14 fallan por `ASESOR_CHUNK_SIZE`/`ASESOR_TOP_K` no en `Settings` (pre-existente, bloqueado por usuario)
- CSRF tests: 2 con test env quirks (`test_head_options_always_allowed` → 405 router no soporta OPTIONS, `test_public_endpoint_no_csrf_required` → 401 db session en test). Lógica del middleware validada en los 7 restantes.

---

## [1.3.1] - 2026-06-13

### Fixed
- OCI: Fallback a download directo cuando PAR falla (commit `57cbffc`)
- OCI: `sign_headers()` acepta `content_type` como keyword argument
- storage.py: Content-Type para requests con body JSON

### Changed
- Reorganización de carpetas del proyecto
- Scripts movidos a `scripts/{debug,maintenance,legacy}/`
- Documentación movida a `docs/{arquitectura,auditorias,despliegue,...}/`
- Auditorías consolidadas en `docs/auditorias/`

## [1.3.0-beta] - 2026-06-09

### Fixed
- RBAC: `admin_empresa` no puede crear RAT en empresa ajena
- RBAC: `usuario` no puede crear brechas de seguridad
- Endpoint `/health` creado
- `_get_user()` wrapper corregido en consentimientos y eipd
- Token blacklist implementado

### Added
- Páginas `/consentimientos` y `/eipd` en frontend
- Hash chain de auditoría verificable
- PII masking en logs

### Changed
- Score de seguridad: 7/10 → 8.5/10
- Score general: 6.3/10 → 7.5/10

## [1.2.0] - 2026-06-08

### Fixed
- IDOR en `/companies/{id}`
- `/companies/publico` sin autenticación
- CSV injection en exports
- Índices faltantes en BD
- N+1 queries

### Added
- Repository pattern base
- Audit hash chain
- Token blacklist

## [1.1.0] - 2026-05-31

### Added
- Sistema de roles (superadmin, admin_empresa, usuario)
- Módulo de consentimientos (Art. 12)
- Módulo EIPD (Art. 15 bis)
- Cola de tareas asíncronas
- OnboardingChecklist

### Fixed
- Rate limiting en endpoints de auth
- Validación de RUT chileno

## [1.0.0] - 2026-05

### Added
- CRUD completo de RATs
- Gestión de empresas y usuarios
- Módulo de brechas de seguridad (Art. 14 bis)
- Módulo ARCO (Solicitudes de Derecho)
- Exportación PDF y CSV
- Chat IA

---

## Reglas de Versionado

- **MAJOR**: Breaking changes (ej: cambio de modelo de datos)
- **MINOR**: Nuevas funcionalidades compatibles
- **PATCH**: Bug fixes y mejoras menores

## Formato de Commits

```
feat: nueva funcionalidad
fix: bug fix
chore: mantenimiento (deps, refactor, docs)
docs: solo documentación
test: solo tests
refactor: refactorización de código
security: fix de seguridad
```

---

*Generado: 2026-06-14*
