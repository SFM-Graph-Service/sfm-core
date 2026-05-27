# Changelog

All notable changes to SFM Core will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

No unreleased changes at this time.

## [0.1.0] - 2026-05-27

**First public release of the Social Fabric Matrix (SFM) graph analysis framework.**

This is an experimental research software release implementing F. Gregory Hayden's Social Fabric Matrix methodology. The implementation is based on interpretation of Hayden's published work with documented structural differences (see SFM_FIDELITY_ANALYSIS.md for complete analysis).

### Added

**Core Framework**
- Complete SFM graph modeling system with 40+ specialized node types across 12 analytical domains
- Dual-backend architecture: NetworkX (default, in-memory) and Neo4j (scalable, persistent)
- REST API with FastAPI (30+ endpoints, interactive OpenAPI documentation)
- Comprehensive query engine with graph traversal capabilities

**Analysis Methods**
- Ceremonial vs Instrumental classification and analysis
- Circular causation detection (feedback loop identification)
- Institutional holarchy mapping
- Network centrality and influence metrics
- Temporal evolution queries
- Uncertainty propagation framework
- Conflict detection algorithms

**Data Integration**
- CSV/Excel import adapters with automatic delimiter detection
- JSON import/export with full graph serialization
- OECD API integration for economic indicators
- World Bank API integration for development data
- GraphML export for network visualization tools
- Bulk import operations (210x performance improvement over individual operations)

**Validation & Examples**
- 678 test cases with 92% code coverage
- 4 Hayden case study implementations:
  - Nebraska K-12 education finance (Hoffman & Hayden 2007)
  - Low-level radioactive waste (Hayden & Bolduc 2000)
  - Corporate director networks (Hayden, Wood & Kaya 2002)
  - Clean Air Act analysis
- Performance benchmarks and scaling analysis

**Documentation**
- Complete README with quickstart guide
- Analysis Methods Guide (31.3KB) - comprehensive methodology documentation
- Neo4j Integration Guide (13.5KB) - backend setup and migration
- Scaling Guide (13.5KB) - performance optimization strategies
- Setup Guide with validation scripts
- SFM Fidelity Analysis documenting implementation gaps and future roadmap
- CONTRIBUTORS.md with full AI assistance disclosure
- CITATION.cff for academic citation support
- 5-minute quickstart tutorial (docs/QUICKSTART.md)

### Security

- **CWE-22 Path Traversal Protection**: Two-tier validation in CSV/Excel importers
  - Always blocks obvious path traversal attempts (../, ../../, etc.)
  - Optional strict directory restriction mode via `allowed_base_dir` parameter
  - All file operations protected by default while maintaining backward compatibility
- CodeQL security scanning enabled in CI/CD
- Dependency vulnerability monitoring via GitHub Dependabot

### Fixed

- Performance test reliability on CI runners (added 20% timing tolerance for hardware variance)
- Path validation backward compatibility with tempfile usage
- All CodeQL security alerts resolved before release

### Known Limitations

**Implementation Fidelity (7.5/10 overall)**
- Square matrix structure not fully implemented (institution×criteria vs component×component)
- Delivery model simplified compared to Hayden's canonical approach
- Temporal modeling limited (no graphical clocks implementation)
- Cell descriptions not enforced as required deliverables
- See SFM_FIDELITY_ANALYSIS.md for complete gap analysis and roadmap

**Performance Considerations**
- NetworkX backend recommended for <10,000 nodes
- Neo4j backend required for larger graphs (10K+ nodes)
- Benchmark results from 16-core development machine (adjust expectations for CI/slower hardware)

**AI Assistance Disclosure**
- Extensive AI assistance (Claude Sonnet 4.5) used throughout development
- All code, analysis, and documentation independently verified by human author
- Users should validate outputs for their specific use cases

### Notes

- **Development Status**: Alpha (experimental research software)
- **License**: GNU General Public License v3.0 (GPL-3.0)
- **Python Support**: 3.9, 3.10, 3.11, 3.12
- **Citation**: Both this software and Hayden's foundational work should be cited (see CITATION.cff)
- **Academic Use**: Encouraged for policy analysis, institutional economics research, and systems modeling
- **Transparency**: Full disclosure of AI assistance and methodology interpretation gaps

[Unreleased]: https://github.com/SFM-Graph-Service/sfm-core/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/SFM-Graph-Service/sfm-core/releases/tag/v0.1.0
