"""TASK-106 / TASK-302 kabul kriterleri: dosya validasyonu + sahiplik kontrolü (403)."""
import io
import os
import uuid

import pytest
from sqlalchemy import select

from app.db.session import async_session_maker
from app.models.cv_draft import CVDraft
from app.models.document_embedding import EMBEDDING_DIM, DocumentEmbedding
from app.models.uploaded_document import UploadedDocument


async def _register(client) -> tuple[str, str]:
    email = f"doc_{uuid.uuid4().hex[:10]}@example.com"
    response = await client.post("/api/v1/auth/register", json={"email": email, "password": "password123"})
    body = response.json()
    return body["access_token"], body["user_id"]


async def _register_token(client) -> str:
    token, _ = await _register(client)
    return token


@pytest.mark.asyncio
async def test_upload_rejects_unsupported_file_type(client):
    token = await _register_token(client)
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
    token = await _register_token(client)
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
    token = await _register_token(client)
    response = await client.post(
        "/api/v1/documents/upload",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("test.pdf", io.BytesIO(b"%PDF-1.4\n%%EOF"), "application/pdf")},
        data={"document_type": "resume"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_other_users_document_status_returns_403(client):
    token_a = await _register_token(client)
    token_b = await _register_token(client)

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
    token = await _register_token(client)
    response = await client.get(
        f"/api/v1/documents/{uuid.uuid4()}/status", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_own_document_returns_204_and_removes_it(client):
    token = await _register_token(client)
    upload_response = await client.post(
        "/api/v1/documents/upload",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("test.pdf", io.BytesIO(b"%PDF-1.4\n%%EOF"), "application/pdf")},
        data={"document_type": "cv"},
    )
    doc_id = upload_response.json()["document_id"]

    async with async_session_maker() as db:
        document = await db.get(UploadedDocument, uuid.UUID(doc_id))
        file_path = document.file_path
    assert file_path is not None
    assert os.path.exists(file_path)

    delete_response = await client.delete(
        f"/api/v1/documents/{doc_id}", headers={"Authorization": f"Bearer {token}"}
    )
    assert delete_response.status_code == 204
    assert delete_response.content == b""

    # Disk temizliği doğrulanır
    assert not os.path.exists(file_path)

    # Belge artık DB'de yok -> status polling 404 dönmeli
    status_response = await client.get(
        f"/api/v1/documents/{doc_id}/status", headers={"Authorization": f"Bearer {token}"}
    )
    assert status_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_other_users_document_returns_403(client):
    token_a = await _register_token(client)
    token_b = await _register_token(client)

    upload_response = await client.post(
        "/api/v1/documents/upload",
        headers={"Authorization": f"Bearer {token_a}"},
        files={"file": ("test.pdf", io.BytesIO(b"%PDF-1.4\n%%EOF"), "application/pdf")},
        data={"document_type": "cv"},
    )
    doc_id = upload_response.json()["document_id"]

    response = await client.delete(
        f"/api/v1/documents/{doc_id}", headers={"Authorization": f"Bearer {token_b}"}
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "FORBIDDEN"

    # Belge hala mevcut olmalı (silinmemiş)
    async with async_session_maker() as db:
        document = await db.get(UploadedDocument, uuid.UUID(doc_id))
        assert document is not None


@pytest.mark.asyncio
async def test_delete_nonexistent_document_returns_404(client):
    token = await _register_token(client)
    response = await client.delete(
        f"/api/v1/documents/{uuid.uuid4()}", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "DOCUMENT_NOT_FOUND"


@pytest.mark.asyncio
async def test_delete_document_cascades_embeddings_and_nullifies_cv_draft_reference(client):
    token, user_id = await _register(client)
    upload_response = await client.post(
        "/api/v1/documents/upload",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("test.pdf", io.BytesIO(b"%PDF-1.4\n%%EOF"), "application/pdf")},
        data={"document_type": "cv"},
    )
    doc_id = uuid.UUID(upload_response.json()["document_id"])

    # RAG index kaydı ve draft referansı elle kuruluyor (Sprint 1'de gerçek pipeline yok)
    async with async_session_maker() as db:
        embedding = DocumentEmbedding(
            document_id=doc_id,
            content="test chunk",
            embedding=[0.0] * EMBEDDING_DIM,
            doc_metadata={"source_label": "user_document"},
        )
        draft = CVDraft(
            user_id=uuid.UUID(user_id),
            uploaded_document_id=doc_id,
            form_data={},
        )
        db.add_all([embedding, draft])
        await db.commit()
        await db.refresh(draft)
        draft_id = draft.id

    delete_response = await client.delete(
        f"/api/v1/documents/{doc_id}", headers={"Authorization": f"Bearer {token}"}
    )
    assert delete_response.status_code == 204

    async with async_session_maker() as db:
        remaining_embeddings = (
            await db.execute(select(DocumentEmbedding).where(DocumentEmbedding.document_id == doc_id))
        ).scalars().all()
        assert remaining_embeddings == []

        refreshed_draft = await db.get(CVDraft, draft_id)
        assert refreshed_draft is not None
        assert refreshed_draft.uploaded_document_id is None
