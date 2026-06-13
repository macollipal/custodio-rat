"""
Test alternativo: crea un RAT con un archivo que NO deberia caer al fallback.
Si storage_url sigue None, el problema es runtime (vars OCI mal configuradas).
"""

import requests
import base64
import sys

BASE = "https://custodio-api-qa.vercel.app"

# PDF mas grande para descartar silent fallback
PDF = b"%PDF-1.4\n" + (b"X" * 1000) + b"\n%%EOF"
PDF_B64 = base64.b64encode(PDF).decode()

r = requests.post(f"{BASE}/auth/login", json={"username": "admin", "password": "Admin1234!"}, timeout=10)
token = r.json()["access_token"]
headers = {"Authorization": f"Bearer {token}", "Origin": "https://custodio-qa.vercel.app"}

# Crear otro RAT con archivo
payload = {
    "company_id": 1,
    "nombre_proceso": "OCI DEBUG 2",
    "categoria_datos": "Test",
    "categoria_titulares": "Test",
    "finalidad": "Debug OCI runtime",
    "base_legal": "Consentimiento",
    "fuente_datos": "Directamente del titular",
    "plazo_retencion": "1 año",
    "archivo_base_legal_nombre": "debug2.pdf",
    "archivo_base_legal_tipo": "application/pdf",
    "archivo_base_legal_base64": PDF_B64,
}

r = requests.post(f"{BASE}/rats", json=payload, headers=headers, timeout=30)
print(f"POST /rats: {r.status_code}")
data = r.json()
print(f"  id: {data.get('id')}")
print(f"  archivo_base_legal_storage_url: {data.get('archivo_base_legal_storage_url')}")
print(f"  archivo_base_legal_nombre: {data.get('archivo_base_legal_nombre')}")
print(f"  tiene_archivo_base_legal: {data.get('tiene_archivo_base_legal')}")
print(f"  Completitud: {data.get('completitud')}")

# Hacer GET al RAT
if data.get('id'):
    r2 = requests.get(f"{BASE}/rats/{data['id']}", headers=headers, timeout=10)
    data2 = r2.json()
    print(f"\nGET /rats/{data['id']}:")
    print(f"  archivo_base_legal_storage_url: {data2.get('archivo_base_legal_storage_url')}")
    print(f"  archivo_base_legal_datos en respuesta: {'archivo_base_legal_datos' in data2}")
