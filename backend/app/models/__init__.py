"""SQLAlchemy modelleri.

Alembic autogenerate'in tüm tabloları görebilmesi için modeller burada
içe aktarılır (bkz. alembic/env.py -> target_metadata = Base.metadata).
"""
from app.db.base import Base
from app.models.chat_message import ChatMessage
from app.models.cv_draft import CVDraft
from app.models.document_embedding import DocumentEmbedding
from app.models.interview_session import InterviewSession
from app.models.roadmap import Roadmap
from app.models.skill_gap_report import SkillGapReport
from app.models.uploaded_document import UploadedDocument
from app.models.user import User
from app.models.user_profile import UserProfile

__all__ = [
    "Base",
    "User",
    "UserProfile",
    "UploadedDocument",
    "CVDraft",
    "SkillGapReport",
    "Roadmap",
    "InterviewSession",
    "ChatMessage",
    "DocumentEmbedding",
]
