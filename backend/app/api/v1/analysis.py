"""API_CONTRACT.md §5/§6 Skill Gap + Roadmap (TASK-205, TASK-207)."""
from __future__ import annotations

import math
import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified

from app.core.constants import (
    MSG_FORBIDDEN,
    MSG_NO_DOCUMENTS_FOR_ANALYSIS,
    MSG_ROADMAP_NOT_FOUND,
    MSG_SKILL_GAP_NOT_FOUND,
    MSG_TASK_NOT_FOUND_IN_ROADMAP,
)
from app.core.exceptions import BadRequestError, ForbiddenError, NotFoundError
from app.deps import get_current_user, get_db
from app.models.enums import ProcessingStatus
from app.models.roadmap import Roadmap
from app.models.skill_gap_report import SkillGapReport
from app.models.uploaded_document import UploadedDocument
from app.models.user import User
from app.schemas.roadmap import (
    ActiveRoadmapResponse,
    GenerateRoadmapRequest,
    GenerateRoadmapResponse,
    RoadmapResponse,
    UpdateRoadmapTaskRequest,
    UpdateRoadmapTaskResponse,
)
from app.schemas.skill_gap import (
    AnalyzeSkillGapRequest,
    AnalyzeSkillGapResponse,
    LatestSkillGapResponse,
    SkillGapReportResponse,
)

skill_gap_router = APIRouter()
roadmap_router = APIRouter()


def _to_skill_gap_response(report: SkillGapReport) -> SkillGapReportResponse:
    return SkillGapReportResponse(
        report_id=str(report.id),
        user_id=str(report.user_id),
        target_position=report.target_position,
        match_score=report.match_score,
        source_document_ids=report.source_document_ids or [],
        missing_skills=report.missing_skills or [],
        status=report.status.value,
        generated_at=report.generated_at,
    )


def _to_roadmap_response(roadmap: Roadmap) -> RoadmapResponse:
    return RoadmapResponse(
        roadmap_id=str(roadmap.id),
        user_id=str(roadmap.user_id),
        skill_gap_report_id=str(roadmap.skill_gap_report_id),
        weeks_total=roadmap.weeks_total,
        weekly_hours=roadmap.weekly_hours,
        milestones=roadmap.milestones or [],
        plan=roadmap.plan or [],
        progress_percent=roadmap.progress_percent,
        status=roadmap.status.value,
        created_at=roadmap.created_at,
    )


@skill_gap_router.post("/analyze", response_model=AnalyzeSkillGapResponse, status_code=202)
async def analyze_skill_gap(
    payload: AnalyzeSkillGapRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AnalyzeSkillGapResponse:
    doc_count = (
        await db.execute(
            select(UploadedDocument.id).where(UploadedDocument.user_id == current_user.id).limit(1)
        )
    ).first()
    if doc_count is None:
        raise BadRequestError(MSG_NO_DOCUMENTS_FOR_ANALYSIS)

    report = SkillGapReport(
        user_id=current_user.id,
        target_position=payload.target_position,
        status=ProcessingStatus.QUEUED,
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)

    from app.tasks.analysis_tasks import analyze_skill_gap_task

    task = analyze_skill_gap_task.delay(str(report.id), str(current_user.id), payload.target_position)

    return AnalyzeSkillGapResponse(task_id=task.id, report_id=str(report.id), status="queued")


@skill_gap_router.get("/latest", response_model=LatestSkillGapResponse)
async def get_latest_skill_gap(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> LatestSkillGapResponse:
    result = await db.execute(
        select(SkillGapReport)
        .where(SkillGapReport.user_id == current_user.id)
        .order_by(SkillGapReport.generated_at.desc())
        .limit(1)
    )
    report = result.scalar_one_or_none()
    if report is None:
        return LatestSkillGapResponse(report=None)
    return LatestSkillGapResponse(report=_to_skill_gap_response(report))


@skill_gap_router.get("/{report_id}", response_model=SkillGapReportResponse)
async def get_skill_gap_report(
    report_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SkillGapReportResponse:
    report = await db.get(SkillGapReport, report_id)
    if report is None:
        raise NotFoundError(MSG_SKILL_GAP_NOT_FOUND)
    if report.user_id != current_user.id:
        raise ForbiddenError(MSG_FORBIDDEN)
    return _to_skill_gap_response(report)


@roadmap_router.post("/generate", response_model=GenerateRoadmapResponse, status_code=202)
async def generate_roadmap(
    payload: GenerateRoadmapRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> GenerateRoadmapResponse:
    report = await db.get(SkillGapReport, uuid.UUID(payload.skill_gap_report_id))
    if report is None or report.user_id != current_user.id:
        raise NotFoundError(MSG_SKILL_GAP_NOT_FOUND)

    roadmap = Roadmap(
        user_id=current_user.id,
        skill_gap_report_id=report.id,
        weekly_hours=payload.weekly_hours,
        status=ProcessingStatus.QUEUED,
    )
    db.add(roadmap)
    await db.commit()
    await db.refresh(roadmap)

    from app.tasks.analysis_tasks import generate_roadmap_task

    task = generate_roadmap_task.delay(
        str(roadmap.id), str(report.id), payload.weekly_hours, str(current_user.id)
    )

    return GenerateRoadmapResponse(task_id=task.id, roadmap_id=str(roadmap.id), status="queued")


@roadmap_router.get("/active", response_model=ActiveRoadmapResponse)
async def get_active_roadmap(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> ActiveRoadmapResponse:
    result = await db.execute(
        select(Roadmap)
        .where(Roadmap.user_id == current_user.id)
        .order_by(Roadmap.created_at.desc())
        .limit(1)
    )
    roadmap = result.scalar_one_or_none()
    if roadmap is None:
        return ActiveRoadmapResponse(roadmap=None)
    return ActiveRoadmapResponse(roadmap=_to_roadmap_response(roadmap))


@roadmap_router.get("/{roadmap_id}", response_model=RoadmapResponse)
async def get_roadmap(
    roadmap_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> RoadmapResponse:
    roadmap = await db.get(Roadmap, roadmap_id)
    if roadmap is None:
        raise NotFoundError(MSG_ROADMAP_NOT_FOUND)
    if roadmap.user_id != current_user.id:
        raise ForbiddenError(MSG_FORBIDDEN)
    return _to_roadmap_response(roadmap)


@roadmap_router.patch("/{roadmap_id}/task/{task_id}", response_model=UpdateRoadmapTaskResponse)
async def update_roadmap_task(
    roadmap_id: uuid.UUID,
    task_id: str,
    payload: UpdateRoadmapTaskRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UpdateRoadmapTaskResponse:
    roadmap = await db.get(Roadmap, roadmap_id)
    if roadmap is None:
        raise NotFoundError(MSG_ROADMAP_NOT_FOUND)
    if roadmap.user_id != current_user.id:
        raise ForbiddenError(MSG_FORBIDDEN)

    plan = roadmap.plan or []
    found = False
    total_tasks = 0
    done_tasks = 0
    for week in plan:
        for t in week.get("tasks", []):
            total_tasks += 1
            if t.get("task_id") == task_id:
                t["done"] = payload.done
                found = True
            if t.get("done"):
                done_tasks += 1

    if not found:
        raise NotFoundError(MSG_TASK_NOT_FOUND_IN_ROADMAP)

    roadmap.plan = plan
    # `plan` iki seviye iç içe (hafta -> tasks -> task dict) mutasyona uğradı;
    # `MutableList` yalnızca en dıştaki liste işlemlerini yakalar, bu yüzden
    # değişikliği açıkça işaretleyip UPDATE'e dahil olmasını garanti ediyoruz
    # (bkz. TASK-207 kabul kriterleri: done=true kalıcı olmalı).
    flag_modified(roadmap, "plan")
    roadmap.progress_percent = math.floor((done_tasks / total_tasks) * 100) if total_tasks else 0

    await db.commit()

    return UpdateRoadmapTaskResponse(
        task_id=task_id, done=payload.done, progress_percent=roadmap.progress_percent
    )
