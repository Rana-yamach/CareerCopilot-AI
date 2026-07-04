"""Ortak FastAPI dependency'leri: get_db, get_current_user."""
import uuid
from collections.abc import AsyncGenerator

from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import MSG_INVALID_TOKEN, MSG_TOKEN_MISSING, MSG_USER_NOT_FOUND
from app.core.exceptions import UnauthorizedError
from app.core.security import decode_access_token
from app.db.session import async_session_maker
from app.models.user import User


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def get_current_user(
    authorization: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
) -> User:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise UnauthorizedError(MSG_TOKEN_MISSING)

    token = authorization.split(" ", 1)[1].strip()
    try:
        payload = decode_access_token(token)
    except ValueError as exc:
        raise UnauthorizedError(MSG_INVALID_TOKEN) from exc

    user_id_raw = payload.get("sub")
    if not user_id_raw:
        raise UnauthorizedError(MSG_INVALID_TOKEN)

    try:
        user_id = uuid.UUID(user_id_raw)
    except ValueError as exc:
        raise UnauthorizedError(MSG_INVALID_TOKEN) from exc

    user = await db.get(User, user_id)
    if user is None:
        raise UnauthorizedError(MSG_USER_NOT_FOUND)

    return user
