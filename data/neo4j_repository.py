"""
Neo4j-based implementation of SFMRepository for persistent graph storage.

This module provides a Neo4j backend for the SFM graph data, implementing
all the abstract methods defined in SFMRepository. It handles serialization
of complex Python types (UUID, datetime, enums) to Neo4j properties and
provides efficient graph operations using Cypher queries.
"""

import uuid
import json
from datetime import datetime
from typing import Optional, List, Type, Any, Dict, TYPE_CHECKING
from enum import Enum

try:
    from neo4j import GraphDatabase, Driver, ManagedTransaction
    from neo4j.exceptions import Neo4jError, ServiceUnavailable
    _neo4j_available = True
except ImportError:
    # Allow import without neo4j driver installed for testing
    GraphDatabase = None  # type: ignore
    Driver = None  # type: ignore
    ManagedTransaction = None  # type: ignore
    Neo4jError = Exception  # type: ignore
    ServiceUnavailable = Exception  # type: ignore
    _neo4j_available = False

from models import Node
from models.sfm_enums import RelationshipKind
from models.exceptions import (
    SFMValidationError,
    SFMNotFoundError,
    NodeCreationError,
    RelationshipValidationError,
)
from graph.sfm_graph import Relationship, SFMGraph
from data.repositories import SFMRepository


class Neo4jSerializationError(Exception):
    """Exception raised for serialization errors in Neo4j operations."""


class Neo4jConnectionError(Exception):
    """Exception raised for Neo4j connection errors."""


class Neo4jSFMRepository(SFMRepository):
    """
    Neo4j-based implementation of SFMRepository.

    This implementation stores SFM graph data in a Neo4j graph database,
    providing persistent storage with efficient graph queries.

    Node labels are derived directly from Python class names (e.g., Actor -> :Actor).
    Properties handle serialization of UUID, datetime, and enum fields.
    """

    def __init__(self, uri: str, username: str, password: str):
        """
        Initialize the Neo4j repository.

        Args:
            uri: Neo4j connection URI (e.g., "bolt://localhost:7687")
            username: Neo4j username
            password: Neo4j password

        Raises:
            Neo4jConnectionError: If Neo4j driver is not available or connection fails
        """
        if GraphDatabase is None:
            raise Neo4jConnectionError(
                "neo4j driver not installed. Install with: pip install neo4j"
            )

        try:
            self._driver: Driver = GraphDatabase.driver(uri, auth=(username, password))
            # Test connection
            with self._driver.session() as session:
                session.run("RETURN 1")
        except Exception as e:
            # Handle both Neo4j-specific errors and general exceptions
            if _neo4j_available and isinstance(e, (ServiceUnavailable, Neo4jError)):
                raise Neo4jConnectionError(f"Failed to connect to Neo4j at {uri}: {e}") from e
            raise Neo4jConnectionError(f"Neo4j initialization error: {e}") from e

    def close(self) -> None:
        """Close the Neo4j driver connection."""
        if self._driver:
            self._driver.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close connection."""
        self.close()

    @staticmethod
    def _serialize_value(value: Any) -> Any:
        """
        Serialize Python values to Neo4j-compatible types.

        Handles UUID, datetime, and enum serialization.
        """
        if value is None:
            return None
        elif isinstance(value, uuid.UUID):
            return str(value)
        elif isinstance(value, datetime):
            return value.isoformat()
        elif isinstance(value, Enum):
            return value.value
        elif isinstance(value, dict):
            return {k: Neo4jSFMRepository._serialize_value(v) for k, v in value.items()}
        elif isinstance(value, (list, tuple)):
            return [Neo4jSFMRepository._serialize_value(v) for v in value]
        else:
            return value

    @staticmethod
    def _deserialize_value(value: Any, target_type: Optional[type] = None) -> Any:
        """
        Deserialize Neo4j values back to Python types.

        Args:
            value: The value to deserialize
            target_type: Optional type hint for deserialization
        """
        if value is None:
            return None
        elif target_type == uuid.UUID and isinstance(value, str):
            return uuid.UUID(value)
        elif target_type == datetime and isinstance(value, str):
            return datetime.fromisoformat(value)
        else:
            return value

    @staticmethod
    def _node_to_properties(node: Node) -> Dict[str, Any]:
        """
        Convert a Node instance to Neo4j properties dictionary.

        Serializes all node attributes, handling complex types.
        """
        properties = {}

        for attr_name, attr_value in node.__dict__.items():
            if attr_name.startswith('_'):
                # Skip private attributes
                continue

            serialized = Neo4jSFMRepository._serialize_value(attr_value)
            properties[attr_name] = serialized

        # Store the Python class name for deserialization
        properties['_python_class'] = type(node).__name__

        return properties

    @staticmethod
    def _properties_to_node(properties: Dict[str, Any], node_class: Type[Node]) -> Node:
        """
        Reconstruct a Node instance from Neo4j properties.

        Args:
            properties: Dictionary of node properties from Neo4j
            node_class: The Python class to instantiate
        """
        # Remove internal properties
        props = {k: v for k, v in properties.items() if not k.startswith('_')}

        # Deserialize specific fields
        if 'id' in props:
            props['id'] = uuid.UUID(props['id'])
        if 'created_at' in props:
            props['created_at'] = datetime.fromisoformat(props['created_at'])
        if 'modified_at' in props and props['modified_at']:
            props['modified_at'] = datetime.fromisoformat(props['modified_at'])
        if 'previous_version_id' in props and props['previous_version_id']:
            props['previous_version_id'] = uuid.UUID(props['previous_version_id'])

        # Reconstruct meta dict if it was serialized as string
        if 'meta' in props and isinstance(props['meta'], str):
            try:
                props['meta'] = json.loads(props['meta'])
            except (json.JSONDecodeError, TypeError):
                pass

        try:
            return node_class(**props)
        except TypeError as e:
            raise Neo4jSerializationError(
                f"Failed to deserialize node of type {node_class.__name__}: {e}"
            ) from e

    def create_node(self, node: Node) -> Node:
        """
        Create a new node in Neo4j.

        Args:
            node: The Node instance to create

        Returns:
            The created node

        Raises:
            NodeCreationError: If a node with the same ID already exists
        """
        node_label = type(node).__name__
        properties = self._node_to_properties(node)

        with self._driver.session() as session:
            try:
                result = session.execute_write(
                    self._create_node_tx, node_label, properties, node.id
                )
                if result is None:
                    raise NodeCreationError(
                        f"Node with ID {node.id} already exists",
                        node_type=node_label,
                        node_id=node.id
                    )
                return node
            except Neo4jError as e:
                raise NodeCreationError(
                    f"Failed to create node: {e}",
                    node_type=node_label,
                    node_id=node.id
                ) from e

    @staticmethod
    def _create_node_tx(tx: ManagedTransaction, label: str, properties: Dict[str, Any],
                        node_id: uuid.UUID) -> Optional[Dict[str, Any]]:
        """ManagedTransaction function to create a node."""
        # Check if node already exists
        check_query = f"""
        MATCH (n:{label} {{id: $id}})
        RETURN n
        """
        existing = tx.run(check_query, id=str(node_id)).single()
        if existing:
            return None

        # Create the node
        create_query = f"""
        CREATE (n:{label} $properties)
        RETURN n
        """  # noqa: S608
        result = tx.run(create_query, properties=properties)
        record = result.single()
        return record[0] if record else None

    def read_node(self, node_id: uuid.UUID) -> Optional[Node]:
        """
        Read a node by its ID from Neo4j.

        Args:
            node_id: The UUID of the node to read

        Returns:
            The Node instance or None if not found
        """
        with self._driver.session() as session:
            result = session.execute_read(self._read_node_tx, node_id)
            return result

    @staticmethod
    def _read_node_tx(tx: ManagedTransaction, node_id: uuid.UUID) -> Optional[Node]:
        """ManagedTransaction function to read a node."""
        query = """
        MATCH (n {id: $id})
        RETURN n, labels(n) as labels
        """
        result = tx.run(query, id=str(node_id)).single()

        if not result:
            return None

        node_data = dict(result['n'])
        labels = result['labels']

        # Get the Python class name from properties or labels
        python_class = node_data.get('_python_class')
        if not python_class and labels:
            python_class = labels[0]

        if not python_class:
            raise Neo4jSerializationError("Cannot determine node type")

        # Import the node class dynamically
        try:
            import models
            node_class = getattr(models, python_class, Node)
            return Neo4jSFMRepository._properties_to_node(node_data, node_class)
        except AttributeError:
            # Fallback to generic Node
            return Neo4jSFMRepository._properties_to_node(node_data, Node)

    def update_node(self, node: Node) -> Node:
        """
        Update an existing node in Neo4j.

        Args:
            node: The Node instance to update

        Returns:
            The updated node

        Raises:
            SFMNotFoundError: If the node doesn't exist
        """
        node_label = type(node).__name__
        properties = self._node_to_properties(node)

        with self._driver.session() as session:
            try:
                result = session.execute_write(
                    self._update_node_tx, node_label, properties, node.id
                )
                if result is None:
                    raise SFMNotFoundError(
                        entity_type=node_label,
                        entity_id=node.id
                    )
                return node
            except Neo4jError as e:
                raise SFMValidationError(
                    f"Failed to update node: {e}",
                    field="node",
                    value=str(node.id)
                ) from e

    @staticmethod
    def _update_node_tx(tx: ManagedTransaction, label: str, properties: Dict[str, Any],
                        node_id: uuid.UUID) -> Optional[Dict[str, Any]]:
        """ManagedTransaction function to update a node."""
        query = f"""
        MATCH (n:{label} {{id: $id}})
        SET n = $properties
        RETURN n
        """  # noqa: S608
        result = tx.run(query, id=str(node_id), properties=properties)
        record = result.single()
        return record[0] if record else None

    def delete_node(self, node_id: uuid.UUID) -> bool:
        """
        Delete a node by its ID from Neo4j.

        Args:
            node_id: The UUID of the node to delete

        Returns:
            True if the node was deleted, False if not found
        """
        with self._driver.session() as session:
            return session.execute_write(self._delete_node_tx, node_id)

    @staticmethod
    def _delete_node_tx(tx: ManagedTransaction, node_id: uuid.UUID) -> bool:
        """ManagedTransaction function to delete a node and its relationships."""
        query = """
        MATCH (n {id: $id})
        DETACH DELETE n
        RETURN count(n) as deleted
        """
        result = tx.run(query, id=str(node_id)).single()
        return result['deleted'] > 0 if result else False

    def list_nodes(self, node_type: Optional[Type[Node]] = None) -> List[Node]:
        """
        List all nodes, optionally filtered by type.

        Args:
            node_type: Optional Python class to filter by

        Returns:
            List of Node instances
        """
        with self._driver.session() as session:
            return session.execute_read(self._list_nodes_tx, node_type)

    @staticmethod
    def _list_nodes_tx(tx: ManagedTransaction, node_type: Optional[Type[Node]] = None) -> List[Node]:
        """ManagedTransaction function to list nodes."""
        if node_type:
            label = node_type.__name__
            query = f"""
            MATCH (n:{label})
            RETURN n, labels(n) as labels
            """
        else:
            query = """
            MATCH (n)
            WHERE NOT n:_Neo4jInternal
            RETURN n, labels(n) as labels
            """

        results = tx.run(query)
        nodes = []

        for record in results:
            node_data = dict(record['n'])
            labels = record['labels']

            python_class = node_data.get('_python_class')
            if not python_class and labels:
                python_class = labels[0]

            if python_class:
                try:
                    import models
                    node_class = getattr(models, python_class, Node)
                    node = Neo4jSFMRepository._properties_to_node(node_data, node_class)
                    nodes.append(node)
                except (AttributeError, Neo4jSerializationError):
                    continue

        return nodes

    def create_relationship(self, rel: Relationship) -> Relationship:
        """
        Create a new relationship in Neo4j.

        Args:
            rel: The Relationship instance to create

        Returns:
            The created relationship

        Raises:
            RelationshipValidationError: If relationship already exists
            SFMNotFoundError: If source or target nodes don't exist
        """
        with self._driver.session() as session:
            try:
                result = session.execute_write(self._create_relationship_tx, rel)
                if result is None:
                    raise RelationshipValidationError(
                        "Failed to create relationship: source or target not found",
                        source_id=rel.source_id,
                        target_id=rel.target_id,
                        relationship_kind=rel.kind
                    )
                return rel
            except Neo4jError as e:
                raise RelationshipValidationError(
                    f"Failed to create relationship: {e}",
                    source_id=rel.source_id,
                    target_id=rel.target_id,
                    relationship_kind=rel.kind
                ) from e

    @staticmethod
    def _create_relationship_tx(tx: ManagedTransaction, rel: Relationship) -> Optional[Dict[str, Any]]:
        """ManagedTransaction function to create a relationship."""
        # Prepare properties
        properties: Dict[str, Any] = {
            'id': str(rel.id),
            'kind': rel.kind,
        }
        if rel.weight is not None:
            properties['weight'] = rel.weight
        if rel.meta:
            properties['meta'] = Neo4jSFMRepository._serialize_value(rel.meta)

        # Create relationship with dynamic type
        rel_type = rel.kind if rel.kind else "RELATED_TO"
        query = f"""
        MATCH (source {{id: $source_id}}), (target {{id: $target_id}})
        CREATE (source)-[r:{rel_type} $properties]->(target)
        RETURN r
        """  # noqa: S608

        result = tx.run(
            query,
            source_id=str(rel.source_id),
            target_id=str(rel.target_id),
            properties=properties
        )
        record = result.single()
        return record[0] if record else None

    def read_relationship(self, rel_id: uuid.UUID) -> Optional[Relationship]:
        """
        Read a relationship by its ID from Neo4j.

        Args:
            rel_id: The UUID of the relationship to read

        Returns:
            The Relationship instance or None if not found
        """
        with self._driver.session() as session:
            return session.execute_read(self._read_relationship_tx, rel_id)

    @staticmethod
    def _read_relationship_tx(tx: ManagedTransaction, rel_id: uuid.UUID) -> Optional[Relationship]:
        """ManagedTransaction function to read a relationship."""
        query = """
        MATCH ()-[r {id: $id}]->()
        RETURN r, startNode(r).id as source_id, endNode(r).id as target_id, type(r) as rel_type
        """
        result = tx.run(query, id=str(rel_id)).single()

        if not result:
            return None

        rel_data = dict(result['r'])

        return Relationship(
            id=uuid.UUID(rel_data['id']),
            source_id=uuid.UUID(result['source_id']),
            target_id=uuid.UUID(result['target_id']),
            kind=rel_data.get('kind', result['rel_type']),
            weight=rel_data.get('weight'),
            meta=rel_data.get('meta', {})
        )

    def update_relationship(self, rel: Relationship) -> Relationship:
        """
        Update an existing relationship in Neo4j.

        Args:
            rel: The Relationship instance to update

        Returns:
            The updated relationship

        Raises:
            SFMNotFoundError: If the relationship doesn't exist
        """
        with self._driver.session() as session:
            result = session.execute_write(self._update_relationship_tx, rel)
            if result is None:
                raise SFMNotFoundError(
                    entity_type="Relationship",
                    entity_id=rel.id
                )
            return rel

    @staticmethod
    def _update_relationship_tx(tx: ManagedTransaction, rel: Relationship) -> Optional[Dict[str, Any]]:
        """ManagedTransaction function to update a relationship."""
        properties: Dict[str, Any] = {
            'id': str(rel.id),
            'kind': rel.kind,
        }
        if rel.weight is not None:
            properties['weight'] = rel.weight
        if rel.meta:
            properties['meta'] = Neo4jSFMRepository._serialize_value(rel.meta)

        query = """
        MATCH ()-[r {id: $id}]->()
        SET r = $properties
        RETURN r
        """
        result = tx.run(query, id=str(rel.id), properties=properties)
        record = result.single()
        return record[0] if record else None

    def delete_relationship(self, rel_id: uuid.UUID) -> bool:
        """
        Delete a relationship by its ID from Neo4j.

        Args:
            rel_id: The UUID of the relationship to delete

        Returns:
            True if the relationship was deleted, False if not found
        """
        with self._driver.session() as session:
            return session.execute_write(self._delete_relationship_tx, rel_id)

    @staticmethod
    def _delete_relationship_tx(tx: ManagedTransaction, rel_id: uuid.UUID) -> bool:
        """ManagedTransaction function to delete a relationship."""
        query = """
        MATCH ()-[r {id: $id}]->()
        DELETE r
        RETURN count(r) as deleted
        """
        result = tx.run(query, id=str(rel_id)).single()
        return result['deleted'] > 0 if result else False

    def list_relationships(self, kind: Optional[RelationshipKind] = None) -> List[Relationship]:
        """
        List all relationships, optionally filtered by kind.

        Args:
            kind: Optional RelationshipKind to filter by

        Returns:
            List of Relationship instances
        """
        with self._driver.session() as session:
            return session.execute_read(self._list_relationships_tx, kind)

    @staticmethod
    def _list_relationships_tx(tx: ManagedTransaction, kind: Optional[RelationshipKind] = None) -> List[Relationship]:
        """ManagedTransaction function to list relationships."""
        if kind:
            query = """
            MATCH ()-[r]->()
            WHERE r.kind = $kind
            RETURN r, startNode(r).id as source_id, endNode(r).id as target_id, type(r) as rel_type
            """
            results = tx.run(query, kind=kind.value if hasattr(kind, 'value') else kind)
        else:
            query = """
            MATCH ()-[r]->()
            RETURN r, startNode(r).id as source_id, endNode(r).id as target_id, type(r) as rel_type
            """
            results = tx.run(query)

        relationships = []
        for record in results:
            rel_data = dict(record['r'])
            relationships.append(Relationship(
                id=uuid.UUID(rel_data['id']),
                source_id=uuid.UUID(record['source_id']),
                target_id=uuid.UUID(record['target_id']),
                kind=rel_data.get('kind', record['rel_type']),
                weight=rel_data.get('weight'),
                meta=rel_data.get('meta', {})
            ))

        return relationships

    def find_relationships(
        self,
        source_id: Optional[uuid.UUID] = None,
        target_id: Optional[uuid.UUID] = None,
        kind: Optional[RelationshipKind] = None,
    ) -> List[Relationship]:
        """
        Find relationships matching the specified criteria.

        Args:
            source_id: Optional source node ID filter
            target_id: Optional target node ID filter
            kind: Optional relationship kind filter

        Returns:
            List of matching Relationship instances
        """
        with self._driver.session() as session:
            return session.execute_read(
                self._find_relationships_tx, source_id, target_id, kind
            )

    @staticmethod
    def _find_relationships_tx(
        tx: ManagedTransaction,
        source_id: Optional[uuid.UUID] = None,
        target_id: Optional[uuid.UUID] = None,
        kind: Optional[RelationshipKind] = None,
    ) -> List[Relationship]:
        """ManagedTransaction function to find relationships."""
        conditions = []
        params: Dict[str, Any] = {}

        if source_id:
            conditions.append("startNode(r).id = $source_id")
            params['source_id'] = str(source_id)
        if target_id:
            conditions.append("endNode(r).id = $target_id")
            params['target_id'] = str(target_id)
        if kind:
            conditions.append("r.kind = $kind")
            params['kind'] = kind.value if hasattr(kind, 'value') else kind

        where_clause = " AND ".join(conditions) if conditions else "true"

        query = f"""
        MATCH ()-[r]->()
        WHERE {where_clause}
        RETURN r, startNode(r).id as source_id, endNode(r).id as target_id, type(r) as rel_type
        """

        results = tx.run(query, **params)

        relationships = []
        for record in results:
            rel_data = dict(record['r'])
            relationships.append(Relationship(
                id=uuid.UUID(rel_data['id']),
                source_id=uuid.UUID(record['source_id']),
                target_id=uuid.UUID(record['target_id']),
                kind=rel_data.get('kind', record['rel_type']),
                weight=rel_data.get('weight'),
                meta=rel_data.get('meta', {})
            ))

        return relationships

    def load_graph(self) -> SFMGraph:
        """
        Load the complete SFM graph from Neo4j.

        Returns:
            SFMGraph instance containing all nodes and relationships
        """
        graph = SFMGraph()

        # Load all nodes
        nodes = self.list_nodes()
        for node in nodes:
            graph.add_node(node)

        # Load all relationships
        relationships = self.list_relationships()
        for rel in relationships:
            graph.add_relationship(rel)

        return graph

    def save_graph(self, graph: SFMGraph) -> None:
        """
        Save the complete SFM graph to Neo4j.

        This performs a batch save operation, clearing existing data
        and creating all nodes and relationships from the graph.

        Args:
            graph: The SFMGraph to save
        """
        # Clear existing data
        self.clear()

        # Create all nodes in batch
        for node in graph:
            try:
                self.create_node(node)
            except NodeCreationError:
                # Node already exists, update it
                self.update_node(node)

        # Create all relationships in batch
        for rel in graph.relationships.values():
            try:
                self.create_relationship(rel)
            except RelationshipValidationError:
                # Relationship might already exist, skip
                pass

    def clear(self) -> None:
        """
        Clear all SFM data from the Neo4j database.

        WARNING: This deletes all nodes and relationships.
        """
        with self._driver.session() as session:
            session.execute_write(self._clear_tx)

    @staticmethod
    def _clear_tx(tx: ManagedTransaction) -> None:
        """ManagedTransaction function to clear all data."""
        query = """
        MATCH (n)
        DETACH DELETE n
        """
        tx.run(query)

    def execute_query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Execute a raw Cypher query and return results.

        This method allows direct Cypher queries for advanced Neo4j operations
        that aren't covered by the standard repository interface.

        Args:
            query: Cypher query string
            parameters: Optional dictionary of query parameters

        Returns:
            List of result records as dictionaries

        Example:
            >>> results = repo.execute_query(
            ...     "MATCH (n:PolicyInstrument) RETURN n.label as label, n.instrument_type as type"
            ... )
            >>> for record in results:
            ...     print(f"{record['label']}: {record['type']}")
        """
        with self._driver.session() as session:
            return session.execute_read(
                self._execute_query_tx, query, parameters or {}
            )

    @staticmethod
    def _execute_query_tx(
        tx: ManagedTransaction, query: str, parameters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """ManagedTransaction function to execute a query."""
        result = tx.run(query, parameters)
        return [dict(record) for record in result]
