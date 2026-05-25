"""
Social assessment components for the Social Fabric Matrix framework.

This module contains classes for social value assessment, social fabric indicators,
social costs, and other social evaluation tools.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

from models.base_nodes import Node
from models.sfm_enums import (
    SocialFabricIndicatorType,
    SocialValueDimension,
    SocialCostType,
)


@dataclass
class SocialValueAssessment(Node):
    """Assessment of social value using Hayden's framework."""

    assessed_entity_id: Optional[uuid.UUID] = None  # What is being assessed - made optional for dataclass ordering
    life_process_impact: Optional[float] = None      # Impact on life processes
    community_continuity: Optional[float] = None     # Effect on community
    environmental_integration: Optional[float] = None # Environmental harmony
    cultural_development: Optional[float] = None     # Cultural advancement
    instrumental_efficiency: Optional[float] = None  # Problem-solving effectiveness

    ceremonial_elements: List[str] = field(default_factory=lambda: [])  # Status quo aspects
    instrumental_elements: List[str] = field(default_factory=lambda: [])  # Problem-solving aspects
    value_conflicts: List[str] = field(default_factory=lambda: [])     # Conflicting values
    assessment_methodology: str = "holistic"
    social_value_dimensions: List[SocialValueDimension] = field(default_factory=lambda: [])
    stakeholder_perspectives: Dict[str, float] = field(default_factory=lambda: {})  # Different stakeholder views

    def __post_init__(self) -> None:
        """Validate that assessed entity is provided."""
        if self.assessed_entity_id is None:
            raise ValueError("assessed_entity_id is required for SocialValueAssessment")


@dataclass
class SocialFabricIndicator(Node):
    """Specialized indicator for measuring social fabric health per Hayden's framework."""

    indicator_type: SocialFabricIndicatorType = SocialFabricIndicatorType.INSTITUTIONAL_COHERENCE
    current_value: Optional[float] = None  # Current measured value
    baseline_value: Optional[float] = None  # Historical baseline for comparison
    target_threshold: Optional[float] = None  # Desired threshold value
    warning_threshold: Optional[float] = None  # Warning level threshold

    # SFM-specific properties
    affected_institutions: List[uuid.UUID] = field(default_factory=lambda: [])  # Institutions measured
    measurement_methodology: str = "qualitative_assessment"
    stakeholder_perspectives: Dict[str, float] = field(default_factory=lambda: {})  # Different viewpoints

    # Integration with matrix
    related_matrix_cells: List[uuid.UUID] = field(default_factory=lambda: [])  # Relevant matrix cells
    normative_framework: Optional[str] = None  # Evaluation framework
    ceremonial_biases: List[str] = field(default_factory=lambda: [])  # Potential ceremonial distortions

    # Trend analysis
    trend_direction: Optional[str] = None  # "improving", "declining", "stable"
    trend_strength: Optional[float] = None  # Strength of trend (0-1)
    intervention_responsiveness: Optional[float] = None  # How responsive to interventions (0-1)

    def assess_fabric_health(self) -> Dict[str, Any]:
        """Comprehensive assessment of social fabric health."""
        assessment: Dict[str, Any] = {
            "overall_health": "unknown",
            "trend": self.trend_direction or "unknown",
            "stakeholder_consensus": 0.0,
            "intervention_urgency": 0.0
        }

        # Determine overall health
        if self.current_value is not None:
            if self.warning_threshold and self.current_value < self.warning_threshold:
                assessment["overall_health"] = "poor"
                assessment["intervention_urgency"] = 0.8
            elif self.target_threshold and self.current_value >= self.target_threshold:
                assessment["overall_health"] = "good"
                assessment["intervention_urgency"] = 0.2
            else:
                assessment["overall_health"] = "moderate"
                assessment["intervention_urgency"] = 0.5

        # Calculate stakeholder consensus
        if self.stakeholder_perspectives:
            values = list(self.stakeholder_perspectives.values())
            if values:
                mean_val = sum(values) / len(values)
                variance = sum((v - mean_val) ** 2 for v in values) / len(values)
                assessment["stakeholder_consensus"] = max(0.0, 1.0 - variance)

        return assessment


@dataclass
class SocialCost(Node):
    """Represents social costs per Kapp's theory integrated with Hayden's SFM."""

    cost_type: SocialCostType = SocialCostType.ENVIRONMENTAL_DEGRADATION
    estimated_cost: Optional[float] = None  # Monetary estimate if possible
    cost_unit: Optional[str] = None  # Unit of measurement

    # Cost characteristics
    cost_bearers: List[uuid.UUID] = field(default_factory=lambda: [])  # Who bears the cost
    cost_creators: List[uuid.UUID] = field(default_factory=lambda: [])  # Who creates the cost
    externalization_mechanism: Optional[str] = None  # How cost is externalized

    # Temporal aspects
    cost_trajectory: Optional[str] = None  # "increasing", "decreasing", "stable"
    cumulative_effect: Optional[float] = None  # Cumulative impact over time
    irreversibility_risk: Optional[float] = None  # Risk of irreversible damage (0-1)

    # SFM integration
    institutional_causes: List[uuid.UUID] = field(default_factory=lambda: [])  # Institutions causing costs
    ceremonial_amplifiers: List[str] = field(default_factory=lambda: [])  # Ceremonial factors that amplify costs
    instrumental_mitigation: List[str] = field(default_factory=lambda: [])  # Instrumental approaches to reduce costs
    matrix_cell_impacts: List[uuid.UUID] = field(default_factory=lambda: [])  # Matrix cells affected by costs

    # Policy relevance
    internalization_strategies: List[str] = field(default_factory=lambda: [])  # Ways to internalize costs
    regulatory_gaps: List[str] = field(default_factory=lambda: [])  # Regulatory failures
    collective_action_potential: Optional[float] = None  # Potential for collective action (0-1)

    def assess_cost_severity(self) -> Dict[str, Any]:
        """Assess severity and urgency of social cost."""
        severity_assessment: Dict[str, Any] = {
            "economic_magnitude": "unknown",
            "social_impact": "unknown",
            "urgency_level": "unknown",
            "intervention_feasibility": "unknown"
        }

        # Assess economic magnitude
        if self.estimated_cost is not None:
            # This would need contextual thresholds for proper assessment
            if self.estimated_cost > 1000000:  # Placeholder threshold
                severity_assessment["economic_magnitude"] = "high"
            elif self.estimated_cost > 100000:
                severity_assessment["economic_magnitude"] = "moderate"
            else:
                severity_assessment["economic_magnitude"] = "low"

        # Assess social impact based on number of cost bearers
        bearer_count = len(self.cost_bearers)
        if bearer_count > 10:
            severity_assessment["social_impact"] = "widespread"
        elif bearer_count > 3:
            severity_assessment["social_impact"] = "moderate"
        else:
            severity_assessment["social_impact"] = "limited"

        # Assess urgency based on irreversibility and trajectory
        urgency_factors = 0
        if self.irreversibility_risk and self.irreversibility_risk > 0.7:
            urgency_factors += 2
        if self.cost_trajectory == "increasing":
            urgency_factors += 1

        if urgency_factors >= 2:
            severity_assessment["urgency_level"] = "high"
        elif urgency_factors >= 1:
            severity_assessment["urgency_level"] = "moderate"
        else:
            severity_assessment["urgency_level"] = "low"

        # Assess intervention feasibility
        mitigation_strategies = len(self.instrumental_mitigation) + len(self.internalization_strategies)
        if mitigation_strategies >= 3:
            severity_assessment["intervention_feasibility"] = "feasible"
        elif mitigation_strategies >= 1:
            severity_assessment["intervention_feasibility"] = "challenging"
        else:
            severity_assessment["intervention_feasibility"] = "difficult"

        return severity_assessment
