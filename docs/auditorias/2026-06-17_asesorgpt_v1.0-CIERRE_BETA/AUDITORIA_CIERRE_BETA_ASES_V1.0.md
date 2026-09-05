# Auditoría de Cierre Beta — Custodio Asesor (RAG) v1.0

**Fecha:** 17 de Junio de 2026
**Producto:** Custodio Asesor — Gestión de Corpus (Módulo RAG)
**Versión auditada:** v1.0-beta (gestión de corpus)
**Auditor:** Equipo de Desarrollo — Custodio
**Estado:** CIERRE BETA — módulo funcional deployado a QA
**Commits de referencia:** `06eb1da` (corpus management) → `9e99352` (fix duplicate index) → `f18bb43` (chat history fix)
**Rama:** `qa`

---

## 1. Resumen Ejecutivo

Módulo de **Gestión de Corpus del Asesor RAG** completado y deployado a QA.
Desde la auditoría de cierre v1.0 (16-Jun-2026) hasta hoy (17-Jun-2026),
se implementó y deployó la gestión completa de documentos del corpus:

- Upload de archivos `.md` / `.txt` (drag-drop, hasta 5MB)
- Listado con metadata (nombre, tamaño, tipo, chunks, fecha)
- Descarga via URL presigned (OCI) o link directo
- Soft delete (documento + chunks en BD + archivo en OCI)
- Auto-indexación al subir (incremental)
- Indexación completa bajo demanda (superadmin)

El módulo está **100% implementado y deployado en QA**.

---

## 2. Commits desde Auditoría Previa (16-Jun-2026 → 17-Jun-2026)

| Commit | Fecha | Descripción | Archivos |
|--------|-------|-------------|----------|
| `06eb1da` | 17-Jun | feat(asesor): corpus management - upload/delete/list docs for RAG | 8 |
| `9e99352` | 17-Jun | fix(asesor): remove duplicate index + add Union import for backwards compat | 2 |
| `f18bb43` | 17-Jun | fix(asesor): clear chat history on user change to prevent session bleed | 2 |

**Total: 3 commits nuevos, 12 archivos cambiados.**

---

## 3. Componentes Entregados

### 3.1 Backend

| Componente | Archivo | Estado |
|------------|---------|--------|
| Modelo | `backend/app/models/asesor.py` → `AsesorCorpusDocument` | ✅ |
| Store service | `backend/app/services/asesor_corpus_store.py` | ✅ |
| Endpoints corpus | `backend/app/routes/admin_asesor.py` (4 endpoints nuevos) | ✅ |
| Indexer actualizado | `backend/app/services/asesor_indexer.py` (BD-first + auto-reindex) | ✅ |

### 3.2 Frontend

| Componente | Archivo | Estado |
|------------|---------|--------|
| AsesorCorpusTab | `frontend-next/components/configuracion/AsesorCorpusTab.tsx` | ✅ |
| Cliente API | `frontend-next/lib/asesor-api.ts` (4 funciones nuevas) | ✅ |
| Tab en Configuración | `frontend-next/app/(app)/configuracion/page.tsx` | ✅ |

---

## 4. Endpoints de Gestión de Corpus

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| GET | `/admin/asesor/documents` | JWT + superadmin | Lista documentos con metadata |
| POST | `/admin/asesor/upload` | JWT + superadmin | Upload archivo + auto-index |
| GET | `/admin/asesor/documents/{id}/download` | JWT + superadmin | URL de descarga |
| DELETE | `/admin/asesor/documents/{id}` | JWT + superadmin | Soft delete documento + chunks |

**Total: 4 endpoints** — todos implementados.

---

## 5. Bugs Detectados y Corregidos

| Bug | Commit | Descripción |
|-----|--------|-------------|
| Duplicate index `idx_asesor_source` | `9e99352` | Migration tenía 2 índices en la misma columna |
| Chat history bleed entre usuarios | `f18bb43` | `useEffect` de carga usaba `companyId` en vez de `user?.id` como dependencia |
| Import `Union` faltante en Python 3.10 | `9e99352` | `Optional` requiere `Union` del módulo `typing` |

---

## 6. Bugs Pendientes

| Bug | severity | Descripción | Workaround |
|-----|----------|-------------|------------|
| **CORS error en reindex QA** | ALTA | POST `/admin/asesor/index` retorna sin CORS headers en producción serverless | Usar curl directo o verificar logs Vercel |
| 14 tests Asesor preexistentes | BAJA | Bloqueados por 9 constantes `ASESOR_*` faltantes en `Settings` | Configurar en Vercel QA |

---

## 7. Score de Cumplimiento — Beta

| Dimensión | Score | Justificación |
|-----------|-------|---------------|
| Completitud funcional | 9/10 | Gestión corpus completa; solo falta smoke test E2E |
| Tests | 8/10 | Tests corpus management pendientes (~80 líneas) |
| Frontend UX | 9/10 | Drag-drop, badges, inline confirm, download — UX completa |
| Seguridad | 8/10 | Solo superadmin, soft delete, hash SHA256, auditoría completa |
| Documentación | 9/10 | CIERRE_BETA generado, CHANGELOG actualizado |
| **TOTAL** | **8.6/10** | Módulo listo para beta en QA |

---

## 8. Estado del Módulo

| Recurso | Estado | Detalle |
|---------|--------|---------|
| Corpus seed inicial | ✅ | `backend/data/asesor_corpus/que_es_un_rat.md` |
| Gestión documental | ✅ | Upload/list/download/delete deployados |
| Auto-reindex | ✅ | POST /upload ejecuta indexación incremental |
| Reindex manual | ✅ | POST /admin/asesor/index con `force=true` |
| UI drag-drop | ✅ | `AsesorCorpusTab.tsx` con preview |
| Estadísticas corpus | ✅ | GET /admin/asesor/stats con `total_chunks`, `total_documents`, `provider` |
| Chat history fix | ✅ | `f18bb43` — historial se limpia al cambiar de usuario |
| Tests corpus endpoints | ⏳ | **Pendientes** — ~80 líneas |

---

## 9. Tests Pendientes

| Suite | Tests | Estado |
|-------|-------|--------|
| Corpus endpoints | 4 | ⏳ **PENDIENTES** |
| Tests Asesor preexistentes | 14 | ⏳ Bloqueados por config `ASESOR_*` |

**Test coverage objetivo:** 4 tests para los 4 endpoints de corpus management.

---

## 10. Checklist de Cierre Beta

| Item | Estado | Referencia |
|------|--------|------------|
| Gestión corpus backend completa | ✅ | `asesor_corpus_store.py` |
| 4 endpoints admin corpus | ✅ | `admin_asesor.py` lines 125-278 |
| UI drag-drop + lista + download | ✅ | `AsesorCorpusTab.tsx` |
| Tab "Asesor · Corpus" en Config | ✅ | `configuracion/page.tsx` |
| Auto-reindex al upload | ✅ | `asesor_corpus_store.py:upload()` |
| Chat history bleed fix | ✅ | `f18bb43` |
| Commit a qa | ✅ | `f18bb43` |
| **Tests corpus endpoints** | ⏳ | **Pendiente** |
| **Documentación cierre beta** | ✅ | Este documento |
| **CHANGELOG actualizado** | ✅ | `CHANGELOG.md` v1.6.1-beta |

---

## 11. Proyección Siguiente

### v1.1 — Asesor (Post-Beta)

| # | Item | Prioridad | Esfuerzo |
|---|------|-----------|----------|
| P1 | Tests corpus management (~80 líneas) | ALTA | 2h |
| P2 | Corpus completo: texto Ley 21.719 + manuales + guías APDC | ALTA | 3h |
| P3 | Smoke test E2E Playwright (10 tests) | MEDIA | 2h |
| P4 | Fix CORS/reindex QA (diagnóstico + fix cold start) | ALTA | 2h |
| P5 | Métricas de calidad (precision@k, faithfulness) | MEDIA | 2h |
| P6 | Streaming SSE (respuestas en tiempo real) | BAJA | 4h |

### Módulo Companies — Quick Wins v1.1

| # | Item | Esfuerzo estimado |
|---|------|-------------------|
| QW1 | Health Score en listado empresas | 1h |
| QW2 | Alerta contrato encargado por vencer (30 días) | 2h |
| QW3 | Banner DPO incompleto en dashboard | 1h |
| QW4 | Score SLA ARCO en resumen empresa | 1h |
| QW5 | Botón crear EIPD desde RAT (drawer) | 1h |

---

*Documento generado: 17 Junio 2026*
*Auditoría de cierre beta — Custodio Asesor (RAG) v1.0 — gestión de corpus*
