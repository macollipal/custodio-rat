"""
Build 08 — API REST v1.8 (Post Iter 11 + Iter 12)
Genera: docs/documentacion_oficial/08_API_REST_Custodio_RAT_Manager_v1.8.docx
Cambios v1.8:
- Iter 12: PATCH /tkt-solicitud-derecho/{id} con hash SHA-256 auto + validación evidencia
- Iter 12: causal_rechazo como CausalRechazoEnum
"""
import os
import sys
_THIS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _THIS)
from _theme_custodio import *
import _theme_custodio
_theme_custodio.DOC_VERSION = "v1.8"

OUT_DIR = r"C:\Users\chelo\Desktop\RAT_opencode\docs\documentacion_oficial"
ASSETS_DIR = os.path.join(OUT_DIR, "assets")
OUT_FILE = os.path.join(OUT_DIR, "08_API_REST_Custodio_RAT_Manager_v1.8.docx")
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
    ])
    add_toc(doc)

    doc.add_heading("1. Introducción", level=1)
    add_paragraph(doc, f"Este documento especifica la API REST de {BRAND_FULL}. "
                      "Todos los endpoints requieren Bearer JWT (cookie httpOnly). "
                      "Rbac: superadmin > admin_empresa > usuario.")

    doc.add_heading("2. Cambios en v1.8 — Endpoints relevantes", level=1)
    endpoints_v18 = [
        ["PATCH", "/tkt-solicitud-derecho/{ticket_id}", "JWT", "admin_empresa, superadmin",
         "estado, respuesta_texto, causal_rechazo*, prioridad, responsable_id",
         "200 + TktTicketResponse", "TKT-ARCO"],
        ["*", "*causal_rechazo: enum cerrado (CausalRechazoEnum) con 7 valores: falta_identidad, solicitud_manifiestamente_infundada, solicitud_excesiva, falta_poder_notorial, plazo_vencido, identidad_no_verificada, otro", "", "", "", "", "", ""],
        ["*", "*HTTP 400 si estado=resuelto sin adjuntos ni respuesta_texto (evidencia obligatoria)", "", "", "", "", "", ""],
        ["*", "*SHA-256 computado automáticamente de tkt_adjuntos al resolver", "", "", "", "", "", ""],
    ]
    add_endpoint_table(doc, "2.1 Módulo TKT — Cambios v1.8", endpoints_v18)

    add_id_glossary(doc, [
        ("TKT-###", "Tag TKT-ARCO", "Endpoints del módulo de ticketing ARCO."),
    ])
    add_final_note(doc)
    doc.save(OUT_FILE)
    print(f"[OK] {OUT_FILE}")


if __name__ == "__main__":
    build()
