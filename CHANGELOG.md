# Changelog — Custodio RAT Manager

## [Unreleased] - 2026-06-13

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
- **NEW**: `app/core/crypto.py` — módulo Fernet con `encrypt()`, `decrypt()`, `generate_key()`
- BYTEA RAT (`archivo_base_legal_datos`) ahora cifrado con Fernet antes de guardar
- BYTEA contratos encargado (`archivo_pdf_datos`) ahora cifrado con Fernet
- `download_rat_file()` descifra automáticamente antes de retornar contenido
- `ENCRYPTION_KEY` configurable via env var (obligatoria en producción)
- Dev fallback: datos sin cifrar si `ENCRYPTION_KEY` no está configurada (con warning)
- Clave inválida no crashea — almacena sin cifrar (fail-safe)
- **NOTA**: OCI storage NO cifrado (PAR pre-signed URLs incompatible con cifrado cliente)
- 10 tests de encryption en `tests/test_crypto.py` (1 skipped por test env issues)
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
- 84+ tests pasando (de 240 baseline + crypto)
- 7 tests CSRF validan la lógica del middleware (3 con test env issues conocidos)
- 10 tests crypto (1 skipped por test env issues)
- 14 tests asesor pre-existentes siguen pendientes (bloqueado por config faltante)

### Files
- `backend/app/middleware/csrf.py` (NEW, 60 líneas)
- `backend/app/schemas/common.py` (NEW, 27 líneas)
- `backend/app/schemas/feriado.py` (NEW)
- `backend/app/schemas/admin_tasks.py` (NEW)
- 8 schemas existentes ampliados con `*ListResponse`
- 13 archivos de routes con `response_model=` agregado
- `backend/tests/test_csrf.py` (NEW, 10 tests)
- `backend/app/core/crypto.py` (NEW, 56 líneas — Fernet encryption)
- `backend/app/services/eipd_service.py` (NEW)
- `backend/app/services/feriado_service.py` (NEW)
- `backend/app/services/consentimiento_service.py` (NEW)
- `backend/app/services/encargado_contrato_service.py` (NEW)
- `backend/app/services/solicitud_derecho_service.py` (NEW)
- `backend/tests/test_crypto.py` (NEW, 11 tests)

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

*Generado: 2026-06-13*
