"""
Build Matriz — Matriz de Trazabilidad v1.4 (Post-OCI Integration)
Genera: docs/documentacion_oficial/Matriz_Trazabilidad_Custodio_RAT_Manager_v1.4.docx
Cambios v1.4:
- OCI Object Storage agregado (DT-OCI-01)
- Admin Asesor IA agregado (DT-OCI-02)
- TC para OCI fallback chain
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
OUT_FILE = os.path.join(OUT_DIR, "Matriz_Trazabilidad_Custodio_RAT_Manager_v1.4.docx")
DOC_CODE = "CUST-DOC-MATRIZ"
DOC_TITLE = "Matriz de Trazabilidad"
DOC_DATE = "Junio 2026"


def build():
    doc = new_document()
    add_header_footer(doc, DOC_TITLE)
    add_cover(doc, title="MATRIZ DE TRAZABILIDAD",
              subtitle="Requisitos Ley 21.719 → Features → User Stories → Tests",
              code=DOC_CODE)
    add_version_control(doc, DOC_CODE, DOC_TITLE, changes=[
        ("1.0", "Junio 2026", "Matriz inicial con 20 requisitos de la Ley 21.719."),
        ("1.1", "Junio 2026", "Agregados requisitos de seguridad: token blacklist, hash chain, IDOR."),
        ("1.2", "Junio 2026", "Actualizada post-auditoría con hallazgos críticos."),
        ("1.3", "Junio 2026", "_Beta Launch: DT-014/DT-015/DT-016/DT-017 añadidos, todos los P0 cerrados._"),
        ("1.4", "Junio 2026", "_OCI Object Storage (DT-OCI-01), Admin Asesor IA (DT-OCI-02), TC para fallback chain._"),
    ])
    add_toc(doc)

    doc.add_heading("1. Trazabilidad requisitos legales", level=1)
    add_paragraph(doc, "Todos los artículos de la Ley 21.719 relevantes para Custodio RAT Manager:")
    ley_table = [
        ["Artículo", "Requisito", "Feature relacionada", "Estado"],
        ["Art. 12", "_Consentimiento expreso (Art. 12)_",
         "_US-CONS-01, US-CONS-02, CB-01_", "_CERRADO v1.3_"],
        ["Art. 14 bis", "_Gestión de brechas de seguridad_",
         "US-BRCH-01, DT-015", "_CERRADO v1.3_"],
        ["Art. 14 ter", "_Política de transparencia pública_",
         "US-PUB-01, US-PUB-02", "Cerrado"],
        ["Art. 14 quater", "_Contratos con encargados del tratamiento_",
         "US-ENC-01 al US-ENC-04", "Cerrado"],
        ["Art. 15", "_Registro de Actividades de Tratamiento (RAT)_",
         "US-RAT-01 al US-RAT-07, DT-014", "_CERRADO v1.3_"],
        ["Art. 15 bis", "_Evaluaciones de Impacto (EIPD)_",
         "_US-EIPD-01, US-EIPD-02, CB-02_", "_CERRADO v1.3_"],
        ["Art. 16", "_Datos sensibles requieren EIPD_",
         "US-EIPD-01, US-EIPD-02", "Cerrado"],
        ["Art. 17", "_Derechos ARCO (Acceso, Rectificación, Cancelación, Oposición)_",
         "US-ARCO-01 al US-ARCO-06", "Cerrado"],
        ["Art. 19", "_Medidas de seguridad técnicas y organizacionales_",
         "TF-01 al TF-12, S14 (pendiente)", "Parcial"],
    ]
    add_styled_table(doc, ["Artículo", "Requisito", "Feature relacionada", "Estado"],
                     ley_table, col_widths_cm=[2.0, 5.5, 5.5, 3.5],
                     first_col_bold=True, underline_new=True)

    doc.add_heading("2. Hallazgos de auditoría → acción", level=1)
    add_paragraph(doc, "_ traceability de los hallazgos de auditoría v1.3 y v1.4:_")
    hallz_table = [
        ["ID", "Descripción", "Gravedad", "Corrección", "Commit", "Estado"],
        ["R-API-03", "_Token blacklist JTI_", "Crítico", "_get_current_user consulta blacklist_", "96167b5", "_CERRADO_"],
        ["R-API-04", "_IDOR en /companies/{id}_", "Crítico", "_check_company_access en todas rutas_", "96167b5", "_CERRADO_"],
        ["R-API-05", "_/companies/publico sin auth_", "Crítico", "_auth requerida en endpoint_", "96167b5", "_CERRADO_"],
        ["R-API-06", "_CSV injection_", "Crítico", "_Sanitización con prefijo '_'_", "96167b5", "_CERRADO_"],
        ["R-API-07", "_Rate limiting_", "Alto", "_slowapi en /auth/login 5/min_", "96167b5", "_CERRADO_"],
        ["R-API-08", "_JWT expiry 24h_", "Medio", "_Expiry 480 min + refresh rotation_", "96167b5", "_CERRADO_"],
        ["DT-014", "_admin_empresa RAT cross-company_", "Crítico", "_RBAC check con get_empresas_usuario()_", "6209e2d", "_CERRADO_"],
        ["DT-015", "_usuario crea brechas_", "Crítico", "_RBAC bloquea rol usuario en POST /brechas/_", "6209e2d", "_CERRADO_"],
        ["DT-016", "_Sin /health endpoint_", "Medio", "_GET /health y /health/db implementados_", "6209e2d", "_CERRADO_"],
        ["DT-017", "_consentimientos/eipd 500_", "Crítico", "_get_user() → Depends(get_current_user)_", "6980187/43287c0", "_CERRADO_"],
        ["DT-OCI-01", "_Descarga archivo sin OCI_", "Alto", "_Fallback chain PAR→signed GET→BYTEA_", "57cbffc", "_CERRADO v1.4_"],
        ["DT-OCI-02", "_Gestión corpus asesor IA_", "Medio", "_Admin Asesor endpoints_", "admin_asesor.py", "_CERRADO v1.4_"],
    ]
    add_styled_table(doc, ["ID", "Descripción", "Gravedad", "Corrección", "Commit", "Estado"],
                     hallz_table, col_widths_cm=[1.8, 4.5, 2.0, 4.5, 2.5, 2.2],
                     first_col_bold=True, underline_new=True)

    doc.add_heading("3. Features → Tests", level=1)
    add_paragraph(doc, "_Cobertura actual: ~25% (meta v1.4: 40%). Tests ejecutados: 215 pytest + ~65 E2E._")
    feat_test = [
        ["TF-01 Token blacklist", "pytest: test_blacklist_*", "215 passed", "OK"],
        ["TF-02 IDOR protection", "pytest: test_idor_* + E2E", "215 passed", "OK"],
        ["TF-03 CSV sanitization", "pytest: test_csv_injection_*", "215 passed", "OK"],
        ["TF-04 Hash chain", "pytest: test_hash_chain_*", "215 passed", "OK"],
        ["TF-05 Rate limiting", "pytest: test_rate_limit_*", "215 passed", "OK"],
        ["TF-08 RBAC fixes", "_pytest: test_rbac_* + QA-RAT-03, QA-BRCH-02_", "215 passed", "OK"],
        ["TF-09 Router fixes", "_pytest: test_consent_* + test_eipd_*_", "215 passed", "OK"],
        ["TF-10 /health", "_pytest: test_health_* + QA-SYS-01/02_", "215 passed", "OK"],
        ["TF-11 OCI Storage", "_QA-RAT-07, QA-RAT-08, QA-RAT-09 (fallback chain)_", "NEW v1.4", "OK"],
        ["TF-12 Admin Asesor", "_QA-AS-01, QA-AS-02, QA-AS-03, QA-AS-04_", "NEW v1.4", "OK"],
        ["S14 CSRF", "Pendiente", "0 tests", "PENDIENTE"],
        ["C1 Encryption", "Pendiente", "0 tests", "PENDIENTE"],
    ]
    add_styled_table(doc, ["Feature", "Tests", "Resultado", "Estado"],
                     feat_test, col_widths_cm=[4.0, 5.0, 3.0, 3.5],
                     first_col_bold=True, underline_new=True)

    add_risks_appendix(doc, [
        ("R-MAT-01", "Pendientes S14 y C1 bloquean compliance total Ley 21.719.", "Alto"),
    ])

    doc.save(OUT_FILE)
    print(f"[OK] {OUT_FILE}")


if __name__ == "__main__":
    build()