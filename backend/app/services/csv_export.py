"""
Exportacion CSV del Registro RAT.
Previene CSV injection y sanitiza datos sensibles (PII).
"""
import csv
import io

from app.models.rat import RAT
from app.core.pii import sanitize_pii

_DANGEROUS_CSV_PREFIXES = ("=", "+", "-", "\t", "\r")


def sanitize_csv_value(value: str) -> str:
    """Previene CSV injection prefijando con ' si el valor parece una formula."""
    if not isinstance(value, str):
        value = str(value) if value is not None else ""
    if value.startswith(_DANGEROUS_CSV_PREFIXES):
        return "'" + value
    return value


CAMPOS_RAT = [
    ("ID", "id"),
    ("Nombre del Proceso", "nombre_proceso"),
    ("Categorías de Titulares", "categoria_titulares"),
    ("Fuente de Datos", "fuente_datos"),
    ("Destinatarios / Encargados", "destinatarios"),
    ("Nombre Encargado", "nombre_encargado"),
    ("Contrato Encargado", "tiene_contrato_encargado"),
    ("Categoría de Datos", "categoria_datos"),
    ("Datos Sensibles", "datos_sensibles"),
    ("Tipo Dato Sensible (Art. 2 g)", "tipo_dato_sensible"),
    ("Tratamiento NNA", "datos_nna"),
    ("Nivel Confidencialidad", "nivel_confidencialidad"),
    ("Estructura del Dato", "estructura_dato"),
    ("Datos Anonimizados", "datos_anonimizados"),
    ("Datos Seudonimizados", "datos_seudonimizados"),
    ("Requiere EIPD", "evaluacion_impacto"),
    ("Estado EIPD", "estado_eipd"),
    ("Fecha EIPD", "fecha_eipd"),
    ("Decisiones Automatizadas", "decisiones_automatizadas"),
    ("Lógica Automatizada", "logica_automatizada"),
    ("Base Legal", "base_legal"),
    ("Finalidad", "finalidad"),
    ("Test Interés Legítimo", "test_interes_legitimo"),
    ("Obs. Auditoría", "observaciones_auditoria"),
    ("Plazo de Retención", "plazo_retencion"),
    ("Medidas de Seguridad", "medidas_seguridad"),
    ("Transferencia de Datos", "transferencia_datos"),
    ("Transferencia Internacional", "transferencia_internacional"),
    ("País Destino", "pais_destino"),
    ("Garantías Transfer. Internacional", "garantias_transferencia_int"),
    ("Transferencia Nacional", "transferencia_nacional"),
    ("Sistema Almacenamiento", "sistema_almacenamiento"),
    ("Volumen Titulares Estimado", "volumen_titulares_estimado"),
    ("Operaciones de Tratamiento", "operaciones_tratamiento"),
    ("Responsable Tratamiento Email", "responsable_tratamiento_email"),
    ("Ciclo Procesamiento", "ciclo_procesamiento"),
    ("Automatización", "automatizacion"),
    ("Frecuencia", "frecuencia"),
    ("Doc. Cláusulas", "doc_clausulas"),
    ("Medidas Organizativas", "medidas_organizativas"),
    ("Mecanismos Eliminación", "mecanismos_eliminacion"),
    ("Técnica Anonimización", "tecnica_anonimizacion"),
    ("Origen Dato (Portabilidad)", "origen_dato_portabilidad"),
    ("Fecha Levantamiento", "fecha_levantamiento"),
    ("Estado", "estado"),
    ("Bloqueado (Art. 8 ter)", "bloqueado"),
    ("Aprobado por", "aprobado_por"),
    ("Fecha Aprobación", "fecha_aprobacion"),
    ("Creado por", "created_by"),
    ("Fecha Creación", "created_at"),
    ("Última Actualización", "updated_at"),
    ("Tiene Archivo Base Legal", "tiene_archivo_base_legal"),
]


def exportar_csv(rats: list[RAT]) -> bytes:
    """Genera un CSV UTF-8 con BOM para compatibilidad con Excel. Previene CSV injection."""
    output = io.StringIO()
    writer = csv.writer(output, delimiter=";", quoting=csv.QUOTE_ALL)

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
            elif attr == "operaciones_tratamiento":
                value = getattr(rat, attr, None)
                if isinstance(value, list):
                    value = ", ".join(str(v) for v in value)
                else:
                    value = value or ""
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
            elif hasattr(value, "value"):
                value = value.value
            text_value = value if isinstance(value, str) else (str(value) if value is not None else "")
            text_value = sanitize_pii(text_value)
            text_value = sanitize_csv_value(text_value)
            fila.append(text_value)
        writer.writerow(fila)

    return ("\ufeff" + output.getvalue()).encode("utf-8")
