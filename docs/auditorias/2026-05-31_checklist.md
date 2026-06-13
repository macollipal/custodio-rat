# Checklist Arquitectónico — Custodio RAT Manager

**Fecha:** 2026-05-31
**Última verificación:** [VERIFICAR]
**Estado:** Producción Inicial / Beta

---

> **Nota:** Este documento fue generado el 2026-05-31 y refleja el estado del proyecto en esa fecha. Los items marcados como completados pueden haber cambiado o revertido. Verificar contra el codebase actual antes de usar como referencia.

## 🔴 PRIORIDAD CRÍTICA (Esta semana)

- [x] **FIX: `GET /rats/auditoria/{company_id}` sin authorization** — Cualquier usuario puede leer audit logs de cualquier empresa
- [x] **Paginar `GET /auth/users`** — Devuelve TODOS los usuarios, crashea con 1000+
- [x] **Paginar `GET /companies`** — Sin límite
- [x] **Paginar `GET /brechas`** — Sin límite
- [x] **Paginar `GET /solicitudes-derecho`** — Sin límite

---

## 🟠 PRIORIDAD ALTA (2 semanas)

- [x] **Unificar `calcular_completitud`** — Comentario en `_calcular_estado` referencia modelo
- [x] **Audit logging en `POST /ai/ask`** — log_audit con question truncada, provider, ip
- [x] **Fix `require_editor_or_admin_empresa` y `require_company_admin`** — Documentación corregida
- [x] **Retry logic en database.py** — Pool QueuePool, pool_recycle, on_connect sanea Neon
- [ ] **Validar RUT en backend** — Postergado por usuario
- [ ] **Index en `audit_logs(usuario, timestamp)`** — Pendiente (requiere migrate)
- [ ] **Mover `archivo_base_legal_datos` a object storage** — Pendiente (futuro)
- [ ] **Eliminar columna `is_admin` legacy** — Pendiente (futuro, bajo impacto)

---

## 🟡 PRIORIDAD MEDIA (1 mes)

- [ ] **Reemplazar `fetch()` por `api.*`** — configuracion, conexion, ejercitar
- [ ] **Splitear componentes >300 líneas:**
  - RatWizard (873) → 4 step components + WizardProgress
  - reportes (866) → AIChat, Filters, Table, ColumnPicker
  - configuracion (861) → 4 archivos de tab
  - companies (717) → CompanyForm, UserAccessPanel, modales
  - RatEditForm (445) → mismo split
  - RatTable (450) → Row, ExpandedRow, Filters
- [ ] **Rate limiting extendido** — Agregar a POST /companies, /rats, /brechas
- [ ] **Externalizar `TIPOS_PROCESO` y `ALERTAS_AUDITORIA`** — Editables por admin, no en código
- [ ] **Fix timezone inconsistency** — export_service UTC-4 vs get_dashboard_stats UTC
- [x] **Retry logic en database.py** — Para conexiones transitorias Neon
- [ ] **Validar email en backend** — Formato email_dpo en Company schema

---

## 🟢 PRIORIDAD BAJA (2-3 meses)

- [ ] **Remover token de localStorage** — Solo httpOnly cookie (elimina XSS)
- [ ] **Refresh tokens JWT** — 8h sin refresh es malo para UX
- [ ] **Cache para `decode_access_token`** — Blacklist check en BD por request, cachear TTL 30s
- [ ] **Tests E2E** — Login → empresa → RAT → exportar PDF (Playwright)
- [ ] **Unificar `DESCRIPCIONES_BASE`** — constants.ts y RatWizard.tsx duplicado
- [ ] **CompanySwitcher extraído** — Sidebar y Topbar duplicados
- [ ] **Observabilidad** — Correlation ID en logs, métricas, alertas

---

## 🔒 CHECKLIST SEGURIDAD

- [ ] **XSS en AlertBanner** — dangerouslySetInnerHTML con datos propios ok, vigilar user-generated
- [ ] **CAPTCHA en ejercitar/page** — Formulario público sin protección bots
- [ ] **CSRF protection** — Cookies sin CSRF token
- [ ] **HSTS header** — Para enforce HTTPS
- [ ] **Undo delete no persiste password** — Backend rechaza o genera temporal

---

## 📊 RESUMEN

| Prioridad | Items | Esfuerzo |
|-----------|-------|----------|
| 🔴 Crítica | 5 | 2-3 días |
| 🟠 Alta | 7 | 3-5 días |
| 🟡 Media | 10 | 2-3 sem |
| 🟢 Baja | 8 | 2-4 sem |
| 🔒 Seguridad | 5 | 1-2 sem |

**Total: 35 items | ~7-9 semanas**

---

*Basado en opinion_Arq_2026-05-31.md — 2026-05-31*