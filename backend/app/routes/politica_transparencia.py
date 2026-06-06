"""
Endpoints públicos de Política de Transparencia (Art. 14 ter Ley 21.719 — REC-02).
No requieren autenticación — son de acceso público.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.politica_transparencia import PoliticaTransparenciaOut
from app.services.politica_transparencia_service import generar_politica

router = APIRouter(prefix="/publico/transparencia", tags=["Transparencia Pública"])


@router.get("/{company_id}", response_model=PoliticaTransparenciaOut, summary="Política de transparencia pública (Art. 14 ter — REC-02)")
def obtener_politica(
    company_id: int,
    db: Session = Depends(get_db),
):
    """Retorna la política de transparencia completa de una empresa. No requiere autenticación."""
    return generar_politica(db, company_id)
