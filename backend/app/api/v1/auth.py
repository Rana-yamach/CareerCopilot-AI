from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rate_limit import limiter
from app.deps import get_db
from app.schemas.auth import (
    AuthResponse,
    LoginRequest,
    RefreshRequest,
    RefreshResponse,
    RegisterRequest,
)
from app.services import auth_service

router = APIRouter()


@router.post("/register", response_model=AuthResponse, status_code=201)
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)) -> AuthResponse:
    return await auth_service.register_user(db, email=payload.email, password=payload.password)


@router.post("/login", response_model=AuthResponse, status_code=200)
@limiter.limit("10/minute")
async def login(
    request: Request, payload: LoginRequest, db: AsyncSession = Depends(get_db)
) -> AuthResponse:
    return await auth_service.login_user(db, email=payload.email, password=payload.password)


@router.post("/refresh", response_model=RefreshResponse, status_code=200)
async def refresh(payload: RefreshRequest, db: AsyncSession = Depends(get_db)) -> RefreshResponse:
    return await auth_service.refresh_access_token(db, refresh_token=payload.refresh_token)
