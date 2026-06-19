"""
Validation utilities for import operations.

Provides validation at multiple levels:
- Format validation (file structure, headers, API responses)
- Field validation (types, ranges, enum values)
- Node validation (constructor checks, required fields)
- Graph validation (referential integrity, duplicates)
"""

from typing import Any, Dict, List, Optional, Type
from enum import Enum
import uuid


class ValidationError(Exception):
    """Base exception for validation errors."""
    pass


class FormatValidationError(ValidationError):
    """File or data format is invalid."""
    pass


class FieldValidationError(ValidationError):
    """Field value is invalid."""
    pass


class NodeValidationError(ValidationError):
    """Node construction or constraint violation."""
    pass


def validate_csv_headers(headers: List[str], required_columns: List[str]) -> List[str]:
    """
    Validate that CSV headers contain required columns.

    Args:
        headers: Actual CSV column headers
        required_columns: Expected required columns

    Returns:
        List of validation errors (empty if valid)
    """
    errors = []
    missing = set(required_columns) - set(headers)
    if missing:
        errors.append(f"Missing required columns: {', '.join(missing)}")
    return errors


def validate_enum_value(value: str, enum_class: Type[Enum]) -> Optional[str]:
    """
    Validate that value is valid for enum class.

    Args:
        value: String value to validate
        enum_class: Enum class

    Returns:
        Error message if invalid, None if valid
    """
    try:
        # Try exact name match
        for member in enum_class:
            if member.name == value.upper():
                return None
            if hasattr(member, 'value') and member.value == value:
                return None

        # Try case-insensitive match
        for member in enum_class:
            if member.name.upper() == value.upper():
                return None

        # Suggest closest match
        suggestions = [m.name for m in enum_class]
        return f"Invalid enum value '{value}'. Valid values: {', '.join(suggestions)}"

    except (AttributeError, TypeError) as e:
        return f"Enum validation error: {e}"


def validate_range(value: float, min_val: float, max_val: float, field_name: str) -> Optional[str]:
    """
    Validate that numeric value is within range.

    Args:
        value: Value to validate
        min_val: Minimum allowed value
        max_val: Maximum allowed value
        field_name: Field name for error messages

    Returns:
        Error message if invalid, None if valid
    """
    if value < min_val or value > max_val:
        return f"{field_name} must be between {min_val} and {max_val}, got {value}"
    return None


def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> List[str]:
    """
    Validate that required fields are present and non-empty.

    Args:
        data: Data dictionary
        required_fields: List of required field names

    Returns:
        List of validation errors
    """
    errors = []
    for field in required_fields:
        if field not in data:
            errors.append(f"Required field '{field}' is missing")
        elif data[field] is None or data[field] == "":
            errors.append(f"Required field '{field}' cannot be empty")
    return errors


def validate_uuid(value: str, field_name: str) -> Optional[str]:
    """
    Validate that string is valid UUID.

    Args:
        value: String to validate
        field_name: Field name for error messages

    Returns:
        Error message if invalid, None if valid
    """
    try:
        uuid.UUID(value)
        return None
    except (ValueError, AttributeError):
        return f"{field_name} must be a valid UUID, got '{value}'"


def validate_node_type(node_type: str, available_types: List[str]) -> Optional[str]:
    """
    Validate that node type exists in SFM schema.

    Args:
        node_type: Node type name
        available_types: List of valid node type names

    Returns:
        Error message if invalid, None if valid
    """
    if node_type not in available_types:
        # Find closest match for suggestion
        suggestions = [t for t in available_types if node_type.lower() in t.lower()]
        if suggestions:
            return f"Unknown node type '{node_type}'. Did you mean: {', '.join(suggestions[:3])}?"
        return f"Unknown node type '{node_type}'. Valid types: {', '.join(available_types[:10])}..."
    return None


def validate_duplicate_ids(ids: List[uuid.UUID]) -> List[str]:
    """
    Check for duplicate node IDs.

    Args:
        ids: List of node IDs

    Returns:
        List of validation errors
    """
    errors = []
    seen = set()
    for node_id in ids:
        if node_id in seen:
            errors.append(f"Duplicate node ID: {node_id}")
        seen.add(node_id)
    return errors


def suggest_enum_fix(value: str, enum_class: Type[Enum]) -> Optional[str]:
    """
    Suggest closest matching enum value.

    Args:
        value: Invalid value
        enum_class: Enum class

    Returns:
        Suggestion or None
    """
    value_upper = value.upper()
    for member in enum_class:
        # Check if value is substring of enum name
        if value_upper in member.name:
            return f"Did you mean '{member.name}'?"

    # No close match found
    return None
