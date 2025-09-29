from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user
from app.db.session import get_db
from app.db.models import Account, User
from app.schemas.account import AccountCreate, AccountRead

router = APIRouter(prefix="/api/v1/accounts", tags=["accounts"])

@router.get("", response_model=list[AccountRead])
async def list_accounts(
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
):
    res = await db.execute(select(Account).where(Account.user_id == user.id).order_by(Account.id.asc()))
    return res.scalars().all()

@router.post("", response_model=AccountRead, status_code=201)
async def create_account(
        payload: AccountCreate,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
):
    acc = Account(user_id=user.id, name=payload.name, currency=payload.currency)
    db.add(acc)
    await db.flush()
    await db.commit()
    await db.refresh(acc)
    return acc

@router.get("/{account_id}", response_model=AccountRead)
async def get_account_by_id(
        account_id: int,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
):
    res = await db.execute(
        select(Account).where(Account.id == account_id, Account.user_id == user.id)
    )
    account = res.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account