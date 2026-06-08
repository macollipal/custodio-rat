"""
Repository específico para RAT.
Incluye eager loading de relaciones para evitar N+1 queries.
"""

from typing import Optional, Sequence
from sqlalchemy.orm import Session, selectinload

from app.models.rat import RAT
from app.repositories.base import Repository


class RATRepository(Repository[RAT]):
    """Repository para el modelo RAT con optimizaciones de queries."""

    def __init__(self, db: Session):
        super().__init__(RAT, db)

    def get_all_by_company(
        self, company_id: int, skip: int = 0, limit: int = 200
    ) -> Sequence[RAT]:
        """Listar RATs de una empresa con relaciones precargadas."""
        return (
            self.db.query(RAT)
            .options(
                selectinload(RAT.company),
                selectinload(RAT.consentimientos),
            )
            .filter(RAT.company_id == company_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_with_relations(self, rat_id: int) -> Optional[RAT]:
        """Obtener RAT con todas sus relaciones cargadas."""
        return (
            self.db.query(RAT)
            .options(
                selectinload(RAT.company),
                selectinload(RAT.eipd),
                selectinload(RAT.consentimientos),
            )
            .filter(RAT.id == rat_id)
            .first()
        )

    def count_by_company(self, company_id: int) -> int:
        """Contar RATs de una empresa."""
        return self.db.query(RAT).filter(RAT.company_id == company_id).count()

    def get_by_company_and_estado(
        self, company_id: int, estado: str, skip: int = 0, limit: int = 200
    ) -> Sequence[RAT]:
        """Listar RATs por empresa y estado (con índice compuesto)."""
        return (
            self.db.query(RAT)
            .options(selectinload(RAT.company))
            .filter(RAT.company_id == company_id, RAT.estado == estado)
            .offset(skip)
            .limit(limit)
            .all()
        )