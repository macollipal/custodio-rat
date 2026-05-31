from slowapi import Limiter
from slowapi.util import get_remote_address
import os

def _get_limiter_key(request):
    if os.getenv("ENV") == "test":
        return None
    return get_remote_address(request)

limiter = Limiter(key_func=_get_limiter_key)
