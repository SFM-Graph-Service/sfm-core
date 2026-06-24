"""Change tracking for incremental SFM graph persistence."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
from typing import Dict, Optional, Set


@dataclass
class ChangeTracker:
    """Track graph changes since the last successful save/load."""

    added_nodes: Set[uuid.UUID] = field(default_factory=set)
    modified_nodes: Set[uuid.UUID] = field(default_factory=set)
    deleted_nodes: Set[uuid.UUID] = field(default_factory=set)
    added_relationships: Set[uuid.UUID] = field(default_factory=set)
    modified_relationships: Set[uuid.UUID] = field(default_factory=set)
    deleted_relationships: Set[uuid.UUID] = field(default_factory=set)
    last_save_timestamp: Optional[datetime] = None

    def mark_node_added(self, node_id: uuid.UUID) -> None:
        self.deleted_nodes.discard(node_id)
        self.modified_nodes.discard(node_id)
        self.added_nodes.add(node_id)

    def mark_node_modified(self, node_id: uuid.UUID) -> None:
        if node_id not in self.added_nodes and node_id not in self.deleted_nodes:
            self.modified_nodes.add(node_id)

    def mark_node_deleted(self, node_id: uuid.UUID) -> None:
        if node_id in self.added_nodes:
            self.added_nodes.discard(node_id)
            self.modified_nodes.discard(node_id)
            return
        self.modified_nodes.discard(node_id)
        self.deleted_nodes.add(node_id)

    def mark_relationship_added(self, relationship_id: uuid.UUID) -> None:
        self.deleted_relationships.discard(relationship_id)
        self.modified_relationships.discard(relationship_id)
        self.added_relationships.add(relationship_id)

    def mark_relationship_modified(self, relationship_id: uuid.UUID) -> None:
        if relationship_id not in self.added_relationships and relationship_id not in self.deleted_relationships:
            self.modified_relationships.add(relationship_id)

    def mark_relationship_deleted(self, relationship_id: uuid.UUID) -> None:
        if relationship_id in self.added_relationships:
            self.added_relationships.discard(relationship_id)
            self.modified_relationships.discard(relationship_id)
            return
        self.modified_relationships.discard(relationship_id)
        self.deleted_relationships.add(relationship_id)

    def has_changes(self) -> bool:
        return any(
            (
                self.added_nodes,
                self.modified_nodes,
                self.deleted_nodes,
                self.added_relationships,
                self.modified_relationships,
                self.deleted_relationships,
            )
        )

    def summary(self) -> Dict[str, int]:
        return {
            "nodes_added": len(self.added_nodes),
            "nodes_modified": len(self.modified_nodes),
            "nodes_deleted": len(self.deleted_nodes),
            "relationships_added": len(self.added_relationships),
            "relationships_modified": len(self.modified_relationships),
            "relationships_deleted": len(self.deleted_relationships),
        }

    def clear(self) -> None:
        self.added_nodes.clear()
        self.modified_nodes.clear()
        self.deleted_nodes.clear()
        self.added_relationships.clear()
        self.modified_relationships.clear()
        self.deleted_relationships.clear()
        self.last_save_timestamp = datetime.now(timezone.utc)
