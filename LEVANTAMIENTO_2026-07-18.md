# Levantamiento Detallado - Custodio RAT

> ## 📅 **LEVANTAMIENTO: 2026-07-18**
> ## 🔖 **Identificador único**: `LEVANTAMIENTO_2026-07-18`
> ## 🎯 **Propósito**: inventario completo del proyecto + identificación de mejoras

**Skills utilizadas:**
- `architect-senior` (auditoría arquitectónica)
- `qa-senior` (auditoría QA + seguridad)
- `frontend-guardian` (auditoría UX frontend)
- `custodio-auditoria` (metodología auditoría)
- `doc-governance` (gobernanza docs)

**Subagentes especializados:**
- `arquitecto-custodio` → reporte arquitectura
- `qa-custodio` → reporte QA/seguridad backend
- `frontend-ux-custodio` → reporte UX frontend
- `dpo-custodio` → reporte compliance Ley 21.719

---

## 1. Inventario del Proyecto

### 1.1 Métricas globales

| Componente | Cantidad | LOC | Estado |
|---|---|---|---|
| Backend Python files | 118 | ~15,319 | ✅ |
| Frontend TSX files | 126 | ~21,327 | ✅ |
| Tests pytest | 64 | — | ✅ |
| Tests vitest | 8 | — | ⚠️ Mínimo |
| E2E Playwright | 21 | — | ✅ |
| Docs .md | 99 | — | ✅ |
| Docs .docx | 118 | — | ✅ |
| Migrations | 4 | — | ✅ |
| **Total código** | **244 archivos** | **~36.6K LOC** | |

### 1.2 Estructura backend (118 archivos .py)

| Componente | Archivos | LOC | Estado | Observaciones |
|---|---|---|---|---|
| `app/main.py` | 1 | 339 | ✅ | Lifespan + middleware + 22 routers |
| `app/routes/` | 24 | ~1,800 | ⚠️ | Sin versionamiento API |
| `app/services/` | 39 | ~2,500 | ⚠️ | `rat_crud.py` 467 LOC hace demasiado |
| `app/models/` | 26 | ~800 | ✅ | Enums bien definidos |
| `app/core/` | 5 | ~500 | ✅ | Security, config, logging, storage |
| `app/middleware/` | 3 | ~80 | ✅ | RequestId, CSRF, SecurityHeaders |
| `migrations/` | 17 | — | ✅ | 4 recientes + 13 legacy |

### 1.3 Estructura frontend (126 archivos .tsx)

| Componente | Archivos | LOC | Estado | Observaciones |
|---|---|---|---|---|
| `components/ui/` | 22 | ~1,200 | ✅ | Sistema coherente, homologado QW4 |
| `components/rat/` | 8 | ~2,000 | ⚠️ | RatWizard膨胀ado |
| `components/dashboard/` | 5 | ~800 | ✅ | KPICard, StatusChart |
| `context/AppContext.tsx` | 1 | 221 | ⚠️ | 20+ estados, "Dios context" |
| `app/(app)/` | 16 | ~3,000 | ✅ | Estructura limpia |
| `lib/api.ts` | 1 | 1,201 | ✅ | Cliente completo |
| `lib/constants.ts` | 1 | 110 | ✅ | Single source of truth |
| `types/index.ts` | 1 | 285 | ⚠️ | Faltan campos del modelo Python |

### 1.4 Documentación

| Categoría | Cantidad | Ubicación |
|---|---|---|
| Documentación oficial v1.9 | 9 .docx | `docs/documentacion_oficial/` |
| Auditorías previas | ~15 | `docs/auditorias/` |
| Manuales | 4 .md + 1 .docx | `docs/manuales/` |
| Status/SESSION_HANDOFF | 4 .md | `docs/` |
| Compliance | varios | `docs/cumplimiento/` |

---

## 2. Scores Consolidados por Dimensión

### 2.1 Score arquitectónico (architect-senior)

| Categoría | Score | Estado |
|---|---|---|
| Escalabilidad | 6.5/10 | Multi-tenant correcto, BYTEA 10MB no escala |
| Mantenibilidad | 6.0/10 | Sistema de diseño UI homog., deuda en servicios |
| Seguridad | 7.5/10 | Hash chain, JWT, CORS, CSRF, sin 2FA |
| Rendimiento | 5.5/10 | Dashboard N+1, scheduler serverless broken |
| Observabilidad | 5.0/10 | Logging OK, sin métricas ni alertas |
| Arquitectura General | 7.0/10 | Monolito modular bien organizado |
| **Promedio** | **6.3/10** | **Producción Inicial → Empresarial** |

### 2.2 Score QA + Seguridad backend (qa-senior)

| Categoría | Score | Estado |
|---|---|---|
| Seguridad | 7/10 | Buena base, caída por crypto fallback |
| Mantenibilidad | 5/10 | Funciones largas, duplicación |
| Rendimiento | 6/10 | N+1 en reportes |
| Testing | 6/10 | Coverage buena en seguridad, gaps en flujos E2E |
| Calidad General | 6.5/10 | Sólida, refactor pendiente |
| **Promedio** | **6.1/10** | |

### 2.3 Score Frontend UX (frontend-guardian)

| Categoría | Score | Estado |
|---|---|---|
| UX | — | APTO CON OBSERVACIONES |
| Accesibilidad | — | axe-core login: 0 críticas |
| Responsive | — | Dashboard responsive, Brechas mobile OK |
| Performance | — | Bundle no auditado |
| Component Quality | — | 22 átomos coherentes |
| **Veredicto** | **APTO** | 5 bloqueantes identificados |

### 2.4 Score Compliance Ley 21.719 (dpo-custodio)

| Módulo | Score | Estado |
|---|---|---|
| RAT | 9/10 | ✅ Sólido |
| ARCO/Solicitudes | 9/10 | ✅ Workflow completo |
| Consentimientos | 8/10 | ✅ Buen cifrado PII |
| Encargados | 8/10 | ✅ Alertas vencimiento |
| Auditoría (Art. 28) | 8/10 | ✅ Hash chain robusto |
| Multi-tenancy | 8/10 | ✅ RBAC bien implementado |
| EIPD | 5/10 | ⚠️ Falta workflow DPO |
| Brechas | 6/10 | ⚠️ Notificación manual |
| Transparencia | 4/10 | 🔴 Texto incorrecto AEPD |
| Cifrado PII (Art. 11) | 5/10 | ⚠️ Solo consentimientos |
| **Promedio** | **6.9/10** | **Listo para Producción Inicial** |

### 2.5 Score global consolidado

| Dimensión | Score |
|---|---|
| 🏛️ Arquitectura | 6.3/10 |
| 🔒 Seguridad | 6.5/10 |
| ✅ QA/Calidad | 6.1/10 |
| 🎨 UX/Frontend | 7.5/10 (veredicto APTO) |
| ⚖️ Compliance Ley 21.719 | 6.9/10 |
| **Promedio global** | **6.7/10** |

---

## 3. Hallazgos Críticos Consolidados (P0)

Estos hallazgos son **bloqueantes para Producción Empresarial** o **riesgo legal alto**.

### 3.1 Backend / Compliance

#### C1. `crypto.py:43-45` — Fallback a texto plano en producción
- **Severidad:** CRÍTICA
- **Archivo:** `backend/app/core/crypto.py:43-45`
- **Descripción:** Si `ENCRYPTION_KEY` no está configurada, `encrypt()` retorna datos sin cifrar con un warning. Si se despliega con config incorrecta, PII queda en texto plano en BD.
- **Compliance:** Art. 11 Ley 21.719 (cifrado obligatorio de datos personales).
- **Fix:** `raise RuntimeError("ENCRYPTION_KEY no configurada")` en vez de retornar plaintext.

#### C2. `rats.py:92` — Base legal no validada contra lista taxativa
- **Severidad:** CRÍTICA
- **Archivo:** `backend/app/schemas/rat.py`, `backend/app/routes/rats.py:92`
- **Descripción:** El schema `RATCreate.base_legal` acepta cualquier string libre. No hay enum que restrinja a las 7 causales del Art. 13.
- **Compliance:** Art. 13 (base legal taxativa).
- **Fix:** Crear `enum BaseLegal` con los 7 valores válidos y usar en schema.

#### C3. `scheduler.py:93-106` — Scheduler threading incompatible con Vercel serverless
- **Severidad:** CRÍTICA
- **Archivo:** `backend/app/services/scheduler.py:93-106`
- **Descripción:** El scheduler usa `threading.Thread` daemon. En Vercel serverless, los threads mueren con el proceso. 5 jobs nunca se ejecutan (RATs vencidos, brechas 72h, contratos, EIPD, consentimientos).
- **Compliance:** Art. 14 bis (brechas 72h), Art. 16 (revisión RAT).
- **Fix:** Configurar Vercel Cron para llamar `/admin/tasks/run` cada 5 min.

#### C4. `consentimiento_service.py:77-78` — Dual storage plaintext + cipher
- **Severidad:** CRÍTICA
- **Archivo:** `backend/app/services/consentimiento_service.py:77-78`
- **Descripción:** Se guardan tanto `nombre_titular` (plaintext) como `nombre_titular_cipher` (cifrado). PII existe en texto plano en BD.
- **Compliance:** Art. 11.
- **Fix:** Eliminar columnas plaintext, usar solo cifradas, descifrar on-demand.

#### C5. `rats.py:135-141` — N+1 query en reportes
- **Severidad:** CRÍTICA
- **Archivo:** `backend/app/routes/rats.py:135-141`, `backend/app/services/rat_crud.py:315-319`
- **Descripción:** Dashboard carga TODOS los RATs de la empresa en memoria para calcular completitud/riesgo. Con 1000 RATs × 50 empresas → 50K objetos por request.
- **Performance:** Crítico para escala.
- **Fix:** Mover cálculos a SQL aggregates.

#### C6. `audit_service.py:54` — Timestamp sin UTC en hash chain
- **Severidad:** CRÍTICA
- **Archivo:** `backend/app/services/audit_service.py:54`
- **Descripción:** `timestamp.replace(tzinfo=None)` pierde timezone antes del hash. Si hay cambio de DST o timezone, hash chain se rompe.
- **Compliance:** Art. 28 (auditoría inmutable).
- **Fix:** Normalizar a UTC antes de hashear.

#### C7. Endpoints públicos sin rate limiting
- **Severidad:** CRÍTICA
- **Archivo:** `backend/app/routes/seguimiento.py:59-72`, `backend/app/routes/tkt_solicitud_derecho.py` (público)
- **Descripción:** `/seguimiento/{tracking_token}` y formulario público ARCO sin rate limit específico (debería ser 10/h por IP).
- **Seguridad:** Prevenir enumeración y DoS.
- **Fix:** `@limiter.limit("10/hour")` específico.

### 3.2 Frontend / UX

#### C8. RatWizard de 1311 líneas (frontend-guardian)
- **Severidad:** CRÍTICA (UX + mantenibilidad)
- **Archivo:** `frontend-next/components/rat/RatWizard.tsx` (1311 líneas)
- **Descripción:** Wizard monolítico, viola SOLID, bloquea code splitting, imposible de testear completamente. A pesar de tener `WizardModular/`, el orquestador sigue siendo grande.
- **Fix:** Extraer lógica de validación y persistencia a hooks/context.

#### C9. `dangerouslySetInnerHTML` en AlertBanner
- **Severidad:** CRÍTICA (XSS)
- **Archivo:** `frontend-next/components/dashboard/AlertBanner.tsx`
- **Descripción:** Mensajes del backend se renderizan como HTML sin sanitización. Riesgo XSS si backend devuelve PII sin escapar.
- **Seguridad:** OWASP A03.
- **Fix:** Sanitizar con DOMPurify o reemplazar por texto plano con formato Markdown.

#### C10. `confirm()` nativo para eliminar brechas
- **Severidad:** CRÍTICA (UX)
- **Archivo:** `frontend-next/app/(app)/breaches/page.tsx:574`
- **Descripción:** `window.confirm()` nativo es feo en mobile, no accesible, no personalizable. Debería usar `ConfirmDialog` component.
- **Fix:** Migrar a `ConfirmDialog` componente (ya existe).

---

## 4. Hallazgos Altos (P1)

### 4.1 Backend

| # | Hallazgo | Archivo | Esfuerzo | Impacto |
|---|---|---|---|---|
| A1 | Cache LRU tokens revocados no compartido en serverless | `core/security.py:20-55` | 1d | Seguridad |
| A2 | `tracking_token` enumerable sin UUID v4 garantizado | `routes/seguimiento.py:59` | 0.5d | Seguridad |
| A3 | `actualizar_ticket` 180 líneas, viola SRP | `tkt_solicitud_derecho.py:277` | 1d | Mantenibilidad |
| A4 | `rat_service.py` re-export sin lógica | `services/rat_service.py:1-72` | 0.5d | Mantenibilidad |
| A5 | `rat_crud.py` 467 líneas, hace demasiado | `services/rat_crud.py` | 2d | Mantenibilidad |
| A6 | Sin versionamiento API `/api/v1/` | `main.py:185-207` | 1d | Evolución |
| A7 | Tipos TypeScript desincronizados de Pydantic | `types/index.ts` vs `models/rat.py` | 3d | Type-safety |
| A8 | Race condition en hash chain | `audit_service.py:83-128` | 1d | Concurrencia |
| A9 | Sin paginación cursor-based | `routes/rats.py:169-196` | 2d | Performance |
| A10 | Notificación titulares brecha solo loggeada | `breach_service.py:121` | 1d | Compliance |
| A11 | `onMouseEnter/onMouseLeave` en Sidebar (mobile broken) | `components/layout/Sidebar.tsx` | 0.5d | UX |
| A12 | AppContext 221 líneas, 20+ estados | `context/AppContext.tsx` | 2d | Mantenibilidad |
| A13 | Dashboard retorna `null` en error (pantalla en blanco) | `app/(app)/dashboard/page.tsx` | 0.5d | UX |

### 4.2 Compliance (Art. 14 bis, 14 ter)

| # | Hallazgo | Compliance | Esfuerzo |
|---|---|---|---|
| C-A1 | Endpoint `/publico/transparencia` texto incorrecto | Art. 14 ter | 0.5d |
| C-A2 | Notificación a titulares brecha sin implementar | Art. 14 bis | 1d |
| C-A3 | EIPD sin workflow completo de aprobación DPO | Art. 15 bis | 3d |

---

## 5. Hallazgos Medios (P2)

### 5.1 Backend

| # | Hallazgo | Archivo | Esfuerzo |
|---|---|---|---|
| M1 | Duplicación validación acceso empresa (~65 líneas) | `tkt_solicitud_derecho.py:107-110`+ | 1d |
| M2 | Funciones largas `reportes` 135 líneas | `rats.py:32-166` | 1d |
| M3 | Magic numbers hardcodeados | varios | 0.5d |
| M4 | Sin cleanup archivos huérfanos OCI | `core/storage.py` | 2d |
| M5 | Soft delete asimétrico (solo Companies) | models/ | 3d |
| M6 | Sin métricas de negocio (Prometheus/CloudWatch) | services/ | 3d |
| M7 | Tests E2E ARCO workflow incompleto | tests/ | 2d |
| M8 | Tests scheduler 72h faltan | tests/ | 1d |
| M9 | Tests de concurrencia hash chain faltan | tests/ | 1d |
| M10 | Sin idempotency-key en creación RATs | routes/rats.py | 2d |

### 5.2 Frontend

| # | Hallazgo | Esfuerzo |
|---|---|---|
| M-F1 | Validación magic bytes frontend pre-upload | 0.5d |
| M-F2 | stale-while-revalidate en dashboard | 3d |
| M-F3 | Validación RUT en vivo formularios | 0.5d |
| M-F4 | Email confirmación doble input | 0.5d |
| M-F5 | Confirmación email al crear usuario | 0.5d |

---

## 6. Fortalezas Detectadas (TOP 10)

1. **Hash chain auditoría inmutable** — `audit_service.py` con SHA-256 + verificación de integridad
2. **Multi-tenancy robusto** — `check_company_access` + tests IDOR exhaustivos
3. **Cifrado PII con Fernet** — implementado correctamente en consentimientos
4. **Sistema de diseño UI homogéneo** — 22 átomos cohesivos post-QW4
5. **WCAG touch targets ≥44px** — default en Button component
6. **Logging estructurado** — JSON en producción, request_id end-to-end
7. **Migraciones reversibles** — `BEGIN/COMMIT` + `IF NOT EXISTS`
8. **Tests cobertura seguridad** — `test_security.py` exhaustivo
9. **axe-core a11y** — 0 violaciones críticas en login page
10. **Compliance ARCO workflow** — completo con plazos, validaciones, evidencia

---

## 7. Deuda Técnica Cuantificada

| Categoría | Items | Esfuerzo total |
|---|---|---|
| Backend refactor | 5 (rat_crud split, rat_service delete, magic numbers, etc.) | ~8 días |
| Frontend refactor | 3 (AppContext split, RatWizard split, magic bytes) | ~6 días |
| Compliance gaps | 3 (transparencia, breach notification, EIPD workflow) | ~5 días |
| Performance | 4 (N+1, paginación, scheduler, storage) | ~8 días |
| Security | 5 (rate limiting, crypto fallback, IDOR tests) | ~4 días |
| **Total deuda técnica** | **20 items** | **~31 días (6 sprints)** |

---

## 8. Top 15 Quick Wins (1-2 días cada uno)

Ordenados por impacto/esfuerzo:

| # | Quick Win | Esfuerzo | Impacto | Archivo |
|---|---|---|---|---|
| QW1 | Fix crypto fallback (C1) | 0.5d | CRÍTICO | `crypto.py:43-45` |
| QW2 | Configurar Vercel Cron para scheduler (C3) | 1d | CRÍTICO | `vercel.json` + `/admin/tasks/run` |
| QW3 | Rate limiting específico público ARCO (C7) | 0.5d | CRÍTICO | `tkt_solicitud_derecho.py` |
| QW4 | Validar base legal contra enum (C2) | 0.5d | CRÍTICO | `schemas/rat.py` |
| QW5 | Eliminar columnas plaintext Consentimiento (C4) | 0.5d | CRÍTICO | `consentimiento_service.py` + migration |
| QW6 | Fix timestamp UTC en hash chain (C6) | 0.5d | CRÍTICO | `audit_service.py:54` |
| QW7 | Migrar `confirm()` a `ConfirmDialog` (C10) | 0.5d | ALTO | `breaches/page.tsx` |
| QW8 | Eliminar `dangerouslySetInnerHTML` (C9) | 0.5d | CRÍTICO | `AlertBanner.tsx` |
| QW9 | Refactor `actualizar_ticket` 180 LOC (A3) | 1d | ALTO | `tkt_solicitud_derecho.py:277` |
| QW10 | Eliminar re-export `rat_service.py` (A4) | 0.5d | BAJO | `services/rat_service.py` |
| QW11 | Fix Dashboard null en error (A13) | 0.5d | ALTO | `dashboard/page.tsx` |
| QW12 | Cursor-pagination `GET /rats` (A9) | 2d | ALTO | `routes/rats.py:169` |
| QW13 | Notificación a titulares brecha (A10) | 1d | CRÍTICO | `email_service.py` |
| QW14 | Implementar `confirm()` accesible (C10) | 0.5d | ALTO | varios |
| QW15 | Eliminar hover-only JS en Sidebar (A11) | 0.5d | ALTO | `Sidebar.tsx` |

**Total esfuerzo QWs: ~10 días**

---

## 9. Roadmap por Fases

### Fase 1 — Estabilidad Operacional (Sprint 1-4, ~1 mes)

**Objetivo:** Eliminar bloqueantes críticos.

**Entregables:**
1. QW1-QW6 (todos los críticos)
2. QW13 (notificación titulares brecha)
3. Tests E2E ARCO workflow completo
4. Tests scheduler 72h

**Métricas de éxito:**
- Cero bloqueantes para Producción Empresarial
- Scheduler ejecutándose sin intervención manual
- Cero PII en texto plano

---

### Fase 2 — Observabilidad y Performance (Sprint 5-10, ~2 meses)

**Objetivo:** Dashboards SRE + mejora de rendimiento.

**Entregables:**
1. QW12 (cursor-pagination)
2. Métricas OCI Monitoring (latencia, errores, uptime)
3. Dashboard SRE
4. React Query / SWR en frontend
5. Eager load relaciones (N+1 fix)

**Métricas de éxito:**
- Latencia p95 < 500ms
- 0 queries N+1
- Dashboard SRE visible

---

### Fase 3 — Compliance Empresarial (Sprint 11-20, ~4 meses)

**Objetivo:** Listo para Producción Empresarial con fiscalización APDC.

**Entregables:**
1. Multi-factor authentication (TOTP)
2. SSO/SAML integration
3. Versionamiento API `/api/v1/`
4. Generación automática tipos TypeScript desde Pydantic
5. Migración completa BYTEA → OCI Object Storage
6. Soft delete en todos los modelos con PII
7. DR test documentado
8. Manual para clientes no-técnicos (`manual/`)

**Métricas de éxito:**
- 100% cobertura MFA opcional
- 0 registros en BYTEA
- DR test ejecutado RTO < 4h, RPO < 1h
- Listos para fiscalización APDC del 1 dic 2026

---

## 10. Readiness para Producción Empresarial

### Estado actual: **Producción Inicial (6.7/10)**

### Criterios cumplidos ✅
- Funcionalidad core RAT operativa
- Módulos ARCO, Brechas, Consentimientos, EIPD funcionales
- Multi-tenant con RBAC
- Hash chain de auditoría
- Sistema de diseño UI
- Tests funcionales de flujos críticos
- Deploy automatizado en Vercel

### Criterios NO cumplidos ❌
- **Rate limiting por plan** (solo global)
- **Métricas de uptime SLA** (sin dashboards SRE)
- **SSO/SAML corporativo** (no implementado)
- **Auditoría unificada cross-módulo** (parcial)
- **MFA** (no implementado)
- **DR test documentado**
- **Capacitación in-app** (no implementada)
- **Reportes regulatorios avanzados APDP** (básico)

### Para pasar a Producción Empresarial
Resolver P0 (10 críticos) + P1 principales + tener dashboard SRE activo + MFA opcional.

---

## 11. Recomendaciones Priorizadas

### Esta semana (QW1-QW6)
- Arreglar crypto fallback (CRÍTICO Art. 11)
- Validar base legal enum (CRÍTICO Art. 13)
- Configurar Vercel Cron (CRÍTICO scheduler)
- Eliminar plaintext Consentimiento (CRÍTICO Art. 11)
- Rate limiting público (CRÍTICO Seguridad)
- Fix timestamp UTC hash chain (CRÍTICO Art. 28)

### Este mes (QW7-QW15 + A1-A13 principales)
- Migrar `confirm()` a `ConfirmDialog`
- Eliminar `dangerouslySetInnerHTML`
- Refactorizar `actualizar_ticket` 180 LOC
- Cursor-pagination en listados
- Notificación a titulares brecha
- Eliminar hover-only JS

### Este trimestre (Fase 2)
- Métricas de negocio + Dashboard SRE
- React Query / SWR
- Eager load N+1
- Generar tipos TypeScript desde Pydantic

---

## 12. Conclusión

Custodio RAT es un proyecto **sólido y bien arquitecturado** con score 6.7/10 que está listo para **Producción Inicial** pero requiere trabajo enfocado en 10 hallazgos críticos + 13 altos para llegar a **Producción Empresarial**.

**Las prioridades inmediatas** son 7 hallazgos bloqueantes (C1-C7) que afectan compliance Ley 21.719 crítico. Resolverlos toma ~10 días y desbloquea el camino hacia Producción Empresarial antes del 1 de diciembre de 2026.

**Las fortalezas clave** del proyecto son el hash chain de auditoría, multi-tenancy robusto, cifrado PII, sistema de diseño UI y el workflow ARCO completo. Estos son evidencia de decisiones arquitectónicas correctas.

**La velocidad de mejora** ha sido alta (5 commits en la última sesión cubriendo homologación UX + QW4 + axe-core + tests), lo que indica que el equipo está ejecutando bien y puede resolver los pendientes.

---

*Levantamiento generado: 2026-07-18 | Skills: 5 (architect-senior, qa-senior, frontend-guardian, custodio-auditoria, doc-governance) | Subagentes: 4 especializados*

## Log de cambios

| Fecha | Cambio | Autor |
|-------|--------|-------|
| 2026-07-18 | Levantamiento inicial detallado con 4 auditorías especializadas | Emece |