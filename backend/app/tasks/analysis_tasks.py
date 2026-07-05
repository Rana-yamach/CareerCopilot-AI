"""CV üretim, Skill Gap ve Roadmap Celery task'ları (TASK-204, TASK-205, TASK-207)."""
from __future__ import annotations

import asyncio
import uuid

from sqlalchemy import select

from app.core.logging import get_logger
from app.db.session import async_session_maker, run_in_fresh_event_loop
from app.models.cv_draft import CVDraft
from app.models.enums import CVDraftStatus, ProcessingStatus
from app.models.roadmap import Roadmap
from app.models.skill_gap_report import SkillGapReport
from app.models.uploaded_document import UploadedDocument
from app.tasks.celery_app import celery_app

logger = get_logger(__name__)


async def _generate_cv(draft_id: str) -> str:
    from app.agents.cv_writer_agent import CVWriterAgent

    async with async_session_maker() as db:
        draft = await db.get(CVDraft, uuid.UUID(draft_id))
        if draft is None:
            logger.warning("generate_cv_task: draft bulunamadı %s", draft_id)
            return "failed"

        try:
            result = await CVWriterAgent().write(draft.form_data, draft.output_language.value)
            draft.cv_json = result["cv_json"]
            draft.generated_text_tr = result["text_tr"]
            draft.generated_text_en = result["text_en"]
            draft.status = CVDraftStatus.GENERATED
        except Exception:
            logger.exception("generate_cv_task başarısız oldu: %s", draft_id)
            await db.commit()
            return "failed"
        await db.commit()
        return "completed"


@celery_app.task(name="app.tasks.analysis_tasks.generate_cv_task", bind=True)
def generate_cv_task(self, draft_id: str, user_id: str) -> dict:
    meta = {"resource_type": "cv_draft", "resource_id": draft_id, "user_id": user_id}
    self.update_state(state="PROCESSING", meta=meta)
    final_status = asyncio.run(run_in_fresh_event_loop(_generate_cv(draft_id)))
    return {**meta, "final_status": final_status}


async def _analyze_skill_gap(report_id: str, user_id: str, target_position: str) -> str:
    from app.agents.skill_gap_agent import SkillGapAgent

    async with async_session_maker() as db:
        report = await db.get(SkillGapReport, uuid.UUID(report_id))
        if report is None:
            logger.warning("analyze_skill_gap_task: rapor bulunamadı %s", report_id)
            return "failed"

        report.status = ProcessingStatus.PROCESSING
        await db.commit()

        try:
            result = await db.execute(
                select(UploadedDocument).where(UploadedDocument.user_id == uuid.UUID(user_id))
            )
            documents = result.scalars().all()
            parsed_skills_list = [doc.parsed_skills or {} for doc in documents]
            report.source_document_ids = [str(doc.id) for doc in documents]

            analysis = await SkillGapAgent().analyze(db, target_position, parsed_skills_list)
            report.match_score = analysis["match_score"]
            report.missing_skills = analysis["missing_skills"]
            report.status = ProcessingStatus.COMPLETED
            report.error_message = None
        except Exception as exc:
            logger.exception("analyze_skill_gap_task başarısız oldu: %s", report_id)
            report.status = ProcessingStatus.FAILED
            report.error_message = str(exc)
            await db.commit()
            return "failed"

        await db.commit()
        return "completed"


@celery_app.task(name="app.tasks.analysis_tasks.analyze_skill_gap_task", bind=True)
def analyze_skill_gap_task(self, report_id: str, user_id: str, target_position: str) -> dict:
    meta = {"resource_type": "skill_gap_report", "resource_id": report_id, "user_id": user_id}
    self.update_state(state="PROCESSING", meta=meta)
    final_status = asyncio.run(run_in_fresh_event_loop(_analyze_skill_gap(report_id, user_id, target_position)))
    return {**meta, "final_status": final_status}


async def _generate_roadmap(roadmap_id: str, skill_gap_report_id: str, weekly_hours: int) -> str:
    from app.agents.roadmap_agent import RoadmapAgent

    async with async_session_maker() as db:
        roadmap = await db.get(Roadmap, uuid.UUID(roadmap_id))
        if roadmap is None:
            logger.warning("generate_roadmap_task: roadmap bulunamadı %s", roadmap_id)
            return "failed"

        roadmap.status = ProcessingStatus.PROCESSING
        await db.commit()

        try:
            report = await db.get(SkillGapReport, uuid.UUID(skill_gap_report_id))
            missing_skills = report.missing_skills if report else []

            plan = await RoadmapAgent().generate(missing_skills, weekly_hours)
            roadmap.weeks_total = plan["total_weeks"]
            roadmap.milestones = plan["milestones"]

            # Her task'a benzersiz bir task_id ata (PATCH endpoint için).
            weekly_plan = plan["weekly_plan"]
            for week in weekly_plan:
                for t in week.get("tasks", []):
                    t.setdefault("task_id", str(uuid.uuid4()))
            roadmap.plan = weekly_plan

            roadmap.status = ProcessingStatus.COMPLETED
            roadmap.error_message = None
        except Exception as exc:
            logger.exception("generate_roadmap_task başarısız oldu: %s", roadmap_id)
            roadmap.status = ProcessingStatus.FAILED
            roadmap.error_message = str(exc)
            await db.commit()
            return "failed"

        await db.commit()
        return "completed"


@celery_app.task(name="app.tasks.analysis_tasks.generate_roadmap_task", bind=True)
def generate_roadmap_task(self, roadmap_id: str, skill_gap_report_id: str, weekly_hours: int, user_id: str) -> dict:
    meta = {"resource_type": "roadmap", "resource_id": roadmap_id, "user_id": user_id}
    self.update_state(state="PROCESSING", meta=meta)
    final_status = asyncio.run(
        run_in_fresh_event_loop(_generate_roadmap(roadmap_id, skill_gap_report_id, weekly_hours))
    )
    return {**meta, "final_status": final_status}
