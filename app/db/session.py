from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

_engine = None
_SessionLocal = None


def get_engine():
    """
    Lazily initialize and return the SQLAlchemy engine.
    Uses the current settings.DATABASE_URL (so tests can override it).
    """
    global _engine
    if _engine is None:
        _engine = create_async_engine(
            settings.DATABASE_URL,
            future=True,
            echo=False,   # set True for debugging
        )
    return _engine


def get_sessionmaker():
    """
    Lazily initialize and return the sessionmaker bound to the engine.
    """
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(
            bind=get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
        )
    return _SessionLocal


# Default dependency for FastAPI
async def get_db():
    """
    Yields a DB session. Safe to override in tests.
    """
    SessionLocal = get_sessionmaker()
    async with SessionLocal() as session:
        yield session
