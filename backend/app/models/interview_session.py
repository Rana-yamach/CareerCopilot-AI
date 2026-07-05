import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.enums import InterviewCategory, InterviewDifficulty


class InterviewSession(Base):
    __tablename__ = "interview_session"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("user.id", ondelete="CASCADE"), index=True, nullable=False
    )
    target_position: Mapped[str] = mapped_column(String(255), nullable=False)
    difficulty: Mapped[InterviewDifficulty] = mapped_column(
        Enum(InterviewDifficulty, name="interview_difficulty_enum", values_callable=lambda e: [i.value for i in e]),
        nullable=False,
    )
    category: Mapped[InterviewCategory] = mapped_column(
        Enum(InterviewCategory, name="interview_category_enum", values_callable=lambda e: [i.value for i in e]),
        nullable=False,
    )
    # `MutableList.as_mutable` bu kolonda append/insert/pop gibi liste seviyeli
    # in-place mutasyonları SQLAlchemy'nin change tracking mekanizmasına bildirir
    # (bkz. answer_interview: questions.append(...) sonrası flag_modified ile
    # birlikte, iç içe geçmiş dict mutasyonları da garanti altına alınır).
    questions: Mapped[list] = mapped_column(MutableList.as_mutable(JSONB), nullable=False, default=list)
    overall_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
