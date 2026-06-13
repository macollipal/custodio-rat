# S14 — CSRF Protection — Custodio RAT Manager

## Estado: PENDIENTE (requiere decisión de arquitectura)

---

## Hallazgo

CSRF no implementado. Los endpoints que modifican estado (`POST`, `PUT`, `DELETE`) son vulnerables a cross-site request forgery.

---

## Análisis del Problema

### Arquitectura actual

| Componente | Dominio | Notas |
|-----------|---------|-------|
| Frontend | `custodio-qa.vercel.app` (假设) | SPA en Vercel |
| Backend API | `custodio-qa.vercel.app` (o subdomain diferente) | FastAPI |

### El dilema de SameSite cookies

El backend usa cookies httpOnly para almacenar tokens:

```python
# auth.py
def _cookie_options(max_age: int = None) -> dict:
    return {
        "max_age": max_age or COOKIE_MAX_AGE,
        "httponly": True,
        "secure": True,
        "samesite": "none" if settings.ENVIRONMENT == "production" else "lax",
        "path": "/",
    }
```

| SameSite | Efecto | ¿Funciona con cross-origin? |
|----------|--------|---------------------------|
| `Strict` | Cookie solo se envía en requests same-origin | ❌ SPA no puede navegar |
| `Lax` | Se envía en navegación top-level | ⚠️ Puede no funcionar en todos los flows |
| `None` | Se envía en todos los requests | ✅ Necesario para cross-origin |

### Riesgos

1. **Miembro malicioso** induce a un admin a hacer click en link que dispara `DELETE /companies/5`
2. **Form malicious** en otro sitio hace `POST /rats/` con datos falsos
3. **Imagen/iframe** en email hace `POST /brechas/` para crear brecha falsa

---

## Opciones de Solución

### Opción 1: Double-Submit Cookie Pattern (Recomendado)

**Cómo funciona:**
1. Server emite cookie `csrf_token` (sin httpOnly, para JS legible)
2. Client lee el token y lo incluye en header `X-CSRF-Token` en requests state-changing
3. Server valida que `X-CSRF-Token` == cookie `csrf_token`

**Ventajas:**
- No requiere cambios en infraestructura de dominios
- Seguro contra CSRF
- Implementable en FastAPI middleware

**Desventajas:**
- Necesita cambiar frontend para leer y enviar el token
- Cookies de CSRF token deben tener `SameSite=None; Secure` (cross-origin)

```python
# Ejemplo middleware CSRF
class CSRFMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["method"] in ("POST", "PUT", "PATCH", "DELETE"):
            # Validar CSRF token
            ...
```

### Opción 2: Same-Domain Deployment

Hacer que frontend y backend estén en el mismo dominio:
- Frontend: `custodio.example.com`
- Backend: `custodio.example.com/api`

**Ventajas:**
- `SameSite=Strict` funciona
- No necesita CSRF tokens
- Más simple

**Desventajas:**
- Requiere cambiar configuración de Vercel
- Monorepo o proxy inverso

### Opción 3: Origin Validation Middleware

Validar `Origin` o `Referer` header en el backend:

```python
@app.middleware
async def validate_origin(request: Request, call_next):
    origin = request.headers.get("origin")
    if origin and origin not in ALLOWED_ORIGINS:
        raise HTTPException(403, "Invalid origin")
    return await call_next(request)
```

**Ventajas:**
- Implementación simple
- Funciona con cookies `SameSite=None`

**Desventajas:**
- No protege contra todas las formas de CSRF
- Depende de que el cliente envíe Origin header

---

## Recomendación

**Opción 1 + 3 combinadas:**
1. Implementar Origin validation middleware (protección básica)
2. En paralelo, implementar Double-Submit cookie pattern (protección completa)
3. Planificar migración a same-domain para simplificar

---

## Implementación sugerida (Opción 1+3)

### Paso 1: Origin Validation (1 hora)

```python
# app/middleware/csrf.py
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "").split(",")

class OriginValidationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method in ("POST", "PUT", "PATCH", "DELETE"):
            origin = request.headers.get("origin") or request.headers.get("referer")
            if origin:
                allowed = any(o.strip().rstrip("/") in origin for o in ALLOWED_ORIGINS if o.strip())
                if not allowed and not request.url.hostname == "localhost":
                    raise HTTPException(403, "CSRF: Invalid origin")
        return await call_next(request)
```

### Paso 2: Double-Submit Cookie (4 horas)

1. Backend: generar `csrf_token` en login, guardar en cookie `csrf_token` (no httpOnly)
2. Frontend: leer `csrf_token` de cookies, enviar en header `X-CSRF-Token`
3. Backend: validar `X-CSRF-Token` == cookie `csrf_token` en requests state-changing

---

## Decisión Pendiente

| Opción | Esfuerzo | Riesgo | Recomendación |
|--------|---------|--------|--------------|
| 1. Double-submit | 4-6 horas | Medio | ✅ Implementar |
| 2. Same-domain | 1-2 días | Alto | Post-poned |
| 3. Origin validation | 1 hora | Bajo | ✅ Implementar primero |

---

## Estado

- [x] Documento creado
- [ ] Decision architecture team
- [ ] Implementar origin validation (1h)
- [ ] Implementar double-submit pattern (4h)
- [ ] Testing CSRF

---

*Documento generado: 08 Junio 2026*
*S14 — CSRF Protection — Custodio RAT Manager v1.2*