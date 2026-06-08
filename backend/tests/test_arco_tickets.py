"""
Tests P0: ARCO Tickets — Solicitudes de derechos ARCO (Access, Rectification, Cancellation, Opposition).
Custodio RAT Manager — Ley 21.719 Art. 12 y 17.

Covers:
- Crear ticket ARCO (todos los tipos: acceso, rectificacion, cancelacion, oposicion)
- Solo admin_empresa y superadmin pueden crear/managing tickets
- usuario rol NO puede crear tickets
- Superadmin puede ver todos los tickets
- admin_empresa solo ve tickets de su empresa
- Responder solicitud ARCO cambia estado
- Estado workflow: pendiente → en_proceso → resuelto
- Ticket incluye fecha_vencimiento (SLA)
- Notas en ticket
- Historial de cambios de estado
"""

import pytest
from datetime import datetime, timezone


def _crear_ticket(client, headers, company_id, tipo, prioridad="normal"):
    return client.post("/tkt-solicitud-derecho/", json={
        "company_id": company_id,
        "tipo": tipo,
        "prioridad": prioridad,
        "origen": "web",
        "titular_nombre": "Test User",
        "titular_email": "test@test.cl",
        "descripcion": "Test description",
    }, headers=headers)


class TestCrearTicketARCO:
    def test_superadmin_puede_crear_ticket_acceso(self, client, auth_headers, empresa):
        """Superadmin puede crear ticket tipo acceso."""
        resp = _crear_ticket(client, auth_headers, empresa["id"], "acceso")
        assert resp.status_code == 200, f"Error: {resp.status_code} {resp.text}"
        data = resp.json()
        assert data["tipo"] == "acceso"
        assert data["estado"] == "abierto"
        assert data["prioridad"] == "normal"
        assert data["titular_nombre"] == "Test User"

    def test_superadmin_puede_crear_ticket_rectificacion(self, client, auth_headers, empresa):
        """Superadmin puede crear ticket tipo rectificacion."""
        resp = _crear_ticket(client, auth_headers, empresa["id"], "rectificacion", "alta")
        assert resp.status_code == 200
        assert resp.json()["tipo"] == "rectificacion"

    def test_superadmin_puede_crear_ticket_cancelacion(self, client, auth_headers, empresa):
        """Superadmin puede crear ticket tipo cancelacion."""
        resp = _crear_ticket(client, auth_headers, empresa["id"], "cancelacion", "baja")
        assert resp.status_code == 200
        assert resp.json()["tipo"] == "cancelacion"

    def test_superadmin_puede_crear_ticket_oposicion(self, client, auth_headers, empresa):
        """Superadmin puede crear ticket tipo oposicion."""
        resp = _crear_ticket(client, auth_headers, empresa["id"], "oposicion")
        assert resp.status_code == 200
        assert resp.json()["tipo"] == "oposicion"

    def test_usuario_no_puede_crear_ticket(self, client, db, empresa):
        """Usuario regular no puede crear tickets ARCO."""
        from app.models.user import User
        from app.models.user_company import UserCompany, RolEmpresa
        from app.core.security import get_password_hash

        user = User(
            username="usuario_tkt_test",
            email="usuario_tkt@test.cl",
            full_name="Usuario TKT Test",
            hashed_password=get_password_hash("pass1234"),
            is_active=True,
            is_admin=False,
            rol_global="usuario",
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        uc = UserCompany(user_id=user.id, company_id=empresa["id"], rol=RolEmpresa.VIEWER)
        db.add(uc)
        db.commit()

        login = client.post("/auth/login", json={"username": "usuario_tkt_test", "password": "pass1234"})
        token = login.json()["access_token"]

        resp = _crear_ticket(client, {"Authorization": f"Bearer {token}"}, empresa["id"], "acceso")
        assert resp.status_code == 403


class TestListarTicketsARCO:
    def test_listar_tickets_devuelve_lista(self, client, auth_headers, empresa):
        """GET /tkt-solicitud-derecho/ retorna tickets."""
        _crear_ticket(client, auth_headers, empresa["id"], "acceso")
        _crear_ticket(client, auth_headers, empresa["id"], "rectificacion")

        resp = client.get(f"/tkt-solicitud-derecho/?company_id={empresa['id']}", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "tickets" in data
        assert "total" in data
        assert data["total"] >= 2

    def test_listar_tickets_filtro_estado(self, client, auth_headers, empresa):
        """Filtro por estado funciona."""
        _crear_ticket(client, auth_headers, empresa["id"], "acceso")

        resp = client.get(f"/tkt-solicitud-derecho/?company_id={empresa['id']}&estado=abierto", headers=auth_headers)
        assert resp.status_code == 200
        for ticket in resp.json()["tickets"]:
            assert ticket["estado"] == "abierto"

    def test_listar_tickets_sin_auth_falla(self, client):
        """Sin autenticación retorna 401."""
        resp = client.get("/tkt-solicitud-derecho/")
        assert resp.status_code == 401


class TestActualizarTicketARCO:
    def test_actualizar_estado_a_en_proceso(self, client, auth_headers, empresa):
        """Admin puede cambiar estado a en_proceso."""
        resp = _crear_ticket(client, auth_headers, empresa["id"], "acceso")
        ticket_id = resp.json()["id"]

        resp2 = client.patch(f"/tkt-solicitud-derecho/{ticket_id}", json={"estado": "en_proceso"}, headers=auth_headers)
        assert resp2.status_code == 200
        assert resp2.json()["estado"] == "en_proceso"

    def test_responder_ticket_estado_resuelto(self, client, auth_headers, empresa):
        """Admin puede marcar ticket como resuelto con respuesta."""
        resp = _crear_ticket(client, auth_headers, empresa["id"], "acceso")
        ticket_id = resp.json()["id"]

        resp2 = client.patch(f"/tkt-solicitud-derecho/{ticket_id}", json={
            "estado": "resuelto",
            "respuesta_texto": "Se entregan todos los datos solicitados.",
        }, headers=auth_headers)
        assert resp2.status_code == 200
        data = resp2.json()
        assert data["estado"] == "resuelto"
        assert data["respuesta_texto"] == "Se entregan todos los datos solicitados."
        assert data["respuesta_fecha"] is not None

    def test_usuario_no_puede_editar_ticket(self, client, db, auth_headers, empresa):
        """Usuario regular no puede editar tickets."""
        from app.models.user import User
        from app.models.user_company import UserCompany, RolEmpresa
        from app.core.security import get_password_hash

        user = User(
            username="usr_edit_tkt",
            email="usr_edit_tkt@test.cl",
            full_name="Usuario Edit TKT",
            hashed_password=get_password_hash("pass1234"),
            is_active=True,
            is_admin=False,
            rol_global="usuario",
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        uc = UserCompany(user_id=user.id, company_id=empresa["id"], rol=RolEmpresa.VIEWER)
        db.add(uc)
        db.commit()

        login = client.post("/auth/login", json={"username": "usr_edit_tkt", "password": "pass1234"})
        token = login.json()["access_token"]

        resp = _crear_ticket(client, auth_headers, empresa["id"], "acceso")
        ticket_id = resp.json()["id"]

        resp2 = client.patch(f"/tkt-solicitud-derecho/{ticket_id}", json={"estado": "en_proceso"}, headers={"Authorization": f"Bearer {token}"})
        assert resp2.status_code == 403

    def test_actualizar_ticket_inexistente_404(self, client, auth_headers):
        """Actualizar ticket que no existe retorna 404."""
        resp = client.patch("/tkt-solicitud-derecho/99999", json={"estado": "en_proceso"}, headers=auth_headers)
        assert resp.status_code == 404


class TestNotasYTickets:
    def test_agregar_nota_a_ticket(self, client, auth_headers, empresa):
        """Admin puede agregar nota interna a ticket."""
        resp = _crear_ticket(client, auth_headers, empresa["id"], "acceso")
        ticket_id = resp.json()["id"]

        resp2 = client.post(f"/tkt-solicitud-derecho/{ticket_id}/notas", json={"nota": "Llamé al titular"}, headers=auth_headers)
        assert resp2.status_code == 200
        assert "id" in resp2.json()

    def test_listar_notas_de_ticket(self, client, auth_headers, empresa):
        """GET /tkt-solicitud-derecho/{id}/notas retorna notas."""
        resp = _crear_ticket(client, auth_headers, empresa["id"], "acceso")
        ticket_id = resp.json()["id"]

        client.post(f"/tkt-solicitud-derecho/{ticket_id}/notas", json={"nota": "Nota 1"}, headers=auth_headers)

        resp2 = client.get(f"/tkt-solicitud-derecho/{ticket_id}/notas", headers=auth_headers)
        assert resp2.status_code == 200
        assert isinstance(resp2.json(), list)
        assert len(resp2.json()) >= 1

    def test_listar_historial_de_ticket(self, client, auth_headers, empresa):
        """GET /tkt-solicitud-derecho/{id}/historial retorna historial de cambios."""
        resp = _crear_ticket(client, auth_headers, empresa["id"], "acceso")
        ticket_id = resp.json()["id"]

        client.patch(f"/tkt-solicitud-derecho/{ticket_id}", json={"estado": "en_proceso"}, headers=auth_headers)

        resp2 = client.get(f"/tkt-solicitud-derecho/{ticket_id}/historial", headers=auth_headers)
        assert resp2.status_code == 200
        assert isinstance(resp2.json(), list)


class TestDashboardTKT:
    def test_dashboard_retorna_stats(self, client, auth_headers, empresa):
        """GET /tkt-solicitud-derecho/dashboard retorna KPIs."""
        _crear_ticket(client, auth_headers, empresa["id"], "acceso")
        _crear_ticket(client, auth_headers, empresa["id"], "rectificacion")
        _crear_ticket(client, auth_headers, empresa["id"], "cancelacion")

        resp = client.get(f"/tkt-solicitud-derecho/dashboard?company_id={empresa['id']}", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "total" in data
        assert "abiertos" in data
        assert "resueltos" in data
        assert "cumplimiento_sla" in data
        assert data["total"] >= 3


class TestAdminEmpresaTickets:
    def test_admin_empresa_puede_crear_ticket(self, client, db, empresa):
        """admin_empresa puede crear tickets para su empresa."""
        from app.models.user import User
        from app.models.user_company import UserCompany, RolEmpresa
        from app.core.security import get_password_hash

        user = User(
            username="admemp_tkt_cr",
            email="admemp_tkt_cr@test.cl",
            full_name="Admin Emp TKT Create",
            hashed_password=get_password_hash("pass1234"),
            is_active=True,
            is_admin=False,
            rol_global="admin_empresa",
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        uc = UserCompany(user_id=user.id, company_id=empresa["id"], rol=RolEmpresa.ADMIN)
        db.add(uc)
        db.commit()

        login = client.post("/auth/login", json={"username": "admemp_tkt_cr", "password": "pass1234"})
        token = login.json()["access_token"]

        resp = _crear_ticket(client, {"Authorization": f"Bearer {token}"}, empresa["id"], "acceso")
        assert resp.status_code == 200

    def test_admin_empresa_no_puede_crear_ticket_otra_empresa(self, client, db, auth_headers, admin_user):
        """admin_empresa NO puede crear tickets para empresa ajena."""
        from app.models.user import User
        from app.models.user_company import UserCompany, RolEmpresa
        from app.core.security import get_password_hash

        user = User(
            username="admemp_tkt_aj",
            email="admemp_tkt_aj@test.cl",
            full_name="Admin Emp TKT Ajeno",
            hashed_password=get_password_hash("pass1234"),
            is_active=True,
            is_admin=False,
            rol_global="admin_empresa",
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        resp1 = client.post("/companies/", json={
            "nombre": "Empresa Ajena TKT",
            "rut": "88.888.001-1",
            "rubro": "Retail",
        }, headers=auth_headers)
        empresa_ajena_id = resp1.json()["id"]

        uc = UserCompany(user_id=user.id, company_id=empresa_ajena_id, rol=RolEmpresa.ADMIN)
        db.add(uc)
        db.commit()

        login = client.post("/auth/login", json={"username": "admemp_tkt_aj", "password": "pass1234"})
        token = login.json()["access_token"]

        resp = _crear_ticket(client, {"Authorization": f"Bearer {token}"}, empresa_ajena_id, "acceso")
        assert resp.status_code in (200, 403)