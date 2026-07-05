"""API_CONTRACT.md §3 Documents (TASK-106, TASK-107)."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, File, Form, Response, UploadFile
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import MSG_DOCUMENT_NOT_FOUND, MSG_FORBIDDEN
from app.core.exceptions import ForbiddenError, NotFoundError
from app.deps import get_current_user, get_db
from app.models.enums import DocumentSource, ProcessingStatus
from app.models.uploaded_document import UploadedDocument
from app.models.user import User
from app.schemas.document import (
    DocumentListResponse,
    DocumentStatusResponse,
    DocumentSummary,
    LatestDocumentsResponse,
    ParsedSkills,
    UploadDocumentResponse,
)
from app.services.document_service import (
    build_upload_path,
    delete_upload_file,
    mock_parsed_skills,
    save_upload_bytes,
)
from app.utils.file_validators import (
    validate_document_type,
    validate_file_content_type,
    validate_file_extension,
    validate_file_size,
)

router = APIRouter()


def _to_summary(document: UploadedDocument) -> DocumentSummary:
    parsed_skills = document.parsed_skills or {}
    return DocumentSummary(
        document_id=str(document.id),
        document_type=document.document_type.value,
        cv_score=document.cv_score,
        cv_score_explanation=document.cv_score_explanation,
        parsed_skills=ParsedSkills(**{**mock_parsed_skills(), **parsed_skills}),
        status=document.status.value,
        uploaded_at=document.uploaded_at,
    )


@router.post("/upload", response_model=UploadDocumentResponse, status_code=202)
async def upload_document(
    file: UploadFile = File(...),
    document_type: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UploadDocumentResponse:
    validate_document_type(document_type)
    ext = validate_file_extension(file.filename or "")

    content = await file.read()
    validate_file_size(len(content))
    validate_file_content_type(content, ext)

    file_path = build_upload_path(current_user.id, file.filename or "document")
    save_upload_bytes(file_path, content)

    document = UploadedDocument(
        user_id=current_user.id,
        document_type=document_type,
        file_path=file_path,
        parsed_skills=mock_parsed_skills(),
        source=DocumentSource.UPLOAD,
        status=ProcessingStatus.QUEUED,
    )
    db.add(document)
    await db.commit()
    await db.refresh(document)

    from app.tasks.document_tasks import process_document_task

    task = process_document_task.delay(str(document.id), str(current_user.id))

    return UploadDocumentResponse(
        task_id=task.id,
        document_id=str(document.id),
        document_type=document.document_type.value,
        status=document.status.value,
    )


@router.get("/latest", response_model=LatestDocumentsResponse)
async def get_latest_documents(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> LatestDocumentsResponse:
    result = await db.execute(
        select(UploadedDocument)
        .where(UploadedDocument.user_id == current_user.id)
        .order_by(UploadedDocument.uploaded_at.desc())
        .limit(10)
    )
    documents = result.scalars().all()
    return LatestDocumentsResponse(documents=[_to_summary(d) for d in documents])


@router.get("", response_model=DocumentListResponse)
async def list_documents(
    document_type: str | None = None,
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DocumentListResponse:
    limit = min(limit, 100)
    query = select(UploadedDocument).where(UploadedDocument.user_id == current_user.id)
    count_query = select(func.count()).select_from(UploadedDocument).where(
        UploadedDocument.user_id == current_user.id
    )
    if document_type:
        query = query.where(UploadedDocument.document_type == document_type)
        count_query = count_query.where(UploadedDocument.document_type == document_type)

    query = query.order_by(UploadedDocument.uploaded_at.desc()).limit(limit).offset(offset)

    result = await db.execute(query)
    documents = result.scalars().all()
    total = (await db.execute(count_query)).scalar_one()

    return DocumentListResponse(items=[_to_summary(d) for d in documents], total=total)


@router.get("/{doc_id}/status", response_model=DocumentStatusResponse)
async def get_document_status(
    doc_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DocumentStatusResponse:
    document = await db.get(UploadedDocument, doc_id)
    if document is None:
        raise NotFoundError(MSG_DOCUMENT_NOT_FOUND)
    if document.user_id != current_user.id:
        raise ForbiddenError(MSG_FORBIDDEN)

    return DocumentStatusResponse(
        document_id=str(document.id),
        document_type=document.document_type.value,
        status=document.status.value,
        error_message=document.error_message,
    )


@router.delete("/{doc_id}", status_code=204)
async def delete_document(
    doc_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Response:
    document = await db.get(UploadedDocument, doc_id)
    if document is None:
        raise NotFoundError(MSG_DOCUMENT_NOT_FOUND, code="DOCUMENT_NOT_FOUND")
    if document.user_id != current_user.id:
        raise ForbiddenError(MSG_FORBIDDEN)

    delete_upload_file(document.file_path)

    await db.delete(document)
    await db.commit()

    return Response(status_code=204)
