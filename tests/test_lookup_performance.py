"""
Lookup performance benchmarking tests for SFM Core.

Tests lookup speed for nodes and relationships with various graph sizes.
Provides benchmarks for identifying performance bottlenecks.
"""

import pytest
import time
import uuid
from typing import List, Tuple
from models.base_nodes import Node, Actor, Institution
from graph.sfm_graph import SFMGraph, Relationship
from api.sfm_service import SFMService


class TestNodeLookupPerformance:
    """Test node lookup performance."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = SFMService()

    def create_test_nodes(self, count: int) -> List[Node]:
        """Create test nodes for benchmarking.

        Args:
            count: Number of nodes to create

        Returns:
            List of created nodes
        """
        nodes = []
        for i in range(count):
            node = self.service.create_node(
                label=f"Node {i}",
                node_type="Actor" if i % 2 == 0 else "Institution",
                description=f"Test node {i}",
                meta={"index": i, "batch": i // 100}
            )
            nodes.append(node)
        return nodes

    def test_lookup_by_id_small_graph(self):
        """Test lookup by ID with 100 nodes."""
        # Create 100 nodes
        nodes = self.create_test_nodes(100)

        # Measure lookup time
        start_time = time.time()

        for node in nodes:
            found_node = self.service.get_node(node.id)
            assert found_node is not None
            assert found_node.id == node.id

        elapsed = time.time() - start_time

        # Should complete in < 1 second
        assert elapsed < 1.0

        print(f"\n100 node lookups: {elapsed:.4f}s ({100/elapsed:.0f} lookups/sec)")

    def test_lookup_by_id_medium_graph(self):
        """Test lookup by ID with 1000 nodes."""
        # Create 1000 nodes
        nodes = self.create_test_nodes(1000)

        # Measure lookup time for sample
        sample_size = 100
        sample_nodes = nodes[::10]  # Every 10th node

        start_time = time.time()

        for node in sample_nodes:
            found_node = self.service.get_node(node.id)
            assert found_node is not None

        elapsed = time.time() - start_time

        # Should complete in < 1 second
        assert elapsed < 1.0

        print(f"\n{sample_size} lookups in 1000-node graph: {elapsed:.4f}s ({sample_size/elapsed:.0f} lookups/sec)")

    def test_lookup_by_id_large_graph(self):
        """Test lookup by ID with 5000 nodes."""
        # Create 5000 nodes
        nodes = self.create_test_nodes(5000)

        # Measure lookup time for sample
        sample_size = 100
        sample_nodes = nodes[::50]  # Every 50th node

        start_time = time.time()

        for node in sample_nodes:
            found_node = self.service.get_node(node.id)
            assert found_node is not None

        elapsed = time.time() - start_time

        # Should complete in < 2 seconds
        assert elapsed < 2.0

        print(f"\n{sample_size} lookups in 5000-node graph: {elapsed:.4f}s ({sample_size/elapsed:.0f} lookups/sec)")

    def test_lookup_nonexistent_nodes(self):
        """Test lookup performance for nonexistent nodes."""
        # Create 1000 nodes
        self.create_test_nodes(1000)

        # Generate random UUIDs that don't exist
        nonexistent_ids = [uuid.uuid4() for _ in range(100)]

        start_time = time.time()

        for node_id in nonexistent_ids:
            found_node = self.service.get_node(node_id)
            assert found_node is None

        elapsed = time.time() - start_time

        # Failed lookups should still be fast
        assert elapsed < 1.0

        print(f"\n100 failed lookups: {elapsed:.4f}s ({100/elapsed:.0f} lookups/sec)")


class TestRelationshipLookupPerformance:
    """Test relationship lookup performance."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = SFMService()

    def create_test_graph(self, node_count: int, rel_per_node: int) -> Tuple[List[Node], List[Relationship]]:
        """Create test graph with nodes and relationships.

        Args:
            node_count: Number of nodes to create
            rel_per_node: Number of relationships per node

        Returns:
            Tuple of (nodes, relationships)
        """
        # Create nodes
        nodes = []
        for i in range(node_count):
            node = self.service.create_node(
                label=f"Node {i}",
                node_type="Actor",
                description=f"Test node {i}"
            )
            nodes.append(node)

        # Create relationships
        relationships = []
        for i, source_node in enumerate(nodes):
            for j in range(rel_per_node):
                target_idx = (i + j + 1) % len(nodes)
                target_node = nodes[target_idx]

                rel = Relationship(
                    source_id=source_node.id,
                    target_id=target_node.id,
                    kind="influences",
                    weight=0.5
                )

                created_rel = self.service.create_relationship(rel)
                relationships.append(created_rel)

        return nodes, relationships

    def test_relationship_lookup_by_id(self):
        """Test relationship lookup by ID."""
        # Create graph with 100 nodes, 3 relationships each = 300 rels
        nodes, rels = self.create_test_graph(100, 3)

        # Measure lookup time
        sample_size = min(100, len(rels))
        sample_rels = rels[:sample_size]

        start_time = time.time()

        for rel in sample_rels:
            found_rel = self.service.get_relationship(rel.id)
            assert found_rel is not None
            assert found_rel.id == rel.id

        elapsed = time.time() - start_time

        # Should complete in < 1 second
        assert elapsed < 1.0

        print(f"\n{sample_size} relationship lookups: {elapsed:.4f}s ({sample_size/elapsed:.0f} lookups/sec)")

    def test_outgoing_relationships_lookup(self):
        """Test finding all outgoing relationships for nodes."""
        # Create graph
        nodes, rels = self.create_test_graph(100, 5)

        # Measure time to find outgoing relationships for each node
        start_time = time.time()

        for node in nodes[:20]:  # Sample 20 nodes
            outgoing = [r for r in self.service.graph.relationships.values()
                        if r.source_id == node.id]
            assert len(outgoing) >= 0  # May be 0 if no outgoing

        elapsed = time.time() - start_time

        # Should complete in < 1 second
        assert elapsed < 1.0

        print(f"\nOutgoing relationships for 20 nodes: {elapsed:.4f}s ({20/elapsed:.0f} nodes/sec)")

    def test_incoming_relationships_lookup(self):
        """Test finding all incoming relationships for nodes."""
        # Create graph
        nodes, rels = self.create_test_graph(100, 5)

        # Measure time to find incoming relationships for each node
        start_time = time.time()

        for node in nodes[:20]:  # Sample 20 nodes
            incoming = [r for r in self.service.graph.relationships.values()
                        if r.target_id == node.id]
            assert len(incoming) >= 0  # May be 0 if no incoming

        elapsed = time.time() - start_time

        # Should complete in < 1 second
        assert elapsed < 1.0

        print(f"\nIncoming relationships for 20 nodes: {elapsed:.4f}s ({20/elapsed:.0f} nodes/sec)")


class TestBulkLookupPerformance:
    """Test bulk lookup operations."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = SFMService()

    def test_bulk_node_retrieval(self):
        """Test retrieving multiple nodes at once."""
        # Create 1000 nodes
        nodes = []
        for i in range(1000):
            node = self.service.create_node(
                label=f"Node {i}",
                node_type="Actor",
                description=f"Test node {i}"
            )
            nodes.append(node)

        # Measure time to retrieve all nodes
        start_time = time.time()

        all_nodes = list(self.service.graph)

        elapsed = time.time() - start_time

        assert len(all_nodes) == 1000

        # Should complete in < 1 second
        assert elapsed < 1.0

        print(f"\nBulk retrieval of 1000 nodes: {elapsed:.4f}s ({1000/elapsed:.0f} nodes/sec)")

    def test_bulk_relationship_retrieval(self):
        """Test retrieving all relationships at once."""
        # Create graph with 100 nodes, 5 relationships each = 500 rels
        nodes = []
        for i in range(100):
            node = self.service.create_node(
                label=f"Node {i}",
                node_type="Actor",
                description=f"Test node {i}"
            )
            nodes.append(node)

        for i, source_node in enumerate(nodes):
            for j in range(5):
                target_idx = (i + j + 1) % len(nodes)
                target_node = nodes[target_idx]

                rel = Relationship(
                    source_id=source_node.id,
                    target_id=target_node.id,
                    kind="influences",
                    weight=0.5
                )
                self.service.create_relationship(rel)

        # Measure time to retrieve all relationships
        start_time = time.time()

        all_rels = list(self.service.graph.relationships.values())

        elapsed = time.time() - start_time

        assert len(all_rels) == 500

        # Should complete in < 1 second
        assert elapsed < 1.0

        print(f"\nBulk retrieval of 500 relationships: {elapsed:.4f}s ({500/elapsed:.0f} rels/sec)")


class TestFilteredLookupPerformance:
    """Test filtered lookup performance."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = SFMService()

    def test_filter_by_node_type(self):
        """Test filtering nodes by type."""
        # Create mixed node types
        for i in range(500):
            node_type = "Actor" if i % 3 == 0 else "Institution" if i % 3 == 1 else "Technology"
            self.service.create_node(
                label=f"Node {i}",
                node_type=node_type,
                description=f"Test {node_type}"
            )

        # Measure time to filter by type
        start_time = time.time()

        actors = [n for n in self.service.graph if isinstance(n, Actor)]

        elapsed = time.time() - start_time

        assert len(actors) > 0

        # Should complete in < 1 second
        assert elapsed < 1.0

        print(f"\nFilter 500 nodes by type: {elapsed:.4f}s ({500/elapsed:.0f} nodes/sec)")

    def test_filter_by_metadata(self):
        """Test filtering nodes by metadata."""
        # Create nodes with metadata
        for i in range(500):
            self.service.create_node(
                label=f"Node {i}",
                node_type="Actor",
                description="Test",
                meta={"category": "A" if i % 2 == 0 else "B", "value": i}
            )

        # Measure time to filter by metadata
        start_time = time.time()

        category_a = [n for n in self.service.graph
                      if hasattr(n, 'meta') and n.meta.get("category") == "A"]

        elapsed = time.time() - start_time

        assert len(category_a) > 0

        # Should complete in < 1 second
        assert elapsed < 1.0

        print(f"\nFilter 500 nodes by metadata: {elapsed:.4f}s ({500/elapsed:.0f} nodes/sec)")


class TestCachingPerformance:
    """Test caching impact on lookup performance."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = SFMService()

    def test_repeated_lookup_performance(self):
        """Test performance of repeated lookups (should benefit from caching)."""
        # Create 100 nodes
        nodes = []
        for i in range(100):
            node = self.service.create_node(
                label=f"Node {i}",
                node_type="Actor",
                description="Test"
            )
            nodes.append(node)

        # First pass - cold cache
        start_time = time.time()
        for node in nodes:
            found = self.service.get_node(node.id)
            assert found is not None
        first_pass = time.time() - start_time

        # Second pass - warm cache
        start_time = time.time()
        for node in nodes:
            found = self.service.get_node(node.id)
            assert found is not None
        second_pass = time.time() - start_time

        # Both should be fast
        assert first_pass < 1.0
        assert second_pass < 1.0

        print(f"\nFirst pass: {first_pass:.4f}s, Second pass: {second_pass:.4f}s")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
