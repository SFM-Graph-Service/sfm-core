"""
Technology integration components for the Social Fabric Matrix framework.

This module contains classes for tool-skill-technology complexes, ecological
systems, and technology-institution relationships.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

from models.base_nodes import Node
from models.sfm_enums import ToolSkillTechnologyType


@dataclass
class ToolSkillTechnologyComplex(Node):
    """Hayden's integrated tool-skill-technology system."""

    technology_type: ToolSkillTechnologyType = ToolSkillTechnologyType.PHYSICAL_TOOL
    physical_tools: List[uuid.UUID] = field(default_factory=lambda: [])  # Links to TechnologySystem
    required_skills: List[uuid.UUID] = field(default_factory=lambda: [])  # Links to skill nodes
    knowledge_base: List[uuid.UUID] = field(default_factory=lambda: [])  # Links to information resources
    integration_level: Optional[float] = None  # How well integrated (0-1)
    problem_solving_capacity: Optional[float] = None  # Effectiveness (0-1)
    institutional_support_required: List[uuid.UUID] = field(default_factory=lambda: [])
    compatibility_constraints: Dict[str, str] = field(default_factory=lambda: {})
    maintenance_requirements: List[str] = field(default_factory=lambda: [])


@dataclass
class EcologicalSystem(Node):
    """Environmental component integration - part of Hayden's comprehensive SFM approach."""

    ecosystem_type: Optional[str] = None  # "forest", "watershed", "urban", etc.
    environmental_health: Optional[float] = None  # Overall health score (0-1)
    biodiversity_index: Optional[float] = None  # Biodiversity measure (0-1)
    carrying_capacity: Optional[float] = None  # Ecosystem carrying capacity
    resource_stocks: Dict[str, float] = field(default_factory=lambda: {})  # Resource type -> quantity

    # Institutional relationships
    governing_institutions: List[uuid.UUID] = field(default_factory=lambda: [])  # Institutions that govern this ecosystem
    impacting_technologies: List[uuid.UUID] = field(default_factory=lambda: [])  # Technologies affecting ecosystem
    dependent_communities: List[uuid.UUID] = field(default_factory=lambda: [])  # Communities dependent on ecosystem

    # Environmental indicators
    pollution_levels: Dict[str, float] = field(default_factory=lambda: {})  # Pollutant type -> level
    regeneration_capacity: Optional[float] = None  # Ability to regenerate (0-1)
    resilience_factors: List[str] = field(default_factory=lambda: [])  # Factors supporting resilience
    vulnerability_factors: List[str] = field(default_factory=lambda: [])  # Factors creating vulnerability

    # Matrix integration
    matrix_deliveries: List[Dict[str, Any]] = field(default_factory=lambda: [])  # Ecosystem services delivered
    matrix_requirements: List[Dict[str, Any]] = field(default_factory=lambda: [])  # Requirements from other matrix elements
    ecological_constraints: Dict[str, List[str]] = field(default_factory=lambda: {})  # Constraints on other activities

    def calculate_sustainability_score(self) -> float:
        """Calculate overall ecosystem sustainability score."""
        scores: List[float] = []

        if self.environmental_health is not None:
            scores.append(self.environmental_health * 0.3)
        if self.biodiversity_index is not None:
            scores.append(self.biodiversity_index * 0.25)
        if self.regeneration_capacity is not None:
            scores.append(self.regeneration_capacity * 0.25)

        # Factor in pollution (inverse relationship)
        if self.pollution_levels:
            avg_pollution = sum(self.pollution_levels.values()) / len(self.pollution_levels)
            scores.append((1.0 - min(1.0, avg_pollution)) * 0.2)

        return sum(scores) if scores else 0.0
