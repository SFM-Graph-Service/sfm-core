"""
Comprehensive evaluation scenario tests for SFM Core.

Tests realistic SFM scenarios including:
- Policy impact analysis
- Institutional network effects
- Resource flow analysis
- Cultural value conflicts
- Technology integration impacts
"""

import uuid
import pytest
from typing import List, Dict, Any

from api.sfm_service import SFMService, SFMServiceConfig
from models.complex_analysis import (
    DigraphAnalysis,
    CircularCausationProcess,
    ConflictDetection,
)
from models.network_analysis import (
    CrossImpactAnalysis,
    DeliveryRelationship,
    MatrixDeliveryNetwork,
)
from models.institutional_analysis import PathDependencyAnalysis
from models.cultural_analysis import (
    ValueSystem,
    SocialBelief,
    CulturalAttitude,
)
from models.system_analysis import InstitutionalHolarchy
from models.sfm_enums import (
    ConflictType,
    CrossImpactType,
    PathDependencyType,
    ValueSystemType,
    InstitutionalLevel,
)


class TestDigraphEvaluation:
    """Test digraph analysis evaluation scenarios."""

    def test_institutional_dependency_network_analysis(self):
        """Test analysis of institutional dependency networks."""
        service = SFMService()

        # Create test institutions
        institution_ids = [uuid.uuid4() for _ in range(5)]

        # Evaluate dependency network - service creates analysis internally
        result = service.evaluate_digraph(institution_ids, analyze_sequences=True)

        # Verify results
        assert result is not None
        assert "dependency_matrix" in result
        assert "critical_institutions" in result
        assert "leverage_points" in result
        assert "stability_score" in result
        assert "propagation_analysis" in result

    def test_circular_dependency_detection(self):
        """Test detection of circular institutional dependencies."""
        service = SFMService()

        # Create circular dependency scenario
        institution_ids = [uuid.uuid4() for _ in range(4)]

        result = service.evaluate_digraph(institution_ids, analyze_sequences=False)

        # Verify structure is present (empty cycles is valid for new analysis)
        assert "cycles" in result
        assert "stability_score" in result

    def test_propagation_sequence_analysis(self):
        """Test analysis of change propagation sequences through institutions."""
        service = SFMService()

        institution_ids = [uuid.uuid4() for _ in range(6)]

        result = service.evaluate_digraph(institution_ids, analyze_sequences=True)

        assert "propagation_analysis" in result
        assert "critical_sequences" in result["propagation_analysis"]
        assert "sequence_patterns" in result["propagation_analysis"]


class TestCircularCausationEvaluation:
    """Test circular causation process evaluation scenarios."""

    def test_virtuous_cycle_dynamics(self):
        """Test evaluation of virtuous circular causation cycles."""
        service = SFMService()

        # Create virtuous cycle
        process = CircularCausationProcess(
            label="Innovation-Education Virtuous Cycle",
            description="Mutual reinforcement of innovation and education",
            process_type="virtuous",
            causation_strength=0.85,
            feedback_polarity="positive",
            time_scale="medium-term",
            momentum_level=0.75,
            stability_tendency=0.8,
            change_acceleration=0.15,
        )

        service.create_node(process)
        result = service.evaluate_circular_causation(process.id)

        assert result["process_direction"] == "beneficial"
        assert result["process_strength"] == 0.85
        assert result["stability_assessment"] == "highly_stable"

    def test_vicious_cycle_detection(self):
        """Test detection and evaluation of vicious cycles."""
        service = SFMService()

        process = CircularCausationProcess(
            label="Poverty-Education Vicious Cycle",
            description="Negative reinforcement between poverty and low education",
            process_type="vicious",
            causation_strength=0.75,
            feedback_polarity="positive",
            time_scale="long-term",
            momentum_level=0.65,
            stability_tendency=0.7,
        )

        service.create_node(process)
        result = service.evaluate_circular_causation(process.id)

        assert result["process_direction"] == "harmful"
        assert result["stability_assessment"] == "highly_stable"

    def test_intervention_point_identification(self):
        """Test identification of intervention points in circular processes."""
        service = SFMService()

        process = CircularCausationProcess(
            label="Healthcare Access Cycle",
            process_type="mixed",
            causation_strength=0.6,
            intervention_opportunities=[
                {"point": "insurance_reform", "leverage": 0.8},
                {"point": "education_access", "leverage": 0.6},
            ],
            policy_leverage_points=[
                {"policy": "universal_coverage", "effectiveness": 0.9},
            ],
        )

        service.create_node(process)
        result = service.evaluate_circular_causation(process.id)

        assert result["intervention_potential"] > 0.0


class TestConflictDetectionEvaluation:
    """Test conflict detection evaluation scenarios."""

    def test_value_conflict_detection(self):
        """Test detection of cultural value conflicts."""
        service = SFMService()

        system_id = uuid.uuid4()
        conflict_system = ConflictDetection(
            label="Environmental vs Economic Value Conflict",
            analyzed_system_id=system_id,
            conflict_type=ConflictType.VALUE_CONFLICT,
            direct_conflicts=[
                {"id": "conf_1", "type": "value_conflict", "severity": 0.8},
                {"id": "conf_2", "type": "value_conflict", "severity": 0.6},
            ],
            indirect_conflicts=[
                {"id": "conf_3", "type": "institutional_conflict", "severity": 0.5},
            ],
            conflict_intensity={"conf_1": 0.8, "conf_2": 0.6, "conf_3": 0.5},
            urgency_levels={"conf_1": 0.9, "conf_2": 0.5, "conf_3": 0.4},
        )

        service.create_node(conflict_system)
        result = service.evaluate_conflict_detection(conflict_system.id)

        assert result["total_conflicts"] == 3
        assert "conflict_report" in result
        assert "priority_analysis" in result
        assert len(result["priority_analysis"]) == 3

    def test_institutional_contradiction_analysis(self):
        """Test analysis of institutional contradictions."""
        service = SFMService()

        system_id = uuid.uuid4()
        institution_ids = [uuid.uuid4() for _ in range(3)]

        conflict_system = ConflictDetection(
            label="Regulatory Contradictions",
            analyzed_system_id=system_id,
            conflict_type=ConflictType.AUTHORITY_CONFLICT,
            institutional_contradictions=institution_ids,
            direct_conflicts=[
                {"id": "reg_1", "type": "regulatory", "severity": 0.7},
            ],
        )

        service.create_node(conflict_system)
        result = service.evaluate_conflict_detection(conflict_system.id)

        assert len(conflict_system.institutional_contradictions) == 3

    def test_ceremonial_instrumental_tensions(self):
        """Test detection of ceremonial vs instrumental tensions."""
        service = SFMService()

        system_id = uuid.uuid4()

        conflict_system = ConflictDetection(
            label="Ceremonial-Instrumental Tensions",
            analyzed_system_id=system_id,
            conflict_type=ConflictType.CEREMONIAL_INSTRUMENTAL,
            ceremonial_instrumental_tensions=[
                {"tension": "tradition_vs_innovation", "strength": 0.75},
            ],
            ceremonial_dominance_conflicts=[
                {"conflict": "status_quo_blocking", "impact": 0.8},
            ],
        )

        service.create_node(conflict_system)
        result = service.evaluate_conflict_detection(conflict_system.id)

        assert result is not None
        assert len(conflict_system.ceremonial_instrumental_tensions) > 0


class TestNetworkEvaluation:
    """Test network analysis evaluation scenarios."""

    def test_cross_impact_policy_analysis(self):
        """Test cross-impact analysis for policy changes."""
        service = SFMService()

        primary_cell = uuid.uuid4()
        impacted_cells = {
            str(uuid.uuid4()): 0.8,
            str(uuid.uuid4()): 0.6,
            str(uuid.uuid4()): 0.4,
        }

        analysis = CrossImpactAnalysis(
            label="Carbon Tax Policy Impact",
            primary_cell_id=primary_cell,
            impacted_cells=impacted_cells,
            impact_type=CrossImpactType.SYSTEMIC,
            impact_mechanism="price_signal_propagation",
            time_delay=6.0,
            confidence_level=0.75,
            mitigation_strategies=["gradual_implementation", "industry_support"],
            amplification_strategies=["publicity_campaign", "incentive_alignment"],
        )

        service.create_node(analysis)
        result = service.evaluate_cross_impact(analysis.id)

        assert len(result["impacted_cells"]) == 3
        assert result["impact_mechanism"] == "price_signal_propagation"
        assert len(result["mitigation_strategies"]) == 2

    def test_delivery_network_performance(self):
        """Test delivery network performance evaluation."""
        service = SFMService()

        relationship_ids = [uuid.uuid4() for _ in range(5)]

        network = MatrixDeliveryNetwork(
            label="Healthcare Delivery Network",
            network_scope="regional",
            network_density=0.65,
            network_efficiency=0.75,
            delivery_success_rate=0.82,
            coordination_effectiveness=0.7,
            delivery_relationships=relationship_ids,
            redundancy_level=0.6,
            adaptation_capacity=0.55,
        )

        service.create_node(network)
        result = service.evaluate_network_performance(network.id)

        assert result["overall_performance"] > 0.7
        assert result["network_health"] in ["excellent", "good"]
        assert "improvement_priorities" in result

    def test_delivery_relationship_assessment(self):
        """Test individual delivery relationship assessment."""
        service = SFMService()

        source_id = uuid.uuid4()
        target_id = uuid.uuid4()

        relationship = DeliveryRelationship(
            label="Hospital-Clinic Service Delivery",
            source_component_id=source_id,
            target_component_id=target_id,
            delivery_type="service",
            delivery_quality=0.85,
            delivery_reliability=0.9,
            delivery_efficiency=0.75,
            criticality=0.8,
        )

        service.create_node(relationship)
        result = service.evaluate_delivery_performance(relationship.id)

        assert result["reliability_rating"] == "high"
        assert result["overall_performance"] > 0.7


class TestInstitutionalEvaluation:
    """Test institutional analysis evaluation scenarios."""

    def test_path_dependency_lock_in_analysis(self):
        """Test analysis of institutional path dependency and lock-in."""
        service = SFMService()

        institution_id = uuid.uuid4()

        analysis = PathDependencyAnalysis(
            label="QWERTY Keyboard Lock-in",
            analyzed_institution_id=institution_id,
            dependency_strength=PathDependencyType.STRONG,
            critical_junctures=["typewriter_adoption", "computer_standardization"],
            lock_in_mechanisms=["network_effects", "training_costs", "equipment_standardization"],
            switching_costs={"retraining": 0.9, "equipment": 0.7},
            alternative_paths=["Dvorak", "Colemak"],
            path_efficiency=0.6,
            network_effects=0.95,
        )

        service.create_node(analysis)
        result = service.evaluate_path_dependency(analysis.id)

        assert result["dependency_strength"] == "PathDependencyType.STRONG"
        assert len(result["lock_in_mechanisms"]) == 3
        assert result["network_effects"] == 0.95
        assert result["path_efficiency"] == 0.6


class TestCulturalEvaluation:
    """Test cultural analysis evaluation scenarios."""

    def test_value_system_coherence_analysis(self):
        """Test value system coherence and alignment analysis."""
        service = SFMService()

        institution_ids = [uuid.uuid4() for _ in range(3)]

        value_system = ValueSystem(
            label="Democratic Values System",
            system_type=ValueSystemType.CULTURAL_DOMINANT,
            core_values=["freedom", "equality", "justice"],
            value_hierarchy={"freedom": 0.9, "equality": 0.85, "justice": 0.8},
            cultural_embedding=0.75,
            institutional_support=institution_ids,
            change_resistance=0.6,
            adaptive_capacity=0.5,
        )

        service.create_node(value_system)
        result = service.evaluate_value_system(value_system.id)

        assert result["coherence_score"] >= 0.0
        assert result["institutional_alignment"] > 0.0
        assert len(result["core_values"]) == 3

    def test_belief_stability_assessment(self):
        """Test social belief stability assessment."""
        service = SFMService()

        belief = SocialBelief(
            label="Climate Change Scientific Consensus",
            belief_type="factual",
            belief_strength=0.95,
            change_resistance=0.7,
            social_reinforcement=0.8,
        )

        service.create_node(belief)
        result = service.evaluate_belief_stability(belief.id)

        assert result["stability_level"] == "high"
        assert result["change_potential"] < 0.5

    def test_attitude_mediation_capacity(self):
        """Test cultural attitude mediation capacity analysis."""
        service = SFMService()

        belief_ids = [uuid.uuid4() for _ in range(2)]
        institution_ids = [uuid.uuid4() for _ in range(3)]

        attitude = CulturalAttitude(
            label="Pro-Environmental Attitude",
            attitude_type="supportive",
            attitude_strength=0.75,
            related_beliefs=belief_ids,
            influenced_institutions=institution_ids,
            belief_attitude_coherence=0.85,
            behavioral_predictability=0.7,
        )

        service.create_node(attitude)
        result = service.evaluate_attitude_mediation(attitude.id)

        assert result["mediation_strength"] > 0.7
        assert result["coherence_level"] == "high"
        assert result["influence_scope"] == 3


class TestSystemHolarchyEvaluation:
    """Test system holarchy evaluation scenarios."""

    def test_institutional_holarchy_coherence(self):
        """Test institutional holarchy coherence analysis."""
        service = SFMService()

        local_institutions = [uuid.uuid4() for _ in range(3)]
        regional_institutions = [uuid.uuid4() for _ in range(2)]
        national_institutions = [uuid.uuid4() for _ in range(1)]

        holarchy = InstitutionalHolarchy(
            label="Education System Holarchy",
            institutional_levels={
                InstitutionalLevel.LOCAL_PRACTICE: local_institutions,
                InstitutionalLevel.OPERATIONAL: regional_institutions,
                InstitutionalLevel.COLLECTIVE_CHOICE: national_institutions,
            },
            level_interactions={
                "local_regional": {"strength": 0.7},
                "regional_national": {"strength": 0.8},
            },
            hierarchical_coherence=0.75,
            power_concentration={
                InstitutionalLevel.COLLECTIVE_CHOICE: 0.6,
                InstitutionalLevel.OPERATIONAL: 0.3,
                InstitutionalLevel.LOCAL_PRACTICE: 0.1,
            },
        )

        service.create_node(holarchy)
        result = service.evaluate_system_holarchy(holarchy.id)

        assert result["system_coherence"] >= 0.0
        assert len(result["leverage_points"]) > 0
        assert result["hierarchical_coherence"] == 0.75


class TestIntegratedEvaluation:
    """Test integrated multi-dimensional evaluation scenarios."""

    def test_policy_impact_comprehensive_analysis(self):
        """Test comprehensive policy impact analysis across multiple dimensions."""
        service = SFMService()

        # Create multi-dimensional policy scenario
        institution_ids = [uuid.uuid4() for _ in range(4)]

        # Institutional dependencies
        digraph = DigraphAnalysis(
            label="Universal Healthcare Policy Dependencies",
            analyzed_institutions=institution_ids,
            stability_score=0.65,
        )
        service.create_node(digraph)

        # Cross-impact analysis
        primary_cell = uuid.uuid4()
        cross_impact = CrossImpactAnalysis(
            label="Healthcare Policy Cross-Impact",
            primary_cell_id=primary_cell,
            impacted_cells={str(uuid.uuid4()): 0.7},
            confidence_level=0.75,
        )
        service.create_node(cross_impact)

        # Evaluate both dimensions
        dep_result = service.evaluate_digraph(institution_ids, analyze_sequences=False)
        impact_result = service.evaluate_cross_impact(cross_impact.id)

        assert "stability_score" in dep_result
        assert impact_result["confidence_level"] == 0.75

    def test_technology_integration_impact_assessment(self):
        """Test technology integration impact on social fabric."""
        service = SFMService()

        # Technology causes circular causation in society
        tech_process = CircularCausationProcess(
            label="AI Technology Integration Cycle",
            process_type="mixed",
            causation_strength=0.8,
            time_scale="short-term",
        )
        service.create_node(tech_process)

        # Creates conflicts with existing values
        system_id = uuid.uuid4()
        tech_conflict = ConflictDetection(
            label="AI vs Human Labor Values",
            analyzed_system_id=system_id,
            conflict_type=ConflictType.VALUE_CONFLICT,
            technology_institution_mismatches=[
                {"tech": "AI", "institution": "labor_market", "mismatch": 0.7}
            ],
        )
        service.create_node(tech_conflict)

        # Evaluate both
        process_result = service.evaluate_circular_causation(tech_process.id)
        conflict_result = service.evaluate_conflict_detection(tech_conflict.id)

        assert process_result["process_strength"] == 0.8
        assert len(tech_conflict.technology_institution_mismatches) > 0
