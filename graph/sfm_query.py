"""
Abstract query layer for Social Fabric Matrix (SFM) analysis.
Provides high-level analytical queries with support for different graph storage backends.
Default implementation uses NetworkX for graph analysis.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple, Any
import uuid
from dataclasses import dataclass
from enum import Enum

import networkx as nx

from graph.sfm_graph import SFMGraph, Relationship
from models.base_nodes import Node
from models.complex_analysis import ConflictDetection
from models.cultural_analysis import CeremonialInstrumentalClassification
from models.sfm_enums import FlowNature
from models.system_analysis import InstitutionalHolarchy

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
        return nx.density(self.nx_graph)

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

    def query_ceremonial_vs_instrumental(
        self, threshold: float = 0.5
    ) -> Dict[str, List[Node]]:
        """Query nodes classified by ceremonial vs instrumental characteristics."""
        results: Dict[str, List[Node]] = {
            "ceremonial": [],
            "instrumental": [],
            "mixed": []
        }

        for node in self.graph:
            # Check if node has ceremonial/instrumental classification
            if isinstance(node, CeremonialInstrumentalClassification):
                if node.ceremonial_score and node.ceremonial_score >= threshold:
                    results["ceremonial"].append(node)
                elif node.instrumental_score and node.instrumental_score >= threshold:
                    results["instrumental"].append(node)
                else:
                    results["mixed"].append(node)
            else:
                # For other nodes, try to infer from metadata
                if hasattr(node, 'meta') and node.meta:
                    ceremonial_score = node.meta.get('ceremonial_score', 0.0)
                    instrumental_score = node.meta.get('instrumental_score', 0.0)

                    # Ensure scores are numeric
                    if isinstance(ceremonial_score, (int, float)) and ceremonial_score >= threshold:
                        results["ceremonial"].append(node)
                    elif isinstance(instrumental_score, (int, float)) and instrumental_score >= threshold:
                        results["instrumental"].append(node)
                    else:
                        results["mixed"].append(node)

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
                if neighbor not in path or (neighbor == source_id and len(path) > 2):
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

        return conflicts


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
