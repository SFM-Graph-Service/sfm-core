"""
Graph structure and network metrics for SFM modeling.

This module defines the SFMGraph class that aggregates all SFM entities
and the NetworkMetrics class for network analysis.
"""

from __future__ import annotations

import uuid
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Iterator, Set, Any
from datetime import datetime

from models.base_nodes import Node

# Set up logger
logger = logging.getLogger(__name__)


@dataclass
class NetworkMetrics(Node):
    """Captures network analysis metrics for nodes or subgraphs."""

    centrality_measures: Dict[str, float] = field(default_factory=lambda: {})
    clustering_coefficient: Optional[float] = None
    path_lengths: Dict[uuid.UUID, float] = field(default_factory=lambda: {})
    community_assignment: Optional[str] = None


@dataclass
class Relationship:
    """Simple relationship class for connecting nodes."""

    id: uuid.UUID = field(default_factory=uuid.uuid4)
    source_id: uuid.UUID = field(default=None)  # type: ignore
    target_id: uuid.UUID = field(default=None)  # type: ignore
    kind: str = ""
    weight: Optional[float] = None
    meta: Dict[str, Any] = field(default_factory=lambda: {})


@dataclass
class SFMGraph:
    """A complete Social Fabric Matrix representation."""

    id: uuid.UUID = field(default_factory=uuid.uuid4)
    name: str = ""
    description: Optional[str] = None

    # Core components - use generic node storage
    nodes: Dict[uuid.UUID, Node] = field(default_factory=lambda: {})
    relationships: Dict[uuid.UUID, Relationship] = field(default_factory=lambda: {})
    network_metrics: Dict[uuid.UUID, NetworkMetrics] = field(default_factory=lambda: {})

    # Model metadata
    version: int = 1
    created_at: datetime = field(default_factory=datetime.now)
    modified_at: Optional[datetime] = None
    data_quality: Optional[str] = None
    previous_version_id: Optional[uuid.UUID] = None

    # Performance optimization: Central node index for O(1) lookups
    _node_index: Dict[uuid.UUID, Node] = field(default_factory=lambda: {}, init=False)
    _relationship_cache: Dict[uuid.UUID, List[Relationship]] = field(
        default_factory=lambda: {}, init=False
    )
    _relationship_cache_max_size: int = field(default=1000, init=False)

    def __post_init__(self):
        """Initialize performance optimizations."""
        self._node_index = self.nodes.copy()

    def add_node(self, node: Node) -> Node:
        """Add a node to the graph."""
        self.nodes[node.id] = node
        self._node_index[node.id] = node
        return node

    def add_relationship(self, relationship: Relationship) -> Relationship:
        """Add a relationship to the SFM graph."""
        self.relationships[relationship.id] = relationship
        self._clear_relationship_cache()
        return relationship

    def _find_node_by_id(self, node_id: uuid.UUID) -> Optional[Node]:
        """Find a node by its ID using central index for O(1) lookup."""
        return self._node_index.get(node_id)

    def get_node_by_id(self, node_id: uuid.UUID) -> Optional[Node]:
        """Public method to retrieve a node by its ID."""
        return self._find_node_by_id(node_id)

    def __iter__(self) -> Iterator[Node]:
        """Iterate over all nodes in the SFMGraph."""
        return iter(self.nodes.values())

    def __len__(self) -> int:
        """Return the total number of nodes in the graph."""
        return len(self.nodes)

    def clear(self) -> None:
        """Clear all nodes and relationships from the graph."""
        self.nodes.clear()
        self.relationships.clear()
        self._node_index.clear()
        self._relationship_cache.clear()

    def _clear_relationship_cache(self) -> None:
        """Clear the relationship cache when relationships change."""
        self._relationship_cache.clear()

    def get_node_relationships(self, node_id: uuid.UUID) -> List[Relationship]:
        """Get all relationships for a node with caching for performance."""
        # Check cache
        if node_id in self._relationship_cache:
            return self._relationship_cache[node_id]

        # Compute relationships for this node
        relationships: List[Relationship] = []
        for relationship in self.relationships.values():
            if node_id in (relationship.source_id, relationship.target_id):
                relationships.append(relationship)

        # Cache result with simple size management
        if len(self._relationship_cache) >= self._relationship_cache_max_size:
            # Simple eviction: remove one random item to make space
            oldest_key: uuid.UUID = next(iter(self._relationship_cache))
            del self._relationship_cache[oldest_key]

        self._relationship_cache[node_id] = relationships
        return relationships

    def get_all_node_ids(self) -> Set[uuid.UUID]:
        """Get all node IDs in the graph."""
        return set(self._node_index.keys())

    def remove_node_from_memory(self, node_id: uuid.UUID) -> bool:
        """Remove a node from memory."""
        if node_id not in self._node_index:
            return False

        try:
            del self.nodes[node_id]
            del self._node_index[node_id]
            self._relationship_cache.pop(node_id, None)
            logger.debug(f"Removed node {node_id} from memory")
            return True
        except Exception as e:
            logger.error(f"Failed to remove node {node_id} from memory: {e}")
            return False
