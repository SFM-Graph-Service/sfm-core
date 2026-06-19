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
from typing import Any, Dict, List, Optional, Type

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
    NODE_TYPE_REGISTRY = {
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
    def get_node_class(node_type_name: str) -> Optional[Type[Node]]:
        """
        Get node class by type name.

        Args:
            node_type_name: Name of node type (e.g., "InstitutionalStructure")

        Returns:
            Node class or None if not found
        """
        return NodeSerializer.NODE_TYPE_REGISTRY.get(node_type_name)

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
                # Handle special types
                if isinstance(value, uuid.UUID):
                    result[key] = str(value)
                elif isinstance(value, datetime):
                    result[key] = value.isoformat()
                elif isinstance(value, Enum):
                    result[key] = value.value
                elif isinstance(value, (list, dict, str, int, float, bool, type(None))):
                    result[key] = value
                else:
                    # Try to convert to string for other types
                    try:
                        result[key] = str(value)
                    except Exception:
                        logger.warning("Could not serialize attribute %s of node %s", key, node.id)

        return result

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

        # Create node instance
        try:
            # Remove 'type' from data as it's not a constructor parameter
            node_data = {k: v for k, v in data.items() if k != 'type'}
            node = node_class(**node_data)
            return node
        except Exception as e:
            raise SFMSerializationError(
                f"Failed to create node of type {node_type_name}: {str(e)}"
            ) from e


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

        # Serialize relationships
        relationships = []
        for rel in graph.relationships.values():
            relationships.append({
                'id': str(rel.id),
                'source_id': str(rel.source_id),
                'target_id': str(rel.target_id),
                'kind': rel.kind if hasattr(rel, 'kind') else None,
            })

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

        # Deserialize relationships
        from graph.sfm_graph import Relationship
        relationships_data = data.get('relationships', [])
        for rel_data in relationships_data:
            try:
                rel = Relationship(
                    id=uuid.UUID(rel_data['id']),
                    source_id=uuid.UUID(rel_data['source_id']),
                    target_id=uuid.UUID(rel_data['target_id']),
                    kind=rel_data.get('kind', '')
                )
                graph.add_relationship(rel)
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
                snapshot["relationships"].append({
                    'id': str(rel.id),
                    'source_id': str(rel.source_id),
                    'target_id': str(rel.target_id),
                    'kind': rel.kind if hasattr(rel, 'kind') else None,
                    'weight': rel.weight if hasattr(rel, 'weight') else None,
                    'meta': rel.meta if hasattr(rel, 'meta') else {}
                })

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
            from graph.sfm_graph import SFMGraph, Relationship

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
                    rel = Relationship(
                        id=uuid.UUID(rel_data['id']),
                        source_id=uuid.UUID(rel_data['source_id']),
                        target_id=uuid.UUID(rel_data['target_id']),
                        kind=rel_data.get('kind', ''),
                        weight=rel_data.get('weight'),
                        meta=rel_data.get('meta', {})
                    )
                    graph.add_relationship(rel)
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
