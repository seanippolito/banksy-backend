import pytest
from httpx import AsyncClient
from sqlalchemy import select
from app.db.models import Account, User


@pytest.mark.asyncio
async def test_create_account(authorized_client: AsyncClient, db_session):
    # Get the authorized user from DB
    result = await db_session.execute(select(User).limit(1))
    user = result.scalar_one()

    # Create account payload
    payload = {
        "name": "Checking Account",
        "currency": "USD",
    }

    resp = await authorized_client.post("/api/v1/accounts", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == payload["name"]
    assert data["currency"] == payload["currency"]

    # Verify in DB
    db_account = await db_session.execute(
        select(Account).where(Account.id == data["id"])
    )
    account = db_account.scalar_one()
    assert account.user_id == user.id


@pytest.mark.asyncio
async def test_list_accounts(authorized_client: AsyncClient, db_session):
    # Seed an account
    result = await db_session.execute(select(User).limit(1))
    user = result.scalar_one()

    account = Account(name="Savings", currency="USD", user_id=user.id)
    db_session.add(account)
    await db_session.commit()

    resp = await authorized_client.get("/api/v1/accounts")
    assert resp.status_code == 200
    accounts = resp.json()
    assert any(a["name"] == "Savings" for a in accounts)


@pytest.mark.asyncio
async def test_get_account_by_id(authorized_client: AsyncClient, db_session):
    # Seed account
    result = await db_session.execute(select(User).limit(1))
    user = result.scalar_one()

    account = Account(name="Investment", currency="USD", user_id=user.id)
    db_session.add(account)
    await db_session.commit()
    await db_session.refresh(account)

    resp = await authorized_client.get(f"/api/v1/accounts/{account.id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == account.id
    assert data["name"] == "Investment"
