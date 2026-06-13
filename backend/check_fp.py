import os
from app.core.config import settings
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import base64
import hashlib

key_content = settings.OCI_KEY_CONTENT
literal_n = chr(92) + chr(110)
real_nl = chr(10)
if literal_n in key_content and real_nl not in key_content:
    key_content = key_content.replace(literal_n, real_nl)

pk = serialization.load_pem_private_key(key_content.encode(), password=None, backend=default_backend())
pub_der = pk.public_key().public_bytes(
    serialization.Encoding.DER,
    serialization.PublicFormat.SubjectPublicKeyInfo
)
sha = hashlib.sha256(pub_der).digest()
md5 = hashlib.md5(pub_der).hexdigest()
# OCI uses colon-separated MD5 fingerprint
fingerprint = ':'.join(md5[i:i+2] for i in range(0, len(md5), 2))
cfg_fp = settings.oci.get("fingerprint", "")
print(f"Computed fingerprint: {fingerprint}")
print(f"Config fingerprint:   {cfg_fp}")
print(f"Match: {fingerprint.upper() == cfg_fp.upper()}")
