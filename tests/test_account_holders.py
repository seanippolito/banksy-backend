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

@pytest.mark.asyncio
async def test_add_holder(authorized_client: AsyncClient, test_account):
    print(f"test_account: {test_account.id}")

    resp = await authorized_client.post(
        f"/api/v1/account-holders/{test_account.id}/holders",
        json={"user_id": test_account.user_id, "account_id": test_account.id, "holder_type": "PRIMARY"},
    )
    print(resp.json())
    assert resp.status_code == 200
    data = resp.json()
    assert data["account_id"] == test_account.id
    assert data["user_id"] == test_account.user_id


@pytest.mark.asyncio
async def test_list_holders(authorized_client: AsyncClient, test_account):
    resp = await authorized_client.get(f"/api/v1/account-holders/{test_account.id}/holders")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_remove_holder(authorized_client: AsyncClient, db_session, test_account):
    # Add a holder first
    resp = await authorized_client.post(
        f"/api/v1/account-holders/{test_account.id}/holders",
        json={"user_id": test_account.user_id, "account_id": test_account.id, "holder_type": "JOINT"},
    )
    holder = resp.json()

    print(f"holder: {holder}")
    # Now remove it
    resp = await authorized_client.delete(f"/api/v1/account-holders/holders/{holder['id']}")
    assert resp.status_code == 200
    assert resp.json()["ok"] is True
