"""
Build 12 — Manual Técnico v1.7 (Sprint 2: Export tickets + SLA alerts)
Genera: docs/documentacion_oficial/12_Manual_Tecnico_Custodio_RAT_Manager_v1.7.docx
Cambios v1.7:
- export_tkt_service.py: generar_csv(), generar_excel() (openpyxl), generar_pdf() (reportlab), generar_resumen_html()
- export_tkt.py: endpoints GET /export/tkt/csv, /excel, /pdf con 5 filtros
- sla_alert_service.py: TaskType.SLA_ALERT_T2, _run_sla_alert_t2(), notificar_sla_alert_t2()
- GitHub Actions: .github/workflows/sla-alert.yml con cron y workflow_dispatch
- tarea_service.py: integración TaskType.SLA_ALERT_T2 en run_task()
- email_service.py: función notificar_sla_alert_t2() con tabla HTML, color coding
- frontend-next/lib/api.ts: descargarTktCsv(), descargarTktExcel(), descargarTktPdf(), downloadBlob()
- frontend-next/app/(app)/tkt_solicitud_derecho/page.tsx: SlaAlertBanner + Export dropdown
--- (v1.6 ---)
- RatDetailModal + RatDetailView + PdfPreview (React components)
- Drawer responsive con 5 size variants (sm/md/lg/xl/full)
- AppContext memoized + useRef stable callbacks
- Dashboard clickable + useMemo ordering fix
- IDOR+500 fix en /rats/{id}/archivo
--- (v1.5 ---)
- CSRF Middleware documentado (csrf.py)
- Encryption Layer documentado (crypto.py, ENCRYPTION_KEY)
- Service Layer documentado (5 servicios)
- Migration script documentado (encrypt_existing_bytea.py)
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
OUT_FILE = os.path.join(OUT_DIR, "12_Manual_Tecnico_Custodio_RAT_Manager_v1.7.docx")
DOC_CODE = "CUST-DOC-12"
DOC_TITLE = "Manual Técnico"
DOC_DATE = "Junio 2026"


def build():
    doc = new_document()
    add_header_footer(doc, DOC_TITLE)
    add_cover(doc, title="MANUAL TÉCNICO",
              subtitle="Arquitectura, stack, deployment y operaciones · v1.7",
              code=DOC_CODE)
    add_version_control(doc, DOC_CODE, DOC_TITLE, changes=[
        ("1.0", "Junio 2026", "Arquitectura inicial: FastAPI + Next.js + Neon."),
        ("1.1", "Junio 2026", "Agregados módulos AI, Feriados, transparencia. ALLOWED_ORIGINS configurable."),
        ("1.2", "Junio 2026", "Seguridad: token blacklist, IDOR, CSV sanitize, hash chain, PII masking."),
        ("1.3", "Junio 2026", "_Beta Launch: /health endpoint, RBAC fixes DT-014/DT-015, router fixes consentimientos/eipd._"),
        ("1.4", "Junio 2026", "_OCI Object Storage con fallback chain (PAR→signed GET→BYTEA), Admin Asesor IA._"),
        ("1.5", "Junio 2026", "_Seguridad: CSRF, Encryption at Rest, Service Layer, Migration scripts._"),
        ("1.6", "Junio 2026", "_UI/UX: RatDetailModal, Drawer responsive, AppContext memo, IDOR fix backend._"),
        ("1.7", "Junio 2026", "_Sprint 2: export_tkt_service.py, sla_alert_service.py, GitHub Actions workflow._"),
    ])
    add_toc(doc)

    doc.add_heading("1. Arquitectura del sistema", level=1)
    add_paragraph(doc, BRAND_FULL + " usa arquitectura modular de 3 capas:")
    add_bullet(doc, "Frontend: Next.js 14 (App Router) + TypeScript + TailwindCSS. Desplegado en Vercel.")
    add_bullet(doc, "Backend: FastAPI 0.115 + Uvicorn ASGI. Desplegado en Vercel Serverless Functions.")
    add_bullet(doc, "Base de datos: Neon PostgreSQL 15 (serverless). Cache: LRU en memoria.")
    add_bullet(doc, "_Almacenamiento: OCI Object Storage con fallback a BYTEA en PostgreSQL._")
    add_paragraph(doc, "_API Backend: https://custodio-api-qa.vercel.app (QA). Frontend: https://custodio-qa.vercel.app (QA)._")

    doc.add_heading("2. Stack tecnológico", level=1)
    stack = [
        ["Componente", "Tecnología", "Versión"],
        ["Backend", "FastAPI + Uvicorn", "0.115+"],
        ["Frontend", "Next.js + TypeScript", "14+"],
        ["DB", "Neon PostgreSQL", "15+"],
        ["Storage", "_OCI Object Storage + BYTEA fallback_", "_v1.4_"],
        ["Auth", "python-jose + passlib", "JWT RS256"],
        ["PDF", "ReportLab", "4.0+"],
        ["CSV", "csv + sanitization custom", "—"],
        ["Excel", "_openpyxl_", "_v1.7_"],
        ["Rate limit", "slowapi", "0.1+"],
        ["Logging", "Python logging + PIIMaskingFilter", "—"],
        ["IA", "_MiniMax M2.7 / OpenAI GPT-4_", "_v1.4_"],
    ]
    add_styled_table(doc, ["Componente", "Tecnología", "Versión"],
                     stack, col_widths_cm=[3.5, 5.5, 3.5],
                     first_col_bold=True, underline_new=True)

    doc.add_heading("3. Modelos de datos", level=1)
    add_paragraph(doc, "_Modelos principales: User, Company, RAT, Consentimiento, EIPD, Breach, TicketArco, AuditLog, AsesorChunk. "
                      "RAT tiene campo archivo_base_legal_storage_url (OCI) además de archivo_base_legal_datos (BYTEA)._")

    doc.add_heading("4. OCI Object Storage Integration", level=1)
    add_paragraph(doc, "_Implementación de OCI Object Storage (storage.py):_")
    oci_components = [
        ["OCISigner", "_Firma requests para OCI API usando API Signing Key (RSA SHA256)._"],
        ["OCIStorageBackend", "_Backend de almacenamiento con upload, download, delete, list._"],
        ["create_presigned_url()", "_Genera PAR (Pre-Authenticated Request) para descarga directa._"],
        ["copy_to_archive()", "_Copia objeto al bucket archive antes de eliminar._"],
        ["list_archive_objects()", "_Lista objetos en bucket de archive._"],
    ]
    add_styled_table(doc, ["Componente", "Descripción"], oci_components,
                     col_widths_cm=[4.5, 13.0], first_col_bold=True, underline_new=True)

    doc.add_heading("4.1 Fallback Chain para descarga", level=2)
    add_paragraph(doc, "_El endpoint GET /rats/{rat_id}/archivo implementa una cadena de fallback:_")
    fallback_chain = [
        ["Paso 1", "PAR (Pre-Authenticated Request)", "_Intenta generar URL pre-firmada desde OCI. Si IAM no tiene permisos PAR, continúa._"],
        ["Paso 2", "Signed GET directo", "_Descarga directo desde OCI usando OCISigner (requiere 'manage objects')._"],
        ["Paso 3", "BYTEA fallback", "_Retorna datos de PostgreSQL (campo archivo_base_legal_datos)._"],
    ]
    add_styled_table(doc, ["Paso", "Método", "Descripción"], fallback_chain,
                     col_widths_cm=[1.5, 4.5, 11.5], first_col_bold=True, underline_new=True)

    doc.add_heading("5. Seguridad implementada", level=1)
    add_paragraph(doc, "_Todas las medidas de seguridad de v1.4:_")
    seguridad = [
        ["Token blacklist", "_JTI consultado en get_current_user. LRU cache 1000 slots. Tokens revocados retornan 401._"],
        ["IDOR protection", "_check_company_access() en todas las rutas con company_id. Fallback 403._"],
        ["RBAC", "_admin_empresa solo gestiona RATs de sus empresas (DT-014). usuario no crea brechas (DT-015)._"],
        ["CSV sanitization", "_Prefijo ' (apostrophe) en campos que empiecen con =, +, -, @ para prevenir CSV injection._"],
        ["Hash chain", "_prev_hash SHA256 en cada audit_log. verify_audit_chain() para validar integridad._"],
        ["Rate limiting", "_5/min /auth/login, 5/min cambio password, 3/hora tickets ARCO, 10/min logout, 10/min AI._"],
        ["PII masking", "_PIIMaskingFilter en logging: mask email, RUT, IP, tokens, passwords en logs._"],
        ["JWT expiry", "_480 min (8h). Refresh token rotation en logout._"],
    ]
    add_styled_table(doc, ["Medida", "Descripción"], seguridad,
                     col_widths_cm=[3.5, 13.0], first_col_bold=True)

    doc.add_heading("6. Admin Asesor IA", level=1)
    add_paragraph(doc, "_Gestión del corpus del asesor IA (solo superadmin):_")
    asesor_routes = [
        ["POST /admin/asesor/index", "_Indexa archivos en el corpus. Params: paths (lista), force (bool)._"],
        ["GET /admin/asesor/stats", "_Retorna estadísticas: total chunks, fuentes, tamaño promedio._"],
        ["DELETE /admin/asesor/documents/{chunk_id}", "_Elimina un chunk específico del índice._"],
    ]
    add_styled_table(doc, ["Ruta", "Descripción"], asesor_routes,
                     col_widths_cm=[5.5, 12.0], first_col_bold=True, underline_new=True)

    doc.add_heading("7. Export Tickets Service (export_tkt_service.py)", level=1)
    add_paragraph(doc, "_Servicio de exportación de tickets ARCO en múltiples formatos (v1.7):_")
    export_funcs = [
        ["generar_csv()", "_Genera CSV con sanitización de inyección. Headers: company_id, estado, prioridad, fecha_desde, fecha_hasta._"],
        ["generar_excel()", "_Genera archivo .xlsx usando openpyxl con formatting, headers en negrita y estilos._"],
        ["generar_pdf()", "_Genera PDF usando ReportLab con tabla formateada y footer del documento._"],
        ["generar_resumen_html()", "_Genera resumen HTML embebible con estilos inline para emails._"],
    ]
    add_styled_table(doc, ["Función", "Descripción"], export_funcs,
                     col_widths_cm=[4.0, 13.5], first_col_bold=True, underline_new=True)

    doc.add_heading("7.1 Endpoints de Exportación (export_tkt.py)", level=2)
    add_paragraph(doc, "_Endpoints REST para descarga de tickets con 5 filtros (v1.7):_")
    export_endpoints = [
        ["GET /export/tkt/csv", "_company_id, estado, prioridad, fecha_desde, fecha_hasta → CSV sanitizado_"],
        ["GET /export/tkt/excel", "_company_id, estado, prioridad, fecha_desde, fecha_hasta → .xlsx (openpyxl)_"],
        ["GET /export/tkt/pdf", "_company_id, estado, prioridad, fecha_desde, fecha_hasta → PDF (ReportLab)_"],
    ]
    add_styled_table(doc, ["Endpoint", "Parámetros y formato"], export_endpoints,
                     col_widths_cm=[4.0, 13.5], first_col_bold=True, underline_new=True)

    doc.add_heading("8. SLA Alert Service (sla_alert_service.py)", level=1)
    add_paragraph(doc, "_Servicio de alertas SLA para tickets T2 (v1.7):_")
    sla_components = [
        ["TaskType.SLA_ALERT_T2", "_Enum TaskType extendido con SLA_ALERT_T2 para tareas programadas de alerta._"],
        ["_run_sla_alert_t2()", "_Función principal que evalúa estado de tickets y determina cuáles requieren alerta._"],
        ["notificar_sla_alert_t2()", "_Envía notificación por email con tabla HTML, coding de colores según severidad._"],
    ]
    add_styled_table(doc, ["Componente", "Descripción"], sla_components,
                     col_widths_cm=[4.5, 13.0], first_col_bold=True, underline_new=True)

    doc.add_heading("8.1 Integración en tarea_service.py", level=2)
    add_paragraph(doc, "_run_task() en tarea_service.py ahora soporta TaskType.SLA_ALERT_T2 para scheduling._")

    doc.add_heading("9. GitHub Actions Workflow (sla-alert.yml)", level=1)
    add_paragraph(doc, "_Workflow de GitHub Actions para ejecución periódica de alertas SLA (v1.7):_")
    workflow_table = [
        ["Trigger", "_cron: 0 */4 * * * (cada 4 horas). workflow_dispatch para ejecución manual._"],
        ["Ruta", "_.github/workflows/sla-alert.yml_"],
        ["Entorno", "_Python 3.11, dependencias del proyecto instaladas._"],
    ]
    add_styled_table(doc, ["Propiedad", "Descripción"], workflow_table,
                     col_widths_cm=[3.0, 14.5], first_col_bold=True, underline_new=True)

    doc.add_heading("10. Email Service - notificar_sla_alert_t2()", level=1)
    add_paragraph(doc, "_Función en email_service.py para envío de alertas SLA (v1.7):_")
    email_table = [
        ["Entrada", "_Lista de tickets con estado, prioridad, días_pendientes._"],
        ["Salida", "_Email HTML con tabla formateada, coding de colores (verde/amarillo/rojo)._"],
        ["Tabla HTML", "_Columnas: ID, Empresa, Estado, Prioridad, Días. Filas con color según SLA._"],
        ["Color coding", "_Verde: dentro de SLA. Amarillo: próximo a vencer. Rojo: SLA vencido._"],
    ]
    add_styled_table(doc, ["Aspecto", "Descripción"], email_table,
                     col_widths_cm=[3.0, 14.5], first_col_bold=True, underline_new=True)

    doc.add_heading("11. Frontend API (frontend-next/lib/api.ts)", level=1)
    add_paragraph(doc, "_Funciones de exportación en el cliente Next.js (v1.7):_")
    api_table = [
        ["descargarTktCsv()", "_Llama GET /export/tkt/csv, usa downloadBlob() para descarga._"],
        ["descargarTktExcel()", "_Llama GET /export/tkt/excel, usa downloadBlob() para descarga._"],
        ["descargarTktPdf()", "_Llama GET /export/tkt/pdf, usa downloadBlob() para descarga._"],
        ["downloadBlob()", "_Helper genérico: crea Blob, URL.createObjectURL, trigger click en link oculto._"],
    ]
    add_styled_table(doc, ["Función", "Descripción"], api_table,
                     col_widths_cm=[4.0, 13.5], first_col_bold=True, underline_new=True)

    doc.add_heading("12. Frontend - Página Tickets (tkt_solicitud_derecho/page.tsx)", level=1)
    add_paragraph(doc, "_Componentes nuevos en la UI de tickets (v1.7):_")
    frontend_table = [
        ["SlaAlertBanner", "_Banner superior con estado SLA de tickets. Muestra conteo y color coding._"],
        ["Export dropdown", "_Dropdown en toolbar para exportar CSV/Excel/PDF con filtros aplicados._"],
    ]
    add_styled_table(doc, ["Componente", "Descripción"], frontend_table,
                     col_widths_cm=[4.0, 13.5], first_col_bold=True, underline_new=True)

    doc.add_heading("13. Deployment y variables de entorno", level=1)
    add_paragraph(doc, "_Backend (Vercel): DATABASE_URL, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES=480, "
                      "ENV=test|production, CORS_ALLOWED_ORIGINS, OCI_* (namespace, region, bucket, tenancy, user, fingerprint, key_content)._")
    add_paragraph(doc, "_Frontend: NEXT_PUBLIC_API_BASE=https://custodio-api-qa.vercel.app._")
    add_paragraph(doc, "_OCI config: OCI_NAMESPACE, OCI_REGION, OCI_BUCKET, OCI_ARCHIVE_BUCKET, OCI_TENANCY, OCI_USER, OCI_FINGERPRINT, OCI_KEY_CONTENT._")

    doc.add_heading("14. Logs y monitoreo", level=1)
    add_paragraph(doc, "_PIIMaskingFilter aplicado automáticamente a todos los handlers de logging._ "
                      "Campos filtrados: email, rut, ip_address, access_token, refresh_token, password. "
                      "Logs en formato JSON para ingestion en monitoreo centralizado.")

    doc.add_heading("15. Commits técnicos v1.7", level=1)
    commits_v17 = [
        ["export_tkt_service", "_ generación CSV, Excel (openpyxl), PDF (ReportLab), HTML._"],
        ["export_tkt.py", "_ endpoints GET /export/tkt/ con 5 filtros._"],
        ["sla_alert_service", "_ TaskType.SLA_ALERT_T2, _run_sla_alert_t2, notificar_sla_alert_t2._"],
        ["sla-alert.yml", "_ GitHub Actions workflow con cron 0 */4 * * *_"],
        ["tarea_service", "_ integración TaskType.SLA_ALERT_T2 en run_task._"],
        ["email_service", "_ función notificar_sla_alert_t2 con tabla HTML y color coding._"],
        ["frontend/api.ts", "_ descargarTktCsv, descargarTktExcel, descargarTktPdf, downloadBlob._"],
        ["tkt_solicitud_derecho", "_ SlaAlertBanner + Export dropdown._"],
    ]
    add_styled_table(doc, ["Commit/Archivo", "Descripción"], commits_v17,
                     col_widths_cm=[4.0, 13.5], first_col_bold=True, underline_new=True)

    doc.add_heading("16. Pendientes técnicos para v1.8", level=1)
    pending = [
        ["SLA-T1", "SLA Alert T1", "P0", "Implementar alertas para tickets T1 además de T2."],
        ["DT-009", "Cobertura tests", "P1", "~30% actual. Meta 45%."],
        ["DT-010", "E2E CI/CD", "P1", "Playwright en pipeline de GitHub Actions."],
        ["EXPORT-01", "Export filtrado", "P2", "Permitir selección de columnas a exportar."],
    ]
    add_styled_table(doc, ["ID", "Nombre", "Prioridad", "Descripción"],
                     pending, col_widths_cm=[1.8, 3.5, 1.8, 9.4],
                     first_col_bold=True)

    add_risks_appendix(doc, [
        ("R-MT-01", "Pendientes S14 y C1 de v1.4 requieren cambios de infraestructura significativos.", "Alto"),
        ("R-MT-02", "Coverage 30% vs meta 45%. Necesarios ~40 tests unitarios adicionales.", "Medio"),
        ("R-MT-03", "_PAR IAM permission no disponible. Fallback a signed GET requiere 'manage objects'._", "Bajo"),
    ])

    doc.save(OUT_FILE)
    print(f"[OK] {OUT_FILE}")


if __name__ == "__main__":
    build()
