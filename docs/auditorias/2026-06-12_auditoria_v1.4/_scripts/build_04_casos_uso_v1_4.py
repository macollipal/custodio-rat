"""
Build 04 — Casos de Uso v1.4 (Post-OCI Integration)
Genera: docs/documentacion_oficial/04_Casos_de_Uso_Custodio_RAT_Manager_v1.4.docx
Cambios v1.4:
- CU-048: Descargar archivo RAT con fallback OCI (PAR → signed GET → BYTEA)
- CU-049: Admin Asesor IA - Indexar corpus
- CU-050: Admin Asesor IA - Stats y eliminar chunks
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
OUT_FILE = os.path.join(OUT_DIR, "04_Casos_de_Uso_Custodio_RAT_Manager_v1.4.docx")
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
        ("1.2", "Junio 2026", "_Auditoría v1.2: módulo Feriados (CU-039 a CU-042), fixes P0 (blacklist, IDOR, CSV, hash chain)._"),
        ("1.3", "Junio 2026", "_Beta Launch: RBAC fixes DT-014/DT-015 (CU-043/CU-044), /health (CU-045), EIPD (CU-047), consentimientos (CU-046)._"),
        ("1.4", "Junio 2026", "_Post-OCI: descarga con fallback chain (CU-048), Admin Asesor IA (CU-049/CU-050)._"),
    ])
    add_toc(doc)

    doc.add_heading("1. Introducción", level=1)
    add_paragraph(doc, f"Este documento especifica los casos de uso de {BRAND_FULL} "
                      "en formato formal. Cada CU incluye: identificador (CU-###), nombre, "
                      "actores, precondiciones, flujo principal, flujos alternativos y resultado esperado.")

    doc.add_heading("2. Listado consolidado de casos de uso", level=1)
    casos = [
        ["CU-001", "Iniciar sesión", "AC-01/02/03", "RF-001", "Login con JWT"],
        ["CU-002", "Cerrar sesión", "AC-01/02/03", "RF-004", "_Logout con blacklist LRU_"],
        ["CU-003", "Recuperar sesión activa", "AC-01/02/03", "RF-009", "GET /auth/me"],
        ["CU-004", "Cambiar contraseña propia", "AC-01/02/03", "RF-002", "PUT /auth/me/password"],
        ["CU-005", "Onboarding primera empresa", "AC-01", "RF-015", "Wizard inicial"],
        ["CU-006", "Crear empresa", "AC-01", "RF-010", "POST /companies"],
        ["CU-007", "Editar empresa", "AC-01/02", "RF-011", "PUT /companies/{id}"],
        ["CU-008", "Eliminar empresa", "AC-01", "RF-011", "DELETE /companies/{id}"],
        ["CU-009", "Asignar usuario a empresa", "AC-01/02", "RF-012", "POST /companies/{cid}/usuarios"],
        ["CU-010", "Crear proceso RAT (wizard)", "AC-02/03", "RF-020 a RF-029", "POST /rats"],
        ["CU-011", "Editar proceso RAT", "AC-02/03", "RF-029", "PUT /rats/{id}"],
        ["CU-012", "Duplicar proceso RAT", "AC-02/03", "RF-030", "Duplicar"],
        ["CU-013", "Eliminar proceso RAT", "AC-02/03", "RF-031", "DELETE /rats/{id}"],
        ["CU-014", "Aprobar proceso RAT", "AC-02/01", "RF-034", "POST /rats/{id}/aprobar"],
        ["CU-015", "Adjuntar documento base legal", "AC-02/03", "RF-026", "Subida a OCI con fallback BYTEA"],
        ["CU-016", "Listar procesos RAT con filtros", "AC-01/02/03", "RF-074", "GET /rats/reportes"],
        ["CU-017", "Exportar RATs a CSV", "AC-01/02", "RF-070", "_GET /rats/export/csv (sanitizado)_"],
        ["CU-018", "Exportar RATs a PDF", "AC-01/02", "RF-071", "GET /rats/export/pdf"],
        ["CU-019", "Exportar RAT individual a PDF", "AC-01/02/03", "RF-072", "GET /rats/{id}/export/pdf"],
        ["CU-020", "Consultar auditoría de RAT", "AC-01/02/03", "RF-081", "_GET /rats/{id}/auditoria (hash chain)_"],
        ["CU-021", "Registrar brecha de seguridad", "AC-01/02", "RF-050", "POST /brechas"],
        ["CU-022", "Alertar plazo APDC 72h", "Sistema", "RF-051", "Cálculo automático"],
        ["CU-023", "Presentar formulario ARCO público", "AC-05", "RF-060", "/solicitud_derecho"],
        ["CU-024", "Crear solicitud ARCO", "AC-05", "RF-062", "POST /solicitudes-derecho"],
        ["CU-025", "Responder solicitud ARCO", "AC-01/02", "RF-064", "PATCH /solicitudes-derecho/{id}/responder"],
        ["CU-026", "Gestionar ticket TKT", "AC-01/02", "RF-063/065", "PATCH /tkt-solicitud-derecho/{id}"],
        ["CU-027", "Consultar sugerencias de RAT", "AC-01/02/03", "RF-041", "POST /rats/sugerencias"],
        ["CU-028", "Gestionar rubros", "AC-01", "RF-042", "CRUD /rubros"],
        ["CU-029", "Consultar chat IA", "AC-01/02/03", "RF-090", "POST /ai/ask"],
        ["CU-030", "Ver dashboard de cumplimiento", "AC-01/02/03", "RF-075", "GET /rats/dashboard/{cid}"],
        ["CU-031", "Crear usuario", "AC-01", "RF-007", "POST /auth/users"],
        ["CU-032", "Cambiar contraseña de tercero", "AC-01", "RF-003", "PUT /auth/users/{id}/password"],
        ["CU-033", "Registrar consentimiento expreso", "AC-02/03", "RF-095", "_POST /consentimientos/ (CB-01 fix)_"],
        ["CU-034", "Crear ticket ARCO manualmente", "AC-02", "RF-099", "POST /tkt-solicitud-derecho"],
        ["CU-035", "Gestionar estado del ticket", "AC-02/03", "RF-100", "PATCH /tkt-solicitud-derecho/{id}"],
        ["CU-036", "Definir prioridad del ticket", "AC-02/03", "RF-101", "Prioridad: BAJA/NORMAL/URGENTE"],
        ["CU-037", "Agregar notas internas al ticket", "AC-02/03", "RF-103", "POST /tkt-solicitud-derecho/{id}/notas"],
        ["CU-038", "Ver historial de cambios del ticket", "AC-02/03", "RF-104", "GET /tkt-solicitud-derecho/{id}/historial"],
        ["CU-039", "Gestionar feriados nacionales (CRUD)", "AC-01", "RF-110", "CRUD /admin/feriados"],
        ["CU-040", "Subir feriados en bulk por CSV", "AC-01", "RF-111", "POST /admin/feriados/upload"],
        ["CU-041", "Exportar feriados a CSV", "AC-01", "RF-112", "GET /admin/feriados/export"],
        ["CU-042", "Verificar integridad de cadena de auditoría", "AC-01", "RF-081", "_GET /rats/auditoria/verify-chain_"],
        ["CU-043", "_Crear RAT en empresa asignada (DT-014)_", "AC-02", "RF-114", "_POST /rats/ (RBAC admin_empresa)_"],
        ["CU-044", "_usuario NO crea brecha (DT-015)_", "AC-03", "RF-115", "_POST /brechas/ (403 si rol=usuario)_"],
        ["CU-045", "_Health check del sistema_", "Sistema", "RF-116", "_GET /health y /health/db_"],
        ["CU-046", "_Gestionar consentimientos_", "AC-02/03", "RF-095 a RF-098", "_GET/POST /consentimientos/ (CB-01)_"],
        ["CU-047", "_Gestionar EIPD_", "AC-02/03", "RF-117 a RF-119", "_GET/POST/PUT /eipd/ (CB-02)_"],
        ["CU-048", "_Descargar documento con fallback OCI_", "AC-01/02/03", "RF-117/RF-119", "_GET /rats/{id}/archivo (PAR→signed GET→BYTEA)_"],
        ["CU-049", "_Indexar corpus del asesor IA_", "AC-01", "RF-118", "_POST /admin/asesor/index_"],
        ["CU-050", "_Gestionar chunks del asesor IA_", "AC-01", "RF-118", "_GET /admin/asesor/stats, DELETE /admin/asesor/documents/{id}_"],
    ]
    add_styled_table(doc, ["ID", "Nombre", "Actores", "Trazabilidad RF", "Disparador"],
                     casos, col_widths_cm=[1.5, 4.2, 2.0, 3.0, 4.5], first_col_bold=True,
                     underline_new=True)

    doc.add_heading("3. Especificación detallada de casos críticos", level=1)

    def spec_cu(cu_id, name, actors, pre, main_steps, alt_steps, post):
        doc.add_heading(f"{cu_id} — {name}", level=2)
        add_kv_table(doc, [
            ("ID", cu_id),
            ("Nombre", name),
            ("Actores", actors),
            ("Precondiciones", pre),
        ])
        doc.add_heading("Flujo principal", level=3)
        for s in main_steps:
            add_numbered(doc, s)
        if alt_steps:
            doc.add_heading("Flujos alternativos", level=3)
            for label, steps in alt_steps:
                add_paragraph(doc, label, bold=True)
                for s in steps:
                    add_numbered(doc, s)
        doc.add_heading("Resultado esperado", level=3)
        add_paragraph(doc, post)

    spec_cu("CU-001", "Iniciar sesión",
            "AC-01/02/03 — Superadmin, Admin empresa, Usuario",
            "El usuario accede a /login sin una sesión activa.",
            [
                "El usuario ingresa username y contraseña.",
                "El sistema valida credenciales con bcrypt.",
                "_El sistema consulta el token blacklist para verificar que el token no haya sido revocado._",
                "El sistema genera JWT con expiry 8h y retorna cookie httpOnly.",
                "El sistema redirige a /dashboard.",
            ],
            [
                ("A) Credenciales inválidas:", ["Mensaje 'Credenciales inválidas' sin revelar si el usuario existe."]),
                ("B) Rate limit excedido (5/min):", ["HTTP 429 + mensaje de esperar."]),
            ],
            "Usuario autenticado con JWT válido por 8h. Token sujeto a blacklist.")

    spec_cu("CU-048", "_Descargar documento con fallback OCI_",
            "AC-01/02/03 — Superadmin, Admin empresa, Usuario",
            "Usuario autenticado con acceso al RAT.",
            [
                "_El usuario pulsa 'Descargar' en el documento de base legal de un RAT._",
                "_GET /rats/{rat_id}/archivo se ejecuta._",
                "_Intento 1: El sistema intenta generar PAR (pre-signed URL) desde OCI._",
                "_Si PAR exitoso: retorna {url, nombre, content_type, expires_in_seconds}._",
                "_Si PAR falla (sin permisos IAM): continuar al intento 2._",
                "_Intento 2: El sistema descarga directamente desde OCI usando signed GET._",
                "_Si download exitoso: retorna bytes codificados en base64._",
                "_Si OCI falla: usar fallback BYTEA (datos almacenados en PostgreSQL)._",
                "_La descarga se registra en audit_log._",
            ],
            [
                ("A) Archivo no encontrado:", ["HTTP 404 Not Found."]),
                ("B) Sin acceso a la empresa:", ["HTTP 403 Forbidden."]),
            ],
            "_200 OK con URL pre-firmada (PAR) o bytes (signed GET o BYTEA). Auditoría registrada._")

    spec_cu("CU-049", "_Indexar corpus del asesor IA_",
            "AC-01 — Superadmin",
            "Superadmin autenticado.",
            [
                "_El superadmin accede a la sección de administración del asesor IA._",
                "_Selecciona archivos o directorios para indexar._",
                "_POST /admin/asesor/index se ejecuta con paths y opción force._",
                "_El sistema chunkifica el contenido (texto extraído, limpiado, dividido)._",
                "_El sistema almacena cada chunk en asesor_chunks._",
                "_Retorna estadísticas: indexed, skipped, errors, duration_ms._",
            ],
            [
                ("A) Indexación parcial:", ["Algunos archivos fallan, otros se indexan."]),
            ],
            "_200 OK con estadísticas de indexación. Auditoría registrada._")

    spec_cu("CU-050", "_Gestionar chunks del asesor IA_",
            "AC-01 — Superadmin",
            "Superadmin autenticado.",
            [
                "_GET /admin/asesor/stats: retorna estadísticas del corpus._",
                "_DELETE /admin/asesor/documents/{chunk_id}: elimina un chunk específico._",
                "_Ambas operaciones se registran en audit_log._",
            ],
            [
                ("A) Chunk no encontrado:", ["HTTP 404 Not Found."]),
            ],
            "_Stats con total chunks, fuentes, tamaño. Delete retorna {ok: true}._")

    add_open_questions(doc, [
        "¿Los CU deben incluir criterios de aceptación en Gherkin (V2)?",
        "¿Se deben modelar flujos de error sistemáticamente para todos los CU?",
    ])
    add_risks_appendix(doc, [
        ("R-CU-01", "CU-029 (IA) depende de servicio externo. Mitigación: mensaje informativo si no disponible.", "Medio"),
    ])
    add_id_glossary(doc, [
        ("CU-###", "Caso de Uso", "Interacción actor-sistema con flujos principal y alternativo."),
        ("AC-###", "Actor", "Persona, sistema o servicio externo."),
    ])
    add_final_note(doc)
    doc.save(OUT_FILE)
    print(f"[OK] {OUT_FILE}")


if __name__ == "__main__":
    build()