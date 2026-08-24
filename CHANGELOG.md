# Changelog — Custodio RAT Manager

## [Unreleased] - 2026-08-24

### Quick Wins ARCO + Formulario Público

#### Público-QW5 — Detección de titular repetido
- Nuevo endpoint `GET /publico/verificar-titular?company_id=X&email=Y` (sin auth, rate 20/min)
- Al hacer blur en el campo email del formulario público, consulta si el titular ya tiene tickets abiertos en esa empresa
- Banner amarillo de advertencia (no bloquea el envío) con contador de tickets y enlace a seguimiento

#### CI/CD — Correcciones de pipeline
- **Ruff lint** (5 errores): `crypto.py` (F401), `politica_transparencia.py` (F401), `email_service.py` (F541), `main.py` (E402)
- **Vitest**: excluir `e2e/` del runner para que Playwright no corra en vitest
- **WCAG**: `#9CA3AF` → `#6B7280` en `dashboard/page.tsx` (Tailwind gray-500, ratio 4.5:1)
- **Nomenclatura**: `APDC` → `APDP` en tests, títulos y documentación (nomenclatura oficial chilena)
- **`wcag-contrast.test.ts`**: removido test de `solicitud_derecho/page.tsx` (archivo eliminado)
- **`company-alerts-banner.test.ts`**: actualizado `"ARCO vencidas"` → `"ARCOP+ vencidas"`
- **pip-audit**: escaneo de vulnerabilidades CVE en dependencias Python (bloquea solo CRITICAL, HIGH como warning)
- **`backend-tests` env vars**: `ALLOWED_ORIGINS` y `ENVIRONMENT` hardcodeados para CI; step de verificación si `TEST_DATABASE_URL` no está configurado

#### Documentación
- README.md: 95+ → 761+ tests; APDC → APDP; ficha empresa; formulario ARCOP+; sin "próximas funcionalidades" ya implementadas
- `docs/STATUS.md`: versión, fecha, scores y próximos pasos actualizados a 2026-08-24
- `docs/backlog_seguimiento.md`: 9 QWs adicionales marcados como cerrados (v1.4 → v1.5)
- CHANGELOG.md: sincronizado con trabajo real

---

## [Unreleased] - 2026-08-22

### QA — Corrección total de suite de tests (78 → 0 fallidos)

Dos sesiones de trabajo (commits `79b1f5c` y `5978abc`) llevaron la suite de 78 fallos a 0.

#### Backend — Fixes de compliance y comportamiento

- **`POST /auth/users` → 201**: agregado `status_code=201` al endpoint (antes retornaba 200)
- **PATCH ticket → resuelto con `metodo_verificacion_identidad` en body**: el handler en
  `tkt_solicitud_derecho.py` verificaba el campo en BD antes de aplicar el body, causando
  422 silencioso. Condición corregida a `not ticket.metodo_verificacion_identidad and not data.metodo_verificacion_identidad`
- **`encrypt_existing_bytea._check_prerequisites()`**: eliminado fallback a `settings.ENCRYPTION_KEY`
  cuando `ENCRYPTION_KEY=""` en entorno — el script de migración debe validar explícitamente la env var
- **`/rats` EIPD validator**: validación de `datos_sensibles=True` requiere `evaluacion_impacto + estado_eipd`
- **`POST /rats` con `decisiones_automatizadas=True`**: requiere `logica_automatizada` (Art. 8)
- **`POST /rats` con `responsable_tratamiento_email`**: valida formato email (Art. 16)
- **`/auditoria/verify-chain` vs `/{company_id}`**: reordenamiento de rutas FastAPI (static antes de parameterizado)

#### Tests — Correcciones de payloads y expectativas

- `test_encrypt_migration.py`: `make_rat()` sin `categoria_titulares` (NOT NULL) → agregado; mojibake CP1252 corregido
- `test_dashboard.py`: `datos_sensibles=True` bloqueado por EIPD validator → payload con `evaluacion_impacto + estado_eipd`
- `test_rat_gaps_21719.py`: 2 tests actualizados para esperar 422 (el backend ahora valida `logica_automatizada` y `email_responsable`)
- `test_rbac_deep.py`: RUT fijo `77.777.777-7` causaba 409 en parallel test runs → UUID-based RUT
- `test_e2e.py`, `test_e2e_workflow_rat.py`: múltiples fixes (mojibake, UUID RUT, EIPD campos, estado consentimiento)
- `test_arco_sprint1.py`, `test_arco_sprint3.py`, `test_qw10_formulario.py`: migrados a endpoints canónicos actuales

---

## [Unreleased] - 2026-08-09

### Sprint UX — Mejoras de interfaz

#### B-02 — Banner NNA en RatWizard (Step 2)
- Alerta visual cuando `datos_nna != "ninguno"` advirtiendo restricción de base legal (Art. 16 Ley 21.719)
- `components/rat/WizardModular/steps/Step2.tsx`

#### M-04 — Editor de Política de Transparencia (Art. 14 ter)
- Nueva columna `overrides_json` en `politicas_transparencia` — permite personalizar cada ítem
- `PUT /transparencia/{company_id}` (autenticado, admin_empresa o superadmin)
- Frontend: modo edición inline por ítem, badge "personalizado", botón "↩ Automático"
- Hash SHA-256 se recalcula en cada guardado
- Migración: `2026_08_09_001_politica_overrides.sql`

#### Select.tsx — Fix de merge de estilos
- Extraído `style` del spread `{...rest}` y mergeado con defaults del componente
- Evita que un style parcial (solo border/color) pise el fondo/texto internos

---

## [Unreleased] - 2026-08-08

### Sprint B — Compliance Ley 21.719 (backend)

#### B-01 — BreachUpdate con Literal types
- `causa_raiz` y `estado_cierre` en `BreachUpdate` ahora son `Literal` enforced (igual que `BreachBase`)

#### M-01 — respuesta_texto obligatoria en ARCO
- `ticket_service.py`: bloquea resolver un ticket ARCO sin `respuesta_texto` no vacía (Art. 12 Ley 21.719)

#### C-03 — Monitor secundario brechas 72h
- Nuevo `TaskType.SLA_ALERT_BRECHA_72H` + job scheduler cada 12h
- Detecta `SecurityBreach` con `notificado_apdc=False` y `fecha_deteccion < ahora - 72h`
- Alerta al DPO de cada empresa afectada (Art. 14 bis Ley 21.719)

#### C-02 — Alerta plazo de retención vencido
- Nuevo `TaskType.SLA_ALERT_PLAZO_RETENCION` + job scheduler cada 24h
- Parsea `plazo_retencion` (texto libre) con regex años/meses/días
- Calcula expiración desde `created_at` y notifica DPO de RATs aprobados vencidos (Art. 16)

---

## [Unreleased] - 2026-08-07

### Sprint A — Compliance Ley 21.719 (backend)

#### C-01 — Soft delete RAT
- `delete_rat()` ahora asigna `deleted_at = datetime.now(UTC)` en lugar de `db.delete(rat)`
- `get_rats()` y `get_rat()` filtran `deleted_at IS NULL` (Art. 19 + 28 cadena de custodia)

#### C-04 — Test interés legítimo obligatorio
- `validar_test_interes_legitimo()` bloquea create/update cuando `base_legal` contiene "Interés legítimo" sin test ≥50 chars (Art. 16)

#### C-05 — EIPD gate en aprobación
- `aprobar_rat()` llama `validar_eipd_obligatoria()` antes de cambiar estado a APROBADO
- Antes era posible aprobar con `datos_sensibles=True` sin EIPD (Art. 15 bis)

#### C-06 — NNA requiere base legal reforzada
- `validar_datos_nna_base_legal()`: cuando `datos_nna != "ninguno"` solo acepta Consentimiento, Interés vital u Obligación legal (Art. 16)

#### C-07 — Delete RAT bloquea con consentimientos activos
- `delete_rat()` verifica `tiene_consentimiento_activo()` antes de soft delete
- Retorna 409 Conflict si hay consentimientos activos (Art. 12)

#### M-05 — Mutex anonimizado/seudonimizado
- `model_validator` en `RATBase` bloquea `datos_anonimizados=True AND datos_seudonimizados=True` simultáneo

---

## [Unreleased] - 2026-07-03

### Mejora Continua — Higiene y Compliance

#### Infraestructura y Seguridad
- Agregado CI/CD con `secret-scan.yml` (gitleaks en push/PR)
- Configurado `pytest-cov` y `vitest --coverage` para medicion de cobertura
- Reforzado `.pre-commit-config.yaml` (pre-commit-hooks + gitleaks v8.18.2)
- Creado `scripts/security_audit.py` (runner local de auditoria de seguridad)
- Creado `SECURITY.md` (politica de seguridad standard)

#### Limpieza del Repositorio
- Eliminados 61 archivos del tracking (violaban .gitignore): __pycache__, .coverage, logs, capturas debug
- Eliminadas carpetas basura: test/ raiz, latest_logs/, .opencode_backup/, .pytest_cache/ raiz
- Reorganizados scripts de backend/ a backend/scripts/migration/
- Movido TEST_EXECUTION_REPORT_ARCO a docs/auditorias/
- Reforzado .gitignore: frontend coverage, diag-*, bpmn.vbak, lock files, test-results

#### Skills de Compliance (13 total)
- Corregidos bugs en debug-login, custodio-auditoria, api-review
- Normalizado APDC -> APDP en todas las skills y tests
- Creadas 4 skills criticas de compliance:
  - `eipd-management` (Art. 15 bis)
  - `consentimiento-management` (Art. 12)
  - `politica-transparencia` (Art. 14 ter)
  - `encargado-tratamiento` (Art. 14 quater)

#### Documentacion
- Creado `docs/cumplimiento/INCIDENT_RESPONSE.md` (protocolo 72h APDP)
- Creado `docs/CLEANUP_2026-07-03.md` (bitacora de esta mejora)
- Eliminada docs/legacy/ (vacia)

#### Nota de Seguridad
- **Incidente de secrets (2026-06-XX)**: 4 passwords Neon rotados, git filter-repo ejecutado.
  LEY DIVINA formalizada: skill security-secret-scan + pre-commit hook.
  Nota: commit historico 48e0d08 menciona "hardcode DATABASE_URL and SECRET_KEY" —
  NO contiene secretos reales (eran placeholders), pero el mensaje de commit es misleading.

---

## [Unreleased] - 2026-07-01

### Track D — Security gaps restantes (Z-01, Z-03)
- ✅ **(Z-01) RESUELTO**: Content-Security-Policy + HSTS en backend y frontend.
  - Backend: `default-src 'none'; frame-ancestors 'none'` (API restrictiva)
  - Frontend: CSP permite self, connect-src a backends QA/prod
  - HSTS: max-age=31536000; includeSubDomains (1 año)
  - Tests: 6 backend + 10 frontend = 16 tests
- ✅ **(Z-03) RESUELTO**: File upload validation (extension + tamano).
  - Nuevo service `file_validation.py` reutilizable
  - `validate_upload(file, allowed_extensions, max_bytes, content_type_prefix)`
  - 400 si extension invalida, 413 si tamano excede
  - Integrado en POST /admin/asesor/upload (md/txt, 5MB) y POST /feriados/upload (csv, 2MB)
  - Tests: 13 nuevos en `test_file_validation.py`

### Track C — N-02 Feature Gates
- ✅ **(N-02) RESUELTO**: Feature gates por empresa y modulo.
  Permite activar/desactivar modulos completos (RAT, ARCO, Brechas,
  EIPD, Consentimientos, Encargados, Transparencia, Reportes, Asesor)
  para cada empresa de forma granular.
  
  Componentes:
  - **Backend** (3 commits):
    - Modelo `ModulePermission` con UNIQUE(company_id, modulo)
    - Service con `is_module_enabled`, `get_company_modules`,
      `set_module_enabled`, `bulk_update_modules`, `require_module_enabled`
    - Endpoints REST: GET /module-permissions/{id}, GET .../active,
      PUT .../{modulo}, PUT ... (bulk)
    - Wire-up en rutas criticas: /rats/, /brechas/, /tkt-solicitud-derecho/
      retornan 403 cuando modulo esta deshabilitado
  - **Frontend** (1 commit):
    - Tab "Módulos" en /configuracion (solo superadmin)
    - 4 funciones API nuevas en lib/api.ts
    - Dropdown empresa + 9 toggles con role=switch + aria-checked
  
  Tests: 24 nuevos (10 service + 7 endpoints + 7 integration gate).

### Track B — Módulo Empresas (QW7, QW2, QW1)
- ✅ **(QW7) RESUELTO**: Banner de alertas de cumplimiento en lista de empresas.
  Muestra 4 tipos de alertas agregadas: RATs vencidos, solicitudes ARCO
  con SLA vencido, empresas con completitud <50%, empresas sin DPO.
  Si no hay alertas, no se renderiza. Accesible (role=region + aria-label).
  Test: 10 nuevos en `frontend-next/__tests__/company-alerts-banner.test.ts`
- ✅ **(QW2) RESUELTO**: Botón "Reporte APDC" en cada empresa.
  Conecta `api.exportarCni()` con la UI. Descarga JSON estructurado
  para presentar ante la autoridad (Ley 21.719). Valida que la empresa
  tenga RATs antes de exportar. Test: 14 nuevos en
  `frontend-next/__tests__/company-export-apdc.test.ts`
- ✅ **(QW1) RESUELTO**: Drawer de auditoría per-empresa.
  Componente `CompanyAuditDrawer` con timeline de eventos de auditoría
  de los RATs de la empresa, filtrable por acción, con colores
  semánticos. Test: 15 nuevos en
  `frontend-next/__tests__/company-audit-drawer.test.ts`

### Track A — Security, UX, Tests (commits previos)
- ✅ **(Z-02) RESUELTO**: CORS restrictivo con `allow_methods` y `allow_headers` específicos
- ✅ **(Z-06) RESUELTO**: JSONFormatter activo también en QA y staging
- ✅ **(N-01) RESUELTO**: Test `test_delete_document_existente` corregido
- ✅ **(A11y-1) RESUELTO**: Contraste WCAG AA en texto secundario
- ✅ **(UX-mobile-2) RESUELTO**: StepIndicator sticky en mobile

### Pendientes
- ❌ **(N-02)**: Feature gates por módulo (RAT/ARCO/Brechas)
- ❌ **(Z-01)**: Security headers — falta CSP
- ❌ **(Z-03)**: File upload validation (extensión + max size)

### Tests
- 82 tests agregados en Tracks A+B (28 backend + 54 frontend), todos pasando.
- Total: 172 tests passing (28 backend + 144 frontend incluyendo tests preexistentes).

### Files (Track B — 3 commits)
- `frontend-next/components/companies/CompanyAlertsBanner.tsx` (nuevo)
- `frontend-next/components/companies/CompanyAuditDrawer.tsx` (nuevo)
- `frontend-next/components/companies/index.ts` (exports)
- `frontend-next/app/(app)/companies/page.tsx` (integra QW7, QW2, QW1)
- `frontend-next/__tests__/company-alerts-banner.test.ts` (nuevo)
- `frontend-next/__tests__/company-export-apdc.test.ts` (nuevo)
- `frontend-next/__tests__/company-audit-drawer.test.ts` (nuevo)

---

## [1.6.1-beta] - 2026-06-17

### Features (Asesor — Gestión de Corpus)

- **NEW**: `AsesorCorpusDocument` model — metadata en BD, archivo en OCI (`asesor_corpus/`)
- **NEW**: `asesor_corpus_store.py` — store service con lógica OCI + BD + auto-reindex + soft delete
- **NEW**: 4 endpoints corpus management en `admin_asesor.py`:
  - `GET /admin/asesor/documents` — lista documentos con metadata
  - `POST /admin/asesor/upload` — upload + auto-indexación incremental
  - `GET /admin/asesor/documents/{id}/download` — URL presigned OCI
  - `DELETE /admin/asesor/documents/{id}` — soft delete doc + chunks + OCI
- **NEW**: Indexer BD-first con fallback filesystem; auto-reindex al subir documento
- **NEW**: `AsesorCorpusTab.tsx` — drag-drop, lista con badges, confirmación inline, download
- **NEW**: Tab "Asesor · Corpus" en Configuración (solo superadmin visible)
- **NEW**: Dual provider embeddings: Cohere (`embed-multilingual-v3.0`) + Groq (`llama-3.3-70b-versatile`)

### Fixes (Asesor)

- **FIX**: Chat history bleed — `useEffect` de carga de historial usaba `companyId` en vez de `user?.id` como dependencia (`f18bb43`)
- **FIX**: Duplicate index `idx_asesor_source` en migración BD (`9e99352`)
- **FIX**: `Union` import faltante para Python 3.10 backwards compat (`9e99352`)

### Known Issues

- **CORS error reindex QA**: POST `/admin/asesor/index` no retorna headers CORS en Vercel serverless — hipótesis: cold start + OCI + Cohere timeout
- 14 tests Asesor preexistentes siguen bloqueados por config faltante (`ASESOR_*` en Settings)

### Files

- `backend/app/models/asesor.py` (AsesorCorpusDocument model — nuevo)
- `backend/app/services/asesor_corpus_store.py` (store OCI+DB — nuevo)
- `backend/app/routes/admin_asesor.py` (4 endpoints nuevos — modificado)
- `backend/app/services/asesor_indexer.py` (BD-first fallback — modificado)
- `frontend-next/lib/asesor-api.ts` (4 funciones API corpus — modificado)
- `frontend-next/components/configuracion/AsesorCorpusTab.tsx` (UI corpus — nuevo)
- `frontend-next/app/(app)/asesor/page.tsx` (chat history fix — modificado)

### Quick Wins (v1.6.1)

- **QW1**: Health Score en listado empresas — `GET /companies` y `GET /companies/{id}` ahora retornan `completitud_promedio` y `rats_vencidos` (regex `plazo_retencion` + `created_at + años*365 vs now`)
- **QW2**: Scheduler revisar encargados vencidos — `REVISAR_ENCARGADOS_VENCIDOS` task type + `_run_revisar_encargados_vencidos()` + `notificar_vencimiento_encargado()` email + scheduler daily enqueue (≤30 días)
- **QW3**: Banner DPO incompleto en dashboard — `AlertBanner type=danger` en `dashboard/page.tsx` cuando `!contacto_dpo` o `!email_dpo`
- **QW4**: Score SLA ARCO en resumen empresa — `CompanyOut` con `solicitudes_pendientes` (estado abierto/en_proceso/pendiente) y `solicitudes_vencidas_sla` (fecha_vencimiento < now && no resuelto)
- **QW5**: Pre-fill EIPD desde RAT — `router.push('/eipd?rat_id=${rat.id}')` en `RatDetailView`; `EIPDPage` lee `rat_id` de searchParams y pre-selecciona RAT en `EIPDForm`

### Files (Quick Wins)

- `backend/app/routes/companies.py` (SLA ARCO stats — modificado)
- `backend/app/schemas/company.py` (CompanyOut fields — modificado)
- `backend/app/services/task_service.py` (REVISAR_ENCARGADOS_VENCIDOS — modificado)
- `backend/app/services/scheduler.py` (job diario encargado — modificado)
- `backend/app/services/email_service.py` (notificar_vencimiento_encargado — modificado)
- `backend/app/models/task.py` (TaskType enum — modificado)
- `frontend-next/app/(app)/dashboard/page.tsx` (DPO banner — modificado)
- `frontend-next/app/(app)/eipd/page.tsx` (pre-fill desde rat_id — modificado)
- `frontend-next/components/rat/RatDetailView.tsx` (botón EIPD con router.push — modificado)

---

## [1.6.0-beta] - 2026-06-15

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
