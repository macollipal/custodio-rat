"""
Build MTX — Matriz de Trazabilidad v1.9 (Post Iter 11 + Iter 12)
Genera: docs/documentacion_oficial/Matriz_Trazabilidad_Custodio_RAT_Manager_v1.9.docx
Cambios v1.9:
- RF-141 a RF-162 → HU-086 a HU-097 → CU-069 a CU-077 → TC-030 a TC-038
"""
import os
import sys
_THIS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _THIS)
from _theme_custodio import *
import _theme_custodio
_theme_custodio.DOC_VERSION = "v1.9"

OUT_DIR = r"C:\Users\chelo\Desktop\RAT_opencode\docs\documentacion_oficial"
ASSETS_DIR = os.path.join(OUT_DIR, "assets")
OUT_FILE = os.path.join(OUT_DIR, "Matriz_Trazabilidad_Custodio_RAT_Manager_v1.9.docx")
DOC_CODE = "CUST-DOC-MTX"
DOC_TITLE = "Matriz de Trazabilidad"


def build():
    doc = new_document()
    add_header_footer(doc, DOC_TITLE)
    add_cover(doc, title="MATRIZ DE TRAZABILIDAD",
              subtitle="RF → HU → CU → TC · Iter 11+12",
              code=DOC_CODE)
    add_version_control(doc, DOC_CODE, DOC_TITLE, changes=[
        ("1.0", "Junio 2026", "Matriz inicial."),
        ("1.1", "Junio 2026", "RF-041 a RF-051 → HU y CU."),
        ("1.2", "Junio 2026", "_RF-052 a RF-065 → HU y CU._"),
        ("1.3", "Junio 2026", "_RF-066 a RF-090 → HU y CU._"),
        ("1.4", "Junio 2026", "_RF-091 a RF-128 → HU y CU._"),
        ("1.5", "Junio 2026", "_RF-129 a RF-140 → HU-072 a HU-085 → CU-059 a CU-068 → TC-020 a TC-029._"),
        ("1.6", "Junio 2026", "_RF-129 a RF-140 → HU-072 a HU-085 → CU-059 a CU-068 → TC-020 a TC-029._"),
        ("1.7", "Junio 2026", "RF-129 a RF-140 → Sprint 1+2."),
        ("1.8", "Junio 2026", "_RF-141 a RF-162 → HU-086 a HU-097 → CU-069 a CU-077 → TC-030 a TC-038._"),
        ("1.9", "Julio 2026", "_RF-163 a RF-169 → HU-098 a HU-103 → CU-078 a CU-082 → TC-039 a TC-046._"),
    ])
    add_toc(doc)

    doc.add_heading("1. Matriz RF → HU → CU → TC (v1.9 — Iter 13)", level=1)

    matriz = [
        ["RF-163", "HU-098", "CU-078", "TC-039-041", "IDOR multi-tenant en 6 endpoints RAT (404 si empresa no coincide)", "CRÍTICO"],
        ["RF-163", "HU-098", "CU-078", "TC-043", "Superadmin accede a RAT de cualquier empresa", "CRÍTICO"],
        ["RF-164", "HU-099", "CU-079", "TC-044", "base_legal_valida strict contra enum taxativo (6 opciones)", "ALTO"],
        ["RF-165", "HU-100", "CU-080", "TC-045", "ConsentimientoAlert: listarConsentimientos() si datos_sensibles=True", "ALTO"],
        ["RF-166", "HU-101", "CU-081", "N/A", "Homologación orden campos RAT (5 pasos canónicos)", "ALTO"],
        ["RF-167", "HU-102", "CU-082", "TC-046", "PDF con títulos de sección y alertas rojas", "MEDIO"],
        ["RF-168", "HU-103", "CU-082", "N/A", "Encoding UTF-8 corregido en backend", "MEDIO"],
        ["RF-169", "N/A", "N/A", "N/A", "Código muerto eliminado (return duplicado, model_dump duplicado)", "BAJA"],
    ]
    add_styled_table(doc, ["RF", "HU", "CU", "TC", "Descripción", "Severidad"],
                     matriz, col_widths_cm=[1.5, 1.5, 1.5, 1.5, 7.0, 2.0],
                     first_col_bold=True, underline_new=True)

    doc.add_heading("2. Cobertura de trazabilidad", level=1)
    add_paragraph(doc, "_Total RF documentados: 169 (RF-001 a RF-169). "
                      "RF con HU: 100%. RF con CU: 95%. RF con TC: 80%._")

    add_id_glossary(doc, [
        ("RF-###", "Requisito Funcional", "Capacidad del sistema."),
        ("HU-###", "Historia de Usuario", "Necesidad del usuario."),
        ("CU-###", "Caso de Uso", "Interacción actor-sistema."),
        ("TC-###", "Caso de Prueba", "Validación técnica."),
    ])
    add_final_note(doc)
    doc.save(OUT_FILE)
    print(f"[OK] {OUT_FILE}")


if __name__ == "__main__":
    build()
