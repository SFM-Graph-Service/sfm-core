"""
API layer module for SFM Core.

Provides the service facade for Beta unified model operations.
"""

from api.sfm_service import (
    SFMService,
    SFMServiceConfig,
    ServiceHealth,
    GraphStatistics,
    ThresholdAlert,
    VALID_TEMPORAL_RATES,
    validate_temporal_rate,
)

__version__ = "0.7.0"

__all__ = [
    "SFMService",
    "SFMServiceConfig",
    "ServiceHealth",
    "GraphStatistics",
    "ThresholdAlert",
    "VALID_TEMPORAL_RATES",
    "validate_temporal_rate",
    "__version__",
]
