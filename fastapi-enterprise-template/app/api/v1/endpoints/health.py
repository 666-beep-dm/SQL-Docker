from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logging import logger
from app.db.session import get_db
from app.schemas.common import HealthResponse

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health & readiness check",
)
async def health_check(db: AsyncSession = Depends(get_db)) -> HealthResponse:
    try:
        await db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception as exc:
        logger.error(f"DB health check failed: {exc}")
        db_status = "degraded"

    return HealthResponse(
        status=db_status,
        version=settings.APP_VERSION,
    )
