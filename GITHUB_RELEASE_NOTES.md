# SFM Core v0.1.0 - Initial Release

**First public release of the Social Fabric Matrix (SFM) graph analysis framework.**

## Overview

SFM Core implements F. Gregory Hayden's Social Fabric Matrix methodology for analyzing institutional systems through graph-based networks. This experimental research software provides tools for policy analysis, institutional economics research, and systems modeling.

**Fidelity Disclosure**: This implementation interprets Hayden's methodology with known structural differences (see `SFM_FIDELITY_ANALYSIS.md`). Current fidelity: 7.5/10. Full transparency documentation included.

**AI Assistance Disclosure**: Developed with extensive Claude AI (Anthropic) assistance throughout architecture, implementation, testing, and documentation. All outputs independently verified by human author.

## Key Features

### Core Capabilities
- **40+ Specialized Node Types** across 12 analytical domains (institutions, technologies, values, rules, etc.)
- **Dual Backend Architecture**: Fast in-memory NetworkX (default) or scalable Neo4j (10K+ nodes)
- **REST API**: FastAPI-based service with interactive OpenAPI documentation
- **Advanced Analysis**:
  - Ceremonial vs Instrumental classification
  - Circular causation detection (feedback loops)
  - Institutional holarchy mapping
  - Network centrality and influence metrics
  - Temporal evolution queries

### Data Import/Export
- **Import Formats**: CSV, JSON, OECD API, World Bank API
- **Export Formats**: JSON, GraphML, PNG visualization
- **Bulk Operations**: 210x performance improvement over individual operations

### Validation & Testing
- **678 test cases** with 92% coverage
- **Case Studies**: Nebraska K-12 education, corporate director networks, Clean Air Act analysis
- **Performance**: NetworkX handles <10K nodes in-memory; Neo4j scales to millions

## Installation

```bash
# Install from PyPI (minimal dependencies)
pip install sfm-core

# With Neo4j backend support
pip install sfm-core[neo4j]

# With visualization tools
pip install sfm-core[visualization]

# All optional dependencies
pip install sfm-core[all]

# Development tools
pip install sfm-core[dev]
```

**Requirements**: Python 3.9+

## Quick Start

```python
from api.sfm_service import SFMService
from models import Node
from graph.sfm_graph import Relationship

# Create service (uses fast NetworkX backend)
service = SFMService()

# Create institutional nodes
epa = service.create_node(Node(
    label="EPA",
    description="Environmental Protection Agency",
    meta={"ceremonial_score": 0.3, "instrumental_score": 0.7}
))

# Run analysis
service.initialize_query_engine()
analysis = service.get_ceremonial_analysis(threshold=0.5)
cycles = service.get_circular_causation(source_id=epa.id)
```

Full quickstart: [docs/QUICKSTART.md](docs/QUICKSTART.md)

## Documentation

- **Setup Guide**: [docs/SETUP_GUIDE.md](docs/SETUP_GUIDE.md)
- **Analysis Methods**: [docs/ANALYSIS_METHODS_GUIDE.md](docs/ANALYSIS_METHODS_GUIDE.md)
- **Fidelity Analysis**: [SFM_FIDELITY_ANALYSIS.md](SFM_FIDELITY_ANALYSIS.md)
- **API Reference**: http://localhost:8000/docs (when server running)
- **Contributing**: [CONTRIBUTORS.md](CONTRIBUTORS.md)

## Known Limitations

### Implementation Fidelity
- Square matrix structure not implemented (7.5/10 overall fidelity)
- Delivery model simplified compared to Hayden's canonical approach
- Temporal modeling limited (no graphical clocks)
- See `SFM_FIDELITY_ANALYSIS.md` for complete analysis

### Performance
- NetworkX backend: <10K nodes recommended
- Neo4j backend required for larger graphs
- Benchmark results from 16-core machine (adjust expectations for CI/slower hardware)

### AI Assistance
- Extensive AI (Claude Sonnet 4.5) used throughout development
- All code and analysis independently verified by human author
- Users should validate outputs for their specific use cases

## Academic Citation

If you use SFM Core in your research, please cite both:

**This software:**
```bibtex
@software{sfm_core_2026,
  author = {Dabbs, Garrick},
  title = {SFM Core: Social Fabric Matrix Graph Service},
  year = {2026},
  url = {https://github.com/SFM-Graph-Service/sfm-core},
  version = {0.1.0},
  doi = {10.5281/zenodo.XXXXXXX}  # Will be assigned upon release
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

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for detailed version history.

### Added in v0.1.0
- Complete SFM graph modeling framework
- NetworkX and Neo4j backend implementations
- REST API with FastAPI
- 40+ specialized node types
- CSV/JSON import with OECD/World Bank adapters
- Ceremonial/instrumental analysis
- Circular causation detection
- Comprehensive test suite (678 tests, 92% coverage)
- Complete documentation suite
- Security: Path traversal validation for file imports

### Security
- Path validation for file imports (opt-in, backward compatible)
- Documented security considerations in README
- Regular dependency updates via Dependabot

## License

GNU General Public License v3.0 (GPL-3.0)

See [LICENSE](LICENSE) for details.

## Support & Contributing

- **Issues**: [GitHub Issues](https://github.com/SFM-Graph-Service/sfm-core/issues)
- **Discussions**: [GitHub Discussions](https://github.com/SFM-Graph-Service/sfm-core/discussions)
- **Contributing**: See [CONTRIBUTORS.md](CONTRIBUTORS.md)
- **Email**: garrickdabbs@gmail.com

## Acknowledgments

**F. Gregory Hayden** - Creator of the Social Fabric Matrix methodology. This implementation is based on interpretation of his published work.

**Claude AI (Anthropic)** - Extensive AI assistance throughout development. See `CONTRIBUTORS.md` for full disclosure.

---

**Status**: Experimental Research Software (Alpha)

This is research software based on interpretation of academic methodology. Known gaps from canonical SFM are documented. Academic and research use encouraged; production deployment requires validation.
