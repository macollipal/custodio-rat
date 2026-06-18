"""
Tests para QW1: Consolidación ARCO — Unificación de SolicitudDerecho y TktSolicitudDerecho.
Custodio RAT Manager — Ley 21.719.

Covers:
- Crear ticket con tipos extendidos: acceso, rectificacion, cancelacion, oposicion, bloqueo, portabilidad
- Crear ticket con prioridad "urgente" (no "alta")
- Crear ticket pasando rat_id
- Workflow bloquear RAT (Art. 8 ter): /bloquear → estado "bloqueado", RAT.bloqueado=True
- Workflow desbloquear RAT: /desbloquear → estado "resuelto", RAT.bloqueado=False
- Workflow rechazo fundado (Art. 12.5): /rechazar → estado "rechazado"
- Exportar portabilidad (Art. 9): /portabilidad/export
- Guardar datos de portabilidad: /portabilidad/guardar
"""

import pytest


def _crear_ticket(client, headers, company_id, tipo, prioridad="normal", rat_id=None):
    payload = {
        "company_id": company_id,
        "tipo": tipo,
        "prioridad": prioridad,
        "origen": "web",
        "titular_nombre": "Juan Titular",
        "titular_email": "juan@titular.cl",
        "descripcion": "Solicitud de prueba",
    }
    if rat_id is not None:
        payload["rat_id"] = rat_id
    return client.post("/tkt-solicitud-derecho/", json=payload, headers=headers)


def _crear_rat(client, headers, empresa_id):
    resp = client.post("/rats/", json={
        "company_id": empresa_id,
        "nombre_proceso": "Proceso Test RAT",
        "categoria_datos": "Nombre, email",
        "categoria_titulares": "Clientes",
        "finalidad": "Gestión comercial",
        "base_legal": "Consentimiento",
        "fuente_datos": "Titular web",
        "plazo_retencion": "5 años",
    }, headers=headers)
    if resp.status_code != 201:
        raise RuntimeError(f"No se pudo crear RAT: {resp.status_code} {resp.text}")
    return resp.json()["id"]


class TestTiposExtendidosTKT:
    def test_crear_ticket_bloqueo(self, client, auth_headers, empresa):
        """Superadmin puede crear ticket tipo bloqueo (Art. 8 ter)."""
        resp = _crear_ticket(client, auth_headers, empresa["id"], "bloqueo")
        assert resp.status_code == 200, f"Error: {resp.status_code} {resp.text}"
        data = resp.json()
        assert data["tipo"] == "bloqueo"
        assert data["estado"] == "abierto"

    def test_crear_ticket_portabilidad(self, client, auth_headers, empresa):
        """Superadmin puede crear ticket tipo portabilidad (Art. 9)."""
        resp = _crear_ticket(client, auth_headers, empresa["id"], "portabilidad")
        assert resp.status_code == 200
        assert resp.json()["tipo"] == "portabilidad"

    def test_crear_ticket_prioridad_urgente(self, client, auth_headers, empresa):
        """Prioridad correcta es urgente (no alta) según Ley 21.719."""
        resp = _crear_ticket(client, auth_headers, empresa["id"], "acceso", prioridad="urgente")
        assert resp.status_code == 200
        assert resp.json()["prioridad"] == "urgente"

    def test_crear_ticket_con_rat_id(self, client, auth_headers, empresa):
        """Ticket puede crearse con rat_id para workflow de bloqueo."""
        rat_id = _crear_rat(client, auth_headers, empresa["id"])
        resp = _crear_ticket(client, auth_headers, empresa["id"], "bloqueo", rat_id=rat_id)
        assert resp.status_code == 200
        data = resp.json()
        assert data["rat_id"] == rat_id


class TestWorkflowBloqueo:
    def test_bloquear_rat_cambia_estado_bloqueado(self, client, auth_headers, empresa):
        """POST /bloquear marca ticket como bloqueado y RAT como bloqueado."""
        rat_id = _crear_rat(client, auth_headers, empresa["id"])

        resp_tkt = _crear_ticket(client, auth_headers, empresa["id"], "bloqueo", rat_id=rat_id)
        assert resp_tkt.status_code == 200
        ticket_id = resp_tkt.json()["id"]

        resp_bloq = client.post(
            f"/tkt-solicitud-derecho/{ticket_id}/bloquear",
            json={"rat_id": rat_id, "dias_bloqueo": 5},
            headers=auth_headers,
        )
        assert resp_bloq.status_code == 200, f"Bloquear falló: {resp_bloq.status_code} {resp_bloq.text}"
        data = resp_bloq.json()
        assert data["estado"] == "bloqueado"
        assert data["rat_id"] == rat_id
        assert data["plazo_bloqueo_vencimiento"] is not None

    def test_bloquear_rat_invalido_falla(self, client, auth_headers, empresa):
        """Bloquear con rat_id de otra empresa falla."""
        resp_tkt = _crear_ticket(client, auth_headers, empresa["id"], "bloqueo")
        ticket_id = resp_tkt.json()["id"]

        resp = client.post(
            f"/tkt-solicitud-derecho/{ticket_id}/bloquear",
            json={"rat_id": 99999, "dias_bloqueo": 5},
            headers=auth_headers,
        )
        assert resp.status_code in (400, 404)

    def test_desbloquear_cambia_estado_resuelto(self, client, auth_headers, empresa):
        """POST /desbloquear marca ticket como resuelto y RAT como desbloqueado."""
        rat_id = _crear_rat(client, auth_headers, empresa["id"])

        resp_tkt = _crear_ticket(client, auth_headers, empresa["id"], "bloqueo", rat_id=rat_id)
        ticket_id = resp_tkt.json()["id"]

        client.post(
            f"/tkt-solicitud-derecho/{ticket_id}/bloquear",
            json={"rat_id": rat_id, "dias_bloqueo": 5},
            headers=auth_headers,
        )

        resp_desb = client.post(
            f"/tkt-solicitud-derecho/{ticket_id}/desbloquear",
            headers=auth_headers,
        )
        assert resp_desb.status_code == 200, f"Desbloquear falló: {resp_desb.status_code} {resp_desb.text}"
        data = resp_desb.json()
        assert data["estado"] == "resuelto"
        assert data["respuesta_texto"] is not None

    def test_desbloquear_ticket_no_bloqueado_falla(self, client, auth_headers, empresa):
        """Desbloquear un ticket que no está bloqueado retorna error."""
        resp_tkt = _crear_ticket(client, auth_headers, empresa["id"], "acceso")
        ticket_id = resp_tkt.json()["id"]

        resp = client.post(
            f"/tkt-solicitud-derecho/{ticket_id}/desbloquear",
            headers=auth_headers,
        )
        assert resp.status_code == 400


class TestWorkflowRechazo:
    def test_rechazar_solicitud_motivo_fundado(self, client, auth_headers, empresa):
        """POST /rechazar marca ticket como rechazado con motivo (Art. 12.5)."""
        resp_tkt = _crear_ticket(client, auth_headers, empresa["id"], "acceso")
        ticket_id = resp_tkt.json()["id"]

        resp_rech = client.post(
            f"/tkt-solicitud-derecho/{ticket_id}/rechazar",
            json={"motivo": "Solicitud manifiestamente infundada según Art. 12.5"},
            headers=auth_headers,
        )
        assert resp_rech.status_code == 200, f"Rechazar falló: {resp_rech.status_code} {resp_rech.text}"
        data = resp_rech.json()
        assert data["estado"] == "rechazado"
        assert data["respuesta_texto"] is not None
        assert data["respuesta_fecha"] is not None


class TestWorkflowPortabilidad:
    def test_export_portabilidad_ticket_correcto(self, client, auth_headers, empresa):
        """GET /portabilidad/export retorna datos de portabilidad."""
        resp_tkt = _crear_ticket(client, auth_headers, empresa["id"], "portabilidad")
        ticket_id = resp_tkt.json()["id"]

        resp = client.get(
            f"/tkt-solicitud-derecho/{ticket_id}/portabilidad/export",
            headers=auth_headers,
        )
        assert resp.status_code == 200, f"Export falló: {resp.status_code} {resp.text}"
        data = resp.json()
        assert data["tipo"] == "portabilidad"
        assert data["id"] == ticket_id

    def test_export_portabilidad_ticket_no_portabilidad_falla(self, client, auth_headers, empresa):
        """Exportar portabilidad en ticket que no es de portabilidad falla."""
        resp_tkt = _crear_ticket(client, auth_headers, empresa["id"], "acceso")
        ticket_id = resp_tkt.json()["id"]

        resp = client.get(
            f"/tkt-solicitud-derecho/{ticket_id}/portabilidad/export",
            headers=auth_headers,
        )
        assert resp.status_code == 400

    def test_guardar_portabilidad_marca_resuelto(self, client, auth_headers, empresa):
        """POST /portabilidad/guardar guarda datos y marca ticket como resuelto."""
        resp_tkt = _crear_ticket(client, auth_headers, empresa["id"], "portabilidad")
        ticket_id = resp_tkt.json()["id"]

        datos_json = '{"nombre":"Juan","datos":["email","nombre"]}'

        resp = client.post(
            f"/tkt-solicitud-derecho/{ticket_id}/portabilidad/guardar",
            json={"portability_data": datos_json},
            headers=auth_headers,
        )
        assert resp.status_code == 200, f"Guardar portabilidad falló: {resp.status_code} {resp.text}"
        data = resp.json()
        assert data["estado"] == "resuelto"
        assert data["portability_data"] == datos_json


class TestAutorizacionWorkflows:
    def test_usuario_no_puede_bloquear(self, client, db, auth_headers, empresa):
        """Usuario regular no puede bloquear RATs."""
        from app.models.user import User
        from app.models.user_company import UserCompany, RolEmpresa
        from app.core.security import get_password_hash

        user = User(
            username="usr_bloqueo_test",
            email="usr_bloqueo@test.cl",
            full_name="Usuario Bloqueo Test",
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

        login = client.post("/auth/login", json={"username": "usr_bloqueo_test", "password": "pass1234"})
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        rat_id = _crear_rat(client, auth_headers, empresa["id"])
        resp_tkt = _crear_ticket(client, auth_headers, empresa["id"], "bloqueo")
        ticket_id = resp_tkt.json()["id"]

        resp = client.post(
            f"/tkt-solicitud-derecho/{ticket_id}/bloquear",
            json={"rat_id": rat_id, "dias_bloqueo": 5},
            headers=headers,
        )
        assert resp.status_code == 403
