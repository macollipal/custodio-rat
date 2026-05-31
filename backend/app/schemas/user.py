from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    full_name: str
    password: str
    rol_global: str = "usuario"
    company_id: Optional[int] = None


class UserOut(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    is_active: bool
    rol_global: str
    created_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserOut


class TokenData(BaseModel):
    username: Optional[str] = None


class LoginRequest(BaseModel):
    username: str
    password: str


class PasswordChange(BaseModel):
    current_password: str
    new_password: str


class PasswordChangeOther(BaseModel):
    new_password: str
