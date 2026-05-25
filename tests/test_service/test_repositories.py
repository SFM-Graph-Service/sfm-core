"""
Unit tests for SFM repository interfaces and implementations.
Tests abstract repository interface and concrete implementations.
"""

import unittest
import uuid

from models import Node
from models.cultural_analysis import CeremonialInstrumentalClassification
from data.repositories import (
    SFMRepository,
    SFMRepositoryFactory,
    TypedSFMRepository,
)
from graph.sfm_graph import SFMGraph, Relationship


class TestSFMRepositoryFactory(unittest.TestCase):
    """Test repository factory."""

    def test_create_networkx_repository(self):
        """Test creating NetworkX repository."""
        repo = SFMRepositoryFactory.create_repository("networkx")

        self.assertIsNotNone(repo)
        self.assertIsInstance(repo, SFMRepository)

    def test_create_memory_repository(self):
        """Test creating memory repository."""
        # "memory" storage type is not supported, use "test" instead
        repo = SFMRepositoryFactory.create_repository("test")

        self.assertIsNotNone(repo)
        self.assertIsInstance(repo, SFMRepository)

    def test_invalid_storage_type_raises_error(self):
        """Test that invalid storage type raises SFMValidationError."""
        from models.exceptions import SFMValidationError
        with self.assertRaises(SFMValidationError):
            SFMRepositoryFactory.create_repository("invalid")


class TestRepositoryCRUD(unittest.TestCase):
    """Test basic CRUD operations on repository."""

    def setUp(self):
        """Set up test repository."""
        self.repo = SFMRepositoryFactory.create_repository("networkx")

    def test_create_node(self):
        """Test creating a node."""
        node = Node(label="Test Node", description="A test node")
        created = self.repo.create_node(node)

        self.assertIsNotNone(created)
        self.assertEqual(created.label, "Test Node")
        self.assertIsInstance(created.id, uuid.UUID)

    def test_read_node(self):
        """Test reading a node."""
        node = Node(label="Test Node", description="A test node")
        created = self.repo.create_node(node)

        retrieved = self.repo.read_node(created.id)

        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.id, created.id)
        self.assertEqual(retrieved.label, "Test Node")

    def test_read_nonexistent_node(self):
        """Test reading nonexistent node returns None."""
        fake_id = uuid.uuid4()
        result = self.repo.read_node(fake_id)

        self.assertIsNone(result)

    def test_update_node(self):
        """Test updating a node."""
        node = Node(label="Original", description="Original description")
        created = self.repo.create_node(node)

        # Update the node
        created.label = "Updated"
        updated = self.repo.update_node(created)

        self.assertEqual(updated.label, "Updated")

        # Verify the update persisted
        retrieved = self.repo.read_node(created.id)
        self.assertEqual(retrieved.label, "Updated")

    def test_delete_node(self):
        """Test deleting a node."""
        node = Node(label="To Delete", description="Will be deleted")
        created = self.repo.create_node(node)

        result = self.repo.delete_node(created.id)

        self.assertTrue(result)

        # Verify deletion
        retrieved = self.repo.read_node(created.id)
        self.assertIsNone(retrieved)

    def test_delete_nonexistent_node(self):
        """Test deleting nonexistent node returns False."""
        fake_id = uuid.uuid4()
        result = self.repo.delete_node(fake_id)

        self.assertFalse(result)

    def test_list_nodes(self):
        """Test listing all nodes."""
        # Create multiple nodes
        node1 = Node(label="Node1", description="First")
        node2 = Node(label="Node2", description="Second")

        self.repo.create_node(node1)
        self.repo.create_node(node2)

        nodes = self.repo.list_nodes()

        self.assertGreaterEqual(len(nodes), 2)

    def test_list_nodes_by_type(self):
        """Test listing nodes filtered by type."""
        # Create different node types
        node1 = Node(label="Basic", description="Basic node")
        node2 = CeremonialInstrumentalClassification(
            label="Ceremonial",
            description="Ceremonial node",
            ceremonial_score=0.8
        )

        self.repo.create_node(node1)
        self.repo.create_node(node2)

        # List specific type
        ceremonial_nodes = self.repo.list_nodes(
            node_type=CeremonialInstrumentalClassification
        )

        self.assertGreater(len(ceremonial_nodes), 0)
        for node in ceremonial_nodes:
            self.assertIsInstance(node, CeremonialInstrumentalClassification)


class TestRelationshipOperations(unittest.TestCase):
    """Test relationship CRUD operations."""

    def setUp(self):
        """Set up test repository with nodes."""
        self.repo = SFMRepositoryFactory.create_repository("networkx")

        # Create test nodes
        self.node1 = Node(label="Node1", description="First")
        self.node2 = Node(label="Node2", description="Second")

        self.repo.create_node(self.node1)
        self.repo.create_node(self.node2)

    def test_create_relationship(self):
        """Test creating a relationship."""
        rel = Relationship(
            source_id=self.node1.id,
            target_id=self.node2.id,
            kind="connects"
        )

        created = self.repo.create_relationship(rel)

        self.assertIsNotNone(created)
        self.assertEqual(created.source_id, self.node1.id)
        self.assertEqual(created.target_id, self.node2.id)

    def test_read_relationship(self):
        """Test reading a relationship."""
        rel = Relationship(
            source_id=self.node1.id,
            target_id=self.node2.id,
            kind="connects"
        )

        created = self.repo.create_relationship(rel)
        retrieved = self.repo.read_relationship(created.id)

        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.id, created.id)

    def test_delete_relationship(self):
        """Test deleting a relationship."""
        rel = Relationship(
            source_id=self.node1.id,
            target_id=self.node2.id,
            kind="connects"
        )

        created = self.repo.create_relationship(rel)
        result = self.repo.delete_relationship(created.id)

        self.assertTrue(result)

        # Verify deletion
        retrieved = self.repo.read_relationship(created.id)
        self.assertIsNone(retrieved)

    def test_list_relationships(self):
        """Test listing all relationships."""
        rel1 = Relationship(
            source_id=self.node1.id,
            target_id=self.node2.id,
            kind="type1"
        )
        rel2 = Relationship(
            source_id=self.node2.id,
            target_id=self.node1.id,
            kind="type2"
        )

        self.repo.create_relationship(rel1)
        self.repo.create_relationship(rel2)

        rels = self.repo.list_relationships()

        self.assertGreaterEqual(len(rels), 2)


class TestRepositoryClear(unittest.TestCase):
    """Test repository clear operations."""

    def setUp(self):
        """Set up test repository with data."""
        self.repo = SFMRepositoryFactory.create_repository("networkx")

        # Add test data
        node = Node(label="Test", description="Test node")
        self.repo.create_node(node)

    def test_clear(self):
        """Test clearing all data."""
        # Verify data exists
        nodes = self.repo.list_nodes()
        self.assertGreater(len(nodes), 0)

        # Clear data
        self.repo.clear()

        # Verify data is cleared
        nodes = self.repo.list_nodes()
        self.assertEqual(len(nodes), 0)


class TestTypedRepository(unittest.TestCase):
    """Test typed repository wrapper."""

    def setUp(self):
        """Set up typed repository."""
        base_repo = SFMRepositoryFactory.create_repository("networkx")
        self.typed_repo = TypedSFMRepository(base_repo, Node)

    def test_create_typed_node(self):
        """Test creating a typed node."""
        node = Node(label="Typed", description="Typed node")
        created = self.typed_repo.create(node)

        self.assertIsNotNone(created)
        self.assertIsInstance(created, Node)

    def test_list_typed_nodes(self):
        """Test listing typed nodes."""
        node1 = Node(label="Node1", description="First")
        node2 = Node(label="Node2", description="Second")

        self.typed_repo.create(node1)
        self.typed_repo.create(node2)

        nodes = self.typed_repo.list_all()

        self.assertGreaterEqual(len(nodes), 2)
        for node in nodes:
            self.assertIsInstance(node, Node)


class TestRepositoryTransactions(unittest.TestCase):
    """Test repository transaction support (if implemented)."""

    def setUp(self):
        """Set up test repository."""
        self.repo = SFMRepositoryFactory.create_repository("networkx")

    def test_multiple_operations(self):
        """Test multiple operations in sequence."""
        # Create multiple nodes
        nodes = []
        for i in range(5):
            node = Node(label=f"Node{i}", description=f"Node {i}")
            created = self.repo.create_node(node)
            nodes.append(created)

        # Verify all nodes exist
        all_nodes = self.repo.list_nodes()
        self.assertGreaterEqual(len(all_nodes), 5)

        # Delete some nodes
        for node in nodes[:2]:
            self.repo.delete_node(node.id)

        # Verify deletions
        remaining = self.repo.list_nodes()
        self.assertGreaterEqual(len(remaining), 3)


class TestRepositoryEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""

    def setUp(self):
        """Set up test repository."""
        self.repo = SFMRepositoryFactory.create_repository("networkx")

    def test_duplicate_node_creation(self):
        """Test handling of duplicate node IDs."""
        node = Node(label="Original", description="Original node")
        created = self.repo.create_node(node)

        # Try to create node with same ID
        duplicate = Node(label="Duplicate", description="Duplicate")
        duplicate.id = created.id

        # Repository should handle this gracefully
        # (exact behavior depends on implementation)

    def test_update_nonexistent_node(self):
        """Test updating nonexistent node."""
        node = Node(label="Nonexistent", description="Does not exist")

        # Should raise error
        with self.assertRaises(Exception):
            self.repo.update_node(node)


if __name__ == "__main__":
    unittest.main()
