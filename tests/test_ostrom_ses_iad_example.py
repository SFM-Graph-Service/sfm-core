"""
Tests for Ostrom SES/IAD ↔ SFM Bridge Example.

Validates that the example builds without error and creates expected structure
per issue #27 requirements.
"""

from examples.framework_bridges.ostrom_ses_iad_example import build_ostrom_ses_iad_sfm


def test_ostrom_example_builds_without_error():
    """Test that Ostrom SES/IAD example builds successfully."""
    matrix, service = build_ostrom_ses_iad_sfm()

    assert matrix is not None
    assert service is not None


def test_ostrom_example_has_expected_components():
    """Test that matrix has expected number of components."""
    matrix, service = build_ostrom_ses_iad_sfm()

    # Should have 9 components:
    # 4 actors + 4 rules + 1 resource system
    assert len(matrix.components) == 9


def test_ostrom_example_has_delivery_cells():
    """Test that matrix has action situations as delivery cells."""
    matrix, service = build_ostrom_ses_iad_sfm()

    # Should have at least 5 action situations:
    # - Quota setting
    # - Harvesting
    # - Monitoring
    # - Sanctioning
    # - Deliberation
    # - External oversight
    non_empty_cells = matrix.get_non_empty_cells()
    assert len(non_empty_cells) >= 5


def test_ostrom_example_has_criteria_evaluations():
    """Test that outcomes are linked to criteria."""
    matrix, service = build_ostrom_ses_iad_sfm()

    # Should have evaluates_to relationships for outcomes
    all_relationships = service.list_relationships()
    criteria_rels = [rel for rel in all_relationships if rel.kind == "evaluates_to"]

    # Should have at least 3 outcome evaluations:
    # - Forest sustainability
    # - Equity
    # - Legitimacy
    assert len(criteria_rels) >= 3


def test_ostrom_example_rules_have_metadata():
    """Test that rules-in-use have Ostrom metadata."""
    matrix, service = build_ostrom_ses_iad_sfm()

    all_nodes = service.list_nodes()

    # Find nodes with ostrom_type = "rule_in_use"
    rules = [
        node for node in all_nodes
        if hasattr(node, "meta") and node.meta.get("ostrom_type") == "rule_in_use"
    ]

    # Should have 4 rules: harvesting quota, monitoring, sanctioning, deliberation
    assert len(rules) >= 4

    # Rules should have rule_type metadata
    for rule in rules:
        assert "ostrom_rule_type" in rule.meta
        assert rule.meta["ostrom_rule_type"] in [
            "boundary_rule",
            "information_rule",
            "payoff_rule",
            "aggregation_rule",
            "choice_rule",
            "position_rule",
            "scope_rule"
        ]


def test_ostrom_example_actors_have_metadata():
    """Test that actors have Ostrom metadata."""
    matrix, service = build_ostrom_ses_iad_sfm()

    all_nodes = service.list_nodes()

    # Find nodes with ostrom_type = "actor"
    actors = [
        node for node in all_nodes
        if hasattr(node, "meta") and node.meta.get("ostrom_type") == "actor"
    ]

    # Should have 4 actors: association, users, monitoring authority, external authority
    assert len(actors) >= 4

    # Actors should have role metadata
    for actor in actors:
        assert "ostrom_role" in actor.meta


def test_ostrom_example_deliveries_have_types():
    """Test that action situations have typed deliveries."""
    matrix, service = build_ostrom_ses_iad_sfm()

    non_empty_cells = matrix.get_non_empty_cells()

    # Collect all delivery types
    delivery_types = set()
    for cell in non_empty_cells:
        for delivery in cell.deliveries:
            delivery_types.add(delivery.delivery_type)

    # Should have at least these Ostrom-relevant delivery types:
    # - authority (quota setting, external recognition)
    # - extraction (harvesting)
    # - information (monitoring)
    # - sanction (enforcement)
    # - voice (deliberation)
    expected_types = {"authority", "extraction", "information", "sanction", "voice"}
    assert expected_types.issubset(delivery_types)
