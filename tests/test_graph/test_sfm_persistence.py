"""
Unit tests for SFM graph persistence.
Tests serialization, deserialization, and storage of Beta unified model graphs.
"""

import tempfile
import unittest
import uuid
from pathlib import Path

from models import Node
from models.cultural_analysis import CeremonialInstrumentalClassification
from models.system_analysis import InstitutionalHolarchy
from graph.sfm_graph import SFMGraph, Relationship
from graph.sfm_persistence import (
    StorageFormat,
    GraphMetadata,
    SFMPersistenceManager,
)


class TestStorageFormat(unittest.TestCase):
    """Test storage format enum."""

    def test_format_values(self):
        """Test storage format enum values."""
        self.assertEqual(StorageFormat.JSON.value, "json")
        self.assertEqual(StorageFormat.PICKLE.value, "pickle")
        self.assertEqual(StorageFormat.COMPRESSED_JSON.value, "json.gz")
        self.assertEqual(StorageFormat.COMPRESSED_PICKLE.value, "pickle.gz")


class TestGraphMetadata(unittest.TestCase):
    """Test graph metadata dataclass."""

    def test_metadata_creation(self):
        """Test metadata creation."""
        metadata = GraphMetadata(
            graph_id="test_id",
            label="Test Graph",
            version=1,
            node_count=10,
            relationship_count=15,
            format=StorageFormat.JSON,
            checksum="abc123"
        )

        self.assertEqual(metadata.version, 1)
        self.assertEqual(metadata.node_count, 10)
        self.assertEqual(metadata.relationship_count, 15)
        self.assertEqual(metadata.format, StorageFormat.JSON)


class TestSFMPersistenceManager(unittest.TestCase):
    """Test persistence manager class."""

    def setUp(self):
        """Set up persistence manager and test graph."""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = SFMPersistenceManager(storage_dir=Path(self.temp_dir))

        self.graph = SFMGraph()
        self.node = Node(label="Test", description="Test node")
        self.graph.add_node(self.node)

    def test_manager_initialization(self):
        """Test manager initialization."""
        self.assertIsNotNone(self.manager)
        self.assertEqual(self.manager.storage_dir, Path(self.temp_dir))

    def test_manager_save(self):
        """Test manager save operation."""
        graph_id = self.manager.save(self.graph, label="test_graph")

        self.assertIsInstance(graph_id, str)

        # Verify file exists
        files = list(Path(self.temp_dir).glob("*.json"))
        self.assertGreater(len(files), 0)

    def test_manager_load(self):
        """Test manager load operation."""
        graph_id = self.manager.save(self.graph, label="test_graph")
        loaded = self.manager.load(graph_id)

        self.assertIsInstance(loaded, SFMGraph)
        self.assertEqual(len(list(loaded)), 1)

    def test_manager_list(self):
        """Test manager list operation."""
        self.manager.save(self.graph, label="graph1")
        self.manager.save(self.graph, label="graph2")

        saved_graphs = self.manager.list_saved_graphs()

        self.assertIsInstance(saved_graphs, list)
        self.assertGreaterEqual(len(saved_graphs), 2)

    def test_manager_delete(self):
        """Test manager delete operation."""
        graph_id = self.manager.save(self.graph, label="to_delete")

        result = self.manager.delete(graph_id)
        self.assertTrue(result)

        # Verify file is deleted
        with self.assertRaises(FileNotFoundError):
            self.manager.load(graph_id)


class TestComplexGraphPersistence(unittest.TestCase):
    """Test persistence with complex graphs."""

    def setUp(self):
        """Set up complex test graph."""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = SFMPersistenceManager(storage_dir=Path(self.temp_dir))

        self.graph = SFMGraph()

        # Add various node types
        self.node1 = Node(label="Node1", description="First node")
        self.node2 = CeremonialInstrumentalClassification(
            label="Ceremonial",
            description="Ceremonial node",
            ceremonial_score=0.8,
            instrumental_score=0.2
        )
        self.node3 = InstitutionalHolarchy(
            label="Institution",
            description="Institutional node"
        )

        self.graph.add_node(self.node1)
        self.graph.add_node(self.node2)
        self.graph.add_node(self.node3)

        # Add relationships
        self.rel1 = Relationship(
            source_id=self.node1.id,
            target_id=self.node2.id,
            kind="flows_to"
        )
        self.graph.add_relationship(self.rel1)

    def test_save_and_load_complex_graph(self):
        """Test saving and loading graph with multiple node types."""
        graph_id = self.manager.save(self.graph, label="complex_graph")
        loaded = self.manager.load(graph_id)

        self.assertIsInstance(loaded, SFMGraph)
        self.assertEqual(len(list(loaded)), 3)
        self.assertEqual(len(loaded.relationships), 1)

    def test_node_type_preservation(self):
        """Test that node types are preserved during persistence."""
        graph_id = self.manager.save(self.graph, label="type_test")
        loaded = self.manager.load(graph_id)

        # Check node types are preserved
        nodes = list(loaded)
        node_types = [type(node).__label__ for node in nodes]

        self.assertIn("Node", node_types)
        self.assertIn("CeremonialInstrumentalClassification", node_types)
        self.assertIn("InstitutionalHolarchy", node_types)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""

    def setUp(self):
        """Set up test manager."""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = SFMPersistenceManager(storage_dir=Path(self.temp_dir))

    def test_empty_graph_persistence(self):
        """Test persisting empty graph."""
        graph = SFMGraph()
        graph_id = self.manager.save(graph, label="empty_graph")

        loaded = self.manager.load(graph_id)
        self.assertEqual(len(list(loaded)), 0)

    def test_large_graph_persistence(self):
        """Test persisting large graph."""
        graph = SFMGraph()

        # Add many nodes
        for i in range(100):
            node = Node(label=f"Node{i}", description=f"Node {i}")
            graph.add_node(node)

        graph_id = self.manager.save(graph, label="large_graph")
        loaded = self.manager.load(graph_id)

        self.assertEqual(len(list(loaded)), 100)

    def test_load_nonexistent_graph(self):
        """Test loading nonexistent graph raises error."""
        with self.assertRaises(FileNotFoundError):
            self.manager.load("nonexistent_id")


if __name__ == "__main__":
    unittest.main()
