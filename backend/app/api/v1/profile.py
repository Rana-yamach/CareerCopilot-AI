from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_current_user, get_db
from app.models.user import User
from app.repositories.user_repository import get_profile_by_user_id
from app.schemas.profile import ProfileResponse, UpdateProfileRequest

router = APIRouter()


def _to_response(user: User, profile) -> ProfileResponse:  # noqa: ANN001
    return ProfileResponse(
        user_id=str(user.id),
        email=user.email,
        github_username=profile.github_username if profile else None,
        target_position=profile.target_position if profile else None,
        target_company=profile.target_company if profile else None,
        created_at=user.created_at,
        updated_at=profile.updated_at if profile else user.created_at,
    )


@router.get("", response_model=ProfileResponse)
async def get_profile(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> ProfileResponse:
    profile = await get_profile_by_user_id(db, current_user.id)
    return _to_response(current_user, profile)


@router.patch("", response_model=ProfileResponse)
async def update_profile(
    payload: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProfileResponse:
    profile = await get_profile_by_user_id(db, current_user.id)
    if profile is None:
        from app.models.user_profile import UserProfile

        profile = UserProfile(user_id=current_user.id)
        db.add(profile)

    if payload.github_username is not None:
        profile.github_username = payload.github_username
    if payload.target_position is not None:
        profile.target_position = payload.target_position
    if payload.target_company is not None:
        profile.target_company = payload.target_company

    await db.commit()
    await db.refresh(profile)

    return _to_response(current_user, profile)
