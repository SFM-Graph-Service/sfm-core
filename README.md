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

A Python framework for institutional analysis and policy modeling using graph-based methods. Build and analyze complex institutional systems through delivery-centric matrices, circular causation detection, and multi-framework integration.

**Core Capabilities:**
- **Institutional Modeling**: 40+ specialized node types for policy instruments, institutional structures, value systems, and economic mechanisms
- **Delivery-Centric Analysis**: Model multi-type deliveries (money, rules, authority, information) between institutional components
- **Advanced Graph Analytics**: Circular causation detection, network centrality, conflict identification, temporal evolution tracking
- **Multi-Framework Integration**: Bridges to Doughnut Economics, Ostrom SES/IAD frameworks
- **Production Ready**: Dual backends (NetworkX in-memory, Neo4j persistent), REST API, 990 passing tests

---

## Quick Start

### Installation

```bash
pip install sfm-core
```

Or for development:

```bash
git clone https://github.com/SFM-Graph-Service/sfm-core.git
cd sfm-core
pip install -e .
```

### Basic Usage

```python
from api.sfm_service import SFMService
from models import Node
from graph.sfm_graph import Relationship

# Initialize service
service = SFMService()

# Model institutional components
legislature = service.create_node(Node(
    label="State Legislature",
    description="Lawmaking body with budget authority"
))

school_districts = service.create_node(Node(
    label="School Districts",
    description="Local education providers"
))

# Create delivery relationship
funding_delivery = Relationship(
    source_id=legislature.id,
    target_id=school_districts.id,
    kind="delivers_funding",
    weight=0.85,
    meta={"delivery_type": "money", "annual_amount": 800_000_000}
)
service.create_relationship(funding_delivery)

# Run analysis
service.initialize_query_engine()
analysis = service.get_ceremonial_analysis(threshold=0.5)
cycles = service.get_circular_causation(source_id=legislature.id)

print(f"Found {len(cycles)} feedback loops")
print(f"Ceremonial/Instrumental ratio: {analysis['ceremonial_ratio']:.2f}")
```

---

## Use Cases

### Policy Impact Analysis
Model policy instruments, institutional arrangements, and regulatory frameworks. Evaluate impacts against normative criteria. Track temporal evolution and uncertainty propagation through policy pathways.

**Example**: Environmental regulation analysis with feedback loops between EPA standards, industry compliance, and environmental outcomes.

### Institutional Economics Research  
Analyze institutional evolution, path dependency, and ceremonial vs instrumental tensions. Identify circular causation patterns and institutional holarchies.

**Example**: Study power dynamics in corporate director networks or ceremonial dominance patterns in regulatory capture.

### Multi-Framework Synthesis
Integrate institutional economics (SFM) with ecological economics (Doughnut) and commons governance (Ostrom). Bridge continuous planetary boundaries to discrete institutional deliveries.

**Example**: Connect CO2 emissions thresholds to specific policy instruments and institutional actors.

### Technology Systems Analysis
Track technology readiness levels, innovation diffusion patterns, and tool-skill-technology complexes. Model feedback between technological change and institutional adaptation.

**Example**: Analyze adoption barriers for renewable energy technologies across institutional landscape.

### Sustainability Assessment
Apply Doughnut Economics framework to evaluate institutional performance against social foundations and ecological ceilings. Identify delivery gaps and institutional conflicts.

**Example**: Map institutional deliveries to 12 social foundations (healthcare, education, income) and 9 ecological boundaries (climate, biodiversity, pollution).

---

## Key Features

### 1. Delivery-Centric Matrices

Model complex institutional systems using square N×N matrices where components appear on both axes. Cells contain multiple heterogeneous deliveries (money + rules + authority in same cell).

```python
from models.delivery_matrix import SFMDeliveryMatrix, Delivery, SFMDeliveryCell

# Create delivery matrix
matrix = service.create_delivery_matrix(description="Education Finance System")
matrix.add_component(legislature.id)
matrix.add_component(school_districts.id)

# Add multiple deliveries to single cell
cell = SFMDeliveryCell(
    source_component_id=legislature.id,
    target_component_id=school_districts.id,
    cell_description="Legislature provides funding and regulatory oversight"
)

cell.add_delivery(Delivery(
    delivery_type="money",
    delivery_content="$800M annual appropriation",
    quantity=800_000_000,
    units="USD/year"
))

cell.add_delivery(Delivery(
    delivery_type="rule",
    delivery_content="Student enrollment reporting requirements"
))

cell.add_delivery(Delivery(
    delivery_type="authority",
    delivery_content="Audit power over district expenditures"
))

matrix.set_cell(cell)
```

**Features:**
- Multiple heterogeneous deliveries per cell
- Required cell descriptions (enforced validation)
- Temporal modeling (delivery rates, threshold monitoring)
- Export to Excel with matrix view + delivery details

### 2. Advanced Analysis Methods

**Circular Causation Detection:**
Identify feedback loops and cumulative causation patterns. Classify as reinforcing (virtuous/vicious cycles) or balancing (regulatory feedback).

```python
service.initialize_query_engine()
cycles = service.get_circular_causation(source_id=epa.id)

for cycle in cycles:
    print(f"Loop: {' → '.join(cycle['labels'])}")
    print(f"Strength: {cycle['strength']:.2f}")
    print(f"Type: {cycle['feedback_type']}")
```

**Ceremonial vs Instrumental Analysis:**
Classify institutional behaviors as status quo reinforcing (ceremonial) or problem-solving (instrumental). Identify system dominance patterns.

```python
analysis = service.get_ceremonial_analysis(threshold=0.5)
print(f"Ratio: {analysis['ceremonial_ratio']:.2f}")  # > 1.0 = ceremonial dominance
```

**Conflict Detection:**
Identify value conflicts, resource conflicts, and institutional contradictions with severity classification.

```python
conflicts = service.get_conflicts()
for conflict in conflicts:
    print(f"{conflict['severity'].upper()}: {conflict['description']}")
```

**Network Centrality:**
Compute betweenness, degree, closeness, and eigenvector centrality. Identify institutional bottlenecks and power brokers.

```python
from graph.centrality import compute_centrality_metrics
centrality = compute_centrality_metrics(matrix, service)
```

### 3. Multi-Framework Integration

**Doughnut Economics Bridge:**
Convert continuous planetary/social boundaries to discrete institutional delivery weights.

```python
from graph.doughnut_bridge import boundary_state_to_delivery

# CO2 emissions (ecological ceiling, overshoot polarity)
co2_weight = boundary_state_to_delivery(
    indicator_value=420,  # ppm CO2
    threshold=350,        # safe boundary
    polarity="overshoot"
)
# Returns: -0.20 (driving overshoot)

# Income access (social foundation, shortfall polarity)  
income_weight = boundary_state_to_delivery(
    indicator_value=0.65,  # 65% adequate income
    threshold=0.95,        # 95% target
    polarity="shortfall"
)
# Returns: -0.32 (shortfall)
```

**Ostrom SES/IAD Bridge:**
Encode commons governance analysis through actors, rules-in-use, and action situations.

```python
from examples.framework_bridges.ostrom_ses_iad_example import build_ostrom_ses_iad_sfm

matrix, service = build_ostrom_ses_iad_sfm()
# Returns: 9 components (4 actors, 4 rules, 1 resource)
#          5+ action situations (delivery cells)
```

See [docs/framework_bridges.md](docs/framework_bridges.md) for complete methodology.

### 4. Temporal & Uncertainty Modeling

**Temporal Evolution:**
Track institutional changes over time periods with versioning and event nodes.

```python
from datetime import datetime, timedelta

evolution = service._query_engine.query_temporal_evolution(
    start_date=datetime(1970, 1, 1),
    end_date=datetime(1990, 12, 31),
    time_step=timedelta(days=365*5)  # 5-year intervals
)

for snapshot in evolution:
    print(f"{snapshot['date']}: {snapshot['nodes']} nodes")
```

**Uncertainty Propagation:**
Compound uncertainty through causal pathways with confidence intervals.

```python
rel = Relationship(
    source_id=policy.id,
    target_id=outcome.id,
    kind="produces",
    weight=0.8,
    meta={"confidence_interval": [0.7, 0.9]}
)

result = service._query_engine.propagate_uncertainty_through_path([policy.id, outcome.id])
print(f"95% CI: ({result['uncertainty_range'][0]:.2f}, {result['uncertainty_range'][1]:.2f})")
```

### 5. Production Features

**Dual Backend Architecture:**

| Backend | Performance | Use Case |
|---------|-------------|----------|
| **NetworkX** (default) | 700K rels/sec bulk creation<br>2-5M items/sec queries | Development, <10K nodes |
| **Neo4j** (production) | Indexed constant-time ops<br>Multi-user concurrent | Production, >10K nodes |

**REST API** (30+ endpoints):
```bash
# Start server
uvicorn api.rest.app:app --host 0.0.0.0 --port 8000

# Access docs
curl http://localhost:8000/docs  # Swagger UI
```

**Export Formats:**
- **Excel**: Matrix view + cell descriptions + delivery details
- **System Dynamics**: XMILE format for Stella/Vensim
- **NetworkX**: GEXF, GraphML for external visualization tools (Gephi, yEd)
- **JSON**: Full graph state with metadata

> **Note**: sfm-core is a backend library focused on institutional analysis and graph operations. For interactive visualization and frontend applications, see [sfm-visualization](https://github.com/SFM-Graph-Service/sfm-visualization) - a modern React/Next.js frontend with network graphs, matrix heatmaps, and temporal animations.

**Persistence:**
```python
# Save analysis
service.save("my_analysis.json", format_type=StorageFormat.JSON)

# Load later
service.load("my_analysis.json", format_type=StorageFormat.JSON)
```

---

## Performance & Scaling

### Benchmarks (NetworkX Backend)

```
Operation                    Performance
─────────────────────────────────────────────
Node creation               164,965 nodes/sec
Bulk relationships          703,310 rels/sec
Query scans (in-memory)     2.2M-4.7M items/sec
```

### Scaling Recommendations

| Graph Size | Backend | Strategy |
|------------|---------|----------|
| < 1K nodes | NetworkX | Individual operations fine |
| 1K-10K nodes | NetworkX | Use `create_relationships_bulk()` |
| > 10K nodes | **Neo4j** | Migrate for indexed queries |

### Memory Estimation

```
10k nodes + 30k rels ≈ 17MB
100k nodes + 300k rels ≈ 170MB
1M nodes + 3M rels ≈ 1.7GB
```

---

## Documentation

### Comprehensive Guides

- **[Analysis Methods Guide](docs/ANALYSIS_METHODS_GUIDE.md)** - Complete guide to all analysis methods
- **[Framework Bridges Guide](docs/framework_bridges.md)** - Doughnut Economics and Ostrom SES/IAD integration
- **[Neo4j Integration Guide](docs/NEO4J_INTEGRATION_GUIDE.md)** - Production backend setup
- **[Scaling Guide](docs/SCALING_GUIDE.md)** - Performance tuning and optimization
- **[Visualization Project](docs/VISUALIZATION_PROJECT.md)** - Frontend/visualization separation and migration guide

### API Documentation

**Interactive Documentation** (when server running):
- Swagger UI: http://localhost:8000/docs  
- ReDoc: http://localhost:8000/redoc

### Example Applications

Complete worked examples demonstrating framework capabilities:

- **Framework Bridges** (`examples/framework_bridges/`)
  - Doughnut Economics integration
  - Ostrom SES/IAD community forest management
  
- **Policy Analysis** (`examples/`)
  - Environmental regulation modeling
  - Technology innovation systems
  - Institutional economics research

- **Hayden Case Studies** (`examples/hayden_case_studies/`)
  - 5 complete implementations from institutional economics literature
  - See [examples/hayden_case_studies/README.md](examples/hayden_case_studies/README.md) for methodology and citations
  - Demonstrates delivery-centric matrices, temporal modeling, and ceremonial-instrumental analysis

---

## Research & Methodology

This framework implements delivery-centric institutional analysis based on the Social Fabric Matrix methodology developed by F. Gregory Hayden. The implementation emphasizes:

- **Delivery-Centric Structure**: Components interact through explicit deliveries (money, rules, authority, information)
- **Multiple Deliveries Per Cell**: Single institutional relationships often involve multiple heterogeneous delivery types
- **Square Non-Symmetric Matrices**: Components on both axes, Cell(i,j) ≠ Cell(j,i)
- **Cell Descriptions as Deliverables**: Required narrative content explaining institutional relationships

**Reference:**
> Hayden, F. G. (2006). *Policymaking for a Good Society: The Social Fabric Matrix Approach to Policy Analysis and Program Evaluation*. Springer.

**Framework Integration Methodology:**

The Doughnut Economics and Ostrom SES/IAD bridges are methodological contributions demonstrating how global sustainability frameworks and commons governance models can be operationalized at the institutional level. See [docs/framework_bridges.md](docs/framework_bridges.md) for complete mapping methodology.

**Implementation Status:**

This is experimental research software under active development. Known limitations and future roadmap are documented in [GitHub Issues](https://github.com/SFM-Graph-Service/sfm-core/issues).

---

## Contributing

### Research Collaboration Welcome

We welcome contributions in:

**Methodological Validation:**
- Fidelity assessment of delivery-centric implementation
- Framework bridge validation (Doughnut, Ostrom)
- Additional case studies from institutional economics literature

**Technical Contributions:**
- Performance optimizations and scaling improvements
- Additional backend implementations
- Analysis method enhancements
- Data import/export adapters

**Research Applications:**
- Apply to new policy domains or institutional systems
- Comparative institutional analysis
- Integration with other modeling frameworks (ABM, system dynamics)
- Empirical validation studies

### How to Contribute

1. **Research Questions**: Open a [GitHub Discussion](https://github.com/SFM-Graph-Service/sfm-core/discussions)
2. **Bug Reports**: Open a [GitHub Issue](https://github.com/SFM-Graph-Service/sfm-core/issues)
3. **Code Contributions**: Fork → Feature Branch → Tests → Pull Request

**Development Setup:**
```bash
git clone https://github.com/SFM-Graph-Service/sfm-core.git
cd sfm-core
pip install -r requirements.txt
pip install -e .
pytest tests/ --cov
```

---

## Citation

If you use this framework in your research, please cite:

```bibtex
@software{sfm_core_2026,
  author = {Dabbs, Garrick},
  title = {SFM Core: Social Fabric Matrix Graph Service},
  year = {2026},
  url = {https://github.com/SFM-Graph-Service/sfm-core},
  version = {0.9.1},
  doi = {10.5281/zenodo.20418500}
}
```

For foundational methodology:

```bibtex
@book{hayden2006policymaking,
  author = {Hayden, F. Gregory},
  title = {Policymaking for a Good Society: The Social Fabric Matrix Approach to Policy Analysis and Program Evaluation},
  year = {2006},
  publisher = {Springer},
  isbn = {978-0-387-33812-8}
}
```

---

## License

GPL-3.0 License - See LICENSE file for details

---

## Contact & Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/SFM-Graph-Service/sfm-core/issues)  
- **Discussions**: [GitHub Discussions](https://github.com/SFM-Graph-Service/sfm-core/discussions)
- **API Docs**: Run server and visit `/docs`

---

**AI Assistance Disclosure**: Claude AI was used extensively in code development, documentation, and architectural design. All outputs should be independently verified for research applications.

**Status**: Experimental Research Software | **Version**: 0.9.1 | **Python**: 3.9+ | **Tests**: 991 passing ✓
