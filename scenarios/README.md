# SFM Historical Scenarios

This directory contains implementations of historical policy scenarios modeled using the Social Fabric Matrix (SFM) Core framework. These scenarios serve multiple purposes:

1. **Validate framework applicability** to real-world policy analysis
2. **Discover gaps** in node types, relationships, and analytical methods
3. **Demonstrate methodology** for applying Hayden's SFM to complex systems
4. **Provide reference models** for future SFM work

## Available Scenarios

### Clean Air Act 1972 (Starter)

**File**: `clean_air_act_starter.py`  
**Status**: Template (needs research and completion)  
**Difficulty**: Moderate  
**Time Estimate**: 8-16 hours

Models the 1972 Clean Air Act Amendments as a complex socio-economic system with institutional actors, policy instruments, technologies, and weighted relationships showing causal pathways.

**Key Features**:
- Institutional hierarchy (EPA → State agencies)
- Industry resistance vs. public health advocacy
- Technology-forcing provisions and adoption patterns
- Economic costs vs. health benefits
- Temporal evolution 1970-1990

**Learning Outcomes**:
- Practice multi-source fact verification
- Develop intuition for relationship weight selection
- Identify framework limitations through real use
- Understand ceremonial vs. instrumental analysis in practice

## Quick Start

### Prerequisites

1. **Start the SFM API server**:
```bash
cd /path/to/sfm-core
uvicorn api.rest.app:app --reload
```

2. **Install dependencies**:
```bash
pip install requests
```

3. **Choose a scenario** and review the detailed prompt:
```bash
# Read the full instructions
cat ../prompts/clean_air_act_scenario.md

# Review the template
cat ../prompts/scenario_analysis_template.md
```

### Running a Scenario

```bash
# Run the starter script (incomplete, needs research)
python clean_air_act_starter.py

# Output will show what's been created and what needs work
```

### Completing a Scenario

The starter scripts are **templates** that need research and completion:

1. **Research Phase** (3-6 hours)
   - Read primary sources (legislation, official reports)
   - Read secondary sources (scholarly books and articles)
   - Document facts with 2+ sources each
   - Create a bibliography

2. **Implementation Phase** (3-6 hours)
   - Fill in the TODOs in the starter script
   - Create all nodes with proper metadata
   - Define relationships with justified weights
   - Add comprehensive source citations

3. **Analysis Phase** (1-2 hours)
   - Run ceremonial analysis
   - Detect circular causation loops
   - Identify conflicts
   - Map institutional holarchy
   - Trace outcome pathways

4. **Gap Analysis Phase** (1-2 hours)
   - Document missing node types or relationships
   - Note usability issues encountered
   - Identify theoretical limitations
   - Propose specific improvements

5. **Documentation Phase** (1-2 hours)
   - Write scenario documentation
   - Create gap analysis report
   - Export model to JSON
   - Summarize findings

## Scenario Structure

Each completed scenario should include:

```
scenarios/
├── [scenario_name]/
│   ├── README.md                    # Scenario overview
│   ├── build_model.py              # Node and relationship creation
│   ├── run_analysis.py             # Execute all SFM analyses
│   ├── validate_model.py           # Historical accuracy checks
│   ├── model_export.json           # Complete model dump
│   ├── sources.bib                 # Bibliography of references
│   └── gap_analysis.md             # Identified framework gaps
```

## Recommended Research Sources

### Primary Sources
- **Legislation**: Original bills, public laws, amendments
- **Government Reports**: Congressional committee reports, GAO studies, agency documents
- **Official Statistics**: Bureau of Labor Statistics, EPA data, Census Bureau
- **Court Cases**: Supreme Court decisions, circuit court rulings (if applicable)

### Secondary Sources
- **Peer-reviewed Journals**: Journal of Policy Analysis and Management, Journal of Public Economics, etc.
- **Books**: Published by university presses or established publishers
- **Think Tank Reports**: Brookings, RAND, Urban Institute (verify with other sources)
- **News Archives**: Historical newspapers for contemporary accounts (verify with official sources)

### Source Quality Hierarchy

1. **Primary sources** (legislation, official data) - Most authoritative
2. **Peer-reviewed research** - High quality, vetted
3. **Government reports** - Generally reliable, verify methodology
4. **Think tank research** - Check for bias, verify data
5. **News articles** - Use for context only, verify facts elsewhere
6. **Blogs/opinions** - Avoid for factual claims

**Rule**: Every major factual claim needs 2+ sources from tiers 1-3.

## Weight Justification Guidelines

Relationship weights (0.0 to 1.0) should be **evidence-based**, not arbitrary:

### Weight Ranges

- **0.9-1.0**: Near-determinative
  - Legal requirements with enforcement
  - Physical/technical necessities
  - Example: "Catalytic converter adoption depends on federal mandate" (1.0)

- **0.7-0.9**: Strong influence
  - Regulatory authority with some discretion
  - Major funding leverage
  - Example: "EPA influences state agencies through funding" (0.85)

- **0.5-0.7**: Moderate influence
  - Significant lobbying or advocacy
  - Market pressures
  - Example: "Industry lobbying influences policy design" (0.65)

- **0.3-0.5**: Weak to moderate
  - Indirect effects
  - Competing factors present
  - Example: "Public opinion influences congressional action" (0.45)

- **0.1-0.3**: Weak influence
  - Minor factors
  - Easily overridden
  - Example: "Individual consumer choice affects aggregate demand" (0.2)

### Documentation Requirements

For each weighted relationship, document in metadata:
```json
{
  "mechanism": "How does source affect target?",
  "weight_justification": "Why this specific weight?",
  "source_1": "Citation showing the relationship exists",
  "source_2": "Citation showing the strength/magnitude",
  "alternative_estimates": "Other estimates if conflicting data exists"
}
```

## Common Pitfalls

### 1. Insufficient Source Verification
❌ **Don't**: "Everyone knows the EPA was created in 1970"  
✅ **Do**: Cite Reorganization Plan No. 3 of 1970 (35 FR 15623) + EPA.gov history

### 2. Arbitrary Weights
❌ **Don't**: "EPA influences states (weight: 0.7) because it feels moderately strong"  
✅ **Do**: "EPA influences states (weight: 0.85) based on Section 110 mandate authority + 80% federal funding for state implementation (Portney 1992, p.45)"

### 3. Anachronistic Modeling
❌ **Don't**: Include nodes/relationships that didn't exist in the time period  
✅ **Do**: Model the system as it existed 1970-1977, note later developments separately

### 4. Scope Creep
❌ **Don't**: Try to model every detail of a complex policy  
✅ **Do**: Focus on strategic-level institutional actors and primary causal pathways

### 5. Missing the Point
❌ **Don't**: Just create a model  
✅ **Do**: Use the exercise to discover what's missing or difficult in the framework

## Gap Analysis Framework

As you build scenarios, systematically document:

### 1. Missing Node Types
- What entities can't be represented with current types?
- Examples: Informal social movements, ecological systems, information networks

### 2. Missing Relationship Kinds
- What connections can't be expressed?
- Examples: Temporal sequences, probabilistic causation, conditional dependencies

### 3. Missing Analytical Methods
- What questions can't be answered with current queries?
- Examples: Counterfactual analysis, sensitivity testing, distributional impacts

### 4. Usability Issues
- Where is the API awkward or tedious?
- Examples: Bulk operations, templating, import/export formats

### 5. Documentation Gaps
- What's unclear or missing from docs?
- Examples: Weight selection guidance, scenario examples, best practices

## Contributing Completed Scenarios

When you complete a scenario:

1. **Verify completeness**:
   - [ ] All nodes have 2+ source citations
   - [ ] All relationships have justified weights
   - [ ] All four SFM analyses executed
   - [ ] Gap analysis completed with examples
   - [ ] Model exports to JSON successfully
   - [ ] Documentation written

2. **Create a pull request** with:
   - Complete scenario directory
   - Updated this README with scenario summary
   - Gap analysis findings in `docs/gap_analysis_[scenario].md`

3. **Include in PR description**:
   - Summary of what the scenario models
   - Key insights from the analysis
   - Most critical gaps discovered
   - Estimated time to complete (for future users)

## Future Scenarios

Suggested scenarios to develop:

### Environmental
- [ ] Clean Water Act (1972)
- [ ] Endangered Species Act (1973)
- [ ] Superfund/CERCLA (1980)

### Economic
- [ ] Glass-Steagall Act (1933)
- [ ] Telecommunications Act (1996)
- [ ] Dodd-Frank Act (2010)

### Social
- [ ] Social Security Act (1935)
- [ ] Civil Rights Act (1964)
- [ ] Medicare/Medicaid (1965)

### Technology
- [ ] Internet Development (ARPANET to WWW)
- [ ] Renewable Energy Policy Evolution
- [ ] Agricultural Green Revolution

## Questions or Issues?

- Review `/prompts/clean_air_act_scenario.md` for detailed instructions
- Check `/prompts/scenario_analysis_template.md` for the general template
- Review API documentation in `/API_DOCUMENTATION.md`
- Open an issue on GitHub if you discover bugs or unclear documentation

---

**Remember**: The goal isn't just to create models, but to **systematically test and improve the SFM Core framework** through real-world application. Your gap analysis is as valuable as the model itself.
