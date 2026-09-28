"""Every persistence path must round-trip every Relationship field."""

import uuid
from datetime import datetime

import pytest

from graph.sfm_graph import Relationship, SFMGraph
from graph.sfm_persistence import (
    RelationshipSerializer,
    SFMGraphSerializer,
    SFMPersistenceManager,
    StorageFormat,
)
from models import Node


def _rich(a: Node, b: Node) -> Relationship:
    return Relationship(
        source_id=a.id, target_id=b.id, kind="funds", weight=0.8,
        meta={"note": "x", "nested": {"k": [1, 2]}},
        confidence=0.9, confidence_interval=(0.7, 0.9), uncertainty_type="epistemic",
        data_sources=["A", "B"], source_agreement="high",
        valid_from=datetime(2026, 1, 1), valid_to=datetime(2026, 12, 31),
    )


def _assert_rich(rel: Relationship, original: Relationship) -> None:
    assert rel.id == original.id
    assert rel.source_id == original.source_id and rel.target_id == original.target_id
    assert rel.kind == "funds" and rel.weight == 0.8
    assert rel.meta == {"note": "x", "nested": {"k": [1, 2]}}
    assert rel.confidence == 0.9
    assert tuple(rel.confidence_interval) == (0.7, 0.9)
    assert rel.uncertainty_type == "epistemic"
    assert rel.data_sources == ["A", "B"]
    assert rel.source_agreement == "high"
    assert rel.valid_from == datetime(2026, 1, 1)
    assert rel.valid_to == datetime(2026, 12, 31)


@pytest.fixture
def graph():
    g = SFMGraph()
    a, b = Node(label="A"), Node(label="B")
    g.add_node(a)
    g.add_node(b)
    g.add_relationship(_rich(a, b))
    return g


def test_serializer_round_trip():
    a, b = Node(label="A"), Node(label="B")
    original = _rich(a, b)
    restored = RelationshipSerializer.from_dict(RelationshipSerializer.to_dict(original))
    _assert_rich(restored, original)


def test_serializer_omits_unset_fields_and_reads_legacy_shape():
    a, b = Node(label="A"), Node(label="B")
    bare = Relationship(source_id=a.id, target_id=b.id, kind="x", weight=0.3)
    data = RelationshipSerializer.to_dict(bare)
    assert set(data) == {"id", "source_id", "target_id", "kind", "weight"}

    legacy = {"id": str(uuid.uuid4()), "source_id": str(a.id), "target_id": str(b.id), "kind": "x", "weight": 0.3}
    restored = RelationshipSerializer.from_dict(legacy)
    assert restored.weight == 0.3 and restored.meta == {} and restored.data_sources == []
    assert restored.confidence is None and restored.confidence_interval is None


def test_graph_serializer_round_trip(graph):
    original = next(iter(graph.relationships.values()))
    for fmt in (StorageFormat.JSON, StorageFormat.COMPRESSED_JSON):
        blob = SFMGraphSerializer.serialize_graph(graph, fmt)
        restored_graph = SFMGraphSerializer.deserialize_graph(blob, fmt)
        assert len(restored_graph.relationships) == 1
        _assert_rich(next(iter(restored_graph.relationships.values())), original)


def test_persistence_manager_snapshot_round_trip(graph, tmp_path):
    manager = SFMPersistenceManager(str(tmp_path))
    original = next(iter(graph.relationships.values()))

    path = str(tmp_path / "snap.json")
    manager.export_json_snapshot(graph, path)
    restored = manager.import_json_snapshot(path)
    _assert_rich(next(iter(restored.relationships.values())), original)

    manager.save_graph(graph, "g.json")
    loaded = manager.load_graph("g.json")
    _assert_rich(next(iter(loaded.relationships.values())), original)
