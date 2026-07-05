"""Neon storage temizleme scripti (TASK-303).

- 30 günden eski `user_document` embedding'lerini siler.
- Kullanıcı başına maksimum 100 chunk sınırı uygular (en yeni 100 tanesi tutulur).

Kullanım (konteyner içinde, manuel/cron):
    python scripts/cleanup_embeddings.py
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import text  # noqa: E402

from app.db.session import async_session_maker  # noqa: E402

RETENTION_DAYS = 30
MAX_CHUNKS_PER_USER = 100


async def cleanup() -> None:
    async with async_session_maker() as db:
        # 1) 30 günden eski user_document embedding'lerini sil.
        result = await db.execute(
            text(
                """
                DELETE FROM document_embedding
                WHERE metadata->>'source_label' = 'user_document'
                  AND created_at < now() - (:retention_days || ' days')::interval
                """
            ),
            {"retention_days": RETENTION_DAYS},
        )
        print(f"[cleanup] {result.rowcount} adet {RETENTION_DAYS} günden eski chunk silindi.")
        await db.commit()

        # 2) Kullanıcı başına en fazla MAX_CHUNKS_PER_USER chunk kalsın (en yenileri tut).
        result = await db.execute(
            text(
                """
                DELETE FROM document_embedding de
                WHERE de.metadata->>'source_label' = 'user_document'
                  AND de.id IN (
                    SELECT id FROM (
                      SELECT id,
                             row_number() OVER (
                               PARTITION BY metadata->>'user_id'
                               ORDER BY created_at DESC
                             ) AS rn
                      FROM document_embedding
                      WHERE metadata->>'source_label' = 'user_document'
                    ) ranked
                    WHERE ranked.rn > :max_chunks
                  )
                """
            ),
            {"max_chunks": MAX_CHUNKS_PER_USER},
        )
        print(f"[cleanup] {result.rowcount} adet fazla chunk (kullanıcı başına {MAX_CHUNKS_PER_USER} sınırı) silindi.")
        await db.commit()


if __name__ == "__main__":
    asyncio.run(cleanup())
