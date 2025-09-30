from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.api.deps import get_current_user
from app.db.session import get_db
from app.db.models import AccountHolder, User, Account
from app.schemas.account_holder import AccountHolderCreate, AccountHolderRead

router = APIRouter(prefix="/api/v1/account-holders", tags=["account-holders"])


@router.get("", response_model=list[AccountHolderRead])
async def list_account_holders(
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(AccountHolder).join(Account).where(Account.user_id == user.id)
    )
    return result.scalars().all()


@router.post("", response_model=AccountHolderRead, status_code=201)
async def create_account_holder(
        payload: AccountHolderCreate,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
):
    # Validate account ownership
    account = await db.scalar(
        select(Account).where(Account.id == payload.account_id, Account.user_id == user.id)
    )
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    ah = AccountHolder(
        user_id=payload.user_id,
        account_id=payload.account_id,
        holder_type=payload.holder_type,
    )
    db.add(ah)
    await db.flush()
    await db.commit()
    await db.refresh(ah)
    return ah

# List all holders for an account
@router.get("/{account_id}/holders", response_model=list[AccountHolderRead])
async def list_holders(
        account_id: int,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
):
    # Ensure user owns account
    acc = await db.get(Account, account_id)
    if not acc or acc.user_id != user.id:
        raise HTTPException(status_code=404, detail="Account not found")

    res = await db.execute(
        select(AccountHolder).where(AccountHolder.account_id == account_id)
    )
    return res.scalars().all()


# Add a new holder
@router.post("/{account_id}/holders", response_model=AccountHolderRead)
async def add_holder(
        account_id: int,
        payload: AccountHolderCreate,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
):
    print(f"account")
    # Ensure primary user owns account
    acc = await db.get(Account, account_id)
    print(f"account {acc.user_id}")
    if not acc or acc.user_id != user.id:
        raise HTTPException(status_code=404, detail="Account not found")

    holder = AccountHolder(account_id=account_id, user_id=payload.user_id, holder_type=payload.holder_type)
    db.add(holder)
    await db.commit()
    await db.refresh(holder)
    return holder


# Remove a holder
@router.delete("/holders/{holder_id}")
async def remove_holder(
        holder_id: int,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
):
    holder = await db.get(AccountHolder, holder_id)
    if not holder:
        raise HTTPException(status_code=404, detail="Holder not found")

    acc = await db.get(Account, holder.account_id)
    if not acc or acc.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to remove holder")

    await db.delete(holder)
    await db.commit()
    return {"ok": True}