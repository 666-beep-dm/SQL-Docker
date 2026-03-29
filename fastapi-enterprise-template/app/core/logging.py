import logging
import sys
from logging.config import dictConfig


def configure_logging() -> None:
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "json": {
                    "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
                    "format": "%(asctime)s %(name)s %(levelname)s %(message)s",
                },
                "standard": {
                    "format": "[%(asctime)s] %(levelname)s [%(name)s] %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "stream": sys.stdout,
                    "formatter": "standard",
                    "level": "DEBUG",
                },
            },
            "root": {
                "handlers": ["console"],
                "level": "INFO",
            },
            "loggers": {
                "app": {"handlers": ["console"], "level": "DEBUG", "propagate": False},
                "uvicorn": {"handlers": ["console"], "level": "INFO", "propagate": False},
                "sqlalchemy.engine": {"handlers": ["console"], "level": "WARNING", "propagate": False},
            },
        }
    )


logger = logging.getLogger("app")
