"""
Regression checks that Hayden case-study matrices preserve published structure.
"""

from examples.hayden_case_studies import nebraska_k12
from examples.hayden_case_studies import radioactive_waste
from graph.analysis_report import run_analysis_battery
from models import Node
from api.sfm_service import SFMService


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
    """
    Test Nebraska K-12 matrix per Hoffman & Hayden (2007).

    Verifies 13×13 structure with 6 social beliefs + 7 institutions,
    key TEEOSA cells, and required component types.
    """
    service = SFMService()
    matrix, components = nebraska_k12.create_nebraska_k12_matrix(service)

    # Verify 13×13 matrix structure
    assert len(matrix.components) == 13, "Matrix must be 13×13 per published paper"
    assert len(components) == 13, "Must have exactly 13 components"

    # Verify component types: 6 social beliefs + 7 institutional organizations
    beliefs = [c for c in components if "Social Belief" in c.label]
    institutions = [c for c in components if "Social Belief" not in c.label]

    assert len(beliefs) == 6, "Must have exactly 6 social belief components"
    assert len(institutions) == 7, "Must have exactly 7 institutional organization components"

    # Verify specific social beliefs (exact list from paper Figure 1, p. 361)
    belief_labels = {b.label for b in beliefs}
    required_beliefs = {
        "Equity (Social Belief)",
        "Adequacy/Sufficiency (Social Belief)",
        "Cost/Efficiency (Social Belief)",
        "Comprehensive Size (Social Belief)",
        "Consolidation (Social Belief)",
        "Local Control (Social Belief)",
    }
    assert required_beliefs == belief_labels, f"Missing beliefs: {required_beliefs - belief_labels}"

    # Verify specific institutions (exact list from paper Figure 1, p. 361)
    institution_labels = {inst.label for inst in institutions}
    required_institutions = {
        "Courts/Legal System",
        "Nebraska Legislature/Governor",
        "K-12 Public Schools",
        "Property Tax Program",
        "Property Wealth",
        "Nebraska Department of Education",
        "Nebraska Department of Revenue",
    }
    assert required_institutions == institution_labels, \
        f"Missing institutions: {required_institutions - institution_labels}"


def test_llrw_reproduces_published_structure_and_normative_links():
    matrix, service = radioactive_waste.create_llrw_matrix()
    nodes = _node_by_label(service)

    # Hayden & Bolduc (2000), LLRW compact matrix includes host state, four generator
    # states, compact authority, and federal regulator (see docs/hayden_sfm_guide.md).
    labels_by_id = _labels_by_id(service)
    component_labels = {labels_by_id[component_id] for component_id in matrix.components}
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


def test_nebraska_k12_teeosa_cells():
    """
    Test Nebraska K-12 TEEOSA formula cells per Hoffman & Hayden (2007).

    Verifies key cells (7,12), (8,12), (8,13), (13,12) contain TEEOSA rules.
    Quote from paper p. 360: "Our interest is with the deliveries in cells
    (7,12), (8,12), (8,13), and (13,12). Together these cells contain the
    State education finance system called the Tax Equity and Educational
    Opportunities Support Act (TEEOSA)."
    """
    service = SFMService()
    matrix, components = nebraska_k12.create_nebraska_k12_matrix(service)

    def _node_by_label(components):
        return {c.label: c for c in components}

    nodes = _node_by_label(components)

    # Cell (8,12): Legislature → Dept of Education (TEEOSA rules)
    leg_to_dept_ed = matrix.get_cell(
        nodes["Nebraska Legislature/Governor"].id,
        nodes["Nebraska Department of Education"].id
    )
    assert leg_to_dept_ed is not None, "Cell (8,12) Legislature → Dept Ed must exist"
    assert len(leg_to_dept_ed.deliveries) > 0, "Cell (8,12) must contain TEEOSA formula rules"

    # Verify this cell contains "rule" delivery type for TEEOSA formula
    delivery_types = {d.delivery_type for d in leg_to_dept_ed.deliveries}
    assert "rule" in delivery_types, "Cell (8,12) must contain rule delivery (TEEOSA formula)"

    # Verify delivery content mentions TEEOSA
    has_teeosa = any("TEEOSA" in d.delivery_content or "formula" in d.delivery_content.lower()
                     for d in leg_to_dept_ed.deliveries)
    assert has_teeosa, "Cell (8,12) must reference TEEOSA formula in delivery content"

    # Cell (8,13): Legislature → Dept of Revenue
    leg_to_dept_rev = matrix.get_cell(
        nodes["Nebraska Legislature/Governor"].id,
        nodes["Nebraska Department of Revenue"].id
    )
    assert leg_to_dept_rev is not None, "Cell (8,13) Legislature → Dept Revenue must exist"

    # Cell (13,12): Dept of Revenue → Dept of Education
    rev_to_dept_ed = matrix.get_cell(
        nodes["Nebraska Department of Revenue"].id,
        nodes["Nebraska Department of Education"].id
    )
    assert rev_to_dept_ed is not None, "Cell (13,12) Dept Revenue → Dept Ed must exist"
    assert len(rev_to_dept_ed.deliveries) > 0, "Cell (13,12) must contain property valuation data"

    # Cell (7,12): Courts → Dept of Education
    courts_to_dept_ed = matrix.get_cell(
        nodes["Courts/Legal System"].id,
        nodes["Nebraska Department of Education"].id
    )
    assert courts_to_dept_ed is not None, "Cell (7,12) Courts → Dept Ed must exist"
