"""
Build 10 — Plan de QA v1.4 (Post-OCI Integration)
Genera: docs/documentacion_oficial/10_Plan_QA_Custodio_RAT_Manager_v1.4.docx
Cambios v1.4:
- Nuevos casos: OCI download fallback chain, Admin Asesor IA
"""
import os
import sys
_THIS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _THIS)
from _theme_custodio import *
import _theme_custodio
_theme_custodio.DOC_VERSION = "v1.4"

OUT_DIR = r"C:\Users\chelo\Desktop\RAT_opencode\docs\documentacion_oficial"
ASSETS_DIR = os.path.join(OUT_DIR, "assets")
OUT_FILE = os.path.join(OUT_DIR, "10_Plan_QA_Custodio_RAT_Manager_v1.4.docx")
DOC_CODE = "CUST-DOC-10"
DOC_TITLE = "Plan de Calidad"
DOC_DATE = "Junio 2026"


def build():
    doc = new_document()
    add_header_footer(doc, DOC_TITLE)
    add_cover(doc, title="PLAN DE QUALITY ASSURANCE",
              subtitle="Estrategia, casos de prueba y métricas · v1.4",
              code=DOC_CODE)
    add_version_control(doc, DOC_CODE, DOC_TITLE, changes=[
        ("1.0", "Junio 2026", "Plan inicial con 45 casos de prueba para OLA-1."),
        ("1.1", "Junio 2026", "Agregados casos de seguridad: token blacklist, IDOR, rate limit."),
        ("1.2", "Junio 2026", "Casos actualizados post-auditoría: CSV injection, hash chain, PII masking."),
        ("1.3", "Junio 2026", "_Beta Launch: nuevos casos DT-014/DT-015/DT-016, CB-01/CB-02 (consentimientos/eipd), 215 pytest + ~65 E2E pasan._"),
        ("1.4", "Junio 2026", "_Post-OCI: casos para OCI download fallback chain, Admin Asesor IA._"),
    ])
    add_toc(doc)

    doc.add_heading("1. Resumen ejecutivo", level=1)
    add_paragraph(doc, "_v1.4 (12-Jun-2026): OCI Object Storage integrado con fallback chain. Score: 7.6/10._")
    add_paragraph(doc, "Cobertura de código: ~25% (meta v1.4: 40%, v1.5: 70%). "
                      "QA backend: https://custodio-api-qa.vercel.app. QA frontend: https://custodio-qa.vercel.app.")

    doc.add_heading("2. Estrategia de testing", level=1)
    test_pyramid = [
        ["Nivel", "Cantidad", "Framework", "Estado v1.4"],
        ["Unit tests (backend)", "~200", "pytest + fixture isolation", "215+ passed"],
        ["Integration tests", "~15", "pytest + testclient", "Pasando"],
        ["E2E (Playwright)", "~70", "Playwright + pytest", "~65 passing"],
        ["Security scans", "3", "Manual audit + SQL injection", "Pasando"],
        ["Load tests", "Pendiente", "locust", "No ejecutado"],
    ]
    add_styled_table(doc, ["Nivel", "Cantidad", "Framework", "Estado v1.4"],
                     test_pyramid, col_widths_cm=[3.5, 2.5, 5.0, 5.5],
                     first_col_bold=True)

    doc.add_heading("3. Casos de prueba — Módulo Auth", level=1)
    auth_cases = [
        ["QA-AUTH-01", "Login válido", "POST /auth/login con credenciales válidas", "200 + JWT", "Automatizado"],
        ["QA-AUTH-02", "Login inválido", "POST /auth/login con password incorrecto", "401 Unauthorized", "Automatizado"],
        ["QA-AUTH-03", "Token revoked", "GET /auth/me con token en blacklist", "401 Unauthorized", "Automatizado"],
        ["QA-AUTH-04", "Rate limit login", "6 logins fallidos en 1 min", "429 Too Many Requests", "Automatizado"],
        ["QA-AUTH-05", "Cambio password propio", "PUT /auth/me/password con old_password correcto", "200 + mensaje", "Automatizado"],
    ]
    add_styled_table(doc, ["ID", "Título", "Pasos", "Resultado esperado", "Tipo"],
                     auth_cases, col_widths_cm=[2.5, 3.5, 6.5, 4.0, 2.0],
                     first_col_bold=True)

    doc.add_heading("4. Casos de prueba — Módulo RATs", level=1)
    rat_cases = [
        ["QA-RAT-01", "Crear RAT válido", "POST /rats/ con datos completos", "201 Created", "Automatizado"],
        ["QA-RAT-02", "_admin_empresa crea RAT en empresa propia_", "_POST /rats/ con empresa asignada_", "_201 Created_", "_Automatizado_"],
        ["QA-RAT-03", "_admin_empresa NO crea RAT en empresa ajena (DT-014)_", "_POST /rats/ con empresa NO asignada_", "_403 Forbidden_", "_Automatizado_"],
        ["QA-RAT-04", "Exportar CSV RATs", "GET /rats/export/csv con auth", "200 + CSV sanitizado", "Automatizado"],
        ["QA-RAT-05", "CSV injection prevention", "RAT con nombre =cmd|...'!A1", "CSV con ' escapado", "Automatizado"],
        ["QA-RAT-06", "Verificar hash chain", "GET /rats/auditoria/verify-chain", "{valid: true}", "Automatizado"],
        ["QA-RAT-07", "_Descarga con PAR (OCI pre-signed URL)_", "_GET /rats/{id}/archivo con OCI disponible_", "_200 + url pre-firmada_", "_Automatizado_"],
        ["QA-RAT-08", "_Fallback a signed GET cuando PAR falla_", "_GET /rats/{id}/archivo sin permisos PAR_", "_200 + bytes_", "_Automatizado_"],
        ["QA-RAT-09", "_Fallback a BYTEA cuando OCI no disponible_", "_GET /rats/{id}/archivo con OCI caído_", "_200 + bytes BYTEA_", "_Automatizado_"],
    ]
    add_styled_table(doc, ["ID", "Título", "Pasos", "Resultado esperado", "Tipo"],
                     rat_cases, col_widths_cm=[2.5, 4.5, 6.0, 4.0, 2.0],
                     first_col_bold=True, underline_new=True)

    doc.add_heading("5. Casos de prueba — Módulo Brechas", level=1)
    breach_cases = [
        ["QA-BRCH-01", "Crear brecha como admin", "POST /brechas/ con rol admin", "201 Created", "Automatizado"],
        ["QA-BRCH-02", "_usuario NO crea brecha (DT-015)_", "_POST /brechas/ con rol usuario_", "_403 Forbidden_", "_Automatizado_"],
        ["QA-BRCH-03", "Evaluar riesgo brecha", "POST /brechas/{id}/evaluar-riesgo", "200 + evaluación", "Automatizado"],
    ]
    add_styled_table(doc, ["ID", "Título", "Pasos", "Resultado esperado", "Tipo"],
                     breach_cases, col_widths_cm=[2.5, 4.5, 6.0, 4.0, 2.0],
                     first_col_bold=True, underline_new=True)

    doc.add_heading("6. Casos de prueba — Módulos Consentimientos y EIPD", level=1)
    consent_cases = [
        ["QA-CONS-01", "_Listar consentimientos_", "_GET /consentimientos/ con auth_", "_200 + lista_", "_Automatizado_"],
        ["QA-CONS-02", "_Crear consentimiento_", "_POST /consentimientos/ con datos_", "_201 Created_", "_Automatizado_"],
        ["QA-CONS-03", "_Revocar consentimiento_", "_POST /consentimientos/{id}/revocar_", "_200 + estado revoked_", "_Automatizado_"],
        ["QA-EIPD-01", "_Listar EIPDs_", "_GET /eipd/ con auth_", "_200 + lista_", "_Automatizado_"],
        ["QA-EIPD-02", "_Crear EIPD_", "_POST /eipd/ con RAT asociado_", "_201 Created_", "_Automatizado_"],
        ["QA-EIPD-03", "_Actualizar EIPD_", "_PUT /eipd/{id} con workflow_", "_200 + EIPD actualizado_", "_Automatizado_"],
    ]
    add_styled_table(doc, ["ID", "Título", "Pasos", "Resultado esperado", "Tipo"],
                     consent_cases, col_widths_cm=[2.5, 4.5, 6.0, 4.0, 2.0],
                     first_col_bold=True, underline_new=True)

    doc.add_heading("7. Casos de prueba — Admin Asesor IA", level=1)
    asesor_cases = [
        ["QA-AS-01", "_Indexar corpus_", "_POST /admin/asesor/index con paths_", "_200 + stats_", "_Automatizado_"],
        ["QA-AS-02", "_Ver stats del corpus_", "_GET /admin/asesor/stats_", "_200 + total chunks_", "_Automatizado_"],
        ["QA-AS-03", "_Eliminar chunk_", "_DELETE /admin/asesor/documents/{id}_", "_200 + {ok: true}_", "_Automatizado_"],
        ["QA-AS-04", "_Solo superadmin puede acceder_", "_GET /admin/asesor/stats con usuario normal_", "_403 Forbidden_", "_Automatizado_"],
    ]
    add_styled_table(doc, ["ID", "Título", "Pasos", "Resultado esperado", "Tipo"],
                     asesor_cases, col_widths_cm=[2.5, 4.5, 6.0, 4.0, 2.0],
                     first_col_bold=True, underline_new=True)

    doc.add_heading("8. Casos de prueba — Health y Sistema", level=1)
    system_cases = [
        ["QA-SYS-01", "_GET /health sin auth_", "_GET /health_", "_200 + {\"status\": \"ok\"}_", "_Automatizado_"],
        ["QA-SYS-02", "_GET /health/db_", "_GET /health/db_", "_200 + {status, latency_ms}_", "_Automatizado_"],
        ["QA-SYS-03", "IDOR en /companies/{id}", "GET /companies/{id} con empresa no asignada", "403 Forbidden", "Automatizado"],
    ]
    add_styled_table(doc, ["ID", "Título", "Pasos", "Resultado esperado", "Tipo"],
                     system_cases, col_widths_cm=[2.5, 4.5, 6.0, 4.0, 2.0],
                     first_col_bold=True, underline_new=True)

    doc.add_heading("9. Bugs abiertos", level=1)
    open_bugs = [
        ["S14", "CSRF protection", "P0", "No hay validación anti-CSRF en formularios.",
         "Pendiente v1.4"],
        ["C1", "Encryption at rest", "P1", "Datos sensibles sin AES-256 a nivel DB.",
         "Pendiente v1.4"],
        ["A6", "Service layer", "P2", "Lógica de negocio acoplada a routes.",
         "Pendiente v1.5"],
    ]
    add_styled_table(doc, ["ID", "Nombre", "Prioridad", "Descripción", "ETA"],
                     open_bugs, col_widths_cm=[1.5, 3.0, 1.8, 7.0, 3.2],
                     first_col_bold=True)

    add_risks_appendix(doc, [
        ("R-QA-01", "3 E2E failures por browser crashes (límite memoria). No son errores funcionales.", "Bajo"),
        ("R-QA-02", "Coverage 25% vs meta 40%. Se necesitan ~30 tests unitarios más.", "Medio"),
    ])

    doc.save(OUT_FILE)
    print(f"[OK] {OUT_FILE}")


if __name__ == "__main__":
    build()