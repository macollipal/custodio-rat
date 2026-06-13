"""
Schemas comunes reutilizables para toda la API.
"""

from typing import Generic, List, TypeVar, Optional
from pydantic import BaseModel


T = TypeVar("T")


class MessageResponse(BaseModel):
    message: str
    ok: bool = True


class OkResponse(BaseModel):
    ok: bool = True


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int

    class Config:
        populate_by_name = True


class DeleteResponse(BaseModel):
    ok: bool = True
    id: int