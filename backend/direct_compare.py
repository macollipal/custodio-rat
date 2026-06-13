"""
Comparar directamente: SDK signer vs Mi signer (sin network).
"""
import email.utils
import base64
import hashlib

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend

from app.core.config import settings
cfg = settings.oci
key_content = settings.OCI_KEY_CONTENT
literal_n = chr(92) + chr(110)
real_nl = chr(10)
if literal_n in key_content and real_nl not in key_content:
    key_content = key_content.replace(literal_n, real_nl)

private_key = serialization.load_pem_private_key(
    key_content.encode(), password=None, backend=default_backend()
)

tenancy = cfg["tenancy"]
user = cfg["user"]
fingerprint = cfg["fingerprint"]
key_id = f"{tenancy}/{user}/{fingerprint}"
region = cfg["region"]
host = f"objectstorage.{region}.oraclecloud.com"
namespace = cfg["namespace"]
bucket = cfg["bucket"]

method = "GET"
path = f"/n/{namespace}/b/{bucket}/o"
url = f"https://{host}{path}"

# =============================================
# MI FIRMA
# =============================================
date_str = email.utils.formatdate(usegmt=True)
signing_headers_list = ["(request-target)", "date", "host"]
signing_values = {
    "(request-target)": f"{method.lower()} {path}",
    "date": date_str,
    "host": host,
}
signing_string_mio = "\n".join([
    f"{h}: {signing_values[h]}"
    for h in signing_headers_list
])

signature_mio = private_key.sign(
    signing_string_mio.encode("ascii"),
    padding.PKCS1v15(),
    hashes.SHA256()
)
my_signature_b64 = base64.b64encode(signature_mio).decode("ascii")

my_auth = (
    f'Signature version="1",algorithm="SHA256withRSA",'
    f'keyId="{key_id}",signature="{my_signature_b64}",'
    f'headers="{" ".join(signing_headers_list)}"'
)

# =============================================
# SDK FIRMA (llamando el signer directamente)
# =============================================
from oci import Signer as OCISigner

# Crear signer del SDK
sdk_signer = OCISigner(
    tenancy=tenancy,
    user=user,
    fingerprint=fingerprint,
    private_key_file_location=None,
    private_key_content=key_content
)

# Usar el signer para firmar una request
import requests
req = requests.Request(method, url)
prepared = req.prepare()

# Ahora usar el SDK signer para firmar los headers
# El signer espera headers en un formato especial
# Vamos a ver que produce

# Generar los headers con el SDK signer
# EI método do_request_sign es el que firma
from oci.base_client import BaseClient

# Podemos crear un request mock y llamar sign_headers
class MockRequest:
    def __init__(self, method, url):
        self.method = method
        self.url = url
        self.path_url = url.split(host)[1] if host in url else '/'
        self.headers = {}
        self.body = None

mock_req = MockRequest(method, url)
mock_req.headers['date'] = date_str
mock_req.headers['host'] = host

# Llamar el signer del SDK
signed_req = sdk_signer.do_request_sign(mock_req, enforce_content_headers=True)

print("=== MI FIRMA ===")
print(f"Signing string:")
print(repr(signing_string_mio))
print(f"\nMi Authorization:")
for part in my_auth.split(","):
    print(f"  {part}")

print("\n=== SDK FIRMA ===")
print(f"Headers después de firmar:")
for k, v in signed_req.headers.items():
    if k.lower() in ['authorization', 'date', 'host']:
        print(f"  {k}: {v[:80]}{'...' if len(v) > 80 else ''}")

# =============================================
# COMPARAR LOS SIGNING STRINGS
# =============================================
print("\n=== COMPARACIÓN ===")

# Extraer signing string del SDK
# El SDK usa httpsig_cffi internamente, así que el signing string
# debería ser igual, pero el signature será diferente

# Extraer signature del SDK
import re
sdk_auth = signed_req.headers.get('Authorization', '')
sdk_sig_match = re.search(r'signature="([^"]+)"', sdk_auth)
my_sig_match = re.search(r'signature="([^"]+)"', my_auth)

print(f"\nSDK Authorization header completo:")
print(sdk_auth[:300])
print(f"\nMi Authorization header completo:")
print(my_auth[:300])

if sdk_sig_match and my_sig_match:
    sdk_sig = sdk_sig_match.group(1)
    my_sig = my_sig_match.group(1)
    print(f"\nSDK signature length: {len(sdk_sig)}")
    print(f"Mi signature length: {len(my_sig)}")
    print(f"Signatures iguales: {sdk_sig == my_sig}")
    if sdk_sig != my_sig:
        print(f"\n[DEBUG] Los signatures son DIFERENTES!")
        print(f"SDK signature: {sdk_sig[:50]}...")
        print(f"Mi signature: {my_sig[:50]}...")

# Verificar que los headers que se usan para firmar son los mismos
sdk_keyid_match = re.search(r'keyId="([^"]+)"', sdk_auth)
my_keyid_match = re.search(r'keyId="([^"]+)"', my_auth)
print(f"\nSDK keyId: {sdk_keyid_match.group(1) if sdk_keyid_match else 'N/A'}")
print(f"Mi keyId: {my_keyid_match.group(1) if my_keyid_match else 'N/A'}")

# Comparar algorithm
sdk_alg_match = re.search(r'algorithm="([^"]+)"', sdk_auth)
my_alg_match = re.search(r'algorithm="([^"]+)"', my_auth)
print(f"\nSDK algorithm: {sdk_alg_match.group(1) if sdk_alg_match else 'N/A'}")
print(f"Mi algorithm: {my_alg_match.group(1) if my_alg_match else 'N/A'}")

# Comparar version
sdk_ver_match = re.search(r'version="([^"]+)"', sdk_auth)
my_ver_match = re.search(r'version="([^"]+)"', my_auth)
print(f"\nSDK version: {sdk_ver_match.group(1) if sdk_ver_match else 'N/A'}")
print(f"Mi version: {my_ver_match.group(1) if my_ver_match else 'N/A'}")

# Comparar headers
sdk_hdrs_match = re.search(r'headers="([^"]+)"', sdk_auth)
my_hdrs_match = re.search(r'headers="([^"]+)"', my_auth)
print(f"\nSDK headers: {sdk_hdrs_match.group(1) if sdk_hdrs_match else 'N/A'}")
print(f"Mi headers: {my_hdrs_match.group(1) if my_hdrs_match else 'N/A'}")
