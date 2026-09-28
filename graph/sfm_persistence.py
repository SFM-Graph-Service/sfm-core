"""
SFM Graph Persistence Manager (Beta)

Provides persistence capabilities for Social Fabric Matrix graphs using the Beta unified model.
Enables storage, loading, and serialization of in-memory graph data.

Key Features:
- JSON storage formats (default and recommended)
- Pickle storage formats (opt-in only — see security warning below)
- Serialization for all 33 Beta unified model node types
- Data validation and integrity checking
- Version management

.. warning:: **Pickle Security**
    The ``PICKLE`` and ``COMPRESSED_PICKLE`` storage formats use Python's
    ``pickle`` module.  Deserializing pickle data from an **untrusted source**
    allows arbitrary code execution on the host.  Pickle deserialization is
    therefore **disabled by default**.  It must be explicitly opted into by
    passing ``allow_pickle=True`` to :meth:`SFMGraphSerializer.deserialize_graph`
    and :meth:`SFMPersistenceManager.load_graph`.  Never enable ``allow_pickle``
    for data received from untrusted parties.  The default and recommended
    format is JSON.
"""

import gzip
import hashlib
import json
import logging
import pickle
import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union, cast, get_args, get_origin, get_type_hints

import networkx as nx

# Import all Beta unified model node types
from models import (
    Node,
    InformalNorm,
    MatrixCell,
    SFMCriteria,
    SFMMatrix,
    SystemProperty,
    SystemLevelAnalysis,
    InstitutionalHolarchy,
    PolicyInstrument,
    ValueJudgment,
    ProblemSolvingSequence,
    InstitutionalStructure,
    PathDependencyAnalysis,
    TransactionCost,
    CoordinationMechanism,
    CommonsGovernance,
    CeremonialInstrumentalClassification,
    ValueSystem,
    SocialBelief,
    CulturalAttitude,
    SocialValueAssessment,
    SocialFabricIndicator,
    SocialCost,
    ToolSkillTechnologyComplex,
    EcologicalSystem,
    CrossImpactAnalysis,
    DeliveryRelationship,
    MatrixDeliveryNetwork,
    DigraphAnalysis,
    CircularCausationProcess,
    ConflictDetection,
    InstrumentalistInquiryFramework,
    NormativeSystemsAnalysis,
    PolicyRelevanceIntegration,
    DatabaseIntegrationCapability,
    SocialIndicatorSystem,
    EvolutionaryPathway,
    SocialProvisioningMatrix,
    Scenario,
    ScenarioPath,
    ScenarioSet,
    Event,
)

# Import Hayden-compliant delivery matrix types
from models.delivery_matrix import Delivery, SFMDeliveryCell, SFMDeliveryMatrix

# Import temporal modeling types
from models.temporal_clocks import TemporalClock, TemporalPhase

# Setup logging
logger = logging.getLogger(__name__)


class StorageFormat(Enum):
    """Supported storage formats for SFM graphs."""
    JSON = "json"
    PICKLE = "pickle"
    COMPRESSED_JSON = "json.gz"
    COMPRESSED_PICKLE = "pickle.gz"


@dataclass
class GraphMetadata:
    """Metadata associated with stored graphs."""
    graph_id: str
    name: str
    description: str = ""
    version: int = 1
    created_at: Optional[datetime] = None
    modified_at: Optional[datetime] = None
    node_count: int = 0
    relationship_count: int = 0
    checksum: str = ""
    format: StorageFormat = StorageFormat.JSON

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


class SFMSerializationError(Exception):
    """Errors related to graph serialization/deserialization."""


class SFMPersistenceError(Exception):
    """General persistence-related errors."""


class NodeSerializer:
    """Handles serialization of Beta unified model nodes."""

    # Map of all Beta node types plus Hayden-compliant delivery matrix types for serialization
    NODE_TYPE_REGISTRY: Dict[str, type] = {
        "Node": Node,
        "InformalNorm": InformalNorm,
        "MatrixCell": MatrixCell,
        "SFMCriteria": SFMCriteria,
        "SFMMatrix": SFMMatrix,
        "SystemProperty": SystemProperty,
        "SystemLevelAnalysis": SystemLevelAnalysis,
        "InstitutionalHolarchy": InstitutionalHolarchy,
        "PolicyInstrument": PolicyInstrument,
        "ValueJudgment": ValueJudgment,
        "ProblemSolvingSequence": ProblemSolvingSequence,
        "InstitutionalStructure": InstitutionalStructure,
        "PathDependencyAnalysis": PathDependencyAnalysis,
        "TransactionCost": TransactionCost,
        "CoordinationMechanism": CoordinationMechanism,
        "CommonsGovernance": CommonsGovernance,
        "CeremonialInstrumentalClassification": CeremonialInstrumentalClassification,
        "ValueSystem": ValueSystem,
        "SocialBelief": SocialBelief,
        "CulturalAttitude": CulturalAttitude,
        "SocialValueAssessment": SocialValueAssessment,
        "SocialFabricIndicator": SocialFabricIndicator,
        "SocialCost": SocialCost,
        "ToolSkillTechnologyComplex": ToolSkillTechnologyComplex,
        "EcologicalSystem": EcologicalSystem,
        "CrossImpactAnalysis": CrossImpactAnalysis,
        "DeliveryRelationship": DeliveryRelationship,
        "MatrixDeliveryNetwork": MatrixDeliveryNetwork,
        "DigraphAnalysis": DigraphAnalysis,
        "CircularCausationProcess": CircularCausationProcess,
        "ConflictDetection": ConflictDetection,
        "InstrumentalistInquiryFramework": InstrumentalistInquiryFramework,
        "NormativeSystemsAnalysis": NormativeSystemsAnalysis,
        "PolicyRelevanceIntegration": PolicyRelevanceIntegration,
        "DatabaseIntegrationCapability": DatabaseIntegrationCapability,
        "SocialIndicatorSystem": SocialIndicatorSystem,
        "EvolutionaryPathway": EvolutionaryPathway,
        "SocialProvisioningMatrix": SocialProvisioningMatrix,
        "Scenario": Scenario,
        "ScenarioPath": ScenarioPath,
        "ScenarioSet": ScenarioSet,
        "Event": Event,
        # Hayden-compliant delivery matrix types
        "Delivery": Delivery,
        "SFMDeliveryCell": SFMDeliveryCell,
        "SFMDeliveryMatrix": SFMDeliveryMatrix,
        # Temporal modeling types
        "TemporalClock": TemporalClock,
        "TemporalPhase": TemporalPhase,
    }

    @staticmethod
    def get_node_class(node_type_name: str) -> Optional[type]:
        """
        Get node class by type name.

        Args:
            node_type_name: Name of node type (e.g., "InstitutionalStructure")

        Returns:
            Node class or None if not found
        """
        return NodeSerializer.NODE_TYPE_REGISTRY.get(node_type_name)

    @staticmethod
    def _delivery_to_dict(delivery: Any) -> Dict[str, Any]:
        """Serialize a Delivery dataclass to a plain dictionary."""
        return {
            'delivery_type': delivery.delivery_type,
            'delivery_content': delivery.delivery_content,
            'quantity': delivery.quantity,
            'units': delivery.units,
            'temporal_rate': delivery.temporal_rate,
            'temporal_clock': delivery.temporal_clock,
            'threshold': delivery.threshold,
            'threshold_direction': delivery.threshold_direction,
            'last_threshold_check': (
                delivery.last_threshold_check.isoformat()
                if delivery.last_threshold_check is not None else None
            ),
            'certainty': delivery.certainty,
            'data_sources': list(delivery.data_sources),
        }

    @staticmethod
    def _to_jsonable(value: Any) -> Any:
        """Recursively convert UUIDs, datetimes and Enums (inside lists, tuples, dicts) to JSON-safe values."""
        if isinstance(value, uuid.UUID):
            return str(value)
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, Enum):
            return value.value
        if isinstance(value, dict):
            return {
                (str(k) if isinstance(k, (uuid.UUID, Enum, datetime)) else k): NodeSerializer._to_jsonable(v)
                for k, v in value.items()
            }
        if isinstance(value, (list, tuple)):
            return [NodeSerializer._to_jsonable(v) for v in value]
        return value

    @staticmethod
    def node_to_dict(node: Node) -> Dict[str, Any]:
        """
        Convert a Node to dictionary representation.
        Handles all 33 Beta unified model node types.
        """
        result: Dict[str, Any] = {
            'type': type(node).__name__,
            'id': str(node.id),
            'label': node.label,
            'description': node.description,
            'meta': node.meta,
        }

        # Add all attributes from the node's __dict__
        for key, value in node.__dict__.items():
            if key not in result and not key.startswith('_'):
                # Special handling for SFMDeliveryMatrix.cells:
                # The dict has Tuple[UUID, UUID] keys which are not JSON-serialisable.
                if key == 'cells' and hasattr(node, 'components'):
                    serialized_cells: Dict[str, Any] = {}
                    for (src_id, tgt_id), cell in value.items():
                        cell_key = f"{src_id}:{tgt_id}"
                        serialized_cells[cell_key] = NodeSerializer.node_to_dict(cell)
                    result[key] = serialized_cells
                # Special handling for SFMDeliveryMatrix.components (List[UUID]):
                elif key == 'components' and isinstance(value, list):
                    result[key] = [str(v) if isinstance(v, uuid.UUID) else v for v in value]
                # Special handling for SFMDeliveryCell.deliveries (List[Delivery]):
                elif key == 'deliveries' and isinstance(value, list):
                    result[key] = [NodeSerializer._delivery_to_dict(d) for d in value]
                # Handle special types, including inside containers
                elif isinstance(value, (uuid.UUID, datetime, Enum, list, tuple, dict)):
                    result[key] = NodeSerializer._to_jsonable(value)
                elif isinstance(value, (str, int, float, bool, type(None))):
                    result[key] = value
                else:
                    # Try to convert to string for other types
                    try:
                        result[key] = str(value)
                    except Exception:
                        logger.warning("Could not serialize attribute %s of node %s", key, node.id)

        return result

    @staticmethod
    def _coerce_value(hint: Any, value: Any) -> Any:
        """Coerce a JSON-shaped value back to the type its dataclass field declares."""
        origin = get_origin(hint)
        args = get_args(hint)

        if origin is Union:
            if value is None:
                return None
            for candidate in (a for a in args if a is not type(None)):
                try:
                    return NodeSerializer._coerce_value(candidate, value)
                except (ValueError, TypeError):
                    continue
            return value
        if origin in (list, List):
            if isinstance(value, list) and args:
                return [NodeSerializer._coerce_value(args[0], v) for v in value]
            return value
        if origin in (tuple, Tuple):
            if isinstance(value, (list, tuple)) and args:
                hints = [args[0]] * len(value) if len(args) == 2 and args[1] is Ellipsis else list(args)
                return tuple(NodeSerializer._coerce_value(h, v) for h, v in zip(hints, value))
            return value
        if origin in (dict, Dict):
            if isinstance(value, dict) and len(args) == 2:
                return {
                    NodeSerializer._coerce_value(args[0], k): NodeSerializer._coerce_value(args[1], v)
                    for k, v in value.items()
                }
            return value
        if hint is datetime and isinstance(value, str):
            return datetime.fromisoformat(value)
        if hint is uuid.UUID and isinstance(value, str):
            return uuid.UUID(value)
        if isinstance(hint, type) and issubclass(hint, Enum) and not isinstance(value, hint):
            return hint(value)
        return value

    @staticmethod
    def _coerce_fields(node_class: type, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Restore datetime, UUID and Enum values (and containers of them) from their
        serialised forms, driven by the dataclass field annotations, so a node
        reads back with the same types it was written with.
        """
        try:
            hints = get_type_hints(node_class)
        except Exception:  # unresolved forward references: leave values as-is
            return node_data
        coerced: Dict[str, Any] = {}
        for key, value in node_data.items():
            hint = hints.get(key)
            if hint is None or value is None:
                coerced[key] = value
                continue
            try:
                coerced[key] = NodeSerializer._coerce_value(hint, value)
            except (ValueError, TypeError):
                coerced[key] = value
        return coerced

    @staticmethod
    def dict_to_node(data: Dict[str, Any]) -> Node:
        """
        Convert dictionary representation back to a Node.
        Handles all 33 Beta unified model node types.
        """
        node_type_name = data.get('type')
        if not node_type_name:
            raise SFMSerializationError("Missing 'type' field in node data")

        node_class = NodeSerializer.NODE_TYPE_REGISTRY.get(node_type_name)
        if not node_class:
            raise SFMSerializationError(f"Unknown node type: {node_type_name}")

        # Convert UUID strings back to UUID objects
        if 'id' in data:
            data['id'] = uuid.UUID(data['id'])

        # Remove 'type' from data as it's not a constructor parameter
        node_data = NodeSerializer._coerce_fields(
            node_class, {k: v for k, v in data.items() if k != 'type'}
        )

        # Special handling for SFMDeliveryMatrix: reconstruct cells dict with tuple keys
        if node_type_name == 'SFMDeliveryMatrix':
            try:
                cells_data = node_data.pop('cells', {})
                components_raw = node_data.pop('components', [])
                components = [
                    uuid.UUID(c) if isinstance(c, str) else c
                    for c in components_raw
                ]
                matrix = node_class(components=components, **node_data)
                for cell_key, cell_dict in cells_data.items():
                    src_str, tgt_str = cell_key.split(':', 1)
                    src_id = uuid.UUID(src_str)
                    tgt_id = uuid.UUID(tgt_str)
                    cell = NodeSerializer.dict_to_node(cell_dict)
                    matrix.cells[(src_id, tgt_id)] = cell
                return cast(Node, matrix)
            except Exception as e:
                raise SFMSerializationError(
                    f"Failed to create SFMDeliveryMatrix: {str(e)}"
                ) from e

        # Special handling for SFMDeliveryCell: reconstruct Delivery objects and UUID fields
        if node_type_name == 'SFMDeliveryCell':
            try:
                deliveries_data = node_data.pop('deliveries', [])
                for uuid_field in ('source_component_id', 'target_component_id'):
                    if uuid_field in node_data and isinstance(node_data[uuid_field], str):
                        node_data[uuid_field] = uuid.UUID(node_data[uuid_field])
                deliveries = []
                for d_dict in deliveries_data:
                    raw = dict(d_dict)
                    if raw.get('last_threshold_check'):
                        raw['last_threshold_check'] = datetime.fromisoformat(
                            raw['last_threshold_check']
                        )
                    deliveries.append(Delivery(**raw))
                node_data['deliveries'] = deliveries
                return cast(Node, node_class(**node_data))
            except Exception as e:
                raise SFMSerializationError(
                    f"Failed to create SFMDeliveryCell: {str(e)}"
                ) from e

        # Create node instance (standard path)
        try:
            node = cast(Node, node_class(**node_data))
            return node
        except Exception as e:
            raise SFMSerializationError(
                f"Failed to create node of type {node_type_name}: {str(e)}"
            ) from e


class RelationshipSerializer:
    """
    Single source of truth for Relationship <-> dict conversion.

    Every persistence path (snapshots, version commits, deltas, JSON export and
    import) must go through this pair so that no field is silently dropped.
    from_dict tolerates the historical five-field shape (id, source_id,
    target_id, kind, weight).
    """

    @staticmethod
    def to_dict(rel: Any) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            'id': str(rel.id),
            'source_id': str(rel.source_id),
            'target_id': str(rel.target_id),
            'kind': rel.kind,
            'weight': rel.weight,
        }
        if rel.meta:
            data['meta'] = dict(rel.meta)
        if rel.confidence is not None:
            data['confidence'] = rel.confidence
        if rel.confidence_interval is not None:
            data['confidence_interval'] = list(rel.confidence_interval)
        if rel.uncertainty_type:
            data['uncertainty_type'] = rel.uncertainty_type
        if rel.data_sources:
            data['data_sources'] = list(rel.data_sources)
        if rel.source_agreement:
            data['source_agreement'] = rel.source_agreement
        if rel.valid_from is not None:
            data['valid_from'] = rel.valid_from.isoformat()
        if rel.valid_to is not None:
            data['valid_to'] = rel.valid_to.isoformat()
        return data

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> Any:
        from graph.sfm_graph import Relationship

        ci = data.get('confidence_interval')
        return Relationship(
            id=uuid.UUID(data['id']),
            source_id=uuid.UUID(data['source_id']),
            target_id=uuid.UUID(data['target_id']),
            kind=data.get('kind') or '',
            weight=data.get('weight'),
            meta=dict(data.get('meta') or {}),
            confidence=data.get('confidence'),
            confidence_interval=(ci[0], ci[1]) if ci else None,
            uncertainty_type=data.get('uncertainty_type'),
            data_sources=list(data.get('data_sources') or []),
            source_agreement=data.get('source_agreement'),
            valid_from=datetime.fromisoformat(data['valid_from']) if data.get('valid_from') else None,
            valid_to=datetime.fromisoformat(data['valid_to']) if data.get('valid_to') else None,
        )


class SFMGraphSerializer:
    """Handles serialization and deserialization of SFM graphs."""

    @staticmethod
    def serialize_graph(graph: Any, format_type: StorageFormat = StorageFormat.JSON) -> bytes:
        """Serialize an SFM graph to bytes."""
        try:
            if format_type in [StorageFormat.JSON, StorageFormat.COMPRESSED_JSON]:
                return SFMGraphSerializer._serialize_json(graph, format_type)
            if format_type in [StorageFormat.PICKLE, StorageFormat.COMPRESSED_PICKLE]:
                return SFMGraphSerializer._serialize_pickle(graph, format_type)

            raise SFMSerializationError(f"Unsupported format: {format_type}")

        except Exception as e:
            raise SFMSerializationError(f"Failed to serialize graph: {str(e)}") from e

    @staticmethod
    def _serialize_json(graph: Any, format_type: StorageFormat) -> bytes:
        """Serialize graph to JSON format."""
        data = SFMGraphSerializer._graph_to_dict(graph)
        json_str = json.dumps(data, indent=2, default=SFMGraphSerializer.json_serializer)
        json_bytes = json_str.encode('utf-8')

        if format_type == StorageFormat.COMPRESSED_JSON:
            return gzip.compress(json_bytes)
        return json_bytes

    @staticmethod
    def _serialize_pickle(graph: Any, format_type: StorageFormat) -> bytes:
        """Serialize graph to Pickle format."""
        if format_type == StorageFormat.COMPRESSED_PICKLE:
            return gzip.compress(pickle.dumps(graph, protocol=pickle.HIGHEST_PROTOCOL))
        return pickle.dumps(graph, protocol=pickle.HIGHEST_PROTOCOL)

    @staticmethod
    def _graph_to_dict(graph: Any) -> Dict[str, Any]:
        """Convert SFMGraph to dictionary representation."""
        nodes_by_type: Dict[str, List[Dict[str, Any]]] = {}

        # Group nodes by type
        for node in graph:
            node_type = type(node).__name__
            if node_type not in nodes_by_type:
                nodes_by_type[node_type] = []
            nodes_by_type[node_type].append(NodeSerializer.node_to_dict(node))

        relationships = [
            RelationshipSerializer.to_dict(rel) for rel in graph.relationships.values()
        ]

        return {
            'id': str(getattr(graph, 'id', uuid.uuid4())),
            'name': getattr(graph, 'name', 'SFM Graph'),
            'description': getattr(graph, 'description', ''),
            'nodes_by_type': nodes_by_type,
            'relationships': relationships,
            'metadata': {
                'serialized_at': datetime.now().isoformat(),
                'node_count': len(list(graph)),
                'relationship_count': len(graph.relationships),
            }
        }

    @staticmethod
    def json_serializer(obj: Any) -> Any:
        """Custom JSON serializer for special types."""
        if isinstance(obj, (datetime,)):
            return obj.isoformat()
        if isinstance(obj, uuid.UUID):
            return str(obj)
        if isinstance(obj, Enum):
            return obj.value
        raise TypeError(f"Type {type(obj)} not serializable")

    @staticmethod
    def deserialize_graph(
        data: bytes,
        format_type: StorageFormat = StorageFormat.JSON,
        allow_pickle: bool = False,
    ) -> Any:
        """Deserialize bytes to an SFM graph.

        Args:
            data: Raw bytes to deserialize.
            format_type: The :class:`StorageFormat` used when the graph was
                serialized.  Defaults to ``StorageFormat.JSON``.
            allow_pickle: Must be explicitly set to ``True`` to allow pickle
                deserialization.  Defaults to ``False``.  **Only enable this
                for data that originates from a fully trusted source** — pickle
                data from an untrusted source can execute arbitrary code.

        Raises:
            SFMSerializationError: If deserialization fails, the format is
                unsupported, or pickle deserialization is attempted without
                ``allow_pickle=True``.
        """
        try:
            if format_type in [StorageFormat.COMPRESSED_JSON, StorageFormat.COMPRESSED_PICKLE]:
                data = gzip.decompress(data)

            if format_type in [StorageFormat.JSON, StorageFormat.COMPRESSED_JSON]:
                dict_data = json.loads(data.decode('utf-8'))
                return SFMGraphSerializer._dict_to_graph(dict_data)

            if format_type in [StorageFormat.PICKLE, StorageFormat.COMPRESSED_PICKLE]:
                if not allow_pickle:
                    raise SFMSerializationError(
                        "Pickle deserialization is disabled by default because unpickling "
                        "untrusted data can execute arbitrary code (CWE-502). "
                        "Pass allow_pickle=True only when the source is fully trusted."
                    )
                return pickle.loads(data)  # nosec B301 – caller has opted in

            raise SFMSerializationError(f"Unsupported format: {format_type}")

        except SFMSerializationError:
            raise
        except Exception as e:
            raise SFMSerializationError(f"Failed to deserialize graph: {str(e)}") from e

    @staticmethod
    def _dict_to_graph(data: Dict[str, Any]) -> Any:
        """Convert dictionary representation back to SFMGraph."""
        # Import here to avoid circular dependency
        from graph.sfm_graph import SFMGraph

        graph = SFMGraph()

        # Deserialize nodes by type
        nodes_by_type = data.get('nodes_by_type', {})
        for _, nodes_data in nodes_by_type.items():
            for node_data in nodes_data:
                try:
                    node = NodeSerializer.dict_to_node(node_data)
                    graph.add_node(node)
                except Exception as e:
                    logger.warning("Failed to deserialize node: %s", str(e))

        for rel_data in data.get('relationships', []):
            try:
                graph.add_relationship(RelationshipSerializer.from_dict(rel_data))
            except Exception as e:
                logger.warning("Failed to deserialize relationship: %s", str(e))

        return graph


class SFMPersistenceManager:
    """Manages persistence operations for SFM graphs."""

    def __init__(self, base_path: str = "./sfm_data"):
        """Initialize persistence manager."""
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        logger.info("Initialized persistence manager at %s", self.base_path)

    def save_graph(
        self,
        graph: Any,
        filename: str,
        format_type: StorageFormat = StorageFormat.JSON
    ) -> GraphMetadata:
        """Save a graph to disk."""
        file_path = self.base_path / filename

        # Serialize graph
        data = SFMGraphSerializer.serialize_graph(graph, format_type)

        # Write to file
        with open(file_path, 'wb') as f:
            f.write(data)

        # Create metadata
        metadata = GraphMetadata(
            graph_id=str(getattr(graph, 'id', uuid.uuid4())),
            name=getattr(graph, 'name', 'SFM Graph'),
            description=getattr(graph, 'description', ''),
            node_count=len(list(graph)),
            relationship_count=len(graph.relationships),
            checksum=hashlib.sha256(data).hexdigest(),
            format=format_type,
        )

        logger.info("Saved graph to %s", file_path)
        return metadata

    def load_graph(
        self,
        filename: str,
        format_type: StorageFormat = StorageFormat.JSON,
        allow_pickle: bool = False,
    ) -> Any:
        """Load a graph from disk.

        Args:
            filename: Name of the file to load (relative to ``base_path``).
            format_type: The :class:`StorageFormat` the file was saved in.
                Defaults to ``StorageFormat.JSON``.
            allow_pickle: Set to ``True`` only for files from fully trusted
                sources.  See :meth:`SFMGraphSerializer.deserialize_graph` for
                the security implications.
        """
        file_path = self.base_path / filename

        if not file_path.exists():
            raise SFMPersistenceError(f"File not found: {file_path}")

        # Read file
        with open(file_path, 'rb') as f:
            data = f.read()

        # Deserialize graph
        graph = SFMGraphSerializer.deserialize_graph(data, format_type, allow_pickle=allow_pickle)

        logger.info("Loaded graph from %s", file_path)
        return graph

    def export_graphml(self, graph: Any, path: str) -> None:
        """
        Export graph to GraphML format using networkx.

        Args:
            graph: SFMGraph instance to export
            path: File path for the exported GraphML file

        Raises:
            SFMPersistenceError: If export fails
        """
        try:
            # Convert SFMGraph to networkx DiGraph
            nx_graph = self._sfm_to_networkx(graph)

            # Write to GraphML format
            nx.write_graphml(nx_graph, path)
            logger.info("Exported graph to GraphML: %s", path)

        except Exception as e:
            raise SFMPersistenceError(f"Failed to export GraphML: {str(e)}") from e

    def export_gexf(self, graph: Any, path: str) -> None:
        """
        Export graph to GEXF format using networkx.

        Args:
            graph: SFMGraph instance to export
            path: File path for the exported GEXF file

        Raises:
            SFMPersistenceError: If export fails
        """
        try:
            # Convert SFMGraph to networkx DiGraph
            nx_graph = self._sfm_to_networkx(graph)

            # Write to GEXF format
            nx.write_gexf(nx_graph, path)
            logger.info("Exported graph to GEXF: %s", path)

        except Exception as e:
            raise SFMPersistenceError(f"Failed to export GEXF: {str(e)}") from e

    def export_json_snapshot(self, graph: Any, path: str) -> None:
        """
        Export graph to a custom JSON snapshot format.

        Format: {
            "metadata": {...},
            "nodes": [...],
            "relationships": [...]
        }

        Args:
            graph: SFMGraph instance to export
            path: File path for the exported JSON file

        Raises:
            SFMPersistenceError: If export fails
        """
        try:
            # Build snapshot structure
            snapshot: Dict[str, Any] = {
                "metadata": {
                    "graph_id": str(getattr(graph, 'id', uuid.uuid4())),
                    "name": getattr(graph, 'name', 'SFM Graph'),
                    "description": getattr(graph, 'description', ''),
                    "version": getattr(graph, 'version', 1),
                    "created_at": getattr(graph, 'created_at', datetime.now()).isoformat(),
                    "exported_at": datetime.now().isoformat(),
                    "node_count": len(list(graph)),
                    "relationship_count": len(graph.relationships),
                },
                "nodes": [],
                "relationships": []
            }

            # Serialize nodes
            for node in graph:
                snapshot["nodes"].append(NodeSerializer.node_to_dict(node))

            # Serialize relationships
            for rel in graph.relationships.values():
                rel_dict = RelationshipSerializer.to_dict(rel)
                rel_dict.setdefault('meta', {})
                snapshot["relationships"].append(rel_dict)

            # Write to file
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(snapshot, f, indent=2, default=self._json_serializer)

            logger.info("Exported JSON snapshot: %s", path)

        except Exception as e:
            raise SFMPersistenceError(f"Failed to export JSON snapshot: {str(e)}") from e

    def import_json_snapshot(self, path: str) -> Any:
        """
        Import graph from a custom JSON snapshot format.

        Args:
            path: File path of the JSON snapshot to import

        Returns:
            Reconstructed SFMGraph instance

        Raises:
            SFMPersistenceError: If import fails or file not found
        """
        try:
            # Check file exists
            if not Path(path).exists():
                raise SFMPersistenceError(f"File not found: {path}")

            # Load snapshot
            with open(path, 'r', encoding='utf-8') as f:
                snapshot = json.load(f)

            # Validate snapshot structure
            if not all(key in snapshot for key in ['metadata', 'nodes', 'relationships']):
                raise SFMPersistenceError("Invalid snapshot format: missing required keys")

            # Import here to avoid circular dependency
            from graph.sfm_graph import SFMGraph

            # Create new graph
            graph = SFMGraph()
            metadata = snapshot['metadata']
            graph.id = uuid.UUID(metadata.get('graph_id', str(uuid.uuid4())))
            graph.name = metadata.get('name', 'SFM Graph')
            graph.description = metadata.get('description', '')
            graph.version = metadata.get('version', 1)

            # Deserialize nodes
            for node_data in snapshot['nodes']:
                try:
                    node = NodeSerializer.dict_to_node(node_data)
                    graph.add_node(node)
                except Exception as e:
                    logger.warning("Failed to deserialize node: %s", str(e))

            # Deserialize relationships
            for rel_data in snapshot['relationships']:
                try:
                    graph.add_relationship(RelationshipSerializer.from_dict(rel_data))
                except Exception as e:
                    logger.warning("Failed to deserialize relationship: %s", str(e))

            logger.info("Imported JSON snapshot from: %s", path)
            logger.info("Loaded %d nodes and %d relationships",
                       len(list(graph)), len(graph.relationships))

            return graph

        except SFMPersistenceError:
            raise
        except Exception as e:
            raise SFMPersistenceError(f"Failed to import JSON snapshot: {str(e)}") from e

    def _sfm_to_networkx(self, graph: Any) -> nx.DiGraph:
        """
        Convert SFMGraph to networkx DiGraph.

        Args:
            graph: SFMGraph instance to convert

        Returns:
            networkx DiGraph with node and edge attributes
        """
        nx_graph: nx.DiGraph = nx.DiGraph()

        # Add nodes with attributes
        for node in graph:
            node_attrs = {
                'label': node.label,
                'description': node.description,
                'type': type(node).__name__,
            }
            # Add additional attributes from node meta
            if hasattr(node, 'meta') and node.meta:
                node_attrs['meta'] = json.dumps(node.meta)

            nx_graph.add_node(str(node.id), **node_attrs)

        # Add edges with attributes
        for rel in graph.relationships.values():
            edge_attrs = {}
            if hasattr(rel, 'kind') and rel.kind:
                edge_attrs['kind'] = rel.kind
            if hasattr(rel, 'weight') and rel.weight is not None:
                edge_attrs['weight'] = rel.weight
            if hasattr(rel, 'meta') and rel.meta:
                edge_attrs['meta'] = json.dumps(rel.meta)

            nx_graph.add_edge(str(rel.source_id), str(rel.target_id), **edge_attrs)

        return nx_graph

    @staticmethod
    def _json_serializer(obj: Any) -> Any:
        """Custom JSON serializer for special types."""
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, uuid.UUID):
            return str(obj)
        if isinstance(obj, Enum):
            return obj.value
        raise TypeError(f"Type {type(obj)} not serializable")


# Public API
__all__ = [
    "StorageFormat",
    "GraphMetadata",
    "SFMSerializationError",
    "SFMPersistenceError",
    "NodeSerializer",
    "SFMGraphSerializer",
    "SFMPersistenceManager",
]
