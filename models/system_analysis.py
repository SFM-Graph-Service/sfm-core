"""
System analysis components for the Social Fabric Matrix framework.

This module contains classes for analyzing system-level properties, metrics,
and comprehensive system analysis capabilities.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any

from models.base_nodes import Node
from models.sfm_enums import (
    SystemPropertyType,
    SystemArchetype,
    InstitutionalLevel,
)


@dataclass
class SystemProperty(Node):  # pylint: disable=too-many-instance-attributes
    """Represents a system-level property or metric of the SFM."""

    property_type: SystemPropertyType = SystemPropertyType.STRUCTURAL
    value: Any = None
    unit: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    # Nodes that this property applies to
    affected_nodes: List[uuid.UUID] = field(default_factory=lambda: [])
    # Relationships that contribute to this property
    contributing_relationships: List[uuid.UUID] = field(default_factory=lambda: [])
    # id, name, and description are inherited from Node


@dataclass
class SystemLevelAnalysis(Node):
    """Comprehensive system-level analysis of SFM."""

    analyzed_system_boundary: str = "undefined"
    institutions_analyzed: List[uuid.UUID] = field(default_factory=lambda: [])
    actors_analyzed: List[uuid.UUID] = field(default_factory=lambda: [])

    # System properties
    system_coherence: Optional[float] = None      # How well-integrated (0-1)
    system_resilience: Optional[float] = None     # Ability to handle shocks (0-1)
    system_adaptability: Optional[float] = None   # Capacity for change (0-1)
    system_efficiency: Optional[float] = None     # Resource utilization (0-1)
    system_sustainability: Optional[float] = None # Long-term viability (0-1)

    # Bottlenecks and leverage points
    system_bottlenecks: List[uuid.UUID] = field(default_factory=lambda: [])
    leverage_points: List[uuid.UUID] = field(default_factory=lambda: [])
    critical_dependencies: List[uuid.UUID] = field(default_factory=lambda: [])

    # System dynamics
    dominant_feedback_loops: List[uuid.UUID] = field(default_factory=lambda: [])
    system_archetypes: List[SystemArchetype] = field(default_factory=lambda: [])
    change_capacity: Optional[float] = None
    emergence_patterns: List[str] = field(default_factory=lambda: [])  # Emergent behaviors
    system_learning_rate: Optional[float] = None  # How fast system learns (0-1)

    def __post_init__(self) -> None:
        """Validate that system boundary is defined."""
        if not self.analyzed_system_boundary or self.analyzed_system_boundary == "undefined":
            raise ValueError("analyzed_system_boundary must be defined for SystemLevelAnalysis")


@dataclass
class InstitutionalHolarchy(Node):  # pylint: disable=too-many-instance-attributes
    """Represents nested levels of institutional arrangements per Hayden's framework."""

    institutional_levels: Dict[InstitutionalLevel, List[uuid.UUID]] = field(default_factory=lambda: {})
    level_interactions: Dict[str, Dict[str, float]] = field(default_factory=lambda: {})  # Inter-level relationships
    authority_flows: Dict[str, List[uuid.UUID]] = field(default_factory=lambda: {})  # How authority flows

    # Holarchy properties
    emergence_patterns: List[str] = field(default_factory=lambda: [])  # How higher levels emerge
    constraint_flows: Dict[str, List[str]] = field(default_factory=lambda: {})  # Top-down constraints
    innovation_sources: Dict[InstitutionalLevel, List[str]] = field(default_factory=lambda: {})  # Where innovation occurs

    # SFM integration
    matrix_cell_mapping: Dict[InstitutionalLevel, List[uuid.UUID]] = field(default_factory=lambda: {})  # Cells by level
    cross_level_dependencies: List[uuid.UUID] = field(default_factory=lambda: [])  # Dependencies across levels
    power_concentration: Dict[InstitutionalLevel, float] = field(default_factory=lambda: {})  # Power distribution

    # System properties
    hierarchical_coherence: Optional[float] = None  # How well levels work together (0-1)
    adaptive_capacity_by_level: Dict[InstitutionalLevel, float] = field(default_factory=lambda: {})
    bottleneck_levels: List[InstitutionalLevel] = field(default_factory=lambda: [])  # Constraint points

    def calculate_system_coherence(self) -> float:
        """Calculate overall coherence of the institutional holarchy."""
        if not self.level_interactions:
            return 0.0

        # Sum positive interactions, penalize negative ones
        total_interactions = 0
        positive_interactions = 0

        for level_interactions in self.level_interactions.values():
            for interaction_strength in level_interactions.values():
                total_interactions += 1
                if interaction_strength > 0:
                    positive_interactions += interaction_strength

        return positive_interactions / total_interactions if total_interactions > 0 else 0.0

    def identify_leverage_points(self) -> List[InstitutionalLevel]:
        """Identify levels with highest leverage for system change."""
        leverage_scores: Dict[InstitutionalLevel, float] = {}

        for level in InstitutionalLevel:
            # Count connections and power concentration
            connections = len(self.institutional_levels.get(level, []))
            power = self.power_concentration.get(level, 0.0)
            leverage_scores[level] = connections * power

        # Return top 3 leverage points
        sorted_levels = sorted(leverage_scores.items(), key=lambda x: x[1], reverse=True)
        return [level for level, _ in sorted_levels[:3]]