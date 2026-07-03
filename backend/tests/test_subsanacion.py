"""
Tests para QW3: Workflow de SubsanaciÃ³n.
Custodio RAT Manager â€” Ley 21.719 Art. 12.

Covers:
- Solicitar subsanaciÃ³n desde estado abierto/en_proceso/pendiente
- Error al solicitar subsanaciÃ³n desde otros estados
- Completar subsanaciÃ³n y volver a en_proceso
- Error al completar si no estÃ¡ en subsanacion
- Extension del plazo al solicitar subsanaciÃ³n
- Permisos: usuario no puede solicitar subsanaciÃ³n
"""

import pytest


class TestSubsanacionWorkflow:
    def test_solicitar_subsanacion_desde_abierto(self, client, auth_headers, empresa, db):
        """Admin puede solicitar subsanaciÃ³n desde estado abierto."""
        ticket_resp = client.post("/tkt-solicitud-derecho/", json={
            "company_id": empresa["id"],
            "tipo": "acceso",
            "titular_nombre": "Juan Perez",
            "titular_email": "juan@test.cl",
            "prioridad": "normal",
        }, headers=auth_headers)
        assert ticket_resp.status_code == 200
        ticket_id = ticket_resp.json()["id"]

        resp = client.post(f"/tkt-solicitud-derecho/{ticket_id}/subsanar", json={
            "detalle": "Por favor complete su nÃºmero de RUT para procesar su solicitud de acceso.",
        }, headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["estado"] == "subsanacion"
        assert data["subsanacion_detalle"] is not None
        assert data["subsanacion_fecha_pedido"] is not None
        assert data["fecha_vencimiento"] is not None

    def test_solicitar_subsanacion_desde_en_proceso(self, client, auth_headers, empresa, db):
        """Admin puede solicitar subsanaciÃ³n desde estado en_proceso."""
        ticket_resp = client.post("/tkt-solicitud-derecho/", json={
            "company_id": empresa["id"],
            "tipo": "acceso",
            "titular_nombre": "Maria Lopez",
            "titular_email": "maria@test.cl",
            "prioridad": "normal",
        }, headers=auth_headers)
        ticket_id = ticket_resp.json()["id"]

        client.patch(f"/tkt-solicitud-derecho/{ticket_id}", json={"estado": "en_proceso"}, headers=auth_headers)

        resp = client.post(f"/tkt-solicitud-derecho/{ticket_id}/subsanar", json={
            "detalle": "Se requiere documentaciÃ³n adicional para verificar su identidad.",
        }, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["estado"] == "subsanacion"

    def test_solicitar_subsanacion_error_desde_resuelto(self, client, auth_headers, empresa, db):
        """No se puede solicitar subsanaciÃ³n desde estado resuelto."""
        ticket_resp = client.post("/tkt-solicitud-derecho/", json={
            "company_id": empresa["id"],
            "tipo": "acceso",
            "titular_nombre": "Pedro Gomez",
            "titular_email": "pedro@test.cl",
        }, headers=auth_headers)
        ticket_id = ticket_resp.json()["id"]

        client.patch(f"/tkt-solicitud-derecho/{ticket_id}", json={
            "estado": "resuelto",
            "respuesta_texto": "Datos entregados",
        }, headers=auth_headers)

        resp = client.post(f"/tkt-solicitud-derecho/{ticket_id}/subsanar", json={
            "detalle": "InformaciÃ³n faltante",
        }, headers=auth_headers)
        assert resp.status_code == 400

    def test_completar_subsanacion(self, client, auth_headers, empresa, db):
        """Admin puede completar subsanaciÃ³n y vuelve a en_proceso con nuevo plazo."""
        ticket_resp = client.post("/tkt-solicitud-derecho/", json={
            "company_id": empresa["id"],
            "tipo": "rectificacion",
            "titular_nombre": "Ana Martinez",
            "titular_email": "ana@test.cl",
        }, headers=auth_headers)
        ticket_id = ticket_resp.json()["id"]

        client.post(f"/tkt-solicitud-derecho/{ticket_id}/subsanar", json={
            "detalle": "Complete su RUT por favor.",
        }, headers=auth_headers)

        resp = client.post(f"/tkt-solicitud-derecho/{ticket_id}/completar-subsanacion", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["estado"] == "en_proceso"
        assert data["subsanacion_detalle"] is None
        assert data["subsanacion_fecha_pedido"] is None

    def test_completar_subsanacion_error_si_no_esta_en_subsanacion(self, client, auth_headers, empresa, db):
        """No se puede completar subsanaciÃ³n si el ticket no estÃ¡ en subsanacion."""
        ticket_resp = client.post("/tkt-solicitud-derecho/", json={
            "company_id": empresa["id"],
            "tipo": "acceso",
            "titular_nombre": "Carlos Ruiz",
            "titular_email": "carlos@test.cl",
        }, headers=auth_headers)
        ticket_id = ticket_resp.json()["id"]

        resp = client.post(f"/tkt-solicitud-derecho/{ticket_id}/completar-subsanacion", headers=auth_headers)
        assert resp.status_code == 400

    def test_usuario_no_puede_solicitar_subsanacion(self, client, db, empresa, auth_headers):
        """Usuario regular no puede solicitar subsanaciÃ³n (receives 403)."""
        from app.models.user import User
        from app.models.user_company import UserCompany, RolEmpresa
        from app.core.security import get_password_hash

        user = User(
            username="usr_sub2",
            email="usr_sub2@test.cl",
            full_name="Usuario Subs Test 2",
            hashed_password=get_password_hash("pass1234"),
            is_active=True,
            is_admin=False,
            rol_global="usuario",
        )
        db.add(user)
        db.commit()

        uc = UserCompany(user_id=user.id, company_id=empresa["id"], rol=RolEmpresa.VIEWER)
        db.add(uc)
        db.commit()

        ticket_resp = client.post("/tkt-solicitud-derecho/", json={
            "company_id": empresa["id"],
            "tipo": "acceso",
            "titular_nombre": "Test User",
            "titular_email": "test@test.cl",
        }, headers=auth_headers)
        ticket_id = ticket_resp.json()["id"]

        login = client.post("/auth/login", json={"username": "usr_sub2", "password": "pass1234"})
        token = login.json()["access_token"]
        headers_usr = {"Authorization": f"Bearer {token}"}

        resp = client.post(f"/tkt-solicitud-derecho/{ticket_id}/subsanar", json={
            "detalle": "InformaciÃ³n faltante para procesar solicitud.",
        }, headers=headers_usr)
        assert resp.status_code == 403

    def test_detalle_min_length_validation(self, client, auth_headers, empresa, db):
        """El detalle de subsanaciÃ³n debe tener al menos 10 caracteres."""
        ticket_resp = client.post("/tkt-solicitud-derecho/", json={
            "company_id": empresa["id"],
            "tipo": "acceso",
            "titular_nombre": "Test Short",
            "titular_email": "short@test.cl",
        }, headers=auth_headers)
        ticket_id = ticket_resp.json()["id"]

        resp = client.post(f"/tkt-solicitud-derecho/{ticket_id}/subsanar", json={
            "detalle": "corto",
        }, headers=auth_headers)
        assert resp.status_code == 422
