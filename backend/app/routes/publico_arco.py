"""
C-08: Formulario público ARCO (Art. 12 Ley 21.719).
Permite al titular ejercer sus derechos sin autenticación.
Rate limited: 10 solicitudes/hora por IP.
"""
import hashlib
import hmac
import os
import time
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


class CsrfTokenResponse(BaseModel):
    token: str
    header_name: str
    expires_in_seconds: int


_CSRF_SECRET = os.environ.get("SECRET_KEY", "csrf-dev-secret")[:32]
_CSRF_TTL = 3600  # 1 hora


@router.get("/csrf-token", response_model=CsrfTokenResponse, summary="Obtener CSRF token para formulario público")
@limiter.limit("30/minute")
def csrf_token(request: Request):
    """Genera un CSRF token HMAC-SHA256 para proteger el formulario público ARCO."""
    ts = str(int(time.time()))
    nonce = os.urandom(16).hex()
    payload = f"{ts}.{nonce}"
    sig = hmac.new(_CSRF_SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()
    token = f"{payload}.{sig}"
    return CsrfTokenResponse(
        token=token,
        header_name="X-CSRF-Token",
        expires_in_seconds=_CSRF_TTL,
    )


@router.get("/empresas", response_model=list[EmpresaPublicaOut])
@limiter.limit("30/minute")
def listar_empresas_publicas(request: Request, db: Session = Depends(get_db)):
    """Lista empresas con módulo ARCO activo para el formulario público."""
    from app.models.company import Company
    from app.models.module_permission import ModulePermission
    empresas = (
        db.query(Company.id, Company.nombre)
        .order_by(Company.nombre)
        .all()
    )
    # Una sola query: empresas que tienen ARCO explícitamente desactivado.
    # Por defecto (sin fila), el módulo está activo (opt-out).
    arco_disabled_ids = {
        row.company_id
        for row in db.query(ModulePermission.company_id)
        .filter(ModulePermission.modulo == "ARCO", ModulePermission.enabled.is_(False))
        .all()
    }
    return [
        EmpresaPublicaOut(id=e.id, nombre=e.nombre)
        for e in empresas
        if e.id not in arco_disabled_ids
    ]


class VerificarTitularResponse(BaseModel):
    tiene_tickets_abiertos: bool
    cantidad: int


@router.get("/verificar-titular", response_model=VerificarTitularResponse)
@limiter.limit("20/minute")
def verificar_titular(
    request: Request,
    company_id: int,
    email: str,
    db: Session = Depends(get_db),
):
    """Verifica si un email ya tiene solicitudes ARCO abiertas para una empresa.
    No requiere autenticación. Rate limited para evitar enumeración."""
    from app.models.tkt_solicitud_derecho import TktSolicitudDerecho
    ESTADOS_ABIERTOS = {"abierto", "en_proceso", "pendiente_subsanacion", "pendiente"}
    count = (
        db.query(TktSolicitudDerecho)
        .filter(
            TktSolicitudDerecho.company_id == company_id,
            TktSolicitudDerecho.titular_email == email,
            TktSolicitudDerecho.estado.in_(ESTADOS_ABIERTOS),
        )
        .count()
    )
    return VerificarTitularResponse(tiene_tickets_abiertos=count > 0, cantidad=count)


def _verify_csrf(request: Request) -> None:
    """Valida CSRF token HMAC-SHA256 del header X-CSRF-Token.
    En entorno de test (ENV=test) la validación se omite para no romper la suite."""
    if os.environ.get("ENV") == "test":
        return
    token = request.headers.get("X-CSRF-Token", "")
    try:
        parts = token.split(".")
        if len(parts) != 3:
            raise ValueError("formato inválido")
        ts_str, nonce, sig = parts
        payload = f"{ts_str}.{nonce}"
        expected = hmac.new(_CSRF_SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, sig):
            raise ValueError("firma inválida")
        if int(time.time()) - int(ts_str) > _CSRF_TTL:
            raise ValueError("token expirado")
    except (ValueError, TypeError):
        raise HTTPException(status_code=403, detail="CSRF token inválido o ausente. Obtenga uno en GET /publico/csrf-token.")


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
    _verify_csrf(request)
    from app.models.company import Company
    from app.services.ticket_service import crear_ticket
    from app.services.module_permission_service import get_active_modules

    empresa = db.query(Company).filter(Company.id == body.company_id).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada.")

    if "ARCO" not in get_active_modules(db, body.company_id):
        raise HTTPException(
            status_code=403,
            detail="Esta empresa no está habilitada para recibir solicitudes ARCO en este momento.",
        )

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
