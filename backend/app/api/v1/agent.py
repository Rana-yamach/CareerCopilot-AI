"""API_CONTRACT.md §9 Agent — Chat / Orchestrator (TASK-211).

`/agent/chat` senkron SSE stream olarak çalışır (ARCHITECTURE.md §3.3):
Orchestrator intent sınıflandırır, ilgili alt ajanın kısa Türkçe yanıtını
üretir ve kelime kelime akıtır.
"""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Header
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base import AgentContext
from app.agents.orchestrator import OrchestratorAgent
from app.agents.skill_gap_agent import SkillGapAgent
from app.core.constants import MSG_FORBIDDEN
from app.core.exceptions import ForbiddenError, NotFoundError, UnauthorizedError
from app.core.security import decode_access_token
from app.deps import get_current_user, get_db
from app.llm.streaming import sse_done, sse_error, sse_event
from app.models.chat_message import ChatMessage
from app.models.enums import ChatRole
from app.models.user import User
from app.repositories.user_repository import get_profile_by_user_id
from app.schemas.chat import (
    ChatSessionMessagesResponse,
    ChatSessionsResponse,
    SendChatMessageRequest,
)

router = APIRouter()


async def _authenticate_for_sse(authorization: str | None, db: AsyncSession) -> User:
    """StreamingResponse başlamadan önce senkron 401 kontrolü (contract gereği)."""
    if not authorization or not authorization.lower().startswith("bearer "):
        raise UnauthorizedError("Kimlik doğrulama gerekli.")
    token = authorization.split(" ", 1)[1].strip()
    try:
        payload = decode_access_token(token)
    except ValueError as exc:
        raise UnauthorizedError("Token geçersiz veya süresi dolmuş.") from exc
    user = await db.get(User, uuid.UUID(payload["sub"]))
    if user is None:
        raise UnauthorizedError("Kullanıcı bulunamadı.")
    return user


async def _build_reply(db: AsyncSession, user: User, intent: str, message: str) -> str:
    if intent == "skill_gap":
        result = await SkillGapAgent().analyze(db, target_position=message, documents_parsed_skills=[])
        skills = ", ".join(s["name"] for s in result["missing_skills"][:3]) or "belirli bir eksiklik"
        return (
            f"Profilini incelediğimde eşleşme skorun yaklaşık %{result['match_score']}. "
            f"Öncelikli olarak şu konulara odaklanmanı öneririm: {skills}. "
            "Detaylı rapor için Beceri Boşluğu sayfasını ziyaret edebilirsin."
        )
    if intent == "cv_writer":
        return (
            "CV oluşturmak için CV Oluşturucu sayfasındaki bölüm seçim ekranını kullanabilirsin; "
            "orada adım adım seni yönlendireceğim."
        )
    if intent == "cv_agent":
        return (
            "CV'ni analiz etmemi istiyorsan Belgelerim sayfasından PDF/DOCX formatında yükleyebilirsin; "
            "yükleme sonrası analiz otomatik başlar."
        )
    if intent == "roadmap":
        return (
            "Kişisel bir haftalık çalışma planı oluşturmak için önce bir Beceri Boşluğu analizi yapmalısın, "
            "ardından Yol Haritası sayfasından planını oluşturabilirsin."
        )
    if intent == "interview":
        return (
            "Mülakat simülasyonuna başlamak için Mülakat sayfasına gidip hedef pozisyonunu ve "
            "zorluk seviyeni seçebilirsin."
        )
    return OrchestratorAgent().build_general_reply(message)


@router.post("/chat")
async def chat(
    payload: SendChatMessageRequest,
    authorization: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    user = await _authenticate_for_sse(authorization, db)

    message_id = str(uuid.uuid4())

    profile = await get_profile_by_user_id(db, user.id)
    user_profile_dict = {
        "target_position": profile.target_position if profile else None,
        "target_company": profile.target_company if profile else None,
        "github_username": profile.github_username if profile else None,
    }

    # IDOR koruması: client keyfi bir session_id gönderebilir. Geçmişi her
    # zaman `ChatMessage.user_id == user.id` filtresiyle çekiyoruz; sonuç boş
    # dönerse (session hiç yoksa ya da başka bir kullanıcıya aitse) 403
    # fırlatmak yerine sessizce yeni bir oturum başlatıyoruz — böylece başka
    # bir kullanıcının chat geçmişi asla bu isteğin bağlamına sızmaz.
    session_id = payload.session_id
    if session_id:
        history_result = await db.execute(
            select(ChatMessage)
            .where(
                ChatMessage.session_id == uuid.UUID(session_id),
                ChatMessage.user_id == user.id,
            )
            .order_by(ChatMessage.created_at.desc())
            .limit(10)
        )
        history_messages = list(reversed(history_result.scalars().all()))
        if not history_messages:
            session_id = str(uuid.uuid4())
            chat_history: list[dict] = []
        else:
            chat_history = [{"role": m.role.value, "content": m.content} for m in history_messages]
    else:
        session_id = str(uuid.uuid4())
        chat_history = []

    db.add(ChatMessage(user_id=user.id, session_id=uuid.UUID(session_id), role=ChatRole.USER, content=payload.message))
    await db.commit()

    ctx = AgentContext(
        user_id=str(user.id),
        session_id=session_id,
        user_profile=user_profile_dict,
        chat_history=chat_history,
    )

    async def event_generator():
        orchestrator = OrchestratorAgent()
        classification = await orchestrator.classify_intent(ctx, payload.message)
        intent = classification.get("intent", "general")
        agent_used = classification.get("followup_agent") or intent

        yield sse_event(
            {"session_id": session_id, "message_id": message_id, "intent": intent, "agent": agent_used},
            event="metadata",
        )

        try:
            reply_text = await _build_reply(db, user, intent, payload.message)
        except Exception:  # noqa: BLE001
            yield sse_error("LLM_ERROR", "Sunucu şu anda yoğun, lütfen tekrar deneyin.")
            yield sse_done()
            return

        for word in reply_text.split(" "):
            yield sse_event({"token": word + " "})

        db.add(
            ChatMessage(
                user_id=user.id,
                session_id=uuid.UUID(session_id),
                role=ChatRole.ASSISTANT,
                content=reply_text,
                agent_used=agent_used,
            )
        )
        await db.commit()

        yield sse_done()

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.get("/sessions", response_model=ChatSessionsResponse)
async def list_chat_sessions(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> ChatSessionsResponse:
    result = await db.execute(
        select(ChatMessage).where(ChatMessage.user_id == current_user.id).order_by(ChatMessage.created_at.desc())
    )
    messages = result.scalars().all()

    sessions: dict[str, dict] = {}
    for m in messages:
        sid = str(m.session_id)
        if sid not in sessions:
            sessions[sid] = {
                "session_id": sid,
                "last_message_preview": m.content[:120],
                "last_agent": m.agent_used,
                "message_count": 0,
                "started_at": m.created_at,
                "last_message_at": m.created_at,
            }
        sessions[sid]["message_count"] += 1
        if m.created_at < sessions[sid]["started_at"]:
            sessions[sid]["started_at"] = m.created_at

    return ChatSessionsResponse(sessions=list(sessions.values()))


@router.get("/sessions/{session_id}/messages", response_model=ChatSessionMessagesResponse)
async def get_session_messages(
    session_id: uuid.UUID,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ChatSessionMessagesResponse:
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.asc())
        .limit(limit)
    )
    messages = result.scalars().all()
    if not messages:
        raise NotFoundError("Sohbet oturumu bulunamadı.")
    if messages[0].user_id != current_user.id:
        raise ForbiddenError(MSG_FORBIDDEN)

    return ChatSessionMessagesResponse(
        session_id=str(session_id),
        messages=[
            {
                "message_id": str(m.id),
                "role": m.role.value,
                "content": m.content,
                "agent_used": m.agent_used,
                "created_at": m.created_at,
            }
            for m in messages
        ],
    )
