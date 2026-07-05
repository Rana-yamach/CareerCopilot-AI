"""API_CONTRACT.md §10 Tasks şemaları."""
from typing import Literal

from pydantic import BaseModel

ResourceType = Literal["document", "cv_draft", "skill_gap_report", "roadmap"]
TaskStatus = Literal["queued", "processing", "completed", "failed"]


class TaskStatusResponse(BaseModel):
    task_id: str
    status: TaskStatus
    resource_type: ResourceType
    resource_id: str
    progress_percent: int
    error_code: str | None = None
    error_message: str | None = None
