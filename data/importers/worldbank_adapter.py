"""
World Bank API import adapter.

Supports importing development indicators:
- GDP, population, emissions
- Country-specific time series
- Custom indicator queries

API Documentation: https://datahelpdesk.worldbank.org/knowledgebase/articles/889392-about-the-indicators-api-documentation
"""

import time
from typing import Any, Dict, Iterator, Optional, Union, List
from pathlib import Path
import requests
from datetime import datetime

from .base_adapter import BaseImportAdapter, ImportConfig
from .mapping_config import MappingConfig
from .validators import ValidationError


class WorldBankAdapter(BaseImportAdapter):
    """
    Import adapter for World Bank API.

    Fetches development indicators for specific countries and time ranges.
    Maps data to SocialFabricIndicator or SocialCost nodes depending on
    indicator type.
    """

    BASE_URL = "https://api.worldbank.org/v2"

    # Common indicator codes
    INDICATORS = {
        "GDP": "NY.GDP.MKTP.CD",  # GDP (current US$)
        "GDP_GROWTH": "NY.GDP.MKTP.KD.ZG",  # GDP growth (annual %)
        "POPULATION": "SP.POP.TOTL",  # Population, total
        "CO2_EMISSIONS": "EN.ATM.CO2E.KT",  # CO2 emissions (kt)
        "POVERTY": "SI.POV.DDAY",  # Poverty headcount ratio
        "GINI": "SI.POV.GINI",  # GINI index
        "UNEMPLOYMENT": "SL.UEM.TOTL.ZS",  # Unemployment, total (% of labor force)
    }

    def __init__(
        self,
        country: str,
        indicator: str,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
        mapping: Optional[MappingConfig] = None,
        config: Optional[ImportConfig] = None,
        rate_limit_delay: float = 0.3
    ):
        """
        Initialize World Bank adapter.

        Args:
            country: Country code (e.g., "USA", "GBR", "CHN") or "all"
            indicator: Indicator code (e.g., "NY.GDP.MKTP.CD") or name from INDICATORS
            start_year: Start year for time range (optional)
            end_year: End year for time range (optional)
            mapping: Field mapping configuration (uses default if None)
            config: Import configuration
            rate_limit_delay: Seconds between API calls (default: 0.3)
        """
        super().__init__(config)
        self.country = country.upper()

        # Resolve indicator name to code if needed
        self.indicator = self.INDICATORS.get(indicator.upper(), indicator)

        self.start_year = start_year
        self.end_year = end_year
        self.mapping = mapping or self._default_mapping()
        self.rate_limit_delay = rate_limit_delay
        self._last_request_time = 0.0
        self._cache: Dict[str, Any] = {}

    def _default_mapping(self) -> MappingConfig:
        """Create default mapping for World Bank indicators."""
        from .mapping_config import MappingTemplates
        return MappingTemplates.worldbank_indicator()

    def detect_format(self, source: Union[str, Path, Dict[str, Any]]) -> bool:
        """
        Detect if source is a World Bank API reference.

        Args:
            source: String starting with "worldbank:" or dict with country/indicator

        Returns:
            True if source is World Bank format
        """
        if isinstance(source, str):
            return source.startswith("worldbank:")
        if isinstance(source, dict):
            return "country" in source and "indicator" in source
        return False

    def extract_nodes(self, source: Union[str, Path, Dict[str, Any]]) -> Iterator[Dict[str, Any]]:
        """
        Extract nodes from World Bank API.

        Args:
            source: World Bank API reference (e.g., "worldbank:USA:GDP")

        Yields:
            Dictionaries with SFM node attributes (after mapping)
        """
        # Parse source if string format
        if isinstance(source, str) and source.startswith("worldbank:"):
            parts = source[10:].split(":")
            country = parts[0] if len(parts) > 0 else self.country
            indicator = parts[1] if len(parts) > 1 else self.indicator
        else:
            country = self.country
            indicator = self.indicator

        # Fetch data from API with pagination
        try:
            all_data = self._fetch_all_pages(country, indicator)

            # Map to SFM nodes
            for record in all_data:
                try:
                    # Add metadata
                    record["data_source"] = "World Bank"
                    record["fetched_at"] = datetime.now().isoformat()

                    mapped = self.mapping.transform_row(record)
                    yield mapped
                except (KeyError, ValueError) as e:
                    if not self.config.continue_on_error:
                        raise ValueError(f"Failed to map record: {e}") from e
                    continue

        except requests.RequestException as e:
            raise ValidationError(f"World Bank API request failed: {e}") from e

    def _fetch_all_pages(
        self,
        country: str,
        indicator: str,
        per_page: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        Fetch all pages of data from World Bank API.

        World Bank API uses pagination with page numbers.

        Args:
            country: Country code
            indicator: Indicator code
            per_page: Records per page (max 32500, default 1000)

        Returns:
            List of all data records
        """
        all_data = []
        page = 1

        while True:
            data = self._fetch_page(country, indicator, page, per_page)

            # World Bank API returns [metadata, data]
            if not isinstance(data, list) or len(data) < 2:
                break

            metadata, records = data[0], data[1]

            if not records:
                break

            all_data.extend(records)

            # Check if more pages
            total_pages = metadata.get("pages", 1)
            if page >= total_pages:
                break

            page += 1

        return all_data

    def _fetch_page(
        self,
        country: str,
        indicator: str,
        page: int = 1,
        per_page: int = 1000,
        max_retries: int = 3
    ) -> Any:
        """
        Fetch single page from World Bank API.

        Args:
            country: Country code
            indicator: Indicator code
            page: Page number (1-indexed)
            per_page: Records per page
            max_retries: Maximum retry attempts

        Returns:
            Parsed JSON response
        """
        # Build cache key
        cache_key = f"{country}:{indicator}:{page}:{per_page}"

        # Check cache
        if cache_key in self._cache:
            return self._cache[cache_key]

        # Rate limiting
        elapsed = time.time() - self._last_request_time
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)

        # Build URL
        url = f"{self.BASE_URL}/country/{country}/indicator/{indicator}"

        params = {
            "format": "json",
            "page": page,
            "per_page": per_page
        }

        # Add date range if specified
        if self.start_year and self.end_year:
            params["date"] = f"{self.start_year}:{self.end_year}"
        elif self.start_year:
            params["date"] = f"{self.start_year}:{datetime.now().year}"

        # Retry logic
        for attempt in range(max_retries):
            try:
                response = requests.get(url, params=params, timeout=30)
                response.raise_for_status()

                self._last_request_time = time.time()

                data = response.json()
                self._cache[cache_key] = data
                return data

            except requests.RequestException as e:
                if attempt == max_retries - 1:
                    raise
                time.sleep(2 ** attempt)  # Exponential backoff

        raise ValidationError(f"Failed to fetch World Bank data after {max_retries} retries")

    def extract_relationships(self, source: Union[str, Path, Dict[str, Any]]) -> Iterator[Dict[str, Any]]:
        """
        Extract relationships from World Bank data.

        Not supported - World Bank data is primarily time series indicators.

        Args:
            source: Data source

        Yields:
            Empty (relationships not supported)
        """
        return iter([])

    def validate_format(self, source: Union[str, Path, Dict[str, Any]]) -> List[str]:
        """
        Validate World Bank API parameters.

        Args:
            source: World Bank API reference

        Returns:
            List of validation errors
        """
        errors = []

        if not self.country:
            errors.append("country is required for World Bank adapter")

        if not self.indicator:
            errors.append("indicator is required for World Bank adapter")

        # Validate country code format (3 letters)
        if self.country != "ALL" and len(self.country) not in [2, 3]:
            errors.append(f"Invalid country code: '{self.country}' (expected 2-3 letters)")

        # Validate year range
        if self.start_year and self.end_year:
            if self.start_year > self.end_year:
                errors.append(f"start_year ({self.start_year}) must be <= end_year ({self.end_year})")

        # Test API connectivity (optional - can be expensive)
        if self.config.validate_references:
            try:
                # Simple request with limit=1 to check if endpoint works
                url = f"{self.BASE_URL}/country/{self.country}/indicator/{self.indicator}"
                response = requests.get(
                    url,
                    params={"format": "json", "per_page": 1},
                    timeout=5
                )

                if response.status_code == 404:
                    errors.append(
                        f"World Bank country '{self.country}' or indicator '{self.indicator}' not found"
                    )
                elif response.status_code != 200:
                    errors.append(f"World Bank API returned status {response.status_code}")

            except requests.RequestException:
                # Don't fail validation on network errors
                pass

        return errors

    def estimate_size(self, source: Union[str, Path, Dict[str, Any]]) -> int:
        """
        Estimate number of data points.

        World Bank API provides total count in metadata.

        Args:
            source: Data source

        Returns:
            Estimated record count
        """
        try:
            # Fetch first page to get metadata
            data = self._fetch_page(self.country, self.indicator, page=1, per_page=1)

            if isinstance(data, list) and len(data) >= 1:
                metadata = data[0]
                return metadata.get("total", 0)

            return 0
        except Exception:
            return 0  # Unknown size
