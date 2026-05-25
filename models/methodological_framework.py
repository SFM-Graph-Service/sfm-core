"""
Methodological framework components for the Social Fabric Matrix.

This module contains classes for instrumentalist inquiry, normative analysis,
policy integration, and other methodological tools that support SFM analysis.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

from models.base_nodes import Node
from models.sfm_enums import NormativeFramework


@dataclass
class InstrumentalistInquiryFramework(Node):
    """Represents Hayden's instrumentalist approach to inquiry - methodological foundation of SFM."""

    inquiry_purpose: Optional[str] = None  # Purpose of the inquiry
    problem_context: Optional[str] = None  # Context of the problem being investigated
    normative_orientation: Optional[str] = None  # Normative stance of the inquiry
    embedded_values: List[str] = field(default_factory=lambda: [])  # Values embedded in the inquiry

    # Instrumentalist characteristics
    problem_solving_focus: Optional[float] = None  # Focus on problem-solving (0-1)
    contextual_sensitivity: Optional[float] = None  # Sensitivity to context (0-1)
    evolutionary_perspective: Optional[float] = None  # Evolutionary approach level (0-1)
    holistic_approach: Optional[float] = None  # Holistic thinking level (0-1)

    # Inquiry process
    inquiry_stages: List[Dict[str, Any]] = field(default_factory=lambda: [])  # Stages of inquiry
    knowledge_integration: Dict[str, List[str]] = field(default_factory=lambda: {})  # How knowledge is integrated
    stakeholder_involvement: List[Dict[str, Any]] = field(default_factory=lambda: [])  # Stakeholder participation

    # Methodological principles
    fallibilistic_approach: Optional[bool] = None  # Recognition of fallibility
    democratic_participation: Optional[float] = None  # Level of democratic participation (0-1)
    transparent_process: Optional[float] = None  # Process transparency (0-1)
    adaptability: Optional[float] = None  # Adaptability to changing contexts (0-1)

    def assess_inquiry_quality(self) -> Dict[str, Any]:
        """Assess quality of instrumentalist inquiry framework."""
        quality_assessment: Dict[str, Any] = {
            "overall_quality": 0.0,
            "methodological_rigor": "unknown",
            "stakeholder_engagement": "unknown",
            "problem_relevance": "unknown",
            "improvement_areas": []
        }

        # Calculate overall quality
        quality_factors: List[float] = []
        if self.problem_solving_focus is not None:
            quality_factors.append(self.problem_solving_focus * 0.25)
        if self.contextual_sensitivity is not None:
            quality_factors.append(self.contextual_sensitivity * 0.25)
        if self.holistic_approach is not None:
            quality_factors.append(self.holistic_approach * 0.25)
        if self.democratic_participation is not None:
            quality_factors.append(self.democratic_participation * 0.25)

        if quality_factors:
            quality_assessment["overall_quality"] = sum(quality_factors)

        # Assess methodological rigor
        rigor_score = 0.0
        if self.transparent_process is not None:
            rigor_score += self.transparent_process * 0.5
        if self.adaptability is not None:
            rigor_score += self.adaptability * 0.5

        if rigor_score >= 0.7:
            quality_assessment["methodological_rigor"] = "high"
        elif rigor_score >= 0.4:
            quality_assessment["methodological_rigor"] = "moderate"
        else:
            quality_assessment["methodological_rigor"] = "low"
            quality_assessment["improvement_areas"].append("Enhance methodological rigor")

        # Assess stakeholder engagement
        if len(self.stakeholder_involvement) >= 3:
            quality_assessment["stakeholder_engagement"] = "comprehensive"
        elif len(self.stakeholder_involvement) >= 1:
            quality_assessment["stakeholder_engagement"] = "limited"
        else:
            quality_assessment["stakeholder_engagement"] = "minimal"
            quality_assessment["improvement_areas"].append("Increase stakeholder engagement")

        # Assess problem relevance
        if self.problem_solving_focus is not None:
            if self.problem_solving_focus >= 0.8:
                quality_assessment["problem_relevance"] = "high"
            elif self.problem_solving_focus >= 0.6:
                quality_assessment["problem_relevance"] = "moderate"
            else:
                quality_assessment["problem_relevance"] = "low"
                quality_assessment["improvement_areas"].append("Strengthen problem relevance")

        return quality_assessment


@dataclass
class NormativeSystemsAnalysis(Node):
    """Hayden's normative systems analysis framework for SFM evaluation."""

    normative_criteria: List[str] = field(default_factory=lambda: [])  # Normative evaluation criteria
    value_hierarchy: Dict[str, float] = field(default_factory=lambda: {})  # Value priorities
    ethical_framework: Optional[str] = None  # Underlying ethical framework
    social_welfare_measure: Optional[str] = None  # How social welfare is measured

    # Analysis components
    system_evaluation: Dict[str, float] = field(default_factory=lambda: {})  # System component evaluations
    alternative_assessments: List[Dict[str, Any]] = field(default_factory=lambda: [])  # Alternative system assessments
    policy_recommendations: List[Dict[str, Any]] = field(default_factory=lambda: [])  # Policy recommendations

    # Normative principles
    life_process_enhancement: Optional[float] = None  # Focus on life process (0-1)
    democratic_values: Optional[float] = None  # Democratic value emphasis (0-1)
    sustainability_priority: Optional[float] = None  # Sustainability priority (0-1)
    equity_considerations: Optional[float] = None  # Equity emphasis (0-1)

    # Evaluation process
    stakeholder_values: Dict[str, Dict[str, float]] = field(default_factory=lambda: {})  # Stakeholder value sets
    value_conflicts: List[Dict[str, Any]] = field(default_factory=lambda: [])  # Identified value conflicts
    consensus_mechanisms: List[str] = field(default_factory=lambda: [])  # Consensus-building approaches

    def conduct_normative_evaluation(self) -> Dict[str, Any]:
        """Conduct comprehensive normative evaluation of system."""
        evaluation_results: Dict[str, Any] = {
            "overall_system_score": 0.0,
            "value_alignment": "unknown",
            "policy_priority_areas": [],
            "stakeholder_consensus_level": 0.0,
            "normative_recommendations": []
        }

        # Calculate component scores
        evaluation_results["overall_system_score"] = self._calculate_overall_system_score()
        evaluation_results["value_alignment"] = self._assess_value_alignment()
        evaluation_results["policy_priority_areas"] = self._identify_policy_priorities()
        evaluation_results["stakeholder_consensus_level"] = self._calculate_stakeholder_consensus()
        evaluation_results["normative_recommendations"] = self._generate_normative_recommendations(
            evaluation_results)

        return evaluation_results

    def _calculate_overall_system_score(self) -> float:
        """Calculate weighted overall system score."""
        if not self.system_evaluation:
            return 0.0

        weighted_scores: List[float] = []
        for component, score in self.system_evaluation.items():
            weight = self.value_hierarchy.get(component, 1.0)
            weighted_scores.append(score * weight)

        return sum(weighted_scores) / len(weighted_scores) if weighted_scores else 0.0

    def _assess_value_alignment(self) -> str:
        """Assess alignment with core values."""
        alignment_factors: List[float] = []
        
        value_factors = [
            self.life_process_enhancement,
            self.democratic_values,
            self.sustainability_priority,
            self.equity_considerations
        ]
        
        alignment_factors = [factor for factor in value_factors if factor is not None]
        
        if not alignment_factors:
            return "unknown"

        avg_alignment = sum(alignment_factors) / len(alignment_factors)
        if avg_alignment >= 0.8:
            return "strong"
        elif avg_alignment >= 0.6:
            return "moderate"
        else:
            return "weak"

    def _identify_policy_priorities(self) -> List[str]:
        """Identify components needing policy attention."""
        return [
            component for component, score in self.system_evaluation.items()
            if score < 0.6
        ]

    def _calculate_stakeholder_consensus(self) -> float:
        """Calculate level of stakeholder consensus."""
        if not self.stakeholder_values:
            return 0.0

        consensus_scores: List[float] = []
        for value_type in self.value_hierarchy.keys():
            stakeholder_scores = [
                stakeholder_vals.get(value_type, 0.0)
                for stakeholder_vals in self.stakeholder_values.values()
            ]
            if len(stakeholder_scores) > 1:
                # Calculate variance as inverse measure of consensus
                mean_score = sum(stakeholder_scores) / len(stakeholder_scores)
                variance = sum((s - mean_score)**2 for s in stakeholder_scores) / len(stakeholder_scores)
                consensus_scores.append(max(0.0, 1.0 - variance))

        return sum(consensus_scores) / len(consensus_scores) if consensus_scores else 0.0

    def _generate_normative_recommendations(self, evaluation_results: Dict[str, Any]) -> List[str]:
        """Generate actionable normative recommendations."""
        recommendations = []
        
        if evaluation_results["overall_system_score"] < 0.7:
            recommendations.append("System requires significant normative improvements")
        if evaluation_results["value_alignment"] == "weak":
            recommendations.append("Strengthen alignment with core values")
        if evaluation_results["stakeholder_consensus_level"] < 0.6:
            recommendations.append("Build greater stakeholder consensus")

        return recommendations


@dataclass
class PolicyRelevanceIntegration(Node):
    """Integration framework connecting SFM analysis to political action - key to Hayden's approach."""

    policy_context: Optional[str] = None  # Policy environment context
    political_feasibility: Optional[float] = None  # Political feasibility (0-1)
    implementation_capacity: Optional[float] = None  # Implementation capacity (0-1)
    stakeholder_support: Optional[float] = None  # Stakeholder support level (0-1)

    # Political action integration
    lobbying_strategies: List[Dict[str, Any]] = field(default_factory=lambda: [])  # Lobbying approaches
    budgetary_processes: List[Dict[str, Any]] = field(default_factory=lambda: [])  # Budget integration
    administrative_implementation: Dict[str, List[str]] = field(default_factory=lambda: {})  # Implementation pathways
    legislative_pathways: List[Dict[str, Any]] = field(default_factory=lambda: [])  # Legislative routes

    # Policy tools
    policy_instruments: List[uuid.UUID] = field(default_factory=lambda: [])  # Available policy tools
    institutional_leverage_points: List[Dict[str, Any]] = field(default_factory=lambda: [])  # Leverage points
    coalition_building_opportunities: List[Dict[str, Any]] = field(default_factory=lambda: [])  # Coalition opportunities

    # Implementation strategy
    short_term_actions: List[str] = field(default_factory=lambda: [])  # Immediate actions
    medium_term_goals: List[str] = field(default_factory=lambda: [])  # Medium-term objectives
    long_term_vision: Optional[str] = None  # Long-term vision
    success_indicators: Dict[str, str] = field(default_factory=lambda: {})  # Success measures

    # Monitoring and feedback
    policy_monitoring_system: Optional[str] = None  # How policy is monitored
    feedback_mechanisms: List[Dict[str, Any]] = field(default_factory=lambda: [])  # Feedback systems
    adaptive_management: Optional[float] = None  # Adaptive management capacity (0-1)

    def assess_policy_integration_capacity(self) -> Dict[str, Any]:
        """Assess capacity for integrating analysis with policy action."""
        integration_assessment: Dict[str, Any] = {
            "overall_integration_capacity": 0.0,
            "political_viability": "unknown",
            "implementation_readiness": "unknown",
            "stakeholder_alignment": "unknown",
            "strategic_recommendations": []
        }

        # Calculate component assessments
        integration_assessment["overall_integration_capacity"] = self._calculate_integration_capacity()
        integration_assessment["political_viability"] = self._assess_political_viability()
        integration_assessment["implementation_readiness"] = self._assess_implementation_readiness()
        integration_assessment["stakeholder_alignment"] = self._assess_stakeholder_alignment()
        integration_assessment["strategic_recommendations"] = self._generate_strategic_recommendations()

        return integration_assessment

    def _calculate_integration_capacity(self) -> float:
        """Calculate overall integration capacity score."""
        capacity_factors: List[float] = []
        
        if self.political_feasibility is not None:
            capacity_factors.append(self.political_feasibility * 0.3)
        if self.implementation_capacity is not None:
            capacity_factors.append(self.implementation_capacity * 0.3)
        if self.stakeholder_support is not None:
            capacity_factors.append(self.stakeholder_support * 0.4)

        return sum(capacity_factors) if capacity_factors else 0.0

    def _assess_political_viability(self) -> str:
        """Assess political viability level."""
        if self.political_feasibility is None:
            return "unknown"
        
        if self.political_feasibility >= 0.7:
            return "high"
        elif self.political_feasibility >= 0.4:
            return "moderate"
        else:
            return "low"

    def _assess_implementation_readiness(self) -> str:
        """Assess implementation readiness level."""
        if self.implementation_capacity is None:
            return "unknown"
        
        if self.implementation_capacity >= 0.7:
            return "high"
        elif self.implementation_capacity >= 0.4:
            return "moderate"
        else:
            return "low"

    def _assess_stakeholder_alignment(self) -> str:
        """Assess stakeholder alignment level."""
        if self.stakeholder_support is None:
            return "unknown"
        
        if self.stakeholder_support >= 0.7:
            return "strong"
        elif self.stakeholder_support >= 0.4:
            return "moderate"
        else:
            return "weak"

    def _generate_strategic_recommendations(self) -> List[str]:
        """Generate strategic recommendations based on assessment."""
        recommendations = []
        
        # Check individual factors
        if self.political_feasibility is not None and self.political_feasibility < 0.4:
            recommendations.append("Build political support")
        if self.implementation_capacity is not None and self.implementation_capacity < 0.4:
            recommendations.append("Strengthen implementation capacity")
        if self.stakeholder_support is not None and self.stakeholder_support < 0.4:
            recommendations.append("Build stakeholder coalitions")
        
        # Check system capabilities
        if len(self.policy_instruments) < 3:
            recommendations.append("Expand policy instrument toolkit")
        if len(self.coalition_building_opportunities) < 2:
            recommendations.append("Identify coalition opportunities")
        if self.adaptive_management is not None and self.adaptive_management < 0.6:
            recommendations.append("Enhance adaptive management capacity")

        return recommendations


@dataclass
class DatabaseIntegrationCapability(Node):
    """Database integration for statistical analysis support - part of Hayden's methodology."""

    database_type: Optional[str] = None  # Type of database system
    data_architecture: Optional[str] = None  # Data architecture approach
    integration_level: Optional[float] = None  # Level of integration (0-1)
    data_quality_standards: List[str] = field(default_factory=lambda: [])  # Quality standards

    # Data management
    data_collection_protocols: List[Dict[str, Any]] = field(default_factory=lambda: [])  # Collection protocols
    data_validation_rules: List[Dict[str, Any]] = field(default_factory=lambda: [])  # Validation rules
    data_storage_systems: Dict[str, str] = field(default_factory=lambda: {})  # Storage systems
    data_access_controls: List[str] = field(default_factory=lambda: [])  # Access controls

    # Statistical analysis integration
    statistical_packages: List[str] = field(default_factory=lambda: [])  # Statistical software
    analysis_workflows: List[Dict[str, Any]] = field(default_factory=lambda: [])  # Analysis workflows
    visualization_capabilities: Dict[str, List[str]] = field(default_factory=lambda: {})  # Visualization tools
    reporting_systems: List[Dict[str, Any]] = field(default_factory=lambda: [])  # Reporting capabilities

    # Matrix integration
    matrix_data_mapping: Dict[str, str] = field(default_factory=lambda: {})  # Matrix -> database mapping
    indicator_calculation_rules: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {})  # Calculation rules
    automated_updates: List[str] = field(default_factory=lambda: [])  # Automated update processes

    # Performance metrics
    data_processing_speed: Optional[float] = None  # Processing speed rating (0-1)
    system_reliability: Optional[float] = None  # System reliability (0-1)
    user_satisfaction: Optional[float] = None  # User satisfaction (0-1)

    def evaluate_database_capability(self) -> Dict[str, Any]:
        """Evaluate database integration and analytical capability."""
        capability_evaluation: Dict[str, Any] = {
            "overall_capability": 0.0,
            "data_management_quality": "unknown",
            "analytical_power": "unknown",
            "matrix_integration_level": "unknown",
            "improvement_priorities": []
        }

        # Calculate overall capability
        capability_factors: List[float] = []
        if self.integration_level is not None:
            capability_factors.append(self.integration_level * 0.3)
        if self.data_processing_speed is not None:
            capability_factors.append(self.data_processing_speed * 0.3)
        if self.system_reliability is not None:
            capability_factors.append(self.system_reliability * 0.4)

        if capability_factors:
            capability_evaluation["overall_capability"] = sum(capability_factors)

        # Assess data management quality
        quality_indicators = len(self.data_quality_standards) + len(self.data_validation_rules)
        if quality_indicators >= 5:
            capability_evaluation["data_management_quality"] = "high"
        elif quality_indicators >= 3:
            capability_evaluation["data_management_quality"] = "moderate"
        else:
            capability_evaluation["data_management_quality"] = "low"
            capability_evaluation["improvement_priorities"].append("Strengthen data management")

        # Assess analytical power
        analysis_capabilities = len(self.statistical_packages) + len(self.analysis_workflows)
        if analysis_capabilities >= 5:
            capability_evaluation["analytical_power"] = "strong"
        elif analysis_capabilities >= 3:
            capability_evaluation["analytical_power"] = "moderate"
        else:
            capability_evaluation["analytical_power"] = "limited"
            capability_evaluation["improvement_priorities"].append("Expand analytical capabilities")

        # Assess matrix integration level
        integration_indicators = len(self.matrix_data_mapping) + len(self.indicator_calculation_rules)
        if integration_indicators >= 10:
            capability_evaluation["matrix_integration_level"] = "comprehensive"
        elif integration_indicators >= 5:
            capability_evaluation["matrix_integration_level"] = "partial"
        else:
            capability_evaluation["matrix_integration_level"] = "minimal"
            capability_evaluation["improvement_priorities"].append("Enhance matrix integration")

        # Additional improvement priorities
        if self.user_satisfaction is not None and self.user_satisfaction < 0.7:
            capability_evaluation["improvement_priorities"].append("Improve user experience")
        if len(self.automated_updates) < 3:
            capability_evaluation["improvement_priorities"].append("Increase automation")

        return capability_evaluation