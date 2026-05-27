# sfm-core — Social Fabric Matrix Graph Service

[![CI](https://github.com/SFM-Graph-Service/sfm-core/actions/workflows/ci.yml/badge.svg)](https://github.com/SFM-Graph-Service/sfm-core/actions/workflows/ci.yml)
[![Code Quality](https://github.com/SFM-Graph-Service/sfm-core/actions/workflows/code-quality.yml/badge.svg)](https://github.com/SFM-Graph-Service/sfm-core/actions/workflows/code-quality.yml)
[![Security](https://github.com/SFM-Graph-Service/sfm-core/actions/workflows/security.yml/badge.svg)](https://github.com/SFM-Graph-Service/sfm-core/actions/workflows/security.yml)
[![Performance](https://github.com/SFM-Graph-Service/sfm-core/actions/workflows/performance.yml/badge.svg)](https://github.com/SFM-Graph-Service/sfm-core/actions/workflows/performance.yml)
[![Documentation](https://github.com/SFM-Graph-Service/sfm-core/actions/workflows/documentation.yml/badge.svg)](https://github.com/SFM-Graph-Service/sfm-core/actions/workflows/documentation.yml)

A production-ready Python framework implementing F. Gregory Hayden's Social Fabric Matrix (SFM) methodology for modeling, analyzing, and querying complex socio-economic systems through graph-based data structures.

**Key Features:**
- **40+ Specialized Node Types** across 12 analytical domains for comprehensive institutional economic modeling
- **Dual-Backend Architecture**: NetworkX (in-memory, 700K rels/sec) or Neo4j (persistent, production-scale)
- **Advanced Analysis**: Ceremonial vs instrumental classification, circular causation detection, institutional holarchy mapping, conflict detection
- **Temporal & Uncertainty Support**: Track institutional evolution over time with confidence intervals and uncertainty propagation
- **REST API**: 30+ FastAPI endpoints with OpenAPI documentation
- **Performance Optimized**: 210x speedup with bulk operations, handles 50K+ nodes efficiently

---

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Architecture Overview](#architecture-overview)
- [Core Features](#core-features)
- [API Usage](#api-usage)
- [Analysis Methods](#analysis-methods)
- [Performance & Scaling](#performance--scaling)
- [Documentation](#documentation)
- [Contributing](#contributing)

---

## Installation

### Requirements

- **Python**: 3.9 or higher
- **System Dependencies**: graphviz (for visualization)
- **Optional**: Docker & Docker Compose (for Neo4j backend)

### Basic Installation (NetworkX Backend)

For development, testing, and datasets with <10,000 nodes:

```bash
# Clone the repository
git clone https://github.com/SFM-Graph-Service/sfm-core.git
cd sfm-core

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install package in development mode
pip install -e .

# Verify installation
python -c "from api.sfm_service import SFMService; print('✓ Installation successful')"
pytest tests/  # Run test suite (501 tests)
```

### Production Installation (Neo4j Backend)

For production deployments and datasets with >10,000 nodes:

```bash
# Install as above, then start Neo4j
docker-compose up neo4j

# Configure environment
export STORAGE_TYPE=neo4j
export NEO4J_URI=bolt://localhost:7687
export NEO4J_USERNAME=neo4j
export NEO4J_PASSWORD=neo4j_password

# Start API server
uvicorn api.rest.app:app --host 0.0.0.0 --port 8000
```

**Access Points:**
- REST API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Neo4j Browser: http://localhost:7474

---

## Quick Start

### Python API

```python
from api.sfm_service import SFMService
from models import Node
from graph.sfm_graph import Relationship

# Initialize service (defaults to NetworkX backend)
service = SFMService()

# Create nodes
epa = service.create_node(Node(
    label="EPA",
    description="Environmental Protection Agency"
))

standards = service.create_node(Node(
    label="Auto Emission Standards",
    description="Clean Air Act vehicle emission requirements"
))

# Create relationship
relationship = Relationship(
    source_id=epa.id,
    target_id=standards.id,
    kind="mandates",
    weight=0.9
)
service.create_relationship(relationship)

# Initialize query engine for analysis
service.initialize_query_engine()

# Run ceremonial vs instrumental analysis
analysis = service.get_ceremonial_analysis(threshold=0.5)
print(f"Ceremonial/Instrumental ratio: {analysis['ceremonial_ratio']:.2f}")

# Detect circular causation
cycles = service.get_circular_causation(source_id=epa.id)
for cycle in cycles:
    print(f"Found feedback loop: {cycle['feedback_type']}")

# Get statistics
stats = service.get_statistics()
print(f"Total nodes: {stats.total_nodes}, relationships: {stats.total_relationships}")
```

### REST API

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Create a node
curl -X POST http://localhost:8000/api/v1/nodes \
  -H "Content-Type: application/json" \
  -d '{
    "label": "EPA Standards",
    "description": "National Ambient Air Quality Standards",
    "meta": {"ceremonial_score": 0.3, "instrumental_score": 0.7}
  }'

# Run ceremonial analysis
curl -X POST http://localhost:8000/api/v1/query/ceremonial \
  -H "Content-Type: application/json" \
  -d '{"threshold": 0.5}'

# Query temporal evolution
curl -X POST http://localhost:8000/api/v1/query/temporal-evolution \
  -H "Content-Type: application/json" \
  -d '{
    "start_date": "1970-01-01T00:00:00Z",
    "end_date": "1990-12-31T23:59:59Z",
    "time_step_days": 1825
  }'
```

---

## Architecture Overview

### Three-Layer Architecture

```
┌─────────────────────────────────────────────────────────┐
│  API LAYER (FastAPI REST)                               │
│  - 30+ endpoints with OpenAPI docs                      │
│  - Health monitoring & statistics                       │
│  - CRUD operations + analysis queries                   │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│  SERVICE LAYER (SFMService)                             │
│  - Unified facade pattern                               │
│  - Query engine integration                             │
│  - Bulk operations (210x speedup)                       │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│  DATA LAYER (Dual Backend)                              │
│  - NetworkX: In-memory (2-5M items/sec)                 │
│  - Neo4j: Persistent graph database                     │
│  - Abstract repository pattern                          │
└─────────────────────────────────────────────────────────┘
```

### Dual-Backend Support

| Backend | Performance | Use Case | Strengths |
|---------|------------|----------|-----------|
| **NetworkX** (default) | 2-5M items/sec query speed<br>700K rels/sec bulk creation | Development, prototyping<br>Graphs <10K nodes | Fast queries, no setup required<br>Excellent for research |
| **Neo4j** (production) | Indexed, constant-time ops<br>Multi-user concurrent | Production deployments<br>Graphs >10K nodes | Persistent storage, Cypher queries<br>Advanced graph algorithms |

**When to migrate**: Graph exceeds 20K relationships, need concurrent access, or require persistent storage without manual save/load.

---

## Core Features

### 1. Comprehensive Domain Models (40+ Node Types)

Organized across **12 analytical domains**:

- **Institutional Analysis**: InstitutionalStructure, PathDependencyAnalysis (3-layer framework)
- **Policy Framework**: PolicyInstrument, ValueJudgment, ProblemSolvingSequence
- **Economic Analysis**: TransactionCost, CoordinationMechanism, CommonsGovernance
- **Cultural Analysis**: CeremonialInstrumentalClassification, ValueSystem, SocialBelief
- **Network Analysis**: CrossImpactAnalysis, DeliveryRelationship, MatrixDeliveryNetwork
- **System Analysis**: SystemProperty, InstitutionalHolarchy, SystemLevelAnalysis
- **Technology Integration**: ToolSkillTechnologyComplex, EcologicalSystem (TRL tracking)
- **Social Assessment**: SocialValueAssessment, SocialFabricIndicator, SocialCost
- **Complex Analysis**: DigraphAnalysis, CircularCausationProcess, ConflictDetection
- **Matrix Components**: MatrixCell, SFMCriteria, SFMMatrix
- **Meta Entities**: Scenario, ScenarioSet, ScenarioPath, TimeSlice, Event, InformalNorm
- **Base Infrastructure**: Node (versioning, temporal tracking, data quality metadata)

**Key Model Features**:
- UUID-based primary keys for distributed systems
- Versioning support (`version`, `previous_version_id`)
- Temporal tracking (`created_at`, `modified_at`, `valid_from`, `valid_to`)
- Data quality metadata (`certainty` 0-1, `data_quality`, `data_sources`)
- Comprehensive enum validation (166KB enums covering flows, institutions, values)

### 2. Advanced Analysis Methods

**Ceremonial vs Instrumental Analysis**
- 4-stage classification cascade (explicit nodes → metadata → type inference → relationship patterns)
- Identifies status quo reinforcing vs problem-solving behaviors
- Ratio calculation for system dominance detection

**Circular Causation Detection**
- Feedback loop identification (reinforcing vs balancing)
- Path dependency analysis
- Cycle strength metrics via cumulative weight calculation

**Institutional Holarchy Mapping**
- Nested hierarchical structure visualization
- Multi-level organizational analysis
- Parent-child relationship tracking

**Conflict Detection**
- Value conflicts, resource conflicts, institutional contradictions
- Ceremonial-instrumental tension identification
- Severity classification (low/medium/high)

**Network Structure Analysis**
- Centrality measures (betweenness, degree, closeness, eigenvector)
- Shortest path finding with relationship kind filters
- Community detection (Louvain algorithm)
- Bottleneck identification via betweenness centrality

### 3. Temporal & Uncertainty Support

**Temporal Modeling**
- Relationship versioning with `valid_from` and `valid_to` dates
- Temporal evolution queries (snapshots over time periods)
- Weight history tracking with effective dates and reasons
- Event nodes for discrete institutional changes

**Uncertainty Propagation**
- Confidence intervals on relationships (`confidence_interval` tuple)
- Multiplicative uncertainty compounding through causal pathways
- Uncertainty type classification (epistemic, aleatory, ambiguity, volatility)
- Data source tracking with agreement levels
- Sensitivity analysis for identifying critical uncertainties

### 4. Performance Optimizations

**Bulk Relationship Creation** (210x speedup)
```python
# Individual creation: 703 rels/sec (degrades with size)
for rel in relationships:
    service.create_relationship(rel)

# Bulk creation: 703,310 rels/sec (constant time)
service.create_relationships_bulk(relationships)
```

**Benchmark Results** (NetworkX backend):
- Node creation: 164,965 nodes/sec
- Bulk relationships: 703,310 rels/sec
- Query scans: 2.2M-4.7M items/sec
- Adjacency lookups: O(1) constant time

**Scaling Recommendations**:
- < 1,000 nodes: NetworkX with individual operations
- 1K-10K nodes: NetworkX with bulk operations
- > 10K nodes: Neo4j backend recommended

### 5. Production Features

**REST API** (30+ endpoints):
- **CRUD**: 12 endpoints (nodes: 7, relationships: 5)
- **Analysis**: 6 endpoints (ceremonial, circular causation, holarchy, conflicts, temporal, uncertainty)
- **Evaluation**: 10 endpoints (digraph, cross-impact, delivery performance, etc.)
- **Health & Stats**: 2 endpoints with monitoring metrics

**Docker Support**:
```bash
# Development (NetworkX)
docker-compose up api-dev

# Production (Neo4j)
docker-compose up api-neo4j neo4j
```

**Error Handling**:
- SFM-specific error types (ValidationError, NotFoundError, IntegrityError)
- HTTP status code mapping
- Remediation suggestions in error responses

**API Documentation**:
- Interactive Swagger UI at `/docs`
- ReDoc alternative view at `/redoc`
- Complete request/response examples

---

## API Usage

### CRUD Operations

```python
from api.sfm_service import SFMService
from models import Node
from graph.sfm_graph import Relationship

service = SFMService()

# CREATE node
node = Node(label="Technology Innovation", description="Catalytic converter")
created = service.create_node(node)

# READ node
retrieved = service.get_node(created.id)

# UPDATE node
retrieved.description = "Updated description"
updated = service.update_node(retrieved)

# DELETE node
success = service.delete_node(created.id)

# LIST nodes (with optional type filter)
from models.institutional_analysis import Institution
institutions = service.list_nodes(node_type=Institution)

# CREATE relationship
rel = Relationship(source_id=n1.id, target_id=n2.id, kind="influences", weight=0.8)
created_rel = service.create_relationship(rel)

# BULK create relationships (efficient)
relationships = [
    Relationship(n1.id, n2.id, "enables", 0.8),
    Relationship(n2.id, n3.id, "produces", 0.7),
]
service.create_relationships_bulk(relationships)
```

### Analysis Examples

**Temporal Evolution:**
```python
from datetime import datetime, timedelta

service.initialize_query_engine()

evolution = service._query_engine.query_temporal_evolution(
    start_date=datetime(1970, 1, 1),
    end_date=datetime(1990, 12, 31),
    time_step=timedelta(days=365*5)  # 5-year intervals
)

for snapshot in evolution:
    print(f"{snapshot['date']}: {snapshot['nodes']} nodes, avg weight {snapshot['avg_weight']:.2f}")
```

**Uncertainty Propagation:**
```python
# Build pathway with confidence intervals
rel1 = Relationship(
    source_id=naaqs.id,
    target_id=emissions.id,
    kind="produces",
    weight=0.8,
    meta={"confidence_interval": [0.7, 0.9], "data_sources": ["EPA 1997"]}
)

service.create_relationship(rel1)
service.initialize_query_engine()

# Propagate uncertainty
path = [naaqs.id, emissions.id, health.id]
result = service._query_engine.propagate_uncertainty_through_path(path)

print(f"Central estimate: {result['cumulative_effect']:.2f}")
print(f"95% CI: ({result['uncertainty_range'][0]:.2f}, {result['uncertainty_range'][1]:.2f})")
```

### REST API Examples

**Create Node:**
```bash
curl -X POST http://localhost:8000/api/v1/nodes \
  -H "Content-Type: application/json" \
  -d '{
    "label": "EPA Standards",
    "description": "NAAQS standards",
    "meta": {"ceremonial_score": 0.3}
  }'
```

**Ceremonial Analysis:**
```bash
curl -X POST http://localhost:8000/api/v1/query/ceremonial \
  -H "Content-Type: application/json" \
  -d '{"threshold": 0.5}'
```

**Circular Causation:**
```bash
curl http://localhost:8000/api/v1/query/circular-causation/{source_node_id}
```

---

## Analysis Methods

### Ceremonial vs Instrumental Analysis

Identifies nodes exhibiting ceremonial (status quo reinforcing) vs instrumental (problem-solving) behaviors based on Veblen's institutional economics framework.

```python
service.initialize_query_engine()
analysis = service.get_ceremonial_analysis(threshold=0.5)

print(f"Ceremonial nodes: {len(analysis['ceremonial_nodes'])}")
print(f"Instrumental nodes: {len(analysis['instrumental_nodes'])}")
print(f"Ratio: {analysis['ceremonial_ratio']:.2f}")

# Interpretation:
# Ratio > 1.0: Ceremonial dominance (resistance to change)
# Ratio < 1.0: Instrumental dominance (adaptive innovation)
```

### Circular Causation Detection

Detects feedback loops and circular causation cycles based on Myrdal's cumulative causation concept.

```python
cycles = service.get_circular_causation(source_id=epa.id)

for cycle in cycles:
    print(f"Loop: {' -> '.join(cycle['labels'])}")
    print(f"Strength: {cycle['strength']:.2f}")
    print(f"Type: {cycle['feedback_type']}")  # "reinforcing" or "balancing"
```

**Interpretation:**
- **Strength > 0.5**: Strong feedback loop (likely to dominate system behavior)
- **Reinforcing**: Amplifies initial change (virtuous/vicious cycle)
- **Balancing**: Dampens change toward equilibrium (regulatory feedback)

### Institutional Holarchy

Maps nested hierarchical structures of institutions (holons within holons) based on Koestler's holarchy concept.

```python
holarchy = service.get_holarchy(institution_id=epa.id)

print(f"Organizational depth: {holarchy['depth']}")
print(f"Total institutions: {holarchy['total_institutions']}")

# Interpretation:
# Depth 3-5: Typical bureaucratic hierarchy
# Depth > 5: Deep hierarchy (potential coordination challenges)
```

### Conflict Detection

Identifies value conflicts, resource conflicts, and institutional contradictions.

```python
conflicts = service.get_conflicts()

for conflict in conflicts:
    print(f"{conflict['severity'].upper()}: {conflict['description']}")
    print(f"Type: {conflict['type']}")
```

---

## Performance & Scaling

### NetworkX Backend Benchmarks

```
Operation                    Performance
─────────────────────────────────────────────
Node creation               164,965 nodes/sec
Individual relationships    703 rels/sec
Bulk relationships          703,310 rels/sec (210x faster)
Query scans                 2.2M-4.7M items/sec
Adjacency lookups           O(1) constant time
```

### Scaling Recommendations

| Graph Size | Backend | Creation Method | Notes |
|------------|---------|----------------|-------|
| < 1,000 nodes | NetworkX | Individual | Excellent performance |
| 1K-10K nodes | NetworkX | **Bulk required** | Use `create_relationships_bulk()` |
| > 10K nodes | **Neo4j** | Bulk | Indexed, constant-time operations |

**Migration Path**: Start with NetworkX for prototyping → Switch to bulk operations when >500 relationships → Migrate to Neo4j when >20K relationships.

### Memory Estimation

```
Node: ~500 bytes (base) + metadata
Relationship: ~400 bytes (with all fields) + metadata

10k nodes + 30k rels ≈ 17MB
100k nodes + 300k rels ≈ 170MB
1M nodes + 3M rels ≈ 1.7GB
```

---

## Documentation

### Comprehensive Guides

- **[Analysis Methods Guide](docs/ANALYSIS_METHODS_GUIDE.md)** (31.3KB) - Complete guide to all analysis methods with examples, interpretation guidelines, and best practices
- **[Neo4j Integration Guide](docs/NEO4J_INTEGRATION_GUIDE.md)** (13.5KB) - Backend setup, migration from NetworkX, Cypher query examples
- **[Scaling Guide](docs/SCALING_GUIDE.md)** (13.5KB) - Performance tuning, backend selection, troubleshooting

### Example Scripts

- **`examples/rest_api_demo.py`** (9.9KB) - Complete REST API workflow demonstration
- **`examples/neo4j_integration_demo.py`** (13.0KB) - Neo4j backend usage and migration
- **`examples/backend_migration_demo.py`** (13.5KB) - NetworkX to Neo4j migration example

### API Documentation

**Interactive Documentation** (when server running):
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

**Test Suite**: 501 passing tests covering all components
```bash
pytest tests/ -v --cov
```

---

## Project Structure

```
sfm-core/
├── models/                         # 40+ domain models (12 modules)
│   ├── base_nodes.py              # Core Node class with versioning
│   ├── sfm_enums.py               # Comprehensive enum definitions (166KB)
│   ├── institutional_analysis.py  # Institutional structures
│   ├── policy_framework.py        # Policy instruments
│   ├── economic_analysis.py       # Transaction costs, coordination
│   ├── cultural_analysis.py       # Value systems, beliefs
│   └── ...                        # 6 more domain modules
├── graph/                          # Graph structures & queries
│   ├── sfm_graph.py               # Core graph with relationships
│   ├── sfm_query.py               # Query engine (43.4KB)
│   └── sfm_persistence.py         # Save/load operations
├── data/                           # Repository backends
│   ├── repositories.py            # NetworkX implementation
│   └── neo4j_repository.py        # Neo4j implementation
├── api/                            # Service & REST API
│   ├── sfm_service.py             # Unified service facade (42.8KB)
│   └── rest/                      # FastAPI application
│       ├── app.py                 # FastAPI setup
│       ├── schemas.py             # Pydantic request/response models
│       └── routers/               # 5 router modules (30+ endpoints)
├── docs/                           # Documentation (3 comprehensive guides)
├── examples/                       # Demonstration scripts
├── tests/                          # Test suite (501 tests)
├── docker-compose.yml              # Docker deployment
└── requirements.txt                # Python dependencies
```

---

## Use Cases

1. **Policy Impact Analysis** - Model policy instruments, institutional arrangements, and evaluate impacts
2. **Institutional Economics Research** - Analyze institutional evolution, path dependency, ceremonial dominance
3. **Environmental Regulation Modeling** - Clean Air Act case study with temporal evolution and uncertainty
4. **Technology Systems Analysis** - Track technology readiness levels, innovation diffusion
5. **Cultural and Value System Analysis** - Map value conflicts, belief systems, social capital

---

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Run tests (`pytest tests/`)
4. Commit changes (`git commit -m 'Add amazing feature'`)
5. Push to branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

**Development Setup:**
```bash
pip install -r requirements.txt
pip install -e .
pytest tests/ --cov
```

---

## License

GPL-3.0 License - See LICENSE file for details

---

## Citation

If you use SFM Core in your research, please cite:

```
F. Gregory Hayden (1988). "Values, Beliefs and Attitudes in a Sociotechnical 
Setting." Economic Issues, 22(2), 415-432.

SFM Core Framework (2026). Social Fabric Matrix Graph Service. 
GitHub: https://github.com/SFM-Graph-Service/sfm-core
```

---

## Contact & Support

- **Issues**: [GitHub Issues](https://github.com/SFM-Graph-Service/sfm-core/issues)
- **Documentation**: [docs/](docs/)
- **API Docs**: Run server and visit `/docs`

---

**Status**: Production-ready | **Version**: 0.1.0 | **Python**: 3.9+ | **Tests**: 501 passing ✓
