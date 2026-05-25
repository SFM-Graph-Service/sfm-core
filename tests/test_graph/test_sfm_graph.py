"""
Unit tests for SFMGraph class - Graph structure and network representation.

Tests the SFMGraph class for proper node and relationship management,
caching, and core graph operations using sfm_core.models.
"""

import unittest
import uuid
from typing import List
from datetime import datetime

from models.base_nodes import Node
from models.matrix_components import MatrixCell
from models.system_analysis import SystemProperty
from graph.sfm_graph import SFMGraph, NetworkMetrics, Relationship


class TestNetworkMetrics(unittest.TestCase):
    """Test suite for NetworkMetrics dataclass."""

    def test_network_metrics_creation(self):
        """Test NetworkMetrics initialization."""
        metrics = NetworkMetrics(
            id=uuid.uuid4(),
            label="Test Metrics",
            centrality_measures={"betweenness": 0.5, "closeness": 0.3},
            clustering_coefficient=0.7,
            community_assignment="community_1"
        )

        self.assertIsInstance(metrics, Node)
        self.assertIsInstance(metrics.centrality_measures, dict)
        self.assertEqual(metrics.centrality_measures["betweenness"], 0.5)
        self.assertEqual(metrics.clustering_coefficient, 0.7)
        self.assertEqual(metrics.community_assignment, "community_1")

    def test_network_metrics_defaults(self):
        """Test NetworkMetrics with default values."""
        metrics = NetworkMetrics(
            id=uuid.uuid4(),
            label="Default Metrics"
        )

        self.assertEqual(len(metrics.centrality_measures), 0)
        self.assertIsNone(metrics.clustering_coefficient)
        self.assertIsNone(metrics.community_assignment)

    def test_network_metrics_path_lengths(self):
        """Test NetworkMetrics with path lengths."""
        node_id = uuid.uuid4()
        target_id = uuid.uuid4()

        metrics = NetworkMetrics(
            id=node_id,
            label="Path Metrics",
            path_lengths={target_id: 2.5}
        )

        self.assertIn(target_id, metrics.path_lengths)
        self.assertEqual(metrics.path_lengths[target_id], 2.5)


class TestRelationship(unittest.TestCase):
    """Test suite for Relationship class."""

    def test_relationship_creation(self):
        """Test Relationship initialization."""
        source_id = uuid.uuid4()
        target_id = uuid.uuid4()

        rel = Relationship(
            source_id=source_id,
            target_id=target_id,
            kind="GOVERNS",
            weight=0.8
        )

        self.assertIsInstance(rel.id, uuid.UUID)
        self.assertEqual(rel.source_id, source_id)
        self.assertEqual(rel.target_id, target_id)
        self.assertEqual(rel.kind, "GOVERNS")
        self.assertEqual(rel.weight, 0.8)

    def test_relationship_defaults(self):
        """Test Relationship with default values."""
        rel = Relationship(
            source_id=uuid.uuid4(),
            target_id=uuid.uuid4()
        )

        self.assertIsInstance(rel.id, uuid.UUID)
        self.assertEqual(rel.kind, "")
        self.assertIsNone(rel.weight)
        self.assertEqual(len(rel.meta), 0)

    def test_relationship_with_metadata(self):
        """Test Relationship with metadata."""
        rel = Relationship(
            source_id=uuid.uuid4(),
            target_id=uuid.uuid4(),
            kind="INFLUENCES",
            meta={"strength": "strong", "type": "direct"}
        )

        self.assertEqual(rel.meta["strength"], "strong")
        self.assertEqual(rel.meta["type"], "direct")


class TestSFMGraph(unittest.TestCase):
    """Test suite for SFMGraph class."""

    def setUp(self):
        """Set up test fixtures."""
        self.graph = SFMGraph(
            name="Test Graph",
            description="Test SFM Graph"
        )

    def test_graph_initialization(self):
        """Test SFMGraph initialization."""
        self.assertIsInstance(self.graph.id, uuid.UUID)
        self.assertEqual(self.graph.name, "Test Graph")
        self.assertEqual(self.graph.description, "Test SFM Graph")
        self.assertEqual(len(self.graph.nodes), 0)
        self.assertEqual(len(self.graph.relationships), 0)
        self.assertEqual(self.graph.version, 1)
        self.assertIsInstance(self.graph.created_at, datetime)

    def test_add_node(self):
        """Test adding a node to the graph."""
        node = MatrixCell(
            id=uuid.uuid4(),
            label="Test Cell",
            description="Test matrix cell"
        )

        result = self.graph.add_node(node)

        self.assertEqual(result, node)
        self.assertEqual(len(self.graph.nodes), 1)
        self.assertIn(node.id, self.graph.nodes)
        self.assertEqual(self.graph.nodes[node.id], node)

    def test_add_multiple_nodes(self):
        """Test adding multiple nodes."""
        nodes = [
            MatrixCell(id=uuid.uuid4(), label=f"Cell {i}")
            for i in range(5)
        ]

        for node in nodes:
            self.graph.add_node(node)

        self.assertEqual(len(self.graph.nodes), 5)
        for node in nodes:
            self.assertIn(node.id, self.graph.nodes)

    def test_add_relationship(self):
        """Test adding a relationship to the graph."""
        source = MatrixCell(id=uuid.uuid4(), label="Source")
        target = MatrixCell(id=uuid.uuid4(), label="Target")

        self.graph.add_node(source)
        self.graph.add_node(target)

        rel = Relationship(
            source_id=source.id,
            target_id=target.id,
            kind="CONNECTS",
            weight=0.7
        )

        result = self.graph.add_relationship(rel)

        self.assertEqual(result, rel)
        self.assertEqual(len(self.graph.relationships), 1)
        self.assertIn(rel.id, self.graph.relationships)

    def test_get_node_by_id(self):
        """Test retrieving a node by ID."""
        node = SystemProperty(
            id=uuid.uuid4(),
            label="Test Property",
            property_name="test_prop"
        )

        self.graph.add_node(node)
        retrieved = self.graph.get_node_by_id(node.id)

        self.assertEqual(retrieved, node)
        self.assertEqual(retrieved.label, "Test Property")

    def test_get_node_by_id_not_found(self):
        """Test retrieving a non-existent node."""
        non_existent_id = uuid.uuid4()
        result = self.graph.get_node_by_id(non_existent_id)

        self.assertIsNone(result)

    def test_get_node_relationships(self):
        """Test retrieving relationships for a node."""
        source = MatrixCell(id=uuid.uuid4(), label="Source")
        target1 = MatrixCell(id=uuid.uuid4(), label="Target 1")
        target2 = MatrixCell(id=uuid.uuid4(), label="Target 2")

        self.graph.add_node(source)
        self.graph.add_node(target1)
        self.graph.add_node(target2)

        rel1 = Relationship(source_id=source.id, target_id=target1.id, kind="R1")
        rel2 = Relationship(source_id=source.id, target_id=target2.id, kind="R2")
        rel3 = Relationship(source_id=target1.id, target_id=source.id, kind="R3")

        self.graph.add_relationship(rel1)
        self.graph.add_relationship(rel2)
        self.graph.add_relationship(rel3)

        relationships = self.graph.get_node_relationships(source.id)

        self.assertEqual(len(relationships), 3)
        self.assertIn(rel1, relationships)
        self.assertIn(rel2, relationships)
        self.assertIn(rel3, relationships)

    def test_relationship_caching(self):
        """Test that relationship retrieval uses caching."""
        node = MatrixCell(id=uuid.uuid4(), label="Test Node")
        self.graph.add_node(node)

        rel = Relationship(
            source_id=node.id,
            target_id=uuid.uuid4(),
            kind="TEST"
        )
        self.graph.add_relationship(rel)

        # First call should cache
        relationships1 = self.graph.get_node_relationships(node.id)

        # Second call should use cache
        relationships2 = self.graph.get_node_relationships(node.id)

        self.assertEqual(relationships1, relationships2)
        self.assertIn(node.id, self.graph._relationship_cache)

    def test_relationship_cache_invalidation(self):
        """Test that cache is cleared when relationships change."""
        node = MatrixCell(id=uuid.uuid4(), label="Test Node")
        self.graph.add_node(node)

        rel1 = Relationship(source_id=node.id, target_id=uuid.uuid4(), kind="R1")
        self.graph.add_relationship(rel1)

        # Cache is populated
        self.graph.get_node_relationships(node.id)
        self.assertIn(node.id, self.graph._relationship_cache)

        # Adding new relationship should clear cache
        rel2 = Relationship(source_id=node.id, target_id=uuid.uuid4(), kind="R2")
        self.graph.add_relationship(rel2)

        self.assertEqual(len(self.graph._relationship_cache), 0)

    def test_get_all_node_ids(self):
        """Test retrieving all node IDs."""
        nodes = [
            MatrixCell(id=uuid.uuid4(), label=f"Node {i}")
            for i in range(3)
        ]

        for node in nodes:
            self.graph.add_node(node)

        node_ids = self.graph.get_all_node_ids()

        self.assertEqual(len(node_ids), 3)
        for node in nodes:
            self.assertIn(node.id, node_ids)

    def test_remove_node_from_memory(self):
        """Test removing a node from memory."""
        node = MatrixCell(id=uuid.uuid4(), label="Test Node")
        self.graph.add_node(node)

        result = self.graph.remove_node_from_memory(node.id)

        self.assertTrue(result)
        self.assertNotIn(node.id, self.graph.nodes)
        self.assertNotIn(node.id, self.graph._node_index)

    def test_remove_nonexistent_node(self):
        """Test removing a node that doesn't exist."""
        non_existent_id = uuid.uuid4()
        result = self.graph.remove_node_from_memory(non_existent_id)

        self.assertFalse(result)

    def test_remove_node_clears_cache(self):
        """Test that removing a node clears its relationship cache."""
        node = MatrixCell(id=uuid.uuid4(), label="Test Node")
        self.graph.add_node(node)

        rel = Relationship(source_id=node.id, target_id=uuid.uuid4(), kind="TEST")
        self.graph.add_relationship(rel)

        # Populate cache
        self.graph.get_node_relationships(node.id)
        self.assertIn(node.id, self.graph._relationship_cache)

        # Remove node
        self.graph.remove_node_from_memory(node.id)

        self.assertNotIn(node.id, self.graph._relationship_cache)

    def test_graph_iteration(self):
        """Test iterating over graph nodes."""
        nodes = [
            MatrixCell(id=uuid.uuid4(), label=f"Node {i}")
            for i in range(5)
        ]

        for node in nodes:
            self.graph.add_node(node)

        iterated_nodes = list(self.graph)

        self.assertEqual(len(iterated_nodes), 5)
        for node in nodes:
            self.assertIn(node, iterated_nodes)

    def test_graph_length(self):
        """Test graph length operator."""
        self.assertEqual(len(self.graph), 0)

        for i in range(10):
            node = MatrixCell(id=uuid.uuid4(), label=f"Node {i}")
            self.graph.add_node(node)

        self.assertEqual(len(self.graph), 10)

    def test_clear_graph(self):
        """Test clearing all nodes and relationships."""
        nodes = [MatrixCell(id=uuid.uuid4(), label=f"Node {i}") for i in range(3)]
        for node in nodes:
            self.graph.add_node(node)

        rel = Relationship(
            source_id=nodes[0].id,
            target_id=nodes[1].id,
            kind="TEST"
        )
        self.graph.add_relationship(rel)

        self.graph.clear()

        self.assertEqual(len(self.graph.nodes), 0)
        self.assertEqual(len(self.graph.relationships), 0)
        self.assertEqual(len(self.graph._node_index), 0)
        self.assertEqual(len(self.graph._relationship_cache), 0)

    def test_node_index_consistency(self):
        """Test that _node_index stays consistent with nodes dict."""
        node = MatrixCell(id=uuid.uuid4(), label="Test Node")
        self.graph.add_node(node)

        # Both should contain the node
        self.assertIn(node.id, self.graph.nodes)
        self.assertIn(node.id, self.graph._node_index)
        self.assertEqual(self.graph.nodes[node.id], self.graph._node_index[node.id])

        # After removal, both should be empty
        self.graph.remove_node_from_memory(node.id)
        self.assertNotIn(node.id, self.graph.nodes)
        self.assertNotIn(node.id, self.graph._node_index)

    def test_relationship_cache_size_limit(self):
        """Test that relationship cache respects size limit."""
        # Create many nodes
        nodes = [MatrixCell(id=uuid.uuid4(), label=f"Node {i}") for i in range(1100)]
        for node in nodes:
            self.graph.add_node(node)

        # Create relationships and trigger caching for > max_size nodes
        for i in range(1100):
            rel = Relationship(
                source_id=nodes[i].id,
                target_id=nodes[(i + 1) % 1100].id,
                kind="TEST"
            )
            self.graph.add_relationship(rel)

        # Populate cache for all nodes
        for node in nodes:
            self.graph.get_node_relationships(node.id)

        # Cache should respect max size
        self.assertLessEqual(
            len(self.graph._relationship_cache),
            self.graph._relationship_cache_max_size
        )


class TestSFMGraphMetadata(unittest.TestCase):
    """Test suite for SFMGraph metadata and versioning."""

    def test_graph_versioning(self):
        """Test graph version management."""
        graph = SFMGraph(name="Versioned Graph", version=1)

        self.assertEqual(graph.version, 1)

    def test_graph_timestamps(self):
        """Test graph timestamp management."""
        graph = SFMGraph(name="Timestamped Graph")

        self.assertIsInstance(graph.created_at, datetime)
        self.assertIsNone(graph.modified_at)

    def test_graph_quality_metadata(self):
        """Test graph data quality metadata."""
        graph = SFMGraph(
            name="Quality Graph",
            data_quality="high"
        )

        self.assertEqual(graph.data_quality, "high")

    def test_graph_previous_version(self):
        """Test graph previous version tracking."""
        previous_id = uuid.uuid4()
        graph = SFMGraph(
            name="New Version Graph",
            version=2,
            previous_version_id=previous_id
        )

        self.assertEqual(graph.version, 2)
        self.assertEqual(graph.previous_version_id, previous_id)


if __name__ == "__main__":
    unittest.main()
