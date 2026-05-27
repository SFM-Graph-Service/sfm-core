# Hayden's Social Fabric Matrix: Implementation Guide

## Introduction

This guide documents the **Social Fabric Matrix (SFM)** methodology developed by F. Gregory Hayden over 40+ years of institutionalist research. The SFM is an analytical tool for modeling social-ecological-economic systems through component interactions and deliveries.

**sfm-core** is an experimental implementation of Hayden's SFM structure based on published research, enabling:
- Policy analysis with explicit delivery tracking
- System dynamics modeling of institutional systems
- Cultural values integration (ceremonial vs. instrumental)
- Temporal modeling across multiple time scales
- Demonstration case studies from published research

**Note**: This is research software under active development. Claude AI was used to assist with code development and documentation. Errors may exist and users should verify outputs independently.

## Core Concepts

### The Social Fabric

Hayden's "social fabric" is the interconnected web of components that constitute a functioning society. Unlike pure market models, the SFM recognizes:

- **Six component categories**: Institutions, values, technologies, resources, ecosystems, communities
- **Multiple delivery types**: Money, energy, pollution, rules, authority, information
- **Cultural values**: Ceremonial (status-quo) vs. instrumental (problem-solving) forces
- **Polychronic time**: Multiple simultaneous temporal scales (legislative cycles, fiscal years, academic calendars)
- **Non-equilibrium dynamics**: Real-world systems don't settle at equilibrium points

The SFM captures **what components actually deliver to each other**, not abstract relationships.

### Why Square Matrices?

> "The SFM is a square, non-symmetric, input-output style matrix where row labels equal column labels. Cell (i,j) records what component i delivers to component j."
> 
> — Hayden (2008)

**Square structure** (N×N): Same components appear on **both** rows and columns because components both give and receive deliveries.

**Non-symmetric**: Cell (i,j) ≠ Cell (j,i)
- Legislature → School District: Money, rules, mandates
- School District → Legislature: Reports, compliance data, lobbying

**Why not rectangular?** Rectangular matrices (institution × criteria) evaluate institutions against fixed criteria. SFMs model **dynamic interactions** between components that play multiple roles.

### Multiple Heterogeneous Deliveries

**Hayden's critical 2008 requirement:**

> "A positive/negative sign is NOT sufficient to characterize a cell. Multiple distinct deliveries per cell are required to capture the heterogeneous nature of real-world interactions."
> 
> — Hayden (2008)

**Example: Legislature → School District**

Cell (Legislature, School District) contains:
1. **Money delivery**: $800M annual appropriation via TEEOSA formula
2. **Rule delivery**: Compliance requirements for formula qualification
3. **Authority delivery**: Audit power over district spending
4. **Information delivery**: Reporting requirements for student outcomes

Collapsing these to a single scalar (e.g., +0.8) loses critical policy information.

**Implementation:**

```python
from models.delivery_matrix import Delivery, SFMDeliveryMatrix

# Each cell holds a LIST of deliveries
cell = matrix.get_cell(legislature_id, school_district_id)

# Multiple deliveries per cell
cell.deliveries = [
    Delivery(
        delivery_type="money",
        delivery_content="$800M annual appropriation via TEEOSA",
        quantity=800_000_000,
        units="USD/year",
        temporal_rate="annual"
    ),
    Delivery(
        delivery_type="rule",
        delivery_content="TEEOSA compliance requirements"
    ),
    Delivery(
        delivery_type="authority",
        delivery_content="Audit power over district spending"
    )
]
```

### Cell Descriptions as Canonical Deliverables

Hayden's methodology treats **cell descriptions as canonical deliverables**, not optional metadata.

> "Cell descriptions are the primary product of SFM analysis. They document the narrative understanding of what each component delivers to others."
> 
> — Hayden (2013)

**Required per Hayden methodology**: Non-empty cells MUST have descriptions.

**Validation enforced:**

```python
@dataclass
class SFMDeliveryCell(Node):
    deliveries: List[Delivery] = field(default_factory=list)
    cell_description: str = ""
    
    def __post_init__(self):
        if self.deliveries and not self.cell_description:
            raise ValueError(
                "Non-empty SFM cells require cell_description per Hayden methodology. "
                "Cell descriptions are canonical SFM deliverables, not optional metadata."
            )
```

**Example description:**

```python
cell_description = """
Legislature provides funding to school districts through state aid formula (TEEOSA).
Districts must meet compliance requirements and submit annual reports to qualify.
Funding levels are based on district needs, enrollment, and local property tax capacity.
"""
```

## Six Component Categories

Hayden identifies six fundamental component types in social-ecological-economic systems:

### 1. Institutions

Organizations and formal structures:
- Government agencies (Legislature, Department of Education)
- Corporations (utilities, manufacturers)
- Non-profits (foundations, advocacy groups)
- Universities and research centers

**Example deliveries:**
- Money (appropriations, grants, contracts)
- Rules (regulations, mandates, policies)
- Authority (enforcement power, oversight)

### 2. Value Systems

Cultural belief systems and norms:
- Religious traditions
- Political ideologies
- Professional ethics
- Community values

Hayden distinguishes:
- **Ceremonial values**: Preserve status quo, resist change (hierarchy, tradition)
- **Instrumental values**: Problem-solving, adapt to evidence (efficiency, equity)

**Example deliveries:**
- Ceremonial pressure (resist policy change)
- Instrumental guidance (evidence-based reform)

### 3. Technologies

Methods, processes, and tools:
- Production technologies (manufacturing, agriculture)
- Information technologies (databases, communication)
- Educational methods (pedagogy, curriculum)

**Example deliveries:**
- Technical capacity (machinery, software)
- Knowledge (technical expertise)
- Standards (specifications, protocols)

### 4. Natural Resources

Physical stocks and flows:
- Water systems (aquifers, watersheds)
- Energy sources (fossil fuels, renewables)
- Land and minerals
- Atmospheric resources

**Example deliveries:**
- Energy (electricity, fuel)
- Materials (minerals, water)
- Pollution (CO2, wastewater)

### 5. Ecosystems

Ecological systems and processes:
- Watersheds and wetlands
- Forests and grasslands
- Coastal zones
- Wildlife populations

**Example deliveries:**
- Ecosystem services (water filtration, pollination)
- Habitat (species support)
- Pollution absorption (carbon sequestration)

### 6. Communities

Social groups and populations:
- Local communities
- Demographic groups
- Workers and households
- Students and families

**Example deliveries:**
- Labor (work hours, skills)
- Political pressure (votes, advocacy)
- Cultural practices (traditions, norms)

## Temporal Modeling

### Polychronic Systems

Real systems operate on **multiple simultaneous time scales**:

- **Legislative cycles**: Biennial sessions (Nebraska: 90-day + 60-day sessions with interims)
- **Budget years**: Annual appropriations
- **Fiscal years**: July 1 - June 30 government accounting
- **Academic years**: August - May school calendars
- **Continuous processes**: Ongoing monitoring, daily operations

**Hayden's polychronic concept** (1993): Different components operate on different clocks, requiring explicit temporal synchronization.

### Graphical Clocks

**TemporalClock** implements Hayden's graphical clock concept:

```python
from models.temporal_clocks import TemporalClock, TemporalPhase, create_legislative_clock
from datetime import timedelta

# Nebraska biennial legislative cycle
leg_clock = create_legislative_clock(state="Nebraska", biennial=True)

# Phases: first_session (90d) → first_interim (270d) → second_session (60d) → second_interim (310d)
print(leg_clock.phases)  # 4 phases totaling 730 days

# Advance through cycle
leg_clock.advance_phase()  # Now in "first_interim"

# Synchronize deliveries to clock
leg_clock.synchronize_delivery(
    source_id=legislature_id,
    target_id=school_district_id,
    delivery_index=0  # Money delivery
)
```

### Delivery Temporal Rates

Deliveries can specify temporal characteristics:

```python
Delivery(
    delivery_type="money",
    delivery_content="Annual appropriation",
    quantity=800_000_000,
    units="USD/year",
    temporal_rate="annual",  # When delivery occurs
    temporal_clock="fiscal_year"  # Which clock governs timing
)
```

**Temporal rate values:**
- `"annual"`: Once per year
- `"monthly"`: Twelve times per year
- `"quarterly"`: Four times per year
- `"continuous"`: Ongoing flow
- `"event_triggered"`: Conditional on events

### Threshold Monitoring

**Real-time monitoring** per Hayden (1987, 1993):

```python
from api.sfm_service import SFMService

service = SFMService()

# Create delivery with threshold
pollution_delivery = Delivery(
    delivery_type="pollution",
    delivery_content="CO2 emissions from power plant",
    quantity=550,
    units="million tons/year",
    threshold=500,  # Alert above 500
    threshold_direction="above"
)

# Monitor all deliveries against thresholds
alerts = service.check_delivery_thresholds(matrix)

for alert in alerts:
    print(f"THRESHOLD EXCEEDED: {alert.delivery.delivery_content}")
    print(f"Current: {alert.current_value}, Threshold: {alert.threshold}")
```

**Use cases:**
- Environmental monitoring (pollution limits)
- Budget tracking (spending caps)
- Performance monitoring (outcome thresholds)

## Matrix Structure and API

### Creating a Delivery Matrix

```python
from api.sfm_service import SFMService
from models import Node
from models.delivery_matrix import Delivery, SFMDeliveryMatrix

service = SFMService()

# Create components (institutions, values, resources, etc.)
legislature = Node(label="Nebraska Legislature", description="Unicameral legislative body")
dept_ed = Node(label="Department of Education", description="State education agency")
districts = Node(label="School Districts", description="Local K-12 districts")

# Register components
service.create_node(legislature)
service.create_node(dept_ed)
service.create_node(districts)

# Create square N×N matrix (same components on rows and columns)
matrix = service.create_delivery_matrix(
    label="Nebraska K-12 Education Finance",
    description="TEEOSA funding system SFM",
    components=[legislature.id, dept_ed.id, districts.id],
    matrix_scope="state"
)

# Add deliveries to cells
money_delivery = Delivery(
    delivery_type="money",
    delivery_content="$800M annual appropriation via TEEOSA formula",
    quantity=800_000_000,
    units="USD/year",
    temporal_rate="annual",
    certainty=0.95
)

service.add_delivery_to_matrix(
    matrix,
    source_id=legislature.id,
    target_id=districts.id,
    delivery=money_delivery,
    cell_description="Legislature provides funding to school districts through state aid formula"
)
```

### Matrix Operations

```python
# Get specific cell
cell = matrix.get_cell(legislature.id, districts.id)
print(f"Deliveries: {len(cell.deliveries)}")
print(f"Description: {cell.cell_description}")

# Get all non-empty cells
non_empty = matrix.get_non_empty_cells()
print(f"Matrix has {len(non_empty)} non-empty cells")

# Get outgoing deliveries (what component delivers to others)
outgoing = matrix.get_component_outgoing_cells(legislature.id)
print(f"Legislature delivers to {len(outgoing)} components")

# Get incoming deliveries (what component receives)
incoming = matrix.get_component_incoming_cells(districts.id)
print(f"Districts receive from {len(incoming)} components")

# Validate matrix structure
errors = matrix.validate_structure()
if errors:
    print("Validation errors:", errors)
else:
    print("Matrix validates per Hayden requirements")
```

### Cell Operations

```python
# Get deliveries by type
money_deliveries = cell.get_deliveries_by_type("money")
rule_deliveries = cell.get_deliveries_by_type("rule")

# Sum quantities by type
total_money = cell.get_total_quantity_by_type("money")
print(f"Total money delivered: ${total_money:,.0f}")

# Add multiple deliveries to same cell
rule_delivery = Delivery(
    delivery_type="rule",
    delivery_content="TEEOSA compliance requirements"
)

cell.add_delivery(rule_delivery)
print(f"Cell now has {len(cell.deliveries)} deliveries")
```

## Export Formats

### XLSX Export (Hayden 2013 Format)

The XLSX exporter produces three-sheet workbooks matching Hayden's published format:

```python
from graph.exporters import export_delivery_matrix_to_xlsx
from pathlib import Path

export_delivery_matrix_to_xlsx(
    matrix,
    Path("nebraska_k12_finance.xlsx"),
    service,
    include_cell_descriptions=True,
    include_delivery_details=True
)
```

**Sheet 1: Matrix View** (Square N×N)
- Row 1: Component labels (column headers)
- Column A: Component labels (row headers)
- Cells: Concatenated delivery summaries
- Color-coding by dominant delivery type:
  - Money: Light green (#C6EFCE)
  - Rule: Light red (#FFC7CE)
  - Authority: Light yellow (#FFEB9C)
  - Information: Light blue (#BDD7EE)
  - Energy: Light orange (#F4B084)
  - Pollution: Light gray (#D9D9D9)

**Sheet 2: Cell Descriptions** (Canonical Deliverables)
- Columns: Source | Target | Description | Delivery Count
- One row per non-empty cell
- Full narrative descriptions per Hayden methodology

**Sheet 3: Delivery Details** (Data Table)
- Columns: Source | Target | Type | Content | Quantity | Units | Rate | Threshold | Certainty
- One row per delivery
- Complete delivery metadata for analysis

**Example output:**

| Source | Target | Type | Content | Quantity | Units |
|--------|--------|------|---------|----------|-------|
| Legislature | School Districts | money | $800M annual appropriation... | 800000000 | USD/year |
| Legislature | School Districts | rule | TEEOSA compliance requirements | | |
| Dept of Education | School Districts | information | Standards and reporting... | | |

### System Dynamics Export (XMILE)

Export to System Dynamics models per Hayden & Hoffman (2007) *ithink* usage:

```python
from graph.exporters import export_to_xmile

export_to_xmile(
    matrix,
    Path("nebraska_k12_finance.xmile"),
    service,
    model_name="Nebraska K-12 Finance System",
    model_description="TEEOSA funding dynamics"
)
```

**Mapping:**
- **Components → Stocks**: Each matrix component becomes a stock variable
- **Deliveries with quantities → Flows**: Quantified deliveries become flows between stocks
- **Delivery rates → Flow equations**: Temporal rates define flow equations
- **Unquantified deliveries → Auxiliaries**: Qualitative deliveries become auxiliary variables

**Generated XMILE structure:**

```xml
<xmile version="1.0">
  <model>
    <variables>
      <stock name="Legislature">
        <eqn>0</eqn>
      </stock>
      <stock name="School_Districts">
        <eqn>0</eqn>
      </stock>
      <flow name="money_Legislature_to_School_Districts">
        <eqn>800000000</eqn>
      </flow>
    </variables>
  </model>
</xmile>
```

Compatible with:
- Stella Architect
- Vensim
- AnyLogic
- Other XMILE-compliant SD tools

### Matrix-Digraph Duality

Convert between matrix and directed graph representations:

```python
from graph.converters import to_multidigraph, from_multidigraph
import networkx as nx

# Matrix → MultiDiGraph
G = matrix.to_multidigraph(service)  # Convenience method
# OR
G = to_multidigraph(matrix, service)

print(f"Nodes: {len(G.nodes())}")
print(f"Edges: {len(G.edges())}")

# Each delivery becomes a labeled edge
for src, tgt, key, data in G.edges(data=True, keys=True):
    print(f"{src} --[{key}]--> {tgt}: {data['delivery_content']}")

# MultiDiGraph → Matrix (reconstruction)
reconstructed = from_multidigraph(G, service, matrix_label="Reconstructed")

# Verify roundtrip
assert len(reconstructed.components) == len(matrix.components)
```

**Use cases:**
- Network analysis (centrality, clustering, feedback loops)
- Visualization with NetworkX/Graphviz
- Graph algorithms (shortest paths, community detection)
- Integration with graph databases (Neo4j, NetworkX)

### Summary Statistics

```python
summary = matrix.get_summary()  # Convenience method
# OR
from graph.converters import get_delivery_summary
summary = get_delivery_summary(matrix)

print(summary)
```

**Output:**

```python
{
    'components': 5,
    'non_empty_cells': 6,
    'total_cells': 25,
    'total_deliveries': 9,
    'deliveries_by_type': {
        'money': 4,
        'rule': 1,
        'authority': 2,
        'information': 1,
        'energy': 1
    },
    'cells_with_multiple_deliveries': 2,
    'quantified_deliveries': 5,
    'cells_with_descriptions': 6
}
```

## Demonstration Case Studies

### 1. Nebraska K-12 Education Finance (Hoffman & Hayden 2007)

**Study**: "Evolution of Structure in a State K-12 Education Finance System: Nebraska TEEOSA"

**System modeled**: Tax Equity and Educational Opportunities Support Act (TEEOSA) funding formula

**Components**:
1. Nebraska Legislature (biennial sessions)
2. Department of Education (state agency)
3. School Districts (245 local districts)
4. Taxpayers (property tax base)
5. Students (enrollment-driven funding)

**Key deliveries**:
- Legislature → Districts: $800M annual appropriation
- Legislature → Dept Ed: Oversight authority
- Dept Ed → Districts: Standards and reporting requirements
- Districts → Students: Educational services
- Taxpayers → Legislature: Tax revenue and political pressure

**Temporal clocks**:
- Legislative: Biennial cycle (90-day + 60-day sessions)
- Fiscal: July 1 - June 30 state budget
- Academic: August - May school year

**File**: `examples/hayden_case_studies/nebraska_k12_finance.py`

**Generated output**: `nebraska_k12_finance.xlsx` (8.5 KB)

### 2. Corporate Director Networks (Hayden, Wood & Kaya 2002)

**Study**: "Patterns of Delivery and Correlation Coefficients in Corporate Director Networks"

**System modeled**: Interlocking corporate directorates as power delivery systems

**Components**:
- Fortune 500 corporations
- Financial institutions (banks, investment firms)
- Corporate directors (individuals serving on multiple boards)
- Industry associations

**Key deliveries**:
- Directors → Corporations: Strategic guidance, authority
- Corporations → Directors: Compensation, information access
- Financial institutions → Corporations: Capital, credit
- Industry associations → Corporations: Policy coordination

**Analysis focus**: Network centrality as indicator of power delivery patterns

**File**: `examples/hayden_case_studies/director_networks.py`

### 3. Low-Level Radioactive Waste (Hayden & Bolduc 2000)

**Study**: "Instrumental Reasoning in LLRW Policy Analysis"

**System modeled**: Interstate compact for radioactive waste disposal

**Components**:
- Host states (waste facility sites)
- Generator states (waste producers)
- Interstate compacts (regulatory bodies)
- Nuclear utilities (waste generators)
- Federal Nuclear Regulatory Commission

**Key deliveries**:
- Utilities → Host states: Waste shipments, payments
- Host states → Generator states: Disposal capacity
- Compacts → States: Authority, regulations
- Federal NRC → Compacts: Oversight, standards

**Cultural values conflict**:
- Ceremonial: NIMBY resistance, state sovereignty
- Instrumental: Risk reduction, scientific siting

**File**: `examples/hayden_case_studies/radioactive_waste.py`

## Integration with Cultural Framework

SFM integrates with Hayden's institutional economics cultural framework:

### Ceremonial vs. Instrumental Components

```python
cell.ceremonial_component = 0.7  # High status-quo preservation
cell.instrumental_component = 0.3  # Low problem-solving orientation
```

**Ceremonial deliveries** (preserve status quo):
- Traditional authority structures
- Hierarchical control
- Resistance to change
- Status-based resource allocation

**Instrumental deliveries** (enable problem-solving):
- Evidence-based policy
- Adaptive management
- Technological innovation
- Equity-oriented resource distribution

### Cultural Values Influence

```python
cell.cultural_values_influence = {
    "efficiency": 0.6,  # Instrumental value
    "equity": 0.4,      # Instrumental value
    "hierarchy": -0.3,  # Ceremonial resistance
    "tradition": -0.2   # Ceremonial resistance
}
```

**Analysis**: Cells with high ceremonial components resist instrumental change even when deliveries suggest problem-solving need.

## API Reference

### Core Classes

#### `Delivery`

Single delivery within an SFM cell.

**Attributes:**
- `delivery_type: str` - Type: "money", "energy", "pollution", "rule", "authority", "information"
- `delivery_content: str` - Narrative description (REQUIRED)
- `quantity: Optional[float]` - Numeric quantity
- `units: Optional[str]` - Units for quantity
- `temporal_rate: Optional[str]` - Temporal rate: "annual", "monthly", "continuous", "event_triggered"
- `temporal_clock: Optional[str]` - Clock name governing timing
- `threshold: Optional[float]` - Monitoring threshold value
- `threshold_direction: Optional[str]` - "above" or "below"
- `certainty: Optional[float]` - Confidence (0.0-1.0)
- `data_sources: List[str]` - Documentation sources

**Validation:**
- `delivery_type` and `delivery_content` are REQUIRED
- `threshold_direction` must be "above" or "below" if set
- `certainty` must be 0.0-1.0 if set

#### `SFMDeliveryCell`

Cell (i,j) showing deliveries from component i → component j.

**Attributes:**
- `source_component_id: uuid.UUID` - Source component (row)
- `target_component_id: uuid.UUID` - Target component (column)
- `deliveries: List[Delivery]` - All deliveries from source to target
- `cell_description: str` - Narrative description (REQUIRED for non-empty cells)
- `net_correlation: Optional[CorrelationType]` - Aggregate correlation
- `cultural_values_influence: Dict[str, float]` - Cultural values effects
- `ceremonial_component: Optional[float]` - Ceremonial strength
- `instrumental_component: Optional[float]` - Instrumental strength

**Methods:**
- `add_delivery(delivery: Delivery)` - Add delivery to cell
- `get_deliveries_by_type(delivery_type: str) -> List[Delivery]` - Filter by type
- `get_total_quantity_by_type(delivery_type: str) -> Optional[float]` - Sum quantities

**Validation:**
- Non-empty cells MUST have `cell_description`
- `source_component_id` and `target_component_id` are REQUIRED

#### `SFMDeliveryMatrix`

Square N×N Hayden-compliant delivery matrix.

**Attributes:**
- `components: List[uuid.UUID]` - Components on both axes
- `cells: Dict[Tuple[uuid.UUID, uuid.UUID], SFMDeliveryCell]` - Cells indexed by (source, target)
- `matrix_scope: Optional[str]` - Scope: "local", "regional", "national", "global"
- `temporal_scope: Optional[Tuple[datetime, datetime]]` - Time range

**Methods:**
- `get_cell(source_id, target_id) -> Optional[SFMDeliveryCell]` - Get cell at (i,j)
- `set_cell(cell: SFMDeliveryCell)` - Set cell (validates component membership)
- `add_component(component_id: uuid.UUID)` - Add component to both axes
- `remove_component(component_id: uuid.UUID)` - Remove component and its cells
- `is_square() -> bool` - Verify square structure (always True by design)
- `get_non_empty_cells() -> List[SFMDeliveryCell]` - Get cells with deliveries
- `get_component_outgoing_cells(component_id) -> List[SFMDeliveryCell]` - Outgoing deliveries
- `get_component_incoming_cells(component_id) -> List[SFMDeliveryCell]` - Incoming deliveries
- `validate_structure() -> List[str]` - Validate per Hayden requirements
- `to_multidigraph(service) -> nx.MultiDiGraph` - Convert to graph
- `get_summary() -> dict` - Get summary statistics

### Service Layer

#### `SFMService`

High-level service for SFM operations.

**Matrix Operations:**
```python
create_delivery_matrix(
    label: str,
    description: str = "",
    components: List[uuid.UUID] = None,
    matrix_scope: Optional[str] = None
) -> SFMDeliveryMatrix

add_delivery_to_matrix(
    matrix: SFMDeliveryMatrix,
    source_id: uuid.UUID,
    target_id: uuid.UUID,
    delivery: Delivery,
    cell_description: str
) -> SFMDeliveryCell
```

**Temporal Operations:**
```python
create_temporal_clock(
    label: str,
    clock_name: str,
    period_length: timedelta,
    phases: List[TemporalPhase] = None
) -> TemporalClock

synchronize_delivery_to_clock(
    clock: TemporalClock,
    matrix: SFMDeliveryMatrix,
    source_id: uuid.UUID,
    target_id: uuid.UUID,
    delivery_index: int
) -> None

check_delivery_thresholds(
    matrix: SFMDeliveryMatrix
) -> List[ThresholdAlert]
```

### Export Functions

```python
from graph.exporters import (
    export_delivery_matrix_to_xlsx,
    export_to_xmile
)

# XLSX export
export_delivery_matrix_to_xlsx(
    matrix: SFMDeliveryMatrix,
    filepath: Path,
    service: SFMService,
    include_cell_descriptions: bool = True,
    include_delivery_details: bool = True
) -> None

# System Dynamics export
export_to_xmile(
    matrix: SFMDeliveryMatrix,
    filepath: Path,
    service: SFMService,
    model_name: Optional[str] = None,
    model_description: Optional[str] = None
) -> None
```

### Conversion Functions

```python
from graph.converters import (
    to_multidigraph,
    from_multidigraph,
    matrix_to_adjacency_dict,
    adjacency_dict_to_matrix,
    get_delivery_summary
)

# Matrix ↔ Graph
to_multidigraph(matrix: SFMDeliveryMatrix, service: SFMService) -> nx.MultiDiGraph
from_multidigraph(G: nx.MultiDiGraph, service: SFMService) -> SFMDeliveryMatrix

# Matrix ↔ Adjacency dictionary
matrix_to_adjacency_dict(matrix: SFMDeliveryMatrix, service: SFMService) -> dict
adjacency_dict_to_matrix(adj: dict, service: SFMService) -> SFMDeliveryMatrix

# Summary statistics
get_delivery_summary(matrix: SFMDeliveryMatrix) -> dict
```

## Research Foundation

This implementation is based on 40+ years of Hayden's published research:

### Foundational Papers

1. **Hayden, F. G. (1982)**. "Social Fabric Matrix: From Perspective to Analytical Framework." *Journal of Economic Issues*, 16(3), 637-662.
   - Original SFM formulation
   - Component categories and interaction types

2. **Hayden, F. G. (1987)**. "Evolution of Time Constructs and Effects on Socioeconomic Planning and Policy." *Journal of Economic Issues*, 21(3), 1281-1312.
   - Polychronic time modeling
   - Temporal rates and thresholds

3. **Hayden, F. G. (1993)**. "Institutionalist Policymaking." In *Tool and Samuels (eds.), State, Society, and Corporate Power*, 283-310.
   - Graphical clocks for policy cycles
   - Ceremonial vs. instrumental components

4. **Hayden, F. G. (2006)**. *Policymaking for a Good Society: The Social Fabric Matrix Approach to Policy Analysis and Program Evaluation*. Springer.
   - Comprehensive SFM methodology
   - Matrix-digraph duality
   - Quality of solution sets

5. **Hayden, F. G. (2008)**. "Normative Analysis of Instituted Processes." In *The Handbook of Institutional Economics*, 271-295.
   - Multiple deliveries requirement
   - Square matrix structure justification

### Applied Case Studies

6. **Hayden, F. G., & Bolduc, R. (2000)**. "Instrumental Reasoning and Normative Analysis in LLRW Policy Analysis." *Journal of Economic Issues*, 34(4), 831-849.
   - Low-level radioactive waste case study

7. **Hayden, F. G., Wood, S., & Kaya, I. (2002)**. "Patterns of Delivery and Correlation Coefficients in Social Fabric Matrix Analyses of Corporate Director Networks." *Journal of Economic Issues*, 36(2), 345-352.
   - Corporate network analysis

8. **Hoffman, S., & Hayden, F. G. (2007)**. "Evolution of Structure in a State K-12 Education Finance System: Nebraska TEEOSA." *Journal of Economic Issues*, 41(4), 995-1022.
   - Nebraska education finance (primary validation case study)
   - System dynamics modeling with *ithink*

9. **Hayden, F. G. (2013)**. "Social Fabric Matrix Analysis of a Health Care Delivery Proposal." In *Alternative Theories of Competition*, 245-268.
   - Health care policy analysis
   - XLSX matrix export format

## Implementation Assessment

**sfm-core** aims for high fidelity to Hayden's published methodology:

| Dimension | Implementation |
|-----------|----------------|
| Matrix Structure | Square N×N, non-symmetric, component×component |
| Multiple Deliveries | List-based heterogeneous delivery storage |
| Cell Descriptions | Required for non-empty cells, validated |
| Temporal Modeling | Rates, clocks, phases, threshold monitoring |
| Cultural Integration | Ceremonial/instrumental components, values influence |
| Export Capabilities | XLSX, XMILE (System Dynamics) |
| Graph Duality | Bidirectional matrix ↔ MultiDiGraph conversion |

Implementation is based on Hayden's published work spanning 40+ years of research.

## License and Citation

**sfm-core** is open source software.

If you use this implementation in research, please cite:

```
Hayden, F. G. (2006). Policymaking for a Good Society: The Social Fabric Matrix Approach 
to Policy Analysis and Program Evaluation. Springer.
```

And acknowledge:

```
This analysis uses sfm-core, an experimental implementation of Hayden's Social Fabric Matrix 
methodology (https://github.com/yourusername/sfm-core).
```

## Further Reading

- **Institutional Economics**: Tool, M. R. (1993). *The Discretionary Economy*. Westview Press.
- **System Dynamics**: Forrester, J. W. (1961). *Industrial Dynamics*. MIT Press.
- **Social Fabric Analysis**: Bush, P. D. (1987). "The Theory of Institutional Change." *Journal of Economic Issues*, 21(3), 1075-1116.
- **Cultural Framework**: Veblen, T. (1899). *The Theory of the Leisure Class*. Macmillan.

---

*Last updated: 2026-05-27*
