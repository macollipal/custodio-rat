"""
Comparar los headers de mi firma vs la firma del SDK.
Hago una request real con el SDK y capturo los headers que envía.
"""
import base64
import email.utils
import hashlib
import requests
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

# ========================================
# MI FIRMA MANUAL
# ========================================
date_str = email.utils.formatdate(usegmt=True)
signing_headers_list = ["(request-target)", "date", "host"]
signing_values = {
    "(request-target)": f"{method.lower()} {path}",
    "date": date_str,
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

my_headers = {
    "Host": host,
    "Date": date_str,
    "Authorization": (
        f'Signature version="1",algorithm="SHA256withRSA",'
        f'keyId="{key_id}",signature="{my_signature_b64}",'
        f'headers="{" ".join(signing_headers_list)}"'
    )
}

print("=== MI FIRMA MANUAL ===")
print(f"URL: {url}")
print(f"Signing string:")
print(repr(signing_string))
print(f"\nHeaders que YO envío:")
for k, v in my_headers.items():
    if k == "Authorization":
        print(f"  {k}:")
        # Mostrar el Authorization header en partes legibles
        parts = v.split(",")
        for part in parts:
            print(f"    {part}")
    else:
        print(f"  {k}: {v}")

# ========================================
# FIRMA DEL SDK (interceptando la request)
# ========================================
print("\n" + "="*50)
print("=== FIRMA DEL SDK (OCI official) ===")

import oci
from oci.object_storage.object_storage_client import ObjectStorageClient

# Necesito interceptar la request del SDK
# Voy a usar un approach diferente: hacer la request con el SDK
# pero con un transport adaptation que capture los headers

# Alternativa: usar requests-tracker o similar
# Pero la forma mas simple es parchear el metodo _sign_request del SDK

from oci import Signer as OCISigner
from oci.base_client import BaseClient

# Guardar el metodo original
original_sign_request = BaseClient._sign_request

def patched_sign_request(self, request, *args, **kwargs):
    # Interceptar justo antes de firmar
    global sdk_request_info
    sdk_request_info = {
        'method': request.method,
        'url': request.url,
        'headers': dict(request.headers),
    }
    return original_sign_request(self, request, *args, **kwargs)

BaseClient._sign_request = patched_sign_request

# Ahora hacer la request con el SDK
sdk_config = {
    "tenancy": tenancy,
    "user": user,
    "fingerprint": fingerprint,
    "key_content": key_content,
    "region": region,
}

sdk_client = ObjectStorageClient(sdk_config)
try:
    result = sdk_client.list_objects(
        namespace_name=namespace,
        bucket_name=bucket
    )
    print(f"SDK Request successful: {len(result.data.objects)} objects")
except Exception as e:
    print(f"SDK Error: {e}")

# Restaurar
BaseClient._sign_request = original_sign_request

# Mostrar lo que capturamos
if 'sdk_request_info' in globals():
    print(f"\nHeaders que el SDK envía:")
    for k, v in sdk_request_info['headers'].items():
        if k.lower() in ['authorization', 'date', 'host'] or k.lower() == 'x-content-sha256':
            print(f"  {k}: {v[:100]}{'...' if len(v) > 100 else ''}")
else:
    print("No pude capturar los headers del SDK")

# ========================================
# TEST: hacer request con MI FIRMA vs SDK FIRMA
# ========================================
print("\n" + "="*50)
print("=== TEST COMPARATIVO ===")

# Mi request
resp_mi_firma = requests.get(url, headers=my_headers, timeout=10)
print(f"Request con MI firma: {resp_mi_firma.status_code}")

# Request del SDK (replicando sus headers)
if 'sdk_request_info' in globals():
    resp_sdk_firma = requests.get(
        sdk_request_info['url'],
        headers=sdk_request_info['headers'],
        timeout=10
    )
    print(f"Request con SDK firma: {resp_sdk_firma.status_code}")
