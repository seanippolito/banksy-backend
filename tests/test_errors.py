import pytest
from sqlalchemy import select
from app.db.models import ApplicationLogger
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_errors_authenticated(authorized_client, db_session):
    # Insert a fake error
    log = ApplicationLogger(
        user_id=None,
        error_code="500",
        message="Unit test error",
        location="test"
    )
    db_session.add(log)
    await db_session.commit()

    resp = await authorized_client.get("/api/v1/errors")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert any("Unit test error" in e["message"] for e in data)

@pytest.mark.asyncio
async def test_error_logger_pass_through(client: AsyncClient):
    resp = await client.get("/api/v1/health")
    assert resp.status_code == 200
    # Should not create any ApplicationLogger entries