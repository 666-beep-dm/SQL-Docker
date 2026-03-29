# Production Backend App

A production-ready FastAPI application with layered architecture, PostgreSQL, Alembic migrations, and Docker.

---

## Project Structure

```
production_backend_app/
│
├── app/
│   ├── core/
│   │   ├── config.py        # pydantic-settings configuration
│   │   ├── database.py      # Async SQLAlchemy engine & session
│   │   ├── logging.py       # Structured logging setup
│   │   └── security.py      # Password hashing utilities
│   │
│   ├── models/
│   │   └── user.py          # SQLAlchemy User model
│   │
│   ├── schemas/
│   │   └── user.py          # Pydantic V2 request/response schemas
│   │
│   ├── repositories/
│   │   └── user_repository.py  # Data access layer
│   │
│   ├── services/
│   │   └── user_service.py  # Business logic layer
│   │
│   ├── routers/
│   │   ├── health.py        # /health endpoint with DB check
│   │   └── users.py         # Full CRUD for User entity
│   │
│   └── main.py              # FastAPI app entry point
│
├── alembic/
│   ├── versions/
│   │   └── 0001_initial_users_table.py
│   ├── env.py
│   └── script.py.mako
│
├── scripts/
│   └── entrypoint.sh        # Waits for DB, runs migrations
│
├── alembic.ini
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
├── .dockerignore
└── .gitignore
```

---

## Quick Start

### 1. Configure environment
```bash
cp .env.example .env
# Edit .env with your values
```

### 2. Build and run with Docker Compose
```bash
docker compose up --build
```

### 3. Verify the application
```bash
curl http://localhost:8000/health
```

---

## API Endpoints

| Method   | Endpoint                  | Description         |
|----------|---------------------------|---------------------|
| GET      | `/health`                 | Health + DB check   |
| POST     | `/api/v1/users/`          | Create user         |
| GET      | `/api/v1/users/`          | List users          |
| GET      | `/api/v1/users/{id}`      | Get user by ID      |
| PATCH    | `/api/v1/users/{id}`      | Update user         |
| DELETE   | `/api/v1/users/{id}`      | Delete user         |

Interactive docs: **http://localhost:8000/docs**

---

## Database Migrations

```bash
# Generate a new migration
docker compose exec app alembic revision --autogenerate -m "your message"

# Apply migrations
docker compose exec app alembic upgrade head

# Rollback one step
docker compose exec app alembic downgrade -1
```

---

## Architecture

```
Request → Router → Service → Repository → Database
                ↓
           Schemas (Pydantic V2 validation)
```

- **Router**: HTTP layer, dependency injection, input/output schemas
- **Service**: Business logic, validation rules, orchestration
- **Repository**: Raw DB queries via SQLAlchemy 2.0 async
- **Model**: SQLAlchemy ORM table definitions
