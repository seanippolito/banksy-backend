
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from app.main import app
from app.db.models import Base  # flat models.py with Base defined
from app.db.models import User, Account
from app.db.session import get_engine, get_sessionmaker, get_db


# -------------------------------------------------------------------
# DATABASE FIXTURE
# -------------------------------------------------------------------

TEST_CLERK_ID = "test_clerk_id"
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# -----------------------------------------------------------------------------
# Database setup/teardown
# -----------------------------------------------------------------------------

@pytest_asyncio.fixture(scope="session", autouse=True)
def override_settings():
    # Swap out settings.DATABASE_URL before engine is created
    from app.core import config
    config.settings.DATABASE_URL = TEST_DATABASE_URL

    # Reset engine/sessionmaker
    import app.db.session as db_session
    db_session._engine = create_async_engine(TEST_DATABASE_URL, future=True)
    db_session._SessionLocal = sessionmaker(
        db_session._engine, class_=AsyncSession, expire_on_commit=False
    )
    yield

@pytest_asyncio.fixture(scope="session", autouse=True)
async def prepare_database():
    """Create all tables in the in-memory test DB at the start of the session."""
    async with get_engine().begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

@pytest_asyncio.fixture()
async def db_session():
    """Create a new database schema for a test, then drop it."""
    SessionLocal = get_sessionmaker()
    async with SessionLocal() as session:
        yield session # cleanup

@pytest_asyncio.fixture(autouse=True)
async def clean_tables(db_session):
    for table in reversed(Base.metadata.sorted_tables):
        await db_session.execute(table.delete())
    await db_session.commit()

@pytest_asyncio.fixture(autouse=True)
def reset_overrides():
    app.dependency_overrides = {}
    yield
    app.dependency_overrides = {}

# -------------------------------------------------------------------
# CLIENT FIXTURE
# -------------------------------------------------------------------

@pytest_asyncio.fixture
async def client(db_session):
    # Override get_db with our test session
    async def _get_test_db():
        yield db_session

    app.dependency_overrides[get_db] = _get_test_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c

# -------------------------------------------------------------------
# AUTHORIZED CLIENT FIXTURE
# -------------------------------------------------------------------

@pytest_asyncio.fixture
async def authorized_client(db_session):

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
        # Pretend Clerk issued a JWT for this user
        ac.headers.update({"Authorization": f"Bearer mock-jwt-for-{TEST_CLERK_ID}"})
        yield ac

@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession):
    """Create and return a test user in the DB."""
    user = User(
        clerk_user_id="clerk_test_user_fixture",
        email="fixtureuser@example.com",
        first_name="Fixture",
        last_name="User",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest_asyncio.fixture
async def test_account(db_session):
    """Create a test account tied to the authorized test user."""
    # Grab the first test user from DB (should exist from authorized_client fixture)
    result = await db_session.execute(select(User).where(User.clerk_user_id == TEST_CLERK_ID))
    user = result.scalar_one()

    account = Account(user_id=user.id, name="Fixture Account", currency="USD")
    db_session.add(account)
    await db_session.commit()
    await db_session.refresh(account)

    return account