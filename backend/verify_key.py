"""
Verify the .pem file fingerprint matches the OCI config.
"""
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import hashlib

# Read the .pem file
with open(r"C:\Users\chelo\.oci\oci_api_key", "rb") as f:
    key_content = f.read()

pk = serialization.load_pem_private_key(key_content, password=None, backend=default_backend())
pub_der = pk.public_key().public_bytes(
    serialization.Encoding.DER,
    serialization.PublicFormat.SubjectPublicKeyInfo
)
md5 = hashlib.md5(pub_der).hexdigest()
fingerprint = ':'.join(md5[i:i+2] for i in range(0, len(md5), 2))
print(f"PEM file fingerprint: {fingerprint}")

# Compare with OCI config
from app.core.config import settings
cfg_fp = settings.oci.get("fingerprint", "")
print(f"Config fingerprint:   {cfg_fp}")
print(f"Match: {fingerprint.upper() == cfg_fp.upper()}")

# Also check OCI_KEY_CONTENT
key_env = settings.OCI_KEY_CONTENT
literal_n = chr(92) + chr(110)
real_nl = chr(10)
if literal_n in key_env and real_nl not in key_env:
    key_env = key_env.replace(literal_n, real_nl)

pk2 = serialization.load_pem_private_key(key_env.encode(), password=None, backend=default_backend())
pub_der2 = pk2.public_key().public_bytes(
    serialization.Encoding.DER,
    serialization.PublicFormat.SubjectPublicKeyInfo
)
md5_2 = hashlib.md5(pub_der2).hexdigest()
fp2 = ':'.join(md5_2[i:i+2] for i in range(0, len(md5_2), 2))
print(f"\nOCI_KEY_CONTENT fingerprint: {fp2}")
print(f"Match with PEM: {fingerprint.upper() == fp2.upper()}")
