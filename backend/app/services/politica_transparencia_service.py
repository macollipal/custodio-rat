"""
Servicio de generación de Política de Transparencia Pública (Art. 14 ter Ley 21.719 — REC-02).
Genera dinámicamente los 12 ítems requeridos por la ley a partir de los datos del sistema.
"""

import hashlib
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.models.company import Company
from app.models.rat import RAT
from app.models.politica_transparencia import PoliticaTransparencia
from app.schemas.politica_transparencia import PoliticaTransparenciaOut


DERECHOS_ARCO = (
    "Derechos del titular bajo la Ley 21.719:\n"
    "a) Acceso: derecho a conocer si sus datos personales están siendo tratados y a obtener copia de ellos.\n"
    "b) Rectificación: derecho a corregir errores o actualizar sus datos personales.\n"
    "c) Cancelación: derecho a eliminar sus datos personales cuando ya no sean necesarios.\n"
    "d) Oposición: derecho a oponerse al tratamiento de sus datos personales.\n"
    "e) Bloqueo temporal: derecho a solicitar la suspensión temporal del tratamiento de sus datos.\n"
    "f) Portabilidad: derecho a recibir sus datos en formato estructurado y de uso común."
)

RECURRIR_APDC = (
    "Si el titular considera que sus derechos no han sido atendidos por el responsable del tratamiento, "
    "puede recurrir gratuitamente ante la Agencia Española de Protección de Datos (AEPD) — equivalente local: "
    "la Autoridad de Protección de Datos de Chile (APDC) — para进行检查 y eventual sanción."
)


def generar_politica(db: Session, company_id: int) -> PoliticaTransparenciaOut:
    """Genera la política de transparencia completa para una empresa (Art. 14 ter — REC-02)."""
    empresa: Optional[Company] = db.query(Company).filter(Company.id == company_id).first()
    if not empresa:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Empresa no encontrada.")

    rats = db.query(RAT).filter(RAT.company_id == company_id).all()

    items = _generar_items(empresa, rats)
    contenido = _serializar_items(items)
    hash_val = hashlib.sha256(contenido.encode("utf-8")).hexdigest()

    politica = db.query(PoliticaTransparencia).filter(
        PoliticaTransparencia.company_id == company_id
    ).first()

    ahora = datetime.now(timezone.utc)
    if politica:
        politica.version = _incrementar_version(politica.version)
        politica.fecha_generacion = ahora
        politica.hash_sha256 = hash_val
    else:
        politica = PoliticaTransparencia(
            company_id=company_id,
            version="1.0",
            fecha_generacion=ahora,
            hash_sha256=hash_val,
        )
        db.add(politica)

    db.commit()
    db.refresh(politica)

    return PoliticaTransparenciaOut(
        company_id=empresa.id,
        nombre_empresa=empresa.nombre,
        rut_empresa=empresa.rut or "",
        rubro=empresa.rubro,
        contacto_dpo=empresa.contacto_dpo,
        email_dpo=empresa.email_dpo,
        domicilio=empresa.direccion,
        version=politica.version,
        fecha_generacion=politica.fecha_generacion,
        hash_sha256=politica.hash_sha256,
        **items,
    )


def _generar_items(empresa: Company, rats: list[RAT]) -> dict:
    """Genera los 12 ítems de la política de transparencia."""
    items = {}

    items["item_a_politica"] = (
        f"Política de tratamiento de datos personales de {empresa.nombre}. "
        f"Versión vigente. Fecha de última actualización: {datetime.now(timezone.utc).strftime('%d-%m-%Y')}."
    )

    items["item_b_responsable"] = (
        f"Responsable: {empresa.nombre}\n"
        f"RUT: {empresa.rut or 'No informado'}\n"
        f"Representante legal: {'No registrado' if not empresa.contacto_dpo else empresa.contacto_dpo}\n"
        f"Delegado de Protección de Datos (DPO): {empresa.contacto_dpo or 'No designado'}\n"
        f"Email DPO: {empresa.email_dpo or 'No registrado'}"
    )

    items["item_c_domicilio"] = (
        f"Domicilio: {empresa.direccion or 'No informado'}\n"
        f"Email de contacto para ejercicio de derechos: {empresa.email_dpo or 'No registrado'}\n"
        f"Canal para ejercer derechos ARCO: {empresa.canal_ejercicio_derechos or 'No especificado'}"
    )

    cats_datos = list(set(r.categoria_datos for r in rats if r.categoria_datos))
    cats_titulares = list(set(r.categoria_titulares for r in rats if r.categoria_titulares))
    finalidades = list(set(r.finalidad for r in rats if r.finalidad))
    bases_legales = list(set(r.base_legal for r in rats if r.base_legal))
    items["item_d_categorias"] = (
        f"Categorías de datos tratados: {', '.join(cats_datos) if cats_datos else 'No registrados'}\n"
        f"Categorías de titulares: {', '.join(cats_titulares) if cats_titulares else 'No registrados'}\n"
        f"Finalidades del tratamiento: {', '.join(finalidades) if finalidades else 'No registradas'}\n"
        f"Bases de legitimidad: {', '.join(bases_legales) if bases_legales else 'No registradas'}"
    )

    medidas = list(set(r.medidas_seguridad for r in rats if r.medidas_seguridad))
    items["item_e_medidas"] = (
        f"Medidas de seguridad implementadas: {', '.join(m for m in medidas if m) if medidas else 'No registradas'}"
    )

    items["item_f_derechos_arco"] = DERECHOS_ARCO
    items["item_g_recurir_apdc"] = RECURRIR_APDC

    transferencias = [
        f"- {r.nombre_proceso}: {r.pais_destino or 'sin especificar'}"
        for r in rats if r.transferencia_internacional
    ]
    items["item_h_transferencias"] = (
        "Transferencias internacionales de datos:\n" + "\n".join(transferencias)
        if transferencias else "No se realizan transferencias internacionales de datos."
    )

    plazos = list(set(r.plazo_retencion for r in rats if r.plazo_retencion))
    items["item_i_conservacion"] = (
        f"Períodos de conservación: {', '.join(p for p in plazos if p) if plazos else 'No registrados'}"
    )

    fuentes = list(set(r.fuente_datos for r in rats if r.fuente_datos))
    items["item_j_fuente"] = (
        f"Fuentes de datos: {', '.join(f for f in fuentes if f) if fuentes else 'No registradas'}"
    )

    items["item_k_retirar_consentimiento"] = (
        "El titular tiene derecho a retirar el consentimiento en cualquier momento, "
        "mediante solicitud escrita al responsable del tratamiento. "
        "La retirada del consentimiento no afecta la licitud del tratamiento basada en el consentimiento "
        "previo a su retirada."
    )

    decisiones = [
        f"- {r.nombre_proceso}: {r.decisiones_automatizadas and 'Sí' or 'No'}"
        for r in rats if r.decisiones_automatizadas
    ]
    items["item_l_decisiones_automatizadas"] = (
        "Procesos con decisiones automatizadas:\n" + "\n".join(decisiones)
        if decisiones else "No existen procesos con decisiones automatizadas o perfilamiento."
    )

    return items


def _serializar_items(items: dict) -> str:
    return "\n---\n".join(f"{k}: {v}" for k, v in items.items())


def _incrementar_version(version: str) -> str:
    parts = version.split(".")
    if len(parts) == 2:
        major, minor = parts
        return f"{major}.{int(minor) + 1}"
    return f"{version}.1"
