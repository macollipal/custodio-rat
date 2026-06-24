"""
Build 08 — API REST v1.7 (Gap G1: estaba en v1.4, nunca regenerado en v1.5 ni v1.6)
Genera: docs/documentacion_oficial/08_API_REST_Custodio_RAT_Manager_v1.7.docx
Cambios v1.7:
- Gap G1 cerrado: doc 08 ahora en v1.7 (estaba en v1.4 desde Jun-12)
- Sprint 2: 4 endpoints nuevos /export/tkt/{csv,excel,pdf}, /admin/tasks/enqueue-sla-alerts
- 60+ endpoints documentados con método, path, auth, RBAC, params, response, tags
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
OUT_FILE = os.path.join(OUT_DIR, "08_API_REST_Custodio_RAT_Manager_v1.7.docx")
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
        ("1.7", "Junio 2026", "_Gap G1 cerrado: doc 08 ahora en v1.7. Sprint 2: 4 endpoints nuevos (export_tkt, enqueue-sla-alerts)._"),
    ])
    add_toc(doc)

    doc.add_heading("1. Introducción", level=1)
    add_paragraph(doc,
        f"La API REST de {BRAND_FULL} sigue el estándar OpenAPI 3.0 y está "
        "implementada con FastAPI. Base URL: /api/v1. Todos los endpoints "
        "requieren autenticación JWT Bearer excepto los endpoints públicos "
        "documentados explícitamente.")
    add_paragraph(doc,
        "La API usa cookies httpOnly para el token de acceso (8h). "
        "CSRF protection habilitada con CSRFMiddleware. "
        "Rate limiting por IP y por usuario según el endpoint.")

    doc.add_heading("2. Autenticación y Autorización", level=1)
    auth_table = [
        ["JWT Bearer", "Cookie httpOnly", "8 horas", "HS256"],
        ["Refresh Token", "Cookie httpOnly", "7 días", "HS256"],
        ["CSRF Token", "Header X-CSRF-Token", "Por sesión", "samesite=lax"],
        ["Token Blacklist", "LRU Cache 1000", "Hasta expiración", "Revocación"],
    ]
    add_styled_table(doc, ["Tipo", "Storage", "TTL", "Algoritmo"],
                     auth_table, col_widths_cm=[3.5, 3.5, 3.0, 3.0], first_col_bold=True)

    doc.add_heading("3. Endpoints por Módulo", level=1)

    doc.add_heading("3.1 Módulo de Autenticación (/api/v1/auth)", level=2)
    add_endpoint_table(doc, "Auth", [
        ["POST", "/login", "No", "Público", "email, password", "Token + cookie", "auth"],
        ["POST", "/refresh", "Sí", "Usuario", "refresh_token (cookie)", "Token", "auth"],
        ["POST", "/logout", "Sí", "Usuario", "—", "MessageResponse", "auth"],
        ["GET", "/me", "Sí", "Usuario", "—", "UserOut", "auth"],
        ["POST", "/users", "Sí", "superadmin", "email, password, nombre, rol, empresa_ids", "UserOut", "auth"],
        ["PUT", "/users/{user_id}", "Sí", "superadmin", "user_id, campos", "UserOut", "auth"],
        ["DELETE", "/users/{user_id}", "Sí", "superadmin", "user_id", "MessageResponse", "auth"],
        ["PUT", "/users/{user_id}/password", "Sí", "superadmin", "user_id, new_password", "MessageResponse", "auth"],
        ["PUT", "/me/password", "Sí", "Usuario", "current_password, new_password", "UserOut", "auth"],
        ["GET", "/users", "Sí", "admin_empresa", "skip, limit, empresa_id", "UserListResponse", "auth"],
    ])

    doc.add_heading("3.2 Módulo de Empresas (/api/v1/companies)", level=2)
    add_endpoint_table(doc, "Companies", [
        ["GET", "/publico", "Sí", "Usuario", "—", "list[CompanyPublicOut]", "companies"],
        ["GET", "/", "Sí", "admin_empresa", "skip, limit", "CompanyListResponse", "companies"],
        ["GET", "/{company_id}", "Sí", "admin_empresa", "company_id", "CompanyOut", "companies"],
        ["POST", "/", "Sí", "superadmin", "rut, razon_social, giro, etc.", "CompanyOut", "companies"],
        ["PUT", "/{company_id}", "Sí", "superadmin", "company_id, campos", "CompanyOut", "companies"],
        ["DELETE", "/{company_id}", "Sí", "superadmin", "company_id + password", "MessageResponse", "companies"],
        ["PATCH", "/{company_id}/desactivar", "Sí", "superadmin", "company_id", "CompanyOut", "companies"],
        ["PATCH", "/{company_id}/reactivar", "Sí", "superadmin", "company_id", "CompanyOut", "companies"],
        ["POST", "/{company_id}/hard-delete", "Sí", "superadmin", "company_id + password", "MessageResponse", "companies"],
    ])

    doc.add_heading("3.3 Módulo RAT (/api/v1/rats)", level=2)
    add_endpoint_table(doc, "RATs", [
        ["GET", "/", "Sí", "admin_empresa", "skip, limit, estado, riesgos", "list[RATOut]", "rats"],
        ["GET", "/{rat_id}", "Sí", "admin_empresa", "rat_id", "RATOut", "rats"],
        ["POST", "/", "Sí", "admin_empresa", "campos RAT", "RATOut", "rats"],
        ["PUT", "/{rat_id}", "Sí", "admin_empresa", "rat_id, campos", "RATOut", "rats"],
        ["DELETE", "/{rat_id}", "Sí", "admin_empresa", "rat_id", "MessageResponse", "rats"],
        ["POST", "/{rat_id}/aprobar", "Sí", "admin_empresa", "rat_id", "RATOut", "rats"],
        ["POST", "/{rat_id}/revision", "Sí", "admin_empresa", "rat_id", "AuditLogOut", "rats"],
        ["GET", "/{rat_id}/archivo", "Sí", "admin_empresa", "rat_id", "FileResponse", "rats"],
        ["POST", "/{rat_id}/consentimientos", "Sí", "admin_empresa", "rat_id, campos", "ConsentimientoOut", "rats"],
        ["GET", "/{rat_id}/auditoria", "Sí", "admin_empresa", "rat_id", "list[AuditLogOut]", "rats"],
        ["GET", "/dashboard/{company_id}", "Sí", "admin_empresa", "company_id", "ReportesResponse", "rats"],
        ["GET", "/sugerencias/tipos", "Sí", "admin_empresa", "—", "list[str]", "rats"],
        ["POST", "/sugerencias", "Sí", "admin_empresa", "tipo_proceso", "RATSugerenciaOut", "rats"],
        ["GET", "/export/csv", "Sí", "admin_empresa", "filtros", "FileResponse", "rats"],
        ["GET", "/export/pdf", "Sí", "admin_empresa", "filtros", "FileResponse", "rats"],
        ["GET", "/{rat_id}/export/pdf", "Sí", "admin_empresa", "rat_id", "FileResponse", "rats"],
        ["GET", "/export/cni", "Sí", "admin_empresa", "filtros", "FileResponse", "rats"],
        ["GET", "/auditoria/{company_id}", "Sí", "admin_empresa", "company_id", "FileResponse", "rats"],
        ["GET", "/auditoria/verify-chain", "Sí", "superadmin", "—", "VerifyChainResponse", "rats"],
    ])

    doc.add_heading("3.4 Módulo EIPD (/api/v1/eipds)", level=2)
    add_endpoint_table(doc, "EIPDs", [
        ["GET", "/", "Sí", "admin_empresa", "skip, limit, rat_id", "EIPDListResponse", "eipd"],
        ["GET", "/rat/{rat_id}", "Sí", "admin_empresa", "rat_id", "EIPDOut", "eipd"],
        ["POST", "/", "Sí", "admin_empresa", "rat_id, evaluacion, medidas", "EIPDOut", "eipd"],
        ["PUT", "/{eipd_id}", "Sí", "admin_empresa", "eipd_id, campos", "EIPDOut", "eipd"],
    ])

    doc.add_heading("3.5 Módulo Brechas (/api/v1/breaches)", level=2)
    add_endpoint_table(doc, "Brechas", [
        ["GET", "/", "Sí", "admin_empresa", "skip, limit, company_id", "BreachListResponse", "breaches"],
        ["GET", "/{breach_id}", "Sí", "admin_empresa", "breach_id", "BreachOut", "breaches"],
        ["POST", "/", "Sí", "admin_empresa", "descripcion, fecha, datos_comprometidos, etc.", "BreachOut", "breaches"],
        ["PUT", "/{breach_id}", "Sí", "admin_empresa", "breach_id, campos", "BreachOut", "breaches"],
        ["POST", "/{breach_id}/evaluar-riesgo", "Sí", "admin_empresa", "breach_id", "BreachOut", "breaches"],
        ["DELETE", "/{breach_id}", "Sí", "admin_empresa", "breach_id", "MessageResponse", "breaches"],
    ])

    doc.add_heading("3.6 Módulo Consentimientos (/api/v1/consentimientos)", level=2)
    add_endpoint_table(doc, "Consentimientos", [
        ["GET", "/", "Sí", "admin_empresa", "skip, limit, rat_id", "ConsentimientoListResponse", "consentimientos"],
        ["GET", "/{consentimiento_id}", "Sí", "admin_empresa", "consentimiento_id", "ConsentimientoOut", "consentimientos"],
        ["POST", "/", "Sí", "admin_empresa", "nombre_titular, email, canal, texto_consentimiento", "ConsentimientoOut", "consentimientos"],
        ["POST", "/{consentimiento_id}/revocar", "Sí", "admin_empresa", "consentimiento_id", "ConsentimientoOut", "consentimientos"],
    ])

    doc.add_heading("3.7 Módulo Feriados (/api/v1/feriados)", level=2)
    add_endpoint_table(doc, "Feriados", [
        ["GET", "/", "Sí", "admin_empresa", "anio", "FeriadoListResponse", "feriados"],
        ["GET", "/years", "Sí", "admin_empresa", "—", "FeriadoYearsResponse", "feriados"],
        ["POST", "/upload", "Sí", "superadmin", "CSV file (multipart)", "MessageResponse", "feriados"],
        ["GET", "/example", "Sí", "superadmin", "—", "FileResponse", "feriados"],
        ["DELETE", "/{anio}", "Sí", "superadmin", "anio", "MessageResponse", "feriados"],
    ])

    doc.add_heading("3.8 Módulo Tickets ARCO (/api/v1/solicitudes-derecho)", level=2)
    add_endpoint_table(doc, "Tickets ARCO", [
        ["GET", "/token", "No", "Público", "—", "TokenResponse", "solicitudes"],
        ["POST", "/", "No", "Público", "tipo, nombre, rut, email, descripcion, rut_titular, telefono, pais, fecha_nacimiento, rat_id, representante_nombre, representante_rut", "dict", "solicitudes"],
        ["GET", "/", "Sí", "admin_empresa", "skip, limit, estado, prioridad, origen, fecha_desde, fecha_hasta", "list[SolicitudResponse]", "solicitudes"],
        ["GET", "/{solicitud_id}", "Sí", "admin_empresa", "solicitud_id", "SolicitudResponse", "solicitudes"],
        ["GET", "/{solicitud_id}/historial", "Sí", "admin_empresa", "solicitud_id", "list[HistorialEntry]", "solicitudes"],
        ["PATCH", "/{solicitud_id}/responder", "Sí", "admin_empresa", "solicitud_id, estado, notas", "SolicitudResponse", "solicitudes"],
        ["POST", "/{solicitud_id}/bloquear", "Sí", "admin_empresa", "solicitud_id", "MessageResponse", "solicitudes"],
        ["POST", "/{solicitud_id}/desbloquear", "Sí", "admin_empresa", "solicitud_id", "MessageResponse", "solicitudes"],
        ["GET", "/{solicitud_id}/portabilidad/export", "Sí", "admin_empresa", "solicitud_id", "FileResponse", "solicitudes"],
    ])

    doc.add_heading("3.9 Módulo Tickets ARCO — Admin (/api/v1/admin/tkt-solicitud-derecho)", level=2)
    add_endpoint_table(doc, "Tickets Admin", [
        ["GET", "/", "Sí", "admin_empresa", "skip, limit, estado, prioridad, empresa_id", "TktSolicitudListResponse", "tkt_admin"],
        ["GET", "/{tkt_id}", "Sí", "admin_empresa", "tkt_id", "TktSolicitudDetailResponse", "tkt_admin"],
        ["PATCH", "/{tkt_id}", "Sí", "admin_empresa", "tkt_id, estado, prioridad", "TktSolicitudOut", "tkt_admin"],
        ["POST", "/{tkt_id}/notas", "Sí", "admin_empresa", "tkt_id, contenido", "TktNotaOut", "tkt_admin"],
        ["GET", "/{tkt_id}/notas", "Sí", "admin_empresa", "tkt_id", "list[TktNotaOut]", "tkt_admin"],
    ])

    doc.add_heading("3.10 Sprint 2 — Export Tickets ARCO (/api/v1/export/tkt)", level=2)
    add_endpoint_table(doc, "_Export Tickets ARCO_", [
        ["_GET_", "_/csv_", "_Sí_", "_admin_empresa_",
         "_company_id, estado, prioridad, fecha_desde, fecha_hasta_",
         "_FileResponse (text/csv; charset=utf-8-sig)_", "_export_"],
        ["_GET_", "_/excel_", "_Sí_", "_admin_empresa_",
         "_company_id, estado, prioridad, fecha_desde, fecha_hasta_",
         "_FileResponse (application/vnd.openxmlformats-officedocument.spreadsheetml.sheet)_",
         "_export_"],
        ["_GET_", "_/pdf_", "_Sí_", "_admin_empresa_",
         "_company_id, estado, prioridad, fecha_desde, fecha_hasta_",
         "_FileResponse (application/pdf)_", "_export_"],
    ])

    doc.add_heading("3.11 Sprint 2 — SLA Alert T-2 (/api/v1/admin/tasks)", level=2)
    add_endpoint_table(doc, "_SLA Alert T-2 días_", [
        ["_POST_", "_/enqueue-sla-alerts_", "_Sí_", "_superadmin_",
         "_—_",
         "_TaskEnqueueResponse (tarea SLA_ALERT_T2 encolada)_", "_tasks_"],
    ])

    doc.add_heading("3.12 Módulo Tasks (/api/v1/admin/tasks)", level=2)
    add_endpoint_table(doc, "Tasks", [
        ["GET", "/", "Sí", "superadmin", "skip, limit, tipo, estado", "TaskListResponse", "tasks"],
        ["GET", "/stats", "Sí", "superadmin", "—", "TaskStatsResponse", "tasks"],
        ["POST", "/run", "Sí", "superadmin (cron)", "—", "TaskRunResponse", "tasks"],
        ["POST", "/enqueue", "Sí", "superadmin", "tipo, params", "TaskEnqueueResponse", "tasks"],
    ])

    doc.add_heading("3.13 Módulo AI (/api/v1/ai)", level=2)
    add_endpoint_table(doc, "AI", [
        ["POST", "/ask", "Sí", "Usuario", "pregunta, contexto", "AskResponse", "ai"],
    ])

    doc.add_heading("3.14 Módulo Admin Asesor IA (/api/v1/admin/asesor)", level=2)
    add_endpoint_table(doc, "Admin Asesor", [
        ["POST", "/index", "Sí", "superadmin", "texto, metadata", "AsesorIndexResponse", "admin_asesor"],
        ["GET", "/stats", "Sí", "superadmin", "—", "AsesorStatsResponse", "admin_asesor"],
        ["GET", "/documents", "Sí", "superadmin", "skip, limit", "AsesorDocumentsListResponse", "admin_asesor"],
        ["POST", "/upload", "Sí", "superadmin", "file (PDF/TXT/MD)", "AsesorUploadResponse", "admin_asesor"],
        ["GET", "/documents/{doc_id}/download", "Sí", "superadmin", "doc_id", "FileResponse", "admin_asesor"],
        ["DELETE", "/documents/{doc_id}", "Sí", "superadmin", "doc_id", "AsesorDeleteResponse", "admin_asesor"],
        ["DELETE", "/documents/{doc_id}/chunks/{chunk_id}", "Sí", "superadmin", "doc_id, chunk_id", "MessageResponse", "admin_asesor"],
    ])

    doc.add_heading("3.15 Módulo Rubros (/api/v1/rubros)", level=2)
    add_endpoint_table(doc, "Rubros", [
        ["GET", "", "Sí", "Usuario", "—", "list[RubroOut]", "rubros"],
        ["POST", "", "Sí", "superadmin", "nombre", "RubroOut", "rubros"],
        ["PUT", "/{rubro_id}", "Sí", "superadmin", "rubro_id, nombre", "RubroOut", "rubros"],
        ["DELETE", "/{rubro_id}", "Sí", "superadmin", "rubro_id", "OkResponse", "rubros"],
    ])

    doc.add_heading("3.16 Módulo Seguimiento Público (/api/v1/seguimiento)", level=2)
    add_endpoint_table(doc, "Seguimiento", [
        ["GET", "/{tracking_token}", "No", "Público", "tracking_token", "SeguimientoResponse", "seguimiento"],
    ])

    doc.add_heading("3.17 Módulo Encargados Contrato (/api/v1/encargados-contrato)", level=2)
    add_endpoint_table(doc, "Encargados", [
        ["GET", "/", "Sí", "admin_empresa", "skip, limit", "EncargadoContratoListResponse", "encargados"],
        ["GET", "/{contrato_id}", "Sí", "admin_empresa", "contrato_id", "EncargadoContratoOut", "encargados"],
        ["POST", "/", "Sí", "admin_empresa", "nombre, rut, email, empresa_id, archivo", "EncargadoContratoOut", "encargados"],
        ["PUT", "/{contrato_id}", "Sí", "admin_empresa", "contrato_id, campos", "EncargadoContratoOut", "encargados"],
        ["DELETE", "/{contrato_id}", "Sí", "admin_empresa", "contrato_id", "MessageResponse", "encargados"],
    ])

    doc.add_heading("3.18 Módulo DEPs (/api/v1/deps)", level=2)
    add_endpoint_table(doc, "DEPs", [
        ["GET", "/", "Sí", "admin_empresa", "skip, limit", "DEPListResponse", "deps"],
        ["POST", "/", "Sí", "admin_empresa", "nombre, empresa_id, padre_id", "DEPOut", "deps"],
        ["PUT", "/{dep_id}", "Sí", "admin_empresa", "dep_id, campos", "DEPOut", "deps"],
        ["DELETE", "/{dep_id}", "Sí", "admin_empresa", "dep_id", "MessageResponse", "deps"],
    ])

    doc.add_heading("3.19 Módulo User Companies (/api/v1/user-companies)", level=2)
    add_endpoint_table(doc, "User Companies", [
        ["GET", "/", "Sí", "Usuario", "—", "list[UserCompanyOut]", "user_companies"],
        ["POST", "/", "Sí", "superadmin", "user_id, company_id", "UserCompanyOut", "user_companies"],
        ["DELETE", "/{uc_id}", "Sí", "superadmin", "uc_id", "MessageResponse", "user_companies"],
    ])

    doc.add_heading("3.20 Módulo Tkt Reglas Asignación (/api/v1/admin/tkt-reglas-asignacion)", level=2)
    add_endpoint_table(doc, "Tkt Reglas", [
        ["GET", "/", "Sí", "admin_empresa", "skip, limit", "list[TktReglaAsignacionResponse]", "tkt_reglas"],
        ["GET", "/{regla_id}", "Sí", "admin_empresa", "regla_id", "TktReglaAsignacionResponse", "tkt_reglas"],
        ["POST", "/", "Sí", "admin_empresa", "nombre, condiciones, usuario_asignado_id", "TktReglaAsignacionResponse", "tkt_reglas"],
        ["PUT", "/{regla_id}", "Sí", "admin_empresa", "regla_id, campos", "TktReglaAsignacionResponse", "tkt_reglas"],
        ["DELETE", "/{regla_id}", "Sí", "admin_empresa", "regla_id", "MessageResponse", "tkt_reglas"],
    ])

    doc.add_heading("3.21 Módulo Tkt Plantillas (/api/v1/admin/tkt-plantillas)", level=2)
    add_endpoint_table(doc, "Tkt Plantillas", [
        ["GET", "/", "Sí", "admin_empresa", "skip, limit", "list[TktPlantillaResponse]", "tkt_plantillas"],
        ["GET", "/{plantilla_id}", "Sí", "admin_empresa", "plantilla_id", "TktPlantillaResponse", "tkt_plantillas"],
        ["POST", "/", "Sí", "admin_empresa", "nombre, contenido, tipo", "TktPlantillaResponse", "tkt_plantillas"],
        ["PUT", "/{plantilla_id}", "Sí", "admin_empresa", "plantilla_id, campos", "TktPlantillaResponse", "tkt_plantillas"],
        ["DELETE", "/{plantilla_id}", "Sí", "admin_empresa", "plantilla_id", "MessageResponse", "tkt_plantillas"],
    ])

    doc.add_heading("4. Códigos de Error Estándar", level=1)
    error_codes = [
        ["400", "Bad Request", "Parámetros inválidos o faltantes."],
        ["401", "Unauthorized", "Token expirado o CSRF inválido."],
        ["403", "Forbidden", "Sin permisos para el recurso (RBAC)."],
        ["404", "Not Found", "Recurso no encontrado."],
        ["409", "Conflict", "Conflicto de estado (ej. RAT ya aprobado)."],
        ["422", "Validation Error", "Schema Pydantic no validado."],
        ["429", "Too Many Requests", "Rate limit excedido."],
        ["500", "Internal Server Error", "Error inesperado del servidor."],
    ]
    add_styled_table(doc, ["Código", "Nombre", "Descripción"], error_codes,
                     col_widths_cm=[1.8, 3.5, 12.2], first_col_bold=True)

    doc.add_heading("5. Rate Limiting", level=1)
    rate_limits = [
        ["/auth/login", "5/min", "Por IP"],
        ["/auth/logout", "10/min", "Por usuario"],
        ["/ai/ask", "20/min", "Por usuario"],
        ["/solicitudes-derecho/", "3/hour", "Por IP"],
        ["Default", "100/min", "Por IP"],
    ]
    add_styled_table(doc, ["Endpoint", "Límite", "Scope"], rate_limits,
                     col_widths_cm=[5.5, 2.5, 4.0], first_col_bold=True)

    doc.add_heading("6. PII Masking en Logs", level=1)
    add_paragraph(doc, "Los siguientes campos son enmascarados automáticamente en logs:")
    pii_fields = [
        ["email", "j***@ejemplo.com"],
        ["rut", "12.345.678-*"],
        ["ip_origen", "192.168.***"],
        ["password", "***"],
        ["Authorization", "Bearer ***"],
    ]
    add_styled_table(doc, ["Campo", "Ejemplo máscara"], pii_fields,
                     col_widths_cm=[5.0, 7.0], first_col_bold=True)

    add_final_note(doc)
    doc.save(OUT_FILE)
    print(f"[OK] {OUT_FILE}")


if __name__ == "__main__":
    build()
