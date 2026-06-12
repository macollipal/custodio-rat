"""
Abstracción de almacenamiento para archivos RAT.
Soporta: local (default) y OCI Object Storage via REST API + firma RSA manual.
Usa cryptography (ya instalada) + requests (ya instalada). Sin SDK Oracle.
"""

import base64
import email.utils
import hashlib
import logging
import os
import time
import uuid
from abc import ABC, abstractmethod
from pathlib import Path
from urllib.parse import quote

import requests
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend

logger = logging.getLogger(__name__)


class StorageBackend(ABC):
    @abstractmethod
    def upload(self, file_content: bytes, object_name: str, content_type: str = "application/octet-stream") -> str:
        pass

    @abstractmethod
    def download(self, object_name: str) -> bytes:
        pass

    @abstractmethod
    def delete(self, object_name: str) -> None:
        pass

    @abstractmethod
    def get_url(self, object_name: str) -> str:
        pass


class LocalStorageBackend(StorageBackend):
    def __init__(self, base_dir: str = None):
        if base_dir is None:
            base_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def upload(self, file_content: bytes, object_name: str, content_type: str = "application/octet-stream") -> str:
        file_path = self.base_dir / object_name
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(file_content)
        return object_name

    def download(self, object_name: str) -> bytes:
        file_path = self.base_dir / object_name
        if not file_path.exists():
            raise FileNotFoundError(f"Object {object_name} not found")
        with open(file_path, "rb") as f:
            return f.read()

    def delete(self, object_name: str) -> None:
        file_path = self.base_dir / object_name
        if file_path.exists():
            file_path.unlink()

    def get_url(self, object_name: str) -> str:
        return f"/uploads/{object_name}"


class OCISigner:
    """Firma requests para OCI Object Storage API usando API Signing Key."""

    def __init__(self, tenancy: str, user: str, fingerprint: str, key_content: str, region: str):
        self.key_id = f"{tenancy}/{user}/{fingerprint}"
        self.region = region

        if "\\n" in key_content and "\n" not in key_content:
            key_content = key_content.replace("\\n", "\n")

        self.private_key = serialization.load_pem_private_key(
            key_content.encode(),
            password=None,
            backend=default_backend()
        )

    def _sign(self, message: str) -> str:
        signature = self.private_key.sign(
            message.encode("ascii"),
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        return base64.b64encode(signature).decode("ascii")

    def sign_headers(self, method: str, path: str, host: str, body: bytes = None) -> dict:
        date_str = email.utils.formatdate(usegmt=True)

        headers = {
            "host": host,
            "date": date_str,
        }

        signing_headers = ["(request-target)", "date", "host"]
        signing_values = {
            "(request-target)": f"{method.lower()} {path}",
            "date": date_str,
            "host": host,
        }

        if body:
            m = hashlib.sha256()
            m.update(body)
            sha256_digest = base64.b64encode(m.digest()).decode("ascii")
            headers["content-length"] = str(len(body))
            headers["content-type"] = "application/octet-stream"
            headers["x-content-sha256"] = sha256_digest
            signing_headers.extend(["content-length", "content-type", "x-content-sha256"])
            signing_values["content-length"] = str(len(body))
            signing_values["content-type"] = "application/octet-stream"
            signing_values["x-content-sha256"] = sha256_digest

        signing_string = "\n".join([
            f"{h}: {signing_values[h]}"
            for h in signing_headers
        ])

        signature = self._sign(signing_string)

        auth = (
            f'Signature version="1",'
            f'algorithm="rsa-sha256",'
            f'keyId="{self.key_id}",'
            f'signature="{signature}"'
        )
        headers["Authorization"] = auth
        return headers


class OCIStorageBackend(StorageBackend):
    def __init__(self, config: dict, key_content: str):
        self.namespace = config["namespace"]
        self.region = config["region"]
        self.bucket = config["bucket"]
        self.host = f"objectstorage.{self.region}.oraclecloud.com"
        self.base_url = f"https://{self.host}"

        self.signer = OCISigner(
            tenancy=config["tenancy"],
            user=config["user"],
            fingerprint=config["fingerprint"],
            key_content=key_content,
            region=self.region
        )

    def _request(self, method: str, path: str, data: bytes = None, content_type: str = None) -> dict:
        signed_headers = self.signer.sign_headers(method, path, self.host, data)
        url = f"{self.base_url}{path}"
        resp = requests.request(
            method,
            url,
            data=data,
            headers=signed_headers,
            timeout=30
        )
        return resp

    def upload(self, file_content: bytes, object_name: str, content_type: str = "application/octet-stream") -> str:
        path = f"/n/{self.namespace}/b/{self.bucket}/o/{quote(object_name, safe='')}"
        resp = self._request("PUT", path, file_content, content_type)
        if resp.status_code not in (200, 201):
            logger.error(f"OCI upload failed: {resp.status_code} {resp.text}")
            raise Exception(f"OCI upload failed: {resp.status_code}")
        logger.info(f"Uploaded {object_name} to OCI bucket {self.bucket}")
        return object_name

    def download(self, object_name: str) -> bytes:
        path = f"/n/{self.namespace}/b/{self.bucket}/o/{quote(object_name, safe='')}"
        resp = self._request("GET", path)
        if resp.status_code == 404:
            raise FileNotFoundError(f"Object {object_name} not found in OCI")
        if resp.status_code != 200:
            logger.error(f"OCI download failed: {resp.status_code} {resp.text}")
            raise Exception(f"OCI download failed: {resp.status_code}")
        return resp.content

    def delete(self, object_name: str) -> None:
        path = f"/n/{self.namespace}/b/{self.bucket}/o/{quote(object_name, safe='')}"
        resp = self._request("DELETE", path)
        if resp.status_code not in (204, 404):
            logger.error(f"OCI delete failed: {resp.status_code} {resp.text}")
            raise Exception(f"OCI delete failed: {resp.status_code}")
        logger.info(f"Deleted {object_name} from OCI bucket {self.bucket}")

    def get_url(self, object_name: str) -> str:
        return f"https://objectstorage.{self.region}.oraclecloud.com/n/{self.namespace}/b/{self.bucket}/o/{quote(object_name, safe='')}"

    def list_objects(self, prefix: str = "") -> list[str]:
        path = f"/n/{self.namespace}/b/{self.bucket}/o/"
        if prefix:
            path += f"?prefix={quote(prefix, safe='')}"
        resp = self._request("GET", path)
        if resp.status_code != 200:
            logger.error(f"OCI list failed: {resp.status_code} {resp.text}")
            raise Exception(f"OCI list failed: {resp.status_code}")
        import xml.etree.ElementTree as ET
        root = ET.fromstring(resp.content)
        objects = []
        for obj in root.findall(".//object"):
            name = obj.text
            if name:
                objects.append(name)
        return objects


def get_storage_backend() -> StorageBackend:
    from app.core.config import settings

    cfg = settings.oci
    backend = cfg.get("backend", "local")

    if backend == "oci":
        required = ["namespace", "region", "bucket", "tenancy", "user", "fingerprint"]
        missing = [k for k in required if not cfg.get(k)]
        if missing:
            raise ValueError(f"OCI config incompleta: faltan {missing}")
        if not settings.OCI_KEY_CONTENT:
            raise ValueError("OCI_KEY_CONTENT es requerida")

        return OCIStorageBackend(config=cfg, key_content=settings.OCI_KEY_CONTENT)

    return LocalStorageBackend()


def generate_object_name(prefix: str, original_filename: str) -> str:
    ext = Path(original_filename).suffix.lower()
    unique = uuid.uuid4().hex[:12]
    return f"{prefix}/{unique}{ext}"
