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
    estilo_resumen_txt = ParagraphStyle(
        "resumen_txt", fontSize=6, textColor=colors.black, fontName="Helvetica", leading=7,
    )
    estilo_resumen_hdr = ParagraphStyle(
        "resumen_hdr", fontSize=6, textColor=colors.white, fontName="Helvetica-Bold", leading=7,
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

    def _ph(txt):
        return Paragraph(txt, estilo_resumen_hdr)

    def _pt(txt):
        return Paragraph(txt, estilo_resumen_txt)

    resumen_data = [[
        _ph("#"), _ph("Proceso"), _ph("Categoría Datos"), _ph("Base Legal"),
        _ph("Estado"), _ph("Sens."), _ph("NNA"), _ph("T.Int."), _ph("EIPD"), _ph("Dec.A."),
    ]]
    for i, rat in enumerate(rats, 1):
        resumen_data.append([
            _pt(str(i)),
            _pt(sanitize_pii(rat.nombre_proceso or "")),
            _pt(sanitize_pii(rat.categoria_datos or "")),
            _pt(sanitize_pii(rat.base_legal or "")),
            _pt(rat.estado.value.upper()),
            _pt("SÍ" if rat.datos_sensibles else "No"),
            _pt("SÍ" if getattr(rat, "datos_nna", None) else "No"),
            _pt("SÍ" if rat.transferencia_internacional else "No"),
            _pt("SÍ" if rat.evaluacion_impacto else "No"),
            _pt("SÍ" if rat.decisiones_automatizadas else "No"),
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


def exportar_pdf_apdp(rats: list[RAT], company: Company) -> bytes:
    """Genera el Reporte APDP formal para presentación ante la Agencia de Protección de Datos.

    Formato oficial Art. 16 Ley 21.719: 7 campos obligatorios + indicadores de compliance.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2.5 * cm,
        bottomMargin=2.5 * cm,
        title=f"Reporte APDP - {company.nombre}",
    )

    COLOR_APDP = colors.HexColor("#1E40AF")
    COLOR_FONDO = colors.HexColor("#EFF6FF")
    COLOR_GRIS = colors.HexColor("#F3F4F6")

    s_titulo = ParagraphStyle("apdp_titulo", fontSize=16, fontName="Helvetica-Bold",
                               textColor=COLOR_APDP, alignment=TA_CENTER, spaceAfter=4)
    s_sub = ParagraphStyle("apdp_sub", fontSize=9, textColor=colors.HexColor("#6B7280"),
                            alignment=TA_CENTER, spaceAfter=2)
    s_seccion = ParagraphStyle("apdp_sec", fontSize=9, fontName="Helvetica-Bold",
                                textColor=colors.white, backColor=COLOR_APDP,
                                leftIndent=4, rightIndent=4)
    s_label = ParagraphStyle("apdp_lbl", fontSize=7, fontName="Helvetica-Bold",
                              textColor=colors.HexColor("#374151"))
    s_valor = ParagraphStyle("apdp_val", fontSize=8, textColor=colors.HexColor("#111827"),
                              leading=11)
    s_normal = ParagraphStyle("apdp_nrm", fontSize=8, textColor=colors.HexColor("#374151"),
                               leading=11)
    s_alerta = ParagraphStyle("apdp_alrt", fontSize=7, textColor=colors.HexColor("#DC2626"),
                               fontName="Helvetica-Oblique")
    s_ok = ParagraphStyle("apdp_ok", fontSize=7, textColor=colors.HexColor("#059669"),
                           fontName="Helvetica-Oblique")
    s_pie = ParagraphStyle("apdp_pie", fontSize=6, textColor=colors.grey, alignment=TA_CENTER)
    s_cert = ParagraphStyle("apdp_cert", fontSize=8, textColor=colors.HexColor("#374151"),
                             leading=13, spaceBefore=6, spaceAfter=6)

    ahora = datetime.now(_ZONA_CHILE).strftime("%d/%m/%Y %H:%M")
    story = []

    # ── PORTADA ──────────────────────────────────────────────────────────────
    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph("REGISTRO DE ACTIVIDADES DE TRATAMIENTO", s_titulo))
    story.append(Paragraph("Informe para la Agencia de Protección de Datos Personales (APDP)", s_sub))
    story.append(Paragraph("Artículo 16 — Ley 21.719 de Protección de Datos Personales — Chile", s_sub))
    story.append(HRFlowable(width="100%", thickness=2, color=COLOR_APDP, spaceAfter=8))

    datos_empresa = [
        ["Responsable del Tratamiento:", company.nombre or "—"],
        ["RUT:", company.rut or "—"],
        ["Domicilio / Dirección:", company.direccion or "—"],
        ["DPO / Contacto:", company.contacto_dpo or "—"],
        ["Email DPO:", company.email_dpo or "—"],
        ["Canal ejercicio de derechos:", company.canal_ejercicio_derechos or "—"],
        ["Fecha de generación:", ahora],
        ["Total de RATs declarados:", str(len(rats))],
    ]
    tbl_empresa = Table(datos_empresa, colWidths=[6 * cm, 11.7 * cm])
    tbl_empresa.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#1E40AF")),
        ("TEXTCOLOR", (1, 0), (1, -1), colors.HexColor("#111827")),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, COLOR_GRIS]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#E5E7EB")),
    ]))
    story.append(tbl_empresa)
    story.append(Spacer(1, 0.5 * cm))

    # ── DECLARACIÓN DE CONFORMIDAD ───────────────────────────────────────────
    story.append(Paragraph("DECLARACIÓN DE CONFORMIDAD", s_seccion))
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph(
        f"El responsable del tratamiento <b>{company.nombre or 'la empresa'}</b>, con RUT "
        f"<b>{company.rut or 'no informado'}</b>, declara bajo su responsabilidad que el presente "
        "documento constituye el Registro de Actividades de Tratamiento de datos personales "
        "conforme al artículo 16 de la Ley 21.719, que los datos contenidos son fidedignos "
        "y que se han adoptado las medidas técnicas y organizativas necesarias para garantizar "
        "la protección de los datos personales tratados.",
        s_cert,
    ))
    story.append(Spacer(1, 0.3 * cm))

    # ── TABLA ÍNDICE ─────────────────────────────────────────────────────────
    story.append(Paragraph("ÍNDICE DE TRATAMIENTOS DECLARADOS", s_seccion))
    story.append(Spacer(1, 0.2 * cm))

    cabecera = [
        Paragraph("#", s_label),
        Paragraph("Proceso", s_label),
        Paragraph("Categoría Datos", s_label),
        Paragraph("Base Legal", s_label),
        Paragraph("Titulares", s_label),
        Paragraph("Estado", s_label),
        Paragraph("Compliance", s_label),
    ]
    filas_indice = [cabecera]
    for i, r in enumerate(rats, 1):
        gaps = []
        if r.datos_sensibles and (r.estado_eipd or "") not in ("completada",):
            gaps.append("EIPD pendiente")
        if r.transferencia_internacional and not r.garantias_transferencia_int:
            gaps.append("Sin garantías TI")
        if ("interés legítimo" in (r.base_legal or "").lower() or
                "interes legitimo" in (r.base_legal or "").lower()) and not r.test_interes_legitimo:
            gaps.append("Sin test IL")
        compliance_txt = "OK" if not gaps else "; ".join(gaps)
        compliance_style = s_ok if not gaps else s_alerta
        filas_indice.append([
            Paragraph(str(i), s_normal),
            Paragraph(r.nombre_proceso or "—", s_normal),
            Paragraph(r.categoria_datos or "—", s_normal),
            Paragraph(r.base_legal or "—", s_normal),
            Paragraph(r.categoria_titulares or "—", s_normal),
            Paragraph((r.estado.value if hasattr(r.estado, "value") else str(r.estado)).capitalize(), s_normal),
            Paragraph(compliance_txt, compliance_style),
        ])
    tbl_indice = Table(filas_indice, colWidths=[0.6*cm, 4*cm, 3*cm, 2.8*cm, 2.8*cm, 1.7*cm, 2.8*cm])
    tbl_indice.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), COLOR_APDP),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, COLOR_FONDO]),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#E5E7EB")),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(tbl_indice)
    story.append(Spacer(1, 0.5 * cm))

    # ── FICHAS ART. 16 POR RAT ───────────────────────────────────────────────
    story.append(Paragraph("DETALLE DE TRATAMIENTOS — ART. 16 LEY 21.719", s_seccion))

    def _v(val) -> str:
        if val is None:
            return "—"
        if isinstance(val, bool):
            return "Sí" if val else "No"
        return str(val).strip() or "—"

    for i, r in enumerate(rats, 1):
        story.append(Spacer(1, 0.4 * cm))
        story.append(Paragraph(f"TRATAMIENTO {i}: {(r.nombre_proceso or '').upper()}", s_seccion))
        story.append(Spacer(1, 0.15 * cm))

        campos_art16 = [
            ("1. Nombre del proceso (Art. 16 a)", _v(r.nombre_proceso)),
            ("2. Categoría de datos (Art. 16 b)", _v(r.categoria_datos)),
            ("3. Categoría de titulares (Art. 16 c)", _v(r.categoria_titulares)),
            ("4. Finalidad del tratamiento (Art. 16 d)", _v(r.finalidad)),
            ("5. Base legal (Art. 16 e)", _v(r.base_legal)),
            ("6. Fuente de los datos (Art. 16 f)", _v(r.fuente_datos)),
            ("7. Plazo de retención (Art. 16 g)", _v(r.plazo_retencion)),
            ("Medidas de seguridad (recom.)", _v(r.medidas_seguridad)),
            ("Destinatarios (recom.)", _v(r.destinatarios)),
            ("Transferencia datos (recom.)", _v(r.transferencia_datos)),
            ("Datos sensibles", _v(r.datos_sensibles)),
            ("Estado EIPD", _v(r.estado_eipd)),
            ("Transferencia internacional", _v(r.transferencia_internacional)),
            ("País destino", _v(r.pais_destino) if r.transferencia_internacional else "N/A"),
            ("Garantías transferencia int.", _v(r.garantias_transferencia_int) if r.transferencia_internacional else "N/A"),
            ("Decisiones automatizadas", _v(r.decisiones_automatizadas)),
            ("Estado del RAT", _v(r.estado.value if hasattr(r.estado, "value") else r.estado)),
        ]

        ficha_data = []
        for label, valor in campos_art16:
            ficha_data.append([
                Paragraph(label, s_label),
                Paragraph(valor, s_valor),
            ])

        tbl_ficha = Table(ficha_data, colWidths=[6.5 * cm, 11.2 * cm])
        tbl_ficha.setStyle(TableStyle([
            ("FONTSIZE", (0, 0), (-1, -1), 7),
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, COLOR_GRIS]),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#E5E7EB")),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        story.append(tbl_ficha)

    # ── RESUMEN COMPLIANCE ────────────────────────────────────────────────────
    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph("RESUMEN DE COMPLIANCE", s_seccion))
    story.append(Spacer(1, 0.2 * cm))

    total_r = len(rats)
    aprobados = sum(1 for r in rats if (r.estado.value if hasattr(r.estado, "value") else str(r.estado)) == "aprobado")
    con_eipd_ok = sum(1 for r in rats if (r.estado_eipd or "") == "completada")
    con_datos_sensibles = sum(1 for r in rats if r.datos_sensibles)
    con_ti = sum(1 for r in rats if r.transferencia_internacional)
    con_garantias = sum(1 for r in rats if r.transferencia_internacional and r.garantias_transferencia_int)

    resumen = [
        ["Indicador", "Total", "Compliant", "Gap"],
        ["RATs Aprobados", str(total_r), str(aprobados), str(total_r - aprobados)],
        ["EIPD completadas (de datos sensibles)", str(con_datos_sensibles), str(con_eipd_ok), str(max(0, con_datos_sensibles - con_eipd_ok))],
        ["Transferencias con garantías", str(con_ti), str(con_garantias), str(con_ti - con_garantias)],
    ]
    tbl_resumen = Table(resumen, colWidths=[9 * cm, 2.2 * cm, 2.5 * cm, 2 * cm])
    tbl_resumen.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), COLOR_APDP),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, COLOR_FONDO]),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#E5E7EB")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
    ]))
    story.append(tbl_resumen)

    # ── SECCIÓN DE FIRMA ──────────────────────────────────────────────────────
    story.append(Spacer(1, 1 * cm))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.grey))
    story.append(Spacer(1, 0.3 * cm))
    firma_data = [
        ["Delegado de Protección de Datos (DPO):", "Representante Legal:"],
        [" ", " "],
        [" ", " "],
        [" ", " "],
        [company.contacto_dpo or "___________________________",
         "___________________________"],
        ["Firma y Timbre", "Firma y Timbre"],
        [ahora, ahora],
    ]
    tbl_firma = Table(firma_data, colWidths=[8.85 * cm, 8.85 * cm])
    tbl_firma.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("LINEABOVE", (0, 4), (-1, 4), 0.5, colors.HexColor("#374151")),
    ]))
    story.append(tbl_firma)

    # ── PIE ───────────────────────────────────────────────────────────────────
    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph(
        "Documento generado por Custodio RAT Manager conforme al Art. 16 Ley 21.719 de Chile. "
        "Para uso oficial ante la Agencia de Protección de Datos Personales (APDP). "
        f"Generado el {ahora}.",
        s_pie,
    ))

    doc.build(story)
    return buffer.getvalue()
