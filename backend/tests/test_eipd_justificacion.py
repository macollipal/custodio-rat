"""
Tests para validación EIPD obligatoria con justificación documentada (Art. 15 bis Ley 21.719).
Cubre validar_eipd_obligatoria() de rat_validators.py.

Compatible con la versión refactorizada (agosto 2026): el validador reside en
`app.services.rat_validators` y acepta parámetros opcionales (rat_id, db) para
verificar existencia real de la EIPD en BD.
"""
import pytest
from fastapi import HTTPException

from app.services.rat_validators import validar_eipd_obligatoria
from app.services.rat_constants import UMBRAL_JUSTIFICACION_EIPD
from app.models.eipd import ResultadoEIPD


class TestValidarEipdObligatoriaLegacyMode:
    """Tests del modo legacy (solo flags en payload, sin DB check)."""

    def test_datos_sensibles_con_estado_no_requerida_falla(self):
        data = {
            "datos_sensibles": True,
            "transferencia_internacional": False,
            "estado_eipd": "no_requerida",
            "evaluacion_impacto": False,
        }
        with pytest.raises(HTTPException) as exc_info:
            validar_eipd_obligatoria(data)
        assert exc_info.value.status_code == 422
        assert "EIPD" in exc_info.value.detail

    def test_transferencia_internacional_sin_eipd_falla(self):
        data = {
            "datos_sensibles": False,
            "transferencia_internacional": True,
            "estado_eipd": "no_requerida",
            "evaluacion_impacto": False,
        }
        with pytest.raises(HTTPException) as exc_info:
            validar_eipd_obligatoria(data)
        assert exc_info.value.status_code == 422

    def test_datos_sensibles_con_evaluacion_impacto_true_pasa(self):
        data = {
            "datos_sensibles": True,
            "transferencia_internacional": False,
            "estado_eipd": "en_proceso",
            "evaluacion_impacto": True,
        }
        validar_eipd_obligatoria(data)

    def test_no_requerida_justificada_con_justificacion_corta_falla(self):
        data = {
            "datos_sensibles": True,
            "transferencia_internacional": False,
            "estado_eipd": "no_requerida_justificada",
            "evaluacion_impacto": False,
            "justificacion_no_aplica": "corta",
        }
        with pytest.raises(HTTPException) as exc_info:
            validar_eipd_obligatoria(data)
        assert exc_info.value.status_code == 422
        assert "20 caracteres" in exc_info.value.detail or str(UMBRAL_JUSTIFICACION_EIPD) in exc_info.value.detail

    def test_no_requerida_justificada_con_19_chars_falla(self):
        data = {
            "datos_sensibles": True,
            "transferencia_internacional": False,
            "estado_eipd": "no_requerida_justificada",
            "evaluacion_impacto": False,
            "justificacion_no_aplica": "x" * 19,
        }
        with pytest.raises(HTTPException):
            validar_eipd_obligatoria(data)

    def test_no_requerida_justificada_con_20_chars_pasa(self):
        data = {
            "datos_sensibles": True,
            "transferencia_internacional": False,
            "estado_eipd": "no_requerida_justificada",
            "evaluacion_impacto": False,
            "justificacion_no_aplica": "x" * 20,
        }
        validar_eipd_obligatoria(data)

    def test_no_requerida_justificada_sin_justificacion_falla(self):
        data = {
            "datos_sensibles": True,
            "transferencia_internacional": False,
            "estado_eipd": "no_requerida_justificada",
            "evaluacion_impacto": False,
            "justificacion_no_aplica": None,
        }
        with pytest.raises(HTTPException):
            validar_eipd_obligatoria(data)

    def test_no_requerida_justificada_solo_espacios_falla(self):
        data = {
            "datos_sensibles": True,
            "transferencia_internacional": False,
            "estado_eipd": "no_requerida_justificada",
            "evaluacion_impacto": False,
            "justificacion_no_aplica": "                    ",
        }
        with pytest.raises(HTTPException):
            validar_eipd_obligatoria(data)

    def test_sin_flags_especiales_no_requiere_eipd(self):
        data = {
            "datos_sensibles": False,
            "transferencia_internacional": False,
            "estado_eipd": "no_requerida",
            "evaluacion_impacto": False,
        }
        validar_eipd_obligatoria(data)

    def test_ambos_flags_juntos_con_eipd_pasa(self):
        data = {
            "datos_sensibles": True,
            "transferencia_internacional": True,
            "estado_eipd": "completada",
            "evaluacion_impacto": True,
        }
        validar_eipd_obligatoria(data)


class TestValidarEipdObligatoriaDbMode:
    """Tests del nuevo modo con DB check (cuando se pasan rat_id y db)."""

    def test_sin_eipd_en_bd_falla(self):
        """Si rat_id y db, y no existe EIPD, debe fallar 422."""
        from unittest.mock import MagicMock
        data = {
            "datos_sensibles": True,
            "transferencia_internacional": False,
            "estado_eipd": "no_requerida",
        }
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = None
        with pytest.raises(HTTPException) as exc_info:
            validar_eipd_obligatoria(data, rat_id=42, db=db)
        assert exc_info.value.status_code == 422

    def test_con_eipd_no_requerida_en_bd_falla(self):
        """EIPD marcada como no_requerida en BD no es válida si RAT tiene datos sensibles."""
        from unittest.mock import MagicMock
        data = {
            "datos_sensibles": True,
            "transferencia_internacional": False,
        }
        eipd_mock = MagicMock()
        eipd_mock.resultado = ResultadoEIPD.NO_REQUERIDA
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = eipd_mock
        with pytest.raises(HTTPException):
            validar_eipd_obligatoria(data, rat_id=42, db=db)

    def test_con_eipd_completada_pasa(self):
        """EIPD completada + datos sensibles pasa la validación."""
        from unittest.mock import MagicMock
        data = {
            "datos_sensibles": True,
            "transferencia_internacional": False,
        }
        eipd_mock = MagicMock()
        eipd_mock.resultado = ResultadoEIPD.COMPLETADA
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = eipd_mock
        validar_eipd_obligatoria(data, rat_id=42, db=db)

    def test_con_eipd_en_proceso_pasa(self):
        from unittest.mock import MagicMock
        data = {
            "datos_sensibles": True,
            "transferencia_internacional": False,
        }
        eipd_mock = MagicMock()
        eipd_mock.resultado = ResultadoEIPD.EN_PROCESO
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = eipd_mock
        validar_eipd_obligatoria(data, rat_id=42, db=db)

    def test_con_eipd_no_requerida_justificada_pasa(self):
        from unittest.mock import MagicMock
        data = {
            "datos_sensibles": True,
            "transferencia_internacional": False,
        }
        eipd_mock = MagicMock()
        eipd_mock.resultado = ResultadoEIPD.NO_REQUERIDA_JUSTIFICADA
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = eipd_mock
        validar_eipd_obligatoria(data, rat_id=42, db=db)

    def test_sin_datos_sensibles_db_mode_no_consulta_bd(self):
        """Sin datos sensibles, no se hace check de DB (early-return)."""
        from unittest.mock import MagicMock
        data = {
            "datos_sensibles": False,
            "transferencia_internacional": False,
        }
        db = MagicMock()
        validar_eipd_obligatoria(data, rat_id=42, db=db)
        db.query.assert_not_called()
