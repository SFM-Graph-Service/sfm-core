"""
Data layer module for SFM Core.

Provides repository abstractions and data access patterns for Beta unified model.
"""

from data.repositories import (
    SFMRepository,
    NetworkXSFMRepository,
    TypedSFMRepository,
    RelationshipRepository,
    SFMRepositoryFactory,
)

__all__ = [
    "SFMRepository",
    "NetworkXSFMRepository",
    "TypedSFMRepository",
    "RelationshipRepository",
    "SFMRepositoryFactory",
]
