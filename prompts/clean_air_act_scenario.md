# Historical Scenario Analysis: 1972 Clean Air Act Amendments

## Objective

Build a comprehensive Social Fabric Matrix model of the 1972 Clean Air Act Amendments using the SFM Core REST API. This exercise will:

1. **Test framework applicability** to real-world policy analysis
2. **Discover gaps** in node types, relationship kinds, and analytical methods
3. **Validate usefulness** of Hayden's SFM methodology for historical policy evaluation
4. **Ensure factual accuracy** through multi-source verification

## Background Context

The Clean Air Act Amendments of 1972 (formally enacted in 1970 with major amendments in 1977) represented a transformative shift in U.S. environmental policy. Model this as a complex socio-economic system with:

- **Institutional changes**: EPA creation, state implementation plans, federal standards
- **Economic impacts**: Technology adoption costs, health benefits, compliance burdens
- **Social outcomes**: Public health improvements, environmental justice issues, employment effects
- **Technological evolution**: Catalytic converters, scrubbers, monitoring systems
- **Ceremonial vs. instrumental tensions**: Industry resistance vs. public health goals

## Phase 1: Research and Fact Verification

Before creating any API calls, research and document the following. **All facts must be verified from at least 2 independent scholarly or governmental sources.**

### Required Historical Elements

1. **Key Institutions**
   - Environmental Protection Agency (EPA) - established 1970
   - State environmental agencies
   - Industry groups (Auto Manufacturers Association, etc.)
   - Environmental advocacy groups (Sierra Club, Natural Resources Defense Council)
   - Congressional committees involved

2. **Major Actors**
   - Political actors (Nixon, Muskie, key legislators)
   - Industry leaders and lobbying organizations
   - Environmental advocates
   - Affected communities (urban populations, industrial workers)

3. **Technologies**
   - Catalytic converters (timing, adoption rate, cost)
   - Smokestack scrubbers
   - Air quality monitoring systems
   - Alternative fuel research

4. **Economic Metrics** (with sources)
   - Implementation costs for industry
   - Public health savings (reduced mortality, morbidity)
   - Job creation/loss in affected sectors
   - GDP impact estimates

5. **Policy Instruments**
   - National Ambient Air Quality Standards (NAAQS)
   - State Implementation Plans (SIPs)
   - Technology-forcing provisions
   - Enforcement mechanisms

### Documentation Format

For each fact, provide:
```
FACT: [Statement]
SOURCE 1: [Author, Title, Publisher, Year, Page/URL]
SOURCE 2: [Author, Title, Publisher, Year, Page/URL]
RELEVANCE: [Why this matters for the SFM model]
```

## Phase 2: Model Design

Based on your research, design the SFM model structure:

### Node Categories

Identify and categorize nodes using available SFM Core node types:

**Institutions** (use `Institution` node type):
- EPA (layer: formal_rule, scope: federal)
- State environmental agencies (layer: formal_rule, scope: state)
- Industry trade associations (layer: informal_norm, scope: sector)

**Actors** (use `Actor` node type):
- Federal government (sector: public, role: regulator)
- Auto manufacturers (sector: private, role: producer)
- Environmental groups (sector: civic, role: advocate)
- Affected communities (sector: public, role: beneficiary)

**Policy Instruments** (use `PolicyInstrument` node type):
- NAAQS standards (type: regulatory, target: air quality)
- SIP requirements (type: planning, target: state compliance)
- Technology mandates (type: economic, target: emissions reduction)

**Technologies** (use `Technology` node type):
- Catalytic converters (maturity: emerging_1970s)
- Emissions monitoring systems (maturity: established)

**Resources** (use `Resource` node type):
- Federal funding for implementation
- Technical expertise
- Political capital

**Economic Impacts** (use appropriate economic analysis nodes):
- Implementation costs (TransactionCost)
- Health benefits (externality reduction)
- Employment effects

### Relationship Design

Design weighted relationships with justified weights (0.0 to 1.0):

**Influence Relationships** (`kind: "influences"`):
- EPA → State agencies (weight: 0.9 - strong regulatory authority)
- Environmental groups → Congressional action (weight: 0.6 - significant but not determinative)
- Industry lobbying → Policy design (weight: 0.7 - substantial influence on implementation details)

**Dependency Relationships** (`kind: "depends_on"`):
- Catalytic converter adoption → Federal standards (weight: 1.0 - absolute dependency)
- State compliance → Federal funding (weight: 0.8 - strong but not total)

**Conflict Relationships** (`kind: "conflicts_with"`):
- Industry profit motives → Compliance costs (weight: 0.9 - direct opposition)
- Short-term economic costs → Long-term health benefits (weight: 0.7 - temporal tension)

**Custom Relationship Kinds** (if needed):
- `kind: "enables"` - for technology enabling policy
- `kind: "constrains"` - for regulations constraining behavior
- `kind: "benefits_from"` - for economic benefit flows

### Temporal Considerations

Model the system at three timepoints:
1. **Pre-1970**: Baseline conditions
2. **1970-1977**: Initial implementation period
3. **1977-1990**: Mature implementation with 1977 amendments

## Phase 3: API Implementation

### Setup and Health Check

```bash
# Start the API server
uvicorn api.rest.app:app --reload

# Verify connectivity
curl http://localhost:8000/api/v1/health
```

### Node Creation Script

Create a Python script `clean_air_act_model.py` that:

1. **Creates all institutional nodes** with proper metadata:
```python
import requests
import json
from typing import Dict, List, Any

BASE_URL = "http://localhost:8000/api/v1"

def create_institution(label: str, description: str, meta: Dict[str, str]) -> str:
    """Create an institution node and return its ID."""
    response = requests.post(
        f"{BASE_URL}/nodes/",
        json={
            "label": label,
            "description": description,
            "node_type": "Institution",
            "meta": meta
        }
    )
    response.raise_for_status()
    return response.json()["id"]

# Example usage
epa_id = create_institution(
    label="Environmental Protection Agency",
    description="Federal agency created 1970 to enforce environmental protection laws",
    meta={
        "established": "1970",
        "layer": "formal_rule",
        "scope": "federal",
        "source_1": "EPA History: https://www.epa.gov/history",
        "source_2": "Reorganization Plan No. 3 of 1970"
    }
)
```

2. **Creates all other node types** (actors, policies, technologies, resources)

3. **Documents node IDs** in a structured format for relationship creation

4. **Validates creation** by retrieving and verifying each node

### Relationship Creation Script

Create relationships with weights based on historical evidence:

```python
def create_relationship(source_id: str, target_id: str, kind: str, 
                       weight: float, meta: Dict[str, Any]) -> str:
    """Create a relationship with weight and metadata."""
    response = requests.post(
        f"{BASE_URL}/relationships/",
        json={
            "source_id": source_id,
            "target_id": target_id,
            "kind": kind,
            "weight": weight,
            "meta": meta
        }
    )
    response.raise_for_status()
    return response.json()["id"]

# Example: EPA influences state agencies
rel_id = create_relationship(
    source_id=epa_id,
    target_id=state_agency_id,
    kind="influences",
    weight=0.9,
    meta={
        "mechanism": "Federal standards and funding leverage",
        "source_1": "Switzer, Environmental Politics (1994), p.89",
        "source_2": "Portney, Natural Resources Journal (1992)",
        "time_period": "1970-1977"
    }
)
```

### Weight Justification Template

For each relationship, document:
```python
{
    "relationship": "EPA → State Agencies (influences)",
    "weight": 0.9,
    "justification": "Federal enforcement authority under CAA Section 113",
    "evidence": [
        "Melnick (1983): 'EPA retained veto power over state plans'",
        "Ringquist (1993): '90% of state plans modified by EPA'",
        "Federal funding tied to compliance"
    ],
    "weight_calculation": "High authority (0.5) + funding leverage (0.3) + enforcement power (0.1) = 0.9"
}
```

## Phase 4: Analysis and Validation

### Run SFM Analyses

1. **Ceremonial vs. Instrumental Analysis**
```python
# Identify ceremonial (symbolic) vs instrumental (efficiency-seeking) institutions
response = requests.post(
    f"{BASE_URL}/query/ceremonial",
    json={"threshold": 0.5}
)
ceremonial_analysis = response.json()

# Expected insights:
# - Some industry compliance may be ceremonial (minimal action)
# - Environmental advocacy may have ceremonial elements (symbolic victories)
# - EPA enforcement should be instrumental (measurable outcomes)
```

2. **Circular Causation Detection**
```python
# Find feedback loops (e.g., health improvements → political support → stronger regulations)
response = requests.get(f"{BASE_URL}/query/circular-causation/{epa_id}")
cycles = response.json()

# Document identified cycles and their policy implications
```

3. **Conflict Detection**
```python
# Identify institutional conflicts
response = requests.get(f"{BASE_URL}/query/conflicts")
conflicts = response.json()

# Expected conflicts:
# - Industry profit vs. compliance costs
# - State autonomy vs. federal mandates
# - Economic growth vs. environmental protection
```

4. **Holarchy Analysis**
```python
# Analyze institutional hierarchy and power relations
response = requests.get(f"{BASE_URL}/query/holarchy/{epa_id}")
holarchy = response.json()

# Map the regulatory hierarchy from federal to state to local
```

### Outcome Modeling

Use the relationship graph to trace policy outcomes:

1. **Health Impact Pathway**
   - NAAQS standards → Emissions reductions → Air quality improvements → Health outcomes
   - Weight the pathway and calculate expected effect magnitude

2. **Economic Impact Pathway**
   - Technology mandates → Industry costs → Employment effects → Economic adjustments
   - Identify offsetting factors (health savings, new industries)

3. **Behavioral Change Pathway**
   - Public awareness → Political pressure → Stronger enforcement → Compliance improvements
   - Model the feedback loop dynamics

### Validation Checks

1. **Historical Accuracy**
   - Do modeled relationships align with documented historical events?
   - Are outcome predictions consistent with actual 1970-1990 data?
   - Cross-reference with EPA historical reports

2. **Internal Consistency**
   - Do relationship weights sum logically?
   - Are conflicting relationships properly modeled?
   - Do circular causation loops make theoretical sense?

3. **Multi-Source Verification**
   - Every major claim backed by 2+ sources
   - Conflicting sources documented and reconciled
   - Primary sources (legislation, EPA reports) prioritized over secondary

## Phase 5: Gap Analysis

### Framework Coverage Gaps

Document what the current SFM Core framework **cannot adequately model**:

1. **Missing Node Types**
   - Are there important entities not captured by existing node types?
   - Examples to check:
     - Informal social norms not tied to institutions?
     - Ecological systems affected by the policy?
     - Information flows and knowledge networks?

2. **Missing Relationship Types**
   - What relationship kinds are needed beyond `influences`, `depends_on`, `conflicts_with`?
   - Examples to check:
     - Temporal sequencing ("must_precede")
     - Partial dependencies ("partially_enables")
     - Probabilistic relationships ("may_cause")
     - Intensity variations beyond linear weights

3. **Missing Analytical Methods**
   - What analyses would be valuable but aren't available?
   - Examples to check:
     - Temporal evolution tracking (how relationships change over time)
     - Counterfactual analysis (what if EPA wasn't created?)
     - Sensitivity analysis (how robust are outcomes to weight changes?)
     - Distributional impacts (who benefits, who pays?)

4. **Metadata Limitations**
   - What contextual information can't be captured in current metadata?
   - Examples to check:
     - Time-varying properties
     - Geographic scope variations
     - Uncertainty/confidence levels
     - Data quality indicators

### Usability Gaps

Document where the API makes modeling difficult:

1. **Data Entry Challenges**
   - Is it tedious to create complex models?
   - Missing bulk import features?
   - No template system for common patterns?

2. **Query Limitations**
   - Can you ask the questions that matter for policy analysis?
   - Missing aggregation or filtering capabilities?
   - No export formats for visualization tools?

3. **Documentation Gaps**
   - Unclear how to model specific scenarios?
   - Missing examples for complex relationship patterns?
   - Insufficient guidance on weight selection?

### Theoretical Gaps

Document where Hayden's SFM methodology itself may be limited:

1. **Modeling Power Dynamics**
   - Can the framework adequately capture power asymmetries?
   - Are ceremonial/instrumental distinctions sufficient?

2. **Temporal Dynamics**
   - Does the static graph model limit understanding of change processes?
   - How to represent path dependencies and lock-in effects?

3. **Uncertainty and Complexity**
   - How to model unknown or contested causal relationships?
   - Can the framework handle emergent properties?

## Phase 6: Deliverables

### 1. Model Documentation

Create `docs/scenarios/clean_air_act_1972.md`:

```markdown
# Clean Air Act 1972 SFM Model

## Executive Summary
- [Model purpose and scope]
- [Key findings from analysis]
- [Policy insights derived]

## Historical Context
- [Detailed background with sources]

## Model Structure
- [Node inventory with justifications]
- [Relationship inventory with weights and evidence]
- [Model assumptions and limitations]

## Implementation
- [API usage details]
- [Data sources and verification]
- [Code repository location]

## Analysis Results
- [Ceremonial analysis findings]
- [Circular causation patterns]
- [Conflict analysis]
- [Holarchy mapping]
- [Outcome pathway tracing]

## Validation
- [Historical accuracy assessment]
- [Multi-source verification summary]
- [Expert review notes]

## Gap Analysis
- [Framework coverage gaps]
- [Usability issues encountered]
- [Theoretical limitations identified]

## Recommendations
- [API improvements needed]
- [New node types to consider]
- [Additional analytical methods]
- [Documentation enhancements]
```

### 2. Python Implementation

Complete, runnable scripts:
- `clean_air_act_model.py` - Node and relationship creation
- `clean_air_act_analysis.py` - Run all analyses
- `clean_air_act_validation.py` - Validate against historical data
- `requirements.txt` - Dependencies

### 3. Data Files

- `clean_air_act_nodes.json` - Node definitions with metadata
- `clean_air_act_relationships.json` - Relationship definitions with weights
- `clean_air_act_sources.bib` - BibTeX of all references
- `clean_air_act_export.json` - Full model export via API

### 4. Gap Analysis Report

`docs/gap_analysis_clean_air_act.md`:

```markdown
# SFM Framework Gap Analysis: Clean Air Act Case Study

## Critical Gaps (High Priority)

### 1. [Gap Name]
- **Type**: Node Type / Relationship / Analysis Method / API Feature
- **Description**: [What's missing]
- **Impact**: [Why this matters]
- **Example from CAA**: [Specific scenario that revealed this gap]
- **Proposed Solution**: [Recommendation]
- **Complexity**: Low / Medium / High

## Moderate Gaps (Medium Priority)
[Same structure]

## Minor Gaps (Nice to Have)
[Same structure]

## Theoretical Considerations
[Deeper questions about SFM methodology itself]

## Summary and Prioritization
[Recommended roadmap for addressing gaps]
```

### 5. Visualization

If possible, create:
- Network diagram of the institutional structure
- Pathway diagrams for key outcomes
- Timeline showing temporal evolution
- Heat map of relationship weights

## Success Criteria

This scenario analysis succeeds if it:

1. ✅ **Creates a complete model** with 30+ nodes and 50+ relationships
2. ✅ **All facts verified** from 2+ independent sources
3. ✅ **Runs all available analyses** (ceremonial, circular causation, conflicts, holarchy)
4. ✅ **Identifies specific gaps** with concrete examples
5. ✅ **Produces actionable recommendations** for framework improvements
6. ✅ **Documents everything** for reproducibility
7. ✅ **Demonstrates real-world applicability** of Hayden's SFM to policy analysis

## Research Sources to Start With

### Primary Sources
- Clean Air Act of 1970 (Public Law 91-604)
- Clean Air Act Amendments of 1977 (Public Law 95-95)
- EPA Historical Documents: https://www.epa.gov/history
- Congressional Record (debates and committee reports)

### Secondary Scholarly Sources
- Melnick, R. Shep. *Regulation and the Courts: The Case of the Clean Air Act* (1983)
- Portney, Paul R. *Public Policies for Environmental Protection* (1992)
- Switzer, Jacqueline Vaughn. *Environmental Politics: Domestic and Global Dimensions* (1994)
- Ringquist, Evan J. *Environmental Protection at the State Level* (1993)

### Data Sources
- EPA Air Trends: https://www.epa.gov/air-trends
- Bureau of Labor Statistics: Employment in affected industries
- CDC/NCHS: Mortality and morbidity trends 1970-1990
- Congressional Budget Office: Cost-benefit analyses

## Notes and Constraints

- **Scope limitation**: Focus on 1970-1990 period for manageability
- **Geographic scope**: U.S. federal policy (acknowledge state variations exist)
- **Model granularity**: Aim for strategic-level model, not implementation details
- **Source quality**: Prioritize peer-reviewed and governmental sources
- **Time budget**: This is a comprehensive exercise - allocate 8-16 hours of focused work

## Expected Learning Outcomes

By completing this scenario, you will:

1. Understand how to apply SFM methodology to real-world policy
2. Identify practical limitations of the current framework
3. Develop intuition for relationship weight selection
4. Practice multi-source fact verification
5. Create a reference model for future SFM work
6. Generate a concrete roadmap for framework improvements

---

**Ready to begin?** Start with Phase 1 research and fact verification. Build your source bibliography before touching the API.
