"""
Middleware ASGI/HTTP para propagación de X-Request-ID.

- Si el cliente envía X-Request-ID, se respeta.
- Si no, se genera un UUID v4.
- Se guarda en contextvars para que el sistema de logging lo lea.
- Se devuelve en la respuesta como header X-Request-ID para correlación cliente↔servidor.
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.logging_config import set_request_id


class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        incoming = request.headers.get("X-Request-ID")
        rid = set_request_id(incoming)
        response = await call_next(request)
        response.headers["X-Request-ID"] = rid
        return response
