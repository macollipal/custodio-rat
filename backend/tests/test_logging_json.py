"""
Tests de logging estructurado JSON.

Valida que JSONFormatter se activa en production, qa y staging
(no solo production), y que el formato texto se usa en development.
Tambien valida que request_id se incluye en cada log (Z-06).
"""
import json
import logging
import os

import pytest


@pytest.fixture(autouse=True)
def restore_env():
    """Restaura ENVIRONMENT y reconfigura logging despues de cada test."""
    original_env = os.environ.get("ENVIRONMENT")
    yield
    if original_env is None:
        os.environ.pop("ENVIRONMENT", None)
    else:
        os.environ["ENVIRONMENT"] = original_env
    from app.core.logging_config import setup_logging
    setup_logging()


def _capture_log(env_value, message="test_log_message"):
    """Helper: setea env, reconfigura logging, emite un log y retorna el record."""
    if env_value is None:
        os.environ.pop("ENVIRONMENT", None)
    else:
        os.environ["ENVIRONMENT"] = env_value
    from app.core.logging_config import setup_logging
    setup_logging()
    logger = logging.getLogger("test_logger_xyz")
    logger.info(message)
    for h in logging.getLogger().handlers:
        if hasattr(h, "stream"):
            h.flush()
    return message


def test_json_formatter_active_in_production(capsys):
    """ENVIRONMENT=production usa JSONFormatter (parseable)."""
    _capture_log("production")
    captured = capsys.readouterr()
    lines = [ln for ln in captured.out.splitlines() if ln.startswith("{")]
    assert len(lines) >= 1, "Debio emitir al menos un log JSON"
    parsed = json.loads(lines[0])
    assert parsed["level"] == "INFO"
    assert parsed["message"] == "test_log_message"
    assert "request_id" in parsed
    assert "timestamp" in parsed
    assert "logger" in parsed


def test_json_formatter_active_in_qa(capsys):
    """ENVIRONMENT=qa usa JSONFormatter (Z-06 fix)."""
    _capture_log("qa")
    captured = capsys.readouterr()
    lines = [ln for ln in captured.out.splitlines() if ln.startswith("{")]
    assert len(lines) >= 1, "QA debe emitir JSON (no solo production)"
    parsed = json.loads(lines[0])
    assert parsed["level"] == "INFO"


def test_json_formatter_active_in_staging(capsys):
    """ENVIRONMENT=staging usa JSONFormatter."""
    _capture_log("staging")
    captured = capsys.readouterr()
    lines = [ln for ln in captured.out.splitlines() if ln.startswith("{")]
    assert len(lines) >= 1, "Staging debe emitir JSON"
    parsed = json.loads(lines[0])
    assert parsed["level"] == "INFO"


def test_text_formatter_in_development(capsys):
    """ENVIRONMENT=development usa formato texto legible."""
    _capture_log("development")
    captured = capsys.readouterr()
    lines = [ln for ln in captured.out.splitlines() if ln.strip()]
    assert len(lines) >= 1
    has_json = any(ln.startswith("{") for ln in lines)
    assert not has_json, "Development NO debe emitir JSON"
    assert any("test_log_message" in ln for ln in lines)


def test_text_formatter_when_env_unset(capsys):
    """Sin ENVIRONMENT (default) usa formato texto (no rompe en local)."""
    _capture_log(None)
    captured = capsys.readouterr()
    lines = [ln for ln in captured.out.splitlines() if ln.strip()]
    assert len(lines) >= 1
    has_json = any(ln.startswith("{") for ln in lines)
    assert not has_json, "Sin env var debe ser texto legible"


def test_json_log_has_request_id(capsys):
    """Cada log JSON incluye el campo request_id."""
    _capture_log("qa")
    captured = capsys.readouterr()
    lines = [ln for ln in captured.out.splitlines() if ln.startswith("{")]
    assert len(lines) >= 1
    parsed = json.loads(lines[0])
    assert "request_id" in parsed
    assert isinstance(parsed["request_id"], str)
    assert len(parsed["request_id"]) >= 1


def test_json_log_includes_exception_when_set(capsys):
    """Si hay exc_info, el JSON incluye el campo 'exception'."""
    if "ENVIRONMENT" in os.environ:
        del os.environ["ENVIRONMENT"]
    os.environ["ENVIRONMENT"] = "qa"
    from app.core.logging_config import setup_logging
    setup_logging()
    logger = logging.getLogger("test_exception_logger")
    try:
        raise ValueError("test_exception_value")
    except ValueError:
        logger.exception("an_error_happened")
    captured = capsys.readouterr()
    lines = [ln for ln in captured.out.splitlines() if ln.startswith("{")]
    assert len(lines) >= 1
    parsed = json.loads(lines[0])
    assert parsed["message"] == "an_error_happened"
    assert "exception" in parsed
    assert "test_exception_value" in parsed["exception"]
