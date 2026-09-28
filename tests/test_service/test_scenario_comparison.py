"""Scenario comparison across version snapshots and the working graph."""

from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient

from api.rest.app import create_app
from api.rest.dependencies import get_sfm_service
from api.sfm_service import SFMService
from graph.sfm_graph import Relationship
from graph.version_control import VersionControlError
from models import Node
from models.exceptions import SFMValidationError


@pytest.fixture
def service(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    return SFMService()


@pytest.fixture
def loop_service(service):
    """Baseline: a 3-node reinforcing loop A->B->C->A plus an isolated D, committed as 'baseline'."""
    a = service.create_node(Node(label="A"))
    b = service.create_node(Node(label="B"))
    c = service.create_node(Node(label="C"))
    d = service.create_node(Node(label="D"))
    service.create_relationship(Relationship(
        source_id=a.id, target_id=b.id, kind="drives", weight=0.8,
        confidence=0.9, confidence_interval=(0.7, 0.9), data_sources=["Report 1"],
        uncertainty_type="epistemic", source_agreement="high", meta={"note": "kept"},
    ))
    service.create_relationship(Relationship(source_id=b.id, target_id=c.id, kind="drives", weight=0.5))
    service.create_relationship(Relationship(source_id=c.id, target_id=a.id, kind="drives", weight=0.9))
    service.commit("baseline", tags=["baseline"])
    service.nodes = {"a": a, "b": b, "c": c, "d": d}
    return service


class TestRelationshipRoundTrip:
    def test_commit_checkout_preserves_uncertainty_fields(self, loop_service):
        svc = loop_service
        svc.create_node(Node(label="scratch"))
        svc.commit("v2")
        svc.checkout("baseline")

        rel = next(r for r in svc.list_relationships() if r.weight == 0.8)
        assert rel.confidence == 0.9
        assert rel.confidence_interval == (0.7, 0.9)
        assert rel.data_sources == ["Report 1"]
        assert rel.uncertainty_type == "epistemic"
        assert rel.source_agreement == "high"
        assert rel.meta == {"note": "kept"}

    def test_from_dict_accepts_legacy_five_field_shape(self):
        legacy = {"id": str(uuid.uuid4()), "source_id": str(uuid.uuid4()),
                  "target_id": str(uuid.uuid4()), "kind": "x", "weight": 0.3}
        rel = SFMService._relationship_from_dict(legacy)
        assert rel.weight == 0.3
        assert rel.confidence is None
        assert rel.data_sources == []
        assert rel.meta == {}


class TestCompareScenarios:
    def test_working_graph_vs_baseline_after_breaking_the_loop(self, loop_service):
        svc = loop_service
        n = svc.nodes
        # Sever C->A, add D into a new loop with A: A->D->A
        ca = next(r for r in svc.list_relationships() if r.source_id == n["c"].id)
        svc.delete_relationship(ca.id)
        svc.create_relationship(Relationship(source_id=n["a"].id, target_id=n["d"].id, kind="funds", weight=0.6, confidence=0.5))
        svc.create_relationship(Relationship(source_id=n["d"].id, target_id=n["a"].id, kind="opposes", weight=0.7))

        result = svc.compare_scenarios(base_ref="baseline", alt_ref=None, source_id=n["a"].id)

        assert result["base"]["ref"] == "baseline"
        assert result["base"]["message"] == "baseline"
        assert result["alternative"]["ref"] == "working"
        assert result["alternative"]["version_id"] is None
        assert set(result["analyses"]) == {"structure", "centrality", "loops", "conflicts", "circular_causation"}

        structure = result["structure"]
        assert structure["nodes"] == {"base": 4, "alternative": 4, "delta": 0}
        assert structure["relationships"] == {"base": 3, "alternative": 4, "delta": 1}
        assert structure["relationships_added"] == 2
        assert structure["relationships_deleted"] == 1
        assert structure["density"]["delta"] > 0

        loops = result["loops"]
        assert loops["simple_cycles"] == {"base": 1, "alternative": 1, "delta": 0}
        assert loops["nodes_in_loops"] == {"base": 3, "alternative": 2, "delta": -1}
        base_lev = {p["label"] for p in loops["leverage_points"]["base"]}
        alt_lev = {p["label"] for p in loops["leverage_points"]["alternative"]}
        assert base_lev == {"A", "B", "C"}
        assert alt_lev == {"A", "D"}
        movers = {m["label"]: m["delta"] for m in loops["participation_movers"]}
        assert movers == {"B": -1, "C": -1, "D": 1}

        conflicts = result["conflicts"]
        assert conflicts["total"] == {"base": 0, "alternative": 1, "delta": 1}
        assert conflicts["by_severity"]["high"]["alternative"] == 1
        assert conflicts["new"] == ["D opposes A"]
        assert conflicts["resolved"] == []

        cc = result["circular_causation"]
        assert cc["source_label"] == "A"
        assert cc["cycles"] == {"base": 1, "alternative": 1, "delta": 0}
        assert cc["reinforcing"]["base"] == 1
        assert cc["max_strength"]["base"] == pytest.approx(0.36)
        assert cc["max_strength"]["alternative"] == pytest.approx(0.42)

        degree = result["centrality"]["degree"]
        labels = {m["label"] for m in degree["top_movers"]}
        assert {"C", "D"} <= labels
        assert all("delta" in m for m in degree["top_movers"])

    def test_two_committed_versions(self, loop_service):
        svc = loop_service
        svc.create_node(Node(label="E"))
        svc.commit("added E", tags=["with-e"])

        result = svc.compare_scenarios(base_ref="baseline", alt_ref="with-e", analyses=["structure"])
        assert result["alternative"]["ref"] == "with-e"
        assert result["alternative"]["message"] == "added E"
        assert result["structure"]["nodes"] == {"base": 4, "alternative": 5, "delta": 1}
        assert result["structure"]["nodes_added"] == 1
        assert "centrality" not in result

    def test_head_relative_refs(self, loop_service):
        svc = loop_service
        svc.create_node(Node(label="E"))
        svc.commit("v2")
        result = svc.compare_scenarios(base_ref="HEAD~1", alt_ref="HEAD", analyses=["structure"])
        assert result["structure"]["nodes"]["delta"] == 1

    def test_comparison_does_not_touch_live_graph_or_engine(self, loop_service):
        svc = loop_service
        svc.initialize_query_engine()
        engine_before = svc.query_engine
        version_before = svc._graph_version
        svc.compare_scenarios(base_ref="baseline", alt_ref=None)
        assert svc._graph_version == version_before
        assert svc.query_engine is engine_before
        assert len(svc.list_nodes()) == 4

    def test_unknown_ref_raises(self, loop_service):
        with pytest.raises(VersionControlError):
            loop_service.compare_scenarios(base_ref="no-such-tag")

    def test_unknown_analysis_raises(self, loop_service):
        with pytest.raises(SFMValidationError):
            loop_service.compare_scenarios(base_ref="baseline", analyses=["vibes"])

    def test_circular_causation_requires_source(self, loop_service):
        with pytest.raises(SFMValidationError):
            loop_service.compare_scenarios(base_ref="baseline", analyses=["circular_causation"])

    def test_identical_scenarios_have_zero_deltas(self, loop_service):
        result = loop_service.compare_scenarios(base_ref="baseline", alt_ref="baseline")
        assert result["structure"]["nodes"]["delta"] == 0
        assert result["structure"]["relationships_modified"] == 0
        assert result["loops"]["participation_movers"] == []
        for kind in ("betweenness", "degree", "eigenvector"):
            assert result["centrality"][kind]["nodes_changed"] == 0
        assert result["conflicts"]["new"] == [] and result["conflicts"]["resolved"] == []


class TestCompareScenariosEndpoint:
    @pytest.fixture
    def client(self, loop_service):
        app = create_app()
        app.dependency_overrides[get_sfm_service] = lambda: loop_service
        return TestClient(app)

    def test_post_compare_working_vs_tag(self, client, loop_service):
        loop_service.create_node(Node(label="E"))
        resp = client.post("/api/v1/query/compare-scenarios", json={
            "base_ref": "baseline", "analyses": ["structure", "loops"],
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["alternative"]["ref"] == "working"
        assert data["structure"]["nodes"] == {"base": 4, "alternative": 5, "delta": 1}
        assert data["loops"]["simple_cycles"]["base"] == 1
        assert data["centrality"] is None

    def test_unknown_ref_is_404(self, client):
        resp = client.post("/api/v1/query/compare-scenarios", json={"base_ref": "missing"})
        assert resp.status_code == 404
        assert "missing" in resp.json()["detail"]

    def test_unknown_analysis_is_400(self, client):
        resp = client.post("/api/v1/query/compare-scenarios", json={
            "base_ref": "baseline", "analyses": ["vibes"],
        })
        assert resp.status_code == 400
        assert resp.json()["error"] == "VALIDATION_ERROR"

    def test_top_n_validation(self, client):
        resp = client.post("/api/v1/query/compare-scenarios", json={"base_ref": "baseline", "top_n": 0})
        assert resp.status_code == 422
