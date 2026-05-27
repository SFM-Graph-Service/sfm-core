"""
Base node class and core infrastructure for SFM modeling.

This module defines the foundational Node class that serves as the base
for all SFM entities.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, Iterator, Optional, Tuple, List


@dataclass
class Node:  # pylint: disable=too-many-instance-attributes
    """Generic graph node with a UUID primary key and free-form metadata."""

    label: str
    description: Optional[str] = None
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    meta: Dict[str, str] = field(default_factory=lambda: {})
    # Versioning and data quality fields
    version: int = 1
    created_at: datetime = field(default_factory=datetime.now)
    modified_at: Optional[datetime] = None
    certainty: Optional[float] = 1.0  # Confidence level (0-1)
    data_quality: Optional[str] = None  # Description of data quality
    previous_version_id: Optional[uuid.UUID] = None

    def __iter__(self) -> Iterator[Tuple[str, Any]]:
        """Iterator that yields (attribute_name, attribute_value) pairs."""
        for attr_name, attr_value in self.__dict__.items():
            yield attr_name, attr_value


@dataclass
class InformalNorm(Node):
    """
    Represents informal social norms, cultural beliefs, and voluntary standards.

    Distinguishes from formal Institutions while capturing important
    institutional economics elements.

    Examples:
    - "Industry Voluntary Emission Goals" (pre-1970 CAA)
    - "Environmental Consciousness Cultural Shift" (1970s)
    - "Professional Engineering Standards" (voluntary compliance)
    """
    norm_type: str = ""  # "cultural", "professional", "voluntary", "traditional"
    enforcement_mechanism: str = ""  # "peer_pressure", "reputation", "values", "social_sanctions"
    strength: str = ""  # "weak", "moderate", "strong"
    formalization_date: Optional[datetime] = None  # If later became formal rule
    formalized_as: Optional[uuid.UUID] = None  # Link to formal Institution if formalized
    geographic_scope: Optional[str] = None  # "local", "regional", "national", "global"

    def __post_init__(self):
        if not self.norm_type:
            self.norm_type = "cultural"
        if not self.enforcement_mechanism:
            self.enforcement_mechanism = "social_sanctions"
        if not self.strength:
            self.strength = "moderate"


@dataclass
class Event(Node):
    """
    Represents a discrete event that changes system state.

    Examples:
    - "1975 Auto Standards Delay" (Congress grants extension)
    - "1977 Clean Air Act Amendments" (New legislation passed)
    - "1981 Auto Standards Met" (Industry achieves compliance)
    """
    event_type: str = ""  # "legislative", "regulatory", "technological", "political"
    event_date: Optional[datetime] = None
    duration: Optional[timedelta] = None
    impact_magnitude: Optional[float] = None  # 0-1 scale
    affected_nodes: List[uuid.UUID] = field(default_factory=list)
    affected_relationships: List[uuid.UUID] = field(default_factory=list)

    def __post_init__(self):
        if not self.event_type:
            self.event_type = "unspecified"
