"""
Schemas para el módulo Admin Tasks.
"""
from pydantic import BaseModel
from typing import Optional


class TaskItem(BaseModel):
    id: int
    task_type: str
    status: str
    attempts: int
    max_attempts: int
    last_error: Optional[str] = None
    scheduled_for: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


class TaskListResponse(BaseModel):
    tasks: list[TaskItem]
    total: int
    skip: int
    limit: int


class TaskStatsResponse(BaseModel):
    pending: int
    running: int
    retrying: int
    done: int
    failed: int


class TaskRunResponse(BaseModel):
    ok: bool
    processed: int
    failed: int


class TaskEnqueueResponse(BaseModel):
    id: int
    task_type: str
    status: str