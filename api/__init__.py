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

__version__ = "0.7.0"

__all__ = [
    "SFMService",
    "SFMServiceConfig",
    "ServiceHealth",
    "GraphStatistics",
    "__version__",
]
