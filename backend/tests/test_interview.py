"""TASK-210 kabul kriterleri + JSONB mutasyon regresyon testi.

Kod incelemesi bulgu #1 (KRİTİK): `InterviewSession.questions` düz JSONB kolonu
in-place mutasyona uğrayıp aynı obje referansıyla geri atanınca SQLAlchemy
değişikliği "değişmemiş" sanıp UPDATE'e dahil etmiyordu. Bu testler; hem
ara sorularda (append çağrılan dal) hem de oturum tamamlanma anında (append
çağrılmayan, yalnızca iç içe dict mutasyonu içeren dal) cevapların kalıcı
yazıldığını doğrular.
"""
from __future__ import annotations

import uuid

import pytest


@pytest.fixture(autouse=True)
def _force_llm_fallback(monkeypatch):
    """LLM (HF Inference API) çağrısını devre dışı bırakıp heuristic fallback
    yoluna zorlar. Bu testler JSONB kalıcılık regresyonunu doğruluyor; gerçek
    HF ağ çağrısına (token/ağ erişimi belirsiz, yavaş) bağımlı olmamalı."""

    async def _raise(*_args, **_kwargs):
        raise RuntimeError("Test ortamında LLM çağrısı devre dışı bırakıldı (heuristic fallback zorlanıyor).")

    monkeypatch.setattr("app.llm.hf_client.HFInferenceClient.generate", _raise)


async def _register(client) -> str:
    email = f"iv_{uuid.uuid4().hex[:10]}@example.com"
    response = await client.post("/api/v1/auth/register", json={"email": email, "password": "password123"})
    return response.json()["access_token"]


async def _start_session(client, token: str) -> dict:
    response = await client.post(
        "/api/v1/interview/start",
        headers={"Authorization": f"Bearer {token}"},
        json={"target_position": "Google SWE L3", "difficulty": "junior", "category": "algorithmic"},
    )
    assert response.status_code == 201, response.text
    return response.json()


@pytest.mark.asyncio
async def test_consecutive_answers_are_persisted_and_advance_correctly(client):
    """Regresyon: ilk cevap DB'ye yazılmadan ikinci `answer` çağrısı yapılırsa
    (bug'ta) question_index uyuşmazlığı/422 üretiyordu ya da ilk cevap sessizce
    kayboluyordu. Artık her iki çağrı da 200 dönmeli ve cevaplar kalıcı olmalı."""
    token = await _register(client)
    started = await _start_session(client, token)
    session_id = started["session_id"]
    assert started["question_index"] == 0

    answer_0 = await client.post(
        f"/api/v1/interview/{session_id}/answer",
        headers={"Authorization": f"Bearer {token}"},
        json={"question_index": 0, "user_answer": "İki pointer kullanarak diziyi taradım ve karşılaştırdım."},
    )
    assert answer_0.status_code == 200, answer_0.text
    body_0 = answer_0.json()
    assert body_0["answered"]["question_index"] == 0
    assert body_0["answered"]["user_answer"]
    assert body_0["is_session_complete"] is False
    next_q = body_0["next_question"]
    assert next_q is not None
    assert next_q["question_index"] == 1

    answer_1 = await client.post(
        f"/api/v1/interview/{session_id}/answer",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "question_index": 1,
            "user_answer": "Binary search tree'de in-order traversal ile k'ıncı elemanı bulurum.",
        },
    )
    assert answer_1.status_code == 200, answer_1.text
    body_1 = answer_1.json()
    assert body_1["answered"]["question_index"] == 1
    assert body_1["answered"]["user_answer"]

    summary = await client.get(
        f"/api/v1/interview/{session_id}/summary", headers={"Authorization": f"Bearer {token}"}
    )
    assert summary.status_code == 200, summary.text
    summary_body = summary.json()
    answered_questions = [q for q in summary_body["questions"] if q.get("user_answer")]
    assert len(answered_questions) == 2
    assert answered_questions[0]["question_index"] == 0
    assert answered_questions[1]["question_index"] == 1


@pytest.mark.asyncio
async def test_final_answer_persists_even_without_next_question_append(client):
    """Regresyon: MAX_QUESTIONS'a ulaşıldığında kod `questions.append(...)`
    çağırmaz (yalnızca iç içe dict mutasyonu yapar); bu dal `MutableList`
    sarmalayıcısını bile tetiklemeyebileceği için `flag_modified` gereklidir.
    Son sorunun cevabı ve overall_score kalıcı yazılmalı."""
    token = await _register(client)
    started = await _start_session(client, token)
    session_id = started["session_id"]

    last_response = None
    for idx in range(5):  # interview.py MAX_QUESTIONS = 5
        last_response = await client.post(
            f"/api/v1/interview/{session_id}/answer",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "question_index": idx,
                "user_answer": f"Cevap numarası {idx} - detaylı açıklama ve örnekler içerir.",
            },
        )
        assert last_response.status_code == 200, last_response.text

    final_body = last_response.json()
    assert final_body["is_session_complete"] is True
    assert final_body["next_question"] is None

    summary = await client.get(
        f"/api/v1/interview/{session_id}/summary", headers={"Authorization": f"Bearer {token}"}
    )
    assert summary.status_code == 200, summary.text
    summary_body = summary.json()
    assert summary_body["ended_at"] is not None
    assert summary_body["overall_score"] is not None

    answered = [q for q in summary_body["questions"] if q.get("user_answer")]
    assert len(answered) == 5

    last_q = next(q for q in summary_body["questions"] if q["question_index"] == 4)
    assert last_q["user_answer"] is not None
    assert last_q["score"] is not None
    assert last_q["feedback"] is not None


@pytest.mark.asyncio
async def test_other_users_interview_session_returns_403(client):
    token_a = await _register(client)
    token_b = await _register(client)

    started = await _start_session(client, token_a)
    session_id = started["session_id"]

    response = await client.post(
        f"/api/v1/interview/{session_id}/answer",
        headers={"Authorization": f"Bearer {token_b}"},
        json={"question_index": 0, "user_answer": "Başka birinin oturumuna cevap vermeye çalışıyorum."},
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "FORBIDDEN"
