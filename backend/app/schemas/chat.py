"""API_CONTRACT.md §9 Agent — Chat / Orchestrator şemaları."""
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, field_validator

AgentIntent = Literal["cv_agent", "skill_gap", "roadmap", "interview", "cv_writer", "general"]


class SendChatMessageRequest(BaseModel):
    message: str
    session_id: str | None = None

    @field_validator("message")
    @classmethod
    def not_empty(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("message alanı boş olamaz.")
        return value


class ChatSessionSummary(BaseModel):
    session_id: str
    last_message_preview: str
    last_agent: str | None
    message_count: int
    started_at: datetime
    last_message_at: datetime


class ChatSessionsResponse(BaseModel):
    sessions: list[ChatSessionSummary]


class ChatMessageItem(BaseModel):
    message_id: str
    role: str
    content: str
    agent_used: str | None = None
    created_at: datetime


class ChatSessionMessagesResponse(BaseModel):
    session_id: str
    messages: list[ChatMessageItem]
