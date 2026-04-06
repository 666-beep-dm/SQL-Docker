from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.exceptions import AppException
from app.core.logging import logger


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    logger.warning(f"AppException [{exc.status_code}]: {exc.message} | path={request.url.path}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": exc.status_code,
            "error": exc.__class__.__name__.replace("Exception", ""),
            "detail": exc.message,
        },
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    logger.warning(f"Validation error: {exc.errors()} | path={request.url.path}")
    return JSONResponse(
        status_code=422,
        content={
            "status": 422,
            "error": "Validation Error",
            "detail": exc.errors(),
        },
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error(f"Unhandled exception on {request.method} {request.url.path}", exc_info=exc)
    return JSONResponse(
        status_code=500,
        content={
            "status": 500,
            "error": "Internal Server Error",
            "detail": "An unexpected error occurred.",
        },
    )
