"""TASK-108 kabul kriterleri: form validasyonu + sahiplik kontrolü (403)."""
import uuid

import pytest

VALID_FORM_DATA = {
    "personal": {"name": "Ahmet Yılmaz", "email": "ahmet@example.com"},
    "selected_sections": ["skills"],
    "sections": [
        {
            "type": "skills",
            "order": 1,
            "title": "Yetenekler",
            "content": {"languages": ["Python"], "frameworks": [], "tools": []},
        }
    ],
    "github_projects_imported": False,
}


async def _register(client) -> str:
    email = f"cv_{uuid.uuid4().hex[:10]}@example.com"
    response = await client.post("/api/v1/auth/register", json={"email": email, "password": "password123"})
    return response.json()["access_token"]


@pytest.mark.asyncio
async def test_generate_cv_missing_name_email_returns_422(client):
    token = await _register(client)
    payload = {
        "form_data": {**VALID_FORM_DATA, "personal": {"name": "", "email": ""}},
        "output_language": "tr",
    }
    response = await client.post(
        "/api/v1/cv/generate", headers={"Authorization": f"Bearer {token}"}, json=payload
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_generate_cv_empty_sections_returns_422(client):
    token = await _register(client)
    payload = {
        "form_data": {**VALID_FORM_DATA, "selected_sections": []},
        "output_language": "tr",
    }
    response = await client.post(
        "/api/v1/cv/generate", headers={"Authorization": f"Bearer {token}"}, json=payload
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_generate_cv_success_returns_202(client):
    token = await _register(client)
    payload = {"form_data": VALID_FORM_DATA, "output_language": "tr"}
    response = await client.post(
        "/api/v1/cv/generate", headers={"Authorization": f"Bearer {token}"}, json=payload
    )
    assert response.status_code == 202
    body = response.json()
    assert body["draft_id"]
    assert body["status"] == "queued"


@pytest.mark.asyncio
async def test_other_users_draft_returns_403(client):
    token_a = await _register(client)
    token_b = await _register(client)

    payload = {"form_data": VALID_FORM_DATA, "output_language": "tr"}
    create_response = await client.post(
        "/api/v1/cv/generate", headers={"Authorization": f"Bearer {token_a}"}, json=payload
    )
    draft_id = create_response.json()["draft_id"]

    response = await client.get(
        f"/api/v1/cv/draft/{draft_id}", headers={"Authorization": f"Bearer {token_b}"}
    )
    assert response.status_code == 403
