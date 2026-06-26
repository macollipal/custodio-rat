"""
Tests para sanitizacion PII en exports (Art. 5 Ley 21.719 - principio de minimizacion).
Cubre sanitize_pii() de app/core/pii.py que se aplica en CSV y PDF.
"""
import pytest

from app.core.pii import sanitize_pii


class TestPiiSanitizationRut:
    """Tests de sanitizacion de RUT chileno formato XX.XXX.XXX-X."""

    @pytest.mark.parametrize("input_text,expected", [
        ("76.123.456-7", "76.123.456-*"),
        ("RUT: 12.345.678-9", "RUT: 12.345.678-*"),
        ("76.123.456-K", "76.123.456-*"),
        ("11.222.333-5 contacto", "11.222.333-* contacto"),
    ])
    def test_sanitize_rut_formato_punto_guion(self, input_text, expected):
        assert sanitize_pii(input_text) == expected

    def test_sin_rut_no_altera(self):
        assert sanitize_pii("Texto sin RUT aqui") == "Texto sin RUT aqui"

    def test_rut_malformado_no_se_altera(self):
        assert sanitize_pii("123.456-7") == "123.456-7"


class TestPiiSanitizationRun:
    """Tests de sanitizacion de RUN formato XXXXXXXX-X (sin puntos)."""

    @pytest.mark.parametrize("input_text,expected", [
        ("RUN 12345678-5", "RUN 12345678-*"),
        ("7654321-9 titular", "7654321-* titular"),
    ])
    def test_sanitize_run_sin_puntos(self, input_text, expected):
        assert sanitize_pii(input_text) == expected


class TestPiiSanitizationEmail:
    """Tests de sanitizacion de emails."""

    @pytest.mark.parametrize("input_text,expected", [
        ("juan.perez@empresa.cl", "j***@empresa.cl"),
        ("contacto: maria@test.cl", "contacto: m***@test.cl"),
    ])
    def test_sanitize_email_basico(self, input_text, expected):
        assert sanitize_pii(input_text) == expected

    def test_sanitize_email_usuario_1_caracter_retorna_mask_minimo(self):
        assert sanitize_pii("a@b.cl") == "*@b.cl"

    def test_sin_email_no_altera(self):
        assert sanitize_pii("Texto sin email") == "Texto sin email"


class TestPiiSanitizationIpv4:
    """Tests de sanitizacion de direcciones IPv4."""

    @pytest.mark.parametrize("input_text,expected", [
        ("192.168.1.100", "***.***.***.100"),
        ("IP: 10.0.0.1 servidor", "IP: ***.***.***.1 servidor"),
        ("172.16.254.1", "***.***.***.1"),
    ])
    def test_sanitize_ipv4(self, input_text, expected):
        assert sanitize_pii(input_text) == expected

    def test_sin_ip_no_altera(self):
        assert sanitize_pii("Texto sin IP") == "Texto sin IP"

    def test_ip_formato_incorrecto_matchea_regex(self):
        """El regex acepta cualquier secuencia de 4 octetos numericos (1-3 digitos c/u)."""
        assert sanitize_pii("999.999.999.999") == "***.***.***.999"


class TestPiiSanitizationCombinado:
    """Tests de combinacion de multiples tipos de PII en un mismo texto."""

    def test_multiples_tipos_pii_en_texto(self):
        text = "RUT 76.123.456-7, email juan@test.cl, IP 192.168.1.1"
        result = sanitize_pii(text)
        assert "76.123.456-*" in result
        assert "j***@test.cl" in result
        assert "***.***.***.1" in result
        assert "76.123.456-7" not in result
        assert "juan@test.cl" not in result
        assert "192.168.1.1" not in result

    def test_idempotente(self):
        text = "RUT 76.123.456-7"
        once = sanitize_pii(text)
        twice = sanitize_pii(once)
        assert once == twice


class TestPiiSanitizationEdgeCases:
    """Casos borde y entradas invalidas."""

    def test_none_retorna_empty_string(self):
        assert sanitize_pii(None) == ""

    def test_empty_string_retorna_empty(self):
        assert sanitize_pii("") == ""

    def test_non_string_retorna_el_mismo_valor(self):
        """Non-string no se modifica; sanitize_pii retorna el valor tal cual."""
        assert sanitize_pii(123) == 123

    def test_texto_largo_con_pii(self):
        text = "A" * 1000 + " RUT 12.345.678-9 " + "B" * 1000
        result = sanitize_pii(text)
        assert "12.345.678-*" in result
        assert "A" * 1000 in result
        assert "B" * 1000 in result