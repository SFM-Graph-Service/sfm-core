"""Tests for incremental/delta-based SFM persistence."""

import json
from pathlib import Path

from api.sfm_service import SFMService
from graph.sfm_graph import Relationship
from models import Node


def _delta_files(tmp_path: Path, stem: str = "graph") -> list[Path]:
    return sorted(tmp_path.glob(f"{stem}_delta_*.json"))


def _read_json(filepath: Path) -> dict:
    return json.loads(filepath.read_text(encoding="utf-8"))


def _build_saved_graph(service: SFMService, tmp_path: Path, filename: str = "graph.json"):
    node1 = Node(label="Node 1")
    node2 = Node(label="Node 2")
    service.create_node(node1)
    service.create_node(node2)
    relationship = Relationship(source_id=node1.id, target_id=node2.id, kind="depends_on", weight=1.0)
    service.create_relationship(relationship)
    service.save(filename, base_path=str(tmp_path))
    return node1, node2, relationship


class TestChangeTracking:
    def test_change_tracker_starts_empty(self):
        service = SFMService()
        tracker = service.repository.change_tracker

        assert tracker.summary() == {
            "nodes_added": 0,
            "nodes_modified": 0,
            "nodes_deleted": 0,
            "relationships_added": 0,
            "relationships_modified": 0,
            "relationships_deleted": 0,
        }
        assert tracker.has_changes() is False

    def test_create_node_marks_node_added(self):
        service = SFMService()
        node = Node(label="Tracked")

        service.create_node(node)

        assert node.id in service.repository.change_tracker.added_nodes

    def test_save_clears_change_tracker(self, tmp_path):
        service = SFMService()
        service.create_node(Node(label="Tracked"))

        service.save("graph.json", base_path=str(tmp_path))

        tracker = service.repository.change_tracker
        assert tracker.has_changes() is False
        assert tracker.last_save_timestamp is not None

    def test_update_existing_node_marks_node_modified(self, tmp_path):
        service = SFMService()
        node, _, _ = _build_saved_graph(service, tmp_path)
        node.label = "Updated"

        service.update_node(node)

        tracker = service.repository.change_tracker
        assert node.id in tracker.modified_nodes
        assert node.id not in tracker.added_nodes

    def test_update_new_node_does_not_duplicate_added_state(self):
        service = SFMService()
        node = Node(label="Tracked")
        service.create_node(node)
        node.label = "Updated"

        service.update_node(node)

        tracker = service.repository.change_tracker
        assert node.id in tracker.added_nodes
        assert node.id not in tracker.modified_nodes

    def test_delete_new_node_removes_net_change(self):
        service = SFMService()
        node = Node(label="Ephemeral")
        service.create_node(node)

        service.delete_node(node.id)

        tracker = service.repository.change_tracker
        assert node.id not in tracker.added_nodes
        assert node.id not in tracker.deleted_nodes

    def test_delete_existing_node_marks_node_deleted(self, tmp_path):
        service = SFMService()
        node, _, _ = _build_saved_graph(service, tmp_path)

        service.delete_node(node.id)

        assert node.id in service.repository.change_tracker.deleted_nodes

    def test_create_relationship_marks_relationship_added(self):
        service = SFMService()
        node1 = service.create_node(Node(label="Source"))
        node2 = service.create_node(Node(label="Target"))
        relationship = Relationship(source_id=node1.id, target_id=node2.id, kind="depends_on")

        service.create_relationship(relationship)

        assert relationship.id in service.repository.change_tracker.added_relationships

    def test_update_existing_relationship_marks_relationship_modified(self, tmp_path):
        service = SFMService()
        _, _, relationship = _build_saved_graph(service, tmp_path)
        relationship.weight = 2.0

        service.update_relationship(relationship)

        tracker = service.repository.change_tracker
        assert relationship.id in tracker.modified_relationships
        assert relationship.id not in tracker.added_relationships

    def test_delete_new_relationship_removes_net_change(self):
        service = SFMService()
        node1 = service.create_node(Node(label="Source"))
        node2 = service.create_node(Node(label="Target"))
        relationship = Relationship(source_id=node1.id, target_id=node2.id, kind="depends_on")
        service.create_relationship(relationship)

        service.delete_relationship(relationship.id)

        tracker = service.repository.change_tracker
        assert relationship.id not in tracker.added_relationships
        assert relationship.id not in tracker.deleted_relationships

    def test_delete_node_marks_incident_relationship_deleted(self, tmp_path):
        service = SFMService()
        node1, _, relationship = _build_saved_graph(service, tmp_path)

        service.delete_node(node1.id)

        assert relationship.id in service.repository.change_tracker.deleted_relationships


class TestIncrementalSave:
    def test_first_incremental_save_without_existing_snapshot_creates_base_snapshot(self, tmp_path):
        service = SFMService()
        service.create_node(Node(label="Node 1"))

        result = service.save_incremental("graph.json", base_path=str(tmp_path))

        assert result["mode"] == "base_snapshot"
        assert (tmp_path / "graph_base.json").exists()
        assert _delta_files(tmp_path) == []

    def test_incremental_save_with_no_changes_returns_noop(self, tmp_path):
        service = SFMService()
        service.create_node(Node(label="Node 1"))
        service.save("graph.json", base_path=str(tmp_path))

        result = service.save_incremental("graph.json", base_path=str(tmp_path))

        assert result["delta_created"] is False
        assert _delta_files(tmp_path) == []

    def test_incremental_save_after_full_save_creates_delta_file(self, tmp_path):
        service = SFMService()
        _build_saved_graph(service, tmp_path)
        service.create_node(Node(label="New Node"))

        result = service.save_incremental("graph.json", base_path=str(tmp_path))

        assert result["delta_created"] is True
        assert len(_delta_files(tmp_path)) == 1

    def test_incremental_save_uses_requested_snapshot_as_base_when_present(self, tmp_path):
        service = SFMService()
        service.create_node(Node(label="Node 1"))
        service.save("graph.json", base_path=str(tmp_path))
        service.create_node(Node(label="Node 2"))

        service.save_incremental("graph.json", base_path=str(tmp_path))
        delta_payload = _read_json(_delta_files(tmp_path)[0])

        assert delta_payload["metadata"]["base_snapshot"] == "graph.json"

    def test_delta_file_records_change_summary(self, tmp_path):
        service = SFMService()
        node1, node2, relationship = _build_saved_graph(service, tmp_path)
        node1.label = "Updated Node 1"
        service.update_node(node1)
        service.delete_node(node2.id)
        node3 = service.create_node(Node(label="Node 3"))
        service.create_relationship(Relationship(source_id=node1.id, target_id=node3.id, kind="supports"))

        service.save_incremental("graph.json", base_path=str(tmp_path))
        summary = _read_json(_delta_files(tmp_path)[0])["metadata"]["changes_summary"]

        assert summary == {
            "nodes_added": 1,
            "nodes_modified": 1,
            "nodes_deleted": 1,
            "relationships_added": 1,
            "relationships_modified": 0,
            "relationships_deleted": 1,
        }

    def test_delta_file_records_added_nodes(self, tmp_path):
        service = SFMService()
        service.save("graph.json", base_path=str(tmp_path))
        service.create_node(Node(label="Added Node"))

        service.save_incremental("graph.json", base_path=str(tmp_path))
        nodes_added = _read_json(_delta_files(tmp_path)[0])["changes"]["nodes_added"]

        assert [node["label"] for node in nodes_added] == ["Added Node"]

    def test_delta_file_records_modified_nodes(self, tmp_path):
        service = SFMService()
        node, _, _ = _build_saved_graph(service, tmp_path)
        node.label = "Updated Node 1"
        service.update_node(node)

        service.save_incremental("graph.json", base_path=str(tmp_path))
        nodes_modified = _read_json(_delta_files(tmp_path)[0])["changes"]["nodes_modified"]

        assert [node["label"] for node in nodes_modified] == ["Updated Node 1"]

    def test_delta_file_records_deleted_nodes(self, tmp_path):
        service = SFMService()
        _, node2, _ = _build_saved_graph(service, tmp_path)

        service.delete_node(node2.id)
        service.save_incremental("graph.json", base_path=str(tmp_path))
        nodes_deleted = _read_json(_delta_files(tmp_path)[0])["changes"]["nodes_deleted"]

        assert nodes_deleted == [str(node2.id)]

    def test_incremental_delta_is_smaller_than_full_snapshot_for_small_change(self, tmp_path):
        service = SFMService()
        nodes = [service.create_node(Node(label=f"Node {index}")) for index in range(200)]
        for index in range(199):
            service.create_relationship(
                Relationship(source_id=nodes[index].id, target_id=nodes[index + 1].id, kind="links")
            )
        full_result = service.save("large_graph.json", base_path=str(tmp_path))
        service.create_node(Node(label="Small change"))

        delta_result = service.save_incremental("large_graph.json", base_path=str(tmp_path))

        assert delta_result["size_bytes"] < full_result["size_bytes"]


class TestLoadWithDeltas:
    def test_load_with_deltas_replays_single_delta(self, tmp_path):
        service = SFMService()
        node1, _, _ = _build_saved_graph(service, tmp_path)
        node1.label = "Updated Node 1"
        service.update_node(node1)
        added = service.create_node(Node(label="Node 3"))
        service.create_relationship(Relationship(source_id=node1.id, target_id=added.id, kind="supports"))
        service.save_incremental("graph.json", base_path=str(tmp_path))

        loaded_service = SFMService()
        result = loaded_service.load_with_deltas("graph.json", base_path=str(tmp_path))

        assert result["deltas_applied"] == 1
        assert {node.label for node in loaded_service.list_nodes()} == {"Updated Node 1", "Node 2", "Node 3"}
        assert len(loaded_service.list_relationships()) == 2

    def test_load_with_deltas_replays_multiple_deltas_in_order(self, tmp_path):
        service = SFMService()
        node1, _, _ = _build_saved_graph(service, tmp_path)
        added = service.create_node(Node(label="Node 3"))
        service.save_incremental("graph.json", base_path=str(tmp_path))
        added.label = "Node 3 Updated"
        service.update_node(added)
        service.create_relationship(Relationship(source_id=node1.id, target_id=added.id, kind="supports"))
        service.save_incremental("graph.json", base_path=str(tmp_path))

        loaded_service = SFMService()
        loaded_service.load_with_deltas("graph.json", base_path=str(tmp_path))

        labels = {node.label for node in loaded_service.list_nodes()}
        assert "Node 3 Updated" in labels
        assert len(loaded_service.list_relationships()) == 2

    def test_load_with_deltas_uses_base_alias_when_present(self, tmp_path):
        service = SFMService()
        service.create_node(Node(label="Node 1"))
        service.save_incremental("graph.json", base_path=str(tmp_path))
        service.create_node(Node(label="Node 2"))
        service.save_incremental("graph.json", base_path=str(tmp_path))

        loaded_service = SFMService()
        result = loaded_service.load_with_deltas("graph.json", base_path=str(tmp_path))

        assert result["base_snapshot"] == "graph_base.json"
        assert {node.label for node in loaded_service.list_nodes()} == {"Node 1", "Node 2"}

    def test_load_with_deltas_clears_change_tracker(self, tmp_path):
        service = SFMService()
        service.create_node(Node(label="Node 1"))
        service.save("graph.json", base_path=str(tmp_path))
        service.create_node(Node(label="Node 2"))
        service.save_incremental("graph.json", base_path=str(tmp_path))

        loaded_service = SFMService()
        loaded_service.load_with_deltas("graph.json", base_path=str(tmp_path))

        assert loaded_service.repository.change_tracker.has_changes() is False


class TestCompaction:
    def test_compact_removes_delta_files(self, tmp_path):
        service = SFMService()
        service.create_node(Node(label="Node 1"))
        service.save("graph.json", base_path=str(tmp_path))
        service.create_node(Node(label="Node 2"))
        service.save_incremental("graph.json", base_path=str(tmp_path))
        service.create_node(Node(label="Node 3"))
        service.save_incremental("graph.json", base_path=str(tmp_path))

        result = service.compact("graph.json", base_path=str(tmp_path))

        assert result["compacted_deltas"] == 2
        assert _delta_files(tmp_path) == []

    def test_compact_preserves_final_graph_state(self, tmp_path):
        service = SFMService()
        node1, _, _ = _build_saved_graph(service, tmp_path)
        added = service.create_node(Node(label="Node 3"))
        service.save_incremental("graph.json", base_path=str(tmp_path))
        node1.label = "Updated Node 1"
        service.update_node(node1)
        service.create_relationship(Relationship(source_id=node1.id, target_id=added.id, kind="supports"))
        service.save_incremental("graph.json", base_path=str(tmp_path))

        service.compact("graph.json", base_path=str(tmp_path))
        loaded_service = SFMService()
        result = loaded_service.load_with_deltas("graph.json", base_path=str(tmp_path))

        assert result["deltas_applied"] == 0
        assert {node.label for node in loaded_service.list_nodes()} == {"Updated Node 1", "Node 2", "Node 3"}
        assert len(loaded_service.list_relationships()) == 2

    def test_compact_rewrites_requested_snapshot_when_no_base_alias_exists(self, tmp_path):
        service = SFMService()
        service.create_node(Node(label="Node 1"))
        service.save("graph.json", base_path=str(tmp_path))
        service.create_node(Node(label="Node 2"))
        service.save_incremental("graph.json", base_path=str(tmp_path))

        result = service.compact("graph.json", base_path=str(tmp_path))

        assert Path(result["filepath"]).name == "graph.json"
        assert (tmp_path / "graph.json").exists()
