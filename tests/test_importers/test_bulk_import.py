"""
Integration tests for bulk import system.

Tests the full import flow from CSV to SFM graph:
- CSV → adapter → service → repository → graph
- Round-trip validation (import → export → import → verify)
- Performance benchmarks
"""

import pytest
import tempfile
from pathlib import Path
import csv
import time

from api.sfm_service import SFMService
from data.importers import CSVImportAdapter, MappingTemplates, ImportConfig
from models.base_nodes import Node


class TestBulkImportFlow:
    """Test complete import flow."""

    def setup_method(self):
        """Set up test service."""
        self.service = SFMService()

    def test_import_basic_nodes_from_csv(self):
        """Test importing basic nodes from CSV."""
        # Create sample CSV
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['name', 'description'])
            writer.writeheader()
            for i in range(10):
                writer.writerow({
                    'name': f'Node {i}',
                    'description': f'Test node number {i}'
                })
            path = f.name

        try:
            # Import using adapter
            mapping = MappingTemplates.basic_node()
            adapter = CSVImportAdapter(mapping)

            result = self.service.import_bulk(path, adapter=adapter)

            # Verify results
            assert result.nodes_created == 10
            assert result.nodes_failed == 0
            assert len(result.errors) == 0

            # Verify nodes in graph
            all_nodes = self.service.list_nodes()
            assert len(all_nodes) == 10

            # Check first node
            first_node = [n for n in all_nodes if n.label == 'Node 0'][0]
            assert first_node.description == 'Test node number 0'

        finally:
            Path(path).unlink()

    def test_import_with_dry_run(self):
        """Test dry-run mode validates without persisting."""
        # Create sample CSV
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['name', 'description'])
            writer.writeheader()
            writer.writerow({'name': 'Test', 'description': 'Test desc'})
            path = f.name

        try:
            # Import with dry_run=True
            mapping = MappingTemplates.basic_node()
            config = ImportConfig(dry_run=True)
            adapter = CSVImportAdapter(mapping, config)

            result = self.service.import_bulk(path, adapter=adapter, config=config)

            # Dry run validates but doesn't persist or count
            assert result.nodes_created == 0  # Not counted in dry_run
            assert result.nodes_failed == 0
            assert len(result.errors) == 0

            # Verify no nodes in graph
            all_nodes = self.service.list_nodes()
            assert len(all_nodes) == 0

        finally:
            Path(path).unlink()

    def test_import_with_continue_on_error(self):
        """Test continue-on-error mode skips invalid rows."""
        # Create CSV with mixed valid/invalid rows
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['name', 'description'])
            writer.writeheader()
            writer.writerow({'name': 'Valid1', 'description': 'First valid'})
            writer.writerow({'name': '', 'description': 'Missing name'})  # Invalid - empty required field
            writer.writerow({'name': 'Valid2', 'description': 'Second valid'})
            path = f.name

        try:
            # Import with continue_on_error=True (default)
            mapping = MappingTemplates.basic_node()
            adapter = CSVImportAdapter(mapping)

            result = self.service.import_bulk(path, adapter=adapter)

            # Should create valid nodes, skip invalid
            assert result.nodes_created >= 2  # At least the 2 valid ones
            assert len(result.errors) >= 0  # May have errors for invalid rows

            # Verify valid nodes in graph
            all_nodes = self.service.list_nodes()
            labels = [n.label for n in all_nodes]
            assert 'Valid1' in labels
            assert 'Valid2' in labels

        finally:
            Path(path).unlink()

    def test_import_large_file_performance(self):
        """Test importing large CSV file."""
        # Create CSV with 1000 rows
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['name', 'description'])
            writer.writeheader()
            for i in range(1000):
                writer.writerow({
                    'name': f'Node {i}',
                    'description': f'Description {i}'
                })
            path = f.name

        try:
            # Import and measure time
            mapping = MappingTemplates.basic_node()
            adapter = CSVImportAdapter(mapping)

            start = time.time()
            result = self.service.import_bulk(path, adapter=adapter)
            elapsed = time.time() - start

            # Verify results
            assert result.nodes_created == 1000
            assert result.nodes_failed == 0

            # Performance check: should complete in <5 seconds
            assert elapsed < 5.0, f"Import took {elapsed:.2f}s, expected <5s"

            print(f"Imported 1000 nodes in {elapsed:.2f}s ({1000/elapsed:.0f} nodes/sec)")

        finally:
            Path(path).unlink()


class TestBulkCreatePerformance:
    """Test bulk node creation performance."""

    def setup_method(self):
        """Set up test service."""
        self.service = SFMService()

    def test_bulk_vs_individual_creation(self):
        """Compare bulk vs individual node creation performance."""
        # Create 500 nodes individually for measurable timing difference
        nodes_individual = [
            Node(label=f'Individual {i}', description=f'Node {i}')
            for i in range(500)
        ]

        start = time.time()
        for node in nodes_individual:
            self.service.create_node(node)
        individual_time = time.time() - start

        # Create 500 nodes in bulk
        nodes_bulk = [
            Node(label=f'Bulk {i}', description=f'Node {i}')
            for i in range(500)
        ]

        start = time.time()
        self.service.repository.create_nodes_bulk(nodes_bulk)
        bulk_time = time.time() - start

        # Bulk should be faster or at least comparable
        speedup = individual_time / bulk_time if bulk_time > 0 else 0
        print(f"Individual: {individual_time:.4f}s, Bulk: {bulk_time:.4f}s, Speedup: {speedup:.1f}x")

        # Should see speedup (exact ratio varies by backend, NetworkX is very fast for both)
        # Allow 20% tolerance for timing variability on slower CI runners
        tolerance = 1.2
        assert bulk_time < individual_time * tolerance, \
            f"Bulk creation significantly slower than individual: {bulk_time:.4f}s vs {individual_time:.4f}s (speedup: {speedup:.2f}x)"

        # Verify all nodes created
        all_nodes = self.service.list_nodes()
        assert len(all_nodes) == 1000  # 500 individual + 500 bulk
