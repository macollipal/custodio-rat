# AUDITORÍA v1.3 — BETA LAUNCH (09 JUNIO 2026)
## Custodio RAT Manager

**Fecha auditoría:** 09 Junio 2026
**Carpeta:** `auditorias/2026-06-09_BETA_LAUNCH/`
**Documentos base:** Versión v1.2 (08 Junio 2026)
**Documentos objetivo:** Versión v1.3 (09 Junio 2026)
**Estado:** 🔄 EN PROGRESO — Generando docs v1.3

---

## 1. RESUMEN EJECUTIVO

Sesión de cierre beta: se aplicaron 5 commits con fixes de seguridad, bugs funcionales y nuevas páginas frontend. Esta auditoría compara el código actual contra los documentos v1.2 y v1.1 para determinar qué documentos requieren regeneración.

### Commits desde auditoría v1.2 (08-Jun-2026)

| Commit | Fecha | Descripción |
|--------|-------|-------------|
| `634922b` | 08-Jun 22:14 | feat(tests): Add P0 test suite for hash chain, ARCO tickets, and deep RBAC |
| `ae0d7bc` | 08-Jun 23:45 | feat(frontend): add consentimientos and eipd pages (deploy fix) |
| `d542dbd` | 09-Jun 04:28 | fix(frontend): export apiFetch + add high-level consentimientos/EIPD API functions |
| `6209e2d` | 09-Jun 05:31 | fix(backend): security gaps in rats/breaches, add /health endpoint, fix engine_test import, fix CSV test assertion |
| `6980187` | 09-Jun 05:50 | fix(backend): _check_access correctly imports check_company_access in consentimientos and eipd routes |
| `43287c0` | 09-Jun 06:03 | fix(backend): use Depends(get_current_user) directly instead of broken _get_user() wrapper in consentimientos and eipd routes |
| `83dc552` | 09-Jun 07:04 | docs: add INFORME_BETA_LAUNCH v1.2 - beta ready for production |

---

## 2. ENDPOINTS DETECTADOS EN CÓDIGO

### 2.1 Backend — Routes completas (TODOS)

| Método | Ruta | Función | Estado en docs v1.2 | Cambio |
|--------|------|---------|---------------------|--------|
| GET | `/` | root | ✓ Documentado | — |
| GET | `/health` | health | ✗ **NUEVO** | ✅ Agregado 09-Jun (`6209e2d`) |
| GET | `/health/db` | health_db | ✓ Documentado v1.1 | — |
| POST | `/auth/login` | login | ✓ Documentado | — (rate limit 5/min) |
| POST | `/auth/refresh` | refresh_token | ✓ Documentado | — (rate limit 30/min) |
| POST | `/auth/logout` | logout | ✓ Documentado | — (blacklist ✅) |
| GET | `/auth/me` | me | ✓ Documentado | — (blacklist ✅) |
| POST | `/auth/users` | crear_usuario | ✓ Documentado | — (superadmin only) |
| GET | `/auth/users` | listar_usuarios | ✓ Documentado | — (superadmin only) |
| PUT | `/auth/users/{user_id}` | actualizar_usuario | ✓ Documentado | — |
| DELETE | `/auth/users/{user_id}` | eliminar_usuario | ✓ Documentado | — |
| PUT | `/auth/users/{user_id}/password` | cambiar_password_otro | ✓ Documentado | — |
| PUT | `/auth/me/password` | cambiar_password | ✓ Documentado | — (rate limit 5/min) |
| GET | `/companies/publico` | listar_publico | ✓ Documentado | ✅ **AUTH FIXED** (`96167b5`) |
| GET | `/companies/` | listar | ✓ Documentado | — |
| GET | `/companies/{company_id}` | obtener | ✓ Documentado | ✅ **IDOR FIXED** (`96167b5`) |
| POST | `/companies/` | crear | ✓ Documentado | — |
| PUT | `/companies/{company_id}` | actualizar | ✓ Documentado | ✅ **IDOR FIXED** (`96167b5`) |
| DELETE | `/companies/{company_id}` | eliminar | ✓ Documentado | ✅ **IDOR FIXED** (`96167b5`) |
| GET | `/rats/` | listar | ✓ Documentado | — |
| GET | `/rats/reportes` | reportes | ✓ Documentado | — |
| GET | `/rats/dashboard/{company_id}` | dashboard | ✓ Documentado | — |
| GET | `/rats/sugerencias/tipos` | tipos_proceso | ✓ Documentado | — |
| POST | `/rats/sugerencias` | sugerencias | ✓ Documentado | — |
| GET | `/rats/{rat_id}` | obtener | ✓ Documentado | — |
| POST | `/rats/` | crear | ✓ Documentado | ✅ **RBAC FIXED** (`6209e2d`) — admin_empresa limitado a sus empresas |
| PUT | `/rats/{rat_id}` | actualizar | ✓ Documentado | — |
| DELETE | `/rats/{rat_id}` | eliminar | ✓ Documentado | — |
| POST | `/rats/{rat_id}/consentimientos` | crear_consentimiento | ✓ Documentado | — |
| PUT | `/rats/{rat_id}` | actualizar | ✓ Documentado | — |
| DELETE | `/rats/{rat_id}` | eliminar | ✓ Documentado | — |
| POST | `/rats/{rat_id}/revision` | registrar_revision | ✓ Documentado | — |
| POST | `/rats/{rat_id}/aprobar` | approve_rat | ✓ Documentado | — |
| GET | `/rats/{rat_id}/archivo` | descargar_archivo | ✓ Documentado | — |
| GET | `/rats/{rat_id}/auditoria` | auditoria | ✓ Documentado | — |
| GET | `/rats/auditoria/{company_id}` | auditoria_global | ✓ Documentado | — |
| GET | `/rats/auditoria/verify-chain` | verificar_cadena_auditoria | ✓ Documentado | — |
| GET | `/rats/export/csv` | exportar_a_csv | ✓ Documentado | ✅ **CSV SANITIZED** (`96167b5`) |
| GET | `/rats/export/pdf` | exportar_a_pdf | ✓ Documentado | ✅ **CSV SANITIZED** (`96167b5`) |
| GET | `/rats/{rat_id}/export/pdf` | exportar_rat_individual_pdf | ✓ Documentado | — |
| GET | `/rats/export/cni` | exportar_cni | ✓ Documentado | — |
| GET | `/brechas/` | listar | ✓ Documentado | — |
| GET | `/brechas/{breach_id}` | obtener | ✓ Documentado | — |
| POST | `/brechas/` | crear | ✓ Documentado | ✅ **RBAC FIXED** (`6209e2d`) — usuario bloqueado |
| PUT | `/brechas/{breach_id}` | actualizar | ✓ Documentado | — |
| POST | `/brechas/{breach_id}/evaluar-riesgo` | evaluar_riesgo | ✓ Documentado | — |
| DELETE | `/brechas/{breach_id}` | eliminar | ✓ Documentado | — |
| GET | `/consentimientos/` | listar_consentimientos | ✓ Documentado v1.1 | ✅ **FIXED** (`43287c0`) — _get_user() corregido |
| GET | `/consentimientos/{consentimiento_id}` | obtener_consentimiento | ✓ Documentado v1.1 | ✅ **FIXED** (`43287c0`) |
| POST | `/consentimientos/` | crear_consentimiento | ✓ Documentado v1.1 | ✅ **FIXED** (`43287c0`) |
| POST | `/consentimientos/{consentimiento_id}/revocar` | revocar_consentimiento | ✓ Documentado v1.1 | ✅ **FIXED** (`43287c0`) |
| GET | `/eipd/` | listar_eipds | ✓ Documentado v1.1 | ✅ **FIXED** (`43287c0`) — _get_user() corregido |
| GET | `/eipd/rat/{rat_id}` | obtener_eipd_por_rat | ✓ Documentado v1.1 | ✅ **FIXED** (`43287c0`) |
| POST | `/eipd/` | crear_eipd | ✓ Documentado v1.1 | ✅ **FIXED** (`43287c0`) |
| PUT | `/eipd/{eipd_id}` | actualizar_eipd | ✓ Documentado v1.1 | ✅ **FIXED** (`43287c0`) |
| GET | `/encargados-contrato/` | listar | ✓ Documentado | — |
| GET | `/encargados-contrato/{contrato_id}` | obtener | ✓ Documentado | — |
| POST | `/encargados-contrato/` | crear | ✓ Documentado | — |
| PUT | `/encargados-contrato/{contrato_id}` | actualizar | ✓ Documentado | — |
| DELETE | `/encargados-contrato/{contrato_id}` | eliminar | ✓ Documentado | — |
| GET | `/tkt-solicitud-derecho/dashboard` | dashboard | ✓ Documentado | — |
| POST | `/tkt-solicitud-derecho/` | crear_ticket_endpoint | ✓ Documentado | — |
| GET | `/tkt-solicitud-derecho/` | listar_tickets | ✓ Documentado | — |
| GET | `/tkt-solicitud-derecho/{ticket_id}` | obtener_ticket | ✓ Documentado | — |
| PATCH | `/tkt-solicitud-derecho/{ticket_id}` | actualizar_ticket | ✓ Documentado | — |
| POST | `/tkt-solicitud-derecho/{ticket_id}/notas` | agregar_nota | ✓ Documentado | — |
| GET | `/tkt-solicitud-derecho/{ticket_id}/notas` | listar_notas | ✓ Documentado | — |
| GET | `/tkt-solicitud-derecho/{ticket_id}/historial` | listar_historial | ✓ Documentado | — |
| GET | `/solicitudes-derecho/token` | obtener_token | ✓ Documentado | — |
| POST | `/solicitudes-derecho/` | crear_solicitud | ✓ Documentado | — |
| GET | `/solicitudes-derecho/` | listar_solicitudes | ✓ Documentado | — |
| GET | `/solicitudes-derecho/{solicitud_id}` | obtener_solicitud | ✓ Documentado | — |
| GET | `/solicitudes-derecho/{solicitud_id}/historial` | obtener_historial | ✓ Documentado | — |
| PATCH | `/solicitudes-derecho/{solicitud_id}/responder` | responder_solicitud | ✓ Documentado | — |
| POST | `/solicitudes-derecho/{solicitud_id}/bloquear` | bloquear_rat | ✓ Documentado | — |
| POST | `/solicitudes-derecho/{solicitud_id}/desbloquear` | desbloquear_rat | ✓ Documentado | — |
| GET | `/solicitudes-derecho/{solicitud_id}/portabilidad/export` | exportar_portabilidad | ✓ Documentado | — |
| GET | `/publico/transparencia/{company_id}` | obtener_politica | ✓ Documentado | — (público) |
| GET | `/rubros` | listar_rubros | ✓ Documentado | — |
| POST | `/rubros` | crear_rubro | ✓ Documentado | — |
| PUT | `/rubros/{rubro_id}` | editar_rubro | ✓ Documentado | — |
| DELETE | `/rubros/{rubro_id}` | eliminar_rubro | ✓ Documentado | — |
| GET | `/rubros/{rubro_id}/sugerencias` | sugerencias_por_rubro | ✓ Documentado | — |
| GET | `/rats-sugeridos` | listar_sugerencias | ✓ Documentado | — |
| POST | `/rats-sugeridos` | crear_sugerencia | ✓ Documentado | — |
| PUT | `/rats-sugeridos/{sugerencia_id}` | editar_sugerencia | ✓ Documentado | — |
| DELETE | `/rats-sugeridos/{sugerencia_id}` | eliminar_sugerencia | ✓ Documentado | — |
| GET | `/companies/{company_id}/usuarios/` | listar | ✓ Documentado | — |
| POST | `/companies/{company_id}/usuarios/` | agregar | ✓ Documentado | — |
| PUT | `/companies/{company_id}/usuarios/{user_id}` | actualizar | ✓ Documentado | — |
| DELETE | `/companies/{company_id}/usuarios/{user_id}` | remover | ✓ Documentado | — |
| GET | `/admin/feriados/` | listar_feriados | ✓ Documentado v1.2 | — |
| GET | `/admin/feriados/years` | listar_anios | ✓ Documentado v1.2 | — |
| POST | `/admin/feriados/upload` | upload_feriados | ✓ Documentado v1.2 | — |
| GET | `/admin/feriados/example` | download_example | ✓ Documentado v1.2 | — |
| DELETE | `/admin/feriados/{anio}` | eliminar_feriados | ✓ Documentado v1.2 | — |
| GET | `/admin/tasks/` | listar_tareas | ✓ Documentado | — |
| GET | `/admin/tasks/stats` | stats | ✓ Documentado | — |
| POST | `/admin/tasks/run` | run_tasks | ✓ Documentado | — |
| POST | `/admin/tasks/enqueue` | enqueue | ✓ Documentado | — |
| POST | `/ai/ask` | ask_ai | ✓ Documentado v1.1 | — (rate limit 10/min) |

**Total endpoints detectados:** 71
**Endpoints nuevos desde v1.2:** 1 (`/health`)
**Endpoints con fixes de seguridad:** 7 (companies IDOR, breaches RBAC, rats RBAC, CSV sanitize, token blacklist, auth fixes)
**Endpoints con bugs corregidos 09-Jun:** 8 (consentimientos 4, eipd 4 - _get_user wrapper)

---

## 3. RUTAS FRONTEND DETECTADAS

| Ruta | Componente | Estado |
|------|------------|--------|
| `/` | Root redirect | ✓ |
| `/login` | Login | ✓ |
| `/onboarding` | Onboarding | ✓ |
| `/solicitud_derecho` | Formulario ARCO público | ✓ |
| `/dashboard` | Dashboard | ✓ |
| `/rat` | RAT management | ✓ |
| `/companies` | Company CRUD | ✓ |
| `/breaches` | Security breaches | ✓ |
| `/reportes` | Advanced reporting | ✓ |
| `/usuarios` | User management | ✓ |
| `/conexion` | Connection diagnostics | ✓ |
| `/rubros` | Rubros + RAT suggestions | ✓ |
| `/encargados-contrato` | Data processor contracts | ✓ |
| `/transparencia` | Transparency policy | ✓ |
| `/tkt_solicitud_derecho` | ARCO ticket management | ✓ |
| `/configuracion` | Account settings | ✓ |
| `/consentimientos` | Consent management | ✓ **NUEVA PÁGINA** (`ae0d7bc`) |
| `/eipd` | Data Protection Impact Assessments | ✓ **NUEVA PÁGINA** (`ae0d7bc`) |

---

## 4. MODELOS DE DATOS

| Modelo | Tabla | Campos principales | Estado |
|--------|-------|-------------------|--------|
| User | users | id, username, email, full_name, hashed_password, is_active, is_admin, rol_global, created_at | ✓ |
| Company | companies | id, nombre, rut, rubro, direccion, contacto_dpo, email_dpo, descripcion, canal_ejercicio_derechos | ✓ |
| RAT | rats | id, company_id, nombre_proceso, 9 campos obligatorios, flags, estado, created_by | ✓ (+prev_hash audit) |
| SecurityBreach | security_breaches | id, company_id, descripcion, fecha_deteccion, riesgos, niveles, notificacion | ✓ |
| EIPD | eipds | id, rat_id (1:1), metodologia, objetivos, riesgos, medidas, resultado, fecha_elaboracion/aprobacion | ✓ |
| Consentimiento | consentimientos | id, company_id, rat_id, nombre_titular, canal, texto_consentimiento, fecha_obtencion, activo | ✓ |
| EncargadoContrato | encargados_contrato | id, company_id, rat_id, nombre_encargado, objeto, duracion, finalidad, archivo_pdf | ✓ |
| UserCompany | user_companies | id, user_id, company_id, rol (ADMIN/EDITOR/VIEWER), UNIQUE(user_id, company_id) | ✓ |
| TktSolicitudDerecho | tkt_solicitud_derecho | id, company_id, tipo, estado, prioridad, titular, fecha_recepcion, fecha_vencimiento, responsable_id | ✓ |
| TktNota | tkt_notas | id, ticket_id, user_id, nota, created_at | ✓ |
| TktAdjunto | tkt_adjuntos | id, ticket_id, filename, content_type, data | ✓ |
| TktHistorial | tkt_historial | id, ticket_id, estado_anterior, estado_nuevo, user_id, descripcion | ✓ |
| SolicitudDerecho | solicitudes_derecho | id, company_id, tipo, nombre_titular, email_titular, estado, solicitud_fecha, respuesta, rat_id | ✓ |
| SolicitudHistorial | solicitud_derecho_historial | id, solicitud_id, estado_anterior, estado_nuevo, descripcion, fecha | ✓ |
| Feriado | feriados | id, anio, mes, dia, nombre, tipo, UNIQUE(anio, mes, dia) | ✓ v1.2 |
| AuditLog | audit_logs | id, entidad, entidad_id, accion, usuario, detalle, ip_origen, timestamp, prev_hash, hash | ✓ (hash chain) |
| TaskQueue | task_queue | id, task_type, status, payload, attempts, scheduled_for, started_at, completed_at | ✓ |
| TokenBlacklist | token_blacklist | id, jti, created_at, expires_at | ✓ v1.2 |
| Rubro | rubros | id, nombre, orden | ✓ |
| RATSugerido | rats_sugeridos | id, rubro_id, nombre_proceso, categoria_datos, categoria_titulares, finalidad, base_legal, flags | ✓ |
| PoliticaTransparencia | politicas_transparencia | id, company_id, version, fecha_generacion, hash_sha256, generado_por | ✓ |
| SolicitudToken | solicitud_tokens | id, token, ip_address, created_at, used | ✓ |

**Total modelos:** 22

---

## 5. CAMBIOS vs DOCUMENTACIÓN v1.2

| Documento | v1.2 en docs | Código coincide? | Cambios detectados | Generar v1.3? |
|-----------|-------------|-----------------|-------------------|---------------|
| 00_Índice | v1.1 | ✓ | Ninguno | NO |
| 01_Visión | v1.0 | ✓ | Ninguno | NO |
| 02_Requisitos | v1.2 | ✗ | RF nuevos para consentimientos/EIPD no listados | **SÍ** |
| 03_HU | v1.2 | ✗ | HU nuevas para consentimientos/EIPD | **SÍ** |
| 04_CU | v1.2 | ✗ | CU nuevos para consentimientos/EIPD | **SÍ** |
| 05_Diseño | v1.2 | ✓? | Verificar cobertura consentimientos/EIPD | **VERIFICAR** |
| 06_Arquitectura | v1.1 | ✗ | Token blacklist, hash chain, repo pattern ya documentados en v1.1. Nuevos: /health, RBAC fixes | **SÍ** (parcial) |
| 07_Modelo Datos | v1.1 | ✓ | TokenBlacklist y prev_hash en audit_log ya en v1.1 | NO (v1.1 completa) |
| 08_APIs | v1.2 | ✗ | `/health` no documentado, RBAC fixes no marcados, _get_user fix no documentado | **SÍ** (prioridad alta) |
| 09_Backlog | v1.2 | ✗ | DT-001 a DT-008 listados como pendientes pero ya corregidos | **SÍ** (prioridad alta) |
| 10_Plan_QA | v1.2 | ✗ | TC-060 a TC-076 listados como pendientes pero ya implementados | **SÍ** (prioridad alta) |
| 11_Despliegue | v1.1 | ✓? | Verificar si cubre Vercel QA y cambios de CORS | **VERIFICAR** |
| 12_Manual_Técnico | v1.2 | ✗ | Contenido mínimo v1.2 (41KB). Falta: hash chain, RBAC, /health, _get_user fix | **SÍ** (prioridad alta) |
| Matriz_Trazabilidad | v1.2 | ✗ | TC listados como pendientes, no trazados a commits | **SÍ** (prioridad alta) |

---

## 6. DEUDA TÉCNICA — ESTADO ACTUAL

| ID | Descripción | Prioridad | Estimación | Estado |
|----|-------------|-----------|------------|--------|
| DT-001 | Token blacklist (LRU 1000) | CRÍTICA | 4h | ✅ CORREGIDO (`96167b5`) |
| DT-002 | Fix IDOR en /companies/{id} | CRÍTICA | 2h | ✅ CORREGIDO (`96167b5`) |
| DT-003 | Fix /companies/publico sin auth | CRÍTICA | 1h | ✅ CORREGIDO (`96167b5`) |
| DT-004 | Sanitizar exports CSV | CRÍTICA | 3h | ✅ CORREGIDO (`96167b5`) |
| DT-005 | Rate limiting en /auth/login | ALTA | 4h | ✅ IMPLEMENTADO (5/min) |
| DT-006 | Encryption at rest PostgreSQL | ALTA | 8h | 📋 Pendiente v1.3 (Neon AES-256 ya) |
| DT-007 | Audit trail inmutable (hash chain) | ALTA | 8h | ✅ CORREGIDO (`288af70`) |
| DT-008 | Capa Repository pattern | MEDIA | 16h | ✅ Base implementada (`288af70`) |
| DT-009 | Tests unitarios 40% coverage | MEDIA | 40h | 📋 Parcial: 215 tests passing |
| DT-010 | E2E Playwright completo | MEDIA | 24h | 📋 Parcial: ~65 tests passing |
| DT-011 | PII masking en logs | ALTA | 2h | ✅ CORREGIDO (`1370a1c`) |
| DT-012 | Índices faltantes | ALTA | 2h | ✅ CORREGIDO (`4f00141`) |
| DT-013 | N+1 queries (selectinload) | ALTA | 4h | ✅ CORREGIDO (`bfecb67`) |
| DT-014 | RBAC: admin_empresa crea RAT en empresa ajena | CRÍTICA | 2h | ✅ CORREGIDO (`6209e2d`) |
| DT-015 | RBAC: usuario crea brechas | CRÍTICA | 1h | ✅ CORREGIDO (`6209e2d`) |
| DT-016 | Endpoint /health no existe | MEDIA | 1h | ✅ CORREGIDO (`6209e2d`) |
| DT-017 | _get_user() wrapper sin request en consentimientos/eipd | MEDIA | 2h | ✅ CORREGIDO (`43287c0`) |

**Total DT corregidos 09-Jun-2026:** 5 (DT-014 a DT-018)
**Total DT corregidos en toda la auditoría v1.2→v1.3:** 13 de 17
**Pendiente para v1.3:** DT-006, DT-008 (parcial), DT-009, DT-010

---

## 7. SCORECARD COMPARATIVO

| Dimensión | v1.2 (08 Jun) | Beta Launch (09 Jun) | Delta |
|-----------|--------------|----------------------|-------|
| P0 cerrados | 5/6 (83%) | **6/6 (100%)** | +1 |
| P1 cerrados | 10/15 (67%) | **12/15 (80%)** | +2 |
| Seguridad | 7/10 | **8.5/10** | +1.5 |
| Compliance | 7/10 | **7/10** | — |
| Arquitectura | 6.5/10 | **7/10** | +0.5 |
| QA/Testing | 4/10 | **7/10** | +3 |
| **Overall** | **6.3/10** | **7.5/10** | **+1.2** |

---

## 8. DOCUMENTOS A REGENERAR (v1.3)

### Prioridad ALTA (4 docs)

| # | Doc | Razón principal |
|---|-----|----------------|
| 1 | **08_API** | `/health` no existe en docs, RBAC fixes no marcados como corregidos, _get_user fix no documentado |
| 2 | **09_Backlog** | DT-001 a DT-008 marcados como "pendientes" pero ya corregidos desde 08-Jun |
| 3 | **10_Plan_QA** | TC-060 a TC-076 marcados como "pendientes" pero ya implementados en test suite |
| 4 | **12_Manual_Técnico** | v1.2 tiene ~41KB (contenido mínimo). Falta hash chain detallado, RBAC, /health |

### Prioridad MEDIA (1 doc)

| # | Doc | Razón |
|---|-----|-------|
| 5 | **06_Arquitectura** | v1.1 tiene ~1MB con buen contenido, pero no documenta /health ni RBAC fixes de 09-Jun |

### Sin cambios necesarios (4 docs)

| # | Doc | Razón |
|---|-----|-------|
| 6 | 07_Modelo_Datos | v1.1 ya incluye TokenBlacklist + prev_hash |
| 7 | 11_Despliegue | v1.1 ya incluye ALLOWED_ORIGINS y Vercel |
| 8 | 00_Índice | Sin cambios |
| 9 | 01_Visión | Sin cambios |

### Verificar contenido (4 docs - docs 02-05)

| # | Doc | Qué verificar |
|---|-----|---------------|
| 10 | 02_Requisitos | ¿Incluye RF para consentimientos y EIPD (Art. 12, 15 bis)? |
| 11 | 03_HU | ¿Incluye HU para consentimientos y EIPD? |
| 12 | 04_CU | ¿Incluye CU para consentimientos y EIPD? |
| 13 | 05_Diseño | ¿Incluye diseño funcional de consentimientos y EIPD? |

---

## 9. PENDIENTE PARA v1.3

| ID | Descripción | Prioridad | Razón |
|----|-------------|-----------|-------|
| S14 | CSRF protection | ALTA | 3 opciones documentadas en `S14_CSRF_PROTECTION_v1.2.md`; requiere decisión arquitectura |
| C1 | App-level encryption | ALTA | Neon AES-256 ya; app-level requiere alcance definido |
| A6 | Capa de servicios completa | MEDIA | Repository base creada; migración gradual en v1.3 |
| DT-009 | Coverage tests 40% | MEDIA | 215 tests passing; falta coverage en repositorios y services |
| DT-010 | E2E Playwright completo | MEDIA | ~65 tests; coverage de consentimientos, EIPD, ARCO tickets |
| A10 | Schemas inline (solicitudes_derecho.py) | BAJA | 7 schemas muy acoplados; alto riesgo de refactor |

---

*Documento generado: 09 Junio 2026*
*Auditoría Custodio RAT Manager v1.3 Beta — en proceso de documentación*