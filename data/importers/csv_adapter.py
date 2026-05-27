"""
CSV and Excel import adapter.

Supports:
- CSV files with automatic delimiter detection
- Excel files (.xlsx, .xls)
- Streaming for large files (>10K rows)
- Field mapping with type coercion
- Enum translation
"""

import csv
from pathlib import Path
from typing import Any, Dict, Iterator, Optional, Union
import pandas as pd

from .base_adapter import BaseImportAdapter, ImportConfig
from .mapping_config import MappingConfig
from .validators import validate_csv_headers


class CSVImportAdapter(BaseImportAdapter):
    """
    Import adapter for CSV and Excel files.

    Uses streaming architecture to handle large files without loading
    entire dataset into memory. Supports field mapping, type coercion,
    and enum translation.
    """

    def __init__(self, mapping: MappingConfig, config: Optional[ImportConfig] = None):
        """
        Initialize CSV adapter with field mapping.

        Args:
            mapping: Field mapping configuration
            config: Import configuration
        """
        super().__init__(config)
        self.mapping = mapping

    def detect_format(self, source: Union[str, Path, Dict[str, Any]]) -> bool:
        """
        Detect if source is a CSV or Excel file.

        Args:
            source: File path to check

        Returns:
            True if file is CSV or Excel format
        """
        if isinstance(source, dict):
            return False

        path = Path(source) if isinstance(source, str) else source
        if not path.exists():
            return False

        # Check file extension
        ext = path.suffix.lower()
        return ext in ['.csv', '.tsv', '.txt', '.xlsx', '.xls']

    def extract_nodes(self, source: Union[str, Path, Dict[str, Any]]) -> Iterator[Dict[str, Any]]:
        """
        Extract nodes from CSV/Excel file.

        Uses streaming for CSV files and chunked reading for Excel.

        Args:
            source: Path to CSV or Excel file

        Yields:
            Dictionaries with SFM node attributes (after mapping)
        """
        path = Path(source) if isinstance(source, str) else source

        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        # Route to appropriate handler
        ext = path.suffix.lower()
        if ext in ['.csv', '.tsv', '.txt']:
            yield from self._extract_from_csv(path)
        elif ext in ['.xlsx', '.xls']:
            yield from self._extract_from_excel(path)
        else:
            raise ValueError(f"Unsupported file type: {ext}")

    def _extract_from_csv(self, path: Path) -> Iterator[Dict[str, Any]]:
        """
        Stream nodes from CSV file.

        Args:
            path: Path to CSV file

        Yields:
            Mapped node dictionaries
        """
        # Auto-detect delimiter
        delimiter = self._detect_delimiter(path)

        with open(path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=delimiter)

            # Validate headers
            if reader.fieldnames:
                required_fields = [
                    m.source_field for m in self.mapping.mappings if m.required
                ]
                errors = validate_csv_headers(list(reader.fieldnames), required_fields)
                if errors:
                    raise ValueError(f"CSV validation failed: {'; '.join(errors)}")

            # Stream rows
            for row_num, row in enumerate(reader, start=1):
                try:
                    mapped = self.mapping.transform_row(row)
                    yield mapped
                except (KeyError, ValueError) as e:
                    if not self.config.continue_on_error:
                        raise ValueError(f"Row {row_num}: {e}") from e
                    # Skip invalid rows in continue-on-error mode
                    continue

    def _extract_from_excel(self, path: Path) -> Iterator[Dict[str, Any]]:
        """
        Stream nodes from Excel file using chunked reading.

        Args:
            path: Path to Excel file

        Yields:
            Mapped node dictionaries
        """
        # Read in chunks to avoid loading entire file
        chunk_size = self.config.batch_size

        for chunk_df in pd.read_excel(path, chunksize=chunk_size):
            for row_num, row in chunk_df.iterrows():
                try:
                    # Convert pandas Series to dictionary
                    row_dict = row.to_dict()

                    # Apply mapping
                    mapped = self.mapping.transform_row(row_dict)
                    yield mapped
                except (KeyError, ValueError) as e:
                    if not self.config.continue_on_error:
                        raise ValueError(f"Row {row_num}: {e}") from e
                    # Skip invalid rows
                    continue

    def extract_relationships(self, source: Union[str, Path, Dict[str, Any]]) -> Iterator[Dict[str, Any]]:
        """
        Extract relationships from CSV/Excel file.

        Not supported for basic CSV adapter. Return empty iterator.

        Args:
            source: Path to file

        Yields:
            Empty (relationships not supported)
        """
        # CSV files typically don't encode relationships
        # This would require additional columns like:
        # source_node_id, target_node_id, relationship_type, weight
        # For now, return empty iterator
        return iter([])

    def _detect_delimiter(self, path: Path) -> str:
        """
        Auto-detect CSV delimiter.

        Args:
            path: Path to CSV file

        Returns:
            Detected delimiter (comma, tab, semicolon, pipe)
        """
        # Read first 1024 bytes to detect delimiter
        with open(path, 'r', encoding='utf-8') as f:
            sample = f.read(1024)

        # Use csv.Sniffer to detect
        try:
            sniffer = csv.Sniffer()
            dialect = sniffer.sniff(sample)
            return dialect.delimiter
        except csv.Error:
            # Fall back to comma
            return ','

    def validate_format(self, source: Union[str, Path, Dict[str, Any]]) -> list[str]:
        """
        Validate CSV/Excel format.

        Args:
            source: Path to file

        Returns:
            List of validation errors
        """
        errors = []
        path = Path(source) if isinstance(source, str) else source

        # Check file exists
        if not path.exists():
            errors.append(f"File not found: {path}")
            return errors

        # Check file extension
        ext = path.suffix.lower()
        if ext not in ['.csv', '.tsv', '.txt', '.xlsx', '.xls']:
            errors.append(f"Unsupported file type: {ext}")
            return errors

        # Validate headers (CSV only, quick check)
        if ext in ['.csv', '.tsv', '.txt']:
            delimiter = self._detect_delimiter(path)
            with open(path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter=delimiter)
                if reader.fieldnames:
                    required_fields = [
                        m.source_field for m in self.mapping.mappings if m.required
                    ]
                    header_errors = validate_csv_headers(list(reader.fieldnames), required_fields)
                    errors.extend(header_errors)

        return errors

    def estimate_size(self, source: Union[str, Path, Dict[str, Any]]) -> Optional[int]:
        """
        Estimate number of rows in file.

        Args:
            source: Path to file

        Returns:
            Estimated row count
        """
        path = Path(source) if isinstance(source, str) else source

        if not path.exists():
            return None

        ext = path.suffix.lower()

        if ext in ['.csv', '.tsv', '.txt']:
            # Count lines (subtract 1 for header)
            with open(path, 'r', encoding='utf-8') as f:
                return sum(1 for _ in f) - 1

        elif ext in ['.xlsx', '.xls']:
            # Use pandas to get row count
            try:
                df = pd.read_excel(path)
                return len(df)
            except Exception:
                return None

        return None
