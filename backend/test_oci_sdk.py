"""
Test OCI credentials using the OCI SDK to verify they work.
"""
import os
import oci
from app.core.config import settings

cfg = settings.oci
key_content = settings.OCI_KEY_CONTENT
literal_n = chr(92) + chr(110)
real_nl = chr(10)
if literal_n in key_content and real_nl not in key_content:
    key_content = key_content.replace(literal_n, real_nl)

# Write key to temp file (OCI SDK needs a file)
key_file = "C:\\Users\\chelo\\AppData\\Local\\Temp\\opencode\\oci_test_key.pem"
os.makedirs(os.path.dirname(key_file), exist_ok=True)
with open(key_file, "w") as f:
    f.write(key_content)

# Create OCI config dict
oci_config = {
    "tenancy": cfg["tenancy"],
    "user": cfg["user"],
    "fingerprint": cfg["fingerprint"],
    "key_file": key_file,
    "region": cfg["region"],
}

print(f"Config: {oci_config}")

try:
    # Try to create Object Storage client
    object_storage = oci.object_storage.ObjectStorageClient(oci_config)
    namespace = object_storage.get_namespace().data
    print(f"Namespace: {namespace}")

    # Try to list buckets
    buckets = object_storage.list_buckets(namespace_name=namespace, compartment_id=cfg["tenancy"])
    print(f"Buckets: {[b.name for b in buckets.data]}")

    # Try to list objects in our bucket
    objects = object_storage.list_objects(namespace_name=namespace, bucket_name=cfg["bucket"])
    print(f"Objects in {cfg['bucket']}: {[o.name for o in objects.data.objects]}")
    print("\n[OK] OCI SDK works with these credentials!")

except Exception as e:
    print(f"\n[FAIL] OCI SDK error: {e}")
    import traceback
    traceback.print_exc()
