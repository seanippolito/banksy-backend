from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.db.session import get_engine
from app.db.models import Base
from app.core.config import settings
from app.api.v1.users import router as users_router
from app.api.v1.admin import router as admin_router  # <-- will add this file below
from app.api.v1.accounts import router as accounts_router
from app.api.v1.transactions import router as transactions_router
from app.api.v1.account_holders import router as account_holders_router
from app.api.v1.cards import router as cards_router
from app.api.v1.money_transfers import router as money_transfers_router
from app.api.v1.statements import router as statements_router
from app.api.v1.errors import router as errors_router
from app.middleware.error_logger import error_logger_middleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code
    print("App starting up...")
    # Auto-create tables for dev/SQLite. For Postgres prod, use Alembic.
    async with get_engine().begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        try:
            # Log tables present (SQLite)
            res = await conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            tables = [r[0] for r in res.fetchall()]
            print("[startup] DB:", settings.DATABASE_URL)
            print("[startup] Tables:", tables)
        except Exception as e:
            print("[startup] Could not list tables:", repr(e))
    print("DB ready at", settings.DATABASE_URL)
    print("Banksy Backend available at http://127.0.0.1:8000 (mapped from 0.0.0.0 inside Docker), health check is available at http://127.0.0.1:8000/api/v1/health")
    yield
    # Shutdown code
    print("App shutting down...")

app = FastAPI(
    title="Banksy API",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS (allow the frontend origin & auth header)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Requested-With"],
)

app.middleware("http")(error_logger_middleware)

app.include_router(users_router)
app.include_router(admin_router)
app.include_router(accounts_router)
app.include_router(transactions_router)
app.include_router(account_holders_router)
app.include_router(cards_router)
app.include_router(money_transfers_router)
app.include_router(statements_router)
app.include_router(errors_router)

@app.get("/api/v1/health")
async def health():
    return {"status": "ok", "service": "Banksy Backend Test Me ✅"}
