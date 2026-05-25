"""
Network analysis components for the Social Fabric Matrix framework.

This module contains classes for cross-impact analysis, delivery relationships,
network analysis, and system interactions.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple

from models.base_nodes import Node
from models.sfm_enums import CrossImpactType


@dataclass
class CrossImpactAnalysis(Node):
    """Analyzes how changes in matrix cells affect other cells."""

    primary_cell_id: Optional[uuid.UUID] = None  # The cell being changed - made optional for dataclass ordering
    impacted_cells: Dict[str, float] = field(default_factory=lambda: {})  # Cell ID string -> impact strength
    impact_type: CrossImpactType = CrossImpactType.DIRECT
    impact_mechanism: Optional[str] = None  # How the impact occurs
    time_delay: Optional[float] = None  # Lag time for impact
    confidence_level: Optional[float] = None  # Confidence in impact assessment
    feedback_loops: List[uuid.UUID] = field(default_factory=lambda: [])  # Related feedback loops
    institutional_mediators: List[uuid.UUID] = field(default_factory=lambda: [])  # Institutions that mediate impact
    mitigation_strategies: List[str] = field(default_factory=lambda: [])  # Ways to reduce negative impacts
    amplification_strategies: List[str] = field(default_factory=lambda: [])  # Ways to enhance positive impacts

    def __post_init__(self) -> None:
        """Validate that primary cell is provided."""
        if self.primary_cell_id is None:
            raise ValueError("primary_cell_id is required for CrossImpactAnalysis")


@dataclass
class DeliveryRelationship(Node):
    """Models how system components make deliveries to each other - core to Hayden's SFM."""

    source_component_id: Optional[uuid.UUID] = None
    target_component_id: Optional[uuid.UUID] = None
    delivery_type: Optional[str] = None  # "service", "resource", "information", "value", etc.
    delivery_content: Optional[str] = None  # What is being delivered
    delivery_mechanism: Optional[str] = None  # How delivery is made

    # Delivery characteristics
    delivery_quality: Optional[float] = None  # Quality of delivery (0-1)
    delivery_reliability: Optional[float] = None  # Reliability (0-1)
    delivery_frequency: Optional[str] = None  # How often delivery occurs
    delivery_capacity: Optional[float] = None  # Maximum capacity (0-1)
    delivery_efficiency: Optional[float] = None  # Efficiency of delivery (0-1)

    # Relationship dynamics
    reciprocity_level: Optional[float] = None  # Level of reciprocity (0-1)
    dependency_strength: Optional[float] = None  # How dependent target is on delivery (0-1)
    substitutability: Optional[float] = None  # Availability of substitutes (0-1)
    criticality: Optional[float] = None  # Criticality to system functioning (0-1)

    # Matrix integration
    institutional_mediation: List[uuid.UUID] = field(default_factory=lambda: [])  # Institutions mediating delivery
    technological_requirements: List[uuid.UUID] = field(default_factory=lambda: [])  # Required technologies
    cultural_factors: Dict[str, float] = field(default_factory=lambda: {})  # Cultural influences on delivery
    ecological_constraints: List[str] = field(default_factory=lambda: [])  # Environmental constraints

    # Performance metrics
    delivery_failures: List[Dict[str, Any]] = field(default_factory=lambda: [])  # Record of failures
    improvement_opportunities: List[str] = field(default_factory=lambda: [])  # Potential improvements
    monitoring_indicators: Dict[str, float] = field(default_factory=lambda: {})  # Performance indicators

    def assess_delivery_performance(self) -> Dict[str, Any]:
        """Assess overall delivery relationship performance."""
        performance_assessment: Dict[str, Any] = {
            "overall_performance": 0.0,
            "reliability_rating": "unknown",
            "efficiency_rating": "unknown",
            "criticality_level": "unknown",
            "improvement_potential": 0.0
        }

        # Calculate overall performance
        performance_factors: List[float] = []
        if self.delivery_quality is not None:
            performance_factors.append(self.delivery_quality * 0.3)
        if self.delivery_reliability is not None:
            performance_factors.append(self.delivery_reliability * 0.3)
        if self.delivery_efficiency is not None:
            performance_factors.append(self.delivery_efficiency * 0.4)

        if performance_factors:
            performance_assessment["overall_performance"] = sum(performance_factors)

        # Assess reliability rating
        if self.delivery_reliability is not None:
            if self.delivery_reliability >= 0.8:
                performance_assessment["reliability_rating"] = "high"
            elif self.delivery_reliability >= 0.6:
                performance_assessment["reliability_rating"] = "moderate"
            else:
                performance_assessment["reliability_rating"] = "low"

        # Assess efficiency rating
        if self.delivery_efficiency is not None:
            if self.delivery_efficiency >= 0.8:
                performance_assessment["efficiency_rating"] = "high"
            elif self.delivery_efficiency >= 0.6:
                performance_assessment["efficiency_rating"] = "moderate"
            else:
                performance_assessment["efficiency_rating"] = "low"

        # Assess criticality level
        if self.criticality is not None:
            if self.criticality >= 0.7:
                performance_assessment["criticality_level"] = "high"
            elif self.criticality >= 0.4:
                performance_assessment["criticality_level"] = "moderate"
            else:
                performance_assessment["criticality_level"] = "low"

        # Calculate improvement potential
        current_performance = performance_assessment["overall_performance"]
        performance_assessment["improvement_potential"] = max(0.0, 1.0 - current_performance)

        return performance_assessment


@dataclass
class MatrixDeliveryNetwork(Node):
    """Network of deliveries between matrix cells - central to Hayden's SFM methodology."""

    network_scope: Optional[str] = None  # "local", "regional", "national", "global"
    network_density: Optional[float] = None  # Density of delivery relationships (0-1)
    network_centralization: Optional[float] = None  # Centralization level (0-1)
    network_efficiency: Optional[float] = None  # Overall efficiency (0-1)

    # Network components
    delivery_relationships: List[uuid.UUID] = field(default_factory=lambda: [])  # Individual delivery relationships
    hub_components: List[uuid.UUID] = field(default_factory=lambda: [])  # Network hubs
    peripheral_components: List[uuid.UUID] = field(default_factory=lambda: [])  # Peripheral components
    bridge_components: List[uuid.UUID] = field(default_factory=lambda: [])  # Bridge components

    # Network characteristics
    redundancy_level: Optional[float] = None  # Network redundancy (0-1)
    vulnerability_points: List[Dict[str, Any]] = field(default_factory=lambda: [])  # Network vulnerabilities
    resilience_factors: List[str] = field(default_factory=lambda: [])  # Factors supporting resilience
    adaptation_capacity: Optional[float] = None  # Network adaptation capacity (0-1)

    # Network flows
    flow_patterns: Dict[str, List[Dict[str, Any]]] = field(default_factory=lambda: {})  # Flow type -> patterns
    bottlenecks: List[Dict[str, Any]] = field(default_factory=lambda: [])  # Network bottlenecks
    capacity_constraints: Dict[str, float] = field(default_factory=lambda: {})  # Constraint type -> severity

    # Performance metrics
    delivery_success_rate: Optional[float] = None  # Overall success rate (0-1)
    network_responsiveness: Optional[float] = None  # Response to changes (0-1)
    coordination_effectiveness: Optional[float] = None  # Coordination quality (0-1)

    def analyze_network_performance(self) -> Dict[str, Any]:
        """Analyze overall network performance and health."""
        network_analysis: Dict[str, Any] = {
            "overall_performance": 0.0,
            "network_health": "unknown",
            "critical_vulnerabilities": len(self.vulnerability_points),
            "improvement_priorities": [],
            "network_type": "unknown"
        }

        # Calculate overall performance
        performance_factors: List[float] = []
        if self.network_efficiency is not None:
            performance_factors.append(self.network_efficiency * 0.3)
        if self.delivery_success_rate is not None:
            performance_factors.append(self.delivery_success_rate * 0.3)
        if self.coordination_effectiveness is not None:
            performance_factors.append(self.coordination_effectiveness * 0.4)

        if performance_factors:
            network_analysis["overall_performance"] = sum(performance_factors)

        # Assess network health
        health_score = network_analysis["overall_performance"]
        if health_score >= 0.8:
            network_analysis["network_health"] = "excellent"
        elif health_score >= 0.6:
            network_analysis["network_health"] = "good"
        elif health_score >= 0.4:
            network_analysis["network_health"] = "fair"
        else:
            network_analysis["network_health"] = "poor"

        # Determine network type
        if self.network_centralization is not None:
            if self.network_centralization >= 0.7:
                network_analysis["network_type"] = "centralized"
            elif self.network_centralization <= 0.3:
                network_analysis["network_type"] = "decentralized"
            else:
                network_analysis["network_type"] = "distributed"

        # Identify improvement priorities
        if len(self.bottlenecks) > 2:
            network_analysis["improvement_priorities"].append("Address network bottlenecks")
        if len(self.vulnerability_points) > 3:
            network_analysis["improvement_priorities"].append("Strengthen network resilience")
        if self.redundancy_level is not None and self.redundancy_level < 0.5:
            network_analysis["improvement_priorities"].append("Increase network redundancy")

        return network_analysis