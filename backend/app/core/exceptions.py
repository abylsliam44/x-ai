from typing import Any, Optional

from fastapi import HTTPException, status


class AppError(HTTPException):
    code: str = "app_error"
    default_status: int = status.HTTP_400_BAD_REQUEST

    def __init__(self, message: str, *, status_code: Optional[int] = None, details: Any = None) -> None:
        super().__init__(
            status_code=status_code or self.default_status,
            detail={"code": self.code, "message": message, "details": details},
        )


class NotFoundError(AppError):
    code = "not_found"
    default_status = status.HTTP_404_NOT_FOUND


class UnauthorizedError(AppError):
    code = "unauthorized"
    default_status = status.HTTP_401_UNAUTHORIZED


class ForbiddenError(AppError):
    code = "forbidden"
    default_status = status.HTTP_403_FORBIDDEN


class ConflictError(AppError):
    code = "conflict"
    default_status = status.HTTP_409_CONFLICT


class ValidationError(AppError):
    code = "validation_error"
    default_status = status.HTTP_422_UNPROCESSABLE_ENTITY


class ProviderError(AppError):
    code = "provider_error"
    default_status = status.HTTP_502_BAD_GATEWAY


class WorkflowError(AppError):
    code = "workflow_error"
    default_status = status.HTTP_500_INTERNAL_SERVER_ERROR
