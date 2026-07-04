"""TASK-211 kabul kriterleri + IDOR regresyon testi (kod incelemesi bulgu #2).

Bug: `POST /agent/chat` client'ın gönderdiği keyfi bir `session_id`'nin sahiplik
kontrolü yapmadan geçmiş mesaj sorgusunda kullanıyordu; başka bir kullanıcının
chat geçmişi LLM bağlamına dahil edilip o session'a mesaj eklenebiliyordu.
Düzeltme: `ChatMessage.user_id == current_user.id` filtresi eklendi; sonuç
boşsa (session yok ya da başkasına aitse) sessizce yeni bir session_id üretilir.
"""
from __future__ import annotations

import json
import re
import uuid

import pytest


@pytest.fixture(autouse=True)
def _force_llm_fallback(monkeypatch):
    """`/agent/chat` senkron olarak aynı process içinde ajanları çağırır (Celery
    değil), bu yüzden monkeypatch burada etkilidir. LLM ağ çağrısına bağımlı
    olmadan orchestrator'ın heuristic intent sınıflandırma yoluna zorlar."""

    async def _raise(*_args, **_kwargs):
        raise RuntimeError("Test ortamında LLM çağrısı devre dışı bırakıldı (heuristic fallback zorlanıyor).")

    monkeypatch.setattr("app.llm.hf_client.HFInferenceClient.generate", _raise)


async def _register(client) -> str:
    email = f"chat_{uuid.uuid4().hex[:10]}@example.com"
    response = await client.post("/api/v1/auth/register", json={"email": email, "password": "password123"})
    return response.json()["access_token"]


def _extract_metadata(sse_text: str) -> dict:
    match = re.search(r"event: metadata\r?\ndata: (\{.*\})", sse_text)
    assert match, f"metadata event bulunamadı: {sse_text!r}"
    return json.loads(match.group(1))


@pytest.mark.asyncio
async def test_chat_ignores_session_id_belonging_to_another_user(client):
    token_a = await _register(client)
    token_b = await _register(client)

    message_a = "Google SWE olmak istiyorsam sıradaki adımım ne?"
    response_a = await client.post(
        "/api/v1/agent/chat",
        headers={"Authorization": f"Bearer {token_a}"},
        json={"message": message_a, "session_id": None},
    )
    assert response_a.status_code == 200, response_a.text
    session_id_a = _extract_metadata(response_a.text)["session_id"]

    # Kullanıcı B, kullanıcı A'nın session_id'sini kullanmaya çalışır (IDOR denemesi).
    message_b = "Bu oturuma sızmaya çalışıyorum"
    response_b = await client.post(
        "/api/v1/agent/chat",
        headers={"Authorization": f"Bearer {token_b}"},
        json={"message": message_b, "session_id": session_id_a},
    )
    assert response_b.status_code == 200, response_b.text
    session_id_b = _extract_metadata(response_b.text)["session_id"]

    # Sunucu, B'nin isteği için A'nın session_id'sini asla kullanmamalı;
    # sessizce yeni bir oturum açmalı (403 fırlatmak yerine).
    assert session_id_b != session_id_a

    # B'nin kendi (yeni) oturumunun geçmişinde A'nın mesajı kesinlikle olmamalı.
    messages_b = await client.get(
        f"/api/v1/agent/sessions/{session_id_b}/messages",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert messages_b.status_code == 200
    contents_b = [m["content"] for m in messages_b.json()["messages"]]
    assert message_a not in contents_b
    assert message_b in contents_b

    # A'nın kendi oturumu B'nin denemesinden hiç etkilenmemiş olmalı.
    messages_a = await client.get(
        f"/api/v1/agent/sessions/{session_id_a}/messages",
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert messages_a.status_code == 200
    contents_a = [m["content"] for m in messages_a.json()["messages"]]
    assert message_a in contents_a
    assert message_b not in contents_a

    # A, kendi session_id'sini tekrar kullanarak konuşmaya devam edebilmeli.
    response_a2 = await client.post(
        "/api/v1/agent/chat",
        headers={"Authorization": f"Bearer {token_a}"},
        json={"message": "Peki sonraki adım ne olmalı?", "session_id": session_id_a},
    )
    assert response_a2.status_code == 200
    assert _extract_metadata(response_a2.text)["session_id"] == session_id_a


@pytest.mark.asyncio
async def test_chat_with_nonexistent_session_id_starts_fresh_session(client):
    token = await _register(client)
    fake_session_id = str(uuid.uuid4())

    response = await client.post(
        "/api/v1/agent/chat",
        headers={"Authorization": f"Bearer {token}"},
        json={"message": "Hiç var olmayan bir session_id gönderiyorum", "session_id": fake_session_id},
    )
    assert response.status_code == 200
    returned_session_id = _extract_metadata(response.text)["session_id"]
    assert returned_session_id != fake_session_id
