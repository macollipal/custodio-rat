"""
Build 01 — Vision y Alcance del Asesor v1.0
============================================
Genera: docs/documentacion_oficial_asesorgpt/01_Vision_Alcance_AsesorCustodio_v1.0.docx
Código: ASES-DOC-01
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
OUT_FILE = os.path.join(REGEN_DIR, "01_Vision_Alcance_AsesorCustodio_v1.0.docx")
os.makedirs(REGEN_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)
DOC_CODE = "ASES-DOC-01"
DOC_TITLE = "Vision y Alcance del Asesor"


def build():
    doc = new_document()
    add_header_footer(doc, DOC_TITLE)
    add_cover(doc,
              title="VISION Y ALCANCE DEL ASESOR",
              subtitle="Modulo RAG de Custodio RAT Manager - Ley 21.719",
              code=DOC_CODE)
    add_version_control(doc, DOC_CODE, DOC_TITLE, changes=[
        ("1.0", "Junio 2026",
         "Creacion inicial del documento a partir de la auditoría previa AUDITORIA_ASES_V1.0."),
    ])
    add_toc(doc)
    fig_counter = [0]
    tab_counter = [0]

    # ============================================================
    # 1. PROBLEMA QUE RESUELVE
    # ============================================================
    doc.add_heading("1. Problema que resuelve", level=1)
    add_paragraph(doc,
        "Las organizaciones chilenas que deben cumplir la Ley 21.719 se enfrentan a "
        "tres problemas operativos recurrentes al gestionar el Registro de Actividades "
        "de Tratamiento (RAT):")
    add_bullet(doc, "Interpretacion legal: Dificultad para interpretar los articulos de la ley sin asistencia legal especializada.")
    add_bullet(doc, "Inconsistencia: Respuestas inconsistentes al responder consultas internas sobre que RAT crear, que base legal aplicar o como documentar un consentimiento.")
    add_bullet(doc, "Latencia: Tiempo elevado entre la consulta del responsable y la obtencion de una respuesta accionable.")
    add_paragraph(doc,
        "El modulo Custodio Asesor ataca estos tres problemas con un asistente IA que "
        "recupera evidencia directa desde el corpus legal (Ley 21.719) y los manuales "
        "operativos de Custodio RAT Manager, y genera respuestas citadas y trazables.")
    add_note(doc, "Citas obligatorias",
        "El Asesor nunca responde 'de memoria'. Toda respuesta incluye al menos una "
        "cita a la fuente ([Fuente: <nombre>, seccion <X>]). Si no encuentra "
        "evidencia en el corpus, lo indica honestamente en lugar de inventar.")

    # ============================================================
    # 2. OBJETIVOS DEL NEGOCIO
    # ============================================================
    doc.add_heading("2. Objetivos del negocio", level=1)
    add_caption_table(doc, "Objetivos de negocio del Asesor", tab_counter, "Tabla")
    add_styled_table(doc,
        ["ID", "Descripción"],
        [
            ["ON-01", "Reducir el tiempo medio de respuesta a consultas sobre Ley 21.719 de ~1 dia a < 5 segundos (P95)."],
            ["ON-02", "Aumentar la consistencia de las RATs generadas por distintos usuarios de una misma empresa."],
            ["ON-03", "Disminuir la dependencia de asesoria legal externa para consultas operativas recurrentes."],
            ["ON-04", "Acelerar la adopcion de Custodio RAT Manager como herramienta de uso cotidiano."],
            ["ON-05", "Generar diferenciacion competitiva frente a competidores que no ofrecen asistencia IA contextual."],
        ],
        col_widths_cm=[2.5, 15.09], first_col_bold=True)

    # ============================================================
    # 3. PUBLICO OBJETIVO
    # ============================================================
    doc.add_heading("3. Público objetivo", level=1)
    add_caption_table(doc, "Público objetivo del Asesor", tab_counter, "Tabla")
    add_styled_table(doc,
        ["Rol", "Necesidad cubierta"],
        [
            ["DPO / Oficial de proteccion de datos",
             "Consultas tecnicas recurrentes sobre articulos y procedimientos de la ley."],
            ["Administrador de empresa (admin_empresa)",
             "Dudas operativas al crear/editar RATs, brechas o consentimientos."],
            ["Usuario regular",
             "Soporte contextual al usar el sistema, sin abandonar la pantalla actual."],
            ["Auditor externo / APDP",
             "Acceso de solo lectura a evidencia y consultas registradas (audit_log)."],
        ],
        col_widths_cm=[5.5, 12.09], first_col_bold=True)

    # ============================================================
    # 4. PROPUESTA DE VALOR
    # ============================================================
    doc.add_heading("4. Propuesta de valor", level=1)
    add_paragraph(doc,
        "Custodio Asesor ofrece respuestas accionables, citadas y trazables sobre la "
        "Ley 21.719, integradas a la plataforma Custodio RAT Manager. La propuesta se "
        "apoya en cuatro pilares:")
    add_bullet(doc, "Recuperacion: Recupera evidencia del corpus legal y de manuales operativos antes de responder.", bold_prefix="Recuperacion: ")
    add_bullet(doc, "Citas: Cita explicitamente el articulo o seccion de la que extrae la respuesta.", bold_prefix="Citas: ")
    add_bullet(doc, "Auditoría: Registra cada consulta en audit_log para evidencia de cumplimiento.", bold_prefix="Auditoría: ")
    add_bullet(doc, "Aislamiento: Mantiene el contexto multi-tenant: nunca mezcla información entre empresas.", bold_prefix="Aislamiento: ")

    # ============================================================
    # 5. ALCANCE DEL PRODUCTO
    # ============================================================
    doc.add_heading("5. Alcance del producto (v1.0)", level=1)

    doc.add_heading("5.1 Dentro del alcance", level=2)
    add_bullet(doc, "Chat autenticado en la pagina /asesor para usuarios logueados.")
    add_bullet(doc, "Retrieval-augmented generation sobre el corpus indexado.")
    add_bullet(doc, "Citas a fuentes en cada respuesta con link al documento original.")
    add_bullet(doc, "Auditoría de cada consulta en audit_log (entidad=asesor).")
    add_bullet(doc, "Endpoint admin /admin/asesor/index para indexar/actualizar el corpus.")
    add_bullet(doc, "Endpoint admin /admin/asesor/stats para ver cobertura del corpus.")
    add_bullet(doc, "Soporte de corpus Markdown (.md) y texto plano (.txt) en v1.0.")
    add_bullet(doc, "Embeddings via MiniMax con fallback automático a OpenAI.")

    doc.add_heading("5.2 Fuera del alcance (v1.0)", level=2)
    add_bullet(doc, "Acceso público (formulario ARCO) - se difiere a v1.1.")
    add_bullet(doc, "Streaming de respuestas via SSE - se difiere a v1.1.")
    add_bullet(doc, "Reindex automático programado - se difiere a v1.1.")
    add_bullet(doc, "Historial de conversaciones persistido - se difiere a v1.1.")
    add_bullet(doc, "Soporte de PDFs con OCR - se difiere a v1.1 (en v1.0 solo se soporta texto extraido).")
    add_bullet(doc, "Multi-idioma - solo español en v1.0.")
    add_bullet(doc, "Re-ranking con cross-encoder - v1.0 usa cosine top-k simple.")

    # ============================================================
    # 6. BENEFICIOS ESPERADOS
    # ============================================================
    doc.add_heading("6. Beneficios esperados", level=1)
    add_caption_table(doc, "Beneficios esperados del Asesor", tab_counter, "Tabla")
    add_styled_table(doc,
        ["Beneficio medible", "Métrica objetivo"],
        [
            ["Reduccion del tiempo de consulta legal", "De 1 dia a < 5 segundos (P95)"],
            ["Cobertura del corpus", "100% de los articulos relevantes indexados"],
            ["Tasa de respuestas con cita valida", ">= 95%"],
            ["Adopcion por usuarios", ">= 40% de usuarios activos usan el Asesor en el primer mes"],
            ["Reduccion de tickets a soporte humano", ">= 30% menos tickets de primer nivel"],
        ],
        col_widths_cm=[7.0, 10.59])

    # ============================================================
    # 7. RESTRICCIONES Y ASUNCIONES
    # ============================================================
    doc.add_heading("7. Restricciones y asunciones", level=1)

    doc.add_heading("7.1 Restricciones tecnicas", level=2)
    add_bullet(doc, "Vercel serverless: latencia de cold start afecta a la primera consulta.")
    add_bullet(doc, "Neon free tier: limite de almacenamiento vectorial a monitorear.")
    add_bullet(doc, "Costo de embeddings: indexacion completa solo se ejecuta bajo demanda (no automática en v1.0).")

    doc.add_heading("7.2 Asunciones de negocio", level=2)
    add_bullet(doc, "Los usuarios tienen rol autenticado (no se permite uso anonimo).")
    add_bullet(doc, "El corpus inicial (Ley + manuales) es mantenido por el equipo Custodio.")
    add_bullet(doc, "El LLM no entrega consejo legal profesional: derivados a abogado si la consulta lo requiere.")

    # ============================================================
    # 8. METRICAS DE EXITO (KPIs)
    # ============================================================
    doc.add_heading("8. Métricas de exito (KPIs)", level=1)
    add_caption_table(doc, "KPIs del Asesor v1.0", tab_counter, "Tabla")
    add_styled_table(doc,
        ["ID", "Métrica", "Objetivo", "Frecuencia"],
        [
            ["KPI-01", "Latencia P95 de respuesta", "< 5 segundos", "Medicion continua"],
            ["KPI-02", "Consultas con >= 1 cita", ">= 95%", "Medicion diaria"],
            ["KPI-03", "Tasa de fallback al chat generico", "<= 20%", "Medicion semanal"],
            ["KPI-04", "Usuarios activos que usan el Asesor", ">= 40% en primer mes", "Medicion mensual"],
            ["KPI-05", "Chunks indexados", ">= 200 (Ley + manuales)", "Verificar tras indexar"],
        ],
        col_widths_cm=[2.0, 6.5, 4.5, 4.59], first_col_bold=True)

    # ============================================================
    # 9. RIESGOS DE PRODUCTO
    # ============================================================
    doc.add_heading("9. Riesgos de producto", level=1)
    add_caption_table(doc, "Riesgos de producto del Asesor", tab_counter, "Tabla")
    add_styled_table(doc,
        ["ID", "Severidad", "Descripción", "Mitigacion"],
        [
            ["R-01", "Alta", "Alucinaciones del LLM que contradigan la ley.",
             "Prompt con cita obligatoria + threshold de similitud mínimo."],
            ["R-02", "Alta", "Endpoint de embeddings MiniMax no disponible.",
             "Fallback automático a OpenAI documentado y testeado."],
            ["R-03", "Media", "Adopcion baja por usuarios.",
             "OnboardingChecklist incluye paso 'Probar el Asesor' en v1.1."],
            ["R-04", "Media", "Costos de embeddings por reindex excesivo.",
             "Indexacion idempotente por hash (solo chunks nuevos)."],
            ["R-05", "Baja", "Branding del Asesor confunde con producto separado.",
             "UI clarifica 'Modulo Asesor de Custodio' en cada pagina."],
        ],
        col_widths_cm=[2.0, 2.5, 6.5, 6.59], first_col_bold=True)

    # ============================================================
    # APENDICES
    # ============================================================
    add_open_questions(doc, [
        "縎e debe permitir que empresas suban sus propios documentos al corpus? (v1.1 vs v2.0)",
        "緾ual es el costo máximo aceptable por mes de embeddings+LLM en produccion?",
        "緿ebe el Asesor poder sugerir acciones en la UI (ej: 'Crear RAT ahora')?",
    ])
    add_risks_appendix(doc, [
        ("R-01", "Alucinaciones del LLM sobre la ley", "Alta"),
        ("R-02", "Endpoint embeddings MiniMax no disponible", "Alta"),
        ("R-03", "Adopcion baja por usuarios", "Media"),
        ("R-04", "Costos de embeddings", "Media"),
        ("R-05", "Confusion de branding con producto separado", "Baja"),
    ])
    add_id_glossary(doc, [
        ("RAG", "Retrieval-Augmented Generation",
         "Arquitectura que combina recuperacion de documentos con generación de texto."),
        ("pgvector", "Extension de PostgreSQL",
         "Soporte nativo de vectores y busqueda por similitud en Neon."),
        ("Embedding", "Vector numerico",
         "Representacion densa (1536 dim) de un texto para busqueda semantica."),
        ("Top-k", "k resultados mas similares",
         "Parametro de retrieval: cantidad de chunks a pasar al LLM."),
    ])
    add_final_note(doc)

    doc.save(OUT_FILE)
    print(f"[OK] Generado: {OUT_FILE}")


if __name__ == "__main__":
    build()
