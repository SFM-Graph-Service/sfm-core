"""Version control orchestration for SFM graph snapshots."""

from __future__ import annotations

import gzip
import json
import os
import uuid
from datetime import datetime, timezone
from io import BytesIO
from typing import Any, Dict, List, Optional, Tuple

import networkx as nx

from graph.version_storage import GraphVersion, VersionStorage


class VersionControlError(Exception):
    """Raised when version-control operations fail."""


class SFMVersionController:
    """Git-inspired version operations over serialized graph snapshots."""

    def __init__(self, root_path: str = ".sfm_versions"):
        self.storage = VersionStorage(root_path=root_path)

    @staticmethod
    def _normalize_snapshot(snapshot_data: Dict[str, Any]) -> Dict[str, Any]:
        normalized: Dict[str, Any] = json.loads(json.dumps(snapshot_data))

        metadata = normalized.get("metadata", {})
        if isinstance(metadata, dict):
            metadata.pop("saved_at", None)

        nodes_by_type = normalized.get("nodes_by_type", {})
        if isinstance(nodes_by_type, dict):
            for node_type, nodes in nodes_by_type.items():
                if isinstance(nodes, list):
                    nodes_by_type[node_type] = sorted(
                        nodes, key=lambda item: item.get("id", "")
                    )

        relationships = normalized.get("relationships", [])
        if isinstance(relationships, list):
            normalized["relationships"] = sorted(
                relationships, key=lambda item: item.get("id", "")
            )

        return normalized

    @staticmethod
    def _serialize_snapshot(snapshot_data: Dict[str, Any]) -> bytes:
        normalized = SFMVersionController._normalize_snapshot(snapshot_data)
        raw = json.dumps(normalized, sort_keys=True, separators=(",", ":")).encode(
            "utf-8"
        )
        return gzip.compress(raw)

    @staticmethod
    def _deserialize_snapshot(snapshot_blob: bytes) -> Dict[str, Any]:
        result: Dict[str, Any] = json.loads(gzip.decompress(snapshot_blob).decode("utf-8"))
        return result

    @staticmethod
    def _snapshot_stats(snapshot_data: Dict[str, Any]) -> Dict[str, int]:
        metadata = snapshot_data.get("metadata", {})
        return {
            "node_count": int(metadata.get("node_count", 0)),
            "relationship_count": int(metadata.get("relationship_count", 0)),
        }

    def commit_snapshot(
        self,
        snapshot_data: Dict[str, Any],
        message: str,
        tags: Optional[List[str]] = None,
    ) -> GraphVersion:
        if not message or not message.strip():
            raise VersionControlError("Commit message is required")

        compressed_snapshot = self._serialize_snapshot(snapshot_data)
        checksum = self.storage.store_object(compressed_snapshot)

        head = self.storage.get_head_version_id()
        current_branch = self.storage.get_current_branch() or "main"
        if not self.storage.branch_exists(current_branch):
            self.storage.write_branch(current_branch, head or uuid.uuid4())
            if head is None:
                # Remove placeholder branch file when repo is truly empty
                branch_path = self.storage.branches_path / current_branch
                if branch_path.exists():
                    branch_path.unlink()

        version = GraphVersion(
            version_id=uuid.uuid4(),
            parent_version_id=head,
            timestamp=datetime.now(timezone.utc),
            author=os.getenv("SFM_AUTHOR") or os.getenv("USER") or "unknown",
            message=message.strip(),
            tags=list(tags or []),
            stats=self._snapshot_stats(snapshot_data),
            checksum=checksum,
        )

        self.storage.put_version(version, branch=current_branch)
        self.storage.write_branch(current_branch, version.version_id)
        self.storage.set_head_branch(current_branch)

        for tag in version.tags:
            self.storage.write_tag(tag, version.version_id)

        return version

    def _resolve_version(self, version_ref: str) -> uuid.UUID:
        version_id = self.storage.resolve_ref(version_ref)
        if version_id is None:
            raise VersionControlError(f"Unknown version reference: {version_ref}")
        return version_id

    def get_version_snapshot(self, version_ref: str) -> Tuple[GraphVersion, Dict[str, Any]]:
        version_id = self._resolve_version(version_ref)
        version = self.storage.get_version(version_id)
        if version is None:
            raise VersionControlError(f"Version metadata not found: {version_id}")

        snapshot = self._deserialize_snapshot(self.storage.read_object(version.checksum))
        return version, snapshot

    def checkout(self, version_ref: str) -> GraphVersion:
        version_id = self._resolve_version(version_ref)
        version = self.storage.get_version(version_id)
        if version is None:
            raise VersionControlError(f"Version metadata not found: {version_id}")

        if self.storage.branch_exists(version_ref):
            self.storage.set_head_branch(version_ref)
        else:
            self.storage.set_head_detached(version_id)

        return version

    def list_versions(self, branch: str = "main", limit: int = 20) -> List[GraphVersion]:
        return self.storage.list_branch_versions(branch=branch, limit=limit)

    @staticmethod
    def _index_nodes(snapshot: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        index: Dict[str, Dict[str, Any]] = {}
        for node_list in snapshot.get("nodes_by_type", {}).values():
            for node in node_list:
                node_id = node.get("id")
                if node_id:
                    index[node_id] = node
        return index

    @staticmethod
    def _index_relationships(snapshot: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        return {
            rel["id"]: rel
            for rel in snapshot.get("relationships", [])
            if rel.get("id")
        }

    @staticmethod
    def _diff_maps(
        old_map: Dict[str, Dict[str, Any]],
        new_map: Dict[str, Dict[str, Any]],
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
        old_ids = set(old_map)
        new_ids = set(new_map)

        added = [new_map[item_id] for item_id in sorted(new_ids - old_ids)]
        deleted = [old_map[item_id] for item_id in sorted(old_ids - new_ids)]

        modified: List[Dict[str, Any]] = []
        for item_id in sorted(old_ids & new_ids):
            if old_map[item_id] != new_map[item_id]:
                modified.append({"before": old_map[item_id], "after": new_map[item_id]})

        return added, modified, deleted

    def diff_versions(self, version1: str, version2: str) -> Dict[str, Any]:
        _, snapshot1 = self.get_version_snapshot(version1)
        _, snapshot2 = self.get_version_snapshot(version2)

        node_added, node_modified, node_deleted = self._diff_maps(
            self._index_nodes(snapshot1), self._index_nodes(snapshot2)
        )
        rel_added, rel_modified, rel_deleted = self._diff_maps(
            self._index_relationships(snapshot1), self._index_relationships(snapshot2)
        )

        return {
            "nodes_added": node_added,
            "nodes_modified": node_modified,
            "nodes_deleted": node_deleted,
            "relationships_added": rel_added,
            "relationships_modified": rel_modified,
            "relationships_deleted": rel_deleted,
        }

    def create_branch(self, branch_name: str, from_version: Optional[str] = None) -> str:
        if not branch_name.strip():
            raise VersionControlError("Branch name cannot be empty")
        if self.storage.branch_exists(branch_name):
            raise VersionControlError(f"Branch already exists: {branch_name}")

        source_ref = from_version or "HEAD"
        source_version = self.storage.resolve_ref(source_ref)
        if source_version is None:
            raise VersionControlError(f"Cannot create branch from: {source_ref}")

        self.storage.write_branch(branch_name, source_version)
        self.storage.set_head_branch(branch_name)
        return branch_name

    @staticmethod
    def _merge_snapshots(
        ours: Dict[str, Any],
        theirs: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        merged = json.loads(json.dumps(ours))
        conflicts: List[Dict[str, Any]] = []

        merged_nodes = SFMVersionController._index_nodes(merged)
        for node_id, node_data in SFMVersionController._index_nodes(theirs).items():
            if node_id in merged_nodes and merged_nodes[node_id] != node_data:
                conflicts.append({"entity": "node", "id": node_id})
            else:
                merged_nodes[node_id] = node_data

        nodes_by_type: Dict[str, List[Dict[str, Any]]] = {}
        for node in merged_nodes.values():
            node_type = node.get("node_type", "Node")
            nodes_by_type.setdefault(node_type, []).append(node)
        for key in nodes_by_type:
            nodes_by_type[key] = sorted(nodes_by_type[key], key=lambda item: item.get("id", ""))
        merged["nodes_by_type"] = nodes_by_type

        merged_rels = SFMVersionController._index_relationships(merged)
        for rel_id, rel_data in SFMVersionController._index_relationships(theirs).items():
            if rel_id in merged_rels and merged_rels[rel_id] != rel_data:
                conflicts.append({"entity": "relationship", "id": rel_id})
            else:
                merged_rels[rel_id] = rel_data

        merged["relationships"] = sorted(
            merged_rels.values(), key=lambda item: item.get("id", "")
        )
        merged["metadata"]["node_count"] = len(merged_nodes)
        merged["metadata"]["relationship_count"] = len(merged_rels)

        return merged, conflicts

    def merge_branch(self, branch_name: str, strategy: str = "manual") -> Dict[str, Any]:
        if strategy not in {"manual", "ours", "theirs"}:
            raise VersionControlError(f"Unsupported merge strategy: {strategy}")

        source_head = self.storage.read_branch(branch_name)
        if source_head is None:
            raise VersionControlError(f"Branch not found: {branch_name}")

        current_head = self.storage.get_head_version_id()
        current_branch = self.storage.get_current_branch()
        if current_head is None or current_branch is None:
            raise VersionControlError("Cannot merge without an active branch HEAD")

        if source_head == current_head:
            return {
                "status": "already_up_to_date",
                "strategy": strategy,
                "source_branch": branch_name,
                "target_branch": current_branch,
                "conflicts": [],
            }

        ours_version = self.storage.get_version(current_head)
        theirs_version = self.storage.get_version(source_head)
        if ours_version is None or theirs_version is None:
            raise VersionControlError("Missing version metadata for merge")

        ours_snapshot = self._deserialize_snapshot(self.storage.read_object(ours_version.checksum))
        theirs_snapshot = self._deserialize_snapshot(
            self.storage.read_object(theirs_version.checksum)
        )

        conflicts: List[Dict[str, Any]] = []
        if strategy == "ours":
            merged_snapshot = ours_snapshot
        elif strategy == "theirs":
            merged_snapshot = theirs_snapshot
        else:
            merged_snapshot, conflicts = self._merge_snapshots(ours_snapshot, theirs_snapshot)

        merged_version = self.commit_snapshot(
            merged_snapshot,
            message=(
                f"Merge branch '{branch_name}' into '{current_branch}' "
                f"with strategy '{strategy}'"
            ),
        )

        return {
            "status": "merged",
            "strategy": strategy,
            "source_branch": branch_name,
            "target_branch": current_branch,
            "merged_version_id": str(merged_version.version_id),
            "conflicts": conflicts,
        }

    def show_history(self, format: str = "text") -> str:
        versions = self.storage.list_all_versions()
        if format == "json":
            return json.dumps(
                [
                    {
                        "version_id": str(v.version_id),
                        "parent_version_id": (
                            str(v.parent_version_id) if v.parent_version_id else None
                        ),
                        "timestamp": v.timestamp.isoformat(),
                        "author": v.author,
                        "message": v.message,
                        "tags": v.tags,
                        "stats": v.stats,
                        "checksum": v.checksum,
                    }
                    for v in versions
                ],
                indent=2,
            )

        if format == "graphml":
            graph: nx.DiGraph = nx.DiGraph()
            for version in versions:
                version_id = str(version.version_id)
                graph.add_node(version_id, message=version.message)
                if version.parent_version_id:
                    graph.add_edge(str(version.parent_version_id), version_id)

            buffer = BytesIO()
            nx.write_graphml(graph, buffer)
            return buffer.getvalue().decode("utf-8")

        branch_refs = self.storage.list_branches()
        tag_refs = self.storage.list_tags()
        head_version = self.storage.get_head_version_id()
        lines: List[str] = []
        for version in versions:
            refs: List[str] = []
            if head_version and head_version == version.version_id:
                refs.append("HEAD")
            refs.extend(
                f"branch:{name}"
                for name, version_id in branch_refs.items()
                if version_id == version.version_id
            )
            refs.extend(
                f"tag:{name}"
                for name, version_id in tag_refs.items()
                if version_id == version.version_id
            )

            refs_text = f" ({', '.join(refs)})" if refs else ""
            lines.append(
                f"* {version.version_id.hex[:8]}{refs_text} "
                f"{version.message} ({version.timestamp.strftime('%Y-%m-%d %H:%M')})"
            )

        return "\n".join(lines)
