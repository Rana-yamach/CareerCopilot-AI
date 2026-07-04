"""Async SQLAlchemy engine + sessionmaker (ARCHITECTURE.md §7.3)."""
from collections.abc import AsyncGenerator, Coroutine
from typing import TypeVar

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings

engine = create_async_engine(
    settings.database_url,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    echo=False,
)

async_session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


_T = TypeVar("_T")


async def run_in_fresh_event_loop(coro: Coroutine[None, None, _T]) -> _T:
    """Celery task'ları için: bir coroutine'i çalıştırır ve sonunda `engine`
    connection pool'unu (asyncio.dispose ile) temizler.

    Celery worker her task'ı `asyncio.run(...)` ile ayrı bir event loop'ta
    çalıştırır (bkz. `tasks/*.py`); ancak `engine` modül seviyesinde tek bir
    singleton'dır ve asyncpg bağlantıları oluşturuldukları event loop'a
    bağlıdır. Bir task bitip loop kapandığında pool'daki bağlantılar
    "bayat" kalır; bir sonraki task farklı bir loop'ta bu bağlantıları
    tekrar kullanmaya çalışırsa asyncpg
    `RuntimeError: Future attached to a different loop` hatası fırlatır.
    Bu yüzden her task'ın kendi event loop'u kapanmadan önce (henüz loop
    çalışırken) pool'u dispose ediyoruz; bir sonraki task'ın ilk sorgusu
    yeni loop'ta sıfırdan bir bağlantı açar.
    """
    try:
        return await coro
    finally:
        await engine.dispose()
