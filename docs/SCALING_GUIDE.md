# SFM Core Scaling Guide

**Version**: 1.0  
**Last Updated**: 2026-05-27

**Note**: This is research software under active development. Claude AI was used to assist with documentation. Performance metrics are approximate and should be verified for your specific use case.

---

## Overview

This guide helps you choose the right backend and optimization strategies for your SFM modeling scenarios based on graph size and performance requirements.

---

## Quick Reference

| Graph Size | Recommended Backend | Creation Method | Query Performance |
|------------|-------------------|-----------------|-------------------|
| < 1,000 nodes, < 5,000 rels | NetworkX (default) | Individual | Excellent (2-5M items/sec) |
| 1,000-10,000 nodes, 5k-20k rels | NetworkX | **Bulk** | Excellent |
| > 10,000 nodes, > 20k rels | Neo4j (recommended) | Bulk | Good (indexed) |

---

## Backend Comparison

### NetworkX Backend (In-Memory)

**Best For**:
- Prototyping and development
- Small to medium scenarios (<10k relationships)
- Fast query requirements (2-5M items/sec)
- No database setup required

**Characteristics**:
- ✅ **Blazing fast queries**: 2.2M-4.7M items/sec for scans, O(1) adjacency lookups
- ✅ **Fast node creation**: 150k-200k nodes/sec
- ⚠️ **Relationship creation degrades**: Drops from 1,670 to 462 rels/sec over 15k relationships
- ✅ **Bulk creation fix**: 210x speedup with `create_relationships_bulk()` (700k rels/sec)
- ❌ **Memory bound**: Entire graph in RAM
- ❌ **No persistence**: In-memory only (use save/load for persistence)

**Performance Data** (from stress test):
```
Nodes: 5,000 in 0.03s (164,965/sec)
Relationships (individual): 15,000 in 21.33s (703/sec, degrades 63%)
Relationships (bulk): 3,000 in 0.004s (703,310/sec)
Query scan: 2.2M-4.7M items/sec
```

**Bottleneck Identified**:
- Individual `create_relationship()` has O(n) duplicate check via edge iteration
- Each relationship creation iterates all existing edges: reportviews.py:958 (5,050 calls for 100 rels)
- **Solution**: Use `create_relationships_bulk()` for scenarios with 100+ relationships

---

### Neo4j Backend (Graph Database)

**Best For**:
- Production deployments with large graphs (>10k relationships)
- Multi-user concurrent access
- Persistent storage requirements
- Complex graph traversals (beyond depth 3-4)

**Characteristics**:
- ✅ **Indexed relationship creation**: Constant time performance at scale
- ✅ **Persistent storage**: Survives restarts
- ✅ **Concurrent access**: Multi-user safe
- ✅ **Cypher query language**: Advanced graph queries
- ⚠️ **Network overhead**: Slower than in-memory for small graphs
- ⚠️ **Setup required**: Requires Neo4j server installation

**Setup**:
```python
from api.sfm_service import SFMService, SFMServiceConfig

config = SFMServiceConfig(
    storage_type="neo4j",
    neo4j_uri="bolt://localhost:7687",
    neo4j_username="neo4j",
    neo4j_password="your-password"
)
service = SFMService(config)
```

**When to Migrate**:
- Individual relationship creation consistently < 500/sec
- Graph size exceeds 20k relationships
- Need concurrent access from multiple users
- Require persistent storage without manual save/load

---

## Optimization Strategies

### 1. Bulk Relationship Creation

**Problem**: Individual creation O(n) duplicate check causes 63% throughput drop over 15k rels.

**Solution**: Use `create_relationships_bulk()` for 210x speedup.

#### Before (Slow):
```python
from graph.sfm_graph import Relationship

# Creating 3,000 relationships individually
for i in range(3000):
    rel = Relationship(
        source_id=nodes[i].id,
        target_id=nodes[i+1].id,
        kind="influences",
        weight=0.8
    )
    service.create_relationship(rel)  # 0.90s total (3,336/sec)
```

#### After (Fast):
```python
# Prepare all relationships first
relationships = []
for i in range(3000):
    rel = Relationship(
        source_id=nodes[i].id,
        target_id=nodes[i+1].id,
        kind="influences",
        weight=0.8
    )
    relationships.append(rel)

# Create in bulk
service.create_relationships_bulk(relationships)  # 0.004s total (703,310/sec)
```

**Speedup**: 210x faster (0.90s → 0.004s for 3,000 relationships)

**When to Use**:
- Scenario builders creating 100+ relationships
- Data imports from CSV, JSON, or external APIs
- Batch operations where all relationships known upfront
- Any time creating more than ~50 relationships

**Safety**:
- Validates all relationships before any creation (atomic)
- Checks source/target node existence upfront
- Detects duplicate IDs within batch (intra-batch validation)
- Throws same exceptions as individual creation

---

### 2. Temporal and Uncertainty Fields

New fields added to `Relationship` class may increase memory footprint. For large graphs, consider:

**Memory-Conscious Approach**:
```python
# Only populate fields when needed
rel = Relationship(
    source_id=source_id,
    target_id=target_id,
    kind="influences",
    weight=0.8
    # Leave temporal/uncertainty fields as None if not needed
)
```

**Full Metadata Approach** (recommended for research scenarios):
```python
from datetime import datetime

rel = Relationship(
    source_id=source_id,
    target_id=target_id,
    kind="influences",
    weight=0.8,
    
    # Temporal
    valid_from=datetime(1970, 1, 1),
    valid_to=datetime(1990, 12, 31),
    
    # Uncertainty
    confidence=0.85,
    confidence_interval=(0.7, 0.9),
    uncertainty_type="epistemic",
    data_sources=["EPA 1997", "Industry studies"],
    source_agreement="low"
)
```

**Memory Impact**:
- Base Relationship: ~200 bytes
- With all temporal/uncertainty fields: ~400 bytes
- 10k relationships: ~2MB → ~4MB difference (negligible)

---

### 3. Query Optimization

**Metadata Filters** (Fast: 2.6M nodes/sec):
```python
# Efficient: Single pass through nodes
filtered = [n for n in service._repository.graph if 'pattern' in (n.description or '')]
```

**Relationship Weight Filters** (Fast: 4.8M rels/sec):
```python
# Efficient: Single pass through edges
nx_graph = service._repository.graph
high_weight = [
    data.get('data') 
    for u, v, key, data in nx_graph.edges(data=True, keys=True)
    if data.get('data') and data.get('data').weight and data.get('data').weight > 0.9
]
```

**Node Lookups** (Instant: O(1)):
```python
# Very fast: NetworkX adjacency lookup
outgoing = list(nx_graph.out_edges(node_id, keys=True))
incoming = list(nx_graph.in_edges(node_id, keys=True))
```

**Complex Analysis** (1,016 nodes/sec):
```python
# Slower but acceptable: O(n²) ceremonial analysis
service.initialize_query_engine()
analysis = service.get_ceremonial_analysis(threshold=0.5)
# 5k nodes: 4.9s
# 50k nodes: ~490s (consider caching)
```

---

## Migration Patterns

### Small → Medium (NetworkX Individual → NetworkX Bulk)

**When**: Scenario grows to 500+ relationships

**Steps**:
1. Refactor scenario builder to prepare relationships in list
2. Replace individual `create_relationship()` calls with single `create_relationships_bulk()`
3. Expect 100-200x speedup

**Example**:
```python
# Before
for source, target, kind, weight in scenario_data:
    rel = Relationship(source_id=source, target_id=target, kind=kind, weight=weight)
    service.create_relationship(rel)

# After
rels = [
    Relationship(source_id=s, target_id=t, kind=k, weight=w)
    for s, t, k, w in scenario_data
]
service.create_relationships_bulk(rels)
```

---

### Medium → Large (NetworkX → Neo4j)

**When**: Graph exceeds 20k relationships or requires persistence

**Steps**:

1. **Install Neo4j**:
```bash
# Docker method
docker run -d \
  --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/your-password \
  neo4j:latest
```

2. **Update Service Configuration**:
```python
from api.sfm_service import SFMService, SFMServiceConfig

# Old: NetworkX (default)
service = SFMService()

# New: Neo4j
config = SFMServiceConfig(
    storage_type="neo4j",
    neo4j_uri="bolt://localhost:7687",
    neo4j_username="neo4j",
    neo4j_password="your-password"
)
service = SFMService(config)
```

3. **Export/Import Data** (if migrating existing graph):
```python
# Export from NetworkX
old_service = SFMService()
export_data = old_service.export_graph()

# Import to Neo4j
new_service = SFMService(config)
new_service.import_graph(export_data)
```

4. **Update Scenario Builders**:
- No code changes needed for CRUD operations
- Query methods identical
- Bulk creation still recommended

---

## Performance Benchmarks

### NetworkX Backend

| Operation | Throughput | Notes |
|-----------|------------|-------|
| Node creation | 150k-200k/sec | Constant time |
| Relationship creation (individual) | 1,670 → 462/sec | Degrades O(n) |
| Relationship creation (bulk) | 700k/sec | 210x faster |
| Metadata filter | 2.6M nodes/sec | O(n) scan |
| Weight filter | 4.8M rels/sec | O(n) scan |
| Adjacency lookup | Instant | O(1) |
| Ceremonial analysis | 1,016 nodes/sec | O(n²) |

### Neo4j Backend

| Operation | Throughput | Notes |
|-----------|------------|-------|
| Node creation | 5k-10k/sec | Network overhead |
| Relationship creation | 2k-5k/sec | Indexed, constant time |
| Cypher query (indexed) | 10k-50k/sec | Depends on index |
| Cypher query (full scan) | 1k-10k/sec | Depends on complexity |
| Traversal (depth 3-5) | 100-1k/sec | Highly optimized |

*Neo4j benchmarks are estimates based on typical configurations. Actual performance varies with schema, indexes, and hardware.*

---

## Best Practices

### 1. Choose Backend Early

**Decision Tree**:
```
Are you building a production system? 
├─ Yes → Will it have >10k relationships?
│  ├─ Yes → Use Neo4j
│  └─ No → Start with NetworkX, plan migration path
└─ No (research/prototype) → Use NetworkX
```

### 2. Use Bulk Creation for Scenarios

**Always** use `create_relationships_bulk()` when:
- Creating >50 relationships at once
- Building scenarios programmatically
- Importing data from external sources

**Exception**: Real-time relationship creation (user interactions, streaming data) should use individual creation.

### 3. Profile Before Optimizing

**Warning Signs**:
- Relationship creation <500/sec
- Query times >5s for <10k nodes
- Memory usage >80% of available RAM

**Profiling Command**:
```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Your scenario code here

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)
```

### 4. Monitor Memory Usage

**Estimate**:
- Node: ~500 bytes (base) + metadata
- Relationship: ~400 bytes (with all fields) + metadata
- 10k nodes + 30k rels ≈ 17MB (in-memory graph)
- 100k nodes + 300k rels ≈ 170MB
- 1M nodes + 3M rels ≈ 1.7GB

**Check Usage**:
```python
import psutil
import os

process = psutil.Process(os.getpid())
memory_mb = process.memory_info().rss / 1024 / 1024
print(f"Memory usage: {memory_mb:.0f} MB")
```

---

## Troubleshooting

### Problem: Relationship Creation Slowing Down

**Symptoms**: Throughput drops from 1,500/sec to <500/sec

**Diagnosis**:
```python
import time

# Time batches of 100 relationships
for batch in range(10):
    start = time.time()
    for i in range(100):
        # Create relationship
        pass
    elapsed = time.time() - start
    print(f"Batch {batch}: {elapsed:.3f}s ({100/elapsed:.0f}/sec)")
```

**Solutions**:
1. Switch to `create_relationships_bulk()` (210x speedup)
2. If already using bulk, consider Neo4j backend
3. Check for memory pressure (see memory monitoring above)

---

### Problem: Queries Timing Out

**Symptoms**: Ceremonial analysis >10s, path queries never return

**Diagnosis**:
- Graph size >50k nodes: O(n²) algorithms slow
- Circular causation depth >5: Exponential search space
- Missing indexes (Neo4j only): Full table scans

**Solutions**:
1. **Cache analysis results**:
```python
# Run once, save result
analysis = service.get_ceremonial_analysis(threshold=0.5)
import json
with open('ceremonial_cache.json', 'w') as f:
    json.dump(analysis, f)
```

2. **Limit query scope**:
```python
# Instead of full graph circular causation
service.get_circular_causation(source_id, max_depth=3)  # Limit depth
```

3. **Use Neo4j with indexes** (for >20k relationships):
```cypher
CREATE INDEX FOR (n:Node) ON (n.ceremonial_score)
CREATE INDEX FOR ()-[r:INFLUENCES]-() ON (r.weight)
```

---

### Problem: Out of Memory

**Symptoms**: Python process killed, `MemoryError` exceptions

**Diagnosis**:
```python
# Check graph size
stats = service.get_statistics()
print(f"Nodes: {stats.total_nodes}, Rels: {stats.total_relationships}")

# Estimate memory
est_mb = (stats.total_nodes * 0.5 + stats.total_relationships * 0.4) / 1000
print(f"Estimated graph memory: {est_mb:.0f} MB")
```

**Solutions**:
1. **Migrate to Neo4j** (persistent storage, not memory-bound)
2. **Reduce metadata** (avoid large meta dicts)
3. **Process in chunks** (load/analyze/save subgraphs)
4. **Increase system RAM** (cloud instances, etc.)

---

## Appendix: Profiling Results

### Relationship Creation Bottleneck

**Profile output** (100 relationships created individually):
```
ncalls  tottime  cumtime  function
  5050    0.016    0.024  reportviews.py:958(<genexpr>)  ← O(n) edge iteration
   100    0.001    0.027  repositories.py:197(create_relationship)
   100    0.000    0.000  multidigraph.py:428(add_edge)
```

**Interpretation**:
- 5,050 calls to `<genexpr>` = 50.5 iterations per relationship on average
- Matches O(n) behavior: at 100 rels created, checking against ~50 existing edges each time
- Validates bulk creation optimization: build ID set once (O(n)) instead of per-relationship (O(n²))

---

## Contact & Support

For questions about scaling or performance:
- GitHub Issues: [sfm-core/issues](https://github.com/your-org/sfm-core/issues)
- Documentation: [sfm-core/docs](https://github.com/your-org/sfm-core/docs)

---

**Last Updated**: 2026-05-26  
**Version**: 1.0
