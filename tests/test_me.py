import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_me_endpoint(authorized_client: AsyncClient):
    resp = await authorized_client.get("/api/v1/me")
    assert resp.status_code == 200
    data = resp.json()
    assert "id" in data
    assert "email" in data
