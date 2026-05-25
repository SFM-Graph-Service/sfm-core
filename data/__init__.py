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

from data.neo4j_repository import (
    Neo4jSFMRepository,
    Neo4jConnectionError,
    Neo4jSerializationError,
)

__all__ = [
    "SFMRepository",
    "NetworkXSFMRepository",
    "Neo4jSFMRepository",
    "TypedSFMRepository",
    "RelationshipRepository",
    "SFMRepositoryFactory",
    "Neo4jConnectionError",
    "Neo4jSerializationError",
]
