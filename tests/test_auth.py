"""Тесты проверяющие корректность работы API."""

from httpx import AsyncClient
from sqlalchemy import select

from app.db.session import _ensure_engine
from app.models.user import User


async def test_register_returns_profile_without_password(client: AsyncClient) -> None:
    r = await client.post(
        "/api/v1/auth/register",
        json={"email": "u@example.com", "password": "secretpass1"},
    )
    assert r.status_code == 201
    data = r.json()
    assert data["email"] == "u@example.com"
    assert "password" not in data
    assert data["role"] == "free_user"
    assert data["id"] >= 1


async def test_register_duplicate_email_409(client: AsyncClient) -> None:
    body = {"email": "dup@example.com", "password": "secretpass1"}
    assert (await client.post("/api/v1/auth/register", json=body)).status_code == 201
    r2 = await client.post("/api/v1/auth/register", json=body)
    assert r2.status_code == 409


async def test_login_returns_tokens(client: AsyncClient) -> None:
    await client.post(
        "/api/v1/auth/register",
        json={"email": "login@example.com", "password": "mypassword1"},
    )
    r = await client.post(
        "/api/v1/auth/login",
        json={"email": "login@example.com", "password": "mypassword1"},
    )
    assert r.status_code == 200
    data = r.json()
    assert "access_token" in data and "refresh_token" in data
    assert data.get("token_type") == "bearer"


async def test_login_wrong_password_401(client: AsyncClient) -> None:
    await client.post(
        "/api/v1/auth/register",
        json={"email": "x@example.com", "password": "rightpassword1"},
    )
    r = await client.post(
        "/api/v1/auth/login",
        json={"email": "x@example.com", "password": "wrongpassword1"},
    )
    assert r.status_code == 401


async def test_me_without_token_401(client: AsyncClient) -> None:
    r = await client.get("/api/v1/users/me")
    assert r.status_code == 401


async def test_me_with_valid_token(client: AsyncClient) -> None:
    await client.post(
        "/api/v1/auth/register",
        json={"email": "me@example.com", "password": "secretpass1"},
    )
    login = await client.post(
        "/api/v1/auth/login",
        json={"email": "me@example.com", "password": "secretpass1"},
    )
    token = login.json()["access_token"]
    r = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    assert r.json()["email"] == "me@example.com"


async def test_refresh_returns_new_access(client: AsyncClient) -> None:
    await client.post(
        "/api/v1/auth/register",
        json={"email": "r@example.com", "password": "secretpass1"},
    )
    login = await client.post(
        "/api/v1/auth/login",
        json={"email": "r@example.com", "password": "secretpass1"},
    )
    refresh = login.json()["refresh_token"]
    r = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh},
    )
    assert r.status_code == 200
    new_access = r.json()["access_token"]
    assert new_access != login.json()["access_token"]


async def test_password_stored_hashed_not_plaintext(client: AsyncClient) -> None:
    plain = "mysecurepass1"
    await client.post(
        "/api/v1/auth/register",
        json={"email": "hash@example.com", "password": plain},
    )

    factory = _ensure_engine()
    async with factory() as session:
        result = await session.execute(select(User).where(User.email == "hash@example.com"))
        user = result.scalar_one()
        assert user.password_hash != plain
        assert user.password_hash.startswith("$2")
