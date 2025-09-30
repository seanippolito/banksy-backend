from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.api.deps import get_current_user
from app.db.session import get_db
from app.db.models import Account, Transaction, User
from app.schemas.money_transfer import MoneyTransferCreate
from app.schemas.transaction import TransactionRead
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

    if not sender:
        raise HTTPException(status_code=404, detail="Sender account not found")

    # Validate recipient account exists
    recipient = await db.scalar(select(Account).where(Account.id == payload.recipient_account_id))
    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient account not found")

    transfer_id = str(uuid4())

    # Debit from sender
    debit = Transaction(
        account_id=sender.id,
        amount=payload.amount,
        type="DEBIT",
        description=payload.description or f"Transfer to {recipient.id}",
        transfer_id=transfer_id,
    )
    db.add(debit)


    # Credit to recipient
    credit = Transaction(
        account_id=recipient.id,
        amount=payload.amount,
        type="CREDIT",
        description=payload.description or f"Transfer from {sender.id}",
        transfer_id=transfer_id,
    )
    db.add(credit)

    await db.commit()
    return {"transfer_id": transfer_id, "status": "success"}

@router.get("/{transfer_id}", response_model=list[TransactionRead])
async def get_transfer(
        transfer_id: str,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
):
    # Only return transactions owned by this user
    res = await db.execute(
        select(Transaction).where(
            Transaction.transfer_id == transfer_id,
            Transaction.account.has(user_id=user.id),
            )
    )
    txs = res.scalars().all()
    if not txs:
        raise HTTPException(status_code=404, detail="Transfer not found")
    return txs