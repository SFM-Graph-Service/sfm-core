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
from typing import Dict, List, Optional, Any, Union, Type, TypeVar
from dataclasses import dataclass

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
    TypedSFMRepository,
)

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
    ):
        self.storage_type = storage_type
        self.graph_size_limit = graph_size_limit


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

        # Initialize repository
        self._repository: SFMRepository = SFMRepositoryFactory.create_repository(
            self.config.storage_type
        )

        # Query engine will be initialized in Phase 2 Step 2
        self._query_engine: Optional[Any] = None

        logger.info("SFM Service initialized with storage type: %s", self.config.storage_type)

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

        # Placeholder - will call query_engine.get_ceremonial_analysis in Phase 2 Step 2
        logger.info("Performing ceremonial analysis with threshold %.2f", threshold)
        return {
            "ceremonial_nodes": [],
            "instrumental_nodes": [],
            "ceremonial_ratio": 0.0,
            "threshold": threshold,
        }

    def get_circular_causation(self, source_id: uuid.UUID) -> list:
        """
        Identify circular causation patterns starting from a source node.

        Args:
            source_id: UUID of the starting node

        Returns:
            List of circular causation cycles, where each cycle is:
                - nodes: List of node IDs in the cycle
                - strength: Aggregate strength of the cycle
                - feedback_type: reinforcing or balancing

        Raises:
            SFMNotFoundError: If source node doesn't exist
        """
        # Verify source node exists
        source_node = self.get_node(source_id)
        if source_node is None:
            raise SFMNotFoundError(entity_type="Node", entity_id=source_id)

        if self.query_engine is None:
            logger.warning("Query engine not initialized, returning empty cycles")
            return []

        # Placeholder - will call query_engine.get_circular_causation in Phase 2 Step 2
        logger.info("Finding circular causation from node %s", source_id)
        return []

    def get_holarchy(self, institution_id: uuid.UUID) -> dict:
        """
        Get institutional holarchy (nested hierarchy) for an institution.

        Args:
            institution_id: UUID of the institution node

        Returns:
            Dictionary containing:
                - institution_id: The root institution UUID
                - layers: List of holarchy layers from top to bottom
                - relationships: Parent-child relationships
                - depth: Maximum depth of the holarchy

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

        # Placeholder - will call query_engine.get_holarchy in Phase 2 Step 2
        logger.info("Building holarchy for institution %s", institution_id)
        return {
            "institution_id": str(institution_id),
            "layers": [],
            "relationships": [],
            "depth": 0,
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

        # Placeholder - will call query_engine.get_conflicts in Phase 2 Step 2
        logger.info("Detecting system conflicts")
        return []

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

        result = {
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


# Public API
__all__ = [
    "SFMService",
    "SFMServiceConfig",
    "ServiceHealth",
    "GraphStatistics",
    "SFMError",
    "SFMValidationError",
    "SFMNotFoundError",
    "NodeCreationError",
]
