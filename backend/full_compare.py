"""
Comparar byte por byte: SDK vs Mi implementación.
Hacemos una request real con el SDK y tomamos los headers exactos.
"""
import socket
import threading
import email.utils
import base64
import hashlib
import http.server

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
# CAPTURAR REQUEST DEL SDK USANDO PROXY
# =============================================
import http.client
import json

captured_request = {}

class ProxyHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # Silenciar

    def do_CONNECT(self):
        self.wfile.write(b"HTTP/1.1 501\r\n\r\n")

    def do_GET(self):
        global captured_request
        # Capturar headers
        captured_request = {
            'method': self.command,
            'path': self.path,
            'headers': dict(self.headers),
            'raw': self.raw_requestline.decode('utf-8', errors='ignore'),
        }
        # Responder 200 para que la request continue
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(b'{"captured": true}')

import http.server

# Iniciar proxy
proxy_port = 8899
proxy_server = http.server.HTTPServer(('localhost', proxy_port), ProxyHandler)
proxy_thread = threading.Thread(target=proxy_server.handle_request)
proxy_thread.start()

# Configurar proxy para SDK
import os
os.environ['http_proxy'] = f'http://localhost:{proxy_port}'
os.environ['https_proxy'] = f'http://localhost:{proxy_port}'

# Hacer request con SDK
import oci
from oci.object_storage.object_storage_client import ObjectStorageClient

sdk_config = {
    "tenancy": tenancy,
    "user": user,
    "fingerprint": fingerprint,
    "key_content": key_content,
    "region": region,
}

sdk_client = ObjectStorageClient(sdk_config)
try:
    result = sdk_client.list_objects(namespace_name=namespace, bucket_name=bucket)
    print(f"SDK Request successful: {len(result.data.objects)} objects")
except Exception as e:
    print(f"SDK Error: {e}")

# Limpiar proxy
os.environ.pop('http_proxy', None)
os.environ.pop('https_proxy', None)
proxy_thread.join(timeout=3)

# =============================================
# MOSTRAR LOS HEADERS CAPTURADOS
# =============================================
print("\n" + "="*60)
print("=== HEADERS QUE EL SDK ENVÍA (capturados via proxy) ===")
print(f"Method: {captured_request.get('method')}")
print(f"Path: {captured_request.get('path')}")
print("\nHeaders relevantes:")
for k, v in captured_request.get('headers', {}).items():
    k_lower = k.lower()
    if k_lower in ['authorization', 'date', 'host', 'x-content-sha256', 'content-length', 'content-type']:
        print(f"  {k}: {v[:80]}{'...' if len(v) > 80 else ''}")

# =============================================
# AHORA MI FIRMA MANUAL (mismo timestamp)
# =============================================
print("\n" + "="*60)
print("=== MI FIRMA MANUAL (mismo request) ===")

# Usar el mismo date que capturamos del SDK
sdk_date = captured_request.get('headers', {}).get('date', '')
if not sdk_date:
    sdk_date = email.utils.formatdate(usegmt=True)

signing_headers_list = ["(request-target)", "date", "host"]
signing_values = {
    "(request-target)": f"{method.lower()} {path}",
    "date": sdk_date,
    "host": host,
}
signing_string = "\n".join([
    f"{h}: {signing_values[h]}"
    for h in signing_headers_list
])

signature = private_key.sign(
    signing_string.encode("ascii"),
    padding.PKCS1v15(),
    hashes.SHA256()
)
my_signature_b64 = base64.b64encode(signature).decode("ascii")

my_auth_header = (
    f'Signature version="1",algorithm="SHA256withRSA",'
    f'keyId="{key_id}",signature="{my_signature_b64}",'
    f'headers="{" ".join(signing_headers_list)}"'
)

print(f"Signing string:")
print(repr(signing_string))
print(f"\nMi Authorization header:")
for part in my_auth_header.split(","):
    print(f"  {part}")

# =============================================
# COMPARAR
# =============================================
print("\n" + "="*60)
print("=== COMPARACIÓN ===")

sdk_auth = captured_request.get('headers', {}).get('Authorization', '')
print(f"\nSDK Authorization (primeros 200 chars):")
print(sdk_auth[:200])

print(f"\nMi Authorization (primeros 200 chars):")
print(my_auth_header[:200])

# Comparar signature
import re
sdk_sig_match = re.search(r'signature="([^"]+)"', sdk_auth)
my_sig_match = re.search(r'signature="([^"]+)"', my_auth_header)

if sdk_sig_match and my_sig_match:
    sdk_sig = sdk_sig_match.group(1)
    my_sig = my_sig_match.group(1)
    print(f"\nSDK signature length: {len(sdk_sig)}")
    print(f"Mi signature length: {len(my_sig)}")
    print(f"Signatures iguales: {sdk_sig == my_sig}")
    if sdk_sig != my_sig:
        print(f"\nSDK signature: {sdk_sig[:40]}...")
        print(f"Mi signature: {my_sig[:40]}...")

# Comparar keyId
sdk_keyid_match = re.search(r'keyId="([^"]+)"', sdk_auth)
my_keyid_match = re.search(r'keyId="([^"]+)"', my_auth_header)
if sdk_keyid_match and my_keyid_match:
    print(f"\nSDK keyId: {sdk_keyid_match.group(1)}")
    print(f"Mi keyId: {my_keyid_match.group(1)}")
    print(f"keyIds iguales: {sdk_keyid_match.group(1) == my_keyid_match.group(1)}")
