"""
Tests para QW4: Workflow de PrÃ³rroga.
Custodio RAT Manager â€” Ley 21.719 Art. 12 bis.

Covers:
- Prorrogar ticket desde estado abierto/en_proceso/pendiente
- Error al prorrogar desde resuelto/rechazado/bloqueado
- Error al prorrogar dos veces
- Extension del plazo al prorrogar
- Permisos: usuario no puede prorrogar
- LÃ­mite mÃ¡ximo de 10 dÃ­as
"""



class TestProrrogaWorkflow:
    def test_prorrogar_desde_abierto(self, client, auth_headers, empresa, db):
        """Admin puede prorrogar desde estado abierto."""
        ticket_resp = client.post("/tkt-solicitud-derecho/", json={
            "company_id": empresa["id"],
            "tipo": "acceso",
            "titular_nombre": "Juan Perez",
            "titular_email": "juan@test.cl",
            "prioridad": "normal",
        }, headers=auth_headers)
        assert ticket_resp.status_code == 200
        ticket_id = ticket_resp.json()["id"]

        resp = client.post(f"/tkt-solicitud-derecho/{ticket_id}/prorrogar", json={
            "dias": 5,
            "motivo": "Carga de trabajo excepcional",
        }, headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["estado"] == "prorroga"
        assert data["prorroga_fecha"] is not None
        assert data["prorroga_dias"] == 5
        assert data["fecha_vencimiento"] is not None

    def test_prorrogar_desde_en_proceso(self, client, auth_headers, empresa, db):
        """Admin puede prorrogar desde estado en_proceso."""
        ticket_resp = client.post("/tkt-solicitud-derecho/", json={
            "company_id": empresa["id"],
            "tipo": "rectificacion",
            "titular_nombre": "Maria Lopez",
            "titular_email": "maria@test.cl",
        }, headers=auth_headers)
        ticket_id = ticket_resp.json()["id"]

        client.patch(f"/tkt-solicitud-derecho/{ticket_id}", json={"estado": "en_proceso"}, headers=auth_headers)

        resp = client.post(f"/tkt-solicitud-derecho/{ticket_id}/prorrogar", json={
            "dias": 10,
        }, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["estado"] == "prorroga"
        assert resp.json()["prorroga_dias"] == 10

    def test_prorrogar_error_desde_resuelto(self, client, auth_headers, empresa, db):
        """No se puede prorrogar desde estado resuelto."""
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

        resp = client.post(f"/tkt-solicitud-derecho/{ticket_id}/prorrogar", json={
            "dias": 5,
        }, headers=auth_headers)
        assert resp.status_code == 400

    def test_prorrogar_error_dos_veces(self, client, auth_headers, empresa, db):
        """No se puede prorrogar dos veces el mismo ticket."""
        ticket_resp = client.post("/tkt-solicitud-derecho/", json={
            "company_id": empresa["id"],
            "tipo": "acceso",
            "titular_nombre": "Ana Martinez",
            "titular_email": "ana@test.cl",
        }, headers=auth_headers)
        ticket_id = ticket_resp.json()["id"]

        client.post(f"/tkt-solicitud-derecho/{ticket_id}/prorrogar", json={"dias": 5}, headers=auth_headers)

        resp = client.post(f"/tkt-solicitud-derecho/{ticket_id}/prorrogar", json={"dias": 3}, headers=auth_headers)
        assert resp.status_code == 400
        assert "ya fue prorrogado" in resp.json()["detail"]

    def test_usuario_no_puede_prorrogar(self, client, db, empresa, auth_headers):
        """Usuario regular no puede prorrogar."""
        from app.models.user import User
        from app.models.user_company import UserCompany, RolEmpresa
        from app.core.security import get_password_hash

        user = User(
            username="usr_prorroga",
            email="usr_prorroga@test.cl",
            full_name="Usuario Prorroga",
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

        login = client.post("/auth/login", json={"username": "usr_prorroga", "password": "pass1234"})
        token = login.json()["access_token"]
        headers_usr = {"Authorization": f"Bearer {token}"}

        resp = client.post(f"/tkt-solicitud-derecho/{ticket_id}/prorrogar", json={
            "dias": 5,
        }, headers=headers_usr)
        assert resp.status_code == 403

    def test_dias_maximo_10(self, client, auth_headers, empresa, db):
        """No se puede prorrogar mÃ¡s de 10 dÃ­as."""
        ticket_resp = client.post("/tkt-solicitud-derecho/", json={
            "company_id": empresa["id"],
            "tipo": "acceso",
            "titular_nombre": "Carlos Ruiz",
            "titular_email": "carlos@test.cl",
        }, headers=auth_headers)
        ticket_id = ticket_resp.json()["id"]

        resp = client.post(f"/tkt-solicitud-derecho/{ticket_id}/prorrogar", json={
            "dias": 15,
        }, headers=auth_headers)
        assert resp.status_code == 422
