"""
Build 04 — Arquitectura y Modelo de Datos del Asesor v1.0
=========================================================
Genera: docs/documentacion_oficial_asesorgpt/_regen/04_Arquitectura_Datos_AsesorCustodio_v1.0.docx
Código: ASES-DOC-04

Incluye 4 figuras Mermaid (C4 contexto, C4 contenedor, secuencia RAG, ER).
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
OUT_FILE = os.path.join(REGEN_DIR, "04_Arquitectura_Datos_AsesorCustodio_v1.0.docx")
os.makedirs(REGEN_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)

DOC_CODE = "ASES-DOC-04"
DOC_TITLE = "Arquitectura y Modelo de Datos"


def build():
    doc = new_document()
    add_header_footer(doc, DOC_TITLE)
    add_cover(doc,
              title="ARQUITECTURA Y MODELO DE DATOS",
              subtitle="C4, secuencia RAG, decisiones arquitectonicas y ER del Asesor",
              code=DOC_CODE)
    add_version_control(doc, DOC_CODE, DOC_TITLE, changes=[
        ("1.0", "Junio 2026",
         "Creacion inicial del documento a partir de la auditoría previa AUDITORIA_ASES_V1.0."),
    ])
    add_toc(doc)
    fig_counter = [0]
    tab_counter = [0]

    # 1. Resumen arquitectónico
    doc.add_heading("1. Resumen arquitectónico", level=1)
    add_paragraph(doc,
        "El modulo Custodio Asesor se integra a la arquitectura existente de Custodio "
        "RAT Manager como un nuevo subsistema RAG. Reutiliza la capa de autenticacion "
        "(JWT), auditoría (audit_log), almacenamiento (SQLite/PostgreSQL) y servicios "
        "IA (MiniMax como provider principal, OpenAI como fallback).")

    # 2. C4 Nivel 1 - Contexto
    doc.add_heading("2. Diagrama de contexto (C4 Nivel 1)", level=1)
    c4_context = """
flowchart LR
    U(["Usuario autenticado"]) -->|POST /asesor/ask| SYS["Custodio RAT Manager<br/>(Backend FastAPI)"]
    SA(["Superadmin"]) -->|POST /admin/asesor/index| SYS
    SA -->|GET /admin/asesor/stats| SYS
    SYS -->|prompt + contexto| LLM{{"LLM externo<br/>MiniMax / OpenAI"}}
    SYS -->|embeddings| EMB{{"Embeddings API<br/>MiniMax / OpenAI"}}
    SYS -->|audit_log| DB[("PostgreSQL / SQLite")]
"""
    add_figure(doc, c4_context,
        "Diagrama C4 Nivel 1 - Contexto del Asesor.",
        ASSETS_DIR, fig_counter, name_hint="c4_asesor_context",
        width_inches=6.5)

    # 3. C4 Nivel 2 - Contenedores
    doc.add_heading("3. Diagrama de contenedores (C4 Nivel 2)", level=1)
    c4_container = """
flowchart TB
    subgraph FE["Frontend Next.js"]
        UIX["/asesor<br/>AsesorChat + SourceChip"]
    end
    subgraph BE["Backend FastAPI serverless"]
        ASR["asesor_service<br/>orquestador RAG"]
        IDX["asesor_indexer"]
        RTV["asesor_retriever"]
        EMB["asesor_embedder"]
        CHK["asesor_chunker"]
    end
    subgraph DB["PostgreSQL / SQLite"]
        TBL[("asesor_chunks<br/>+ embeddings JSON")]
    end
    subgraph EXT["Servicios externos"]
        LLM{{"LLM<br/>MiniMax / OpenAI"}}
        EMBAPI{{"Embeddings<br/>MiniMax / OpenAI"}}
    end
    UIX -->|POST /asesor/ask| ASR
    ASR --> RTV
    ASR --> LLM
    RTV -->|cosine top-k| TBL
    IDX --> CHK
    IDX --> EMB
    IDX -->|upsert| TBL
    EMB --> EMBAPI
"""
    add_figure(doc, c4_container,
        "Diagrama C4 Nivel 2 - Contenedores del Asesor.",
        ASSETS_DIR, fig_counter, name_hint="c4_asesor_container",
        width_inches=6.8)

    # 4. Secuencia RAG
    doc.add_heading("4. Diagrama de secuencia RAG", level=1)
    seq_rag = """
sequenceDiagram
    autonumber
    actor U as Usuario
    participant FE as Frontend
    participant BE as asesor_service
    participant EMB as embedder
    participant RT as retriever
    participant DB as BD
    participant LLM as LLM
    U->>FE: Escribe pregunta
    FE->>BE: POST /asesor/ask {question}
    BE->>EMB: embed_query(question)
    EMB-->>BE: query_embedding
    BE->>RT: retrieve(query_embedding, top_k=5)
    RT->>DB: SELECT * FROM asesor_chunks
    DB-->>RT: rows
    RT-->>BE: top-k chunks con score
    BE->>LLM: prompt(question + chunks)
    LLM-->>BE: respuesta + citas
    BE->>DB: audit_log(entidad=asesor, accion=consulta)
    BE-->>FE: {answer, sources}
    FE-->>U: render + chips
"""
    add_figure(doc, seq_rag,
        "Secuencia retrieve-augment-generate del Asesor.",
        ASSETS_DIR, fig_counter, name_hint="seq_asesor_rag",
        width_inches=6.8)

    # 5. Decisiones arquitectonicas
    doc.add_heading("5. Decisiones arquitectonicas (AD-ASES)", level=1)
    add_caption_table(doc, "Decisiones arquitectonicas del Asesor", tab_counter, "Tabla")
    add_styled_table(doc,
        ["ID", "Decision", "Justificacion"],
        [
            ["AD-ASES-12", "Almacenar embeddings como JSON en SQLite/PostgreSQL (v1.0); migrar a pgvector en Neon para v1.1+ si el tamano crece.",
             "Simplifica el deploy serverless y evita dependencias nativas en Vercel; suficiente para < 10k chunks."],
            ["AD-ASES-13", "Reusar MINIMAX_API_KEY como provider principal de embeddings; fallback automático a OpenAI.",
             "Reuso del LLM ya contratado; minimiza costo incremental."],
            ["AD-ASES-14", "Cosine similarity con threshold 0.7 + top-k=5.",
             "Buen balance precision/recall para corpus pequenos de tipo legal."],
            ["AD-ASES-15", "Solo usuarios autenticados pueden usar el Asesor (no público en v1.0).",
             "Compliance: las consultas deben quedar en el audit_log de la empresa."],
            ["AD-ASES-16", "Documentacion del Asesor en carpeta propia con theme verde-dorado.",
             "Separacion visual y conceptual respecto al producto padre."],
            ["AD-ASES-17", "8 documentos consolidados + matriz (no 14 separados).",
             "Reduce overhead de mantenimiento sin perder trazabilidad."],
        ],
        col_widths_cm=[3.0, 7.5, 7.09], first_col_bold=True)

    # 6. Modelo de datos
    doc.add_heading("6. Modelo de datos (ER)", level=1)
    er_asesor = """
erDiagram
    ASESOR_CHUNKS {
        int id PK
        string source
        string source_type
        string title
        text content
        string content_hash UK
        int chunk_index
        int token_count
        text embedding_json
        text chunk_metadata
        datetime created_at
        datetime updated_at
    }
"""
    add_figure(doc, er_asesor,
        "Diagrama ER del modulo Asesor.",
        ASSETS_DIR, fig_counter, name_hint="er_asesor",
        width_inches=6.5)

    add_caption_table(doc, "Tabla asesor_chunks - descripción de columnas", tab_counter, "Tabla")
    add_styled_table(doc,
        ["Columna", "Tipo", "Descripción"],
        [
            ["id", "INTEGER PK", "Identificador unico autoincremental."],
            ["source", "STRING", "Ruta absoluta del archivo fuente (ej: data/asesor_corpus/ley/ley_21719.md)."],
            ["source_type", "STRING", "Tipo: 'ley', 'manual', 'caso_uso', 'auditoría', 'otros'."],
            ["title", "STRING", "Titulo extraido del primer encabezado Markdown."],
            ["content", "TEXT", "Contenido del chunk (800 tokens aprox)."],
            ["content_hash", "STRING UK", "Hash sha256 del contenido para idempotencia."],
            ["chunk_index", "INTEGER", "Indice del chunk dentro del documento."],
            ["token_count", "INTEGER", "Cantidad estimada de tokens del chunk."],
            ["embedding_json", "TEXT", "Embedding serializado como JSON (lista de floats, 1536 dim)."],
            ["chunk_metadata", "TEXT", "JSON con file_size, indexed_at, etc."],
            ["created_at", "DATETIME", "Fecha de creacion."],
            ["updated_at", "DATETIME", "Fecha de ultima actualizacion."],
        ],
        col_widths_cm=[3.5, 3.5, 10.59], first_col_bold=True)

    # 7. Componentes del código
    doc.add_heading("7. Componentes del código", level=1)
    add_caption_table(doc, "Archivos clave del Asesor", tab_counter, "Tabla")
    add_styled_table(doc,
        ["Archivo", "Rol"],
        [
            ["backend/app/services/asesor_chunker.py", "Divide documentos en chunks (800 tokens, overlap 100)."],
            ["backend/app/services/asesor_embedder.py", "Genera embeddings (MiniMax + fallback OpenAI)."],
            ["backend/app/services/asesor_indexer.py", "Indexa el corpus: walk path, chunk, embed, upsert idempotente."],
            ["backend/app/services/asesor_retriever.py", "Recupera top-k chunks por cosine similarity."],
            ["backend/app/services/asesor_service.py", "Orquestador: embed query -> retrieve -> build prompt -> call LLM -> audit."],
            ["backend/app/routes/asesor.py", "POST /asesor/ask (público autenticado)."],
            ["backend/app/routes/admin_asesor.py", "POST /admin/asesor/index, GET /admin/asesor/stats, DELETE /admin/asesor/documents/{id}."],
            ["backend/app/models/asesor.py", "Modelo SQLAlchemy de la tabla asesor_chunks."],
            ["backend/app/schemas/asesor.py", "Schemas Pydantic (AsesorAskRequest, AsesorAskResponse, etc.)."],
            ["frontend-next/lib/asesor-api.ts", "Cliente HTTP del Asesor para el frontend."],
            ["frontend-next/app/(app)/asesor/page.tsx", "Pagina /asesor con el chat."],
        ],
        col_widths_cm=[7.0, 10.59], first_col_bold=True)

    # Apéndices
    add_open_questions(doc, [
        "縈igrar embeddings a pgvector en Neon en v1.1?",
        "縎e debe agregar cache de respuestas para consultas repetidas?",
    ])
    add_risks_appendix(doc, [
        ("R-01", "Costo computacional del cosine sobre todos los chunks sin índice vectorial", "Media"),
        ("R-02", "Tamano de la tabla asesor_chunks puede crecer mucho en produccion", "Media"),
    ])
    add_id_glossary(doc, [
        ("AD-ASES-NN", "Decision arquitectonica del Asesor", "Decision tecnica con contexto, opciones y justificacion."),
        ("C4", "Modelo de arquitectura C4", "Contexto, Contenedores, Componentes, Código (4 niveles)."),
    ])
    add_final_note(doc)

    doc.save(OUT_FILE)
    print(f"[OK] Generado: {OUT_FILE}")


if __name__ == "__main__":
    build()
