"""
Build 10 — Plan de QA v1.6.5 (Post Iter 11 + Iter 12)
Genera: docs/documentacion_oficial/10_Plan_QA_Custodio_RAT_Manager_v1.6.5.docx
Cambios v1.6.5:
- TC-030 a TC-038: 9 tests nuevos para los fixes de Iter 12
"""
import os
import sys
_THIS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _THIS)
from _theme_custodio import *
import _theme_custodio
_theme_custodio.DOC_VERSION = "v1.6.5"

OUT_DIR = r"C:\Users\chelo\Desktop\RAT_opencode\docs\documentacion_oficial"
ASSETS_DIR = os.path.join(OUT_DIR, "assets")
OUT_FILE = os.path.join(OUT_DIR, "10_Plan_QA_Custodio_RAT_Manager_v1.6.5.docx")
DOC_CODE = "CUST-DOC-10"
DOC_TITLE = "Plan de Calidad"
DOC_DATE = "Junio 2026"


def build():
    doc = new_document()
    add_header_footer(doc, DOC_TITLE)
    add_cover(doc, title="PLAN DE QUALITY ASSURANCE",
              subtitle="Estrategia, casos de prueba y métricas · v1.6.5",
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
    ])
    add_toc(doc)

    doc.add_heading("1. Resumen ejecutivo", level=1)
    add_paragraph(doc, "_v1.6.5 (26-Jun-2026): 9 fixes CRITICOS+ALTOS Iter 12. Score: 6.3/10. pytest: 10/10 PASS (test_rat_tier1_tier2.py). TypeScript: 0 errores._")
    add_paragraph(doc, "QA backend: https://custodio-api-qa.vercel.app. QA frontend: https://custodio-qa.vercel.app.")

    doc.add_heading("2. Casos de prueba nuevos (v1.6.5 — Iter 11+12)", level=1)
    tc_nuevos = [
        ["TC-030", "CRÍTICO", "Backend", "BYTEA archivo_base_legal_datos >10MB → PostgreSQL CHECK constraint violation",
         "PUT /rats/{id} con archivo_base_legal_base64 >10MB", "Error 400 con mensaje 'exceeds maximum size'", "pytest"],
        ["TC-031", "CRÍTICO", "Backend", "BYTEA tkt_adjunto.data >10MB → PostgreSQL CHECK constraint violation",
         "POST /tkt-solicitud-derecho/{id}/adjuntos con archivo >10MB", "Error 400", "pytest"],
        ["TC-032", "CRÍTICO", "Backend", "Test IL con menos de 50 caracteres → Pydantic validation error",
         "PUT /rats/{id} con test_interes_legitimo <50 chars", "Error 422 de Pydantic", "pytest"],
        ["TC-033", "CRÍTICO", "Backend", "PATCH TKT resuelto sin adjuntos → HTTP 400",
         "PATCH /tkt-solicitud-derecho/{id} con estado=resuelto sin adjuntos", "Error 400: 'No se puede resolver sin evidencia'", "pytest"],
        ["TC-034", "CRÍTICO", "Backend", "Hash SHA-256 calculado automáticamente al resolver TKT con adjuntos",
         "PATCH /tkt-solicitud-derecho/{id} con adjuntos y estado=resuelto", "evidencia_respuesta_hash no null en response", "pytest"],
        ["TC-035", "ALTO", "Backend", "causal_rechazo con valor no permitido → Pydantic validation error",
         "PATCH /tkt-solicitud-derecho/{id} con causal_rechazo='valor_invalido'", "Error 422", "pytest"],
        ["TC-036", "ALTO", "Backend", "causal_rechazo obligatorio al rechazar TKT → toast error",
         "Intentar guardar respuesta con estado=rechazado y causal_rechazo vacío", "HTTP 400 o validación frontend", "Playwright"],
        ["TC-037", "ALTO", "Backend", "Notificación APDC enviada al marcar notificado_apdc=true en brecha",
         "PUT /brechas/{id} con notificado_apdc=true (primera vez)", "Email enviado al DPO (logged en DRY_RUN)", "pytest + mock"],
        ["TC-038", "ALTO", "Backend", "pytest test_rat_tier1_tier2.py pasa contra Neon QA",
         "python -m pytest tests/test_rat_tier1_tier2.py -v", "10/10 PASS contra custodio_test Neon QA", "pytest"],
    ]
    add_styled_table(doc, ["ID", "Severidad", "Nivel", "Descripción", "Pasos", "Resultado Esperado", "Framework"],
                     tc_nuevos, col_widths_cm=[1.0, 1.5, 1.5, 3.5, 4.5, 3.5, 1.5],
                     first_col_bold=True, underline_new=True)

    doc.add_heading("3. Resumen de cobertura", level=1)
    cobertura = [
        ["Backend pytest", "~230 tests", "pytest + httpx", "10 nuevos en TC-030 a TC-038", "225+ passing"],
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
