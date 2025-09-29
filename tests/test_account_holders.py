import pytest
from httpx import AsyncClient
from sqlalchemy import select
from app.db.models import Account, AccountHolder, User


@pytest.mark.asyncio
async def test_create_account_holder(authorized_client: AsyncClient, db_session):
    # Get the authorized user from DB
    result = await db_session.execute(select(User).limit(1))
    user = result.scalar_one()

    # Create account owned by test user
    acc = Account(user_id=user.id, name="Test Account", currency="USD")
    db_session.add(acc)
    await db_session.commit()
    await db_session.refresh(acc)

    payload = {
        "user_id": user.id,
        "account_id": acc.id,
        "holder_type": "Primary"
    }

    resp = await authorized_client.post("/api/v1/account-holders", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["holder_type"] == "Primary"
    assert data["account_id"] == acc.id

    # Verify DB
    holder = await db_session.get(AccountHolder, data["id"])
    assert holder is not None


@pytest.mark.asyncio
async def test_list_account_holders(authorized_client: AsyncClient):
    resp = await authorized_client.get("/api/v1/account-holders")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
