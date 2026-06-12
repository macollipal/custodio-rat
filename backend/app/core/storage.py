"""
Abstracci├│n de almacenamiento para archivos RAT.
Soporta: local (default) y OCI Object Storage.
"""

import logging
import os
import uuid
from abc import ABC, abstractmethod
from pathlib import Path

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


class OCIStorageBackend(StorageBackend):
    def __init__(self, config: dict, key_content: str):
        self.namespace = config["namespace"]
        self.region = config["region"]
        self.bucket = config["bucket"]

        import oci
        import os
        import tempfile

        if not key_content:
            raise ValueError("OCI_KEY_CONTENT es requerida para backend OCI")

        if "\\n" in key_content and "\n" not in key_content:
            key_content = key_content.replace("\\n", "\n")

        key_path = "/tmp/oci_api_key"
        with open(key_path, "w") as f:
            f.write(key_content)
        os.chmod(key_path, 0o600)

        oci_config = {
            "tenancy": config["tenancy"],
            "user": config["user"],
            "fingerprint": config["fingerprint"],
            "key_file": key_path,
            "region": config["region"],
        }

        self.client = oci.object_storage.ObjectStorageClient(config=oci_config)

    def upload(self, file_content: bytes, object_name: str, content_type: str = "application/octet-stream") -> str:
        try:
            self.client.put_object(
                namespace_name=self.namespace,
                bucket_name=self.bucket,
                object_name=object_name,
                put_object_body=file_content,
                content_type=content_type
            )
            logger.info(f"Uploaded {object_name} to OCI bucket {self.bucket}")
            return object_name
        except Exception as e:
            logger.error(f"OCI upload failed: {e}")
            raise

    def download(self, object_name: str) -> bytes:
        try:
            response = self.client.get_object(
                namespace_name=self.namespace,
                bucket_name=self.bucket,
                object_name=object_name
            )
            return response.data.content
        except Exception as e:
            logger.error(f"OCI download failed: {e}")
            raise

    def delete(self, object_name: str) -> None:
        try:
            self.client.delete_object(
                namespace_name=self.namespace,
                bucket_name=self.bucket,
                object_name=object_name
            )
            logger.info(f"Deleted {object_name} from OCI bucket {self.bucket}")
        except Exception as e:
            logger.error(f"OCI delete failed: {e}")
            raise

    def get_url(self, object_name: str) -> str:
        return f"https://objectstorage.{self.region}.oraclecloud.com/n/{self.namespace}/b/{self.bucket}/o/{object_name}"

    def list_objects(self, prefix: str = "") -> list[str]:
        try:
            response = self.client.list_objects(
                namespace_name=self.namespace,
                bucket_name=self.bucket,
                prefix=prefix
            )
            return [obj.name for obj in response.data.objects]
        except Exception as e:
            logger.error(f"OCI list failed: {e}")
            raise


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
