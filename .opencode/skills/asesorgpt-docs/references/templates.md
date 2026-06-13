# Templates reutilizables para documentos del Asesor

Snippets Python (python-docx + theme del Asesor) listos para copiar y adaptar.

---

## Plantilla base de un script de build

```python
"""
Build NN — <Nombre del documento> vX.Y
======================================
Genera: docs/documentacion_oficial_asesorgpt/NN_<Nombre>_AsesorCustodio_vX.Y.docx
"""
import os
import sys
_THIS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _THIS)
from _theme_asesorgpt import *
import _theme_asesorgpt
# _theme_asesorgpt.DOC_VERSION = "vX.Y"  # ya viene en "v1.0" por defecto

OUT_DIR = r"C:\Users\chelo\Desktop\RAT_opencode\docs\documentacion_oficial_asesorgpt"
ASSETS_DIR = os.path.join(OUT_DIR, "assets")
OUT_FILE = os.path.join(OUT_DIR, "NN_<Nombre>_AsesorCustodio_vX.Y.docx")
DOC_CODE = "ASES-DOC-NN"
DOC_TITLE = "<Título del documento>"


def build():
    doc = new_document()
    add_header_footer(doc, DOC_TITLE)
    add_cover(doc,
              title="<TÍTULO EN MAYÚSCULAS>",
              subtitle="<Subtítulo descriptivo>",
              code=DOC_CODE)
    add_version_control(doc, DOC_CODE, DOC_TITLE, changes=[
        ("1.0", "Junio 2026", "Creación inicial del documento."),
    ])
    add_toc(doc)
    fig_counter = [0]
    tab_counter = [0]

    # ============================================================
    # CUERPO DEL DOCUMENTO
    # ============================================================
    doc.add_heading("1. <Sección>", level=1)
    add_paragraph(doc, "<Texto introductorio>")

    # ============================================================
    # APÉNDICES OBLIGATORIOS
    # ============================================================
    add_open_questions(doc, [
        "<Pregunta abierta 1>",
        "<Pregunta abierta 2>",
    ])
    add_risks_appendix(doc, [
        ("R-01", "<Descripción>", "Alta"),
    ])
    add_id_glossary(doc, [
        ("RF-ASES-01", "<Nombre>", "<Descripción corta>"),
    ])
    add_final_note(doc)

    doc.save(OUT_FILE)
    print(f"[OK] Generado: {OUT_FILE}")


if __name__ == "__main__":
    build()
```

---

## Bloque: requisitos funcionales (RF)

```python
doc.add_heading("2. Requisitos funcionales", level=1)
add_paragraph(doc, "Los siguientes requisitos son obligatorios para v1.0:")

rf_rows = [
    ["RF-ASES-01", "Alta", "Pendiente",
     "El sistema debe permitir indexar documentos del corpus en formato Markdown y PDF."],
    ["RF-ASES-02", "Alta", "Pendiente",
     "El sistema debe responder consultas en menos de 5 segundos en el percentil 95."],
    # ...
]
add_caption_table(doc, "Requisitos funcionales del Asesor", tab_counter, "Tabla")
add_styled_table(doc,
                 ["ID", "Prioridad", "Estado", "Descripción"],
                 rf_rows,
                 col_widths_cm=[2.5, 2.0, 2.5, 10.59],
                 first_col_bold=True)
```

---

## Bloque: historias de usuario (US)

```python
doc.add_heading("3. Historias de usuario", level=1)

hu_rows = [
    ["US-ASES-01",
     "Como admin_empresa",
     "Quiero consultar al Asesor sobre la Ley 21.719",
     "Para resolver dudas operativas sin salir de la plataforma",
     "P0 · 100% · Cerrado"],
]
add_caption_table(doc, "Historias de usuario del Asesor", tab_counter, "Tabla")
add_styled_table(doc,
                 ["ID", "Como (rol)", "Quiero", "Para", "Prioridad · Cobertura · Estado"],
                 hu_rows,
                 col_widths_cm=[2.0, 3.0, 5.0, 4.0, 3.59],
                 first_col_bold=True)
```

---

## Bloque: criterios de aceptación (dentro de una US)

```python
doc.add_heading("3.1 US-ASES-01 — Consultar al Asesor", level=2)
add_bullet(doc, "Dado un usuario autenticado, cuando envía una pregunta, entonces recibe una respuesta en menos de 5 segundos.")
add_bullet(doc, "Dado que la respuesta supera el umbral de similitud, cuando se muestra al usuario, entonces incluye al menos 1 cita a la fuente.")
add_bullet(doc, "Dado que no hay documentos relevantes, cuando se responde, entonces se muestra un mensaje 'Sin información suficiente en el corpus'.")
```

---

## Bloque: caso de uso (CU)

```python
doc.add_heading("4.1 CU-ASES-01 — Consultar al Asesor", level=2)

add_kv_table(doc, [
    ("Nombre", "Consultar al Asesor"),
    ("Actores", "Usuario autenticado (admin_empresa, usuario, superadmin)"),
    ("Precondiciones", "Usuario autenticado · corpus indexado con al menos 1 documento"),
    ("Postcondiciones", "Consulta registrada en audit_log con fuentes citadas"),
])

doc.add_heading("Flujo principal", level=3)
add_numbered(doc, "El usuario accede a /asesor.")
add_numbered(doc, "El usuario escribe una pregunta en el chat.")
add_numbered(doc, "El sistema ejecuta retrieve() sobre asesor_chunks.")
add_numbered(doc, "El sistema construye el prompt con las top-k=5 fuentes.")
add_numbered(doc, "El LLM genera la respuesta.")
add_numbered(doc, "El sistema registra la consulta en audit_log y muestra la respuesta con chips de fuentes.")

doc.add_heading("Flujos alternativos", level=3)
add_warning(doc, "Sin cobertura",
            "Si ningún chunk supera min_similarity=0.7, se muestra mensaje de fallback al chat genérico (/ai/ask).")
```

---

## Bloque: diagrama C4 (contenedor)

```python
c4_container = """
flowchart TB
    subgraph FE["Frontend Next.js"]
        UIX["/asesor<br/>AsesorChat + SourceChip"]
    end
    subgraph BE["Backend FastAPI serverless"]
        ASR["asesor_service<br/>orquestador"]
        IDX["asesor_indexer"]
        RTV["asesor_retriever"]
        EMB["asesorEmbedder"]
    end
    subgraph DB["PostgreSQL + pgvector"]
        VEC[("asesor_chunks<br/>+ embeddings")]
    end
    subgraph EXT["Servicios externos"]
        LLM{{"LLM<br/>MiniMax / OpenAI"}}
    end
    UIX -->|POST /asesor/ask| ASR
    ASR --> RTV
    RTV -->|cosine top-k| VEC
    ASR -->|prompt + contexto| LLM
    IDX -->|embeddings| EMB
    IDX -->|upsert| VEC
"""
add_figure(doc, c4_container,
           "Diagrama C4 Nivel 2 — Contenedores del Asesor.",
           ASSETS_DIR, fig_counter, name_hint="c4_asesor_container",
           width_inches=6.8)
```

---

## Bloque: diagrama de secuencia RAG

```python
seq_rag = """
sequenceDiagram
    autonumber
    actor U as Usuario
    participant FE as Frontend
    participant BE as asesor_service
    participant RT as retriever
    participant VEC as pgvector
    participant LLM as LLM
    U->>FE: Escribe pregunta
    FE->>BE: POST /asesor/ask {question}
    BE->>RT: retrieve(query, top_k=5)
    RT->>VEC: cosine similarity
    VEC-->>RT: chunks con score
    RT-->>BE: top-k chunks
    BE->>LLM: prompt(question + chunks)
    LLM-->>BE: respuesta + citas
    BE->>BE: audit_log(entidad=asesor)
    BE-->>FE: {answer, sources}
    FE-->>U: render + chips
"""
add_figure(doc, seq_rag,
           "Secuencia retrieve-augment-generate del Asesor.",
           ASSETS_DIR, fig_counter, name_hint="seq_rag",
           width_inches=6.8)
```

---

## Bloque: modelo de datos (ER)

```python
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
        vector embedding
        json metadata
        datetime created_at
        datetime updated_at
    }
    ASESOR_QUERIES {
        int id PK
        string username
        text question
        json sources
        float top_score
        string provider
        datetime created_at
    }
    ASESOR_QUERIES ||--o{ ASESOR_CHUNKS : "citas"
"""
add_figure(doc, er_asesor,
           "Diagrama ER del módulo Asesor.",
           ASSETS_DIR, fig_counter, name_hint="er_asesor",
           width_inches=6.8)
```

---

## Bloque: API endpoint

```python
doc.add_heading("2.1 POST /asesor/ask", level=2)

add_kv_table(doc, [
    ("Método", "POST"),
    ("Ruta", "/asesor/ask"),
    ("Auth", "JWT Bearer (cookie httpOnly)"),
    ("Rate limit", "10/min (slowapi)"),
])

doc.add_heading("Request", level=3)
add_paragraph(doc, "Content-Type: application/json", italic=True)
add_styled_table(doc, ["Campo", "Tipo", "Requerido", "Descripción"],
                 [
                     ["question", "string", "Sí", "Pregunta del usuario (1-2000 chars)"],
                     ["context", "string", "No", "Contexto adicional del sistema"],
                 ],
                 col_widths_cm=[3.0, 2.0, 2.0, 10.59])

doc.add_heading("Response 200", level=3)
add_styled_table(doc, ["Campo", "Tipo", "Descripción"],
                 [
                     ["answer", "string", "Respuesta generada por el LLM"],
                     ["sources", "Source[]", "Array de fuentes citadas"],
                 ],
                 col_widths_cm=[3.0, 3.0, 11.59])

doc.add_heading("Errores", level=3)
add_styled_table(doc, ["Código", "Causa"],
                 [
                     ["401", "Token JWT inválido o expirado"],
                     ["429", "Rate limit excedido"],
                     ["503", "No hay LLM configurado (ni MINIMAX_API_KEY ni OPENAI_API_KEY)"],
                 ],
                 col_widths_cm=[2.0, 15.59])
```

---

## Bloque: backlog priorizado

```python
doc.add_heading("2. Backlog", level=1)

backlog = [
    ["DT-ASES-01", "P0", "Feature", "Pipeline de indexación con chunking jerárquico", "Cerrado"],
    ["DT-ASES-02", "P0", "Feature", "Endpoint /asesor/ask con retrieve-augment-generate", "Cerrado"],
    ["DT-ASES-03", "P0", "Feature", "Citas a fuentes en respuestas", "Cerrado"],
    ["DT-ASES-04", "P0", "Feature", "Endpoint admin /admin/asesor/index", "Cerrado"],
    ["DT-ASES-05", "P0", "Feature", "Auditoría de consultas en audit_log", "Cerrado"],
    ["DT-ASES-06", "P1", "Feature", "Streaming de respuestas vía SSE", "Pendiente"],
    ["DT-ASES-07", "P1", "Feature", "Reindex automático semanal", "Pendiente"],
    ["DT-ASES-08", "P2", "Feature", "Historial de conversaciones por usuario", "Pendiente"],
]
add_caption_table(doc, "Backlog del Asesor v1.0", tab_counter, "Tabla")
add_styled_table(doc,
                 ["ID", "Prioridad", "Tipo", "Título", "Estado"],
                 backlog,
                 col_widths_cm=[2.0, 1.8, 2.0, 9.0, 2.79],
                 first_col_bold=True)
```
