"""
Orquestador del servicio RAT — re-exporta todas las funciones para backward compatibility.

Modulos:
- rat_constants: constantes de negocio
- rat_alerts: alertas automaticas de auditoria
- rat_validators: validaciones de negocio (Arts. 11, 14 quater, 15 bis, 16 Ley 21.719)
- rat_file: manejo de archivos (OCI/BYTEA con cifrado Fernet)
- rat_crud: operaciones de base de datos

Este archivo existe unicamente para no romper imports existentes en routes y tests.
Los nuevos imports deben venir de los modulos especificos.
"""
from app.services.rat_constants import (
    CAMPOS_OBLIGATORIOS_COMPLETO,
    CAMPOS_COMPLETITUD_EXTENDIDOS,
    UMBRAL_COMPLETITUD_COMPLETO,
    UMBRAL_JUSTIFICACION_EIPD,
    UMBRAL_MIN_LENGTH_CATEGORIA_TITULARES,
    UMBRAL_MIN_LENGTH_TEST_INTERES_LEGITIMO,
)
from app.services.rat_alerts import ALERTAS_AUDITORIA, generar_alertas_auditoria
from app.services.rat_validators import (
    tiene_consentimiento_activo,
    tiene_contrato_encargado_activo,
    validar_base_legal_otra_requiere_archivo,
    validar_consentimiento_sensibles,
    validar_contrato_encargado,
    validar_eipd_obligatoria,
)
from app.services.rat_file import download_rat_file, procesar_archivo_base_legal
from app.services.rat_crud import (
    aprobar_rat,
    create_rat,
    delete_rat,
    get_audit_logs,
    get_dashboard_stats,
    get_rat,
    get_rats,
    get_rat_for_user,
    marcar_revisado,
    update_rat,
)

__all__ = [
    "ALERTAS_AUDITORIA",
    "CAMPOS_COMPLETITUD_EXTENDIDOS",
    "CAMPOS_OBLIGATORIOS_COMPLETO",
    "UMBRAL_COMPLETITUD_COMPLETO",
    "UMBRAL_JUSTIFICACION_EIPD",
    "UMBRAL_MIN_LENGTH_CATEGORIA_TITULARES",
    "UMBRAL_MIN_LENGTH_TEST_INTERES_LEGITIMO",
    "aprobar_rat",
    "create_rat",
    "delete_rat",
    "download_rat_file",
    "generar_alertas_auditoria",
    "get_audit_logs",
    "get_dashboard_stats",
    "get_rat",
    "get_rats",
    "get_rat_for_user",
    "marcar_revisado",
    "procesar_archivo_base_legal",
    "tiene_consentimiento_activo",
    "tiene_contrato_encargado_activo",
    "update_rat",
    "validar_base_legal_otra_requiere_archivo",
    "validar_consentimiento_sensibles",
    "validar_contrato_encargado",
    "validar_eipd_obligatoria",
]
