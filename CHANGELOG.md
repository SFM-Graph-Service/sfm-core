# Changelog

All notable changes to SFM Core will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial implementation of Social Fabric Matrix methodology
- 40+ specialized node types across 12 analytical domains
- Dual-backend architecture (NetworkX and Neo4j)
- REST API with 30+ FastAPI endpoints
- Advanced analysis methods (ceremonial vs instrumental, circular causation, etc.)
- Temporal modeling and uncertainty propagation
- Bulk operations with 210x performance improvement
- CSV/Excel import adapters with security features
- XLSX matrix export functionality
- System Dynamics (XMILE) export capability
- Path validation for secure file imports
- Comprehensive test suite (678 tests)

### Security
- Path traversal protection in CSV/Excel importers (opt-in via `allowed_base_dir`)
- CodeQL security scanning enabled

### Documentation
- Analysis Methods Guide (31.3KB)
- Neo4j Integration Guide (13.5KB)
- Scaling Guide (13.5KB)
- Setup Guide with validation scripts
- SFM Fidelity Analysis documenting implementation gaps
- 4 Hayden case study examples

## [0.1.0] - TBD

### Notes
- Initial experimental release
- Research software under active development
- Implementation based on interpretation of Hayden's published work
- Known structural differences from canonical SFM methodology (see SFM_FIDELITY_ANALYSIS.md)
- Extensive AI assistance used in development (Claude AI)

[Unreleased]: https://github.com/SFM-Graph-Service/sfm-core/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/SFM-Graph-Service/sfm-core/releases/tag/v0.1.0
