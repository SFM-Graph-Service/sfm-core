"""
Unit and integration tests for SFM Service.
Tests the service facade for Beta unified model operations including Phase 2 query methods.
"""

import unittest
import uuid
from unittest.mock import Mock, patch

from models import Node
from models.exceptions import (
    SFMError,
    SFMValidationError,
    SFMNotFoundError,
    NodeCreationError,
)
from models.cultural_analysis import CeremonialInstrumentalClassification
from models.system_analysis import InstitutionalHolarchy
from api.sfm_service import (
    SFMService,
    SFMServiceConfig,
    ServiceHealth,
    GraphStatistics,
)
from data.repositories import SFMRepositoryFactory
from graph.sfm_graph import Relationship


class TestSFMServiceConfig(unittest.TestCase):
    """Test service configuration."""

    def test_default_config(self):
        """Test default configuration values."""
        config = SFMServiceConfig()

        self.assertEqual(config.storage_type, "networkx")
        self.assertEqual(config.graph_size_limit, 10000)

    def test_custom_config(self):
        """Test custom configuration."""
        config = SFMServiceConfig(
            storage_type="memory",
            graph_size_limit=5000
        )

        self.assertEqual(config.storage_type, "memory")
        self.assertEqual(config.graph_size_limit, 5000)


class TestServiceHealth(unittest.TestCase):
    """Test ServiceHealth dataclass."""

    def test_health_creation(self):
        """Test health status creation."""
        health = ServiceHealth(
            status="healthy",
            node_count=100,
            relationship_count=150
        )

        self.assertEqual(health.status, "healthy")
        self.assertEqual(health.node_count, 100)
        self.assertEqual(health.relationship_count, 150)


class TestGraphStatistics(unittest.TestCase):
    """Test GraphStatistics dataclass."""

    def test_statistics_creation(self):
        """Test statistics creation."""
        stats = GraphStatistics(
            total_nodes=50,
            total_relationships=75,
            node_types={"Node": 30, "Actor": 20}
        )

        self.assertEqual(stats.total_nodes, 50)
        self.assertEqual(stats.total_relationships, 75)
        self.assertEqual(stats.node_types["Node"], 30)


class TestSFMServiceInitialization(unittest.TestCase):
    """Test service initialization."""

    def test_default_initialization(self):
        """Test service initialization with defaults."""
        service = SFMService()

        self.assertIsNotNone(service)
        self.assertIsNotNone(service.repository)
        self.assertIsNotNone(service.config)

    def test_custom_config_initialization(self):
        """Test service initialization with custom config."""
        config = SFMServiceConfig(storage_type="networkx")
        service = SFMService(config=config)

        self.assertEqual(service.config.storage_type, "networkx")


class TestNodeOperations(unittest.TestCase):
    """Test basic node CRUD operations."""

    def setUp(self):
        """Set up test service."""
        self.service = SFMService()

    def test_create_node(self):
        """Test creating a node."""
        node = Node(label="Test Node", description="A test node")
        created = self.service.create_node(node)

        self.assertIsNotNone(created)
        self.assertEqual(created.label, "Test Node")
        self.assertIsInstance(created.id, uuid.UUID)

    def test_get_node(self):
        """Test retrieving a node."""
        node = Node(label="Test Node", description="A test node")
        created = self.service.create_node(node)

        retrieved = self.service.get_node(created.id)

        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.id, created.id)
        self.assertEqual(retrieved.label, "Test Node")

    def test_get_nonexistent_node(self):
        """Test retrieving nonexistent node returns None."""
        fake_id = uuid.uuid4()
        result = self.service.get_node(fake_id)

        self.assertIsNone(result)

    def test_update_node(self):
        """Test updating a node."""
        node = Node(label="Original", description="Original description")
        created = self.service.create_node(node)

        # Update the node
        created.label = "Updated"
        updated = self.service.update_node(created)

        self.assertEqual(updated.label, "Updated")

        # Verify the update persisted
        retrieved = self.service.get_node(created.id)
        self.assertEqual(retrieved.label, "Updated")

    def test_delete_node(self):
        """Test deleting a node."""
        node = Node(label="To Delete", description="Will be deleted")
        created = self.service.create_node(node)

        result = self.service.delete_node(created.id)

        self.assertTrue(result)

        # Verify deletion
        retrieved = self.service.get_node(created.id)
        self.assertIsNone(retrieved)

    def test_delete_nonexistent_node(self):
        """Test deleting nonexistent node."""
        fake_id = uuid.uuid4()
        result = self.service.delete_node(fake_id)

        self.assertFalse(result)

    def test_list_nodes(self):
        """Test listing all nodes."""
        # Create multiple nodes
        node1 = Node(label="Node1", description="First")
        node2 = Node(label="Node2", description="Second")

        self.service.create_node(node1)
        self.service.create_node(node2)

        nodes = self.service.list_nodes()

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

        self.service.create_node(node1)
        self.service.create_node(node2)

        # List only base Node types
        base_nodes = self.service.list_nodes(node_type=Node)

        self.assertGreater(len(base_nodes), 0)


class TestServiceStatus(unittest.TestCase):
    """Test service health and statistics."""

    def setUp(self):
        """Set up test service with data."""
        self.service = SFMService()

        # Add some test data
        node1 = Node(label="Node1", description="First")
        node2 = Node(label="Node2", description="Second")

        self.service.create_node(node1)
        self.service.create_node(node2)

    def test_get_health(self):
        """Test getting service health status."""
        health = self.service.get_health()

        self.assertIsInstance(health, ServiceHealth)
        self.assertEqual(health.status, "healthy")
        self.assertGreaterEqual(health.node_count, 2)

    def test_get_statistics(self):
        """Test getting graph statistics."""
        stats = self.service.get_statistics()

        self.assertIsInstance(stats, GraphStatistics)
        self.assertGreaterEqual(stats.total_nodes, 2)
        self.assertIsInstance(stats.node_types, dict)


class TestPhase2QueryMethods(unittest.TestCase):
    """Test Phase 2 query methods (Beta framework extensions)."""

    def setUp(self):
        """Set up test service."""
        self.service = SFMService()

    def test_get_ceremonial_analysis_invalid_threshold(self):
        """Test ceremonial analysis with invalid threshold."""
        with self.assertRaises(SFMValidationError):
            self.service.get_ceremonial_analysis(threshold=1.5)

        with self.assertRaises(SFMValidationError):
            self.service.get_ceremonial_analysis(threshold=-0.1)

    def test_get_ceremonial_analysis_valid_threshold(self):
        """Test ceremonial analysis with valid threshold."""
        result = self.service.get_ceremonial_analysis(threshold=0.5)

        self.assertIsInstance(result, dict)
        self.assertIn("ceremonial_nodes", result)
        self.assertIn("instrumental_nodes", result)
        self.assertIn("ceremonial_ratio", result)
        self.assertIn("threshold", result)
        self.assertEqual(result["threshold"], 0.5)

    def test_get_circular_causation_nonexistent_node(self):
        """Test circular causation with nonexistent node."""
        fake_id = uuid.uuid4()

        with self.assertRaises(SFMNotFoundError):
            self.service.get_circular_causation(fake_id)

    def test_get_circular_causation_valid_node(self):
        """Test circular causation with valid node."""
        node = Node(label="Source", description="Source node")
        created = self.service.create_node(node)

        result = self.service.get_circular_causation(created.id)

        # Engine not initialized: the documented contract is an empty list, not None or an error
        self.assertEqual(result, [])

    def test_get_holarchy_nonexistent_institution(self):
        """Test holarchy with nonexistent institution."""
        fake_id = uuid.uuid4()

        with self.assertRaises(SFMNotFoundError):
            self.service.get_holarchy(fake_id)

    def test_get_holarchy_valid_institution(self):
        """Test holarchy with valid institution."""
        institution = InstitutionalHolarchy(
            label="Test Institution",
            description="Test holarchy"
        )
        created = self.service.create_node(institution)

        result = self.service.get_holarchy(created.id)

        self.assertIsInstance(result, dict)
        self.assertIn("institution_id", result)
        self.assertIn("layers", result)
        self.assertIn("relationships", result)
        self.assertIn("depth", result)

    def test_get_conflicts(self):
        """Test conflict detection."""
        result = self.service.get_conflicts()

        # Engine not initialized: the documented contract is an empty list
        self.assertEqual(result, [])

        self.service.initialize_query_engine()
        self.assertEqual(self.service.get_conflicts(), [])


class TestDataClearing(unittest.TestCase):
    """Test data clearing operations."""

    def setUp(self):
        """Set up test service with data."""
        self.service = SFMService()

        # Add test data
        node = Node(label="Test", description="Test node")
        self.service.create_node(node)

    def test_clear_all_data(self):
        """Test clearing all data."""
        # Verify data exists
        nodes = self.service.list_nodes()
        self.assertGreater(len(nodes), 0)

        # Clear data
        result = self.service.clear_all_data()

        self.assertEqual(result["status"], "success")

        # Verify data is cleared
        nodes = self.service.list_nodes()
        self.assertEqual(len(nodes), 0)


class TestErrorHandling(unittest.TestCase):
    """Test error handling."""

    def setUp(self):
        """Set up test service."""
        self.service = SFMService()

    def test_update_nonexistent_node_raises_error(self):
        """Test updating nonexistent node raises error."""
        node = Node(label="Nonexistent", description="Does not exist")

        with self.assertRaises(SFMNotFoundError):
            self.service.update_node(node)


class TestRepositoryIntegration(unittest.TestCase):
    """Test repository integration."""

    def test_repository_property(self):
        """Test repository property access."""
        service = SFMService()

        repo = service.repository

        self.assertIsNotNone(repo)

    def test_query_engine_property(self):
        """Test query engine property access."""
        service = SFMService()

        # Query engine may not be initialized yet (Phase 2 Step 2)
        engine = service.query_engine

        # Should not raise error, may be None or initialized


class TestHolarchyWiring(unittest.TestCase):
    """Tests verifying the holarchy service method is wired to the query engine."""

    def setUp(self):
        self.service = SFMService()

    def test_get_holarchy_returns_real_result_when_engine_initialized(self):
        """get_holarchy should return non-placeholder data when query engine is active."""
        # Build a 3-level institutional nesting
        parent = Node(label="Federal Agency", description="Top-level institution")
        child = Node(label="Regional Office", description="Sub-institution")
        grandchild = Node(label="Local Office", description="Sub-sub-institution")

        self.service.create_node(parent)
        self.service.create_node(child)
        self.service.create_node(grandchild)

        # Connect parent → child → grandchild so BFS assigns distinct levels
        self.service.create_relationship(
            Relationship(source_id=parent.id, target_id=child.id, kind="contains")
        )
        self.service.create_relationship(
            Relationship(source_id=child.id, target_id=grandchild.id, kind="contains")
        )

        self.service.initialize_query_engine()
        result = self.service.get_holarchy(parent.id)

        self.assertIsInstance(result, dict)
        self.assertIn("institution_id", result)
        self.assertIn("layers", result)
        self.assertIn("depth", result)
        self.assertIn("total_institutions", result)
        self.assertEqual(result["total_institutions"], 3)
        self.assertEqual(result["depth"], 3)

        layers_by_level = {layer["level"]: layer["nodes"] for layer in result["layers"]}
        self.assertEqual(len(layers_by_level["organizational"]), 1)
        self.assertEqual(len(layers_by_level["local"]), 1)
        self.assertEqual(len(layers_by_level["regional"]), 1)

    def test_get_holarchy_uninitialized_engine_returns_empty(self):
        """get_holarchy should return empty-but-valid dict if engine not initialized."""
        institution = Node(label="Lonely Agency", description="no children")
        self.service.create_node(institution)

        # Do NOT call initialize_query_engine()
        result = self.service.get_holarchy(institution.id)

        self.assertIsInstance(result, dict)
        self.assertEqual(result["layers"], [])
        self.assertEqual(result["depth"], 0)


class TestGraphSizeLimit(unittest.TestCase):
    """graph_size_limit must actually be enforced."""

    def test_create_node_raises_when_limit_reached(self):
        from models.exceptions import GraphSizeExceededError, ErrorCode

        service = SFMService(SFMServiceConfig(graph_size_limit=3))
        for i in range(3):
            service.create_node(Node(label=f"N{i}"))

        with self.assertRaises(GraphSizeExceededError) as ctx:
            service.create_node(Node(label="N3"))

        self.assertEqual(ctx.exception.error_code, ErrorCode.GRAPH_SIZE_EXCEEDED)
        self.assertEqual(ctx.exception.details["limit"], 3)
        self.assertEqual(service.get_statistics().total_nodes, 3)

    def test_limit_zero_or_none_disables_check(self):
        service = SFMService(SFMServiceConfig(graph_size_limit=0))
        for i in range(5):
            service.create_node(Node(label=f"N{i}"))
        self.assertEqual(service.get_statistics().total_nodes, 5)

    def test_import_bulk_respects_limit(self):
        import tempfile
        from pathlib import Path
        from data.importers import CSVImportAdapter, MappingTemplates, ImportConfig

        service = SFMService(SFMServiceConfig(graph_size_limit=2))
        with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as f:
            f.write("name,description\n")
            for i in range(5):
                f.write(f"Node{i},desc\n")
            path = f.name
        try:
            adapter = CSVImportAdapter(MappingTemplates.basic_node(), ImportConfig(batch_size=2))
            result = service.import_bulk(path, adapter=adapter, config=ImportConfig(batch_size=2))
        finally:
            Path(path).unlink(missing_ok=True)

        self.assertEqual(result.nodes_created, 2)
        self.assertGreater(result.nodes_failed, 0)
        self.assertTrue(any("size limit" in e.message for e in result.errors))
        self.assertEqual(service.get_statistics().total_nodes, 2)


class TestQueryEngineFreshness(unittest.TestCase):
    """Once initialized, the query engine must reflect subsequent mutations."""

    def setUp(self):
        self.service = SFMService()
        self.a = self.service.create_node(Node(label="A"))
        self.b = self.service.create_node(Node(label="B"))
        self.service.initialize_query_engine()

    def test_engine_rebuilds_after_node_creation(self):
        self.assertEqual(len(self.service.query_engine.graph), 2)
        self.service.create_node(Node(label="C"))
        self.assertEqual(len(self.service.query_engine.graph), 3)

    def test_engine_rebuilds_after_relationship_and_delete(self):
        rel = self.service.create_relationship(
            Relationship(source_id=self.a.id, target_id=self.b.id, kind="influences")
        )
        self.assertEqual(len(self.service.query_engine.graph.relationships), 1)
        self.service.delete_relationship(rel.id)
        self.assertEqual(len(self.service.query_engine.graph.relationships), 0)
        self.service.delete_node(self.b.id)
        self.assertEqual(len(self.service.query_engine.graph), 1)

    def test_engine_not_rebuilt_when_unchanged(self):
        engine = self.service.query_engine
        self.service.get_node(self.a.id)
        self.assertIs(self.service.query_engine, engine)

    def test_engine_stays_none_until_initialized(self):
        service = SFMService()
        service.create_node(Node(label="X"))
        self.assertIsNone(service.query_engine)


if __name__ == "__main__":
    unittest.main()
