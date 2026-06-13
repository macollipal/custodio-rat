"""
Script Generador — Documentos v1.2
====================================
Crea los scripts build_v1_2.py para cada documento que requiere actualización
y los ejecuta para generar los .docx en documentacion_oficial/

Documentos a actualizar a v1.2:
- 08_API (6 endpoints Feriados nuevos)
- 09_Backlog (deuda técnica seguridad)
- 10_Plan_QA (nuevos TC de seguridad)
- 12_Manual_Tecnico (nuevo módulo Feriados)
- Matriz_Trazabilidad (nuevos RF/HU/CU/TC)
"""
import os
import shutil

_BUILD_DIR = r"C:\Users\chelo\Desktop\RAT_opencode\paso\desarrollo_de_software_estandar\_build"
_OUT_DIR = r"C:\Users\chelo\Desktop\RAT_opencode\docs\documentacion_oficial"
_AUDIT_DIR = r"C:\Users\chelo\Desktop\RAT_opencode\auditorias\2026-06-08_auditoria_v1.2"

os.makedirs(_OUT_DIR, exist_ok=True)

# =============================================================================
# 08_API_v1_2 — Módulo Feriados (6 endpoints)
# =============================================================================
BUILD_08_V12 = r"""\"\"\"
Build 08 — Documentación de APIs v1.2
======================================
Genera: docs/documentacion_oficial/08_API_Custodio_RAT_Manager_v1.2.docx

Cambios v1.2:
- Agregado módulo Feriados (/admin/feriados/*)
\"\"\"
import os
import sys
_THIS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _THIS)
from _theme_custodio import *
_OUT_DIR = r"C:\\Users\\chelo\\Desktop\\RAT_opencode\\docs\\documentacion_oficial"
ASSETS_DIR = os.path.join(_OUT_DIR, "assets")
OUT_FILE = os.path.join(_OUT_DIR, "08_API_Custodio_RAT_Manager_v1.2.docx")
DOC_CODE = "CUST-DOC-08"
DOC_TITLE = "Documentación de APIs"
DOC_VERSION = "v1.2"
DOC_DATE = "Junio 2026"

def build():
    doc = new_document()
    add_header_footer(doc, DOC_TITLE)
    add_cover(doc, title="DOCUMENTACIÓN DE APIs",
              subtitle="Catálogo completo de endpoints REST · FastAPI + JWT",
              code=DOC_CODE)
    add_version_control(doc, DOC_CODE, DOC_TITLE, changes=[
        ("1.0", "Junio 2026", "Catálogo inicial de endpoints, derivado de app/routes/*."),
        ("1.1", "Junio 2026", "Agregado módulo AI (/ai/ask), RATs sugeridos y Tickets ARCO."),
        ("1.2", "Junio 2026", "_Agregado módulo Feriados (/admin/feriados/*) con 6 endpoints nuevos._"),
    ])
    add_toc(doc)
    fig_counter = [0]; tab_counter = [0]

    # === 1. Introducción ===
    doc.add_heading("1. Introducción", level=1)
    add_paragraph(doc, f"Este documento cataloga todos los endpoints REST de {BRAND_FULL}.")
    add_paragraph(doc, "Backend: FastAPI 0.115 + Uvicorn ASGI + Neon PostgreSQL.")

    # === 2. Autenticación ===
    doc.add_heading("2. Autenticación", level=1)
    add_paragraph(doc, "JWT Bearer token en header Authorization. Cookies httpOnly para web.")

    # === 3. Endpoints por módulo ===
    doc.add_heading("3. Endpoints por módulo", level=1)

    # --- 3.X Módulo Feriados (NUEVO) ---
    doc.add_heading("3.X Módulo Feriados", level=2)
    add_paragraph(doc, "_Nuevo módulo agregado en auditoría v1.2 para gestión de feriados nacionales chilenos._")

    feriados_endpoints = [
        ["GET", "/admin/feriados/", "list_feriados", "Lista feriados por año. Query: anio (int, opcional)"],
        ["POST", "/admin/feriados/", "create_feriado", "Crea un feriado individual. Body: {fecha, nombre, tipo}"],
        ["DELETE", "/admin/feriados/{id}", "delete_feriado", "Elimina un feriado por ID"],
        ["POST", "/admin/feriados/upload", "upload_feriados_csv", "Upload bulk CSV con encoding UTF-8 BOM. Body: multipart/form-data"],
        ["GET", "/admin/feriados/export", "export_feriados", "Exporta feriados como CSV. Query: anio (int, opcional)"],
    ]
    add_styled_table(doc, ["Método", "Ruta", "Función", "Descripción"],
                     feriados_endpoints, col_widths_cm=[2.0, 4.5, 4.0, 6.0],
                     first_col_bold=True)

    doc.add_paragraph()
    add_nota(doc, "Los feriados se usan en el cálculo de fechas límite de atención de Tickets ARCO. "
                  "El sistema incluye feriados chilenos pre-cargados hasta 2040.")

    # === 4. Códigos de error ===
    doc.add_heading("4. Códigos de error comunes", level=1)
    err_codes = [
        ["200", "OK", "Operación exitosa."],
        ["201", "Created", "Recurso creado."],
        ["204", "No Content", "Operación exitosa sin cuerpo."],
        ["400", "Bad Request", "Datos inválidos."],
        ["401", "Unauthorized", "Token ausente o inválido."],
        ["403", "Forbidden", "Acceso a empresa ajena (IDOR)."],
        ["404", "Not Found", "Recurso no encontrado."],
        ["429", "Too Many Requests", "Rate limit excedido."],
        ["500", "Internal Server Error", "Error inesperado."],
    ]
    add_styled_table(doc, ["Código", "Nombre", "Descripción"], err_codes,
                     col_widths_cm=[2.0, 4.0, 11.5], first_col_bold=True)

    # === 5. Apéndice B: Hallazgos auditoría ===
    doc.add_heading("5. Apéndice B — Riesgos identificados (v1.2)", level=1)
    add_paragraph(doc, "Hallazgos de seguridad y compliance detectados en auditoría del 08-Jun-2026:")
    hallazgos_api = [
        ["R-API-03", "_CRÍTICO_", "_Token blacklist no consultado en get_current_user — tokens revocados siguen activos._"],
        ["R-API-04", "_CRÍTICO_", "_IDOR en /companies/{{id}} — acceso a datos de otra empresa._"],
        ["R-API-05", "_CRÍTICO_", "_/companies/publico accesible sin autenticación._"],
        ["R-API-06", "_CRÍTICO_", "_CSV injection en exports — fórmulas no sanitizadas._"],
        ["R-API-07", "_ALTO_", "Sin rate limiting en /auth/login (brute force posible)."],
        ["R-API-08", "_ALTO_", "JWT expiry 24h demasiado largo para sesiones sensibles."],
    ]
    add_styled_table(doc, ["ID", "Severidad", "Descripción"], hallazgos_api,
                     col_widths_cm=[2.0, 2.5, 12.0], first_col_bold=True)

    add_open_questions(doc, [
        "¿Se implementará token blacklist en V2?",
        "¿Se corregirá el IDOR en /companies/{id}?",
    ])
    add_risks_appendix(doc, [
        ("R-API-03", "Token blacklist no implementado. Un token robado permanece válido hasta expiry.", "Crítico"),
        ("R-API-06", "CSV injection permite inyección de fórmulasmaliciosas en exports.", "Crítico"),
    ])

    doc.save(OUT_FILE)
    print(f"Generado: {{OUT_FILE}}")

if __name__ == "__main__":
    build()
"""

# =============================================================================
# 09_BACKLOG_v1_2 — Deuda técnica seguridad
# =============================================================================
BUILD_09_V12 = r"""\"\"\"
Build 09 — Backlog del Producto v1.2
====================================
Genera: docs/documentacion_oficial/09_Backlog_Producto_Custodio_RAT_Manager_v1.2.docx

Cambios v1.2:
- Nuevos items de deuda técnica (seguridad P0/P1)
\"\"\"
import os
import sys
_THIS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _THIS)
from _theme_custodio import *
_OUT_DIR = r"C:\\Users\\chelo\\Desktop\\RAT_opencode\\docs\\documentacion_oficial"
ASSETS_DIR = os.path.join(_OUT_DIR, "assets")
OUT_FILE = os.path.join(_OUT_DIR, "09_Backlog_Producto_Custodio_RAT_Manager_v1.2.docx")
DOC_CODE = "CUST-DOC-09"
DOC_TITLE = "Backlog del Producto"
DOC_VERSION = "v1.2"
DOC_DATE = "Junio 2026"

def build():
    doc = new_document()
    add_header_footer(doc, DOC_TITLE)
    add_cover(doc, title="BACKLOG DEL PRODUCTO",
              subtitle="MVP actual, V1, V2 y roadmap trimestral", code=DOC_CODE)
    add_version_control(doc, DOC_CODE, DOC_TITLE, changes=[
        ("1.0", "Junio 2026", "Creación inicial del backlog."),
        ("1.1", "Junio 2026", "Se marcan como completadas las 6 HUs de auditoría de cumplimiento."),
        ("1.2", "Junio 2026", "_Nuevos items de deuda técnica de seguridad (DT-001 a DT-010) y nuevo módulo Feriados._"),
    ])
    add_toc(doc)
    fig_counter = [0]; tab_counter = [0]

    doc.add_heading("1. Introducción", level=1)
    add_paragraph(doc, f"Backlog de {BRAND_FULL} organizado en MVP, V1 y V2.")

    # === MVP actual ===
    doc.add_heading("2. MVP actual", level=1)
    mvp = [
        ["AUT-01", "Login JWT con cookies httpOnly y rate limit 5/min.", "Listo"],
        ["AUT-02", "Logout con revocación de token (blacklist).", "Listo"],
        ["RAT-01", "CRUD completo de RATs con filtros y exportación.", "Listo"],
        ["BREACH-01", "Gestión de security breaches con notificación.", "Listo"],
        ["EIPD-01", "Evaluaciones de impacto (EIPD) completas.", "Listo"],
        ["FER-01", "_Gestión de feriados nacionales (CRUD + CSV bulk)._", "_Listo v1.2_"],
    ]
    add_styled_table(doc, ["ID", "Descripción", "Estado"], mvp,
                     col_widths_cm=[2.0, 12.0, 2.5], first_col_bold=True)

    # === Deuda técnica v1.2 ===
    doc.add_heading("3. Deuda técnica — Seguridad (v1.2)", level=1)
    add_paragraph(doc, "_Items de deuda técnica identificados en auditoría del 08-Jun-2026._")
    deuda = [
        ["DT-001", "_CRÍTICA_", "_Implementar token blacklist en get_current_user (4h)_"],
        ["DT-002", "_CRÍTICA_", "_Fix IDOR en /companies/{{id}} (2h)_"],
        ["DT-003", "_CRÍTICA_", "_Fix /companies/publico sin auth (1h)_"],
        ["DT-004", "_CRÍTICA_", "_Sanitizar exports CSV contra inyección (3h)_"],
        ["DT-005", "_ALTA_", "Implementar rate limiting en /auth/login (4h)"],
        ["DT-006", "_ALTA_", "Encryption at rest PostgreSQL (8h)"],
        ["DT-007", "_ALTA_", "Audit trail inmutable con hash chain (8h)"],
        ["DT-008", "_MEDIA_", "Capa de servicios / Repository pattern (16h)"],
        ["DT-009", "_MEDIA_", "Tests unitarios 40% coverage (40h)"],
        ["DT-010", "_MEDIA_", "E2E Playwright completo (24h)"],
    ]
    add_styled_table(doc, ["ID", "Prioridad", "Descripción"], deuda,
                     col_widths_cm=[2.0, 2.5, 12.0], first_col_bold=True)

    doc.save(OUT_FILE)
    print(f"Generado: {{OUT_FILE}}")

if __name__ == "__main__":
    build()
"""

# =============================================================================
# 10_QA_v1_2 — Nuevos TC de seguridad
# =============================================================================
BUILD_10_V12 = r"""\"\"\"
Build 10 — Plan de QA v1.2
===========================
Genera: docs/documentacion_oficial/10_Plan_QA_Custodio_RAT_Manager_v1.2.docx

Cambios v1.2:
- Nuevos TC de seguridad (IDOR, CSV injection, token blacklist)
- TC para módulo Feriados
\"\"\"
import os
import sys
_THIS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _THIS)
from _theme_custodio import *
_OUT_DIR = r"C:\\Users\\chelo\\Desktop\\RAT_opencode\\docs\\documentacion_oficial"
ASSETS_DIR = os.path.join(_OUT_DIR, "assets")
OUT_FILE = os.path.join(_OUT_DIR, "10_Plan_QA_Custodio_RAT_Manager_v1.2.docx")
DOC_CODE = "CUST-DOC-10"
DOC_TITLE = "Plan de QA"
DOC_VERSION = "v1.2"
DOC_DATE = "Junio 2026"

def build():
    doc = new_document()
    add_header_footer(doc, DOC_TITLE)
    add_cover(doc, title="PLAN DE QA",
              subtitle="Estrategia, casos de prueba y cobertura del MVP", code=DOC_CODE)
    add_version_control(doc, DOC_CODE, DOC_TITLE, changes=[
        ("1.0", "Junio 2026", "Creación inicial del plan de QA."),
        ("1.1", "Junio 2026", "Agregados TC para Consentimientos, RATs sugeridos y Tickets ARCO."),
        ("1.2", "Junio 2026", "_Nuevos TC de seguridad (TC-060 a TC-072) y TC para módulo Feriados (TC-073 a TC-076)._"),
    ])
    add_toc(doc)
    fig_counter = [0]; tab_counter = [0]

    doc.add_heading("1. Introducción", level=1)
    add_paragraph(doc, f"Estrategia y casos de prueba de {BRAND_FULL}.")

    doc.add_heading("2. Estrategia", level=1)
    add_paragraph(doc, "Pirámide: Unitarias → Integración → E2E. Cobertura objetivo ≥80% en endpoints críticos.")

    # === Nuevos TC v1.2 ===
    doc.add_heading("3. Casos de prueba — Seguridad (v1.2)", level=1)
    add_paragraph(doc, "_TC nuevos identificados en auditoría del 08-Jun-2026._")

    tc_seg = [
        ["TC-060", "_CRÍTICO_", "Verificar que token revocado no permite acceso", "P0"],
        ["TC-061", "_CRÍTICO_", "Intentar acceder a /companies/{id} de otra empresa (IDOR)", "P0"],
        ["TC-062", "_CRÍTICO_", "Acceder a /companies/publico sin token (esperar 401)", "P0"],
        ["TC-063", "_CRÍTICO_", "Exportar CSV con fórmula =SUM(A:A) — verificar sanitización", "P0"],
        ["TC-064", "_ALTO_", "Brute force en /auth/login — verificar rate limit", "P1"],
        ["TC-065", "_ALTO_", "JWT con expiry largo — verificar logout efectivo", "P1"],
        ["TC-066", "_ALTO_", "XSS en campos de texto — verificar sanitización", "P1"],
        ["TC-067", "_MEDIO_", "CSP/HSTS headers presentes en respuestas", "P2"],
        ["TC-068", "_MEDIO_", "PII mask en logs de aplicación", "P2"],
        ["TC-069", "_MEDIO_", "CSRF token en state-changing operations", "P2"],
    ]
    add_styled_table(doc, ["TC", "Prioridad", "Descripción", "Severidad"], tc_seg,
                     col_widths_cm=[1.8, 2.0, 10.0, 2.7], first_col_bold=True)

    doc.add_heading("4. Casos de prueba — Módulo Feriados (v1.2)", level=1)
    tc_fer = [
        ["TC-073", "Listar feriados por año (GET /admin/feriados/?anio=2026)", "Listo"],
        ["TC-074", "Crear feriado individual (POST /admin/feriados/)", "Listo"],
        ["TC-075", "Eliminar feriado (DELETE /admin/feriados/{id})", "Listo"],
        ["TC-076", "Upload bulk CSV con encoding UTF-8 BOM", "Listo"],
    ]
    add_styled_table(doc, ["TC", "Descripción", "Estado"], tc_fer,
                     col_widths_cm=[1.8, 12.0, 2.7], first_col_bold=True)

    # === Apéndice B ===
    doc.add_heading("5. Apéndice B — Hallazgos QA (v1.2)", level=1)
    hallazgos_qa = [
        ["QA-01", "_CRÍTICO_", "_Cobertura tests <5% — sin unit tests en servicios core_"],
        ["QA-02", "_CRÍTICO_", "_Sin tests de seguridad (SQL injection, XSS, IDOR)_"],
        ["QA-03", "_ALTO_", "Mocking insuficiente — tests tocan BD real"],
        ["QA-04", "_ALTO_", "Tests E2E no incluyen flujos de error"],
        ["QA-05", "_MEDIO_", "Datos de test hardcoded en lugar de factories"],
    ]
    add_styled_table(doc, ["ID", "Prioridad", "Descripción"], hallazgos_qa,
                     col_widths_cm=[2.0, 2.5, 12.0], first_col_bold=True)

    doc.save(OUT_FILE)
    print(f"Generado: {{OUT_FILE}}")

if __name__ == "__main__":
    build()
"""

# =============================================================================
# 12_MANUAL_v1_2 — Nuevo módulo Feriados
# =============================================================================
BUILD_12_V12 = r"""\"\"\"
Build 12 — Manual Técnico v1.2
==============================
Genera: docs/documentacion_oficial/12_Manual_Tecnico_Custodio_RAT_Manager_v1.2.docx

Cambios v1.2:
- Nuevo modelo Feriado y ruta CRUD
- Stack actualizado (SQLAlchemy 2.0)
\"\"\"
import os
import sys
_THIS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _THIS)
from _theme_custodio import *
_OUT_DIR = r"C:\\Users\\chelo\\Desktop\\RAT_opencode\\docs\\documentacion_oficial"
ASSETS_DIR = os.path.join(_OUT_DIR, "assets")
OUT_FILE = os.path.join(_OUT_DIR, "12_Manual_Tecnico_Custodio_RAT_Manager_v1.2.docx")
DOC_CODE = "CUST-DOC-12"
DOC_TITLE = "Manual Técnico"
DOC_VERSION = "v1.2"
DOC_DATE = "Junio 2026"

def build():
    doc = new_document()
    add_header_footer(doc, DOC_TITLE)
    add_cover(doc, title="MANUAL TÉCNICO",
              subtitle="Arquitectura, stack y guía de despliegue", code=DOC_CODE)
    add_version_control(doc, DOC_CODE, DOC_TITLE, changes=[
        ("1.0", "Junio 2026", "Creación inicial del manual técnico."),
        ("1.2", "Junio 2026", "_Agregado modelo Feriado, ruta CRUD, SQLAlchemy 2.0 unificado, nueva sección de deuda técnica._"),
    ])
    add_toc(doc)
    fig_counter = [0]; tab_counter = [0]

    doc.add_heading("1. Introducción", level=1)
    add_paragraph(doc, f"Manual técnico de {BRAND_FULL}.")

    doc.add_heading("2. Stack tecnológico", level=1)
    stack = [
        ["Backend", "FastAPI 0.115 + Python 3.11 + Uvicorn"],
        ["ORM", "SQLAlchemy 2.0+ (unificado en todos los modelos)"],
        ["DB", "PostgreSQL 15+ (Neon en producción)"],
        ["Frontend", "Next.js 14 + TypeScript + Tailwind CSS 3"],
        ["Auth", "JWT (python-jose) + cookies httpOnly"],
        ["Validación", "Pydantic v2"],
    ]
    add_styled_table(doc, ["Componente", "Tecnología"], stack,
                     col_widths_cm=[4.0, 12.5], first_col_bold=True)

    doc.add_heading("3. Modelo de datos — Nuevos modelos v1.2", level=1)
    add_paragraph(doc, "_Modelo Feriado (nuevo en v1.2):_")
    modelo_feriado = [
        ["id", "Integer", "PK, autoincrement"],
        ["fecha", "Date", "Fecha del feriado, único por año"],
        ["nombre", "String(200)", "Nombre del feriado"],
        ["tipo", "Enum", "NACIONAL, REGIONAL, RELIGIOSO, CIVICO"],
        ["company_id", "Integer", "FK a companies (nullable para feriados nacionales)"],
        ["created_at", "DateTime", "Timestamp de creación"],
    ]
    add_styled_table(doc, ["Campo", "Tipo", "Descripción"], modelo_feriado,
                     col_widths_cm=[3.0, 4.0, 9.5], first_col_bold=True)

    doc.add_heading("4. Rutas — Módulo Feriados (v1.2)", level=1)
    rutas_fer = [
        ["GET", "/admin/feriados/", "Lista feriados filtrados por año"],
        ["POST", "/admin/feriados/", "Crea feriado individual"],
        ["DELETE", "/admin/feriados/{id}", "Elimina feriado"],
        ["POST", "/admin/feriados/upload", "Upload bulk CSV UTF-8 BOM"],
        ["GET", "/admin/feriados/export", "Exporta feriados como CSV"],
    ]
    add_styled_table(doc, ["Método", "Ruta", "Descripción"], rutas_fer,
                     col_widths_cm=[2.0, 5.0, 9.5], first_col_bold=True)

    # === Apéndice B ===
    doc.add_heading("5. Apéndice B — Deuda técnica arquitectura (v1.2)", level=1)
    deuda_arch = [
        ["A1", "_CRÍTICO_", "_Token blacklist no consultado en get_current_user_"],
        ["A2", "_CRÍTICO_", "_IDOR en /companies/{{id}} y /companies/publico_"],
        ["A4", "_CRÍTICO_", "_CSV injection en exports_"],
        ["A5", "_ALTO_", "Sin patrón Repository — lógica acoplada a routes"],
        ["A6", "_ALTO_", "Sin capa de servicios para lógica de negocio"],
        ["A15", "_ALTO_", "N+1 queries en listados de rats y breaches"],
    ]
    add_styled_table(doc, ["ID", "Prioridad", "Descripción"], deuda_arch,
                     col_widths_cm=[1.5, 2.5, 12.5], first_col_bold=True)

    doc.save(OUT_FILE)
    print(f"Generado: {{OUT_FILE}}")

if __name__ == "__main__":
    build()
"""

# =============================================================================
# MATRIZ_v1_2 — Nuevos RF/HU/CU/TC
# =============================================================================
BUILD_MATRIZ_V12 = r"""\"\"\"
Build Matriz — Matriz de Trazabilidad v1.2
==========================================
Genera: docs/documentacion_oficial/Matriz_Trazabilidad_Custodio_RAT_Manager_v1.2.docx

Cambios v1.2:
- Nuevos RF/HU/CU/TC del módulo Feriados
- TC de seguridad nuevos
\"\"\"
import os
import sys
_THIS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _THIS)
from _theme_custodio import *
_OUT_DIR = r"C:\\Users\\chelo\\Desktop\\RAT_opencode\\docs\\documentacion_oficial"
ASSETS_DIR = os.path.join(_OUT_DIR, "assets")
OUT_FILE = os.path.join(_OUT_DIR, "Matriz_Trazabilidad_Custodio_RAT_Manager_v1.2.docx")
DOC_CODE = "CUST-DOC-MTX"
DOC_TITLE = "Matriz de Trazabilidad"
DOC_VERSION = "v1.2"
DOC_DATE = "Junio 2026"

def build():
    doc = new_document()
    add_header_footer(doc, DOC_TITLE)
    add_cover(doc, title="MATRIZ DE TRAZABILIDAD",
              subtitle="RF → HU → CU → TC → APIs", code=DOC_CODE)
    add_version_control(doc, DOC_CODE, DOC_TITLE, changes=[
        ("1.0", "Junio 2026", "Creación inicial de la matriz."),
        ("1.2", "Junio 2026", "_Nuevos RF/HU/CU/TC del módulo Feriados y TC de seguridad (TC-060 a TC-076)._"),
    ])
    add_toc(doc)
    fig_counter = [0]; tab_counter = [0]

    doc.add_heading("1. Introducción", level=1)
    add_paragraph(doc, f"Matriz de trazabilidad de {BRAND_FULL} que vincula Requisitos Funcionales (RF), "
                  "Historias de Usuario (HU), Casos de Uso (CU), Casos de Prueba (TC) y endpoints de API.")

    # === Nuevos RF v1.2 ===
    doc.add_heading("2. Nuevos RF — Módulo Feriados (v1.2)", level=1)
    rf_fer = [
        ["RF-FER-01", "ALTA", "El sistema debe permitir consultar feriados nacionales por año", "API: GET /admin/feriados/"],
        ["RF-FER-02", "ALTA", "El sistema debe permitir crear feriados individuales", "API: POST /admin/feriados/"],
        ["RF-FER-03", "ALTA", "El sistema debe permitir eliminar feriados", "API: DELETE /admin/feriados/{id}"],
        ["RF-FER-04", "ALTA", "El sistema debe permitir upload bulk de feriados por CSV", "API: POST /admin/feriados/upload"],
        ["RF-FER-05", "MEDIA", "El sistema debe permitir exportar feriados como CSV", "API: GET /admin/feriados/export"],
    ]
    add_styled_table(doc, ["RF", "Prioridad", "Descripción", "Traza"], rf_fer,
                     col_widths_cm=[2.0, 2.0, 8.0, 4.5], first_col_bold=True)

    # === Nuevos TC v1.2 ===
    doc.add_heading("3. Nuevos TC — Seguridad y Feriados (v1.2)", level=1)
    tc_nuevos = [
        ["TC-060", "RF-SEC-01", "Token revocado no permite acceso", "P0"],
        ["TC-061", "RF-SEC-01", "IDOR: acceder a empresa ajena", "P0"],
        ["TC-062", "RF-SEC-01", "/companies/publico sin auth → 401", "P0"],
        ["TC-063", "RF-SEC-01", "CSV injection en exports", "P0"],
        ["TC-073", "RF-FER-01", "Listar feriados por año", "Alta"],
        ["TC-074", "RF-FER-02", "Crear feriado individual", "Alta"],
        ["TC-075", "RF-FER-03", "Eliminar feriado", "Alta"],
        ["TC-076", "RF-FER-04", "Upload bulk CSV UTF-8 BOM", "Alta"],
    ]
    add_styled_table(doc, ["TC", "RF origen", "Descripción", "Prioridad"], tc_nuevos,
                     col_widths_cm=[1.8, 2.5, 9.0, 2.7], first_col_bold=True)

    # === Apéndice B ===
    doc.add_heading("4. Apéndice B — Hallazgos de trazabilidad (v1.2)", level=1)
    hallazgos = [
        ["MTX-01", "_CRÍTICO_", "_TC-060 a TC-069 sin implementación en test suite_"],
        ["MTX-02", "_ALTO_", "RF-FER-01 a RF-FER-05 no estaban en matriz anterior"],
        ["MTX-03", "_MEDIO_", "TC-073 a TC-076 pendientes de automatizar"],
    ]
    add_styled_table(doc, ["ID", "Prioridad", "Descripción"], hallazgos,
                     col_widths_cm=[2.0, 2.5, 12.0], first_col_bold=True)

    doc.save(OUT_FILE)
    print(f"Generado: {{OUT_FILE}}")

if __name__ == "__main__":
    build()
"""

# =============================================================================
# GENERAR Y EJECUTAR
# =============================================================================
scripts = {
    "build_08_api_v1_2.py": BUILD_08_V12,
    "build_09_backlog_v1_2.py": BUILD_09_V12,
    "build_10_qa_v1_2.py": BUILD_10_V12,
    "build_12_manual_tecnico_v1_2.py": BUILD_12_V12,
    "build_matriz_v1_2.py": BUILD_MATRIZ_V12,
}

print("=" * 60)
print("Generando scripts v1.2...")
print("=" * 60)

for fname, content in scripts.items():
    path = os.path.join(_BUILD_DIR, fname)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  Creado: {fname}")

print()
print("Ejecutando scripts v1.2...")

import importlib.util
import sys as _sys

for fname in scripts:
    script_path = os.path.join(_BUILD_DIR, fname)
    print(f"  Ejecutando: {fname}...")
    try:
        spec = importlib.util.spec_from_file_location(fname.replace(".py", ""), script_path)
        module = importlib.util.module_from_spec(spec)
        _sys.modules[fname] = module
        spec.loader.exec_module(module)
        print(f"    OK: {fname}")
    except Exception as e:
        print(f"    ERROR en {fname}: {e}")

print()
print("=" * 60)
print("Documentos v1.2 generados:")
for fname in scripts:
    docname = fname.replace("_v1_2.py", "_v1.2.docx").replace("build_", "")
    # Transform to actual doc name
    docname = docname.replace("08_api", "08_API").replace("09_backlog", "09_Backlog_Producto")
    docname = docname.replace("10_qa", "10_Plan_QA").replace("12_manual_tecnico", "12_Manual_Tecnico")
    docname = docname.replace("matriz", "Matriz_Trazabilidad")
    docpath = os.path.join(_OUT_DIR, docname)
    exists = "EXISTS" if os.path.exists(docpath) else "NOT FOUND"
    print(f"  {docname} — {exists}")

print("=" * 60)
print("Done.")