"""
Tests para QW6: Plantillas de respuesta por tipo de derecho ARCO.
Custodio RAT Manager — Ley 21.719 Art. 12.

Covers:
- CRUD de plantillas (solo admin_empresa y superadmin)
- Seed de 5 plantillas por defecto al primer acceso
- Listar plantillas por tipo
- Renderizado de plantillas con variables
- Responder ticket con plantilla_id
"""

import pytest


class TestPlantillaCRUD:
    def test_superadmin_puede_crear_plantilla(self, client, auth_headers, empresa):
        """Superadmin puede crear una plantilla."""
        resp = client.post("/tkt-plantillas/", json={
            "tipo": "acceso",
            "nombre": "Mi plantilla acceso",
            "contenido": "Estimado {{nombre_titular}}: Le informamos que...",
            "activo": True,
        }, headers=auth_headers)
        assert resp.status_code == 200, f"Error: {resp.status_code} {resp.text}"
        data = resp.json()
        assert data["tipo"] == "acceso"
        assert data["nombre"] == "Mi plantilla acceso"
        assert data["id"] is not None

    def test_usuario_no_puede_crear_plantilla(self, client, db, empresa):
        """Usuario regular no puede crear plantillas."""
        from app.models.user import User
        from app.models.user_company import UserCompany, RolEmpresa
        from app.core.security import get_password_hash

        user = User(
            username="usr_plant_test",
            email="usr_plant@test.cl",
            full_name="Usuario Plantilla Test",
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

        login = client.post("/auth/login", json={"username": "usr_plant_test", "password": "pass1234"})
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        resp = client.post("/tkt-plantillas/", json={
            "tipo": "acceso",
            "nombre": "Plantilla Test",
            "contenido": "Texto",
        }, headers=headers)
        assert resp.status_code == 403

    def test_listar_plantillas_vacia_seed(self, client, auth_headers, empresa):
        """Primera llamada a GET /tkt-plantillas/ hace seed de 5 plantillas."""
        resp = client.get("/tkt-plantillas/", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) >= 5

    def test_listar_plantillas_por_tipo(self, client, auth_headers, empresa):
        """GET /tkt-plantillas/?tipo=acceso retorna solo plantillas de acceso."""
        resp = client.get("/tkt-plantillas/?tipo=acceso", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        for p in data:
            assert p["tipo"] == "acceso"

    def test_actualizar_plantilla(self, client, auth_headers, empresa):
        """PUT /tkt-plantillas/{id} actualiza plantilla."""
        resp = client.post("/tkt-plantillas/", json={
            "tipo": "rectificacion",
            "nombre": "Plantilla original",
            "contenido": "Contenido original",
        }, headers=auth_headers)
        plantilla_id = resp.json()["id"]

        resp2 = client.put(f"/tkt-plantillas/{plantilla_id}", json={
            "nombre": "Plantilla actualizada",
            "contenido": "Contenido nuevo",
        }, headers=auth_headers)
        assert resp2.status_code == 200
        data = resp2.json()
        assert data["nombre"] == "Plantilla actualizada"
        assert data["contenido"] == "Contenido nuevo"

    def test_eliminar_plantilla(self, client, auth_headers, empresa):
        """DELETE /tkt-plantillas/{id} elimina plantilla."""
        resp = client.post("/tkt-plantillas/", json={
            "tipo": "cancelacion",
            "nombre": "Para eliminar",
            "contenido": "Contenido",
        }, headers=auth_headers)
        plantilla_id = resp.json()["id"]

        resp2 = client.delete(f"/tkt-plantillas/{plantilla_id}", headers=auth_headers)
        assert resp2.status_code == 200

        resp3 = client.get(f"/tkt-plantillas/{plantilla_id}", headers=auth_headers)
        assert resp3.status_code == 404

    def test_obtener_plantilla_inexistente_404(self, client, auth_headers):
        """GET /tkt-plantillas/99999 retorna 404."""
        resp = client.get("/tkt-plantillas/99999", headers=auth_headers)
        assert resp.status_code == 404


class TestPlantillaRender:
    def test_render_plantilla_sustituye_variables(self, client, auth_headers, empresa):
        """El renderizado sustituye {{nombre_titular}}, {{empresa}}, etc."""
        resp = client.post("/tkt-plantillas/", json={
            "tipo": "acceso",
            "nombre": "Test render",
            "contenido": "Hola {{nombre_titular}}, de parte de {{empresa}}, fecha {{fecha}}, sol {{numero_solicitud}}",
        }, headers=auth_headers)
        plantilla_id = resp.json()["id"]

        resp2 = client.get(f"/tkt-plantillas/{plantilla_id}", headers=auth_headers)
        data = resp2.json()
        assert "{{nombre_titular}}" in data["contenido"]

    def test_seed_plantillas_tiene_5_tipos(self, client, auth_headers, empresa):
        """Seed incluye plantillas para acceso, rectificacion, cancelacion, oposicion, bloqueo."""
        resp = client.get("/tkt-plantillas/", headers=auth_headers)
        data = resp.json()
        tipos = {p["tipo"] for p in data}
        assert "acceso" in tipos
        assert "rectificacion" in tipos
        assert "cancelacion" in tipos
        assert "oposicion" in tipos
        assert "bloqueo" in tipos


class TestResponderConPlantilla:
    def test_responder_ticket_con_plantilla_id(self, client, auth_headers, empresa):
        """PATCH con plantilla_id renders template y marca resuelto."""
        resp_plantilla = client.get("/tkt-plantillas/?tipo=acceso", headers=auth_headers)
        plantillas = resp_plantilla.json()
        assert len(plantillas) > 0
        plantilla_id = plantillas[0]["id"]

        resp_tkt = client.post("/tkt-solicitud-derecho/", json={
            "company_id": empresa["id"],
            "tipo": "acceso",
            "titular_nombre": "Pedro Test",
            "titular_email": "pedro@test.cl",
        }, headers=auth_headers)
        assert resp_tkt.status_code == 200
        ticket_id = resp_tkt.json()["id"]

        resp_patch = client.patch(
            f"/tkt-solicitud-derecho/{ticket_id}",
            json={"plantilla_id": plantilla_id},
            headers=auth_headers,
        )
        assert resp_patch.status_code == 200, f"Error: {resp_patch.status_code} {resp_patch.text}"
        data = resp_patch.json()
        assert data["estado"] == "resuelto"
        assert data["respuesta_texto"] is not None
        assert "{{nombre_titular}}" not in data["respuesta_texto"]
        assert "Pedro Test" in data["respuesta_texto"]

    def test_respuesta_texto_prevalece_sobre_plantilla(self, client, auth_headers, empresa):
        """Si se envía both respuesta_texto y plantilla_id, prevalece respuesta_texto."""
        resp_plantilla = client.get("/tkt-plantillas/?tipo=acceso", headers=auth_headers)
        plantilla_id = resp_plantilla.json()[0]["id"]

        resp_tkt = client.post("/tkt-solicitud-derecho/", json={
            "company_id": empresa["id"],
            "tipo": "acceso",
            "titular_nombre": "Juan Test",
            "titular_email": "juan@test.cl",
        }, headers=auth_headers)
        ticket_id = resp_tkt.json()["id"]

        resp_patch = client.patch(
            f"/tkt-solicitud-derecho/{ticket_id}",
            json={"respuesta_texto": "Mi respuesta directa", "plantilla_id": plantilla_id},
            headers=auth_headers,
        )
        assert resp_patch.status_code == 200
        data = resp_patch.json()
        assert data["respuesta_texto"] == "Mi respuesta directa"

    def test_plantilla_inexistente_retorna_404(self, client, auth_headers, empresa):
        """PATCH con plantilla_id inexistente retorna 404."""
        resp_tkt = client.post("/tkt-solicitud-derecho/", json={
            "company_id": empresa["id"],
            "tipo": "acceso",
            "titular_nombre": "Laura Test",
            "titular_email": "laura@test.cl",
        }, headers=auth_headers)
        ticket_id = resp_tkt.json()["id"]

        resp_patch = client.patch(
            f"/tkt-solicitud-derecho/{ticket_id}",
            json={"plantilla_id": 99999},
            headers=auth_headers,
        )
        assert resp_patch.status_code == 404
