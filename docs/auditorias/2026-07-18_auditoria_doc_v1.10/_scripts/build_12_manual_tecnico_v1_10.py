"""
Build 12 — Manual Técnico v1.10 (Post Iter 11 + Iter 12)
Genera: docs/documentacion_oficial/12_Manual_Tecnico_Custodio_RAT_Manager_v1.10.docx
Cambios v1.10:
- Flujo BYTEA 10MB limit
- Test IL min 50 chars
- Hash SHA-256 auto ARCO
- causal_rechazo enum
"""
import os
import sys
_THIS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _THIS)
from _theme_custodio import *
import _theme_custodio
_theme_custodio.DOC_VERSION = "v1.10"

OUT_DIR = r"C:\Users\chelo\Desktop\RAT_opencode\docs\documentacion_oficial"
ASSETS_DIR = os.path.join(OUT_DIR, "assets")
OUT_FILE = os.path.join(OUT_DIR, "12_Manual_Tecnico_Custodio_RAT_Manager_v1.10.docx")
DOC_CODE = "CUST-DOC-12"
DOC_TITLE = "Manual Técnico"
DOC_DATE = "Junio 2026"


def build():
    doc = new_document()
    add_header_footer(doc, DOC_TITLE)
    add_cover(doc, title="MANUAL TÉCNICO",
              subtitle="Arquitectura, seguridad, despliegue y operaciones",
              code=DOC_CODE)
    add_version_control(doc, DOC_CODE, DOC_TITLE, changes=[
        ("1.0", "Junio 2026", "Manual técnico inicial: auth, JWT, RBAC, RAT, ARCO."),
        ("1.1", "Junio 2026", "Actualizado con Token blacklist, hash chain, PII masking, CSRF."),
        ("1.2", "Junio 2026", "_Csv injection sanitization, IDOR protection, rate limiting._"),
        ("1.3", "Junio 2026", "_Beta Launch: /health, RBAC fixes, Fernet encryption._"),
        ("1.4", "Junio 2026", "_OCI Object Storage + Admin Asesor IA._"),
        ("1.5", "Junio 2026", "_CSRF middleware, Encryption at Rest Fernet, Service Layer._"),
        ("1.6", "Junio 2026", "_UI/UX: RatDetailModal, Drawer responsive, Dashboard clickable._"),
        ("1.7", "Junio 2026", "Sprint 1+2: FORMADMIN ARCO, SLA Alert T-2d, Export ARCO CSV/Excel/PDF."),
        ("1.8", "Junio 2026", "_Iter 11+12: BYTEA 10MB limit, Test IL min 50chars, Hash SHA-256 auto ARCO, causal_rechazo enum, notificaciones auto._"),
        ("1.9", "Julio 2026", "_IDOR multi-tenant get_rat_for_user() en 6 endpoints RAT. base_legal_valida strict. ConsentimientoAlert. Homologación orden campos RAT. PDF títulos de sección. Encoding UTF-8 fix._"),
    ])
    add_toc(doc)

    doc.add_heading("1. Cambios técnicos en v1.10", level=1)
    cambios_v18 = [
        ["BYTEA 10MB limit", "CRÍTICO", "models/rat.py, models/tkt_adjunto.py, migrations/2026_06_26_013_bytea_limit_10mb.sql",
         "LargeBinary(10_000_000) en SQLAlchemy. CHECK constraint en PostgreSQL. Aplica a rats.archivo_base_legal_datos y tkt_adjuntos.data."],
        ["Test IL min 50 chars", "CRÍTICO", "schemas/rat.py, components/rat/RatWizard.tsx, components/rat/RatEditForm.tsx",
         "Pydantic Field(min_length=50). Validación en RatWizard paso 3 y RatEditForm. Toast error si <50 chars."],
        ["Hash SHA-256 auto ARCO", "CRÍTICO", "routes/tkt_solicitud_derecho.py (PATCH endpoint)",
         "hashlib.sha256() sobre todos los tkt_adjuntos.data en orden. Asignado a evidencia_respuesta_hash al resolver."],
        ["causal_rechazo enum", "ALTO", "schemas/tkt_solicitud_derecho.py, models/tkt_solicitud_derecho.py, components/tkt/TicketDrawer.tsx",
         "CausalRechazoEnum: 7 valores (Art. 29 RL). Dropdown en TicketDrawer cuando estado=rechazado. Toast error si rechazado sin causal."],
        ["Toggle ARCO 44px", "ALTO", "app/solicitud_derecho/page.tsx",
         "w-4 h-4 → w-11 h-11. Touch target WCAG 2.1 Level AA para mobile."],
        ["Notificaciones APDC auto", "ALTO", "services/breach_service.py (actualizar_brecha)",
         "Email al DPO via notificar_nueva_brecha() cuando notificado_apdc=true. DRY_RUN si SMTP no configurado."],
        ["Notificaciones titulares auto", "ALTO", "services/breach_service.py (actualizar_brecha)",
         "Log.info cuando notificado_titulares=true. Preparado para automatizar por canal (email/SMS/otro)."],
    ]
    add_styled_table(doc, ["Cambio", "Severidad", "Archivos", "Descripción"], cambios_v18,
                     col_widths_cm=[2.5, 1.5, 5.0, 9.0], first_col_bold=True, underline_new=True)

    doc.add_heading("2. Flujo de evidencia ARCO con hash SHA-256", level=1)
    add_numbered(doc, "1. Admin crea/adhiere documentos a ticket TKT vía POST /tkt-solicitud-derecho/{id}/adjuntos")
    add_numbered(doc, "2. Admin resuelve ticket: PATCH /tkt-solicitud-derecho/{id} con estado='resuelto'")
    add_numbered(doc, "3. Backend detecta estado=resuelto + ticket.evidencia_respuesta_hash == null")
    add_numbered(doc, "4. Backend calcula SHA-256 de todos los tkt_adjuntos.data (en orden por id)")
    add_numbered(doc, "5. Backend asigna sha.hexdigest() a ticket.evidencia_respuesta_hash y guarda en BD")
    add_numbered(doc, "6. Si no hay adjuntos ni respuesta_texto → HTTP 400: 'No se puede resolver sin evidencia'")
    add_numbered(doc, "7. Respuesta se envía al titular con hash en metadata de auditoría")

    doc.add_heading("3. Límite BYTEA 10MB", level=1)
    add_numbered(doc, "1. Frontend valida tamaño antes de subir (si aplica)")
    add_numbered(doc, "2. SQLAlchemy usa LargeBinary(10_000_000) → PostgreSQL tipo BYTEA sin límite explícito en tipo")
    add_numbered(doc, "3. CHECK constraint added via migración SQL: octet_length(column) <= 10_000_000")
    add_numbered(doc, "4. Si se intenta insertar >10MB → PostgreSQL raise_sql constraint violation → rollback")
    add_numbered(doc, "5. Error capturado por service layer → HTTP 400 o 500 según contexto")

    add_final_note(doc)
    doc.save(OUT_FILE)
    print(f"[OK] {OUT_FILE}")


if __name__ == "__main__":
    build()
