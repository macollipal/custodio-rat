"""
Tests para QW10: Formulario Público ARCO (migrado al nuevo endpoint /publico/ejercer-derechos).
- Campos representante_nombre, representante_rut, poder_notarial_notas
- Respuesta incluye tracking_token y mensaje
- Status: 201

API canónico: POST /publico/ejercer-derechos (JSON only, sin adjuntos)
"""
import uuid


def _base_payload(empresa_id):
    return {
        "company_id": empresa_id,
        "tipo": "acceso",
        "titular_nombre": "Juan Pérez",
        "titular_rut": "12.345.678-5",
        "titular_email": "juan@perez.cl",
        "descripcion": "Quiero acceder a mis datos personales registrados en el sistema.",
    }


class TestQW10Representante:
    def test_crear_solicitud_con_representante(self, client, empresa):
        """El formulario público acepta representante_nombre con poder notarial."""
        payload = {
            **_base_payload(empresa["id"]),
            "representante_nombre": "María López",
            "representante_rut": "98.765.432-1",
            "representante_poder_notarial_notas": "Poder notarial otorgado ante notario en fecha 2026-01-15.",
        }
        resp = client.post("/publico/ejercer-derechos", json=payload)
        assert resp.status_code == 201, resp.text
        data = resp.json()
        assert "tracking_token" in data
        assert data["tracking_token"] is not None
        assert "mensaje" in data

    def test_crear_solicitud_sin_representante(self, client, empresa):
        """El formulario funciona sin campos de representante (compatibilidad)."""
        resp = client.post("/publico/ejercer-derechos", json=_base_payload(empresa["id"]))
        assert resp.status_code == 201, resp.text
        data = resp.json()
        assert "tracking_token" in data

    def test_representante_sin_poder_notarial_falla(self, client, empresa):
        """Representante sin poder_notarial_notas es rechazado con 422."""
        payload = {
            **_base_payload(empresa["id"]),
            "representante_nombre": "Ana Torres",
        }
        resp = client.post("/publico/ejercer-derechos", json=payload)
        assert resp.status_code == 422

    def test_representante_rut_sin_nombre_se_acepta(self, client, empresa):
        """representante_rut sin nombre se acepta (schema no valida solo rut)."""
        payload = {
            **_base_payload(empresa["id"]),
            "representante_rut": "11.111.111-1",
        }
        resp = client.post("/publico/ejercer-derechos", json=payload)
        assert resp.status_code == 201, resp.text


class TestQW10Archivos:
    def test_crear_solicitud_json_sin_archivos(self, client, empresa):
        """El formulario JSON acepta solicitudes sin archivos adjuntos."""
        resp = client.post("/publico/ejercer-derechos", json=_base_payload(empresa["id"]))
        assert resp.status_code == 201, resp.text
        assert "tracking_token" in resp.json()

    def test_descripcion_requerida_minima(self, client, empresa):
        """Descripción con menos de 10 caracteres es rechazada."""
        payload = {**_base_payload(empresa["id"]), "descripcion": "corta"}
        resp = client.post("/publico/ejercer-derechos", json=payload)
        assert resp.status_code == 422

    def test_empresa_inexistente_falla(self, client):
        """Empresa que no existe devuelve 404."""
        payload = {**_base_payload(99999)}
        resp = client.post("/publico/ejercer-derechos", json=payload)
        assert resp.status_code == 404

    def test_email_invalido_falla(self, client, empresa):
        """Email titular inválido devuelve 422."""
        payload = {**_base_payload(empresa["id"]), "titular_email": "no-es-email"}
        resp = client.post("/publico/ejercer-derechos", json=payload)
        assert resp.status_code == 422


class TestQW10TrackingToken:
    def test_respuesta_incluye_tracking_token(self, client, empresa):
        """La respuesta del POST incluye tracking_token para seguimiento."""
        resp = client.post("/publico/ejercer-derechos", json=_base_payload(empresa["id"]))
        assert resp.status_code == 201, resp.text
        data = resp.json()
        assert "tracking_token" in data
        assert data["tracking_token"] is not None
        assert len(data["tracking_token"]) == 36

    def test_tracking_token_es_uuid_unico(self, client, empresa):
        """Cada solicitud recibe un tracking_token único."""
        resp1 = client.post("/publico/ejercer-derechos", json={
            **_base_payload(empresa["id"]),
            "titular_email": f"uno+{uuid.uuid4().hex[:6]}@track.cl",
        })
        assert resp1.status_code == 201
        tk1 = resp1.json()["tracking_token"]

        resp2 = client.post("/publico/ejercer-derechos", json={
            **_base_payload(empresa["id"]),
            "tipo": "rectificacion",
            "titular_email": f"dos+{uuid.uuid4().hex[:6]}@track.cl",
        })
        assert resp2.status_code == 201
        tk2 = resp2.json()["tracking_token"]

        assert tk1 != tk2
