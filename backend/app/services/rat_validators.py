"""
Validadores de negocio para el RAT (Arts. 11, 14 quater, 15 bis, 16 Ley 21.719).
Todas las funciones lanzan HTTPException(422) cuando la validacion falla.
"""
import logging
from typing import TYPE_CHECKING, Optional

from fastapi import HTTPException, status

from app.services.rat_constants import UMBRAL_JUSTIFICACION_EIPD

UMBRAL_TEST_INTERES_LEGITIMO = 50

if TYPE_CHECKING:
    from sqlalchemy.orm import Session
    from app.models.rat import RAT

logger = logging.getLogger(__name__)


def tiene_consentimiento_activo(db: "Session", rat_id: int) -> bool:
    """Retorna True si el RAT tiene al menos un consentimiento activo."""
    from app.models.consentimiento import Consentimiento
    return db.query(Consentimiento).filter(
        Consentimiento.rat_id == rat_id,
        Consentimiento.activo == True,  # noqa: E712
    ).first() is not None


def tiene_contrato_encargado_activo(db: "Session", rat_id: int) -> bool:
    """Retorna True si el RAT tiene al menos un contrato de encargado activo."""
    from app.models.encargado_contrato import EncargadoContrato
    return db.query(EncargadoContrato).filter(
        EncargadoContrato.rat_id == rat_id,
        EncargadoContrato.activo == True,  # noqa: E712
    ).first() is not None


def validar_consentimiento_sensibles(db: "Session", rat: "RAT") -> None:
    """Valida que si datos_sensibles=True, exista al menos un consentimiento activo (Art. 16 - REC-06)."""
    if rat.datos_sensibles and not tiene_consentimiento_activo(db, rat.id):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "Este RAT trata datos sensibles y no tiene consentimiento expreso activo. "
                "Para tratar datos sensibles basados en consentimiento (Art. 16 Ley 21.719), "
                "debe registrar primero el consentimiento del titular mediante "
                "POST /rats/{rat_id}/consentimientos antes de guardar el RAT."
            ),
        )


def validar_contrato_encargado(db: "Session", rat: "RAT") -> None:
    """Valida que si nombre_encargado esta definido, exista al menos un contrato activo (Art. 14 quater - REC-03)."""
    if rat.nombre_encargado and not tiene_contrato_encargado_activo(db, rat.id):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "Este RAT tiene un encargado del tratamiento registrado pero no tiene contrato de encargo activo. "
                "Para registrar un encargado es obligatorio contar con un contrato que establezca las instrucciones "
                "de tratamiento, confidencialidad y seguridad (Art. 14 quater Ley 21.719). "
                "Cree el contrato mediante POST /encargados-contrato antes de guardar el RAT."
            ),
        )


def validar_test_interes_legitimo(data: dict) -> None:
    """Valida que base_legal='Interés legítimo' exija test de 3 pasos documentado (Art. 16 Ley 21.719).

    Sin test documentado, la base legal no puede considerarse legítima: la ley exige
    acreditar que el interés prevalece sobre los derechos del titular.
    """
    base_legal = (data.get("base_legal") or "").strip().lower()
    if "interés legítimo" not in base_legal and "interes legitimo" not in base_legal:
        return
    test = (data.get("test_interes_legitimo") or "").strip()
    if not test or len(test) < UMBRAL_TEST_INTERES_LEGITIMO:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                f"La base legal 'Interés legítimo' requiere un test de 3 pasos documentado "
                f"con al menos {UMBRAL_TEST_INTERES_LEGITIMO} caracteres (Art. 16 Ley 21.719). "
                "Complete los campos paso1, paso2 y paso3 antes de guardar el RAT."
            ),
        )


def validar_datos_nna_base_legal(data: dict) -> None:
    """Valida que datos de menores (NNA) usen base legal reforzada (Art. 16 Ley 21.719).

    El tratamiento de datos de menores requiere consentimiento del titular/apoderado
    o interés vital — no admite bases legales como 'Interés legítimo' o 'Contrato'.
    """
    datos_nna = (data.get("datos_nna") or "").strip().lower()
    if datos_nna in ("ninguno", "", "no"):
        return
    base_legal = (data.get("base_legal") or "").strip().lower()
    bases_permitidas = ("consentimiento", "interés vital", "interes vital", "obligación legal", "obligacion legal")
    if not any(b in base_legal for b in bases_permitidas):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "El tratamiento de datos de menores de edad (NNA) requiere base legal "
                "'Consentimiento del titular', 'Interés vital' u 'Obligación legal' "
                "(Art. 16 Ley 21.719). La base legal seleccionada no es admisible para NNA."
            ),
        )


def validar_base_legal_otra_requiere_archivo(data: dict) -> None:
    """Valida que base_legal='Otra' requiera documento adjunto (Art. 11 + 16 Ley 21.719).

    El responsable del tratamiento debe poder acreditar la base legal que invoca.
    Cuando se selecciona 'Otra' (base legal no categorizada), es obligatorio
    adjuntar el documento que respalde la invocacion de dicha base.
    """
    base_legal = (data.get("base_legal") or "").strip()
    archivo = data.get("archivo_base_legal_base64")
    if base_legal.lower() == "otra" and not archivo:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "La base legal 'Otra' requiere un documento adjunto que respalde la invocacion "
                "de dicha base legal (Art. 11 + 16 Ley 21.719). Adjunte el documento mediante "
                "el campo 'archivo_base_legal_base64' antes de guardar el RAT."
            ),
        )


def validar_eipd_obligatoria(data: dict, rat_id: Optional[int] = None, db: Optional["Session"] = None) -> None:
    """Valida EIPD obligatoria si datos_sensibles=True o transferencia_internacional=True (Arts. 15 bis y 28 Ley 21.719).

    Si el RAT declara datos sensibles o transferencia internacional, debe existir una EIPD
    (registrada en la tabla eipds) vinculada al RAT antes de tratar los datos.

    Comportamiento:
    - Si no hay rat_id o no hay db, valida solo los flags del payload (compat hacia atras).
    - Si hay rat_id y db, exige que exista una EIPD con resultado distinto de NO_REQUERIDA
      (acepta NO_REQUERIDA_JUSTIFICADA con justificacion_no_aplica de al menos UMBRAL_JUSTIFICACION_EIPD).

    Acepta resultado='no_requerida_justificada' con justificacion_no_aplica (>=20 chars) como excepcion documentada.
    """
    datos_sensibles = data.get("datos_sensibles", False)
    transferencia_internacional = data.get("transferencia_internacional", False)

    if not (datos_sensibles or transferencia_internacional):
        return

    estado_eipd = data.get("estado_eipd", "no_requerida")
    evaluacion_impacto = data.get("evaluacion_impacto", False)
    justificacion = (data.get("justificacion_no_aplica") or "").strip()

    if rat_id is not None and db is not None:
        from app.models.eipd import EIPD, ResultadoEIPD
        eipd_db = db.query(EIPD).filter(EIPD.rat_id == rat_id).first()
        if eipd_db is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "msg": "Este RAT requiere EIPD según Art. 15 bis",
                    "rat_id": rat_id,
                    "eipd_url": f"/eipd/?rat_id={rat_id}",
                },
            )
        if eipd_db.resultado == ResultadoEIPD.NO_REQUERIDA:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "msg": "La EIPD vinculada a este RAT figura como 'no_requerida' pero el RAT declara datos sensibles o transferencia internacional.",
                    "rat_id": rat_id,
                    "eipd_url": f"/eipd/?rat_id={rat_id}",
                },
            )
        return

    if estado_eipd == "no_requerida":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "Este RAT trata datos sensibles o declara transferencia internacional y requiere "
                "una Evaluación de Impacto en la Protección de Datos (EIPD) conforme al Art. 15 bis "
                "de la Ley 21.719. Debes iniciar la EIPD antes de tratar estos datos. "
                "Creá la EIPD mediante POST /eipd/ vinculada a este RAT."
            ),
        )

    if estado_eipd == "no_requerida_justificada":
        if len(justificacion) < UMBRAL_JUSTIFICACION_EIPD:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    f"Para que el resultado EIPD sea 'no_requerida_justificada' debe ingresar una "
                    f"justificación documentada de al menos {UMBRAL_JUSTIFICACION_EIPD} caracteres (Art. 15 bis Ley 21.719)."
                ),
            )
        return

    if not evaluacion_impacto:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "Este RAT trata datos sensibles o declara transferencia internacional y requiere "
                "que evaluacion_impacto=True (Art. 15 bis Ley 21.719). "
                "No se puede aprobar un RAT con datos sensibles o transferencias internacionales "
                "sin documentar la evaluación de impacto."
            ),
        )
