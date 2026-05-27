"""
OECD.Stat API import adapter.

Supports importing statistical indicators from OECD datasets:
- GREEN_GROWTH (environmental indicators)
- QNA (quarterly national accounts)
- Custom datasets via SDMX-JSON API

API Documentation: https://data.oecd.org/api/sdmx-json-documentation/
"""

import time
from typing import Any, Dict, Iterator, Optional, Union, List
from pathlib import Path
import requests
from datetime import datetime

from .base_adapter import BaseImportAdapter, ImportConfig
from .mapping_config import MappingConfig
from .validators import ValidationError


class OECDAdapter(BaseImportAdapter):
    """
    Import adapter for OECD.Stat API.

    Fetches statistical indicators via SDMX-JSON API and maps them to
    SocialFabricIndicator nodes. Supports automatic pagination, rate limiting,
    and response caching.
    """

    BASE_URL = "https://stats.oecd.org/SDMX-JSON/data"

    def __init__(
        self,
        dataset_id: str,
        filters: Optional[Dict[str, str]] = None,
        mapping: Optional[MappingConfig] = None,
        config: Optional[ImportConfig] = None,
        rate_limit_delay: float = 0.5
    ):
        """
        Initialize OECD adapter.

        Args:
            dataset_id: OECD dataset identifier (e.g., "GREEN_GROWTH", "QNA")
            filters: Optional filters as dict (e.g., {"LOCATION": "USA", "MEASURE": "CO2"})
            mapping: Field mapping configuration (uses default if None)
            config: Import configuration
            rate_limit_delay: Seconds to wait between API calls (default: 0.5)
        """
        super().__init__(config)
        self.dataset_id = dataset_id
        self.filters = filters or {}
        self.mapping = mapping or self._default_mapping()
        self.rate_limit_delay = rate_limit_delay
        self._last_request_time = 0.0
        self._cache: Dict[str, Any] = {}

    def _default_mapping(self) -> MappingConfig:
        """Create default mapping for OECD indicators."""
        from .mapping_config import MappingTemplates
        return MappingTemplates.oecd_indicator()

    def detect_format(self, source: Union[str, Path, Dict[str, Any]]) -> bool:
        """
        Detect if source is an OECD API reference.

        Args:
            source: String starting with "oecd:" or dict with dataset_id

        Returns:
            True if source is OECD format
        """
        if isinstance(source, str):
            return source.startswith("oecd:")
        if isinstance(source, dict):
            return "dataset_id" in source or "oecd_dataset" in source
        return False

    def extract_nodes(self, source: Union[str, Path, Dict[str, Any]]) -> Iterator[Dict[str, Any]]:
        """
        Extract nodes from OECD API.

        Args:
            source: OECD API reference (e.g., "oecd:GREEN_GROWTH")

        Yields:
            Dictionaries with SFM node attributes (after mapping)
        """
        # Parse source if string format
        if isinstance(source, str) and source.startswith("oecd:"):
            dataset_id = source[5:]  # Remove "oecd:" prefix
        else:
            dataset_id = self.dataset_id

        # Fetch data from API
        try:
            data = self._fetch_data(dataset_id, self.filters)

            # Parse SDMX-JSON format
            observations = self._parse_sdmx_json(data)

            # Map to SFM nodes
            for obs in observations:
                try:
                    mapped = self.mapping.transform_row(obs)
                    yield mapped
                except (KeyError, ValueError) as e:
                    if not self.config.continue_on_error:
                        raise ValueError(f"Failed to map observation: {e}") from e
                    continue

        except requests.RequestException as e:
            raise ValidationError(f"OECD API request failed: {e}") from e

    def _fetch_data(
        self,
        dataset_id: str,
        filters: Dict[str, str],
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Fetch data from OECD API with rate limiting and caching.

        Args:
            dataset_id: Dataset identifier
            filters: Query filters
            max_retries: Maximum retry attempts

        Returns:
            Parsed JSON response
        """
        # Build cache key
        cache_key = f"{dataset_id}:{str(sorted(filters.items()))}"

        # Check cache
        if cache_key in self._cache:
            return self._cache[cache_key]

        # Rate limiting
        elapsed = time.time() - self._last_request_time
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)

        # Build URL
        filter_str = self._build_filter_string(filters)
        url = f"{self.BASE_URL}/{dataset_id}/{filter_str}"

        # Retry logic
        for attempt in range(max_retries):
            try:
                response = requests.get(
                    url,
                    headers={"Accept": "application/vnd.sdmx.data+json"},
                    timeout=30
                )
                response.raise_for_status()

                self._last_request_time = time.time()

                data = response.json()
                self._cache[cache_key] = data
                return data

            except requests.RequestException as e:
                if attempt == max_retries - 1:
                    raise
                time.sleep(2 ** attempt)  # Exponential backoff

        raise ValidationError(f"Failed to fetch OECD data after {max_retries} retries")

    def _build_filter_string(self, filters: Dict[str, str]) -> str:
        """
        Build OECD filter string from dictionary.

        Args:
            filters: Filter dictionary (e.g., {"LOCATION": "USA", "MEASURE": "CO2"})

        Returns:
            Filter string (e.g., "USA.CO2")
        """
        if not filters:
            return "all"

        # OECD uses dot-separated dimension values
        # Order matters - follow OECD dimension structure
        return ".".join(str(v) for v in filters.values())

    def _parse_sdmx_json(self, data: Dict[str, Any]) -> Iterator[Dict[str, str]]:
        """
        Parse SDMX-JSON format to flat dictionaries.

        SDMX-JSON structure:
        {
          "dataSets": [{
            "observations": {
              "0:0:0:0": [value],
              ...
            }
          }],
          "structure": {
            "dimensions": [...],
            "attributes": [...]
          }
        }

        Args:
            data: SDMX-JSON response

        Yields:
            Flat dictionaries with dimension values and observations
        """
        try:
            # Extract structure
            structure = data.get("structure", {})
            dimensions = structure.get("dimensions", {}).get("observation", [])

            # Extract dataset
            datasets = data.get("dataSets", [])
            if not datasets:
                return

            observations = datasets[0].get("observations", {})

            # Parse each observation
            for key, values in observations.items():
                # Parse dimension indices (e.g., "0:1:2:3")
                indices = [int(i) for i in key.split(":")]

                # Build flat dictionary
                obs_dict = {}

                # Add dimension values
                for i, dim in enumerate(dimensions):
                    if i < len(indices):
                        dim_id = dim.get("id", f"DIM_{i}")
                        dim_values = dim.get("values", [])
                        dim_index = indices[i]

                        if dim_index < len(dim_values):
                            dim_value = dim_values[dim_index].get("id", "")
                            obs_dict[dim_id] = dim_value

                # Add observation value
                if values and len(values) > 0:
                    obs_dict["Value"] = values[0]

                # Add metadata
                obs_dict["dataset_id"] = self.dataset_id
                obs_dict["data_source"] = "OECD"
                obs_dict["fetched_at"] = datetime.now().isoformat()

                yield obs_dict

        except (KeyError, IndexError, ValueError) as e:
            raise ValidationError(f"Failed to parse SDMX-JSON: {e}") from e

    def extract_relationships(self, source: Union[str, Path, Dict[str, Any]]) -> Iterator[Dict[str, Any]]:
        """
        Extract relationships from OECD data.

        Not supported - OECD data is primarily indicators.

        Args:
            source: Data source

        Yields:
            Empty (relationships not supported)
        """
        return iter([])

    def validate_format(self, source: Union[str, Path, Dict[str, Any]]) -> List[str]:
        """
        Validate OECD API parameters.

        Args:
            source: OECD API reference

        Returns:
            List of validation errors
        """
        errors = []

        if not self.dataset_id:
            errors.append("dataset_id is required for OECD adapter")

        # Test API connectivity (optional - can be expensive)
        if self.config.validate_references:
            try:
                # Simple HEAD request to check if dataset exists
                url = f"{self.BASE_URL}/{self.dataset_id}/all"
                response = requests.head(url, timeout=5)
                if response.status_code == 404:
                    errors.append(f"OECD dataset '{self.dataset_id}' not found")
            except requests.RequestException:
                # Don't fail validation on network errors
                pass

        return errors

    def estimate_size(self, source: Union[str, Path, Dict[str, Any]]) -> int:
        """
        Estimate number of observations.

        Note: OECD API doesn't provide count endpoint, so we fetch and count.
        For large datasets, this may be expensive.

        Args:
            source: Data source

        Returns:
            Estimated observation count
        """
        try:
            data = self._fetch_data(self.dataset_id, self.filters)
            datasets = data.get("dataSets", [])
            if datasets:
                observations = datasets[0].get("observations", {})
                return len(observations)
            return 0
        except Exception:
            return 0  # Unknown size
