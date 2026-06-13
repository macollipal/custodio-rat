"""
Test OCI signing locally by making the actual request.
"""
import requests
from app.core.config import settings
from app.core.storage import OCIStorageBackend

cfg = settings.oci
backend = OCIStorageBackend(cfg, settings.OCI_KEY_CONTENT)

method = "GET"
path = "/n/axic9xl7e4ss/b/custodio-documents-qa/o"
host = backend.host

signed = backend.signer.sign_headers(method, path, host)
url = f"https://{host}{path}"

print(f"URL: {url}")
print(f"Headers: {dict(signed)}")
print()

resp = requests.get(url, headers=signed, timeout=10)
print(f"Status: {resp.status_code}")
print(f"Body: {resp.text[:200]}")
