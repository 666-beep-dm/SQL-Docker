class AppException(Exception):
    """Base application exception."""
    def __init__(self, message: str, status_code: int = 500) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class NotFoundException(AppException):
    def __init__(self, message: str = "Resource not found.") -> None:
        super().__init__(message, status_code=404)


class ConflictException(AppException):
    def __init__(self, message: str = "Resource already exists.") -> None:
        super().__init__(message, status_code=409)
