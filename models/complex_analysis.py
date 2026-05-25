"""
Complex analysis tools for the Social Fabric Matrix framework.

This module contains sophisticated analytical tools including digraph analysis,
circular causation processes, conflict detection, and other complex analytical classes.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple

from models.base_nodes import Node
from models.sfm_enums import ConflictType


@dataclass
class DigraphAnalysis(Node):
    """Enhanced digraph analysis with sequence analysis for institutional dependency tracking."""

    analyzed_institutions: List[uuid.UUID] = field(default_factory=lambda: [])
    dependency_matrix: Dict[str, Dict[str, float]] = field(default_factory=lambda: {})
    cycle_detection: List[List[uuid.UUID]] = field(default_factory=lambda: [])  # Circular dependencies
    path_analysis: Dict[str, List[uuid.UUID]] = field(default_factory=lambda: {})
    critical_institutions: List[uuid.UUID] = field(default_factory=lambda: [])  # High dependency nodes
    leverage_points: List[uuid.UUID] = field(default_factory=lambda: [])  # High influence nodes
    stability_score: Optional[float] = None  # System stability measure (0-1)
    complexity_measure: Optional[float] = None  # System complexity (0-1)
    analysis_timestamp: datetime = field(default_factory=datetime.now)
    methodology_notes: Optional[str] = None

    # Enhanced sequence analysis capabilities
    propagation_sequences: Dict[str, List[Dict[str, Any]]] = field(default_factory=lambda: {})  # Change propagation paths
    temporal_dependencies: Dict[str, Dict[str, float]] = field(default_factory=lambda: {})  # Time-lagged dependencies
    sequence_patterns: List[Dict[str, Any]] = field(default_factory=lambda: [])  # Recurring sequence patterns
    cascade_potential: Dict[str, float] = field(default_factory=lambda: {})  # Institution -> cascade risk

    # Dynamic sequence properties
    sequence_stability: Optional[float] = None  # Stability of propagation sequences (0-1)
    adaptation_pathways: List[List[uuid.UUID]] = field(default_factory=lambda: [])  # Paths for system adaptation
    bottleneck_sequences: List[List[uuid.UUID]] = field(default_factory=lambda: [])  # Sequence bottlenecks

    def analyze_propagation_sequences(
        self,
        initial_change: uuid.UUID,
        time_steps: int = 5) -> List[Dict[str, Any]]:
        """Analyze how changes propagate through the institutional network over time."""
        sequences: List[Dict[str, Any]] = []

        # Start with initial change
        current_affected: Dict[str, float] = {str(initial_change): 1.0}  # Institution ID -> impact strength
        sequence_step: Dict[str, Any] = {
            "step": 0,
            "affected_institutions": current_affected.copy(),
            "new_impacts": current_affected.copy(),
            "cumulative_impact": sum(current_affected.values())
        }
        sequences.append(sequence_step)

        # Propagate through time steps
        for step in range(1, time_steps + 1):
            new_impacts: Dict[str, float] = {}

            # For each currently affected institution, find its dependencies
            for institution_id, impact_strength in current_affected.items():
                if institution_id in self.dependency_matrix:
                    for dependent_id, dependency_strength in self.dependency_matrix[institution_id].items():
                        # Calculate propagated impact (with decay)
                        decay_factor = 0.8 ** step  # Impact decays over time
                        propagated_impact = impact_strength * dependency_strength * decay_factor

                        if propagated_impact > 0.1:  # Threshold for significant impact
                            if dependent_id not in new_impacts:
                                new_impacts[dependent_id] = 0.0
                            new_impacts[dependent_id] += propagated_impact

            # Add new impacts to cumulative
            for inst_id, impact in new_impacts.items():
                if inst_id not in current_affected:
                    current_affected[inst_id] = 0.0
                current_affected[inst_id] += impact

            sequence_step = {
                "step": step,
                "affected_institutions": current_affected.copy(),
                "new_impacts": new_impacts,
                "cumulative_impact": sum(current_affected.values())
            }
            sequences.append(sequence_step)

            # Stop if no new significant impacts
            if not new_impacts:
                break

        return sequences

    def identify_critical_sequences(self) -> List[Dict[str, Any]]:
        """Identify sequences that are critical for system functioning."""
        critical_sequences: List[Dict[str, Any]] = []

        # Analyze each potential starting point
        for institution_id in self.analyzed_institutions:
            sequences = self.analyze_propagation_sequences(institution_id)

            # Calculate sequence criticality
            max_impact = max(seq["cumulative_impact"] for seq in sequences)
            affected_count = len(sequences[-1]["affected_institutions"]) if sequences else 0

            if max_impact > 2.0 or affected_count > len(self.analyzed_institutions) * 0.5:
                critical_sequences.append({
                    "starting_institution": institution_id,
                    "max_impact": max_impact,
                    "institutions_affected": affected_count,
                    "sequence_length": len(sequences),
                    "criticality_score": max_impact * (affected_count / len(self.analyzed_institutions))
                })

        return sorted(critical_sequences, key=lambda x: x["criticality_score"], reverse=True)

    def detect_sequence_patterns(self) -> List[Dict[str, Any]]:
        """Detect recurring patterns in propagation sequences."""
        patterns: List[Dict[str, Any]] = []

        # Analyze sequences for common patterns
        all_sequences: List[List[Dict[str, Any]]] = []
        for institution_id in self.analyzed_institutions[:10]:  # Limit for performance
            sequences = self.analyze_propagation_sequences(institution_id, time_steps=3)
            all_sequences.append(sequences)

        # Look for common propagation paths
        path_frequency: Dict[str, int] = {}
        for sequences in all_sequences:
            for i in range(len(sequences) - 1):
                current_step = sequences[i]
                next_step = sequences[i + 1]

                # Create path signature
                current_institutions = set(current_step["affected_institutions"].keys())
                new_institutions = set(next_step["new_impacts"].keys())

                if new_institutions:  # Only if there are new impacts
                    path_key = f"{len(current_institutions)}->{len(new_institutions)}"
                    if path_key not in path_frequency:
                        path_frequency[path_key] = 0
                    path_frequency[path_key] += 1

        # Identify frequent patterns
        total_sequences = len(all_sequences)
        for path_pattern, frequency in path_frequency.items():
            if frequency / total_sequences > 0.3:  # Appears in >30% of sequences
                patterns.append({
                    "pattern": path_pattern,
                    "frequency": frequency,
                    "prevalence": frequency / total_sequences,
                    "description": f"Pattern where {path_pattern} institutions are affected"
                })

        return sorted(patterns, key=lambda x: x["prevalence"], reverse=True)

    def assess_sequence_stability(self) -> Dict[str, Any]:
        """Assess the stability of propagation sequences."""
        stability_assessment: Dict[str, Any] = {
            "overall_stability": "unknown",
            "vulnerable_sequences": [],
            "stable_sequences": [],
            "stability_factors": []
        }

        # Analyze critical sequences for stability
        critical_sequences = self.identify_critical_sequences()

        for seq in critical_sequences:
            institution_id = seq["starting_institution"]

            # Check if starting institution is in leverage points (more vulnerable)
            if institution_id in self.leverage_points:
                stability_assessment["vulnerable_sequences"].append({
                    "institution": institution_id,
                    "reason": "High leverage point - changes here affect many others",
                    "impact_potential": seq["criticality_score"]
                })
            else:
                stability_assessment["stable_sequences"].append({
                    "institution": institution_id,
                    "stability_factor": seq["criticality_score"]
                })

        # Overall stability assessment
        vulnerable_count = len(stability_assessment["vulnerable_sequences"])
        total_critical = len(critical_sequences)

        if total_critical > 0:
            stability_ratio = 1.0 - (vulnerable_count / total_critical)
            if stability_ratio > 0.7:
                stability_assessment["overall_stability"] = "high"
            elif stability_ratio > 0.4:
                stability_assessment["overall_stability"] = "moderate"
            else:
                stability_assessment["overall_stability"] = "low"

        return stability_assessment

    def recommend_sequence_interventions(self) -> List[Dict[str, Any]]:
        """Recommend interventions to improve sequence stability."""
        recommendations: List[Dict[str, Any]] = []

        stability_assessment = self.assess_sequence_stability()

        # Recommendations for vulnerable sequences
        for vulnerable_seq in stability_assessment["vulnerable_sequences"]:
            institution_id = vulnerable_seq["institution"]

            recommendations.append({
                "type": "risk_mitigation",
                "target_institution": institution_id,
                "intervention": "Create redundant pathways to reduce dependency",
                "priority": "high" if vulnerable_seq["impact_potential"] > 3.0 else "medium",
                "rationale": "Institution is high-leverage point affecting many others"
            })

        # Recommendations for bottlenecks
        for bottleneck_sequence in self.bottleneck_sequences:
            if bottleneck_sequence:  # Check if sequence is not empty
                bottleneck_institution = bottleneck_sequence[len(bottleneck_sequence) // 2]  # Middle of sequence

                recommendations.append({
                    "type": "bottleneck_resolution",
                    "target_institution": bottleneck_institution,
                    "intervention": "Strengthen capacity or create alternative pathways",
                    "priority": "medium",
                    "rationale": "Institution is a bottleneck in critical sequences"
                })

        return sorted(
            recommendations,
            key=lambda x: {"high": 3, "medium": 2, "low": 1}[x["priority"]],
            reverse=True)


@dataclass
class CircularCausationProcess(Node):
    """Models Veblen's circular and cumulative causation processes - foundational to Hayden's SFM."""

    process_type: Optional[str] = None  # "virtuous", "vicious", "neutral"
    causation_strength: Optional[float] = None  # Strength of causal process (0-1)
    feedback_polarity: Optional[str] = None  # "positive", "negative", "mixed"
    time_scale: Optional[str] = None  # "short-term", "medium-term", "long-term"

    # Process components
    causal_elements: List[uuid.UUID] = field(default_factory=lambda: [])  # Elements in causal chain
    feedback_loops: List[Dict[str, Any]] = field(default_factory=lambda: [])  # Feedback mechanisms
    reinforcement_mechanisms: List[str] = field(default_factory=lambda: [])  # What reinforces the process
    disruption_factors: List[str] = field(default_factory=lambda: [])  # What can disrupt the process

    # Process dynamics
    momentum_level: Optional[float] = None  # Process momentum (0-1)
    stability_tendency: Optional[float] = None  # Tendency toward stability (0-1)
    change_acceleration: Optional[float] = None  # Rate of change acceleration
    threshold_effects: List[Dict[str, Any]] = field(default_factory=lambda: [])  # Critical thresholds

    # Matrix integration
    institutional_embedment: List[uuid.UUID] = field(default_factory=lambda: [])  # Institutions embedding process
    technological_enablers: List[uuid.UUID] = field(default_factory=lambda: [])  # Technologies enabling process
    cultural_reinforcement: Dict[str, float] = field(default_factory=lambda: {})  # Cultural reinforcement factors
    ecological_limits: List[str] = field(default_factory=lambda: [])  # Environmental constraints

    # Intervention points
    intervention_opportunities: List[Dict[str, Any]] = field(default_factory=lambda: [])  # Where to intervene
    policy_leverage_points: List[Dict[str, Any]] = field(default_factory=lambda: [])  # Policy intervention points

    def analyze_causation_dynamics(self) -> Dict[str, Any]:
        """Analyze the dynamics of the circular causation process."""
        dynamics_analysis: Dict[str, Any] = {
            "process_strength": self.causation_strength or 0.0,
            "process_direction": "unknown",
            "stability_assessment": "unknown",
            "intervention_potential": 0.0,
            "system_impact": "unknown"
        }

        # Determine process direction
        if self.process_type == "virtuous":
            dynamics_analysis["process_direction"] = "beneficial"
        elif self.process_type == "vicious":
            dynamics_analysis["process_direction"] = "harmful"
        else:
            dynamics_analysis["process_direction"] = "neutral"

        # Assess stability
        if self.stability_tendency is not None:
            if self.stability_tendency >= 0.7:
                dynamics_analysis["stability_assessment"] = "highly_stable"
            elif self.stability_tendency >= 0.4:
                dynamics_analysis["stability_assessment"] = "moderately_stable"
            else:
                dynamics_analysis["stability_assessment"] = "unstable"

        # Calculate intervention potential
        intervention_factors = len(self.intervention_opportunities) + len(self.policy_leverage_points)
        dynamics_analysis["intervention_potential"] = min(1.0, intervention_factors / 10.0)

        # Assess system impact
        if self.momentum_level is not None and self.causation_strength is not None:
            impact_score = (self.momentum_level + self.causation_strength) / 2
            if impact_score >= 0.7:
                dynamics_analysis["system_impact"] = "high"
            elif impact_score >= 0.4:
                dynamics_analysis["system_impact"] = "moderate"
            else:
                dynamics_analysis["system_impact"] = "low"

        return dynamics_analysis


@dataclass
class ConflictDetection(Node):
    """System for detecting contradictory relationships and institutional conflicts per Hayden's SFM methodology."""

    analyzed_system_id: Optional[uuid.UUID] = None  # System being analyzed
    conflict_type: ConflictType = ConflictType.VALUE_CONFLICT

    # Detected conflicts
    direct_conflicts: List[Dict[str, Any]] = field(default_factory=lambda: [])  # Direct contradictions
    indirect_conflicts: List[Dict[str, Any]] = field(default_factory=lambda: [])  # Indirect conflicts
    potential_conflicts: List[Dict[str, Any]] = field(default_factory=lambda: [])  # Potential future conflicts

    # Conflict characteristics
    conflict_intensity: Dict[str, float] = field(default_factory=lambda: {})  # Conflict ID -> intensity (0-1)
    affected_stakeholders: Dict[str, List[uuid.UUID]] = field(default_factory=lambda: {})  # Conflict -> stakeholders
    resolution_difficulty: Dict[str, float] = field(default_factory=lambda: {})  # Conflict -> difficulty (0-1)

    # Enhanced SFM integration
    conflicting_matrix_cells: List[Tuple[uuid.UUID, uuid.UUID]] = field(default_factory=lambda: [])  # Conflicting cell pairs
    institutional_contradictions: List[uuid.UUID] = field(default_factory=lambda: [])  # Contradictory institutions
    value_system_conflicts: List[Tuple[uuid.UUID, uuid.UUID]] = field(default_factory=lambda: [])  # Conflicting value systems

    # Delivery system conflicts - Hayden's emphasis on deliveries
    delivery_contradictions: Dict[str, List[Dict[str, Any]]] = field(default_factory=lambda: {})  # Conflicting deliveries
    delivery_failures: List[Dict[str, Any]] = field(default_factory=lambda: [])  # Failed delivery relationships

    # Belief/Value/Attitude conflicts - Hayden's cultural analysis
    belief_value_contradictions: List[Dict[str, Any]] = field(default_factory=lambda: [])  # Belief-value conflicts
    attitude_belief_misalignments: List[Dict[str, Any]] = field(default_factory=lambda: [])  # Attitude-belief conflicts
    cultural_institutional_conflicts: List[Dict[str, Any]] = field(default_factory=lambda: [])  # Culture-institution conflicts

    # Ceremonial vs Instrumental conflicts - Core to Hayden's framework
    ceremonial_instrumental_tensions: List[Dict[str, Any]] = field(default_factory=lambda: [])
    ceremonial_dominance_conflicts: List[Dict[str, Any]] = field(default_factory=lambda: [])  # When ceremonial blocks instrumental
    instrumental_disruption_conflicts: List[Dict[str, Any]] = field(default_factory=lambda: [])  # When instrumental disrupts ceremonial

    # Technology-Institution conflicts
    technology_institution_mismatches: List[Dict[str, Any]] = field(default_factory=lambda: [])
    technological_ceremonial_conflicts: List[Dict[str, Any]] = field(default_factory=lambda: [])

    # Ecological system conflicts - Hayden includes ecological systems
    ecological_institutional_conflicts: List[Dict[str, Any]] = field(default_factory=lambda: [])
    ecological_technology_conflicts: List[Dict[str, Any]] = field(default_factory=lambda: [])

    # Resolution approaches
    mediation_mechanisms: Dict[str, List[str]] = field(default_factory=lambda: {})  # Conflict -> mechanisms
    structural_solutions: Dict[str, List[str]] = field(default_factory=lambda: {})  # Conflict -> structural changes
    compromise_possibilities: Dict[str, List[str]] = field(default_factory=lambda: {})  # Conflict -> compromises

    # Temporal aspects
    conflict_trajectory: Dict[str, str] = field(default_factory=lambda: {})  # Conflict -> "escalating"/"stable"/"declining"
    historical_precedents: Dict[str, List[str]] = field(default_factory=lambda: {})  # Similar past conflicts
    urgency_levels: Dict[str, float] = field(default_factory=lambda: {})  # Conflict -> urgency (0-1)

    def __post_init__(self) -> None:
        """Validate that system is provided."""
        if self.analyzed_system_id is None:
            raise ValueError("analyzed_system_id is required for ConflictDetection")

    def detect_matrix_contradictions(self, matrix_cells: List[uuid.UUID]) -> List[Dict[str, Any]]:
        """Detect contradictions between matrix cell correlations."""
        contradictions: List[Dict[str, Any]] = []

        # This would need access to actual matrix cell data to implement fully
        # For now, return structure for potential contradictions

        for i, cell1 in enumerate(matrix_cells):
            for cell2 in matrix_cells[i+1:]:
                # Check for logical contradictions
                # Example: Institution A enhances Criterion X (+3)
                # but Institution A conflicts with Institution B (-2)
                # and Institution B also enhances Criterion X (+3)
                # This suggests a contradiction that needs investigation

                contradiction: Dict[str, Any] = {
                    "cell_pair": (cell1, cell2),
                    "contradiction_type": "logical_inconsistency",
                    "severity": "moderate",
                    "description": "Potential logical inconsistency detected",
                    "investigation_needed": True
                }
                contradictions.append(contradiction)

        return contradictions

    def assess_conflict_priority(self) -> List[Dict[str, Any]]:
        """Prioritize conflicts for resolution efforts."""
        all_conflicts = self.direct_conflicts + self.indirect_conflicts

        prioritized: List[Dict[str, Any]] = []
        for conflict in all_conflicts:
            conflict_id = conflict.get("id", "unknown")

            priority_score = 0.0

            # Factor in intensity
            intensity = self.conflict_intensity.get(conflict_id, 0.5)
            priority_score += intensity * 0.4

            # Factor in urgency
            urgency = self.urgency_levels.get(conflict_id, 0.5)
            priority_score += urgency * 0.3

            # Factor in number of affected stakeholders
            stakeholders = len(self.affected_stakeholders.get(conflict_id, []))
            stakeholder_score = min(1.0, stakeholders / 10.0)  # Normalize
            priority_score += stakeholder_score * 0.2

            # Factor in resolution difficulty (inverse - easier to resolve gets higher priority)
            difficulty = self.resolution_difficulty.get(conflict_id, 0.5)
            priority_score += (1.0 - difficulty) * 0.1

            prioritized.append({
                "conflict": conflict,
                "priority_score": priority_score,
                "recommended_action": "immediate" if priority_score > 0.7 else "planned" if priority_score > 0.4 else "monitor"
            })

        return sorted(prioritized, key=lambda x: x["priority_score"], reverse=True)

    def generate_conflict_report(self) -> Dict[str, Any]:
        """Generate comprehensive conflict analysis report."""
        report: Dict[str, Any] = {
            "conflict_summary": {
                "total_conflicts": len(self.direct_conflicts) + len(self.indirect_conflicts),
                "direct_conflicts": len(self.direct_conflicts),
                "indirect_conflicts": len(self.indirect_conflicts),
                "high_priority_conflicts": 0
            },
            "conflict_types": {},
            "affected_areas": [],
            "resolution_recommendations": [],
            "monitoring_requirements": []
        }

        # Count high priority conflicts
        priority_analysis = self.assess_conflict_priority()
        report["conflict_summary"]["high_priority_conflicts"] = len([
            c for c in priority_analysis if c["priority_score"] > 0.7
        ])

        # Analyze conflict types
        all_conflicts = self.direct_conflicts + self.indirect_conflicts
        for conflict in all_conflicts:
            conflict_type = conflict.get("type", "unknown")
            if conflict_type not in report["conflict_types"]:
                report["conflict_types"][conflict_type] = 0
            report["conflict_types"][conflict_type] += 1

        # Identify affected areas
        if self.conflicting_matrix_cells:
            report["affected_areas"].append("Matrix cell relationships")
        if self.institutional_contradictions:
            report["affected_areas"].append("Institutional arrangements")
        if self.value_system_conflicts:
            report["affected_areas"].append("Value system alignment")

        # Generate recommendations
        for conflict_id, mechanisms in self.mediation_mechanisms.items():
            if mechanisms:
                report["resolution_recommendations"].append(f"Conflict {conflict_id}: {mechanisms[0]}")

        return report
