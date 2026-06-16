"""
Build 07 — Despliegue y Manual Técnico del Asesor v1.0
=======================================================
Genera: docs/documentacion_oficial_asesorgpt/_regen/07_Despliegue_Tecnico_AsesorCustodio_v1.0.docx
Código: ASES-DOC-07
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
OUT_FILE = os.path.join(REGEN_DIR, "07_Despliegue_Tecnico_AsesorCustodio_v1.0.docx")
os.makedirs(REGEN_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)

DOC_CODE = "ASES-DOC-07"
DOC_TITLE = "Despliegue y Manual Técnico"


def build():
    doc = new_document()
    add_header_footer(doc, DOC_TITLE)
    add_cover(doc,
              title="DESPLIEGUE Y MANUAL TECNICO",
              subtitle="Setup, variables de entorno, troubleshooting y operacion del Asesor",
              code=DOC_CODE)
    add_version_control(doc, DOC_CODE, DOC_TITLE, changes=[
        ("1.0", "Junio 2026",
         "Creacion inicial del documento a partir de la auditoría previa AUDITORIA_ASES_V1.0."),
    ])
    add_toc(doc)
    fig_counter = [0]
    tab_counter = [0]

    # 1. Requisitos previos
    doc.add_heading("1. Requisitos previos", level=1)
    add_bullet(doc, "Python 3.9+ (recomendado 3.11).")
    add_bullet(doc, "PostgreSQL 14+ con la extension pgvector instalada (Neon ya la soporta).")
    add_bullet(doc, "Acceso a MiniMax o OpenAI para embeddings + LLM.")
    add_bullet(doc, "Backend de Custodio RAT Manager funcionando (puerto 8002 en local).")

    # 2. Variables de entorno
    doc.add_heading("2. Variables de entorno", level=1)
    add_paragraph(doc,
        "Las variables del Asesor usan el prefijo ASESOR_*. Se anaden al archivo "
        "backend/.env (local) o a las variables de Vercel (produccion).")
    add_caption_table(doc, "Variables de entorno del Asesor", tab_counter, "Tabla")
    add_styled_table(doc,
        ["Variable", "Tipo", "Default", "Descripción"],
        [
            ["ASESOR_CORPUS_PATH", "string", "data/asesor_corpus", "Carpeta raiz del corpus indexable."],
            ["ASESOR_CHUNK_SIZE", "int", "800", "Tamano de chunk en tokens."],
            ["ASESOR_CHUNK_OVERLAP", "int", "100", "Overlap entre chunks consecutivos."],
            ["ASESOR_TOP_K", "int", "5", "Cantidad de chunks a recuperar por consulta."],
            ["ASESOR_MIN_SIMILARITY", "float", "0.7", "Threshold de cosine similarity (0-1)."],
            ["ASESOR_LLM_MAX_TOKENS", "int", "1000", "Max tokens de la respuesta del LLM."],
            ["ASESOR_LLM_TEMPERATURE", "float", "0.3", "Temperatura del LLM (0=determinista, 1=creativo)."],
            ["MINIMAX_EMBEDDING_MODEL", "string", "embo-01", "Modelo de embeddings de MiniMax."],
            ["OPENAI_EMBEDDING_MODEL", "string", "text-embedding-3-small", "Modelo de embeddings de OpenAI (fallback)."],
        ],
        col_widths_cm=[5.0, 2.0, 4.0, 6.59], first_col_bold=True)

    # 3. Instalacion
    doc.add_heading("3. Instalacion", level=1)
    doc.add_heading("3.1 Dependencias nuevas en requirements.txt", level=2)
    add_paragraph(doc,
        "Anadir al archivo backend/requirements.txt: pgvector, tiktoken, pypdf, numpy. "
        "Luego correr pip install -r requirements.txt.")
    doc.add_heading("3.2 Activar pgvector en Neon", level=2)
    add_paragraph(doc,
        "En la consola SQL de Neon (o via psql): CREATE EXTENSION IF NOT EXISTS vector;")
    add_warning(doc, "Verificar primero",
        "Si la extension ya esta habilitada, el comando no hace nada. Si la cuenta "
        "Neon free tier no la incluye, migrar a plan Pro.")
    doc.add_heading("3.3 Crear tabla asesor_chunks", level=2)
    add_paragraph(doc, "Aplicar la migracion del Asesor: alembic upgrade head.")
    doc.add_heading("3.4 Copiar el corpus inicial", level=2)
    add_paragraph(doc,
        "El corpus se mantiene en backend/asesor_corpus/ (gitignored). Copiar los "
        "archivos de la ley y manuales desde paso/ley_21719/ y docs/manuales/.")

    # 4. Operacion
    doc.add_heading("4. Operacion del Asesor", level=1)
    doc.add_heading("4.1 Indexar el corpus por primera vez", level=2)
    add_paragraph(doc, "Desde la UI: ir a /admin/asesor y click en 'Indexar corpus'.")
    add_paragraph(doc, "Desde la API: POST /admin/asesor/index con token de superadmin.")
    doc.add_heading("4.2 Ver estadisticas", level=2)
    add_paragraph(doc, "GET /admin/asesor/stats retorna cobertura del corpus.")
    doc.add_heading("4.3 Eliminar un chunk del índice", level=2)
    add_paragraph(doc, "DELETE /admin/asesor/documents/{id} (requiere superadmin).")

    # 5. Troubleshooting
    doc.add_heading("5. Troubleshooting", level=1)
    add_caption_table(doc, "Problemas frecuentes y soluciones", tab_counter, "Tabla")
    add_styled_table(doc,
        ["Sintoma", "Causa probable", "Solucion"],
        [
            ["503 al consultar /asesor/ask", "No hay MINIMAX_API_KEY ni OPENAI_API_KEY configuradas.",
             "Definir al menos una en backend/.env o en Vercel."],
            ["Respuestas sin fuentes", "Corpus no indexado o min_similarity muy alto.",
             "Reindexar via POST /admin/asesor/index. Bajar ASESOR_MIN_SIMILARITY a 0.6."],
            ["Latencia > 10 segundos", "Embeddings lentos por provider o corpus > 5k chunks.",
             "Evaluar pgvector + index ivfflat. Reducir ASESOR_TOP_K a 3."],
            ["Error al reindexar: 'No existe archivo'", "Path en ASESOR_CORPUS_PATH no accesible.",
             "Verificar que la ruta existe y tiene permisos de lectura."],
            ["MiniMax embeddings retorna 404", "El endpoint /v1/embeddings no esta disponible en MiniMax.",
             "El sistema hace fallback automático a OpenAI. Si no hay OpenAI, configurar uno."],
        ],
        col_widths_cm=[4.0, 6.0, 7.59], first_col_bold=True)

    # 6. Costos
    doc.add_heading("6. Estimacion de costos operacionales", level=1)
    add_caption_table(doc, "Costos estimados del Asesor", tab_counter, "Tabla")
    add_styled_table(doc,
        ["Item", "Frecuencia", "Costo unitario aprox", "Costo mensual aprox"],
        [
            ["Embeddings (indexacion inicial 200 chunks)", "Una vez", "USD 0.02", "USD 0.02"],
            ["Embeddings (consulta)", "Por consulta", "USD 0.0001", "USD 3.00 (1k cons/mes)"],
            ["LLM (consulta, ~500 tokens)", "Por consulta", "USD 0.0015", "USD 45.00 (1k cons/mes)"],
            ["PostgreSQL (Neon free)", "Continuo", "USD 0", "USD 0"],
        ],
        col_widths_cm=[6.0, 3.5, 4.0, 4.09], first_col_bold=True)
    add_note(doc, "Costos aproximados",
        "Los costos son estimaciones a Junio 2026. Varillan segun el modelo LLM "
        "usado (MiniMax vs OpenAI) y el volumen de consultas. Reevaluar trimestralmente.")

    # Apéndices
    add_open_questions(doc, [
        "縎e debe ofrecer una opcion de BYO-LLM (bring your own LLM) en v2.0?",
        "緾uando migrar a pgvector nativo?",
    ])
    add_risks_appendix(doc, [
        ("R-01", "Costo de embeddings+LLM puede exceder presupuesto si hay spam de consultas", "Media"),
        ("R-02", "Dependencia de proveedor externo (MiniMax u OpenAI)", "Media"),
    ])
    add_id_glossary(doc, [
        ("RNF-ASES-NN", "Requisito no funcional del Asesor", "Restriccion operacional o de calidad."),
    ])
    add_final_note(doc)

    doc.save(OUT_FILE)
    print(f"[OK] Generado: {OUT_FILE}")


if __name__ == "__main__":
    build()
