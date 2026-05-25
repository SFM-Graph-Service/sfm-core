"""
Additional specialized components for the Social Fabric Matrix framework.

This module contains additional specialized classes that support various aspects
of SFM analysis including social indicators, evolutionary pathways, and other
specialized tools.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

from models.base_nodes import Node
from models.sfm_enums import EvolutionaryStage, NormativeFramework


@dataclass
class SocialIndicatorSystem(Node):
    """Systematic social indicator development and management - key to Hayden's methodology."""

    indicator_category: Optional[str] = None  # "economic", "social", "environmental", "institutional"
    measurement_framework: Optional[str] = None  # Framework used for measurement
    data_collection_method: Optional[str] = None  # How data is collected
    update_frequency: Optional[str] = None  # How often indicators are updated

    # Indicator components
    primary_indicators: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {})  # Core indicators
    secondary_indicators: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {})  # Supporting indicators
    composite_indicators: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {})  # Composite measures

    # System characteristics
    indicator_validity: Optional[float] = None  # Validity of indicator system (0-1)
    indicator_reliability: Optional[float] = None  # Reliability of measurements (0-1)
    stakeholder_acceptance: Optional[float] = None  # Stakeholder acceptance level (0-1)
    policy_relevance: Optional[float] = None  # Relevance to policy decisions (0-1)

    # Matrix integration
    matrix_cell_linkages: Dict[uuid.UUID, List[str]] = field(default_factory=lambda: {})  # Cell -> indicators
    institutional_monitoring: Dict[uuid.UUID, List[str]] = field(default_factory=lambda: {})  # Institution -> responsibilities
    feedback_mechanisms: List[Dict[str, Any]] = field(default_factory=lambda: [])  # How indicators feed back to system

    # Database integration
    data_sources: List[str] = field(default_factory=lambda: [])  # Data sources
    database_schema: Optional[str] = None  # Database structure
    statistical_methods: List[str] = field(default_factory=lambda: [])  # Statistical approaches used
    quality_controls: List[str] = field(default_factory=lambda: [])  # Quality control measures

    def assess_indicator_system_quality(self) -> Dict[str, Any]:
        """Assess quality and effectiveness of indicator system."""
        quality_assessment: Dict[str, Any] = {
            "overall_quality": 0.0,
            "coverage_adequacy": "unknown",
            "measurement_quality": "unknown",
            "policy_utility": "unknown",
            "improvement_needs": []
        }

        # Calculate overall quality
        quality_factors: List[float] = []
        if self.indicator_validity is not None:
            quality_factors.append(self.indicator_validity * 0.3)
        if self.indicator_reliability is not None:
            quality_factors.append(self.indicator_reliability * 0.3)
        if self.policy_relevance is not None:
            quality_factors.append(self.policy_relevance * 0.4)

        if quality_factors:
            quality_assessment["overall_quality"] = sum(quality_factors)

        # Assess coverage adequacy
        total_indicators = len(self.primary_indicators) + len(self.secondary_indicators)
        if total_indicators >= 10:
            quality_assessment["coverage_adequacy"] = "comprehensive"
        elif total_indicators >= 5:
            quality_assessment["coverage_adequacy"] = "adequate"
        else:
            quality_assessment["coverage_adequacy"] = "limited"

        # Assess measurement quality
        if self.indicator_reliability is not None:
            if self.indicator_reliability >= 0.8:
                quality_assessment["measurement_quality"] = "high"
            elif self.indicator_reliability >= 0.6:
                quality_assessment["measurement_quality"] = "moderate"
            else:
                quality_assessment["measurement_quality"] = "low"
                quality_assessment["improvement_needs"].append("Improve measurement reliability")

        # Assess policy utility
        if self.policy_relevance is not None:
            if self.policy_relevance >= 0.8:
                quality_assessment["policy_utility"] = "high"
            elif self.policy_relevance >= 0.6:
                quality_assessment["policy_utility"] = "moderate"
            else:
                quality_assessment["policy_utility"] = "low"
                quality_assessment["improvement_needs"].append("Enhance policy relevance")

        return quality_assessment


@dataclass
class EvolutionaryPathway(Node):
    """Represents evolutionary development pathways for institutions and systems."""

    pathway_stage: EvolutionaryStage = EvolutionaryStage.EMERGENCE
    development_trajectory: List[str] = field(default_factory=lambda: [])  # Historical development path
    evolutionary_pressures: List[str] = field(default_factory=lambda: [])  # Forces driving evolution
    adaptation_mechanisms: List[str] = field(default_factory=lambda: [])  # How system adapts

    # Evolutionary characteristics
    selection_pressures: Dict[str, float] = field(default_factory=lambda: {})  # Pressure type -> intensity
    mutation_rate: Optional[float] = None  # Rate of institutional change (0-1)
    inheritance_mechanisms: List[str] = field(default_factory=lambda: [])  # How traits are passed on
    fitness_landscape: Dict[str, float] = field(default_factory=lambda: {})  # Adaptive fitness measures

    # Path dependencies
    locked_in_traits: List[str] = field(default_factory=lambda: [])  # Characteristics hard to change
    branching_points: List[Dict[str, Any]] = field(default_factory=lambda: [])  # Critical decision points
    alternative_pathways: List[str] = field(default_factory=lambda: [])  # Paths not taken

    # Future evolution
    evolutionary_potential: Optional[float] = None  # Potential for future evolution (0-1)
    constraints_on_evolution: List[str] = field(default_factory=lambda: [])  # Limits on change
    predicted_trajectories: List[Dict[str, Any]] = field(default_factory=lambda: [])  # Predicted future paths

    def assess_evolutionary_potential(self) -> Dict[str, Any]:
        """Assess potential for future evolutionary development."""
        evolution_assessment: Dict[str, Any] = {
            "adaptability": "unknown",
            "constraint_level": "unknown",
            "diversity_potential": 0.0,
            "evolutionary_recommendations": []
        }

        # Assess adaptability based on adaptation mechanisms
        if len(self.adaptation_mechanisms) >= 3:
            evolution_assessment["adaptability"] = "high"
        elif len(self.adaptation_mechanisms) >= 1:
            evolution_assessment["adaptability"] = "moderate"
        else:
            evolution_assessment["adaptability"] = "low"
            evolution_assessment["evolutionary_recommendations"].append("Develop adaptation mechanisms")

        # Assess constraint level
        constraint_count = len(self.constraints_on_evolution) + len(self.locked_in_traits)
        if constraint_count <= 2:
            evolution_assessment["constraint_level"] = "low"
        elif constraint_count <= 5:
            evolution_assessment["constraint_level"] = "moderate"
        else:
            evolution_assessment["constraint_level"] = "high"
            evolution_assessment["evolutionary_recommendations"].append("Address evolutionary constraints")

        # Assess diversity potential
        if self.fitness_landscape:
            # More diverse fitness landscape suggests greater evolutionary potential
            fitness_variance = sum((f - sum(self.fitness_landscape.values())/len(self.fitness_landscape.values()))**2 
                                 for f in self.fitness_landscape.values()) / len(self.fitness_landscape.values())
            evolution_assessment["diversity_potential"] = min(1.0, fitness_variance)

        return evolution_assessment


@dataclass
class SocialProvisioningMatrix(Node):
    """Specialized matrix for analyzing social provisioning systems - core to Hayden's approach."""

    provisioning_categories: List[str] = field(default_factory=lambda: [])  # Types of social provisioning
    provision_mechanisms: Dict[str, List[str]] = field(default_factory=lambda: {})  # How provisions are delivered
    beneficiary_groups: List[uuid.UUID] = field(default_factory=lambda: [])  # Who benefits from provisions

    # Provisioning effectiveness
    coverage_adequacy: Dict[str, float] = field(default_factory=lambda: {})  # Category -> adequacy (0-1)
    access_equity: Dict[str, float] = field(default_factory=lambda: {})  # Category -> equity (0-1)
    quality_standards: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {})  # Quality measures

    # Resource allocation
    resource_allocation_matrix: Dict[str, Dict[str, float]] = field(default_factory=lambda: {})  # Provider -> resources
    funding_sources: Dict[str, List[str]] = field(default_factory=lambda: {})  # Funding mechanisms
    cost_effectiveness: Dict[str, float] = field(default_factory=lambda: {})  # Cost per outcome

    # System integration
    institutional_providers: List[uuid.UUID] = field(default_factory=lambda: [])  # Providing institutions
    coordination_mechanisms: List[uuid.UUID] = field(default_factory=lambda: [])  # Coordination systems
    accountability_systems: Dict[str, List[str]] = field(default_factory=lambda: {})  # Accountability mechanisms

    def analyze_provisioning_gaps(self) -> Dict[str, Any]:
        """Analyze gaps in social provisioning system."""
        gap_analysis: Dict[str, Any] = {
            "coverage_gaps": [],
            "access_barriers": [],
            "quality_issues": [],
            "resource_shortfalls": [],
            "priority_interventions": []
        }

        # Identify coverage gaps
        for category, adequacy in self.coverage_adequacy.items():
            if adequacy < 0.7:  # Below threshold
                gap_analysis["coverage_gaps"].append({
                    "category": category,
                    "adequacy_level": adequacy,
                    "gap_severity": "high" if adequacy < 0.4 else "moderate"
                })

        # Identify access barriers
        for category, equity in self.access_equity.items():
            if equity < 0.6:  # Below equity threshold
                gap_analysis["access_barriers"].append({
                    "category": category,
                    "equity_level": equity,
                    "barrier_severity": "high" if equity < 0.3 else "moderate"
                })

        # Generate priority interventions
        for gap in gap_analysis["coverage_gaps"]:
            if gap["gap_severity"] == "high":
                gap_analysis["priority_interventions"].append(f"Expand {gap['category']} coverage")

        for barrier in gap_analysis["access_barriers"]:
            if barrier["barrier_severity"] == "high":
                gap_analysis["priority_interventions"].append(f"Improve {barrier['category']} access equity")

        return gap_analysis