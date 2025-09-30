from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.api.deps import get_current_user
from app.db.session import get_db
from app.db.models import Card, User, Account
from app.schemas.card import CardCreate, CardRead
import random

router = APIRouter(prefix="/api/v1/cards", tags=["cards"])


@router.get("", response_model=list[CardRead])
async def list_cards(
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Card).join(Account).where(Account.user_id == user.id)
    )
    return result.scalars().all()


@router.post("", response_model=CardRead, status_code=201)
async def create_card(
        payload: CardCreate,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
):
    # Validate account ownership
    account = await db.scalar(
        select(Account).where(Account.id == payload.account_id, Account.user_id == user.id)
    )
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    card = Card(
        account_id=payload.account_id,
        card_number_last4=payload.card_number_last4,
        card_type=payload.card_type,
        expiration_month=payload.expiration_month,
        expiration_year=payload.expiration_year,
        status=payload.status,
    )
    db.add(card)
    await db.flush()
    await db.commit()
    await db.refresh(card)
    return card

@router.post("/ship/{account_id}", response_model=CardRead)
async def ship_card(
        account_id: int,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
):
    # Verify account belongs to user
    res = await db.execute(
        select(Account).where(Account.id == account_id, Account.user_id == user.id)
    )
    account = res.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    last_4 = f"{random.randint(0, 9999):04}"

    # Create card
    card = Card(
        account_id=account.id,
        card_number_last4=last_4,  # mock/test value
        card_type="CREDIT",
        expiration_month=12,
        expiration_year=2030,
        status="Active",
    )
    db.add(card)
    await db.commit()
    await db.refresh(card)
    return card