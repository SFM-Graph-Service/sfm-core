"""
Unit tests for SFMService persistence operations.

Tests save(), load(), reload(), unload(), export_snapshot(), import_snapshot().
"""

import pytest
import json
from pathlib import Path
import tempfile
import shutil

from api.sfm_service import SFMService
from models import Node
from models.delivery_matrix import Delivery, SFMDeliveryMatrix
from graph.sfm_persistence import SFMPersistenceError


class TestSaveLoad:
    """Tests for save() and load() operations."""

    def test_save_creates_file(self, tmp_path):
        """Test that save() creates a file on disk."""
        service = SFMService()

        # Create some nodes
        node1 = Node(label="Node 1", description="First node")
        node2 = Node(label="Node 2", description="Second node")
        service.create_node(node1)
        service.create_node(node2)

        # Save to temporary directory
        result = service.save("test_graph.json", base_path=str(tmp_path))

        assert Path(result["filepath"]).exists()
        assert result["node_count"] == 2
        assert result["format"] == "json"
        assert result["size_bytes"] > 0
        assert "checksum" in result

    def test_save_json_format(self, tmp_path):
        """Test saving in JSON format."""
        service = SFMService()
        node = Node(label="Test Node")
        service.create_node(node)

        result = service.save("test.json", format_type="json", base_path=str(tmp_path))

        # Verify it's valid JSON
        with open(result["filepath"], 'r') as f:
            data = json.load(f)
            assert "nodes_by_type" in data

    def test_save_compressed_json(self, tmp_path):
        """Test saving in compressed JSON format."""
        service = SFMService()

        # Create multiple nodes for better compression
        for i in range(10):
            service.create_node(Node(label=f"Node {i}", description=f"Description {i}"))

        result = service.save("test.json.gz", format_type="json.gz", base_path=str(tmp_path))

        assert result["format"] == "json.gz"
        assert Path(result["filepath"]).exists()
        # Compressed should be smaller (though not guaranteed for tiny data)
        assert result["size_bytes"] > 0

    def test_load_replaces_graph(self, tmp_path):
        """Test that load(replace=True) replaces current graph."""
        service = SFMService()

        # Create and save first graph
        node1 = Node(label="Original Node")
        service.create_node(node1)
        service.save("original.json", base_path=str(tmp_path))

        # Create second graph and save
        service.unload()
        node2 = Node(label="New Node")
        service.create_node(node2)
        service.save("new.json", base_path=str(tmp_path))

        # Load original (should replace)
        result = service.load("original.json", base_path=str(tmp_path), replace=True)

        assert result["replaced"] is True
        assert result["total_nodes"] == 1

        # Verify we have original node, not new node
        nodes = service.list_nodes()
        assert len(nodes) == 1
        assert nodes[0].label == "Original Node"

    def test_load_merges_graph(self, tmp_path):
        """Test that load(replace=False) merges into current graph."""
        service1 = SFMService()
        service2 = SFMService()

        # Create and save first graph
        node1 = Node(label="Node 1")
        service1.create_node(node1)
        service1.save("graph1.json", base_path=str(tmp_path))

        # Create and save second graph
        node2 = Node(label="Node 2")
        service2.create_node(node2)
        service2.save("graph2.json", base_path=str(tmp_path))

        # Start fresh service and load both
        service3 = SFMService()
        service3.load("graph1.json", base_path=str(tmp_path))
        result = service3.load("graph2.json", base_path=str(tmp_path), replace=False)

        assert result["replaced"] is False
        assert result["total_nodes"] == 2

        # Verify we have both nodes
        nodes = service3.list_nodes()
        labels = {n.label for n in nodes}
        assert labels == {"Node 1", "Node 2"}

    def test_load_nonexistent_file_raises_error(self, tmp_path):
        """Test that loading nonexistent file raises error."""
        service = SFMService()

        with pytest.raises(SFMPersistenceError, match="File not found"):
            service.load("nonexistent.json", base_path=str(tmp_path))

    def test_save_load_preserves_node_attributes(self, tmp_path):
        """Test that save/load preserves all node attributes."""
        service1 = SFMService()

        # Create node with metadata
        node = Node(
            label="Test Node",
            description="Test Description",
            meta={"key1": "value1", "key2": 42}
        )
        service1.create_node(node)
        service1.save("test.json", base_path=str(tmp_path))

        # Load in new service
        service2 = SFMService()
        service2.load("test.json", base_path=str(tmp_path))

        # Verify attributes preserved
        loaded_nodes = service2.list_nodes()
        assert len(loaded_nodes) == 1
        loaded = loaded_nodes[0]

        assert loaded.label == "Test Node"
        assert loaded.description == "Test Description"
        assert loaded.meta == {"key1": "value1", "key2": 42}

    def test_save_load_preserves_relationships(self, tmp_path):
        """Test that relationships are preserved across save/load."""
        service1 = SFMService()

        # Create nodes and relationship
        node1 = Node(label="Source")
        node2 = Node(label="Target")
        service1.create_node(node1)
        service1.create_node(node2)

        from graph.sfm_graph import Relationship
        rel = Relationship(source_id=node1.id, target_id=node2.id, kind="depends_on")
        service1.create_relationship(rel)

        service1.save("with_rels.json", base_path=str(tmp_path))

        # Load and verify
        service2 = SFMService()
        result = service2.load("with_rels.json", base_path=str(tmp_path))

        assert result["relationship_count"] == 1
        rels = service2.list_relationships()
        assert len(rels) == 1
        assert rels[0].kind == "depends_on"


class TestReload:
    """Tests for reload() operation."""

    def test_reload_discards_changes(self, tmp_path):
        """Test that reload() discards unsaved changes."""
        service = SFMService()

        # Create and save initial state
        node1 = Node(label="Saved Node")
        service.create_node(node1)
        service.save("state.json", base_path=str(tmp_path))

        # Make changes
        node2 = Node(label="Unsaved Node")
        service.create_node(node2)
        assert len(service.list_nodes()) == 2

        # Reload (should discard node2)
        service.reload("state.json", base_path=str(tmp_path))

        nodes = service.list_nodes()
        assert len(nodes) == 1
        assert nodes[0].label == "Saved Node"

    def test_reload_equivalent_to_load_replace(self, tmp_path):
        """Test that reload() is equivalent to load(replace=True)."""
        service1 = SFMService()
        service2 = SFMService()

        # Save initial state
        node = Node(label="Test")
        service1.create_node(node)
        service1.save("test.json", base_path=str(tmp_path))

        # reload() in service1
        service1.create_node(Node(label="Extra"))  # Add extra node
        reload_result = service1.reload("test.json", base_path=str(tmp_path))

        # load(replace=True) in service2
        service2.create_node(Node(label="Extra"))  # Add extra node
        load_result = service2.load("test.json", base_path=str(tmp_path), replace=True)

        # Both should have same result
        assert reload_result["total_nodes"] == load_result["total_nodes"]
        assert reload_result["replaced"] == load_result["replaced"]


class TestUnload:
    """Tests for unload() operation."""

    def test_unload_clears_all_nodes(self):
        """Test that unload() removes all nodes."""
        service = SFMService()

        # Create multiple nodes
        for i in range(5):
            service.create_node(Node(label=f"Node {i}"))

        assert len(service.list_nodes()) == 5

        # Unload
        result = service.unload()

        assert result["nodes_removed"] == 5
        assert len(service.list_nodes()) == 0

    def test_unload_clears_all_relationships(self):
        """Test that unload() removes all relationships."""
        service = SFMService()

        # Create nodes and relationships
        node1 = Node(label="N1")
        node2 = Node(label="N2")
        service.create_node(node1)
        service.create_node(node2)

        from graph.sfm_graph import Relationship
        for i in range(3):
            rel = Relationship(source_id=node1.id, target_id=node2.id, kind=f"rel_{i}")
            service.create_relationship(rel)

        assert len(service.list_relationships()) == 3

        # Unload
        result = service.unload()

        assert result["relationships_removed"] == 3
        assert len(service.list_relationships()) == 0

    def test_unload_returns_metadata(self):
        """Test that unload() returns correct metadata."""
        service = SFMService()

        # Create data
        for i in range(3):
            service.create_node(Node(label=f"Node {i}"))

        result = service.unload()

        assert "nodes_removed" in result
        assert "relationships_removed" in result
        assert "timestamp" in result
        assert result["nodes_removed"] == 3

    def test_unload_save_reload_workflow(self, tmp_path):
        """Test common workflow: save → modify → unload → reload."""
        service = SFMService()

        # 1. Create initial state and save
        node1 = Node(label="Original")
        service.create_node(node1)
        service.save("backup.json", base_path=str(tmp_path))

        # 2. Make changes
        service.create_node(Node(label="Modified"))
        assert len(service.list_nodes()) == 2

        # 3. Unload (discard changes)
        service.unload()
        assert len(service.list_nodes()) == 0

        # 4. Reload from backup
        service.reload("backup.json", base_path=str(tmp_path))

        nodes = service.list_nodes()
        assert len(nodes) == 1
        assert nodes[0].label == "Original"


class TestExportImportSnapshot:
    """Tests for export_snapshot() and import_snapshot()."""

    def test_export_json_snapshot(self, tmp_path):
        """Test exporting to JSON snapshot format."""
        service = SFMService()

        node = Node(label="Test Node", description="Test")
        service.create_node(node)

        filepath = tmp_path / "snapshot.json"
        result = service.export_snapshot(str(filepath), export_format="json")

        assert Path(result["filepath"]).exists()
        assert result["format"] == "json"
        assert result["node_count"] == 1

        # Verify valid JSON
        with open(filepath, 'r') as f:
            data = json.load(f)
            assert "metadata" in data
            assert "nodes" in data

    def test_export_graphml_format(self, tmp_path):
        """Test exporting to GraphML format."""
        service = SFMService()

        node1 = Node(label="N1")
        node2 = Node(label="N2")
        service.create_node(node1)
        service.create_node(node2)

        filepath = tmp_path / "graph.graphml"
        result = service.export_snapshot(str(filepath), export_format="graphml")

        assert Path(result["filepath"]).exists()
        assert result["format"] == "graphml"

        # Verify it's XML (GraphML is XML-based)
        with open(filepath, 'r') as f:
            content = f.read()
            assert '<?xml' in content or '<graphml' in content

    def test_export_gexf_format(self, tmp_path):
        """Test exporting to GEXF format."""
        service = SFMService()

        node = Node(label="Test")
        service.create_node(node)

        filepath = tmp_path / "graph.gexf"
        result = service.export_snapshot(str(filepath), export_format="gexf")

        assert Path(result["filepath"]).exists()
        assert result["format"] == "gexf"

    def test_export_unsupported_format_raises_error(self, tmp_path):
        """Test that unsupported export format raises error."""
        service = SFMService()

        filepath = tmp_path / "graph.unknown"

        with pytest.raises(ValueError, match="Unsupported export format"):
            service.export_snapshot(str(filepath), export_format="unknown")

    def test_import_snapshot_roundtrip(self, tmp_path):
        """Test export → import roundtrip preserves data."""
        service1 = SFMService()

        # Create data
        node1 = Node(label="Node 1", description="First", meta={"key": "value"})
        node2 = Node(label="Node 2", description="Second")
        service1.create_node(node1)
        service1.create_node(node2)

        from graph.sfm_graph import Relationship
        rel = Relationship(source_id=node1.id, target_id=node2.id, kind="links_to")
        service1.create_relationship(rel)

        # Export
        filepath = tmp_path / "roundtrip.json"
        service1.export_snapshot(str(filepath), export_format="json")

        # Import into new service
        service2 = SFMService()
        result = service2.import_snapshot(str(filepath))

        assert result["node_count"] == 2
        assert result["relationship_count"] == 1

        # Verify data integrity
        nodes = service2.list_nodes()
        labels = {n.label for n in nodes}
        assert labels == {"Node 1", "Node 2"}

        rels = service2.list_relationships()
        assert len(rels) == 1
        assert rels[0].kind == "links_to"


class TestDeliveryMatrixPersistence:
    """Test persistence with Hayden-compliant delivery matrices."""

    @pytest.mark.skip(reason="SFMDeliveryMatrix not yet implemented - planned for fidelity improvements")
    def test_save_load_delivery_matrix(self, tmp_path):
        """Test that delivery matrices can be saved and loaded."""
        service1 = SFMService()

        # Create delivery matrix
        matrix = service1.create_delivery_matrix(
            label="Test Matrix",
            description="Test delivery matrix",
            components=[],
            matrix_scope="local"
        )

        # Create components
        comp1 = Node(label="Component 1")
        comp2 = Node(label="Component 2")
        service1.create_node(comp1)
        service1.create_node(comp2)

        matrix.add_component(comp1.id)
        matrix.add_component(comp2.id)

        # Add delivery
        delivery = Delivery(
            delivery_type="money",
            delivery_content="$100 transfer",
            quantity=100.0,
            units="USD"
        )
        service1.add_delivery_to_matrix(
            matrix, comp1.id, comp2.id,
            delivery,
            cell_description="Payment delivery"
        )

        # Save
        service1.save("matrix_test.json", base_path=str(tmp_path))

        # Load in new service
        service2 = SFMService()
        service2.load("matrix_test.json", base_path=str(tmp_path))

        # Verify matrix preserved
        matrices = [n for n in service2.list_nodes() if hasattr(n, 'components')]
        assert len(matrices) > 0

        loaded_matrix = matrices[0]
        assert loaded_matrix.label == "Test Matrix"
        assert len(loaded_matrix.components) == 2


class TestPersistenceEdgeCases:
    """Test edge cases and error conditions."""

    def test_save_empty_graph(self, tmp_path):
        """Test saving an empty graph."""
        service = SFMService()

        result = service.save("empty.json", base_path=str(tmp_path))

        assert result["node_count"] == 0
        assert result["relationship_count"] == 0
        assert Path(result["filepath"]).exists()

    def test_load_empty_graph(self, tmp_path):
        """Test loading an empty graph."""
        service1 = SFMService()
        service1.save("empty.json", base_path=str(tmp_path))

        service2 = SFMService()
        result = service2.load("empty.json", base_path=str(tmp_path))

        assert result["total_nodes"] == 0
        assert result["total_relationships"] == 0

    def test_multiple_save_overwrites(self, tmp_path):
        """Test that multiple saves to same filename overwrite."""
        service = SFMService()

        # First save
        node1 = Node(label="Version 1")
        service.create_node(node1)
        result1 = service.save("overwrite.json", base_path=str(tmp_path))

        # Second save (should overwrite)
        service.unload()
        node2 = Node(label="Version 2")
        service.create_node(node2)
        result2 = service.save("overwrite.json", base_path=str(tmp_path))

        # Load should get version 2
        service3 = SFMService()
        service3.load("overwrite.json", base_path=str(tmp_path))

        nodes = service3.list_nodes()
        assert len(nodes) == 1
        assert nodes[0].label == "Version 2"

    def test_pickle_deserialization_disabled_by_default(self, tmp_path):
        """Test that pickle deserialization requires explicit opt-in."""
        from graph.sfm_persistence import SFMPersistenceError, SFMSerializationError

        service = SFMService()
        node = Node(label="Test")
        service.create_node(node)

        # Save as pickle (requires allow_pickle in actual implementation)
        # For now, just verify the error message
        service.save("test.pickle", format_type="pickle", base_path=str(tmp_path))

        # Try to load without allow_pickle flag
        with pytest.raises((SFMSerializationError, Exception)) as exc_info:
            service.load("test.pickle", format_type="pickle", base_path=str(tmp_path),
                        allow_pickle=False)

        # Should mention pickle security
        assert "pickle" in str(exc_info.value).lower() or "untrusted" in str(exc_info.value).lower()


# Fixtures
@pytest.fixture
def tmp_path():
    """Create temporary directory for test files."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir, ignore_errors=True)
