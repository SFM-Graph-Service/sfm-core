"""
Unit tests for system_analysis module.
"""

import pytest
from uuid import uuid4
from datetime import datetime
from models.system_analysis import (
    SystemProperty,
    SystemLevelAnalysis,
    InstitutionalHolarchy,
)
from models.sfm_enums import SystemPropertyType, InstitutionalLevel, SystemArchetype


class TestSystemProperty:
    """Test suite for SystemProperty class."""

    def test_system_property_instantiation(self):
        """Test basic SystemProperty creation."""
        prop = SystemProperty(label="Test Property")
        assert prop.label == "Test Property"

    def test_system_property_with_type(self):
        """Test SystemProperty with property type."""
        prop = SystemProperty(label="Dynamic", property_type=SystemPropertyType.DYNAMIC)
        assert prop.property_type == SystemPropertyType.DYNAMIC

    def test_system_property_with_manifestation(self):
        """Test SystemProperty with value and unit."""
        prop = SystemProperty(
            label="Resilience",
            value=0.85,
            unit="score",
        )
        assert prop.value == 0.85
        assert prop.unit == "score"

    def test_system_property_with_mechanism(self):
        """Test SystemProperty with affected nodes."""
        node_ids = [uuid4(), uuid4()]
        prop = SystemProperty(
            label="Adaptation",
            affected_nodes=node_ids,
        )
        assert len(prop.affected_nodes) == 2

    def test_system_property_with_evidence(self):
        """Test SystemProperty with timestamp."""
        timestamp = datetime.now()
        prop = SystemProperty(
            label="Stability",
            timestamp=timestamp,
        )
        assert prop.timestamp == timestamp

    def test_system_property_with_measurement(self):
        """Test SystemProperty with contributing relationships."""
        rel_ids = [uuid4(), uuid4()]
        prop = SystemProperty(
            label="Complexity",
            contributing_relationships=rel_ids,
        )
        assert len(prop.contributing_relationships) == 2

    def test_system_property_with_level(self):
        """Test SystemProperty with value."""
        prop = SystemProperty(
            label="Macro Property",
            value=0.75,
        )
        assert prop.value == 0.75

    def test_system_property_complete(self):
        """Test SystemProperty with all fields."""
        node_ids = [uuid4() for _ in range(2)]
        rel_ids = [uuid4() for _ in range(2)]
        timestamp = datetime.now()
        prop = SystemProperty(
            label="Complete Property",
            description="Fully specified property",
            property_type=SystemPropertyType.STRUCTURAL,
            value=0.9,
            unit="index",
            timestamp=timestamp,
            affected_nodes=node_ids,
            contributing_relationships=rel_ids,
        )
        assert prop.label == "Complete Property"
        assert prop.property_type == SystemPropertyType.STRUCTURAL
        assert prop.value == 0.9


class TestSystemLevelAnalysis:
    """Test suite for SystemLevelAnalysis class."""

    def test_system_level_analysis_instantiation(self):
        """Test basic SystemLevelAnalysis creation."""
        analysis = SystemLevelAnalysis(
            label="Test Analysis", analyzed_system_boundary="Regional education system"
        )
        assert analysis.label == "Test Analysis"
        assert analysis.analyzed_system_boundary == "Regional education system"

    def test_analysis_with_level(self):
        """Test SystemLevelAnalysis with institutions analyzed."""
        inst_ids = [uuid4(), uuid4()]
        analysis = SystemLevelAnalysis(
            label="Micro Analysis",
            analyzed_system_boundary="Local community",
            institutions_analyzed=inst_ids,
        )
        assert len(analysis.institutions_analyzed) == 2

    def test_analysis_with_focus(self):
        """Test SystemLevelAnalysis with actors analyzed."""
        actor_ids = [uuid4(), uuid4()]
        analysis = SystemLevelAnalysis(
            label="Focused Analysis",
            analyzed_system_boundary="Policy network",
            actors_analyzed=actor_ids,
        )
        assert len(analysis.actors_analyzed) == 2

    def test_analysis_with_framework(self):
        """Test SystemLevelAnalysis with system coherence."""
        analysis = SystemLevelAnalysis(
            label="Framed Analysis",
            analyzed_system_boundary="Healthcare system",
            system_coherence=0.85,
        )
        assert analysis.system_coherence == 0.85

    def test_analysis_with_methods(self):
        """Test SystemLevelAnalysis with system resilience."""
        analysis = SystemLevelAnalysis(
            label="Methodological",
            analyzed_system_boundary="Transport network",
            system_resilience=0.72,
        )
        assert analysis.system_resilience == 0.72

    def test_analysis_with_findings(self):
        """Test SystemLevelAnalysis with system adaptability."""
        analysis = SystemLevelAnalysis(
            label="Complete Study",
            analyzed_system_boundary="Energy grid",
            system_adaptability=0.68,
        )
        assert analysis.system_adaptability == 0.68

    def test_analysis_with_links(self):
        """Test SystemLevelAnalysis with bottlenecks."""
        bottleneck_ids = [uuid4(), uuid4()]
        analysis = SystemLevelAnalysis(
            label="Linked",
            analyzed_system_boundary="Supply chain",
            system_bottlenecks=bottleneck_ids,
        )
        assert len(analysis.system_bottlenecks) == 2

    def test_analysis_complete(self):
        """Test SystemLevelAnalysis with all fields."""
        inst_ids = [uuid4() for _ in range(3)]
        actor_ids = [uuid4() for _ in range(2)]
        bottlenecks = [uuid4()]
        leverage = [uuid4()]
        feedback_loops = [uuid4()]

        analysis = SystemLevelAnalysis(
            label="Complete Analysis",
            description="Multi-level study",
            analyzed_system_boundary="National economy",
            institutions_analyzed=inst_ids,
            actors_analyzed=actor_ids,
            system_coherence=0.78,
            system_resilience=0.82,
            system_adaptability=0.71,
            system_efficiency=0.85,
            system_sustainability=0.69,
            system_bottlenecks=bottlenecks,
            leverage_points=leverage,
            dominant_feedback_loops=feedback_loops,
            system_archetypes=[SystemArchetype.LIMITS_TO_GROWTH],
        )
        assert analysis.label == "Complete Analysis"
        assert len(analysis.institutions_analyzed) == 3
        assert analysis.system_coherence == 0.78


class TestInstitutionalHolarchy:
    """Test suite for InstitutionalHolarchy class."""

    def test_holarchy_instantiation(self):
        """Test basic InstitutionalHolarchy creation."""
        holarchy = InstitutionalHolarchy(label="Test Holarchy")
        assert holarchy.label == "Test Holarchy"
        assert holarchy.institutional_levels == {}

    def test_holarchy_with_single_layer(self):
        """Test InstitutionalHolarchy with one layer."""
        inst_ids = [uuid4()]
        holarchy = InstitutionalHolarchy(
            label="Single Layer",
            institutional_levels={InstitutionalLevel.OPERATIONAL: inst_ids},
        )
        assert len(holarchy.institutional_levels) == 1
        assert InstitutionalLevel.OPERATIONAL in holarchy.institutional_levels

    def test_holarchy_with_multiple_layers(self):
        """Test InstitutionalHolarchy with multiple layers."""
        levels_map = {
            InstitutionalLevel.CONSTITUTIONAL: [uuid4()],
            InstitutionalLevel.COLLECTIVE_CHOICE: [uuid4()],
            InstitutionalLevel.OPERATIONAL: [uuid4()],
        }
        holarchy = InstitutionalHolarchy(
            label="Multi Layer",
            institutional_levels=levels_map,
        )
        assert len(holarchy.institutional_levels) == 3

    def test_holarchy_with_nesting(self):
        """Test InstitutionalHolarchy with emergence patterns."""
        holarchy = InstitutionalHolarchy(
            label="Nested",
            emergence_patterns=["Hierarchical governance structure"],
        )
        assert len(holarchy.emergence_patterns) == 1

    def test_holarchy_with_interactions(self):
        """Test InstitutionalHolarchy with level interactions."""
        interactions = {
            "constitutional_to_collective": {"influence": 0.8},
            "collective_to_operational": {"influence": 0.7},
        }
        holarchy = InstitutionalHolarchy(
            label="Interactive",
            level_interactions=interactions,
        )
        assert len(holarchy.level_interactions) == 2

    def test_holarchy_with_dynamics(self):
        """Test InstitutionalHolarchy with constraint flows."""
        constraints = {
            "top_down": ["Regulatory requirements", "Budget allocations"],
        }
        holarchy = InstitutionalHolarchy(
            label="Dynamic",
            constraint_flows=constraints,
        )
        assert "top_down" in holarchy.constraint_flows

    def test_holarchy_with_boundary(self):
        """Test InstitutionalHolarchy with power concentration."""
        power_dist = {
            InstitutionalLevel.CONSTITUTIONAL: 0.7,
            InstitutionalLevel.OPERATIONAL: 0.3,
        }
        holarchy = InstitutionalHolarchy(
            label="Bounded",
            power_concentration=power_dist,
        )
        assert holarchy.power_concentration[InstitutionalLevel.CONSTITUTIONAL] == 0.7

    def test_holarchy_complete(self):
        """Test InstitutionalHolarchy with all fields."""
        levels_map = {
            InstitutionalLevel.CONSTITUTIONAL: [uuid4()],
            InstitutionalLevel.COLLECTIVE_CHOICE: [uuid4()],
            InstitutionalLevel.OPERATIONAL: [uuid4()],
        }
        interactions = {"const_to_coll": {"strength": 0.8}}
        power_dist = {
            InstitutionalLevel.CONSTITUTIONAL: 0.6,
            InstitutionalLevel.COLLECTIVE_CHOICE: 0.3,
            InstitutionalLevel.OPERATIONAL: 0.1,
        }

        holarchy = InstitutionalHolarchy(
            label="Complete Holarchy",
            description="Full institutional structure",
            institutional_levels=levels_map,
            level_interactions=interactions,
            power_concentration=power_dist,
            emergence_patterns=["Three-tier structure"],
            constraint_flows={"top_down": ["Regulations"]},
            hierarchical_coherence=0.85,
        )
        assert holarchy.label == "Complete Holarchy"
        assert len(holarchy.institutional_levels) == 3
        assert holarchy.hierarchical_coherence == 0.85
