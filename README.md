# sfm-core — Social Fabric Matrix Graph Service

[![CI](https://github.com/SFM-Graph-Service/sfm-core/actions/workflows/ci.yml/badge.svg)](https://github.com/SFM-Graph-Service/sfm-core/actions/workflows/ci.yml)
[![Code Quality](https://github.com/SFM-Graph-Service/sfm-core/actions/workflows/code-quality.yml/badge.svg)](https://github.com/SFM-Graph-Service/sfm-core/actions/workflows/code-quality.yml)
[![Security](https://github.com/SFM-Graph-Service/sfm-core/actions/workflows/security.yml/badge.svg)](https://github.com/SFM-Graph-Service/sfm-core/actions/workflows/security.yml)
[![Performance](https://github.com/SFM-Graph-Service/sfm-core/actions/workflows/performance.yml/badge.svg)](https://github.com/SFM-Graph-Service/sfm-core/actions/workflows/performance.yml)
[![Documentation](https://github.com/SFM-Graph-Service/sfm-core/actions/workflows/documentation.yml/badge.svg)](https://github.com/SFM-Graph-Service/sfm-core/actions/workflows/documentation.yml)

A unified Python library implementing F. Gregory Hayden's Social Fabric Matrix (SFM) methodology for modeling, analyzing, and querying complex socio-economic systems through graph-based data structures and sophisticated analysis tools.

The Social Fabric Matrix framework enables researchers, policy analysts, and decision-makers to model complex interdependencies within socio-economic systems, analyze policy impacts through interconnected networks, and trace the effects of interventions using advanced graph algorithms. This core library provides a clean, domain-organized model layer that separates SFM theory from implementation details, offering type-safe data models with comprehensive enum validation and extensible architecture suitable for both research prototyping and production-scale policy analysis applications.

## Installation

### Requirements
- Python 3.9+
- NetworkX 3.0+
- Additional dependencies listed in requirements.txt

### Setup

```bash
# Install from PyPI (when published)
pip install sfm-core

# Or install from source
git clone https://github.com/SFM-Graph-Service/sfm-core.git
cd sfm-core
pip install -r requirements.txt
pip install -e .
```

### Verification

```bash
# Run the test suite to verify installation
python -m unittest discover tests -v

# Test basic functionality
python -c "from models.base_nodes import Node; from models.sfm_enums import ActorSector; print('Installation successful')"
```

## Quick Start

### Basic Usage

```python
from models.base_nodes import Node
from models.institutional_analysis import Institution, InstitutionalArrangement
from models.policy_framework import PolicyInstrument
from models.economic_analysis import TransactionCost
from models.sfm_enums import (
    InstitutionLayer,
    PolicyInstrumentType,
    TransactionCostType,
    EnumValidator
)

# Create institutional entities with proper typing
formal_rule = Institution(
    label="Agricultural Subsidy Program",
    layer=InstitutionLayer.FORMAL_RULE,
    description="Federal program providing subsidies to farmers"
)

# Create policy instruments
subsidy = PolicyInstrument(
    label="Direct Payment Subsidy",
    instrument_type=PolicyInstrumentType.ECONOMIC,
    target_behavior="Increase crop production"
)

# Analyze transaction costs
coordination_cost = TransactionCost(
    label="Subsidy Application Processing",
    cost_type=TransactionCostType.COORDINATION,
    magnitude=0.3,
    description="Administrative burden of processing applications"
)

# Use enum validation
validator = EnumValidator()
is_valid = validator.validate_policy_instrument(
    PolicyInstrumentType.ECONOMIC,
    InstitutionLayer.FORMAL_RULE
)
print(f"Policy instrument valid for context: {is_valid}")

# Create institutional arrangements
arrangement = InstitutionalArrangement(
    label="Agricultural Support Framework",
    participants=["USDA", "Farm Bureau", "County Extension Offices"],
    formal_rules=["7 U.S.C. § 1308"],
    informal_norms=["Community support", "Sustainable practices"]
)
```

### Working with Specialized Components

```python
from models.technology_integration import TechnologySystem
from models.cultural_analysis import ValueSystem
from models.network_analysis import DeliveryRelationship
from models.sfm_enums import TechnologyReadinessLevel, ValueCategory

# Model technology systems
precision_ag = TechnologySystem(
    label="Precision Agriculture Platform",
    trl=TechnologyReadinessLevel.TRL_7,
    description="GPS-guided farming equipment and analytics"
)

# Track value systems
sustainability = ValueSystem(
    label="Environmental Sustainability",
    value_category=ValueCategory.ENVIRONMENTAL,
    legitimacy_source="Public consensus and scientific evidence"
)

# Define delivery relationships
extension_service = DeliveryRelationship(
    label="County Extension Services",
    service_type="Technical assistance",
    delivery_mechanism="In-person consultations and workshops",
    coverage_area="County-level",
    effectiveness=0.75
)
```

## REST API

SFM Core provides a production-ready REST API built with FastAPI, exposing all framework capabilities via HTTP endpoints.

### Quick Start with REST API

```bash
# Start the development server
uvicorn api.rest.app:app --reload

# Access interactive documentation
open http://localhost:8000/api/v1/docs
```

### API Endpoints

**Health & Diagnostics**:
- `GET /api/v1/health` - Service health and graph statistics
- `GET /api/v1/statistics` - Detailed graph statistics

**Node CRUD**:
- `POST /api/v1/nodes/` - Create node
- `GET /api/v1/nodes/{id}` - Get node by ID
- `PUT /api/v1/nodes/{id}` - Update node
- `DELETE /api/v1/nodes/{id}` - Delete node
- `GET /api/v1/nodes/` - List all nodes (with optional type filter)
- `GET /api/v1/nodes/types` - List all available node types
- `DELETE /api/v1/nodes/clear` - Clear all data

**Query Analysis** (Phase 2):
- `POST /api/v1/query/ceremonial` - Ceremonial vs instrumental analysis
- `GET /api/v1/query/circular-causation/{source_id}` - Circular causation detection
- `GET /api/v1/query/holarchy/{institution_id}` - Institutional holarchy
- `GET /api/v1/query/conflicts` - Conflict detection

**Evaluation** (Phase 3):
- `POST /api/v1/evaluate/digraph` - Digraph analysis
- `GET /api/v1/evaluate/circular-causation/{process_id}` - Process dynamics
- `GET /api/v1/evaluate/conflict-detection/{system_id}` - System conflicts
- `GET /api/v1/evaluate/cross-impact/{cell_id}` - Cross-impact effects
- `GET /api/v1/evaluate/delivery-performance/{relationship_id}` - Delivery performance
- `GET /api/v1/evaluate/network-performance/{network_id}` - Network health
- `GET /api/v1/evaluate/path-dependency/{institution_id}` - Path dependency
- `GET /api/v1/evaluate/value-system/{value_system_id}` - Value coherence
- `GET /api/v1/evaluate/belief-stability/{belief_id}` - Belief stability
- `GET /api/v1/evaluate/attitude-mediation/{attitude_id}` - Attitude mediation
- `GET /api/v1/evaluate/system-holarchy/{holarchy_id}` - Holarchy coherence

### API Example

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# Create a node
response = requests.post(
    f"{BASE_URL}/nodes/",
    json={
        "label": "Federal Reserve",
        "description": "Central banking system",
        "node_type": "Institution",
        "meta": {"established": "1913"}
    }
)
node = response.json()

# Run ceremonial analysis
analysis = requests.post(
    f"{BASE_URL}/query/ceremonial",
    json={"threshold": 0.5}
).json()

print(f"Ceremonial ratio: {analysis['ceremonial_ratio']}")
```

### Docker Deployment

```bash
# Development (NetworkX backend)
docker-compose up api-dev

# Production (Neo4j backend)
docker-compose up api-neo4j neo4j

# Access API at http://localhost:8000
# Neo4j browser at http://localhost:7474
```

### API Documentation

- **Interactive Docs**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc
- **OpenAPI Spec**: http://localhost:8000/api/v1/openapi.json
- **Detailed Guide**: See [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
- **Neo4j Integration**: See [docs/NEO4J_INTEGRATION_GUIDE.md](docs/NEO4J_INTEGRATION_GUIDE.md)
- **Example Scripts**: [examples/rest_api_demo.py](examples/rest_api_demo.py), [examples/neo4j_integration_demo.py](examples/neo4j_integration_demo.py), [examples/backend_migration_demo.py](examples/backend_migration_demo.py)

## Module Map

The `sfm-core` library is organized into 12 focused domain modules, each addressing a specific aspect of the Social Fabric Matrix framework:

| Module | Description |
|--------|-------------|
| **base_nodes** | Base Node class and core infrastructure for all SFM entities |
| **sfm_enums** | Comprehensive enum definitions for SFM framework values, institutions, resources, flows, and relationships with validation logic |
| **institutional_analysis** | Institutional structures, path dependencies, and institutional arrangements following Hayden's three-layer framework |
| **policy_framework** | Policy instruments, value judgments, and problem-solving sequences for policy development and analysis |
| **economic_analysis** | Transaction costs, coordination mechanisms, commons governance, and economic aspects of institutions |
| **cultural_analysis** | Cultural values, belief systems, norms, and social cohesion components |
| **network_analysis** | Cross-impact analysis, delivery relationships, network structures, and system interactions |
| **system_analysis** | System-level properties, metrics, feedback loops, and comprehensive system analysis |
| **technology_integration** | Technology systems, innovation tracking, and Technology Readiness Level (TRL) assessment |
| **social_assessment** | Social capital, power structures, equity analysis, and social welfare metrics |
| **methodological_framework** | Research methods, analytical frameworks, and SFM methodology implementation |
| **complex_analysis** | Multi-level analysis, emergence properties, and complex adaptive systems modeling |

## Documentation

For comprehensive documentation, design rationale, and advanced usage examples, see:

- **[docs/](docs/)** — Full documentation including:
  - **SFM Overview** — Theoretical foundation and Hayden's methodology
  - **Design Proposal** — Comprehensive architectural design and extensibility roadmap
  - **Module Documentation** — Detailed guides for each domain module
  - **Hayden SFM Alignment** — Methodological compliance and theoretical accuracy
  - **Enum Validation Guide** — Using the validation system effectively

## Architecture

### Design Principles

**sfm-core** implements a clean, domain-organized architecture that prioritizes:

1. **Theory-Practice Separation**: SFM domain models are isolated from implementation details (repositories, query engines, APIs)
2. **Domain Organization**: Each module represents a coherent analytical domain within Hayden's framework
3. **Type Safety**: Strong typing with comprehensive validation ensures data integrity and developer experience
4. **Extensibility**: Clean interfaces allow new analysis methods and storage backends without modifying core models
5. **Hayden Compliance**: Faithful implementation of SFM theoretical framework with methodological rigor

### Module Organization

```
sfm-core/
├── models/                         # Domain model implementations
│   ├── base_nodes.py              # Base Node class and infrastructure
│   ├── sfm_enums.py               # Comprehensive enumeration definitions
│   ├── institutional_analysis.py  # Institutional structures and arrangements
│   ├── policy_framework.py        # Policy instruments and value judgments
│   ├── economic_analysis.py       # Transaction costs and coordination
│   ├── cultural_analysis.py       # Cultural values and belief systems
│   ├── network_analysis.py        # Network structures and interactions
│   ├── system_analysis.py         # System-level properties and feedback
│   ├── technology_integration.py  # Technology systems and innovation
│   ├── social_assessment.py       # Social capital and equity analysis
│   ├── methodological_framework.py # Research methods and frameworks
│   └── complex_analysis.py        # Multi-level and emergence modeling
├── docs/                          # Documentation and design materials
├── tests/                         # Comprehensive test suite
├── examples/                      # Example implementations
└── pyproject.toml                 # Python project configuration
```

### Data Model Philosophy

The **sfm-core** library provides pure data models representing Hayden's Social Fabric Matrix entities:

- **Actors**: Decision-making entities (agencies, firms, individuals) with sector classification
- **Institutions**: Three-layer institutional framework (formal rules, organizations, informal norms)
- **Resources**: Stocks and assets with comprehensive type validation
- **Processes**: Transformation activities with input/output flow tracking
- **Relationships**: Semantic connections between entities with validation rules
- **Policies**: Formal interventions with authority attribution and instrument typing
- **Values**: Cultural and institutional value frameworks
- **Technology**: Innovation tracking with Technology Readiness Level assessment

These models are designed to be **consumed** by higher-level services that provide:
- Repository patterns and storage backends (NetworkX, Neo4j, etc.)
- Query engines for network analysis and policy impact assessment
- Service layers for simplified API access
- Visualization and export capabilities

## Contributing

We welcome contributions to the Social Fabric Matrix Core Library! This project follows open-source best practices.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/SFM-Graph-Service/sfm-core.git
cd sfm-core

# Install in development mode with all dependencies
pip install -r requirements.txt
pip install -e .

# Run tests to verify setup
python -m unittest discover tests -v
```

### Historical Scenario Analysis

The `scenarios/` directory contains templates and frameworks for building SFM models of real-world historical policies. These scenarios serve to:

- **Validate** the framework's applicability to actual policy analysis
- **Discover gaps** in node types, relationships, and analytical methods  
- **Demonstrate** best practices for applying Hayden's SFM methodology
- **Provide** reference models for future work

**Quick Start**:

```bash
# Review the detailed Clean Air Act prompt
cat prompts/clean_air_act_scenario.md

# Run the starter script (needs research to complete)
python scenarios/clean_air_act_starter.py
```

**Key Features**:
- Multi-source fact verification requirements (2+ sources per claim)
- Evidence-based relationship weight justification
- Comprehensive gap analysis framework
- Structured deliverables (model, documentation, findings)

See [`scenarios/README.md`](scenarios/README.md) for complete instructions and guidelines.

### Development Guidelines

- Follow existing code structure and naming conventions
- Add comprehensive tests for new functionality
- Ensure compatibility with existing examples
- Use type hints and docstrings for all public methods
- Follow PEP 8 style guidelines

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Roadmap

### Current Release (v0.1.0)
- [x] Unified domain-organized model layer
- [x] 12 focused analytical domain modules
- [x] Comprehensive enum validation system
- [x] Type-safe data models with proper inheritance
- [x] Full SFM theoretical coverage

### Near Term (v0.2.0)
- [ ] Enhanced documentation with usage examples
- [ ] Additional specialized node types
- [ ] Extended enum validation capabilities
- [ ] Integration examples with graph backends

### Medium Term (v0.3.0)
- [ ] Performance optimizations for large models
- [ ] Additional analytical frameworks
- [ ] Enhanced metadata and versioning support
- [ ] Multi-language support for international applications

---

*The sfm-core library provides a robust foundation for implementing F. Gregory Hayden's Social Fabric Matrix methodology in modern Python applications.*
