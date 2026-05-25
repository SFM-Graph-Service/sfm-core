"""
Cultural analysis components for the Social Fabric Matrix framework.

This module contains classes for analyzing ceremonial vs instrumental patterns,
value systems, beliefs, attitudes, and cultural aspects of institutions.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from models.base_nodes import Node
from models.sfm_enums import (
    CeremonialInstrumentalType,
    ValueSystemType,
)


@dataclass
class CeremonialInstrumentalClassification(Node):
    """Classifies behaviors/institutions as ceremonial vs instrumental."""

    classification: CeremonialInstrumentalType = CeremonialInstrumentalType.MIXED
    ceremonial_score: Optional[float] = None  # 0-1, higher = more ceremonial
    instrumental_score: Optional[float] = None  # 0-1, higher = more instrumental
    change_resistance: Optional[float] = None  # Resistance to adaptive change (0-1)
    problem_solving_contribution: Optional[float] = None  # Contribution to problem solving (0-1)
    status_quo_reinforcement: Optional[float] = None  # Reinforces existing patterns (0-1)
    adaptive_potential: Optional[float] = None  # Capacity for change (0-1)
    supporting_evidence: List[str] = field(default_factory=lambda: [])
    classification_rationale: Optional[str] = None
    temporal_dynamics: Optional[str] = None


@dataclass
class ValueSystem(Node):
    """Represents cultural value systems in Hayden's framework."""

    system_type: ValueSystemType = ValueSystemType.CULTURAL_DOMINANT
    core_values: List[str] = field(default_factory=lambda: [])  # Primary values in this system
    value_hierarchy: Dict[str, float] = field(default_factory=lambda: {})  # Value priorities (0-1)
    cultural_embedding: Optional[float] = None  # How deeply embedded (0-1)
    transmission_mechanisms: List[str] = field(default_factory=lambda: [])  # How values are transmitted

    # SFM-specific properties
    ceremonial_elements: List[str] = field(default_factory=lambda: [])  # Status quo reinforcing aspects
    instrumental_elements: List[str] = field(default_factory=lambda: [])  # Problem-solving aspects
    value_conflicts: List[uuid.UUID] = field(default_factory=lambda: [])  # Conflicting value systems
    institutional_support: List[uuid.UUID] = field(default_factory=lambda: [])  # Supporting institutions
    change_resistance: Optional[float] = None  # Resistance to value change (0-1)
    adaptive_capacity: Optional[float] = None  # Capacity for value evolution (0-1)

    # Integration with matrix
    influenced_matrix_cells: List[uuid.UUID] = field(default_factory=lambda: [])  # Matrix cells influenced
    legitimacy_source: Optional[str] = None  # What legitimizes this value system
    stakeholder_alignment: Dict[str, float] = field(default_factory=lambda: {})  # Stakeholder agreement

    def calculate_coherence_score(self) -> float:
        """Calculate internal coherence of value system."""
        if not self.value_hierarchy:
            return 0.0

        # More balanced hierarchy = higher coherence
        values = list(self.value_hierarchy.values())
        if not values:
            return 0.0

        # Calculate variance - lower variance = higher coherence
        mean_val = sum(values) / len(values)
        variance = sum((v - mean_val) ** 2 for v in values) / len(values)
        return max(0.0, 1.0 - variance)  # Inverse relationship

    def assess_institutional_alignment(self) -> float:
        """Assess alignment between values and supporting institutions."""
        if not self.institutional_support:
            return 0.0

        # More institutional support = better alignment
        support_count = len(self.institutional_support)
        return min(1.0, support_count * 0.2)  # Cap at 1.0


@dataclass
class SocialBelief(Node):
    """Social beliefs distinct from values and attitudes - core to Hayden's cultural analysis."""

    belief_type: Optional[str] = None  # "factual", "normative", "existential", etc.
    belief_strength: Optional[float] = None  # Strength of belief (0-1)
    cultural_domain: Optional[str] = None  # Domain where belief operates
    legitimacy_source: Optional[str] = None  # Source of belief legitimacy

    # Belief relationships
    supporting_values: List[uuid.UUID] = field(default_factory=lambda: [])  # Values that support this belief
    conflicting_beliefs: List[uuid.UUID] = field(default_factory=lambda: [])  # Contradictory beliefs
    institutional_embedment: List[uuid.UUID] = field(default_factory=lambda: [])  # Institutions embedding this belief

    # Belief characteristics
    evidence_basis: List[str] = field(default_factory=lambda: [])  # Evidence supporting belief
    cultural_transmission: Optional[str] = None  # How belief is transmitted
    change_resistance: Optional[float] = None  # Resistance to change (0-1)
    social_reinforcement: Optional[float] = None  # Social reinforcement level (0-1)

    # Matrix integration
    institutional_influence: Dict[uuid.UUID, float] = field(default_factory=lambda: {})  # Institution -> influence level
    attitude_mediation_effects: Dict[uuid.UUID, float] = field(default_factory=lambda: {})  # Attitude -> mediation effect
    belief_coherence_score: Optional[float] = None  # Internal coherence (0-1)

    def assess_belief_stability(self) -> Dict[str, Any]:
        """Assess stability and change potential of belief."""
        stability_assessment: Dict[str, Any] = {
            "stability_level": "unknown",
            "change_potential": 0.0,
            "reinforcement_factors": len(self.supporting_values),
            "challenge_factors": len(self.conflicting_beliefs)
        }

        if self.change_resistance is not None and self.social_reinforcement is not None:
            stability_score = (self.change_resistance + self.social_reinforcement) / 2
            if stability_score >= 0.7:
                stability_assessment["stability_level"] = "high"
            elif stability_score >= 0.4:
                stability_assessment["stability_level"] = "moderate"
            else:
                stability_assessment["stability_level"] = "low"

            stability_assessment["change_potential"] = 1.0 - stability_score

        return stability_assessment


@dataclass
class CulturalAttitude(Node):
    """Attitudes that mediate between beliefs and institutions - Hayden's cultural framework."""

    attitude_type: Optional[str] = None  # "supportive", "resistant", "neutral", etc.
    attitude_strength: Optional[float] = None  # Strength of attitude (0-1)
    emotional_component: Optional[float] = None  # Emotional intensity (0-1)
    behavioral_tendency: Optional[str] = None  # Behavioral predisposition

    # Attitude relationships
    related_beliefs: List[uuid.UUID] = field(default_factory=lambda: [])  # Beliefs this attitude relates to
    influenced_institutions: List[uuid.UUID] = field(default_factory=lambda: [])  # Institutions influenced by attitude
    attitude_objects: List[uuid.UUID] = field(default_factory=lambda: [])  # Objects of the attitude

    # Attitude characteristics
    formation_context: Optional[str] = None  # Context where attitude formed
    stability_factors: List[str] = field(default_factory=lambda: [])  # Factors supporting attitude stability
    change_triggers: List[str] = field(default_factory=lambda: [])  # Potential change triggers
    social_desirability: Optional[float] = None  # Social acceptability (0-1)

    # Matrix integration
    institutional_mediation_effects: Dict[uuid.UUID, float] = field(default_factory=lambda: {})  # Institution -> mediation
    belief_attitude_coherence: Optional[float] = None  # Coherence with beliefs (0-1)
    behavioral_predictability: Optional[float] = None  # Predictability of behavior (0-1)

    def analyze_mediation_capacity(self) -> Dict[str, Any]:
        """Analyze attitude's capacity to mediate between beliefs and institutions."""
        mediation_analysis: Dict[str, Any] = {
            "mediation_strength": 0.0,
            "coherence_level": "unknown",
            "influence_scope": len(self.influenced_institutions),
            "stability_rating": "unknown"
        }

        # Calculate mediation strength
        if self.attitude_strength is not None and self.behavioral_predictability is not None:
            mediation_analysis["mediation_strength"] = (self.attitude_strength + self.behavioral_predictability) / 2

        # Assess coherence
        if self.belief_attitude_coherence is not None:
            if self.belief_attitude_coherence >= 0.7:
                mediation_analysis["coherence_level"] = "high"
            elif self.belief_attitude_coherence >= 0.4:
                mediation_analysis["coherence_level"] = "moderate"
            else:
                mediation_analysis["coherence_level"] = "low"

        # Assess stability
        stability_score = len(self.stability_factors) / max(1, len(self.change_triggers))
        if stability_score >= 2.0:
            mediation_analysis["stability_rating"] = "high"
        elif stability_score >= 1.0:
            mediation_analysis["stability_rating"] = "moderate"
        else:
            mediation_analysis["stability_rating"] = "low"

        return mediation_analysis