from datetime import datetime
from pydantic import BaseModel
from app.models.user_company import RolEmpresa


class UserCompanyCreate(BaseModel):
    username: str
    rol: RolEmpresa = RolEmpresa.EDITOR


class UserCompanyOut(BaseModel):
    id:         int
    user_id:    int
    company_id: int
    rol:        RolEmpresa
    created_at: datetime
    username:   str
    full_name:  str
    email:      str

    model_config = {"from_attributes": True}


class UserCompanyUpdate(BaseModel):
    rol: RolEmpresa
