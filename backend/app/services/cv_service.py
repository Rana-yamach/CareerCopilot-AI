"""CV Draft domain servisi (TASK-108, TASK-204, TASK-209)."""
from __future__ import annotations

import os
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import MSG_CV_NOT_GENERATED_YET
from app.core.exceptions import ConflictError
from app.models.cv_draft import CVDraft
from app.models.enums import CVDraftStatus, DocumentSource, DocumentType, ProcessingStatus
from app.models.uploaded_document import UploadedDocument
from app.services.pdf_render_service import render_cv_pdf


async def create_draft(db: AsyncSession, user_id: uuid.UUID, form_data: dict, output_language: str) -> CVDraft:
    draft = CVDraft(
        user_id=user_id,
        form_data=form_data,
        output_language=output_language,
        status=CVDraftStatus.DRAFT,
    )
    db.add(draft)
    await db.commit()
    await db.refresh(draft)
    return draft


def _render_draft_pdf_bytes(draft: CVDraft, language: str) -> bytes:
    text = draft.user_edited_text or (
        draft.generated_text_tr if language == "tr" else draft.generated_text_en
    )
    text = text or ""

    form_data = draft.form_data or {}
    personal = form_data.get("personal", {})
    sections = sorted(form_data.get("sections", []), key=lambda s: s.get("order", 0))

    headline = ""
    for section in sections:
        if section.get("type") == "experience":
            items = section.get("content", {}).get("items") or []
            if items:
                headline = items[0].get("title", "")
            break

    return render_cv_pdf(personal=personal, sections=sections, body_text=text, headline=headline)


def preview_draft_pdf(draft: CVDraft, language: str) -> bytes:
    """CVBuilderEditorPage'in canlı PDF önizlemesi için: kalıcı belge/durum
    değişikliği yapmadan (export'un aksine) anlık PDF byte'ları üretir.
    `form_data.sections` taslak oluşturulduğu andan itibaren mevcut olduğu
    için `status="draft"` iken de çalışır.
    """
    return _render_draft_pdf_bytes(draft, language)


async def export_draft_to_pdf(
    db: AsyncSession, draft: CVDraft, language: str, upload_dir: str
) -> tuple[UploadedDocument, bytes]:
    if draft.status == CVDraftStatus.DRAFT:
        raise ConflictError(MSG_CV_NOT_GENERATED_YET)

    text = draft.user_edited_text or (
        draft.generated_text_tr if language == "tr" else draft.generated_text_en
    )
    pdf_bytes = _render_draft_pdf_bytes(draft, language)

    user_dir = os.path.join(upload_dir, str(draft.user_id))
    os.makedirs(user_dir, exist_ok=True)
    file_path = os.path.join(user_dir, f"cv_{draft.id}.pdf")
    with open(file_path, "wb") as f:
        f.write(pdf_bytes)

    document = UploadedDocument(
        user_id=draft.user_id,
        document_type=DocumentType.GENERATED_CV,
        file_path=file_path,
        raw_text=text,
        parsed_skills={},
        source=DocumentSource.GENERATED,
        status=ProcessingStatus.COMPLETED,
    )
    db.add(document)
    await db.flush()

    draft.uploaded_document_id = document.id
    draft.status = CVDraftStatus.EXPORTED

    await db.commit()
    await db.refresh(document)

    return document, pdf_bytes
