# Auditoría Previa — Custodio Asesor (RAG) v1.0

**Fecha:** 09 de Junio de 2026
**Producto:** Custodio Asesor (módulo RAG de Custodio RAT Manager)
**Versión auditada:** N/A (nace de cero)
**Versión objetivo:** v1.0
**Auditor:** Equipo de Desarrollo — Custodio
**Estado:** EN CURSO

---

## 1. Propósito de la auditoría

Esta auditoría documenta la **creación desde cero** del módulo **Custodio Asesor (RAG)** como feature de la plataforma Custodio RAT Manager. A diferencia de auditorías incrementales (v1.0 → v1.1 → ...), esta parte de la **no existencia** del módulo y deja constancia de:

1. Los componentes del producto padre que el Asesor va a integrar.
2. Las decisiones arquitectónicas adoptadas para el RAG.
3. El alcance documental (8 documentos + matriz) y su plan de generación.
4. Los vacíos de información que requieren resolución previa a la implementación.

---

## 2. Inventario del producto padre (Custodio RAT Manager)

Auditoría del estado actual de la plataforma para identificar puntos de integración con el Asesor.

### 2.1 Stack tecnológico (confirmado)

| Capa | Tecnología | Versión |
|------|-----------|---------|
| Backend | FastAPI | 0.115.5 |
| Backend | Uvicorn | 0.32.1 |
| ORM | SQLAlchemy | 2.0.36 |
| Validación | Pydantic | 2.10.3 |
| Auth | python-jose (JWT) | 3.3.0 |
| Hashing | passlib + bcrypt | 1.7.4 / 4.0.1 |
| PDF | ReportLab | 4.2.5 |
| Rate limit | slowapi | 0.1.9 |
| DB prod | PostgreSQL (Neon) | — |
| DB local | SQLite | — |
| Frontend | Next.js | 16.2 |
| Frontend | React | 19 |
| Frontend | TypeScript | — |
| Frontend | Tailwind CSS | v4 |
| Tests | pytest + httpx | 8.3.4 / 0.27.2 |
| E2E | Playwright | — |
| Deploy | Vercel (serverless) | — |

### 2.2 Servicios IA existentes (a sustituir/ampliar)

| Endpoint | Archivo | Estado |
|----------|---------|--------|
| `POST /ai/ask` | `backend/app/routes/ai.py` | Funcional, **sin RAG** |

**Hallazgo:** El endpoint actual solo envía un `SYSTEM_PROMPT` al LLM, sin retrieval. Es candidato natural a ser **extendido** con un endpoint paralelo `POST /asesor/ask` (no reemplazo) que añada retrieval sobre el corpus.

### 2.3 Módulos del producto padre que el Asesor referenciará

| Módulo | Razón de referencia |
|--------|---------------------|
| `ai.py` | Proveer LLM (MiniMax / OpenAI) compartido |
| `audit_service.py` | Registrar cada consulta del Asesor con trazabilidad |
| `core/config.py` | Añadir `ASESOR_*` settings |
| `core/security.py` | Reusar `get_current_user` para auth |
| `models/asesor.py` (nuevo) | Persistir chunks del corpus |
| `database/database.py` | Reusar `get_db` |
| Frontend: `lib/api.ts` | Cliente HTTP compartido |

---

## 3. Decisiones arquitectónicas del Asesor

### AD-12 — Vector store: pgvector en Neon

**Contexto:** Necesidad de almacenar embeddings del corpus de la Ley 21.719 + manuales.

**Opciones evaluadas:**
- (A) pgvector en Neon ✅ **(elegida)**: sin servicio externo, backups incluidos, escala OK para v1.0
- (B) ChromaDB local: no soporta Vercel serverless por FS efímero
- (C) Pinecone/Qdrant cloud: añade costo y variable extra

**Decisión:** pgvector.
**Implicaciones:**
- Nueva migración `003_asesor_chunks.py` con `CREATE EXTENSION IF NOT EXISTS vector;`
- Índices: `ivfflat (embedding vector_cosine_ops)` con `lists=100` (ajustable)
- Dimensión embedding: **1536** (text-embedding-3-small por defecto)

### AD-13 — Embeddings: MiniMax con fallback OpenAI

**Contexto:** Ya existe `MINIMAX_API_KEY` como provider principal del chat.

**Decisión:** Reusar `MINIMAX_API_KEY` para embeddings. Si MiniMax no expone endpoint de embeddings, fallback automático a OpenAI (`OPENAI_API_KEY`).

**Implicaciones:**
- Settings: `MINIMAX_EMBEDDING_MODEL`, `OPENAI_EMBEDDING_MODEL`
- Servicio `asesor_embedder.py` con detección automática de provider

### AD-14 — Corpus inicial

**Contexto:** El usuario instruyó que el corpus arranque con "la ley y manuales de uso de custodio".

**Decisión:**
- **Ley 21.719**: texto del PDF oficial en `paso/ley_21719/Ley-21719_13-DIC-2024.pdf` (extraído en `paso/ley_21719/ley_21719_texto.txt`)
- **Manuales de uso**:
  - `docs/MANUAL_USUARIO_FUNCIONAL.md`
  - `docs/casos_de_uso/CASO_01..06_*.md`
  - `MANUAL_PRUEBAS_CUSTODIO.md`
  - `que_es_rat.md`
- Copia canónica en `backend/asesor_corpus/` (gitignored)

### AD-15 — Acceso: solo autenticados

**Contexto:** Compliance. Los datos de auditoría deben quedar en el log de la empresa.

**Decisión:** Solo usuarios autenticados pueden usar el chat. Excluido el formulario ARCO público.

**Implicaciones:** Reusar `get_current_user` de `routes/deps.py`.

### AD-16 — Documentación en `documentacion_oficial_asesorgpt/`

**Contexto:** El usuario quiere mantener la documentación del Asesor **separada** del producto padre.

**Decisión:** Carpeta independiente `docs/documentacion_oficial_asesorgpt/`, theme propio (`_theme_asesorgpt.py`), prefijos `ASES-DOC-NN`, scripts en `paso/desarrollo_de_software_estandar/_build/asesor/`.

### AD-17 — Consolidación documental: 8 docs + matriz

**Contexto:** El usuario preguntó si 14 docs es excesivo para un módulo.

**Decisión:** Plan C — **8 documentos consolidados** (por afinidad temática) + matriz de trazabilidad.

| Doc | Fusión |
|-----|--------|
| ASES-DOC-01 | Visión + Alcance |
| ASES-DOC-02 | Requisitos + HU |
| ASES-DOC-03 | CU + Diseño funcional |
| ASES-DOC-04 | Arquitectura + Modelo de datos |
| ASES-DOC-05 | API + Backlog |
| ASES-DOC-06 | Plan de QA |
| ASES-DOC-07 | Despliegue + Manual técnico |
| ASES-DOC-08 | Módulo Asesor (spec dedicado) |
| ASES-MTX | Matriz de trazabilidad |

### AD-18 — Skill OpenCode dedicada

**Contexto:** Mantener consistencia documental en futuras iteraciones.

**Decisión:** Crear skill `.opencode/skills/asesorgpt-docs/SKILL.md` con workflow de mantenimiento.

---

## 4. Hallazgos de la auditoría

### 4.1 Componentes nuevos a crear

| Componente | Tipo | Carpeta |
|------------|------|---------|
| `asesor_chunker.py` | Servicio | `backend/app/services/` |
| `asesor_embedder.py` | Servicio | `backend/app/services/` |
| `asesor_indexer.py` | Servicio | `backend/app/services/` |
| `asesor_retriever.py` | Servicio | `backend/app/services/` |
| `asesor_service.py` | Servicio | `backend/app/services/` |
| `asesor.py` | Rutas | `backend/app/routes/` |
| `admin_asesor.py` | Rutas | `backend/app/routes/` |
| `asesor.py` | Modelos | `backend/app/models/` |
| `asesor.py` | Schemas | `backend/app/schemas/` |
| `asesor-api.ts` | Cliente HTTP | `frontend-next/lib/` |
| `AsesorChat.tsx` | Componente | `frontend-next/components/asesor/` |
| `SourceChip.tsx` | Componente | `frontend-next/components/asesor/` |
| `page.tsx` | Página | `frontend-next/app/(app)/asesor/` |
| 8 scripts de build | Scripts | `paso/.../_build/asesor/` |
| 1 matriz | Script | `paso/.../_build/asesor/` |
| 1 theme | Theme | `paso/.../_build/asesor/` |
| 1 skill | Skill | `.opencode/skills/asesorgpt-docs/` |

### 4.2 Componentes a modificar

| Componente | Cambio |
|------------|--------|
| `backend/requirements.txt` | +`pgvector`, `tiktoken`, `pypdf`, `numpy` |
| `backend/app/core/config.py` | +Settings `ASESOR_*`, `MINIMAX_EMBEDDING_MODEL`, `OPENAI_EMBEDDING_MODEL` |
| `backend/app/main.py` | +Registro de routers `asesor` y `admin_asesor` |
| `backend/app/services/audit_service.py` | +Acción `entidad="asesor"` para auditoría de consultas |
| `frontend-next/components/layout/Sidebar.tsx` | +Entrada "Asesor" en navegación |
| `frontend-next/context/AppContext.tsx` | +Estado del modo Asesor (opcional v1.1) |

### 4.3 Componentes NO modificados

- `auth.py`, `rats.py`, `breaches.py`, `consentimientos.py`, `eipd.py`, etc.: el Asesor solo **consume** lo que ya existe.
- `audit_service.py` mantiene su API actual; el Asesor solo añade un valor nuevo de `entidad`.

---

## 5. Vacíos de información (a resolver antes de implementar)

Estos puntos quedan abiertos para iteración posterior:

1. **Endpoint de embeddings MiniMax**: ¿está disponible públicamente? Si no, fallback OpenAI documentado.
2. **Reindex automático**: ¿cron externo (Vercel Cron) o scheduler interno (no compatible con serverless)?
3. **Streaming de respuestas**: ¿SSE en v1.0 o queda para v1.1?
4. **Tamaño máximo del corpus**: ¿límite en tokens, número de archivos o ambos?
5. **Persistencia de conversaciones**: ¿el Asesor guarda historial? Si sí, ¿cuánto tiempo?
6. **Rate limit por usuario**: ¿compartido con `/ai/ask` o independiente?
7. **Branding del frontend**: ¿logo SVG propio del Asesor (verde-dorado) o se usa emoji/icono simple?
8. **Soporte multi-idioma**: ¿solo español o también inglés?
9. **Re-ranking**: ¿usar cross-encoder o basta con cosine top-k=5?
10. **Métricas de calidad**: ¿qué KPI medimos (precision@k, faithfulness, answer relevancy)?

---

## 6. Riesgos identificados

| ID | Riesgo | Severidad | Mitigación |
|----|--------|-----------|------------|
| R-01 | Embeddings MiniMax no disponibles | Alta | Fallback OpenAI documentado y testeado |
| R-02 | Alucinaciones del LLM sobre la ley | Alta | Prompt con cita obligatoria + threshold de similitud |
| R-03 | Costos de embeddings | Media | Indexación idempotente por hash (solo chunks nuevos) |
| R-04 | pgvector no activado en Neon prod | Alta | Verificar `CREATE EXTENSION` antes del primer indexado |
| R-05 | Documentación desincronizada con código | Media | AUDIT_GUIDE.md + skill OpenCode dedicada |
| R-06 | Corpus desactualizado si cambia la ley | Media | Job de reindex semanal + alerta en stats |
| R-07 | Latencia alta por embedding + LLM | Media | Caché por hash + top-k=5 + temperature=0.2 |
| R-08 | Sobreindexación (muchos chunks irrelevantes) | Baja | Chunking jerárquico 800 tokens + min_similarity=0.7 |
| R-09 | Pérdida de detalle vs 14 docs originales | Baja | Spec maestro ASES-DOC-08 absorbe profundidad |
| R-10 | Cambios en la API rompen el frontend | Baja | Tipos TypeScript sincronizados en `lib/asesor-api.ts` |

---

## 7. Plan de ejecución (referencia)

| Fase | Entregable | Estado |
|------|-----------|--------|
| 0 | Auditoría previa (este doc) | ✅ |
| 1 | Diseño técnico: schema + settings + contratos | Pendiente |
| 2 | Backend: servicios, rutas, modelos, migración | Pendiente |
| 3 | Frontend: `/asesor`, `AsesorChat`, citas | Pendiente |
| 4 | Tests pytest + e2e Playwright | Pendiente |
| 5 | Documentación: 8 .docx + 8 scripts + matriz + theme + skill | Pendiente |
| 6 | Despliegue: local → QA → prod | Pendiente |
| 7 | Auditoría de cierre + cobertura RF→HU→CU→TC | Pendiente |

---

## 8. Conclusión de la auditoría

El módulo **Custodio Asesor (RAG)** es viable técnicamente y se integra limpiamente en Custodio RAT Manager sin afectar componentes existentes. La decisión de **separar la documentación** (`documentacion_oficial_asesorgpt/`) y **consolidar a 8 documentos** mantiene la profesionalidad del estándar documental sin sobredocumentar un módulo.

**Recomendación:** PROCEDER con la implementación siguiendo el plan de 7 fases.

---

*Auditoría controlada — actualizar al cierre de cada fase.*
