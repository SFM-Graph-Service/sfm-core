"""
Tests for matrix-digraph conversion.

Tests cover:
- Matrix to MultiDiGraph conversion
- MultiDiGraph to matrix reconstruction
- Adjacency dictionary conversions
- Delivery summary statistics
- SFMDeliveryMatrix.from_multidigraph() convenience method
- SFMService.analyze_matrix_as_graph() graph analysis
"""

import uuid

import pytest
import networkx as nx

from api.sfm_service import SFMService
from models import Node
from models.delivery_matrix import Delivery, SFMDeliveryMatrix
from graph.converters import (
    to_multidigraph,
    from_multidigraph,
    matrix_to_adjacency_dict,
    adjacency_dict_to_matrix,
    get_delivery_summary
)


class TestMatrixToDigraph:
    """Test matrix to digraph conversion."""

    def setup_method(self):
        """Setup test service and matrix."""
        self.service = SFMService()

        # Create components
        self.comp_a = Node(label="Component A")
        self.comp_b = Node(label="Component B")
        self.comp_c = Node(label="Component C")

        self.service.create_node(self.comp_a)
        self.service.create_node(self.comp_b)
        self.service.create_node(self.comp_c)

        # Create matrix
        self.matrix = self.service.create_delivery_matrix(
            label="Test Matrix",
            description="Test conversion matrix",
            components=[self.comp_a.id, self.comp_b.id, self.comp_c.id]
        )

        # Add deliveries
        delivery1 = Delivery(
            delivery_type="money",
            delivery_content="Funding",
            quantity=1_000_000,
            units="USD/year"
        )

        delivery2 = Delivery(
            delivery_type="rule",
            delivery_content="Regulations"
        )

        self.service.add_delivery_to_matrix(
            self.matrix,
            self.comp_a.id,
            self.comp_b.id,
            delivery1,
            cell_description="A funds B"
        )

        self.service.add_delivery_to_matrix(
            self.matrix,
            self.comp_a.id,
            self.comp_b.id,
            delivery2,
            cell_description="A funds B"
        )

    def test_to_multidigraph_creates_nodes(self):
        """Test conversion creates nodes for all components."""
        G = to_multidigraph(self.matrix, self.service)

        assert isinstance(G, nx.MultiDiGraph)
        assert len(G.nodes()) == 3
        assert self.comp_a.id in G.nodes()
        assert self.comp_b.id in G.nodes()
        assert self.comp_c.id in G.nodes()

    def test_to_multidigraph_node_attributes(self):
        """Test nodes have correct attributes."""
        G = to_multidigraph(self.matrix, self.service)

        node_data = G.nodes[self.comp_a.id]
        assert node_data['label'] == "Component A"

    def test_to_multidigraph_creates_edges(self):
        """Test conversion creates edges for deliveries."""
        G = to_multidigraph(self.matrix, self.service)

        # Should have 2 edges (A->B with 2 deliveries)
        assert G.number_of_edges() == 2

        # Check edges exist
        assert G.has_edge(self.comp_a.id, self.comp_b.id)

    def test_to_multidigraph_edge_attributes(self):
        """Test edges have delivery attributes."""
        G = to_multidigraph(self.matrix, self.service)

        # Get edges from A to B
        edges = G.get_edge_data(self.comp_a.id, self.comp_b.id)

        # Should have 2 edges (money and rule)
        assert len(edges) == 2

        # Check for money edge
        money_edge = edges.get('money')
        assert money_edge is not None
        assert money_edge['delivery_content'] == "Funding"
        assert money_edge['quantity'] == 1_000_000
        assert money_edge['units'] == "USD/year"

    def test_to_multidigraph_graph_attributes(self):
        """Test graph has matrix metadata."""
        G = to_multidigraph(self.matrix, self.service)

        assert G.graph['matrix_label'] == "Test Matrix"
        assert G.graph['matrix_description'] == "Test conversion matrix"
        assert 'matrix_id' in G.graph

    def test_to_multidigraph_via_matrix_method(self):
        """Test convenience method on matrix."""
        G = self.matrix.to_multidigraph(self.service)

        assert isinstance(G, nx.MultiDiGraph)
        assert len(G.nodes()) == 3


class TestDigraphToMatrix:
    """Test digraph to matrix reconstruction."""

    def setup_method(self):
        """Setup test service."""
        self.service = SFMService()

    def test_from_multidigraph_reconstructs_components(self):
        """Test reconstruction creates all components."""
        # Create simple graph
        G = nx.MultiDiGraph()

        comp_a = uuid.uuid4()
        comp_b = uuid.uuid4()

        G.add_node(comp_a, label="A")
        G.add_node(comp_b, label="B")

        G.add_edge(
            comp_a, comp_b,
            key="money",
            delivery_content="Payment",
            quantity=1000,
            cell_description="A pays B"
        )

        # Reconstruct matrix
        matrix = from_multidigraph(G, self.service, matrix_label="Reconstructed")

        assert matrix.label == "Reconstructed"
        assert len(matrix.components) == 2

    def test_from_multidigraph_reconstructs_deliveries(self):
        """Test reconstruction preserves deliveries."""
        G = nx.MultiDiGraph()

        comp_a = uuid.uuid4()
        comp_b = uuid.uuid4()

        G.add_node(comp_a, label="A")
        G.add_node(comp_b, label="B")

        G.add_edge(
            comp_a, comp_b,
            key="money",
            delivery_content="Funding",
            quantity=5000,
            units="USD",
            certainty=0.9,
            cell_description="A funds B"
        )

        G.add_edge(
            comp_a, comp_b,
            key="rule",
            delivery_content="Regulation",
            cell_description="A funds B"
        )

        matrix = from_multidigraph(G, self.service)

        # Check cell has 2 deliveries
        cell = matrix.get_cell(comp_a, comp_b)
        assert cell is not None
        assert len(cell.deliveries) == 2

        # Check delivery attributes preserved
        money_deliveries = [d for d in cell.deliveries if d.delivery_type == "money"]
        assert len(money_deliveries) == 1
        assert money_deliveries[0].quantity == 5000
        assert money_deliveries[0].certainty == 0.9

    def test_roundtrip_conversion(self):
        """Test matrix -> graph -> matrix roundtrip."""
        # Create original matrix
        comp_a = Node(label="A")
        comp_b = Node(label="B")

        self.service.create_node(comp_a)
        self.service.create_node(comp_b)

        original = self.service.create_delivery_matrix(
            label="Original",
            components=[comp_a.id, comp_b.id]
        )

        delivery = Delivery(
            delivery_type="energy",
            delivery_content="Services",
            quantity=100
        )

        self.service.add_delivery_to_matrix(
            original,
            comp_a.id,
            comp_b.id,
            delivery,
            cell_description="A provides services to B"
        )

        # Convert to graph
        G = to_multidigraph(original, self.service)

        # Convert back to matrix
        reconstructed = from_multidigraph(G, self.service)

        # Verify
        assert len(reconstructed.components) == 2
        cell = reconstructed.get_cell(comp_a.id, comp_b.id)
        assert cell is not None
        assert len(cell.deliveries) == 1
        assert cell.deliveries[0].delivery_type == "energy"
        assert cell.deliveries[0].quantity == 100


class TestAdjacencyConversion:
    """Test adjacency dictionary conversions."""

    def setup_method(self):
        """Setup test service and matrix."""
        self.service = SFMService()

        self.comp_a = Node(label="A")
        self.comp_b = Node(label="B")

        self.service.create_node(self.comp_a)
        self.service.create_node(self.comp_b)

        self.matrix = self.service.create_delivery_matrix(
            components=[self.comp_a.id, self.comp_b.id]
        )

        delivery = Delivery(
            delivery_type="money",
            delivery_content="Payment"
        )

        self.service.add_delivery_to_matrix(
            self.matrix,
            self.comp_a.id,
            self.comp_b.id,
            delivery,
            cell_description="Payment from A to B"
        )

    def test_matrix_to_adjacency_dict(self):
        """Test matrix to adjacency dictionary."""
        adj = matrix_to_adjacency_dict(self.matrix, self.service)

        assert self.comp_a.id in adj
        assert self.comp_b.id in adj[self.comp_a.id]
        assert len(adj[self.comp_a.id][self.comp_b.id]) == 1
        assert adj[self.comp_a.id][self.comp_b.id][0].delivery_type == "money"

    def test_adjacency_dict_to_matrix(self):
        """Test adjacency dictionary to matrix."""
        # Create adjacency dict
        adj = {
            self.comp_a.id: {
                self.comp_b.id: [
                    Delivery(delivery_type="rule", delivery_content="Regulation")
                ]
            },
            self.comp_b.id: {}
        }

        matrix = adjacency_dict_to_matrix(adj, self.service, label="From Adj")

        assert matrix.label == "From Adj"
        assert len(matrix.components) == 2

        cell = matrix.get_cell(self.comp_a.id, self.comp_b.id)
        assert cell is not None
        assert len(cell.deliveries) == 1


class TestDeliverySummary:
    """Test delivery summary statistics."""

    def setup_method(self):
        """Setup test matrix with various deliveries."""
        self.service = SFMService()

        self.comp_a = Node(label="A")
        self.comp_b = Node(label="B")
        self.comp_c = Node(label="C")

        self.service.create_node(self.comp_a)
        self.service.create_node(self.comp_b)
        self.service.create_node(self.comp_c)

        self.matrix = self.service.create_delivery_matrix(
            components=[self.comp_a.id, self.comp_b.id, self.comp_c.id]
        )

        # A -> B: 2 deliveries (money, rule)
        self.service.add_delivery_to_matrix(
            self.matrix,
            self.comp_a.id,
            self.comp_b.id,
            Delivery(delivery_type="money", delivery_content="Funding", quantity=1000),
            cell_description="A funds B"
        )

        self.service.add_delivery_to_matrix(
            self.matrix,
            self.comp_a.id,
            self.comp_b.id,
            Delivery(delivery_type="rule", delivery_content="Rules"),
            cell_description="A funds B"
        )

        # B -> C: 1 delivery (energy)
        self.service.add_delivery_to_matrix(
            self.matrix,
            self.comp_b.id,
            self.comp_c.id,
            Delivery(delivery_type="energy", delivery_content="Services", quantity=500),
            cell_description="B provides services to C"
        )

    def test_get_delivery_summary(self):
        """Test delivery summary statistics."""
        summary = get_delivery_summary(self.matrix)

        assert summary['components'] == 3
        assert summary['non_empty_cells'] == 2
        assert summary['total_deliveries'] == 3
        assert summary['deliveries_by_type']['money'] == 1
        assert summary['deliveries_by_type']['rule'] == 1
        assert summary['deliveries_by_type']['energy'] == 1
        assert summary['cells_with_multiple_deliveries'] == 1
        assert summary['quantified_deliveries'] == 2
        assert summary['cells_with_descriptions'] == 2

    def test_get_summary_via_matrix_method(self):
        """Test convenience method on matrix."""
        summary = self.matrix.get_summary()

        assert summary['total_deliveries'] == 3
        assert summary['components'] == 3


class TestFromMultidigraphClassMethod:
    """Test SFMDeliveryMatrix.from_multidigraph() class method."""

    def setup_method(self):
        """Setup test service."""
        self.service = SFMService()

    def test_from_multidigraph_returns_matrix(self):
        """Test that from_multidigraph returns an SFMDeliveryMatrix instance."""
        G = nx.MultiDiGraph()
        comp_a = uuid.uuid4()
        comp_b = uuid.uuid4()
        G.add_node(comp_a, label="A")
        G.add_node(comp_b, label="B")
        G.add_edge(comp_a, comp_b, key="money", delivery_content="Funding",
                   cell_description="A funds B")

        matrix = SFMDeliveryMatrix.from_multidigraph(G, self.service)

        assert isinstance(matrix, SFMDeliveryMatrix)

    def test_from_multidigraph_components(self):
        """Test from_multidigraph reconstructs all components."""
        G = nx.MultiDiGraph()
        comp_a = uuid.uuid4()
        comp_b = uuid.uuid4()
        comp_c = uuid.uuid4()
        G.add_node(comp_a, label="A")
        G.add_node(comp_b, label="B")
        G.add_node(comp_c, label="C")

        matrix = SFMDeliveryMatrix.from_multidigraph(G, self.service)

        assert len(matrix.components) == 3
        assert comp_a in matrix.components
        assert comp_b in matrix.components
        assert comp_c in matrix.components

    def test_from_multidigraph_with_label(self):
        """Test from_multidigraph uses provided matrix_label."""
        G = nx.MultiDiGraph()
        comp_a = uuid.uuid4()
        G.add_node(comp_a, label="A")

        matrix = SFMDeliveryMatrix.from_multidigraph(
            G, self.service, matrix_label="My Label"
        )

        assert matrix.label == "My Label"

    def test_from_multidigraph_uses_graph_label_attribute(self):
        """Test from_multidigraph falls back to graph attribute for label."""
        G = nx.MultiDiGraph()
        G.graph['matrix_label'] = "Graph Attribute Label"
        comp_a = uuid.uuid4()
        G.add_node(comp_a, label="A")

        matrix = SFMDeliveryMatrix.from_multidigraph(G, self.service)

        assert matrix.label == "Graph Attribute Label"

    def test_from_multidigraph_preserves_deliveries(self):
        """Test from_multidigraph reconstructs deliveries correctly."""
        G = nx.MultiDiGraph()
        comp_a = uuid.uuid4()
        comp_b = uuid.uuid4()
        G.add_node(comp_a, label="A")
        G.add_node(comp_b, label="B")
        G.add_edge(comp_a, comp_b, key="money",
                   delivery_content="Annual appropriation",
                   quantity=500_000, units="USD/year",
                   cell_description="A funds B")
        G.add_edge(comp_a, comp_b, key="rule",
                   delivery_content="Regulations",
                   cell_description="A funds B")

        matrix = SFMDeliveryMatrix.from_multidigraph(G, self.service)

        cell = matrix.get_cell(comp_a, comp_b)
        assert cell is not None
        assert len(cell.deliveries) == 2
        money = [d for d in cell.deliveries if d.delivery_type == "money"][0]
        assert money.quantity == 500_000
        assert money.units == "USD/year"

    def test_from_multidigraph_roundtrip_via_class_method(self):
        """Test matrix → graph → matrix roundtrip using class method."""
        comp_a = Node(label="Component A")
        comp_b = Node(label="Component B")
        self.service.create_node(comp_a)
        self.service.create_node(comp_b)

        original = self.service.create_delivery_matrix(
            label="Original Matrix",
            components=[comp_a.id, comp_b.id]
        )
        delivery = Delivery(
            delivery_type="information",
            delivery_content="Policy reports",
            quantity=12,
            units="reports/year"
        )
        self.service.add_delivery_to_matrix(
            original, comp_a.id, comp_b.id, delivery,
            cell_description="A sends reports to B"
        )

        # Convert to graph then back using class method
        G = original.to_multidigraph(self.service)
        reconstructed = SFMDeliveryMatrix.from_multidigraph(
            G, self.service, matrix_label="Roundtrip"
        )

        assert len(reconstructed.components) == 2
        cell = reconstructed.get_cell(comp_a.id, comp_b.id)
        assert cell is not None
        assert len(cell.deliveries) == 1
        assert cell.deliveries[0].delivery_type == "information"
        assert cell.deliveries[0].quantity == 12

    def test_from_multidigraph_empty_graph(self):
        """Test from_multidigraph with empty graph produces empty matrix."""
        G = nx.MultiDiGraph()

        matrix = SFMDeliveryMatrix.from_multidigraph(G, self.service)

        assert isinstance(matrix, SFMDeliveryMatrix)
        assert len(matrix.components) == 0
        assert len(matrix.cells) == 0

    def test_from_multidigraph_single_component(self):
        """Test from_multidigraph with single component (no edges)."""
        G = nx.MultiDiGraph()
        comp_a = uuid.uuid4()
        G.add_node(comp_a, label="Lone Component")

        matrix = SFMDeliveryMatrix.from_multidigraph(G, self.service)

        assert len(matrix.components) == 1
        assert comp_a in matrix.components
        assert len(matrix.cells) == 0


class TestAnalyzeMatrixAsGraph:
    """Test SFMService.analyze_matrix_as_graph() method."""

    def setup_method(self):
        """Setup test service and matrix with deliveries."""
        self.service = SFMService()

        self.comp_a = Node(label="Legislature")
        self.comp_b = Node(label="Agency")
        self.comp_c = Node(label="Community")

        self.service.create_node(self.comp_a)
        self.service.create_node(self.comp_b)
        self.service.create_node(self.comp_c)

        self.matrix = self.service.create_delivery_matrix(
            label="Policy Matrix",
            components=[self.comp_a.id, self.comp_b.id, self.comp_c.id]
        )

        self.service.add_delivery_to_matrix(
            self.matrix, self.comp_a.id, self.comp_b.id,
            Delivery(delivery_type="money", delivery_content="Budget appropriation",
                     quantity=10_000_000),
            cell_description="Legislature funds Agency"
        )

        self.service.add_delivery_to_matrix(
            self.matrix, self.comp_b.id, self.comp_c.id,
            Delivery(delivery_type="rule", delivery_content="Program guidelines"),
            cell_description="Agency regulates Community"
        )

        self.service.add_delivery_to_matrix(
            self.matrix, self.comp_c.id, self.comp_a.id,
            Delivery(delivery_type="information", delivery_content="Feedback reports"),
            cell_description="Community informs Legislature"
        )

    def test_analyze_returns_dict(self):
        """Test analyze_matrix_as_graph returns a dictionary."""
        result = self.service.analyze_matrix_as_graph(self.matrix)

        assert isinstance(result, dict)

    def test_analyze_node_count(self):
        """Test node_count matches number of components."""
        result = self.service.analyze_matrix_as_graph(self.matrix)

        assert result['node_count'] == 3

    def test_analyze_edge_count(self):
        """Test edge_count matches total deliveries."""
        result = self.service.analyze_matrix_as_graph(self.matrix)

        assert result['edge_count'] == 3

    def test_analyze_density(self):
        """Test density is a float between 0 and 1."""
        result = self.service.analyze_matrix_as_graph(self.matrix)

        assert isinstance(result['density'], float)
        assert 0.0 <= result['density'] <= 1.0

    def test_analyze_strongly_connected_components(self):
        """Test strongly_connected_components is a positive integer."""
        result = self.service.analyze_matrix_as_graph(self.matrix)

        assert isinstance(result['strongly_connected_components'], int)
        assert result['strongly_connected_components'] >= 1

    def test_analyze_detects_cycle(self):
        """Test cycles list contains the A→B→C→A cycle."""
        result = self.service.analyze_matrix_as_graph(self.matrix)

        assert isinstance(result['cycles'], list)
        # With A→B→C→A, there should be at least one cycle
        assert len(result['cycles']) >= 1

    def test_analyze_cycles_capped_at_ten(self):
        """Test cycles list is capped at 10 entries."""
        result = self.service.analyze_matrix_as_graph(self.matrix)

        assert len(result['cycles']) <= 10

    def test_analyze_centrality_keys(self):
        """Test centrality contains entries for each component."""
        result = self.service.analyze_matrix_as_graph(self.matrix)

        centrality = result['centrality']
        assert isinstance(centrality, dict)
        assert self.comp_a.id in centrality
        assert self.comp_b.id in centrality
        assert self.comp_c.id in centrality

    def test_analyze_centrality_values(self):
        """Test centrality values are floats between 0 and 1."""
        result = self.service.analyze_matrix_as_graph(self.matrix)

        for score in result['centrality'].values():
            assert isinstance(score, float)
            assert 0.0 <= score <= 1.0

    def test_analyze_empty_matrix(self):
        """Test analyze_matrix_as_graph works on empty matrix."""
        empty_matrix = self.service.create_delivery_matrix(
            label="Empty",
            components=[self.comp_a.id, self.comp_b.id]
        )
        result = self.service.analyze_matrix_as_graph(empty_matrix)

        assert result['node_count'] == 2
        assert result['edge_count'] == 0
        assert result['density'] == 0.0
        assert result['cycles'] == []

    def test_analyze_all_keys_present(self):
        """Test result contains all expected keys."""
        result = self.service.analyze_matrix_as_graph(self.matrix)

        expected_keys = {
            'node_count', 'edge_count', 'density',
            'strongly_connected_components', 'cycles', 'centrality'
        }
        assert expected_keys.issubset(result.keys())

