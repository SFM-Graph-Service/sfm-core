"""
Abstract query layer for Social Fabric Matrix (SFM) analysis.
Provides high-level analytical queries with support for different graph storage backends.
Default implementation uses NetworkX for graph analysis.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple, Any, Union
import uuid
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import warnings

import networkx as nx

from graph.sfm_graph import SFMGraph, Relationship
from models.base_nodes import Node
from models.complex_analysis import ConflictDetection
from models.cultural_analysis import CeremonialInstrumentalClassification
from models.sfm_enums import FlowNature
from models.system_analysis import InstitutionalHolarchy
from models.policy_framework import PolicyInstrument

# Public API
__all__ = [
    'AnalysisType',
    'QueryResult',
    'NodeMetrics',
    'FlowAnalysis',
    'SFMQueryEngine',
    'NetworkXSFMQueryEngine',
    'SFMQueryFactory',
]


class AnalysisType(Enum):
    """Types of SFM analysis supported."""

    CENTRALITY = "centrality"
    INFLUENCE = "influence"
    DEPENDENCY = "dependency"
    FLOW_ANALYSIS = "flow_analysis"
    NETWORK_STRUCTURE = "network_structure"
    POLICY_IMPACT = "policy_impact"
    SCENARIO_COMPARISON = "scenario_comparison"
    CEREMONIAL_INSTRUMENTAL = "ceremonial_instrumental"
    CIRCULAR_CAUSATION = "circular_causation"
    HOLARCHY = "holarchy"
    CONFLICT = "conflict"


@dataclass
class QueryResult:
    """Container for query results with metadata."""

    data: Any
    query_type: str
    parameters: Dict[str, Any]
    metadata: Dict[str, Any]
    timestamp: str


@dataclass
class NodeMetrics:
    """Metrics for individual nodes in the SFM."""

    node_id: uuid.UUID
    centrality_scores: Dict[str, float]
    influence_score: float
    dependency_score: float
    connectivity: int
    node_type: str


@dataclass
class FlowAnalysis:
    """Analysis results for resource/value flows."""

    flow_paths: List[List[uuid.UUID]]
    bottlenecks: List[uuid.UUID]
    flow_volumes: Dict[uuid.UUID, float]
    efficiency_metrics: Dict[str, float]


class SFMQueryEngine(ABC):  # pylint: disable=too-many-public-methods
    """Abstract base class for SFM analytical queries."""

    def __init__(self, graph: SFMGraph):
        self.graph = graph

    # ─── NODE ANALYSIS ───

    @abstractmethod
    def get_node_centrality(
        self, node_id: uuid.UUID, centrality_type: str = "betweenness"
    ) -> float:
        """Calculate centrality measures for a node."""

    @abstractmethod
    def get_most_central_nodes(
        self,
        node_type: Optional[type] = None,
        centrality_type: str = "betweenness",
        limit: int = 10,
    ) -> List[Tuple[uuid.UUID, float]]:
        """Get the most central nodes by type."""

    @abstractmethod
    def get_node_neighbors(
        self,
        node_id: uuid.UUID,
        relationship_kinds: Optional[List[str]] = None,
        distance: int = 1,
    ) -> List[uuid.UUID]:
        """Get neighboring nodes within specified distance."""

    # ─── RELATIONSHIP ANALYSIS ───

    @abstractmethod
    def find_shortest_path(
        self,
        source_id: uuid.UUID,
        target_id: uuid.UUID,
        relationship_kinds: Optional[List[str]] = None,
    ) -> Optional[List[uuid.UUID]]:
        """Find shortest path between two nodes."""

    @abstractmethod
    def find_cycles(self, max_length: int = 10) -> List[List[uuid.UUID]]:
        """Find cycles in the graph (feedback loops)."""

    # ─── FLOW ANALYSIS ───

    @abstractmethod
    def identify_bottlenecks(self, flow_type: FlowNature) -> List[uuid.UUID]:
        """Identify bottleneck nodes in flow networks."""

    # ─── STRUCTURAL ANALYSIS ───

    @abstractmethod
    def get_network_density(self) -> float:
        """Calculate overall network density."""

    @abstractmethod
    def identify_communities(
        self, algorithm: str = "louvain"
    ) -> Dict[int, List[uuid.UUID]]:
        """Identify communities/clusters in the network."""

    # ─── COMPOSITE QUERIES ───

    @abstractmethod
    def comprehensive_node_analysis(self, node_id: uuid.UUID) -> NodeMetrics:
        """Comprehensive analysis of a single node."""

    # ═══════════════════════════════════════════════════════════════════════════
    # BETA FRAMEWORK EXTENSIONS
    # ═══════════════════════════════════════════════════════════════════════════

    @abstractmethod
    def query_ceremonial_vs_instrumental(
        self, threshold: float = 0.5
    ) -> Dict[str, List[Node]]:
        """
        Query nodes classified by ceremonial vs instrumental characteristics.

        Uses Beta's cultural_analysis.py framework to classify nodes as:
        - Ceremonial: Status quo reinforcing, tradition-bound
        - Instrumental: Problem-solving, adaptive, technology-enabling

        Args:
            threshold: Minimum score (0-1) to include in classification

        Returns:
            Dict with 'ceremonial', 'instrumental', and 'mixed' node lists
        """

    @abstractmethod
    def query_circular_causation_paths(
        self, source_id: uuid.UUID, max_depth: int = 5
    ) -> List[List[Node]]:
        """
        Trace circular causation paths starting from a source node.

        Uses Beta's complex_analysis.py digraph logic to identify feedback
        loops and cumulative causation sequences.

        Args:
            source_id: Starting node UUID
            max_depth: Maximum path length to trace

        Returns:
            List of paths, each path is a list of Node objects
        """

    @abstractmethod
    def query_holarchy_levels(
        self, institution_id: uuid.UUID
    ) -> Dict[str, List[Node]]:
        """
        Query institutional holarchy levels for nested arrangements.

        Uses Beta's system_analysis.py institutional holarchy model to
        identify hierarchical institutional structures.

        Args:
            institution_id: Root institution UUID

        Returns:
            Dict mapping holarchy levels to node lists
        """

    @abstractmethod
    def detect_conflicts(self) -> List[Dict[str, Any]]:
        """
        Detect conflicts and contradictions in the graph.

        Uses Beta's complex_analysis.py conflict detection to identify:
        - Direct contradictions
        - Value conflicts
        - Institutional contradictions
        - Ceremonial vs instrumental tensions

        Returns:
            List of conflict descriptions with metadata
        """


class NetworkXSFMQueryEngine(SFMQueryEngine):  # pylint: disable=too-many-public-methods
    """NetworkX-based implementation of SFM query engine."""

    def __init__(self, graph: SFMGraph):
        super().__init__(graph)
        self.nx_graph: nx.MultiDiGraph = self._build_networkx_graph()

    def _build_networkx_graph(self) -> nx.MultiDiGraph:
        """Convert SFMGraph to NetworkX graph for analysis."""
        from models.delivery_matrix import SFMDeliveryCell

        nx_graph: nx.MultiDiGraph = nx.MultiDiGraph()

        # Add all nodes
        for node in self.graph:
            nx_graph.add_node(node.id, data=node, type=type(node).__name__)

        # Add all relationships as edges
        for rel in self.graph.relationships.values():
            nx_graph.add_edge(
                rel.source_id,
                rel.target_id,
                key=rel.id,
                data=rel,
                kind=rel.kind,
                weight=rel.weight or 1.0,
            )

        # Also add edges derived from SFMDeliveryCell nodes so that delivery
        # matrix entries participate in graph traversal (circular causation,
        # cycle detection, centrality, etc.).
        for node in self.graph:
            if (
                isinstance(node, SFMDeliveryCell)
                and node.deliveries
                and node.source_component_id is not None
                and node.target_component_id is not None
                and node.source_component_id in nx_graph
                and node.target_component_id in nx_graph
            ):
                # Derive edge weight from average delivery certainty when available
                certainties = [
                    d.certainty
                    for d in node.deliveries
                    if d.certainty is not None
                ]
                weight = sum(certainties) / len(certainties) if certainties else 1.0
                nx_graph.add_edge(
                    node.source_component_id,
                    node.target_component_id,
                    key=node.id,
                    data=node,
                    kind="delivery",
                    weight=weight,
                )

        return nx_graph

    def get_node_centrality(
        self, node_id: uuid.UUID, centrality_type: str = "betweenness"
    ) -> float:
        """Calculate centrality measures for a node."""
        if centrality_type == "betweenness":
            centrality = nx.betweenness_centrality(self.nx_graph)
        elif centrality_type == "closeness":
            centrality = nx.closeness_centrality(self.nx_graph)
        elif centrality_type == "degree":
            centrality = nx.degree_centrality(self.nx_graph)
        else:
            centrality = nx.betweenness_centrality(self.nx_graph)

        return centrality.get(node_id, 0.0)

    def get_most_central_nodes(
        self,
        node_type: Optional[type] = None,
        centrality_type: str = "betweenness",
        limit: int = 10,
    ) -> List[Tuple[uuid.UUID, float]]:
        """Get the most central nodes by type."""
        if centrality_type == "betweenness":
            all_centralities = nx.betweenness_centrality(self.nx_graph)
        elif centrality_type == "closeness":
            all_centralities = nx.closeness_centrality(self.nx_graph)
        elif centrality_type == "degree":
            all_centralities = nx.degree_centrality(self.nx_graph)
        else:
            all_centralities = nx.betweenness_centrality(self.nx_graph)

        # Filter by node type if specified
        if node_type:
            filtered_centrality = {
                node_id: score
                for node_id, score in all_centralities.items()
                if isinstance(self.nx_graph.nodes[node_id]["data"], node_type)
            }
        else:
            filtered_centrality = all_centralities

        # Sort and return top nodes
        sorted_nodes = sorted(
            filtered_centrality.items(), key=lambda x: x[1], reverse=True
        )
        return sorted_nodes[:limit]

    def get_node_neighbors(
        self,
        node_id: uuid.UUID,
        relationship_kinds: Optional[List[str]] = None,
        distance: int = 1,
    ) -> List[uuid.UUID]:
        """Get neighboring nodes within specified distance."""
        if node_id not in self.nx_graph.nodes():
            return []

        if distance == 1:
            if relationship_kinds:
                neighbors = []
                for neighbor in self.nx_graph.neighbors(node_id):
                    for edge_data in self.nx_graph[node_id][neighbor].values():
                        if edge_data.get("kind") in relationship_kinds:
                            neighbors.append(neighbor)
                            break
                return list(set(neighbors))
            return list(self.nx_graph.neighbors(node_id))

        # Multi-hop neighbors
        try:
            ego_graph = nx.ego_graph(self.nx_graph, node_id, radius=distance)
            return [n for n in ego_graph.nodes() if n != node_id]
        except (nx.NetworkXError, nx.NodeNotFound):
            return []

    def find_shortest_path(
        self,
        source_id: uuid.UUID,
        target_id: uuid.UUID,
        relationship_kinds: Optional[List[str]] = None,
    ) -> Optional[List[uuid.UUID]]:
        """Find shortest path between two nodes."""
        try:
            if source_id not in self.nx_graph.nodes() or target_id not in self.nx_graph.nodes():
                return None

            path = nx.shortest_path(self.nx_graph, source_id, target_id)
            return path if isinstance(path, list) else None
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return None

    def find_cycles(self, max_length: int = 10) -> List[List[uuid.UUID]]:
        """Find cycles in the graph (feedback loops)."""
        try:
            cycles = []
            for cycle in nx.simple_cycles(self.nx_graph):
                if len(cycle) <= max_length:
                    cycles.append(cycle)
            return cycles
        except nx.NetworkXError:
            return []

    def identify_bottlenecks(self, flow_type: FlowNature) -> List[uuid.UUID]:
        """Identify bottleneck nodes in flow networks."""
        if self.nx_graph.number_of_nodes() <= 1:
            return []

        centrality = nx.betweenness_centrality(self.nx_graph)
        if not centrality:
            return []

        threshold = sorted(centrality.values())[-max(1, len(centrality) // 10)]
        bottlenecks = [
            node_id for node_id, score in centrality.items() if score >= threshold
        ]
        return bottlenecks

    def get_network_density(self) -> float:
        """Calculate overall network density."""
        return float(nx.density(self.nx_graph))

    def identify_communities(
        self, algorithm: str = "louvain"
    ) -> Dict[int, List[uuid.UUID]]:
        """Identify communities/clusters in the network."""
        if self.nx_graph.number_of_nodes() == 0:
            return {}

        try:
            undirected_graph = self.nx_graph.to_undirected()
            communities = nx.algorithms.community.louvain_communities(undirected_graph)

            community_dict = {}
            for i, community in enumerate(communities):
                community_dict[i] = list(community)
            return community_dict
        except (nx.NetworkXError, AttributeError):
            return {0: list(self.nx_graph.nodes())}

    def comprehensive_node_analysis(self, node_id: uuid.UUID) -> NodeMetrics:
        """Comprehensive analysis of a single node."""
        if node_id not in self.nx_graph.nodes():
            return NodeMetrics(
                node_id=node_id,
                centrality_scores={"betweenness": 0.0, "closeness": 0.0, "degree": 0.0},
                influence_score=0.0,
                dependency_score=0.0,
                connectivity=0,
                node_type="Unknown"
            )

        centrality_scores = {
            "betweenness": self.get_node_centrality(node_id, "betweenness"),
            "closeness": self.get_node_centrality(node_id, "closeness"),
            "degree": self.get_node_centrality(node_id, "degree"),
        }

        neighbors = self.get_node_neighbors(node_id)
        influence_score = len([n for n in neighbors if self.nx_graph.has_edge(node_id, n)])
        dependency_score = len([n for n in neighbors if self.nx_graph.has_edge(n, node_id)])

        return NodeMetrics(
            node_id=node_id,
            centrality_scores=centrality_scores,
            influence_score=influence_score / len(neighbors) if neighbors else 0.0,
            dependency_score=dependency_score / len(neighbors) if neighbors else 0.0,
            connectivity=len(neighbors),
            node_type=type(self.nx_graph.nodes[node_id]["data"]).__name__,
        )

    # ═══════════════════════════════════════════════════════════════════════════
    # BETA FRAMEWORK EXTENSIONS - NEW METHODS
    # ═══════════════════════════════════════════════════════════════════════════

    def _infer_ceremonial_instrumental_from_type(self, node: Node) -> Tuple[float, float]:
        """Infer ceremonial/instrumental scores from node type.

        Returns:
            Tuple of (ceremonial_score, instrumental_score)
        """
        # Get the node's class name
        node_type = type(node).__name__

        # Check for specialized node types
        if isinstance(node, PolicyInstrument):
            return (0.5, 0.5)  # Policies can be either

        # Infer from class name or node_type metadata
        type_name = node_type
        if hasattr(node, 'meta') and node.meta and 'node_type' in node.meta:
            type_name = node.meta.get('node_type', node_type)

        # Type-based inference
        if type_name in ('Institution', 'InstitutionalStructure'):
            return (0.6, 0.4)  # Institutions preserve status quo
        elif type_name in ('Technology', 'ToolSkillTechnologyComplex'):
            return (0.2, 0.8)  # Technology solves problems
        elif type_name in ('Process', 'ProblemSolvingSequence'):
            return (0.3, 0.7)
        elif type_name == 'Resource':
            return (0.3, 0.7)
        elif type_name in ('PolicyInstrument', 'ValueJudgment'):
            return (0.5, 0.5)  # Policies can be either
        elif type_name in ('Actor', 'SocialBelief', 'CulturalAttitude'):
            return (0.5, 0.5)  # Actors need relationship analysis

        return (0.0, 0.0)

    def _infer_ceremonial_instrumental_from_relationships(self, node: Node) -> Tuple[float, float]:
        """Infer ceremonial/instrumental scores from relationship patterns.

        Returns:
            Tuple of (ceremonial_score, instrumental_score)
        """
        CEREMONIAL_KINDS = {"constrains", "controls", "regulates", "requires", "mandates"}
        INSTRUMENTAL_KINDS = {"enables", "produces", "innovates", "solves", "improves"}

        # Get outgoing relationships from this node
        outgoing = [rel for rel in self.graph.relationships.values() if rel.source_id == node.id]
        if not outgoing:
            return (0.0, 0.0)

        ceremonial_count = sum(1 for r in outgoing if r.kind in CEREMONIAL_KINDS)
        instrumental_count = sum(1 for r in outgoing if r.kind in INSTRUMENTAL_KINDS)
        total = ceremonial_count + instrumental_count

        if total == 0:
            return (0.0, 0.0)
        return (ceremonial_count / total, instrumental_count / total)

    def query_ceremonial_vs_instrumental(
        self, threshold: float = 0.5
    ) -> Dict[str, List[Node]]:
        """Query nodes classified by ceremonial vs instrumental characteristics.

        Uses a 4-method cascade for classification:
        1. Beta model nodes (CeremonialInstrumentalClassification)
        2. Metadata scores (ceremonial_score, instrumental_score)
        3. Type-based inference (Institution → ceremonial, Technology → instrumental)
        4. Relationship-based inference (count ceremonial vs instrumental relationship kinds)
        """
        results: Dict[str, List[Node]] = {
            "ceremonial": [],
            "instrumental": [],
            "mixed": []
        }
        unclassified_count = 0

        for node in self.graph:
            score_assigned = False
            ceremonial_score = 0.0
            instrumental_score = 0.0

            # Method 1: Beta model nodes (existing - keep for backward compatibility)
            if isinstance(node, CeremonialInstrumentalClassification):
                ceremonial_score = node.ceremonial_score or 0.0
                instrumental_score = node.instrumental_score or 0.0
                score_assigned = True

            # Method 2: Metadata (existing - improve to handle string/None values)
            elif hasattr(node, 'meta') and node.meta:
                c_score = node.meta.get('ceremonial_score')
                i_score = node.meta.get('instrumental_score')
                if c_score is not None or i_score is not None:
                    try:
                        ceremonial_score = float(c_score) if isinstance(c_score, str) and c_score not in ('', 'null') else 0.0
                        instrumental_score = float(i_score) if isinstance(i_score, str) and i_score not in ('', 'null') else 0.0
                        score_assigned = True
                    except (ValueError, TypeError):
                        # Invalid metadata values, continue to next method
                        pass

            # Method 3: Type inference (NEW)
            if not score_assigned:
                ceremonial_score, instrumental_score = self._infer_ceremonial_instrumental_from_type(node)
                if ceremonial_score > 0.0 or instrumental_score > 0.0:
                    score_assigned = True

            # Method 4: Relationship inference (NEW)
            if not score_assigned:
                ceremonial_score, instrumental_score = self._infer_ceremonial_instrumental_from_relationships(node)
                if ceremonial_score > 0.0 or instrumental_score > 0.0:
                    score_assigned = True

            # Classify based on scores
            if score_assigned:
                if ceremonial_score >= threshold and ceremonial_score > instrumental_score:
                    results["ceremonial"].append(node)
                elif instrumental_score >= threshold and instrumental_score > ceremonial_score:
                    results["instrumental"].append(node)
                else:
                    results["mixed"].append(node)
            else:
                unclassified_count += 1

        # Warn if nothing classified
        total_nodes = len(list(self.graph))
        if unclassified_count == total_nodes and total_nodes > 0:
            warnings.warn(
                f"No nodes were classified ({unclassified_count} total). "
                "Consider adding 'ceremonial_score' and 'instrumental_score' to node metadata, "
                "or use specialized node types like Institution or Technology.",
                UserWarning
            )

        return results

    def query_circular_causation_paths(
        self, source_id: uuid.UUID, max_depth: int = 5
    ) -> List[List[Node]]:
        """Trace circular causation paths starting from a source node."""
        paths: List[List[Node]] = []

        # Check if source node exists
        if source_id not in self.nx_graph.nodes():
            return paths

        # Use DFS to find paths that return to source
        def dfs_paths(current: uuid.UUID, path: List[uuid.UUID], depth: int):
            if depth > max_depth:
                return

            # Check if we've returned to source (circular)
            if len(path) > 2 and current == source_id:
                # Convert UUIDs to Node objects
                node_path = []
                for node_id in path:
                    node = self.graph.get_node_by_id(node_id)
                    if node:
                        node_path.append(node)
                if node_path:
                    paths.append(node_path)
                return

            # Explore neighbors
            for neighbor in self.nx_graph.neighbors(current):
                if neighbor not in path or (neighbor == source_id and len(path) >= 2):
                    dfs_paths(neighbor, path + [neighbor], depth + 1)

        # Start DFS from source
        dfs_paths(source_id, [source_id], 0)
        return paths

    def query_holarchy_levels(
        self, institution_id: uuid.UUID
    ) -> Dict[str, List[Node]]:
        """Query institutional holarchy levels for nested arrangements."""
        levels: Dict[str, List[Node]] = {
            "global": [],
            "national": [],
            "regional": [],
            "local": [],
            "organizational": [],
            "individual": []
        }

        # Check if institution exists
        institution_node = self.graph.get_node_by_id(institution_id)
        if not institution_node:
            return levels

        # If the node is already an InstitutionalHolarchy, use its structure
        if isinstance(institution_node, InstitutionalHolarchy):
            for level_name, node_ids in institution_node.institutional_levels.items():
                level_key = str(level_name.value if hasattr(level_name, 'value') else level_name)
                for node_id in node_ids:
                    node = self.graph.get_node_by_id(node_id)
                    if node and level_key in levels:
                        levels[level_key].append(node)
        else:
            # Build holarchy by analyzing graph structure
            # Use BFS to traverse from institution outward
            visited = {institution_id}
            queue = [(institution_id, 0)]

            while queue:
                current_id, depth = queue.pop(0)
                current_node = self.graph.get_node_by_id(current_id)

                if not current_node:
                    continue

                # Assign to level based on depth
                if depth == 0:
                    levels["organizational"].append(current_node)
                elif depth == 1:
                    levels["local"].append(current_node)
                elif depth == 2:
                    levels["regional"].append(current_node)
                elif depth == 3:
                    levels["national"].append(current_node)
                else:
                    levels["global"].append(current_node)

                # Add neighbors to queue
                if depth < 5:  # Limit depth to prevent infinite loops
                    for neighbor in self.nx_graph.neighbors(current_id):
                        if neighbor not in visited:
                            visited.add(neighbor)
                            queue.append((neighbor, depth + 1))

        return levels

    def detect_conflicts(self) -> List[Dict[str, Any]]:
        """Detect conflicts and contradictions in the graph."""
        conflicts: List[Dict[str, Any]] = []

        # Check for ConflictDetection nodes in the graph
        for node in self.graph:
            if isinstance(node, ConflictDetection):
                # Extract conflicts from the ConflictDetection node
                for direct_conflict in node.direct_conflicts:
                    conflicts.append({
                        "type": "direct",
                        "conflict_type": node.conflict_type.value if hasattr(node.conflict_type, 'value') else str(node.conflict_type),
                        "details": direct_conflict,
                        "source_node": node.id
                    })

                for indirect_conflict in node.indirect_conflicts:
                    conflicts.append({
                        "type": "indirect",
                        "conflict_type": node.conflict_type.value if hasattr(node.conflict_type, 'value') else str(node.conflict_type),
                        "details": indirect_conflict,
                        "source_node": node.id
                    })

        # Also detect structural conflicts in the graph
        # Look for contradictory relationships (e.g., A->B positive, A->B negative)
        relationship_pairs: Dict[Tuple[uuid.UUID, uuid.UUID], List[Relationship]] = {}

        for rel in self.graph.relationships.values():
            pair_key = (rel.source_id, rel.target_id)
            if pair_key not in relationship_pairs:
                relationship_pairs[pair_key] = []
            relationship_pairs[pair_key].append(rel)

        for (source, target), rels in relationship_pairs.items():
            if len(rels) > 1:
                # Check for contradictory relationships
                weights = [r.weight for r in rels if r.weight is not None]
                if weights and max(weights) > 0 and min(weights) < 0:
                    conflicts.append({
                        "type": "structural",
                        "conflict_type": "contradictory_relationships",
                        "source": source,
                        "target": target,
                        "details": f"Contradictory relationships between nodes: {weights}",
                        "relationships": [r.id for r in rels]
                    })

        # Method 3: Semantic conflict relationships
        CONFLICT_KINDS = {
            "conflicts_with", "opposes", "contradicts", "challenges",
            "undermines", "blocks", "resists"
        }

        for rel in self.graph.relationships.values():
            if rel.kind in CONFLICT_KINDS:
                source_node = self.graph.get_node_by_id(rel.source_id)
                target_node = self.graph.get_node_by_id(rel.target_id)

                conflicts.append({
                    "type": "semantic",
                    "conflict_type": rel.kind,
                    "source": source_node.label if source_node else "unknown",
                    "source_id": str(rel.source_id),
                    "target": target_node.label if target_node else "unknown",
                    "target_id": str(rel.target_id),
                    "weight": rel.weight,
                    "evidence": rel.meta.get("evidence", "") if rel.meta else "",
                    "relationship_id": str(rel.id)
                })

        return conflicts

    # ═══════════════════════════════════════════════════════════════════════════
    # UNCERTAINTY ANALYSIS METHODS (GAP 3)
    # ═══════════════════════════════════════════════════════════════════════════

    def analyze_weight_uncertainty(self) -> Dict[str, Any]:
        """Analyze uncertainty across all relationship weights."""
        rels_with_ci = []
        rels_without_ci = []

        for rel in self.graph.relationships.values():
            if rel.confidence_interval:
                rels_with_ci.append(rel)
            else:
                rels_without_ci.append(rel)

        return {
            "total_relationships": len(list(self.graph.relationships.values())),
            "with_confidence_intervals": len(rels_with_ci),
            "without_confidence_intervals": len(rels_without_ci),
            "coverage": len(rels_with_ci) / len(list(self.graph.relationships.values())) if self.graph.relationships else 0,
            "avg_uncertainty_range": self._calculate_avg_uncertainty_range(rels_with_ci)
        }

    def _calculate_avg_uncertainty_range(self, rels: List[Relationship]) -> float:
        """Calculate average width of confidence intervals."""
        if not rels:
            return 0.0
        ranges = [upper - lower for lower, upper in [r.confidence_interval for r in rels if r.confidence_interval]]
        return sum(ranges) / len(ranges) if ranges else 0.0

    def propagate_uncertainty_through_path(
        self,
        path: List[uuid.UUID]
    ) -> Dict[str, Any]:
        """Propagate uncertainty through a causal pathway."""
        cumulative_weight = 1.0
        cumulative_lower = 1.0
        cumulative_upper = 1.0

        path_segments = []

        for i in range(len(path) - 1):
            source_id = path[i]
            target_id = path[i + 1]

            # Find relationship
            rel = self._find_relationship(source_id, target_id)
            if not rel:
                continue

            weight = rel.weight or 0.5
            if rel.confidence_interval:
                lower, upper = rel.confidence_interval
            else:
                lower, upper = weight, weight

            cumulative_weight *= weight
            cumulative_lower *= lower
            cumulative_upper *= upper

            source_node = self.graph.get_node_by_id(source_id)
            target_node = self.graph.get_node_by_id(target_id)
            path_segments.append({
                "source": source_node.label if source_node else "unknown",
                "target": target_node.label if target_node else "unknown",
                "weight": weight,
                "confidence_interval": (lower, upper)
            })

        return {
            "path_segments": path_segments,
            "cumulative_effect": cumulative_weight,
            "uncertainty_range": (cumulative_lower, cumulative_upper),
            "uncertainty_width": cumulative_upper - cumulative_lower
        }

    def sensitivity_analysis(
        self,
        outcome_node_id: uuid.UUID,
        vary_percentage: float = 0.2
    ) -> Dict[str, Any]:
        """Perform sensitivity analysis by varying weights."""
        # Find all paths to outcome node
        paths_to_outcome = self._find_all_paths_to_node(outcome_node_id, max_depth=5)

        # For each path, vary weights and see impact
        sensitivity_results: List[Dict[str, Any]] = []

        for path in paths_to_outcome:
            # Vary each relationship weight
            for rel_id in path:
                rel = self.graph.relationships.get(rel_id)
                if not rel or rel.weight is None:
                    continue

                # Calculate with +/- vary_percentage
                weight_low = rel.weight * (1 - vary_percentage)
                weight_high = rel.weight * (1 + vary_percentage)

                # Temporarily modify and recalculate
                original_weight = rel.weight
                rel.weight = weight_low
                effect_low = self._calculate_path_effect(path)
                rel.weight = weight_high
                effect_high = self._calculate_path_effect(path)
                rel.weight = original_weight  # Restore

                source_node = self.graph.get_node_by_id(rel.source_id)
                target_node = self.graph.get_node_by_id(rel.target_id)

                sensitivity_results.append({
                    "relationship": rel.kind,
                    "source": source_node.label if source_node else "unknown",
                    "target": target_node.label if target_node else "unknown",
                    "base_weight": original_weight,
                    "effect_range": (effect_low, effect_high),
                    "sensitivity": (effect_high - effect_low) / (weight_high - weight_low) if weight_high != weight_low else 0.0
                })

        # Sort by sensitivity (highest first)
        sensitivity_results.sort(key=lambda x: abs(x["sensitivity"]), reverse=True)

        outcome_node = self.graph.get_node_by_id(outcome_node_id)
        return {
            "outcome_node": outcome_node.label if outcome_node else "unknown",
            "sensitivity_ranking": sensitivity_results
        }

    def _find_relationship(self, source_id: uuid.UUID, target_id: uuid.UUID) -> Optional[Relationship]:
        """Find relationship between two nodes."""
        for rel in self.graph.relationships.values():
            if rel.source_id == source_id and rel.target_id == target_id:
                return rel
        return None

    def _find_all_paths_to_node(self, target_id: uuid.UUID, max_depth: int = 5) -> List[List[uuid.UUID]]:
        """Find all paths leading to target node."""
        # Simplified implementation - would use BFS/DFS in practice
        # Returns list of paths, where each path is list of relationship IDs
        return []  # Placeholder

    def _calculate_path_effect(self, path: List[uuid.UUID]) -> float:
        """Calculate cumulative effect along a path."""
        effect = 1.0
        for rel_id in path:
            rel = self.graph.relationships.get(rel_id)
            if rel and rel.weight:
                effect *= rel.weight
        return effect

    # ═══════════════════════════════════════════════════════════════════════════
    # CONDITIONAL RELATIONSHIP QUERIES (GAP 5)
    # ═══════════════════════════════════════════════════════════════════════════

    def check_conditional_satisfaction(
        self,
        dependent_node_id: uuid.UUID
    ) -> Dict[str, Any]:
        """
        Check if conditional dependencies are satisfied.

        Args:
            dependent_node_id: UUID of node with conditional dependencies

        Returns:
            Dictionary with satisfied/unsatisfied conditions

        Example:
            # Check if catalytic converter dependencies are satisfied
            result = engine.check_conditional_satisfaction(catalytic_converter.id)
            # Returns: {"all_satisfied": True/False, "satisfied_conditions": [...], ...}
        """
        # Find all outgoing depends_on_if relationships
        conditional_rels = [
            rel for rel in self.graph.relationships.values()
            if rel.source_id == dependent_node_id
            and ("_if" in rel.kind or "conditional" in rel.meta)
        ]

        satisfied = []
        unsatisfied = []

        for rel in conditional_rels:
            if "conditional" in rel.meta:
                condition_node_id = uuid.UUID(rel.meta["conditional"]["condition_node"])  # type: ignore[index]
                condition_node = self.graph.get_node_by_id(condition_node_id)

                # Check if condition node is "active" (exists and has positive attributes)
                is_satisfied = condition_node is not None

                if is_satisfied:
                    satisfied.append({
                        "relationship": rel.kind,
                        "condition": condition_node.label if condition_node else "unknown"
                    })
                else:
                    unsatisfied.append({
                        "relationship": rel.kind,
                        "condition": "Missing condition node"
                    })

        dependent_node = self.graph.get_node_by_id(dependent_node_id)
        return {
            "dependent_node": dependent_node.label if dependent_node else "unknown",
            "satisfied_conditions": satisfied,
            "unsatisfied_conditions": unsatisfied,
            "all_satisfied": len(unsatisfied) == 0
        }

    # ═══════════════════════════════════════════════════════════════════════════
    # GEOGRAPHIC QUERY METHODS (GAP 6)
    # ═══════════════════════════════════════════════════════════════════════════

    def get_nodes_by_geography(
        self,
        state: Optional[str] = None,
        scope: Optional[str] = None,
        jurisdiction: Optional[str] = None
    ) -> List[Node]:
        """
        Query nodes by geographic attributes.

        Args:
            state: State name to filter by (e.g., "California", "TX")
            scope: Geographic scope to filter by ("federal", "state", "local", "regional")
            jurisdiction: Specific jurisdiction to filter by

        Returns:
            List of nodes matching geographic criteria

        Example:
            # Find all California state-level policies
            ca_policies = engine.get_nodes_by_geography(state="California", scope="state")
        """
        matching_nodes = []

        for node in self.graph:
            if not hasattr(node, 'meta') or not node.meta:
                continue

            geography: Union[str, Dict[str, str]] = node.meta.get("geography", {})
            if isinstance(geography, str):
                # Handle string geography metadata
                if state and state.lower() in geography.lower():
                    matching_nodes.append(node)
            elif isinstance(geography, dict):
                # Handle structured geography
                if state and geography.get("state") == state:
                    matching_nodes.append(node)
                elif scope and geography.get("scope") == scope:
                    matching_nodes.append(node)
                elif jurisdiction and geography.get("jurisdiction") == jurisdiction:
                    matching_nodes.append(node)

        return matching_nodes

    def get_policy_stringency_map(self) -> Dict[str, float]:
        """
        Generate map of policy stringency by geographic unit.

        Returns:
            Dictionary of {state: avg_stringency} where stringency
            is calculated from relationship weights

        Example:
            # Get average policy stringency by state
            stringency_map = engine.get_policy_stringency_map()
            # Returns: {"California": 0.85, "Texas": 0.62, ...}
        """
        state_map: Dict[str, float] = {}

        for node in self.graph:
            if not hasattr(node, 'meta') or not node.meta:
                continue

            geography: Union[str, Dict[str, str]] = node.meta.get("geography", {})
            if isinstance(geography, dict) and "state" in geography:
                state = geography["state"]

                # Calculate stringency from outgoing relationships
                outgoing = [
                    rel for rel in self.graph.relationships.values()
                    if rel.source_id == node.id
                ]

                if outgoing:
                    avg_weight = sum(r.weight for r in outgoing if r.weight) / len(outgoing)
                    if state in state_map:
                        state_map[state] = (state_map[state] + avg_weight) / 2
                    else:
                        state_map[state] = avg_weight

        return state_map



    # ═══════════════════════════════════════════════════════════════════════════
    # TEMPORAL QUERY METHODS
    # ═══════════════════════════════════════════════════════════════════════════

    def get_nodes_active_at_time(self, target_date: datetime) -> List[Node]:
        """Get all nodes that existed at a specific time."""
        active_nodes = []
        for node in self.graph:
            # Check if node was created before target_date
            if node.created_at <= target_date:
                # Check if not yet modified after target_date (still active)
                if node.modified_at is None or node.modified_at > target_date:
                    active_nodes.append(node)
        return active_nodes

    def get_relationships_active_at_time(self, target_date: datetime) -> List[Relationship]:
        """Get all relationships active at a specific time."""
        active_rels = []
        for rel in self.graph.relationships.values():
            # Check valid_from and valid_to bounds
            if rel.valid_from and rel.valid_from > target_date:
                continue
            if rel.valid_to and rel.valid_to <= target_date:
                continue
            active_rels.append(rel)
        return active_rels

    def get_relationship_weight_history(
        self, 
        relationship_id: uuid.UUID
    ) -> List[Dict[str, Any]]:
        """Get weight change history for a relationship."""
        rel = self.graph.get_relationship_by_id(relationship_id)
        if not rel or "weight_history" not in rel.meta:
            return []
        return rel.meta["weight_history"]  # type: ignore[no-any-return]

    def query_temporal_evolution(
        self,
        start_date: datetime,
        end_date: datetime,
        time_step: timedelta = timedelta(days=365)
    ) -> List[Dict[str, Any]]:
        """Query graph state evolution over time period."""
        snapshots = []
        current_date = start_date
        
        while current_date <= end_date:
            snapshot = {
                "date": current_date.isoformat(),
                "nodes": len(self.get_nodes_active_at_time(current_date)),
                "relationships": len(self.get_relationships_active_at_time(current_date)),
                "avg_weight": self._calculate_avg_weight_at_time(current_date)
            }
            snapshots.append(snapshot)
            current_date += time_step
        
        return snapshots

    def _calculate_avg_weight_at_time(self, target_date: datetime) -> float:
        """Calculate average relationship weight at specific time."""
        active_rels = self.get_relationships_active_at_time(target_date)
        weights = [r.weight for r in active_rels if r.weight is not None]
        return sum(weights) / len(weights) if weights else 0.0


class SFMQueryFactory:
    """Factory for creating SFM query engines."""

    @staticmethod
    def create_query_engine(
        graph: SFMGraph, backend: str = "networkx"
    ) -> SFMQueryEngine:
        """Create a query engine for the specified backend."""
        if backend.lower() == "networkx":
            return NetworkXSFMQueryEngine(graph)

        raise ValueError(f"Unsupported backend: {backend}")

