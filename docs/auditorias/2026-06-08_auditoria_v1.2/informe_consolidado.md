# INFORME CONSOLIDADO — AUDITORÍA v1.2 (POST-FIXES)
## Custodio RAT Manager

**Fecha:** 08 Junio 2026
**Auditoría:** v1.2
**Especialistas:** Arquitecto Senior, QA Lead, Compliance Ley 21.719
**Puntuaciones post-fixes:** Arquitectura 6.5/10 | Seguridad 7/10 | QA 4/10 | Compliance 7/10
**Estado:** ✅ AUDITORÍA COMPLETADA

---

## 1. RESUMEN EJECUTIVO

Auditoría completa del codebase Custodio RAT Manager realizada por 3 especialistas en paralelo. Se identificaron **63+ hallazgos** distribuidos en seguridad, arquitectura, testing, compliance legal y funcionalidad.

**Resultado:** Todos los hallazgos P0 (críticos) fueron corregidos durante la sesión. La deuda técnica pendiente para v1.3 es de 3 items principales.

---

## 2. HALLAZGOS CORREGIDOS DURANTE LA SESIÓN

### 2.1 P0 — Críticos ✅

| # | Hallazgo | commit | Estado |
|---|----------|--------|--------|
| S1 | Token blacklist no consultado — tokens revocados siguen activos | `96167b5` | ✅ CORREGIDO |
| S2 | IDOR en `/companies/{id}` — acceso a datos de otra empresa | `96167b5` | ✅ CORREGIDO |
| S3 | `/companies/publico` accesible sin autenticación | `96167b5` | ✅ CORREGIDO |
| S4 | CSV injection en exports — fórmulas no sanitizadas | `96167b5` | ✅ CORREGIDO |
| C6 | Registro de accesos no inmutable — sin hash chain | `288af70` | ✅ CORREGIDO |

### 2.2 P1 — Altos ✅

| # | Hallazgo | commit | Estado |
|---|----------|--------|--------|
| A8 | Índices faltantes en consultas frecuentes | `4f00141` | ✅ CORREGIDO |
| C2 | Logging contiene PII sin mask | `1370a1c` | ✅ CORREGIDO |
| A15 | N+1 queries en listados (rats, breaches) | `bfecb67` | ✅ CORREGIDO |
| A5 | Sin patrón Repository — lógica acoplada | `288af70` | ✅ CORREGIDO (base) |
| S9 | Falta rate limiting en `/auth/login` | — | ✅ Ya implementado (5/min) |
| S11 | Tokens JWT con expiry 24h demasiado largo | — | ✅ Ya implementado (8h) |
| S12 | Sin password hashing con salt | — | ✅ Ya implementado (bcrypt $2b$12$) |

### 2.3 Bugs funcionales ✅

| # | Hallazgo | commit | Estado |
|---|----------|--------|--------|
| XSS-01 | XSS en `tkt_solicitud_derecho/page.tsx:75` — `&` no escapado | `14f7072` | ✅ CORREGIDO |
| DEBUG-01 | Console.log DEBUG en `lib/api.ts` | `a05fdc9` | ✅ CORREGIDO |
| DEBUG-02 | `/debug/env` expuesto en `main.py` | `37e07c2` | ✅ CORREGIDO |
| AUTH-01 | 401 devuelto como `{}` silencioso en `lib/api.ts` | `a05fdc9` | ✅ CORREGIDO |
| F1 | Feriados no considera años > 2030 | `37e07c2` | ✅ CORREGIDO |
| FERIADOS-01 | Feriados chilenos extendidos a 2040 | `37e07c2` | ✅ CORREGIDO |
| SCHEMA-01 | EIPD schemas extraídos a `schemas/eipd.py` | `da53026` | ✅ CORREGIDO |
| SEED-01 | Seed data movido a `app/data/seed_rubros.json` | `37e07c2` | ✅ CORREGIDO |

### 2.4 Mejoras arquitectónicas ✅

| # | Hallazgo | commit | Estado |
|---|----------|--------|--------|
| AUTH-02 | `check_company_access` centralizado en `deps.py` | `96167b5` | ✅ CORREGIDO |
| DB-01 | Índices `ix_rats_company_estado`, `ix_security_breaches_company_fecha` | `4f00141` | ✅ CORREGIDO |
| SQL-01 | SQLAlchemy 2.0 style unificado en 7 modelos | `37e07c2` | ✅ CORREGIDO |
| FE-01 | Token refresh automático, 401→login redirect, apiFetch retry | `a05fdc9` | ✅ CORREGIDO |

---

## 3. SCORECARD CONSOLIDADO

| Dimensión | v1.0 (inicial) | v1.2 (post-auditoría) | Tendencia |
|-----------|----------------|------------------------|-----------|
| Arquitectura | 2/10 | **6.5/10** | ✅ +4.5 |
| Seguridad | 2/10 | **7/10** | ✅ +5 |
| QA/Testing | 1/10 | **4/10** | ✅ +3 |
| Compliance | 3/10 | **7/10** | ✅ +4 |
| Funcionalidad | 7/10 | **9/10** | ✅ +2 |

---

## 4. HALLAZGOS PENDIENTES — PRIORIDAD PARA v1.3

### 4.1 Alta prioridad

| # | Hallazgo | Ubicación | Razón |
|---|----------|-----------|-------|
| C1 | Encryption at rest a nivel aplicación | DB | Neon ya provee AES-256; app-level pendiente |
| S14 | CSRF protection | Varios | 3 opciones documentadas en S14_CSRF_PROTECTION_v1.2.md — pendiente decisión |
| A6 | Capa de servicios completa | routes/ | Repository base creado, migración gradual en v1.3 |

### 4.2 Media prioridad

| # | Hallazgo | Ubicación | Razón |
|---|----------|-----------|-------|
| T1 | Coverage tests 40% | Backend | 17 tests unitarios en test_user_service.py; falta coverage |
| T8 | Tests de seguridad (SQL injection, XSS, IDOR) | Backend | TC-060-069 creados; ejecutar en CI |
| A10 | Schemas duplicados | schemas/ | 7 schemas en solicitudes_derecho.py; inline en ai.py |

### 4.3 Baja prioridad

| # | Hallazgo | Ubicación |
|---|----------|-----------|
| PII logging avanzado | Estructurar logs JSON estructurados | logging_config.py |
| Migración Alembic | ETL manual → migraciones versionadas | migrate_to_neon.py |

---

## 5. DEUDA TÉCNICA — ESTADO FINAL

| ID | Descripción | Prioridad | Estado |
|----|-------------|-----------|--------|
| DT-001 | Token blacklist (LRU 1000) | CRÍTICA | ✅ CORREGIDO |
| DT-002 | Fix IDOR en /companies/{id} | CRÍTICA | ✅ CORREGIDO |
| DT-003 | Fix /companies/publico sin auth | CRÍTICA | ✅ CORREGIDO |
| DT-004 | Sanitizar exports CSV | CRÍTICA | ✅ CORREGIDO |
| DT-005 | Rate limiting en /auth/login | ALTA | ✅ Implementado |
| DT-006 | Encryption at rest PostgreSQL | ALTA | 📋 Doc: Neon AES-256 (v1.3) |
| DT-007 | Audit trail inmutable (hash chain) | ALTA | ✅ CORREGIDO |
| DT-008 | Capa Repository pattern | MEDIA | ✅ Base implementada |
| DT-009 | Tests unitarios 40% coverage | MEDIA | 📋 17 tests (v1.3) |
| DT-010 | E2E Playwright completo | MEDIA | 📋 Pendiente |
| DT-011 | PII masking en logs | ALTA | ✅ CORREGIDO |
| DT-012 | Índices faltantes | ALTA | ✅ CORREGIDO |
| DT-013 | N+1 queries | ALTA | ✅ CORREGIDO |

**Total corregidos:** 10/13
**Pendiente v1.3:** DT-006, DT-009, DT-010

---

## 6. DOCUMENTACIÓN GENERADA

### Documentos .docx ✅

| Documento | Versión | Estado |
|----------|---------|--------|
| 02_Requisitos | v1.2 | ✅ Generado |
| 03_Historias de Usuario | v1.2 | ✅ Generado |
| 04_Casos de Uso | v1.2 | ✅ Generado |
| 05_Diseño Funcional | v1.2 | ✅ Generado |
| 06_Arquitectura | v1.1 | ✅ Generado (estaba en v1.0) |
| 07_Modelo de Datos | v1.1 | ✅ Generado (estaba en v1.0) |
| 08_APIs | v1.2 | ✅ Generado |
| 09_Backlog | v1.2 | ✅ Generado |
| 10_Plan_QA | v1.2 | ✅ Generado |
| 11_Despliegue | v1.1 | ✅ Generado (estaba en v1.0) |
| 12_Manual_Técnico | v1.2 | ✅ Generado |
| Matriz_Trazabilidad | v1.2 | ✅ Generado |

### Documentos técnicos en auditorias/

| Documento | Descripción |
|-----------|-------------|
| `AUDITORIA_V1.2.md` | Matriz de diferencias post-fixes |
| `informe_consolidado.md` | Este informe |
| `informe_arquitecto.md` | Hallazgos arquitecto |
| `informe_qa.md` | Hallazgos QA |
| `informe_compliance.md` | Hallazgos compliance |
| `ROADMAP_OLA1_v1.2.md` | Roadmap Olas 1-3 |
| `C1_ENCRYPTION_AT_REST_v1.2.md` | Análisis C1 |
| `S14_CSRF_PROTECTION_v1.2.md` | Análisis S14 con 3 opciones |
| `A5_A6_ARQUITECTURA_v1.2.md` | Análisis A5/A6 |
| `BACKUP_RECOVERY_v1.2.md` | Análisis C3 |

---

## 7. RECOMENDACIONES — v1.3

### Alta prioridad (antes del 15 Junio 2026)
1. **[ALTA]** Ejecutar script `migration_audit_hash_chain.sql` en producción Neon
2. **[ALTA]** Decidir arquitectura CSRF (S14) — mismo dominio vs double-submit vs origin validation
3. **[ALTA]** Tests de seguridad ejecutados en CI: TC-060 a TC-069

### Media prioridad
4. **[MEDIA]** Implementar coverage >= 40% en endpoints críticos
5. **[MEDIA]** E2E Playwright para flujos principales (login, crear RAT, exportar CSV)
6. **[MEDIA]** App-level encryption (C1) — decisión sobre alcance

---

## 8. REGISTRO DE AUDITORÍA

| Fecha | Versión | Especialistas | Hallazgos | Docs actualizados | Estado |
|-------|---------|--------------|-----------|-------------------|--------|
| 06 Junio 2026 | v1.1 | N/D | N/D | 00-12, Matriz | — |
| 08 Junio 2026 | v1.2 | 3 (Arquitecto, QA, Compliance) | 63+ | 12 docs | ✅ COMPLETADA |

**Rama:** `qa`
**Vercel QA:** ✅ Deploy exitoso
**Commits en qa:** 15

---

*Informe consolidado post-fixes: 08 Junio 2026*
*3 especialistas ejecutados en paralelo*
*Auditoría Custodio RAT Manager — v1.2 COMPLETADA*