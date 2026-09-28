"""CSV relationship import: companion file, label/UUID endpoints, service resolution, REST."""

import uuid
from io import BytesIO

import pytest
from fastapi.testclient import TestClient

from api.rest.app import create_app
from api.rest.dependencies import get_sfm_service
from api.sfm_service import SFMService
from data.importers import CSVImportAdapter, ImportConfig, MappingTemplates
from models import Node


NODES = "name,description\nEPA,Regulator\nIndustry,Regulated\nLobby,Advocacy\n"
RELS = (
    "source,target,kind,weight,confidence,data_sources,meta\n"
    "EPA,Industry,regulates,0.9,0.8,CAA 1990;EPA report,\"{\"\"evidence\"\": \"\"statute\"\"}\"\n"
    "Industry,Lobby,funds,0.7,,,\n"
    "Lobby,EPA,influences,,,,plain note\n"
)


@pytest.fixture
def files(tmp_path):
    nodes = tmp_path / "institutions.csv"
    nodes.write_text(NODES)
    rels = tmp_path / "institutions_relationships.csv"
    rels.write_text(RELS)
    return nodes, rels


class TestAdapter:
    def test_sibling_file_is_discovered(self, files):
        nodes, _ = files
        adapter = CSVImportAdapter(MappingTemplates.basic_node())
        rels = list(adapter.extract_relationships(str(nodes)))
        assert [r["kind"] for r in rels] == ["regulates", "funds", "influences"]
        first = rels[0]
        assert first["source_label"] == "EPA" and first["target_label"] == "Industry"
        assert first["weight"] == 0.9
        assert first["confidence"] == 0.8
        assert first["data_sources"] == ["CAA 1990", "EPA report"]
        assert first["meta"] == {"evidence": "statute"}
        assert "weight" not in rels[2]
        assert rels[2]["meta"] == {"note": "plain note"}

    def test_explicit_file_and_uuid_endpoints(self, tmp_path):
        a, b = uuid.uuid4(), uuid.uuid4()
        rels = tmp_path / "edges.csv"
        rels.write_text(f"from,to,type,id\n{a},{b},links,{uuid.uuid5(uuid.NAMESPACE_URL, 'e1')}\n")
        nodes = tmp_path / "n.csv"
        nodes.write_text(NODES)
        adapter = CSVImportAdapter(MappingTemplates.basic_node(), relationships_file=rels)
        out = list(adapter.extract_relationships(str(nodes)))
        assert out == [{
            "kind": "links", "meta": {}, "source_id": a, "target_id": b,
            "id": uuid.uuid5(uuid.NAMESPACE_URL, "e1"),
        }]

    def test_no_companion_yields_nothing(self, tmp_path):
        nodes = tmp_path / "alone.csv"
        nodes.write_text(NODES)
        assert list(CSVImportAdapter(MappingTemplates.basic_node()).extract_relationships(str(nodes))) == []

    def test_incomplete_rows_skipped_or_raise(self, tmp_path):
        rels = tmp_path / "r.csv"
        rels.write_text("source,target,kind\nA,,x\nA,B,\nA,B,ok\n")
        nodes = tmp_path / "n.csv"
        nodes.write_text(NODES)
        lenient = CSVImportAdapter(MappingTemplates.basic_node(), relationships_file=rels)
        assert [r["kind"] for r in lenient.extract_relationships(str(nodes))] == ["ok"]
        strict = CSVImportAdapter(MappingTemplates.basic_node(), relationships_file=rels,
                                  config=ImportConfig(continue_on_error=False))
        with pytest.raises(ValueError):
            list(strict.extract_relationships(str(nodes)))


class TestServiceImport:
    def test_labels_resolve_to_nodes_created_in_same_import(self, files):
        nodes, _ = files
        service = SFMService()
        result = service.import_bulk(str(nodes), adapter=CSVImportAdapter(MappingTemplates.basic_node()))

        assert result.nodes_created == 3
        assert result.relationships_created == 3
        assert result.relationships_failed == 0
        by_kind = {r.kind: r for r in service.list_relationships()}
        epa = next(n for n in service.list_nodes() if n.label == "EPA")
        industry = next(n for n in service.list_nodes() if n.label == "Industry")
        assert by_kind["regulates"].source_id == epa.id
        assert by_kind["regulates"].target_id == industry.id
        assert by_kind["regulates"].confidence == 0.8
        assert by_kind["regulates"].data_sources == ["CAA 1990", "EPA report"]
        assert by_kind["regulates"].meta == {"evidence": "statute"}

    def test_labels_resolve_against_existing_nodes(self, tmp_path):
        service = SFMService()
        existing = service.create_node(Node(label="Courts"))
        nodes = tmp_path / "n.csv"
        nodes.write_text("name,description\nEPA,Regulator\n")
        rels = tmp_path / "n_relationships.csv"
        rels.write_text("source,target,kind\nEPA,Courts,appeals_to\nEPA,Nobody,funds\n")

        result = service.import_bulk(str(nodes), adapter=CSVImportAdapter(MappingTemplates.basic_node()))
        assert result.nodes_created == 1
        assert result.relationships_created == 1
        assert result.relationships_failed == 1
        assert any("Nobody" in e.message for e in result.errors)
        rel = service.list_relationships()[0]
        assert rel.target_id == existing.id and rel.kind == "appeals_to"

    def test_dry_run_counts_relationships_without_persisting(self, files):
        nodes, _ = files
        service = SFMService()
        result = service.import_bulk(str(nodes), adapter=CSVImportAdapter(MappingTemplates.basic_node()),
                                     config=ImportConfig(dry_run=True))
        assert result.nodes_created == 0
        assert result.relationships_created == 3
        assert service.list_relationships() == []


class TestEndpoint:
    def test_csv_upload_with_relationships_file(self):
        service = SFMService()
        app = create_app()
        app.dependency_overrides[get_sfm_service] = lambda: service
        client = TestClient(app)

        response = client.post(
            "/api/v1/import/csv",
            files={
                "file": ("inst.csv", BytesIO(NODES.encode()), "text/csv"),
                "relationships": ("inst_rels.csv", BytesIO(RELS.encode()), "text/csv"),
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["nodes_created"] == 3
        assert data["relationships_created"] == 3
        assert len(service.list_relationships()) == 3

    def test_unsupported_relationships_extension_is_400(self):
        client = TestClient(create_app())
        response = client.post(
            "/api/v1/import/csv",
            files={
                "file": ("inst.csv", BytesIO(NODES.encode()), "text/csv"),
                "relationships": ("rels.pdf", BytesIO(b"x"), "application/pdf"),
            },
        )
        assert response.status_code == 400
        assert "relationships file type" in response.json()["detail"]
