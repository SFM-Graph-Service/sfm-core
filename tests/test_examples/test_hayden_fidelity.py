"""Regression checks for structural facts in Hayden-linked case studies."""

from examples.hayden_case_studies.nebraska_k12_finance import build_nebraska_k12_matrix
from examples.hayden_case_studies.radioactive_waste import create_llrw_matrix


def test_nebraska_structure_matches_documented_delivery_layout():
    # Hoffman & Hayden (2007), JOEI 41(4): TEEOSA represented as compact state-level delivery system.
    matrix, service = build_nebraska_k12_matrix()
    summary = matrix.get_summary()

    assert summary["components"] == 5
    assert summary["non_empty_cells"] == 6
    assert summary["total_deliveries"] == 9

    labels = {node.label for node in service.list_nodes()}
    assert "State Legislature" in labels
    assert "Department of Education" in labels
    assert "School Districts" in labels


def test_llrw_structure_matches_documented_compact_pattern():
    # Hayden & Bolduc (2000), JOEI 34(4): host state + generator states + compact governance.
    matrix, service = create_llrw_matrix()
    summary = matrix.get_summary()

    assert summary["components"] == 11
    assert summary["total_deliveries"] >= 30

    labels = {node.label for node in service.list_nodes()}
    assert "Nebraska (Host State)" in labels
    assert "Central Interstate Compact Commission" in labels
    assert "Nuclear Regulatory Commission" in labels

    delivery_types = summary["deliveries_by_type"]
    assert "pollution" in delivery_types
    assert "authority" in delivery_types
    assert "rule" in delivery_types
