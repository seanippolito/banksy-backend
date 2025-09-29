import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_me_unauthorized(client: AsyncClient):
    resp = await client.get("/api/v1/me")
    assert resp.status_code == 401  # no auth header

@pytest.mark.asyncio
async def test_me_authorized(authorized_client: AsyncClient):
    resp = await authorized_client.get("/api/v1/me")
    assert resp.status_code == 200
    data = resp.json()
    assert "email" in data
    assert "clerk_user_id" in data
