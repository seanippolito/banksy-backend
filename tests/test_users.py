import pytest
from httpx import AsyncClient
from sqlalchemy import select
from app.db.models import User
from sqlalchemy import delete

@pytest.mark.asyncio
async def test_list_users(authorized_client: AsyncClient, db_session):
    # Seed a user
    user = User(
        clerk_user_id="clerk_test_user_123",
        email="testuser@example.com",
        first_name="Test",
        last_name="User",
    )
    db_session.add(user)
    await db_session.commit()

    # Call API
    resp = await authorized_client.get("/api/v1/users")
    assert resp.status_code == 200
    data = resp.json()
    assert any(u["email"] == "testuser@example.com" for u in data)


@pytest.mark.asyncio
async def test_get_user_by_id(authorized_client: AsyncClient, db_session):
    # Get a user from DB
    result = await db_session.execute(select(User).limit(1))
    user = result.scalar_one()

    resp = await authorized_client.get(f"/api/v1/users/{user.id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == user.email
