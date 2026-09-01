from datetime import datetime, date
from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field, field_validator, model_validator
import json

from app.models.rat import EstadoRAT


# Categorías especiales de datos sensibles taxativas (Art. 4 Ley 21.719)
CATEGORIAS_SENSIBLES_ART4: list[str] = [
    "Origen étnico o racial",
    "Opiniones políticas",
    "Convicciones religiosas o filosóficas",
    "Afiliación sindical",
    "Datos genéticos",
    "Datos biométricos",
    "Datos relativos a la salud",
    "Vida u orientación sexual",
    "Condenas penales o delitos",
]

# Origen de los datos (Art. 14 ter lit. e): cuando no vienen del titular, hay obligación de informar
ORIGEN_DATOS_OPCIONES: list[str] = ["titular", "tercero", "fuente_publica", "mixto"]


class BaseLegal(str, Enum):
    """Base legal taxativa del Art. 13 Ley 21.719.

    Es string-Enum para serializar como string en JSON/API, pero provee
    type-safety en Python (autocomplete en IDE, validación de typos).
    """
    CONSENTIMIENTO = "Consentimiento del titular"
    CONTRATO = "Ejecución de contrato"
    OBLIGACION_LEGAL = "Obligación legal"
    INTERES_LEGITIMO = "Interés legítimo"
    INTERES_VITAL = "Interés vital del titular"
    INTERES_PUBLICO = "Misión de interés público"
    BIOMETRICOS = "Datos biométricos de identificación (Art. 16 BIS)"
    OTRA = "Otra"


# Lista plana para mantener compatibilidad con UI y serialización.
BASE_LEGAL_OPTIONS: list[str] = [b.value for b in BaseLegal]

# Descripciones para tooltip/documentación en UI.
BASE_LEGAL_DESCRIPCIONES: dict[str, str] = {
    BaseLegal.CONSENTIMIENTO.value: "Art. 12 — El titular autorizó expresamente el tratamiento de sus datos personales.",
    BaseLegal.CONTRATO.value: "Art. 13.2 — El tratamiento es necesario para la ejecución de un contrato.",
    BaseLegal.OBLIGACION_LEGAL.value: "Art. 13.3 — El tratamiento es necesario para cumplir una obligación legal.",
    BaseLegal.INTERES_LEGITIMO.value: "Art. 13.5 — Interés legítimo del responsable, documentado mediante test de 3 pasos.",
    BaseLegal.INTERES_VITAL.value: "Art. 13.4 — Interés vital del titular (salud, seguridad).",
    BaseLegal.INTERES_PUBLICO.value: "Art. 13.6 — Misión de interés público.",
    BaseLegal.BIOMETRICOS.value: "Art. 16 BIS — Datos biométricos para identificación inequívoca. Requiere EIPD obligatoria.",
    BaseLegal.OTRA.value: "Otra base legal no contemplada en las anteriores. Adjuntar documento legal que la justifique.",
}


class BaseLegalOptionsOut(BaseModel):
    opciones: list[str]
    descripciones: dict[str, str]


def _normalizar_test_il(val: Any) -> Optional[str]:
    """Normaliza test_interes_legitimo: acepta dict, JSON-string, o legacy string delimitado."""
    if val is None:
        return None
    if isinstance(val, dict):
        required = ["paso1", "paso2", "paso3"]
        if not all(k in val for k in required):
            raise ValueError(f"test_interes_legitimo como dict debe tener los campos: {required}")
        total = sum(len(str(v or "").strip()) for v in val.values())
        if total < 50:
            raise ValueError("El test de interés legítimo debe tener al menos 50 caracteres en total.")
        return json.dumps(val, ensure_ascii=False)
    if isinstance(val, str):
        val = val.strip()
        if not val:
            return None
        try:
            parsed = json.loads(val)
            if isinstance(parsed, dict):
                return _normalizar_test_il(parsed)
        except Exception:
            pass
    return val


class RATBase(BaseModel):
    nombre_proceso: str
    categoria_datos: str
    categoria_titulares: str = Field(..., min_length=3, description="Categoría de titulares (Art. 16 — obligatorio)")
    finalidad: str
    base_legal: str
    fuente_datos: str
    transferencia_datos: Optional[str] = None
    plazo_retencion: str
    medidas_seguridad: Optional[str] = None
    destinatarios: Optional[str] = None
    transferencia_internacional: bool = False
    pais_destino: Optional[str] = None
    garantias_transferencia_int: Optional[str] = None
    datos_sensibles: bool = False
    tipo_dato_sensible: Optional[str] = None
    evaluacion_impacto: bool = False
    estado_eipd: Optional[str] = "no_requerida"
    justificacion_no_aplica: Optional[str] = None
    fecha_eipd: Optional[date] = None
    decisiones_automatizadas: bool = False
    # Campos nuevos gaps Ley 21.719 (Iter 10)
    sistema_almacenamiento: Optional[str] = None
    volumen_titulares_estimado: Optional[int] = None
    operaciones_tratamiento: Optional[Any] = None
    logica_automatizada: Optional[str] = None
    responsable_tratamiento_email: Optional[str] = None
    # Campos Tier 1 - Gaps criticos (Iter 11)
    datos_nna: Optional[str] = None
    nivel_confidencialidad: Optional[str] = None
    estructura_dato: Optional[str] = None
    datos_anonimizados: bool = False
    datos_seudonimizados: bool = False
    # Origen de los datos (Art. 14 ter lit. e) — enum: titular/tercero/fuente_publica/mixto
    origen_datos: Optional[str] = None

    # Campos Tier 2 - Operativos (Iter 11)
    ciclo_procesamiento: Optional[str] = None
    automatizacion: Optional[str] = None
    frecuencia: Optional[str] = None
    transferencia_nacional: bool = False
    doc_clausulas: Optional[str] = None
    medidas_organizativas: Optional[str] = None
    mecanismos_eliminacion: Optional[str] = None
    tecnica_anonimizacion: Optional[str] = None
    origen_dato_portabilidad: Optional[str] = None
    fecha_levantamiento: Optional[date] = None
    nombre_encargado: Optional[str] = None
    tiene_contrato_encargado: bool = False
    test_interes_legitimo: Optional[str] = Field(
        default=None,
        description="Test de interés legítimo (Art. 16). Acepta JSON estructurado {paso1,paso2,paso3} o string legacy. Se normaliza a JSON en almacenamiento.",
    )
    observaciones_auditoria: Optional[str] = None
    # Documento de base legal (base64 para transporte; se almacena como binary en BD)
    archivo_base_legal_nombre: Optional[str] = None
    archivo_base_legal_tipo: Optional[str] = None
    archivo_base_legal_base64: Optional[str] = None
    archivo_base_legal_storage_url: Optional[str] = None

    @field_validator('responsable_tratamiento_email')
    @classmethod
    def responsable_email_valido(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        import re
        pattern = r'^[^@\s]+@[^@\s]+\.[^@\s]+$'
        if not re.match(pattern, v):
            raise ValueError("responsable_tratamiento_email debe tener formato de email válido")
        return v

    @field_validator('estado_eipd')
    @classmethod
    def estado_eipd_valido(cls, v: Optional[str]) -> Optional[str]:
        opciones = ["no_requerida", "no_requerida_justificada", "pendiente", "en_proceso", "completada"]
        if v is not None and v not in opciones:
            raise ValueError(f"estado_eipd debe ser uno de {opciones}")
        return v

    @field_validator('test_interes_legitimo', mode='before')
    @classmethod
    def test_interes_legitimo_normalizar(cls, v: Any) -> Any:
        return _normalizar_test_il(v)

    @model_validator(mode='after')
    def validar_anonimizado_mutex(self) -> 'RATBase':
        if self.datos_anonimizados and self.datos_seudonimizados:
            raise ValueError(
                "Un dato no puede ser simultáneamente anonimizado y seudonimizado: "
                "son técnicas mutuamente excluyentes (anonimización es irreversible; "
                "seudonimización mantiene la posibilidad de reidentificación)."
            )
        return self


class RATCreate(RATBase):
    company_id: int

    @field_validator("nombre_proceso")
    @classmethod
    def nombre_no_vacio(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("El nombre del proceso no puede estar vacío.")
        return v.strip()

    @field_validator("base_legal")
    @classmethod
    def base_legal_valida(cls, v: str) -> str:
        stripped = v.strip()
        if stripped not in BASE_LEGAL_OPTIONS:
            raise ValueError(
                f"base_legal debe ser una de las {len(BASE_LEGAL_OPTIONS)} opciones válidas "
                f"(Art. 13 Ley 21.719): {BASE_LEGAL_OPTIONS}"
            )
        return stripped

    @model_validator(mode='after')
    def validar_campos_condicionales(self) -> 'RATCreate':
        if self.transferencia_internacional:
            if not self.pais_destino or not self.pais_destino.strip():
                raise ValueError("pais_destino es requerido cuando transferencia_internacional=True")
            if not self.garantias_transferencia_int or not self.garantias_transferencia_int.strip():
                raise ValueError("garantias_transferencia_int es requerido cuando transferencia_internacional=True")
        if self.datos_sensibles and not self.tipo_dato_sensible:
            raise ValueError("tipo_dato_sensible es requerido cuando datos_sensibles=True")
        # Validar que tipo_dato_sensible use categorías taxativas del Art. 4 Ley 21.719
        if self.tipo_dato_sensible:
            cats = [c.strip() for c in self.tipo_dato_sensible.split(",") if c.strip()]
            invalidas = [c for c in cats if c not in CATEGORIAS_SENSIBLES_ART4]
            if invalidas:
                raise ValueError(
                    f"Las siguientes categorías no corresponden a categorías especiales del Art. 4 Ley 21.719: {invalidas}. "
                    f"Use las categorías oficiales: {CATEGORIAS_SENSIBLES_ART4}"
                )
        if self.decisiones_automatizadas and not self.logica_automatizada:
            raise ValueError("logica_automatizada es requerido cuando decisiones_automatizadas=True (Art. 8 Ley 21.719)")
        if self.origen_datos and self.origen_datos not in ORIGEN_DATOS_OPCIONES:
            raise ValueError(f"origen_datos debe ser uno de: {ORIGEN_DATOS_OPCIONES}")
        return self


class RATUpdate(RATBase):
    """H3.4 — Update DTO que hereda de RATBase.

    Todos los campos son opcionales via exclude_unset semantics.
    El servicio usa data.model_dump(exclude_none=True) para construir
    el payload de actualizacion SQL.

    NOTA: Los campos requeridos de RATBase (nombre_proceso, etc.) son
    validados solo si el cliente los envia. Esto se logra con el
    model_validator pre-processor que elimina campos requeridos vacios
    del payload antes de la validacion.
    """
    estado: Optional[EstadoRAT] = None
    archivo_base_legal_base64: Optional[str] = None

    @model_validator(mode='before')
    @classmethod
    def _strip_unset_required_fields(cls, data):
        """Permite que campos requeridos de RATBase sean opcionales en update.

        Campos con min_length > 1 necesitan placeholder para pasar validacion.
        Campos sin min_length se dejan como None para que exclude_unset=True
        en el servicio los excluya del model_dump.
        """
        if isinstance(data, dict):
            from app.schemas.rat import RATBase as _RATBase
            required_fields = [
                (name, field)
                for name, field in _RATBase.model_fields.items()
                if field.is_required()
            ]
            for field_name, field in required_fields:
                if field_name not in data or data[field_name] is None:
                    min_len = 1
                    for m in field.metadata:
                        if hasattr(m, 'min_length'):
                            min_len = m.min_length
                            break
                    placeholder = "." * max(min_len, 1)
                    data[field_name] = placeholder
        return data

    @model_validator(mode='before')
    @classmethod
    def validar_campos_condicionales_before(cls, data):
        if isinstance(data, dict):
            ti = data.get('transferencia_internacional')
            if ti is True:
                pais = data.get('pais_destino')
                garantias = data.get('garantias_transferencia_int')
                if not pais or not str(pais).strip():
                    raise ValueError("pais_destino es requerido cuando transferencia_internacional=True")
                if not garantias or not str(garantias).strip():
                    raise ValueError("garantias_transferencia_int es requerido cuando transferencia_internacional=True")
            # Validar categorías sensibles si se envían explícitamente en el update
            tipo_sensible = data.get('tipo_dato_sensible')
            if tipo_sensible and isinstance(tipo_sensible, str):
                cats = [c.strip() for c in tipo_sensible.split(",") if c.strip()]
                invalidas = [c for c in cats if c not in CATEGORIAS_SENSIBLES_ART4]
                if invalidas:
                    raise ValueError(
                        f"Categorías no reconocidas por Art. 4 Ley 21.719: {invalidas}. "
                        f"Opciones válidas: {CATEGORIAS_SENSIBLES_ART4}"
                    )
            # Validar logica_automatizada cuando decisiones_automatizadas=True
            if data.get('decisiones_automatizadas') is True and not data.get('logica_automatizada'):
                raise ValueError("logica_automatizada es requerido cuando decisiones_automatizadas=True (Art. 8 Ley 21.719)")
            # Validar origen_datos si se envía
            origen = data.get('origen_datos')
            if origen and origen not in ORIGEN_DATOS_OPCIONES:
                raise ValueError(f"origen_datos debe ser uno de: {ORIGEN_DATOS_OPCIONES}")
        return data


class RATOut(RATBase):
    id: int
    company_id: int
    estado: EstadoRAT
    aprobado_por: Optional[str] = None
    fecha_aprobacion: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    completitud: Optional[int] = None
    nivel_riesgo: Optional[str] = None
    # Indica si existe documento de base legal (el contenido no se transmite por JSON)
    tiene_archivo_base_legal: bool = False

    model_config = {"from_attributes": True}


class RATSugerencia(BaseModel):
    tipo_proceso: str


class SugerenciasTiposOut(BaseModel):
    """H2.3 — Response model para GET /rats/sugerencias/tipos."""
    tipos: list[str]


class RATSugerenciaOut(BaseModel):
    tipo_proceso: str
    categoria_datos: str
    categoria_titulares: str
    finalidad: str
    base_legal: str
    plazo_retencion_sugerido: str
    datos_sensibles: bool
    tipo_dato_sensible: Optional[str] = None
    evaluacion_impacto: Optional[bool] = None
    decisiones_automatizadas: Optional[bool] = None
    observacion: str


class TestInteresLegitimo(BaseModel):
    paso1_interes_legitimo: str
    paso2_necesidad: str
    paso3_balance: str


class ReportesResponse(BaseModel):
    total: int
    skip: int
    limit: int
    sort_by: str
    sort_order: str
    filtros_aplicados: dict
    rats: list[RATOut]
