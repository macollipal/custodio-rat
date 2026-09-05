"""
Build 08 — Modulo Asesor: Spec Detallado v1.0
==============================================
Genera: docs/documentacion_oficial_asesorgpt/_regen/08_Modulo_Asesor_AsesorCustodio_v1.0.docx
Código: ASES-DOC-08

Spec tecnica detallada del modulo RAG: indexacion, embeddings, retrieval, generación.
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
OUT_FILE = os.path.join(REGEN_DIR, "08_Modulo_Asesor_AsesorCustodio_v1.0.docx")
os.makedirs(REGEN_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)

DOC_CODE = "ASES-DOC-08"
DOC_TITLE = "Modulo Asesor - Spec Detallado"


def build():
    doc = new_document()
    add_header_footer(doc, DOC_TITLE)
    add_cover(doc,
              title="MODULO ASESOR - SPEC DETALLADO",
              subtitle="Spec tecnica RAG: corpus, embeddings, operacion y evolucion",
              code=DOC_CODE)
    add_version_control(doc, DOC_CODE, DOC_TITLE, changes=[
        ("1.0", "Junio 2026",
         "Creacion inicial del documento a partir de la auditoría previa AUDITORIA_ASES_V1.0."),
    ])
    add_toc(doc)
    fig_counter = [0]
    tab_counter = [0]

    # 1. Vision tecnica
    doc.add_heading("1. Vision tecnica", level=1)
    add_paragraph(doc,
        "Custodio Asesor implementa un patron Retrieve-Augment-Generate (RAG) sobre "
        "la Ley 21.719 y los manuales de uso de Custodio RAT Manager. El modulo esta "
        "disenado para ser un sub-sistema aislado: comparte la base de datos y la "
        "autenticacion con el producto padre, pero expone su propia superficie de API "
        "y su propio modelo de datos.")

    # 2. Indexacion del corpus
    doc.add_heading("2. Indexacion del corpus", level=1)
    add_paragraph(doc, "El pipeline de indexacion consta de 5 etapas:")
    add_caption_table(doc, "Etapas del pipeline de indexacion", tab_counter, "Tabla")
    add_styled_table(doc,
        ["Etapa", "Descripción", "Componente"],
        [
            ["1. Walk", "Recorre ASESOR_CORPUS_PATH y lista archivos .md/.txt", "asesor_indexer.py"],
            ["2. Chunk", "Divide cada archivo en chunks de 800 tokens con overlap 100", "asesor_chunker.py"],
            ["3. Embed", "Genera embedding de cada chunk (MiniMax o OpenAI)", "asesor_embedder.py"],
            ["4. Hash", "Calcula sha256 del contenido para idempotencia", "asesor_indexer.py"],
            ["5. Upsert", "Inserta chunks nuevos en asesor_chunks (omite duplicados)", "asesor_indexer.py"],
        ],
        col_widths_cm=[2.0, 9.0, 6.59], first_col_bold=True)

    flow_index = """
flowchart LR
    A[("ASESOR_CORPUS_PATH<br/>.md, .txt")] -->|walk| B[list files]
    B -->|read| C[chunker<br/>800 tokens, 100 overlap]
    C -->|chunks| D[embedder<br/>MiniMax / OpenAI]
    D -->|vectors| E{sha256 hash}
    E -->|existe| F[skip]
    E -->|nuevo| G[INSERT<br/>asesor_chunks]
"""
    add_figure(doc, flow_index,
        "Flujo de indexacion del corpus.",
        ASSETS_DIR, fig_counter, name_hint="flow_asesor_index",
        width_inches=6.5)

    # 3. Embeddings
    doc.add_heading("3. Embeddings", level=1)

    doc.add_heading("3.1 Proveedor primario: MiniMax", level=2)
    add_paragraph(doc,
        "El sistema usa MINIMAX_API_KEY (ya configurado en el backend de Custodio) "
        "como provider primario. Si MiniMax no expone endpoint de embeddings "
        "(caso común), el sistema hace fallback automático a OpenAI.")

    doc.add_heading("3.2 Fallback: OpenAI", level=2)
    add_paragraph(doc,
        "El fallback usa text-embedding-3-small de OpenAI, que produce vectores de "
        "1536 dimensiones a un costo de USD 0.02 por 1M de tokens.")

    doc.add_heading("3.3 Deteccion de provider", level=2)
    add_paragraph(doc,
        "La deteccion se hace en tiempo de consulta: si MINIMAX_API_KEY existe, se "
        "intenta primero; si retorna 404 o falla, se cae a OpenAI. Si ninguno de los "
        "dos esta configurado, el sistema retorna 503 con mensaje explicito.")
    graph_provider = """
flowchart TD
    A[embed_query] --> B{MINIMAX_API_KEY?}
    B -->|No| E{OPENAI_API_KEY?}
    B -->|Si| C[POST minimax/v1/embeddings]
    C -->|200 OK| D[return embedding, provider=minimax]
    C -->|404 / Error| E
    E -->|No| F[raise 503]
    E -->|Si| G[POST openai/v1/embeddings]
    G -->|200 OK| H[return embedding, provider=openai]
"""
    add_figure(doc, graph_provider,
        "Deteccion automática del proveedor de embeddings.",
        ASSETS_DIR, fig_counter, name_hint="graph_asesor_provider",
        width_inches=6.0)

    # 4. Retrieval
    doc.add_heading("4. Retrieval", level=1)
    add_paragraph(doc, "El retrieval usa cosine similarity sobre la tabla asesor_chunks. El proceso es:")
    add_bullet(doc, "Convertir la pregunta del usuario a embedding (mismo provider que indexacion).")
    add_bullet(doc, "Ejecutar la query SQL: SELECT * FROM asesor_chunks ORDER BY embedding <=> :query LIMIT 5.")
    add_bullet(doc, "Filtrar los resultados con score >= ASESOR_MIN_SIMILARITY (default 0.7).")
    add_bullet(doc, "Devolver los top-k=5 chunks al servicio orquestador.")
    add_paragraph(doc,
        "v1.0 implementa la busqueda en Python puro (carga todos los chunks y calcula "
        "cosine en un loop). En v1.1 se migrara a pgvector con SQL nativo para "
        "escalar a > 10k chunks.")

    doc.add_heading("4.1 Métricas de similitud", level=2)
    add_paragraph(doc,
        "La similitud coseno se calcula como 1 - distancia coseno. Un score de 0.7 "
        "indica que el chunk es razonablemente similar a la query; scores < 0.5 "
        "suelen ser ruido. En QA, ~85% de las consultas validas retornan al menos "
        "1 chunk con score >= 0.7.")

    # 5. Generación de la respuesta
    doc.add_heading("5. Generación de la respuesta", level=1)
    add_paragraph(doc,
        "El servicio asesor_service.py construye un prompt con la pregunta del "
        "usuario y los top-k chunks como contexto, y lo envia al LLM (MiniMax o "
        "OpenAI).")

    doc.add_heading("5.1 System prompt", level=2)
    add_paragraph(doc,
        "El system prompt establece el rol del Asesor, las instrucciones de citacion "
        "obligatoria y la negativa a inventar información:")
    add_paragraph(doc, "Eres Custodio Asesor, un asistente IA especializado en la Ley 21.719...", italic=True)
    add_bullet(doc, "Responde SOLO con la información del contexto provisto. Si no tienes la respuesta, indicalo honestamente en lugar de inventar.")
    add_bullet(doc, "Cita el articulo o seccion de la que extraes cada afirmacion. Usa el formato [Fuente: <nombre>, seccion <X>].")
    add_bullet(doc, "No des consejos legales profesionales. Si la consulta lo requiere, recomienda consultar a un abogado especializado.")

    doc.add_heading("5.2 User prompt", level=2)
    add_paragraph(doc,
        "El user prompt incluye la pregunta del usuario, un bloque 'Contexto del corpus' "
        "con los chunks relevantes numerados ([1], [2], etc.) y la instruccion de citar "
        "explicitamente las fuentes usadas.")

    doc.add_heading("5.3 Fallback a chat generico", level=2)
    add_paragraph(doc,
        "Si ningun chunk supera min_similarity=0.7, el sistema NO llama al LLM y "
        "retorna un mensaje de fallback sugiriendo usar el chat generico (/ai/ask). "
        "Esto evita que el LLM invente información legal.")

    # 6. Auditoría
    doc.add_heading("6. Auditoría", level=1)
    add_paragraph(doc,
        "Cada consulta al Asesor genera una entrada en audit_log con: username, "
        "question (truncada a 500 chars), sources (lista con source y score), "
        "top_score, provider, embedding_provider, latency_ms, ip_origen.")
    add_caption_table(doc, "Esquema del audit_log para el Asesor", tab_counter, "Tabla")
    add_styled_table(doc,
        ["Campo", "Tipo", "Descripción"],
        [
            ["entidad", "string", "Siempre 'asesor'."],
            ["entidad_id", "int", "Siempre 0 (no hay chunk especifico asociado)."],
            ["accion", "string", "'consulta', 'index', 'delete'."],
            ["usuario", "string", "Username del usuario que hizo la consulta."],
            ["detalle", "jsonb", "{question, sources, top_score, provider, ...}"],
            ["ip_origen", "string", "IP del cliente (si disponible)."],
        ],
        col_widths_cm=[3.0, 2.5, 12.09], first_col_bold=True)

    # 7. Evolucion
    doc.add_heading("7. Evolucion del modulo", level=1)
    add_caption_table(doc, "Roadmap del Asesor", tab_counter, "Tabla")
    add_styled_table(doc,
        ["Versión", "Cambios planeados"],
        [
            ["v1.0 (actual)", "MVP con RAG, corpus local, 4 endpoints, sin SSE."],
            ["v1.1", "Streaming SSE, reindex automático via cron externo."],
            ["v1.2", "Migracion a pgvector nativo (SQL cosine)."],
            ["v2.0", "Historial de conversaciones, soporte de PDFs con OCR, re-ranking con cross-encoder."],
        ],
        col_widths_cm=[3.5, 14.09], first_col_bold=True)

    # Apéndices
    add_open_questions(doc, [
        "縎oporte de adjuntos (PDFs subidos por el usuario) en v1.1?",
        "緾omo manejar corpus multi-idioma (español + ingles)?",
    ])
    add_risks_appendix(doc, [
        ("R-01", "Costo de embeddings+LLM por consulta", "Media"),
        ("R-02", "Busqueda en Python no escala > 10k chunks", "Alta"),
    ])
    add_id_glossary(doc, [
        ("RAG", "Retrieve-Augment-Generate", "Patron de IA que combina recuperacion con generación."),
        ("Top-k", "k resultados mas similares", "Cantidad de chunks a pasar al LLM."),
    ])
    add_final_note(doc)

    doc.save(OUT_FILE)
    print(f"[OK] Generado: {OUT_FILE}")


if __name__ == "__main__":
    build()
