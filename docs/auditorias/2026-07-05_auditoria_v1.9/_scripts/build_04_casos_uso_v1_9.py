"""
Build 04 — Casos de Uso v1.9 (Post Iter 11 + Iter 12)
Genera: docs/documentacion_oficial/04_Casos_de_Uso_Custodio_RAT_Manager_v1.9.docx
Cambios v1.9:
- Iter 11: CU-069 a CU-071 (15 campos Tier 1+Tier 2)
- Iter 12: CU-072 a CU-077 (9 fixes CRITICOS+ALTOS)
"""
import os
import sys
_THIS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _THIS)
from _theme_custodio import *
import _theme_custodio
_theme_custodio.DOC_VERSION = "v1.9"

OUT_DIR = r"C:\Users\chelo\Desktop\RAT_opencode\docs\documentacion_oficial"
ASSETS_DIR = os.path.join(OUT_DIR, "assets")
OUT_FILE = os.path.join(OUT_DIR, "04_Casos_de_Uso_Custodio_RAT_Manager_v1.9.docx")
DOC_CODE = "CUST-DOC-04"
DOC_TITLE = "Casos de Uso"


def build():
    doc = new_document()
    add_header_footer(doc, DOC_TITLE)
    add_cover(doc, title="CASOS DE USO",
              subtitle="Especificación formal de interacciones actor-sistema",
              code=DOC_CODE)
    add_version_control(doc, DOC_CODE, DOC_TITLE, changes=[
        ("1.0", "Junio 2026", "Creación inicial del documento de casos de uso."),
        ("1.1", "Junio 2026", "Auditoría técnica: CU-033 a CU-038 para Consentimientos y Tickets ARCO."),
        ("1.2", "Junio 2026", "_Auditoría v1.2: módulo Feriados (CU-039 a CU-042), fixes P0 (blacklist, IDOR, CSV)._"),
        ("1.3", "Junio 2026", "_Beta Launch: RBAC fixes DT-014/DT-015 (CU-043/CU-044), /health (CU-045), EIPD (CU-047), consentimientos (CU-046)._"),
        ("1.4", "Junio 2026", "_Post-OCI: descarga con fallback chain (CU-048), Admin Asesor IA (CU-049/CU-050)._"),
        ("1.5", "Junio 2026", "_Seguridad: CSRF (CU-051), Encryption at Rest (CU-052), Service Layer (CU-053), Schemas Pydantic (CU-054)._"),
        ("1.6", "Junio 2026", "_UI/UX: RatDetailModal (CU-055), Drawer responsive (CU-056), Dashboard clickable (CU-057), Sort estable (CU-058)._"),
        ("1.7", "Junio 2026", "Sprint 1: FORMADMIN ARCO (CU-059 a CU-063). Sprint 2: SLA Alert + Export ARCO (CU-064 a CU-068)."),
        ("1.8", "Junio 2026", "_Iter 11: 15 campos Tier 1+Tier 2 RAT (CU-069 a CU-071). Iter 12: 9 fixes CRITICOS+ALTOS (CU-072 a CU-077)._"),
        ("1.9", "Julio 2026", "_IDOR multi-tenant en 6 endpoints RAT (CU-078). base_legal_valida strict (CU-079). ConsentimientoAlert (CU-080). Homologación orden campos (CU-081). PDF títulos sección (CU-082)._"),
    ])
    add_toc(doc)

    doc.add_heading("1. Introducción", level=1)
    add_paragraph(doc, f"Este Documento especifica los casos de uso de {BRAND_FULL} "
                      "en formato formal. Cada CU incluye: identificador (CU-###), nombre, "
                      "actores, precondiciones, flujo principal, flujos alternativos y resultado esperado.")

    doc.add_heading("2. Listado de casos de uso nuevos (v1.9)", level=1)
    casos_nuevos = [
        ["CU-069", "Registrar 15 campos Tier 1+Tier 2 en RAT", "AC-02/03", "RF-141 a RF-155", "PUT /rats/{id}"],
        ["CU-070", "BYTEA limitado a 10MB en archivo_base_legal y tkt_adjunto", "Sistema", "RF-156", "CHECK constraint PostgreSQL"],
        ["CU-071", "Test IL validado con mínimo 50 caracteres", "AC-02/03", "RF-157", "PUT /rats/{id} — validación Pydantic + frontend"],
        ["CU-072", "Hash SHA-256 automático de evidencia ARCO al resolver TKT", "Sistema", "RF-158", "PATCH /tkt-solicitud-derecho/{id}"],
        ["CU-073", "causal_rechazo con enum cerrado (7 causales Art. 29 RL)", "AC-01/02", "RF-159", "PATCH /tkt-solicitud-derecho/{id} — dropdown"],
        ["CU-074", "Toggle ARCO con touch target 44x44px (mobile)", "AC-05", "RF-160", "UI: solicitud_derecho/page.tsx"],
        ["CU-075", "Notificación APDC automatizada al crear brecha", "Sistema", "RF-161", "actualizar_brecha() — email_service"],
        ["CU-076", "Notificación a titulares automatizada al cerrar brecha", "Sistema", "RF-162", "actualizar_brecha() — logging"],
        ["CU-077", "TKT no puede resolverse sin evidencia ni hash", "AC-01/02", "RF-158", "PATCH /tkt-solicitud-derecho/{id} — HTTP 400"],
        ["CU-078", "IDOR multi-tenant: empresa no puede acceder a RAT de otra", "AC-02/03", "RF-163", "get_rat_for_user() — retorna 404 en 6 endpoints"],
        ["CU-079", "base_legal_valida strict contra enum taxativo", "Sistema", "RF-164", "base_legal_valida() — 6 opciones válidas"],
        ["CU-080", "ConsentimientoAlert antes de guardar RAT con datos_sensibles", "Sistema", "RF-165", "handleSave() — listarConsentimientos()"],
        ["CU-081", "Homologación orden campos RAT en wizard, drawer y PDF", "Sistema", "RF-166", "RatDetailView + RatEditForm + RatWizard + export_service"],
        ["CU-082", "PDF con títulos de sección y alertas rojas", "Sistema", "RF-167", "export_service — PASOx — IDENTIFICACIÓN con COLOR_PRIMARIO"],
    ]
    add_styled_table(doc, ["ID", "Nombre", "Actores", "Trazabilidad", "Endpoint/Flujo"],
                     casos_nuevos, col_widths_cm=[1.5, 4.5, 2.0, 2.5, 4.5], first_col_bold=True,
                     underline_new=True)

    add_id_glossary(doc, [
        ("CU-###", "Caso de Uso", "Especificación de interacción actor-sistema."),
    ])
    add_final_note(doc)
    doc.save(OUT_FILE)
    print(f"[OK] {OUT_FILE}")


if __name__ == "__main__":
    build()
