"""
Tests para C2: validación de base legal contra enum taxativo del Art. 13.

Cubre:
- Enum BaseLegal exporta los 8 valores correctos
- Schema RATCreate valida contra BaseLegal
- Errores claros cuando valor no está en enum
- Descripciones para UI
"""
import pytest
from app.schemas.rat import (
    BaseLegal,
    BASE_LEGAL_OPTIONS,
    BASE_LEGAL_DESCRIPCIONES,
    RATCreate,
)


class TestBaseLegalEnum:
    def test_enum_tiene_8_valores(self):
        """El enum debe tener exactamente 8 valores (Art. 13 + biométricos + Otra)."""
        assert len(BaseLegal) == 8

    def test_valores_no_cambian_sin_migracion(self):
        """Los valores deben ser estables (no cambiar sin migration explícita)."""
        expected = {
            "Consentimiento del titular",
            "Ejecución de contrato",
            "Obligación legal",
            "Interés legítimo",
            "Interés vital del titular",
            "Misión de interés público",
            "Datos biométricos de identificación (Art. 16 BIS)",
            "Otra",
        }
        actual = {b.value for b in BaseLegal}
        assert actual == expected

    def test_base_legal_options_es_lista_plana(self):
        """BASE_LEGAL_OPTIONS debe ser list[str] para serialización."""
        assert isinstance(BASE_LEGAL_OPTIONS, list)
        for v in BASE_LEGAL_OPTIONS:
            assert isinstance(v, str)

    def test_descripciones_cubren_todas_las_opciones(self):
        """Cada opción debe tener descripción."""
        for opt in BASE_LEGAL_OPTIONS:
            assert opt in BASE_LEGAL_DESCRIPCIONES, f"Falta descripción para: {opt}"
            desc = BASE_LEGAL_DESCRIPCIONES[opt]
            assert isinstance(desc, str)
            assert len(desc) > 10  # descripciones reales, no stubs


class TestRATCreateValidacion:
    def _payload_valido(self, empresa_id: int = 1, **overrides) -> dict:
        base = {
            "company_id": empresa_id,
            "nombre_proceso": "Test RAT",
            "categoria_datos": "Identificación, contacto",
            "categoria_titulares": "Clientes",
            "finalidad": "Gestión de clientes",
            "base_legal": "Consentimiento del titular",
            "fuente_datos": "Titular",
            "plazo_retencion": "5 años",
        }
        base.update(overrides)
        return base

    def test_base_legal_valida_todas_las_opciones(self):
        """Cada valor del enum debe ser aceptado por el schema (a nivel sintáctico)."""
        for opt in BASE_LEGAL_OPTIONS:
            payload = self._payload_valido(base_legal=opt)
            rat = RATCreate(**payload)
            assert rat.base_legal == opt

    def test_base_legal_invalida_rechaza_con_error_explicito(self):
        """Un valor fuera del enum debe ser rechazado con mensaje claro."""
        payload = self._payload_valido(base_legal="base inventada")
        with pytest.raises(Exception) as exc_info:
            RATCreate(**payload)
        error_msg = str(exc_info.value)
        assert "base_legal" in error_msg.lower()
        assert "válidas" in error_msg.lower() or "válid" in error_msg.lower()

    def test_base_legal_vacia_rechaza(self):
        """String vacío debe rechazarse."""
        payload = self._payload_valido(base_legal="")
        with pytest.raises(Exception):
            RATCreate(**payload)

    def test_base_legal_con_espacios_se_normaliza(self):
        """Espacios al rededor deben ser stripped."""
        payload = self._payload_valido(base_legal="  Consentimiento del titular  ")
        rat = RATCreate(**payload)
        assert rat.base_legal == "Consentimiento del titular"

    def test_base_legal_case_sensitive(self):
        """Las mayúsculas importan — 'consentimiento' minúscula debe rechazarse."""
        payload = self._payload_valido(base_legal="consentimiento del titular")
        with pytest.raises(Exception):
            RATCreate(**payload)


class TestBaseLegalIntegracion:
    """Tests de integración con el endpoint POST /rats/."""

    def test_endpoint_rechaza_base_legal_invalida(
        self, client, auth_headers, empresa
    ):
        """POST /rats/ con base_legal inválida debe retornar 422."""
        payload = {
            "company_id": empresa["id"],
            "nombre_proceso": "RAT con base legal inválida",
            "categoria_datos": "Nombre",
            "categoria_titulares": "Clientes",
            "finalidad": "Test",
            "base_legal": "no-contemplada-en-ley",
            "fuente_datos": "Titular",
            "plazo_retencion": "1 año",
        }
        resp = client.post("/rats/", json=payload, headers=auth_headers)
        assert resp.status_code == 422
        detail = resp.json()["detail"][0]
        assert "base_legal" in str(detail["loc"])
        assert "válid" in detail["msg"].lower() or "valid" in detail["msg"].lower()

    def test_endpoint_acepta_todas_las_opciones_validas(
        self, client, auth_headers, empresa
    ):
        """POST /rats/ debe aceptar cada opción válida del enum.

        Excluye 'Otra' que requiere archivo adjunto cifrado (test complejo).
        """
        for opt in BASE_LEGAL_OPTIONS:
            if opt == "Otra":
                # 'Otra' requiere archivo adjunto (Art. 11+16) + ENCRYPTION_KEY
                continue
            payload = {
                "company_id": empresa["id"],
                "nombre_proceso": f"RAT con {opt[:30]}",
                "categoria_datos": "Nombre",
                "categoria_titulares": "Clientes",
                "finalidad": "Test",
                "base_legal": opt,
                "fuente_datos": "Titular",
                "plazo_retencion": "1 año",
            }
            if "Interés legítimo" in opt or "interes legitimo" in opt.lower():
                payload["test_interes_legitimo"] = '{"paso1": "Identificamos interés legítimo válido de gestión interna", "paso2": "Verificamos que no prevalecen derechos del titular", "paso3": "Medidas adoptadas para minimizar impacto en privacidad"}'
            resp = client.post("/rats/", json=payload, headers=auth_headers)
            assert resp.status_code == 201, f"Falló con base_legal={opt}: {resp.text}"
            rat_id = resp.json()["id"]
            client.delete(f"/rats/{rat_id}", headers=auth_headers)