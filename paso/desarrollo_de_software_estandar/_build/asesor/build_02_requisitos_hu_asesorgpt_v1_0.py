"""
Build 02 — Requisitos e Historias de Usuario del Asesor v1.0
=============================================================
Genera: docs/documentacion_oficial_asesorgpt/_regen/02_Requisitos_HU_AsesorCustodio_v1.0.docx
Código: ASES-DOC-02
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
OUT_FILE = os.path.join(REGEN_DIR, "02_Requisitos_HU_AsesorCustodio_v1.0.docx")
os.makedirs(REGEN_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)

DOC_CODE = "ASES-DOC-02"
DOC_TITLE = "Requisitos e Historias de Usuario"


def build():
    doc = new_document()
    add_header_footer(doc, DOC_TITLE)
    add_cover(doc,
              title="REQUISITOS E HISTORIAS DE USUARIO",
              subtitle="RF, RNF y HU con criterios de aceptacion del Asesor",
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
        "Este documento consolida los requisitos funcionales (RF), no funcionales (RNF) "
        "y las historias de usuario (HU) del modulo Custodio Asesor (RAG). Cada RF se "
        "trazara contra al menos una HU y cada HU tendra criterios de aceptacion "
        "verificables. Los IDs siguen el formato ASES-NN segun la convencion del modulo.")

    # 2. Requisitos funcionales (RF)
    doc.add_heading("2. Requisitos funcionales (RF)", level=1)
    add_paragraph(doc, "Los siguientes requisitos funcionales son obligatorios para v1.0:")
    add_caption_table(doc, "Requisitos funcionales del Asesor v1.0", tab_counter, "Tabla")
    add_styled_table(doc,
        ["ID", "Prioridad", "Estado", "Descripción"],
        [
            ["RF-ASES-01", "Alta", "Implementado", "El sistema debe permitir consultar al Asesor mediante una interfaz de chat en /asesor."],
            ["RF-ASES-02", "Alta", "Implementado", "El sistema debe recuperar evidencia del corpus indexado antes de generar una respuesta (RAG)."],
            ["RF-ASES-03", "Alta", "Implementado", "El sistema debe citar explicitamente la fuente de cada afirmacion en formato [Fuente: nombre, seccion X]."],
            ["RF-ASES-04", "Alta", "Implementado", "El sistema debe indexar el corpus desde archivos .md y .txt, idempotente por hash sha256."],
            ["RF-ASES-05", "Alta", "Implementado", "El sistema debe registrar cada consulta en audit_log con entidad=asesor, accion=consulta."],
            ["RF-ASES-06", "Alta", "Implementado", "El sistema debe limitar el acceso a usuarios autenticados (no público en v1.0)."],
            ["RF-ASES-07", "Alta", "Implementado", "El sistema debe permitir al superadmin reindexar el corpus via POST /admin/asesor/index."],
            ["RF-ASES-08", "Alta", "Implementado", "El sistema debe permitir al superadmin consultar estadisticas del corpus via GET /admin/asesor/stats."],
            ["RF-ASES-09", "Alta", "Implementado", "El sistema debe permitir eliminar chunks del índice via DELETE /admin/asesor/documents/{id}."],
            ["RF-ASES-10", "Alta", "Implementado", "El sistema debe aplicar rate limit de 10/min en POST /asesor/ask (slowapi)."],
            ["RF-ASES-11", "Alta", "Implementado", "El sistema debe usar embeddings MiniMax con fallback automático a OpenAI si MiniMax no expone /v1/embeddings."],
            ["RF-ASES-12", "Alta", "Implementado", "El sistema debe usar cosine similarity con threshold min_similarity=0.7 para filtrar resultados."],
        ],
        col_widths_cm=[2.5, 2.0, 2.5, 10.59], first_col_bold=True)

    # 3. Requisitos no funcionales (RNF)
    doc.add_heading("3. Requisitos no funcionales (RNF)", level=1)
    add_caption_table(doc, "Requisitos no funcionales del Asesor v1.0", tab_counter, "Tabla")
    add_styled_table(doc,
        ["ID", "Categoría", "Descripción"],
        [
            ["RNF-ASES-01", "Rendimiento", "P95 de respuesta < 5 segundos en QA."],
            ["RNF-ASES-02", "Disponibilidad", "Servicio tolerante a fallos: si MiniMax falla, fallback a OpenAI; si no hay LLM, error 503."],
            ["RNF-ASES-03", "Seguridad", "Solo usuarios autenticados pueden usar el Asesor; consulta al audit_log incluye username y origen."],
            ["RNF-ASES-04", "Trazabilidad", "Toda consulta al Asesor debe quedar registrada con timestamp, fuentes citadas y provider usado."],
            ["RNF-ASES-05", "Mantenibilidad", "Código modular: chunker, embedder, indexer, retriever, service como servicios separados."],
        ],
        col_widths_cm=[3.0, 4.0, 10.59], first_col_bold=True)

    # 4. Historias de usuario (HU)
    doc.add_heading("4. Historias de usuario (HU)", level=1)
    add_caption_table(doc, "Historias de usuario del Asesor v1.0", tab_counter, "Tabla")
    add_styled_table(doc,
        ["ID", "Como (rol)", "Quiero", "Para", "Prioridad - Estado"],
        [
            ["US-ASES-01", "Como admin_empresa", "Quiero consultar al Asesor sobre la Ley 21.719 desde la plataforma",
             "Para resolver dudas operativas sin salir de la aplicacion", "P0 - Cerrado"],
            ["US-ASES-02", "Como usuario regular", "Quiero ver citas a las fuentes de cada respuesta",
             "Para validar que la información es correcta antes de usarla", "P0 - Cerrado"],
            ["US-ASES-03", "Como superadmin", "Quiero indexar el corpus desde la UI o API",
             "Para mantener actualizada la base de conocimiento del Asesor", "P0 - Cerrado"],
            ["US-ASES-04", "Como superadmin", "Quiero ver estadisticas del corpus (chunks, documentos, ultimo indexado)",
             "Para monitorear la cobertura del Asesor", "P0 - Cerrado"],
            ["US-ASES-05", "Como DPO", "Quiero que cada consulta quede registrada en audit_log",
             "Para evidencia de cumplimiento ante la APDP", "P0 - Cerrado"],
            ["US-ASES-06", "Como usuario", "Quiero un fallback al chat generico cuando el Asesor no encuentra info",
             "Para no quedar sin respuesta ante consultas fuera del corpus", "P1 - Cerrado"],
        ],
        col_widths_cm=[2.0, 3.5, 4.5, 4.5, 3.09], first_col_bold=True)

    # 5. Criterios de aceptacion por historia
    doc.add_heading("5. Criterios de aceptacion por historia", level=1)

    doc.add_heading("5.1 US-ASES-01 - Consultar al Asesor", level=2)
    add_bullet(doc, "Dado un usuario autenticado, cuando accede a /asesor, entonces ve una interfaz de chat con un campo de texto.")
    add_bullet(doc, "Cuando envia una pregunta, recibe una respuesta en menos de 5 segundos (P95).")
    add_bullet(doc, "La respuesta incluye al menos una cita a una fuente del corpus cuando hay cobertura.")

    doc.add_heading("5.2 US-ASES-02 - Ver citas a las fuentes", level=2)
    add_bullet(doc, "Cada respuesta muestra chips clicables con el nombre del documento fuente.")
    add_bullet(doc, "Al hacer click en un chip, se abre el documento (ruta local) o se muestra un modal con el fragmento citado.")
    add_bullet(doc, "Si no hay cobertura, se muestra mensaje explicito 'Sin información suficiente en el corpus'.")

    doc.add_heading("5.3 US-ASES-03 - Indexar el corpus", level=2)
    add_bullet(doc, "El superadmin accede a /admin/asesor/index (protegido por rol).")
    add_bullet(doc, "El sistema procesa los archivos nuevos o modificados y devuelve {indexed, skipped, errors}.")
    add_bullet(doc, "La operacion es idempotente: reindexar el mismo corpus no genera duplicados (usa hash sha256 por chunk).")

    doc.add_heading("5.4 US-ASES-04 - Ver estadisticas", level=2)
    add_bullet(doc, "El superadmin puede consultar GET /admin/asesor/stats.")
    add_bullet(doc, "La respuesta incluye: total_chunks, total_documents, chunks_por_source, ultimo_indexado.")

    doc.add_heading("5.5 US-ASES-05 - Auditoría de consultas", level=2)
    add_bullet(doc, "Cada consulta al /asesor/ask genera un registro en audit_log.")
    add_bullet(doc, "El registro incluye: username, question (truncado a 500 chars), sources (lista), top_score, provider, embedding_provider, latency_ms.")
    add_bullet(doc, "La accion queda con entidad=asesor, accion=consulta.")

    doc.add_heading("5.6 US-ASES-06 - Fallback al chat generico", level=2)
    add_bullet(doc, "Si ningun chunk supera min_similarity=0.7, el sistema retorna un mensaje de fallback.")
    add_bullet(doc, "El frontend muestra un banner 'El Asesor no encontro información. 緿eseas probar el chat generico?' con CTA.")
    add_bullet(doc, "El chat generico reusa el endpoint /ai/ask existente.")

    # 6. Trazabilidad RF -> HU
    doc.add_heading("6. Trazabilidad RF a HU", level=1)
    add_paragraph(doc,
        "Cada requisito funcional esta cubierto por al menos una historia de usuario. "
        "La trazabilidad detallada se mantiene en la matriz ASES-MTX.")
    add_caption_table(doc, "Trazabilidad RF-ASES a HU-ASES", tab_counter, "Tabla")
    add_styled_table(doc,
        ["Requisito", "Historia(s) que lo cubre(n)"],
        [
            ["RF-ASES-01", "US-ASES-01"],
            ["RF-ASES-02", "US-ASES-01, US-ASES-03"],
            ["RF-ASES-03", "US-ASES-02"],
            ["RF-ASES-04", "US-ASES-03"],
            ["RF-ASES-05", "US-ASES-05"],
            ["RF-ASES-06", "US-ASES-01"],
            ["RF-ASES-07", "US-ASES-03"],
            ["RF-ASES-08", "US-ASES-04"],
            ["RF-ASES-09", "US-ASES-03"],
            ["RF-ASES-10", "US-ASES-01"],
            ["RF-ASES-11", "US-ASES-01, US-ASES-03"],
            ["RF-ASES-12", "US-ASES-01, US-ASES-06"],
        ],
        col_widths_cm=[5.0, 12.59], first_col_bold=True)

    # Apéndices
    add_open_questions(doc, [
        "縀l Asesor debe permitir conversaciones multi-turn (memoria entre preguntas) en v1.1?",
        "緾ual es el costo máximo aceptable por consulta (embeddings + LLM)?",
        "緿ebe el Asesor sugerir acciones (botones) o solo entregar texto?",
    ])
    add_risks_appendix(doc, [
        ("R-01", "Alucinaciones del LLM sobre la ley", "Alta"),
        ("R-02", "Endpoint embeddings MiniMax no disponible", "Alta"),
        ("R-03", "Costos de embeddings por reindex excesivo", "Media"),
    ])
    add_id_glossary(doc, [
        ("RF-ASES-NN", "Requisito funcional del Asesor", "Capacidad obligatoria que el modulo debe entregar."),
        ("RNF-ASES-NN", "Requisito no funcional del Asesor", "Restriccion de calidad, rendimiento, seguridad u operacional."),
        ("US-ASES-NN", "Historia de usuario del Asesor", "Necesidad de un actor cubierta por uno o mas RF."),
    ])
    add_final_note(doc)

    doc.save(OUT_FILE)
    print(f"[OK] Generado: {OUT_FILE}")


if __name__ == "__main__":
    build()
