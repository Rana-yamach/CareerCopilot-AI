"""API_CONTRACT.md §8 GitHub şemaları."""
import re

from pydantic import BaseModel, field_validator

from app.core.constants import MSG_GITHUB_INVALID_USERNAME

GITHUB_USERNAME_RE = re.compile(r"^[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,37}[a-zA-Z0-9])?$")


class ConnectGithubRequest(BaseModel):
    github_username: str

    @field_validator("github_username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        if not value or not GITHUB_USERNAME_RE.match(value):
            raise ValueError(MSG_GITHUB_INVALID_USERNAME)
        return value


class ConnectGithubResponse(BaseModel):
    github_username: str
    public_repos: int
    avatar_url: str
    verified: bool


class GithubSyncResponse(BaseModel):
    github_username: str
    languages: dict[str, float]
    total_public_repos: int
    synced_at: str


class GithubProjectItem(BaseModel):
    name: str
    description: str
    tech_stack: list[str]
    repo_url: str | None = None
    stars: int = 0


class GithubProjectsResponse(BaseModel):
    projects: list[GithubProjectItem]
    count: int
