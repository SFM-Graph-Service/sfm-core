"""
Unit and integration tests for SFM query engine.
Tests the abstract query layer and NetworkX implementation for Phase 2.
"""

import unittest
import uuid
from typing import List, Dict

from models import Node
from models.base_nodes import Node as BaseNode
from models.sfm_enums import FlowNature
from models.cultural_analysis import CeremonialInstrumentalClassification
from models.complex_analysis import ConflictDetection
from models.system_analysis import InstitutionalHolarchy
from graph.sfm_graph import SFMGraph, Relationship
from graph.sfm_query import (
    SFMQueryEngine,
    NetworkXSFMQueryEngine,
    SFMQueryFactory,
    AnalysisType,
    QueryResult,
    NodeMetrics,
    FlowAnalysis,
)


class TestQueryDataClasses(unittest.TestCase):
    """Test data classes used in query results."""

    def test_query_result_creation(self):
        """Test QueryResult dataclass creation."""
        result = QueryResult(
            data={"test": "data"},
            query_type="centrality",
            parameters={"node_id": str(uuid.uuid4())},
            metadata={"execution_time": 0.1},
            timestamp="2025-06-19T10:00:00",
        )

        self.assertEqual(result.data, {"test": "data"})
        self.assertEqual(result.query_type, "centrality")
        self.assertIsInstance(result.parameters, dict)
        self.assertIsInstance(result.metadata, dict)

    def test_node_metrics_creation(self):
        """Test NodeMetrics dataclass creation."""
        node_id = uuid.uuid4()
        metrics = NodeMetrics(
            node_id=node_id,
            centrality_scores={"betweenness": 0.5, "closeness": 0.3},
            influence_score=0.7,
            dependency_score=0.4,
            connectivity=5,
            node_type="TestNode"
        )

        self.assertEqual(metrics.node_id, node_id)
        self.assertEqual(metrics.centrality_scores["betweenness"], 0.5)
        self.assertEqual(metrics.influence_score, 0.7)
        self.assertEqual(metrics.connectivity, 5)

    def test_flow_analysis_creation(self):
        """Test FlowAnalysis dataclass creation."""
        node_ids = [uuid.uuid4() for _ in range(3)]
        analysis = FlowAnalysis(
            flow_paths=[[node_ids[0], node_ids[1]], [node_ids[1], node_ids[2]]],
            bottlenecks=[node_ids[1]],
            flow_volumes={node_ids[1]: 100.0},
            efficiency_metrics={"overall": 0.8}
        )

        self.assertEqual(len(analysis.flow_paths), 2)
        self.assertEqual(len(analysis.bottlenecks), 1)
        self.assertIn(node_ids[1], analysis.bottlenecks)


class TestAnalysisType(unittest.TestCase):
    """Test AnalysisType enum."""

    def test_analysis_types_exist(self):
        """Test that all expected analysis types are defined."""
        expected_types = [
            "CENTRALITY",
            "INFLUENCE",
            "DEPENDENCY",
            "FLOW_ANALYSIS",
            "NETWORK_STRUCTURE",
            "POLICY_IMPACT",
            "SCENARIO_COMPARISON",
            "CEREMONIAL_INSTRUMENTAL",
            "CIRCULAR_CAUSATION",
            "HOLARCHY",
            "CONFLICT",
        ]

        for analysis_type in expected_types:
            self.assertTrue(hasattr(AnalysisType, analysis_type))


class TestNetworkXSFMQueryEngine(unittest.TestCase):
    """Test NetworkX-based query engine implementation."""

    def setUp(self):
        """Set up test graph and query engine."""
        self.graph = SFMGraph()

        # Create test nodes
        self.node1 = Node(label="Node1", description="First node")
        self.node2 = Node(label="Node2", description="Second node")
        self.node3 = Node(label="Node3", description="Third node")

        self.graph.add_node(self.node1)
        self.graph.add_node(self.node2)
        self.graph.add_node(self.node3)

        # Create test relationships
        self.rel1 = Relationship(
            source_id=self.node1.id,
            target_id=self.node2.id,
            kind="flows_to",
            weight=1.0
        )
        self.rel2 = Relationship(
            source_id=self.node2.id,
            target_id=self.node3.id,
            kind="flows_to",
            weight=1.0
        )

        self.graph.add_relationship(self.rel1)
        self.graph.add_relationship(self.rel2)

        # Create query engine
        self.engine = NetworkXSFMQueryEngine(self.graph)

    def test_engine_initialization(self):
        """Test query engine initialization."""
        self.assertIsNotNone(self.engine)
        self.assertEqual(self.engine.graph, self.graph)
        self.assertIsNotNone(self.engine.nx_graph)
        self.assertEqual(self.engine.nx_graph.number_of_nodes(), 3)

    def test_get_node_centrality(self):
        """Test node centrality calculation."""
        centrality = self.engine.get_node_centrality(self.node1.id, "betweenness")
        self.assertIsInstance(centrality, float)
        self.assertGreaterEqual(centrality, 0.0)
        self.assertLessEqual(centrality, 1.0)

        # Test other centrality types
        closeness = self.engine.get_node_centrality(self.node1.id, "closeness")
        self.assertIsInstance(closeness, float)

        degree = self.engine.get_node_centrality(self.node1.id, "degree")
        self.assertIsInstance(degree, float)

        # Test default (unknown type falls back to betweenness)
        default = self.engine.get_node_centrality(self.node1.id, "unknown")
        self.assertIsInstance(default, float)

    def test_get_most_central_nodes(self):
        """Test getting most central nodes."""
        central_nodes = self.engine.get_most_central_nodes(limit=2)
        self.assertIsInstance(central_nodes, list)
        self.assertLessEqual(len(central_nodes), 2)

        for node_id, score in central_nodes:
            self.assertIsInstance(node_id, uuid.UUID)
            self.assertIsInstance(score, float)

        # Test other centrality types
        closeness_nodes = self.engine.get_most_central_nodes(centrality_type="closeness", limit=2)
        self.assertIsInstance(closeness_nodes, list)

        degree_nodes = self.engine.get_most_central_nodes(centrality_type="degree", limit=2)
        self.assertIsInstance(degree_nodes, list)

        # Test with node type filter
        filtered_nodes = self.engine.get_most_central_nodes(node_type=Node, limit=2)
        self.assertIsInstance(filtered_nodes, list)

    def test_get_node_neighbors(self):
        """Test getting node neighbors."""
        neighbors = self.engine.get_node_neighbors(self.node1.id)
        self.assertIsInstance(neighbors, list)
        self.assertIn(self.node2.id, neighbors)

    def test_find_shortest_path(self):
        """Test finding shortest path between nodes."""
        path = self.engine.find_shortest_path(self.node1.id, self.node3.id)
        self.assertIsNotNone(path)
        self.assertEqual(path[0], self.node1.id)
        self.assertEqual(path[-1], self.node3.id)

    def test_find_cycles(self):
        """Test finding cycles in graph."""
        # Add cycle
        rel_cycle = Relationship(
            source_id=self.node3.id,
            target_id=self.node1.id,
            kind="flows_to"
        )
        self.graph.add_relationship(rel_cycle)

        engine = NetworkXSFMQueryEngine(self.graph)
        cycles = engine.find_cycles(max_length=5)

        self.assertIsInstance(cycles, list)
        # Should find at least one cycle
        self.assertGreater(len(cycles), 0)

    def test_identify_bottlenecks(self):
        """Test identifying bottleneck nodes."""
        bottlenecks = self.engine.identify_bottlenecks(FlowNature.MATERIAL)
        self.assertIsInstance(bottlenecks, list)

    def test_get_network_density(self):
        """Test network density calculation."""
        density = self.engine.get_network_density()
        self.assertIsInstance(density, float)
        self.assertGreaterEqual(density, 0.0)
        self.assertLessEqual(density, 1.0)

    def test_identify_communities(self):
        """Test community detection."""
        communities = self.engine.identify_communities()
        self.assertIsInstance(communities, dict)

    def test_comprehensive_node_analysis(self):
        """Test comprehensive node analysis."""
        metrics = self.engine.comprehensive_node_analysis(self.node1.id)

        self.assertIsInstance(metrics, NodeMetrics)
        self.assertEqual(metrics.node_id, self.node1.id)
        self.assertIsInstance(metrics.centrality_scores, dict)
        self.assertIn("betweenness", metrics.centrality_scores)
        self.assertIn("closeness", metrics.centrality_scores)
        self.assertIn("degree", metrics.centrality_scores)


class TestBetaQueryMethods(unittest.TestCase):
    """Test Beta framework query methods (Phase 2 extensions)."""

    def setUp(self):
        """Set up test graph with Beta model nodes."""
        self.graph = SFMGraph()

        # Create nodes with ceremonial/instrumental characteristics
        self.ceremonial_node = CeremonialInstrumentalClassification(
            label="Ceremonial Node",
            description="Status quo reinforcing",
            ceremonial_score=0.8,
            instrumental_score=0.2
        )

        self.instrumental_node = CeremonialInstrumentalClassification(
            label="Instrumental Node",
            description="Problem solving",
            ceremonial_score=0.2,
            instrumental_score=0.9
        )

        self.mixed_node = Node(
            label="Mixed Node",
            description="Mixed characteristics",
            meta={"ceremonial_score": "0.4", "instrumental_score": "0.4"}
        )

        self.graph.add_node(self.ceremonial_node)
        self.graph.add_node(self.instrumental_node)
        self.graph.add_node(self.mixed_node)

        self.engine = NetworkXSFMQueryEngine(self.graph)

    def test_query_ceremonial_vs_instrumental(self):
        """Test ceremonial vs instrumental classification query."""
        results = self.engine.query_ceremonial_vs_instrumental(threshold=0.5)

        self.assertIsInstance(results, dict)
        self.assertIn("ceremonial", results)
        self.assertIn("instrumental", results)
        self.assertIn("mixed", results)

        # Assert non-empty classification
        total_classified = len(results["ceremonial"]) + len(results["instrumental"]) + len(results["mixed"])
        self.assertGreater(total_classified, 0, "Expected nodes to be classified")

        # Verify ceremonial node is classified correctly
        ceremonial_ids = [n.id for n in results["ceremonial"]]
        self.assertIn(self.ceremonial_node.id, ceremonial_ids)

        # Verify instrumental node is classified correctly
        instrumental_ids = [n.id for n in results["instrumental"]]
        self.assertIn(self.instrumental_node.id, instrumental_ids)

    def test_query_circular_causation_paths(self):
        """Test circular causation path detection."""
        # Create circular path
        node1 = Node(label="Node1", description="First")
        node2 = Node(label="Node2", description="Second")
        node3 = Node(label="Node3", description="Third")

        self.graph.add_node(node1)
        self.graph.add_node(node2)
        self.graph.add_node(node3)

        # Create cycle: node1 -> node2 -> node3 -> node1
        self.graph.add_relationship(Relationship(
            source_id=node1.id, target_id=node2.id, kind="causes"
        ))
        self.graph.add_relationship(Relationship(
            source_id=node2.id, target_id=node3.id, kind="causes"
        ))
        self.graph.add_relationship(Relationship(
            source_id=node3.id, target_id=node1.id, kind="causes"
        ))

        engine = NetworkXSFMQueryEngine(self.graph)
        paths = engine.query_circular_causation_paths(node1.id, max_depth=5)

        self.assertIsInstance(paths, list)
        self.assertGreater(len(paths), 0, "Expected to find at least one circular path")
        self.assertIsInstance(paths[0], list)
        self.assertIsInstance(paths[0][0], Node)
        self.assertEqual(paths[0][0].id, node1.id, "Cycle should start with source node")
        self.assertEqual(paths[0][-1].id, node1.id, "Cycle should end with source node")

    def test_query_circular_causation_paths_two_node_cycle(self):
        """Test that 2-node (mutual) cycles are detected by query_circular_causation_paths."""
        nodeA = Node(label="NodeA", description="First node in mutual cycle")
        nodeB = Node(label="NodeB", description="Second node in mutual cycle")
        self.graph.add_node(nodeA)
        self.graph.add_node(nodeB)

        # Create mutual (2-node) cycle via explicit Relationship objects: A → B and B → A
        self.graph.add_relationship(Relationship(
            source_id=nodeA.id, target_id=nodeB.id, kind="influences"
        ))
        self.graph.add_relationship(Relationship(
            source_id=nodeB.id, target_id=nodeA.id, kind="influences"
        ))

        engine = NetworkXSFMQueryEngine(self.graph)
        paths_a = engine.query_circular_causation_paths(nodeA.id, max_depth=5)
        paths_b = engine.query_circular_causation_paths(nodeB.id, max_depth=5)

        self.assertGreater(len(paths_a), 0, "Should detect 2-node cycle from nodeA")
        self.assertGreater(len(paths_b), 0, "Should detect 2-node cycle from nodeB")

    def test_build_networkx_graph_includes_delivery_cell_edges(self):
        """Test that SFMDeliveryCell nodes contribute edges to the NetworkX graph."""
        from models.delivery_matrix import Delivery, SFMDeliveryCell

        src = Node(label="Source", description="Delivery source")
        tgt = Node(label="Target", description="Delivery target")
        self.graph.add_node(src)
        self.graph.add_node(tgt)

        # Create an SFMDeliveryCell (delivery matrix entry) instead of a Relationship
        cell = SFMDeliveryCell(
            label="Source→Target",
            source_component_id=src.id,
            target_component_id=tgt.id,
            cell_description="Test delivery",
        )
        cell.add_delivery(Delivery(
            delivery_type="information",
            delivery_content="test",
            certainty=0.8,
        ))
        self.graph.add_node(cell)

        engine = NetworkXSFMQueryEngine(self.graph)

        # The edge derived from the delivery cell should be present
        self.assertTrue(
            engine.nx_graph.has_edge(src.id, tgt.id),
            "NetworkX graph should include edge derived from SFMDeliveryCell",
        )

    def test_circular_causation_via_delivery_matrix(self):
        """Test that circular causation is detected when cycle is encoded as delivery cells."""
        from models.delivery_matrix import Delivery, SFMDeliveryCell

        epa = Node(label="EPA", description="Federal agency")
        state = Node(label="State", description="State agency")
        self.graph.add_node(epa)
        self.graph.add_node(state)

        # EPA → State delivery cell
        cell_es = SFMDeliveryCell(
            label="EPA→State",
            source_component_id=epa.id,
            target_component_id=state.id,
            cell_description="EPA sets standards for state",
        )
        cell_es.add_delivery(Delivery(delivery_type="rule", delivery_content="NAAQS", certainty=1.0))
        self.graph.add_node(cell_es)

        # State → EPA delivery cell (creates the feedback loop)
        cell_se = SFMDeliveryCell(
            label="State→EPA",
            source_component_id=state.id,
            target_component_id=epa.id,
            cell_description="State submits implementation plans to EPA",
        )
        cell_se.add_delivery(Delivery(delivery_type="information", delivery_content="SIP", certainty=0.95))
        self.graph.add_node(cell_se)

        engine = NetworkXSFMQueryEngine(self.graph)
        paths = engine.query_circular_causation_paths(epa.id, max_depth=5)

        self.assertGreater(
            len(paths), 0,
            "Should detect circular causation when cycle is encoded via SFMDeliveryCell nodes",
        )

    def test_query_holarchy_levels(self):
        """Test institutional holarchy query."""
        # Create institution
        institution = InstitutionalHolarchy(
            label="Test Institution",
            description="Test holarchy"
        )
        self.graph.add_node(institution)

        engine = NetworkXSFMQueryEngine(self.graph)
        levels = engine.query_holarchy_levels(institution.id)

        self.assertIsInstance(levels, dict)
        expected_keys = ["global", "national", "regional", "local", "organizational", "individual"]
        for key in expected_keys:
            self.assertIn(key, levels)
            self.assertIsInstance(levels[key], list)

    def test_detect_conflicts(self):
        """Test conflict detection."""
        # Create conflict detection node
        conflict_node = ConflictDetection(
            label="Test Conflict",
            description="Test conflict detection",
            analyzed_system_id=uuid.uuid4(),
            direct_conflicts=["Conflict A", "Conflict B"],
            indirect_conflicts=["Indirect C"]
        )
        self.graph.add_node(conflict_node)

        # Add contradictory relationships
        node1 = Node(label="Node1", description="First")
        node2 = Node(label="Node2", description="Second")
        self.graph.add_node(node1)
        self.graph.add_node(node2)

        self.graph.add_relationship(Relationship(
            source_id=node1.id, target_id=node2.id, kind="supports", weight=1.0
        ))
        self.graph.add_relationship(Relationship(
            source_id=node1.id, target_id=node2.id, kind="opposes", weight=-1.0
        ))

        engine = NetworkXSFMQueryEngine(self.graph)
        conflicts = engine.detect_conflicts()

        self.assertIsInstance(conflicts, list)
        self.assertGreater(len(conflicts), 0, "Expected to find conflicts")
        conflict = conflicts[0]
        self.assertIn("type", conflict)
        self.assertIn("conflict_type", conflict)


class TestSFMQueryFactory(unittest.TestCase):
    """Test query engine factory."""

    def test_create_networkx_engine(self):
        """Test creating NetworkX query engine."""
        graph = SFMGraph()
        engine = SFMQueryFactory.create_query_engine(graph, backend="networkx")

        self.assertIsInstance(engine, NetworkXSFMQueryEngine)
        self.assertEqual(engine.graph, graph)

    def test_invalid_backend_raises_error(self):
        """Test that invalid backend raises ValueError."""
        graph = SFMGraph()

        with self.assertRaises(ValueError):
            SFMQueryFactory.create_query_engine(graph, backend="invalid")


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""

    def test_empty_graph_operations(self):
        """Test operations on empty graph."""
        graph = SFMGraph()
        engine = NetworkXSFMQueryEngine(graph)

        # Should handle empty graph gracefully
        density = engine.get_network_density()
        self.assertEqual(density, 0.0)

        communities = engine.identify_communities()
        self.assertEqual(communities, {})

        bottlenecks = engine.identify_bottlenecks(FlowNature.MATERIAL)
        self.assertEqual(bottlenecks, [])

    def test_nonexistent_node_operations(self):
        """Test operations on nonexistent nodes."""
        graph = SFMGraph()
        node = Node(label="Test", description="Test node")
        graph.add_node(node)

        engine = NetworkXSFMQueryEngine(graph)

        # Query nonexistent node
        fake_id = uuid.uuid4()
        neighbors = engine.get_node_neighbors(fake_id)
        self.assertEqual(neighbors, [])

        # Path to nonexistent node
        path = engine.find_shortest_path(node.id, fake_id)
        self.assertIsNone(path)

    def test_single_node_graph(self):
        """Test operations on single-node graph."""
        graph = SFMGraph()
        node = Node(label="Solo", description="Only node")
        graph.add_node(node)

        engine = NetworkXSFMQueryEngine(graph)

        centrality = engine.get_node_centrality(node.id)
        self.assertEqual(centrality, 0.0)

        metrics = engine.comprehensive_node_analysis(node.id)
        self.assertEqual(metrics.connectivity, 0)


class TestUncertaintyAnalysis(unittest.TestCase):
    """Test uncertainty analysis methods (Gap 3)."""

    def setUp(self):
        """Set up test graph with uncertainty data."""
        self.graph = SFMGraph()

        # Create test nodes
        self.node1 = Node(label="Node1", description="First node")
        self.node2 = Node(label="Node2", description="Second node")
        self.node3 = Node(label="Node3", description="Third node")

        self.graph.add_node(self.node1)
        self.graph.add_node(self.node2)
        self.graph.add_node(self.node3)

        # Create relationships with confidence intervals
        self.rel1 = Relationship(
            source_id=self.node1.id,
            target_id=self.node2.id,
            kind="produces",
            weight=0.8,
            confidence_interval=(0.7, 0.9),
            confidence=0.85,
            uncertainty_type="epistemic",
            data_sources=["EPA 1997", "Industry studies"],
            source_agreement="low"
        )
        self.rel2 = Relationship(
            source_id=self.node2.id,
            target_id=self.node3.id,
            kind="enables",
            weight=0.6,
            confidence_interval=(0.5, 0.7),
            confidence=0.75,
            uncertainty_type="aleatory"
        )
        self.rel3 = Relationship(
            source_id=self.node1.id,
            target_id=self.node3.id,
            kind="influences",
            weight=0.5
            # No confidence interval
        )

        self.graph.add_relationship(self.rel1)
        self.graph.add_relationship(self.rel2)
        self.graph.add_relationship(self.rel3)

        self.engine = NetworkXSFMQueryEngine(self.graph)

    def test_analyze_weight_uncertainty(self):
        """Test weight uncertainty analysis."""
        result = self.engine.analyze_weight_uncertainty()

        self.assertIsInstance(result, dict)
        self.assertIn("total_relationships", result)
        self.assertIn("with_confidence_intervals", result)
        self.assertIn("without_confidence_intervals", result)
        self.assertIn("coverage", result)
        self.assertIn("avg_uncertainty_range", result)

        # Verify counts
        self.assertEqual(result["total_relationships"], 3)
        self.assertEqual(result["with_confidence_intervals"], 2)
        self.assertEqual(result["without_confidence_intervals"], 1)

        # Verify coverage calculation
        expected_coverage = 2 / 3
        self.assertAlmostEqual(result["coverage"], expected_coverage, places=5)

        # Verify average uncertainty range
        # rel1: 0.9 - 0.7 = 0.2, rel2: 0.7 - 0.5 = 0.2, avg = 0.2
        self.assertAlmostEqual(result["avg_uncertainty_range"], 0.2, places=5)

    def test_propagate_uncertainty_through_path(self):
        """Test uncertainty propagation through pathway."""
        # Create path node1 -> node2 -> node3
        path = [self.node1.id, self.node2.id, self.node3.id]
        result = self.engine.propagate_uncertainty_through_path(path)

        self.assertIsInstance(result, dict)
        self.assertIn("path_segments", result)
        self.assertIn("cumulative_effect", result)
        self.assertIn("uncertainty_range", result)
        self.assertIn("uncertainty_width", result)

        # Verify path segments
        self.assertEqual(len(result["path_segments"]), 2)

        # Verify cumulative effect (0.8 * 0.6 = 0.48)
        expected_effect = 0.8 * 0.6
        self.assertAlmostEqual(result["cumulative_effect"], expected_effect, places=5)

        # Verify uncertainty range
        # Lower: 0.7 * 0.5 = 0.35
        # Upper: 0.9 * 0.7 = 0.63
        lower, upper = result["uncertainty_range"]
        self.assertAlmostEqual(lower, 0.35, places=5)
        self.assertAlmostEqual(upper, 0.63, places=5)

        # Verify uncertainty width
        expected_width = 0.63 - 0.35
        self.assertAlmostEqual(result["uncertainty_width"], expected_width, places=5)

    def test_sensitivity_analysis(self):
        """Test sensitivity analysis."""
        # Create simple causal chain
        result = self.engine.sensitivity_analysis(
            outcome_node_id=self.node3.id,
            vary_percentage=0.2
        )

        self.assertIsInstance(result, dict)
        self.assertIn("outcome_node", result)
        self.assertIn("sensitivity_ranking", result)

        # Verify outcome node
        self.assertEqual(result["outcome_node"], "Node3")

        # Verify rankings structure (even if empty, should be a list)
        self.assertIsInstance(result["sensitivity_ranking"], list)

    def test_relationship_uncertainty_fields(self):
        """Test that uncertainty fields are properly set on relationships."""
        # Verify rel1 has all uncertainty fields
        self.assertEqual(self.rel1.confidence, 0.85)
        self.assertEqual(self.rel1.confidence_interval, (0.7, 0.9))
        self.assertEqual(self.rel1.uncertainty_type, "epistemic")
        self.assertEqual(len(self.rel1.data_sources), 2)
        self.assertIn("EPA 1997", self.rel1.data_sources)
        self.assertEqual(self.rel1.source_agreement, "low")

        # Verify rel3 has None for missing fields
        self.assertIsNone(self.rel3.confidence)
        self.assertIsNone(self.rel3.confidence_interval)
        self.assertIsNone(self.rel3.uncertainty_type)
        self.assertEqual(len(self.rel3.data_sources), 0)
        self.assertIsNone(self.rel3.source_agreement)

    def test_empty_graph_uncertainty(self):
        """Test uncertainty analysis on empty graph."""
        empty_graph = SFMGraph()
        engine = NetworkXSFMQueryEngine(empty_graph)

        result = engine.analyze_weight_uncertainty()
        self.assertEqual(result["total_relationships"], 0)
        self.assertEqual(result["with_confidence_intervals"], 0)
        self.assertEqual(result["coverage"], 0)
        self.assertEqual(result["avg_uncertainty_range"], 0.0)


if __name__ == "__main__":
    unittest.main()
