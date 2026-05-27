"""
Field mapping configuration for import adapters.

Provides declarative mapping from external data formats to SFM node attributes,
including type coercion, enum translation, and metadata extraction.
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
from enum import Enum
import uuid
from datetime import datetime


@dataclass
class FieldMapping:
    """
    Maps a single field from external format to SFM node attribute.

    Supports:
    - Direct field mapping (external_col -> node.attribute)
    - Nested metadata mapping (external_col -> node.meta["key"])
    - Type coercion via transform function
    - Required/optional fields with defaults
    """
    source_field: str                    # Column name in external data
    target_field: str                    # Node attribute (or "meta.key" for metadata)
    transform: Optional[Callable[[Any], Any]] = None  # Transformation function
    required: bool = False               # Error if missing
    default: Any = None                  # Default if missing

    def apply(self, row_data: Dict[str, Any]) -> tuple[str, Any]:
        """
        Apply mapping to extract and transform value from row.

        Args:
            row_data: Dictionary of external field names -> values

        Returns:
            Tuple of (target_field, transformed_value)

        Raises:
            KeyError: If required field is missing
            ValueError: If transformation fails
        """
        # Get source value
        if self.source_field not in row_data:
            if self.required:
                raise KeyError(f"Required field '{self.source_field}' not found in data")
            value = self.default
        else:
            value = row_data[self.source_field]

        # Apply transformation
        if value is not None and self.transform is not None:
            try:
                value = self.transform(value)
            except (ValueError, TypeError) as e:
                raise ValueError(
                    f"Failed to transform field '{self.source_field}': {e}"
                ) from e

        return (self.target_field, value)


@dataclass
class MappingConfig:
    """
    Complete mapping configuration for transforming external data to SFM nodes.

    Defines:
    - Target node type
    - Field mappings (external -> SFM attributes)
    - Enum translations
    - Type coercion rules
    """
    node_type: str  # SFM node type name (e.g., "InstitutionalStructure")
    mappings: List[FieldMapping] = field(default_factory=list)

    def add_mapping(self, mapping: FieldMapping) -> None:
        """Add a field mapping."""
        self.mappings.append(mapping)

    def transform_row(self, row_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform external row data to SFM node attributes.

        Args:
            row_data: Dictionary of external field names -> values

        Returns:
            Dictionary of SFM node attributes

        Raises:
            KeyError: If required field missing
            ValueError: If transformation fails
        """
        result = {
            "_node_type": self.node_type  # Store type for later instantiation
        }
        meta_dict = {}

        for mapping in self.mappings:
            target_field, value = mapping.apply(row_data)

            # Handle metadata fields (format: "meta.key")
            if target_field.startswith("meta."):
                meta_key = target_field[5:]  # Remove "meta." prefix
                meta_dict[meta_key] = value
            else:
                result[target_field] = value

        # Add meta dict if any metadata was collected
        if meta_dict:
            result["meta"] = meta_dict

        return result


class MappingTemplates:
    """
    Pre-built mapping templates for common data formats.

    Provides ready-to-use configurations for typical scenarios like:
    - CSV files with institutional data
    - OECD statistical indicators
    - World Bank development data
    - Generic nodes (label + description only)
    """

    @staticmethod
    def basic_node() -> MappingConfig:
        """
        Basic node mapping with just label and description.

        Expected CSV columns: name, description
        """
        config = MappingConfig(node_type="Node")
        config.add_mapping(FieldMapping(
            source_field="name",
            target_field="label",
            required=True
        ))
        config.add_mapping(FieldMapping(
            source_field="description",
            target_field="description",
            default=""
        ))
        return config

    @staticmethod
    def csv_institution() -> MappingConfig:
        """
        Institutional structure mapping for CSV files.

        Expected CSV columns: name, description, type, jurisdiction
        Maps to InstitutionalStructure node type.
        """
        config = MappingConfig(node_type="InstitutionalStructure")

        config.add_mapping(FieldMapping(
            source_field="name",
            target_field="label",
            required=True
        ))
        config.add_mapping(FieldMapping(
            source_field="description",
            target_field="description",
            default=""
        ))
        config.add_mapping(FieldMapping(
            source_field="type",
            target_field="institution_type",
            transform=lambda x: x.upper() if x else None
        ))
        config.add_mapping(FieldMapping(
            source_field="jurisdiction",
            target_field="meta.jurisdiction"
        ))
        return config

    @staticmethod
    def oecd_indicator() -> MappingConfig:
        """
        OECD statistical indicator mapping.

        Expected JSON fields: LOCATION, Value, TIME_PERIOD, INDICATOR
        Maps to SocialFabricIndicator node type.
        """
        config = MappingConfig(node_type="SocialFabricIndicator")

        config.add_mapping(FieldMapping(
            source_field="INDICATOR",
            target_field="label",
            required=True
        ))
        config.add_mapping(FieldMapping(
            source_field="LOCATION",
            target_field="meta.country",
            transform=lambda x: x.upper() if x else None
        ))
        config.add_mapping(FieldMapping(
            source_field="Value",
            target_field="current_value",
            transform=float,
            required=True
        ))
        config.add_mapping(FieldMapping(
            source_field="TIME_PERIOD",
            target_field="meta.year",
            transform=int
        ))
        return config

    @staticmethod
    def worldbank_indicator() -> MappingConfig:
        """
        World Bank indicator mapping.

        Expected JSON fields: indicator, country, value, date
        Maps to SocialFabricIndicator node type.
        """
        config = MappingConfig(node_type="SocialFabricIndicator")

        config.add_mapping(FieldMapping(
            source_field="indicator",
            target_field="label",
            required=True
        ))
        config.add_mapping(FieldMapping(
            source_field="country",
            target_field="meta.country"
        ))
        config.add_mapping(FieldMapping(
            source_field="value",
            target_field="current_value",
            transform=float
        ))
        config.add_mapping(FieldMapping(
            source_field="date",
            target_field="meta.year",
            transform=int
        ))
        return config


# Helper functions for common transformations

def parse_datetime(value: str) -> datetime:
    """Parse datetime from ISO format string."""
    return datetime.fromisoformat(value)


def parse_uuid(value: str) -> uuid.UUID:
    """Parse UUID from string."""
    return uuid.UUID(value)


def parse_enum(enum_class: type) -> Callable[[str], Enum]:
    """
    Create enum parser for specific enum class.

    Args:
        enum_class: Enum class to parse

    Returns:
        Function that parses string to enum value
    """
    def parser(value: str) -> Enum:
        """Parse string to enum value."""
        # Try exact match first
        for member in enum_class:
            if member.name == value.upper():
                return member
            if hasattr(member, 'value') and member.value == value:
                return member

        # Fall back to case-insensitive name match
        for member in enum_class:
            if member.name.upper() == value.upper():
                return member

        raise ValueError(f"'{value}' is not a valid {enum_class.__name__}")

    return parser


def to_float(value: Any) -> float:
    """Convert value to float, handling empty strings."""
    if value == "" or value is None:
        return 0.0
    return float(value)


def to_int(value: Any) -> int:
    """Convert value to int, handling empty strings."""
    if value == "" or value is None:
        return 0
    return int(value)
