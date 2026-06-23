# SFM Core Visualization Guide

**Version**: 0.7.0  
**Last Updated**: 2026-06-23

This guide explains how to visualize Social Fabric Matrix case studies using the built-in converter functions and NetworkX/matplotlib visualization capabilities.

---

## Table of Contents

1. [Quick Start: Visualize a Case Study](#quick-start)
2. [Visualization Methods](#visualization-methods)
3. [Customization Options](#customization-options)
4. [Export Formats](#export-formats)
5. [Advanced Examples](#advanced-examples)

---

## Quick Start

### Basic Network Visualization

```python
from examples.hayden_case_studies.director_networks import create_director_network_matrix
from graph.converters import to_multidigraph
import networkx as nx
import matplotlib.pyplot as plt

# Create matrix from case study
matrix, service = create_director_network_matrix()

# Convert to NetworkX graph
G = to_multidigraph(matrix, service)

# Draw network
plt.figure(figsize=(12, 8))
pos = nx.spring_layout(G, k=0.5, iterations=50)

# Draw nodes
nx.draw_networkx_nodes(G, pos, node_size=1000, node_color='lightblue', alpha=0.9)

# Draw edges with different colors by delivery type
edge_colors = []
for u, v, key, data in G.edges(data=True, keys=True):
    if key == 'authority':
        edge_colors.append('red')
    elif key == 'information':
        edge_colors.append('blue')
    elif key == 'money':
        edge_colors.append('green')
    else:
        edge_colors.append('gray')

nx.draw_networkx_edges(G, pos, edge_color=edge_colors, alpha=0.6, width=2, arrows=True)

# Draw labels
labels = nx.get_node_attributes(G, 'label')
nx.draw_networkx_labels(G, pos, labels, font_size=10, font_weight='bold')

plt.title("Director Networks: Corporate Power Structure", fontsize=16)
plt.axis('off')
plt.tight_layout()
plt.savefig('director_networks_visualization.png', dpi=300, bbox_inches='tight')
plt.show()
```

**Output**: High-resolution network diagram showing director interlocks and delivery flows.

---

## Visualization Methods

### Method 1: Spring Layout (Force-Directed)

Best for: General network structure, moderate node counts (< 50 nodes)

```python
from graph.converters import to_multidigraph
import networkx as nx
import matplotlib.pyplot as plt

# Convert matrix to graph
G = to_multidigraph(matrix, service)

# Spring layout positions nodes based on edge connections
pos = nx.spring_layout(G, k=0.5, iterations=50, seed=42)

plt.figure(figsize=(12, 8))
nx.draw(G, pos, with_labels=True, node_color='lightblue', 
        node_size=1000, font_size=10, font_weight='bold',
        edge_color='gray', arrows=True, arrowsize=20)
plt.title("SFM Network Visualization")
plt.axis('off')
plt.show()
```

---

### Method 2: Circular Layout

Best for: Highlighting symmetric relationships, equal node importance

```python
pos = nx.circular_layout(G)

plt.figure(figsize=(10, 10))
nx.draw(G, pos, with_labels=True, node_color='lightgreen',
        node_size=1200, font_size=10, arrows=True)
plt.title("SFM Circular Layout")
plt.axis('off')
plt.show()
```

---

### Method 3: Hierarchical Layout

Best for: Top-down institutional hierarchies, policy flows

```python
# Requires graphviz_layout
try:
    from networkx.drawing.nx_agraph import graphviz_layout
    pos = graphviz_layout(G, prog='dot')
except ImportError:
    print("Install pygraphviz for hierarchical layout: pip install pygraphviz")
    pos = nx.spring_layout(G)

plt.figure(figsize=(12, 10))
nx.draw(G, pos, with_labels=True, node_color='lightyellow',
        node_size=1000, font_size=9, arrows=True)
plt.title("SFM Hierarchical Layout")
plt.axis('off')
plt.show()
```

---

### Method 4: Node Sizing by Centrality

Highlight power brokers and institutional hubs:

```python
from graph.centrality import compute_centrality_metrics

# Compute centrality
centrality = compute_centrality_metrics(matrix, service)

# Map labels to node IDs for sizing
label_to_id = {data['label']: node_id for node_id, data in G.nodes(data=True)}
betweenness = centrality['betweenness']

# Size nodes by betweenness centrality
node_sizes = []
for node_id in G.nodes():
    label = G.nodes[node_id]['label']
    size = 500 + (betweenness.get(label, 0) * 5000)  # Base size + centrality
    node_sizes.append(size)

plt.figure(figsize=(12, 8))
pos = nx.spring_layout(G, k=0.5, iterations=50)

nx.draw_networkx_nodes(G, pos, node_size=node_sizes, 
                       node_color='lightcoral', alpha=0.8)
nx.draw_networkx_edges(G, pos, edge_color='gray', alpha=0.5, arrows=True)
nx.draw_networkx_labels(G, pos, 
                        labels={n: G.nodes[n]['label'] for n in G.nodes()},
                        font_size=8, font_weight='bold')

plt.title("SFM Network (Node Size = Betweenness Centrality)", fontsize=14)
plt.axis('off')
plt.tight_layout()
plt.show()
```

---

### Method 5: Edge Coloring by Delivery Type

Distinguish different types of institutional deliveries:

```python
# Define color mapping for delivery types
delivery_colors = {
    'money': '#2ecc71',       # Green
    'authority': '#e74c3c',   # Red
    'information': '#3498db', # Blue
    'rule': '#f39c12',        # Orange
    'energy': '#9b59b6',      # Purple
    'pollution': '#95a5a6',   # Gray
}

plt.figure(figsize=(14, 10))
pos = nx.spring_layout(G, k=0.6, iterations=50)

# Draw nodes
nx.draw_networkx_nodes(G, pos, node_size=1200, node_color='#ecf0f1', alpha=0.9)

# Draw edges by type with legend
for delivery_type, color in delivery_colors.items():
    edges = [(u, v) for u, v, key in G.edges(keys=True) if key == delivery_type]
    if edges:
        nx.draw_networkx_edges(G, pos, edgelist=edges, edge_color=color,
                              width=2.5, alpha=0.7, arrows=True, arrowsize=15,
                              label=delivery_type.capitalize())

# Labels
labels = {n: G.nodes[n]['label'] for n in G.nodes()}
nx.draw_networkx_labels(G, pos, labels, font_size=9, font_weight='bold')

plt.title("SFM Delivery Types", fontsize=16)
plt.legend(loc='upper left', fontsize=10)
plt.axis('off')
plt.tight_layout()
plt.show()
```

---

## Customization Options

### Node Styling

```python
# Custom node colors based on component type
node_colors = []
for node_id in G.nodes():
    label = G.nodes[node_id]['label']
    if 'Director' in label:
        node_colors.append('#e74c3c')  # Red for directors
    elif 'Corporation' in label or 'Company' in label:
        node_colors.append('#3498db')  # Blue for corporations
    elif 'EPA' in label or 'Agency' in label:
        node_colors.append('#2ecc71')  # Green for agencies
    else:
        node_colors.append('#95a5a6')  # Gray for others

nx.draw_networkx_nodes(G, pos, node_color=node_colors, 
                       node_size=1000, alpha=0.8)
```

### Edge Labels (Show Delivery Details)

```python
# Create edge labels showing delivery content (first 30 chars)
edge_labels = {}
for u, v, key, data in G.edges(data=True, keys=True):
    content = data.get('delivery_content', '')[:30]
    edge_labels[(u, v)] = f"{key}: {content}"

nx.draw_networkx_edge_labels(G, pos, edge_labels, 
                             font_size=7, font_color='red')
```

### Save High-Resolution Output

```python
# Save as PNG (raster)
plt.savefig('sfm_network.png', dpi=300, bbox_inches='tight', facecolor='white')

# Save as SVG (vector, scalable)
plt.savefig('sfm_network.svg', format='svg', bbox_inches='tight')

# Save as PDF (vector, publication-ready)
plt.savefig('sfm_network.pdf', format='pdf', bbox_inches='tight')
```

---

## Export Formats

### 1. GEXF (Gephi Compatible)

For advanced visualization in [Gephi](https://gephi.org/):

```python
import networkx as nx

# Export to GEXF format
nx.write_gexf(G, 'sfm_network.gexf')

print("Exported to GEXF. Open in Gephi for advanced visualization.")
```

**Gephi Workflow:**
1. Open Gephi
2. File → Open → Select `sfm_network.gexf`
3. Layout: Choose ForceAtlas2 or Yifan Hu
4. Appearance: Size nodes by degree/betweenness
5. Export: File → Export → PNG/SVG/PDF

---

### 2. GraphML (yEd Compatible)

For hierarchical visualization in [yEd](https://www.yworks.com/products/yed):

```python
nx.write_graphml(G, 'sfm_network.graphml')
```

**yEd Workflow:**
1. Open yEd
2. File → Open → Select `sfm_network.graphml`
3. Layout → Hierarchical or Organic
4. Export: File → Export → PNG/SVG/PDF

---

### 3. System Dynamics (XMILE)

For integration with Stella/Vensim (already implemented):

```python
from graph.exporters.system_dynamics_exporter import export_to_xmile

export_to_xmile(matrix, 'sfm_system_dynamics.xmile', service)

print("Exported to XMILE. Open in Stella, Vensim, or isee Exchange.")
```

---

### 4. Excel Matrix View

For spreadsheet-based visualization:

```python
from graph.exporters.xlsx_exporter import export_delivery_matrix_to_xlsx
from pathlib import Path

export_delivery_matrix_to_xlsx(
    matrix, 
    Path('sfm_matrix.xlsx'), 
    service,
    include_cell_descriptions=True
)

print("Exported to Excel. Open in Excel/LibreOffice for matrix view.")
```

**Excel File Structure:**
- **Sheet 1**: N×N matrix with delivery summaries
- **Sheet 2**: Cell descriptions (narrative deliverables)
- **Sheet 3**: Delivery details table (filterable)

---

## Advanced Examples

### Example 1: Clean Air Act EPA Feedback Loop

Visualize circular causation in environmental policy:

```python
from examples.hayden_case_studies.clean_air_act_1970 import build_clean_air_matrix
from graph.converters import to_multidigraph
import networkx as nx
import matplotlib.pyplot as plt

# Load case study
matrix, service = build_clean_air_matrix()
G = to_multidigraph(matrix, service)

# Find circular causation (feedback loops)
try:
    cycles = list(nx.simple_cycles(G))
    print(f"Found {len(cycles)} circular causation paths")
    
    # Highlight largest cycle
    if cycles:
        largest_cycle = max(cycles, key=len)
        cycle_edges = [(largest_cycle[i], largest_cycle[i+1]) 
                       for i in range(len(largest_cycle)-1)]
        cycle_edges.append((largest_cycle[-1], largest_cycle[0]))  # Close loop
        
        plt.figure(figsize=(14, 10))
        pos = nx.spring_layout(G, k=0.7, iterations=50)
        
        # Draw all edges in gray
        nx.draw_networkx_edges(G, pos, edge_color='lightgray', 
                              alpha=0.3, arrows=True)
        
        # Highlight feedback loop in red
        nx.draw_networkx_edges(G, pos, edgelist=cycle_edges,
                              edge_color='red', width=3, alpha=0.9,
                              arrows=True, arrowsize=20,
                              label='EPA Feedback Loop')
        
        # Draw nodes
        nx.draw_networkx_nodes(G, pos, node_size=1200, 
                              node_color='lightblue', alpha=0.9)
        
        # Labels
        labels = {n: G.nodes[n]['label'] for n in G.nodes()}
        nx.draw_networkx_labels(G, pos, labels, font_size=9, font_weight='bold')
        
        plt.title("Clean Air Act: EPA Circular Causation Path", fontsize=16)
        plt.legend(fontsize=12)
        plt.axis('off')
        plt.tight_layout()
        plt.savefig('clean_air_feedback_loop.png', dpi=300, bbox_inches='tight')
        plt.show()
        
except:
    print("No cycles detected or NetworkX version issue")
```

---

### Example 2: Nebraska K-12 School Districts as Broker Nodes

Visualize institutional centrality with node sizing:

```python
from examples.hayden_case_studies.nebraska_k12_finance import create_nebraska_k12_matrix
from graph.converters import to_multidigraph
from graph.centrality import compute_centrality_metrics, identify_power_brokers
import networkx as nx
import matplotlib.pyplot as plt

# Load case study
matrix, service = create_nebraska_k12_matrix()
G = to_multidigraph(matrix, service)

# Compute centrality
centrality = compute_centrality_metrics(matrix, service)
brokers = identify_power_brokers(centrality, betweenness_threshold=0.05)

print(f"Power brokers (betweenness > 0.05): {len(brokers)}")
for label, score in brokers:
    print(f"  {label}: {score:.3f}")

# Visualize with centrality-based sizing
plt.figure(figsize=(14, 10))
pos = nx.spring_layout(G, k=0.8, iterations=50)

# Node sizes by betweenness
betweenness = centrality['betweenness']
label_to_id = {G.nodes[n]['label']: n for n in G.nodes()}

node_sizes = []
node_colors = []
for node_id in G.nodes():
    label = G.nodes[node_id]['label']
    b_score = betweenness.get(label, 0)
    
    # Size based on centrality
    node_sizes.append(500 + b_score * 8000)
    
    # Color power brokers differently
    if b_score > 0.05:
        node_colors.append('#e74c3c')  # Red for power brokers
    else:
        node_colors.append('#3498db')  # Blue for others

nx.draw_networkx_nodes(G, pos, node_size=node_sizes, 
                       node_color=node_colors, alpha=0.8)
nx.draw_networkx_edges(G, pos, edge_color='gray', alpha=0.4, 
                      arrows=True, arrowsize=12)

labels = {n: G.nodes[n]['label'] for n in G.nodes()}
nx.draw_networkx_labels(G, pos, labels, font_size=8, font_weight='bold')

plt.title("Nebraska K-12 Finance: School Districts as Brokers\n(Node Size = Betweenness Centrality)", 
         fontsize=14)
plt.axis('off')
plt.tight_layout()
plt.savefig('nebraska_k12_centrality.png', dpi=300, bbox_inches='tight')
plt.show()
```

---

### Example 3: Interactive Visualization with Plotly

For web-based interactive exploration:

```python
import plotly.graph_objects as go
import networkx as nx
from graph.converters import to_multidigraph

# Convert matrix to graph
G = to_multidigraph(matrix, service)
pos = nx.spring_layout(G, k=0.5, iterations=50)

# Extract edge coordinates
edge_x = []
edge_y = []
for u, v in G.edges():
    x0, y0 = pos[u]
    x1, y1 = pos[v]
    edge_x.extend([x0, x1, None])
    edge_y.extend([y0, y1, None])

edge_trace = go.Scatter(
    x=edge_x, y=edge_y,
    line=dict(width=0.5, color='#888'),
    hoverinfo='none',
    mode='lines')

# Extract node coordinates
node_x = []
node_y = []
node_text = []
for node in G.nodes():
    x, y = pos[node]
    node_x.append(x)
    node_y.append(y)
    node_text.append(G.nodes[node]['label'])

node_trace = go.Scatter(
    x=node_x, y=node_y,
    mode='markers+text',
    text=node_text,
    textposition="top center",
    hoverinfo='text',
    marker=dict(
        size=20,
        color='lightblue',
        line=dict(width=2, color='darkblue')))

fig = go.Figure(data=[edge_trace, node_trace],
              layout=go.Layout(
                title='Interactive SFM Network',
                showlegend=False,
                hovermode='closest',
                margin=dict(b=0,l=0,r=0,t=40),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                )

fig.write_html('sfm_interactive.html')
fig.show()

print("Interactive visualization saved to sfm_interactive.html")
```

**Note**: Requires `pip install plotly`

---

## Complete Visualization Script

Save as `visualize_case_study.py`:

```python
#!/usr/bin/env python3
"""
SFM Case Study Visualization Script

Usage:
    python visualize_case_study.py --case director_networks --method spring --output viz.png
"""

import argparse
import matplotlib.pyplot as plt
import networkx as nx
from pathlib import Path

from graph.converters import to_multidigraph
from graph.centrality import compute_centrality_metrics


def visualize_case_study(case_name: str, layout_method: str = 'spring', 
                         output_file: str = None, show: bool = True):
    """
    Visualize any SFM case study with customizable layout.
    
    Args:
        case_name: 'director_networks', 'clean_air', 'nebraska_k12', 'llrw'
        layout_method: 'spring', 'circular', 'hierarchical', 'centrality'
        output_file: Path to save visualization (optional)
        show: Whether to display plot
    """
    # Import case study
    if case_name == 'director_networks':
        from examples.hayden_case_studies.director_networks import create_director_network_matrix
        matrix, service = create_director_network_matrix()
        title = "Corporate Director Networks"
    elif case_name == 'clean_air':
        from examples.hayden_case_studies.clean_air_act_1970 import build_clean_air_matrix
        matrix, service = build_clean_air_matrix()
        title = "Clean Air Act 1970"
    elif case_name == 'nebraska_k12':
        from examples.hayden_case_studies.nebraska_k12_finance import create_nebraska_k12_matrix
        matrix, service = create_nebraska_k12_matrix()
        title = "Nebraska K-12 Finance"
    elif case_name == 'llrw':
        from examples.hayden_case_studies.llrw_compact import create_llrw_matrix
        matrix, service = create_llrw_matrix()
        title = "Low-Level Radioactive Waste Compact"
    else:
        raise ValueError(f"Unknown case: {case_name}")
    
    # Convert to graph
    G = to_multidigraph(matrix, service)
    
    # Choose layout
    if layout_method == 'spring':
        pos = nx.spring_layout(G, k=0.6, iterations=50)
    elif layout_method == 'circular':
        pos = nx.circular_layout(G)
    elif layout_method == 'hierarchical':
        try:
            from networkx.drawing.nx_agraph import graphviz_layout
            pos = graphviz_layout(G, prog='dot')
        except ImportError:
            print("graphviz not available, using spring layout")
            pos = nx.spring_layout(G, k=0.6, iterations=50)
    elif layout_method == 'centrality':
        # Spring layout weighted by centrality
        centrality = compute_centrality_metrics(matrix, service)
        pos = nx.spring_layout(G, k=0.6, iterations=50)
    else:
        pos = nx.spring_layout(G, k=0.6, iterations=50)
    
    # Create figure
    plt.figure(figsize=(14, 10))
    
    # Node sizing
    if layout_method == 'centrality':
        centrality = compute_centrality_metrics(matrix, service)
        betweenness = centrality['betweenness']
        node_sizes = []
        for node_id in G.nodes():
            label = G.nodes[node_id]['label']
            size = 500 + (betweenness.get(label, 0) * 5000)
            node_sizes.append(size)
    else:
        node_sizes = 1200
    
    # Draw
    nx.draw_networkx_nodes(G, pos, node_size=node_sizes, 
                          node_color='lightblue', alpha=0.9)
    nx.draw_networkx_edges(G, pos, edge_color='gray', alpha=0.6,
                          arrows=True, arrowsize=15, width=2)
    
    labels = {n: G.nodes[n]['label'] for n in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels, font_size=9, font_weight='bold')
    
    plt.title(f"{title} - {layout_method.capitalize()} Layout", fontsize=16)
    plt.axis('off')
    plt.tight_layout()
    
    if output_file:
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Saved to {output_file}")
    
    if show:
        plt.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Visualize SFM case studies')
    parser.add_argument('--case', required=True, 
                       choices=['director_networks', 'clean_air', 'nebraska_k12', 'llrw'],
                       help='Case study to visualize')
    parser.add_argument('--method', default='spring',
                       choices=['spring', 'circular', 'hierarchical', 'centrality'],
                       help='Layout method')
    parser.add_argument('--output', help='Output file path (PNG/PDF/SVG)')
    parser.add_argument('--no-show', action='store_true', help='Do not display plot')
    
    args = parser.parse_args()
    
    visualize_case_study(
        case_name=args.case,
        layout_method=args.method,
        output_file=args.output,
        show=not args.no_show
    )
```

---

## Dependencies

All visualization functionality requires:

```bash
# Core dependencies (already in requirements.txt)
pip install networkx matplotlib

# Optional: Advanced layouts
pip install pygraphviz  # For hierarchical layouts

# Optional: Interactive visualizations
pip install plotly
```

---

## Summary

**Built-in Capabilities:**
- ✅ NetworkX graph conversion (`graph/converters.py`)
- ✅ Multiple layout algorithms (spring, circular, hierarchical)
- ✅ Node sizing by centrality metrics
- ✅ Edge coloring by delivery type
- ✅ Export to GEXF, GraphML, XMILE, Excel
- ✅ High-resolution PNG/PDF/SVG output

**No additional tools required** - all visualization can be done with built-in converter functions and standard NetworkX/matplotlib.

**Next Steps:**
- Run complete visualization script above
- Explore interactive Plotly visualizations
- Use Gephi/yEd for publication-quality diagrams
- Integrate XMILE files with System Dynamics software

---

**Documentation Version**: 0.7.0  
**Author**: SFM Core Development Team  
**License**: GPL-3.0
