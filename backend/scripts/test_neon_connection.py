"""Neon (veya local pgvector) bağlantı test scripti (TASK-102).

`DATABASE_URL` üzerinden basit bir SELECT çalıştırır ve pgvector extension'ının
aktif olup olmadığını kontrol eder. Gerçek kimlik bilgilerini asla loglamaz.

Kullanım:
    python scripts/test_neon_connection.py
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import text  # noqa: E402

from app.db.session import engine  # noqa: E402


async def main() -> None:
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT 1"))
        assert result.scalar_one() == 1
        print("[test_neon_connection] SELECT 1 başarılı.")

        ext_result = await conn.execute(
            text("SELECT extname FROM pg_extension WHERE extname = 'vector'")
        )
        if ext_result.first():
            print("[test_neon_connection] pgvector extension AKTİF.")
        else:
            print("[test_neon_connection] UYARI: pgvector extension bulunamadı.")


if __name__ == "__main__":
    asyncio.run(main())
