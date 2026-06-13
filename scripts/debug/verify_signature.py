"""
Test that local signing produces same signature as what Vercel would produce.
"""
from app.core.config import settings
from app.core.storage import OCIStorageBackend
import base64
import hashlib

cfg = settings.oci
backend = OCIStorageBackend(cfg, settings.OCI_KEY_CONTENT)

# Sign a test request
method = "GET"
path = "/n/axic9xl7e4ss/b/custodio-documents-qa/o"
host = backend.host

signed = backend.signer.sign_headers(method, path, host)

# Extract the signing string
import email.utils
date_str = signed.get("Date") or signed.get("date")
signing_string = "\n".join([
    f"(request-target): {method.lower()} {path}",
    f"date: {date_str}",
    f"host: {host}",
])

# Verify signature locally
import base64
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend

key_content = settings.OCI_KEY_CONTENT
if chr(92)+chr(110) in key_content and chr(10) not in key_content:
    key_content = key_content.replace(chr(92)+chr(110), chr(10))

# Extract signature from Authorization header
auth = signed.get("Authorization", "")
sig_start = auth.find('signature="') + len('signature="')
sig_end = auth.find('"', sig_start)
signature = auth[sig_start:sig_end]

# Try to verify the signature with the public key
try:
    private_key = serialization.load_pem_private_key(
        key_content.encode(), password=None, backend=default_backend()
    )
    public_key = private_key.public_key()
    public_key.verify(
        base64.b64decode(signature),
        signing_string.encode("ascii"),
        padding.PKCS1v15(),
        hashes.SHA256()
    )
    print("[OK] Signature is valid (verifies with own public key)")
except Exception as e:
    print(f"[FAIL] Signature verification FAILED: {e}")

print(f"\nSigning string:")
print(repr(signing_string))
print(f"\nSignature: {signature[:40]}...")
print(f"Signature length: {len(signature)}")
