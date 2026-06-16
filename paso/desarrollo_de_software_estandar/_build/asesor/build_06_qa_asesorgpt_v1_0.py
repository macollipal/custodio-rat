"""
Build 06 — Plan de QA del Asesor v1.0
======================================
Genera: docs/documentacion_oficial_asesorgpt/_regen/06_QA_AsesorCustodio_v1.0.docx
Código: ASES-DOC-06
"""
import os
import sys
_THIS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _THIS)
from _theme_asesorgpt import *
import _theme_asesorgpt
_theme_asesorgpt.DOC_VERSION = "v1.0"

OUT_DIR = r"C:\Users\chelo\Desktop\RAT_opencode\docs\documentacion_oficial_asesorgpt"
REGEN_DIR = os.path.join(OUT_DIR, "_regen")
ASSETS_DIR = os.path.join(REGEN_DIR, "assets")
OUT_FILE = os.path.join(REGEN_DIR, "06_QA_AsesorCustodio_v1.0.docx")
os.makedirs(REGEN_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)

DOC_CODE = "ASES-DOC-06"
DOC_TITLE = "Plan de QA"


def build():
    doc = new_document()
    add_header_footer(doc, DOC_TITLE)
    add_cover(doc,
              title="PLAN DE QA",
              subtitle="Estrategia, casos de prueba y criterios de salida del Asesor",
              code=DOC_CODE)
    add_version_control(doc, DOC_CODE, DOC_TITLE, changes=[
        ("1.0", "Junio 2026",
         "Creacion inicial del documento a partir de la auditoría previa AUDITORIA_ASES_V1.0."),
    ])
    add_toc(doc)
    fig_counter = [0]
    tab_counter = [0]

    # 1. Introduccion
    doc.add_heading("1. Introduccion", level=1)
    add_paragraph(doc,
        "Este documento define la estrategia de pruebas y los casos de prueba (TC) del "
        "modulo Custodio Asesor. Los TC estan organizados por componente (chunker, "
        "embedder, retriever, service) y por endpoint. Cubre pruebas unitarias, de "
        "integracion, E2E y manuales.")

    # 2. Estrategia
    doc.add_heading("2. Estrategia de pruebas", level=1)
    doc.add_heading("2.1 Piramide de pruebas", level=2)
    add_bullet(doc, "Unitarios: mínimo 70% de cobertura de los servicios asesor_*.py.")
    add_bullet(doc, "Integracion: 1 happy path + 2 edge cases por endpoint.")
    add_bullet(doc, "E2E: 1 flujo critico (consulta completa) y 1 flujo de admin (index).")
    add_bullet(doc, "Manual: checklist de 5 items por release.")
    doc.add_heading("2.2 Datos de prueba", level=2)
    add_bullet(doc, "Corpus de QA: subset de la Ley 21.719 (5 articulos) + 1 manual de uso.")
    add_bullet(doc, "Consultas precargadas: 10 preguntas con respuesta esperada conocida.")
    add_bullet(doc, "Usuarios de prueba: superadmin (index), admin_empresa (consulta), usuario (consulta).")

    # 3. Casos de prueba
    doc.add_heading("3. Casos de prueba (TC)", level=1)

    doc.add_heading("3.1 TC de indexacion", level=2)
    add_caption_table(doc, "TC de indexacion", tab_counter, "Tabla")
    add_styled_table(doc,
        ["ID", "Escenario", "Resultado esperado"],
        [
            ["TC-ASES-01", "Indexar corpus vacio", "Retorna indexed=0, skipped=0, errors=[\"No hay archivos para indexar\"]."],
            ["TC-ASES-02", "Indexar 1 archivo .md nuevo", "Retorna indexed>=1, errors=[]. Chunk aparece en stats."],
            ["TC-ASES-03", "Reindexar mismo archivo", "Retorna indexed=0, skipped=N (los chunks ya estaban)."],
            ["TC-ASES-04", "Indexar archivo con formato no soportado (.docx)", "Es ignorado silenciosamente (soporta .md, .txt)."],
            ["TC-ASES-05", "Indexar con MiniMax caido", "Fallback a OpenAI o error explicito si tampoco hay OpenAI."],
        ],
        col_widths_cm=[2.5, 5.0, 10.09], first_col_bold=True)

    doc.add_heading("3.2 TC de retrieval", level=2)
    add_caption_table(doc, "TC de retrieval", tab_counter, "Tabla")
    add_styled_table(doc,
        ["ID", "Escenario", "Resultado esperado"],
        [
            ["TC-ASES-06", "Consulta con chunks relevantes", "Retorna top-k=5 con score >= 0.7."],
            ["TC-ASES-07", "Consulta sin cobertura (off-topic)", "Retorna lista vacia; asesor_service retorna mensaje de fallback."],
            ["TC-ASES-08", "Chunks con embedding corrupto (JSON invalido)", "Se omiten sin romper la query."],
        ],
        col_widths_cm=[2.5, 5.0, 10.09], first_col_bold=True)

    doc.add_heading("3.3 TC de endpoint /asesor/ask", level=2)
    add_caption_table(doc, "TC de /asesor/ask", tab_counter, "Tabla")
    add_styled_table(doc,
        ["ID", "Escenario", "Resultado esperado"],
        [
            ["TC-ASES-09", "Usuario autenticado + pregunta valida", "200, respuesta con sources y provider."],
            ["TC-ASES-10", "Sin token JWT", "401."],
            ["TC-ASES-11", "11 consultas en 1 minuto (rate limit)", "La 11ma retorna 429."],
            ["TC-ASES-12", "Pregunta vacia", "422 (validacion Pydantic)."],
            ["TC-ASES-13", "Sin LLM configurado", "503 con mensaje 'No hay LLM configurado'."],
        ],
        col_widths_cm=[2.5, 5.0, 10.09], first_col_bold=True)

    doc.add_heading("3.4 TC de endpoint /admin/asesor/index", level=2)
    add_caption_table(doc, "TC de /admin/asesor/index", tab_counter, "Tabla")
    add_styled_table(doc,
        ["ID", "Escenario", "Resultado esperado"],
        [
            ["TC-ASES-14", "superadmin indexa corpus", "200, retorna indexed/skipped/errors."],
            ["TC-ASES-15", "admin_empresa intenta indexar", "403 (solo superadmin)."],
            ["TC-ASES-16", "Index con force=true", "Elimina chunks previos del source antes de reindexar."],
        ],
        col_widths_cm=[2.5, 5.0, 10.09], first_col_bold=True)

    doc.add_heading("3.5 TC de endpoint /admin/asesor/stats", level=2)
    add_caption_table(doc, "TC de /admin/asesor/stats", tab_counter, "Tabla")
    add_styled_table(doc,
        ["ID", "Escenario", "Resultado esperado"],
        [
            ["TC-ASES-17", "superadmin consulta stats", "200, retorna {total_chunks, total_documents, chunks_por_source, ultimo_indexado, provider}."],
            ["TC-ASES-18", "usuario intenta consultar", "403."],
        ],
        col_widths_cm=[2.5, 5.0, 10.09], first_col_bold=True)

    doc.add_heading("3.6 TC de frontend (Playwright)", level=2)
    add_caption_table(doc, "TC de frontend (Playwright)", tab_counter, "Tabla")
    add_styled_table(doc,
        ["ID", "Escenario", "Resultado esperado"],
        [
            ["TC-ASES-19", "Login + navegar a /asesor", "Se muestra el chat con input vacio."],
            ["TC-ASES-20", "Escribir pregunta y enviar", "Aparece burbuja de respuesta con chips de fuentes."],
            ["TC-ASES-21", "Click en chip de fuente", "Se abre modal con el fragmento citado."],
        ],
        col_widths_cm=[2.5, 5.0, 10.09], first_col_bold=True)

    # 4. Criterios de salida
    doc.add_heading("4. Criterios de salida (release)", level=1)
    add_bullet(doc, "100% de los TC P0 ejecutados y pasando.")
    add_bullet(doc, ">= 90% de los TC P1 ejecutados y pasando.")
    add_bullet(doc, "Cobertura unitaria >= 70% en servicios asesor_*.py.")
    add_bullet(doc, "Tasa de respuestas con cita >= 95% (medida sobre 50 consultas de muestra).")
    add_bullet(doc, "Latencia P95 < 5 segundos en QA.")
    add_bullet(doc, "0 errores criticos en audit_log durante smoke test de 1 hora.")

    # 5. Métricas de calidad RAG
    doc.add_heading("5. Métricas de calidad RAG", level=1)
    add_paragraph(doc,
        "El Asesor introduce métricas especificas que no aplican a sistemas CRUD "
        "tradicionales. Estas se monitorean de forma continua en el dashboard de QA:")
    add_caption_table(doc, "Métricas de calidad RAG", tab_counter, "Tabla")
    add_styled_table(doc,
        ["Métrica", "Definicion", "Objetivo"],
        [
            ["Citation recall", "% de respuestas que incluyen >= 1 fuente citada", ">= 95%"],
            ["Answer relevance", "Score promedio de similitud pregunta-respuesta (manual)", ">= 0.7"],
            ["Hallucination rate", "% de respuestas con afirmaciones no soportadas por el corpus", "< 5%"],
            ["Refusal rate", "% de consultas donde el Asesor responde 'no encontre información'", "<= 20%"],
        ],
        col_widths_cm=[4.0, 8.0, 5.59], first_col_bold=True)

    # Apéndices
    add_open_questions(doc, [
        "緾omo medir 'hallucination rate' de forma automatizada en CI?",
        "緿ebe haber un benchmark de preguntas canonicas con respuestas esperadas?",
    ])
    add_risks_appendix(doc, [
        ("R-01", "Cobertura unitaria insuficiente (< 70%) por falta de mocks de httpx", "Media"),
        ("R-02", "Tasa de alucinaciones variable entre proveedores LLM", "Media"),
    ])
    add_id_glossary(doc, [
        ("TC-ASES-NN", "Caso de prueba del Asesor", "Test case que valida un RF o flujo del Asesor."),
    ])
    add_final_note(doc)

    doc.save(OUT_FILE)
    print(f"[OK] Generado: {OUT_FILE}")


if __name__ == "__main__":
    build()
