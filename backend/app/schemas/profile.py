"""API_CONTRACT.md §2 Profil şemaları."""
from datetime import datetime

from pydantic import BaseModel


class ProfileResponse(BaseModel):
    user_id: str
    email: str
    github_username: str | None
    target_position: str | None
    target_company: str | None
    created_at: datetime
    updated_at: datetime


class UpdateProfileRequest(BaseModel):
    github_username: str | None = None
    target_position: str | None = None
    target_company: str | None = None
