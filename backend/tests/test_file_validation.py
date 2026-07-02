"""
Tests de Z-03: file upload validation (extension + tamano).

Cubre:
- Extension valida pasa
- Extension invalida retorna 400
- Sin extension retorna 400
- Tamano excedido retorna 413
- Tamano justo debajo del limite pasa
- Content-Type mismatch retorna 400
"""
import io
import pytest
from fastapi import UploadFile

from app.services.file_validation import validate_upload


def _make_upload(filename: str, content: bytes, content_type: str = "text/plain") -> UploadFile:
    return UploadFile(filename=filename, file=io.BytesIO(content), headers={"content-type": content_type})


class TestExtensionValidation:
    def test_valid_extension_passes(self):
        """Extension valida (md) pasa el filtro."""
        upload = _make_upload("test.md", b"# content")
        content = validate_upload(upload, allowed_extensions=["md", "txt"], max_bytes=1024)
        assert content == b"# content"

    def test_invalid_extension_raises_400(self):
        """Extension invalida (exe) levanta 400."""
        upload = _make_upload("malware.exe", b"x" * 100)
        with pytest.raises(Exception) as exc_info:
            validate_upload(upload, allowed_extensions=["md", "txt"], max_bytes=1024)
        assert exc_info.value.status_code == 400
        assert "exe" in exc_info.value.detail.lower() or "extension" in exc_info.value.detail.lower()

    def test_no_extension_raises_400(self):
        """Archivo sin extension levanta 400."""
        upload = _make_upload("README", b"x")
        with pytest.raises(Exception) as exc_info:
            validate_upload(upload, allowed_extensions=["md"], max_bytes=1024)
        assert exc_info.value.status_code == 400

    def test_uppercase_extension_normalized(self):
        """Extension en mayusculas (MD) es aceptada."""
        upload = _make_upload("test.MD", b"x")
        content = validate_upload(upload, allowed_extensions=["md"], max_bytes=1024)
        assert content == b"x"

    def test_multiple_allowed_extensions(self):
        """Lista de extensiones validas se respetan."""
        for ext in ["md", "txt", "csv"]:
            upload = _make_upload(f"file.{ext}", b"x")
            content = validate_upload(upload, allowed_extensions=["md", "txt", "csv"], max_bytes=1024)
            assert content == b"x"


class TestSizeValidation:
    def test_size_under_limit_passes(self):
        """Tamano bajo el limite pasa."""
        upload = _make_upload("test.md", b"x" * 500)
        content = validate_upload(upload, allowed_extensions=["md"], max_bytes=1024)
        assert len(content) == 500

    def test_size_exactly_at_limit_passes(self):
        """Tamano exacto al limite pasa."""
        upload = _make_upload("test.md", b"x" * 1024)
        content = validate_upload(upload, allowed_extensions=["md"], max_bytes=1024)
        assert len(content) == 1024

    def test_size_over_limit_raises_413(self):
        """Tamano sobre el limite levanta 413."""
        upload = _make_upload("test.md", b"x" * 2000)
        with pytest.raises(Exception) as exc_info:
            validate_upload(upload, allowed_extensions=["md"], max_bytes=1024)
        assert exc_info.value.status_code == 413
        assert "demasiado grande" in exc_info.value.detail.lower() or "mb" in exc_info.value.detail.lower()

    def test_size_realistic_max(self):
        """Test con 5MB (limite del Asesor upload)."""
        upload = _make_upload("big.md", b"x" * (5 * 1024 * 1024))  # 5MB exactos
        content = validate_upload(upload, allowed_extensions=["md"], max_bytes=5 * 1024 * 1024)
        assert len(content) == 5 * 1024 * 1024

    def test_size_just_over_5mb_raises(self):
        """Test con 5MB + 1 byte levanta 413."""
        upload = _make_upload("big.md", b"x" * (5 * 1024 * 1024 + 1))
        with pytest.raises(Exception) as exc_info:
            validate_upload(upload, allowed_extensions=["md"], max_bytes=5 * 1024 * 1024)
        assert exc_info.value.status_code == 413


class TestContentTypeValidation:
    def test_content_type_prefix_passes(self):
        """Content-Type que empieza con prefijo esperado pasa."""
        upload = _make_upload("test.md", b"x", content_type="text/markdown")
        content = validate_upload(
            upload,
            allowed_extensions=["md"],
            max_bytes=1024,
            check_content_type_prefix="text/",
        )
        assert content == b"x"

    def test_content_type_mismatch_raises_400(self):
        """Content-Type que NO coincide con prefijo esperado levanta 400."""
        upload = _make_upload("test.md", b"x", content_type="application/octet-stream")
        with pytest.raises(Exception) as exc_info:
            validate_upload(
                upload,
                allowed_extensions=["md"],
                max_bytes=1024,
                check_content_type_prefix="text/",
            )
        assert exc_info.value.status_code == 400
        assert "content-type" in exc_info.value.detail.lower()

    def test_no_content_type_with_check_skips_validation(self):
        """Si content_type es None y check esta activo, no falla (skip)."""
        upload = UploadFile(filename="test.md", file=io.BytesIO(b"x"))
        content = validate_upload(
            upload,
            allowed_extensions=["md"],
            max_bytes=1024,
            check_content_type_prefix="text/",
        )
        assert content == b"x"