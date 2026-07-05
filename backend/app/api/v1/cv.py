"""API_CONTRACT.md §4 CV Generate / Writer (TASK-108, TASK-204, TASK-209)."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.constants import MSG_CV_DRAFT_NOT_FOUND, MSG_DOCUMENT_NOT_FOUND, MSG_FORBIDDEN
from app.core.exceptions import ForbiddenError, NotFoundError
from app.deps import get_current_user, get_db
from app.models.cv_draft import CVDraft
from app.models.uploaded_document import UploadedDocument
from app.models.user import User
from app.schemas.cv import (
    CVDraftListItem,
    CVDraftListResponse,
    CVDraftResponse,
    ExportPdfRequest,
    ExportPdfResponse,
    GenerateCVRequest,
    GenerateCVResponse,
    UpdateCVDraftRequest,
)
from app.services import cv_service

router = APIRouter()


def _to_draft_response(draft: CVDraft) -> CVDraftResponse:
    return CVDraftResponse(
        draft_id=str(draft.id),
        user_id=str(draft.user_id),
        form_data=draft.form_data,
        cv_json=draft.cv_json,
        text_tr=draft.generated_text_tr,
        text_en=draft.generated_text_en,
        user_edited_text=draft.user_edited_text,
        output_language=draft.output_language.value,
        status=draft.status.value,
        uploaded_document_id=str(draft.uploaded_document_id) if draft.uploaded_document_id else None,
        created_at=draft.created_at,
        updated_at=draft.updated_at,
    )


@router.post("/generate", response_model=GenerateCVResponse, status_code=202)
async def generate_cv(
    payload: GenerateCVRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> GenerateCVResponse:
    draft = await cv_service.create_draft(
        db,
        user_id=current_user.id,
        form_data=payload.form_data.model_dump(),
        output_language=payload.output_language,
    )

    from app.tasks.analysis_tasks import generate_cv_task

    task = generate_cv_task.delay(str(draft.id), str(current_user.id))

    return GenerateCVResponse(task_id=task.id, draft_id=str(draft.id), status="queued")


@router.get("/drafts", response_model=CVDraftListResponse)
async def list_drafts(
    limit: int = 20,
    offset: int = 0,
    status: str | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CVDraftListResponse:
    limit = min(limit, 100)
    query = select(CVDraft).where(CVDraft.user_id == current_user.id)
    count_query = select(func.count()).select_from(CVDraft).where(CVDraft.user_id == current_user.id)
    if status:
        query = query.where(CVDraft.status == status)
        count_query = count_query.where(CVDraft.status == status)

    query = query.order_by(CVDraft.created_at.desc()).limit(limit).offset(offset)

    result = await db.execute(query)
    drafts = result.scalars().all()
    total = (await db.execute(count_query)).scalar_one()

    items = [
        CVDraftListItem(
            draft_id=str(d.id),
            status=d.status.value,
            output_language=d.output_language.value,
            created_at=d.created_at,
            updated_at=d.updated_at,
            personal_name=(d.form_data or {}).get("personal", {}).get("name", ""),
        )
        for d in drafts
    ]
    return CVDraftListResponse(items=items, total=total)


@router.get("/draft/{draft_id}", response_model=CVDraftResponse)
async def get_draft(
    draft_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CVDraftResponse:
    draft = await db.get(CVDraft, draft_id)
    if draft is None:
        raise NotFoundError(MSG_CV_DRAFT_NOT_FOUND)
    if draft.user_id != current_user.id:
        raise ForbiddenError(MSG_FORBIDDEN)
    return _to_draft_response(draft)


@router.patch("/draft/{draft_id}", response_model=CVDraftResponse)
async def update_draft(
    draft_id: uuid.UUID,
    payload: UpdateCVDraftRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CVDraftResponse:
    draft = await db.get(CVDraft, draft_id)
    if draft is None:
        raise NotFoundError(MSG_CV_DRAFT_NOT_FOUND)
    if draft.user_id != current_user.id:
        raise ForbiddenError(MSG_FORBIDDEN)

    draft.user_edited_text = payload.user_edited_text
    await db.commit()
    await db.refresh(draft)
    return _to_draft_response(draft)


@router.post("/export-pdf", response_model=ExportPdfResponse)
async def export_pdf(
    payload: ExportPdfRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ExportPdfResponse:
    draft = await db.get(CVDraft, uuid.UUID(payload.draft_id))
    if draft is None:
        raise NotFoundError(MSG_CV_DRAFT_NOT_FOUND)
    if draft.user_id != current_user.id:
        raise ForbiddenError(MSG_FORBIDDEN)

    document, _ = await cv_service.export_draft_to_pdf(
        db, draft, language=payload.language, upload_dir=settings.upload_dir
    )

    return ExportPdfResponse(
        document_id=str(document.id),
        draft_id=str(draft.id),
        download_url=f"/api/v1/cv/download/{document.id}",
    )


@router.get("/download/{document_id}")
async def download_pdf(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Response:
    document = await db.get(UploadedDocument, document_id)
    if document is None:
        raise NotFoundError(MSG_DOCUMENT_NOT_FOUND)
    if document.user_id != current_user.id:
        raise ForbiddenError(MSG_FORBIDDEN)

    with open(document.file_path, "rb") as f:
        pdf_bytes = f.read()

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="cv_{document_id}.pdf"'},
    )
