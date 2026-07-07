from slowapi import Limiter
from slowapi.util import get_remote_address
import os


def _get_limiter_key(request):
    """Obtiene la key de rate-limit para una request.

    Prioridad:
    1. Header ``X-Forwarded-For`` (proxy/load balancer).
    2. Header ``X-Real-IP`` (nginx).
    3. Conexion directa ``client.host``.
    4. En modo test: UUID random para evitar colisiones.
    5. Fallback "unknown" si todo lo anterior falla.
    """
    if os.getenv("ENV") == "test":
        import uuid
        return f"test-{uuid.uuid4().hex[:12]}"

    # S3.2: priorizar X-Forwarded-For para entornos detrás de proxy.
    xff = request.headers.get("x-forwarded-for") if request.headers else None
    if xff:
        return xff.split(",")[0].strip()

    x_real_ip = request.headers.get("x-real-ip") if request.headers else None
    if x_real_ip:
        return x_real_ip.strip()

    addr = get_remote_address(request)
    if not addr or addr == "unknown":
        return "fallback"
    return addr


limiter = Limiter(key_func=_get_limiter_key)
