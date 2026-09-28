"""
RDF / Linked Data import adapter.

Reads any RDF serialisation rdflib understands (Turtle, RDF/XML, N-Triples,
N3, JSON-LD, TriG) and turns labelled resources into SFM nodes and the object
properties between them into relationships.

Node identity is deterministic: a resource's UUID is uuid5(NAMESPACE_URL, iri),
so re-importing the same data updates rather than duplicates, and
relationships can be resolved by IRI without a lookup table.
"""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Set, Union

from .base_adapter import BaseImportAdapter, ImportConfig
from .mapping_config import MappingConfig
from .validators import ValidationError

try:
    import rdflib
    from rdflib import Graph, Literal, URIRef
    from rdflib.namespace import DCTERMS, FOAF, RDF, RDFS, SKOS
    _RDFLIB_AVAILABLE = True
except ImportError:  # pragma: no cover - exercised only when rdflib is absent
    rdflib = None  # type: ignore[assignment]
    _RDFLIB_AVAILABLE = False


RDF_EXTENSIONS = {
    ".ttl": "turtle",
    ".rdf": "xml",
    ".owl": "xml",
    ".xml": "xml",
    ".nt": "nt",
    ".n3": "n3",
    ".jsonld": "json-ld",
    ".json": "json-ld",
    ".trig": "trig",
}


def _ns(uri: str) -> Any:
    return URIRef(uri)


def _local_name(iri: str) -> str:
    """Last path segment or fragment of an IRI, as a snake_case identifier."""
    tail = iri.rsplit("#", 1)[-1].rsplit("/", 1)[-1]
    out = []
    for i, ch in enumerate(tail):
        if ch.isupper() and i and (tail[i - 1].islower() or tail[i - 1].isdigit()):
            out.append("_")
        out.append(ch.lower() if ch.isalnum() else "_")
    return "".join(out).strip("_") or "related_to"


def iri_to_uuid(iri: str) -> uuid.UUID:
    return uuid.uuid5(uuid.NAMESPACE_URL, str(iri))


class RDFAdapter(BaseImportAdapter):
    """Import adapter for RDF files (Turtle, RDF/XML, N-Triples, N3, JSON-LD, TriG)."""

    def __init__(
        self,
        mapping: Optional[MappingConfig] = None,
        config: Optional[ImportConfig] = None,
        rdf_format: Optional[str] = None,
        type_map: Optional[Dict[str, str]] = None,
        label_predicates: Optional[List[str]] = None,
        description_predicates: Optional[List[str]] = None,
        preferred_language: str = "en",
    ):
        """
        Args:
            mapping: Field mapping (defaults to MappingTemplates.rdf_entity())
            config: Import configuration
            rdf_format: rdflib parser name; inferred from the file extension if omitted
            type_map: rdf:type IRI or local name -> SFM node type name
                      (e.g. {"Organization": "InstitutionalStructure"})
            label_predicates: IRIs to read the node label from, in priority order
            description_predicates: IRIs to read the description from, in priority order
            preferred_language: Language tag preferred when a literal has several
        """
        if not _RDFLIB_AVAILABLE:
            raise ImportError("rdflib is required for RDFAdapter. Install it with: pip install rdflib")
        super().__init__(config)
        self.mapping = mapping or self._default_mapping()
        self.rdf_format = rdf_format
        self.type_map = {self._key(k): v for k, v in (type_map or {}).items()}
        self.preferred_language = preferred_language
        self.label_predicates = [
            _ns(p) for p in (label_predicates or [
                str(RDFS.label), "https://schema.org/name", "http://schema.org/name",
                str(SKOS.prefLabel), str(DCTERMS.title), str(FOAF.name),
            ])
        ]
        self.description_predicates = [
            _ns(p) for p in (description_predicates or [
                str(RDFS.comment), "https://schema.org/description", "http://schema.org/description",
                str(DCTERMS.description), str(SKOS.definition),
            ])
        ]
        self._graph_cache: Dict[str, Any] = {}

    @staticmethod
    def _key(type_ref: str) -> str:
        """type_map keys may be full IRIs or local names; normalise both to the local name."""
        return _local_name(type_ref)

    def _default_mapping(self) -> MappingConfig:
        from .mapping_config import MappingTemplates
        return MappingTemplates.rdf_entity()

    # ------------------------------------------------------------------ format

    def detect_format(self, source: Union[str, Path, Dict[str, Any]]) -> bool:
        if isinstance(source, dict):
            return False
        if isinstance(source, str) and source.startswith("rdf:"):
            return True
        path = Path(source)
        if path.suffix.lower() not in RDF_EXTENSIONS or not path.is_file():
            return False
        if path.suffix.lower() in (".xml", ".json"):
            head = path.read_text(encoding="utf-8", errors="ignore")[:4096]
            return "rdf" in head.lower() or "@context" in head
        return True

    def validate_format(self, source: Union[str, Path, Dict[str, Any]]) -> List[str]:
        path = self._path(source)
        if not path.is_file():
            return [f"RDF file not found: {path}"]
        if self.rdf_format is None and path.suffix.lower() not in RDF_EXTENSIONS:
            return [f"Cannot infer RDF format from extension '{path.suffix}'; pass rdf_format explicitly"]
        return []

    # ----------------------------------------------------------------- parsing

    @staticmethod
    def _path(source: Union[str, Path, Dict[str, Any]]) -> Path:
        if isinstance(source, dict):
            raise ValidationError("RDFAdapter needs a file path, not a dict")
        text = str(source)
        return Path(text[4:] if text.startswith("rdf:") else text)

    def _load(self, source: Union[str, Path, Dict[str, Any]]) -> Any:
        path = self._path(source)
        key = str(path.resolve())
        if key in self._graph_cache:
            return self._graph_cache[key]
        fmt = self.rdf_format or RDF_EXTENSIONS.get(path.suffix.lower())
        graph = Graph()
        try:
            graph.parse(str(path), format=fmt)
        except Exception as e:
            raise ValidationError(f"Failed to parse RDF file {path}: {e}") from e
        self._graph_cache[key] = graph
        return graph

    def _literal(self, graph: Any, subject: Any, predicates: List[Any]) -> Optional[str]:
        for predicate in predicates:
            values = [o for o in graph.objects(subject, predicate) if isinstance(o, Literal)]
            if not values:
                continue
            for value in values:
                if value.language == self.preferred_language:
                    return str(value)
            for value in values:
                if not value.language:
                    return str(value)
            return str(values[0])
        return None

    def _entities(self, graph: Any) -> Dict[Any, Dict[str, Any]]:
        """Every IRI subject with a label becomes a node; others are treated as vocabulary."""
        entities: Dict[Any, Dict[str, Any]] = {}
        for subject in sorted(set(graph.subjects()), key=str):
            if not isinstance(subject, URIRef):
                continue
            label = self._literal(graph, subject, self.label_predicates)
            if label is None:
                continue
            rdf_types = [str(t) for t in graph.objects(subject, RDF.type) if isinstance(t, URIRef)]
            entities[subject] = {
                "id": iri_to_uuid(subject),
                "uri": str(subject),
                "label": label,
                "description": self._literal(graph, subject, self.description_predicates) or "",
                "rdf_types": rdf_types,
                "rdf_type_names": [_local_name(t) for t in rdf_types],
                "data_source": "RDF",
            }
        return entities

    def _node_type_for(self, rdf_types: List[str]) -> Optional[str]:
        for type_iri in rdf_types:
            mapped = self.type_map.get(_local_name(type_iri))
            if mapped:
                return mapped
        return None

    # -------------------------------------------------------------- extraction

    def extract_nodes(self, source: Union[str, Path, Dict[str, Any]]) -> Iterator[Dict[str, Any]]:
        graph = self._load(source)
        for entity in self._entities(graph).values():
            try:
                mapped = self.mapping.transform_row(entity)
            except (KeyError, ValueError) as e:
                if not self.config.continue_on_error:
                    raise ValueError(f"Failed to map RDF entity {entity['uri']}: {e}") from e
                continue
            node_type = self._node_type_for(entity["rdf_types"])
            if node_type:
                mapped["_node_type"] = node_type
            yield mapped

    def extract_relationships(self, source: Union[str, Path, Dict[str, Any]]) -> Iterator[Dict[str, Any]]:
        graph = self._load(source)
        entities = self._entities(graph)
        skip: Set[Any] = set(self.label_predicates) | set(self.description_predicates) | {RDF.type}
        seen: Set[Any] = set()
        for subject, predicate, obj in sorted(graph, key=lambda t: (str(t[0]), str(t[1]), str(t[2]))):
            if predicate in skip or subject not in entities or obj not in entities:
                continue
            if (subject, predicate, obj) in seen:
                continue
            seen.add((subject, predicate, obj))
            yield {
                # Deterministic so re-importing the same triple is a duplicate, not a second edge
                "id": uuid.uuid5(uuid.NAMESPACE_URL, f"{subject} {predicate} {obj}"),
                "source_id": entities[subject]["id"],
                "target_id": entities[obj]["id"],
                "kind": _local_name(str(predicate)),
                "meta": {"predicate": str(predicate), "data_source": "RDF"},
            }

    def estimate_size(self, source: Union[str, Path, Dict[str, Any]]) -> Optional[int]:
        try:
            return len(self._entities(self._load(source)))
        except ValidationError:
            return None
