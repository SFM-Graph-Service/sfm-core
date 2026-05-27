"""
Lookup performance benchmarking tests for SFM Core.

Tests lookup speed for nodes and relationships with various graph sizes.
"""

import pytest
import time
import uuid
from typing import List
from models.base_nodes import Node
from graph.sfm_graph import Relationship
from api.sfm_service import SFMService


class TestNodeLookupPerformance:
    """Test node lookup performance."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = SFMService()

    def create_test_nodes(self, count: int) -> List[Node]:
        """Create test nodes for benchmarking."""
        nodes = []
        for i in range(count):
            node = Node(
                label=f"Node {i}",
                description=f"Test node {i}",
                meta={"index": i}
            )
            created = self.service.create_node(node)
            nodes.append(created)
        return nodes

    def test_lookup_by_id_small_graph(self):
        """Test lookup by ID with 100 nodes."""
        nodes = self.create_test_nodes(100)

        start_time = time.time()
        for node in nodes:
            found_node = self.service.get_node(node.id)
            assert found_node is not None
            assert found_node.id == node.id

        elapsed = time.time() - start_time
        assert elapsed < 1.0
        print(f"\n100 node lookups: {elapsed:.4f}s")

    def test_lookup_by_id_medium_graph(self):
        """Test lookup by ID with 1000 nodes."""
        nodes = self.create_test_nodes(1000)
        sample_nodes = nodes[::10]  # Every 10th node

        start_time = time.time()
        for node in sample_nodes:
            found_node = self.service.get_node(node.id)
            assert found_node is not None

        elapsed = time.time() - start_time
        assert elapsed < 1.0
        print(f"\n100 lookups in 1000-node graph: {elapsed:.4f}s")

    def test_lookup_nonexistent_nodes(self):
        """Test lookup performance for nonexistent nodes."""
        self.create_test_nodes(100)
        nonexistent_ids = [uuid.uuid4() for _ in range(100)]

        start_time = time.time()
        for node_id in nonexistent_ids:
            found_node = self.service.get_node(node_id)
            assert found_node is None

        elapsed = time.time() - start_time
        assert elapsed < 1.0
        print(f"\n100 failed lookups: {elapsed:.4f}s")


class TestRelationshipLookupPerformance:
    """Test relationship lookup performance."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = SFMService()

    def test_relationship_lookup_by_id(self):
        """Test relationship lookup by ID."""
        # Create nodes
        nodes = []
        for i in range(100):
            node = Node(label=f"Node {i}", description="Test")
            created = self.service.create_node(node)
            nodes.append(created)

        # Create relationships
        rels = []
        for i in range(min(100, len(nodes) - 1)):
            rel = Relationship(
                source_id=nodes[i].id,
                target_id=nodes[i + 1].id,
                kind="influences",
                weight=0.5
            )
            created_rel = self.service.create_relationship(rel)
            rels.append(created_rel)

        # Measure lookup time
        start_time = time.time()
        for rel in rels:
            found_rel = self.service.get_relationship(rel.id)
            assert found_rel is not None

        elapsed = time.time() - start_time
        assert elapsed < 1.0
        print(f"\n{len(rels)} relationship lookups: {elapsed:.4f}s")


class TestBulkLookupPerformance:
    """Test bulk lookup operations."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = SFMService()

    def test_bulk_node_retrieval(self):
        """Test retrieving multiple nodes at once."""
        # Create 500 nodes
        for i in range(500):
            node = Node(label=f"Node {i}", description="Test")
            self.service.create_node(node)

        # Measure time to retrieve all nodes
        start_time = time.time()
        all_nodes = []
        for node_id in self.service.repository.graph.nodes():
            node = self.service.get_node(node_id)
            if node:
                all_nodes.append(node)
        elapsed = time.time() - start_time

        assert len(all_nodes) == 500
        assert elapsed < 1.0
        print(f"\nBulk retrieval of 500 nodes: {elapsed:.4f}s")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
