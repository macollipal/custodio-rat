"""
Tests para validacion EIPD obligatoria con justificacion documentada (Art. 15 bis Ley 21.719).
Cubre _validar_eipd_obligatoria() de rat_service.py.
"""
import pytest
from fastapi import HTTPException

from app.services.rat_service import _validar_eipd_obligatoria


class TestValidarEipdObligatoria:
    """Tests de unidad sobre la funcion _validar_eipd_obligatoria."""

    def test_datos_sensibles_sin_eipd_falla(self):
        """datos_sensibles=True sin evaluacion_impacto debe lanzar 422."""
        data = {
            "datos_sensibles": True,
            "transferencia_internacional": False,
            "estado_eipd": "no_requerida",
            "evaluacion_impacto": False,
        }
        with pytest.raises(HTTPException) as exc_info:
            _validar_eipd_obligatoria(data)
        assert exc_info.value.status_code == 422
        assert "EIPD" in exc_info.value.detail

    def test_transferencia_internacional_sin_eipd_falla(self):
        """transferencia_internacional=True sin EIPD debe lanzar 422."""
        data = {
            "datos_sensibles": False,
            "transferencia_internacional": True,
            "estado_eipd": "no_requerida",
            "evaluacion_impacto": False,
        }
        with pytest.raises(HTTPException) as exc_info:
            _validar_eipd_obligatoria(data)
        assert exc_info.value.status_code == 422

    def test_datos_sensibles_con_evaluacion_impacto_true_pasa(self):
        """datos_sensibles=True con evaluacion_impacto=True debe pasar."""
        data = {
            "datos_sensibles": True,
            "transferencia_internacional": False,
            "estado_eipd": "en_progreso",
            "evaluacion_impacto": True,
        }
        _validar_eipd_obligatoria(data)

    def test_no_requerida_justificada_con_justificacion_corta_falla(self):
        """estado_eipd=no_requerida_justificada con <20 chars debe fallar."""
        data = {
            "datos_sensibles": True,
            "transferencia_internacional": False,
            "estado_eipd": "no_requerida_justificada",
            "evaluacion_impacto": False,
            "justificacion_no_aplica": "corta",
        }
        with pytest.raises(HTTPException) as exc_info:
            _validar_eipd_obligatoria(data)
        assert exc_info.value.status_code == 422
        assert "20 caracteres" in exc_info.value.detail

    def test_no_requerida_justificada_con_19_chars_falla(self):
        data = {
            "datos_sensibles": True,
            "transferencia_internacional": False,
            "estado_eipd": "no_requerida_justificada",
            "evaluacion_impacto": False,
            "justificacion_no_aplica": "x" * 19,
        }
        with pytest.raises(HTTPException) as exc_info:
            _validar_eipd_obligatoria(data)
        assert exc_info.value.status_code == 422

    def test_no_requerida_justificada_con_20_chars_pasa(self):
        data = {
            "datos_sensibles": True,
            "transferencia_internacional": False,
            "estado_eipd": "no_requerida_justificada",
            "evaluacion_impacto": False,
            "justificacion_no_aplica": "x" * 20,
        }
        _validar_eipd_obligatoria(data)

    def test_no_requerida_justificada_sin_justificacion_falla(self):
        data = {
            "datos_sensibles": True,
            "transferencia_internacional": False,
            "estado_eipd": "no_requerida_justificada",
            "evaluacion_impacto": False,
            "justificacion_no_aplica": None,
        }
        with pytest.raises(HTTPException):
            _validar_eipd_obligatoria(data)

    def test_no_requerida_justificada_solo_espacios_falla(self):
        data = {
            "datos_sensibles": True,
            "transferencia_internacional": False,
            "estado_eipd": "no_requerida_justificada",
            "evaluacion_impacto": False,
            "justificacion_no_aplica": "                    ",
        }
        with pytest.raises(HTTPException):
            _validar_eipd_obligatoria(data)

    def test_sin_flags_especiales_no_requiere_eipd(self):
        """Sin datos sensibles ni transferencia internacional, no se requiere EIPD."""
        data = {
            "datos_sensibles": False,
            "transferencia_internacional": False,
            "estado_eipd": "no_requerida",
            "evaluacion_impacto": False,
        }
        _validar_eipd_obligatoria(data)

    def test_ambos_flags_juntos_con_eipd_pasa(self):
        """datos_sensibles + transferencia_internacional con EIPD completada pasa."""
        data = {
            "datos_sensibles": True,
            "transferencia_internacional": True,
            "estado_eipd": "completada",
            "evaluacion_impacto": True,
        }
        _validar_eipd_obligatoria(data)