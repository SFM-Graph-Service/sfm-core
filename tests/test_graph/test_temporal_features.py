"""Test temporal modeling features."""

import pytest
import uuid
from datetime import datetime, timedelta

from graph.sfm_graph import SFMGraph, Relationship
from models.base_nodes import Node, Event
from graph.sfm_query import NetworkXSFMQueryEngine


class TestTemporalFeatures:
    """Test suite for temporal modeling capabilities."""

    def setup_method(self):
        """Set up test fixtures."""
        self.graph = SFMGraph()
        self.query_engine = NetworkXSFMQueryEngine(self.graph)

    def test_relationship_has_temporal_fields(self):
        """Test that Relationship class has temporal fields."""
        node1 = Node(label="Node 1")
        node2 = Node(label="Node 2")
        self.graph.add_node(node1)
        self.graph.add_node(node2)

        rel = Relationship(
            source_id=node1.id,
            target_id=node2.id,
            kind="influences",
            weight=0.7
        )
        self.graph.add_relationship(rel)

        # Check temporal fields exist
        assert hasattr(rel, 'created_at')
        assert hasattr(rel, 'modified_at')
        assert hasattr(rel, 'valid_from')
        assert hasattr(rel, 'valid_to')
        assert hasattr(rel, 'version')
        assert hasattr(rel, 'previous_version_id')

        # Check default values
        assert isinstance(rel.created_at, datetime)
        assert rel.modified_at is None
        assert rel.valid_from is None
        assert rel.valid_to is None
        assert rel.version == 1
        assert rel.previous_version_id is None

    def test_event_node_creation(self):
        """Test Event node type creation."""
        event = Event(
            label="1975 Auto Standards Delay",
            description="Congress grants extension to auto industry",
            event_type="legislative",
            event_date=datetime(1975, 3, 15),
            impact_magnitude=0.8
        )

        self.graph.add_node(event)

        # Verify event fields
        assert event.event_type == "legislative"
        assert event.event_date == datetime(1975, 3, 15)
        assert event.impact_magnitude == 0.8
        assert isinstance(event.affected_nodes, list)
        assert isinstance(event.affected_relationships, list)

    def test_get_nodes_active_at_time(self):
        """Test temporal node queries."""
        # Create nodes at different times
        past_date = datetime.now() - timedelta(days=365)
        current_date = datetime.now()

        node1 = Node(label="Old Node", created_at=past_date)
        node2 = Node(label="New Node", created_at=current_date)

        self.graph.add_node(node1)
        self.graph.add_node(node2)

        # Query at intermediate time
        query_date = datetime.now() - timedelta(days=180)
        active = self.query_engine.get_nodes_active_at_time(query_date)

        # Should only find node1
        assert len(active) == 1
        assert active[0].label == "Old Node"

    def test_get_relationships_active_at_time(self):
        """Test relationship temporal validity."""
        node1 = Node(label="Node 1")
        node2 = Node(label="Node 2")
        self.graph.add_node(node1)
        self.graph.add_node(node2)

        # Create relationship with temporal validity
        rel = Relationship(
            source_id=node1.id,
            target_id=node2.id,
            kind="influences",
            weight=0.7,
            valid_from=datetime(1970, 1, 1),
            valid_to=datetime(1975, 12, 31)
        )
        self.graph.add_relationship(rel)

        # Query during validity period
        active_1972 = self.query_engine.get_relationships_active_at_time(datetime(1972, 6, 1))
        assert len(active_1972) == 1

        # Query after validity period
        active_1980 = self.query_engine.get_relationships_active_at_time(datetime(1980, 1, 1))
        assert len(active_1980) == 0

    def test_temporal_evolution_query(self):
        """Test query_temporal_evolution method."""
        # Create nodes and relationships with temporal data
        node1 = Node(label="Node 1", created_at=datetime(1970, 1, 1))
        node2 = Node(label="Node 2", created_at=datetime(1975, 1, 1))
        self.graph.add_node(node1)
        self.graph.add_node(node2)

        rel = Relationship(
            source_id=node1.id,
            target_id=node2.id,
            kind="influences",
            weight=0.8,
            valid_from=datetime(1970, 1, 1),
            valid_to=datetime(1980, 12, 31)
        )
        self.graph.add_relationship(rel)

        # Query evolution over time
        evolution = self.query_engine.query_temporal_evolution(
            start_date=datetime(1970, 1, 1),
            end_date=datetime(1980, 1, 1),
            time_step=timedelta(days=365*5)  # 5-year intervals
        )

        # Verify snapshots returned
        assert len(evolution) > 0
        assert all('date' in snap for snap in evolution)
        assert all('nodes' in snap for snap in evolution)
        assert all('relationships' in snap for snap in evolution)

    def test_relationship_weight_history(self):
        """Test tracking relationship weight changes."""
        node1 = Node(label="Node 1")
        node2 = Node(label="Node 2")
        self.graph.add_node(node1)
        self.graph.add_node(node2)

        rel = Relationship(
            source_id=node1.id,
            target_id=node2.id,
            kind="influences",
            weight=0.7
        )
        rel.meta["weight_history"] = [
            {
                "date": datetime(1975, 1, 1).isoformat(),
                "weight": 0.7,
                "previous_weight": 0.9,
                "reason": "Industry influence declined"
            }
        ]
        self.graph.add_relationship(rel)

        # Retrieve weight history
        history = self.query_engine.get_relationship_weight_history(rel.id)

        assert len(history) == 1
        assert history[0]["weight"] == 0.7
        assert history[0]["previous_weight"] == 0.9

    def test_get_relationship_by_id(self):
        """Test SFMGraph.get_relationship_by_id method."""
        node1 = Node(label="Node 1")
        node2 = Node(label="Node 2")
        self.graph.add_node(node1)
        self.graph.add_node(node2)

        rel = Relationship(
            source_id=node1.id,
            target_id=node2.id,
            kind="influences",
            weight=0.7
        )
        self.graph.add_relationship(rel)

        # Retrieve by ID
        retrieved = self.graph.get_relationship_by_id(rel.id)
        assert retrieved is not None
        assert retrieved.id == rel.id
        assert retrieved.kind == "influences"

        # Try non-existent ID
        non_existent = self.graph.get_relationship_by_id(uuid.uuid4())
        assert non_existent is None
