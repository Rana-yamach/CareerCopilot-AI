"""API_CONTRACT.md §8 GitHub (TASK-212)."""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import MSG_GITHUB_NOT_CONNECTED
from app.core.exceptions import BadRequestError
from app.deps import get_current_user, get_db
from app.models.user import User
from app.repositories.user_repository import get_profile_by_user_id
from app.schemas.github import (
    ConnectGithubRequest,
    ConnectGithubResponse,
    GithubProjectItem,
    GithubProjectsResponse,
    GithubSyncResponse,
)
from app.services import github_service

router = APIRouter()


@router.post("/connect", response_model=ConnectGithubResponse)
async def connect_github(
    payload: ConnectGithubRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ConnectGithubResponse:
    summary = github_service.get_github_user_summary(payload.github_username)

    profile = await get_profile_by_user_id(db, current_user.id)
    if profile is not None:
        profile.github_username = payload.github_username
        await db.commit()

    return ConnectGithubResponse(**summary)


@router.get("/sync", response_model=GithubSyncResponse)
async def sync_github(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> GithubSyncResponse:
    profile = await get_profile_by_user_id(db, current_user.id)
    if profile is None or not profile.github_username:
        raise BadRequestError(MSG_GITHUB_NOT_CONNECTED)

    stats = github_service.get_language_stats(profile.github_username)
    return GithubSyncResponse(
        github_username=stats["github_username"],
        languages=stats["languages"],
        total_public_repos=stats["total_public_repos"],
        synced_at=datetime.now(timezone.utc).isoformat(),
    )


@router.get("/projects", response_model=GithubProjectsResponse)
async def get_github_projects(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> GithubProjectsResponse:
    profile = await get_profile_by_user_id(db, current_user.id)
    if profile is None or not profile.github_username:
        raise BadRequestError(MSG_GITHUB_NOT_CONNECTED)

    projects = github_service.get_projects_for_cv(profile.github_username)
    return GithubProjectsResponse(
        projects=[GithubProjectItem(**p) for p in projects], count=len(projects)
    )
