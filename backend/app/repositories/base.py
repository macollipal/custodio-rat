"""
Patrón Repository — Capa de acceso a datos.
Abstrae el acceso a la BD para facilitar testing y mantenimiento.

No elimina las queries existentes en services/routes — es aditivo.
Se migra incrementally: nuevo código usa repositories, viejo código sigue funcionando.
"""

from typing import TypeVar, Generic, Type, Optional, Sequence
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.database.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class Repository(Generic[ModelType]):
    """
    Repositorio genérico con operaciones CRUD básicas.
    Especializar con el modelo concreto, ej:
        class RATRepository(Repository[RAT]):
            ...
    """

    def __init__(self, model: Type[ModelType], db: Session):
        self._model = model
        self.db = db

    def get_by_id(self, id: int) -> Optional[ModelType]:
        return self.db.query(self._model).filter(self._model.id == id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> Sequence[ModelType]:
        return self.db.query(self._model).offset(skip).limit(limit).all()

    def count(self) -> int:
        return self.db.query(func.count(self._model.id)).scalar()

    def add(self, entity: ModelType) -> ModelType:
        self.db.add(entity)
        self.db.flush()
        self.db.refresh(entity)
        return entity

    def delete(self, entity: ModelType) -> None:
        self.db.delete(entity)
        self.db.flush()

    def save(self, entity: ModelType) -> ModelType:
        """Add or update depending on whether entity has id."""
        if entity.id:
            self.db.merge(entity)
            self.db.flush()
        else:
            self.db.add(entity)
            self.db.flush()
        return entity