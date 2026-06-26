"""
Tests para schema EncargadoContratoCreate - campos pais y direccion (Art. 14 quater Ley 21.719).
"""
import pytest
from datetime import datetime, timezone
from pydantic import ValidationError

from app.schemas.encargado_contrato import EncargadoContratoCreate


def _base_payload() -> dict:
    return {
        "company_id": 1,
        "nombre_encargado": "Encargado Test SpA",
        "objeto": "Tratamiento de datos personales",
        "duracion_inicio": datetime(2026, 1, 15, 10, 0, 0, tzinfo=timezone.utc).isoformat(),
        "finalidad": "Gestion de clientes",
        "tipo_datos": "Datos identificativos",
        "categorias_titulares": "Clientes",
        "derechos_obligaciones": "Confidencialidad",
    }


class TestEncargadoContratoSchemaPaisDireccion:
    """Tests del schema Pydantic EncargadoContratoCreate."""

    def test_contrato_sin_pais_ni_direccion_es_valido(self):
        data = _base_payload()
        schema = EncargadoContratoCreate(**data)
        assert schema.pais is None
        assert schema.direccion is None

    def test_contrato_con_pais_y_direccion_es_valido(self):
        data = _base_payload()
        data["pais"] = "Chile"
        data["direccion"] = "Av. Apoquindo 4000, Las Condes, Santiago"
        schema = EncargadoContratoCreate(**data)
        assert schema.pais == "Chile"
        assert schema.direccion == "Av. Apoquindo 4000, Las Condes, Santiago"

    def test_pais_con_caracteres_unicode(self):
        data = _base_payload()
        data["pais"] = "Espana"
        data["direccion"] = "Calle Gran Via 1, Madrid"
        schema = EncargadoContratoCreate(**data)
        assert schema.pais == "Espana"
        assert "Gran Via" in schema.direccion

    def test_pais_largo(self):
        data = _base_payload()
        data["pais"] = "Reino Unido de Gran Bretana e Irlanda del Norte"
        schema = EncargadoContratoCreate(**data)
        assert schema.pais == "Reino Unido de Gran Bretana e Irlanda del Norte"

    def test_campos_obligatorios_siguen_siendo_requeridos(self):
        data = _base_payload()
        del data["nombre_encargado"]
        with pytest.raises(ValidationError) as exc_info:
            EncargadoContratoCreate(**data)
        assert "nombre_encargado" in str(exc_info.value)

    def test_pais_y_direccion_no_validan_contenido(self):
        """Schema no valida formato de pais (no es codigo ISO). Solo es texto libre."""
        data = _base_payload()
        data["pais"] = "XX"
        schema = EncargadoContratoCreate(**data)
        assert schema.pais == "XX"


class TestEncargadoContratoEndpointPaisDireccion:
    """Tests de schema Pydantic directos (sin endpoint, evita conflictos de transaccion)."""

    def test_schema_crear_encargado_con_pais_y_direccion(self):
        from app.schemas.encargado_contrato import EncargadoContratoCreate
        data = _base_payload()
        data["pais"] = "Argentina"
        data["direccion"] = "Av. Corrientes 1234, Buenos Aires"
        schema = EncargadoContratoCreate(**data)
        assert schema.pais == "Argentina"
        assert schema.direccion == "Av. Corrientes 1234, Buenos Aires"

    def test_schema_crear_encargado_sin_pais_ni_direccion(self):
        from app.schemas.encargado_contrato import EncargadoContratoCreate
        data = _base_payload()
        schema = EncargadoContratoCreate(**data)
        assert schema.pais is None
        assert schema.direccion is None

    def test_schema_update_con_pais_y_direccion(self):
        from app.schemas.encargado_contrato import EncargadoContratoUpdate
        schema = EncargadoContratoUpdate(pais="Peru", direccion="Av. Larco 345, Miraflores, Lima")
        assert schema.pais == "Peru"
        assert schema.direccion == "Av. Larco 345, Miraflores, Lima"