"""TASK-106 / TASK-302 kabul kriterleri: dosya validasyonu + sahiplik kontrolü (403)."""
import io
import uuid

import pytest


async def _register(client) -> str:
    email = f"doc_{uuid.uuid4().hex[:10]}@example.com"
    response = await client.post("/api/v1/auth/register", json={"email": email, "password": "password123"})
    return response.json()["access_token"]


@pytest.mark.asyncio
async def test_upload_rejects_unsupported_file_type(client):
    token = await _register(client)
    response = await client.post(
        "/api/v1/documents/upload",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("test.txt", io.BytesIO(b"hello world"), "text/plain")},
        data={"document_type": "cv"},
    )
    assert response.status_code == 415
    assert response.json()["error"]["code"] == "UNSUPPORTED_MEDIA_TYPE"


@pytest.mark.asyncio
async def test_upload_rejects_oversized_file(client):
    token = await _register(client)
    big_content = b"%PDF-1.4\n" + b"0" * (6 * 1024 * 1024)
    response = await client.post(
        "/api/v1/documents/upload",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("test.pdf", io.BytesIO(big_content), "application/pdf")},
        data={"document_type": "cv"},
    )
    assert response.status_code == 413
    assert response.json()["error"]["code"] == "PAYLOAD_TOO_LARGE"


@pytest.mark.asyncio
async def test_upload_rejects_invalid_document_type(client):
    token = await _register(client)
    response = await client.post(
        "/api/v1/documents/upload",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("test.pdf", io.BytesIO(b"%PDF-1.4\n%%EOF"), "application/pdf")},
        data={"document_type": "resume"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_other_users_document_status_returns_403(client):
    token_a = await _register(client)
    token_b = await _register(client)

    upload_response = await client.post(
        "/api/v1/documents/upload",
        headers={"Authorization": f"Bearer {token_a}"},
        files={"file": ("test.pdf", io.BytesIO(b"%PDF-1.4\n%%EOF"), "application/pdf")},
        data={"document_type": "cv"},
    )
    doc_id = upload_response.json()["document_id"]

    response = await client.get(
        f"/api/v1/documents/{doc_id}/status", headers={"Authorization": f"Bearer {token_b}"}
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "FORBIDDEN"


@pytest.mark.asyncio
async def test_document_status_not_found_returns_404(client):
    token = await _register(client)
    response = await client.get(
        f"/api/v1/documents/{uuid.uuid4()}/status", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404
