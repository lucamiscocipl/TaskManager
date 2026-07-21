import logging

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.exceptions import (
    ApplicationError,
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    InfrastructureError,
    NotFoundError,
    PayloadTooLargeError,
    RequestValidationError,
    UnsupportedMediaTypeError,
)

logger = logging.getLogger(__name__)


def _status_code_for(error: ApplicationError) -> int:
    if isinstance(error, AuthenticationError):
        return status.HTTP_401_UNAUTHORIZED
    if isinstance(error, AuthorizationError):
        return status.HTTP_403_FORBIDDEN
    if isinstance(error, NotFoundError):
        return status.HTTP_404_NOT_FOUND
    if isinstance(error, ConflictError):
        return status.HTTP_409_CONFLICT
    if isinstance(error, UnsupportedMediaTypeError):
        return status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
    if isinstance(error, PayloadTooLargeError):
        return status.HTTP_413_CONTENT_TOO_LARGE
    if isinstance(error, RequestValidationError):
        return status.HTTP_400_BAD_REQUEST
    return status.HTTP_500_INTERNAL_SERVER_ERROR


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(ApplicationError)
    async def handle_application_error(
        request: Request,
        error: ApplicationError,
    ) -> JSONResponse:
        status_code = _status_code_for(error)
        headers = None

        if isinstance(error, InfrastructureError):
            logger.error(
                "Infrastructure failure while handling %s %s",
                request.method,
                request.url.path,
                exc_info=(type(error), error, error.__traceback__),
            )
            detail = "Internal server error"
        else:
            detail = error.message

        if isinstance(error, AuthenticationError):
            headers = {"WWW-Authenticate": "Bearer"}

        return JSONResponse(
            status_code=status_code,
            content={"detail": detail},
            headers=headers,
        )
