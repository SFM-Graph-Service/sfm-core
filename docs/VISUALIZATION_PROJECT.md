# SFM Visualization Project

## Overview

This document outlines the separation of visualization features from sfm-core and the planned sfm-visualization project.

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

## Planned sfm-visualization Project

**Repository**: https://github.com/SFM-Graph-Service/sfm-visualization (coming soon)

**Planned Features:**

### Interactive Visualizations
- **Network diagrams**: Interactive node-link graphs with zoom/pan
- **Matrix heat maps**: Delivery strength visualization
- **Temporal evolution**: Animated institutional change over time
- **Hierarchical layouts**: Institutional holarchy visualization
- **Circular causation**: Feedback loop highlighting

### Visualization Technologies
- **matplotlib**: Static publication-quality figures
- **plotly**: Interactive web-based visualizations
- **dash**: Full dashboard applications
- **D3.js integration**: Advanced custom visualizations
- **NetworkX layout algorithms**: Spring, hierarchical, circular

### Dashboard Features
- Real-time analysis updates
- Multi-graph comparison views
- Ceremonial vs instrumental classification overlays
- Centrality metric visualization (node sizing by betweenness)
- Edge coloring by delivery type
- Interactive filtering and exploration

### Example Applications
- Policy impact visualization dashboards
- Institutional network explorers
- Temporal evolution animations
- Comparative case study viewers

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

### Future with sfm-visualization
```bash
pip install sfm-core sfm-visualization
```

```python
from api.sfm_service import SFMService
from sfm_visualization import NetworkVisualizer

service = SFMService()
# ... build graph ...

# One-line visualization
viz = NetworkVisualizer(service)
viz.show_interactive()  # Interactive plotly dashboard
viz.save_figure("network.png")  # Publication figure
```

## External Visualization Tools

While the sfm-visualization project is in development, use these external tools:

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

## Timeline

- **v0.9.0 (June 2026)**: Visualization removed from sfm-core
- **Q3 2026**: Initial sfm-visualization project release
  - Basic matplotlib/plotly integration
  - Network diagram generator
  - Matrix heat map visualization
  
- **Q4 2026**: Dashboard features
  - Interactive dash application
  - Multi-graph comparison
  - Real-time analysis updates

- **2027**: Advanced features
  - Temporal animation
  - 3D network visualization
  - Custom layout algorithms

## Contributing

Interested in helping build sfm-visualization? Watch the repository and join discussions:
- **GitHub**: https://github.com/SFM-Graph-Service/sfm-visualization/discussions (coming soon)
- **Issues**: Feature requests and bug reports welcome

## Questions?

For questions about:
- **Backend/analysis**: Open issue at https://github.com/SFM-Graph-Service/sfm-core/issues
- **Visualization**: Watch for sfm-visualization repository announcement
- **Export formats**: See sfm-core documentation

---

**Last Updated**: 2026-06-24 | **sfm-core Version**: 0.9.0
