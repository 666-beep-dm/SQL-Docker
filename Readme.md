# FastAPI Enterprise Template — Production-Ready REST API

## Project Overview

A fully production-grade RESTful User Management API built with FastAPI and async SQLAlchemy 2.0. The project solves the common problem of structuring a Python backend that is simultaneously fast to develop and safe to deploy: it wires up Clean Architecture layering (router → service → repository), automated database migrations, connection-pooled async PostgreSQL access, and a containerized deployment in a single coherent codebase. It serves as a reference template for any backend service that needs robust user lifecycle management out of the box.

## Key Features

- **Full async stack** — `asyncpg` driver + `AsyncSession` throughout; no blocking I/O
- **Soft-delete pattern** — users are never hard-deleted; partial unique index on `email WHERE is_deleted = false` prevents ghost conflicts
- **Repository Pattern** — database queries isolated in `UserRepository`; service layer never touches raw SQL
- **Pydantic v2 schemas** — strict input validation with `EmailStr`, `Field` constraints, and `model_validate` for ORM serialization
- **Structured exception hierarchy** — `AppException → NotFoundException / ConflictException` with registered FastAPI handlers returning consistent JSON error shapes
- **Alembic migrations** — version-controlled schema changes with automatic `upgrade head` on container startup via `entrypoint.sh`
- **Connection pool tuning** — `pool_size=10`, `max_overflow=20`, `pool_pre_ping=True` baked into the engine
- **Health endpoint** — `/api/v1/health` executes a live `SELECT 1` and reports DB readiness alongside app version
- **Docker-first** — multi-stage Dockerfile, `docker-compose.yml` with service health checks and `depends_on: condition: service_healthy`
- **URL-safe password encoding** — `quote_plus` in `Settings.DATABASE_URL` property prevents special-character breakage without exposing a raw `DATABASE_URL` env variable

## Architecture

```
HTTP Client
    │
    ▼
FastAPI App (main.py)
  ├── CORS Middleware
  ├── Exception Handlers (AppException, ValidationError, unhandled)
  └── Router: /api/v1
        ├── /health          ← readiness probe
        └── /users           ← CRUD endpoints
              │
              ▼
        UserService          ← business logic, conflict/not-found checks
              │
              ▼
        UserRepository       ← async SQLAlchemy queries
              │
              ▼
        PostgreSQL 16        ← via asyncpg, connection-pooled engine
```

**Data flow — create user:**

```
POST /api/v1/users
  → UserCreate (Pydantic validation)
  → UserService.create_user()
      → UserRepository.get_by_email()   # duplicate check
      → UserRepository.create()         # flush + refresh
  → UserResponse (model_validate)
  ← 201 Created
```

## Tech Stack

- Python 3.11
- FastAPI 0.111 · Uvicorn
- SQLAlchemy 2.0 (async) · asyncpg
- Alembic 1.13
- Pydantic v2 · pydantic-settings
- bcrypt · python-jose
- PostgreSQL 16
- Docker · Docker Compose

## Project Structure

```
fastapi-enterprise-template/
├── app/
│   ├── api/
│   │   ├── deps.py                  # Dependency injection (DB session → UserService)
│   │   └── v1/endpoints/
│   │       ├── health.py            # GET /health
│   │       └── users.py             # POST / GET / PATCH / DELETE /users
│   ├── core/
│   │   ├── config.py                # Pydantic Settings; DATABASE_URL computed property
│   │   ├── error_handlers.py        # Registered FastAPI exception handlers
│   │   ├── exceptions.py            # AppException hierarchy
│   │   ├── logging.py               # Structured logging setup
│   │   └── security.py              # bcrypt password hashing
│   ├── db/
│   │   └── session.py               # Async engine + session factory + get_db dependency
│   ├── models/
│   │   ├── mixins.py                # UUIDMixin, TimestampMixin, SoftDeleteMixin
│   │   └── user.py                  # User ORM model
│   ├── repositories/
│   │   └── user_repository.py       # All DB queries; pagination with COUNT subquery
│   ├── schemas/
│   │   ├── common.py                # HealthResponse
│   │   └── user.py                  # UserCreate, UserUpdate, UserResponse, UserListResponse
│   ├── services/
│   │   └── user_service.py          # Business logic layer
│   └── main.py                      # App factory, middleware, lifespan hook
├── alembic/
│   └── versions/0001_create_users_table.py  # Partial unique index on email
├── scripts/
│   ├── entrypoint.sh                # alembic upgrade head → exec uvicorn
│   └── seed.py                      # Dev data seeder
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

## Installation & Run

```bash
git clone <repo-url>
cd fastapi-enterprise-template

cp .env.example .env          # review defaults if needed

docker compose up --build     # starts postgres + app; migrations run automatically
```

API available at `http://localhost:8000`
Interactive docs at `http://localhost:8000/docs`

## API Usage Examples

**Create user**
```bash
curl -X POST http://localhost:8000/api/v1/users \
  -H "Content-Type: application/json" \
  -d '{"first_name":"Alice","last_name":"Smith","email":"alice@example.com","password":"securepass1"}'
```
```json
{
  "id": "d4f2e9a1-...",
  "first_name": "Alice",
  "last_name": "Smith",
  "email": "alice@example.com",
  "age": null,
  "is_active": true,
  "is_deleted": false,
  "created_at": "2025-04-01T12:00:00Z",
  "updated_at": "2025-04-01T12:00:00Z"
}
```

**List users (paginated)**
```bash
curl "http://localhost:8000/api/v1/users?skip=0&limit=10&include_inactive=false"
```
```json
{ "total": 42, "items": [...] }
```

**Partial update**
```bash
curl -X PATCH http://localhost:8000/api/v1/users/<uuid> \
  -H "Content-Type: application/json" \
  -d '{"age": 30}'
```

**Soft delete**
```bash
curl -X DELETE http://localhost:8000/api/v1/users/<uuid>
# 204 No Content
```

**Health check**
```bash
curl http://localhost:8000/api/v1/health
```
```json
{ "status": "ok", "version": "1.0.0" }
```

## Skills Demonstrated

**Backend Development**
Async Python from the engine up: `AsyncSession`, `async_sessionmaker`, `asynccontextmanager` lifespan, `await session.flush()` + `refresh()` pattern for returning post-insert state.

**API Design — REST / FastAPI**
Versioned prefix `/api/v1`, correct HTTP verbs and status codes (201, 204, 404, 409), `Query` parameter validation with `ge`/`le` bounds, separated request and response schemas, `response_model` enforced on every route.

**Database Design**
UUID primary keys, `TimestampMixin` with server-side `NOW()` defaults, `SoftDeleteMixin` with partial unique index `ix_users_email_active WHERE is_deleted = false` — prevents duplicate-email conflicts for restored accounts without a full table scan.

**Docker / Containerization**
Production-ready Dockerfile on `python:3.11-slim` with apt cleanup, `PYTHONDONTWRITEBYTECODE`, `PYTHONUNBUFFERED`, and `PIP_NO_CACHE_DIR`. Compose file wires DB health check → app `depends_on` so migrations never race against a cold Postgres.

**System Design Thinking**
Repository Pattern enforces the single-responsibility principle: the service layer makes zero direct SQLAlchemy calls. `Settings.DATABASE_URL` is a computed `@property` rather than an environment variable to prevent `quote_plus`-solvable special-character bugs in production passwords. Connection pool sized with `max_overflow` headroom for burst traffic.

## Engineering Challenges & Solutions

**Special characters in DB passwords crashing containers**
Using a raw `DATABASE_URL` env variable breaks when passwords contain `@`, `$`, or `!`. Solution: only accept individual `POSTGRES_*` fields and build the URL via `urllib.parse.quote_plus` inside a `@property`. This is documented inline so future contributors don't regress it.

**Partial unique index for soft-deleted users**
A standard `UNIQUE` constraint on `email` would block re-registering an email after soft-delete. The migration creates `CREATE UNIQUE INDEX ix_users_email_active ON users (email) WHERE is_deleted = false`, allowing the same email to be reused post-deletion while maintaining the uniqueness guarantee for live records.

**Race condition on DB startup in Docker Compose**
The app container starts Alembic migrations immediately on boot. Without a proper health check, migrations would fail if Postgres is still initializing. The Compose file uses `pg_isready` as the DB health check and `depends_on: condition: service_healthy` on the app service — ensuring Alembic always connects to a ready database.

**Transaction safety via dependency injection**
`get_db()` yields a session that commits on clean exit and rolls back on any exception. All DB operations in a single request share this session, making accidental partial writes impossible without explicitly committing mid-request.

## What I Learned

Implementing the Repository Pattern end-to-end clarified where business logic belongs versus where data access logic belongs — the boundary becomes obvious when you realize the service should read like a policy document, not a SQL tutorial. Building the partial unique index forced me to understand PostgreSQL partial indexes at the DDL level rather than relying on ORM magic. Getting Docker Compose health checks right for the first time removed an entire category of flaky container startup failures.

## Future Improvements

- **JWT authentication** — issue access/refresh token pair on login; protect write endpoints with `Depends(get_current_user)`
- **Role-based access control** — `is_admin` flag or a dedicated `roles` table with M2M relationship
- **Rate limiting** — per-IP or per-user using `slowapi` or Redis-backed middleware
- **Observability** — Prometheus metrics via `prometheus-fastapi-instrumentator`, structured JSON logs forwarded to Loki
- **Test suite** — `pytest-asyncio` + `httpx.AsyncClient` integration tests; factory fixtures with `faker`
- **CI/CD** — GitHub Actions pipeline: lint (ruff) → type-check (mypy) → test → Docker build → push to registry
- **Kubernetes** — HPA on CPU/RPS, PVC for Postgres, NetworkPolicy to isolate the DB service