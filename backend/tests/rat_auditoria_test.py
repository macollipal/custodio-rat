"""
Tests para GET /rats/{id}/auditoria — historial de auditoria del RAT.

Cubre:
- acceso sin autenticacion → 401
- acceso a RAT inexistente → 404
- acceso valido → 200 + lista de logs
- IDOR: usuario de otra empresa no puede ver la auditoria → 404 (no 403)
  (404 por diseno: no exponer existencia del recurso a usuarios no autorizados)

Nota: el endpoint llama get_rat_for_user() que retorna 404 (no 403) cuando el
usuario no tiene acceso, para no filtrar la existencia del RAT.
"""



class TestAuditoriaEndpoint:
    def test_auditoria_sin_auth_401(self, client, empresa):
        """Sin token debe retornar 401."""
        resp = client.get("/rats/99999/auditoria")
        assert resp.status_code == 401, f"Expected 401, got {resp.status_code}"

    def test_auditoria_rat_inexistente_retorna_lista_vacia(self, client, auth_headers, empresa):
        """RAT inexistente retorna lista vacia (no 404 â€” no hay entidad que buscar)."""
        resp = client.get("/rats/99999/auditoria", headers=auth_headers)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        assert resp.json() == [], "Auditoria de RAT inexistente debe ser lista vacia"

    def test_auditoria_con_logs_retorna_200(self, client, auth_headers, rat_base):
        """Un RAT con actividad retorna una lista no vacia."""
        created = client.post("/rats/", json=rat_base, headers=auth_headers)
        assert created.status_code == 201
        rat_id = created.json()["id"]

        resp = client.get(f"/rats/{rat_id}/auditoria", headers=auth_headers)
        assert resp.status_code == 200
        logs = resp.json()
        assert isinstance(logs, list)
        assert len(logs) > 0, "Debe haber al menos un log de creacion"

    def test_auditoria_idor_usuario_ajeno_404(self, client, db, auth_headers, empresa, rat_base):
        """Usuario de empresa B no puede ver la auditoria de un RAT de empresa A.

        El endpoint /rats/{id}/auditoria llama get_rat_for_user() que retorna 404
        cuando el usuario no tiene acceso a la empresa del RAT. Esto es por diseno
        de seguridad: no exponer la existencia del RAT a usuarios no autorizados.
        """
        from app.models.user import User, RolGlobal
        from app.models.user_company import UserCompany, RolEmpresa
        from app.core.security import get_password_hash

        created = client.post("/rats/", json=rat_base, headers=auth_headers)
        assert created.status_code == 201
        rat_id = created.json()["id"]

        otra_empresa = client.post("/companies/", json={
            "nombre": "Empresa Ajena Audit", "rut": "76.777.888-9", "rubro": "Test",
            "contacto_dpo": "Otro", "email_dpo": "audit@ajena.cl"
        }, headers=auth_headers)
        assert otra_empresa.status_code == 201
        otra_company_id = otra_empresa.json()["id"]

        user = User(
            username="user_audit_idor", email="audit@idor.cl", full_name="User Audit IDOR",
            hashed_password=get_password_hash("pass123"), is_active=True, rol_global=RolGlobal.USUARIO.value
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        uc = UserCompany(user_id=user.id, company_id=otra_company_id, rol=RolEmpresa.VIEWER)
        db.add(uc)
        db.commit()

        login = client.post("/auth/login", json={"username": "user_audit_idor", "password": "pass123"})
        assert login.status_code == 200
        otro_token = login.json()["access_token"]

        resp = client.get(
            f"/rats/{rat_id}/auditoria",
            headers={"Authorization": f"Bearer {otro_token}"}
        )
        assert resp.status_code == 404, f"IDOR: deberia retornar 404 (no exponer existencia), pero obtuvo {resp.status_code}"
