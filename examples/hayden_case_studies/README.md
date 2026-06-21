# Hayden Case Studies

This directory contains demonstration implementations of the Social Fabric Matrix (SFM) methodology based on Frederick Gregory Hayden's research. Each case study showcases specific SFM analytical capabilities and is grounded in published research.

## Overview

The SFM is a framework for analyzing social systems through the lens of institutional economics. These case studies demonstrate how SFM can be used to map institutional relationships, identify circular causation, analyze ceremonial-instrumental conflicts, and evaluate normative criteria.

**Core Methodology:**
- Hayden, F. G. (2006). *Policymaking for a Good Society: The Social Fabric Matrix Approach to Policy Analysis and Program Evaluation*. Springer.

## Case Studies

### 1. Clean Air Act of 1970
**File:** `clean_air_act_1970.py`

**Primary Citation:**
- Hayden's general SFM methodology applied to environmental policy

**SFM Features Demonstrated:**
- **Circular causation**: EPA standards → state implementation → emissions reductions → health improvements → public support → stronger standards
- **Institutional holarchy**: Three governance levels (federal→state→local)
- **Ceremonial vs instrumental**: Technology-forcing requirements (instrumental) balanced by cooperative federalism (ceremonial)
- **Feedback cycles**: Emission monitoring → violations → enforcement → compliance
- **Normative criteria evaluation**: Deliveries evaluated against health protection, environmental justice, and innovation criteria
- **Temporal modeling**: Implementation timeline with phase transitions (1970-1977)
- **Conflicts**: Environmental justice gaps between universal goals and disproportionate EJ community exposure

**Scope:**
- **Components**: 18 (federal agencies, states, industries, communities, value systems)
- **Delivery cells**: 24 non-empty cells
- **Deliveries**: ~37 total (rules, money, pollution, authority, information)
- **Criteria**: 3 (Public Health Protection, Environmental Justice, Technology Forcing & Innovation)
- **Time period**: 1970-2010
- **Data sources**: EPA, Congressional Research Service, Nature Communications, peer-reviewed journals

**Key Insights:**
- Demonstrates effectiveness of technology-forcing standards (catalytic converter mandate)
- Reveals persistent environmental justice disparities despite universal air quality improvements
- Maps complex federal-state cooperative federalism delivery system

---

### 2. Corporate Director Networks
**File:** `director_networks.py`

**Primary Citation:**
- Hayden, F. G., Wood, S., & Kaya, I. (2002). "Patterns of Delivery and Correlation Coefficients in Social Fabric Matrix Analyses of Corporate Director Networks." *Journal of Economic Issues*, 36(2), 345-352.

**SFM Features Demonstrated:**
- **Network centrality**: Interlocking directorates as information delivery networks
- **Power delivery analysis**: Money, authority, and information flows
- **Delivery correlation**: Positive correlations between compensation and governance authority
- **Cultural values**: Corporate governance ceremonial frameworks

**Scope:**
- **Components**: 10 (financial institutions, corporations, industry associations, individual directors)
- **Delivery cells**: 21 non-empty cells
- **Deliveries**: ~28 total (money, authority, information)
- **Network structure**: Simplified Fortune 500 financial-industrial linkages

**Key Insights:**
- Directors serving on multiple boards deliver information across financial-industrial boundaries
- High-centrality directors facilitate capital flows
- Interlocking pattern: financial institutions → corporations (capital), directors → corporations (authority), corporations → directors (compensation + information access)

---

### 3. Low-Level Radioactive Waste Policy
**File:** `radioactive_waste.py`

**Primary Citation:**
- Hayden, F. G., & Bolduc, R. (2000). "Instrumental Reasoning and Normative Analysis in LLRW Policy Analysis." *Journal of Economic Issues*, 34(4), 831-849.

**SFM Features Demonstrated:**
- **Ceremonial-instrumental conflict**: NIMBY resistance (ceremonial) vs. scientific risk management (instrumental)
- **Cultural values analysis**: Quantified ceremonial/instrumental components in delivery cells
- **Interstate compact structure**: Regional coordination mechanisms
- **Normative criteria evaluation**: Health protection, interstate equity, scientific management
- **Threshold monitoring**: Waste volume thresholds with alert system
- **Policy deadlock analysis**: Ceremonial encapsulation preventing instrumental solutions

**Scope:**
- **Components**: 11 (host state, 4 generator states, federal NRC, interstate compact, environmental groups, citizens)
- **Delivery cells**: 26 non-empty cells
- **Deliveries**: ~30 total (pollution/waste, money, rules, authority, information)
- **Criteria**: 3 (Public Health Protection, Interstate Equity, Scientific Risk Management)
- **Cultural values**: Quantified ceremonial_component and instrumental_component scores

**Key Insights:**
- Demonstrates how high ceremonial resistance (0.9) can block instrumental solutions
- Interstate compact payments ($5M-$10M) insufficient to overcome ceremonial NIMBY barriers
- Environmental groups can provide instrumental problem-solving (0.8 instrumental score)
- Policy ultimately failed when ceremonial values dominated rational risk analysis

---

### 4. Nebraska K-12 Education Finance (TEEOSA)
**File:** `nebraska_k12_finance.py`

**Primary Citation:**
- Hoffman, S., & Hayden, F. G. (2007). "Equilibrium and Emergence for Social Fabric Matrix Analysis." *Journal of Economic Issues*, 41(4), 1105-1126.

**SFM Features Demonstrated:**
- **Circular causation**: Property taxes → state appropriations → TEEOSA formula → district funding → student outcomes → property values
- **Formula-based delivery system**: TEEOSA (Tax Equity and Educational Opportunities Support Act) as algorithmic delivery mechanism
- **Holarchical governance**: State legislature → Department of Education → local school districts
- **Feedback loops**: Student enrollment changes trigger formula recalculations
- **Ceremonial-instrumental balance**: Formula equalization (instrumental) vs. local control (ceremonial)

**Scope:**
- **Components**: 5 (legislature, department of education, school districts, taxpayers, students)
- **Delivery cells**: 6 non-empty cells
- **Deliveries**: ~9 total (money, rules, authority, services)
- **Formula**: TEEOSA school funding formula ($800M annually in study period)

**Key Insights:**
- Demonstrates formula-based delivery systems in SFM framework
- Shows tension between state equalization goals and local property tax autonomy
- 249 school districts coordinated through single delivery system

---

## Running the Case Studies

Each case study can be run independently:

```bash
# Individual case studies
python examples/hayden_case_studies/clean_air_act_1970.py
python examples/hayden_case_studies/director_networks.py
python examples/hayden_case_studies/radioactive_waste.py
python examples/hayden_case_studies/nebraska_k12_finance.py

# Cross-case comparison
python examples/hayden_case_studies/compare_cases.py
```

Each study will:
1. Build the SFM delivery matrix
2. Run the full SFM analysis battery (circular causation, holarchy, ceremonial-instrumental, feedback cycles, conflicts, criteria evaluation)
3. Export to Excel (`.xlsx` file in same directory)
4. Print key findings with citations

## Analysis Battery Components

All case studies are analyzed using the comprehensive SFM analysis battery (implemented in `graph/analysis_report.py`):

1. **Ceremonial vs Instrumental Classification** (Veblen-Hayden)
   - Identifies deliveries that preserve status quo (ceremonial) vs. solve problems (instrumental)

2. **Circular Causation Paths** (Myrdal cumulative causation)
   - Detects feedback loops and reinforcing cycles in the delivery system

3. **Institutional Holarchy Levels** (Koestler)
   - Maps hierarchical nesting of institutions (federal→state→local, etc.)

4. **Feedback Cycles**
   - Identifies closed-loop regulatory and delivery systems

5. **Conflicts/Contradictions**
   - Detects tensions between competing values or institutional goals

6. **Normative Criteria Evaluation** (Hayden's normative framework)
   - Scores which deliveries serve or undermine specified social criteria
   - Classifies alignment as SERVES, UNDERMINES, NEUTRAL, or UNKNOWN
   - Calculates aggregate alignment scores (-1.0 to +1.0)

7. **Temporal Evolution** (when temporal clocks present)
   - Tracks system changes over time through phase transitions

## Excel Export Format

Each case study exports to a three-sheet Excel workbook:

- **Sheet 1: Matrix View** - N×N grid showing deliveries between components
- **Sheet 2: Cell Descriptions** - Narrative descriptions for each non-empty cell (required per Hayden methodology)
- **Sheet 3: Delivery Details** - Tabular listing of all deliveries with quantities, units, temporal rates

## Comparative Metrics

Cross-case comparison table (generated by `compare_cases.py`):

| Metric | Clean Air | Director Networks | Radioactive Waste | Nebraska K-12 |
|--------|-----------|-------------------|-------------------|---------------|
| Components | 18 | 10 | 11 | 5 |
| Non-empty cells | 24 | 21 | 26 | 6 |
| Total deliveries | ~37 | ~28 | ~30 | ~9 |
| Circular causation paths | ✓ | ✓ | ✓ | ✓ |
| Holarchy levels | 3 | 3 | 4 | 3 |
| C/I conflicts detected | ✓ | - | ✓✓ | ✓ |
| Normative criteria | 3 | - | 3 | - |
| Temporal modeling | ✓ | - | ✓ | - |

## Data Verification

Case studies prioritize empirical grounding:

- **Clean Air Act**: Uses verified EPA data, Congressional Research Service reports, and peer-reviewed journals (Nature Communications, ScienceDirect)
- **Director Networks**: Based on Hayden, Wood & Kaya (2002) published correlation analysis
- **Radioactive Waste**: Grounded in Hayden & Bolduc (2000) LLRW policy analysis
- **Nebraska K-12**: Derived from Hoffman & Hayden (2007) TEEOSA formula study

All quantified deliveries cite data sources. Where data is unavailable, deliveries are marked as qualitative or estimated.

## Research Fidelity

These implementations aim for high fidelity to Hayden's canonical SFM methodology:

- **Square matrices**: Components appear on both axes (component×component, not institution×criteria)
- **Multiple heterogeneous deliveries per cell**: Cells can contain multiple distinct delivery types
- **Cell descriptions required**: Non-empty cells must have narrative descriptions (Hayden deliverable standard)
- **Relationship-based evaluation**: Criteria evaluation uses explicit relationships, not implicit scoring
- **Cultural values integration**: Ceremonial and instrumental components quantified where applicable

See `docs/SFM_FIDELITY_ANALYSIS.md` for detailed methodology adherence analysis.

## Citation

If you use these case studies in research, please cite:

**For the SFM methodology:**
```
Hayden, F. G. (2006). Policymaking for a Good Society: The Social Fabric Matrix 
Approach to Policy Analysis and Program Evaluation. Springer.
```

**For specific case studies, cite the relevant paper:**
- Director networks: Hayden, Wood & Kaya (2002)
- Radioactive waste: Hayden & Bolduc (2000)
- Nebraska K-12: Hoffman & Hayden (2007)
- Clean Air Act: Original analysis based on EPA and peer-reviewed sources

## Additional Resources

- **Main documentation**: `../../docs/`
- **SFM methodology guide**: `../../docs/hayden_sfm_guide.md`
- **API reference**: `../../docs/api/`
- **Source code**: `../../graph/`, `../../models/`, `../../api/`

## Contributing

When adding new case studies:

1. Base on published Hayden research or well-documented policy systems
2. Include complete citation in docstring
3. Specify which SFM features the study demonstrates
4. Use verified data sources where possible (cite in comments)
5. Include cell descriptions for all non-empty cells
6. Run the full analysis battery
7. Export to Excel for validation
8. Add entry to this README with summary statistics
9. Update `compare_cases.py` to include new study

## License

These case studies are educational demonstrations of the SFM methodology. The underlying research is cited appropriately. See repository LICENSE for code licensing.
