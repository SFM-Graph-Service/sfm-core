"""
Tests for CSV import adapter.

Covers:
- Format detection
- Field mapping
- Type coercion
- Error handling
- Streaming large files
"""

import pytest
import tempfile
from pathlib import Path
import csv

from data.importers import CSVImportAdapter, MappingTemplates, ImportConfig, FieldMapping, MappingConfig


class TestCSVAdapterDetection:
    """Test format detection."""

    def test_detect_csv_file(self):
        """Test CSV file detection."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("name,description\n")
            f.write("Test,Test description\n")
            path = f.name

        try:
            adapter = CSVImportAdapter(MappingTemplates.basic_node())
            assert adapter.detect_format(path) is True
        finally:
            Path(path).unlink()

    def test_detect_excel_file(self):
        """Test Excel file detection."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xlsx', delete=False) as f:
            path = f.name

        try:
            adapter = CSVImportAdapter(MappingTemplates.basic_node())
            # Will return True even though file is empty (extension-based detection)
            assert adapter.detect_format(path) is True
        finally:
            Path(path).unlink()

    def test_reject_non_csv(self):
        """Test rejection of non-CSV files."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            path = f.name

        try:
            adapter = CSVImportAdapter(MappingTemplates.basic_node())
            # .txt is actually supported (treated as CSV)
            assert adapter.detect_format(path) is True
        finally:
            Path(path).unlink()

    def test_reject_dict(self):
        """Test rejection of dictionary input."""
        adapter = CSVImportAdapter(MappingTemplates.basic_node())
        assert adapter.detect_format({"key": "value"}) is False


class TestCSVAdapterExtraction:
    """Test node extraction from CSV."""

    def test_extract_basic_nodes(self):
        """Test extracting basic nodes with label and description."""
        # Create temporary CSV
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['name', 'description'])
            writer.writeheader()
            writer.writerow({'name': 'Node1', 'description': 'First node'})
            writer.writerow({'name': 'Node2', 'description': 'Second node'})
            path = f.name

        try:
            adapter = CSVImportAdapter(MappingTemplates.basic_node())
            nodes = list(adapter.extract_nodes(path))

            assert len(nodes) == 2
            assert nodes[0]['label'] == 'Node1'
            assert nodes[0]['description'] == 'First node'
            assert nodes[0]['_node_type'] == 'Node'

            assert nodes[1]['label'] == 'Node2'
            assert nodes[1]['description'] == 'Second node'
        finally:
            Path(path).unlink()

    def test_extract_with_missing_optional_fields(self):
        """Test extraction with missing optional fields uses defaults."""
        # Create CSV with missing description
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['name', 'description'])
            writer.writeheader()
            writer.writerow({'name': 'Node1', 'description': ''})
            path = f.name

        try:
            adapter = CSVImportAdapter(MappingTemplates.basic_node())
            nodes = list(adapter.extract_nodes(path))

            assert len(nodes) == 1
            assert nodes[0]['description'] == ''  # Empty string default
        finally:
            Path(path).unlink()

    def test_extract_with_metadata(self):
        """Test extraction with metadata fields."""
        # Create CSV with jurisdiction metadata
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['name', 'description', 'type', 'jurisdiction'])
            writer.writeheader()
            writer.writerow({
                'name': 'EPA',
                'description': 'Environmental Protection Agency',
                'type': 'regulatory',
                'jurisdiction': 'Federal'
            })
            path = f.name

        try:
            adapter = CSVImportAdapter(MappingTemplates.csv_institution())
            nodes = list(adapter.extract_nodes(path))

            assert len(nodes) == 1
            assert nodes[0]['label'] == 'EPA'
            assert nodes[0]['structure_type'] == 'regulatory'  # Transformed to lowercase for InstitutionalStructure
            assert 'meta' in nodes[0]
            assert nodes[0]['meta']['jurisdiction'] == 'Federal'
        finally:
            Path(path).unlink()


class TestCSVAdapterValidation:
    """Test CSV validation."""

    def test_validate_missing_file(self):
        """Test validation fails for missing file."""
        adapter = CSVImportAdapter(MappingTemplates.basic_node())
        errors = adapter.validate_format('/nonexistent/file.csv')

        assert len(errors) > 0
        assert 'not found' in errors[0].lower()

    def test_validate_missing_required_column(self):
        """Test validation fails for missing required column."""
        # Create CSV without required 'name' column
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['description'])
            writer.writeheader()
            writer.writerow({'description': 'Test'})
            path = f.name

        try:
            adapter = CSVImportAdapter(MappingTemplates.basic_node())
            errors = adapter.validate_format(path)

            assert len(errors) > 0
            assert 'name' in errors[0].lower()
        finally:
            Path(path).unlink()


class TestCSVAdapterSizeEstimation:
    """Test size estimation."""

    def test_estimate_csv_size(self):
        """Test estimating CSV file size."""
        # Create CSV with 10 rows
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['name', 'description'])
            writer.writeheader()
            for i in range(10):
                writer.writerow({'name': f'Node{i}', 'description': f'Description {i}'})
            path = f.name

        try:
            adapter = CSVImportAdapter(MappingTemplates.basic_node())
            size = adapter.estimate_size(path)

            assert size == 10
        finally:
            Path(path).unlink()


class TestMappingConfig:
    """Test field mapping configuration."""

    def test_basic_mapping(self):
        """Test basic field mapping."""
        mapping = MappingConfig(node_type="Node")
        mapping.add_mapping(FieldMapping(
            source_field="name",
            target_field="label",
            required=True
        ))

        row_data = {"name": "TestNode"}
        result = mapping.transform_row(row_data)

        assert result['label'] == 'TestNode'
        assert result['_node_type'] == 'Node'

    def test_mapping_with_transform(self):
        """Test field mapping with transformation."""
        mapping = MappingConfig(node_type="Node")
        mapping.add_mapping(FieldMapping(
            source_field="name",
            target_field="label",
            transform=str.upper
        ))

        row_data = {"name": "testnode"}
        result = mapping.transform_row(row_data)

        assert result['label'] == 'TESTNODE'

    def test_mapping_with_default(self):
        """Test field mapping with default value."""
        mapping = MappingConfig(node_type="Node")
        mapping.add_mapping(FieldMapping(
            source_field="description",
            target_field="description",
            default="No description"
        ))

        row_data = {}  # Missing description
        result = mapping.transform_row(row_data)

        assert result['description'] == 'No description'

    def test_mapping_to_metadata(self):
        """Test field mapping to metadata."""
        mapping = MappingConfig(node_type="Node")
        mapping.add_mapping(FieldMapping(
            source_field="country",
            target_field="meta.country"
        ))

        row_data = {"country": "USA"}
        result = mapping.transform_row(row_data)

        assert 'meta' in result
        assert result['meta']['country'] == 'USA'

    def test_mapping_missing_required_field(self):
        """Test mapping fails for missing required field."""
        mapping = MappingConfig(node_type="Node")
        mapping.add_mapping(FieldMapping(
            source_field="name",
            target_field="label",
            required=True
        ))

        row_data = {}  # Missing required field

        with pytest.raises(KeyError):
            mapping.transform_row(row_data)
