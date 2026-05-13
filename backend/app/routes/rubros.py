"""
Routes para Rubros y RATs Sugeridos.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.routes.deps import get_current_user
from app.models.rubro import Rubro
from app.models.rats_sugerido import RATSugerido
from app.schemas.rubro import RubroCreate, RubroUpdate, RubroOut
from app.schemas.rats_sugerido import RATSugeridoCreate, RATSugeridoUpdate, RATSugeridoOut

router = APIRouter(prefix="/rubros", tags=["Rubros"])


@router.get("", response_model=list[RubroOut], summary="Listar rubros ordenados")
def listar_rubros(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    rubos = db.query(Rubro).order_by(Rubro.orden.desc()).all()
    result = []
    for r in rubos:
        total = db.query(RATSugerido).filter(RATSugerido.rubro_id == r.id).count()
        out = RubroOut.model_validate(r)
        out.total_sugerencias = total
        result.append(out)
    return result


@router.post("", response_model=RubroOut, summary="Crear rubro (superadmin)")
def crear_rubro(payload: RubroCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.rol_global != "superadmin":
        raise HTTPException(status_code=403, detail="Solo superadmin puede crear rubros.")
    existente = db.query(Rubro).filter(Rubro.nombre == payload.nombre).first()
    if existente:
        raise HTTPException(status_code=409, detail="El rubro ya existe.")
    rubro = Rubro(nombre=payload.nombre, orden=payload.orden)
    db.add(rubro)
    db.commit()
    db.refresh(rubro)
    return rubro


@router.put("/{rubro_id}", response_model=RubroOut, summary="Editar rubro (superadmin)")
def editar_rubro(rubro_id: int, payload: RubroUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.rol_global != "superadmin":
        raise HTTPException(status_code=403, detail="Solo superadmin puede editar rubros.")
    rubro = db.query(Rubro).filter(Rubro.id == rubro_id).first()
    if not rubro:
        raise HTTPException(status_code=404, detail="Rubro no encontrado.")
    if payload.nombre is not None:
        rubro.nombre = payload.nombre
    if payload.orden is not None:
        rubro.orden = payload.orden
    db.commit()
    db.refresh(rubro)
    return rubro


@router.delete("/{rubro_id}", summary="Eliminar rubro (superadmin)")
def eliminar_rubro(rubro_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.rol_global != "superadmin":
        raise HTTPException(status_code=403, detail="Solo superadmin puede eliminar rubros.")
    rubro = db.query(Rubro).filter(Rubro.id == rubro_id).first()
    if not rubro:
        raise HTTPException(status_code=404, detail="Rubro no encontrado.")
    db.delete(rubro)
    db.commit()
    return {"ok": True}


@router.get("/{rubro_id}/sugerencias", response_model=list[RATSugeridoOut], summary="Sugerencias de RAT para un rubro")
def sugerencias_por_rubro(rubro_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    rubro = db.query(Rubro).filter(Rubro.id == rubro_id).first()
    if not rubro:
        raise HTTPException(status_code=404, detail="Rubro no encontrado.")
    return db.query(RATSugerido).filter(RATSugerido.rubro_id == rubro_id).all()


# --- Rutas para rats_sugeridos ---

router_sugeridos = APIRouter(prefix="/rats-sugeridos", tags=["RATs Sugeridos"])


@router_sugeridos.get("", response_model=list[RATSugeridoOut], summary="Listar todos los rats sugeridos")
def listar_sugerencias(rubro_id: Optional[int] = Query(None), db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    query = db.query(RATSugerido)
    if rubro_id is not None:
        query = query.filter(RATSugerido.rubro_id == rubro_id)
    if current_user.rol_global != "superadmin":
        query = query.filter(RATSugerido.rubro_id == current_user.empresa_id)
    return query.all()


@router_sugeridos.post("", response_model=RATSugeridoOut, summary="Crear sugerencia")
def crear_sugerencia(payload: RATSugeridoCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.rol_global not in ("superadmin", "admin_empresa"):
        raise HTTPException(status_code=403, detail="No tienes permisos.")
    if current_user.rol_global == "admin_empresa":
        from app.services.user_company_service import get_empresas_usuario
        empresas = get_empresas_usuario(db, current_user.id)
        if payload.rubro_id not in empresas:
            raise HTTPException(status_code=403, detail="Solo puedes crear sugerencias para tu rubro.")
    sugerencia = RATSugerido(**payload.model_dump())
    db.add(sugerencia)
    db.commit()
    db.refresh(sugerencia)
    return sugerencia


@router_sugeridos.put("/{sugerencia_id}", response_model=RATSugeridoOut, summary="Editar sugerencia")
def editar_sugerencia(sugerencia_id: int, payload: RATSugeridoUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.rol_global not in ("superadmin", "admin_empresa"):
        raise HTTPException(status_code=403, detail="No tienes permisos.")
    sugerencia = db.query(RATSugerido).filter(RATSugerido.id == sugerencia_id).first()
    if not sugerencia:
        raise HTTPException(status_code=404, detail="Sugerencia no encontrada.")
    if current_user.rol_global == "admin_empresa":
        from app.services.user_company_service import get_empresas_usuario
        empresas = get_empresas_usuario(db, current_user.id)
        if sugerencia.rubro_id not in empresas:
            raise HTTPException(status_code=403, detail="No puedes editar sugerencias de otros rubros.")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(sugerencia, key, value)
    db.commit()
    db.refresh(sugerencia)
    return sugerencia


@router_sugeridos.delete("/{sugerencia_id}", summary="Eliminar sugerencia")
def eliminar_sugerencia(sugerencia_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.rol_global not in ("superadmin", "admin_empresa"):
        raise HTTPException(status_code=403, detail="No tienes permisos.")
    sugerencia = db.query(RATSugerido).filter(RATSugerido.id == sugerencia_id).first()
    if not sugerencia:
        raise HTTPException(status_code=404, detail="Sugerencia no encontrada.")
    if current_user.rol_global == "admin_empresa":
        from app.services.user_company_service import get_empresas_usuario
        empresas = get_empresas_usuario(db, current_user.id)
        if sugerencia.rubro_id not in empresas:
            raise HTTPException(status_code=403, detail="No puedes eliminar sugerencias de otros rubros.")
    db.delete(sugerencia)
    db.commit()
    return {"ok": True}