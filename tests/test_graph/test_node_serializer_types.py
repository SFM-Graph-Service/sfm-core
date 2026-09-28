"""Typed fields (datetime, UUID, Enum, and containers of them) survive a NodeSerializer round trip."""

import json
import uuid
from datetime import datetime

from graph.sfm_persistence import NodeSerializer
from models import Node
from models.complex_analysis import ConflictDetection, DigraphAnalysis
from models.enums.relationships import ConflictType


def _through_json(node):
    """Emulate disk: serialise, dump to JSON text with the service's fallbacks, parse, rebuild."""
    text = json.dumps(NodeSerializer.node_to_dict(node), default=str)
    return NodeSerializer.dict_to_node(json.loads(text))


def test_base_node_datetimes_are_restored():
    node = Node(label="n", created_at=datetime(2026, 1, 2, 3, 4, 5), modified_at=datetime(2026, 2, 3))
    restored = _through_json(node)
    assert restored.created_at == datetime(2026, 1, 2, 3, 4, 5)
    assert restored.modified_at == datetime(2026, 2, 3)
    assert isinstance(restored.id, uuid.UUID)


def test_uuid_lists_and_non_core_datetimes_are_restored():
    ids = [uuid.uuid4(), uuid.uuid4()]
    node = DigraphAnalysis(
        label="d",
        analyzed_institutions=ids,
        analysis_timestamp=datetime(2025, 6, 1, 12, 0),
        cycle_detection=[[ids[0], ids[1]]],
    )
    restored = _through_json(node)
    assert restored.analyzed_institutions == ids
    assert all(isinstance(i, uuid.UUID) for i in restored.analyzed_institutions)
    assert restored.analysis_timestamp == datetime(2025, 6, 1, 12, 0)
    assert restored.cycle_detection == [[ids[0], ids[1]]]


def test_enums_and_uuid_tuples_are_restored():
    a, b = uuid.uuid4(), uuid.uuid4()
    node = ConflictDetection(
        label="c",
        conflict_type=ConflictType.RESOURCE_CONFLICT,
        analyzed_system_id=a,
        conflicting_matrix_cells=[(a, b)],
    )
    restored = _through_json(node)
    assert restored.conflict_type is ConflictType.RESOURCE_CONFLICT
    assert restored.analyzed_system_id == a
    assert restored.conflicting_matrix_cells == [(a, b)]
    assert isinstance(restored.conflicting_matrix_cells[0], tuple)


def test_unknown_or_malformed_values_are_left_untouched():
    data = NodeSerializer.node_to_dict(Node(label="x"))
    data["created_at"] = "not-a-date"
    restored = NodeSerializer.dict_to_node(data)
    assert restored.created_at == "not-a-date"


def test_neo4j_property_path_uses_the_same_coercion():
    from data.neo4j_repository import Neo4jSFMRepository

    ids = [uuid.uuid4()]
    node = DigraphAnalysis(label="d", analyzed_institutions=ids, analysis_timestamp=datetime(2025, 1, 1))
    props = Neo4jSFMRepository._node_to_properties(node)
    assert props["analyzed_institutions"] == [str(ids[0])]
    restored = Neo4jSFMRepository._properties_to_node(props, DigraphAnalysis)
    assert restored.analyzed_institutions == ids
    assert restored.analysis_timestamp == datetime(2025, 1, 1)
