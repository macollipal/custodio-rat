"""
Build 05 — API y Backlog del Asesor v1.0
=========================================
Genera: docs/documentacion_oficial_asesorgpt/_regen/05_API_Backlog_AsesorCustodio_v1.0.docx
Código: ASES-DOC-05
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
OUT_FILE = os.path.join(REGEN_DIR, "05_API_Backlog_AsesorCustodio_v1.0.docx")
os.makedirs(REGEN_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)

DOC_CODE = "ASES-DOC-05"
DOC_TITLE = "API y Backlog"


def build():
    doc = new_document()
    add_header_footer(doc, DOC_TITLE)
    add_cover(doc,
              title="API Y BACKLOG",
              subtitle="Endpoints REST y backlog priorizado del Asesor",
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
        "El Asesor expone 4 endpoints REST: 1 público (consulta) y 3 de administracion "
        "(index, stats, delete). Todos requieren autenticacion JWT excepto los de admin "
        "que ademas requieren rol superadmin.")

    # 2. Endpoints publicos
    doc.add_heading("2. Endpoints publicos", level=1)

    doc.add_heading("2.1 POST /asesor/ask", level=2)
    add_kv_table(doc, [
        ("Metodo", "POST"),
        ("Ruta", "/asesor/ask"),
        ("Auth", "JWT Bearer (cookie httpOnly)"),
        ("Rate limit", "10/min (slowapi)"),
        ("Descripción", "Consulta al Asesor con RAG. Retorna respuesta + fuentes citadas."),
    ])
    add_caption_table(doc, "POST /asesor/ask - Request", tab_counter, "Tabla")
    add_styled_table(doc,
        ["Campo", "Tipo", "Requerido", "Descripción"],
        [
            ["question", "string", "Si", "Pregunta del usuario (1-2000 chars)."],
            ["context", "string", "No", "Contexto adicional del sistema (e.g. empresa activa)."],
        ],
        col_widths_cm=[3.0, 2.0, 2.0, 10.59])
    add_caption_table(doc, "POST /asesor/ask - Response 200", tab_counter, "Tabla")
    add_styled_table(doc,
        ["Campo", "Tipo", "Descripción"],
        [
            ["answer", "string", "Respuesta generada por el LLM."],
            ["sources", "Source[]", "Array de fuentes citadas (max 5)."],
            ["provider", "string", "'minimax' o 'openai' segun quien respondio."],
            ["embedding_provider", "string", "'minimax' u 'openai' segun quien embebio la query."],
            ["latency_ms", "int", "Latencia total de la operacion."],
        ],
        col_widths_cm=[3.0, 3.0, 11.59])
    add_caption_table(doc, "POST /asesor/ask - Errores", tab_counter, "Tabla")
    add_styled_table(doc,
        ["Código", "Causa"],
        [
            ["401", "Token JWT invalido o expirado."],
            ["429", "Rate limit excedido (10/min)."],
            ["503", "No hay LLM configurado (ni MINIMAX_API_KEY ni OPENAI_API_KEY)."],
        ],
        col_widths_cm=[2.0, 15.59])

    # 3. Endpoints admin
    doc.add_heading("3. Endpoints de administracion", level=1)

    doc.add_heading("3.1 POST /admin/asesor/index", level=2)
    add_kv_table(doc, [
        ("Auth", "JWT Bearer + rol superadmin"),
        ("Descripción", "Indexa o actualiza el corpus. Idempotente por hash sha256."),
    ])
    add_styled_table(doc,
        ["Campo", "Tipo", "Requerido", "Descripción"],
        [["paths", "string[]", "No", "Lista de rutas a indexar. Si vacio, usa ASESOR_CORPUS_PATH."],
         ["force", "bool", "No", "Si true, elimina chunks previos del source antes de reindexar (default false)."]],
        col_widths_cm=[3.0, 2.0, 2.0, 10.59])

    doc.add_heading("3.2 GET /admin/asesor/stats", level=2)
    add_kv_table(doc, [
        ("Auth", "JWT Bearer + rol superadmin"),
        ("Descripción", "Retorna métricas del corpus indexado."),
    ])
    add_styled_table(doc,
        ["Campo", "Tipo", "Descripción"],
        [
            ["total_chunks", "int", "Cantidad total de chunks en el índice."],
            ["total_documents", "int", "Cantidad de documentos fuente unicos."],
            ["chunks_por_source", "object", "Mapa source -> count de chunks."],
            ["ultimo_indexado", "datetime|null", "Fecha del ultimo chunk indexado."],
            ["provider", "string", "'minimax' o 'openai' segun API key activa."],
        ],
        col_widths_cm=[4.0, 3.0, 10.59])

    doc.add_heading("3.3 DELETE /admin/asesor/documents/{chunk_id}", level=2)
    add_kv_table(doc, [
        ("Auth", "JWT Bearer + rol superadmin"),
        ("Descripción", "Elimina un chunk del índice. Registra accion=delete en audit_log."),
    ])
    add_styled_table(doc,
        ["Código", "Causa"],
        [
            ["200", "Chunk eliminado correctamente."],
            ["404", "Chunk no encontrado."],
        ],
        col_widths_cm=[2.0, 15.59])

    # 4. Backlog priorizado
    doc.add_heading("4. Backlog priorizado", level=1)
    add_caption_table(doc, "Backlog del Asesor v1.0", tab_counter, "Tabla")
    add_styled_table(doc,
        ["ID", "Prioridad", "Tipo", "Titulo", "Estado"],
        [
            ["DT-ASES-01", "P0", "Feature", "Pipeline de indexacion con chunking jerarquico", "Cerrado"],
            ["DT-ASES-02", "P0", "Feature", "Endpoint /asesor/ask con retrieve-augment-generate", "Cerrado"],
            ["DT-ASES-03", "P0", "Feature", "Citas a fuentes en respuestas", "Cerrado"],
            ["DT-ASES-04", "P0", "Feature", "Endpoint admin /admin/asesor/index", "Cerrado"],
            ["DT-ASES-05", "P0", "Feature", "Auditoría de consultas en audit_log", "Cerrado"],
            ["DT-ASES-06", "P1", "Feature", "Streaming de respuestas via SSE", "Pendiente"],
            ["DT-ASES-07", "P1", "Feature", "Reindex automático semanal (cron externo)", "Pendiente"],
            ["DT-ASES-08", "P2", "Feature", "Historial de conversaciones por usuario", "Pendiente"],
            ["DT-ASES-09", "P2", "Feature", "Soporte de PDFs con OCR", "Pendiente"],
            ["DT-ASES-10", "P2", "Feature", "Re-ranking con cross-encoder", "Pendiente"],
        ],
        col_widths_cm=[2.5, 2.0, 2.0, 7.5, 3.59], first_col_bold=True)

    # 5. Sprints sugeridos
    doc.add_heading("5. Sprints sugeridos", level=1)
    add_caption_table(doc, "Planificación por sprints", tab_counter, "Tabla")
    add_styled_table(doc,
        ["Sprint", "Items", "Entregable"],
        [
            ["v1.0 (cerrado)", "DT-ASES-01 a DT-ASES-05", "MVP funcional con corpus indexado, RAG y auditoría."],
            ["v1.1 (siguiente)", "DT-ASES-06, DT-ASES-07", "SSE + reindex automático."],
            ["v2.0 (futuro)", "DT-ASES-08 a DT-ASES-10", "Historial, PDFs y re-ranking."],
        ],
        col_widths_cm=[4.0, 5.0, 8.59], first_col_bold=True)

    # Apéndices
    add_open_questions(doc, [
        "緿ebe haber un endpoint DELETE en bulk (por source)?",
        "緾uando se debe invalidar el cache de respuestas?",
    ])
    add_risks_appendix(doc, [
        ("R-01", "Alucinaciones del LLM sobre la ley", "Alta"),
        ("R-02", "Endpoint embeddings MiniMax no disponible", "Alta"),
    ])
    add_id_glossary(doc, [
        ("EP-ASES-NN", "Endpoint del Asesor", "Ruta HTTP del modulo Asesor."),
        ("DT-ASES-NN", "Item de backlog del Asesor", "Feature, bug o tarea del backlog del modulo."),
    ])
    add_final_note(doc)

    doc.save(OUT_FILE)
    print(f"[OK] Generado: {OUT_FILE}")


if __name__ == "__main__":
    build()
