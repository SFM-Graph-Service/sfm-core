"""
Unit tests for base_nodes module.
"""

import pytest
import uuid
from datetime import datetime
from models.base_nodes import Node


class TestNode:
    """Test suite for Node base class."""

    def test_node_instantiation(self):
        """Test basic Node instantiation."""
        node = Node(label="Test Node")
        assert node.label == "Test Node"
        assert isinstance(node.id, uuid.UUID)
        assert node.version == 1
        assert node.certainty == 1.0

    def test_node_with_description(self):
        """Test Node with optional description."""
        node = Node(label="Test", description="Test description")
        assert node.description == "Test description"

    def test_node_with_metadata(self):
        """Test Node with custom metadata."""
        meta = {"key1": "value1", "key2": "value2"}
        node = Node(label="Test", meta=meta)
        assert node.meta == meta
        assert node.meta["key1"] == "value1"

    def test_node_default_timestamps(self):
        """Test that timestamps are set correctly."""
        node = Node(label="Test")
        assert isinstance(node.created_at, datetime)
        assert node.modified_at is None

    def test_node_versioning(self):
        """Test version tracking."""
        node = Node(label="Test")
        assert node.version == 1
        assert node.previous_version_id is None

    def test_node_certainty_validation(self):
        """Test certainty value range."""
        node = Node(label="Test", certainty=0.5)
        assert node.certainty == 0.5

    def test_node_data_quality(self):
        """Test data quality field."""
        node = Node(label="Test", data_quality="high")
        assert node.data_quality == "high"

    def test_node_iteration(self):
        """Test that Node can be iterated."""
        node = Node(label="Test", description="Desc")
        attrs = dict(node)
        assert "label" in attrs
        assert "description" in attrs
        assert attrs["label"] == "Test"

    def test_node_with_custom_id(self):
        """Test Node with pre-assigned UUID."""
        custom_id = uuid.uuid4()
        node = Node(label="Test", id=custom_id)
        assert node.id == custom_id

    def test_node_empty_metadata(self):
        """Test Node with empty metadata dict."""
        node = Node(label="Test")
        assert node.meta == {}
        assert isinstance(node.meta, dict)

    def test_node_certainty_boundaries(self):
        """Test certainty at boundaries."""
        node_low = Node(label="Low", certainty=0.0)
        node_high = Node(label="High", certainty=1.0)
        assert node_low.certainty == 0.0
        assert node_high.certainty == 1.0

    def test_node_modified_timestamp(self):
        """Test setting modified timestamp."""
        now = datetime.now()
        node = Node(label="Test", modified_at=now)
        assert node.modified_at == now

    def test_node_version_with_previous(self):
        """Test versioning with previous version reference."""
        prev_id = uuid.uuid4()
        node = Node(label="Test", version=2, previous_version_id=prev_id)
        assert node.version == 2
        assert node.previous_version_id == prev_id

    def test_node_all_fields(self):
        """Test Node with all fields populated."""
        node_id = uuid.uuid4()
        prev_id = uuid.uuid4()
        created = datetime.now()
        modified = datetime.now()
        meta = {"source": "test", "category": "example"}

        node = Node(
            label="Complete Node",
            description="Fully specified node",
            id=node_id,
            meta=meta,
            version=3,
            created_at=created,
            modified_at=modified,
            certainty=0.85,
            data_quality="verified",
            previous_version_id=prev_id,
        )

        assert node.label == "Complete Node"
        assert node.description == "Fully specified node"
        assert node.id == node_id
        assert node.meta == meta
        assert node.version == 3
        assert node.created_at == created
        assert node.modified_at == modified
        assert node.certainty == 0.85
        assert node.data_quality == "verified"
        assert node.previous_version_id == prev_id


class TestNodeComposition:
    """Test Node composition and combination scenarios."""

    def test_multiple_nodes_different_labels(self):
        """Test creating multiple nodes with different labels."""
        nodes = [Node(label=f"Node {i}") for i in range(5)]
        assert len(nodes) == 5
        assert all(isinstance(n.id, uuid.UUID) for n in nodes)

    def test_node_metadata_update(self):
        """Test updating node metadata."""
        node = Node(label="Test")
        node.meta["new_key"] = "new_value"
        assert node.meta["new_key"] == "new_value"

    def test_node_certainty_decimal(self):
        """Test certainty with decimal values."""
        node = Node(label="Test", certainty=0.123456)
        assert node.certainty == 0.123456

    def test_node_version_increment(self):
        """Test version incrementing scenario."""
        node_v1 = Node(label="Test")
        node_v2 = Node(
            label="Test",
            version=node_v1.version + 1,
            previous_version_id=node_v1.id,
        )
        assert node_v2.version == 2
        assert node_v2.previous_version_id == node_v1.id

    def test_node_dict_conversion(self):
        """Test converting Node to dict via iteration."""
        node = Node(label="Test", description="Desc")
        node_dict = {k: v for k, v in node}
        assert "label" in node_dict
        assert "description" in node_dict
        assert node_dict["label"] == "Test"

    def test_node_with_none_values(self):
        """Test Node with explicitly None values."""
        node = Node(
            label="Test",
            description=None,
            modified_at=None,
            data_quality=None,
        )
        assert node.description is None
        assert node.modified_at is None
        assert node.data_quality is None

    def test_node_timestamp_ordering(self):
        """Test timestamp ordering."""
        node1 = Node(label="First")
        node2 = Node(label="Second")
        assert node2.created_at >= node1.created_at


class TestNodeNegativeTests:
    """Negative test cases for Node class."""

    def test_node_empty_label(self):
        """Test Node with empty label (should still work)."""
        node = Node(label="")
        assert node.label == ""

    def test_node_with_special_characters(self):
        """Test Node label with special characters."""
        node = Node(label="Test @#$% Node")
        assert node.label == "Test @#$% Node"

    def test_node_large_metadata(self):
        """Test Node with large metadata dict."""
        large_meta = {f"key{i}": f"value{i}" for i in range(100)}
        node = Node(label="Test", meta=large_meta)
        assert len(node.meta) == 100

    def test_node_unicode_label(self):
        """Test Node with Unicode characters."""
        node = Node(label="测试节点")
        assert node.label == "测试节点"

    def test_node_long_description(self):
        """Test Node with very long description."""
        long_desc = "A" * 10000
        node = Node(label="Test", description=long_desc)
        assert len(node.description) == 10000
