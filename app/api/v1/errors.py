from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.db.models import ApplicationLogger
from app.api.deps import get_current_user
from app.schemas.error_log import ErrorLogRead

router = APIRouter(prefix="/api/v1/errors", tags=["errors"])

@router.get("", response_model=list[ErrorLogRead])
async def list_errors(
        db: AsyncSession = Depends(get_db),
        user=Depends(get_current_user),  # TODO: restrict to admin role
):
    print("return errors enter")
    res = await db.execute(select(ApplicationLogger).order_by(ApplicationLogger.created_at.desc()))
    print("return errors exit")
    return res.scalars().all()
