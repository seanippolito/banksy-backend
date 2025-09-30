# Banksy – Full-Stack Banking MVP

Banksy is a **full-stack banking application MVP** built with:

* **Backend**: FastAPI + SQLAlchemy + Alembic + SQLite (dev) / Postgres (prod)

## 🛠️ Prerequisites

* Python 3.12+
* [Poetry](https://python-poetry.org/) (Python dependency manager)

---

## 💾 Database Setup

Banksy stores its data in `banksy.db` (SQLite in development).

### Data Directory

```bash
mkdir -p apps/backend/data
```

### Run Migrations

```bash
cd apps/backend
poetry run alembic upgrade head
```

### Seed Basic Data

```bash
make seed
```
---

## 🚀 Running the Application

### Local Development (without Docker)

1. Start backend

   ```bash
   cd apps/backend
   poetry install
   poetry run uvicorn app.main:app --reload
   ```

---

## 📖 API Documentation

FastAPI provides interactive API docs at:

👉 [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🧪 Testing

Run backend tests with coverage report included:

```bash
cd apps/backend
poetry run pytest -v
```

In-memory SQLite is used for testing to isolate from dev/prod data.

---
