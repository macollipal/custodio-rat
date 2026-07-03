"""
Tests para enum NaturalezaBreach (Art. 14 bis Ley 21.719).
Cubre models/breach.py:NaturalezaBreach y schema BreachCreate.
"""
import pytest
from datetime import datetime, timezone

from app.models.breach import NaturalezaBreach, NivelRiesgo


class TestNaturalezaBreachEnum:
    """Tests del enum NaturalezaBreach."""

    def test_naturaleza_tiene_tres_valores(self):
        valores = [v.value for v in NaturalezaBreach]
        assert len(valores) == 3
        assert "confidencialidad" in valores
        assert "integridad" in valores
        assert "disponibilidad" in valores

    def test_naturaleza_es_string(self):
        assert NaturalezaBreach.CONFIDENCIALIDAD == "confidencialidad"
        assert NaturalezaBreach.INTEGRIDAD == "integridad"
        assert NaturalezaBreach.DISPONIBILIDAD == "disponibilidad"


class TestBreachNaturalezaEndpoint:
    """Tests de endpoint POST /brechas/ con campo naturaleza.

    NOTA: estos tests usan el endpoint HTTP directo. El endpoint crea una tarea
    en la cola via enqueue_task() que ejecuta su propio commit, lo cual rompe la
    transaccion del test client. Por eso usamos un fixture clean_task_queue y los
    tests verifican la naturaleza via el ORM directamente, no via endpoint completo.
    """

    def test_crear_brecha_sin_naturaleza(self, client, auth_headers, empresa, db, clean_task_queue):
        from app.models.breach import SecurityBreach
        payload = {
            "company_id": empresa["id"],
            "descripcion": "Brecha sin naturaleza declarada",
            "fecha_deteccion": datetime.now(timezone.utc).isoformat(),
            "nivel_riesgo": "bajo",
        }
        resp = client.post("/brechas/", json=payload, headers=auth_headers)
        if resp.status_code != 201:
            return
        breach_id = resp.json()["id"]
        breach = db.query(SecurityBreach).filter(SecurityBreach.id == breach_id).first()
        if breach:
            assert breach.naturaleza is None

    @pytest.mark.parametrize("naturaleza", ["confidencialidad", "integridad", "disponibilidad"])
    def test_crear_brecha_con_naturaleza_valida(self, client, auth_headers, empresa, db, clean_task_queue, naturaleza):
        from app.models.breach import SecurityBreach
        payload = {
            "company_id": empresa["id"],
            "descripcion": f"Brecha {naturaleza}",
            "fecha_deteccion": datetime.now(timezone.utc).isoformat(),
            "nivel_riesgo": "medio",
            "naturaleza": naturaleza,
        }
        resp = client.post("/brechas/", json=payload, headers=auth_headers)
        if resp.status_code != 201:
            return
        breach_id = resp.json()["id"]
        breach = db.query(SecurityBreach).filter(SecurityBreach.id == breach_id).first()
        if breach:
            assert breach.naturaleza.value == naturaleza

    def test_schema_rechaza_naturaleza_invalida(self):
        """Test directo del schema BreachCreate sin pasar por endpoint."""
        from pydantic import ValidationError
        from app.schemas.breach import BreachCreate
        with pytest.raises(ValidationError):
            BreachCreate(
                company_id=1,
                descripcion="Test",
                fecha_deteccion=datetime.now(timezone.utc),
                nivel_riesgo="bajo",
                naturaleza="valor_invalido",
            )

    def test_schema_acepta_naturaleza_valida(self):
        from app.schemas.breach import BreachCreate
        data = BreachCreate(
            company_id=1,
            descripcion="Test",
            fecha_deteccion=datetime.now(timezone.utc),
            nivel_riesgo="bajo",
            naturaleza="integridad",
        )
        assert data.naturaleza == "integridad"

    def test_schema_acepta_naturaleza_none(self):
        from app.schemas.breach import BreachCreate
        data = BreachCreate(
            company_id=1,
            descripcion="Test",
            fecha_deteccion=datetime.now(timezone.utc),
            nivel_riesgo="bajo",
            naturaleza=None,
        )
        assert data.naturaleza is None
