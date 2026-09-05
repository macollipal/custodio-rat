"""
Build 06 — Decisiones Técnicas (ADR) v1.7
Genera: docs/documentacion_oficial/06_Decisiones_Tecnicas_Custodio_RAT_Manager_v1.7.docx
Cambios v1.7:
- ADR-19: FormADMIN ARCO — validación en vivo, debounce, doble input email, tooltips Ley 21.719
- ADR-20: Task SLA_ALERT_T2 — TaskType enum, _run_sla_alert_t2(), agrupar por empresa, email grupal HTML
- ADR-21: Export Service — csv/excel/pdf generators en export_tkt_service.py, endpoints REST
- ADR-22: GitHub Actions SLA Alert — workflow sla-alert.yml con cron 4h + workflow_dispatch
"""
import os
import sys
_THIS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _THIS)
from _theme_custodio import *
import _theme_custodio
_theme_custodio.DOC_VERSION = "v1.7"

OUT_DIR = r"C:\Users\chelo\Desktop\RAT_opencode\docs\documentacion_oficial"
ASSETS_DIR = os.path.join(OUT_DIR, "assets")
OUT_FILE = os.path.join(OUT_DIR, "06_Decisiones_Tecnicas_Custodio_RAT_Manager_v1.7.docx")
DOC_CODE = "CUST-DOC-06"
DOC_TITLE = "Decisiones Técnicas"


def build():
    doc = new_document()
    add_header_footer(doc, DOC_TITLE)
    add_cover(doc, title="DECISIONES TÉCNICAS",
              subtitle="Architecture Decision Records (ADR)",
              code=DOC_CODE)
    add_version_control(doc, DOC_CODE, DOC_TITLE, changes=[
        ("1.0", "Junio 2026", "Creación inicial de la arquitectura."),
        ("1.1", "Junio 2026", "Token blacklist LRU, hash chain en audit_log, patrón Repository, PII masking, optimización N+1."),
        ("1.2", "Junio 2026", "_Token blacklist, IDOR protection, CSV sanitize, hash chain, PII masking._"),
        ("1.3", "Junio 2026", "_Beta Launch: /health endpoint (ADR-12), RBAC fixes DT-014/DT-015, router fixes CB-01/CB-02._"),
        ("1.4", "Junio 2026", "_OCI Object Storage con fallback chain (ADR-14), Admin Asesor IA (ADR-15), MiniMax M2.7._"),
        ("1.5", "Junio 2026", "_Seguridad: CSRF (S14), Encryption at Rest Fernet (C1), Service Layer (A6), Schemas Pydantic (A10)._"),
        ("1.6", "Junio 2026", "_UI/UX: RatDetailModal (ADR-16), Drawer responsive (ADR-17), Dashboard clickable (ADR-18), useRef stable callbacks._"),
        ("1.7", "Junio 2026", "_Sprint 1: FormADMIN ARCO pattern (ADR-19). Sprint 2: SLA Alert task pattern (ADR-20), Export service (ADR-21), GitHub Actions (ADR-22)._"),
    ])
    add_toc(doc)

    doc.add_heading("1. Resumen", level=1)
    add_paragraph(doc, f"{BRAND_FULL} es una aplicación SaaS B2B para gestión del RAT (Ley 21.719). "
                      "Este documento lista las decisiones arquitectónicas significativas (ADR) que guían el diseño y desarrollo.")

    doc.add_heading("2. Decisiones técnicas relevantes", level=1)
    adrs = [
        ["ADR-01", "Next.js 16 + React 19", "Rendimiento, ecosistema, despliegue directo a Vercel, TypeScript."],
        ["ADR-02", "FastAPI sobre Flask o Django REST", "Tipado nativo, async/await, OpenAPI automático, Pydantic."],
        ["ADR-03", "SQLAlchemy 2.0", "Madurez, soporte Postgres, migraciones simples."],
        ["ADR-04", "Neon PostgreSQL", "Compatibilidad Vercel, plan gratuito, branching, AES-256."],
        ["ADR-05", "_OCI Object Storage para binarios_", "_Almacenamiento en OCI con fallback a BYTEA. bucket custodio-documents-qa._"],
        ["ADR-06", "JWT 8h + blacklist LRU", "Balance seguridad/UX. Blacklist permite logout efectivo."],
        ["ADR-07", "Rate limiting con slowapi", "Mitigación de fuerza bruta y abuso."],
        ["ADR-08", "Mermaid pre-renderizado a PNG", "Word no soporta Mermaid runtime."],
        ["ADR-09", "Audit log con hash chain", "Inmutabilidad del registro de auditoría."],
        ["ADR-10", "Patrón Repository (app/repositories/)", "Abstracción de acceso a datos; selectinload evitan N+1."],
        ["ADR-11", "PIIMaskingFilter en logging", "Mask email, RUT, IP, tokens y contraseñas."],
        ["ADR-12", "_GET /health y /health/db endpoints_", "_Health checks sin auth para monitoreo. /health stateless, /health/db prueba DB._"],
        ["ADR-13", "_RBAC: admin_empresa RAT + usuario breach_", "_DT-014: get_empresas_usuario() en POST /rats/. DT-015: validación de rol en POST /brechas/._"],
        ["ADR-14", "_OCI Object Storage con fallback chain_", "_PAR → signed GET → BYTEA. OCISigner para firma RSA. copy_to_archive antes de delete._"],
        ["ADR-15", "_Admin Asesor IA_", "_POST /admin/asesor/index, GET /admin/asesor/stats, DELETE /admin/asesor/documents/{id}. Solo superadmin._"],
        ["ADR-16", "_RatDetailModal con tabs Ver/Editar_", "_Componente React con useReducer. Slots: Detalle, Editar, Historial. OnDuplicate/OnDelete._"],
        ["ADR-17", "_Drawer responsive 5 sizes_", "_Drawer responsive: 5 sizes (sm/md/lg/xl/2xl), maxHeight 92vh, hasHeader conditional._"],
        ["ADR-18", "_Dashboard clickable_", "_RatDetailModal in-page. onDuplicate/onDelete con confirmación. useRef para callbacks estables._"],
        ["ADR-19", "_FormADMIN ARCO pattern_", "_Validación en vivo, debounce 300ms, doble input email (confirmEmail), tooltips Ley 21.719._"],
        ["ADR-20", "_Task SLA_ALERT_T2_", "_TaskType enum, _run_sla_alert_t2(), agrupar por empresa, email grupal HTML._"],
        ["ADR-21", "_Export Service_", "_csv/excel/pdf generators en export_tkt_service.py, endpoints REST._"],
        ["ADR-22", "_GitHub Actions SLA Alert_", "_workflow sla-alert.yml con cron 4h + workflow_dispatch._"],
    ]
    add_styled_table(doc, ["ID", "Decisión", "Justificación"], adrs,
                     col_widths_cm=[1.8, 5.0, 10.7], first_col_bold=True,
                     underline_new=True)

    add_id_glossary(doc, [
        ("ADR", "Architecture Decision Record", "Documento que captura una decisión arquitectónica significativa."),
        ("SLA", "Service Level Agreement", "Acuerdo de nivel de servicio para tiempos de respuesta."),
    ])
    add_final_note(doc)
    doc.save(OUT_FILE)
    print(f"[OK] {OUT_FILE}")


if __name__ == "__main__":
    build()
