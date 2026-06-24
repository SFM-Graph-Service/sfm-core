"""Version storage backend for SFM graph snapshots."""

from __future__ import annotations

import hashlib
import json
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class GraphVersion:
    """Metadata for a versioned graph snapshot."""

    version_id: uuid.UUID
    parent_version_id: Optional[uuid.UUID]
    timestamp: datetime
    author: str
    message: str
    tags: List[str]
    stats: Dict[str, int]
    checksum: str


class VersionStorage:
    """Stores graph versions, objects, and refs on local disk."""

    def __init__(self, root_path: str = ".sfm_versions"):
        self.root_path = Path(root_path)
        self.objects_path = self.root_path / "objects"
        self.refs_path = self.root_path / "refs"
        self.tags_path = self.refs_path / "tags"
        self.branches_path = self.refs_path / "branches"
        self.db_path = self.root_path / "versions.db"

        self.objects_path.mkdir(parents=True, exist_ok=True)
        self.tags_path.mkdir(parents=True, exist_ok=True)
        self.branches_path.mkdir(parents=True, exist_ok=True)
        self._init_db()

        head_path = self._head_path()
        if not head_path.exists():
            head_path.write_text("ref: refs/branches/main", encoding="utf-8")

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS versions (
                    version_id TEXT PRIMARY KEY,
                    parent_version_id TEXT,
                    timestamp TEXT NOT NULL,
                    author TEXT NOT NULL,
                    message TEXT NOT NULL,
                    tags_json TEXT NOT NULL,
                    stats_json TEXT NOT NULL,
                    checksum TEXT NOT NULL,
                    branch TEXT
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_versions_parent ON versions(parent_version_id)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_versions_branch ON versions(branch)"
            )
            conn.commit()

    def _head_path(self) -> Path:
        return self.refs_path / "HEAD"

    def _branch_path(self, branch_name: str) -> Path:
        return self.branches_path / branch_name

    def _tag_path(self, tag_name: str) -> Path:
        return self.tags_path / tag_name

    def store_object(self, raw_data: bytes) -> str:
        checksum = hashlib.sha256(raw_data).hexdigest()
        object_path = self.objects_path / checksum
        if not object_path.exists():
            object_path.write_bytes(raw_data)
        return checksum

    def read_object(self, checksum: str) -> bytes:
        return (self.objects_path / checksum).read_bytes()

    def put_version(self, version: GraphVersion, branch: Optional[str] = None) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO versions (
                    version_id,
                    parent_version_id,
                    timestamp,
                    author,
                    message,
                    tags_json,
                    stats_json,
                    checksum,
                    branch
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(version.version_id),
                    str(version.parent_version_id) if version.parent_version_id else None,
                    version.timestamp.astimezone(timezone.utc).isoformat(),
                    version.author,
                    version.message,
                    json.dumps(version.tags),
                    json.dumps(version.stats),
                    version.checksum,
                    branch,
                ),
            )
            conn.commit()

    def get_version(self, version_id: uuid.UUID) -> Optional[GraphVersion]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM versions WHERE version_id = ?", (str(version_id),)
            ).fetchone()
        if row is None:
            return None
        return self._row_to_graph_version(row)

    def get_version_branch(self, version_id: uuid.UUID) -> Optional[str]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT branch FROM versions WHERE version_id = ?", (str(version_id),)
            ).fetchone()
        return row["branch"] if row else None

    def list_branch_versions(self, branch: str, limit: int = 20) -> List[GraphVersion]:
        head = self.read_branch(branch)
        if not head:
            return []

        result: List[GraphVersion] = []
        current: Optional[uuid.UUID] = head
        while current and len(result) < limit:
            version = self.get_version(current)
            if version is None:
                break
            result.append(version)
            current = version.parent_version_id
        return result

    def list_all_versions(self) -> List[GraphVersion]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM versions ORDER BY timestamp DESC").fetchall()
        return [self._row_to_graph_version(row) for row in rows]

    def _row_to_graph_version(self, row: sqlite3.Row) -> GraphVersion:
        parent_raw = row["parent_version_id"]
        parent = uuid.UUID(parent_raw) if parent_raw else None
        return GraphVersion(
            version_id=uuid.UUID(row["version_id"]),
            parent_version_id=parent,
            timestamp=datetime.fromisoformat(row["timestamp"]),
            author=row["author"],
            message=row["message"],
            tags=list(json.loads(row["tags_json"])),
            stats=dict(json.loads(row["stats_json"])),
            checksum=row["checksum"],
        )

    def set_head_branch(self, branch_name: str) -> None:
        self._head_path().write_text(
            f"ref: refs/branches/{branch_name}", encoding="utf-8"
        )

    def set_head_detached(self, version_id: uuid.UUID) -> None:
        self._head_path().write_text(str(version_id), encoding="utf-8")

    def get_head_raw(self) -> str:
        return self._head_path().read_text(encoding="utf-8").strip()

    def get_current_branch(self) -> Optional[str]:
        raw = self.get_head_raw()
        if raw.startswith("ref: refs/branches/"):
            return raw.split("/")[-1]
        return None

    def get_head_version_id(self) -> Optional[uuid.UUID]:
        raw = self.get_head_raw()
        if raw.startswith("ref: refs/branches/"):
            branch = raw.split("/")[-1]
            return self.read_branch(branch)
        try:
            return uuid.UUID(raw)
        except ValueError:
            return None

    def read_branch(self, branch_name: str) -> Optional[uuid.UUID]:
        path = self._branch_path(branch_name)
        if not path.exists():
            return None
        return uuid.UUID(path.read_text(encoding="utf-8").strip())

    def write_branch(self, branch_name: str, version_id: uuid.UUID) -> None:
        self._branch_path(branch_name).write_text(str(version_id), encoding="utf-8")

    def branch_exists(self, branch_name: str) -> bool:
        return self._branch_path(branch_name).exists()

    def list_branches(self) -> Dict[str, uuid.UUID]:
        result: Dict[str, uuid.UUID] = {}
        for branch_path in self.branches_path.iterdir():
            if branch_path.is_file():
                result[branch_path.name] = uuid.UUID(
                    branch_path.read_text(encoding="utf-8").strip()
                )
        return result

    def write_tag(self, tag_name: str, version_id: uuid.UUID) -> None:
        self._tag_path(tag_name).write_text(str(version_id), encoding="utf-8")

    def read_tag(self, tag_name: str) -> Optional[uuid.UUID]:
        path = self._tag_path(tag_name)
        if not path.exists():
            return None
        return uuid.UUID(path.read_text(encoding="utf-8").strip())

    def list_tags(self) -> Dict[str, uuid.UUID]:
        result: Dict[str, uuid.UUID] = {}
        for tag_path in self.tags_path.iterdir():
            if tag_path.is_file():
                result[tag_path.name] = uuid.UUID(
                    tag_path.read_text(encoding="utf-8").strip()
                )
        return result

    def resolve_ref(self, version_ref: str) -> Optional[uuid.UUID]:
        if version_ref == "HEAD":
            return self.get_head_version_id()

        if version_ref.startswith("HEAD~"):
            raw_steps = version_ref.split("~", maxsplit=1)[1]
            if not raw_steps.isdigit():
                return None
            current = self.get_head_version_id()
            steps = int(raw_steps)
            while current and steps > 0:
                version = self.get_version(current)
                if version is None:
                    return None
                current = version.parent_version_id
                steps -= 1
            return current

        if self.branch_exists(version_ref):
            return self.read_branch(version_ref)

        tag_version = self.read_tag(version_ref)
        if tag_version:
            return tag_version

        try:
            candidate = uuid.UUID(version_ref)
        except ValueError:
            return None

        return candidate if self.get_version(candidate) else None
