"""
Unit tests for graph.centrality module (Issue #35).

Tests compute_centrality_metrics, format_centrality_report, and
identify_power_brokers using fixture delivery matrices.
"""

import pytest

from api.sfm_service import SFMService
from models import Node
from models.delivery_matrix import Delivery
from graph.centrality import (
    compute_centrality_metrics,
    format_centrality_report,
    identify_power_brokers,
)


@pytest.fixture
def triangle_matrix():
    """
    Three-node directed triangle: A → B → C → A, plus A → C.

    The direct A→C edge means B is not a required intermediary,
    but B still has nonzero betweenness via the A→B→C path.
    Returns (matrix, service, node_labels_dict).
    """
    service = SFMService()

    node_a = Node(label="Node A", description="Source")
    node_b = Node(label="Node B", description="Bridge")
    node_c = Node(label="Node C", description="Sink")

    for node in [node_a, node_b, node_c]:
        service.create_node(node)

    matrix = service.create_delivery_matrix(
        label="Triangle Matrix",
        description="Three-node triangle for centrality tests",
        components=[node_a.id, node_b.id, node_c.id],
        matrix_scope="local",
    )

    # A → B
    service.add_delivery_to_matrix(
        matrix, node_a.id, node_b.id,
        Delivery(delivery_type="money", delivery_content="Transfer A to B"),
        cell_description="A delivers money to B",
    )
    # B → C
    service.add_delivery_to_matrix(
        matrix, node_b.id, node_c.id,
        Delivery(delivery_type="money", delivery_content="Transfer B to C"),
        cell_description="B delivers money to C",
    )
    # C → A
    service.add_delivery_to_matrix(
        matrix, node_c.id, node_a.id,
        Delivery(delivery_type="money", delivery_content="Transfer C to A"),
        cell_description="C delivers money to A",
    )
    # A → C (second path bypassing B)
    service.add_delivery_to_matrix(
        matrix, node_a.id, node_c.id,
        Delivery(delivery_type="information", delivery_content="Direct A to C"),
        cell_description="A delivers information directly to C",
    )

    return matrix, service, {"A": node_a.label, "B": node_b.label, "C": node_c.label}


@pytest.fixture
def empty_matrix():
    """Matrix with two components but no deliveries."""
    service = SFMService()
    node_x = Node(label="Node X", description="Isolated X")
    node_y = Node(label="Node Y", description="Isolated Y")
    for node in [node_x, node_y]:
        service.create_node(node)

    matrix = service.create_delivery_matrix(
        label="Empty Matrix",
        description="No deliveries",
        components=[node_x.id, node_y.id],
        matrix_scope="local",
    )
    return matrix, service


@pytest.fixture
def broker_matrix():
    """
    Hub-and-spoke topology: Broker → Spoke1, Spoke2, Spoke3.

    The broker is the sole intermediary; it should have the highest
    betweenness centrality.
    """
    service = SFMService()

    broker = Node(label="Broker", description="Central hub")
    spoke1 = Node(label="Spoke 1", description="Peripheral node 1")
    spoke2 = Node(label="Spoke 2", description="Peripheral node 2")
    spoke3 = Node(label="Spoke 3", description="Peripheral node 3")

    nodes = [broker, spoke1, spoke2, spoke3]
    for node in nodes:
        service.create_node(node)

    matrix = service.create_delivery_matrix(
        label="Broker Matrix",
        description="Hub-and-spoke delivery network",
        components=[n.id for n in nodes],
        matrix_scope="national",
    )

    for spoke in [spoke1, spoke2, spoke3]:
        service.add_delivery_to_matrix(
            matrix, broker.id, spoke.id,
            Delivery(delivery_type="authority", delivery_content=f"Broker → {spoke.label}"),
            cell_description=f"Broker delivers authority to {spoke.label}",
        )
        service.add_delivery_to_matrix(
            matrix, spoke.id, broker.id,
            Delivery(delivery_type="information", delivery_content=f"{spoke.label} → Broker"),
            cell_description=f"{spoke.label} delivers information to Broker",
        )

    return matrix, service, broker.label


class TestComputeCentralityMetrics:
    """Tests for compute_centrality_metrics."""

    def test_returns_three_metrics(self, triangle_matrix):
        matrix, service, _ = triangle_matrix
        result = compute_centrality_metrics(matrix, service)

        assert "betweenness" in result
        assert "degree" in result
        assert "closeness" in result

    def test_all_component_labels_present(self, triangle_matrix):
        matrix, service, labels = triangle_matrix
        result = compute_centrality_metrics(matrix, service)

        for key in ("betweenness", "degree", "closeness"):
            metric = result[key]
            for label in labels.values():
                assert label in metric, f"{label} missing from {key}"

    def test_scores_are_valid_floats(self, triangle_matrix):
        matrix, service, _ = triangle_matrix
        result = compute_centrality_metrics(matrix, service)

        for key in ("betweenness", "closeness"):
            for label, score in result[key].items():
                assert isinstance(score, float), f"{key}[{label}] should be float"
                assert 0.0 <= score <= 1.0, f"{key}[{label}]={score} out of [0,1]"

        # Degree centrality on a DiGraph normalizes by (n-1), so sums of
        # in_degree + out_degree can exceed 1.0 for well-connected nodes.
        for label, score in result["degree"].items():
            assert isinstance(score, float), f"degree[{label}] should be float"
            assert score >= 0.0, f"degree[{label}]={score} should be non-negative"

    def test_empty_matrix_returns_empty_dicts(self, empty_matrix):
        matrix, service = empty_matrix
        result = compute_centrality_metrics(matrix, service)

        # Nodes are present but there are no edges, so all centralities are 0
        for key in ("betweenness", "degree", "closeness"):
            assert isinstance(result[key], dict)
            for score in result[key].values():
                assert score == 0.0

    def test_broker_has_highest_degree(self, broker_matrix):
        matrix, service, broker_label = broker_matrix
        result = compute_centrality_metrics(matrix, service)

        degree_scores = result["degree"]
        top_node = max(degree_scores, key=degree_scores.get)
        assert top_node == broker_label, (
            f"Expected broker '{broker_label}' to have highest degree, got '{top_node}'"
        )


class TestFormatCentralityReport:
    """Tests for format_centrality_report."""

    def test_output_is_non_empty_string(self, triangle_matrix):
        matrix, service, _ = triangle_matrix
        centrality = compute_centrality_metrics(matrix, service)
        report = format_centrality_report(centrality)
        assert isinstance(report, str)
        assert len(report) > 0

    def test_custom_title_appears_in_output(self, triangle_matrix):
        matrix, service, _ = triangle_matrix
        centrality = compute_centrality_metrics(matrix, service)
        title = "My Custom Title"
        report = format_centrality_report(centrality, title=title)
        assert title in report

    def test_metric_names_appear_in_output(self, triangle_matrix):
        matrix, service, _ = triangle_matrix
        centrality = compute_centrality_metrics(matrix, service)
        report = format_centrality_report(centrality)
        assert "Betweenness" in report
        assert "Degree" in report
        assert "Closeness" in report

    def test_top_n_limits_entries(self, broker_matrix):
        matrix, service, _ = broker_matrix
        centrality = compute_centrality_metrics(matrix, service)
        report = format_centrality_report(centrality, top_n=1)
        # Each metric section should list at most 1 node ("1. <label>:")
        assert report.count("  1.") >= 1
        assert "  2." not in report

    def test_empty_centrality_produces_string(self):
        report = format_centrality_report({"betweenness": {}, "degree": {}, "closeness": {}})
        assert isinstance(report, str)


class TestIdentifyPowerBrokers:
    """Tests for identify_power_brokers."""

    def test_returns_list_of_tuples(self, triangle_matrix):
        matrix, service, _ = triangle_matrix
        centrality = compute_centrality_metrics(matrix, service)
        brokers = identify_power_brokers(centrality)
        assert isinstance(brokers, list)
        for item in brokers:
            assert isinstance(item, tuple)
            assert len(item) == 2

    def test_sorted_descending(self, broker_matrix):
        matrix, service, _ = broker_matrix
        centrality = compute_centrality_metrics(matrix, service)
        # Lower threshold to ensure we get some results
        brokers = identify_power_brokers(centrality, betweenness_threshold=0.0)
        scores = [score for _, score in brokers]
        assert scores == sorted(scores, reverse=True)

    def test_threshold_filters_low_scores(self, triangle_matrix):
        matrix, service, _ = triangle_matrix
        centrality = compute_centrality_metrics(matrix, service)
        # Set threshold above maximum possible score → empty list
        brokers = identify_power_brokers(centrality, betweenness_threshold=2.0)
        assert brokers == []

    def test_broker_identified_above_threshold(self, broker_matrix):
        matrix, service, broker_label = broker_matrix
        centrality = compute_centrality_metrics(matrix, service)
        # Broker should appear with low threshold
        brokers = identify_power_brokers(centrality, betweenness_threshold=0.0)
        broker_labels = [label for label, _ in brokers]
        assert broker_label in broker_labels


class TestDirectorNetworkCentrality:
    """
    Integration test: director network produces expected centrality pattern.

    Directors Smith and Jones serve on multiple boards and should have
    higher betweenness than single-institution nodes (Hayden 2002).
    """

    def test_directors_have_nonzero_betweenness(self):
        from examples.hayden_case_studies.director_networks import (
            create_director_network_matrix,
        )

        matrix, service = create_director_network_matrix()
        centrality = compute_centrality_metrics(matrix, service)

        betweenness = centrality["betweenness"]
        assert betweenness.get("Director Smith", 0.0) > 0.0, (
            "Director Smith should have positive betweenness in corporate network"
        )
        assert betweenness.get("Director Jones", 0.0) > 0.0, (
            "Director Jones should have positive betweenness in corporate network"
        )

    def test_format_report_includes_directors(self):
        from examples.hayden_case_studies.director_networks import (
            create_director_network_matrix,
        )

        matrix, service = create_director_network_matrix()
        centrality = compute_centrality_metrics(matrix, service)
        report = format_centrality_report(centrality, top_n=10)
        assert "Director Smith" in report or "Director Jones" in report
