"""Tests for versioned persistence and time-travel operations."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from api.sfm_service import SFMService
from graph.sfm_graph import Relationship
from graph.version_control import VersionControlError
from models import Node


@pytest.fixture
def service(tmp_path, monkeypatch):
    """Service scoped to an isolated working directory."""
    monkeypatch.chdir(tmp_path)
    return SFMService()


def _create_pair_with_relationship(service: SFMService, kind: str = "links_to"):
    node1 = service.create_node(Node(label="Node A"))
    node2 = service.create_node(Node(label="Node B"))
    rel = service.create_relationship(
        Relationship(source_id=node1.id, target_id=node2.id, kind=kind)
    )
    return node1, node2, rel


def test_commit_creates_version_and_storage(service):
    service.create_node(Node(label="N1"))

    version = service.commit("initial commit", tags=["baseline"])

    assert version.message == "initial commit"
    assert version.parent_version_id is None
    assert "baseline" in version.tags

    root = Path(".sfm_versions")
    assert (root / "versions.db").exists()
    assert (root / "objects" / version.checksum).exists()


def test_commit_requires_message(service):
    service.create_node(Node(label="N1"))

    with pytest.raises(VersionControlError):
        service.commit("   ")


def test_checkout_by_tag_restores_graph(service):
    service.create_node(Node(label="Before"))
    service.commit("v1", tags=["baseline"])

    service.create_node(Node(label="After"))
    service.commit("v2")
    assert len(service.list_nodes()) == 2

    checked_out = service.checkout("baseline")

    labels = {node.label for node in service.list_nodes()}
    assert checked_out.message == "v1"
    assert labels == {"Before"}


def test_checkout_head_ancestor(service):
    service.create_node(Node(label="v1"))
    service.commit("v1")

    service.create_node(Node(label="v2"))
    service.commit("v2")

    service.create_node(Node(label="v3"))
    service.commit("v3")

    service.checkout("HEAD~2")
    labels = {node.label for node in service.list_nodes()}
    assert labels == {"v1"}


def test_list_versions_returns_branch_history(service):
    service.create_node(Node(label="N1"))
    v1 = service.commit("v1")

    service.create_node(Node(label="N2"))
    v2 = service.commit("v2")

    versions = service.list_versions(branch="main")
    assert [v.version_id for v in versions[:2]] == [v2.version_id, v1.version_id]


def test_list_versions_respects_limit(service):
    service.create_node(Node(label="N1"))
    service.commit("v1")
    service.create_node(Node(label="N2"))
    service.commit("v2")
    service.create_node(Node(label="N3"))
    service.commit("v3")

    versions = service.list_versions(limit=2)
    assert len(versions) == 2


def test_diff_versions_detects_node_add_and_modify(service):
    node = service.create_node(Node(label="N1", description="old"))
    v1 = service.commit("v1")

    updated = service.get_node(node.id)
    assert updated is not None
    updated.description = "new"
    service.update_node(updated)
    service.create_node(Node(label="N2"))
    v2 = service.commit("v2")

    diff = service.diff_versions(str(v1.version_id), str(v2.version_id))

    assert len(diff["nodes_added"]) == 1
    assert len(diff["nodes_modified"]) == 1
    assert len(diff["nodes_deleted"]) == 0


def test_diff_versions_detects_relationship_delete(service):
    node1, node2, rel = _create_pair_with_relationship(service)
    v1 = service.commit("with rel")

    service.repository.delete_relationship(rel.id)
    assert len(service.list_relationships()) == 0
    v2 = service.commit("without rel")

    diff = service.diff_versions(str(v1.version_id), str(v2.version_id))

    assert len(diff["relationships_added"]) == 0
    assert len(diff["relationships_deleted"]) == 1
    assert diff["relationships_deleted"][0]["id"] == str(rel.id)


def test_create_branch_creates_and_switches_branch(service):
    service.create_node(Node(label="root"))
    root = service.commit("root")

    created = service.create_branch("hypothesis-1")
    assert created == "hypothesis-1"

    service.create_node(Node(label="branch node"))
    branch_commit = service.commit("branch commit")

    main_versions = service.list_versions("main")
    branch_versions = service.list_versions("hypothesis-1")

    assert main_versions[0].version_id == root.version_id
    assert branch_versions[0].version_id == branch_commit.version_id


def test_create_branch_from_specific_version(service):
    service.create_node(Node(label="v1"))
    v1 = service.commit("v1", tags=["baseline"])

    service.create_node(Node(label="v2"))
    service.commit("v2")

    service.create_branch("alt", from_version="baseline")
    service.create_node(Node(label="alt-only"))
    alt_commit = service.commit("alt commit")

    history = service.list_versions("alt")
    assert history[0].version_id == alt_commit.version_id
    assert history[1].version_id == v1.version_id


def test_create_branch_duplicate_raises(service):
    service.create_node(Node(label="v1"))
    service.commit("v1")
    service.create_branch("exp")

    with pytest.raises(VersionControlError):
        service.create_branch("exp")


def test_checkout_branch_name_attaches_head(service):
    service.create_node(Node(label="base"))
    service.commit("base")
    service.create_branch("exp")
    service.create_node(Node(label="exp1"))
    service.commit("exp commit")

    service.checkout("main")
    service.create_node(Node(label="main2"))
    committed = service.commit("main commit")

    assert service.list_versions("main")[0].version_id == committed.version_id


@pytest.mark.parametrize("strategy", ["ours", "theirs", "manual"])
def test_merge_branch_returns_merge_result(service, strategy):
    service.create_node(Node(label="base"))
    service.commit("base")

    service.create_branch("exp")
    service.create_node(Node(label="exp-node"))
    service.commit("exp work")

    service.checkout("main")
    service.create_node(Node(label="main-node"))
    service.commit("main work")

    result = service.merge_branch("exp", strategy=strategy)
    assert result["strategy"] == strategy
    assert result["status"] in {"merged", "already_up_to_date"}


def test_merge_branch_invalid_strategy(service):
    service.create_node(Node(label="base"))
    service.commit("base")
    service.create_branch("exp")
    service.create_node(Node(label="exp-node"))
    service.commit("exp work")
    service.checkout("main")

    with pytest.raises(VersionControlError):
        service.merge_branch("exp", strategy="invalid")


def test_merge_branch_manual_reports_conflicts(service):
    node = service.create_node(Node(label="base", description="original"))
    service.commit("base")

    service.create_branch("exp")
    branch_node = service.get_node(node.id)
    assert branch_node is not None
    branch_node.description = "exp"
    service.update_node(branch_node)
    service.commit("exp update")

    service.checkout("main")
    main_node = service.get_node(node.id)
    assert main_node is not None
    main_node.description = "main"
    service.update_node(main_node)
    service.commit("main update")

    result = service.merge_branch("exp", strategy="manual")
    assert result["status"] == "merged"
    assert isinstance(result["conflicts"], list)
    assert any(conflict["entity"] == "node" for conflict in result["conflicts"])


def test_show_history_text_json_graphml(service):
    service.create_node(Node(label="N1"))
    committed = service.commit("v1", tags=["baseline"])

    text_output = service.show_history("text")
    json_output = service.show_history("json")
    graphml_output = service.show_history("graphml")

    assert committed.version_id.hex[:8] in text_output
    parsed = json.loads(json_output)
    assert parsed[0]["message"] == "v1"
    assert "graphml" in graphml_output


def test_deduplicates_identical_snapshots(service):
    service.create_node(Node(label="N1"))
    v1 = service.commit("same-1")
    v2 = service.commit("same-2")

    assert v1.checksum == v2.checksum

    objects = list((Path(".sfm_versions") / "objects").iterdir())
    assert len(objects) == 1


@pytest.mark.parametrize(
    "version_ref, should_work",
    [
        ("HEAD", True),
        ("HEAD~0", True),
        ("HEAD~1", True),
        ("main", True),
        ("missing-tag", False),
        ("HEAD~99", False),
    ],
)
def test_checkout_reference_variants(service, version_ref, should_work):
    service.create_node(Node(label="v1"))
    committed = service.commit("v1", tags=["tag-v1"])
    service.create_node(Node(label="v2"))
    service.commit("v2")

    if should_work:
        service.checkout(version_ref)
        assert len(service.list_nodes()) >= 1
    else:
        with pytest.raises(VersionControlError):
            service.checkout(version_ref)

    # Ensure direct UUID checkout works in all cases
    service.checkout(str(committed.version_id))
    assert any(node.label == "v1" for node in service.list_nodes())


@pytest.mark.parametrize("history_format", ["text", "json", "graphml"])
def test_show_history_supported_formats(service, history_format):
    service.create_node(Node(label="node"))
    service.commit("commit")

    output = service.show_history(history_format)
    assert isinstance(output, str)
    assert output


@pytest.mark.parametrize("tag_name", ["baseline", "final", "paper-v1", "paper-v2", "published"])
def test_commit_writes_tag_refs(service, tag_name):
    service.create_node(Node(label="node"))
    version = service.commit(f"commit-{tag_name}", tags=[tag_name])

    service.create_node(Node(label="new-node"))
    service.commit("new-head")

    restored = service.checkout(tag_name)
    assert restored.version_id == version.version_id
