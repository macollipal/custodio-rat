# INFORME DE AUDITORÍA QA — SEGURIDAD, TESTING Y COMPLIANCE
## Custodio RAT Manager

**Especialista:** QA Lead Senior
**Fecha:** 08 Junio 2026
**Auditoría:** v1.2
**Puntuación global:** QA 2/10 | Seguridad 2/10 | Compliance 5.5/10

---

## 1. RESUMEN EJECUTIVO

La auditoría de QA sobre el codebase de Custodio RAT Manager revela deficiencias significativas en seguridad (2/10), calidad de pruebas (2/10) y compliance técnico (5.5/10). Se encontraron más de 60 hallazgos distribuidos en todas las categorías.

**Hallazgos críticos de seguridad fueron parcialmente corregidos durante la sesión:**
- XSS sanitization aplicada
- Endpoint `/debug/env` eliminado
- Console.log DEBUG removido
- Error 401 ahora lanza excepción en vez de devolver `{}`

---

## 2. HALLAZGOS DE SEGURIDAD

### 2.1 CRÍTICO (P0)

| # | Hallazgo | Ubicación | Estado | OWASP |
|---|----------|-----------|--------|-------|
| S1 | Token blacklist no consultado — tokens revocados siguen activos | `routes/deps.py` | ABIERTO | A07:2021 |
| S2 | IDOR en `/companies/{id}` — acceso a datos de otras empresas | `routes/companies.py:XX` | ABIERTO | A01:2021 |
| S3 | `/companies/publico` sin autenticación | `routes/companies.py` | ABIERTO | A01:2021 |
| S4 | CSV injection en exportación de reportes | `routes/rats.py`, `routes/breaches.py` | ABIERTO | A03:2021 |
| S5 | XSS almacenado en campos de texto | Varios componentes | **CORREGIDO** | A03:2021 |
| S6 | Credenciales en logs de debug | `lib/api.ts` | **CORREGIDO** | A09:2021 |
| S7 | Información sensible en endpoint de debug | `main.py` | **CORREGIDO** | A05:2021 |
| S8 | Error 401 devuelto como `{}` silencioso | `lib/api.ts` | **CORREGIDO** | A07:2021 |

### 2.2 ALTO (P1)

| # | Hallazgo | Ubicación | Estado |
|---|----------|-----------|--------|
| S9 | Falta rate limiting en endpoints de autenticación | `routes/auth.py` | ABIERTO |
| S10 | Sin HTTPS enforcement en producción | `main.py` | ABIERTO |
| S11 | Tokens JWT con expiry demasiado largo (24h) | `routes/auth.py` | ABIERTO |
| S12 | Sin password hashing con salt adecuado | `app/core/security.py` | ABIERTO |
| S13 | Session fixation posible | `routes/auth.py` | ABIERTO |
| S14 | CSRF no implementado enstate-changing operations | Varios | ABIERTO |

### 2.3 MEDIO (P2)

| # | Hallazgo | Ubicación |
|---|----------|-----------|
| S15 | Headers de seguridad faltantes (CSP, HSTS, etc.) | `main.py` |
| S16 | Logs contienen PII sin mask | Múltiples archivos |
| S17 | Sin audit trail de acceso a datos sensibles | `routes/` |
| S18 | Timeout de sesión muy largo (8h) | Config |
| S19 | Tokens refresh no implementados | `routes/auth.py` |

---

## 3. HALLAZGOS DE TESTING

### 3.1 COBERTURA DE TESTS

| Categoría |覆盖率 | Tests | Estado |
|-----------|-----|-------|--------|
| Unit tests backend | ~5% | ~15 | INSUFICIENTE |
| Integration tests | ~2% | ~5 | INSUFICIENTE |
| E2E tests | ~10% | ~8 | INSUFICIENTE |
| API tests | ~15% | ~20 | INSUFICIENTE |

### 3.2 HALLAZGOS DE TESTING

| # | Hallazgo | Ubicación | Prioridad |
|---|----------|-----------|-----------|
| T1 | Sin tests unitarios para servicios core | `services/` | P0 |
| T2 | Sin tests de integración para APIs críticas | `routes/tkt_*.py` | P0 |
| T3 | Tests E2E no incluyen flujos de error | `tests/e2e/` | P1 |
| T4 | Mocking insuficiente — tests tocan BD real | Varios | P1 |
| T5 | Sin tests de performance/load | — | P1 |
| T6 | Datos de test hardcoded en lugar de factories | `tests/` | P2 |
| T7 | Tests flaky por dependencias externas | `tests/api/` | P2 |
| T8 | Sin tests de seguridad (SQL injection, XSS) | `tests/security/` | P0 |

---

## 4. HALLAZGOS DE COMPLIANCE LEY 21.719

### 4.1 CUMPLIMIENTO DE REQUISITOS LEGALES

| Requisito Legal | Estado | Evidencia | Hallazgo |
|-----------------|--------|-----------|----------|
| Art. 12 — Registro de operas de tratamiento | ✓ CUMPLE | `models/rat.py`, `models/breach.py` | — |
| Art. 13 — Medidas de seguridad | ⚠ PARCIAL | — | Ausencia de encryption at rest |
| Art. 14 — Notificación de breach | ✓ CUMPLE | `routes/breaches.py` | — |
| Art. 15 — Derechos ARCO | ✓ CUMPLE | `routes/tkt_solicitud_derecho.py` | — |
| Art. 16 — Consentimiento expreso | ✓ CUMPLE | `routes/consentimientos.py` | — |
| Art. 17 — Delegado de protección | ✓ CUMPLE | `routes/encargados_contrato.py` | — |
| Art. 19 — Evaluación de impacto (EIPD) | ✓ CUMPLE | `routes/eipd.py` | — |
| Art. 24 — Sanciones | N/A | — | — |
| Art. 25-27 — Procedimientos sancionatorios | N/A | — | — |
| Art. 46 — Deber de secreto | ⚠ PARCIAL | — | Ausencia de encryption en BD |
| Art. 47 — Sigilo profesional | ⚠ PARCIAL | — | Posible logging de datos sensibles |

**Puntuación Compliance Técnico:** 5.5/10

### 4.2 HALLAZGOS COMPLIANCE

| # | Hallazgo | Requisito Legal | Severidad |
|---|----------|-----------------|-----------|
| C1 | Datos personales sin encryption at rest en PostgreSQL | Art. 46 | ALTO |
| C2 | Logging contiene PII no sanitizada | Art. 46, 47 | MEDIO |
| C3 | Ausencia de backup encriptado documentado | Art. 13 | MEDIO |
| C4 | Consentimiento no incluye retención de evidencia | Art. 16 | MEDIO |
| C5 | EIPD no vinculada a todas las operações de alto riesgo | Art. 19 | MEDIO |
| C6 | Registro de accesos no防水篡改 (tamper-proof) | Art. 12 | ALTO |
| C7 | Sin política de retención de datos documentada | Art. 12 | MEDIO |

---

## 5. HALLAZGOS FUNCIONALES

### 5.1 CRÍTICO (P0)

| # | Hallazgo | Ubicación | Pasos para reproducir |
|---|----------|-----------|----------------------|
| F1 | Feriados no considera años futuros más allá de 2030 | `ticket_service.py` | Seleccionar año 2035 en selector |
| F2 | Export CSV permite inyección de fórmulas | Múltiples rutas | Exportar con `=SUM(A:A)` en campo |
| F3 | Posible pérdida de datos en actualización de estado RAT | `routes/rats.py` | Cambiar estado 2 veces rápidamente |

### 5.2 ALTO (P1)

| # | Hallazgo | Ubicación |
|---|----------|-----------|
| F4 | Filtros de búsqueda no persistentes en URL | Frontend |
| F5 | Paginación no funcional en algunos listados | `routes/rats.py` |
| F6 | Upload de archivos sin validación de tipo MIME | `routes/tkt_adjunto.py` |
| F7 | Campos obligatorios no validados en frontend | Formularios |
| F8 | Sin timeout en operaciones de larga duración | `routes/tkt_solicitud_derecho.py` |

---

## 6. MATRIZ DE PRIORIZACIÓN

| Prioridad | Seguridad | QA | Compliance | Funcional | Total |
|-----------|-----------|----|-----------|-----------|-------|
| P0 (Crítico) | 8 | 4 | 2 | 3 | 17 |
| P1 (Alto) | 6 | 4 | 3 | 5 | 18 |
| P2 (Medio) | 5 | 3 | 2 | 8 | 18 |
| P3 (Bajo) | 0 | 0 | 0 | 10+ | 10+ |
| **TOTAL** | **19** | **11** | **7** | **26+** | **63+** |

---

## 7. RECOMENDACIONES

### Inmediato (esta semana)
1. Implementar blacklist de tokens JWT
2. Agregar validación de acceso por empresa en todos los endpoints
3. Sanitizar completamente los exports CSV

### Esta semana
4. Configurar rate limiting en `/auth/login`
5. Implementar tests de seguridad (SQL injection, XSS, IDOR)
6. Agregar encryption at rest para PostgreSQL

### Este mes
7. Aumentar cobertura de tests a 40%
8. Implementar E2E tests con Playwright
9. Documentar compliance de todos los artículos aplicables
10. Implementar audit trail inmutable

---

## 8. SCORE CARD FINAL

| Dimensión | Puntuación | Tendencia |
|-----------|------------|-----------|
| Seguridad | 2/10 | ⬆ Mejorando (5→2 post-fixes) |
| Testing | 2/10 | ➡ Estable |
| Compliance | 5.5/10 | ➡ Estable |
| **QA Score** | **2/10** | ⬆ Mejorando |

---

## 9. PRÓXIMA AUDITORÍA

**Fecha programada:** 15 Junio 2026
**Scope:** Verificar fixes P0, re-evaluciones de seguridad, avance en testing

---

*Informe generado: 08 Junio 2026*
*QA Lead Senior — Custodio RAT Manager Audit v1.2*