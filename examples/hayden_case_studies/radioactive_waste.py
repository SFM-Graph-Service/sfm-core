"""
Low-Level Radioactive Waste Policy Demonstration

Demonstration SFM analysis based on:
Hayden, F. G., & Bolduc, R. (2000). "Instrumental Reasoning and Normative
Analysis in LLRW Policy Analysis." Journal of Economic Issues, 34(4), 831-849.

SFM Methodology:
    Hayden, F. G. (2006). Policymaking for a Good Society: The Social Fabric Matrix
    Approach to Policy Analysis and Program Evaluation. Springer.

Demonstrates interstate compact system for low-level radioactive waste (LLRW) disposal.
Illustrates conflict between ceremonial (NIMBY, state sovereignty) and
instrumental (risk reduction, scientific siting) values.

Key concepts:
- Host states provide disposal capacity, receive payments
- Generator states produce waste, pay for disposal
- Interstate compacts coordinate regional solutions
- Federal NRC provides oversight and standards
- Cultural values conflict: ceremonial vs. instrumental
"""

from pathlib import Path
from api.sfm_service import SFMService
from models import Node
from models.delivery_matrix import Delivery
from graph.exporters import export_delivery_matrix_to_xlsx


def create_llrw_matrix():
    """
    Create SFM for LLRW interstate compact system.

    Focus on Central Interstate Low-Level Radioactive Waste Compact
    (Nebraska as host state, 1998-2002 period).
    """
    service = SFMService()

    # =========================================================================
    # STEP 1: Define components
    # =========================================================================

    # Host state
    nebraska = Node(
        label="Nebraska (Host State)",
        description="Host state for Central Compact LLRW disposal facility"
    )

    # Generator states
    arkansas = Node(
        label="Arkansas",
        description="Generator state in Central Compact"
    )

    kansas = Node(
        label="Kansas",
        description="Generator state in Central Compact"
    )

    louisiana = Node(
        label="Louisiana",
        description="Generator state in Central Compact"
    )

    oklahoma = Node(
        label="Oklahoma",
        description="Generator state in Central Compact"
    )

    # Coordinating body
    central_compact = Node(
        label="Central Interstate Compact Commission",
        description="Regional regulatory authority for LLRW disposal"
    )

    # Federal oversight
    federal_nrc = Node(
        label="Nuclear Regulatory Commission",
        description="Federal agency regulating nuclear materials and waste"
    )

    # Waste generators (utilities)
    nuclear_utilities = Node(
        label="Nuclear Power Utilities",
        description="Operators of nuclear power plants generating LLRW"
    )

    # Medical/research generators
    medical_generators = Node(
        label="Medical & Research Facilities",
        description="Hospitals, universities, labs generating medical/research LLRW"
    )

    # Community values
    nebraska_citizens = Node(
        label="Nebraska Citizens",
        description="Local communities near proposed facility (Boyd County)"
    )

    environmental_groups = Node(
        label="Environmental Advocacy Groups",
        description="Organizations monitoring LLRW disposal safety"
    )

    # Register all components
    components = [
        nebraska, arkansas, kansas, louisiana, oklahoma,
        central_compact, federal_nrc,
        nuclear_utilities, medical_generators,
        nebraska_citizens, environmental_groups
    ]

    for comp in components:
        service.create_node(comp)

    # =========================================================================
    # STEP 2: Create delivery matrix
    # =========================================================================

    matrix = service.create_delivery_matrix(
        label="LLRW Interstate Compact System",
        description="Central Interstate Compact for low-level radioactive waste disposal",
        components=[c.id for c in components],
        matrix_scope="regional"
    )

    # =========================================================================
    # STEP 3: Generator states → Host state (waste and payment)
    # =========================================================================

    # Generator states deliver waste and payment to Nebraska
    generator_states = [arkansas, kansas, louisiana, oklahoma]
    waste_volumes = {
        arkansas.id: 12_000,   # cubic feet/year
        kansas.id: 8_000,
        louisiana.id: 15_000,
        oklahoma.id: 10_000
    }
    payments = {
        arkansas.id: 2_400_000,   # USD/year
        kansas.id: 1_600_000,
        louisiana.id: 3_000_000,
        oklahoma.id: 2_000_000
    }

    for state in generator_states:
        # Waste delivery (pollution)
        service.add_delivery_to_matrix(
            matrix,
            state.id,
            nebraska.id,
            Delivery(
                delivery_type="pollution",
                delivery_content=f"Low-level radioactive waste shipments from {state.label}",
                quantity=waste_volumes[state.id],
                units="cubic feet/year",
                temporal_rate="continuous",
                threshold=waste_volumes[state.id] * 1.2,  # 20% over baseline triggers alert
                threshold_direction="above",
                certainty=0.90
            ),
            cell_description=f"{state.label} ships LLRW to Nebraska disposal facility"
        )

        # Payment delivery
        service.add_delivery_to_matrix(
            matrix,
            state.id,
            nebraska.id,
            Delivery(
                delivery_type="money",
                delivery_content=f"Disposal fees and surcharges from {state.label}",
                quantity=payments[state.id],
                units="USD/year",
                temporal_rate="annual",
                certainty=0.95
            ),
            cell_description=f"{state.label} ships LLRW to Nebraska disposal facility"
        )

    # =========================================================================
    # STEP 4: Nebraska → Generator states (disposal capacity)
    # =========================================================================

    for state in generator_states:
        service.add_delivery_to_matrix(
            matrix,
            nebraska.id,
            state.id,
            Delivery(
                delivery_type="energy",  # Using "energy" type for disposal capacity (service)
                delivery_content=f"Guaranteed disposal capacity for {state.label} waste",
                quantity=waste_volumes[state.id],
                units="cubic feet/year",
                temporal_rate="continuous",
                certainty=0.85
            ),
            cell_description=f"Nebraska provides disposal capacity to {state.label}"
        )

    # =========================================================================
    # STEP 5: Central Compact → States (authority and coordination)
    # =========================================================================

    # Compact → Nebraska (host state authority)
    service.add_delivery_to_matrix(
        matrix,
        central_compact.id,
        nebraska.id,
        Delivery(
            delivery_type="authority",
            delivery_content="Authority to accept waste and collect surcharges",
            certainty=1.0
        ),
        cell_description="Central Compact grants Nebraska host state authority and regulatory power"
    )

    service.add_delivery_to_matrix(
        matrix,
        central_compact.id,
        nebraska.id,
        Delivery(
            delivery_type="rule",
            delivery_content="Compact regulations and operating requirements",
            certainty=0.95
        ),
        cell_description="Central Compact grants Nebraska host state authority and regulatory power"
    )

    service.add_delivery_to_matrix(
        matrix,
        central_compact.id,
        nebraska.id,
        Delivery(
            delivery_type="money",
            delivery_content="Compact administrative funding and technical assistance",
            quantity=500_000,
            units="USD/year",
            temporal_rate="annual",
            certainty=0.90
        ),
        cell_description="Central Compact grants Nebraska host state authority and regulatory power"
    )

    # Compact → Generator states (regulations)
    for state in generator_states:
        service.add_delivery_to_matrix(
            matrix,
            central_compact.id,
            state.id,
            Delivery(
                delivery_type="rule",
                delivery_content=f"Waste acceptance criteria and shipping requirements for {state.label}",
                certainty=0.95
            ),
            cell_description=f"Central Compact regulates {state.label} waste management"
        )

    # =========================================================================
    # STEP 6: Federal NRC → Compact and states (oversight)
    # =========================================================================

    # NRC → Central Compact
    service.add_delivery_to_matrix(
        matrix,
        federal_nrc.id,
        central_compact.id,
        Delivery(
            delivery_type="authority",
            delivery_content="Federal authorization for interstate compact operations",
            certainty=1.0
        ),
        cell_description="Federal NRC authorizes and oversees Central Compact operations"
    )

    service.add_delivery_to_matrix(
        matrix,
        federal_nrc.id,
        central_compact.id,
        Delivery(
            delivery_type="rule",
            delivery_content="Federal regulations for LLRW disposal and licensing",
            certainty=1.0
        ),
        cell_description="Federal NRC authorizes and oversees Central Compact operations"
    )

    # NRC → Nebraska
    service.add_delivery_to_matrix(
        matrix,
        federal_nrc.id,
        nebraska.id,
        Delivery(
            delivery_type="rule",
            delivery_content="Facility licensing requirements and safety standards",
            certainty=1.0
        ),
        cell_description="Federal NRC regulates Nebraska disposal facility licensing and safety"
    )

    # =========================================================================
    # STEP 7: Waste generators → States (waste production)
    # =========================================================================

    # Nuclear utilities → States
    utility_waste_share = 0.80  # 80% of LLRW from nuclear power
    for state in generator_states:
        service.add_delivery_to_matrix(
            matrix,
            nuclear_utilities.id,
            state.id,
            Delivery(
                delivery_type="pollution",
                delivery_content=f"Nuclear power plant LLRW requiring disposal from {state.label}",
                quantity=waste_volumes[state.id] * utility_waste_share,
                units="cubic feet/year",
                temporal_rate="continuous",
                certainty=0.92
            ),
            cell_description=f"Nuclear utilities in {state.label} generate LLRW"
        )

    # Medical/research → States
    medical_waste_share = 0.20  # 20% of LLRW from medical/research
    for state in generator_states:
        service.add_delivery_to_matrix(
            matrix,
            medical_generators.id,
            state.id,
            Delivery(
                delivery_type="pollution",
                delivery_content=f"Medical and research LLRW from {state.label} facilities",
                quantity=waste_volumes[state.id] * medical_waste_share,
                units="cubic feet/year",
                temporal_rate="continuous",
                certainty=0.88
            ),
            cell_description=f"Medical/research facilities in {state.label} generate LLRW"
        )

    # =========================================================================
    # STEP 8: Nebraska citizens → Nebraska (ceremonial resistance)
    # =========================================================================

    # CRITICAL: Demonstrates ceremonial vs. instrumental conflict
    service.add_delivery_to_matrix(
        matrix,
        nebraska_citizens.id,
        nebraska.id,
        Delivery(
            delivery_type="rule",
            delivery_content="NIMBY opposition and legal challenges to facility siting",
            certainty=0.95
        ),
        cell_description="Nebraska citizens oppose LLRW facility through political and legal resistance (CEREMONIAL VALUE)"
    )

    # Set ceremonial component (status-quo preservation, resist change)
    cell = matrix.get_cell(nebraska_citizens.id, nebraska.id)
    cell.ceremonial_component = 0.9  # HIGH ceremonial resistance
    cell.instrumental_component = 0.1  # LOW instrumental problem-solving

    cell.cultural_values_influence = {
        "community_sovereignty": 0.8,  # CEREMONIAL: preserve local autonomy
        "nimby_resistance": 0.7,       # CEREMONIAL: resist external burden
        "risk_aversion": -0.5,         # Blocks INSTRUMENTAL risk reduction
        "scientific_siting": -0.6      # Blocks INSTRUMENTAL evidence-based policy
    }

    # =========================================================================
    # STEP 9: Environmental groups → Nebraska (instrumental monitoring)
    # =========================================================================

    service.add_delivery_to_matrix(
        matrix,
        environmental_groups.id,
        nebraska.id,
        Delivery(
            delivery_type="information",
            delivery_content="Technical analysis and safety monitoring recommendations",
            certainty=0.85
        ),
        cell_description="Environmental groups provide instrumental safety analysis and monitoring (INSTRUMENTAL VALUE)"
    )

    # Set instrumental component (problem-solving, evidence-based)
    cell = matrix.get_cell(environmental_groups.id, nebraska.id)
    cell.ceremonial_component = 0.2  # LOW ceremonial resistance
    cell.instrumental_component = 0.8  # HIGH instrumental problem-solving

    cell.cultural_values_influence = {
        "risk_reduction": 0.7,         # INSTRUMENTAL: minimize public health risk
        "scientific_siting": 0.8,      # INSTRUMENTAL: evidence-based location selection
        "transparency": 0.6,           # INSTRUMENTAL: open information sharing
        "nimby_resistance": -0.3       # Opposes CEREMONIAL resistance
    }

    # =========================================================================
    # STEP 10: Environmental groups → Federal NRC (monitoring input)
    # =========================================================================

    service.add_delivery_to_matrix(
        matrix,
        environmental_groups.id,
        federal_nrc.id,
        Delivery(
            delivery_type="information",
            delivery_content="Public comments and technical review of NRC regulations",
            certainty=0.80
        ),
        cell_description="Environmental groups provide public input to NRC regulatory process"
    )

    return matrix, service


def main():
    """Generate LLRW SFM and export to XLSX."""

    print("="*70)
    print("LOW-LEVEL RADIOACTIVE WASTE POLICY CASE STUDY")
    print("Hayden & Bolduc (2000)")
    print("="*70)

    # Create matrix
    matrix, service = create_llrw_matrix()

    # Display summary
    summary = matrix.get_summary()

    print(f"\nMatrix Summary:")
    print(f"  Components: {summary['components']}")
    print(f"  Non-empty cells: {summary['non_empty_cells']}")
    print(f"  Total deliveries: {summary['total_deliveries']}")
    print(f"\nDeliveries by type:")
    for dtype, count in summary['deliveries_by_type'].items():
        print(f"  {dtype}: {count}")

    print(f"\nCells with multiple deliveries: {summary['cells_with_multiple_deliveries']}")
    print(f"Quantified deliveries: {summary['quantified_deliveries']}")

    # Check thresholds (pollution monitoring)
    alerts = service.check_delivery_thresholds(matrix)
    if alerts:
        print(f"\nTHRESHOLD ALERTS: {len(alerts)}")
        for alert in alerts:
            print(f"  {alert.delivery.delivery_content}")
            print(f"  Current: {alert.current_value}, Threshold: {alert.threshold}")
    else:
        print("\nNo threshold alerts (waste volumes within baseline)")

    # Export to XLSX
    output_path = Path(__file__).parent / "radioactive_waste.xlsx"
    export_delivery_matrix_to_xlsx(
        matrix,
        output_path,
        service,
        include_cell_descriptions=True,
        include_delivery_details=True
    )

    print(f"\nExported to: {output_path}")
    print(f"File size: {output_path.stat().st_size / 1024:.1f} KB")

    # Key findings (per Hayden & Bolduc 2000)
    print("\n" + "="*70)
    print("KEY FINDINGS (Hayden & Bolduc 2000):")
    print("="*70)

    print("\n1. CEREMONIAL vs. INSTRUMENTAL CONFLICT:")
    print("   CEREMONIAL (Status-quo preservation):")
    print("   - Nebraska citizens resist facility (NIMBY, state sovereignty)")
    print("   - Ceremonial component: 0.9 (high resistance to change)")
    print("   - Cultural values: community_sovereignty (0.8), nimby_resistance (0.7)")
    print()
    print("   INSTRUMENTAL (Problem-solving):")
    print("   - Environmental groups advocate scientific siting")
    print("   - Instrumental component: 0.8 (high evidence-based approach)")
    print("   - Cultural values: risk_reduction (0.7), scientific_siting (0.8)")

    print("\n2. DELIVERY PATTERN ANALYSIS:")
    print("   - Generator states → Nebraska: Waste (pollution) + Payment (money)")
    print("   - Nebraska → Generator states: Disposal capacity (energy/service)")
    print("   - Compact → States: Authority + Rules + Coordination")
    print("   - Federal NRC → All: Oversight + Standards")

    print("\n3. POLICY DEADLOCK (1998-2002):")
    print("   - High ceremonial resistance blocked facility construction")
    print("   - Instrumental arguments (risk reduction, scientific siting) insufficient")
    print("   - Compact eventually dissolved, Nebraska withdrew as host state")

    print("\n4. INSTITUTIONALIST INSIGHT:")
    print("   - Technical/economic solutions fail when ceremonial values dominate")
    print("   - Cultural values analysis reveals deeper barriers than cost-benefit")
    print("   - Ceremonial encapsulation prevents instrumental problem-solving")

    print("\n5. THRESHOLD MONITORING:")
    print("   - Waste volume thresholds set at 120% of baseline")
    print("   - Alerts trigger when generator states exceed contracted volumes")
    print("   - Demonstrates Hayden's real-time monitoring concept (1987)")

    print("\n" + "="*70)


if __name__ == "__main__":
    main()
