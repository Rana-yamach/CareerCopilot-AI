"""Auth domain servisi (TASK-105)."""
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import (
    MSG_EMAIL_ALREADY_REGISTERED,
    MSG_INVALID_CREDENTIALS,
    MSG_REFRESH_TOKEN_INVALID,
)
from app.core.exceptions import ConflictError, UnauthorizedError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    hash_password,
    verify_password,
)
from app.repositories.user_repository import create_user, get_user_by_email, get_user_by_id
from app.schemas.auth import AuthResponse, RefreshResponse


async def register_user(db: AsyncSession, email: str, password: str) -> AuthResponse:
    existing = await get_user_by_email(db, email)
    if existing is not None:
        raise ConflictError(MSG_EMAIL_ALREADY_REGISTERED)

    user = await create_user(db, email=email, password_hash=hash_password(password))

    access_token, expires_in = create_access_token(user.id, user.email)
    refresh_token = create_refresh_token(user.id, user.email)

    return AuthResponse(
        user_id=str(user.id),
        email=user.email,
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=expires_in,
    )


async def login_user(db: AsyncSession, email: str, password: str) -> AuthResponse:
    user = await get_user_by_email(db, email)
    if user is None or not verify_password(password, user.password_hash):
        raise UnauthorizedError(MSG_INVALID_CREDENTIALS)

    access_token, expires_in = create_access_token(user.id, user.email)
    refresh_token = create_refresh_token(user.id, user.email)

    return AuthResponse(
        user_id=str(user.id),
        email=user.email,
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=expires_in,
    )


async def refresh_access_token(db: AsyncSession, refresh_token: str) -> RefreshResponse:
    try:
        payload = decode_refresh_token(refresh_token)
    except ValueError as exc:
        raise UnauthorizedError(MSG_REFRESH_TOKEN_INVALID) from exc

    user_id_raw = payload.get("sub")
    if not user_id_raw:
        raise UnauthorizedError(MSG_REFRESH_TOKEN_INVALID)

    import uuid as _uuid

    user = await get_user_by_id(db, _uuid.UUID(user_id_raw))
    if user is None:
        raise UnauthorizedError(MSG_REFRESH_TOKEN_INVALID)

    access_token, expires_in = create_access_token(user.id, user.email)
    return RefreshResponse(access_token=access_token, expires_in=expires_in)
