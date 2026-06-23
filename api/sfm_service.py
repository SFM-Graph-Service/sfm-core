"""
SFM Service - Unified Facade for Social Fabric Matrix Framework (Beta)

This module provides a simplified interface to the SFM Core Beta unified model.
It acts as a facade for common SFM operations and integrates the Phase 2 query engine.

Key Features:
- Unified interface for creating and managing SFM nodes
- Built-in repository management
- Integrated query engine for advanced network analysis
- Phase 2 query methods: ceremonial analysis, circular causation, holarchy, conflicts
"""

import logging
import uuid
from typing import Dict, List, Optional, Any, Type, TypeVar, Union
from dataclasses import dataclass
from pathlib import Path

from models import Node
from models.exceptions import (
    SFMError,
    SFMValidationError,
    SFMNotFoundError,
    NodeCreationError,
)
from data.repositories import (
    SFMRepository,
    SFMRepositoryFactory,
)
from graph.sfm_graph import Relationship

# Setup logging
logger = logging.getLogger(__name__)

T = TypeVar("T", bound=Node)


@dataclass
class ServiceHealth:
    """Service health status"""
    status: str
    node_count: int
    relationship_count: int


@dataclass
class GraphStatistics:
    """Graph statistics"""
    total_nodes: int
    total_relationships: int
    node_types: Dict[str, int]


class SFMServiceConfig:
    """Configuration for SFM Service"""

    def __init__(
        self,
        storage_type: str = "networkx",
        graph_size_limit: int = 10000,
        neo4j_uri: Optional[str] = None,
        neo4j_username: Optional[str] = None,
        neo4j_password: Optional[str] = None,
    ):
        self.storage_type = storage_type
        self.graph_size_limit = graph_size_limit
        self.neo4j_uri = neo4j_uri
        self.neo4j_username = neo4j_username
        self.neo4j_password = neo4j_password


class SFMService:
    """
    Main service facade for SFM Core Beta operations.
    Provides high-level interface to Beta unified model and Phase 2 query engine.
    """

    def __init__(self, config: Optional[SFMServiceConfig] = None):
        """
        Initialize the SFM Service.

        Args:
            config: Service configuration. If None, uses default settings.
        """
        self.config = config or SFMServiceConfig()

        # Initialize repository with Neo4j parameters if provided
        self._repository: SFMRepository = SFMRepositoryFactory.create_repository(
            storage_type=self.config.storage_type,
            neo4j_uri=self.config.neo4j_uri,
            neo4j_username=self.config.neo4j_username,
            neo4j_password=self.config.neo4j_password,
        )

        # Query engine will be initialized in Phase 2 Step 2
        self._query_engine: Optional[Any] = None

        logger.info("SFM Service initialized with storage type: %s", self.config.storage_type)

    def initialize_query_engine(self):
        """
        Initialize the query engine from the current graph state.

        This must be called after nodes/relationships are added to enable
        query methods like ceremonial analysis, conflict detection, etc.
        """
        from graph.sfm_query import NetworkXSFMQueryEngine

        # Load the complete SFMGraph from the repository
        graph = self._repository.load_graph()

        # Create the query engine
        self._query_engine = NetworkXSFMQueryEngine(graph)
        logger.info("Query engine initialized with %d nodes", len(list(graph)))

    @property
    def repository(self) -> SFMRepository:
        """Get the underlying repository"""
        return self._repository

    @property
    def query_engine(self) -> Any:
        """
        Get the query engine.
        Phase 2 Step 2 will create the actual query engine.
        """
        if self._query_engine is None:
            # Placeholder - will be replaced in Phase 2 Step 2
            logger.warning("Query engine not yet initialized")
        return self._query_engine

    def get_health(self) -> ServiceHealth:
        """Get service health status"""
        nodes = self._repository.list_nodes()
        relationships = self._repository.list_relationships()

        return ServiceHealth(
            status="healthy",
            node_count=len(nodes),
            relationship_count=len(relationships),
        )

    def create_node(self, node: Node) -> Node:
        """
        Create a new node in the system.

        Args:
            node: The node to create

        Returns:
            The created node

        Raises:
            NodeCreationError: If node creation fails
            SFMValidationError: If validation fails
        """
        try:
            created_node = self._repository.create_node(node)
            logger.info("Created node %s of type %s", created_node.id, type(created_node).__name__)
            return created_node
        except Exception as e:
            logger.error("Failed to create node: %s", str(e))
            raise

    def get_node(self, node_id: uuid.UUID) -> Optional[Node]:
        """
        Get a node by its ID.

        Args:
            node_id: The ID of the node to retrieve

        Returns:
            The node if found, None otherwise
        """
        return self._repository.read_node(node_id)

    def update_node(self, node: Node) -> Node:
        """
        Update an existing node.

        Args:
            node: The node to update

        Returns:
            The updated node

        Raises:
            SFMNotFoundError: If node doesn't exist
        """
        return self._repository.update_node(node)

    def delete_node(self, node_id: uuid.UUID) -> bool:
        """
        Delete a node by its ID.

        Args:
            node_id: The ID of the node to delete

        Returns:
            True if deleted, False if not found
        """
        return self._repository.delete_node(node_id)

    def list_nodes(self, node_type: Optional[Type[Node]] = None) -> List[Node]:
        """
        List all nodes, optionally filtered by type.

        Args:
            node_type: Optional node type to filter by

        Returns:
            List of nodes
        """
        return self._repository.list_nodes(node_type)

    # Relationship CRUD operations

    def create_relationship(self, relationship: Relationship) -> Relationship:
        """
        Create a new relationship in the graph.

        Args:
            relationship: Relationship object to create

        Returns:
            Created relationship with ID

        Raises:
            SFMNotFoundError: If source or target node doesn't exist
            SFMValidationError: If relationship validation fails
        """
        created = self._repository.create_relationship(relationship)
        logger.info("Created relationship: %s -> %s (%s)", relationship.source_id, relationship.target_id, relationship.kind)
        return created

    def create_relationships_bulk(self, relationships: List[Relationship]) -> List[Relationship]:
        """
        Create multiple relationships in bulk for performance.

        This method bypasses per-relationship duplicate checking by building
        an ID set upfront, reducing O(n²) to O(n) complexity for large batches.

        Recommended for:
        - Scenario building with 100+ relationships
        - Data imports from external sources
        - Batch operations where IDs are known to be unique

        Args:
            relationships: List of relationship objects to create

        Returns:
            List of created relationships

        Raises:
            SFMNotFoundError: If any source or target node doesn't exist
            SFMValidationError: If any relationship ID is duplicate

        Example:
            >>> rels = [
            ...     Relationship(source_id=n1, target_id=n2, kind="influences", weight=0.8),
            ...     Relationship(source_id=n2, target_id=n3, kind="enables", weight=0.9),
            ... ]
            >>> created = service.create_relationships_bulk(rels)
            >>> print(f"Created {len(created)} relationships")
        """
        created = self._repository.create_relationships_bulk(relationships)
        logger.info("Bulk created %d relationships", len(created))
        return created

    def get_relationship(self, relationship_id: uuid.UUID) -> Optional[Relationship]:
        """
        Retrieve a relationship by ID.

        Args:
            relationship_id: UUID of the relationship

        Returns:
            Relationship object or None if not found
        """
        return self._repository.read_relationship(relationship_id)

    def update_relationship(self, relationship: Relationship) -> Relationship:
        """
        Update an existing relationship.

        Args:
            relationship: Relationship object with updated data

        Returns:
            Updated relationship

        Raises:
            SFMNotFoundError: If relationship doesn't exist
        """
        updated = self._repository.update_relationship(relationship)
        logger.info("Updated relationship: %s", relationship.id)
        return updated

    def delete_relationship(self, relationship_id: uuid.UUID) -> bool:
        """
        Delete a relationship by ID.

        Args:
            relationship_id: UUID of relationship to delete

        Returns:
            True if deleted, False if not found
        """
        success = self._repository.delete_relationship(relationship_id)
        if success:
            logger.info("Deleted relationship: %s", relationship_id)
        return success

    def list_relationships(self, kind: Optional[str] = None) -> List[Relationship]:
        """
        List all relationships, optionally filtered by kind.

        Args:
            kind: Optional relationship kind string to filter by

        Returns:
            List of relationships
        """
        # Get all relationships and filter by string kind if specified
        all_relationships = self._repository.list_relationships()
        if kind:
            return [r for r in all_relationships if r.kind == kind]
        return all_relationships

    def find_relationships(
        self,
        source_id: Optional[uuid.UUID] = None,
        target_id: Optional[uuid.UUID] = None,
        kind: Optional[str] = None
    ) -> List[Relationship]:
        """
        Find relationships matching the specified criteria.

        Args:
            source_id: Filter by source node ID
            target_id: Filter by target node ID
            kind: Filter by relationship kind string

        Returns:
            List of matching relationships
        """
        # Get relationships filtered by node IDs
        relationships = self._repository.find_relationships(source_id, target_id, None)

        # Further filter by string kind if specified
        if kind:
            relationships = [r for r in relationships if r.kind == kind]

        return relationships

    # ─── CONDITIONAL RELATIONSHIP HELPERS (Gap 5) ───

    def create_conditional_relationship(
        self,
        source_id: uuid.UUID,
        target_id: uuid.UUID,
        kind: str,
        weight: float,
        condition_node_id: uuid.UUID,
        condition_type: str = "necessary_but_not_sufficient",
        meta: Optional[Dict[str, Any]] = None
    ) -> Relationship:
        """
        Create relationship with conditional dependency.

        Args:
            source_id: Source node UUID
            target_id: Target node UUID
            kind: Relationship kind (e.g., "depends_on", "enables")
            weight: Relationship weight (0-1)
            condition_node_id: UUID of condition node that must be satisfied
            condition_type: "necessary", "sufficient", "necessary_and_sufficient",
                           "necessary_but_not_sufficient"
            meta: Additional metadata

        Returns:
            Created conditional relationship

        Example:
            # "Catalytic converter adoption depends on auto standards IF unleaded fuel available"
            create_conditional_relationship(
                source_id=catalytic_converter.id,
                target_id=auto_standards.id,
                kind="depends_on",
                weight=0.8,
                condition_node_id=unleaded_fuel.id,
                condition_type="necessary_but_not_sufficient"
            )
        """
        rel_meta = meta or {}
        rel_meta["conditional"] = {
            "condition_node": str(condition_node_id),
            "condition_type": condition_type,
            "logic": "depends_on_if"
        }

        relationship = Relationship(
            source_id=source_id,
            target_id=target_id,
            kind=f"{kind}_if",  # e.g., "enables_if", "depends_on_if"
            weight=weight,
            meta=rel_meta
        )

        return self.create_relationship(relationship)

    def create_compound_dependency(
        self,
        dependent_node_id: uuid.UUID,
        required_nodes: List[uuid.UUID],
        logic: str = "AND",  # "AND", "OR", "XOR"
        weight: float = 1.0
    ) -> List[Relationship]:
        """
        Create multiple relationships representing AND/OR logic.

        Args:
            dependent_node_id: Node that depends on others
            required_nodes: List of node UUIDs that are required
            logic: "AND" (all required), "OR" (any required), "XOR" (exactly one)
            weight: Weight for all relationships

        Returns:
            List of created relationships

        Example:
            # EPA enforcement depends on (Congressional funding AND Public support)
            create_compound_dependency(
                dependent_node_id=epa_enforcement.id,
                required_nodes=[congressional_funding.id, public_support.id],
                logic="AND",
                weight=0.9
            )
        """
        relationships = []

        for req_node_id in required_nodes:
            rel_meta = {
                "compound_dependency": {
                    "logic": logic,
                    "group": str(dependent_node_id),
                    "total_required": len(required_nodes)
                }
            }

            relationship = Relationship(
                source_id=dependent_node_id,
                target_id=req_node_id,
                kind=f"depends_on_{logic.lower()}",
                weight=weight,
                meta=rel_meta
            )

            created = self.create_relationship(relationship)
            relationships.append(created)

        return relationships

    # ─── GEOGRAPHIC HELPERS (Gap 6) ───

    def create_node_with_geography(
        self,
        label: str,
        description: str,
        geographic_scope: str,  # "federal", "state", "local", "regional"
        state: Optional[str] = None,
        jurisdiction: Optional[str] = None,
        meta: Optional[Dict[str, Any]] = None
    ) -> Node:
        """
        Create node with geographic metadata.

        Args:
            label: Node label
            description: Node description
            geographic_scope: "federal", "state", "local", "regional"
            state: State name (e.g., "California", "TX")
            jurisdiction: Specific jurisdiction name
            meta: Additional metadata

        Returns:
            Created node with geographic metadata

        Example:
            # Create California-specific air quality standard
            create_node_with_geography(
                label="California Air Quality Standards",
                description="CARB emission standards stricter than federal",
                geographic_scope="state",
                state="California",
                jurisdiction="CARB"
            )
        """
        node_meta = meta or {}
        node_meta["geography"] = {
            "scope": geographic_scope,
            "state": state,
            "jurisdiction": jurisdiction
        }

        # Import Node here to avoid circular dependency
        from models import Node

        node = Node(
            label=label,
            description=description,
            meta=node_meta
        )

        return self.create_node(node)

    def get_statistics(self) -> GraphStatistics:
        """
        Get graph statistics.

        Returns:
            GraphStatistics object with node and relationship counts
        """
        nodes = self._repository.list_nodes()
        relationships = self._repository.list_relationships()

        # Count nodes by type
        node_types: Dict[str, int] = {}
        for node in nodes:
            node_type = type(node).__name__
            node_types[node_type] = node_types.get(node_type, 0) + 1

        return GraphStatistics(
            total_nodes=len(nodes),
            total_relationships=len(relationships),
            node_types=node_types,
        )

    def clear_all_data(self) -> Dict[str, Any]:
        """
        Clear all data from the repository.

        Returns:
            Dictionary with operation status
        """
        self._repository.clear()
        logger.info("Cleared all data from repository")
        return {"status": "success", "message": "All data cleared"}

    # ========================================================================
    # Phase 2 Query Methods - Wrapping Beta Query Engine
    # ========================================================================

    def get_ceremonial_analysis(self, threshold: float = 0.5) -> dict:
        """
        Analyze ceremonial vs instrumental behaviors in the system.

        Args:
            threshold: Ceremonial threshold (0.0-1.0)

        Returns:
            Dictionary containing:
                - ceremonial_nodes: List of ceremonially-oriented nodes
                - instrumental_nodes: List of instrumentally-oriented nodes
                - ceremonial_ratio: Ratio of ceremonial to total
                - threshold: The threshold used

        Raises:
            SFMValidationError: If threshold is invalid
        """
        if not 0.0 <= threshold <= 1.0:
            raise SFMValidationError(
                "Threshold must be between 0.0 and 1.0",
                field="threshold",
                value=threshold
            )

        if self.query_engine is None:
            logger.warning("Query engine not initialized, returning empty analysis")
            return {
                "ceremonial_nodes": [],
                "instrumental_nodes": [],
                "ceremonial_ratio": 0.0,
                "threshold": threshold,
            }

        # Call query engine method
        logger.info("Performing ceremonial analysis with threshold %.2f", threshold)
        results = self.query_engine.query_ceremonial_vs_instrumental(threshold=threshold)

        # Convert Node objects to dict summaries for API response
        ceremonial_nodes = [{
            "id": node.id,
            "label": node.label,
            "node_type": type(node).__name__
        } for node in results.get("ceremonial", [])]

        instrumental_nodes = [{
            "id": node.id,
            "label": node.label,
            "node_type": type(node).__name__
        } for node in results.get("instrumental", [])]

        # Calculate ratio
        total_classified = len(ceremonial_nodes) + len(instrumental_nodes)
        ceremonial_ratio = len(ceremonial_nodes) / total_classified if total_classified > 0 else 0.0

        return {
            "ceremonial_nodes": ceremonial_nodes,
            "instrumental_nodes": instrumental_nodes,
            "ceremonial_ratio": ceremonial_ratio,
            "threshold": threshold,
        }

    def get_circular_causation(self, source_id: uuid.UUID) -> list:
        """
        Find circular causation paths starting from a source node.

        Traces feedback loops and cumulative causation sequences.

        Args:
            source_id: Starting node UUID

        Returns:
            List of cycles, each cycle is a list of dicts with node info

        Raises:
            SFMNotFoundError: If source node doesn't exist
        """
        try:
            # Verify source node exists first (before checking query engine)
            source_node = self.get_node(source_id)
            if source_node is None:
                raise SFMNotFoundError(entity_type="Node", entity_id=source_id)

            # Check if query engine is available
            if self.query_engine is None:
                logger.warning("Query engine not initialized, returning empty cycles")
                return []

            # Call query engine method
            logger.info("Finding circular causation from node %s", source_id)
            paths = self.query_engine.query_circular_causation_paths(source_id, max_depth=5)

            # Convert Node objects to dicts for API response
            cycles = []
            for path in paths:
                nodes = [{
                    "id": str(node.id),
                    "label": node.label,
                    "type": type(node).__name__
                } for node in path]
                # Wrap in a dict with "nodes" key for schema compatibility
                cycles.append({"nodes": nodes})

            logger.info("Found %d circular causation paths", len(cycles))
            return cycles

        except SFMNotFoundError:
            raise
        except Exception as e:
            logger.error("Error finding circular causation: %s", e, exc_info=True)
            return []

    def get_holarchy(self, institution_id: uuid.UUID) -> dict:
        """
        Get institutional holarchy (nested hierarchy) for an institution.

        Args:
            institution_id: UUID of the institution node

        Returns:
            Dictionary containing:
                - institution_id: The root institution UUID
                - layers: List of holarchy layers from top to bottom, each with
                  ``level`` (str) and ``nodes`` (list of node dicts)
                - relationships: Parent-child relationships (reserved for future)
                - depth: Number of populated holarchy levels
                - total_institutions: Total node count across all levels

        Raises:
            SFMNotFoundError: If institution doesn't exist
        """
        # Verify institution exists
        institution_node = self.get_node(institution_id)
        if institution_node is None:
            raise SFMNotFoundError(entity_type="Node", entity_id=institution_id)

        if self.query_engine is None:
            logger.warning("Query engine not initialized, returning empty holarchy")
            return {
                "institution_id": str(institution_id),
                "layers": [],
                "relationships": [],
                "depth": 0,
            }

        # Call the real query engine implementation
        logger.info("Building holarchy for institution %s", institution_id)
        levels: Dict[str, List[Node]] = self.query_engine.query_holarchy_levels(institution_id)

        # Convert Node objects to serialisable dicts and build layers list
        layers = []
        total_institutions = 0
        for level_name, nodes in levels.items():
            if nodes:
                layer = {
                    "level": level_name,
                    "nodes": [
                        {"id": str(n.id), "label": n.label, "type": type(n).__name__}
                        for n in nodes
                    ],
                }
                layers.append(layer)
                total_institutions += len(nodes)

        # Depth = number of non-empty levels
        depth = len(layers)

        return {
            "institution_id": str(institution_id),
            "layers": layers,
            "relationships": [],
            "depth": depth,
            "total_institutions": total_institutions,
        }

    def get_conflicts(self) -> list:
        """
        Detect value conflicts in the system.

        Returns:
            List of detected conflicts, where each conflict is:
                - conflict_type: Type of conflict (value, resource, institutional)
                - nodes: List of node IDs involved
                - severity: Conflict severity (0.0-1.0)
                - description: Human-readable description
        """
        if self.query_engine is None:
            logger.warning("Query engine not initialized, returning empty conflicts")
            return []

        # Call query engine method
        logger.info("Detecting system conflicts")
        conflicts = self.query_engine.detect_conflicts()
        return list(conflicts)

    # ========================================================================
    # Phase 3 Evaluation Methods - Analysis & Assessment
    # ========================================================================

    def evaluate_digraph(
        self, institutions: List[uuid.UUID], analyze_sequences: bool = True
    ) -> Dict[str, Any]:
        """
        Perform digraph analysis on institutional dependencies.

        Args:
            institutions: List of institution IDs to analyze
            analyze_sequences: Whether to analyze propagation sequences

        Returns:
            Dictionary containing:
                - dependency_matrix: Institution dependency relationships
                - cycles: Detected circular dependencies
                - critical_institutions: High-dependency nodes
                - leverage_points: High-influence nodes
                - stability_score: System stability measure
                - propagation_analysis: Optional sequence analysis results

        Raises:
            SFMValidationError: If institutions list is invalid
        """
        from models.complex_analysis import DigraphAnalysis

        if not institutions:
            raise SFMValidationError(
                "At least one institution required for digraph analysis",
                field="institutions",
                value=institutions,
            )

        analysis = DigraphAnalysis(
            label="Digraph Analysis",
            analyzed_institutions=institutions,
        )

        result: Dict[str, Any] = {
            "dependency_matrix": analysis.dependency_matrix,
            "cycles": analysis.cycle_detection,
            "critical_institutions": analysis.critical_institutions,
            "leverage_points": analysis.leverage_points,
            "stability_score": analysis.stability_score,
            "complexity_measure": analysis.complexity_measure,
        }

        if analyze_sequences:
            critical_seqs = analysis.identify_critical_sequences()
            patterns = analysis.detect_sequence_patterns()
            stability = analysis.assess_sequence_stability()

            result["propagation_analysis"] = {
                "critical_sequences": critical_seqs,
                "sequence_patterns": patterns,
                "sequence_stability": stability,
            }

        logger.info("Completed digraph analysis for %d institutions", len(institutions))
        return result

    def evaluate_circular_causation(
        self, process_id: uuid.UUID
    ) -> Dict[str, Any]:
        """
        Analyze circular causation process dynamics.

        Args:
            process_id: ID of CircularCausationProcess to evaluate

        Returns:
            Dictionary containing process dynamics analysis

        Raises:
            SFMNotFoundError: If process doesn't exist
        """
        from models.complex_analysis import CircularCausationProcess

        process = self.get_node(process_id)
        if not isinstance(process, CircularCausationProcess):
            raise SFMNotFoundError(
                entity_type="CircularCausationProcess", entity_id=process_id
            )

        dynamics = process.analyze_causation_dynamics()
        logger.info("Evaluated circular causation for process %s", process_id)
        return dynamics

    def evaluate_conflict_detection(
        self, system_id: uuid.UUID
    ) -> Dict[str, Any]:
        """
        Detect and analyze system conflicts.

        Args:
            system_id: ID of system to analyze for conflicts

        Returns:
            Dictionary containing comprehensive conflict report

        Raises:
            SFMNotFoundError: If system doesn't exist
        """
        from models.complex_analysis import ConflictDetection

        system = self.get_node(system_id)
        if not isinstance(system, ConflictDetection):
            raise SFMNotFoundError(
                entity_type="ConflictDetection", entity_id=system_id
            )

        # Generate comprehensive conflict report
        report = system.generate_conflict_report()
        priority_analysis = system.assess_conflict_priority()

        result = {
            "conflict_report": report,
            "priority_analysis": priority_analysis,
            "total_conflicts": len(system.direct_conflicts) + len(system.indirect_conflicts),
        }

        logger.info("Evaluated conflicts in system %s", system_id)
        return result

    def evaluate_cross_impact(
        self, cell_id: uuid.UUID
    ) -> Dict[str, Any]:
        """
        Analyze cross-impact effects of a matrix cell change.

        Args:
            cell_id: ID of matrix cell to analyze

        Returns:
            Dictionary containing cross-impact analysis results

        Raises:
            SFMNotFoundError: If cell doesn't exist
        """
        from models.network_analysis import CrossImpactAnalysis

        cell = self.get_node(cell_id)
        if not isinstance(cell, CrossImpactAnalysis):
            raise SFMNotFoundError(
                entity_type="CrossImpactAnalysis", entity_id=cell_id
            )

        result = {
            "primary_cell_id": str(cell.primary_cell_id),
            "impacted_cells": cell.impacted_cells,
            "impact_type": str(cell.impact_type),
            "impact_mechanism": cell.impact_mechanism,
            "time_delay": cell.time_delay,
            "confidence_level": cell.confidence_level,
            "mitigation_strategies": cell.mitigation_strategies,
            "amplification_strategies": cell.amplification_strategies,
        }

        logger.info("Evaluated cross-impact for cell %s", cell_id)
        return result

    def evaluate_delivery_performance(
        self, relationship_id: uuid.UUID
    ) -> Dict[str, Any]:
        """
        Assess delivery relationship performance.

        Args:
            relationship_id: ID of DeliveryRelationship to evaluate

        Returns:
            Dictionary containing performance assessment

        Raises:
            SFMNotFoundError: If relationship doesn't exist
        """
        from models.network_analysis import DeliveryRelationship

        relationship = self.get_node(relationship_id)
        if not isinstance(relationship, DeliveryRelationship):
            raise SFMNotFoundError(
                entity_type="DeliveryRelationship", entity_id=relationship_id
            )

        performance = relationship.assess_delivery_performance()
        logger.info("Evaluated delivery performance for relationship %s", relationship_id)
        return performance

    def evaluate_network_performance(
        self, network_id: uuid.UUID
    ) -> Dict[str, Any]:
        """
        Analyze delivery network performance and health.

        Args:
            network_id: ID of MatrixDeliveryNetwork to evaluate

        Returns:
            Dictionary containing network analysis

        Raises:
            SFMNotFoundError: If network doesn't exist
        """
        from models.network_analysis import MatrixDeliveryNetwork

        network = self.get_node(network_id)
        if not isinstance(network, MatrixDeliveryNetwork):
            raise SFMNotFoundError(
                entity_type="MatrixDeliveryNetwork", entity_id=network_id
            )

        analysis = network.analyze_network_performance()
        logger.info("Evaluated network performance for %s", network_id)
        return analysis

    def evaluate_path_dependency(
        self, institution_id: uuid.UUID
    ) -> Dict[str, Any]:
        """
        Analyze path-dependent institutional development.

        Args:
            institution_id: ID of institution to analyze

        Returns:
            Dictionary containing path dependency analysis

        Raises:
            SFMNotFoundError: If institution doesn't exist
        """
        from models.institutional_analysis import PathDependencyAnalysis

        analysis_node = self.get_node(institution_id)
        if not isinstance(analysis_node, PathDependencyAnalysis):
            raise SFMNotFoundError(
                entity_type="PathDependencyAnalysis", entity_id=institution_id
            )

        result = {
            "analyzed_institution_id": str(analysis_node.analyzed_institution_id),
            "dependency_strength": str(analysis_node.dependency_strength),
            "critical_junctures": analysis_node.critical_junctures,
            "lock_in_mechanisms": analysis_node.lock_in_mechanisms,
            "switching_costs": analysis_node.switching_costs,
            "alternative_paths": analysis_node.alternative_paths,
            "intervention_points": analysis_node.intervention_points,
            "path_efficiency": analysis_node.path_efficiency,
            "exit_barriers": analysis_node.exit_barriers,
            "network_effects": analysis_node.network_effects,
        }

        logger.info("Evaluated path dependency for institution %s", institution_id)
        return result

    def evaluate_value_system(
        self, value_system_id: uuid.UUID
    ) -> Dict[str, Any]:
        """
        Analyze cultural value system coherence and alignment.

        Args:
            value_system_id: ID of ValueSystem to evaluate

        Returns:
            Dictionary containing value system analysis

        Raises:
            SFMNotFoundError: If value system doesn't exist
        """
        from models.cultural_analysis import ValueSystem

        value_system = self.get_node(value_system_id)
        if not isinstance(value_system, ValueSystem):
            raise SFMNotFoundError(
                entity_type="ValueSystem", entity_id=value_system_id
            )

        coherence = value_system.calculate_coherence_score()
        alignment = value_system.assess_institutional_alignment()

        result = {
            "value_system_id": str(value_system_id),
            "system_type": str(value_system.system_type),
            "coherence_score": coherence,
            "institutional_alignment": alignment,
            "core_values": value_system.core_values,
            "value_hierarchy": value_system.value_hierarchy,
            "ceremonial_elements": value_system.ceremonial_elements,
            "instrumental_elements": value_system.instrumental_elements,
            "change_resistance": value_system.change_resistance,
            "adaptive_capacity": value_system.adaptive_capacity,
        }

        logger.info("Evaluated value system %s", value_system_id)
        return result

    def evaluate_belief_stability(
        self, belief_id: uuid.UUID
    ) -> Dict[str, Any]:
        """
        Assess social belief stability and change potential.

        Args:
            belief_id: ID of SocialBelief to evaluate

        Returns:
            Dictionary containing belief stability assessment

        Raises:
            SFMNotFoundError: If belief doesn't exist
        """
        from models.cultural_analysis import SocialBelief

        belief = self.get_node(belief_id)
        if not isinstance(belief, SocialBelief):
            raise SFMNotFoundError(
                entity_type="SocialBelief", entity_id=belief_id
            )

        stability = belief.assess_belief_stability()
        logger.info("Evaluated belief stability for %s", belief_id)
        return stability

    def evaluate_attitude_mediation(
        self, attitude_id: uuid.UUID
    ) -> Dict[str, Any]:
        """
        Analyze attitude's capacity to mediate between beliefs and institutions.

        Args:
            attitude_id: ID of CulturalAttitude to evaluate

        Returns:
            Dictionary containing mediation analysis

        Raises:
            SFMNotFoundError: If attitude doesn't exist
        """
        from models.cultural_analysis import CulturalAttitude

        attitude = self.get_node(attitude_id)
        if not isinstance(attitude, CulturalAttitude):
            raise SFMNotFoundError(
                entity_type="CulturalAttitude", entity_id=attitude_id
            )

        mediation = attitude.analyze_mediation_capacity()
        logger.info("Evaluated attitude mediation for %s", attitude_id)
        return mediation

    def evaluate_system_holarchy(
        self, holarchy_id: uuid.UUID
    ) -> Dict[str, Any]:
        """
        Analyze institutional holarchy coherence and leverage points.

        Args:
            holarchy_id: ID of InstitutionalHolarchy to evaluate

        Returns:
            Dictionary containing holarchy analysis

        Raises:
            SFMNotFoundError: If holarchy doesn't exist
        """
        from models.system_analysis import InstitutionalHolarchy

        holarchy = self.get_node(holarchy_id)
        if not isinstance(holarchy, InstitutionalHolarchy):
            raise SFMNotFoundError(
                entity_type="InstitutionalHolarchy", entity_id=holarchy_id
            )

        coherence = holarchy.calculate_system_coherence()
        leverage = holarchy.identify_leverage_points()

        result = {
            "holarchy_id": str(holarchy_id),
            "system_coherence": coherence,
            "leverage_points": [str(lp) for lp in leverage],
            "hierarchical_coherence": holarchy.hierarchical_coherence,
            "institutional_levels": {
                str(k): [str(v) for v in vals]
                for k, vals in holarchy.institutional_levels.items()
            },
            "bottleneck_levels": [str(bl) for bl in holarchy.bottleneck_levels],
        }

        logger.info("Evaluated holarchy %s", holarchy_id)
        return result

    def export_to_json(self) -> Dict[str, Any]:
        """
        Export the entire graph to JSON format.

        Returns:
            Dictionary with "nodes" and "relationships" lists, plus metadata

        Example:
            >>> export_data = service.export_to_json()
            >>> import json
            >>> with open('backup.json', 'w') as f:
            ...     json.dump(export_data, f)
        """
        from datetime import datetime, timezone

        nodes_data = []
        for node in self.list_nodes():
            # Serialize node to dict
            node_dict: Dict[str, Any] = {
                "id": str(node.id),
                "label": node.label,
                "description": node.description,
                "meta": node.meta,
                "version": node.version,
                "created_at": node.created_at.isoformat() if node.created_at else None,
                "modified_at": node.modified_at.isoformat() if node.modified_at else None,
                "node_type": type(node).__name__,
            }

            # Add type-specific fields
            for attr_name in dir(node):
                if attr_name.startswith('_') or attr_name in ('id', 'label', 'description', 'meta', 'version', 'created_at', 'modified_at'):
                    continue
                attr_value = getattr(node, attr_name, None)
                if callable(attr_value):
                    continue
                # Serialize enums and complex types
                if attr_value is not None and hasattr(attr_value, 'value'):  # Enum
                    node_dict[attr_name] = attr_value.value
                elif isinstance(attr_value, (list, dict, str, int, float, bool, type(None))):
                    node_dict[attr_name] = attr_value
                elif hasattr(attr_value, 'isoformat'):  # datetime
                    node_dict[attr_name] = attr_value.isoformat()
                else:
                    node_dict[attr_name] = str(attr_value)

            nodes_data.append(node_dict)

        # Export relationships
        relationships_data: List[Any] = []
        for rel in self.list_relationships():
            rel_dict = {
                "id": str(rel.id),
                "source_id": str(rel.source_id),
                "target_id": str(rel.target_id),
                "kind": rel.kind,
                "weight": rel.weight,
                "meta": rel.meta,
            }
            relationships_data.append(rel_dict)

        export_data = {
            "nodes": nodes_data,
            "relationships": relationships_data,
            "metadata": {
                "export_time": datetime.now(timezone.utc).isoformat(),
                "node_count": len(nodes_data),
                "relationship_count": len(relationships_data),
                "sfm_version": "0.2.0",
            }
        }

        logger.info("Exported %d nodes to JSON", len(nodes_data))
        return export_data

    def import_from_json(self, import_data: Dict[str, Any]) -> None:
        """
        Import graph data from JSON format.

        Args:
            import_data: Dictionary with "nodes" and "relationships" lists

        Raises:
            SFMValidationError: If import data is invalid

        Example:
            >>> import json
            >>> with open('backup.json', 'r') as f:
            ...     import_data = json.load(f)
            >>> service.import_from_json(import_data)
        """
        import importlib
        from datetime import datetime

        if "nodes" not in import_data:
            raise SFMValidationError(
                "Import data missing 'nodes' field",
                "import_data",
                str(import_data.keys())
            )

        nodes_imported = 0
        for node_data in import_data["nodes"]:
            node_type = node_data.get("node_type", "Node")

            # Dynamically import the node class
            try:
                # Try importing from models package
                models_module = importlib.import_module("models")
                node_class = getattr(models_module, node_type, Node)
            except (ImportError, AttributeError):
                node_class = Node

            # Prepare constructor arguments
            constructor_args: Dict[str, Any] = {}
            for key, value in node_data.items():
                if key in ("node_type", "created_at", "modified_at"):
                    continue
                if key == "id":
                    constructor_args[key] = uuid.UUID(value)
                elif isinstance(value, str) and key.endswith('_at'):
                    try:
                        constructor_args[key] = datetime.fromisoformat(value)
                    except ValueError:
                        constructor_args[key] = value
                else:
                    constructor_args[key] = value

            # Create the node
            try:
                node = node_class(**constructor_args)
                self.create_node(node)
                nodes_imported += 1
            except Exception as e:
                logger.warning("Failed to import node %s: %s", node_data.get('id'), e)
                continue

        # Import relationships if present
        relationships_imported = 0
        if "relationships" in import_data:
            from graph.sfm_graph import Relationship

            for rel_data in import_data["relationships"]:
                try:
                    relationship = Relationship(
                        id=uuid.UUID(rel_data["id"]),
                        source_id=uuid.UUID(rel_data["source_id"]),
                        target_id=uuid.UUID(rel_data["target_id"]),
                        kind=rel_data.get("kind", ""),
                        weight=rel_data.get("weight"),
                        meta=rel_data.get("meta", {})
                    )
                    self.create_relationship(relationship)
                    relationships_imported += 1
                except Exception as e:
                    logger.warning("Failed to import relationship %s: %s", rel_data.get('id'), e)
                    continue

        logger.info("Imported %d nodes and %d relationships from JSON", nodes_imported, relationships_imported)

    def import_bulk(
        self,
        source: Union[str, Path, Dict[str, Any]],
        adapter: Optional[Any] = None,  # BaseImportAdapter type
        config: Optional[Any] = None     # ImportConfig type
    ) -> Any:  # ImportResult type
        """
        Import data in bulk using appropriate adapter.

        Supports auto-detection of format (CSV, JSON, URL patterns) or
        explicit adapter specification. Uses bulk node creation for performance.

        Args:
            source: File path, URL, or data dictionary
            adapter: Import adapter (auto-detected if not provided)
            config: Import configuration (uses defaults if not provided)

        Returns:
            ImportResult with statistics, errors, and warnings

        Example:
            >>> from data.importers import CSVImportAdapter, MappingTemplates
            >>> mapping = MappingTemplates.csv_institution()
            >>> adapter = CSVImportAdapter(mapping)
            >>> result = service.import_bulk('institutions.csv', adapter=adapter)
            >>> print(f"Created {result.nodes_created} nodes")
        """
        import time
        from data.importers import ImportResult, ImportConfig
        from graph.sfm_persistence import NodeSerializer

        # Use provided config or defaults
        if config is None:
            config = ImportConfig()

        # Auto-detect adapter if not provided
        if adapter is None:
            from data.importers.csv_adapter import CSVImportAdapter
            from data.importers import MappingTemplates

            # Try CSV detection
            adapter = CSVImportAdapter(MappingTemplates.basic_node(), config)
            if not adapter.detect_format(source):
                raise ValueError("Could not auto-detect import format. Please provide an adapter.")

        # Initialize result
        result = ImportResult()
        start_time = time.time()

        # Validate format first
        format_errors = adapter.validate_format(source)
        if format_errors and not config.continue_on_error:
            for error in format_errors:
                result.add_error(None, None, error)
            result.elapsed_time = time.time() - start_time
            return result

        # Batch tracking
        node_batch: List[Node] = []
        row_num = 0

        try:
            # Stream nodes from source
            for row_num, node_dict in enumerate(adapter.extract_nodes(source), start=1):
                try:
                    # Get node type
                    node_type_name = node_dict.pop("_node_type", config.default_node_type)

                    # Instantiate node using NodeSerializer registry
                    node_class = NodeSerializer.get_node_class(node_type_name)
                    if node_class is None:
                        raise ValueError(f"Unknown node type: {node_type_name}")

                    # Create node instance
                    node = node_class(**node_dict)

                    # Add to batch
                    node_batch.append(node)

                    # Flush batch when reaching batch size
                    if len(node_batch) >= config.batch_size:
                        if not config.dry_run:
                            self.repository.create_nodes_bulk(node_batch)
                        result.nodes_created += len(node_batch)
                        node_batch = []

                        if config.show_progress and row_num % config.progress_interval == 0:
                            logger.info("Imported %d nodes...", result.nodes_created)

                except Exception as e:
                    result.nodes_failed += 1
                    result.add_error(
                        row=row_num,
                        field=None,
                        message=str(e),
                        suggested_fix=None
                    )

                    if not config.continue_on_error:
                        break

            # Flush remaining nodes
            if node_batch and not config.dry_run:
                self.repository.create_nodes_bulk(node_batch)
                result.nodes_created += len(node_batch)

        except Exception as e:
            result.add_error(None, None, f"Import failed: {e}")
            logger.error("Bulk import failed: %s", e)

        result.elapsed_time = time.time() - start_time

        logger.info(
            "Bulk import complete: %d nodes created, %d failed, %.2fs elapsed",
            result.nodes_created,
            result.nodes_failed,
            result.elapsed_time
        )

        return result

    # Hayden-compliant delivery matrix methods

    def create_delivery_matrix(
        self,
        matrix_id: Optional[uuid.UUID] = None,
        components: Optional[List[uuid.UUID]] = None,
        description: str = "",
        label: str = "SFM Delivery Matrix",
        matrix_scope: Optional[str] = None
    ) -> Any:  # SFMDeliveryMatrix type
        """
        Create new Hayden-compliant delivery matrix.

        Creates a square N×N matrix where components appear on both axes.
        Non-symmetric: Cell (i,j) ≠ Cell (j,i)

        Args:
            matrix_id: Optional matrix ID (generated if not provided)
            components: Initial component UUIDs (can be added later)
            description: Matrix description
            label: Matrix label
            matrix_scope: Scope level (local, regional, national, global)

        Returns:
            SFMDeliveryMatrix instance

        Example:
            >>> matrix = service.create_delivery_matrix(
            ...     label="Nebraska K-12 Education Finance",
            ...     matrix_scope="state"
            ... )
            >>> matrix.add_component(legislature_id)
            >>> matrix.add_component(school_district_id)
        """
        from models.delivery_matrix import SFMDeliveryMatrix

        matrix = SFMDeliveryMatrix(
            id=matrix_id or uuid.uuid4(),
            label=label,
            description=description,
            components=components or [],
            matrix_scope=matrix_scope
        )

        # Store in repository
        self.repository.create_node(matrix)

        logger.info("Created delivery matrix '%s' with %d components", label, len(matrix.components))
        return matrix

    def add_delivery_to_matrix(
        self,
        matrix: Any,  # SFMDeliveryMatrix type
        source_id: uuid.UUID,
        target_id: uuid.UUID,
        delivery: Any,  # Delivery type
        cell_description: str
    ) -> Any:  # SFMDeliveryCell type
        """
        Add delivery to matrix cell.

        Creates cell if doesn't exist. Supports multiple deliveries per cell
        per Hayden 2008 requirement.

        Args:
            matrix: SFMDeliveryMatrix instance
            source_id: Source component UUID
            target_id: Target component UUID
            delivery: Delivery instance to add
            cell_description: Required cell description per Hayden methodology

        Returns:
            SFMDeliveryCell with delivery added

        Raises:
            ValueError: If components not in matrix or cell_description empty

        Example:
            >>> from models.delivery_matrix import Delivery
            >>> delivery = Delivery(
            ...     delivery_type="money",
            ...     delivery_content="$800M annual appropriation",
            ...     quantity=800_000_000,
            ...     units="USD/year",
            ...     temporal_rate="annual"
            ... )
            >>> cell = service.add_delivery_to_matrix(
            ...     matrix=matrix,
            ...     source_id=legislature_id,
            ...     target_id=school_district_id,
            ...     delivery=delivery,
            ...     cell_description="Legislature provides funding to school district"
            ... )
        """
        from models.delivery_matrix import SFMDeliveryCell

        # Validate components are in matrix
        if source_id not in matrix.components:
            raise ValueError(f"Source component {source_id} not in matrix")
        if target_id not in matrix.components:
            raise ValueError(f"Target component {target_id} not in matrix")

        # Validate cell description
        if not cell_description:
            raise ValueError(
                "cell_description is required per Hayden methodology. "
                "Cell descriptions are canonical SFM deliverables."
            )

        # Get or create cell
        cell = matrix.get_cell(source_id, target_id)
        if cell is None:
            # Get component labels for cell label
            source_node = self.repository.read_node(source_id)
            target_node = self.repository.read_node(target_id)
            cell_label = f"{source_node.label if source_node else source_id}→{target_node.label if target_node else target_id}"

            cell = SFMDeliveryCell(
                label=cell_label,
                source_component_id=source_id,
                target_component_id=target_id,
                cell_description=cell_description
            )
            matrix.set_cell(cell)
            self.repository.create_node(cell)

        # Add delivery to cell
        cell.add_delivery(delivery)

        # Update cell in repository
        self.repository.update_node(cell)

        logger.info(
            "Added %s delivery to cell (%s, %s): %s",
            delivery.delivery_type,
            source_id,
            target_id,
            delivery.delivery_content[:50]
        )

        return cell

    def validate_delivery_matrix(self, matrix: Any) -> List[str]:  # SFMDeliveryMatrix type
        """
        Validate matrix per Hayden requirements.

        Checks:
        - Square structure (components on both axes)
        - Non-empty cells have descriptions
        - Deliveries are heterogeneously typed
        - Components exist in graph

        Args:
            matrix: SFMDeliveryMatrix to validate

        Returns:
            List of validation error messages (empty if valid)

        Example:
            >>> errors = service.validate_delivery_matrix(matrix)
            >>> if errors:
            ...     print("Validation errors:")
            ...     for error in errors:
            ...         print(f"  - {error}")
            ... else:
            ...     print("Matrix is valid per Hayden methodology")
        """
        errors = []

        # Check square structure
        if not matrix.is_square():
            errors.append("Matrix is not square")

        # Check matrix's own validation
        matrix_errors = matrix.validate_structure()
        errors.extend(matrix_errors)

        # Check that all components exist in graph
        for comp_id in matrix.components:
            try:
                node = self.repository.read_node(comp_id)
                if node is None:
                    errors.append(f"Component {comp_id} not found in graph")
            except Exception as e:
                errors.append(f"Error checking component {comp_id}: {e}")

        # Check delivery heterogeneity (optional quality check)
        for cell in matrix.get_non_empty_cells():
            delivery_types = set(d.delivery_type for d in cell.deliveries)
            if len(delivery_types) == 1 and len(cell.deliveries) > 1:
                logger.warning(
                    "Cell (%s, %s) has %d deliveries but all same type (%s). "
                    "Consider heterogeneous delivery types per Hayden 2008.",
                    cell.source_component_id,
                    cell.target_component_id,
                    len(cell.deliveries),
                    list(delivery_types)[0]
                )

        return errors

    # ========================================
    # Temporal Modeling & Threshold Monitoring
    # ========================================

    # Valid temporal rates per Hayden 1987/1993
    VALID_TEMPORAL_RATES = [
        "continuous",
        "real_time",
        "daily",
        "weekly",
        "monthly",
        "quarterly",
        "annual",
        "biennial",
        "event_triggered",
        "on_demand",
        "legislative_cycle",
        "fiscal_year",
        "academic_year",
    ]

    def validate_temporal_rate(self, delivery: Any) -> bool:
        """
        Validate delivery temporal rate.

        Args:
            delivery: Delivery instance to validate

        Returns:
            True if valid or None, False if invalid

        Example:
            >>> delivery = Delivery(delivery_type="money", delivery_content="Payment", temporal_rate="annual")
            >>> service.validate_temporal_rate(delivery)
            True
        """
        if delivery.temporal_rate is None:
            return True

        # Normalize hyphen/underscore for backward compatibility
        # (existing code uses "event-triggered", new uses "event_triggered")
        normalized_rate = delivery.temporal_rate.replace('-', '_')
        return normalized_rate in self.VALID_TEMPORAL_RATES

    def check_delivery_thresholds(
        self,
        matrix: Any  # SFMDeliveryMatrix
    ) -> List['ThresholdAlert']:
        """
        Monitor all deliveries against thresholds.

        Implements Hayden 1987/1993 real-time monitoring concept.
        Checks each delivery with a threshold and returns alerts for
        values that have crossed the threshold.

        Args:
            matrix: SFMDeliveryMatrix to monitor

        Returns:
            List of ThresholdAlert objects for deliveries that crossed thresholds

        Example:
            >>> alerts = service.check_delivery_thresholds(matrix)
            >>> for alert in alerts:
            ...     print(f"{alert.delivery.delivery_type}: {alert.current_value} {alert.direction} threshold {alert.threshold}")
        """
        from datetime import datetime

        alerts = []

        for cell in matrix.cells.values():
            for delivery in cell.deliveries:
                if delivery.threshold is None or delivery.quantity is None:
                    continue

                triggered = False
                direction = ""

                if delivery.threshold_direction == "above":
                    if delivery.quantity > delivery.threshold:
                        triggered = True
                        direction = "exceeded"
                elif delivery.threshold_direction == "below":
                    if delivery.quantity < delivery.threshold:
                        triggered = True
                        direction = "below"

                if triggered:
                    alert = ThresholdAlert(
                        delivery=delivery,
                        cell=cell,
                        current_value=delivery.quantity,
                        threshold=delivery.threshold,
                        direction=direction,
                        timestamp=datetime.now()
                    )
                    alerts.append(alert)

                    # Update last check time on delivery
                    delivery.last_threshold_check = datetime.now()

        return alerts

    def update_delivery_quantity(
        self,
        matrix: Any,  # SFMDeliveryMatrix
        source_id: uuid.UUID,
        target_id: uuid.UUID,
        delivery_index: int,
        new_quantity: float
    ) -> List['ThresholdAlert']:
        """
        Update delivery quantity and check for threshold violations.

        Updates the quantity and immediately checks if threshold crossed.
        Implements real-time monitoring per Hayden 1987/1993.

        Args:
            matrix: SFMDeliveryMatrix containing delivery
            source_id: Source component UUID
            target_id: Target component UUID
            delivery_index: Index of delivery in cell's delivery list
            new_quantity: New quantity value

        Returns:
            List of ThresholdAlert objects (may be empty)

        Raises:
            ValueError: If cell or delivery not found

        Example:
            >>> alerts = service.update_delivery_quantity(
            ...     matrix, source_id, target_id, 0, 550_000_000
            ... )
            >>> if alerts:
            ...     print(f"Threshold violated: {alerts[0].direction}")
        """
        from datetime import datetime

        cell = matrix.get_cell(source_id, target_id)
        if cell is None:
            raise ValueError(f"Cell ({source_id}, {target_id}) not found in matrix")

        if delivery_index >= len(cell.deliveries):
            raise ValueError(
                f"Delivery index {delivery_index} out of range (cell has {len(cell.deliveries)} deliveries)"
            )

        delivery = cell.deliveries[delivery_index]
        old_quantity = delivery.quantity

        # Update quantity
        delivery.quantity = new_quantity

        # Check threshold immediately (before persisting)
        alerts = []
        if delivery.threshold is not None:
            triggered = False
            direction = ""

            if delivery.threshold_direction == "above":
                if new_quantity > delivery.threshold:
                    triggered = True
                    direction = "exceeded"
            elif delivery.threshold_direction == "below":
                if new_quantity < delivery.threshold:
                    triggered = True
                    direction = "below"

            # Always update last_threshold_check when threshold exists
            delivery.last_threshold_check = datetime.now()

            if triggered:
                alert = ThresholdAlert(
                    delivery=delivery,
                    cell=cell,
                    current_value=new_quantity,
                    threshold=delivery.threshold,
                    direction=direction,
                    timestamp=datetime.now()
                )
                alerts.append(alert)

        # Update cell in repository (after updating last_threshold_check)
        self.repository.update_node(cell)

        logger.info(
            "Updated delivery quantity from %s to %s in cell (%s, %s)",
            old_quantity, new_quantity, source_id, target_id
        )

        return alerts

    def get_deliveries_by_temporal_rate(
        self,
        matrix: Any,  # SFMDeliveryMatrix
        temporal_rate: str
    ) -> List[Dict[str, Any]]:
        """
        Filter deliveries by temporal rate.

        Finds all deliveries with specified temporal rate across matrix.

        Args:
            matrix: SFMDeliveryMatrix to search
            temporal_rate: Temporal rate to filter by (e.g., "annual", "monthly")

        Returns:
            List of dicts with delivery info: {
                "delivery": Delivery object,
                "cell": SFMDeliveryCell,
                "source_id": UUID,
                "target_id": UUID,
                "delivery_index": int
            }

        Example:
            >>> annual_deliveries = service.get_deliveries_by_temporal_rate(matrix, "annual")
            >>> for item in annual_deliveries:
            ...     print(f"{item['delivery'].delivery_content}: {item['delivery'].quantity}")
        """
        results = []

        for (source_id, target_id), cell in matrix.cells.items():
            for idx, delivery in enumerate(cell.deliveries):
                if delivery.temporal_rate == temporal_rate:
                    results.append({
                        "delivery": delivery,
                        "cell": cell,
                        "source_id": source_id,
                        "target_id": target_id,
                        "delivery_index": idx
                    })

        logger.info(
            "Found %d deliveries with temporal_rate='%s'",
            len(results), temporal_rate
        )

        return results

    def create_temporal_clock(
        self,
        clock_name: str,
        label: str,
        description: str = "",
        period_length: Optional[Any] = None,  # timedelta
        phases: Optional[List[Any]] = None  # List[TemporalPhase]
    ) -> Any:  # TemporalClock
        """
        Create temporal clock for polychronic modeling.

        Args:
            clock_name: Unique identifier (e.g., "nebraska_legislative_cycle")
            label: Display label
            description: Clock description
            period_length: Full cycle duration (timedelta)
            phases: List of TemporalPhase objects

        Returns:
            TemporalClock instance

        Example:
            >>> from datetime import timedelta
            >>> from models.temporal_clocks import TemporalPhase
            >>> phase1 = TemporalPhase("session", timedelta(days=120))
            >>> phase2 = TemporalPhase("interim", timedelta(days=245))
            >>> clock = service.create_temporal_clock(
            ...     "legislative_cycle",
            ...     "Legislative Cycle",
            ...     period_length=timedelta(days=365),
            ...     phases=[phase1, phase2]
            ... )
        """
        from models.temporal_clocks import TemporalClock

        clock = TemporalClock(
            label=label,
            description=description,
            clock_name=clock_name,
            period_length=period_length,
            phases=phases or []
        )

        # Register in repository
        self.repository.create_node(clock)
        return clock

    def synchronize_delivery_to_clock(
        self,
        clock: Any,  # TemporalClock
        source_id: uuid.UUID,
        target_id: uuid.UUID,
        delivery_index: int = 0
    ) -> None:
        """
        Synchronize delivery to temporal clock.

        Args:
            clock: TemporalClock to synchronize to
            source_id: Source component UUID
            target_id: Target component UUID
            delivery_index: Index of delivery in cell's delivery list

        Example:
            >>> clock = service.create_temporal_clock(...)
            >>> service.synchronize_delivery_to_clock(
            ...     clock, legislature_id, district_id, delivery_index=0
            ... )
        """
        clock.synchronize_delivery(source_id, target_id, delivery_index)
        self.repository.update_node(clock)

    def advance_clock(
        self,
        clock: Any,  # TemporalClock
        matrix: Optional[Any] = None  # SFMDeliveryMatrix
    ) -> Dict[str, Any]:
        """
        Advance clock to next phase and check for due deliveries.

        Args:
            clock: TemporalClock to advance
            matrix: Optional SFMDeliveryMatrix to check for due deliveries

        Returns:
            Dictionary with:
                - new_phase: Name of new phase
                - previous_phase: Name of previous phase
                - deliveries_due: List of deliveries due in new phase (if matrix provided)
                - alerts: List of threshold alerts for due deliveries

        Example:
            >>> result = service.advance_clock(clock, matrix)
            >>> print(f"Advanced to {result['new_phase']}")
            >>> if result['deliveries_due']:
            ...     print(f"{len(result['deliveries_due'])} deliveries now due")
        """
        from datetime import datetime

        previous_phase = clock.current_phase
        new_phase = clock.advance_phase()

        # Update clock in repository
        self.repository.update_node(clock)

        result = {
            "new_phase": new_phase,
            "previous_phase": previous_phase,
            "deliveries_due": [],
            "alerts": []
        }

        # Check for deliveries due in new phase
        if matrix is not None:
            deliveries_due = clock.get_deliveries_due(matrix)
            result["deliveries_due"] = deliveries_due

            # Check thresholds for due deliveries
            for delivery_info in deliveries_due:
                delivery = delivery_info["delivery"]
                cell = delivery_info["cell"]

                if delivery.threshold is not None and delivery.quantity is not None:
                    triggered = False
                    direction = ""

                    if delivery.threshold_direction == "above":
                        if delivery.quantity > delivery.threshold:
                            triggered = True
                            direction = "exceeded"
                    elif delivery.threshold_direction == "below":
                        if delivery.quantity < delivery.threshold:
                            triggered = True
                            direction = "below"

                    if triggered:
                        alert = ThresholdAlert(
                            delivery=delivery,
                            cell=cell,
                            current_value=delivery.quantity,
                            threshold=delivery.threshold,
                            direction=direction,
                            timestamp=datetime.now()
                        )
                        result["alerts"].append(alert)

        logger.info(
            "Advanced clock '%s' from %s to %s (%d deliveries due)",
            clock.clock_name, previous_phase, new_phase, len(result["deliveries_due"])
        )

        return result

    # =========================================================================
    # Private Helper Methods for Persistence
    # =========================================================================

    def _build_snapshot_dict(self) -> Dict[str, Any]:
        """Build snapshot dictionary from current service state."""
        from datetime import datetime
        from graph.sfm_persistence import NodeSerializer

        # Get all nodes
        all_nodes = self.list_nodes()

        # Group nodes by type
        nodes_by_type: Dict[str, List[Dict[str, Any]]] = {}
        for node in all_nodes:
            node_type = type(node).__name__
            if node_type not in nodes_by_type:
                nodes_by_type[node_type] = []
            nodes_by_type[node_type].append(NodeSerializer.node_to_dict(node))

        # Get all relationships from repository
        all_rels = self.list_relationships()
        relationships = []
        for rel in all_rels:
            relationships.append({
                'id': str(rel.id),
                'source_id': str(rel.source_id),
                'target_id': str(rel.target_id),
                'kind': rel.kind if hasattr(rel, 'kind') else None,
                'weight': rel.weight if hasattr(rel, 'weight') else None,
            })

        return {
            'metadata': {
                'saved_at': datetime.now().isoformat(),
                'node_count': len(all_nodes),
                'relationship_count': len(relationships),
                'version': 1
            },
            'nodes_by_type': nodes_by_type,
            'relationships': relationships
        }

    @staticmethod
    def _json_serializer(obj: Any) -> Any:
        """Custom JSON serializer for special types."""
        from datetime import datetime
        from enum import Enum
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, uuid.UUID):
            return str(obj)
        if isinstance(obj, Enum):
            return obj.value
        raise TypeError(f"Type {type(obj)} not serializable")

    # =========================================================================
    # Persistence Operations: Save, Load, Reload, Unload
    # =========================================================================

    def save(
        self,
        filename: str,
        format_type: str = "json",
        base_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Save current SFM graph to disk.

        Args:
            filename: Name of file to save (e.g., "my_sfm.json")
            format_type: Storage format - "json" (default), "json.gz",
                        "pickle", "pickle.gz"
            base_path: Directory to save to (default: "./sfm_data")

        Returns:
            Dictionary with save metadata:
                - filepath: Absolute path to saved file
                - format: Storage format used
                - node_count: Number of nodes saved
                - relationship_count: Number of relationships saved
                - checksum: SHA-256 checksum of saved data
                - size_bytes: File size in bytes

        Example:
            >>> service = SFMService()
            >>> # ... create nodes and relationships ...
            >>> metadata = service.save("clean_air_act.json")
            >>> print(f"Saved {metadata['node_count']} nodes to {metadata['filepath']}")
        """
        from graph.sfm_persistence import SFMPersistenceManager, StorageFormat

        # Map string to StorageFormat enum
        format_map = {
            "json": StorageFormat.JSON,
            "json.gz": StorageFormat.COMPRESSED_JSON,
            "pickle": StorageFormat.PICKLE,
            "pickle.gz": StorageFormat.COMPRESSED_PICKLE,
        }

        storage_format = format_map.get(format_type.lower(), StorageFormat.JSON)

        # Build snapshot for persistence
        from graph.sfm_persistence import SFMPersistenceManager

        manager = SFMPersistenceManager(base_path or "./sfm_data")
        filepath = manager.base_path / filename

        # Build custom snapshot structure
        snapshot_data = self._build_snapshot_dict()

        # Serialize based on format
        if storage_format in [StorageFormat.JSON, StorageFormat.COMPRESSED_JSON]:
            import json
            import gzip
            json_str = json.dumps(snapshot_data, indent=2, default=self._json_serializer)
            json_bytes = json_str.encode('utf-8')

            if storage_format == StorageFormat.COMPRESSED_JSON:
                data_bytes = gzip.compress(json_bytes)
            else:
                data_bytes = json_bytes
        else:
            # Pickle formats
            import pickle
            import gzip
            pickle_bytes = pickle.dumps(snapshot_data, protocol=pickle.HIGHEST_PROTOCOL)

            if storage_format == StorageFormat.COMPRESSED_PICKLE:
                data_bytes = gzip.compress(pickle_bytes)
            else:
                data_bytes = pickle_bytes

        # Write to file
        with open(filepath, 'wb') as f:
            f.write(data_bytes)

        # Calculate checksum
        import hashlib
        checksum = hashlib.sha256(data_bytes).hexdigest()

        # Get file size
        file_size = filepath.stat().st_size

        result = {
            "filepath": str(filepath.absolute()),
            "format": format_type,
            "node_count": snapshot_data['metadata']['node_count'],
            "relationship_count": snapshot_data['metadata']['relationship_count'],
            "checksum": checksum,
            "size_bytes": file_size,
            "created_at": snapshot_data['metadata']['saved_at']
        }

        logger.info("Saved SFM graph: %s (%d nodes, %d relationships, %d bytes)",
                   filename, result['node_count'], result['relationship_count'], file_size)

        return result

    def load(
        self,
        filename: str,
        format_type: str = "json",
        base_path: Optional[str] = None,
        replace: bool = True,
        allow_pickle: bool = False
    ) -> Dict[str, Any]:
        """
        Load SFM graph from disk.

        Args:
            filename: Name of file to load
            format_type: Storage format - "json", "json.gz", "pickle", "pickle.gz"
            base_path: Directory to load from (default: "./sfm_data")
            replace: If True, replace current graph. If False, merge into current graph.
            allow_pickle: **SECURITY WARNING** - Only set True for trusted sources.
                         Pickle deserialization can execute arbitrary code.

        Returns:
            Dictionary with load metadata:
                - filepath: Absolute path to loaded file
                - format: Storage format used
                - node_count: Number of nodes loaded
                - relationship_count: Number of relationships loaded
                - replaced: Whether current graph was replaced or merged

        Raises:
            SFMPersistenceError: If file not found or deserialization fails
            SFMSerializationError: If pickle deserialization attempted without allow_pickle=True

        Example:
            >>> service = SFMService()
            >>> metadata = service.load("clean_air_act.json")
            >>> print(f"Loaded {metadata['node_count']} nodes")
        """
        from graph.sfm_persistence import SFMPersistenceManager, StorageFormat

        format_map = {
            "json": StorageFormat.JSON,
            "json.gz": StorageFormat.COMPRESSED_JSON,
            "pickle": StorageFormat.PICKLE,
            "pickle.gz": StorageFormat.COMPRESSED_PICKLE,
        }

        storage_format = format_map.get(format_type.lower(), StorageFormat.JSON)

        # Initialize persistence manager
        from graph.sfm_persistence import SFMPersistenceManager
        import json
        import gzip

        manager = SFMPersistenceManager(base_path or "./sfm_data")
        filepath = manager.base_path / filename

        if not filepath.exists():
            from graph.sfm_persistence import SFMPersistenceError
            raise SFMPersistenceError(f"File not found: {filepath}")

        # Read file
        with open(filepath, 'rb') as f:
            data_bytes = f.read()

        # Decompress if needed
        if storage_format in [StorageFormat.COMPRESSED_JSON, StorageFormat.COMPRESSED_PICKLE]:
            data_bytes = gzip.decompress(data_bytes)

        # Deserialize
        if storage_format in [StorageFormat.JSON, StorageFormat.COMPRESSED_JSON]:
            snapshot_data = json.loads(data_bytes.decode('utf-8'))
        else:
            # Pickle formats
            if not allow_pickle:
                from graph.sfm_persistence import SFMSerializationError
                raise SFMSerializationError(
                    "Pickle deserialization is disabled by default because unpickling "
                    "untrusted data can execute arbitrary code (CWE-502). "
                    "Pass allow_pickle=True only when the source is fully trusted."
                )
            import pickle
            snapshot_data = pickle.loads(data_bytes)  # nosec B301

        # Count before replacement/merge
        nodes_before = len(self.list_nodes())
        rels_before = len(self.list_relationships())

        if replace:
            # Clear current state
            self.unload()

        # Load nodes
        from graph.sfm_persistence import NodeSerializer
        nodes_loaded = 0
        for _node_type, nodes_data in snapshot_data.get('nodes_by_type', {}).items():
            for node_data in nodes_data:
                try:
                    node = NodeSerializer.dict_to_node(node_data)
                    self.repository.create_node(node)
                    nodes_loaded += 1
                except Exception as e:
                    logger.warning("Failed to load node: %s", e)

        # Load relationships
        from graph.sfm_graph import Relationship
        rels_loaded = 0
        for rel_data in snapshot_data.get('relationships', []):
            try:
                rel = Relationship(
                    id=uuid.UUID(rel_data['id']),
                    source_id=uuid.UUID(rel_data['source_id']),
                    target_id=uuid.UUID(rel_data['target_id']),
                    kind=rel_data.get('kind', ''),
                    weight=rel_data.get('weight'),
                )
                self.repository.create_relationship(rel)
                rels_loaded += 1
            except Exception as e:
                logger.warning("Failed to load relationship: %s", e)

        logger.info("Loaded %d nodes and %d relationships from %s",
                   nodes_loaded, rels_loaded, filename)

        # Get final counts
        nodes_after = len(self.list_nodes())
        rels_after = len(self.list_relationships())

        filepath = manager.base_path / filename

        result = {
            "filepath": str(filepath.absolute()),
            "format": format_type,
            "node_count": nodes_after - (nodes_before if not replace else 0),
            "relationship_count": rels_after - (rels_before if not replace else 0),
            "replaced": replace,
            "total_nodes": nodes_after,
            "total_relationships": rels_after
        }

        logger.info("Loaded SFM graph: %s (%d nodes, %d relationships)",
                   filename, result['node_count'], result['relationship_count'])

        return result

    def reload(self, filename: str, format_type: str = "json",
               base_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Reload graph from disk, replacing current state.

        Convenience method equivalent to load(filename, replace=True).
        Useful for reverting to a saved state or refreshing from disk.

        Args:
            filename: Name of file to reload
            format_type: Storage format
            base_path: Directory to load from

        Returns:
            Load metadata dictionary

        Example:
            >>> # Make changes to graph
            >>> service.create_node(Node(label="Test"))
            >>>
            >>> # Revert to saved state
            >>> service.reload("clean_air_act.json")
            >>> # All changes since last save are discarded
        """
        logger.info("Reloading graph from %s (discarding current state)", filename)
        return self.load(filename, format_type, base_path, replace=True)

    def unload(self) -> Dict[str, Any]:
        """
        Unload current graph, clearing all nodes and relationships.

        WARNING: This operation cannot be undone unless graph was saved first.
        All in-memory data will be lost.

        Returns:
            Dictionary with unload metadata:
                - nodes_removed: Number of nodes cleared
                - relationships_removed: Number of relationships cleared
                - timestamp: When unload occurred

        Example:
            >>> # Save before unloading
            >>> service.save("backup.json")
            >>>
            >>> # Clear current state
            >>> metadata = service.unload()
            >>> print(f"Cleared {metadata['nodes_removed']} nodes")
            >>>
            >>> # Start fresh or reload
            >>> service.reload("backup.json")
        """
        from datetime import datetime

        # Count before clearing
        all_nodes = self.list_nodes()
        all_rels = self.list_relationships()

        nodes_count = len(all_nodes)
        rels_count = len(all_rels)

        # Delete all relationships first
        for rel in all_rels:
            try:
                self.repository.delete_relationship(rel.id)
            except Exception as e:
                logger.warning("Failed to delete relationship %s: %s", rel.id, e)

        # Delete all nodes
        for node in all_nodes:
            try:
                self.repository.delete_node(node.id)
            except Exception as e:
                logger.warning("Failed to delete node %s: %s", node.id, e)

        # Reset query engine if it exists
        if self._query_engine is not None:
            self._query_engine = None
            logger.info("Query engine reset after unload")

        result = {
            "nodes_removed": nodes_count,
            "relationships_removed": rels_count,
            "timestamp": datetime.now().isoformat()
        }

        logger.info("Unloaded SFM graph: %d nodes and %d relationships cleared",
                   nodes_count, rels_count)

        return result

    def export_snapshot(
        self,
        filepath: str,
        export_format: str = "json"
    ) -> Dict[str, Any]:
        """
        Export graph to external format for interoperability.

        Supported formats:
            - "json": Custom JSON snapshot format (flat nodes list)
            - "graphml": GraphML format (for yEd, Cytoscape)
            - "gexf": GEXF format (for Gephi)

        Args:
            filepath: Full path to export file
            export_format: Export format type

        Returns:
            Dictionary with export metadata:
                - filepath: Absolute path to exported file
                - format: Export format used
                - node_count: Number of nodes exported
                - relationship_count: Number of relationships exported
                - size_bytes: File size

        Example:
            >>> # Export for Gephi visualization
            >>> service.export_snapshot("/tmp/network.gexf", format="gexf")
            >>>
            >>> # Export for yEd
            >>> service.export_snapshot("/tmp/network.graphml", format="graphml")
        """
        from pathlib import Path
        import json

        path = Path(filepath)

        # Export based on format
        if export_format.lower() == "json":
            # Build flat snapshot (different from save() format)
            from datetime import datetime
            from graph.sfm_persistence import NodeSerializer

            all_nodes = self.list_nodes()
            all_rels = self.list_relationships()

            snapshot_data = {
                "metadata": {
                    "saved_at": datetime.now().isoformat(),
                    "node_count": len(all_nodes),
                    "relationship_count": len(all_rels),
                    "version": 1
                },
                "nodes": [NodeSerializer.node_to_dict(node) for node in all_nodes],
                "relationships": [
                    {
                        'id': str(rel.id),
                        'source_id': str(rel.source_id),
                        'target_id': str(rel.target_id),
                        'kind': rel.kind if hasattr(rel, 'kind') else None,
                        'weight': rel.weight if hasattr(rel, 'weight') else None,
                    }
                    for rel in all_rels
                ]
            }

            with open(path, 'w', encoding='utf-8') as f:
                json.dump(snapshot_data, f, indent=2, default=self._json_serializer)
        elif export_format.lower() in ["graphml", "gexf"]:
            # Export to NetworkX format
            import networkx as nx

            nodes = self.list_nodes()
            if not nodes:
                raise ValueError("Cannot export empty graph")

            # Build NetworkX graph from repository
            G: nx.MultiDiGraph = nx.MultiDiGraph()

            # Add nodes with attributes
            for node in nodes:
                G.add_node(
                    str(node.id),
                    label=node.label,
                    node_type=type(node).__name__
                )

            # Add edges
            for rel in self.list_relationships():
                G.add_edge(
                    str(rel.source_id),
                    str(rel.target_id),
                    key=str(rel.id),
                    kind=rel.kind if hasattr(rel, 'kind') else None
                )

            # Export based on format
            if export_format.lower() == "graphml":
                nx.write_graphml(G, str(path))
            else:  # gexf
                nx.write_gexf(G, str(path))
        else:
            raise ValueError(f"Unsupported export format: {export_format}")

        # Get file info
        file_size = path.stat().st_size if path.exists() else 0

        result = {
            "filepath": str(path.absolute()),
            "format": export_format,
            "node_count": len(self.list_nodes()),
            "relationship_count": len(self.list_relationships()),
            "size_bytes": file_size
        }

        logger.info("Exported snapshot: %s (%s format, %d bytes)",
                   filepath, export_format, file_size)

        return result

    def import_snapshot(self, filepath: str) -> Dict[str, Any]:
        """
        Import graph from JSON snapshot format (flat nodes list).

        Args:
            filepath: Full path to JSON snapshot file

        Returns:
            Import metadata dictionary

        Example:
            >>> service = SFMService()
            >>> metadata = service.import_snapshot("/tmp/my_network.json")
            >>> print(f"Imported {metadata['node_count']} nodes")
        """
        from pathlib import Path
        import json
        from graph.sfm_persistence import NodeSerializer, SFMPersistenceError

        path = Path(filepath)
        if not path.exists():
            raise SFMPersistenceError(f"File not found: {filepath}")

        # Load JSON
        with open(path, 'r', encoding='utf-8') as f:
            snapshot_data = json.load(f)

        # Validate format
        if "nodes" not in snapshot_data:
            raise SFMPersistenceError("Invalid snapshot format: missing 'nodes' key")

        # Clear current graph
        self.unload()

        # Import nodes
        nodes_loaded = 0
        for node_data in snapshot_data.get("nodes", []):
            try:
                node = NodeSerializer.dict_to_node(node_data)
                self.repository.create_node(node)
                nodes_loaded += 1
            except Exception as e:
                logger.warning("Failed to import node: %s", e)

        # Import relationships
        from graph.sfm_graph import Relationship
        rels_loaded = 0
        for rel_data in snapshot_data.get("relationships", []):
            try:
                rel = Relationship(
                    id=uuid.UUID(rel_data['id']),
                    source_id=uuid.UUID(rel_data['source_id']),
                    target_id=uuid.UUID(rel_data['target_id']),
                    kind=rel_data.get('kind', ''),
                    weight=rel_data.get('weight'),
                )
                self.repository.create_relationship(rel)
                rels_loaded += 1
            except Exception as e:
                logger.warning("Failed to import relationship: %s", e)

        result = {
            "filepath": filepath,
            "node_count": nodes_loaded,
            "relationship_count": rels_loaded
        }

        logger.info("Imported snapshot: %s (%d nodes, %d relationships)",
                   filepath, result['node_count'], result['relationship_count'])

        return result


# ThresholdAlert dataclass
@dataclass
class ThresholdAlert:
    """
    Alert when delivery crosses monitoring threshold.

    Per Hayden 1987/1993 real-time monitoring concept.

    Attributes:
        delivery: Delivery that crossed threshold
        cell: SFMDeliveryCell containing the delivery
        current_value: Current delivery quantity
        threshold: Threshold value
        direction: "exceeded" (above) or "below"
        timestamp: When alert was generated
    """
    from datetime import datetime
    from models.delivery_matrix import Delivery, SFMDeliveryCell

    delivery: 'Delivery'
    cell: 'SFMDeliveryCell'
    current_value: float
    threshold: float
    direction: str  # "exceeded" or "below"
    timestamp: datetime


# Public API
__all__ = [
    "SFMService",
    "SFMServiceConfig",
    "ServiceHealth",
    "GraphStatistics",
    "ThresholdAlert",
    "SFMError",
    "SFMValidationError",
    "SFMNotFoundError",
    "NodeCreationError",
]
