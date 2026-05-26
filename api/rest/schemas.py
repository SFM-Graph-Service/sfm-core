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

    model_config = ConfigDict(from_attributes=True)


class RelationshipListResponse(BaseModel):
    """Schema for list of relationships response."""
    relationships: List[RelationshipResponse]
    total: int


# Query Analysis Schemas

class CeremonialAnalysisRequest(BaseModel):
    """Request schema for ceremonial analysis."""
    threshold: float = Field(default=0.5, ge=0.0, le=1.0, description="Ceremonial threshold")


class CeremonialAnalysisResponse(BaseModel):
    """Response schema for ceremonial analysis."""
    ceremonial_nodes: List[uuid.UUID]
    instrumental_nodes: List[uuid.UUID]
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
