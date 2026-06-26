"""
Build 09 — Backlog de Producto v1.8 (Post Iter 11 + Iter 12)
Genera: docs/documentacion_oficial/09_Backlog_Producto_Custodio_RAT_Manager_v1.8.docx
Cambios v1.8:
- Items cerrados: DT-ITER12-01 a DT-ITER12-09
- Items nuevos: QW-ITER13-01 paginación, QW-ITER13-02 retry OCI, QW-ITER13-03 audit_log table
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
OUT_FILE = os.path.join(OUT_DIR, "09_Backlog_Producto_Custodio_RAT_Manager_v1.8.docx")
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
        ("1.5", "Junio 2026", "_Seguridad: CSRF (DT-SEC-01), Encryption at Rest (DT-SEC-02), Service Layer (DT-ARC-01)._"),
        ("1.6", "Junio 2026", "_UI/UX: RatDetailModal (DT-UX-01), Drawer responsive (DT-UX-02), Dashboard clickable (DT-UX-03), IDOR fix (DT-UX-04)._"),
        ("1.7", "Junio 2026", "Sprint 1: FORMADMIN ARCO QW1-QW10. Sprint 2: SLA Alert T-2d + Export ARCO CSV/Excel/PDF."),
        ("1.8", "Junio 2026", "_Iter 11+12: 9 fixes CRITICOS+ALTOS cerrados (DT-ITER12-01 a DT-ITER12-09). Score: 6.3/10. QW-ITER13: paginación, retry OCI, audit_log table._"),
    ])
    add_toc(doc)

    doc.add_heading("1. Vista general del backlog", level=1)
    add_paragraph(doc, "_Total: 49 items. Estado al 26-Jun-2026: 41 completados, 3 en desarrollo, 5 pendientes. "
                      "Prioridad: Critical (P0) > High (P1) > Medium (P2) > Low (P3)._")

    doc.add_heading("2. Items cerrados en v1.8 (Iter 11 + Iter 12)", level=1)
    items_cerrados = [
        ["DT-ITER12-01", "P0", "Feature", "_BYTEA 10MB limit en rats.archivo_base_legal_datos y tkt_adjuntos.data (CHECK constraint PostgreSQL)_",
         "LargeBinary(10_000_000) + migration SQL", "CERRADO"],
        ["DT-ITER12-02", "P0", "Feature", "_Test IL mínimo 50 caracteres: Pydantic Field(min_length=50) + RatWizard + RatEditForm validación_",
         "schemas/rat.py, RatWizard.tsx, RatEditForm.tsx", "CERRADO"],
        ["DT-ITER12-03", "P0", "Feature", "_Hash SHA-256 automático evidencia ARCO: computa de tkt_adjuntos al resolver TKT_",
         "routes/tkt_solicitud_derecho.py PATCH", "CERRADO"],
        ["DT-ITER12-04", "P1", "Feature", "_causal_rechazo enum cerrado (7 causales Art. 29 RL) + dropdown TicketDrawer_",
         "schemas/tkt_solicitud_derecho.py, TicketDrawer.tsx", "CERRADO"],
        ["DT-ITER12-05", "P1", "Feature", "_Toggle ARCO touch target 44x44px (mobile accessibility WCAG 2.1)_",
         "solicitud_derecho/page.tsx", "CERRADO"],
        ["DT-ITER12-06", "P1", "Feature", "_Notificación APDC automatizada: actualizar_brecha() envía email al DPO_",
         "services/breach_service.py", "CERRADO"],
        ["DT-ITER12-07", "P1", "Feature", "_Notificación a titulares automatizada: actualizar_brecha() loggea cuando notificado_titulares=true_",
         "services/breach_service.py", "CERRADO"],
        ["DT-ITER12-08", "P1", "Feature", "_TKT no puede resolverse sin evidencia: HTTP 400 si estado=resuelto sin adjuntos/hash_",
         "routes/tkt_solicitud_derecho.py PATCH", "CERRADO"],
        ["DT-ITER12-09", "P1", "Feature", "_15 campos Tier 1+Tier 2 RAT (datos_nna, nivel_confidencialidad, etc.)_",
         "models/rat.py, schemas/rat.py, migrations SQL", "CERRADO"],
    ]
    add_styled_table(doc, ["ID", "Prioridad", "Tipo", "Título", "Archivos", "Estado"],
                     items_cerrados, col_widths_cm=[1.8, 1.5, 1.5, 5.5, 3.0, 1.7],
                     first_col_bold=True, underline_new=True)

    doc.add_heading("3. Items pendientes (QW-ITER13)", level=1)
    items_pendientes = [
        ["QW-ITER13-01", "P2", "Feature", "Paginación en listados >100 registros (RAT/ARCO/Brechas)", "Alto esfuerzo"],
        ["QW-ITER13-02", "P3", "Feature", "Retry logic en OCI uploads (resilience)", "Medio esfuerzo"],
        ["QW-ITER13-03", "P2", "Feature", "Logs de auditoría en tabla audit_log (Art. 28 Ley 21.719)", "Medio esfuerzo"],
    ]
    add_styled_table(doc, ["ID", "Prioridad", "Tipo", "Título", "Esfuerzo estimado"],
                     items_pendientes, col_widths_cm=[1.8, 1.5, 1.5, 5.5, 3.0],
                     first_col_bold=True)

    add_final_note(doc)
    doc.save(OUT_FILE)
    print(f"[OK] {OUT_FILE}")


if __name__ == "__main__":
    build()
