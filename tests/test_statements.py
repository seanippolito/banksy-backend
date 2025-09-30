import pytest
from httpx import AsyncClient
from sqlalchemy import select, text
from datetime import date, timedelta, datetime
from app.db.models import User, Account, Transaction


@pytest.mark.asyncio
async def test_generate_statements_balance(authorized_client: AsyncClient, db_session):
    # Fetch authorized user
    result = await db_session.execute(select(User).limit(1))
    user = result.scalar_one()

    # Create account for this user
    account = Account(user_id=user.id, name="Checking", currency="USD")
    db_session.add(account)
    await db_session.commit()
    await db_session.refresh(account)

    now = datetime.utcnow()
    # Create CREDIT and DEBIT transactions (positive amounts only)
    tx1 = Transaction(account_id=account.id, amount=1000, type="CREDIT", description="Deposit", created_at=now)
    tx2 = Transaction(account_id=account.id, amount=200, type="DEBIT", description="Withdrawal", created_at=now)
    db_session.add_all([tx1, tx2])
    await db_session.commit()

    # Define statement range covering both txs
    today = date.today()
    payload = {
        "start_date": str(today - timedelta(days=1)),
        "end_date": str(today + timedelta(days=1)),
    }

    resp = await authorized_client.post("/api/v1/statements", json=payload)
    assert resp.status_code == 200
    data = resp.json()

    # Validate structure
    assert isinstance(data, list)
    assert len(data) == 1
    statement = data[0]

    assert statement["account_id"] == account.id
    assert statement["balance"] == 800  # 1000 CREDIT - 200 DEBIT
    assert len(statement["transactions"]) == 2

    # Transaction checks
    descriptions = [tx["description"] for tx in statement["transactions"]]
    assert "Deposit" in descriptions
    assert "Withdrawal" in descriptions

    types = {tx["type"] for tx in statement["transactions"]}
    assert "CREDIT" in types
    assert "DEBIT" in types


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
