"""Dependency injection for REST API."""

from functools import lru_cache
from api.sfm_service import SFMService, SFMServiceConfig
from api.rest.config import settings


@lru_cache()
def get_sfm_service() -> SFMService:
    """
    Get or create singleton SFMService instance.

    Uses lru_cache to ensure one instance per worker process.
    Safe for NetworkX backend (thread-safe reads).
    For Neo4j backend, connection pooling handles concurrency.

    Returns:
        SFMService instance configured from environment settings.
    """
    config = SFMServiceConfig(
        storage_type=settings.STORAGE_TYPE,
        graph_size_limit=settings.GRAPH_SIZE_LIMIT,
    )
    return SFMService(config=config)
