# SFM Core Quickstart Guide

**Goal:** Get started with Social Fabric Matrix analysis in under 5 minutes.

## Installation

```bash
# Install from PyPI
pip install sfm-core

# Or install with optional dependencies
pip install sfm-core[neo4j]  # Production backend
pip install sfm-core[dev]    # Development tools
pip install sfm-core[all]    # All optional dependencies
```

**Requirements:** Python 3.9 or higher

## Your First SFM Analysis (3 Minutes)

Let's analyze a simple institutional system: EPA regulations influencing auto manufacturers.

### Step 1: Create the Service

```python
from api.sfm_service import SFMService
from models import Node
from graph.sfm_graph import Relationship

# Initialize service (uses fast in-memory NetworkX backend)
service = SFMService()
```

### Step 2: Create Institutional Nodes

```python
# Create institutions
epa = service.create_node(Node(
    label="EPA",
    description="Environmental Protection Agency",
    meta={
        "ceremonial_score": 0.3,  # More instrumental (problem-solving)
        "instrumental_score": 0.7,
        "jurisdiction": "Federal"
    }
))

auto_industry = service.create_node(Node(
    label="Auto Industry",
    description="Vehicle manufacturers",
    meta={
        "ceremonial_score": 0.6,  # More ceremonial (status quo)
        "instrumental_score": 0.4
    }
))

emission_standards = service.create_node(Node(
    label="Emission Standards",
    description="Clean Air Act vehicle emission requirements",
    meta={
        "instrumental_score": 0.8
    }
))

catalytic_converter = service.create_node(Node(
    label="Catalytic Converter Technology",
    description="Technology mandated by EPA to reduce emissions",
    meta={
        "instrumental_score": 0.9
    }
))
```

### Step 3: Create Relationships (Deliveries)

```python
# EPA mandates emission standards
service.create_relationship(Relationship(
    source_id=epa.id,
    target_id=emission_standards.id,
    kind="mandates",
    weight=0.9,
    meta={"delivery_type": "rule"}
))

# Standards require technology adoption
service.create_relationship(Relationship(
    source_id=emission_standards.id,
    target_id=catalytic_converter.id,
    kind="requires",
    weight=0.8,
    meta={"delivery_type": "requirement"}
))

# Auto industry implements technology
service.create_relationship(Relationship(
    source_id=auto_industry.id,
    target_id=catalytic_converter.id,
    kind="implements",
    weight=0.7,
    meta={"delivery_type": "action", "resistance": 0.4}
))

# Technology reduces emissions (feedback loop)
service.create_relationship(Relationship(
    source_id=catalytic_converter.id,
    target_id=emission_standards.id,
    kind="achieves_compliance",
    weight=0.6,
    meta={"delivery_type": "outcome"}
))
```

### Step 4: Run Analysis

```python
# Initialize query engine for advanced analysis
service.initialize_query_engine()

# Ceremonial vs Instrumental Analysis
analysis = service.get_ceremonial_analysis(threshold=0.5)
print(f"\n📊 Ceremonial/Instrumental Analysis:")
print(f"  Ceremonial nodes: {len(analysis['ceremonial_nodes'])}")
print(f"  Instrumental nodes: {len(analysis['instrumental_nodes'])}")
print(f"  Ratio: {analysis['ceremonial_ratio']:.2f}")
print(f"  Interpretation: {'Status quo dominance' if analysis['ceremonial_ratio'] > 1 else 'Innovation/problem-solving dominance'}")

# Detect Circular Causation (feedback loops)
cycles = service.get_circular_causation(source_id=epa.id)
print(f"\n🔄 Circular Causation Detection:")
if cycles:
    for cycle in cycles[:3]:  # Show first 3 cycles
        print(f"  Loop: {' → '.join(cycle['labels'])}")
        print(f"    Strength: {cycle['strength']:.2f}")
        print(f"    Type: {cycle['feedback_type']}")
else:
    print("  No feedback loops detected from EPA node")

# Get System Statistics
stats = service.get_statistics()
print(f"\n📈 System Statistics:")
print(f"  Total nodes: {stats.total_nodes}")
print(f"  Total relationships: {stats.total_relationships}")
print(f"  Network density: {stats.network_density:.3f}")
```

**Expected Output:**
```
📊 Ceremonial/Instrumental Analysis:
  Ceremonial nodes: 1
  Instrumental nodes: 3
  Ratio: 0.33
  Interpretation: Innovation/problem-solving dominance

🔄 Circular Causation Detection:
  Loop: EPA → Emission Standards → Catalytic Converter Technology → Emission Standards
    Strength: 0.43
    Type: balancing

📈 System Statistics:
  Total nodes: 4
  Total relationships: 4
  Network density: 0.333
```

## What Just Happened?

1. **Ceremonial vs Instrumental**: The system is instrumentally dominated (ratio < 1), meaning it's more focused on problem-solving (reducing emissions) than maintaining the status quo.

2. **Circular Causation**: We detected a balancing feedback loop where technology compliance feeds back into standards achievement, creating regulatory stability.

3. **Network Structure**: Low density (0.33) indicates a relatively sparse network with focused relationships.

## Next Steps

### Run a Real Case Study

```bash
# Nebraska K-12 Education Finance (Hayden's published work)
python examples/nebraska_k12_education.py

# Clean Air Act Analysis
python examples/clean_air_act_demo.py

# Corporate Director Networks
python examples/corporate_director_networks.py
```

### Explore the REST API

```bash
# Start the API server
uvicorn api.rest.app:app --reload

# View interactive docs
# http://localhost:8000/docs

# Example: Create node via API
curl -X POST http://localhost:8000/api/v1/nodes \
  -H "Content-Type: application/json" \
  -d '{
    "label": "Test Institution",
    "description": "Testing the API",
    "meta": {"ceremonial_score": 0.5}
  }'
```

### Scale to Neo4j Backend

For graphs >10,000 nodes, migrate to Neo4j:

```bash
# Start Neo4j
docker-compose up neo4j

# Set environment variables
export STORAGE_TYPE=neo4j
export NEO4J_URI=bolt://localhost:7687
export NEO4J_USERNAME=neo4j
export NEO4J_PASSWORD=neo4j_password

# Use Neo4j backend
from api.sfm_service import SFMService
service = SFMService()  # Automatically uses Neo4j when env vars set
```

See [Neo4j Integration Guide](NEO4J_INTEGRATION_GUIDE.md) for details.

### Learn Advanced Analysis

See [Analysis Methods Guide](ANALYSIS_METHODS_GUIDE.md) for:
- Institutional holarchy mapping
- Conflict detection
- Temporal evolution queries
- Uncertainty propagation
- Network centrality analysis

### Import Real Data

```python
from data.importers import CSVImportAdapter, MappingTemplates

# Import institutions from CSV
adapter = CSVImportAdapter(MappingTemplates.csv_institution())
result = service.import_bulk('institutions.csv', adapter=adapter)
print(f"Imported {result.success_count} institutions")
```

See examples in `examples/` directory for CSV format.

## Common Issues

### Import Error: "No module named 'api'"

```bash
# Install in development mode
pip install -e .

# Or ensure you're in the project directory
cd sfm-core
```

### NetworkX vs Neo4j Confusion

- **NetworkX** (default): In-memory, fast for <10K nodes, no setup required
- **Neo4j**: Persistent database, for >10K nodes, requires Docker

Start with NetworkX, migrate to Neo4j when needed.

### Low Performance with Large Graphs

```python
# Use bulk operations (210x faster)
# ❌ Don't do this:
for rel in relationships:
    service.create_relationship(rel)

# ✅ Do this instead:
service.create_relationships_bulk(relationships)
```

See [Scaling Guide](SCALING_GUIDE.md) for details.

## Understanding SFM Fidelity

This implementation interprets Hayden's methodology with some structural differences. See [SFM_FIDELITY_ANALYSIS.md](../SFM_FIDELITY_ANALYSIS.md) for:
- Known gaps from canonical SFM
- Implementation choices
- Fidelity scores by component
- Roadmap for improvements

**Current Overall Fidelity: 7.5/10**

## Resources

- **Full Documentation**: [README.md](../README.md)
- **Setup Guide**: [SETUP_GUIDE.md](SETUP_GUIDE.md)
- **Analysis Methods**: [ANALYSIS_METHODS_GUIDE.md](ANALYSIS_METHODS_GUIDE.md)
- **API Reference**: http://localhost:8000/docs (when server running)
- **Case Studies**: `examples/` directory
- **Issues & Questions**: [GitHub Issues](https://github.com/SFM-Graph-Service/sfm-core/issues)

## Citation

If you use SFM Core in your research:

```bibtex
@software{sfm_core_2026,
  author = {Dabbs, Garrick},
  title = {SFM Core: Social Fabric Matrix Graph Service},
  year = {2026},
  url = {https://github.com/SFM-Graph-Service/sfm-core},
  version = {0.1.0}
}
```

Also cite Hayden's foundational work:
> Hayden, F. G. (2006). *Policymaking for a Good Society: The Social Fabric Matrix Approach to Policy Analysis and Program Evaluation*. Springer.

---

**Ready to dive deeper?** Check out the [Analysis Methods Guide](ANALYSIS_METHODS_GUIDE.md) or run the example scripts!
