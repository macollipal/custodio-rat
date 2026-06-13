"""
Endpoints para gestionar la cola de tareas asincronas.
- POST /admin/tasks/run: procesa las tareas pendientes (llamado por cron externo)
- GET  /admin/tasks: lista el estado de la cola
- GET  /admin/tasks/stats: estadísticas
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.task import TaskQueue, TaskStatus
from app.services.task_service import process_pending_tasks, enqueue_task
from app.schemas.admin_tasks import (
    TaskListResponse, TaskStatsResponse, TaskRunResponse, TaskEnqueueResponse,
)

router = APIRouter(prefix="/admin/tasks", tags=["Admin - Tareas Asíncronas"])


def _get_user():
    from app.routes.deps import get_current_user as _u
    return _u()


class EnqueueRequest(BaseModel):
    task_type: str
    payload: dict = {}
    max_attempts: int = 3


@router.get("/", response_model=TaskListResponse, summary="Listar tareas de la cola")
async def listar_tareas(
    status: str = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user=Depends(_get_user),
):
    """Lista las tareas en la cola. Solo para diagnostico."""
    if current_user.rol_global != "superadmin":
        raise HTTPException(status_code=403, detail="Solo superadmin puede ver la cola")

    q = db.query(TaskQueue)
    if status:
        q = q.filter(TaskQueue.status == status)
    total = q.count()
    items = q.order_by(TaskQueue.scheduled_for.desc()).offset(skip).limit(limit).all()

    return TaskListResponse(
        tasks=[
            {
                "id": t.id,
                "task_type": t.task_type,
                "status": t.status,
                "attempts": t.attempts,
                "max_attempts": t.max_attempts,
                "last_error": t.last_error,
                "scheduled_for": t.scheduled_for.isoformat() if t.scheduled_for else None,
                "started_at": t.started_at.isoformat() if t.started_at else None,
                "completed_at": t.completed_at.isoformat() if t.completed_at else None,
            }
            for t in items
        ],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/stats", response_model=TaskStatsResponse, summary="Estadísticas de la cola")
async def stats(
    db: Session = Depends(get_db),
    current_user=Depends(_get_user),
):
    if current_user.rol_global != "superadmin":
        raise HTTPException(status_code=403, detail="Solo superadmin puede ver estadísticas")

    from sqlalchemy import func
    rows = (
        db.query(TaskQueue.status, func.count(TaskQueue.id))
        .group_by(TaskQueue.status)
        .all()
    )
    by_status = {s: c for s, c in rows}
    return TaskStatsResponse(
        pending=by_status.get("pending", 0),
        running=by_status.get("running", 0),
        retrying=by_status.get("retrying", 0),
        done=by_status.get("done", 0),
        failed=by_status.get("failed", 0),
    )


@router.post("/run", response_model=TaskRunResponse, summary="Procesar tareas pendientes (llamado por cron)")
async def run_tasks(
    max_tasks: int = 20,
    db: Session = Depends(get_db),
    current_user=Depends(_get_user),
):
    """Procesa las tareas pendientes. Pensado para ser llamado por un cron externo
    (Vercel Cron, GitHub Actions, EasyCron, etc.) cada 1-5 minutos.

    Tambien puede ser llamado manualmente por un superadmin para forzar el procesamiento.
    """
    if current_user.rol_global != "superadmin":
        raise HTTPException(status_code=403, detail="Solo superadmin puede ejecutar el worker")

    result = process_pending_tasks(db, max_tasks=max_tasks)
    return TaskRunResponse(ok=True, **result)


@router.post("/enqueue", response_model=TaskEnqueueResponse, summary="Encolar una tarea manualmente")
async def enqueue(
    data: EnqueueRequest,
    db: Session = Depends(get_db),
    current_user=Depends(_get_user),
):
    if current_user.rol_global != "superadmin":
        raise HTTPException(status_code=403, detail="Solo superadmin puede encolar tareas")

    task = enqueue_task(
        db=db,
        task_type=data.task_type,
        payload=data.payload,
        max_attempts=data.max_attempts,
    )
    return TaskEnqueueResponse(id=task.id, task_type=task.task_type, status=task.status)
