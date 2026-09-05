"""
Alertas de auditor├¡a generadas automaticamente seg├║n flags del RAT (Art. 16 Ley 21.719).
"""

ALERTAS_AUDITORIA = {
    "datos_sensibles": (
        "⚠️ Este proceso trata datos sensibles (Art. 2 letra g Ley 21.719). Verifique que cuenta con base legal "
        "explícita y medidas de seguridad reforzadas. Documente el tipo específico de dato sensible."
    ),
    "datos_sensibles_consentimiento": (
        "⚠️ BASE LEGAL: El tratamiento de datos sensibles basado en consentimiento requiere que sea EXPRESO "
        "(no basta consentimiento implícito). Documente el mecanismo de obtención y revocación del consentimiento."
    ),
    "datos_sensibles_biometria": (
        "🚨 BIOMETRÍA: Los datos biométricos destinados a identificar inequívocamente a una persona se rigen por "
        "el Art. 16 BIS Ley 21.719. Requieren base legal específica y evaluación EIPD. En relaciones laborales, "
        "el consentimiento del empleado NO es base legal válida (relación jerárquica asimétrica)."
    ),
    "evaluacion_impacto": (
        "📋 Se marcó que requiere Evaluación de Impacto en Protección de Datos (EIPD/DPIA). "
        "Asegúrese de completarla y documentarla antes de iniciar el tratamiento (Art. 15 bis Ley 21.719)."
    ),
    "transferencia_internacional": (
        "🌍 Este proceso incluye transferencia internacional de datos. "
        "Verifique que el país destinatario cuenta con nivel adecuado de protección o que se aplican "
        "garantías apropiadas (SCC, BCR u otras). Chile NO está en la lista de adecuación de la UE. "
        "Documente las garantías aplicadas en el campo correspondiente."
    ),
    "transferencia_sin_garantias": (
        "🌍 ATENCIÓN: Se registró transferencia internacional sin especificar las garantías aplicadas. "
        "Documente si aplica nivel adecuado, SCC u otras garantías (Art. 28 Ley 21.719)."
    ),
    "decisiones_automatizadas": (
        "🤖 Este proceso involucra decisiones automatizadas o perfilamiento. Los titulares tienen derecho a "
        "solicitar intervención humana e impugnar la decisión (Art. 8 Ley 21.719). Documente la lógica del sistema "
        "y el mecanismo de revisión humana disponible. Evalúe si requiere EIPD."
    ),
    "interes_legitimo": (
        "⚖️ Base legal: Interés legítimo. Debe documentar el test de 3 pasos: (1) ¿existe interés legítimo real? "
        "(2) ¿el tratamiento es necesario para ese interés? (3) ¿prevalece sobre los derechos del titular? "
        "Sin este test documentado, la base no sirve como defensa ante la APDC."
    ),
    "interes_legitimo_sin_test": (
        "⚖️ PENDIENTE: Base legal Interés legítimo requiere documentar el test de 3 pasos en el campo correspondiente."
    ),
    "encargado_sin_contrato": (
        "📄 ENCARGADO SIN CONTRATO: Se registró un encargado del tratamiento pero no se ha confirmado la existencia "
        "de un contrato de encargo que establezca las instrucciones de tratamiento, confidencialidad y seguridad "
        "(Art. 14 quater Ley 21.719)."
    ),
    "eipd_pendiente": (
        "⏳ EIPD PENDIENTE: Este proceso requiere Evaluación de Impacto en Protección de Datos y aún no está completada. "
        "No puede iniciarse el tratamiento hasta completar la EIPD (Art. 15 bis Ley 21.719)."
    ),
    "falta_doc_base_legal": (
        "📄 SIN DOCUMENTO DE BASE LEGAL: La base legal seleccionada requiere un documento que la respalde "
        "(consentimiento, contrato, norma legal, EIPD, etc.). Adjunte el documento correspondiente para alcanzar el 100% de completitud."
    ),
}


def generar_alertas_auditoria(data: dict) -> str:
    """Genera observaciones automaticas de auditoria segun flags activados."""
    alertas = []
    base_legal = (data.get("base_legal") or "").lower()
    tipo_sensible = (data.get("tipo_dato_sensible") or "").lower()

    if data.get("datos_sensibles"):
        alertas.append(ALERTAS_AUDITORIA["datos_sensibles"])
        if "consentimiento" in base_legal:
            alertas.append(ALERTAS_AUDITORIA["datos_sensibles_consentimiento"])
        if "biométrico" in tipo_sensible or "biometrico" in tipo_sensible:
            alertas.append(ALERTAS_AUDITORIA["datos_sensibles_biometria"])

    if data.get("evaluacion_impacto"):
        alertas.append(ALERTAS_AUDITORIA["evaluacion_impacto"])

    if data.get("transferencia_internacional"):
        alertas.append(ALERTAS_AUDITORIA["transferencia_internacional"])
        if not data.get("garantias_transferencia_int"):
            alertas.append(ALERTAS_AUDITORIA["transferencia_sin_garantias"])

    if data.get("decisiones_automatizadas"):
        alertas.append(ALERTAS_AUDITORIA["decisiones_automatizadas"])

    if "interés legítimo" in base_legal or "interes legitimo" in base_legal:
        alertas.append(ALERTAS_AUDITORIA["interes_legitimo"])
        if not data.get("test_interes_legitimo"):
            alertas.append(ALERTAS_AUDITORIA["interes_legitimo_sin_test"])

    if data.get("nombre_encargado") and not data.get("tiene_contrato_encargado"):
        alertas.append(ALERTAS_AUDITORIA["encargado_sin_contrato"])

    if data.get("evaluacion_impacto") and (data.get("estado_eipd") or "pendiente") not in ("completada",):
        alertas.append(ALERTAS_AUDITORIA["eipd_pendiente"])

    base_legal_raw = data.get("base_legal") or ""
    if base_legal_raw.strip().lower() != "otra" and not data.get("archivo_base_legal_datos"):
        alertas.append(ALERTAS_AUDITORIA["falta_doc_base_legal"])

    return "\n".join(alertas)
