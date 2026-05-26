"""HTTP exception handlers for REST API.

Note: Some status codes use raw integers (422, 413) instead of named constants
to avoid deprecation warnings. The new constant names (HTTP_422_UNPROCESSABLE_CONTENT,
HTTP_413_CONTENT_TOO_LARGE) are not yet available in Starlette 1.1.0.
"""

from datetime import datetime, timezone
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from models.exceptions import (
    SFMError,
    ErrorCode,
)


# HTTP status code mapping for SFM error codes
ERROR_CODE_HTTP_STATUS = {
    ErrorCode.NOT_FOUND_ERROR: status.HTTP_404_NOT_FOUND,
    ErrorCode.VALIDATION_ERROR: status.HTTP_400_BAD_REQUEST,
    ErrorCode.NODE_CREATION_ERROR: status.HTTP_400_BAD_REQUEST,
    ErrorCode.NODE_UPDATE_ERROR: status.HTTP_400_BAD_REQUEST,
    ErrorCode.NODE_DELETE_ERROR: status.HTTP_400_BAD_REQUEST,
    ErrorCode.RELATIONSHIP_ERROR: status.HTTP_400_BAD_REQUEST,
    ErrorCode.INTEGRITY_ERROR: status.HTTP_409_CONFLICT,
    ErrorCode.QUERY_EXECUTION_ERROR: status.HTTP_500_INTERNAL_SERVER_ERROR,
    ErrorCode.QUERY_TIMEOUT_ERROR: status.HTTP_504_GATEWAY_TIMEOUT,
    ErrorCode.QUERY_SYNTAX_ERROR: status.HTTP_400_BAD_REQUEST,
    ErrorCode.DATABASE_CONNECTION_ERROR: status.HTTP_503_SERVICE_UNAVAILABLE,
    ErrorCode.DATABASE_TRANSACTION_ERROR: status.HTTP_500_INTERNAL_SERVER_ERROR,
    ErrorCode.DATABASE_PERSISTENCE_ERROR: status.HTTP_500_INTERNAL_SERVER_ERROR,
    ErrorCode.PERMISSION_DENIED_ERROR: status.HTTP_403_FORBIDDEN,
    ErrorCode.SECURITY_VALIDATION_ERROR: status.HTTP_403_FORBIDDEN,
    ErrorCode.GRAPH_SIZE_EXCEEDED: 413,  # Raw int avoids deprecation (HTTP_413_CONTENT_TOO_LARGE not yet available)
    ErrorCode.GRAPH_OPERATION_ERROR: status.HTTP_500_INTERNAL_SERVER_ERROR,
}


async def sfm_exception_handler(request: Request, exc: SFMError) -> JSONResponse:
    """
    Handle SFMError exceptions and convert to HTTP responses.

    Maps SFM error codes to appropriate HTTP status codes and
    returns structured error response.

    Args:
        request: FastAPI request object
        exc: SFMError exception instance

    Returns:
        JSONResponse with error details and appropriate status code
    """
    # Get HTTP status code from error code, default to 500
    http_status = ERROR_CODE_HTTP_STATUS.get(
        exc.error_code,
        status.HTTP_500_INTERNAL_SERVER_ERROR
    )

    # Build error response
    error_response = {
        "error": exc.error_code.value if hasattr(exc.error_code, "value") else str(exc.error_code),
        "message": exc.message,
        "context": exc.context.to_dict() if hasattr(exc.context, "to_dict") else {},
        "remediation": exc.remediation,
        "details": exc.details if hasattr(exc, "details") else None,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    return JSONResponse(
        status_code=http_status,
        content=error_response
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
) -> JSONResponse:
    """
    Handle Pydantic validation errors.

    Args:
        request: FastAPI request object
        exc: RequestValidationError exception

    Returns:
        JSONResponse with validation error details
    """
    return JSONResponse(
        status_code=422,  # Raw int avoids deprecation (HTTP_422_UNPROCESSABLE_CONTENT not yet available)
        content={
            "error": "VALIDATION_ERROR",
            "message": "Request validation failed",
            "context": {
                "errors": exc.errors(),
                "body": exc.body if hasattr(exc, "body") else None,
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle unexpected exceptions.

    Args:
        request: FastAPI request object
        exc: Generic exception

    Returns:
        JSONResponse with generic error message
    """
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred",
            "context": {
                "exception_type": type(exc).__name__,
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    )
