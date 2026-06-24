# Quick Start Guide

Get up and running with the synthetic climate network dataset in 5 minutes.

## 1. Generate the Dataset

```bash
cd /home/gdabbs/repos/sfm-core/examples/synthetic_data
python generate_large_network.py
```

Output:
```
Created 1056 nodes
Created 6363 relationships
✓ Generation complete!
```

## 2. Validate the Data

```bash
python validate_network.py
```

Expected: `✓ ALL VALIDATION CHECKS PASSED`

## 3. Run Example Analyses

```bash
python example_analysis.py
```

This demonstrates 8 different analysis patterns:
1. Major funding sources
2. Federal regulatory reach
3. Geographic distribution
4. Ceremonial vs instrumental patterns
5. Most connected institutions
6. Technology deployment
7. Policy implementation
8. Collaboration networks

## 4. Load in Python

```python
import json

# Load the dataset
with open('climate_network.json', 'r') as f:
    data = json.load(f)

# Access components
nodes = data['nodes']
relationships = data['relationships']
stats = data['statistics']

print(f"Loaded {stats['total_nodes']} nodes")
print(f"Loaded {stats['total_relationships']} relationships")
```

## 5. Simple Query Example

Find all climate tech companies:

```python
climate_tech = [
    node for node in data['nodes'] 
    if node['category'] == 'climate_tech'
]

print(f"Found {len(climate_tech)} climate tech companies:")
for company in climate_tech[:5]:
    print(f"  - {company['name']}")
```

## 6. Relationship Query Example

Find who funds climate tech:

```python
from collections import Counter

# Get all investment relationships to climate tech
climate_tech_ids = {n['id'] for n in climate_tech}

investors = Counter()
for rel in data['relationships']:
    if rel['target'] in climate_tech_ids and rel['type'] == 'investment':
        source = next(n for n in data['nodes'] if n['id'] == rel['source'])
        investors[source['name']] += 1

print("\nTop investors in climate tech:")
for investor, count in investors.most_common(10):
    print(f"  {investor}: {count} investments")
```

## 7. Visualize in Gephi

1. Open Gephi
2. File → Open → `climate_network.gexf`
3. Layout → Force Atlas 2
4. Statistics → Average Degree, Modularity
5. Appearance → Nodes → Color → Partition → category
6. Appearance → Nodes → Size → Ranking → Degree

## 8. Network Statistics

```python
# Simple centrality calculation
from collections import Counter

in_degree = Counter()
out_degree = Counter()

for rel in data['relationships']:
    out_degree[rel['source']] += 1
    in_degree[rel['target']] += 1

# Find most influential
node_lookup = {n['id']: n['name'] for n in data['nodes']}

print("Most influential (out-degree):")
for node_id, count in out_degree.most_common(5):
    print(f"  {node_lookup[node_id]}: {count}")
```

## Common Queries

### Find nodes by category
```python
federal_agencies = [n for n in data['nodes'] if n['category'] == 'federal_agency']
```

### Find relationships by type
```python
funding = [r for r in data['relationships'] if r['delivery_type'] == 'money']
```

### Filter by geographic scope
```python
national = [n for n in data['nodes'] if n['metadata']['geographic_scope'] == 'national']
```

### Find high ceremonial institutions
```python
ceremonial = [
    n for n in data['nodes'] 
    if n['metadata']['ceremonial_score'] > 0.7
]
```

## Next Steps

- Read `README.md` for detailed documentation
- See `DATASET_SUMMARY.md` for dataset overview
- Check `example_analysis.py` for more query patterns
- Modify `generate_large_network.py` to create custom networks

## Troubleshooting

**Files not found?**
```bash
# Make sure you're in the right directory
cd /home/gdabbs/repos/sfm-core/examples/synthetic_data
ls -l  # Should see .json, .gexf, .py files
```

**Import errors?**
```bash
# Only standard library required - no external dependencies
python --version  # Should be Python 3.8+
```

**Dataset too large?**
```python
# Reduce node counts in generate_large_network.py
# Look for list slicing opportunities, e.g.:
climate_tech = climate_tech[:20]  # Instead of all 50+
```

**Need different scenario?**
- Edit institution names in generator
- Adjust relationship generation logic
- Change temporal validity periods
- Modify ceremonial/instrumental distributions

## Support

- **Dataset questions:** See `README.md` FAQ section
- **SFM framework:** Check main sfm-core documentation
- **Issues:** Open GitHub issue with reproducible example
