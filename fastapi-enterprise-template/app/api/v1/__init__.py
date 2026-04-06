from fastapi import APIRouter

from app.api.v1.endpoints import health, users

router = APIRouter()

router.include_router(health.router, tags=["Health"])
router.include_router(users.router, prefix="/users", tags=["Users"])
