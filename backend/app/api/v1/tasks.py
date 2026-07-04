"""API_CONTRACT.md §10 Tasks — ortak async iş durum endpointi (TASK-213)."""
from __future__ import annotations

from celery.result import AsyncResult
from fastapi import APIRouter, Depends

from app.core.constants import MSG_FORBIDDEN, MSG_TASK_NOT_FOUND
from app.core.exceptions import ForbiddenError, NotFoundError
from app.deps import get_current_user
from app.models.user import User
from app.schemas.tasks import TaskStatusResponse
from app.tasks.celery_app import celery_app

router = APIRouter()

_CELERY_STATE_MAP = {
    "PENDING": "queued",
    "RECEIVED": "queued",
    "STARTED": "processing",
    "PROCESSING": "processing",
    "RETRY": "processing",
    "SUCCESS": "completed",
    "FAILURE": "failed",
    "REVOKED": "failed",
}


@router.get("/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(
    task_id: str, current_user: User = Depends(get_current_user)
) -> TaskStatusResponse:
    result = AsyncResult(task_id, app=celery_app)

    meta = result.info if isinstance(result.info, dict) else {}
    resource_type = meta.get("resource_type")
    resource_id = meta.get("resource_id")
    owner_id = meta.get("user_id")

    if not resource_type or not resource_id:
        raise NotFoundError(MSG_TASK_NOT_FOUND)
    if owner_id and owner_id != str(current_user.id):
        raise ForbiddenError(MSG_FORBIDDEN)

    status = _CELERY_STATE_MAP.get(result.state, "queued")
    error_code = None
    error_message = None
    progress_percent = 0

    if status == "completed":
        progress_percent = 100
        if meta.get("final_status") == "failed":
            status = "failed"
            error_code = "INTERNAL_ERROR"
            error_message = meta.get("error_message") or "İşlem sırasında bir hata oluştu."
    elif status == "processing":
        progress_percent = 50
    elif status == "failed":
        error_code = "INTERNAL_ERROR"
        error_message = "İşlem başarısız oldu."

    return TaskStatusResponse(
        task_id=task_id,
        status=status,
        resource_type=resource_type,
        resource_id=resource_id,
        progress_percent=progress_percent,
        error_code=error_code,
        error_message=error_message,
    )
