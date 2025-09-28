import pytest
from httpx import AsyncClient
from app.main import app

@pytest.fixture
async def authorized_client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        # mock auth header if needed
        client.headers.update({"Authorization": "Bearer testtoken"})
        yield client
