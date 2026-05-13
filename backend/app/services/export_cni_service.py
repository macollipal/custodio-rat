"""
Generador de informe RAT en formato CNI para提交APDC (Ley 21.719).
"""

from datetime import datetime, timezone
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.rat import RAT
    from app.models.company import Company


def exportar_rat_cni(rats: list["RAT"], company: "Company") -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    lines = []
    lines.append("=" * 80)
    lines.append("REGISTRO DE ACTIVIDADES DE TRATAMIENTO (RAT) — FORMATO APDC")
    lines.append("Ley 21.719 — Protección de Datos Personales (Chile)")
    lines.append("=" * 80)
    lines.append("")
    lines.append("INFORMACIÓN DE LA EMPRESA")
    lines.append("-" * 40)
    lines.append(f"  Razón Social: {company.nombre}")
    lines.append(f"  RUT:           {company.rut}")
    lines.append(f"  Rubro:         {company.rubro or 'No especificado'}")
    lines.append(f"  Dirección:     {company.direccion or 'No especificada'}")
    lines.append(f"  DPO:           {company.contacto_dpo or 'No especificado'}")
    lines.append(f"  Email DPO:     {company.email_dpo or 'No especificado'}")
    lines.append(f"  Canal ejercer derechos: {company.canal_ejercicio_derechos or 'No especificado'}")
    lines.append("")
    lines.append("=" * 80)
    lines.append(f"Total de procesos RAT registrados: {len(rats)}")
    lines.append(f"Fecha de generación: {now}")
    lines.append("=" * 80)
    lines.append("")
    lines.append("REGISTROS RAT")
    lines.append("=" * 80)

    for i, rat in enumerate(rats, 1):
        lines.append("")
        lines.append(f"[{i}] ID: {rat.id}")
        lines.append("-" * 40)
        lines.append(f"  Nombre proceso:          {rat.nombre_proceso}")
        lines.append(f"  Categoría datos:         {rat.categoria_datos or 'No especificada'}")
        lines.append(f"  Categoría titulares:     {rat.categoria_titulares or 'No especificada'}")
        lines.append(f"  Finalidad:               {rat.finalidad or 'No especificada'}")
        lines.append(f"  Base legal:              {rat.base_legal or 'No especificada'}")
        lines.append(f"  Plazo retención:        {rat.plazo_retencion or 'No especificado'}")
        lines.append(f"  Datos sensibles:        {'Sí' if rat.datos_sensibles else 'No'}")
        if rat.tipo_dato_sensible:
            lines.append(f"  Tipo dato sensible:      {rat.tipo_dato_sensible}")
        lines.append(f"  Evaluación impacto (EIPD): {'Sí' if rat.evaluacion_impacto else 'No'}")
        if rat.estado_eipd:
            lines.append(f"  Estado EIPD:             {rat.estado_eipd}")
        lines.append(f"  Transferencia internacional: {'Sí' if rat.transferencia_internacional else 'No'}")
        if rat.pais_destino:
            lines.append(f"  País destino:            {rat.pais_destino}")
        if rat.garantias_transferencia_int:
            lines.append(f"  Garantías transferencia: {rat.garantias_transferencia_int}")
        lines.append(f"  Decisiones automatizadas: {'Sí' if rat.decisiones_automatizadas else 'No'}")
        lines.append(f"  Medidas seguridad:       {rat.medidas_seguridad or 'No especificadas'}")
        lines.append(f"  Destinatarios:           {rat.destinatarios or 'No especificados'}")
        lines.append(f"  Nombre encargado:        {rat.nombre_encargado or 'No aplicable'}")
        lines.append(f"  Tiene contrato encargado: {'Sí' if rat.tiene_contrato_encargado else ('No' if rat.nombre_encargado else 'N/A')}")
        lines.append(f"  Estado RAT:              {rat.estado.value if hasattr(rat.estado, 'value') else rat.estado}")
        lines.append(f"  Completitud:             {rat.calcular_completitud() if hasattr(rat, 'calcular_completitud') else 'N/A'}%")
        lines.append(f"  Nivel riesgo:            {rat.calcular_nivel_riesgo() if hasattr(rat, 'calcular_nivel_riesgo') else 'N/A'}")
        lines.append(f"  Creado por:              {rat.created_by or 'Desconocido'}")
        lines.append(f"  Fecha creación:          {rat.created_at}")
        lines.append(f"  Última actualización:    {rat.updated_at}")
        if rat.observaciones_auditoria:
            lines.append(f"  Observaciones auditoría: {rat.observaciones_auditoria}")

    sensibles_count = sum(1 for r in rats if r.datos_sensibles)
    eipd_count = sum(1 for r in rats if r.evaluacion_impacto)
    transfer_count = sum(1 for r in rats if r.transferencia_internacional)

    lines.append("")
    lines.append("=" * 80)
    lines.append("RESUMEN ESTADÍSTICO")
    lines.append("=" * 80)
    lines.append(f"  Total procesos:                    {len(rats)}")
    lines.append(f"  Procesos con datos sensibles:      {sensibles_count}")
    lines.append(f"  Requieren Evaluación de Impacto:   {eipd_count}")
    lines.append(f"  Con transferencia internacional:   {transfer_count}")
    lines.append(f"  Estados: ")
    estados = {}
    for r in rats:
        e = r.estado.value if hasattr(r.estado, 'value') else r.estado
        estados[e] = estados.get(e, 0) + 1
    for k, v in estados.items():
        lines.append(f"    - {k}: {v}")
    lines.append("")
    lines.append("=" * 80)
    lines.append(f"Informe generado el {now} por Custodio RAT Manager")
    lines.append("Este documento cumple con los requisitos del Art. 12 quáter Ley 21.719")
    lines.append("=" * 80)

    return "\n".join(lines)