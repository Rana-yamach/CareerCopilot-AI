"""API_CONTRACT.md §3 Documents şemaları."""
from datetime import datetime

from pydantic import BaseModel


class ParsedSkills(BaseModel):
    languages: list[str] = []
    frameworks: list[str] = []
    tools: list[str] = []
    experience: list = []
    education: list = []


class UploadDocumentResponse(BaseModel):
    task_id: str
    document_id: str
    document_type: str
    status: str


class DocumentStatusResponse(BaseModel):
    document_id: str
    document_type: str
    status: str
    error_message: str | None = None


class DocumentSummary(BaseModel):
    document_id: str
    document_type: str
    cv_score: int | None
    cv_score_explanation: str | None
    parsed_skills: ParsedSkills
    status: str
    uploaded_at: datetime


class LatestDocumentsResponse(BaseModel):
    documents: list[DocumentSummary]


class DocumentListResponse(BaseModel):
    items: list[DocumentSummary]
    total: int
