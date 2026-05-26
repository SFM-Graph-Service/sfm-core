# Phase 6: Neo4j Integration Examples

## Overview

Created comprehensive documentation and example scripts demonstrating Neo4j backend integration, addressing the v0.2.0 roadmap item "Integration examples with graph backends".

**Implementation Date**: Continuation after Phase 5 (Node Type Registry)  
**Test Coverage**: 474 tests passing (no new tests required - documentation and examples only)  
**Status**: ✅ Complete

## Motivation

While SFM Core supported Neo4j backend since Phase 3 (Persistence Layer), users needed:

1. **Practical Examples**: Working code showing how to use Neo4j backend
2. **Migration Patterns**: How to move from NetworkX prototyping to Neo4j production
3. **Query Examples**: Cypher queries for common SFM analysis tasks
4. **Best Practices**: Performance optimization, troubleshooting, configuration
5. **Complete Workflows**: End-to-end scenarios for real-world use cases

## Deliverables

### 1. Neo4j Integration Demo Script

**File**: `examples/neo4j_integration_demo.py` (285 lines)

**Demonstrates**:
- ✅ Configuring SFMService for Neo4j backend
- ✅ Creating institutional analysis models (5 different node types)
- ✅ Running direct Cypher queries via Neo4j repository
- ✅ Performing ceremonial analysis with persistent storage
- ✅ Viewing graph statistics
- ✅ Exploring data in Neo4j Browser

**Sample Model Created**:
- Federal Agricultural Subsidy Program (InstitutionalStructure)
- Direct Payment Subsidy (PolicyInstrument)
- Environmental Sustainability Values (ValueSystem)
- Subsidy Application Processing Cost (TransactionCost)
- Subsidy-Environment Value Tension (ValueJudgment)

**Cypher Queries Included**:
1. Find all PolicyInstrument nodes
2. Find nodes with environmental metadata
3. Count nodes by type
4. Find transaction costs with magnitude

**Usage**:
```bash
# Start Neo4j
docker-compose up neo4j

# Run demo
python examples/neo4j_integration_demo.py

# View in Neo4j Browser
open http://localhost:7474
```

**Output Example**:
```
======================================================================
 1. Initializing SFM Service with Neo4j Backend
======================================================================
✓ Connected to Neo4j at bolt://localhost:7687
✓ Using credentials: neo4j

======================================================================
 2. Creating Institutional Analysis Model
======================================================================

Creating Federal Subsidy Program institution...
✓ Created institution: Federal Agricultural Subsidy Program (uuid)

Creating Direct Payment policy instrument...
✓ Created policy: Direct Payment Subsidy (uuid)

...

✓ Created 5 nodes in Neo4j
✓ Total nodes in graph: 5

======================================================================
 3. Running Cypher Queries
======================================================================

Query 1: Find all PolicyInstrument nodes
  - Direct Payment Subsidy: ECONOMIC

...
```

### 2. Backend Migration Demo Script

**File**: `examples/backend_migration_demo.py` (415 lines)

**Demonstrates Three Migration Scenarios**:

#### Scenario 1: Prototype to Production

**Pattern**: Develop in NetworkX (fast iteration) → Deploy to Neo4j (persistent production)

```bash
python examples/backend_migration_demo.py --mode prototype-to-production
```

**Workflow**:
1. Create policy model in NetworkX (in-memory)
2. Export to JSON
3. Import to Neo4j
4. Verify data consistency

**Benefits**:
- Fast prototyping without database setup
- Zero configuration during development
- Easy migration to production
- Data validation before deployment

#### Scenario 2: Backup

**Pattern**: Export Neo4j data to JSON for disaster recovery

```bash
python examples/backend_migration_demo.py --mode backup
```

**Creates**: `exports/neo4j_backup_YYYYMMDD_HHMMSS.json`

**Benefits**:
- Version-controllable backups
- Platform-independent format
- Can restore to any backend
- Supports disaster recovery

#### Scenario 3: Restore

**Pattern**: Restore JSON backup to Neo4j

```bash
python examples/backend_migration_demo.py --mode restore
```

**Features**:
- Lists available backups
- Uses most recent by default
- Clears existing data before restore
- Verifies restoration

### 3. Comprehensive Integration Guide

**File**: `docs/NEO4J_INTEGRATION_GUIDE.md` (550+ lines)

**Contents**:

#### Overview Section
- Backend comparison table (NetworkX vs Neo4j)
- When to use Neo4j
- Prerequisites and installation

#### Quick Start
- Starting Neo4j via Docker
- Configuring SFMService
- Creating and querying data
- Exploring in Neo4j Browser

#### Backend Configuration
- Environment variables
- Programmatic configuration
- REST API with Neo4j backend

#### Integration Patterns

**Pattern 1: Prototype in NetworkX, Deploy to Neo4j**
```python
# Development: NetworkX
dev_service = SFMService(SFMServiceConfig(storage_type="networkx"))
# ... develop model ...
export_data = dev_service.export_to_json()

# Production: Neo4j
prod_service = SFMService(SFMServiceConfig(storage_type="neo4j", ...))
prod_service.import_from_json(export_data)
```

**Pattern 2: Direct Neo4j Development**
```python
# Use Neo4j from the start
service = SFMService(SFMServiceConfig(storage_type="neo4j", ...))
# All operations persist immediately
```

**Pattern 3: Backup and Restore**
```python
# Backup
backup_data = service.export_to_json()
with open(f'backup_{timestamp}.json', 'w') as f:
    json.dump(backup_data, f)

# Restore
service.import_from_json(backup_data)
```

**Pattern 4: Hybrid Queries (Python + Cypher)**
```python
# SFM Service methods
stats = service.get_statistics()

# Direct Cypher for complex queries
results = neo4j_repo.execute_query("""
    MATCH (p:PolicyInstrument)-[:INFLUENCES]->(i:InstitutionalStructure)
    RETURN p.label, i.label
""")
```

#### Cypher Query Examples

**Basic Queries**:
- List all nodes: `MATCH (n) RETURN n LIMIT 25`
- Count by type: `MATCH (n) RETURN labels(n)[0] as type, count(*)`
- Find specific type: `MATCH (n:PolicyInstrument) RETURN n`

**Advanced Queries**:
- Find nodes with metadata: `WHERE n.meta_agency IS NOT NULL`
- Search by label: `WHERE n.label CONTAINS 'Subsidy'`
- Property filtering: `WHERE t.magnitude > 0.2`
- Date ranges: `WHERE n.created_at >= datetime('2024-01-01')`

**Future Relationship Queries** (when relationships added):
```cypher
// Find policy influences
MATCH (p:PolicyInstrument)-[:INFLUENCES]->(i:Institution)
RETURN p.label, i.label

// Find circular dependencies
MATCH path = (n)-[:DEPENDS_ON*]->(n)
RETURN path

// Shortest path
MATCH path = shortestPath((a)-[*]-(b))
RETURN path
```

#### Performance Considerations

**Indexing**:
```cypher
CREATE INDEX label_index FOR (n:Node) ON (n.label);
CREATE INDEX type_index FOR (n:PolicyInstrument) ON (n.instrument_type);
```

**Query Optimization**:
- ❌ Avoid: Full graph scans
- ✅ Prefer: Filter by label first, then properties

**Memory Configuration**:
```conf
server.memory.heap.initial_size=4g
server.memory.heap.max_size=4g
server.memory.pagecache.size=4g
```

#### Troubleshooting Guide

Covers common issues:
- **Connection Refused**: Docker networking, port conflicts
- **Authentication Failed**: Password reset, credential verification
- **Slow Queries**: Indexing, EXPLAIN/PROFILE analysis
- **Database Locked**: File permissions, concurrent instances
- **Memory Errors**: Heap size, batch imports, cache clearing

Each issue includes:
- Problem description
- Step-by-step solutions
- Example commands
- Prevention tips

### 4. Updated Documentation

**Modified**: `README.md`

Added references to new integration examples:
```markdown
- **Neo4j Integration**: See [docs/NEO4J_INTEGRATION_GUIDE.md](...)
- **Example Scripts**: 
  - [examples/rest_api_demo.py](...)
  - [examples/neo4j_integration_demo.py](...)
  - [examples/backend_migration_demo.py](...)
```

## Benefits

### For Developers

1. **Clear Migration Path**: NetworkX → Neo4j workflow documented
2. **Working Examples**: Copy-paste ready code for common scenarios
3. **Best Practices**: Performance, configuration, troubleshooting
4. **Cypher Templates**: Query examples for SFM-specific analysis

### For Researchers

1. **Persistent Storage**: Models survive restarts, enabling long-term analysis
2. **Visual Exploration**: Neo4j Browser for interactive graph visualization
3. **Complex Queries**: Cypher for sophisticated graph traversals
4. **Backup/Restore**: JSON export for version control and sharing

### For Production Users

1. **Deployment Guide**: Docker configuration, environment variables
2. **Scalability**: Handle millions of nodes efficiently
3. **Reliability**: Battle-tested database with ACID guarantees
4. **Disaster Recovery**: Backup and restore procedures

## Usage Statistics

### Files Created

| File | Lines | Purpose |
|------|-------|---------|
| `examples/neo4j_integration_demo.py` | 285 | Working Neo4j integration example |
| `examples/backend_migration_demo.py` | 415 | Migration scenarios and patterns |
| `docs/NEO4J_INTEGRATION_GUIDE.md` | 550+ | Comprehensive integration guide |

**Total**: 1,250+ lines of documentation and examples

### Example Coverage

**Integration Patterns**: 4 documented patterns  
**Cypher Queries**: 15+ examples (basic + advanced)  
**Migration Scenarios**: 3 complete workflows  
**Troubleshooting Issues**: 5 common problems with solutions  

### Backend Comparison

| Feature | NetworkX | Neo4j |
|---------|----------|-------|
| **Setup Time** | Instant | ~30 seconds (Docker) |
| **Persistence** | None | Disk-based |
| **Query Language** | Python only | Python + Cypher |
| **Scale** | ~10K nodes | Millions of nodes |
| **Visualization** | External tools | Built-in Neo4j Browser |
| **Concurrent Access** | No | Yes |
| **Use Case** | Prototyping | Production |

## Testing

No new unit/integration tests required (documentation and examples only).

**Verification**:
- ✅ All 474 existing tests passing
- ✅ Both example scripts execute successfully (manual testing)
- ✅ Docker Compose configurations work
- ✅ Neo4j Browser queries validated

## Example Workflows

### Workflow 1: Research Project

```bash
# 1. Rapid prototyping
python
>>> from api.sfm_service import SFMService, SFMServiceConfig
>>> service = SFMService(SFMServiceConfig(storage_type="networkx"))
>>> # ... build model rapidly ...

# 2. Export for sharing
>>> data = service.export_to_json()
>>> with open('research_model.json', 'w') as f:
...     json.dump(data, f)

# 3. Collaborator imports to Neo4j for analysis
python examples/backend_migration_demo.py --mode restore
# Opens Neo4j Browser for visual exploration
```

### Workflow 2: Production Deployment

```bash
# 1. Start production Neo4j
docker-compose up -d neo4j

# 2. Start API with Neo4j backend
docker-compose up -d api-neo4j

# 3. Access API
curl http://localhost:8001/api/v1/health
# {"status":"healthy","node_count":0,"relationship_count":0}

# 4. Create models via API (persists to Neo4j)
curl -X POST http://localhost:8001/api/v1/nodes/ \
  -H "Content-Type: application/json" \
  -d '{"label":"Policy", "node_type":"PolicyInstrument"}'

# 5. View in Neo4j Browser
open http://localhost:7474
```

### Workflow 3: Regular Backups

```bash
# Weekly backup script
#!/bin/bash
DATE=$(date +%Y%m%d)
python examples/backend_migration_demo.py --mode backup
cp exports/neo4j_backup_*.json backups/weekly_$DATE.json
git add backups/weekly_$DATE.json
git commit -m "Weekly backup $DATE"
git push
```

## Integration with Existing Features

### REST API

The Neo4j backend works seamlessly with the Phase 4 REST API:

```bash
# Start API with Neo4j
docker-compose up api-neo4j neo4j

# All API endpoints work with Neo4j storage
curl http://localhost:8001/api/v1/nodes/
curl http://localhost:8001/api/v1/query/ceremonial
curl http://localhost:8001/api/v1/evaluate/digraph
```

### Export/Import (Phase 3)

Migration demos leverage Phase 3 export/import functionality:

```python
# Export from any backend
data = service.export_to_json()

# Import to any backend
service.import_from_json(data)
```

### Node Types (Phase 5)

Neo4j Browser queries can filter by node types:

```cypher
// Use types from Phase 5 registry
MATCH (n:PolicyInstrument) RETURN n
MATCH (n:ValueSystem) RETURN n
MATCH (n:TransactionCost) RETURN n
```

## Success Criteria

✅ Comprehensive Neo4j integration guide (550+ lines)  
✅ Working integration demo with institutional model  
✅ Backend migration demo with 3 scenarios  
✅ 15+ Cypher query examples  
✅ 4 integration patterns documented  
✅ Performance and troubleshooting sections  
✅ Docker configurations tested  
✅ All 474 tests still passing  
✅ README updated with references  

## Next Steps

Based on the v0.2.0 roadmap, remaining items:

1. **Enhanced documentation with usage examples** ✅ (Partially complete with Neo4j examples)
2. **Additional specialized node types** - Could add domain-specific node types
3. **Extended enum validation capabilities** - Enhance enum validation system

Or explore v0.3.0 roadmap:
- Performance optimizations for large models
- Additional analytical frameworks
- Enhanced metadata and versioning support
- Multi-language support for international applications

## Resources

- **Integration Guide**: `docs/NEO4J_INTEGRATION_GUIDE.md`
- **Integration Demo**: `examples/neo4j_integration_demo.py`
- **Migration Demo**: `examples/backend_migration_demo.py`
- **Docker Compose**: `docker-compose.yml` (includes Neo4j service)
- **Neo4j Documentation**: https://neo4j.com/docs/
- **Cypher Reference**: https://neo4j.com/docs/cypher-manual/current/
