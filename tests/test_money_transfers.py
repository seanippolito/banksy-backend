import pytest
from httpx import AsyncClient
from sqlalchemy import select
from app.db.models import User, Account, Transaction


@pytest.mark.asyncio
async def test_money_transfer_success(authorized_client: AsyncClient, db_session):
    # Fetch authorized user
    result = await db_session.execute(select(User).limit(1))
    user = result.scalar_one()

    # Create sender and recipient accounts
    sender = Account(user_id=user.id, name="Checking", currency="USD")
    recipient = Account(user_id=user.id, name="Savings", currency="USD")
    db_session.add_all([sender, recipient])
    await db_session.commit()
    await db_session.refresh(sender)
    await db_session.refresh(recipient)

    print(
        f"Sender: {sender.id} | Recipient: {recipient.id}")
    # Perform transfer
    resp = await authorized_client.post(
        "/api/v1/money-transfers",
        json={
            "sender_account_id": sender.id,
            "recipient_account_id": recipient.id,
            "amount": 500,
            "description": "Test Transfer"
        }
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "transfer_id" in data

    # Verify two transactions created
    txs = await db_session.execute(
        select(Transaction).where(Transaction.transfer_id == data["transfer_id"])
    )
    txs = txs.scalars().all()
    assert len(txs) == 2
    assert any(tx.amount == -500 for tx in txs)
    assert any(tx.amount == 500 for tx in txs)


@pytest.mark.asyncio
async def test_money_transfer_invalid_recipient(authorized_client: AsyncClient, db_session):
    result = await db_session.execute(select(User).limit(1))
    user = result.scalar_one()

    # Sender only
    sender = Account(user_id=user.id, name="Checking", currency="USD")
    db_session.add(sender)
    await db_session.commit()
    await db_session.refresh(sender)

    # Recipient doesn't exist
    resp = await authorized_client.post(
        "/api/v1/money-transfers",
        json={
            "sender_account_id": sender.id,
            "recipient_account_id": 999999,
            "amount": 500,
        }
    )
    assert resp.status_code == 404
