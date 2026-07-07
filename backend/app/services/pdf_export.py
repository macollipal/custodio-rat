"""
Exportacion PDF del Registro RAT.
Genera un PDF profesional con resumen + fichas individuales.
"""
import io
from datetime import datetime, timezone, timedelta

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
)
from reportlab.lib.enums import TA_CENTER

from app.models.rat import RAT
from app.models.company import Company
from app.core.pii import sanitize_pii

try:
    from zoneinfo import ZoneInfo as _ZoneInfo
    _ZONA_CHILE = _ZoneInfo("America/Santiago")
except Exception:
    _ZONA_CHILE = timezone(timedelta(hours=-4))


def _truncar(texto: str, largo: int) -> str:
    if not texto:
        return ""
    return texto[:largo] + "..." if len(texto) > largo else texto


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

    COLOR_PRIMARIO = colors.HexColor("#1B3A6B")
    COLOR_SECUNDARIO = colors.HexColor("#2E86AB")
    COLOR_ALERTA = colors.HexColor("#E74C3C")
    COLOR_FONDO = colors.HexColor("#F8F9FA")

    estilo_titulo = ParagraphStyle(
        "titulo", fontSize=18, textColor=COLOR_PRIMARIO,
        alignment=TA_CENTER, fontName="Helvetica-Bold", spaceAfter=6,
    )
    estilo_subtitulo = ParagraphStyle(
        "subtitulo", fontSize=11, textColor=COLOR_SECUNDARIO,
        alignment=TA_CENTER, fontName="Helvetica", spaceAfter=4,
    )
    estilo_label = ParagraphStyle(
        "label", fontSize=8, textColor=COLOR_PRIMARIO, fontName="Helvetica-Bold",
    )
    estilo_valor = ParagraphStyle(
        "valor", fontSize=8, textColor=colors.black, fontName="Helvetica", leading=10,
    )
    estilo_alerta = ParagraphStyle(
        "alerta", fontSize=7, textColor=COLOR_ALERTA, fontName="Helvetica-Oblique",
    )
    estilo_seccion = ParagraphStyle(
        "seccion", fontSize=8, textColor=colors.white, fontName="Helvetica-Bold", leading=10,
    )

    story = []

    story.append(Paragraph("REGISTRO DE ACTIVIDADES DE TRATAMIENTO", estilo_titulo))
    story.append(Paragraph("Conforme al Art. 16 de la Ley 21.719 — Protección de Datos Personales", estilo_subtitulo))
    story.append(HRFlowable(width="100%", thickness=2, color=COLOR_PRIMARIO))
    story.append(Spacer(1, 0.3 * cm))

    story.append(Paragraph(f"Responsable del Tratamiento: {company.nombre}", estilo_label))
    story.append(Paragraph(f"RUT: {company.rut}  |  Rubro: {company.rubro or 'No especificado'}", estilo_valor))
    if company.contacto_dpo:
        story.append(Paragraph(f"Delegado de Protección de Datos (DPO): {company.contacto_dpo} — {company.email_dpo or ''}", estilo_valor))
    story.append(Paragraph(f"Fecha de generación: {datetime.now(_ZONA_CHILE).strftime('%d/%m/%Y %H:%M')} (hora Chile)", estilo_valor))
    story.append(Paragraph(f"Total de procesos registrados: {len(rats)}", estilo_valor))
    story.append(Spacer(1, 0.5 * cm))

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

    for i, rat in enumerate(rats, 1):
        story.append(HRFlowable(width="100%", thickness=1, color=COLOR_SECUNDARIO))
        story.append(Spacer(1, 0.2 * cm))
        story.append(Paragraph(f"PROCESO {i}: {rat.nombre_proceso.upper()}", estilo_label))
        story.append(Spacer(1, 0.2 * cm))

        def _v(val):
            return sanitize_pii(val) if val else "—"

        def _b(val):
            return "Sí" if val else "No"

        campos_ficha = [
            ("SECCION", "PASO 1 — IDENTIFICACIÓN DEL PROCESO"),
            ("ID RAT", str(rat.id)),
            ("Nombre del Proceso", _v(rat.nombre_proceso)),
            ("Categorías de Titulares", _v(rat.categoria_titulares or "No especificadas")),
            ("Fuente de los Datos", _v(rat.fuente_datos)),
            ("Destinatarios / Encargados del Tratamiento", _v(rat.destinatarios or "No especificados")),
        ]
        if getattr(rat, "nombre_encargado", None):
            contrato_txt = "Sí" if getattr(rat, "tiene_contrato_encargado", False) else "NO DOCUMENTADO"
            campos_ficha.append(("Encargado del Tratamiento", f"{_v(rat.nombre_encargado)} — Contrato: {contrato_txt}"))
        campos_ficha.append(("SECCION", "PASO 2 — DATOS TRATADOS"))
        campos_ficha.append(("Categoría de Datos Tratados", _v(rat.categoria_datos)))
        if getattr(rat, "datos_sensibles", False):
            tipo_txt = f" — Tipo: {sanitize_pii(rat.tipo_dato_sensible)}" if getattr(rat, "tipo_dato_sensible", None) else ""
            campos_ficha.append(("Datos Sensibles (Art. 2 g)", f"SÍ{tipo_txt}"))
        campos_ficha.append(("Tratamiento NNA", _v(getattr(rat, "datos_nna", None))))
        campos_ficha.append(("Nivel Confidencialidad", _v(getattr(rat, "nivel_confidencialidad", None))))
        campos_ficha.append(("Estructura del Dato", _v(getattr(rat, "estructura_dato", None))))
        campos_ficha.append(("Datos Anonimizados", _b(getattr(rat, "datos_anonimizados", False))))
        campos_ficha.append(("Datos Seudonimizados", _b(getattr(rat, "datos_seudonimizados", False))))
        if getattr(rat, "evaluacion_impacto", False):
            eipd_estado = getattr(rat, "estado_eipd", "pendiente") or "pendiente"
            eipd_fecha = getattr(rat, "fecha_eipd", None)
            eipd_txt = f"SÍ — Estado: {eipd_estado.upper()}"
            if eipd_fecha:
                eipd_txt += f" — Fecha: {eipd_fecha.strftime('%d/%m/%Y')}"
            if eipd_estado != "completada":
                eipd_txt += " — PENDIENTE"
            campos_ficha.append(("EIPD (Evaluación de Impacto)", eipd_txt))
        if getattr(rat, "decisiones_automatizadas", False):
            campos_ficha.append(("Decisiones Automatizadas (Art. 8)", f"SÍ — {_v(getattr(rat, 'logica_automatizada', None))}"))
        campos_ficha.append(("SECCION", "PASO 3 — FINALIDAD Y BASE LEGAL"))
        campos_ficha.append(("Base Legal (Art. 13 / 16 / 16 BIS Ley 21.719)", _v(rat.base_legal)))
        campos_ficha.append(("Finalidad del Tratamiento", _v(rat.finalidad)))
        if getattr(rat, "test_interes_legitimo", None):
            campos_ficha.append(("Test Interés Legítimo (3 pasos)", _v(rat.test_interes_legitimo)))
        if getattr(rat, "observaciones_auditoria", None):
            campos_ficha.append(("Obs. Auditoría", _v(getattr(rat, "observaciones_auditoria", None))))
        campos_ficha.append(("SECCION", "PASO 4 — ALMACENAMIENTO Y TRANSFERENCIAS"))
        campos_ficha.append(("Plazo de Retención", _v(rat.plazo_retencion)))
        campos_ficha.append(("Medidas de Seguridad", _v(rat.medidas_seguridad or "No especificadas")))
        campos_ficha.append(("Transferencia o Comunicación de Datos", _v(rat.transferencia_datos or "No aplica")))
        if getattr(rat, "transferencia_internacional", False):
            pais = getattr(rat, "pais_destino", None) or "No especificado"
            garantias = getattr(rat, "garantias_transferencia_int", None) or "NO ESPECIFICADAS"
            campos_ficha.append(("Transferencia Internacional", f"SÍ — País: {pais} — Garantías: {garantias}"))
        campos_ficha.append(("Transferencia Nacional", _b(getattr(rat, "transferencia_nacional", False))))
        campos_ficha.append(("Sistema Almacenamiento", _v(getattr(rat, "sistema_almacenamiento", None))))
        campos_ficha.append(("Volumen Titulares Estimado", str(getattr(rat, "volumen_titulares_estimado", None) or "—")))
        campos_ficha.append(("SECCION", "PASO 5 — COMPLIANCE OPERATIVO"))
        ops = getattr(rat, "operaciones_tratamiento", None)
        if ops:
            ops_str = ", ".join(ops) if isinstance(ops, list) else str(ops)
            campos_ficha.append(("Operaciones de Tratamiento", ops_str))
        campos_ficha.append(("Responsable Tratamiento (email)", _v(getattr(rat, "responsable_tratamiento_email", None))))
        campos_ficha.append(("Ciclo de Procesamiento", _v(getattr(rat, "ciclo_procesamiento", None))))
        campos_ficha.append(("Automatización", _v(getattr(rat, "automatizacion", None))))
        campos_ficha.append(("Frecuencia", _v(getattr(rat, "frecuencia", None))))
        campos_ficha.append(("Doc. Cláusulas", _v(getattr(rat, "doc_clausulas", None))))
        campos_ficha.append(("Medidas Organizativas", _v(getattr(rat, "medidas_organizativas", None))))
        campos_ficha.append(("Mecanismos de Eliminación", _v(getattr(rat, "mecanismos_eliminacion", None))))
        campos_ficha.append(("Técnica Anonimización", _v(getattr(rat, "tecnica_anonimizacion", None))))
        campos_ficha.append(("Origen Dato (Portabilidad)", _v(getattr(rat, "origen_dato_portabilidad", None))))
        campos_ficha.append(("Fecha Levantamiento", _v(getattr(rat, "fecha_levantamiento", None))))
        campos_ficha.append(("SECCION", "METADATOS Y AUDITORÍA"))
        campos_ficha.append(("Bloqueado (Art. 8 ter)", "SÍ — RAT BLOQUEADO" if getattr(rat, "bloqueado", False) else "No"))
        campos_ficha.append(("Aprobado por", _v(getattr(rat, "aprobado_por", None))))
        if getattr(rat, "fecha_aprobacion", None):
            campos_ficha.append(("Fecha Aprobación", getattr(rat, "fecha_aprobacion", None).strftime("%d/%m/%Y %H:%M")))

        ficha_data = []
        seccion_indices = []
        for item in campos_ficha:
            if item[0] == "SECCION":
                _, titulo = item
                idx = len(ficha_data)
                seccion_indices.append(idx)
                ficha_data.append([Paragraph(titulo, estilo_seccion), Paragraph("", estilo_seccion)])
            else:
                label, valor = item
                ficha_data.append([
                    Paragraph(label, estilo_label),
                    Paragraph(str(valor), estilo_valor),
                ])

        if rat.datos_sensibles:
            tipo_txt = f" — Tipo: {sanitize_pii(rat.tipo_dato_sensible)}" if getattr(rat, "tipo_dato_sensible", None) else ""
            ficha_data.append([
                Paragraph("⚠️ Datos Sensibles (Art. 2 g)", estilo_alerta),
                Paragraph(f"TRATAMIENTO DE DATOS SENSIBLES{tipo_txt} — Requiere base legal expresa y medidas reforzadas", estilo_alerta),
            ])
        if rat.transferencia_internacional:
            garantias_txt = f" | Garantías: {sanitize_pii(getattr(rat, 'garantias_transferencia_int', '') or '')}" if getattr(rat, "garantias_transferencia_int", None) else " | Garantías: NO ESPECIFICADAS"
            ficha_data.append([
                Paragraph("🌐 Transferencia Internacional", estilo_alerta),
                Paragraph(f"SÍ — País destino: {rat.pais_destino or 'No especificado'}{garantias_txt}", estilo_alerta),
            ])
        if rat.evaluacion_impacto and getattr(rat, "estado_eipd", None) != "completada":
            ficha_data.append([
                Paragraph("📋 EIPD Pendiente (Art. 15 bis)", estilo_alerta),
                Paragraph("La Evaluación de Impacto aún no está completada. Debe finalizarse antes de iniciar el tratamiento.", estilo_alerta),
            ])
        if getattr(rat, "bloqueado", False):
            ficha_data.append([
                Paragraph("🚫 RAT Bloqueado (Art. 8 ter)", estilo_alerta),
                Paragraph("El tratamiento de datos ha sido suspendido. No debe realizarse ningún tratamiento de datos bajo este RAT hasta que se levante el bloqueo.", estilo_alerta),
            ])

        style_cmds = [
            ("BACKGROUND", (0, 0), (0, -1), COLOR_FONDO),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("GRID", (0, 0), (-1, -1), 0.3, colors.lightgrey),
            ("PADDING", (0, 0), (-1, -1), 5),
            ("SPAN", (0, 0), (1, 0)),
        ]
        for idx in seccion_indices:
            style_cmds.append(("BACKGROUND", (0, idx), (1, idx), COLOR_PRIMARIO))
            style_cmds.append(("TEXTCOLOR", (0, idx), (1, idx), colors.white))
            style_cmds.append(("FONTNAME", (0, idx), (1, idx), "Helvetica-Bold"))
            style_cmds.append(("PADDING", (0, idx), (1, idx), 6))

        tabla_ficha = Table(ficha_data, colWidths=[5 * cm, 12.7 * cm])
        tabla_ficha.setStyle(TableStyle(style_cmds))
        story.append(tabla_ficha)
        story.append(Spacer(1, 0.5 * cm))

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
