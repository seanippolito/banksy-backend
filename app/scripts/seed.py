import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_sessionmaker
from app.db.models import User, Account

async def main():
    SessionLocal = get_sessionmaker()
    async with SessionLocal() as db:  # type: AsyncSession
        # pick first user
        user = (await db.execute(select(User).order_by(User.id.asc()))).scalars().first()
        if not user:
            print("[seed] No users yet; sign in once via frontend to create your user.")
            return
        exists = (await db.execute(select(Account).where(Account.user_id == user.id))).scalars().first()
        if exists:
            print("[seed] Account already exists; skipping")
            return
        acc = Account(user_id=user.id, name="Primary Checking", currency="USD")
        db.add(acc)
        await db.commit()
        print(f"[seed] Created account id={acc.id} for user_id={user.id}")

if __name__ == "__main__":
    asyncio.run(main())
