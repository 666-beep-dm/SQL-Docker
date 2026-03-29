"""
Structured logging configuration for the application.
"""
import logging
import sys
from app.core.config import get_settings

settings = get_settings()

LOG_LEVEL = logging.DEBUG if settings.debug else logging.INFO

LOG_FORMAT = (
    "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s"
)


def configure_logging() -> None:
    """Configure root logger with a consistent format."""
    logging.basicConfig(
        level=LOG_LEVEL,
        format=LOG_FORMAT,
        stream=sys.stdout,
    )
    # Quieten noisy third-party loggers
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if settings.debug else logging.WARNING
    )
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Return a named logger inheriting the root configuration."""
    return logging.getLogger(name)
