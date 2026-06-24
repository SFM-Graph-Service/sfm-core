# Synthetic Climate Policy Network - Dataset Summary

**Generated:** 2026-06-24  
**Scenario:** National Climate Policy Network 2025-2035  
**Framework:** Social Fabric Matrix (SFM) Institutional Analysis

## Quick Stats

```
Total Nodes:         1,056
Total Relationships: 6,363
Average Degree:      6.03
Network Density:     Low (realistic for institutional networks)
Data Size:           3.5 MB (JSON), 1.2 MB (GEXF)
```

## Node Composition

### By Category (Top 10)

| Category | Count | Description |
|----------|-------|-------------|
| Technology | 117 | Energy and climate technologies |
| Community Organizations | 102 | Grassroots advocacy groups |
| Industry Associations | 96 | Trade associations |
| Non-Profits | 79 | Environmental NGOs |
| Research Institutions | 71 | Universities and labs |
| Policy Instruments | 67 | Regulations and programs |
| Climate Tech | 54 | Clean technology companies |
| Labor Unions | 50 | Worker organizations |
| Venture Capital | 49 | Climate tech investors |
| Media | 43 | Climate journalism |

### Geographic Coverage

- **Federal agencies:** 15
- **State agencies:** 31 (covering 20 US states)
- **Municipal agencies:** 25 (major US cities)
- **International organizations:** 8
- **National scope:** 779 organizations
- **Local scope:** 147 organizations

## Relationship Types

### Top 10 Relationship Types

| Type | Count | Delivery |
|------|-------|----------|
| Advocacy | 1,132 | Information |
| Advisory | 975 | Information |
| Collaboration | 686 | Information |
| Lobbying | 576 | Information |
| Investment | 554 | Money |
| Coverage | 344 | Information |
| Normative Influence | 320 | Values |
| Policy Influence | 272 | Information |
| Implementation | 248 | Rules |
| Technical Input | 210 | Information |

### Delivery Types

- **Information flows:** 4,349 (68%)
- **Money transfers:** 596 (9%)
- **Rules/regulations:** 548 (9%)
- **Value influences:** 320 (5%)
- **Technology transfers:** 270 (4%)
- **Infrastructure:** 150 (2%)
- **Collaboration:** 130 (2%)

## Institutional Characteristics

### Ceremonial vs Instrumental Scores

The dataset models realistic institutional behavior with ceremonial (symbolic/legitimizing) and instrumental (operational/practical) dimensions:

```
Ceremonial Scores:
  Mean:   0.494
  Range:  0.100 - 0.899

Instrumental Scores:
  Mean:   0.507
  Range:  0.100 - 0.900

Correlation: -0.854 (strong negative, as expected)
```

This negative correlation reflects institutional theory: organizations balancing symbolic legitimacy with practical effectiveness.

### Most Connected Institutions

**Most Influential (highest out-degree):**
1. Department of Energy (37 connections)
2. Federal Energy Regulatory Commission (30)
3. Environmental Protection Agency (25)
4. Securities and Exchange Commission (20)
5. Department of Treasury (20)

**Most Referenced (highest in-degree):**
1. Department of Interior (62 connections)
2. Agency for International Development (61)
3. Department of Energy (56)
4. Securities and Exchange Commission (55)
5. Environmental Protection Agency (54)

## Network Structure

### Degree Distribution

- Average out-degree: 6.03
- Average in-degree: 6.03
- Max out-degree: 37
- Max in-degree: 62

The distribution follows a realistic pattern with:
- Many lightly-connected organizations (communities, local groups)
- Moderate connectivity for most institutions
- High connectivity for central coordinating bodies (federal agencies)

### Community Structure

The network exhibits natural clustering:
- **Government cluster:** Federal-state-local hierarchies
- **Private sector cluster:** Corporations, utilities, finance
- **Civil society cluster:** NGOs, community organizations, unions
- **Research cluster:** Universities and labs
- **Technology cluster:** Clean tech companies and systems

Cross-cluster connections represent:
- Public-private partnerships
- Research commercialization
- Stakeholder engagement
- Multi-sector coalitions

## Temporal Metadata

All nodes and relationships include temporal validity:

- **Valid from:** 2025-2027 (establishment period)
- **Valid to:** 2030-2035 (expiration/sunset)
- **Established dates:** Distributed 2025-2028

This enables temporal network analysis and scenario modeling.

## Data Quality

### Validation Results

✓ All node IDs unique  
✓ All node names unique  
✓ All required fields present  
✓ All scores within valid ranges (0-1)  
✓ All relationship references valid  
✓ No orphaned nodes  
✓ No self-loops  
✓ Statistics consistent  

### Realism Features

1. **Plausible institution names** based on real organizations
2. **Realistic relationship patterns** (e.g., federal agencies regulate state agencies)
3. **Geographic coherence** (state agencies linked to specific states)
4. **Temporal consistency** (dates within 2025-2035 scenario)
5. **Strength variation** (relationships weighted 0.3-0.9)
6. **Confidence intervals** (0.7-0.95) modeling data uncertainty

## Use Cases

### 1. Graph Visualization Development
- Testing force-directed layouts with 1000+ nodes
- Hierarchical clustering algorithms
- Interactive filtering and search
- Performance benchmarking

### 2. Institutional Analysis
- Ceremonial vs instrumental patterns
- Multi-level governance structures
- Cross-sector collaboration
- Policy diffusion pathways

### 3. Network Analysis Methods
- Centrality algorithms (degree, betweenness, closeness)
- Community detection (Louvain, modularity)
- Path analysis (shortest paths, influence chains)
- Structural holes and brokerage

### 4. Teaching and Training
- Institutional economics education
- Network analysis pedagogy
- Policy analysis methods
- Data visualization principles

## Files Included

| File | Size | Purpose |
|------|------|---------|
| `climate_network.json` | 3.5 MB | Main dataset (SFM format) |
| `climate_network.gexf` | 1.2 MB | GEXF format for Gephi |
| `generate_large_network.py` | 95 KB | Generator script |
| `validate_network.py` | 6.3 KB | Validation script |
| `example_analysis.py` | 8.1 KB | Analysis examples |
| `README.md` | 14 KB | Documentation |
| `DATASET_SUMMARY.md` | This file | Dataset overview |

## Reproducibility

The dataset is generated with a fixed random seed (42) for reproducibility:

```python
python generate_large_network.py  # Always produces same output
```

To generate variations:
```python
# Edit seed in ClimateNetworkGenerator(seed=42)
generator = ClimateNetworkGenerator(seed=123)  # Different network
```

## Limitations

**This is synthetic data for demonstration purposes:**

- ✗ Relationships are plausible but not factual
- ✗ Do not use for actual policy analysis
- ✗ Temporal data is scenario-based, not historical
- ✗ Strength scores are randomized, not empirical

**However, the structure is realistic:**

- ✓ Institutional types based on real organizations
- ✓ Relationship patterns follow known governance structures
- ✓ Network properties match empirical institutional networks
- ✓ Suitable for methods development and visualization

## Citation

If using this dataset in research or presentations:

```
Synthetic National Climate Policy Network (2025-2035)
Generated for Social Fabric Matrix (SFM) Framework
Dataset: 1,056 nodes, 6,363 relationships
Source: sfm-core/examples/synthetic_data
Date: 2026-06-24
```

## Next Steps

1. **Load the data:** See `README.md` for loading instructions
2. **Validate:** Run `python validate_network.py`
3. **Explore:** Run `python example_analysis.py`
4. **Visualize:** Import `climate_network.gexf` into Gephi
5. **Analyze:** Build custom queries using examples in `README.md`

## Contact

For questions about:
- **Dataset structure:** See `README.md`
- **SFM framework:** See main sfm-core documentation
- **Customization:** Edit `generate_large_network.py`
- **Issues:** Open issue in sfm-core repository

---

**Generated with:** sfm-core synthetic data generator v1.0  
**License:** Use freely for research, education, and development  
**Status:** ✓ Validated | ✓ Complete | ✓ Ready for use
