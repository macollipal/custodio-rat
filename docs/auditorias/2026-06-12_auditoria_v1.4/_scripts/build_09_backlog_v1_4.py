"""
Build 09 — Backlog de Producto v1.4 (Post-OCI Integration)
Genera: docs/documentacion_oficial/09_Backlog_Producto_Custodio_RAT_Manager_v1.4.docx
Cambios v1.4:
- OCI Object Storage integration (DT-OCI-01)
- Admin Asesor IA (DT-OCI-02)
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
OUT_FILE = os.path.join(OUT_DIR, "09_Backlog_Producto_Custodio_RAT_Manager_v1.4.docx")
DOC_CODE = "CUST-DOC-09"
DOC_TITLE = "Backlog de Producto"
DOC_DATE = "Junio 2026"


def build():
    doc = new_document()
    add_header_footer(doc, DOC_TITLE)
    add_cover(doc, title="BACKLOG DE PRODUCTO",
              subtitle="User Stories, Features y Bugs · Priorización OLA-1 a OLA-3",
              code=DOC_CODE)
    add_version_control(doc, DOC_CODE, DOC_TITLE, changes=[
        ("1.0", "Junio 2026", "Backlog inicial con 20 items priorizados para OLA-1."),
        ("1.1", "Junio 2026", "Agregados 8 features de compliance: Token blacklist, hash chain, IDOR, CSRF, encryption."),
        ("1.2", "Junio 2026", "Items de auditoría v1.2: brecha CSV injection, public company IDOR, rate limits, PII masking."),
        ("1.3", "Junio 2026", "_Beta Launch: cerrados P0 de auditoría, nuevos items DT-014/DT-015/DT-016, pendientes CSRF/encryption._"),
        ("1.4", "Junio 2026", "_Post-OCI: OCI Object Storage con fallback chain, Admin Asesor IA._"),
    ])
    add_toc(doc)

    doc.add_heading("1. Vista general del backlog", level=1)
    add_paragraph(doc, "Total: 40 items. Estado al 12-Jun-2026: 32 completados, 2 en desarrollo, 6 pendientes. "
                      "Prioridad: Critical (P0) > High (P1) > Medium (P2) > Low (P3). "
                      "Ciclo de sprint: 2 semanas.")

    add_paragraph(doc, "_Items nuevos en v1.4 (post-OCI integration):_")
    new_v14 = [
        ["DT-OCI-01", "P0", "Feature", "OCI Object Storage con fallback chain (PAR → signed GET → BYTEA)",
         "57cbffc · storage.py, rat_service.py", "CERRADO"],
        ["DT-OCI-02", "P1", "Feature", "Admin Asesor IA (indexar, stats, eliminar chunks)",
         "admin_asesor.py", "CERRADO"],
    ]
    add_styled_table(doc, ["ID", "Prioridad", "Tipo", "Título", "Commit · Archivo", "Estado"],
                     new_v14, col_widths_cm=[1.5, 1.8, 1.5, 7.0, 4.0, 1.7],
                     first_col_bold=True, underline_new=True)

    doc.add_heading("2. User Stories por módulo", level=1)

    doc.add_heading("2.1 Módulo Auth", level=2)
    auth_stories = [
        ["US-AUTH-01", "Como administrador, quiero gestionar usuarios completamente para mantener el sistema actualizado.",
         "P1", "100%", "Cerrado"],
        ["US-AUTH-02", "Como usuario, quiero cambiar mi password de forma segura.",
         "P2", "100%", "Cerrado"],
        ["US-AUTH-03", "_Como usuario, quiero que mi token sea revocado automáticamente al hacer logout (blacklist LRU)._",
         "P0", "100%", "Cerrado v1.2"],
    ]
    add_styled_table(doc, ["ID", "Descripción", "Prioridad", "Cobertura", "Estado"],
                     auth_stories, col_widths_cm=[2.0, 9.5, 1.8, 1.7, 2.5],
                     first_col_bold=True)

    doc.add_heading("2.2 Módulo RATs", level=2)
    rat_stories = [
        ["US-RAT-01", "Como admin, quiero crear y editar RATs con campos completos.",
         "P0", "100%", "Cerrado"],
        ["US-RAT-02", "Como usuario, quiero ver la lista de RATs de mi empresa.",
         "P1", "100%", "Cerrado"],
        ["US-RAT-03", "Como admin, quiero exportar RATs a CSV y PDF.",
         "P1", "100%", "Cerrado"],
        ["US-RAT-04", "_Como admin_empresa, solo quiero crear RATs en empresas que gestiono (DT-014)._",
         "P0", "100%", "Cerrado v1.3"],
        ["US-RAT-05", "_Como usuario, quiero dar consentimiento expreso para cada RAT._",
         "P0", "90%", "En progreso"],
        ["US-RAT-06", "_Como admin, quiero registrar revisiones periódicas de mis RATs._",
         "P2", "100%", "Cerrado"],
        ["US-RAT-07", "_Como usuario, quiero descargar el documento de base legal de un RAT con fallback automático._",
         "P0", "100%", "Cerrado v1.4"],
    ]
    add_styled_table(doc, ["ID", "Descripción", "Prioridad", "Cobertura", "Estado"],
                     rat_stories, col_widths_cm=[2.0, 9.5, 1.8, 1.7, 2.5],
                     first_col_bold=True, underline_new=True)

    doc.add_heading("2.3 Módulo Brechas", level=2)
    breach_stories = [
        ["US-BRCH-01", "Como admin, quiero registrar brechas de seguridad con evaluación de riesgo.",
         "P0", "100%", "Cerrado"],
        ["US-BRCH-02", "Como admin, quiero recibir alertas de vencimiento de brechas.",
         "P2", "80%", "En progreso"],
        ["US-BRCH-03", "_Como rol usuario, NO quiero poder crear brechas (DT-015)._",
         "P0", "100%", "Cerrado v1.3"],
    ]
    add_styled_table(doc, ["ID", "Descripción", "Prioridad", "Cobertura", "Estado"],
                     breach_stories, col_widths_cm=[2.0, 9.5, 1.8, 1.7, 2.5],
                     first_col_bold=True, underline_new=True)

    doc.add_heading("2.4 Consentimientos y EIPD", level=2)
    consent_stories = [
        ["US-CONS-01", "_Como responsable, quiero registrar consentimientos expresos (Art. 12)._",
         "P0", "100%", "Cerrado v1.3"],
        ["US-CONS-02", "_Como responsable, quiero poder revocar consentimientos._",
         "P0", "100%", "Cerrado v1.3"],
        ["US-EIPD-01", "_Como responsable, quiero crear y gestionar EIPDs (Art. 15 bis)._",
         "P0", "100%", "Cerrado v1.3"],
        ["US-EIPD-02", "_Como responsable, quiero asociar EIPDs a RATs específicos._",
         "P0", "100%", "Cerrado v1.3"],
    ]
    add_styled_table(doc, ["ID", "Descripción", "Prioridad", "Cobertura", "Estado"],
                     consent_stories, col_widths_cm=[2.0, 9.5, 1.8, 1.7, 2.5],
                     first_col_bold=True, underline_new=True)

    doc.add_heading("2.5 Módulo Asesor IA", level=2)
    ai_stories = [
        ["US-AI-01", "Como superadmin, quiero indexar documentos en el corpus del asesor IA.",
         "P1", "100%", "Cerrado v1.4"],
        ["US-AI-02", "Como superadmin, quiero ver estadísticas del corpus.",
         "P1", "100%", "Cerrado v1.4"],
        ["US-AI-03", "Como superadmin, quiero eliminar chunks irrelevantes del índice.",
         "P1", "100%", "Cerrado v1.4"],
    ]
    add_styled_table(doc, ["ID", "Descripción", "Prioridad", "Cobertura", "Estado"],
                     ai_stories, col_widths_cm=[2.0, 9.5, 1.8, 1.7, 2.5],
                     first_col_bold=True, underline_new=True)

    doc.add_heading("3. Features técnicos", level=1)
    tech_features = [
        ["TF-01", "P0", "Seguridad", "_Token blacklist con JTI + LRU cache (commit 96167b5)._"],
        ["TF-02", "P0", "Seguridad", "_IDOR protection con check_company_access (96167b5)._"],
        ["TF-03", "P0", "Seguridad", "_CSV injection sanitization (96167b5)._"],
        ["TF-04", "P0", "Seguridad", "_Hash chain SHA256 en audit_logs (96167b5)._"],
        ["TF-05", "P0", "Seguridad", "Rate limiting con slowapi en /auth/login (5/min)."],
        ["TF-06", "P1", "Seguridad", "_PII masking en logs (PIIMaskingFilter)._"],
        ["TF-07", "P1", "Seguridad", "JWT expiry 480 min + refresh token rotation."],
        ["TF-08", "P0", "Bug", "_RBAC fixes DT-014/DT-015 (6209e2d)._"],
        ["TF-09", "P0", "Bug", "_Router fixes consentimientos/eipd (6980187, 43287c0)._"],
        ["TF-10", "P0", "Feature", "_Endpoint /health y /health/db (6209e2d)._"],
        ["TF-11", "P0", "Feature", "_OCI Object Storage con fallback chain (57cbffc)._"],
        ["TF-12", "P1", "Feature", "_Admin Asesor IA: index, stats, delete chunk (admin_asesor.py)._"],
        ["S14", "P0", "Pendiente", "CSRF protection para formularios web (S14 de auditoría)."],
        ["C1", "P1", "Pendiente", "Encryption at rest a nivel aplicación (AES-256)."],
        ["A6", "P2", "Pendiente", "Service layer decoupling (para unit tests)."],
        ["DT-009", "P1", "Pendiente", "Cobertura de tests 40% (actualmente ~25%)."],
        ["DT-010", "P1", "Pendiente", "Tests E2E completos con Playwright CI/CD."],
    ]
    add_styled_table(doc, ["ID", "Prioridad", "Categoría", "Descripción"],
                     tech_features, col_widths_cm=[1.8, 1.8, 2.5, 10.4],
                     first_col_bold=True)

    doc.add_heading("4. Bugs pendientes", level=1)
    pending_bugs = [
        ["S14", "CSRF protection", "P0", "No hay validación CSRF en formularios web.",
         "Pendiente", "v1.4"],
        ["C1", "Encryption at rest", "P1", "Datos sensibles sin encryption a nivel DB.",
         "Pendiente", "v1.4"],
        ["A6", "Service layer", "P2", "Lógica de negocio mezclada con routes.",
         "Pendiente", "v1.5"],
    ]
    add_styled_table(doc, ["ID", "Nombre", "Prioridad", "Descripción", "Estado", "ETA"],
                     pending_bugs, col_widths_cm=[1.5, 3.5, 1.8, 6.0, 2.0, 1.7],
                     first_col_bold=True)

    doc.add_heading("5. Definition of Done", level=1)
    add_paragraph(doc, "Cada item del backlog debe cumplir:")
    add_bullet(doc, "Código con tests unitarios (coverage ≥ 40% para v1.3, 70% para v1.4)")
    add_bullet(doc, "Code review aprobado por QA")
    add_bullet(doc, "E2E con Playwright pasando en QA")
    add_bullet(doc, "Documentación actualizada")
    add_bullet(doc, "No vulnerabilidades críticas en scan de seguridad")

    add_risks_appendix(doc, [
        ("R-BK-01", "Pendientes S14 y C1 bloquean certificación Ley 21.719 completa.", "Alto"),
        ("R-BK-02", "DT-009 y DT-010 requieren inversión significativa en infrastructure CI/CD.", "Medio"),
    ])
    add_open_questions(doc, [
        "¿Se prioriza CSRF (S14) para v1.4 o v1.5?",
        "¿Se usará AWS KMS o similar para C1 encryption?",
    ])

    doc.save(OUT_FILE)
    print(f"[OK] {OUT_FILE}")


if __name__ == "__main__":
    build()