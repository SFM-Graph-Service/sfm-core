# SFM Core Analysis Methods Guide

**Version**: 1.0  
**Last Updated**: 2026-05-27

**Note**: This is research software under active development. Claude AI was used to assist with documentation. Verify outputs independently.

---

## Overview

This guide explains the analytical capabilities of SFM Core for institutional economic analysis. All methods are accessible through the `SFMService` API and REST endpoints.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Core Analysis Methods](#core-analysis-methods)
   - [Ceremonial vs Instrumental Analysis](#ceremonial-vs-instrumental-analysis)
   - [Circular Causation Detection](#circular-causation-detection)
   - [Institutional Holarchy](#institutional-holarchy)
   - [Conflict Detection](#conflict-detection)
3. [Advanced Analysis](#advanced-analysis)
   - [Temporal Evolution](#temporal-evolution)
   - [Uncertainty Propagation](#uncertainty-propagation)
4. [Network Structure Analysis](#network-structure-analysis)
   - [Centrality Measures](#centrality-measures)
   - [Path Finding](#path-finding)
   - [Community Detection](#community-detection)
5. [Interpreting Results](#interpreting-results)
6. [Examples](#examples)

---

## Quick Start

```python
from api.sfm_service import SFMService

# Initialize service
service = SFMService()

# Load or build your scenario
# (see scenario building docs)

# Initialize query engine for analysis
service.initialize_query_engine()

# Run ceremonial vs instrumental analysis
analysis = service.get_ceremonial_analysis(threshold=0.5)

print(f"Ceremonial nodes: {len(analysis['ceremonial'])}")
print(f"Instrumental nodes: {len(analysis['instrumental'])}")
print(f"Ceremonial/Instrumental ratio: {analysis['ratio']}")
```

---

## Core Analysis Methods

### Ceremonial vs Instrumental Analysis

**Purpose**: Identify nodes that exhibit ceremonial (status quo reinforcing, traditional) vs instrumental (problem-solving, adaptive) behaviors.

**Theory**: Based on Veblen's institutional economics distinction between:
- **Ceremonial**: Institutions preserving status quo, traditional authority, prestige
- **Instrumental**: Technology-enabling, problem-solving, adaptive institutions

**Method**: Uses 4-stage classification cascade:
1. Check for explicit `CeremonialInstrumentalClassification` nodes
2. Check metadata scores (`ceremonial_score`, `instrumental_score`)
3. Infer from node type (Institution → ceremonial, Technology → instrumental)
4. Infer from relationship patterns (constrains/controls vs enables/produces)

#### Python API

```python
# Get ceremonial vs instrumental classification
analysis = service.get_ceremonial_analysis(threshold=0.5)

# Results structure
{
    "ceremonial": [Node(...), Node(...)],  # List of ceremonial nodes
    "instrumental": [Node(...), Node(...)],  # List of instrumental nodes
    "mixed": [Node(...)],  # Nodes scoring above threshold in both
    "ratio": 1.2  # Ceremonial/instrumental ratio (>1 = ceremonial dominance)
}
```

**Parameters**:
- `threshold` (float, default 0.5): Minimum score (0-1) to include in classification. Lower threshold captures more nodes, higher threshold only strong cases.

**Interpretation**:
- **Ratio > 1.0**: System dominated by ceremonial behaviors (status quo bias, resistance to change)
- **Ratio < 1.0**: System dominated by instrumental behaviors (adaptive, problem-solving)
- **Ratio ≈ 1.0**: Balanced system with ceremonial-instrumental conflict

#### REST API

```bash
POST /api/query/ceremonial
Content-Type: application/json

{
  "threshold": 0.5
}
```

**Response**:
```json
{
  "ceremonial": [
    {"id": "...", "label": "Auto Industry Lobbying", "ceremonial_score": 0.8},
    {"id": "...", "label": "Congressional Delays", "ceremonial_score": 0.7}
  ],
  "instrumental": [
    {"id": "...", "label": "Catalytic Converter Tech", "instrumental_score": 0.9},
    {"id": "...", "label": "Emissions Monitoring", "instrumental_score": 0.8}
  ],
  "mixed": [],
  "ratio": 0.67
}
```

#### Example: Clean Air Act Analysis

```python
# Build Clean Air Act scenario (simplified)
auto_industry = service.create_node(
    label="Auto Industry",
    node_type="Actor",
    meta={"ceremonial_score": 0.8, "instrumental_score": 0.2}
)

catalytic_converter = service.create_node(
    label="Catalytic Converter Technology",
    node_type="Technology",
    meta={"ceremonial_score": 0.1, "instrumental_score": 0.9}
)

# Run analysis
analysis = service.get_ceremonial_analysis(threshold=0.5)

# Interpret: CAA had ceremonial resistance (industry delays)
# vs instrumental innovation (catalytic converters)
if analysis['ratio'] > 1.0:
    print("System shows ceremonial dominance - expect implementation delays")
else:
    print("System shows instrumental dominance - expect adaptive innovation")
```

---

### Circular Causation Detection

**Purpose**: Identify feedback loops and circular causation cycles in the system.

**Theory**: Myrdal's cumulative causation concept - economic processes create self-reinforcing or self-limiting cycles. Critical for understanding:
- Reinforcing loops (virtuous/vicious cycles)
- Balancing loops (regulatory feedback)
- Path dependency and lock-in

**Method**: Detects cycles in the directed graph, calculates cycle strength from relationship weights, classifies as reinforcing (net positive feedback) or balancing (net negative feedback).

#### Python API

```python
# Detect circular causation from a source node
cycles = service.get_circular_causation(source_id=node.id)

# Results structure
[
    {
        "nodes": [uuid1, uuid2, uuid3, uuid1],  # Cycle path (starts and ends at source)
        "labels": ["EPA", "Standards", "Emissions", "Health", "EPA"],
        "strength": 0.64,  # Cumulative effect (product of weights)
        "feedback_type": "reinforcing"  # "reinforcing" or "balancing"
    },
    ...
]
```

**Parameters**:
- `source_id` (UUID): Starting node for cycle detection
- `max_depth` (int, default 5): Maximum path length to search (longer = slower but more complete)

**Interpretation**:
- **Strength > 0.5**: Strong feedback loop (likely to dominate system behavior)
- **Strength 0.3-0.5**: Moderate feedback (contributes to dynamics but not dominant)
- **Strength < 0.3**: Weak feedback (may be overshadowed by other forces)
- **Reinforcing**: Amplifies initial change (virtuous/vicious cycle)
- **Balancing**: Dampens change toward equilibrium (regulatory feedback)

#### REST API

```bash
GET /api/query/circular-causation/{source_node_id}
```

**Response**:
```json
{
  "source_id": "550e8400-e29b-41d4-a716-446655440000",
  "cycles": [
    {
      "nodes": ["550e8400-...", "660e8400-...", "770e8400-...", "550e8400-..."],
      "labels": ["EPA Standards", "Auto Compliance", "Industry Lobbying", "EPA Standards"],
      "strength": 0.56,
      "feedback_type": "reinforcing"
    }
  ]
}
```

#### Example: EPA Standards Feedback Loop

```python
# Build EPA standards loop
epa = service.create_node(label="EPA", node_type="Institution")
standards = service.create_node(label="Auto Standards", node_type="PolicyInstrument")
compliance = service.create_node(label="Industry Compliance", node_type="Process")
lobbying = service.create_node(label="Industry Lobbying", node_type="Actor")

# Create causal chain
service.create_relationship(epa.id, standards.id, "mandates", 0.9)
service.create_relationship(standards.id, compliance.id, "requires", 0.8)
service.create_relationship(compliance.id, lobbying.id, "triggers", 0.7)
service.create_relationship(lobbying.id, epa.id, "influences", 0.6)

# Detect cycle
cycles = service.get_circular_causation(epa.id)

# Interpret
for cycle in cycles:
    if cycle['feedback_type'] == 'reinforcing':
        if cycle['strength'] > 0.5:
            print(f"Strong reinforcing loop detected: {cycle['labels']}")
            print("System may exhibit runaway dynamics or lock-in")
    else:
        print(f"Balancing loop: {cycle['labels']}")
        print("System has negative feedback stabilization")
```

**Common Patterns**:
- **Virtuous cycle**: Innovation → Adoption → Learning → More Innovation
- **Vicious cycle**: Pollution → Health → Costs → Reduced Innovation → More Pollution
- **Regulatory balance**: Standards → Compliance → Monitoring → Adjusted Standards

---

### Institutional Holarchy

**Purpose**: Map nested hierarchical structures of institutions (holons within holons).

**Theory**: Arthur Koestler's concept of holarchy - each institution is simultaneously a whole (holon) and a part of a larger whole. Critical for understanding:
- Multi-level governance (federal/state/local)
- Organizational hierarchies
- Nested property rights

**Method**: Traverses institutional containment relationships (`contains`, `composed_of`) to build hierarchical layers.

#### Python API

```python
# Get institutional holarchy for a root institution
holarchy = service.get_holarchy(institution_id=root_institution.id)

# Results structure
{
    "institution_id": uuid,
    "layers": [
        {
            "level": 0,
            "institutions": [{"id": uuid, "label": "EPA"}]
        },
        {
            "level": 1,
            "institutions": [
                {"id": uuid, "label": "Air Quality Division"},
                {"id": uuid, "label": "Water Quality Division"}
            ]
        }
    ],
    "total_depth": 3,
    "total_institutions": 15
}
```

**Parameters**:
- `institution_id` (UUID): Root institution to analyze
- `max_depth` (int, default 10): Maximum hierarchy depth

**Interpretation**:
- **Depth 1-2**: Flat organizational structure
- **Depth 3-5**: Typical bureaucratic hierarchy
- **Depth > 5**: Deep hierarchy (potential coordination challenges)
- **Total institutions**: Organizational complexity measure

#### REST API

```bash
GET /api/query/holarchy/{institution_id}
```

**Response**:
```json
{
  "institution_id": "550e8400-e29b-41d4-a716-446655440000",
  "layers": [
    {
      "level": 0,
      "institutions": [{"id": "550e8400-...", "label": "EPA", "type": "Institution"}]
    },
    {
      "level": 1,
      "institutions": [
        {"id": "660e8400-...", "label": "Air & Radiation Office", "type": "Institution"},
        {"id": "770e8400-...", "label": "Water Office", "type": "Institution"}
      ]
    }
  ],
  "total_depth": 2,
  "total_institutions": 3
}
```

#### Example: EPA Organizational Structure

```python
# Build EPA holarchy
epa = service.create_node(label="EPA", node_type="Institution")
air_office = service.create_node(label="Office of Air & Radiation", node_type="Institution")
water_office = service.create_node(label="Office of Water", node_type="Institution")
regional_office = service.create_node(label="Region 5 Office", node_type="Institution")

# Create containment relationships
service.create_relationship(epa.id, air_office.id, "contains", 1.0)
service.create_relationship(epa.id, water_office.id, "contains", 1.0)
service.create_relationship(epa.id, regional_office.id, "contains", 1.0)

# Get holarchy
holarchy = service.get_holarchy(epa.id)

print(f"EPA organizational depth: {holarchy['total_depth']}")
print(f"Total sub-units: {holarchy['total_institutions']}")

# Interpret coordination complexity
if holarchy['total_depth'] > 4:
    print("Deep hierarchy - coordination challenges likely")
```

---

### Conflict Detection

**Purpose**: Identify contradictions, tensions, and conflicts in the system.

**Theory**: Identifies conflicts between:
- **Value conflicts**: Incompatible normative goals
- **Resource conflicts**: Competition for scarce resources
- **Institutional conflicts**: Contradictory rules or procedures
- **Ceremonial-instrumental conflicts**: Status quo vs change

**Method**: Detects opposing relationship kinds (`opposes`, `conflicts_with`), contradictory metadata, and structural tensions.

#### Python API

```python
# Detect all conflicts in the system
conflicts = service.get_conflicts()

# Results structure
[
    {
        "type": "value_conflict",
        "severity": "high",  # "low", "medium", "high"
        "description": "Environmental protection vs Economic growth",
        "involved_nodes": [uuid1, uuid2],
        "metadata": {...}
    },
    ...
]
```

**Interpretation**:
- **Severity high**: Fundamental conflict requiring resolution
- **Severity medium**: Tension requiring negotiation
- **Severity low**: Minor incompatibility, manageable
- **Type value_conflict**: Normative disagreement (hardest to resolve)
- **Type resource_conflict**: Allocation problem (solvable with redistribution)

#### REST API

```bash
GET /api/query/conflicts
```

**Response**:
```json
{
  "conflicts": [
    {
      "type": "value_conflict",
      "severity": "high",
      "description": "Industry profit vs Public health",
      "involved_nodes": ["550e8400-...", "660e8400-..."],
      "metadata": {"relationship_kinds": ["opposes"]}
    }
  ],
  "total": 1
}
```

#### Example: Clean Air Act Value Conflict

```python
# Build conflict scenario
industry_profit = service.create_node(
    label="Industry Profit Maximization",
    node_type="ValueJudgment"
)

public_health = service.create_node(
    label="Public Health Protection",
    node_type="ValueJudgment"
)

# Create opposing relationship
service.create_relationship(
    industry_profit.id,
    public_health.id,
    "opposes",
    0.9,
    meta={"conflict_type": "value_conflict"}
)

# Detect conflicts
conflicts = service.get_conflicts()

for conflict in conflicts:
    if conflict['severity'] == 'high':
        print(f"High-severity conflict: {conflict['description']}")
        print("Requires policy intervention or institutional change")
```

---

## Advanced Analysis

### Temporal Evolution

**Purpose**: Analyze how the system changed over time periods.

**Theory**: Institutional change is path-dependent and evolutionary. Temporal analysis reveals:
- Critical junctures (rapid institutional change)
- Gradual drift (slow evolution)
- Punctuated equilibrium patterns
- Lock-in and breakout dynamics

**Method**: Queries graph state at regular time intervals, tracking node/relationship creation, modification, and deactivation.

#### Python API

```python
from datetime import datetime, timedelta

# Query temporal evolution
snapshots = service._query_engine.query_temporal_evolution(
    start_date=datetime(1970, 1, 1),
    end_date=datetime(1990, 12, 31),
    time_step=timedelta(days=365*5)  # 5-year intervals
)

# Results structure
[
    {
        "date": "1970-01-01T00:00:00",
        "nodes": 10,  # Active nodes at this time
        "relationships": 25,  # Active relationships
        "avg_weight": 0.65  # Average relationship strength
    },
    {
        "date": "1975-01-01T00:00:00",
        "nodes": 15,
        "relationships": 42,
        "avg_weight": 0.58
    },
    ...
]
```

**Parameters**:
- `start_date` (datetime): Analysis start
- `end_date` (datetime): Analysis end
- `time_step` (timedelta): Interval between snapshots (e.g., 1 year, 5 years)

**Interpretation**:
- **Increasing nodes**: System growth, new actors entering
- **Decreasing nodes**: System contraction, consolidation
- **Increasing avg_weight**: Strengthening relationships, institutionalization
- **Decreasing avg_weight**: Weakening relationships, institutional decline
- **Rapid changes**: Critical junctures, policy shocks

#### REST API

```bash
POST /api/query/temporal-evolution
Content-Type: application/json

{
  "start_date": "1970-01-01T00:00:00Z",
  "end_date": "1990-12-31T23:59:59Z",
  "time_step_days": 1825  # 5 years
}
```

**Response**:
```json
{
  "snapshots": [
    {
      "date": "1970-01-01T00:00:00",
      "nodes": 10,
      "relationships": 25,
      "avg_weight": 0.65
    },
    {
      "date": "1975-01-01T00:00:00",
      "nodes": 15,
      "relationships": 42,
      "avg_weight": 0.58
    }
  ],
  "start_date": "1970-01-01T00:00:00Z",
  "end_date": "1990-12-31T23:59:59Z",
  "time_step_days": 1825,
  "total_snapshots": 5
}
```

#### Example: Clean Air Act Evolution (1970-1990)

```python
from datetime import datetime, timedelta

# Create temporal relationships with valid_from/valid_to
# Example: Auto industry influence declines over time

# 1970-1975: High influence period
rel_1970 = Relationship(
    source_id=auto_industry.id,
    target_id=congress.id,
    kind="influences",
    weight=0.9,
    valid_from=datetime(1970, 1, 1),
    valid_to=datetime(1975, 12, 31)
)

# 1976-1981: Declining influence
rel_1976 = Relationship(
    source_id=auto_industry.id,
    target_id=congress.id,
    kind="influences",
    weight=0.7,
    valid_from=datetime(1976, 1, 1),
    valid_to=datetime(1981, 12, 31)
)

# 1982-present: Weak influence
rel_1982 = Relationship(
    source_id=auto_industry.id,
    target_id=congress.id,
    kind="influences",
    weight=0.5,
    valid_from=datetime(1982, 1, 1),
    valid_to=None  # Ongoing
)

service.create_relationship(rel_1970)
service.create_relationship(rel_1976)
service.create_relationship(rel_1982)

# Query evolution
evolution = service._query_engine.query_temporal_evolution(
    start_date=datetime(1970, 1, 1),
    end_date=datetime(1990, 12, 31),
    time_step=timedelta(days=365*5)
)

# Plot evolution
import matplotlib.pyplot as plt

dates = [s['date'] for s in evolution]
avg_weights = [s['avg_weight'] for s in evolution]

plt.plot(dates, avg_weights)
plt.title("Clean Air Act: Relationship Strength Evolution")
plt.xlabel("Year")
plt.ylabel("Average Weight")
plt.show()

# Interpret
print("1970: Auto industry influence at peak (0.9)")
print("1981: Influence declined to 0.5 after standards compliance")
print("Pattern: Gradual institutional weakening of ceremonial resistance")
```

---

### Uncertainty Propagation

**Purpose**: Calculate how uncertainty compounds through causal pathways.

**Theory**: Uncertainty propagates multiplicatively through causal chains. Critical for:
- Sensitivity analysis (which relationships matter most)
- Risk assessment (how confident are we in outcomes)
- Evidence quality tracking (data source reliability)

**Method**: Multiplies confidence intervals along pathway, calculates cumulative uncertainty range.

#### Python API

```python
# Propagate uncertainty through a causal path
result = service._query_engine.propagate_uncertainty_through_path(
    path=[node1.id, node2.id, node3.id]
)

# Results structure
{
    "path_segments": [
        {
            "source": "NAAQS Standards",
            "target": "Emissions Reduction",
            "weight": 0.8,
            "confidence_interval": (0.7, 0.9)
        },
        {
            "source": "Emissions Reduction",
            "target": "Health Benefits",
            "weight": 0.7,
            "confidence_interval": (0.5, 0.9)
        }
    ],
    "cumulative_effect": 0.56,  # 0.8 * 0.7
    "uncertainty_range": (0.35, 0.81),  # (0.7*0.5, 0.9*0.9)
    "uncertainty_width": 0.46  # Absolute uncertainty
}
```

**Parameters**:
- `path` (List[UUID]): Ordered list of node IDs forming the causal pathway

**Interpretation**:
- **cumulative_effect**: Central estimate of pathway strength
- **uncertainty_range**: 95% confidence interval for effect
- **uncertainty_width**: Absolute uncertainty (higher = less confident)
- **Width > 0.5**: High uncertainty, need better data
- **Width < 0.2**: Low uncertainty, confident estimate

#### REST API

```bash
POST /api/query/uncertainty-propagation
Content-Type: application/json

{
  "path": [
    "550e8400-e29b-41d4-a716-446655440000",
    "660e8400-e29b-41d4-a716-446655440001",
    "770e8400-e29b-41d4-a716-446655440002"
  ]
}
```

**Response**:
```json
{
  "path_segments": [
    {
      "source": "Auto Standards",
      "target": "Catalytic Converters",
      "weight": 0.8,
      "confidence_interval": [0.7, 0.9]
    },
    {
      "source": "Catalytic Converters",
      "target": "Emissions Reduction",
      "weight": 0.9,
      "confidence_interval": [0.8, 0.95]
    }
  ],
  "cumulative_effect": 0.72,
  "uncertainty_range": [0.56, 0.855],
  "uncertainty_width": 0.295
}
```

#### Example: Health Benefits Uncertainty

```python
# Build causal chain with confidence intervals
naaqs = service.create_node(label="NAAQS Standards", node_type="PolicyInstrument")
emissions = service.create_node(label="Emissions Reduction", node_type="Process")
health = service.create_node(label="Health Benefits", node_type="Resource")

# Create relationships with uncertainty
# EPA estimate: 0.8 ± 0.1
rel1 = Relationship(
    source_id=naaqs.id,
    target_id=emissions.id,
    kind="produces",
    weight=0.8,
    confidence_interval=(0.7, 0.9),
    uncertainty_type="epistemic",
    data_sources=["EPA 1997"],
    confidence=0.85
)

# Contested estimate: EPA says 0.7, industry says 0.5
rel2 = Relationship(
    source_id=emissions.id,
    target_id=health.id,
    kind="produces",
    weight=0.7,  # Central estimate
    confidence_interval=(0.5, 0.9),  # Wide range
    uncertainty_type="epistemic",
    data_sources=["EPA 1997", "Industry studies", "Academic research"],
    source_agreement="low",  # Sources disagree
    confidence=0.60  # Lower confidence due to disagreement
)

service.create_relationship(rel1)
service.create_relationship(rel2)

# Propagate uncertainty
path = [naaqs.id, emissions.id, health.id]
result = service._query_engine.propagate_uncertainty_through_path(path)

print(f"Central estimate: {result['cumulative_effect']:.2f}")
print(f"95% CI: ({result['uncertainty_range'][0]:.2f}, {result['uncertainty_range'][1]:.2f})")
print(f"Uncertainty width: {result['uncertainty_width']:.2f}")

# Interpret
if result['uncertainty_width'] > 0.4:
    print("HIGH UNCERTAINTY: Health benefits estimate highly uncertain")
    print("Reason: EPA and industry data sources disagree substantially")
    print("Recommendation: Conduct independent epidemiological study")
else:
    print("Acceptable uncertainty for policy decision")
```

**Sensitivity Analysis Use Case**:

```python
# Which relationship contributes most uncertainty?
# Vary each relationship's CI and observe impact

# Sensitivity to emissions reduction uncertainty
rel2_tight = Relationship(..., confidence_interval=(0.65, 0.75))  # Tighter
result_tight = service._query_engine.propagate_uncertainty_through_path(path)

# Compare
print(f"Original uncertainty: {result['uncertainty_width']:.2f}")
print(f"With tighter emissions CI: {result_tight['uncertainty_width']:.2f}")
print(f"Improvement: {(result['uncertainty_width'] - result_tight['uncertainty_width']) / result['uncertainty_width'] * 100:.1f}%")

# This identifies which data gaps matter most for reducing overall uncertainty
```

---

## Network Structure Analysis

### Centrality Measures

**Purpose**: Identify most important nodes using various centrality metrics.

**Available Metrics**:
- **Betweenness**: Nodes on many shortest paths (brokers, bridges)
- **Closeness**: Nodes with short paths to all others (communication hubs)
- **Degree**: Nodes with many connections (hubs)
- **Eigenvector**: Nodes connected to other important nodes (influence)

#### Python API

```python
# Get most central nodes by type
central_nodes = service._query_engine.get_most_central_nodes(
    node_type=Institution,
    centrality_type="betweenness",
    limit=10
)

# Results: [(node_id, centrality_score), ...]
for node_id, score in central_nodes:
    node = service.get_node(node_id)
    print(f"{node.label}: {score:.3f}")
```

**Interpretation**:
- **Betweenness > 0.1**: Critical bridge/broker role
- **Closeness > 0.5**: Central communication position
- **Degree > avg**: Well-connected hub
- **Eigenvector > 0.1**: Influential position

---

### Path Finding

**Purpose**: Find shortest causal paths between nodes.

#### Python API

```python
# Find shortest path
path = service._query_engine.find_shortest_path(
    source_id=source_node.id,
    target_id=target_node.id,
    relationship_kinds=["influences", "enables"]  # Optional filter
)

# path is List[UUID] of node IDs along the path
```

**Interpretation**:
- **Path length 1**: Direct relationship
- **Path length 2-3**: Short causal chain (typical)
- **Path length > 5**: Distant indirect effect
- **No path**: Nodes in different components

---

### Community Detection

**Purpose**: Identify clusters/communities of tightly connected nodes.

#### Python API

```python
# Detect communities
communities = service._query_engine.identify_communities(
    algorithm="louvain"
)

# Results: {community_id: [node_id, ...], ...}
for comm_id, node_ids in communities.items():
    print(f"Community {comm_id}: {len(node_ids)} nodes")
```

**Interpretation**:
- **Few large communities**: Integrated system
- **Many small communities**: Fragmented system
- **Isolated communities**: Potential coordination failures

---

## Interpreting Results

### Ceremonial-Instrumental Ratio

| Ratio | Interpretation | Policy Implication |
|-------|---------------|-------------------|
| > 2.0 | Severe ceremonial dominance | Expect strong resistance to change |
| 1.5-2.0 | Moderate ceremonial bias | Change requires overcoming status quo |
| 0.8-1.5 | Balanced system | Context-dependent dynamics |
| 0.5-0.8 | Moderate instrumental bias | Innovation-friendly environment |
| < 0.5 | Severe instrumental dominance | Potential instability, lack of structure |

### Circular Causation Strength

| Strength | Interpretation | System Behavior |
|----------|---------------|-----------------|
| > 0.7 | Dominant feedback loop | Path-dependent, lock-in likely |
| 0.5-0.7 | Strong feedback | Significant but not deterministic |
| 0.3-0.5 | Moderate feedback | One of several forces |
| < 0.3 | Weak feedback | Overshadowed by other dynamics |

### Conflict Severity

| Severity | Action Required | Resolution Difficulty |
|----------|----------------|---------------------|
| High | Immediate policy intervention | Difficult, fundamental values |
| Medium | Negotiation, compromise | Moderate, institutional design |
| Low | Monitor, minor adjustments | Easy, technical solutions |

---

## Examples

### Example 1: Full Clean Air Act Analysis

```python
from api.sfm_service import SFMService
from datetime import datetime, timedelta
import json

# Initialize
service = SFMService()

# Build scenario (simplified)
epa = service.create_node(label="EPA", node_type="Institution")
congress = service.create_node(label="Congress", node_type="Institution")
auto_industry = service.create_node(
    label="Auto Industry",
    node_type="Actor",
    meta={"ceremonial_score": 0.8}
)
catalytic_converter = service.create_node(
    label="Catalytic Converter",
    node_type="Technology",
    meta={"instrumental_score": 0.9}
)
health = service.create_node(label="Public Health", node_type="Resource")

# Relationships with temporal and uncertainty metadata
service.create_relationship(
    epa.id, congress.id, "reports_to", 0.9,
    meta={"valid_from": "1970-01-01", "valid_to": None}
)

service.create_relationship(
    auto_industry.id, congress.id, "influences", 0.7,
    meta={
        "valid_from": "1970-01-01",
        "confidence_interval": [0.6, 0.8],
        "uncertainty_type": "epistemic"
    }
)

service.create_relationship(
    catalytic_converter.id, health.id, "improves", 0.8,
    meta={"confidence_interval": [0.7, 0.9]}
)

# Initialize query engine
service.initialize_query_engine()

# Run all analyses
print("=== CEREMONIAL VS INSTRUMENTAL ===")
ceremonial = service.get_ceremonial_analysis(threshold=0.5)
print(f"Ratio: {ceremonial['ratio']:.2f}")
if ceremonial['ratio'] > 1.0:
    print("System shows ceremonial resistance to change")

print("\n=== CIRCULAR CAUSATION ===")
cycles = service.get_circular_causation(epa.id)
for cycle in cycles[:3]:  # Top 3
    print(f"Loop: {' -> '.join(cycle['labels'])}")
    print(f"Strength: {cycle['strength']:.2f}, Type: {cycle['feedback_type']}")

print("\n=== CONFLICTS ===")
conflicts = service.get_conflicts()
for conflict in conflicts:
    print(f"{conflict['severity'].upper()}: {conflict['description']}")

print("\n=== TEMPORAL EVOLUTION ===")
evolution = service._query_engine.query_temporal_evolution(
    start_date=datetime(1970, 1, 1),
    end_date=datetime(1990, 12, 31),
    time_step=timedelta(days=365*5)
)
print(f"Snapshots: {len(evolution)}")
print(f"1970 avg weight: {evolution[0]['avg_weight']:.2f}")
print(f"1990 avg weight: {evolution[-1]['avg_weight']:.2f}")

print("\n=== UNCERTAINTY PROPAGATION ===")
path = [catalytic_converter.id, health.id]
uncertainty = service._query_engine.propagate_uncertainty_through_path(path)
print(f"Central estimate: {uncertainty['cumulative_effect']:.2f}")
print(f"95% CI: ({uncertainty['uncertainty_range'][0]:.2f}, {uncertainty['uncertainty_range'][1]:.2f})")
print(f"Uncertainty width: {uncertainty['uncertainty_width']:.2f}")

# Export results
results = {
    "ceremonial_analysis": ceremonial,
    "circular_causation": cycles,
    "conflicts": conflicts,
    "temporal_evolution": evolution,
    "uncertainty_propagation": uncertainty
}

with open("clean_air_act_analysis.json", "w") as f:
    json.dump(results, f, indent=2, default=str)

print("\nResults exported to clean_air_act_analysis.json")
```

---

### Example 2: Sensitivity Analysis Workflow

```python
# Identify which uncertainty sources matter most

# Build pathway: Policy -> Technology -> Adoption -> Outcome
policy = service.create_node(label="Policy", node_type="PolicyInstrument")
tech = service.create_node(label="Technology", node_type="Technology")
adoption = service.create_node(label="Adoption Rate", node_type="Process")
outcome = service.create_node(label="Environmental Outcome", node_type="Resource")

# Create relationships with baseline uncertainty
rel1 = service.create_relationship(
    policy.id, tech.id, "enables", 0.8,
    meta={"confidence_interval": [0.7, 0.9]}
)

rel2 = service.create_relationship(
    tech.id, adoption.id, "drives", 0.6,
    meta={"confidence_interval": [0.4, 0.8]}  # Wide uncertainty
)

rel3 = service.create_relationship(
    adoption.id, outcome.id, "produces", 0.7,
    meta={"confidence_interval": [0.6, 0.8]}
)

# Baseline uncertainty
service.initialize_query_engine()
path = [policy.id, tech.id, adoption.id, outcome.id]
baseline = service._query_engine.propagate_uncertainty_through_path(path)

print(f"Baseline uncertainty width: {baseline['uncertainty_width']:.3f}")

# Sensitivity test: Tighten rel2 uncertainty (better adoption data)
rel2_tight = service.update_relationship(
    rel2.id,
    Relationship(..., meta={"confidence_interval": [0.55, 0.65]})
)

improved = service._query_engine.propagate_uncertainty_through_path(path)
reduction = (baseline['uncertainty_width'] - improved['uncertainty_width']) / baseline['uncertainty_width']

print(f"Improved uncertainty width: {improved['uncertainty_width']:.3f}")
print(f"Reduction: {reduction*100:.1f}%")
print(f"Conclusion: Better adoption rate data would reduce overall uncertainty by {reduction*100:.1f}%")
```

---

## Best Practices

1. **Always initialize query engine before analysis**:
   ```python
   service.initialize_query_engine()
   ```

2. **Use appropriate thresholds**:
   - Ceremonial analysis: 0.5 (balanced), 0.3 (inclusive), 0.7 (strict)
   - Circular causation: max_depth=5 (default), 3 (fast), 7 (thorough)

3. **Interpret results in context**:
   - Ceremonial ratio depends on scenario scope (government-heavy vs market-heavy)
   - Feedback strength depends on weight scale (0-1 typical)
   - Conflicts reflect modeled relationships, not all real-world tensions

4. **Combine multiple methods**:
   - Ceremonial analysis identifies resistance
   - Circular causation explains dynamics
   - Temporal analysis shows evolution
   - Uncertainty quantifies confidence

5. **Document assumptions**:
   - Record data sources in relationship metadata
   - Track confidence intervals for contested estimates
   - Note temporal scope limitations

---

## Contact & Support

For questions about analysis methods:
- GitHub Issues: [sfm-core/issues](https://github.com/your-org/sfm-core/issues)
- Documentation: [sfm-core/docs](https://github.com/your-org/sfm-core/docs)

---

**Last Updated**: 2026-05-26  
**Version**: 1.0
