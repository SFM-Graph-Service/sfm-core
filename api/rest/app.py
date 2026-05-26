"""FastAPI application factory for SFM Core REST API."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from api.rest.config import settings
from api.rest.exceptions import (
    sfm_exception_handler,
    validation_exception_handler,
    generic_exception_handler,
)
from models.exceptions import SFMError

# Import routers
from api.rest.routers import health, nodes, query, evaluate


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application.

    Returns:
        Configured FastAPI application instance
    """
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.PROJECT_VERSION,
        debug=settings.DEBUG,
        docs_url=f"{settings.API_V1_PREFIX}/docs",
        openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
        redoc_url=f"{settings.API_V1_PREFIX}/redoc",
        description="REST API for Social Fabric Matrix (SFM) Core framework - "
                    "modeling, analyzing, and querying complex socio-economic systems",
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.CORS_ALLOW_METHODS,
        allow_headers=settings.CORS_ALLOW_HEADERS,
    )

    # Exception handlers
    app.add_exception_handler(SFMError, sfm_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, generic_exception_handler)

    # Include routers
    app.include_router(
        health.router,
        prefix=settings.API_V1_PREFIX,
        tags=["Health & Diagnostics"]
    )
    app.include_router(
        nodes.router,
        prefix=f"{settings.API_V1_PREFIX}/nodes",
        tags=["Nodes"]
    )
    app.include_router(
        query.router,
        prefix=f"{settings.API_V1_PREFIX}/query",
        tags=["Query Analysis"]
    )
    app.include_router(
        evaluate.router,
        prefix=f"{settings.API_V1_PREFIX}/evaluate",
        tags=["Evaluation"]
    )

    return app


# Create application instance
app = create_app()
