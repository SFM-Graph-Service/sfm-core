# SFM Core REST API Documentation

Production-ready REST API for the Social Fabric Matrix (SFM) Core framework, providing HTTP access to modeling, analyzing, and querying complex socio-economic systems.

## Table of Contents

- [Quick Start](#quick-start)
- [API Overview](#api-overview)
- [Authentication](#authentication)
- [Health & Diagnostics](#health--diagnostics)
- [Node CRUD Operations](#node-crud-operations)
- [Query Analysis (Phase 2)](#query-analysis-phase-2)
- [Evaluation (Phase 3)](#evaluation-phase-3)
- [Error Handling](#error-handling)
- [OpenAPI Documentation](#openapi-documentation)

## Quick Start

### Start the Development Server

```bash
# With NetworkX backend (in-memory)
uvicorn api.rest.app:app --reload

# Access interactive docs
open http://localhost:8000/api/v1/docs
```

### Using Docker

```bash
# Development with NetworkX
docker-compose up api-dev

# Production-like with Neo4j
docker-compose up api-neo4j neo4j
```

## API Overview

**Base URL**: `http://localhost:8000/api/v1`

**Content-Type**: `application/json`

**Response Format**: All responses are JSON with consistent structure

**HTTP Methods**:
- `GET` - Retrieve resources
- `POST` - Create resources or trigger analysis
- `PUT` - Update resources
- `DELETE` - Remove resources

## Authentication

Current version does not require authentication. Future versions will support API key and OAuth2 authentication.

## Health & Diagnostics

### Get Health Status

```http
GET /api/v1/health
```

**Response** (200 OK):
```json
{
  "status": "healthy",
  "node_count": 150,
  "relationship_count": 320,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Get Graph Statistics

```http
GET /api/v1/statistics
```

**Response** (200 OK):
```json
{
  "total_nodes": 150,
  "total_relationships": 320,
  "node_types": {
    "Actor": 45,
    "Institution": 30,
    "Technology": 25,
    "Resource": 20,
    "Node": 30
  }
}
```

## Node CRUD Operations

### Create Node

```http
POST /api/v1/nodes/
Content-Type: application/json

{
  "label": "Agricultural Subsidy Program",
  "description": "Federal program providing subsidies to farmers",
  "node_type": "Institution",
  "meta": {
    "source": "USDA",
    "year": "2024"
  }
}
```

**Response** (201 Created):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "label": "Agricultural Subsidy Program",
  "description": "Federal program providing subsidies to farmers",
  "meta": {
    "source": "USDA",
    "year": "2024"
  },
  "version": 1,
  "created_at": "2024-01-15T10:30:00Z",
  "modified_at": null,
  "node_type": "Institution"
}
```

### Get Node by ID

```http
GET /api/v1/nodes/{node_id}
```

**Response** (200 OK):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "label": "Agricultural Subsidy Program",
  "description": "Federal program providing subsidies to farmers",
  "meta": {"source": "USDA", "year": "2024"},
  "version": 1,
  "created_at": "2024-01-15T10:30:00Z",
  "modified_at": null,
  "node_type": "Institution"
}
```

**Response** (404 Not Found):
```json
{
  "error": "NOT_FOUND_ERROR",
  "message": "Node with ID 550e8400-e29b-41d4-a716-446655440000 not found",
  "context": {
    "entity_type": "Node",
    "entity_id": "550e8400-e29b-41d4-a716-446655440000"
  },
  "timestamp": "2024-01-15T10:35:00Z"
}
```

### List All Nodes

```http
GET /api/v1/nodes/
GET /api/v1/nodes/?node_type=Actor
```

**Response** (200 OK):
```json
{
  "nodes": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "label": "Agricultural Subsidy Program",
      "description": "Federal program providing subsidies to farmers",
      "meta": {"source": "USDA", "year": "2024"},
      "version": 1,
      "created_at": "2024-01-15T10:30:00Z",
      "modified_at": null,
      "node_type": "Institution"
    }
  ],
  "total": 1
}
```

### Update Node

```http
PUT /api/v1/nodes/{node_id}
Content-Type: application/json

{
  "label": "Updated Agricultural Subsidy Program",
  "description": "Expanded federal program",
  "node_type": "Institution",
  "meta": {
    "source": "USDA",
    "year": "2024",
    "status": "active"
  }
}
```

**Response** (200 OK):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "label": "Updated Agricultural Subsidy Program",
  "description": "Expanded federal program",
  "meta": {
    "source": "USDA",
    "year": "2024",
    "status": "active"
  },
  "version": 2,
  "created_at": "2024-01-15T10:30:00Z",
  "modified_at": "2024-01-15T11:00:00Z",
  "node_type": "Institution"
}
```

### Delete Node

```http
DELETE /api/v1/nodes/{node_id}
```

**Response** (204 No Content)

### Clear All Data

**⚠️ WARNING: This operation cannot be undone!**

```http
DELETE /api/v1/nodes/clear
```

**Response** (200 OK):
```json
{
  "status": "success",
  "message": "All data cleared"
}
```

### List Node Types

Get all available node types in the SFM framework.

```http
GET /api/v1/nodes/types
GET /api/v1/nodes/types?include_domains=true
```

**Response** (200 OK) - Basic:
```json
{
  "node_types": [
    "CeremonialInstrumentalClassification",
    "CircularCausationProcess",
    "CommonsGovernance",
    "ConflictDetection",
    "CoordinationMechanism",
    "CrossImpactAnalysis",
    "CulturalAttitude",
    "DatabaseIntegrationCapability",
    "DeliveryRelationship",
    "DigraphAnalysis",
    "EcologicalSystem",
    "EvolutionaryPathway",
    "InstitutionalHolarchy",
    "InstitutionalStructure",
    "InstrumentalistInquiryFramework",
    "MatrixCell",
    "MatrixDeliveryNetwork",
    "Node",
    "NormativeSystemsAnalysis",
    "PathDependencyAnalysis",
    "PolicyInstrument",
    "PolicyRelevanceIntegration",
    "ProblemSolvingSequence",
    "SFMCriteria",
    "SFMMatrix",
    "Scenario",
    "ScenarioPath",
    "ScenarioSet",
    "SocialBelief",
    "SocialCost",
    "SocialFabricIndicator",
    "SocialIndicatorSystem",
    "SocialProvisioningMatrix",
    "SocialValueAssessment",
    "SystemLevelAnalysis",
    "SystemProperty",
    "ToolSkillTechnologyComplex",
    "TransactionCost",
    "ValueJudgment",
    "ValueSystem"
  ],
  "total": 40,
  "by_domain": null
}
```

**Response** (200 OK) - With Domains:
```json
{
  "node_types": ["..."],
  "total": 40,
  "by_domain": {
    "base": ["Node"],
    "complex_analysis": [
      "CircularCausationProcess",
      "ConflictDetection",
      "DigraphAnalysis"
    ],
    "cultural_analysis": [
      "CeremonialInstrumentalClassification",
      "CulturalAttitude",
      "SocialBelief",
      "ValueSystem"
    ],
    "economic_analysis": [
      "CommonsGovernance",
      "CoordinationMechanism",
      "TransactionCost"
    ],
    "institutional_analysis": [
      "InstitutionalStructure",
      "PathDependencyAnalysis"
    ],
    "matrix_components": [
      "MatrixCell",
      "SFMCriteria",
      "SFMMatrix"
    ],
    "meta_entities": [
      "Scenario",
      "ScenarioPath",
      "ScenarioSet"
    ],
    "methodological_framework": [
      "DatabaseIntegrationCapability",
      "InstrumentalistInquiryFramework",
      "NormativeSystemsAnalysis",
      "PolicyRelevanceIntegration"
    ],
    "network_analysis": [
      "CrossImpactAnalysis",
      "DeliveryRelationship",
      "MatrixDeliveryNetwork"
    ],
    "policy_framework": [
      "PolicyInstrument",
      "ProblemSolvingSequence",
      "ValueJudgment"
    ],
    "social_assessment": [
      "SocialCost",
      "SocialFabricIndicator",
      "SocialValueAssessment"
    ],
    "specialized_components": [
      "EvolutionaryPathway",
      "SocialIndicatorSystem",
      "SocialProvisioningMatrix"
    ],
    "system_analysis": [
      "InstitutionalHolarchy",
      "SystemLevelAnalysis",
      "SystemProperty"
    ],
    "technology_integration": [
      "EcologicalSystem",
      "ToolSkillTechnologyComplex"
    ]
  }
}
```

**Use Case**: Query this endpoint before filtering nodes by type to see all available types.

## Query Analysis (Phase 2)

### Ceremonial Analysis

Identify ceremonial (status-seeking) vs instrumental (efficiency-seeking) behaviors.

```http
POST /api/v1/query/ceremonial
Content-Type: application/json

{
  "threshold": 0.5
}
```

**Response** (200 OK):
```json
{
  "ceremonial_nodes": [
    "550e8400-e29b-41d4-a716-446655440000",
    "660e8400-e29b-41d4-a716-446655440001"
  ],
  "instrumental_nodes": [
    "770e8400-e29b-41d4-a716-446655440002"
  ],
  "ceremonial_ratio": 0.67,
  "threshold": 0.5
}
```

### Circular Causation

Detect feedback loops and circular causation patterns.

```http
GET /api/v1/query/circular-causation/{source_id}
```

**Response** (200 OK):
```json
{
  "cycles": [
    {
      "nodes": [
        "550e8400-e29b-41d4-a716-446655440000",
        "660e8400-e29b-41d4-a716-446655440001",
        "770e8400-e29b-41d4-a716-446655440002"
      ],
      "strength": 0.8,
      "feedback_type": "reinforcing"
    },
    {
      "nodes": [
        "880e8400-e29b-41d4-a716-446655440003",
        "990e8400-e29b-41d4-a716-446655440004"
      ],
      "strength": 0.6,
      "feedback_type": "balancing"
    }
  ],
  "source_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### Institutional Holarchy

Analyze nested institutional hierarchies.

```http
GET /api/v1/query/holarchy/{institution_id}
```

**Response** (200 OK):
```json
{
  "institution_id": "550e8400-e29b-41d4-a716-446655440000",
  "layers": [
    {
      "level": 0,
      "institutions": ["550e8400-e29b-41d4-a716-446655440000"]
    },
    {
      "level": 1,
      "institutions": [
        "660e8400-e29b-41d4-a716-446655440001",
        "770e8400-e29b-41d4-a716-446655440002"
      ]
    }
  ],
  "relationships": [
    {
      "parent": "550e8400-e29b-41d4-a716-446655440000",
      "child": "660e8400-e29b-41d4-a716-446655440001",
      "type": "governs"
    }
  ],
  "depth": 2
}
```

### Conflict Detection

Identify value, resource, and institutional conflicts.

```http
GET /api/v1/query/conflicts
```

**Response** (200 OK):
```json
{
  "conflicts": [
    {
      "conflict_type": "value",
      "nodes": [
        "550e8400-e29b-41d4-a716-446655440000",
        "660e8400-e29b-41d4-a716-446655440001"
      ],
      "severity": 0.8,
      "description": "Conflicting value orientations between institutions"
    },
    {
      "conflict_type": "resource",
      "nodes": [
        "770e8400-e29b-41d4-a716-446655440002",
        "880e8400-e29b-41d4-a716-446655440003"
      ],
      "severity": 0.6,
      "description": "Resource allocation conflict"
    }
  ],
  "total": 2
}
```

## Evaluation (Phase 3)

### Digraph Evaluation

Analyze institutional dependencies and hierarchies.

```http
POST /api/v1/evaluate/digraph
Content-Type: application/json

{
  "institutions": [
    "550e8400-e29b-41d4-a716-446655440000",
    "660e8400-e29b-41d4-a716-446655440001",
    "770e8400-e29b-41d4-a716-446655440002"
  ],
  "analyze_sequences": true
}
```

**Response** (200 OK):
```json
{
  "result": {
    "dependencies": {
      "direct": 5,
      "transitive": 12
    },
    "sequences": [
      {
        "path": ["550e...", "660e...", "770e..."],
        "length": 3
      }
    ],
    "hierarchy_depth": 3
  },
  "evaluation_type": "digraph"
}
```

### Circular Causation Evaluation

```http
GET /api/v1/evaluate/circular-causation/{process_id}
```

**Response** (200 OK):
```json
{
  "result": {
    "feedback_loops": [
      {"type": "reinforcing", "strength": 0.8},
      {"type": "balancing", "strength": 0.6}
    ],
    "cumulative_effect": 0.7
  },
  "entity_id": "550e8400-e29b-41d4-a716-446655440000",
  "evaluation_type": "circular_causation"
}
```

### Other Evaluation Endpoints

All evaluation endpoints follow the same pattern:

- `GET /api/v1/evaluate/conflict-detection/{system_id}`
- `GET /api/v1/evaluate/cross-impact/{cell_id}`
- `GET /api/v1/evaluate/delivery-performance/{relationship_id}`
- `GET /api/v1/evaluate/network-performance/{network_id}`
- `GET /api/v1/evaluate/path-dependency/{institution_id}`
- `GET /api/v1/evaluate/value-system/{value_system_id}`
- `GET /api/v1/evaluate/belief-stability/{belief_id}`
- `GET /api/v1/evaluate/attitude-mediation/{attitude_id}`
- `GET /api/v1/evaluate/system-holarchy/{holarchy_id}`

Each returns:
```json
{
  "result": { /* evaluation-specific data */ },
  "entity_id": "uuid-string",
  "evaluation_type": "evaluation_name"
}
```

## Error Handling

All errors follow a consistent structure leveraging the SFM error framework.

### Error Response Format

```json
{
  "error": "ERROR_CODE",
  "message": "Human-readable error message",
  "context": {
    "entity_type": "Node",
    "entity_id": "550e8400-e29b-41d4-a716-446655440000"
  },
  "remediation": "Suggested fix or next steps",
  "timestamp": "2024-01-15T10:35:00Z"
}
```

### HTTP Status Codes

| Status Code | Error Type | Description |
|-------------|------------|-------------|
| 400 | VALIDATION_ERROR | Invalid request data |
| 404 | NOT_FOUND_ERROR | Resource not found |
| 409 | INTEGRITY_ERROR | Data integrity violation |
| 422 | Unprocessable Entity | Request validation failed (Pydantic) |
| 500 | QUERY_EXECUTION_ERROR | Internal query failure |
| 503 | DATABASE_CONNECTION_ERROR | Database unavailable |

### Example Error Responses

**404 Not Found**:
```json
{
  "error": "NOT_FOUND_ERROR",
  "message": "Node with ID 550e8400-e29b-41d4-a716-446655440000 not found",
  "context": {
    "entity_type": "Node",
    "entity_id": "550e8400-e29b-41d4-a716-446655440000"
  },
  "remediation": "Verify the node ID exists using GET /api/v1/nodes/",
  "timestamp": "2024-01-15T10:35:00Z"
}
```

**400 Validation Error** (Threshold):
```json
{
  "error": "VALIDATION_ERROR",
  "message": "Threshold must be between 0.0 and 1.0",
  "context": {
    "field": "threshold",
    "value": 1.5
  },
  "remediation": "Set threshold to a value between 0.0 and 1.0",
  "timestamp": "2024-01-15T10:35:00Z"
}
```

**400 Invalid Node Type**:
```json
{
  "detail": {
    "error": "VALIDATION_ERROR",
    "message": "Invalid node_type: 'InvalidType'",
    "context": {
      "invalid_type": "InvalidType",
      "valid_types_sample": [
        "CeremonialInstrumentalClassification",
        "CircularCausationProcess",
        "CommonsGovernance",
        "ConflictDetection",
        "CoordinationMechanism",
        "CrossImpactAnalysis",
        "CulturalAttitude",
        "DatabaseIntegrationCapability",
        "DeliveryRelationship",
        "DigraphAnalysis"
      ],
      "total_valid_types": 40
    },
    "remediation": "Use GET /api/v1/nodes/types to see all valid node types"
  }
}
```

## OpenAPI Documentation

### Interactive API Documentation

The API provides auto-generated interactive documentation:

**Swagger UI**: `http://localhost:8000/api/v1/docs`
- Interactive API explorer
- Try out endpoints directly in the browser
- View request/response schemas

**ReDoc**: `http://localhost:8000/api/v1/redoc`
- Beautiful, three-panel documentation
- Detailed schema descriptions
- Code samples

**OpenAPI Schema**: `http://localhost:8000/api/v1/openapi.json`
- Machine-readable API specification
- Use for code generation
- Import into API testing tools (Postman, Insomnia)

## Python Client Example

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# Create a node
response = requests.post(
    f"{BASE_URL}/nodes/",
    json={
        "label": "My Institution",
        "description": "Test institution",
        "node_type": "Institution",
        "meta": {"year": "2024"}
    }
)
node = response.json()
print(f"Created node: {node['id']}")

# Get node
node_id = node['id']
response = requests.get(f"{BASE_URL}/nodes/{node_id}")
print(f"Retrieved: {response.json()['label']}")

# Run ceremonial analysis
response = requests.post(
    f"{BASE_URL}/query/ceremonial",
    json={"threshold": 0.5}
)
analysis = response.json()
print(f"Ceremonial ratio: {analysis['ceremonial_ratio']}")

# Delete node
requests.delete(f"{BASE_URL}/nodes/{node_id}")
print("Node deleted")
```

## cURL Examples

### Create and Query

```bash
# Create a node
curl -X POST http://localhost:8000/api/v1/nodes/ \
  -H "Content-Type: application/json" \
  -d '{
    "label": "Test Institution",
    "node_type": "Institution",
    "meta": {"source": "API test"}
  }'

# List all nodes
curl http://localhost:8000/api/v1/nodes/

# Run ceremonial analysis
curl -X POST http://localhost:8000/api/v1/query/ceremonial \
  -H "Content-Type: application/json" \
  -d '{"threshold": 0.6}'

# Get conflicts
curl http://localhost:8000/api/v1/query/conflicts
```

## Rate Limiting & Performance

- **No rate limiting** in current version
- **Recommended limits** for production:
  - 1000 requests/minute per IP
  - 100 concurrent connections
  
- **Performance considerations**:
  - NetworkX backend: ~10,000 nodes efficiently
  - Neo4j backend: Scales to millions of nodes
  - Query endpoints are more expensive than CRUD
  - Evaluation endpoints most expensive (use sparingly)

## Next Steps

1. Explore the interactive docs at `/api/v1/docs`
2. Try the Quick Start examples
3. Review the [SFM Core Documentation](README.md) for conceptual overview
4. Check [examples/](examples/) for complete workflows
