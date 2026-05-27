"""
Tests for World Bank adapter.

Covers:
- API request handling
- Pagination
- Rate limiting
- Error handling
- Indicator name resolution
"""

import pytest
from unittest.mock import Mock, patch
import json

from data.importers import WorldBankAdapter, ImportConfig


class TestWorldBankAdapterDetection:
    """Test format detection."""

    def test_detect_worldbank_string(self):
        """Test detection of worldbank: prefix."""
        adapter = WorldBankAdapter(country="USA", indicator="GDP")
        assert adapter.detect_format("worldbank:USA:GDP") is True

    def test_detect_worldbank_dict(self):
        """Test detection of dict with country and indicator."""
        adapter = WorldBankAdapter(country="USA", indicator="GDP")
        assert adapter.detect_format({"country": "USA", "indicator": "GDP"}) is True

    def test_reject_non_worldbank(self):
        """Test rejection of non-World Bank formats."""
        adapter = WorldBankAdapter(country="USA", indicator="GDP")
        assert adapter.detect_format("oecd:GREEN_GROWTH") is False
        assert adapter.detect_format("data.csv") is False


class TestWorldBankAdapterExtraction:
    """Test data extraction."""

    @patch('data.importers.worldbank_adapter.requests.get')
    def test_extract_nodes_basic(self, mock_get):
        """Test extracting nodes from World Bank API response."""
        # Mock World Bank API response
        mock_response = Mock()
        mock_response.json.return_value = [
            {
                "page": 1,
                "pages": 1,
                "per_page": 1000,
                "total": 2
            },
            [
                {
                    "indicator": {"id": "NY.GDP.MKTP.CD", "value": "GDP (current US$)"},
                    "country": {"id": "USA", "value": "United States"},
                    "value": 21000000000000,
                    "date": "2020"
                },
                {
                    "indicator": {"id": "NY.GDP.MKTP.CD", "value": "GDP (current US$)"},
                    "country": {"id": "USA", "value": "United States"},
                    "value": 20500000000000,
                    "date": "2019"
                }
            ]
        ]
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        # Create adapter and extract
        adapter = WorldBankAdapter(country="USA", indicator="GDP")
        nodes = list(adapter.extract_nodes("worldbank:USA:GDP"))

        # Verify results
        assert len(nodes) == 2
        assert nodes[0]["_node_type"] == "SocialFabricIndicator"
        assert nodes[0]["label"] == "GDP (current US$)"
        assert nodes[0]["current_value"] == 21000000000000
        assert nodes[0]["meta"]["country"] == "USA"
        assert nodes[0]["meta"]["year"] == 2020

    @patch('data.importers.worldbank_adapter.requests.get')
    def test_extract_with_year_range(self, mock_get):
        """Test extraction with year range filter."""
        mock_response = Mock()
        mock_response.json.return_value = [
            {"page": 1, "pages": 1, "total": 0},
            []
        ]
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        # Create adapter with year range
        adapter = WorldBankAdapter(
            country="USA",
            indicator="GDP",
            start_year=2015,
            end_year=2020
        )

        list(adapter.extract_nodes("worldbank:USA:GDP"))

        # Verify date parameter in request
        call_args = mock_get.call_args
        assert "date" in call_args[1]["params"]
        assert call_args[1]["params"]["date"] == "2015:2020"

    @patch('data.importers.worldbank_adapter.requests.get')
    def test_pagination(self, mock_get):
        """Test automatic pagination handling."""
        # Mock multi-page response
        page1_response = Mock()
        page1_response.json.return_value = [
            {"page": 1, "pages": 2, "total": 100},
            [{"indicator": {"value": "Test"}, "country": {"id": "USA"}, "value": 1.0, "date": "2020"}]
        ]
        page1_response.raise_for_status = Mock()

        page2_response = Mock()
        page2_response.json.return_value = [
            {"page": 2, "pages": 2, "total": 100},
            [{"indicator": {"value": "Test"}, "country": {"id": "USA"}, "value": 2.0, "date": "2019"}]
        ]
        page2_response.raise_for_status = Mock()

        mock_get.side_effect = [page1_response, page2_response]

        # Create adapter
        adapter = WorldBankAdapter(country="USA", indicator="GDP")
        nodes = list(adapter.extract_nodes("worldbank:USA:GDP"))

        # Should fetch both pages
        assert len(nodes) == 2
        assert mock_get.call_count == 2

    @patch('data.importers.worldbank_adapter.requests.get')
    def test_indicator_name_resolution(self, mock_get):
        """Test resolving indicator names to codes."""
        mock_response = Mock()
        mock_response.json.return_value = [
            {"page": 1, "pages": 1, "total": 0},
            []
        ]
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        # Use friendly name instead of code
        adapter = WorldBankAdapter(country="USA", indicator="GDP")

        # Verify adapter resolves name to code during initialization
        assert adapter.indicator == "NY.GDP.MKTP.CD"

        # Call without source argument to use adapter's own indicator
        list(adapter.extract_nodes({}))

        # Should use resolved code in URL
        call_args = mock_get.call_args
        assert "NY.GDP.MKTP.CD" in call_args[0][0]

    @patch('data.importers.worldbank_adapter.requests.get')
    def test_handle_null_values(self, mock_get):
        """Test handling null values in data."""
        mock_response = Mock()
        mock_response.json.return_value = [
            {"page": 1, "pages": 1, "total": 1},
            [
                {
                    "indicator": {"value": "Test Indicator"},
                    "country": {"id": "USA"},
                    "value": None,  # Null value
                    "date": "2020"
                }
            ]
        ]
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        adapter = WorldBankAdapter(country="USA", indicator="GDP")
        nodes = list(adapter.extract_nodes("worldbank:USA:GDP"))

        # Should handle null gracefully
        assert len(nodes) == 1
        assert nodes[0]["current_value"] is None


class TestWorldBankAdapterValidation:
    """Test validation."""

    def test_validate_missing_country(self):
        """Test validation fails for missing country."""
        adapter = WorldBankAdapter(country="", indicator="GDP")
        errors = adapter.validate_format("worldbank::GDP")

        assert len(errors) > 0
        assert "country" in errors[0].lower()

    def test_validate_missing_indicator(self):
        """Test validation fails for missing indicator."""
        adapter = WorldBankAdapter(country="USA", indicator="")
        errors = adapter.validate_format("worldbank:USA:")

        assert len(errors) > 0
        assert "indicator" in errors[0].lower()

    def test_validate_invalid_year_range(self):
        """Test validation fails for invalid year range."""
        adapter = WorldBankAdapter(
            country="USA",
            indicator="GDP",
            start_year=2020,
            end_year=2010  # End before start
        )
        errors = adapter.validate_format("worldbank:USA:GDP")

        assert len(errors) > 0
        assert "start_year" in errors[0].lower() or "year" in errors[0].lower()


class TestWorldBankAdapterCaching:
    """Test response caching."""

    @patch('data.importers.worldbank_adapter.requests.get')
    def test_cache_hit(self, mock_get):
        """Test cached responses avoid API calls."""
        mock_response = Mock()
        mock_response.json.return_value = [
            {"page": 1, "pages": 1, "total": 0},
            []
        ]
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        adapter = WorldBankAdapter(country="USA", indicator="GDP")

        # First call hits API
        list(adapter.extract_nodes("worldbank:USA:GDP"))
        initial_calls = mock_get.call_count

        # Second call uses cache (same page)
        list(adapter.extract_nodes("worldbank:USA:GDP"))
        assert mock_get.call_count == initial_calls  # No additional call


class TestWorldBankAdapterSizeEstimation:
    """Test size estimation."""

    @patch('data.importers.worldbank_adapter.requests.get')
    def test_estimate_size(self, mock_get):
        """Test estimating record count from metadata."""
        mock_response = Mock()
        mock_response.json.return_value = [
            {"page": 1, "pages": 5, "total": 42},
            []
        ]
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        adapter = WorldBankAdapter(country="USA", indicator="GDP")
        size = adapter.estimate_size("worldbank:USA:GDP")

        assert size == 42
