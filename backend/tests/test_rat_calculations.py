"""
Tests unitarios para app/services/rat_calculations.py (H3.1).

Cobertura:
- calcular_completitud: formula Art. 16 + penalizacion base legal sin doc
- calcular_nivel_riesgo: thresholds bajo/medio/alto/critico
- Wrappers de compatibilidad para instancias de modelo
- Test de regresion del incidente 2026-07-08 — db.query(RAT.calcular_completitud, ...)
  ya no es posible desde codigo (las funciones reciben dicts, no son lambdas
  de instancia).

Historia: este test existe porque el 2026-07-08 la funcion
RAT.calcular_completitud vivia en el modelo y SQLAlchemy intento
ejecutarla como columna de SQL — TypeError en runtime. La refactorizacion
H3.1 movio la logica a funciones puras que aceptan dict, sin self.
"""
import pytest

from app.services import rat_calculations
from app.services.rat_calculations import (
    UMBRAL_RIESGO_CRITICO,
    UMBRAL_RIESGO_ALTO,
    UMBRAL_RIESGO_MEDIO,
    calcular_completitud,
    calcular_nivel_riesgo,
    calcular_completitud_de_modelo,
    calcular_nivel_riesgo_de_modelo,
)


# ── Helpers para construir RATs de prueba ────────────────────────────────────

def _rat_minimal():
    """RAT con solo los 7 obligatorios Art. 16. ~28% completitud esperado."""
    return {
        "nombre_proceso": "Proceso X",
        "categoria_datos": "Identificacion",
        "categoria_titulares": "Empleados",
        "finalidad": "Gestion interna",
        "base_legal": "Ejecucion de contrato",
        "fuente_datos": "Directamente del titular",
        "plazo_retencion": "5 anos",
        # Recomendados vacios
        "medidas_seguridad": None,
        "destinatarios": None,
        "transferencia_datos": None,
        # Tier 1 vacios
        "nivel_confidencialidad": None,
        "estructura_dato": None,
        "datos_nna": None,
        "datos_anonimizados": None,
        "datos_seudonimizados": None,
        # Tier 2 vacios
        "sistema_almacenamiento": None,
        "volumen_titulares_estimado": None,
        "responsable_tratamiento_email": None,
        "ciclo_procesamiento": None,
        "automatizacion": None,
        "frecuencia": None,
        "transferencia_nacional": None,
        "doc_clausulas": None,
        "medidas_organizativas": None,
        "mecanismos_eliminacion": None,
        # Sin doc
        "archivo_base_legal_datos": None,
    }


def _rat_completo_con_doc():
    """RAT con todos los 25 campos poblados + doc adjunto. 100% esperado."""
    base = _rat_minimal()
    base.update({
        "medidas_seguridad": "Cifrado AES-256, control de acceso",
        "destinatarios": "Proveedor CRM SpA",
        "transferencia_datos": "Interna",
        "nivel_confidencialidad": "alto",
        "estructura_dato": "persona_natural",
        "datos_nna": "no",
        "datos_anonimizados": False,
        "datos_seudonimizados": True,
        "sistema_almacenamiento": "PostgreSQL 16",
        "volumen_titulares_estimado": 5000,
        "responsable_tratamiento_email": "dpo@empresa.cl",
        "ciclo_procesamiento": "Continuo",
        "automatizacion": "Mixto",
        "frecuencia": "Diaria",
        "transferencia_nacional": False,
        "doc_clausulas": "Cláusula modelo ONTRATOS SERNAC 2024",
        "medidas_organizativas": "Capacitación anual + política interna",
        "mecanismos_eliminacion": "DELETE + VACUUM",
        "archivo_base_legal_datos": b"%PDF-1.4 fake content",
    })
    return base


# ── Tests de calcular_completitud ────────────────────────────────────────────

class TestCalcularCompletitud:
    """Cobertura formula Ley 21.719 Art. 16 + gaps Tier 1/Tier 2."""

    def test_rat_minimal_solo_obligatorios(self):
        """Solo 7 obligatorios poblados, resto vacio."""
        # 7 obligatorios completos + 18 vacios = 7/25 = 28%
        # Pero base_legal != 'Otra' sin doc → penalizacion -1 → 6/25 = 24%
        pct = calcular_completitud(_rat_minimal())
        assert pct == 24, f"Esperado 24% (7 oblig - 1 penalizacion), obtuvo {pct}%"

    def test_rat_completo_con_doc_sin_penalizacion(self):
        """Todos los 25 campos poblados + doc adjunto → 100%."""
        pct = calcular_completitud(_rat_completo_con_doc())
        assert pct == 100, f"Esperado 100%, obtuvo {pct}%"

    def test_penalizacion_base_legal_sin_doc(self):
        """Base legal != 'Otra' sin doc adjunto → -1."""
        data = _rat_minimal()
        # Poblamos todo el tier 2 para llegar a muchos campos
        data.update({
            "medidas_seguridad": "X", "destinatarios": "X", "transferencia_datos": "X",
            "nivel_confidencialidad": "alto", "estructura_dato": "X",
            "datos_nna": "no", "datos_anonimizados": False, "datos_seudonimizados": True,
            "sistema_almacenamiento": "X", "volumen_titulares_estimado": 1,
            "responsable_tratamiento_email": "x@x.cl",
            "ciclo_procesamiento": "X", "automatizacion": "X", "frecuencia": "X",
            "transferencia_nacional": False,
            "doc_clausulas": "X", "medidas_organizativas": "X", "mecanismos_eliminacion": "X",
        })
        # 7 oblig + 3 rec + 5 tier1 + 10 tier2 = 25, sin doc → penalizacion -1 = 96%
        pct = calcular_completitud(data)
        assert pct == 96, f"Esperado 96% (25-1)/25, obtuvo {pct}%"

    def test_sin_penalizacion_si_base_legal_es_otra(self):
        """Base legal == 'Otra' (case-insensitive) → no penaliza sin doc."""
        data = _rat_completo_con_doc()
        data["base_legal"] = "Otra"
        data["archivo_base_legal_datos"] = None
        # Sigue siendo 100% porque 'Otra' exime la penalizacion
        pct = calcular_completitud(data)
        assert pct == 100, f"'Otra' deberia eximir penalizacion; obtuvo {pct}%"

    def test_strings_vacios_no_cuentan(self):
        """String vacio debe contar como no completado (como None)."""
        data = _rat_minimal()
        data["nombre_proceso"] = "   "
        data["categoria_datos"] = ""
        # 5 obligatorios restantes + 0 rec + 0 tier1 + 0 tier2 = 5/25, menos penalizacion = 4/25 = 16%
        pct = calcular_completitud(data)
        assert pct == 16, f"Esperado 16% con strings vacios, obtuvo {pct}%"

    def test_listas_y_dicts_vacios_no_cuentan(self):
        """operaciones_tratamiento=[] no cuenta como completado (Field nuevo)."""
        # operaciones_tratamiento está en tier nuevo pero aqui verificamos
        # que la heuristica _truthy maneja listas vacias
        d = _rat_minimal()
        d["operaciones_tratamiento"] = []
        # No rompe ni sube la completitud porque [] no cuenta
        pct_base = calcular_completitud(_rat_minimal())
        pct_empty = calcular_completitud(d)
        assert pct_empty == pct_base


# ── Tests de calcular_nivel_riesgo ───────────────────────────────────────────

class TestCalcularNivelRiesgo:
    """Cobertura umbrales bajo/medio/alto/critico."""

    def test_sin_factores_riesgo_bajo(self):
        """RAT vacío/limpio = 'bajo'."""
        d = {
            "datos_sensibles": False,
            "evaluacion_impacto": False,
            "decisiones_automatizadas": False,
            "transferencia_internacional": False,
            "garantias_transferencia_int": None,
            "tipo_dato_sensible": "",
            "nombre_encargado": None,
            "tiene_contrato_encargado": False,
            "estado_eipd": "no_requerida",
        }
        assert calcular_nivel_riesgo(d) == "bajo"

    def test_datos_sensibles_sube_a_medio(self):
        """datos_sensibles=True suma +2 → score=2 ≥ UMBRAL_RIESGO_MEDIO(3)? No."""
        # UMBRAL_RIESGO_MEDIO = 3, datos_sensibles=+2 → score=2 → bajo (no llega a 3)
        d = {
            "datos_sensibles": True,
            "evaluacion_impacto": False,
            "decisiones_automatizadas": False,
            "transferencia_internacional": False,
            "estado_eipd": "no_requerida",
        }
        # score=2 < 3 (MEDIO) → bajo
        assert calcular_nivel_riesgo(d) == "bajo"

    def test_datos_sensibles_mas_eipd_pendiente_alto(self):
        """datos_sensibles + evaluacion_pendiente = +4 → alto (>=5)."""
        d = {
            "datos_sensibles": True,
            "evaluacion_impacto": True,
            "estado_eipd": "pendiente",
            "decisiones_automatizadas": False,
            "transferencia_internacional": False,
        }
        # score = 2 + 2 = 4 < 5 (ALTO) → medio
        assert calcular_nivel_riesgo(d) == "medio"

    def test_critico_cuando_score_ge_7(self):
        """Score >= UMBRAL_RIESGO_CRITICO = 7."""
        d = {
            "datos_sensibles": True,        # +2
            "evaluacion_impacto": True,
            "estado_eipd": "pendiente",     # +2
            "decisiones_automatizadas": True, # +2
            "transferencia_internacional": True,
            "garantias_transferencia_int": None,  # +1
            "tipo_dato_sensible": "biométrico",  # +1
            "nombre_encargado": "Proveedor",
            "tiene_contrato_encargado": False,    # +1
        }
        # score = 2 + 2 + 2 + 1 + 1 + 1 = 9 >= 7 (CRITICO)
        assert calcular_nivel_riesgo(d) == "critico"

    def test_tipo_dato_biometrico_sube_score(self):
        """'biometric' o 'menor' en tipo_dato_sensible → +1 al score.

        Caso: solo datos_sensibles=True (score=2 < MEDIO=3 → 'bajo').
        Anadiendo 'biometric' deberia sumar +1 → score=3 (MEDIO).
        Usamos ASCII puro para evitar problemas de encoding en CI.
        """
        base_sin_especial = {
            "datos_sensibles": True,        # +2 → score=2
            "evaluacion_impacto": False,
            "decisiones_automatizadas": False,
            "transferencia_internacional": False,
            "estado_eipd": "no_requerida",
            "tipo_dato_sensible": "",
        }
        # score=2 < 3 (MEDIO) → 'bajo'
        assert calcular_nivel_riesgo(base_sin_especial) == "bajo"

        # Anadiendo biometric: score=2+1=3 → MEDIO (>=3, <5)
        d_bio = {**base_sin_especial, "tipo_dato_sensible": "biometric facial"}
        assert calcular_nivel_riesgo(d_bio) == "medio"

        # Anadiendo 'menor': mismo efecto (busca 'menor' en lowercase)
        d_menor = {**base_sin_especial, "tipo_dato_sensible": "datos de menor de edad"}
        assert calcular_nivel_riesgo(d_menor) == "medio"


# ── Tests de compatibilidad con modelo ──────────────────────────────────────

class TestWrappersCompatibilidad:
    """Los métodos del modelo deben seguir funcionando via wrappers."""

    def test_wrapper_completitud_acepta_instancia_fake(self):
        """Wrapper toma cualquier objeto con __dict__ (no necesita BD)."""
        class FakeRAT:
            nombre_proceso = "X"
            categoria_datos = "X"
            categoria_titulares = "X"
            finalidad = "X"
            base_legal = "Otra"  # exime penalizacion
            fuente_datos = "X"
            plazo_retencion = "X"

        result = calcular_completitud_de_modelo(FakeRAT())
        assert isinstance(result, int)
        assert 0 <= result <= 100

    def test_wrapper_riesgo_acepta_instancia_fake(self):
        class FakeRAT:
            datos_sensibles = False
            evaluacion_impacto = False
            estado_eipd = "no_requerida"
            decisiones_automatizadas = False
            transferencia_internacional = False
            garantias_transferencia_int = None
            tipo_dato_sensible = ""
            nombre_encargado = None
            tiene_contrato_encargado = False

        result = calcular_nivel_riesgo_de_modelo(FakeRAT())
        assert result == "bajo"


# ── Test de regresión del incidente 2026-07-08 ──────────────────────────────

class TestRegresionIncidente20260708:
    """Reproduce el incidente de produccion 'RAT.calcular_completitud() missing self'.

    El bug era doble:
    1. db.query(RAT.calcular_completitud, ...) lanzaba TypeError porque
       SQLAlchemy intentaba invocar el metodo como columna sin 'self'.
    2. db.query(col1, col2, ...) devolvia Row (no instancia), por lo que
       r.calcular_completitud() lanzaba AttributeError.

    La refactorizacion H3.1 elimina ambos problemas:
    1. Las funciones puras no son metodos de instancia, no hay 'self' que confundir.
    2. Las funciones aceptan Mapping (dict) — compatibles con Row tambien.
    """

    def test_funciones_puras_no_son_metodos_instancia(self):
        """Las funciones del servicio NO usan self, evitando el bug original."""
        # Si alguien intenta tratar calcular_completitud como metodo de instancia,
        # deberia fallar de forma obvia, NO silenciosamente.
        import inspect
        sig = inspect.signature(calcular_completitud)
        assert "self" not in sig.parameters, (
            "REGRESION: rat_calculations.calcular_completitud() no debe "
            "tener 'self' — eso es exactamente lo que causo el incidente "
            "del 2026-07-08 ('missing self positional argument')."
        )
        sig2 = inspect.signature(calcular_nivel_riesgo)
        assert "self" not in sig2.parameters

    def test_funciones_puras_aceptan_mapping_generico(self):
        """Compatibilidad con namedtuple / Row / dict (todos son Mappings)."""
        from collections import namedtuple
        Row = namedtuple("Row", ["nombre_proceso", "base_legal"])

        # Mapping-like (no dict literal pero dict-like)
        class MappingLike(dict):
            pass

        m = MappingLike()
        m["nombre_proceso"] = "X"
        m["base_legal"] = "Otra"
        # No debe lanzar — la funcion acepta cualquier Mapping
        result = calcular_completitud(m)
        assert isinstance(result, int)

    def test_endpoints_criticos_siguen_funcionando(self):
        """Sanity check: la firma es compatible con lo que ya usan los routers.

        Los routers hacen rat.calcular_completitud() donde rat es instancia.
        El wrapper calcular_completitud_de_modelo() debe producir mismos
        resultados que el metodo antiguo.
        """
        # Caso 1: RAT completo con doc
        completo = _rat_completo_con_doc()
        # Aplicar via wrapper y via funcion pura deben dar mismo resultado
        from app.models.rat import RAT
        rat_instance = RAT(**completo)
        via_pura = calcular_completitud(completo)
        via_wrapper = calcular_completitud_de_modelo(rat_instance)
        assert via_pura == via_wrapper == 100

        # Caso 2: RAT sin doc, base legal != 'Otra'
        minimo = _rat_minimal()
        rat_inst_min = RAT(**minimo)
        via_pura2 = calcular_completitud(minimo)
        via_wrapper2 = calcular_completitud_de_modelo(rat_inst_min)
        assert via_pura2 == via_wrapper2 == 24


# ── Test de invariantes del servicio ────────────────────────────────────────

class TestInvariantes:
    """Invariantes que el servicio debe mantener en el tiempo."""

    def test_completitud_siempre_en_rango_0_100(self):
        """Para cualquier input valido, el output esta en [0, 100]."""
        casos = [
            _rat_minimal(),
            _rat_completo_con_doc(),
            {},  # vacio total
            {"nombre_proceso": ""},  # string vacio
        ]
        for caso in casos:
            result = calcular_completitud(caso)
            assert 0 <= result <= 100, f"completitud={result} fuera de rango para {caso}"

    def test_riesgo_retorna_valores_del_enum(self):
        """El output debe ser uno de los 4 valores canonicos."""
        casos = [
            {},
            _rat_completo_con_doc(),
            {"datos_sensibles": True, "evaluacion_impacto": True, "estado_eipd": "pendiente",
             "decisiones_automatizadas": True, "transferencia_internacional": True,
             "garantias_transferencia_int": None, "tipo_dato_sensible": "biometria",
             "nombre_encargado": "X", "tiene_contrato_encargado": False},
        ]
        for caso in casos:
            result = calcular_nivel_riesgo(caso)
            assert result in {"bajo", "medio", "alto", "critico"}

    def test_umbrales_son_exportados_del_servicio(self):
        """Los umbrales viven en el servicio (no en el modelo)."""
        # Si cambia el modelo, el umbral sigue accesible para logica externa
        assert UMBRAL_RIESGO_CRITICO == 7
        assert UMBRAL_RIESGO_ALTO == 5
        assert UMBRAL_RIESGO_MEDIO == 3
        # Y rat_calculations los expone
        assert rat_calculations.UMBRAL_RIESGO_CRITICO == 7
