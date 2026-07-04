"""pgvector extension kontrolü.

Uygulama başlangıcında (`main.py` lifespan) çağrılır; Neon/pgvector
üzerinde `vector` extension'ının aktif olduğundan emin olur.
Şema değişiklikleri buradan YAPILMAZ — yalnızca Alembic migration ile yapılır.
"""
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from app.core.logging import get_logger

logger = get_logger(__name__)


async def ensure_pgvector_extension(engine: AsyncEngine) -> None:
    try:
        async with engine.begin() as conn:
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        logger.info("pgvector extension hazır.")
    except Exception:  # noqa: BLE001
        logger.exception("pgvector extension kontrolü başarısız oldu.")
