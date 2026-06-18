"""
Tests para QW8: Portal del Titular — Seguimiento por tracking_token.
GET /seguimiento/{tracking_token} — público, sin auth.
"""

import pytest
from datetime import datetime, timezone, timedelta


class TestQW8Seguimiento:
    def test_consulta_token_valido_retorna_estado(self, client, db, empresa):
        """Un tracking_token válido devuelve los datos del ticket."""
        from app.services.ticket_service import crear_ticket_desde_solicitud
        from app.models.company import Company

        company = db.query(Company).filter(Company.id == empresa["id"]).first()

        ticket = crear_ticket_desde_solicitud(
            db=db,
            company_id=empresa["id"],
            tipo="acceso",
            titular_nombre="Juan Pérez",
            titular_email="juan@perez.cl",
            descripcion="Quiero saber qué datos tienen",
            origen="web",
            company_nombre=company.nombre if company else "Test",
        )

        resp = client.get(f"/seguimiento/{ticket.tracking_token}")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        data = resp.json()
        assert data["id"] == ticket.id
        assert data["tipo"] == "Acceso"
        assert data["estado"] == "Abierto"
        assert "fecha_recepcion" in data
        assert "dias_restantes" in data
        assert isinstance(data["historial"], list)

    def test_consulta_token_invalido_retorna_404(self, client):
        """Un tracking_token que no existe devuelve 404."""
        resp = client.get("/seguimiento/00000000-0000-0000-0000-000000000000")
        assert resp.status_code == 404
        assert "No se encontró" in resp.json()["detail"]

    def test_consulta_sin_token_retorna_404(self, client):
        """Sin tracking_token devuelve 404 (not found)."""
        resp = client.get("/seguimiento/")
        assert resp.status_code in (404, 405)

    def test_consulta_con_estado_subsanacion(self, client, db, empresa):
        """Un ticket en estado subsanacion muestra ese estado."""
        from app.services.ticket_service import crear_ticket_desde_solicitud, solicitar_subsanacion
        from app.models.company import Company

        company = db.query(Company).filter(Company.id == empresa["id"]).first()

        ticket = crear_ticket_desde_solicitud(
            db=db,
            company_id=empresa["id"],
            tipo="acceso",
            titular_nombre="Test Subsanación",
            titular_email="subsan@test.cl",
            origen="web",
            company_nombre=company.nombre if company else "Test",
        )

        solicitar_subsanacion(
            db=db,
            ticket_id=ticket.id,
            detalle="Falta cédula de identidad",
        )

        resp = client.get(f"/seguimiento/{ticket.tracking_token}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["estado"] == "Subsanación"

    def test_consulta_con_historial(self, client, db, empresa):
        """El endpoint devuelve el historial de cambios."""
        from app.services.ticket_service import crear_ticket_desde_solicitud
        from app.models.company import Company

        company = db.query(Company).filter(Company.id == empresa["id"]).first()

        ticket = crear_ticket_desde_solicitud(
            db=db,
            company_id=empresa["id"],
            tipo="cancelacion",
            titular_nombre="Carlos Méndez",
            titular_email="carlos@mendez.cl",
            origen="web",
            company_nombre=company.nombre if company else "Test",
        )

        resp = client.get(f"/seguimiento/{ticket.tracking_token}")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["historial"]) >= 1
        assert data["historial"][0]["estado_nuevo"] == "Abierto"

    def test_no_requiere_auth(self, client, db, empresa):
        """El endpoint es público — no requiere Bearer token."""
        from app.services.ticket_service import crear_ticket_desde_solicitud
        from app.models.company import Company

        company = db.query(Company).filter(Company.id == empresa["id"]).first()

        ticket = crear_ticket_desde_solicitud(
            db=db,
            company_id=empresa["id"],
            tipo="acceso",
            titular_nombre="Sin Auth",
            titular_email="sinauth@test.cl",
            origen="web",
            company_nombre=company.nombre if company else "Test",
        )

        resp = client.get(f"/seguimiento/{ticket.tracking_token}")
        assert resp.status_code == 200

    def test_dias_restantes_es_negativo_si_vencido(self, client, db, empresa):
        """Un ticket vencido muestra dias_restantes negativo."""
        from app.services.ticket_service import crear_ticket_desde_solicitud
        from app.models.company import Company

        company = db.query(Company).filter(Company.id == empresa["id"]).first()

        ticket = crear_ticket_desde_solicitud(
            db=db,
            company_id=empresa["id"],
            tipo="acceso",
            titular_nombre="Vencido Test",
            titular_email="vencido@test.cl",
            origen="web",
            company_nombre=company.nombre if company else "Test",
        )
        ticket.fecha_vencimiento = datetime.now(timezone.utc) - timedelta(days=5)
        db.commit()

        resp = client.get(f"/seguimiento/{ticket.tracking_token}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["dias_restantes"] is not None
        assert data["dias_restantes"] < 0
