"""Phase 2 query analysis endpoints."""

import uuid
from datetime import timedelta
from fastapi import APIRouter, Depends

from api.sfm_service import SFMService
from api.rest.dependencies import get_sfm_service
from api.rest.schemas import (
    CeremonialAnalysisRequest,
    CeremonialAnalysisResponse,
    CircularCausationResponse,
    HolarchyResponse,
    ConflictsResponse,
    TemporalEvolutionRequest,
    TemporalEvolutionResponse,
    UncertaintyPropagationRequest,
    UncertaintyPropagationResponse,
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


@router.post(
    "/temporal-evolution",
    response_model=TemporalEvolutionResponse,
    summary="Temporal evolution analysis",
    description="Analyze how the system evolved over a time period"
)
def get_temporal_evolution(
    request: TemporalEvolutionRequest,
    service: SFMService = Depends(get_sfm_service)
) -> TemporalEvolutionResponse:
    """
    Analyze temporal evolution of the system.

    Returns snapshots of the system state at regular intervals,
    showing how nodes and relationships changed over time.

    Args:
        request: Start date, end date, and time step parameters

    Returns:
        List of temporal snapshots with network metrics
    """
    service.initialize_query_engine()
    if service._query_engine is None:
        raise RuntimeError("Query engine failed to initialize")
    snapshots = service._query_engine.query_temporal_evolution(
        start_date=request.start_date,
        end_date=request.end_date,
        time_step=timedelta(days=request.time_step_days)
    )
    return TemporalEvolutionResponse(
        snapshots=snapshots,
        start_date=request.start_date,
        end_date=request.end_date,
        time_step_days=request.time_step_days,
        total_snapshots=len(snapshots)
    )


@router.post(
    "/uncertainty-propagation",
    response_model=UncertaintyPropagationResponse,
    summary="Uncertainty propagation analysis",
    description="Propagate uncertainty through a causal pathway"
)
def get_uncertainty_propagation(
    request: UncertaintyPropagationRequest,
    service: SFMService = Depends(get_sfm_service)
) -> UncertaintyPropagationResponse:
    """
    Propagate uncertainty through a causal pathway.

    Calculates how uncertainty compounds through a chain of
    causal relationships, providing confidence intervals for
    the overall pathway effect.

    Args:
        request: Ordered list of node IDs forming the pathway

    Returns:
        Path segments with uncertainty ranges and cumulative effect
    """
    service.initialize_query_engine()
    if service._query_engine is None:
        raise RuntimeError("Query engine failed to initialize")
    result = service._query_engine.propagate_uncertainty_through_path(
        path=request.path
    )
    return UncertaintyPropagationResponse(**result)
