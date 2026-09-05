"""Tests QW4 ARCO: Dashboard 'derechos más ejercidos' (por_tipo).

Custodio RAT Manager - Ley 21.719 Art. 12.
"""


def _crear_ticket(client, headers, company_id, tipo):
    return client.post("/tkt-solicitud-derecho/", json={
        "company_id": company_id,
        "tipo": tipo,
        "prioridad": "normal",
        "origen": "web",
        "titular_nombre": "Test User QW4",
        "titular_email": "qw4@test.cl",
        "descripcion": "QW4 test",
    }, headers=headers)


def test_dashboard_incluye_por_tipo(client, auth_headers, empresa):
    """QW4: dashboard incluye agrupamiento por tipo (derechos más ejercidos)."""
    company_id = empresa["id"]

    # Crear 2 tickets de acceso + 1 de cada uno
    for tipo in ["acceso", "acceso", "rectificacion", "cancelacion"]:
        resp = _crear_ticket(client, auth_headers, company_id, tipo)
        assert resp.status_code in (200, 201), f"Fallo creando ticket {tipo}: {resp.text}"

    # Consultar dashboard
    resp = client.get(f"/tkt-solicitud-derecho/dashboard?company_id={company_id}", headers=auth_headers)
    assert resp.status_code == 200, resp.text
    data = resp.json()

    assert "por_tipo" in data, f"QW4: dashboard debe incluir 'por_tipo'. Keys: {list(data.keys())}"
    por_tipo = data["por_tipo"]
    assert isinstance(por_tipo, dict), f"por_tipo debe ser dict, got {type(por_tipo)}"

    # Verificar conteo
    assert por_tipo.get("acceso", 0) >= 2, f"Debe contar >=2 tickets de acceso, got {por_tipo}"
    assert por_tipo.get("rectificacion", 0) >= 1, f"Debe contar >=1 ticket de rectificacion, got {por_tipo}"
    assert por_tipo.get("cancelacion", 0) >= 1, f"Debe contar >=1 ticket de cancelacion, got {por_tipo}"


def test_dashboard_por_tipo_vacio_sin_tickets(client, auth_headers, empresa):
    """QW4: por_tipo es dict vacio si no hay tickets (no falla)."""
    company_id = empresa["id"]
    resp = client.get(f"/tkt-solicitud-derecho/dashboard?company_id={company_id}", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "por_tipo" in data
    assert isinstance(data["por_tipo"], dict)