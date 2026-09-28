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
from models.delivery_matrix import SFMDeliveryCell
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
    'compute_data_quality',
]


def _severity_label(severity: float) -> str:
    if severity >= 0.7:
        return "high"
    if severity >= 0.4:
        return "medium"
    return "low"


def _severity_fields(severity: float) -> Dict[str, Any]:
    clamped = max(0.0, min(1.0, severity))
    return {"severity": clamped, "severity_label": _severity_label(clamped)}


def _min_confidence(rels: List[Relationship]) -> Optional[float]:
    values = [r.confidence for r in rels if r.confidence is not None]
    return min(values) if values else None


def _evidence_strength(rels: List[Relationship]) -> str:
    source_count = sum(len(r.data_sources or []) for r in rels)
    if source_count == 0:
        return "none"
    if any(r.source_agreement == "low" for r in rels):
        return "low"
    if source_count == 1:
        return "low"
    if source_count == 2:
        return "medium"
    return "high"


def _conflict_detail_text(detail: Any) -> str:
    if isinstance(detail, dict):
        for key in ("description", "summary", "label", "name"):
            if detail.get(key):
                return str(detail[key])
        return ", ".join(f"{k}={v}" for k, v in detail.items())
    return str(detail)


def compute_data_quality(
    relationships: List[Relationship],
    node_lookup: Any,
) -> Dict[str, Any]:
    """
    Summarise the evidential quality of a set of relationships.

    node_lookup is a callable mapping a node id to a Node (or None), used
    only to label the flagged relationships.
    """
    total = len(relationships)

    def describe(rel: Relationship) -> Dict[str, Any]:
        src = node_lookup(rel.source_id)
        tgt = node_lookup(rel.target_id)
        return {
            "id": str(rel.id),
            "source": src.label if src else str(rel.source_id),
            "target": tgt.label if tgt else str(rel.target_id),
            "kind": rel.kind,
            "weight": rel.weight,
            "source_agreement": rel.source_agreement,
        }

    undocumented = [r for r in relationships if not r.data_sources]
    without_ci = [r for r in relationships if not r.confidence_interval]
    without_confidence = [r for r in relationships if r.confidence is None]
    low_agreement = [r for r in relationships if r.source_agreement == "low"]

    by_type: Dict[str, int] = {}
    for rel in relationships:
        key = rel.uncertainty_type or "unspecified"
        by_type[key] = by_type.get(key, 0) + 1

    if total:
        penalties = len(undocumented) + len(without_ci) + len(low_agreement)
        quality_score = max(0.0, 1.0 - penalties / (3.0 * total))
    else:
        quality_score = 1.0

    return {
        "total_relationships": total,
        "with_data_sources": total - len(undocumented),
        "with_confidence_interval": total - len(without_ci),
        "with_confidence": total - len(without_confidence),
        "low_source_agreement": len(low_agreement),
        "quality_score": quality_score,
        "undocumented": [describe(r) for r in undocumented],
        "low_agreement": [describe(r) for r in low_agreement],
        "by_uncertainty_type": by_type,
    }


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
        self._centrality_cache: Dict[str, Dict[uuid.UUID, float]] = {}
        self._loop_participation: Optional[Dict[uuid.UUID, int]] = None

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

    SUPPORTED_CENTRALITY_TYPES = ("betweenness", "closeness", "degree", "eigenvector")

    def get_all_centrality(self, centrality_type: str = "betweenness") -> Dict[uuid.UUID, float]:
        """
        Return the centrality score for every node, computed once per engine instance.

        Unknown centrality_type falls back to betweenness. Eigenvector centrality
        is computed on a simple DiGraph projection (MultiDiGraph is unsupported by
        NetworkX) and returns all zeros if the power iteration fails to converge.
        """
        if centrality_type not in self.SUPPORTED_CENTRALITY_TYPES:
            centrality_type = "betweenness"

        cached = self._centrality_cache.get(centrality_type)
        if cached is not None:
            return cached

        if centrality_type == "closeness":
            scores = nx.closeness_centrality(self.nx_graph)
        elif centrality_type == "degree":
            scores = nx.degree_centrality(self.nx_graph)
        elif centrality_type == "eigenvector":
            simple = nx.DiGraph(self.nx_graph)
            try:
                scores = nx.eigenvector_centrality(simple, max_iter=1000, weight="weight")
            except (nx.PowerIterationFailedConvergence, nx.NetworkXException):
                scores = {n: 0.0 for n in simple.nodes}
        else:
            scores = nx.betweenness_centrality(self.nx_graph)

        result = {node_id: float(score) for node_id, score in scores.items()}
        self._centrality_cache[centrality_type] = result
        return result

    def get_node_centrality(
        self, node_id: uuid.UUID, centrality_type: str = "betweenness"
    ) -> float:
        """Calculate centrality measures for a node."""
        return self.get_all_centrality(centrality_type).get(node_id, 0.0)

    def get_most_central_nodes(
        self,
        node_type: Optional[type] = None,
        centrality_type: str = "betweenness",
        limit: int = 10,
    ) -> List[Tuple[uuid.UUID, float]]:
        """Get the most central nodes by type."""
        all_centralities = self.get_all_centrality(centrality_type)

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

        Uses a 5-method cascade for classification:
        1. Beta model nodes (CeremonialInstrumentalClassification)
        2. Metadata scores (ceremonial_score, instrumental_score)
        2.5. SFMDeliveryCell aggregation (ceremonial_component / instrumental_component
             averaged across all cells whose source_component_id matches the node)
        3. Type-based inference (Institution → ceremonial, Technology → instrumental)
        4. Relationship-based inference (count ceremonial vs instrumental relationship kinds)
        """
        results: Dict[str, List[Node]] = {
            "ceremonial": [],
            "instrumental": [],
            "mixed": []
        }
        unclassified_count = 0

        # Pre-compute cell-level scores per source component from SFMDeliveryCell nodes.
        # Cells store ceremonial_component / instrumental_component directly on the cell;
        # aggregate them to the source component node so the classifier can use them.
        cell_scores: Dict[uuid.UUID, List[Tuple[Optional[float], Optional[float]]]] = {}
        for n in self.graph:
            if isinstance(n, SFMDeliveryCell) and n.source_component_id is not None:
                c = n.ceremonial_component
                i = n.instrumental_component
                if c is not None or i is not None:
                    cell_scores.setdefault(n.source_component_id, []).append((c, i))

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

            # Method 2.5: SFMDeliveryCell scores aggregated to source component nodes.
            # Reads ceremonial_component / instrumental_component from cells whose
            # source_component_id matches this node, then averages them.
            if not score_assigned and node.id in cell_scores:
                pairs = cell_scores[node.id]
                # Average only non-None values per dimension to avoid None -> 0.0 bias
                ceremonial_values = [p[0] for p in pairs if p[0] is not None]
                instrumental_values = [p[1] for p in pairs if p[1] is not None]

                if ceremonial_values or instrumental_values:
                    ceremonial_score = sum(ceremonial_values) / len(ceremonial_values) if ceremonial_values else 0.0
                    instrumental_score = sum(instrumental_values) / len(instrumental_values) if instrumental_values else 0.0
                    score_assigned = True

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
        """Trace circular causation paths starting from a source node (node lists only)."""
        return [
            cycle["nodes"]
            for cycle in self.query_circular_causation_detailed(source_id, max_depth)
        ]

    def query_circular_causation_detailed(
        self, source_id: uuid.UUID, max_depth: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Trace circular causation paths and describe each loop analytically.

        Each returned dict contains:
            nodes            Node objects along the loop (starts and ends at source)
            node_ids, labels Parallel id / label lists
            edges            One descriptor per hop (strongest parallel edge is used)
            length           Number of hops
            gain             Signed product of edge weights (loop gain)
            gain_range       (lower, upper) gain from compounding confidence intervals
            strength         |gain|
            strength_range   (lower, upper) bounds on |gain|
            feedback_type    "reinforcing" (even number of negative links) or "balancing"
            negative_links   Count of negative-weight hops
            confidence       Lowest edge confidence in the loop, or None if none recorded
            weakest_link     Edge with the least evidence (lowest confidence, else lowest |weight|)
            weakest_link_basis  "confidence" or "weight"
            leverage_node    Node in the loop participating in the most loops graph-wide
        """
        if source_id not in self.nx_graph.nodes():
            return []

        id_paths: List[List[uuid.UUID]] = []

        def dfs_paths(current: uuid.UUID, path: List[uuid.UUID], depth: int) -> None:
            if depth > max_depth:
                return
            if len(path) > 2 and current == source_id:
                id_paths.append(path)
                return
            for neighbor in self.nx_graph.neighbors(current):
                if neighbor not in path or (neighbor == source_id and len(path) >= 2):
                    dfs_paths(neighbor, path + [neighbor], depth + 1)

        dfs_paths(source_id, [source_id], 0)

        participation = self.get_loop_participation()
        cycles = []
        for id_path in id_paths:
            described = self._describe_cycle(id_path, participation)
            if described is not None:
                cycles.append(described)
        return cycles

    def _describe_cycle(
        self, id_path: List[uuid.UUID], participation: Dict[uuid.UUID, int]
    ) -> Optional[Dict[str, Any]]:
        nodes = [n for n in (self.graph.get_node_by_id(i) for i in id_path) if n is not None]
        if not nodes:
            return None

        edges = [self._strongest_edge(u, v) for u, v in zip(id_path, id_path[1:])]

        gain = 1.0
        gain_lo = gain_hi = 1.0
        negative_links = 0
        for edge in edges:
            weight = edge["weight"] if edge["weight"] is not None else 1.0
            if weight < 0:
                negative_links += 1
            gain *= weight
            lo, hi = edge["weight_range"]
            products = (gain_lo * lo, gain_lo * hi, gain_hi * lo, gain_hi * hi)
            gain_lo, gain_hi = min(products), max(products)

        strength_lo = 0.0 if gain_lo <= 0.0 <= gain_hi else min(abs(gain_lo), abs(gain_hi))
        strength_hi = max(abs(gain_lo), abs(gain_hi))

        with_confidence = [e for e in edges if e["confidence"] is not None]
        if with_confidence:
            weakest = min(with_confidence, key=lambda e: e["confidence"])
            weakest_basis = "confidence"
        else:
            weakest = min(edges, key=lambda e: abs(e["weight"]) if e["weight"] is not None else 1.0)
            weakest_basis = "weight"

        loop_members = id_path[:-1]
        leverage_id = max(loop_members, key=lambda n: participation.get(n, 0))
        leverage_node = self.graph.get_node_by_id(leverage_id)

        return {
            "nodes": nodes,
            "node_ids": list(id_path),
            "labels": [n.label for n in nodes],
            "edges": edges,
            "length": len(edges),
            "gain": gain,
            "gain_range": (gain_lo, gain_hi),
            "strength": abs(gain),
            "strength_range": (strength_lo, strength_hi),
            "feedback_type": "balancing" if negative_links % 2 else "reinforcing",
            "negative_links": negative_links,
            "confidence": min(e["confidence"] for e in with_confidence) if with_confidence else None,
            "weakest_link": weakest,
            "weakest_link_basis": weakest_basis,
            "leverage_node": {
                "id": leverage_id,
                "label": leverage_node.label if leverage_node else str(leverage_id),
                "loop_participation": participation.get(leverage_id, 0),
            },
        }

    def _strongest_edge(self, source_id: uuid.UUID, target_id: uuid.UUID) -> Dict[str, Any]:
        """Describe the highest-|weight| edge between two nodes, noting how many parallel edges exist."""
        edge_data = self.nx_graph.get_edge_data(source_id, target_id) or {}
        best_key: Any = None
        best_attrs: Dict[str, Any] = {}
        for key, attrs in edge_data.items():
            if not best_attrs or abs(attrs.get("weight", 1.0)) > abs(best_attrs.get("weight", 1.0)):
                best_key, best_attrs = key, attrs

        payload = best_attrs.get("data")
        if isinstance(payload, Relationship):
            weight: Optional[float] = payload.weight if payload.weight is not None else 1.0
            confidence_interval = payload.confidence_interval
            confidence = payload.confidence
            data_sources = list(payload.data_sources or [])
        else:
            weight = best_attrs.get("weight", 1.0)
            confidence_interval = None
            certainties = [
                d.certainty for d in getattr(payload, "deliveries", []) if d.certainty is not None
            ]
            confidence = sum(certainties) / len(certainties) if certainties else None
            data_sources = sorted({
                s for d in getattr(payload, "deliveries", []) for s in (d.data_sources or [])
            })

        return {
            "id": best_key,
            "source_id": source_id,
            "target_id": target_id,
            "kind": best_attrs.get("kind"),
            "weight": weight,
            "weight_range": tuple(confidence_interval) if confidence_interval else (weight, weight),
            "confidence": confidence,
            "data_sources": data_sources,
            "parallel_edges": len(edge_data),
        }

    def get_loop_participation(self, max_cycle_length: int = 8) -> Dict[uuid.UUID, int]:
        """
        Count, for every node, how many simple cycles (up to max_cycle_length) it lies on.

        Nodes on many loops are the system's leverage points: intervening there
        perturbs the most feedback structure. Computed once per engine instance.
        """
        if self._loop_participation is None:
            counts: Dict[uuid.UUID, int] = {n: 0 for n in self.nx_graph.nodes}
            simple = nx.DiGraph(self.nx_graph)
            for cycle in nx.simple_cycles(simple, length_bound=max_cycle_length):
                for node_id in cycle:
                    counts[node_id] += 1
            self._loop_participation = counts
        return self._loop_participation

    def data_quality_report(self) -> Dict[str, Any]:
        """Summarise how well-evidenced the graph's relationships are."""
        return compute_data_quality(
            list(self.graph.relationships.values()),
            self.graph.get_node_by_id,
        )

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
        """
        Detect conflicts and contradictions in the graph.

        Every conflict carries: type (direct/indirect/structural/semantic),
        conflict_type, description, involved_nodes, severity (0-1),
        severity_label (low/medium/high), confidence (lowest recorded on the
        supporting relationships, or None) and evidence_strength
        (none/low/medium/high, from cited data sources and source agreement).
        """
        conflicts: List[Dict[str, Any]] = []

        for node in self.graph:
            if isinstance(node, ConflictDetection):
                conflict_type = node.conflict_type.value if hasattr(node.conflict_type, 'value') else str(node.conflict_type)
                intensities = [v for v in node.conflict_intensity.values() if v is not None]
                base_severity = sum(intensities) / len(intensities) if intensities else 0.6
                involved = [str(node.id)] + ([str(node.analyzed_system_id)] if node.analyzed_system_id else [])

                for direct_conflict in node.direct_conflicts:
                    conflicts.append({
                        "type": "direct",
                        "conflict_type": conflict_type,
                        "details": direct_conflict,
                        "description": _conflict_detail_text(direct_conflict),
                        "source_node": node.id,
                        "involved_nodes": involved,
                        **_severity_fields(base_severity),
                        "confidence": None,
                        "evidence_strength": "none",
                    })

                for indirect_conflict in node.indirect_conflicts:
                    conflicts.append({
                        "type": "indirect",
                        "conflict_type": conflict_type,
                        "details": indirect_conflict,
                        "description": _conflict_detail_text(indirect_conflict),
                        "source_node": node.id,
                        "involved_nodes": involved,
                        **_severity_fields(base_severity * 0.7),
                        "confidence": None,
                        "evidence_strength": "none",
                    })

        # Structural: opposite-signed relationships between the same pair
        relationship_pairs: Dict[Tuple[uuid.UUID, uuid.UUID], List[Relationship]] = {}
        for rel in self.graph.relationships.values():
            relationship_pairs.setdefault((rel.source_id, rel.target_id), []).append(rel)

        for (source, target), rels in relationship_pairs.items():
            if len(rels) > 1:
                weights = [r.weight for r in rels if r.weight is not None]
                if weights and max(weights) > 0 and min(weights) < 0:
                    source_node = self.graph.get_node_by_id(source)
                    target_node = self.graph.get_node_by_id(target)
                    src_label = source_node.label if source_node else str(source)
                    tgt_label = target_node.label if target_node else str(target)
                    conflicts.append({
                        "type": "structural",
                        "conflict_type": "contradictory_relationships",
                        "source": source,
                        "target": target,
                        "details": f"Contradictory relationships between nodes: {weights}",
                        "description": (
                            f"{src_label} → {tgt_label} has both positive and negative "
                            f"relationships (weights {weights})"
                        ),
                        "relationships": [r.id for r in rels],
                        "involved_nodes": [str(source), str(target)],
                        **_severity_fields(min(1.0, (max(weights) - min(weights)) / 2.0)),
                        "confidence": _min_confidence(rels),
                        "evidence_strength": _evidence_strength(rels),
                    })

        # Semantic: relationship kinds that denote opposition
        CONFLICT_KINDS = {
            "conflicts_with", "opposes", "contradicts", "challenges",
            "undermines", "blocks", "resists"
        }

        for rel in self.graph.relationships.values():
            if rel.kind in CONFLICT_KINDS:
                source_node = self.graph.get_node_by_id(rel.source_id)
                target_node = self.graph.get_node_by_id(rel.target_id)
                src_label = source_node.label if source_node else "unknown"
                tgt_label = target_node.label if target_node else "unknown"
                severity = min(1.0, abs(rel.weight)) if rel.weight is not None else 0.5

                conflicts.append({
                    "type": "semantic",
                    "conflict_type": rel.kind,
                    "source": src_label,
                    "source_id": str(rel.source_id),
                    "target": tgt_label,
                    "target_id": str(rel.target_id),
                    "weight": rel.weight,
                    "evidence": rel.meta.get("evidence", "") if rel.meta else "",
                    "relationship_id": str(rel.id),
                    "description": f"{src_label} {rel.kind.replace('_', ' ')} {tgt_label}",
                    "involved_nodes": [str(rel.source_id), str(rel.target_id)],
                    **_severity_fields(severity),
                    "confidence": rel.confidence,
                    "evidence_strength": _evidence_strength([rel]),
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
        """
        Find all simple upstream paths ending at target node.

        Returns a list of paths; each path is an ordered list of relationship IDs
        from the furthest upstream edge to the edge entering target_id. Only edges
        backed by a Relationship (not delivery-cell edges) are followed, since the
        sensitivity calculation varies Relationship.weight.
        """
        if target_id not in self.nx_graph:
            return []

        paths: List[List[uuid.UUID]] = []

        def walk(node: uuid.UUID, path: List[uuid.UUID], visited: set, depth: int) -> None:
            if depth >= max_depth:
                return
            for pred, _, key in self.nx_graph.in_edges(node, keys=True):
                if key not in self.graph.relationships or pred in visited:
                    continue
                new_path = [key] + path
                paths.append(new_path)
                walk(pred, new_path, visited | {pred}, depth + 1)

        walk(target_id, [], {target_id}, 0)
        return paths

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

