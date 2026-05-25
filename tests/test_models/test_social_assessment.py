"""
Unit tests for social_assessment module.
"""

import pytest
from uuid import uuid4
from models.social_assessment import (
    SocialValueAssessment,
    SocialFabricIndicator,
    SocialCost,
)
from models.sfm_enums import SocialFabricIndicatorType, SocialCostType


class TestSocialValueAssessment:
    def test_instantiation(self):
        sva = SocialValueAssessment(assessed_entity_id=uuid4(), label="Test Assessment")
        assert sva.label == "Test Assessment"

    def test_with_dimension(self):
        entity_id = uuid4()
        sva = SocialValueAssessment(
            assessed_entity_id=entity_id, label="Life Process", life_process_impact=0.75
        )
        assert sva.life_process_impact == 0.75

    def test_with_assessment(self):
        sva = SocialValueAssessment(
            assessed_entity_id=uuid4(), label="Assessed", life_process_impact=0.85
        )
        assert sva.life_process_impact == 0.85

    def test_with_methodology(self):
        sva = SocialValueAssessment(
            assessed_entity_id=uuid4(),
            label="Methodical",
            description="Survey-based assessment",
        )
        assert sva.description == "Survey-based assessment"

    def test_with_stakeholders(self):
        sva = SocialValueAssessment(
            assessed_entity_id=uuid4(),
            label="Participatory",
            description="Stakeholder input collected",
        )
        assert sva.description == "Stakeholder input collected"

    def test_complete(self):
        entity_id = uuid4()
        sva = SocialValueAssessment(
            assessed_entity_id=entity_id,
            label="Complete",
            description="Full social value assessment",
            life_process_impact=0.8,
            community_continuity=0.7,
        )
        assert sva.label == "Complete"


class TestSocialFabricIndicator:
    def test_instantiation(self):
        sfi = SocialFabricIndicator(label="Test Indicator")
        assert sfi.label == "Test Indicator"

    def test_with_type(self):
        sfi = SocialFabricIndicator(
            label="Coherence",
            indicator_type=SocialFabricIndicatorType.INSTITUTIONAL_COHERENCE,
        )
        assert sfi.indicator_type == SocialFabricIndicatorType.INSTITUTIONAL_COHERENCE

    def test_with_metric(self):
        sfi = SocialFabricIndicator(label="Measured", current_value=0.65)
        assert sfi.current_value == 0.65

    def test_with_threshold(self):
        sfi = SocialFabricIndicator(label="Baseline", baseline_value=0.5)
        assert sfi.baseline_value == 0.5

    def test_with_trend(self):
        sfi = SocialFabricIndicator(label="Trending", description="Upward trend")
        assert sfi.description == "Upward trend"

    def test_complete(self):
        sfi = SocialFabricIndicator(
            label="Complete",
            description="Full indicator",
            indicator_type=SocialFabricIndicatorType.SOCIAL_INTEGRATION,
            current_value=0.72,
            baseline_value=0.65,
        )
        assert sfi.label == "Complete"


class TestSocialCost:
    def test_instantiation(self):
        sc = SocialCost(label="Test Cost")
        assert sc.label == "Test Cost"

    def test_with_type(self):
        sc = SocialCost(
            label="Environmental", cost_type=SocialCostType.ENVIRONMENTAL_DEGRADATION
        )
        assert sc.cost_type == SocialCostType.ENVIRONMENTAL_DEGRADATION

    def test_with_impact(self):
        sc = SocialCost(
            label="Impactful", description="Significant environmental impact"
        )
        assert sc.description == "Significant environmental impact"

    def test_with_populations(self):
        sc = SocialCost(
            label="Population Effect", description="Affects vulnerable populations"
        )
        assert sc.description == "Affects vulnerable populations"

    def test_complete(self):
        sc = SocialCost(
            label="Complete",
            description="Full social cost assessment",
            cost_type=SocialCostType.HEALTH_IMPACTS,
            estimated_cost=1000000.0,
            cost_unit="USD",
        )
        assert sc.label == "Complete"
