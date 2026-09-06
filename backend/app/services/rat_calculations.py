"""
Servicios de cálculo derivados del RAT (H3.1).

Historia:
- 2026-07-07: el método RAT.calcular_completitud() estaba en el modelo RAT
  de SQLAlchemy. Esto provocaba dos clases de bugs:

  1. db.query(RAT.calcular_completitud, ...) — SQLAlchemy interpretaba el
     método como lambda e intentaba ejecutarlo sin 'self', lanzando
     TypeError en runtime (incidente de produccion del 2026-07-08 01:36 UTC).

  2. db.query(col1, col2, ...) devolvia Row (named tuple) sin acceso a
     metodos de instancia → AttributeError cuando se llamaba
     r.calcular_completitud().

- Solucion: extraer la logica a funciones PURAS que aceptan un dict de
  datos. Sin estado, sin self, sin efectos colaterales. Testables sin BD.

Los metodos del modelo se mantienen como wrappers de compatibilidad
que llaman al servicio. Asi nadie rompe codigo existente.
"""
from __future__ import annotations

from typing import Any, Mapping


# Umbrales (movidos del modelo)
UMBRAL_RIESGO_CRITICO = 7
UMBRAL_RIESGO_ALTO = 5
UMBRAL_RIESGO_MEDIO = 3


def _truthy(value: Any) -> bool:
    """Un valor se considera completado si existe y no es string vacío.
    Para booleanos: solo True cuenta — False es el default de BD, no una decisión activa del usuario.
    """
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    if isinstance(value, str) and not value.strip():
        return False
    if isinstance(value, (list, dict)) and len(value) == 0:
        return False
    return True


def calcular_completitud(data: Mapping[str, Any]) -> int:
    """Calcula la completitud (0-100) de un RAT a partir de un dict de campos.

    Acepta cualquier Mapping — instancia del modelo RAT (via __dict__),
    dict de SQLAlchemy row, dict de Pydantic schema, etc.

    Formula Ley 21.719 Art. 16 + gaps Tier 1/Tier 2:
    - 7 obligatorios Art. 16
    - 3 recomendados Art. 16
    - 5 Tier 1 criticos compliance APDP
    - 10 Tier 2 operativos
    Total: 25 campos. Penalizacion -1 si base legal != 'Otra' sin doc adjunto.

    Returns:
        int entre 0 y 100 (porcentaje redondeado).
    """
    obligatorios = [
        data.get("nombre_proceso"),
        data.get("categoria_datos"),
        data.get("categoria_titulares"),
        data.get("finalidad"),
        data.get("base_legal"),
        data.get("fuente_datos"),
        data.get("plazo_retencion"),
    ]
    recomendados = [
        data.get("medidas_seguridad"),
        data.get("destinatarios"),
        data.get("transferencia_datos"),
    ]
    tier1 = [
        data.get("nivel_confidencialidad"),
        data.get("estructura_dato"),
        data.get("datos_nna"),
        data.get("datos_anonimizados"),
        data.get("datos_seudonimizados"),
    ]
    tier2 = [
        data.get("sistema_almacenamiento"),
        data.get("volumen_titulares_estimado"),
        data.get("responsable_tratamiento_email"),
        data.get("ciclo_procesamiento"),
        data.get("automatizacion"),
        data.get("frecuencia"),
        data.get("transferencia_nacional"),
        data.get("doc_clausulas"),
        data.get("medidas_organizativas"),
        data.get("mecanismos_eliminacion"),
    ]
    todos = obligatorios + recomendados + tier1 + tier2
    total = len(todos)
    completados = sum(1 for c in todos if _truthy(c))

    # Penalizacion: base legal != 'Otra' sin documento adjunto
    base_legal = data.get("base_legal")
    if base_legal and str(base_legal).strip().lower() != "otra":
        if not data.get("archivo_base_legal_datos") and not data.get("archivo_base_legal_storage_url"):
            completados = max(completados - 1, 0)

    return round((completados / total) * 100) if total else 0


def calcular_nivel_riesgo(data: Mapping[str, Any]) -> str:
    """Calcula el nivel de riesgo ('bajo' | 'medio' | 'alto' | 'critico') del RAT.

    Mismo algoritmo que antes estaba en el modelo. Acepta Mapping para
    testabilidad sin BD.

    Returns:
        String entre {'bajo', 'medio', 'alto', 'critico'}.
    """
    score = 0

    if data.get("datos_sensibles"):
        score += 2

    estado_eipd = data.get("estado_eipd") or "pendiente"
    evaluacion_impacto = data.get("evaluacion_impacto")
    if evaluacion_impacto and estado_eipd != "completada":
        score += 2

    if data.get("decisiones_automatizadas"):
        score += 2

    if data.get("transferencia_internacional") and not data.get("garantias_transferencia_int"):
        score += 1

    tipo = (data.get("tipo_dato_sensible") or "").lower()
    if "biométric" in tipo or "biometric" in tipo or "menor" in tipo:
        score += 1

    if data.get("nombre_encargado") and not data.get("tiene_contrato_encargado"):
        score += 1

    vol = data.get("volumen_titulares_estimado") or 0
    if vol >= 100_000:
        score += 3   # Art. 15 bis: volumen masivo dispara EIPD
    elif vol >= 10_000:
        score += 2
    elif vol >= 1_000:
        score += 1

    if score >= UMBRAL_RIESGO_CRITICO:
        return "critico"
    if score >= UMBRAL_RIESGO_ALTO:
        return "alto"
    if score >= UMBRAL_RIESGO_MEDIO:
        return "medio"
    return "bajo"


# ── Wrappers de compatibilidad ────────────────────────────────────────────────
# Mantienen el comportamiento de los métodos de instancia para que
# código existente siga funcionando. Recomendado: migrar llamadores
# a usar las funciones puras cuando se refactorice cada endpoint.

def calcular_completitud_de_modelo(rat) -> int:
    """Wrapper para el método de instancia RAT.calcular_completitud()."""
    return calcular_completitud(_rat_a_dict(rat))


def calcular_nivel_riesgo_de_modelo(rat) -> str:
    """Wrapper para el método de instancia RAT.calcular_nivel_riesgo()."""
    return calcular_nivel_riesgo(_rat_a_dict(rat))


def rat_to_dict(rat) -> dict:
    """Convierte instancia SQLAlchemy RAT a dict plano para pasar al servicio puro.

    Sqlalchemy 2.x tiene __dict__ ya populated thanks to `expire_on_commit=False`
    pero hay columnas sensibles (bytes, JSON) que necesitamos pasar tal cual.
    Filtra las claves internas que empiezan con '_' (como _sa_instance_state).

    Uso:
        from app.services.rat_calculations import rat_to_dict, calcular_completitud
        rat = db.query(RAT).first()
        pct = calcular_completitud(rat_to_dict(rat))
    """
    if hasattr(rat, "__dict__"):
        return {k: v for k, v in rat.__dict__.items() if not k.startswith("_")}
    if hasattr(rat, "_asdict"):
        return dict(rat._asdict())
    return dict(rat)


def _rat_a_dict(rat) -> dict:
    """Compatibilidad hacia atras: alias de rat_to_dict.

    Mantener el nombre original privado para no romper nada.
    """
    return rat_to_dict(rat)
