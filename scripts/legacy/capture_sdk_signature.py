"""
Capturar la firma exacta que produce el OCI SDK para comparar con la implementación manual.
"""
import os
import base64
import hashlib
import email.utils
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend

# Cargar clave
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

# Parametros
tenancy = cfg["tenancy"]
user = cfg["user"]
fingerprint = cfg["fingerprint"]
key_id = f"{tenancy}/{user}/{fingerprint}"
region = cfg["region"]
host = f"objectstorage.{region}.oraclecloud.com"
namespace = cfg["namespace"]
bucket = cfg["bucket"]

# Request que queremos firmar
method = "GET"
path = f"/n/{namespace}/b/{bucket}/o"

# Firmar con el METODO DEL SDK (httpsig_cffi internamente)
# Primero necesito ver como lo hace el SDK
import oci
from oci import Signer as OCISigner

# Crear el signer del SDK
oci_signer = OCISigner(
    key_content.encode(),
    fingerprint,
    tenancy,
    user
)

# El signer del SDK tiene una propiedad 'scope' o similar?
print("=== OCI SDK Signer ===")
print(f"Tipo: {type(oci_signer)}")
print(f"Dir: {[x for x in dir(oci_signer) if not x.startswith('_')]}")

# Intentar acceder al signer interno
if hasattr(oci_signer, '_signer'):
    print(f"Signer interno: {type(oci_signer._signer)}")
    print(f"Signer interno dir: {[x for x in dir(oci_signer._signer) if not x.startswith('_')]}")

# Si el SDK usa httpsig_cffi, podemos acceder a la clave privada
# y ver como firma
print("\n=== Mi implementación manual ===")

# Mi signing string
date_str = email.utils.formatdate(usegmt=True)
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

print(f"Signing string (mío):")
print(repr(signing_string))

# Mi firma
message = signing_string.encode("ascii")
signature = private_key.sign(
    message,
    padding.PKCS1v15(),
    hashes.SHA256()
)
my_signature_b64 = base64.b64encode(signature).decode("ascii")
print(f"\nMi firma (base64): {my_signature_b64[:60]}...")
print(f"Largo de mi firma: {len(my_signature_b64)}")

# Ahora quiero ver que firma produce el SDK
# Puedo usar el debugger de requests para ver los headers que envia
import requests

# Crear una request para ver que headers genera el SDK
from oci.object_storage.object_storage_client import ObjectStorageClient

object_storage = ObjectStorageClient({
    "tenancy": tenancy,
    "user": user,
    "fingerprint": fingerprint,
    "key_content": key_content,
    "region": region,
})

# En lugar de hacer la request, podemos usar el signer directamente
# para firmar un mensaje de prueba
print("\n=== Comparación ===")

# Obtener el signing string del SDK (si es posible)
# El OCI SDK usa HMAC-like signing para la mayoria de casos pero para
# Object Storage usa firma RSA directa

# Vamos a hacer una request real pero con un proxy que capture los headers
import http.server
import threading
import json

captured_headers = {}
captured = threading.Event()

class ProxyHandler(http.server.BaseHTTPRequestHandler):
    def do_CONNECT(self):
        self.wfile.write(b"HTTP/1.1 501 Not Implemented\r\n\r\n")

    def log_message(self, format, *args):
        pass  # Silenciar logs

    def do_GET(self):
        global captured_headers, captured
        captured_headers = dict(self.headers)
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"status": "captured"}')
        captured.set()

# Iniciar proxy en puerto 8899
proxy_server = http.server.HTTPServer(('localhost', 8899), ProxyHandler)
proxy_thread = threading.Thread(target=proxy_server.handle_request)
proxy_thread.start()

# Configurar SDK para usar proxy
import os
os.environ['http_proxy'] = 'http://localhost:8899'
os.environ['https_proxy'] = 'http://localhost:8899'

try:
    resp = object_storage.list_objects(namespace_name=namespace, bucket_name=bucket)
except Exception as e:
    if not captured.is_set():
        proxy_thread.join(timeout=5)

print(f"Headers capturados: {len(captured_headers)}")
for k, v in captured_headers.items():
    if k.lower() in ['authorization', 'date', 'host']:
        print(f"  {k}: {v[:100]}{'...' if len(v) > 100 else ''}")

# Limpiar proxy
os.environ.pop('http_proxy', None)
os.environ.pop('https_proxy', None)
