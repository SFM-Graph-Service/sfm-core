"""
Tests for OECD adapter.

Covers:
- API request handling
- SDMX-JSON parsing
- Rate limiting
- Error handling
- Caching
"""

import pytest
from unittest.mock import Mock, patch
import json

from data.importers import OECDAdapter, ImportConfig


class TestOECDAdapterDetection:
    """Test format detection."""

    def test_detect_oecd_string(self):
        """Test detection of oecd: prefix."""
        adapter = OECDAdapter(dataset_id="GREEN_GROWTH")
        assert adapter.detect_format("oecd:GREEN_GROWTH") is True

    def test_detect_oecd_dict(self):
        """Test detection of dict with dataset_id."""
        adapter = OECDAdapter(dataset_id="GREEN_GROWTH")
        assert adapter.detect_format({"dataset_id": "QNA"}) is True
        assert adapter.detect_format({"oecd_dataset": "GREEN_GROWTH"}) is True

    def test_reject_non_oecd(self):
        """Test rejection of non-OECD formats."""
        adapter = OECDAdapter(dataset_id="GREEN_GROWTH")
        assert adapter.detect_format("worldbank:USA:GDP") is False
        assert adapter.detect_format("data.csv") is False
        assert adapter.detect_format({"other": "data"}) is False


class TestOECDAdapterExtraction:
    """Test data extraction."""

    @patch('data.importers.oecd_adapter.requests.get')
    def test_extract_nodes_basic(self, mock_get):
        """Test extracting nodes from OECD API response."""
        # Mock SDMX-JSON response
        mock_response = Mock()
        mock_response.json.return_value = {
            "structure": {
                "dimensions": {
                    "observation": [
                        {
                            "id": "LOCATION",
                            "values": [{"id": "USA"}]
                        },
                        {
                            "id": "TIME_PERIOD",
                            "values": [{"id": "2020"}]
                        }
                    ]
                }
            },
            "dataSets": [
                {
                    "observations": {
                        "0:0": [42.5]
                    }
                }
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        # Create adapter and extract
        adapter = OECDAdapter(dataset_id="GREEN_GROWTH")
        nodes = list(adapter.extract_nodes("oecd:GREEN_GROWTH"))

        # Verify results
        assert len(nodes) == 1
        assert nodes[0]["_node_type"] == "SocialFabricIndicator"
        assert nodes[0]["current_value"] == 42.5
        assert "meta" in nodes[0]
        assert nodes[0]["meta"]["country"] == "USA"

    @patch('data.importers.oecd_adapter.requests.get')
    def test_extract_with_filters(self, mock_get):
        """Test extraction with dimension filters."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "structure": {"dimensions": {"observation": []}},
            "dataSets": [{"observations": {}}]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        # Create adapter with filters
        adapter = OECDAdapter(
            dataset_id="GREEN_GROWTH",
            filters={"LOCATION": "USA", "MEASURE": "CO2"}
        )

        list(adapter.extract_nodes("oecd:GREEN_GROWTH"))

        # Verify URL includes filters
        call_args = mock_get.call_args
        assert "USA.CO2" in call_args[0][0]  # Filter string in URL

    @patch('data.importers.oecd_adapter.requests.get')
    def test_rate_limiting(self, mock_get):
        """Test rate limiting between requests."""
        import time

        mock_response = Mock()
        mock_response.json.return_value = {
            "structure": {"dimensions": {"observation": []}},
            "dataSets": [{"observations": {}}]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        # Create adapter with short delay
        adapter = OECDAdapter(dataset_id="GREEN_GROWTH", rate_limit_delay=0.1)

        # Make two requests
        start = time.time()
        list(adapter.extract_nodes("oecd:GREEN_GROWTH"))
        adapter._cache.clear()  # Clear cache to force second request
        list(adapter.extract_nodes("oecd:GREEN_GROWTH"))
        elapsed = time.time() - start

        # Should have delay between requests
        assert elapsed >= 0.1


class TestOECDAdapterValidation:
    """Test validation."""

    def test_validate_missing_dataset(self):
        """Test validation fails for missing dataset_id."""
        adapter = OECDAdapter(dataset_id="")
        errors = adapter.validate_format("oecd:GREEN_GROWTH")

        assert len(errors) > 0
        assert "dataset_id" in errors[0].lower()

    @patch('data.importers.oecd_adapter.requests.head')
    def test_validate_api_connectivity(self, mock_head):
        """Test validation checks API connectivity when enabled."""
        mock_head.return_value = Mock(status_code=404)

        config = ImportConfig(validate_references=True)
        adapter = OECDAdapter(dataset_id="INVALID_DATASET", config=config)

        errors = adapter.validate_format("oecd:INVALID_DATASET")

        # Should report dataset not found
        assert any("not found" in err.lower() for err in errors)


class TestOECDAdapterCaching:
    """Test response caching."""

    @patch('data.importers.oecd_adapter.requests.get')
    def test_cache_hit(self, mock_get):
        """Test cached responses avoid API calls."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "structure": {"dimensions": {"observation": []}},
            "dataSets": [{"observations": {}}]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        adapter = OECDAdapter(dataset_id="GREEN_GROWTH")

        # First call hits API
        list(adapter.extract_nodes("oecd:GREEN_GROWTH"))
        assert mock_get.call_count == 1

        # Second call uses cache
        list(adapter.extract_nodes("oecd:GREEN_GROWTH"))
        assert mock_get.call_count == 1  # No additional call


class TestOECDAdapterSizeEstimation:
    """Test size estimation."""

    @patch('data.importers.oecd_adapter.requests.get')
    def test_estimate_size(self, mock_get):
        """Test estimating observation count."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "structure": {"dimensions": {"observation": []}},
            "dataSets": [
                {
                    "observations": {
                        "0:0": [1.0],
                        "0:1": [2.0],
                        "1:0": [3.0]
                    }
                }
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        adapter = OECDAdapter(dataset_id="GREEN_GROWTH")
        size = adapter.estimate_size("oecd:GREEN_GROWTH")

        assert size == 3
