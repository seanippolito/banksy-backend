from fastapi import APIRouter, Depends
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from pathlib import Path
import os

from app.db.session import get_db, engine
from app.db.models import User
from app.schemas.user import UserRead
from app.core.config import settings

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])

@router.get("/dbinfo")
async def dbinfo():
    # Try to resolve local file path from DATABASE_URL (only for sqlite)
    url = settings.DATABASE_URL
    local_file = None
    if url.startswith("sqlite"):
        # strip driver and leading scheme
        # sqlite+aiosqlite:////absolute/path OR sqlite+aiosqlite:///relative.db
        path = url.split(":///")[-1]
        local_file = Path(path)
        exists = local_file.exists()
        size = local_file.stat().st_size if exists else 0
    else:
        exists = None
        size = None

    # List tables via pragma (SQLite) or generic reflection fallback
    tables = []
    try:
        async with engine.begin() as conn:
            res = await conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            tables = [r[0] for r in res.fetchall()]
    except Exception as e:
        tables = [f"(error listing tables: {e!r})"]

    return {
        "database_url": url,
        "resolved_path": str(local_file) if local_file else None,
        "exists": exists,
        "size_bytes": size,
        "tables": tables,
    }

@router.get("/users", response_model=list[UserRead])
async def list_users(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(User).order_by(User.id.asc()))
    return res.scalars().all()
