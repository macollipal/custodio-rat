from datetime import datetime
from typing import Optional
from pydantic import BaseModel

ITEM_KEYS = [
    "item_a_politica",
    "item_b_responsable",
    "item_c_domicilio",
    "item_d_categorias",
    "item_e_medidas",
    "item_f_derechos_arco",
    "item_g_recurir_apdc",
    "item_h_transferencias",
    "item_i_conservacion",
    "item_j_fuente",
    "item_k_retirar_consentimiento",
    "item_l_decisiones_automatizadas",
]


class PoliticaTransparenciaUpdate(BaseModel):
    overrides: dict[str, Optional[str]]

    def model_post_init(self, __context) -> None:
        invalid = [k for k in self.overrides if k not in ITEM_KEYS]
        if invalid:
            raise ValueError(f"Claves de override inválidas: {invalid}. Permitidas: {ITEM_KEYS}")


class PoliticaTransparenciaOut(BaseModel):
    company_id: int
    nombre_empresa: str
    rut_empresa: str
    rubro: Optional[str] = None
    contacto_dpo: Optional[str] = None
    email_dpo: Optional[str] = None
    domicilio: Optional[str] = None
    version: str
    fecha_generacion: datetime
    hash_sha256: Optional[str] = None

    item_a_politica: Optional[str] = None
    item_b_responsable: Optional[str] = None
    item_c_domicilio: Optional[str] = None
    item_d_categorias: Optional[str] = None
    item_e_medidas: Optional[str] = None
    item_f_derechos_arco: Optional[str] = None
    item_g_recurir_apdc: Optional[str] = None
    item_h_transferencias: Optional[str] = None
    item_i_conservacion: Optional[str] = None
    item_j_fuente: Optional[str] = None
    item_k_retirar_consentimiento: Optional[str] = None
    item_l_decisiones_automatizadas: Optional[str] = None

    model_config = {"from_attributes": True}
