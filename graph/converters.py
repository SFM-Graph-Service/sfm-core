"""
Bidirectional conversion between delivery matrices and digraphs.

Enables Hayden's matrix-digraph duality: the same SFM can be represented
either as an N×N matrix or as a directed graph with labeled edges.

Reference:
    Hayden (2006): "The quality of the solution set in social economics"
    - Discusses matrix-digraph equivalence for SFM analysis
"""

from typing import Any, Optional
import uuid

import networkx as nx

from models.delivery_matrix import Delivery, SFMDeliveryMatrix


def to_multidigraph(
    matrix: SFMDeliveryMatrix,
    service: Any  # SFMService
) -> nx.MultiDiGraph:
    """
    Convert delivery matrix to NetworkX MultiDiGraph.

    Each component becomes a node, each delivery becomes a labeled edge.
    Preserves all delivery metadata as edge attributes.

    Args:
        matrix: SFMDeliveryMatrix to convert
        service: SFMService for reading component labels

    Returns:
        NetworkX MultiDiGraph with deliveries as edges

    Example:
        >>> G = to_multidigraph(matrix, service)
        >>> G.nodes()
        NodeView((...))
        >>> G.edges(data=True, keys=True)
        OutMultiEdgeDataView([(...)])
    """
    G = nx.MultiDiGraph()

    # Add nodes for components
    for comp_id in matrix.components:
        node = service.repository.read_node(comp_id)
        if node:
            G.add_node(
                comp_id,
                label=node.label,
                description=node.description if hasattr(node, 'description') else ""
            )
        else:
            G.add_node(comp_id, label=str(comp_id))

    # Add edges for deliveries
    for (src_id, tgt_id), cell in matrix.cells.items():
        if not cell.deliveries:
            continue

        for delivery in cell.deliveries:
            # Use delivery type as edge key for MultiDiGraph
            G.add_edge(
                src_id,
                tgt_id,
                key=delivery.delivery_type,
                delivery_content=delivery.delivery_content,
                quantity=delivery.quantity,
                units=delivery.units,
                temporal_rate=delivery.temporal_rate,
                temporal_clock=delivery.temporal_clock,
                threshold=delivery.threshold,
                threshold_direction=delivery.threshold_direction,
                certainty=delivery.certainty,
                data_sources=delivery.data_sources,
                cell_description=cell.cell_description
            )

    # Store matrix metadata as graph attributes
    G.graph['matrix_label'] = matrix.label
    G.graph['matrix_description'] = matrix.description if hasattr(matrix, 'description') else ""
    G.graph['matrix_scope'] = matrix.matrix_scope
    G.graph['matrix_id'] = str(matrix.id)

    return G


def from_multidigraph(
    G: nx.MultiDiGraph,
    service: Any,  # SFMService
    matrix_label: Optional[str] = None,
    matrix_description: Optional[str] = None
) -> SFMDeliveryMatrix:
    """
    Reconstruct delivery matrix from NetworkX MultiDiGraph.

    Groups edges by (source, target) into cells with multiple deliveries.

    Args:
        G: NetworkX MultiDiGraph with deliveries as edges
        service: SFMService for creating matrix
        matrix_label: Optional label (uses graph attribute if not provided)
        matrix_description: Optional description (uses graph attribute if not provided)

    Returns:
        SFMDeliveryMatrix reconstructed from graph

    Example:
        >>> matrix = from_multidigraph(G, service)
        >>> len(matrix.components)
        5
    """
    # Get matrix metadata from graph attributes or parameters
    label = matrix_label or G.graph.get('matrix_label', 'Reconstructed Matrix')
    description = matrix_description or G.graph.get('matrix_description', '')
    matrix_scope = G.graph.get('matrix_scope')

    # Create matrix
    matrix = service.create_delivery_matrix(
        label=label,
        description=description,
        matrix_scope=matrix_scope
    )

    # Add components (nodes)
    for node_id in G.nodes():
        if isinstance(node_id, uuid.UUID):
            matrix.add_component(node_id)
        else:
            # If node_id is not UUID, might need conversion
            # For now, assume UUIDs
            pass

    # Group edges by (source, target) to reconstruct cells
    cells_dict = {}  # (src, tgt) -> list of deliveries

    for src, tgt, key, data in G.edges(data=True, keys=True):
        # Reconstruct delivery from edge attributes
        delivery = Delivery(
            delivery_type=key,  # Edge key is delivery type
            delivery_content=data.get('delivery_content', ''),
            quantity=data.get('quantity'),
            units=data.get('units'),
            temporal_rate=data.get('temporal_rate'),
            temporal_clock=data.get('temporal_clock'),
            threshold=data.get('threshold'),
            threshold_direction=data.get('threshold_direction'),
            certainty=data.get('certainty'),
            data_sources=data.get('data_sources', [])
        )

        cell_key = (src, tgt)
        if cell_key not in cells_dict:
            cells_dict[cell_key] = {
                'deliveries': [],
                'cell_description': data.get('cell_description', '')
            }

        cells_dict[cell_key]['deliveries'].append(delivery)

    # Add cells to matrix
    for (src_id, tgt_id), cell_data in cells_dict.items():
        # Add deliveries to matrix
        for delivery in cell_data['deliveries']:
            service.add_delivery_to_matrix(
                matrix,
                src_id,
                tgt_id,
                delivery,
                cell_description=cell_data['cell_description']
            )

    return matrix


def matrix_to_adjacency_dict(
    matrix: SFMDeliveryMatrix,
    service: Any  # SFMService
) -> dict:
    """
    Convert matrix to adjacency dictionary representation.

    Args:
        matrix: SFMDeliveryMatrix to convert
        service: SFMService for reading component labels

    Returns:
        Dictionary mapping source -> target -> list of deliveries

    Example:
        >>> adj = matrix_to_adjacency_dict(matrix, service)
        >>> adj[legislature_id][school_district_id]
        [<Delivery money>, <Delivery rule>]
    """
    adj = {}

    for comp_id in matrix.components:
        adj[comp_id] = {}

    for (src_id, tgt_id), cell in matrix.cells.items():
        if cell.deliveries:
            adj[src_id][tgt_id] = cell.deliveries

    return adj


def adjacency_dict_to_matrix(
    adj: dict,
    service: Any,  # SFMService
    label: str = "Matrix from Adjacency",
    description: str = ""
) -> SFMDeliveryMatrix:
    """
    Create matrix from adjacency dictionary.

    Args:
        adj: Dictionary mapping source -> target -> list of deliveries
        service: SFMService for creating matrix
        label: Matrix label
        description: Matrix description

    Returns:
        SFMDeliveryMatrix created from adjacency dictionary
    """
    # Get all component IDs
    all_components = set(adj.keys())
    for targets in adj.values():
        all_components.update(targets.keys())

    # Create matrix
    matrix = service.create_delivery_matrix(
        label=label,
        description=description,
        components=list(all_components)
    )

    # Add deliveries
    for src_id, targets in adj.items():
        for tgt_id, deliveries in targets.items():
            if deliveries:
                for delivery in deliveries:
                    # Generate cell description from first delivery if needed
                    cell_description = f"Deliveries from {src_id} to {tgt_id}"
                    service.add_delivery_to_matrix(
                        matrix,
                        src_id,
                        tgt_id,
                        delivery,
                        cell_description=cell_description
                    )

    return matrix


def get_delivery_summary(matrix: SFMDeliveryMatrix) -> dict:
    """
    Get summary statistics for delivery matrix.

    Args:
        matrix: SFMDeliveryMatrix to summarize

    Returns:
        Dictionary with summary statistics

    Example:
        >>> summary = get_delivery_summary(matrix)
        >>> summary['total_deliveries']
        9
        >>> summary['deliveries_by_type']
        {'money': 4, 'rule': 1, 'authority': 2, 'information': 1, 'energy': 1}
    """
    summary = {
        'components': len(matrix.components),
        'non_empty_cells': len(matrix.get_non_empty_cells()),
        'total_cells': len(matrix.cells),
        'total_deliveries': 0,
        'deliveries_by_type': {},
        'cells_with_multiple_deliveries': 0,
        'quantified_deliveries': 0,
        'cells_with_descriptions': 0
    }

    for cell in matrix.cells.values():
        if cell.deliveries:
            summary['total_deliveries'] += len(cell.deliveries)

            if len(cell.deliveries) > 1:
                summary['cells_with_multiple_deliveries'] += 1

            if cell.cell_description:
                summary['cells_with_descriptions'] += 1

            for delivery in cell.deliveries:
                dtype = delivery.delivery_type
                summary['deliveries_by_type'][dtype] = summary['deliveries_by_type'].get(dtype, 0) + 1

                if delivery.quantity is not None:
                    summary['quantified_deliveries'] += 1

    return summary
