"""
Servicio de exportación: CSV y PDF del Registro RAT.
"""

import csv
import io
from datetime import datetime, timezone, timedelta

try:
    from zoneinfo import ZoneInfo as _ZoneInfo
    _ZONA_CHILE = _ZoneInfo("America/Santiago")
except Exception:
    _ZONA_CHILE = timezone(timedelta(hours=-4))
from typing import IO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT

from app.models.rat import RAT
from app.models.company import Company
from app.core.pii import sanitize_pii


_DANGEROUS_CSV_PREFIXES = ("=", "+", "-", "\t", "\r")


def sanitize_csv_value(value: str) -> str:
    """Previene CSV injection prefijando con ' si el valor parece una fórmula."""
    if not isinstance(value, str):
        value = str(value) if value is not None else ""
    if value.startswith(_DANGEROUS_CSV_PREFIXES):
        return "'" + value
    return value


CAMPOS_RAT = [
    # Campos obligatorios Art. 16
    ("ID", "id"),
    ("Nombre del Proceso", "nombre_proceso"),
    ("Categoría de Datos", "categoria_datos"),
    ("Categorías de Titulares", "categoria_titulares"),
    ("Finalidad", "finalidad"),
    ("Base Legal", "base_legal"),
    ("Fuente de Datos", "fuente_datos"),
    ("Plazo de Retención", "plazo_retencion"),
    # Campos recomendados Art. 16
    ("Medidas de Seguridad", "medidas_seguridad"),
    ("Destinatarios / Encargados", "destinatarios"),
    ("Transferencia de Datos", "transferencia_datos"),
    # Encargado del tratamiento
    ("Nombre Encargado", "nombre_encargado"),
    ("Contrato Encargado", "tiene_contrato_encargado"),
    # Transferencia internacional
    ("Transfer. Internacional", "transferencia_internacional"),
    ("País Destino", "pais_destino"),
    ("Garantías Transfer. Internacional", "garantias_transferencia_int"),
    ("Transferencia Nacional", "transferencia_nacional"),
    # Datos sensibles y EIPD
    ("Datos Sensibles", "datos_sensibles"),
    ("Tipo Dato Sensible (Art. 2 g)", "tipo_dato_sensible"),
    ("Datos NNA (Menores)", "datos_nna"),
    ("Requiere EIPD", "evaluacion_impacto"),
    ("Estado EIPD", "estado_eipd"),
    ("Fecha EIPD", "fecha_eipd"),
    ("Decisiones Automatizadas", "decisiones_automatizadas"),
    ("Lógica Automatizada", "logica_automatizada"),
    # Test interés legítimo
    ("Test Interés Legítimo", "test_interes_legitimo"),
    # Tier 1 - Gaps críticos Ley 21.719
    ("Nivel Confidencialidad", "nivel_confidencialidad"),
    ("Estructura del Dato", "estructura_dato"),
    ("Datos Anonimizados", "datos_anonimizados"),
    ("Datos Seudonimizados", "datos_seudonimizados"),
    # Tier 2 - Operativos
    ("Ciclo Procesamiento", "ciclo_procesamiento"),
    ("Automatización", "automatizacion"),
    ("Frecuencia", "frecuencia"),
    ("Sistema Almacenamiento", "sistema_almacenamiento"),
    ("Volumen Titulares Estimado", "volumen_titulares_estimado"),
    ("Responsable Tratamiento Email", "responsable_tratamiento_email"),
    ("Doc Clausulas", "doc_clausulas"),
    ("Medidas Organizativas", "medidas_organizativas"),
    ("Mecanismos Eliminación", "mecanismos_eliminacion"),
    ("Técnica Anonimización", "tecnica_anonimizacion"),
    ("Origen Dato Portabilidad", "origen_dato_portabilidad"),
    ("Fecha Levantamiento", "fecha_levantamiento"),
    # Metadatos y auditoría
    ("Estado", "estado"),
    ("Aprobado por", "aprobado_por"),
    ("Fecha Aprobación", "fecha_aprobacion"),
    ("Creado por", "created_by"),
    ("Fecha creación", "created_at"),
    ("Última actualización", "updated_at"),
    ("Tiene Archivo Base Legal", "tiene_archivo_base_legal"),
]


def exportar_csv(rats: list[RAT]) -> bytes:
    """Genera un CSV UTF-8 con BOM para compatibilidad con Excel. Previene CSV injection."""
    output = io.StringIO()
    writer = csv.writer(output, delimiter=";", quoting=csv.QUOTE_ALL)

    # Encabezado — sanitizado contra injection
    writer.writerow([sanitize_csv_value(label) for label, _ in CAMPOS_RAT])

    for rat in rats:
        fila = []
        for _, attr in CAMPOS_RAT:
            if attr == "tiene_archivo_base_legal":
                value = "Sí" if getattr(rat, "archivo_base_legal_datos", None) else "No"
            elif attr == "fecha_eipd":
                value = getattr(rat, attr, None)
                if value:
                    value = value.strftime("%d/%m/%Y")
                else:
                    value = ""
            elif attr == "fecha_levantamiento":
                value = getattr(rat, attr, None)
                if value:
                    value = value.strftime("%d/%m/%Y")
                else:
                    value = ""
            elif attr == "fecha_aprobacion":
                value = getattr(rat, attr, None)
                if value:
                    value = value.strftime("%d/%m/%Y %H:%M")
                else:
                    value = ""
            else:
                value = getattr(rat, attr, "")
            if isinstance(value, bool):
                value = "Sí" if value else "No"
            elif isinstance(value, datetime):
                value = value.strftime("%d/%m/%Y %H:%M")
            elif hasattr(value, "value"):  # Enum
                value = value.value
            text_value = value if isinstance(value, str) else (str(value) if value is not None else "")
            text_value = sanitize_pii(text_value)
            text_value = sanitize_csv_value(text_value)
            fila.append(text_value)
        writer.writerow(fila)

    return ("\ufeff" + output.getvalue()).encode("utf-8")


def exportar_pdf(rats: list[RAT], company: Company) -> bytes:
    """Genera un PDF profesional con el RAT completo de la empresa."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()
    COLOR_PRIMARIO = colors.HexColor("#1B3A6B")
    COLOR_SECUNDARIO = colors.HexColor("#2E86AB")
    COLOR_ALERTA = colors.HexColor("#E74C3C")
    COLOR_FONDO = colors.HexColor("#F8F9FA")

    estilo_titulo = ParagraphStyle(
        "titulo",
        fontSize=18,
        textColor=COLOR_PRIMARIO,
        alignment=TA_CENTER,
        fontName="Helvetica-Bold",
        spaceAfter=6,
    )
    estilo_subtitulo = ParagraphStyle(
        "subtitulo",
        fontSize=11,
        textColor=COLOR_SECUNDARIO,
        alignment=TA_CENTER,
        fontName="Helvetica",
        spaceAfter=4,
    )
    estilo_label = ParagraphStyle(
        "label",
        fontSize=8,
        textColor=COLOR_PRIMARIO,
        fontName="Helvetica-Bold",
    )
    estilo_valor = ParagraphStyle(
        "valor",
        fontSize=8,
        textColor=colors.black,
        fontName="Helvetica",
        leading=10,
    )
    estilo_alerta = ParagraphStyle(
        "alerta",
        fontSize=7,
        textColor=COLOR_ALERTA,
        fontName="Helvetica-Oblique",
    )

    story = []

    # Encabezado
    story.append(Paragraph("REGISTRO DE ACTIVIDADES DE TRATAMIENTO", estilo_titulo))
    story.append(Paragraph("Conforme al Art. 16 de la Ley 21.719 — Protección de Datos Personales", estilo_subtitulo))
    story.append(HRFlowable(width="100%", thickness=2, color=COLOR_PRIMARIO))
    story.append(Spacer(1, 0.3 * cm))

    # Datos de la empresa
    story.append(Paragraph(f"Responsable del Tratamiento: {company.nombre}", estilo_label))
    story.append(Paragraph(f"RUT: {company.rut}  |  Rubro: {company.rubro or 'No especificado'}", estilo_valor))
    if company.contacto_dpo:
        story.append(Paragraph(f"Delegado de Protección de Datos (DPO): {company.contacto_dpo} — {company.email_dpo or ''}", estilo_valor))
    story.append(Paragraph(f"Fecha de generación: {datetime.now(_ZONA_CHILE).strftime('%d/%m/%Y %H:%M')} (hora Chile)", estilo_valor))
    story.append(Paragraph(f"Total de procesos registrados: {len(rats)}", estilo_valor))
    story.append(Spacer(1, 0.5 * cm))

    # Tabla de resumen
    resumen_data = [["#", "Proceso", "Categoría Datos", "Base Legal", "Estado", "Sensibles", "NNA", "Transf. Int.", "EIPD", "Dec. Auto."]]
    for i, rat in enumerate(rats, 1):
        resumen_data.append([
            str(i),
            _truncar(sanitize_pii(rat.nombre_proceso or ""), 25),
            _truncar(sanitize_pii(rat.categoria_datos or ""), 25),
            _truncar(sanitize_pii(rat.base_legal or ""), 20),
            rat.estado.value.upper(),
            "SÍ" if rat.datos_sensibles else "No",
            "SÍ" if getattr(rat, "datos_nna", None) else "No",
            "SÍ" if rat.transferencia_internacional else "No",
            "SÍ" if rat.evaluacion_impacto else "No",
            "SÍ" if rat.decisiones_automatizadas else "No",
        ])

    tabla_resumen = Table(
        resumen_data,
        colWidths=[0.5 * cm, 3.5 * cm, 3.5 * cm, 3 * cm, 2 * cm, 1.5 * cm, 1 * cm, 1.5 * cm, 1 * cm, 1.5 * cm],
        repeatRows=1,
    )
    tabla_resumen.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), COLOR_PRIMARIO),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 6),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, COLOR_FONDO]),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (0, -1), "CENTER"),
        ("ALIGN", (5, 0), (-1, -1), "CENTER"),
        ("PADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(tabla_resumen)
    story.append(Spacer(1, 0.8 * cm))

    # Fichas individuales por proceso
    for i, rat in enumerate(rats, 1):
        story.append(HRFlowable(width="100%", thickness=1, color=COLOR_SECUNDARIO))
        story.append(Spacer(1, 0.2 * cm))
        story.append(Paragraph(f"PROCESO {i}: {rat.nombre_proceso.upper()}", estilo_label))
        story.append(Spacer(1, 0.2 * cm))

        campos_ficha = [
            ("Categoría de Datos Tratados", sanitize_pii(rat.categoria_datos)),
            ("Categorías de Titulares", sanitize_pii(rat.categoria_titulares or "No especificadas")),
            ("Finalidad del Tratamiento", sanitize_pii(rat.finalidad)),
            ("Base Legal (Art. 13 / 16 / 16 BIS Ley 21.719)", sanitize_pii(rat.base_legal)),
            ("Fuente de los Datos", sanitize_pii(rat.fuente_datos)),
            ("Transferencia o Comunicación de Datos", sanitize_pii(rat.transferencia_datos or "No aplica")),
            ("Plazo de Retención", sanitize_pii(rat.plazo_retencion)),
            ("Medidas de Seguridad", sanitize_pii(rat.medidas_seguridad or "No especificadas")),
            ("Destinatarios / Encargados del Tratamiento", sanitize_pii(rat.destinatarios or "No especificados")),
        ]
        if getattr(rat, "nombre_encargado", None):
            contrato_txt = "Sí" if getattr(rat, "tiene_contrato_encargado", False) else "NO DOCUMENTADO"
            campos_ficha.append(("Encargado del Tratamiento", f"{sanitize_pii(rat.nombre_encargado)} — Contrato: {contrato_txt}"))
        if getattr(rat, "test_interes_legitimo", None):
            campos_ficha.append(("Test Interés Legítimo (3 pasos)", sanitize_pii(rat.test_interes_legitimo)))
        if getattr(rat, "logica_automatizada", None):
            campos_ficha.append(("Lógica Automatizada (Art. 8)", sanitize_pii(rat.logica_automatizada)))
        if getattr(rat, "datos_nna", None):
            campos_ficha.append(("Datos NNA (Menores)", sanitize_pii(rat.datos_nna)))
        if getattr(rat, "nivel_confidencialidad", None):
            campos_ficha.append(("Nivel Confidencialidad", sanitize_pii(rat.nivel_confidencialidad)))
        if getattr(rat, "estructura_dato", None):
            campos_ficha.append(("Estructura del Dato", sanitize_pii(rat.estructura_dato)))
        if getattr(rat, "ciclo_procesamiento", None):
            campos_ficha.append(("Ciclo de Procesamiento", sanitize_pii(rat.ciclo_procesamiento)))
        if getattr(rat, "automatizacion", None):
            campos_ficha.append(("Automatización", sanitize_pii(rat.automatizacion)))
        if getattr(rat, "frecuencia", None):
            campos_ficha.append(("Frecuencia", sanitize_pii(rat.frecuencia)))
        if getattr(rat, "sistema_almacenamiento", None):
            campos_ficha.append(("Sistema Almacenamiento", sanitize_pii(rat.sistema_almacenamiento)))
        if getattr(rat, "responsable_tratamiento_email", None):
            campos_ficha.append(("Responsable Tratamiento (email)", sanitize_pii(rat.responsable_tratamiento_email)))
        if getattr(rat, "transferencia_nacional", None):
            campos_ficha.append(("Transferencia Nacional", "Sí" if rat.transferencia_nacional else "No"))
        if getattr(rat, "doc_clausulas", None):
            campos_ficha.append(("Doc. Cláusulas", sanitize_pii(rat.doc_clausulas)))
        if getattr(rat, "medidas_organizativas", None):
            campos_ficha.append(("Medidas Organizativas", sanitize_pii(rat.medidas_organizativas)))
        if getattr(rat, "mecanismos_eliminacion", None):
            campos_ficha.append(("Mecanismos de Eliminación", sanitize_pii(rat.mecanismos_eliminacion)))
        if getattr(rat, "tecnica_anonimizacion", None):
            campos_ficha.append(("Técnica Anonimización", sanitize_pii(rat.tecnica_anonimizacion)))
        if getattr(rat, "datos_anonimizados", None):
            campos_ficha.append(("Datos Anonimizados", "Sí" if rat.datos_anonimizados else "No"))
        if getattr(rat, "datos_seudonimizados", None):
            campos_ficha.append(("Datos Seudonimizados", "Sí" if rat.datos_seudonimizados else "No"))
        if getattr(rat, "origen_dato_portabilidad", None):
            campos_ficha.append(("Origen Dato Portabilidad", sanitize_pii(rat.origen_dato_portabilidad)))
        if getattr(rat, "volumen_titulares_estimado", None):
            campos_ficha.append(("Volumen Titulares Estimado", str(rat.volumen_titulares_estimado)))

        ficha_data = []
        for label, valor in campos_ficha:
            ficha_data.append([
                Paragraph(label, estilo_label),
                Paragraph(str(valor), estilo_valor),
            ])

        # Flags especiales
        if rat.datos_sensibles:
            tipo_txt = f" — Tipo: {sanitize_pii(rat.tipo_dato_sensible)}" if getattr(rat, "tipo_dato_sensible", None) else ""
            ficha_data.append([
                Paragraph("Datos Sensibles (Art. 2 g)", estilo_label),
                Paragraph(f"SÍ{tipo_txt} — Requiere base legal expresa y medidas reforzadas", estilo_alerta),
            ])
        if rat.transferencia_internacional:
            garantias_txt = f" | Garantías: {sanitize_pii(getattr(rat, 'garantias_transferencia_int', '') or '')}" if getattr(rat, "garantias_transferencia_int", None) else " | Garantías: NO ESPECIFICADAS"
            ficha_data.append([
                Paragraph("Transferencia Internacional", estilo_label),
                Paragraph(f"SÍ — País destino: {rat.pais_destino or 'No especificado'}{garantias_txt}", estilo_alerta),
            ])
        if rat.evaluacion_impacto:
            eipd_estado = getattr(rat, "estado_eipd", "pendiente") or "pendiente"
            eipd_fecha = getattr(rat, "fecha_eipd", None)
            eipd_txt = f"SÍ — Estado: {eipd_estado.upper()}"
            if eipd_fecha:
                eipd_txt += f" — Fecha: {eipd_fecha}"
            if eipd_estado != "completada":
                eipd_txt += " — PENDIENTE de completar antes de iniciar el tratamiento"
            ficha_data.append([
                Paragraph("EIPD (Art. 15 bis)", estilo_label),
                Paragraph(eipd_txt, estilo_alerta),
            ])
        if getattr(rat, "decisiones_automatizadas", False):
            ficha_data.append([
                Paragraph("Decisiones Automatizadas (Art. 8)", estilo_label),
                Paragraph("SÍ — Documente la lógica del sistema y el mecanismo de revisión humana disponible", estilo_alerta),
            ])
        if getattr(rat, "transferencia_nacional", None) and rat.transferencia_nacional:
            ficha_data.append([
                Paragraph("Transferencia Nacional", estilo_label),
                Paragraph("SÍ — Comunicación de datos dentro de Chile", estilo_alerta),
            ])

        tabla_ficha = Table(ficha_data, colWidths=[5 * cm, 12.7 * cm])
        tabla_ficha.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), COLOR_FONDO),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("GRID", (0, 0), (-1, -1), 0.3, colors.lightgrey),
            ("PADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(tabla_ficha)

        if rat.observaciones_auditoria:
            story.append(Spacer(1, 0.2 * cm))
            story.append(Paragraph(f"Observaciones de auditoría: {sanitize_pii(rat.observaciones_auditoria)}", estilo_alerta))

        story.append(Spacer(1, 0.5 * cm))

    # Pie de página legal
    story.append(HRFlowable(width="100%", thickness=1, color=colors.grey))
    story.append(Spacer(1, 0.2 * cm))
    pie = ParagraphStyle("pie", fontSize=6, textColor=colors.grey, alignment=TA_CENTER)
    story.append(Paragraph(
        "Este documento fue generado automáticamente por Custodio conforme a los requisitos del "
        "Artículo 16 de la Ley 21.719 de Protección de Datos Personales de Chile. "
        "Documento de carácter confidencial — solo para uso interno y ante la Agencia de Protección de Datos Personales.",
        pie,
    ))

    doc.build(story)
    return buffer.getvalue()


def _truncar(texto: str, largo: int) -> str:
    if not texto:
        return ""
    return texto[:largo] + "..." if len(texto) > largo else texto
