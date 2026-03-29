# Production Backend App

A production-ready **FastAPI** backend built with **Async SQLAlchemy 2.0**, **PostgreSQL**, and **Alembic** migrations. Implements the Repository Pattern, Service Layer, and FastAPI Dependency Injection throughout.

---

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Project Structure](#project-structure)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Local Development (Docker)](#local-development-docker)
  - [Local Development (without Docker)](#local-development-without-docker)
- [Environment Variables](#environment-variables)
- [Database Migrations](#database-migrations)
- [Seeding the Database](#seeding-the-database)
- [API Reference](#api-reference)
- [Design Decisions](#design-decisions)
- [Error Handling](#error-handling)

---

## Architecture Overview

```
HTTP Request
    │
    ▼
┌─────────────────────┐
│   FastAPI Router    │  ← Input validation via Pydantic schemas
│  (api/v1/endpoints) │
└────────┬────────────┘
         │  Depends()
         ▼
┌─────────────────────┐
│   Service Layer     │  ← Business logic, orchestration, transactions
│   (services/)       │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│ Repository Layer    │  ← All SQL / ORM access
│  (repositories/)    │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  SQLAlchemy ORM     │  ← Async engine + session factory
│  PostgreSQL         │
└─────────────────────┘
```

---

## Project Structure

```
production_backend_app/
├── app/
│   ├── api/
│   │   ├── deps.py                  # FastAPI dependency injection
│   │   └── v1/
│   │       ├── __init__.py          # v1 router aggregator
│   │       └── endpoints/
│   │           ├── health.py        # GET /api/v1/health
│   │           └── users.py         # CRUD /api/v1/users
│   ├── core/
│   │   ├── config.py                # Pydantic Settings (env vars)
│   │   ├── error_handlers.py        # Global FastAPI exception handlers
│   │   ├── exceptions.py            # Domain exception classes
│   │   ├── logging.py               # Structured logging configuration
│   │   └── security.py              # bcrypt password hashing
│   ├── db/
│   │   └── session.py               # Async engine, session factory, get_db()
│   ├── models/
│   │   ├── mixins.py                # UUID PK, timestamps, soft-delete mixins
│   │   └── user.py                  # User ORM model
│   ├── repositories/
│   │   └── user_repository.py       # User database access layer
│   ├── schemas/
│   │   ├── common.py                # HealthResponse, MessageResponse
│   │   └── user.py                  # UserCreate, UserUpdate, UserResponse, ...
│   ├── services/
│   │   └── user_service.py          # User business logic
│   └── main.py                      # Application factory (create_app)
├── alembic/
│   ├── versions/
│   │   └── 0001_create_users.py     # Initial migration
│   ├── env.py                       # Async-aware Alembic env
│   └── script.py.mako               # Migration template
├── scripts/
│   └── seed.py                      # DB seed script (10 test users)
├── alembic.ini
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
└── .gitignore
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI 0.111 |
| ORM | SQLAlchemy 2.0 (async) |
| Driver | asyncpg (async), psycopg2 (Alembic) |
| Database | PostgreSQL 16 |
| Migrations | Alembic 1.13 |
| Validation | Pydantic v2 + pydantic-settings |
| Passwords | passlib + bcrypt |
| Runtime | Python 3.12, Uvicorn |
| Containers | Docker + Docker Compose |

---

## Getting Started

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) ≥ 24 (or Docker Engine + Compose v2)
- Python 3.12+ (for local development without Docker)

---

### Local Development (Docker)

This is the recommended path — everything runs in containers.

**1. Clone and configure**

```bash
cd production_backend_app
cp .env.example .env          # Review and adjust if needed
```

**2. Build and start all services**

```bash
docker compose up --build
```

This will:
- Start a PostgreSQL 16 container with a health check.
- Build the FastAPI image.
- Run `alembic upgrade head` automatically on startup.
- Start Uvicorn with `--reload` for hot-reloading.

**3. Verify the app is running**

```
GET http://localhost:8000/api/v1/health
→ {"status": "ok", "version": "1.0.0"}
```

**4. Open the interactive API docs**

- Swagger UI: http://localhost:8000/docs
- ReDoc:       http://localhost:8000/redoc

**5. Seed the database (optional)**

```bash
docker compose exec app python scripts/seed.py
```

**6. Stop all services**

```bash
docker compose down           # Keep volume
docker compose down -v        # Also remove postgres_data volume
```

---

### Local Development (without Docker)

**1. Create a virtual environment**

```bash
python -m venv .venv
source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

**2. Configure environment**

```bash
cp .env.example .env
# Edit .env — point POSTGRES_HOST to your local PostgreSQL instance
```

**3. Run migrations**

```bash
alembic upgrade head
```

**4. Start the server**

```bash
uvicorn app.main:app --reload --port 8000
```

**5. Seed the database (optional)**

```bash
python scripts/seed.py
```

---

## Environment Variables

All configuration is driven by environment variables (loaded from `.env` in development).

| Variable | Default | Description |
|---|---|---|
| `APP_NAME` | `Production Backend App` | Application display name |
| `APP_VERSION` | `1.0.0` | Shown in /health and OpenAPI docs |
| `DEBUG` | `false` | Enables SQLAlchemy query logging |
| `SECRET_KEY` | *(required)* | Min 32-char secret for signing tokens |
| `POSTGRES_HOST` | `localhost` | PostgreSQL hostname |
| `POSTGRES_PORT` | `5432` | PostgreSQL port |
| `POSTGRES_DB` | `production_db` | Database name |
| `POSTGRES_USER` | `postgres` | Database user |
| `POSTGRES_PASSWORD` | `postgres` | Database password |

> **Production note:** Always set a strong `SECRET_KEY` and replace the default `POSTGRES_PASSWORD`. Never commit `.env` to source control.

---

## Database Migrations

Alembic is configured for **async-aware** auto-generation. The `alembic/env.py` imports all ORM models automatically, so Alembic can detect schema changes.

```bash
# Apply all pending migrations
alembic upgrade head

# Create a new auto-generated migration
alembic revision --autogenerate -m "add phone_number to users"

# Downgrade one step
alembic downgrade -1

# Show current revision
alembic current

# Show migration history
alembic history --verbose

# Generate SQL script (offline mode, no DB connection needed)
alembic upgrade head --sql
```

---

## Seeding the Database

The seed script (`scripts/seed.py`) inserts 10 realistic test users. It is **idempotent** — re-running it skips any user whose email already exists.

```bash
# Via Docker Compose
docker compose exec app python scripts/seed.py

# Locally
python scripts/seed.py
```

Sample output:

```
INFO  ✔ Created user: alice.johnson@example.com
INFO  ✔ Created user: bob.smith@example.com
...
INFO  Seed complete — created: 10, skipped: 0, total: 10
```

---

## API Reference

All endpoints are prefixed with `/api/v1`.

### Health

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/v1/health` | Liveness / readiness check |

**Response 200**
```json
{
  "status": "ok",
  "version": "1.0.0"
}
```

---

### Users

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/v1/users` | Create a new user |
| `GET` | `/api/v1/users` | List users (paginated) |
| `GET` | `/api/v1/users/{id}` | Get a single user |
| `PATCH` | `/api/v1/users/{id}` | Partially update a user |
| `DELETE` | `/api/v1/users/{id}` | Soft-delete a user |

#### Create User — `POST /api/v1/users`

**Request body**
```json
{
  "first_name": "Alice",
  "last_name": "Johnson",
  "email": "alice@example.com",
  "password": "Secure#Pass1",
  "age": 29
}
```

**Response 201**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "first_name": "Alice",
  "last_name": "Johnson",
  "email": "alice@example.com",
  "age": 29,
  "is_active": true,
  "is_deleted": false,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

#### List Users — `GET /api/v1/users`

Query parameters:

| Parameter | Type | Default | Description |
|---|---|---|---|
| `skip` | int | `0` | Offset (≥ 0) |
| `limit` | int | `20` | Page size (1–100) |
| `include_inactive` | bool | `false` | Include inactive users |

**Response 200**
```json
{
  "total": 42,
  "items": [ { "id": "...", ... } ]
}
```

#### Update User — `PATCH /api/v1/users/{id}`

All fields are optional. Only supplied fields are updated.

```json
{
  "first_name": "Alicia",
  "age": 30,
  "is_active": false
}
```

#### Delete User — `DELETE /api/v1/users/{id}`

Returns `204 No Content`. The record is **soft-deleted** (`is_deleted = true`); it is not physically removed from the database.

---

### Error Responses

All errors follow a consistent envelope:

```json
{
  "status": 404,
  "error": "Not Found",
  "detail": "User with id '...' not found."
}
```

| HTTP Status | Cause |
|---|---|
| `404` | Resource does not exist or is soft-deleted |
| `409` | Duplicate email on create |
| `422` | Request validation failure (Pydantic) |
| `500` | Unhandled server error |

---

## Design Decisions

### UUID Primary Keys
All models use `uuid.uuid4()` as the primary key. UUIDs avoid sequential ID enumeration attacks, are safe to generate client-side, and merge cleanly across distributed databases.

### Soft Delete
Records are never physically removed via the normal API. The `is_deleted` boolean flag (and `deleted_at` timestamp) are set instead. A **partial unique index** (`WHERE is_deleted = false`) on the `email` column means a deleted user's email can be re-registered without violating uniqueness.

### Repository Pattern
All SQL lives in `repositories/`. Services never construct SQLAlchemy queries directly. This keeps business logic testable without a database and makes it trivial to swap the storage backend.

### Service Layer
`services/` contains all business rules (duplicate checks, password hashing, cascade logic). Routers delegate immediately to services and never contain business logic themselves.

### Dependency Injection
`app/api/deps.py` wires `AsyncSession → Repository → Service` using FastAPI's `Depends()` system. Each request gets a fresh session; the `get_db()` generator commits on success and rolls back on any exception.

### Transaction Management
`get_db()` in `app/db/session.py` manages the top-level transaction. The repository uses `session.flush()` (write to DB, don't commit) to obtain generated values within a transaction, leaving the commit decision to the session context manager. This ensures that multiple repository calls in a single service method are atomic.
