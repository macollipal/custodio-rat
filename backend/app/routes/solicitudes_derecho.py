from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.solicitud_derecho import SolicitudDerecho, TipoSolicitud, EstadoSolicitud

router = APIRouter(prefix="/solicitudes-derecho", tags=["Solicitudes de Derecho"])


@router.get("/")
def listar_solicitudes(db: Session = Depends(get_db)):
    return []


@router.get("/{solicitud_id}")
def obtener_solicitud(solicitud_id: int, db: Session = Depends(get_db)):
    raise HTTPException(status_code=404, detail="No implementado")
