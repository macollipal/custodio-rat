"""
Abstracción de almacenamiento para archivos RAT.
Soporta: local (default) y OCI Object Storage via REST API + firma RSA manual.
Usa cryptography (ya instalada) + requests (ya instalada). Sin SDK Oracle.
"""

import base64
import email.utils
import hashlib
import json
import logging
import os
import time
import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timezone, timedelta
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
            "Host": host,
            "Date": date_str,
        }

        signing_headers = ["date", "(request-target)", "host"]
        signing_values = {
            "(request-target)": f"{method.lower()} {path}",
            "date": date_str,
            "host": host,
        }

        if body:
            m = hashlib.sha256()
            m.update(body)
            sha256_digest = base64.b64encode(m.digest()).decode("ascii")
            headers["Content-Length"] = str(len(body))
            headers["Content-Type"] = "application/octet-stream"
            headers["X-Content-Sha256"] = sha256_digest
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
            f'Signature algorithm="rsa-sha256",'
            f'headers="{" ".join(signing_headers)}",'
            f'keyId="{self.key_id}",'
            f'signature="{signature}",'
            f'version="1"'
        )
        headers["Authorization"] = auth
        return headers


class OCIStorageBackend(StorageBackend):
    def __init__(self, config: dict, key_content: str):
        self.namespace = config["namespace"]
        self.region = config["region"]
        self.bucket = config["bucket"]
        self.archive_bucket = config.get("archive_bucket", "")
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

    def create_presigned_url(self, object_name: str, expires_in_seconds: int = 300) -> str:
        """Genera una pre-signed URL para descarga directa desde OCI.

        Args:
            object_name: Nombre del objeto en el bucket
            expires_in_seconds: Tiempo de expiración (default 5 minutos)

        Returns:
            URL pre-firmada para descarga directa
        """
        import json
        from datetime import datetime, timezone, timedelta

        if not self.archive_bucket:
            target_bucket = self.bucket
        else:
            target_bucket = self.bucket

        path = f"/n/{self.namespace}/b/{target_bucket}/p"
        time_expires = (datetime.now(timezone.utc) + timedelta(seconds=expires_in_seconds)).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

        payload = json.dumps({
            "objectName": object_name,
            "accessType": "ObjectRead",
            "timeExpires": time_expires
        })

        resp = self._request("POST", path, payload.encode(), "application/json")
        if resp.status_code not in (200, 201):
            logger.error(f"OCI presigned URL failed: {resp.status_code} {resp.text}")
            raise Exception(f"OCI presigned URL failed: {resp.status_code}")

        result = resp.json()
        return result.get("accessUri", "")

    def copy_to_archive(self, object_name: str, archive_prefix: str = "archived") -> str:
        """Copia un objeto al bucket de archive.

        Args:
            object_name: Nombre del objeto en el bucket activo
            archive_prefix: Prefijo para el objeto en archive (default 'archived')

        Returns:
            Nombre del objeto en el bucket archive
        """
        if not self.archive_bucket:
            logger.warning("No archive_bucket configured, skipping archive copy")
            return object_name

        archive_object_name = f"{archive_prefix}/{object_name}"

        source_path = f"/n/{self.namespace}/b/{self.bucket}/o/{quote(object_name, safe='')}"
        dest_path = f"/n/{self.namespace}/b/{self.archive_bucket}/o/{quote(archive_object_name, safe='')}"

        copy_payload = json.dumps({
            "destination": dest_path,
            "metadata": {
                "copied-from": object_name,
                "archived-at": datetime.now(timezone.utc).isoformat()
            }
        })

        resp = self._request("POST", source_path + "/actions/copy", copy_payload.encode(), "application/json")
        if resp.status_code not in (200, 201):
            logger.error(f"OCI copy to archive failed: {resp.status_code} {resp.text}")
            raise Exception(f"OCI copy to archive failed: {resp.status_code}")

        logger.info(f"Copied {object_name} to archive bucket as {archive_object_name}")
        return archive_object_name

    def delete_from_archive(self, archive_object_name: str) -> None:
        """Elimina un objeto del bucket de archive.

        Args:
            archive_object_name: Nombre del objeto en el bucket archive
        """
        if not self.archive_bucket:
            raise ValueError("No archive_bucket configured")

        path = f"/n/{self.namespace}/b/{self.archive_bucket}/o/{quote(archive_object_name, safe='')}"
        resp = self._request("DELETE", path)
        if resp.status_code not in (204, 404):
            logger.error(f"OCI delete from archive failed: {resp.status_code} {resp.text}")
            raise Exception(f"OCI delete from archive failed: {resp.status_code}")
        logger.info(f"Deleted {archive_object_name} from archive bucket")

    def list_archive_objects(self, prefix: str = "") -> list[dict]:
        """Lista objetos en el bucket de archive.

        Returns:
            Lista de diccionarios con name, size, created_time, etc.
        """
        if not self.archive_bucket:
            return []

        path = f"/n/{self.namespace}/b/{self.archive_bucket}/o/"
        if prefix:
            path += f"?prefix={quote(prefix, safe='')}"

        resp = self._request("GET", path)
        if resp.status_code != 200:
            logger.error(f"OCI list archive failed: {resp.status_code} {resp.text}")
            return []

        import xml.etree.ElementTree as ET
        root = ET.fromstring(resp.content)
        objects = []
        for obj in root.findall(".//object"):
            name = obj.find("name")
            size = obj.find("size")
            created = obj.find("timeCreated")
            objects.append({
                "name": name.text if name is not None else "",
                "size": int(size.text) if size is not None and size.text else 0,
                "created": created.text if created is not None else ""
            })
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
