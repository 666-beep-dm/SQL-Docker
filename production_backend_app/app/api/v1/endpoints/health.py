"""
Health-check endpoint.
GET /health → 200 OK with application version.
"""
from fastapi import APIRouter

from app.core.config import get_settings
from app.schemas.common import HealthResponse

router = APIRouter(tags=["Health"])
settings = get_settings()


@router.get("/health", response_model=HealthResponse, summary="Health check")
async def health() -> HealthResponse:
    """
    Returns the application health status and current version.

    Useful for readiness / liveness probes in container orchestrators.
    """
    return HealthResponse(status="ok", version=settings.app_version)
