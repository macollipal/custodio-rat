# OWASP ZAP Baseline — Custodio RAT QA

**Fecha:** 2026-06-13
**Target:** `https://custodio-qa.vercel.app`
**Versión auditada:** qa (post S14 + A10)
**Estado:** ⚠️ **Baseline manual** (ZAP automatizado no disponible en el entorno)

---

## ⚠️ Nota sobre metodología

OWASP ZAP automatizado no pudo ejecutarse en este entorno (Docker daemon no disponible, ZAP standalone no instalado). Este documento es un **baseline manual** basado en:
- Revisión de código fuente (FastAPI, Next.js)
- Inspección de headers HTTP via `curl` / `TestClient`
- Conocimiento del stack y configuración

**Para baseline automatizado se recomienda:**
- Levantar ZAP en una máquina con Docker o ZAP standalone
- Apuntar a `https://custodio-qa.vercel.app`
- Generar reporte HTML/JSON
- Comparar con post-C1 (encryption)

---

## 1. Headers de seguridad HTTP

### Verificación manual contra `https://custodio-qa.vercel.app/`

| Header | Valor | Estado |
|--------|-------|--------|
| `Strict-Transport-Security` | `max-age=63072000; includeSubDomains; preload` | ✅ **HSTS activo** (Vercel default) |
| `Content-Security-Policy` | — | ❌ No configurado |
| `X-Frame-Options` | — | ❌ No configurado |
| `X-Content-Type-Options` | — | ❌ No configurado |
| `Referrer-Policy` | — | ❌ No configurado |
| `Permissions-Policy` | — | ❌ No configurado |
| `X-XSS-Protection` | — | (Deprecado, no relevante) |

**Análisis:**
- **HSTS** lo provee Vercel automáticamente (bueno, no requiere acción).
- El resto de headers de seguridad **no están configurados** a nivel backend ni a nivel Next.js.

**Riesgo:** sin CSP/X-Frame-Options, hay riesgo de clickjacking y XSS si un atacante logra inyectar contenido (vía input no sanitizado del lado frontend).

**Recomendación:** agregar middleware de security headers en FastAPI (válido para endpoints API):
```python
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=()"
    return response
```

---

## 2. Cookies (ya auditado en S14)

| Aspecto | Estado | Referencia |
|---------|--------|------------|
| `httponly` | ✅ Sí | `auth.py:34` |
| `secure` | ✅ Sí | `auth.py:35` |
| `samesite` | ✅ `lax` (post-S14) | `auth.py:36` |
| Expiración | ✅ ACCESS 8h, REFRESH 30d | `auth.py:27-28` |
| Revocación | ✅ Token blacklist | `security.py:revoke_token` |

**CSRF protection (post-S14):**
- `samesite=lax` bloquea cross-site POST con cookies
- `CSRFMiddleware` valida `X-Requested-With` en mutantes con cookie
- Bearer token exento (no vulnerable)

**Veredicto:** ✅ Cookies seguras para compliance Ley 21.719 Art. 12.

---

## 3. CORS

| Aspecto | Estado | Referencia |
|---------|--------|------------|
| `allow_origins` | ✅ Whitelist (no `*`) | `main.py:135` |
| `allow_credentials` | ✅ `True` (necesario para cookies) | `main.py:136` |
| `allow_methods` | ⚠️ `*` | `main.py:137` |
| `allow_headers` | ⚠️ `*` | `main.py:138` |

**Riesgo:** `allow_methods=["*"]` + `allow_headers=["*"]` es permisivo. Si bien `allow_origins` está restringido, defense-in-depth sugiere limitar a:
```python
allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
allow_headers=["Authorization", "Content-Type", "X-Requested-With"]
```

**Veredicto:** ⚠️ Funciona, mejorable.

---

## 4. Autenticación y autorización

| Aspecto | Estado | Referencia |
|---------|--------|------------|
| JWT con HS256 | ✅ Implementado | `core/security.py` |
| Refresh token rotation | ✅ Implementado | `auth.py:refresh` |
| Token blacklist | ✅ Implementado | `core/security.py:revoke_token` |
| RBAC (3 roles) | ✅ `superadmin`, `admin_empresa`, `usuario` | `models/user.py` |
| IDOR prevention | ✅ `check_company_access` | `routes/deps.py:110` |
| Rate limiting | ✅ `slowapi` en login | `core/limiter.py` |
| Password hashing | ✅ bcrypt | `core/security.py:17` |
| CSRF (post-S14) | ✅ `samesite=lax` + middleware | `middleware/csrf.py` |

**Veredicto:** ✅ Autenticación robusta. Cumple Ley 21.719.

---

## 5. Validación de input

| Aspecto | Estado | Referencia |
|---------|--------|------------|
| Pydantic schemas | ✅ En TODOS los endpoints con body | `schemas/*` |
| Path traversal | ✅ FastAPI valida paths | framework |
| SQL Injection | ✅ SQLAlchemy ORM (parametrized) | models/* |
| XSS | ⚠️ Backend no sanitiza (responsabilidad del frontend) | — |
| File upload (PDFs) | ⚠️ Acepta cualquier extensión/nombre | `encargados_contrato.py` |
| File upload size limit | ⚠️ No configurado | — |

**Veredicto:** ✅ Inputs validados, ⚠️ File upload mejorable.

---

## 6. Almacenamiento de datos

| Aspecto | Estado | Referencia |
|---------|--------|------------|
| Passwords | ✅ bcrypt (12 rounds) | `core/security.py:17` |
| BYTEA archivos (RAT, contratos) | ❌ **Plano** | `models/rat.py:74` |
| OCI storage | ❌ **Plano** (no cifrado client-side) | `core/storage.py` |
| Database connection | ✅ SSL en Neon (`sslmode=require`) | `.env.example:28` |
| Backups | ❓ No documentado | — |

**Veredicto:** ❌ **Encryption at rest NO implementado.** Bloqueante para compliance Ley 21.719 Art. 16.

**Pendiente crítico:** **C1 — Encryption at rest** (ya en plan, próximo a ejecutar).

---

## 7. Logging y observabilidad

| Aspecto | Estado | Referencia |
|---------|--------|------------|
| Request ID | ✅ Middleware + contextvar | `middleware/request_id.py` |
| Logging JSON en prod | ✅ | `core/logging_config.py` |
| Audit log (operaciones) | ✅ `log_audit` | `services/audit_service.py` |
| Hash chain (audit) | ✅ | `test_hash_chain.py` |
| Health check | ✅ `/health` | `main.py` |

**Veredicto:** ✅ Logging y audit completo. Compliance Art. 14 (trazabilidad de operaciones).

---

## 8. Resumen de hallazgos

| # | Hallazgo | Severidad | Estado |
|---|----------|-----------|--------|
| Z-01 | Headers de seguridad no reforzados (CSP, HSTS, X-Frame-Options) | Media | Pendiente — agregar middleware |
| Z-02 | CORS `allow_methods=["*"]` permisivo | Baja | Pendiente — restringir |
| Z-03 | File upload sin validación de extensión/tamaño | Media | Pendiente — validar extensión y max size |
| Z-04 | BYTEA y OCI sin cifrado at rest | **ALTA** | **C1 (en plan)** |
| Z-05 | No hay rate limit en endpoints además de `/auth/login` | Baja | Aceptable — slowapi en login es suficiente |
| Z-06 | Backups de BD no documentados | Baja | Pendiente — documentar política |

---

## 9. Veredicto global

**Estado de seguridad del backend Custodio RAT:**
- ✅ Autenticación robusta (JWT + bcrypt + blacklist + CSRF)
- ✅ Validación de input (Pydantic + SQLAlchemy)
- ✅ Logging completo (request ID + audit log + hash chain)
- ✅ Cookies seguras (httponly + secure + samesite=lax)
- ⚠️ Headers HTTP no reforzados (recomendable agregar middleware)
- ❌ **Encryption at rest NO implementado** (C1 pendiente)

**Compliance Ley 21.719:**
- Art. 12 (consentimiento): ✅
- Art. 14 (trazabilidad): ✅ (audit log con hash chain)
- Art. 16 (seguridad técnica): ⚠️ Parcial (faltan headers + encryption at rest)

**Acción prioritaria:** ejecutar **C1 — Encryption at rest** (próxima fase del plan).

---

## 10. Cómo ejecutar ZAP automatizado (para futuro)

### Opción A — Docker (recomendado)
```bash
docker pull owasp/zap2docker-stable
docker run -u zap -p 8080:8080 -i owasp/zap2docker-stable \
  zap-full-scan.py -t https://custodio-qa.vercel.app -r zap-report.html
```

### Opción B — Standalone
1. Descargar ZAP desde https://www.zaproxy.org/download/
2. Iniciar ZAP daemon
3. Usar API: `python -c "from zapv2 import ZAPv2; zap = ZAPv2(apikey='...')"`

### Opción C — GitHub Action
```yaml
- name: OWASP ZAP Scan
  uses: zaproxy/action-baseline@v0.7.0
  with:
    target: https://custodio-qa.vercel.app
```

---

*Generado manualmente el 2026-06-13 por agente opencode.*
*Próxima medición: post-C1 (encryption) para comparar delta.*