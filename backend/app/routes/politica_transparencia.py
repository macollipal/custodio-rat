"""
Endpoints de Política de Transparencia (Art. 14 ter Ley 21.719 — REC-02).
GET público — sin autenticación.
PUT privado — requiere admin_empresa o superadmin (M-04 editor).
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.routes.deps import get_current_user
from app.schemas.politica_transparencia import PoliticaTransparenciaOut, PoliticaTransparenciaUpdate
from app.services.politica_transparencia_service import generar_politica, guardar_overrides

router = APIRouter(tags=["Transparencia"])


@router.get("/publico/transparencia/{company_id}", response_model=PoliticaTransparenciaOut, summary="Política de transparencia pública (Art. 14 ter — REC-02)")
def obtener_politica(
    company_id: int,
    db: Session = Depends(get_db),
):
    """Retorna la política de transparencia completa de una empresa. No requiere autenticación."""
    return generar_politica(db, company_id)


@router.put("/transparencia/{company_id}", response_model=PoliticaTransparenciaOut, summary="Editar política de transparencia (M-04)")
def actualizar_politica(
    company_id: int,
    body: PoliticaTransparenciaUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Guarda overrides por ítem. Valor null o vacío restaura el texto auto-generado."""
    if current_user.rol_global not in ("superadmin", "admin_empresa"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Se requiere rol admin_empresa o superadmin.")
    if current_user.rol_global == "admin_empresa":
        from app.services.user_company_service import get_empresas_usuario
        ids = get_empresas_usuario(db, current_user.id)
        if company_id not in ids:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sin acceso a esta empresa.")
    return guardar_overrides(db, company_id, body.overrides, usuario=current_user.username)
