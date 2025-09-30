import pytest
from httpx import AsyncClient
from sqlalchemy import select, text
from datetime import date, timedelta
from app.db.models import User, Account, Transaction


@pytest.mark.asyncio
async def test_generate_statements(authorized_client: AsyncClient, db_session):
    result = await db_session.execute(select(User).limit(1))
    user = result.scalar_one()

    # Create account with transactions
    account = Account(user_id=user.id, name="Checking", currency="USD")
    db_session.add(account)
    await db_session.commit()
    await db_session.refresh(account)

    tx1 = Transaction(account_id=account.id, amount=1000, type="CREDIT", description="Deposit")
    tx2 = Transaction(account_id=account.id, amount=200, type="DEBIT", description="Withdrawal")
    db_session.add_all([tx1, tx2])
    await db_session.commit()

    today = date.today()
    resp = await authorized_client.post(
        "/api/v1/statements",
        json={"start_date": str(today - timedelta(days=1)), "end_date": str(today + timedelta(days=1))}
    )
    assert resp.status_code == 200
    data = resp.json()
    print(f"Data: {data}")
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["account_id"] == account.id
    assert data[0]["balance"] == 800
    assert len(data[0]["transactions"]) == 2


@pytest.mark.asyncio
async def test_generate_statements_no_accounts(authorized_client: AsyncClient, db_session):
    # Delete all accounts for authorized user
    result = await db_session.execute(select(User).limit(1))
    user = result.scalar_one()

    await db_session.execute(
        text(f"DELETE FROM accounts WHERE user_id = '{user.id}'")
    )
    await db_session.commit()

    today = date.today()
    resp = await authorized_client.post(
        "/api/v1/statements",
        json={"start_date": str(today - timedelta(days=1)), "end_date": str(today + timedelta(days=1))}
    )
    assert resp.status_code == 404
