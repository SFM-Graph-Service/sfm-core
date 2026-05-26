# SFM Scenario Analysis Template

This is a reusable template for analyzing historical policy scenarios using SFM Core.

## Quick Start Prompt for Claude

```
I need you to build a Social Fabric Matrix model of [POLICY/EVENT] using the SFM Core REST API.

## Your Task

1. **Research Phase**
   - Gather facts about [POLICY/EVENT] from 2+ credible sources per claim
   - Identify key institutions, actors, technologies, and policy instruments
   - Document economic impacts with quantitative data where available

2. **Model Design**
   - Design nodes using appropriate SFM Core node types (Institution, Actor, PolicyInstrument, Technology, Resource, etc.)
   - Define weighted relationships (0.0-1.0) with evidence-based justifications
   - Create relationship metadata documenting sources and mechanisms

3. **API Implementation**
   - Write Python scripts to create all nodes via POST /api/v1/nodes/
   - Create relationships via POST /api/v1/relationships/
   - Export the complete model via GET /api/v1/nodes/ and /api/v1/relationships/

4. **Analysis**
   - Run ceremonial analysis: POST /api/v1/query/ceremonial
   - Detect circular causation: GET /api/v1/query/circular-causation/{node_id}
   - Find conflicts: GET /api/v1/query/conflicts
   - Map holarchy: GET /api/v1/query/holarchy/{institution_id}
   - Trace outcome pathways through the relationship graph

5. **Gap Analysis**
   - Document what node types, relationships, or analyses are missing
   - Identify usability issues with the API or framework
   - Note theoretical limitations of the SFM methodology
   - Provide specific examples and proposed solutions

6. **Deliverables**
   - Complete Python implementation scripts
   - Documentation with all sources cited
   - Gap analysis report with actionable recommendations
   - JSON export of the full model

## API Reference

Base URL: http://localhost:8000/api/v1

### Available Node Types
- Node (base type)
- Actor (sector, role, influence_capacity)
- Institution (layer, scope, enforcement_mechanism)
- PolicyInstrument (instrument_type, target_behavior, effectiveness)
- Technology (maturity, adoption_rate, environmental_impact)
- Resource (resource_type, quantity, renewability)
- Process (process_type, efficiency, sustainability)
- TransactionCost (cost_type, magnitude, distribution)
- Belief, Value, Norm, Attitude (cultural nodes)
- NetworkStructure, DeliveryRelationship, CriteriaStandard (network nodes)
- And 20+ more specialized types (see /api/v1/nodes/types)

### Common Relationship Kinds
- "influences" - general influence or causation
- "depends_on" - dependency relationship
- "conflicts_with" - opposition or tension
- "enables" - makes possible or facilitates
- "constrains" - limits or restricts
- Custom kinds allowed (use descriptive strings)

### Relationship Weights (0.0 to 1.0)
- 0.9-1.0: Determinative, nearly absolute
- 0.7-0.9: Strong, substantial effect
- 0.5-0.7: Moderate, significant but not dominant
- 0.3-0.5: Weak to moderate, notable but limited
- 0.1-0.3: Weak, minor influence
- 0.0-0.1: Negligible, minimal effect

## Example: [POLICY_NAME]

### Context
[Brief description of the policy/event and why it matters]

### Time Period
[Start date] to [End date]

### Key Questions to Answer
1. What institutions were created, modified, or abolished?
2. Who were the primary actors and what were their motivations?
3. What technologies or economic changes enabled or resulted from the policy?
4. What conflicts emerged and how were they resolved (or not)?
5. What feedback loops developed?
6. What were the measurable outcomes?

### Expected Node Count
- Institutions: [estimate]
- Actors: [estimate]
- Policy Instruments: [estimate]
- Technologies: [estimate]
- Others: [estimate]
- **Total**: [estimate]

### Expected Relationship Count
- Influences: [estimate]
- Dependencies: [estimate]
- Conflicts: [estimate]
- Others: [estimate]
- **Total**: [estimate]

### Source Requirements
- Minimum 2 sources per major factual claim
- Prefer primary sources (legislation, official reports) and peer-reviewed research
- Document conflicting sources and explain resolution

### Success Metrics
- [ ] Model captures all major institutional actors
- [ ] Relationship weights justified with evidence
- [ ] All SFM analyses run successfully
- [ ] Outcomes match historical record
- [ ] Gaps documented with specific examples
- [ ] All sources verified and cited
```

## Scenario Difficulty Levels

### Level 1: Simple (2-4 hours)
- Single policy intervention
- 10-20 nodes, 15-30 relationships
- Clear institutional actors
- Well-documented outcomes
- Example: Creation of a specific regulatory agency

### Level 2: Moderate (6-10 hours)
- Complex policy package
- 30-50 nodes, 50-100 relationships
- Multiple institutional layers
- Competing interests
- Example: Clean Air Act 1972

### Level 3: Advanced (15+ hours)
- System transformation
- 50+ nodes, 100+ relationships
- Long time horizon
- Multiple feedback loops
- Example: New Deal reforms, Welfare Reform Act

## Recommended Scenarios

### Environmental Policy
- Clean Air Act (1970, 1977 amendments)
- Clean Water Act (1972)
- Superfund/CERCLA (1980)
- Endangered Species Act (1973)

### Economic Policy
- Glass-Steagall Act (1933)
- Telecommunications Act (1996)
- Dodd-Frank Act (2010)
- NAFTA/USMCA

### Social Policy
- Social Security Act (1935)
- Civil Rights Act (1964)
- Medicare/Medicaid (1965)
- Welfare Reform (1996)

### Technology/Innovation
- Internet development (ARPANET → WWW)
- Renewable energy subsidies
- Agricultural technology adoption (Green Revolution)
- Telecommunications deregulation

## Template Scripts

### Minimal Node Creation
```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

def create_node(label, node_type, description="", meta=None):
    response = requests.post(
        f"{BASE_URL}/nodes/",
        json={
            "label": label,
            "description": description,
            "node_type": node_type,
            "meta": meta or {}
        }
    )
    response.raise_for_status()
    return response.json()["id"]

# Example usage
epa_id = create_node(
    label="Environmental Protection Agency",
    node_type="Institution",
    description="Federal environmental regulator",
    meta={"established": "1970", "source": "EPA.gov"}
)
```

### Minimal Relationship Creation
```python
def create_relationship(source_id, target_id, kind, weight=None, meta=None):
    response = requests.post(
        f"{BASE_URL}/relationships/",
        json={
            "source_id": source_id,
            "target_id": target_id,
            "kind": kind,
            "weight": weight,
            "meta": meta or {}
        }
    )
    response.raise_for_status()
    return response.json()["id"]

# Example usage
rel_id = create_relationship(
    source_id=epa_id,
    target_id=state_agency_id,
    kind="influences",
    weight=0.85,
    meta={"mechanism": "Federal mandate", "source": "CAA Section 110"}
)
```

### Run Analysis
```python
def analyze_ceremonial(threshold=0.5):
    response = requests.post(
        f"{BASE_URL}/query/ceremonial",
        json={"threshold": threshold}
    )
    return response.json()

def find_cycles(node_id):
    response = requests.get(
        f"{BASE_URL}/query/circular-causation/{node_id}"
    )
    return response.json()

def detect_conflicts():
    response = requests.get(f"{BASE_URL}/query/conflicts")
    return response.json()
```

## Gap Documentation Template

```markdown
### Gap: [Short Name]

**Category**: Node Type / Relationship Kind / Analysis Method / API Feature / Documentation

**Severity**: Critical / High / Medium / Low

**Description**: 
[What's missing from the framework]

**Discovery Context**:
[Specific scenario and moment when you encountered this gap]

**Current Workaround**:
[How you handled it, if possible]

**Impact on Analysis**:
[What insights are lost or difficult to obtain]

**Proposed Solution**:
[Specific, implementable recommendation]

**Example Implementation** (if applicable):
```python
# How the proposed feature might work
```

**Related Gaps**:
- [Link to related gaps]

**Priority Justification**:
[Why this should be addressed at given priority level]
```

## Final Checklist

Before submitting your scenario analysis:

- [ ] All nodes have descriptions and metadata
- [ ] All relationships have weights and justifications
- [ ] Every major claim has 2+ sources cited
- [ ] All four SFM analyses executed (ceremonial, circular, conflicts, holarchy)
- [ ] Gap analysis includes specific examples from the scenario
- [ ] Python scripts are complete and runnable
- [ ] Model can be exported and re-imported via JSON
- [ ] Documentation explains modeling choices
- [ ] Recommendations are specific and actionable

---

**Use this template** for any historical policy scenario analysis to systematically test and improve the SFM Core framework.
