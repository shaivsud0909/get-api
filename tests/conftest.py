import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from app.authentication.utils import hash_password
from app.database.connection import AsyncSessionLocal
from app.database.models import User
from app.main import app


def _new_client() -> AsyncClient:
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


async def _login(client: AsyncClient, credentials: dict) -> None:
    resp = await client.post("/login", json=credentials)
    assert resp.status_code == 200, resp.text
    client.headers["Authorization"] = f"Bearer {resp.json()['access_token']}"


@pytest.fixture
async def client():
    """Unauthenticated client. Also runs the app lifespan, so user_client/admin_client depend on it."""
    async with app.router.lifespan_context(app):
        async with _new_client() as c:
            yield c


@pytest.fixture
async def user_client(client):
    """Client logged in as a fresh user. `user_client.user_id` holds the user's id."""
    credentials = {
        "email": f"test-user-{uuid.uuid4().hex[:10]}@example.com",
        "password": "UserPass123!",
    }
    async with _new_client() as c:
        resp = await c.post("/signup", json=credentials)
        assert resp.status_code == 200, resp.text
        c.user_id = resp.json()["id"]
        await _login(c, credentials)
        yield c


@pytest.fixture
async def admin_client(client):
    """Client logged in as a fresh admin (inserted directly, since /signup only creates users)."""
    credentials = {
        "email": f"test-admin-{uuid.uuid4().hex[:10]}@example.com",
        "password": "AdminPass123!",
    }
    async with AsyncSessionLocal() as db:
        db.add(
            User(
                email=credentials["email"],
                password_hash=hash_password(credentials["password"]),
                role="admin",
                is_active=True,
                is_verified=True,
            )
        )
        await db.commit()

    async with _new_client() as c:
        await _login(c, credentials)
        yield c
