"""
Build 06 — Arquitectura de Software v1.9 (Post Iter 11 + Iter 12)
Genera: docs/documentacion_oficial/06_Arquitectura_Software_Custodio_RAT_Manager_v1.9.docx
Cambios v1.9:
- Iter 11: 15 campos Tier 1+Tier 2 RAT (ADR-23)
- Iter 12: ADR-24 BYTEA limit 10MB, ADR-25 Test IL min 50chars, ADR-26 Hash SHA-256 auto ARCO
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
OUT_FILE = os.path.join(OUT_DIR, "06_Arquitectura_Software_Custodio_RAT_Manager_v1.9.docx")
DOC_CODE = "CUST-DOC-06"
DOC_TITLE = "Arquitectura de Software"


def build():
    doc = new_document()
    add_header_footer(doc, DOC_TITLE)
    add_cover(doc, title="ARQUITECTURA DE SOFTWARE",
              subtitle="Diagramas C4, despliegue, secuencias y decisiones técnicas",
              code=DOC_CODE)
    add_version_control(doc, DOC_CODE, DOC_TITLE, changes=[
        ("1.0", "Junio 2026", "Creación inicial de la arquitectura."),
        ("1.1", "Junio 2026", "Token blacklist LRU, hash chain en audit_log, patrón Repository, PII masking, optimización N+1."),
        ("1.2", "Junio 2026", "_Token blacklist, IDOR protection, CSV sanitize, hash chain, PII masking._"),
        ("1.3", "Junio 2026", "_Beta Launch: /health endpoint (ADR-12), RBAC fixes DT-014/DT-015, router fixes CB-01/CB-02._"),
        ("1.4", "Junio 2026", "_OCI Object Storage con fallback chain (ADR-14), Admin Asesor IA (ADR-15), MiniMax M2.7._"),
        ("1.5", "Junio 2026", "_Seguridad: CSRF (S14), Encryption at Rest Fernet (C1), Service Layer (A6), Schemas Pydantic (A10)._"),
        ("1.6", "Junio 2026", "_UI/UX: RatDetailModal (ADR-16), Drawer responsive (ADR-17), Dashboard clickable (ADR-18), useRef stable callbacks._"),
        ("1.7", "Junio 2026", "Sprint 1: FormADMIN ARCO QW1-QW10 (ADR-19). Sprint 2: Task SLA_ALERT_T2 pattern (ADR-20), Export service (ADR-21), GitHub Actions (ADR-22)."),
        ("1.8", "Junio 2026", "_Iter 11: 15 campos Tier 1+Tier 2 RAT (ADR-23). Iter 12: ADR-24 BYTEA limit 10MB, ADR-25 Test IL min 50chars, ADR-26 Hash SHA-256 auto ARCO, ADR-27 causal_rechazo enum, ADR-28 notificaciones auto brechas._"),
        ("1.9", "Julio 2026", "_IDOR multi-tenant get_rat_for_user() en 6 endpoints (ADR-29). base_legal_valida strict (ADR-30). ConsentimientoAlert (ADR-31). Homologación orden campos RAT (ADR-32). PDF títulos sección (ADR-33)._"),
    ])
    add_toc(doc)

    doc.add_heading("1. Resumen ejecutivo", level=1)
    add_paragraph(doc, f"{BRAND_FULL} es una aplicación SaaS B2B para gestión del RAT (Ley 21.719). "
                      "Arquitectura modular, multi-tenant, desplegada en Vercel con Neon PostgreSQL. "
                      "Backend: FastAPI serverless. Frontend: Next.js 16 con App Router.")
    add_paragraph(doc, "_En v1.9 se implementó: BYTEA 10MB limit (DoS protection), "
                      "Test IL min 50 chars (Art. 16 Ley 21.719), Hash SHA-256 auto ARCO, "
                      "causal_rechazo enum cerrado (Art. 29 RL), notificaciones auto brechas, "
                      "toggle 44px mobile accessibility. Score: 6.3/10._")

    doc.add_heading("2. Decisiones de Arquitectura (ADRs) — Novedades v1.9", level=1)
    adrs_nuevos = [
        ["ADR-23", "Iter 11: Campos Tier 1+Tier 2 RAT", "Alta", "2026-06-25",
         "_Se agregan 15 campos nuevos a rats: datos_nna, nivel_confidencialidad, estructura_dato, datos_anonimizados, datos_seudonimizados, ciclo_procesamiento, automatizacion, frecuencia, transferencia_nacional, doc_clausulas, medidas_organizativas, mecanismos_eliminacion, tecnica_anonimizacion, origen_dato_portabilidad, fecha_levantamiento. Modelos SQLAlchemy actualizados, schemas Pydantic, migraciones SQL._"],
        ["ADR-24", "CRÍTICO: BYTEA 10MB limit (DoS protection)", "Crítica", "2026-06-26",
         "_CHECK constraint octet_length <= 10_000_000 en rats.archivo_base_legal_datos y tkt_adjuntos.data. LargeBinary(10_000_000) en SQLAlchemy. Aplica a archivo_base_legal (RAT) y tkt_adjunto.data (ARCO)._"],
        ["ADR-25", "CRÍTICO: Test IL mínimo 50 caracteres (Art. 16 Ley 21.719)", "Crítica", "2026-06-26",
         "_Pydantic Field(min_length=50) en test_interes_legitimo. RatWizard y RatEditForm validan en frontend con toast error. AlertBanner obligatorio en UI._"],
        ["ADR-26", "CRÍTICO: Hash SHA-256 automático evidencia ARCO", "Crítica", "2026-06-26",
         "_PATCH /tkt-solicitud-derecho/{id} computa SHA-256 de todos los adjuntos (tkt_adjuntos) al resolver el ticket. Si no hay adjuntos ni respuesta_texto, retorna HTTP 400._"],
        ["ADR-27", "ALTO: causal_rechazo enum cerrado (Art. 29 RL)", "Alta", "2026-06-26",
         "_CausalRechazoEnum con 7 valores: falta_identidad, solicitud_manifiestamente_infundada, solicitud_excesiva, falta_poder_notorial, plazo_vencido, identidad_no_verificada, otro. Dropdown en TicketDrawer._"],
        ["ADR-28", "ALTO: Notificaciones automatizadas en brechas (Art. 14 bis Ley 21.719)", "Alta", "2026-06-26",
         "_actualizar_brecha() envía email al DPO cuando notificado_apdc=true. Logueba cuando notificado_titulares=true (preparado para canal)._"],
        ["ADR-29", "CRÍTICO: IDOR multi-tenant en 6 endpoints RAT", "Crítica", "2026-07-05",
         "_get_rat_for_user() en GET /rats/{id}, PUT /rats/{id}, DELETE /rats/{id}, POST /rats/{id}/revision, POST /rats/{id}/aprobar, GET /rats/{id}/auditoria. Retorna 404 si empresa no coincide, superadmin accede a todos._"],
        ["ADR-30", "ALTO: base_legal_valida strict contra enum taxativo", "Alta", "2026-07-05",
         "_Validación contra 6 opciones: consentimiento, interes_legitimo, contrato, obligacion_legal, tarea_publica, interes_publico. Antes siempre retornaba v.strip()._"],
        ["ADR-31", "ALTO: ConsentimientoAlert en RatEditForm.handleSave()", "Alta", "2026-07-05",
         "_listarConsentimientos(company_id, rat.id, true) antes de guardar. Si datos_sensibles=True y no hay consentimiento activo → toast error y no guarda._"],
        ["ADR-32", "ALTO: Homologación orden campos RAT (5 pasos canónicos)", "Alta", "2026-07-05",
         "_RatDetailView, RatEditForm, RatWizard y PDF reordenados: Identificación → Datos tratados → Finalidad y ley → Almacenamiento → Compliance operativo._"],
        ["ADR-33", "MEDIO: PDF con títulos de sección y alertas rojas", "Media", "2026-07-05",
         "_PASO 1 — IDENTIFICACIÓN, PASO 2 — DATOS TRATADOS, etc. con fondo COLOR_PRIMARIO (#1B3A6B) y texto blanco bold. Alertas rojas al final de cada ficha._"],
    ]
    add_styled_table(doc, ["ID", "Título", "Prioridad", "Fecha", "Decisión"], adrs_nuevos,
                     col_widths_cm=[1.5, 3.5, 1.5, 1.5, 10.5], first_col_bold=True, underline_new=True)

    add_id_glossary(doc, [
        ("ADR-###", "Decisión de Arquitectura", "Decisión técnica formal que modifica la arquitectura."),
    ])
    add_final_note(doc)
    doc.save(OUT_FILE)
    print(f"[OK] {OUT_FILE}")


if __name__ == "__main__":
    build()
