"""
Enhanced Dimensional Meta Entities and Scenario Modeling for SFM analysis.

This module defines foundational dimensional entities and comprehensive scenario
modeling capabilities for SFM analysis including time, space, scenarios, and
advanced scenario planning frameworks.
"""

from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from enum import Enum, auto

from models.base_nodes import Node

class ScenarioType(Enum):
    """Types of scenarios in SFM analysis."""

    BASELINE = auto()           # Current trends baseline
    POLICY_ALTERNATIVE = auto() # Policy intervention scenarios
    COUNTERFACTUAL = auto()     # What-if counterfactual scenarios
    EXPLORATORY = auto()        # Exploratory future scenarios
    NORMATIVE = auto()          # Desired future scenarios
    STRESS_TEST = auto()        # Stress testing scenarios

class UncertaintyType(Enum):
    """Types of uncertainty in scenario modeling."""

    ALEATORY = auto()           # Natural variability/randomness
    EPISTEMIC = auto()          # Knowledge/data uncertainty
    AMBIGUITY = auto()          # Multiple interpretations
    VOLATILITY = auto()         # High variability over time

@dataclass(frozen=True)
class TimeSlice:
    """Enhanced discrete period for snapshot-style SFM accounting."""

    label: str  # e.g. "FY2025" or "Q1-2030"
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    duration: Optional[timedelta] = None
    time_resolution: Optional[str] = None  # e.g., "annual", "quarterly", "monthly"

    def __post_init__(self):
        if self.start_date and self.end_date and not self.duration:
            object.__setattr__(self, 'duration', self.end_date - self.start_date)

@dataclass(frozen=True)
class SpatialUnit:
    """Enhanced hierarchical spatial identifier with geographic context."""

    code: str  # e.g. "US-WA-SEATTLE"
    name: str  # human-friendly display
    spatial_level: Optional[str] = None  # e.g., "nation", "state", "city"
    parent_unit: Optional[str] = None  # Parent spatial unit code
    geographic_bounds: Optional[Dict[str, float]] = None  # Lat/lon bounds
    population: Optional[int] = None
    area: Optional[float] = None  # Area in square kilometers

@dataclass
class Scenario(Node):
    """Enhanced scenario modeling for comprehensive SFM analysis."""

    scenario_type: Optional[ScenarioType] = None
    scenario_description: Optional[str] = None
    time_horizon: Optional[int] = None  # Time horizon in years

    # Scenario assumptions
    key_assumptions: List[str] = field(default_factory=list)
    driving_forces: List[str] = field(default_factory=list)
    external_conditions: Dict[str, Any] = field(default_factory=dict)
    policy_interventions: List[str] = field(default_factory=list)

    # Uncertainty characterization
    uncertainty_factors: Dict[str, UncertaintyType] = field(default_factory=dict)
    confidence_level: Optional[float] = None  # 0-1 scale
    sensitivity_factors: List[str] = field(default_factory=list)

    # Scenario variables
    variable_ranges: Dict[str, Tuple[float, float]] = field(default_factory=dict)
    probabilistic_variables: Dict[str, Dict[str, float]] = field(default_factory=dict)
    scenario_pathways: List[Dict[str, Any]] = field(default_factory=dict)

    # Cross-scenario relationships
    reference_scenarios: List[uuid.UUID] = field(default_factory=list)
    scenario_variants: List[uuid.UUID] = field(default_factory=list)
    scenario_combinations: List[uuid.UUID] = field(default_factory=list)

    # Scenario outcomes
    expected_outcomes: Dict[str, Any] = field(default_factory=dict)
    outcome_indicators: List[str] = field(default_factory=list)
    performance_metrics: Dict[str, float] = field(default_factory=dict)

    # Scenario validation
    plausibility_score: Optional[float] = None  # 0-1 scale
    internal_consistency: Optional[float] = None  # 0-1 scale
    stakeholder_acceptance: Dict[uuid.UUID, float] = field(default_factory=dict)

    # Implementation considerations
    implementation_feasibility: Optional[float] = None  # 0-1 scale
    resource_requirements: Dict[str, float] = field(default_factory=dict)
    implementation_barriers: List[str] = field(default_factory=list)
    enabling_conditions: List[str] = field(default_factory=list)

    # SFM integration
    matrix_scenario_effects: List[uuid.UUID] = field(default_factory=list)
    delivery_system_implications: List[uuid.UUID] = field(default_factory=list)
    institutional_scenario_requirements: List[uuid.UUID] = field(default_factory=list)

@dataclass
class ScenarioSet(Node):
    """Collection of related scenarios for comprehensive analysis."""

    set_name: Optional[str] = None
    set_purpose: Optional[str] = None
    scenarios: List[uuid.UUID] = field(default_factory=list)

    # Set characteristics
    scenario_count: Optional[int] = None
    coverage_completeness: Optional[float] = None  # 0-1 scale
    scenario_diversity: Optional[float] = None  # Diversity of scenarios

    # Set relationships
    baseline_scenario: Optional[uuid.UUID] = None
    comparison_matrix: Dict[Tuple[uuid.UUID, uuid.UUID], float] = field(default_factory=dict)
    scenario_clusters: List[List[uuid.UUID]] = field(default_factory=list)

    # Set analysis
    convergent_outcomes: List[str] = field(default_factory=list)
    divergent_outcomes: List[str] = field(default_factory=list)
    robust_strategies: List[str] = field(default_factory=list)

    # Decision support
    decision_criteria: List[str] = field(default_factory=list)
    preference_weights: Dict[str, float] = field(default_factory=dict)
    scenario_rankings: Dict[str, List[uuid.UUID]] = field(default_factory=dict)

    # SFM integration
    matrix_set_analysis: Optional[float] = None
    delivery_system_robustness: Optional[float] = None
    institutional_adaptability_assessment: Optional[float] = None

@dataclass
class ScenarioPath(Node):
    """Models dynamic paths/trajectories through scenarios over time."""

    path_name: Optional[str] = None
    path_description: Optional[str] = None

    # Path structure
    path_stages: List[Dict[str, Any]] = field(default_factory=list)
    transition_points: List[Dict[str, Any]] = field(default_factory=list)
    decision_nodes: List[Dict[str, Any]] = field(default_factory=list)

    # Path characteristics
    path_probability: Optional[float] = None  # 0-1 scale
    path_desirability: Optional[float] = None  # 0-1 scale
    path_feasibility: Optional[float] = None  # 0-1 scale

    # Path dependencies
    enabling_conditions: List[str] = field(default_factory=list)
    critical_decisions: List[str] = field(default_factory=list)
    path_dependencies: List[str] = field(default_factory=list)

    # Path outcomes
    cumulative_outcomes: Dict[str, Any] = field(default_factory=dict)
    endpoint_scenarios: List[uuid.UUID] = field(default_factory=list)
    path_impacts: Dict[str, float] = field(default_factory=dict)

    # Path monitoring
    path_indicators: List[str] = field(default_factory=list)
    milestone_markers: List[Dict[str, Any]] = field(default_factory=list)
    early_warning_signals: List[str] = field(default_factory=list)

    # SFM integration
    matrix_path_effects: List[uuid.UUID] = field(default_factory=list)
    delivery_path_implications: List[uuid.UUID] = field(default_factory=list)
    institutional_path_requirements: List[uuid.UUID] = field(default_factory=list)
