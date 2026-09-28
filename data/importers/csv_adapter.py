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
import json
import uuid
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Union
import pandas as pd

from .base_adapter import BaseImportAdapter, ImportConfig
from .mapping_config import MappingConfig
from .validators import validate_csv_headers


def _is_uri_like_source(value: str) -> bool:
    """
    Return True when a source string looks like a non-local identifier/URI (scheme:... or scheme://...),
    rather than a filesystem path.

    Notes:
    - Windows drive-letter paths (e.g. "C:\\tmp\\file.csv") are treated as local paths.
    """
    # Windows drive-letter paths: "C:\\...", "C:/...", or "C:relative"
    if len(value) >= 2 and value[1] == ":" and value[0].isalpha():
        return False

    if "://" in value:
        return True

    if ":" in value:
        scheme = value.split(":", 1)[0]
        return scheme.isalpha()

    return False


def _validate_safe_path(path: Path, base_dir: Optional[Path] = None) -> Path:
    """
    Validate path for security against path traversal attacks.

    Two-tier validation:
    1. ALWAYS blocks obvious path traversal attempts (../, ../../, etc.)
    2. OPTIONALLY enforces strict directory restriction (if base_dir provided)

    This approach:
    - Prevents CWE-22 path traversal attacks (always enabled)
    - Maintains backward compatibility (strict mode opt-in)
    - Allows tempfile usage while blocking malicious paths

    Args:
        path: Path to validate
        base_dir: Optional base directory for strict mode.
                 None = only block obvious attacks (backward compatible)
                 Path = also enforce path must be within this directory

    Returns:
        Resolved absolute path

    Raises:
        ValueError: If path contains traversal attempts or (in strict mode) is outside base_dir

    Examples:
        # Backward compatible mode (blocks obvious attacks only):
        >>> _validate_safe_path(Path("/tmp/file.csv"))  # ✅ OK
        >>> _validate_safe_path(Path("../../etc/passwd"))  # ❌ ValueError

        # Strict mode (enforces directory restriction):
        >>> _validate_safe_path(Path("/tmp/file.csv"), base_dir=Path("/tmp"))  # ✅ OK
        >>> _validate_safe_path(Path("/tmp/file.csv"), base_dir=Path.cwd())  # ❌ ValueError
    """
    # Convert to Path if string
    path = Path(path)

    # ALWAYS block obvious path traversal patterns before resolution
    # This catches "../../../etc/passwd" and similar attacks
    if ".." in path.parts:
        raise ValueError(
            f"Path traversal detected: path contains '..' component: {path}. "
            "This is a security risk (CWE-22)."
        )

    # Resolve to absolute path to handle symlinks and relative paths
    try:
        resolved_path = path.resolve()
    except (OSError, RuntimeError) as e:
        raise ValueError(f"Invalid path: {e}") from e

    # OPTIONAL: Strict directory restriction (if base_dir provided)
    if base_dir is not None:
        try:
            resolved_base = base_dir.resolve()
            resolved_path.relative_to(resolved_base)
        except ValueError as e:
            raise ValueError(
                f"Path outside allowed directory: {path} resolves to {resolved_path}, "
                f"which is not within {base_dir}"
            ) from e
        except (OSError, RuntimeError) as e:
            raise ValueError(f"Invalid base directory: {e}") from e

    return resolved_path


class CSVImportAdapter(BaseImportAdapter):
    """
    Import adapter for CSV and Excel files.

    Uses streaming architecture to handle large files without loading
    entire dataset into memory. Supports field mapping, type coercion,
    and enum translation.
    """

    RELATIONSHIP_SOURCE_COLUMNS = ("source", "source_id", "from", "source_label")
    RELATIONSHIP_TARGET_COLUMNS = ("target", "target_id", "to", "target_label")
    RELATIONSHIP_KIND_COLUMNS = ("kind", "type", "relationship", "relationship_type", "predicate")

    def __init__(
        self,
        mapping: MappingConfig,
        config: Optional[ImportConfig] = None,
        allowed_base_dir: Optional[Path] = None,
        relationships_file: Optional[Union[str, Path]] = None,
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
            relationships_file: Optional CSV of relationships with columns
                            source, target, kind and optionally weight, id, meta (JSON),
                            confidence, data_sources (';'-separated). source/target may be
                            node UUIDs or node labels. If omitted, a sibling file named
                            ``<stem>_relationships<suffix>`` is used when it exists.
        """
        super().__init__(config)
        self.mapping = mapping
        self.allowed_base_dir = allowed_base_dir
        self.relationships_file = Path(relationships_file) if relationships_file else None

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

        if isinstance(source, str) and _is_uri_like_source(source):
            return False

        path = Path(source) if isinstance(source, str) else source

        # Validate path before accessing filesystem
        # Always validates against path traversal; optionally enforces base_dir restriction
        try:
            safe_path = _validate_safe_path(path, self.allowed_base_dir)
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
        if isinstance(source, dict):
            raise TypeError(f"Expected a file path, got dict: {source}")
        if isinstance(source, str) and _is_uri_like_source(source):
            raise ValueError(f"Expected a local file path, got non-file source: {source}")
        path = Path(source) if isinstance(source, str) else source

        # Validate path for security (always blocks path traversal)
        safe_path = _validate_safe_path(path, self.allowed_base_dir)

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
        # Path should already be validated by caller, but double-check for safety
        safe_path = _validate_safe_path(path, self.allowed_base_dir)

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
        # Path should already be validated by caller, but double-check for safety
        safe_path = _validate_safe_path(path, self.allowed_base_dir)

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

    def _relationships_path(self, source: Union[str, Path, Dict[str, Any]]) -> Optional[Path]:
        if self.relationships_file is not None:
            return _validate_safe_path(self.relationships_file, self.allowed_base_dir)
        if isinstance(source, dict) or (isinstance(source, str) and _is_uri_like_source(source)):
            return None
        node_path = Path(source)
        sibling = node_path.with_name(f"{node_path.stem}_relationships{node_path.suffix or '.csv'}")
        if sibling.exists():
            return _validate_safe_path(sibling, self.allowed_base_dir)
        return None

    @staticmethod
    def _pick(row: Dict[str, Any], names: tuple) -> Optional[str]:
        lowered = {str(k).strip().lower(): v for k, v in row.items() if k is not None}
        for name in names:
            value = lowered.get(name)
            if value is not None and str(value).strip() != "":
                return str(value).strip()
        return None

    @staticmethod
    def _endpoint(value: str) -> Dict[str, Any]:
        """A UUID string references a node id; anything else references a node label."""
        try:
            return {"id": uuid.UUID(value)}
        except ValueError:
            return {"label": value}

    def extract_relationships(self, source: Union[str, Path, Dict[str, Any]]) -> Iterator[Dict[str, Any]]:
        """
        Extract relationships from a companion CSV (see ``relationships_file``).

        Yields dicts with ``source_id``/``target_id`` (when the column held a UUID) or
        ``source_label``/``target_label`` (when it held a node label, resolved by
        ``SFMService.import_bulk``), plus ``kind``, ``weight``, ``meta`` and optional
        ``id``, ``confidence`` and ``data_sources``.
        """
        path = self._relationships_path(source)
        if path is None:
            return
        if not path.exists():
            raise FileNotFoundError(f"Relationships file not found: {path}")

        if path.suffix.lower() in (".xlsx", ".xls"):
            rows: List[Dict[str, Any]] = [r.to_dict() for _, r in pd.read_excel(path).iterrows()]
        else:
            with open(path, "r", newline="", encoding="utf-8") as f:
                rows = list(csv.DictReader(f, delimiter=self._detect_delimiter(path)))

        for row_num, row in enumerate(rows, start=1):
            src = self._pick(row, self.RELATIONSHIP_SOURCE_COLUMNS)
            tgt = self._pick(row, self.RELATIONSHIP_TARGET_COLUMNS)
            kind = self._pick(row, self.RELATIONSHIP_KIND_COLUMNS)
            if not src or not tgt or not kind:
                if not self.config.continue_on_error:
                    raise ValueError(f"Relationship row {row_num}: source, target and kind are required")
                continue

            rel: Dict[str, Any] = {"kind": kind, "meta": {}}
            for prefix, value in (("source", src), ("target", tgt)):
                for key, resolved in self._endpoint(value).items():
                    rel[f"{prefix}_{key}"] = resolved

            weight = self._pick(row, ("weight",))
            if weight is not None:
                try:
                    rel["weight"] = float(weight)
                except ValueError:
                    if not self.config.continue_on_error:
                        raise ValueError(f"Relationship row {row_num}: weight '{weight}' is not numeric")
                    continue
            rel_id = self._pick(row, ("id",))
            if rel_id:
                try:
                    rel["id"] = uuid.UUID(rel_id)
                except ValueError:
                    rel["id"] = uuid.uuid5(uuid.NAMESPACE_URL, f"{path}:{rel_id}")
            confidence = self._pick(row, ("confidence",))
            if confidence is not None:
                try:
                    rel["confidence"] = float(confidence)
                except ValueError:
                    pass
            sources = self._pick(row, ("data_sources", "sources"))
            if sources:
                rel["data_sources"] = [s.strip() for s in sources.split(";") if s.strip()]
            meta = self._pick(row, ("meta",))
            if meta:
                try:
                    parsed = json.loads(meta)
                    if isinstance(parsed, dict):
                        rel["meta"] = parsed
                except json.JSONDecodeError:
                    rel["meta"] = {"note": meta}
            yield rel

    def _detect_delimiter(self, path: Path) -> str:
        """
        Auto-detect CSV delimiter.

        Args:
            path: Validated safe path to CSV file

        Returns:
            Detected delimiter (comma, tab, semicolon, pipe)
        """
        # Path should already be validated by caller, but double-check for safety
        safe_path = _validate_safe_path(path, self.allowed_base_dir)

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
        if isinstance(source, dict):
            errors.append("Invalid path: expected a file path, got dict")
            return errors
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
        if isinstance(source, dict):
            return None
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
