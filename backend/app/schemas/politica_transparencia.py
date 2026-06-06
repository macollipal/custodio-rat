from datetime import datetime
from typing import Optional
from pydantic import BaseModel


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
