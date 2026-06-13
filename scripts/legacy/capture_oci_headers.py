"""
Capture the actual HTTP request that the OCI SDK sends.
"""
import os
import oci
import logging
from app.core.config import settings

# Enable OCI SDK debug logging
logging.basicConfig(level=logging.DEBUG)
oci_logger = logging.getLogger("oci")
oci_logger.setLevel(logging.DEBUG)

cfg = settings.oci
key_content = settings.OCI_KEY_CONTENT
literal_n = chr(92) + chr(110)
real_nl = chr(10)
if literal_n in key_content and real_nl not in key_content:
    key_content = key_content.replace(literal_n, real_nl)

key_file = "C:\\Users\\chelo\\AppData\\Local\\Temp\\opencode\\oci_test_key.pem"
os.makedirs(os.path.dirname(key_file), exist_ok=True)
with open(key_file, "w") as f:
    f.write(key_content)

oci_config = {
    "tenancy": cfg["tenancy"],
    "user": cfg["user"],
    "fingerprint": cfg["fingerprint"],
    "key_file": key_file,
    "region": cfg["region"],
}

# Intercept the request to see headers
original_request = None

def capture_request(request, **kwargs):
    global original_request
    original_request = request
    print("\n=== OCI SDK Request ===")
    print(f"Method: {request.method}")
    print(f"URL: {request.url}")
    print("Headers:")
    for k, v in request.headers.items():
        print(f"  {k}: {v[:100]}{'...' if len(v) > 100 else ''}")
    raise Exception("STOP_HERE")  # Don't actually send

# Monkey-patch the session
import oci.base_client
original_call = oci.base_client.BaseClient.call_api

def patched_call_api(self, request, *args, **kwargs):
    print("\n=== OCI SDK Request (patched) ===")
    print(f"Method: {request.method}")
    print(f"URL: {request.url}")
    print("Headers:")
    for k, v in request.headers.items():
        print(f"  {k}: {v[:100]}{'...' if len(v) > 100 else ''}")
    raise Exception("STOP_HERE")

oci.base_client.BaseClient.call_api = patched_call_api

try:
    object_storage = oci.object_storage.ObjectStorageClient(oci_config)
    namespace = object_storage.get_namespace().data
    print(f"Namespace: {namespace}")
    buckets = object_storage.list_buckets(namespace_name=namespace, compartment_id=cfg["tenancy"])
except Exception as e:
    if str(e) != "STOP_HERE":
        print(f"Error: {e}")
