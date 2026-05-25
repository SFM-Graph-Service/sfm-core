"""
SFM Service - Unified Facade for Social Fabric Matrix Framework (Beta)

This module provides a simplified interface to the SFM Core Beta unified model.
It acts as a facade for common SFM operations and integrates the Phase 2 query engine.

Key Features:
- Unified interface for creating and managing SFM nodes
- Built-in repository management
- Integrated query engine for advanced network analysis
- Phase 2 query methods: ceremonial analysis, circular causation, holarchy, conflicts
"""

import logging
import uuid
from typing import Dict, List, Optional, Any, Union, Type, TypeVar
from dataclasses import dataclass

from models import Node
from models.exceptions import (
    SFMError,
    SFMValidationError,
    SFMNotFoundError,
    NodeCreationError,
)
from data.repositories import (
    SFMRepository,
    SFMRepositoryFactory,
    TypedSFMRepository,
)

# Setup logging
logger = logging.getLogger(__name__)

T = TypeVar("T", bound=Node)


@dataclass
class ServiceHealth:
    """Service health status"""
    status: str
    node_count: int
    relationship_count: int


@dataclass
class GraphStatistics:
    """Graph statistics"""
    total_nodes: int
    total_relationships: int
    node_types: Dict[str, int]


class SFMServiceConfig:
    """Configuration for SFM Service"""

    def __init__(
        self,
        storage_type: str = "networkx",
        graph_size_limit: int = 10000,
    ):
        self.storage_type = storage_type
        self.graph_size_limit = graph_size_limit


class SFMService:
    """
    Main service facade for SFM Core Beta operations.
    Provides high-level interface to Beta unified model and Phase 2 query engine.
    """

    def __init__(self, config: Optional[SFMServiceConfig] = None):
        """
        Initialize the SFM Service.

        Args:
            config: Service configuration. If None, uses default settings.
        """
        self.config = config or SFMServiceConfig()

        # Initialize repository
        self._repository: SFMRepository = SFMRepositoryFactory.create_repository(
            self.config.storage_type
        )

        # Query engine will be initialized in Phase 2 Step 2
        self._query_engine: Optional[Any] = None

        logger.info("SFM Service initialized with storage type: %s", self.config.storage_type)

    @property
    def repository(self) -> SFMRepository:
        """Get the underlying repository"""
        return self._repository

    @property
    def query_engine(self) -> Any:
        """
        Get the query engine.
        Phase 2 Step 2 will create the actual query engine.
        """
        if self._query_engine is None:
            # Placeholder - will be replaced in Phase 2 Step 2
            logger.warning("Query engine not yet initialized")
        return self._query_engine

    def get_health(self) -> ServiceHealth:
        """Get service health status"""
        nodes = self._repository.list_nodes()
        relationships = self._repository.list_relationships()

        return ServiceHealth(
            status="healthy",
            node_count=len(nodes),
            relationship_count=len(relationships),
        )

    def create_node(self, node: Node) -> Node:
        """
        Create a new node in the system.

        Args:
            node: The node to create

        Returns:
            The created node

        Raises:
            NodeCreationError: If node creation fails
            SFMValidationError: If validation fails
        """
        try:
            created_node = self._repository.create_node(node)
            logger.info("Created node %s of type %s", created_node.id, type(created_node).__name__)
            return created_node
        except Exception as e:
            logger.error("Failed to create node: %s", str(e))
            raise

    def get_node(self, node_id: uuid.UUID) -> Optional[Node]:
        """
        Get a node by its ID.

        Args:
            node_id: The ID of the node to retrieve

        Returns:
            The node if found, None otherwise
        """
        return self._repository.read_node(node_id)

    def update_node(self, node: Node) -> Node:
        """
        Update an existing node.

        Args:
            node: The node to update

        Returns:
            The updated node

        Raises:
            SFMNotFoundError: If node doesn't exist
        """
        return self._repository.update_node(node)

    def delete_node(self, node_id: uuid.UUID) -> bool:
        """
        Delete a node by its ID.

        Args:
            node_id: The ID of the node to delete

        Returns:
            True if deleted, False if not found
        """
        return self._repository.delete_node(node_id)

    def list_nodes(self, node_type: Optional[Type[Node]] = None) -> List[Node]:
        """
        List all nodes, optionally filtered by type.

        Args:
            node_type: Optional node type to filter by

        Returns:
            List of nodes
        """
        return self._repository.list_nodes(node_type)

    def get_statistics(self) -> GraphStatistics:
        """
        Get graph statistics.

        Returns:
            GraphStatistics object with node and relationship counts
        """
        nodes = self._repository.list_nodes()
        relationships = self._repository.list_relationships()

        # Count nodes by type
        node_types: Dict[str, int] = {}
        for node in nodes:
            node_type = type(node).__name__
            node_types[node_type] = node_types.get(node_type, 0) + 1

        return GraphStatistics(
            total_nodes=len(nodes),
            total_relationships=len(relationships),
            node_types=node_types,
        )

    def clear_all_data(self) -> Dict[str, Any]:
        """
        Clear all data from the repository.

        Returns:
            Dictionary with operation status
        """
        self._repository.clear()
        logger.info("Cleared all data from repository")
        return {"status": "success", "message": "All data cleared"}

    # ========================================================================
    # Phase 2 Query Methods - Wrapping Beta Query Engine
    # ========================================================================

    def get_ceremonial_analysis(self, threshold: float = 0.5) -> dict:
        """
        Analyze ceremonial vs instrumental behaviors in the system.

        Args:
            threshold: Ceremonial threshold (0.0-1.0)

        Returns:
            Dictionary containing:
                - ceremonial_nodes: List of ceremonially-oriented nodes
                - instrumental_nodes: List of instrumentally-oriented nodes
                - ceremonial_ratio: Ratio of ceremonial to total
                - threshold: The threshold used

        Raises:
            SFMValidationError: If threshold is invalid
        """
        if not 0.0 <= threshold <= 1.0:
            raise SFMValidationError(
                "Threshold must be between 0.0 and 1.0",
                field="threshold",
                value=threshold
            )

        if self.query_engine is None:
            logger.warning("Query engine not initialized, returning empty analysis")
            return {
                "ceremonial_nodes": [],
                "instrumental_nodes": [],
                "ceremonial_ratio": 0.0,
                "threshold": threshold,
            }

        # Placeholder - will call query_engine.get_ceremonial_analysis in Phase 2 Step 2
        logger.info("Performing ceremonial analysis with threshold %.2f", threshold)
        return {
            "ceremonial_nodes": [],
            "instrumental_nodes": [],
            "ceremonial_ratio": 0.0,
            "threshold": threshold,
        }

    def get_circular_causation(self, source_id: uuid.UUID) -> list:
        """
        Identify circular causation patterns starting from a source node.

        Args:
            source_id: UUID of the starting node

        Returns:
            List of circular causation cycles, where each cycle is:
                - nodes: List of node IDs in the cycle
                - strength: Aggregate strength of the cycle
                - feedback_type: reinforcing or balancing

        Raises:
            SFMNotFoundError: If source node doesn't exist
        """
        # Verify source node exists
        source_node = self.get_node(source_id)
        if source_node is None:
            raise SFMNotFoundError(entity_type="Node", entity_id=source_id)

        if self.query_engine is None:
            logger.warning("Query engine not initialized, returning empty cycles")
            return []

        # Placeholder - will call query_engine.get_circular_causation in Phase 2 Step 2
        logger.info("Finding circular causation from node %s", source_id)
        return []

    def get_holarchy(self, institution_id: uuid.UUID) -> dict:
        """
        Get institutional holarchy (nested hierarchy) for an institution.

        Args:
            institution_id: UUID of the institution node

        Returns:
            Dictionary containing:
                - institution_id: The root institution UUID
                - layers: List of holarchy layers from top to bottom
                - relationships: Parent-child relationships
                - depth: Maximum depth of the holarchy

        Raises:
            SFMNotFoundError: If institution doesn't exist
        """
        # Verify institution exists
        institution_node = self.get_node(institution_id)
        if institution_node is None:
            raise SFMNotFoundError(entity_type="Node", entity_id=institution_id)

        if self.query_engine is None:
            logger.warning("Query engine not initialized, returning empty holarchy")
            return {
                "institution_id": str(institution_id),
                "layers": [],
                "relationships": [],
                "depth": 0,
            }

        # Placeholder - will call query_engine.get_holarchy in Phase 2 Step 2
        logger.info("Building holarchy for institution %s", institution_id)
        return {
            "institution_id": str(institution_id),
            "layers": [],
            "relationships": [],
            "depth": 0,
        }

    def get_conflicts(self) -> list:
        """
        Detect value conflicts in the system.

        Returns:
            List of detected conflicts, where each conflict is:
                - conflict_type: Type of conflict (value, resource, institutional)
                - nodes: List of node IDs involved
                - severity: Conflict severity (0.0-1.0)
                - description: Human-readable description
        """
        if self.query_engine is None:
            logger.warning("Query engine not initialized, returning empty conflicts")
            return []

        # Placeholder - will call query_engine.get_conflicts in Phase 2 Step 2
        logger.info("Detecting system conflicts")
        return []


# Public API
__all__ = [
    "SFMService",
    "SFMServiceConfig",
    "ServiceHealth",
    "GraphStatistics",
    "SFMError",
    "SFMValidationError",
    "SFMNotFoundError",
    "NodeCreationError",
]
