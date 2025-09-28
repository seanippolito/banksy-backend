from logging.config import fileConfig
import sys
from pathlib import Path

# Ensure the backend root is on sys.path so "import app.*" works.
# env.py lives at: apps/backend/app/db/alembic/env.py
BACKEND_ROOT = Path(__file__).resolve().parents[3]  # -> apps/backend
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from sqlalchemy import engine_from_config, pool
from alembic import context

# ---- App imports to get models & settings
from app.core.config import settings
from app.db.models import Base

# Alembic Config object
config = context.config

# Use the app's DB URL so Alembic matches runtime
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL.replace("+aiosqlite", ""))  # Alembic uses sync driver

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
