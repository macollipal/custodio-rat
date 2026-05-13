"""
Servicio de sugerencias automáticas para el RAT.
Dado un tipo de proceso, retorna valores precompletados según las
categorías más comunes en empresas chilenas bajo la Ley 21.719.
"""

from app.schemas.rat import RATSugerenciaOut

# Base de conocimiento: tipo_proceso → sugerencias
SUGERENCIAS: dict[str, dict] = {
    "clientes web": {
        "categoria_datos": "Datos identificativos (nombre, email, teléfono), datos de navegación y comportamiento online",
        "categoria_titulares": "Clientes y usuarios del servicio web",
        "finalidad": "Gestión de la relación comercial, atención al cliente, envío de comunicaciones y marketing digital",
        "base_legal": "Ejecución de contrato",
        "plazo_retencion_sugerido": "5 años desde el último contacto comercial",
        "datos_sensibles": False,
        "decisiones_automatizadas": False,
        "observacion": "Si se realizan perfiles de comportamiento o scoring automatizado, activar el flag de decisiones automatizadas y evaluar EIPD.",
    },
    "empleados": {
        "categoria_datos": "Datos identificativos, laborales, remuneracionales, de salud (licencias médicas), previsionales",
        "categoria_titulares": "Trabajadores y ex-trabajadores de la organización",
        "finalidad": "Gestión de la relación laboral, liquidación de remuneraciones, cumplimiento de obligaciones legales previsionales y tributarias",
        "base_legal": "Obligación legal",
        "plazo_retencion_sugerido": "10 años desde el término de la relación laboral (Art. 58 Código del Trabajo)",
        "datos_sensibles": True,
        "tipo_dato_sensible": "Salud (licencias médicas)",
        "evaluacion_impacto": False,
        "decisiones_automatizadas": False,
        "observacion": (
            "Los datos de salud (licencias) son datos sensibles — base legal: obligación legal. "
            "ATENCIÓN: Si se usan datos biométricos, registrarlos en un proceso separado 'Control biométrico de asistencia', "
            "ya que requieren tratamiento bajo Art. 16 BIS. En relaciones laborales, el consentimiento del empleado "
            "NO es base legal válida para biometría (relación jerárquica asimétrica — ver Caso Martorell, AEPD)."
        ),
    },
    "control biométrico asistencia": {
        "categoria_datos": "Datos biométricos de identificación (huella dactilar, facial o equivalente), registro de hora de entrada/salida",
        "categoria_titulares": "Trabajadores sujetos a control de asistencia",
        "finalidad": "Control de asistencia y cumplimiento de jornada laboral según Art. 33 Código del Trabajo",
        "base_legal": "Obligación legal",
        "plazo_retencion_sugerido": "5 años desde el registro (norma tributaria y laboral)",
        "datos_sensibles": True,
        "tipo_dato_sensible": "Datos biométricos de identificación (Art. 16 BIS Ley 21.719)",
        "evaluacion_impacto": True,
        "decisiones_automatizadas": False,
        "observacion": (
            "IMPORTANTE — Art. 16 BIS: Los datos biométricos destinados a identificar inequívocamente a una persona "
            "requieren EIPD previa y base legal específica. El consentimiento del empleado NO es base válida en contextos "
            "laborales por la asimetría de poder (confirmado por jurisprudencia europea, caso Martorell Siglo XXI). "
            "Documente si usa 'minucias' (hash de huella) o imagen directa — ambas son datos biométricos protegidos. "
            "Obtenga asesoría legal antes de implementar y verifique si el proveedor tiene contrato de encargo del tratamiento."
        ),
    },
    "proveedores": {
        "categoria_datos": "Datos identificativos de contacto, datos tributarios (RUT, actividad económica), datos bancarios",
        "categoria_titulares": "Proveedores de bienes y servicios (personas naturales o contactos de personas jurídicas)",
        "finalidad": "Gestión de la relación contractual, pagos, evaluación crediticia y cumplimiento tributario",
        "base_legal": "Ejecución de contrato",
        "plazo_retencion_sugerido": "6 años desde el cierre del ejercicio contable (norma tributaria SII)",
        "datos_sensibles": False,
        "decisiones_automatizadas": False,
        "observacion": "Verificar que los datos bancarios están cifrados en reposo y en tránsito. Si se usa evaluación crediticia automatizada, activar flag de decisiones automatizadas.",
    },
    "postulantes": {
        "categoria_datos": "Datos identificativos, currículum vitae, historial laboral, referencias personales",
        "categoria_titulares": "Postulantes y candidatos a cargos laborales",
        "finalidad": "Proceso de selección y reclutamiento de personal",
        "base_legal": "Consentimiento del titular",
        "plazo_retencion_sugerido": "2 años desde la postulación o hasta cubrir el cargo",
        "datos_sensibles": False,
        "decisiones_automatizadas": False,
        "observacion": "Informar al postulante mediante aviso de privacidad. No solicitar datos no necesarios para el cargo (principio de proporcionalidad). Si se usa screening automatizado de CVs, activar flag de decisiones automatizadas.",
    },
    "pacientes": {
        "categoria_datos": "Datos de salud, datos identificativos, historial clínico, datos de tratamientos y medicamentos",
        "categoria_titulares": "Pacientes y beneficiarios del servicio de salud",
        "finalidad": "Prestación de servicios de salud, seguimiento clínico, facturación a seguros de salud",
        "base_legal": "Interés vital del titular",
        "plazo_retencion_sugerido": "15 años desde el último registro clínico (Ley 19.966 GES)",
        "datos_sensibles": True,
        "tipo_dato_sensible": "Salud (física o mental)",
        "evaluacion_impacto": True,
        "decisiones_automatizadas": False,
        "observacion": "Datos de salud: categoría sensible del Art. 2 letra g. Requiere EIPD y medidas de seguridad reforzadas. Si se usa diagnóstico o triaje automatizado, documentar el mecanismo de revisión humana.",
    },
    "menores de edad": {
        "categoria_datos": "Datos identificativos, datos académicos, datos de contacto de tutores o apoderados",
        "categoria_titulares": "Niños, niñas y adolescentes (menores de 18 años)",
        "finalidad": "Servicios educativos, actividades recreativas o deportivas autorizadas por el representante legal",
        "base_legal": "Consentimiento del titular",
        "plazo_retencion_sugerido": "3 años desde el término de la relación con el servicio",
        "datos_sensibles": True,
        "evaluacion_impacto": True,
        "decisiones_automatizadas": False,
        "observacion": "El consentimiento debe ser otorgado por el representante legal (padre/madre/tutor). Aplicar principio de minimización estricto. Los menores de edad constituyen categoría especial con protección reforzada.",
    },
    "marketing": {
        "categoria_datos": "Datos identificativos, preferencias, historial de compras, datos de comportamiento online",
        "categoria_titulares": "Clientes y personas que han otorgado consentimiento para comunicaciones comerciales",
        "finalidad": "Envío de comunicaciones comerciales personalizadas, análisis de segmentos y preferencias de clientes",
        "base_legal": "Consentimiento del titular",
        "plazo_retencion_sugerido": "2 años desde el último consentimiento activo",
        "datos_sensibles": False,
        "decisiones_automatizadas": True,
        "observacion": "Implementar mecanismo de opt-out sencillo (tan fácil como el opt-in). Registrar fecha, medio y versión del consentimiento. Los titulares pueden oponerse al tratamiento para marketing directo sin necesidad de justificación (Art. 8 Ley 21.719).",
    },
    "videovigilancia": {
        "categoria_datos": "Imágenes y videos de personas en espacios físicos",
        "categoria_titulares": "Personas presentes en las instalaciones vigiladas (empleados, visitantes, clientes)",
        "finalidad": "Seguridad de instalaciones y protección de bienes propios",
        "base_legal": "Interés legítimo",
        "plazo_retencion_sugerido": "30 días desde la grabación (salvo incidentes que requieran conservación)",
        "datos_sensibles": False,
        "evaluacion_impacto": False,
        "decisiones_automatizadas": False,
        "observacion": (
            "Interés legítimo requiere test de 3 pasos documentado. Colocar señalética visible antes del área vigilada. "
            "Las grabaciones no pueden usarse para otros fines. Si se usa reconocimiento facial o análisis automatizado "
            "de comportamiento, se activa Art. 16 BIS y la EIPD pasa a ser OBLIGATORIA."
        ),
    },
    "socios o accionistas": {
        "categoria_datos": "Datos identificativos, participación accionaria, datos patrimoniales, datos tributarios",
        "categoria_titulares": "Socios, accionistas y directores de la organización",
        "finalidad": "Gestión societaria, cumplimiento normativo ante CMF y SII, reparto de dividendos",
        "base_legal": "Obligación legal",
        "plazo_retencion_sugerido": "10 años desde el término de la relación societaria",
        "datos_sensibles": False,
        "decisiones_automatizadas": False,
        "observacion": "Algunos datos pueden estar sujetos a normas de la CMF y deben tratarse con confidencialidad. Verificar obligaciones de reporte ante reguladores.",
    },
    "contabilidad y facturación": {
        "categoria_datos": "Datos identificativos tributarios (RUT), datos de contacto comercial, datos de transacciones comerciales, detalle de compras y ventas, datos de pago (facturas electrónicas)",
        "categoria_titulares": "Clientes, proveedores y terceros con quienes se emiten o reciben documentos tributarios",
        "finalidad": "Cumplimiento de obligaciones tributarias ante el SII, emisión de facturas electrónicas, registro contable de transacciones comerciales, declaración de impuestos",
        "base_legal": "Obligación legal",
        "plazo_retencion_sugerido": "10 años desde la emisión del documento (Art. 12 Ley 19.983 y normativa SII)",
        "datos_sensibles": False,
        "decisiones_automatizadas": False,
        "observacion": "La retención de facturas electrónicas es obligatoria por 10 años según normativa del SII. Si se usa factoring electrónico o cobranza automatizada, activar flag de decisiones automatizadas y evaluar si requiere EIPD.",
    },
    "evaluación de desempeño": {
        "categoria_datos": "Datos identificativos del trabajador, calificaciones de desempeño, logros, metas cumplidas, competencias evaluadas,retroalimentación escrita",
        "categoria_titulares": "Trabajadores de la organización",
        "finalidad": "Evaluación periódica del desempeño laboral, definición de metas, retroalimentación y desarrollo profesional",
        "base_legal": "Interés legítimo",
        "plazo_retencion_sugerido": "2 años desde la evaluación o hasta el término de la relación laboral",
        "datos_sensibles": False,
        "decisiones_automatizadas": False,
        "observacion": "La base legal 'Interés legítimo' requiere test de 3 pasos documentado. Las evaluaciones deben ser conocidas por el trabajador. Si el sistema genera rankings o puntuaciones automáticas que influyan en promociones/contratación, activar decisiones automatizadas.",
    },
    "riesgos laborales": {
        "categoria_datos": "Datos identificativos del trabajador, datos de accidentes laborales, datos de licencias médicas, datos de exámenes de empleo, datos de mutuelle de seguridad (ACHS)",
        "categoria_titulares": "Trabajadores, contratistas y visitantes afectados por incidentes de seguridad laboral",
        "finalidad": "Prevención de riesgos laborales, gestión de accidentes del trabajo, cumplimiento de obligaciones legales en materia de seguridad y salud ocupacional (DS 594), reporte a mutualidades (ACHS)",
        "base_legal": "Obligación legal",
        "plazo_retencion_sugerido": "5 años desde el registro del accidente o evento (normativa mutual y DS 594)",
        "datos_sensibles": True,
        "tipo_dato_sensible": "Salud (física o mental)",
        "evaluacion_impacto": False,
        "decisiones_automatizadas": False,
        "observacion": "Los datos de salud laboral (licencias, exámenes médicos) son sensibles — requieren medidas de seguridad reforzadas. El reporte a la mutual es obligatorio. Si el análisis predictivo de accidentes identifica trabajadores específicos, puede activar decisiones automatizadas.",
    },
}

# Alias para búsqueda flexible
ALIAS: dict[str, str] = {
    "cliente": "clientes web",
    "clientes": "clientes web",
    "usuario": "clientes web",
    "usuarios": "clientes web",
    "trabajador": "empleados",
    "trabajadores": "empleados",
    "rrhh": "empleados",
    "recursos humanos": "empleados",
    "proveedor": "proveedores",
    "candidatos": "postulantes",
    "reclutamiento": "postulantes",
    "salud": "pacientes",
    "clinica": "pacientes",
    "hospital": "pacientes",
    "menor": "menores de edad",
    "niños": "menores de edad",
    "publicidad": "marketing",
    "correo comercial": "marketing",
    "email marketing": "marketing",
    "camaras": "videovigilancia",
    "cámaras": "videovigilancia",
    "cctv": "videovigilancia",
    "accionista": "socios o accionistas",
    "socios":     "socios o accionistas",
    "directorio": "socios o accionistas",
    "empleado":   "empleados",
    "personal":   "empleados",
    "vigilancia": "videovigilancia",
    "paciente":   "pacientes",
    "niño":       "menores de edad",
    "niña":       "menores de edad",
    "biometria":        "control biométrico asistencia",
    "biometría":        "control biométrico asistencia",
    "huella dactilar":  "control biométrico asistencia",
    "reconocimiento facial": "control biométrico asistencia",
    "control asistencia":    "control biométrico asistencia",
    "asistencia biométrica": "control biométrico asistencia",
    "facturación": "contabilidad y facturación",
    "facturas": "contabilidad y facturación",
    "cuenta por cobrar": "contabilidad y facturación",
    "contabilidad": "contabilidad y facturación",
    "impuestos": "contabilidad y facturación",
    "SII": "contabilidad y facturación",
    "remuneraciones": "empleados",
    "liquidación": "empleados",
    "nómina": "empleados",
    "evaluación desempeño": "evaluación de desempeño",
    "evaluacion desempeño": "evaluación de desempeño",
    "ODJ": "evaluación de desempeño",
    "desempeño": "evaluación de desempeño",
    "metas": "evaluación de desempeño",
    "SST": "riesgos laborales",
    "seguridad laboral": "riesgos laborales",
    "accidentes": "riesgos laborales",
    "mutual": "riesgos laborales",
}


def sugerir_rat(tipo_proceso: str) -> RATSugerenciaOut:
    """
    Retorna sugerencias de campos RAT dado un tipo de proceso.
    Hace búsqueda exacta primero, luego por alias y finalmente por palabras clave parciales.
    """
    clave = tipo_proceso.lower().strip()

    # Búsqueda exacta
    datos = SUGERENCIAS.get(clave)

    # Búsqueda por alias
    if not datos:
        clave_normalizada = ALIAS.get(clave)
        if clave_normalizada:
            datos = SUGERENCIAS.get(clave_normalizada)

    # Búsqueda por intersección de palabras (más precisa que substring)
    if not datos:
        clave_words = set(clave.split())
        mejor_key, mejor_score = None, 0
        for key in SUGERENCIAS:
            score = len(clave_words & set(key.split()))
            if score > mejor_score:
                mejor_score, mejor_key = score, key
        if not mejor_key:
            for key in SUGERENCIAS:
                if key in clave or clave in key:
                    mejor_key = key
                    break
        if mejor_key:
            datos = SUGERENCIAS[mejor_key]
            clave = mejor_key

    if not datos:
        return RATSugerenciaOut(
            tipo_proceso=tipo_proceso,
            categoria_datos="No se encontraron sugerencias automáticas. Complete manualmente.",
            categoria_titulares="Indique las categorías de titulares (clientes, empleados, proveedores, etc.)",
            finalidad="Defina la finalidad específica del tratamiento.",
            base_legal="Seleccione la base legal aplicable según Art. 13 Ley 21.719.",
            plazo_retencion_sugerido="Defina el plazo según necesidad del negocio y normativa aplicable.",
            datos_sensibles=False,
            observacion=(
                f"No se encontró plantilla para '{tipo_proceso}'. "
                "Tipos disponibles: " + ", ".join(SUGERENCIAS.keys())
            ),
        )

    return RATSugerenciaOut(
        tipo_proceso=tipo_proceso,
        categoria_datos=datos["categoria_datos"],
        categoria_titulares=datos["categoria_titulares"],
        finalidad=datos["finalidad"],
        base_legal=datos["base_legal"],
        plazo_retencion_sugerido=datos["plazo_retencion_sugerido"],
        datos_sensibles=datos["datos_sensibles"],
        tipo_dato_sensible=datos.get("tipo_dato_sensible"),
        evaluacion_impacto=datos.get("evaluacion_impacto"),
        decisiones_automatizadas=datos.get("decisiones_automatizadas"),
        observacion=datos["observacion"],
    )


def listar_tipos_proceso() -> list[str]:
    """Retorna todos los tipos de proceso disponibles."""
    return list(SUGERENCIAS.keys())
