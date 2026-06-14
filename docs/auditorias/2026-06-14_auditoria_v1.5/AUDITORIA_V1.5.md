# AUDITORÍA v1.5 — 14 JUNIO 2026
## Custodio RAT Manager

**Fecha auditoría:** 14 Junio 2026
**Carpeta:** `docs/auditorias/2026-06-14_auditoria_v1.5/`
**Documentos base:** Versión v1.4 (12 Junio 2026)
**Documentos objetivo:** Versión v1.5 (14 Junio 2026)
**Score anterior:** 7.6/10
**Madurez:** Producción Inicial → Producción

---

## 1. RESUMEN EJECUTIVO

Auditoría post-integración de seguridad crítica (S14 CSRF + C1 BYTEA Encryption + A6 Service Layer + A10 Schemas). Los principales cambios desde v1.4 son:
- **S14 (CSRF)**: Implementación completa con `samesite=lax` + `CSRFMiddleware` + rate limiter per-request
- **C1 (Encryption at Rest)**: Módulo Fernet para BYTEA con script de migración idempotente
- **A10 (Schemas Pydantic)**: 35+ endpoints con `response_model=`, OpenAPI spec completo
- **A6 (Service Layer)**: 5 nuevos servicios para centralizar lógica de negocio
- El score sube de 7.6/10 a **8.3/10** tras los fixes de seguridad

### Commits desde auditoría v1.4 (12-Jun-2026 → 14-Jun-2026)

| Commit | Fecha | Descripción |
|--------|-------|-------------|
| `7ef3d78` | 14-Jun | docs: update OWASP ZAP baseline post-C1 + A6, update CHANGELOG |
| `82d5723` | 14-Jun | feat(A6): service layer for EIPD, Feriado, Consentimiento, EncargadoContrato, SolicitudDerecho |
| `9f50f04` | 13-Jun | feat(C1): Fernet BYTEA encryption for RAT + EncargadoContrato, crypto tests, ENCRYPTION_KEY config |
| `1328001` | 13-Jun | feat(C1): Fernet encryption infra + BYTEA encryption for RAT + EncargadoContrato |
| `26725eb` | 13-Jun | docs(security): OWASP ZAP baseline manual (2026-06-13) — pre-C1 |

---

## 2. ENDPOINTS DETECTADOS EN CÓDIGO

### 2.1 Backend — Routes completas (TODOS)

Todos los 74 endpoints de v1.4 se mantienen. No hay cambios en rutas.

**Total endpoints detectados:** 74 (sin cambios desde v1.4)

---

## 3. RUTAS FRONTEND DETECTADAS

**Total páginas frontend:** 19 (sin cambios desde v1.4)

---

## 4. MODELOS DE DATOS

Todos los 23 modelos de v1.4 se mantienen. Sin cambios.

---

## 5. CAMBIOS vs DOCUMENTACIÓN v1.4

| Documento | v1.4 en docs | Código coincide? | Cambios detectados | Generar v1.5? |
|-----------|-------------|-----------------|-------------------|---------------|
| 00_Índice | v1.1 | ✓ | Ninguno | NO |
| 01_Visión | v1.0 | ✓ | Ninguno | NO |
| 02_Requisitos | v1.4 | ✗ | RF-120 (C1 BYTEA), RF-121 (A6 service layer), RF-122 (A10 schemas) | **SÍ** |
| 03_HU | v1.4 | ✗ | HU para S14, C1, A6, A10 | **SÍ** |
| 04_CU | v1.4 | ✗ | CU para CSRF middleware, encrypt/decrypt, service layer | **SÍ** |
| 05_Diseño | v1.3 | ✓ | Sin cambios | NO |
| 06_Arquitectura | v1.4 | ✗ | Crypto layer, service layer, CSRFMiddleware | **SÍ** |
| 07_Modelo Datos | v1.1 | ✓ | Sin cambios | NO |
| 08_APIs | v1.4 | ✓ | Sin cambios (A10 usa schemas wrapper sin cambiar rutas) | NO |
| 09_Backlog | v1.4 | ✓ | Sin cambios | NO |
| 10_Plan_QA | v1.4 | ✓ | Sin cambios | NO |
| 11_Despliegue | v1.2 | ✓ | Sin cambios | NO |
| 12_Manual_Técnico | v1.4 | ✗ | crypto.py, service layer, CSRF middleware, ENCRYPTION_KEY | **SÍ** |
| Matriz_Trazabilidad | v1.4 | ✗ | TC para S14, C1, A6, A10 | **SÍ** |

---

## 6. SCORECARD COMPARATIVO

| Dimensión | v1.4 (12 Jun) | v1.5 (14 Jun) | Delta |
|-----------|--------------|----------------------|-------|
| Escalabilidad | 7.5/10 | **7.5/10** | — |
| Mantenibilidad | 7/10 | **8/10** | +1.0 (A6 + A10) |
| Seguridad | 8.5/10 | **9/10** | +0.5 (S14 + C1) |
| Rendimiento | 7/10 | **7/10** | — |
| Observabilidad | 7.5/10 | **7.5/10** | — |
| Arquitectura General | 7.5/10 | **8/10** | +0.5 (A6 service layer) |
| **Overall** | **7.6/10** | **8.3/10** | **+0.7** |

---

## 7. FORTALEZAS DETECTADAS

- CSRF protection completa con `samesite=lax` + middleware dedicado
- Encryption at rest con Fernet para BYTEA (RAT + EncargadoContrato + tkt_adjuntos)
- Migration script idempotente con dry-run y backup automático
- Service layer centralizando lógica de negocio (5 servicios nuevos)
- OpenAPI spec completo con 35+ endpoints con schemas
- Arquitectura de almacenamiento robusta (OCI + BYTEA fallback)
- Hash chain de auditoría implementado y funcional
- RBAC completo con 3 niveles de acceso
- Módulo de IA con soporte MiniMax y OpenAI fallback
- Cola de tareas asíncronas con retry automático
- Exportación PDF, CSV, CNI para compliance APDC

---

## 8. HALLAZGOS CERRADOS DESDE v1.4

| ID | Descripción | Severidad | Estado |
|----|-------------|-----------|--------|
| S14 | CSRF protection | ALTA | ✅ **CERRADO** — `samesite=lax` + CSRFMiddleware |
| C1 | BYTEA encryption at rest | ALTA | ✅ **CERRADO** — Fernet + script migración |
| A10 | Schemas Pydantic | BAJA | ✅ **CERRADO** — 35+ endpoints con response_model |
| A6 | Service layer | MEDIA | ✅ **CERRADO** — 5 servicios nuevos |

---

## 9. FORTALEZAS PENDIENTES (No abordados en v1.5)

| ID | Descripción | Prioridad | Razón |
|----|-------------|-----------|-------|
| Z-01 | Security headers (CSP, X-Frame-Options) | Media | Pendiente — agregar middleware |
| Z-02 | CORS restrictivo | Baja | Pendiente — mejorar allow_methods/headers |
| Z-03 | File upload validation | Media | Pendiente — validar extensión y max size |
| Z-06 | Backups documentados | Baja | Pendiente — documentar política |

---

## 10. SCORE DE CUMPLIMIENTO LEY 21.719

| Artículo | Tema | Estado |
|----------|------|--------|
| Art. 12 | Consentimiento | ✅ Implementado |
| Art. 14 | Trazabilidad | ✅ Hash chain + audit log |
| Art. 15 bis | EIPD | ✅ Módulo completo |
| Art. 16 | Seguridad técnica | ✅ BYTEA cifrado + OCI bucket security |
| Art. 17 | Notificación brechas | ✅ Módulo de brechas |
| Art. 14 ter | Política transparencia | ✅ Endpoint público |

---

*Documento generado: 14 Junio 2026*
*Auditoría Custodio RAT Manager v1.5 — post S14 + C1 + A6 + A10*
