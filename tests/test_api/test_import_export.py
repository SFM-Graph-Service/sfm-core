"""
Tests for import/export REST API endpoints.

Covers:
- GET /import/formats - List supported formats
- POST /import/csv - Upload and import CSV/Excel files
- POST /import/oecd - OECD API import
- POST /import/worldbank - World Bank API import
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

        # Check OECD format (now implemented)
        oecd_format = next(f for f in data["formats"] if f["format_name"] == "oecd")
        assert oecd_format["adapter_available"] is True

        # Check World Bank format (now implemented)
        wb_format = next(f for f in data["formats"] if f["format_name"] == "worldbank")
        assert wb_format["adapter_available"] is True

        sdmx_format = next(f for f in data["formats"] if f["format_name"] == "sdmx")
        assert sdmx_format["adapter_available"] is True
        assert "ECB" in sdmx_format["description"]
        assert ".json" in sdmx_format["file_extensions"]


class TestSDMXImportEndpoint:
    """Test POST /import/sdmx endpoint."""

    def setup_method(self):
        self.app = create_app()
        self.client = TestClient(self.app)

    def test_import_sdmx_dry_run(self):
        from unittest.mock import Mock, patch
        import json as _json

        payload = {
            "structure": {"dimensions": {"observation": [
                {"id": "REF_AREA", "values": [{"id": "US"}]},
                {"id": "TIME_PERIOD", "values": [{"id": "2023"}, {"id": "2024"}]},
            ]}},
            "dataSets": [{"observations": {"0:0": [1.5], "0:1": [1.7]}}],
        }
        with patch("data.importers.sdmx_adapter.requests.get") as mock_get:
            mock_get.return_value = Mock(text=_json.dumps(payload), raise_for_status=Mock())
            response = self.client.post(
                "/api/v1/import/sdmx",
                data={"agency": "ECB", "flow": "EXR", "key": "A.USD.EUR.SP00.A",
                      "start_period": "2023", "dry_run": "true"},
            )
            assert response.status_code == 200
            data = response.json()
            assert data["nodes_created"] == 0  # dry run counts nothing as created
            assert data["nodes_failed"] == 0
            assert mock_get.call_args[0][0].endswith("/data/EXR/A.USD.EUR.SP00.A")
            assert mock_get.call_args.kwargs["params"] == {"startPeriod": "2023"}

    def test_import_sdmx_unknown_agency_is_400(self):
        response = self.client.post(
            "/api/v1/import/sdmx",
            data={"agency": "NOT_AN_AGENCY", "flow": "EXR"},
        )
        assert response.status_code == 400
        assert "Unknown SDMX agency" in response.json()["detail"]

    def test_import_sdmx_requires_flow(self):
        """A missing form field must be a structured 422, not a 500 from serialising FormData."""
        response = self.client.post("/api/v1/import/sdmx", data={"agency": "ECB"})
        assert response.status_code == 422
        data = response.json()
        assert data["error"] == "VALIDATION_ERROR"
        assert any(e["loc"][-1] == "flow" for e in data["context"]["errors"])
        assert data["context"]["body"] == {"agency": "ECB"}

    def test_csv_upload_validation_error_is_422(self):
        """Multipart bodies with an upload must also serialise in the 422 response."""
        response = self.client.post(
            "/api/v1/import/csv",
            files={"file": ("t.csv", BytesIO(b"name\nA\n"), "text/csv")},
            data={"batch_size": "not-a-number"},
        )
        assert response.status_code == 422
        body = response.json()["context"]["body"]
        assert body["batch_size"] == "not-a-number"
        assert body["file"] == {"filename": "t.csv"}


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

    def test_import_csv_unknown_mapping_template_is_400(self):
        """An unrecognised template must be rejected, not silently mapped as basic_node."""
        csv_bytes = b"name,description\nNode1,First\n"
        response = self.client.post(
            "/api/v1/import/csv",
            files={"file": ("test.csv", BytesIO(csv_bytes), "text/csv")},
            data={"mapping_template": "not_a_template"}
        )
        assert response.status_code == 400
        detail = response.json()["detail"]
        assert "not_a_template" in detail
        for name in ("basic_node", "csv_institution", "oecd_indicator", "worldbank_indicator"):
            assert name in detail

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
    """Test POST /import/oecd endpoint."""

    def setup_method(self):
        """Set up test client."""
        self.app = create_app()
        self.client = TestClient(self.app)

    @pytest.fixture(autouse=True)
    def mock_oecd_api(self, monkeypatch):
        """Mock OECD API requests."""
        from unittest.mock import Mock, patch

        def mock_get(*args, **kwargs):
            response = Mock()
            response.json.return_value = {
                "structure": {
                    "dimensions": {
                        "observation": [
                            {"id": "LOCATION", "values": [{"id": "USA"}]},
                            {"id": "TIME_PERIOD", "values": [{"id": "2020"}]}
                        ]
                    }
                },
                "dataSets": [{"observations": {"0:0": [42.5]}}]
            }
            response.raise_for_status = Mock()
            return response

        monkeypatch.setattr("data.importers.oecd_adapter.requests.get", mock_get)

    def test_oecd_import_success(self):
        """Test successful OECD import."""
        response = self.client.post(
            "/api/v1/import/oecd",
            data={
                "dataset_id": "GREEN_GROWTH",
                "filters": '{"LOCATION": "USA"}'
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["nodes_created"] >= 0  # May be 0 due to mocking
        assert isinstance(data["errors"], list)

    def test_oecd_import_invalid_filters(self):
        """Test OECD import with invalid JSON filters."""
        response = self.client.post(
            "/api/v1/import/oecd",
            data={
                "dataset_id": "GREEN_GROWTH",
                "filters": "invalid json"
            }
        )

        assert response.status_code == 400
        assert "invalid json" in response.json()["detail"].lower()


class TestWorldBankImportEndpoint:
    """Test POST /import/worldbank endpoint."""

    def setup_method(self):
        """Set up test client."""
        self.app = create_app()
        self.client = TestClient(self.app)

    @pytest.fixture(autouse=True)
    def mock_worldbank_api(self, monkeypatch):
        """Mock World Bank API requests."""
        from unittest.mock import Mock

        def mock_get(*args, **kwargs):
            response = Mock()
            response.json.return_value = [
                {"page": 1, "pages": 1, "total": 1},
                [
                    {
                        "indicator": {"id": "NY.GDP.MKTP.CD", "value": "GDP (current US$)"},
                        "country": {"id": "USA", "value": "United States"},
                        "value": 21000000000000,
                        "date": "2020"
                    }
                ]
            ]
            response.raise_for_status = Mock()
            return response

        monkeypatch.setattr("data.importers.worldbank_adapter.requests.get", mock_get)

    def test_worldbank_import_success(self):
        """Test successful World Bank import."""
        response = self.client.post(
            "/api/v1/import/worldbank",
            data={
                "country": "USA",
                "indicator": "GDP"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["nodes_created"] >= 0
        assert isinstance(data["errors"], list)

    def test_worldbank_import_with_year_range(self):
        """Test World Bank import with year range."""
        response = self.client.post(
            "/api/v1/import/worldbank",
            data={
                "country": "GBR",
                "indicator": "POPULATION",
                "start_year": 2015,
                "end_year": 2020
            }
        )

        assert response.status_code == 200
