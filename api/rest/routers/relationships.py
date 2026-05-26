"""Relationship CRUD endpoints."""

import uuid
from typing import Optional
from fastapi import APIRouter, Depends, status, Query, HTTPException

from api.sfm_service import SFMService
from api.rest.dependencies import get_sfm_service
from api.rest.schemas import (
    RelationshipCreate,
    RelationshipResponse,
    RelationshipListResponse,
)
from graph.sfm_graph import Relationship
from models.exceptions import SFMNotFoundError

router = APIRouter()


def _relationship_to_response(rel: Relationship) -> RelationshipResponse:
    """
    Convert Relationship domain model to RelationshipResponse schema.

    Args:
        rel: Domain Relationship object

    Returns:
        RelationshipResponse Pydantic model
    """
    return RelationshipResponse(
        id=rel.id,
        source_id=rel.source_id,
        target_id=rel.target_id,
        kind=rel.kind,
        weight=rel.weight,
        meta=rel.meta,
    )


def _create_relationship_from_schema(rel_data: RelationshipCreate) -> Relationship:
    """
    Create Relationship domain model from RelationshipCreate schema.

    Args:
        rel_data: RelationshipCreate Pydantic model

    Returns:
        Relationship domain object
    """
    return Relationship(
        source_id=rel_data.source_id,
        target_id=rel_data.target_id,
        kind=rel_data.kind,
        weight=rel_data.weight,
        meta=rel_data.meta
    )


# Specific routes first

@router.post(
    "/",
    response_model=RelationshipResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create relationship",
    description="Create a new relationship between two nodes"
)
def create_relationship(
    rel_data: RelationshipCreate,
    service: SFMService = Depends(get_sfm_service)
) -> RelationshipResponse:
    """
    Create a new relationship.

    Creates a directed relationship from source node to target node.
    Both nodes must exist before creating the relationship.

    Returns:
        Created relationship with generated ID

    Raises:
        SFMNotFoundError: If source or target node doesn't exist
    """
    relationship = _create_relationship_from_schema(rel_data)
    created = service.create_relationship(relationship)
    return _relationship_to_response(created)


@router.get(
    "/",
    response_model=RelationshipListResponse,
    summary="List relationships",
    description="List all relationships, optionally filtered by kind, source, or target"
)
def list_relationships(
    kind: Optional[str] = Query(
        None,
        description="Filter by relationship kind"
    ),
    source_id: Optional[uuid.UUID] = Query(
        None,
        description="Filter by source node ID"
    ),
    target_id: Optional[uuid.UUID] = Query(
        None,
        description="Filter by target node ID"
    ),
    service: SFMService = Depends(get_sfm_service)
) -> RelationshipListResponse:
    """
    List all relationships.

    Args:
        kind: Optional relationship kind filter
        source_id: Optional source node ID filter
        target_id: Optional target node ID filter

    Returns:
        List of relationships and total count
    """
    # If any filter is provided, use find_relationships
    if kind or source_id or target_id:
        relationships = service.find_relationships(
            source_id=source_id,
            target_id=target_id,
            kind=kind
        )
    else:
        # Otherwise list all
        relationships = service.list_relationships()

    return RelationshipListResponse(
        relationships=[_relationship_to_response(r) for r in relationships],
        total=len(relationships)
    )


# Parameterized routes last

@router.get(
    "/{relationship_id}",
    response_model=RelationshipResponse,
    summary="Get relationship",
    description="Retrieve a relationship by its ID"
)
def get_relationship(
    relationship_id: uuid.UUID,
    service: SFMService = Depends(get_sfm_service)
) -> RelationshipResponse:
    """
    Get a relationship by ID.

    Args:
        relationship_id: UUID of the relationship to retrieve

    Returns:
        Relationship data

    Raises:
        SFMNotFoundError: If relationship with given ID doesn't exist
    """
    relationship = service.get_relationship(relationship_id)
    if relationship is None:
        raise SFMNotFoundError(entity_type="Relationship", entity_id=relationship_id)
    return _relationship_to_response(relationship)


@router.put(
    "/{relationship_id}",
    response_model=RelationshipResponse,
    summary="Update relationship",
    description="Update an existing relationship"
)
def update_relationship(
    relationship_id: uuid.UUID,
    rel_data: RelationshipCreate,
    service: SFMService = Depends(get_sfm_service)
) -> RelationshipResponse:
    """
    Update an existing relationship.

    Replaces the relationship's kind, weight, and metadata with new values.

    Args:
        relationship_id: UUID of the relationship to update
        rel_data: New relationship data

    Returns:
        Updated relationship data

    Raises:
        SFMNotFoundError: If relationship with given ID doesn't exist
    """
    relationship = _create_relationship_from_schema(rel_data)
    relationship.id = relationship_id
    updated = service.update_relationship(relationship)
    return _relationship_to_response(updated)


@router.delete(
    "/{relationship_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete relationship",
    description="Delete a relationship by its ID"
)
def delete_relationship(
    relationship_id: uuid.UUID,
    service: SFMService = Depends(get_sfm_service)
) -> None:
    """
    Delete a relationship.

    Args:
        relationship_id: UUID of the relationship to delete

    Raises:
        SFMNotFoundError: If relationship with given ID doesn't exist
    """
    success = service.delete_relationship(relationship_id)
    if not success:
        raise SFMNotFoundError(entity_type="Relationship", entity_id=relationship_id)
