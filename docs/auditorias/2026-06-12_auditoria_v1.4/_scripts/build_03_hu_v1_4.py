"""
Build 03 — Historias de Usuario v1.4 (Post-OCI Integration)
Genera: docs/documentacion_oficial/03_Historias_Usuario_Custodio_RAT_Manager_v1.4.docx
Cambios v1.4:
- HU-061: Descargar archivo RAT con fallback OCI
- HU-062: Admin asesor IA (indexar corpus)
- HU-063: Admin asesor IA (stats y eliminar chunks)
- EP-12: OCI Object Storage
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
OUT_FILE = os.path.join(OUT_DIR, "03_Historias_Usuario_Custodio_RAT_Manager_v1.4.docx")
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

    doc.add_heading("3. Listado consolidado de historias de usuario", level=1)
    hus = [
        ["HU-001", "EP-01", "RF-001", "Alta", "M", "Login seguro"],
        ["HU-002", "EP-01", "RF-004", "Alta", "S", "Logout efectivo con blacklist"],
        ["HU-003", "EP-01", "RF-002", "Alta", "S", "Cambiar mi contraseña"],
        ["HU-004", "EP-01", "RF-003", "Media", "S", "Admin cambia contraseña de tercero"],
        ["HU-005", "EP-01", "RF-015", "Media", "M", "Onboarding de primera empresa"],
        ["HU-006", "EP-01", "RF-010", "Alta", "M", "Crear empresa"],
        ["HU-007", "EP-01", "RF-007", "Alta", "M", "Crear usuario con rol"],
        ["HU-008", "EP-01", "RF-012", "Alta", "M", "Asignar usuario a empresa"],
        ["HU-009", "EP-01", "RF-013", "Alta", "S", "Aislamiento multi-tenant (IDOR protection)"],
        ["HU-010", "EP-02", "RF-020", "Alta", "L", "Crear RAT con wizard 4 pasos"],
        ["HU-011", "EP-02", "RF-022", "Alta", "M", "Marcar RAT con datos sensibles"],
        ["HU-012", "EP-02", "RF-024", "Alta", "M", "Seleccionar base legal"],
        ["HU-013", "EP-02", "RF-025", "Media", "M", "Test de interés legítimo (3 pasos)"],
        ["HU-014", "EP-02", "RF-026", "Alta", "L", "Adjuntar documento de base legal"],
        ["HU-015", "EP-02", "RF-028", "Alta", "M", "Ver nivel de riesgo calculado"],
        ["HU-016", "EP-02", "RF-029", "Alta", "M", "Cambiar estado del RAT"],
        ["HU-017", "EP-02", "RF-030", "Media", "S", "Duplicar RAT"],
        ["HU-018", "EP-02", "RF-034", "Alta", "S", "Aprobar RAT"],
        ["HU-019", "EP-02", "RF-033", "Media", "S", "Registrar revisión periódica"],
        ["HU-020", "EP-04", "RF-050", "Alta", "L", "Registrar brecha de seguridad"],
        ["HU-021", "EP-04", "RF-051", "Alta", "M", "Alertar plazo APDC 72h"],
        ["HU-022", "EP-05", "RF-060", "Alta", "L", "Presentar formulario ARCO público"],
        ["HU-023", "EP-05", "RF-062", "Alta", "M", "Crear solicitud ARCO con token"],
        ["HU-024", "EP-05", "RF-064", "Alta", "M", "Responder solicitud ARCO"],
        ["HU-025", "EP-05", "RF-063", "Alta", "L", "Gestionar ticket TKT"],
        ["HU-026", "EP-06", "RF-074", "Alta", "L", "Filtrar y ordenar reportes"],
        ["HU-027", "EP-06", "RF-070", "Alta", "M", "Exportar RATs a CSV (sanitizado)"],
        ["HU-028", "EP-06", "RF-071", "Alta", "L", "Exportar RATs a PDF"],
        ["HU-029", "EP-06", "RF-072", "Alta", "M", "Exportar RAT individual a PDF"],
        ["HU-030", "EP-06", "RF-075", "Alta", "L", "Ver dashboard de cumplimiento"],
        ["HU-031", "EP-06", "RF-073", "Media", "M", "Exportar RAT en formato CNI"],
        ["HU-032", "EP-07", "RF-041", "Alta", "M", "Aplicar sugerencia al crear RAT"],
        ["HU-033", "EP-07", "RF-042", "Baja", "L", "Gestionar rubros y sugerencias"],
        ["HU-034", "EP-08", "RF-081", "Alta", "M", "Consultar auditoría con hash chain"],
        ["HU-035", "EP-08", "RF-082", "Media", "M", "Auditoría global por empresa"],
        ["HU-036", "EP-09", "RF-090", "Baja", "M", "Chat IA sobre Ley 21.719"],
        ["HU-037", "EP-03", "RF-027", "Alta", "S", "Ver completitud del RAT"],
        ["HU-038", "EP-03", "RF-023", "Alta", "M", "Marcar RAT con EIPD"],
        ["HU-039", "EP-01", "RF-006", "Alta", "S", "Auto-seed del superadmin inicial"],
        ["HU-040", "EP-03", "RF-031", "Alta", "S", "Eliminar RAT con confirmación"],
        ["HU-041", "EP-03", "RF-095", "Alta", "M", "Registrar consentimiento expreso"],
        ["HU-042", "EP-03", "RF-096", "Alta", "S", "Registrar IP de origen del consentimiento"],
        ["HU-043", "EP-03", "RF-097", "Alta", "S", "Revocar consentimiento"],
        ["HU-044", "EP-03", "RF-098", "Alta", "M", "Vincular consentimiento a RAT"],
        ["HU-045", "EP-05", "RF-099", "Alta", "M", "Crear ticket ARCO manualmente"],
        ["HU-046", "EP-05", "RF-100", "Alta", "S", "Gestionar estado del ticket"],
        ["HU-047", "EP-05", "RF-101", "Alta", "S", "Definir prioridad del ticket"],
        ["HU-048", "EP-05", "RF-102", "Alta", "S", "Registrar origen del ticket"],
        ["HU-049", "EP-05", "RF-103", "Alta", "M", "Agregar notas internas al ticket"],
        ["HU-050", "EP-05", "RF-104", "Alta", "M", "Ver historial de cambios del ticket"],
        ["HU-051", "EP-05", "RF-105", "Alta", "S", "Calcular fecha de vencimiento SLA"],
        ["HU-052", "EP-10", "RF-110", "Alta", "M", "Gestionar feriados nacionales (CRUD)"],
        ["HU-053", "EP-10", "RF-111", "Alta", "M", "Subir feriados en bulk por CSV"],
        ["HU-054", "EP-10", "RF-112", "Alta", "S", "Exportar feriados a CSV"],
        ["HU-055", "EP-10", "RF-113", "Alta", "S", "Verificar días hábiles en cálculo SLA"],
        ["HU-056", "EP-02", "RF-114", "Alta", "S", "_admin_empresa crea RAT SOLO en sus empresas_"],
        ["HU-057", "EP-04", "RF-115", "Alta", "S", "_usuario NO puede crear brechas de seguridad_"],
        ["HU-058", "EP-01", "RF-116", "Media", "S", "_Ver estado del sistema con /health_"],
        ["HU-059", "EP-03", "RF-117", "Alta", "M", "_Crear EIPD asociado a un RAT_"],
        ["HU-060", "EP-03", "RF-118", "Alta", "M", "_Actualizar EIPD con workflow_"],
        ["HU-061", "EP-12", "RF-117/RF-119", "Alta", "M", "_Descargar documento de base legal con fallback OCI_"],
        ["HU-062", "EP-09", "RF-118", "Alta", "M", "_Indexar corpus del asesor IA_"],
        ["HU-063", "EP-09", "RF-118", "Alta", "S", "_Ver stats y eliminar chunks del asesor IA_"],
    ]
    add_styled_table(doc, ["HU", "Épica", "Trazabilidad", "Prioridad", "Tamaño", "Título"],
                     hus, col_widths_cm=[1.3, 1.3, 1.6, 1.4, 1.2, 10.7], first_col_bold=True,
                     underline_new=True)

    doc.add_heading("4. Especificación detallada de historias críticas", level=1)

    def hu(hu_id, title, epica, rf, rol, want, for_benefit, criterios, prioridad, tamano):
        doc.add_heading(f"{hu_id} — {title}", level=2)
        add_kv_table(doc, [
            ("ID", hu_id),
            ("Épica", epica),
            ("Trazabilidad RF", rf),
            ("Prioridad", prioridad),
            ("Tamaño", tamano),
        ])
        add_paragraph(doc, "Formato Como/Quiero/Para:", bold=True)
        add_paragraph(doc, f"Como {rol}, quiero {want} para {for_benefit}.")
        add_paragraph(doc, "Criterios de aceptación:", bold=True)
        for c in criterios:
            add_bullet(doc, c)

    hu("HU-001", "Login seguro", "EP-01", "RF-001",
       "usuario autenticado del sistema",
       "iniciar sesión con mi username y contraseña",
       "acceder al dashboard y a las funciones de mi rol",
       [
           "El sistema valida credenciales con bcrypt y emite JWT 8h.",
           "El sistema setea cookie httpOnly 'custodio_token'.",
           "_El sistema consulta el token blacklist antes de validar el JWT._",
           "Rate limit 5/min por IP.",
       ], "Alta", "M (3)")

    hu("HU-061", "_Descargar documento de base legal con fallback OCI_", "EP-12", "RF-117/RF-119",
       "admin_empresa o superadmin",
       "_descargar el documento de base legal de un RAT de forma segura, con fallback automático_",
       "_garantizar disponibilidad del documento incluso si OCI no está disponible_",
       [
           "_El sistema intenta generar PAR (pre-signed URL) para descarga directa desde OCI._",
           "_Si PAR falla, el sistema usa signed GET directo contra OCI Object Storage._",
           "_Si OCI falla, el sistema retorna los bytes almacenados en BYTEA (PostgreSQL)._",
           "_La descarga se registra en el log de auditoría._",
       ], "Alta", "M (3)")

    hu("HU-062", "_Indexar corpus del asesor IA_", "EP-09", "RF-118",
       "superadmin",
       "_indexar nuevos documentos en el corpus del asesor IA_",
       "_mantener las sugerencias del chat IA actualizadas con la normativa vigente_",
       [
           "_El superadmin selecciona archivos o directorios para indexar._",
           "_El sistema chunkifica el contenido y lo almacena en asesor_chunks._",
           "_El sistema retorna estadísticas: chunks indexados, omitidos, errores._",
       ], "Alta", "M (3)")

    hu("HU-063", "_Ver stats y eliminar chunks del asesor IA_", "EP-09", "RF-118",
       "superadmin",
       "_consultar estadísticas del corpus y eliminar chunks específicos_",
       "_mantener la calidad del corpus eliminando contenido irrelevante o duplicado_",
       [
           "_GET /admin/asesor/stats retorna: total chunks, fuentes, tamaño promedio._",
           "_DELETE /admin/asesor/documents/{chunk_id} elimina un chunk específico._",
           "_Las operaciones se registran en el log de auditoría._",
       ], "Alta", "S (2)")

    add_open_questions(doc, [
        "¿Se debe implementar autoguardo en wizard RAT?",
        "¿Se estiman HU con Planning Poker en sesiones de refinement?",
    ])
    add_risks_appendix(doc, [
        ("R-HU-01", "Pendientes S14 (CSRF) y C1 (encryption) bloquean compliance total.", "Alto"),
    ])
    add_id_glossary(doc, [
        ("HU-###", "Historia de Usuario", "Necesidad del usuario en formato 'Como/Quiero/Para'."),
        ("EP-###", "Épica", "Conjunto de HU relacionadas."),
        ("M (3)", "Tamaño medio", "3 puntos de historia: ~1-2 días."),
        ("L (5)", "Tamaño grande", "5 puntos de historia: ~3-5 días."),
        ("S (2)", "Tamaño pequeño", "2 puntos de historia: ~1 día."),
    ])
    add_final_note(doc)
    doc.save(OUT_FILE)
    print(f"[OK] {OUT_FILE}")


if __name__ == "__main__":
    build()