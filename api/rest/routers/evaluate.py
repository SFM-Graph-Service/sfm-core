"""Phase 3 evaluation endpoints."""

import uuid
from fastapi import APIRouter, Depends

from api.sfm_service import SFMService
from api.rest.dependencies import get_sfm_service
from api.rest.schemas import (
    DigraphEvaluationRequest,
    EvaluationResponse,
)

router = APIRouter()


@router.post(
    "/digraph",
    response_model=EvaluationResponse,
    summary="Digraph evaluation",
    description="Perform digraph analysis on institutional dependencies"
)
def evaluate_digraph(
    request: DigraphEvaluationRequest,
    service: SFMService = Depends(get_sfm_service)
) -> EvaluationResponse:
    """
    Evaluate institutional digraph.

    Analyzes dependencies, hierarchies, and propagation sequences
    between institutions.

    Args:
        request: List of institution IDs and analysis options

    Returns:
        Digraph analysis results including sequences and dependencies
    """
    result = service.evaluate_digraph(
        institutions=request.institutions,
        analyze_sequences=request.analyze_sequences
    )
    return EvaluationResponse(
        result=result,
        evaluation_type="digraph"
    )


@router.get(
    "/circular-causation/{process_id}",
    response_model=EvaluationResponse,
    summary="Circular causation evaluation",
    description="Analyze circular causation process dynamics"
)
def evaluate_circular_causation(
    process_id: uuid.UUID,
    service: SFMService = Depends(get_sfm_service)
) -> EvaluationResponse:
    """
    Evaluate circular causation process.

    Analyzes feedback loops, reinforcing/balancing dynamics,
    and cumulative causation patterns.

    Args:
        process_id: UUID of CircularCausationProcess

    Returns:
        Process dynamics analysis
    """
    result = service.evaluate_circular_causation(process_id)
    return EvaluationResponse(
        result=result,
        entity_id=process_id,
        evaluation_type="circular_causation"
    )


@router.get(
    "/conflict-detection/{system_id}",
    response_model=EvaluationResponse,
    summary="Conflict detection evaluation",
    description="Detect and analyze system conflicts"
)
def evaluate_conflict_detection(
    system_id: uuid.UUID,
    service: SFMService = Depends(get_sfm_service)
) -> EvaluationResponse:
    """
    Evaluate system conflicts.

    Identifies value conflicts, resource conflicts, and
    institutional contradictions.

    Args:
        system_id: UUID of system to analyze

    Returns:
        Conflict detection and severity analysis
    """
    result = service.evaluate_conflict_detection(system_id)
    return EvaluationResponse(
        result=result,
        entity_id=system_id,
        evaluation_type="conflict_detection"
    )


@router.get(
    "/cross-impact/{cell_id}",
    response_model=EvaluationResponse,
    summary="Cross-impact evaluation",
    description="Analyze cross-impact effects of matrix cell changes"
)
def evaluate_cross_impact(
    cell_id: uuid.UUID,
    service: SFMService = Depends(get_sfm_service)
) -> EvaluationResponse:
    """
    Evaluate cross-impact effects.

    Analyzes how changes in one matrix cell propagate through
    the system affecting other cells.

    Args:
        cell_id: UUID of matrix cell

    Returns:
        Cross-impact propagation analysis
    """
    result = service.evaluate_cross_impact(cell_id)
    return EvaluationResponse(
        result=result,
        entity_id=cell_id,
        evaluation_type="cross_impact"
    )


@router.get(
    "/delivery-performance/{relationship_id}",
    response_model=EvaluationResponse,
    summary="Delivery performance evaluation",
    description="Assess delivery relationship performance"
)
def evaluate_delivery_performance(
    relationship_id: uuid.UUID,
    service: SFMService = Depends(get_sfm_service)
) -> EvaluationResponse:
    """
    Evaluate delivery relationship.

    Assesses performance, efficiency, and bottlenecks in
    delivery relationships.

    Args:
        relationship_id: UUID of DeliveryRelationship

    Returns:
        Performance metrics and bottleneck analysis
    """
    result = service.evaluate_delivery_performance(relationship_id)
    return EvaluationResponse(
        result=result,
        entity_id=relationship_id,
        evaluation_type="delivery_performance"
    )


@router.get(
    "/network-performance/{network_id}",
    response_model=EvaluationResponse,
    summary="Network performance evaluation",
    description="Analyze delivery network performance and health"
)
def evaluate_network_performance(
    network_id: uuid.UUID,
    service: SFMService = Depends(get_sfm_service)
) -> EvaluationResponse:
    """
    Evaluate delivery network.

    Analyzes overall network health, throughput, and
    coordination effectiveness.

    Args:
        network_id: UUID of MatrixDeliveryNetwork

    Returns:
        Network performance and health metrics
    """
    result = service.evaluate_network_performance(network_id)
    return EvaluationResponse(
        result=result,
        entity_id=network_id,
        evaluation_type="network_performance"
    )


@router.get(
    "/path-dependency/{institution_id}",
    response_model=EvaluationResponse,
    summary="Path dependency evaluation",
    description="Analyze path-dependent institutional development"
)
def evaluate_path_dependency(
    institution_id: uuid.UUID,
    service: SFMService = Depends(get_sfm_service)
) -> EvaluationResponse:
    """
    Evaluate path dependency.

    Analyzes how historical choices constrain current options
    and future trajectories.

    Args:
        institution_id: UUID of institution

    Returns:
        Path dependency analysis and lock-in effects
    """
    result = service.evaluate_path_dependency(institution_id)
    return EvaluationResponse(
        result=result,
        entity_id=institution_id,
        evaluation_type="path_dependency"
    )


@router.get(
    "/value-system/{value_system_id}",
    response_model=EvaluationResponse,
    summary="Value system evaluation",
    description="Analyze cultural value system coherence and alignment"
)
def evaluate_value_system(
    value_system_id: uuid.UUID,
    service: SFMService = Depends(get_sfm_service)
) -> EvaluationResponse:
    """
    Evaluate value system.

    Assesses internal coherence, alignment with institutions,
    and cultural stability.

    Args:
        value_system_id: UUID of ValueSystem

    Returns:
        Value system coherence and alignment analysis
    """
    result = service.evaluate_value_system(value_system_id)
    return EvaluationResponse(
        result=result,
        entity_id=value_system_id,
        evaluation_type="value_system"
    )


@router.get(
    "/belief-stability/{belief_id}",
    response_model=EvaluationResponse,
    summary="Belief stability evaluation",
    description="Assess social belief stability and change potential"
)
def evaluate_belief_stability(
    belief_id: uuid.UUID,
    service: SFMService = Depends(get_sfm_service)
) -> EvaluationResponse:
    """
    Evaluate belief stability.

    Analyzes resilience of social beliefs and potential for
    paradigm shifts.

    Args:
        belief_id: UUID of SocialBelief

    Returns:
        Stability metrics and change potential
    """
    result = service.evaluate_belief_stability(belief_id)
    return EvaluationResponse(
        result=result,
        entity_id=belief_id,
        evaluation_type="belief_stability"
    )


@router.get(
    "/attitude-mediation/{attitude_id}",
    response_model=EvaluationResponse,
    summary="Attitude mediation evaluation",
    description="Analyze attitude's capacity to mediate between beliefs and institutions"
)
def evaluate_attitude_mediation(
    attitude_id: uuid.UUID,
    service: SFMService = Depends(get_sfm_service)
) -> EvaluationResponse:
    """
    Evaluate attitude mediation.

    Assesses how cultural attitudes mediate between abstract beliefs
    and concrete institutional practices.

    Args:
        attitude_id: UUID of CulturalAttitude

    Returns:
        Mediation effectiveness analysis
    """
    result = service.evaluate_attitude_mediation(attitude_id)
    return EvaluationResponse(
        result=result,
        entity_id=attitude_id,
        evaluation_type="attitude_mediation"
    )


@router.get(
    "/system-holarchy/{holarchy_id}",
    response_model=EvaluationResponse,
    summary="System holarchy evaluation",
    description="Analyze institutional holarchy coherence and leverage points"
)
def evaluate_system_holarchy(
    holarchy_id: uuid.UUID,
    service: SFMService = Depends(get_sfm_service)
) -> EvaluationResponse:
    """
    Evaluate system holarchy.

    Analyzes nested institutional hierarchies, coherence across levels,
    and identifies system leverage points.

    Args:
        holarchy_id: UUID of InstitutionalHolarchy

    Returns:
        Holarchy coherence and leverage point analysis
    """
    result = service.evaluate_system_holarchy(holarchy_id)
    return EvaluationResponse(
        result=result,
        entity_id=holarchy_id,
        evaluation_type="system_holarchy"
    )
