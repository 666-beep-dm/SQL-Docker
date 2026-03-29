# ============================================================
# Stage 1 — dependency builder
# ============================================================
FROM python:3.12-slim AS builder

WORKDIR /app

# Install build tools required by some packages (e.g. psycopg2)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --prefix=/install --no-cache-dir -r requirements.txt


# ============================================================
# Stage 2 — runtime image
# ============================================================
FROM python:3.12-slim AS runtime

LABEL maintainer="your-team@example.com"
LABEL description="Production Backend App — FastAPI + Async SQLAlchemy 2.0"

# Runtime library for psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy installed Python packages from builder
COPY --from=builder /install /usr/local

# Copy application source
COPY . .

# Non-root user for security
RUN addgroup --system appgroup \
    && adduser --system --ingroup appgroup appuser \
    && chown -R appuser:appgroup /app

USER appuser

# Expose the application port
EXPOSE 8000

# Entrypoint — run Alembic migrations then start Uvicorn
CMD ["sh", "-c", \
     "alembic upgrade head && \
      uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2"]
