import logging
import sys
from logging.config import dictConfig


def configure_logging() -> None:
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {
                    "format": "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s",
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
            "root": {"handlers": ["console"], "level": "INFO"},
            "loggers": {
                "app": {"handlers": ["console"], "level": "DEBUG", "propagate": False},
                "uvicorn": {"handlers": ["console"], "level": "INFO", "propagate": False},
                "sqlalchemy.engine": {"handlers": ["console"], "level": "WARNING", "propagate": False},
            },
        }
    )


logger = logging.getLogger("app")
