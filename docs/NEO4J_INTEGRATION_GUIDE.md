# Neo4j Integration Guide

Complete guide to using SFM Core with Neo4j graph database for persistent storage, advanced querying, and production deployments.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Backend Configuration](#backend-configuration)
- [Integration Patterns](#integration-patterns)
- [Example Scripts](#example-scripts)
- [Cypher Query Examples](#cypher-query-examples)
- [Performance Considerations](#performance-considerations)
- [Troubleshooting](#troubleshooting)

## Overview

SFM Core supports two storage backends:

| Backend | Use Case | Persistence | Scale | Query Language |
|---------|----------|-------------|-------|----------------|
| **NetworkX** | Prototyping, testing, small datasets | In-memory (ephemeral) | ~10,000 nodes | Python methods |
| **Neo4j** | Production, large datasets, complex queries | Disk-based (persistent) | Millions of nodes | Cypher + Python |

### When to Use Neo4j

Choose Neo4j backend when you need:

✅ **Persistent Storage**: Data survives application restarts  
✅ **Large Datasets**: Handle millions of nodes efficiently  
✅ **Complex Queries**: Use Cypher for advanced graph traversals  
✅ **Concurrent Access**: Multiple clients querying simultaneously  
✅ **Production Deployment**: Reliable, battle-tested database  
✅ **Visual Exploration**: Neo4j Browser for interactive data exploration  

## Prerequisites

### Software Requirements

1. **Python 3.9+** with sfm-core installed
2. **Neo4j 5.x** database server
3. **neo4j Python driver** (automatically installed with sfm-core)

### Installing Neo4j

**Option 1: Docker (Recommended for Development)**

```bash
# Using the provided docker-compose.yml
docker-compose up neo4j

# Neo4j will be available at:
# - Browser: http://localhost:7474
# - Bolt: bolt://localhost:7687
# - Credentials: neo4j/neo4j_password
```

**Option 2: Desktop Application**

Download from https://neo4j.com/download/

**Option 3: System Package**

```bash
# Ubuntu/Debian
wget -O - https://debian.neo4j.com/neotechnology.gpg.key | sudo apt-key add -
echo 'deb https://debian.neo4j.com stable latest' | sudo tee /etc/apt/sources.list.d/neo4j.list
sudo apt-get update
sudo apt-get install neo4j

# macOS
brew install neo4j

# Start service
sudo systemctl start neo4j  # Linux
brew services start neo4j   # macOS
```

## Quick Start

### 1. Start Neo4j

```bash
# Using Docker
docker-compose up neo4j

# Verify Neo4j is running
curl http://localhost:7474
```

### 2. Configure SFM Service

```python
from api.sfm_service import SFMService, SFMServiceConfig

# Configure for Neo4j backend
config = SFMServiceConfig(
    storage_type="neo4j",
    neo4j_uri="bolt://localhost:7687",
    neo4j_username="neo4j",
    neo4j_password="neo4j_password",
)

service = SFMService(config=config)
```

### 3. Create and Query Data

```python
from models.policy_framework import PolicyInstrument
from models.sfm_enums import PolicyInstrumentType

# Create a node (persists to Neo4j)
policy = PolicyInstrument(
    label="Carbon Tax",
    description="Tax on carbon emissions",
    instrument_type=PolicyInstrumentType.ECONOMIC
)
policy = service.create_node(policy)

# Query back from Neo4j
retrieved = service.get_node(policy.id)
print(f"Retrieved: {retrieved.label}")

# Data persists across restarts!
```

### 4. Explore in Neo4j Browser

1. Open http://localhost:7474
2. Login with neo4j/neo4j_password
3. Run query: `MATCH (n) RETURN n`
4. Visualize your SFM graph!

## Backend Configuration

### Environment Variables

Set these environment variables to configure Neo4j connection:

```bash
# .env file
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=neo4j_password
```

### Programmatic Configuration

```python
import os
from api.sfm_service import SFMService, SFMServiceConfig

config = SFMServiceConfig(
    storage_type="neo4j",
    neo4j_uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
    neo4j_username=os.getenv("NEO4J_USERNAME", "neo4j"),
    neo4j_password=os.getenv("NEO4J_PASSWORD", "neo4j"),
)

service = SFMService(config=config)
```

### REST API with Neo4j

Start the API server with Neo4j backend:

```bash
# Using Docker
docker-compose up api-neo4j neo4j

# Manual start
export NEO4J_URI=bolt://localhost:7687
export NEO4J_USERNAME=neo4j
export NEO4J_PASSWORD=neo4j_password
uvicorn api.rest.app:app --host 0.0.0.0 --port 8000
```

The API will use Neo4j for all operations.

## Integration Patterns

### Pattern 1: Prototype in NetworkX, Deploy to Neo4j

Develop rapidly with in-memory NetworkX, then migrate to persistent Neo4j for production.

```python
# Development: NetworkX
dev_service = SFMService(SFMServiceConfig(storage_type="networkx"))

# Create model
node = dev_service.create_node(...)

# Export to JSON
export_data = dev_service.export_to_json()
with open('model.json', 'w') as f:
    json.dump(export_data, f)

# Production: Neo4j
prod_service = SFMService(SFMServiceConfig(
    storage_type="neo4j",
    neo4j_uri="bolt://prod-server:7687",
    neo4j_username="neo4j",
    neo4j_password="secure_password",
))

# Import to production
with open('model.json', 'r') as f:
    import_data = json.load(f)
prod_service.import_from_json(import_data)
```

**See**: `examples/backend_migration_demo.py --mode prototype-to-production`

### Pattern 2: Direct Neo4j Development

Use Neo4j from the start for persistent storage during development.

```python
# Configure Neo4j
service = SFMService(SFMServiceConfig(
    storage_type="neo4j",
    neo4j_uri="bolt://localhost:7687",
    neo4j_username="neo4j",
    neo4j_password="neo4j",
))

# All operations persist immediately
institution = service.create_node(...)  # Persisted
service.update_node(institution)         # Updated in DB
service.delete_node(institution.id)      # Deleted from DB
```

**See**: `examples/neo4j_integration_demo.py`

### Pattern 3: Backup and Restore

Regular backups of Neo4j data to JSON for disaster recovery.

```python
# Backup
service = SFMService(SFMServiceConfig(storage_type="neo4j", ...))
backup_data = service.export_to_json()
with open(f'backup_{timestamp}.json', 'w') as f:
    json.dump(backup_data, f)

# Restore (to same or different Neo4j instance)
service.clear_all_data()  # Clear existing data
with open('backup.json', 'r') as f:
    service.import_from_json(json.load(f))
```

**See**: `examples/backend_migration_demo.py --mode backup` and `--mode restore`

### Pattern 4: Hybrid Queries (Python + Cypher)

Use SFM Service methods for common operations, drop down to Cypher for complex queries.

```python
# SFM Service methods
service = SFMService(SFMServiceConfig(storage_type="neo4j", ...))
stats = service.get_statistics()
ceremonial = service.get_ceremonial_analysis()

# Direct Cypher for complex queries
neo4j_repo = service.repository
results = neo4j_repo.execute_query("""
    MATCH (p:PolicyInstrument)-[:INFLUENCES]->(i:InstitutionalStructure)
    WHERE p.instrument_type = 'ECONOMIC'
    RETURN p.label as policy, i.label as institution
""")

for record in results:
    print(f"{record['policy']} → {record['institution']}")
```

## Example Scripts

### 1. Neo4j Integration Demo

**File**: `examples/neo4j_integration_demo.py`

Demonstrates:
- Connecting to Neo4j
- Creating institutional analysis models
- Running Cypher queries
- Performing ceremonial analysis
- Exploring in Neo4j Browser

**Usage**:

```bash
# Start Neo4j
docker-compose up neo4j

# Run demo
python examples/neo4j_integration_demo.py

# View results
open http://localhost:7474
```

### 2. Backend Migration Demo

**File**: `examples/backend_migration_demo.py`

Demonstrates:
- Migrating from NetworkX to Neo4j
- Backing up Neo4j data to JSON
- Restoring JSON backups to Neo4j
- Verifying data consistency

**Usage**:

```bash
# Prototype → Production migration
python examples/backend_migration_demo.py --mode prototype-to-production

# Backup Neo4j data
python examples/backend_migration_demo.py --mode backup

# Restore from backup
python examples/backend_migration_demo.py --mode restore
```

## Cypher Query Examples

### Basic Queries

**List all nodes**:
```cypher
MATCH (n)
RETURN n
LIMIT 25
```

**Count nodes by type**:
```cypher
MATCH (n)
RETURN labels(n)[0] as type, count(*) as count
ORDER BY count DESC
```

**Find specific node type**:
```cypher
MATCH (n:PolicyInstrument)
RETURN n.label, n.description, n.instrument_type
```

### Advanced Queries

**Find nodes with metadata**:
```cypher
MATCH (n)
WHERE n.meta_agency IS NOT NULL
RETURN n.label, n.meta_agency, n.meta_established
```

**Search by label**:
```cypher
MATCH (n)
WHERE n.label CONTAINS 'Subsidy'
RETURN n
```

**Property-based filtering**:
```cypher
MATCH (t:TransactionCost)
WHERE t.magnitude > 0.2
RETURN t.label, t.magnitude, t.cost_type
ORDER BY t.magnitude DESC
```

**Date range queries**:
```cypher
MATCH (n)
WHERE n.created_at >= datetime('2024-01-01')
RETURN n.label, n.created_at
ORDER BY n.created_at DESC
```

### Relationship Queries

**Note**: Current version stores nodes only. Relationship support coming in future versions.

When relationships are added, you'll be able to query like:

```cypher
// Find policy instruments that influence institutions
MATCH (p:PolicyInstrument)-[:INFLUENCES]->(i:InstitutionalStructure)
RETURN p.label, i.label

// Find circular dependencies
MATCH path = (n)-[:DEPENDS_ON*]->(n)
RETURN path

// Find shortest path between entities
MATCH path = shortestPath(
  (a:PolicyInstrument)-[*]-(b:ValueSystem)
)
RETURN path
```

## Performance Considerations

### Indexing

Neo4j automatically indexes node IDs (UUID). For custom queries, create indexes:

```cypher
// Index on label (for text search)
CREATE INDEX label_index FOR (n:Node) ON (n.label);

// Index on node type
CREATE INDEX type_index FOR (n:PolicyInstrument) ON (n.instrument_type);

// Index on metadata
CREATE INDEX agency_index FOR (n:InstitutionalStructure) ON (n.meta_agency);
```

### Query Optimization

**❌ Avoid**:
```cypher
// Full graph scan - slow on large datasets
MATCH (n)
WHERE n.label CONTAINS 'term'
RETURN n
```

**✅ Prefer**:
```cypher
// Filtered by label first, then property check
MATCH (n:PolicyInstrument)
WHERE n.label CONTAINS 'term'
RETURN n
```

### Connection Pooling

The Neo4j Python driver uses connection pooling automatically. Default pool size: 100 connections.

To adjust:

```python
from neo4j import GraphDatabase

driver = GraphDatabase.driver(
    "bolt://localhost:7687",
    auth=("neo4j", "password"),
    max_connection_pool_size=50,
    connection_timeout=30.0,
)
```

### Memory Configuration

For large datasets, adjust Neo4j memory settings in `neo4j.conf`:

```conf
# Heap size (recommended: 25-50% of available RAM)
server.memory.heap.initial_size=4g
server.memory.heap.max_size=4g

# Page cache (recommended: 50% of available RAM minus heap)
server.memory.pagecache.size=4g
```

Or via Docker:

```yaml
neo4j:
  environment:
    - NEO4J_server_memory_heap_initial__size=4g
    - NEO4J_server_memory_heap_max__size=4g
    - NEO4J_server_memory_pagecache_size=4g
```

## Troubleshooting

### Connection Refused

**Problem**: `ServiceUnavailable: Unable to retrieve routing information`

**Solutions**:
```bash
# 1. Check Neo4j is running
docker ps | grep neo4j
curl http://localhost:7474

# 2. Check connection settings
echo $NEO4J_URI  # Should be bolt://localhost:7687

# 3. Test with cypher-shell
docker exec -it neo4j cypher-shell -u neo4j -p neo4j_password

# 4. Check Docker networks
docker network ls
docker network inspect sfm-core_default
```

### Authentication Failed

**Problem**: `AuthError: The client is unauthorized due to authentication failure`

**Solutions**:
```bash
# 1. Check credentials
docker-compose logs neo4j | grep password

# 2. Reset Neo4j password
docker exec -it neo4j neo4j-admin set-initial-password new_password

# 3. Verify in Neo4j Browser
open http://localhost:7474
# Login with neo4j/new_password
```

### Slow Queries

**Problem**: Queries taking too long

**Solutions**:

1. **Add indexes**:
```cypher
CREATE INDEX FOR (n:PolicyInstrument) ON (n.label);
```

2. **Use EXPLAIN/PROFILE**:
```cypher
EXPLAIN MATCH (n) WHERE n.label CONTAINS 'term' RETURN n;
PROFILE MATCH (n) WHERE n.label CONTAINS 'term' RETURN n;
```

3. **Limit results**:
```cypher
MATCH (n)
RETURN n
LIMIT 100
```

### Database Locked

**Problem**: `Cannot write to Neo4j database`

**Solutions**:
```bash
# 1. Check file permissions
ls -l /path/to/neo4j/data

# 2. Stop other Neo4j instances
docker ps -a | grep neo4j
docker stop $(docker ps -aq --filter name=neo4j)

# 3. Clear lock files (if safe)
rm /path/to/neo4j/data/databases/neo4j/store_lock
```

### Memory Errors

**Problem**: `OutOfMemoryError: Java heap space`

**Solutions**:

1. **Increase heap size**:
```yaml
# docker-compose.yml
neo4j:
  environment:
    - NEO4J_server_memory_heap_max__size=4g
```

2. **Batch large imports**:
```python
# Instead of importing 10,000 nodes at once
for batch in chunks(nodes, 1000):
    service.import_from_json({"nodes": batch, "relationships": []})
```

3. **Clear cache**:
```cypher
CALL db.clearQueryCaches();
```

## Next Steps

1. **Try the examples**: Run `examples/neo4j_integration_demo.py`
2. **Explore the data**: Use Neo4j Browser at http://localhost:7474
3. **Learn Cypher**: https://neo4j.com/docs/cypher-manual/current/
4. **Production deployment**: See Neo4j deployment guides
5. **REST API with Neo4j**: `docker-compose up api-neo4j neo4j`

## Additional Resources

- **Neo4j Documentation**: https://neo4j.com/docs/
- **Cypher Reference**: https://neo4j.com/docs/cypher-manual/current/
- **Neo4j Python Driver**: https://neo4j.com/docs/python-manual/current/
- **SFM Core API Docs**: See `API_DOCUMENTATION.md`
- **Docker Deployment**: See `docker-compose.yml`
