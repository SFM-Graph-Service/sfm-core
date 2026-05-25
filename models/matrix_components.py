"""
Core matrix components for the Social Fabric Matrix framework.

This module contains the fundamental building blocks of the SFM matrix including
matrix cells, criteria, and complete matrix configurations.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any

from models.base_nodes import Node
from models.sfm_enums import (
    CorrelationType,
    CorrelationScale,
    EvidenceQuality,
    CriteriaType,
    CriteriaPriority,
    MeasurementApproach,
)


@dataclass
class MatrixCell(Node):  # pylint: disable=too-many-instance-attributes
    """Represents a cell in the Social Fabric Matrix showing institution-criteria relationship with enhanced SFM integration."""  # pylint: disable=line-too-long

    institution_id: Optional[uuid.UUID] = None  # Made optional with default to fix dataclass ordering  # pylint: disable=line-too-long
    criteria_id: Optional[uuid.UUID] = None     # Made optional with default to fix dataclass ordering  # pylint: disable=line-too-long
    correlation_type: CorrelationType = CorrelationType.UNKNOWN
    correlation_strength: Optional[float] = None  # 0-1 scale
    correlation_scale: CorrelationScale = CorrelationScale.NEUTRAL  # Hayden's standardized -3 to +3 scale
    evidence_quality: EvidenceQuality = EvidenceQuality.LOW
    justification: Optional[str] = None
    data_sources: List[str] = field(default_factory=lambda: [])
    confidence_level: Optional[float] = None  # 0-1 scale
    last_updated: datetime = field(default_factory=datetime.now)
    reviewed_by: Optional[str] = None
    review_date: Optional[datetime] = None

    # Enhanced SFM Integration - Delivery System Modeling
    deliveries_provided: List[Dict[str, Any]] = field(default_factory=lambda: [])  # What this cell delivers to others
    deliveries_received: List[Dict[str, Any]] = field(default_factory=lambda: [])  # What this cell receives from others
    delivery_quality: Optional[float] = None  # Quality of deliveries (0-1)
    delivery_reliability: Optional[float] = None  # Reliability of deliveries (0-1)
    delivery_capacity: Optional[float] = None  # Capacity for deliveries (0-1)

    # Cultural Integration - Hayden's cultural values/beliefs/attitudes framework
    cultural_values_influence: Dict[str, float] = field(default_factory=lambda: {})  # Value type -> influence strength
    social_beliefs_alignment: Dict[str, float] = field(default_factory=lambda: {})  # Belief type -> alignment level
    attitude_mediation: Dict[str, float] = field(default_factory=lambda: {})  # Attitude type -> mediation effect
    cultural_legitimacy: Optional[float] = None  # Cultural legitimacy of the relationship (0-1)

    # Ceremonial vs Instrumental Analysis
    ceremonial_component: Optional[float] = None  # Ceremonial aspects of the relationship (0-1)
    instrumental_component: Optional[float] = None  # Instrumental aspects of the relationship (0-1)
    ceremonial_barriers: List[str] = field(default_factory=lambda: [])  # Ceremonial obstacles
    instrumental_enablers: List[str] = field(default_factory=lambda: [])  # Instrumental facilitators

    # Technology Integration
    technology_dependencies: List[uuid.UUID] = field(default_factory=lambda: [])  # Required technologies
    technology_compatibility: Optional[float] = None  # How well technology supports relationship (0-1)
    technological_change_sensitivity: Optional[float] = None  # Sensitivity to tech changes (0-1)

    # Ecological System Integration
    ecological_constraints: List[str] = field(default_factory=lambda: [])  # Environmental constraints
    ecological_impact: Optional[float] = None  # Environmental impact (-1 to +1)
    ecological_sustainability: Optional[float] = None  # Sustainability rating (0-1)
    resource_flows: Dict[str, float] = field(default_factory=lambda: {})  # Resource type -> flow amount

    # Network Process Integration
    network_position: Optional[str] = None  # Position in network ("central", "peripheral", "bridge")
    network_influence: Optional[float] = None  # Influence within network (0-1)
    feedback_loops: List[Dict[str, Any]] = field(default_factory=lambda: [])  # Feedback relationships
    system_criticality: Optional[float] = None  # Criticality to overall system (0-1)

    # Social Indicator Integration
    social_indicators: Dict[str, float] = field(default_factory=lambda: {})  # Indicator type -> value
    indicator_trends: Dict[str, str] = field(default_factory=lambda: {})  # Indicator -> trend direction
    monitoring_frequency: Optional[str] = None  # How often indicators are updated

    # Temporal Sequencing
    temporal_sequence_position: Optional[int] = None  # Position in temporal sequence
    sequence_dependencies: List[uuid.UUID] = field(default_factory=lambda: [])  # Dependent cells in sequence
    temporal_coordination_requirements: List[str] = field(default_factory=lambda: [])  # Timing requirements

    def __post_init__(self) -> None:
        """Validate that required fields are provided."""
        if self.institution_id is None:
            raise ValueError("institution_id is required for MatrixCell")
        if self.criteria_id is None:
            raise ValueError("criteria_id is required for MatrixCell")

    def calculate_weighted_score(self, criteria_weight: float) -> Optional[float]:
        """Calculate weighted contribution to overall matrix score."""
        if self.correlation_strength is None:
            return None

        multiplier = 1.0 if self.correlation_type == CorrelationType.POSITIVE else -1.0
        if self.correlation_type == CorrelationType.NEUTRAL:
            multiplier = 0.0
        elif self.correlation_type == CorrelationType.UNKNOWN:
            multiplier = 0.0  # Unknown treated as neutral for scoring

        return self.correlation_strength * multiplier * criteria_weight

    def get_confidence_adjusted_score(self) -> Optional[float]:
        """Get score adjusted for confidence level."""
        if self.correlation_strength is None or self.confidence_level is None:
            return None
        return self.correlation_strength * self.confidence_level

    def get_evidence_weighted_score(self) -> Optional[float]:
        """Get score weighted by evidence quality."""
        if self.correlation_strength is None:
            return None

        # Weight evidence quality: LOW=0.5, MEDIUM=0.7, HIGH=0.9, VERIFIED=1.0
        evidence_weights = {
            EvidenceQuality.LOW: 0.5,
            EvidenceQuality.MEDIUM: 0.7,
            EvidenceQuality.HIGH: 0.9,
            EvidenceQuality.VERIFIED: 1.0
        }

        evidence_weight = evidence_weights.get(self.evidence_quality, 0.5)
        return self.correlation_strength * evidence_weight

    def get_standardized_correlation_value(self) -> float:
        """Convert correlation scale to standardized numeric value (-3 to +3)."""
        scale_values = {
            CorrelationScale.STRONGLY_NEGATIVE: -3.0,
            CorrelationScale.MODERATELY_NEGATIVE: -2.0,
            CorrelationScale.WEAKLY_NEGATIVE: -1.0,
            CorrelationScale.NEUTRAL: 0.0,
            CorrelationScale.WEAKLY_POSITIVE: 1.0,
            CorrelationScale.MODERATELY_POSITIVE: 2.0,
            CorrelationScale.STRONGLY_POSITIVE: 3.0
        }
        return scale_values.get(self.correlation_scale, 0.0)

    def set_correlation_from_numeric(self, value: float) -> None:
        """Set correlation scale from numeric value (-3 to +3)."""
        if value <= -2.5:
            self.correlation_scale = CorrelationScale.STRONGLY_NEGATIVE
        elif value <= -1.5:
            self.correlation_scale = CorrelationScale.MODERATELY_NEGATIVE
        elif value <= -0.5:
            self.correlation_scale = CorrelationScale.WEAKLY_NEGATIVE
        elif value <= 0.5:
            self.correlation_scale = CorrelationScale.NEUTRAL
        elif value <= 1.5:
            self.correlation_scale = CorrelationScale.WEAKLY_POSITIVE
        elif value <= 2.5:
            self.correlation_scale = CorrelationScale.MODERATELY_POSITIVE
        else:
            self.correlation_scale = CorrelationScale.STRONGLY_POSITIVE

    def assess_cell_quality(self) -> Dict[str, Any]:
        """Comprehensive assessment of matrix cell quality."""
        assessment: Dict[str, Any] = {
            "data_quality": "unknown",
            "confidence": "medium",
            "completeness": "partial",
            "consistency": "consistent",
            "review_status": "needs_review"
        }

        # Assess data quality
        if len(self.data_sources) >= 3 and self.evidence_quality in [EvidenceQuality.HIGH, EvidenceQuality.VERIFIED]:
            assessment["data_quality"] = "high"
        elif len(self.data_sources) >= 2 and self.evidence_quality == EvidenceQuality.MEDIUM:
            assessment["data_quality"] = "moderate"
        else:
            assessment["data_quality"] = "low"

        # Assess confidence
        if self.confidence_level:
            if self.confidence_level >= 0.8:
                assessment["confidence"] = "high"
            elif self.confidence_level >= 0.6:
                assessment["confidence"] = "medium"
            else:
                assessment["confidence"] = "low"

        # Assess completeness
        required_fields: list[Optional[Any]] = [self.institution_id, self.criteria_id, self.justification]
        completed_fields = sum(1 for field in required_fields if field is not None)
        if completed_fields == len(required_fields):
            assessment["completeness"] = "complete"
        elif completed_fields >= len(required_fields) // 2:
            assessment["completeness"] = "partial"
        else:
            assessment["completeness"] = "incomplete"

        # Check consistency between correlation measures
        if self.correlation_strength is not None:
            numeric_correlation = self.get_standardized_correlation_value()
            expected_strength = abs(numeric_correlation) / 3.0  # Normalize to 0-1

            if abs(self.correlation_strength - expected_strength) > 0.3:
                assessment["consistency"] = "inconsistent"

        # Check review status
        if self.reviewed_by and self.review_date:
            assessment["review_status"] = "reviewed"

        return assessment

    def analyze_delivery_relationships(self) -> Dict[str, Any]:
        """Analyze delivery relationships for this matrix cell - core to Hayden's SFM."""
        delivery_analysis: Dict[str, Any] = {
            "deliveries_provided_count": len(self.deliveries_provided),
            "deliveries_received_count": len(self.deliveries_received),
            "delivery_balance": "unknown",
            "delivery_effectiveness": 0.0,
            "delivery_criticality": 0.0
        }

        # Assess delivery balance
        provided = len(self.deliveries_provided)
        received = len(self.deliveries_received)
        if provided > received * 1.5:
            delivery_analysis["delivery_balance"] = "net_provider"
        elif received > provided * 1.5:
            delivery_analysis["delivery_balance"] = "net_receiver"
        else:
            delivery_analysis["delivery_balance"] = "balanced"

        # Calculate delivery effectiveness
        if self.delivery_quality and self.delivery_reliability:
            delivery_analysis["delivery_effectiveness"] = (self.delivery_quality + self.delivery_reliability) / 2

        # Assess criticality based on system criticality and network influence
        if self.system_criticality and self.network_influence:
            delivery_analysis["delivery_criticality"] = (self.system_criticality + self.network_influence) / 2

        return delivery_analysis

    def assess_cultural_integration(self) -> Dict[str, Any]:
        """Assess cultural integration aspects - Hayden's values/beliefs/attitudes framework."""
        cultural_assessment: Dict[str, Any] = {
            "cultural_values_count": len(self.cultural_values_influence),
            "social_beliefs_count": len(self.social_beliefs_alignment),
            "attitude_mediation_count": len(self.attitude_mediation),
            "cultural_coherence": 0.0,
            "cultural_legitimacy_level": "unknown"
        }

        # Calculate cultural coherence (alignment between values, beliefs, attitudes)
        total_cultural_elements = (
            len(self.cultural_values_influence) +
            len(self.social_beliefs_alignment) +
            len(self.attitude_mediation)
        )

        if total_cultural_elements > 0:
            values_avg = sum(self.cultural_values_influence.values()) / len(self.cultural_values_influence) if self.cultural_values_influence else 0
            beliefs_avg = sum(self.social_beliefs_alignment.values()) / len(self.social_beliefs_alignment) if self.social_beliefs_alignment else 0
            attitudes_avg = sum(self.attitude_mediation.values()) / len(self.attitude_mediation) if self.attitude_mediation else 0

            # Coherence is inversely related to variance
            cultural_scores = [values_avg, beliefs_avg, attitudes_avg]
            if len([s for s in cultural_scores if s > 0]) > 1:
                variance = sum((s - sum(cultural_scores)/3)**2 for s in cultural_scores) / len(cultural_scores)
                cultural_assessment["cultural_coherence"] = max(0.0, 1.0 - variance)

        # Assess cultural legitimacy level
        if self.cultural_legitimacy:
            if self.cultural_legitimacy >= 0.8:
                cultural_assessment["cultural_legitimacy_level"] = "high"
            elif self.cultural_legitimacy >= 0.6:
                cultural_assessment["cultural_legitimacy_level"] = "moderate"
            else:
                cultural_assessment["cultural_legitimacy_level"] = "low"

        return cultural_assessment

    def analyze_ceremonial_instrumental_balance(self) -> Dict[str, Any]:
        """Analyze ceremonial vs instrumental balance - central to Hayden's framework."""
        balance_analysis: Dict[str, Any] = {
            "ceremonial_score": self.ceremonial_component or 0.0,
            "instrumental_score": self.instrumental_component or 0.0,
            "balance_type": "unknown",
            "dominant_aspect": "unknown",
            "barriers_count": len(self.ceremonial_barriers),
            "enablers_count": len(self.instrumental_enablers),
            "adjustment_recommendations": []
        }

        # Determine balance type
        ceremonial = self.ceremonial_component or 0.0
        instrumental = self.instrumental_component or 0.0

        if ceremonial > instrumental * 1.5:
            balance_analysis["balance_type"] = "ceremonial_dominated"
            balance_analysis["dominant_aspect"] = "ceremonial"
            balance_analysis["adjustment_recommendations"].append("Increase instrumental problem-solving capacity")
        elif instrumental > ceremonial * 1.5:
            balance_analysis["balance_type"] = "instrumental_dominated"
            balance_analysis["dominant_aspect"] = "instrumental"
            balance_analysis["adjustment_recommendations"].append("Consider ceremonial stabilization needs")
        else:
            balance_analysis["balance_type"] = "balanced"
            balance_analysis["dominant_aspect"] = "balanced"

        # Assess barriers vs enablers
        if len(self.ceremonial_barriers) > len(self.instrumental_enablers):
            balance_analysis["adjustment_recommendations"].append("Address ceremonial barriers")
        elif len(self.instrumental_enablers) > len(self.ceremonial_barriers):
            balance_analysis["adjustment_recommendations"].append("Leverage instrumental enablers")

        return balance_analysis

    def assess_ecological_integration(self) -> Dict[str, Any]:
        """Assess ecological system integration - part of Hayden's comprehensive approach."""
        ecological_assessment: Dict[str, Any] = {
            "ecological_constraints_count": len(self.ecological_constraints),
            "ecological_impact_level": "unknown",
            "sustainability_rating": "unknown",
            "resource_flows_count": len(self.resource_flows),
            "environmental_health": 0.0
        }

        # Assess ecological impact level
        if self.ecological_impact is not None:
            if self.ecological_impact >= 0.5:
                ecological_assessment["ecological_impact_level"] = "positive"
            elif self.ecological_impact <= -0.5:
                ecological_assessment["ecological_impact_level"] = "negative"
            else:
                ecological_assessment["ecological_impact_level"] = "neutral"

        # Assess sustainability rating
        if self.ecological_sustainability is not None:
            if self.ecological_sustainability >= 0.8:
                ecological_assessment["sustainability_rating"] = "high"
            elif self.ecological_sustainability >= 0.6:
                ecological_assessment["sustainability_rating"] = "moderate"
            else:
                ecological_assessment["sustainability_rating"] = "low"

        # Calculate environmental health score
        if self.ecological_impact is not None and self.ecological_sustainability is not None:
            # Weight sustainability higher than impact
            ecological_assessment["environmental_health"] = (
                self.ecological_sustainability * 0.7 +
                max(0, self.ecological_impact) * 0.3
            )

        return ecological_assessment

    def analyze_social_indicators(self) -> Dict[str, Any]:
        """Analyze social indicators - key to Hayden's methodology."""
        indicator_analysis: Dict[str, Any] = {
            "indicators_count": len(self.social_indicators),
            "trending_indicators": {"improving": [], "declining": [], "stable": []},
            "indicator_coverage": "unknown",
            "monitoring_adequacy": "unknown"
        }

        # Categorize trends
        for indicator, trend in self.indicator_trends.items():
            if trend in ["improving", "increasing", "positive"]:
                indicator_analysis["trending_indicators"]["improving"].append(indicator)
            elif trend in ["declining", "decreasing", "negative"]:
                indicator_analysis["trending_indicators"]["declining"].append(indicator)
            else:
                indicator_analysis["trending_indicators"]["stable"].append(indicator)

        # Assess indicator coverage
        if len(self.social_indicators) >= 5:
            indicator_analysis["indicator_coverage"] = "comprehensive"
        elif len(self.social_indicators) >= 3:
            indicator_analysis["indicator_coverage"] = "adequate"
        else:
            indicator_analysis["indicator_coverage"] = "limited"

        # Assess monitoring adequacy
        if self.monitoring_frequency in ["daily", "weekly", "monthly"]:
            indicator_analysis["monitoring_adequacy"] = "adequate"
        else:
            indicator_analysis["monitoring_adequacy"] = "insufficient"

        return indicator_analysis


@dataclass
class SFMCriteria(Node):  # pylint: disable=too-many-instance-attributes
    """Evaluation criteria used in the Social Fabric Matrix with Hayden's priority system."""

    criteria_type: CriteriaType = CriteriaType.SOCIAL
    measurement_approach: MeasurementApproach = MeasurementApproach.QUALITATIVE
    priority: CriteriaPriority = CriteriaPriority.SECONDARY  # Hayden's primary/secondary distinction
    weight: Optional[float] = None  # Relative importance (0-1)
    sub_criteria: List[uuid.UUID] = field(default_factory=lambda: [])
    evaluation_method: Optional[str] = None
    data_requirements: List[str] = field(default_factory=lambda: [])
    measurement_frequency: Optional[str] = None
    responsible_party: Optional[str] = None

    # Hayden's priority system integration
    life_process_relevance: Optional[float] = None  # Relevance to life process enhancement (0-1)
    instrumental_capacity: Optional[float] = None  # Problem-solving capacity measure (0-1)
    ceremonial_bias_risk: Optional[float] = None  # Risk of ceremonial distortion (0-1)
    normative_justification: Optional[str] = None  # Why this criterion matters normatively

    def calculate_hayden_priority_score(self) -> float:
        """Calculate priority score using Hayden's framework."""
        if self.priority == CriteriaPriority.PRIMARY:
            base_score = 1.0
        elif self.priority == CriteriaPriority.SECONDARY:
            base_score = 0.7
        else:  # TERTIARY
            base_score = 0.4

        # Adjust based on life process relevance
        if self.life_process_relevance is not None:
            base_score *= (0.5 + 0.5 * self.life_process_relevance)

        # Penalize for ceremonial bias risk
        if self.ceremonial_bias_risk is not None:
            base_score *= (1.0 - 0.3 * self.ceremonial_bias_risk)

        return max(0.0, min(1.0, base_score))

    def assess_criterion_quality(self) -> Dict[str, Any]:
        """Assess the quality and appropriateness of this criterion."""
        assessment: Dict[str, Any] = {
            "priority_appropriateness": "appropriate",
            "measurement_feasibility": "feasible",
            "normative_strength": "moderate",
            "bias_risk": "low"
        }

        # Check priority appropriateness
        if self.priority == CriteriaPriority.PRIMARY and (self.life_process_relevance or 0) < 0.5:
            assessment["priority_appropriateness"] = "questionable"

        # Check measurement feasibility
        if self.measurement_approach == MeasurementApproach.QUANTITATIVE and not self.data_requirements:
            assessment["measurement_feasibility"] = "difficult"

        # Check normative strength
        if self.normative_justification:
            assessment["normative_strength"] = "strong"
        elif not self.normative_justification and self.priority == CriteriaPriority.PRIMARY:
            assessment["normative_strength"] = "weak"

        # Check bias risk
        if self.ceremonial_bias_risk and self.ceremonial_bias_risk > 0.7:
            assessment["bias_risk"] = "high"
        elif self.ceremonial_bias_risk and self.ceremonial_bias_risk > 0.3:
            assessment["bias_risk"] = "moderate"

        return assessment


@dataclass
class SFMMatrix(Node):  # pylint: disable=too-many-instance-attributes
    """Represents a complete Social Fabric Matrix configuration."""

    institutions: List[uuid.UUID] = field(default_factory=lambda: [])  # Row headers
    criteria: List[uuid.UUID] = field(default_factory=lambda: [])  # Column headers
    matrix_cells: List[uuid.UUID] = field(default_factory=lambda: [])  # All cells in matrix
    matrix_purpose: str = "General institutional analysis"
    analysis_context: Optional[uuid.UUID] = None  # Link to AnalyticalContext
    completeness_score: Optional[float] = None  # How complete is the matrix (0-1)
    consistency_score: Optional[float] = None  # Internal consistency (0-1)
    last_validation: Optional[datetime] = None
    validation_results: Dict[str, Any] = field(default_factory=lambda: {})
    digraph_analysis: Optional[uuid.UUID] = None  # Link to DigraphAnalysis
    cross_impact_analyses: List[uuid.UUID] = field(default_factory=lambda: [])  # Links to CrossImpactAnalysis
    problem_solving_sequences: List[uuid.UUID] = field(default_factory=lambda: [])  # Related problem-solving
    matrix_version: int = 1  # Version number for tracking changes
    sensitivity_analysis: Dict[str, Any] = field(default_factory=lambda: {})  # Sensitivity analysis results
