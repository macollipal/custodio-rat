"""
Middleware CSRF para protección contra ataques de solicitud cruzada.

Protege endpoints mutantes (POST/PUT/PATCH/DELETE) que usan autenticación por cookie.
No aplica a requests con Bearer token (no son vulnerables a CSRF por cookie).

Defensa en capas:
1. samesite=lax ya bloquea la mayoría de ataques (solo navegación GET cross-site)
2. Este middleware bloquea los POST cross-site que el navegador podría enviar con cookie

Uso: requests que incluyen la cookie custodio_token Y usan método mutante
      deben incluir el header X-Requested-With: XMLHttpRequest (enviado automáticamente
      por fetch() y XMLHttpRequest en browsers modernos).
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.routes.deps import COOKIE_NAME


CSRF_SAFE_METHODS = {"GET", "HEAD", "OPTIONS", "TRACE"}

CSRF_SAFE_PATHS = {
    "/docs",
    "/redoc",
    "/openapi.json",
    "/auth/login",
    "/auth/refresh",
    "/publico/",
    "/ai/ask",
    "/health",
    "/",
}


class CSRFMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method in CSRF_SAFE_METHODS:
            return await call_next(request)

        if any(request.url.path.startswith(p) for p in CSRF_SAFE_PATHS):
            return await call_next(request)

        if "Authorization" in request.headers:
            return await call_next(request)

        cookie_token = request.cookies.get(COOKIE_NAME)
        if not cookie_token:
            return await call_next(request)

        x_requested_with = request.headers.get("X-Requested-With", "").lower()
        if x_requested_with == "xmlhttprequest":
            return await call_next(request)

        return JSONResponse(
            status_code=403,
            content={
                "detail": (
                    "CSRF validation failed. "
                    "For AJAX requests, include the header X-Requested-With: XMLHttpRequest. "
                    "Requests with Authorization: Bearer token are exempt."
                )
            },
        )