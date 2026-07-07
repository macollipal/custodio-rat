"""
Constantes de negocio para el Registro de Actividades de Tratamiento (RAT).
"""

CAMPOS_OBLIGATORIOS_COMPLETO = [
    "nombre_proceso",
    "categoria_datos",
    "categoria_titulares",
    "finalidad",
    "base_legal",
    "fuente_datos",
    "plazo_retencion",
]

CAMPOS_COMPLETITUD_EXTENDIDOS = [
    "medidas_seguridad",
    "destinatarios",
    "transferencia_datos",
    "nivel_confidencialidad",
    "estructura_dato",
    "datos_nna",
    "datos_anonimizados",
    "datos_seudonimizados",
    "sistema_almacenamiento",
    "volumen_titulares_estimado",
    "responsable_tratamiento_email",
    "ciclo_procesamiento",
    "automatizacion",
    "frecuencia",
    "transferencia_nacional",
    "doc_clausulas",
    "medidas_organizativas",
    "mecanismos_eliminacion",
]

UMBRAL_COMPLETITUD_COMPLETO = 90
UMBRAL_JUSTIFICACION_EIPD = 20
UMBRAL_MIN_LENGTH_CATEGORIA_TITULARES = 3
UMBRAL_MIN_LENGTH_TEST_INTERES_LEGITIMO = 50
UMBRAL_RIESGO_CRITICO = 7
UMBRAL_RIESGO_ALTO = 5
UMBRAL_RIESGO_MEDIO = 3
DIAS_REVISION_RAT = 180
DIAS_ALERTA_RAT_POR_VENCER = 90
DIAS_UMBRAL_EIPD = 90
DIAS_UMBRAL_CONSENTIMIENTO = 730
