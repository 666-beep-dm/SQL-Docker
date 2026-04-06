from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import router as api_v1_router
from app.core.config import settings
from app.core.error_handlers import (
    app_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from app.core.exceptions import AppException
from app.core.logging import configure_logging, logger


configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION} (debug={settings.DEBUG})")
    yield
    from app.db.session import engine
    await engine.dispose()
    logger.info("Application shutdown complete.")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Exception handlers
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)

    # Routers
    app.include_router(api_v1_router, prefix="/api/v1")

    return app


app = create_app()
