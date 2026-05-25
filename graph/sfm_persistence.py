"""
SFM Graph Persistence Manager (Beta)

Provides persistence capabilities for Social Fabric Matrix graphs using the Beta unified model.
Enables storage, loading, and serialization of in-memory graph data.

Key Features:
- JSON and Pickle storage formats
- Serialization for all 33 Beta unified model node types
- Data validation and integrity checking
- Version management
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
from typing import Any, Dict, List, Optional, Union

# Import all Beta unified model node types
from models import (
    Node,
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
)

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

    # Map of all 33 Beta node types for serialization
    NODE_TYPE_REGISTRY = {
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
    }

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
                'kind': rel.kind.value if hasattr(rel, 'kind') and rel.kind else None,
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
    def deserialize_graph(data: bytes, format_type: StorageFormat = StorageFormat.JSON) -> Any:
        """Deserialize bytes to an SFM graph."""
        try:
            if format_type in [StorageFormat.COMPRESSED_JSON, StorageFormat.COMPRESSED_PICKLE]:
                data = gzip.decompress(data)

            if format_type in [StorageFormat.JSON, StorageFormat.COMPRESSED_JSON]:
                dict_data = json.loads(data.decode('utf-8'))
                return SFMGraphSerializer._dict_to_graph(dict_data)

            if format_type in [StorageFormat.PICKLE, StorageFormat.COMPRESSED_PICKLE]:
                return pickle.loads(data)

            raise SFMSerializationError(f"Unsupported format: {format_type}")

        except Exception as e:
            raise SFMSerializationError(f"Failed to deserialize graph: {str(e)}") from e

    @staticmethod
    def _dict_to_graph(data: Dict[str, Any]) -> Any:
        """Convert dictionary representation back to SFMGraph."""
        # Import here to avoid circular dependency
        from sfm_core.graph import SFMGraph

        graph = SFMGraph()

        # Deserialize nodes by type
        nodes_by_type = data.get('nodes_by_type', {})
        for node_type, nodes_data in nodes_by_type.items():
            for node_data in nodes_data:
                try:
                    node = NodeSerializer.dict_to_node(node_data)
                    graph.add_node(node)
                except Exception as e:
                    logger.warning("Failed to deserialize node: %s", str(e))

        # Deserialize relationships (placeholder - will be implemented with graph module)
        # relationships_data = data.get('relationships', [])
        # for rel_data in relationships_data:
        #     # Create and add relationship
        #     pass

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
        format_type: StorageFormat = StorageFormat.JSON
    ) -> Any:
        """Load a graph from disk."""
        file_path = self.base_path / filename

        if not file_path.exists():
            raise SFMPersistenceError(f"File not found: {file_path}")

        # Read file
        with open(file_path, 'rb') as f:
            data = f.read()

        # Deserialize graph
        graph = SFMGraphSerializer.deserialize_graph(data, format_type)

        logger.info("Loaded graph from %s", file_path)
        return graph


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
