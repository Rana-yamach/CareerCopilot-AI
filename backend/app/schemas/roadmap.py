"""API_CONTRACT.md §6 Analysis — Roadmap şemaları."""
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, field_validator

from app.core.constants import MSG_WEEKLY_HOURS_INVALID

TaskStatus = Literal["queued", "processing", "completed", "failed"]


class GenerateRoadmapRequest(BaseModel):
    skill_gap_report_id: str
    weekly_hours: int

    @field_validator("weekly_hours")
    @classmethod
    def validate_hours(cls, value: int) -> int:
        if value < 1 or value > 40:
            raise ValueError(MSG_WEEKLY_HOURS_INVALID)
        return value


class GenerateRoadmapResponse(BaseModel):
    task_id: str
    roadmap_id: str
    status: str = "queued"


class RoadmapMilestone(BaseModel):
    week: int
    title: str


class RoadmapTaskItem(BaseModel):
    task_id: str
    title: str
    done: bool
    resource: str


class RoadmapWeekPlan(BaseModel):
    week: int
    theme: str
    tasks: list[dict]


class RoadmapResponse(BaseModel):
    roadmap_id: str
    user_id: str
    skill_gap_report_id: str
    weeks_total: int | None
    weekly_hours: int
    milestones: list[dict]
    plan: list[dict]
    progress_percent: int
    status: TaskStatus
    created_at: datetime


class ActiveRoadmapResponse(BaseModel):
    roadmap: RoadmapResponse | None = None


class UpdateRoadmapTaskRequest(BaseModel):
    done: bool


class UpdateRoadmapTaskResponse(BaseModel):
    task_id: str
    done: bool
    progress_percent: int
