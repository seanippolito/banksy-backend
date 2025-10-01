# -------------------------------
# Stage 0: Base
# -------------------------------
FROM python:3.12-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_NO_INTERACTION=1 \
    # We'll create and pin our venv at /opt/venv and always use it
    VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:$PATH"
WORKDIR /app

# OS deps (add build tools later if you need compiled wheels)
RUN apt-get update -y && apt-get install -y --no-install-recommends \
    curl ca-certificates \
  && rm -rf /var/lib/apt/lists/*

# Create the virtualenv at a fixed path
RUN python -m venv /opt/venv

# Upgrade pip and install Poetry into the venv (so `poetry` is on PATH)
RUN /opt/venv/bin/pip install --upgrade pip && /opt/venv/bin/pip install "poetry>=1.8.3"

# -------------------------------
# Stage 1: Builder (prod deps)
# -------------------------------
FROM base AS builder-prod
# Copy only dependency manifests for caching
COPY apps/backend/pyproject.toml apps/backend/poetry.lock* /app/

# Configure Poetry to use the already-created venv at /opt/venv
RUN poetry config virtualenvs.create false

# Install ONLY main (prod) dependencies into /opt/venv
RUN poetry install --only main --no-root

# -------------------------------
# Stage 2: Runner (production)
# -------------------------------
FROM base AS runner
# Bring in the populated /opt/venv
COPY --from=builder-prod /opt/venv /opt/venv

# App code
COPY apps/backend/ /app/

# Add start script
COPY docker/start-backend.sh /start-backend.sh
RUN chmod +x /start-backend.sh

# Non-root user
RUN useradd -m appuser
USER appuser

EXPOSE 8000
# `uvicorn` now exists at /opt/venv/bin/uvicorn and is on PATH
# CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]

# In runner:
CMD ["/start-backend.sh", "prod"]

# -------------------------------
# Stage 3: Builder (dev deps)
# -------------------------------
FROM base AS builder-dev
COPY apps/backend/pyproject.toml apps/backend/poetry.lock* /app/
RUN poetry config virtualenvs.create false
# Install main + dev deps into /opt/venv for hot reload / tooling
RUN poetry install --no-root

# -------------------------------
# Stage 4: Dev (hot reload)
# -------------------------------
FROM base AS dev
# Bring in the /opt/venv with dev deps
COPY --from=builder-dev /opt/venv /opt/venv

# App code (will be overlayed by volume in compose override)
COPY apps/backend/ /app/

# Add start script
COPY docker/start-backend.sh /start-backend.sh
RUN chmod +x /start-backend.sh

EXPOSE 8000
#CMD ["poetry", "run", "uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
# In dev stage:
CMD ["/start-backend.sh", "dev"]