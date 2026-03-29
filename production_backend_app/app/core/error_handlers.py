"""
Global FastAPI exception handlers.
Maps domain exceptions → HTTP responses and logs every error.
"""
import traceback

from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.core.exceptions import (
    AppBaseException,
    ConflictException,
    NotFoundException,
    ValidationException,
    DatabaseException,
)
from app.core.logging import get_logger

logger = get_logger(__name__)


def _error_body(status: int, error: str, detail: object) -> dict:
    return {"status": status, "error": error, "detail": detail}


async def not_found_handler(request: Request, exc: NotFoundException) -> JSONResponse:
    logger.warning("Not found: %s | path=%s", exc.message, request.url.path)
    return JSONResponse(
        status_code=404,
        content=_error_body(404, "Not Found", exc.message),
    )


async def conflict_handler(request: Request, exc: ConflictException) -> JSONResponse:
    logger.warning("Conflict: %s | path=%s", exc.message, request.url.path)
    return JSONResponse(
        status_code=409,
        content=_error_body(409, "Conflict", exc.message),
    )


async def validation_handler(request: Request, exc: ValidationException) -> JSONResponse:
    logger.warning("Validation error: %s | path=%s", exc.message, request.url.path)
    return JSONResponse(
        status_code=422,
        content=_error_body(422, "Unprocessable Entity", exc.message),
    )


async def database_handler(request: Request, exc: DatabaseException) -> JSONResponse:
    logger.error("Database error: %s | path=%s", exc.message, request.url.path)
    return JSONResponse(
        status_code=500,
        content=_error_body(500, "Internal Server Error", exc.message),
    )


async def app_base_handler(request: Request, exc: AppBaseException) -> JSONResponse:
    logger.error("Application error: %s | path=%s", exc.message, request.url.path)
    return JSONResponse(
        status_code=500,
        content=_error_body(500, "Internal Server Error", exc.message),
    )


async def pydantic_validation_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    errors = exc.errors()
    logger.warning("Request validation failed: %s | path=%s", errors, request.url.path)
    return JSONResponse(
        status_code=422,
        content=_error_body(422, "Unprocessable Entity", errors),
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    # Always log the FULL traceback so it appears in `docker compose logs app`
    tb = traceback.format_exc()
    logger.error(
        "Unhandled exception on %s %s\n"
        "Exception type : %s\n"
        "Exception value: %s\n"
        "Traceback:\n%s",
        request.method,
        request.url.path,
        type(exc).__name__,
        exc,
        tb,
    )
    return JSONResponse(
        status_code=500,
        content=_error_body(
            500,
            "Internal Server Error",
            # Expose the real error message to make debugging easier.
            # In a hardened production deployment you would return a generic
            # message here and rely on log aggregation instead.
            f"{type(exc).__name__}: {exc}",
        ),
    )


def register_exception_handlers(app) -> None:  # noqa: ANN001
    """Attach all exception handlers to a FastAPI app instance."""
    app.add_exception_handler(NotFoundException, not_found_handler)
    app.add_exception_handler(ConflictException, conflict_handler)
    app.add_exception_handler(ValidationException, validation_handler)
    app.add_exception_handler(DatabaseException, database_handler)
    app.add_exception_handler(AppBaseException, app_base_handler)
    app.add_exception_handler(RequestValidationError, pydantic_validation_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
