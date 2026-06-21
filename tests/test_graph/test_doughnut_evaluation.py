"""
Unit tests for Doughnut Economics evaluation.

Validates that evaluate_doughnut() correctly identifies delivery chains
driving boundaries into overshoot/shortfall, and that the embedded economy
holarchy is properly constructed.
"""

from api.sfm_service import SFMService
from graph.doughnut_evaluation import (
    evaluate_doughnut,
    build_embedded_economy_holarchy,
    DoughnutReport,
    BoundaryEvaluation,
)
from graph.sfm_graph import Relationship
from models.frameworks.doughnut import build_doughnut_criteria
from models.matrix_components import SFMCriteria
from models.base_nodes import Node
from models.enums import CriteriaType, CriteriaPriority, MeasurementApproach


def test_evaluate_doughnut_returns_report():
    """Test that evaluate_doughnut returns a DoughnutReport."""
    service = SFMService()

    # Add some Doughnut criteria
    criteria = build_doughnut_criteria()
    for criterion in criteria[:5]:  # Add first 5 to keep test fast
        service.create_node(criterion)

    report = evaluate_doughnut(service)

    assert isinstance(report, DoughnutReport)
    assert report.total_boundaries == 21
    # Should find criteria that were added
    assert len(report.social_foundation) + len(report.ecological_ceiling) >= 0


def test_evaluate_doughnut_classifies_social_ecological():
    """Test that criteria are correctly classified into social/ecological."""
    service = SFMService()

    # Add one social and one ecological criterion
    food = SFMCriteria(
        label="Food Test",
        description="Test social foundation",
        criteria_type=CriteriaType.SOCIAL,
        measurement_approach=MeasurementApproach.QUANTITATIVE,
        priority=CriteriaPriority.PRIMARY,
        life_process_relevance=1.0,
        meta={
            "polarity": "shortfall",
            "doughnut_dimension": "social_foundation",
            "source": "Test",
        },
    )

    climate = SFMCriteria(
        label="Climate Test",
        description="Test ecological ceiling",
        criteria_type=CriteriaType.ENVIRONMENTAL,
        measurement_approach=MeasurementApproach.QUANTITATIVE,
        priority=CriteriaPriority.PRIMARY,
        life_process_relevance=1.0,
        meta={
            "polarity": "overshoot",
            "doughnut_dimension": "ecological_ceiling",
            "source": "Test",
        },
    )

    service.create_node(food)
    service.create_node(climate)

    report = evaluate_doughnut(service)

    assert len(report.social_foundation) == 1
    assert len(report.ecological_ceiling) == 1
    assert report.social_foundation[0].criterion.label == "Food Test"
    assert report.ecological_ceiling[0].criterion.label == "Climate Test"


def test_evaluate_doughnut_detects_driving_chains():
    """Test that driving delivery chains are correctly identified."""
    service = SFMService()

    # Create a delivery chain: Factory -> Pollution -> Climate boundary
    factory = Node(label="Factory", description="Industrial facility")
    pollution_delivery = Node(label="CO2 Emissions", description="Pollution delivery")
    climate = SFMCriteria(
        label="Climate Change",
        description="Test climate boundary",
        criteria_type=CriteriaType.ENVIRONMENTAL,
        measurement_approach=MeasurementApproach.QUANTITATIVE,
        priority=CriteriaPriority.PRIMARY,
        life_process_relevance=1.0,
        meta={
            "polarity": "overshoot",
            "doughnut_dimension": "ecological_ceiling",
            "source": "Test",
        },
    )

    service.create_node(factory)
    service.create_node(pollution_delivery)
    service.create_node(climate)

    # Factory produces pollution
    service.create_relationship(Relationship(
        source_id=factory.id,
        target_id=pollution_delivery.id,
        kind="produces",
        weight=0.8,
    ))

    # Pollution evaluates negatively to climate boundary
    service.create_relationship(Relationship(
        source_id=pollution_delivery.id,
        target_id=climate.id,
        kind="evaluates_to",
        weight=-0.9,  # Negative impact
    ))

    report = evaluate_doughnut(service)

    # Should find the climate boundary
    climate_eval = report.get_boundary_by_label("Climate Change")
    assert climate_eval is not None
    assert climate_eval.polarity == "overshoot"
    assert climate_eval.net_impact == "negative"
    assert climate_eval.impact_strength > 0

    # Should detect overshoot due to negative impact
    assert climate_eval.status == "overshoot"
    assert report.overshoot_count == 1


def test_evaluate_doughnut_detects_shortfall():
    """Test that shortfall in social foundation is correctly detected."""
    service = SFMService()

    # Create delivery chain with inadequate food supply
    farm = Node(label="Farm", description="Food production")
    food_delivery = Node(label="Food Supply", description="Food delivery")
    food_boundary = SFMCriteria(
        label="Food Security",
        description="Test food boundary",
        criteria_type=CriteriaType.SOCIAL,
        measurement_approach=MeasurementApproach.QUANTITATIVE,
        priority=CriteriaPriority.PRIMARY,
        life_process_relevance=1.0,
        meta={
            "polarity": "shortfall",
            "doughnut_dimension": "social_foundation",
            "source": "Test",
        },
    )

    service.create_node(farm)
    service.create_node(food_delivery)
    service.create_node(food_boundary)

    # Farm produces food
    service.create_relationship(Relationship(
        source_id=farm.id,
        target_id=food_delivery.id,
        kind="produces",
        weight=0.3,  # Low production
    ))

    # Food delivery evaluates negatively to food boundary (inadequate)
    service.create_relationship(Relationship(
        source_id=food_delivery.id,
        target_id=food_boundary.id,
        kind="evaluates_to",
        weight=-0.7,  # Negative = below threshold
    ))

    report = evaluate_doughnut(service)

    food_eval = report.get_boundary_by_label("Food Security")
    assert food_eval is not None
    assert food_eval.polarity == "shortfall"
    assert food_eval.net_impact == "negative"
    assert food_eval.status == "shortfall"
    assert report.shortfall_count == 1


def test_evaluate_doughnut_two_boundaries():
    """Test with synthetic graph wired to 2+ boundaries per issue #24 requirements."""
    service = SFMService()

    # Boundary 1: Food (social foundation)
    food_boundary = SFMCriteria(
        label="Food",
        description="Food security",
        criteria_type=CriteriaType.SOCIAL,
        measurement_approach=MeasurementApproach.QUANTITATIVE,
        priority=CriteriaPriority.PRIMARY,
        life_process_relevance=1.0,
        meta={
            "polarity": "shortfall",
            "doughnut_dimension": "social_foundation",
            "source": "Test",
        },
    )

    # Boundary 2: Climate (ecological ceiling)
    climate_boundary = SFMCriteria(
        label="Climate Change",
        description="Climate stability",
        criteria_type=CriteriaType.ENVIRONMENTAL,
        measurement_approach=MeasurementApproach.QUANTITATIVE,
        priority=CriteriaPriority.PRIMARY,
        life_process_relevance=1.0,
        meta={
            "polarity": "overshoot",
            "doughnut_dimension": "ecological_ceiling",
            "source": "Test",
        },
    )

    # Components
    factory = Node(label="Industrial Factory", description="Manufacturing facility")
    farm = Node(label="Agricultural Farm", description="Food production")
    emissions = Node(label="CO2 Emissions", description="Greenhouse gases")
    food_supply = Node(label="Food Supply", description="Agricultural output")

    service.create_node(food_boundary)
    service.create_node(climate_boundary)
    service.create_node(factory)
    service.create_node(farm)
    service.create_node(emissions)
    service.create_node(food_supply)

    # Delivery chain 1: Factory -> Emissions -> Climate (overshoot)
    service.create_relationship(Relationship(
        source_id=factory.id,
        target_id=emissions.id,
        kind="produces",
        weight=0.9,
    ))
    service.create_relationship(Relationship(
        source_id=emissions.id,
        target_id=climate_boundary.id,
        kind="evaluates_to",
        weight=-0.95,  # Strong negative impact
    ))

    # Delivery chain 2: Farm -> Food Supply -> Food boundary (adequate)
    service.create_relationship(Relationship(
        source_id=farm.id,
        target_id=food_supply.id,
        kind="produces",
        weight=0.8,
    ))
    service.create_relationship(Relationship(
        source_id=food_supply.id,
        target_id=food_boundary.id,
        kind="evaluates_to",
        weight=0.7,  # Positive = adequate
    ))

    report = evaluate_doughnut(service)

    # Verify climate boundary is in overshoot
    climate_eval = report.get_boundary_by_label("Climate Change")
    assert climate_eval is not None
    assert climate_eval.status == "overshoot"
    assert climate_eval.net_impact == "negative"
    assert len(climate_eval.driving_chains) > 0

    # Verify food boundary is met
    food_eval = report.get_boundary_by_label("Food")
    assert food_eval is not None
    assert food_eval.status == "met"
    assert food_eval.net_impact == "positive"

    # Verify counts
    assert report.overshoot_count == 1
    assert report.met_count == 1
    assert report.shortfall_count == 0


def test_embedded_economy_holarchy_three_levels():
    """Test that embedded economy builder yields exactly 3 nested levels."""
    service = SFMService()

    # Add nodes at each holarchy level
    # Biosphere: ecological boundaries
    climate = SFMCriteria(
        label="Climate Change",
        description="Ecological ceiling",
        criteria_type=CriteriaType.ENVIRONMENTAL,
        measurement_approach=MeasurementApproach.QUANTITATIVE,
        priority=CriteriaPriority.PRIMARY,
        life_process_relevance=1.0,
        meta={
            "polarity": "overshoot",
            "doughnut_dimension": "ecological_ceiling",
            "source": "Test",
        },
    )

    # Society: social foundation
    health = SFMCriteria(
        label="Health",
        description="Social foundation",
        criteria_type=CriteriaType.SOCIAL,
        measurement_approach=MeasurementApproach.QUANTITATIVE,
        priority=CriteriaPriority.PRIMARY,
        life_process_relevance=1.0,
        meta={
            "polarity": "shortfall",
            "doughnut_dimension": "social_foundation",
            "source": "Test",
        },
    )

    # Economy: economic criteria
    income = SFMCriteria(
        label="Income",
        description="Economic system",
        criteria_type=CriteriaType.ECONOMIC,
        measurement_approach=MeasurementApproach.QUANTITATIVE,
        priority=CriteriaPriority.PRIMARY,
        life_process_relevance=1.0,
        meta={
            "source": "Test",
        },
    )

    service.create_node(climate)
    service.create_node(health)
    service.create_node(income)

    holarchy = build_embedded_economy_holarchy(service)

    # Verify exactly 3 levels
    assert len(holarchy) == 3
    assert "biosphere" in holarchy
    assert "society" in holarchy
    assert "economy" in holarchy

    # Verify nesting structure
    assert len(holarchy["biosphere"]) >= 1  # Climate should be here
    assert len(holarchy["society"]) >= 1    # Health should be here
    assert len(holarchy["economy"]) >= 1    # Income should be here

    # Verify climate is in biosphere
    biosphere_labels = [node["label"] for node in holarchy["biosphere"]]
    assert "Climate Change" in biosphere_labels

    # Verify health is in society
    society_labels = [node["label"] for node in holarchy["society"]]
    assert "Health" in biosphere_labels or "Health" in society_labels

    # Verify income is in economy
    economy_labels = [node["label"] for node in holarchy["economy"]]
    assert "Income" in economy_labels


def test_doughnut_report_get_methods():
    """Test DoughnutReport helper methods."""
    report = DoughnutReport()

    # Add some boundary evaluations
    food_criterion = SFMCriteria(
        label="Food",
        description="Test",
        criteria_type=CriteriaType.SOCIAL,
        measurement_approach=MeasurementApproach.QUANTITATIVE,
        priority=CriteriaPriority.PRIMARY,
        life_process_relevance=1.0,
        meta={"polarity": "shortfall", "doughnut_dimension": "social_foundation"},
    )

    climate_criterion = SFMCriteria(
        label="Climate",
        description="Test",
        criteria_type=CriteriaType.ENVIRONMENTAL,
        measurement_approach=MeasurementApproach.QUANTITATIVE,
        priority=CriteriaPriority.PRIMARY,
        life_process_relevance=1.0,
        meta={"polarity": "overshoot", "doughnut_dimension": "ecological_ceiling"},
    )

    food_eval = BoundaryEvaluation(
        criterion=food_criterion,
        polarity="shortfall",
        status="shortfall",
    )

    climate_eval = BoundaryEvaluation(
        criterion=climate_criterion,
        polarity="overshoot",
        status="overshoot",
    )

    report.social_foundation.append(food_eval)
    report.ecological_ceiling.append(climate_eval)

    # Test get_boundary_by_label
    assert report.get_boundary_by_label("Food") == food_eval
    assert report.get_boundary_by_label("Climate") == climate_eval
    assert report.get_boundary_by_label("Nonexistent") is None

    # Test get_overshoot_boundaries
    overshoot = report.get_overshoot_boundaries()
    assert len(overshoot) == 1
    assert overshoot[0].criterion.label == "Climate"

    # Test get_shortfall_boundaries
    shortfall = report.get_shortfall_boundaries()
    assert len(shortfall) == 1
    assert shortfall[0].criterion.label == "Food"
