import os
import pytest
import pytest_asyncio
import asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import delete, select

from app.main import app
from app.db.models import Base  # flat models.py with Base defined
from app.db.session import AsyncSessionLocal
from app.db.models import User, Account
# -------------------------------------------------------------------
# DATABASE FIXTURE
# -------------------------------------------------------------------

DATABASE_URL = "sqlite+aiosqlite:///:memory:"
TEST_CLERK_ID = "test_clerk_id"

engine_test = create_async_engine(DATABASE_URL, future=True, echo=False)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine_test, class_=AsyncSession
)

@pytest_asyncio.fixture(scope="function", autouse=True)
async def db_session():
    """Create a new database schema for a test, then drop it."""
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.rollback()
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# -------------------------------------------------------------------
# CLIENT FIXTURE
# -------------------------------------------------------------------

@pytest_asyncio.fixture
async def client(db_session):
    """HTTPX client with DB session injected into FastAPI app deps."""
    async def _override_get_db():
        yield db_session

    app.dependency_overrides.clear()
    from app.api.deps import get_db
    app.dependency_overrides[get_db] = _override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

# -------------------------------------------------------------------
# AUTHORIZED CLIENT FIXTURE
# -------------------------------------------------------------------

@pytest_asyncio.fixture
async def authorized_client(db_session):

    # Delete any previous test user
    await db_session.execute(delete(User).where(User.clerk_user_id == TEST_CLERK_ID))
    await db_session.commit()

    # Create a fake user
    user = User(
        clerk_user_id=TEST_CLERK_ID,
        email="test@example.com",
        first_name="Test",
        last_name="User"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Dependency override to return this user
    async def override_get_current_user():
        return user

    app.dependency_overrides.clear()
    app.dependency_overrides[__import__('app.api.deps').api.deps.get_current_user] = override_get_current_user

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest_asyncio.fixture
async def test_account(db_session):
    """Create a test account tied to the authorized test user."""
    # Grab the first test user from DB (should exist from authorized_client fixture)
    result = await db_session.execute(select(User).where(User.clerk_user_id == TEST_CLERK_ID).limit(1))
    user = result.scalar_one()

    print(f"Creating test account for user_id={user.clerk_user_id}")
    account = Account(user_id=user.id, name="Fixture Account", currency="USD")
    db_session.add(account)
    await db_session.commit()
    await db_session.refresh(account)

    return account