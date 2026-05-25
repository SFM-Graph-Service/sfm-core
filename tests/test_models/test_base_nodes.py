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
