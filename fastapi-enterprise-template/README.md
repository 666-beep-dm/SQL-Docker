# FastAPI Enterprise Template

Production-ready FastAPI backend — async SQLAlchemy 2.0, PostgreSQL, Alembic, Docker.

## Project Structure

```
fastapi-enterprise-template/
├── app/
│   ├── api/
│   │   ├── deps.py                     # DI: Session → Service wiring
│   │   └── v1/
│   │       ├── __init__.py             # v1 router aggregator
│   │       └── endpoints/
│   │           ├── health.py           # GET /api/v1/health
│   │           └── users.py            # CRUD /api/v1/users
│   ├── core/
│   │   ├── config.py                   # pydantic-settings (DATABASE_URL @property)
│   │   ├── error_handlers.py           # Global exception handlers
│   │   ├── exceptions.py               # NotFoundException, ConflictException
│   │   ├── logging.py                  # Structured logging
│   │   └── security.py                 # bcrypt hashing (no passlib)
│   ├── db/
│   │   └── session.py                  # Async engine + session factory
│   ├── models/
│   │   ├── mixins.py                   # UUIDMixin, TimestampMixin, SoftDeleteMixin
│   │   └── user.py                     # User ORM model
│   ├── repositories/
│   │   └── user_repository.py          # Data access layer
│   ├── schemas/
│   │   ├── common.py                   # HealthResponse, MessageResponse
│   │   └── user.py                     # UserCreate, UserUpdate, UserResponse
│   ├── services/
│   │   └── user_service.py             # Business logic
│   └── main.py                         # App factory (create_app)
├── alembic/
│   ├── versions/
│   │   └── 0001_create_users_table.py
│   ├── env.py                          # Async Alembic + quote_plus fix
│   └── script.py.mako
├── scripts/
│   ├── entrypoint.sh                   # migrate → start uvicorn
│   └── seed.py                         # 10 idempotent test users
├── alembic.ini
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── .env.example
```

## Quick Start

```bash
# 1. Enter the project folder
cd fastapi-enterprise-template

# 2. Start everything (first time)
docker compose up --build
```

Wait until you see:
```
production_app | >>> Migrations complete. Starting application...
production_app | INFO: Application startup complete.
```

```bash
# 3. Health check (new terminal)
curl http://localhost:8000/api/v1/health

# 4. Create a user
curl -X POST http://localhost:8000/api/v1/users \
  -H "Content-Type: application/json" \
  -d '{"first_name":"Alice","last_name":"Smith","email":"alice@example.com","password":"mypassword1"}'

# 5. Seed 10 test users
docker compose exec app python scripts/seed.py

# 6. Interactive docs
# http://localhost:8000/docs
```

## API Endpoints

All endpoints are prefixed with `/api/v1`.

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/health` | Health + DB check |
| POST | `/api/v1/users` | Create user |
| GET | `/api/v1/users` | List users (paginated) |
| GET | `/api/v1/users/{id}` | Get user by ID |
| PATCH | `/api/v1/users/{id}` | Update user |
| DELETE | `/api/v1/users/{id}` | Soft-delete user |

### Query Parameters — GET /api/v1/users

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `skip` | int | 0 | Offset |
| `limit` | int | 20 | Page size (max 100) |
| `include_inactive` | bool | false | Show inactive users |

## Key Design Decisions

| Decision | Reason |
|----------|--------|
| `DATABASE_URL` as `@property` only | Prevents special chars in passwords from corrupting hostname DNS resolution |
| `bcrypt` direct (no passlib) | passlib is incompatible with bcrypt 4.x on Python 3.11+ |
| All env vars inline in docker-compose | Avoids shell interpolation of `$`, `@`, `!` in passwords |
| Soft delete (`is_deleted`) | Records are never physically removed; email reuse is allowed via partial unique index |
| Partial unique index on email | `WHERE is_deleted = false` — deleted users free up their email |
| Repository pattern | All SQL lives in repositories; services stay testable without a DB |
| `session.flush()` not `commit()` | Lets the session context manager own the transaction boundary |

## Migrations

```bash
# Apply all migrations
docker compose exec app alembic upgrade head

# Generate new migration
docker compose exec app alembic revision --autogenerate -m "add phone to users"

# Rollback one step
docker compose exec app alembic downgrade -1

# View history
docker compose exec app alembic history --verbose
```

## Useful Commands

| Command | Description |
|---------|-------------|
| `docker compose up --build` | First-time build and start |
| `docker compose up` | Start without rebuilding |
| `docker compose down` | Stop (keep data) |
| `docker compose down -v` | Stop and delete DB volume |
| `docker compose exec app python scripts/seed.py` | Seed test data |
| `docker logs -f production_app` | Follow app logs |
| `docker logs -f production_db` | Follow DB logs |
| `docker compose ps` | Check container status |
