"""
Modelo TaskQueue: cola de tareas asincronas persistida en BD.
Permite ejecutar trabajos en background de forma durable.
Compatible con Vercel serverless: las tareas se ejecutan cuando un worker las reclama.
"""
from datetime import datetime, timezone
from enum import Enum as PyEnum

from sqlalchemy import DateTime, Enum, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class TaskStatus(str, PyEnum):
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"
    RETRYING = "retrying"


class TaskType(str, PyEnum):
    REVISAR_RATS_VENCIDOS = "revisar_rats_vencidos"
    NOTIFICAR_BRECHA_DPO = "notificar_brecha_dpo"
    NOTIFICAR_RESPUESTA_ARCO = "notificar_respuesta_arco"
    NOTIFICAR_VENCIMIENTO_RAT = "notificar_vencimiento_rat"
    CLEANUP_TOKENS = "cleanup_tokens"


class TaskQueue(Base):
    __tablename__ = "task_queue"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    task_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    status: Mapped[str] = mapped_column(
        Enum(TaskStatus), default=TaskStatus.PENDING, nullable=False, index=True
    )
    payload: Mapped[str] = mapped_column(Text, nullable=True)
    attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_attempts: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    last_error: Mapped[str] = mapped_column(Text, nullable=True)
    scheduled_for: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True
    )
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
