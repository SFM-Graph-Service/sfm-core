"""
Base classes and interfaces for bulk data import adapters.

Provides abstract base class for import adapters and common data structures
for import results, configuration, and errors.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Iterator, List, Optional, Union
from pathlib import Path

from models.base_nodes import Node
from graph.sfm_graph import Relationship


@dataclass
class ImportError:
    """Details about an import error."""
    row: Optional[int] = None
    field: Optional[str] = None
    message: str = ""
    suggested_fix: Optional[str] = None


@dataclass
class ImportResult:
    """
    Result of a bulk import operation.

    Provides statistics on success/failure counts, detailed error reports,
    warnings, and performance metrics.
    """
    nodes_created: int = 0
    nodes_failed: int = 0
    relationships_created: int = 0
    relationships_failed: int = 0
    errors: List[ImportError] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    elapsed_time: float = 0.0

    def add_error(self, row: Optional[int], field: Optional[str],
                  message: str, suggested_fix: Optional[str] = None) -> None:
        """Add an error to the result."""
        self.errors.append(ImportError(
            row=row,
            field=field,
            message=message,
            suggested_fix=suggested_fix
        ))

    def add_warning(self, message: str) -> None:
        """Add a warning to the result."""
        self.warnings.append(message)


@dataclass
class ImportConfig:
    """
    Configuration for import operations.

    Controls validation behavior, error handling, and performance tuning.
    """
    dry_run: bool = False              # Validate without persisting
    continue_on_error: bool = True     # Skip invalid rows vs. abort
    batch_size: int = 1000             # Nodes per bulk flush
    validate_enums: bool = True        # Strict enum validation
    validate_references: bool = False  # Check relationship source/target existence
    default_node_type: str = "Node"    # Fallback when type not specified

    # Progress tracking
    show_progress: bool = False
    progress_interval: int = 100       # Update every N rows


class BaseImportAdapter(ABC):
    """
    Abstract base class for data import adapters.

    Adapters transform external data formats (CSV, API responses, etc.)
    into SFM nodes and relationships. Each adapter implements:
    - Format detection
    - Data extraction (streaming)
    - Field mapping to SFM schema
    """

    def __init__(self, config: Optional[ImportConfig] = None):
        """
        Initialize adapter with configuration.

        Args:
            config: Import configuration (uses defaults if not provided)
        """
        self.config = config or ImportConfig()

    @abstractmethod
    def detect_format(self, source: Union[str, Path, Dict[str, Any]]) -> bool:
        """
        Auto-detect if this adapter can handle the given source.

        Args:
            source: File path, URL, or data dictionary

        Returns:
            True if adapter can handle this source
        """
        pass

    @abstractmethod
    def extract_nodes(self, source: Union[str, Path, Dict[str, Any]]) -> Iterator[Dict[str, Any]]:
        """
        Extract node data from source as dictionaries.

        Yields raw dictionaries with external field names. The mapping layer
        will transform these to SFM node attributes.

        Args:
            source: Data source to extract from

        Yields:
            Dictionaries with external field names and values
        """
        pass

    @abstractmethod
    def extract_relationships(self, source: Union[str, Path, Dict[str, Any]]) -> Iterator[Dict[str, Any]]:
        """
        Extract relationship data from source as dictionaries.

        Not all formats support relationships. Return empty iterator if unsupported.

        Args:
            source: Data source to extract from

        Yields:
            Dictionaries with source_id, target_id, kind, weight, etc.
        """
        pass

    def validate_format(self, source: Union[str, Path, Dict[str, Any]]) -> List[str]:
        """
        Validate source format before extraction.

        Args:
            source: Data source to validate

        Returns:
            List of validation errors (empty if valid)
        """
        return []

    def estimate_size(self, source: Union[str, Path, Dict[str, Any]]) -> Optional[int]:
        """
        Estimate number of nodes that will be extracted.

        Used for progress tracking. Return None if size cannot be determined.

        Args:
            source: Data source

        Returns:
            Estimated node count or None
        """
        return None
