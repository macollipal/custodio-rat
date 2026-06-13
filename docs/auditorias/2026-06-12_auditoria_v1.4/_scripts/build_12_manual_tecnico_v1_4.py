"""
Build 12 — Manual Técnico v1.4 (Post-OCI Integration)
Genera: docs/documentacion_oficial/12_Manual_Tecnico_Custodio_RAT_Manager_v1.4.docx
Cambios v1.4:
- OCI Object Storage documentado (storage.py, OCISigner, fallback chain)
- Admin Asesor IA documentado
- Nuevo endpoint /rats/{id}/archivo con fallback chain
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
OUT_FILE = os.path.join(OUT_DIR, "12_Manual_Tecnico_Custodio_RAT_Manager_v1.4.docx")
DOC_CODE = "CUST-DOC-12"
DOC_TITLE = "Manual Técnico"
DOC_DATE = "Junio 2026"


def build():
    doc = new_document()
    add_header_footer(doc, DOC_TITLE)
    add_cover(doc, title="MANUAL TÉCNICO",
              subtitle="Arquitectura, stack, deployment y operaciones · v1.4",
              code=DOC_CODE)
    add_version_control(doc, DOC_CODE, DOC_TITLE, changes=[
        ("1.0", "Junio 2026", "Arquitectura inicial: FastAPI + Next.js + Neon."),
        ("1.1", "Junio 2026", "Agregados módulos AI, Feriados, transparencia. ALLOWED_ORIGINS configurable."),
        ("1.2", "Junio 2026", "Seguridad: token blacklist, IDOR, CSV sanitize, hash chain, PII masking."),
        ("1.3", "Junio 2026", "_Beta Launch: /health endpoint, RBAC fixes DT-014/DT-015, router fixes consentimientos/eipd._"),
        ("1.4", "Junio 2026", "_OCI Object Storage con fallback chain (PAR→signed GET→BYTEA), Admin Asesor IA._"),
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

    doc.add_heading("7. Deployment y variables de entorno", level=1)
    add_paragraph(doc, "_Backend (Vercel): DATABASE_URL, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES=480, "
                      "ENV=test|production, CORS_ALLOWED_ORIGINS, OCI_* (namespace, region, bucket, tenancy, user, fingerprint, key_content)._")
    add_paragraph(doc, "_Frontend: NEXT_PUBLIC_API_BASE=https://custodio-api-qa.vercel.app._")
    add_paragraph(doc, "_OCI config: OCI_NAMESPACE, OCI_REGION, OCI_BUCKET, OCI_ARCHIVE_BUCKET, OCI_TENANCY, OCI_USER, OCI_FINGERPRINT, OCI_KEY_CONTENT._")

    doc.add_heading("8. Logs y monitoreo", level=1)
    add_paragraph(doc, "_PIIMaskingFilter aplicado automáticamente a todos los handlers de logging._ "
                      "Campos filtrados: email, rut, ip_address, access_token, refresh_token, password. "
                      "Logs en formato JSON para ingestion en monitoreo centralizado.")

    doc.add_heading("9. Commits técnicos v1.4", level=1)
    commits_seg = [
        ["57cbffc", "_Fallback OCI download cuando PAR falla (storage.py, rat_service.py)_"],
        ["reorganizacion-carpetas", "_Reorganización carpetas docs/, scripts/, archive/_"],
    ]
    add_styled_table(doc, ["Commit", "Descripción"], commits_seg,
                     col_widths_cm=[2.0, 15.5], first_col_bold=True, underline_new=True)

    doc.add_heading("10. Pendientes técnicos para v1.4", level=1)
    pending = [
        ["S14", "CSRF protection", "P0", "Validación anti-CSRF en formularios web."],
        ["C1", "Encryption at rest", "P1", "AES-256 encryption a nivel aplicación."],
        ["A6", "Service layer", "P2", "Decoupling lógica de negocio para unit tests."],
        ["DT-009", "Cobertura tests", "P1", "~25% actual. Meta 40%."],
        ["DT-010", "E2E CI/CD", "P1", "Playwright en pipeline de GitHub Actions."],
    ]
    add_styled_table(doc, ["ID", "Nombre", "Prioridad", "Descripción"],
                     pending, col_widths_cm=[1.8, 3.5, 1.8, 9.4],
                     first_col_bold=True)

    add_risks_appendix(doc, [
        ("R-MT-01", "Pendientes S14 y C1 requieren cambios de infraestructura significativos.", "Alto"),
        ("R-MT-02", "Coverage 25% vs meta 40%. Necesarios ~30 tests unitarios adicionales.", "Medio"),
        ("R-MT-03", "_PAR IAM permission no disponible. Fallback a signed GET requiere 'manage objects'._", "Bajo"),
    ])

    doc.save(OUT_FILE)
    print(f"[OK] {OUT_FILE}")


if __name__ == "__main__":
    build()