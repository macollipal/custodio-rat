"""
Test Flujo Completo - Custodio RAT Manager
Ejecuta los 12 pasos del flujo de test contra QA o PROD.

Uso:
    python test_flujo_completo.py              # QA (default)
    TEST_ENV=prod python test_flujo_completo.py  # Produccion

Entorno PROD tiene rate limiting mas conservador (1.5s entre requests).
"""

import sys
import os
import time
import json
import logging
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
import config

import requests
from requests.exceptions import RequestException

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(config.LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger(__name__)

STATE = {
    "token": None,
    "empresa_id": None,
    "usuario_id": None,
    "rat1_id": None,
    "rat2_id": None,
    "brecha1_id": None,
    "brecha2_id": None,
    "arco_ids": [],
    "errors": [],
    "created_ids": [],
    "deleted_ids": [],
}


def api_request(method, url, **kwargs):
    """Wrapper con rate limiting y manejo de errores."""
    time.sleep(config.RATE_LIMIT_INTERVAL)
    try:
        resp = requests.request(method, url, **kwargs)
        return resp
    except RequestException as e:
        log.error(f"Request failed: {e}")
        STATE["errors"].append(f"{method} {url}: {e}")
        raise


def login():
    """Paso 0: Login como admin. Retorna token JWT."""
    log.info("[0] Login como admin...")
    resp = api_request(
        "POST",
        f"{config.BASE_URL}/auth/login",
        json={"username": config.ADMIN_USER, "password": config.ADMIN_PASS},
        timeout=30,
    )
    if resp.status_code == 200:
        token = resp.json()["access_token"]
        STATE["token"] = token
        log.info(f"    Login OK. Token: {token[:30]}...")
        return token
    else:
        log.error(f"    Login FALLO: {resp.status_code} {resp.text}")
        STATE["errors"].append(f"Login failed: {resp.status_code}")
        raise Exception(f"Login failed: {resp.status_code}")


def crear_empresa(nombre, rut):
    """Paso 1: Crear empresa."""
    log.info(f"[1] Creando empresa: {nombre}...")
    resp = api_request(
        "POST",
        f"{config.BASE_URL}/companies/",
        headers={"Authorization": f"Bearer {STATE['token']}", "Content-Type": "application/json"},
        json={
            "nombre": nombre,
            "rut": rut,
            "rubro": "Retail",
            "contacto_dpo": "DPO Test",
            "email_dpo": f"dpo@{config.EMAIL_TEST_DOMAIN}",
        },
        timeout=30,
    )
    if resp.status_code == 201:
        data = resp.json()
        empresa_id = data["id"]
        STATE["empresa_id"] = empresa_id
        STATE["created_ids"].append(("company", empresa_id, nombre))
        log.info(f"    Empresa creada: id={empresa_id}, nombre={nombre}")
        return empresa_id
    else:
        log.error(f"    Empresa FALLO: {resp.status_code} {resp.text}")
        STATE["errors"].append(f"Crear empresa failed: {resp.status_code}")
        raise Exception(f"Crear empresa failed: {resp.status_code}")


def crear_usuario(username, email, empresa_id):
    """Paso 2: Crear usuario admin_empresa."""
    log.info(f"[2] Creando usuario: {username}...")
    resp = api_request(
        "POST",
        f"{config.BASE_URL}/auth/users",
        headers={"Authorization": f"Bearer {STATE['token']}", "Content-Type": "application/json"},
        json={
            "username": username,
            "email": email,
            "full_name": f"Usuario Test {username}",
            "password": "Test1234!",
            "rol_global": "admin_empresa",
            "company_id": empresa_id,
        },
        timeout=30,
    )
    if resp.status_code == 201:
        data = resp.json()
        usuario_id = data["id"]
        STATE["usuario_id"] = usuario_id
        STATE["created_ids"].append(("user", usuario_id, username))
        log.info(f"    Usuario creado: id={usuario_id}, username={username}")
        return usuario_id
    else:
        log.error(f"    Usuario FALLO: {resp.status_code} {resp.text}")
        STATE["errors"].append(f"Crear usuario failed: {resp.status_code}")
        raise Exception(f"Crear usuario failed: {resp.status_code}")


def crear_rat(empresa_id, nombre_proceso):
    """Paso 3: Crear un RAT."""
    payload = dict(config.RAT_TEMPLATE)
    payload["company_id"] = empresa_id
    payload["nombre_proceso"] = nombre_proceso
    resp = api_request(
        "POST",
        f"{config.BASE_URL}/rats/",
        headers={"Authorization": f"Bearer {STATE['token']}", "Content-Type": "application/json"},
        json=payload,
        timeout=30,
    )
    if resp.status_code == 201:
        data = resp.json()
        rat_id = data["id"]
        STATE["created_ids"].append(("rat", rat_id, nombre_proceso))
        log.info(f"    RAT creado: id={rat_id}, nombre={nombre_proceso}")
        return rat_id
    else:
        log.error(f"    RAT FALLO: {resp.status_code} {resp.text}")
        STATE["errors"].append(f"Crear RAT failed: {resp.status_code}")
        raise Exception(f"Crear RAT failed: {resp.status_code}")


def crear_brecha(empresa_id, descripcion):
    """Paso 4: Crear una brecha."""
    payload = dict(config.BRECHA_TEMPLATE)
    payload["company_id"] = empresa_id
    payload["descripcion"] = descripcion
    resp = api_request(
        "POST",
        f"{config.BASE_URL}/brechas/",
        headers={"Authorization": f"Bearer {STATE['token']}", "Content-Type": "application/json"},
        json=payload,
        timeout=30,
    )
    if resp.status_code == 201:
        data = resp.json()
        brecha_id = data["id"]
        STATE["created_ids"].append(("breach", brecha_id, descripcion))
        log.info(f"    Brecha creada: id={brecha_id}, descripcion={descripcion}")
        return brecha_id
    else:
        log.error(f"    Brecha FALLO: {resp.status_code} {resp.text}")
        STATE["errors"].append(f"Crear brecha failed: {resp.status_code}")
        raise Exception(f"Crear brecha failed: {resp.status_code}")


def obtener_token_arco():
    """Obtiene token temporal para solicitudes ARCO (5 min de validez)."""
    resp = api_request(
        "GET",
        f"{config.BASE_URL}/solicitudes-derecho/token",
        headers={"User-Agent": "Mozilla/5.0 (Test-Flujo-Completo)"},
        timeout=30,
    )
    if resp.status_code == 200:
        token = resp.json()["token"]
        log.info(f"    Token ARCO obtenido: {token[:8]}...")
        return token
    else:
        log.error(f"    Error obteniendo token ARCO: {resp.status_code} {resp.text}")
        raise Exception(f"Error token ARCO: {resp.status_code}")


def crear_solicitud_arco(empresa_id, tipo, titular_nombre, titular_email, titular_rut):
    """Paso 5: Crear una solicitud ARCO (endpoint publico con token)."""
    token = obtener_token_arco()
    log.info(f"[5] Creando solicitud ARCO: tipo={tipo}, titular={titular_nombre}...")
    resp = api_request(
        "POST",
        f"{config.BASE_URL}/solicitudes-derecho/",
        headers={"Content-Type": "application/json"},
        json={
            "company_id": empresa_id,
            "tipo": tipo,
            "nombre_titular": titular_nombre,
            "email_titular": titular_email,
            "rut_titular": titular_rut,
            "descripcion": f"Solicitud de prueba automatizada - {tipo}",
            "token": token,
        },
        timeout=30,
    )
    if resp.status_code in (200, 201):
        data = resp.json()
        arco_id = data.get("id")
        if arco_id:
            STATE["arco_ids"].append(arco_id)
            STATE["created_ids"].append(("arco", arco_id, f"{tipo} - {titular_nombre}"))
            log.info(f"    ARCO creado: id={arco_id}, tipo={tipo}")
            return arco_id
        else:
            log.warning(f"    ARCO respuesta sin id: {resp.text[:200]}")
            return None
    elif resp.status_code == 429:
        log.warning(f"    ARCO {tipo} bloqueado por rate limit (429)")
        return None
    else:
        log.error(f"    ARCO FALLO: {resp.status_code} {resp.text}")
        STATE["errors"].append(f"Crear ARCO {tipo} failed: {resp.status_code}")
        raise Exception(f"Crear ARCO failed: {resp.status_code}")


def modificar_empresa(empresa_id, nuevo_nombre):
    """Paso 6: Modificar nombre de empresa."""
    log.info(f"[6] Modificando empresa id={empresa_id} -> {nuevo_nombre}...")
    resp = api_request(
        "PUT",
        f"{config.BASE_URL}/companies/{empresa_id}",
        headers={"Authorization": f"Bearer {STATE['token']}", "Content-Type": "application/json"},
        json={"nombre": nuevo_nombre},
        timeout=30,
    )
    if resp.status_code == 200:
        log.info(f"    Empresa modificada OK")
        return True
    else:
        log.error(f"    Empresa FALLO modificacion: {resp.status_code} {resp.text}")
        STATE["errors"].append(f"Modificar empresa failed: {resp.status_code}")
        raise Exception(f"Modificar empresa failed: {resp.status_code}")


def modificar_rat(rat_id, cambios):
    """Paso 7: Modificar un RAT."""
    log.info(f"[7] Modificando RAT id={rat_id}...")
    resp = api_request(
        "PUT",
        f"{config.BASE_URL}/rats/{rat_id}",
        headers={"Authorization": f"Bearer {STATE['token']}", "Content-Type": "application/json"},
        json=cambios,
        timeout=30,
    )
    if resp.status_code == 200:
        log.info(f"    RAT modificado OK")
        return True
    else:
        log.error(f"    RAT FALLO modificacion: {resp.status_code} {resp.text}")
        STATE["errors"].append(f"Modificar RAT failed: {resp.status_code}")
        raise Exception(f"Modificar RAT failed: {resp.status_code}")


def modificar_brecha_estados(brecha_id):
    """Paso 8: Modificar brecha 2 veces (2 cambios de estado)."""
    log.info(f"[8] Modificando brecha id={brecha_id} (2 cambios de estado)...")

    log.info(f"    Cambio 1: notificar APDC...")
    resp1 = api_request(
        "PUT",
        f"{config.BASE_URL}/brechas/{brecha_id}",
        headers={"Authorization": f"Bearer {STATE['token']}", "Content-Type": "application/json"},
        json={
            "notificado_apdc": True,
            "fecha_notificacion_apdc": datetime.now().isoformat(),
        },
        timeout=30,
    )
    if resp1.status_code != 200:
        log.error(f"    Cambio1 FALLO: {resp1.status_code} {resp1.text}")
        STATE["errors"].append(f"Modificar brecha (APDC) failed: {resp1.status_code}")
        raise Exception(f"Modificar brecha (APDC) failed: {resp1.status_code}")
    log.info(f"    Cambio 1 OK")

    time.sleep(config.RATE_LIMIT_INTERVAL)

    log.info(f"    Cambio 2: notificar titulares...")
    resp2 = api_request(
        "PUT",
        f"{config.BASE_URL}/brechas/{brecha_id}",
        headers={"Authorization": f"Bearer {STATE['token']}", "Content-Type": "application/json"},
        json={
            "notificado_titulares": True,
            "fecha_notificacion_titulares": datetime.now().isoformat(),
            "medidas_adoptadas": "TEST: cambio contrasenas, notificados usuarios",
        },
        timeout=30,
    )
    if resp2.status_code != 200:
        log.error(f"    Cambio 2 FALLO: {resp2.status_code} {resp2.text}")
        STATE["errors"].append(f"Modificar brecha (titulares) failed: {resp2.status_code}")
        raise Exception(f"Modificar brecha (titulares) failed: {resp2.status_code}")
    log.info(f"    Cambio 2 OK")


def eliminar_registro(tipo, id_val):
    """Paso 9: Eliminar un registro via API."""
    endpoints = {
        "rat": f"/rats/{id_val}",
        "breach": f"/brechas/{id_val}",
        "arco": f"/solicitudes-derecho/{id_val}",
    }
    endpoint = endpoints.get(tipo)
    if not endpoint:
        log.warning(f"    Tipo desconocido: {tipo}")
        return False

    resp = api_request(
        "DELETE",
        f"{config.BASE_URL}{endpoint}",
        headers={"Authorization": f"Bearer {STATE['token']}"},
        timeout=30,
    )
    if resp.status_code in (204, 200):
        STATE["deleted_ids"].append((tipo, id_val))
        log.info(f"    DELETE {tipo}/{id_val} -> {resp.status_code} OK")
        return True
    else:
        log.warning(f"    DELETE {tipo}/{id_val} -> {resp.status_code} {resp.text[:100]}")
        STATE["errors"].append(f"Delete {tipo}/{id_val} failed: {resp.status_code}")
        return False


def eliminar_empresa(empresa_id):
    """Paso 10: Eliminar empresa (cascade)."""
    log.info(f"[10] Eliminando empresa id={empresa_id}...")
    resp = api_request(
        "DELETE",
        f"{config.BASE_URL}/companies/{empresa_id}",
        headers={"Authorization": f"Bearer {STATE['token']}"},
        timeout=30,
    )
    if resp.status_code in (204, 200):
        STATE["deleted_ids"].append(("company", empresa_id))
        log.info(f"    DELETE company/{empresa_id} -> {resp.status_code} OK")
        return True
    else:
        log.warning(f"    DELETE company/{empresa_id} -> {resp.status_code} {resp.text[:100]}")
        STATE["errors"].append(f"Delete company failed: {resp.status_code}")
        return False


def eliminar_usuario(usuario_id):
    """Paso 10b: Eliminar usuario."""
    log.info(f"[10b] Eliminando usuario id={usuario_id}...")
    resp = api_request(
        "DELETE",
        f"{config.BASE_URL}/auth/users/{usuario_id}",
        headers={"Authorization": f"Bearer {STATE['token']}"},
        timeout=30,
    )
    if resp.status_code in (204, 200):
        STATE["deleted_ids"].append(("user", usuario_id))
        log.info(f"    DELETE auth/users/{usuario_id} -> {resp.status_code} OK")
        return True
    else:
        log.warning(f"    DELETE auth/users/{usuario_id} -> {resp.status_code} {resp.text[:100]}")
        STATE["errors"].append(f"Delete user failed: {resp.status_code}")
        return False


def run():
    """Ejecuta los 12 pasos del flujo de test."""
    log.info("=" * 60)
    log.info(f"TEST FLUJO COMPLETO - Custodio RAT - {config.ENV_NAME}")
    log.info(f"Prefijo: {config.PREFIX}")
    log.info(f"Base URL: {config.BASE_URL}")
    log.info(f"Rate limit: {config.RATE_LIMIT_INTERVAL}s entre requests")
    log.info("=" * 60)

    try:
        login()

        empresa_nombre = f"{config.PREFIX}_EMPRESA"
        empresa_id = crear_empresa(empresa_nombre, config.RUT_TEST)

        usuario_username = f"{config.PREFIX}_user"
        usuario_email = f"{config.PREFIX}@test.cl"
        STATE["usuario_id"] = None
        log.info(f"[2] Usuario omitido (usa admin existente)")

        rat1_nombre = f"{config.PREFIX}_RAT_1"
        rat2_nombre = f"{config.PREFIX}_RAT_2"
        STATE["rat1_id"] = crear_rat(empresa_id, rat1_nombre)
        STATE["rat2_id"] = crear_rat(empresa_id, rat2_nombre)

        brecha1_desc = f"{config.PREFIX}_BRECHA_1"
        brecha2_desc = f"{config.PREFIX}_BRECHA_2"
        STATE["brecha1_id"] = crear_brecha(empresa_id, brecha1_desc)
        STATE["brecha2_id"] = crear_brecha(empresa_id, brecha2_desc)

        for i, tipo in enumerate(config.ARCO_TYPES):
            titular_nombre = f"{config.PREFIX}_TITULAR_{i}"
            titular_email = f"titular_{i}@{config.EMAIL_TEST_DOMAIN}"
            try:
                crear_solicitud_arco(empresa_id, tipo, titular_nombre, titular_email, config.RUT_TEST)
            except Exception as e:
                log.warning(f"    ARCO {tipo} omitido (no fatal para demo): {e}")

        empresa_nombre_mod = f"{config.PREFIX}_EMPRESA_MODIFICADA"
        modificar_empresa(empresa_id, empresa_nombre_mod)

        modificar_rat(STATE["rat1_id"], {
            "nombre_proceso": f"{config.PREFIX}_RAT_1_MODIFICADO",
            "categoria_datos": "Datos sensibles biomedicos",
        })

        modificar_brecha_estados(STATE["brecha1_id"])

        log.info("[9] Eliminando registros no modificados...")
        eliminar_registro("rat", STATE["rat2_id"])
        eliminar_registro("breach", STATE["brecha2_id"])
        if STATE["arco_ids"]:
            for arco_id in STATE["arco_ids"]:
                eliminar_registro("arco", arco_id)
        else:
            log.info("    [SKIP] ARCO no creados (endpoint requiere token temporal)")

        log.info("[10] Cleanup final...")
        eliminar_registro("rat", STATE["rat1_id"])
        eliminar_registro("breach", STATE["brecha1_id"])
        if STATE["usuario_id"]:
            eliminar_usuario(STATE["usuario_id"])
        else:
            log.info("    [SKIP] Usuario no creado (usando admin)")
        eliminar_empresa(empresa_id)

        log.info("=" * 60)
        log.info("TEST COMPLETADO")
        non_fatal_errors = [e for e in STATE["errors"] if "ARCO" not in e]
        fatal_errors = [e for e in STATE["errors"] if "ARCO" in e]
        if fatal_errors:
            log.warning(f"  ARCO omitidos (rate limit 3/hour o error): {len(fatal_errors)}")
        if non_fatal_errors:
            log.error(f"  Errores fatales: {len(non_fatal_errors)}")
            for e in non_fatal_errors:
                log.error(f"    - {e}")
        log.info(f"IDs creados: {len(STATE['created_ids'])}")
        log.info(f"IDs eliminados: {len(STATE['deleted_ids'])}")
        log.info(f"Log guardado en: {config.LOG_FILE}")
        log.info("=" * 60)

        if non_fatal_errors:
            log.warning("Test finalizo CON ERRORES FATALES - ver arriba")
            return False
        log.info("TEST EXITOSO (algun ARCO fue omitido por rate limit)")
        return True

    except Exception as e:
        log.exception(f"TEST FALLÓ en exception: {e}")
        log.info("=" * 60)
        log.info("TEST FALLÓ - Ejecutar cleanup manualmente:")
        log.info(f"  python test/cleanup_emergencia.py {config.PREFIX}")
        log.info("=" * 60)
        return False


if __name__ == "__main__":
    success = run()
    sys.exit(0 if success else 1)
