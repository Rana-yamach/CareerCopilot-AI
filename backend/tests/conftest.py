"""Pytest fixtures: docker-compose'daki pgvector/redis servislerine karşı çalışır.

Testler `docker compose exec backend pytest` ile veya CI'da aynı ağdaki
servislere karşı çalıştırılmalıdır (DATABASE_URL / REDIS_URL env'den okunur).
"""
from __future__ import annotations

import asyncio

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.db.base import Base
from app.db.session import engine
from app.main import app


@pytest_asyncio.fixture(scope="session", autouse=True)
async def _prepare_database():
    async with engine.begin() as conn:
        await conn.run_sync(lambda sync_conn: sync_conn.execute(__import__("sqlalchemy").text(
            "CREATE EXTENSION IF NOT EXISTS vector"
        )))
        await conn.run_sync(Base.metadata.create_all)
    # `engine` modül seviyesinde bir singleton'dır (asyncpg connection pool
    # içerir). pytest-asyncio (auto mode) her test fonksiyonu için varsayılan
    # olarak yeni bir event loop açar; önceki bir loop'ta oluşturulmuş pool
    # bağlantıları yeni loop'ta kullanılmaya çalışılırsa asyncpg
    # "Future attached to a different loop" hatası fırlatır (bkz. SQLAlchemy
    # async dokümantasyonu: engine loop'lar arasında paylaşılmamalı, loop
    # değiştiğinde dispose() çağrılmalı). Bu yüzden kurulum bağlantısını her
    # test kendi loop'unda taze bir bağlantı açsın diye burada dispose ediyoruz.
    await engine.dispose()
    yield


@pytest_asyncio.fixture(autouse=True)
async def _dispose_engine_pool_after_test():
    """Her testten sonra pool'u temizler ki bir sonraki test (farklı bir
    event loop ile) önceki loop'a bağlı bayat bir bağlantıyı yeniden
    kullanmaya çalışmasın."""
    yield
    await engine.dispose()


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
