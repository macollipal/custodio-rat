"""
Test E2E OCI contra Vercel QA.
1. Login con usuario admin
2. Crear RAT con PDF de prueba
3. Verificar que archivo_base_legal_storage_url aparece en respuesta
4. Descargar el archivo via GET /rats/{id}/archivo
5. Verificar que el contenido es identico
"""

import requests
import base64
import json
import sys

BASE = "https://custodio-api-qa.vercel.app"

# PDF minimo valido (1 pagina de prueba)
PDF_CONTENT = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >>
endobj
4 0 obj
<< /Length 44 >>
stream
BT /F1 12 Tf 100 700 Td (Test OCI QA) Tj ET
endstream
endobj
xref
0 5
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000109 00000 n
0000000206 00000 n
trailer
<< /Size 5 /Root 1 0 R >>
startxref
300
%%EOF"""

PDF_B64 = base64.b64encode(PDF_CONTENT).decode()

failures = []
warnings = []

def check(name, ok, detail=""):
    icon = "[OK]" if ok else "[FAIL]"
    print(f"  {icon} {name}: {detail}")
    if not ok:
        failures.append(name)
    return ok

print("=" * 60)
print("E2E TEST - OCI Storage en Vercel QA")
print("=" * 60)

# 1. Health checks
print("\n[1] HEALTH")
try:
    r = requests.get(f"{BASE}/health", timeout=10)
    check("Backend health", r.status_code == 200, f"status={r.status_code}")
except Exception as e:
    check("Backend health", False, str(e))

try:
    r = requests.get(f"{BASE}/health/db", timeout=10)
    ok = r.status_code == 200 and r.json().get("status") == "ok"
    check("DB health", ok, f"status={r.status_code} latency={r.json().get('latency_ms')}ms")
except Exception as e:
    check("DB health", False, str(e))

# 2. Login
print("\n[2] LOGIN")
token = None
try:
    r = requests.post(f"{BASE}/auth/login", json={"username": "admin", "password": "Admin1234!"}, timeout=10)
    if check("Login admin/admin", r.status_code == 200, f"status={r.status_code}"):
        data = r.json()
        token = data.get("access_token")
        check("Token recibido", token is not None, f"len={len(token) if token else 0}")
    else:
        print(f"  Body: {r.text[:200]}")
        failures.append("Login fallo - abortando")
        sys.exit(1)
except Exception as e:
    check("Login", False, str(e))
    sys.exit(1)

# 3. Listar companies para obtener una valida
print("\n[3] EMPRESAS")
headers = {"Authorization": f"Bearer {token}", "Origin": "https://custodio-qa.vercel.app"}
company_id = None
try:
    r = requests.get(f"{BASE}/companies", headers=headers, timeout=10)
    if r.status_code == 200:
        data = r.json()
        companies = data.get("empresas", data) if isinstance(data, dict) else data
        if isinstance(companies, list) and len(companies) > 0:
            company_id = companies[0]["id"]
            check("Company obtenida", True, f"id={company_id} nombre={companies[0].get('nombre')}")
        else:
            print(f"  Body: {r.text[:200]}")
            check("Hay companies", False, "lista vacia")
    else:
        print(f"  Status: {r.status_code}")
        print(f"  Body: {r.text[:200]}")
        check("Listar companies", False)
except Exception as e:
    check("Companies", False, str(e))

if not company_id:
    print("\n[ERROR] No se puede continuar sin company_id")
    sys.exit(1)

# 4. Crear RAT con PDF
print("\n[4] CREAR RAT CON PDF")
rat_id = None
storage_url = None
try:
    payload = {
        "company_id": company_id,
        "nombre_proceso": "TEST OCI E2E - QA",
        "categoria_datos": "Datos identificativos",
        "categoria_titulares": "Empleados",
        "finalidad": "Test de integración OCI - automatizado",
        "base_legal": "Consentimiento",
        "fuente_datos": "Directamente del titular",
        "plazo_retencion": "1 año",
        "archivo_base_legal_nombre": "test_oci.pdf",
        "archivo_base_legal_tipo": "application/pdf",
        "archivo_base_legal_base64": PDF_B64,
    }
    r = requests.post(f"{BASE}/rats", json=payload, headers=headers, timeout=30)
    if check("POST /rats", r.status_code in (200, 201), f"status={r.status_code}"):
        data = r.json()
        rat_id = data.get("id")
        storage_url = data.get("archivo_base_legal_storage_url")
        tiene_archivo = data.get("tiene_archivo_base_legal")
        check("RAT id recibido", rat_id is not None, f"id={rat_id}")
        check("tiene_archivo_base_legal", tiene_archivo is True, f"value={tiene_archivo}")
        check("archivo_base_legal_storage_url presente", storage_url is not None and len(storage_url) > 0,
              f"value={storage_url[:60] if storage_url else 'None'}...")
    else:
        print(f"  Body: {r.text[:300]}")
        failures.append("Crear RAT fallo")
except Exception as e:
    check("Crear RAT", False, str(e))

# 5. Descargar archivo
print("\n[5] DESCARGAR ARCHIVO")
if rat_id:
    try:
        r = requests.get(f"{BASE}/rats/{rat_id}/archivo", headers=headers, timeout=30)
        if check(f"GET /rats/{rat_id}/archivo", r.status_code == 200, f"status={r.status_code}"):
            content = r.content
            check("Content-Length", len(content) == len(PDF_CONTENT), f"got={len(content)} expected={len(PDF_CONTENT)}")
            check("Contenido identico", content == PDF_CONTENT, "bytes coinciden")
        else:
            print(f"  Body: {r.text[:200]}")
            failures.append("Descargar archivo fallo")
    except Exception as e:
        check("Descargar", False, str(e))

# 6. Listar archivos en OCI bucket (solo metadata - via storage backend NO accesible desde test)
print("\n[6] VERIFICACION FINAL")
if storage_url:
    print(f"  Archivo en OCI: {storage_url}")
    if storage_url.startswith("rats/"):
        check("Path en OCI correcto", True, f"prefix=rats/")
    else:
        check("Path en OCI", False, f"path inesperado: {storage_url}")

# Resumen
print("\n" + "=" * 60)
if failures:
    print(f"[FAIL] {len(failures)} fallos:")
    for f in failures:
        print(f"  - {f}")
    sys.exit(1)
else:
    print("[OK] Todos los tests E2E pasaron")
    sys.exit(0)
