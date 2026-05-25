"""
Simple test to verify graph module works correctly.
"""

import uuid
from graph import SFMGraph, NetworkXSFMQueryEngine, Relationship
from models.base_nodes import Node
from models.cultural_analysis import (
    CeremonialInstrumentalClassification,
    ValueSystem,
)
from models.complex_analysis import ConflictDetection
from models.system_analysis import InstitutionalHolarchy
from models.sfm_enums import ConflictType, InstitutionalLevel


def test_basic_graph_operations():
    """Test basic graph operations."""
    print("Testing basic graph operations...")

    # Create graph
    graph = SFMGraph(name="Test Graph")

    # Create and add nodes
    node1 = Node(label="Node 1", description="Test node 1")
    node2 = Node(label="Node 2", description="Test node 2")

    graph.add_node(node1)
    graph.add_node(node2)

    # Add relationship
    rel = Relationship(source_id=node1.id, target_id=node2.id, kind="relates_to")
    graph.add_relationship(rel)

    # Verify
    assert len(graph) == 2, "Should have 2 nodes"
    assert len(graph.relationships) == 1, "Should have 1 relationship"

    # Test retrieval
    retrieved = graph.get_node_by_id(node1.id)
    assert retrieved is not None, "Should retrieve node"
    assert retrieved.label == "Node 1", "Label should match"

    print("✓ Basic graph operations passed")


def test_query_engine():
    """Test NetworkX query engine."""
    print("\nTesting query engine...")

    graph = SFMGraph(name="Query Test")

    # Create nodes
    node1 = Node(label="Central Node")
    node2 = Node(label="Node 2")
    node3 = Node(label="Node 3")

    graph.add_node(node1)
    graph.add_node(node2)
    graph.add_node(node3)

    # Add relationships
    graph.add_relationship(Relationship(source_id=node1.id, target_id=node2.id, kind="connects"))
    graph.add_relationship(Relationship(source_id=node1.id, target_id=node3.id, kind="connects"))

    # Create query engine
    query_engine = NetworkXSFMQueryEngine(graph)

    # Test centrality
    centrality = query_engine.get_node_centrality(node1.id, "degree")
    assert centrality > 0, "Central node should have non-zero centrality"

    # Test neighbors
    neighbors = query_engine.get_node_neighbors(node1.id)
    assert len(neighbors) == 2, "Should have 2 neighbors"

    # Test density
    density = query_engine.get_network_density()
    assert density > 0, "Network should have positive density"

    print("✓ Query engine tests passed")


def test_ceremonial_instrumental_query():
    """Test ceremonial vs instrumental classification query."""
    print("\nTesting ceremonial vs instrumental query...")

    graph = SFMGraph(name="Cultural Test")

    # Create ceremonial node
    ceremonial = CeremonialInstrumentalClassification(
        label="Ceremonial Behavior",
        ceremonial_score=0.8,
        instrumental_score=0.2
    )

    # Create instrumental node
    instrumental = CeremonialInstrumentalClassification(
        label="Instrumental Behavior",
        ceremonial_score=0.2,
        instrumental_score=0.9
    )

    graph.add_node(ceremonial)
    graph.add_node(instrumental)

    query_engine = NetworkXSFMQueryEngine(graph)
    results = query_engine.query_ceremonial_vs_instrumental(threshold=0.5)

    assert len(results["ceremonial"]) == 1, "Should have 1 ceremonial node"
    assert len(results["instrumental"]) == 1, "Should have 1 instrumental node"

    print("✓ Ceremonial vs instrumental query passed")


def test_circular_causation_query():
    """Test circular causation path query."""
    print("\nTesting circular causation query...")

    graph = SFMGraph(name="Causation Test")

    # Create a simple cycle: A -> B -> C -> A
    node_a = Node(label="Node A")
    node_b = Node(label="Node B")
    node_c = Node(label="Node C")

    graph.add_node(node_a)
    graph.add_node(node_b)
    graph.add_node(node_c)

    graph.add_relationship(Relationship(source_id=node_a.id, target_id=node_b.id, kind="causes"))
    graph.add_relationship(Relationship(source_id=node_b.id, target_id=node_c.id, kind="causes"))
    graph.add_relationship(Relationship(source_id=node_c.id, target_id=node_a.id, kind="causes"))

    query_engine = NetworkXSFMQueryEngine(graph)
    paths = query_engine.query_circular_causation_paths(node_a.id, max_depth=5)

    assert len(paths) > 0, "Should find circular causation paths"

    print("✓ Circular causation query passed")


def test_holarchy_query():
    """Test institutional holarchy query."""
    print("\nTesting holarchy query...")

    graph = SFMGraph(name="Holarchy Test")

    # Create holarchy structure
    holarchy = InstitutionalHolarchy(
        label="Test Holarchy",
        institutional_levels={
            InstitutionalLevel.CONSTITUTIONAL: [uuid.uuid4()],
            InstitutionalLevel.OPERATIONAL: [uuid.uuid4(), uuid.uuid4()],
        }
    )

    graph.add_node(holarchy)

    query_engine = NetworkXSFMQueryEngine(graph)
    levels = query_engine.query_holarchy_levels(holarchy.id)

    # Verify method returns expected structure
    assert isinstance(levels, dict), "Should return dict of levels"
    assert "organizational" in levels, "Should have organizational level key"

    print("✓ Holarchy query passed")


def test_conflict_detection():
    """Test conflict detection query."""
    print("\nTesting conflict detection...")

    graph = SFMGraph(name="Conflict Test")

    # Create conflict detection node
    conflict_detector = ConflictDetection(
        label="Conflict Analysis",
        analyzed_system_id=uuid.uuid4(),
        conflict_type=ConflictType.VALUE_CONFLICT,
        direct_conflicts=[
            {"id": "conflict1", "type": "value", "description": "Value clash"}
        ]
    )

    graph.add_node(conflict_detector)

    query_engine = NetworkXSFMQueryEngine(graph)
    conflicts = query_engine.detect_conflicts()

    assert len(conflicts) > 0, "Should detect conflicts"
    assert conflicts[0]["type"] == "direct", "Should identify direct conflict"

    print("✓ Conflict detection passed")


if __name__ == "__main__":
    test_basic_graph_operations()
    test_query_engine()
    test_ceremonial_instrumental_query()
    test_circular_causation_query()
    test_holarchy_query()
    test_conflict_detection()

    print("\n" + "=" * 50)
    print("All tests passed successfully!")
    print("=" * 50)
