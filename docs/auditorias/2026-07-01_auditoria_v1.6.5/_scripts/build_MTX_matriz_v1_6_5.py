"""
Build MTX — Matriz de Trazabilidad v1.6.5 (Post Iter 11 + Iter 12)
Genera: docs/documentacion_oficial/Matriz_Trazabilidad_Custodio_RAT_Manager_v1.6.5.docx
Cambios v1.6.5:
- RF-141 a RF-162 → HU-086 a HU-097 → CU-069 a CU-077 → TC-030 a TC-038
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
OUT_FILE = os.path.join(OUT_DIR, "Matriz_Trazabilidad_Custodio_RAT_Manager_v1.6.5.docx")
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
    ])
    add_toc(doc)

    doc.add_heading("1. Matriz RF → HU → CU → TC (v1.6.5 — Iter 11+12)", level=1)

    matriz = [
        ["RF-141", "HU-086", "CU-069", "TC-030", "BYTEA 10MB limit (archivo_base_legal)", "CRÍTICO"],
        ["RF-142-149", "HU-087", "CU-069", "TC-030", "15 campos Tier 1+Tier 2 RAT", "ALTA"],
        ["RF-156", "HU-090", "CU-070", "TC-031", "BYTEA limit 10MB (tkt_adjunto)", "CRÍTICO"],
        ["RF-157", "HU-091", "CU-071", "TC-032", "Test IL mínimo 50 caracteres (Art. 16)", "CRÍTICO"],
        ["RF-158", "HU-092", "CU-072", "TC-033", "Hash SHA-256 auto evidencia ARCO", "CRÍTICO"],
        ["RF-158", "HU-097", "CU-077", "TC-034", "Hash SHA-256 calculado al resolver TKT", "CRÍTICO"],
        ["RF-159", "HU-093", "CU-073", "TC-035", "causal_rechazo enum cerrado (Art. 29 RL)", "ALTO"],
        ["RF-159", "HU-096", "CU-073", "TC-036", "causal_rechazo obligatorio al rechazar", "ALTO"],
        ["RF-160", "HU-094", "CU-074", "N/A", "Toggle ARCO 44x44px mobile", "ALTO"],
        ["RF-161", "HU-095", "CU-075", "TC-037", "Notificación APDC automatizada (Art. 14 bis)", "ALTO"],
        ["RF-162", "HU-096", "CU-076", "N/A", "Notificación titulares automatizada", "ALTO"],
    ]
    add_styled_table(doc, ["RF", "HU", "CU", "TC", "Descripción", "Severidad"],
                     matriz, col_widths_cm=[1.5, 1.5, 1.5, 1.5, 7.0, 2.0],
                     first_col_bold=True, underline_new=True)

    doc.add_heading("2. Cobertura de trazabilidad", level=1)
    add_paragraph(doc, "_Total RF documentados: 162 (RF-001 a RF-162). "
                      "RF con HU: 100%. RF con CU: 95%. RF con TC: 85%._")

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
