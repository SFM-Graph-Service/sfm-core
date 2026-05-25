"""
API layer module for SFM Core.

Provides the service facade for Beta unified model operations.
"""

from api.sfm_service import (
    SFMService,
    SFMServiceConfig,
    ServiceHealth,
    GraphStatistics,
)

__all__ = [
    "SFMService",
    "SFMServiceConfig",
    "ServiceHealth",
    "GraphStatistics",
]
