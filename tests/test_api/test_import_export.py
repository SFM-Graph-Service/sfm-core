"""
Tests for import/export REST API endpoints.

Covers:
- GET /import/formats - List supported formats
- POST /import/csv - Upload and import CSV/Excel files
- POST /import/oecd - OECD API import (placeholder)
- POST /import/worldbank - World Bank API import (placeholder)
"""

import pytest
import tempfile
import csv
from pathlib import Path
from io import BytesIO

from fastapi.testclient import TestClient

from api.rest.app import create_app


class TestImportFormatsEndpoint:
    """Test GET /import/formats endpoint."""

    def setup_method(self):
        """Set up test client."""
        self.app = create_app()
        self.client = TestClient(self.app)

    def test_list_formats(self):
        """Test listing supported import formats."""
        response = self.client.get("/api/v1/import/formats")

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "formats" in data
        assert len(data["formats"]) >= 5  # CSV, OECD, World Bank, SDMX, RDF

        # Check CSV format details
        csv_format = next(f for f in data["formats"] if f["format_name"] == "csv")
        assert csv_format["display_name"] == "CSV/Excel"
        assert csv_format["adapter_available"] is True
        assert ".csv" in csv_format["file_extensions"]
        assert ".xlsx" in csv_format["file_extensions"]

        # Check OECD format (not yet implemented)
        oecd_format = next(f for f in data["formats"] if f["format_name"] == "oecd")
        assert oecd_format["adapter_available"] is False


class TestCSVImportEndpoint:
    """Test POST /import/csv endpoint."""

    def setup_method(self):
        """Set up test client."""
        self.app = create_app()
        self.client = TestClient(self.app)

    def test_import_csv_success(self):
        """Test successful CSV import."""
        # Create temporary CSV
        csv_content = "name,description\nNode1,First node\nNode2,Second node\n"
        csv_bytes = csv_content.encode('utf-8')

        # Upload file
        response = self.client.post(
            "/api/v1/import/csv",
            files={"file": ("test.csv", BytesIO(csv_bytes), "text/csv")},
            data={
                "node_type": "Node",
                "dry_run": "false"
            }
        )

        assert response.status_code == 200
        data = response.json()

        # Verify results
        assert data["nodes_created"] == 2
        assert data["nodes_failed"] == 0
        assert len(data["errors"]) == 0
        assert data["elapsed_time"] > 0

    def test_import_csv_dry_run(self):
        """Test CSV import with dry-run mode."""
        csv_content = "name,description\nTest,Test description\n"
        csv_bytes = csv_content.encode('utf-8')

        response = self.client.post(
            "/api/v1/import/csv",
            files={"file": ("test.csv", BytesIO(csv_bytes), "text/csv")},
            data={
                "dry_run": "true"
            }
        )

        assert response.status_code == 200
        data = response.json()

        # Dry run should validate but not create
        assert data["nodes_created"] == 0
        assert data["nodes_failed"] == 0
        assert len(data["errors"]) == 0

    def test_import_csv_with_errors(self):
        """Test CSV import with validation errors."""
        # CSV with empty required field
        csv_content = "name,description\n,Missing name\nValid,Valid node\n"
        csv_bytes = csv_content.encode('utf-8')

        response = self.client.post(
            "/api/v1/import/csv",
            files={"file": ("test.csv", BytesIO(csv_bytes), "text/csv")},
            data={
                "continue_on_error": "true"
            }
        )

        assert response.status_code == 200
        data = response.json()

        # Should create valid node, skip invalid
        assert data["nodes_created"] >= 1
        # May have errors depending on validation strictness
        assert isinstance(data["errors"], list)

    def test_import_csv_invalid_file_type(self):
        """Test rejection of invalid file types."""
        content = b"Invalid content"

        response = self.client.post(
            "/api/v1/import/csv",
            files={"file": ("test.txt", BytesIO(content), "text/plain")},
            data={}
        )

        # .txt is actually supported as CSV, so test with unsupported extension
        response = self.client.post(
            "/api/v1/import/csv",
            files={"file": ("test.pdf", BytesIO(content), "application/pdf")},
            data={}
        )

        assert response.status_code == 400
        assert "Unsupported file type" in response.json()["detail"]

    def test_import_csv_with_batch_size(self):
        """Test CSV import with custom batch size."""
        # Create CSV with multiple rows
        csv_content = "name,description\n"
        for i in range(50):
            csv_content += f"Node{i},Description {i}\n"
        csv_bytes = csv_content.encode('utf-8')

        response = self.client.post(
            "/api/v1/import/csv",
            files={"file": ("test.csv", BytesIO(csv_bytes), "text/csv")},
            data={
                "batch_size": "10"  # Small batches
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert data["nodes_created"] == 50
        assert data["nodes_failed"] == 0

    def test_import_csv_with_mapping_template(self):
        """Test CSV import with pre-built mapping template."""
        csv_content = "name,description,type,jurisdiction\nEPA,Environmental Agency,regulatory,Federal\n"
        csv_bytes = csv_content.encode('utf-8')

        response = self.client.post(
            "/api/v1/import/csv",
            files={"file": ("institutions.csv", BytesIO(csv_bytes), "text/csv")},
            data={
                "mapping_template": "csv_institution"
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert data["nodes_created"] == 1
        assert data["nodes_failed"] == 0

    def test_import_excel_file(self):
        """Test Excel file import."""
        # Create temporary Excel file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xlsx', delete=False) as f:
            excel_path = f.name

        try:
            # Write Excel file using pandas
            import pandas as pd
            df = pd.DataFrame({
                'name': ['Node1', 'Node2'],
                'description': ['First', 'Second']
            })
            df.to_excel(excel_path, index=False)

            # Read file as bytes
            with open(excel_path, 'rb') as f:
                excel_bytes = f.read()

            response = self.client.post(
                "/api/v1/import/csv",
                files={"file": ("test.xlsx", BytesIO(excel_bytes), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
                data={}
            )

            assert response.status_code == 200
            data = response.json()

            assert data["nodes_created"] == 2
            assert data["nodes_failed"] == 0

        finally:
            Path(excel_path).unlink(missing_ok=True)


class TestOECDImportEndpoint:
    """Test POST /import/oecd endpoint (placeholder)."""

    def setup_method(self):
        """Set up test client."""
        self.app = create_app()
        self.client = TestClient(self.app)

    def test_oecd_import_not_implemented(self):
        """Test that OECD import returns 501 Not Implemented."""
        response = self.client.post(
            "/api/v1/import/oecd",
            data={
                "dataset_id": "GREEN_GROWTH",
                "filters": '{"LOCATION": "USA"}'
            }
        )

        assert response.status_code == 501
        assert "not yet implemented" in response.json()["detail"].lower()


class TestWorldBankImportEndpoint:
    """Test POST /import/worldbank endpoint (placeholder)."""

    def setup_method(self):
        """Set up test client."""
        self.app = create_app()
        self.client = TestClient(self.app)

    def test_worldbank_import_not_implemented(self):
        """Test that World Bank import returns 501 Not Implemented."""
        response = self.client.post(
            "/api/v1/import/worldbank",
            data={
                "country": "USA",
                "indicator": "NY.GDP.MKTP.CD"
            }
        )

        assert response.status_code == 501
        assert "not yet implemented" in response.json()["detail"].lower()
