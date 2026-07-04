"""FastAPI uygulama giriş noktası (TASK-109, TASK-110)."""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from app.api.v1 import api_router
from app.config import settings
from app.core.constants import MSG_RATE_LIMITED_LOGIN, MSG_VALIDATION_ERROR
from app.core.exceptions import AppException
from app.core.logging import configure_logging, get_logger
from app.core.rate_limit import limiter
from app.db.init_db import ensure_pgvector_extension
from app.db.session import engine

configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await ensure_pgvector_extension(engine)
    logger.info("CareerCopilot AI backend başlatıldı (ortam: %s).", settings.environment)
    yield
    logger.info("CareerCopilot AI backend kapatılıyor.")


app = FastAPI(
    title="CareerCopilot AI API",
    version="1.0.0",
    docs_url="/api/v1/docs",
    openapi_url="/api/v1/openapi.json",
    lifespan=lifespan,
)

app.state.limiter = limiter

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": exc.code, "message": exc.message_tr}},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    # Pydantic v2 validasyon hatalarını Türkçeleştir: field_validator'lardan gelen
    # ValueError mesajları zaten Türkçedir; diğerleri için genel mesaj kullanılır.
    first_error = exc.errors()[0] if exc.errors() else {}
    message = first_error.get("msg", MSG_VALIDATION_ERROR)
    # Pydantic v2 "Value error, <mesaj>" öneki ekler; temizle.
    if message.startswith("Value error, "):
        message = message[len("Value error, ") :]
    else:
        message = MSG_VALIDATION_ERROR

    return JSONResponse(
        status_code=422,
        content={"error": {"code": "VALIDATION_ERROR", "message": message}},
    )


@app.exception_handler(RateLimitExceeded)
async def rate_limit_exception_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    return JSONResponse(
        status_code=429,
        content={"error": {"code": "RATE_LIMITED", "message": MSG_RATE_LIMITED_LOGIN}},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Beklenmeyen hata: %s", request.url)
    return JSONResponse(
        status_code=500,
        content={"error": {"code": "INTERNAL_ERROR", "message": "Beklenmeyen bir sunucu hatası oluştu."}},
    )


@app.get("/health", tags=["health"])
async def root_health() -> dict:
    """Kök seviye health check (TASK-101 kabul kriteri, Railway keep-alive)."""
    return {"status": "ok"}


app.include_router(api_router)
