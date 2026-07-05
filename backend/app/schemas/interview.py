"""API_CONTRACT.md §7 Interview şemaları."""
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, field_validator

from app.core.constants import MSG_INTERVIEW_ANSWER_REQUIRED, MSG_TARGET_POSITION_REQUIRED

InterviewDifficulty = Literal["junior", "mid"]
InterviewCategory = Literal["algorithmic", "system", "behavioral"]


class StartInterviewRequest(BaseModel):
    target_position: str
    difficulty: InterviewDifficulty
    category: InterviewCategory

    @field_validator("target_position")
    @classmethod
    def not_empty(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError(MSG_TARGET_POSITION_REQUIRED)
        return value


class StartInterviewResponse(BaseModel):
    session_id: str
    question_index: int
    question: str
    target_position: str
    difficulty: str
    category: str
    started_at: datetime


class AnswerInterviewRequest(BaseModel):
    question_index: int
    user_answer: str

    @field_validator("user_answer")
    @classmethod
    def not_empty(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError(MSG_INTERVIEW_ANSWER_REQUIRED)
        return value


class AnsweredQuestion(BaseModel):
    question_index: int
    question: str
    user_answer: str
    feedback: str
    score: int
    correct_answer_hint: str


class NextQuestion(BaseModel):
    question_index: int
    question: str


class AnswerInterviewResponse(BaseModel):
    session_id: str
    answered: AnsweredQuestion
    next_question: NextQuestion | None
    is_session_complete: bool


class InterviewSummaryResponse(BaseModel):
    session_id: str
    target_position: str
    difficulty: str
    category: str
    overall_score: int | None
    questions: list[dict]
    strengths: list[str]
    improvements: list[str]
    started_at: datetime
    ended_at: datetime | None


class InterviewSessionListItem(BaseModel):
    session_id: str
    target_position: str
    category: str
    overall_score: int | None
    started_at: datetime
    ended_at: datetime | None


class InterviewSessionsResponse(BaseModel):
    items: list[InterviewSessionListItem]
    total: int
