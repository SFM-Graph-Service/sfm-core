# SFM Visualization Project

## Overview

This document outlines the separation of visualization features from sfm-core and describes the sfm-visualization project.

## Rationale

As of v0.9.0, sfm-core is positioned as a **pure backend library** focused on:
- Institutional analysis and graph operations
- Delivery-centric matrix modeling
- Data processing and analysis methods
- Data export in standard formats

Visualization and frontend features are being moved to a separate project for:
- **Cleaner dependency management**: Backend dependencies (pandas, networkx, neo4j) separate from frontend (matplotlib, plotly, dash)
- **Independent versioning**: Visualization updates don't require backend releases
- **Better separation of concerns**: Backend focused on data/analysis, frontend on presentation
- **Easier maintenance**: Smaller, focused codebases

## Current State (v0.9.0)

**Removed from sfm-core:**
- `visualization` optional dependency group (matplotlib, pyvis)
- `docs/VISUALIZATION_GUIDE.md`
- Matplotlib plotting examples in documentation

**Retained in sfm-core:**
- All core analysis methods
- Data export to GEXF, GraphML (for external tools)
- Excel export with matrix views
- XMILE export for System Dynamics
- JSON export for full graph state

## Data Export Formats

sfm-core provides comprehensive data export for use with external visualization tools:

### NetworkX Graph Formats
- **GEXF** (Graph Exchange XML Format)
  - Use with: Gephi, web-based graph visualization
  - Export: `service.export_to_gexf("graph.gexf")`
  
- **GraphML** (Graph Markup Language)
  - Use with: yEd, Cytoscape, Gephi
  - Export: `service.export_to_graphml("graph.graphml")`

### Spreadsheet Format
- **Excel** (.xlsx)
  - Three sheets: Matrix view, Cell descriptions, Delivery details
  - Use with: Excel, Numbers, LibreOffice
  - Export: `export_delivery_matrix_to_xlsx(matrix, "output.xlsx", service)`

### System Dynamics Format
- **XMILE** (OASIS Standard)
  - Use with: Stella, Vensim, isee Exchange
  - Export: `export_to_xmile(matrix, "model.xmile", service)`

### JSON Format
- **Full graph state** with metadata
  - Use with: Custom visualization tools, web apps
  - Export: `service.save("graph.json", format_type=StorageFormat.JSON)`

## sfm-visualization Project

**Repository**: https://github.com/SFM-Graph-Service/sfm-visualization  
**Status**: ✅ Live and ready for deployment  
**Technology**: Next.js 14 + TypeScript + React Flow + Plotly.js

### Current Features (v1.0.0)

**Interactive Visualization Components:**
- ✅ **NetworkVisualization**: React Flow network graphs with 4 layout algorithms (force-directed, hierarchical, circular, grid)
- ✅ **MatrixHeatmap**: N×N delivery matrix heat maps with hover tooltips
- ✅ **TemporalTimeline**: Animated institutional evolution with Plotly.js charts and play/pause controls
- ✅ **AnalysisPanel**: Metrics dashboard showing ceremonial/instrumental ratios, circular causation, conflicts
- ✅ **CaseStudySelector**: Load Hayden case studies or upload custom JSON data

**Visualization Technologies:**
- **React Flow 11+**: Interactive network diagrams with zoom/pan
- **Plotly.js 2.30+**: Time series charts and analytics
- **Tailwind CSS**: Modern, responsive styling
- **TypeScript**: Full type safety

**Deployment Features:**
- Docker containerization with multi-stage builds
- docker-compose.yml orchestrates sfm-core + frontend
- Configurable backend URL via environment variables
- Works locally (`npm run dev`) or any cloud container platform

**Sample Data Included:**
- 3 Hayden case studies (Clean Air Act, Nebraska K-12, Healthcare Reform)
- Synthetic 1000+ node climate policy network
- Complete TypeScript interfaces for SFM data structures

## Migration Guide for Users

### Before v0.9.0
```bash
pip install sfm-core[visualization]
```

```python
import matplotlib.pyplot as plt
from api.sfm_service import SFMService

service = SFMService()
# ... build graph ...

# Visualization was manual
plt.figure()
# ... matplotlib code ...
plt.show()
```

### After v0.9.0
```bash
# Backend only
pip install sfm-core

# Or with external visualization tools
pip install sfm-core gephi-toolkit  # for GEXF
```

```python
from api.sfm_service import SFMService
from graph.exporters import export_to_gexf

service = SFMService()
# ... build graph ...

# Export for visualization
export_to_gexf(service, "output.gexf")
# Open output.gexf in Gephi for visualization
```

### With sfm-visualization (Current)
```bash
# Install backend
pip install sfm-core

# Clone and run frontend
git clone https://github.com/SFM-Graph-Service/sfm-visualization.git
cd sfm-visualization/frontend
npm install
npm run dev
# Access at http://localhost:3000
```

Or use Docker Compose:
```bash
cd sfm-visualization
docker-compose up
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
```

Load data via the web interface:
1. Start sfm-core backend
2. Navigate to http://localhost:3000/example
3. Select Hayden case study or upload JSON
4. Interact with network graphs, matrices, and timelines

## External Visualization Tools

You can also use these external tools with GEXF/GraphML export:

### Gephi (Recommended)
- **Download**: https://gephi.org/
- **Format**: GEXF or GraphML
- **Features**: Force-directed layouts, community detection, node sizing, edge filtering
- **Best for**: Exploratory network analysis, publication figures

### yEd
- **Download**: https://www.yworks.com/products/yed
- **Format**: GraphML
- **Features**: Automatic layouts, hierarchical diagrams, interactive editing
- **Best for**: Institutional holarchy, tree structures

### Cytoscape
- **Download**: https://cytoscape.org/
- **Format**: GraphML
- **Features**: Biological network focus, extensive plugin ecosystem
- **Best for**: Complex network analysis, custom layouts

### Stella/Vensim (System Dynamics)
- **Format**: XMILE
- **Features**: Dynamic simulation, stock-flow diagrams
- **Best for**: Temporal modeling, feedback loops

## Version History

- ✅ **v0.9.0 (June 2026)**: Visualization removed from sfm-core
- ✅ **v1.0.0 (June 2026)**: Initial sfm-visualization release
  - Next.js 14 frontend with 5 visualization components
  - React Flow network diagrams with 4 layout algorithms
  - Plotly.js charts and temporal timelines
  - Docker containerization
  - Sample Hayden case studies
  
**Roadmap:**
- **Q3 2026**: Enhanced features
  - Export to PNG/SVG/PDF
  - User authentication
  - Data persistence/caching
  
- **Q4 2026**: Advanced analytics
  - Custom visualization layouts
  - Collaborative features (sharing, annotations)
  - Performance optimizations for 10K+ nodes

- **2027**: Enterprise features
  - 3D network visualization
  - Mobile responsive design
  - WCAG accessibility compliance

## Contributing

Interested in contributing to sfm-visualization? 
- **GitHub**: https://github.com/SFM-Graph-Service/sfm-visualization
- **Issues**: https://github.com/SFM-Graph-Service/sfm-visualization/issues
- **Issues**: Feature requests and bug reports welcome

## Questions?

For questions about:
- **Backend/analysis**: Open issue at https://github.com/SFM-Graph-Service/sfm-core/issues
- **Visualization**: Watch for sfm-visualization repository announcement
- **Export formats**: See sfm-core documentation

---

**Last Updated**: 2026-06-24 | **sfm-core Version**: 0.9.1 | **sfm-visualization**: v1.0.0
