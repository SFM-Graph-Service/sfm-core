"""Health and statistics endpoints."""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends

from api.sfm_service import SFMService
from api.rest.dependencies import get_sfm_service
from api.rest.schemas import HealthResponse, StatisticsResponse

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Get service health status including node and relationship counts"
)
def get_health(service: SFMService = Depends(get_sfm_service)) -> HealthResponse:
    """
    Check service health and get basic statistics.

    Returns health status with current node and relationship counts.
    """
    health = service.get_health()

    return HealthResponse(
        status=health.status,
        node_count=health.node_count,
        relationship_count=health.relationship_count,
        timestamp=datetime.now(timezone.utc)
    )


@router.get(
    "/statistics",
    response_model=StatisticsResponse,
    summary="Graph statistics",
    description="Get detailed graph statistics including node type breakdown"
)
def get_statistics(service: SFMService = Depends(get_sfm_service)) -> StatisticsResponse:
    """
    Get detailed graph statistics.

    Returns statistics including total nodes, relationships,
    and breakdown by node type.
    """
    stats = service.get_statistics()

    return StatisticsResponse(
        total_nodes=stats.total_nodes,
        total_relationships=stats.total_relationships,
        node_types=stats.node_types
    )
