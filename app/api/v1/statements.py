from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.api.deps import get_current_user
from app.db.session import get_db
from app.db.models import Account, Transaction, User
from app.schemas.statement import StatementRequest, StatementResponse, StatementTransaction

router = APIRouter(prefix="/api/v1/statements", tags=["statements"])

@router.post("", response_model=list[StatementResponse])
async def generate_statements(
        payload: StatementRequest,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
):
    accounts = await db.execute(select(Account).where(Account.user_id == user.id))
    accounts = accounts.scalars().all()

    if not accounts:
        raise HTTPException(status_code=404, detail="No accounts found for user")

    results = []
    for acc in accounts:
        txs = await db.execute(
            select(Transaction).where(
                and_(
                    Transaction.account_id == acc.id,
                    Transaction.created_at >= payload.start_date,
                    Transaction.created_at <= payload.end_date
                )
            ).order_by(Transaction.created_at.asc())
        )
        txs = txs.scalars().all()
        balance = sum(tx.amount for tx in txs)

        results.append(
            StatementResponse(
                account_id=str(acc.id),
                balance=balance,
                transactions=[
                    StatementTransaction(
                        date=tx.created_at.isoformat(),
                        description=tx.description,
                        amount=tx.amount,
                        type=tx.type,
                    ) for tx in txs
                ]
            )
        )
    return results
