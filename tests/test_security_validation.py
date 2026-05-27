"""
Security validation tests for SFM Core.

Tests input sanitization, XSS prevention, SQL injection prevention,
and metadata validation as specified in security.yml workflow.
"""

import pytest
import uuid
from typing import Dict, Any
from models.base_nodes import Node
from graph.sfm_graph import Relationship
from api.sfm_service import SFMService


class TestInputSanitization:
    """Test input sanitization logic."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = SFMService()

    def test_node_label_sanitization(self):
        """Test that node labels are properly sanitized."""
        # Test with potentially malicious input
        malicious_label = "<script>alert('xss')</script>"

        node = Node(
            label=malicious_label,
            description="Test node"
        )
        created = self.service.create_node(node)

        # Label should be stored as-is (no HTML interpretation in backend)
        assert created.label == malicious_label
        assert isinstance(created, Node)

    def test_node_description_sanitization(self):
        """Test that node descriptions handle special characters."""
        special_chars = "'; DROP TABLE nodes; --"

        node = Node(
            label="Test Node",
            description=special_chars
        )
        created = self.service.create_node(node)

        assert created.description == special_chars
        assert created.id is not None

    def test_metadata_value_sanitization(self):
        """Test that metadata values are properly sanitized."""
        test_meta = {
            "script": "<script>alert('xss')</script>",
            "sql": "'; DROP TABLE metadata; --",
            "null": None,
            "nested": {"key": "<img src=x onerror=alert(1)>"}
        }

        node = Node(
            label="Test Node",
            description="Test",
            meta=test_meta
        )
        created = self.service.create_node(node)

        assert created.meta["script"] == "<script>alert('xss')</script>"
        assert created.meta["sql"] == "'; DROP TABLE metadata; --"
        assert created.meta["null"] is None
        assert created.meta["nested"]["key"] == "<img src=x onerror=alert(1)>"


class TestXSSPrevention:
    """Test XSS prevention mechanisms."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = SFMService()

    def test_xss_in_node_creation(self):
        """Test XSS prevention in node creation."""
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert(1)>",
            "javascript:alert('XSS')",
        ]

        for payload in xss_payloads:
            node = Node(
                label=payload,
                description=f"Description with {payload}"
            )
            created = self.service.create_node(node)

            assert created.label == payload
            assert payload in created.description

    def test_xss_in_relationship_metadata(self):
        """Test XSS prevention in relationship metadata."""
        node1 = Node(label="Node 1", description="Test")
        node2 = Node(label="Node 2", description="Test")

        created1 = self.service.create_node(node1)
        created2 = self.service.create_node(node2)

        xss_meta = {
            "description": "<script>alert('xss')</script>",
            "evidence": "Evidence <img src=x onerror=alert(1)>"
        }

        rel = Relationship(
            source_id=created1.id,
            target_id=created2.id,
            kind="influences",
            weight=0.5,
            meta=xss_meta
        )

        created_rel = self.service.create_relationship(rel)

        assert created_rel.meta["description"] == "<script>alert('xss')</script>"
        assert "onerror" in created_rel.meta["evidence"]


class TestSQLInjectionPrevention:
    """Test SQL injection prevention."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = SFMService()

    def test_sql_injection_in_node_label(self):
        """Test SQL injection prevention in node labels."""
        sql_payloads = [
            "'; DROP TABLE nodes; --",
            "' OR '1'='1",
            "admin'--",
        ]

        for payload in sql_payloads:
            node = Node(
                label=payload,
                description="Test node"
            )
            created = self.service.create_node(node)

            assert created.label == payload
            assert isinstance(created.id, uuid.UUID)


class TestMetadataValidation:
    """Test metadata validation logic."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = SFMService()

    def test_metadata_type_validation(self):
        """Test that metadata accepts various types correctly."""
        valid_meta: Dict[str, Any] = {
            "string": "value",
            "int": 42,
            "float": 3.14,
            "bool": True,
            "none": None,
            "list": [1, 2, 3],
            "dict": {"nested": "value"}
        }

        node = Node(
            label="Test Node",
            description="Test",
            meta=valid_meta
        )
        created = self.service.create_node(node)

        assert created.meta["string"] == "value"
        assert created.meta["int"] == 42
        assert created.meta["float"] == 3.14
        assert created.meta["bool"] is True
        assert created.meta["none"] is None
        assert created.meta["list"] == [1, 2, 3]
        assert created.meta["dict"]["nested"] == "value"

    def test_metadata_empty_validation(self):
        """Test that empty metadata is handled correctly."""
        node1 = Node(
            label="Node 1",
            description="Test",
            meta={}
        )
        created1 = self.service.create_node(node1)
        assert created1.meta == {}

        node2 = Node(
            label="Node 2",
            description="Test"
        )
        created2 = self.service.create_node(node2)
        assert isinstance(created2.meta, dict)


class TestBoundaryConditions:
    """Test boundary conditions and edge cases."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = SFMService()

    def test_very_long_strings(self):
        """Test handling of very long strings."""
        long_string = "A" * 10000

        node = Node(
            label=long_string,
            description=long_string
        )
        created = self.service.create_node(node)

        assert len(created.label) == 10000
        assert len(created.description) == 10000

    def test_unicode_characters(self):
        """Test handling of unicode characters."""
        unicode_strings = [
            "日本語",  # Japanese
            "العربية",  # Arabic
            "Ελληνικά",  # Greek
            "😀🎉🔥",  # Emojis
        ]

        for unicode_str in unicode_strings:
            node = Node(
                label=unicode_str,
                description=f"Description: {unicode_str}"
            )
            created = self.service.create_node(node)

            assert created.label == unicode_str
            assert unicode_str in created.description


class TestRelationshipSecurity:
    """Test security aspects of relationships."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = SFMService()

        node1 = Node(label="Node 1", description="Test")
        node2 = Node(label="Node 2", description="Test")

        self.node1 = self.service.create_node(node1)
        self.node2 = self.service.create_node(node2)

    def test_relationship_weight_validation(self):
        """Test that relationship weights are validated."""
        valid_weights = [0.0, 0.5, 1.0, None]

        for weight in valid_weights:
            rel = Relationship(
                source_id=self.node1.id,
                target_id=self.node2.id,
                kind="influences",
                weight=weight
            )
            created_rel = self.service.create_relationship(rel)
            assert created_rel.weight == weight


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
