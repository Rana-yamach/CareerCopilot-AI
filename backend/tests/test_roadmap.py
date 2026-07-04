"""TASK-207 kabul kriterleri + JSONB mutasyon regresyon testi.

Kod incelemesi bulgu #1 (KRİTİK): `Roadmap.plan` düz JSONB kolonu, haftalık
plan içindeki iç içe geçmiş task dict'leri in-place mutasyona uğrayıp aynı
obje referansıyla geri atanınca SQLAlchemy değişikliği algılamıyor,
`done: true` DB'ye asla yazılmıyordu. Bu testler gerçek Celery worker'a karşı
çalışır (docker-compose): skill-gap analizi -> roadmap üretimi -> görev
tamamlama -> kalıcılık ve kümülatif progress_percent doğrulaması.
"""
from __future__ import annotations

import io
import math
import time
import uuid

import pytest

POLL_INTERVAL_SECONDS = 1.5
POLL_TIMEOUT_SECONDS = 120.0

# NOT: Skill Gap / Roadmap üretimi gerçek Celery worker (ayrı bir process/container)
# tarafından yürütülür; bu yüzden test_interview.py'deki gibi `monkeypatch` ile
# `HFInferenceClient.generate`'i bu süreç içinde geçersiz kılmanın worker
# process'ine hiçbir etkisi olmaz. `.env` içindeki `HF_API_TOKEN` placeholder
# (`hf_xxx_replace_me`) olduğundan gerçek HF çağrısı zaten 401 ile hızla başarısız
# olur ve mevcut heuristic fallback yoluna düşer — testler bu doğal davranışa
# dayanır (ayrıca bkz. RoadmapAgent/SkillGapAgent heuristic fallback).


async def _register(client) -> str:
    email = f"rm_{uuid.uuid4().hex[:10]}@example.com"
    response = await client.post("/api/v1/auth/register", json={"email": email, "password": "password123"})
    return response.json()["access_token"]


async def _upload_minimal_cv(client, token: str) -> None:
    response = await client.post(
        "/api/v1/documents/upload",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("cv.pdf", io.BytesIO(b"%PDF-1.4\n%%EOF"), "application/pdf")},
        data={"document_type": "cv"},
    )
    assert response.status_code == 202, response.text


async def _wait_for_status(client, token: str, url: str) -> dict:
    deadline = time.monotonic() + POLL_TIMEOUT_SECONDS
    while True:
        response = await client.get(url, headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200, response.text
        body = response.json()
        if body["status"] in ("completed", "failed"):
            return body
        if time.monotonic() > deadline:
            pytest.fail(f"{url} zaman aşımına uğradı (celery_worker çalışıyor mu?), son durum: {body}")
        import asyncio

        await asyncio.sleep(POLL_INTERVAL_SECONDS)


@pytest.mark.asyncio
async def test_roadmap_task_completion_persists_and_progress_accumulates(client):
    token = await _register(client)
    await _upload_minimal_cv(client, token)

    analyze_response = await client.post(
        "/api/v1/skill-gap/analyze",
        headers={"Authorization": f"Bearer {token}"},
        json={"target_position": "Google SWE L3"},
    )
    assert analyze_response.status_code == 202, analyze_response.text
    report_id = analyze_response.json()["report_id"]

    report = await _wait_for_status(client, token, f"/api/v1/skill-gap/{report_id}")
    assert report["status"] == "completed", report

    generate_response = await client.post(
        "/api/v1/roadmap/generate",
        headers={"Authorization": f"Bearer {token}"},
        json={"skill_gap_report_id": report_id, "weekly_hours": 10},
    )
    assert generate_response.status_code == 202, generate_response.text
    roadmap_id = generate_response.json()["roadmap_id"]

    roadmap = await _wait_for_status(client, token, f"/api/v1/roadmap/{roadmap_id}")
    assert roadmap["status"] == "completed", roadmap
    assert roadmap["progress_percent"] == 0

    all_task_ids = [t["task_id"] for week in roadmap["plan"] for t in week["tasks"]]
    total_tasks = len(all_task_ids)
    assert total_tasks > 0

    # --- Görev 1'i tamamla ---
    patch_1 = await client.patch(
        f"/api/v1/roadmap/{roadmap_id}/task/{all_task_ids[0]}",
        headers={"Authorization": f"Bearer {token}"},
        json={"done": True},
    )
    assert patch_1.status_code == 200, patch_1.text
    body_1 = patch_1.json()
    assert body_1["done"] is True
    expected_progress_1 = math.floor((1 / total_tasks) * 100)
    assert body_1["progress_percent"] == expected_progress_1

    # Regresyon: kalıcılığı ayrı bir GET ile doğrula (bug'ta done=true asla
    # DB'ye yazılmıyor, her GET progress_percent=0 ve done=false dönüyordu).
    roadmap_after_1 = await client.get(
        f"/api/v1/roadmap/{roadmap_id}", headers={"Authorization": f"Bearer {token}"}
    )
    assert roadmap_after_1.status_code == 200
    roadmap_after_1_body = roadmap_after_1.json()
    assert roadmap_after_1_body["progress_percent"] == expected_progress_1
    first_task = next(
        t for week in roadmap_after_1_body["plan"] for t in week["tasks"] if t["task_id"] == all_task_ids[0]
    )
    assert first_task["done"] is True

    if total_tasks == 1:
        return

    # --- Görev 2'yi de tamamla: progress kümülatif artmalı ---
    patch_2 = await client.patch(
        f"/api/v1/roadmap/{roadmap_id}/task/{all_task_ids[1]}",
        headers={"Authorization": f"Bearer {token}"},
        json={"done": True},
    )
    assert patch_2.status_code == 200, patch_2.text
    expected_progress_2 = math.floor((2 / total_tasks) * 100)
    assert patch_2.json()["progress_percent"] == expected_progress_2
    assert expected_progress_2 >= expected_progress_1

    roadmap_after_2 = await client.get(
        f"/api/v1/roadmap/{roadmap_id}", headers={"Authorization": f"Bearer {token}"}
    )
    roadmap_after_2_body = roadmap_after_2.json()
    assert roadmap_after_2_body["progress_percent"] == expected_progress_2
    done_count = sum(1 for week in roadmap_after_2_body["plan"] for t in week["tasks"] if t["done"])
    assert done_count == 2
    # İlk görevin done durumu da hâlâ korunmalı (üzerine yazılmamalı).
    first_task_after_2 = next(
        t for week in roadmap_after_2_body["plan"] for t in week["tasks"] if t["task_id"] == all_task_ids[0]
    )
    assert first_task_after_2["done"] is True


@pytest.mark.asyncio
async def test_task_not_found_in_roadmap_returns_404(client):
    token = await _register(client)
    await _upload_minimal_cv(client, token)

    analyze_response = await client.post(
        "/api/v1/skill-gap/analyze",
        headers={"Authorization": f"Bearer {token}"},
        json={"target_position": "Backend Developer"},
    )
    report_id = analyze_response.json()["report_id"]
    await _wait_for_status(client, token, f"/api/v1/skill-gap/{report_id}")

    generate_response = await client.post(
        "/api/v1/roadmap/generate",
        headers={"Authorization": f"Bearer {token}"},
        json={"skill_gap_report_id": report_id, "weekly_hours": 5},
    )
    roadmap_id = generate_response.json()["roadmap_id"]
    await _wait_for_status(client, token, f"/api/v1/roadmap/{roadmap_id}")

    response = await client.patch(
        f"/api/v1/roadmap/{roadmap_id}/task/{uuid.uuid4()}",
        headers={"Authorization": f"Bearer {token}"},
        json={"done": True},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_other_users_roadmap_task_update_returns_403(client):
    token_a = await _register(client)
    token_b = await _register(client)
    await _upload_minimal_cv(client, token_a)

    analyze_response = await client.post(
        "/api/v1/skill-gap/analyze",
        headers={"Authorization": f"Bearer {token_a}"},
        json={"target_position": "Data Scientist"},
    )
    report_id = analyze_response.json()["report_id"]
    await _wait_for_status(client, token_a, f"/api/v1/skill-gap/{report_id}")

    generate_response = await client.post(
        "/api/v1/roadmap/generate",
        headers={"Authorization": f"Bearer {token_a}"},
        json={"skill_gap_report_id": report_id, "weekly_hours": 5},
    )
    roadmap_id = generate_response.json()["roadmap_id"]
    roadmap = await _wait_for_status(client, token_a, f"/api/v1/roadmap/{roadmap_id}")
    task_id = roadmap["plan"][0]["tasks"][0]["task_id"]

    response = await client.patch(
        f"/api/v1/roadmap/{roadmap_id}/task/{task_id}",
        headers={"Authorization": f"Bearer {token_b}"},
        json={"done": True},
    )
    assert response.status_code == 403
