"""TASK-105 kabul kriterleri testleri."""
import uuid

import pytest
from sqlalchemy import select

from app.db.session import async_session_maker
from app.models.user import User


def _unique_email() -> str:
    return f"test_{uuid.uuid4().hex[:10]}@example.com"


@pytest.mark.asyncio
async def test_register_creates_user_and_returns_tokens(client):
    email = _unique_email()
    response = await client.post("/api/v1/auth/register", json={"email": email, "password": "password123"})

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == email
    assert body["access_token"]
    assert body["refresh_token"]
    assert body["token_type"] == "bearer"
    assert body["expires_in"] == 3600


@pytest.mark.asyncio
async def test_register_duplicate_email_returns_409(client):
    email = _unique_email()
    await client.post("/api/v1/auth/register", json={"email": email, "password": "password123"})

    response = await client.post("/api/v1/auth/register", json={"email": email, "password": "password123"})

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "CONFLICT"


@pytest.mark.asyncio
async def test_register_short_password_returns_422(client):
    response = await client.post(
        "/api/v1/auth/register", json={"email": _unique_email(), "password": "short"}
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_login_wrong_credentials_returns_401(client):
    email = _unique_email()
    await client.post("/api/v1/auth/register", json={"email": email, "password": "password123"})

    response = await client.post("/api/v1/auth/login", json={"email": email, "password": "wrong-password"})

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


@pytest.mark.asyncio
async def test_login_success_returns_tokens(client):
    email = _unique_email()
    await client.post("/api/v1/auth/register", json={"email": email, "password": "password123"})

    response = await client.post("/api/v1/auth/login", json={"email": email, "password": "password123"})

    assert response.status_code == 200
    assert response.json()["access_token"]


@pytest.mark.asyncio
async def test_refresh_returns_new_access_token(client):
    email = _unique_email()
    register_response = await client.post(
        "/api/v1/auth/register", json={"email": email, "password": "password123"}
    )
    refresh_token = register_response.json()["refresh_token"]

    response = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})

    assert response.status_code == 200
    body = response.json()
    assert body["access_token"]
    assert body["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_refresh_invalid_token_returns_401(client):
    response = await client.post("/api/v1/auth/refresh", json={"refresh_token": "not-a-valid-token"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_password_is_bcrypt_hashed(client):
    email = _unique_email()
    await client.post("/api/v1/auth/register", json={"email": email, "password": "password123"})

    async with async_session_maker() as db:
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one()
        assert user.password_hash.startswith("$2b$")
        assert user.password_hash != "password123"


@pytest.mark.asyncio
async def test_profile_requires_auth(client):
    response = await client.get("/api/v1/profile")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_profile_with_token_returns_profile(client):
    email = _unique_email()
    register_response = await client.post(
        "/api/v1/auth/register", json={"email": email, "password": "password123"}
    )
    token = register_response.json()["access_token"]

    response = await client.get("/api/v1/profile", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json()["email"] == email
