import pytest
from httpx import AsyncClient
from sqlalchemy import select
from app.db.models import Account, Card, User


@pytest.mark.asyncio
async def test_create_card(authorized_client: AsyncClient, db_session):
    # Get the authorized user from DB
    result = await db_session.execute(select(User).limit(1))
    user = result.scalar_one()

    acc = Account(user_id=user.id, name="Card Account", currency="USD")
    db_session.add(acc)
    await db_session.commit()
    await db_session.refresh(acc)

    payload = {
        "account_id": acc.id,
        "card_number_last4": "1234",
        "card_type": "Debit",
        "expiration_month": 12,
        "expiration_year": 2030,
        "status": "Active",
    }

    resp = await authorized_client.post("/api/v1/cards", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["card_number_last4"] == "1234"
    assert data["account_id"] == acc.id

    # Verify DB
    card = await db_session.get(Card, data["id"])
    assert card is not None


@pytest.mark.asyncio
async def test_list_cards(authorized_client: AsyncClient):
    resp = await authorized_client.get("/api/v1/cards")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
