"""
Domain-level exceptions used across service and repository layers.
"""


class AppBaseException(Exception):
    """Base class for all application exceptions."""

    def __init__(self, message: str = "An unexpected error occurred.") -> None:
        self.message = message
        super().__init__(self.message)


class NotFoundException(AppBaseException):
    """Raised when a requested resource does not exist (or is soft-deleted)."""

    def __init__(self, resource: str = "Resource", identifier: object = None) -> None:
        detail = f"{resource} not found."
        if identifier is not None:
            detail = f"{resource} with id '{identifier}' not found."
        super().__init__(detail)


class ConflictException(AppBaseException):
    """Raised on uniqueness constraint violations (e.g. duplicate email)."""

    def __init__(self, message: str = "Resource already exists.") -> None:
        super().__init__(message)


class ValidationException(AppBaseException):
    """Raised when business-rule validation fails."""

    def __init__(self, message: str = "Validation error.") -> None:
        super().__init__(message)


class DatabaseException(AppBaseException):
    """Raised when an unrecoverable database error occurs."""

    def __init__(self, message: str = "A database error occurred.") -> None:
        super().__init__(message)
