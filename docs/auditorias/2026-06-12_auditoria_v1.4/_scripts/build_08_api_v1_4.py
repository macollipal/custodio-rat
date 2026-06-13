"""
Build 08 — Documentación de APIs v1.4 (Post-OCI Integration)
Genera: docs/documentacion_oficial/08_API_Custodio_RAT_Manager_v1.4.docx
Cambios v1.4:
- Nuevo endpoint GET /rats/{id}/archivo con fallback chain OCI
- Nuevos endpoints /admin/asesor/* (index, stats, delete chunk)
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
OUT_FILE = os.path.join(OUT_DIR, "08_API_Custodio_RAT_Manager_v1.4.docx")
DOC_CODE = "CUST-DOC-08"
DOC_TITLE = "Documentación de APIs"
DOC_DATE = "Junio 2026"


def build():
    doc = new_document()
    add_header_footer(doc, DOC_TITLE)
    add_cover(doc, title="DOCUMENTACIÓN DE APIs",
              subtitle="Catálogo completo de endpoints REST · FastAPI + JWT",
              code=DOC_CODE)
    add_version_control(doc, DOC_CODE, DOC_TITLE, changes=[
        ("1.0", "Junio 2026", "Catálogo inicial de endpoints, derivado de app/routes/*."),
        ("1.1", "Junio 2026", "Agregado módulo AI (/ai/ask), RATs sugeridos y Tickets ARCO."),
        ("1.2", "Junio 2026", "_Módulo Feriados (6 endpoints), P0 security fixes (token blacklist, IDOR, CSV sanitize, hash chain)._"),
        ("1.3", "Junio 2026", "_Beta Launch: nuevo endpoint /health, RBAC fixes DT-014/DT-015, routers consentimientos/eipd corregidos._"),
        ("1.4", "Junio 2026", "_Post-OCI: GET /rats/{id}/archivo con fallback chain, /admin/asesor/* para gestión del corpus IA._"),
    ])
    add_toc(doc)
    fig_counter = [0]
    tab_counter = [0]

    doc.add_heading("1. Introducción", level=1)
    add_paragraph(doc, "Este documento cataloga todos los endpoints REST de " + BRAND_FULL + ".")
    add_paragraph(doc, "Backend: FastAPI 0.115 + Uvicorn ASGI + Neon PostgreSQL. "
                      "Autenticación: JWT Bearer token. Base de datos: PostgreSQL 15+.")

    doc.add_heading("2. Autenticación", level=1)
    add_paragraph(doc, "Todos los endpoints requieren JWT Bearer token en header Authorization. "
                      "Excepciones: /auth/login, /auth/refresh, /health, /docs, /redoc. Cookies httpOnly para sesión web.")
    add_paragraph(doc, "_El sistema consulta la token blacklist en get_current_user antes de validar el JWT. "
                      "Los tokens revocados (logout o fuerza bruta) retornan 401._")

    doc.add_heading("3. Endpoints de sistema", level=1)
    add_paragraph(doc, "_Endpoints de sistema (v1.3+):_")
    sistema_endpoints = [
        ["GET", "/health", "health", "_Simple health check. Retorna {\"status\": \"ok\"}. Sin autenticación._"],
        ["GET", "/health/db", "health_db", "Health check con conectividad a base de datos PostgreSQL. Retorna latency_ms."],
    ]
    add_styled_table(doc, ["Método", "Ruta", "Función", "Descripción"],
                     sistema_endpoints, col_widths_cm=[2.0, 3.5, 3.5, 7.5],
                     first_col_bold=True, underline_new=True)

    doc.add_heading("4. Módulo Feriados", level=1)
    add_paragraph(doc, "Gestión de feriados nacionales chilenos (usados en cálculo de días hábiles para Tickets ARCO). "
                      "Requiere rol superadmin.")
    feriados_endpoints = [
        ["GET", "/admin/feriados/", "list_feriados", "Lista feriados por año. Query: anio (int, opcional)"],
        ["GET", "/admin/feriados/years", "list_anios", "Lista años con feriados disponibles."],
        ["POST", "/admin/feriados/upload", "upload_feriados", "Upload bulk CSV UTF-8 BOM."],
        ["GET", "/admin/feriados/example", "download_example", "Descarga CSV ejemplo para upload."],
        ["DELETE", "/admin/feriados/{anio}", "eliminar_feriados", "Elimina todos los feriados de un año."],
    ]
    add_styled_table(doc, ["Método", "Ruta", "Función", "Descripción"],
                     feriados_endpoints, col_widths_cm=[2.0, 4.5, 4.0, 6.0],
                     first_col_bold=True)

    doc.add_heading("5. Módulo Auth", level=1)
    add_paragraph(doc, "Autenticación y gestión de usuarios. Rate limits: login 5/min, refresh 30/min, logout 10/min.")
    auth_endpoints = [
        ["POST", "/auth/login", "login", "Login con username/password. Retorna access_token + refresh_token + user."],
        ["POST", "/auth/refresh", "refresh_token", "Renovar access token con refresh token. Rotation habilitada."],
        ["POST", "/auth/logout", "logout", "Revoca token agregándolo a blacklist LRU."],
        ["GET", "/auth/me", "me", "Usuario actual. Consulta blacklist."],
        ["POST", "/auth/users", "crear_usuario", "_Crear usuario. Solo superadmin._"],
        ["GET", "/auth/users", "listar_usuarios", "_Listar usuarios. Solo superadmin._"],
        ["PUT", "/auth/users/{user_id}", "actualizar_usuario", "_Editar usuario. Solo superadmin._"],
        ["DELETE", "/auth/users/{user_id}", "eliminar_usuario", "_Eliminar usuario. Solo superadmin._"],
        ["PUT", "/auth/users/{user_id}/password", "cambiar_password_otro", "_Cambiar password de otro usuario. Solo superadmin._"],
        ["PUT", "/auth/me/password", "cambiar_password", "Cambiar password propio. Rate limit 5/min."],
    ]
    add_styled_table(doc, ["Método", "Ruta", "Función", "Descripción"],
                     auth_endpoints, col_widths_cm=[2.0, 4.5, 4.0, 6.0],
                     first_col_bold=True)

    doc.add_heading("6. Módulo Companies", level=1)
    companies_endpoints = [
        ["GET", "/companies/publico", "listar_publico", "_Acceso público (sin auth) para política de transparencia._"],
        ["GET", "/companies/", "listar", "Lista empresas (superadmin ve todas)."],
        ["GET", "/companies/{company_id}", "obtener", "_IDOR protection: verifica acceso a empresa._"],
        ["POST", "/companies/", "crear", "_Crear empresa. Solo superadmin._"],
        ["PUT", "/companies/{company_id}", "actualizar", "_IDOR protection en update._"],
        ["DELETE", "/companies/{company_id}", "eliminar", "_IDOR protection + solo superadmin._"],
    ]
    add_styled_table(doc, ["Método", "Ruta", "Función", "Descripción"],
                     companies_endpoints, col_widths_cm=[2.0, 4.5, 4.0, 6.0],
                     first_col_bold=True)

    doc.add_heading("7. Módulo RATs", level=1)
    add_paragraph(doc, "CRUD de Registros de Actividades de Tratamiento (Art. 16 Ley 21.719). "
                      "RBAC: admin_empresa solo puede crear RATs en sus propias empresas (DT-014 corregido).")
    rat_endpoints = [
        ["GET", "/rats/", "listar", "Lista RATs filtrados por acceso de empresa."],
        ["GET", "/rats/reportes", "reportes", "Reporte filtrado con paginación y filtros avanzados."],
        ["GET", "/rats/dashboard/{company_id}", "dashboard", "KPIs del dashboard de una empresa."],
        ["GET", "/rats/sugerencias/tipos", "tipos_proceso", "Lista tipos de proceso para sugerencias."],
        ["POST", "/rats/sugerencias", "sugerencias", "Sugerencias precompletadas para un tipo de proceso."],
        ["GET", "/rats/{rat_id}", "obtener", "Detalle de un RAT."],
        ["POST", "/rats/", "crear", "_RBAC: admin_empresa limitado a sus empresas (DT-014)._"],
        ["PUT", "/rats/{rat_id}", "actualizar", "Actualizar RAT."],
        ["DELETE", "/rats/{rat_id}", "eliminar", "Eliminar RAT."],
        ["POST", "/rats/{rat_id}/consentimientos", "crear_consentimiento", "Registrar consentimiento expreso (Art. 16)."],
        ["POST", "/rats/{rat_id}/revision", "registrar_revision", "Marcar RAT como revisado periódicamente."],
        ["POST", "/rats/{rat_id}/aprobar", "approve_rat", "_Aprobar RAT (admin_empresa o superadmin)._"],
        ["GET", "/rats/{rat_id}/archivo", "descargar_archivo", "_Descarga con fallback chain: PAR → signed GET → BYTEA._"],
        ["GET", "/rats/{rat_id}/auditoria", "auditoria", "Historial de auditoría del RAT."],
        ["GET", "/rats/auditoria/{company_id}", "auditoria_global", "Auditoría global de empresa."],
        ["GET", "/rats/auditoria/verify-chain", "verificar_cadena_auditoria", "_Verifica hash chain completo. Retorna {valid, broken_at}._"],
        ["GET", "/rats/export/csv", "exportar_a_csv", "_CSV sanitizado contra inyección de fórmulas._"],
        ["GET", "/rats/export/pdf", "exportar_a_pdf", "PDF con ReportLab."],
        ["GET", "/rats/{rat_id}/export/pdf", "exportar_rat_individual_pdf", "PDF individual de un RAT."],
        ["GET", "/rats/export/cni", "exportar_cni", "Formato CNI para APDC (Ley 21.719)."],
    ]
    add_styled_table(doc, ["Método", "Ruta", "Función", "Descripción"],
                     rat_endpoints, col_widths_cm=[2.0, 5.0, 4.0, 5.5],
                     first_col_bold=True)

    doc.add_heading("8. Módulo Brechas", level=1)
    add_paragraph(doc, "_Gestión de brechas de seguridad (Art. 14 bis). RBAC: rol usuario NO puede crear brechas (DT-015 corregido)._")
    brechas_endpoints = [
        ["GET", "/brechas/", "listar", "Lista brechas de la empresa."],
        ["GET", "/brechas/{breach_id}", "obtener", "Detalle de una brecha."],
        ["POST", "/brechas/", "crear", "_Bloqueado para rol usuario (DT-015)._"],
        ["PUT", "/brechas/{breach_id}", "actualizar", "Actualizar brecha."],
        ["POST", "/brechas/{breach_id}/evaluar-riesgo", "evaluar_riesgo", "Evalúa riesgo razonable (Art. 14 bis)."],
        ["DELETE", "/brechas/{breach_id}", "eliminar", "Eliminar brecha."],
    ]
    add_styled_table(doc, ["Método", "Ruta", "Función", "Descripción"],
                     brechas_endpoints, col_widths_cm=[2.0, 5.0, 4.0, 5.5],
                     first_col_bold=True, underline_new=True)

    doc.add_heading("9. Módulo Consentimientos", level=1)
    add_paragraph(doc, "_Gestión de consentimientos expresos (Art. 12 Ley 21.719). "
                      "El router estaba roto en v1.2 (_get_user sin request). Corregido en v1.3._")
    consent_endpoints = [
        ["GET", "/consentimientos/", "listar_consentimientos", "Lista consentimientos con filtros por RAT y estado."],
        ["GET", "/consentimientos/{consentimiento_id}", "obtener_consentimiento", "Detalle de un consentimiento."],
        ["POST", "/consentimientos/", "crear_consentimiento", "Crear consentimiento."],
        ["POST", "/consentimientos/{consentimiento_id}/revocar", "revocar_consentimiento", "_Revocar consentimiento (Art. 12)._"],
    ]
    add_styled_table(doc, ["Método", "Ruta", "Función", "Descripción"],
                     consent_endpoints, col_widths_cm=[2.0, 5.0, 4.0, 5.5],
                     first_col_bold=True, underline_new=True)

    doc.add_heading("10. Módulo EIPD", level=1)
    add_paragraph(doc, "_Evaluaciones de Impacto en Protección de Datos (Art. 15 bis). "
                      "El router estaba roto en v1.2 (_get_user sin request). Corregido en v1.3._")
    eipd_endpoints = [
        ["GET", "/eipd/", "listar_eipds", "Lista EIPDs de la empresa."],
        ["GET", "/eipd/rat/{rat_id}", "obtener_eipd_por_rat", "EIPD asociado a un RAT específico."],
        ["POST", "/eipd/", "crear_eipd", "Crear EIPD (1:1 con RAT)."],
        ["PUT", "/eipd/{eipd_id}", "actualizar_eipd", "Actualizar EIPD (workflow)."],
    ]
    add_styled_table(doc, ["Método", "Ruta", "Función", "Descripción"],
                     eipd_endpoints, col_widths_cm=[2.0, 4.5, 4.0, 6.0],
                     first_col_bold=True, underline_new=True)

    doc.add_heading("11. Módulo Admin Asesor IA", level=1)
    add_paragraph(doc, "_Gestión del corpus del asesor IA (solo superadmin). Indexación, estadísticas y eliminación de chunks._")
    asesor_endpoints = [
        ["POST", "/admin/asesor/index", "index_endpoint", "_Indexa archivos en el corpus del asesor IA. Params: paths, force._"],
        ["GET", "/admin/asesor/stats", "stats_endpoint", "_Retorna estadísticas del corpus: total chunks, fuentes, tamaño._"],
        ["DELETE", "/admin/asesor/documents/{chunk_id}", "delete_chunk_endpoint", "_Elimina un chunk específico del índice._"],
    ]
    add_styled_table(doc, ["Método", "Ruta", "Función", "Descripción"],
                     asesor_endpoints, col_widths_cm=[2.0, 5.0, 4.0, 5.5],
                     first_col_bold=True, underline_new=True)

    doc.add_heading("12. Módulo Tickets ARCO", level=1)
    tkt_endpoints = [
        ["GET", "/tkt-solicitud-derecho/dashboard", "dashboard", "Dashboard con métricas y alertas SLA."],
        ["POST", "/tkt-solicitud-derecho/", "crear_ticket_endpoint", "Crear ticket (usuario bloqueado)."],
        ["GET", "/tkt-solicitud-derecho/", "listar_tickets", "Lista tickets con filtros."],
        ["GET", "/tkt-solicitud-derecho/{ticket_id}", "obtener_ticket", "Detalle ticket."],
        ["PATCH", "/tkt-solicitud-derecho/{ticket_id}", "actualizar_ticket", "Actualizar estado/prioridad/etc."],
        ["POST", "/tkt-solicitud-derecho/{ticket_id}/notas", "agregar_nota", "Agregar nota interna."],
        ["GET", "/tkt-solicitud-derecho/{ticket_id}/notas", "listar_notas", "Listar notas."],
        ["GET", "/tkt-solicitud-derecho/{ticket_id}/historial", "listar_historial", "Historial de cambios."],
    ]
    add_styled_table(doc, ["Método", "Ruta", "Función", "Descripción"],
                     tkt_endpoints, col_widths_cm=[2.0, 5.5, 4.0, 5.0],
                     first_col_bold=True)

    doc.add_heading("13. Módulos adicionales", level=2)
    add_paragraph(doc, "Encargados de contrato, solicitudes de derecho, transparencia, IA, rubros, tareas.")
    otros_endpoints = [
        ["Encargados", "GET/POST/PUT/DELETE", "/encargados-contrato/", "CRUD contratos de encargado (Art. 14 quater)."],
        ["Solicitudes", "GET/POST/PATCH", "/solicitudes-derecho/", "Solicitudes ARCO públicas y gestión interna."],
        ["Transparencia", "GET", "/publico/transparencia/{company_id}", "_Política de transparencia pública (Art. 14 ter). Sin auth._"],
        ["AI", "POST", "/ai/ask", "Chat IA con contexto de RATs. Rate limit 10/min."],
        ["Rubros", "GET/POST/PUT/DELETE", "/rubros", "Gestión de rubros y RATs sugeridos."],
        ["Tareas", "GET/POST", "/admin/tasks/", "Cola de tareas asíncronas (scheduler)."],
    ]
    add_styled_table(doc, ["Módulo", "Métodos", "Prefijo", "Descripción"],
                     otros_endpoints, col_widths_cm=[3.0, 3.0, 5.0, 5.5],
                     first_col_bold=True)

    doc.add_heading("14. Códigos de error comunes", level=1)
    err_codes = [
        ["200", "OK", "Operación exitosa."],
        ["201", "Created", "Recurso creado."],
        ["204", "No Content", "Operación exitosa sin cuerpo."],
        ["400", "Bad Request", "Datos inválidos (validación Pydantic)."],
        ["401", "Unauthorized", "Token ausente, inválido o revocado (blacklist)."],
        ["403", "Forbidden", "_Acceso denegado: empresa ajena o rol insuficiente (DT-014, DT-015)._"],
        ["404", "Not Found", "Recurso no encontrado."],
        ["422", "Unprocessable Entity", "Entidad no procesable (validación fallida)."],
        ["429", "Too Many Requests", "Rate limit excedido."],
        ["500", "Internal Server Error", "Error inesperado del servidor."],
    ]
    add_styled_table(doc, ["Código", "Nombre", "Descripción"], err_codes,
                     col_widths_cm=[2.0, 4.0, 11.5], first_col_bold=True)

    doc.add_heading("15. Medidas de seguridad implementadas", level=1)
    add_paragraph(doc, "_Todas las medidas de seguridad identificadas en auditoría v1.2 fueron corregidas en v1.3 beta launch:_")
    seguridad = [
        ["Token blacklist (LRU 1000)", "_Implementado en get_current_user (commit 96167b5). JTI consultado en cada request._"],
        ["IDOR protection", "_check_company_access en todas las rutas con company_id. /companies/publico requiere auth._"],
        ["CSV sanitization", "_Prefijo apostrophe (') en campos que empiecen con =, +, -, @ (commit 96167b5)._"],
        ["Rate limiting", "_5/min /auth/login, 5/min cambio password, 3/hora ARCO, 10/min logout, 10/min AI._"],
        ["PII masking en logs", "_PIIMaskingFilter en logging_config.py: mask email, RUT, IP, tokens, passwords._"],
        ["Hash chain en auditoría", "_prev_hash + SHA256 para cada audit_log. verify_audit_chain() valida integridad._"],
        ["RBAC: admin_empresa RAT", "_DT-014: admin_empresa solo crea RATs en empresas que gestiona (6209e2d)._"],
        ["RBAC: usuario breach", "_DT-015: rol usuario no puede crear brechas de seguridad (6209e2d)._"],
        ["Router fixes", "__get_user() wrapper corregido en consentimientos y eipd (commits 6980187, 43287c0)._"],
    ]
    add_styled_table(doc, ["Medida", "Descripción"], seguridad,
                     col_widths_cm=[4.5, 13.0], first_col_bold=True,
                     underline_new=True)

    doc.add_heading("16. OCI Object Storage — Fallback Chain", level=1)
    add_paragraph(doc, "_El endpoint GET /rats/{rat_id}/archivo implementa una cadena de fallback para garantizar disponibilidad:_")
    oci_fallback = [
        ["Paso 1", "PAR (Pre-Authenticated Request)", "_Intenta generar URL pre-firmada desde OCI Object Storage. Si IAM no tiene permisos PAR, continúa al paso 2._"],
        ["Paso 2", "Signed GET directo", "_Descarga directo desde OCI usando firma RSA de la API key. Requiere permiso 'manage objects'._"],
        ["Paso 3", "BYTEA fallback", "_Si OCI falla completamente, retorna datos binarios almacenados en PostgreSQL (campo archivo_base_legal_datos)._"],
    ]
    add_styled_table(doc, ["Paso", "Método", "Descripción"], oci_fallback,
                     col_widths_cm=[1.5, 4.5, 11.5], first_col_bold=True,
                     underline_new=True)

    add_risks_appendix(doc, [
        ("R-API-09", "Hash chain no cubre registros históricos previos a v1.2. "
                     "Script SQL migration_audit_hash_chain.sql disponible.", "Medio"),
        ("R-API-10", "_PAR IAM permission no disponible (manage pre-authenticated-requests). Fallback a signed GET funciona con 'manage objects'._", "Bajo"),
    ])

    doc.save(OUT_FILE)
    print(f"[OK] {OUT_FILE}")


if __name__ == "__main__":
    build()