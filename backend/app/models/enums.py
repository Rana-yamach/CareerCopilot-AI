"""ARCHITECTURE.md §7.1 Enum tipleri."""
from enum import Enum


class DocumentType(str, Enum):
    CV = "cv"
    LINKEDIN_PDF = "linkedin_pdf"
    GENERATED_CV = "generated_cv"


class DocumentSource(str, Enum):
    UPLOAD = "upload"
    GENERATED = "generated"


class ProcessingStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class CVDraftStatus(str, Enum):
    DRAFT = "draft"
    GENERATED = "generated"
    EXPORTED = "exported"


class OutputLanguage(str, Enum):
    TR = "tr"
    EN = "en"
    BOTH = "both"


class ChatRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"


class InterviewDifficulty(str, Enum):
    JUNIOR = "junior"
    MID = "mid"


class InterviewCategory(str, Enum):
    ALGORITHMIC = "algorithmic"
    SYSTEM = "system"
    BEHAVIORAL = "behavioral"
