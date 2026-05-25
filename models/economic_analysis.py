"""
Economic analysis components for the Social Fabric Matrix framework.

This module contains classes for analyzing transaction costs, coordination
mechanisms, commons governance, and other economic aspects of institutions.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import List, Optional

from models.base_nodes import Node
from models.sfm_enums import (
    CoordinationMechanismType,
    CoordinationScope,
    CommonsGovernanceType,
)


@dataclass
class TransactionCost(Node):
    """Analysis of costs associated with institutional transactions."""

    cost_type: str = "search_information"  # Made string with default instead of enum
    cost_amount: Optional[float] = None  # Monetary cost if quantifiable
    time_cost: Optional[float] = None    # Time required
    uncertainty_cost: Optional[float] = None  # Risk/uncertainty costs
    bargaining_cost: Optional[float] = None   # Negotiation costs
    enforcement_cost: Optional[float] = None  # Monitoring/compliance costs
    affected_institutions: List[uuid.UUID] = field(default_factory=lambda: [])
    reduction_strategies: List[str] = field(default_factory=lambda: [])
    measurement_approach: str = "qualitative"
    cost_drivers: List[str] = field(default_factory=lambda: [])  # What causes these costs
    cost_beneficiaries: List[uuid.UUID] = field(default_factory=lambda: [])  # Who benefits from these costs


@dataclass
class CoordinationMechanism(Node):
    """Represents mechanisms for coordinating economic activity."""

    mechanism_type: CoordinationMechanismType = CoordinationMechanismType.PRICE_SYSTEM
    coordination_scope: CoordinationScope = CoordinationScope.LOCAL
    effectiveness_measure: Optional[float] = None  # How well it coordinates (0-1)
    participating_actors: List[uuid.UUID] = field(default_factory=lambda: [])
    coordinated_activities: List[uuid.UUID] = field(default_factory=lambda: [])
    information_requirements: List[str] = field(default_factory=lambda: [])
    failure_modes: List[str] = field(default_factory=lambda: [])
    backup_mechanisms: List[uuid.UUID] = field(default_factory=lambda: [])
    coordination_costs: Optional[float] = None  # Cost of coordination
    response_time: Optional[float] = None  # How quickly mechanism responds
    adaptability: Optional[float] = None  # Ability to adapt to change (0-1)


@dataclass
class CommonsGovernance(Node):
    """Analysis of common pool resource governance."""

    resource_id: Optional[uuid.UUID] = None  # The commons resource - made optional for dataclass ordering
    governance_type: CommonsGovernanceType = CommonsGovernanceType.COMMUNITY_MANAGED
    design_principles: List[str] = field(default_factory=lambda: [])  # Ostrom's principles
    user_community: List[uuid.UUID] = field(default_factory=lambda: [])  # Resource users
    monitoring_mechanisms: List[str] = field(default_factory=lambda: [])
    conflict_resolution: List[str] = field(default_factory=lambda: [])
    sustainability_indicators: List[uuid.UUID] = field(default_factory=lambda: [])
    threat_level: Optional[float] = None  # Threat to commons (0-1)
    governance_effectiveness: Optional[float] = None  # How well governance works (0-1)
    resource_condition: Optional[float] = None  # Current state of resource (0-1)
    collective_action_capacity: Optional[float] = None  # Community's ability to act collectively (0-1)
    external_pressures: List[str] = field(default_factory=lambda: [])  # External threats

    def __post_init__(self) -> None:
        """Validate that resource is provided."""
        if self.resource_id is None:
            raise ValueError("resource_id is required for CommonsGovernance")
