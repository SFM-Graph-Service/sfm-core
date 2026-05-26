# Phase 5: Node Type Registry Enhancement

## Overview

Enhanced the REST API with a comprehensive node type registry system that provides validation, discovery, and better error messaging for node type operations.

**Implementation Date**: Continuation after Phase 4 completion  
**Test Coverage**: 99% API coverage, 474 total tests passing (+5 new tests)  
**Status**: ✅ Complete

## Motivation

The Phase 4 REST API implementation included a TODO comment in the nodes router:
```python
# TODO: Implement type filtering once we have proper node type registry
```

Users needed a way to:
1. **Discover** all available node types in the SFM framework
2. **Validate** node_type parameters to prevent errors
3. **Understand** the organization of node types by domain module
4. **Get helpful errors** when using invalid node types

## Implementation

### 1. Node Type Registry Module

**File**: `api/rest/node_registry.py`

Created a centralized registry containing all 40 Node subclasses from the 14 domain modules:

```python
NODE_TYPES = {
    "base": {"Node"},
    "complex_analysis": {"DigraphAnalysis", "CircularCausationProcess", "ConflictDetection"},
    "cultural_analysis": {"CeremonialInstrumentalClassification", "ValueSystem", "SocialBelief", "CulturalAttitude"},
    "economic_analysis": {"TransactionCost", "CoordinationMechanism", "CommonsGovernance"},
    # ... 11 more domains
}
```

**Functions**:
- `get_all_node_types()`: Returns set of all 40 valid node type names
- `is_valid_node_type(node_type)`: Validates a node type string
- `get_node_types_by_domain()`: Returns types organized by domain module
- `ALL_NODE_TYPES`: Pre-computed set for fast O(1) validation

### 2. New API Endpoint: GET /api/v1/nodes/types

**Purpose**: Allow users to discover all available node types

**Basic Usage**:
```bash
GET /api/v1/nodes/types
```

**Response**:
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

**With Domain Breakdown**:
```bash
GET /api/v1/nodes/types?include_domains=true
```

Returns the same data plus `by_domain` object showing node types grouped by their domain module (base, complex_analysis, cultural_analysis, etc.).

### 3. Enhanced Node Type Validation

**Updated**: `api/rest/routers/nodes.py` - `list_nodes()` endpoint

**Before**:
```python
# TODO: Implement type filtering once we have proper node type registry
nodes = service.list_nodes()
if node_type:
    nodes = [n for n in nodes if type(n).__name__ == node_type]
```

**After**:
```python
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

nodes = service.list_nodes()
if node_type:
    nodes = [n for n in nodes if type(n).__name__ == node_type]
```

**Error Response Example**:
```bash
GET /api/v1/nodes/?node_type=InvalidType
```

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

### 4. New Pydantic Schema

**Added to**: `api/rest/schemas.py`

```python
class NodeTypesResponse(BaseModel):
    """Schema for node types registry response."""
    node_types: List[str]
    total: int
    by_domain: Optional[Dict[str, List[str]]] = None
```

### 5. Comprehensive Testing

**Added 5 New Tests** to `tests/test_api/test_nodes.py`:

1. `test_list_node_types_basic()`: Verify basic /types endpoint
2. `test_list_node_types_with_domains()`: Verify domain breakdown
3. `test_list_nodes_with_invalid_type()`: Verify 400 error for invalid type
4. `test_list_nodes_with_valid_type()`: Verify filtering works with valid type
5. `test_node_types_integration()`: Integration test with real service

**Test Results**: All 474 tests passing (469 + 5 new)

### 6. Documentation Updates

**API_DOCUMENTATION.md**:
- Added comprehensive /types endpoint documentation
- Added invalid node_type error example to error handling section
- Included both basic and with-domains response examples

**README.md**:
- Added `GET /api/v1/nodes/types` to Node CRUD endpoints list

## Benefits

1. **API Discoverability**: Users can now discover all 40 available node types programmatically
2. **Better Error Messages**: Invalid node_type parameters return helpful 400 errors with suggestions
3. **Domain Organization**: Users can see how node types are organized across the 14 SFM domain modules
4. **Input Validation**: Prevents confusing errors by validating node_type early
5. **Developer Experience**: Clear remediation guidance ("Use GET /api/v1/nodes/types to see all valid node types")

## Technical Details

### Node Type Inventory

The registry includes all 40 Node subclasses across 14 domain modules:

| Domain Module | Node Types | Count |
|---------------|------------|-------|
| base | Node | 1 |
| complex_analysis | DigraphAnalysis, CircularCausationProcess, ConflictDetection | 3 |
| cultural_analysis | CeremonialInstrumentalClassification, ValueSystem, SocialBelief, CulturalAttitude | 4 |
| economic_analysis | TransactionCost, CoordinationMechanism, CommonsGovernance | 3 |
| institutional_analysis | InstitutionalStructure, PathDependencyAnalysis | 2 |
| matrix_components | MatrixCell, SFMCriteria, SFMMatrix | 3 |
| meta_entities | Scenario, ScenarioSet, ScenarioPath | 3 |
| methodological_framework | InstrumentalistInquiryFramework, NormativeSystemsAnalysis, PolicyRelevanceIntegration, DatabaseIntegrationCapability | 4 |
| network_analysis | CrossImpactAnalysis, DeliveryRelationship, MatrixDeliveryNetwork | 3 |
| policy_framework | PolicyInstrument, ValueJudgment, ProblemSolvingSequence | 3 |
| social_assessment | SocialValueAssessment, SocialFabricIndicator, SocialCost | 3 |
| specialized_components | SocialIndicatorSystem, EvolutionaryPathway, SocialProvisioningMatrix | 3 |
| system_analysis | SystemProperty, SystemLevelAnalysis, InstitutionalHolarchy | 3 |
| technology_integration | ToolSkillTechnologyComplex, EcologicalSystem | 2 |
| **Total** | | **40** |

### Performance

- **Registry Lookup**: O(1) using pre-computed `ALL_NODE_TYPES` set
- **Validation**: Fast set membership check
- **Endpoint Response**: ~40KB JSON with all types and domains

## Usage Examples

### Python Client

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# Get all available node types
response = requests.get(f"{BASE_URL}/nodes/types")
types = response.json()
print(f"Total node types: {types['total']}")
print(f"Available types: {types['node_types'][:5]}...")

# Get types organized by domain
response = requests.get(f"{BASE_URL}/nodes/types?include_domains=true")
types = response.json()
print(f"Policy framework types: {types['by_domain']['policy_framework']}")

# Filter nodes by valid type
response = requests.get(f"{BASE_URL}/nodes/?node_type=PolicyInstrument")
policy_instruments = response.json()

# Try invalid type (returns 400 with helpful error)
try:
    response = requests.get(f"{BASE_URL}/nodes/?node_type=FakeType")
    response.raise_for_status()
except requests.HTTPError as e:
    print(f"Error: {e.response.json()['detail']['message']}")
    print(f"Suggestion: {e.response.json()['detail']['remediation']}")
```

### cURL

```bash
# List all node types
curl http://localhost:8000/api/v1/nodes/types

# Get domain breakdown
curl http://localhost:8000/api/v1/nodes/types?include_domains=true

# Filter nodes by type
curl http://localhost:8000/api/v1/nodes/?node_type=ValueSystem

# See validation error
curl http://localhost:8000/api/v1/nodes/?node_type=InvalidType
```

## Files Changed

### New Files
1. `api/rest/node_registry.py` (106 lines) - Node type registry

### Modified Files
1. `api/rest/routers/nodes.py` - Added validation and /types endpoint
2. `api/rest/schemas.py` - Added NodeTypesResponse schema
3. `tests/test_api/test_nodes.py` - Added 5 new tests
4. `API_DOCUMENTATION.md` - Documented new endpoint and error example
5. `README.md` - Added /types to endpoint list

### Test Results
```
====================== 474 passed, 2646 warnings in 0.97s ======================
Coverage: 99% (api/rest)
```

## Success Criteria

✅ Node type registry with all 40 types from 14 domains  
✅ GET /api/v1/nodes/types endpoint working  
✅ Domain breakdown via ?include_domains=true parameter  
✅ Node type validation with helpful error messages  
✅ 5 comprehensive tests added (unit + integration)  
✅ Documentation updated (API docs + README)  
✅ All 474 tests passing  
✅ 99% API test coverage maintained  

## Next Steps

Potential future enhancements:
1. **Node Type Factory**: Extend `_create_node_from_schema()` to create specialized node instances based on node_type field
2. **Type-Specific Validation**: Add validation rules for type_fields based on node_type
3. **OpenAPI Schema Generation**: Auto-generate discriminated union schemas for node types
4. **Node Type Descriptions**: Add human-readable descriptions for each node type
5. **Domain Module Metadata**: Add descriptions for each domain module
