"""
CORS restrictivo por ruta (Z-02).

Rutas públicas  (/publico/*, /health, /):
    - allow_origins: * (ciudadanos acceden desde cualquier dominio)
    - allow_credentials: False (no se envían cookies/tokens)
    - methods: GET, POST, OPTIONS

Rutas privadas (todas las demás):
    - allow_origins: ALLOWED_ORIGINS (lista controlada de frontends)
    - allow_credentials: True (se necesita Authorization header)
    - methods: GET, POST, PUT, PATCH, DELETE, OPTIONS
"""

from __future__ import annotations

PUBLIC_PREFIXES = (
    "/publico/",
    "/health",
    "/",  # sólo match exacto de "/"
)

_PUBLIC_METHODS = b"GET, POST, OPTIONS"
_PRIVATE_METHODS = b"GET, POST, PUT, PATCH, DELETE, OPTIONS"
_PUBLIC_HEADERS = b"Content-Type, Accept, Origin"
_PRIVATE_HEADERS = b"Authorization, Content-Type, X-Requested-With, X-Request-ID, Accept, Origin"
_EXPOSE_HEADERS = b"X-Request-ID"
_MAX_AGE = b"600"


def _is_public(path: str) -> bool:
    if path == "/":
        return True
    for prefix in PUBLIC_PREFIXES:
        if prefix != "/" and path.startswith(prefix):
            return True
    return False


def _cors_response_headers(origin: str, path: str, allowed_origins: set[str]) -> list[tuple[bytes, bytes]]:
    """Devuelve los headers CORS para una respuesta real (no preflight)."""
    headers: list[tuple[bytes, bytes]] = []
    if not origin:
        return headers

    if _is_public(path):
        headers.append((b"access-control-allow-origin", b"*"))
        headers.append((b"access-control-expose-headers", _EXPOSE_HEADERS))
    elif origin in allowed_origins:
        headers.append((b"access-control-allow-origin", origin.encode()))
        headers.append((b"access-control-allow-credentials", b"true"))
        headers.append((b"vary", b"Origin"))
        headers.append((b"access-control-expose-headers", _EXPOSE_HEADERS))

    return headers


def _preflight_headers(origin: str, path: str, allowed_origins: set[str]) -> list[tuple[bytes, bytes]]:
    """Devuelve los headers para una respuesta OPTIONS (preflight)."""
    headers: list[tuple[bytes, bytes]] = []
    if not origin:
        return headers

    is_public = _is_public(path)
    if is_public:
        headers.append((b"access-control-allow-origin", b"*"))
        headers.append((b"access-control-allow-methods", _PUBLIC_METHODS))
        headers.append((b"access-control-allow-headers", _PUBLIC_HEADERS))
    elif origin in allowed_origins:
        headers.append((b"access-control-allow-origin", origin.encode()))
        headers.append((b"access-control-allow-credentials", b"true"))
        headers.append((b"vary", b"Origin"))
        headers.append((b"access-control-allow-methods", _PRIVATE_METHODS))
        headers.append((b"access-control-allow-headers", _PRIVATE_HEADERS))
        headers.append((b"access-control-expose-headers", _EXPOSE_HEADERS))

    if headers:
        headers.append((b"access-control-max-age", _MAX_AGE))

    return headers


class CORSByPathMiddleware:
    """Middleware ASGI que aplica política CORS diferenciada por ruta."""

    def __init__(self, app, allowed_origins: list[str]):
        self.app = app
        self.allowed_origins: set[str] = set(allowed_origins)

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        raw_headers = dict(scope.get("headers", []))
        origin = raw_headers.get(b"origin", b"").decode("utf-8", errors="ignore")
        path: str = scope.get("path", "")
        method: str = scope.get("method", "GET")

        if method == "OPTIONS":
            preflight_hdrs = _preflight_headers(origin, path, self.allowed_origins)
            await send({
                "type": "http.response.start",
                "status": 204,
                "headers": preflight_hdrs,
            })
            await send({"type": "http.response.body", "body": b""})
            return

        cors_hdrs = _cors_response_headers(origin, path, self.allowed_origins)

        async def patched_send(message):
            if message.get("type") == "http.response.start" and cors_hdrs:
                existing = list(message.get("headers", []))
                existing.extend(cors_hdrs)
                message = {**message, "headers": existing}
            await send(message)

        await self.app(scope, receive, patched_send)
