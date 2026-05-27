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


def _validate_safe_path(path: Path, base_dir: Optional[Path] = None) -> Path:
    """
    Validate that path is safe and doesn't escape base directory.

    Prevents path traversal attacks by ensuring resolved path is within
    the allowed base directory.

    Args:
        path: Path to validate
        base_dir: Base directory to restrict access to (default: current working directory)

    Returns:
        Resolved absolute path

    Raises:
        ValueError: If path attempts to escape base directory or contains unsafe components
    """
    if base_dir is None:
        base_dir = Path.cwd()

    # Resolve to absolute path to handle symlinks and relative paths
    try:
        resolved_path = path.resolve()
        resolved_base = base_dir.resolve()
    except (OSError, RuntimeError) as e:
        raise ValueError(f"Invalid path: {e}") from e

    # Check if resolved path is within base directory
    try:
        resolved_path.relative_to(resolved_base)
    except ValueError as e:
        raise ValueError(
            f"Path traversal detected: {path} resolves outside allowed directory {base_dir}"
        ) from e

    return resolved_path


class CSVImportAdapter(BaseImportAdapter):
    """
    Import adapter for CSV and Excel files.

    Uses streaming architecture to handle large files without loading
    entire dataset into memory. Supports field mapping, type coercion,
    and enum translation.
    """

    def __init__(
        self,
        mapping: MappingConfig,
        config: Optional[ImportConfig] = None,
        allowed_base_dir: Optional[Path] = None
    ):
        """
        Initialize CSV adapter with field mapping.

        Args:
            mapping: Field mapping configuration
            config: Import configuration
            allowed_base_dir: Base directory for path validation.
                            None (default) = path traversal validation disabled (backward compatible).
                            Path object = only allow files within this directory tree.
                            For production file uploads, set to a secure upload directory.
        """
        super().__init__(config)
        self.mapping = mapping
        self.allowed_base_dir = allowed_base_dir

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

        # Validate path before accessing filesystem (if enabled)
        try:
            safe_path = _validate_safe_path(path, self.allowed_base_dir) if self.allowed_base_dir else path
        except ValueError:
            return False

        if not safe_path.exists():
            return False

        # Check file extension
        ext = safe_path.suffix.lower()
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

        # Validate path for security (if enabled)
        safe_path = _validate_safe_path(path, self.allowed_base_dir) if self.allowed_base_dir else path

        if not safe_path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        # Route to appropriate handler
        ext = safe_path.suffix.lower()
        if ext in ['.csv', '.tsv', '.txt']:
            yield from self._extract_from_csv(safe_path)
        elif ext in ['.xlsx', '.xls']:
            yield from self._extract_from_excel(safe_path)
        else:
            raise ValueError(f"Unsupported file type: {ext}")

    def _extract_from_csv(self, path: Path) -> Iterator[Dict[str, Any]]:
        """
        Stream nodes from CSV file.

        Args:
            path: Validated safe path to CSV file

        Yields:
            Mapped node dictionaries
        """
        # Path should already be validated by caller, but ensure it's safe (if enabled)
        safe_path = _validate_safe_path(path, self.allowed_base_dir) if self.allowed_base_dir else path

        # Auto-detect delimiter
        delimiter = self._detect_delimiter(safe_path)

        with open(safe_path, 'r', newline='', encoding='utf-8') as f:
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
        Extract nodes from Excel file.

        Note: pandas read_excel does not support chunked reading,
        so entire file is loaded into memory. For very large Excel files,
        consider converting to CSV first.

        Args:
            path: Validated safe path to Excel file

        Yields:
            Mapped node dictionaries
        """
        # Path should already be validated by caller, but ensure it's safe (if enabled)
        safe_path = _validate_safe_path(path, self.allowed_base_dir) if self.allowed_base_dir else path

        # Read entire Excel file (no chunksize support in pandas.read_excel)
        df = pd.read_excel(safe_path)

        for row_num, row in df.iterrows():
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
            path: Validated safe path to CSV file

        Returns:
            Detected delimiter (comma, tab, semicolon, pipe)
        """
        # Path should already be validated by caller, but double-check (if enabled)
        safe_path = _validate_safe_path(path, self.allowed_base_dir) if self.allowed_base_dir else path

        # Read first 1024 bytes to detect delimiter
        with open(safe_path, 'r', encoding='utf-8') as f:
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

        # Validate path for security (if enabled)
        try:
            safe_path = _validate_safe_path(path, self.allowed_base_dir) if self.allowed_base_dir else path
        except ValueError as e:
            errors.append(f"Invalid path: {e}")
            return errors

        # Check file exists
        if not safe_path.exists():
            errors.append(f"File not found: {path}")
            return errors

        # Check file extension
        ext = safe_path.suffix.lower()
        if ext not in ['.csv', '.tsv', '.txt', '.xlsx', '.xls']:
            errors.append(f"Unsupported file type: {ext}")
            return errors

        # Validate headers (CSV only, quick check)
        if ext in ['.csv', '.tsv', '.txt']:
            delimiter = self._detect_delimiter(safe_path)
            with open(safe_path, 'r', encoding='utf-8') as f:
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

        # Validate path for security (if enabled)
        try:
            safe_path = _validate_safe_path(path, self.allowed_base_dir) if self.allowed_base_dir else path
        except ValueError:
            return None

        if not safe_path.exists():
            return None

        ext = safe_path.suffix.lower()

        if ext in ['.csv', '.tsv', '.txt']:
            # Count lines (subtract 1 for header)
            with open(safe_path, 'r', encoding='utf-8') as f:
                return sum(1 for _ in f) - 1

        elif ext in ['.xlsx', '.xls']:
            # Use pandas to get row count
            try:
                df = pd.read_excel(safe_path)
                return len(df)
            except Exception:
                return None

        return None
