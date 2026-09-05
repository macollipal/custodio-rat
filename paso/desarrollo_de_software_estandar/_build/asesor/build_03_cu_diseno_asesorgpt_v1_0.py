"""
Build 03 — Casos de Uso y Diseño Funcional del Asesor v1.0
============================================================
Genera: docs/documentacion_oficial_asesorgpt/_regen/03_CU_Diseno_AsesorCustodio_v1.0.docx
Código: ASES-DOC-03
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
OUT_FILE = os.path.join(REGEN_DIR, "03_CU_Diseno_AsesorCustodio_v1.0.docx")
os.makedirs(REGEN_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)

DOC_CODE = "ASES-DOC-03"
DOC_TITLE = "Casos de Uso y Diseño Funcional"


def build():
    doc = new_document()
    add_header_footer(doc, DOC_TITLE)
    add_cover(doc,
              title="CASOS DE USO Y DISENO FUNCIONAL",
              subtitle="CU, pantallas, flujos y reglas de negocio del Asesor",
              code=DOC_CODE)
    add_version_control(doc, DOC_CODE, DOC_TITLE, changes=[
        ("1.0", "Junio 2026",
         "Creacion inicial del documento a partir de la auditoría previa AUDITORIA_ASES_V1.0."),
    ])
    add_toc(doc)
    fig_counter = [0]
    tab_counter = [0]

    # 1. Actores
    doc.add_heading("1. Actores", level=1)
    add_paragraph(doc, "Los actores que interactuan con el Asesor son:")
    add_caption_table(doc, "Actores del Asesor", tab_counter, "Tabla")
    add_styled_table(doc,
        ["ID", "Actor", "Descripción"],
        [
            ["AC-ASES-01", "Usuario autenticado (admin_empresa, usuario, superadmin)", "Realiza consultas al Asesor desde /asesor."],
            ["AC-ASES-02", "Superadmin", "Indexa y mantiene el corpus; consulta estadisticas."],
            ["AC-ASES-03", "Sistema de IA externo", "Genera embeddings (MiniMax/OpenAI) y respuestas (LLM)."],
        ],
        col_widths_cm=[2.5, 6.0, 9.09], first_col_bold=True)

    # 2. Casos de uso
    doc.add_heading("2. Casos de uso", level=1)

    # 2.1 CU-ASES-01
    doc.add_heading("2.1 CU-ASES-01 - Consultar al Asesor", level=2)
    add_kv_table(doc, [
        ("Nombre", "Consultar al Asesor"),
        ("Actores", "Usuario autenticado (admin_empresa, usuario, superadmin)"),
        ("Precondiciones", "Usuario autenticado - corpus indexado con al menos 1 documento"),
        ("Postcondiciones", "Consulta registrada en audit_log con fuentes citadas"),
    ])
    doc.add_heading("Flujo principal", level=3)
    add_numbered(doc, "El usuario accede a la pagina /asesor.")
    add_numbered(doc, "El sistema muestra la interfaz de chat con un campo de entrada vacio.")
    add_numbered(doc, "El usuario escribe una pregunta (1-2000 caracteres) y presiona 'Enviar'.")
    add_numbered(doc, "El frontend hace POST /asesor/ask con la pregunta.")
    add_numbered(doc, "El backend ejecuta retrieve() sobre asesor_chunks usando cosine similarity.")
    add_numbered(doc, "El backend selecciona los top-k=5 chunks con score >= min_similarity=0.7.")
    add_numbered(doc, "El backend construye el prompt con la pregunta + contexto de los chunks.")
    add_numbered(doc, "El LLM (MiniMax u OpenAI) genera la respuesta.")
    add_numbered(doc, "El sistema registra la consulta en audit_log y muestra la respuesta con chips de fuentes.")
    doc.add_heading("Flujos alternativos", level=3)
    add_warning(doc, "Sin cobertura",
        "Si ningun chunk supera min_similarity=0.7, se muestra mensaje de fallback al chat generico (/ai/ask).")

    # 2.2 CU-ASES-02
    doc.add_heading("2.2 CU-ASES-02 - Ver citas a las fuentes", level=2)
    add_kv_table(doc, [
        ("Nombre", "Ver citas a las fuentes"),
        ("Actores", "Usuario autenticado"),
        ("Precondiciones", "Respuesta del Asesor incluye sources con al menos 1 item"),
        ("Postcondiciones", "El usuario puede abrir el documento o ver el fragmento citado"),
    ])
    add_numbered(doc, "La respuesta del Asesor renderiza chips por cada source.")
    add_numbered(doc, "Al hacer click en un chip, se abre el documento o un modal con el fragmento.")
    add_numbered(doc, "El modal muestra: nombre del documento, seccion, score de similitud y excerpt del chunk.")

    # 2.3 CU-ASES-03
    doc.add_heading("2.3 CU-ASES-03 - Indexar el corpus (admin)", level=2)
    add_kv_table(doc, [
        ("Nombre", "Indexar el corpus"),
        ("Actores", "Superadmin"),
        ("Precondiciones", "Corpus existe en ASESOR_CORPUS_PATH - usuario con rol superadmin"),
        ("Postcondiciones", "Chunks nuevos indexados, duplicados omitidos por hash"),
    ])
    add_numbered(doc, "El superadmin accede a /admin/asesor (UI) o hace POST /admin/asesor/index (API).")
    add_numbered(doc, "El sistema lista archivos .md/.txt en el corpus path.")
    add_numbered(doc, "Por cada archivo: chunking -> embeddings -> upsert en asesor_chunks (idempotente por sha256).")
    add_numbered(doc, "El sistema retorna {indexed, skipped, errors, duration_ms}.")
    add_numbered(doc, "El sistema registra la operacion en audit_log con accion=index.")

    # 2.4 CU-ASES-04
    doc.add_heading("2.4 CU-ASES-04 - Ver estadisticas del corpus", level=2)
    add_kv_table(doc, [
        ("Nombre", "Ver estadisticas del corpus"),
        ("Actores", "Superadmin"),
        ("Precondiciones", "Usuario con rol superadmin"),
        ("Postcondiciones", "El sistema retorna métricas del corpus"),
    ])
    add_numbered(doc, "El superadmin accede a GET /admin/asesor/stats.")
    add_numbered(doc, "El sistema retorna {total_chunks, total_documents, chunks_por_source, ultimo_indexado, provider}.")

    # 2.5 CU-ASES-05
    doc.add_heading("2.5 CU-ASES-05 - Eliminar chunk del índice", level=2)
    add_kv_table(doc, [
        ("Nombre", "Eliminar chunk del índice"),
        ("Actores", "Superadmin"),
        ("Precondiciones", "Chunk existe en asesor_chunks"),
        ("Postcondiciones", "Chunk eliminado, accion registrada en audit_log"),
    ])
    add_numbered(doc, "El superadmin hace DELETE /admin/asesor/documents/{chunk_id}.")
    add_numbered(doc, "El sistema elimina el chunk y registra accion=delete en audit_log.")

    # 3. Mapa de pantallas
    doc.add_heading("3. Mapa de pantallas", level=1)
    add_caption_table(doc, "Pantallas del modulo Asesor", tab_counter, "Tabla")
    add_styled_table(doc,
        ["Ruta", "Acceso", "Propósito"],
        [
            ["/asesor", "Auth requerido", "Chat del Asesor con historial en sesión."],
            ["/admin/asesor", "superadmin", "Panel de indexacion y estadisticas del corpus."],
        ],
        col_widths_cm=[4.0, 4.0, 9.59], first_col_bold=True)

    # 4. Reglas de negocio
    doc.add_heading("4. Reglas de negocio", level=1)
    add_caption_table(doc, "Reglas de negocio del Asesor", tab_counter, "Tabla")
    add_styled_table(doc,
        ["ID", "Regla", "Origen"],
        [
            ["RN-ASES-01", "Solo usuarios autenticados pueden usar el Asesor.", "AD-ASES-15"],
            ["RN-ASES-02", "Toda respuesta del Asesor debe incluir al menos 1 cita cuando hay cobertura.", "RF-ASES-03"],
            ["RN-ASES-03", "Si no hay cobertura, el sistema debe retornar mensaje explicito (no inventar).", "US-ASES-02"],
            ["RN-ASES-04", "La operacion de indexacion es idempotente por hash sha256 del contenido.", "RF-ASES-04"],
            ["RN-ASES-05", "El rate limit del endpoint /asesor/ask es 10/min por IP+usuario.", "RF-ASES-10"],
            ["RN-ASES-06", "Si MiniMax embeddings falla, fallback automático a OpenAI.", "RNF-ASES-02"],
            ["RN-ASES-07", "Cada consulta al Asesor queda registrada en audit_log con entidad=asesor.", "RF-ASES-05"],
        ],
        col_widths_cm=[2.5, 9.0, 6.09], first_col_bold=True)

    # 5. Wireframe conceptual del chat
    doc.add_heading("5. Wireframe conceptual del chat", level=1)
    add_paragraph(doc,
        "La pantalla /asesor presenta un chat vertical con burbujas diferenciadas "
        "(usuario a la derecha, Asesor a la izquierda). Cada respuesta del Asesor "
        "muestra, debajo del texto, una fila de chips con las fuentes citadas. "
        "Un campo de entrada fijo en la parte inferior acepta preguntas de hasta 2000 chars.")

    # Apéndices
    add_open_questions(doc, [
        "緿ebe el Asesor soportar adjuntos (PDFs subidos por el usuario) en v1.1?",
        "緾ual es la frecuencia de reindex automático si se implementa en v1.1?",
    ])
    add_risks_appendix(doc, [
        ("R-01", "Alucinaciones del LLM sobre la ley", "Alta"),
        ("R-02", "Endpoint embeddings MiniMax no disponible", "Alta"),
    ])
    add_id_glossary(doc, [
        ("CU-ASES-NN", "Caso de uso del Asesor", "Interaccion actor-sistema con flujo principal y alternativos."),
        ("RN-ASES-NN", "Regla de negocio del Asesor", "Restriccion que el sistema debe respetar siempre."),
    ])
    add_final_note(doc)

    doc.save(OUT_FILE)
    print(f"[OK] Generado: {OUT_FILE}")


if __name__ == "__main__":
    build()
