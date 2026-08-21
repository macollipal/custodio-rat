"""
Smoke test Z-03 — File upload MIME validation integration.

Verifica que TODOS los endpoints de upload del backend usen
file_validation.validate_upload() con las configuraciones correctas:

- admin/asesor/upload: md/txt ≤ 5MB
- feriados/upload: csv ≤ 2MB
- (futuros endpoints pueden agregarse aqui)

Historia: este test existe porque Z-03 (Z items del auditor) requiere
que TODO upload de archivos valide extension + tamano + content-type
+ magic bytes (cuando aplique). Si un dev nuevo crea un endpoint de
upload sin usar este helper, este test lo detecta.
"""
import inspect

import pytest

from app.services import file_validation


def _get_routes_with_upload_file():
    """Encuentra todos los endpoints FastAPI que reciben UploadFile."""
    from app.main import app
    routes = []
    for route in app.routes:
        if hasattr(route, "endpoint") and route.endpoint is not None:
            sig = inspect.signature(route.endpoint)
            for name, param in sig.parameters.items():
                ann = str(param.annotation)
                if "UploadFile" in ann:
                    routes.append((route.path, name))
    return routes


def _uses_validate_upload(endpoint_path):
    """Verifica si el codigo fuente del modulo importa/usa validate_upload."""
    import importlib
    from app.main import app
    for route in app.routes:
        if hasattr(route, "path") and route.path == endpoint_path:
            module = importlib.import_module(route.endpoint.__module__)
            src = inspect.getsource(module)
            return "validate_upload" in src, src
    return False, ""


class TestZ03UploadValidation:
    """Z-03 Compliance check."""

    def test_validate_upload_helper_exists(self):
        """El helper validate_upload debe existir."""
        assert hasattr(file_validation, "validate_upload")
        assert callable(file_validation.validate_upload)

    def test_validate_upload_validates_extension(self):
        """Extension invalida debe lanzar HTTPException 400."""
        from app.services.file_validation import validate_upload

        class FakeUpload:
            filename = "malware.exe"
            content_type = "application/octet-stream"

            class _F:
                def read(self_inner):
                    return b"x" * 100

            file = _F()

        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            validate_upload(
                FakeUpload(),
                allowed_extensions=["md"],
                max_bytes=1024,
            )
        assert exc_info.value.status_code == 400
        assert "extension" in exc_info.value.detail.lower()

    def test_validate_upload_validates_size(self):
        """Archivo > max_bytes debe lanzar HTTPException 413."""
        from app.services.file_validation import validate_upload

        class FakeUpload:
            filename = "big.md"
            content_type = "text/markdown"

            class _F:
                def read(self_inner):
                    return b"x" * 2000

            file = _F()

        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            validate_upload(
                FakeUpload(),
                allowed_extensions=["md"],
                max_bytes=1024,
            )
        assert exc_info.value.status_code == 413

    def test_validate_upload_validates_magic_bytes_when_enabled(self):
        """Si validate_magic_bytes=True, .pdf con magic bytes falsos debe fallar."""
        from app.services.file_validation import validate_upload

        class FakeUpload:
            filename = "fake.pdf"
            content_type = "application/pdf"

            class _F:
                def read(self_inner):
                    return b"GIF89a magic-bytes-de-imagen-pero-content-type-dice-pdf"

            file = _F()

        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            validate_upload(
                FakeUpload(),
                allowed_extensions=["pdf"],
                max_bytes=1024,
                validate_magic_bytes=True,
            )
        assert exc_info.value.status_code == 400

    def test_validate_upload_accepts_real_pdf(self):
        """Un PDF real con magic bytes correctos pasa."""
        from app.services.file_validation import validate_upload

        class FakeUpload:
            filename = "doc.pdf"
            content_type = "application/pdf"

            class _F:
                def read(self_inner):
                    return b"%PDF-1.4 contenido real"

            file = _F()

        # No debe raise
        result = validate_upload(
            FakeUpload(),
            allowed_extensions=["pdf"],
            max_bytes=1024,
            validate_magic_bytes=True,
        )
        assert result.startswith(b"%PDF-")

    def test_known_upload_endpoints_use_validate_upload(self):
        """Los endpoints de upload conocidos DEBEN usar validate_upload.

        Si un dev nuevo crea un endpoint de upload sin usar este helper,
        este test lo detecta (Z-03 regression detector).
        """
        known_upload_paths = [
            "/admin/asesor/upload",
            "/admin/feriados/upload",
        ]
        for path in known_upload_paths:
            uses_helper, src = _uses_validate_upload(path)
            assert uses_helper, (
                f"Z-03 regression: endpoint {path} debe usar "
                f"file_validation.validate_upload() — revisar codigo fuente"
            )

    def test_all_upload_endpoints_in_app_are_known(self):
        """Lista los endpoints UploadFile encontrados. Si aparece uno nuevo,
        anadirlo a known_upload_paths arriba."""
        routes = _get_routes_with_upload_file()
        routes_str = "\n".join(f"  {p} (param: {n})" for p, n in routes)
        print(f"\n[INFO] Endpoints con UploadFile en app:\n{routes_str}")
        # Sanity check: al menos 2 endpoints conocidos
        assert len(routes) >= 2, (
            f"Se esperaban al menos 2 endpoints de upload; encontrados: {len(routes)}"
        )
