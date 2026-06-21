"""
Unit tests for criteria evaluation functionality (Issue #20).

Tests the evaluate_against_criteria function with fixture graphs containing
known delivery→criterion relationships.
"""

import pytest

from api.sfm_service import SFMService
from models import Node, SFMCriteria
from models.sfm_enums import CriteriaType, CriteriaPriority
from models.delivery_matrix import Delivery
from graph.criteria_evaluation import (
    EvaluationAlignment,
    evaluate_against_criteria,
    format_evaluation_report
)
from graph import Relationship


@pytest.fixture
def simple_fixture():
    """
    Create a simple fixture graph for criteria evaluation testing.

    Components:
    - institution_a (delivers to institution_b)
    - institution_b (receives delivery)
    - health_criterion (evaluates delivery)

    Matrix structure:
    - Cell (institution_a → institution_b) contains health delivery
    - Relationship links cell to health_criterion with positive weight
    """
    service = SFMService()

    # Create components
    institution_a = Node(
        label="Institution A",
        description="Delivers health services"
    )
    service.create_node(institution_a)

    institution_b = Node(
        label="Institution B",
        description="Receives health services"
    )
    service.create_node(institution_b)

    # Create health criterion
    health_criterion = SFMCriteria(
        label="Public Health",
        description="Protection of public health",
        criteria_type=CriteriaType.SOCIAL,
        priority=CriteriaPriority.PRIMARY,
        weight=1.0,
        life_process_relevance=0.95,
        instrumental_capacity=0.90,
        ceremonial_bias_risk=0.10,
        normative_justification="Protect public health"
    )
    service.create_node(health_criterion)

    # Create delivery matrix
    matrix = service.create_delivery_matrix(
        label="Test Matrix",
        description="Test delivery matrix",
        components=[institution_a.id, institution_b.id],
        matrix_scope="local"
    )

    # Add delivery to cell
    service.add_delivery_to_matrix(
        matrix,
        institution_a.id,
        institution_b.id,
        Delivery(
            delivery_type="health_service",
            delivery_content="Primary care clinic provides healthcare to community",
            quantity=1000,
            units="patient visits/year",
            temporal_rate="annual",
            certainty=0.95
        ),
        cell_description="Institution A provides health services to Institution B"
    )

    # Link cell to criterion with positive weight (SERVES)
    cell = matrix.get_cell(institution_a.id, institution_b.id)
    service.create_relationship(
        Relationship(
            source_id=cell.id,
            target_id=health_criterion.id,
            kind="evaluates_to",
            weight=0.90  # Positive weight = serves criterion
        )
    )

    return service, matrix, health_criterion, institution_a, institution_b


@pytest.fixture
def multi_delivery_fixture():
    """
    Create fixture with multiple deliveries per cell.

    Tests that evaluation handles multiple heterogeneous deliveries correctly.
    """
    service = SFMService()

    # Create components
    provider = Node(label="Healthcare Provider", description="Medical services provider")
    service.create_node(provider)

    community = Node(label="Community", description="Local community")
    service.create_node(community)

    # Create criteria
    health_criterion = SFMCriteria(
        label="Health Protection",
        description="Protect community health",
        criteria_type=CriteriaType.SOCIAL,
        priority=CriteriaPriority.PRIMARY,
        weight=1.0
    )
    service.create_node(health_criterion)

    equity_criterion = SFMCriteria(
        label="Health Equity",
        description="Equitable health access",
        criteria_type=CriteriaType.SOCIAL,
        priority=CriteriaPriority.PRIMARY,
        weight=0.9
    )
    service.create_node(equity_criterion)

    # Create matrix
    matrix = service.create_delivery_matrix(
        label="Healthcare Matrix",
        components=[provider.id, community.id]
    )

    # Add multiple deliveries to same cell
    service.add_delivery_to_matrix(
        matrix,
        provider.id,
        community.id,
        Delivery(
            delivery_type="health_service",
            delivery_content="Primary care services",
            quantity=5000,
            units="visits/year"
        ),
        cell_description="Provider delivers multiple health services to community"
    )

    service.add_delivery_to_matrix(
        matrix,
        provider.id,
        community.id,
        Delivery(
            delivery_type="health_service",
            delivery_content="Preventive care programs",
            quantity=2000,
            units="screenings/year"
        ),
        cell_description="Provider delivers multiple health services to community"
    )

    # Link cell to both criteria
    cell = matrix.get_cell(provider.id, community.id)
    service.create_relationship(
        Relationship(
            source_id=cell.id,
            target_id=health_criterion.id,
            kind="evaluates_to",
            weight=0.95
        )
    )
    service.create_relationship(
        Relationship(
            source_id=cell.id,
            target_id=equity_criterion.id,
            kind="evaluates_to",
            weight=0.85
        )
    )

    return service, matrix, health_criterion, equity_criterion


@pytest.fixture
def undermining_fixture():
    """
    Create fixture with deliveries that UNDERMINE criteria.

    Tests negative relationship weights (undermining alignment).
    """
    service = SFMService()

    # Create components
    polluter = Node(label="Industrial Facility", description="Polluting facility")
    service.create_node(polluter)

    community = Node(label="Community", description="Nearby community")
    service.create_node(community)

    # Create environmental health criterion
    env_health = SFMCriteria(
        label="Environmental Health",
        description="Clean air and water",
        criteria_type=CriteriaType.ENVIRONMENTAL,
        priority=CriteriaPriority.PRIMARY,
        weight=1.0
    )
    service.create_node(env_health)

    # Create matrix
    matrix = service.create_delivery_matrix(
        label="Pollution Matrix",
        components=[polluter.id, community.id]
    )

    # Add pollution delivery
    service.add_delivery_to_matrix(
        matrix,
        polluter.id,
        community.id,
        Delivery(
            delivery_type="pollution",
            delivery_content="Air pollution from industrial emissions",
            quantity=500,
            units="tons/year",
            certainty=0.90
        ),
        cell_description="Industrial facility pollutes nearby community"
    )

    # Link cell to criterion with NEGATIVE weight (UNDERMINES)
    cell = matrix.get_cell(polluter.id, community.id)
    service.create_relationship(
        Relationship(
            source_id=cell.id,
            target_id=env_health.id,
            kind="evaluates_to",
            weight=-0.85  # Negative weight = undermines criterion
        )
    )

    return service, matrix, env_health, polluter, community


def test_evaluate_simple_serving_delivery(simple_fixture):
    """Test evaluation of single delivery that serves a criterion."""
    service, matrix, health_criterion, institution_a, institution_b = simple_fixture

    # Evaluate
    results = evaluate_against_criteria(service)

    # Assertions
    assert len(results) == 1, "Should have one criterion result"
    assert health_criterion.id in results

    result = results[health_criterion.id]
    assert result.criterion_label == "Public Health"
    assert result.criterion_type == str(CriteriaType.SOCIAL.value)
    assert result.priority == str(CriteriaPriority.PRIMARY.value)

    # Check serving deliveries
    assert result.serving_delivery_count == 1
    assert len(result.serving_deliveries) == 1
    assert result.undermining_delivery_count == 0
    assert len(result.undermining_deliveries) == 0

    # Check delivery details
    serving_delivery = result.serving_deliveries[0]
    assert serving_delivery.alignment == EvaluationAlignment.SERVES
    assert serving_delivery.alignment_strength == 0.90  # Matches relationship weight
    assert serving_delivery.delivery_type == "health_service"
    assert "healthcare" in serving_delivery.delivery_content.lower()

    # Check aggregate score (should be positive)
    assert result.overall_alignment_score > 0
    assert result.overall_alignment_score <= 1.0


def test_evaluate_undermining_delivery(undermining_fixture):
    """Test evaluation of delivery that undermines a criterion."""
    service, matrix, env_health, polluter, community = undermining_fixture

    # Evaluate
    results = evaluate_against_criteria(service)

    # Assertions
    assert len(results) == 1
    assert env_health.id in results

    result = results[env_health.id]

    # Check undermining deliveries
    assert result.undermining_delivery_count == 1
    assert len(result.undermining_deliveries) == 1
    assert result.serving_delivery_count == 0

    # Check delivery details
    undermining_delivery = result.undermining_deliveries[0]
    assert undermining_delivery.alignment == EvaluationAlignment.UNDERMINES
    assert undermining_delivery.alignment_strength == 0.85  # Abs value of -0.85
    assert undermining_delivery.delivery_type == "pollution"

    # Check aggregate score (should be negative)
    assert result.overall_alignment_score < 0
    assert result.overall_alignment_score >= -1.0

    # Check recommendations
    assert len(result.recommendations) > 0
    assert any("negative" in rec.lower() for rec in result.recommendations)


def test_evaluate_multiple_deliveries_per_cell(multi_delivery_fixture):
    """Test evaluation handles multiple deliveries in single cell."""
    service, matrix, health_criterion, equity_criterion = multi_delivery_fixture

    # Evaluate
    results = evaluate_against_criteria(service)

    # Should have results for both criteria
    assert len(results) == 2
    assert health_criterion.id in results
    assert equity_criterion.id in results

    # Both should have serving deliveries from same cell
    health_result = results[health_criterion.id]
    equity_result = results[equity_criterion.id]

    # Each criterion sees both deliveries from the cell
    assert health_result.serving_delivery_count == 2
    assert equity_result.serving_delivery_count == 2

    # Check alignment scores are positive
    assert health_result.overall_alignment_score > 0
    assert equity_result.overall_alignment_score > 0


def test_evaluate_no_criteria():
    """Test evaluation with no criteria returns empty results."""
    service = SFMService()

    # Create matrix with no criteria
    inst_a = Node(label="A", description="Institution A")
    service.create_node(inst_a)
    inst_b = Node(label="B", description="Institution B")
    service.create_node(inst_b)

    matrix = service.create_delivery_matrix(
        label="Matrix",
        components=[inst_a.id, inst_b.id]
    )

    service.add_delivery_to_matrix(
        matrix,
        inst_a.id,
        inst_b.id,
        Delivery(delivery_type="test", delivery_content="Test delivery"),
        cell_description="Test"
    )

    # Evaluate - should return empty
    results = evaluate_against_criteria(service)
    assert len(results) == 0


def test_evaluate_unlinked_criterion():
    """Test criterion with no linked deliveries."""
    service = SFMService()

    # Create criterion but no deliveries linked to it
    criterion = SFMCriteria(
        label="Unlinked Criterion",
        description="Not linked to any deliveries",
        criteria_type=CriteriaType.SOCIAL,
        priority=CriteriaPriority.SECONDARY,
        weight=0.5
    )
    service.create_node(criterion)

    # Create some deliveries (but don't link to criterion)
    inst_a = Node(label="A", description="A")
    service.create_node(inst_a)
    inst_b = Node(label="B", description="B")
    service.create_node(inst_b)

    matrix = service.create_delivery_matrix(
        label="Matrix",
        components=[inst_a.id, inst_b.id]
    )

    service.add_delivery_to_matrix(
        matrix,
        inst_a.id,
        inst_b.id,
        Delivery(delivery_type="test", delivery_content="Test"),
        cell_description="Test"
    )

    # Evaluate
    results = evaluate_against_criteria(service)

    # Should have criterion result with zero deliveries
    assert criterion.id in results
    result = results[criterion.id]
    assert result.serving_delivery_count == 0
    assert result.undermining_delivery_count == 0
    assert result.overall_alignment_score == 0.0


def test_format_evaluation_report(simple_fixture):
    """Test that format_evaluation_report produces valid output."""
    service, matrix, health_criterion, _, _ = simple_fixture

    results = evaluate_against_criteria(service)
    report_text = format_evaluation_report(results, include_details=True)

    # Check report contains key sections
    assert "CRITERIA EVALUATION REPORT" in report_text
    assert "Public Health" in report_text
    assert "Overall Alignment Score" in report_text
    assert "Serving Deliveries" in report_text

    # Check detail formatting
    assert "health_service" in report_text  # Delivery type
    assert "healthcare" in report_text.lower()  # Delivery content


def test_format_evaluation_report_no_details(simple_fixture):
    """Test report formatting without delivery details."""
    service, matrix, health_criterion, _, _ = simple_fixture

    results = evaluate_against_criteria(service)
    report_text = format_evaluation_report(results, include_details=False)

    # Should have summary but not delivery details
    assert "CRITERIA EVALUATION REPORT" in report_text
    assert "Overall Alignment Score" in report_text
    # Should NOT have individual delivery listings
    assert "✓" not in report_text


def test_format_empty_results():
    """Test formatting with no results."""
    results = {}
    report_text = format_evaluation_report(results)

    assert "No criteria evaluation results available" in report_text


def test_evaluation_with_neutral_weight():
    """Test delivery with near-zero weight classified as NEUTRAL."""
    service = SFMService()

    inst_a = Node(label="A", description="A")
    service.create_node(inst_a)
    inst_b = Node(label="B", description="B")
    service.create_node(inst_b)

    criterion = SFMCriteria(
        label="Test Criterion",
        description="Test",
        criteria_type=CriteriaType.SOCIAL,
        priority=CriteriaPriority.TERTIARY,
        weight=0.5
    )
    service.create_node(criterion)

    matrix = service.create_delivery_matrix(
        label="Matrix",
        components=[inst_a.id, inst_b.id]
    )

    service.add_delivery_to_matrix(
        matrix,
        inst_a.id,
        inst_b.id,
        Delivery(delivery_type="test", delivery_content="Minimal impact delivery"),
        cell_description="Test"
    )

    # Link with very small weight (NEUTRAL)
    cell = matrix.get_cell(inst_a.id, inst_b.id)
    service.create_relationship(
        Relationship(
            source_id=cell.id,
            target_id=criterion.id,
            kind="evaluates_to",
            weight=0.05  # Very small positive weight
        )
    )

    results = evaluate_against_criteria(service)
    result = results[criterion.id]

    # Should be classified as NEUTRAL (weight between -0.1 and 0.1)
    assert len(result.neutral_deliveries) == 1
    assert result.neutral_deliveries[0].alignment == EvaluationAlignment.NEUTRAL


def test_evaluation_aggregate_calculations():
    """Test that aggregate scores and analysis are calculated correctly."""
    service = SFMService()

    inst_a = Node(label="A", description="A")
    service.create_node(inst_a)
    inst_b = Node(label="B", description="B")
    service.create_node(inst_b)
    inst_c = Node(label="C", description="C")
    service.create_node(inst_c)

    criterion = SFMCriteria(
        label="Test Criterion",
        description="Test",
        criteria_type=CriteriaType.ECONOMIC,
        priority=CriteriaPriority.PRIMARY,
        weight=1.0
    )
    service.create_node(criterion)

    matrix = service.create_delivery_matrix(
        label="Matrix",
        components=[inst_a.id, inst_b.id, inst_c.id]
    )

    # Add one serving delivery
    service.add_delivery_to_matrix(
        matrix,
        inst_a.id,
        inst_b.id,
        Delivery(delivery_type="benefit", delivery_content="Positive delivery"),
        cell_description="Positive"
    )
    cell_ab = matrix.get_cell(inst_a.id, inst_b.id)
    service.create_relationship(
        Relationship(
            source_id=cell_ab.id,
            target_id=criterion.id,
            kind="evaluates_to",
            weight=0.8
        )
    )

    # Add one undermining delivery
    service.add_delivery_to_matrix(
        matrix,
        inst_a.id,
        inst_c.id,
        Delivery(delivery_type="cost", delivery_content="Negative delivery"),
        cell_description="Negative"
    )
    cell_ac = matrix.get_cell(inst_a.id, inst_c.id)
    service.create_relationship(
        Relationship(
            source_id=cell_ac.id,
            target_id=criterion.id,
            kind="evaluates_to",
            weight=-0.6
        )
    )

    results = evaluate_against_criteria(service)
    result = results[criterion.id]

    # Check counts
    assert result.serving_delivery_count == 1
    assert result.undermining_delivery_count == 1

    # Check aggregate score calculation
    # weighted_sum = (+0.8) + (-0.6) = 0.2
    # total_weight = 0.8 + 0.6 = 1.4
    # overall_score = 0.2 / 1.4 ≈ 0.143
    expected_score = (0.8 - 0.6) / (0.8 + 0.6)
    assert abs(result.overall_alignment_score - expected_score) < 0.001

    # Check that strengths and weaknesses are populated
    assert len(result.key_strengths) > 0
    assert len(result.key_weaknesses) > 0
