# Framework Bridges: Connecting SFM to Sustainability and Governance Frameworks

This document positions the Social Fabric Matrix (SFM) implementation in relation to two major frameworks:

1. **Raworth's Doughnut Economics** — Global sustainability boundaries (continuous indicators)
2. **Ostrom's Social-Ecological Systems (SES) / Institutional Analysis and Development (IAD)** — Commons governance (rules-in-use, action arenas)

Both bridges extend SFM's analytical reach while preserving Hayden's institutional delivery chain methodology. **The mappings themselves constitute research contributions**, demonstrating how institutional analysis can integrate with sustainability science and commons governance frameworks.

---

## 1. Doughnut Economics ↔ SFM Bridge

### 1.1 Framework Overview

**Raworth's Doughnut Economics** (2017):
- **Structure**: 12 social foundation dimensions + 9 ecological ceiling boundaries = 21 criteria
- **Measurement**: Continuous indicators (CO2 ppm, income ratios, access percentages)
- **Thresholds**: Scientific/normative boundaries defining "safe and just space"
- **Level**: Global/national aggregate indicators
- **Purpose**: Identify overshoot (ecological) and shortfall (social) conditions

**Hayden's Social Fabric Matrix**:
- **Structure**: Square N×N delivery matrix between institutional components
- **Measurement**: Boolean/weighted deliveries representing transactions
- **Evaluation**: Normative criteria assessment (correlation weights)
- **Level**: Institutional meso-level (deliveries between specific actors)
- **Purpose**: Trace delivery chains and evaluate normative outcomes

### 1.2 The Core Methodological Challenge

**Problem**: How do we connect continuous boundary indicators (Doughnut) with discrete institutional deliveries (SFM)?

- **Doughnut**: "CO2 concentration is 420 ppm, threshold is 350 ppm → 20% overshoot"
- **SFM**: "EPA → Auto Manufacturers delivers emissions standards (weight: +0.8)"

The gap is not just measurement scale—it's **epistemological**:
- Doughnut measures **system states** (outcomes)
- SFM traces **institutional actions** (delivery chains)

### 1.3 Bridge Solution: `boundary_state_to_delivery()`

The bridge converts continuous boundary readings into delivery weights while preserving both:

1. **Quantitative precision** (Doughnut's indicator values)
2. **Institutional attribution** (SFM's delivery chain structure)

**Function Signature**:

```python
def boundary_state_to_delivery(
    indicator_value: float,
    threshold: float,
    polarity: Literal["shortfall", "overshoot"]
) -> float:
    """
    Convert continuous Doughnut boundary state to SFM delivery weight.
    
    Returns weight in [-1.0, +1.0]:
    - Negative weights: Delivery undermines boundary (drives overshoot/shortfall)
    - Positive weights: Delivery helps meet boundary (reduces overshoot/addresses shortfall)
    - Zero: At threshold
    """
```

**Weight Calculation**:

- **Shortfall boundaries** (social foundation):
  ```
  weight = (indicator_value - threshold) / |threshold|
  ```
  - Below threshold → negative (shortfall)
  - Above threshold → positive (meeting/exceeding foundation)

- **Overshoot boundaries** (ecological ceiling):
  ```
  weight = -(indicator_value - threshold) / |threshold|
  ```
  - Above threshold → negative (overshoot)
  - Below threshold → positive (within safe zone)

**Example — CO2 Emissions** (Ecological Ceiling):

```python
# Current CO2: 420 ppm, Safe threshold: 350 ppm
weight = boundary_state_to_delivery(420, 350, "overshoot")
# Result: -0.20 (20% overshoot, negative delivery weight)

# EPA standards reduce to 300 ppm
weight = boundary_state_to_delivery(300, 350, "overshoot")
# Result: +0.14 (within safe zone, positive delivery weight)
```

### 1.4 Integration Pattern

**Step 1**: Create Doughnut boundaries as SFM criteria nodes

```python
air_pollution = SFMCriteria(
    label="Air Pollution",
    description="Ecological ceiling for air quality (PM2.5, CO2, etc.)",
    criteria_type=CriteriaType.ENVIRONMENTAL,
    meta={
        "doughnut_dimension": "ecological_ceiling",
        "polarity": "overshoot",
        "threshold": 350  # ppm CO2
    }
)
```

**Step 2**: Link institutional deliveries to boundaries via `evaluates_to` relationships

```python
# Pollution delivery from coal plants → Air Pollution boundary
pollution_delivery = Delivery(
    delivery_type="pollution",
    delivery_content="Annual CO2 emissions",
    quantity=420,  # Current ppm
    units="ppm CO2"
)

service.add_delivery_to_matrix(
    matrix,
    source=coal_power_plant,
    target=air_pollution_boundary,
    delivery=pollution_delivery
)
```

**Step 3**: Evaluate impact using `boundary_state_to_delivery()`

```python
weight = boundary_state_to_delivery(
    indicator_value=420,
    threshold=350,
    polarity="overshoot"
)
# weight = -0.20 (driving overshoot)
```

**Step 4**: Trace delivery chains to identify institutional drivers

SFM's circular causation analysis reveals:
- Which institutions deliver pollution (negative weights)
- Which institutions deliver emissions reductions (positive weights)
- Net institutional impact on boundary

### 1.5 Research Contributions

1. **Downscaling**: Applies global Doughnut framework to national/local policy analysis
2. **Institutional attribution**: Links macro-level boundary states to meso-level delivery chains
3. **Policy leverage**: Identifies which institutional deliveries to strengthen/weaken
4. **Normative integration**: Preserves both Doughnut's thresholds and SFM's evaluative framework

**Methodological Caveat**: The mapping is not "discovered" but **constructed**. The choice to represent boundary states as delivery weights is a modeling decision that enables analysis but introduces assumptions:

- **Linearity**: Weight calculation assumes linear scaling (may miss tipping points)
- **Attribution**: Assigns boundary impacts to delivery chains (causal inference)
- **Aggregation**: Net impact sums delivery weights (assumes additive effects)

These are *transparent research choices*, not neutral technical operations.

---

## 2. Ostrom SES/IAD ↔ SFM Bridge

### 2.1 Framework Overview

**Ostrom's SES/IAD Framework**:
- **Structure**: Multi-tier framework with 50+ variables across social, ecological, and governance subsystems
- **Core Concepts**:
  - **Rules-in-Use**: Institutional rules actually followed (vs. formal rules)
  - **Action Arena**: Space where actors with positions interact in action situations
  - **Action Situations**: Specific decision points (harvest, monitor, sanction)
  - **Outcomes**: Results that feed back to modify rules/conditions
- **Level**: Meso-level commons governance (community forests, fisheries, irrigation)
- **Purpose**: Understand institutional diversity in natural resource governance

**Conceptual Alignment with SFM**:

| Ostrom Concept | SFM Equivalent | Mapping Notes |
|----------------|----------------|---------------|
| **Actors** | Institutional Components (Nodes) | Community association, resource users, monitors |
| **Rules-in-Use** | Institutions (Nodes) | Boundary rules, aggregation rules, payoff rules |
| **Action Arena** | Node Cluster | All actors + rules in a governance space |
| **Action Situations** | Delivery Cells | Quota setting, harvesting, monitoring, sanctioning |
| **Outcomes** | Criteria Evaluations | Forest sustainability, equity, legitimacy |
| **Interactions** | Deliveries | Authority, voice, extraction, surveillance |

### 2.2 Bridge Value

**What Ostrom Provides to SFM**:
- Granular vocabulary for rules (7 rule types: boundary, position, choice, aggregation, information, payoff, scope)
- Diagnostic framework for commons governance (design principles, scale matching)
- SES variables for systematic comparison across cases

**What SFM Adds to Ostrom**:
- **Delivery chain tracing**: Follow governance flows through institutional network
- **Normative evaluation**: Assess outcomes against social criteria (not just efficiency)
- **Circular causation**: Explicit feedback loops between institutions and outcomes
- **Matrix representation**: Visual/computational structure for complex governance systems

### 2.3 Mapping Example: Community Forest Governance

See `examples/framework_bridges/ostrom_ses_iad_example.py` for full implementation.

**Setup**:
- **Resource System**: Community forest (timber + ecosystem services)
- **Actors**: Community association, forest users, monitoring authority, external government
- **Rules-in-Use**: Harvesting quota (boundary rule), monitoring protocol (information rule), sanctioning (payoff rule), deliberation (aggregation rule)

**SFM Encoding**:

1. **Actors → Nodes**:
   ```python
   community_association = Node(
       label="Community Forest Association",
       meta={"ostrom_type": "actor", "ostrom_role": "collective_choice_authority"}
   )
   ```

2. **Rules → Nodes**:
   ```python
   harvesting_quota_rule = Node(
       label="Harvesting Quota Rule",
       meta={
           "ostrom_type": "rule_in_use",
           "ostrom_rule_type": "boundary_rule",
           "rule_statement": "Attribute: Community members | May: Harvest | Up to: 5 m³/year"
       }
   )
   ```

3. **Action Situations → Delivery Cells**:
   ```python
   # Quota Setting
   service.add_delivery_to_matrix(
       matrix,
       source=community_association,
       target=forest_users,
       delivery=Delivery(
           delivery_type="authority",
           delivery_content="Harvesting quota of 5 cubic meters per member per year"
       ),
       cell_description="Association establishes quotas per boundary rule"
   )
   
   # Harvesting
   service.add_delivery_to_matrix(
       matrix,
       source=forest_users,
       target=forest_resource_system,
       delivery=Delivery(
           delivery_type="extraction",
           delivery_content="Timber harvesting within quota limits",
           quantity=500.0,
           units="cubic_meters/year"
       )
   )
   
   # Monitoring
   service.add_delivery_to_matrix(
       matrix,
       source=monitoring_authority,
       target=forest_users,
       delivery=Delivery(
           delivery_type="information",
           delivery_content="Monthly random plot monitoring"
       )
   )
   ```

4. **Outcomes → Criteria**:
   ```python
   forest_sustainability = SFMCriteria(
       label="Forest Sustainability",
       criteria_type=CriteriaType.ENVIRONMENTAL,
       meta={"ostrom_type": "outcome"}
   )
   
   # Link harvesting outcome to sustainability
   service.create_relationship(Relationship(
       source_id=forest_resource_system.id,
       target_id=forest_sustainability.id,
       kind="evaluates_to",
       weight=0.7  # Positive: sustainable harvest
   ))
   ```

### 2.4 Analytical Gains

**From Ostrom Perspective**:
- Visualize entire action arena as SFM square matrix
- Trace delivery chains: quota setting → harvesting → monitoring → sanctioning → deliberation → quota revision
- Quantify rule impact through delivery weights

**From SFM Perspective**:
- Ostrom's 7 rule types enrich institutional classification
- SES diagnostic variables provide systematic metadata
- Design principles (Ostrom 1990) become testable via delivery chain structure

**Example Insight**:

> Ostrom's **"graduated sanctions"** design principle becomes traceable as a delivery chain:
> - Monitoring Authority → Users: Information delivery (surveillance)
> - Monitoring Authority → Users: Sanction delivery (graduated fines)
> - Users → Association: Voice delivery (appeal process)
>
> SFM reveals: Legitimacy outcome depends on **balance** between sanction strength and voice opportunities.

### 2.5 Research Contributions

1. **Computational operationalization**: Ostrom's conceptual framework becomes computable SFM structure
2. **Cross-case comparison**: SFM matrices enable systematic comparison of governance structures (matrix similarity metrics)
3. **Design principle testing**: SFM delivery chain properties (connectivity, reciprocity, feedback) correlate with Ostrom's design principles
4. **Normative integration**: Adds social criteria evaluation to Ostrom's efficiency-focused outcome analysis

**Methodological Caveat**: The SES framework is deliberately **non-prescriptive** (no universal best practices). Encoding it in SFM risks:
- Over-formalizing context-dependent rules
- Losing qualitative institutional detail in quantification
- Imposing SFM's normative evaluation on Ostrom's diagnostic approach

The bridge is **not neutral translation**—it reframes Ostrom's descriptive analysis through SFM's evaluative lens.

---

## 3. Methodological Reflections

### 3.1 Mapping as Research Contribution

Both bridges are **modeling choices**, not discoveries:

- **Doughnut→SFM**: Decision to represent boundary states as delivery weights
- **Ostrom→SFM**: Decision to encode rules-in-use as institutional nodes

These mappings:
- **Enable** new analyses (institutional attribution of boundary impacts, computational SES comparison)
- **Introduce** new assumptions (linearity, causal attribution, evaluative framing)
- **Privilege** certain questions (delivery chains, normative outcomes) over others (micro-level behavior, evolutionary dynamics)

The research value lies in:
1. **Transparency**: Explicit documentation of mapping choices
2. **Utility**: New analytical capabilities (downscaling Doughnut, operationalizing SES)
3. **Critique**: Recognition that mappings shape what we see/miss

### 3.2 When to Use Each Bridge

**Use Doughnut-SFM when**:
- Analyzing policy impacts on global sustainability boundaries
- Downscaling planetary boundaries to national/local institutional analysis
- Identifying institutional drivers of overshoot/shortfall
- Evaluating **"Who delivers what impact on which boundaries?"**

**Use Ostrom-SFM when**:
- Analyzing commons governance structures
- Comparing institutional designs across resource systems
- Tracing rule-in-use delivery chains
- Evaluating **"How do rules shape action situations and outcomes?"**

**Use both when**:
- Analyzing natural resource governance with sustainability outcomes
- Example: Community forest management (Ostrom structure) evaluated against climate/biodiversity boundaries (Doughnut)

### 3.3 Limitations

**Doughnut-SFM**:
- Assumes institutional deliveries causally drive boundary states (attribution challenge)
- Linear weight calculation misses tipping points and threshold dynamics
- Global thresholds may not apply at local/national scale (downscaling validity)

**Ostrom-SFM**:
- Rules-in-use are context-embedded; encoding as nodes may lose situated meaning
- SFM's normative evaluation contradicts SES framework's diagnostic neutrality
- Matrix representation privileges network structure over evolutionary/temporal processes

### 3.4 Future Research Directions

**Doughnut-SFM**:
- Non-linear weight functions for tipping point boundaries
- Multi-scale analysis (local deliveries aggregating to national boundary impacts)
- Temporal dynamics (delivery rates → boundary state change over time)
- Integration with Earth system models (SFM institutional analysis → ESM forcing)

**Ostrom-SFM**:
- SES variable encoding as node metadata (systematic comparative analysis)
- Design principle formalization as matrix properties (e.g., "nested enterprises" → multi-level holarchy)
- Robustness analysis (which delivery chain structures resist shocks?)
- Agent-based extensions (SFM structure + behavioral rules → simulation)

---

## 4. References

### Doughnut Economics

- Raworth, K. (2017). *Doughnut Economics: Seven Ways to Think Like a 21st-Century Economist*. Chelsea Green Publishing.
- Raworth, K. (2012). A safe and just space for humanity: Can we live within the doughnut? *Oxfam Discussion Paper*.
- Steffen, W., et al. (2015). Planetary boundaries: Guiding human development on a changing planet. *Science*, 347(6223), 1259855.
- O'Neill, D. W., et al. (2018). A good life for all within planetary boundaries. *Nature Sustainability*, 1(2), 88-95.

### Ostrom SES/IAD Framework

- Ostrom, E. (1990). *Governing the Commons: The Evolution of Nodes for Collective Action*. Cambridge University Press.
- Ostrom, E. (2005). *Understanding Institutional Diversity*. Princeton University Press.
- Ostrom, E. (2007). A diagnostic approach for going beyond panaceas. *Proceedings of the National Academy of Sciences*, 104(39), 15181-15187.
- McGinnis, M. D., & Ostrom, E. (2014). Social-ecological system framework: initial changes and continuing challenges. *Ecology and Society*, 19(2), 30.
- Cox, M., Arnold, G., & Villamayor Tomás, S. (2010). A review of design principles for community-based natural resource management. *Ecology and Society*, 15(4), 38.

### Hayden SFM

- Hayden, F. G. (2006). *Policymaking for a Good Society: The Social Fabric Matrix Approach to Policy Analysis and Program Evaluation*. Springer.
- Hayden, F. G. (2008). Integrating ecological and social system components of policy. *Journal of Economic Issues*, 42(2), 477-486.
- Hayden, F. G., & Bolduc, S. R. (2000). A social fabric matrix/multi-regional input-output analysis of low-level radioactive waste management in the United States. *Journal of Economic Issues*, 34(2), 367-378.

### Framework Bridges

- Fath, B. D., Dean, C. A., & Katzmair, H. (2015). Navigating the adaptive cycle: an approach to managing the resilience of social systems. *Ecology and Society*, 20(2), 24.
  - Integrates Holling's adaptive cycle with network analysis (methodological parallel)
- Cumming, G. S., et al. (2015). Understanding protected area resilience: a multi-scale, social-ecological approach. *Ecological Applications*, 25(2), 299-319.
  - Multi-scale SES analysis (methodological parallel for Doughnut downscaling)

---

## 5. Implementation Examples

### Doughnut-SFM

- **Clean Air Act ↔ Doughnut**: `examples/hayden_case_studies/clean_air_act_doughnut.py`
  - Maps EPA regulatory deliveries to Air Pollution (ecological ceiling), Health (social foundation), Water (social foundation)
  - Demonstrates boundary evaluation, driving chain identification

- **Helper Functions**: `graph/doughnut_bridge.py`
  - `boundary_state_to_delivery()`: Convert continuous indicator to delivery weight
  - `get_delivery_state()`: Classify weight as positive/negative/neutral

- **Tests**: `tests/test_doughnut_bridge.py`
  - 24 unit tests covering shortfall/overshoot polarities, threshold conditions, real-world examples

### Ostrom SES/IAD-SFM

- **Community Forest Example**: `examples/framework_bridges/ostrom_ses_iad_example.py`
  - Encodes forest commons governance in SFM framework
  - Demonstrates rules-in-use → institutions, action arena → node cluster, action situations → delivery cells
  - Evaluates sustainability, equity, legitimacy outcomes

---

## 6. Conclusion

The Doughnut-SFM and Ostrom-SFM bridges **extend institutional analysis** into sustainability science and commons governance. They are not neutral mappings but **methodological contributions** that:

1. **Enable new analyses**: Institutional attribution of boundary impacts, computational SES comparison
2. **Introduce new assumptions**: Linear scaling, causal attribution, normative evaluation
3. **Require transparency**: Document choices, recognize limitations, invite critique

Future research should explore:
- Multi-scale integration (local institutions → national boundaries → global Earth system)
- Temporal dynamics (delivery rates → boundary state trajectories)
- Non-linear thresholds (tipping points, adaptive cycles)
- Empirical validation (do SFM delivery chains predict boundary outcomes?)

The bridges demonstrate that **framework integration is itself a research contribution**—one that shapes what questions we can ask and what answers we can find.
