"""API_CONTRACT.md §7 Interview (TASK-210)."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified

from app.agents.interview_agent import InterviewAgent
from app.core.constants import (
    MSG_FORBIDDEN,
    MSG_INTERVIEW_QUESTION_INDEX_MISMATCH,
    MSG_INTERVIEW_SESSION_ALREADY_ENDED,
    MSG_INTERVIEW_SESSION_NOT_FOUND,
)
from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError, ValidationError
from app.deps import get_current_user, get_db
from app.models.interview_session import InterviewSession
from app.models.user import User
from app.schemas.interview import (
    AnswerInterviewRequest,
    AnswerInterviewResponse,
    AnsweredQuestion,
    InterviewSessionListItem,
    InterviewSessionsResponse,
    InterviewSummaryResponse,
    NextQuestion,
    StartInterviewRequest,
    StartInterviewResponse,
)

router = APIRouter()

MAX_QUESTIONS = 5


@router.post("/start", response_model=StartInterviewResponse, status_code=201)
async def start_interview(
    payload: StartInterviewRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> StartInterviewResponse:
    question = await InterviewAgent().generate_question(
        target_position=payload.target_position,
        difficulty=payload.difficulty,
        category=payload.category,
        question_index=0,
        previous_qa=[],
    )

    session = InterviewSession(
        user_id=current_user.id,
        target_position=payload.target_position,
        difficulty=payload.difficulty,
        category=payload.category,
        questions=[{"question_index": 0, "question": question, "user_answer": None, "feedback": None, "score": None, "correct_answer_hint": None}],
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)

    return StartInterviewResponse(
        session_id=str(session.id),
        question_index=0,
        question=question,
        target_position=session.target_position,
        difficulty=session.difficulty.value,
        category=session.category.value,
        started_at=session.started_at,
    )


@router.post("/{session_id}/answer", response_model=AnswerInterviewResponse)
async def answer_interview(
    session_id: uuid.UUID,
    payload: AnswerInterviewRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AnswerInterviewResponse:
    session = await db.get(InterviewSession, session_id)
    if session is None:
        raise NotFoundError(MSG_INTERVIEW_SESSION_NOT_FOUND)
    if session.user_id != current_user.id:
        raise ForbiddenError(MSG_FORBIDDEN)
    if session.ended_at is not None:
        raise ConflictError(MSG_INTERVIEW_SESSION_ALREADY_ENDED)

    questions = session.questions or []
    current_q = next((q for q in questions if q["question_index"] == payload.question_index), None)
    if current_q is None:
        raise ValidationError(MSG_INTERVIEW_QUESTION_INDEX_MISMATCH)

    agent = InterviewAgent()
    evaluation = await agent.evaluate_answer(
        target_position=session.target_position,
        difficulty=session.difficulty.value,
        category=session.category.value,
        question=current_q["question"],
        user_answer=payload.user_answer,
    )

    current_q["user_answer"] = payload.user_answer
    current_q["feedback"] = evaluation.get("feedback")
    current_q["score"] = evaluation.get("score")
    current_q["correct_answer_hint"] = evaluation.get("correct_answer_hint")

    is_complete = len(questions) >= MAX_QUESTIONS
    next_question_payload = None

    if not is_complete:
        next_index = payload.question_index + 1
        next_question_text = await agent.generate_question(
            target_position=session.target_position,
            difficulty=session.difficulty.value,
            category=session.category.value,
            question_index=next_index,
            previous_qa=questions,
        )
        questions.append(
            {
                "question_index": next_index,
                "question": next_question_text,
                "user_answer": None,
                "feedback": None,
                "score": None,
                "correct_answer_hint": None,
            }
        )
        next_question_payload = NextQuestion(question_index=next_index, question=next_question_text)
    else:
        session.ended_at = datetime.now(timezone.utc)
        scores = [q["score"] for q in questions if q.get("score") is not None]
        session.overall_score = round(sum(scores) / len(scores) * 10) if scores else None

    session.questions = questions
    # `questions` içindeki dict elemanları yerinde (in-place) mutasyona uğradı
    # (current_q["user_answer"] = ... vb.). `MutableList` sarmalayıcısı yalnızca
    # liste seviyeli işlemleri (append/pop/...) yakalar; iç içe dict
    # mutasyonlarının oturum tamamlanma dalında (append çağrılmadığı durumda)
    # da kalıcı yazılmasını garanti etmek için değişikliği açıkça işaretliyoruz.
    flag_modified(session, "questions")
    await db.commit()

    return AnswerInterviewResponse(
        session_id=str(session.id),
        answered=AnsweredQuestion(
            question_index=current_q["question_index"],
            question=current_q["question"],
            user_answer=current_q["user_answer"],
            feedback=current_q["feedback"],
            score=current_q["score"],
            correct_answer_hint=current_q["correct_answer_hint"],
        ),
        next_question=next_question_payload,
        is_session_complete=is_complete,
    )


@router.get("/{session_id}/summary", response_model=InterviewSummaryResponse)
async def get_interview_summary(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> InterviewSummaryResponse:
    session = await db.get(InterviewSession, session_id)
    if session is None:
        raise NotFoundError(MSG_INTERVIEW_SESSION_NOT_FOUND)
    if session.user_id != current_user.id:
        raise ForbiddenError(MSG_FORBIDDEN)

    questions = session.questions or []
    scored = [q for q in questions if q.get("score") is not None]
    strengths = [f"{q['question'][:40]}... konusunda iyi performans" for q in scored if q["score"] >= 7][:3]
    improvements = [f"{q['question'][:40]}... konusunda geliştirme alanı" for q in scored if q["score"] < 7][:3]

    return InterviewSummaryResponse(
        session_id=str(session.id),
        target_position=session.target_position,
        difficulty=session.difficulty.value,
        category=session.category.value,
        overall_score=session.overall_score,
        questions=questions,
        strengths=strengths or ["Genel katılım ve iletişim"],
        improvements=improvements or ["Daha fazla pratik yapılması önerilir"],
        started_at=session.started_at,
        ended_at=session.ended_at,
    )


@router.get("/sessions", response_model=InterviewSessionsResponse)
async def list_interview_sessions(
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> InterviewSessionsResponse:
    limit = min(limit, 100)
    query = (
        select(InterviewSession)
        .where(InterviewSession.user_id == current_user.id)
        .order_by(InterviewSession.started_at.desc())
        .limit(limit)
        .offset(offset)
    )
    count_query = select(func.count()).select_from(InterviewSession).where(
        InterviewSession.user_id == current_user.id
    )

    result = await db.execute(query)
    sessions = result.scalars().all()
    total = (await db.execute(count_query)).scalar_one()

    items = [
        InterviewSessionListItem(
            session_id=str(s.id),
            target_position=s.target_position,
            category=s.category.value,
            overall_score=s.overall_score,
            started_at=s.started_at,
            ended_at=s.ended_at,
        )
        for s in sessions
    ]
    return InterviewSessionsResponse(items=items, total=total)
