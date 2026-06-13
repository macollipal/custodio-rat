# Patrones de diagramas Mermaid para el Asesor

Patrones probados que renderizan correctamente con `mermaid-cli` (npx -y @mermaid-js/mermaid-cli@10.9.1).

---

## 1. C4 Nivel 1 — Contexto

```python
c4_context = """
flowchart TB
    subgraph Actores["Actores humanos"]
        U1([Superadmin])
        U2([Admin de empresa])
        U3([Usuario regular])
    end

    subgraph Asesor["Módulo Custodio Asesor (RAG)"]
        SYS[("Asesor<br/>Chat IA")]
    end

    subgraph Externos["Sistemas externos"]
        EXT1[(Neon PostgreSQL<br/>+ pgvector)]
        EXT2{{LLM<br/>MiniMax / OpenAI}}
    end

    U1 --> SYS
    U2 --> SYS
    U3 --> SYS

    SYS -->|Retrieve cosine| EXT1
    SYS -->|Prompt + LLM| EXT2
    SYS -->|Embeddings| EXT2
"""
```

---

## 2. C4 Nivel 2 — Contenedor

```python
c4_container = """
flowchart TB
    subgraph FE["Frontend Next.js (Vercel)"]
        P[("/asesor · AsesorChat")]
    end

    subgraph BE["Backend FastAPI serverless"]
        SVC["asesor_service"]
        IDX["asesor_indexer"]
        RTV["asesor_retriever"]
        EMB["asesor_embedder"]
    end

    subgraph DB["PostgreSQL + pgvector (Neon)"]
        TBL[("asesor_chunks")]
    end

    subgraph EXT["Servicios externos"]
        LLM{{"LLM<br/>MiniMax / OpenAI"}}
    end

    P -->|POST /asesor/ask| SVC
    P -->|POST /admin/asesor/index| IDX
    SVC --> RTV
    RTV -->|cosine top-k=5| TBL
    SVC -->|prompt+contexto| LLM
    IDX --> EMB
    IDX -->|upsert| TBL
"""
```

---

## 3. Secuencia — Retrieve-Augment-Generate

```python
seq_rag = """
sequenceDiagram
    autonumber
    actor U as Usuario
    participant FE as Frontend
    participant API as asesor_service
    participant RT as retriever
    participant EMB as embedder
    participant DB as pgvector
    participant LLM as LLM
    U->>FE: Escribe pregunta
    FE->>API: POST /asesor/ask {question}
    API->>EMB: embed(question)
    EMB-->>API: query_vector
    API->>RT: retrieve(query_vector, top_k=5)
    RT->>DB: ORDER BY embedding <=> $1 LIMIT 5
    DB-->>RT: chunks con score
    RT-->>API: top-k chunks
    API->>LLM: prompt(question + chunks)
    LLM-->>API: {answer, sources}
    API->>API: audit_log(entidad=asesor)
    API-->>FE: {answer, sources}
    FE-->>U: render + chips
"""
```

---

## 4. ER — Modelo de datos del Asesor

```python
er_asesor = """
erDiagram
    ASESOR_CHUNKS {
        int id PK
        string source "ruta o URL"
        string source_type "ley|manual|caso_uso|auditoria"
        string title "encabezado"
        text content "chunk text"
        string content_hash UK "sha256"
        int chunk_index
        int token_count
        vector embedding "vector(1536)"
        json metadata
        datetime created_at
        datetime updated_at
    }
    ASESOR_QUERIES {
        int id PK
        string username
        text question
        json sources "array de {source, score}"
        float top_score
        string provider "minimax|openai"
        string embedding_provider
        int latency_ms
        datetime created_at
    }
    AUDIT_LOG ||--o{ ASESOR_QUERIES : "registra"
"""
```

---

## 5. Flujo de indexación (flowchart)

```python
flow_index = """
flowchart LR
    A[Corpus MD/PDF] --> B[Chunker<br/>800 tokens + 100 overlap]
    B --> C[Embedder<br/>MiniMax / OpenAI]
    C --> D[Hash sha256]
    D -->|ya existe| E[Skip]
    D -->|nuevo| F[UPSERT<br/>asesor_chunks]
    F --> G[(pgvector)]
"""
```

---

## 6. Roadmap / Gantt simplificado

```python
gantt = """
gantt
    title Custodio Asesor — Roadmap
    dateFormat YYYY-MM-DD
    section Fase 0-1
    Auditoría + diseño      :done, a1, 2026-06-09, 3d
    section Fase 2-3
    Backend + Frontend      :active, a2, after a1, 7d
    section Fase 4-5
    Tests + Documentación   :a3, after a2, 5d
    section Fase 6-7
    Despliegue + Cierre     :a4, after a3, 4d
"""
```

---

## 7. Diagrama de decisión (graph)

```python
graph_provider = """
flowchart TD
    A[/asesor/ask] --> B{MINIMAX_API_KEY?}
    B -->|Sí| C{Tiene endpoint<br/>embeddings?}
    B -->|No| D{OPENAI_API_KEY?}
    C -->|Sí| E[Usar MiniMax embeddings]
    C -->|No| D
    D -->|Sí| F[Usar OpenAI embeddings]
    D -->|No| G[Error 503]
"""
```

---

## Tips de renderizado

- **Saltos de línea en etiquetas**: usar `<br/>` en lugar de `\n`.
- **Subgraphs con espacios**: envolver el nombre entre comillas: `subgraph FE["Frontend Next.js"]`.
- **Caret de foreign-key en ER**: `||--o{` (uno a cero-o-muchos), `||--||` (uno a uno), `}o--o{` (muchos a muchos).
- **Evitar caracteres especiales** en etiquetas: usar `["texto"]` para escapar.
- **Vista flowchart vs sequence**: `flowchart TB/LR` para procesos, `sequenceDiagram` para interacciones temporales, `erDiagram` para datos, `gantt` para cronogramas.

---

## Convención de nombres para `name_hint`

El `name_hint` se usa para el cache de PNG y el nombre del archivo:

| Diagrama | `name_hint` |
|----------|-------------|
| C4 contexto Asesor | `c4_asesor_context` |
| C4 contenedor Asesor | `c4_asesor_container` |
| Secuencia RAG | `seq_asesor_rag` |
| Secuencia indexación | `seq_asesor_index` |
| ER Asesor | `er_asesor` |
| Flujo indexación | `flow_asesor_index` |
| Roadmap | `gantt_asesor` |
| Decisión embeddings | `graph_asesor_provider` |
