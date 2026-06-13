from slowapi import Limiter
from slowapi.util import get_remote_address
import os


def _get_limiter_key(request):
    if os.getenv("ENV") == "test":
        import uuid
        return f"test-{uuid.uuid4().hex[:12]}"
    addr = get_remote_address(request)
    if not addr or addr == "unknown":
        return "fallback"
    return addr


limiter = Limiter(key_func=_get_limiter_key)
