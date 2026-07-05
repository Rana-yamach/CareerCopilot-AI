"""API_CONTRACT.md §4 CV Generate / Writer şemaları."""
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, field_validator, model_validator

from app.core.constants import (
    MSG_CV_NAME_EMAIL_REQUIRED,
    MSG_CV_SECTIONS_REQUIRED,
)

SectionType = Literal[
    "education",
    "experience",
    "skills",
    "languages",
    "certificates",
    "interests",
    "projects",
    "courses",
    "awards",
    "organisations",
    "publications",
    "references",
    "declaration",
    "custom",
]

OutputLanguageLiteral = Literal["tr", "en", "both"]


class PersonalInfo(BaseModel):
    name: str = ""
    email: str = ""
    phone: str | None = None
    location: str | None = None
    linkedin_url: str | None = None
    github_url: str | None = None


class CVSection(BaseModel):
    type: SectionType
    order: int
    title: str
    content: dict[str, Any]


class CVFormData(BaseModel):
    personal: PersonalInfo
    selected_sections: list[SectionType]
    sections: list[CVSection] = []
    github_projects_imported: bool = False

    @model_validator(mode="after")
    def validate_required_fields(self) -> "CVFormData":
        if not self.personal.name.strip() or not self.personal.email.strip():
            raise ValueError(MSG_CV_NAME_EMAIL_REQUIRED)
        if not self.selected_sections:
            raise ValueError(MSG_CV_SECTIONS_REQUIRED)
        return self


class GenerateCVRequest(BaseModel):
    form_data: CVFormData
    output_language: OutputLanguageLiteral


class GenerateCVResponse(BaseModel):
    task_id: str
    draft_id: str
    status: str = "queued"


class CVJson(BaseModel):
    personal: dict[str, Any] = {}
    sections: list[dict[str, Any]] = []


class CVDraftResponse(BaseModel):
    draft_id: str
    user_id: str
    form_data: dict[str, Any]
    cv_json: dict[str, Any] | None
    text_tr: str | None
    text_en: str | None
    user_edited_text: str | None
    output_language: str
    status: str
    uploaded_document_id: str | None
    created_at: datetime
    updated_at: datetime


class UpdateCVDraftRequest(BaseModel):
    user_edited_text: str

    @field_validator("user_edited_text")
    @classmethod
    def not_empty(cls, value: str) -> str:
        if value is None:
            raise ValueError("user_edited_text zorunludur.")
        return value


class CVDraftListItem(BaseModel):
    draft_id: str
    status: str
    output_language: str
    created_at: datetime
    updated_at: datetime
    personal_name: str


class CVDraftListResponse(BaseModel):
    items: list[CVDraftListItem]
    total: int


class ExportPdfRequest(BaseModel):
    draft_id: str
    language: Literal["tr", "en"]


class ExportPdfResponse(BaseModel):
    document_id: str
    draft_id: str
    download_url: str
    document_type: str = "generated_cv"
    status: str = "exported"
