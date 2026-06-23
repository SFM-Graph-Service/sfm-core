# sfm-core — Social Fabric Matrix Graph Service

[![CI](https://github.com/SFM-Graph-Service/sfm-core/actions/workflows/ci.yml/badge.svg)](https://github.com/SFM-Graph-Service/sfm-core/actions/workflows/ci.yml)
[![Code Quality](https://github.com/SFM-Graph-Service/sfm-core/actions/workflows/code-quality.yml/badge.svg)](https://github.com/SFM-Graph-Service/sfm-core/actions/workflows/code-quality.yml)
[![Security](https://github.com/SFM-Graph-Service/sfm-core/actions/workflows/security.yml/badge.svg)](https://github.com/SFM-Graph-Service/sfm-core/actions/workflows/security.yml)
[![Performance](https://github.com/SFM-Graph-Service/sfm-core/actions/workflows/performance.yml/badge.svg)](https://github.com/SFM-Graph-Service/sfm-core/actions/workflows/performance.yml)
[![Documentation](https://github.com/SFM-Graph-Service/sfm-core/actions/workflows/documentation.yml/badge.svg)](https://github.com/SFM-Graph-Service/sfm-core/actions/workflows/documentation.yml)
[![PyPI](https://img.shields.io/pypi/v/sfm-core)](https://pypi.org/project/sfm-core/)
[![Python](https://img.shields.io/pypi/pyversions/sfm-core)](https://pypi.org/project/sfm-core/)
[![License](https://img.shields.io/badge/License-GPL--3.0-blue.svg)](https://github.com/SFM-Graph-Service/sfm-core/blob/main/LICENSE)
[![DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.20418500-blue)](https://doi.org/10.5281/zenodo.20418500)

An experimental Python framework implementing F. Gregory Hayden's Social Fabric Matrix (SFM) methodology for modeling, analyzing, and querying socio-economic systems through graph-based data structures.

**Status**: This is experimental research software under active development. The implementation is based on interpretation of Hayden's published work, particularly:

> Hayden, F. G. (2006). *Policymaking for a Good Society: The Social Fabric Matrix Approach to Policy Analysis and Program Evaluation*. Springer.

This software is intended for academic evaluation and institutional economics research.

**Implementation Fidelity Note**: This implementation interprets Hayden's Social Fabric Matrix methodology based on published literature. There are known structural differences from Hayden's canonical approach (e.g., current matrix uses institution×criteria instead of component×component structure). See project documentation for details.

**AI Assistance Disclosure**: Claude AI was used extensively throughout code development, documentation, and architectural design. All outputs should be independently verified. Known limitations exist in the implementation.

**Key Features:**
- **40+ Specialized Node Types** across 12 analytical domains for institutional economic modeling
- **Dual-Backend Architecture**: NetworkX (in-memory, 700K rels/sec) or Neo4j (persistent, production-scale)
- **Advanced Analysis**: Ceremonial vs instrumental classification, circular causation detection, institutional holarchy mapping, conflict detection, normative criteria evaluation
- **Temporal & Uncertainty Support**: Track institutional evolution over time with confidence intervals and uncertainty propagation
- **REST API**: 30+ FastAPI endpoints with OpenAPI documentation
- **Performance Optimized**: 210x speedup with bulk operations, handles 50K+ nodes efficiently
- **Hayden Case Studies**: 4 complete implementations with cross-case comparison and Excel export

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

**📖 For detailed setup instructions, see [SETUP_GUIDE.md](SETUP_GUIDE.md)**

### Requirements

- **Python**: 3.9 or higher (3.10+ recommended)
- **System Dependencies**: graphviz (for visualization)
- **Optional**: Docker & Docker Compose (for Neo4j backend)

### Quick Install (Local Development)

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

# Run test suite
pytest tests/
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

### Framework Bridges Demo

Bridge SFM with established frameworks (Doughnut Economics, Ostrom SES/IAD):

```python
from graph.doughnut_bridge import boundary_state_to_delivery
from examples.framework_bridges.ostrom_ses_iad_example import build_ostrom_ses_iad_sfm

# Doughnut Economics: Convert continuous indicators to SFM delivery weights
# Example: CO2 emissions (ecological ceiling, overshoot polarity)
co2_weight = boundary_state_to_delivery(
    indicator_value=420,  # ppm CO2
    threshold=350,        # safe planetary boundary
    polarity="overshoot"
)
print(f"CO2 delivery weight: {co2_weight:.2f}")  # -0.20 (driving overshoot)

# Example: Income access (social foundation, shortfall polarity)
income_weight = boundary_state_to_delivery(
    indicator_value=0.65,  # 65% have adequate income
    threshold=0.95,        # 95% target
    polarity="shortfall"
)
print(f"Income delivery weight: {income_weight:.2f}")  # -0.32 (shortfall)

# Ostrom SES/IAD: Build complete worked example
matrix, service = build_ostrom_ses_iad_sfm()
print(f"Components: {len(matrix.components)}")  # 9 (actors, rules, resource system)
print(f"Action situations: {len(matrix.get_non_empty_cells())}")  # 5+ delivery cells

# See docs/framework_bridges.md for full methodology
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

### Visualize Case Studies

All case studies can be visualized using built-in NetworkX converters:

```python
from examples.hayden_case_studies.director_networks import create_director_network_matrix
from graph.converters import to_multidigraph
from graph.centrality import compute_centrality_metrics
import networkx as nx
import matplotlib.pyplot as plt

# Load case study
matrix, service = create_director_network_matrix()

# Convert to NetworkX graph
G = to_multidigraph(matrix, service)

# Visualize with matplotlib
plt.figure(figsize=(12, 8))
pos = nx.spring_layout(G, k=0.5, iterations=50)

# Draw network
nx.draw_networkx_nodes(G, pos, node_size=1000, node_color='lightblue', alpha=0.9)
nx.draw_networkx_edges(G, pos, edge_color='gray', alpha=0.6, arrows=True, width=2)
nx.draw_networkx_labels(G, pos, {n: G.nodes[n]['label'] for n in G.nodes()}, 
                       font_size=10, font_weight='bold')

plt.title("Director Networks: Corporate Power Structure")
plt.axis('off')
plt.savefig('director_networks.png', dpi=300, bbox_inches='tight')
plt.show()

# Compute and display centrality metrics
centrality = compute_centrality_metrics(matrix, service)
print("\nTop 3 Power Brokers (Betweenness Centrality):")
sorted_betweenness = sorted(centrality['betweenness'].items(), 
                            key=lambda x: x[1], reverse=True)
for label, score in sorted_betweenness[:3]:
    print(f"  {label}: {score:.3f}")
```

**Export Formats:**
- **NetworkX Graph**: GEXF, GraphML (for Gephi, yEd)
- **System Dynamics**: XMILE (for Stella, Vensim, isee Exchange)
- **Spreadsheet**: Excel with matrix view + delivery details
- **High-Res**: PNG, PDF, SVG for publications

See [docs/VISUALIZATION_GUIDE.md](docs/VISUALIZATION_GUIDE.md) for complete examples including:
- Node sizing by centrality metrics
- Edge coloring by delivery type
- Interactive Plotly visualizations
- Circular causation highlighting
- Hierarchical layouts

### Persistence

Save and load your SFM graphs for later analysis or sharing. The service supports JSON (human-readable), compressed JSON (space-efficient), and pickle (fastest) formats.

```python
from api.sfm_service import SFMService, StorageFormat

service = SFMService()
# ... build your graph ...

# Save to JSON (human-readable, safe for sharing)
service.save("my_analysis.json", format_type=StorageFormat.JSON)

# Load later
service2 = SFMService()
service2.load("my_analysis.json", format_type=StorageFormat.JSON)

# Export snapshot for archival (includes metadata)
snapshot = service.export_snapshot()
# Later: service.import_snapshot(snapshot)
```

**Storage Formats**:
- `StorageFormat.JSON` - Human-readable, cross-platform compatible
- `StorageFormat.COMPRESSED` - Gzip-compressed JSON (70% size reduction)
- `StorageFormat.PICKLE` - Binary format (fastest, Python-only)

**Security Warning**: Only load pickle files from trusted sources. Pickle deserialization can execute arbitrary code.

See [docs/PERSISTENCE_GUIDE.md](docs/PERSISTENCE_GUIDE.md) for complete documentation including versioning, migration, and snapshot management.

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

| Backend | Performance (Synthetic Benchmarks) | Use Case | Strengths |
|---------|------------|----------|-----------|
| **NetworkX** (default) | 2-5M items/sec (in-memory scans)<br>700K rels/sec bulk creation | Development, prototyping<br>Graphs <10K nodes | Fast queries, no setup required<br>Excellent for research |
| **Neo4j** (production) | Indexed, constant-time ops<br>Multi-user concurrent | Production deployments<br>Graphs >10K nodes | Persistent storage, Cypher queries<br>Advanced graph algorithms |

**When to migrate**: Graph exceeds 20K relationships, need concurrent access, or require persistent storage without manual save/load.

---

## Core Features

### 1. Domain Models (40+ Node Types)

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
- Extensive enum validation (166KB enums covering flows, institutions, values)

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

### 5. Security Considerations

**File Import Security**: The CSV/Excel import adapters support optional path validation to prevent directory traversal attacks:

```python
from pathlib import Path
from data.importers import CSVImportAdapter, MappingTemplates

# INSECURE (default for backward compatibility):
adapter = CSVImportAdapter(MappingTemplates.basic_node())
# This allows reading ANY file path - only use with trusted sources

# SECURE (recommended for production file uploads):
adapter = CSVImportAdapter(
    MappingTemplates.basic_node(),
    allowed_base_dir=Path("/secure/upload/directory")
)
# This restricts file access to the specified directory tree
```

**Best Practices**:
- Enable path validation (`allowed_base_dir=...`) for user-uploaded files
- Use dedicated upload directories with restricted permissions
- CodeQL security scanning is enabled on this repository
- Review security alerts at: https://github.com/SFM-Graph-Service/sfm-core/security

### 7. Production Features

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

**Note**: These are synthetic benchmarks measured on a single machine. Real-world performance depends on data characteristics, query patterns, and hardware.

```
Operation                    Performance
─────────────────────────────────────────────
Node creation               164,965 nodes/sec
Individual relationships    703 rels/sec
Bulk relationships          703,310 rels/sec (210x faster)
Query scans (in-memory)     2.2M-4.7M items/sec
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
- **[Framework Bridges Guide](docs/framework_bridges.md)** - Methodological bridges to Doughnut Economics and Ostrom SES/IAD frameworks
- **[Neo4j Integration Guide](docs/NEO4J_INTEGRATION_GUIDE.md)** (13.5KB) - Backend setup, migration from NetworkX, Cypher query examples
- **[Scaling Guide](docs/SCALING_GUIDE.md)** (13.5KB) - Performance tuning, backend selection, troubleshooting

### Example Scripts

- **`examples/rest_api_demo.py`** (9.9KB) - Complete REST API workflow demonstration
- **`examples/neo4j_integration_demo.py`** (13.0KB) - Neo4j backend usage and migration
- **`examples/backend_migration_demo.py`** (13.5KB) - NetworkX to Neo4j migration example
- **`examples/framework_bridges/`** - Doughnut Economics and Ostrom SES/IAD bridge examples
  - `ostrom_ses_iad_example.py` - Complete community forest management case study

### Hayden Case Studies

Complete implementations of Social Fabric Matrix methodology based on Hayden's published research:

- **[Case Studies README](examples/hayden_case_studies/README.md)** - Overview, methodology, and citation guide
- **Clean Air Act 1970** (48KB) - Environmental policy with temporal evolution, criteria evaluation, and verified EPA data
- **Corporate Director Networks** (18KB) - Interlocking directorates analysis (Hayden, Wood & Kaya 2002)
- **Low-Level Radioactive Waste** (26KB) - Ceremonial-instrumental conflict analysis (Hayden & Bolduc 2000)
- **Nebraska K-12 Education Finance** (14KB) - TEEOSA formula system (Hoffman & Hayden 2007)
- **Cross-Case Comparison** - `compare_cases.py` generates comparative metrics table

**Run the comparison:**
```bash
python examples/hayden_case_studies/compare_cases.py
```

**Features Demonstrated:**
- Square N×N delivery matrices with multiple deliveries per cell
- Normative criteria evaluation (SERVES/UNDERMINES/NEUTRAL classification)
- Circular causation and feedback cycle detection
- Ceremonial vs instrumental conflict analysis
- Cultural values quantification
- Temporal modeling with phase transitions
- Excel export with cell descriptions

All case studies export to `.xlsx` format with three sheets: matrix view, cell descriptions (Hayden deliverable standard), and delivery details.

### Framework Bridges

Methodological bridges connecting SFM to established frameworks:

- **[Framework Bridges Guide](docs/framework_bridges.md)** - Complete methodology documentation
- **Doughnut Economics ↔ SFM** (`graph/doughnut_bridge.py`) - Convert continuous planetary/social boundaries to discrete delivery weights
  - 12 social foundations + 9 ecological ceilings
  - Linear scaling: distance from threshold → weight in [-1.0, +1.0]
  - Polarity-aware: shortfall (social) vs overshoot (ecological)
  - Validated with real-world examples (CO2, healthcare access, air pollution)
- **Ostrom SES/IAD ↔ SFM** (`examples/framework_bridges/ostrom_ses_iad_example.py`) - Encode institutional analysis
  - Actors → Nodes, Rules-in-Use → Nodes, Action Situations → Delivery Cells
  - Complete worked example: community forest management
  - Metadata tracking: ostrom_type, ostrom_role, ostrom_rule_type
  - 4 actors, 4 rules, 1 resource system, 3 outcomes, 5 action situations

**Research Contribution**: The mapping itself is a methodological contribution demonstrating how global sustainability frameworks and commons governance models can be operationalized at the institutional level through SFM analysis.

### API Documentation

**Interactive Documentation** (when server running):
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

**Test Suite**: 800 passing tests covering all components
```bash
pytest tests/ -v --cov
```

**Test Coverage Highlights:**
- Core graph operations: 150+ tests
- Analysis methods: 100+ tests
- Framework bridges: 31 tests (Doughnut + Ostrom)
- Hayden case studies: 80+ tests
- Import/export: 50+ tests
- REST API: 60+ tests

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
├── docs/                           # Documentation (3 guides)
├── examples/                       # Demonstration scripts
├── tests/                          # Test suite (678 tests)
├── docker-compose.yml              # Docker deployment
└── requirements.txt                # Python dependencies
```

---

## Use Cases

1. **Policy Impact Analysis** - Model policy instruments, institutional arrangements, and evaluate impacts against normative criteria
2. **Institutional Economics Research** - Analyze institutional evolution, path dependency, ceremonial dominance patterns
3. **Environmental Regulation Modeling** - Clean Air Act case study with temporal evolution and uncertainty propagation
4. **Technology Systems Analysis** - Track technology readiness levels, innovation diffusion, tool-skill-technology complexes
5. **Cultural and Value System Analysis** - Map value conflicts, belief systems, social capital, ceremonial vs instrumental tensions
6. **Sustainability Assessment** - Bridge to Doughnut Economics for planetary boundaries and social foundations analysis
7. **Commons Governance** - Bridge to Ostrom SES/IAD for analyzing collective action, rules-in-use, and resource management
8. **Cross-Framework Synthesis** - Integrate institutional economics (SFM), ecological economics (Doughnut), and commons governance (Ostrom)

---

## Contributing

### Research Collaboration Welcome

This is experimental research software implementing F. Gregory Hayden's Social Fabric Matrix methodology. We welcome:

**Methodological Contributions:**
- Validation of implementation fidelity to Hayden's published work
- Additional case studies from institutional economics literature
- Framework bridges to other methodologies (beyond Doughnut/Ostrom)
- Critiques and improvements to current mapping approaches

**Technical Contributions:**
- Performance optimizations and scaling improvements
- Additional backend implementations (graph databases, distributed systems)
- Analysis method enhancements (new algorithms, query optimizations)
- Data import/export adapters (additional formats, visualization tools)

**Research Applications:**
- Apply SFM Core to new policy domains or institutional systems
- Comparative institutional analysis across cases
- Integration with other modeling frameworks (ABM, system dynamics, etc.)
- Empirical validation studies

### How to Contribute

1. **For Research Questions**: Open a [GitHub Discussion](https://github.com/SFM-Graph-Service/sfm-core/discussions) to discuss methodology, interpretation, or application questions
2. **For Bug Reports**: Open a [GitHub Issue](https://github.com/SFM-Graph-Service/sfm-core/issues) with reproduction steps
3. **For Code Contributions**:
   - Fork the repository
   - Create a feature branch (`git checkout -b feature/amazing-feature`)
   - Run tests (`pytest tests/`)
   - Commit changes (`git commit -m 'Add amazing feature'`)
   - Push to branch (`git push origin feature/amazing-feature`)
   - Open a Pull Request

**Development Setup:**
```bash
pip install -r requirements.txt
pip install -e .
pytest tests/ --cov
```

### Research Feedback Needed

We are particularly interested in feedback on:

1. **Fidelity to Hayden's Methodology**: Does the implementation accurately reflect SFM as described in Hayden's published work? Known limitations are documented in [GitHub Issues](https://github.com/SFM-Graph-Service/sfm-core/issues).

2. **Framework Bridges Methodology**: Are the Doughnut Economics and Ostrom SES/IAD mappings methodologically sound? See [docs/framework_bridges.md](docs/framework_bridges.md) for current approach.

3. **Case Study Validity**: Do the Hayden case study implementations (Clean Air Act, Corporate Directors, etc.) correctly represent the original research? See [examples/hayden_case_studies/](examples/hayden_case_studies/).

4. **Research Applications**: What additional use cases or institutional domains would benefit from SFM modeling? What analysis methods are missing?

**Contact**: Open a [GitHub Discussion](https://github.com/SFM-Graph-Service/sfm-core/discussions) or email the maintainers.

---

## License

GPL-3.0 License - See LICENSE file for details

---

## Citation

If you use SFM Core in your research, please cite both:

**This software:**
```bibtex
@software{sfm_core_2026,
  author = {Dabbs, Garrick},
  title = {SFM Core: Social Fabric Matrix Graph Service},
  year = {2026},
  url = {https://github.com/SFM-Graph-Service/sfm-core},
  version = {0.7.0},
  doi = {10.5281/zenodo.20418500}
}
```

**For framework bridges specifically:**
```bibtex
@software{sfm_framework_bridges_2026,
  author = {Dabbs, Garrick},
  title = {Framework Bridges for Social Fabric Matrix: Doughnut Economics and Ostrom SES/IAD},
  year = {2026},
  url = {https://github.com/SFM-Graph-Service/sfm-core/tree/main/examples/framework_bridges},
  howpublished = {SFM Core v0.7.0},
  note = {Methodological bridges connecting SFM to Raworth's Doughnut Economics and Ostrom's SES/IAD frameworks}
}
```

**Hayden's foundational work:**
```bibtex
@book{hayden2006policymaking,
  author = {Hayden, F. Gregory},
  title = {Policymaking for a Good Society: The Social Fabric Matrix Approach to Policy Analysis and Program Evaluation},
  year = {2006},
  publisher = {Springer},
  isbn = {978-0-387-33812-8}
}
```

**DOI**: [![DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.20418500-blue)](https://doi.org/10.5281/zenodo.20418500)

---

## Contact & Support

- **Issues**: [GitHub Issues](https://github.com/SFM-Graph-Service/sfm-core/issues)
- **Documentation**: [docs/](docs/)
- **API Docs**: Run server and visit `/docs`

---

**Status**: Experimental Research Software | **Version**: 0.7.0 | **Python**: 3.9+ | **Tests**: 800 passing ✓
