import pytest
from httpx import AsyncClient
from sqlalchemy import select
from app.db.models import User, Account, Transaction


@pytest.mark.asyncio
async def test_create_transaction(authorized_client, test_account, db_session):
    payload = {
        "account_id": test_account.id,
        "amount": 5000,
        "type": "DEBIT",
        "description": "Test transaction",
    }
    resp = await authorized_client.post("/api/v1/transactions", json=payload)
    assert resp.status_code == 201

    print(resp.json())

    data = resp.json()
    assert data["account_id"] == test_account.id
    assert data["amount"] == 5000
    assert data["type"] == "DEBIT"
    assert data["description"] == "Test transaction"


    # Validate persistence in DB
    result = await db_session.execute(select(Transaction).where(Transaction.account_id == test_account.id))
    tx = result.scalar_one()
    assert tx.amount == 5000
    assert tx.description == "Test transaction"


@pytest.mark.asyncio
async def test_create_transaction_invalid_account(authorized_client: AsyncClient):
    # Try to create a transaction for an account that doesn't belong to the user
    payload = {
        "account_id": 99999,  # non-existent account
        "amount": 1000,
        "type": "CREDIT",
        "description": "Invalid account test",
    }

    resp = await authorized_client.post("/api/v1/transactions", json=payload)
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Account not found"
