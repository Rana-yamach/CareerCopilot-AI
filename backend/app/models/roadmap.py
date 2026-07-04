import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.enums import ProcessingStatus


class Roadmap(Base):
    __tablename__ = "roadmap"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("user.id", ondelete="CASCADE"), index=True, nullable=False
    )
    skill_gap_report_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("skill_gap_report.id", ondelete="CASCADE"), nullable=False
    )
    weeks_total: Mapped[int | None] = mapped_column(Integer, nullable=True)
    weekly_hours: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    milestones: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    # `MutableList.as_mutable`: update_roadmap_task, task done durumunu haftalık
    # plan içindeki iç içe task dict'lerinde in-place günceller; liste seviyeli
    # değişim izlemeyi (flag_modified ile birlikte) garanti eder.
    plan: Mapped[list] = mapped_column(MutableList.as_mutable(JSONB), nullable=False, default=list)
    progress_percent: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[ProcessingStatus] = mapped_column(
        Enum(ProcessingStatus, name="processing_status_enum", values_callable=lambda e: [i.value for i in e]),
        nullable=False,
        default=ProcessingStatus.QUEUED,
    )
    error_message: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
