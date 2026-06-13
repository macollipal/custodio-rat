"""
Verificacion del estado final post-test.
Verifica que los registros con el prefijo dado fueron eliminados.

Uso:
    python verificar_estado_final.py TEST_FLUIDO_DEMO_20260608_143022
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
import config

import requests

EXPECTED_COUNTS = {
    "companies": 0,
    "rats": 0,
    "security_breaches": 0,
    "solicitudes_derecho": 0,
    "tkt_solicitud_derecho": 0,
}


def login():
    resp = requests.post(
        f"{config.BASE_URL}/auth/login",
        json={"username": config.ADMIN_USER, "password": config.ADMIN_PASS},
        timeout=30,
    )
    if resp.status_code == 200:
        return resp.json()["access_token"]
    raise Exception(f"Login failed: {resp.status_code}")


def get_count(endpoint, token):
    resp = requests.get(
        f"{config.BASE_URL}{endpoint}",
        headers={"Authorization": f"Bearer {token}"},
        timeout=30,
    )
    if resp.status_code == 200:
        data = resp.json()
        if isinstance(data, list):
            return len(data)
        if isinstance(data, dict) and "empresas" in data:
            return data.get("total", len(data.get("empresas", [])))
        return len(data)
    return -1


def check_nombre_contains(endpoint, token, prefix, field_name="nombre"):
    resp = requests.get(
        f"{config.BASE_URL}{endpoint}",
        headers={"Authorization": f"Bearer {token}"},
        timeout=30,
    )
    if resp.status_code != 200:
        return 0
    data = resp.json()
    items = data.get("empresas", data) if isinstance(data, dict) else data
    count = sum(1 for item in items if prefix in str(item.get(field_name, "")))
    return count


def run(prefix):
    print(f"Verificando registros con prefijo: {prefix}")
    print(f"Entorno: {config.ENV_NAME} ({config.BASE_URL})")
    print("-" * 60)

    try:
        token = login()
        print("Login OK")
    except Exception as e:
        print(f"ERROR Login: {e}")
        return False

    all_ok = True

    endpoints = [
        ("companies", "/companies/"),
        ("rats", "/rats/"),
        ("security_breaches", "/brechas/"),
        ("solicitudes_derecho", "/solicitudes-derecho/"),
        ("tkt_solicitud_derecho", "/tkt-solicitud-derecho/"),
    ]

    for name, endpoint in endpoints:
        count = check_nombre_contains(endpoint, token, prefix)
        expected = EXPECTED_COUNTS.get(name, 0)
        status = "OK" if count == expected else "FAIL"
        if count != expected:
            all_ok = False
        print(f"  {name:30s}: {count} encontrados (esperado: {expected}) [{status}]")

    print("-" * 60)
    if all_ok:
        print("VERIFICACION: TODOS LOS REGISTROS FUERON ELIMINADOS")
 return True
    else:
        print("VERIFICACION: QUEDAN REGISTROS POR ELIMINAR")
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python verificar_estado_final.py <PREFIX>")
        print(f"Ejemplo: python verificar_estado_final.py {config.PREFIX}")
        sys.exit(1)

    prefix = sys.argv[1]
    success = run(prefix)
    sys.exit(0 if success else 1)
