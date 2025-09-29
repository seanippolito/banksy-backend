from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.api.deps import get_current_user
from app.db.session import get_db
from app.db.models import Account, Transaction, User
from app.schemas.money_transfer import MoneyTransferCreate
from uuid import uuid4

router = APIRouter(prefix="/api/v1/money-transfers", tags=["money_transfers"])

@router.post("")
async def create_money_transfer(
        payload: MoneyTransferCreate,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
):
    # Validate ownership of sender account
    sender = await db.scalar(select(Account).where(
        Account.id == payload.sender_account_id,
        Account.user_id == user.id
    ))

    print(f"Sender: {sender}")
    if not sender:
        raise HTTPException(status_code=404, detail="Sender account not found")

    # Validate recipient account exists
    recipient = await db.scalar(select(Account).where(Account.id == payload.recipient_account_id))
    print(f"Sender: {recipient}")
    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient account not found")

    transfer_id = str(uuid4())

    # Debit from sender
    debit = Transaction(
        account_id=sender.id,
        amount=-payload.amount,
        type="debit",
        description=payload.description or f"Transfer to {recipient.id}",
        transfer_id=transfer_id,
    )
    db.add(debit)

    # Credit to recipient
    credit = Transaction(
        account_id=recipient.id,
        amount=payload.amount,
        type="credit",
        description=payload.description or f"Transfer from {sender.id}",
        transfer_id=transfer_id,
    )
    db.add(credit)

    await db.commit()
    return {"transfer_id": transfer_id, "status": "success"}
