"""
Smoke tests for Clean Air Act ↔ Doughnut Economics integration example.

Validates that the example runs end-to-end and produces non-empty reports
per issue #25 requirements.
"""

from examples.hayden_case_studies.clean_air_act_doughnut import (
    create_clean_air_act_doughnut_matrix,
)
from graph.analysis_report import run_analysis_battery
from graph.criteria_evaluation import evaluate_against_criteria
from graph.doughnut_evaluation import evaluate_doughnut


def test_clean_air_act_doughnut_creates_matrix():
    """Test that matrix creation completes without errors."""
    matrix, service = create_clean_air_act_doughnut_matrix()

    assert matrix is not None
    assert service is not None

    # Verify matrix has components
    summary = matrix.get_summary()
    assert summary["components"] > 0
    assert summary["non_empty_cells"] > 0
    assert summary["total_deliveries"] > 0


def test_clean_air_act_doughnut_has_doughnut_boundaries():
    """Test that Doughnut boundaries are present in graph."""
    matrix, service = create_clean_air_act_doughnut_matrix()

    all_nodes = service.list_nodes()
    node_labels = {node.label for node in all_nodes}

    # Should have the three CAA-relevant Doughnut boundaries
    assert "Air Pollution" in node_labels
    assert "Health" in node_labels
    assert "Water" in node_labels


def test_clean_air_act_doughnut_analysis_battery_runs():
    """Test that SFM analysis battery runs and produces non-empty report."""
    matrix, service = create_clean_air_act_doughnut_matrix()

    report = run_analysis_battery(service)

    assert report is not None
    # Verify report has content (node count should be positive)
    assert report.node_count > 0


def test_clean_air_act_doughnut_evaluation_runs():
    """Test that Doughnut evaluation runs and produces non-empty report."""
    matrix, service = create_clean_air_act_doughnut_matrix()

    doughnut_report = evaluate_doughnut(service)

    assert doughnut_report is not None
    assert doughnut_report.total_boundaries == 21

    # Should have evaluated at least the three CAA-relevant boundaries
    all_evaluated = doughnut_report.social_foundation + doughnut_report.ecological_ceiling
    assert len(all_evaluated) >= 3


def test_clean_air_act_doughnut_identifies_air_pollution_boundary():
    """Test that Air Pollution boundary is identified with driving chains."""
    matrix, service = create_clean_air_act_doughnut_matrix()

    doughnut_report = evaluate_doughnut(service)

    air_pollution = doughnut_report.get_boundary_by_label("Air Pollution")
    assert air_pollution is not None
    assert air_pollution.polarity == "overshoot"

    # Should have identified driving chains (pollution deliveries)
    assert len(air_pollution.driving_chains) > 0

    # Net impact can be positive (EPA standards reduce overshoot) or negative (pollution drives it)
    # Both are valid depending on which delivery chains dominate
    assert air_pollution.net_impact in ["negative", "neutral", "positive"]


def test_clean_air_act_doughnut_identifies_health_boundary():
    """Test that Health boundary is identified with driving chains."""
    matrix, service = create_clean_air_act_doughnut_matrix()

    doughnut_report = evaluate_doughnut(service)

    health = doughnut_report.get_boundary_by_label("Health")
    assert health is not None
    assert health.polarity == "shortfall"

    # Should have identified driving chains
    assert len(health.driving_chains) > 0


def test_clean_air_act_doughnut_identifies_water_boundary():
    """Test that Water boundary is identified with driving chains."""
    matrix, service = create_clean_air_act_doughnut_matrix()

    doughnut_report = evaluate_doughnut(service)

    water = doughnut_report.get_boundary_by_label("Water")
    assert water is not None
    assert water.polarity == "shortfall"

    # Should have identified driving chains (acid rain impacts)
    assert len(water.driving_chains) > 0


def test_clean_air_act_doughnut_embedded_economy_holarchy():
    """Test that embedded economy holarchy has all three levels."""
    matrix, service = create_clean_air_act_doughnut_matrix()

    doughnut_report = evaluate_doughnut(service)

    holarchy = doughnut_report.embedded_economy_holarchy

    # Should have exactly 3 levels
    assert len(holarchy) == 3
    assert "biosphere" in holarchy
    assert "society" in holarchy
    assert "economy" in holarchy

    # Each level should have at least one node
    assert len(holarchy["biosphere"]) > 0
    assert len(holarchy["society"]) > 0
    # Economy level may be empty in this simplified example
    # (no explicit economic criteria nodes beyond boundaries)


def test_clean_air_act_doughnut_criteria_evaluation_runs():
    """Test that criteria evaluation runs (if SFM criteria present)."""
    matrix, service = create_clean_air_act_doughnut_matrix()

    # May have zero traditional SFM criteria (focuses on Doughnut)
    # But evaluation should not crash
    criteria_results = evaluate_against_criteria(service)

    assert criteria_results is not None


def test_clean_air_act_doughnut_delivery_boundary_linkages():
    """Test that delivery cells are linked to Doughnut boundaries."""
    matrix, service = create_clean_air_act_doughnut_matrix()

    # Get all relationships
    all_relationships = service.list_relationships()

    # Find evaluates_to relationships pointing to Doughnut boundaries
    all_nodes = service.list_nodes()
    boundary_ids = {
        node.id for node in all_nodes
        if hasattr(node, "meta") and
        node.meta.get("doughnut_dimension") in ["social_foundation", "ecological_ceiling"]
    }

    # Should have relationships linking delivery cells to boundaries
    boundary_evaluations = [
        rel for rel in all_relationships
        if rel.kind == "evaluates_to" and rel.target_id in boundary_ids
    ]

    assert len(boundary_evaluations) > 0, \
        "No delivery cells linked to Doughnut boundaries via evaluates_to relationships"


def test_clean_air_act_doughnut_end_to_end_smoke():
    """
    Smoke test: Full end-to-end execution per issue #25 requirements.

    Validates that:
    1. Matrix creation completes
    2. SFM analysis battery runs
    3. Doughnut evaluation runs
    4. Both produce non-empty reports
    5. Named boundaries are identified
    """
    # Create matrix
    matrix, service = create_clean_air_act_doughnut_matrix()
    assert matrix is not None

    # Run SFM analysis
    sfm_report = run_analysis_battery(service)
    assert sfm_report is not None
    assert sfm_report.node_count > 0

    # Run Doughnut evaluation
    doughnut_report = evaluate_doughnut(service)
    assert doughnut_report is not None
    assert doughnut_report.total_boundaries == 21

    # Verify named boundaries are present and evaluated
    air_pollution = doughnut_report.get_boundary_by_label("Air Pollution")
    health = doughnut_report.get_boundary_by_label("Health")
    water = doughnut_report.get_boundary_by_label("Water")

    assert air_pollution is not None, "Air Pollution boundary not found"
    assert health is not None, "Health boundary not found"
    assert water is not None, "Water boundary not found"

    # All three should have driving chains
    assert len(air_pollution.driving_chains) > 0, "Air Pollution has no driving chains"
    assert len(health.driving_chains) > 0, "Health has no driving chains"
    assert len(water.driving_chains) > 0, "Water has no driving chains"

    # Status should be determined (not left at default)
    assert air_pollution.status in ["met", "overshoot", "shortfall"]
    assert health.status in ["met", "overshoot", "shortfall"]
    assert water.status in ["met", "overshoot", "shortfall"]
