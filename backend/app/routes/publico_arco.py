"""
C-08: Formulario público ARCO (Art. 12 Ley 21.719).
Permite al titular ejercer sus derechos sin autenticación.
Rate limited: 10 solicitudes/hora por IP.
"""
from typing import Optional, Literal

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, EmailStr, Field, model_validator
from sqlalchemy.orm import Session

from app.core.limiter import limiter
from app.database.database import get_db

router = APIRouter(prefix="/publico", tags=["Público ARCO"])

TipoArcoEnum = Literal[
    "acceso", "rectificacion", "cancelacion", "oposicion", "bloqueo", "portabilidad"
]

TIPO_LABELS = {
    "acceso": "Acceso",
    "rectificacion": "Rectificación",
    "cancelacion": "Cancelación / Supresión",
    "oposicion": "Oposición",
    "bloqueo": "Bloqueo temporal",
    "portabilidad": "Portabilidad",
}


class EmpresaPublicaOut(BaseModel):
    id: int
    nombre: str


class EjercerDerechosRequest(BaseModel):
    company_id: int
    tipo: TipoArcoEnum
    titular_nombre: str = Field(..., min_length=2, max_length=200)
    titular_email: EmailStr
    titular_rut: Optional[str] = Field(None, max_length=12)
    descripcion: str = Field(..., min_length=10, max_length=2000)
    telefono: Optional[str] = Field(None, max_length=50)
    representante_nombre: Optional[str] = Field(None, max_length=255)
    representante_rut: Optional[str] = Field(None, max_length=20)
    representante_poder_notarial_notas: Optional[str] = None

    @model_validator(mode="after")
    def validar_representante(self):
        if self.representante_nombre and not self.representante_poder_notarial_notas:
            raise ValueError(
                "Si hay representante, debe indicar las notas del poder notarial "
                "(representante_poder_notarial_notas)."
            )
        return self


class EjercerDerechosResponse(BaseModel):
    tracking_token: str
    mensaje: str


@router.get("/empresas", response_model=list[EmpresaPublicaOut])
def listar_empresas_publicas(db: Session = Depends(get_db)):
    """Lista empresas activas (id + nombre) para el formulario público ARCO."""
    from app.models.company import Company
    empresas = (
        db.query(Company.id, Company.nombre)
        .order_by(Company.nombre)
        .all()
    )
    return [EmpresaPublicaOut(id=e.id, nombre=e.nombre) for e in empresas]


@router.post(
    "/ejercer-derechos",
    response_model=EjercerDerechosResponse,
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit("10/hour")
def ejercer_derechos(
    request: Request,
    body: EjercerDerechosRequest,
    db: Session = Depends(get_db),
):
    """Crea solicitud ARCO pública del titular sin autenticación (Art. 12 Ley 21.719)."""
    from app.models.company import Company
    from app.services.ticket_service import crear_ticket

    empresa = db.query(Company).filter(Company.id == body.company_id).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada.")

    ticket = crear_ticket(
        db=db,
        company_id=body.company_id,
        tipo=body.tipo,
        titular_nombre=body.titular_nombre,
        titular_email=body.titular_email,
        titular_rut=body.titular_rut,
        descripcion=body.descripcion,
        telefono=body.telefono,
        origen="web",
        prioridad="normal",
        created_by="titular_publico",
        representante_nombre=body.representante_nombre,
        representante_rut=body.representante_rut,
        representante_poder_notarial_notas=body.representante_poder_notarial_notas,
    )

    tipo_label = TIPO_LABELS.get(body.tipo, body.tipo.upper())
    return EjercerDerechosResponse(
        tracking_token=ticket.tracking_token,
        mensaje=(
            f"Su solicitud de {tipo_label} fue recibida y está siendo procesada. "
            f"Recibirá confirmación en {body.titular_email}. "
            "Guarde su código de seguimiento para consultar el estado en cualquier momento."
        ),
    )
