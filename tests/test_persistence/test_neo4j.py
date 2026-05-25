"""
Comprehensive tests for Neo4j repository implementation.

These tests use unittest.mock to mock the neo4j driver, ensuring no live
database connection is required. Tests cover all CRUD operations, relationship
management, graph save/load, error handling, and serialization of complex types.
"""

import unittest
import uuid
from datetime import datetime
from unittest.mock import Mock, MagicMock, patch, call
from typing import Any, Dict, List

from models import Node
from models.base_nodes import Node as BaseNode
from models.matrix_components import MatrixCell
from models.system_analysis import SystemProperty
from models.sfm_enums import RelationshipKind
from models.exceptions import (
    SFMNotFoundError,
    NodeCreationError,
    RelationshipValidationError,
)
from graph.sfm_graph import Relationship, SFMGraph


class TestNeo4jRepository(unittest.TestCase):
    """Test suite for Neo4jSFMRepository with mocked Neo4j driver."""

    def setUp(self):
        """Set up test fixtures with mocked Neo4j driver."""
        # Create mock driver and session
        self.mock_driver = MagicMock()
        self.mock_session = MagicMock()
        self.mock_tx = MagicMock()

        # Configure session context manager
        self.mock_driver.session.return_value.__enter__.return_value = self.mock_session
        self.mock_driver.session.return_value.__exit__.return_value = None

        # Patch GraphDatabase.driver to return our mock
        self.driver_patcher = patch('data.neo4j_repository.GraphDatabase.driver')
        self.mock_graph_db = self.driver_patcher.start()
        self.mock_graph_db.return_value = self.mock_driver

        # Import after patching
        from data.neo4j_repository import Neo4jSFMRepository
        self.Neo4jSFMRepository = Neo4jSFMRepository

        # Create repository instance
        self.repo = Neo4jSFMRepository("bolt://localhost:7687", "neo4j", "password")

        # Test data
        self.test_id = uuid.uuid4()
        self.test_node = BaseNode(
            id=self.test_id,
            label="Test Node",
            description="A test node",
            version=1,
            created_at=datetime.now(),
            certainty=0.95
        )

    def tearDown(self):
        """Clean up after tests."""
        self.driver_patcher.stop()

    def test_init_successful_connection(self):
        """Test successful repository initialization."""
        # Session.run should be called during init to test connection
        self.mock_session.run.assert_called_once_with("RETURN 1")
        self.assertIsNotNone(self.repo._driver)

    def test_init_connection_failure(self):
        """Test initialization failure when Neo4j is unavailable."""
        from neo4j.exceptions import ServiceUnavailable

        # Create a new mock that raises ServiceUnavailable
        failing_driver = MagicMock()
        failing_session = MagicMock()
        failing_driver.session.return_value.__enter__.return_value = failing_session
        failing_session.run.side_effect = ServiceUnavailable("Connection failed")

        with patch('data.neo4j_repository.GraphDatabase.driver', return_value=failing_driver):
            from data.neo4j_repository import Neo4jConnectionError, Neo4jSFMRepository

            with self.assertRaises(Neo4jConnectionError):
                Neo4jSFMRepository("bolt://localhost:7687", "neo4j", "wrong")

    def test_serialize_value_uuid(self):
        """Test UUID serialization."""
        test_uuid = uuid.uuid4()
        result = self.Neo4jSFMRepository._serialize_value(test_uuid)
        self.assertEqual(result, str(test_uuid))
        self.assertIsInstance(result, str)

    def test_serialize_value_datetime(self):
        """Test datetime serialization."""
        test_dt = datetime.now()
        result = self.Neo4jSFMRepository._serialize_value(test_dt)
        self.assertEqual(result, test_dt.isoformat())
        self.assertIsInstance(result, str)

    def test_serialize_value_enum(self):
        """Test enum serialization."""
        test_enum = RelationshipKind.INFLUENCES
        result = self.Neo4jSFMRepository._serialize_value(test_enum)
        self.assertEqual(result, test_enum.value)

    def test_serialize_value_dict(self):
        """Test dictionary serialization with nested complex types."""
        test_dict = {
            "id": uuid.uuid4(),
            "timestamp": datetime.now(),
            "kind": RelationshipKind.IMPLEMENTS
        }
        result = self.Neo4jSFMRepository._serialize_value(test_dict)
        self.assertIsInstance(result, dict)
        self.assertIsInstance(result["id"], str)
        self.assertIsInstance(result["timestamp"], str)
        self.assertEqual(result["kind"], RelationshipKind.IMPLEMENTS.value)

    def test_serialize_value_list(self):
        """Test list serialization."""
        test_list = [uuid.uuid4(), datetime.now(), RelationshipKind.DEPENDS_ON]
        result = self.Neo4jSFMRepository._serialize_value(test_list)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 3)
        self.assertIsInstance(result[0], str)
        self.assertIsInstance(result[1], str)

    def test_serialize_value_none(self):
        """Test None serialization."""
        result = self.Neo4jSFMRepository._serialize_value(None)
        self.assertIsNone(result)

    def test_node_to_properties(self):
        """Test node conversion to Neo4j properties."""
        properties = self.Neo4jSFMRepository._node_to_properties(self.test_node)

        self.assertIn('id', properties)
        self.assertIn('label', properties)
        self.assertIn('_python_class', properties)
        self.assertEqual(properties['_python_class'], 'Node')
        self.assertIsInstance(properties['id'], str)
        self.assertEqual(properties['label'], "Test Node")
        self.assertEqual(properties['certainty'], 0.95)

    def test_properties_to_node(self):
        """Test properties conversion back to Node."""
        properties = {
            'id': str(self.test_id),
            'label': 'Test Node',
            'description': 'A test node',
            'version': 1,
            'created_at': datetime.now().isoformat(),
            'certainty': 0.95,
            '_python_class': 'Node'
        }

        node = self.Neo4jSFMRepository._properties_to_node(properties, BaseNode)

        self.assertIsInstance(node, BaseNode)
        self.assertEqual(node.id, self.test_id)
        self.assertEqual(node.label, 'Test Node')
        self.assertEqual(node.certainty, 0.95)

    def test_create_node_success(self):
        """Test successful node creation."""
        # Mock the transaction execution
        mock_result = MagicMock()
        mock_result.single.return_value = {'n': {'id': str(self.test_id)}}
        self.mock_session.execute_write.return_value = {'id': str(self.test_id)}

        result = self.repo.create_node(self.test_node)

        self.assertEqual(result, self.test_node)
        self.mock_session.execute_write.assert_called_once()

    def test_create_node_duplicate(self):
        """Test node creation failure when ID already exists."""
        # Mock transaction to return None (indicating duplicate)
        self.mock_session.execute_write.return_value = None

        with self.assertRaises(NodeCreationError) as ctx:
            self.repo.create_node(self.test_node)

        self.assertIn("already exists", str(ctx.exception))

    def test_read_node_success(self):
        """Test successful node read."""
        # Mock the transaction execution
        properties = {
            'id': str(self.test_id),
            'label': 'Test Node',
            'description': 'A test node',
            'version': 1,
            'created_at': datetime.now().isoformat(),
            '_python_class': 'Node'
        }

        mock_record = {
            'n': properties,
            'labels': ['Node']
        }

        mock_result = MagicMock()
        mock_result.single.return_value = mock_record

        # Configure execute_read to call the transaction function
        def execute_read_side_effect(func, *args):
            return func(self.mock_tx, *args)

        self.mock_session.execute_read.side_effect = execute_read_side_effect
        self.mock_tx.run.return_value.single.return_value = mock_record

        result = self.repo.read_node(self.test_id)

        self.assertIsNotNone(result)
        self.assertEqual(result.id, self.test_id)
        self.assertEqual(result.label, 'Test Node')

    def test_read_node_not_found(self):
        """Test reading a non-existent node."""
        self.mock_tx.run.return_value.single.return_value = None

        def execute_read_side_effect(func, *args):
            return func(self.mock_tx, *args)

        self.mock_session.execute_read.side_effect = execute_read_side_effect

        result = self.repo.read_node(uuid.uuid4())

        self.assertIsNone(result)

    def test_update_node_success(self):
        """Test successful node update."""
        mock_result = MagicMock()
        mock_result.single.return_value = {'n': {'id': str(self.test_id)}}
        self.mock_session.execute_write.return_value = {'id': str(self.test_id)}

        self.test_node.label = "Updated Node"
        result = self.repo.update_node(self.test_node)

        self.assertEqual(result.label, "Updated Node")
        self.mock_session.execute_write.assert_called_once()

    def test_update_node_not_found(self):
        """Test update failure when node doesn't exist."""
        self.mock_session.execute_write.return_value = None

        with self.assertRaises(SFMNotFoundError):
            self.repo.update_node(self.test_node)

    def test_delete_node_success(self):
        """Test successful node deletion."""
        self.mock_session.execute_write.return_value = True

        result = self.repo.delete_node(self.test_id)

        self.assertTrue(result)
        self.mock_session.execute_write.assert_called_once()

    def test_delete_node_not_found(self):
        """Test deleting a non-existent node."""
        self.mock_session.execute_write.return_value = False

        result = self.repo.delete_node(uuid.uuid4())

        self.assertFalse(result)

    def test_list_nodes_all(self):
        """Test listing all nodes."""
        # Mock multiple nodes
        mock_records = [
            {
                'n': {
                    'id': str(uuid.uuid4()),
                    'label': 'Node 1',
                    '_python_class': 'Node'
                },
                'labels': ['Node']
            },
            {
                'n': {
                    'id': str(uuid.uuid4()),
                    'label': 'Node 2',
                    '_python_class': 'Node'
                },
                'labels': ['Node']
            }
        ]

        mock_result = MagicMock()
        mock_result.__iter__.return_value = iter(mock_records)

        def execute_read_side_effect(func, *args):
            return func(self.mock_tx, *args)

        self.mock_session.execute_read.side_effect = execute_read_side_effect
        self.mock_tx.run.return_value = mock_result

        results = self.repo.list_nodes()

        self.assertEqual(len(results), 2)
        self.assertTrue(all(isinstance(n, BaseNode) for n in results))

    def test_list_nodes_filtered_by_type(self):
        """Test listing nodes filtered by type."""
        # MatrixCell requires institution_id and criteria_id
        inst_id = uuid.uuid4()
        crit_id = uuid.uuid4()

        mock_records = [
            {
                'n': {
                    'id': str(uuid.uuid4()),
                    'label': 'Matrix Cell',
                    'institution_id': str(inst_id),
                    'criteria_id': str(crit_id),
                    '_python_class': 'MatrixCell'
                },
                'labels': ['MatrixCell']
            }
        ]

        mock_result = MagicMock()
        mock_result.__iter__.return_value = iter(mock_records)

        def execute_read_side_effect(func, *args):
            return func(self.mock_tx, *args)

        self.mock_session.execute_read.side_effect = execute_read_side_effect
        self.mock_tx.run.return_value = mock_result

        results = self.repo.list_nodes(MatrixCell)

        self.assertEqual(len(results), 1)

    def test_create_relationship_success(self):
        """Test successful relationship creation."""
        source_id = uuid.uuid4()
        target_id = uuid.uuid4()
        rel = Relationship(
            id=uuid.uuid4(),
            source_id=source_id,
            target_id=target_id,
            kind="INFLUENCES",
            weight=0.8
        )

        mock_result = MagicMock()
        mock_result.single.return_value = {'r': {'id': str(rel.id)}}
        self.mock_session.execute_write.return_value = {'id': str(rel.id)}

        result = self.repo.create_relationship(rel)

        self.assertEqual(result, rel)
        self.mock_session.execute_write.assert_called_once()

    def test_create_relationship_node_not_found(self):
        """Test relationship creation when source/target node doesn't exist."""
        rel = Relationship(
            id=uuid.uuid4(),
            source_id=uuid.uuid4(),
            target_id=uuid.uuid4(),
            kind="INFLUENCES"
        )

        self.mock_session.execute_write.return_value = None

        with self.assertRaises(RelationshipValidationError):
            self.repo.create_relationship(rel)

    def test_read_relationship_success(self):
        """Test successful relationship read."""
        rel_id = uuid.uuid4()
        source_id = uuid.uuid4()
        target_id = uuid.uuid4()

        mock_record = {
            'r': {
                'id': str(rel_id),
                'kind': 'INFLUENCES',
                'weight': 0.8
            },
            'source_id': str(source_id),
            'target_id': str(target_id),
            'rel_type': 'INFLUENCES'
        }

        def execute_read_side_effect(func, *args):
            return func(self.mock_tx, *args)

        self.mock_session.execute_read.side_effect = execute_read_side_effect
        self.mock_tx.run.return_value.single.return_value = mock_record

        result = self.repo.read_relationship(rel_id)

        self.assertIsNotNone(result)
        self.assertEqual(result.id, rel_id)
        self.assertEqual(result.source_id, source_id)
        self.assertEqual(result.target_id, target_id)
        self.assertEqual(result.weight, 0.8)

    def test_read_relationship_not_found(self):
        """Test reading a non-existent relationship."""
        self.mock_tx.run.return_value.single.return_value = None

        def execute_read_side_effect(func, *args):
            return func(self.mock_tx, *args)

        self.mock_session.execute_read.side_effect = execute_read_side_effect

        result = self.repo.read_relationship(uuid.uuid4())

        self.assertIsNone(result)

    def test_update_relationship_success(self):
        """Test successful relationship update."""
        rel = Relationship(
            id=uuid.uuid4(),
            source_id=uuid.uuid4(),
            target_id=uuid.uuid4(),
            kind="INFLUENCES",
            weight=0.9
        )

        mock_result = MagicMock()
        mock_result.single.return_value = {'r': {'id': str(rel.id)}}
        self.mock_session.execute_write.return_value = {'id': str(rel.id)}

        result = self.repo.update_relationship(rel)

        self.assertEqual(result, rel)

    def test_update_relationship_not_found(self):
        """Test update failure when relationship doesn't exist."""
        rel = Relationship(
            id=uuid.uuid4(),
            source_id=uuid.uuid4(),
            target_id=uuid.uuid4(),
            kind="INFLUENCES"
        )

        self.mock_session.execute_write.return_value = None

        with self.assertRaises(SFMNotFoundError):
            self.repo.update_relationship(rel)

    def test_delete_relationship_success(self):
        """Test successful relationship deletion."""
        self.mock_session.execute_write.return_value = True

        result = self.repo.delete_relationship(uuid.uuid4())

        self.assertTrue(result)

    def test_delete_relationship_not_found(self):
        """Test deleting a non-existent relationship."""
        self.mock_session.execute_write.return_value = False

        result = self.repo.delete_relationship(uuid.uuid4())

        self.assertFalse(result)

    def test_list_relationships_all(self):
        """Test listing all relationships."""
        mock_records = [
            {
                'r': {
                    'id': str(uuid.uuid4()),
                    'kind': 'INFLUENCES',
                    'weight': 0.7
                },
                'source_id': str(uuid.uuid4()),
                'target_id': str(uuid.uuid4()),
                'rel_type': 'INFLUENCES'
            },
            {
                'r': {
                    'id': str(uuid.uuid4()),
                    'kind': 'DEPENDS_ON',
                    'weight': 0.9
                },
                'source_id': str(uuid.uuid4()),
                'target_id': str(uuid.uuid4()),
                'rel_type': 'DEPENDS_ON'
            }
        ]

        mock_result = MagicMock()
        mock_result.__iter__.return_value = iter(mock_records)

        def execute_read_side_effect(func, *args):
            return func(self.mock_tx, *args)

        self.mock_session.execute_read.side_effect = execute_read_side_effect
        self.mock_tx.run.return_value = mock_result

        results = self.repo.list_relationships()

        self.assertEqual(len(results), 2)

    def test_find_relationships_by_source(self):
        """Test finding relationships by source node."""
        source_id = uuid.uuid4()

        mock_records = [
            {
                'r': {
                    'id': str(uuid.uuid4()),
                    'kind': 'INFLUENCES'
                },
                'source_id': str(source_id),
                'target_id': str(uuid.uuid4()),
                'rel_type': 'INFLUENCES'
            }
        ]

        mock_result = MagicMock()
        mock_result.__iter__.return_value = iter(mock_records)

        def execute_read_side_effect(func, *args, **kwargs):
            return func(self.mock_tx, *args, **kwargs)

        self.mock_session.execute_read.side_effect = execute_read_side_effect
        self.mock_tx.run.return_value = mock_result

        results = self.repo.find_relationships(source_id=source_id)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].source_id, source_id)

    def test_find_relationships_by_target(self):
        """Test finding relationships by target node."""
        target_id = uuid.uuid4()

        mock_records = [
            {
                'r': {
                    'id': str(uuid.uuid4()),
                    'kind': 'INFLUENCES'
                },
                'source_id': str(uuid.uuid4()),
                'target_id': str(target_id),
                'rel_type': 'INFLUENCES'
            }
        ]

        mock_result = MagicMock()
        mock_result.__iter__.return_value = iter(mock_records)

        def execute_read_side_effect(func, *args, **kwargs):
            return func(self.mock_tx, *args, **kwargs)

        self.mock_session.execute_read.side_effect = execute_read_side_effect
        self.mock_tx.run.return_value = mock_result

        results = self.repo.find_relationships(target_id=target_id)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].target_id, target_id)

    def test_load_graph(self):
        """Test loading complete graph from repository."""
        # Mock nodes
        node_records = [
            {
                'n': {
                    'id': str(uuid.uuid4()),
                    'label': 'Node 1',
                    '_python_class': 'Node'
                },
                'labels': ['Node']
            }
        ]

        # Mock relationships
        rel_records = [
            {
                'r': {
                    'id': str(uuid.uuid4()),
                    'kind': 'INFLUENCES'
                },
                'source_id': str(uuid.uuid4()),
                'target_id': str(uuid.uuid4()),
                'rel_type': 'INFLUENCES'
            }
        ]

        node_result = MagicMock()
        node_result.__iter__.return_value = iter(node_records)

        rel_result = MagicMock()
        rel_result.__iter__.return_value = iter(rel_records)

        # Setup execute_read to return different results based on call
        call_count = [0]

        def execute_read_side_effect(func, *args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:  # First call for nodes
                self.mock_tx.run.return_value = node_result
            else:  # Second call for relationships
                self.mock_tx.run.return_value = rel_result
            return func(self.mock_tx, *args, **kwargs)

        self.mock_session.execute_read.side_effect = execute_read_side_effect

        graph = self.repo.load_graph()

        self.assertIsInstance(graph, SFMGraph)
        self.assertEqual(len(graph.nodes), 1)
        self.assertEqual(len(graph.relationships), 1)

    def test_save_graph(self):
        """Test saving complete graph to repository."""
        # Create a test graph
        graph = SFMGraph()
        node1 = BaseNode(id=uuid.uuid4(), label="Node 1")
        node2 = BaseNode(id=uuid.uuid4(), label="Node 2")
        graph.add_node(node1)
        graph.add_node(node2)

        rel = Relationship(
            id=uuid.uuid4(),
            source_id=node1.id,
            target_id=node2.id,
            kind="INFLUENCES"
        )
        graph.add_relationship(rel)

        # Mock successful operations
        self.mock_session.execute_write.return_value = True

        # Call save_graph
        self.repo.save_graph(graph)

        # Verify clear was called and nodes/relationships were created
        # The actual number of calls depends on clear + create operations
        self.assertGreater(self.mock_session.execute_write.call_count, 0)

    def test_clear(self):
        """Test clearing all data from repository."""
        self.mock_session.execute_write.return_value = None

        self.repo.clear()

        self.mock_session.execute_write.assert_called_once()

    def test_context_manager(self):
        """Test using repository as context manager."""
        with patch('data.neo4j_repository.GraphDatabase.driver') as mock_graph_db:
            mock_driver = MagicMock()
            mock_session = MagicMock()
            mock_driver.session.return_value.__enter__.return_value = mock_session
            mock_driver.session.return_value.__exit__.return_value = None
            mock_graph_db.return_value = mock_driver

            from data.neo4j_repository import Neo4jSFMRepository

            with Neo4jSFMRepository("bolt://localhost:7687", "neo4j", "password") as repo:
                self.assertIsNotNone(repo)

            # Verify close was called
            mock_driver.close.assert_called_once()

    def test_serialization_with_meta_dict(self):
        """Test serialization of nodes with metadata dictionaries."""
        node = BaseNode(
            id=uuid.uuid4(),
            label="Test",
            meta={"key1": "value1", "key2": "value2"}
        )

        properties = self.Neo4jSFMRepository._node_to_properties(node)

        self.assertIn('meta', properties)
        self.assertIsInstance(properties['meta'], dict)

    def test_error_handling_neo4j_error(self):
        """Test error handling for Neo4j driver errors."""
        from neo4j.exceptions import Neo4jError

        self.mock_session.execute_write.side_effect = Neo4jError("Database error")

        with self.assertRaises(NodeCreationError):
            self.repo.create_node(self.test_node)


if __name__ == '__main__':
    unittest.main()
