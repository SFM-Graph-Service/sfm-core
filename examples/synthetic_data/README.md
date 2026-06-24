# Synthetic Climate Policy Network Dataset

This directory contains a synthetic institutional analysis dataset for demonstrating the Social Fabric Matrix (SFM) framework with complex graph visualization.

## Overview

The dataset models a realistic **National Climate Policy Network (2025-2035)**, representing the institutional ecosystem around climate policy in the United States. It includes federal agencies, state governments, municipalities, private corporations, non-profits, research institutions, and the relationships between them.

## Dataset Composition

### Nodes (1000-1500 total)

The network includes the following institutional categories:

| Category | Count | Description |
|----------|-------|-------------|
| **Federal Agencies** | ~15 | EPA, DOE, DOI, NOAA, FERC, Treasury, SEC, etc. |
| **State Agencies** | ~30-40 | State environmental and energy departments |
| **Municipal Agencies** | ~25 | City sustainability offices in major metros |
| **Private Utilities** | ~15 | Electric utility companies (PG&E, Duke Energy, etc.) |
| **Climate Tech** | ~15 | Clean energy technology companies (Tesla, First Solar, etc.) |
| **Energy Transition** | ~6 | Oil & gas companies transitioning (ExxonMobil Clean Energy, etc.) |
| **Financial Services** | ~8 | Climate investment divisions (BlackRock, Goldman Sachs, etc.) |
| **Technology** | ~6 | Big tech climate programs (Google, Microsoft, Apple, etc.) |
| **Non-Profits** | ~20 | Environmental NGOs (NRDC, Sierra Club, EDF, etc.) |
| **Research Institutions** | ~16 | Universities and national labs |
| **Policy Instruments** | ~25 | Regulations, programs, standards (Clean Air Act, RPS, etc.) |
| **Value Systems** | ~15 | Normative frameworks (Environmental Justice, Net Zero, etc.) |
| **Technology Systems** | ~20 | Infrastructure and platforms (Solar PV, Battery Storage, etc.) |
| **International Orgs** | ~8 | UNFCCC, IPCC, IEA, World Bank, etc. |

### Relationships (3000-5000 total)

Multiple relationship types modeling real institutional interactions:

| Type | Delivery | Description |
|------|----------|-------------|
| **Regulatory** | Rules | Federal/state oversight and regulation |
| **Funding** | Money | Research grants, program funding |
| **Investment** | Money | Private capital deployment |
| **Implementation** | Rules | Policy adoption and enforcement |
| **Advocacy** | Information | Policy advocacy by NGOs |
| **Collaboration** | Information | Inter-organizational partnerships |
| **Advisory** | Information | Scientific and technical advice |
| **Development** | Technology | Technology R&D |
| **Deployment** | Infrastructure | Technology implementation |
| **Normative Influence** | Values | Value systems shaping policy |

### Node Metadata

Each node includes:
- **Ceremonial Score** (0.1-0.9): Degree of symbolic/legitimizing function
- **Instrumental Score** (0.1-0.9): Degree of practical/operational function  
  *(Negatively correlated with ceremonial for realism)*
- **Geographic Scope**: local, state, regional, national, international
- **Temporal Validity**: valid_from and valid_to dates (2025-2035)
- **Category-Specific Fields**: budget level, authority level, sector, etc.

### Relationship Metadata

Each relationship includes:
- **Strength** (0.3-0.9): Intensity of relationship
- **Confidence** (0.7-0.95): Data quality indicator
- **Temporal Period**: established date, last_updated
- **Delivery Type**: money, rules, information, technology, values, collaboration

## Generating the Dataset

### Prerequisites

Python 3.8+ with standard library (no external dependencies required for JSON export).

Optional for GEXF export:
```bash
# Already included in Python stdlib
# xml.etree.ElementTree
```

### Generate

```bash
cd /home/gdabbs/repos/sfm-core/examples/synthetic_data
python generate_large_network.py
```

Or make executable and run directly:
```bash
chmod +x generate_large_network.py
./generate_large_network.py
```

### Output

The script generates:
1. **climate_network.json** - Full dataset in SFM-Core JSON format
2. **climate_network.gexf** - GEXF format for Gephi validation
3. **Console output** - Detailed statistics and composition

## Loading into SFM-Core

### Option 1: Direct JSON Import

```python
import json
from pathlib import Path

# Load the dataset
with open('examples/synthetic_data/climate_network.json', 'r') as f:
    data = json.load(f)

# Access components
nodes = data['nodes']
relationships = data['relationships']
stats = data['statistics']

print(f"Loaded {stats['total_nodes']} nodes and {stats['total_relationships']} relationships")
```

### Option 2: Using SFM-Core API (if available)

```python
from sfm_core import Network

# Initialize network
network = Network.from_json('examples/synthetic_data/climate_network.json')

# Query the network
federal_agencies = network.get_nodes_by_category('federal_agency')
funding_flows = network.get_relationships_by_type('funding')

# Analyze
stats = network.calculate_statistics()
influential_nodes = network.get_most_influential(limit=10)
```

## Example Analysis Queries

### 1. Identify Key Funding Sources

Find institutions providing the most funding:

```python
from collections import Counter

funding_sources = Counter()
for rel in data['relationships']:
    if rel['delivery_type'] == 'money':
        # Find source node name
        source_id = rel['source']
        source_node = next(n for n in data['nodes'] if n['id'] == source_id)
        funding_sources[source_node['name']] += 1

print("Top funding sources:")
for source, count in funding_sources.most_common(10):
    print(f"  {source}: {count} funding relationships")
```

### 2. Analyze Regulatory Chains

Trace regulatory relationships from federal to local:

```python
# Find EPA
epa = next(n for n in data['nodes'] if n['name'] == 'Environmental Protection Agency')

# Find all regulatory relationships from EPA
epa_regulations = [
    r for r in data['relationships'] 
    if r['source'] == epa['id'] and r['type'] == 'regulatory'
]

print(f"EPA has {len(epa_regulations)} direct regulatory relationships")
```

### 3. Geographic Distribution

Analyze state-level activity:

```python
state_nodes = [n for n in data['nodes'] if n['category'] == 'state_agency']
states = set(n['metadata'].get('state') for n in state_nodes if 'state' in n['metadata'])

print(f"Network covers {len(states)} states:")
for state in sorted(states):
    state_orgs = [n for n in state_nodes if n['metadata'].get('state') == state]
    print(f"  {state}: {len(state_orgs)} agencies")
```

### 4. Ceremonial vs Instrumental Analysis

Compare ceremonial and instrumental scores:

```python
import statistics

ceremonial_scores = [n['metadata']['ceremonial_score'] for n in data['nodes']]
instrumental_scores = [n['metadata']['instrumental_score'] for n in data['nodes']]

print("Ceremonial scores:")
print(f"  Mean: {statistics.mean(ceremonial_scores):.3f}")
print(f"  Median: {statistics.median(ceremonial_scores):.3f}")

print("Instrumental scores:")
print(f"  Mean: {statistics.mean(instrumental_scores):.3f}")
print(f"  Median: {statistics.median(instrumental_scores):.3f}")

# Correlation
import math
n = len(ceremonial_scores)
mean_c = statistics.mean(ceremonial_scores)
mean_i = statistics.mean(instrumental_scores)
covariance = sum((c - mean_c) * (i - mean_i) for c, i in zip(ceremonial_scores, instrumental_scores)) / n
std_c = statistics.stdev(ceremonial_scores)
std_i = statistics.stdev(instrumental_scores)
correlation = covariance / (std_c * std_i)

print(f"Correlation: {correlation:.3f} (expected negative)")
```

### 5. Network Centrality (Simple Version)

Identify most connected nodes:

```python
from collections import Counter

# Count in-degree and out-degree
in_degree = Counter()
out_degree = Counter()

for rel in data['relationships']:
    out_degree[rel['source']] += 1
    in_degree[rel['target']] += 1

# Find node names
def get_node_name(node_id):
    return next(n['name'] for n in data['nodes'] if n['id'] == node_id)

print("Most influential (out-degree):")
for node_id, count in out_degree.most_common(10):
    print(f"  {get_node_name(node_id)}: {count}")

print("\nMost influenced (in-degree):")
for node_id, count in in_degree.most_common(10):
    print(f"  {get_node_name(node_id)}: {count}")
```

### 6. Policy Implementation Chains

Trace how policies flow from federal to local:

```python
# Find a specific policy
clean_air_act = next(
    n for n in data['nodes'] 
    if 'Clean Air Act' in n['name']
)

# Find all implementation relationships
implementations = [
    r for r in data['relationships']
    if r['target'] == clean_air_act['id'] and r['type'] == 'implementation'
]

print(f"Clean Air Act implemented by {len(implementations)} institutions:")
for rel in implementations[:10]:  # Show first 10
    implementer = next(n for n in data['nodes'] if n['id'] == rel['source'])
    print(f"  - {implementer['name']} ({implementer['category']})")
```

### 7. Technology Deployment Patterns

Analyze which technologies are most deployed:

```python
tech_deployment = Counter()

for rel in data['relationships']:
    if rel['type'] == 'deployment':
        target = next(n for n in data['nodes'] if n['id'] == rel['target'])
        if target['type'] == 'technology_system':
            tech_deployment[target['name']] += 1

print("Most deployed technologies:")
for tech, count in tech_deployment.most_common(10):
    print(f"  {tech}: {count} deployments")
```

## Validation with Gephi

The GEXF export can be validated in [Gephi](https://gephi.org/):

1. Open Gephi
2. File → Open → `climate_network.gexf`
3. Import report shows nodes and edges
4. Run statistics:
   - Average Degree
   - Network Diameter
   - Modularity (community detection)
   - PageRank
5. Apply layouts:
   - Force Atlas 2 for clustered view
   - Fruchterman Reingold for balanced view
6. Color nodes by category attribute
7. Size nodes by degree centrality

## Customization

### Change Network Size

Edit the generator to adjust scale:

```python
# In generate_large_network.py, modify these sections:

# Reduce to 500 nodes
states = states[:10]  # Instead of all 20
climate_tech = climate_tech[:8]  # Instead of all 15

# Increase to 2000 nodes
# Add more categories or duplicate with variations
```

### Different Scenario

Modify the scenario theme:

```python
# Change from climate to healthcare:
class HealthcareNetworkGenerator(ClimateNetworkGenerator):
    def generate_federal_agencies(self):
        agencies = [
            ("Centers for Disease Control", "Disease control"),
            ("Food and Drug Administration", "Drug regulation"),
            ("Centers for Medicare and Medicaid", "Healthcare finance"),
            # ... etc
        ]
```

### Adjust Relationship Density

Control the number of relationships:

```python
# In generate_relationships(), adjust sample sizes:
for state in random.sample(states, min(30, len(states))):  # More connections
# vs
for state in random.sample(states, min(5, len(states))):   # Fewer connections
```

## Dataset Statistics (Expected)

Generated with seed=42:

```
Total Nodes: 1000-1500
Total Relationships: 3000-5000
Average Degree: 4-6
Network Density: Low (realistic for institutional networks)

Node Categories: 14
Relationship Types: 10+
Delivery Types: 6

Geographic Coverage:
  - 50 states (via state agencies)
  - 25+ major cities
  - National and international levels
```

## Use Cases

This dataset is suitable for:

1. **Graph Visualization Development**
   - Testing force-directed layouts
   - Hierarchical clustering algorithms
   - Interactive filtering and search

2. **Institutional Analysis Demos**
   - Ceremonial vs instrumental patterns
   - Multi-level governance structures
   - Cross-sector collaboration

3. **Network Analysis Benchmarking**
   - Centrality algorithms
   - Community detection
   - Path analysis

4. **SFM-Core Feature Testing**
   - Large-scale data import/export
   - Query performance
   - Visualization rendering

5. **Educational Purposes**
   - Teaching institutional economics
   - Network analysis training
   - Policy analysis methods

## Data Quality Notes

This is **synthetic data** generated for demonstration purposes. Characteristics:

- **Realistic structure**: Based on actual US climate policy institutions
- **Fictional relationships**: Connections are plausible but not factual
- **Temporal consistency**: Dates within 2025-2035 scenario
- **Statistical properties**: Designed to mimic real institutional networks

**Do not use for actual policy analysis or decision-making.**

## Extending the Dataset

### Add Temporal Dynamics

```python
# Generate multiple snapshots
for year in range(2025, 2036):
    generator = ClimateNetworkGenerator(seed=year)
    generator.generate_network()
    generator.export_json(f'climate_network_{year}.json')
```

### Add Weighted Influence

```python
# Calculate compound influence scores
def calculate_influence(node_id, depth=2):
    # Recursive influence through network
    # Based on relationship strength and target centrality
    pass
```

### Export to Other Formats

```python
# Add NetworkX export
import networkx as nx

G = nx.DiGraph()
for node in data['nodes']:
    G.add_node(node['id'], **node)
for rel in data['relationships']:
    G.add_edge(rel['source'], rel['target'], **rel)

nx.write_gml(G, 'climate_network.gml')
```

## License

This synthetic dataset and generator script are provided as-is for use with SFM-Core.

## Contact

For questions about this dataset or SFM-Core:
- See main SFM-Core repository documentation
- Open an issue for dataset-specific questions
