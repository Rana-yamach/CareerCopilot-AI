import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.enums import CVDraftStatus, OutputLanguage


class CVDraft(Base):
    __tablename__ = "cv_draft"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("user.id", ondelete="CASCADE"), index=True, nullable=False
    )
    uploaded_document_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("uploaded_document.id", ondelete="SET NULL"), nullable=True
    )
    form_data: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    cv_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    generated_text_tr: Mapped[str | None] = mapped_column(Text, nullable=True)
    generated_text_en: Mapped[str | None] = mapped_column(Text, nullable=True)
    user_edited_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    output_language: Mapped[OutputLanguage] = mapped_column(
        Enum(OutputLanguage, name="output_language_enum", values_callable=lambda e: [i.value for i in e]),
        nullable=False,
        default=OutputLanguage.TR,
    )
    status: Mapped[CVDraftStatus] = mapped_column(
        Enum(CVDraftStatus, name="cv_draft_status_enum", values_callable=lambda e: [i.value for i in e]),
        nullable=False,
        default=CVDraftStatus.DRAFT,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
