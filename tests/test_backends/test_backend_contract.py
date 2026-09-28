"""
Backend contract: every storage backend must behave identically through SFMService.

Runs against NetworkX always and against Neo4j when NEO4J_URI is set (see
tests/conftest.py). Anything asserted here is a guarantee the service makes
regardless of backend, so a failure on one backend only is backend drift.
"""

from __future__ import annotations

import uuid
from datetime import datetime

import pytest

from graph.sfm_graph import Relationship
from models import Node
from models.exceptions import GraphSizeExceededError, SFMNotFoundError, NodeCreationError
from models.policy_framework import PolicyInstrument
from api.sfm_service import SFMService, SFMServiceConfig


def _rich_relationship(source: Node, target: Node) -> Relationship:
    return Relationship(
        source_id=source.id,
        target_id=target.id,
        kind="funds",
        weight=0.8,
        meta={"note": "appropriation", "nested": {"fy": 2026, "items": [1, 2]}},
        confidence=0.9,
        confidence_interval=(0.7, 0.9),
        uncertainty_type="epistemic",
        data_sources=["Budget Act 2026", "Audit report"],
        source_agreement="high",
        valid_from=datetime(2026, 7, 1, 0, 0, 0),
        valid_to=datetime(2027, 6, 30, 0, 0, 0),
    )


class TestNodeContract:
    def test_create_read_update_delete(self, backend_service):
        svc = backend_service
        node = svc.create_node(Node(label="Legislature", description="Lawmaking body", meta={"tier": "state"}))

        fetched = svc.get_node(node.id)
        assert fetched is not None
        assert fetched.id == node.id
        assert fetched.label == "Legislature"
        assert fetched.description == "Lawmaking body"
        assert fetched.meta == {"tier": "state"}

        fetched.description = "Amended"
        svc.update_node(fetched)
        assert svc.get_node(node.id).description == "Amended"

        assert svc.delete_node(node.id) is True
        assert svc.get_node(node.id) is None
        assert svc.delete_node(node.id) is False

    def test_duplicate_id_is_rejected(self, backend_service):
        node = backend_service.create_node(Node(label="A"))
        with pytest.raises(NodeCreationError):
            backend_service.create_node(Node(id=node.id, label="A again"))

    def test_typed_nodes_round_trip_and_filter(self, backend_service):
        svc = backend_service
        svc.create_node(Node(label="plain"))
        instrument = svc.create_node(PolicyInstrument(label="Emission Standard", description="Rule"))

        fetched = svc.get_node(instrument.id)
        assert isinstance(fetched, PolicyInstrument)
        assert fetched.label == "Emission Standard"

        instruments = svc.list_nodes(PolicyInstrument)
        assert [n.id for n in instruments] == [instrument.id]
        assert len(svc.list_nodes()) == 2

    def test_count_nodes_and_size_limit(self, backend):
        import os
        if backend == "neo4j":
            config = SFMServiceConfig(
                storage_type="neo4j", graph_size_limit=2,
                neo4j_uri=os.environ["NEO4J_URI"],
                neo4j_username=os.getenv("NEO4J_USERNAME", "neo4j"),
                neo4j_password=os.getenv("NEO4J_PASSWORD", "password"),
            )
        else:
            config = SFMServiceConfig(graph_size_limit=2)
        svc = SFMService(config)
        svc.repository.clear()
        try:
            svc.create_node(Node(label="1"))
            svc.create_node(Node(label="2"))
            assert svc.repository.count_nodes() == 2
            with pytest.raises(GraphSizeExceededError):
                svc.create_node(Node(label="3"))
            assert svc.repository.count_nodes() == 2
        finally:
            svc.repository.clear()

    def test_bulk_create(self, backend_service):
        nodes = [Node(label=f"N{i}") for i in range(25)]
        created = backend_service.repository.create_nodes_bulk(nodes)
        assert len(created) == 25
        assert backend_service.repository.count_nodes() == 25
        assert {n.label for n in backend_service.list_nodes()} == {f"N{i}" for i in range(25)}


class TestRelationshipContract:
    def test_uncertainty_fields_round_trip(self, backend_service):
        svc = backend_service
        a = svc.create_node(Node(label="A"))
        b = svc.create_node(Node(label="B"))
        rel = svc.create_relationship(_rich_relationship(a, b))

        for fetched in (svc.get_relationship(rel.id), svc.list_relationships()[0]):
            assert fetched.id == rel.id
            assert fetched.source_id == a.id and fetched.target_id == b.id
            assert fetched.kind == "funds"
            assert fetched.weight == 0.8
            assert fetched.meta == {"note": "appropriation", "nested": {"fy": 2026, "items": [1, 2]}}
            assert fetched.confidence == 0.9
            assert tuple(fetched.confidence_interval) == (0.7, 0.9)
            assert fetched.uncertainty_type == "epistemic"
            assert fetched.data_sources == ["Budget Act 2026", "Audit report"]
            assert fetched.source_agreement == "high"
            assert fetched.valid_from == datetime(2026, 7, 1, 0, 0, 0)
            assert fetched.valid_to == datetime(2027, 6, 30, 0, 0, 0)

    def test_update_and_delete(self, backend_service):
        svc = backend_service
        a = svc.create_node(Node(label="A"))
        b = svc.create_node(Node(label="B"))
        rel = svc.create_relationship(Relationship(source_id=a.id, target_id=b.id, kind="funds", weight=0.5))

        rel.weight = 0.9
        rel.confidence = 0.4
        svc.update_relationship(rel)
        fetched = svc.get_relationship(rel.id)
        assert fetched.weight == 0.9
        assert fetched.confidence == 0.4

        assert svc.delete_relationship(rel.id) is True
        assert svc.get_relationship(rel.id) is None
        assert svc.delete_relationship(rel.id) is False

    def test_missing_endpoint_is_rejected(self, backend_service):
        a = backend_service.create_node(Node(label="A"))
        with pytest.raises(Exception) as excinfo:
            backend_service.create_relationship(
                Relationship(source_id=a.id, target_id=uuid.uuid4(), kind="funds")
            )
        assert excinfo.type.__name__ in {"SFMNotFoundError", "RelationshipValidationError"}

    def test_deleting_node_removes_incident_relationships(self, backend_service):
        svc = backend_service
        a = svc.create_node(Node(label="A"))
        b = svc.create_node(Node(label="B"))
        c = svc.create_node(Node(label="C"))
        svc.create_relationship(Relationship(source_id=a.id, target_id=b.id, kind="x"))
        svc.create_relationship(Relationship(source_id=b.id, target_id=c.id, kind="x"))
        keep = svc.create_relationship(Relationship(source_id=a.id, target_id=c.id, kind="x"))

        svc.delete_node(b.id)
        assert [r.id for r in svc.list_relationships()] == [keep.id]

    def test_bulk_create_relationships(self, backend_service):
        svc = backend_service
        nodes = [svc.create_node(Node(label=f"N{i}")) for i in range(6)]
        rels = [
            Relationship(source_id=nodes[i].id, target_id=nodes[(i + 1) % 6].id, kind="next", weight=0.5)
            for i in range(6)
        ]
        created = svc.create_relationships_bulk(rels)
        assert len(created) == 6
        assert len(svc.list_relationships()) == 6
        assert len(svc.list_relationships(kind="next")) == 6
        assert svc.list_relationships(kind="other") == []


class TestGraphContract:
    def test_clear_and_load_graph(self, backend_service):
        svc = backend_service
        a = svc.create_node(Node(label="A"))
        b = svc.create_node(Node(label="B"))
        svc.create_relationship(_rich_relationship(a, b))

        graph = svc.repository.load_graph()
        assert {n.label for n in graph} == {"A", "B"}
        assert len(graph.relationships) == 1
        loaded = next(iter(graph.relationships.values()))
        assert loaded.data_sources == ["Budget Act 2026", "Audit report"]

        svc.clear_all_data()
        assert svc.list_nodes() == []
        assert svc.list_relationships() == []
        assert svc.repository.count_nodes() == 0


class TestAnalysisParity:
    """The same institutional model must yield the same analysis on every backend."""

    @pytest.fixture
    def model(self, backend_service):
        svc = backend_service
        epa = svc.create_node(Node(label="EPA"))
        standards = svc.create_node(Node(label="Standards"))
        industry = svc.create_node(Node(label="Industry"))
        lobby = svc.create_node(Node(label="Lobby"))
        svc.create_relationship(Relationship(source_id=epa.id, target_id=standards.id, kind="mandates",
                                             weight=0.9, confidence=0.8, confidence_interval=(0.8, 1.0),
                                             data_sources=["CAA 1990"]))
        svc.create_relationship(Relationship(source_id=standards.id, target_id=industry.id, kind="constrains",
                                             weight=-0.6, confidence=0.5))
        svc.create_relationship(Relationship(source_id=industry.id, target_id=lobby.id, kind="funds", weight=0.7))
        svc.create_relationship(Relationship(source_id=lobby.id, target_id=epa.id, kind="influences", weight=0.5))
        svc.create_relationship(Relationship(source_id=lobby.id, target_id=standards.id, kind="opposes", weight=0.85))
        svc.initialize_query_engine()
        return {"svc": svc, "epa": epa, "standards": standards, "lobby": lobby}

    def test_circular_causation_identical_across_backends(self, model):
        cycles = model["svc"].get_circular_causation(model["epa"].id)
        assert len(cycles) == 1
        cycle = cycles[0]
        assert cycle["labels"] == ["EPA", "Standards", "Industry", "Lobby", "EPA"]
        assert cycle["feedback_type"] == "balancing"
        assert cycle["negative_links"] == 1
        assert cycle["strength"] == pytest.approx(0.9 * 0.6 * 0.7 * 0.5)
        assert cycle["strength_range"][0] == pytest.approx(0.8 * 0.6 * 0.7 * 0.5)
        assert cycle["strength_range"][1] == pytest.approx(1.0 * 0.6 * 0.7 * 0.5)
        assert cycle["confidence"] == 0.5
        assert cycle["weakest_link"]["kind"] == "constrains"

    def test_conflicts_identical_across_backends(self, model):
        conflicts = model["svc"].get_conflicts()
        assert len(conflicts) == 1
        assert conflicts[0]["description"] == "Lobby opposes Standards"
        assert conflicts[0]["severity_label"] == "high"
        assert conflicts[0]["evidence_strength"] == "none"

    def test_leverage_and_data_quality_identical_across_backends(self, model):
        svc = model["svc"]
        leverage = svc.get_leverage_points()
        assert leverage["nodes_in_loops"] == 4
        assert {p["label"] for p in leverage["leverage_points"]} == {"EPA", "Standards", "Industry", "Lobby"}

        quality = svc.get_data_quality_report()
        assert quality["total_relationships"] == 5
        assert quality["with_data_sources"] == 1
        assert quality["with_confidence_interval"] == 1
        assert quality["with_confidence"] == 2
        assert quality["by_uncertainty_type"] == {"unspecified": 5}

    def test_query_engine_rebuilds_after_mutation(self, model):
        svc = model["svc"]
        assert len(svc.query_engine.graph) == 4
        svc.create_node(Node(label="Courts"))
        assert len(svc.query_engine.graph) == 5
