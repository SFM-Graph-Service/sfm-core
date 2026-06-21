"""
Regression checks that Hayden case-study matrices preserve published structure.
"""

from examples.hayden_case_studies import nebraska_k12_finance
from examples.hayden_case_studies import radioactive_waste
from graph.analysis_report import run_analysis_battery
from models import Node


def _labels_by_id(service):
    labels = {}
    for node in service.list_nodes():
        if isinstance(node, Node):
            labels[node.id] = node.label
    return labels


def _node_by_label(service):
    return {
        node.label: node
        for node in service.list_nodes()
        if isinstance(node, Node)
    }


def test_nebraska_k12_reproduces_published_structure():
    matrix, service = nebraska_k12_finance.build_nebraska_k12_matrix()
    labels = _labels_by_id(service)
    nodes = _node_by_label(service)

    # Hoffman & Hayden (2007), Nebraska TEEOSA matrix component roster
    # (summarized in docs/hayden_sfm_guide.md, "Nebraska K-12 Education Finance").
    assert {labels[component_id] for component_id in matrix.components} == {
        "State Legislature",
        "Department of Education",
        "School Districts",
        "Taxpayers",
        "Students",
    }

    # Hoffman & Hayden (2007), Nebraska delivery matrix structure:
    # Legislature/Districts, Legislature/DeptEd, DeptEd/Districts, Districts/Students,
    # Taxpayers/Legislature, Taxpayers/Districts.
    assert len(matrix.get_non_empty_cells()) == 6
    assert sum(len(cell.deliveries) for cell in matrix.cells.values()) == 9

    # Hoffman & Hayden (2007), TEEOSA channel: Legislature -> School Districts
    # carries at least funding and compliance requirements.
    legislature_to_districts = matrix.get_cell(
        nodes["State Legislature"].id,
        nodes["School Districts"].id,
    )
    assert legislature_to_districts is not None
    assert {delivery.delivery_type for delivery in legislature_to_districts.deliveries} == {
        "money",
        "rule",
    }


def test_llrw_reproduces_published_structure_and_normative_links():
    matrix, service = radioactive_waste.create_llrw_matrix()
    nodes = _node_by_label(service)

    # Hayden & Bolduc (2000), LLRW compact matrix includes host state, four generator
    # states, compact authority, and federal regulator (see docs/hayden_sfm_guide.md).
    component_labels = {nodes_by_id_label for nodes_by_id_label in _labels_by_id(service).values()}
    assert {
        "Nebraska (Host State)",
        "Arkansas",
        "Kansas",
        "Louisiana",
        "Oklahoma",
        "Central Interstate Compact Commission",
        "Nuclear Regulatory Commission",
    }.issubset(component_labels)

    # Hayden & Bolduc (2000), Figure-level delivery pattern:
    # generator states -> Nebraska ship waste and fees; Nebraska -> generators returns capacity.
    for state in ("Arkansas", "Kansas", "Louisiana", "Oklahoma"):
        outbound = matrix.get_cell(nodes[state].id, nodes["Nebraska (Host State)"].id)
        inbound = matrix.get_cell(nodes["Nebraska (Host State)"].id, nodes[state].id)
        assert outbound is not None
        assert {delivery.delivery_type for delivery in outbound.deliveries} == {"pollution", "money"}
        assert inbound is not None
        assert {delivery.delivery_type for delivery in inbound.deliveries} == {"energy"}

    # Hayden & Bolduc (2000), compact governance channel to host state:
    # authority + rules + funding.
    compact_to_nebraska = matrix.get_cell(
        nodes["Central Interstate Compact Commission"].id,
        nodes["Nebraska (Host State)"].id,
    )
    assert compact_to_nebraska is not None
    assert {delivery.delivery_type for delivery in compact_to_nebraska.deliveries} == {
        "authority",
        "rule",
        "money",
    }

    # Hayden & Bolduc (2000), normative linkage in published argument:
    # NRC safety standards evaluate positively to Public Health Protection criterion.
    nrc_to_nebraska = matrix.get_cell(
        nodes["Nuclear Regulatory Commission"].id,
        nodes["Nebraska (Host State)"].id,
    )
    public_health = nodes["Public Health Protection"]
    assert nrc_to_nebraska is not None
    assert any(
        relationship.source_id == nrc_to_nebraska.id
        and relationship.target_id == public_health.id
        and relationship.kind == "evaluates_to"
        and relationship.weight == 0.95
        for relationship in service.list_relationships()
    )

    # Hayden (2006), SFM holarchy requirement:
    # compact authority appears as an organizational-level institution.
    report = run_analysis_battery(service)
    assert "Central Interstate Compact Commission" in report.holarchy_levels
    assert "organizational" in report.holarchy_levels["Central Interstate Compact Commission"]
