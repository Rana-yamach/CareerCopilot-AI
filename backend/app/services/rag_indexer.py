"""Belge metnini chunk'layıp embed edip DocumentEmbedding tablosuna yazar
(TASK-203 yan etkisi). `metadata.source_label = "user_document"`.
"""
from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.document_embedding import DocumentEmbedding
from app.models.uploaded_document import UploadedDocument
from app.services.embedding_service import encode
from app.utils.text_chunker import chunk_text

logger = get_logger(__name__)


async def index_document_text(db: AsyncSession, document: UploadedDocument) -> int:
    """Belgenin raw_text alanını chunk'layıp embedding olarak kaydeder.
    Dönüş: kaç chunk indexlendiği.
    """
    if not document.raw_text:
        return 0

    chunks = chunk_text(document.raw_text)
    if not chunks:
        return 0

    vectors = encode([c["content"] for c in chunks])

    for chunk, vector in zip(chunks, vectors, strict=False):
        embedding_row = DocumentEmbedding(
            document_id=document.id,
            content=chunk["content"],
            embedding=vector,
            doc_metadata={
                "chunk_index": chunk["chunk_index"],
                "document_type": document.document_type.value
                if hasattr(document.document_type, "value")
                else document.document_type,
                "source_label": "user_document",
                "user_id": str(document.user_id),
            },
        )
        db.add(embedding_row)

    await db.commit()
    logger.info("Belge %s için %d chunk indexlendi.", document.id, len(chunks))
    return len(chunks)
