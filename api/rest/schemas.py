"""Pydantic schemas for REST API request/response models."""

import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict


# Health & Statistics Schemas

class HealthResponse(BaseModel):
    """Health check response schema."""
    status: str
    node_count: int
    relationship_count: int
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


class StatisticsResponse(BaseModel):
    """Graph statistics response schema."""
    total_nodes: int
    total_relationships: int
    node_types: Dict[str, int]

    model_config = ConfigDict(from_attributes=True)


# Node CRUD Schemas

class NodeCreate(BaseModel):
    """Schema for creating a new node."""
    label: str = Field(..., description="Node label/name")
    description: Optional[str] = Field(None, description="Optional description")
    meta: Dict[str, str] = Field(default_factory=dict, description="Metadata key-value pairs")
    node_type: str = Field(default="Node", description="Node type class name")
    type_fields: Optional[Dict[str, Any]] = Field(None, description="Type-specific fields")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "label": "Agricultural Subsidy Program",
                "description": "Federal program providing subsidies to farmers",
                "node_type": "Institution",
                "meta": {"source": "USDA", "year": "2024"}
            }
        }
    )


class NodeUpdate(BaseModel):
    """Schema for updating an existing node."""
    label: Optional[str] = Field(None, description="Updated label")
    description: Optional[str] = Field(None, description="Updated description")
    meta: Optional[Dict[str, str]] = Field(None, description="Updated metadata")
    type_fields: Optional[Dict[str, Any]] = Field(None, description="Updated type-specific fields")


class NodeResponse(BaseModel):
    """Schema for node response."""
    id: uuid.UUID
    label: str
    description: Optional[str]
    meta: Dict[str, str]
    version: int
    created_at: datetime
    modified_at: Optional[datetime]
    node_type: str

    model_config = ConfigDict(from_attributes=True)


class NodeListResponse(BaseModel):
    """Schema for list of nodes response."""
    nodes: List[NodeResponse]
    total: int


class ClearDataResponse(BaseModel):
    """Schema for clear all data response."""
    status: str
    message: str


class NodeTypesResponse(BaseModel):
    """Schema for node types registry response."""
    node_types: List[str]
    total: int
    by_domain: Optional[Dict[str, List[str]]] = None


# Relationship CRUD Schemas

class RelationshipCreate(BaseModel):
    """Schema for creating a new relationship."""
    source_id: uuid.UUID = Field(..., description="Source node ID")
    target_id: uuid.UUID = Field(..., description="Target node ID")
    kind: str = Field(default="", description="Relationship kind/type")
    weight: Optional[float] = Field(None, description="Optional relationship weight")
    meta: Dict[str, Any] = Field(default_factory=dict, description="Metadata key-value pairs")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "source_id": "123e4567-e89b-12d3-a456-426614174000",
                "target_id": "123e4567-e89b-12d3-a456-426614174001",
                "kind": "influences",
                "weight": 0.8,
                "meta": {"strength": "high"}
            }
        }
    )


class RelationshipResponse(BaseModel):
    """Schema for relationship response."""
    id: uuid.UUID
    source_id: uuid.UUID
    target_id: uuid.UUID
    kind: str
    weight: Optional[float]
    meta: Dict[str, Any]

    # Temporal fields
    created_at: Optional[datetime] = None
    modified_at: Optional[datetime] = None
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    version: int = 1
    previous_version_id: Optional[uuid.UUID] = None

    # Uncertainty fields
    confidence: Optional[float] = None
    confidence_interval: Optional[tuple[float, float]] = None
    uncertainty_type: Optional[str] = None
    data_sources: List[str] = Field(default_factory=list)
    source_agreement: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class RelationshipListResponse(BaseModel):
    """Schema for list of relationships response."""
    relationships: List[RelationshipResponse]
    total: int


# Query Analysis Schemas

class NodeSummary(BaseModel):
    """Summary information for a node."""
    id: uuid.UUID
    label: str
    node_type: str


class CeremonialAnalysisRequest(BaseModel):
    """Request schema for ceremonial analysis."""
    threshold: float = Field(default=0.5, ge=0.0, le=1.0, description="Ceremonial threshold")


class CeremonialAnalysisResponse(BaseModel):
    """Response schema for ceremonial analysis."""
    ceremonial_nodes: List[NodeSummary]
    instrumental_nodes: List[NodeSummary]
    ceremonial_ratio: float
    threshold: float


class CircularCausationResponse(BaseModel):
    """Response schema for circular causation analysis."""
    cycles: List[Dict[str, Any]]
    source_id: uuid.UUID


class HolarchyResponse(BaseModel):
    """Response schema for holarchy analysis."""
    institution_id: uuid.UUID
    layers: List[Dict[str, Any]]
    relationships: List[Dict[str, Any]]
    depth: int


class ConflictsResponse(BaseModel):
    """Response schema for conflicts detection."""
    conflicts: List[Dict[str, Any]]
    total: int


class TemporalEvolutionRequest(BaseModel):
    """Request schema for temporal evolution analysis."""
    start_date: datetime = Field(..., description="Start date for temporal analysis")
    end_date: datetime = Field(..., description="End date for temporal analysis")
    time_step_days: int = Field(default=365, description="Time step in days (default: 365 = 1 year)")


class TemporalEvolutionResponse(BaseModel):
    """Response schema for temporal evolution analysis."""
    snapshots: List[Dict[str, Any]]
    start_date: datetime
    end_date: datetime
    time_step_days: int
    total_snapshots: int


class UncertaintyPropagationRequest(BaseModel):
    """Request schema for uncertainty propagation analysis."""
    path: List[uuid.UUID] = Field(..., description="Ordered list of node IDs forming causal pathway")


class UncertaintyPropagationResponse(BaseModel):
    """Response schema for uncertainty propagation analysis."""
    path_segments: List[Dict[str, Any]]
    cumulative_effect: float
    uncertainty_range: tuple[float, float]
    uncertainty_width: float


# Evaluation Schemas

class DigraphEvaluationRequest(BaseModel):
    """Request schema for digraph evaluation."""
    institutions: List[uuid.UUID] = Field(..., description="List of institution IDs to analyze")
    analyze_sequences: bool = Field(default=True, description="Whether to analyze sequences")


class EvaluationResponse(BaseModel):
    """Generic evaluation response schema."""
    result: Dict[str, Any]
    entity_id: Optional[uuid.UUID] = None
    evaluation_type: str


# Error Response Schema

class ErrorResponse(BaseModel):
    """Error response schema."""
    error: str
    message: str
    context: Dict[str, Any]
    remediation: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime
