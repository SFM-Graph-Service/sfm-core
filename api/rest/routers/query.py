"""Phase 2 query analysis endpoints."""

import uuid
from fastapi import APIRouter, Depends

from api.sfm_service import SFMService
from api.rest.dependencies import get_sfm_service
from api.rest.schemas import (
    CeremonialAnalysisRequest,
    CeremonialAnalysisResponse,
    CircularCausationResponse,
    HolarchyResponse,
    ConflictsResponse,
)

router = APIRouter()


@router.post(
    "/ceremonial",
    response_model=CeremonialAnalysisResponse,
    summary="Ceremonial analysis",
    description="Analyze ceremonial vs instrumental behaviors in the system"
)
def get_ceremonial_analysis(
    request: CeremonialAnalysisRequest = CeremonialAnalysisRequest(),
    service: SFMService = Depends(get_sfm_service)
) -> CeremonialAnalysisResponse:
    """
    Analyze ceremonial vs instrumental behaviors.

    Identifies nodes that exhibit ceremonial (status-seeking, traditional)
    vs instrumental (efficiency-seeking, adaptive) behaviors based on
    the specified threshold.

    Args:
        request: Analysis parameters including threshold

    Returns:
        Analysis results with ceremonial/instrumental node lists and ratio
    """
    result = service.get_ceremonial_analysis(threshold=request.threshold)
    return CeremonialAnalysisResponse(**result)


@router.get(
    "/circular-causation/{source_id}",
    response_model=CircularCausationResponse,
    summary="Circular causation analysis",
    description="Identify circular causation patterns from a source node"
)
def get_circular_causation(
    source_id: uuid.UUID,
    service: SFMService = Depends(get_sfm_service)
) -> CircularCausationResponse:
    """
    Identify circular causation patterns.

    Detects feedback loops and circular causation cycles starting from
    the specified source node. Returns reinforcing and balancing loops
    with their strength metrics.

    Args:
        source_id: UUID of the starting node

    Returns:
        List of detected cycles with nodes, strength, and feedback type
    """
    cycles = service.get_circular_causation(source_id)
    return CircularCausationResponse(
        cycles=cycles,
        source_id=source_id
    )


@router.get(
    "/holarchy/{institution_id}",
    response_model=HolarchyResponse,
    summary="Institutional holarchy",
    description="Get nested institutional hierarchy for an institution"
)
def get_holarchy(
    institution_id: uuid.UUID,
    service: SFMService = Depends(get_sfm_service)
) -> HolarchyResponse:
    """
    Get institutional holarchy.

    Returns the nested hierarchical structure of institutions,
    showing parent-child relationships and organizational layers.

    Args:
        institution_id: UUID of the institution node

    Returns:
        Holarchy structure with layers, relationships, and depth
    """
    result = service.get_holarchy(institution_id)
    return HolarchyResponse(**result)


@router.get(
    "/conflicts",
    response_model=ConflictsResponse,
    summary="Conflict detection",
    description="Detect value and resource conflicts in the system"
)
def get_conflicts(
    service: SFMService = Depends(get_sfm_service)
) -> ConflictsResponse:
    """
    Detect system conflicts.

    Identifies value conflicts, resource conflicts, and institutional
    conflicts within the socio-economic system. Returns conflicts with
    severity ratings and involved nodes.

    Returns:
        List of detected conflicts with type, severity, and description
    """
    conflicts = service.get_conflicts()
    return ConflictsResponse(
        conflicts=conflicts,
        total=len(conflicts)
    )
