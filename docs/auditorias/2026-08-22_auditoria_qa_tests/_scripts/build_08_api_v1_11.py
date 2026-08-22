"""
Build 08 — API REST v1.11 (QA Total 2026-08-22)
Genera: docs/documentacion_oficial/08_API_REST_Custodio_RAT_Manager_v1.11.docx
Cambios v1.11:
- POST /auth/users: status_code=201 (antes 200)
- GET /publico/csrf-token: nuevo endpoint CSRF token
- PUT /transparencia/{company_id}: nuevo endpoint politica editable
"""
import os
import sys
_THIS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _THIS)
from _theme_custodio import *
import _theme_custodio
_theme_custodio.DOC_VERSION = "v1.11"

OUT_DIR = r"C:\Users\chelo\Desktop\RAT_opencode\docs\documentacion_oficial"
ASSETS_DIR = os.path.join(OUT_DIR, "assets")
OUT_FILE = os.path.join(OUT_DIR, "08_API_REST_Custodio_RAT_Manager_v1.11.docx")
DOC_CODE = "CUST-DOC-08"
DOC_TITLE = "API REST"


def add_endpoint_table(doc, title, endpoints):
    doc.add_heading(title, level=2)
    headers = ["Método", "Path", "Auth", "RBAC", "Params", "Response", "Tags"]
    col_widths = [1.4, 5.0, 1.0, 2.5, 4.0, 3.5, 2.5]
    add_styled_table(doc, headers, endpoints, col_widths_cm=col_widths, first_col_bold=True)


def build():
    doc = new_document()
    add_header_footer(doc, DOC_TITLE)
    add_cover(doc,
              title="API REST",
              subtitle="Endpoints, autenticación, Authorization y esquemas de datos",
              code=DOC_CODE)
    add_version_control(doc, DOC_CODE, DOC_TITLE, changes=[
        ("1.0", "Junio 2026", "Creación inicial del documento de API."),
        ("1.1", "Junio 2026", "Endpoints completos del módulo RAT y autenticación."),
        ("1.2", "Junio 2026", "_Endpoints de brechas, ARCO, consentimientos._"),
        ("1.3", "Junio 2026", "_Beta Launch: /health, RBAC, EIPD._"),
        ("1.4", "Junio 2026", "_OCI Object Storage endpoints, asesor IA._"),
        ("1.5", "Junio 2026", "PENDING — no regenerado (gap pre-existente)."),
        ("1.6", "Junio 2026", "PENDING — no regenerado (gap pre-existente)."),
        ("1.7", "Junio 2026", "Gap G1 cerrado: Sprint 2 export endpoints + enqueue-sla-alerts."),
        ("1.8", "Junio 2026", "_PATCH /tkt-solicitud-derecho/{id} con hash SHA-256 auto + validación evidencia. causal_rechazo como CausalRechazoEnum (7 valores)._"),
        ("1.9", "Julio 2026", "_IDOR multi-tenant get_rat_for_user() en 6 endpoints RAT. base_legal_valida strict. ConsentimientoAlert en handleSave. Homologacion campos RAT. PDF titulos seccion._"),
        ("1.10", "Agosto 2026", "_Sprint A+B+UX: soft delete RAT, EIPD gate aprobacion, SLA alerts 72h, respuesta_texto obligatoria, politica transparencia editable (overrides_json)._"),
        ("1.11", "Agosto 2026", "_QA Total: POST /auth/users → 201. GET /publico/csrf-token nuevo. PUT /transparencia/{company_id} nuevo. PATCH TKT resuelto con metodo_verificacion en body._"),
    ])
    add_toc(doc)

    doc.add_heading("1. Introducción", level=1)
    add_paragraph(doc, f"Este documento especifica la API REST de {BRAND_FULL}. "
                      "Todos los endpoints requieren Bearer JWT (cookie httpOnly). "
                      "Rbac: superadmin > admin_empresa > usuario.")

    doc.add_heading("2. Cambios en v1.11 — Endpoints nuevos y modificados", level=1)
    endpoints_v18 = [
        ["POST", "/auth/users", "JWT", "superadmin",
         "UserCreate: username, email, full_name, password, rol_global",
         "201 + UserOut (antes: 200)", "AUTH"],
        ["GET", "/publico/csrf-token", "No", "Publica (rate 30/min)",
         "—",
         "200 + {token, header_name, expires_in_seconds}", "CSRF"],
        ["PUT", "/transparencia/{company_id}", "JWT", "admin_empresa, superadmin",
         "overrides_json: dict personalizado de items",
         "200 + PoliticaTransparenciaResponse", "TRANSPARENCIA"],
        ["PATCH", "/tkt-solicitud-derecho/{ticket_id}", "JWT", "admin_empresa, superadmin",
         "estado, respuesta_texto, metodo_verificacion_identidad*, causal_rechazo*, prioridad",
         "200 + TktTicketResponse", "TKT-ARCO"],
        ["*", "*metodo_verificacion_identidad: requerido cuando estado=resuelto (Art. 12). Puede enviarse en el body del PATCH en lugar de requerir que ya exista en BD.", "", "", "", "", ""],
        ["*", "*causal_rechazo: enum cerrado (CausalRechazoEnum) con 7 valores: falta_identidad, solicitud_manifiestamente_infundada, solicitud_excesiva, falta_poder_notorial, plazo_vencido, identidad_no_verificada, otro", "", "", "", "", ""],
    ]
    add_endpoint_table(doc, "2.1 Endpoints nuevos/modificados v1.11", endpoints_v18)

    doc.add_heading("3. Módulo RAT — IDOR multi-tenant y homologación", level=1)
    endpoints_v19 = [
        ["GET", "/rats/{rat_id}", "JWT", "admin_empresa, superadmin",
         "—",
         "200 + RatResponse | 404 si empresa no coincide", "RAT"],
        ["PUT", "/rats/{rat_id}", "JWT", "admin_empresa, superadmin",
         "RatUpdate schema completo",
         "200 + RatResponse | 404 si empresa no coincide", "RAT"],
        ["DELETE", "/rats/{rat_id}", "JWT", "superadmin",
         "—",
         "204 | 404 si empresa no coincide", "RAT"],
        ["POST", "/rats/{rat_id}/revision", "JWT", "admin_empresa, superadmin",
         "—",
         "200 + RatResponse | 404 si empresa no coincide", "RAT"],
        ["POST", "/rats/{rat_id}/aprobar", "JWT", "admin_empresa, superadmin",
         "RAT schema completo (25 campos)",
         "200 + RatResponse | 404 si empresa no coincide", "RAT"],
        ["GET", "/rats/{rat_id}/auditoria", "JWT", "admin_empresa, superadmin",
         "—",
         "200 + list[AuditLogResponse] | 404 si empresa no coincide", "RAT"],
        ["*", "*get_rat_for_user() retorna 404 (no 403) para no filtrar existencia de RATs ajenos. Superadmin accede a todos los RATs.", "", "", "", "", ""],
        ["*", "*base_legal_valida: enum strict (6 opciones). ConsentimientoAlert: listarConsentimientos() si datos_sensibles=True.", "", "", "", "", ""],
    ]
    add_endpoint_table(doc, "3.1 Módulo RAT — IDOR multi-tenant", endpoints_v19)

    add_id_glossary(doc, [
        ("TKT-###", "Tag TKT-ARCO", "Endpoints del módulo de ticketing ARCO."),
    ])
    add_final_note(doc)
    doc.save(OUT_FILE)
    print(f"[OK] {OUT_FILE}")


if __name__ == "__main__":
    build()
