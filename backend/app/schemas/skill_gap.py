"""API_CONTRACT.md §5 Analysis — Skill Gap şemaları."""
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, field_validator

from app.core.constants import MSG_TARGET_POSITION_REQUIRED

TaskStatus = Literal["queued", "processing", "completed", "failed"]


class AnalyzeSkillGapRequest(BaseModel):
    target_position: str

    @field_validator("target_position")
    @classmethod
    def not_empty(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError(MSG_TARGET_POSITION_REQUIRED)
        return value


class AnalyzeSkillGapResponse(BaseModel):
    task_id: str
    report_id: str
    status: str = "queued"


class SkillResource(BaseModel):
    title: str
    type: str
    url: str


class MissingSkill(BaseModel):
    name: str
    priority: int
    estimated_weeks: int
    resources: list[SkillResource]


class SkillGapReportResponse(BaseModel):
    report_id: str
    user_id: str
    target_position: str
    match_score: int | None
    source_document_ids: list[str]
    missing_skills: list[dict]
    status: TaskStatus
    generated_at: datetime


class LatestSkillGapResponse(BaseModel):
    report: SkillGapReportResponse | None = None
