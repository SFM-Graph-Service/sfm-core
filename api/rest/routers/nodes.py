"""Node CRUD endpoints."""

import uuid
from typing import Optional
from fastapi import APIRouter, Depends, status, Query, HTTPException

from api.sfm_service import SFMService
from api.rest.dependencies import get_sfm_service
from api.rest.schemas import NodeCreate, NodeResponse, NodeListResponse, ClearDataResponse, NodeTypesResponse
from api.rest.node_registry import ALL_NODE_TYPES, is_valid_node_type, get_node_types_by_domain
from models.base_nodes import Node
from models.exceptions import SFMNotFoundError

router = APIRouter()


def _node_to_response(node: Node) -> NodeResponse:
    """
    Convert Node domain model to NodeResponse schema.

    Args:
        node: Domain Node object

    Returns:
        NodeResponse Pydantic model
    """
    return NodeResponse(
        id=node.id,
        label=node.label,
        description=node.description,
        meta=node.meta,
        version=node.version,
        created_at=node.created_at,
        modified_at=node.modified_at,
        node_type=type(node).__name__,
    )


def _create_node_from_schema(node_data: NodeCreate) -> Node:
    """
    Create Node domain model from NodeCreate schema.

    Currently creates basic Node instances. In the future,
    this could be extended to create specialized node types
    based on node_type field.

    Args:
        node_data: NodeCreate Pydantic model

    Returns:
        Node domain object
    """
    # For now, create basic Node objects
    # Future enhancement: Use node_type to create specialized node instances
    return Node(
        label=node_data.label,
        description=node_data.description,
        meta=node_data.meta
    )


# Specific routes first (exact path matches)

@router.post(
    "/",
    response_model=NodeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create node",
    description="Create a new node in the SFM graph"
)
def create_node(
    node_data: NodeCreate,
    service: SFMService = Depends(get_sfm_service)
) -> NodeResponse:
    """
    Create a new node.

    Creates a node with the specified label, description, and metadata.
    Returns the created node with generated ID and timestamps.
    """
    node = _create_node_from_schema(node_data)
    created = service.create_node(node)
    return _node_to_response(created)


@router.get(
    "/",
    response_model=NodeListResponse,
    summary="List nodes",
    description="List all nodes, optionally filtered by type"
)
def list_nodes(
    node_type: Optional[str] = Query(
        None,
        description="Filter by node type (e.g., 'Node', 'PolicyInstrument', 'ValueSystem')"
    ),
    service: SFMService = Depends(get_sfm_service)
) -> NodeListResponse:
    """
    List all nodes.

    Args:
        node_type: Optional node type filter. Must be a valid SFM node type.

    Returns:
        List of nodes and total count

    Raises:
        HTTPException: 400 if node_type is invalid
    """
    # Validate node_type parameter against registry
    if node_type and not is_valid_node_type(node_type):
        raise HTTPException(
            status_code=400,
            detail={
                "error": "VALIDATION_ERROR",
                "message": f"Invalid node_type: '{node_type}'",
                "context": {
                    "invalid_type": node_type,
                    "valid_types_sample": sorted(list(ALL_NODE_TYPES))[:10],
                    "total_valid_types": len(ALL_NODE_TYPES),
                },
                "remediation": "Use GET /api/v1/nodes/types to see all valid node types"
            }
        )

    # Get all nodes from service
    nodes = service.list_nodes()

    # Filter by type if specified and valid
    if node_type:
        nodes = [n for n in nodes if type(n).__name__ == node_type]

    return NodeListResponse(
        nodes=[_node_to_response(n) for n in nodes],
        total=len(nodes)
    )


@router.delete(
    "/clear",
    response_model=ClearDataResponse,
    status_code=status.HTTP_200_OK,
    summary="Clear all data",
    description="Delete all nodes and relationships from the graph"
)
def clear_all_data(
    service: SFMService = Depends(get_sfm_service)
) -> ClearDataResponse:
    """
    Clear all data from the graph.

    WARNING: This operation cannot be undone!

    Returns:
        Success message
    """
    result = service.clear_all_data()
    return ClearDataResponse(**result)


@router.get(
    "/types",
    response_model=NodeTypesResponse,
    summary="List node types",
    description="Get all available node types in the SFM framework"
)
def list_node_types(
    include_domains: bool = Query(
        False,
        description="Include breakdown by domain module"
    )
) -> NodeTypesResponse:
    """
    List all available node types.

    Returns the complete registry of SFM node types, optionally
    organized by domain module.

    Args:
        include_domains: If True, include node types grouped by domain

    Returns:
        List of all node type names and optional domain breakdown
    """
    all_types = sorted(list(ALL_NODE_TYPES))

    if include_domains:
        # Convert sets to sorted lists for JSON serialization
        by_domain = {
            domain: sorted(list(types))
            for domain, types in get_node_types_by_domain().items()
        }
        return NodeTypesResponse(
            node_types=all_types,
            total=len(all_types),
            by_domain=by_domain
        )
    else:
        return NodeTypesResponse(
            node_types=all_types,
            total=len(all_types)
        )


# Parameterized routes last (path parameter matches)

@router.get(
    "/{node_id}",
    response_model=NodeResponse,
    summary="Get node",
    description="Retrieve a node by its ID"
)
def get_node(
    node_id: uuid.UUID,
    service: SFMService = Depends(get_sfm_service)
) -> NodeResponse:
    """
    Get a node by ID.

    Args:
        node_id: UUID of the node to retrieve

    Returns:
        Node data

    Raises:
        SFMNotFoundError: If node with given ID doesn't exist
    """
    node = service.get_node(node_id)
    if node is None:
        raise SFMNotFoundError(entity_type="Node", entity_id=node_id)
    return _node_to_response(node)


@router.put(
    "/{node_id}",
    response_model=NodeResponse,
    summary="Update node",
    description="Update an existing node"
)
def update_node(
    node_id: uuid.UUID,
    node_data: NodeCreate,
    service: SFMService = Depends(get_sfm_service)
) -> NodeResponse:
    """
    Update an existing node.

    Replaces the node's label, description, and metadata with new values.

    Args:
        node_id: UUID of the node to update
        node_data: New node data

    Returns:
        Updated node data

    Raises:
        SFMNotFoundError: If node with given ID doesn't exist
    """
    node = _create_node_from_schema(node_data)
    node.id = node_id
    updated = service.update_node(node)
    return _node_to_response(updated)


@router.delete(
    "/{node_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete node",
    description="Delete a node by its ID"
)
def delete_node(
    node_id: uuid.UUID,
    service: SFMService = Depends(get_sfm_service)
) -> None:
    """
    Delete a node.

    Args:
        node_id: UUID of the node to delete

    Raises:
        SFMNotFoundError: If node with given ID doesn't exist
    """
    success = service.delete_node(node_id)
    if not success:
        raise SFMNotFoundError(entity_type="Node", entity_id=node_id)
