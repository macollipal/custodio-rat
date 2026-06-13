"""
Debug OCI signing - compare our implementation with what OCI SDK does.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import base64
import email.utils
import hashlib
from urllib.parse import quote

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend

from app.core.config import settings

cfg = settings.oci
key_content = settings.OCI_KEY_CONTENT

# Load key
if "\\n" in key_content and "\n" not in key_content:
    key_content = key_content.replace("\\n", "\n")

private_key = serialization.load_pem_private_key(
    key_content.encode(),
    password=None,
    backend=default_backend()
)

key_id = f"{cfg['tenancy']}/{cfg['user']}/{cfg['fingerprint']}"
method = "GET"
path = "/n/axic9xl7e4ss/b/custodio-documents-qa/o/tests/debug_test.txt"
host = "objectstorage.sa-santiago-1.oraclecloud.com"

date_str = email.utils.formatdate(usegmt=True)

print("=== OCI SIGNING DEBUG ===")
print(f"KeyId: {key_id}")
print(f"Date: {date_str}")
print(f"Method: {method}")
print(f"Path: {path}")
print(f"Host: {host}")
print()

# Build signing string
signing_headers = ["(request-target)", "date", "host"]
signing_values = {
    "(request-target)": f"{method.lower()} {path}",
    "date": date_str,
    "host": host,
}

signing_string = "\n".join([
    f"{h}: {signing_values[h]}"
    for h in signing_headers
])

print("Signing string:")
print(signing_string)
print()

# Sign
signature = private_key.sign(
    signing_string.encode("ascii"),
    padding.PKCS1v15(),
    hashes.SHA256()
)
sig_b64 = base64.b64encode(signature).decode("ascii")

print(f"Signature (base64, first 50): {sig_b64[:50]}...")
print(f"Signature length: {len(sig_b64)}")
print()

# Build auth header
auth = (
    f'Signature version="1",'
    f'algorithm="SHA256withRSA",'
    f'keyId="{key_id}",'
    f'signature="{quote(sig_b64, safe="")}"'
)

print("Authorization header:")
print(auth[:150] + "...")
print()

# Make actual request
import requests
headers = {
    "host": host,
    "date": date_str,
    "Authorization": auth,
}

url = f"https://{host}{path}"
print(f"Request URL: {url}")
print(f"Request headers: {headers}")
print()

resp = requests.get(url, headers=headers, timeout=30)
print(f"Status: {resp.status_code}")
print(f"Response: {resp.text[:200] if resp.text else '(empty)'}")
