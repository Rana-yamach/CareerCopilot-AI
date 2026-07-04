import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.enums import DocumentSource, DocumentType, ProcessingStatus


class UploadedDocument(Base):
    __tablename__ = "uploaded_document"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("user.id", ondelete="CASCADE"), index=True, nullable=False
    )
    document_type: Mapped[DocumentType] = mapped_column(
        Enum(DocumentType, name="document_type_enum", values_callable=lambda e: [i.value for i in e]),
        index=True,
        nullable=False,
    )
    file_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    parsed_skills: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    cv_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cv_score_explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    source: Mapped[DocumentSource] = mapped_column(
        Enum(DocumentSource, name="document_source_enum", values_callable=lambda e: [i.value for i in e]),
        nullable=False,
        default=DocumentSource.UPLOAD,
    )
    status: Mapped[ProcessingStatus] = mapped_column(
        Enum(ProcessingStatus, name="processing_status_enum", values_callable=lambda e: [i.value for i in e]),
        nullable=False,
        default=ProcessingStatus.QUEUED,
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
