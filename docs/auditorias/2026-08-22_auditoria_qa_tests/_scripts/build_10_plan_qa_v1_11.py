"""
Build 10 — Plan de QA v1.11 (QA Total: 78 fallos → 0)
Genera: docs/documentacion_oficial/10_Plan_QA_Custodio_RAT_Manager_v1.11.docx
Cambios v1.11:
- TC-047 a TC-055: 9 casos nuevos para los fixes de la sesión QA 2026-08-22
- Suite completa verde: 732 tests, 0 fallos
"""
import os
import sys
_THIS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _THIS)
from _theme_custodio import *
import _theme_custodio
_theme_custodio.DOC_VERSION = "v1.11"

OUT_DIR = r"C:\Users\chelo\Desktop\RAT_opencode\docs\documentacion_oficial"
ASSETS_DIR = os.path.join(OUT_DIR, "assets")
OUT_FILE = os.path.join(OUT_DIR, "10_Plan_QA_Custodio_RAT_Manager_v1.11.docx")
DOC_CODE = "CUST-DOC-10"
DOC_TITLE = "Plan de Calidad"
DOC_DATE = "Agosto 2026"


def build():
    doc = new_document()
    add_header_footer(doc, DOC_TITLE)
    add_cover(doc, title="PLAN DE QUALITY ASSURANCE",
              subtitle="Estrategia, casos de prueba y métricas · v1.11",
              code=DOC_CODE)
    add_version_control(doc, DOC_CODE, DOC_TITLE, changes=[
        ("1.0", "Junio 2026", "Plan inicial con 45 casos de prueba para OLA-1."),
        ("1.1", "Junio 2026", "Agregados casos de seguridad: token blacklist, IDOR, rate limit."),
        ("1.2", "Junio 2026", "Casos actualizados post-auditoría: CSV injection, hash chain, PII masking."),
        ("1.3", "Junio 2026", "_Beta Launch: nuevos casos DT-014/DT-015/DT-016, CB-01/CB-02 (consentimientos/eipd), 215 pytest + ~65 E2E pasan._"),
        ("1.4", "Junio 2026", "_Post-OCI: casos para OCI download fallback chain, Admin Asesor IA._"),
        ("1.5", "Junio 2026", "_Seguridad: CSRF middleware, Encryption migration, Service Layer._"),
        ("1.6", "Junio 2026", "_UI/UX: TC-015 a TC-019 para RatDetailModal, PdfPreview, Sort, Dashboard, IDOR fix._"),
        ("1.7", "Junio 2026", "Sprint 1+2: TC-020 a TC-029 para FORMADMIN ARCO, SLA Alert, Export."),
        ("1.8", "Junio 2026", "_Iter 11+12: TC-030 a TC-038 para BYTEA 10MB, Test IL min 50, Hash SHA-256 auto, causal_rechazo enum, toggle 44px, notificaciones auto._"),
        ("1.9", "Julio 2026", "_TC-039 a TC-043 para IDOR multi-tenant (5 tests), base_legal_valida strict, ConsentimientoAlert, homologacion campos RAT, PDF titulos seccion._"),
        ("1.10", "Agosto 2026", "_TC-044 a TC-046: base_legal_valida, ConsentimientoAlert, PDF titulos. Sprint A/B/UX: C-01 soft delete, C-04 IL gate, C-05 EIPD gate, M-01 respuesta obligatoria, M-04 politica transparencia._"),
        ("1.11", "Agosto 2026", "_QA Total (2026-08-22): 78 fallos → 0. TC-047 a TC-055: PATCH resuelto con metodo_verificacion, POST /auth/users 201, ENCRYPTION_KEY estricta, EIPD payload datos_sensibles, RUT UUID, Fernet heuristica, encrypt migration idempotente, endpoint CSRF, route ordering._"),
    ])
    add_toc(doc)

    doc.add_heading("1. Resumen ejecutivo", level=1)
    add_paragraph(doc, "_v1.11 (22-Ago-2026): QA total completado. Suite: 732 tests, 0 fallos. Score QA: verde. Fixes: auth 201, prorroga identidad, encrypt_migration, EIPD validator, route ordering FastAPI._")
    add_paragraph(doc, "QA backend: https://custodio-qa.vercel.app. Frontend: https://custodio-qa.vercel.app.")

    doc.add_heading("2. Casos de prueba nuevos (v1.11 — QA Total 2026-08-22)", level=1)
    tc_nuevos = [
        ["TC-047", "CRÍTICO", "Backend", "PATCH TKT → resuelto con metodo_verificacion_identidad en body debe retornar 200",
         "PATCH /tkt-solicitud-derecho/{id} con estado=resuelto y metodo_verificacion_identidad en body", "HTTP 200, estado=resuelto", "pytest"],
        ["TC-048", "CRÍTICO", "Backend", "Prorrogar ticket desde estado resuelto debe retornar 400",
         "POST /tkt-solicitud-derecho/{id}/prorrogar (ticket en estado resuelto)", "HTTP 400", "pytest"],
        ["TC-049", "ALTO", "Backend", "POST /auth/users retorna 201 al crear usuario nuevo",
         "POST /auth/users con datos validos", "HTTP 201 con objeto usuario", "pytest"],
        ["TC-050", "ALTO", "Backend", "encrypt_existing_bytea falla si ENCRYPTION_KEY='' (sin fallback a settings)",
         "Ejecutar _check_prerequisites() con ENCRYPTION_KEY=''", "SystemExit", "pytest"],
        ["TC-051", "ALTO", "Backend", "encrypt_existing_bytea detect datos ya cifrados como Fernet",
         "is_already_encrypted(fernet.encrypt(b'test'))", "True", "pytest"],
        ["TC-052", "ALTO", "Backend", "encrypt_existing_bytea dry-run no modifica BD",
         "_migrate_table(..., dry_run=True)", "stats['migrados']==0, datos sin cambios", "pytest"],
        ["TC-053", "ALTO", "Backend", "encrypt_existing_bytea segunda pasada idempotente",
         "_migrate_table() dos veces sobre mismos datos", "Segunda: ya_cifrados=1, migrados=0", "pytest"],
        ["TC-054", "ALTO", "Backend", "EIPD validator bloquea datos_sensibles=True sin evaluacion_impacto+estado_eipd",
         "POST /rats/ con datos_sensibles=True sin EIPD fields", "HTTP 422", "pytest"],
        ["TC-055", "MEDIO", "Backend", "Ruta /auditoria/verify-chain no capturada por /{company_id}",
         "GET /rats/auditoria/verify-chain (superadmin)", "HTTP 200 con chain info", "pytest"],
    ]
    add_styled_table(doc, ["ID", "Severidad", "Nivel", "Descripción", "Pasos", "Resultado Esperado", "Framework"],
                     tc_nuevos, col_widths_cm=[1.0, 1.5, 1.5, 3.5, 4.5, 3.5, 1.5],
                     first_col_bold=True, underline_new=True)

    doc.add_heading("3. Resumen de cobertura", level=1)
    cobertura = [
        ["Backend pytest", "~732 tests", "pytest + httpx", "9 nuevos en TC-047 a TC-055", "732 passing (0 fallos)"],
        ["Frontend TypeScript", "0 errors", "tsc --noEmit", "Sin cambios en types", "0 errors"],
        ["Integration", "QA Neon", "Neon PostgreSQL", "custodio_test + neondb", "OK"],
    ]
    add_styled_table(doc, ["Tipo", "Cantidad", "Framework", "Alcance", "Estado"],
                     cobertura, col_widths_cm=[2.5, 1.5, 2.0, 3.5, 3.0])

    add_final_note(doc)
    doc.save(OUT_FILE)
    print(f"[OK] {OUT_FILE}")


if __name__ == "__main__":
    build()
