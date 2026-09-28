"""
Tests for the RDF / Linked Data adapter.

Covers detection, entity and relationship extraction from Turtle, language
preference, deterministic IRI-derived ids, type_map, JSON-LD parsing, and
service-level import including relationships.
"""

import uuid

import pytest

from api.sfm_service import SFMService
from data.importers import RDFAdapter, ImportConfig, iri_to_uuid, MappingTemplates
from data.importers.validators import ValidationError
from models import Node
from models.institutional_analysis import InstitutionalStructure


TURTLE = """
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix schema: <https://schema.org/> .
@prefix ex: <http://example.org/> .

ex:EPA a schema:GovernmentOrganization ;
    rdfs:label "Environmental Protection Agency"@en , "Agence de protection"@fr ;
    rdfs:comment "US federal regulator" ;
    schema:regulates ex:AutoIndustry ;
    schema:memberOf ex:Cabinet .

ex:AutoIndustry a schema:Organization ;
    schema:name "Auto Industry" ;
    schema:funds ex:Lobby ;
    schema:employee "not a resource" .

ex:Lobby rdfs:label "Industry Lobby" ;
    schema:influences ex:EPA .

ex:Cabinet a schema:Organization .

ex:Unlabelled schema:funds ex:EPA .
"""


@pytest.fixture
def ttl_file(tmp_path):
    path = tmp_path / "institutions.ttl"
    path.write_text(TURTLE)
    return str(path)


class TestDetection:
    def test_detects_rdf_files_and_prefix(self, ttl_file, tmp_path):
        adapter = RDFAdapter()
        assert adapter.detect_format(ttl_file) is True
        assert adapter.detect_format("rdf:" + ttl_file) is True
        assert adapter.detect_format("data.csv") is False
        assert adapter.detect_format({"x": 1}) is False

        xml = tmp_path / "plain.xml"
        xml.write_text("<root/>")
        assert adapter.detect_format(str(xml)) is False
        rdfxml = tmp_path / "graph.xml"
        rdfxml.write_text('<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"/>')
        assert adapter.detect_format(str(rdfxml)) is True

    def test_validate_format(self, ttl_file, tmp_path):
        adapter = RDFAdapter()
        assert adapter.validate_format(ttl_file) == []
        assert "not found" in adapter.validate_format(str(tmp_path / "missing.ttl"))[0]
        odd = tmp_path / "data.bin"
        odd.write_text("x")
        assert "Cannot infer" in adapter.validate_format(str(odd))[0]
        assert RDFAdapter(rdf_format="turtle").validate_format(str(odd)) == []


class TestExtraction:
    def test_entities_with_labels_become_nodes(self, ttl_file):
        nodes = list(RDFAdapter().extract_nodes(ttl_file))
        by_label = {n["label"]: n for n in nodes}
        # Cabinet has no label and Unlabelled has no label: neither becomes a node
        assert set(by_label) == {"Environmental Protection Agency", "Auto Industry", "Industry Lobby"}

        epa = by_label["Environmental Protection Agency"]
        assert epa["_node_type"] == "Node"
        assert epa["id"] == iri_to_uuid("http://example.org/EPA")
        assert epa["description"] == "US federal regulator"
        assert epa["meta"]["uri"] == "http://example.org/EPA"
        assert epa["meta"]["rdf_types"] == ["https://schema.org/GovernmentOrganization"]
        assert epa["meta"]["data_source"] == "RDF"
        assert by_label["Industry Lobby"]["description"] == ""

    def test_language_preference(self, ttl_file):
        fr = RDFAdapter(preferred_language="fr")
        labels = {n["meta"]["uri"]: n["label"] for n in fr.extract_nodes(ttl_file)}
        assert labels["http://example.org/EPA"] == "Agence de protection"
        # Auto Industry only has an untagged schema:name; falls back to it
        assert labels["http://example.org/AutoIndustry"] == "Auto Industry"

    def test_ids_are_deterministic(self, ttl_file):
        first = {n["meta"]["uri"]: n["id"] for n in RDFAdapter().extract_nodes(ttl_file)}
        second = {n["meta"]["uri"]: n["id"] for n in RDFAdapter().extract_nodes(ttl_file)}
        assert first == second
        assert all(isinstance(v, uuid.UUID) for v in first.values())

    def test_type_map_overrides_node_type(self, ttl_file):
        adapter = RDFAdapter(type_map={
            "GovernmentOrganization": "InstitutionalStructure",
            "https://schema.org/Organization": "PolicyInstrument",
        })
        types = {n["label"]: n["_node_type"] for n in adapter.extract_nodes(ttl_file)}
        assert types == {
            "Environmental Protection Agency": "InstitutionalStructure",
            "Auto Industry": "PolicyInstrument",
            "Industry Lobby": "Node",
        }

    def test_relationships_between_labelled_resources(self, ttl_file):
        rels = list(RDFAdapter().extract_relationships(ttl_file))
        epa, auto, lobby = (iri_to_uuid(f"http://example.org/{n}") for n in ("EPA", "AutoIndustry", "Lobby"))
        triples = {(r["source_id"], r["kind"], r["target_id"]) for r in rels}
        assert triples == {
            (epa, "regulates", auto),
            (auto, "funds", lobby),
            (lobby, "influences", epa),
        }
        # memberOf -> Cabinet (unlabelled) and the literal employee value are excluded
        assert all(r["meta"]["predicate"].startswith("https://schema.org/") for r in rels)
        assert RDFAdapter().estimate_size(ttl_file) == 3

    def test_camel_case_predicates_become_snake_case(self, tmp_path):
        path = tmp_path / "p.ttl"
        path.write_text("""
        @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        @prefix ex: <http://example.org/> .
        ex:A rdfs:label "A" ; ex:reportsTo ex:B ; ex:hasPart2 ex:B .
        ex:B rdfs:label "B" .
        """)
        kinds = sorted(r["kind"] for r in RDFAdapter().extract_relationships(str(path)))
        assert kinds == ["has_part2", "reports_to"]

    def test_jsonld(self, tmp_path):
        path = tmp_path / "g.jsonld"
        path.write_text("""
        {"@context": {"name": "https://schema.org/name", "knows": {"@id": "https://schema.org/knows", "@type": "@id"}},
         "@graph": [
           {"@id": "http://example.org/a", "name": "Alpha", "knows": "http://example.org/b"},
           {"@id": "http://example.org/b", "name": "Beta"}
         ]}
        """)
        adapter = RDFAdapter()
        assert {n["label"] for n in adapter.extract_nodes(str(path))} == {"Alpha", "Beta"}
        assert [r["kind"] for r in adapter.extract_relationships(str(path))] == ["knows"]

    def test_unparseable_file_raises(self, tmp_path):
        path = tmp_path / "bad.ttl"
        path.write_text("this is not turtle @@@")
        with pytest.raises(ValidationError):
            list(RDFAdapter().extract_nodes(str(path)))

    def test_rdf_entity_template_requires_label(self):
        with pytest.raises(KeyError):
            MappingTemplates.rdf_entity().transform_row({"id": uuid.uuid4(), "uri": "x"})


class TestServiceImport:
    def test_import_bulk_creates_nodes_and_relationships(self, ttl_file):
        service = SFMService()
        adapter = RDFAdapter(type_map={"GovernmentOrganization": "InstitutionalStructure"})
        result = service.import_bulk(ttl_file, adapter=adapter)

        assert result.nodes_created == 3
        assert result.nodes_failed == 0
        assert result.relationships_created == 3
        assert result.relationships_failed == 0
        assert result.errors == []

        epa = service.get_node(iri_to_uuid("http://example.org/EPA"))
        assert isinstance(epa, InstitutionalStructure)
        assert epa.label == "Environmental Protection Agency"
        kinds = sorted(r.kind for r in service.list_relationships())
        assert kinds == ["funds", "influences", "regulates"]

        service.initialize_query_engine()
        cycles = service.get_circular_causation(epa.id)
        assert len(cycles) == 1
        assert cycles[0]["labels"] == [
            "Environmental Protection Agency", "Auto Industry", "Industry Lobby", "Environmental Protection Agency"
        ]

    def test_dry_run_counts_without_persisting(self, ttl_file):
        service = SFMService()
        result = service.import_bulk(ttl_file, adapter=RDFAdapter(), config=ImportConfig(dry_run=True))
        assert result.nodes_created == 0
        assert result.relationships_created == 3
        assert service.list_nodes() == [] and service.list_relationships() == []

    def test_reimport_is_idempotent(self, ttl_file):
        service = SFMService()
        service.import_bulk(ttl_file, adapter=RDFAdapter())
        second = service.import_bulk(ttl_file, adapter=RDFAdapter())
        # Same deterministic ids: every node and relationship is reported as a duplicate...
        assert second.nodes_created == 0 and second.nodes_failed == 3
        assert second.relationships_created == 0 and second.relationships_failed == 3
        assert all("already exists" in e.message for e in second.errors)
        # ...and the graph keeps exactly one copy of each
        assert len(service.list_nodes()) == 3
        assert len(service.list_relationships()) == 3

    def test_duplicate_inside_a_batch_does_not_sink_the_batch(self, ttl_file):
        """A pre-existing id in a bulk batch must fail only that node, not the whole batch."""
        service = SFMService()
        service.create_node(Node(id=iri_to_uuid("http://example.org/Lobby"), label="pre-existing"))
        result = service.import_bulk(ttl_file, adapter=RDFAdapter())
        assert result.nodes_created == 2
        assert result.nodes_failed == 1
        assert result.relationships_created == 3
        assert len(service.list_nodes()) == 3
