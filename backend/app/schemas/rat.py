from datetime import datetime, date
from typing import Any, Optional
from pydantic import BaseModel, Field, field_validator, model_validator
import json

from app.models.rat import EstadoRAT


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

    @field_validator('estado_eipd')
    @classmethod
    def estado_eipd_valido(cls, v: Optional[str]) -> Optional[str]:
        opciones = ["no_requerida", "no_requerida_justificada", "pendiente", "en_proceso", "completada"]
        if v is not None and v not in opciones:
            raise ValueError(f"estado_eipd debe ser uno de {opciones}")
        return v

    @field_validator('responsable_tratamiento_email')
    @classmethod
    def email_formato_responsable(cls, v: Optional[str]) -> Optional[str]:
        import re
        if v and v.strip():
            patron = r'^[\w.\-]+@[\w.\-]+\.\w{2,}$'
            if not re.match(patron, v.strip()):
                raise ValueError("responsable_tratamiento_email debe ser un email válido (ej: dpo@empresa.cl)")
        return v

    @field_validator('test_interes_legitimo', mode='before')
    @classmethod
    def test_interes_legitimo_normalizar(cls, v: Any) -> Any:
        return _normalizar_test_il(v)


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
        opciones_validas = [
            "Consentimiento del titular",
            "Ejecución de contrato",
            "Obligación legal",
            "Interés legítimo",
            "Interés vital del titular",
            "Misión de interés público",
            "Otra",
        ]
        stripped = v.strip()
        if stripped not in opciones_validas:
            raise ValueError(f"base_legal debe ser una de las opciones válidas: {opciones_validas}")
        return stripped

    @model_validator(mode='after')
    def validar_campos_condicionales(self) -> 'RATCreate':
        if self.transferencia_internacional:
            if not self.pais_destino or not self.pais_destino.strip():
                raise ValueError("pais_destino es requerido cuando transferencia_internacional=True")
            if not self.garantias_transferencia_int or not self.garantias_transferencia_int.strip():
                raise ValueError("garantias_transferencia_int es requerido cuando transferencia_internacional=True")
        if self.decisiones_automatizadas:
            if not self.logica_automatizada or not self.logica_automatizada.strip():
                raise ValueError("logica_automatizada es requerido cuando decisiones_automatizadas=True")
        if self.datos_sensibles and not self.tipo_dato_sensible:
            raise ValueError("tipo_dato_sensible es requerido cuando datos_sensibles=True")
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
        """Permite que campos requeridos de RATBase sean opcionales en update."""
        if isinstance(data, dict):
            # Si el cliente no envia un campo requerido, no validarlo
            # Pydantic requiere que el campo este presente (no None) si es required
            # Workaround: removemos campos requeridos que vienen vacios/None
            from app.schemas.rat import RATBase as _RATBase
            required_fields = [
                name for name, field in _RATBase.model_fields.items()
                if field.is_required()
            ]
            for field_name in required_fields:
                if field_name not in data or data[field_name] is None:
                    data.setdefault(field_name, "")
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
            da = data.get('decisiones_automatizadas')
            if da is True:
                logica = data.get('logica_automatizada')
                if not logica or not str(logica).strip():
                    raise ValueError("logica_automatizada es requerido cuando decisiones_automatizadas=True")
            ds = data.get('datos_sensibles')
            if ds is True:
                tipo = data.get('tipo_dato_sensible')
                if not tipo or not str(tipo).strip():
                    raise ValueError("tipo_dato_sensible es requerido cuando datos_sensibles=True")
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
