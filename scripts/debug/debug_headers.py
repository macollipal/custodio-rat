"""
Debug: see exactly what requests sends.
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

# Use PreparedRequest to see what gets sent
req = requests.Request(method, url, headers=signed)
prepared = req.prepare()

print("=== Headers in prepared request ===")
for k, v in prepared.headers.items():
    print(f"  {k}: {v[:80]}{'...' if len(v) > 80 else ''}")

print(f"\n=== Method: {prepared.method} ===")
print(f"=== URL: {prepared.url} ===")
print(f"=== Path: {prepared.path_url} ===")
