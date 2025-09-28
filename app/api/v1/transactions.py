from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user
from app.db.session import get_db
from app.db.models import Account, Transaction, User
from app.schemas.transaction import TransactionRead

router = APIRouter(prefix="/api/v1/transactions", tags=["transactions"])

@router.get("", response_model=list[TransactionRead])
async def list_transactions(
        account_id: int = Query(...),
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
):
    # ensure account belongs to user
    owns = await db.scalar(select(Account.id).where(Account.id == account_id, Account.user_id == user.id))
    if not owns:
        raise HTTPException(status_code=404, detail="Account not found")
    res = await db.execute(select(Transaction).where(Transaction.account_id == account_id).order_by(Transaction.id.desc()))
    return res.scalars().all()
