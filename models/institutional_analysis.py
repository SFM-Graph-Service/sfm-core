"""
Institutional analysis components for the Social Fabric Matrix framework.

This module contains classes for analyzing institutional structures,
path dependencies, and institutional arrangements.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from models.base_nodes import Node
from models.sfm_enums import PathDependencyType


@dataclass
class InstitutionalStructure(Node):
    """Represents institutional arrangements and their structural properties."""

    structure_type: str = "formal"  # Made string with default instead of enum to fix ordering
    governance_mechanism: str = "hierarchical"  # Made string with default instead of enum
    decision_making_process: str = "autocratic"  # Made string with default instead of enum
    enforcement_mechanism: str = "legal"  # Made string with default instead of enum
    scope: str = "local"  # Made string with default instead of enum
    legitimacy_source: Optional[str] = None  # What gives this institution legitimacy
    power_distribution: Dict[str, float] = field(default_factory=lambda: {})  # How power is distributed
    accountability_mechanisms: List[str] = field(default_factory=lambda: [])  # How institution is held accountable
    change_mechanisms: List[str] = field(default_factory=lambda: [])  # How institution can change
    formal_rules: List[str] = field(default_factory=lambda: [])  # Written rules
    informal_norms: List[str] = field(default_factory=lambda: [])  # Unwritten conventions
    sanctions: List[str] = field(default_factory=lambda: [])  # Penalties for non-compliance
    institutional_memory: Optional[str] = None  # How knowledge is preserved


@dataclass
class PathDependencyAnalysis(Node):
    """Analysis of path-dependent institutional development."""

    analyzed_institution_id: Optional[uuid.UUID] = None  # Made optional for dataclass ordering
    dependency_strength: PathDependencyType = PathDependencyType.MODERATE
    critical_junctures: List[str] = field(default_factory=lambda: [])  # Key historical moments
    lock_in_mechanisms: List[str] = field(default_factory=lambda: [])  # What creates lock-in
    switching_costs: Dict[str, float] = field(default_factory=lambda: {})  # Costs of change
    alternative_paths: List[str] = field(default_factory=lambda: [])   # What could have been
    intervention_points: List[str] = field(default_factory=lambda: [])  # Where change is possible
    historical_trajectory: List[str] = field(default_factory=lambda: [])  # Development path
    path_efficiency: Optional[float] = None  # How efficient is current path (0-1)
    exit_barriers: List[str] = field(default_factory=lambda: [])  # Barriers to changing path
    network_effects: Optional[float] = None  # Strength of network effects (0-1)

    def __post_init__(self) -> None:
        """Validate that analyzed institution is provided."""
        if self.analyzed_institution_id is None:
            raise ValueError("analyzed_institution_id is required for PathDependencyAnalysis")
