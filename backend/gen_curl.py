"""
Generate a curl command with the signed headers, to test OCI signing locally.
"""
from app.core.config import settings
from app.core.storage import OCIStorageBackend
import shlex

cfg = settings.oci
backend = OCIStorageBackend(cfg, settings.OCI_KEY_CONTENT)

method = "GET"
path = "/n/axic9xl7e4ss/b/custodio-documents-qa/o"
host = backend.host

signed = backend.signer.sign_headers(method, path, host)

# Build curl command
url = f"https://{host}{path}"
curl_parts = ["curl", "-v", "-X", method, url]
for k, v in signed.items():
    curl_parts.extend(["-H", f"{k}: {v}"])

print(" ".join(shlex.quote(p) for p in curl_parts))
