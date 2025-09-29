import pytest
from fastapi import Depends, FastAPI
from httpx import AsyncClient

from app.api import deps
from app.db.models import User

@pytest.mark.asyncio
async def test_get_current_user_unauthorized(client: AsyncClient):
    resp = await client.get("/api/v1/users/me")  # no auth header
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_optional_none(client: AsyncClient):
    app = FastAPI()

    @app.get("/optional")
    async def optional_route(user=Depends(deps.get_current_user_optional)):
        return {"user": user}

    test_client = AsyncClient(app=app, base_url="http://test")
    resp = await test_client.get("/optional")
    assert resp.status_code == 200
    assert resp.json() == {"user": None}


@pytest.mark.asyncio
async def test_get_current_user_upserts(db_session, authorized_client: AsyncClient):
    # Hitting /me should insert our test user
    resp = await authorized_client.get("/api/v1/users/me")
    assert resp.status_code == 200
    data = resp.json()
    assert "email" in data

    user = await db_session.get(User, data["id"])
    assert user is not None
    assert user.email == data["email"]
