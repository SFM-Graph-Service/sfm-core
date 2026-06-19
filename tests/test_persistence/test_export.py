"""
Unit tests for SFM graph export and import functionality.
Tests GraphML, GEXF, and custom JSON snapshot formats with round-trip validation.
"""

import json
import os
import tempfile
import unittest
import uuid
from pathlib import Path

import networkx as nx

from models import Node
from models.cultural_analysis import CeremonialInstrumentalClassification
from models.system_analysis import InstitutionalHolarchy, SystemProperty
from models.matrix_components import MatrixCell, SFMMatrix
from graph.sfm_graph import SFMGraph, Relationship
from graph.sfm_persistence import (
    SFMPersistenceManager,
    SFMPersistenceError,
)


class TestGraphMLExport(unittest.TestCase):
    """Test GraphML export functionality."""

    def setUp(self):
        """Set up test graph and manager."""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = SFMPersistenceManager(base_path=self.temp_dir)
        self.graph = self._create_test_graph()

    def _create_test_graph(self) -> SFMGraph:
        """Create a test graph with multiple node types and relationships."""
        graph = SFMGraph(name="Test Graph", description="Test export/import")

        # Create diverse node types
        self.node1 = Node(label="Base Node", description="A basic node")
        self.node2 = CeremonialInstrumentalClassification(
            label="Ceremonial",
            description="Ceremonial classification",
            ceremonial_score=0.8,
            instrumental_score=0.2
        )
        self.node3 = InstitutionalHolarchy(
            label="Institution",
            description="Institutional structure"
        )
        self.node4 = SystemProperty(
            label="Property",
            description="System property"
        )
        self.node5 = Node(
            label="Cell",
            description="Additional node"
        )

        graph.add_node(self.node1)
        graph.add_node(self.node2)
        graph.add_node(self.node3)
        graph.add_node(self.node4)
        graph.add_node(self.node5)

        # Create relationships
        self.rel1 = Relationship(
            source_id=self.node1.id,
            target_id=self.node2.id,
            kind="influences"
        )
        self.rel2 = Relationship(
            source_id=self.node2.id,
            target_id=self.node3.id,
            kind="constrains"
        )
        self.rel3 = Relationship(
            source_id=self.node3.id,
            target_id=self.node4.id,
            kind="determines",
            weight=0.75
        )
        self.rel4 = Relationship(
            source_id=self.node4.id,
            target_id=self.node5.id,
            kind="contains"
        )

        graph.add_relationship(self.rel1)
        graph.add_relationship(self.rel2)
        graph.add_relationship(self.rel3)
        graph.add_relationship(self.rel4)

        return graph

    def test_export_graphml_creates_file(self):
        """Test that GraphML export creates a valid file."""
        output_path = os.path.join(self.temp_dir, "test.graphml")
        self.manager.export_graphml(self.graph, output_path)

        self.assertTrue(os.path.exists(output_path))
        self.assertGreater(os.path.getsize(output_path), 0)

    def test_export_graphml_valid_format(self):
        """Test that exported GraphML file is valid and can be read by networkx."""
        output_path = os.path.join(self.temp_dir, "test.graphml")
        self.manager.export_graphml(self.graph, output_path)

        # Load and validate with networkx
        loaded_graph = nx.read_graphml(output_path)
        self.assertIsInstance(loaded_graph, nx.DiGraph)
        self.assertEqual(len(loaded_graph.nodes), 5)
        self.assertEqual(len(loaded_graph.edges), 4)

    def test_export_graphml_preserves_node_attributes(self):
        """Test that node attributes are preserved in GraphML export."""
        output_path = os.path.join(self.temp_dir, "test.graphml")
        self.manager.export_graphml(self.graph, output_path)

        loaded_graph = nx.read_graphml(output_path)

        # Check that nodes have required attributes
        for node_id, attrs in loaded_graph.nodes(data=True):
            self.assertIn('label', attrs)
            self.assertIn('description', attrs)
            self.assertIn('type', attrs)

    def test_export_graphml_preserves_edge_attributes(self):
        """Test that edge attributes are preserved in GraphML export."""
        output_path = os.path.join(self.temp_dir, "test.graphml")
        self.manager.export_graphml(self.graph, output_path)

        loaded_graph = nx.read_graphml(output_path)

        # Check that edges have kind attribute
        for u, v, attrs in loaded_graph.edges(data=True):
            self.assertIn('kind', attrs)

    def test_export_graphml_error_handling(self):
        """Test error handling for invalid paths."""
        invalid_path = "/invalid/nonexistent/path/test.graphml"

        with self.assertRaises(SFMPersistenceError):
            self.manager.export_graphml(self.graph, invalid_path)


class TestGEXFExport(unittest.TestCase):
    """Test GEXF export functionality."""

    def setUp(self):
        """Set up test graph and manager."""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = SFMPersistenceManager(base_path=self.temp_dir)
        self.graph = self._create_test_graph()

    def _create_test_graph(self) -> SFMGraph:
        """Create a test graph with multiple node types and relationships."""
        graph = SFMGraph(name="Test Graph", description="Test export/import")

        # Create diverse node types
        node1 = Node(label="Node1", description="First node")
        node2 = Node(label="Node2", description="Second node")
        node3 = Node(label="Node3", description="Third node")

        graph.add_node(node1)
        graph.add_node(node2)
        graph.add_node(node3)

        # Create relationships
        rel1 = Relationship(
            source_id=node1.id,
            target_id=node2.id,
            kind="links_to"
        )
        rel2 = Relationship(
            source_id=node2.id,
            target_id=node3.id,
            kind="contains"
        )

        graph.add_relationship(rel1)
        graph.add_relationship(rel2)

        return graph

    def test_export_gexf_creates_file(self):
        """Test that GEXF export creates a valid file."""
        output_path = os.path.join(self.temp_dir, "test.gexf")
        self.manager.export_gexf(self.graph, output_path)

        self.assertTrue(os.path.exists(output_path))
        self.assertGreater(os.path.getsize(output_path), 0)

    def test_export_gexf_valid_format(self):
        """Test that exported GEXF file is valid and can be read by networkx."""
        output_path = os.path.join(self.temp_dir, "test.gexf")
        self.manager.export_gexf(self.graph, output_path)

        # Load and validate with networkx
        loaded_graph = nx.read_gexf(output_path)
        self.assertIsInstance(loaded_graph, nx.DiGraph)
        self.assertEqual(len(loaded_graph.nodes), 3)
        self.assertEqual(len(loaded_graph.edges), 2)

    def test_export_gexf_preserves_attributes(self):
        """Test that node and edge attributes are preserved in GEXF export."""
        output_path = os.path.join(self.temp_dir, "test.gexf")
        self.manager.export_gexf(self.graph, output_path)

        loaded_graph = nx.read_gexf(output_path)

        # Check that nodes have attributes
        for node_id, attrs in loaded_graph.nodes(data=True):
            self.assertIn('label', attrs)
            self.assertIn('description', attrs)


class TestJSONSnapshotExport(unittest.TestCase):
    """Test custom JSON snapshot export functionality."""

    def setUp(self):
        """Set up test graph and manager."""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = SFMPersistenceManager(base_path=self.temp_dir)
        self.graph = self._create_test_graph()

    def _create_test_graph(self) -> SFMGraph:
        """Create a test graph with 8-10 nodes and relationships."""
        graph = SFMGraph(name="Complex Graph", description="Complex test graph")

        # Create 8 diverse node types
        nodes = [
            Node(label="Base1", description="Base node 1"),
            Node(label="Base2", description="Base node 2"),
            CeremonialInstrumentalClassification(
                label="Ceremonial1",
                description="Ceremonial node",
                ceremonial_score=0.9,
                instrumental_score=0.1
            ),
            InstitutionalHolarchy(label="Institution1", description="Institution"),
            SystemProperty(label="Property1", description="System property"),
            Node(label="Node1", description="Additional node 1"),
            Node(label="Node2", description="Additional node 2"),
            SFMMatrix(label="Matrix1", description="SFM Matrix"),
        ]

        # Add nodes to graph
        for node in nodes:
            graph.add_node(node)

        # Create various relationships
        relationships = [
            Relationship(source_id=nodes[0].id, target_id=nodes[1].id, kind="connects"),
            Relationship(source_id=nodes[1].id, target_id=nodes[2].id, kind="influences"),
            Relationship(source_id=nodes[2].id, target_id=nodes[3].id, kind="constrains"),
            Relationship(source_id=nodes[3].id, target_id=nodes[4].id, kind="determines", weight=0.8),
            Relationship(source_id=nodes[4].id, target_id=nodes[5].id, kind="contains"),
            Relationship(source_id=nodes[5].id, target_id=nodes[6].id, kind="relates"),
            Relationship(source_id=nodes[6].id, target_id=nodes[7].id, kind="includes"),
        ]

        for rel in relationships:
            graph.add_relationship(rel)

        return graph

    def test_export_json_snapshot_creates_file(self):
        """Test that JSON snapshot export creates a valid file."""
        output_path = os.path.join(self.temp_dir, "snapshot.json")
        self.manager.export_json_snapshot(self.graph, output_path)

        self.assertTrue(os.path.exists(output_path))
        self.assertGreater(os.path.getsize(output_path), 0)

    def test_export_json_snapshot_structure(self):
        """Test that JSON snapshot has correct structure."""
        output_path = os.path.join(self.temp_dir, "snapshot.json")
        self.manager.export_json_snapshot(self.graph, output_path)

        with open(output_path, 'r') as f:
            snapshot = json.load(f)

        # Validate structure
        self.assertIn('metadata', snapshot)
        self.assertIn('nodes', snapshot)
        self.assertIn('relationships', snapshot)

        # Validate metadata
        metadata = snapshot['metadata']
        self.assertIn('graph_id', metadata)
        self.assertIn('name', metadata)
        self.assertIn('node_count', metadata)
        self.assertIn('relationship_count', metadata)

        # Validate counts
        self.assertEqual(metadata['node_count'], 8)
        self.assertEqual(metadata['relationship_count'], 7)
        self.assertEqual(len(snapshot['nodes']), 8)
        self.assertEqual(len(snapshot['relationships']), 7)

    def test_export_json_snapshot_preserves_node_properties(self):
        """Test that node properties are preserved in JSON snapshot."""
        output_path = os.path.join(self.temp_dir, "snapshot.json")
        self.manager.export_json_snapshot(self.graph, output_path)

        with open(output_path, 'r') as f:
            snapshot = json.load(f)

        # Check each node has required fields
        for node in snapshot['nodes']:
            self.assertIn('id', node)
            self.assertIn('label', node)
            self.assertIn('description', node)
            self.assertIn('type', node)

    def test_export_json_snapshot_preserves_relationship_properties(self):
        """Test that relationship properties are preserved in JSON snapshot."""
        output_path = os.path.join(self.temp_dir, "snapshot.json")
        self.manager.export_json_snapshot(self.graph, output_path)

        with open(output_path, 'r') as f:
            snapshot = json.load(f)

        # Check each relationship has required fields
        for rel in snapshot['relationships']:
            self.assertIn('id', rel)
            self.assertIn('source_id', rel)
            self.assertIn('target_id', rel)
            self.assertIn('kind', rel)


class TestJSONSnapshotImport(unittest.TestCase):
    """Test custom JSON snapshot import functionality."""

    def setUp(self):
        """Set up test graph and manager."""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = SFMPersistenceManager(base_path=self.temp_dir)
        self.graph = self._create_test_graph()

    def _create_test_graph(self) -> SFMGraph:
        """Create a test graph with diverse node types."""
        graph = SFMGraph(name="Import Test", description="Import test graph")

        nodes = [
            Node(label="N1", description="Node 1"),
            Node(label="N2", description="Node 2"),
            CeremonialInstrumentalClassification(
                label="C1",
                description="Ceremonial",
                ceremonial_score=0.6,
                instrumental_score=0.4
            ),
            InstitutionalHolarchy(label="I1", description="Institution"),
            SystemProperty(label="P1", description="Property"),
        ]

        for node in nodes:
            graph.add_node(node)

        relationships = [
            Relationship(source_id=nodes[0].id, target_id=nodes[1].id, kind="r1"),
            Relationship(source_id=nodes[1].id, target_id=nodes[2].id, kind="r2"),
            Relationship(source_id=nodes[2].id, target_id=nodes[3].id, kind="r3"),
            Relationship(source_id=nodes[3].id, target_id=nodes[4].id, kind="r4", weight=0.5),
        ]

        for rel in relationships:
            graph.add_relationship(rel)

        return graph

    def test_import_json_snapshot_loads_file(self):
        """Test that JSON snapshot can be imported."""
        output_path = os.path.join(self.temp_dir, "snapshot.json")
        self.manager.export_json_snapshot(self.graph, output_path)

        loaded_graph = self.manager.import_json_snapshot(output_path)
        self.assertIsInstance(loaded_graph, SFMGraph)

    def test_import_json_snapshot_file_not_found(self):
        """Test error handling for missing file."""
        with self.assertRaises(SFMPersistenceError):
            self.manager.import_json_snapshot("/nonexistent/file.json")

    def test_import_json_snapshot_invalid_format(self):
        """Test error handling for invalid JSON format."""
        invalid_path = os.path.join(self.temp_dir, "invalid.json")

        # Create invalid JSON
        with open(invalid_path, 'w') as f:
            json.dump({"invalid": "structure"}, f)

        with self.assertRaises(SFMPersistenceError):
            self.manager.import_json_snapshot(invalid_path)


class TestRoundTripExportImport(unittest.TestCase):
    """Test round-trip export/import for all formats."""

    def setUp(self):
        """Set up test graph and manager."""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = SFMPersistenceManager(base_path=self.temp_dir)
        self.graph = self._create_comprehensive_graph()

    def _create_comprehensive_graph(self) -> SFMGraph:
        """Create a comprehensive test graph for round-trip testing."""
        graph = SFMGraph(
            name="Comprehensive Test",
            description="Comprehensive test graph for round-trip validation"
        )

        # Create 10 diverse nodes
        nodes = [
            Node(label="Node1", description="Base node 1"),
            Node(label="Node2", description="Base node 2"),
            CeremonialInstrumentalClassification(
                label="Ceremonial",
                description="Ceremonial classification",
                ceremonial_score=0.7,
                instrumental_score=0.3
            ),
            InstitutionalHolarchy(
                label="Institution",
                description="Institutional structure"
            ),
            SystemProperty(
                label="Property",
                description="System property"
            ),
            Node(label="Additional1", description="Additional node 1"),
            Node(label="Additional2", description="Additional node 2"),
            SFMMatrix(label="Matrix", description="SFM Matrix"),
            Node(label="Node3", description="Base node 3"),
            Node(label="Node4", description="Base node 4"),
        ]

        for node in nodes:
            graph.add_node(node)

        # Create relationships with various properties
        relationships = [
            Relationship(source_id=nodes[0].id, target_id=nodes[1].id, kind="connects"),
            Relationship(source_id=nodes[1].id, target_id=nodes[2].id, kind="influences", weight=0.6),
            Relationship(source_id=nodes[2].id, target_id=nodes[3].id, kind="constrains"),
            Relationship(source_id=nodes[3].id, target_id=nodes[4].id, kind="determines", weight=0.9),
            Relationship(source_id=nodes[4].id, target_id=nodes[5].id, kind="contains"),
            Relationship(source_id=nodes[5].id, target_id=nodes[6].id, kind="relates"),
            Relationship(source_id=nodes[6].id, target_id=nodes[7].id, kind="includes", weight=0.4),
            Relationship(source_id=nodes[7].id, target_id=nodes[8].id, kind="links"),
            Relationship(source_id=nodes[8].id, target_id=nodes[9].id, kind="flows_to", weight=0.2),
        ]

        for rel in relationships:
            graph.add_relationship(rel)

        return graph

    def test_json_snapshot_round_trip(self):
        """Test JSON snapshot export → import → verify identical."""
        export_path = os.path.join(self.temp_dir, "roundtrip.json")

        # Export
        self.manager.export_json_snapshot(self.graph, export_path)

        # Import
        loaded_graph = self.manager.import_json_snapshot(export_path)

        # Assert identical
        self.assertEqual(len(list(loaded_graph)), len(list(self.graph)))
        self.assertEqual(len(loaded_graph.relationships), len(self.graph.relationships))

        # Verify node count
        self.assertEqual(len(list(loaded_graph)), 10)

        # Verify relationship count
        self.assertEqual(len(loaded_graph.relationships), 9)

    def test_json_snapshot_preserves_node_properties(self):
        """Test that node properties are preserved in round-trip."""
        export_path = os.path.join(self.temp_dir, "roundtrip.json")

        # Get original node IDs and labels
        original_nodes = {str(node.id): node.label for node in self.graph}

        # Export and import
        self.manager.export_json_snapshot(self.graph, export_path)
        loaded_graph = self.manager.import_json_snapshot(export_path)

        # Verify all nodes are present
        loaded_nodes = {str(node.id): node.label for node in loaded_graph}

        self.assertEqual(len(original_nodes), len(loaded_nodes))

        # Verify labels are preserved
        for node_id, label in original_nodes.items():
            self.assertIn(node_id, loaded_nodes)
            self.assertEqual(loaded_nodes[node_id], label)

    def test_json_snapshot_preserves_relationships(self):
        """Test that relationships are preserved in round-trip."""
        export_path = os.path.join(self.temp_dir, "roundtrip.json")

        # Get original relationship details
        original_rels = {
            str(rel.id): (str(rel.source_id), str(rel.target_id), rel.kind)
            for rel in self.graph.relationships.values()
        }

        # Export and import
        self.manager.export_json_snapshot(self.graph, export_path)
        loaded_graph = self.manager.import_json_snapshot(export_path)

        # Verify all relationships are present
        loaded_rels = {
            str(rel.id): (str(rel.source_id), str(rel.target_id), rel.kind)
            for rel in loaded_graph.relationships.values()
        }

        self.assertEqual(len(original_rels), len(loaded_rels))

        # Verify relationship details are preserved
        for rel_id, (source, target, kind) in original_rels.items():
            self.assertIn(rel_id, loaded_rels)
            loaded_source, loaded_target, loaded_kind = loaded_rels[rel_id]
            self.assertEqual(loaded_source, source)
            self.assertEqual(loaded_target, target)
            self.assertEqual(loaded_kind, kind)

    def test_json_snapshot_preserves_node_types(self):
        """Test that node types are preserved through round-trip."""
        export_path = os.path.join(self.temp_dir, "roundtrip.json")

        # Get original node types
        original_types = {type(node).__name__ for node in self.graph}

        # Export and import
        self.manager.export_json_snapshot(self.graph, export_path)
        loaded_graph = self.manager.import_json_snapshot(export_path)

        # Get loaded node types
        loaded_types = {type(node).__name__ for node in loaded_graph}

        # Verify all types are preserved
        self.assertEqual(original_types, loaded_types)


class TestEmptyGraphExport(unittest.TestCase):
    """Test export/import with empty graphs."""

    def setUp(self):
        """Set up manager and empty graph."""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = SFMPersistenceManager(base_path=self.temp_dir)
        self.empty_graph = SFMGraph(name="Empty", description="Empty graph")

    def test_export_empty_graphml(self):
        """Test exporting empty graph to GraphML."""
        output_path = os.path.join(self.temp_dir, "empty.graphml")
        self.manager.export_graphml(self.empty_graph, output_path)

        loaded = nx.read_graphml(output_path)
        self.assertEqual(len(loaded.nodes), 0)
        self.assertEqual(len(loaded.edges), 0)

    def test_export_empty_gexf(self):
        """Test exporting empty graph to GEXF."""
        output_path = os.path.join(self.temp_dir, "empty.gexf")
        self.manager.export_gexf(self.empty_graph, output_path)

        loaded = nx.read_gexf(output_path)
        self.assertEqual(len(loaded.nodes), 0)
        self.assertEqual(len(loaded.edges), 0)

    def test_export_import_empty_json_snapshot(self):
        """Test exporting and importing empty graph via JSON snapshot."""
        output_path = os.path.join(self.temp_dir, "empty.json")
        self.manager.export_json_snapshot(self.empty_graph, output_path)

        loaded = self.manager.import_json_snapshot(output_path)
        self.assertEqual(len(list(loaded)), 0)
        self.assertEqual(len(loaded.relationships), 0)


class TestPickleSecurityGate(unittest.TestCase):
    """Tests for pickle deserialization security gate (Issue #1)."""

    def setUp(self):
        """Set up a simple graph and serialized pickle bytes for tests."""
        from graph.sfm_persistence import SFMGraphSerializer, StorageFormat, SFMSerializationError
        self.SFMGraphSerializer = SFMGraphSerializer
        self.StorageFormat = StorageFormat
        self.SFMSerializationError = SFMSerializationError

        self.graph = SFMGraph(name="Pickle Test", description="Security test graph")
        node = Node(label="Test Node", description="node for pickle test")
        self.graph.add_node(node)

        # Pre-serialise to pickle bytes for use in deserialization tests
        self.pickle_bytes = SFMGraphSerializer.serialize_graph(
            self.graph, StorageFormat.PICKLE
        )
        self.compressed_pickle_bytes = SFMGraphSerializer.serialize_graph(
            self.graph, StorageFormat.COMPRESSED_PICKLE
        )

    def test_pickle_deserialize_blocked_by_default(self):
        """Pickle deserialization must raise SFMSerializationError without allow_pickle."""
        with self.assertRaises(self.SFMSerializationError) as ctx:
            self.SFMGraphSerializer.deserialize_graph(
                self.pickle_bytes, self.StorageFormat.PICKLE
            )
        self.assertIn("allow_pickle", str(ctx.exception))

    def test_compressed_pickle_deserialize_blocked_by_default(self):
        """Compressed pickle deserialization must raise without allow_pickle."""
        with self.assertRaises(self.SFMSerializationError):
            self.SFMGraphSerializer.deserialize_graph(
                self.compressed_pickle_bytes, self.StorageFormat.COMPRESSED_PICKLE
            )

    def test_pickle_deserialize_allowed_with_opt_in(self):
        """Pickle deserialization succeeds when allow_pickle=True."""
        result = self.SFMGraphSerializer.deserialize_graph(
            self.pickle_bytes, self.StorageFormat.PICKLE, allow_pickle=True
        )
        self.assertIsNotNone(result)

    def test_json_round_trip_unaffected(self):
        """JSON serialization/deserialization continues to work unchanged."""
        json_bytes = self.SFMGraphSerializer.serialize_graph(
            self.graph, self.StorageFormat.JSON
        )
        result = self.SFMGraphSerializer.deserialize_graph(
            json_bytes, self.StorageFormat.JSON
        )
        self.assertIsNotNone(result)

    def test_compressed_json_round_trip_unaffected(self):
        """Compressed JSON round-trip continues to work unchanged."""
        json_bytes = self.SFMGraphSerializer.serialize_graph(
            self.graph, self.StorageFormat.COMPRESSED_JSON
        )
        result = self.SFMGraphSerializer.deserialize_graph(
            json_bytes, self.StorageFormat.COMPRESSED_JSON
        )
        self.assertIsNotNone(result)


if __name__ == "__main__":
    unittest.main()
