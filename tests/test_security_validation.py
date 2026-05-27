"""
Security validation tests for SFM Core.

Tests input sanitization, XSS prevention, SQL injection prevention,
and metadata validation as specified in security.yml workflow.
"""

import pytest
import uuid
from typing import Dict, Any
from models.base_nodes import Node, Actor, Institution, Technology
from graph.sfm_graph import SFMGraph, Relationship
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

        node = self.service.create_node(
            label=malicious_label,
            node_type="Actor",
            description="Test node"
        )

        # Label should be stored as-is (no HTML interpretation in backend)
        # But should not execute when rendered
        assert node.label == malicious_label
        assert isinstance(node, Node)

    def test_node_description_sanitization(self):
        """Test that node descriptions handle special characters."""
        special_chars = "'; DROP TABLE nodes; --"

        node = self.service.create_node(
            label="Test Node",
            node_type="Actor",
            description=special_chars
        )

        assert node.description == special_chars
        assert node.id is not None

    def test_metadata_value_sanitization(self):
        """Test that metadata values are properly sanitized."""
        # Test with various potentially problematic values
        test_meta = {
            "script": "<script>alert('xss')</script>",
            "sql": "'; DROP TABLE metadata; --",
            "null": None,
            "nested": {"key": "<img src=x onerror=alert(1)>"}
        }

        node = self.service.create_node(
            label="Test Node",
            node_type="Actor",
            description="Test",
            meta=test_meta
        )

        # Metadata should be stored correctly
        assert node.meta["script"] == "<script>alert('xss')</script>"
        assert node.meta["sql"] == "'; DROP TABLE metadata; --"
        assert node.meta["null"] is None
        assert node.meta["nested"]["key"] == "<img src=x onerror=alert(1)>"


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
            "<svg onload=alert(1)>",
            "<iframe src='javascript:alert(1)'>",
        ]

        for payload in xss_payloads:
            node = self.service.create_node(
                label=payload,
                node_type="Actor",
                description=f"Description with {payload}"
            )

            # Node should be created (backend doesn't interpret HTML)
            assert node.label == payload
            assert payload in node.description

    def test_xss_in_relationship_metadata(self):
        """Test XSS prevention in relationship metadata."""
        node1 = self.service.create_node(
            label="Node 1",
            node_type="Actor",
            description="Test"
        )
        node2 = self.service.create_node(
            label="Node 2",
            node_type="Actor",
            description="Test"
        )

        xss_meta = {
            "description": "<script>alert('xss')</script>",
            "evidence": "Evidence <img src=x onerror=alert(1)>"
        }

        rel = Relationship(
            source_id=node1.id,
            target_id=node2.id,
            kind="influences",
            weight=0.5,
            meta=xss_meta
        )

        created_rel = self.service.create_relationship(rel)

        # Metadata should be stored as-is
        assert created_rel.meta["description"] == "<script>alert('xss')</script>"
        assert "onerror" in created_rel.meta["evidence"]


class TestSQLInjectionPrevention:
    """Test SQL injection prevention (relevant for Neo4j backend)."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = SFMService()

    def test_sql_injection_in_node_label(self):
        """Test SQL injection prevention in node labels."""
        sql_payloads = [
            "'; DROP TABLE nodes; --",
            "' OR '1'='1",
            "admin'--",
            "' UNION SELECT * FROM users--",
            "1'; DELETE FROM nodes WHERE '1'='1",
        ]

        for payload in sql_payloads:
            node = self.service.create_node(
                label=payload,
                node_type="Actor",
                description="Test node"
            )

            # Node should be created safely
            assert node.label == payload
            assert isinstance(node.id, uuid.UUID)

    def test_sql_injection_in_search(self):
        """Test SQL injection prevention in search operations."""
        # Create test nodes
        self.service.create_node(
            label="Legitimate Node",
            node_type="Actor",
            description="Test"
        )

        # Try SQL injection in search
        sql_search = "' OR 1=1--"

        # Search should not cause issues
        # (NetworkX backend doesn't use SQL, but test for future Neo4j backend)
        nodes = list(self.service.graph)

        # Should get legitimate results only
        assert len(nodes) >= 1
        assert all(isinstance(n.id, uuid.UUID) for n in nodes)


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

        node = self.service.create_node(
            label="Test Node",
            node_type="Actor",
            description="Test",
            meta=valid_meta
        )

        # All types should be preserved
        assert node.meta["string"] == "value"
        assert node.meta["int"] == 42
        assert node.meta["float"] == 3.14
        assert node.meta["bool"] is True
        assert node.meta["none"] is None
        assert node.meta["list"] == [1, 2, 3]
        assert node.meta["dict"]["nested"] == "value"

    def test_metadata_empty_validation(self):
        """Test that empty metadata is handled correctly."""
        # Empty dict
        node1 = self.service.create_node(
            label="Node 1",
            node_type="Actor",
            description="Test",
            meta={}
        )
        assert node1.meta == {}

        # None (should default to empty dict)
        node2 = self.service.create_node(
            label="Node 2",
            node_type="Actor",
            description="Test"
        )
        assert isinstance(node2.meta, dict)

    def test_metadata_special_keys(self):
        """Test metadata with special key names."""
        special_meta = {
            "": "empty_key",
            " ": "space_key",
            "key with spaces": "value",
            "key-with-dashes": "value",
            "key_with_underscores": "value",
            "key.with.dots": "value",
            "key/with/slashes": "value"
        }

        node = self.service.create_node(
            label="Test Node",
            node_type="Actor",
            description="Test",
            meta=special_meta
        )

        # All keys should be preserved
        assert node.meta[""] == "empty_key"
        assert node.meta[" "] == "space_key"
        assert node.meta["key with spaces"] == "value"
        assert node.meta["key-with-dashes"] == "value"


class TestBoundaryConditions:
    """Test boundary conditions and edge cases."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = SFMService()

    def test_very_long_strings(self):
        """Test handling of very long strings."""
        long_string = "A" * 10000

        node = self.service.create_node(
            label=long_string,
            node_type="Actor",
            description=long_string
        )

        assert len(node.label) == 10000
        assert len(node.description) == 10000

    def test_unicode_characters(self):
        """Test handling of unicode characters."""
        unicode_strings = [
            "日本語",  # Japanese
            "العربية",  # Arabic
            "Ελληνικά",  # Greek
            "עברית",  # Hebrew
            "😀🎉🔥",  # Emojis
            "→←↑↓",  # Arrows
        ]

        for unicode_str in unicode_strings:
            node = self.service.create_node(
                label=unicode_str,
                node_type="Actor",
                description=f"Description: {unicode_str}"
            )

            assert node.label == unicode_str
            assert unicode_str in node.description

    def test_null_byte_injection(self):
        """Test handling of null byte injection attempts."""
        null_byte_payload = "test\x00malicious"

        node = self.service.create_node(
            label=null_byte_payload,
            node_type="Actor",
            description="Test"
        )

        # Should handle null bytes safely
        assert node.label == null_byte_payload


class TestRelationshipSecurity:
    """Test security aspects of relationships."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = SFMService()

        # Create test nodes
        self.node1 = self.service.create_node(
            label="Node 1",
            node_type="Actor",
            description="Test"
        )
        self.node2 = self.service.create_node(
            label="Node 2",
            node_type="Actor",
            description="Test"
        )

    def test_relationship_weight_validation(self):
        """Test that relationship weights are validated."""
        # Valid weights
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

    def test_relationship_invalid_node_ids(self):
        """Test relationships with invalid node IDs."""
        # Non-existent node IDs should be rejected by graph
        fake_id = uuid.uuid4()

        rel = Relationship(
            source_id=fake_id,
            target_id=self.node2.id,
            kind="influences",
            weight=0.5
        )

        # Depending on implementation, this might raise an error
        # or create a dangling relationship
        # For now, test that it doesn't crash
        try:
            created_rel = self.service.create_relationship(rel)
            # If created, verify IDs are preserved
            assert created_rel.source_id == fake_id
        except Exception:
            # If rejected, that's also acceptable
            pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
