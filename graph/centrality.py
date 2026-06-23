"""
Network centrality metrics for SFM delivery matrices.

Implements Hayden's network analysis methodology for identifying
institutional power structures and strategic positions within
delivery networks.

Reference:
    Hayden, F.G., Wood, J.C., & Kaya, K. (2002). "Network analysis of
    corporate power: An exploration of the relationship between corporate
    interlocks and the power of the capitalist class."
    Journal of Economic Issues.
"""

from typing import Any, Dict, List, Tuple
import uuid

try:
    import networkx as nx
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "networkx is required for centrality analysis. "
        "Install it with: pip install networkx"
    ) from exc

from models.delivery_matrix import SFMDeliveryMatrix


def compute_centrality_metrics(
    matrix: SFMDeliveryMatrix,
    service: Any,
) -> Dict[str, Dict[str, float]]:
    """
    Compute network centrality metrics for SFM delivery matrix components.

    Builds a directed graph from the delivery matrix where each non-empty
    cell becomes a weighted edge (weight = number of deliveries). Computes
    betweenness, degree, and closeness centrality for all component nodes.

    Args:
        matrix: SFM delivery matrix containing cells and deliveries.
        service: SFMService instance used to resolve node labels.

    Returns:
        Dictionary with three centrality measures, each mapping
        component label to its centrality score::

            {
                'betweenness': {'Director Smith': 0.45, ...},
                'degree':      {'Director Smith': 0.60, ...},
                'closeness':   {'Director Smith': 0.55, ...},
            }
    """
    G: nx.DiGraph = nx.DiGraph()

    # Add all matrix components as nodes
    for component_id in matrix.components:
        node = service.get_node(component_id)
        label = node.label if node is not None else str(component_id)
        G.add_node(component_id, label=label)

    # Add weighted edges from delivery cells
    # Use inverted weight (distance) so more deliveries = shorter path
    for (source_id, target_id), cell in matrix.cells.items():
        delivery_count = len(cell.deliveries)
        if delivery_count > 0:
            # Store both strength and distance
            G.add_edge(
                source_id,
                target_id,
                weight=delivery_count,
                distance=1.0 / delivery_count
            )

    if G.number_of_nodes() == 0:
        return {"betweenness": {}, "degree": {}, "closeness": {}}

    # Use distance for path-based centrality (inverted strength)
    betweenness_by_id = nx.betweenness_centrality(G, weight="distance")
    degree_by_id = nx.degree_centrality(G)
    closeness_by_id = nx.closeness_centrality(G, distance="distance")

    def _label_map(scores_by_id: Dict[uuid.UUID, float]) -> Dict[str, float]:
        result: Dict[str, float] = {}
        for node_id, score in scores_by_id.items():
            label = G.nodes[node_id].get("label", str(node_id))
            result[label] = score
        return result

    return {
        "betweenness": _label_map(betweenness_by_id),
        "degree": _label_map(degree_by_id),
        "closeness": _label_map(closeness_by_id),
    }


def format_centrality_report(
    centrality: Dict[str, Dict[str, float]],
    title: str = "Network Centrality Analysis",
    top_n: int = 5,
) -> str:
    """
    Format centrality metrics as a human-readable report string.

    Args:
        centrality: Output of :func:`compute_centrality_metrics`.
        title: Section heading for the report.
        top_n: Number of top-ranked nodes to display per metric.

    Returns:
        Formatted multi-line string suitable for console output.
    """
    lines: List[str] = []
    lines.append(title)
    lines.append("=" * len(title))

    metric_labels = {
        "betweenness": "Betweenness Centrality (broker/bridge role)",
        "degree": "Degree Centrality (hub connectivity)",
        "closeness": "Closeness Centrality (communication reach)",
    }

    for metric_key, metric_label in metric_labels.items():
        scores = centrality.get(metric_key, {})
        if not scores:
            continue

        lines.append(f"\n{metric_label}:")
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        for rank, (label, score) in enumerate(ranked[:top_n], start=1):
            lines.append(f"  {rank}. {label}: {score:.3f}")

    return "\n".join(lines)


def identify_power_brokers(
    centrality: Dict[str, Dict[str, float]],
    betweenness_threshold: float = 0.1,
) -> List[Tuple[str, float]]:
    """
    Identify nodes with high betweenness centrality (power brokers).

    Nodes above the threshold act as critical bridges or brokers
    within the delivery network, facilitating flows between otherwise
    disconnected components.

    Args:
        centrality: Output of :func:`compute_centrality_metrics`.
        betweenness_threshold: Minimum betweenness score to qualify
            as a power broker (default 0.1).

    Returns:
        List of (label, betweenness_score) tuples sorted descending,
        filtered to scores above *betweenness_threshold*.
    """
    betweenness = centrality.get("betweenness", {})
    brokers = [
        (label, score)
        for label, score in betweenness.items()
        if score >= betweenness_threshold
    ]
    return sorted(brokers, key=lambda x: x[1], reverse=True)
