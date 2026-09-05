"""
Build 03 — Historias de Usuario v1.6.5 (Post Iter 11 + Iter 12 audit-loop)
Genera: docs/documentacion_oficial/03_Historias_Usuario_Custodio_RAT_Manager_v1.6.5.docx
Cambios v1.6.5:
- Iter 11: 15 campos Tier 1+Tier 2 RAT (HU-086 a HU-089)
- Iter 12: 9 fixes CRITICOS+ALTOS (HU-090 a HU-097)
- Score: 6.3/10 (RAT 6.2, ARCO 6.8, Brechas 5.9)
"""
import os
import sys
_THIS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _THIS)
from _theme_custodio import *
import _theme_custodio
_theme_custodio.DOC_VERSION = "v1.6.5"

OUT_DIR = r"C:\Users\chelo\Desktop\RAT_opencode\docs\documentacion_oficial"
ASSETS_DIR = os.path.join(OUT_DIR, "assets")
OUT_FILE = os.path.join(OUT_DIR, "03_Historias_Usuario_Custodio_RAT_Manager_v1.6.5.docx")
DOC_CODE = "CUST-DOC-03"
DOC_TITLE = "Historias de Usuario"


def build():
    doc = new_document()
    add_header_footer(doc, DOC_TITLE)
    add_cover(doc, title="HISTORIAS DE USUARIO",
              subtitle="Backlog priorizado por valor y rol",
              code=DOC_CODE)
    add_version_control(doc, DOC_CODE, DOC_TITLE, changes=[
        ("1.0", "Junio 2026", "Creación inicial del backlog de historias de usuario."),
        ("1.1", "Junio 2026", "Auditoría técnica: HU-041 a HU-051 para Consentimientos y Tickets ARCO."),
        ("1.2", "Junio 2026", "_Auditoría v1.2: módulo Feriados (HU-052 a HU-055), fixes P0 (blacklist, IDOR, CSV)._"),
        ("1.3", "Junio 2026", "_Beta Launch: RBAC fixes DT-014/DT-015 (HU-056/HU-057), /health (HU-058), módulo EIPD (HU-059/HU-060)._"),
        ("1.4", "Junio 2026", "_Post-OCI: descarga con fallback chain (HU-061), Admin Asesor IA (HU-062/HU-063), OCI storage (EP-12)._"),
        ("1.5", "Junio 2026", "_Seguridad: CSRF (HU-064), Encryption at Rest (HU-065), Service Layer (HU-066), Schemas (HU-067)._"),
        ("1.6", "Junio 2026", "_UI/UX: RatDetailModal (HU-068), Drawer responsive (HU-069), Dashboard clickable (HU-070), Sort estable (HU-071)._"),
        ("1.7", "Junio 2026", "Sprint 1: FORMADMIN ARCO QW1-QW10 (HU-072 a HU-078). Sprint 2: SLA Alert T-2d (HU-079 a HU-081), Export ARCO (HU-082 a HU-085)."),
        ("1.8", "Junio 2026", "_Iter 11: 15 campos Tier 1+Tier 2 RAT (HU-086 a HU-089). Iter 12: 9 fixes CRITICOS+ALTOS (HU-090 a HU-097). Score 6.3/10 (RAT 6.2, ARCO 6.8, Brechas 5.9)._"),
    ])
    add_toc(doc)

    doc.add_heading("1. Introducción", level=1)
    add_paragraph(doc, f"Este documento contiene las historias de usuario (HU) de {BRAND_FULL} "
                      "en formato 'Como/Quiero/Para', con criterios de aceptación, prioridad "
                      "y complejidad estimada (Fibonacci). Organizadas por épicas y trazadas a RF-###.")

    doc.add_heading("2. Épicas del producto", level=1)
    epicas = [
        ["EP-01", "Autenticación y multi-tenancy", "Login, sesión, empresas, aislamiento por rol."],
        ["EP-02", "Gestión del RAT", "Crear, editar, duplicar, eliminar, aprobar."],
        ["EP-03", "Cumplimiento", "Alertas, completitud, riesgos, EIPD, consentimientos."],
        ["EP-04", "Brechas de seguridad", "Art. 14 bis, plazo APDC 72h, notificaciones."],
        ["EP-05", "Derechos ARCO", "Art. 14 y 16 bis, formulario público, ticket."],
        ["EP-06", "Reportes y exportaciones", "CSV, PDF, CNI, dashboard."],
        ["EP-07", "Sugerencias por rubro", "Plantillas prellenadas por industria."],
        ["EP-08", "Auditoría", "Bitácora con hash chain."],
        ["EP-09", "Asistente IA", "Chat contextual sobre la Ley 21.719."],
        ["EP-10", "Feriados nacionales", "Gestión de feriados chilenos para días hábiles."],
        ["EP-11", "Consentimientos y EIPD", "Registro de consentimientos (Art. 12) y Evaluaciones de Impacto (Art. 15 bis)."],
        ["EP-12", "_OCI Object Storage_", "_Almacenamiento de documentos en OCI con fallback a BYTEA._"],
    ]
    add_styled_table(doc, ["ID", "Épica", "Descripción"], epicas,
                     col_widths_cm=[1.8, 5.0, 10.7], first_col_bold=True, underline_new=True)

    doc.add_heading("3. Listado de historias de usuario (selección nuevas)", level=1)

    doc.add_heading("3.1 Iter 11: 15 Campos Tier 1+Tier 2 RAT", level=2)
    hus_iter11 = [
        ["HU-086", "EP-02", "RF-141", "Alta", "M", "Registrar datos NNA en RAT"],
        ["HU-087", "EP-02", "RF-142-149", "Media", "S", "Registrar nivel confidencialidad y estructura del dato"],
        ["HU-088", "EP-02", "RF-146-149", "Media", "S", "Registrar ciclo de procesamiento y frecuencia"],
        ["HU-089", "EP-02", "RF-150-155", "Media", "M", "Registrar campos operativos Tier 2"],
    ]
    add_styled_table(doc, ["ID", "EP", "RF", "Prioridad", "Complex", "Título"], hus_iter11,
                     col_widths_cm=[1.5, 1.0, 1.5, 1.5, 1.5, 10.5], first_col_bold=True, underline_new=True)

    doc.add_heading("3.2 Iter 12: Fixes CRÍTICOS y ALTOS", level=2)
    hus_iter12 = [
        ["HU-090", "EP-02", "RF-156", "CRÍTICO", "S", "_Validar límite 10MB en archivos BYTEA (archivo_base_legal, tkt_adjunto)_"],
        ["HU-091", "EP-02", "RF-157", "CRÍTICO", "S", "_Test IL con mínimo 50 caracteres como validación obligatoria (Art. 16)_"],
        ["HU-092", "EP-05", "RF-158", "CRÍTICO", "M", "_Hash SHA-256 de evidencia ARCO computado automáticamente al resolver TKT_"],
        ["HU-093", "EP-05", "RF-159", "ALTO", "S", "_causal_rechazo con enum cerrado de 7 causales Art. 29 RL_"],
        ["HU-094", "EP-05", "RF-160", "ALTO", "S", "_Toggle ARCO con touch target 44x44px para accessibility mobile_"],
        ["HU-095", "EP-04", "RF-161", "ALTO", "M", "_Notificación APDC automatizada al marcar notificado_apdc=true_"],
        ["HU-096", "EP-04", "RF-162", "ALTO", "M", "_Notificación a titulares automatizada al marcar notificado_titulares=true_"],
        ["HU-097", "EP-05", "RF-158", "ALTO", "S", "_TKT no puede resolverse sin evidencia ni hash (validación HTTP 400)_"],
    ]
    add_styled_table(doc, ["ID", "EP", "RF", "Prioridad", "Complex", "Título"], hus_iter12,
                     col_widths_cm=[1.5, 1.0, 1.5, 1.5, 1.5, 10.5], first_col_bold=True, underline_new=True)

    doc.add_heading("4. Épicas del producto (completo)", level=1)
    epicas_full = [
        ["EP-01", "Autenticación y multi-tenancy", "HU-001 a HU-009"],
        ["EP-02", "Gestión del RAT", "HU-010 a HU-040, HU-086 a HU-089"],
        ["EP-03", "Cumplimiento", "HU-041 a HU-049"],
        ["EP-04", "Brechas de seguridad", "HU-050 a HU-054, HU-095 a HU-096"],
        ["EP-05", "Derechos ARCO", "HU-060 a HU-068, HU-092 a HU-094, HU-097"],
        ["EP-06", "Reportes y exportaciones", "HU-070 a HU-080"],
        ["EP-07", "Sugerencias por rubro", "HU-040 a HU-041"],
        ["EP-08", "Auditoría", "HU-080 a HU-082"],
        ["EP-09", "Asistente IA", "HU-090 a HU-094"],
        ["EP-10", "Feriados nacionales", "HU-052 a HU-055"],
        ["EP-11", "Consentimientos y EIPD", "HU-056 a HU-059"],
        ["EP-12", "OCI Object Storage", "HU-061 a HU-063"],
    ]
    add_styled_table(doc, ["ID", "Épica", "HUs"], epicas_full,
                     col_widths_cm=[1.8, 5.0, 10.7], first_col_bold=True)

    add_open_questions(doc, [
        "¿Se debe implementar autoguardo en wizard RAT?",
        "¿Se estiman HU con Planning Poker en sesiones de refinement?",
    ])
    add_risks_appendix(doc, [
        ("R-HU-01", "Pendientes: Z-01 (security headers), Z-02 (CORS restrictivo), Z-03 (file upload validation).", "Alto"),
    ])
    add_id_glossary(doc, [
        ("HU-###", "Historia de Usuario", "Necesidad del usuario en formato 'Como/Quiero/Para'."),
        ("EP-###", "Épica", "Conjunto de HU relacionadas."),
    ])
    add_final_note(doc)
    doc.save(OUT_FILE)
    print(f"[OK] {OUT_FILE}")


if __name__ == "__main__":
    build()
